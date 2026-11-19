#!/usr/bin/env python3
"""Syncs tools/sale.json with the company's KV.EE XML feed (RBO -> Firma -> «Kuulutuste väljund XML»).

The feed URL contains an access key, so it is NOT stored in the repository: it is read from the
environment variable KV_FEED_URL (GitHub Actions secret). Exits with 0 when nothing changed,
writes tools/sale.json and prints CHANGED when the list changed, exits non-zero on any problem
(the previous sale.json is kept untouched in that case).
"""
import json, os, pathlib, re, sys, datetime, urllib.request, xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
SALE = ROOT / 'tools/sale.json'
RULES = json.load(open(ROOT / 'tools/sale_rules.json', encoding='utf-8'))
COMPANY_ID = '12681'


def fetch(src):
    if src.startswith(('http://', 'https://')):
        req = urllib.request.Request(src, headers={'User-Agent': 'tarkkinnisvara.ee-sync/1.0'})
        with urllib.request.urlopen(req, timeout=60) as r:
            if r.status != 200:
                raise SystemExit(f'feed HTTP {r.status}')
            return r.read()
    return open(src, 'rb').read()


def txt(o, path):
    e = o.find(path)
    return (e.text or '').strip() if e is not None else ''


def num(s, default=None):
    try:
        return float(s)
    except (TypeError, ValueError):
        return default


def parse(xml_bytes):
    root = ET.fromstring(xml_bytes)
    cid = txt(root, 'company/company_info/id')
    if cid != COMPANY_ID:
        raise SystemExit(f'unexpected company id in feed: {cid!r}')
    items = []
    for o in root.findall('objects/object'):
        if txt(o, 'deal_type') != 'sell':
            continue
        oid = int(txt(o, 'id'))
        street, nr = txt(o, 'location/street'), txt(o, 'location/house_nr')
        city, part = txt(o, 'location/city'), txt(o, 'location/city_part')
        tallinn = city == 'Tallinn'
        addr = f'{street} {nr}'.strip()
        if not tallinn and part:
            addr += f', {part}'           # apartment numbers are never published
        price, area = num(txt(o, 'price')), num(txt(o, 'area'))
        m = re.match(r'\(\s*([\d.\-]+)\s*,\s*([\d.\-]+)\s*\)', txt(o, 'coordinate'))
        if not (price and area and m):
            print(f'skip {oid} {addr}: no price/area/coordinates', file=sys.stderr)
            continue
        fl = None
        tf, nf = txt(o, 'this_floor'), txt(o, 'num_floors')
        if tf.isdigit() and nf.isdigit():
            fl = [int(tf), int(nf)]
        photos = []
        for u in (e.text or '' for e in o.findall('images/image/imageURI')):
            mm = re.search(r'/object/\d+/(\d+/\d+)\.jpg', u)
            if mm:
                photos.append(mm.group(1))
        it = {
            'id': oid, 'a': addr, 'd': part if tallinn else f'{part} ({city})',
            'r': int(num(txt(o, 'room_count'), 0) or 0), 'm': round(area, 1) if area % 1 else int(area),
            'pr': int(price), 'yr': int(num(txt(o, 'year_built'), 0) or 0) or None,
            'posted': txt(o, 'date_created')[:10], 'mod': txt(o, 'date_modified')[:10],
            'lat': float(m.group(1)), 'lon': float(m.group(2)), 'p': photos,
        }
        if fl:
            it['fl'] = fl
        if not tallinn:
            it['loc'] = f'{part}, {city}'
        otype = txt(o, 'object_type')
        if otype == 'house':
            it['type'] = 'suvila' if txt(o, 'building_type') == 'summerhouse' else 'maja'
        it.update(RULES.get('overrides', {}).get(str(oid), {}))
        items.append(it)
    return items


def apply_rules(items):
    out = []
    for it in items:
        if it['id'] in RULES.get('exclude_ids', []):
            continue
        if any(it['a'].startswith(p) for p in RULES.get('exclude_addr_prefix', [])):
            continue
        out.append(it)
    # duplicates (same address): keep the preferred id, otherwise the most recently modified one
    by = {}
    for it in out:
        by.setdefault(it['a'], []).append(it)
    keep = []
    for a, group in by.items():
        pref = RULES.get('prefer_ids', {}).get(a)
        chosen = next((g for g in group if g['id'] == pref), None) or max(group, key=lambda g: g['mod'])
        if len(group) > 1:
            print(f'duplicate {a}: ids {[g["id"] for g in group]} -> keeping {chosen["id"]}', file=sys.stderr)
        keep.append(chosen)
    # stable order: previous order first (so the list does not jump around), new listings go to the top
    prev = json.load(open(SALE, encoding='utf-8')) if SALE.exists() else {'items': []}
    order = {x['id']: i for i, x in enumerate(prev['items'])}
    keep.sort(key=lambda g: (g['id'] in order, order.get(g['id'], 0) if g['id'] in order else -int(g['id'])))
    for g in keep:
        g.pop('mod', None)
    return keep, prev


def main():
    src = os.environ.get('KV_FEED_URL') or (sys.argv[1] if len(sys.argv) > 1 else '')
    if not src:
        raise SystemExit('KV_FEED_URL is not set')
    items, prev = apply_rules(parse(fetch(src)))
    old = [x for x in prev['items'] if not x.get('hide')]
    if len(old) >= 3 and len(items) < len(old) * 0.4 and '--force' not in sys.argv:
        raise SystemExit(f'refusing to publish {len(items)} listings after {len(old)} (feed looks broken); use --force')
    cur = [{k: v for k, v in x.items() if k not in ('hide', 'mo')} for x in old]
    if cur == items and prev.get('remove_addr') == RULES.get('remove_addr') and prev.get('sold_extra') == RULES.get('sold_extra'):
        print('no changes')
        return
    new_ids, gone = {x['id'] for x in items}, {x['id']: x['a'] for x in old}
    for x in items:
        if x['id'] not in gone:
            print('+ added', x['id'], x['a'], x['pr'])
    for i, a in gone.items():
        if i not in new_ids:
            print('- removed', i, a)
    data = {'updated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d'),
            'source': 'KV.EE XML feed (RBO)', 'items': items,
            'remove_addr': RULES.get('remove_addr', []), 'sold_extra': RULES.get('sold_extra', [])}
    SALE.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('CHANGED')


if __name__ == '__main__':
    main()
