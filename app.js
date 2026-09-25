"use strict";

function initCaseFilters() {
  const buttons = [...document.querySelectorAll(".case-filter")];
  const cards = [...document.querySelectorAll(".case-card")];
  if (!buttons.length) return;
  buttons.forEach(button => button.addEventListener("click", () => {
    const family = button.dataset.caseFilter;
    buttons.forEach(item => item.setAttribute("aria-pressed", String(item === button)));
    cards.forEach(card => { card.hidden = family !== "all" && card.dataset.family !== family; });
  }));
}

function initTimingModel() {
  const noise = document.getElementById("noise-range");
  const threshold = document.getElementById("threshold-range");
  if (!noise || !threshold) return;
  const hitBar = document.getElementById("hit-bar");
  const missBar = document.getElementById("miss-bar");
  const histogram = document.getElementById("histogram");
  const readout = document.getElementById("timing-readout");

  function render() {
    const n = Number(noise.value);
    const t = Number(threshold.value);
    document.getElementById("noise-output").value = String(n);
    document.getElementById("threshold-output").value = String(t);
    // Fixed pseudo-random sequence keeps the comparison stable when sliders move.
    let seed = 20260925;
    const random = () => {
      seed ^= seed << 13; seed ^= seed >>> 17; seed ^= seed << 5;
      return (seed >>> 0) / 4294967296;
    };
    let correct = 0, hitSum = 0, missSum = 0;
    const hitBins = Array(14).fill(0);
    const missBins = Array(14).fill(0);
    for (let i = 0; i < 100; i++) {
      const hit = Math.max(10, 80 + (random() + random() + random() - 1.5) * n * 1.9);
      const miss = Math.max(10, 160 + (random() + random() + random() - 1.5) * n * 1.9);
      hitSum += hit; missSum += miss;
      hitBins[Math.min(13, Math.floor(hit / 20))]++;
      missBins[Math.min(13, Math.floor(miss / 20))]++;
      if (hit < t) correct++;
      if (miss >= t) correct++;
    }
    const hitAvg = Math.round(hitSum / 100);
    const missAvg = Math.round(missSum / 100);
    hitBar.style.height = String(Math.min(95, hitAvg / 200 * 100)) + "%";
    missBar.style.height = String(Math.min(95, missAvg / 200 * 100)) + "%";
    const maxCount = Math.max(...hitBins, ...missBins, 1);
    histogram.replaceChildren(...hitBins.map((count, i) => {
      const bin = document.createElement("div");
      bin.className = "hist-bin";
      const hitBar = document.createElement("span");
      hitBar.className = "hist-hit";
      hitBar.style.height = String(count / maxCount * 76) + "px";
      const missBar = document.createElement("span");
      missBar.className = "hist-miss";
      missBar.style.height = String(missBins[i] / maxCount * 76) + "px";
      bin.append(hitBar, missBar);
      return bin;
    }));
    histogram.setAttribute("aria-label", `100 个 Hit 与 100 个 Miss 教学样本按耗时分布；噪声 ${n}，阈值 ${t}`);
    readout.textContent = `模型样本：Hit 平均 ${hitAvg}、Miss 平均 ${missAvg}；阈值 ${t}；200 次判决中 ${correct} 次正确（${Math.round(correct / 2)}%）。`;
  }
  noise.addEventListener("input", render);
  threshold.addEventListener("input", render);
  render();
}

function initPipelineModel() {
  const next = document.getElementById("sim-next");
  const reset = document.getElementById("sim-reset");
  if (!next || !reset) return;
  const lines = [...document.querySelectorAll(".sim-line")];
  const readout = document.getElementById("pipeline-readout");
  const captions = [
    "训练仅建立预测倾向；还没有泄漏。",
    "错误预测打开短暂执行窗口；检查尚未完成。",
    "教学模型中的值 3 被编码为 probe[3] 的缓存热状态。",
    "架构结果被撤销；模型中的缓存热状态没有被撤销。",
    "模型观测到 probe[3]。真实攻击还需反复采样、控制噪声与满足硬件条件。"
  ];
  let step = -1;
  function render() {
    lines.forEach((line, i) => line.classList.toggle("active", i === step));
    readout.textContent = step < 0 ? "点击“下一步”查看教学模型。" : captions[step];
    next.disabled = step >= captions.length - 1;
  }
  next.addEventListener("click", () => { if (step < captions.length - 1) step++; render(); });
  reset.addEventListener("click", () => { step = -1; render(); });
  render();
}

initCaseFilters();
initTimingModel();
initPipelineModel();
