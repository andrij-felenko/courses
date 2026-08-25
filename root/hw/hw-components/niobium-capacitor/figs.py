#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор технічних SVG-діаграм для теми niobium-capacitor."""

import os
import sys

# Підключення svgkit із scripts/ у корені репозиторію (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def draw_polyline(pts, color=LINE, sw=2, dash=None):
    """Малювання ламаної лінії через послідовність сегментів line()."""
    res = []
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        res.append(line(x1, y1, x2, y2, color=color, sw=sw, dash=dash))
    return "".join(res)


def fig_structure():
    """Будова та шари твердотільного оксидно-ніобієвого конденсатора."""
    w, h = 840, 520
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Внутрішня структура твердотільного SMD ніобієвого конденсатора (NbO)", size=16, bold=True))

    # Корпус (епоксидний компаунд) - рамка без заливки
    frags.append(rect(80, 60, 680, 430, rx=12, fill="none", stroke=MUTED, sw=2))
    b_case, _, _ = textbox(420, 80, "Епоксидний герметичний корпус (Molded Epoxy Case)", size=12, pad=6, fill="#f4f6f8", stroke=MUTED, min_w=340)
    frags.append(b_case)

    # Анодний вивід (зліва)
    frags.append(rect(10, 240, 90, 30, rx=4, fill="#d5dbdb", stroke=LINE, sw=1.5))
    frags.append(text(50, 260, "+ Анод", size=13, bold=True, color=POS))

    # Катодний вивід (справа)
    frags.append(rect(740, 240, 90, 30, rx=4, fill="#d5dbdb", stroke=LINE, sw=1.5))
    frags.append(text(785, 260, "− Катод", size=13, bold=True, color=NEG))

    # Ніобієвий анодний дріт (приварений до виводу x=100 і заходить у сердечник x=210)
    frags.append(rect(100, 248, 105, 14, rx=2, fill="#7f8c8d", stroke=LINE, sw=1.5))
    frags.append(line(205, 220, 205, 290, color=LINE, sw=2))

    # Центральний пористий сердечник (Спічений Nb / NbO) - без заливки, щоб не конфліктувати з блоками
    frags.append(rect(205, 120, 420, 270, rx=8, fill="none", stroke=LINE, sw=2))

    # Шари всередині пористого тіла (зсунуті праворуч x=340, щоб не торкатися анодного дроту x <= 205)
    # 1. Пористий оксидно-ніобієвий анод
    b_anode, _, _ = textbox(345, 160, "1. Пористий анод (NbO / Nb)\nСпічений порошок, питома площа > 1.5 м²/г", size=11, pad=6, fill="#eaeded", stroke=LINE, min_w=240)
    frags.append(b_anode)

    # 2. Анодний діелектрик Nb2O5
    b_diel, _, _ = textbox(345, 240, "2. Діелектрик: оксид Nb₂O₅\nАнодування, ε_r ≈ 41, товщина 15–80 нм", size=11, pad=6, fill="#d4efdf", stroke=FIELD, bold=True, min_w=240)
    frags.append(b_diel)

    # 3. Твердий катодний електроліт (MnO2 або полімер)
    b_cath, _, _ = textbox(345, 320, "3. Твердий електроліт (MnO₂ / Полімер)\nПросочує всі пори анодного сердечника", size=11, pad=6, fill="#d6eaf8", stroke=NEG, min_w=240)
    frags.append(b_cath)

    # Зовнішні інтерфейсні шари анодного блоку (Справа від сердечника)
    frags.append(rect(625, 140, 16, 230, fill="#2c3e50", stroke=LINE, sw=1))  # Вуглецевий шар (Carbon)
    frags.append(rect(641, 140, 16, 230, fill="#bdc3c7", stroke=LINE, sw=1))  # Срібний шар (Silver paint)
    frags.append(rect(657, 170, 73, 170, fill="#f9e79f", stroke="#d4ac0d", sw=1.5)) # Струмопровідний клей

    b_ext, _, _ = textbox(545, 435, "Зовнішні шари катода:\nВуглець (Graphite) → Срібна фарба (Ag) → Струмопровідний клей", size=11, pad=6, fill="#fef9e7", stroke="#d4ac0d", min_w=400)
    frags.append(b_ext)

    # З'єднувальні містки
    frags.append(line(633, 130, 633, 140, color=LINE, sw=1.5))
    frags.append(line(649, 130, 649, 140, color=LINE, sw=1.5))
    frags.append(line(693, 340, 693, 400, color="#d4ac0d", sw=1.5))
    frags.append(line(730, 255, 740, 255, color="#d4ac0d", sw=2))

    render(os.path.join(OUT_DIR, "structure-and-materials.svg"), w, h, *frags)


def fig_self_healing():
    """Фізика відмови: катастрофічне горіння танталу проти самопасивації ніобію."""
    w, h = 840, 480
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Порівняння реакції на локальний пробій: тантал (Ta) проти ніобій-оксиду (NbO)", size=16, bold=True))

    # Ліва колонка: Тантал + MnO2 (Рамка без заливки)
    frags.append(rect(30, 60, 370, 390, rx=8, fill="none", stroke=POS, sw=2))
    frags.append(text(215, 88, "Танталовий конденсатор (Ta / MnO₂)", size=14, bold=True, color=POS))

    b_ta1, _, _ = textbox(215, 130, "1. Локальний дефект діелектрика Ta₂O₅\nСплеск струму → точковий нагрів > 450 °C", size=11, pad=6, fill="#ffffff", stroke=POS, min_w=330)
    frags.append(b_ta1)

    b_ta2, _, _ = textbox(215, 210, "2. Термічний розпад катода MnO₂\n2 MnO₂ → Mn₂O₃ + O₂↑ (виділення вільного кисню)", size=11, pad=6, fill="#ffffff", stroke=POS, min_w=330)
    frags.append(b_ta2)

    b_ta3, _, _ = textbox(215, 290, "3. Екзотермічне окиснення металу\n4 Ta + 5 O₂ → 2 Ta₂O₅ + ΔH (T > 2000 °C)", size=11, pad=6, fill="#ffffff", stroke=POS, min_w=330)
    frags.append(b_ta3)

    b_ta4, _, _ = textbox(215, 385, "НАСЛІДОК: теплове розганяння (Thermal Runaway)\nКоротке замикання, відкрите полум'я, дим і прогар плати", size=11, pad=8, fill="#f9d5d5", stroke=POS, bold=True, min_w=330)
    frags.append(b_ta4)

    frags.append(arrow(215, 160, 215, 182, color=POS, sw=2))
    frags.append(arrow(215, 240, 215, 262, color=POS, sw=2))
    frags.append(arrow(215, 320, 215, 347, color=POS, sw=2))

    # Права колонка: Ніобій-оксид NbO (Рамка без заливки)
    frags.append(rect(440, 60, 370, 390, rx=8, fill="none", stroke=FIELD, sw=2))
    frags.append(text(625, 88, "Оксидно-ніобієвий (NbO / MnO₂)", size=14, bold=True, color=FIELD))

    b_nb1, _, _ = textbox(625, 130, "1. Локальний пробій діелектрика Nb₂O₅\nСплеск струму → локальне розігрівання зони дефекту", size=11, pad=6, fill="#ffffff", stroke=FIELD, min_w=330)
    frags.append(b_nb1)

    b_nb2, _, _ = textbox(625, 210, "2. Відновлення до нижчих оксидів\nNb₂O₅ → 2 NbO₂ + ½ O₂ (енергопоглинальна реакція)", size=11, pad=6, fill="#ffffff", stroke=FIELD, min_w=330)
    frags.append(b_nb2)

    b_nb3, _, _ = textbox(625, 290, "3. Формування ізоляційного корка\nNbO₂ має високий опір (ρ ~ 10²–10⁴ Ом·см) → струм спадає", size=11, pad=6, fill="#ffffff", stroke=FIELD, min_w=330)
    frags.append(b_nb3)

    b_nb4, _, _ = textbox(625, 385, "НАСЛІДОК: самопасивація (Self-Passivation)\nБезпечний обрив кола (Open Circuit), нульовий ризик пожежі", size=11, pad=8, fill="#d4efdf", stroke=FIELD, bold=True, min_w=330)
    frags.append(b_nb4)

    frags.append(arrow(625, 160, 625, 182, color=FIELD, sw=2))
    frags.append(arrow(625, 240, 625, 262, color=FIELD, sw=2))
    frags.append(arrow(625, 320, 625, 347, color=FIELD, sw=2))

    render(os.path.join(OUT_DIR, "self-healing-mechanism.svg"), w, h, *frags)


def fig_dielectric_comparison():
    """Порівняння діелектриків: Al2O3 vs Ta2O5 vs Nb2O5."""
    w, h = 840, 440
    frags = []

    frags.append(text(w / 2, 28, "Порівняльні характеристики вентильних діелектриків: Al₂O₃, Ta₂O₅ та Nb₂O₅", size=16, bold=True))

    # Стовпець 1: Алюміній Al2O3 (Рамка без заливки)
    frags.append(rect(40, 60, 230, 350, rx=8, fill="none", stroke=LINE, sw=1.5))
    frags.append(text(155, 90, "Алюміній (Al₂O₃)", size=14, bold=True))
    b_al_eps, _, _ = textbox(155, 140, "Проникність: ε_r ≈ 9.5\nБазова поляризація", size=11, pad=6, fill="#ffffff", stroke=MUTED, min_w=190)
    frags.append(b_al_eps)
    b_al_rho, _, _ = textbox(155, 215, "Густина металу: 2.70 г/см³\nЛегкий, але низька ε_r", size=11, pad=6, fill="#ffffff", stroke=MUTED, min_w=190)
    frags.append(b_al_rho)
    b_al_v, _, _ = textbox(155, 290, "Товщина оксиду: ~1.2 нм/В\nВисока напруга (> 500 В)", size=11, pad=6, fill="#ffffff", stroke=MUTED, min_w=190)
    frags.append(b_al_v)
    b_al_cv, _, _ = textbox(155, 365, "CV/cc: Низька / Середня\nВеликі габарити банки", size=11, pad=6, fill="#eaeded", stroke=LINE, min_w=190)
    frags.append(b_al_cv)

    # Стовпець 2: Тантал Ta2O5 (Рамка без заливки)
    frags.append(rect(305, 60, 230, 350, rx=8, fill="none", stroke=POS, sw=1.5))
    frags.append(text(420, 90, "Тантал (Ta₂O₅)", size=14, bold=True, color=POS))
    b_ta_eps, _, _ = textbox(420, 140, "Проникність: ε_r ≈ 27\nВисока питома ємність", size=11, pad=6, fill="#ffffff", stroke=POS, min_w=190)
    frags.append(b_ta_eps)
    b_ta_rho, _, _ = textbox(420, 215, "Густина металу: 16.65 г/см³\nВажкий, дорогий ресурс", size=11, pad=6, fill="#ffffff", stroke=POS, min_w=190)
    frags.append(b_ta_rho)
    b_ta_v, _, _ = textbox(420, 290, "Товщина оксиду: ~1.7 нм/В\nНапруги до 50 В", size=11, pad=6, fill="#ffffff", stroke=POS, min_w=190)
    frags.append(b_ta_v)
    b_ta_cv, _, _ = textbox(420, 365, "CV/cc: Дуже висока\nАле ризик займання", size=11, pad=6, fill="#fadbd8", stroke=POS, min_w=190)
    frags.append(b_ta_cv)

    # Стовпець 3: Ніобій-оксид Nb2O5 (Рамка без заливки)
    frags.append(rect(570, 60, 230, 350, rx=8, fill="none", stroke=FIELD, sw=2))
    frags.append(text(685, 90, "Ніобій-оксид (Nb₂O₅)", size=14, bold=True, color=FIELD))
    b_nb_eps, _, _ = textbox(685, 140, "Проникність: ε_r ≈ 41–42\nНайвища серед оксидів!", size=11, pad=6, fill="#ffffff", stroke=FIELD, bold=True, min_w=190)
    frags.append(b_nb_eps)
    b_nb_rho, _, _ = textbox(685, 215, "Густина металу: 4.57 г/см³\nУ 3.6× легший за тантал", size=11, pad=6, fill="#ffffff", stroke=FIELD, min_w=190)
    frags.append(b_nb_rho)
    b_nb_v, _, _ = textbox(685, 290, "Товщина оксиду: ~3.7 нм/В\nОптимум під низьку V (≤ 10 В)", size=11, pad=6, fill="#ffffff", stroke=FIELD, min_w=190)
    frags.append(b_nb_v)
    b_nb_cv, _, _ = textbox(685, 365, "CV/cc: Висока + Безпека\nНеспаленна конструкція", size=11, pad=6, fill="#d4efdf", stroke=FIELD, bold=True, min_w=190)
    frags.append(b_nb_cv)

    render(os.path.join(OUT_DIR, "dielectric-comparison.svg"), w, h, *frags)


def fig_derating():
    """Криві дератингу напруги за температурою: NbO проти Ta MnO2 проти Polymer."""
    w, h = 840, 460
    frags = []

    frags.append(text(w / 2, 28, "Вимоги до дератингу напруги (Voltage Derating) за температурою", size=16, bold=True))

    ox, oy, gw, gh = 90, 380, 680, 270
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2))

    # Сітка Y (0%, 20%, 50%, 80%, 100%)
    for pct, label in [(0, "0%"), (20, "20%"), (50, "50%"), (80, "80%"), (100, "100%")]:
        y_pos = oy - (pct / 100.0) * gh
        frags.append(line(ox, y_pos, ox + gw, y_pos, color="#e5e7e9", sw=1))
        frags.append(text(ox - 25, y_pos + 4, label, size=11, anchor="end", color=MUTED))

    # Позначки осі X
    temps = [(-55, 0.0), (25, 0.44), (85, 0.78), (105, 0.89), (125, 1.0)]
    for temp, frac in temps:
        x_pos = ox + frac * gw
        frags.append(line(x_pos, oy, x_pos, oy + 6, color=LINE, sw=1.5))
        frags.append(text(x_pos, oy + 22, f"{temp} °C", size=11, color=MUTED))

    frags.append(text(ox + gw / 2, oy + 44, "Температура навколишнього середовища (°C)", size=12, bold=True))
    frags.append(text(ox - 55, oy - gh / 2, "V_op / V_rated", size=12, bold=True, anchor="middle"))

    # Крива 1: Твердотільний тантал Ta MnO2 (Червоний - жорсткий 50% дератинг)
    x_m55 = ox + 0.0 * gw
    x_85 = ox + 0.78 * gw
    x_125 = ox + 1.0 * gw
    y_50 = oy - 0.50 * gh
    y_33 = oy - 0.33 * gh
    frags.append(line(x_m55, y_50, x_85, y_50, color=POS, sw=3))
    frags.append(line(x_85, y_50, x_125, y_33, color=POS, sw=3))

    # Крива 2: Оксидно-ніобієвий NbO MnO2 (Зелений - помірний 20% дератинг)
    y_80 = oy - 0.80 * gh
    frags.append(line(x_m55, y_80, x_85, y_80, color=FIELD, sw=3))
    frags.append(line(x_85, y_80, x_125, y_50, color=FIELD, sw=3))

    # Крива 3: Провідний полімер Ta / Nb (Синій - дератинг 10-20%)
    y_90 = oy - 0.90 * gh
    y_60 = oy - 0.60 * gh
    x_105 = ox + 0.89 * gw
    frags.append(line(x_m55, y_90, x_105, y_90, color=NEG, sw=2, dash="4,3"))
    frags.append(line(x_105, y_90, x_125, y_60, color=NEG, sw=2, dash="4,3"))

    # Пояснювальні плашки
    b_nb_lbl, _, _ = textbox(310, 80, "Оксидно-ніобієвий NbO (20% дератинг до +85 °C)\nБезпечна зона: 0.8 · V_rated на шині живлення", size=11, pad=6, fill="#eafaf1", stroke=FIELD, bold=True, min_w=310)
    frags.append(b_nb_lbl)

    b_ta_lbl, _, _ = textbox(310, 210, "Танталовий Ta MnO₂ (50% дератинг обов'язковий!)\nЛише 0.5 · V_rated через ризик займання", size=11, pad=6, fill="#fdedec", stroke=POS, bold=True, min_w=310)
    frags.append(b_ta_lbl)

    b_poly_lbl, _, _ = textbox(630, 80, "Полімерні Ta/Nb (10–20% дератинг)\nШирокий температурний діапазон", size=11, pad=6, fill="#ebf5fb", stroke=NEG, min_w=220)
    frags.append(b_poly_lbl)

    render(os.path.join(OUT_DIR, "derating-and-temperature.svg"), w, h, *frags)


def fig_frequency():
    """Частотна характеристика імпедансу |Z| та ESR для різних типів конденсаторів."""
    w, h = 840, 480
    frags = []

    frags.append(text(w / 2, 28, "Частотні залежності імпедансу |Z| та ESR: NbO проти Ta проти MLCC", size=16, bold=True))

    ox, oy, gw, gh = 90, 400, 680, 250
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2))

    # Горизонтальна сітка
    imp_labels = [("10 Ом", 0.95), ("1 Ом", 0.70), ("100 мОм", 0.45), ("10 мОм", 0.20), ("1 мОм", 0.0)]
    for lbl, frac in imp_labels:
        y_pos = oy - frac * gh
        frags.append(line(ox, y_pos, ox + gw, y_pos, color="#f2f4f4", sw=1))
        frags.append(text(ox - 15, y_pos + 4, lbl, size=10, anchor="end", color=MUTED))

    # Позначки частоти на осі X
    freqs = [("100 Гц", 0.0), ("1 кГц", 0.2), ("10 кГц", 0.4), ("100 кГц", 0.6), ("1 МГц", 0.8), ("10 МГц", 1.0)]
    for lbl, frac in freqs:
        x_pos = ox + frac * gw
        frags.append(line(x_pos, oy, x_pos, oy + 6, color=LINE, sw=1.5))
        frags.append(text(x_pos, oy + 22, lbl, size=11, color=MUTED))

    frags.append(text(ox + gw / 2, oy + 44, "Частота сигналу f", size=12, bold=True))
    frags.append(text(ox - 55, oy - gh / 2, "Імпеданс |Z|", size=12, bold=True, anchor="middle"))

    # V-подібні криві для різних типів:
    # 1. NbO з катодом MnO2 (100 мкФ, ESR ~ 200 мОм, f0 ~ 300 кГц)
    p_nbo = [(ox + 0.0 * gw, oy - 0.95 * gh), (ox + 0.3 * gw, oy - 0.70 * gh), (ox + 0.55 * gw, oy - 0.45 * gh),
             (ox + 0.68 * gw, oy - 0.45 * gh), (ox + 0.85 * gw, oy - 0.60 * gh), (ox + 1.0 * gw, oy - 0.80 * gh)]
    frags.append(draw_polyline(p_nbo, color=FIELD, sw=3))

    # 2. NbO / Ta з провідним полімером (100 мкФ, ESR ~ 25 мОм, f0 ~ 500 кГц)
    p_poly = [(ox + 0.0 * gw, oy - 0.95 * gh), (ox + 0.3 * gw, oy - 0.70 * gh), (ox + 0.6 * gw, oy - 0.25 * gh),
              (ox + 0.75 * gw, oy - 0.25 * gh), (ox + 0.9 * gw, oy - 0.50 * gh), (ox + 1.0 * gw, oy - 0.75 * gh)]
    frags.append(draw_polyline(p_poly, color=NEG, sw=2.5, dash="4,3"))

    # 3. Кераміка MLCC X7R (100 мкФ, ESR ~ 3 мОм, f0 ~ 1 МГц)
    p_mlcc = [(ox + 0.0 * gw, oy - 0.95 * gh), (ox + 0.4 * gw, oy - 0.60 * gh), (ox + 0.8 * gw, oy - 0.08 * gh),
              (ox + 0.9 * gw, oy - 0.32 * gh), (ox + 1.0 * gw, oy - 0.58 * gh)]
    frags.append(draw_polyline(p_mlcc, color=LINE, sw=2))

    # Легенда розміщена вгорі над графіком (y = 70..120)
    b_leg1, _, _ = textbox(250, 80, "NbO + MnO₂ (100 мкФ): стабільний плаский ESR (~200 мОм)\nЧудове демпфування резонансів без дзвону", size=11, pad=6, fill="#eafaf1", stroke=FIELD, bold=True, min_w=340)
    frags.append(b_leg1)

    b_leg2, _, _ = textbox(620, 65, "Nb / Ta Полімер (100 мкФ)\nУльтранизький ESR (~25 мОм)", size=11, pad=5, fill="#ebf5fb", stroke=NEG, min_w=220)
    frags.append(b_leg2)

    b_leg3, _, _ = textbox(620, 115, "Кераміка MLCC 100 мкФ\nESR < 5 мОм, але гострий Q-пік", size=11, pad=5, fill="#f4f6f8", stroke=LINE, min_w=220)
    frags.append(b_leg3)

    render(os.path.join(OUT_DIR, "impedance-esr-frequency.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_structure()
    fig_self_healing()
    fig_dielectric_comparison()
    fig_derating()
    fig_frequency()
    print("Усі 5 SVG-діаграм успішно згенеровано.")
