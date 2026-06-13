# -*- coding: utf-8 -*-
"""Регенерувати manifest.js з PLAN.md (порядок/назви/шляхи) + диск (що написано → done, історії, extras)."""
import io, os, re

ROOT = r"E:\develop\courses\embedded"
MAN = r"E:\develop\courses\manifest.js"

plan = io.open(os.path.join(ROOT, "PLAN.md"), encoding="utf-8").read()
plan = plan.split("## Мости")[0]  # без мостів

# модулі й розділи з PLAN
mods = {}   # n -> {title, slug, chapters:[(R,title,dir,main)]}
order = []
cur = None
for ln in plan.split("\n"):
    mm = re.match(r"^## Модуль (\d+) — (.+)$", ln)
    if mm:
        cur = int(mm.group(1)); mods[cur] = {"title": mm.group(2).strip(), "slug": None, "chapters": []}
        order.append(cur); continue
    cm = re.match(r"^### Розділ (\d+)\.(\d+) — (.+?) · `([^`]+)`\s*$", ln)
    if cm and cur is not None:
        R = int(cm.group(2)); title = cm.group(3).strip(); path = cm.group(4)
        parts = path.split("/")
        slug = parts[0]; main = parts[-1]; d = "/".join(parts[:-1])
        if mods[cur]["slug"] is None: mods[cur]["slug"] = slug
        mods[cur]["chapters"].append((R, title, d, main))

def status_order(block):
    """rank базових імен вставок за порядком появи в _status.md блоку (порядок читання).
    Після slug-міграції імена не містять -sNN-, тож порядок беремо з _status.md."""
    p = os.path.join(ROOT, block, "_status.md")
    if not os.path.isfile(p): return {}
    txt = io.open(p, encoding="utf-8").read()
    rank = {}
    for i, m in enumerate(re.finditer(r"`([^`]+\.md)`", txt)):
        rank.setdefault(m.group(1).split("/")[-1], i)
    return rank

def scan(d):
    """повертає (histories[], extras[]) у порядку читання (slug-схема: hist-/comp-/math-/proj-)."""
    full = os.path.join(ROOT, d.replace("/", os.sep))
    if not os.path.isdir(full): return [], []
    files = [f for f in os.listdir(full) if f.endswith(".md")]
    rank = status_order(d.split("/")[0])
    keyf = lambda f: (rank.get(f, 10**6), f)
    hist = sorted([f for f in files if f.startswith("hist-")], key=keyf)
    extra = sorted([f for f in files if re.match(r"^(comp|math|proj)-", f)], key=keyf)
    return hist, extra

def jstr(s): return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

modblocks = []
done_count = 0; pend_count = 0
for n in order:
    m = mods[n]
    rows = []
    for (R, title, d, main) in m["chapters"]:
        mainpath = os.path.join(r"E:\develop\courses\embedded", d.replace("/", os.sep), main)
        if os.path.isfile(mainpath):
            done_count += 1
            hist, extra = scan(d)
            ce = "        { n: %d, status: \"done\", title: %s,\n" % (R, jstr(title))
            ce += "          dir: %s, main: %s,\n" % (jstr(d), jstr(main))
            ce += "          histories: [%s]" % (", ".join(jstr(h) for h in hist))
            if extra:
                ce += ",\n          extras: [%s]" % (", ".join(jstr(e) for e in extra))
            ce += " }"
            rows.append(ce)
        else:
            pend_count += 1
            rows.append("        { n: %d, status: \"pending\", title: %s }" % (R, jstr(title)))
    block = ("    {\n      n: %d,\n      title: %s,\n      slug: %s,\n      chapters: [\n%s\n      ]\n    }"
             % (n, jstr(m["title"]), jstr(m["slug"]), ",\n".join(rows)))
    modblocks.append(block)

prelude = io.open(MAN, encoding="utf-8").read()
pre = prelude[:prelude.index("modules:")]
js = pre + "modules: [\n" + ",\n".join(modblocks) + "\n  ]\n};\n"
io.open(MAN, "w", encoding="utf-8", newline="").write(js)
print("manifest.js регенеровано. Розділів done:", done_count, "; pending:", pend_count)
