"""Validate the bilingual case guides, diagrams, index filters and preserved sources."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json,xml.etree.ElementTree as ET,hashlib,subprocess,sys
from collections import Counter
from case_notes import CASES,SOURCES,WALKTHROUGHS
from diagram_examples import EXCERPTS
from case_diagrams import wrap
ROOT=Path(__file__).resolve().parent
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.images=[];self.styles=[];self.sections=[];self.cards=[];self.languages={};self.traces=0;self.a=None
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  if tag=='a':
   if 'href' in d:self.links.append(d['href'])
   if 'data-atlas-lang' in d:self.languages[d['data-atlas-lang']]=d.get('href')
  if tag=='img':self.images.append(d);assert d.get('alt') and d.get('width') and d.get('height')
  if tag=='section':self.sections.append(d.get('id'))
  if tag=='article' and 'case-card' in d.get('class','').split():self.cards.append(d)
  if tag=='pre' and d.get('class')=='case-trace':self.traces+=1

def parse(path):
 p=Page();p.feed(path.read_text());assert len(p.ids)==len(set(p.ids)),path.name;return p

def links(path,page):
 for target in page.links+[x['src'] for x in page.images]:
  u=urlsplit(target)
  if u.scheme or u.netloc:continue
  p=(path.parent/u.path) if u.path else path
  if p.is_dir():p=p/'index.html'
  assert p.exists(),(path.name,target)
  if u.fragment and p.suffix=='.html':assert u.fragment in parse(p).ids,(path.name,target)

assert len(CASES)==14 and len({x['id'] for x in CASES})==14
assert set(WALKTHROUGHS)=={c['id'] for c in CASES}
counts=Counter(c['family'] for c in CASES);assert counts==dict(prediction=6,fault=3,sampling=5)
legacy=json.loads((ROOT/'case_original_links.json').read_text())
for zh in (False,True):
 suffix='.zh' if zh else '';lang='zh' if zh else 'en';index=ROOT/('cases'+suffix+'.html');p=parse(index)
 assert len(p.cards)==14 and Counter(x['data-family'] for x in p.cards)==counts
 links(index,p)
 for c in CASES:
  path=ROOT/('case-'+c['id']+suffix+'.html');page=parse(path);links(path,page)
  assert {x for x in page.sections if x}=={'overview','trace','training','boundary','mitigation','contrast','sources'},path.name
  assert page.traces>=1 and len(page.images)==1
  assert page.languages=={'en':'case-'+c['id']+'.html','zh':'case-'+c['id']+'.zh.html'}
  text=path.read_text();assert all(SOURCES[k][1] in text for k in c['refs'])
  assert not any(x in text for x in ['/Users/','/var/folders/','xiang/outputs'])
  for link in legacy.get(c['id'],{}).get(lang,[]):assert link['href'] in index.read_text(),link
  svg=ROOT/urlsplit(page.images[0]['src']).path;tree=ET.parse(svg)
  assert tree.getroot().attrib['viewBox']=='0 0 1280 1000'
  assert len(tree.findall('.//{http://www.w3.org/2000/svg}marker'))==2
  nodes=list(tree.iter());ex=EXCERPTS[c['id']]
  assert len([n for n in nodes if n.attrib.get('class')=='code-line'])==6
  assert len([n for n in nodes if n.attrib.get('class')=='code-highlight'])==len(ex['hot'])
  svgtext=' '.join(tree.getroot().itertext())
  for code,note in ex['rows']:
   assert len(code)*18*.61 < 633, (c['id'], code)
   assert len(wrap(note[1 if zh else 0],427/18))<=2
   assert code in svgtext
   assert code.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') in text
  assert 'diagram-code' in text
  if ex['cite']:assert ex['cite'][1] in text
 print(lang,'14 guides, one diagram and seven sections each, language/reading/source links PASS')
# Rebuild in place and make sure generated output is deterministic.
files=list(ROOT.glob('case-*.html'))+[ROOT/'cases.html',ROOT/'cases.zh.html']+list((ROOT/'assets/cases').glob('*.svg'))
before={f:hashlib.sha256(f.read_bytes()).digest() for f in files}
subprocess.run([sys.executable,str(ROOT/'build_cases.py')],check=True)
assert all(hashlib.sha256(f.read_bytes()).digest()==h for f,h in before.items()),'Build is not idempotent'
print('58 generated files deterministic; preserved research/PoC links; local anchors and SVG integrity PASS')
