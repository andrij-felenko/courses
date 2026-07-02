# -*- coding: utf-8 -*-
"""Фігури до теми «Керування крутістю фронту».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Дві крайності й вікно між ними ─────────────────────────────────────────
# Ідея: керування крутістю — це вибір точки на осі. Зліва обрив (дзвін, EMI),
# справа обрив (не встигає, зависає в забороненій зоні). Ціль — вузьке вікно.
def fig_window():
    W, H = 760, 360
    f = []

    f.append(text(W / 2, 34,
                  "Крутість фронту — точка на осі; обидва краї — обрив",
                  size=13, color=MUTED, italic=True))

    # горизонтальна вісь швидкості
    ax_y = 250
    f.append(line(70, ax_y, 690, ax_y, color=INK, sw=2))
    f.append(arrow(70, ax_y, 60, ax_y, color=INK, sw=2))        # повільніше вліво
    f.append(arrow(690, ax_y, 700, ax_y, color=INK, sw=2))      # швидше вправо
    f.append(text(90, ax_y + 26, "повільніший фронт", size=10.5, color=MUTED, anchor="start"))
    f.append(text(670, ax_y + 26, "крутіший фронт", size=10.5, color=MUTED, anchor="end"))

    # зелене вікно посередині
    wx0, wx1 = 300, 460
    f.append(rect(wx0, 90, wx1 - wx0, ax_y - 90, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=6))
    f.append(text((wx0 + wx1) / 2, 78, "робоче вікно", size=11, color=FIELD, bold=True))

    # ── ліва біда: занадто повільно ──
    def slow_wave(x0):
        pts = []
        for i in range(0, 60):
            xx = x0 + i * 1.6
            # млява крива, ледь піднімається
            import math
            yy = ax_y - 40 - 40 * (1 - math.exp(-i / 40.0))
            pts.append("%d,%d" % (xx, yy))
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), POS)
    f.append(slow_wave(120))
    f.append(fitbox(80, 298, 190, 48,
                    "зависає в забороненій\nзоні; межа швидкості",
                    size=10, fill="#fdecea", stroke=POS, sw=1.4))

    # ── права біда: занадто круто (дзвін) ──
    def ring_wave(x0):
        import math
        pts = []
        for i in range(0, 62):
            xx = x0 + i * 1.6
            if i < 6:
                yy = ax_y - 40 - (i / 6.0) * 55
            else:
                # затухаючий дзвін над рівнем
                d = i - 6
                yy = ax_y - 40 - 55 - 22 * math.exp(-d / 14.0) * math.cos(d / 3.0)
            pts.append("%d,%d" % (xx, yy))
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), POS)
    f.append(ring_wave(520))
    f.append(fitbox(500, 298, 200, 48,
                    "викид над VDD, дзвін,\nEMI, відбиття",
                    size=10, fill="#fdecea", stroke=POS, sw=1.4))

    # ── у вікні: у міру ──
    def ok_wave(x0):
        import math
        pts = []
        for i in range(0, 44):
            xx = x0 + i * 1.5
            yy = ax_y - 40 - 55 * (1 - math.exp(-i / 12.0))
            pts.append("%d,%d" % (xx, yy))
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), FIELD)
    f.append(ok_wave(330))

    render(os.path.join(IMG, "window.svg"), W, H, *f)


# ── 2. Сегментований драйвер: N паралельних ключів, вмикай скільки треба ──────
# Ідея: керована крутість у чипі — це N маленьких транзисторів пліч-о-пліч;
# скільки з них відкрито (і чи одночасно), таким і виходить нахил.
def fig_segmented():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 32,
                  "Усередині: один «сильний» ключ — це N маленьких паралельних",
                  size=12.5, color=MUTED, italic=True))

    vdd_y = 70
    pin_x = 470
    # шина VDD
    f.append(line(120, vdd_y, 420, vdd_y, color=POS, sw=2))
    f.append(text(110, vdd_y + 4, "VDD", size=11, color=POS, bold=True, anchor="end"))

    # чотири паралельні верхні ключі
    seg_x = [160, 230, 300, 370]
    on = [True, True, False, False]   # відкрито 2 з 4
    for i, x in enumerate(seg_x):
        col = FIELD if on[i] else MUTED
        f.append(line(x, vdd_y, x, 140, color=col, sw=2 if on[i] else 1.4))
        f.append(rect(x - 16, 140, 32, 40, fill="#eef6ef" if on[i] else FILL,
                      stroke=col, sw=1.8 if on[i] else 1.3, rx=6))
        f.append(text(x, 165, "P%d" % (i + 1), size=10, color=col, bold=on[i]))
        # вниз до спільного вузла
        f.append(line(x, 180, x, 230, color=col, sw=2 if on[i] else 1.4))
        f.append(line(x, 230, pin_x, 230, color=col, sw=2 if on[i] else 1.4))
        # позначка «дозвіл»
        state = "on" if on[i] else "off"
        f.append(text(x, 128, state, size=9, color=col, bold=on[i]))

    # спільний вузол → ніжка
    f.append(circle(pin_x, 230, 5, fill=INK, stroke=INK))
    f.append(line(pin_x, 230, 560, 230, color=INK, sw=2.4))
    f.append(text(575, 234, "ніжка", size=11, color=INK, bold=True, anchor="start"))
    f.append(text(575, 250, "→ навантаження C", size=9.5, color=MUTED, anchor="start"))

    # регістр керування зліва
    f.append(rect(70, 250, 150, 120, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8))
    f.append(text(145, 274, "регістр", size=11, color=NEG, bold=True))
    f.append(text(145, 292, "DRIVE / SLEW", size=10, color=INK, bold=True))
    f.append(text(145, 316, "скільки ключів", size=9.5, color=MUTED))
    f.append(text(145, 332, "відкрити — і чи", size=9.5, color=MUTED))
    f.append(text(145, 348, "разом, чи по черзі", size=9.5, color=MUTED))
    f.append(arrow(220, 300, 300, 190, color=NEG, sw=1.5))

    # висновок
    f.append(fitbox(300, 300, 430, 44,
                    "Більше відкритих ключів → менший опір → крутіший фронт (drive).\n"
                    "Вмикати їх сходинками із затримкою → м'якший нахил (slew).",
                    size=10, fill="#fbfbfb", stroke=MUTED, sw=1.4))

    render(os.path.join(IMG, "segmented.svg"), W, H, *f)


# ── 3. Зовнішнє гальмо: послідовний резистор + ємність лінії = RC ─────────────
# Ідея: якщо драйвер незмінний, крутість гальмують ЗОВНІ — резистор у лінію,
# який разом з ємністю навантаження робить RC і згладжує фронт.
def fig_series_rc():
    W, H = 760, 360
    f = []

    f.append(text(W / 2, 32,
                  "Драйвер незмінний? Гальмуй зовні: R у лінію + ємність = RC",
                  size=12.5, color=MUTED, italic=True))

    # драйвер
    f.append(rect(60, 120, 120, 90, fill="#f4f6f8", stroke=LINE, sw=2, rx=10))
    f.append(text(120, 150, "драйвер", size=12, color=INK, bold=True))
    f.append(text(120, 170, "різкий фронт", size=10, color=POS))
    f.append(text(120, 190, "(як є)", size=9.5, color=MUTED))

    # резистор у лінію
    ry = 150
    f.append(line(180, ry, 250, ry, color=INK, sw=2))
    f.append(rect(250, ry - 12, 70, 24, fill="#fff6e5", stroke="#b8860b", sw=1.8, rx=4))
    f.append(text(285, ry + 4, "Rs", size=11, color="#8a6d0b", bold=True))
    f.append(text(285, ry - 22, "22…100 Ω", size=9.5, color=MUTED))
    f.append(line(320, ry, 470, ry, color=INK, sw=2))

    # вузол приймача з ємністю
    f.append(circle(470, ry, 5, fill=INK, stroke=INK))
    f.append(rect(490, 120, 120, 90, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    f.append(text(550, 150, "приймач", size=12, color=NEG, bold=True))
    f.append(text(550, 172, "+ ємність", size=10, color=INK))
    f.append(text(550, 190, "лінії C", size=10, color=INK))

    # конденсатор на землю від вузла
    cap_y = 250
    f.append(line(470, ry, 470, cap_y - 14, color=NEG, sw=1.8))
    f.append(line(456, cap_y - 14, 484, cap_y - 14, color=NEG, sw=2.4))
    f.append(line(456, cap_y - 6, 484, cap_y - 6, color=NEG, sw=2.4))
    f.append(text(500, cap_y - 8, "C (затвор+дріт)", size=9.5, color=NEG, anchor="start"))
    f.append(line(456, cap_y + 2, 484, cap_y + 2, color=INK, sw=2))  # земля
    f.append(line(462, cap_y + 7, 478, cap_y + 7, color=INK, sw=1.6))
    f.append(line(467, cap_y + 12, 473, cap_y + 12, color=INK, sw=1.2))

    # маленький графік згладженого фронту над резистором
    import math
    pts = []
    gx0, gy0 = 250, 70
    for i in range(0, 60):
        xx = gx0 + i * 1.3
        yy = gy0 + 22 - 22 * (1 - math.exp(-i / 20.0))
        pts.append("%d,%d" % (xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), FIELD))
    f.append(text(gx0 + 40, gy0 - 4, "фронт згладжено", size=9.5, color=FIELD))

    f.append(fitbox(120, 288, 520, 42,
                    "τ = Rs·C, тож tr ≈ 2.2·Rs·C. Ставити Rs треба ВПРИТУЛ до драйвера.\n"
                    "Дешево й надійно, але однаковий тормоз на весь бік лінії.",
                    size=10, fill="#fbfbfb", stroke=MUTED, sw=1.4))

    render(os.path.join(IMG, "series-rc.svg"), W, H, *f)


# ── 4. Скільки саме крутості треба: бюджет фронту від довжини й швидкості ─────
# Ідея: ціль не «якнайкрутіше», а «рівно скільки треба». Дві межі: знизу —
# швидкість даних (фронт має бути коротший за біт), згори — довжина лінії
# (надто крутий на довгому дроті → відбиття/EMI). Вибирай між ними.
def fig_budget():
    W, H = 760, 380
    f = []

    f.append(text(W / 2, 32,
                  "Ціль — не «якнайкрутіше», а «рівно скільки треба»",
                  size=12.5, color=MUTED, italic=True))

    # вертикальна вісь крутості
    ax_x = 120
    f.append(line(ax_x, 300, ax_x, 70, color=INK, sw=2))
    f.append(arrow(ax_x, 70, ax_x, 60, color=INK, sw=2))
    f.append(text(ax_x - 8, 64, "крутість", size=10.5, color=INK, anchor="end"))
    f.append(text(ax_x - 8, 300, "млявіше", size=9.5, color=MUTED, anchor="end"))

    # нижня межа (потреба швидкості) — зростає зі швидкістю даних
    f.append(line(ax_x, 250, 660, 150, color=NEG, sw=2, dash="6,5"))
    f.append(text(660, 142, "мінімум: фронт < біта", size=10, color=NEG, anchor="end"))
    f.append(text(500, 210, "швидша шина → крутіший", size=9.5, color=NEG, anchor="middle"))

    # верхня межа (довжина/EMI) — падає з довжиною
    f.append(line(ax_x, 110, 660, 240, color=POS, sw=2, dash="6,5"))
    f.append(text(660, 232, "максимум: довший дріт дзвенить", size=10, color=POS, anchor="end"))

    # робочий коридор між ними (зелений трикутник ліворуч, звужується)
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="#eef6ef" stroke="%s" stroke-width="1.4"/>'
             % (ax_x, 250, ax_x, 110, 470, 195, FIELD))
    f.append(text(250, 185, "коридор", size=11, color=FIELD, bold=True))
    f.append(text(250, 202, "вибору", size=11, color=FIELD, bold=True))

    # горизонтальна вісь
    f.append(line(ax_x, 300, 690, 300, color=INK, sw=2))
    f.append(arrow(690, 300, 700, 300, color=INK, sw=2))
    f.append(text(690, 322, "довжина лінії · швидкість", size=10, color=INK, anchor="end"))

    f.append(fitbox(150, 336, 460, 32,
                    "Крутість бери мінімальну, що ще несе потрібну швидкість — і жодним пікселем крутішу",
                    size=10, fill="#fbfbfb", stroke=MUTED, sw=1.4))

    render(os.path.join(IMG, "budget.svg"), W, H, *f)


if __name__ == "__main__":
    fig_window()
    fig_segmented()
    fig_series_rc()
    fig_budget()
    print("OK: 4 figures ->", IMG)
