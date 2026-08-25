# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Теорема флуктуацій і дисипації» (fluctuation-dissipation)."""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)

def make_fdt_bridge():
    """Фігура 1: Концептуальний місток між флуктуаціями та дисипацією через температуру T."""
    w, h = 840, 320
    frags = []

    # Заголовок панелі
    frags.append(textbox(420, 25, "Фундаментальний зв'язок термодинамічної рівноваги", size=16, bold=True, fill="#eef2f7", stroke="#2c3e50")[0])

    # Лівий блок: Флуктуації
    box_l, wl, hl = textbox(150, 145, "Спонтанні флуктуації\n\n• Випадковий тепловий рух\n• Спектральна густина S_A(ω)\n• Шуми: Джонсона, Броунівський", size=13, pad=10, fill="#eaf0fd", stroke=NEG, sw=2, min_w=240)
    frags.append(box_l)

    # Правий блок: Дисипація
    box_r, wr, hr = textbox(690, 145, "Лінійна дисипація\n\n• Поглинання зовн. енергії\n• Уявна сприйнятливість Im[χ(ω)]\n• Тертя γ, опір R, в'язкість η", size=13, pad=10, fill="#fdecea", stroke=POS, sw=2, min_w=240)
    frags.append(box_r)

    # Центральний місток (Теорема)
    frags.append(arrow(275, 145, 305, 145, color=FIELD, sw=2))
    frags.append(arrow(565, 145, 535, 145, color=FIELD, sw=2))
    
    box_c, wc, hc = textbox(420, 145, "Тепловий резервуар\nТемпература T\n\nS_A(ω) = (2 k_B T / ω) · Im[χ(ω)]", size=12, pad=8, fill="#e8f8f5", stroke=FIELD, sw=2, bold=True)
    frags.append(box_c)

    # Нижня примітка-пояснення
    box_b, wb, hb = textbox(420, 275, "Той самий тепловий хаос мікроатомів породжує і гальмування зовн. сили (дисипацію),\nі хаотичні удари по макросистемі (флуктуації). Механізм взаємодії один і той самий.", size=12, pad=10, fill="#f4f6f8", stroke=MUTED, sw=1)
    frags.append(box_b)

    render(os.path.join(OUT_DIR, 'fdt-bridge.svg'), w, h, *frags)

def make_susceptibility_spectrum():
    """Фігура 2: Залежність уявної частини сприйнятливості Im[χ(ω)] та спектра флуктуацій S_x(ω)."""
    w, h = 760, 340
    frags = []

    # Заголовок
    frags.append(textbox(380, 25, "Сприйнятливість осцилятора χ(ω) та спектр шуму S_x(ω)", size=16, bold=True, fill="#eef2f7", stroke="#2c3e50")[0])

    # Лівий графік: Im[χ(ω)]
    # Осі
    frags.append(arrow(60, 260, 340, 260, color=LINE, sw=1.5)) # x-axis (w)
    frags.append(arrow(60, 260, 60, 60, color=LINE, sw=1.5))   # y-axis Im[chi]
    frags.append(text(345, 265, "ω", size=13, bold=True, anchor="start"))
    frags.append(text(55, 52, "Im[χ(ω)]", size=13, bold=True, anchor="end", color=POS))
    frags.append(text(200, 280, "Частота збудження", size=12, color=MUTED))
    frags.append(text(200, 80, "Резонансний пік поглинання", size=12, color=POS, bold=True))

    # Схематичний пік Im[χ(ω)]
    curve_points = [(60, 258), (100, 255), (140, 245), (170, 210), (190, 140), (200, 90), (210, 140), (230, 210), (260, 245), (300, 255), (330, 258)]
    pts_str = " ".join("%.1f,%.1f" % p for p in curve_points)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pts_str, POS))
    frags.append(line(200, 90, 200, 260, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(200, 273, "ω₀", size=12, bold=True))

    # Правий графік: S_x(ω)
    frags.append(arrow(420, 260, 700, 260, color=LINE, sw=1.5)) # x-axis (w)
    frags.append(arrow(420, 260, 420, 60, color=LINE, sw=1.5))   # y-axis S_x
    frags.append(text(705, 265, "ω", size=13, bold=True, anchor="start"))
    frags.append(text(415, 52, "S_x(ω)", size=13, bold=True, anchor="end", color=NEG))
    frags.append(text(560, 280, "Частота флуктуацій", size=12, color=MUTED))
    frags.append(text(560, 80, "Спектр теплового шуму", size=12, color=NEG, bold=True))

    # Схематичний пік S_x(ω)
    curve_points_s = [(420, 220), (450, 230), (500, 240), (530, 210), (550, 140), (560, 95), (570, 140), (590, 210), (620, 245), (660, 255), (690, 258)]
    pts_str_s = " ".join("%.1f,%.1f" % p for p in curve_points_s)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pts_str_s, NEG))
    frags.append(line(560, 95, 560, 260, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(560, 273, "ω₀", size=12, bold=True))

    # Пояснення посередині
    frags.append(arrow(350, 150, 410, 150, color=FIELD, sw=2))
    frags.append(text(380, 138, "× (2k_BT / ω)", size=11, bold=True, color=FIELD))

    render(os.path.join(OUT_DIR, 'susceptibility-spectrum.svg'), w, h, *frags)

def make_brownian_particle():
    """Фігура 3: Броунівська частинка у рідині — випадкові удари vs в'язке тертя."""
    w, h = 760, 300
    frags = []

    # Заголовок
    frags.append(textbox(380, 22, "Мікроскопічний механізм: Броунівська частинка", size=15, bold=True, fill="#eef2f7", stroke="#2c3e50")[0])

    # Середовище (рідина)
    frags.append(rect(40, 50, 680, 220, fill="#f4f8ff", stroke="#b0c4de", sw=1.5, rx=8))
    frags.append(text(650, 70, "Рідина (Т)", size=12, color=MUTED, bold=True))

    # Молекули рідини
    mols = [(100, 90), (140, 180), (120, 230), (220, 80), (260, 220), (500, 80), (540, 230), (620, 100), (640, 200)]
    for mx, my in mols:
        frags.append(circle(mx, my, 5, fill="#a0c4ff", stroke=NEG, sw=1))

    # Велика Броунівська частинка
    cx, cy = 380, 160
    frags.append(circle(cx, cy, 42, fill="#ffeaa7", stroke="#d63031", sw=2.5))
    frags.append(text(cx, cy - 5, "Частинка", size=13, bold=True, color="#2d3436"))
    frags.append(text(cx, cy + 12, "маса m, швидкість v", size=11, color=MUTED))

    # Сили: випадкові удари
    frags.append(arrow(290, 130, 340, 148, color=POS, sw=2))
    frags.append(text(285, 120, "Хаотичний удар F_fluc(t)", size=11, color=POS, bold=True))

    frags.append(arrow(470, 200, 420, 175, color=POS, sw=2))
    frags.append(text(480, 212, "Тепловий поштовх", size=11, color=POS, bold=True))

    # Сила в'язкого тертя
    frags.append(arrow(380, 160, 460, 160, color="#0984e3", sw=2))
    frags.append(text(420, 150, "Рух v", size=11, color="#0984e3", bold=True))

    frags.append(arrow(380, 160, 310, 160, color=NEG, sw=2.5))
    frags.append(text(330, 178, "Тертя -γv (Дисипація)", size=11, color=NEG, bold=True))

    render(os.path.join(OUT_DIR, 'brownian-particle.svg'), w, h, *frags)

def make_electrical_fdt():
    """Фігура 4: Електричний випадок ТФД — опір R як джерело шуму Джонсона—Найквіста."""
    w, h = 760, 290
    frags = []

    # Заголовок
    frags.append(textbox(380, 22, "Електрична інтерпретація: резистор R як дисипатор і джерело шуму", size=15, bold=True, fill="#eef2f7", stroke="#2c3e50")[0])

    # Ліва схема: Дисипація
    frags.append(rect(60, 55, 300, 215, fill="#ffffff", stroke="#b2bec3", sw=1.5, rx=8))
    frags.append(text(210, 78, "1. Поглинання енергії (Дисипація)", size=13, bold=True, color=POS))
    
    frags.append(rect(175, 120, 70, 35, fill="#ffeaa7", stroke="#d63031", sw=1.5))
    frags.append(text(210, 142, "R (Опір)", size=12, bold=True))
    
    frags.append(circle(100, 180, 18, fill="#eaf0fd", stroke=NEG, sw=1.5))
    frags.append(text(100, 185, "U_ext", size=11, bold=True, color=NEG))
    
    frags.append(line(100, 162, 100, 137, color=LINE, sw=1.5))
    frags.append(line(100, 137, 175, 137, color=LINE, sw=1.5))
    frags.append(line(245, 137, 310, 137, color=LINE, sw=1.5))
    frags.append(line(310, 137, 310, 210, color=LINE, sw=1.5))
    frags.append(line(310, 210, 100, 210, color=LINE, sw=1.5))
    frags.append(line(100, 210, 100, 198, color=LINE, sw=1.5))

    frags.append(text(210, 245, "Виділення тепла: P = U² / R", size=12, bold=True, color=POS))

    # Стрілка еквівалентності
    frags.append(arrow(375, 160, 415, 160, color=FIELD, sw=2.5))
    frags.append(text(395, 145, "ТФД", size=12, bold=True, color=FIELD))

    # Права схема: Еквівалентна шумова схема Найквіста
    frags.append(rect(430, 55, 290, 215, fill="#ffffff", stroke="#b2bec3", sw=1.5, rx=8))
    frags.append(text(575, 78, "2. Тепловий шум (Флуктуації)", size=13, bold=True, color=NEG))

    frags.append(rect(540, 120, 70, 35, fill="#ffeaa7", stroke="#d63031", sw=1.5))
    frags.append(text(575, 142, "R (безшумний)", size=11, bold=True))

    frags.append(circle(470, 180, 18, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(text(470, 185, "U_ш", size=11, bold=True, color=POS))

    frags.append(line(470, 162, 470, 137, color=LINE, sw=1.5))
    frags.append(line(470, 137, 540, 137, color=LINE, sw=1.5))
    frags.append(line(610, 137, 680, 137, color=LINE, sw=1.5))
    frags.append(line(680, 137, 680, 210, color=LINE, sw=1.5))
    frags.append(line(680, 210, 470, 210, color=LINE, sw=1.5))
    frags.append(line(470, 210, 470, 198, color=LINE, sw=1.5))

    frags.append(text(575, 245, "Густина шуму: S_V = 4 k_B T R", size=12, bold=True, color=NEG))

    render(os.path.join(OUT_DIR, 'electrical-fdt.svg'), w, h, *frags)

def make_quantum_classical_fdt():
    """Фігура 5: перехід від класичної межі k_B·T до нульових коливань ℏω/2."""
    C_FLUC = "#e67e22"    # класична межа
    C_QUANT = "#8e44ad"   # квантова крива
    C_AXIS = "#7f8c8d"    # осі

    W, H = 840, 340
    frags = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    frags.append(text(W / 2, 28, "Перехід від класичної до квантової теореми флуктуацій і дисипації", size=16, bold=True))

    ox, oy = 90, 270
    axis_w = 680
    frags.append(line(ox, oy, ox + axis_w, oy, color=C_AXIS, sw=1.8))
    frags.append(arrow(ox + axis_w - 10, oy, ox + axis_w + 15, oy, color=C_AXIS, sw=1.8))
    frags.append(text(ox + axis_w + 25, oy + 4, "Частота ω (або ℏω / k_B T)", size=12, bold=True, color=C_AXIS, anchor="start"))

    frags.append(line(ox, oy, ox, 60, color=C_AXIS, sw=1.8))
    frags.append(arrow(ox, 70, ox, 45, color=C_AXIS, sw=1.8))
    frags.append(text(ox - 10, 50, "Ефективна шумова енергія E_еф", size=12, bold=True, color=C_AXIS, anchor="end"))

    # Класична межа E_еф = k_B T (горизонтальна пряма)
    y_classical = oy - 90
    frags.append(line(ox, y_classical, ox + axis_w - 40, y_classical, color=C_FLUC, sw=2.2, dash="6,4"))
    frags.append(text(ox + 460, y_classical - 12, "Класична межа: E_еф = k_B T (рівнорозподіл)", size=12, color=C_FLUC, bold=True))

    # Квантова крива E_еф = (ℏω / 2) · coth(ℏω / 2k_BT)
    pts_quantum = []
    for px in range(0, 620, 8):
        x_val = px / 100.0  # відношення ℏω / k_B T
        if x_val < 0.05:
            eff = 1.0
        else:
            eff = (x_val / 2.0) / math.tanh(x_val / 2.0)
        pts_quantum.append((ox + px, oy - 90 * eff))

    d_quant = "M " + " L ".join("%.1f,%.1f" % p for p in pts_quantum)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (d_quant, C_QUANT))

    # Асимптота нульових коливань ℏω/2
    frags.append(text(ox + 520, oy - 200, "Квантова межа: ℏω / 2\n(нульові коливання вакууму)", size=12, color=C_QUANT, bold=True))

    # Зона кросоверу
    frags.append(line(ox + 200, oy, ox + 200, oy - 140, color="#bdc3c7", sw=1.2, dash="3,3"))
    frags.append(textbox(ox + 200, oy + 25, "Кросовер: ℏω ≈ k_B T", size=11.5, fill="#f4ecf7", stroke=C_QUANT, pad=6)[0])

    render(os.path.join(OUT_DIR, 'quantum-classical-fdt.svg'), W, H, *frags)

if __name__ == '__main__':
    make_fdt_bridge()
    make_susceptibility_spectrum()
    make_brownian_particle()
    make_electrical_fdt()
    make_quantum_classical_fdt()
    print("Всі 5 SVG-фігур успішно згенеровано у ./img/")
