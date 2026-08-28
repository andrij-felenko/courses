# -*- coding: utf-8 -*-
"""figs.py — ілюстрації до теми «Керована термінація: коли правильна дія — впасти».
Генерує SVG-фігури за допомогою svgkit у теку ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), "img"), exist_ok=True)


def fig_hardware_architecture():
    W, H = 960, 530
    P = []
    P.append(text(W / 2, 28, "Апаратна архітектура незалежної системи припинення польоту (FTS)", size=16, bold=True))

    # Ліва зона: Головний контур польотного контролера (Primary FC Domain)
    fc_x, fc_y, fc_w, fc_h = 40, 55, 270, 445
    P.append(rect(fc_x, fc_y, fc_w, fc_h, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    P.append(text(fc_x + fc_w / 2, fc_y + 24, "Головний контур (Primary FC)", size=13, bold=True, color="#334155"))
    P.append(line(fc_x + 15, fc_y + 34, fc_x + fc_w - 15, fc_y + 34, color="#cbd5e1", sw=1))

    # Елементи головного контуру
    P.append(fitbox(fc_x + 20, fc_y + 48, fc_w - 40, 60,
                    "Основна батарея (LiPo 6S)\nта плата PDB / BEC 5V",
                    size=11, pad=6, fill="#ffffff", stroke="#cbd5e1", bold=False))

    P.append(fitbox(fc_x + 20, fc_y + 125, fc_w - 40, 85,
                    "Польотний контролер (FC)\n"
                    "• Основна RTOS / автопілот\n"
                    "• Первинний GNSS + IMU\n"
                    "• Телеметрія MAVLink",
                    size=10.5, pad=6, fill="#ffffff", stroke="#cbd5e1", bold=False))

    P.append(fitbox(fc_x + 20, fc_y + 230, fc_w - 40, 65,
                    "ШІМ / DShot лінії керування\n(сигнали на регулятори ESC)",
                    size=10.5, pad=6, fill="#ffffff", stroke="#cbd5e1", bold=False))

    P.append(fitbox(fc_x + 20, fc_y + 315, fc_w - 40, 80,
                    "Силова установка\n"
                    "• Регулятори швидкості (ESC)\n"
                    "• Безколекторні мотори\n"
                    "• Тягові пропелери",
                    size=10.5, pad=6, fill="#ffffff", stroke="#cbd5e1", bold=False))

    P.append(text(fc_x + fc_w / 2, fc_y + 425, "Зона ризику: зависання або PDB-відмова", size=9.5, color=MUTED, italic=True))

    # Середня зона: Бар'єр гальванічної ізоляції та силові комутатори
    bar_x, bar_y, bar_w, bar_h = 345, 55, 270, 445
    P.append(rect(bar_x, bar_y, bar_w, bar_h, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=8))
    P.append(text(bar_x + bar_w / 2, bar_y + 24, "Бар'єр ізоляції та переривання", size=13, bold=True, color="#b45309"))
    P.append(line(bar_x + 15, bar_y + 34, bar_x + bar_w - 15, bar_y + 34, color="#fde68a", sw=1))

    P.append(fitbox(bar_x + 15, bar_y + 48, bar_w - 30, 80,
                    "Оптоізолятори / Швидкісні буфери\n"
                    "Повна гальванічна розв'язка сигналів\n"
                    "між FC та резервним FTS\n"
                    "(пробивна напруга > 2.5 кВ)",
                    size=10, pad=6, fill="#ffffff", stroke="#fcd34d", bold=False))

    P.append(fitbox(bar_x + 15, bar_y + 148, bar_w - 30, 88,
                    "Апаратний селектор ШІМ / eFuse\n"
                    "• High-Side MOSFET переривач\n"
                    "• Миттєве заземлення ліній DShot\n"
                    "• Апаратний пріоритет FTS Kill",
                    size=10, pad=6, fill="#ffffff", stroke="#fcd34d", bold=False))

    P.append(fitbox(bar_x + 15, bar_y + 256, bar_w - 30, 105,
                    "Двоконтурний інтерлок піропатрона\n"
                    "• Ключ ARM (увімкнення заряду)\n"
                    "• Ключ FIRE (імпульс підриву)\n"
                    "• Захист від брязкоту живлення\n"
                    "• Ємнісний накопичувач струму",
                    size=10, pad=6, fill="#ffffff", stroke="#fcd34d", bold=False))

    P.append(fitbox(bar_x + 15, bar_y + 380, bar_w - 30, 52,
                    "Силовий вихід:\nМиттєве відсікання живлення моторів",
                    size=10, pad=5, fill="#fef2f2", stroke="#fca5a5", color=POS, bold=True))

    # Права зона: Повністю незалежна підсистема FTS (Dedicated FTS Domain)
    fts_x, fts_y, fts_w, fts_h = 650, 55, 270, 445
    P.append(rect(fts_x, fts_y, fts_w, fts_h, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=8))
    P.append(text(fts_x + fts_w / 2, fts_y + 24, "Підсистема FTS (Dedicated Safe)", size=13, bold=True, color="#1d4ed8"))
    P.append(line(fts_x + 15, fts_y + 34, fts_x + fts_w - 15, fts_y + 34, color="#bfdbfe", sw=1))

    P.append(fitbox(fts_x + 15, fts_y + 48, fts_w - 30, 75,
                    "Автономне живлення FTS\n"
                    "• Окрема батарея LiFePO4 2S\n"
                    "• Суперконденсаторний буфер 5Ф\n"
                    "• Робота ≥ 45 хв без головного борту",
                    size=10, pad=6, fill="#ffffff", stroke="#93c5fd", bold=False))

    P.append(fitbox(fts_x + 15, fts_y + 140, fts_w - 30, 95,
                    "Незалежний мікроконтролер FTS\n"
                    "• Виділений чип (STM32G0/RP2040)\n"
                    "• Власний тривісний IMU (детектор штопору)\n"
                    "• Автономний FSM безпеки\n"
                    "• Апаратний сторожовий таймер",
                    size=10, pad=6, fill="#ffffff", stroke="#93c5fd", bold=False))

    P.append(fitbox(fts_x + 15, fts_y + 252, fts_w - 30, 80,
                    "Резервний радіоканал (868/433 МГц)\n"
                    "• Прямий LoRa/GFSK канал зв'язку\n"
                    "• Криптографічна автентифікація\n"
                    "• Незалежна антена на кілі/промені",
                    size=10, pad=6, fill="#ffffff", stroke="#93c5fd", bold=False))

    P.append(fitbox(fts_x + 15, fts_y + 350, fts_w - 30, 82,
                    "Активатор парашута\n"
                    "• Балістичний піропатрон (Squib)\n"
                    "• Механічний викидач купола\n"
                    "• Спуск дрона: V < 4.0 м/с",
                    size=10, pad=6, fill="#ffffff", stroke="#93c5fd", bold=False))

    # Зв'язки між блоками (стрілки взаємодії)
    P.append(arrow(fts_x + 15, fts_y + 185, bar_x + bar_w - 15, bar_y + 185, color=POS, sw=2))
    P.append(arrow(bar_x + 15, bar_y + 185, fc_x + fc_w - 15, fc_y + 260, color=POS, sw=2))
    P.append(arrow(bar_x + bar_w / 2, bar_y + 361, bar_x + bar_w / 2, bar_y + 380, color=POS, sw=2))
    P.append(arrow(bar_x + bar_w - 15, bar_y + 305, fts_x + 15, fts_y + 390, color=FIELD, sw=2))

    render(os.path.join(os.path.dirname(__file__), "img", "fts-hardware-architecture.svg"), W, H, *P)


def fig_decision_and_timing():
    W, H = 960, 520
    P = []
    P.append(text(W / 2, 28, "Критерії спрацьовування та часова діаграма аварійної термінації", size=16, bold=True))

    # Верхній блок: 4 критерії тригера FTS
    P.append(text(W / 2, 58, "Вхідні тригери аварійного стану (Критерії ухвалення рішення)", size=12.5, bold=True, color="#475569"))

    col_w = 215
    spacing = 15
    start_x = 25
    y_crit = 72
    h_crit = 120

    # Критерій 1: Геозона
    c1_x = start_x
    P.append(rect(c1_x, y_crit, col_w, h_crit, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=6))
    P.append(text(c1_x + col_w / 2, y_crit + 20, "1. Прорив геозони", size=11.5, bold=True, color=POS))
    P.append(fitbox(c1_x + 10, y_crit + 28, col_w - 20, 84,
                    "Порушення невідкличної\n"
                    "межі утримання (Hard Geofence).\n"
                    "Виліт за межі полігону\n"
                    "у бік населених пунктів.",
                    size=9.5, pad=4, fill="#fef2f2", stroke="#fee2e2", bold=False))

    # Критерій 2: Штопор
    c2_x = c1_x + col_w + spacing
    P.append(rect(c2_x, y_crit, col_w, h_crit, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=6))
    P.append(text(c2_x + col_w / 2, y_crit + 20, "2. Некерований штопор", size=11.5, bold=True, color=POS))
    P.append(fitbox(c2_x + 10, y_crit + 28, col_w - 20, 84,
                    "Кутова швидкість обертання\n"
                    "|ω| > 450 °/с по двох осях\n"
                    "довше ніж t > 300 мс.\n"
                    "Втрата стійкості рами.",
                    size=9.5, pad=4, fill="#fef2f2", stroke="#fee2e2", bold=False))

    # Критерій 3: Розбіжність EKF
    c3_x = c2_x + col_w + spacing
    P.append(rect(c3_x, y_crit, col_w, h_crit, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=6))
    P.append(text(c3_x + col_w / 2, y_crit + 20, "3. Розбіжність EKF", size=11.5, bold=True, color=POS))
    P.append(fitbox(c3_x + 10, y_crit + 28, col_w - 20, 84,
                    "Коваріація нев'язок фільтра\n"
                    "перевищує поріг (ratio > 5.0).\n"
                    "Повна втрата просторової\n"
                    "орієнтації та координат.",
                    size=9.5, pad=4, fill="#fef2f2", stroke="#fee2e2", bold=False))

    # Критерій 4: Ручна команда
    c4_x = c3_x + col_w + spacing
    P.append(rect(c4_x, y_crit, col_w, h_crit, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=6))
    P.append(text(c4_x + col_w / 2, y_crit + 20, "4. Ручна Kill-команда", size=11.5, bold=True, color=POS))
    P.append(fitbox(c4_x + 10, y_crit + 28, col_w - 20, 84,
                    "Пряма команда оператора\n"
                    "через резервний канал 868 МГц.\n"
                    "Двостадійне взведення:\n"
                    "ARM -> TERMINATE + HMAC.",
                    size=9.5, pad=4, fill="#fef2f2", stroke="#fee2e2", bold=False))

    # Розподільчий блок FTS Logic
    P.append(arrow(W / 2, y_crit + h_crit, W / 2, 222, color=POS, sw=2.5))
    P.append(textbox(W / 2, 238, "ЛОГІЧНИЙ ТРИГЕР FTS: ВХІД У ФАЗУ АВАРІЙНОЇ ТЕРМІНАЦІЇ", size=11.5, bold=True, color=POS, fill="#fee2e2", stroke=POS)[0])

    # Нижня частина: Часова шкала виконання термінації (Timeline)
    tl_y = 300
    P.append(line(45, tl_y, 915, tl_y, color="#334155", sw=2.5))
    P.append(arrow(915, tl_y, 940, tl_y, color="#334155", sw=2.5))
    P.append(text(925, tl_y - 12, "Час t", size=11, bold=True, color="#334155"))

    # Фаза 1: T = 0 ms
    t1_x = 90
    P.append(circle(t1_x, tl_y, 6, fill=POS, stroke="#991b1b", sw=1.5))
    P.append(text(t1_x, tl_y - 15, "T = 0 мс", size=11, bold=True, color=POS))
    P.append(fitbox(t1_x - 70, tl_y + 18, 140, 85,
                    "КРОК 1:\n"
                    "Миттєвий Motor Kill\n"
                    "• Зняття ШІМ/DShot\n"
                    "• Відсікання eFuse\n"
                    "• Знеструмлення ESC",
                    size=9.5, pad=5, fill="#fef2f2", stroke="#fca5a5", bold=False))

    # Фаза 2: T = 60..100 ms
    t2_x = 330
    P.append(circle(t2_x, tl_y, 6, fill="#ea580c", stroke="#9a3412", sw=1.5))
    P.append(text(t2_x, tl_y - 15, "T = 60–100 мс", size=11, bold=True, color="#ea580c"))
    P.append(fitbox(t2_x - 85, tl_y + 18, 170, 85,
                    "КРОК 2:\n"
                    "Активація піропатрона\n"
                    "• Зупинка обертання гвинтів\n"
                    "• Імпульс струму на Squib\n"
                    "• Балістичний відстріл",
                    size=9.5, pad=5, fill="#fff7ed", stroke="#fdba74", bold=False))

    # Фаза 3: T = 200..400 ms
    t3_x = 590
    P.append(circle(t3_x, tl_y, 6, fill="#2563eb", stroke="#1e40af", sw=1.5))
    P.append(text(t3_x, tl_y - 15, "T = 200–400 мс", size=11, bold=True, color="#2563eb"))
    P.append(fitbox(t3_x - 85, tl_y + 18, 170, 85,
                    "КРОК 3:\n"
                    "Витягування та наповнення\n"
                    "• Вихід строп із тубуса\n"
                    "• Розгортання полотнища\n"
                    "• Початок гальмування",
                    size=9.5, pad=5, fill="#eff6ff", stroke="#93c5fd", bold=False))

    # Фаза 4: T > 600 ms
    t4_x = 830
    P.append(circle(t4_x, tl_y, 6, fill=FIELD, stroke="#166534", sw=1.5))
    P.append(text(t4_x, tl_y - 15, "T > 600 мс", size=11, bold=True, color=FIELD))
    P.append(fitbox(t4_x - 80, tl_y + 18, 160, 85,
                    "КРОК 4:\n"
                    "Усталений спуск\n"
                    "• Швидкість V < 3.5 м/с\n"
                    "• Енергія удару < 80 Дж\n"
                    "• Безпека людей на землі",
                    size=9.5, pad=5, fill="#f0fdf4", stroke="#86efac", bold=False))

    # Зв'язки між кроками
    P.append(arrow(t1_x + 72, tl_y + 60, t2_x - 87, tl_y + 60, color="#94a3b8", sw=1.5))
    P.append(arrow(t2_x + 87, tl_y + 60, t3_x - 87, tl_y + 60, color="#94a3b8", sw=1.5))
    P.append(arrow(t3_x + 87, tl_y + 60, t4_x - 82, tl_y + 60, color="#94a3b8", sw=1.5))

    render(os.path.join(os.path.dirname(__file__), "img", "fts-decision-and-timing.svg"), W, H, *P)


if __name__ == "__main__":
    fig_hardware_architecture()
    fig_decision_and_timing()
    print("SVG figures generated successfully.")
