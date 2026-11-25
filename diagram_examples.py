"""Short, annotated diagram excerpts; semantic traces are NOT executable PoCs.

Pairs are (English, Chinese). Paper excerpts retain attribution in the page.
"""
def row(code, en, zh): return (code, (en, zh))

EXCERPTS = {
'spectre-v1': dict(kind=('Paper victim fragment + teaching trace', '论文受害者片段 + 教学轨迹'), cite=('Spectre appendix, victim_function', 'https://spectreattack.com/spectre.pdf#page=18'), hot=[2,3], detail=('Train with legal x; this call uses x = 16, size = 16.', '用合法 x 建立通过倾向；本次 x = 16，size = 16。'), visual='array', labels=['0','1','…','15','16'], note=('16 is outside the checked range', '16 在检查允许的范围之外'), rows=[
row('// size = 16; x = 16', 'Teaching inputs, not paper addresses', '教学输入，不是论文实测地址'),
row('if (x < array1_size) {', 'Paper: the unresolved check is false', '原文：未决检查最终为假'),
row('    temp &= array2[array1[x] * 512];', 'Paper: value selects a probe location', '原文：值决定探测数组位置'),
row('}', 'Correct execution skips the body', '正确执行跳过整个 if 主体'),
row('// predicted pass: body may run transiently', 'Only on an affected speculative path', '仅在受影响的推测路径上可能发生'),
row('// later: time probe locations separately', 'Observation is not the transient load', '后续计时观察与瞬态读取是两回事')]),
'spectre-v2': dict(kind=('Paper instruction + teaching context (32-bit x86)', '论文指令 + 教学上下文（32 位 x86）'), cite=('Spectre §5', 'https://spectreattack.com/spectre.pdf#page=7'), hot=[2,3], detail=('PC 0x401240; true target 0x402180; predicted 0x4030A0.', '分支位置 0x401240；真实目标 0x402180；预测目标 0x4030A0。'), visual='targets', labels=['PC: 0x401240','NORMAL: 0x402180','GADGET: 0x4030A0'], note=('Code targets, not secret addresses', '这些是代码地址，不是秘密地址'), rows=[
row('mov eax, [normal_target_slot]', 'Teaching load; EAX gets NORMAL', '教学读取：EAX 得到 NORMAL'),
row('jmp eax', 'Paper instruction: indirect branch', '原文指令：间接跳转'),
row('// predicted target: GADGET', 'May fetch wrong code before resolution', '解析前可能先取错误目标的指令'),
row('// GADGET uses victim-accessible data', 'A wrong target alone is not a leak', '仅猜错目标还不足以泄露'),
row('// real target resolves: NORMAL', 'Discard wrong-path register results', '取消错误路径的寄存器结果'),
row('// architectural target slot unchanged', 'No function-pointer overwrite', '没有改写函数指针')]),
'meltdown': dict(kind=('Paper key instructions + omitted steps', '论文关键指令 + 省略步骤'), cite=('Meltdown Listing 2', 'https://www.usenix.org/system/files/conference/usenixsecurity18/sec18-lipp.pdf#page=9'), hot=[3,4], detail=('RCX names a mapped supervisor-only byte; no branch training.', 'RCX 指向已映射、仅主管可读的字节；无需分支训练。'), visual='mapping', labels=['VA in RCX','Mapped / U=0','Protected byte'], note=('Mapped but denied ≠ unmapped', '已映射但权限不足 ≠ 未映射'), rows=[
row('xor rax, rax', 'Paper: clear RAX; not the fault', '原文：清零 RAX；不是故障点'),
row('; retry label / other steps omitted', 'This is not the complete Listing 2', '省略重试等步骤，不是完整 Listing 2'),
row('mov al, byte [rcx]', 'Paper: denied byte load; AL is low RAX', '原文：越权字节读取，AL 是 RAX 低位'),
row('; dependent_use(AL)  [semantic placeholder]', 'Affected CPU may forward the byte', '受影响 CPU 可能向依赖操作转发字节'),
row('; architectural outcome: permission fault', 'The byte is not committed to AL', '该字节不会正式提交到 AL'),
row('; later observation: inspect cache trace', 'A separate, non-transient measurement', '这是另一次正式执行的观察')]),
'l1tf': dict(hot=[2,4], detail=('Translation is invalid; the relevant line is already in L1D.', '地址翻译无效；相关缓存行已驻留 L1D。'), visual='mapping', labels=['LOAD(V)','INVALID PTE','L1D: 0x2A'], note=('No L1D line → this source absent', '不驻留 L1D 则缺少这条来源'), rows=[
row('request = LOAD(V)', 'Request an address, not a cache index', '请求的是地址，不是缓存索引'),
row('translate(V) = INVALID', 'Terminal translation failure', '发生终止性地址翻译故障'),
row('relevant_L1D_line = 0x2A', 'Illustrative resident byte', '教学设定的驻留字节'),
row('transient: t = 0x2A; dependent_use(t)', 'Affected forwarding despite failure', '翻译失败后仍发生受影响的转发'),
row('architectural: page_fault()', 'No valid translation is committed', '不提交有效翻译或该读取值'),
row('control: evicted line => source absent', 'Not an arbitrary DRAM read', '不能由此推导为任意 DRAM 读取')]),
'mds': dict(hot=[3,4], detail=('LOAD(A) asks for 0x17; unrelated work left 0x6D in a buffer.', 'LOAD(A) 本应得到 0x17；其他工作使缓冲区经过 0x6D。'), visual='slots', labels=['…','17','…','6D','…'], note=('Sample is not selected by A', '样本不由请求地址 A 精确选择'), rows=[
row('expected_LOAD(A) = 0x17', 'The requested address has its own value', '请求地址本来有自己的正确值'),
row('other_work -> buffer(0x6D)', 'Unrelated data traversed CPU buffers', '无关数据经过 CPU 内部缓冲区'),
row('LOAD(A) encounters fault_or_assist', 'Affected load condition, not every load', '需要受影响条件，并非任意读取'),
row('transient: t = 0x6D; dependent_use(t)', 'Sample may be unrelated to A', '样本可能与 A 无关'),
row('architectural: retry_correctly_or_fault', 'No sample becomes the load result', '样本不成为该读取的正式结果'),
row('repeat(A): sample may change', 'Sampling, not chosen-address reading', '这是采样，不是按指定地址读出')]),
'lvi': dict(hot=[2,4], detail=('Follow the victim operand: legitimate v = 1, injected v = 0.', '跟踪受害者操作数：合法 v = 1，错误输入 v = 0。'), visual='targets', labels=['LOAD(config)','Expected v: 1','Wrong v: 0'], note=('Injected operand ≠ secret value', '注入的操作数 ≠ 要推断的秘密'), rows=[
row('victim: v = LOAD(config)', 'Victim load under affected conditions', '处于受影响条件的受害者读取'),
row('victim: result = v + 10', 'Dependency carries the wrong operand', '依赖关系传播错误操作数'),
row('control: v = 1 -> result = 11', 'Normal dataflow', '正常数据流的对照'),
row('affected transient: v = 0 -> result = 10', 'Wrong result exists only transiently', '错误计算结果仅短暂存在'),
row('architectural: reject_wrong_result()', 'Not a committed config overwrite', '不是正式改写了 config'),
row('later: observe_data_dependent_effect()', 'A further effect is needed to leak', '仍需可观察的数据相关效应')]),
'ssb': dict(hot=[2,3], detail=('p and q alias slot_A; only the earlier store address is late.', 'p、q 指向同一 slot_A；较早写入的地址较晚才确定。'), visual='targets', labels=['slot_A: OLD = 3','STORE(p, 8)','LOAD(q)'], note=('Same location, not MDS sampling', '同一位置旧值，不是 MDS 采样'), rows=[
row('slot_A = 3', 'Initial value at this logical location', '该逻辑位置的初始值'),
row('STORE(p, 8)', 'Earlier store; address unresolved', '较早写入，地址尚未就绪'),
row('v = LOAD(q)', 'Later load predicts no overlap', '较晚读取预测与写入不重叠'),
row('transient: v = 3; dependent_use(v)', 'Load bypasses the older store', '读取暂时绕过较早的写入'),
row('resolve: p == q == &slot_A', 'Dependency violation detected', '发现前写后读依赖被违反'),
row('architectural: replay -> v = 8', 'Recovery restores correct ordering', '重执行恢复正确的内存顺序')]),
 'taa': dict(hot=[3,4], detail=('TSX transaction has tentative writes; an asynchronous abort is pending.', 'TSX 事务有暂定写入；异步中止正在等待处理。'), visual='slots', labels=['…','42','…','…','…'], note=('Victim need not use TSX', '被观察者不必使用 TSX'), rows=[
row('committed counter = 5', 'Initial architectural state', '初始正式状态'),
row('transaction: tentative counter = 6', 'Tentative write is not committed', '暂定写入不等于已经提交'),
row('event: asynchronous_abort_pending', 'Not a synchronous XABORT recipe', '不是用 XABORT 冒充异步中止'),
row('transient: t = buffer_sample(0x42)', 'Affected window may sample a buffer', '受影响窗口可能取得缓冲区样本'),
row('architectural: abort; counter = 5', 'Transaction writes are rolled back', '事务写入仍正确回滚'),
row('observe_trace(t)  // separate step', 'Sample is not a transaction result', '样本不是提交的事务结果')]),
'bhi': dict(hot=[3,4], detail=('Keep learned candidates fixed; change the history context.', '保持已学习的候选目标不变，改变历史上下文。'), visual='targets', labels=['H_A => candidate A','H_B => candidate B','Real => NORMAL'], note=('Model, not a fixed table layout', '逻辑模型，不代表固定表结构'), rows=[
row('real_target(J) = NORMAL', 'Architectural target stays intact', '正式目标始终不变'),
row('learned_candidates = {A, B}', 'Hold these candidates fixed', '对照中保持候选目标不变'),
row('history = H_A -> predict A', 'History participates in selection', '历史参与目标候选选择'),
row('history = H_B -> predict B', 'Different history can choose B', '不同历史可能选中 B'),
row('transient: execute(B) if B != NORMAL', 'Wrong target can execute transiently', '错误目标可能短暂执行'),
row('architectural: execute(NORMAL)', 'Not a function-pointer rewrite', '不是改写函数指针')]),
'retbleed': dict(hot=[3,4], detail=('The saved return stays R_OK; affected RET prediction selects R_OTHER.', '保存的返回地址仍为 R_OK；受影响预测却选中 R_OTHER。'), visual='targets', labels=['Saved: R_OK','RET','Predicted: R_OTHER'], note=('CPU-specific prediction conditions', '预测条件取决于具体处理器'), rows=[
row('CALL worker  // saved return = R_OK', 'Abstract call / return context', '抽象的调用 / 返回上下文'),
row('worker: saved_return remains R_OK', 'No software stack overwrite', '没有改写软件栈上的返回地址'),
row('RET', 'Return instruction is the branch', '返回指令自身就是分支'),
row('affected_predict(RET) = R_OTHER', 'Not a universal RSB-underflow rule', '并非通用的 RSB 下溢规则'),
row('transient: execute(R_OTHER)', 'Wrong-path gadget may leave a trace', '错误路径 gadget 可能留下痕迹'),
row('architectural: return_to(R_OK)', 'Real target is resolved and honored', '真实返回目标解析后仍被遵守')]),
'gds': dict(hot=[3,4], detail=('Gather should load lanes from addresses; stale vector state is different.', 'gather 应按地址读取各 lane；陈旧向量状态不是合法来源。'), visual='slots', labels=['11','22','99','44'], note=('99 is stale, not a valid lane result', '99 是旧值，不是合法完成的元素'), rows=[
row('expected = gather([a0, a1, a2, a3])', 'Semantic lanes, not assembly syntax', '语义 lane 示例，不是汇编语法'),
row('expected_values = [11, 22, 33, 44]', 'Illustrative intended values', '教学设定的正确值'),
row('event: a lane fails to complete normally', 'Affected transient gather condition', '受影响的瞬态 gather 条件'),
row('transient: dependent_use(stale_lane=99)', 'Old vector-related state may forward', '可能转发陈旧向量相关状态'),
row('architectural: follow_gather_fault_rules()', 'Partial completion is not stale leakage', '合法部分完成不等于旧值泄露'),
row('victim: prior_vector_use()  // enough', 'Victim need not execute a gather', '被观察者本身不必执行 gather')]),
'rfds': dict(hot=[3,4], detail=('Prior register use leaves OLD; the current task legitimately uses CURRENT.', '先前寄存器使用留下 OLD；当前任务合法使用 CURRENT。'), visual='slots', labels=['…','…','OLD','…','…'], note=('Not guaranteed chosen-value access', '不能保证采到指定值'), rows=[
row('prior_context: register_use(OLD)', 'Prior work on the logical processor', '该逻辑处理器先前的工作'),
row('current_context: register_use(CURRENT)', 'Current architectural value', '当前上下文的正式值'),
row('internal: stale_entry_may_retain(OLD)', 'Conceptual internal state, not an API', '内部状态示意，不是可调用 API'),
row('affected_sample() may reflect OLD', 'No universal trigger instruction claimed', '不声称存在一条通用触发指令'),
row('architectural: use(CURRENT)', 'Not named-register access to a task', '不是按寄存器名读取别的任务'),
row('mitigation: clear_affected_stale_entries', 'Clears remnants, not live task registers', '清理陈旧项，不是清空任务活寄存器')]),
'inception': dict(hot=[3,4], detail=('One speculative window can affect a later RET through predictor state.', '一次推测窗口可借预测状态影响后续 RET。'), visual='targets', labels=['Phantom window','Prediction state','Later RET => GADGET'], note=('Prediction side effects may persist', '预测状态副作用可能延续'), rows=[
row('real_return = R_OK', 'Architectural return remains intact', '正式返回地址仍然完整'),
row('event: affected_phantom_speculation', 'Abstract event; not a trigger recipe', '抽象事件，不是触发指令配方'),
row('transient_activity -> predictor_state', 'Prediction state can be influenced', '瞬态活动可能影响预测状态'),
row('later_RET: predict GADGET', 'Later branch uses altered prediction', '后续分支使用受影响的预测'),
row('transient: execute(GADGET)', 'Transient result is discarded', '瞬态路径的正式结果被取消'),
row('architectural: return_to(R_OK)', 'Recovery need not erase prediction', '恢复不代表清空预测状态')]),
'zenbleed': dict(hot=[2,5], detail=('Wrong-path VZEROUPPER must be undone; correct recovery restores SELF.', '错误路径的 VZEROUPPER 必须撤销，正确恢复应还原 SELF。'), visual='targets', labels=['Before: SELF','Recover: SELF','Bug: unrelated OLD'], note=('Stale data can be architectural', '旧值可能成为正式可见数据'), rows=[
row('valid_upper_state = SELF', 'This context has a valid prior value', '本上下文原本有合法的旧状态'),
row('wrong_path: VZEROUPPER', 'Mnemonic is real; this trace is a model', '指令名真实；整体轨迹仍是语义模型'),
row('event: affected_lifetime_recovery', 'Internal recovery bug on affected Zen 2', '受影响 Zen 2 的内部恢复错误'),
row('correct_recovery: restore(SELF)', 'Wrong-path zeroing must not commit', '错误路径清零不能被正式提交'),
row('bug: later_read() may expose OLD', 'Unrelated stale data becomes visible', '无关陈旧值可能正式可见'),
row('readout: no_cache_timing_required', 'Unlike a discarded MDS/RFDS sample', '不同于不提交的 MDS / RFDS 样本')]),
}
for item in EXCERPTS.values():
 item.setdefault('kind', ('Semantic pseudocode / not an executable PoC', '语义伪代码 / 不是可执行 PoC'))
 item.setdefault('cite', None)
