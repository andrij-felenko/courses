# -*- coding: utf-8 -*-
"""Фігури до теми «Крива розряду батареї».
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
COLOR_DARK = "#2c3e50"
COLOR_GRAY = "#7f8c8d"

def path_svg(d, color=LINE, sw=1.5, fill="none", dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}"{d_attr}/>'

# ── Фігура 1: Три ділянки кривої розряду ──────────────────────────────────
def fig_discharge_curve_regions():
    W, H = 760, 450
    f = []

    ox, oy = 80, 370
    gw, gh = 620, 290

    # Осі
    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    f.append(arrow(ox + gw - 10, oy, ox + gw + 10, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy - gh + 10, ox, oy - gh - 10, color=LINE, sw=1.8))

    f.append(text(ox + gw + 15, oy + 4, "Віддана ємність Q (А·год) / Час t", size=12, bold=True, anchor="start"))
    f.append(text(ox - 10, oy - gh - 15, "Напруга на клемах V (В)", size=12, bold=True, anchor="end"))

    y_vocv = oy - 260
    f.append(line(ox, y_vocv, ox + gw, y_vocv, color="#bdc3c7", sw=1.2, dash="4,4"))
    f.append(text(ox - 10, y_vocv + 4, "Vocv (4.2 В)", size=11, color=COLOR_DARK, anchor="end"))

    y_vnom = oy - 190
    f.append(line(ox, y_vnom, ox + gw, y_vnom, color="#bdc3c7", sw=1.0, dash="2,4"))
    f.append(text(ox - 10, y_vnom + 4, "Vnom (3.7 В)", size=11, color=COLOR_BLUE, anchor="end"))

    y_vcut = oy - 80
    f.append(line(ox, y_vcut, ox + gw, y_vcut, color=COLOR_RED, sw=1.4, dash="5,5"))
    f.append(text(ox - 10, y_vcut + 4, "Vcut (3.0 В)", size=11, color=COLOR_RED, anchor="end"))

    # Вертикальні пунктирні межі між ділянками
    x_r1 = ox + 90
    x_r2 = ox + 490
    f.append(line(x_r1, oy - gh, x_r1, oy, color="#a0aec0", sw=1.5, dash="4,4"))
    f.append(line(x_r2, oy - gh, x_r2, oy, color="#a0aec0", sw=1.5, dash="4,4"))

    # Крива розряду V(t)
    pts = [
        (ox, y_vocv),
        (ox + 30, y_vocv + 35),
        (x_r1, oy - 200),
        (ox + 250, oy - 185),
        (ox + 380, oy - 172),
        (x_r2, oy - 160),
        (ox + 540, oy - 110),
        (ox + 580, y_vcut),
        (ox + 600, y_vcut + 35)
    ]

    path_str = f"M {pts[0][0]} {pts[0][1]} "
    for i in range(1, len(pts)):
        path_str += f"L {pts[i][0]} {pts[i][1]} "

    f.append(path_svg(path_str, color=COLOR_BLUE, sw=3))

    f.append(line(ox + 4, y_vocv, ox + 4, y_vocv + 35, color=COLOR_ORANGE, sw=2))
    f.append(arrow(ox + 4, y_vocv, ox + 4, y_vocv + 30, color=COLOR_ORANGE, sw=1.5))
    f.append(text(ox + 12, y_vocv + 20, "ΔV = I · Ri (Омічний спад)", size=10, bold=True, color=COLOR_ORANGE, anchor="start"))

    # Підписи ділянок у вигляді інформаційних блоків угорі
    b1, w1, h1 = textbox(ox + 45, oy - gh + 30, "І. Початковий спад\n(Омічний + активація)", size=11, pad=6, fill="#ffffff", stroke=COLOR_BLUE, sw=1.2)
    f.append(b1)

    b2, w2, h2 = textbox(ox + 290, oy - gh + 30, "ІІ. Робоче плато розряду\n(Хімічна рівновага фаз, V ≈ Vnom)", size=11, pad=6, fill="#ffffff", stroke=COLOR_GREEN, sw=1.2)
    f.append(b2)

    b3, w3, h3 = textbox(ox + 555, oy - gh + 30, "ІІІ. Завершальне коліно\n(Дифузійне виснаження)", size=11, pad=6, fill="#ffffff", stroke=COLOR_RED, sw=1.2)
    f.append(b3)

    f.append(circle(ox + 580, y_vcut, 6, fill=COLOR_RED, stroke="#ffffff", sw=1.5))
    f.append(text(ox + 580, y_vcut + 20, "Точка відсічки (Vcut)", size=11, bold=True, color=COLOR_RED, anchor="middle"))

    render(os.path.join(IMG, "discharge-curve-regions.svg"), W, H, *f, title="Типова крива розряду гальванічного елемента")


# ── Фігура 2: Вплив струму розряду (C-rate) ──────────────────────────────
def fig_c_rate_effect():
    W, H = 760, 420
    f = []

    ox, oy = 75, 350
    gw, gh = 630, 270

    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    f.append(arrow(ox + gw - 10, oy, ox + gw + 10, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy - gh + 10, ox, oy - gh - 10, color=LINE, sw=1.8))

    f.append(text(ox + gw + 15, oy + 4, "Віддана ємність (А·год)", size=12, bold=True, anchor="start"))
    f.append(text(ox - 10, oy - gh - 15, "Напруга V (В)", size=12, bold=True, anchor="end"))

    y_vcut = oy - 70
    f.append(line(ox, y_vcut, ox + gw, y_vcut, color=COLOR_RED, sw=1.2, dash="5,5"))
    f.append(text(ox - 10, y_vcut + 4, "Vcut", size=11, color=COLOR_RED, anchor="end"))

    p_02c = [(ox, oy - 240), (ox + 40, oy - 225), (ox + 300, oy - 200), (ox + 520, oy - 175), (ox + 580, y_vcut), (ox + 595, y_vcut + 30)]
    str_02c = "M " + " L ".join(f"{x} {y}" for x, y in p_02c)
    f.append(path_svg(str_02c, color=COLOR_GREEN, sw=2.5))
    f.append(text(ox + 530, oy - 185, "0.2 C (Низький струм)", size=11, bold=True, color=COLOR_GREEN, anchor="start"))

    p_1c = [(ox, oy - 240), (ox + 40, oy - 205), (ox + 300, oy - 180), (ox + 480, oy - 155), (ox + 540, y_vcut), (ox + 555, y_vcut + 30)]
    str_1c = "M " + " L ".join(f"{x} {y}" for x, y in p_1c)
    f.append(path_svg(str_1c, color=COLOR_BLUE, sw=2.5))
    f.append(text(ox + 470, oy - 165, "1 C (Номінальний)", size=11, bold=True, color=COLOR_BLUE, anchor="start"))

    p_3c = [(ox, oy - 240), (ox + 40, oy - 170), (ox + 250, oy - 145), (ox + 400, oy - 120), (ox + 460, y_vcut), (ox + 475, y_vcut + 30)]
    str_3c = "M " + " L ".join(f"{x} {y}" for x, y in p_3c)
    f.append(path_svg(str_3c, color=COLOR_ORANGE, sw=2.5))
    f.append(text(ox + 395, oy - 130, "3 C (Високий)", size=11, bold=True, color=COLOR_ORANGE, anchor="start"))

    p_5c = [(ox, oy - 240), (ox + 40, oy - 130), (ox + 200, oy - 110), (ox + 320, oy - 90), (ox + 370, y_vcut), (ox + 385, y_vcut + 30)]
    str_5c = "M " + " L ".join(f"{x} {y}" for x, y in p_5c)
    f.append(path_svg(str_5c, color=COLOR_RED, sw=2.5))
    f.append(text(ox + 310, oy - 98, "5 C (Екстремальний)", size=11, bold=True, color=COLOR_RED, anchor="start"))

    f.append(line(ox + 370, oy + 10, ox + 580, oy + 10, color=COLOR_DARK, sw=1.5))
    f.append(arrow(ox + 480, oy + 10, ox + 370, oy + 10, color=COLOR_DARK, sw=1.5))
    f.append(arrow(ox + 480, oy + 10, ox + 580, oy + 10, color=COLOR_DARK, sw=1.5))
    f.append(text(ox + 475, oy + 28, "Зменшення віддаваної ємності при зростанні струму", size=11, color=COLOR_DARK, anchor="middle"))

    b, w, h = textbox(190, 85, "При зростанні струму:\n1. Зростає омічне просідання I·Ri\n2. Прискорюється дифузійне виснаження\n3. Напруга досягає Vcut раніше", size=11, pad=6, fill="#ffffff", stroke=COLOR_BLUE, sw=1.2)
    f.append(b)

    render(os.path.join(IMG, "c-rate-effect.svg"), W, H, *f, title="Залежність кривої розряду від струму (C-rate)")


# ── Фігура 3: Вплив температури ──────────────────────────────────────────
def fig_temperature_effect():
    W, H = 760, 420
    f = []

    ox, oy = 75, 350
    gw, gh = 630, 270

    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    f.append(arrow(ox + gw - 10, oy, ox + gw + 10, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy - gh + 10, ox, oy - gh - 10, color=LINE, sw=1.8))

    f.append(text(ox + gw + 15, oy + 4, "Доступна ємність (А·год)", size=12, bold=True, anchor="start"))
    f.append(text(ox - 10, oy - gh - 15, "Напруга V (В)", size=12, bold=True, anchor="end"))

    y_vcut = oy - 70
    f.append(line(ox, y_vcut, ox + gw, y_vcut, color=COLOR_RED, sw=1.2, dash="5,5"))
    f.append(text(ox - 10, y_vcut + 4, "Vcut", size=11, color=COLOR_RED, anchor="end"))

    p_45 = [(ox, oy - 240), (ox + 40, oy - 220), (ox + 300, oy - 195), (ox + 530, oy - 175), (ox + 585, y_vcut), (ox + 600, y_vcut + 30)]
    str_45 = "M " + " L ".join(f"{x} {y}" for x, y in p_45)
    f.append(path_svg(str_45, color=COLOR_RED, sw=2.5))
    f.append(text(ox + 540, oy - 185, "+45 °C", size=11, bold=True, color=COLOR_RED, anchor="start"))

    p_25 = [(ox, oy - 240), (ox + 40, oy - 210), (ox + 300, oy - 185), (ox + 500, oy - 165), (ox + 560, y_vcut), (ox + 575, y_vcut + 30)]
    str_25 = "M " + " L ".join(f"{x} {y}" for x, y in p_25)
    f.append(path_svg(str_25, color=COLOR_GREEN, sw=2.5))
    f.append(text(ox + 510, oy - 165, "+25 °C (Норма)", size=11, bold=True, color=COLOR_GREEN, anchor="start"))

    p_0 = [(ox, oy - 240), (ox + 40, oy - 180), (ox + 260, oy - 155), (ox + 410, oy - 130), (ox + 470, y_vcut), (ox + 485, y_vcut + 30)]
    str_0 = "M " + " L ".join(f"{x} {y}" for x, y in p_0)
    f.append(path_svg(str_0, color=COLOR_ORANGE, sw=2.5))
    f.append(text(ox + 420, oy - 135, "0 °C", size=11, bold=True, color=COLOR_ORANGE, anchor="start"))

    p_m20 = [(ox, oy - 240), (ox + 40, oy - 135), (ox + 180, oy - 110), (ox + 280, oy - 90), (ox + 330, y_vcut), (ox + 345, y_vcut + 30)]
    str_m20 = "M " + " L ".join(f"{x} {y}" for x, y in p_m20)
    f.append(path_svg(str_m20, color=COLOR_BLUE, sw=2.5))
    f.append(text(ox + 270, oy - 95, "-20 °C (Мороз)", size=11, bold=True, color=COLOR_BLUE, anchor="start"))

    b, w, h = textbox(190, 85, "При охолодженні:\n• В'язкість електроліту зростає -> іони рухаються повільніше\n• Внутрішній опір Ri може зрости у 3-10 разів\n• Дифузія в електродах гальмується -> виснаження настає швидше", size=11, pad=6, fill="#ffffff", stroke=COLOR_BLUE, sw=1.2)
    f.append(b)

    render(os.path.join(IMG, "temperature-effect.svg"), W, H, *f, title="Вплив температури на розрядну характеристику")


# ── Фігура 4: Складові падіння напруги (Поляризація) ─────────────────────
def fig_polarization_contributions():
    W, H = 760, 440
    f = []

    ox, oy = 80, 370
    gw, gh = 620, 300

    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    f.append(arrow(ox + gw - 10, oy, ox + gw + 10, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy - gh + 10, ox, oy - gh - 10, color=LINE, sw=1.8))

    f.append(text(ox + gw + 15, oy + 4, "Ступінь розрядженості (100% -> 0% SoC)", size=12, bold=True, anchor="start"))
    f.append(text(ox - 10, oy - gh - 15, "Потенціал / Напруга (В)", size=12, bold=True, anchor="end"))

    p_vocv = [(ox, oy - 270), (ox + 200, oy - 255), (ox + 400, oy - 240), (ox + 580, oy - 210)]
    str_vocv = "M " + " L ".join(f"{x} {y}" for x, y in p_vocv)
    f.append(path_svg(str_vocv, color=COLOR_DARK, sw=2, dash="6,4"))
    f.append(text(ox + 400, oy - 280, "Vocv(Q) - Термодинамічна ЕРС", size=11, bold=True, color=COLOR_DARK, anchor="start"))

    p_ohm = [(ox, oy - 240), (ox + 200, oy - 225), (ox + 400, oy - 210), (ox + 580, oy - 175)]
    str_ohm = "M " + " L ".join(f"{x} {y}" for x, y in p_ohm)
    f.append(path_svg(str_ohm, color=COLOR_ORANGE, sw=1.8, dash="4,4"))

    p_act = [(ox, oy - 215), (ox + 200, oy - 200), (ox + 400, oy - 185), (ox + 580, oy - 140)]
    str_act = "M " + " L ".join(f"{x} {y}" for x, y in p_act)
    f.append(path_svg(str_act, color=COLOR_PURPLE, sw=1.8, dash="4,4"))

    p_term = [(ox, oy - 215), (ox + 50, oy - 200), (ox + 200, oy - 195), (ox + 400, oy - 180), (ox + 520, oy - 140), (ox + 560, oy - 80), (ox + 575, oy - 40)]
    str_term = "M " + " L ".join(f"{x} {y}" for x, y in p_term)
    f.append(path_svg(str_term, color=COLOR_BLUE, sw=3))
    f.append(text(ox + 430, oy - 50, "Реальна напруга V(t)", size=12, bold=True, color=COLOR_BLUE, anchor="start"))

    xr = ox + 240
    yr_vocv = oy - 252
    yr_ohm = oy - 222
    yr_act = oy - 197
    yr_term = oy - 192

    f.append(line(xr, yr_vocv, xr, yr_term, color="#bdc3c7", sw=1, dash="2,2"))

    f.append(text(xr + 10, (yr_vocv + yr_ohm) / 2 + 3, "ΔV_Ohm = I · Ri (Омічні втрати)", size=10, bold=True, color=COLOR_ORANGE, anchor="start"))
    f.append(text(xr + 10, (yr_ohm + yr_act) / 2 + 3, "η_act (Активаційна перенапруга)", size=10, bold=True, color=COLOR_PURPLE, anchor="start"))
    f.append(text(xr + 10, (yr_act + yr_term) / 2 + 15, "η_conc (Концентраційна перенапруга)", size=10, bold=True, color=COLOR_RED, anchor="start"))

    b, w, h = textbox(W / 2, oy - 30, "Рівняння балансу напруги:  V(t) = Vocv(Q) - I·Ri - η_act - η_conc", size=12, pad=8, fill="#ffffff", stroke=COLOR_BLUE, sw=1.4)
    f.append(b)

    render(os.path.join(IMG, "polarization-contributions.svg"), W, H, *f, title="Структура напруги елемента під навантаженням")


if __name__ == "__main__":
    fig_discharge_curve_regions()
    fig_c_rate_effect()
    fig_temperature_effect()
    fig_polarization_contributions()
    print("Figures created successfully!")
