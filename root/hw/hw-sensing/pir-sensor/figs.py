# -*- coding: utf-8 -*-
"""Фігури до теми «PIR: рух як зміна тепла».
Запуск:  python figs.py   → пише SVG у ./img/
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
COLOR_AMBER = "#f39c12"


# ── Фігура 1: Двоелементна диференціальна топологія ──────────────────────────
def fig_pyroelectric_crystal_differential():
    W, H = 840, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Диференціальна топологія двоелементного PIR-детектора", size=16, bold=True))

    # Ліва частина: Структура сенсора в корпусі TO-5
    box_l, _, _ = textbox(240, 70, "Внутрішня структура датчика (корпус TO-5 з ІЧ-фільтром)", size=13, bold=True, fill="#eef4fa", stroke="#bcd0e6")
    f.append(box_l)

    # Корпус детектора
    f.append(rect(40, 95, 400, 300, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    f.append(text(240, 115, "Оптичне вхідне вікно (фільтр 8–14 мкм)", size=11, bold=True, color=COLOR_BLUE))
    f.append(rect(100, 122, 280, 8, fill="#aed6f1", stroke="#5dade2", sw=1.2, rx=2))

    # Промені ІЧ-випромінювання на елемент 1
    f.append(arrow(170, 60, 170, 120, color=COLOR_RED, sw=1.8))
    f.append(arrow(190, 60, 190, 120, color=COLOR_RED, sw=1.8))
    f.append(text(180, 52, "ІЧ-промінь", size=10, bold=True, color=COLOR_RED))

    # Піроелемент 1 (активний, нагрівається)
    f.append(rect(140, 150, 80, 50, fill="#fadbd8", stroke=COLOR_RED, sw=1.8, rx=4))
    f.append(text(180, 170, "Елемент A", size=12, bold=True, color=COLOR_RED))
    f.append(text(180, 188, "(+ заряд)", size=11, color=COLOR_RED))

    # Піроелемент 2 (холодний/компенсаційний)
    f.append(rect(260, 150, 80, 50, fill="#d6eaf8", stroke=COLOR_BLUE, sw=1.8, rx=4))
    f.append(text(300, 170, "Елемент B", size=12, bold=True, color=COLOR_BLUE))
    f.append(text(300, 188, "(- заряд)", size=11, color=COLOR_BLUE))

    # З'єднання елементів (зустрічно-послідовне)
    f.append(line(180, 200, 180, 230, color=LINE, sw=1.5))
    f.append(line(300, 200, 300, 230, color=LINE, sw=1.5))
    f.append(line(180, 230, 300, 230, color=LINE, sw=1.5))
    f.append(text(240, 222, "Зустрічне з'єднання (протифаза)", size=10, italic=True, color=MUTED))

    # Лінія до затвора JFET
    f.append(line(140, 175, 100, 175, color=LINE, sw=1.5))
    f.append(line(100, 175, 100, 270, color=LINE, sw=1.5))
    f.append(line(100, 270, 180, 270, color=LINE, sw=1.5))

    # Гігаомний резистор Rg
    f.append(line(120, 270, 120, 300, color=LINE, sw=1.5))
    f.append(rect(108, 300, 24, 45, fill="#fcf3cf", stroke="#f39c12", sw=1.4, rx=2))
    f.append(text(120, 326, "Rg", size=10, bold=True, color=COLOR_ORANGE))
    f.append(line(120, 345, 120, 370, color=LINE, sw=1.5))
    f.append(line(110, 370, 130, 370, color=LINE, sw=2))
    f.append(text(75, 330, "10-100 ГОм", size=9, color=MUTED))

    # JFET-транзистор
    f.append(circle(210, 285, 25, fill="#f4f6f8", stroke=LINE, sw=1.6))
    f.append(line(195, 270, 195, 300, color=LINE, sw=2.5))
    f.append(line(180, 270, 195, 270, color=LINE, sw=1.5))
    f.append(text(187, 263, "G", size=10, bold=True))
    f.append(line(195, 275, 225, 275, color=LINE, sw=1.5))
    f.append(line(225, 275, 225, 250, color=LINE, sw=1.5))
    f.append(line(225, 250, 380, 250, color=LINE, sw=1.5))
    f.append(circle(380, 250, 4, fill=LINE, stroke=LINE))
    f.append(text(410, 254, "VDD", size=11, bold=True, color=COLOR_RED))

    f.append(line(195, 295, 225, 295, color=LINE, sw=1.5))
    f.append(arrow(210, 295, 222, 295, color=LINE, sw=1.5))
    f.append(line(225, 295, 225, 350, color=LINE, sw=1.5))
    f.append(line(225, 350, 380, 350, color=LINE, sw=1.5))
    f.append(circle(380, 350, 4, fill=LINE, stroke=LINE))
    f.append(text(415, 354, "OUT", size=11, bold=True, color=COLOR_BLUE))
    f.append(text(215, 315, "JFET", size=10, color=MUTED))

    # Права частина: Порівняння відгуків
    box_r, _, _ = textbox(640, 70, "Принцип диференціального відсікання завад", size=13, bold=True, fill="#fef9e7", stroke="#f9e79f")
    f.append(box_r)

    # Випадок 1: Загальний нагрів (сонце, протяг)
    f.append(rect(480, 95, 320, 135, fill="#f9f9f9", stroke="#d5dbdb", sw=1.2, rx=6))
    f.append(text(640, 115, "Синфазна дія (фонове нагрівання)", size=11, bold=True, color=COLOR_ORANGE))
    f.append(text(640, 135, "dT1/dt = dT2/dt  (обидва кристали теплішають)", size=10))
    f.append(text(640, 155, "q1(t) = +q0,   q2(t) = -q0", size=11, color=COLOR_BLUE))
    f.append(line(520, 175, 760, 175, color="#bdc3c7", sw=1, dash="3,3"))
    f.append(line(520, 175, 760, 175, color=COLOR_GREEN, sw=2))
    f.append(text(640, 195, "i_total = i1 - i2 = 0  →  СИГНАЛУ НЕМАЄ", size=11, bold=True, color=COLOR_GREEN))
    f.append(text(640, 215, "Придушення фонового тепла (CMRR ~ 50 дБ)", size=10, italic=True, color=MUTED))

    # Випадок 2: Рух людини
    f.append(rect(480, 250, 320, 145, fill="#f9f9f9", stroke="#d5dbdb", sw=1.2, rx=6))
    f.append(text(640, 270, "Диференціальна дія (перетин променя)", size=11, bold=True, color=COLOR_RED))
    f.append(text(640, 290, "Людина нагріває спершу A, потім B", size=10))
    f.append(line(510, 335, 770, 335, color="#bdc3c7", sw=1, dash="3,3"))
    wave_path = "M 520 335 C 550 295, 570 295, 600 335 C 630 375, 650 375, 680 335 L 760 335"
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (wave_path, COLOR_PURPLE))
    f.append(text(600, 310, "+Vmax", size=10, bold=True, color=COLOR_RED))
    f.append(text(640, 370, "-Vmax", size=10, bold=True, color=COLOR_BLUE))
    f.append(text(640, 385, "Двополярний хвильовий сплеск (0.5–5 Гц)", size=10, bold=True, color=COLOR_PURPLE))

    return render(os.path.join(IMG, 'pyroelectric-crystal-differential.svg'), W, H, *f)


# ── Фігура 2: Оптика масиву лінз Френеля ─────────────────────────────────────
def fig_fresnel_lens_zones():
    W, H = 840, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Просторове чергування зон чутливості масивом лінз Френеля", size=16, bold=True))

    # Сенсор зліва
    f.append(rect(30, 160, 45, 90, fill="#2c3e50", stroke=LINE, sw=1.5, rx=4))
    f.append(text(52, 200, "PIR", size=12, bold=True, color="#ffffff"))
    f.append(text(52, 218, "Сенсор", size=10, color="#ecf0f1"))

    # Баня лінзи Френеля (сегментована)
    f.append(rect(80, 130, 20, 150, fill="#ebf5fb", stroke="#3498db", sw=1.8, rx=6))
    f.append(text(90, 115, "Лінза", size=11, bold=True, color=COLOR_BLUE))
    f.append(text(90, 300, "Френеля", size=11, bold=True, color=COLOR_BLUE))

    # Сектори/промені огляду
    # Фасетка 1 (верхня)
    f.append('<polygon points="100,165 520,60 520,105 100,175" fill="#e74c3c" fill-opacity="0.18" stroke="#c0392b" stroke-width="1.2"/>')
    f.append('<polygon points="100,175 520,110 520,155 100,185" fill="#3498db" fill-opacity="0.18" stroke="#2980b9" stroke-width="1.2"/>')

    # Фасетка 2 (центральна)
    f.append('<polygon points="100,195 520,175 520,220 100,205" fill="#e74c3c" fill-opacity="0.22" stroke="#c0392b" stroke-width="1.2"/>')
    f.append('<polygon points="100,205 520,225 520,270 100,215" fill="#3498db" fill-opacity="0.22" stroke="#2980b9" stroke-width="1.2"/>')

    # Фасетка 3 (нижня)
    f.append('<polygon points="100,225 520,290 520,335 100,235" fill="#e74c3c" fill-opacity="0.18" stroke="#c0392b" stroke-width="1.2"/>')
    f.append('<polygon points="100,235 520,340 520,385 100,245" fill="#3498db" fill-opacity="0.18" stroke="#2980b9" stroke-width="1.2"/>')

    # Позначення променів A та B
    f.append(text(460, 192, "Промінь A (+)", size=11, bold=True, color=COLOR_RED))
    f.append(text(460, 252, "Промінь B (-)", size=11, bold=True, color=COLOR_BLUE))

    # Людина, що йде поперек променів
    f.append(line(560, 70, 560, 380, color=COLOR_GREEN, sw=2, dash="5,4"))
    f.append(arrow(560, 70, 560, 375, color=COLOR_GREEN, sw=2.2))
    f.append(text(560, 55, "Траєкторія руху об'єкта (людини)", size=12, bold=True, color=COLOR_GREEN))

    # Фігурка людини
    f.append(circle(560, 195, 9, fill="#f39c12", stroke="#d35400", sw=1.5))
    f.append(line(560, 204, 560, 230, color="#d35400", sw=2))
    f.append(line(548, 215, 572, 215, color="#d35400", sw=1.8))
    f.append(line(560, 230, 550, 250, color="#d35400", sw=1.8))
    f.append(line(560, 230, 570, 250, color="#d35400", sw=1.8))
    f.append(text(595, 210, "Людина", size=11, bold=True, color=COLOR_ORANGE))
    f.append(text(605, 226, "(T ~ 34°C)", size=10, color=MUTED))

    # Права панель: часові графіки переходу
    f.append(rect(650, 60, 175, 340, fill="#f8f9fa", stroke="#dcdde1", sw=1.2, rx=6))
    f.append(text(737, 80, "Хронограма сигналів", size=12, bold=True, color=INK))

    # Графік 1: Тепловий потік на кристал A
    f.append(text(737, 108, "Тепловий потік Φ_A(t)", size=10, bold=True, color=COLOR_RED))
    f.append(line(665, 145, 810, 145, color="#bdc3c7", sw=1))
    f.append('<path d="M 670 145 Q 710 105, 730 145 L 805 145" fill="none" stroke="%s" stroke-width="1.8"/>' % COLOR_RED)

    # Графік 2: Тепловий потік на кристал B
    f.append(text(737, 178, "Тепловий потік Φ_B(t)", size=10, bold=True, color=COLOR_BLUE))
    f.append(line(665, 215, 810, 215, color="#bdc3c7", sw=1))
    f.append('<path d="M 670 215 L 730 215 Q 755 175, 775 215 L 805 215" fill="none" stroke="%s" stroke-width="1.8"/>' % COLOR_BLUE)

    # Графік 3: Вихідна диференціальна напруга V(t)
    f.append(text(737, 250, "Вихідна напруга V_out(t)", size=10, bold=True, color=COLOR_PURPLE))
    f.append(line(665, 310, 810, 310, color="#bdc3c7", sw=1, dash="3,3"))
    f.append('<path d="M 670 310 Q 700 270, 725 310 Q 755 350, 785 310 L 805 310" fill="none" stroke="%s" stroke-width="2.2"/>' % COLOR_PURPLE)
    f.append(text(705, 282, "+V", size=9, bold=True, color=COLOR_RED))
    f.append(text(765, 340, "-V", size=9, bold=True, color=COLOR_BLUE))
    f.append(text(737, 375, "f = v / (d_променя)", size=10, italic=True, color=MUTED))
    f.append(text(737, 390, "Типово 0.5–5 Гц", size=10, bold=True, color=COLOR_GREEN))

    return render(os.path.join(IMG, 'fresnel-lens-zones.svg'), W, H, *f)


# ── Фігура 3: Аналоговий тракт підсилення та компаратора ──────────────────────
def fig_analog_signal_chain():
    W, H = 840, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Структурна схема аналогового тракту обробки PIR-сигналу (BISS0001)", size=16, bold=True))

    # Блок 1: Сенсор
    b1, _, _ = textbox(90, 110, "PIR Сенсор\n(LiTaO3 + JFET)\n~ 1 мВ амплітуда", size=11, pad=8, fill="#fadbd8", stroke=COLOR_RED, sw=1.5)
    f.append(b1)

    f.append(arrow(155, 110, 195, 110, color=LINE, sw=1.8))
    f.append(text(175, 98, "Vin", size=10, bold=True, color=MUTED))

    # Блок 2: 1-й каскад активного смугового фільтра
    b2, _, _ = textbox(280, 110, "1-й каскад ОП (OP1)\nСмуговий фільтр\n0.3–7 Гц, K1 ≈ 40 дБ", size=11, pad=8, fill="#ebf5fb", stroke=COLOR_BLUE, sw=1.5)
    f.append(b2)

    f.append(arrow(365, 110, 405, 110, color=LINE, sw=1.8))
    f.append(text(385, 98, "~100 мВ", size=10, color=MUTED))

    # Блок 3: 2-й каскад підсилювача
    b3, _, _ = textbox(490, 110, "2-й каскад ОП (OP2)\nПідсилювач напруги\nK2 ≈ 30 дБ (ΣK ≈ 70 дБ)", size=11, pad=8, fill="#e8f8f5", stroke=COLOR_GREEN, sw=1.5)
    f.append(b3)

    f.append(arrow(575, 110, 615, 110, color=LINE, sw=1.8))
    f.append(text(595, 98, "1–3 В", size=10, bold=True, color=COLOR_RED))

    # Блок 4: Двопороговий віконний компаратор
    b4, _, _ = textbox(715, 110, "Віконний компаратор\nПоріг ВЕРХ: Vref + Vth\nПоріг НИЗ:  Vref - Vth", size=11, pad=8, fill="#fef9e7", stroke=COLOR_ORANGE, sw=1.5)
    f.append(b4)

    # З'єднання вниз до цифрової частини
    f.append(arrow(715, 160, 715, 210, color=LINE, sw=1.8))
    f.append(text(745, 185, "Імпульси", size=10, bold=True, color=COLOR_PURPLE))

    # Блок 5: Логіка таймера, блокування та антибрязку
    b5, _, _ = textbox(490, 255, "Цифровий контролер / Таймер затримки BISS0001\n• Перезапускний режим (Retriggerable / Non-retriggerable)\n• Таймер вихідного імпульсу Tx (1–10 с)\n• Таймер блокування повторного спрацьовування Ti (0.5–2 с)", size=11, pad=10, fill="#f4ecf7", stroke=COLOR_PURPLE, sw=1.5)
    f.append(b5)

    f.append(line(715, 255, 680, 255, color=LINE, sw=1.8))

    # Вихідний сигнал OUT
    f.append(arrow(300, 255, 140, 255, color=COLOR_GREEN, sw=2.2))
    b_out, _, _ = textbox(75, 255, "ВИХІД OUT\n(3.3 В / 5 В TTL)", size=12, bold=True, pad=8, fill="#d4efdf", stroke=COLOR_GREEN, sw=2)
    f.append(b_out)

    # Пояснювальний блок знизу
    f.append(text(W / 2, 335, "Фільтр відсікає постійний тепловий дрейф (< 0.3 Гц) та мережеві наведення 50/60 Гц (> 7 Гц)", size=11, italic=True, color=MUTED))

    return render(os.path.join(IMG, 'analog-signal-chain.svg'), W, H, *f)


# ── Фігура 4: DSP та розпізнавання форми хвилі ───────────────────────────────
def fig_pir_wave_dsp_fsm():
    W, H = 840, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Алгоритм розпізнавання хвильового патерну та автомат станів (FSM)", size=16, bold=True))

    # Ліва частина: Сигнали (рух проти завад)
    f.append(rect(40, 55, 380, 325, fill="#fcfcfc", stroke="#dcdde1", sw=1.2, rx=6))
    f.append(text(230, 75, "Аналіз сигналу PIR у часі", size=13, bold=True, color=INK))

    # Графік 1: Справжній рух (валідна хвиля)
    f.append(text(140, 102, "1. Справжній рух людини (валідна пара)", size=10, bold=True, color=COLOR_GREEN))
    f.append(line(55, 150, 395, 150, color="#bdc3c7", sw=1, dash="3,3"))
    f.append(line(55, 125, 395, 125, color=COLOR_RED, sw=1, dash="2,2"))
    f.append(line(55, 175, 395, 175, color=COLOR_BLUE, sw=1, dash="2,2"))
    f.append(text(405, 125, "+Vth", size=9, color=COLOR_RED))
    f.append(text(405, 175, "-Vth", size=9, color=COLOR_BLUE))

    # Хвиля
    wave_valid = "M 60 150 L 100 150 Q 130 95, 160 150 Q 190 205, 220 150 L 260 150 L 390 150"
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (wave_valid, COLOR_PURPLE))
    f.append(circle(145, 110, 4, fill=COLOR_RED, stroke=COLOR_RED))
    f.append(text(145, 95, "Пік 1", size=9, bold=True, color=COLOR_RED))
    f.append(circle(205, 190, 4, fill=COLOR_BLUE, stroke=COLOR_BLUE))
    f.append(text(205, 210, "Пік 2", size=9, bold=True, color=COLOR_BLUE))
    f.append(text(290, 138, "Перехід 0", size=9, bold=True, color=COLOR_GREEN))
    f.append(line(175, 135, 175, 165, color=COLOR_GREEN, sw=1.5))

    # Графік 2: Одиночний імпульс (завада від реле/клацання)
    f.append(text(140, 235, "2. Одиночна завада (іскра / спалах світла)", size=10, bold=True, color=COLOR_ORANGE))
    f.append(line(55, 280, 395, 280, color="#bdc3c7", sw=1, dash="3,3"))
    f.append(line(55, 258, 395, 258, color=COLOR_RED, sw=1, dash="2,2"))
    f.append(line(55, 302, 395, 302, color=COLOR_BLUE, sw=1, dash="2,2"))

    spike_noise = "M 60 280 L 120 280 L 135 245 L 150 280 L 390 280"
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (spike_noise, COLOR_ORANGE))
    f.append(text(230, 255, "Немає від'ємного піку → ВІДХИЛЕНО", size=10, bold=True, color=COLOR_RED))
    f.append(text(230, 350, "FSM фільтрує до 98% хибних спрацьовувань", size=10, italic=True, color=MUTED))

    # Права частина: Скінченний автомат розпізнавання FSM
    f.append(rect(440, 55, 360, 325, fill="#fcfcfc", stroke="#dcdde1", sw=1.2, rx=6))
    f.append(text(620, 75, "Автомат станів (FSM DSP)", size=13, bold=True, color=INK))

    # Стан 1: IDLE
    b_idle, _, _ = textbox(620, 115, "IDLE (Очікування спокою)\n|V - V_baseline| < V_th", size=10, pad=6, fill="#f4f6f8", stroke=LINE, sw=1.4)
    f.append(b_idle)

    # Перехід до піку
    f.append(arrow(620, 140, 620, 175, color=COLOR_RED, sw=1.8))
    f.append(text(710, 158, "Перевищено +Vth", size=9, bold=True, color=COLOR_RED))

    # Стан 2: FIRST_PEAK
    b_peak1, _, _ = textbox(620, 200, "FIRST_PEAK_DETECTED\nЗапуск таймера вікна T_win (0.2–1.5 с)", size=10, pad=6, fill="#fadbd8", stroke=COLOR_RED, sw=1.4)
    f.append(b_peak1)

    # Перехід до другого піку
    f.append(arrow(620, 225, 620, 260, color=COLOR_BLUE, sw=1.8))
    f.append(text(725, 243, "Перетин 0 та спад нижче -Vth", size=9, bold=True, color=COLOR_BLUE))

    # Стан 3: CONFIRMED
    b_conf, _, _ = textbox(620, 290, "MOTION_CONFIRMED (Рух підтверджено)\nГенерація вихідного сигналу / події", size=10, pad=6, fill="#d4efdf", stroke=COLOR_GREEN, sw=1.8)
    f.append(b_conf)

    # Таймаут скидання
    f.append('<path d="M 520 200 C 470 200, 470 115, 530 115" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="3,3" marker-end="url(#arrow)"/>' % COLOR_ORANGE)
    f.append(text(465, 160, "Таймаут T_win", size=9, color=COLOR_ORANGE))

    # Скидання після підтвердження
    f.append('<path d="M 720 290 C 785 290, 785 115, 715 115" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="3,3" marker-end="url(#arrow)"/>' % COLOR_GREEN)
    f.append(text(785, 200, "Завершення події", size=9, color=COLOR_GREEN))

    return render(os.path.join(IMG, 'pir-wave-dsp-fsm.svg'), W, H, *f)


if __name__ == "__main__":
    fig_pyroelectric_crystal_differential()
    fig_fresnel_lens_zones()
    fig_analog_signal_chain()
    fig_pir_wave_dsp_fsm()
    print("All figures generated successfully.")
