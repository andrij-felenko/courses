# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

NEWFILL = "#eafaf0"   # новий вузол / копія (зелене)
OLDFILL = "#eef2f6"   # старий/спільний блок (сіре)
BLKFILL = "#eef4ff"   # активний блок (синювате)


# ── cow-share: троє ділять блок, один пише й відколюється ─────────────────────
# Ідея: ліворуч p,q,r указують на один блок (refs=3), жодного копіювання;
# праворуч q пише — refs>1, тож q відколює власну копію, а p,r бачать старий
# блок незмінним (refs упав до 2). Це наочна версія worked-прикладу з тексту.

def fig_cow_share():
    W, H = 940, 430
    p = []
    hb_w, hb_h = 74, 40         # рамка-власник
    blk_w, blk_h = 190, 66      # рамка-блок

    def owner(cx, cy, name, col):
        p.append(rect(cx - hb_w / 2, cy - hb_h / 2, hb_w, hb_h, fill=BG, stroke=col, sw=1.8, rx=6))
        p.append(text(cx, cy + 5, name, size=15, color=col, bold=True))

    def block(cx, cy, title_, sub, fill, stroke):
        p.append(rect(cx - blk_w / 2, cy - blk_h / 2, blk_w, blk_h, fill=fill, stroke=stroke, sw=2.0, rx=8))
        p.append(text(cx, cy - 6, title_, size=14, color=INK, bold=True))
        p.append(text(cx, cy + 16, sub, size=12, color=MUTED))

    # ── ліва панель: усі троє читають один блок ──
    LX = 235
    p.append(text(LX, 64, "Поки всі лише читають — блок один", size=13.5, color=INK, bold=True))
    oy, by = 128, 300
    xs = [LX - 100, LX, LX + 100]
    for name, x in zip(["p", "q", "r"], xs):
        owner(x, oy, name, INK)
        p.append(arrow(x, oy + hb_h / 2 + 3, LX + (x - LX) * 0.14, by - blk_h / 2 - 4, color=MUTED, sw=1.6))
    block(LX, by, "блок #1", 'refs = 3   ·   "data"', BLKFILL, NEG)
    p.append(text(LX, by + blk_h / 2 + 26, "жодного байта не скопійовано", size=11, color=MUTED))

    # роздільник
    p.append(line(470, 66, 470, H - 26, color="#d8dde3", sw=1.3, dash="6 5"))

    # ── права панель: q пише й відколюється ──
    RX = 705
    p.append(text(RX, 64, "q пише X — і аж тепер копіює", size=13.5, color=INK, bold=True))
    old_cx, new_cx = RX - 118, RX + 130
    # власники
    owner(old_cx - 58, oy, "p", INK)
    owner(old_cx + 58, oy, "r", INK)
    owner(new_cx, oy, "q", FIELD)
    # старий спільний блок (p, r)
    block(old_cx, by, "блок #1", 'refs = 2   ·   "data"', BLKFILL, NEG)
    p.append(arrow(old_cx - 58, oy + hb_h / 2 + 3, old_cx - 20, by - blk_h / 2 - 4, color=MUTED, sw=1.6))
    p.append(arrow(old_cx + 58, oy + hb_h / 2 + 3, old_cx + 20, by - blk_h / 2 - 4, color=MUTED, sw=1.6))
    # нова копія (q)
    block(new_cx, by, "блок #2", 'refs = 1   ·   "Xata"', NEWFILL, FIELD)
    p.append(arrow(new_cx, oy + hb_h / 2 + 3, new_cx, by - blk_h / 2 - 4, color=FIELD, sw=1.9))
    p.append(text(new_cx, by + blk_h / 2 + 26, "приватна копія: сюди й лягло X", size=11, color=FIELD, bold=True))
    p.append(text(old_cx, by + blk_h / 2 + 26, "старий блок незмінний", size=11, color=MUTED))

    render(os.path.join(OUT, "cow-share.svg"), W, H, *p,
           title="Копіюємо не тоді, коли роздали, а тоді, коли хтось уперше пише")


# ── fork-pages: fork ділить сторінки, запис копіює рівно один кадр ────────────
# Ідея: ліворуч таблиці сторінок батька й дитини вказують на ті самі фізичні
# кадри, усі R/O — нуль копіювань. Праворуч дитина пише в сторінку 1: збій
# сторінки → копіюється рівно кадр 1, дитина йде на копію, решта спільна.

def fig_fork_pages():
    W, H = 960, 470
    p = []
    n = 3
    ce_w, ce_h = 60, 34         # клітинка таблиці сторінок
    fr_w, fr_h = 78, 34         # фізичний кадр
    gap = 12
    tbl_h = n * (ce_h + gap) - gap

    def page_table(x, top, label, col):
        p.append(text(x + ce_w / 2, top - 14, label, size=12.5, color=col, bold=True))
        ys = []
        for i in range(n):
            y = top + i * (ce_h + gap)
            p.append(rect(x, y, ce_w, ce_h, fill=BG, stroke=col, sw=1.6, rx=4))
            p.append(text(x + ce_w / 2, y + ce_h / 2 + 5, "стор. %d" % i, size=10.5, color=INK))
            ys.append(y + ce_h / 2)
        return ys

    def frames(cx, top, labels, fills, strokes):
        ys = []
        for i in range(len(labels)):
            y = top + i * (fr_h + gap)
            p.append(rect(cx - fr_w / 2, y, fr_w, fr_h, fill=fills[i], stroke=strokes[i], sw=1.7, rx=5))
            p.append(text(cx, y + fr_h / 2 + 5, labels[i], size=11.5, color=INK, bold=True))
            ys.append(y + fr_h / 2)
        return ys

    def panel(px, pw, title_, tcol, split):
        cx = px + pw / 2
        p.append(text(cx, 64, title_, size=13.5, color=tcol, bold=True))
        top = 132
        # таблиці сторінок ліворуч (батько) і праворуч (дитина)
        par_x = px + 24
        chi_x = px + pw - 24 - ce_w
        par_ys = page_table(par_x, top, "батько", NEG)
        chi_ys = page_table(chi_x, top, "дитина", POS)
        # фізичні кадри посередині
        fcx = cx
        if not split:
            labels = ["кадр 0", "кадр 1", "кадр 2"]
            fr_ys = frames(fcx, top, labels, [OLDFILL] * 3, [MUTED] * 3)
            for i in range(n):
                p.append(text(fcx, fr_ys[i] + fr_h / 2 + 13, "R/O", size=9.5, color=MUTED))
                p.append(arrow(par_x + ce_w + 3, par_ys[i], fcx - fr_w / 2 - 3, fr_ys[i], color=NEG, sw=1.5))
                p.append(arrow(chi_x - 3, chi_ys[i], fcx + fr_w / 2 + 3, fr_ys[i], color=POS, sw=1.5))
            p.append(text(cx, top + tbl_h + 40, "ті самі кадри, усі лише для читання — нуль копіювань",
                          size=11.5, color=MUTED))
        else:
            labels = ["кадр 0", "кадр 1", "кадр 2"]
            fr_ys = frames(fcx, top, labels, [OLDFILL, OLDFILL, OLDFILL], [MUTED, NEG, MUTED])
            # новий кадр 1' праворуч від кадру 1
            npx = fcx + 118
            p.append(rect(npx - fr_w / 2, top + (fr_h + gap) * 1, fr_w, fr_h, fill=NEWFILL, stroke=FIELD, sw=2.0, rx=5))
            p.append(text(npx, fr_ys[1] + 5, "кадр 1′", size=11.5, color=INK, bold=True))
            p.append(text(npx, fr_ys[1] + fr_h / 2 + 13, "RW (копія)", size=9.5, color=FIELD, bold=True))
            # спільні сторінки 0 і 2 — обидва
            for i in (0, 2):
                p.append(arrow(par_x + ce_w + 3, par_ys[i], fcx - fr_w / 2 - 3, fr_ys[i], color=NEG, sw=1.5))
                p.append(arrow(chi_x - 3, chi_ys[i], fcx + fr_w / 2 + 3, fr_ys[i], color=POS, sw=1.5))
                p.append(text(fcx, fr_ys[i] + fr_h / 2 + 13, "R/O", size=9.5, color=MUTED))
            # сторінка 1: батько лишається на кадрі 1, дитина йде на кадр 1'
            p.append(arrow(par_x + ce_w + 3, par_ys[1], fcx - fr_w / 2 - 3, fr_ys[1], color=NEG, sw=1.5))
            p.append(arrow(chi_x - 3, chi_ys[1], npx + fr_w / 2 + 3, fr_ys[1], color=FIELD, sw=2.0))
            # позначка збою на клітинці «стор.1» дитини
            p.append(text(chi_x + ce_w / 2, chi_ys[1] - ce_h / 2 - 6, "✳ збій сторінки", size=10, color=POS, bold=True))
            p.append(text(cx, top + tbl_h + 40, "запис у сторінку 1 → копіюється рівно кадр 1",
                          size=11.5, color=FIELD, bold=True))

    panel(0, 470, "Одразу після fork()", INK, split=False)
    p.append(line(478, 52, 478, H - 26, color="#d8dde3", sw=1.3, dash="6 5"))
    panel(486, 474, "Дитина пише в сторінку 1", POS, split=True)

    render(os.path.join(OUT, "fork-pages.svg"), W, H, *p,
           title="fork() ділить сторінки для читання; запис копіює лише одну")


# ── path-copying: змінити листок = скопіювати шлях, решту поділити ────────────
# Ідея: старе дерево (сіре) ціле; щоб замінити правий листок, копіюємо лише
# шлях корінь→8', 12', новий листок 15 (зелені). Нові вузли дивляться на старі
# спільні піддерева пунктиром. Дві версії ділять усе, крім O(log n) вузлів.

def fig_path_copying():
    W, H = 940, 500
    p = []
    R = 23

    def node(cx, cy, val, fill, stroke, tcol=INK):
        p.append(circle(cx, cy, R, fill=fill, stroke=stroke, sw=2.0))
        p.append(text(cx, cy + 5, str(val), size=14, color=tcol, bold=True))

    def edge(x1, y1, x2, y2, col, sw=1.7, dash=None):
        # від краю кола до краю кола
        import math
        a = math.atan2(y2 - y1, x2 - x1)
        p.append(line(x1 + R * math.cos(a), y1 + R * math.sin(a),
                      x2 - R * math.cos(a), y2 - R * math.sin(a), color=col, sw=sw, dash=dash))

    # ── СТАРЕ дерево (сіре), нижня-права зона ──
    Rt = (600, 250)
    L  = (470, 340)
    Rr = (730, 340)
    La = (405, 430); Lb = (535, 430); Rc = (665, 430); Rd = (795, 430)
    old_edges = [(Rt, L), (Rt, Rr), (L, La), (L, Lb), (Rr, Rc), (Rr, Rd)]
    for a, b in old_edges:
        edge(a[0], a[1], b[0], b[1], MUTED, sw=1.6)
    for (cx, cy), v in [(Rt, 8), (L, 4), (Rr, 12), (La, 2), (Lb, 6), (Rc, 10), (Rd, 14)]:
        node(cx, cy, v, OLDFILL, MUTED, tcol=MUTED)
    p.append(text(Rt[0] - R - 58, Rt[1] - 10, "версія 1", size=12, color=MUTED, bold=True, anchor="end"))
    p.append(text(Rt[0] - R - 58, Rt[1] + 8, "старий корінь", size=11, color=MUTED, anchor="end"))

    # ── НОВИЙ шлях (зелений), верхня-права зона, зсунутий угору ──
    Rt2 = (600, 118)
    Rr2 = (748, 240)
    Rd2 = (818, 355)
    # нові покажчики вздовж шляху (суцільні зелені)
    edge(Rt2[0], Rt2[1], Rr2[0], Rr2[1], FIELD, sw=2.2)      # 8' → 12'
    edge(Rr2[0], Rr2[1], Rd2[0], Rd2[1], FIELD, sw=2.2)      # 12' → 15
    # спільні покажчики в старі піддерева (пунктир)
    edge(Rt2[0], Rt2[1], L[0], L[1], FIELD, sw=1.7, dash="5 4")   # 8' → старий вузол 4 (спільне ліве піддерево)
    edge(Rr2[0], Rr2[1], Rc[0], Rc[1], FIELD, sw=1.7, dash="5 4") # 12' → старий листок 10 (спільний)
    node(*Rt2, "8′", NEWFILL, FIELD)
    node(*Rr2, "12′", NEWFILL, FIELD)
    node(*Rd2, "15", NEWFILL, FIELD)
    p.append(text(Rt2[0] + R + 16, Rt2[1] - 8, "версія 2", size=12, color=FIELD, bold=True, anchor="start"))
    p.append(text(Rt2[0] + R + 16, Rt2[1] + 10, "новий корінь", size=11, color=FIELD, anchor="start"))
    p.append(text(Rd2[0] + R + 10, Rd2[1] + 5, "новий листок", size=11, color=FIELD, bold=True, anchor="start"))
    # підписи «спільне» на пунктирних покажчиках (осторонь від самих ліній)
    p.append(text(498, 206, "спільне", size=10.5, color=FIELD, italic=True, anchor="end"))
    p.append(text(642, 402, "спільне", size=10.5, color=FIELD, italic=True, anchor="end"))

    # ── легенда ──
    lx, ly = 40, 80
    p.append(rect(lx, ly, 250, 96, fill="#fbfcfd", stroke="#d8dde3", sw=1.3, rx=8))
    p.append(circle(lx + 24, ly + 26, 11, fill=NEWFILL, stroke=FIELD, sw=2.0))
    p.append(text(lx + 44, ly + 30, "скопійований шлях — O(log n) вузлів", size=11, color=INK, anchor="start"))
    p.append(circle(lx + 24, ly + 54, 11, fill=OLDFILL, stroke=MUTED, sw=2.0))
    p.append(text(lx + 44, ly + 58, "старе спільне піддерево", size=11, color=INK, anchor="start"))
    p.append(line(lx + 14, ly + 80, lx + 34, ly + 80, color=FIELD, sw=1.7, dash="5 4"))
    p.append(text(lx + 44, ly + 84, "покажчик у спільне старе", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "path-copying.svg"), W, H, *p,
           title="Копіювання шляху: змінити один листок — скопіювати лише шлях до нього")


# ── cow-lineage: дві дороги (пам'ять / структури) сходяться на одному принципі ─
# Ідея (для hist-вставки): угорі синя лінія керування пам'яттю — BBN-LISP/940 →
# TENEX 1972 → 3BSD VM без COW → COW-fork у Mach/4.4BSD/Linux; унизу зелена лінія
# структур даних — персистентні дерева Сарнака-Тар'яна → загальна теорія DSST.
# Обидві стрілками входять у центральну рамку «ОДИН ПРИНЦИП».

def fig_lineage():
    W, H = 1120, 560
    p = []
    topy, boty = 155, 410
    LTBLUE, LTGREEN = "#eaf0fd", "#eafaf0"

    # підписи доріжок ліворуч
    p.append(mtext(70, topy - 6, ["Керування", "пам'яттю"], size=13, color=NEG, bold=True))
    p.append(mtext(70, boty - 6, ["Структури", "даних"], size=13, color=FIELD, bold=True))

    def place(cx, cy, s, stroke, fill):
        body, w, h = textbox(cx, cy, s, size=11.5, pad=9, fill=fill, stroke=stroke, sw=1.8, color=INK)
        p.append(body)
        return (cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2)   # left, right, top, bottom

    # ── верхня доріжка: керування пам'яттю ──
    t1 = place(255, topy, "BBN-LISP / SDS 940\n(кін. 1960-х)\nперша COW", NEG, LTBLUE)
    t2 = place(470, topy, "TENEX, PDP-10\n1972\nперша широка COW", NEG, LTBLUE)
    t3 = place(675, topy, "Unix VM: 3BSD\n1979 — без COW\n→ vfork", NEG, LTBLUE)
    t4 = place(850, topy, "COW-fork: Mach\n→ 4.4BSD, Linux", NEG, LTBLUE)
    for a, b in [(t1, t2), (t2, t3), (t3, t4)]:
        p.append(arrow(a[1] + 3, topy, b[0] - 3, topy, color=NEG, sw=1.7))

    # ── нижня доріжка: структури даних ──
    b1 = place(360, boty, "Сарнак і Тар'ян\nперсистентні дерева\nCACM 1986", FIELD, LTGREEN)
    b2 = place(650, boty, "DSST «Making Data\nStructures Persistent»\nSTOC 1986 / JCSS 1989", FIELD, LTGREEN)
    p.append(arrow(b1[1] + 3, boty, b2[0] - 3, boty, color=FIELD, sw=1.7))

    # ── центральна рамка «ОДИН ПРИНЦИП» ──
    cvx, cvy = 1010, 283
    cbody, cw, ch = textbox(cvx, cvy, "ОДИН ПРИНЦИП\nспільне — незмінне\nкопіюй лише те,\nщо змінюєш",
                            size=12.5, pad=12, fill="#fbfcfd", stroke=INK, sw=2.2, color=INK, bold=True, min_w=190)
    cl = cvx - cw / 2
    # обидві доріжки входять у рамку
    p.append(arrow(t4[1] + 3, topy + 8, cl - 3, cvy - 28, color=NEG, sw=1.9))
    p.append(arrow(b2[1] + 3, boty - 8, cl - 3, cvy + 28, color=FIELD, sw=1.9))
    p.append(cbody)   # рамку малюємо поверх кінців стрілок
    p.append(text(cvx, cvy + ch / 2 + 20, "= copy-on-write / персистентність", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "cow-lineage.svg"), W, H, *p,
           title="Дві дороги до однієї думки: пам'ять і структури даних")


# ── version-chain: багато версій ділять одне ядро, кожна додає лише шлях ───────
# Ідея (для proj-вставки про персистентне дерево): масив versions[] тримає корені
# v0..v3; v0 — уся база (велике спільне ядро), а кожна наступна версія — це той
# самий поділений кістяк ПЛЮС тонкий свіжий шлях O(log n) вузлів. Разом k версій
# коштують O(k·log n), а не O(k·n): числа з реального заміру внизу фігури.

def fig_version_chain():
    W, H = 900, 430
    p = []
    ax, cw, ch = 54, 58, 34            # масив versions[]
    cy = [116, 170, 224, 278]          # центри рядків v0..v3
    labels = ["v0", "v1", "v2", "v3"]
    capx, capw, caph = 252, 104, 28    # свіжий шлях (зелена «шапка») для v1..v3
    core_x, core_y, core_w, core_h = 470, 96, 340, 250

    # заголовок масиву й заголовок над зеленими шапками
    p.append(text(ax + cw / 2, 74, "versions[]", size=13, color=INK, bold=True))
    p.append(text(capx + capw / 2, 92, "свіжий шлях версії", size=11.5, color=FIELD, bold=True))

    # спільне ядро (база v0)
    p.append(rect(core_x, core_y, core_w, core_h, fill=OLDFILL, stroke=MUTED, sw=1.9, rx=14))
    p.append(text(core_x + core_w / 2, core_y + core_h / 2 - 10, "версія v0 — база", size=15.5, color=INK, bold=True))
    p.append(text(core_x + core_w / 2, core_y + core_h / 2 + 14, "≈ 1000 вузлів, спільні для всіх версій", size=11.5, color=MUTED))

    # рядки версій
    caps = {1: "+12 вузлів", 2: "+12 вузлів", 3: "+13 вузлів"}
    for i, (lab, y) in enumerate(zip(labels, cy)):
        col = MUTED if i == 0 else NEG
        p.append(rect(ax, y - ch / 2, cw, ch, fill=BG, stroke=col, sw=1.7, rx=6))
        p.append(text(ax + cw / 2, y + 5, lab, size=14, color=col, bold=True))
        if i == 0:
            p.append(arrow(ax + cw + 4, y, core_x - 4, y, color=MUTED, sw=1.6))
            p.append(text(300, 138, "v0 — це й є ядро", size=10.5, color=MUTED, italic=True))
        else:
            p.append(arrow(ax + cw + 4, y, capx - 4, y, color=NEG, sw=1.6))
            p.append(rect(capx, y - caph / 2, capw, caph, fill=NEWFILL, stroke=FIELD, sw=1.8, rx=7))
            p.append(text(capx + capw / 2, y + 4, caps[i], size=12, color=INK, bold=True))
            p.append(arrow(capx + capw + 4, y, core_x - 4, y, color=FIELD, sw=1.8))

    # підсумок унизу
    p.append(text(W / 2, H - 44, "k версій · кожна додає лише шлях O(log n) · разом O(k·log n), а не O(k·n)",
                  size=12.5, color=INK, bold=True))
    p.append(text(W / 2, H - 22, "замір: 20 версій над деревом на 1000 вузлів → 261 новий вузол, а не 20 000",
                  size=11.5, color=MUTED))

    render(os.path.join(OUT, "version-chain.svg"), W, H, *p,
           title="Персистентне дерево: кожна версія — тонкий свіжий шлях над спільним ядром")


# ── height-levels: чому шлях у дереві з розгалуженням-надвоє — це log ──────────
# Ідея: рівень i вміщає щонайбільше 2ⁱ вузлів, тож дерево висоти h має не більш
# ніж 2ʰ⁺¹−1 вузлів; звідси h ≥ log₂(n+1)−1. Логарифм — підлога, а не везіння:
# щоб виокремити 1 із n листків двійковими виборами, треба ≈ log₂ n рівнів.

def fig_height_levels():
    W, H = 860, 470
    p = []
    R = 15
    cx = 350
    top = 92
    row_h = 66
    caps = [1, 2, 4, 8]
    sup = ["⁰", "¹", "²", "³"]
    # вертикальна дужка «висота h» ліворуч
    by0 = top - R - 8
    by1 = top + (len(caps) - 1) * row_h + R + 8
    p.append(line(34, by0, 34, by1, color="#c7ccd3", sw=1.5))
    p.append(line(34, by0, 40, by0, color="#c7ccd3", sw=1.5))
    p.append(line(34, by1, 40, by1, color="#c7ccd3", sw=1.5))
    p.append(text(26, (by0 + by1) / 2 + 4, "h", size=14, color=MUTED, anchor="end", bold=True))
    for i, cap in enumerate(caps):
        y = top + i * row_h
        p.append(text(58, y + 5, "рівень %d" % i, size=12.5, color=MUTED, anchor="start", bold=True))
        span = (cap - 1) * (2 * R + 12)
        x0 = cx - span / 2
        last = (i == len(caps) - 1)
        for j in range(cap):
            x = x0 + j * (2 * R + 12)
            p.append(circle(x, y, R,
                            fill=NEWFILL if last else OLDFILL,
                            stroke=FIELD if last else MUTED, sw=1.8))
        p.append(text(600, y + 5, "≤ 2%s = %d" % (sup[i], cap), size=13, color=INK, anchor="start"))
    ys = top + (len(caps) - 1) * row_h + 58
    p.append(line(58, ys - 16, W - 40, ys - 16, color="#d8dde3", sw=1.2, dash="6 5"))
    p.append(text(W / 2, ys + 6, "n ≤ 2⁰ + 2¹ + 2² + … + 2ʰ = 2ʰ⁺¹ − 1", size=15, color=INK, bold=True))
    p.append(text(W / 2, ys + 36, "⟹  висота  h ≥ log₂(n + 1) − 1", size=15, color=FIELD, bold=True))
    p.append(text(W / 2, ys + 64,
                  "крок униз — один двійковий вибір: виокремити 1 із n листків коштує ≈ log₂ n рівнів",
                  size=11.5, color=MUTED))
    render(os.path.join(OUT, "height-levels.svg"), W, H, *p,
           title="Чому шлях коштує log: висота дерева з розгалуженням-надвоє")


# ── cost-compare: той самий листок — усе дерево проти лише шляху ───────────────
# Ідея: ліворуч зміна перекопіює ВСІ n вузлів (повне копіювання, O(n)),
# праворуч — лише шлях корінь→листок (O(log n)), решта спільна. Унизу таблиця:
# у скільки разів n більше за log₂ n на реальних розмірах.

def fig_copy_vs_path():
    import math
    W, H = 920, 580
    p = []
    R = 13
    levels = 4
    step_y = 70
    oy = 90
    PATH = {(0, 0), (1, 1), (2, 3), (3, 7)}   # шлях до правого листка

    def layout(ox, w):
        pos = {}
        for L in range(levels):
            cnt = 2 ** L
            for idx in range(cnt):
                pos[(L, idx)] = (ox + w * (idx + 0.5) / cnt, oy + L * step_y)
        return pos

    def draw_tree(pos, path_only):
        for L in range(levels - 1):
            for idx in range(2 ** L):
                a = pos[(L, idx)]
                for c in (2 * idx, 2 * idx + 1):
                    b = pos[(L + 1, c)]
                    on = (not path_only) or ((L, idx) in PATH and (L + 1, c) in PATH)
                    ang = math.atan2(b[1] - a[1], b[0] - a[0])
                    p.append(line(a[0] + R * math.cos(ang), a[1] + R * math.sin(ang),
                                  b[0] - R * math.cos(ang), b[1] - R * math.sin(ang),
                                  color=FIELD if on else MUTED, sw=2.0 if on else 1.3,
                                  dash=None if on else "4 4"))
        for (L, idx), (x, y) in pos.items():
            hot = (not path_only) or ((L, idx) in PATH)
            p.append(circle(x, y, R, fill=NEWFILL if hot else OLDFILL,
                            stroke=FIELD if hot else MUTED, sw=1.9 if hot else 1.4))

    base = oy + 3 * step_y
    draw_tree(layout(40, 380), path_only=False)
    p.append(text(230, 64, "повне копіювання", size=14, color=INK, bold=True))
    p.append(text(230, base + 42, "15 нових вузлів  =  O(n)", size=13, color=FIELD, bold=True))

    p.append(line(468, 50, 468, base + 24, color="#d8dde3", sw=1.3, dash="6 5"))

    draw_tree(layout(500, 380), path_only=True)
    p.append(text(690, 64, "копіювання шляху", size=14, color=INK, bold=True))
    p.append(text(690, base + 42, "4 нових вузли  =  O(log n)", size=13, color=FIELD, bold=True))
    p.append(text(690, base + 64, "решта — спільна зі старою версією", size=11, color=MUTED))

    tx, ty = 250, 428
    cw = [140, 130, 160]
    rows = [["n", "log₂ n", "n / log₂ n"],
            ["10³", "≈ 10", "≈ 100"],
            ["10⁶", "≈ 20", "≈ 50 000"],
            ["10⁹", "≈ 30", "≈ 33 000 000"]]
    rh = 30
    p.append(text(tx + sum(cw) / 2, ty - 12, "у скільки разів повна копія дорожча за версію",
                  size=12.5, color=INK, bold=True))
    for r, row in enumerate(rows):
        yy = ty + r * rh
        cxx = tx
        head = (r == 0)
        for cidx, cell in enumerate(row):
            p.append(rect(cxx, yy, cw[cidx], rh, fill=FILL if head else BG, stroke="#d8dde3", sw=1.2, rx=0))
            p.append(text(cxx + cw[cidx] / 2, yy + rh / 2 + 5, cell, size=12.5, color=INK,
                          bold=head or cidx == 2))
            cxx += cw[cidx]
    render(os.path.join(OUT, "cost-compare.svg"), W, H, *p,
           title="Той самий листок: скопіювати все дерево чи лише шлях до нього")


# ── refcount-rule: чому правило refs>1⇒копіюй коректне, і де воно ламається ────
# Ідея: обидві гілки (refs=1 пишемо на місці; refs>1 копіюємо) мутують лише
# приватний вузол — тож інваріант спільності тримається. Небезпечна ЛИШЕ
# недооцінка лічильника; переоцінка тільки марнує копію, але безпечна.

def fig_refcount_rule():
    W, H = 900, 540
    p = []

    def box(cx, cy, w, h, s, fill=FILL, stroke=LINE, tcol=INK, size=13, bold=False):
        p.append(rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, sw=1.8, rx=8))
        lines = s.split("\n")
        y0 = cy - (len(lines) - 1) * size * 0.65 + size * 0.35
        p.append(mtext(cx, y0, lines, size=size, color=tcol, bold=bold))

    box(450, 62, 200, 40, "запис у вузол x", fill=BG, stroke=INK, bold=True)
    p.append(arrow(450, 82, 450, 116, color=INK, sw=1.7))
    box(450, 140, 210, 42, "refs(x) > 1 ?", fill="#fff8e6", stroke="#c9a227", size=14, bold=True)

    p.append(arrow(362, 156, 250, 212, color=NEG, sw=1.7))
    p.append(text(288, 180, "ні", size=12, color=NEG, bold=True))
    box(230, 234, 230, 42, "refs = 1 — вузол приватний", fill=BG, stroke=NEG, size=12.5)
    p.append(arrow(230, 255, 230, 300, color=NEG, sw=1.7))
    box(230, 326, 214, 46, "пиши в x на місці", fill=NEWFILL, stroke=FIELD, size=13, bold=True)

    p.append(arrow(538, 156, 660, 212, color=POS, sw=1.7))
    p.append(text(610, 180, "так", size=12, color=POS, bold=True))
    box(672, 234, 236, 42, "refs > 1 — вузол спільний", fill=BG, stroke=POS, size=12.5)
    p.append(arrow(672, 255, 672, 300, color=POS, sw=1.7))
    box(672, 328, 250, 52, "копія x′ (refs = 1),\nrefs(x)−− ,  пиши в x′", fill=NEWFILL, stroke=FIELD, size=12.5, bold=True)

    p.append(arrow(230, 349, 300, 420, color=FIELD, sw=1.7))
    p.append(arrow(672, 354, 600, 420, color=FIELD, sw=1.7))
    box(450, 440, 480, 46,
        "мутуємо лише приватний вузол (refs = 1)  ⟹  жоден спільний вузол не змінено  ✓",
        fill="#eafaf0", stroke=FIELD, size=12.5, bold=True)

    box(450, 506, 842, 46,
        "Небезпечна лише недооцінка: лічильник каже 1 при ≥ 2 власниках → запис протікає в чужу версію.\n"
        "Переоцінка (каже ≥ 2 при одному власнику) — тільки зайва копія: безпечно, хоч і марно.",
        fill="#fdecea", stroke=POS, size=11.5)

    render(os.path.join(OUT, "refcount-rule.svg"), W, H, *p,
           title="Правило з лічильником: мутуємо лише те, чим володіємо самі")


if __name__ == "__main__":
    fig_cow_share()
    fig_fork_pages()
    fig_path_copying()
    fig_lineage()
    fig_version_chain()
    fig_height_levels()
    fig_copy_vs_path()
    fig_refcount_rule()
    print("figs: готово")
