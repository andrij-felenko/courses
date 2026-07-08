# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Безколекторний мотор (BLDC)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

STEEL = "#c9ced6"   # залізо статора
COPPER = "#c98a3a"  # мідь обмотки
NP = "#c0392b"      # північний полюс магніту (червоний)
SP = "#2457d6"      # південний полюс (синій)


def coil_tooth(f, cx, cy, ang, r_in, r_out, w_deg, fill):
    """Зуб статора як сектор-трапеція від r_in до r_out під кутом ang (град)."""
    a = math.radians(ang)
    da = math.radians(w_deg / 2)
    def pt(r, aa):
        return (cx + r * math.cos(aa), cy + r * math.sin(aa))
    x1, y1 = pt(r_in, a - da)
    x2, y2 = pt(r_out, a - da)
    x3, y3 = pt(r_out, a + da)
    x4, y4 = pt(r_in, a + da)
    p = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (x1, y1, x2, y2, x3, y3, x4, y4)
    f.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1"/>' % (p, fill, INK))


# ── 1. Будова: статор із обмотками + ротор із магнітами (inrunner) ────────────
def fig_anatomy():
    W, H = 860, 470
    f = [text(W / 2, 30, "Обмотки нерухомі, магніти обертаються — комутатора немає",
              size=16, bold=True)]

    cx, cy = 250, 250
    R_yoke = 150          # зовнішнє ярмо статора
    R_tooth_out = 120     # вершина зуба
    R_tooth_in = 78       # основа зуба (зазор)
    R_rotor = 66          # ротор
    R_shaft = 16

    # ярмо статора (кільце)
    f.append(circle(cx, cy, R_yoke, fill="#eef1f4", stroke=INK, sw=1.8))
    f.append(circle(cx, cy, R_tooth_in - 6, fill="#ffffff", stroke=STEEL, sw=1.2))

    # 12 зубів статора з міддю; 3 фази A,B,C по колу
    phase_col = {0: COPPER, 1: "#7a9e3a", 2: "#3a7a9e"}
    phase_lbl = {0: "A", 1: "B", 2: "C"}
    for i in range(12):
        ang = i * 30 - 90
        pc = phase_col[i % 3]
        coil_tooth(f, cx, cy, ang, R_tooth_in, R_tooth_out, 20, STEEL)
        # витки міді обабіч зуба — дві короткі дуги-кружечки
        a = math.radians(ang)
        rr = (R_tooth_in + R_tooth_out) / 2
        ox, oy = -math.sin(a), math.cos(a)  # нормаль до радіуса
        for s in (-1, 1):
            wx = cx + rr * math.cos(a) + s * 13 * ox
            wy = cy + rr * math.sin(a) + s * 13 * oy
            f.append(circle(wx, wy, 5.5, fill=pc, stroke=INK, sw=0.8))

    # ротор — 4 полюси (2 пари), чергування N/S
    f.append(circle(cx, cy, R_rotor, fill="#dfe3e8", stroke=INK, sw=1.5))
    for k in range(4):
        a0 = math.radians(k * 90 - 90)
        col = NP if k % 2 == 0 else SP
        lab = "N" if k % 2 == 0 else "S"
        # сектор магніту (чверть кільця ротора)
        da = math.radians(40)
        def pr(r, aa):
            return (cx + r * math.cos(aa), cy + r * math.sin(aa))
        pts = []
        steps = 8
        for j in range(steps + 1):
            aa = a0 - da + 2 * da * j / steps
            pts.append(pr(R_rotor - 2, aa))
        for j in range(steps + 1):
            aa = a0 + da - 2 * da * j / steps
            pts.append(pr(R_rotor - 22, aa))
        pstr = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
        f.append('<polygon points="%s" fill="%s" stroke="none"/>' % (pstr, col))
        lx, ly = pr(R_rotor - 12, a0)
        f.append(text(lx, ly + 5, lab, size=15, bold=True, color="#ffffff"))
    # вал
    f.append(circle(cx, cy, R_shaft, fill="#9aa2ad", stroke=INK, sw=1.5))
    f.append(text(cx, cy + 5, "вал", size=11, color="#ffffff"))

    # виноски-підписи справа (поза колом, лінії не перетинають написів)
    lx = 470
    items = [
        (cy - 120, STEEL, "залізне ярмо + зуби статора"),
        (cy - 70, COPPER, "мідні обмотки: 3 фази A · B · C"),
        (cy - 20, NP, "постійні магніти на роторі (N)"),
        (cy + 30, SP, "чергування полюсів (S)"),
        (cy + 80, "#9aa2ad", "вал — вихід моменту"),
    ]
    for yy, col, txt in items:
        f.append(rect(lx, yy - 12, 22, 22, fill=col, stroke=INK, sw=1, rx=4))
        f.append(text(lx + 32, yy + 4, txt, size=13, color=INK, anchor="start"))

    # мітка «зазор»
    f.append(text(cx, cy + R_rotor + 28, "повітряний зазор", size=10, color=MUTED))

    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 2. Inrunner vs Outrunner — що всередині, що зовні ─────────────────────────
def fig_inout():
    W, H = 820, 360
    f = [text(W / 2, 30, "Хто всередині: магніти чи обмотки — inrunner проти outrunner",
              size=16, bold=True)]

    def draw(cx, cy, magnets_outside, title, sub):
        R = 92
        if magnets_outside:
            # зовнішнє кільце — магніти (ротор), всередині — обмотки
            f.append(circle(cx, cy, R, fill="#f2d9d9", stroke=INK, sw=1.6))
            # чергування N/S по зовнішньому кільцю
            for k in range(8):
                a = math.radians(k * 45 - 90)
                col = NP if k % 2 == 0 else SP
                x, y = cx + (R - 12) * math.cos(a), cy + (R - 12) * math.sin(a)
                f.append(circle(x, y, 9, fill=col, stroke="none", sw=0))
            f.append(circle(cx, cy, R - 30, fill="#eef1f4", stroke=INK, sw=1.4))
            # зуби-обмотки всередині
            for i in range(6):
                coil_tooth(f, cx, cy, i * 60 - 90, 18, R - 34, 26, COPPER)
            f.append(circle(cx, cy, 12, fill="#9aa2ad", stroke=INK, sw=1.2))
            f.append(text(cx, cy - R - 12, "корпус з магнітами крутиться", size=10, color=MUTED))
        else:
            # зовнішнє кільце — залізо+обмотки (статор), всередині — магніти-ротор
            f.append(circle(cx, cy, R, fill="#eef1f4", stroke=INK, sw=1.6))
            for i in range(6):
                coil_tooth(f, cx, cy, i * 60 - 90, R - 40, R - 6, 26, COPPER)
            f.append(circle(cx, cy, R - 44, fill="#dfe3e8", stroke=INK, sw=1.4))
            for k in range(4):
                a = math.radians(k * 90 - 90)
                col = NP if k % 2 == 0 else SP
                x, y = cx + (R - 56) * math.cos(a), cy + (R - 56) * math.sin(a)
                f.append(circle(x, y, 11, fill=col, stroke="none", sw=0))
            f.append(circle(cx, cy, 12, fill="#9aa2ad", stroke=INK, sw=1.2))
            f.append(text(cx, cy - R - 12, "вал усередині крутиться", size=10, color=MUTED))
        f.append(text(cx, cy + R + 34, title, size=14, bold=True))
        f.append(text(cx, cy + R + 54, sub, size=11, color=MUTED))

    draw(210, 175, False, "Inrunner", "ротор усередині · високі оберти")
    draw(610, 175, True, "Outrunner", "ротор зовні · високий момент")

    render(os.path.join(IMG, "inrunner-outrunner.svg"), W, H, *f)


# ── 3. Підключення: мотор → ESC → батарея + сигнал від МК ─────────────────────
def fig_wiring():
    W, H = 860, 400
    f = [text(W / 2, 30, "Три фази — на ESC; ESC живиться від батареї й слухає МК",
              size=16, bold=True)]

    # мотор (ліворуч)
    mx, my = 130, 210
    f.append(circle(mx, my, 60, fill="#eef1f4", stroke=INK, sw=1.8))
    f.append(text(mx, my - 4, "BLDC", size=15, bold=True))
    f.append(text(mx, my + 16, "мотор", size=11, color=MUTED))
    # три фазні дроти
    ph = [("A", NP), ("B", "#7a9e3a"), ("C", "#3a7a9e")]

    # ESC (центр)
    ex, ey, ew, eh = 330, 120, 190, 180
    f.append(rect(ex, ey, ew, eh, fill="#fafbfc", stroke=INK, sw=1.8, rx=10))
    f.append(text(ex + ew / 2, ey + 26, "ESC", size=15, bold=True))
    f.append(text(ex + ew / 2, ey + 44, "3-фазний інвертор", size=10, color=MUTED))

    # фазні лінії мотор→ESC
    for i, (lab, col) in enumerate(ph):
        yy = my - 34 + i * 34
        f.append(line(mx + 58, yy, ex, yy, color=col, sw=3))
        f.append(text((mx + 58 + ex) / 2, yy - 7, lab, size=12, bold=True, color=col))
    f.append(text((mx + 58 + ex) / 2, my + 78, "три товсті фази", size=10, color=MUTED))

    # батарея (праворуч-угорі)
    bx, by, bw, bh = 640, 96, 150, 70
    f.append(rect(bx, by, bw, bh, fill="#fdf6ec", stroke=INK, sw=1.6, rx=8))
    f.append(text(bx + bw / 2, by + 28, "батарея", size=13, bold=True))
    f.append(text(bx + bw / 2, by + 48, "LiPo · сильний струм", size=10, color=MUTED))
    # живлення батарея→ESC (плюс/мінус)
    f.append(line(ex + ew, ey + 40, bx, by + 24, color=NP, sw=3))
    f.append(plus(bx - 12, by + 24))
    f.append(line(ex + ew, ey + 64, bx, by + 50, color=NEG, sw=3))
    f.append(minus(bx - 12, by + 50))

    # МК (праворуч-унизу)
    cxx, cyy, cw, chh = 640, 220, 150, 70
    f.append(rect(cxx, cyy, cw, chh, fill="#eef7f0", stroke=INK, sw=1.6, rx=8))
    f.append(text(cxx + cw / 2, cyy + 28, "МК / приймач", size=13, bold=True))
    f.append(text(cxx + cw / 2, cyy + 48, "3 дроти сигналу", size=10, color=MUTED))
    # сигнальні лінії ESC→МК: сигнал, +5V, GND
    sy = ey + 110
    for j, (lab, col) in enumerate([("сигнал", INK), ("+5V", NP), ("GND", NEG)]):
        yy = sy + j * 20
        f.append(line(ex + ew, yy, cxx, cyy + 14 + j * 18, color=col, sw=2))
    f.append(text((ex + ew + cxx) / 2, sy - 10, "тонкий джгут керування", size=10, color=MUTED))

    # підпис знизу
    f.append(text(W / 2, H - 16,
                  "струм на мотор дає ESC із батареї; МК лише каже «скільки газу»",
                  size=11, color=MUTED))

    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 4. Часова діаграма керування: озброєння → плавний розгін → скид ───────────
def fig_arm_ramp():
    W, H = 980, 480
    f = [text(W / 2, 30, "Ширина імпульсу в часі: спершу arm-утримання, тоді розгін",
              size=16, bold=True)]

    # система координат (графік — верхня частина; низ лишаємо під виноски)
    ox, oy = 95, 250          # початок осей (лівий-низ графіка)
    plot_w, plot_h = 690, 175    # права колонка (W-ox-plot_w) — під підписи ліній
    us_min, us_max = 900, 2100   # діапазон осі Y (мкс)

    def yv(us):
        return oy - (us - us_min) / (us_max - us_min) * plot_h

    # осі
    f.append(line(ox, oy, ox + plot_w, oy, color=INK, sw=1.6))          # X
    f.append(line(ox, oy, ox, oy - plot_h, color=INK, sw=1.6))          # Y
    f.append(text(ox - 60, oy - plot_h / 2, "ширина", size=12, color=MUTED, anchor="middle"))
    f.append(text(ox - 60, oy - plot_h / 2 + 16, "імпульсу", size=12, color=MUTED, anchor="middle"))

    # горизонтальні орієнтири 1000 / 1500 / 2000 мкс — короткий підпис у правій колонці
    for us, lab, col in [(1000, "1000 (стоп)", NEG),
                         (1500, "1500", MUTED),
                         (2000, "2000 (газ)", NP)]:
        yy = yv(us)
        f.append(line(ox, yy, ox + plot_w, yy, color=col, sw=1, dash="4,4"))
        f.append(text(ox + plot_w + 10, yy + 4, lab, size=11, color=col, anchor="start"))
    f.append(text(ox + plot_w + 10, yv(2000) - 20, "мкс", size=10, color=MUTED, anchor="start"))

    # фази по осі X (частки ширини графіка)
    x0 = ox
    x_arm_end = ox + plot_w * 0.30
    x_ramp_end = ox + plot_w * 0.60
    x_cruise_end = ox + plot_w * 0.82
    x_end = ox + plot_w

    # 1) arm-утримання на 1000 мкс
    y1000 = yv(1000)
    f.append(line(x0, y1000, x_arm_end, y1000, color=INK, sw=3))
    # 2) плавний розгін 1000 → 1700 (згладжена крива, ламаною з кількох сегментів)
    y_cruise = yv(1700)
    steps = 24
    prev = (x_arm_end, y1000)
    for i in range(1, steps + 1):
        t = i / steps
        s = t * t * (3 - 2 * t)               # ease-in-out
        us = 1000 + (1700 - 1000) * s
        cx = x_arm_end + (x_ramp_end - x_arm_end) * t
        cy = yv(us)
        f.append(line(prev[0], prev[1], cx, cy, color=INK, sw=3))
        prev = (cx, cy)
    # 3) крейсер на 1700
    f.append(line(x_ramp_end, y_cruise, x_cruise_end, y_cruise, color=INK, sw=3))
    # 4) плавний скид газу до 1000
    f.append(line(x_cruise_end, y_cruise, x_end, y1000, color=INK, sw=3))

    # підписи фаз під віссю
    def phase_label(xa, xb, s):
        cx = (xa + xb) / 2
        f.append(line(xa, oy + 6, xa, oy + 12, color=MUTED, sw=1))
        f.append(line(xb, oy + 6, xb, oy + 12, color=MUTED, sw=1))
        f.append(text(cx, oy + 26, s, size=11, color=INK))
        return cx

    cx_arm = phase_label(x0, x_arm_end, "озброєння (arm)")
    phase_label(x_arm_end, x_ramp_end, "плавний розгін")
    phase_label(x_ramp_end, x_cruise_end, "робочий газ")
    cx_dec = phase_label(x_cruise_end, x_end, "плавний скид")
    f.append(text(ox + plot_w / 2, oy + 48, "час →", size=12, color=MUTED))

    # ── дві виноски в НИЖНІЙ смузі (поза графіком), з тонким лідером до фази ──
    note_y = oy + 78
    # arm-виноска — ліворуч
    tb = textbox(cx_arm + 40, note_y + 26,
                 ["ESC вимагає ~1-2 с мінімального", "газу на старті, інакше не", "запуститься — це «озброєння»"],
                 size=11, pad=9, fill="#eaf0fd", stroke=NEG, sw=1.2)
    f.append(tb[0])
    f.append(line(cx_arm, oy + 34, cx_arm, note_y + 26 - tb[2] / 2, color=NEG, sw=1, dash="3,3"))

    # back-EMF виноска — праворуч
    tb2 = textbox(cx_dec - 30, note_y + 26,
                  ["різкий скид газу з високих обертів", "жене струм назад у ESC і батарею", "(зворотна ЕРС) — скидай плавно"],
                  size=11, pad=9, fill="#fdf0ee", stroke=NP, sw=1.2)
    f.append(tb2[0])
    f.append(line(cx_dec, oy + 34, cx_dec, note_y + 26 - tb2[2] / 2, color=NP, sw=1, dash="3,3"))

    render(os.path.join(IMG, "arm-ramp.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anatomy()
    fig_inout()
    fig_wiring()
    fig_arm_ramp()
    print("OK: figures written to", IMG)
