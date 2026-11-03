"""Rebuild bunnynote-site/fonts/material-symbols-subset.woff2.

Run this after adding a new Material Symbols icon name to index.html:
    pip install fonttools brotli
    python tools/subset-icons.py

It reads every icon name inside class="material-symbols-outlined" elements,
downloads the full weight-400 Outlined font (keeps the FILL axis), and writes
a tiny font that contains only those icons.
"""
import io, re, sys, urllib.request
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools import subset

SRC = 'https://cdn.jsdelivr.net/npm/@material-symbols/font-400@0.48.2/material-symbols-outlined.woff2'
site = Path(__file__).resolve().parent.parent / 'bunnynote-site'
html = (site / 'index.html').read_text(encoding='utf-8')
names = sorted(set(re.findall(r'material-symbols-outlined[^>]*>\s*([a-z0-9_]+)\s*<', html)))
print('icons:', ' '.join(names))

font = TTFont(io.BytesIO(urllib.request.urlopen(SRC).read()))
rev = {g: chr(c) for c, g in font.getBestCmap().items()}
want = {}
for lookup in font['GSUB'].table.LookupList.Lookup:
    for st in lookup.SubTable:
        st = getattr(st, 'ExtSubTable', st)
        for first, ligs in getattr(st, 'ligatures', {}).items():
            for lig in ligs:
                word = ''.join(rev.get(g, '?') for g in [first] + lig.Component)
                if word in names:
                    want[word] = lig.LigGlyph
missing = set(names) - set(want)
if missing:
    sys.exit(f'not in Material Symbols: {missing}')

opts = subset.Options()
opts.layout_features = ['liga', 'rlig', 'rclt', 'calt']
opts.layout_closure = False  # keep only the ligatures we asked for
opts.flavor = 'woff2'
opts.notdef_outline = True
sub = subset.Subsetter(opts)
sub.populate(text=''.join(sorted(set(''.join(names)))), glyphs=list(want.values()))
sub.subset(font)
out = site / 'fonts' / 'material-symbols-subset.woff2'
font.flavor = 'woff2'
font.save(out)
print(f'wrote {out} ({out.stat().st_size} bytes, {len(names)} icons)')
