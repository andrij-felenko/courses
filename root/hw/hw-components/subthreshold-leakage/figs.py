# -*- coding: utf-8 -*-
"""Фігури до теми «Підпороговий струм і витік» (book/electronics/microelectronics).
Запуск: python figs.py  -> генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Кольори напівпровідникових областей
P_SUB   = "#edf3ec"   # p-підкладка
P_STRK  = "#5a7a58"
N_REG   = "#d8e3f5"   # n+ витік / стік
N_STRK  = "#2a59a8"
OX_FILL = "#fff8db"   # оксид діелектрика
OX_STRK = "#d4a017"
GT_FILL = "#e2e6eb"   # металевий/полі затвор
GT_STRK = "#4b5563"
DEP_FIL = "#f9edf2"   # збіднена область
DEP_STR = "#a84e6c"
WARN_BG = "#fdecea"
WARN_BD = "#c0392b"
OK_BG   = "#e8f5e9"
OK_BD   = "#2e7d32"


def fig_potential_barrier():
    """1. Енергетичний бар'єр у слабкій інверсії та вплив напруги затвора й стоку (DIBL)."""
    w, h = 820, 360
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Електростатичний бар'єр дна зони провідності між витоком і стоком", size=15, bold=True))

    # Вісь енергії та координати
    frags.append(arrow(60, 310, 60, 50, color=LINE, sw=1.6))
    frags.append(text(50, 48, "Енергія електронів E", size=12, color=INK, anchor="start", bold=True))
    frags.append(arrow(60, 310, 770, 310, color=LINE, sw=1.6))
    frags.append(text(765, 328, "Координата x (вздовж каналу)", size=12, color=INK, anchor="end", bold=True))

    # Зони витоку, каналу, стоку
    frags.append(rect(80, 70, 150, 230, fill=N_REG, stroke=N_STRK, sw=1.2, rx=4))
    frags.append(text(155, 95, "Витік n⁺ (Source)", size=13, color=N_STRK, bold=True))
    frags.append(text(155, 115, "Рівень Фермі E_FS", size=11, color=MUTED))

    frags.append(rect(270, 70, 260, 230, fill=P_SUB, stroke=P_STRK, sw=1.2, rx=4))
    frags.append(text(400, 95, "Канал (p-підкладка, слабка інверсія)", size=13, color=P_STRK, bold=True))
    frags.append(text(400, 115, "Високий бар'єр для електронів", size=11, color=MUTED))

    frags.append(rect(570, 70, 170, 230, fill=N_REG, stroke=N_STRK, sw=1.2, rx=4))
    frags.append(text(655, 95, "Стік n⁺ (Drain)", size=13, color=N_STRK, bold=True))
    frags.append(text(655, 115, "Зміщення E_FD = -q·V_DS", size=11, color=MUTED))

    # Крива 1: V_GS = 0, V_DS = 0 (рівноважний стан, високий бар'єр)
    p1 = "M 90,230 L 230,230 C 260,230 300,140 400,140 C 500,140 540,230 570,230 L 730,230"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (p1, POS))
    frags.append(text(400, 132, "V_GS = 0 В (висота бар'єра q·Φ_B0)", size=11, color=POS, bold=True))

    # Крива 2: V_GS > 0 (але < V_th) — затвор опускає бар'єр по всій ширині
    p2 = "M 90,230 L 230,230 C 260,230 300,175 400,175 C 500,175 540,230 570,230 L 730,230"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5,4"/>' % (p2, FIELD))
    frags.append(text(400, 192, "V_GS > 0 В: бар'єр зменшено на q·Δψ_s -> експоненційне зростання I_sub", size=11, color=FIELD, bold=True))

    # Крива 3: V_GS > 0 та висока V_DS (ефект DIBL — стік опускає правий край і вершину бар'єра)
    p3 = "M 90,230 L 230,230 C 255,230 290,195 370,195 C 450,195 520,280 570,280 L 730,280"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="2,3"/>' % (p3, NEG))
    frags.append(text(540, 225, "DIBL (висока V_DS): стік ще сильніше знижує бар'єр", size=11, color=NEG, bold=True))

    # Електрони, що перелітають (дифундують) через бар'єр завдяки тепловій енергії k_B*T
    for ex in [180, 205, 230]:
        frags.append(circle(ex, 218, 5, fill="#dfe7f0", stroke=NEG, sw=1.4))
        frags.append(text(ex, 222, "−", size=10, color=NEG, bold=True))
    frags.append(arrow(240, 218, 320, 190, color=POS, sw=1.5))
    frags.append(text(285, 175, "Теплова дифузія k_B·T", size=10, color=POS, bold=True))

    render(os.path.join(IMG, "potential-barrier.svg"), w, h, *frags)


def fig_subthreshold_iv_curve():
    """2. Передатна характеристика log(I_D) від V_GS: підпороговий розмах S, DIBL, I_on/I_off."""
    w, h = 840, 400
    frags = []

    frags.append(text(w / 2, 26, "Передатна характеристика MOSFET у логарифмічному масштабі log(I_D) від V_GS", size=15, bold=True))

    # Осі
    frags.append(arrow(110, 340, 110, 45, color=LINE, sw=1.6))
    frags.append(text(105, 42, "Струм стоку I_D (лог. масштаб)", size=12, color=INK, anchor="start", bold=True))

    frags.append(arrow(110, 340, 790, 340, color=LINE, sw=1.6))
    frags.append(text(785, 360, "Напруга затвор-витік V_GS (В)", size=12, color=INK, anchor="end", bold=True))

    # Позначки струму на осі Y
    y_vals = [
        (320, "10⁻¹² А (1 пА)"),
        (265, "10⁻⁹ А (1 нА)"),
        (210, "10⁻⁶ А (1 мкА)"),
        (155, "10⁻³ А (1 мА)"),
        (95, "10⁻¹ А (100 мА)"),
    ]
    for y_pos, label in y_vals:
        frags.append(line(105, y_pos, 115, y_pos, color=LINE, sw=1.2))
        frags.append(line(115, y_pos, 760, y_pos, color="#f0f2f5", sw=1.0, dash="3,3"))
        frags.append(text(100, y_pos + 4, label, size=10, color=MUTED, anchor="end"))

    # Позначки напруги на осі X
    frags.append(line(240, 335, 240, 345, color=LINE, sw=1.4))
    frags.append(text(240, 362, "0 В", size=11, bold=True))

    frags.append(line(480, 335, 480, 345, color=LINE, sw=1.4))
    frags.append(text(480, 362, "V_th (поріг)", size=11, bold=True, color=POS))
    frags.append(line(480, 335, 480, 95, color=POS, sw=1.2, dash="4,4"))

    frags.append(line(710, 335, 710, 345, color=LINE, sw=1.4))
    frags.append(text(710, 362, "V_DD (робоча)", size=11, bold=True))

    # Крива 1: Низька V_DS
    p_low = "M 130,325 L 240,300 L 480,210 C 540,180 610,120 710,95"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (p_low, N_STRK))
    frags.append(text(720, 90, "Низька V_DS (0.05 В)", size=11, color=N_STRK, anchor="start", bold=True))

    # Крива 2: Висока V_DS (DIBL)
    p_high = "M 130,305 L 240,265 L 440,195 C 510,165 590,110 710,80"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="5,4"/>' % (p_high, WARN_BD))
    frags.append(text(720, 75, "Висока V_DS = V_DD (DIBL)", size=11, color=WARN_BD, anchor="start", bold=True))

    # Підпороговий розмах S (трикутник нахилу винесено вільніше)
    frags.append(line(310, 275, 370, 275, color=POS, sw=1.6))
    frags.append(line(370, 275, 370, 250, color=POS, sw=1.6))
    frags.append(text(340, 292, "ΔV_GS = S", size=10, color=POS, bold=True))
    frags.append(text(380, 260, "Δ(log I_D) = 1 дек", size=10, color=POS, bold=True, anchor="start"))

    # I_off і I_on позначки
    frags.append(circle(240, 300, 4, fill=N_STRK, stroke=LINE, sw=1.2))
    frags.append(text(230, 310, "I_off (low V_DS)", size=10, color=N_STRK, anchor="end"))

    frags.append(circle(240, 265, 4, fill=WARN_BD, stroke=LINE, sw=1.2))
    frags.append(text(230, 258, "I_off (DIBL)", size=10, color=WARN_BD, anchor="end", bold=True))

    frags.append(circle(710, 80, 4, fill=FIELD, stroke=LINE, sw=1.2))
    frags.append(text(675, 115, "I_on (робочий струм)", size=11, color=FIELD, bold=True))

    # Текстова плашка праворуч внизу
    tb, _, _ = textbox(570, 275, "Область слабкої інверсії (підпорогова):\n• Струм зростає експоненційно: I_sub ∝ 10^(V_GS / S)\n• S_ideal = ln(10)·k_B·T / q ≈ 60 мВ/декаду (при 300 К)\n• У реальних чіпах S ≈ 70–90 мВ/декаду", size=11, pad=8, fill=FILL, stroke=MUTED)
    frags.append(tb)

    render(os.path.join(IMG, "subthreshold-iv-curve.svg"), w, h, *frags)


def fig_leakage_mechanisms():
    """3. Чотири фізичні канали статичного витоку в польовому транзисторі нанорозмірів."""
    w, h = 860, 450
    frags = []

    frags.append(text(w / 2, 26, "Чотири фізичні канали статичного струму витоку в нанорозмірному MOSFET", size=15, bold=True))

    # Транзисторний розріз
    bx, by, bw, bh = 60, 90, 740, 230
    # Тіло p-підкладки
    frags.append(rect(bx, by, bw, bh, fill=P_SUB, stroke=P_STRK, sw=1.8, rx=0))
    frags.append(text(bx + bw / 2, by + bh - 15, "p-підкладка / p-well (тіло транзистора, Body, потенціал V_B)", size=12, color=P_STRK, bold=True))

    # n+ витік (Source)
    sw_w = 160
    frags.append(rect(bx, by, sw_w, 95, fill=N_REG, stroke=N_STRK, sw=1.5, rx=0))
    frags.append(text(bx + sw_w / 2, by + 40, "Витік n⁺ (Source)", size=13, color=N_STRK, bold=True))
    frags.append(text(bx + sw_w / 2, by + 60, "V_S = 0 В", size=11, color=MUTED))

    # n+ стік (Drain)
    frags.append(rect(bx + bw - sw_w, by, sw_w, 95, fill=N_REG, stroke=N_STRK, sw=1.5, rx=0))
    frags.append(text(bx + bw - sw_w / 2, by + 40, "Стік n⁺ (Drain)", size=13, color=N_STRK, bold=True))
    frags.append(text(bx + bw - sw_w / 2, by + 60, "V_D = V_DD", size=11, color=MUTED))

    # Збіднена область довкола каналу
    frags.append(rect(bx + sw_w, by + 10, 420, 85, fill=DEP_FIL, stroke=DEP_STR, sw=1.2, rx=0))
    frags.append(text(bx + bw / 2, by + 65, "Збіднена область під затвором", size=11, color=DEP_STR, italic=True))

    # Тонкий діелектрик затвора (оксид)
    ox_w = 440
    ox_x = bx + (bw - ox_w) / 2
    frags.append(rect(ox_x, by - 16, ox_w, 16, fill=OX_FILL, stroke=OX_STRK, sw=1.5, rx=0))
    frags.append(text(bx + bw / 2, by - 5, "Підзатворний діелектрик (High-k / SiO₂)", size=10, color=OX_STRK, bold=True))

    # Металевий затвор (Gate)
    frags.append(rect(ox_x, by - 48, ox_w, 32, fill=GT_FILL, stroke=GT_STRK, sw=1.6, rx=3))
    frags.append(text(bx + bw / 2, by - 28, "Затвор (Gate, V_G = 0 В у вимкненому стані)", size=12, color=GT_STRK, bold=True))

    # 1. Підпороговий витік (I_sub) - пряма стрілка в каналі
    frags.append(arrow(bx + sw_w - 10, by + 28, bx + bw - sw_w + 10, by + 28, color=POS, sw=2.8))
    tb1, _, _ = textbox(bx + bw / 2, by + 30, "1. Підпороговий струм I_sub (дифузія витік -> стік)", size=10, pad=4, fill="#fff", stroke=POS, bold=True)
    frags.append(tb1)

    # 2. Витік крізь діелектрик затвора (I_gate)
    frags.append(arrow(ox_x + 90, by - 30, ox_x + 90, by + 8, color="#d97706", sw=2.0))
    tb2, _, _ = textbox(ox_x + 90, by - 65, "2. Тунелювання затвора I_gate", size=10, pad=4, fill="#fff", stroke="#d97706", bold=True)
    frags.append(tb2)

    # 3. Зворотний витік p-n переходу стік-підкладка (I_rev)
    frags.append(arrow(bx + bw - sw_w / 2, by + 85, bx + bw - sw_w / 2, by + 140, color="#7c3aed", sw=2.0))
    tb3, _, _ = textbox(680, by + 165, "3. Зворотний витік переходу I_rev", size=10, pad=4, fill="#fff", stroke="#7c3aed", bold=True)
    frags.append(tb3)

    # 4. Струм GIDL (Gate-Induced Drain Leakage) у зоні перекриття затвор-стік
    frags.append(arrow(ox_x + ox_w - 20, by + 5, ox_x + ox_w - 50, by + 85, color="#0284c7", sw=2.0))
    tb4, _, _ = textbox(ox_x + ox_w - 140, by + 115, "4. Витік GIDL (BTBT тунелювання)", size=10, pad=4, fill="#fff", stroke="#0284c7", bold=True)
    frags.append(tb4)

    # Підсумкова плашка
    frags.append(rect(40, 340, 780, 85, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(430, 362, "Повний статичний витік транзистора: I_leak = I_sub + I_gate + I_rev + I_GIDL", size=12, bold=True))
    frags.append(text(430, 384, "• При V_GS = 0 В головним джерелом є I_sub (дифузія неосновних носіїв над бар'єром)", size=11, color=MUTED))
    frags.append(text(430, 404, "• Зі зростанням V_DS посилюються DIBL та GIDL; при тонких діелектриках (<1.5 нм) зростає I_gate", size=11, color=MUTED))

    render(os.path.join(IMG, "leakage-mechanisms.svg"), w, h, *frags)


def fig_multi_vt_tradeoff():
    """4. Багатопорогові бібліотеки Multi-Vt: компроміс швидкодії (затримки) та струму витоку."""
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 26, "Стратегія Multi-V_th: розподіл транзисторів LVT, SVT та HVT у схемі", size=15, bold=True))

    # Ліва панель: графік залежності затримки та витоку від V_th
    frags.append(rect(40, 55, 340, 280, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(210, 80, "Компроміс затримка ↔ витік", size=13, bold=True))

    # Осі графіка
    frags.append(arrow(70, 290, 70, 105, color=LINE, sw=1.4))
    frags.append(text(65, 100, "Струм витоку I_leak (лог.)", size=10, bold=True, anchor="start", color=POS))
    frags.append(arrow(70, 290, 350, 290, color=LINE, sw=1.4))
    frags.append(text(345, 305, "Порогова напруга V_th", size=10, bold=True, anchor="end"))

    # Крива витоку (падає з ростом V_th)
    p_leak = "M 80,120 C 130,130 180,210 330,275"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (p_leak, POS))
    frags.append(text(140, 150, "I_leak (експонента)", size=10, color=POS, bold=True))

    # Крива затримки (зростає з ростом V_th)
    p_delay = "M 80,270 C 180,260 260,200 330,125"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="4,3"/>' % (p_delay, NEG))
    frags.append(text(280, 160, "Затримка t_pd", size=10, color=NEG, bold=True))

    # Три точки LVT, SVT, HVT
    frags.append(circle(115, 135, 5, fill=POS, stroke=LINE, sw=1.2))
    frags.append(text(115, 120, "LVT", size=10, bold=True, color=POS))

    frags.append(circle(200, 215, 5, fill=FIELD, stroke=LINE, sw=1.2))
    frags.append(text(200, 205, "SVT", size=10, bold=True, color=FIELD))

    frags.append(circle(295, 265, 5, fill=NEG, stroke=LINE, sw=1.2))
    frags.append(text(295, 255, "HVT", size=10, bold=True, color=NEG))

    # Права панель: логічні шляхи (критичний і некритичний)
    frags.append(rect(400, 55, 380, 280, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(590, 80, "Оптимізація таймінгу синтезатором (EDA)", size=13, bold=True))

    # Критичний шлях (LVT)
    frags.append(rect(420, 105, 340, 95, fill=WARN_BG, stroke=WARN_BD, sw=1.4, rx=4))
    frags.append(text(590, 125, "Критичний шлях (Critical Timing Path: ~5–15% комірок)", size=11, bold=True, color=WARN_BD))
    frags.append(textbox(470, 160, "LVT вентиль\n(мала затримка)", size=10, pad=4, fill="#fff", stroke=WARN_BD)[0])
    frags.append(arrow(515, 160, 545, 160, color=WARN_BD, sw=1.8))
    frags.append(textbox(590, 160, "LVT вентиль\n(максимум I_on)", size=10, pad=4, fill="#fff", stroke=WARN_BD)[0])
    frags.append(arrow(635, 160, 665, 160, color=WARN_BD, sw=1.8))
    frags.append(textbox(710, 160, "Тригер\n(Setup OK)", size=10, pad=4, fill="#fff", stroke=WARN_BD)[0])

    # Некритичний шлях (HVT)
    frags.append(rect(420, 220, 340, 95, fill=OK_BG, stroke=OK_BD, sw=1.4, rx=4))
    frags.append(text(590, 240, "Некритичні шляхи (Slack > 0: ~85–95% комірок чіпа)", size=11, bold=True, color=OK_BD))
    frags.append(textbox(470, 275, "HVT вентиль\n(витік ×0.05)", size=10, pad=4, fill="#fff", stroke=OK_BD)[0])
    frags.append(arrow(515, 275, 545, 275, color=OK_BD, sw=1.8))
    frags.append(textbox(590, 275, "HVT вентиль\n(економія енергії)", size=10, pad=4, fill="#fff", stroke=OK_BD)[0])
    frags.append(arrow(635, 275, 665, 275, color=OK_BD, sw=1.8))
    frags.append(textbox(710, 275, "Тригер\n(Запас часу)", size=10, pad=4, fill="#fff", stroke=OK_BD)[0])

    render(os.path.join(IMG, "multi-vt-tradeoff.svg"), w, h, *frags)


def fig_body_bias_schemes():
    """5. Адаптивне зміщення підкладки (ABB): пряме (FBB) та зворотне (RBB) зміщення."""
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 26, "Адаптивне керування порогом через зміщення підкладки (Body Biasing)", size=15, bold=True))

    # Блок 1: RBB (Зворотне зміщення)
    frags.append(rect(40, 60, 230, 260, fill="#edf2f7", stroke="#4a5568", sw=1.4, rx=6))
    frags.append(text(155, 85, "RBB: Зворотне зміщення", size=13, bold=True, color="#2b6cb0"))
    frags.append(text(155, 105, "Режим спокою (Standby / Sleep)", size=11, color=MUTED))

    frags.append(rect(60, 125, 190, 70, fill="#fff", stroke="#cbd5e0", sw=1.2, rx=4))
    frags.append(text(155, 148, "V_BS < 0 В (V_B = −0.5 В)", size=11, bold=True, color=POS))
    frags.append(text(155, 172, "Збіднена зона розширюється", size=10, color=MUTED))

    frags.append(textbox(155, 245, "Наслідки RBB:\n• Порогова напруга V_th зростає\n• Підпороговий витік падає в 5–20×\n• Заморожування витоку в сні", size=11, pad=6, fill=OK_BG, stroke=OK_BD)[0])

    # Блок 2: Незміщене тіло (Zero Body Bias - ZBB)
    frags.append(rect(295, 60, 230, 260, fill="#f7fafc", stroke="#a0aec0", sw=1.4, rx=6))
    frags.append(text(410, 85, "ZBB: Нульове зміщення", size=13, bold=True, color=INK))
    frags.append(text(410, 105, "Номінальний режим (Active)", size=11, color=MUTED))

    frags.append(rect(315, 125, 190, 70, fill="#fff", stroke="#cbd5e0", sw=1.2, rx=4))
    frags.append(text(410, 148, "V_BS = 0 В (Підкладка = GND)", size=11, bold=True))
    frags.append(text(410, 172, "Стандартна ширина збіднення", size=10, color=MUTED))

    frags.append(textbox(410, 245, "Номінальний стан:\n• Стандартний V_th = V_th0\n• Номінальний струм I_on\n• Базовий баланс швидкість/витік", size=11, pad=6, fill="#fff", stroke=MUTED)[0])

    # Блок 3: FBB (Пряме зміщення)
    frags.append(rect(550, 60, 230, 260, fill="#fff5f5", stroke="#e53e3e", sw=1.4, rx=6))
    frags.append(text(665, 85, "FBB: Пряме зміщення", size=13, bold=True, color=WARN_BD))
    frags.append(text(665, 105, "Турбо-режим / High Performance", size=11, color=MUTED))

    frags.append(rect(570, 125, 190, 70, fill="#fff", stroke="#cbd5e0", sw=1.2, rx=4))
    frags.append(text(665, 148, "0 < V_BS < +0.4 В", size=11, bold=True, color=FIELD))
    frags.append(text(665, 172, "Збіднена зона звужується", size=10, color=MUTED))

    frags.append(textbox(665, 245, "Наслідки FBB:\n• Порогова напруга V_th падає\n• Струм I_on зростає на 15–30%\n• Прискорення критичних блоків", size=11, pad=6, fill=WARN_BG, stroke=WARN_BD)[0])

    render(os.path.join(IMG, "body-bias-schemes.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_potential_barrier()
    fig_subthreshold_iv_curve()
    fig_leakage_mechanisms()
    fig_multi_vt_tradeoff()
    fig_body_bias_schemes()
    print("All figures generated successfully.")
