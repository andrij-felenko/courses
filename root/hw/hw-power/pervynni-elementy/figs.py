# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'Первинні елементи: літій-тіоніл, лужні, монетка'."""

import os
import sys

# Шлях до спільних помічників svgkit у scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_chem_comparison():
    """Порівняння трьох головних первинних електрохімічних систем."""
    w, h = 820, 360
    frags = []

    # Заголовок блоків-колонок
    cols = [
        ("Літій-тіонілхлорид (Li-SOCl₂)", 50, 50, 220, 290, "#eef6fc", "#2457d6"),
        ("Монетний літій (CR2032 Li-MnO₂)", 300, 50, 220, 290, "#fcf7ee", "#d97706"),
        ("Лужний елемент (Alkaline Zn-MnO₂)", 550, 50, 220, 290, "#f3f4f6", "#4b5563"),
    ]

    for title, x, y, cw, ch, bg_col, border_col in cols:
        # Фон колонки
        frags.append(rect(x, y, cw, ch, fill=bg_col, stroke=border_col, sw=1.5, rx=8))
        # Заголовок колонки
        frags.append(fitbox(x + 10, y + 10, cw - 20, 38, title, size=13, bold=True, fill=BG, stroke=border_col))

    # Вміст для Li-SOCl2
    lisocl_lines = [
        "Номінал: 3.6 В (плато)",
        "Густина: 650 Вт·год/кг",
        "Об'ємна: 1200 Вт·год/л",
        "Саморозряд: < 1% / рік",
        "Термін: 10–20+ років",
        "Діапазон: −55...+85 °C",
        "ESR (бобіна): 30–100 Ом",
        "Пік: пасивація → HLC",
        "Застосування: лічильники,",
        "промисловий IoT, трекери"
    ]
    frags.append(fitbox(60, 105, 200, 220, "\n".join(lisocl_lines), size=12, pad=6, fill=BG, stroke="#cbd5e1"))

    # Вміст для CR2032
    cr_lines = [
        "Номінал: 3.0 В (спад до 2.0)",
        "Густина: 260 Вт·год/кг",
        "Об'ємна: 600 Вт·год/л",
        "Саморозряд: ~1–2% / рік",
        "Термін: 5–10 років",
        "Діапазон: −20...+70 °C",
        "ESR: 10–40 Ом (до 100)",
        "Пік: 15–30 мА (просадка)",
        "Застосування: годинники RTC,",
        "маяки BLE, мікропульсометри"
    ]
    frags.append(fitbox(310, 105, 200, 220, "\n".join(cr_lines), size=12, pad=6, fill=BG, stroke="#cbd5e1"))

    # Вміст для Alkaline
    alk_lines = [
        "Номінал: 1.5 В (спад до 0.9)",
        "Густина: 140 Вт·год/кг",
        "Об'ємна: 350 Вт·год/л",
        "Саморозряд: ~2–3% / рік",
        "Термін: 5–7 років",
        "Діапазон: −10...+50 °C",
        "ESR: 0.15–0.5 Ом (нова)",
        "Ефект Пойкерта: високий",
        "Застосування: пульти ДК,",
        "іграшки, ліхтарики, мишки"
    ]
    frags.append(fitbox(560, 105, 200, 220, "\n".join(alk_lines), size=12, pad=6, fill=BG, stroke="#cbd5e1"))

    render(os.path.join(OUT_DIR, "chem-comparison.svg"), w, h, *frags, title="Порівняння первинних електрохімічних систем")


def fig_discharge_curves():
    """Криві розряду під помірним навантаженням."""
    w, h = 820, 420
    frags = []

    # Сітка координат
    ox, oy = 100, 340
    gw, gh = 660, 260

    # Вісь X та Y
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5))

    # Горизонтальні позначки напруги
    voltages = [
        (4.0, oy - gh * (4.0 / 4.0), "4.0 В"),
        (3.6, oy - gh * (3.6 / 4.0), "3.6 В"),
        (3.0, oy - gh * (3.0 / 4.0), "3.0 В"),
        (2.0, oy - gh * (2.0 / 4.0), "2.0 В"),
        (1.5, oy - gh * (1.5 / 4.0), "1.5 В"),
        (1.0, oy - gh * (1.0 / 4.0), "1.0 В"),
        (0.0, oy, "0.0 В"),
    ]
    for v, ypos, lbl in voltages:
        frags.append(line(ox - 6, ypos, ox + gw, ypos, color="#e5e7eb", sw=1, dash="4,4"))
        frags.append(text(ox - 14, ypos + 4, lbl, size=11, color=MUTED, anchor="end"))

    # Позначки ємності по осі X
    caps = [
        (0, ox, "0%"),
        (25, ox + gw * 0.25, "25%"),
        (50, ox + gw * 0.50, "50%"),
        (75, ox + gw * 0.75, "75%"),
        (100, ox + gw, "100%"),
    ]
    for cap_pct, xpos, lbl in caps:
        frags.append(line(xpos, oy, xpos, oy + 6, color=LINE, sw=1.2))
        frags.append(text(xpos, oy + 22, lbl, size=11, color=MUTED, anchor="middle"))

    frags.append(text(ox + gw / 2, oy + 42, "Віддана ємність від номіналу (%)", size=13, bold=True, anchor="middle"))
    frags.append(text(ox - 55, oy - gh / 2, "Напруга (В)", size=13, bold=True, anchor="middle"))

    # Крива Li-SOCl2 (синій колір) - плоске плато 3.6 В до 95%, потім обрив
    # (0, 3.65) -> (10, 3.60) -> (90, 3.58) -> (95, 3.45) -> (98, 2.5) -> (100, 1.8)
    lisocl_pts = [
        (ox, oy - gh * (3.65 / 4.0)),
        (ox + gw * 0.1, oy - gh * (3.60 / 4.0)),
        (ox + gw * 0.85, oy - gh * (3.58 / 4.0)),
        (ox + gw * 0.94, oy - gh * (3.45 / 4.0)),
        (ox + gw * 0.97, oy - gh * (2.80 / 4.0)),
        (ox + gw * 1.00, oy - gh * (1.80 / 4.0)),
    ]
    path_lisocl = "M " + " L ".join(["%.1f,%.1f" % p for p in lisocl_pts])
    frags.append('<path d="%s" fill="none" stroke="#2457d6" stroke-width="3"/>' % path_lisocl)

    # Крива CR2032 Li-MnO2 (помаранчевий колір) - 3.0 В на старті, пологе зниження до 2.7 В, злам на 85% до 2.0 В
    cr_pts = [
        (ox, oy - gh * (3.10 / 4.0)),
        (ox + gw * 0.05, oy - gh * (2.95 / 4.0)),
        (ox + gw * 0.50, oy - gh * (2.80 / 4.0)),
        (ox + gw * 0.80, oy - gh * (2.65 / 4.0)),
        (ox + gw * 0.92, oy - gh * (2.30 / 4.0)),
        (ox + gw * 1.00, oy - gh * (2.00 / 4.0)),
    ]
    path_cr = "M " + " L ".join(["%.1f,%.1f" % p for p in cr_pts])
    frags.append('<path d="%s" fill="none" stroke="#d97706" stroke-width="3"/>' % path_cr)

    # Крива Alkaline Zn-MnO2 (сіро-зелений колір) - похила лінія від 1.55 В до 0.9 В
    alk_pts = [
        (ox, oy - gh * (1.58 / 4.0)),
        (ox + gw * 0.15, oy - gh * (1.40 / 4.0)),
        (ox + gw * 0.40, oy - gh * (1.25 / 4.0)),
        (ox + gw * 0.70, oy - gh * (1.12 / 4.0)),
        (ox + gw * 0.90, oy - gh * (1.00 / 4.0)),
        (ox + gw * 1.00, oy - gh * (0.85 / 4.0)),
    ]
    path_alk = "M " + " L ".join(["%.1f,%.1f" % p for p in alk_pts])
    frags.append('<path d="%s" fill="none" stroke="#059669" stroke-width="3"/>' % path_alk)

    # Легенда праворуч зверху
    leg_x, leg_y = ox + 360, oy - gh + 15
    frags.append(rect(leg_x, leg_y, 280, 85, fill=BG, stroke="#cbd5e1", sw=1.2, rx=6))
    
    frags.append(line(leg_x + 12, leg_y + 20, leg_x + 35, leg_y + 20, color="#2457d6", sw=3))
    frags.append(text(leg_x + 45, leg_y + 24, "Li-SOCl₂: ідеальне плато 3.6 В", size=12, bold=True, anchor="start"))

    frags.append(line(leg_x + 12, leg_y + 45, leg_x + 35, leg_y + 45, color="#d97706", sw=3))
    frags.append(text(leg_x + 45, leg_y + 49, "CR2032 Li-MnO₂: плато 2.9–2.7 В", size=12, bold=True, anchor="start"))

    frags.append(line(leg_x + 12, leg_y + 70, leg_x + 35, leg_y + 70, color="#059669", sw=3))
    frags.append(text(leg_x + 45, leg_y + 74, "Alkaline Zn-MnO₂: похилий спад 1.5→0.9 В", size=12, bold=True, anchor="start"))

    render(os.path.join(OUT_DIR, "discharge-curves.svg"), w, h, *frags, title="Профілі розрядних кривих первинних систем")


def fig_passivation_hlc():
    """Механізм пасивації Li-SOCl2 та гібридне джерело з HLC."""
    w, h = 820, 380
    frags = []

    # Лівий блок: фізична структура пасивації
    frags.append(rect(40, 50, 350, 300, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(fitbox(55, 60, 320, 32, "Пасивація літієвого анода плівкою LiCl", size=13, bold=True, fill=BG, stroke="#cbd5e1"))

    # Схема шарів
    frags.append(rect(65, 105, 110, 90, fill="#e2e8f0", stroke="#475569", sw=1.5))
    frags.append(mtext(120, 145, "Металевий\nанод Li", size=12, bold=True, anchor="middle"))

    frags.append(rect(175, 105, 30, 90, fill="#fee2e2", stroke="#ef4444", sw=1.5))
    frags.append(mtext(190, 145, "LiCl\nплівка", size=10, bold=True, color="#b91c1c", anchor="middle"))

    frags.append(rect(205, 105, 165, 90, fill="#eff6ff", stroke="#3b82f6", sw=1.5))
    frags.append(mtext(287, 145, "Рідкий катод/електроліт\nSOCl₂ + вуглецевий картон", size=11, bold=True, color="#1e40af", anchor="middle"))

    # Пояснення ефекту
    pass_expl = [
        "• Плівка LiCl захищає від саморозряду (<1%/рік)",
        "• При зберіганні кристали LiCl товщають",
        "• Різкий імпульс струму → просідання до TMV",
        "• TMV (Transient Min Voltage) < 2.2 В → ресет MCU"
    ]
    frags.append(fitbox(55, 210, 320, 125, "\n".join(pass_expl), size=11, pad=6, fill=BG, stroke="#e2e8f0"))

    # Правий блок: Гібридне джерело Li-SOCl2 + HLC
    frags.append(rect(430, 50, 350, 300, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(fitbox(445, 60, 320, 32, "Гібрид: Li-SOCl₂ бобіна + HLC конденсатор", size=13, bold=True, fill=BG, stroke="#86efac"))

    # Схема паралельного з'єднання
    frags.append(rect(455, 105, 130, 75, fill=BG, stroke="#2457d6", sw=1.5, rx=6))
    frags.append(mtext(520, 135, "Li-SOCl₂ бобіна\n3.6 В (велика ємність,\nслабкий струм)", size=11, bold=True, color="#1d4ed8", anchor="middle"))

    frags.append(rect(635, 105, 130, 75, fill=BG, stroke="#16a34a", sw=1.5, rx=6))
    frags.append(mtext(700, 135, "HLC / суперкап\n(низький ESR <0.5 Ом,\nімпульси 1–2 А)", size=11, bold=True, color="#15803d", anchor="middle"))

    # Лінії паралельного з'єднання
    frags.append(line(520, 105, 520, 95, color=LINE, sw=1.5))
    frags.append(line(700, 105, 700, 95, color=LINE, sw=1.5))
    frags.append(line(520, 95, 700, 95, color=LINE, sw=1.5))

    frags.append(line(520, 180, 520, 190, color=LINE, sw=1.5))
    frags.append(line(700, 180, 700, 190, color=LINE, sw=1.5))
    frags.append(line(520, 190, 700, 190, color=LINE, sw=1.5))

    # Стрілка заряджання
    frags.append(arrow(585, 142, 630, 142, color="#2457d6", sw=1.5))
    frags.append(text(608, 134, "I_підзаряд", size=9, bold=True, color="#2457d6", anchor="middle"))

    # Пояснення роботи гібрида
    hlc_expl = [
        "1. У сні Li-SOCl₂ повільно підзаряджає HLC мікроамперами",
        "2. Під час передачі (LoRa/NB-IoT) HLC віддає 100–500 мА",
        "3. Напруга живлення лишається > 3.3 В (без збоїв MCU)",
        "4. Бобіна не перевантажується і працює 15–20 років"
    ]
    frags.append(fitbox(445, 210, 320, 125, "\n".join(hlc_expl), size=11, pad=6, fill=BG, stroke="#bbf7d0"))

    render(os.path.join(OUT_DIR, "passivation-hlc.svg"), w, h, *frags, title="Пасивація Li-SOCl₂ та розв'язання через гібридний конденсатор")


def fig_coin_cell_sag():
    """Еквівалентна схема монетного елемента CR2032 та імпульсне просідання напруги."""
    w, h = 820, 360
    frags = []

    # Лівий блок: Еквівалентна схема під навантаженням
    frags.append(rect(40, 50, 360, 280, fill="#fafaf9", stroke="#78716c", sw=1.5, rx=8))
    frags.append(fitbox(55, 60, 330, 30, "Еквівалентна схема CR2032 під навантаженням", size=13, bold=True, fill=BG, stroke="#d6d3d1"))

    # Модель батареї: Vocv + ESR
    frags.append(rect(65, 105, 140, 95, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(mtext(135, 130, "CR2032\nV_ocv = 3.0 В\nESR = 20–40 Ом", size=11, bold=True, color="#92400e", anchor="middle"))

    # Буферний конденсатор
    frags.append(rect(225, 105, 75, 95, fill="#ecfdf5", stroke="#10b981", sw=1.5, rx=6))
    frags.append(mtext(262, 145, "C_buf\n100 мкФ\n(low leak)", size=10, bold=True, color="#065f46", anchor="middle"))

    # Навантаження MCU / Radio
    frags.append(rect(320, 105, 65, 95, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    frags.append(mtext(352, 145, "BLE\nRadio\n20 мА", size=10, bold=True, color="#1e40af", anchor="middle"))

    # Лінії живлення
    frags.append(line(135, 105, 352, 105, color=POS, sw=2))
    frags.append(line(135, 200, 352, 200, color=NEG, sw=2))

    # Текстовий опис розрахунку
    calc_text = [
        "Без C_buf при I_tx = 20 мА та ESR = 30 Ом:",
        "ΔU = I_tx · ESR = 0.02 А · 30 Ом = 0.60 В",
        "U_out = 2.80 В − 0.60 В = 2.20 В (Brownout!)",
        "З C_buf: струм береться з заряду конденсатора"
    ]
    frags.append(fitbox(55, 215, 330, 100, "\n".join(calc_text), size=11, pad=6, fill=BG, stroke="#e7e5e4"))

    # Правий блок: Осцилограма напруги під час передачі BLE
    frags.append(rect(430, 50, 350, 280, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(fitbox(445, 60, 320, 30, "Осцилограма просідання напруги шини Vcc", size=13, bold=True, fill=BG, stroke="#cbd5e1"))

    # Осі графіка осцилограми
    gx, gy, gw_g, gh_g = 480, 240, 270, 130
    frags.append(line(gx, gy, gx + gw_g, gy, color=LINE, sw=1.5))
    frags.append(line(gx, gy, gx, gy - gh_g, color=LINE, sw=1.5))

    # Рівні напруги
    frags.append(text(gx - 8, gy - gh_g * 0.90, "3.0 В", size=10, color=MUTED, anchor="end"))
    frags.append(text(gx - 8, gy - gh_g * 0.70, "2.6 В", size=10, color=MUTED, anchor="end"))
    frags.append(text(gx - 8, gy - gh_g * 0.35, "2.0 В (UVLO)", size=10, color=POS, anchor="end"))
    frags.append(line(gx - 4, gy - gh_g * 0.35, gx + gw_g, gy - gh_g * 0.35, color="#fca5a5", sw=1, dash="4,3"))

    # Сигнал струму імпульсу (внизу)
    frags.append(rect(gx + 50, gy - 25, 90, 25, fill="#fee2e2", stroke=POS, sw=1.2))
    frags.append(text(gx + 95, gy - 10, "TX 20 мА (5 мс)", size=9, bold=True, color=POS, anchor="middle"))

    # Крива без конденсатора (провал нижче UVLO)
    bad_pts = [
        (gx, gy - gh_g * 0.85),
        (gx + 50, gy - gh_g * 0.85),
        (gx + 51, gy - gh_g * 0.25),
        (gx + 140, gy - gh_g * 0.23),
        (gx + 141, gy - gh_g * 0.84),
        (gx + gw_g, gy - gh_g * 0.84)
    ]
    path_bad = "M " + " L ".join(["%.1f,%.1f" % p for p in bad_pts])
    frags.append('<path d="%s" fill="none" stroke="#ef4444" stroke-width="2" stroke-dasharray="3,3"/>' % path_bad)

    # Крива з буферним конденсатором (плавний неглибокий спад)
    good_pts = [
        (gx, gy - gh_g * 0.85),
        (gx + 50, gy - gh_g * 0.85),
        (gx + 80, gy - gh_g * 0.72),
        (gx + 140, gy - gh_g * 0.65),
        (gx + 200, gy - gh_g * 0.84),
        (gx + gw_g, gy - gh_g * 0.84)
    ]
    path_good = "M " + " L ".join(["%.1f,%.1f" % p for p in good_pts])
    frags.append('<path d="%s" fill="none" stroke="#16a34a" stroke-width="2.5"/>' % path_good)

    # Підписи до кривих
    frags.append(text(gx + 150, gy - gh_g * 0.15, "Без C_buf: ресет UVLO!", size=10, bold=True, color="#dc2626", anchor="start"))
    frags.append(text(gx + 150, gy - gh_g * 0.62, "З C_buf: запас > 0.6 В", size=10, bold=True, color="#16a34a", anchor="start"))

    render(os.path.join(OUT_DIR, "coin-cell-sag.svg"), w, h, *frags, title="Просідання напруги CR2032 при радіопередачі")


if __name__ == "__main__":
    fig_chem_comparison()
    fig_discharge_curves()
    fig_passivation_hlc()
    fig_coin_cell_sag()
    print("Всі 4 фігури успішно згенеровано.")
