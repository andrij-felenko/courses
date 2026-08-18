# -*- coding: utf-8 -*-
"""Фігури до теми «Рекомбінація Шокли — Рида — Холла (SRH)».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_EC = "#2457d6"      # Зона провідності (синій)
COLOR_EV = "#c0392b"      # Валентна зона (червоний)
COLOR_TRAP = "#d35400"    # Рівень пастки (помаранчевий)
COLOR_EI = "#7f8c8d"      # Середина забороненої зони (сірий)
COLOR_ELECTRON = "#2980b9"# Електрон (синій круг)
COLOR_HOLE = "#e74c3c"    # Дірка (червоний круг)
COLOR_GREEN = "#27ae60"   # Перехід / генерація / рекомбінація

# ── Фігура 1: Чотири елементарні процеси SRH ────────────────────────────────
def fig_srh_4steps():
    W, H = 820, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Чотири елементарні процеси рекомбінації та емісії через пастку SRH", size=16, bold=True))

    col_w = (W - 60) / 4
    titles = [
        "1. Захоплення електрона",
        "2. Емісія електрона",
        "3. Захоплення дірки",
        "4. Емісія дірки"
    ]
    subtitles = [
        "r_a = C_n · n · N_t · (1-f)",
        "r_b = e_n · N_t · f",
        "r_c = C_p · p · N_t · f",
        "r_d = e_p · N_t · (1-f)"
    ]

    for i in range(4):
        x0 = 30 + i * col_w
        xc = x0 + col_w / 2
        
        # Заголовок колонки
        f.append(text(xc, 58, titles[i], size=13, bold=True, color=INK))
        f.append(text(xc, 76, subtitles[i], size=11, bold=False, color=MUTED))

        # Енергетична діаграма колонки
        y_ec = 110
        y_et = 210
        y_ev = 310

        # Лінії зон
        f.append(line(x0 + 15, y_ec, x0 + col_w - 15, y_ec, color=COLOR_EC, sw=2.5))
        f.append(line(x0 + 15, y_et, x0 + col_w - 15, y_et, color=COLOR_TRAP, sw=2.0, dash="4,4"))
        f.append(line(x0 + 15, y_ev, x0 + col_w - 15, y_ev, color=COLOR_EV, sw=2.5))

        # Позначки зон (тільки в першій колонці)
        if i == 0:
            f.append(text(x0 + 20, y_ec - 8, "E_c (зона провідності)", size=10, bold=True, color=COLOR_EC, anchor="start"))
            f.append(text(x0 + 20, y_et - 8, "E_t (рівень пастки)", size=10, bold=True, color=COLOR_TRAP, anchor="start"))
            f.append(text(x0 + 20, y_ev + 16, "E_v (валентна зона)", size=10, bold=True, color=COLOR_EV, anchor="start"))

        # Центр пастки
        f.append(circle(xc, y_et, 10, fill='#fff3e0', stroke=COLOR_TRAP, sw=2))

        if i == 0:
            # 1. Захоплення електрона: електрон іде з E_c на E_t
            f.append(circle(xc, y_ec - 15, 6, fill=COLOR_ELECTRON, stroke=COLOR_EC, sw=1.5))
            f.append(arrow(xc, y_ec - 5, xc, y_et - 14, color=COLOR_GREEN, sw=2))
            f.append(text(xc + 18, (y_ec + y_et) / 2, "падає", size=10, color=COLOR_GREEN, anchor="start"))
        elif i == 1:
            # 2. Емісія електрона: електрон вилітає з E_t до E_c
            f.append(circle(xc, y_et, 6, fill=COLOR_ELECTRON, stroke=COLOR_EC, sw=1.5))
            f.append(arrow(xc, y_et - 14, xc, y_ec - 5, color=COLOR_GREEN, sw=2))
            f.append(text(xc + 18, (y_ec + y_et) / 2, "вилітає", size=10, color=COLOR_GREEN, anchor="start"))
        elif i == 2:
            # 3. Захоплення дірки: дірка з E_v іде на E_t (або електрон падає з E_t у валентну зону)
            f.append(circle(xc, y_et, 6, fill=COLOR_ELECTRON, stroke=COLOR_EC, sw=1.5))
            f.append(circle(xc, y_ev + 15, 6, fill='#ffffff', stroke=COLOR_HOLE, sw=2))
            f.append(arrow(xc, y_et + 14, xc, y_ev + 5, color=COLOR_GREEN, sw=2))
            f.append(text(xc + 18, (y_ev + y_et) / 2, "знищує", size=10, color=COLOR_GREEN, anchor="start"))
        elif i == 3:
            # 4. Емісія дірки: електрон із E_v сідає на E_t, залишаючи дірку в E_v
            f.append(arrow(xc, y_ev + 5, xc, y_et + 14, color=COLOR_GREEN, sw=2))
            f.append(circle(xc, y_ev + 25, 6, fill='#ffffff', stroke=COLOR_HOLE, sw=2))
            f.append(text(xc + 18, (y_ev + y_et) / 2, "породжує", size=10, color=COLOR_GREEN, anchor="start"))

    # Підписи під діаграмами
    f.append(rect(30, 350, W - 60, 45, fill='#f8f9fa', stroke='#dcdfe6', sw=1, rx=4))
    f.append(text(W / 2, 377, "Повна рекомбінація пар = (Захоплення електрона) + (Захоплення дірки) через один центр", size=12, bold=True, color=INK))

    render(os.path.join(IMG, "srh-4steps.svg"), W, H, *f)


# ── Фігура 2: Ефективність рекомбінації від рівня пастки ───────────────────
def fig_srh_energy_dependence():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Швидкість рекомбінації SRH від енергетичного рівня пастки (E_t)", size=16, bold=True))

    # Осі координат
    ox, oy = 80, 300
    w_axis = 560
    h_axis = 220

    # Вісь X (Енергія E_t)
    f.append(arrow(ox, oy, ox + w_axis + 20, oy, color=LINE, sw=1.8))
    f.append(text(ox + w_axis + 10, oy + 25, "Енергія пастки E_t", size=12, bold=True, color=INK, anchor="end"))

    # Вісь Y (Швидкість R_SRH)
    f.append(arrow(ox, oy, ox, oy - h_axis - 20, color=LINE, sw=1.8))
    f.append(text(ox - 10, oy - h_axis - 10, "Швидкість R_SRH", size=12, bold=True, color=INK, anchor="start"))

    # Вертикальні лінії меж зон
    x_ev = ox + 40
    x_ei = ox + w_axis / 2
    x_ec = ox + w_axis - 40

    f.append(line(x_ev, oy, x_ev, oy - h_axis, color=COLOR_EV, sw=1.5, dash="4,4"))
    f.append(line(x_ei, oy, x_ei, oy - h_axis, color=COLOR_EI, sw=1.5, dash="4,4"))
    f.append(line(x_ec, oy, x_ec, oy - h_axis, color=COLOR_EC, sw=1.5, dash="4,4"))

    f.append(text(x_ev, oy + 20, "E_v", size=12, bold=True, color=COLOR_EV))
    f.append(text(x_ei, oy + 20, "E_i (середина)", size=12, bold=True, color=COLOR_EI))
    f.append(text(x_ec, oy + 20, "E_c", size=12, bold=True, color=COLOR_EC))

    # Крива колоколу R_SRH (гаусоподібна / лоренцева)
    points = []
    import math
    for px in range(int(x_ev), int(x_ec) + 1):
        # Відстань від середини
        norm_x = (px - x_ei) / (x_ec - x_ei)
        # R падає експоненційно з віддаленням від E_i
        val = math.exp(-6.0 * norm_x * norm_x)
        py = oy - val * (h_axis - 20)
        points.append((px, py))

    path_d = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in points)
    f.append(f'<path d="{path_d}" fill="none" stroke="{COLOR_TRAP}" stroke-width="3"/>')

    # Заповнення під кривою
    area_d = path_d + f" L {x_ec:.1f},{oy:.1f} L {x_ev:.1f},{oy:.1f} Z"
    f.append(f'<path d="{area_d}" fill="{COLOR_TRAP}" fill-opacity="0.12" stroke="none"/>')

    # Позначка максимуму
    f.append(circle(x_ei, oy - (h_axis - 20), 5, fill=COLOR_TRAP, stroke=LINE, sw=1.5))
    f.append(textbox(x_ei + 110, oy - h_axis + 30, "Максимум рекомбінації:\nE_t ≈ E_i (глибокий центр)", size=11, fill='#fff3e0', stroke=COLOR_TRAP, pad=6)[0])

    # Зони прилипання (критичні неактивні рекомбінатори)
    f.append(textbox(x_ev + 70, oy - 40, "Діркові пастки\n(активна емісія)", size=10, fill='#fef2f2', stroke=COLOR_EV, pad=4)[0])
    f.append(textbox(x_ec - 70, oy - 40, "Електронні пастки\n(активна емісія)", size=10, fill='#eff6ff', stroke=COLOR_EC, pad=4)[0])

    render(os.path.join(IMG, "srh-energy-dependence.svg"), W, H, *f)


# ── Фігура 3: Залежність часу життя від рівня інжекції ─────────────────────
def fig_srh_injection_level():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Залежність часу життя SRH від рівня інжекції носіїв (Δn)", size=16, bold=True))

    ox, oy = 90, 300
    w_axis = 560
    h_axis = 220

    # Осі
    f.append(arrow(ox, oy, ox + w_axis + 20, oy, color=LINE, sw=1.8))
    f.append(text(ox + w_axis + 10, oy + 25, "Концентрація інжектованих носіїв Δn", size=12, bold=True, color=INK, anchor="end"))

    f.append(arrow(ox, oy, ox, oy - h_axis - 20, color=LINE, sw=1.8))
    f.append(text(ox - 10, oy - h_axis - 10, "Час життя τ_SRH", size=12, bold=True, color=INK, anchor="start"))

    # Пунктир межі рівнів інжекції
    x_trans = ox + 260
    f.append(line(x_trans, oy, x_trans, oy - h_axis, color=MUTED, sw=1.5, dash="4,4"))
    f.append(text(x_trans, oy + 20, "Δn = p_0 (межа)", size=11, bold=True, color=MUTED))

    # Ліва область: Low Injection
    f.append(rect(ox + 5, oy - h_axis, x_trans - ox - 10, h_axis - 5, fill='#f0fdf4', stroke='none', sw=0, rx=4))
    f.append(text((ox + x_trans) / 2, oy - h_axis + 25, "Низький рівень інжекції (LIL)\nΔn << p_0", size=11, bold=True, color=COLOR_GREEN))

    # Права область: High Injection
    f.append(rect(x_trans + 5, oy - h_axis, ox + w_axis - x_trans - 10, h_axis - 5, fill='#fff7ed', stroke='none', sw=0, rx=4))
    f.append(text((x_trans + ox + w_axis) / 2, oy - h_axis + 25, "Високий рівень інжекції (HIL)\nΔn >> p_0", size=11, bold=True, color=COLOR_TRAP))

    # Рівні плато: τ_n0 та τ_n0 + τ_p0
    y_lil = oy - 60
    y_hil = oy - 180

    f.append(line(ox, y_lil, ox + w_axis, y_lil, color='#d1d5db', sw=1, dash="2,2"))
    f.append(text(ox - 10, y_lil + 4, "τ_n0", size=12, bold=True, color=COLOR_EC, anchor="end"))

    f.append(line(ox, y_hil, ox + w_axis, y_hil, color='#d1d5db', sw=1, dash="2,2"))
    f.append(text(ox - 10, y_hil + 4, "τ_n0 + τ_p0", size=12, bold=True, color=COLOR_TRAP, anchor="end"))

    # S-подібна крива переході від τ_n0 до τ_n0 + τ_p0
    import math
    pts = []
    for px in range(int(ox), int(ox + w_axis) + 1):
        # Перехідна функція sigmoid
        x_norm = (px - x_trans) / 45.0
        sig = 1.0 / (1.0 + math.exp(-x_norm))
        py = y_lil - sig * (y_lil - y_hil)
        pts.append((px, py))

    path_d = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    f.append(f'<path d="{path_d}" fill="none" stroke="{COLOR_EC}" stroke-width="3.2"/>')

    # Текстові підписи на плато
    f.append(text(ox + 100, y_lil - 12, "τ ≈ τ_n0 (обмежено неосновними)", size=11, bold=True, color=COLOR_EC, anchor="start"))
    f.append(text(ox + w_axis - 40, y_hil - 12, "τ ≈ τ_n0 + τ_p0 (насичення пасток)", size=11, bold=True, color=COLOR_TRAP, anchor="end"))

    render(os.path.join(IMG, "srh-injection-level.svg"), W, H, *f)


# ── Фігура 4: Дрібні домішки проти глибоких пасток ─────────────────────────
def fig_srh_shallow_vs_deep():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Порівняння дрібних домішок (легування) та глибоких пасток (SRH)", size=16, bold=True))

    w_card = 330
    h_card = 280

    # Ліва картка: Дрібні домішки
    x1 = 30
    y1 = 50
    f.append(rect(x1, y1, w_card, h_card, fill='#f8fafc', stroke='#cbd5e1', sw=1.5, rx=6))
    f.append(text(x1 + w_card / 2, y1 + 25, "Дрібні домішки (B, P, As)", size=14, bold=True, color=COLOR_EC))
    f.append(text(x1 + w_card / 2, y1 + 43, "Завдання: дати вільні носії (n або p)", size=11, color=MUTED))

    # Зони ліворуч
    f.append(line(x1 + 30, y1 + 80, x1 + w_card - 30, y1 + 80, color=COLOR_EC, sw=2))
    f.append(text(x1 + 35, y1 + 72, "E_c", size=11, bold=True, color=COLOR_EC, anchor="start"))

    f.append(line(x1 + 30, y1 + 100, x1 + w_card - 30, y1 + 100, color=COLOR_EC, sw=1.5, dash="3,3"))
    f.append(text(x1 + w_card - 35, y1 + 96, "E_d (донор: ΔE ≈ 0.04 еВ)", size=10, color=COLOR_EC, anchor="end"))

    f.append(line(x1 + 30, y1 + 220, x1 + w_card - 30, y1 + 220, color=COLOR_EV, sw=1.5, dash="3,3"))
    f.append(text(x1 + w_card - 35, y1 + 232, "E_a (акцептор: ΔE ≈ 0.04 еВ)", size=10, color=COLOR_EV, anchor="end"))

    f.append(line(x1 + 30, y1 + 240, x1 + w_card - 30, y1 + 240, color=COLOR_EV, sw=2))
    f.append(text(x1 + 35, y1 + 252, "E_v", size=11, bold=True, color=COLOR_EV, anchor="start"))

    # Пояснення
    f.append(arrow(x1 + 80, y1 + 98, x1 + 80, y1 + 82, color=COLOR_GREEN, sw=1.8))
    f.append(text(x1 + 90, y1 + 120, "Повна іонізація при 300 K\n(легкий перехід)", size=10, color=INK, anchor="start"))


    # Права картка: Глибокі пастки
    x2 = 380
    y2 = 50
    f.append(rect(x2, y2, w_card, h_card, fill='#fffbf5', stroke='#fed7aa', sw=1.5, rx=6))
    f.append(text(x2 + w_card / 2, y2 + 25, "Глибокі пастки (Au, Pt, Fe, дефекти)", size=14, bold=True, color=COLOR_TRAP))
    f.append(text(x2 + w_card / 2, y2 + 43, "Завдання: знищувати носії (рекомбінація)", size=11, color=MUTED))

    # Зони праворуч
    f.append(line(x2 + 30, y2 + 80, x2 + w_card - 30, y2 + 80, color=COLOR_EC, sw=2))
    f.append(text(x2 + 35, y2 + 72, "E_c", size=11, bold=True, color=COLOR_EC, anchor="start"))

    f.append(line(x2 + 30, y2 + 160, x2 + w_card - 30, y2 + 160, color=COLOR_TRAP, sw=2, dash="4,4"))
    f.append(text(x2 + w_card - 35, y2 + 152, "E_t ≈ E_i (глибокий рівень)", size=10, bold=True, color=COLOR_TRAP, anchor="end"))

    f.append(line(x2 + 30, y2 + 240, x2 + w_card - 30, y2 + 240, color=COLOR_EV, sw=2))
    f.append(text(x2 + 35, y2 + 252, "E_v", size=11, bold=True, color=COLOR_EV, anchor="start"))

    # Стрілки рекомбінації
    f.append(arrow(x2 + 80, y2 + 83, x2 + 80, y2 + 155, color=COLOR_GREEN, sw=1.8))
    f.append(arrow(x2 + 80, y2 + 165, x2 + 80, y2 + 237, color=COLOR_GREEN, sw=1.8))
    f.append(text(x2 + 95, y2 + 120, "1. Електрон падає", size=10, color=INK, anchor="start"))
    f.append(text(x2 + 95, y2 + 200, "2. Дірка рекомбінує", size=10, color=INK, anchor="start"))

    render(os.path.join(IMG, "srh-shallow-vs-deep.svg"), W, H, *f)


if __name__ == "__main__":
    fig_srh_4steps()
    fig_srh_energy_dependence()
    fig_srh_injection_level()
    fig_srh_shallow_vs_deep()
    print("Фігури SRH успішно згенеровано у ./img/")
