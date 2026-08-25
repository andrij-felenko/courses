# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def tbox(cx, cy, s, **kw):
    """textbox повертає (frag,w,h) — беремо лише фрагмент."""
    return textbox(cx, cy, s, **kw)[0]


# ── транзистори-ключі (стиль svgkit) ───────────────────────────────────────
def nmos(cx, cy, on=False, label="N"):
    col = FIELD if on else MUTED
    ch = INK if on else MUTED
    out = [line(cx, cy - 28, cx, cy + 28, color=ch, sw=2.6)]
    out.append(line(cx - 26, cy, cx - 9, cy, color=ch, sw=2))
    out.append(line(cx - 9, cy - 13, cx - 9, cy + 13, color=ch, sw=2.6))
    out.append(text(cx + 11, cy - 18, label, size=12, color=col, bold=True, anchor="start"))
    return "".join(out)


def pmos(cx, cy, on=False, label="P"):
    col = FIELD if on else MUTED
    ch = INK if on else MUTED
    out = [line(cx, cy - 28, cx, cy + 28, color=ch, sw=2.6)]
    out.append(line(cx - 26, cy, cx - 14, cy, color=ch, sw=2))
    out.append(circle(cx - 11, cy, 4.5, fill=BG, stroke=ch, sw=2))
    out.append(line(cx - 6.5, cy - 13, cx - 6.5, cy + 13, color=ch, sw=2.6))
    out.append(text(cx + 11, cy - 18, label, size=12, color=col, bold=True, anchor="start"))
    return "".join(out)


def schmitt(cx, cy, active=True, point="left"):
    """Трикутник-буфер із гістерезис-міткою. point='left' → вихід ліворуч."""
    col = INK if active else MUTED
    if point == "left":
        p = "%d,%d %d,%d %d,%d" % (cx + 30, cy - 26, cx + 30, cy + 26, cx - 34, cy)
    else:
        p = "%d,%d %d,%d %d,%d" % (cx - 30, cy - 26, cx - 30, cy + 26, cx + 34, cy)
    out = ['<polygon points="%s" fill="%s" stroke="%s" stroke-width="2"/>'
           % (p, FILL if active else BG, col)]
    # гістерезис-гліф усередині
    gx = cx - 2
    out.append(line(gx - 8, cy + 5, gx - 2, cy + 5, color=col, sw=1.6))
    out.append(line(gx - 2, cy + 5, gx - 2, cy - 5, color=col, sw=1.6))
    out.append(line(gx - 2, cy - 5, gx + 6, cy - 5, color=col, sw=1.6))
    return "".join(out)


# ─────────────────────────────────────────────────────────────────────────────
# 1) gpio-cell.svg — анатомія комірки: 4 біти регістра ↔ функції ↔ ніжка
# ─────────────────────────────────────────────────────────────────────────────
def fig_cell():
    W, H = 940, 470
    f = []

    # межа комірки
    f.append('<rect x="250" y="70" width="470" height="360" rx="14" '
             'fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="6,5"/>' % MUTED)
    f.append(text(485, 92, "GPIO-комірка (одна ніжка)", size=14, color=MUTED, bold=True))

    # регістри зліва
    f.append(text(140, 92, "біти регістра", size=13, color=INK, bold=True))
    regs = [
        (150, "DIR", "напрям: вхід/вихід", NEG),
        (215, "OUT", "що видати (1/0)", POS),
        (300, "PULL", "підтяжка ↑/↓/нема", FIELD),
        (372, "IN", "що зараз на ніжці", INK),
    ]
    for cy, name, desc, col in regs:
        f.append(rect(55, cy - 22, 160, 44, fill=FILL, stroke=col, sw=2))
        f.append(text(75, cy - 3, name, size=14, color=col, bold=True, anchor="start"))
        f.append(text(75, cy + 15, desc, size=11, color=MUTED, anchor="start"))

    # центральні функційні блоки
    f.append(text(432, 150, "VDD", size=11, color=MUTED))
    f.append(tbox(432, 178, "драйвер\n(двотактний)", size=13, stroke=POS, bold=True))
    f.append(text(432, 214, "GND", size=11, color=MUTED))

    f.append(tbox(432, 300, "підтяжки\n↑ до VDD / ↓ до GND", size=12, stroke=FIELD))

    f.append(schmitt(438, 372, active=True, point="left"))
    f.append(text(470, 400, "вхідний буфер (Шмітт)", size=11, color=MUTED, anchor="middle"))

    # спільний вузол → ніжка
    nx = 588
    f.append(line(nx, 178, nx, 372, color=INK, sw=2.4))
    f.append(circle(nx, 250, 4, fill=INK, stroke=INK))

    # драйвер → вузол
    f.append(line(508, 178, nx, 178, color=INK, sw=2))
    # підтяжки → вузол
    f.append(line(548, 300, nx, 300, color=INK, sw=2))
    # вузол → буфер (вхід буфера справа)
    f.append(line(nx, 372, 468, 372, color=INK, sw=2))
    # вузол → ніжка
    f.append(line(nx, 250, 700, 250, color=INK, sw=2.6))

    # ніжка (pad)
    f.append(rect(700, 232, 34, 34, fill="#eef2f7", stroke=INK, sw=2, rx=3))
    f.append(text(717, 254, "pad", size=11, color=INK))
    f.append(text(717, 292, "ніжка", size=12, color=INK, bold=True))
    f.append(arrow(736, 250, 830, 250, color=INK, sw=2.4))
    f.append(text(848, 246, "зовнішній", size=12, color=MUTED, anchor="middle"))
    f.append(text(848, 262, "світ", size=12, color=MUTED, anchor="middle"))

    # біти → блоки (стрілки)
    f.append(arrow(215, 215, 356, 185, color=POS, sw=1.8))      # OUT → драйвер (дані)
    f.append(arrow(215, 150, 356, 168, color=NEG, sw=1.8))      # DIR → драйвер (дозвіл)
    f.append(arrow(215, 300, 300, 300, color=FIELD, sw=1.8))    # PULL → підтяжки
    f.append(arrow(408, 372, 220, 372, color=INK, sw=1.8))      # буфер → IN

    # підпис ідеї
    f.append(tbox(485, 448,
                  "чотири біти регістра керують маленькою схемою, "
                  "що зшиває «число» з реальною напругою на ніжці",
                  size=13, stroke=INK))
    render(os.path.join(OUT, "gpio-cell.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2) modes.svg — той самий вивід у двох режимах: вихід і вхід
# ─────────────────────────────────────────────────────────────────────────────
def one_mode(cx, out_mode):
    """Стовпчик push-pull + буфер збоку; out_mode=True → драйвер жене, буфер тьмяний."""
    out = []
    yv, yp, ypin, yn, yg = 120, 162, 232, 302, 344
    # у режимі виходу драйвер активний (жене «1» для прикладу), у вході — обидва закриті
    top_on = out_mode
    bot_on = False
    drv = INK if out_mode else MUTED
    out.append(text(cx, yv - 12, "VDD", size=12, color=MUTED))
    out.append(line(cx, yv, cx, yp - 28, color=drv, sw=2, dash=None if out_mode else "4,4"))
    out.append(pmos(cx, yp, on=top_on, label="P"))
    out.append(line(cx, yp + 28, cx, ypin, color=drv, sw=2, dash=None if out_mode else "4,4"))
    out.append(circle(cx, ypin, 4, fill=INK, stroke=INK))
    out.append(line(cx, ypin, cx, yn - 28, color=drv, sw=2, dash=None if out_mode else "4,4"))
    out.append(nmos(cx, yn, on=bot_on, label="N"))
    out.append(line(cx, yn + 28, cx, yg, color=drv, sw=2, dash="4,4"))
    out.append(text(cx, yg + 16, "GND", size=12, color=MUTED))

    # ніжка праворуч
    out.append(line(cx, ypin, cx + 96, ypin, color=INK, sw=2.6))
    out.append(rect(cx + 96, ypin - 15, 30, 30, fill="#eef2f7", stroke=INK, sw=2, rx=3))

    # буфер знизу-зліва читає ніжку
    bcol = MUTED if out_mode else INK
    out.append(line(cx, ypin, cx, ypin + 78, color=bcol, sw=1.8, dash="3,3" if out_mode else None))
    out.append(line(cx, ypin + 78, cx - 60, ypin + 78, color=bcol, sw=1.8, dash="3,3" if out_mode else None))
    out.append(schmitt(cx - 62, ypin + 78, active=not out_mode, point="left"))
    out.append(text(cx - 150, ypin + 82, "→ IN", size=12, color=bcol, bold=not out_mode, anchor="start"))
    return "".join(out)


def fig_modes():
    W, H = 860, 500
    f = []
    # ЛІВО: режим ВИХІД
    f.append(text(215, 56, "DIR = вихід", size=15, color=POS, bold=True))
    f.append(one_mode(215, out_mode=True))
    f.append(arrow(341, 232, 410, 232, color=POS, sw=2.4))
    f.append(text(376, 220, "жене", size=11, color=POS))
    f.append(tbox(215, 470,
                  "драйвер увімкнено: чіп САМ тримає рівень\nі віддає/приймає струм у навантаження",
                  size=12, stroke=POS))

    # роздільник
    f.append(line(430, 60, 430, 440, color="#dddddd", sw=1))

    # ПРАВО: режим ВХІД
    f.append(text(650, 56, "DIR = вхід", size=15, color=NEG, bold=True))
    f.append(one_mode(650, out_mode=False))
    f.append(arrow(846, 232, 776, 232, color=NEG, sw=2.4))
    f.append(text(812, 220, "слухає", size=11, color=NEG))
    f.append(tbox(650, 470,
                  "драйвер вимкнено (Hi-Z для лінії):\nбуфер лише зчитує чужу напругу",
                  size=12, stroke=NEG))
    render(os.path.join(OUT, "modes.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3) floating-pull.svg — плаваючий вхід і внутрішня підтяжка з кнопкою
# ─────────────────────────────────────────────────────────────────────────────
def input_panel(cx, mode, cap, cap_col):
    """mode: 'float' | 'up_open' | 'up_press'."""
    out = []
    yv, ypin, yg = 90, 210, 340
    pin_x = cx
    # ніжка-вузол
    out.append(circle(pin_x, ypin, 4, fill=INK, stroke=INK))
    out.append(text(pin_x + 12, ypin - 10, "ніжка", size=11, color=INK, anchor="start"))

    # підтяжка вгору (є у двох останніх)
    if mode in ("up_open", "up_press"):
        out.append(text(pin_x, yv - 12, "VDD", size=12, color=MUTED))
        out.append(line(pin_x, yv, pin_x, ypin - 44, color=FIELD, sw=2))
        # резистор-зигзаг
        zx, zy = pin_x, ypin - 44
        pts = []
        for i in range(7):
            dx = 7 if i % 2 == 0 else -7
            pts.append((zx + (dx if i not in (0, 6) else 0), zy - i * 6))
        seg = "".join(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                            color=FIELD, sw=2) for i in range(len(pts) - 1))
        out.append(seg)
        out.append(text(pin_x + 16, ypin - 60, "Rпідт", size=11, color=FIELD, anchor="start"))
    else:
        out.append(text(pin_x, yv - 12, "(нічого)", size=12, color=MUTED))
        out.append(line(pin_x, yv + 4, pin_x, ypin - 10, color=MUTED, sw=1.4, dash="4,4"))

    # буфер читає ніжку → рівень
    out.append(line(pin_x, ypin, pin_x + 70, ypin, color=INK, sw=2))
    out.append(schmitt(pin_x + 74, ypin, active=True, point="right"))
    read = {"float": "?", "up_open": "1", "up_press": "0"}[mode]
    rcol = {"float": POS, "up_open": FIELD, "up_press": NEG}[mode]
    out.append(text(pin_x + 130, ypin + 5, read, size=22, color=rcol, bold=True, anchor="start"))

    # кнопка донизу до GND (у двох останніх)
    if mode in ("up_open", "up_press"):
        out.append(line(pin_x, ypin, pin_x, ypin + 46, color=INK, sw=2))
        # контакти кнопки
        pressed = (mode == "up_press")
        if pressed:
            out.append(line(pin_x, ypin + 46, pin_x, yg - 10, color=NEG, sw=2.4))
            out.append(text(pin_x + 14, ypin + 74, "натиснено", size=11, color=NEG, anchor="start"))
        else:
            out.append(line(pin_x, ypin + 46, pin_x, ypin + 62, color=INK, sw=2))
            out.append(line(pin_x - 16, ypin + 70, pin_x + 16, ypin + 62, color=INK, sw=2.4))
            out.append(line(pin_x, ypin + 84, pin_x, yg - 10, color=INK, sw=2, dash="4,4"))
            out.append(text(pin_x + 14, ypin + 78, "розімкнено", size=11, color=MUTED, anchor="start"))
        out.append(text(pin_x, yg + 6, "GND", size=12, color=MUTED))
    else:
        # плаваючий: хвилька-шум біля вузла
        out.append(text(pin_x - 4, ypin + 40, "∿ шум наводиться", size=12, color=POS, anchor="middle"))

    out.append(tbox(cx, 400, cap, size=12, color=cap_col, stroke=cap_col, bold=True))
    return "".join(out)


def fig_floating():
    W, H = 928, 450
    f = []
    f.append(input_panel(150, "float", "без підтяжки:\nрівень НЕ визначено", POS))
    f.append(input_panel(470, "up_open", "підтяжка ↑, кнопка розімкнена:\nчитаємо «1»", FIELD))
    f.append(input_panel(770, "up_press", "кнопку натиснено:\nлінію притягнено до GND → «0»", NEG))
    f.append(line(310, 70, 310, 370, color="#dddddd", sw=1))
    f.append(line(620, 70, 620, 370, color="#dddddd", sw=1))
    render(os.path.join(OUT, "floating-pull.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4) register-map.svg — біт ↔ ніжка: карта регістрів порту
# ─────────────────────────────────────────────────────────────────────────────
def fig_regmap():
    W, H = 900, 470
    f = []
    n = 8
    x0, cw, gap = 250, 66, 8
    cx = lambda i: x0 + i * (cw + gap) + cw / 2

    # приклад стану: біти для P0..P7 (індекс 0 = P0, ліворуч)
    DIR = [1, 0, 0, 1, 0, 1, 0, 0]   # 1=вихід, 0=вхід
    OUTb = [1, 0, 0, 0, 0, 1, 0, 0]
    INb = [1, 1, 0, 0, 1, 1, 0, 1]
    PU = [0, 1, 1, 0, 2, 0, 1, 0]    # 0=нема,1=вгору,2=вниз

    rows = [
        (110, "DIR", DIR, lambda v: ("вих" if v else "вх"), NEG),
        (185, "OUT", OUTb, lambda v: str(v), POS),
        (260, "IN", INb, lambda v: str(v), INK),
        (335, "PUPD", PU, lambda v: ("—", "↑", "↓")[v], FIELD),
    ]
    for ry, name, arr, fmt, col in rows:
        f.append(text(210, ry + 5, name, size=14, color=col, bold=True, anchor="end"))
        for i in range(n):
            x = cx(i) - cw / 2
            out_pin = (DIR[i] == 1)
            fill = "#fdecea" if (name == "OUT" and out_pin) else \
                   ("#eafaf1" if (name == "IN" and not out_pin) else FILL)
            f.append(rect(x, ry - 20, cw, 40, fill=fill, stroke=col, sw=1.6))
            f.append(text(cx(i), ry + 6, fmt(arr[i]), size=15, color=col, bold=True))

    # рядок ніжок
    py = 410
    for i in range(n):
        x = cx(i) - cw / 2
        out_pin = (DIR[i] == 1)
        pc = POS if out_pin else NEG
        f.append(rect(x, py - 18, cw, 36, fill="#eef2f7", stroke=pc, sw=2, rx=3))
        f.append(text(cx(i), py + 5, "P%d" % i, size=14, color=pc, bold=True))
        # напрямна лінія від PUPD-рядка до ніжки (зупиняється перед стрілкою,
        # щоб не перетинати напис)
        f.append(line(cx(i), 355, cx(i), 373, color="#d3d8de", sw=1))
        # стрілка напряму
        if out_pin:
            f.append(text(cx(i), 386, "▲", size=11, color=POS))
        else:
            f.append(text(cx(i), 386, "▼", size=11, color=NEG))

    # легенда
    f.append(rect(250, 60, 16, 16, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(274, 73, "DIR=вих → OUT жене ніжку (▲)", size=12, color=INK, anchor="start"))
    f.append(rect(560, 60, 16, 16, fill="#eafaf1", stroke=INK, sw=1.6))
    f.append(text(584, 73, "DIR=вх → ніжку зчитує IN (▼)", size=12, color=INK, anchor="start"))

    f.append(text(W / 2, 450, "кожен біт у рядку керує однією ніжкою того самого номера",
                  size=13, color=MUTED))
    render(os.path.join(OUT, "register-map.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 5) direction-philosophies.svg — [hist] Motorola: біт на ніжку · Intel: біт на групу
# ─────────────────────────────────────────────────────────────────────────────
def fig_philosophies():
    W, H = 1080, 500
    f = []

    # роздільник двох панелей
    f.append(line(540, 55, 540, 410, color="#d3d8de", sw=1.5, dash="6 5"))

    # ── ЛІВА панель: Motorola MC6820 — біт на КОЖНУ ніжку ────────────────────
    f.append(tbox(280, 78, "Motorola MC6820 · березень 1974", size=14, bold=True,
                  fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(text(280, 124, "DDRA — вісім окремих бітів", size=13, color=MUTED))

    for i in range(8):
        cx0 = 90 + i * 54
        f.append(rect(cx0 - 19, 145, 38, 40, fill="#eafaf1", stroke=FIELD, sw=2, rx=3))
        f.append(text(cx0, 172, "1" if i in (0, 3, 4) else "0",
                      size=15, color=FIELD, bold=True))
        f.append(arrow(cx0, 187, cx0, 246, color=FIELD, sw=1.6))
        f.append(rect(cx0 - 22, 250, 44, 42, fill="#eef2f7", stroke=INK, sw=1.6, rx=3))
        f.append(text(cx0, 277, "PA%d" % i, size=11, color=INK, bold=True))

    f.append(tbox(280, 355, "16 ліній ↔ 16 бітів напряму\nкожну ніжку крутиш окремо",
                  size=13, fill=BG, stroke=FIELD, sw=1.8))

    # ── ПРАВА панель: Intel 8255 — біт на цілу ГРУПУ ─────────────────────────
    f.append(tbox(800, 78, "Intel 8255 · вересень 1975", size=14, bold=True,
                  fill="#f1f3f5", stroke=MUTED, sw=2))
    f.append(text(800, 124, "керуюче слово — один біт на всю групу", size=13, color=MUTED))

    f.append(rect(725, 145, 150, 42, fill="#f1f3f5", stroke=MUTED, sw=2, rx=3))
    f.append(text(800, 172, "один біт = Port A", size=13, color=INK, bold=True))
    for i in range(8):
        cx0 = 610 + i * 54
        f.append(arrow(800, 188, cx0, 246, color=MUTED, sw=1.3))
        f.append(rect(cx0 - 22, 250, 44, 42, fill="#eef2f7", stroke=MUTED, sw=1.6, rx=3))
        f.append(text(cx0, 277, "PA%d" % i, size=11, color=MUTED, bold=True))

    f.append(tbox(800, 355, "24 лінії ↔ 4 біти напряму\nPort A · Port B · Port C-низ · Port C-верх",
                  size=13, fill=BG, stroke=MUTED, sw=1.8))

    f.append(tbox(540, 452, "Переміг рахунок Motorola: у сучасному GPIO напрям кожної ніжки — власний біт",
                  size=13, bold=True, fill="#eafaf1", stroke=FIELD, sw=2))
    render(os.path.join(OUT, "direction-philosophies.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 6) pia-registers.svg — [hist] чотири адреси, шість регістрів, біт 2 як двері
# ─────────────────────────────────────────────────────────────────────────────
def fig_pia_regs():
    W, H = 1020, 490
    f = []
    x0, x1, x2, x3 = 90, 280, 500, 930
    ytop, hdr = 70, 42

    # шапка
    f.append(rect(x0, ytop, x3 - x0, hdr, fill="#eef2f7", stroke=INK, sw=1.6, rx=4))
    f.append(text((x0 + x1) / 2, ytop + 27, "адреса (RS1 RS0)", size=13, bold=True))
    f.append(text((x1 + x2) / 2, ytop + 27, "біт 2 керуючого регістра", size=13, bold=True))
    f.append(text((x2 + x3) / 2, ytop + 27, "що з'явиться за цією адресою", size=13, bold=True))

    # ── колонка адреси: дві клітини ЗЛИТІ (одна адреса — два регістри) ───────
    f.append(rect(x0, 112, x1 - x0, 96, fill="#eafaf1", stroke=FIELD, sw=2, rx=4))
    f.append(text((x0 + x1) / 2, 152, "0 0", size=20, color=FIELD, bold=True))
    f.append(text((x0 + x1) / 2, 176, "одна адреса —", size=11, color=MUTED))
    f.append(text((x0 + x1) / 2, 193, "два регістри", size=11, color=MUTED))

    f.append(rect(x0, 208, x1 - x0, 48, fill=BG, stroke=INK, sw=1.4, rx=4))
    f.append(text((x0 + x1) / 2, 239, "0 1", size=18, color=MUTED, bold=True))

    f.append(rect(x0, 256, x1 - x0, 96, fill="#eafaf1", stroke=FIELD, sw=2, rx=4))
    f.append(text((x0 + x1) / 2, 296, "1 0", size=20, color=FIELD, bold=True))
    f.append(text((x0 + x1) / 2, 320, "одна адреса —", size=11, color=MUTED))
    f.append(text((x0 + x1) / 2, 337, "два регістри", size=11, color=MUTED))

    f.append(rect(x0, 352, x1 - x0, 48, fill=BG, stroke=INK, sw=1.4, rx=4))
    f.append(text((x0 + x1) / 2, 383, "1 1", size=18, color=MUTED, bold=True))

    # ── колонки «біт 2» і «регістр» ──────────────────────────────────────────
    rows = [
        ("0", "DDRA — регістр напряму порту A", FIELD, "#eafaf1"),
        ("1", "PRA — дані порту A", INK, BG),
        ("—", "CRA — керуючий регістр порту A", MUTED, BG),
        ("0", "DDRB — регістр напряму порту B", FIELD, "#eafaf1"),
        ("1", "PRB — дані порту B", INK, BG),
        ("—", "CRB — керуючий регістр порту B", MUTED, BG),
    ]
    for i, (bit, reg, col, fl) in enumerate(rows):
        y = 112 + i * 48
        f.append(rect(x1, y, x2 - x1, 48, fill=fl, stroke=INK, sw=1.4, rx=4))
        f.append(text((x1 + x2) / 2, y + 31, bit, size=18, color=col, bold=True))
        f.append(rect(x2, y, x3 - x2, 48, fill=fl, stroke=INK, sw=1.4, rx=4))
        f.append(text(x2 + 18, y + 30, reg, size=13, color=col, anchor="start",
                      bold=(bit == "0")))

    f.append(mtext(W / 2, 432,
                   ["Дві лінії RS дають ЧОТИРИ адреси — а регістрів ШІСТЬ.",
                    "Біт 2 керуючого регістра — двері: 0 → регістр напряму, 1 → дані порту."],
                   size=13, color=INK))
    render(os.path.join(OUT, "pia-registers.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 7) port-timeline.svg — [hist] дві доріжки: чипи-порти → порт усередині чипа
# ─────────────────────────────────────────────────────────────────────────────
def fig_timeline():
    W, H = 1240, 545
    f = []

    def X(year):
        return 340 + (year - 1974) * 140

    def evbox(cx, cy, name, date, gloss, color, fill):
        w = max(text_width(name, 12, True), text_width(date, 11),
                text_width(gloss, 11)) + 24
        h = 65.0
        out = rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=color, sw=1.8, rx=5)
        out += text(cx, cy - 14, name, size=12, color=color, bold=True)
        out += text(cx, cy + 3, date, size=11, color=MUTED)
        out += text(cx, cy + 21, gloss, size=11, color=INK)
        return out, h

    # доріжки
    f.append(line(300, 225, 1200, 225, color=FIELD, sw=3))
    f.append(line(300, 310, 1200, 310, color=NEG, sw=3))
    f.append(tbox(170, 225, "Окремі чипи-порти\nколо процесора", size=12,
                  fill="#eafaf1", stroke=FIELD, sw=1.8))
    f.append(tbox(170, 310, "Порт усередині\nчипа (мікроконтролери)", size=12,
                  fill="#eaf0fd", stroke=NEG, sw=1.8))

    # доріжка 1 — окремі чипи (написи НАД лінією)
    ev1 = [
        (1974.2, 175, 368, "MC6820 · PIA", "березень 1974", "народився DDR"),
        (1975.7, 100, 578, "Intel 8255 · PPI", "вересень 1975", "напрям на групу"),
        (1976.0, 175, 690, "MOS 6520", "1976", "копія 6820"),
        (1977.0, 100, 760, "MOS 6522 · VIA", "1977", "PIA + таймери"),
    ]
    for yr, cy, bx, name, date, gloss in ev1:
        box, h = evbox(bx, cy, name, date, gloss, FIELD, "#eafaf1")
        f.append(line(bx, cy + h / 2, X(yr), 225, color=FIELD, sw=1.4))
        f.append(box)
        f.append(circle(X(yr), 225, 6, fill=BG, stroke=FIELD, sw=2.5))

    # доріжка 2 — порт у чипі (написи ПІД лінією)
    ev2 = [
        (1974.0, 370, 360, "TMS1000", "1974", "жорсткий напрям ніжок"),
        (1977.0, 445, 760, "MC6801", "1977", "DDR переїхав у чип"),
        (1979.0, 370, 1040, "MC6805", "1979", "дешевий, той самий I/O"),
        (1980.0, 445, 1140, "Intel 8051", "1980", "DDR скасовано"),
    ]
    for yr, cy, bx, name, date, gloss in ev2:
        box, h = evbox(bx, cy, name, date, gloss, NEG, "#eaf0fd")
        f.append(line(bx, cy - h / 2, X(yr), 310, color=NEG, sw=1.4))
        f.append(box)
        f.append(circle(X(yr), 310, 6, fill=BG, stroke=NEG, sw=2.5))

    f.append(text(W / 2, 512,
                  "Програмований напрям народився в чипі-супутнику — і аж за три роки переїхав усередину мікроконтролера",
                  size=13, color=MUTED))
    render(os.path.join(OUT, "port-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_cell()
    fig_modes()
    fig_floating()
    fig_regmap()
    fig_philosophies()
    fig_pia_regs()
    fig_timeline()
    print("done:", os.listdir(OUT))
