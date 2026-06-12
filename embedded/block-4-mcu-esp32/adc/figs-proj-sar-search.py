# -*- coding: utf-8 -*-
"""
Фігури для вставки 4.8.8a — «SAR — двійковий пошук у залізі: N тактів на N біт».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

fig-26-8a-1-discrete-sar-loop.svg — чотири блоки петлі: МК → ЦАП → компаратор → МК.
fig-26-8a-2-clocks-per-bit.svg   — 12 тактів-зважувань (MSB→LSB), кожен = settle + decide.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори модуля
RED   = POS     # "#c0392b"
BLUE  = NEG     # "#2457d6"
GREEN = FIELD   # "#27ae60"
METAL = "#778899"
GOLD  = "#c8922a"
PURP  = "#7c4dff"
LRED  = "#fdecea"
LBLUE = "#e9eefb"
LMETAL = "#dde3ea"
LGOLD  = "#fff6e0"


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.8.8a.1 — Дискретний SAR як петля керування
# ═══════════════════════════════════════════════════════════════════════════════
def fig8a1_discrete_sar_loop():
    W, H = 720, 340
    frags = []

    # ── Заголовок ──
    frags.append(text(W // 2, 26, "Дискретний SAR: петля керування", size=16, bold=True))

    # ── Блоки (по кутах прямокутника) ──
    # [МК]  зліва-вгорі    (cx=160, cy=110)
    # [ЦАП] праворуч-вгорі (cx=520, cy=110)
    # [CMP] праворуч-внизу (cx=520, cy=230)
    # [МК]  зліва-внизу — той самий МК; замінимо на пунктир "назад у МК"
    # Краще: чотири блоки по периметру, стрілки між ними

    BW, BH = 168, 52

    # Блок 1: МК — пробний код
    b1x, b1y = 80, 86    # лівий верхній кут блоку
    b1cx, b1cy = b1x + BW / 2, b1y + BH / 2
    frags.append(fitbox(b1x, b1y, BW, BH, "МК\n(пробний код)",
                        size=13, bold=True, fill=LBLUE, stroke=BLUE, sw=2, rx=8))

    # Блок 2: Зовнішній ЦАП
    b2x, b2y = 472, 86
    b2cx, b2cy = b2x + BW / 2, b2y + BH / 2
    frags.append(fitbox(b2x, b2y, BW, BH, "Зовнішній ЦАП\n(Vtry)",
                        size=13, bold=True, fill=LMETAL, stroke=METAL, sw=2, rx=8))

    # Блок 3: Компаратор
    b3x, b3y = 472, 198
    b3cx, b3cy = b3x + BW / 2, b3y + BH / 2
    frags.append(fitbox(b3x, b3y, BW, BH, "Компаратор ⚖\n(Vin ? Vtry)",
                        size=13, bold=True, fill=LGOLD, stroke=GOLD, sw=2, rx=8))

    # Блок 4: МК (внизу-зліва) — позначити як «назад у МК»
    b4x, b4y = 80, 198
    b4cx, b4cy = b4x + BW / 2, b4y + BH / 2
    frags.append(fitbox(b4x, b4y, BW, BH, "МК\n(лишити / скинути біт)",
                        size=12, bold=False, fill=LBLUE, stroke=BLUE, sw=2, rx=8))

    # ── Стрілки між блоками ──

    # МК → ЦАП (горизонтально вгорі)
    frags.append(arrow(b1x + BW + 2, b1cy, b2x - 2, b2cy, color=INK, sw=2.0))
    # Підпис над стрілкою
    mid_x = (b1x + BW + b2x) / 2
    tb, _, _ = textbox(mid_x, b1cy - 22, "пробний код\n(SPI / GPIO)",
                       size=11, fill="#f4f6f8", stroke=MUTED, sw=1.0, pad=6)
    frags.append(tb)

    # ЦАП → Компаратор (вертикально праворуч)
    frags.append(arrow(b2cx, b2y + BH + 2, b3cx, b3y - 2, color=BLUE, sw=2.0))
    tb2, _, _ = textbox(b2cx + 68, (b2y + BH + b3y) / 2, "Vtry\n(аналог)",
                        size=11, fill=LBLUE, stroke=BLUE, sw=1.0, pad=6, color=BLUE)
    frags.append(tb2)

    # Компаратор → МК (горизонтально внизу)
    frags.append(arrow(b3x - 2, b3cy, b4x + BW + 2, b4cy, color=RED, sw=2.0))
    # Підпис під стрілкою
    mid_x2 = (b3x + b4x + BW) / 2
    tb3, _, _ = textbox(mid_x2, b3cy + 24, "1 біт (GPIO)",
                        size=11, fill=LRED, stroke=RED, sw=1.0, pad=6, color=RED)
    frags.append(tb3)

    # МК (внизу) → МК (вгорі) — лівий край, вертикально замкнена петля
    frags.append(arrow(b4cx, b4y - 2, b1cx, b1y + BH + 2, color=INK, sw=1.8))

    # ── Vin-підпис (зліва від компаратора) ──
    frags.append(arrow(b3x - 80, b3cy, b3x - 2, b3cy, color=GREEN, sw=1.8))
    tb4, _, _ = textbox(b3x - 114, b3cy, "Vin",
                        size=13, bold=True, fill="#eef6ef", stroke=GREEN, sw=1.5, pad=7, color=GREEN)
    frags.append(tb4)

    # ── Нота «один компаратор, N разів» ──
    tb5, _, _ = textbox(W // 2, H - 34, "один компаратор, ужитий N разів = двійковий пошук у залізі",
                        size=12, fill="#f4f6f8", stroke=MUTED, sw=1.2, pad=8)
    frags.append(tb5)

    # ── Підпис рисунка ──
    caption = "Рис. 4.8.8a.1. Дискретний SAR як петля керування"
    frags.append(text(W // 2, H - 12, caption, size=10, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "fig-26-8a-1-discrete-sar-loop.svg"), W, H, *frags,
           title=None)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.8.8a.2 — N тактів на N біт: бюджет 12-бітного перетворення
# ═══════════════════════════════════════════════════════════════════════════════
def fig8a2_clocks_per_bit():
    W, H = 780, 230
    frags = []

    # ── Заголовок ──
    frags.append(text(W // 2, 22, "«N тактів на N біт» — бюджет перетворення", size=15, bold=True))

    N = 12
    # Часова шкала: починається від LX, кожна комірка ширина CELL
    LX = 30
    RX = 640
    TY = 46     # верхній край смуг
    BY = 130    # нижній край смуг
    CH = BY - TY  # висота комірки

    CELL = (RX - LX) / N   # ~50.8 px

    SETTLE_FRAC = 0.65   # 65% комірки — settling
    DECIDE_FRAC = 0.35   # 35% — decide

    bit_labels = ["b11\n(MSB)"] + ["b%d" % i for i in range(10, 1, -1)] + ["b1", "b0\n(LSB)"]

    for i in range(N):
        cx0 = LX + i * CELL
        cx1 = cx0 + CELL
        xs = cx0 + CELL * SETTLE_FRAC   # межа settle/decide

        # Фаза settle (LMETAL)
        frags.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" '
                     'fill="%s" stroke="%s" stroke-width="1.2"/>' % (
                         cx0, TY, CELL * SETTLE_FRAC, CH, LMETAL, METAL))

        # Фаза decide (LGOLD)
        frags.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" '
                     'fill="%s" stroke="%s" stroke-width="1.2"/>' % (
                         xs, TY, CELL * DECIDE_FRAC, CH, LGOLD, GOLD))

        # Підпис біту зверху
        lbl = bit_labels[i]
        frags.append(mtext(cx0 + CELL / 2, TY - 18, lbl, size=9, color=INK, anchor="middle"))

        # Підписи t_settle / t_decide тільки для першої і другої комірки
        if i == 0:
            frags.append(text(cx0 + CELL * SETTLE_FRAC / 2, TY + CH / 2 + 5,
                               "t_settle", size=9, color=METAL, anchor="middle"))
            frags.append(text(xs + CELL * DECIDE_FRAC / 2, TY + CH / 2 + 5,
                               "t_decide", size=9, color=GOLD, anchor="middle"))
        elif i == 1:
            frags.append(text(cx0 + CELL * SETTLE_FRAC / 2, TY + CH / 2 + 5,
                               "t_settle", size=9, color=METAL, anchor="middle"))

    # ── Вісь часу ──
    frags.append(arrow(LX, BY + 10, RX + 20, BY + 10, color=INK, sw=1.5))
    frags.append(text(RX + 26, BY + 15, "час", size=11, color=INK, anchor="start"))

    # ── Дужка-сума під усіма комірками ──
    frags.append(line(LX, BY + 26, RX, BY + 26, color=INK, sw=1.5))
    frags.append(line(LX, BY + 20, LX, BY + 32, color=INK, sw=1.5))
    frags.append(line(RX, BY + 20, RX, BY + 32, color=INK, sw=1.5))
    frags.append(text((LX + RX) / 2, BY + 44,
                       "t_конв ≈ N · (t_settle + t_decide)  ≈ 12 · 1.5 мкс ≈ 18 мкс",
                       size=12, color=INK, anchor="middle", bold=True))

    # ── Легенда (праворуч від шкали) ──
    LEG_X = RX + 40
    frags.append('<rect x="%d" y="%d" width="22" height="14" fill="%s" stroke="%s" stroke-width="1.2"/>' % (
        LEG_X, TY + 8, LMETAL, METAL))
    frags.append(text(LEG_X + 28, TY + 20, "встановлення ЦАП", size=11, color=INK, anchor="start"))
    frags.append('<rect x="%d" y="%d" width="22" height="14" fill="%s" stroke="%s" stroke-width="1.2"/>' % (
        LEG_X, TY + 30, LGOLD, GOLD))
    frags.append(text(LEG_X + 28, TY + 42, "рішення компаратора", size=11, color=INK, anchor="start"))

    # ── Примітка справа ──
    tb_note, _, _ = textbox(LEG_X + 90, BY - 10,
                             "стала затримка\n→ передбачувано",
                             size=11, fill="#eef6ef", stroke=GREEN, sw=1.2, pad=7, color=GREEN)
    frags.append(tb_note)

    # ── Підпис рисунка ──
    frags.append(text(W // 2, H - 10,
                       "Рис. 4.8.8a.2. N тактів на N біт: settle + decide = один такт-зважування",
                       size=10, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "fig-26-8a-2-clocks-per-bit.svg"), W, H, *frags,
           title=None)


if __name__ == "__main__":
    fig8a1_discrete_sar_loop()
    print("fig-26-8a-1-discrete-sar-loop.svg — OK")
    fig8a2_clocks_per_bit()
    print("fig-26-8a-2-clocks-per-bit.svg — OK")
    print("OK - figures for SAR-search insert 4.8.8a")
