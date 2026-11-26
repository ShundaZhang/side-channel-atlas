# -*- coding: utf-8 -*-
"""Reviewed additions from the BTI/BHI discussion. Conversation text is not authority."""
from html import escape as e
CASES_WITH_LESSONS={'spectre-v2','bhi','retbleed'}
BHI_PAPER='https://www.usenix.org/system/files/sec22-barberis.pdf'
ARM_PAPER='https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/Security%20Update%2008%20March%202022/Spectre-BHB%20White%20Paper%20v1.6.pdf'
RISCV='https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html#_unconditional_jumps'

def lesson_content(id,zh):
 if id not in CASES_WITH_LESSONS:return ''
 def t(pair):return pair[1 if zh else 0]
 def para(pair):return '<p>'+e(t(pair))+'</p>'
 def title(pair):return '<h3>'+e(t(pair))+'</h3>'
 def code(pair):return '<pre class="case-trace"><code>'+e(t(pair))+'</code></pre>'
 def table(headers,rows):
  return '<div class="case-table" tabindex="0" role="region" aria-label="'+t(('Worked-example table','教学示例表'))+'"><table><thead><tr>'+''.join('<th scope="col">'+e(t(h))+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(t(cell))+'</td>' for cell in row)+'</tr>' for row in rows)+'</tbody></table></div>'
 def buttons(maxstep):
  return '<label class="model-step-label">'+t(('Trace step','执行步骤'))+' <input data-step type="range" min="0" max="'+str(maxstep)+'" value="0" step="1"></label><div class="model-buttons"><button type="button" data-reset>'+t(('Reset','重置'))+'</button><button type="button" data-back>'+t(('Back','上一步'))+'</button><button type="button" data-next>'+t(('Next step','下一步'))+'</button></div>'
 def readout():return '<p data-readout role="status" aria-live="polite"></p><p data-explanation></p>'
 def lookup():
  return '<div class="training-model" data-training-model="lookup"><h4>'+t(('Change the stored target, or change the lookup context?','改变已存目标，还是改变查找上下文？'))+'</h4>'+para(('Two-entry logical model. H_A/H_G are names, not real CPU histories. Both modes keep the actual function pointer at NORMAL. Controls select counterfactual experiments, not hardware settings.','双项逻辑模型。H_A / H_G 是标签，不是真实 CPU 历史；两种模式的真实函数指针都保持 NORMAL。控件用于选择对照实验，不是硬件设置。'))+'<div class="model-controls"><label>'+t(('Mode','模式'))+' <select data-mode><option value="bti">BTI</option><option value="bhi">BHI</option></select></label><label>'+t(('History context','历史上下文'))+' <select data-history><option>H_A</option><option>H_G</option></select></label><label><input type="checkbox" data-alias checked> '+t(('Assume relevant aliasing','假设满足相关别名条件'))+'</label></div><div class="model-buttons"><button type="button" data-train>'+t(('Model target training toward G','模拟向 G 的目标训练'))+'</button><button type="button" data-reset>'+t(('Reset training','重置训练'))+'</button></div><div class="case-table"><table><thead><tr><th>'+t(('Context','上下文'))+'</th><th>'+t(('Stored target','已存目标'))+'</th><th>'+t(('Selection','选择'))+'</th></tr></thead><tbody><tr><td>H_A</td><td>NORMAL</td><td>—</td></tr><tr><td>H_G</td><td>G</td><td>—</td></tr></tbody></table></div>'+readout()+'</div>'
 s='<section id="worked-models"><h2>'+t(('Worked examples: from branch events to predictions','具体例子：从分支事件到预测结果'))+'</h2><div class="case-model">'+t(('These browser models expose the changing state, not a real predictor. They do not train hardware, access secrets, measure time or infer whether this device is vulnerable.','浏览器模型只展示状态变化，不代表真实预测器；不训练硬件、不访问秘密、不计时，也不检测本机是否存在漏洞。'))+'</div>'
 if id=='spectre-v2':
  s+=title(('Is repeatedly jumping to G enough for BTI?', 'BTI 是不是只要不断跳到 G 就行？'))
  s+=para(('Not by itself. Separate the training branch source S, victim branch J and desired code target G. Repetition can build an association, but it matters only if the relevant predictor lookup/selection can transfer that association to J. Equal full addresses are not required; equal low bits alone are not a universal guarantee. History, predictor tags, domain restrictions, barriers and CPU-specific sharing also matter.','不充分。先分清训练分支源 S、受害者分支 J 和期望的代码目标 G。重复执行可以建立关联，但只有相关预测查找 / 选择机制能把关联迁移到 J，才会影响受害者。不要求完整地址相等，也不能认为低位相同就必然有效；还取决于历史、预测器标签、域限制、屏障和具体 CPU 的共享方式。'))
  s+=code(('''# Semantic training trace; not executable assembly
training context: execute indirect branch S -> G
required: relevant predictor alias / match with victim J
victim J: call fp             # fp = NORMAL
possible early prediction: G # fp was never changed
resolve: execute NORMAL; discard wrong-path results''','''# 语义训练轨迹，不是可执行汇编
训练上下文：执行间接分支 S -> G
必要前提：与受害者 J 满足相关预测别名 / 匹配条件
受害者 J：call fp             # fp = NORMAL
可能的提前预测：G              # fp 始终未变
解析后：执行 NORMAL，取消错误路径结果'''))
  s+=lookup()
 elif id=='bhi':
  s+=title(('Why is branch history useful in the first place?', 'CPU 为什么要参考分支历史？'))
  s+=code(('''// C teaching example: the indirect call site J is the same
void (*fp)(void) = (type == 0) ? func_A : func_B;
fp();  // J: earlier control flow can correlate with the target''','''// C 教学示例：间接调用位置 J 始终相同
void (*fp)(void) = (type == 0) ? func_A : func_B;
fp();  // J：此前的控制流可能与本次目标有关联'''))
  s+=para(('A PC-only last-target predictor struggles when the same call site alternates between A and B. Recent path context can improve the guess before fp is ready. This is the performance motivation, not a requirement that the compiler emit one particular branch sequence; optimizers may use conditional moves or transform the code.','同一调用点在 A、B 间切换时，仅按 PC 记住上次目标的预测器容易失准。fp 未就绪前，近期路径上下文可能帮助预测。这只是性能动机，不要求编译器一定生成某种分支序列；优化器也可能使用条件移动或改写代码。'))
  s+=title(('History shaping: show every update', '历史构造：把每次更新画出来'))
  s+=para(('For intuition only, use an 8-bit outcome shift register resembling a toy GHR. Taken appends 1; Not Taken appends 0. Software is not writing a real BHB register. In this model one pass through eight outcomes fixes the eight bits; repeating the full BHI experiment is a separate question from accumulating more training confidence.','先用一个类似 GHR 的 8 位结果移位寄存器帮助理解：Taken 移入 1，Not Taken 移入 0。软件并不是在写真实 BHB 寄存器。此模型执行一遍八个结果即可确定八个位；反复执行完整 BHI 实验，与“不断累积历史训练置信度”不是同一回事。'))
  s+=code(('''H = ((H << 1) | outcome) & 0xff;  // toy update only
// T N T T N N T N -> 10110010
// then T T T T    -> 00101111''','''H = ((H << 1) | outcome) & 0xff;  // 仅为教学更新规则
// T N T T N N T N -> 10110010
// 再执行 T T T T -> 00101111'''))
  s+='<div class="training-model" data-training-model="history"><h4>'+t(('Step through 8 outcomes, then 4 extra Taken branches','先逐步执行 8 个结果，再加 4 次 Taken'))+'</h4><div data-bits class="history-bits">00000000</div>'+buttons(12)+readout()+'</div>'
  s+=table([('Outcome','分支结果'),('H after update','更新后的 H')],[[(name,'初始' if name=='Start' else name),(value,value)] for name,value in [('Start','00000000'),('T','00000001'),('N','00000010'),('T','00000101'),('T','00001011'),('N','00010110'),('N','00101100'),('T','01011001'),('N','10110010'),('+ T T T T','00101111')]])
  s+=title(('Real history: source, destination and intervening branches', '真实历史：不只有 Taken / Not Taken'))
  s+=para(('A more general conceptual update is H_next = F(H_old, source_PC, destination_PC, outcome, type), with only the inputs used by the implementation included. The BHI paper describes older Intel reverse-engineered histories that mix folded source/destination information. Thus two all-Taken paths can produce different contexts. The 8-bit rule above is not an Intel/Arm BHB formula. The relevant history is the one at victim J: transitions, dispatcher branches and other intervening work may change it.','更一般的概念式是 H_next = F(H_old, 源 PC, 目标 PC, 结果, 类型)，具体实现不一定使用全部输入。BHI 论文介绍过早期 Intel 逆向研究中混入折叠源 / 目标地址信息的历史结构。因此两条全部 Taken 的路径，也可能产生不同上下文。上面的 8 位规则不是 Intel / Arm 的 BHB 公式。真正相关的是到达受害者 J 时的历史；域切换、分发器和中间工作中的分支都可能改变它。'))
  s+=lookup()
  s+=title(('Must the attacker reproduce the victim’s entire history?', '必须完整复制受害者的分支历史吗？'))
  s+=para(('No universal full-history equality is required. Different branch PCs and histories can alias in finite predictor indexing/tagging or selection logic. An entry learned by another victim-domain branch can therefore matter even if J never architecturally called G. Matching a toy hash alone would not prove exploitation: the relevant tags, domain eligibility, predictor choice, confidence and a useful gadget still matter. Arm’s Figure 3 illustrates target reuse through this kind of victim-entry aliasing.','不要求通用的“完整历史相等”。不同分支 PC 和历史，可能在有限的预测器索引 / 标签或选择逻辑中发生别名。因此，即使 J 从未正式调用过 G，受害者域内另一条分支学习的目标项也可能产生影响。仅让教学哈希相同不能证明可利用；仍需考虑相关标签、域资格、预测器选择、置信度和可用 gadget。Arm 白皮书 Figure 3 展示的就是这类受害者目标项的别名复用。'))
  s+=code(('''# Conceptual relation, not a real CPU hash
LookupContext(seed_PC, H_seed, victim_mode)
    may alias LookupContext(J, H_at_J, victim_mode)
# Neither complete PC equality nor complete history equality is assumed.
# Target G must already be eligible in the victim prediction domain.''','''# 概念关系，不是真实 CPU 哈希函数
LookupContext(训练分支 PC, H_seed, 受害者模式)
    可能与 LookupContext(J, 到达 J 时的历史, 受害者模式) 别名
# 不假设完整 PC 或完整历史必须相等。
# 目标 G 仍须已属于受害者允许使用的预测域。'''))
  s+='<p class="prediction-references"><a href="'+BHI_PAPER+'" target="_blank" rel="noopener noreferrer">BHI paper · §2.1 / §5</a> · <a href="'+ARM_PAPER+'" target="_blank" rel="noopener noreferrer">Arm Spectre-BHB · Figure 3</a></p>'
 else:
  s+=title(('CALL trains the return-after-CALL address, not the callee', 'CALL 跟踪的是 CALL 后的返回地址，不是被调函数地址'))
  s+=para(('If a CALL transfers to func_A, the RSB prediction normally tracks where execution should continue after that CALL. The callee address func_A is not that return address. RET normally consumes a return prediction. “Repeatedly RET to G” is therefore not the normal way CALL-based RSB tracking is established. This is also why RSB-entry poisoning must be distinguished from training the alternate target predictor used in the evaluated Intel Retbleed path.','CALL 跳到 func_A 时，RSB 通常跟踪的是“该 CALL 执行完后应回到哪里”。func_A 的入口地址不是这个返回地址；RET 通常消费一个返回预测。因此，“反复 RET 到 G”不是正常 CALL 建立 RSB 跟踪的方式。也正因此，需要区分 RSB 项投毒与原评估 Intel Retbleed 路径中替代目标预测器的训练。'))
  s+='<div class="training-model" data-training-model="rsb"><h4>'+t(('Compare CALL/RET tracking and prediction shortage','对照 CALL / RET 跟踪与预测项不足'))+'</h4><label>'+t(('Scenario','场景'))+' <select data-scenario><option value="normal">'+t(('Two CALLs, two RETs','两次 CALL、两次 RET'))+'</option><option value="underflow">'+t(('Toy capacity 4, six saved returns','教学容量 4，软件栈保存 6 项'))+'</option></select></label>'+para(('Top is on the right. The shortage scenario begins after six nested CALLs; this toy discards the oldest two predictions and consumes the four remaining entries. It assumes an affected Intel-like alternate predictor pre-associated with G. Real RSB overflow/underflow bookkeeping varies; this is not an AMD Retbleed model or a universal RSB design.','右侧为栈顶。预测不足场景从六层 CALL 后开始；教学模型丢弃最早两个预测，逐步消费剩下四项。假设受影响的 Intel 类替代预测器已关联 G。真实 RSB 的溢出 / 下溢管理因 CPU 而异；这不是 AMD Retbleed 模型，也不是通用 RSB 设计。'))+'<p class="model-stack-label">'+t(('Architectural software stack','正式软件栈'))+'</p><div data-software></div><p class="model-stack-label">RSB</p><div data-rsb></div>'+buttons(4)+readout()+'</div>'
  s+=para(('In the capacity-4 example, after four returns there are still two valid software return addresses, but no useful prediction entries. The next RET can consult the affected alternate predictor: its speculative G is separate from the real stack target R2. Prediction shortage alone does not create a leak; a malicious target association, a usable gadget and an observation channel are additional requirements.','容量 4 的例子中，返回四次后，软件栈仍有两个有效返回地址，但可用预测项已耗尽。下一条 RET 可查询受影响的替代预测器：其推测目标 G 与真实栈目标 R2 是两回事。只有预测不足还不会自动泄露；还需要恶意目标关联、可用 gadget 和观察通道。'))
  s+=title(('RSBA is not the same as RRSBA', 'RSBA 与 RRSBA 不应混为一谈'))
  s+=para(('Intel calls unrestricted alternate-return prediction RSBA. RRSBA restricts eligible alternate targets to the current prediction domain when eIBRS applies. This does not make all target/history risks disappear; the applicable RRSBA_DIS controls and history defenses depend on the CPU and software configuration. Do not copy the original Intel Retbleed conditions onto all newer CPUs.','Intel 用 RSBA 表示非受限的替代返回预测；RRSBA 则在适用的 eIBRS 条件下把替代目标限制在当前预测域。这不等于消除所有目标 / 历史风险；适用的 RRSBA_DIS 控制与历史防护仍取决于 CPU 和软件配置。不能把原始 Intel Retbleed 条件直接套到所有更新 CPU。'))
  s+='<p class="prediction-references"><a href="https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/advisory-guidance/return-stack-buffer-underflow.html" target="_blank" rel="noopener noreferrer">Intel · RSBA / RRSBA</a> · <a href="https://docs.kernel.org/admin-guide/hw-vuln/rsb.html" target="_blank" rel="noopener noreferrer">Linux · RSB poisoning / underflow</a></p>'
 s+=title(('One comparison: what is being manipulated?', '放在一起看：究竟操纵了什么？'))
 s+=table([('Mechanism','机制'),('Relevant manipulated state','相关操纵状态'),('Do not confuse it with','不要混淆为')],[
 [('Classic BTI','经典 BTI'),('Target association under matching/aliasing conditions','匹配 / 别名条件下的目标关联'),('Not any jump to any G','不是随便跳到 G 就能影响受害者')],
 [('BHI','BHI'),('History used to select eligible learned targets','选择允许域内已学习目标时的历史'),('Still needs useful learned target state','仍需要有用的已学习目标状态')],
 [('Spectre-RSB / ret2spec','Spectre-RSB / ret2spec'),('Return-prediction entries out of sync with real returns','返回预测项与真实返回不一致'),('Not a software-stack overwrite','不是覆盖软件栈返回地址')],
 [('Intel Retbleed: evaluated path','Intel Retbleed：原评估路径'),('Usable RSB shortage + alternate target poisoning','可用 RSB 不足 + 替代目标关联污染'),('Not necessarily malicious entries in RSB','不一定是把恶意地址压入 RSB')],
 [('AMD Retbleed: evaluated path','AMD Retbleed：原评估路径'),('Branch-type / target prediction confusion at RET','RET 处的分支类型 / 目标预测混淆'),('No universal empty-RAS requirement','不要求 RAS 一定先变空')],
 ])
 s+=para(('“BTI changes the value; BHI changes the lookup context” is a useful memory aid, not a strict hardware taxonomy. Target learning, history and predictor selection interact; BHI is a way to realize BTI, not a disjoint class.','“BTI 偏向改变值，BHI 偏向改变查找上下文”可以帮助记忆，但不是严格的硬件分类定理。目标学习、历史与预测器选择相互影响；BHI 是实现 BTI 的一种方式，不是完全互斥的类别。'))
 if id=='retbleed':
  s+=title(('RISC-V: ISA hints versus microarchitectural security', 'RISC-V：ISA 提示不等于微架构安全保证'))
  s+=para(('The conventional ret pseudoinstruction is jalr x0, x1, 0: its architectural destination is calculated from x1, not popped from an x86-style memory return stack. The RAS is only a prediction structure. RISC-V specifies call/return usage hints through link-register operands x1/x5; it does not require every implementation to use one RAS design or to exhibit Intel/AMD Retbleed.','惯例中的 ret 伪指令为 jalr x0, x1, 0：正式目标由 x1 计算，不是从 x86 式内存返回栈弹出。RAS 只是预测结构。RISC-V 通过 x1 / x5 等链接寄存器操作数表达调用 / 返回用途提示，但不要求所有实现采用相同 RAS，更不意味着必然存在 Intel / AMD Retbleed。'))
  s+=table([('Instruction example','指令示例'),('RAS hint','RAS 提示')],[[(a,a),(b,{'Push':'压入','Pop':'弹出','None':'无','Pop, then push':'先弹出，再压入'}[b])] for a,b in [('jal x1, target','Push'),('jal x5, target','Push'),('jalr x1, x10, 0','Push'),('jalr x0, x1, 0','Pop'),('jalr x0, x10, 0','None'),('jalr x5, x1, 0','Pop, then push'),('jalr x1, x1, 0','Push')]])
  s+=para(('For a concrete RISC-V core, evaluate which domains share target/history/RAS state, how type and fallback selection work, and which state a transition flushes or restricts. These are review questions, not a vulnerability claim. Memory-access isolation alone does not demonstrate predictor-state isolation.','评估具体 RISC-V 核心时，应检查目标 / 历史 / RAS 状态在哪些域间共享、分支类型与替代路径如何选择、转换时哪些状态被清理或限制。这些是设计审查问题，不是漏洞结论。仅证明内存访问隔离，不能证明预测状态也得到隔离。'))
  s+='<p class="prediction-references"><a href="'+RISCV+'" target="_blank" rel="noopener noreferrer">RISC-V ISA · JAL / JALR return-address stack hints</a></p>'
 s+='<nav class="lesson-links" aria-label="'+t(('Related worked examples','相关具体例子'))+'">'+''.join('<a href="case-'+case+('.zh' if zh else '')+'.html#worked-models">'+label+'</a>' for case,label in [('spectre-v2','BTI'),('bhi','BHI'),('retbleed','RSB / Retbleed')] if case!=id)+'</nav><noscript><p>'+t(('Interactive controls require JavaScript; the code, comparison tables and explanations remain readable without it.','交互控件需要 JavaScript；关闭时仍可阅读代码、对照表与解释。'))+'</p></noscript></section>'
 return s
