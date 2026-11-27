#!/usr/bin/env python3
"""Pulls newly sold flats from the company's project table ("PROJEKTID TÖÖS ÕIGE") into tools/sheet_sold.json.

The table itself stays private. A small Google Apps Script bound to it (tools/apps_script/SheetFeed.gs) publishes only
the rows whose status is «Müüdud»: address, status, sale date, area, rooms - the same facts the site already shows.
Feed URL: env SHEET_FEED_URL, argument 1 (URL or local JSON file), or `sheetFeed` in tools/company.json.

How it works
  * `seen`   - every sold flat the site already accounts for (baseline); a flat that becomes «Müüdud» and is not in
               `seen` is a new sale -> an entry in `events`, which build.py turns into a «Müüdud» point and uses to
               hide a matching KV.EE listing (same house + same area).
  * `events` - kept while the flat stays «Müüdud» in the table; if somebody changes the status back, the event goes.
Exit codes: 0 ok (prints CHANGED when the file was rewritten), non-zero on a broken feed (file untouched).
"""
import json, os, pathlib, re, sys, datetime, urllib.request, urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from addr import hkey, flat_key

ROOT = pathlib.Path(__file__).resolve().parent.parent
F = ROOT / 'tools/sheet_sold.json'
MIN_SOLD = 100  # the table has 126 sold flats; fewer means the feed is broken


def load_feed(src):
    if src.startswith(('http://', 'https://')):
        req = urllib.request.Request(src, headers={'User-Agent': 'tarkkinnisvara.ee-sync/1.0'})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
    else:
        raw = open(src, 'rb').read()
    d = json.loads(raw)
    if not d.get('ok', True):
        raise SystemExit(f'feed error: {d.get("error")}')
    return d['rows']


def month(sd):
    m = re.match(r'(\d+)\.(\d+)\.(\d{4})', (sd or '').strip())
    return f'{m.group(3)}-{int(m.group(2)):02d}' if m else None


def num(x):
    try:
        return float(str(x).replace(' ', '').replace(',', '.'))
    except ValueError:
        return None


def geocode(a):
    """Best effort: Maa-amet In-ADS (free, no key). Returns (lat, lon, district) or None."""
    try:
        q = urllib.parse.quote(a.split(',')[0] + ', Tallinn')
        with urllib.request.urlopen(f'https://inaadress.maaamet.ee/inaadress/gazetteer?address={q}&results=1', timeout=20) as r:
            j = json.loads(r.read())
        x = j['addresses'][0]
        return float(x['viitepunkt_b']), float(x['viitepunkt_l']), x.get('asustusyksus')
    except Exception:
        return None


def main():
    src = os.environ.get('SHEET_FEED_URL') or (sys.argv[1] if len(sys.argv) > 1 else '')
    if not src:
        src = json.load(open(ROOT / 'tools/company.json')).get('sheetFeed', '')
    if not src:
        raise SystemExit('SHEET_FEED_URL is not set')
    rows = [r for r in load_feed(src) if r.get('st') == 'Müüdud']
    if len(rows) < MIN_SOLD and '--force' not in sys.argv:
        raise SystemExit(f'feed has only {len(rows)} sold rows (expected >= {MIN_SOLD}); refusing')
    cur = {flat_key(r['a']): r for r in rows}
    old = json.load(open(F, encoding='utf-8')) if F.exists() else {'seen': [], 'events': []}
    seen, events = set(old['seen']), [e for e in old['events'] if e['k'] in cur]
    have = {e['k'] for e in events}
    new = []
    for k, r in cur.items():
        if k in seen or k in have:
            continue
        e = {'k': k, 'a': r['a'], 'sd': month(r.get('sd')), 'm': num(r.get('m')), 'rooms': r.get('r') or None}
        g = geocode(r['a'])
        if g:
            e.update(lat=g[0], lon=g[1], d=g[2])
        events.append(e)
        new.append(e)
        print('+ sold', r['a'], r.get('sd'))
    gone = [e['a'] for e in old['events'] if e['k'] not in cur]
    for a in gone:
        print('- no longer sold', a)
    data = {'updated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d'),
            'seen': sorted(seen | set(cur)), 'events': sorted(events, key=lambda e: e['k'])}
    if data['seen'] == old['seen'] and data['events'] == old['events']:
        print('no changes')
        return
    F.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('CHANGED')


if __name__ == '__main__':
    main()
