# -*- coding: utf-8 -*-
"""Build bilingual case-reading guides and integrate them into the existing case index."""
from pathlib import Path
from html import escape as e
import re,hashlib,json
from case_notes import CASES,SOURCES,WALKTHROUGHS,EXAMPLES
from case_diagrams import make_diagram, WIDTH, HEIGHT
from diagram_examples import EXCERPTS
ROOT=Path(__file__).resolve().parent
LEGACY=json.loads((ROOT/'case_original_links.json').read_text())

def name(case):return case['name']
def href(case,zh=False):return 'case-'+case['id']+('.zh' if zh else '')+'.html'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()[:12]
def css_link():return '<link rel="stylesheet" href="case-guides.css?v='+digest(ROOT/'case-guides.css')+'">'
def add_css(html):
 html=re.sub(r'<link[^>]+href="case-guides\.css[^\"]*"[^>]*>','',html)
 return html.replace('</head>',css_link()+'</head>')
def main():
 for zh in (False,True):
  def t(pair):return pair[1 if zh else 0]
  def p(pair):return '<p>'+e(t(pair))+'</p>'
  suffix='.zh' if zh else ''
  index=ROOT/('cases'+suffix+'.html');original=index.read_text()
  header=original[:original.index('<main')]
  footer=original[original.index('<footer'):]
  for i,c in enumerate(CASES):
   svg='assets/cases/'+c['id']+suffix+'.svg';(ROOT/svg).write_text(make_diagram(c,zh))
   head=re.sub(r'<title>.*?</title>','<title>'+e(name(c))+' · CPU Side Channel Atlas</title>',header)
   head=re.sub(r'<meta[^>]*name="description"[^>]*>','<meta name="description" content="'+e(t(c['thesis']),quote=True)+'">',head)
   def language_link(m):
    tag=m.group();which='data-atlas-lang="zh"' in tag
    return re.sub(r'href="[^\"]*"','href="'+href(c,which)+'"',tag)
   head=re.sub(r'<a\b[^>]*data-atlas-lang="(?:en|zh)"[^>]*>',language_link,head)
   head=add_css(head)
   crumb='<nav class="guide-breadcrumb" aria-label="'+t(('Breadcrumb','面包屑导航'))+'"><a href="cases'+suffix+'.html#catalog">'+t(('All vulnerability guides','全部漏洞导读'))+'</a><a href="foundations'+suffix+'.html">'+t(('Mechanism foundations','机制基础'))+'</a><a href="measurement'+suffix+'.html">'+t(('Cache traces and statistics','缓存痕迹与统计'))+'</a></nav>'
   body='<main id="main"><section class="guide-intro"><div class="wrap">'+crumb+'<span class="eyebrow">'+e(str(c['year'])+' / '+c['cve'])+'</span><h1>'+e(name(c))+'</h1>'+p(c['thesis'])+'</div></section>'
   headings=[('overview',('First understand the mechanism','先理解机制')),('trace',('Follow the teaching example','跟着教学例子走一遍')),('training',('What is trained or triggered?','训练 / 输入到底是什么')),('boundary',('Prerequisites and trust boundary','成立前提与信任边界')),('mitigation',('What does the mitigation interrupt?','缓解切断了哪一环')),('contrast',('Do not confuse these concepts','容易混淆的概念')),('sources',('How to read the original material','带着问题读原始资料'))]
   toc='<aside class="guide-toc"><h2>'+t(('In this guide','本篇导读'))+'</h2><nav aria-label="'+t(('On this page','本页目录'))+'">'+''.join('<a href="#'+id+'">'+t(title)+'</a>' for id,title in headings)+'</nav></aside>'
   body+='<div class="wrap guide-layout">'+toc+'<article class="guide-content">'
   def start(id,title):return '<section id="'+id+'"><h2>'+t(title)+'</h2>'
   body+=start(*headings[0])+'<dl class="case-snapshot">'+''.join('<div><dt>'+t(label)+'</dt><dd>'+e(t(c[key]))+'</dd></div>' for key,label in [('trigger',('Trigger','触发事件')),('source',('Data / prediction source','数据 / 预测来源')),('formal',('Architectural result','正式结果')),('transient',('Affected transient behavior','受影响的瞬态行为'))])+'</dl>'+p(c['mechanism'])
   body+='<figure class="case-diagram"><a href="'+svg+'?v='+digest(ROOT/svg)+'" target="_blank" rel="noopener"><img src="'+svg+'?v='+digest(ROOT/svg)+'" width="1280" height="1000" alt="'+e(t(c['thesis']),quote=True)+'" loading="lazy"></a><figcaption>'+t(('Original teaching diagram. Solid blue shows the correct semantics; dashed orange shows the affected recovery path. This exception can make stale data architecturally visible. Key code and line annotations are embedded below the flow; open full size or expand the copyable text.','本站教学图。蓝色实线表示正确语义，橙色虚线表示受影响的恢复路径。这个例外可能使旧值在架构上可见，图中包含关键代码与逐行解释；可点图放大，或展开下方可复制文本。') if c['id']=='zenbleed' else ('Original teaching diagram. Solid blue shows the architectural outcome; dashed orange shows the affected transient path. Key code and line annotations are embedded below the flow; open full size or expand the copyable text.','本站教学图。蓝色实线表示正式结果，橙色虚线表示受影响的瞬态路径。图中包含关键代码与逐行解释；可点图放大，或展开下方可复制文本。'))+'</figcaption></figure></section>'
   ex=EXCERPTS[c['id']]
   code_text='\n'.join(f'{i:02}  '+code+'  // '+t(note) for i,(code,note) in enumerate(ex['rows'],1))
   code_source=('<p><a target="_blank" rel="noopener noreferrer" href="'+ex['cite'][1]+'">'+e(ex['cite'][0])+'</a></p>') if ex['cite'] else ''
   body+='<details class="diagram-code"><summary>'+t(('Copyable code and line annotations from the diagram','复制图中的代码与逐行解释'))+'</summary><p>'+e(t(ex['kind']))+'</p><pre class="case-trace"><code>'+e(code_text)+'</code></pre>'+code_source+'</details>'
   example=''
   if c['id'] in EXAMPLES:
    ex=EXAMPLES[c['id']]
    example='<div class="case-table" tabindex="0" role="region" aria-label="'+t(('Teaching example comparison','教学例子对照'))+'"><table><thead><tr>'+''.join('<th scope="col">'+e(t(x))+'</th>' for x in ex['headers'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(t(x))+'</td>' for x in row)+'</tr>' for row in ex['rows'])+'</tbody></table></div><pre class="case-trace"><code>'+e(t(ex['code']))+'</code></pre>'
   body+=start(*headings[1])+example+'<div class="case-model">'+t(('Numbered semantic pseudocode, not a runnable attack. Labels and values are illustrative; it does not configure predictors, manufacture faults or decode secrets. The diagram is conceptual, not a measured timing trace.','编号语义伪代码，不是可运行攻击。标签和数值均为教学设定，不配置预测器、不制造故障，也不解码秘密。图是概念模型，不是实测时序。'))+'</div><pre class="case-trace"><code>'+e(t(c['trace']))+'</code></pre>'+p(WALKTHROUGHS[c['id']])+'</section>'
   for pos,key in [(2,'training'),(3,'boundary'),(4,'mitigation')]:body+=start(*headings[pos])+p(c[key])+'</section>'
   body+=start(*headings[5])+'<div class="case-compare">'+p(c['contrast'])+'</div>'
   related={'spectre-v1':'spectre-v2','spectre-v2':'bhi','meltdown':'l1tf','l1tf':'mds','mds':'lvi','lvi':'mds','ssb':'mds','taa':'mds','bhi':'retbleed','retbleed':'inception','gds':'rfds','rfds':'gds','inception':'retbleed','zenbleed':'gds'}[c['id']]
   peer=next(x for x in CASES if x['id']==related)
   body+='<p><a href="'+href(peer,zh)+'">'+t(('Compare with ','对照阅读：'))+e(name(peer))+'</a></p></section>'
   body+=start(*headings[6])+p(c['read'])+'<ul class="case-sources">'+''.join('<li><a href="'+SOURCES[k][1]+'" rel="noopener noreferrer" target="_blank">'+e(SOURCES[k][0])+'</a></li>' for k in c['refs'])+'</ul><div class="guide-read-control">'+t(('For the actual CPU, microcode, kernel and host/guest boundary, verify vendor applicability and system status. These notes do not claim hardware reproduction. ','实际平台应按 CPU、微码、内核及宿主 / 客户机边界核对厂商适用性与系统状态。本文不声称已进行硬件复现。 '))+'<a href="defense'+suffix+'.html">'+t(('Read the defense and status-check guide','查看防御与状态检查'))+'</a></div><p class="case-review">'+t(('Mechanism/source review · November 2026','机制与资料核验 · 2026 年 11 月'))+'</p></section>'
   body+='<nav class="guide-pager" aria-label="'+t(('More case guides','更多案例'))+'">'
   if i:body+='<a href="'+href(CASES[i-1],zh)+'">'+t(('Previous · ','上一篇 · '))+e(name(CASES[i-1]).split(' · ')[0])+'</a>'
   body+='<a href="cases'+suffix+'.html#catalog">'+t(('Case index','案例索引'))+'</a>'
   if i+1<len(CASES):body+='<a href="'+href(CASES[i+1],zh)+'">'+t(('Next · ','下一篇 · '))+e(name(CASES[i+1]).split(' · ')[0])+'</a>'
   body+='</nav></article></div></main>'
   (ROOT/href(c,zh)).write_text(head+body+footer)
  matrix='<section class="section" id="matrix"><div class="wrap"><div class="section-head"><div><span class="eyebrow">01 / CLASSIFICATION</span><h2>'+t(('Classify by the mechanism','先按机制对照'))+'</h2></div><p>'+t(('Fourteen representative cases, not a complete vulnerability or affected-CPU list. Follow a name for an on-site illustrated guide.','14 个代表性案例，不是完整漏洞名录或受影响 CPU 清单。点击名称进入站内图解导读。'))+'</p></div><div class="table-wrap"><table class="matrix"><thead><tr>'+''.join('<th>'+t(x)+'</th>' for x in [('Case / disclosure','案例 / 公开年份'),('Trigger','触发事件'),('Value / prediction source','值 / 预测来源'),('Architectural result','正式结果')])+'</tr></thead><tbody>'
  for c in CASES:matrix+='<tr><td><a href="'+href(c,zh)+'">'+e(name(c).split(' · ')[0])+'</a> / '+str(c['year'])+'</td>'+''.join('<td>'+e(t(c[k]))+'</td>' for k in ['trigger','source','formal'])+'</tr>'
  matrix+='</tbody></table></div></div></section>'
  catalog='<section class="section dark" id="catalog"><div class="wrap"><div class="section-head"><div><span class="eyebrow">02 / CASE FILES</span><h2>'+t(('Fourteen illustrated case guides','14 个图解案例导读'))+'</h2></div><p>'+t(('Read the mechanism snapshot here, then follow the on-site guide for a diagram, numbered pseudocode, prerequisites, distinctions and mitigation rationale before opening the original sources.','先读这里的机制快照，再进入站内导读查看流程图、编号伪代码、前提、易混点和缓解原理，最后深入原始资料。'))+'</p></div><div class="filter-row" role="group" aria-label="'+t(('Filter case families','筛选案例类别'))+'">'
  for family,label in [('all',('All','全部')),('prediction',('Prediction / dependence','预测 / 依赖')),('fault',('Fault / injection','故障 / 注入')),('sampling',('Sampling / register remnants','采样 / 寄存器残留'))]:catalog+='<button class="case-filter" data-case-filter="'+family+'" aria-pressed="'+('true' if family=='all' else 'false')+'">'+t(label)+'</button>'
  catalog+='</div><div class="case-grid">'
  for c in CASES:
   extra=''
   current_urls={SOURCES[k][1] for k in c['refs']}
   for link in LEGACY.get(c['id'],{}).get('zh' if zh else 'en',[]):
    if link['href'] not in current_urls:
     extra+='<a href="'+e(link['href'],quote=True)+'" target="_blank" rel="noopener noreferrer">'+e(link['label'])+'</a>'
   catalog+='<article class="case-card" id="'+c['id']+'" data-family="'+c['family']+'"><span class="tag">'+str(c['year'])+' · '+e(c['cve'])+'</span><h3>'+e(name(c))+'</h3>'+p(c['thesis'])+'<dl class="case-facts">'+''.join('<div><dt>'+t(label)+'</dt><dd>'+e(t(c[key]))+'</dd></div>' for key,label in [('trigger',('Trigger','触发')),('source',('Value / prediction source','值 / 预测来源')),('formal',('Architectural outcome','正式结果'))])+'</dl>'+p(c['contrast'])+'<a class="case-guide-link" href="'+href(c,zh)+'">'+t(('Read the illustrated mechanism guide','阅读图解机制导读'))+'</a><div class="links">'+''.join('<a href="'+SOURCES[k][1]+'" target="_blank" rel="noopener noreferrer">'+e(SOURCES[k][0])+'</a>' for k in c['refs'])+extra+'</div></article>'
  catalog+='</div></div></section>'
  s=original
  for ident,replacement in [('matrix',matrix),('catalog',catalog)]:
   pattern=r'<section\b[^>]*\bid="'+ident+r'"[^>]*>.*?</section>'
   s,n=re.subn(pattern,lambda m:replacement,s,count=1,flags=re.S);assert n==1,ident
  old=t(('Organize representative real-world vulnerabilities by trigger mechanism and leakage boundary. Each card links to original material from the research team or vendor; PoC reproducibility depends on the processor and mitigation state.','按触发机制和泄漏边界整理代表性真实漏洞。每张卡片连接研究团队或供应商原始资料；PoC 是否能重现，取决于处理器和缓解状态。'))
  if zh:s=s.replace(old,'从触发事件、数据 / 预测来源和正式结果出发，理解 14 个代表性漏洞。每个案例都有站内图解导读与一手资料，帮助在阅读论文前建立准确的机制模型。')
  else:
   s=re.sub(r'(<h1>.*?</h1>)<p>.*?</p>',lambda m:m[1]+'<p>Understand fourteen representative vulnerabilities through their triggers, data or prediction sources, and architectural outcomes. Each case has an on-site illustrated guide and primary references.</p>',s,count=1,flags=re.S)
  s=re.sub(r'<meta[^>]*name="description"[^>]*>', '<meta name="description" content="'+t(('Fourteen illustrated CPU vulnerability guides with mechanisms, prerequisites, numbered pseudocode, distinctions and mitigations.','14 个 CPU 漏洞图解导读，包含机制、前提、编号伪代码、关键区别与缓解原理。'))+'">',s)
  s=add_css(s);index.write_text(s)
 print('Built 28 bilingual vulnerability guides, 28 SVG diagrams, and two 14-case indexes')

if __name__=='__main__':main()
