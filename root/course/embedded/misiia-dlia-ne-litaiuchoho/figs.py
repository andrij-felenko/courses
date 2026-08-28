# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорові маркери стрілок
COL_MARKERS = (
    '<defs>'
    '<marker id="arrB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '</defs>' % (NEG, FIELD, POS)
)

def carrow(x1, y1, x2, y2, color, mid, sw=2.0):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arr%s)" stroke-linecap="round"/>'
            % (x1, y1, x2, y2, color, sw, mid))

def block(x, y, w, h, lines, fill, stroke, color=INK, size=12.0, bold=True):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=8)
    n = len(lines)
    cy = y + h / 2 - (n - 1) * size * 1.25 / 2 + size * 0.35
    out += mtext(x + w / 2, cy, lines, size=size, color=color, bold=bold)
    return out


# ── 1. nonholonomic-kinematics: Коптер проти Аккермана проти Човна ─────────────
def fig_nonholonomic_kinematics():
    W, H = 960, 480
    p = [COL_MARKERS]
    p.append(text(W / 2, 34, "Голономний літальний апарат проти неголономних наземних та водних платформ",
                  size=14, color=INK, bold=True))
    p.append(text(W / 2, 54, "різниця в ступенях вільності, бічному ковзанні та обмеженнях радіуса розвороту",
                  size=12, color=MUTED))

    # Три панелі
    pw, ph = 280, 360
    y0 = 76

    # Панель 1: Коптер (Голономний у 2D/3D)
    x1 = 30
    p.append(rect(x1, y0, pw, ph, fill="#f8fafc", stroke=NEG, sw=1.6, rx=10))
    p.append(text(x1 + pw / 2, y0 + 26, "КОПТЕР (3D/2D)", size=13, color=NEG, bold=True))
    p.append(text(x1 + pw / 2, y0 + 44, "Голономний рух у площині", size=11, color=MUTED))

    # Схема коптера в центрі панелі
    cx1, cy1 = x1 + pw / 2, y0 + 150
    p.append(circle(cx1, cy1, 24, fill="#eef2ff", stroke=NEG, sw=1.8))
    p.append(text(cx1, cy1 + 4, "ДРОН", size=10, color=NEG, bold=True))
    # Вектори руху в усі 4 боки
    p.append(carrow(cx1, cy1 - 26, cx1, cy1 - 70, NEG, "B", 2.0))
    p.append(carrow(cx1, cy1 + 26, cx1, cy1 + 70, NEG, "B", 2.0))
    p.append(carrow(cx1 - 26, cy1, cx1 - 70, cy1, NEG, "B", 2.0))
    p.append(carrow(cx1 + 26, cy1, cx1 + 70, cy1, NEG, "B", 2.0))
    p.append(text(cx1, cy1 - 76, "+Vx (вперед)", size=9.5, color=NEG))
    p.append(text(cx1 + 76, cy1 + 4, "+Vy (лаг)", size=9.5, color=NEG, anchor="start"))
    p.append(text(cx1, cy1 + 84, "−Vx (назад)", size=9.5, color=NEG))
    p.append(text(cx1 - 76, cy1 + 4, "−Vy (лаг)", size=9.5, color=NEG, anchor="end"))

    # Опис властивостей коптера
    desc1 = [
        "• Може зависнути на місці (V = 0)",
        "• Рух у будь-який бік без розвороту",
        "• Висота Z — вільний вимір",
        "• Немає радіуса розвороту (R = 0)"
    ]
    for i, line_txt in enumerate(desc1):
        p.append(text(x1 + 14, y0 + 265 + i * 20, line_txt, size=10.5, color=INK, anchor="start"))

    # Панель 2: Ровер Аккермана
    x2 = 340
    p.append(rect(x2, y0, pw, ph, fill="#fdfbf7", stroke="#d98a00", sw=1.6, rx=10))
    p.append(text(x2 + pw / 2, y0 + 26, "РОВЕР АККЕРМАНА (2D)", size=13, color="#d98a00", bold=True))
    p.append(text(x2 + pw / 2, y0 + 44, "Неголономне кермування", size=11, color=MUTED))

    # Схема авто
    cx2, cy2 = x2 + pw / 2, y0 + 150
    # Кузов
    p.append(rect(cx2 - 20, cy2 - 40, 40, 75, fill="#fff7e6", stroke="#d98a00", sw=1.8, rx=5))
    # Задні колеса (прямі)
    p.append(rect(cx2 - 26, cy2 + 15, 8, 20, fill=INK, stroke=INK, sw=1.0, rx=2))
    p.append(rect(cx2 + 18, cy2 + 15, 8, 20, fill=INK, stroke=INK, sw=1.0, rx=2))
    # Передні колеса (повернуті)
    p.append('<rect x="%d" y="%d" width="8" height="20" rx="2" fill="%s" stroke="%s" transform="rotate(25 %d %d)"/>'
             % (cx2 - 26, cy2 - 35, INK, INK, cx2 - 22, cy2 - 25))
    p.append('<rect x="%d" y="%d" width="8" height="20" rx="2" fill="%s" stroke="%s" transform="rotate(25 %d %d)"/>'
             % (cx2 + 18, cy2 - 35, INK, INK, cx2 + 22, cy2 - 25))
    # Вектор швидкості вперед та заборона вбік
    p.append(carrow(cx2, cy2 - 42, cx2, cy2 - 80, "#d98a00", "B", 2.0))
    p.append(text(cx2, cy2 - 86, "Vx (тільки поздовжнє)", size=9.5, color="#d98a00"))
    # Червоний хрестик на бічній швидкості
    p.append(line(cx2 + 25, cy2, cx2 + 65, cy2, color=POS, sw=2.0))
    p.append(text(cx2 + 70, cy2 + 4, "Vy = 0 (заборонено)", size=9.5, color=POS, anchor="start"))
    # Дуга мінімального радіуса
    p.append('<path d="M %d %d A 45 45 0 0 1 %d %d" fill="none" stroke="%s" stroke-dasharray="4,3" stroke-width="1.6"/>'
             % (cx2, cy2 - 40, cx2 + 45, cy2 + 5, MUTED))
    p.append(text(cx2 + 52, cy2 - 20, "R_min", size=10, color=MUTED, italic=True))

    desc2 = [
        "• Бокове ковзання відсутнє (Vy = 0)",
        "• Мінімальний радіус R_min = L/tan(δ)",
        "• Не може крутитися на місці",
        "• Потрібен триточковий розворот"
    ]
    for i, line_txt in enumerate(desc2):
        p.append(text(x2 + 14, y0 + 265 + i * 20, line_txt, size=10.5, color=INK, anchor="start"))

    # Панель 3: Водний апарат (Човен / USV)
    x3 = 650
    p.append(rect(x3, y0, pw, ph, fill="#f0fdf4", stroke=FIELD, sw=1.6, rx=10))
    p.append(text(x3 + pw / 2, y0 + 26, "ВОДНИЙ ЧОВЕН / USV", size=13, color=FIELD, bold=True))
    p.append(text(x3 + pw / 2, y0 + 44, "Гідродинаміка й кермо", size=11, color=MUTED))

    # Схема човна
    cx3, cy3 = x3 + pw / 2, y0 + 150
    # Корпус човна (загострений спереду)
    hull = "M %d %d Q %d %d %d %d L %d %d L %d %d Q %d %d %d %d Z" % (
        cx3, cy3 - 48,
        cx3 + 22, cy3 - 10, cx3 + 20, cy3 + 30,
        cx3 - 20, cy3 + 30,
        cx3 - 20, cy3 + 30,
        cx3 - 22, cy3 - 10, cx3, cy3 - 48
    )
    p.append('<path d="%s" fill="#dcfce7" stroke="%s" stroke-width="1.8"/>' % (hull, FIELD))
    # Гвинт ззаду
    p.append(rect(cx3 - 4, cy3 + 32, 8, 12, fill=INK, stroke=INK, sw=1.0, rx=1))
    # Перо керма з кутом
    p.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="3.0"/>'
             % (cx3, cy3 + 44, cx3 + 12, cy3 + 60, POS))
    p.append(text(cx3 + 18, cy3 + 60, "кермо", size=9.5, color=POS, anchor="start"))
    # Вектор течії збоку (дрейф)
    p.append(carrow(cx3 - 75, cy3 - 10, cx3 - 32, cy3 - 10, NEG, "B", 1.8))
    p.append(text(cx3 - 78, cy3 - 15, "течія / дрейф", size=9.5, color=NEG, anchor="start"))
    # Тяга вперед
    p.append(carrow(cx3, cy3 - 52, cx3, cy3 - 86, FIELD, "G", 2.0))
    p.append(text(cx3, cy3 - 92, "Тяга гвинта", size=9.5, color=FIELD))

    desc3 = [
        "• Кермо діє лише на ходу (V > 0)",
        "• Знесення течією та вітром (кут дрейфу β)",
        "• Величезна інерція та відсутність гальм",
        "• Не може зависнути без тяги гвинтів"
    ]
    for i, line_txt in enumerate(desc3):
        p.append(text(x3 + 14, y0 + 265 + i * 20, line_txt, size=10.5, color=INK, anchor="start"))

    p.append(text(W / 2, 460,
                  "Наземні та водні місії визначаються неголономною кінематикою: траєкторію не можна планувати як прямі відрізки без урахування розвороту й дрейфу.",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "nonholonomic-kinematics.svg"), W, H, *p,
           title="Кінематичні відмінності платформ: 3D дрон, ровер Аккермана та човен")


# ── 2. virtual-anchor: Віртуальний якір (Station Keeping) ──────────────────────
def fig_virtual_anchor():
    W, H = 940, 500
    p = [COL_MARKERS]
    p.append(text(W / 2, 34, "Утримання позиції на воді (Virtual Anchor) без перегріву моторів",
                  size=14, color=INK, bold=True))
    p.append(text(W / 2, 54, "орієнтація носа проти панівної сили, зона мертвого ходу (deadband) та імпульсна тяга",
                  size=12, color=MUTED))

    # Ліва частина: Геометрія сил та зон
    ox, oy = 280, 265
    r_in = 75
    r_out = 150

    # Зовнішнє коло (зона утримання / повернення)
    p.append(circle(ox, oy, r_out, fill="#fef2f2", stroke=POS, sw=1.6))
    p.append(text(ox, oy - r_out - 10, "Зовнішній радіус R_outer (активне повернення)", size=10.5, color=POS, bold=True))

    # Внутрішнє коло (мертва зона / дрейф)
    p.append(circle(ox, oy, r_in, fill="#f0fdf4", stroke=FIELD, sw=1.6))
    p.append(text(ox, oy - r_in - 8, "Мертва зона R_inner (мотори ВИМК)", size=10.5, color=FIELD, bold=True))

    # Цільова точка в центрі
    p.append(circle(ox, oy, 4, fill=INK, stroke=INK, sw=1.5))
    p.append(text(ox + 8, oy + 4, "Ціль (Waypoint)", size=10, color=INK, anchor="start", bold=True))

    # Вектор панівної сили (течія + вітер)
    p.append(carrow(ox - 180, oy - 140, ox - 180, oy + 80, NEG, "B", 2.6))
    p.append(text(ox - 180, oy - 148, "Сумарний вектор", size=11, color=NEG, bold=True))
    p.append(text(ox - 180, oy - 134, "течії й вітру (F_env)", size=10.5, color=NEG))

    # Човен всередині зони (правильно зорієнтований носом догори проти течії)
    bx, by = ox + 15, oy + 35
    hull = "M %d %d Q %d %d %d %d L %d %d L %d %d Q %d %d %d %d Z" % (
        bx, by - 32,
        bx + 14, by - 6, bx + 12, by + 20,
        bx - 12, by + 20,
        bx - 12, by + 20,
        bx - 14, by - 6, bx, by - 32
    )
    p.append('<path d="%s" fill="#ffffff" stroke="%s" stroke-width="1.8"/>' % (hull, INK))
    p.append(circle(bx, by, 3, fill=POS, stroke=POS, sw=1.0))

    # Вектор тяги вперед (короткий імпульс)
    p.append(carrow(bx, by - 34, bx, by - 68, FIELD, "G", 2.2))
    p.append(text(bx + 8, by - 52, "Імпульс тяги", size=10, color=FIELD, anchor="start", bold=True))

    # Стрілка знесення човна назад при вимкнених моторах
    p.append(carrow(bx, by + 22, bx, by + 50, NEG, "B", 1.8))
    p.append(text(bx + 8, by + 42, "вільний дрейф", size=9.5, color=NEG, anchor="start"))

    # Права частина: Порівняння підходів та таймінги
    rx = 570
    p.append(rect(rx, 86, 340, 180, fill="#fff5f5", stroke=POS, sw=1.4, rx=8))
    p.append(text(rx + 170, 110, "✗ НАЇВНИЙ ПІД-РЕГУЛЯТОР", size=12, color=POS, bold=True))
    bad_lines = [
        "• Мотори вмикаються на кожне коливання ±5 см",
        "• Постійна зміна напрямку гвинтів (реверс)",
        "• Струмове навантаження > 80% часу",
        "• Результат: перегрів ESC і розряд АКБ за 15 хв"
    ]
    for i, l in enumerate(bad_lines):
        p.append(text(rx + 16, 134 + i * 22, l, size=10.5, color=INK, anchor="start"))

    p.append(rect(rx, 280, 340, 180, fill="#f0fdf4", stroke=FIELD, sw=1.4, rx=8))
    p.append(text(rx + 170, 304, "✓ ДВОЗОННИЙ ВІРТУАЛЬНИЙ ЯКІР", size=12, color=FIELD, bold=True))
    good_lines = [
        "• 1. Курс фіксується суворо назустріч течії",
        "• 2. У зоні R_inner мотори вимкнені (дрейф)",
        "• 3. На межі R_outer — імпульс тяги 3..5 с",
        "• 4. Шпаруватість (duty cycle) < 20% часу",
        "• Результат: робота годинами без перегріву"
    ]
    for i, l in enumerate(good_lines):
        p.append(text(rx + 16, 328 + i * 22, l, size=10.5, color=INK, anchor="start"))

    p.append(text(W / 2, 480,
                  "Ключовий принцип віртуального якоря: мінімізувати опір носом проти течії й використовувати дрейф у мертвій зоні замість постійного гудіння моторами.",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "virtual-anchor.svg"), W, H, *p,
           title="Утримання точки на воді: орієнтація носа за течією та гістерезис мертвої зони")


# ── 3. rover-odometry-fusion: Ровер у каньйоні й виявлення буксування ──────────
def fig_rover_odometry_fusion():
    W, H = 940, 480
    p = [COL_MARKERS]
    p.append(text(W / 2, 34, "Навігація ровера: злиття одометрії та захист від пробуксовки",
                  size=14, color=INK, bold=True))
    p.append(text(W / 2, 54, "багатопроменевий GNSS у місті проти колісних енкодерів та перевірка через IMU",
                  size=12, color=MUTED))

    # Верхній блок: Проблема в міському каньйоні
    p.append(rect(40, 76, 860, 110, fill="#f8fafc", stroke=MUTED, sw=1.4, rx=8))
    p.append(text(60, 98, "МІСЬКИЙ КАНЬЙОН ТА ПЕРЕШКОДИ (Multipath & Shadowing)", size=12, color=INK, anchor="start", bold=True))

    # Три джерела даних
    p.append(rect(60, 112, 240, 60, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
    p.append(text(180, 132, "GNSS (Супутники)", size=11.5, color=POS, bold=True))
    p.append(text(180, 152, "Стрибки позиції ±15 м від стін", size=10, color=MUTED))

    p.append(rect(350, 112, 240, 60, fill="#fffbf0", stroke="#d98a00", sw=1.2, rx=6))
    p.append(text(470, 132, "Енкодери коліс", size=11.5, color="#d98a00", bold=True))
    p.append(text(470, 152, "Точні кроки, але брешуть при буксуванні", size=10, color=MUTED))

    p.append(rect(640, 112, 240, 60, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(760, 132, "IMU (Акселерометр/Гіроскоп)", size=11.5, color=FIELD, bold=True))
    p.append(text(760, 152, "Швидкий відгук, дрейф інтеграла", size=10, color=MUTED))

    # Нижній блок: Логіка детектора буксування (Cross-Check)
    y_cc = 206
    p.append(rect(40, y_cc, 860, 234, fill="#ffffff", stroke=INK, sw=1.5, rx=8))
    p.append(text(W / 2, y_cc + 24, "МЕХАНІЗМ ДЕТЕКЦІЇ ПРОБУКСОВКИ (WHEEL SLIP DETECTION)", size=13, color=INK, bold=True))

    # Схема крос-валідації
    # Блок енкодерів
    p.append(rect(60, y_cc + 50, 220, 70, fill="#fffbf0", stroke="#d98a00", sw=1.4, rx=6))
    p.append(text(170, y_cc + 74, "Диференціал коліс", size=11.5, color="#d98a00", bold=True))
    p.append(text(170, y_cc + 92, "a_wheel = d(V_wheel)/dt", size=11, color=INK))
    p.append(text(170, y_cc + 108, "ω_wheel = (Vr − Vl) / B", size=10.5, color=MUTED))

    # Блок IMU
    p.append(rect(60, y_cc + 140, 220, 70, fill="#f0fdf4", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(170, y_cc + 164, "Датчики IMU", size=11.5, color=FIELD, bold=True))
    p.append(text(170, y_cc + 182, "a_imu = Accel_X (поздовжнє)", size=11, color=INK))
    p.append(text(170, y_cc + 198, "ω_imu = Gyro_Z (курс)", size=10.5, color=MUTED))

    # Порівняльний компаратор
    p.append(carrow(280, y_cc + 85, 340, y_cc + 120, "#d98a00", "B", 2.0))
    p.append(carrow(280, y_cc + 175, 340, y_cc + 140, FIELD, "G", 2.0))

    p.append(rect(345, y_cc + 95, 200, 70, fill="#f4f4f5", stroke=INK, sw=1.6, rx=8))
    p.append(text(445, y_cc + 120, "КОМПАРАТОР", size=12, color=INK, bold=True))
    p.append(text(445, y_cc + 140, "|a_wheel − a_imu| > ε", size=11.5, color=POS, bold=True))
    p.append(text(445, y_cc + 154, "або |ω_wheel − ω_imu| > δ", size=10, color=MUTED))

    # Рішення: Буксування виявлено
    p.append(carrow(545, y_cc + 130, 605, y_cc + 130, POS, "R", 2.2))

    p.append(rect(610, y_cc + 60, 270, 140, fill="#fff5f5", stroke=POS, sw=1.6, rx=8))
    p.append(text(745, y_cc + 84, "РЕАКЦІЯ АВТОПІЛОТА", size=12, color=POS, bold=True))
    react_lines = [
        "1. Зменшити вагу одометрії в EKF",
        "2. Перехід на інерційне ведення",
        "3. Обмеження крутного моменту",
        "4. Якщо V_wheel > 0, а a_imu = 0",
        "   → статус STUCK (застрягання)"
    ]
    for i, rl in enumerate(react_lines):
        p.append(text(624, y_cc + 106 + i * 18, rl, size=10, color=INK, anchor="start"))

    p.append(text(W / 2, 460,
                  "Істинний рух підтверджується лише тоді, коли енкодери узгоджені з акселерометром та гіроскопом. Розбіжність сигналізує про пробуксовку або лід.",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "rover-odometry-fusion.svg"), W, H, *p,
           title="Комплексування навігації ровера та алгоритм виявлення пробуксовки коліс")


# ── 4. stationary-schedule-fsm: Автомат стаціонарної місії ────────────────────
def fig_stationary_schedule_fsm():
    W, H = 940, 480
    p = [COL_MARKERS]
    p.append(text(W / 2, 34, "Автомат місії стаціонарного пристрою: сон, події та безпека",
                  size=14, color=INK, bold=True))
    p.append(text(W / 2, 54, "енергоощадний цикл сонячного трекера, поливальної системи та промивки фільтрів",
                  size=12, color=MUTED))

    # Схема автомата станів стаціонарної місії
    # 4 основні стани
    y_m = 160
    bw, bh = 180, 80

    # Стан 1: DEEP SLEEP
    s1_x = 40
    p.append(block(s1_x, y_m, bw, bh, ["ГЛИБОКИЙ СОН", "(DEEP SLEEP)", "I < 15 мкА, периферія вимк"],
                   "#f4f4f5", INK, size=11))

    # Стан 2: WAKE & SAMPLE
    s2_x = 260
    p.append(block(s2_x, y_m, bw, bh, ["ОПИТУВАННЯ ДАВАЧІВ", "(WAKE & SAMPLE)", "RTC, вологість, тиск, кут"],
                   "#eef2ff", NEG, size=11))

    # Стан 3: EVALUATE & ACTUATE
    s3_x = 490
    p.append(block(s3_x, y_m, bw, bh, ["ВИКОНАННЯ ДІЇ", "(ACTUATE)", "помпа, клапан, сервопривід"],
                   "#eafaef", FIELD, size=11))

    # Стан 4: VERIFY & SAFE
    s4_x = 720
    p.append(block(s4_x, y_m, bw, bh, ["КОНТРОЛЬ БЕЗПЕКИ", "(VERIFY & SAFE)", "струм мотора, прорив труби"],
                   "#fff5e6", "#d98a00", size=11))

    # Переходи вперед
    p.append(carrow(s1_x + bw, y_m + 30, s2_x, y_m + 30, NEG, "B", 2.0))
    p.append(text(s1_x + bw + 20, y_m + 20, "RTC таймер", size=9.5, color=NEG))

    p.append(carrow(s2_x + bw, y_m + 30, s3_x, y_m + 30, FIELD, "G", 2.0))
    p.append(text(s2_x + bw + 25, y_m + 20, "Поріг досягнуто", size=9.5, color=FIELD))

    p.append(carrow(s3_x + bw, y_m + 30, s4_x, y_m + 30, "#d98a00", "B", 2.0))
    p.append(text(s3_x + bw + 25, y_m + 20, "Дія завершена", size=9.5, color="#d98a00"))

    # Зворотний перехід у сон (все добре)
    p.append('<path d="M %d %d L %d %d L %d %d L %d %d" fill="none" stroke="%s" stroke-width="2.0" marker-end="url(#arrB)"/>'
             % (s4_x + bw / 2, y_m + bh, s4_x + bw / 2, y_m + bh + 45, s1_x + bw / 2, y_m + bh + 45, s1_x + bw / 2, y_m + bh + 2, NEG))
    p.append(text(W / 2, y_m + bh + 38, "Нормальне завершення циклу → встановити наступний RTC будильник і заснути",
                  size=10.5, color=NEG, bold=True))

    # Перехід з SAMPLE у сон якщо дія не потрібна
    p.append('<path d="M %d %d L %d %d L %d %d L %d %d" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4,3" marker-end="url(#arrB)"/>'
             % (s2_x + bw / 2, y_m, s2_x + bw / 2, y_m - 35, s1_x + bw / 2, y_m - 35, s1_x + bw / 2, y_m - 2, MUTED))
    p.append(text((s1_x + s2_x + bw) / 2, y_m - 42, "Полив/трекінг не потрібен (поріг не перевищено)", size=9.5, color=MUTED))

    # Аварійний стан унизу
    ey = 330
    p.append(rect(260, ey, 420, 95, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    p.append(text(470, ey + 24, "АВАРІЙНЕ БЛОКУВАННЯ (EMERGENCY LOCK)", size=12.5, color=POS, bold=True))
    err_lines = [
        "• Струм помпи > I_max (заклинило вал) → вимкнути реле",
        "• Тиск не зростає (сухий хід або прорив) → перекрити магістраль",
        "• Штормовий вітер > 20 м/с → флюгування сонячної панелі"
    ]
    for i, el in enumerate(err_lines):
        p.append(text(276, ey + 46 + i * 16, el, size=9.5, color=INK, anchor="start"))

    # Стрілка аварії з VERIFY в LOCK
    p.append(carrow(s4_x + 30, y_m + bh, 650, ey, POS, "R", 2.0))
    p.append(text(720, ey - 15, "Аварія давача / струму", size=9.5, color=POS))

    p.append(text(W / 2, 460,
                  "Стаціонарний місійний контролер працює в імпульсному режимі з жорстким контролем безпеки та енергоспоживання.",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "stationary-schedule-fsm.svg"), W, H, *p,
           title="Автомат стаціонарної місії: цикл сну, перевірки умов та аварійні блокування")


# ── 5. unified-mission-fsm: Уніфікована машина станів місії ───────────────────
def fig_unified_mission_fsm():
    W, H = 960, 500
    p = [COL_MARKERS]
    p.append(text(W / 2, 34, "Уніфікований місійний рушій для наземних, водних та стаціонарних систем",
                  size=14, color=INK, bold=True))
    p.append(text(W / 2, 54, "єдиний автомат послідовності команд із різними алгоритмами досягнення цілі",
                  size=12, color=MUTED))

    # Схема FSM місійного двигуна
    # Стани горизонтально
    bw, bh = 160, 68
    y_row = 110

    # IDLE
    p.append(block(40, y_row, bw, bh, ["IDLE", "Очікування місії,", "перевірка Arming"], "#f4f4f5", INK, size=11))

    # RUNNING_NAV
    p.append(block(240, y_row, bw, bh, ["RUNNING_NAV", "Рух до точки B", "Pure Pursuit / L1"], "#eef2ff", NEG, size=11))

    # STATION_KEEP
    p.append(block(440, y_row, bw, bh, ["STATION_KEEP", "Утримання точки /", "Віртуальний якір"], "#f0fdf4", FIELD, size=11))

    # ACTION_EXEC
    p.append(block(640, y_row, bw, bh, ["ACTION_EXEC", "Виконання дії:", "полив / зйомка / маніп."], "#fffbf0", "#d98a00", size=11))

    # COMPLETED
    p.append(block(800, 240, 130, bh, ["COMPLETED", "Місію виконано,", "парковка"], "#dcfce7", FIELD, size=11))

    # Стрілки переходів
    p.append(carrow(200, y_row + 34, 238, y_row + 34, NEG, "B", 2.0))
    p.append(text(220, y_row + 24, "Старт", size=9.5, color=NEG))

    p.append(carrow(400, y_row + 34, 438, y_row + 34, FIELD, "G", 2.0))
    p.append(text(420, y_row + 24, "dist < R", size=9.5, color=FIELD))

    p.append(carrow(600, y_row + 34, 638, y_row + 34, "#d98a00", "B", 2.0))
    p.append(text(620, y_row + 24, "Стабілізовано", size=9.5, color="#d98a00"))

    # Цикл переходу до наступного пункту місії (Next Item)
    p.append('<path d="M %d %d L %d %d L %d %d L %d %d" fill="none" stroke="%s" stroke-width="2.0" marker-end="url(#arrB)"/>'
             % (720, y_row + bh, 720, y_row + bh + 35, 320, y_row + bh + 35, 320, y_row + bh + 2, NEG))
    p.append(text(520, y_row + bh + 28, "Дію завершено → наступний пункт місії (item_idx++)", size=10.5, color=NEG, bold=True))

    # Завершення місії
    p.append(carrow(720, y_row + bh, 800, 240 + bh / 2, FIELD, "G", 2.0))
    p.append(text(780, 200, "Всі пункти пройдено", size=9.5, color=FIELD))

    # Аварійні переходи Failsafe (внизу)
    p.append(rect(140, 280, 520, 150, fill="#fff5f5", stroke=POS, sw=1.8, rx=10))
    p.append(text(400, 305, "КОНТУР АВАРІЙНОЇ ДЕГРАДАЦІЇ (FAILSAFE ENGINE)", size=13, color=POS, bold=True))

    failsafe_items = [
        ("Втрата GNSS / зв'язку", "→ Зупинка моторів (активне гальмо) або дрейф з маяком"),
        ("Крен / тангаж > ліміту (25°)", "→ Запобігання перекиданню ровера на косогорі"),
        ("Струмове перевантаження", "→ Виявлення заклинювання редуктора чи намотування водоростей"),
        ("Низький заряд батареї", "→ Спрощений рух додому по пройденому треку (Backtrack)")
    ]
    for i, (f_cause, f_react) in enumerate(failsafe_items):
        p.append(text(160, 332 + i * 22, "• " + f_cause, size=10.5, color=POS, anchor="start", bold=True))
        p.append(text(380, 332 + i * 22, f_react, size=10.5, color=INK, anchor="start"))

    # Стрілка зриву в Failsafe
    p.append(carrow(320, y_row + bh + 45, 320, 278, POS, "R", 2.2))
    p.append(text(330, 255, "Критична аварія", size=10, color=POS, bold=True))

    p.append(text(W / 2, 480,
                  "Уніфікований контролер відділяє логіку черги місії від специфіки руху конкретної платформи (ровер, човен, стаціонарний вузол).",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "unified-mission-fsm.svg"), W, H, *p,
           title="Уніфікований місійний рушій: черга завдань, автомати переходів та аварійний захист")


if __name__ == "__main__":
    fig_nonholonomic_kinematics()
    fig_virtual_anchor()
    fig_rover_odometry_fusion()
    fig_stationary_schedule_fsm()
    fig_unified_mission_fsm()
    print("All figures generated successfully.")
