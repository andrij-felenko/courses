# -*- coding: utf-8 -*-
"""Фігури для статті «Шар трансляції флешу (FTL)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#e8f5ee"
GRAY_FILL = "#eceff1"
HOT_FILL = "#fdecea"


def cell(x, y, w, h, label, kind="free", size=11):
    styles = {
        "valid": (GREEN_FILL, FIELD, INK),
        "new":   (GREEN_FILL, FIELD, INK),
        "invalid": (GRAY_FILL, MUTED, MUTED),
        "free":  (BG, LINE, MUTED),
        "data":  (FILL, LINE, INK),
        "hot":   (HOT_FILL, POS, INK),
    }
    fill, stroke, color = styles.get(kind, (FILL, LINE, INK))
    return fitbox(x, y, w, h, label, size=size, fill=fill, stroke=stroke, color=color)


# ───────────────────────────────────────────────────────────────────────────
# Фігура 1 — непряма адресація й запис не на місце
# ───────────────────────────────────────────────────────────────────────────
def fig_indirection():
    W, H = 900, 470
    f = []

    f.append(textbox(120, 60, "OS: масив\nлогічних секторів", size=13, bold=True)[0])
    f.append(textbox(410, 60, "Таблиця відображення\nLPN → PPN", size=13, bold=True)[0])
    f.append(textbox(730, 60, "Фізичний флеш\n(сторінки)", size=13, bold=True)[0])

    # логічні сектори
    logical = [("LBA 4", False), ("LBA 5", True), ("LBA 6", False), ("LBA 7", False)]
    ly0 = 120
    for i, (lab, hot) in enumerate(logical):
        cy = ly0 + i * 62
        f.append(cell(55, cy - 20, 130, 40, lab, "hot" if hot else "data", size=13))
    f.append(text(120, 380, "OS пише «нову версію LBA 5»", size=11, color=POS))
    f.append(text(120, 396, "і нічого не знає про фізику", size=11, color=MUTED))

    # таблиця відображення
    rows = ["LPN 4  →  P7", "LPN 5  →  P3", "LPN 6  →  P5", "LPN 7  →  P8"]
    my0 = 120
    for i, r in enumerate(rows):
        cy = my0 + i * 62
        f.append(cell(300, cy - 22, 220, 44, r, "hot" if i == 1 else "data", size=13))
    f.append(text(410, 380, "оновлення = переставити", size=11, color=INK))
    f.append(text(410, 396, "один вказівник (P0 → P3)", size=11, color=POS))

    # фізична сітка 3×4
    cw, ch, gap = 62, 44, 12
    gx = 640
    gy = 116
    def gpos(col, row):
        return gx + col * (cw + gap), gy + row * (ch + gap)
    layout = {
        (0, 0): ("P0\nv1 ✗", "invalid"),
        (0, 1): ("P3\nv2", "new"),
        (0, 2): ("вільна", "free"),
        (0, 3): ("вільна", "free"),
        (1, 0): ("дані", "data"),
        (1, 1): ("дані", "data"),
        (1, 2): ("вільна", "free"),
        (1, 3): ("вільна", "free"),
        (2, 0): ("дані", "data"),
        (2, 1): ("дані", "data"),
        (2, 2): ("вільна", "free"),
        (2, 3): ("вільна", "free"),
    }
    for (col, row), (lab, kind) in layout.items():
        x, y = gpos(col, row)
        f.append(cell(x, y, cw, ch, lab, kind, size=10))

    # стрілки: LBA5 → рядок LPN5 → сторінка P3 (нова, суцільна);  старий вказівник → P0 (пунктир)
    f.append(arrow(190, 182, 297, 182, color=POS, sw=2))          # LBA5 → LPN5
    nx, ny = gpos(0, 1)
    f.append(arrow(523, 182, nx - 3, ny + ch / 2, color=POS, sw=2))  # LPN5 → P3
    ox, oy = gpos(0, 0)
    f.append(('<line x1="523" y1="168" x2="%.0f" y2="%.0f" stroke="%s" '
              'stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#arrow)"/>'
              % (ox - 3, oy + ch / 2, MUTED)))                      # старий → P0
    f.append(text(568, 150, "старий вказівник", size=10, color=MUTED))

    render(os.path.join(IMG, "indirection.svg"), W, H, *f,
           title="Один трюк: запис не на місце через таблицю відображення")


# ───────────────────────────────────────────────────────────────────────────
# Фігура 2 — гранулярність відображення
# ───────────────────────────────────────────────────────────────────────────
def fig_granularity():
    W, H = 960, 470
    f = []

    # три панелі-роздільники
    f.append(line(320, 70, 320, 430, color="#d8dee4", sw=1.2))
    f.append(line(640, 70, 640, 430, color="#d8dee4", sw=1.2))

    # ── A: посторінкове ──
    f.append(textbox(165, 62, "Посторінкове", size=14, bold=True)[0])
    for i in range(5):
        y = 100 + i * 40
        f.append(cell(40, y, 108, 32, "LPN %d→P" % i, "data", size=10))
        f.append(cell(196, y, 90, 32, "сторінка", "valid", size=10))
        f.append(arrow(150, y + 16, 194, y + 16, color=LINE, sw=1.3))
    f.append(fitbox(40, 316, 246, 42,
                    "1 запис на КОЖНУ сторінку", size=11, fill=HOT_FILL, stroke=POS))
    f.append(text(165, 384, "гнучко, дешеве оновлення", size=11, color=FIELD))
    f.append(text(165, 404, "але таблиця величезна:", size=11, color=INK))
    f.append(text(165, 421, "1 ТБ ⇒ ~1 ГБ карти", size=11, color=POS))

    # ── B: поблокове ──
    f.append(textbox(480, 62, "Поблокове", size=14, bold=True)[0])
    for i in range(2):
        y = 108 + i * 96
        f.append(cell(360, y + 28, 104, 32, "LBN %d→B" % i, "data", size=10))
        bx = 512
        f.append(('<rect x="%d" y="%d" width="112" height="76" rx="6" fill="none" '
                  'stroke="%s" stroke-width="1.6"/>' % (bx, y, LINE)))
        for j in range(3):
            f.append(cell(bx + 8, y + 6 + j * 22, 96, 18,
                          "сторінка", "valid" if not (i == 0 and j == 1) else "invalid", size=9))
        f.append(arrow(466, y + 44, 510, y + 30, color=LINE, sw=1.3))
    f.append(fitbox(360, 316, 264, 42,
                    "1 запис на БЛОК — карта крихітна", size=11, fill=GREEN_FILL, stroke=FIELD))
    f.append(text(480, 384, "оновлення 1 сторінки ⇒", size=11, color=POS))
    f.append(text(480, 404, "прочитати-стерти-переписати", size=11, color=POS))
    f.append(text(480, 421, "весь блок", size=11, color=POS))

    # ── C: гібридне ──
    f.append(textbox(795, 62, "Гібридне (кешоване)", size=13, bold=True)[0])
    f.append(fitbox(690, 110, 210, 70,
                    "Повна карта\nживе на флеші", size=12, fill=FILL, stroke=LINE))
    f.append(arrow(795, 184, 795, 214, color=NEG, sw=1.8))
    f.append(fitbox(700, 216, 190, 58,
                    "RAM-кеш\nгарячих записів", size=12, fill=GREEN_FILL, stroke=FIELD))
    f.append(fitbox(690, 300, 210, 58,
                    "мала RAM — майже\nгнучкість посторінкового", size=11,
                    fill=HOT_FILL, stroke=POS))

    render(os.path.join(IMG, "mapping-granularity.svg"), W, H, *f,
           title="Наскільки дрібно відображати: розмір карти проти ціни оновлення")


# ───────────────────────────────────────────────────────────────────────────
# Фігура 3 — збирання сміття (GC)
# ───────────────────────────────────────────────────────────────────────────
def fig_gc():
    W, H = 960, 430
    f = []

    def block(x, y, title, pages, title_color=INK):
        out = [text(x + 62, y - 12, title, size=12, bold=True, color=title_color)]
        out.append('<rect x="%d" y="%d" width="124" height="%d" rx="8" fill="none" '
                   'stroke="%s" stroke-width="1.8"/>' % (x, y, len(pages) * 32 + 12, LINE))
        for j, (lab, kind) in enumerate(pages):
            out.append(cell(x + 10, y + 8 + j * 32, 104, 26, lab, kind, size=10))
        return out

    # блок-жертва
    f += block(60, 110, "Блок-жертва", [
        ("чинна", "valid"), ("застаріла ✗", "invalid"),
        ("чинна", "valid"), ("застаріла ✗", "invalid")])

    f.append(arrow(196, 172, 300, 172, color=FIELD, sw=2))
    f.append(text(248, 156, "копіюємо лише", size=11, color=FIELD))
    f.append(text(248, 196, "чинні сторінки", size=11, color=FIELD))

    # вільний блок приймає копії
    f += block(312, 110, "Вільний блок", [
        ("чинна (копія)", "valid"), ("чинна (копія)", "valid"),
        ("вільна", "free"), ("вільна", "free")])

    f.append(arrow(448, 172, 560, 172, color=POS, sw=2))
    f.append(text(504, 156, "стираємо весь", size=11, color=POS))
    f.append(text(504, 196, "блок-жертву", size=11, color=POS))

    # стертий блок повернуто в пул
    f += block(572, 110, "Стертий блок", [
        ("вільна", "free"), ("вільна", "free"),
        ("вільна", "free"), ("вільна", "free")], title_color=FIELD)

    f.append(arrow(708, 172, 792, 172, color=LINE, sw=1.6))
    f.append(fitbox(796, 138, 150, 66,
                    "повернуто\nу пул вільних", size=12, fill=GREEN_FILL, stroke=FIELD))

    f.append(fitbox(150, 300, 660, 44,
                    "Скопійовані чинні сторінки — це ЗАЙВІ записи понад ті, що замовила OS: підсилення запису (WA).",
                    size=12, fill=HOT_FILL, stroke=POS))

    render(os.path.join(IMG, "garbage-collection.svg"), W, H, *f,
           title="Збирання сміття: звільнити блок коштує копіювань")


# ───────────────────────────────────────────────────────────────────────────
# Фігура 4 — шлях одного запису крізь код симулятора (вставка proj-ftl-sim-c)
# ───────────────────────────────────────────────────────────────────────────
def fig_write_path():
    W, H = 1000, 620
    f = []

    f.append(text(250, 58, "Головний шлях: ftl_write()", size=14, bold=True))
    f.append(text(750, 58, "Підпрограма: gc_run()", size=14, bold=True))

    MX, MW, MC = 80, 340, 250
    GX, GW, GC_ = 560, 380, 750

    main = [
        ("ftl_write(lpn, data)", "hot"),
        ("while (freetop <= GC_LOW)\ngc_run();", "data"),
        ("old = map[lpn]\n⚠ читати ТІЛЬКИ після gc_run()", "hot"),
        ("new = alloc_page()\n(може зняти блок із пулу)", "data"),
        ("flash_program(new, data)\nhost_w++    flash_w++", "valid"),
        ("map[lpn] = new", "valid"),
        ("pstate[old] = P_INVALID\ninvalid_cnt[old / PPB]++", "invalid"),
    ]
    for i, (s, kind) in enumerate(main):
        y = 84 + i * 76
        f.append(cell(MX, y, MW, 52, s, kind, size=12))
        if i < len(main) - 1:
            f.append(arrow(MC, y + 52, MC, y + 76, color=LINE, sw=1.6))

    gc = [
        ("v = pick_victim()\nблок із найбільшим invalid_cnt", "data"),
        ("для кожної ЧИННОЇ сторінки блоку:\ndst = alloc_page();  map[powner]=dst", "data"),
        ("flash_w++    gc_copies++\n⚠ записи, яких хост НЕ просив", "hot"),
        ("стерти весь блок v\nerase_cnt[v]++", "valid"),
        ("push_free(v)\nблок повертається в пул", "valid"),
    ]
    for i, (s, kind) in enumerate(gc):
        y = 160 + i * 76
        f.append(cell(GX, y, GW, 52, s, kind, size=11))
        if i < len(gc) - 1:
            f.append(arrow(GC_, y + 52, GC_, y + 76, color=LINE, sw=1.6))

    # головний шлях → GC
    f.append(arrow(MX + MW, 186, GX - 2, 186, color=LINE, sw=1.8))
    f.append(text(489, 172, "пул майже порожній", size=10, color=POS))

    # повернення з GC назад у головний шлях (пунктиром)
    f.append('<polyline points="558,490 500,490 500,262 424,262" fill="none" '
             'stroke="%s" stroke-width="1.6" stroke-dasharray="5 4" '
             'marker-end="url(#arrow)"/>' % MUTED)

    f.append(fitbox(560, 528, 380, 64,
                    "WA = flash_w / host_w\nчисельник росте у ДВОХ місцях: тут і в gc_run()",
                    size=12, fill=HOT_FILL, stroke=POS))

    render(os.path.join(IMG, "ftl-write-path.svg"), W, H, *f,
           title="Шлях одного запису крізь симулятор: звідки беруться зайві записи")


# ───────────────────────────────────────────────────────────────────────────
# Фігура 5 — WA проти надлишку місткості: теорія vs виміряне
# ───────────────────────────────────────────────────────────────────────────
def _theory_wa(op_pct):
    """Асимптотична WA для рівномірного випадкового запису з жадібним GC.
    ρ = (δ−1)/ln δ,  WA = 1/(1−δ), де ρ = логічних/фізичних = 100/(100+OP)."""
    import math
    rho = 100.0 / (100.0 + op_pct)
    lo, hi = 1e-9, 1.0 - 1e-12
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if (mid - 1.0) / math.log(mid) < rho:
            lo = mid
        else:
            hi = mid
    return 1.0 / (1.0 - (lo + hi) / 2.0)


# виміряно симулятором (256 блоків × 64 сторінки, усталений режим)
OPS = [7, 14, 28, 50, 100]
WA_UNIFORM = [8.29, 4.35, 2.50, 1.72, 1.26]
WA_HOTCOLD = [9.50, 5.42, 3.37, 2.39, 1.64]


def fig_wa_curve():
    W, H = 940, 560
    X0, X1 = 120, 800
    Y0, Y1 = 92, 440
    WA_MAX = 10.0
    f = []

    def xp(op):
        return X0 + (op / 105.0) * (X1 - X0)

    def yp(wa):
        return Y1 - ((wa - 1.0) / (WA_MAX - 1.0)) * (Y1 - Y0)

    # сітка + осі
    for wa in (1, 2, 4, 6, 8, 10):
        f.append(line(X0, yp(wa), X1, yp(wa), color="#e6eaee", sw=1))
        f.append(text(X0 - 18, yp(wa) + 4, "%d" % wa, size=11, color=MUTED, anchor="end"))
    for op in (7, 14, 28, 50, 75, 100):
        f.append(line(xp(op), Y0, xp(op), Y1, color="#f0f3f5", sw=1))
        f.append(text(xp(op), Y1 + 22, "%d%%" % op, size=11, color=MUTED))
    f.append(line(X0, Y0, X0, Y1, color=INK, sw=1.6))
    f.append(line(X0, Y1, X1, Y1, color=INK, sw=1.6))
    f.append(text(X0 - 62, (Y0 + Y1) / 2, "WA", size=13, bold=True, color=INK))
    f.append(text((X0 + X1) / 2, Y1 + 52, "надлишок місткості (over-provisioning), % понад логічну",
                  size=12, color=INK))

    # теоретична крива
    pts = []
    op = 5.0
    while op <= 105.0:
        wa = _theory_wa(op)
        if wa <= WA_MAX:
            pts.append("%.1f,%.1f" % (xp(op), yp(wa)))
        op += 0.5
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
             'stroke-dasharray="6 4"/>' % (" ".join(pts), MUTED))

    # виміряне: рівномірне випадкове
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join("%.1f,%.1f" % (xp(o), yp(w)) for o, w in zip(OPS, WA_UNIFORM)), NEG))
    for o, w in zip(OPS, WA_UNIFORM):
        f.append(circle(xp(o), yp(w), 5, fill=BG, stroke=NEG, sw=2.2))

    # виміряне: гаряче/холодне
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join("%.1f,%.1f" % (xp(o), yp(w)) for o, w in zip(OPS, WA_HOTCOLD)), POS))
    for o, w in zip(OPS, WA_HOTCOLD):
        f.append(rect(xp(o) - 5, yp(w) - 5, 10, 10, fill=BG, stroke=POS, sw=2.2, rx=1))

    # легенда — у порожньому правому верхньому куті
    lx, ly = 470, 112
    f.append(rect(lx, ly, 322, 96, fill=BG, stroke="#d8dee4", sw=1.2, rx=6))
    f.append(line(lx + 16, ly + 24, lx + 52, ly + 24, color=MUTED, sw=2, dash="6 4"))
    f.append(text(lx + 62, ly + 28, "теорія (асимптотика, рівномірне)", size=11,
                  color=INK, anchor="start"))
    f.append(line(lx + 16, ly + 52, lx + 52, ly + 52, color=NEG, sw=2.2))
    f.append(circle(lx + 34, ly + 52, 5, fill=BG, stroke=NEG, sw=2.2))
    f.append(text(lx + 62, ly + 56, "симулятор: рівномірне випадкове", size=11,
                  color=INK, anchor="start"))
    f.append(line(lx + 16, ly + 80, lx + 52, ly + 80, color=POS, sw=2.2))
    f.append(rect(lx + 29, ly + 75, 10, 10, fill=BG, stroke=POS, sw=2.2, rx=1))
    f.append(text(lx + 62, ly + 84, "симулятор: 90 % записів у 10 % адрес", size=11,
                  color=INK, anchor="start"))

    # виноска про локальність — біля точки OP=28 %
    f.append(line(xp(28) + 8, yp(3.37), 448, 300, color=POS, sw=1.2, dash="4 3"))
    f.append(fitbox(452, 268, 300, 64,
                    "Локальність робить ГІРШЕ:\n2.50 → 3.37 (+35 %) за того самого OP",
                    size=11, fill=HOT_FILL, stroke=POS))

    render(os.path.join(IMG, "wa-vs-op.svg"), W, H, *f,
           title="Підсилення запису проти надлишку місткості: виміряно й звірено з теорією")


# ───────────────────────────────────────────────────────────────────────────
# Фігура 6 — розкид зносу по блоках
# ───────────────────────────────────────────────────────────────────────────
BIN_LO, BIN_W = 16, 4
HIST_UNIFORM = [0, 0, 157, 97, 0, 0, 0, 0, 0, 0, 0]
HIST_HOTCOLD = [2, 17, 35, 65, 46, 31, 28, 16, 10, 2, 2]


def fig_erase_spread():
    W, H = 960, 470
    f = []
    CNT_MAX = 170.0
    PW = 360
    PH = 250

    def panel(px, title, hist, note, note_kind):
        out = [text(px + PW / 2, 62, title, size=13, bold=True)]
        py0, py1 = 92, 92 + PH
        # осі
        out.append(line(px, py1, px + PW, py1, color=INK, sw=1.5))
        out.append(line(px, py0, px, py1, color=INK, sw=1.5))
        bw = PW / float(len(hist))
        for i, c in enumerate(hist):
            if c == 0:
                continue
            h = (c / CNT_MAX) * PH
            bx = px + i * bw + 3
            out.append(rect(bx, py1 - h, bw - 6, h, fill=GREEN_FILL if note_kind == "ok"
                            else HOT_FILL, stroke=FIELD if note_kind == "ok" else POS,
                            sw=1.4, rx=2))
            out.append(text(bx + (bw - 6) / 2, py1 - h - 8, "%d" % c, size=10, color=MUTED))
        for i in (0, 2, 4, 6, 8, 10):
            out.append(text(px + i * bw, py1 + 20, "%d" % (BIN_LO + i * BIN_W),
                            size=10, color=MUTED))
        out.append(text(px + PW / 2, py1 + 46, "стирань блоку за прогін", size=11, color=INK))
        out.append(fitbox(px + 20, 384, PW - 40, 52, note, size=11,
                          fill=GREEN_FILL if note_kind == "ok" else HOT_FILL,
                          stroke=FIELD if note_kind == "ok" else POS))
        return out

    f += panel(80, "Рівномірне випадкове",
               HIST_UNIFORM,
               "Розкид 24…30 — жадібний GC\nвирівняв знос сам, задарма", "ok")
    f += panel(540, "90 % записів у 10 % адрес",
               HIST_HOTCOLD,
               "Розкид 17…59 — 3.5× між блоками.\nОсь звідки потреба у wear leveling", "bad")

    f.append(text(40, 100, "блоків", size=11, color=MUTED, anchor="start"))
    f.append(text(500, 100, "блоків", size=11, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "erase-spread.svg"), W, H, *f,
           title="Знос по блоках: те саме залізо, той самий GC, різні навантаження")


# ───────────────────────────────────────────────────────────────────────────
# Фігура 7 (вставка hist-ftl-birth) — дві школи й дорога до стандарту
# ───────────────────────────────────────────────────────────────────────────
SIL_FILL = "#eaf0fd"   # кремнієва школа


def fig_two_schools():
    W, H = 1000, 1010
    f = []

    LX, LW = 60, 340          # ліва колонка
    RX, RW = 600, 350         # права колонка
    AX = 500                  # вісь часу

    f.append(fitbox(LX, 52, LW, 46,
                    "Кремнієва школа — SanDisk\n«контролер на картці»",
                    size=13, fill=SIL_FILL, stroke=NEG, bold=True))
    f.append(fitbox(RX, 52, RW, 46,
                    "Системна школа — M-Systems\n«розум у драйвері»",
                    size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))

    rows = [
        ("1988",       "L", "Засновано SanDisk (SunDisk):\nГарарі, Мегротра, Юань", "sil"),
        ("1989 квіт.", "L", "Пріоритет US 5,297,148 (Гарарі й ін.):\nконтролер + флеш = «твердотілий диск»", "sil"),
        ("1989",       "R", "Засновано M-Systems:\nМоран і Мергі", "sys"),
        ("1991",       "L", "Перший комерційний знімний\nATA-флеш-диск, 20 МБ", "sil"),
        ("",           "C", "1991 жовт. — Sprite LFS, Розенблюм і Оустергаут (SOSP): журнал + індекс + чистильник.\n"
                            "Той самий кістяк, інша причина: не фізика флешу, а їзда голівки диска.", "aside"),
        ("~1992",      "R", "У M-Systems приходить Амір Бан:\nзадачу переставлено з файлів на сектори", "sys"),
        ("1992 лип.",  "R", "TrueFFS показано на PC-Card Expo,\nСанта-Клара (джерело однокорінне)", "sys"),
        ("1992 лист.", "L", "PC Card ATA — у стандарті PCMCIA 2.01\n(дорога SanDisk увійшла першою)", "std"),
        ("1993 бер.",  "R", "Заявка US 5,404,485 «Flash file system»,\nєдиний винахідник — Амір Бан", "sys"),
        ("1994",       "L", "CompactFlash: ATA-контролер\nпрямо на картці", "sil"),
        ("1995 квіт.", "R", "Патент US 5,404,485 видано\n(збіг 2013 року)", "sys"),
        ("1996 бер.",  "R", "FTL — у стандарті PC Card 5.04.\nНазву «Flash Translation Layer» дав комітет", "std"),
    ]

    styles = {
        "sil":   (SIL_FILL, NEG),
        "sys":   (GREEN_FILL, FIELD),
        "std":   (HOT_FILL, POS),
        "aside": (FILL, MUTED),
    }

    # спершу розкладка по y — щоб вісь не пройшла крізь текст рядка «aside»
    y = 126
    placed = []
    aside_band = None
    for year, side, label, st in rows:
        h = 50
        placed.append((year, side, label, st, y, h))
        if side == "C":
            aside_band = (y - 8, y + h + 8)
        y += h + 16
    bottom = y - 16

    if aside_band:
        f.append(line(AX, 110, AX, aside_band[0], color="#d8dee4", sw=2))
        f.append(line(AX, aside_band[1], AX, bottom, color="#d8dee4", sw=2))
    else:
        f.append(line(AX, 110, AX, bottom, color="#d8dee4", sw=2))

    for year, side, label, st, y, h in placed:
        fill, stroke = styles[st]
        cy = y + h / 2.0
        if side == "C":
            f.append(fitbox(LX, y, RX + RW - LX, h, label, size=12, fill=fill, stroke=stroke))
        elif side == "L":
            f.append(fitbox(LX, y, LW, h, label, size=12, fill=fill, stroke=stroke))
            f.append(line(LX + LW + 4, cy, AX - 44, cy, color=stroke, sw=1.4))
            f.append(text(AX, cy + 4, year, size=12, bold=True, color=INK))
        else:
            f.append(fitbox(RX, y, RW, h, label, size=12, fill=fill, stroke=stroke))
            f.append(line(RX - 4, cy, AX + 44, cy, color=stroke, sw=1.4))
            f.append(text(AX, cy + 4, year, size=12, bold=True, color=INK))

    f.append(fitbox(LX, bottom + 24, RX + RW - LX, 46,
                    "Червоне — рішення комітету PCMCIA: обидві школи ввійшли в ОДИН стандарт,\n"
                    "різними дверима й у різні роки.",
                    size=12, fill=HOT_FILL, stroke=POS))

    render(os.path.join(IMG, "two-schools.svg"), W, H, *f,
           title="Дві школи однієї задачі: як зробити флеш схожим на диск")


# ───────────────────────────────────────────────────────────────────────────
# Фігура 8 (вставка hist-ftl-birth) — куди переїхав FTL
# ───────────────────────────────────────────────────────────────────────────
def fig_ftl_moved():
    W, H = 980, 470
    f = []

    f.append(textbox(255, 76, "1992–1996: розум на хості", size=14, bold=True)[0])
    f.append(textbox(725, 76, "Сьогодні: розум у контролері", size=14, bold=True)[0])

    # роздільник — двома відрізками, щоб стрілка «переїзду» пройшла чисто
    f.append(line(490, 108, 490, 176, color="#d8dee4", sw=1.2))
    f.append(line(490, 226, 490, 372, color="#d8dee4", sw=1.2))

    # ліва колонка — розум на хості
    f.append(fitbox(85, 108, 340, 44, "DOS + FAT", size=13, fill=FILL, stroke=LINE))
    f.append(arrow(255, 154, 255, 172, color=LINE, sw=1.6))
    f.append(fitbox(85, 174, 340, 50, "Драйвер FTL (TrueFFS) на хості",
                    size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))
    f.append(arrow(255, 226, 255, 244, color=LINE, sw=1.6))
    f.append(fitbox(85, 246, 340, 50, "Лінійна NOR-картка:\nсамі мікросхеми, без розуму",
                    size=12, fill=BG, stroke=LINE))
    f.append(text(255, 324, "Картка дурна, чужа й дешева.", size=11, color=MUTED))
    f.append(text(255, 344, "Брехню веде програма на комп'ютері.", size=11, color=MUTED))

    # права колонка — розум у контролері
    f.append(fitbox(555, 108, 340, 44, "ОС + файлова система", size=13, fill=FILL, stroke=LINE))
    f.append(arrow(725, 154, 725, 172, color=LINE, sw=1.6))
    f.append(fitbox(555, 174, 340, 50, "Контролер: прошивка з FTL",
                    size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))
    f.append(arrow(725, 226, 725, 244, color=LINE, sw=1.6))
    f.append(fitbox(555, 246, 340, 50, "NAND-мікросхеми\nвсередині коробки",
                    size=12, fill=BG, stroke=LINE))
    f.append(text(725, 324, "Носій ззовні — звичайний диск.", size=11, color=MUTED))
    f.append(text(725, 344, "Брехню веде він сам, хост не знає.", size=11, color=MUTED))

    # переїзд
    f.append(text(490, 190, "переїхав", size=11, bold=True, color=POS))
    f.append(arrow(429, 202, 551, 202, color=POS, sw=2))

    f.append(fitbox(90, 392, 800, 54,
                    "Місце програло: розум переїхав усередину носія — туди, куди його від початку клала кремнієва школа.\n"
                    "Алгоритм переміг: у тому контролері працює дисципліна, яку склала системна.",
                    size=12, fill=HOT_FILL, stroke=POS))

    render(os.path.join(IMG, "ftl-moved.svg"), W, H, *f,
           title="Куди переїхав FTL: назва й алгоритм лишилися, місце змінилося")


if __name__ == "__main__":
    fig_indirection()
    fig_granularity()
    fig_gc()
    fig_write_path()
    fig_wa_curve()
    fig_erase_spread()
    fig_two_schools()
    fig_ftl_moved()
    print("OK: figures written to", IMG)
