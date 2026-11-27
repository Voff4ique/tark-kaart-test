# -*- coding: utf-8 -*-
"""Address helpers shared by build.py and sync_sheet.py.

hkey()  -> (street, house) key, so 'Võru 16-141', 'Võru tn 16' and 'Voru tee 16, Tallinn' are the same house.
flat()  -> flat part of a spreadsheet address ('Võru 16-141' -> '141'), '' if none.
"""
import re

_TR = str.maketrans({'õ': 'o', 'ä': 'a', 'ö': 'o', 'ü': 'u', 'š': 's', 'ž': 'z'})
_STOP = {'tn', 'tee', 'mnt', 'pst', 'puiestee', 'pk', 'tanav'}


def _tokens(addr):
    a = (addr or '').lower().translate(_TR).split(',')[0]
    return [t for t in re.findall(r'[a-z]+|\d+[a-z]?', a) if t not in _STOP]


def hkey(addr):
    t = _tokens(addr)
    for i, x in enumerate(t):
        if x[0].isdigit():
            street = next((y for y in reversed(t[:i]) if y[0].isalpha()), '')
            return (street, x)
    return (t[-1] if t else '', '')


def flat(addr):
    t = _tokens(addr)
    for i, x in enumerate(t):
        if x[0].isdigit():
            return '-'.join(t[i + 1:])
    return ''


def flat_key(addr):
    h = hkey(addr)
    return f'{h[0]}-{h[1]}-{flat(addr)}'
