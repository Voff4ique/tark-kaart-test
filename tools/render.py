"""Renders PNG icons, OG image and pre-renders the for-sale cards (needs playwright + chrome)."""
import pathlib, re, sys, json
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from playwright.sync_api import sync_playwright
from mark import standalone, mark_svg
ROOT = pathlib.Path(__file__).resolve().parent.parent
def main():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = b.new_page()
        svg = standalone()
        for name, size in (('favicon-32', 32), ('apple-touch-icon', 180), ('icon-192', 192), ('icon-512', 512), ('favicon-48', 48), ('favicon-16', 16)):
            pg.set_viewport_size({'width': size, 'height': size})
            bg = '#f4efe8' if name.startswith('apple') or name.startswith('icon') else 'transparent'
            pad = int(size * 0.0) if not name.startswith('apple') else int(size * .06)
            pg.set_content(f'<body style="margin:0;background:{bg}"><div style="width:{size}px;height:{size}px;padding:{pad}px;box-sizing:border-box">{svg.replace("<svg ", "<svg width=%d height=%d " % (size-2*pad, size-2*pad))}</div></body>')
            pg.screenshot(path=str(ROOT / f'assets/icons/{name}.png'), omit_background=(bg == 'transparent'))
        # OG image
        pg.set_viewport_size({'width': 1200, 'height': 630})
        og = (ROOT / 'tools/og.html').read_text()
        og = re.sub(r'<script>.*?</script>', lambda m: '<script>document.getElementById("lg").innerHTML=%s+\'<div><b>Tark</b><i>KINNISVARA</i></div>\'</script>' % json.dumps(svg), og, flags=re.S)
        tmp = ROOT / 'tools/.og_run.html'; tmp.write_text(og)
        pg.goto(tmp.as_uri()); pg.wait_for_timeout(600); tmp.unlink()
        pg.screenshot(path=str(ROOT / 'assets/og-image.png'))
        # pre-render sale cards
        for lang, pre in (('et', ''), ('ru', 'ru/'), ('en', 'en/')):
            f = ROOT / pre / 'myygil.html'
            pg.goto(f.as_uri()); pg.wait_for_selector('#g .card'); 
            inner = pg.eval_on_selector('#g', 'e=>e.innerHTML')
            s = f.read_text()
            s2 = re.sub(r'<div class="grid" id="g">.*?</div><p class="note"', lambda m: '<div class="grid" id="g">' + inner.replace('\\', '\\\\') + '</div><p class="note"', s, count=1, flags=re.S)
            assert s2 != s or '<article' in s
            f.write_text(s2)
        b.close()
    from PIL import Image
    im = [Image.open(ROOT / f'assets/icons/favicon-{n}.png') for n in (16, 32, 48)]
    im[2].save(ROOT / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)], append_images=im[:2])
    for n in (16, 48): (ROOT / f'assets/icons/favicon-{n}.png').unlink()
main()
