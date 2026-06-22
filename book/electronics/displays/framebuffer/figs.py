# -*- coding: utf-8 -*-
"""Фігури до теми «Кадровий буфер».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки заливок понад палітру svgkit (легкі тони рядків/комірок)
ROW0  = "#dfe7f5"; ROW0S = "#7d93c4"   # синюватий рядок
ROW1  = "#dfeede"; ROW1S = "#7daa86"   # зеленуватий рядок
ROW2  = "#fdeede"; ROW2S = "#caa24a"   # теплий рядок
COOL  = "#eef4f8"; WARM  = "#fdeceb"; OKBG = "#e7f5ea"
GREY  = "#8a8a8a"


def title(W, s, size=17):
    return text(W / 2, 30, s, size=size, color=INK, bold=True)

def caption(W, y, s):
    return text(W / 2, y, s, size=11.5, color=MUTED, italic=True)


# ── 1. Лінійна памʼять, складена в рядки екрана ──────────────────────────────
def fig_memory_screen():
    W, H = 820, 360
    f = [title(W, "Кадровий буфер: екран — це масив памʼяті, складений у рядки", 18)]
    # лінійна стрічка з 12 комірок
    f.append(text(70, 84, "лінійна памʼять (адреси →)", size=11, color=GREY, anchor="start", bold=True))
    cw, x0, y0 = 56, 70, 96
    fills = [(ROW0, ROW0S)]*4 + [(ROW1, ROW1S)]*4 + [(ROW2, ROW2S)]*4
    for i in range(12):
        fl, st = fills[i]
        f.append(rect(x0 + i*cw, y0, cw, 30, fill=fl, stroke=st, sw=1.2, rx=0))
        f.append(text(x0 + i*cw + cw/2, y0 + 20, str(i), size=11, color=INK))
    # екран 4×3
    f.append(text(420, 178, "екран 4×3 (той самий масив)", size=11, color=GREY, bold=True))
    gx, gy, gs = 320, 190, 50
    for idx in range(12):
        r, c = divmod(idx, 4)
        fl, st = fills[idx]
        f.append(rect(gx + c*gs, gy + r*gs, gs, gs, fill=fl, stroke=st, sw=1.2, rx=0))
        f.append(text(gx + c*gs + gs/2, gy + r*gs + 30, str(idx), size=12, color=INK, bold=True))
    f.append(text(534, 220, "← рядок 0", size=11, color=ROW0S, anchor="start", bold=True))
    f.append(text(534, 270, "← рядок 1", size=11, color=ROW1S, anchor="start", bold=True))
    f.append(text(534, 320, "← рядок 2", size=11, color=ROW2S, anchor="start", bold=True))
    f.append(line(182, 128, 418, 188, color=ROW0S, sw=1.6, dash="4 3"))
    f.append(caption(W, 346, "Перші W комірок памʼяті = рядок 0 екрана, наступні W = рядок 1, і так далі. Малювати — значить писати в ці комірки."))
    render(os.path.join(IMG, "memory-screen.svg"), W, H, *f)


# ── 2. Адреса пікселя (x, y) ─────────────────────────────────────────────────
def fig_addressing():
    W, H = 820, 360
    f = [title(W, "Адреса пікселя (x, y): рядок за рядком", 18)]
    # сітка 8×6
    cs, gx, gy = 34, 70, 90
    for r in range(6):
        for c in range(8):
            hl = (r == 2 and c == 3)
            f.append(rect(gx + c*cs, gy + r*cs, cs, cs,
                          fill=(FIELD_BG if hl else "#fbfbfb"), stroke=GREY, sw=1, rx=0))
    # відмітка пікселя (3,2)
    px = gx + 3*cs + cs/2
    py = gy + 2*cs + cs/2
    f.append(text(px, py + 6, "•", size=18, color=FIELD, bold=True))
    f.append(text(px, gy - 8, "x=3", size=10, color=FIELD, bold=True))
    f.append(text(gx - 8, py, "y=2", size=10, color=FIELD, anchor="end", bold=True))
    f.append(text(gx + 4*cs, gy + 6*cs + 22, "ширина W = 8", size=11, color=GREY))
    # формули справа
    f.append(text(380, 120, "зсув у масиві:", size=13, color=INK, anchor="start", bold=True))
    f.append(rect(380, 132, 380, 40, fill=COOL, stroke=INK, sw=1.4, rx=6))
    f.append(text(570, 157, "offset = (y·W + x) · байтів_на_піксель", size=13, color=INK, bold=True))
    f.append(text(380, 200, "адреса = база + offset", size=13, color=INK, anchor="start"))
    f.append(text(380, 232, "для (3, 2), W=8, 2 байти/піксель:", size=12, color=GREY, anchor="start"))
    f.append(rect(380, 244, 380, 36, fill=OKBG, stroke=FIELD, sw=1.4, rx=6))
    f.append(text(570, 267, "offset = (2·8 + 3)·2 = 38 байтів", size=13, color=INK, bold=True))
    f.append(caption(W, 332, "Рядки інколи доповнюють до межі — тоді в формулі замість W беруть «крок рядка» (stride)."))
    render(os.path.join(IMG, "addressing.svg"), W, H, *f)


# ── 3. Скільки RAM зʼїдає один кадр (таблиця) ────────────────────────────────
def fig_size():
    W, H = 820, 320
    f = [title(W, "Скільки RAM зʼїдає один кадр = W × H × (біт/піксель ÷ 8)", 16)]
    cols = ["роздільність", "1 біт", "8 біт", "16 біт", "24 біти"]
    xs = [70, 220, 350, 480, 610]
    ws = [150, 130, 130, 130, 130]
    # шапка
    for x, w, c in zip(xs, ws, cols):
        f.append(rect(x, 68, w, 36, fill="#eef0f2", stroke=GREY, sw=1.2, rx=0))
        f.append(text(x + w/2, 90, c, size=12, color=INK, bold=True))
    rows = [
        ("128×64",  ["1.0 КБ", "8 КБ",  "16 КБ",  "24 КБ"]),
        ("320×240", ["9.4 КБ", "75 КБ", "150 КБ", "225 КБ"]),
        ("480×272", ["16 КБ",  "128 КБ","255 КБ", "382 КБ"]),
        ("800×480", ["47 КБ",  "375 КБ","750 КБ", "1.1 МБ"]),
    ]
    y = 104
    for name, vals in rows:
        f.append(rect(xs[0], y, ws[0], 44, fill=COOL, stroke=GREY, sw=1.1, rx=0))
        f.append(text(xs[0] + ws[0]/2, y + 27, name, size=12, color=INK, bold=True))
        for j, v in enumerate(vals):
            big = ("МБ" in v) or (v.endswith("КБ") and _kb(v) >= 100)
            fl = WARM if big else OKBG
            col = POS if big else FIELD
            f.append(rect(xs[j+1], y, ws[j+1], 44, fill=fl, stroke=GREY, sw=1.1, rx=0))
            f.append(text(xs[j+1] + ws[j+1]/2, y + 27, v, size=12, color=col))
        y += 44
    f.append(caption(W, 300, "Глибший колір і більший екран множать памʼять. Часто кадр — найбільший споживач RAM у всьому пристрої."))
    render(os.path.join(IMG, "size.svg"), W, H, *f)

def _kb(s):
    try:
        return float(s.replace("КБ", "").strip())
    except ValueError:
        return 0.0


# ── 4. Малювання — запис у комірку масиву ────────────────────────────────────
def fig_drawing():
    W, H = 820, 330
    f = [title(W, "Малювання — це послідовність записів у масив", 18)]
    f.append(rect(70, 90, 150, 70, fill="#eef2f5", stroke=INK, sw=1.6, rx=6))
    f.append(text(145, 122, "set_pixel(x,y,c)", size=12, color=INK, bold=True))
    f.append(text(145, 142, "«постав піксель»", size=9.5, color=GREY))
    f.append(arrow(220, 125, 280, 125, color=INK, sw=2))
    f.append(rect(280, 90, 160, 70, fill=COOL, stroke=INK, sw=1.6, rx=6))
    f.append(text(360, 118, "адреса =", size=11, color=INK, bold=True))
    f.append(text(360, 136, "база+(y·W+x)·бпп", size=10, color=GREY))
    f.append(arrow(440, 125, 500, 125, color=INK, sw=2))
    cs, x0, y0 = 34, 510, 108
    for i in range(8):
        hl = (i == 3)
        f.append(rect(x0 + i*cs, y0, cs, cs, fill=(FIELD_BG if hl else BG), stroke=GREY, sw=1, rx=0))
    f.append(text(x0 + 3*cs + cs/2, y0 + 22, "c", size=12, color=FIELD, bold=True))
    f.append(text(x0 + 4*cs, y0 - 8, "записати колір у комірку", size=10, color=GREY))
    f.append(text(W/2, 230, "Лінія, текст, картинка — усе зводиться до багатьох таких записів.", size=12, color=INK))
    f.append(text(W/2, 252, "Кадровий буфер дає довільний доступ: торкайся будь-якого пікселя будь-коли,", size=12, color=MUTED, italic=True))
    f.append(text(W/2, 272, "склади все в памʼяті — і виштовхни готовий кадр на екран.", size=12, color=MUTED, italic=True))
    f.append(caption(W, 304, "Саме заради цієї свободи компонувати в памʼяті й тримають кадровий буфер."))
    render(os.path.join(IMG, "drawing.svg"), W, H, *f)


# ── 5. Пакування: менше за байт проти цілих байтів ──────────────────────────
def fig_packing():
    W, H = 820, 330
    f = [title(W, "Біт на піксель: коли піксель менший за байт", 18)]
    # 1 біт/піксель: байт = 8 бітів
    f.append(text(120, 92, "1 біт/піксель", size=13, color=INK, bold=True))
    bw, bx, by = 16, 60, 104
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    for i, b in enumerate(bits):
        fl = INK if b else BG
        f.append(rect(bx + i*bw, by, bw, 26, fill=fl, stroke=INK, sw=1, rx=0))
        f.append(text(bx + i*bw + bw/2, by + 18, str(b), size=9,
                      color=(BG if b else INK)))
    f.append(rect(bx, by, 8*bw, 26, fill="none", stroke=POS, sw=2, rx=0))
    f.append(text(120, 152, "1 байт = 8 пікселів", size=11, color=POS, bold=True))
    f.append(text(120, 170, "поставити один → читай-міняй-пиши цілий байт", size=9.5, color=GREY))
    # 16 біт/піксель: кожен піксель — 2 байти
    f.append(text(560, 92, "16 біт/піксель", size=13, color=INK, bold=True))
    px0, pw = 470, 78
    cols = [(ROW0, ROW0S), (ROW1, ROW1S), (ROW2, ROW2S)]
    for i, (fl, st) in enumerate(cols):
        f.append(rect(px0 + i*pw, 104, pw, 26, fill=fl, stroke=st, sw=1.4, rx=0))
        f.append(text(px0 + i*pw + pw/2, 122, "піксель", size=10, color=INK))
        f.append(text(px0 + i*pw + pw/2, 146, "2 байти", size=9, color=GREY))
    f.append(text(560, 170, "1 піксель = 2 байти — проста адресація, пишеш напряму", size=10, color=FIELD, bold=True))
    f.append(text(W/2, 250, "Менше за байт (1, 2, 4 біти) — пікселі пакують у байт, і зміна одного вимагає читай-міняй-пиши", size=12, color=INK))
    f.append(caption(W, 272, "(згадайте сторінкову памʼять SSD1306). Від 8 біт кожен піксель — цілі байти, адресувати легко."))
    render(os.path.join(IMG, "packing.svg"), W, H, *f)


# ── 6. Кадр проти SRAM мікроконтролера (смуги) ──────────────────────────────
def fig_vs_sram():
    W, H = 820, 340
    f = [title(W, "Кадр проти RAM мікроконтролера: хто кого", 18)]
    # вісь масштабу: 1 КБ → px
    x0 = 90; axis_y = 280; per_kb = (760 - 90) / 800.0
    f.append(line(x0, axis_y, 760, axis_y, color=INK, sw=2))
    bars = [
        ("кадр 320×240×16", 150,  POS,  WARM),
        ("кадр 480×272×16", 255,  POS,  WARM),
        ("кадр 800×480×16", 750,  POS,  WARM),
        ("малий МК (SRAM)",  20,   NEG,  "#e9eefb"),
        ("середній МК",      256,  NEG,  "#e9eefb"),
        ("великий МК",       512,  NEG,  "#e9eefb"),
    ]
    y = 70
    for label, kbv, col, fl in bars:
        bw = kbv * per_kb
        f.append(rect(x0, y, bw, 22, fill=fl, stroke=col, sw=1.4, rx=0))
        f.append(text(x0 + 6, y + 16, label, size=10.5, color=col, anchor="start", bold=True))
        f.append(text(x0 + bw + 6, y + 16, "%g КБ" % kbv, size=10, color=GREY, anchor="start"))
        y += 32
    # позначки шкали
    for tick in (100, 250, 500, 750):
        tx = x0 + tick * per_kb
        f.append(line(tx, axis_y - 4, tx, axis_y + 4, color=INK, sw=1.2))
        f.append(text(tx, axis_y + 20, str(tick), size=9.5, color=GREY))
    f.append(text(762, axis_y + 20, "КБ", size=10, color=INK, anchor="start"))
    f.append(caption(W, 318, "Великий кадр легко переростає SRAM навіть пристойного МК — звідси зовнішня памʼять або розумна панель."))
    render(os.path.join(IMG, "vs-sram.svg"), W, H, *f)


# ── 7. Знаковий екран проти бітмапного (вставка hist-alto) ───────────────────
def fig_char_vs_bitmap():
    W, H = 820, 372
    f = [title(W, "Знаковий екран проти бітмапного: чому PARC обрав кожен піксель", 17)]
    # ліворуч — сітка готових символів
    f.append(text(220, 74, "ЗНАКОВИЙ (до Alto)", size=13, color=INK, bold=True))
    glyphs = ["ABCEFH", "KLMNOP", "RSTUVW", "XYZABC"]
    cs, gx, gy = 50, 70, 92
    for r, rowtxt in enumerate(glyphs):
        for c, ch in enumerate(rowtxt):
            f.append(rect(gx + c*cs, gy + r*cs, cs, cs, fill="#fbfbfb", stroke=GREY, sw=1, rx=0))
            f.append(text(gx + c*cs + cs/2, gy + r*cs + 33, ch, size=20, color=INK))
    f.append(text(220, 314, "лише готові символи з ПЗП;", size=10.5, color=GREY))
    f.append(text(220, 330, "один шрифт, жодної графіки", size=10.5, color=GREY))
    # праворуч — вільні пікселі: рамка з кривою й трикутником
    f.append(text(602, 74, "БІТМАПНИЙ (Alto)", size=13, color=INK, bold=True))
    f.append(rect(452, 92, 300, 200, fill="#fbfbfb", stroke=GREY, sw=1.2, rx=0))
    # синусоїда (ламана)
    import math
    pts = []
    for i in range(44):
        x = 470 + i*4
        yv = 144 + 26 * math.sin(i / 7.0)
        pts.append((x, yv))
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        f.append(line(x1, y1, x2, y2, color=INK, sw=2))
    # трикутник
    f.append(line(488, 250, 538, 204, color=INK, sw=2))
    f.append(line(538, 204, 538, 250, color=INK, sw=2))
    f.append(line(488, 250, 538, 250, color=INK, sw=2))
    f.append(text(602, 237, "Aa fi — пропорційний шрифт", size=13, color=INK, anchor="start"))
    f.append(text(602, 314, "кожен піксель вільний:", size=10.5, color=FIELD, bold=True))
    f.append(text(602, 330, "шрифти, графіка, WYSIWYG", size=10.5, color=FIELD, bold=True))
    render(os.path.join(IMG, "char-vs-bitmap.svg"), W, H, *f)


# ── 8. BitBlt: копіювати прямокутник пікселів (вставка hist-alto) ────────────
def fig_bitblt():
    W, H = 820, 320
    f = [title(W, "BitBlt: копіювати прямокутник пікселів (предок усіх «блітерів»)", 17)]
    # «серце» з пікселів — однакова форма для джерела й приймача
    heart = [
        (2, 0), (3, 0),
        (1, 1), (2, 1), (3, 1), (4, 1),
        (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2),
        (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
        (2, 4), (3, 4), (4, 4),
        (2, 5), (3, 5),
    ]
    ps = 20
    # джерело
    f.append(rect(90, 96, 120, 120, fill="#fbfbfb", stroke=INK, sw=1.6, rx=0))
    for (cx, cy) in heart:
        f.append(rect(90 + cx*ps, 96 + cy*ps, ps, ps, fill=INK, stroke=INK, sw=0.4, rx=0))
    f.append(text(150, 86, "джерело", size=11, color=INK, bold=True))
    f.append(arrow(222, 156, 302, 156, color=FIELD, sw=2.4))
    f.append(text(262, 144, "копіювати", size=10, color=FIELD, bold=True))
    # приймач
    f.append(rect(310, 96, 120, 120, fill=COOL, stroke=INK, sw=1.6, rx=0))
    for (cx, cy) in heart:
        f.append(rect(310 + cx*ps, 96 + cy*ps, ps, ps, fill="#3a5e86", stroke="#3a5e86", sw=0.4, rx=0))
    f.append(text(370, 86, "приймач", size=11, color=INK, bold=True))
    # логічна операція
    f.append(rect(466, 114, 226, 84, fill=OKBG, stroke=FIELD, sw=1.4, rx=6))
    f.append(text(579, 138, "+ логічна операція", size=12, color=INK, bold=True))
    f.append(text(579, 158, "AND / OR / XOR", size=12, color=FIELD, bold=True))
    f.append(text(579, 178, "→ маска, прозорість", size=11, color=GREY))
    f.append(caption(W, 288, "Одна операція рухає цілий прямокутник пікселів — і робить швидкими вікна, шрифти й анімацію. Прямий предок 2D-прискорювачів."))
    render(os.path.join(IMG, "bitblt.svg"), W, H, *f)


# Світла заливка під «активну» комірку (зеленувата)
FIELD_BG = "#dff0e2"


if __name__ == "__main__":
    fig_memory_screen()
    fig_addressing()
    fig_size()
    fig_drawing()
    fig_packing()
    fig_vs_sram()
    fig_char_vs_bitmap()
    fig_bitblt()
    print("OK: 8 figures written to ./img/")
