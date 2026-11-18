# -*- coding: utf-8 -*-
"""Static site build: src/*.src.html -> ET root, /ru/, /en/ with SEO/GEO markup.
Run:  python3 tools/build.py
"""
import re, json, os, sys, html, subprocess, pathlib, shutil
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import content as K
from mark import mark_svg, standalone

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
C = json.load(open(ROOT / 'tools/company.json'))
BASE = C['baseUrl']
LANGS = ['et', 'ru', 'en']
PFX = {'et': '', 'ru': 'ru/', 'en': 'en/'}
FILES = {'index': 'index.html', 'myygil': 'myygil.html', 'kaart': 'kaart.html', 'privacy': 'privacy.html'}
LABEL = {'et': 'ET', 'ru': 'RU', 'en': 'EN'}
esc = lambda s: html.escape(s, quote=True)
ADDR_LINE = None
if C.get('address'):
    ADDR_LINE = C['address']

def page_url(lang, page):
    f = FILES[page]
    return BASE + '/' + PFX[lang] + ('' if page == 'index' else f)

def rel_to(lang_from, lang_to, page):
    start = PFX[lang_from] or '.'
    target = PFX[lang_to] + ('' if page == 'index' else FILES[page])
    if page == 'index':
        r = os.path.relpath(PFX[lang_to] or '.', start)
        return './' if r == '.' else r.rstrip('/') + '/'
    return os.path.relpath(target, start)

def node_tx(page_text):
    m = re.search(r'const TX=', page_text); n = re.search(r'\nlet LANG=', page_text)
    seg = page_text[m.start():n.start()]
    js = ("const fs=require('fs');const vm=require('vm');const seg=fs.readFileSync(process.argv[2],'utf8');"
          "const ctx={};vm.createContext(ctx);vm.runInContext(seg+';this.TX=TX',ctx);"
          "const o={};for(const l of Object.keys(ctx.TX)){o[l]={};for(const [k,v] of Object.entries(ctx.TX[l])){if(typeof v!=='function')o[l][k]=v}}"
          "console.log(JSON.stringify(o))")
    tmp = ROOT / 'tools/.tx_seg.js'; tmp.write_text(seg)
    jf = ROOT / 'tools/.tx_run.js'; jf.write_text(js)
    out = subprocess.check_output(['node', str(jf), str(tmp)])
    tmp.unlink(); jf.unlink()
    return json.loads(out)

def js_obj(d):
    return json.dumps(d, ensure_ascii=False)

def must_sub(pat, rep, s, flags=re.S, count=0):
    s2, n = re.subn(pat, rep, s, count=count, flags=flags)
    if n == 0: raise SystemExit('PATTERN NOT FOUND: ' + pat[:80])
    return s2

def must_rep(old, new, s):
    if old not in s: raise SystemExit('TEXT NOT FOUND: ' + old[:80])
    return s.replace(old, new)

# ------------------------------------------------------------------ common transforms
def common(s, lang, page, A):
    # TX extras injected before `let LANG=`
    ex = K.EXTRA_TX.get(page, {}).get(lang)
    allx = ''.join(f"Object.assign(TX.{l},{js_obj(K.EXTRA_TX[page][l])});\n" for l in LANGS) if page in K.EXTRA_TX else ''
    s = must_rep('\nlet LANG=', '\n' + allx + 'let LANG=', s)
    # language handling: language comes from the page itself (one URL per language)
    s = must_sub(r"let LANG=[^\n]*\n", "let LANG=document.documentElement.lang;if(!TX[LANG])LANG='et';\n", s, count=1)
    s = s.replace("try{localStorage.setItem('lang',l)}catch(e){}", '')
    s = must_sub(r"document\.querySelectorAll\('\.(lang|lg) button'\)\.forEach\(b=>b\.onclick=\(\)=>setLang\(b\.dataset\.l\)\);", '', s)
    s = s.replace(".lang button')", ".lang a')").replace(".lg button')", ".lg a')")
    s = s.replace('.lang button{', '.lang a{text-decoration:none;').replace('.lang button.on{', '.lang a.on{')
    s = s.replace('.lg button{', '.lg a{text-decoration:none;').replace('.lg button.on{', '.lg a.on{')
    # switcher markup
    def sw(m):
        cls = m.group(2)
        links = ''.join(
            f'<a href="{rel_to(lang, l, page)}" hreflang="{l}" lang="{l}" data-l="{l}"{" class=\"on\" aria-current=\"true\"" if l == lang else ""}>{LABEL[l]}</a>'
            for l in LANGS)
        return f'<{m.group(1)} class="{cls}"{m.group(3)} aria-label="Language">{links}</{m.group(1)}>'
    s = must_sub(r'<(span|div) class="(lang|lg)"([^>]*)>(?:<button data-l="\w+">\w+</button>){3}</\1>', sw, s)
    # logo mark
    s = re.sub(r'<svg class="lm"( style="[^"]*")? viewBox="0 0 40 40"[^>]*>.*?</svg>',
               lambda m: mark_svg('lm', (m.group(1) or '')[8:-1]), s, flags=re.S)
    # fonts / leaflet / icons / robots
    s = s.replace('<meta name="robots" content="noindex,nofollow">', '')
    s = re.sub(r'<link rel="preconnect" href="https://fonts[^>]*>', '', s)
    s = re.sub(r'<link href="https://fonts.googleapis.com[^>]*>', '', s)
    s = re.sub(r'<link rel="icon"[^>]*>', '', s)
    s = re.sub(r'<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">', '', s)
    s = s.replace('<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>', f'<script src="{A}assets/vendor/leaflet/leaflet.js"></script>')
    s = re.sub(r'<title>.*?</title>', '', s, count=1, flags=re.S)
    s = s.replace('<html lang="et">', f'<html lang="{lang}">')
    # remove leftover staging copy from the source dictionaries
    s = re.sub(r'f_test:"[^"]*",?', '', s)
    s = re.sub(r'foot:"(Testversioon|Тестовая версия|Test version)[^"]*",', '', s)
    s = re.sub(r' \((test|тест)\)', '', s)
    return s

def head_block(lang, page, A, jsonld):
    title, desc = K.META[page][lang]
    canon = page_url(lang, page)
    alts = ''.join(f'<link rel="alternate" hreflang="{l}" href="{page_url(l, page)}">' for l in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{page_url("et", page)}">'
    og_img = BASE + '/assets/og-image.png'
    og = (f'<meta property="og:type" content="website"><meta property="og:site_name" content="Tark Kinnisvara">'
          f'<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">'
          f'<meta property="og:url" content="{canon}"><meta property="og:image" content="{og_img}">'
          f'<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
          f'<meta property="og:image:alt" content="Tark Kinnisvara">'
          f'<meta property="og:locale" content="{K.OG_LOCALE[lang]}">' +
          ''.join(f'<meta property="og:locale:alternate" content="{K.OG_LOCALE[l]}">' for l in LANGS if l != lang) +
          f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}">'
          f'<meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{og_img}">')
    icons = (f'<link rel="icon" href="{A}assets/icons/favicon.svg" type="image/svg+xml">'
             f'<link rel="icon" href="{A}assets/icons/favicon-32.png" sizes="32x32" type="image/png">'
             f'<link rel="apple-touch-icon" href="{A}assets/icons/apple-touch-icon.png"><link rel="manifest" href="{A}manifest.webmanifest">')
    pre = ''.join(f'<link rel="preload" as="font" type="font/woff2" crossorigin href="{A}assets/fonts/{f}.woff2">'
                  for f in ('inter-latin-400-normal', 'fraunces-latin-600-normal'))
    css = f'<link rel="stylesheet" href="{A}assets/fonts.css">'
    if page in ('index', 'kaart'):
        css += f'<link rel="stylesheet" href="{A}assets/vendor/leaflet/leaflet.css"><link rel="preconnect" href="https://server.arcgisonline.com" crossorigin>'
    if page == 'myygil':
        css += '<link rel="preconnect" href="https://img-kv.ee" crossorigin>'
    stg = ("<script>(function(){if(!/(^|\\.)tarkkinnisvara\\.ee$/.test(location.hostname)){var m=document.createElement('meta');"
           "m.name='robots';m.content='noindex,nofollow';document.head.appendChild(m)}})()</script>")
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False, separators=(",", ":"))}</script>'
    return (f'<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">'
            f'<meta name="robots" content="max-image-preview:large,max-snippet:-1"><link rel="canonical" href="{canon}">{alts}'
            f'<meta name="theme-color" content="#f4efe8"><meta name="format-detection" content="telephone=no">{og}{icons}{pre}{css}{stg}{ld}')

def org_node():
    n = {"@type": ["RealEstateAgent", "Organization"], "@id": BASE + "/#org", "name": C['name'], "legalName": C['legalName'],
         "url": BASE + "/", "logo": {"@type": "ImageObject", "url": BASE + "/assets/icons/icon-512.png", "width": 512, "height": 512},
         "image": BASE + "/assets/og-image.png", "email": C['email'], "telephone": C['phoneE164'],
         "identifier": {"@type": "PropertyValue", "propertyID": "Estonian Business Registry code", "value": C['regCode']},
         "address": {"@type": "PostalAddress", "addressLocality": "Tallinn", "addressCountry": "EE"},
         "areaServed": [{"@type": "City", "name": "Tallinn"}, {"@type": "AdministrativeArea", "name": "Harju maakond"}],
         "knowsLanguage": ["et", "ru", "en"],
         "contactPoint": {"@type": "ContactPoint", "contactType": "customer service", "telephone": C['phoneE164'], "email": C['email'],
                          "availableLanguage": ["Estonian", "Russian", "English"]}}
    if C.get('address'):
        n['address'] = {"@type": "PostalAddress", "streetAddress": "Käämo tee 8", "addressLocality": "Harkujärve küla, Harku vald",
                        "addressRegion": "Harju maakond", "postalCode": "76912", "addressCountry": "EE"}
    if C.get('vat'): n['vatID'] = C['vat']
    return n

def website_node(lang):
    return {"@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/", "name": "Tark Kinnisvara",
            "inLanguage": ["et", "ru", "en"], "publisher": {"@id": BASE + "/#org"}}

def webpage_node(lang, page, tx, extra=None):
    title, desc = K.META[page][lang]
    n = {"@type": "WebPage" if page != 'index' else "WebPage", "@id": page_url(lang, page) + "#webpage", "url": page_url(lang, page),
         "name": title, "description": desc, "inLanguage": lang, "isPartOf": {"@id": BASE + "/#website"},
         "about": {"@id": BASE + "/#org"}, "dateModified": C['modified'],
         "primaryImageOfPage": {"@type": "ImageObject", "url": BASE + "/assets/og-image.png"}}
    if extra: n.update(extra)
    return n

def breadcrumb(lang, page, tx):
    items = [("Tark Kinnisvara", page_url(lang, 'index'))]
    if page != 'index':
        nm = {'myygil': tx.get('h') or tx.get('nm7'), 'kaart': tx.get('nm4') or 'Map', 'privacy': K.META['privacy'][lang][0].split(' |')[0]}[page]
        items.append((nm, page_url(lang, page)))
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

# ------------------------------------------------------------------ page builders
def fill_static(s, tx, lang):
    def f(m):
        key = m.group(3)
        if key not in tx: return m.group(0)
        return f'{m.group(1)}{esc(tx[key])}</{m.group(2)}>'
    return re.sub(r'(<(\w+)[^>]*\sdata-t="(\w+)"[^>]*>)</\2>', f, s)

CSS_INDEX = (".sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}"
             ".cinfo{display:flex;flex-wrap:wrap;gap:6px 26px;margin:0 0 26px;font-size:15px}.cinfo a{color:var(--ink)}.cinfo span{color:var(--mut)}"
             ".hp{position:absolute;left:-9999px;width:1px;height:1px;opacity:0}.chk a{color:var(--ink)}"
             "footer .fl{display:flex;flex-wrap:wrap;gap:4px 18px;margin-top:6px;font-size:13px}footer .fl a{color:var(--mut)}footer small{display:block;margin-top:6px}")

def build_index(lang):
    A = '' if lang == 'et' else '../'
    s = (SRC / 'index.src.html').read_text()
    s = common(s, lang, 'index', A)
    tx = node_tx(s)[lang]
    # style additions (first </style>)
    s = s.replace('</style>', CSS_INDEX + '</style>', 1)
    # H1
    s = must_rep('<section class="pin" id="lugu">', f'<h1 class="sr">{esc(K.H1[lang])}</h1>\n<section class="pin" id="lugu">', s)
    # contact block
    cinfo = (f'<div class="cinfo"><b>{C["legalName"]}</b><span><span data-t="reg"></span> {C["regCode"]}</span>'
             f'<span>KMKR {C["vat"]}</span><a href="tel:{C["phoneE164"]}">{C["phone"]}</a><a href="mailto:{C["email"]}">{C["email"]}</a></div><div class="cinfo"><span>{C["address"]}</span></div>')
    s = must_rep('<p class="lead" data-t="c_p"></p>\n<form id="cf" novalidate>', f'<p class="lead" data-t="c_p"></p>\n{cinfo}\n<form id="cf" novalidate>', s)
    s = must_rep('<label class="chk"><input type="checkbox" name="ok" required><span data-t="f_consent"></span></label>',
                 '<label class="hp" aria-hidden="true">Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label>'
                 '<label class="chk"><input type="checkbox" name="ok" required><span><span data-t="f_consent"></span> <a href="privacy.html" data-t="f_pp"></a></span></label>', s)
    s = must_rep('<div class="note" data-t="f_test"></div>', '', s)
    s = must_rep('<div class="ok" id="cok">', f'<div class="ok" id="cfail" style="background:#fee2e2;color:#7f1d1d;margin-bottom:10px"><span data-t="f_fail"></span> <a href="mailto:{C["email"]}">{C["email"]}</a></div><div class="ok" id="cok">', s)
    # footer
    foot = (f'<footer><div><span class="logo" style="gap:9px">{mark_svg("lm", "width:26px;height:26px")}<span>{C["legalName"]} · <span data-t="reg"></span> {C["regCode"]}</span></span>'
            f'<div class="fl"><span>KMKR {C["vat"]}</span><span>{C["address"]}</span><a href="tel:{C["phoneE164"]}">{C["phone"]}</a><a href="mailto:{C["email"]}">{C["email"]}</a></div></div>'
            f'<div><a href="privacy.html" data-t="lg"></a> · <a href="myygil.html" data-t="f4"></a> · <a href="kaart.html" data-t="n3"></a><small data-t="foot"></small></div></footer>')
    s = must_sub(r'<footer>.*?</footer>', lambda m: foot, s)
    # form handler
    new_form = r"""const FORM_URL=window.TK_FORM_URL||'';const T0=Date.now();
$('cf').addEventListener('submit',async e=>{e.preventDefault();const f=e.target,E=f.elements;if(E.website.value)return;
 const bad=()=>{$('cerr').style.display='block';$('cfail').style.display='none'};
 if(!E.name.value.trim()||!(E.phone.value.trim()||E.email.value.trim())||!E.ok.checked)return bad();
 if(Date.now()-T0<2500)return;
 $('cerr').style.display='none';$('cfail').style.display='none';const btn=f.querySelector('button[type=submit]'),lbl=btn.textContent;btn.disabled=true;btn.textContent=TX[LANG].f_sending;
 const data={name:E.name.value.trim(),phone:E.phone.value.trim(),email:E.email.value.trim(),addr:E.addr.value.trim(),msg:E.msg.value.trim(),lang:LANG,page:location.href};
 try{if(!FORM_URL)throw 0;const r=await fetch(FORM_URL,{method:'POST',headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify(data)});const j=await r.json();if(!j.ok)throw 0;
  $('cok').style.display='block';f.style.display='none'}catch(_){$('cfail').style.display='block';btn.disabled=false;btn.textContent=lbl}});"""
    s = must_sub(r"\$\('cf'\)\.addEventListener\('submit',e=>\{.*?e\.target\.style\.display='none'\}\);", lambda m: new_form, s)
    s = must_rep('</head>', '<script>window.TK_FORM_URL=' + json.dumps(C.get('formUrl', '')) + ';</script></head>', s)
    # static fill + caption
    s = fill_static(s, tx, lang)
    st = tx['S'][0]
    s = must_rep('<div class="k" id="ck"></div><h2 id="ch"></h2><p id="cp"></p>',
                 f'<div class="k" id="ck">{esc(st[0])}</div><h2 id="ch">{st[1]}</h2><p id="cp">{esc(st[2])}</p>', s)
    # JSON-LD
    faq = {"@type": "FAQPage", "@id": page_url(lang, 'index') + "#faq", "mainEntity": [
        {"@type": "Question", "name": tx[f'q{i}'], "acceptedAnswer": {"@type": "Answer", "text": tx[f'a{i}']}} for i in (1, 2, 3)]}
    svc = [{"@type": "Service", "name": tx[f'sv{i}h'], "description": tx[f'sv{i}p'], "serviceType": ["Real estate purchase", "Flat renovation", "Real estate sales"][i - 1],
            "provider": {"@id": BASE + "/#org"}, "areaServed": {"@type": "City", "name": "Tallinn"}} for i in (1, 2, 3)]
    ld = {"@context": "https://schema.org", "@graph": [org_node(), website_node(lang), webpage_node(lang, 'index', tx, {"breadcrumb": {"@id": page_url(lang, 'index') + "#bc"}}),
          dict(breadcrumb(lang, 'index', tx), **{"@id": page_url(lang, 'index') + "#bc"}), faq] + svc}
    s = must_rep('</head>', '</head>', s)
    s = must_sub(r'(<meta name="viewport"[^>]*>)', lambda m: m.group(1) + head_block(lang, 'index', A, ld), s, count=1)
    out = ROOT / PFX[lang] / 'index.html'
    out.parent.mkdir(exist_ok=True); out.write_text(s)

def build_myygil(lang):
    A = '' if lang == 'et' else '../'
    s = (SRC / 'myygil.src.html').read_text()
    s = common(s, lang, 'myygil', A)
    tx = node_tx(s)[lang]
    OBJ = json.loads(re.search(r'const OBJ=(\[.*?\]);\n', s, re.S).group(1))
    foot = (f'<footer><span>{C["legalName"]} · <span data-t="reg"></span> {C["regCode"]} · KMKR {C["vat"]} · {C["address"]} · <a href="tel:{C["phoneE164"]}">{C["phone"]}</a> · <a href="mailto:{C["email"]}">{C["email"]}</a></span>'
            f'<span><a href="index.html" data-t="back"></a> · <a href="kaart.html" data-t="nm4"></a> · <a href="privacy.html" data-t="pp"></a></span></footer>')
    s = must_sub(r'<footer>.*?</footer>', lambda m: foot, s)
    s = fill_static(s, tx, lang)
    items = []
    for i, o in enumerate(OBJ):
        name = o['a'].replace(', Türisalu', '')
        items.append({"@type": "ListItem", "position": i + 1, "item": {
            "@type": "Offer", "url": f"https://www.kv.ee/{o['kv']}", "price": o['pr'], "priceCurrency": "EUR",
            "availability": "https://schema.org/InStock", "seller": {"@id": BASE + "/#org"},
            "itemOffered": {"@type": "Apartment", "name": name, "numberOfRooms": o['r'],
                            "floorSize": {"@type": "QuantitativeValue", "value": o['m'], "unitCode": "MTK"},
                            "address": {"@type": "PostalAddress", "streetAddress": name, "addressLocality": ('Türisalu, Harku vald' if 'Türisalu' in o['a'] else 'Tallinn'), "addressRegion": "Harju maakond", "addressCountry": "EE"},
                            "image": f"https://img-kv.ee/image/object/46/{o['p'][0]}.jpg"}}})
    ld = {"@context": "https://schema.org", "@graph": [org_node(), website_node(lang),
          webpage_node(lang, 'myygil', tx, {"breadcrumb": {"@id": page_url(lang, 'myygil') + "#bc"}, "mainEntity": {"@id": page_url(lang, 'myygil') + "#list"}}),
          dict(breadcrumb(lang, 'myygil', tx), **{"@id": page_url(lang, 'myygil') + "#bc"}),
          {"@type": "ItemList", "@id": page_url(lang, 'myygil') + "#list", "name": tx['h'], "numberOfItems": len(items), "itemListElement": items}]}
    s = must_sub(r'(<meta name="viewport"[^>]*>)', lambda m: m.group(1) + head_block(lang, 'myygil', A, ld), s, count=1)
    out = ROOT / PFX[lang] / 'myygil.html'; out.parent.mkdir(exist_ok=True); out.write_text(s)

def build_kaart(lang):
    A = '' if lang == 'et' else '../'
    s = (SRC / 'kaart.src.html').read_text()
    s = common(s, lang, 'kaart', A)
    tx = node_tx(s)[lang]
    s = must_rep('<h1>Tark Kinnisvara</h1>', f'<h1 style="display:flex;align-items:center;gap:9px">{mark_svg("lm", "width:28px;height:28px;flex:none")}Tark Kinnisvara</h1>', s)
    s = must_rep('<a href="myygil.html" data-t="sale"></a></p>', '<a href="myygil.html" data-t="sale"></a> · <a href="privacy.html" data-t="pp"></a></p>', s)
    s = fill_static(s, tx, lang)
    ld = {"@context": "https://schema.org", "@graph": [org_node(), website_node(lang), webpage_node(lang, 'kaart', tx, {"breadcrumb": {"@id": page_url(lang, 'kaart') + "#bc"}}),
          dict(breadcrumb(lang, 'kaart', tx), **{"@id": page_url(lang, 'kaart') + "#bc"})]}
    s = must_sub(r'(<meta name="viewport"[^>]*>)', lambda m: m.group(1) + head_block(lang, 'kaart', A, ld), s, count=1)
    out = ROOT / PFX[lang] / 'kaart.html'; out.parent.mkdir(exist_ok=True); out.write_text(s)

PRIV_TPL = """<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{{--bg:#f4efe8;--ink:#1c1917;--mut:#78716c;--acc:#b45309}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 Inter,system-ui,sans-serif}}
h1,h2{{font-family:Fraunces,Georgia,serif;font-weight:400;letter-spacing:-.02em}}
nav{{position:fixed;top:0;left:0;right:0;z-index:10;display:flex;justify-content:space-between;align-items:center;gap:16px;padding:12px 28px;background:rgba(244,239,232,.92);backdrop-filter:blur(10px);border-bottom:1px solid #0001}}
.logo{{display:flex;align-items:center;gap:11px;text-decoration:none;color:var(--ink)}}.logo .lm{{width:36px;height:36px;flex:none}}.logo .lt{{display:flex;flex-direction:column;line-height:1}}.logo b{{font:600 24px/1 Fraunces,Georgia,serif;letter-spacing:-.01em}}.logo i{{font:600 9.5px/1 Inter,sans-serif;letter-spacing:.32em;margin-top:5px;font-style:normal;color:var(--acc)}}
.right{{display:flex;align-items:center;gap:14px}}.lang a{{color:var(--ink);font:600 13px Inter;opacity:.55;text-decoration:none;padding:2px 4px}}.lang a.on{{opacity:1;text-decoration:underline}}.right>a{{color:var(--ink);font-size:14px;font-weight:500}}
main{{max-width:780px;margin:0 auto;padding:110px 6vw 60px}}h1{{font-size:clamp(34px,5vw,56px);line-height:1.05;margin:0}}h2{{font-size:24px;margin:34px 0 6px}}.lead{{color:#57534e;margin:10px 0 18px}}main a{{color:var(--ink)}}
footer{{padding:30px 6vw;color:var(--mut);font-size:13px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px}}footer a{{color:var(--mut)}}
</style></head><body>
<nav><a class="logo" href="index.html" aria-label="Tark Kinnisvara">{mark}<span class="lt"><b>Tark</b><i>KINNISVARA</i></span></a><div class="right"><span class="lang" aria-label="Language">{sw}</span><a href="index.html">{back}</a></div></nav>
<main>{body}</main>
<footer><span>{legal} · {regl} {reg}</span><span><a href="index.html">{back}</a></span></footer></body></html>"""

def build_privacy(lang):
    A = '' if lang == 'et' else '../'
    sw = ''.join(f'<a href="{rel_to(lang, l, "privacy")}" hreflang="{l}" lang="{l}" data-l="{l}"{" class=\"on\" aria-current=\"true\"" if l == lang else ""}>{LABEL[l]}</a>' for l in LANGS)
    body = K.privacy_html(lang, C, ADDR_LINE)
    page = PRIV_TPL.format(lang=lang, mark=mark_svg('lm'), sw=sw, back=K.PRIVACY_BACK[lang], body=body, legal=C['legalName'],
                           regl={'et': 'Reg. nr', 'ru': 'Рег. номер', 'en': 'Reg. no.'}[lang], reg=C['regCode'])
    tx = {'h': K.META['privacy'][lang][0]}
    ld = {"@context": "https://schema.org", "@graph": [org_node(), website_node(lang),
          webpage_node(lang, 'privacy', tx, {"breadcrumb": {"@id": page_url(lang, 'privacy') + "#bc"}}),
          dict(breadcrumb(lang, 'privacy', tx), **{"@id": page_url(lang, 'privacy') + "#bc"})]}
    page = must_sub(r'(<meta name="viewport"[^>]*>)', lambda m: m.group(1) + head_block(lang, 'privacy', A, ld), page, count=1)
    out = ROOT / PFX[lang] / 'privacy.html'; out.parent.mkdir(exist_ok=True); out.write_text(page)

# ------------------------------------------------------------------ static files
def write_static():
    (ROOT / 'assets/icons').mkdir(parents=True, exist_ok=True)
    (ROOT / 'assets/icons/favicon.svg').write_text(standalone())
    (ROOT / 'robots.txt').write_text(f"""User-agent: *
Allow: /

# AI / answer-engine crawlers are welcome
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Claude-SearchBot
Allow: /
User-agent: Claude-User
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Applebot-Extended
Allow: /
User-agent: Bingbot
Allow: /

Sitemap: {BASE}/sitemap.xml
""")
    urls = []
    for page in FILES:
        for lang in LANGS:
            alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{page_url(l, page)}"/>' for l in LANGS)
            alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{page_url("et", page)}"/>'
            pr = {'index': '1.0', 'myygil': '0.9', 'kaart': '0.6', 'privacy': '0.2'}[page]
            urls.append(f'<url><loc>{page_url(lang, page)}</loc><lastmod>{C["modified"]}</lastmod><priority>{pr}</priority>{alts}</url>')
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(urls) + '\n</urlset>\n')
    (ROOT / 'llms.txt').write_text(K.LLMS.format(base=BASE, reg=C['regCode'], mail=C['email'], tel=C['phone']))
    (ROOT / 'manifest.webmanifest').write_text(json.dumps({
        "name": "Tark Kinnisvara", "short_name": "Tark", "start_url": "./", "display": "browser", "background_color": "#f4efe8", "theme_color": "#f4efe8",
        "icons": [{"src": "assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=1))
    t, d, b = K.NOTFOUND['et'], K.NOTFOUND['ru'], K.NOTFOUND['en']
    (ROOT / '404.html').write_text(f"""<!doctype html><html lang="et"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>404 — Tark Kinnisvara</title><style>body{{margin:0;background:#f4efe8;color:#1c1917;font:16px/1.6 system-ui,sans-serif;display:grid;place-items:center;min-height:100vh;text-align:center;padding:24px}}h1{{font:400 44px Georgia,serif;margin:0 0 8px}}a{{color:#b45309;font-weight:600}}p{{margin:6px 0}}</style></head>
<body><div>{mark_svg('lm', 'width:64px;height:64px', True)}<h1>404</h1><p>{t[0]} · {d[0]} · {b[0]}</p><p><a href="{BASE}/">{t[2]}</a> · <a href="{BASE}/ru/">{d[2]}</a> · <a href="{BASE}/en/">{b[2]}</a></p></div></body></html>""")

if __name__ == '__main__':
    write_static()
    for l in LANGS:
        build_index(l); build_myygil(l); build_kaart(l); build_privacy(l)
    print('built', [str(p.relative_to(ROOT)) for p in sorted(ROOT.glob('**/*.html')) if 'src' not in p.parts and 'node_modules' not in p.parts])
