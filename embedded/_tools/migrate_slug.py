# -*- coding: utf-8 -*-
"""Slug-only міграція embedded (фаза B).

Перейменовує теки розділів і файли на slug-only схему, переносить шляхи в
manifest.js / _status.md / PLAN.md на slug-only (номери М.Р.Т лишаються там же)
і лагодить ІМЕНА у всіх крос-.md-лінках. Фігури в img/ не чіпає; figs-*.py
перейменовує синхронно з вставками (figs.py лишається). ch01.html (єдиний
артефакт) їде разом зі своєю текою.

  chNN-slug / rNN-slug      ->  slug
  chNN-slug.md (головний)   ->  slug.md
  chNN-sK-history-X / chNN-history-X ->  hist-X.md
  chNN-sK-c-X ->  comp-X.md ;  -m- ->  math-X.md ;  -a- ->  proj-X.md

Перейменування файлів — лише наявних на диску (disk-map). Текст (лінки,
manifest/PLAN/_status) переписується ЗА ПАТЕРНОМ chNN/rNN, тож запланіровані
(ще не написані) теки/вставки теж стають slug-only.

  python embedded/_tools/migrate_slug.py            # DRY-RUN (нічого не змінює)
  python embedded/_tools/migrate_slug.py --apply    # виконати міграцію
"""
import io, os, re, sys, posixpath, subprocess

ROOT = r"E:\develop\courses\embedded"
REPO = r"E:\develop\courses"
MANIFEST = r"E:\develop\courses\manifest.js"
PLAN = os.path.join(ROOT, "PLAN.md")
APPLY = "--apply" in sys.argv

def move(src, dst):
    """git mv (зберігає перейменування в індексі); fallback на os.rename для нетрекнутих файлів."""
    try:
        r = subprocess.run(["git", "mv", "-f", src, dst], cwd=REPO,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.returncode == 0:
            return
    except Exception:
        pass
    os.rename(src, dst)

CHAP_RE = re.compile(r'^(ch|r)\d+-')
def strip_chap(b): return CHAP_RE.sub('', b)

def new_md(fn, folder):
    """нове ім'я .md за старим ім'ям і текою-власником (folder може бути None)."""
    if not fn.endswith('.md'):
        return None
    b = fn[:-3]
    if folder is not None and b == folder:
        return strip_chap(folder) + '.md'                 # головний файл розділу
    core = re.sub(r'^s\d+-', '', strip_chap(b))
    if core.startswith('history-'): return 'hist-' + core[len('history-'):] + '.md'
    if core == 'history':           return 'hist-' + (strip_chap(folder) if folder else 'overview') + '.md'
    if core.startswith('c-'):       return 'comp-' + core[2:] + '.md'
    if core.startswith('m-'):       return 'math-' + core[2:] + '.md'
    if core.startswith('a-'):       return 'proj-' + core[2:] + '.md'
    if CHAP_RE.match(b):            return strip_chap(b) + '.md'   # chNN-X.md без маркерів = головний файл
    return None                                            # не класифікується

def new_seg_path(tok, default_owner=None):
    """переписати шлях-токен за патерном; default_owner — тека файла (для same-dir)."""
    segs = tok.split('/')
    owner = None
    out = []
    n = len(segs)
    for i, s in enumerate(segs):
        if i == n - 1 and s.endswith('.md'):
            nm = new_md(s, owner if owner else default_owner)
            out.append(nm if nm else s)
        elif i == n - 1 and CHAP_RE.match(s):                 # хвостовий токен без .md (напр. згадка вставки в прозі)
            nm = new_md(s + '.md', owner if owner else default_owner)
            out.append(nm[:-3] if nm else strip_chap(s))
        else:
            if CHAP_RE.match(s):
                owner = s
                out.append(strip_chap(s))
            else:
                out.append(s)
    return '/'.join(out)

def new_figs(fn, folder):
    if fn == 'figs.py':
        return None
    m = re.match(r'^figs-(.+)\.py$', fn)
    if not m:
        return None
    nm = new_md(m.group(1) + '.md', folder)
    return ('figs-' + nm[:-3] + '.py') if nm else None

# ── disk-карти для фактичних перейменувань (лише наявні файли) ──
FOLDER = {}                 # oldfolder -> slug
FILE = {}                   # oldfilename.md -> newfilename.md
FIGS = {}                   # (folderpath, oldpy) -> newpy
md_oldpaths = []            # (block, folder, fn)
problems = []

for block in sorted(os.listdir(ROOT)):
    bp = os.path.join(ROOT, block)
    if not os.path.isdir(bp) or not (block.startswith('block-') or block == 'bridges'):
        continue
    for folder in sorted(os.listdir(bp)):
        fp = os.path.join(bp, folder)
        if not os.path.isdir(fp) or not CHAP_RE.match(folder):
            continue
        FOLDER[folder] = strip_chap(folder)
        for fn in sorted(os.listdir(fp)):
            if os.path.isdir(os.path.join(fp, fn)):
                continue
            if fn.endswith('.md'):
                nm = new_md(fn, folder)
                if nm is None:
                    problems.append('UNKNOWN md %s/%s/%s' % (block, folder, fn))
                    continue
                FILE[fn] = nm
                md_oldpaths.append((block, folder, fn))
            elif re.match(r'^figs-.*\.py$', fn):
                nf = new_figs(fn, folder)
                if nf:
                    FIGS[(fp, fn)] = nf

# ── переписування тексту (за патерном) ──
LINK_RE = re.compile(r'(\]\()([^)]+?)(\))')
def rewrite_links(text, cur_folder):
    n = [0]
    def repl(m):
        target = m.group(2).strip()
        hi = target.find('#')
        core, frag = (target[:hi], target[hi:]) if hi >= 0 else (target, '')
        if core.startswith('http') or core.startswith('book:') or not core.endswith('.md'):
            return m.group(0)
        nt = new_seg_path(core, default_owner=cur_folder)
        if nt != core:
            n[0] += 1
        return m.group(1) + nt + frag + m.group(3)
    return LINK_RE.sub(repl, text), n[0]

def rewrite_struct(text, quote):
    """переписати path-токени всередині лапок/беків (manifest -> ", PLAN/_status -> `)."""
    cnt = [0]
    pat = re.compile(re.escape(quote) + r'([\w./-]+)' + re.escape(quote))
    def repl(m):
        s = m.group(1)
        if s.endswith('.md') or '/' in s or CHAP_RE.match(s):
            ns = new_seg_path(s)
            if ns != s:
                cnt[0] += 1
            return quote + ns + quote
        return m.group(0)
    return pat.sub(repl, text), cnt[0]

# ── проєкція нового розкладу (для звіту про залишкові биті лінки) ──
NEW_FILES = set('/'.join([b, FOLDER[f], FILE[fn]]) for (b, f, fn) in md_oldpaths)
def project_broken():
    broken = []
    for (b, f, fn) in md_oldpaths:
        nrel = '/'.join([b, FOLDER[f], FILE[fn]])
        try:
            txt = io.open(os.path.join(ROOT, b, f, fn), encoding='utf-8').read()
        except Exception:
            continue
        base = posixpath.dirname(nrel)
        for m in LINK_RE.finditer(txt):
            tgt = m.group(2).strip()
            hi = tgt.find('#')
            core = tgt[:hi] if hi >= 0 else tgt
            if core.startswith('http') or core.startswith('book:') or not core.endswith('.md'):
                continue
            nt = new_seg_path(core, default_owner=f)
            res = posixpath.normpath(posixpath.join(base, nt))
            if res not in NEW_FILES:
                broken.append('%s  ->  %s' % (nrel, tgt))
    return broken

def status_files():
    out = []
    for block in sorted(os.listdir(ROOT)):
        st = os.path.join(ROOT, block, '_status.md')
        if os.path.isfile(st):
            out.append(st)
    return out

# ── DRY-RUN ──
def report():
    print("=== RENAME MAPS ===")
    print("  folders:", len(FOLDER), "| md files:", len(FILE), "| figs-*.py:", len(FIGS), "| problems:", len(problems))
    for p in problems[:20]:
        print("   !", p)
    print("\n=== SAMPLE FILE RENAMES ===")
    for k in list(FILE)[:10]:
        print("  %-40s -> %s" % (k, FILE[k]))

    files_changed = total = 0
    for (b, f, fn) in md_oldpaths:
        _, n = rewrite_links(io.open(os.path.join(ROOT, b, f, fn), encoding='utf-8').read(), f)
        if n:
            files_changed += 1; total += n
    print("\n=== CONTENT LINK REWRITES ===")
    print("  .md files changed:", files_changed, "| link targets rewritten:", total)

    _, mc = rewrite_struct(io.open(MANIFEST, encoding='utf-8').read(), '"')
    _, pc = rewrite_struct(io.open(PLAN, encoding='utf-8').read(), '`')
    sc = 0
    for st in status_files():
        _, c = rewrite_struct(io.open(st, encoding='utf-8').read(), '`')
        sc += c
    print("\n=== STRUCTURED FILES ===")
    print("  manifest.js tokens:", mc, "| PLAN.md tokens:", pc, "| _status.md tokens:", sc)

    broken = project_broken()
    print("\n=== POST-MIGRATION UNRESOLVED .md LINKS (for Phase E) (%d) ===" % len(broken))
    for x in broken:
        print("  ", x)
    print("\nDRY-RUN only. Re-run with --apply to perform the migration.")

def apply():
    for (b, f, fn) in md_oldpaths:                         # 1) лінки в контенті
        p = os.path.join(ROOT, b, f, fn)
        out, n = rewrite_links(io.open(p, encoding='utf-8').read(), f)
        if n:
            io.open(p, 'w', encoding='utf-8', newline='').write(out)
    man, _ = rewrite_struct(io.open(MANIFEST, encoding='utf-8').read(), '"')   # 2) структурні
    io.open(MANIFEST, 'w', encoding='utf-8', newline='').write(man)
    plan, _ = rewrite_struct(io.open(PLAN, encoding='utf-8').read(), '`')
    io.open(PLAN, 'w', encoding='utf-8', newline='').write(plan)
    for st in status_files():
        t, _ = rewrite_struct(io.open(st, encoding='utf-8').read(), '`')
        io.open(st, 'w', encoding='utf-8', newline='').write(t)
    for block in sorted(os.listdir(ROOT)):                 # 3) перейменувати файли
        bp = os.path.join(ROOT, block)
        if not os.path.isdir(bp):
            continue
        for folder in sorted(os.listdir(bp)):
            fp = os.path.join(bp, folder)
            if not os.path.isdir(fp) or folder not in FOLDER:
                continue
            for fn in sorted(os.listdir(fp)):
                if fn.endswith('.md') and fn in FILE and FILE[fn] != fn:
                    move(os.path.join(fp, fn), os.path.join(fp, FILE[fn]))
                elif (fp, fn) in FIGS:
                    move(os.path.join(fp, fn), os.path.join(fp, FIGS[(fp, fn)]))
    for block in sorted(os.listdir(ROOT)):                 # 4) перейменувати теки
        bp = os.path.join(ROOT, block)
        if not os.path.isdir(bp):
            continue
        for folder in sorted(os.listdir(bp)):
            if folder in FOLDER and FOLDER[folder] != folder:
                move(os.path.join(bp, folder), os.path.join(bp, FOLDER[folder]))
    print("APPLIED: %d folders, %d files, %d figs renamed; structured + content rewritten." %
          (len(FOLDER), len(FILE), len(FIGS)))

if __name__ == '__main__':
    apply() if APPLY else report()
