# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def path_el(d, fill="none", stroke=LINE, sw=1.5, stroke_dasharray=None):
    sd = f' stroke-dasharray="{stroke_dasharray}"' if stroke_dasharray else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{sd}/>'


# ── Фігура 1: Спектр газового згасання H2O та O2 ──────────────────────────────────

def fig_gas_spectrum():
    W, H = 800, 380
    p = []

    # Фон та заголовок
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    
    # Вікна прозорості (прямокутники з пустим fill="none" і пунктирною рамкою)
    # 1-10 ГГц (Радіовікно)
    p.append(rect(60, 45, 65, 275, fill="none", stroke="#cbd5e1", sw=1))
    p.append(text(92, 335, "1-10 ГГц", size=10, color=MUTED))
    p.append(text(92, 348, "Супутники / 4G / 5G", size=9, color=MUTED))

    # 30-45 ГГц (Ka-діапазон)
    p.append(rect(190, 45, 75, 275, fill="none", stroke="#cbd5e1", sw=1))
    p.append(text(227, 335, "30-45 ГГц", size=10, color=MUTED))
    p.append(text(227, 348, "Ka-band / SAT", size=9, color=MUTED))

    # 70-110 ГГц (E-band / W-band)
    p.append(rect(390, 45, 120, 275, fill="none", stroke="#cbd5e1", sw=1))
    p.append(text(450, 335, "70-110 ГГц", size=10, color=MUTED))
    p.append(text(450, 348, "E-band / W-band", size=9, color=MUTED))

    # 130-170 ГГц (D-band)
    p.append(rect(580, 45, 110, 275, fill="none", stroke="#cbd5e1", sw=1))
    p.append(text(635, 335, "130-170 ГГц", size=10, color=MUTED))
    p.append(text(635, 348, "D-band / 6G", size=9, color=MUTED))

    # Осі координат
    p.append(line(60, 45, 60, 320, color=INK, sw=1.5))
    p.append(arrow(60, 55, 60, 45, color=INK, sw=1.5))
    p.append(text(50, 40, "γ (дБ/км)", size=11, color=INK, bold=True))

    # Помітки Y
    y_ticks = [
        (310, "0.01"),
        (245, "0.1"),
        (180, "1.0"),
        (115, "10"),
        (55, "100")
    ]
    for y_val, lbl in y_ticks:
        p.append(line(55, y_val, 60, y_val, color=INK, sw=1))
        p.append(line(60, y_val, 750, y_val, color="#e5e7eb", sw=1, dash="2 2"))
        p.append(text(45, y_val + 4, lbl, size=10, color=MUTED, anchor="end"))

    # Вісь X: 60 до 750 (частота 0 до 200 ГГц)
    p.append(line(60, 320, 750, 320, color=INK, sw=1.5))
    p.append(arrow(740, 320, 750, 320, color=INK, sw=1.5))
    p.append(text(750, 340, "Частота (ГГц)", size=11, color=INK, bold=True))

    # Помітки X
    x_ticks = [
        (60, "0"),
        (145, "22.2 (H₂O)"),
        (280, "60 (O₂)"),
        (435, "118.7 (O₂)"),
        (625, "183.3 (H₂O)")
    ]
    for x_val, lbl in x_ticks:
        p.append(line(x_val, 320, x_val, 325, color=INK, sw=1))

    # Крива згасання H2O + O2 (комбінований спектр)
    curve_d = (
        "M 60,310 "
        "Q 100,305 130,265 "
        "Q 145,235 160,265 "
        "Q 210,285 240,190 "
        "Q 280,75 310,190 "
        "Q 340,240 370,230 "
        "Q 435,115 470,225 "
        "Q 530,250 580,180 "
        "Q 625,55 670,185 "
        "Q 710,210 740,200"
    )
    p.append(path_el(curve_d, fill="none", stroke="#0052cc", sw=2.5))

    # Маркери резонансних піків із рамками
    # Пік 22.235 ГГц H2O
    p.append(circle(145, 235, 4, fill="#0052cc", stroke="#ffffff", sw=1.5))
    b1 = fitbox(100, 185, 90, 36, "H₂O пік\n22.235 ГГц", size=10, color="#0052cc", fill="#e6f2ff", stroke="#b3cde0", rx=4)
    p.append(b1)
    p.append(line(145, 221, 145, 235, color="#0052cc", sw=1, dash="2 2"))

    # Пік 60 ГГц O2
    p.append(circle(280, 75, 4, fill="#cc0000", stroke="#ffffff", sw=1.5))
    b2 = fitbox(235, 25, 90, 36, "O₂ смуга\n57-64 ГГц", size=10, color="#cc0000", fill="#ffe6e6", stroke="#ffb3b3", rx=4)
    p.append(b2)
    p.append(line(280, 61, 280, 75, color="#cc0000", sw=1, dash="2 2"))

    # Пік 118.75 ГГц O2
    p.append(circle(435, 115, 4, fill="#cc0000", stroke="#ffffff", sw=1.5))
    b3 = fitbox(390, 65, 90, 36, "O₂ лінія\n118.75 ГГц", size=10, color="#cc0000", fill="#ffe6e6", stroke="#ffb3b3", rx=4)
    p.append(b3)
    p.append(line(435, 101, 435, 115, color="#cc0000", sw=1, dash="2 2"))

    # Пік 183.31 ГГц H2O
    p.append(circle(625, 55, 4, fill="#0052cc", stroke="#ffffff", sw=1.5))
    b4 = fitbox(580, 10, 90, 36, "H₂O пік\n183.31 ГГц", size=10, color="#0052cc", fill="#e6f2ff", stroke="#b3cde0", rx=4)
    p.append(b4)
    p.append(line(625, 46, 625, 55, color="#0052cc", sw=1, dash="2 2"))

    # Легенда
    p.append(rect(520, 260, 210, 50, fill="#ffffff", stroke="#d1d5db", rx=4, sw=1))
    p.append(line(535, 275, 560, 275, color="#0052cc", sw=2.5))
    p.append(text(570, 279, "Сумарне газове згасання", size=10, color=INK))
    p.append(rect(535, 290, 15, 12, fill="none", stroke="#cbd5e1", sw=1))
    p.append(text(555, 300, "Вікна прозорості", size=10, color=MUTED))

    render(os.path.join(OUT, "atmospheric-gas-attenuation-spectrum.svg"), W, H, *p,
           title="Спектр газового згасання в атмосфері")
    print("Generated atmospheric-gas-attenuation-spectrum.svg")


# ── Фігура 2: Дощове згасання залежно від інтенсивності дощу R та поляризації ───────

def fig_rain_attenuation():
    W, H = 800, 360
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))

    # Сітка та осі
    p.append(line(65, 40, 65, 300, color=INK, sw=1.5))
    p.append(arrow(65, 50, 65, 40, color=INK, sw=1.5))
    p.append(text(55, 30, "γᵣ (дБ/км)", size=11, color=INK, bold=True))

    # Y ticks (0 to 30 dB/km)
    y_ticks = [
        (300, "0"),
        (240, "5"),
        (180, "10"),
        (120, "20"),
        (60, "30")
    ]
    for y_val, lbl in y_ticks:
        p.append(line(60, y_val, 65, y_val, color=INK, sw=1))
        if y_val < 300:
            p.append(line(65, y_val, 740, y_val, color="#e5e7eb", sw=1, dash="2 2"))
        p.append(text(50, y_val + 4, lbl, size=10, color=MUTED, anchor="end"))

    # X axis (Rainfall rate R mm/h from 0 to 100)
    p.append(line(65, 300, 740, 300, color=INK, sw=1.5))
    p.append(arrow(730, 300, 740, 300, color=INK, sw=1.5))
    p.append(text(740, 320, "Інтенсивність дощу R (мм/год)", size=11, color=INK, bold=True))

    # X ticks
    x_ticks = [
        (65, "0"),
        (200, "25 (слабкий)"),
        (370, "50 (сильний)"),
        (540, "75 (злива)"),
        (710, "100 (гроза)")
    ]
    for x_val, lbl in x_ticks:
        p.append(line(x_val, 300, x_val, 305, color=INK, sw=1))
        p.append(text(x_val, 320, lbl, size=9, color=MUTED))

    # Криві для різних частот
    # 10 ГГц (зелена, слабке згасання)
    p.append(path_el("M 65,300 Q 370,290 710,265", fill="none", stroke="#009933", sw=2))
    p.append(text(715, 265, "10 ГГц", size=10, color="#009933", bold=True))

    # 28 ГГц Ka-band Горизонтальна поляризація H (синя суцільна)
    p.append(path_el("M 65,300 Q 370,230 710,130", fill="none", stroke="#0052cc", sw=2.5))
    p.append(text(715, 130, "28 ГГц (H)", size=10, color="#0052cc", bold=True))

    # 28 ГГц Ka-band Вертикальна поляризація V (синя штрихова, нижче на 20%)
    p.append(path_el("M 65,300 Q 370,245 710,165", fill="none", stroke="#0052cc", sw=2, stroke_dasharray="5 3"))
    p.append(text(715, 165, "28 ГГц (V)", size=10, color="#0052cc"))

    # 60 ГГц (червона, високе згасання)
    p.append(path_el("M 65,300 Q 370,160 710,55", fill="none", stroke="#cc0000", sw=2.5))
    p.append(text(715, 55, "60 ГГц", size=10, color="#cc0000", bold=True))

    # Пояснювальний бокс про поляризацію та сплюснуті краплі
    b_pol = fitbox(160, 50, 310, 80,
                   "Ефект сплюснутості крапель (Oblate Spheroids):\n"
                   "Краплі дощу сплющуються під час падіння.\n"
                   "Горизонтальна поляризація (H) зазнає на 15-25%\n"
                   "більшого згасання, ніж вертикальна (V).",
                   size=10, color=INK, fill="#fcf8e3", stroke="#faebcc", rx=5)
    p.append(b_pol)

    # Стрілка-вказівка на різницю між H та V
    p.append(line(580, 160, 580, 185, color=INK, sw=1.2))
    p.append(arrow(580, 172, 580, 160, color=INK, sw=1.2))
    p.append(arrow(580, 173, 580, 185, color=INK, sw=1.2))
    p.append(text(590, 177, "Δγ (H vs V)", size=9, color=INK, bold=True))

    render(os.path.join(OUT, "rain-attenuation-vs-rate.svg"), W, H, *p,
           title="Дощове згасання залежно від інтенсивності дощу")
    print("Generated rain-attenuation-vs-rate.svg")


# ── Фігура 3: Геометрія похилого шляху через атмосферу та дощ ───────────────────────

def fig_slant_path():
    W, H = 800, 320
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))

    # Земна поверхня (дуга або похила лінія)
    p.append(path_el("M 30,270 L 770,270", fill="none", stroke="#2d3748", sw=2))
    p.append(rect(30, 270, 740, 35, fill="#f7fafc", stroke="none"))
    p.append(text(400, 290, "Поверхня Землі", size=10, color=MUTED))

    # Земна станція (ЗС)
    p.append(rect(100, 230, 50, 40, fill="#e2e8f0", stroke="#4a5568", rx=3, sw=1.5))
    p.append(path_el("M 115,220 A 25,25 0 0 1 145,200", fill="none", stroke="#2b6cb0", sw=3))
    p.append(line(130, 210, 140, 195, color="#2b6cb0", sw=1.5))
    p.append(text(125, 260, "hₛ", size=10, color=INK, bold=True))
    p.append(text(70, 215, "Земна станція", size=10, color=INK, bold=True))

    # Висота дощового шару (h_R / ізотерма 0°C)
    p.append(line(30, 100, 770, 100, color="#3182ce", sw=1.5, dash="6 4"))
    p.append(text(70, 90, "Висота дощу hᵣ (ізотерма 0°C)", size=10, color="#3182ce", bold=True))

    # Затінена зона дощового осередку (Rain Cell)
    p.append(rect(220, 100, 380, 170, fill="#ebf8ff", stroke="#90cdf4", sw=1))
    p.append(text(410, 120, "Осередок дощу (Rain Cell)", size=11, color="#2b6cb0", bold=True))

    # Похила траса супутникового променя
    p.append(line(135, 205, 700, 45, color="#e53e3e", sw=2.5))
    p.append(arrow(680, 50, 700, 45, color="#e53e3e", sw=2.5))
    p.append(text(710, 40, "До супутника (GEO/LEO)", size=11, color="#e53e3e", bold=True))

    # Перетин з межею дощу
    p.append(circle(506, 100, 4, fill="#e53e3e", stroke="#ffffff", sw=1.5))

    # Кут підвищення θ (elevation angle)
    p.append(line(135, 205, 300, 205, color=MUTED, sw=1, dash="3 3"))
    p.append(path_el("M 185,205 A 50,50 0 0 0 178,193", fill="none", stroke=INK, sw=1.5))
    p.append(text(200, 198, "θ (кут місця)", size=10, color=INK, bold=True))

    # Довжина шляху у дощі L_S
    p.append(line(135, 190, 506, 85, color="#2b6cb0", sw=1.2, dash="2 2"))
    p.append(text(300, 130, "Похилий шлях у дощі Lₛ = (hᵣ - hₛ) / sin(θ)", size=10, color="#2b6cb0", bold=True))

    # Покутна висота дощового стовпа (h_R - h_s)
    p.append(line(530, 100, 530, 270, color=INK, sw=1.2))
    p.append(arrow(530, 120, 530, 100, color=INK, sw=1.2))
    p.append(arrow(530, 250, 530, 270, color=INK, sw=1.2))
    p.append(text(540, 185, "Висота стовпа (hᵣ - hₛ)", size=10, color=INK))

    # Ефективна довжина шляху L_E
    b_eff = fitbox(250, 220, 250, 40,
                   "Ефективна довжина: Lₑ = Lₛ · r₀.₀₁\n"
                   "r₀.₀₁ — коефіцієнт зменшення довжини",
                   size=9, color=INK, fill="#ffffff", stroke="#cbd5e0", rx=4)
    p.append(b_eff)

    render(os.path.join(OUT, "slant-path-propagation-geometry.svg"), W, H, *p,
           title="Геометрія похилого шляху через дощ")
    print("Generated slant-path-propagation-geometry.svg")


if __name__ == "__main__":
    fig_gas_spectrum()
    fig_rain_attenuation()
    fig_slant_path()
