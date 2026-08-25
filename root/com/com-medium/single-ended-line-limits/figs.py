# -*- coding: utf-8 -*-
"""Фігури до теми «Межі односторонніх ліній».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Анатомія односторонньої лінії: сигнальний дріт і контур землі ──────────
def fig_single_ended_anatomy():
    W, H = 780, 440
    f = [text(W / 2, 26, "Анатомія односторонньої лінії: струм завжди повертається через землю",
              size=15, bold=True)]

    # Верхній сигнальний провідник
    f.append(text(75, 75, "Передавач (TX)", size=13, bold=True, color=POS, anchor="start"))
    f.append(text(705, 75, "Приймач (RX)", size=13, bold=True, color=NEG, anchor="end"))

    # Блок TX
    f.append(rect(45, 90, 70, 110, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(80, 130, "CMOS", size=11, bold=True, color=POS))
    f.append(text(80, 150, "Driver", size=11, bold=True, color=POS))
    f.append(circle(115, 120, 4, fill=POS, stroke=POS))
    f.append(circle(115, 175, 4, fill=MUTED, stroke=MUTED))

    # Блок RX
    f.append(rect(665, 90, 70, 110, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(700, 130, "CMOS", size=11, bold=True, color=NEG))
    f.append(text(700, 150, "Gate", size=11, bold=True, color=NEG))
    f.append(circle(665, 120, 4, fill=NEG, stroke=NEG))
    f.append(circle(665, 175, 4, fill=MUTED, stroke=MUTED))

    # Сигнальний дріт
    f.append(line(115, 115, 665, 115, color=POS, sw=2.4))
    f.append(text(390, 100, "Сигнальний провідник (доріжка або жила шлейфу)", size=12, bold=True, color=POS))
    f.append(arrow(240, 108, 300, 108, color=POS, sw=1.8))
    f.append(text(270, 96, "I_sig →", size=10, bold=True, color=POS))

    # Розподілені параметри (індуктивності на сигнальній лінії, ємності на землю)
    for lx in (210, 390, 570):
        f.append(line(lx - 15, 115, lx + 15, 115, color="#b03a2e", sw=4.5))
        f.append(text(lx, 130, "L_line", size=10, color="#b03a2e", bold=True))

    # Позначення ємностей на землю (збоку, не перетинаючи текст)
    for cx in (155, 625):
        f.append(line(cx, 115, cx, 140, color=MUTED, sw=1.2))
        f.append(line(cx - 8, 140, cx + 8, 140, color=MUTED, sw=1.6))
        f.append(line(cx - 8, 146, cx + 8, 146, color=MUTED, sw=1.6))
        f.append(line(cx, 146, cx, 185, color=MUTED, sw=1.2))
        f.append(text(cx + 18, 145, "C_line", size=9.5, color=MUTED, anchor="start"))

    # Площина землі
    f.append(line(115, 185, 665, 185, color=MUTED, sw=2.2))
    f.append(text(390, 204, "Опорний провідник землі (GND Plane / Return Path)", size=12, bold=True, color=MUTED))
    f.append(arrow(470, 178, 410, 178, color=MUTED, sw=1.8))
    f.append(text(440, 170, "← I_return", size=10, bold=True, color=MUTED))

    # Підпис контуру струму (між ємностями, без перетину)
    box_loop = fitbox(200, 147, 380, 28, [
        "Контур зворотного струму (визначає паразитну L і чутливість до завад)"
    ], size=9.5, fill="#fff9e6", stroke="#d4ac0d", color="#7d6608")
    f.append(box_loop)

    # Підсумкові блоки пояснення
    b1 = fitbox(45, 225, 330, 95, [
        "Прямий і зворотний струми:",
        "Сигнал існує не сам по собі, а як різниця потенціалів",
        "між доріжкою та землею. Зворотний струм тече",
        "найкоротшим шляхом під доріжкою. Якщо земля",
        "віддалена — площа петлі S зростає, а з нею й L."
    ], size=11, fill="#fdfefe", stroke=LINE)
    f.append(b1)

    b2 = fitbox(405, 225, 330, 95, [
        "Розподілені параметри (L_line, C_line):",
        "Кожен міліметр провідника має власну ємність",
        "на землю (~1 пФ/см) та індуктивність (~5 нГн/см).",
        "Вони формують хвильовий опір Z₀ = √(L/C)",
        "і визначають швидкість поширення сигналу v."
    ], size=11, fill="#fdfefe", stroke=LINE)
    f.append(b2)

    box_bot = fitbox(45, 335, 690, 85, [
        "Головний висновок: Одностороння лінія завжди складається з ДВОХ провідників — сигнального",
        "і опорного (GND). Будь-який розрив полігону землі або довгий тонкий провід GND збільшує площу петлі,",
        "збільшує паразитну індуктивність L_line і перетворює з'єднання на антену для наведення та випромінювання шумів."
    ], size=11.5, fill="#f4f6f8", stroke="#475569")
    f.append(box_bot)

    render(os.path.join(IMG, "single-ended-anatomy.svg"), W, H, *f)


# ── 2. Відбиття хвилі та дзвін (Transmission Line Reflections) ───────────────
def fig_reflections_ringing():
    W, H = 780, 470
    f = [text(W / 2, 26, "Відбиття хвилі в неузгодженій лінії: подвоєння напруги та дзвін (Ringing)",
              size=15, bold=True)]

    # Ліва частина: фізична модель лінії з коефіцієнтами відбиття
    f.append(text(210, 60, "Схема лінії передачі", size=13, bold=True, color=INK))

    # Джерело TX
    f.append(rect(40, 80, 70, 70, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(75, 105, "TX", size=12, bold=True, color=POS))
    f.append(text(75, 125, "R_S ≈ 20Ω", size=10, color=POS))

    # Лінія Z0
    f.append(line(110, 115, 300, 115, color=POS, sw=2.2))
    f.append(line(110, 140, 300, 140, color=MUTED, sw=2.0))
    f.append(text(205, 103, "Лінія Z₀ ≈ 50Ω, час t_prop", size=10.5, color=INK, bold=True))

    # Приймач RX (Open circuit)
    f.append(rect(300, 80, 80, 70, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(340, 105, "RX (Gate)", size=12, bold=True, color=NEG))
    f.append(text(340, 125, "R_L ≈ ∞", size=10, color=NEG))

    # Стрілки хвиль
    f.append(arrow(130, 125, 230, 125, color=POS, sw=1.5))
    f.append(text(180, 137, "Пряма хвиля V_inc", size=9.5, color=POS))

    f.append(arrow(270, 133, 170, 133, color=NEG, sw=1.5))
    f.append(text(220, 147, "← Відбита хвиля (Г_L = +1)", size=9.5, color=NEG))

    # Формули коефіцієнтів відбиття
    fb_gamma = fitbox(40, 165, 340, 80, [
        "Коефіцієнти відбиття (Г = (R - Z₀) / (R + Z₀)):",
        "• На приймачі: R_L = ∞  →  Г_L = +1.0 (напруга подвоюється!)",
        "• На передавачі: R_S = 20Ω, Z₀ = 50Ω  →  Г_S = -0.43 (фаза інвертується)",
        "Хвиля багаторазово відбивається між кінцями за час 2·t_prop."
    ], size=10.5, fill="#fdfefe", stroke=MUTED)
    f.append(fb_gamma)

    # Права частина: осцилограма на приймачі (V(t))
    f.append(text(580, 60, "Напруга на вході приймача V_RX(t)", size=13, bold=True, color=POS))

    ox = 430
    oy = 210
    gw = 310
    gh = 135

    # Осі
    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5))       # t
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5))       # V
    f.append(text(ox + gw - 10, oy + 18, "Час t", size=11, color=LINE))
    f.append(text(ox - 8, oy - gh + 10, "Напруга V", size=11, color=LINE, anchor="end"))

    # Горизонтальні пунктири рівнів напруги
    # V_DD = 3.3 В (y = oy - 80)
    # V_Overshoot = 4.7 В (y = oy - 114)
    # V_Undershoot = -0.8 В (y = oy + 20)
    # V_threshold = 1.65 В (y = oy - 40)
    f.append(line(ox, oy - 80, ox + gw, oy - 80, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(ox - 6, oy - 76, "V_DD (3.3В)", size=10, color=MUTED, anchor="end"))

    f.append(line(ox, oy - 40, ox + gw, oy - 40, color="#d97706", sw=1.0, dash="2,2"))
    f.append(text(ox - 6, oy - 36, "Поріг (1.65В)", size=10, color="#d97706", anchor="end"))

    f.append(line(ox, oy, ox + gw, oy, color=MUTED, sw=1.0))
    f.append(text(ox - 6, oy + 4, "GND (0В)", size=10, color=MUTED, anchor="end"))

    # Траєкторія дзвону (Ringing waveform)
    # 0 -> стрибок на t_prop (x = ox + 35) до 4.6V -> спад на 3*t_prop (x = ox + 85) до 2.5V -> підйом на 5*t_prop (x = ox + 135) до 3.7V -> стабілізація на 3.3V
    pts = [
        (ox, oy),
        (ox + 35, oy),
        (ox + 42, oy - 115),   # Overshoot (+4.7V)
        (ox + 70, oy - 100),
        (ox + 90, oy - 55),    # Провал нижче V_DD
        (ox + 120, oy - 62),
        (ox + 145, oy - 92),   # Другий закид
        (ox + 180, oy - 76),
        (ox + 210, oy - 82),
        (ox + 250, oy - 80),
        (ox + gw - 10, oy - 80)
    ]
    path_d = ["M %.1f,%.1f" % pts[0]]
    for px, py in pts[1:]:
        path_d.append("L %.1f,%.1f" % (px, py))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(path_d), POS))

    # Підписи аномалій на графіку
    f.append(text(ox + 65, oy - 122, "Закид (Overshoot > 4.7В)", size=10, color=POS, bold=True))
    f.append(arrow(ox + 65, oy - 118, ox + 45, oy - 114, color=POS, sw=1.2))

    f.append(text(ox + 115, oy - 20, "Провал (Undershoot)", size=10, color=NEG, bold=True))
    f.append(arrow(ox + 115, oy - 32, ox + 92, oy - 53, color=NEG, sw=1.2))

    f.append(text(ox + 195, oy - 100, "Дзвін (Ringing)", size=10, color="#b45309", bold=True))

    # Мітки часу t_prop, 2 t_prop, 3 t_prop
    f.append(line(ox + 40, oy - 4, ox + 40, oy + 4, color=LINE, sw=1.5))
    f.append(text(ox + 40, oy + 16, "t_prop", size=9, color=MUTED))

    f.append(line(ox + 90, oy - 4, ox + 90, oy + 4, color=LINE, sw=1.5))
    f.append(text(ox + 90, oy + 16, "3·t_prop", size=9, color=MUTED))

    f.append(line(ox + 145, oy - 4, ox + 145, oy + 4, color=LINE, sw=1.5))
    f.append(text(ox + 145, oy + 16, "5·t_prop", size=9, color=MUTED))

    # Нижній блок висновку
    box_ring = fitbox(40, 260, 340, 95, [
        "Небезпеки перенапруг та дзвону:",
        "1. Пробій затворів та спрацьовування ESD-діодів чіпа.",
        "2. Ризик замикання живлення (CMOS Latch-up).",
        "3. Хибне спрацьовування тригерів Шмітта при спаданні",
        "   хвилі через логічний поріг (Double Clocking в SPI)."
    ], size=10.5, fill="#fff1f2", stroke=POS)
    f.append(box_ring)

    box_bot = fitbox(40, 370, 700, 85, [
        "Умова виникнення відбиттів: якщо час наростання фронту t_rise < 2 · t_prop (де t_prop = довжина / швидкість),",
        "лінія працює в режимі довгої лінії передачі. Навіть на низькій частоті обміну (100 кГц) крутий фронт мікроконтролера",
        "(t_rise ≈ 1.5 нс) викликає сильний дзвін на доріжках довжиною понад 10–12 см."
    ], size=11, fill="#f4f6f8", stroke="#475569")
    f.append(box_bot)

    render(os.path.join(IMG, "reflections-ringing.svg"), W, H, *f)


# ── 3. Перехресні наведення та підстрибування землі ──────────────────────────
def fig_crosstalk_groundbounce():
    W, H = 780, 460
    f = [text(W / 2, 26, "Паразитні зв'язки: перехресні наведення (Crosstalk) та підстрибування землі (SSN)",
              size=15, bold=True)]

    # Ліва половина: Перехресні наведення (Crosstalk)
    f.append(text(195, 58, "1. Наведення між лініями (Crosstalk)", size=13, bold=True, color=POS))

    # Агресор і жертва
    f.append(line(45, 95, 345, 95, color=POS, sw=2.4))
    f.append(text(45, 85, "Агресор (швидкий фронт dV/dt, di/dt)", size=10.5, bold=True, color=POS, anchor="start"))

    f.append(line(45, 160, 345, 160, color=NEG, sw=2.4))
    f.append(text(45, 180, "Жертва (тиха лінія '0' або '1')", size=10.5, bold=True, color=NEG, anchor="start"))

    # Ємнісний зв'язок Cm
    f.append(line(140, 95, 140, 120, color="#b03a2e", sw=1.2))
    f.append(line(130, 120, 150, 120, color="#b03a2e", sw=1.6))
    f.append(line(130, 126, 150, 126, color="#b03a2e", sw=1.6))
    f.append(line(140, 126, 140, 160, color="#b03a2e", sw=1.2))
    f.append(text(160, 125, "C_m (ємнісний струм i = C_m·dV/dt)", size=9.5, color="#b03a2e", anchor="start"))

    # Індуктивний зв'язок Lm
    f.append(circle(260, 127, 10, fill="none", stroke="#b03a2e", sw=1.4))
    f.append(text(260, 131, "M", size=10, bold=True, color="#b03a2e"))
    f.append(text(278, 125, "L_m (ЕРС v = L_m·di/dt)", size=9.5, color="#b03a2e", anchor="start"))

    # Сплеск на лінії-жертві
    f.append(line(45, 220, 170, 220, color=NEG, sw=1.8))
    f.append(line(170, 220, 190, 195, color=POS, sw=2.0))
    f.append(line(190, 195, 210, 220, color=POS, sw=2.0))
    f.append(line(210, 220, 345, 220, color=NEG, sw=1.8))
    f.append(text(195, 185, "Хибний імпульс (Glitch)!", size=10, bold=True, color=POS))

    # Права половина: Підстрибування землі (Ground Bounce / SSN)
    f.append(text(585, 58, "2. Підстрибування землі (Ground Bounce)", size=13, bold=True, color=NEG))

    # Чіп
    f.append(rect(430, 85, 150, 125, fill="#f8fafc", stroke=LINE, sw=1.5))
    f.append(text(505, 105, "Мікроконтролер (IC)", size=11, bold=True, color=INK))

    # N ліній перемикаються
    for ly in (125, 145, 165):
        f.append(line(580, ly, 710, ly, color=POS, sw=1.8))
        f.append(arrow(670, ly, 610, ly, color=POS, sw=1.4))
    f.append(text(645, 115, "N ліній: '1' → '0'", size=10, bold=True, color=POS))
    f.append(text(645, 182, "Сумарний струм N · di/dt", size=9.5, color=POS))

    # Внутрішня земля чіпа та індуктивність виводу
    f.append(line(480, 190, 480, 210, color=MUTED, sw=2.0))
    f.append(line(472, 210, 488, 210, color="#7c3aed", sw=3.5)) # L_pkg
    f.append(text(500, 215, "L_pkg (1–5 нГн)", size=10, bold=True, color="#7c3aed", anchor="start"))
    f.append(line(480, 215, 480, 235, color=MUTED, sw=2.0))
    f.append(line(460, 235, 500, 235, color=MUTED, sw=2.5)) # PCB GND

    f.append(text(505, 150, "GND_die ≠ GND_pcb", size=10, bold=True, color=POS))
    f.append(text(505, 168, "V_bounce = N·L·(di/dt)", size=10.5, bold=True, color=POS))

    # Розділювач між лівою і правою частиною
    f.append(line(390, 50, 390, 260, color="#cbd5e1", sw=1.2, dash="4,4"))

    # Нижні пояснювальні блоки
    b_left = fitbox(45, 265, 330, 85, [
        "Захист від перехресних наведень:",
        "• Правило 3W (відстань між трасами ≥ 3 ширини).",
        "• Копланарне екранування (доріжка землі між лініями).",
        "• Чергування сигнальних жил і землі в шлейфі (S-G-S-G)."
    ], size=10.5, fill="#fdfefe", stroke=MUTED)
    f.append(b_left)

    b_right = fitbox(405, 265, 330, 85, [
        "Захист від підстрибування землі:",
        "• Блокувальні керамічні конденсатори впритул до чіпа.",
        "• Кілька виводів GND у корпусі паралельно (BGA/QFN).",
        "• Програмне обмеження швидкості наростання (Slew Rate)."
    ], size=10.5, fill="#fdfefe", stroke=MUTED)
    f.append(b_right)

    box_bot = fitbox(45, 365, 690, 80, [
        "Спільний наслідок: І Crosstalk, і Ground Bounce створюють хибні сплески напруги на спокійних лініях.",
        "Якщо сплеск перевищує поріг логічного перемикання V_IL (зазвичай ~0.8 В для 3.3 В логіки),",
        "мікроконтролер фіксує фантомне переривання або бітову помилку в сусідньому інтерфейсі."
    ], size=11, fill="#f4f6f8", stroke="#475569")
    f.append(box_bot)

    render(os.path.join(IMG, "crosstalk-groundbounce.svg"), W, H, *f)


# ── 4. Послідовне узгодження на передавачі (Source Series Termination) ───────
def fig_source_termination():
    W, H = 780, 450
    f = [text(W / 2, 26, "Послідовне резистивне узгодження на передавачі (Source Series Termination)",
              size=15, bold=True)]

    # Схема з резистором R_term
    f.append(text(120, 65, "Джерело TX", size=12, bold=True, color=POS))
    f.append(rect(45, 80, 65, 80, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(77, 110, "TX", size=12, bold=True, color=POS))
    f.append(text(77, 130, "R_S ≈ 20Ω", size=9.5, color=POS))

    # Резистор узгодження R_term
    f.append(rect(135, 105, 55, 30, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=3))
    f.append(text(162, 124, "R_term", size=11, bold=True, color="#92400e"))
    f.append(line(110, 120, 135, 120, color=POS, sw=2.0))
    f.append(line(190, 120, 220, 120, color=POS, sw=2.0))
    f.append(text(162, 95, "R_S + R_term = Z₀ (50Ω)", size=10, bold=True, color="#92400e"))

    # Лінія Z0
    f.append(line(220, 120, 520, 120, color=POS, sw=2.2))
    f.append(line(45, 150, 590, 150, color=MUTED, sw=2.0))
    f.append(text(370, 108, "Довга лінія Z₀ = 50Ω, час затримки t_prop", size=10.5, color=INK, bold=True))

    # Приймач RX (Open circuit)
    f.append(rect(520, 80, 75, 80, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(557, 110, "RX (Gate)", size=12, bold=True, color=NEG))
    f.append(text(557, 130, "R_L ≈ ∞", size=9.5, color=NEG))

    # Покроковий рух хвилі
    # Крок 1: на виході дільника біжить хвиля V_DD / 2
    f.append(arrow(240, 132, 330, 132, color=POS, sw=1.6))
    f.append(text(285, 144, "1. Пряма хвиля V = V_DD / 2 (1.65В)", size=9.5, color=POS, bold=True))

    # Крок 2: подвоєння на кінці до V_DD
    f.append(text(605, 115, "2. На кінці RX:", size=10, bold=True, color=NEG, anchor="start"))
    f.append(text(605, 130, "Г_L = +1.0", size=10, color=NEG, anchor="start"))
    f.append(text(605, 145, "V = 2 · (V_DD/2) = V_DD", size=10, bold=True, color=NEG, anchor="start"))

    # Крок 3: зворотна хвиля повертається на джерело й гаситься
    f.append(arrow(470, 138, 380, 138, color=MUTED, sw=1.6))
    f.append(text(425, 150, "3. Відбита хвиля повертається ←", size=9.5, color=MUTED))

    # Графіки: Без узгодження проти З узгодженням
    # 1. Графік без узгодження (зліва)
    gx1, gy1 = 70, 290
    gw, gh = 270, 95
    f.append(text(gx1 + gw / 2, gy1 - gh - 12, "БЕЗ узгодження (R_term = 0)", size=12, bold=True, color=POS))
    f.append(line(gx1, gy1, gx1 + gw, gy1, color=LINE, sw=1.2))
    f.append(line(gx1, gy1, gx1, gy1 - gh, color=LINE, sw=1.2))
    f.append(line(gx1, gy1 - 60, gx1 + gw, gy1 - 60, color=MUTED, sw=0.8, dash="2,2"))
    f.append(text(gx1 - 5, gy1 - 57, "3.3В", size=9, color=MUTED, anchor="end"))

    # Хвиля з сильним дзвоном
    w_bad = [
        (gx1, gy1), (gx1 + 30, gy1), (gx1 + 36, gy1 - 90), (gx1 + 65, gy1 - 40),
        (gx1 + 95, gy1 - 75), (gx1 + 130, gy1 - 55), (gx1 + 170, gy1 - 62),
        (gx1 + 210, gy1 - 60), (gx1 + gw - 5, gy1 - 60)
    ]
    pd_bad = ["M %.1f,%.1f" % w_bad[0]]
    for px, py in w_bad[1:]: pd_bad.append("L %.1f,%.1f" % (px, py))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pd_bad), POS))
    f.append(text(gx1 + 120, gy1 - 85, "Дзвін та перенапруга", size=10, color=POS, italic=True))

    # 2. Графік з узгодженням (справа)
    gx2, gy2 = 440, 290
    f.append(text(gx2 + gw / 2, gy2 - gh - 12, "З ПОСЛІДОВНИМ узгодженням (R_term = 30Ω)", size=12, bold=True, color=FIELD))
    f.append(line(gx2, gy2, gx2 + gw, gy2, color=LINE, sw=1.2))
    f.append(line(gx2, gy2, gx2, gy2 - gh, color=LINE, sw=1.2))
    f.append(line(gx2, gy2 - 60, gx2 + gw, gy2 - 60, color=MUTED, sw=0.8, dash="2,2"))
    f.append(text(gx2 - 5, gy2 - 57, "3.3В", size=9, color=MUTED, anchor="end"))

    # Ідеальна сходинка
    w_good = [
        (gx2, gy2), (gx2 + 30, gy2), (gx2 + 42, gy2 - 60),
        (gx2 + gw - 5, gy2 - 60)
    ]
    pd_good = ["M %.1f,%.1f" % w_good[0]]
    for px, py in w_good[1:]: pd_good.append("L %.1f,%.1f" % (px, py))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pd_good), FIELD))
    f.append(text(gx2 + 130, gy2 - 70, "Чистий плаский фронт без коливань", size=10, color=FIELD, italic=True))

    # Нижній блок
    box_bot = fitbox(45, 325, 690, 105, [
        "Чому послідовне узгодження ідеальне для односторонніх ліній (SPI SCK, UART TX):",
        "1. Нульове постійне споживання струму: на приймачі стоїть розімкнене коло (R_L ≈ ∞), тому струм тече лише під час перемикання.",
        "2. Повне поглинання відбиття: на боці передавача загальний опір дорівнює Z₀, тож коефіцієнт відбиття Г_S = 0.",
        "3. Правило розміщення: резистор R_term повинен стояти ЯКНАЙБЛИЖЧЕ до виводу мікроконтролера (TX/SCK), до початку довгої лінії."
    ], size=11, fill="#f4f6f8", stroke="#475569")
    f.append(box_bot)

    render(os.path.join(IMG, "source-termination.svg"), W, H, *f)


if __name__ == "__main__":
    fig_single_ended_anatomy()
    fig_reflections_ringing()
    fig_crosstalk_groundbounce()
    fig_source_termination()
    print("Всі фігури згенеровано успішно.")
