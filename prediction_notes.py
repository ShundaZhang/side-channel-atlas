# -*- coding: utf-8 -*-
"""Prerequisite concepts and causal examples for prediction-related vulnerabilities."""
from html import escape as e

RELATED={'spectre-v2','bhi','retbleed','inception'}
GLOSSARY=[
('branch-kinds', ('Direct, indirect, conditional: different questions', '直接、间接、条件分支：回答的是不同问题'),
 ('A direct branch encodes its destination in the instruction, usually as a PC-relative displacement. An indirect branch gets its architectural destination from a register or memory operand: call rax, jmp [slot], a callback or a virtual function. A conditional branch asks whether to take a branch; an indirect-target predictor asks where to go. These are separate prediction questions. Here the x86-64 example call rax means “call the address held in RAX,” not “call the address where this instruction resides.”',
 '直接分支把目的地编码在指令中，通常采用相对 PC 的位移。间接分支从寄存器或内存操作数取得正式目标，例如 call rax、jmp [slot]、回调和虚函数调用。条件分支预测回答“跳不跳”，间接目标预测回答“跳到哪里”，两者不是同一个问题。以下 x86-64 示例 call rax 是“调用 RAX 中保存的地址”，不是调用这条指令自身所在的地址。')),
('target-vs-prediction', ('Real target, predicted target and gadget', '真实目标、预测目标与 gadget'),
 ('The real target follows the program’s operands and ISA rules. The predicted target lets the front end fetch before those operands are ready. On a mismatch, wrong-path instructions are squashed, but a data-dependent cache effect can survive. A gadget is existing code whose transient execution can produce such an observable effect; merely landing at a wrong target does not establish disclosure.',
 '真实目标由程序操作数和 ISA 规则决定；预测目标让前端能在操作数未就绪时先取指。两者不一致时，错误路径指令被取消，但与数据相关的缓存效应可能保留。gadget 是可在瞬态执行时产生这类可观察效应的现有代码；仅仅跳错目标，还不能证明发生信息泄露。')),
('btb', ('BTB / target-prediction state', 'BTB / 目标预测状态'),
 ('BTB means Branch Target Buffer. At a teaching level, target-prediction state associates branch contexts with likely code destinations. Aliasing means different branch source addresses or contexts can collide in the predictor’s finite indexing/tagging logic; it does not mean the full virtual addresses are equal. Modern predictors have several structures and selection rules: the examples below are logical models, not a claim that every CPU has one PC→target table.',
 'BTB 即 Branch Target Buffer（分支目标缓冲区）。教学上可把目标预测状态理解为“分支上下文 → 可能的代码目标”的关联。别名 / 碰撞指不同分支源地址或上下文，在预测器有限的索引 / 标签逻辑中重合，不要求完整虚拟地址相同。现代预测器包含多种结构和选择规则；下文只是逻辑模型，不是声称每个 CPU 都只有一张 PC→目标表。')),
('history', ('BHB / history is context, not the function pointer', 'BHB / 历史是上下文，不是函数指针'),
 ('The Branch History Buffer tracks recent control-flow information used in prediction. What is recorded or compressed is implementation-specific; H_A and H_G below name contexts, not literal bit strings that software can write to a BHB register. Executing branches changes history, and history can change which learned target entry is selected. It does not rewrite the function pointer or the actual result of a comparison.',
 'BHB（Branch History Buffer，分支历史缓冲区）记录用于预测的近期控制流信息。具体记录和压缩方式依实现而异；下文 H_A、H_G 是上下文标签，不是软件可直接写入“BHB 寄存器”的比特串。执行分支会改变历史，历史可改变选中的已学习目标项，但不会改写函数指针，也不会改变比较表达式的真实结果。')),
('training-meaning', ('“Training data” means executed branch events here', '这里的“训练数据”是执行过的分支事件'),
 ('This is not ML training on a supplied file of secret bytes. Software exercises control flow: branch source PC, observed destination, branch type, recent history and prediction domain matter. Repetition can establish predictor associations, but arbitrary repeated jumps do not necessarily train a chosen victim branch. Matching/aliasing, processor behavior, barriers, domain restrictions and scheduling determine whether the training transfers. Secret data is consumed later by a disclosure gadget; it is not the training label.',
 '这里不是把秘密字节文件交给机器学习模型训练，而是让软件实际执行控制流：分支源 PC、观察到的目的地、分支类型、近期历史和预测域等因素参与其中。重复执行可建立预测关联，但不是随便重复跳转就能训练指定的受害者分支；是否迁移取决于匹配 / 别名、CPU 行为、屏障、域限制和调度。秘密数据由后面的泄漏 gadget 消费，不是训练标签。')),
]
RSB=(('RSB is a prediction stack, not the software stack', 'RSB 是预测栈，不是软件栈'),
 ('On a normal x86 near CALL, the architectural stack records the address of the instruction after CALL. Separately, a Return Stack Buffer usually tracks expected return destinations in a small hardware prediction stack: CALL conceptually pushes a prediction and RET consumes one. RET’s architectural destination still comes from the software stack. RSB entries accelerate fetching; they do not grant permission or replace that stack. AMD documentation may call related structures RAS/RAP. RSB is also distinct from the CET shadow stack, which is an architectural protection mechanism.',
 '正常 x86 near CALL 会把 CALL 后一条指令的地址写入正式软件栈。与此同时，RSB（Return Stack Buffer，返回栈缓冲区）通常以小型硬件预测栈跟踪预计的返回目的地：概念上 CALL 压入预测，RET 消费预测。RET 的正式目的地仍来自软件栈。RSB 只加速取指，不提供访问权限，也不替代软件栈；AMD 资料还可能使用 RAS / RAP 等名称。RSB 也不是 CET shadow stack，后者是架构层的保护机制。'))

# Independent, labelled examples: not a processor configuration or executable exploit.
NORMAL_RSB=('''CALL f       software stack: [R_main]         RSB: [R_main]
f: CALL g    software stack: [R_main, R_f]    RSB: [R_main, R_f]
g: RET       actual = R_f                    predict = R_f
f: RET       actual = R_main                 predict = R_main
# capacity / overflow policy is CPU-specific; this is only a logical trace''',
'''CALL f       软件栈：[R_main]          RSB：[R_main]
f: CALL g    软件栈：[R_main, R_f]     RSB：[R_main, R_f]
g: RET       正式返回 R_f             预测返回 R_f
f: RET       正式返回 R_main          预测返回 R_main
# 容量和溢出策略取决于 CPU；这里只跟踪逻辑关系''')

DETAILS={
'retbleed':[
(('What does RSB underflow actually mean?', 'RSB 下溢到底是什么意思？'),
 ('The RSB has finite prediction capacity. Deep nesting can lose older predictions; unbalanced calls/returns or context transitions can also make prediction entries unavailable or mismatched. “Underflow” here means RET lacks a usable return-stack prediction, not that RSP points outside valid memory or that the software stack lost R_OK. For the evaluated Intel Skylake-family behavior, the processor can then use alternate indirect-target prediction. Do not assign one universal RSB depth to all CPUs.',
 'RSB 的预测容量有限，深层调用可能丢失较早的预测；CALL / RET 不配对或上下文转换也可能使预测项不可用或失配。这里“下溢”指 RET 缺少可用的返回栈预测，不是 RSP 越出有效内存，更不是软件栈丢失了 R_OK。研究涉及的 Intel Skylake 家族行为中，此时可改用间接目标的替代预测路径。不能给所有 CPU 指定同一个 RSB 深度。')),
(('How the target is trained', '目标究竟怎样被训练'),
 ('Teaching sequence: (1) execute a training-side indirect branch at source S toward code target G; (2) on an affected CPU, S and the victim RET location T alias in relevant target-prediction state, so a G association can influence T; (3) reach T while its affected return-prediction condition holds; (4) the front end predicts G although the software stack still contains R_OK. S, T and G are three code addresses with different roles. Finding the required alias/context is processor-specific; no universal address equality or history recipe is implied.',
 '教学过程：① 训练侧在源位置 S 执行以代码地址 G 为目的地的间接分支；② 在受影响 CPU 上，S 与受害者 RET 所在位置 T，在相关目标预测状态中发生别名，G 的关联因而可能影响 T；③ 在受影响的返回预测条件下到达 T；④ 前端先预测到 G，而软件栈仍保存 R_OK。S、T、G 是三种不同角色的代码地址。所需别名 / 上下文的构造依具体 CPU 而定，不意味着源地址必须完全相等，也不存在通用历史配方。')),
(('Why a kernel target can enter prediction state', '为什么训练可能涉及内核代码地址'),
 ('The original Retbleed researchers observed target-prediction updates even for attempted branches to inaccessible kernel addresses on their affected systems. An architectural fault therefore did not imply that prediction state was unchanged. This is an implementation-specific research observation, not permission to execute kernel code and not a universal property of branches. Ordinary CALL-based RSB tracking and poisoning an alternate target predictor are different mechanisms.',
 '原 Retbleed 研究观察到：在其受影响系统上，即使尝试跳到不可访问的内核地址会造成正式故障，目标预测状态仍可能被更新。因此“正式执行失败”不等于“预测状态未变化”。这是特定实现上的研究观察，不是获得内核代码执行权限，也不是所有分支的通用行为。普通 CALL 跟踪 RSB 与污染替代目标预测器，是不同机制。')),
(('Intel and AMD must be explained separately', 'Intel 与 AMD 必须分开解释'),
 ('Intel in the original evaluated setting: insufficient usable RSB predictions enable an alternate target-prediction path; poisoned target state then matters. AMD Zen 1/2 in the original evaluation: a colliding indirect branch can cause branch-type confusion so a RET is predicted like an indirect branch, without first emptying the RAS. This is why “empty RSB → poisoned BTB” is useful for one path but is not the definition of all Retbleed variants.',
 '原研究涉及的 Intel 路径：可用 RSB 预测不足，使 RET 使用替代目标预测，随后被污染的目标状态才产生影响。原评估中的 AMD Zen 1 / 2 路径：碰撞的间接分支可造成分支类型混淆，使 RET 像间接分支一样被预测，并不要求先清空 RAS。因此“RSB 空 → 使用被污染的 BTB”适合解释一条路径，不能当成所有 Retbleed 变体的定义。')),
(('From a wrong return to an actual leak', '从返回误预测到实际泄露，还差什么'),
 ('At G, the transient gadget must have useful victim data/operands and make a secret-dependent observable effect. The real stack target subsequently resolves to R_OK and the wrong path is squashed; a separate observation reads the trace. The secret is neither pushed into the RSB nor used to train it. Retpoline relies on controlling return speculation; Retbleed shows why the safety of that assumption depends on the return predictor, platform and mitigation state.',
 'G 处的瞬态 gadget 仍须获得有用的受害者数据 / 操作数，并留下与秘密有关的可观察效应。随后真实栈目标解析为 R_OK，错误路径被取消，再由独立观察读取痕迹。秘密既没有压入 RSB，也不是训练 RSB 的数据。Retpoline 依靠控制返回推测；Retbleed 说明这个假设是否安全，取决于返回预测器、平台与缓解状态。')),
],
'bhi':[
(('First define the victim indirect branch', '先明确受害者的间接分支'),
 ('Example: fp = handlers[id]; call fp at PC J. The current id and handlers array determine the real target NORMAL. Before fp arrives, target prediction may choose G. Changing prior branch history does not change id, handlers or fp. The “candidates” are learned target associations inside prediction machinery, not alternative values of a program-level if condition.',
 '例如 fp = handlers[id]，然后在位置 J 执行 call fp。当前 id 与 handlers 表共同决定真实目标 NORMAL；fp 未就绪时，目标预测却可能先选 G。改变此前的分支历史，不会改变 id、handlers 或 fp。“候选目标”是预测机制内已学习的目标关联，不是程序里某个 if 的真假条件。')),
(('Two different preparations: seed a target, then shape history', '两个不同的准备：建立目标关联，再构造历史'),
 ('First, the relevant prediction domain must have a useful target association. In the original kernel demonstration, kernel-executed eBPF provided a disclosure gadget and a way to populate relevant prediction state. More generally, an appropriate in-domain branch/gadget path is needed; later research also found paths without eBPF. Second, the attacker executes a branch sequence to shape history before entering the victim domain. These phases modify different logical inputs: the learned target state versus the history used to select it.',
 '首先，相关预测域内必须存在有用的目标关联。原内核演示借助在内核执行的 eBPF 提供泄漏 gadget，并建立相关预测状态；一般来说，需要合适的同域分支 / gadget 路径，后续研究也找到了不依赖 eBPF 的路径。其次，攻击者在进入受害者域前执行一段分支序列，改变近期历史。这两个阶段影响不同的逻辑输入：前者建立已学习目标状态，后者影响选目标时使用的历史。')),
(('What “history chooses a candidate” means', '“历史选择候选目标”具体是什么意思'),
 ('Use the conceptual expression Predict(J, H, mode, learned_state). Holding J, the real fp and learned_state fixed, H_A can select NORMAL while a matching H_G can select an already-learned G association. A real predictor may use folded history, tags, multiple tables or confidence; this expression is not a physical two-table design or a guarantee that arbitrary history selects arbitrary G. Calls, transitions and intervening branches also affect the history that actually reaches J.',
 '用概念式 Predict(J, H, mode, learned_state) 表示目标预测。保持 J、真实 fp 和已学习状态不变，H_A 可能选 NORMAL，而匹配的 H_G 可能选中已学习的 G 关联。真实预测器可能使用折叠历史、标签、多张表及置信度；该式不是固定的“两张硬件表”，更不是任意历史可选任意 G 的保证。调用、域切换及中间分支，也会影响最终到达 J 的实际历史。')),
(('Why eIBRS is not the same as history isolation', '为什么 eIBRS 不等于历史隔离'),
 ('In the affected eIBRS setting, targets learned in a less privileged predictor mode are restricted from directly supplying privileged predictions. Yet history can still include less-privileged branch activity. BHI uses that influence to select a target entry belonging to the victim’s allowed prediction domain; it does not simply smuggle an arbitrary user-mode target through eIBRS. Cross-mode BHI and the broader intra-mode BTI category must therefore be distinguished.',
 '在受影响的 eIBRS 场景中，较低特权预测模式学习的目标受到限制，不能直接用来供应高特权预测；但历史仍可能包含较低特权分支活动。BHI 借这部分影响，选中属于受害者允许预测域的目标项，而不是简单地把任意用户态目标穿过 eIBRS 塞进内核。应区分跨模式的 BHI 与范围更大的同模式 BTI。')),
(('What the training inputs are not', '训练输入不是什么'),
 ('The key inputs are executed branches and their context, not the secret, a new function pointer, or an out-of-bounds index. Replaying a matching history can bias selection; it does not authorize execution of G or change the real call target. A useful gadget and a receiver are still required. History-clearing entry sequences or applicable BHI_DIS_S controls break this history influence; target/domain defenses and gadget hardening address other links in the chain.',
 '关键输入是执行过的分支及其上下文，不是秘密、新函数指针或越界索引。重放匹配历史可使选择偏向某个目标，但不会赋予 G 执行权限，也不会改变真实调用目标。仍须有可用 gadget 和接收通道。入口历史清理序列或适用的 BHI_DIS_S 控制切断历史影响；目标 / 域防护与 gadget 加固则切断链条中的其他环节。')),
],
}

TABLES={
'retbleed': dict(headers=[('Phase','阶段'),('Software stack','软件栈'),('Prediction state','预测状态'),('What changes?','改变了什么')], rows=[
 [('Ordinary CALL / RET','普通 CALL / RET'),('R_OK','R_OK'),('RSB predicts R_OK','RSB 预测 R_OK'),('Actual = predicted','真实 = 预测')],
 [('Target training','目标训练'),('Victim R_OK unchanged','受害者 R_OK 不变'),('S → G association may alias T','S → G 的关联可能与 T 别名'),('Code-target association','代码目标关联')],
 [('Intel affected path','Intel 受影响路径'),('R_OK remains valid','R_OK 仍有效'),('No usable RSB prediction → alternate target','无可用 RSB 预测 → 替代目标路径'),('Prediction source','预测来源')],
 [('AMD evaluated path','AMD 原评估路径'),('R_OK remains valid','R_OK 仍有效'),('Type confusion can affect RET despite RAS','RAS 不必空，类型混淆也可影响 RET'),('Branch type / target prediction','分支类型 / 目标预测')],
 [('Resolve / recover','解析 / 恢复'),('Return to R_OK','返回 R_OK'),('Wrong-path G is discarded','取消错误路径 G'),('Trace may survive','痕迹可能保留')],
 ]),
'bhi':dict(headers=[('Phase','阶段'),('Target state','目标状态'),('History','历史'),('Actual target','真实目标')],rows=[
 [('Seed in-domain targets','建立同域目标关联'),('Useful NORMAL / G associations learned','学习有用的 NORMAL / G 关联'),('Training contexts','训练时上下文'),('Targets of seed branches','训练分支的实际目标')],
 [('Control comparison','对照'),('Keep learned state fixed','保持已学习状态不变'),('H_A → predict NORMAL','H_A → 预测 NORMAL'),('NORMAL','NORMAL')],
 [('Attacker branch sequence','攻击者分支序列'),('No arbitrary new privileged G','不凭空新增任意特权目标 G'),('Shape history toward H_G','使历史接近匹配的 H_G'),('Future fp unchanged','未来 fp 不变')],
 [('Victim J before resolution','受害者 J 尚未解析'),('Select an eligible G entry','选中允许域内的 G 项'),('Matching history can bias selection','匹配历史可影响选择'),('Still NORMAL','仍为 NORMAL')],
 [('Resolve / recover','解析 / 恢复'),('Discard transient G execution','取消 G 的瞬态执行'),('Does not rewrite program operands','不改写程序操作数'),('Execute NORMAL','执行 NORMAL')],
 ])}

REFERENCES=[('Linux: RSB and return prediction', 'https://docs.kernel.org/admin-guide/hw-vuln/rsb.html'),('Retbleed: paper and CPU-specific explanation','https://comsec.ethz.ch/research/microarch/retbleed/'),('Retbleed original paper','https://comsec.ethz.ch/wp-content/files/retbleed_sec22.pdf'),('Intel: BHB / BHI background and controls','https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/branch-history-injection.html'),('BHI: original paper','https://www.usenix.org/system/files/sec22-barberis.pdf')]

def prerequisites(case,zh):
 if case['id'] not in RELATED:return ''
 def t(v):return v[1 if zh else 0]
 s='<section id="prerequisites"><h2>'+t(('Prerequisites: read these concepts first','前置概念：先分清这些东西'))+'</h2><p>'+t(('The examples use x86 control flow. Prediction structures are not architectural data stores and “training” is not ML training.','以下以 x86 控制流为例。预测结构不是架构数据存储，“训练”也不是机器学习训练。'))+'</p><div class="prediction-concepts">'
 for id,title,body in GLOSSARY:
  s+='<div id="concept-'+id+'"><h3>'+e(t(title))+'</h3><p>'+e(t(body))+'</p></div>'
 if case['id'] in {'retbleed','inception'}:
  s+='<div id="concept-rsb"><h3>'+e(t(RSB[0]))+'</h3><p>'+e(t(RSB[1]))+'</p><pre class="case-trace"><code>'+e(t(NORMAL_RSB))+'</code></pre></div>'
 s+='</div><p class="prediction-references">'+t(('Primary background: ','一手背景资料：'))+' · '.join('<a href="'+url+'" target="_blank" rel="noopener noreferrer">'+e(label)+'</a>' for label,url in REFERENCES)+'</p></section>'
 return s

def training_details(case,zh):
 id=case['id']
 if id not in DETAILS:return ''
 def t(v):return v[1 if zh else 0]
 s='<p class="prediction-references">'+t(('Concept lookup: ','概念回看：'))+' · '.join('<a href="#concept-'+key+'">'+label+'</a>' for key,label in ([('rsb','RSB / '+t(('software stack','软件栈')))] if id=='retbleed' else [])+[('branch-kinds',t(('indirect branch','间接分支'))),('btb','BTB'),('history','BHB'),('training-meaning',t(('training','训练')))])+'</p>'
 for title,body in DETAILS[id]:s+='<h3>'+e(t(title))+'</h3><p>'+e(t(body))+'</p>'
 table=TABLES[id]
 s+='<div class="case-table" tabindex="0" role="region" aria-label="'+t(('Training and execution comparison','训练与执行对照'))+'"><table><thead><tr>'+''.join('<th scope="col">'+e(t(h))+'</th>' for h in table['headers'])+'</tr></thead><tbody>'
 for row in table['rows']:s+='<tr>'+''.join('<td>'+e(t(cell))+'</td>' for cell in row)+'</tr>'
 return s+'</tbody></table></div>'
