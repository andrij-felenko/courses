# -*- coding: utf-8 -*-
"""Фігури до теми «Роль системи збірки: від дерева файлів до артефакту»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

DIRTY = "#fdecea"     # треба перезібрати
CLEAN = "#eaf7ef"     # лишається чинним


def node(cx, cy, label, fill=FILL, stroke=LINE, bold=False, size=15, sw=1.5):
    frag, w, h = textbox(cx, cy, label, size=size, fill=fill, stroke=stroke,
                         bold=bold, sw=sw)
    return frag, (cx, cy, w, h)


def down(a, b, color=LINE, sw=1.8):
    """Стрілка згори вниз: від нижнього краю a до верхнього краю b."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return arrow(ax, ay + ah / 2 + 3, bx, by - bh / 2 - 5, color=color, sw=sw)


# ── 1. Локальні правила складаються в граф; зміна йде тільки вниз ───────────
def fig_graph():
    W, H = 940, 500
    parts = []

    y_src, y_obj, y_bin = 100, 250, 372

    uh, g_uh = node(150, y_src, "util.h", fill=BG, stroke=POS, bold=True, sw=2.2)
    uc, g_uc = node(330, y_src, "util.c", fill=CLEAN, stroke=FIELD)
    mc, g_mc = node(540, y_src, "main.c", fill=CLEAN, stroke=FIELD)
    nc, g_nc = node(760, y_src, "net.c", fill=CLEAN, stroke=FIELD)

    uo, g_uo = node(240, y_obj, "util.o", fill=DIRTY, stroke=POS, sw=2)
    mo, g_mo = node(500, y_obj, "main.o", fill=DIRTY, stroke=POS, sw=2)
    no, g_no = node(760, y_obj, "net.o", fill=CLEAN, stroke=FIELD)

    ap, g_ap = node(500, y_bin, "app", fill=DIRTY, stroke=POS, bold=True, sw=2)

    parts += [uh, uc, mc, nc, uo, mo, no, ap]
    parts.append(text(150, 66, "змінили", size=13, color=POS, bold=True))

    parts += [down(g_uh, g_uo, color=POS), down(g_uh, g_mo, color=POS),
              down(g_uc, g_uo), down(g_mc, g_mo), down(g_nc, g_no),
              down(g_uo, g_ap, color=POS), down(g_mo, g_ap, color=POS),
              down(g_no, g_ap)]

    ly = 456
    for cx, label, fill, stroke in ((190, "змінений вихідний файл", BG, POS),
                                    (500, "треба перезібрати", DIRTY, POS),
                                    (780, "лишається чинним", CLEAN, FIELD)):
        frag, _, _ = textbox(cx, ly, label, size=13, fill=fill, stroke=stroke, pad=8)
        parts.append(frag)

    render(os.path.join(IMG, "graph-and-wave.svg"), W, H, *parts,
           title="Правила задають лише сусідство — граф і хвиля виходять самі")


# ── 2. Ключ задачі: що в ньому є і що його оминає ───────────────────────────
def fig_key():
    W, H = 1000, 520
    parts = []

    # верхня панель: оголошені входи
    parts.append(rect(45, 62, 400, 232, fill="#f8fafc", stroke=MUTED, sw=1.5))
    parts.append(text(245, 88, "Оголошені входи", size=15, bold=True))
    rows = ["вміст .c і всіх включених заголовків",
            "рядок команди: прапорці, макроси",
            "версія компілятора й тулчейна",
            "імена й шляхи вихідних файлів"]
    for i, r in enumerate(rows):
        parts.append(fitbox(62, 102 + i * 46, 366, 38, r, size=13.5))

    parts.append(arrow(452, 178, 512, 178))
    kf, kw, kh = textbox(618, 178, "ключ задачі\n= геш усього\nоголошеного",
                         size=15, bold=True, fill="#eef4ff", stroke=NEG, sw=2)
    parts.append(kf)
    parts.append(arrow(618 + kw / 2 + 4, 178, 762, 178))
    cf, _, _ = textbox(878, 178, "такий ключ уже був —\nрезультат беремо\nз кеша",
                       size=13.5, fill=CLEAN, stroke=FIELD)
    parts.append(cf)

    # нижня панель: непроголошені входи
    parts.append(rect(45, 330, 400, 158, fill="#fff6f5", stroke=POS, sw=1.5))
    parts.append(text(245, 356, "Непроголошені входи", size=15, bold=True, color=POS))
    rows2 = ["заголовок, знайдений у системній теці",
             "час збірки, шлях до теки, оточення",
             "порядок обходу каталогу, паралельність"]
    for i, r in enumerate(rows2):
        parts.append(fitbox(62, 368 + i * 40, 366, 34, r, size=13.5, fill=BG, stroke=POS))

    parts.append(arrow(452, 408, 762, 366, color=POS, sw=2))
    bf, _, _ = textbox(878, 348, "той самий ключ —\nінший результат",
                       size=13.5, fill="#fdecea", stroke=POS, sw=2)
    parts.append(bf)
    parts.append(text(600, 456, "ключ їх не бачить — і рівність, на якій стоїть кеш, тихо ламається",
                      size=13.5, color=POS, italic=True))

    render(os.path.join(IMG, "task-key.svg"), W, H, *parts,
           title="Кеш збірки правдивий рівно настільки, наскільки повний ключ")


# ── 3. Два незалежні вибори: порядок обходу і привід перезапуску ────────────
def fig_space():
    W, H = 1000, 470
    parts = []

    x0, colw = 300, 232
    y0, rowh = 92, 72
    cols = ["топологічний", "з перезапуском", "із призупиненням"]
    rows = ["біт «брудний»", "слід-перевірка", "слід із вмістом", "глибокий слід"]
    cells = [["Make", "Excel", "—"],
             ["Ninja", "—", "Shake"],
             ["CloudBuild", "Bazel", "—"],
             ["Buck", "—", "Nix"]]

    parts.append(text(170, 66, "чим доводять, що робота потрібна", size=13.5, color=MUTED))
    parts.append(text(x0 + 1.5 * colw, 66, "у якому порядку обходять граф", size=13.5, color=MUTED))

    for j, c in enumerate(cols):
        parts.append(fitbox(x0 + j * colw, y0, colw - 6, 40, c, size=14,
                            bold=True, fill="#f8fafc", stroke=MUTED))
    for i, r in enumerate(rows):
        parts.append(fitbox(45, y0 + 48 + i * rowh, 245, rowh - 8, r, size=14,
                            bold=True, fill="#f8fafc", stroke=MUTED))
        for j in range(3):
            v = cells[i][j]
            empty = (v == "—")
            parts.append(fitbox(x0 + j * colw, y0 + 48 + i * rowh, colw - 6, rowh - 8, v,
                                size=15, bold=not empty,
                                fill=BG if empty else CLEAN,
                                stroke=MUTED if empty else FIELD,
                                color=MUTED if empty else INK))

    parts.append(text(500, 438, "порожня клітинка — поєднання, якого поки ніхто не збудував",
                      size=13.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "scheduler-rebuilder.svg"), W, H, *parts,
           title="Порядок і привід — незалежні ручки, а не одна властивість")


# ── 4. Ціни 1976 року: мітка часу, геш, компіляція ───────────────
def fig_costs():
    import math
    W, H = 980, 400
    parts = []

    rows = [
        ("обійти мітки часу", 0.02, "≈ мілісекунди", FIELD, CLEAN),
        ("прогешувати весь вміст", 1.5, "≈ секунда", "#b7791f", "#fdf3e0"),
        ("скомпілювати ОДИН файл", 20.0, "≈ десятки секунд", POS, DIRTY),
    ]

    lx, lw = 34, 268          # колонка підписів
    bx, bmax = 330, 470       # початок і максимальна довжина смуги
    y0, rowh, bh = 92, 92, 40

    parts.append(text(lx + lw / 2, 66, "операція", size=13.5, color=MUTED))
    parts.append(text(bx + bmax / 2, 66, "час (логарифмічна шкала)", size=13.5, color=MUTED))

    for i, (label, val, note, stroke, fill) in enumerate(rows):
        cy = y0 + i * rowh
        parts.append(fitbox(lx, cy - bh / 2 - 4, lw, bh + 8, label,
                            size=14.5, bold=True, fill="#f8fafc", stroke=MUTED))
        w = (math.log10(val) + 2.0) / 3.5 * bmax
        parts.append(rect(bx, cy - bh / 2, w, bh, fill=fill, stroke=stroke, sw=2))
        parts.append(text(bx + w + 14, cy + 5, note, size=14, color=stroke,
                          bold=True, anchor="start"))

    parts.append(text(W / 2, 368,
                      "мітка часу дешевша за геш на два порядки — а геш всього дерева забирав помітну частку однієї компіляції",
                      size=13.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "make-1976-costs.svg"), W, H, *parts,
           title="Ціни 1976 року: чому ознакою став час зміни, а не вміст")


def poly(pts, color=LINE, sw=2.4, dash=None):
    """Ламана без заливки (для графіків)."""
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (" ".join("%.1f,%.1f" % (x, y) for x, y in pts), color, sw, d))


# ── 5. Ціна правки: платить охоплення, а не розмір проєкту ──────────────────
def fig_reach_cost():
    import math
    W, H = 1060, 420
    parts = []

    TAU, LNK, CORES = 0.4, 12.0, 16
    rows = [("одна одиниця трансляції", 1, CLEAN, FIELD),
            ("сто незалежних .cpp", 100, CLEAN, FIELD),
            ("заголовок у 40% одиниць", 1200, DIRTY, POS)]

    lx, lw = 28, 258
    p1x, p1w, p1max = 320, 300, 540.0     # робота, с
    p2x, p2w, p2max = 728, 250, 50.0      # час на 16 ядрах, с
    y0, rowh, bh = 138, 84, 36

    parts.append(text(lx + lw / 2, 96, "що змінили", size=13.5, color=MUTED))
    parts.append(text(p1x + p1w / 2, 96, "робота W, с", size=13.5, color=MUTED))
    parts.append(text(p2x + p2w / 2, 96, "час на 16 ядрах, с", size=13.5, color=MUTED))

    for i, (label, n, fill, stroke) in enumerate(rows):
        cy = y0 + i * rowh
        work = n * TAU + LNK
        wall = math.ceil(n / CORES) * TAU + LNK
        parts.append(fitbox(lx, cy - bh / 2 - 5, lw, bh + 10, label,
                            size=14, bold=True, fill="#f8fafc", stroke=MUTED))
        for bx, bw, bmax, val in ((p1x, p1w, p1max, work), (p2x, p2w, p2max, wall)):
            ln = max(4.0, val / bmax * bw)
            parts.append(rect(bx, cy - bh / 2, ln, bh, fill=fill, stroke=stroke, sw=2))
            parts.append(text(bx + ln + 12, cy + 5, "%.1f" % val, size=14.5,
                              color=stroke, bold=True, anchor="start"))

    parts.append(text(W / 2, 388,
                      "сто файлів коштують на 2.4 с більше за один — а один заголовок ще на 27 с більше за сотню файлів",
                      size=13.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "reach-cost.svg"), W, H, *parts,
           title="Проєкт той самий (3000 одиниць) — ціна правки різниться в десятки разів")


# ── 6. Стеля паралельності: критичний шлях не пробивається ядрами ───────────
def fig_span_ceiling():
    import math
    W, H = 1100, 510
    parts = []

    X0, XW, Y0, YH = 110, 630, 78, 322
    TMIN, TMAX = 10.0, 2000.0
    span = math.log10(TMAX) - math.log10(TMIN)

    def xf(p):
        return X0 + math.log(p, 2) / 7.0 * XW

    def yf(t):
        return Y0 + YH - (math.log10(t) - math.log10(TMIN)) / span * YH

    # сітка й осі
    for t in (10, 100, 1000):
        y = yf(t)
        parts.append(line(X0, y, X0 + XW, y, color="#d7dbe0", sw=1.1, dash="4 5"))
        parts.append(text(X0 - 12, y + 5, str(t), size=13, color=MUTED, anchor="end"))
    parts.append(line(X0, Y0, X0, Y0 + YH, color=INK, sw=1.6))
    parts.append(line(X0, Y0 + YH, X0 + XW, Y0 + YH, color=INK, sw=1.6))
    for p in (1, 2, 4, 8, 16, 32, 64, 128):
        x = xf(p)
        parts.append(line(x, Y0 + YH, x, Y0 + YH + 6, color=INK, sw=1.4))
        parts.append(text(x, Y0 + YH + 24, str(p), size=13, color=MUTED))
    parts.append(text(X0 + XW / 2, Y0 + YH + 52, "ядер p", size=14, color=MUTED))
    parts.append(text(X0 + 4, Y0 - 16, "час, с", size=14, color=MUTED, anchor="start"))

    ps = [1, 2, 4, 8, 16, 32, 64, 128]
    for (Wk, S, color) in ((1612.0, 12.4, NEG), (1700.0, 100.4, POS)):
        pts = [(xf(p), yf(max(Wk / p, S))) for p in ps]
        parts.append(poly(pts, color=color, sw=2.6))
        for x, y in pts:
            parts.append(circle(x, y, 4.2, fill=BG, stroke=color, sw=2))

    lf, _, _ = textbox(920, 170,
                       "плоский граф\n4000 одиниць + лінк\nW = 1612 с   S = 12.4 с\nрозгін вичерпано на 130 ядрах",
                       size=13, fill="#eef4ff", stroke=NEG, sw=2)
    parts.append(lf)
    ld, _, _ = textbox(920, 320,
                       "глибокий граф\n6 стадій ланцюгом\nW = 1700 с   S = 100.4 с\nрозгін вичерпано на 17 ядрах",
                       size=13, fill="#fdecea", stroke=POS, sw=2)
    parts.append(ld)

    parts.append(text(W / 2, 480,
                      "нахил −1 — це W/p; горизонтальна поличка — критичний шлях S, і ядра її не пробивають",
                      size=13.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "span-ceiling.svg"), W, H, *parts,
           title="5.5% зайвої роботи ланцюгом — і на 64 ядрах вчетверо довше")


# ── 7. Рання відсічка: поріг згасання хвилі ─────────────────────────────────
def fig_cutoff_threshold():
    import math
    W, H = 1100, 520
    parts = []

    B = 3.0
    X0, XW, Y0, YH = 110, 600, 78, 336
    DEC = 6.0                      # десяткових порядків по вертикалі

    def xf(a):
        return X0 + a * XW

    def yf(n):
        return Y0 + YH - math.log10(max(n, 1.0)) / DEC * YH

    def expected(a, D):
        m = B * (1.0 - a)
        return sum(m ** k for k in range(D + 1))

    for e in range(7):
        y = yf(10.0 ** e)
        parts.append(line(X0, y, X0 + XW, y, color="#d7dbe0", sw=1.1, dash="4 5"))
        lab = ["1", "10", "100", "10³", "10⁴", "10⁵", "10⁶"][e]
        parts.append(text(X0 - 12, y + 5, lab, size=13, color=MUTED, anchor="end"))
    parts.append(line(X0, Y0, X0, Y0 + YH, color=INK, sw=1.6))
    parts.append(line(X0, Y0 + YH, X0 + XW, Y0 + YH, color=INK, sw=1.6))
    for a in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        x = xf(a)
        parts.append(line(x, Y0 + YH, x, Y0 + YH + 6, color=INK, sw=1.4))
        parts.append(text(x, Y0 + YH + 24, ("%.1f" % a), size=13, color=MUTED))
    parts.append(text(X0 + XW / 2, Y0 + YH + 52,
                      "α — імовірність, що перегенерований файл збігся побайтово",
                      size=14, color=MUTED))
    parts.append(text(X0 + 4, Y0 - 16, "очікувано задач", size=14, color=MUTED, anchor="start"))

    astar = 1.0 - 1.0 / B
    parts.append(line(xf(astar), Y0, xf(astar), Y0 + YH, color=FIELD, sw=2, dash="7 5"))
    parts.append(text(xf(astar) + 10, Y0 - 16, "α* = 1 − 1/b = 0.67",
                      size=13.5, color=FIELD, bold=True, anchor="start"))

    grid = [i / 50.0 for i in range(51)]
    for D, color in ((6, NEG), (12, POS)):
        parts.append(poly([(xf(a), yf(expected(a, D))) for a in grid], color=color, sw=2.6))

    l6, _, _ = textbox(900, 160, "глибина графа\n6 рівнів", size=13.5,
                       fill="#eef4ff", stroke=NEG, sw=2)
    parts.append(l6)
    l12, _, _ = textbox(900, 262, "глибина графа\n12 рівнів", size=13.5,
                        fill="#fdecea", stroke=POS, sw=2)
    parts.append(l12)
    ln, _, _ = textbox(900, 386,
                       "ліворуч від α*\nхвиля росте з глибиною;\nправоруч глибина\nперестає щось важити",
                       size=13, fill="#eaf7ef", stroke=FIELD, sw=2)
    parts.append(ln)

    parts.append(text(X0 + XW / 2, 492,
                      "b = 3 нащадки на вершину; криві сходяться там, де середнє число живих нащадків падає нижче одиниці",
                      size=13.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "cutoff-threshold.svg"), W, H, *parts,
           title="Рання відсічка має поріг: до нього вона лише множник, після — інша поведінка")


# ── 8. Вставка proj-mini-build: три кольори DFS ловлять цикл ────────────────
GRAY_F = "#dfe3e8"      # вершина на стеку
BLACK_F = "#3f4652"     # вершина закрита


def mbnode(cx, cy, label, fill=FILL, stroke=LINE, color=INK, size=15, sw=1.5, bold=False):
    frag, w, h = textbox(cx, cy, label, size=size, fill=fill, stroke=stroke,
                         color=color, bold=bold, sw=sw)
    return frag, (cx, cy, w, h)


def mbright(a, b, color=LINE, sw=1.8):
    """Стрілка зліва направо: від правого краю a до лівого краю b."""
    ax, ay, aw, _ = a
    bx, by, bw, _ = b
    return arrow(ax + aw / 2 + 4, ay, bx - bw / 2 - 5, by, color=color, sw=sw)


def fig_dfs_colors():
    W, H = 980, 440
    parts = []

    tool, g_tool = mbnode(150, 150, "tool", fill=GRAY_F)
    geno, g_geno = mbnode(390, 150, "gen.o", fill=GRAY_F)
    genc, g_genc = mbnode(640, 150, "gen.c", fill=GRAY_F)
    utilo, g_utilo = mbnode(150, 310, "util.o", fill=BLACK_F, stroke=BLACK_F, color=BG)
    genh, g_genh = mbnode(390, 310, "gen.h", fill=BG, stroke=MUTED)

    parts += [tool, geno, genc, utilo, genh]
    parts += [mbright(g_tool, g_geno), mbright(g_geno, g_genc),
              down(g_tool, g_utilo), down(g_geno, g_genh, color=MUTED, sw=1.4)]

    # зворотне ребро gen.c → tool, проведене згори, щоб нічого не перетинати
    parts += [line(640, 127, 640, 96, color=POS, sw=2),
              line(640, 96, 150, 96, color=POS, sw=2),
              arrow(150, 96, 150, 126, color=POS, sw=2)]
    parts.append(text(395, 72, "зворотне ребро у СІРУ вершину — це цикл",
                      size=13.5, color=POS, bold=True))
    parts.append(text(708, 155, "← поточна", size=13, color=MUTED, anchor="start"))

    for cx, label, fill, stroke, color in (
            (180, "білий — ще не заходили", BG, MUTED, INK),
            (496, "сірий — на стеку, в роботі", GRAY_F, LINE, INK),
            (818, "чорний — закрита, циклів нема", BLACK_F, BLACK_F, BG)):
        frag, _, _ = textbox(cx, 395, label, size=13, fill=fill, stroke=stroke,
                             color=color, pad=8)
        parts.append(frag)

    render(os.path.join(IMG, "mb-dfs-colors.svg"), W, H, *parts,
           title="Цикл видно там, де обхід повертається у вершину власної гілки")


# ── 9. Вставка proj-mini-build: життя однієї задачі в робітнику ─────────────
def fig_worker():
    W, H = 1040, 650
    parts = []

    q, g_q = mbnode(520, 90, "черга готових вершин", size=15)
    k, g_k = mbnode(520, 185, "ключ = геш( вміст входів · рядок команди · імʼя виходу )",
                    size=15, fill="#f8fafc")
    d, g_d = mbnode(520, 285, "такий самий ключ уже в журналі,\nа артефакт на місці?",
                    size=15, fill="#eef4ff", stroke=NEG, bold=True, sw=2)
    yes, g_yes = mbnode(235, 400, "так:\nкоманду не запускаємо\n— ось і вся рання відсічка",
                        size=13, fill=CLEAN, stroke=FIELD, sw=2)
    no, g_no = mbnode(805, 400, "ні:\nвиконати у out.mb-tmp\nі атомарно перейменувати",
                      size=13, fill="#fff6f5", stroke=POS, sw=2)
    j, g_j = mbnode(805, 512, "у журнал: ключ і геш артефакту", size=13)
    rel, g_rel = mbnode(520, 592, "нащадкам −1 до лічильника;\nхто дійшов нуля — у чергу готових",
                        size=14, fill="#f8fafc")

    parts += [q, k, d, yes, no, j, rel]
    parts += [down(g_q, g_k), down(g_k, g_d),
              down(g_d, g_yes, color=FIELD), down(g_d, g_no, color=POS),
              down(g_no, g_j, color=POS), down(g_j, g_rel),
              down(g_yes, g_rel, color=FIELD)]

    render(os.path.join(IMG, "mb-worker.svg"), W, H, *parts,
           title="Що робить робітник з однією вершиною")


if __name__ == "__main__":
    fig_graph()
    fig_key()
    fig_space()
    fig_costs()
    fig_reach_cost()
    fig_span_ceiling()
    fig_cutoff_threshold()
    fig_dfs_colors()
    fig_worker()
    print("ok")
