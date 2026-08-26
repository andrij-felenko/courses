# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. heisenbug-probe-effect: фізичний і програмний ефект спостереження ────────
# Ідея: показуємо два канали зникнення дефекту:
# 1) Апаратний: підключення щупа осцилографа (15 пФ + індуктивність земляного дроту)
#    згладжує наносекундний глітч відбиття на шині, і лінія більше не ловить фальшивий такт.
# 2) Програмний: блокуючий printf() додає 2.6 мс затримки, розводячи конкурентні задачі
#    в часі й ліквідуючи гонку даних.

def fig_probe_effect():
    W, H = 840, 420
    p = []

    # Заголовок секцій
    p.append(rect(20, 20, 385, 370, fill="#fcfdfe", stroke="#cfd6dd", sw=1.2, rx=8))
    p.append(rect(435, 20, 385, 370, fill="#fcfdfe", stroke="#cfd6dd", sw=1.2, rx=8))

    p.append(text(212, 45, "Апаратне втручання: щуп осцилографа", size=13, bold=True, color=INK))
    p.append(text(627, 45, "Програмне втручання: виклик printf()", size=13, bold=True, color=INK))

    # Ліва колонка — Апаратний щуп
    # Схема сигналу без щупа (з глітчем)
    p.append(text(40, 75, "Без щупа: відбиття сигналу → помилковий перепад", size=11, bold=True, color=POS, anchor="start"))
    p.append(line(40, 130, 90, 130, color=INK, sw=2.0))
    p.append(line(90, 130, 100, 95, color=INK, sw=2.0))
    p.append(line(100, 95, 120, 95, color=INK, sw=2.0))
    # Глітч/дзвін
    p.append(line(120, 95, 130, 140, color=POS, sw=2.2))
    p.append(line(130, 140, 140, 95, color=POS, sw=2.2))
    p.append(line(140, 95, 220, 95, color=INK, sw=2.0))
    # Поріг логіки
    p.append(line(35, 118, 225, 118, color=MUTED, sw=1.2, dash="3 3"))
    p.append(text(230, 122, "Поріг V_IL", size=10, color=MUTED, anchor="start"))
    p.append(text(130, 160, "⚡ Фальшивий такт!", size=10.5, bold=True, color=POS))

    # Підключення щупа
    b_probe, _, _ = textbox(212, 205, "Щуп: C_probe ≈ 12..15 пФ + L_gnd ≈ 30 нГн\nФільтр нижніх частот: τ = R · (C_line + C_probe)",
                            size=10.5, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.4, min_w=340)
    p.append(b_probe)

    # Сигнал зі щупом (згладжений)
    p.append(text(40, 260, "Зі щупом: фронт завалений, глітч відфільтровано", size=11, bold=True, color=FIELD, anchor="start"))
    p.append(line(40, 310, 85, 310, color=INK, sw=2.0))
    p.append(line(85, 310, 110, 280, color=INK, sw=2.0)) # повільніший фронт
    p.append(line(110, 280, 125, 280, color=INK, sw=2.0))
    p.append(line(125, 280, 135, 292, color=FIELD, sw=2.0)) # згладжений глітч, не перетинає поріг
    p.append(line(135, 292, 145, 280, color=FIELD, sw=2.0))
    p.append(line(145, 280, 220, 280, color=INK, sw=2.0))
    p.append(line(35, 300, 225, 300, color=MUTED, sw=1.2, dash="3 3"))
    p.append(text(230, 304, "Поріг V_IL", size=10, color=MUTED, anchor="start"))
    p.append(text(212, 345, "✓ Дефект зник: глітч не досягає порогу V_IL", size=11, bold=True, color=FIELD))

    # Права колонка — Програмний printf
    p.append(text(455, 75, "Без логів: мікросекундна гонка даних (Race Condition)", size=11, bold=True, color=POS, anchor="start"))
    # Часові смужки задач
    p.append(rect(455, 95, 140, 26, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(text(525, 112, "Задача A: запис у буфер", size=10, bold=True, color=POS))
    p.append(rect(560, 128, 140, 26, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(text(630, 145, "Задача B: читання буфера", size=10, bold=True, color=POS))
    # Зона накладання
    p.append(rect(560, 95, 35, 59, fill="none", stroke=POS, sw=1.8))
    p.append(text(715, 118, "⚡ Одночасний", size=10.5, bold=True, color=POS, anchor="start"))
    p.append(text(715, 134, "доступ до ОЗП!", size=10.5, bold=True, color=POS, anchor="start"))

    # Вставка printf
    b_log, _, _ = textbox(627, 205, "Додано printf(\"val=%d\\n\");\nЗатримка UART 115200 бод: 20 байт ≈ 1.74 мс",
                          size=10.5, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.4, min_w=340)
    p.append(b_log)

    p.append(text(455, 260, "З логами: виклики розведені в часі на мілісекунди", size=11, bold=True, color=FIELD, anchor="start"))
    p.append(rect(455, 280, 120, 26, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(text(515, 297, "Задача A: запис", size=10, bold=True, color=POS))

    # Смужка printf
    p.append(rect(580, 280, 100, 26, fill="#fff3e0", stroke="#e67e22", sw=1.4, rx=4))
    p.append(text(630, 297, "printf() затримка", size=10, bold=True, color="#b9770e"))

    p.append(rect(685, 312, 120, 26, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(745, 329, "Задача B: читання", size=10, bold=True, color=FIELD))

    p.append(text(627, 365, "✓ Дефект зник: інтервал між задачами збільшився у 1000 разів", size=11, bold=True, color=FIELD))

    # Загальний підсумок знизу
    p.append(text(W / 2, 405, "Спостереження змінює фізичні параметри схеми (ємність) або розклад процесора (затримка)",
                  size=12, color=INK, italic=True))

    render(os.path.join(OUT, "heisenbug-probe-effect.svg"), W, H, *p,
           title="Ефект Гайзенбага: чому вимірювання лікує плаваючий дефект")


# ── 2. pvt-setup-hold: площина PVT та порушення Setup / Hold ───────────────────
# Ідея: площина "Напруга / Температура" і дві зони ризику:
# 1) Slow Corner (висока T, низька VDD) → затримка вентилів зростає → Setup Violation.
# 2) Fast Corner (низька T, висока VDD) → затримка надто мала → Hold Violation.
# Знизу — часова діаграма такту та вікно апертури D-тригера.

def fig_pvt_timing():
    W, H = 860, 430
    p = []

    # Лівий блок: Карта кутів PVT
    p.append(rect(20, 20, 370, 380, fill="#fcfdfe", stroke="#cfd6dd", sw=1.2, rx=8))
    p.append(text(205, 45, "Простір параметрів кристала (PVT)", size=13, bold=True, color=INK))

    # Осі координат VDD (Y) та Температура (X)
    x0, y0 = 60, 330
    gw, gh = 290, 240
    p.append(arrow(x0, y0, x0 + gw + 20, y0, color=INK, sw=1.8)) # Вісь T
    p.append(arrow(x0, y0, x0, y0 - gh - 20, color=INK, sw=1.8)) # Вісь VDD

    p.append(text(x0 + gw + 15, y0 + 20, "Температура (°C)", size=11, color=INK, bold=True, anchor="end"))
    p.append(text(x0 - 15, y0 - gh - 10, "Напруга V_DD", size=11, color=INK, bold=True, anchor="start"))

    p.append(text(x0 + 40, y0 + 16, "-40 °C", size=10, color=MUTED))
    p.append(text(x0 + 130, y0 + 16, "+25 °C (Стенд)", size=10, color=MUTED))
    p.append(text(x0 + 240, y0 + 16, "+85 °C", size=10, color=MUTED))

    p.append(text(x0 - 8, y0 - 30, "3.0 В", size=10, color=MUTED, anchor="end"))
    p.append(text(x0 - 8, y0 - 120, "3.3 В", size=10, color=MUTED, anchor="end"))
    p.append(text(x0 - 8, y0 - 210, "3.6 В", size=10, color=MUTED, anchor="end"))

    # Зона Slow Corner
    p.append(rect(x0 + 170, y0 - 70, 110, 60, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
    p.append(text(x0 + 225, y0 - 45, "SLOW CORNER\n(Повільний кут)", size=10, bold=True, color=POS))
    p.append(text(x0 + 225, y0 - 15, "Ризик: Setup Violation", size=9.5, bold=True, color=POS))

    # Зона Fast Corner
    p.append(rect(x0 + 10, y0 - 230, 110, 60, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=6))
    p.append(text(x0 + 65, y0 - 205, "FAST CORNER\n(Швидкий кут)", size=10, bold=True, color=NEG))
    p.append(text(x0 + 65, y0 - 175, "Ризик: Hold Violation", size=9.5, bold=True, color=NEG))

    # Робоча точка лабораторії
    p.append(circle(x0 + 130, y0 - 120, 6, fill=FIELD, stroke=FIELD, sw=1.5))
    p.append(text(x0 + 130, y0 - 132, "Лабораторний стіл (+25°C, 3.3В)", size=9.5, bold=True, color=FIELD))

    # Правий блок: Часова діаграма апертури D-тригера
    p.append(rect(410, 20, 430, 380, fill="#fcfdfe", stroke="#cfd6dd", sw=1.2, rx=8))
    p.append(text(625, 45, "Часові порушення на фронті такту", size=13, bold=True, color=INK))

    # Тактовий сигнал CLK
    p.append(text(430, 85, "CLK", size=11, bold=True, color=INK, anchor="start"))
    p.append(line(470, 95, 580, 95, color=INK, sw=2.0))
    p.append(line(580, 95, 600, 65, color=INK, sw=2.2)) # активний фронт
    p.append(line(600, 65, 780, 65, color=INK, sw=2.0))

    # Заборонена зона (Setup / Hold window)
    p.append(rect(540, 60, 120, 150, fill="#fff3e0", stroke="#e67e22", sw=1.2))
    p.append(line(600, 60, 600, 210, color=POS, sw=1.5, dash="2 2")) # лінія фронту
    p.append(text(570, 78, "t_setup", size=10, bold=True, color="#b9770e"))
    p.append(text(630, 78, "t_hold", size=10, bold=True, color="#b9770e"))

    # Сигнал Data 1: Setup Violation
    p.append(text(430, 135, "DATA\n(Slow)", size=10.5, bold=True, color=POS, anchor="start"))
    p.append(line(470, 150, 570, 150, color=POS, sw=2.0))
    p.append(line(570, 150, 590, 120, color=POS, sw=2.0))
    p.append(line(590, 120, 780, 120, color=POS, sw=2.0))
    p.append(text(675, 145, "⚡ Setup: запізнився до фронту!", size=10, bold=True, color=POS, anchor="start"))

    # Сигнал Data 2: Hold Violation
    p.append(text(430, 185, "DATA\n(Fast)", size=10.5, bold=True, color=NEG, anchor="start"))
    p.append(line(470, 175, 605, 175, color=NEG, sw=2.0))
    p.append(line(605, 175, 625, 205, color=NEG, sw=2.0))
    p.append(line(625, 205, 780, 205, color=NEG, sw=2.0))
    p.append(text(675, 195, "⚡ Hold: змінився занадто рано!", size=10, bold=True, color=NEG, anchor="start"))

    # Висновки в рамці праворуч внизу
    b_rule, _, _ = textbox(625, 305, "Порушення Setup: лікується зменшенням частоти шини\nПорушення Hold: НЕ лікується частотою (потрібна затримка лінії!)",
                           size=10, bold=True, color=INK, fill="#f4f6f8", stroke=LINE, sw=1.4, min_w=380)
    p.append(b_rule)

    p.append(text(W / 2, 415, "Дефект вилазить лише на краях робочого діапазону температур та напруг (PVT Corners)",
                  size=12, color=INK, italic=True))

    render(os.path.join(OUT, "pvt-setup-hold.svg"), W, H, *p,
           title="Граничні таймінги: вплив PVT-кутів на порушення Setup та Hold")


# ── 3. thermal-drift-uart: температурний дрейф RC-генератора та UART ───────────
# Ідея: внутрішній RC-генератор (HSI) має похибку частоти залежно від температури.
# UART вимагає похибки не більше ±2.5%. При -20°C та +60°C похибка виходить за межі,
# викликаючи спорадичні помилки Framing Error.

def fig_thermal_drift():
    W, H = 800, 360
    p = []

    # Вісь X — Температура від -40 до +85 °C
    # Вісь Y — Похибка частоти від -5% до +5%
    x0, y0 = 90, 180
    gw, gh = 620, 240

    # Зона допустимої похибки UART (±2.5%)
    p.append(rect(x0, y0 - 60, gw, 120, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(x0 + gw - 15, y0 - 35, "Допустиме вікно UART (±2.5%)", size=11, bold=True, color=FIELD, anchor="end"))

    # Горизонтальні лінії
    p.append(line(x0 - 15, y0, x0 + gw + 15, y0, color=INK, sw=1.5)) # 0%
    p.append(line(x0 - 15, y0 - 60, x0 + gw + 15, y0 - 60, color=FIELD, sw=1.2, dash="4 4")) # +2.5%
    p.append(line(x0 - 15, y0 + 60, x0 + gw + 15, y0 + 60, color=FIELD, sw=1.2, dash="4 4")) # -2.5%
    p.append(line(x0 - 15, y0 - 110, x0 + gw + 15, y0 - 110, color=MUTED, sw=1.0, dash="2 2")) # +5.0%
    p.append(line(x0 - 15, y0 + 110, x0 + gw + 15, y0 + 110, color=MUTED, sw=1.0, dash="2 2")) # -5.0%

    # Підписи осі Y
    p.append(text(x0 - 20, y0 - 110, "+5.0%", size=10, color=MUTED, anchor="end"))
    p.append(text(x0 - 20, y0 - 60, "+2.5%", size=10.5, bold=True, color=FIELD, anchor="end"))
    p.append(text(x0 - 20, y0 + 5, "0.0%", size=10.5, color=INK, anchor="end"))
    p.append(text(x0 - 20, y0 + 60, "−2.5%", size=10.5, bold=True, color=FIELD, anchor="end"))
    p.append(text(x0 - 20, y0 + 110, "−5.0%", size=10, color=MUTED, anchor="end"))
    p.append(text(x0 - 25, y0 - 130, "Похибка баудрейту", size=11, bold=True, color=INK, anchor="end"))

    # Підписи осі X
    t_points = [
        (x0 + 30,  "-40 °C"),
        (x0 + 130, "-20 °C"),
        (x0 + 260, "0 °C"),
        (x0 + 360, "+25 °C (Калібрування)"),
        (x0 + 490, "+60 °C"),
        (x0 + 580, "+85 °C"),
    ]
    for tx, tlabel in t_points:
        p.append(line(tx, y0 - 120, tx, y0 + 120, color="#e5e9f0", sw=1.0))
        p.append(text(tx, y0 + 138, tlabel, size=10, color=INK, bold=("+25" in tlabel)))

    # Крива температурного дрейфу внутрішнього RC (HSI)
    pts = [
        (x0 + 30, y0 + 105),
        (x0 + 90, y0 + 85),
        (x0 + 130, y0 + 68),
        (x0 + 220, y0 + 20),
        (x0 + 360, y0 - 15), # +25C
        (x0 + 450, y0 - 55),
        (x0 + 490, y0 - 75),
        (x0 + 580, y0 - 95),
    ]
    # Малюємо криву ламаною лінією з товстим штрихом
    for i in range(len(pts) - 1):
        p.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=POS, sw=2.6))
    for px, py in pts:
        p.append(circle(px, py, 4.5, fill=POS, stroke=POS, sw=1.5))

    # Виділення точки калібрування в кімнаті
    p.append(circle(x0 + 360, y0 - 15, 7, fill=FIELD, stroke=FIELD, sw=2.0))
    p.append(text(x0 + 360, y0 - 30, "В кімнаті: похибка +0.6% (OK)", size=10.5, bold=True, color=FIELD))

    # Зони аварії (Framing Error)
    b_err1, _, _ = textbox(x0 + 110, y0 + 100, "⚡ -20 °C: похибка −3.2%\nFraming Error на UART!",
                           size=9.5, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.3, min_w=160)
    p.append(b_err1)

    b_err2, _, _ = textbox(x0 + 520, y0 - 105, "⚡ +60 °C: похибка +3.0%\nВтрата байтів у пакеті!",
                           size=9.5, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.3, min_w=160)
    p.append(b_err2)

    p.append(text(W / 2, 345, "Внутрішній RC-генератор виходить за допустиме вікно зв'язку при екстремальних температурах",
                  size=12, color=INK, italic=True))

    render(os.path.join(OUT, "thermal-drift-uart.svg"), W, H, *p,
           title="Температурний дрейф RC-генератора та вікно стабільності UART")


# ── 4. brownout-transient: імпульсне просідання живлення та сіра зона ──────────
# Ідея: стрибок струму (RF передавач / пуск мотора) створює падіння L*di/dt.
# Якщо напруга потрапляє в "сіру зону" (нижче порогу логіки, але коротше за фільтр BOR),
# мікроконтролер не скидається, а зазнає спотворення пам'яті (HardFault / тихий завис).

def fig_brownout_transient():
    W, H = 820, 390
    p = []

    # Вісь X — час (мкс)
    # Вісь Y — напруга VDD (В)
    x0, y0 = 90, 80
    aw, ah = 680, 240

    p.append(arrow(x0, y0 + ah, x0 + aw + 20, y0 + ah, color=INK, sw=1.8))
    p.append(arrow(x0, y0 + ah, x0, y0 - 20, color=INK, sw=1.8))
    p.append(text(x0 + aw + 15, y0 + ah + 22, "Час (мкс)", size=11, bold=True, color=INK, anchor="end"))
    p.append(text(x0 - 15, y0 - 15, "Напруга V_DD", size=11, bold=True, color=INK, anchor="start"))

    # Рівні напруги
    y_nom = y0 + 30    # 3.3 В
    y_bor = y0 + 110   # 2.7 В (Поріг Brownout Reset)
    y_fail = y0 + 170  # 2.2 В (Поріг гарантованої роботи логіки)

    # Лінії рівнів
    p.append(line(x0, y_nom, x0 + aw, y_nom, color=FIELD, sw=1.2, dash="3 3"))
    p.append(text(x0 - 10, y_nom + 4, "3.3 В (Номінал)", size=10.5, bold=True, color=FIELD, anchor="end"))

    p.append(line(x0, y_bor, x0 + aw, y_bor, color="#e67e22", sw=1.4, dash="4 4"))
    p.append(text(x0 - 10, y_bor + 4, "2.7 В (Поріг BOR)", size=10.5, bold=True, color="#b9770e", anchor="end"))

    p.append(line(x0, y_fail, x0 + aw, y_fail, color=POS, sw=1.4, dash="4 4"))
    p.append(text(x0 - 10, y_fail + 4, "2.2 В (Збій ОЗП / Flash)", size=10.5, bold=True, color=POS, anchor="end"))

    # Заливка небезпечної "сірої зони"
    p.append(rect(x0, y_bor, aw, y_fail - y_bor, fill="#fff8e7", stroke="none"))
    p.append(text(x0 + aw - 15, (y_bor + y_fail) / 2 + 4, "СІРА ЗОНА: апаратне скидання не спрацювало, але пам'ять зіпсовано",
                  size=10.5, bold=True, color="#b9770e", anchor="end"))

    # Форма напруги VDD під час сплеску струму (Wi-Fi TX burst / Motor start)
    p.append(line(x0, y_nom, x0 + 120, y_nom, color=INK, sw=2.2))
    # Стрибок струму вниз
    p.append(line(x0 + 120, y_nom, x0 + 140, y_fail - 15, color=POS, sw=2.6))
    p.append(line(x0 + 140, y_fail - 15, x0 + 180, y_fail - 15, color=POS, sw=2.6))
    # Відновлення
    p.append(line(x0 + 180, y_fail - 15, x0 + 260, y_bor + 20, color=POS, sw=2.2))
    p.append(line(x0 + 260, y_bor + 20, x0 + 380, y_nom, color=INK, sw=2.2))
    p.append(line(x0 + 380, y_nom, x0 + aw, y_nom, color=INK, sw=2.2))

    # Позначка імпульсу струму
    b_tx, _, _ = textbox(x0 + 150, y0 + ah - 40, "Імпульс струму Wi-Fi TX:\nΔI = 400 мА за 10 нс → ΔV = L·(di/dt)",
                         size=10, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.3, min_w=200)
    p.append(b_tx)
    p.append(arrow(x0 + 150, y0 + ah - 65, x0 + 150, y_fail + 5, color=POS, sw=1.5))

    # Пояснення наслідку
    b_res, _, _ = textbox(x0 + 480, y0 + 90, "Тривалість провалу < t_filter (фільтра BOR)\n• Детектор Brownout не встиг скинути ядро\n• Але комірки пам'яті SRAM втратили біти\n→ Наслідок: спонтанний HardFault без логу!",
                          size=10.5, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.4, min_w=310)
    p.append(b_res)

    p.append(text(W / 2, 375, "Мікропросідання напруги від імпульсних навантажень руйнує стан ядра без генерації прапорця BOR",
                  size=12, color=INK, italic=True))

    render(os.path.join(OUT, "brownout-transient.svg"), W, H, *p,
           title="Динамічне просідання живлення VDD: небезпека надшвидких мікропровалів")


if __name__ == "__main__":
    fig_probe_effect()
    fig_pvt_timing()
    fig_thermal_drift()
    fig_brownout_transient()
    print("All figures successfully generated in", OUT)
