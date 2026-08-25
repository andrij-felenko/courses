# -*- coding: utf-8 -*-
"""Фігури до теми «Шрифти».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GRID = "#e2e5e9"   # тонка сітка клітинок
DARK = "#2b2f33"   # «чорний» піксель гліфа
HALF = "#b7bcc1"   # напівтон для згладжування

# Растрова «A» 8×8 (рядки згори вниз, 1 = піксель залитий) ───────────────────
A8 = [
    "00011000",
    "00011000",
    "00100100",
    "00100100",
    "01111110",
    "01000010",
    "01000010",
    "01000010",
]


def cell_grid(f, x0, y0, n, m, c=GRID, sw=1.0):
    """Порожня сітка n×m клітинок по c пікселів від (x0,y0)."""
    for r in range(m):
        for col in range(n):
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                     'fill="none" stroke="%s" stroke-width="%.1f"/>'
                     % (x0 + col * c, y0 + r * c, c, c, GRID, sw))


def fill_cell(f, x0, y0, col, r, c, color=DARK):
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="%s" '
             'stroke-width="0.4"/>' % (x0 + col * c, y0 + r * c, c, c, color, color))


def letter_A_outline(f, cx, top, h, color=INK, sw=2.5, dots=True):
    """Контур літери «A» трьома штрихами + вузлові точки (зелені)."""
    half = h * 0.40
    apex = (cx, top)
    lft = (cx - half, top + h)
    rgt = (cx + half, top + h)
    midL = (cx - half * 0.45, top + h * 0.62)
    midR = (cx + half * 0.45, top + h * 0.62)
    f.append(line(apex[0], apex[1], lft[0], lft[1], color=color, sw=sw))
    f.append(line(apex[0], apex[1], rgt[0], rgt[1], color=color, sw=sw))
    f.append(line(midL[0], midL[1], midR[0], midR[1], color=color, sw=sw))
    if dots:
        for (px, py) in (apex, lft, rgt, midL, midR):
            f.append(circle(px, py, 4, fill=BG, stroke=FIELD, sw=1.8))


# ── 1. Гліф: пікселі проти контуру (результат проти рецепта) ─────────────────
def fig_glyph():
    W, H = 760, 340
    f = [text(W / 2, 30, "Гліф двома способами: готові пікселі проти контуру", size=16, bold=True)]

    # ліворуч — бітмап
    c = 22
    gx, gy = 96, 80
    f.append(text(gx + 4 * c, 66, "БІТМАП", size=13, bold=True))
    cell_grid(f, gx, gy, 8, 8, c)
    for r, rowbits in enumerate(A8):
        for col, b in enumerate(rowbits):
            if b == "1":
                fill_cell(f, gx, gy, col, r, c)
    f.append(text(gx + 4 * c, gy + 8 * c + 22, "готова сітка пікселів", size=11, color=MUTED))
    f.append(text(gx + 4 * c, gy + 8 * c + 40, "(один конкретний розмір)", size=10.5, color=MUTED))

    # праворуч — вектор
    vx = 560
    f.append(text(vx, 66, "ВЕКТОР", size=13, bold=True))
    letter_A_outline(f, vx, gy + 6, 8 * c - 12)
    f.append(text(vx, gy + 8 * c + 22, "контур із точок і кривих", size=11, color=MUTED))
    f.append(text(vx, gy + 8 * c + 40, "(будь-який розмір)", size=10.5, color=FIELD, bold=True))

    f.append(text(W / 2, H - 14,
                  "Бітмап зберігає результат — намальовані пікселі; вектор зберігає рецепт — геометрію форми.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "glyph.svg"), W, H, *f)


# ── 2. Бітмапний шрифт: кожен розмір — окремий набір ─────────────────────────
def fig_bitmap_sizes():
    W, H = 820, 330
    f = [text(W / 2, 30, "Бітмапний шрифт: кожен розмір зберігають окремо", size=16, bold=True)]

    def draw_A(x0, y0, c, color=DARK):
        cell_grid(f, x0, y0, 8, 8, c)
        for r, rowbits in enumerate(A8):
            for col, b in enumerate(rowbits):
                if b == "1":
                    fill_cell(f, x0, y0, col, r, c, color)

    # три «свої блоки» різних кеглів
    f.append(text(112, 78, "малий", size=11, bold=True))
    draw_A(80, 88, 8)
    f.append(text(112, 88 + 8 * 8 + 16, "свій блок", size=10, color=MUTED))

    f.append(text(290, 78, "середній", size=11, bold=True))
    draw_A(256, 88, 13)
    f.append(text(290, 88 + 8 * 13 + 16, "свій блок", size=10, color=MUTED))

    f.append(text(470, 78, "великий", size=11, bold=True))
    draw_A(424, 88, 18)
    f.append(text(470, 88 + 8 * 18 + 16, "свій блок", size=10, color=MUTED))

    f.append(text(285, 300, "кожен кегль — окремий набір гліфів → Flash множиться",
                  size=11, color=INK))

    # праворуч — спроба масштабувати малий: блочно
    f.append(text(680, 78, "малий × масштаб", size=10.5, bold=True, color=POS))
    draw_A(632, 96, 18, color="#9aa0a4")
    f.append(text(680, 96 + 8 * 18 + 16, "= блочно, погано", size=10, color=POS))

    f.append(text(W / 2, H - 12,
                  "Бітмап тривіально малювати, та один збережений розмір не перетворити гладко на інший.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "bitmap-sizes.svg"), W, H, *f)


# ── 3. Векторний шрифт: один контур → будь-який розмір ───────────────────────
def fig_vector_scale():
    W, H = 820, 320
    f = [text(W / 2, 30, "Векторний шрифт: один контур растеризують у будь-який розмір",
              size=16, bold=True)]

    # джерело — контур
    letter_A_outline(f, 150, 86, 150)
    f.append(text(150, 256, "один опис контуру", size=10.5, bold=True))

    f.append(arrow(228, 160, 300, 160, color=INK, sw=2))
    f.append(text(264, 150, "растеризувати", size=9.5, color=FIELD))

    # три кеглі, всі гладкі (суцільні штрихи без вузлів)
    for cx, h, lbl in ((360, 84, "16 px"), (510, 116, "24 px"), (660, 150, "32 px")):
        letter_A_outline(f, cx, 246 - h, h, color=INK, sw=2.2, dots=False)
        f.append(text(cx, 262, lbl, size=10.5, bold=True, color=FIELD))

    f.append(text(W / 2, H - 12,
                  "З однієї геометрії малюють будь-який кегль, і всі гладкі. Ціна — потрібен растеризатор (код, час CPU, RAM).",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "vector-scale.svg"), W, H, *f)


# ── 4. 1 біт проти згладжування ──────────────────────────────────────────────
def fig_aa():
    W, H = 800, 320
    f = [text(W / 2, 30, "Косий штрих: один біт на піксель проти кількох біт зі згладжуванням",
              size=16, bold=True)]

    c = 26
    n = 8
    # діагональний штрих згори-праворуч до низу-ліворуч (рядок r → стовпець n-1-r)
    def stair(x0, y0, aa=False):
        cell_grid(f, x0, y0, n, n, c)
        for r in range(n):
            col = n - 1 - r
            fill_cell(f, x0, y0, col, r, c, DARK)
            if aa:
                # напівтонові сусіди вздовж сходинки пом'якшують край
                if col - 1 >= 0:
                    fill_cell(f, x0, y0, col - 1, r, c, HALF)
                if r + 1 < n:
                    fill_cell(f, x0, y0, col, r + 1, c, HALF)

    # ліворуч: 1 біт
    lx, ly = 96, 84
    f.append(text(lx + n * c / 2, 74, "1 біт — різко", size=11.5, bold=True))
    stair(lx, ly, aa=False)
    f.append(text(lx + n * c / 2, ly + n * c + 18, "сходинки видно", size=10, color=POS))

    # праворуч: 4 біти АА
    rx = 472
    f.append(text(rx + n * c / 2, 74, "4 біти — гладко", size=11.5, bold=True))
    stair(rx, ly, aa=True)
    f.append(text(rx + n * c / 2, ly + n * c + 18, "сірі краї обманюють око", size=10, color=FIELD))

    f.append(text(W / 2, H - 12,
                  "Зберігаючи піксель кількома бітами (тут 4 — 16 рівнів сірого), краї роблять плавними. Ціна — більше байтів на гліф.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "aa.svg"), W, H, *f)


# ── 5. Кернінг: пара AV ──────────────────────────────────────────────────────
def fig_kerning():
    W, H = 760, 300
    f = [text(W / 2, 30, "Кернінг: підгін відстані для конкретної пари літер", size=16, bold=True)]

    def AV(x, kern=False):
        # «A»
        h = 76
        top = 96
        ax = x
        f.append(line(ax, top + h, ax + 26, top, color=INK, sw=3))
        f.append(line(ax + 26, top, ax + 52, top + h, color=INK, sw=3))
        f.append(line(ax + 13, top + h * 0.62, ax + 39, top + h * 0.62, color=INK, sw=3))
        # «V», зсунута ближче, якщо kern
        vx = ax + (58 if kern else 82)
        f.append(line(vx, top, vx + 26, top + h, color=INK, sw=3))
        f.append(line(vx + 26, top + h, vx + 52, top, color=INK, sw=3))

    f.append(text(150, 80, "без кернінгу", size=11.5, bold=True))
    AV(96, kern=False)
    f.append(text(160, 200, "велика дірка між A і V", size=10, color=POS))

    f.append(text(540, 80, "з кернінгом", size=11.5, bold=True))
    AV(486, kern=True)
    f.append(text(540, 200, "V підсунули під навислий край A", size=10, color=FIELD))

    f.append(text(W / 2, H - 38,
                  "Окрім ширини кожної літери, гарний шрифт має таблицю поправок для конкретних ПАР (AV, To).",
                  size=11.5, color=INK))
    f.append(text(W / 2, H - 16,
                  "У дрібних embedded-шрифтах цю таблицю часто пропускають заради пам'яті.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "kerning.svg"), W, H, *f)


# ── 6. Вага у Flash: символів × байтів на гліф ───────────────────────────────
def fig_flash():
    W, H = 824, 312
    f = [text(W / 2, 30, "Вага шрифту у Flash = символів × байтів на гліф", size=16, bold=True)]

    cols = [(70, 180, "конфіг"), (250, 130, "байт/гліф"),
            (380, 160, "латиниця ~100"), (540, 170, "+кирилиця ~200")]
    y = 64
    hh = 34
    for (x, w, lbl) in cols:
        f.append(rect(x, y, w, hh, fill="#eef0f2", stroke=MUTED, sw=1.2, rx=0))
        f.append(text(x + w / 2, y + 22, lbl, size=12, bold=True))

    rows = [
        ("16 px · 1 біт", "32", "3.2 КБ", "6.4 КБ", "#e7f5ea", FIELD),
        ("16 px · 4 біти AA", "128", "12.8 КБ", "25.6 КБ", "#fff8e8", "#b07d18"),
        ("48 px · 1 біт", "288", "28 КБ", "56 КБ", "#fff8e8", "#b07d18"),
        ("48 px · 4 біти AA", "1152", "113 КБ", "225 КБ", "#fdeceb", POS),
    ]
    ry = y + hh
    rh = 46
    for (cfg, bpg, lat, cyr, fillc, txtc) in rows:
        f.append(rect(70, ry, 180, rh, fill="#f6f7f8", stroke=MUTED, sw=1.1, rx=0))
        f.append(text(160, ry + rh / 2 + 5, cfg, size=12, bold=True))
        f.append(rect(250, ry, 130, rh, fill=BG, stroke=MUTED, sw=1.1, rx=0))
        f.append(text(315, ry + rh / 2 + 5, bpg, size=12))
        f.append(rect(380, ry, 160, rh, fill=fillc, stroke=MUTED, sw=1.1, rx=0))
        f.append(text(460, ry + rh / 2 + 5, lat, size=12, color=txtc))
        f.append(rect(540, ry, 170, rh, fill=fillc, stroke=MUTED, sw=1.1, rx=0))
        f.append(text(625, ry + rh / 2 + 5, cyr, size=12, color=txtc))
        ry += rh

    f.append(text(W / 2, H - 12,
                  "Великий кегль, згладжування й широкий набір символів накладаються: разом це сотні кілобайтів.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "flash.svg"), W, H, *f)


# ── 7. (детальна) Метрики гліфа відносно курсора на базовій лінії ─────────────
def fig_metrics():
    W, H = 760, 380
    f = [text(W / 2, 30, "Метрики гліфа: де стоїть карта й куди далі рухати курсор",
              size=16, bold=True)]

    baseY = 250          # базова лінія
    penX = 200           # курсор поточного гліфа

    # базова лінія
    f.append(line(70, baseY, W - 60, baseY, color=MUTED, sw=1.4, dash="6,4"))
    f.append(text(W - 56, baseY + 4, "baseline", size=10.5, color=MUTED, anchor="start"))

    # курсор (вертикаль)
    f.append(line(penX, 80, penX, baseY + 60, color=NEG, sw=1.6, dash="3,3"))
    f.append(text(penX, 72, "курсор (pen)", size=10.5, color=NEG, bold=True))

    # карта гліфа — рамка літери «p» (звисає під базову лінію)
    gx = penX + 22       # xOffset > 0
    gtop = baseY - 96    # yOffset (верх над базовою лінією)
    gw, gh = 96, 150     # ширина/висота карти (гліф звисає)
    f.append(rect(gx, gtop, gw, gh, fill="#eef2f8", stroke=INK, sw=1.6, rx=4))
    # схематична «p» всередині: стовбур + вічко
    f.append(line(gx + 22, gtop + 18, gx + 22, gtop + gh - 12, color=DARK, sw=4))
    f.append('<path d="M%.0f,%.0f q40,0 40,34 q0,34 -40,34" fill="none" stroke="%s" stroke-width="4"/>'
             % (gx + 22, gtop + 26, DARK))

    # xOffset
    f.append(arrow(penX, gtop - 14, gx, gtop - 14, color=FIELD, sw=1.6))
    f.append(text((penX + gx) / 2, gtop - 20, "xOffset", size=10, color=FIELD))

    # width
    f.append(arrow(gx, gtop - 32, gx + gw, gtop - 32, color=INK, sw=1.4))
    f.append(text(gx + gw / 2, gtop - 38, "width", size=10, color=INK))

    # yOffset (від базової лінії до верху карти, вгору)
    f.append(arrow(gx + gw + 16, baseY, gx + gw + 16, gtop, color=FIELD, sw=1.6))
    f.append(text(gx + gw + 22, (baseY + gtop) / 2, "yOffset", size=10, color=FIELD, anchor="start"))

    # звис під базову лінію
    f.append(text(gx + gw + 22, gtop + gh - 6, "звис під baseline", size=9.5, color=MUTED, anchor="start"))

    # advance — до наступного курсора
    nextX = penX + 150   # advance > width
    f.append(line(nextX, 80, nextX, baseY + 60, color=NEG, sw=1.6, dash="3,3"))
    f.append(text(nextX, 72, "наступний курсор", size=10.5, color=NEG, bold=True))
    f.append(arrow(penX, baseY + 44, nextX, baseY + 44, color=POS, sw=1.8))
    f.append(text((penX + nextX) / 2, baseY + 60, "advance (крок)", size=10.5, color=POS, bold=True))

    f.append(text(W / 2, H - 12,
                  "Крок (advance) більший за ширину карти на бічні проміжки; xOffset/yOffset зі знаком ставлять карту відносно курсора.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "d-metrics.svg"), W, H, *f)


if __name__ == "__main__":
    fig_glyph()
    fig_bitmap_sizes()
    fig_vector_scale()
    fig_aa()
    fig_kerning()
    fig_flash()
    fig_metrics()
    print("OK: 7 figures ->", IMG)
