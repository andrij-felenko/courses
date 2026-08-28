# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Порівняння програмного Failsafe та апаратного FTS Kill-Switch ───
def fig_software_vs_hardware_kill():
    W, H = 820, 480
    frags = []
    frags.append(text(W / 2, 28, "Програмний Failsafe проти апаратного Flight Termination System (FTS)",
                      size=15, bold=True))

    # Верхній контур: Програмний Failsafe (вразливий до зависань)
    frags.append(rect(20, 60, 780, 185, fill="#fdf2f0", stroke=POS, sw=1.8))
    frags.append(text(40, 85, "Програмний ланцюг Failsafe / Disarm (залежний від CPU та RTOS)", size=13, bold=True, color=POS, anchor="start"))

    b_w, b_h = 130, 70
    y_top = 110
    frags.append(fitbox(40, y_top, b_w, b_h, "RC-приймач\n(CRSF / SBUS)\n\nПакет керування", size=11, fill="#ffffff", stroke=LINE))
    frags.append(arrow(170, y_top + 35, 200, y_top + 35, color=LINE, sw=1.5))

    frags.append(fitbox(200, y_top, b_w, b_h, "UART-драйвер\nта черга RTOS\n\nОбробка байтів", size=11, fill="#ffffff", stroke=LINE))
    frags.append(arrow(330, y_top + 35, 360, y_top + 35, color=LINE, sw=1.5))

    frags.append(fitbox(360, y_top, b_w, b_h, "Ядро CPU\n(Автопілот / PID)\n\n[УРАЗЛИВЕ ДО ЗБОЮ]", size=11, fill="#feebe8", stroke=POS, bold=True))
    frags.append(arrow(490, y_top + 35, 520, y_top + 35, color=LINE, sw=1.5))

    frags.append(fitbox(520, y_top, b_w, b_h, "Таймер ШІМ / DMA\n(TIMx / DShot)\n\nГенерація імпульсів", size=11, fill="#ffffff", stroke=LINE))
    frags.append(arrow(650, y_top + 35, 680, y_top + 35, color=LINE, sw=1.5))

    frags.append(fitbox(680, y_top, 100, b_h, "Регулятори\nESC та BLDC\nдвигуни", size=11, fill="#ffffff", stroke=LINE))

    frags.append(text(410, y_top + 95, "Точка відмови: при HardFault, зацикленні або блокуванні RTOS таймер продовжує видавати останній ШІМ!", size=11, color=POS, bold=True))

    # Нижній контур: Апаратний FTS (незалежний силовий розрив)
    frags.append(rect(20, 265, 780, 195, fill="#eafaf1", stroke=FIELD, sw=1.8))
    frags.append(text(40, 290, "Апаратний ланцюг FTS Kill-Switch (незалежне знеструмлення шини)", size=13, bold=True, color=FIELD, anchor="start"))

    y_bot = 315
    frags.append(fitbox(40, y_bot, 150, b_h, "Виділений FTS-канал\n(433 / 868 МГц LoRa)\n\nНезалежний приймач", size=11, fill="#ffffff", stroke=FIELD))
    frags.append(arrow(190, y_bot + 35, 230, y_bot + 35, color=FIELD, sw=1.8))

    frags.append(fitbox(230, y_bot, 160, b_h, "Апаратний дешифратор\n(Safety MCU / CPLD)\n\nПеревірка CRC та лінку", size=11, fill="#ffffff", stroke=FIELD))
    frags.append(arrow(390, y_bot + 35, 430, y_bot + 35, color=FIELD, sw=1.8))

    frags.append(fitbox(430, y_bot, 170, b_h, "Силовий розмикач\n(Back-to-Back MOSFET)\n\nРозрив силового кола", size=11, fill="#ffffff", stroke=FIELD, bold=True))
    frags.append(arrow(600, y_bot + 35, 640, y_bot + 35, color=FIELD, sw=1.8))

    frags.append(fitbox(640, y_bot, 140, b_h, "Шина живлення ESC\n+ Лінія відстрілу\nпарашута", size=11, fill="#ffffff", stroke=FIELD))

    frags.append(text(410, y_bot + 95, "Гарантія: силове живлення знімається напряму з ESC за < 100 мкс незалежно від стану польотного контролера", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, 'software-vs-hardware-kill-chain.svg'), W, H, *frags)


# ── Фігура 2: Принципова схема силового розмикача FTS на Back-to-Back MOSFET ──
def fig_fts_power_switch():
    W, H = 820, 430
    frags = []
    frags.append(text(W / 2, 28, "Схема силового розмикача FTS на Back-to-Back MOSFET з захистом від дуги",
                      size=15, bold=True))

    # Лівий блок: Джерело живлення та вхід керування
    frags.append(fitbox(30, 60, 190, 130, "LiPo Батарея (VBAT)\n22.2V - 50.4V (6S-12S)\n\nГоловна силова шина\nСтрум до 150-200 A",
                        size=11, fill="#fef9e7", stroke="#d98324", sw=1.6))

    frags.append(fitbox(30, 220, 190, 170, "Вхід FTS / Kill-Switch\n\n• Виділений радіоприймач\n• Оптоізолятор 2.5 кВ\n• Активний рівень LOW\n• Захист від обриву\n(Pull-Down резистор)",
                        size=11, fill="#f0f4f8", stroke=NEG, sw=1.6))

    # Центральний блок: Силовий блок ключів
    frags.append(rect(260, 60, 310, 330, fill="#f4f6f8", stroke=INK, sw=1.8))
    frags.append(text(415, 85, "Силовий вузол розмикача", size=13, bold=True, color=INK))

    frags.append(fitbox(280, 105, 270, 70, "Драйвер затворів (Gate Driver)\nіз помпою заряду (Charge Pump)\nШвидке розряджання затвора (t_off < 5 µs)",
                        size=10, fill="#ffffff", stroke=LINE))

    frags.append(fitbox(280, 190, 270, 95, "Зустрічні N-MOSFET (Back-to-Back)\n• Q1: Блокування прямого струму\n• Q2: Блокування струму рекуперації\n• Низький опір R_ds(on) < 0.8 мОм\n• Без дуги та залипання контактів",
                        size=10, fill="#eafaf1", stroke=FIELD, bold=True))

    frags.append(fitbox(280, 300, 270, 75, "Ланцюг захисту від індуктивних викидів\n• TVS-супресори (V_br = 60 V)\n• RC-снабер (10 Ом + 100 нФ)\n• Захист від перенапруги при відсічці",
                        size=10, fill="#ffffff", stroke=LINE))

    # Правий блок: Навантаження та парашут
    frags.append(fitbox(610, 60, 180, 150, "Силова шина до ESC\n\n• Регулятори моторів\n• Конденсатори фільтра\n• Знеструмлення за < 10 µs\n• Миттєве зняття тяги",
                        size=11, fill="#fdf2f0", stroke=POS, sw=1.6))

    frags.append(fitbox(610, 240, 180, 150, "Лінія порятунку\n(Safe State Actuator)\n\n• Піропатрон парашута\n• Або сервоскид замка\n• Затримка 50-100 мс\n(після зупинки моторів)",
                        size=11, fill="#eef2f7", stroke=NEG, sw=1.6))

    # З'єднувальні лінії
    # VBAT -> MOSFET
    frags.append(arrow(220, 125, 260, 125, color="#d98324", sw=2.0))
    # FTS input -> Gate Driver
    frags.append(arrow(220, 280, 260, 280, color=NEG, sw=1.8))
    # Gate Driver -> MOSFET
    frags.append(arrow(415, 175, 415, 190, color=LINE, sw=1.5))
    # MOSFET -> ESC
    frags.append(arrow(570, 135, 610, 135, color=POS, sw=2.0))
    # FTS -> Parachute
    frags.append(arrow(570, 315, 610, 315, color=NEG, sw=1.8))

    render(os.path.join(OUT, 'fts-power-switch-circuit.svg'), W, H, *frags)


# ── Фігура 3: Матриця визначення Safe State для різних класів апаратів ─────────
def fig_safe_state_matrix():
    W, H = 820, 440
    frags = []
    frags.append(text(W / 2, 28, "Визначення безпечного стану (Safe State) за кінематикою апарата",
                      size=15, bold=True))

    cols = [
        ("Мультикоптер", "Знеструмлення + Парашут", "• Відсічка тяги моторів (FTS)\n• Затримка 80 мс на зупинку гвинтів\n• Викид рятувального парашута\n• Падіння з малою швидкістю (< 4.5 м/с)", "#fdf2f0", POS),
        ("Літак (Крило)", "Спіраль або Парашут", "• Вимкнення штовхального гвинта\n• Рулі в крен 30° та пікірування\n• Кероване зниження в зону вибитку\n• Або примусовий викид парашута", "#fef9e7", "#d98324"),
        ("Ровер (UGV)", "Гальмування + Відсічка", "• Знеструмлення ходових інверторів\n• Динамічне закорочування обмоток\n• Спрацьовування стоянкових гальм\n• Блокування коліс на місці", "#eafaf1", FIELD),
        ("Катер (USV)", "Відсічка + Циркуляція", "• Перекриття палива / інвертора\n• Стерно в крайній кут (циркуляція)\n• Гасіння кінетичної енергії хвилями\n• Дрейф без загрози іншим суднам", "#eef2f7", NEG)
    ]

    bw = 180
    gap = 16
    x0 = (W - (4 * bw + 3 * gap)) / 2
    y0 = 65
    bh = 330

    for i, (title, action, desc, bg_col, border_col) in enumerate(cols):
        x = x0 + i * (bw + gap)
        frags.append(rect(x, y0, bw, bh, fill=bg_col, stroke=border_col, sw=1.8))
        frags.append(text(x + bw / 2, y0 + 26, title, size=13, bold=True, color=INK))
        frags.append(fitbox(x + 10, y0 + 45, bw - 20, 48, action, size=11, bold=True,
                            fill="#ffffff", stroke=border_col, sw=1.4))
        frags.append(fitbox(x + 10, y0 + 105, bw - 20, 210, desc, size=11, bold=False,
                            fill="none", stroke="none"))

    render(os.path.join(OUT, 'safe-state-matrix.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_software_vs_hardware_kill()
    fig_fts_power_switch()
    fig_safe_state_matrix()
    print("All emergency stop figures generated successfully.")
