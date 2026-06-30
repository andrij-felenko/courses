# -*- coding: utf-8 -*-
# Фігури для comp-вставки «ФЧД із зарядовим насосом». Окремий файл, бо основний
# figs.py теми активно росте; svgkit імпортуємо так само, вивід — у спільну ./img.
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. PFD на двох тригерах + зарядовий насос → фільтр контуру ────────────────
def fig_pfd_block():
    W, H = 900, 440
    f = []

    # дві вхідні мітки
    f.append(text(42, 122, "опора", size=14, color=INK, anchor="end", bold=True))
    f.append(text(42, 140, "f_оп ↑", size=12, color=MUTED, anchor="end"))
    f.append(text(42, 302, "зв. зв.", size=14, color=INK, anchor="end", bold=True))
    f.append(text(42, 320, "f_зв ↑", size=12, color=MUTED, anchor="end"))

    ffx, ffy, ffw, ffh = 110, 90, 160, 70
    # верхній тригер (UP)
    f.append(fitbox(ffx, ffy, ffw, ffh, "Тригер 1\nтакт ← опора", size=13, bold=True,
                    stroke=NEG, sw=2.2, fill="#eef3fe"))
    f.append(text(ffx - 4, ffy + 30, "D=1", size=11, color=MUTED, anchor="end"))
    f.append(arrow(46, 125, ffx, 125, color=INK, sw=2.0))
    # нижній тригер (DOWN)
    ff2y = 270
    f.append(fitbox(ffx, ff2y, ffw, ffh, "Тригер 2\nтакт ← зв. зв.", size=13, bold=True,
                    stroke=NEG, sw=2.2, fill="#eef3fe"))
    f.append(text(ffx - 4, ff2y + 30, "D=1", size=11, color=MUTED, anchor="end"))
    f.append(arrow(46, 305, ffx, 305, color=INK, sw=2.0))

    # виходи UP / DOWN
    f.append(text(ffx + ffw + 8, ffy + 26, "UP", size=13, color=POS, anchor="start", bold=True))
    f.append(text(ffx + ffw + 8, ff2y + 50, "DOWN", size=13, color=NEG, anchor="start", bold=True))

    # AND-скид
    andx, andy = 330, 200
    f.append(fitbox(andx, andy, 86, 56, "&\nскид", size=13, bold=True,
                    stroke=FIELD, sw=2.2, fill="#eafaf0"))
    f.append(line(ffx + ffw, ffy + 36, andx, andy + 16, color=POS, sw=1.8))
    f.append(line(ffx + ffw, ff2y + 36, andx, andy + 40, color=NEG, sw=1.8))
    # скид назад в обидва тригери (пунктир)
    f.append(line(andx + 43, andy + 56, andx + 43, 372, color=FIELD, sw=1.6, dash="5 4"))
    f.append(line(andx + 43, 372, 64, 372, color=FIELD, sw=1.6, dash="5 4"))
    f.append(line(64, 372, 64, ffy + ffh + 6, color=FIELD, sw=1.6, dash="5 4"))
    f.append(arrow(64, ffy + ffh + 6, ffx + 14, ffy + ffh + 6, color=FIELD, sw=1.6))
    f.append(line(64, 372, 64, ff2y + ffh + 6, color=FIELD, sw=1.6, dash="5 4"))
    f.append(arrow(64, ff2y + ffh + 6, ffx + 14, ff2y + ffh + 6, color=FIELD, sw=1.6))
    f.append(text(andx + 50, 388, "скидає обидва, щойно UP і DOWN з'явились разом",
                  size=11, color=FIELD, anchor="middle", italic=True))

    # зарядовий насос
    cpx, cpy, cpw, cph = 520, 150, 150, 150
    f.append(rect(cpx, cpy, cpw, cph, fill="#fff7f5", stroke=POS, sw=2.2, rx=8))
    f.append(text(cpx + cpw / 2, cpy + 20, "зарядовий", size=12, color=INK, bold=True))
    f.append(text(cpx + cpw / 2, cpy + 36, "насос", size=12, color=INK, bold=True))
    f.append(text(cpx + cpw / 2, cpy + 54, "+Vж", size=10, color=MUTED))
    f.append(plus(cpx + cpw / 2, cpy + 72, r=10))
    f.append(text(cpx + cpw / 2 + 16, cpy + 76, "I вгору", size=10, color=POS, anchor="start"))
    f.append(minus(cpx + cpw / 2, cpy + 114, r=10))
    f.append(text(cpx + cpw / 2 + 16, cpy + 118, "I вниз", size=10, color=NEG, anchor="start"))
    f.append(text(cpx + cpw / 2, cpy + cph - 8, "GND", size=10, color=MUTED))
    # UP/DOWN → ключі насоса
    f.append(arrow(ffx + ffw + 36, ffy + 36, cpx, cpy + 72, color=POS, sw=1.6))
    f.append(arrow(ffx + ffw + 36, ff2y + 36, cpx, cpy + 114, color=NEG, sw=1.6))

    # вузол виходу насоса → фільтр контуру
    f.append(line(cpx + cpw / 2, cpy + 82, cpx + cpw / 2, cpy + 104, color=INK, sw=2.0))
    f.append(arrow(cpx + cpw, cpy + cph / 2, cpx + cpw + 56, cpy + cph / 2, color=INK, sw=2.2))

    # фільтр R+C
    lfx = cpx + cpw + 56
    f.append(text(lfx + 64, cpy + 18, "фільтр контуру", size=12, color=INK, bold=True))
    f.append(line(lfx, cpy + cph / 2, lfx + 46, cpy + cph / 2, color=INK, sw=2.0))
    f.append(rect(lfx + 46, cpy + cph / 2 - 8, 28, 16, fill="#ffffff", stroke=INK, sw=1.6, rx=2))
    f.append(text(lfx + 60, cpy + cph / 2 - 14, "R", size=11, color=INK))
    f.append(line(lfx + 74, cpy + cph / 2, lfx + 110, cpy + cph / 2, color=INK, sw=2.0))
    # конденсатор вниз
    f.append(line(lfx + 110, cpy + cph / 2, lfx + 110, cpy + cph / 2 + 26, color=INK, sw=2.0))
    f.append(line(lfx + 98, cpy + cph / 2 + 26, lfx + 122, cpy + cph / 2 + 26, color=INK, sw=2.6))
    f.append(line(lfx + 98, cpy + cph / 2 + 34, lfx + 122, cpy + cph / 2 + 34, color=INK, sw=2.6))
    f.append(text(lfx + 130, cpy + cph / 2 + 32, "C", size=11, color=INK, anchor="start"))
    f.append(line(lfx + 110, cpy + cph / 2 + 34, lfx + 110, cpy + cph / 2 + 52, color=MUTED, sw=1.6))
    f.append(text(lfx + 110, cpy + cph / 2 + 66, "GND", size=10, color=MUTED))
    # вихід керівної напруги
    f.append(arrow(lfx + 110, cpy + cph / 2, lfx + 110, cpy - 12, color=POS, sw=2.0))
    f.append(text(lfx + 116, cpy - 6, "до ГКН", size=12, color=POS, anchor="start", bold=True))

    render(os.path.join(IMG, "pfd-block.svg"), W, H, *f,
           title="ФЧД на двох тригерах і зарядовий насос")


# ── 2. Передавальна характеристика ФЧД: лінійна від −2π до +2π ───────────────
def fig_pfd_curve():
    W, H = 760, 380
    f = []
    ox, oy, w, h = 90, 64, 580, 236
    cx, cy = ox + w / 2, oy + h / 2
    f.append(arrow(ox, cy, ox + w + 10, cy, color=INK, sw=1.6))
    f.append(arrow(cx, oy + h + 10, cx, oy - 10, color=INK, sw=1.6))
    f.append(text(ox + w + 6, cy + 22, "різниця фаз", size=13, color=INK, anchor="end"))
    f.append(text(cx + 10, oy - 2, "середній струм у фільтр", size=12, color=INK, anchor="start"))

    span = w / 2 - 36
    for frac, lab in [(-1, "−2π"), (-0.5, "−π"), (0.5, "+π"), (1, "+2π")]:
        x = cx + frac * span
        f.append(line(x, cy - 5, x, cy + 5, color=MUTED, sw=1.4))
        f.append(text(x, cy + 22, lab, size=11, color=MUTED))

    top = cy - 84
    bot = cy + 84
    f.append(line(ox + 12, bot, cx - span, bot, color=POS, sw=2.8))     # ліве плато
    f.append(line(cx - span, bot, cx + span, top, color=POS, sw=2.8))    # лінійна ділянка
    f.append(line(cx + span, top, ox + w - 12, top, color=POS, sw=2.8))  # праве плато
    f.append(text(cx + span + 6, top - 10, "+I насоса", size=11, color=POS, anchor="start"))
    f.append(text(cx - span - 6, bot + 16, "−I насоса", size=11, color=POS, anchor="end"))

    bx1, _, _ = textbox(ox + 96, top - 28, "генератор повільніший:\nтягне вгору весь час",
                        size=11, color=INK, stroke=MUTED, sw=1.2, fill="#f4f6f8")
    f.append(bx1)
    bx2, _, _ = textbox(ox + w - 96, bot + 34, "генератор швидший:\nтягне вниз весь час",
                        size=11, color=INK, stroke=MUTED, sw=1.2, fill="#f4f6f8")
    f.append(bx2)
    bx3, _, _ = textbox(cx + 110, cy + 52, "лінійна зона:\nстежить за фазою",
                        size=11, color=INK, stroke=FIELD, sw=1.6, fill="#eafaf0")
    f.append(bx3)

    render(os.path.join(IMG, "pfd-curve.svg"), W, H, *f,
           title="Характеристика ФЧД: ловить і фазу, і знак частоти")


# ── 3. Мертва зона і струмова неузгодженість ────────────────────────────────
def fig_pfd_deadzone():
    W, H = 780, 360
    f = []

    # ── ліва панель: мертва зона ──
    ox, oy, w, h = 70, 76, 290, 184
    cx, cy = ox + w / 2, oy + h / 2
    f.append(text(cx, 54, "Мертва зона коло нуля", size=14, bold=True))
    f.append(arrow(ox, cy, ox + w + 8, cy, color=INK, sw=1.4))
    f.append(arrow(cx, oy + h, cx, oy - 6, color=INK, sw=1.4))
    f.append(text(ox + w + 4, cy + 18, "мала різниця фаз", size=10, color=MUTED, anchor="end"))
    # ідеальна пряма (пунктир)
    f.append(line(cx - 92, cy + 66, cx + 92, cy - 66, color=MUTED, sw=1.4, dash="5 4"))
    f.append(text(cx + 94, cy - 60, "ідеал", size=10, color=MUTED, anchor="start"))
    # реальна: плаский шматок біля нуля
    f.append(line(cx - 92, cy + 66, cx - 24, cy + 8, color=POS, sw=2.6))
    f.append(line(cx - 24, cy + 8, cx + 24, cy - 8, color=POS, sw=2.6, dash="2 3"))
    f.append(line(cx + 24, cy - 8, cx + 92, cy - 66, color=POS, sw=2.6))
    f.append(rect(cx - 24, cy - 16, 48, 32, fill="none", stroke=NEG, sw=1.6, rx=4))
    f.append(text(cx, oy + h + 12, "тут коло «сліпе»: імпульс надто куций", size=10, color=NEG))

    # ── права панель: струмова неузгодженість ──
    ox2 = 440
    f.append(text(ox2 + 150, 54, "Неузгодженість струмів", size=14, bold=True))
    base = oy + 140
    f.append(line(ox2, base, ox2 + 300, base, color=MUTED, sw=1.2))
    # UP вищий
    f.append(rect(ox2 + 36, base - 116, 56, 116, fill="#fff0ee", stroke=POS, sw=2.2, rx=4))
    f.append(text(ox2 + 64, base + 18, "вгору (UP)", size=11, color=POS))
    f.append(text(ox2 + 64, base - 124, "I↑", size=12, color=POS, bold=True))
    # DOWN нижчий
    f.append(rect(ox2 + 168, base - 88, 56, 88, fill="#eef3fe", stroke=NEG, sw=2.2, rx=4))
    f.append(text(ox2 + 196, base + 18, "вниз (DOWN)", size=11, color=NEG))
    f.append(text(ox2 + 196, base - 96, "I↓", size=12, color=NEG, bold=True))
    f.append(line(ox2 + 92, base - 108, ox2 + 168, base - 108, color=INK, sw=1.4, dash="4 3"))
    f.append(text(ox2 + 124, base - 116, "≠", size=18, color=INK, bold=True))
    f.append(text(ox2 + 150, oy + h + 12, "нерівні струми → сталий зсув фази й сплески",
                  size=10, color=MUTED))

    render(os.path.join(IMG, "pfd-deadzone.svg"), W, H, *f,
           title="Дві біди ФЧД-насоса: мертва зона і неузгодженість струмів")


if __name__ == "__main__":
    fig_pfd_block()
    fig_pfd_curve()
    fig_pfd_deadzone()
    print("OK comp-pfd figs ->", IMG)
