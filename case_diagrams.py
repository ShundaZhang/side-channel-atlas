"""Original bilingual conceptual diagrams: architectural outcomes versus transient work."""
from html import escape
import textwrap

INK='#17263d';MUTED='#53677d';BLUE='#2459bf';ORANGE='#b65314'

def make_diagram(case, zh):
 def t(pair):return pair[1 if zh else 0]
 def text(x,y,s,size=19,color=INK,bold=False):
  return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}"'+(' font-weight="700"' if bold else '')+'>'+escape(s)+'</text>'
 def lines(x,y,s,width=35,size=20,color=INK):
  return ''.join(text(x,y+i*27,v,size,color) for i,v in enumerate(textwrap.wrap(s,width if not zh else max(11,int(width*.6)),break_long_words=False)))
 title=case['name'].split(' · ')[0]
 body=text(28,39,title,24,INK,True)
 blue_legend=('Solid blue = correct semantics','蓝色实线 = 正确语义') if case['id']=='zenbleed' else ('Solid blue = architectural outcome','蓝色实线 = 正式结果')
 body+=text(28,76,t(blue_legend),17,BLUE)
 orange_legend=('Dashed orange = affected bug path','橙色虚线 = 受影响的错误路径') if case['id']=='zenbleed' else ('Dashed orange = affected transient behavior','橙色虚线 = 受影响的瞬态行为')
 body+=text(500,76,t(orange_legend),17,ORANGE)
 body+='<rect x="28" y="125" width="260" height="195" rx="14" fill="#f0f4f9"/>'
 body+=text(47,158,t(('Trigger / event','触发 / 事件')),18,MUTED,True)+lines(47,198,t(case['trigger']),21,20)
 body+='<rect x="390" y="110" width="580" height="112" rx="14" fill="#e9f0ff"/>'
 body+=text(410,142,t(('Expected correct result','本应得到的正确结果') if case['id']=='zenbleed' else ('Architectural result','正式结果')),18,BLUE,True)+lines(410,179,t(case['formal']),43,20,BLUE)
 body+='<rect x="390" y="275" width="580" height="112" rx="14" fill="#fff0e4"/>'
 body+=text(410,307,t(('Affected transient path','受影响的瞬态路径')),18,ORANGE,True)+lines(410,344,t(case['transient']),43,20,ORANGE)
 body+=f'<path d="M288 210H332V166H380" fill="none" stroke="{BLUE}" stroke-width="3" marker-end="url(#blue)"/>'
 body+=f'<path d="M288 210H332V331H380" fill="none" stroke="{ORANGE}" stroke-width="3" stroke-dasharray="8 6" marker-end="url(#orange)"/>'
 body+='<rect x="28" y="346" width="260" height="125" rx="14" fill="#f0f4f9"/>'
 body+=text(47,375,t(('Value / prediction source','值 / 预测的来源')),16,MUTED,True)+lines(47,407,t(case['source']),23,18)
 footer=t(('No wrong-path result is committed; a trace may remain.','错误路径结果不提交，但可能留下痕迹。'))
 if case['id']=='zenbleed':footer=t(('Exception: stale data may become architecturally visible.','边界例外：旧值可能成为正式可见结果。'))
 body+=lines(390,429,footer,46,18,MUTED)
 title=t((title+' · conceptual flow',title+' · 概念流程'))
 desc=t((case['thesis'][0],case['thesis'][1]))
 defs=f'<marker id="blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="{BLUE}"/></marker><marker id="orange" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="{ORANGE}"/></marker>'
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 490" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc><defs>{defs}</defs><rect width="1000" height="490" fill="#fff"/><g font-family="system-ui, sans-serif">{body}</g></svg>'
