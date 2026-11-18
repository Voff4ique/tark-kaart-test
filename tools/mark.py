"""Tark Kinnisvara logo A: slanted-roof towers (centre tower orange) + DM Serif Display wordmark.
All SVGs are font independent (wordmark is outlined from the self-hosted DM Serif Display file)."""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = ROOT / 'assets/fonts/dm-serif-display-latin-400-normal.woff2'
CH, AM, CREAM = '#1c1917', '#f59e0b', '#f4efe8'
POLY = [('2,48 2,30 12,24 12,48', 0), ('15,48 15,16 25,10 25,48', 0), ('28,48 28,10 38,4 38,48', 1),
        ('41,48 41,22 51,16 51,48', 0), ('54,48 54,32 62,27 62,48', 0)]

def towers(a=CH, b=AM):
    return ''.join(f'<polygon points="{p}" fill="{b if o else a}"/>' for p, o in POLY)

def mark_svg(cls='lm', style='', label=False, dark=False):
    """Wide mark (64:48) for inline use."""
    st = f' style="{style}"' if style else ''
    cl = f' class="{cls}"' if cls else ''
    r = ' role="img" aria-label="Tark Kinnisvara"' if label else ' aria-hidden="true"'
    return f'<svg{cl}{st} viewBox="-1 -1 66 50"{r}>{towers(CREAM if dark else CH)}</svg>'

def standalone():
    """Square favicon / app icon: cream rounded square + mark (readable on light and dark browser chrome)."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="15" fill="{CREAM}"/>'
            f'<g transform="translate(6 14) scale(.84375)">{towers()}</g></svg>')

def plain_mark():
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 66 50">{towers()}</svg>'

def _glyph_paths(lines, size):
    f = TTFont(FONT); gs = f.getGlyphSet(); cm = f.getBestCmap(); upm = f['head'].unitsPerEm
    sc = size / upm; out = []; widths = []
    for li, text in enumerate(lines):
        x = 0; y = (li + 1) * size * .98
        for ch in text:
            g = gs[cm[ord(ch)]]; p = SVGPathPen(gs, ntos=lambda v: ('%.2f' % v).rstrip('0').rstrip('.'))
            g.draw(TransformPen(p, (sc, 0, 0, -sc, x, y)))
            out.append((p.getCommands(), li)); x += g.width * sc
        widths.append(x)
    return out, max(widths), size * .98 * len(lines) + size * .25

def lockup_svg(dark=False, size=34):
    """Horizontal lockup: mark + two-line outlined wordmark. Returns standalone SVG."""
    ink = CREAM if dark else CH
    paths, w, h = _glyph_paths(['Tark', 'Kinnisvara'], size)
    mh = h * .86; mw = mh * 66 / 50 * 1.0; gap = size * .5
    txt = ''.join(f'<path d="{d}" fill="{ink}"/>' for d, _ in paths)
    H = max(h, mh); W = mw + gap + w
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:.1f}" role="img" aria-label="Tark Kinnisvara">'
            f'<svg x="0" y="{(H - mh) / 2:.1f}" width="{mw:.1f}" height="{mh:.1f}" viewBox="-1 -1 66 50">{towers(ink if not dark else CREAM)}</svg>'
            f'<g transform="translate({mw + gap:.1f} {(H - h) / 2 + size * .04:.1f})">{txt}</g></svg>')

if __name__ == '__main__':
    print(standalone())
