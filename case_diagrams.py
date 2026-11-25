"""Bilingual SVG diagrams: event / split outcome / source, then annotated code."""
from html import escape
import unicodedata
from diagram_examples import EXCERPTS

INK='#17263d'; MUTED='#53677d'; BLUE='#2459bf'; ORANGE='#b65314'
WIDTH=1280; HEIGHT=1000

def units(s):
 return sum(1 if unicodedata.east_asian_width(c) in 'WF' else .59 for c in s)

def wrap(s, limit):
 """Font-relative wrapping, including CJK and long symbolic names."""
 out=[]; line=''
 for word in s.split(' '):
  candidate=(line+' '+word).strip()
  if units(candidate)<=limit:line=candidate;continue
  if line:out.append(line);line=''
  for ch in word:
   if units(line+ch)>limit:out.append(line);line=''
   line+=ch
 if line:out.append(line)
 return out

def make_diagram(case, zh):
 def t(pair):return pair[1 if zh else 0]
 def text(x,y,s,size=19,color=INK,bold=False,mono=False,extra=''):
  return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}"'+(' font-weight="700"' if bold else '')+(' font-family="ui-monospace, SFMono-Regular, Consolas, monospace"' if mono else '')+extra+'>'+escape(s)+'</text>'
 def lines(x,y,s,width,size=20,color=INK,bold=False,gap=26):
  return ''.join(text(x,y+i*gap,v,size,color,bold) for i,v in enumerate(wrap(s,width/size)))
 def rect(x,y,w,h,fill,stroke='none',rx=14,extra=''):
  return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" {extra}/>'
 def arrow(path,color=BLUE,dashed=False):
  return f'<path d="{path}" fill="none" stroke="{color}" stroke-width="3"'+(' stroke-dasharray="8 6"' if dashed else '')+' marker-end="url(#'+('orange' if color==ORANGE else 'blue')+')"/>'
 ex=EXCERPTS[case['id']]; zen=case['id']=='zenbleed'
 title=case['name'].split(' · ')[0]
 body=text(40,34,t(('MECHANISM / CODE WALKTHROUGH','机制 / 代码图解')),17,BLUE,True)
 body+=text(40,80,title,34,INK,True)+lines(40,116,t(case['thesis']),1195,21,MUTED)
 body+=rect(30,174,1220,334,'#fff','#d6e0ef',22)
 for x,label in [(55,('What starts it?','从什么事件开始？')),(445,('Correct outcome vs affected behavior','正确结果与受影响行为')),(975,('Source of data / prediction','数据 / 预测从哪里来'))]:body+=text(x,208,t(label),17,MUTED,True)
 body+=rect(54,230,288,245,'#f1f5fa')
 body+=lines(73,263,t(case['trigger']),249,22,INK,True)
 # The concrete inputs sit apart from the generic hardware condition.
 body+=lines(73,362,t(ex['detail']),249,18,MUTED,gap=25)
 body+=rect(438,230,494,105,'#eaf1ff')
 body+=text(456,257,t(('Correct recovery','正确恢复') if zen else ('Architectural outcome','正式结果')),17,BLUE,True)
 body+=lines(456,288,t(case['formal']),457,21,BLUE,gap=26)
 body+=rect(438,365,494,110,'#fff1e6')
 body+=text(456,392,t(('Affected recovery / bug outcome','受影响的恢复 / 错误结果') if zen else ('Affected transient behavior','受影响的瞬态行为')),17,ORANGE,True)
 body+=lines(456,424,t(case['transient']),457,21,ORANGE,gap=26)
 body+=arrow('M342 330H366L403 283H426')+arrow('M366 330L403 420H426',ORANGE,True)
 body+='<circle cx="366" cy="330" r="5" fill="white" stroke="#6c839c" stroke-width="2"/>'
 body+='<path d="M954 224V479" stroke="#e1e8f0"/>'
 body+=rect(970,230,258,245,'#f4f7fb')
 labels=ex['labels']
 if ex['visual'] in ('slots','array'):
  n=len(labels);cell=40 if n==4 else 34;gap=8;start=985
  for i,label in enumerate(labels):
   hot=(i==n-1 if ex['visual']=='array' else label in ('6D','42','99','OLD'))
   body+=rect(start+i*(cell+gap),251,cell,40,'#ffe0bb' if hot else '#fff',ORANGE if hot else '#cddaea',6)
   body+=text(start+i*(cell+gap)+5,277,label,15,ORANGE if hot else MUTED,hot,True)
  body+=lines(986,328,t(case['source']),226,20,ORANGE,True)
 else:
  for i,label in enumerate(labels):
   hot=i==2
   body+=rect(985,246+i*47,228,36,'#fff1e6' if hot else '#e9f0ff')
   body+=text(997,270+i*47,label,16,ORANGE if hot else BLUE,True,True)
  body+=lines(986,417,t(ex['note']),224,17,MUTED,gap=22)
 if ex['visual'] in ('slots','array'):
  body+=lines(986,402,t(ex['note']),224,17,MUTED,gap=22)
 body+=rect(30,528,1220,411,'#fff','#d6e0ef',22)
 body+=text(55,561,t(('KEY CODE / Follow the highlighted line through the diagram','主要代码 / 对照上图，跟踪高亮行的行为')),20,BLUE,True)
 body+=text(55,590,t(ex['kind']),17,MUTED)
 body+=rect(54,606,1172,280,'#f4f7fb')
 body+='<path d="M755 618V875" stroke="#d5deeb"/>'
 for i,(code,explanation) in enumerate(ex['rows'],1):
  y=638+(i-1)*46;hot=i in ex['hot']
  if hot:body+=rect(61,y-24,1158,41,'#fff0e0',rx=6,extra='class="code-highlight"')
  body+=text(73,y,f'{i:02}',17,ORANGE if hot else MUTED,hot,True)
  body+=text(115,y,code,18,ORANGE if hot else INK,hot,True,extra=' class="code-line"')
  body+=lines(775,y-5,t(explanation),427,18,ORANGE if hot else MUTED,hot,gap=21)
 footer=t(('Fragment only: setup, trigger machinery and receiver are omitted; not a hardware reproduction.','仅保留关键片段：省略环境、触发机制和接收端；不代表已在硬件上复现。'))
 body+=text(55,910,footer,17,MUTED)
 if ex['cite']:body+=text(55,931,t(('Key instruction source: ','关键指令出处：'))+ex['cite'][0],14,MUTED)
 else:body+=text(55,931,t(('Semantic model: labels / values are illustrative, not real internal APIs.','语义模型：标签 / 数值用于讲解，不代表真实内部 API。')),14,MUTED)
 body+='<path d="M40 971H78" stroke="'+BLUE+'" stroke-width="3"/>'
 body+=text(91,977,t(('Correct semantics','正确语义')),17,MUTED)
 body+='<path d="M310 971H348" stroke="'+ORANGE+'" stroke-width="3" stroke-dasharray="8 6"/>'
 body+=text(362,977,t(('Affected path','受影响路径')),17,MUTED)
 body+=text(650,977,t(('Zenbleed: stale data may be architectural','Zenbleed：旧值可能正式可见') if zen else ('Transient result discarded; a trace may remain','瞬态结果被取消，但痕迹可能保留')),17,MUTED)
 defs=''.join(f'<marker id="{id}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="{color}"/></marker>' for id,color in [('blue',BLUE),('orange',ORANGE)])
 desc=t(case['thesis'])+' '+t(ex['kind'])+' '+ ' '.join(code+' '+t(note) for code,note in ex['rows'])
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)} / {escape(t(("annotated code walkthrough","代码图解")))}</title><desc id="desc">{escape(desc)}</desc><defs>{defs}</defs><rect width="{WIDTH}" height="{HEIGHT}" fill="#f5f7fc"/><g font-family="system-ui, sans-serif">{body}</g></svg>'
