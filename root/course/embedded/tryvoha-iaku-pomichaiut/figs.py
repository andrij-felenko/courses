# -*- coding: utf-8 -*-
"""figs.py — генерація SVG-фігур для теми «Тривога, яку помічають: пріоритет, звук, потік тривог».
Використовує svgkit зі scripts/. Вивід у ./img/.
"""
import sys, os

TOPIC_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(TOPIC_DIR, '..', '..', '..', '..', 'scripts'))
sys.path.insert(0, SCRIPTS_DIR)
from svgkit import *

IMG_DIR = os.path.join(TOPIC_DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)


# ── Фігура 1: Каскад відмови та придушення першопричини (Alarm Flooding) ───────
def fig_alarm_flooding_cascade():
    W, H = 1060, 560
    P = []

    # Заголовок фігури
    P.append(text(W / 2, 26, "Каскад аварійних повідомлень (Alarm Flooding) та придушення першопричиною", size=15, bold=True))

    # Ліва колонка: Без придушення (лавина тривог)
    w_col = 485
    x_left = 30
    P.append(rect(x_left, 50, w_col, 455, fill="#fff5f5", stroke="#feb2b2", sw=1.5, rx=8))
    P.append(text(x_left + w_col / 2, 75, "БЕЗ ПРИДУШЕННЯ: ЛАВИНА ТРИВОГ (40+ ПОВІДОМЛЕНЬ)", size=12, bold=True, color="#9b2c2c"))

    # Права колонка: З кореляцією та придушенням (Root-Cause Suppression)
    x_right = 545
    P.append(rect(x_right, 50, w_col, 455, fill="#f0fff4", stroke="#9ae6b4", sw=1.5, rx=8))
    P.append(text(x_right + w_col / 2, 75, "З ПРИДУШЕННЯМ ПЕРШОПРИЧИНИ (ROOT-CAUSE SUPPRESSION)", size=12, bold=True, color="#22543d"))

    # Спільна першопричина зверху в обох колонках
    P.append(rect(x_left + 40, 95, w_col - 80, 50, fill="#fed7d7", stroke="#e53e3e", sw=1.8, rx=6))
    P.append(text(x_left + w_col / 2, 116, "ПЕРШОПРИЧИНА: ЗНЕСТРУМЛЕННЯ ШИНИ 5В", size=11, bold=True, color="#742a2a"))
    P.append(text(x_left + w_col / 2, 134, "Коротке замикання в сервоприводі, U_rail = 1.1 В", size=10, color="#742a2a"))

    P.append(rect(x_right + 40, 95, w_col - 80, 50, fill="#fed7d7", stroke="#e53e3e", sw=1.8, rx=6))
    P.append(text(x_right + w_col / 2, 116, "ПЕРШОПРИЧИНА: ЗНЕСТРУМЛЕННЯ ШИНИ 5В", size=11, bold=True, color="#742a2a"))
    P.append(text(x_right + w_col / 2, 134, "Коротке замикання в сервоприводі, U_rail = 1.1 В", size=10, color="#742a2a"))

    # Ліва колонка: стрілка вниз до лавини вторинних симптомів
    y_sym_top = 175
    P.append(arrow(x_left + w_col / 2, 145, x_left + w_col / 2, y_sym_top - 5, color="#e53e3e", sw=2))

    alarms_left = [
        "IMU 1 & 2: SPI Timeout / Data CRC Fail",
        "Barometer: I2C NACK / Zero Pressure",
        "Magnetometer: Bus Fault / Field Invalid",
        "Optical Flow: UART Frame Lost",
        "Rangefinder: No Echo / Sensor Offline",
        "GPS: Serial Timeout / Satellite Loss",
        "ESC Telemetry: Bus Stall / Zero RPM"
    ]

    for i, txt in enumerate(alarms_left):
        y_pos = y_sym_top + i * 36
        P.append(rect(x_left + 30, y_pos, w_col - 60, 28, fill="#ffffff", stroke="#fc8181", sw=1.2, rx=4))
        P.append(text(x_left + 45, y_pos + 18, f"⚠️ CRITICAL: {txt}", size=9.5, bold=True, color="#c53030", anchor="start"))

    # Блок наслідків зліва
    fr_res_l, _, _ = textbox(x_left + w_col / 2, 465,
                             "Результат: 40+ звукових сигналів за 300 мс\nОператор дезорієнтований (когнітивний ступор),\nне бачить справжньої причини й втрачає апарат",
                             size=10, bold=True, fill="#fffaf0", stroke="#dd6b20", min_w=w_col - 40)
    P.append(fr_res_l)

    # Права колонка: фільтр кореляції та результат
    P.append(arrow(x_right + w_col / 2, 145, x_right + w_col / 2, 180, color="#38a169", sw=2))

    fr_filter, _, _ = textbox(x_right + w_col / 2, 215,
                              "Дерево залежностей (Suppression Mask):\nВузол «5V Power Rail» є батьківським для 7 підсистем.\nСпрацьовує правило: Parent ACTIVE => Suppress Children",
                              size=10, bold=True, fill="#e6fffa", stroke="#319795", min_w=w_col - 50)
    P.append(fr_filter)

    P.append(arrow(x_right + w_col / 2, 255, x_right + w_col / 2, 290, color="#38a169", sw=2))

    # Єдина активна тривога оператору
    P.append(rect(x_right + 30, 295, w_col - 60, 56, fill="#feebc8", stroke="#dd6b20", sw=2, rx=6))
    P.append(text(x_right + w_col / 2, 318, "ЄДИНА АКТИВНА ТРИВОГА ДЛЯ ПІЛОТА:", size=11, bold=True, color="#7b341e"))
    P.append(text(x_right + w_col / 2, 338, "CRITICAL: 5V Rail Failure (Child alarms: 42 suppressed)", size=10.5, bold=True, color="#c05621"))

    # Додатковий статус придушених тривог
    P.append(rect(x_right + 30, 365, w_col - 60, 38, fill="#f7fafc", stroke="#cbd5e0", sw=1.2, rx=4))
    P.append(text(x_right + w_col / 2, 382, "Придушені тривоги замасковано у вторинний журнал діагностики.", size=9.5, color="#718096"))
    P.append(text(x_right + w_col / 2, 396, "Звук і головне вікно не захаращуються вторинними збоями.", size=9.5, color="#718096"))

    fr_res_r, _, _ = textbox(x_right + w_col / 2, 465,
                             "Результат: 1 чітке повідомлення та конкретна дія\nПілот миттєво бачить причину: переходить на аварійне\nкерування або активує парашутну систему",
                             size=10, bold=True, fill="#f0fff4", stroke="#38a169", min_w=w_col - 40)
    P.append(fr_res_r)

    # Футер фігури
    fr_bot, _, _ = textbox(W / 2, 535,
                           "Принцип First-Out / Parent-Child: батьківська відмова знеструмлення маскує вторинні збої сенсорів, зберігаючи дієздатність пілота.",
                           size=11, bold=True, fill="#ffffff", stroke=INK)
    P.append(fr_bot)

    render(os.path.join(IMG_DIR, "alarm-flooding-cascade.svg"), W, H, *P)


# ── Фігура 2: Піраміда розподілу тривог за EEMUA 191 / ANSI/ISA-18.2 ───────────
def fig_alarm_hierarchy_eemua():
    W, H = 1060, 560
    P = []

    P.append(text(W / 2, 26, "Ієрархія та розподіл пріоритетів тривог за EEMUA 191 / ANSI/ISA-18.2", size=15, bold=True))

    # Ліва частина: Піраміда розподілу у вигляді ярусів
    pyr_cx = 250

    # Рівень 1: Critical (верхівка)
    fr_c, _, _ = textbox(pyr_cx, 115,
                         "CRITICAL / EMERGENCY\n~5% (до 5 шт)\nДія < 10–30 с",
                         size=11, bold=True, fill="#fed7d7", stroke="#e53e3e", sw=2, min_w=180)
    P.append(fr_c)

    # Рівень 2: Warning (середина)
    fr_w, _, _ = textbox(pyr_cx, 225,
                         "WARNING / HIGH\n~15% (15–20 шт)\nДія 1–5 хв",
                         size=11, bold=True, fill="#feebc8", stroke="#dd6b20", sw=2, min_w=280)
    P.append(fr_w)

    # Рівень 3: Advisory / Low (основа)
    fr_a, _, _ = textbox(pyr_cx, 355,
                         "ADVISORY / LOW / INFO\n~80% (основний масив сповіщень)\nДія не критична (> 10 хв)",
                         size=11, bold=True, fill="#e2e8f0", stroke="#4a5568", sw=2, min_w=380)
    P.append(fr_a)

    # Стрілки зв'язку між ярусами піраміди
    P.append(arrow(pyr_cx, 150, pyr_cx, 185, color="#e53e3e", sw=2))
    P.append(arrow(pyr_cx, 265, pyr_cx, 310, color="#dd6b20", sw=2))

    # Права частина: Характеристики кожного рівня (Табличні картки)
    x_card = 490
    w_card = 535

    # Картка Critical
    P.append(rect(x_card, 75, w_card, 100, fill="#fff5f5", stroke="#e53e3e", sw=1.5, rx=6))
    P.append(rect(x_card, 75, 8, 100, fill="#e53e3e", stroke="none", rx=2))
    P.append(text(x_card + 20, 98, "КРИТИЧНИЙ (Critical / Emergency): Час дії < 10–30 с", size=11, bold=True, color="#9b2c2c", anchor="start"))
    P.append(text(x_card + 20, 120, "• Наслідок: Негайна загроза втрати апарата, зіткнення чи травмування", size=10, color="#2d3748", anchor="start"))
    P.append(text(x_card + 20, 140, "• Візуал: Червоний, миготіння 3–4 Гц, спливаюче модальне вікно", size=10, color="#2d3748", anchor="start"))
    P.append(text(x_card + 20, 160, "• Аудіо: Високочастотний переривчастий тон 3 кГц (4 Гц) + вібрація пульта", size=10, color="#2d3748", anchor="start"))

    # Картка Warning
    P.append(rect(x_card, 190, w_card, 100, fill="#fffaf0", stroke="#dd6b20", sw=1.5, rx=6))
    P.append(rect(x_card, 190, 8, 100, fill="#dd6b20", stroke="none", rx=2))
    P.append(text(x_card + 20, 213, "ПОПЕРЕДЖЕННЯ (Warning / High): Час дії 1–5 хв", size=11, bold=True, color="#c05621", anchor="start"))
    P.append(text(x_card + 20, 235, "• Наслідок: Деградація резерву, перегрів, дефіцит заряду батареї", size=10, color="#2d3748", anchor="start"))
    P.append(text(x_card + 20, 255, "• Візуал: Жовтий / помаранчевий, миготіння 1 Гц, банер у статус-барі", size=10, color="#2d3748", anchor="start"))
    P.append(text(x_card + 20, 275, "• Аудіо: Двотоновий сигнал 1.5 кГц (1 Гц), повтор кожні 15–30 с", size=10, color="#2d3748", anchor="start"))

    # Картка Advisory
    P.append(rect(x_card, 305, w_card, 100, fill="#f7fafc", stroke="#4a5568", sw=1.5, rx=6))
    P.append(rect(x_card, 305, 8, 100, fill="#4a5568", stroke="none", rx=2))
    P.append(text(x_card + 20, 328, "ІНФОРМАЦІЙНИЙ (Advisory / Low): Час дії не критичний (> 10 хв)", size=11, bold=True, color="#2d3748", anchor="start"))
    P.append(text(x_card + 20, 350, "• Наслідок: Перемикання режимів, завершення місії, планові події", size=10, color="#2d3748", anchor="start"))
    P.append(text(x_card + 20, 370, "• Візуал: Синій / сірий / бірюзовий, статична іконка, запис у журнал", size=10, color="#2d3748", anchor="start"))
    P.append(text(x_card + 20, 390, "• Аудіо: Без звуку або одиничний м'який гонг при появі", size=10, color="#2d3748", anchor="start"))

    # Нижня плашка: Нормативи EEMUA 191 щодо частоти появи тривог
    fr_metric, _, _ = textbox(W / 2, 480,
                              "Нормативи частоти появи тривог за EEMUA 191:\n• У сталому режимі: ≤ 1 тривога за 10 хв (≤ 0.1 тривоги/хв)\n• Під час аварійного збурення: ≤ 10 тривог за перші 10 хв процесу",
                              size=11, bold=True, fill="#eef2f7", stroke="#2b6cb0", min_w=W - 60)
    P.append(fr_metric)

    render(os.path.join(IMG_DIR, "alarm-hierarchy-eemua.svg"), W, H, *P)


# ── Фігура 3: Автомат станів життєвого циклу тривоги (Alarm State Machine) ──────
def fig_alarm_state_machine():
    W, H = 1060, 560
    P = []

    P.append(text(W / 2, 26, "Автомат станів тривоги за ISA-18.2: квітування, заглушення та ескалація", size=15, bold=True))

    # Стан 1: NORMAL (Нормальний стан)
    x_norm, y_norm = 160, 160
    fr_norm, w_norm, h_norm = textbox(x_norm, y_norm,
                                      "NORMAL\n(Норма / Очікування)\nПараметри в межах норми.\nІндикатор: ВИМКНЕНО\nЗвук: ТИША",
                                      size=10.5, bold=True, fill="#f0fff4", stroke="#38a169", min_w=190)
    P.append(fr_norm)

    # Стан 2: ACTIVE UNACK (Активна незаквітована)
    x_unack, y_unack = 530, 160
    fr_unack, w_unack, h_unack = textbox(x_unack, y_unack,
                                         "ACTIVE UNACKNOWLEDGED\n(Активна незаквітована)\nПараметр > Порогу.\nІндикатор: МИГОТІННЯ (2-4 Гц)\nЗвук: АКТИВНИЙ СИРЕНА",
                                         size=10.5, bold=True, fill="#fff5f5", stroke="#e53e3e", min_w=220)
    P.append(fr_unack)

    # Стан 3: ACTIVE ACK (Активна заквітована)
    x_ack, y_ack = 900, 160
    fr_ack, w_ack, h_ack = textbox(x_ack, y_ack,
                                   "ACTIVE ACKNOWLEDGED\n(Активна заквітована)\nОператор натиснув ACK.\nІндикатор: СУЦІЛЬНЕ СВІТЛО\nЗвук: ТИША (Заглушено)",
                                   size=10.5, bold=True, fill="#fffaf0", stroke="#dd6b20", min_w=210)
    P.append(fr_ack)

    # Стан 4: CLEARED UNACK (Минула незаквітована)
    x_cl_unack, y_cl_unack = 530, 390
    fr_cl_unack, w_cl_unack, h_cl_unack = textbox(x_cl_unack, y_cl_unack,
                                                 "CLEARED UNACKNOWLEDGED\n(Минула незаквітована)\nПараметр повернувся в норму до ACK.\nІндикатор: ПОВІЛЬНЕ МИГОТІННЯ\nЗвук: ТИША (або м'який тон)",
                                                 size=10.5, bold=True, fill="#edf2f7", stroke="#4a5568", min_w=240)
    P.append(fr_cl_unack)

    # Стан 5: SHELVED / ESCALATED (Відкладена / Ескальована)
    x_esc, y_esc = 900, 390
    fr_esc, w_esc, h_esc = textbox(x_esc, y_esc,
                                   "ESCALATED / SHELVED\n(Ескальована / Автозахист)\nТаймаут T_esc сплив без усунення.\nПріоритет підвищено!\nЗвук: ПОВТОРНА СИРЕНА / FAILSAFE",
                                   size=10.5, bold=True, fill="#fed7d7", stroke="#9b2c2c", min_w=230)
    P.append(fr_esc)

    # ── Переходи між станами ──
    # Normal -> Active Unack
    P.append(arrow(x_norm + w_norm / 2, y_norm, x_unack - w_unack / 2, y_norm, color="#e53e3e", sw=2))
    P.append(text((x_norm + x_unack) / 2, y_norm - 14, "Параметр > Порогу (після Debounce)", size=9.5, bold=True, color="#e53e3e"))

    # Active Unack -> Active Ack (Квітування)
    P.append(arrow(x_unack + w_unack / 2, y_ack, x_ack - w_ack / 2, y_ack, color="#dd6b20", sw=2))
    P.append(text((x_unack + x_ack) / 2, y_ack - 14, "Команда: ACK (Квітувати)", size=9.5, bold=True, color="#dd6b20"))

    # Active Ack -> Normal (Параметр повернувся в норму)
    P.append(line(x_ack, y_ack - h_ack / 2, x_ack, 75, color="#38a169", sw=1.8))
    P.append(line(x_ack, 75, x_norm, 75, color="#38a169", sw=1.8))
    P.append(arrow(x_norm, 75, x_norm, y_norm - h_norm / 2, color="#38a169", sw=1.8))
    P.append(text(W / 2, 63, "Параметр повернувся в норму (U < Порогу - Hysteresis) => Повне очищення", size=9.5, bold=True, color="#22543d"))

    # Active Unack -> Cleared Unack (Параметр зник сам без квітування)
    P.append(arrow(x_unack - 30, y_unack + h_unack / 2, x_cl_unack - 30, y_cl_unack - h_cl_unack / 2, color="#4a5568", sw=1.8))
    P.append(text(x_unack - 110, (y_unack + y_cl_unack) / 2, "Нормалізація\nбез ACK", size=9, bold=True, color="#4a5568"))

    # Cleared Unack -> Normal (Оператор нарешті квітує минулу аварію)
    P.append(arrow(x_cl_unack - w_cl_unack / 2, y_cl_unack, x_norm, y_norm + h_norm / 2 + 10, color="#38a169", sw=1.8))
    P.append(text(x_norm + 60, y_cl_unack + 15, "Команда ACK на минулій тривозі => Очищення", size=9.5, bold=True, color="#22543d"))

    # Active Ack -> Escalated (Сплив таймер мовчання T_esc, а причина не усунута)
    P.append(arrow(x_ack, y_ack + h_ack / 2, x_esc, y_esc - h_esc / 2, color="#9b2c2c", sw=2))
    P.append(text(x_ack + 15, (y_ack + y_esc) / 2, "Таймаут T_esc сплив\n(причина не зникла)", size=9, bold=True, color="#9b2c2c", anchor="start"))

    # Escalated -> Active Ack (Повторний ACK після ескалації)
    P.append(arrow(x_esc - 40, y_esc - h_esc / 2, x_ack - 40, y_ack + h_ack / 2, color="#dd6b20", sw=1.5))

    # Нижній підсумок
    fr_bot, _, _ = textbox(W / 2, 515,
                           "Ключова відмінність: Silence (заглушення) тимчасово вимикає звук, але залишає таймер ескалації T_esc;\n"
                           "Acknowledge (квітування) підтверджує, що оператор прийняв відповідальність за локалізацію аварії.",
                           size=11, bold=True, fill="#ffffff", stroke=INK)
    P.append(fr_bot)

    render(os.path.join(IMG_DIR, "alarm-state-machine.svg"), W, H, *P)


# ── Фігура 4: Повний конвеєр обробки сигналу тривоги (Conditioning Pipeline) ──
def fig_alarm_conditioning_pipeline():
    W, H = 1060, 560
    P = []

    P.append(text(W / 2, 26, "Конвеєр обробки та кондиціонування сигналів аварійної сигналізації", size=15, bold=True))

    # 5 послідовних етапів у конвеєрі
    boxes = [
        ("1. Сире вимірювання\nта фільтрація", "АЦП / Цифровий датчик\n(Шум, викиди, перешкоди)\nФільтр LPF / Медіана", "#f7fafc", "#4a5568"),
        ("2. Гістерезис\nта Дебаунс", "Поріг Th ± Δ_hyst\nТаймери On-delay (200 мс)\nта Off-delay (500 мс)", "#fffaf0", "#dd6b20"),
        ("3. Фільтр деренчання\n(Chattering Filter)", "Детектор Flapping:\n> 3 спрацьовувань за 60 с\n=> Тимчасовий лок з міткою", "#fed7d7", "#c53030"),
        ("4. Стан-залежне\nмаскування (Mode)", "Матриця станів апарата:\nДвигун OFF => Тиск маски\nНа землі => GPS глибина", "#e6fffa", "#319795"),
        ("5. Придушення\nпершопричини (Tree)", "Parent/Child граф відмов:\nШина 5V OFF => Маскувати\nIMU, Baro, Mag, GPS", "#ebf8ff", "#2b6cb0")
    ]

    box_w = 175
    gap = 35
    start_x = 35
    y_box = 135

    for idx, (title, desc, fill_c, stroke_c) in enumerate(boxes):
        cx = start_x + idx * (box_w + gap) + box_w / 2
        fr, _, _ = textbox(cx, y_box, f"{title}\n{desc}", size=10, bold=True, fill=fill_c, stroke=stroke_c, min_w=box_w)
        P.append(fr)

        if idx < len(boxes) - 1:
            P.append(arrow(cx + box_w / 2, y_box, cx + box_w / 2 + gap, y_box, color="#2b6cb0", sw=2))

    # Центральний диспетчер тривог (Alarm Dispatcher & Prioritizer)
    disp_y = 310
    fr_disp, w_disp, h_disp = textbox(W / 2, disp_y,
                                      "Диспетчер тривог (Prioritized Alarm Engine)\n"
                                      "• Черга пріоритетів: Critical (1) > Warning (2) > Advisory (3)\n"
                                      "• Оновлення стану: Перевірка таймерів мовчання та ескалації T_esc\n"
                                      "• Детерміноване виконання без динамічного виділення пам'яті (Zero Heap)",
                                      size=11, bold=True, fill="#edf2f7", stroke="#1a202c", min_w=680)
    P.append(fr_disp)

    # Стрілка вниз від 5-го блоку до диспетчера
    last_cx = start_x + 4 * (box_w + gap) + box_w / 2
    P.append(line(last_cx, y_box + 45, last_cx, disp_y, color="#2b6cb0", sw=2))
    P.append(arrow(last_cx, disp_y, W / 2 + w_disp / 2, disp_y, color="#2b6cb0", sw=2))

    # 3 виходи з диспетчера знизу
    out_y = 445
    outputs = [
        ("АУДІО-СИСТЕМА (Buzzer/TTS)", "Critical: 3 кГц (4 Гц)\nWarning: 1.5 кГц (1 Гц)\nAdvisory: Тиша/Гонг", "#fff5f5", "#e53e3e"),
        ("ВІЗУАЛЬНИЙ HMI (Дисплей)", "Critical: Червоний баннер + модаль\nWarning: Жовтий статус-рядок\nAdvisory: Журнал повідомлень", "#fffaf0", "#dd6b20"),
        ("АВТОМАТИЧНИЙ ЗАХИСТ (Failsafe)", "Ескалація критичної тривоги:\nАвтоповернення (RTL), парашут,\nбезпечне знеструмлення приводів", "#f0fff4", "#38a169")
    ]

    out_w = 290
    out_gap = 40
    out_start_x = 55

    for idx, (title, desc, fill_c, stroke_c) in enumerate(outputs):
        cx = out_start_x + idx * (out_w + out_gap) + out_w / 2
        fr, _, _ = textbox(cx, out_y, f"{title}\n{desc}", size=10, bold=True, fill=fill_c, stroke=stroke_c, min_w=out_w)
        P.append(fr)
        # Стрілка від диспетчера до виходу
        P.append(arrow(cx, disp_y + h_disp / 2, cx, out_y - 35, color=stroke_c, sw=2))

    # Футер
    fr_bot, _, _ = textbox(W / 2, 530,
                           "Повний фільтраційний конвеєр захищає людину від хибних спрацьовувань, деренчання та вторинних симптомів.",
                           size=11, bold=True, fill="#ffffff", stroke=INK)
    P.append(fr_bot)

    render(os.path.join(IMG_DIR, "alarm-conditioning-pipeline.svg"), W, H, *P)


if __name__ == "__main__":
    fig_alarm_flooding_cascade()
    fig_alarm_hierarchy_eemua()
    fig_alarm_state_machine()
    fig_alarm_conditioning_pipeline()
    print("Всі фігури згенеровано успішно.")
