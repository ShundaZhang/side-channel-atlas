# -*- coding: utf-8 -*-
"""Causal diagrams, deliberately separating architectural and predictor state."""
from html import escape
from case_diagrams import wrap
W=1280;H=960
BLUE='#2459bf';ORANGE='#b65314';INK='#17263d';MUTED='#53677d'

def make_prediction_diagram(id,zh):
 def t(v):return v[1 if zh else 0]
 def text(x,y,s,size=20,color=INK,bold=False):
  return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}"'+(' font-weight="700"' if bold else '')+'>'+escape(s)+'</text>'
 def lines(x,y,s,width,size=20,color=INK,bold=False):
  return ''.join(text(x,y+i*27,line,size,color,bold) for i,line in enumerate(wrap(s,width/size)))
 def box(x,y,w,h,title,body,color=BLUE):
  fill='#eef3ff' if color==BLUE else '#fff1e5'
  return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="#d6e0ef"/>'+lines(x+20,y+33,t(title),w-40,21,color,True)+lines(x+20,y+78,t(body),w-40,19)
 def arrow(path,color=BLUE,dashed=False):
  return f'<path d="{path}" fill="none" stroke="{color}" stroke-width="3"'+(' stroke-dasharray="8 6"' if dashed else '')+f' marker-end="url(#{"orange" if color==ORANGE else "blue"})"/>'
 if id=='retbleed':
  title=t(('Retbleed: the real stack and prediction are separate','Retbleed：真实软件栈与预测状态是两条路径'))
  s=text(40,52,title,30,INK,True)
  s+=text(40,87,t(('S = training branch; T = victim RET; G = gadget; R_OK = real saved return','S = 训练分支；T = 受害者 RET；G = gadget；R_OK = 真实返回地址')),19,MUTED)
  s+=box(40,116,570,140,('Architectural path','架构路径'),('CALL saves R_OK in software stack. T: RET must return to R_OK.','CALL 把 R_OK 保存在软件栈。T: RET 最终必须返回 R_OK。'))
  s+=box(670,116,570,140,('Normal prediction path','正常预测路径'),('CALL tracks R_OK in RSB. RET predicts from it before the stack target is ready.','CALL 在 RSB 跟踪 R_OK；RET 在栈目标就绪前借它提前预测。'))
  s+=box(40,294,570,155,('Intel path in the original evaluation','原评估的 Intel 路径'),('No usable RSB prediction → alternate indirect-target prediction. Software R_OK is still present.','无可用 RSB 预测 → 使用间接目标的替代预测路径；软件栈中的 R_OK 仍然存在。'),ORANGE)
  s+=box(670,294,570,155,('AMD Zen 1/2 evaluated path','原评估的 AMD Zen 1 / 2 路径'),('Colliding indirect branch → type confusion at RET. RAS need not be empty.','碰撞的间接分支 → RET 处发生类型混淆；不要求 RAS 先变空。'),ORANGE)
  s+=box(40,490,350,165,('Train target state: S → G','训练目标状态：S → G'),('Execute branches, not secret bytes. Relevant predictor aliasing with T is required.','执行的是分支，不是秘密字节；需要与 T 在相关预测状态中别名。'),ORANGE)
  s+=box(465,490,350,165,('T: RET predicts G','T: RET 先预测到 G'),('Affected path + trained state → transiently fetch code at G.','受影响预测路径 + 已训练状态 → 从 G 瞬态取指。'),ORANGE)
  s+=box(890,490,350,165,('Resolve: return R_OK','解析后：返回 R_OK'),('Squash G. A useful gadget may already have left a data-dependent trace.','取消 G 路径；有用 gadget 可能已经留下数据相关痕迹。'))
  s+=arrow('M325 449V469H550V480',ORANGE,True)+arrow('M955 449V469H740V480',ORANGE,True)
  s+=arrow('M390 574H452',ORANGE,True)+arrow('M815 574H877')
  s+=box(40,697,1200,208,('Read the two stacks independently','把两种栈分开阅读'),('Software: CALL f; CALL g; RET → R_f; RET → R_main. RSB: predicts those returns only while useful entries exist. Underflow is a prediction shortage, not a software-stack memory error. No fixed RSB capacity is assumed. RSB is not CET shadow stack.','软件栈：CALL f；CALL g；RET → R_f；RET → R_main。RSB：有可用项时提前预测这些返回。下溢是预测项不足，不是软件栈内存错误。不假设固定 RSB 容量；RSB 也不是 CET shadow stack。'))
 else:
  title=t(('BHI: target training and history shaping are different phases','BHI：目标关联训练与历史构造是两个不同阶段'))
  s=text(40,52,title,30,INK,True)
  s+=text(40,87,t(('Logical predictor model; not a universal hardware table layout or a runnable PoC','逻辑预测模型；不代表通用硬件表布局，也不是可运行 PoC')),19,MUTED)
  s+=box(40,116,560,164,('Victim-domain preparation','受害者预测域内的准备'),('A seed branch executes toward G in the relevant domain → useful target state is learned. G is not an arbitrary new user-mode target.','同域训练分支执行到 G → 学习有用目标关联。G 不是凭空新增的任意用户态目标。'))
  s+=box(680,116,560,164,('User-side history preparation','用户侧的历史准备'),('Execute a chosen sequence of branches → history H. The input is control flow, not secret data or a new function pointer.','执行选定分支序列 → 历史 H。输入是控制流，不是秘密数据或新函数指针。'),ORANGE)
  s+=arrow('M320 280V343H420V385')+arrow('M960 280V343H860V385',ORANGE,True)
  s+=text(760,326,t(('domain transition; history may influence selection','域切换；历史仍可能影响选择')),16,ORANGE)
  s+=box(190,397,900,155,('Victim indirect branch J: call fp','受害者间接分支 J：call fp'),('fp = handlers[id] = NORMAL. Conceptually: predicted = Predict(J, H, mode, learned_state). History affects selection; fp stays NORMAL.','fp = handlers[id] = NORMAL。概念式：预测目标 = Predict(J, H, mode, 已学习状态)。历史影响选择；fp 仍为 NORMAL。'))
  s+=arrow('M420 552V594H320V625')+arrow('M860 552V594H960V625',ORANGE,True)
  s+=box(40,637,560,145,('Control history H_A → predict NORMAL','对照历史 H_A → 预测 NORMAL'),('Keep J, fp and target state fixed. Correct target is predicted.','保持 J、fp 和目标状态不变，预测命中正确目标。'))
  s+=box(680,637,560,145,('Matching history H_G → predict G','匹配历史 H_G → 预测 G'),('An eligible learned G entry may be selected. Execute G transiently; later recover to NORMAL.','可能选中允许域内已学习的 G 项；G 瞬态执行，之后恢复到 NORMAL。'),ORANGE)
  s+=text(40,826,t(('Candidates ≠ if conditions. History ≠ fp. eIBRS target-mode isolation ≠ history isolation.','候选目标 ≠ if 条件；历史 ≠ fp；eIBRS 的目标模式隔离 ≠ 历史隔离。')),21,INK,True)
  s+=lines(40,866,t(('H_A / H_G are labels, not writable BHB bit strings. Real matching depends on CPU-specific context and intervening branches. A disclosure gadget and observation channel are still necessary.','H_A / H_G 是标签，不是可写入的 BHB 比特串。真实匹配取决于具体 CPU 上下文及途中分支；仍须有泄漏 gadget 和观察通道。')),1200,19,MUTED)
 defs=''.join(f'<marker id="{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="{c}"/></marker>' for i,c in [('blue',BLUE),('orange',ORANGE)])
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title><defs>{defs}</defs><rect width="{W}" height="{H}" fill="#f5f7fc"/><g font-family="system-ui, sans-serif">{s}</g></svg>'
