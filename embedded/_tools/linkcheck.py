# -*- coding: utf-8 -*-
"""linkcheck — кожне посилання має ціль або стаб «в розробці», інакше exit 1.

Перевіряє в усіх .md книги embedded:
  • локальні .md-лінки  ](path.md)  — файл-ціль мусить існувати;
  • крос-книжкові book:<id>/<slug>… — id мусить бути відомою книгою
    (рушій сам показує стаб «в розробці», якщо тема ще не написана);
  • зображення ](path.svg/png) — файл мусить існувати.
Друкує всі нерозв'язані лінки згруповано й завершується кодом 1, якщо такі є.

Запуск:  python embedded/_tools/linkcheck.py
"""
import io, os, re, sys, posixpath

ROOT = r"E:\develop\courses\embedded"
KNOWN_BOOKS = {"electronics", "chem", "math", "components"}
LINK_RE = re.compile(r'\]\(([^)]+?)\)')

missing_md = []
bad_book = []
missing_img = []
queued_md = []
checked = 0

# базові імена вставок/тем, що стоять у чергах _status.md — це легітимний стаб «в розробці»
QUEUED = set()
for dp, dn, fns in os.walk(ROOT):
    if '_status.md' in fns:
        try:
            t = io.open(os.path.join(dp, '_status.md'), encoding='utf-8').read()
        except Exception:
            t = ''
        for m in re.finditer(r'`([^`]+\.md)`', t):
            QUEUED.add(m.group(1).split('/')[-1])

for dp, dn, fns in os.walk(ROOT):
    for fn in fns:
        if not fn.endswith('.md'):
            continue
        full = os.path.join(dp, fn)
        rel = os.path.relpath(full, ROOT).replace('\\', '/')
        try:
            txt = io.open(full, encoding='utf-8').read()
        except Exception:
            continue
        base = posixpath.dirname(rel)
        for m in LINK_RE.finditer(txt):
            href = m.group(1).strip()
            if href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                continue
            if '<' in href or '>' in href or '...' in href:   # шаблон-приклад у документації, не лінк
                continue
            hi = href.find('#')
            core = href[:hi] if hi >= 0 else href
            if core.startswith('book:'):
                checked += 1
                bid = core[len('book:'):].split('/', 1)[0]
                if bid not in KNOWN_BOOKS:
                    bad_book.append('%s  ->  %s' % (rel, href))
                continue
            if core.startswith('http://') or core.startswith('https://') or not core:
                continue
            if core.endswith('.md'):
                checked += 1
                tgt = posixpath.normpath(posixpath.join(base, core))
                if not os.path.isfile(os.path.join(ROOT, tgt.replace('/', os.sep))):
                    if posixpath.basename(core) in QUEUED:
                        queued_md.append('%s  ->  %s' % (rel, href))   # ціль у черзі _status.md
                    else:
                        missing_md.append('%s  ->  %s' % (rel, href))
            elif re.search(r'\.(svg|png|jpg|jpeg|gif|webp)$', core, re.I):
                checked += 1
                tgt = posixpath.normpath(posixpath.join(base, core))
                if not os.path.isfile(os.path.join(ROOT, tgt.replace('/', os.sep))):
                    missing_img.append('%s  ->  %s' % (rel, href))

def dump(title, items):
    print("\n=== %s (%d) ===" % (title, len(items)))
    for x in items:
        print("  ", x)

print("linkcheck: перевірено посилань:", checked)
dump("MISSING .md TARGETS (потрібен стаб або правка)", missing_md)
dump("UNKNOWN book: id", bad_book)
dump("MISSING IMAGE TARGETS", missing_img)
if queued_md:
    print("\n=== У ЧЕРЗІ — ціль ще не написана, але стоїть у _status.md (OK) (%d) ===" % len(queued_md))
    for x in queued_md:
        print("  ", x)

fail = len(missing_md) + len(bad_book) + len(missing_img)
if fail:
    print("\nFAIL:", fail, "нерозв'язаних посилань.")
    sys.exit(1)
print("\nOK: усі посилання мають ціль або стаб.")
