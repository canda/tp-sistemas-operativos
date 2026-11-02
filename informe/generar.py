#!/usr/bin/env python3
"""Genera el informe usando exclusivamente código e imágenes del commit configurado."""
from pathlib import Path
import subprocess, json, hashlib, re, io, textwrap, html
from datetime import datetime
from zoneinfo import ZoneInfo
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Preformatted, Table, TableStyle, KeepTogether, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import argparse

HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser()
ap.add_argument('--repo',type=Path,default=HERE.parent)
ap.add_argument('--output',type=Path,default=HERE/'reporte-sistemas-operativos.pdf')
args=ap.parse_args()
meta=json.loads((HERE/'metadatos.json').read_text())
repo=args.repo
commit=subprocess.check_output(['git','-C',str(repo),'rev-parse',meta['commit']+'^{commit}'],text=True).strip()
def gitfile(path):
    return subprocess.check_output(['git','-C',str(repo),'show',f'{commit}:{path}'])
files=subprocess.check_output(['git','-C',str(repo),'ls-tree','-r','--name-only',commit],text=True).splitlines()
inputs={p:gitfile(p) for p in files if (p.startswith('unidad-') or p == 'consignas-tpo.md') and p.endswith(('.c','.sh','.s','.md','.png','.jpg','.jpeg'))}
fonts=Path('/System/Library/Fonts/Supplemental')
for name,filename in [('Body','Arial.ttf'),('Bold','Arial Bold.ttf'),('Mono','Courier New.ttf')]:
    candidate=fonts/filename
    if not candidate.exists():
        raise SystemExit('Falta la fuente '+str(candidate)+'. Adaptar rutas de fuentes en generar.py.')
    pdfmetrics.registerFont(TTFont(name,str(candidate)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')
navy=colors.HexColor('#152E4C'); blue=colors.HexColor('#166A94'); gray=colors.HexColor('#586674')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCustom',fontName='Bold',fontSize=26,leading=31,textColor=navy,spaceAfter=16))
styles.add(ParagraphStyle(name='H1Custom',fontName='Bold',fontSize=20,leading=25,textColor=navy,spaceAfter=16))
styles.add(ParagraphStyle(name='H2Custom',fontName='Bold',fontSize=11.5,leading=15,textColor=blue,spaceBefore=10,spaceAfter=6,keepWithNext=True))
styles.add(ParagraphStyle(name='TextCustom',fontName='Body',fontSize=10,leading=14.2,spaceAfter=7,textColor=navy))
styles.add(ParagraphStyle(name='CaptionCustom',fontName='Body',fontSize=8.1,leading=11,textColor=gray,spaceAfter=10))
styles.add(ParagraphStyle(name='CodeCustom',fontName='Mono',fontSize=8.2,leading=11.2,backColor=colors.HexColor('#F2F5F8'),borderPadding=7,spaceAfter=10))
styles.add(ParagraphStyle(name='SmallCustom',fontName='Body',fontSize=8,leading=11,textColor=gray,spaceAfter=6))
W,H=595.276,841.89
story=[]
def p(t,sty='TextCustom'):return Paragraph(html.escape(t),styles[sty])
class NumberedCanvas(canvas.Canvas):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.states=[]
    def showPage(self):self.states.append(dict(self.__dict__));self._startPage()
    def save(self):
        count=len(self.states)
        for state in self.states:
            self.__dict__.update(state)
            if self._pageNumber>1:
                self.setStrokeColor(colors.HexColor('#D6E0E9'));self.line(48,45,W-48,45)
                self.setFont('Body',8);self.setFillColor(gray)
                self.drawString(48,31,'UADE | Sistemas Operativos')
                self.drawRightString(W-48,31,f'{self._pageNumber} / {count}')
            self.showPageOriginal()
        super().save()
    def showPageOriginal(self):super().showPage()

def cover_bg(c,d):
    c.setFillColor(navy);c.rect(0,H-150,W,150,fill=1,stroke=0)
    c.setFillColor(colors.white);c.setFont('Bold',48);c.drawString(48,H-80,'UADE')
    c.setFont('Body',12);c.drawString(50,H-111,'Facultad de Ingeniería')
    c.setFillColor(blue);c.rect(48,H-165,75,5,fill=1,stroke=0)

story += [Spacer(1,135),p('Trabajo Práctico Obligatorio','TitleCustom'),p('Sistemas Operativos','H1Custom'),p('Seis ejercicios en C y Bash sobre la plataforma Red Hat'),Spacer(1,12)]
for text in ['Segundo cuatrimestre de 2026 · Materia 3.4.075','Docente: '+meta['docente'],'Fecha del informe: '+meta['fecha']]:story.append(p(text))
story += [Spacer(1,15),p('Integrantes','H2Custom')]
rows=[[p('Nombre y apellido','SmallCustom'),p('Legajo','SmallCustom')]]
for person in meta['integrantes']: rows.append([p(person['nombre']),p(person['legajo'])])
t=Table(rows,colWidths=[345,150],hAlign='LEFT');t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,blue),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#D6E0E9')),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.append(t)
story.append(PageBreak())

class ScreenshotDetail(Flowable):
    def __init__(self,data,rect):
        Flowable.__init__(self)
        self.data=data;self.rect=rect;self.width=499
        self.height=499*(rect[3]-rect[1])/(rect[2]-rect[0])
    def draw(self):
        c=self.canv;x0,y0,x1,y1=self.rect
        source=ImageReader(io.BytesIO(self.data));iw,ih=source.getSize()
        scale=self.width/(x1-x0)
        c.saveState();clip=c.beginPath();clip.rect(0,0,self.width,self.height);c.clipPath(clip,stroke=0)
        c.drawImage(source,-x0*scale,-(ih-y1)*scale,width=iw*scale,height=ih*scale)
        c.restoreState()

lines=(HERE/'contenido.md').read_text().splitlines();i=0;first=True
while i<len(lines):
    line=lines[i];i+=1
    if not line.strip():continue
    if line.startswith('# '):
        if not first:story.append(PageBreak())
        first=False;story.append(p(line[2:],'H1Custom'))
    elif line.startswith('## '):story.append(p(line[3:],'H2Custom'))
    elif line.startswith('```'):
        block=[]
        while i<len(lines) and not lines[i].startswith('```'):block.append(lines[i]);i+=1
        i+=1
        story.append(Preformatted('\n'.join(block),styles['CodeCustom'],maxLineLength=94))
    elif line.startswith('!['):
        match=re.match(r'!\[(.*?)\]\((.*?)\)$',line);caption,path=match.groups()
        data=io.BytesIO(inputs[path]);iw,ih=ImageReader(data).getSize();scale=min(499/iw,275/ih)
        if path.startswith(('unidad-2/','unidad-5/','unidad-6/')):
            if path.startswith('unidad-2/'):
                rect=(365,230,1080,775) if path.endswith('-1.jpeg') else (370,235,1085,765)
            else:
                rect=(45,130,1020,670) if path.startswith('unidad-5/') else (45,400,1020,620)
            visual=ScreenshotDetail(inputs[path],rect)
            caption += ' Detalle de la terminal; se omite el marco de escritorio.'
        else:
            visual=Image(data,width=iw*scale,height=ih*scale)
        story.append(KeepTogether([visual,Spacer(1,7),p(caption,'CaptionCustom')]))
    elif line.startswith('- '):story.append(p('• '+line[2:]))
    else:story.append(p(line))

sourcefiles=sorted(pth for pth in inputs if pth.endswith(('.c','.sh','.s')))
for idx,path in enumerate(sourcefiles):
    story.append(PageBreak())
    story.append(p('Anexo | Código fuente','H1Custom'))
    story.append(p(path,'H2Custom'))
    story.append(p('Código del repositorio. Numeración añadida; las líneas largas se continúan con sangría.','SmallCustom'))
    if path.endswith('.s'):story.append(p('Listado ensamblador incluido en el repositorio: plataforma macOS ARM64, llamada a printf.','CaptionCustom'))
    numbered=[]
    for n,line in enumerate(inputs[path].decode().splitlines(),1):
        parts=textwrap.wrap(line.expandtabs(4),width=94,replace_whitespace=False,drop_whitespace=False) or ['']
        numbered.append(f'{n:3d}  '+parts[0]);numbered.extend('     '+part for part in parts[1:])
    # Bloques pequeños permiten cortes naturales y evitan un párrafo de código indivisible.
    for offset in range(0,len(numbered),20):
        story.append(Preformatted('\n'.join(numbered[offset:offset+20]),styles['CodeCustom']))

styles.add(ParagraphStyle(name='ReferenceNote',fontName='Body',fontSize=7,leading=9.5,textColor=gray,spaceAfter=3))
story.append(Spacer(1,24))
story.append(KeepTogether([
    p('Referencia de versión (control documental)','ReferenceNote'),
    p('Commit: '+commit,'ReferenceNote'),
    p(meta['commit_titulo'],'ReferenceNote'),
    p('Fecha del commit: '+meta['commit_fecha']+' | Rama: '+meta['rama'],'ReferenceNote')
]))

args.output.parent.mkdir(parents=True,exist_ok=True)
doc=SimpleDocTemplate(str(args.output),pagesize=(W,H),rightMargin=48,leftMargin=48,topMargin=48,bottomMargin=60,title='UADE - Trabajo Práctico Obligatorio - Sistemas Operativos',author=', '.join(person['nombre'] for person in meta['integrantes']))
doc.build(story,onFirstPage=cover_bg,canvasmaker=NumberedCanvas)
manifest={'commit':commit,'fecha_generacion':datetime.now(ZoneInfo('America/Argentina/Buenos_Aires')).isoformat(),'insumos_commit':{k:hashlib.sha256(v).hexdigest() for k,v in sorted(inputs.items())},'contenido_sha256':hashlib.sha256((HERE/'contenido.md').read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}
(HERE/'manifiesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(args.output)
