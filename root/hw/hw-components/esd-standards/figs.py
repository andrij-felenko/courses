# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_models_circuit_comparison():
    """Еквівалентні схеми та розрядні кола моделей ESD: HBM, MM, CDM та IEC 61000-4-2."""
    W, H = 840, 520
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke=BG))

    cards = [
        ("1. Human Body Model (HBM)", "ANSI/ESDA/JEDEC JS-001 (компонентний)",
         "C = 100 пФ", "R = 1500 Ом", "L ≈ 7.5 мкГн", "I_peak = 1.33 А (при 2 кВ)",
         "t_rise = 2…10 нс, τ = 150 нс", "Теплове руйнування переходу", POS),
        ("2. Machine Model (MM)", "JEDEC JESD22-A115 (застарілий)",
         "C = 200 пФ", "R = 0 Ом", "L ≈ 0.75 мкГн", "I_peak = 3…5 А (при 200 В)",
         "Коливальний RLC-розряд 15 МГц", "Металевий контакт без демпфування", MUTED),
        ("3. Charged Device Model (CDM)", "ANSI/ESDA/JEDEC JS-002 (компонентний)",
         "C = 1…30 пФ (кристал)", "R < 1…5 Ом (дуга)", "L < 1 нГн", "I_peak = 10…30 А (при 500 В)",
         "t_rise < 200…400 пс, t_p ≈ 1 нс", "Пробій підзатворного оксиду (dV/dt)", FIELD),
        ("4. System Level (IEC 61000-4-2)", "IEC 61000-4-2 (системний / готовий прилад)",
         "C = 150 пФ", "R = 330 Ом", "L ≈ 50 нГн", "I_peak = 30 А (при 8 кВ)",
         "t_rise = 0.7…1.0 нс, плато 30 нс", "Руйнування незахищених портів I/O", NEG),
    ]

    coords = [
        (25, 20, 380, 230),
        (435, 20, 380, 230),
        (25, 270, 380, 230),
        (435, 270, 380, 230),
    ]

    for (title_txt, sub_txt, c_val, r_val, l_val, i_val, t_val, fail_txt, accent), (x, y, w, h) in zip(cards, coords):
        p.append(rect(x, y, w, h, fill=FILL, stroke=accent, sw=2, rx=8))
        p.append(text(x + 15, y + 26, title_txt, size=13, bold=True, color=accent, anchor="start"))
        p.append(text(x + 15, y + 46, sub_txt, size=10, color=MUTED, anchor="start"))
        p.append(line(x + 15, y + 54, x + w - 15, y + 54, color=MUTED, sw=0.8, dash="3,3"))

        # Параметри схеми
        p.append(text(x + 20, y + 78, "Ємність накопичувача:", size=11, color=INK, anchor="start", bold=True))
        p.append(text(x + 180, y + 78, c_val, size=11, color=INK, anchor="start"))

        p.append(text(x + 20, y + 100, "Послідовний опір:", size=11, color=INK, anchor="start", bold=True))
        p.append(text(x + 180, y + 100, r_val, size=11, color=INK, anchor="start"))

        p.append(text(x + 20, y + 122, "Паразитна індуктивність:", size=11, color=INK, anchor="start", bold=True))
        p.append(text(x + 180, y + 122, l_val, size=11, color=INK, anchor="start"))

        p.append(text(x + 20, y + 144, "Піковий струм розряду:", size=11, color=INK, anchor="start", bold=True))
        p.append(text(x + 180, y + 144, i_val, size=11, color=accent, anchor="start", bold=True))

        p.append(text(x + 20, y + 166, "Часові параметри:", size=11, color=INK, anchor="start", bold=True))
        p.append(text(x + 180, y + 166, t_val, size=10.5, color=INK, anchor="start"))

        p.append(rect(x + 15, y + 184, w - 30, 32, fill="#ffffff", stroke=LINE, sw=1, rx=4))
        p.append(text(x + w / 2, y + 204, "Механізм відмови: " + fail_txt, size=10, bold=True, color=INK, anchor="middle"))

    render(os.path.join(IMG, 'models-circuit-comparison.svg'), W, H, *p)


def fig_discharge_waveforms_comparison():
    """Порівняння форм імпульсів струму ESD: CDM, IEC 61000-4-2, HBM та MM."""
    W, H = 840, 430
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke=BG))

    ox, oy = 80, 350
    ax, ay = 790, 50

    # Осі координат
    p.append(line(ox, oy, ax, oy, sw=2))
    p.append(line(ox, oy, ox, ay, sw=2))
    p.append(text(ax - 10, oy + 32, "Час t (логарифмічно-умовна шкала, нс)", size=11.5, anchor="end", color=MUTED))
    p.append(text(ox - 15, ay + 15, "Струм I (А)", size=11.5, anchor="end", color=MUTED))

    # Позначки шкали струму
    for val, y_pos in [(30, 80), (20, 150), (10, 220), (2, 310), (0, oy)]:
        p.append(line(ox - 5, y_pos, ox, y_pos, color=MUTED, sw=1.5))
        p.append(text(ox - 10, y_pos + 4, str(val), size=10.5, anchor="end", color=MUTED))

    # Горизонтальні пунктири
    for y_pos in [80, 150, 220, 310]:
        p.append(line(ox, y_pos, ax, y_pos, color="#e5e7eb", sw=1, dash="4,4"))

    # Позначки осі часу
    t_marks = [
        (ox + 45, "0.5"),
        (ox + 90, "1"),
        (ox + 160, "5"),
        (ox + 250, "15"),
        (ox + 360, "30"),
        (ox + 500, "60"),
        (ox + 650, "120"),
    ]
    for x_pos, txt in t_marks:
        p.append(line(x_pos, oy, x_pos, oy + 5, color=MUTED, sw=1.5))
        p.append(text(x_pos, oy + 20, txt, size=10, anchor="middle", color=MUTED))

    # 1. CDM імпульс (надвузький ультрапік 15-25 А, тривалість ~1 нс)
    cdm_pts = [
        (ox, oy),
        (ox + 15, oy - 120),
        (ox + 25, 120),       # пік ~24 А на 0.3 нс
        (ox + 35, 230),
        (ox + 55, oy - 10),
        (ox + 75, oy),
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join("%.1f,%.1f" % q for q in cdm_pts), FIELD))
    p.append(text(ox + 35, 105, "CDM (JS-002)", size=11, bold=True, color=FIELD, anchor="start"))
    p.append(text(ox + 35, 118, "t_rise < 400 пс", size=9.5, color=FIELD, anchor="start"))

    # 2. IEC 61000-4-2 (перший пік 30 А за 0.8 нс, спад, друге плато 16 А на 30 нс, спад на 60 нс)
    iec_pts = [
        (ox, oy),
        (ox + 30, oy - 100),
        (ox + 65, 80),        # 30 А на 0.8 нс
        (ox + 105, 195),      # спад голки
        (ox + 180, 205),
        (ox + 360, 215),      # 30 нс -> 16 А (y=215)
        (ox + 500, 265),      # 60 нс -> 8 А (y=265)
        (ox + 670, oy - 4),   # 100-150 нс
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>'
             % (" ".join("%.1f,%.1f" % q for q in iec_pts), NEG))
    p.append(text(ox + 85, 70, "IEC 61000-4-2 (8 кВ контактний)", size=11.5, bold=True, color=NEG, anchor="start"))
    p.append(text(ox + 370, 195, "друге плато (30 нс / 16 А)", size=9.5, color=NEG, anchor="start"))

    # 3. HBM імпульс (повільне наростання 2-10 нс, пік 1.33 А, спад τ = 150 нс)
    hbm_pts = [
        (ox, oy),
        (ox + 60, oy - 18),
        (ox + 120, 318),      # пік ~1.33 А на 5-10 нс
        (ox + 240, 324),
        (ox + 420, 332),
        (ox + 600, 342),
        (ox + 700, oy - 1),
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (" ".join("%.1f,%.1f" % q for q in hbm_pts), POS))
    p.append(text(ox + 140, 308, "HBM (JS-001, 2 кВ / 1.33 А)", size=10.5, bold=True, color=POS, anchor="start"))

    # 4. MM розряд (коливальний затухаючий RLC)
    mm_pts = [
        (ox, oy),
        (ox + 40, oy - 60),   # +3.5 А
        (ox + 90, oy + 40),   # зворотна напівхвиля -2 А
        (ox + 140, oy - 35),
        (ox + 190, oy + 25),
        (ox + 240, oy - 15),
        (ox + 290, oy),
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,3"/>'
             % (" ".join("%.1f,%.1f" % q for q in mm_pts), MUTED))
    p.append(text(ox + 95, oy - 48, "MM (коливання)", size=9.5, color=MUTED, anchor="start"))

    # Легенда
    p.append(rect(460, 45, 340, 80, fill=FILL, stroke=LINE, sw=1, rx=6))
    p.append(text(475, 66, "Порівняння енергії та небезпеки:", size=11, bold=True, anchor="start"))
    p.append(text(475, 86, "• IEC 61000-4-2: у 22 рази більший струм, ніж HBM", size=10, color=NEG, anchor="start"))
    p.append(text(475, 104, "• CDM: критичний градієнт dI/dt > 50 А/нс для затворів", size=10, color=FIELD, anchor="start"))

    render(os.path.join(IMG, 'discharge-waveforms-comparison.svg'), W, H, *p)


def fig_iec_gun_test_setup():
    """Схема випробувального стенду та конфігурація генератора ESD за стандартом IEC 61000-4-2."""
    W, H = 840, 460
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke=BG))

    # Заземлювальна пластина підлоги (Ground Reference Plane - GRP)
    p.append(rect(40, 400, 760, 20, fill="#d1d5db", stroke=LINE, sw=1.5, rx=2))
    p.append(text(420, 415, "Опорна пластина заземлення (Ground Reference Plane, GRP — латунь/мідь ≥ 0.25 мм)",
                  size=11, bold=True, anchor="middle"))

    # Дерев'яний стіл (висота 0.8 м)
    p.append(rect(140, 230, 560, 15, fill="#d97706", stroke="#92400e", sw=1.5, rx=2))
    p.append(rect(180, 245, 20, 155, fill="#b45309", stroke="#78350f", sw=1.5))
    p.append(rect(640, 245, 20, 155, fill="#b45309", stroke="#78350f", sw=1.5))
    p.append(text(420, 242, "Дерев'яний стіл (0.8 м над GRP)", size=10.5, color="#ffffff", bold=True, anchor="middle"))

    # Горизонтальна пластина зв'язку (HCP) на столі
    p.append(rect(160, 215, 520, 15, fill="#9ca3af", stroke=LINE, sw=1.5, rx=2))
    p.append(text(300, 226, "Горизонтальна пластина зв'язку (HCP, 1.6 × 0.8 м)", size=10, bold=True, anchor="start"))

    # Ізоляційний килимок 0.5 мм під EUT
    p.append(rect(430, 207, 230, 8, fill="#fef08a", stroke="#ca8a04", sw=1, rx=1))
    p.append(text(545, 204, "Ізолятор (товщина 0.5 мм)", size=9, color="#854d0e", anchor="middle"))

    # Обладнання під випробуванням (EUT)
    p.append(rect(450, 130, 190, 75, fill="#e0e7ff", stroke=NEG, sw=2, rx=6))
    p.append(text(545, 155, "Випробуваний прилад (EUT)", size=11.5, bold=True, color=NEG, anchor="middle"))
    p.append(text(545, 175, "Корпус, порти USB/Eth/I/O", size=10, color=MUTED, anchor="middle"))
    p.append(text(545, 192, "Критерій стійкості: A / B / C / D", size=9.5, color=INK, anchor="middle"))

    # Розрядний резистор HCP -> GRP (2 × 470 кОм)
    p.append(line(170, 230, 170, 400, color=POS, sw=2))
    p.append(rect(155, 290, 30, 30, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    p.append(text(170, 308, "470k", size=9, bold=True, color=POS, anchor="middle"))
    p.append(rect(155, 335, 30, 30, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    p.append(text(170, 353, "470k", size=9, bold=True, color=POS, anchor="middle"))
    p.append(text(125, 335, "Розв'язка HCP", size=10, color=POS, anchor="end"))

    # ESD-генератор (пістолет)
    p.append(rect(190, 70, 140, 50, fill=FILL, stroke=LINE, sw=2, rx=6))
    p.append(text(260, 92, "ESD-генератор", size=11.5, bold=True, anchor="middle"))
    p.append(text(260, 110, "150 пФ / 330 Ом", size=10, color=MUTED, anchor="middle"))

    # Рукоятка та наконечник пістолета
    p.append(rect(240, 120, 35, 45, fill="#4b5563", stroke=LINE, sw=1.5, rx=3))
    # Наконечник до роз'єму EUT
    p.append(line(330, 95, 450, 150, color=POS, sw=3))
    p.append(circle(450, 150, 4, fill=POS, stroke=POS))
    p.append(text(380, 115, "Контактний розряд (±8 кВ)", size=10, bold=True, color=POS, anchor="middle"))

    # Дріт повернення струму пістолета (довжина 2 м до GRP)
    p.append('<path d="M 210 120 C 150 160, 90 280, 90 400" fill="none" stroke="%s" stroke-width="2.5"/>' % INK)
    p.append(text(80, 260, "Кабель заземлення (2 м)", size=10, color=INK, anchor="end"))

    # Інформаційна панель праворуч вгорі
    p.append(rect(480, 25, 320, 85, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    p.append(text(495, 45, "Види впливу за стандартом:", size=11, bold=True, anchor="start"))
    p.append(text(495, 65, "1. Прямий контактний (гострий наконечник, до 8 кВ)", size=10, anchor="start"))
    p.append(text(495, 83, "2. Повітряний розряд (кулястий наконечник, до 15 кВ)", size=10, anchor="start"))
    p.append(text(495, 101, "3. Непрямий розряд (на пластини HCP та VCP)", size=10, anchor="start"))

    render(os.path.join(IMG, 'iec-gun-test-setup.svg'), W, H, *p)


def fig_tlp_test_principle():
    """Принцип вимірювання за методом Transmission Line Pulsing (TLP)."""
    W, H = 840, 420
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke=BG))

    # Блок високовольтного джерела живлення
    p.append(rect(30, 60, 150, 70, fill=FILL, stroke=LINE, sw=1.8, rx=6))
    p.append(text(105, 90, "Джерело напруги", size=12, bold=True, anchor="middle"))
    p.append(text(105, 112, "DC HV (до 2–4 кВ)", size=10.5, color=MUTED, anchor="middle"))

    # Зарядна лінія передачі (50 Ом коаксіальний кабель)
    p.append(rect(230, 60, 180, 70, fill="#e0f2fe", stroke=NEG, sw=2, rx=6))
    p.append(text(320, 88, "Коаксіальна лінія 50 Ом", size=11.5, bold=True, color=NEG, anchor="middle"))
    p.append(text(320, 108, "Довжина L (t_p = 2L / v)", size=10.5, color=NEG, anchor="middle"))
    p.append(text(320, 122, "100 нс імпульс (L ≈ 10 м)", size=9.5, color=MUTED, anchor="middle"))

    # Зв'язок Джерело -> Лінія через резистор заряду
    p.append(line(180, 95, 230, 95, color=LINE, sw=2))
    p.append(rect(195, 87, 20, 16, fill="#ffffff", stroke=LINE, sw=1))
    p.append(text(205, 78, "R_ch", size=9, anchor="middle"))

    # Надшвидкий перемикач (герконове ртутне реле / RF Switch)
    p.append(rect(450, 60, 100, 70, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=6))
    p.append(text(500, 90, "Швидкий ключ", size=11, bold=True, color="#92400e", anchor="middle"))
    p.append(text(500, 110, "Ртутне реле", size=10, color="#b45309", anchor="middle"))

    p.append(line(410, 95, 450, 95, color=LINE, sw=2))

    # Випробуваний компонент (DUT)
    p.append(rect(680, 60, 130, 70, fill="#fee2e2", stroke=POS, sw=2, rx=6))
    p.append(text(745, 90, "Захисний прилад", size=11.5, bold=True, color=POS, anchor="middle"))
    p.append(text(745, 110, "DUT (TVS/Діод)", size=10.5, color=POS, anchor="middle"))

    p.append(line(550, 95, 680, 95, color=LINE, sw=2))

    # Сенсори струму і напруги на шляху до DUT
    p.append(circle(590, 95, 12, fill="#ffffff", stroke=NEG, sw=1.5))
    p.append(text(590, 99, "V", size=10, bold=True, color=NEG, anchor="middle"))
    p.append(circle(640, 95, 12, fill="#ffffff", stroke=POS, sw=1.5))
    p.append(text(640, 99, "I", size=10, bold=True, color=POS, anchor="middle"))

    # З'єднання сенсорів з осцилографом
    p.append(line(590, 107, 590, 200, color=NEG, sw=1.5, dash="3,3"))
    p.append(line(640, 107, 640, 200, color=POS, sw=1.5, dash="3,3"))

    # Осцилограф
    p.append(rect(540, 200, 170, 75, fill=FILL, stroke=LINE, sw=1.8, rx=6))
    p.append(text(625, 228, "Швидкий осцилограф", size=11, bold=True, anchor="middle"))
    p.append(text(625, 248, "Смуга ≥ 1–2 ГГц", size=10, color=MUTED, anchor="middle"))
    p.append(text(625, 264, "Вибірка 70–90 нс вікна", size=9.5, color=FIELD, bold=True, anchor="middle"))

    # Вимірювач витоку після імпульсу (DC Leakage / SMU)
    p.append(rect(680, 295, 130, 60, fill="#f3e8ff", stroke="#7e22ce", sw=1.8, rx=6))
    p.append(text(745, 320, "Джерело-вимірювач", size=10.5, bold=True, color="#6b21a8", anchor="middle"))
    p.append(text(745, 340, "DC SMU (струм витоку)", size=9.5, color="#7e22ce", anchor="middle"))

    p.append(line(745, 130, 745, 295, color="#7e22ce", sw=1.5, dash="4,3"))

    # Діаграма часового вікна імпульсу зліва внизу
    ox, oy = 70, 370
    p.append(line(ox, oy, ox + 360, oy, sw=1.5))
    p.append(line(ox, oy, ox, oy - 160, sw=1.5))
    p.append(text(ox + 350, oy + 20, "час (нс)", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 8, oy - 150, "V, I", size=10, color=MUTED, anchor="end"))

    # Прямокутний імпульс 100 нс із дзвоном на фронті
    pulse_pts = [
        (ox, oy),
        (ox + 10, oy - 135),
        (ox + 20, oy - 110),
        (ox + 35, oy - 125),
        (ox + 50, oy - 120),
        (ox + 230, oy - 120),  # 70 нс
        (ox + 300, oy - 120),  # 90 нс
        (ox + 320, oy),        # 100 нс
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (" ".join("%.1f,%.1f" % q for q in pulse_pts), NEG))

    # Вікно усереднення 70-90 нс
    p.append(rect(ox + 230, oy - 145, 70, 145, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=0))
    p.append(text(ox + 265, oy - 152, "Вікно 70–90%", size=9.5, bold=True, color=FIELD, anchor="middle"))
    p.append(text(ox + 265, oy - 60, "Квазістатична\nточка (V, I)", size=9, color=FIELD, anchor="middle"))

    render(os.path.join(IMG, 'tlp-test-principle.svg'), W, H, *p)


def fig_tlp_snapback_iv_curve():
    """Квазістатична ВАХ захисного елемента з ефектом snapback та крива струму витоку."""
    W, H = 840, 460
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke=BG))

    ox, oy = 90, 390
    ax, ay = 760, 50

    # Осі TLP (Струм I_TLP vs Напруга V_TLP)
    p.append(line(ox, oy, ax, oy, sw=2))
    p.append(line(ox, oy, ox, ay, sw=2))
    p.append(text(ax - 10, oy + 28, "Напруга TLP (В)", size=11.5, anchor="end", color=MUTED))
    p.append(text(ox - 15, ay + 15, "Струм TLP (А)", size=11.5, anchor="end", color=MUTED))

    # Права вісь для струму витоку I_leak
    p.append(line(ax, oy, ax, ay, color="#7e22ce", sw=1.5, dash="3,3"))
    p.append(text(ax + 15, ay + 15, "Струм витоку I_leak (нА / мкА)", size=11, color="#7e22ce", anchor="start"))

    # Характерні точки snapback-кривої
    # V_rwm = 5 В, V_t1 = 14 В (I_t1 ~ 50 мА), V_h = 7 В (I_h ~ 1 А), I_t2 = 25 А (V_c = 12 В)
    x_rwm = ox + 90
    x_vh = ox + 150
    x_vt1 = ox + 380
    x_it2 = ox + 290
    y_it2 = 80
    y_vh = 340
    y_vt1 = 370

    # Крива ВАХ (червона лінія)
    p.append(line(ox, oy, x_rwm, oy, color=POS, sw=2.5))
    p.append(line(x_rwm, oy, x_vt1, y_vt1, color=POS, sw=2.5))
    p.append(line(x_vt1, y_vt1, x_vh, y_vh, color=POS, sw=2.5))  # Snapback відмикання
    p.append(line(x_vh, y_vh, x_it2, y_it2, color=POS, sw=3))    # Робоча гілка R_dyn

    # Точка вторинного пробою (руйнування)
    p.append(line(x_it2, y_it2, x_it2 + 20, y_it2 - 20, color=POS, sw=2, dash="3,3"))
    p.append(circle(x_it2, y_it2, 5, fill=POS, stroke=LINE))

    # Позначення точок на ВАХ
    p.append(circle(x_vt1, y_vt1, 4, fill=POS, stroke=POS))
    p.append(circle(x_vh, y_vh, 4, fill=POS, stroke=POS))

    # Написи ключових параметрів
    p.append(text(x_vt1 + 10, y_vt1 - 10, "V_t1, I_t1 (поріг спрацьовування)", size=10.5, bold=True, color=POS, anchor="start"))
    p.append(text(x_vh - 10, y_vh + 5, "V_h, I_h (напруга утримання)", size=10.5, bold=True, color=POS, anchor="end"))
    p.append(text(x_it2 - 15, y_it2 + 5, "I_t2 (граничний струм / руйнування)", size=11, bold=True, color=POS, anchor="end"))

    # Нахил R_dyn
    p.append(text(x_vh + 105, 210, "Динамічний опір:", size=10.5, bold=True, color=INK, anchor="start"))
    p.append(text(x_vh + 105, 228, "R_dyn = ΔV / ΔI", size=11, bold=True, color=NEG, anchor="start"))

    # Пунктири проєкцій
    p.append(line(x_vt1, y_vt1, x_vt1, oy, color=MUTED, sw=1, dash="3,3"))
    p.append(text(x_vt1, oy + 16, "V_t1", size=10.5, color=MUTED, anchor="middle"))

    p.append(line(x_vh, y_vh, x_vh, oy, color=MUTED, sw=1, dash="3,3"))
    p.append(text(x_vh, oy + 16, "V_h", size=10.5, color=MUTED, anchor="middle"))

    p.append(line(x_it2, y_it2, ox, y_it2, color=MUTED, sw=1, dash="3,3"))
    p.append(text(ox - 8, y_it2 + 4, "I_t2", size=10.5, color=MUTED, anchor="end"))

    p.append(line(x_rwm, oy, x_rwm, oy + 8, color=MUTED, sw=1.5))
    p.append(text(x_rwm, oy + 16, "V_RWM", size=10.5, color=MUTED, anchor="middle"))

    # Крива струму витоку I_leak (фіолетова)
    leak_pts = [
        (ox, 370),
        (x_rwm, 370),
        (x_vh + 50, 368),
        (x_it2 - 20, 362),
        (x_it2, 355),
        (x_it2 + 30, 110),   # Катастрофічний стрибок витоку на 4-6 порядків після I_t2
        (ax - 40, 80),
    ]
    p.append('<polyline points="%s" fill="none" stroke="#7e22ce" stroke-width="2.5" stroke-dasharray="5,4"/>'
             % (" ".join("%.1f,%.1f" % q for q in leak_pts), ))
    p.append(text(x_it2 + 40, 140, "Стрибок витоку (Soft / Hard failure)", size=10, bold=True, color="#6b21a8", anchor="start"))

    # Пояснювальна табличка
    p.append(rect(430, 250, 320, 110, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    p.append(text(445, 272, "Критерії надійності за TLP:", size=11, bold=True, anchor="start"))
    p.append(text(445, 294, "• V_clamp = V_h + I_ESD · R_dyn", size=10, color=NEG, anchor="start"))
    p.append(text(445, 314, "• Snapback знижує розсіювану потужність", size=10, anchor="start"))
    p.append(text(445, 334, "• I_t2 фіксується за зростанням витоку I_leak", size=10, color="#6b21a8", anchor="start"))

    render(os.path.join(IMG, 'tlp-snapback-iv-curve.svg'), W, H, *p)


if __name__ == '__main__':
    fig_models_circuit_comparison()
    fig_discharge_waveforms_comparison()
    fig_iec_gun_test_setup()
    fig_tlp_test_principle()
    fig_tlp_snapback_iv_curve()
    print("Figures generated successfully!")
