/* Deterministic teaching models only: no hardware timing, predictor access or network. */
(function () {
  'use strict';
  function historyStates(sequence, initial = 0) {
    const states = [initial & 255];
    for (const bit of sequence) {
      if (bit !== 0 && bit !== 1) throw new Error('Toy outcome must be 0 or 1');
      states.push(((states.at(-1) << 1) | bit) & 255);
    }
    return states;
  }
  const HISTORY_SEQUENCE = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1];
  function rsbState(scenario, step) {
    if (!['normal', 'underflow'].includes(scenario)) throw new Error('Invalid toy scenario');
    const max = scenario === 'normal' ? 4 : 6;
    if (!Number.isInteger(step) || step < 0 || step > max) throw new Error('Step outside toy trace');
    let stack, rsb, event;
    if (scenario === 'normal') {
      const stacks = [[], ['R_main'], ['R_main', 'R_f'], ['R_main'], []];
      stack = [...stacks[step]]; rsb = [...stack];
      event = ['start', 'CALL f', 'CALL g', 'RET from g', 'RET from f'][step];
    } else {
      stack = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6'].slice(0, 6 - step);
      rsb = ['R3', 'R4', 'R5', 'R6'].slice(0, Math.max(0, 4 - step));
      event = step === 0 ? '6 CALLs completed' : 'RET ' + step;
    }
    const shortage = stack.length > 0 && rsb.length === 0;
    return {stack, rsb, event, max, shortage, actual: stack.at(-1) || null,
      predicted: rsb.at(-1) || (shortage ? 'G' : null), source: stack.length === 0 ? 'none' : shortage ? 'alternate' : 'RSB'};
  }
  function lookupState(mode, history, trained, aliases) {
    if (!['bti', 'bhi'].includes(mode) || !['H_A', 'H_G'].includes(history)) throw new Error('Invalid toy mode');
    const targets = mode === 'bhi' ? ['NORMAL', 'G'] : [trained && aliases ? 'G' : 'NORMAL', 'G'];
    const index = mode === 'bhi' && history === 'H_G' ? 1 : 0;
    return {targets, index, predicted: targets[index], actual: 'NORMAL'};
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {historyStates, HISTORY_SEQUENCE, rsbState, lookupState};
  if (typeof document === 'undefined') return;
  const zh = document.documentElement.lang.startsWith('zh');
  const tr = (en, cn) => zh ? cn : en;
  document.querySelectorAll('[data-training-model]').forEach(root => {
    const kind = root.dataset.trainingModel;
    const q = s => root.querySelector(s);
    const range = q('[data-step]');
    let trained = false;
    function rowCells(values, selected) {
      const row = document.createElement('div'); row.className = 'model-cells';
      for (const [i, value] of values.entries()) {
        const item = document.createElement('span'); item.className = 'model-cell' + (i === selected ? ' selected' : '');
        item.textContent = value; row.append(item);
      }
      return row;
    }
    function draw() {
      if (kind === 'history') {
        const n = Number(range.value), states = historyStates(HISTORY_SEQUENCE), bits = states[n].toString(2).padStart(8, '0');
        q('[data-bits]').replaceChildren(rowCells([...bits], 7));
        q('[data-readout]').textContent = tr('Step ', '步骤 ') + n + '/12 · H = ' + bits;
        q('[data-explanation]').textContent = n === 0 ? tr('Start at zero. Execute one toy outcome at a time.', '从零开始，每次执行一个教学分支结果。') : n <= 8 ? tr('Append outcome ' + HISTORY_SEQUENCE[n - 1] + '; shift out the oldest bit. Target state is not changed here.', '移入结果 ' + HISTORY_SEQUENCE[n - 1] + '，移出最老位；这里不修改目标预测项。') : tr('Extra Taken outcomes overwrite the prepared history. At step 12 it is 00101111, not 10110010.', '额外的 Taken 分支覆盖此前历史。第 12 步为 00101111，不再是 10110010。');
      } else if (kind === 'rsb') {
        const s = rsbState(q('[data-scenario]').value, Number(range.value));
        range.max = s.max;
        const empty = tr('(empty)', '（空）');
        q('[data-software]').replaceChildren(rowCells(s.stack.length ? s.stack : [empty], s.stack.length - 1));
        q('[data-rsb]').replaceChildren(rowCells(s.rsb.length ? s.rsb : [empty], s.rsb.length - 1));
        q('[data-readout]').textContent = tr('Step ', '步骤 ') + range.value + '/' + s.max + ' · ' + (zh ? ({start:'初始', '6 CALLs completed':'六层 CALL 已完成', 'RET from g':'从 g 返回', 'RET from f':'从 f 返回'}[s.event] || s.event) : s.event);
        q('[data-explanation]').textContent = s.actual === null ? (Number(range.value) === 0 ? tr('Start: execute the first CALL to establish a return prediction.', '初始状态：执行第一次 CALL 建立返回预测。') : tr('Trace finished: no next RET in this model.', '轨迹结束：此模型中没有下一条 RET。')) : tr('If returning from this state: stack target = ', '若从此状态返回：软件栈目标 = ') + s.actual + tr('; predicted = ', '；预测目标 = ') + s.predicted + tr('; source = ', '；预测来源 = ') + (s.source === 'alternate' ? tr('affected alternate predictor; stack remains valid', '受影响的替代预测器；软件栈仍有效') : 'RSB');
        root.dataset.shortage = String(s.shortage);
      } else {
        const mode = q('[data-mode]').value, history = q('[data-history]').value, aliases = q('[data-alias]').checked;
        const s = lookupState(mode, history, trained, aliases);
        q('[data-history]').disabled = mode !== 'bhi'; q('[data-alias]').disabled = mode !== 'bti';
        q('[data-train]').disabled = mode !== 'bti' || trained;
        const rows = s.targets.map((target, i) => {
          const row = document.createElement('tr'); if (i === s.index) row.className = 'selected';
          for (const value of [i === 0 ? 'H_A' : 'H_G', target, i === s.index ? tr('selected', '选中') : '—']) { const cell = document.createElement('td'); cell.textContent = value; row.append(cell); }
          return row;
        });
        q('tbody').replaceChildren(...rows);
        q('[data-readout]').textContent = tr('Actual fp = ', '真实 fp = ') + s.actual + tr('; predicted = ', '；预测目标 = ') + s.predicted;
        q('[data-explanation]').textContent = mode === 'bhi' ? tr('Both target entries stay fixed. Only the named lookup context changes. This is selection, not a write into the table.', '两个目标项始终不变，只切换命名的查找上下文；这是选择，不是写入目标表。') : tr('Context H_A stays fixed. Successful abstract training changes its target only if the alias condition is enabled. Repeating arbitrary jumps is not sufficient.', '上下文 H_A 保持不变；仅在启用别名条件时，抽象训练才改变其目标。随便重复跳转并不充分。');
      }
      if (range) {
        q('[data-back]').disabled = Number(range.value) === 0;
        q('[data-next]').disabled = Number(range.value) === Number(range.max);
      }
    }
    root.addEventListener('click', event => {
      const b = event.target.closest('button'); if (!b || !root.contains(b)) return;
      if (b.hasAttribute('data-reset')) { trained = false; if (range) range.value = 0; }
      if (b.hasAttribute('data-train')) trained = true;
      if (b.hasAttribute('data-next')) range.value = Math.min(Number(range.max), Number(range.value) + 1);
      if (b.hasAttribute('data-back')) range.value = Math.max(0, Number(range.value) - 1);
      draw();
    });
    root.addEventListener('input', event => { if (event.target.hasAttribute('data-scenario')) range.value = 0; draw(); });
    root.addEventListener('change', event => { if (event.target.hasAttribute('data-scenario')) range.value = 0; draw(); });
    draw();
  });
}());
