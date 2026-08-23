# -*- coding: utf-8 -*-
"""Фігури вставки proj «Прямий + зворотний зв'язок» (два ступені свободи).
Окремий генератор, щоб не чіпати figs.py теми. Запуск: python figs-proj-ff.py → ./img/proj-ff-*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: структура коду одного такту ────────────────────────────────────
# Дві гілки (u_ff з моделі, u_fb з ПІ) → сума → СПІЛЬНЕ насичення → орган;
# і петля антивіндапу: зрізане (u_sat − u) вертається в інтегратор.
def fig_blockdiagram():
    W, H = 760, 430
    frags = []

    # завдання r ліворуч
    r_x, r_y = 60, 150
    frags.append(text(r_x, r_y - 16, "завдання r", size=13, color=MUTED))
    frags.append(circle(r_x, r_y, 5, fill=INK, stroke=INK))
    # роздвоєння вузол
    split_x = 120
    frags.append(line(r_x, r_y, split_x, r_y, color=LINE))
    frags.append(circle(split_x, r_y, 3.5, fill=INK, stroke=INK))

    # верхня гілка: прямий зв'язок (модель)
    ff_cx, ff_cy = 300, 80
    b, wff, hff = textbox(ff_cx, ff_cy, ["прямий зв'язок F", "u_ff = модель(r)"],
                          size=13, fill="#eef7f0", stroke=FIELD, sw=2.0)
    frags.append(b)
    frags.append(line(split_x, r_y, split_x, ff_cy, color=LINE))
    frags.append(arrow(split_x, ff_cy, ff_cx - wff / 2, ff_cy, color=FIELD))

    # нижня гілка: суматор помилки → ПІ
    sum_x, sum_y = 230, 220
    frags.append(minus(sum_x, sum_y, r=12))
    frags.append(line(split_x, r_y, split_x, sum_y, color=LINE))
    frags.append(arrow(split_x, sum_y, sum_x - 12, sum_y, color=LINE))
    frags.append(text(sum_x - 26, sum_y - 16, "+", size=15, color=POS, bold=True))

    fb_cx, fb_cy = 380, 220
    b, wfb, hfb = textbox(fb_cx, fb_cy, ["зворотний зв'язок C", "u_fb = ПІ(e)"],
                          size=13, fill="#eef2fd", stroke=NEG, sw=2.0)
    frags.append(b)
    frags.append(arrow(sum_x + 12, sum_y, fb_cx - wfb / 2, sum_y, color=LINE))
    frags.append(text((sum_x + fb_cx) / 2, sum_y - 12, "e", size=13, color=INK, italic=True))

    # суматор гілок Σ
    add_x, add_y = 540, 150
    frags.append(plus(add_x, add_y, r=13))
    # u_ff вниз у Σ
    frags.append(line(ff_cx + wff / 2, ff_cy, add_x, ff_cy, color=FIELD))
    frags.append(arrow(add_x, ff_cy, add_x, add_y - 13, color=FIELD))
    # u_fb вгору у Σ
    frags.append(line(fb_cx + wfb / 2, fb_cy, add_x, fb_cy, color=NEG))
    frags.append(arrow(add_x, fb_cy, add_x, add_y + 13, color=NEG))
    frags.append(text(add_x + 40, add_y - 44, "u_ff", size=12, color=FIELD, bold=True))
    frags.append(text(add_x + 40, add_y + 52, "u_fb", size=12, color=NEG, bold=True))

    # спільне насичення на СУМІ
    sat_cx, sat_cy = 650, 150
    b, wsat, hsat = textbox(sat_cx, sat_cy, ["СПІЛЬНЕ", "насичення", "[U_MIN..U_MAX]"],
                            size=12, fill="#fdecea", stroke=POS, sw=2.2)
    frags.append(b)
    frags.append(text(add_x + 20, add_y - 12, "u", size=13, color=INK, italic=True))
    frags.append(arrow(add_x + 13, add_y, sat_cx - wsat / 2, add_y, color=LINE))

    # вихід u_sat до органу
    out_x = 730
    frags.append(arrow(sat_cx + wsat / 2, sat_cy, out_x, sat_cy, color=LINE))
    frags.append(text(out_x - 4, sat_cy - 14, "u_sat", size=12, color=INK, bold=True))
    frags.append(text(out_x - 4, sat_cy + 22, "до органу", size=11, color=MUTED))

    # петля антивіндапу: (u_sat − u) назад в інтегратор ПІ
    aw_y = 340
    frags.append(line(sat_cx, sat_cy + hsat / 2, sat_cx, aw_y, color=POS, dash="5,4"))
    frags.append(line(add_x, add_y + 13, add_x, aw_y, color=POS, dash="5,4"))
    frags.append(text((add_x + sat_cx) / 2, aw_y + 18,
                      "різниця  u_sat − u", size=12, color=POS, bold=True))
    # стрілка назад у блок ПІ
    frags.append(line(sat_cx, aw_y, add_x, aw_y, color=POS, dash="5,4"))
    frags.append(line(add_x, aw_y, fb_cx, aw_y, color=POS, dash="5,4"))
    frags.append(arrow(fb_cx, aw_y, fb_cx, fb_cy + hfb / 2, color=POS))
    frags.append(text(fb_cx + 96, aw_y - 8, "антивіндап", size=11, color=POS))

    render(os.path.join(IMG, "proj-ff-blockdiagram.svg"), W, H, *frags,
           title="Один такт: дві гілки, спільна межа, антивіндап за зрізаним")


# ── Фігура 2: пастка подвійного обрізання ────────────────────────────────────
# Ліворуч (ХИБНО): кожну гілку зрізали окремо → сума однаково впирається,
# але керована частина u_fb втратила діапазон. Праворуч (ПРАВИЛЬНО): межа на сумі.
def fig_double_clip():
    W, H = 760, 360
    frags = []
    frags.append(line(W / 2, 60, W / 2, H - 20, color=MUTED, dash="3,5"))

    def bar(x0, base_y, val, w, color, cap=None, label=None, lab_col=None):
        # стовпчик угору від base_y на val пікселів
        out = rect(x0, base_y - val, w, val, fill=color, stroke=LINE, sw=1.2, rx=3)
        if cap is not None:
            out += line(x0 - 6, base_y - cap, x0 + w + 6, base_y - cap, color=POS, sw=2.2)
        if label:
            out += text(x0 + w / 2, base_y + 16, label, size=12, color=lab_col or INK, bold=True)
        return out

    base = 280
    umax = 190  # пікселів = стеля

    # ── ХИБНО: обрізаємо кожну гілку ──
    frags.append(text(190, 50, "ХИБНО: межа на кожній гілці", size=14, color=POS, bold=True))
    frags.append(line(60, base, 330, base, color=INK, sw=1.5))
    frags.append(line(60, base - umax, 330, base - umax, color=POS, sw=1.6, dash="6,4"))
    frags.append(text(322, base - umax - 8, "U_MAX", size=11, color=POS, anchor="end"))
    # u_ff уже сам на стелі → зрізаний до U_MAX
    frags.append(bar(80, base, umax, 46, FIELD, cap=None, label="u_ff", lab_col=FIELD))
    frags.append(text(103, base - umax - 10, "зрізаний", size=10, color=POS))
    # u_fb хоче додати, але його теж обрізають окремо; сумі нема куди рости
    frags.append(bar(160, base, umax, 46, NEG, label="u_fb", lab_col=NEG))
    frags.append(text(183, base - umax - 10, "теж", size=10, color=POS))
    # «сума» — обидва вперлись, керування мертве
    frags.append(bar(250, base, umax, 46, "#b0453a", label="u_ff+u_fb", lab_col=INK))
    frags.append(text(273, base - umax - 26, "×", size=22, color=POS, bold=True))
    frags.append(text(273, base + 34, "керма нема", size=10, color=POS))

    # ── ПРАВИЛЬНО: сумуємо, тоді одна межа ──
    frags.append(text(575, 50, "ПРАВИЛЬНО: межа на сумі", size=14, color=FIELD, bold=True))
    frags.append(line(430, base, 720, base, color=INK, sw=1.5))
    frags.append(line(430, base - umax, 720, base - umax, color=POS, sw=1.6, dash="6,4"))
    frags.append(text(712, base - umax - 8, "U_MAX", size=11, color=POS, anchor="end"))
    # u_ff нижче стелі (реальна фонова робота)
    ff_v = 120
    frags.append(bar(470, base, ff_v, 60, FIELD, label="u_ff", lab_col=FIELD))
    # u_fb додається зверху, разом у межах
    fb_v = 45
    frags.append(rect(470, base - ff_v - fb_v, 60, fb_v, fill=NEG, stroke=LINE, sw=1.2, rx=3))
    frags.append(text(560, base - ff_v - fb_v / 2 + 4, "+ u_fb", size=12, color=NEG, bold=True))
    # запас до стелі
    frags.append(line(600, base - ff_v - fb_v, 600, base - umax, color=FIELD, sw=1.4))
    frags.append(text(660, (base - ff_v - fb_v + base - umax) / 2 + 4,
                      "є запас", size=11, color=FIELD))
    frags.append(text(595, base + 34, "керма вистачає", size=10, color=FIELD))

    render(os.path.join(IMG, "proj-ff-double-clip.svg"), W, H, *frags,
           title="Обрізати гілки нарізно проти обрізати їхню суму")


if __name__ == "__main__":
    fig_blockdiagram()
    fig_double_clip()
    print("OK: proj-ff-*.svg згенеровано")
