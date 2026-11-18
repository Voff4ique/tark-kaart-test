"""Builds the TK mark (outlined Fraunces glyphs -> font independent SVG)."""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import pathlib
FONT=pathlib.Path(__file__).resolve().parent.parent/'assets/fonts/fraunces-latin-600-normal.woff2'
def glyphs(size=25, cx=24, cy=24):
    f=TTFont(FONT);gs=f.getGlyphSet();cm=f.getBestCmap();upm=f['head'].unitsPerEm
    cap=getattr(f['OS/2'],'sCapHeight',1400) or 1400
    sc=size/upm
    def one(ch,x):
        g=gs[cm[ord(ch)]];p=SVGPathPen(gs,ntos=lambda v:('%.2f'%v).rstrip('0').rstrip('.'))
        base=cy+cap*sc/2
        g.draw(TransformPen(p,(sc,0,0,-sc,x,base)));return p.getCommands(),g.width*sc
    _,wt=one('T',0);_,wk=one('K',0)
    kern=-0.6
    x0=cx-(wt+wk+kern)/2
    t,wt=one('T',x0);k,_=one('K',x0+wt+kern)
    return t,k
def mark_inner():
    t,k=glyphs()
    return ('<rect x="2.5" y="2.5" width="43" height="43" rx="9" fill="#f4efe8" stroke="#1c1917" stroke-width="3"/>'
            f'<path d="{t}" fill="#1c1917"/><path d="{k}" fill="#b45309"/>')
def mark_svg(cls='lm',style='',label=False):
    a=f' style="{style}"' if style else ''
    r=' role="img" aria-label="Tark Kinnisvara"' if label else ' aria-hidden="true"'
    return f'<svg class="{cls}"{a} viewBox="0 0 48 48"{r}>{mark_inner()}</svg>'
def standalone():
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">{mark_inner()}</svg>'
if __name__=='__main__': print(standalone())
