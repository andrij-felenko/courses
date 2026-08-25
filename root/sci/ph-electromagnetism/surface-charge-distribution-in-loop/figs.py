# -*- coding: utf-8 -*-
"""Фігури до теми «Поверхневі заряди в колі зі струмом».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"
COLOR_PURPLE = "#8e44ad"
COLOR_DARK = "#1a1a1a"


# ── Фігура 1: Розподіл поверхневого заряду в колі ───────────────────────────
def fig_circuit_surface_charge():
    W, H = 800, 440
    f = []

    x_left, x_right = 160, 640
    y_top, y_bot = 100, 340
    wire_sw = 4.0

    # Джерело живлення ліворуч (батарея)
    f.append(rect(x_left - 25, (y_top + y_bot) / 2 - 40, 50, 80, fill="#eef2f7", stroke=COLOR_DARK, sw=2.0, rx=4))
    f.append(text(x_left, (y_top + y_bot) / 2 - 10, "Джерело", size=12, bold=True))
    f.append(text(x_left, (y_top + y_bot) / 2 + 10, "ЕРС (V₀)", size=12, color=COLOR_DARK))
    f.append(text(x_left, y_top - 12, "+V₀/2", size=12, bold=True, color=COLOR_RED))
    f.append(text(x_left, y_bot + 22, "-V₀/2", size=12, bold=True, color=COLOR_BLUE))

    # Резистор праворуч
    r_w, r_h = 40, 100
    f.append(rect(x_right - r_w / 2, (y_top + y_bot) / 2 - r_h / 2, r_w, r_h, fill="#fff4e6", stroke=COLOR_ORANGE, sw=2.0, rx=3))
    f.append(text(x_right, (y_top + y_bot) / 2, "Резистор R", size=13, bold=True, color=COLOR_ORANGE))

    # Провідники кола
    f.append(line(x_left, y_top, x_right, y_top, color="#4a5568", sw=wire_sw))
    f.append(line(x_left, y_bot, x_right, y_bot, color="#4a5568", sw=wire_sw))
    f.append(line(x_left, y_top, x_left, (y_top + y_bot) / 2 - 40, color="#4a5568", sw=wire_sw))
    f.append(line(x_left, y_bot, x_left, (y_top + y_bot) / 2 + 40, color="#4a5568", sw=wire_sw))
    f.append(line(x_right, y_top, x_right, (y_top + y_bot) / 2 - r_h / 2, color="#4a5568", sw=wire_sw))
    f.append(line(x_right, y_bot, x_right, (y_top + y_bot) / 2 + r_h / 2, color="#4a5568", sw=wire_sw))

    # Напрямок струму
    f.append(arrow(340, y_top, 380, y_top, color=COLOR_GREEN, sw=2.2))
    f.append(text(400, y_top - 14, "Струм I", size=13, bold=True, color=COLOR_GREEN))
    f.append(arrow(400, y_bot, 360, y_bot, color=COLOR_GREEN, sw=2.2))

    # Поверхневі заряди (+ червоні зверху, - сині знизу)
    pos_x = [190, 240, 290, 340, 390, 440, 490, 540, 590]
    for px in pos_x:
        f.append(text(px, y_top - 8, "+", size=14, bold=True, color=COLOR_RED))
        f.append(text(px, y_top + 16, "+", size=14, bold=True, color=COLOR_RED))
        f.append(text(px, y_bot - 8, "−", size=14, bold=True, color=COLOR_BLUE))
        f.append(text(px, y_bot + 16, "−", size=14, bold=True, color=COLOR_BLUE))

    # Зовнішнє електричне поле E_ext
    for fx in [240, 360, 480, 600]:
        f.append(line(fx, y_top + 22, fx, y_bot - 20, color=COLOR_PURPLE, sw=1.2, dash="4,4"))
        f.append(arrow(fx, 210, fx, 230, color=COLOR_PURPLE, sw=1.5))
    f.append(text(360, 220, "Зовнішнє поле E_ext", size=12, bold=True, color=COLOR_PURPLE))

    # Внутрішнє поле E_in
    f.append(arrow(220, y_top, 270, y_top, color=COLOR_RED, sw=2.0))
    f.append(text(245, y_top + 24, "E_in", size=11, bold=True, color=COLOR_RED))

    # Потенціали
    f.append(text(x_right + 35, y_top + 10, "Високий потенціал", size=11, color=COLOR_RED))
    f.append(text(x_right + 35, y_bot - 10, "Низький потенціал", size=11, color=COLOR_BLUE))

    # Легенда
    box_txt = "Поверхневий заряд σ_s пропорційний локальному потенціалу V(s).\nВін створює внутрішнє напрямне поле E_in та зовнішнє поле E_ext."
    tb, _, _ = textbox(W / 2, 395, box_txt, size=12, fill="#f8fafc", stroke="#cbd5e1", pad=8)
    f.append(tb)

    render(os.path.join(IMG, 'circuit-surface-charge-distribution.svg'), W, H, "\n".join(f),
           title="Розподіл поверхневого заряду та полів у замкненому колі зі струмом")


# ── Фігура 2: Вигин дроту та перехід перерізу ───────────────────────────────
def fig_wire_bend_and_cross_section():
    W, H = 800, 400
    f = []

    midx = W / 2
    f.append(line(midx, 45, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- ПАНЕЛЬ А: Поворот дроту (ліворуч) ---
    f.append(text(midx / 2, 50, "а) Поворот провідника на 90°", size=14, bold=True, color=COLOR_DARK))

    bx, by = 70, 100
    w_thick = 50
    f.append(rect(bx, by, w_thick, 100, fill="#e2e8f0", stroke="#64748b", sw=1.8))
    f.append(rect(bx, by + 100, 160, w_thick, fill="#e2e8f0", stroke="#64748b", sw=1.8))
    f.append(rect(bx + 1, by + 100 + 1, w_thick - 2, w_thick - 2, fill="#e2e8f0", stroke="none", sw=0))

    # Скупчення поверхневого заряду
    f.append(text(bx - 12, by + 90, "+", size=15, bold=True, color=COLOR_RED))
    f.append(text(bx - 12, by + 110, "+", size=15, bold=True, color=COLOR_RED))
    f.append(text(bx - 12, by + 130, "+", size=15, bold=True, color=COLOR_RED))
    f.append(text(bx + 15, by + 162, "+", size=15, bold=True, color=COLOR_RED))

    f.append(text(bx + w_thick + 8, by + 85, "−", size=15, bold=True, color=COLOR_BLUE))
    f.append(text(bx + w_thick + 8, by + 98, "−", size=15, bold=True, color=COLOR_BLUE))

    # Вектори
    f.append(arrow(bx + 25, by + 30, bx + 25, by + 70, color=COLOR_GREEN, sw=2.0))
    f.append(text(bx + 32, by + 50, "J₁", size=12, bold=True, color=COLOR_GREEN))

    f.append(arrow(bx + 10, by + 125, bx + 40, by + 125, color=COLOR_PURPLE, sw=1.8))
    f.append(text(bx + 20, by + 140, "E_trans", size=11, bold=True, color=COLOR_PURPLE))

    f.append(arrow(bx + 90, by + 125, bx + 140, by + 125, color=COLOR_GREEN, sw=2.0))
    f.append(text(bx + 115, by + 112, "J₂", size=12, bold=True, color=COLOR_GREEN))

    tb_a, _, _ = textbox(midx / 2, 335, "Заряд на зовнішньому куті створює\nпоперечне поле E_trans, яке повертає\nтраєкторію носіїв заряду.", size=11, fill="#f8fafc", pad=6)
    f.append(tb_a)

    # --- ПАНЕЛЬ Б: Стрибок перерізу (праворуч) ---
    f.append(text(midx + midx / 2, 50, "б) Стрибок перерізу (A₁ → A₂)", size=14, bold=True, color=COLOR_DARK))

    cx, cy = midx + 60, 150
    f.append(rect(cx, cy - 40, 100, 80, fill="#e2e8f0", stroke="#64748b", sw=1.8))
    f.append(text(cx + 40, cy - 48, "Товстий (A₁)", size=12, bold=True))

    f.append(rect(cx + 100, cy - 20, 120, 40, fill="#cbd5e1", stroke="#64748b", sw=1.8))
    f.append(text(cx + 160, cy - 28, "Тонкий (A₂ < A₁)", size=12, bold=True))

    f.append(arrow(cx + 20, cy, cx + 70, cy, color=COLOR_RED, sw=1.8))
    f.append(text(cx + 45, cy + 18, "E₁ (менше)", size=11, bold=True, color=COLOR_RED))

    f.append(arrow(cx + 120, cy, cx + 190, cy, color=COLOR_RED, sw=2.5))
    f.append(text(cx + 155, cy + 18, "E₂ (більше)", size=11, bold=True, color=COLOR_RED))

    f.append(text(cx + 92, cy - 30, "+", size=14, bold=True, color=COLOR_RED))
    f.append(text(cx + 92, cy + 30, "+", size=14, bold=True, color=COLOR_RED))
    f.append(text(cx + 102, cy - 30, "+", size=14, bold=True, color=COLOR_RED))
    f.append(text(cx + 102, cy + 30, "+", size=14, bold=True, color=COLOR_RED))

    tb_b, _, _ = textbox(midx + midx / 2, 335, "Неперервність струму I = J₁A₁ = J₂A₂ вимагає\nбільшого E₂ у тонкій частині. Градієнт поля\nзабезпечується зарядом на межі σ_s = ε₀(E₂ - E₁).", size=11, fill="#f8fafc", pad=6)
    f.append(tb_b)

    render(os.path.join(IMG, 'wire-bend-and-cross-section.svg'), W, H, "\n".join(f),
           title="Локальний поверхневий заряд на вигині провідника та стрибку перерізу")


# ── Фігура 3: Потік енергії Пойнтінга ───────────────────────────────────────
def fig_poynting_flux_circuit():
    W, H = 800, 440
    f = []

    x_left, x_right = 160, 640
    y_top, y_bot = 110, 330

    # Джерело батарея
    f.append(rect(x_left - 25, (y_top + y_bot) / 2 - 35, 50, 70, fill="#e2e8f0", stroke=COLOR_DARK, sw=2.0, rx=4))
    f.append(text(x_left, (y_top + y_bot) / 2, "Батарея", size=12, bold=True))

    # Резистор
    r_w, r_h = 36, 90
    f.append(rect(x_right - r_w / 2, (y_top + y_bot) / 2 - r_h / 2, r_w, r_h, fill="#fff4e6", stroke=COLOR_ORANGE, sw=2.0, rx=3))
    f.append(text(x_right, (y_top + y_bot) / 2, "Резистор", size=12, bold=True, color=COLOR_ORANGE))

    # Провідники
    f.append(line(x_left, y_top, x_right, y_top, color=COLOR_DARK, sw=3.5))
    f.append(line(x_left, y_bot, x_right, y_bot, color=COLOR_DARK, sw=3.5))
    f.append(line(x_left, y_top, x_left, (y_top + y_bot) / 2 - 35, color=COLOR_DARK, sw=3.5))
    f.append(line(x_left, y_bot, x_left, (y_top + y_bot) / 2 + 35, color=COLOR_DARK, sw=3.5))
    f.append(line(x_right, y_top, x_right, (y_top + y_bot) / 2 - r_h / 2, color=COLOR_DARK, sw=3.5))
    f.append(line(x_right, y_bot, x_right, (y_top + y_bot) / 2 + r_h / 2, color=COLOR_DARK, sw=3.5))

    # Вектори Пойнтінга S
    f.append(arrow(x_left + 35, y_top + 30, x_left + 80, y_top + 30, color=COLOR_GREEN, sw=2.5))
    f.append(arrow(x_left + 35, y_bot - 30, x_left + 80, y_bot - 30, color=COLOR_GREEN, sw=2.5))
    f.append(text(x_left + 65, (y_top + y_bot) / 2, "Випромінювання\nенергії джерелом", size=11, bold=True, color=COLOR_GREEN))

    for sx in [260, 360, 460]:
        f.append(arrow(sx, y_top + 35, sx + 50, y_top + 35, color=COLOR_GREEN, sw=2.5))
        f.append(arrow(sx, y_bot - 35, sx + 50, y_bot - 35, color=COLOR_GREEN, sw=2.5))
        f.append(arrow(sx, 220, sx + 50, 220, color=COLOR_GREEN, sw=2.5))

    f.append(text(385, 200, "Вектор Пойнтінга S вільним простором", size=13, bold=True, color=COLOR_GREEN))

    f.append(arrow(x_right - 60, y_top + 30, x_right - 22, y_top + 45, color=COLOR_GREEN, sw=2.5))
    f.append(arrow(x_right - 60, y_bot - 30, x_right - 22, y_bot - 45, color=COLOR_GREEN, sw=2.5))
    f.append(arrow(x_right - 70, 220, x_right - 22, 220, color=COLOR_GREEN, sw=2.5))

    f.append(text(x_right - 75, y_top + 15, "S входить у резистор", size=11, bold=True, color=COLOR_GREEN))
    f.append(text(x_right + 45, 220, "Джоулеве\nтепло I²R", size=12, bold=True, color=COLOR_RED))

    # E та B поля
    f.append(line(310, y_top + 10, 310, y_bot - 10, color=COLOR_PURPLE, sw=1.2, dash="3,3"))
    f.append(arrow(310, 200, 310, 215, color=COLOR_PURPLE, sw=1.5))
    f.append(text(318, 210, "E_ext", size=11, bold=True, color=COLOR_PURPLE))

    f.append(circle(310, y_top - 18, 6, fill="none", stroke=COLOR_BLUE, sw=1.5))
    f.append(text(310, y_top - 18, "•", size=10, bold=True, color=COLOR_BLUE))
    f.append(text(325, y_top - 18, "B (з екрана)", size=10, bold=True, color=COLOR_BLUE))

    tb_p, _, _ = textbox(W / 2, 395, "Електромагнітна енергія передається НЕ всередині мідних дротів, а крізь навколишній діелектрик.\nПоверхневі заряди напрямляють вектор Пойнтінга S прямо з простору всередину резистора.", size=11, fill="#f8fafc", pad=8)
    f.append(tb_p)

    render(os.path.join(IMG, 'poynting-flux-circuit.svg'), W, H, "\n".join(f),
           title="Потік енергії Пойнтінга у навколишньому просторі електричного кола")


if __name__ == '__main__':
    fig_circuit_surface_charge()
    fig_wire_bend_and_cross_section()
    fig_poynting_flux_circuit()
    print("Всі фігури успішно згенеровано у ./img/")
