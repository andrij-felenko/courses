# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. flight-mode-fsm-graph: граф станів і переходи автомата ─────────────────
def fig_fsm_graph():
    W, H = 1040, 640
    p = []

    # Тло та секції
    p.append(rect(20, 20, 1000, 600, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=12))

    # Зони станів (групи)
    p.append(rect(40, 50, 280, 550, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    p.append(text(180, 78, "Ручні та стабілізовані", size=13, color="#166534", bold=True))

    p.append(rect(340, 50, 330, 550, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    p.append(text(505, 78, "Навігаційні та позиційні", size=13, color="#1e40af", bold=True))

    p.append(rect(690, 50, 330, 550, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=8))
    p.append(text(855, 78, "Автономні та аварійні", size=13, color="#991b1b", bold=True))

    # Вузли ручних режимів
    # Manual
    b_man, _, _ = textbox(180, 140, "MANUAL / ACRO\nПряме керування кутовими\nшвидкостями (Rates)", size=11, pad=8, fill="#ffffff", stroke="#16a34a", sw=1.8, bold=True)
    p.append(b_man)

    # Stabilize
    b_stab, _, _ = textbox(180, 280, "STABILIZE\nАвтовирівнювання горизонту\nКути нахилу (Roll/Pitch)", size=11, pad=8, fill="#ffffff", stroke="#16a34a", sw=1.8, bold=True)
    p.append(b_stab)

    # AltHold
    b_alt, _, _ = textbox(180, 440, "ALT_HOLD\nУтримання висоти за барометром\nРучний Roll/Pitch, Z-регулятор", size=11, pad=8, fill="#ffffff", stroke="#16a34a", sw=1.8, bold=True)
    p.append(b_alt)

    # Вузли позиційних режимів
    # PosHold / Loiter
    b_pos, _, _ = textbox(505, 160, "POSHOLD / LOITER\n3D утримання позиції та швидкості\nПотрібні валідні GNSS + EKF", size=11, pad=8, fill="#ffffff", stroke="#2563eb", sw=1.8, bold=True)
    p.append(b_pos)

    # Guided
    b_gui, _, _ = textbox(505, 310, "GUIDED\nПоліт за зовнішніми цілями GCS\nСтримінг координат / швидкостей", size=11, pad=8, fill="#ffffff", stroke="#2563eb", sw=1.8, bold=True)
    p.append(b_gui)

    # Auto
    b_auto, _, _ = textbox(505, 460, "AUTO\nАвтономна місія за точками\nВиконання плану з пам'яті", size=11, pad=8, fill="#ffffff", stroke="#2563eb", sw=1.8, bold=True)
    p.append(b_auto)

    # Вузли автономних/аварійних режимів
    # RTL
    b_rtl, _, _ = textbox(855, 160, "RTL / RTH\nПовернення на точку зльоту\nПідйом -> Проліт -> Зависання", size=11, pad=8, fill="#ffffff", stroke="#dc2626", sw=1.8, bold=True)
    p.append(b_rtl)

    # Land
    b_land, _, _ = textbox(855, 310, "LAND\nКонтрольоване вертикальне зниження\nДетекція торкання землі -> Disarm", size=11, pad=8, fill="#ffffff", stroke="#dc2626", sw=1.8, bold=True)
    p.append(b_land)

    # Emergency Land / Terminate
    b_emg, _, _ = textbox(855, 460, "EMERGENCY LAND / KILL\nАварійна посадка або відсічка\nFailsafe найвищого пріоритету", size=11, pad=8, fill="#fee2e2", stroke="#991b1b", sw=2.2, color="#7f1d1d", bold=True)
    p.append(b_emg)

    # Переходи та стрілки
    # Manual <-> Stabilize
    p.append(arrow(170, 185, 170, 235, color="#16a34a", sw=1.5))
    p.append(arrow(190, 235, 190, 185, color="#16a34a", sw=1.5))

    # Stabilize <-> AltHold
    p.append(arrow(170, 325, 170, 395, color="#16a34a", sw=1.5))
    p.append(arrow(190, 395, 190, 325, color="#16a34a", sw=1.5))

    # AltHold -> PosHold (пряма стрілка горизонтально праворуч і вгору)
    p.append(line(290, 440, 370, 440, color="#2563eb", sw=1.5))
    p.append(line(370, 440, 370, 160, color="#2563eb", sw=1.5))
    p.append(arrow(370, 160, 385, 160, color="#2563eb", sw=1.5))
    p.append(text(380, 250, "Охоронець: 3D Fix, HDOP<1.5, EKF OK", size=9, color="#1d4ed8", bold=True, anchor="start"))

    # PosHold -> Auto
    p.append(line(625, 160, 650, 160, color="#2563eb", sw=1.5))
    p.append(line(650, 160, 650, 460, color="#2563eb", sw=1.5))
    p.append(arrow(650, 460, 625, 460, color="#2563eb", sw=1.5))
    p.append(text(645, 380, "Охоронець: WP>0, Home OK", size=9, color="#1d4ed8", bold=True, anchor="end"))

    # PosHold -> Guided
    p.append(arrow(505, 205, 505, 265, color="#2563eb", sw=1.5))

    # Failsafe переходи в RTL
    p.append(arrow(625, 140, 735, 140, color="#dc2626", sw=1.6))
    p.append(text(680, 130, "Failsafe RC / Bat", size=9, color="#b91c1c", bold=True))

    # RTL -> Land
    p.append(arrow(855, 205, 855, 265, color="#dc2626", sw=1.6))
    p.append(text(915, 235, "Home досягнуто", size=9, color="#b91c1c"))

    # Critical Failsafe -> Emergency Land
    p.append(arrow(625, 480, 725, 480, color="#7f1d1d", sw=2.0))
    p.append(text(675, 500, "EKF збій / Bat Lv2", size=9, color="#7f1d1d", bold=True))

    # Деградація при втраті сенсорів: PosHold -> AltHold
    p.append(line(385, 180, 350, 180, color="#d97706", sw=1.5))
    p.append(line(350, 180, 350, 420, color="#d97706", sw=1.5))
    p.append(arrow(350, 420, 290, 420, color="#d97706", sw=1.5))
    p.append(text(340, 320, "Втрата GNSS / EKF", size=9, color="#b45309", bold=True, anchor="end"))

    render(os.path.join(OUT, "flight-mode-fsm-graph.svg"), W, H, *p,
           title="Граф станів автомата польотних режимів з умовами-охоронцями та деградацією")


# ── 2. failsafe-preemption-ladder: сходинка пріоритетів і витіснення ──────────
def fig_preemption_ladder():
    W, H = 960, 520
    p = []

    p.append(rect(20, 20, 920, 480, fill="#ffffff", stroke="#e5e7eb", sw=1.5, rx=10))

    # Заголовок
    p.append(text(480, 55, "Ієрархія пріоритетів та арбітраж польотного автомата", size=16, color=INK, bold=True))
    p.append(text(480, 78, "Вищий рівень миттєво витісняє нижчий; повернення керування вимагає явного квитування", size=11, color=MUTED))

    # Ліва колонка — стрілка пріоритету
    p.append(rect(45, 110, 50, 362, fill="#fef2f2", stroke="#f87171", sw=1.5, rx=6))
    p.append(arrow(70, 450, 70, 130, color="#dc2626", sw=2.5))
    p.append(text(70, 462, "MIN", size=9, color="#dc2626", bold=True))
    p.append(text(70, 122, "MAX", size=9, color="#dc2626", bold=True))

    # Рівні сходинки (від найвищого до найнижчого)
    levels = [
        ("РІВЕНЬ 5: АВАРІЙНИЙ ВІДСТРІЛ (HARDWARE KILL / TERMINATE)",
         "Знеструмлення моторів, закриття ШІМ, розкриття парашута. Абсолютний пріоритет над усім софтом.",
         "#fee2e2", "#b91c1c", 110),
        ("РІВЕНЬ 4: КРИТИЧНИЙ FAILSAFE (CRITICAL BATTERY / EKF COLLAPSE)",
         "Примусовий Land або аварійна посадка. Негайно перехоплює керування, блокує місію та GCS.",
         "#ffedd5", "#c2410c", 185),
        ("РІВЕНЬ 3: НАВІГАЦІЙНИЙ FAILSAFE (RC LOSS / GCS TIMEOUT / GEOFENCE)",
         "Активація RTL або автоповернення по треку. Автономне повернення в зону безпеки.",
         "#fef9c3", "#a16207", 260),
        ("РІВЕНЬ 2: РУЧНЕ ПЕРЕХОПЛЕННЯ ОПЕРАТОРА (MANUAL OVERRIDE / STICK FLICK)",
         "Рух стіків пілота в Stabilize/Manual негайно скасовує Auto/Guided (Pilot Priority Interlock).",
         "#dbeafe", "#1d4ed8", 335),
        ("РІВЕНЬ 1: ШТАТНІ ЗАПИТИ ОПЕРАТОРА ТА GCS (POSHOLD / AUTO / GUIDED)",
         "Зміна режиму перемикачем або командою MAVLink. Виконується лише за виконання всіх охоронців.",
         "#f3f4f6", "#4b5563", 410)
    ]

    for title, desc, fill_c, stroke_c, y in levels:
        p.append(rect(110, y, 810, 62, fill=fill_c, stroke=stroke_c, sw=1.8, rx=6))
        p.append(text(130, y + 24, title, size=12, color=stroke_c, bold=True, anchor="start"))
        p.append(text(130, y + 46, desc, size=10.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "failsafe-preemption-ladder.svg"), W, H, *p,
           title="Сходинка пріоритетів і витіснення аварійних режимів польотного автомата")


# ── 3. guard-verification-and-throttle-lock: захист від стрибків і перевірка охоронців
def fig_guard_verification():
    W, H = 960, 560
    p = []

    p.append(rect(20, 20, 920, 520, fill="#ffffff", stroke="#e5e7eb", sw=1.5, rx=10))

    # Заголовок
    p.append(text(480, 52, "Алгоритм перевірки умов-охоронців та захисту від заборонених стрибків", size=15, color=INK, bold=True))

    # Блоки алгоритму
    # 1. Вхід: запит режиму
    b1, _, _ = textbox(160, 120, "1. ЗАПИТ ЗМІНИ РЕЖИМУ\nRC перемикач або MAVLink\n(SET_MODE / DO_SET_MODE)", size=10.5, pad=8, fill="#eff6ff", stroke="#3b82f6", sw=1.5, bold=True)
    p.append(b1)

    # Стрілка 1 -> 2
    p.append(arrow(260, 120, 330, 120, color=LINE, sw=1.5))

    # 2. Перевірка Failsafe
    b2, _, _ = textbox(445, 120, "2. ЧИ АКТИВНИЙ FAILSAFE?\nЯкщо активна критична аварія —\nзапит оператора відкидається", size=10.5, pad=8, fill="#fef2f2", stroke="#ef4444", sw=1.5, bold=True)
    p.append(b2)

    # Відхилення Failsafe
    p.append(arrow(445, 160, 445, 230, color="#dc2626", sw=1.5))
    p.append(text(450, 195, "ТАК (Блокування)", size=9, color="#dc2626", bold=True, anchor="start"))

    b_fail, _, _ = textbox(445, 265, "ВІДХИЛЕННЯ (DENIED)\nЗбереження поточного Failsafe\nВідправка STATUSTEXT у GCS", size=10, pad=6, fill="#fee2e2", stroke="#b91c1c", sw=1.5, color="#7f1d1d", bold=True)
    p.append(b_fail)

    # Стрілка 2 -> 3 (НІ)
    p.append(arrow(560, 120, 630, 120, color="#16a34a", sw=1.5))
    p.append(text(595, 110, "НІ", size=9, color="#16a34a", bold=True))

    # 3. Перевірка охоронців цільового режиму
    b3, _, _ = textbox(775, 120, "3. ПЕРЕВІРКА ОХОРОНЦІВ\nGNSS Fix, HDOP < 1.5, EKF валідний,\nМісія завантажена, Home закріплено", size=10.5, pad=8, fill="#f0fdf4", stroke="#22c55e", sw=1.5, bold=True)
    p.append(b3)

    # Стрілка 3 -> Відхилення (якщо охоронець не пройшов)
    p.append(arrow(775, 165, 775, 230, color="#dc2626", sw=1.5))
    p.append(text(780, 195, "НІ (Помилка передумов)", size=9, color="#dc2626", bold=True, anchor="start"))

    b_rej, _, _ = textbox(775, 265, "ВІДХИЛЕННЯ ЗАПИТУ\nКод MAV_RESULT_DENIED\nПопередження пілоту", size=10, pad=6, fill="#fee2e2", stroke="#b91c1c", sw=1.5, color="#7f1d1d", bold=True)
    p.append(b_rej)

    # Стрілка 3 -> 4 (ТАК)
    p.append(arrow(775, 305, 775, 370, color="#16a34a", sw=1.5))
    p.append(text(780, 335, "ТАК (Охоронці OK)", size=9, color="#16a34a", bold=True, anchor="start"))

    # 4. Перевірка безпеки переходу: захист від стрибка газу
    b4, _, _ = textbox(775, 420, "4. АНТИСТРИБКОВИЙ ЗАХИСТ\nЯкщо перехід з Land/PosHold -> Manual:\nчи нейтралізовано стік газу (Throttle Match)?", size=10.5, pad=8, fill="#fefce8", stroke="#eab308", sw=1.5, bold=True)
    p.append(b4)

    # Стрілка 4 -> Очікування
    p.append(arrow(645, 420, 545, 420, color="#ca8a04", sw=1.5))
    p.append(text(595, 410, "НЕ В ЗОНІ", size=9, color="#ca8a04", bold=True))

    b_wait, _, _ = textbox(420, 420, "ОЧІКУВАННЯ НЕЙТРАЛІЗАЦІЇ\nРежим не змінюється доки оператор\nне зведе стік газу з поточним дроселем", size=10, pad=6, fill="#fef9c3", stroke="#ca8a04", sw=1.5, bold=True)
    p.append(b_wait)

    # Стрілка 4 -> 5 (Успіх)
    p.append(arrow(775, 470, 775, 500, color="#16a34a", sw=1.5))
    p.append(arrow(775, 500, 200, 500, color="#16a34a", sw=1.5))
    p.append(arrow(200, 500, 200, 460, color="#16a34a", sw=1.5))

    # 5. Успішне перемикання режиму
    b5, _, _ = textbox(200, 420, "5. АТОМАРНЕ ПЕРЕМИКАННЯ\nІніціалізація нових контролерів,\nскидання інтеграторів PID без ривка", size=10.5, pad=8, fill="#dcfce7", stroke="#15803d", sw=2.0, color="#14532d", bold=True)
    p.append(b5)

    render(os.path.join(OUT, "guard-verification-and-throttle-lock.svg"), W, H, *p,
           title="Послідовність верифікації охоронців та захисту від заборонених стрибків")


if __name__ == "__main__":
    fig_fsm_graph()
    fig_preemption_ladder()
    fig_guard_verification()
    print("All figures generated successfully.")
