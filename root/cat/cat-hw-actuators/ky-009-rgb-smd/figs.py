# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-009 — RGB SMD-модуль».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED = "#d64545"
GRN = "#3a9d55"
BLU = "#3b6fd6"


def led_symbol(f, cx, cy, col, r=15):
    """Схематичний світлодіод: трикутник (анод зверху) + смужка катода знизу + стрілки світла."""
    # трикутник діода (вершина вниз = катод)
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (cx - r, cy - r, cx + r, cy - r, cx, cy + r, col))
    # смужка катода
    f.append(line(cx - r, cy + r, cx + r, cy + r, color=col, sw=2.6))
    # дві стрілки випромінювання
    f.append(arrow(cx + r - 2, cy - r + 2, cx + r + 12, cy - r - 10, color=col, sw=1.6))
    f.append(arrow(cx + r + 4, cy - r + 6, cx + r + 18, cy - r - 6, color=col, sw=1.6))


# ── 1. Внутрішня схема: три кристали, спільний катод, БЕЗ резисторів ───────────
def fig_internal():
    W, H = 940, 500
    f = [text(W / 2, 30, "Що всередині KY-009: три кристали з одним спільним катодом", size=16, bold=True)]

    # три світлодіоди в ряд (аноди — вгору до своїх пінів; катоди — вниз до спільної шини)
    cols = [(RED, "R"), (GRN, "G"), (BLU, "B")]
    lx = [430, 560, 690]        # x кожного кристала
    ly = 150                    # y центру символів
    # рамка корпусу навколо трьох кристалів
    px, py, pw, ph = lx[0] - 60, ly - 58, (lx[2] - lx[0]) + 120, 116
    f.append(rect(px, py, pw, ph, fill="#f7f7f9", stroke=MUTED, sw=1.6, rx=12))
    f.append(text(px + pw / 2, py - 10, "корпус 5050 (5×5 мм) — одна збірка з трьох кристалів", size=11, color=MUTED))

    top_pin_y = 300           # рядок пінів R,G,B (унизу)
    for (col, lab), x in zip(cols, lx):
        led_symbol(f, x, ly, col)
        # анод (вершина трикутника — вниз): виводимо катод трикутника вгору? ні —
        # у нашому символі вершина = катод (низ), пласка сторона = анод (верх).
        # Анод (верх) веде ВНИЗ повз символ до свого піна прямою вертикаллю збоку.
        ax = x + 28
        f.append(line(x, ly - 15, ax, ly - 15, color=col, sw=2.0))   # від анода вбік
        f.append(line(ax, ly - 15, ax, top_pin_y, color=col, sw=2.0))  # вниз до піна

    # спільна шина катодів — трохи нижче символів, веде ліворуч до піна −
    bus_y = ly + 40
    for x in lx:
        f.append(line(x, ly + 15, x, bus_y, color=INK, sw=2.0))
    f.append(line(lx[0], bus_y, lx[2], bus_y, color=INK, sw=2.6))
    # вивід спільного катода — ліворуч і вниз до піна −
    cath_x = lx[0]
    f.append(line(cath_x, bus_y, cath_x - 90, bus_y, color=INK, sw=2.6))
    f.append(line(cath_x - 90, bus_y, cath_x - 90, top_pin_y, color=INK, sw=2.6))

    # ── піни внизу: −  R  G  B (− окремо ліворуч, R/G/B під своїми кристалами) ──
    pin_defs = [("−", INK, cath_x - 90), ("R", RED, lx[0] + 28),
                ("G", GRN, lx[1] + 28), ("B", BLU, lx[2] + 28)]
    for lab, col, x in pin_defs:
        f.append(rect(x - 8, top_pin_y, 16, 30, fill="#d9c27a", stroke=INK, sw=1.2, rx=3))
        f.append(text(x, top_pin_y + 50, lab, size=16, bold=True, color=col))
    # підпис спільного катода — біля піна, зсунутий ліворуч від його вертикального дроту
    f.append(text(cath_x - 90, top_pin_y + 68, "спільний катод (−)", size=10.5, bold=True, color=INK, anchor="middle"))

    # застереження праворуч — жодних резисторів на платі
    b, _, _ = textbox(838, 150,
                      "На платі НЕМАЄ\nрезисторів!\nГолий кристал —\nструм лічиш сам",
                      size=11, fill="#fdecea", stroke=RED, bold=True)
    f.append(b)

    # підказка про порядок пінів ліворуч
    b, _, _ = textbox(150, 250,
                      "Порядок пінів\nзалежить від версії:\n− R G B  або  − G R B\n(читай напис!)",
                      size=10.5, fill="#eef3fb", stroke=BLU)
    f.append(b)

    render(os.path.join(IMG, "ky009-internal.svg"), W, H, *f)


# ── 2. Розводка пін-у-пін: модуль → резистори → PWM-піни МК ────────────────────
def fig_wiring():
    W, H = 900, 480
    f = [text(W / 2, 30, "Підключення KY-009 до мікроконтролера: три резистори — обовʼязково", size=16, bold=True)]

    # ── ліворуч: модуль KY-009 з 4 пінами ────────────────────────────────
    mx, my, mw, mh = 70, 120, 150, 230
    f.append(rect(mx, my, mw, mh, fill="#eef3fb", stroke=BLU, sw=2.0, rx=12))
    f.append(text(mx + mw / 2, my + 26, "KY-009", size=14, bold=True, color=BLU))
    f.append(text(mx + mw / 2, my + 46, "RGB SMD", size=10.5, color=MUTED))

    pins = [("−", INK, "GND"), ("R", RED, None), ("G", GRN, None), ("B", BLU, None)]
    pin_gap = 44
    py0 = my + 78
    mod_py = [py0 + i * pin_gap for i in range(4)]
    for (lab, col, _), y in zip(pins, mod_py):
        f.append(rect(mx + mw - 6, y - 7, 16, 14, fill="#d9c27a", stroke=INK, sw=1.1, rx=2))
        f.append(text(mx + 20, y + 4, lab, size=14, bold=True, color=col))

    # ── праворуч: плата МК ───────────────────────────────────────────────
    bx, bw = 640, 190
    by, bh = 120, 230
    f.append(rect(bx, by, bw, bh, fill="#eef6ef", stroke=FIELD, sw=2.0, rx=12))
    f.append(text(bx + bw / 2, by + 26, "мікроконтролер", size=13, bold=True, color=FIELD))
    f.append(text(bx + bw / 2, by + 46, "піни з PWM (~)", size=10.5, color=MUTED))

    mcu_labels = ["GND", "D9 ~", "D10 ~", "D11 ~"]
    mcu_py = [py0 + i * pin_gap for i in range(4)]
    for lab, y in zip(mcu_labels, mcu_py):
        f.append(rect(bx - 10, y - 7, 16, 14, fill="#d9c27a", stroke=INK, sw=1.1, rx=2))
        f.append(text(bx + 44, y + 4, lab, size=12, bold=True, color=INK))

    # ── дроти: − напряму до GND; R/G/B через резистор ────────────────────
    res_x = 370
    res_labels = [None, "180 Ω", "110 Ω", "110 Ω"]
    wire_cols = [INK, RED, GRN, BLU]
    for i, (y_from, y_to, col, rl) in enumerate(zip(mod_py, mcu_py, wire_cols, res_labels)):
        xa = mx + mw + 10
        xb = bx - 10
        if rl is None:
            # спільна земля — прямий дріт
            f.append(line(xa, y_from, xb, y_to, color=col, sw=2.0))
        else:
            # від піна до резистора
            f.append(line(xa, y_from, res_x - 34, y_from, color=col, sw=2.0))
            # резистор — прямокутник
            f.append(rect(res_x - 34, y_from - 11, 68, 22, fill=BG, stroke=INK, sw=1.5, rx=3))
            f.append(text(res_x, y_from + 4, rl, size=11, bold=True, color=INK))
            # від резистора до піна МК
            f.append(line(res_x + 34, y_from, xb, y_to, color=col, sw=2.0))

    # пояснення резисторів — унизу, окремою рамкою
    b, _, _ = textbox(W / 2, 420,
                      "R = (5 В − Vf) / 20 мА:   черв. (Vf 1.8) → 160→180 Ω,   зел./син. (Vf 2.8) → 110 Ω.\n"
                      "Без цих резисторів кристал згорить першою ж вмикачкою.",
                      size=11, fill="#fdecea", stroke=RED)
    f.append(b)

    render(os.path.join(IMG, "ky009-wiring.svg"), W, H, *f)


# ── 3. Гамма-крива: чому 128 не половина яскравості (до вставки proj) ──────────
def fig_gamma():
    import math
    W, H = 900, 560
    f = [text(W / 2, 30, "Чому 128 не «половина»: крива, якою око бачить яскравість", size=16, bold=True)]

    # координатна рамка графіка
    gx, gy = 120, 90          # лівий-верхній кут поля графіка
    gw, gh = 560, 380         # ширина/висота поля
    f.append(rect(gx, gy, gw, gh, fill="#fbfbfd", stroke=MUTED, sw=1.4, rx=6))

    # осі
    f.append(line(gx, gy + gh, gx + gw, gy + gh, color=INK, sw=1.8))   # X
    f.append(line(gx, gy, gx, gy + gh, color=INK, sw=1.8))            # Y
    f.append(text(gx + gw / 2, gy + gh + 44, "значення в коді  (analogWrite 0…255)", size=12, color=INK))
    # підпис осі Y — вертикально
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">%s</text>'
             % (gx - 46, gy + gh / 2, FONT, INK, gx - 46, gy + gh / 2, esc("сприйнята оком яскравість")))

    # поділки 0 / 128 / 255 на X
    for frac, lab in [(0, "0"), (0.5, "128"), (1.0, "255")]:
        x = gx + frac * gw
        f.append(line(x, gy + gh, x, gy + gh + 6, color=INK, sw=1.4))
        f.append(text(x, gy + gh + 22, lab, size=11, color=MUTED))
    for frac, lab in [(0, "0%"), (0.5, "50%"), (1.0, "100%")]:
        y = gy + gh - frac * gh
        f.append(line(gx - 6, y, gx, y, color=INK, sw=1.4))
        f.append(text(gx - 22, y + 4, lab, size=11, color=MUTED))

    def X(v):   # код 0..255 -> піксель
        return gx + (v / 255.0) * gw

    def Y(b):   # яскравість 0..1 -> піксель
        return gy + gh - b * gh

    # діагональ «лінійно» — те, що НАЇВНО очікуєш (код = яскравість)
    f.append(line(X(0), Y(0), X(255), Y(1.0), color=MUTED, sw=1.6, dash="6 5"))

    # крива «як бачить око»: фактична світність pin-а лінійна по коду (v/255),
    # але СПРИЙНЯТА яскравість ≈ (v/255)^(1/2.2) — росте круто на початку.
    pts_perc = []
    for i in range(0, 256, 4):
        b = (i / 255.0) ** (1 / 2.2)
        pts_perc.append("%.1f,%.1f" % (X(i), Y(b)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts_perc), POS))

    # крива гама-виправлення, яку кладемо в таблицю: out = (v/255)^2.2 * 255,
    # тобто СВІТНІСТЬ, що дає РІВНОМІРНЕ сприйняття (нижня, «провисла»).
    pts_gam = []
    for i in range(0, 256, 4):
        b = (i / 255.0) ** 2.2
        pts_gam.append("%.1f,%.1f" % (X(i), Y(b)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts_gam), NEG))

    # маркер: код 128 -> сприйнята ≈ 73 % (по червоній), а не 50 %
    b128 = (128 / 255.0) ** (1 / 2.2)
    f.append(line(X(128), gy + gh, X(128), Y(b128), color=POS, sw=1.2, dash="3 4"))
    f.append(line(gx, Y(b128), X(128), Y(b128), color=POS, sw=1.2, dash="3 4"))
    f.append(circle(X(128), Y(b128), 4.5, fill=POS, stroke=BG, sw=1.4))
    f.append(text(X(128) + 8, Y(b128) - 10, "≈ 73 %, не 50 %!", size=11, bold=True, color=POS, anchor="start"))

    # легенда — праворуч, окремими рамками, з запасом
    lx0 = gx + gw + 30
    b, w, _ = textbox(lx0 + 78, 130, "наївне очікування\n(код = яскравість)", size=10.5,
                      fill="#f4f6f8", stroke=MUTED)
    f.append(b)
    b, w, _ = textbox(lx0 + 78, 200, "як око БАЧИТЬ\nсирий код", size=10.5,
                      fill="#fdecea", stroke=POS, bold=True)
    f.append(b)
    b, w, _ = textbox(lx0 + 78, 270, "світність після\nгама-таблиці →\nрівне сприйняття", size=10.5,
                      fill="#eaf0fd", stroke=NEG, bold=True)
    f.append(b)

    # висновок унизу
    b, _, _ = textbox(W / 2, 522,
                      "Око стискає верх діапазону: подвій код — яскравість зросте менш ніж удвічі.\n"
                      "Щоб згасання було плавним, код проганяють крізь криву v → (v/255)^2.2.",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "ky009-gamma.svg"), W, H, *f)


if __name__ == "__main__":
    fig_internal()
    fig_wiring()
    fig_gamma()
    print("OK: img/ky009-internal.svg, img/ky009-wiring.svg, img/ky009-gamma.svg")
