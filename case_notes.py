# -*- coding: utf-8 -*-
"""Bilingual original teaching notes. Values and traces are illustrative, not PoCs."""
SOURCES={
'spectre':('Spectre · §4 / §5','https://arxiv.org/abs/1801.01203'),
'linux-spectre':('Linux · Spectre','https://docs.kernel.org/admin-guide/hw-vuln/spectre.html'),
'meltdown':('Meltdown · §3 / §5.1','https://www.usenix.org/conference/usenixsecurity18/presentation/lipp'),
'pti':('Linux · Page Table Isolation','https://docs.kernel.org/arch/x86/pti.html'),
'foreshadow':('Foreshadow · original research','https://www.usenix.org/conference/usenixsecurity18/presentation/bulck'),
'l1tf':('Linux · L1TF','https://docs.kernel.org/admin-guide/hw-vuln/l1tf.html'),
'mds':('Linux · MDS','https://docs.kernel.org/admin-guide/hw-vuln/mds.html'),
'ridl':('RIDL · original paper','https://mdsattacks.com/files/ridl.pdf'),
'lvi':('Intel · Load Value Injection','https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/load-value-injection.html'),
'lvi-paper':('LVI · original paper','https://gruss.cc/files/lvi.pdf'),
'ssb':('Intel · Speculative Store Bypass','https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/advisory-guidance/speculative-store-bypass.html'),
'ssb-ms':('Microsoft · SSB analysis','https://www.microsoft.com/en-us/msrc/blog/2018/05/analysis-and-mitigation-of-speculative-store-bypass-cve-2018-3639/'),
'exp-tsx':('Linux · TSX Asynchronous Abort','https://docs.kernel.org/admin-guide/hw-vuln/tsx_async_abort.html'),
'zombieload':('ZombieLoad · original research','https://www.zombieload.com/zombieload.pdf'),
'bhi':('Intel · BHI / Intra-mode BTI','https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/branch-history-injection.html'),
'bhi-paper':('BHI · original research','https://www.usenix.org/conference/usenixsecurity22/presentation/barberis'),
'retbleed':('ETH COMSEC · Retbleed','https://comsec.ethz.ch/research/microarch/retbleed/'),
'rsb':('Linux · RSB mitigations','https://docs.kernel.org/admin-guide/hw-vuln/rsb.html'),
'gds':('Linux · Gather Data Sampling','https://docs.kernel.org/admin-guide/hw-vuln/gather_data_sampling.html'),
'downfall':('Downfall · original paper and talk','https://www.usenix.org/conference/usenixsecurity23/presentation/moghimi'),
'rfds':('Linux · Register File Data Sampling','https://docs.kernel.org/admin-guide/hw-vuln/reg-file-data-sampling.html'),
'srso':('Linux · Speculative Return Stack Overflow','https://docs.kernel.org/admin-guide/hw-vuln/srso.html'),
'inception':('ETH COMSEC · Inception','https://comsec.ethz.ch/research/microarch/inception/'),
'zenbleed-author':('Tavis Ormandy · Zenbleed mechanism','https://lock.cmpxchg8b.com/zenbleed.html'),
'zenbleed':('Google · Zenbleed original research','https://github.com/google/security-research/blob/master/pocs/cpus/zenbleed/README.md'),
'amd-zenbleed':('AMD-SB-7008','https://www.amd.com/en/resources/product-security/bulletin/amd-sb-7008.html'),
}
# Each pair is (English, Chinese). Traces are independently written semantic models.
CASES=[
 dict(id='spectre-v1',name='Spectre V1 · Bounds Check Bypass',year=2018,cve='CVE-2017-5753',family='prediction',refs=['spectre','linux-spectre'],
 thesis=('A conditional check eventually fails, but its predicted pass path may already have used an out-of-bounds value.','条件检查最终失败，但被预测为通过的路径，可能已短暂使用越界值。'),
 trigger=('Unresolved conditional branch','条件分支尚未确定'),source=('Victim-accessible array data','受害者可访问的数组数据'),formal=('Reject x = 16 when size = 16','size = 16 时拒绝 x = 16'),transient=('Predicted pass; use array1[16]','预测通过，短暂使用 array1[16]'),
 mechanism=('A byte array starts at teaching address 0x1000 and has 16 elements. Legal indices 0–15 refer to 0x1000–0x100F. Inputs such as 2, 5 and 9 make the same check pass. If x is then 16 while the comparison is unresolved, prediction can temporarily enter the check’s body. The real comparison still rejects it. Only a data-dependent, observable side effect makes this a disclosure path.',
 '假设字节数组从教学地址 0x1000 开始，长度为 16。合法索引 0–15 对应 0x1000–0x100F；2、5、9 等输入会使同一检查通过。本次 x = 16 时，比较尚未完成，预测可能先进入 if 主体。真实比较仍会拒绝。只有后续操作留下与该值相关且可观察的痕迹，才可能形成泄漏链。'),
 training=('Legal inputs bias branch-outcome history. The predictor does not memorize a list of permitted indices or evaluate x < 16 itself. Source-level “pass” need not mean a taken machine branch; compilation can invert the branch direction.',
 '训练输入使用合法索引，让预测器经常观察到检查通过。预测器不是记住合法索引列表，也不是提前算出 x < 16。源码中的“通过”不一定是机器指令的 taken，编译器可以把跳转方向反过来。'),
 boundary=('The attacker needs an influenceable input, a reachable victim gadget and an observable channel. The basic example crosses a software object or sandbox check within the victim’s accessible address space; it does not make a forbidden kernel page architecturally readable.',
 '需要可影响的输入、可触达的受害者 gadget 和可观察通道。基本例子越过的是受害者可访问地址空间中的软件对象或沙箱检查，不是使页表禁止访问的内核页成为合法读取。'),
 mitigation=('Harden the relevant dependency and speculation boundary with platform-appropriate barriers, index handling or compiler transformations. Review the generated code and the particular check. A system-wide Spectre-V1 status is not a proof that every application gadget is hardened.',
 '按平台使用屏障、索引处理或编译器变换，约束相关依赖访问和推测边界。应检查生成代码与具体条件。系统级 Spectre-V1 状态不能证明所有应用 gadget 都已加固。'),
 contrast=('V1 predicts a direction. V2 predicts an indirect target. Neither example requires the load-permission failure central to classic Meltdown.',
 'V1 预测方向，V2 预测间接目标；两者的这个例子都不依赖经典 Meltdown 中的读取权限失败。'),
 trace=('''[01] array1_size = 16; x = 16
[02] if x < array1_size:          # condition is not ready yet
[03]     value = array1[x]       # belongs inside the pass path
[04]     observe_placeholder(value)
[05] transient possibility: predicted pass reaches [03]–[04]
[06] architectural result: condition is false; discard that path''','''[01] array1_size = 16；本次 x = 16
[02] if x < array1_size:         # 条件尚未确定
[03]     value = array1[x]       # 写在通过路径内
[04]     使用该值的占位操作(value)
[05] 可能的瞬态过程：预测通过，先执行 [03]–[04]
[06] 正式结果：条件为假，取消错误路径'''),
 read=('Compare the paper’s §4 boundary check with the x values above. Separate history-building inputs from the violating input, then find the dependent disclosure operation. The placeholder here deliberately leaves out the cache encoder and timing receiver.',
 '对照论文 §4 的边界检查，分别找出用于建立偏向的输入与越界触发输入，再寻找依赖于秘密值的泄漏操作。这里的占位操作有意省略缓存编码器与计时接收端。')),
 dict(id='spectre-v2',name='Spectre V2 · Branch Target Injection',year=2018,cve='CVE-2017-5715',family='prediction',refs=['spectre','linux-spectre'],
 thesis=('The real function pointer stays intact; the CPU may temporarily fetch instructions from a different predicted target.','真实函数指针未被改写，CPU 却可能先从另一个预测目标取指。'),
 trigger=('Indirect target not ready','间接分支真实目标未就绪'),source=('Victim code at predicted gadget','预测目标处的受害者代码'),formal=('Branch to NORMAL','正式转到 NORMAL'),transient=('Execute GADGET first','短暂先执行 GADGET'),
 mechanism=('Keep three code addresses separate: the indirect branch at 0x401240, the real target 0x402180, and a desired predicted gadget at 0x4030A0. These are teaching addresses in the victim’s virtual address space. Before the true target resolves, target prediction can redirect transient execution to the gadget. Resolution restores the correct destination; it does not undo every microarchitectural effect of the wrong path.',
 '区分三个代码地址：间接分支位置 0x401240、真实目标 0x402180、希望预测到的 gadget 0x4030A0。它们均为受害者虚拟地址空间中的教学地址。真实目标尚未确定时，目标预测可能使 CPU 先执行 gadget；解析完成后恢复正确去处，但未必抹掉错误路径留下的所有微架构影响。'),
 training=('The attacker influences target-prediction state and applicable history/context. The mapping of branch PCs, histories and targets is implementation-specific. Do not assume the attacker’s training-side address must equal the victim gadget’s full virtual address.',
 '被影响的是目标预测状态以及适用的历史 / 上下文。分支位置、历史与目标的关联依赖实现，不能假设攻击者训练侧的地址必须与受害者 gadget 的完整虚拟地址相同。'),
 boundary=('A usable gadget must read victim-accessible data and encode an observable effect. Cross-process, user/kernel and guest/host attacks have different predictor-sharing and execution prerequisites. Merely causing a target misprediction is not yet secret recovery.',
 '可用 gadget 还要访问受害者能读的数据，并留下可观察痕迹。跨进程、用户 / 内核和客户机 / 宿主场景的预测器共享及执行条件不同。仅产生目标误预测，不等于已恢复秘密。'),
 mitigation=('Use the CPU- and boundary-specific combination of indirect-branch hardening and predictor controls, such as applicable retpoline, IBRS/eIBRS, IBPB and STIBP. These mechanisms act at different places; later BHI and return-prediction findings limit blanket claims about any one defense.',
 '按 CPU 与边界组合使用间接分支加固和预测器控制，例如适用的 retpoline、IBRS/eIBRS、IBPB 与 STIBP。它们作用位置不同，后续 BHI 和返回预测研究也说明单项防御不宜被概括为通用修复。'),
 contrast=('The gadget address is code, not the secret-data address. BTI changes prediction, not the architecturally stored function pointer.',
 'gadget 地址是代码地址，不是秘密数据地址。BTI 改变预测，不是永久改写函数指针。'),
 trace=('''[01] branch PC = 0x401240
[02] real_target = NORMAL        # 0x402180
[03] predict_target() = GADGET   # 0x4030A0, teaching label
[04] transient: GADGET uses victim data
[05] resolve real_target
[06] architectural: execute NORMAL; discard wrong path''','''[01] 分支指令位置 = 0x401240
[02] 真实目标 = NORMAL           # 0x402180
[03] 预测目标 = GADGET           # 0x4030A0，教学标签
[04] 瞬态：GADGET 使用受害者数据
[05] 真实目标就绪
[06] 正式：执行 NORMAL，取消错误路径'''),
 read=('In Spectre §5, distinguish the indirect jump instruction, its eventual operand, and the code reached by prediction. Then ask which domain supplied predictor state and which domain supplies the data.',
 '读 Spectre §5 时，将间接跳转指令、最终操作数及预测到的代码分开，再问：预测状态来自哪个域，数据又来自哪个域？')),
 dict(id='meltdown',name='Meltdown V3 · Rogue Data Cache Load',year=2018,cve='CVE-2017-5754',family='fault',refs=['meltdown','pti'],
 thesis=('A load still faults, but affected hardware may already have forwarded the protected byte to dependent transient instructions.','读取仍会故障，但受影响硬件可能已把受保护字节交给后续瞬态依赖指令。'),
 trigger=('Load lacks user permission','读取缺少用户态权限'),source=('Data behind a protected mapping','受保护映射中的数据'),formal=('Permission page fault; no byte committed','权限页故障，不提交该字节'),transient=('Dependent operation uses the byte','依赖操作短暂使用该字节'),
 mechanism=('First separate two examples. An independent operation below a faulting instruction can execute early without consuming the fault’s result. Classic Meltdown’s disclosure chain is stronger: it needs a dependent operation to receive the byte from the denied load. A later architectural exception does not prove that permission checking itself waited until retirement; check failure, blocking data forwarding and reporting a fault are distinct events.',
 '先区分两个例子：排在故障指令下面的独立操作，可以在不依赖故障结果的情况下提前执行；经典 Meltdown 的泄漏链则要求更强的条件，即后续依赖操作收到被拒绝读取的那个字节。最终报告异常，不表示权限检查一定拖到退休才发生。“检查失败”“阻断转发”“向软件报告故障”是不同事件。'),
 training=('No branch training is required for the core mechanism. The teaching setup is a mapped page that user mode may not read, on a vulnerable implementation. A valid but forbidden mapping and an absent mapping are different cases.',
 '核心机制不需要训练分支。教学前提是在受影响实现上，页面已映射，但用户态没有读取权限。“有效但禁止访问”和“根本未映射”是不同条件。'),
 boundary=('The classic case concerns user/kernel isolation. The exact reachable data depends on mappings, hardware behavior and system configuration. A failed PoC on patched hardware says nothing by itself about an unrelated Spectre or sampling mechanism.',
 '经典场景涉及用户 / 内核隔离。能触及哪些数据还取决于映射、硬件行为与系统配置。在更新后的硬件上 PoC 失败，不能据此判断其他 Spectre 或采样机制的状态。'),
 mitigation=('PTI/KPTI removes most kernel mappings from the user page-table view and switches page tables at kernel entry/exit. This removes a prerequisite; it is not a branch-predictor flush and is not a general fix for all transient execution.',
 'PTI/KPTI 从用户态页表视图移除大多数内核映射，并在内核出入口切换页表。它切断的是机制所需条件，不是清理分支预测器，也不是所有瞬态执行问题的通用修复。'),
 contrast=('The later timing measurement is ordinary observation code, not execution resuming at the original next instruction after the fault handler. The transient byte is never a permitted architectural read.',
 '后续计时是正式执行的另一段观察代码，不是异常处理完又回到原程序下一行顺序执行。瞬态使用的字节并未成为合法的架构读取结果。'),
 trace=('''[01] V maps a supervisor-only byte; RCX = V
[02] request: byte = LOAD(V)
[03] transient possibility: dependent_use(byte)
[04] architectural: permission fault; byte is not committed
[05] separate observation: inspect a data-dependent trace
[06] control: an unmapped V does not provide this same setup''','''[01] V 映射仅主管可读的字节；RCX = V
[02] 请求：byte = LOAD(V)
[03] 可能的瞬态过程：依赖操作使用 byte
[04] 正式：权限故障，byte 不提交
[05] 独立的后续观察：检查与数据有关的痕迹
[06] 对照：未映射 V 不提供相同的前提'''),
 read=('Compare Meltdown Figure 3 / Listing 1 with Listing 2 in §5.1. The first illustrates work before exception delivery; the second asks whether a denied load can feed a dependent disclosure chain.',
 '对比 Meltdown 图 3 / Listing 1 与 §5.1 的 Listing 2。前者说明报告异常前可能发生的工作，后者关注被拒绝的读取能否为后续依赖泄漏链提供数据。')),
 dict(id='l1tf',name='Foreshadow / L1 Terminal Fault',year=2018,cve='CVE-2018-3615 / CVE-2018-3620 / CVE-2018-3646',family='fault',refs=['foreshadow','l1tf'],
 thesis=('Translation fails, yet data associated with the invalid entry may be transiently supplied from L1D.','地址翻译失败，但与无效页表项相关的数据可能仍从 L1D 被瞬态提供。'),
 trigger=('Terminal address-translation fault','终止性地址翻译故障'),source=('Relevant data already in L1D','相关数据已驻留 L1D'),formal=('Page fault; no valid translation','页故障，没有有效翻译'),transient=('L1D value forwarded despite failure','失败后仍可能转发 L1D 值'),
 mechanism=('An invalid page-table entry can still contain physical-address bits. On affected implementations a terminal fault may not stop those bits from participating in transient access to an already resident L1 data-cache line. The teaching value 0x2A is that line’s existing data, not a virtual address or an attack parameter. A missing L1D line does not turn this into an unrestricted DRAM read.',
 '无效页表项仍可能含有物理地址位。在受影响实现中，终止性故障未能阻止这些位参与对已驻留 L1 数据缓存行的瞬态访问。教学值 0x2A 是该行原有数据，不是虚拟地址或攻击参数。若相关数据不在 L1D，也不能据此把机制延伸成任意 DRAM 读取。'),
 training=('No branch training. Track both constraints: an applicable invalid translation and relevant L1D residency. Unlike the classic Meltdown example, the translation itself is invalid rather than a valid supervisor-only mapping.',
 '不训练分支。要同时跟踪可利用的无效翻译与对应 L1D 驻留。它与经典 Meltdown 示例不同，后者通常是有效但仅主管可访问的映射。'),
 boundary=('Foreshadow studied SGX; related L1TF variants cover OS/SMM and virtualization boundaries. Their CVEs and attacker control differ. An untrusted host manipulating an enclave’s environment is a different threat model from a normal unprivileged process.',
 'Foreshadow 原研究面向 SGX；相关 L1TF 变体涉及 OS/SMM 及虚拟化边界，CVE 与攻击者控制能力不同。不可信宿主操纵 enclave 环境，与普通非特权进程的威胁模型不同。'),
 mitigation=('PTE inversion prevents invalid entries from naming cacheable physical memory. Relevant VM-entry L1D flushing and SMT scheduling/isolation address other parts of the chain. Flushing one boundary does not automatically stop simultaneous activity on a sibling thread.',
 'PTE inversion 使无效项不再指向可缓存物理内存。相关 VM 入口 L1D 刷新、SMT 调度 / 隔离则处理攻击链的其他环节。在一个边界刷新缓存，不自动覆盖兄弟线程的并行活动。'),
 contrast=('L1TF selects through invalid translation and L1D residency. MDS samples internal buffers and generally cannot choose a secret address in this way.',
 'L1TF 的核心约束是无效翻译与 L1D 驻留。MDS 面向内部缓冲区采样，通常不能以同样方式指定秘密地址。'),
 trace=('''[01] request: LOAD(V)
[02] translate(V) = INVALID
[03] setup: relevant L1D line contains 0x2A
[04] transient possibility: t = 0x2A; dependent_use(t)
[05] architectural: report page fault
[06] control: no relevant L1D residency → this source absent''','''[01] 请求：LOAD(V)
[02] translate(V) = INVALID
[03] 教学设定：相关 L1D 行含有 0x2A
[04] 可能的瞬态过程：t = 0x2A，依赖操作使用 t
[05] 正式：报告页故障
[06] 对照：相关数据不驻留 L1D，则缺少这条来源'''),
 read=('Use Foreshadow’s L1-residency discussion and Linux’s invalid-PTE explanation together. Mark the translation failure, the restricted data source, and the boundary-specific mitigation separately.',
 '将 Foreshadow 的 L1 驻留讨论与 Linux 的无效 PTE 说明一起读，分别标记翻译失败、受限的数据来源及对应边界的缓解。')),
 dict(id='mds',name='MDS · RIDL / ZombieLoad / Fallout',year=2019,cve='CVE-2018-12126 / CVE-2018-12127 / CVE-2018-12130 / CVE-2019-11091',family='sampling',refs=['ridl','mds'],
 thesis=('A transient sample may come from a CPU buffer, not from the address the load requested.','瞬态样本可能来自 CPU 内部缓冲区，而非读取指令请求的地址。'),
 trigger=('Faulting or assisting load','读取遇到故障或内部辅助处理'),source=('Fill / store buffers or load ports','填充 / 存储缓冲区或加载端口'),formal=('Correct retry result or a fault','重试得到正确值，或报告故障'),transient=('Unrelated buffer sample consumed','短暂消费无关缓冲区样本'),
 mechanism=('Let region A normally contain 0x17, while 0x6D from other work passes through an affected buffer. A faulting/assisting load of A may transiently receive 0x6D. A later successful retry still returns 0x17, or a real fault is delivered; the sample is not the architectural result. Keeping A fixed does not keep the sample fixed. RIDL, Fallout and ZombieLoad name related research, not three mutually exclusive structures.',
 '设区域 A 的正常数据为 0x17，其他工作中的 0x6D 曾经过受影响缓冲区。对 A 的故障 / 辅助读取可能短暂收到 0x6D；若之后重试成功，仍应得到 0x17，否则正式报告故障，不提交样本。A 不变不保证样本不变。RIDL、Fallout、ZombieLoad 是相关研究名称，并非三个互斥硬件结构。'),
 training=('No branch training is intrinsic. Identify the buffer subtype, the operation opening the sample window and whether data can be attributed to the victim. An internal assist need not be a software-visible exception.',
 '核心不依赖分支训练。应识别缓冲区子类型、打开采样窗口的操作，以及样本能否归因于受害者。内部 assist 不一定成为软件可见异常。'),
 boundary=('Relevant conditions include affected Intel hardware, scheduling on a shared core and sometimes SMT sharing. Sampling and postprocessing are different from directly addressing a secret. Report raw sample rate separately from useful secret-recovery rate.',
 '条件包括受影响 Intel 硬件、共享核心上的调度，以及某些结构的 SMT 共享。采样和后处理不同于按地址直接读取秘密。原始样本率应与有效秘密恢复率分开报告。'),
 mitigation=('Supported microcode and kernel buffer-clearing paths work together; evaluate SMT isolation where simultaneous untrusted execution crosses the security boundary. L1D flushing and clearing these buffers are not interchangeable operations.',
 '支持的微码与内核缓冲区清理路径需要配合；若边界上存在并行的不可信执行，还需评估 SMT 隔离。刷新 L1D 与清理这些缓冲区不能互相替代。'),
 contrast=('MDS describes the observer sampling a value. LVI describes a victim consuming a wrong operand. SSB can expose an old value from the same logical location, rather than MDS’s unrelated sample.',
 'MDS 是观察者采到值，LVI 是受害者消费错误操作数。SSB 则可能使用同一逻辑位置的旧值，不是 MDS 这里的无关样本。'),
 trace=('''[01] normal LOAD(A) result = 0x17
[02] other work passes 0x6D through an affected buffer
[03] LOAD(A) encounters a fault or assist
[04] transient possibility: t = 0x6D
[05] architectural: correct retry returns 0x17, or report fault
[06] repeat with A unchanged: sample may change''','''[01] 正常 LOAD(A) 的结果为 0x17
[02] 其他工作使 0x6D 经过受影响缓冲区
[03] LOAD(A) 遇到故障或 assist
[04] 可能的瞬态过程：t = 0x6D
[05] 正式：重试得到 0x17，或报告故障
[06] A 保持不变再次观察，样本仍可能改变'''),
 read=('In RIDL and the MDS taxonomy, mark the requested address, buffer contents and observed value with different symbols. Ask which subtype supports the claimed sharing boundary before interpreting the result.',
 '阅读 RIDL 与 MDS 分类时，为请求地址、缓冲区内容和观察值分别使用不同符号。先核对具体子类型是否支持所声称的共享边界，再解释结果。')),
 dict(id='lvi',name='LVI · Load Value Injection',year=2020,cve='CVE-2020-0551',family='fault',refs=['lvi-paper','lvi'],
 thesis=('The victim’s own dependent instructions may briefly use a value that its load should not have supplied.','受害者自己的依赖指令，可能短暂使用一次读取本不该提供的值。'),
 trigger=('Victim load faults / assists / aborts','受害者读取故障、辅助或中止'),source=('Wrong operand in victim dataflow','受害者数据流中的错误操作数'),formal=('No result based on wrong operand','不提交基于错误操作数的结果'),transient=('Victim computes with wrong v','受害者短暂用错误 v 计算'),
 mechanism=('For teaching, use v = *config and result = v + 10. A normal v of 1 gives 11. Under an affected forwarding condition, a transient v of 0 could make the dependent operation compute 10, without committing that result. The 0 is an illustrative wrong operand, not the stolen secret, and +10 is not a disclosure gadget. A real attack needs additional victim behavior that exposes sensitive information.',
 '教学例子使用 v = *config 与 result = v + 10。正常 v = 1 时结果为 11；在受影响的转发条件下，瞬态 v = 0 可能使依赖运算一度算出 10，但不提交这个错误结果。0 是错误操作数的例值，不是被窃取的秘密，+10 也不是泄漏 gadget。真实攻击还需要能暴露敏感信息的后续受害者行为。'),
 training=('The core does not require branch training. Distinguish attacker-influenced stale-value forwarding, zero-only forwarding, and no-forwarding behavior. The availability and controllability of a wrong operand depend on the hardware and load condition.',
 '核心不要求分支训练。应区分受攻击者影响的陈旧值转发、只转发零以及不转发任何值的行为。错误操作数能否出现、可控到何种程度，取决于硬件与读取条件。'),
 boundary=('Original LVI work emphasizes SGX under an untrusted OS/VMM. Causing the required victim load condition and controlling the subsequent dataflow are substantial prerequisites. This is not a claim that arbitrary applications can inject persistent data into each other.',
 '原始 LVI 研究重点是 OS/VMM 不可信的 SGX 场景。使指定受害者读取出现所需条件、并影响后续数据流，都是重要前提，不能概括成普通应用彼此任意写入持久数据。'),
 mitigation=('Use the applicable SGX toolchain and platform guidance for load/dependency hardening. A generic instruction to clear MDS buffers is not a sufficient description of every LVI mitigation, especially when forwarding behaviors differ.',
 '按平台使用适用的 SGX 工具链与加载 / 依赖硬化指南。笼统地说“清理 MDS 缓冲区”不足以描述所有 LVI 缓解，尤其在转发行为不同时。'),
 contrast=('Reverse the MDS viewpoint: the important event is a victim consuming the wrong value, not merely the observer reading a leftover sample.',
 '把 MDS 的观察方向反过来看：关键是受害者消费了错误值，而不只是观察者读到一个残留样本。'),
 trace=('''[01] victim: v = LOAD(config)
[02] victim: result = v + 10
[03] control: v = 1 → result = 11
[04] affected load condition may forward wrong v = 0
[05] transient: [02] computes 10
[06] architectural: do not commit result from the wrong v''','''[01] 受害者：v = LOAD(config)
[02] 受害者：result = v + 10
[03] 对照：v = 1，result = 11
[04] 受影响读取条件可能转发错误 v = 0
[05] 瞬态：[02] 一度算出 10
[06] 正式：不提交基于错误 v 的结果'''),
 read=('Read the LVI paper’s victim dataflow next to Intel’s forwarding categories. Label the injected operand and the eventual secret as different objects; do not infer a full exploit from this arithmetic model.',
 '将 LVI 论文的受害者数据流与 Intel 的转发分类对照。为注入操作数和最终秘密分别标记，不要从这个算术模型推断已有完整利用链。')),
 dict(id='ssb',name='SSB · Spectre V4',year=2018,cve='CVE-2018-3639',family='prediction',refs=['ssb','ssb-ms'],
 thesis=('A later load may temporarily read OLD before an earlier overlapping store’s address is resolved.','较早的重叠写入地址尚未确定时，较晚读取可能暂时读到 OLD。'),
 trigger=('Unresolved earlier store address','较早 store 的地址未就绪'),source=('Old value of the same location','同一逻辑位置的旧值'),formal=('Respect store → load dependency','正式遵守前写后读依赖'),transient=('Load bypasses store and sees OLD','读取暂时绕过写入，看到 OLD'),
 mechanism=('Set slot_A to 3, then execute *p = 8 followed by v = *q, with p and q ultimately naming slot_A. While p’s address is unresolved, a memory-dependence predictor can guess that the two accesses do not overlap. The load may then consume 3. Once the overlap is discovered, recovery must obtain 8. If p truly names another location, reading 3 from slot_A is correct, so address equality is essential to the example.',
 '令 slot_A 初值为 3，先执行 *p = 8，再执行 v = *q，且 p、q 最终均指向 slot_A。p 的地址未就绪时，内存依赖预测可能先猜两者不重叠，读取于是短暂使用 3。发现重叠后必须纠正为 8。如果 p 最终确实指向别处，从 slot_A 读取 3 本来就是正确的，因此地址重叠是例子的关键。'),
 training=('This is memory-dependence prediction, not V1’s conditional direction or V2’s target prediction. Branch training is not a defining prerequisite. Implementation-specific history may matter, but the causal question is whether the later load wrongly bypassed a conflicting earlier store.',
 '这是内存依赖预测，不是 V1 的条件方向或 V2 的目标预测。分支训练不是定义前提。实现特定的历史可能有影响，但因果问题是后读是否错误地越过了冲突的前写。'),
 boundary=('A disclosure requires victim code that makes the stale value security-sensitive, such as an old pointer before an intended overwrite. A timing difference in two ordinary loads does not by itself demonstrate sandbox escape or key disclosure.',
 '形成泄漏还需要受害者代码使旧值具备安全意义，例如本应被覆盖的旧指针。两次普通读取存在耗时差，不足以证明沙箱逃逸或密钥泄漏。'),
 mitigation=('Use applicable Speculative Store Bypass Disable (SSBD) controls and platform/compiler guidance at the relevant boundary. Costs and enablement depend on CPU and workload. Disabling unrelated branch prediction is not an explanation of this dependency fix.',
 '按边界使用适用的 SSBD 控制与平台 / 编译器指南。启用方式和代价取决于 CPU 与负载。关闭无关分支预测并不能解释这里的依赖修复。'),
 contrast=('The stale 3 belongs to slot_A. MDS’s illustrative 0x6D came from unrelated buffer activity; the two meanings of “old data” must not be merged.',
 '旧值 3 属于 slot_A；MDS 中示例的 0x6D 来自无关缓冲区活动，不能因为都叫“旧数据”就混为一类。'),
 trace=('''[01] slot_A = 3
[02] STORE(p, 8)           # earlier, address not ready
[03] v = LOAD(q)           # q names slot_A
[04] predict no overlap → transient v = 3
[05] resolve: p and q both name slot_A
[06] architectural: recover/re-execute; v = 8''','''[01] slot_A = 3
[02] STORE(p, 8)          # 较早写入，地址尚未就绪
[03] v = LOAD(q)          # q 指向 slot_A
[04] 预测不重叠，瞬态 v = 3
[05] 地址确定：p、q 均指向 slot_A
[06] 正式：纠正 / 重执行，v = 8'''),
 read=('In the vendor example, find the earlier overwrite, the later dereference and the dependency that the predictor misses. Keep instruction order separate from the order in which addresses become available.',
 '读厂商示例时，找出较早覆盖、较晚解引用及被预测器忽略的依赖。程序顺序与地址就绪顺序需要分开。')),
 dict(id='taa',name='TAA · TSX Asynchronous Abort',year=2019,cve='CVE-2019-11135',family='sampling',refs=['exp-tsx','zombieload'],
 thesis=('Transaction rollback can preserve architectural correctness while a pending abort opens a buffer-sampling window.','事务回滚维持了架构正确性，待处理的异步中止却可能打开缓冲区采样窗口。'),
 trigger=('TSX asynchronous abort pending','TSX 异步中止待处理'),source=('Internal buffer sample','内部缓冲区样本'),formal=('Abort transaction; roll back its writes','中止事务，回滚暂定写入'),transient=('Load consumes an unrelated sample','读取短暂消费无关样本'),
 mechanism=('Start with an architectural counter of 5. A transaction tentatively writes 6, then an asynchronous abort becomes pending. In the affected window a load may consume an unrelated buffer sample, illustrated as 0x42. After rollback the counter is still 5. The tentative write 6, sample 0x42 and committed 5 have three different roles. Atomic rollback of the first does not establish that every microarchitectural trace of the second disappeared.',
 '设正式 counter = 5，事务暂定写为 6，随后异步中止待处理。在受影响窗口里，一次读取可能消费无关缓冲区样本，例值为 0x42。回滚后 counter 仍为 5。暂定写入 6、样本 0x42、正式值 5 扮演三个不同角色；前者的原子回滚，不证明后者所有微架构痕迹都已消失。'),
 training=('No branch training is central. The sampling side uses a relevant enabled TSX path on affected hardware. The victim need not execute TSX. Neither the transaction address nor the counter selects the secret sample.',
 '核心不依赖分支训练。采样一方在受影响硬件上使用相关且已启用的 TSX 路径，被观察者不必使用 TSX。事务地址与 counter 都不是选取秘密样本的地址。'),
 boundary=('Host or guest applications may be relevant depending on affected hardware and core sharing. Like MDS, useful recovery requires samples plus attribution/postprocessing; it is not a chosen-address memory read.',
 '宿主或客户机应用是否构成场景，取决于硬件与核心共享条件。与 MDS 类似，有效恢复需要样本及归因 / 后处理，不是选择地址后直接读内存。'),
 mitigation=('Follow platform guidance for disabling affected TSX use or applying applicable microcode and buffer clearing, with SMT isolation where needed. MDS_NO alone is not an adequate TAA conclusion; verify the TAA-specific status and relevant controls.',
 '按平台指南关闭受影响 TSX 路径，或使用适用微码及缓冲区清理，必要时配合 SMT 隔离。仅凭 MDS_NO 不能判断 TAA，需核对 TAA 专属状态与控制。'),
 contrast=('MDS and TAA can involve similar data sources, but the pending transaction-abort window distinguishes TAA. A victim’s lack of transactions does not eliminate this sampling path.',
 'MDS 与 TAA 的数据来源可能相似，但待完成的事务中止窗口区分了 TAA。受害者不运行事务，并不等于消除了该采样路径。'),
 trace=('''[01] committed counter = 5
[02] transaction tentatively writes counter = 6
[03] event: asynchronous abort pending
[04] transient load may consume sample 0x42
[05] architectural: abort; counter remains 5
[06] sample 0x42 is not a committed transaction result''','''[01] 正式 counter = 5
[02] 事务暂定写入 counter = 6
[03] 输入事件：异步中止待处理
[04] 瞬态读取可能消费样本 0x42
[05] 正式：事务中止，counter 仍为 5
[06] 0x42 不是提交的事务结果'''),
 read=('Compare the original ZombieLoad Variant 2 discussion with Linux’s TAA trigger and mitigation status. Distinguish the observer’s TSX requirement from the victim’s ordinary activity.',
 '将 ZombieLoad Variant 2 的讨论与 Linux 的 TAA 触发 / 状态说明对照，区分观察者的 TSX 前提与受害者的普通活动。')),
 dict(id='bhi',name='BHI · Branch History Injection',year=2022,cve='CVE-2022-0001',family='prediction',refs=['bhi-paper','bhi'],
 thesis=('Changing branch-history context can change which learned target is predicted, without changing the real target.','分支历史上下文变化，可能改变选中的已学习预测目标，而真实目标不变。'),
 trigger=('History-sensitive indirect prediction','间接目标预测受历史影响'),source=('History selects a target candidate','历史参与选择目标候选'),formal=('Resolve and execute NORMAL','解析并执行 NORMAL'),transient=('A history-selected wrong gadget','历史选中的错误 gadget'),
 mechanism=('Hold the indirect branch J, real target NORMAL and learned candidates A/B constant. In a conceptual predictor, context H_A selects A while H_B selects B. If B is wrong, its instructions may briefly execute before resolution. H_A and H_B are labels, not recipes for real history construction. This contrast illustrates why restricting target state and isolating history are not necessarily the same intervention.',
 '保持间接分支 J、真实目标 NORMAL 和已学习候选 A/B 不变。在概念预测器中，上下文 H_A 选 A，H_B 选 B。如果 B 不是正确目标，它的指令可能在解析前短暂执行。H_A、H_B 只是标签，不是真实历史构造配方。这个对照说明限制目标状态与隔离历史不一定是同一种干预。'),
 training=('The emphasis is on history/context influencing target choice, not an out-of-bounds array index. It need not be described as directly inserting a fresh victim target. This is a distinction in causal focus, not a universal two-table microarchitecture.',
 '重点是历史 / 上下文影响目标选择，不是越界数组索引，也不必描述成直接插入一个新的受害者目标。这是因果关注点的区别，不是声称所有 CPU 都有相同的两张硬件表。'),
 boundary=('A leakage gadget and an observation channel remain necessary. Cross-domain and intra-mode cases have different constraints. Read the exact kernel paths and CPU behavior; a broad statement that eIBRS is enabled does not settle every history-related attack.',
 '仍需泄漏 gadget 和观察通道。跨域与同模式场景约束不同，需阅读具体内核路径与 CPU 行为；笼统地说已启用 eIBRS，不能解决所有历史相关问题。'),
 mitigation=('Apply the current platform-specific combination of history controls, kernel history-clearing/hardening and relevant predictor protections. Intel guidance distinguishes BHI_DIS_S and, on supporting systems, IBHF for additional history-related hardening. Verify applicability rather than relying on a single feature label.',
 '使用当前平台适用的历史控制、内核历史清理 / 加固及预测器防护组合。Intel 指南区分 BHI_DIS_S，以及在支持平台上用于额外历史加固的 IBHF。应核对适用性，不依赖一个功能标签。'),
 contrast=('Classic BTI focuses on influenced target prediction; BHI highlights the history used to choose a target. Both belong to the Spectre-V2 family and still require a useful disclosure path.',
 '经典 BTI 关注受影响的目标预测，BHI 强调选目标时使用的历史。两者同属 Spectre-V2 家族，都仍需可用泄漏路径。'),
 trace=('''[01] indirect branch J; real target = NORMAL
[02] learned candidates A and B stay fixed
[03] context H_A → prediction A
[04] context H_B → prediction B
[05] transient: if B != NORMAL, B may execute
[06] architectural: execute NORMAL, not B''','''[01] 间接分支 J，真实目标 = NORMAL
[02] 已学习候选 A、B 保持不变
[03] 上下文 H_A → 预测 A
[04] 上下文 H_B → 预测 B
[05] 瞬态：若 B 不是 NORMAL，可能先执行 B
[06] 正式：执行 NORMAL，不提交 B 路径'''),
 read=('In the BHI paper, label branch PC, history and target candidates separately. In updated vendor guidance, distinguish the original attack class from later gadgets and hardening additions.',
 '读 BHI 论文时，分别标出分支位置、历史和候选目标。读更新后的厂商指南时，区分最初机制、后续 gadget 与新增加固。')),
 dict(id='retbleed',name='Retbleed · Return Target Prediction',year=2022,cve='CVE-2022-29900 / CVE-2022-29901',family='prediction',refs=['retbleed','rsb'],
 thesis=('A RET can transiently go to a wrong target even though the saved architectural return address was never changed.','即使保存的正式返回地址未被改写，RET 仍可能短暂走向错误预测目标。'),
 trigger=('RET under affected prediction conditions','RET 处于受影响预测条件'),source=('Return-target predictor state','返回目标预测状态'),formal=('Return to saved R_OK','正式返回保存的 R_OK'),transient=('Briefly execute R_OTHER','短暂执行 R_OTHER'),
 mechanism=('CALL worker records a return address R_OK. At RET the machine may start fetching a predicted target before the real return resolves. Retbleed shows affected return-prediction paths on particular Intel and AMD implementations. In the model, R_OTHER is a symbolic wrong target; it does not replace the saved address. Once the return resolves the wrong path is discarded, but an executed disclosure gadget may have left a trace.',
 'CALL worker 保存返回地址 R_OK。在 RET 的真实结果确定前，CPU 可能先从预测目标取指。Retbleed 展示特定 Intel 与 AMD 实现上的受影响返回预测路径。模型中的 R_OTHER 是错误目标标签，不会替换保存的返回地址。返回解析后，错误路径被取消，但已经执行的泄漏 gadget 仍可能留下痕迹。'),
 training=('The relevant state is return/target prediction. On evaluated Intel designs RSB underflow is important; the documented AMD behavior is not captured by that same rule. Do not turn one implementation’s trigger into a universal statement about every RET.',
 '相关状态是返回 / 目标预测。研究涉及的 Intel 设计中 RSB 下溢很重要，但同一规则不能概括文献描述的 AMD 行为。不能把某一实现的触发条件当作所有 RET 的通用规则。'),
 boundary=('The attack needs a reachable return and suitable victim code under the evaluated predictor-sharing conditions. Kernel-disclosure demonstrations do not establish identical behavior on newer or differently configured CPUs.',
 '需要可触达的返回点、合适的受害者代码及研究中的预测器共享条件。内核泄漏演示不能外推为更新或不同配置 CPU 上的相同行为。'),
 mitigation=('Use the model-specific microcode and kernel return-path defenses, including applicable return thunks, RSB handling or hardware controls. Retpoline’s use of returns does not prove protection where returns themselves take an affected target-prediction path.',
 '按型号使用微码和内核返回路径缓解，包括适用的返回跳板、RSB 处理或硬件控制。retpoline 使用返回指令，不等于在返回本身进入受影响预测路径时仍能单独保护。'),
 contrast=('A prediction problem is not a stack overwrite or ROP modification of the architectural return address. BHI focuses on history selection; Retbleed focuses on the return instruction’s prediction path.',
 '预测问题不是栈覆盖，也不是用 ROP 改写正式返回地址。BHI 关注历史选择，Retbleed 关注返回指令进入哪种预测路径。'),
 trace=('''[01] CALL worker; saved return = R_OK
[02] worker executes; saved return remains R_OK
[03] RET
[04] affected prediction: target = R_OTHER
[05] transient: instructions at R_OTHER may execute
[06] architectural: return to R_OK''','''[01] CALL worker，保存返回地址 R_OK
[02] worker 执行，保存地址仍为 R_OK
[03] RET
[04] 受影响预测：目标为 R_OTHER
[05] 瞬态：R_OTHER 的指令可能先执行
[06] 正式：返回 R_OK'''),
 read=('Read the research team’s Intel and AMD conditions separately. Follow the return instruction, prediction source and eventual saved address through the argument; then examine the matching kernel defense.',
 '分别阅读研究团队给出的 Intel、AMD 条件，沿返回指令、预测来源及最终保存地址跟踪论证，再检查匹配的内核缓解。')),
 dict(id='gds',name='Downfall · Gather Data Sampling',year=2023,cve='CVE-2022-40982',family='sampling',refs=['downfall','gds'],
 thesis=('An affected transient gather may forward stale vector data; the victim need only have used vector registers.','受影响的瞬态 gather 可能转发旧向量数据，被观察者只需使用过向量寄存器。'),
 trigger=('Transient gather encounters a fault','瞬态 gather 遇到故障'),source=('Stale vector-related state','陈旧向量相关状态'),formal=('Apply gather completion/fault rules','按 gather 完成 / 故障规则处理'),transient=('A lane may receive stale value 99','某 lane 可能暂时收到旧值 99'),
 mechanism=('A conceptual gather should assemble [11,22,33,44] from several memory locations. Under an affected transient fault condition a dependent operation may instead see a stale lane value illustrated as 99. This 99 is not the corresponding memory element. Some gather forms can preserve legitimately completed elements on a fault; that architectural partial-completion behavior must not be confused with committing a wrongly forwarded old value.',
 '概念 gather 应从多个内存位置收集 [11,22,33,44]。在受影响的瞬态故障条件下，依赖操作可能看到以 99 表示的旧 lane 数据。99 不是对应内存元素。某些 gather 形式在故障时可以保留合法完成的元素，这种架构上的部分完成，不能与提交错误转发的旧值混淆。'),
 training=('No branch training is intrinsic. The observer’s gather is relevant to the sampling path, while the victim need not execute gather. The input address list does not select which old register content will be inferred.',
 '核心不依赖分支训练。gather 是观察者一侧的相关指令，被观察者不必执行 gather。输入地址列表不是选择要采出哪份旧寄存器内容的索引。'),
 boundary=('Affected Intel models and microcode determine applicability. Vector-state sampling can cross relevant user/kernel, VM and SGX boundaries under documented conditions, including applicable same-core sharing. Identify the concrete context and schedule rather than generalizing from an instruction name.',
 '适用性取决于受影响 Intel 型号与微码。在文献条件下，向量状态采样可涉及用户 / 内核、虚拟机与 SGX 边界，包括适用的同核共享。应明确上下文与调度，不能仅凭指令名外推。'),
 mitigation=('Use applicable GDS microcode mitigation and keep lower-privilege contexts from disabling the protection. Linux also documents an AVX-disabling fallback when required microcode is unavailable, with functionality and performance costs.',
 '使用适用的 GDS 微码缓解，并防止低权限上下文关闭保护。没有所需微码时，Linux 还记录了禁用 AVX 的回退方法，存在功能与性能代价。'),
 contrast=('GDS concerns a gather-related sampling path. RFDS concerns other stale register-file states. Neither means the victim must run the observer’s trigger instruction.',
 'GDS 关注 gather 相关采样路径，RFDS 关注其他陈旧寄存器文件状态。两者都不能被理解为受害者必须执行观察者的触发指令。'),
 trace=('''[01] intended gather result = [11,22,33,44]
[02] a lane does not complete normally
[03] transient dependent use may see stale 99
[04] 99 came from prior vector-related state
[05] architectural: follow instruction fault/completion rules
[06] do not treat 99 as a legitimate completed element''','''[01] 正常 gather 结果应为 [11,22,33,44]
[02] 某个 lane 未正常完成
[03] 瞬态依赖操作可能看到旧值 99
[04] 99 来自先前向量相关状态
[05] 正式：按指令故障 / 完成规则处理
[06] 不把 99 当成合法完成的元素'''),
 read=('Read Downfall §3 alongside the instruction’s gather semantics. Separate memory elements, old vector data, legal partial results and transient forwarding before interpreting the demonstrated boundary.',
 '将 Downfall §3 与 gather 指令语义对照，在解释边界前区分内存元素、旧向量数据、合法部分结果与瞬态转发。')),
 dict(id='rfds',name='RFDS · Register File Data Sampling',year=2024,cve='CVE-2023-28746',family='sampling',refs=['rfds'],
 thesis=('Previously used register-file values may be sampled; this is not reading another task’s current named register.','先前使用过的寄存器文件值可能被采样，但不是按寄存器名正常读取另一任务的当前寄存器。'),
 trigger=('Affected register-file sampling condition','受影响的寄存器文件采样条件'),source=('Old register-file entries','旧寄存器文件项'),formal=('Use current architectural register state','使用当前架构寄存器状态'),transient=('Sample may reflect OLD','样本可能反映 OLD'),
 mechanism=('A prior context used value OLD. The current context’s legitimate operation uses CURRENT. An old physical register-file entry can retain OLD until overwritten. In an affected condition a sample may reflect OLD, even though normal register operations must still follow the current context’s architectural state. OLD is a data label, not a register number to request. The model intentionally does not invent a universal RFDS trigger instruction.',
 '先前上下文使用过 OLD，当前上下文的合法操作使用 CURRENT。旧物理寄存器文件项在被覆盖前可能保留 OLD。在受影响条件下，样本可能反映 OLD，但普通寄存器操作仍须遵守当前上下文的架构状态。OLD 是数据标签，不是可以请求读取的寄存器编号。此模型有意不虚构通用 RFDS 触发指令。'),
 training=('No branch training is central. The stale source can involve integer, floating-point or vector values depending on the affected core. Sampling does not let the observer choose the exact disclosed value.',
 '核心不依赖分支训练。随受影响核心不同，陈旧来源可能涉及整数、浮点或向量值。采样并不赋予观察者精确选择所泄漏值的能力。'),
 boundary=('RFDS applies to particular Intel Atom/E-core implementations, not every E-core. Documented affected cores lack SMT; the boundary concerns prior use of the same affected logical processor, including process or guest transitions. Do not import a cross-SMT model from GDS or MDS.',
 'RFDS 适用于特定 Intel Atom/E 核实现，不是全部 E 核。文档中的受影响核心不支持 SMT，需关注同一受影响逻辑处理器上的先前使用及进程 / 客户机切换，不能照搬 GDS 或 MDS 的跨 SMT 模型。'),
 mitigation=('Applicable microcode enables RFDS clearing through VERW. Kernel/KVM paths clear at relevant user-return and VM-entry boundaries. Check the RFDS-specific enumeration and status; sharing a mitigation instruction with MDS does not make the vulnerabilities identical.',
 '适用微码使 VERW 能执行 RFDS 清理，内核 / KVM 在返回用户态、进入虚拟机等相关边界调用。需核对 RFDS 专属枚举与状态，和 MDS 共用一条缓解指令并不表示漏洞相同。'),
 contrast=('RFDS is not another name for GDS, and “stale register value” does not imply an architectural permission to read another task’s register file.',
 'RFDS 不是 GDS 的另一名称，“陈旧寄存器值”也不表示存在正常读取其他任务寄存器文件的架构权限。'),
 trace=('''[01] prior context used OLD
[02] current context legitimately uses CURRENT
[03] an old register-file entry may still retain OLD
[04] affected sampling may reflect OLD
[05] normal architectural operations still use CURRENT
[06] clearing targets affected stale entries''','''[01] 先前上下文使用过 OLD
[02] 当前上下文合法使用 CURRENT
[03] 旧寄存器文件项可能仍保留 OLD
[04] 受影响采样可能反映 OLD
[05] 正常架构操作仍使用 CURRENT
[06] 缓解清理的是受影响的陈旧项'''),
 read=('Use the RFDS disclosure’s distinction between current architectural values and old entries. Verify the exact core type and RFDS_CLEAR/RFDS_NO support rather than identifying a CPU only by its marketing family.',
 '读 RFDS 披露时关注当前架构值与旧项的区别。核对准确核心类型及 RFDS_CLEAR/RFDS_NO 支持，不只按市场系列名称识别 CPU。')),
 dict(id='inception',name='Inception / SRSO',year=2023,cve='CVE-2023-20569',family='prediction',refs=['inception','srso'],
 thesis=('Speculation can train later return predictions, so recovering from one wrong path does not remove the predictor state it created.','一次推测可以训练后续返回预测，因此从错误路径恢复，不等于清除了它造成的预测状态。'),
 trigger=('Phantom speculation and return prediction','Phantom 推测与返回预测'),source=('Predictor state trained transiently','在瞬态路径中训练的预测状态'),formal=('Real return address remains R_OK','真实返回地址仍为 R_OK'),transient=('Later RET may go to a wrong gadget','后续 RET 可能先走错误 gadget'),
 mechanism=('The Inception study combines phantom speculation with training in transient execution. A location need not architecturally be a CALL to contribute CALL-like speculative effects on an affected implementation. The resulting return-prediction state can influence a later RET. The teaching sequence below treats these effects as events; it is not an instruction sequence that constructs a real overflowing predictor. The eventual return target remains architecturally correct.',
 'Inception 将 Phantom speculation 与瞬态执行中的训练结合。在受影响实现上，某个位置不必在架构上真是 CALL，也可能产生类似 CALL 的推测效应，由此留下的返回预测状态又影响之后的 RET。下面把这些效应作为输入事件，不给出构造真实预测器溢出的指令序列，最终正式返回目标仍须正确。'),
 training=('The distinctive point is that transient activity can train future predictions. This differs from merely executing legal indices before a V1 check. The exact BTB/return-predictor interaction depends on AMD microarchitecture.',
 '特点是瞬态活动可以训练未来的预测，并非只是在 V1 检查前重复合法索引。BTB 与返回预测器的具体交互依赖 AMD 微架构。'),
 boundary=('The original research evaluates AMD Zen scenarios, including user/kernel disclosure. Separate the paper’s threat model from the exact vendor support matrix and kernel state. A stale prediction by itself is not a recovered secret; a usable gadget and observation channel are still needed.',
 '原研究评估 AMD Zen 场景，包括用户 / 内核泄漏。应将论文威胁模型与准确的厂商支持矩阵、内核状态分开。一个残留预测本身不是已恢复的秘密，仍需可用 gadget 与观察通道。'),
 mitigation=('Use the relevant microcode and kernel SRSO return-path protection. Linux distinguishes extended IBPB from Safe RET and boundary-specific combinations. One control’s presence does not establish protection of user/kernel, guest/host and user/user transitions equally.',
 '使用相关微码与内核 SRSO 返回路径保护。Linux 区分扩展 IBPB、Safe RET 以及按边界组合的措施。某一控制存在，不代表用户 / 内核、客户机 / 宿主和用户 / 用户切换都得到同等保护。'),
 contrast=('Retbleed also concerns RET prediction, but Inception highlights phantom speculation and transient training of later predictions. Neither requires rewriting the software return address.',
 'Retbleed 同样涉及 RET 预测，Inception 则突出 Phantom 推测与对后续预测的瞬态训练。二者都不要求改写软件保存的返回地址。'),
 trace=('''[01] architectural code has a real return R_OK
[02] event: affected phantom speculation opens a window
[03] transient activity influences return-prediction state
[04] later RET predicts a wrong GADGET
[05] transient: GADGET may run
[06] architectural: return to R_OK; prediction effects are separate''','''[01] 架构代码有真实返回地址 R_OK
[02] 输入事件：受影响的 Phantom 推测打开窗口
[03] 瞬态活动影响返回预测状态
[04] 后续 RET 预测到错误 GADGET
[05] 瞬态：GADGET 可能先执行
[06] 正式：返回 R_OK，预测副作用另论'''),
 read=('Track phantom speculation, transient training and the later return as three stages in the research. Then compare Linux’s SRSO status with the actual transition you need to protect.',
 '按三阶段阅读研究：Phantom 推测、瞬态训练、后续返回。再将 Linux 的 SRSO 状态与实际需要保护的切换边界对照。')),
 dict(id='zenbleed',name='Zenbleed · Register Lifetime / Recovery',year=2023,cve='CVE-2023-20593',family='sampling',refs=['zenbleed-author','zenbleed','amd-zenbleed'],
 thesis=('On affected Zen 2 cores, a vector-register recovery bug can expose stale data architecturally, without a cache-timing receiver.','受影响 Zen 2 核心的向量寄存器恢复问题，可能使旧数据在架构上可读，无需缓存计时接收端。'),
 trigger=('Affected speculative register recovery','受影响的推测寄存器恢复'),source=('Reused physical vector-register data','复用的物理向量寄存器数据'),formal=('Restore this context’s valid register state','恢复本上下文的正确寄存器状态'),transient=('Wrong lifetime/recovery state may escape','错误生命周期 / 恢复状态可能逸出'),
 mechanism=('Architectural registers are names backed by renamed, reusable physical storage. An architecturally executed VZEROUPPER clears upper vector state, but if it was on a mispredicted path, recovery must restore the valid state from before that operation. The original report connects incorrect lifetime/recovery bookkeeping to exposure of stale physical-register data. Our example calls the correct current-context state SELF and unrelated stale content OLD. Unlike the other sampling models, the bug can make OLD architecturally visible.',
 '架构寄存器是名字，背后是会重命名与复用的物理存储。正式执行的 VZEROUPPER 会清零向量高半部；但若它位于误预测路径，恢复时应还原该操作之前的有效状态。原报告将错误的生命周期 / 恢复记账与陈旧物理寄存器数据暴露联系起来。例子把本上下文正确状态标为 SELF，将无关旧值标为 OLD。与前面的采样模型不同，错误可能使 OLD 在架构上可见。'),
 training=('The original bug involves specific execution/recovery conditions, not a generic V1/V2 branch-training story. The explanatory model does not supply an instruction recipe for those conditions. The data readout itself need not reconstruct a cache channel.',
 '原始问题依赖具体执行 / 恢复条件，不能套用泛化的 V1/V2 分支训练故事。这里的模型不提供构造这些条件的指令配方，数据读出本身也无需重建缓存通道。'),
 boundary=('Affected Zen 2 implementations can expose data from other work using the shared physical register resources under the reported conditions. Confirm the exact AMD product and update state; do not generalize to all AMD generations or assume SMT is always the only boundary.',
 '在报告条件下，受影响 Zen 2 实现可能暴露其他工作使用共享物理寄存器资源时的数据。需确认准确 AMD 产品与更新状态，不能外推到所有 AMD 代际，也不能认为 SMT 永远是唯一边界。'),
 mitigation=('Install applicable AMD/OEM microcode or firmware updates. Treat any documented workaround as model-specific rather than as a substitute for verifying the supported fix. A cache flush does not explain or repair this register-lifetime bug.',
 '安装适用的 AMD/OEM 微码或固件更新。文档中的替代措施需按型号判断，不能代替核对正式支持的修复。刷新缓存不能解释或修复这个寄存器生命周期问题。'),
 contrast=('This is the taxonomy exception: a speculative precursor can lead to an architecturally visible stale-register value. The other sampling models discard their transient sample as an architectural result.',
 '这是分类中的边界例外：推测前因可以导致正式可见的旧寄存器值。前面的采样模型并不把瞬态样本作为架构结果提交。'),
 trace=('''[01] this context’s valid upper state = SELF
[02] wrong-path VZEROUPPER must not commit
[03] affected register lifetime/recovery event
[04] correct recovery must restore SELF
[05] bug outcome: later architectural read may expose unrelated OLD
[06] this readout does not require cache timing''','''[01] 本上下文的有效高半部状态 = SELF
[02] 错误路径的 VZEROUPPER 不应提交
[03] 出现受影响的寄存器生命周期 / 恢复事件
[04] 正确恢复应还原 SELF
[05] 错误结果：之后正式读取可能暴露无关 OLD
[06] 这类读出无需缓存计时'''),
 read=('In the original report, distinguish architectural register names, physical storage and recovery bookkeeping. Its significance is precisely that not every microarchitectural disclosure ends in a cache-timing channel.',
 '读原始报告时区分架构寄存器名字、物理存储和恢复记账。这个案例的重要性就在于，并非所有微架构信息泄漏最终都使用缓存计时通道。')),
]

WALKTHROUGHS={
'spectre-v1':('Read [02] as the gate for both [03] and [04]. Line [05] describes a possible early path, not a change to the Boolean result. In [06], 16 is still rejected. A short speculative window or unusable channel can prevent disclosure despite a misprediction.','[02] 同时约束 [03]、[04]。[05] 表示一种可能的提前执行路径，不是把布尔结果改成真；[06] 中 16 仍被拒绝。即使误预测存在，窗口太短或通道不可用也会阻止泄漏。'),
'spectre-v2':('In [01] the number identifies the branch instruction itself. In [02] it identifies the correct destination; [03] names different code. None is the secret-data address. The crucial contrast is [04] versus [06], not a corrupted pointer.','[01] 的数字定位分支指令，[02] 定位正确目的地，[03] 定位另一段代码；它们都不是秘密数据地址。关键对照是 [04] 与 [06]，不是函数指针被破坏。'),
'meltdown':('Line [03] depends on the byte requested in [02]. An independent access merely placed after a faulting instruction demonstrates a different, weaker property. Line [05] is separate ordinary observation after a suitable recovery path, not continuation of the forbidden load.','[03] 依赖 [02] 请求的字节。仅仅把一个独立访问排在故障指令之后，展示的是另一种更弱的性质。[05] 是通过适当恢复路径之后的独立正常观察，不是继续执行被禁止的读取。'),
'l1tf':('Compare [02] with [04]: the request has no valid translation, yet the possible value is limited by [03]. The value 0x2A is cached data, not a PTE or an address. The control in [06] removes this particular data source.','对照 [02]、[04]：请求没有有效翻译，但可能出现的值受 [03] 限制。0x2A 是缓存数据，不是 PTE 或地址。[06] 的对照移除了这一特定来源。'),
'mds':('The A in [03] requests one region; 0x6D in [04] came from other activity. Line [05] states what software can legitimately receive. Keeping A unchanged cannot turn sampling into an exact address-selection primitive.','[03] 的 A 请求一个区域，[04] 的 0x6D 却来自其他活动。[05] 才说明软件能合法得到什么。固定 A 不会把采样变成精确的地址选择原语。'),
'lvi':('Follow both [01] and [02] inside the victim. In [05] the victim computes with the wrong operand; the observer has not yet obtained a secret. If [04] forwards nothing, this particular dependent computation cannot use the illustrative zero early.','[01]、[02] 都在受害者内部。[05] 是受害者用错操作数，观察者此时并未得到秘密。如果 [04] 不转发任何值，这个依赖运算就不能提前使用教学零值。'),
'ssb':('Line [05] makes the aliasing relation explicit. Without that overlap, reading 3 is not an error. The difference between [04] and [06] is the value of the same location, not a sample from unrelated work.','[05] 明确了别名关系，没有重叠时读取 3 不是错误。[04]、[06] 的差别来自同一位置的新旧值，不是无关工作的样本。'),
 'taa':('The tentative counter value in [02], unrelated sample in [04] and committed value in [05] are deliberately different. Rolling back 6 establishes transaction semantics; it does not prove that the sample left no observable effect.','[02] 的暂定 counter、[04] 的无关样本和 [05] 的正式值被有意设为不同数值。回滚 6 证明事务语义，不证明样本没有留下可观察影响。'),
'bhi':('Between [03] and [04], hold [01] and [02] fixed. Only the history context changes. The example isolates a selection effect without claiming a particular hardware table layout or a recipe for generating H_B.','从 [03] 到 [04]，保持 [01]、[02] 不变，只更换历史上下文。例子隔离出选择效应，不声称特定硬件表布局，也不给出生成 H_B 的配方。'),
'retbleed':('The saved address in [01] remains unchanged in [02] and [06]. What differs is the early prediction at [04]. This is why the model should not be read as a stack-smashing or software-return-address attack.','[01] 保存的地址在 [02]、[06] 中都不变，变化的是 [04] 的提前预测，因此不能把模型读成栈破坏或软件返回地址攻击。'),
'gds':('Compare the intended elements in [01] with the old 99 in [03]. A legitimate completed lane in [05] is not this stale sample. The diagram omits real masking and fault-handling details to isolate that distinction.','对比 [01] 的正常元素与 [03] 的旧值 99。[05] 中合法完成的 lane 不等于这个样本。图省略了真实掩码和故障处理细节，以突出这种区别。'),
'rfds':('OLD in [03] is an internal retained value, not a register name the observer may choose. CURRENT in [05] remains the current context’s valid state. The example explains provenance rather than inventing a trigger instruction.','[03] 的 OLD 是内部保留值，不是可由观察者选择的寄存器名字；[05] 的 CURRENT 仍是当前上下文的有效状态。例子解释来源，不虚构触发指令。'),
'inception':('Keep [02], [03] and [04] as separate stages. The first transient window can influence predictor state used later. Neither [03] nor [04] means that the saved software return address changed.','将 [02]、[03]、[04] 分成不同阶段。第一个瞬态窗口可影响之后使用的预测状态，[03]、[04] 都不表示软件保存的返回地址被改写。'),
'zenbleed':('The bug outcome in [05] is an architectural read, unlike the discarded transient samples in MDS and RFDS. Compare it with the correctly restored SELF in [04], not a hypothetical committed zero. This exception is why the guide does not equate every disclosure with cache timing.','[05] 的错误结果是正式读取，与 MDS、RFDS 中不提交的瞬态样本不同。应与 [04] 中正确还原的 SELF 对照，而非假设提交了清零结果；这也解释了为何不能把所有泄漏都等同于缓存计时。'),
}

EXAMPLES={
'spectre-v1':dict(
 headers=[('Role','角色'),('x','x'),('x < 16','x < 16'),('Correct execution','正确执行')],
 rows=[[(('History input','历史输入')),('2 / 5 / 9','2 / 5 / 9'),('true','真'),('Read a permitted array element','读取合法数组元素')],[('Violating input','越界输入'),('16','16'),('false','假'),('Skip the entire if body','跳过整个 if 主体')]],
 code=('''// Teaching C fragment: the dependent use is a placeholder.
if (x < array1_size) {
    uint8_t value = array1[x];
    consume_value(value);
}''','''// 教学 C 片段：后续使用为占位操作。
if (x < array1_size) {
    uint8_t value = array1[x];
    consume_value(value);
}''')),
'spectre-v2':dict(
 headers=[('Teaching address','教学地址'),('Role','角色')],
 rows=[[('0x401240','0x401240'),('Location of the indirect branch instruction','间接分支指令本身的位置')],[('0x402180','0x402180'),('Architecturally correct destination','正式应到达的目标')],[('0x4030A0','0x4030A0'),('A different predicted code gadget','另一段被预测到的代码 gadget')]],
 code=('''; Illustrative setup around the paper's 32-bit indirect jump.
mov eax, [normal_target_slot]   ; teaching operand load
jmp eax                         ; the branch operand is the real target
; The branch PC is not the value stored in EAX.''','''; 围绕论文 32 位间接跳转的教学设定。
mov eax, [normal_target_slot]   ; 教学补充：载入正常目标
jmp eax                         ; 分支操作数才是正式目标
; jmp 自身的位置不是 EAX 保存的值。''')),
'meltdown':dict(
 headers=[('Question','问题'),('Independent operation','独立操作'),('Dependent disclosure','依赖泄漏')],
 rows=[[('What can execute early?','什么可能提前执行？'),('An operation not needing the faulted result','不需要故障结果的操作'),('An operation that needs the denied byte','需要被拒绝字节的操作')],[('What must hardware provide?','硬件必须提供什么？'),('An execution opportunity before fault delivery','报告故障前的执行机会'),('The denied byte reaching dependent instructions','被拒绝字节确实流向依赖指令')]],
 code=('''; Short explanatory excerpt around the denied byte load.
xor rax, rax            ; clears RAX; not the permission fault
; intervening paper instruction omitted
mov al, byte [rcx]      ; faulting access in the paper's setup
; AL is RAX's low 8 bits; later teaching operations depend on AL.''','''; 围绕被拒绝字节读取的短解释片段。
xor rax, rax            ; 清零 RAX，本身不是权限故障
; 论文中间一条指令略
mov al, byte [rcx]      ; 论文设定中会故障的内存访问
; AL 是 RAX 低 8 位，后续教学操作依赖 AL。''')),
}
