# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. user-vs-service-doc: Порівняння посібника користувача та сервісного документа ──
def fig_user_vs_service():
    W, H = 880, 440
    p = []

    p.append(text(W / 2, 28, "Порівняння архітектури експлуатаційної та сервісної документації", size=16, color=INK, bold=True))

    # Ліва колонка: Інструкція користувача (Чорна скринька)
    x1, y1, w1, h1 = 30, 55, 385, 360
    p.append(rect(x1, y1, w1, h1, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(rect(x1, y1, w1, 42, fill="#e2e8f0", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(x1 + w1 / 2, y1 + 26, "Посібник користувача (User Manual)", size=14, color=INK, bold=True))

    user_items = [
        ("Цільова аудиторія:", "Кінцевий оператор, власник виробу"),
        ("Модель пристрою:", "«Чорна скринька» — внутрішні вузли приховані"),
        ("Дозволені дії:", "Увімкнення, базова конфігурація, заміна батарей"),
        ("Межа втручання:", "Розкриття корпусу суворо заборонене"),
        ("Діагностика:", "Опис зовнішніх симптомів («перевірте розетку»)"),
        ("Безпека користувача:", "Захисні бар'єри, попередження про високу напругу"),
        ("Захист розробника:", "Збереження комерційної таємниці та IP"),
    ]
    yy = y1 + 62
    for title, desc in user_items:
        p.append(circle(x1 + 18, yy + 6, 4, fill=NEG, stroke=NEG, sw=1))
        p.append(text(x1 + 30, yy + 10, title, size=11, color=INK, bold=True, anchor="start"))
        p.append(text(x1 + 30, yy + 26, desc, size=10, color=MUTED, anchor="start"))
        yy += 41

    # Права колонка: Сервісний посібник (Відкрита біла скринька)
    x2, y2, w2, h2 = 465, 55, 385, 360
    p.append(rect(x2, y2, w2, h2, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    p.append(rect(x2, y2, w2, 42, fill="#dcfce7", stroke="#86efac", sw=1.5, rx=8))
    p.append(text(x2 + w2 / 2, y2 + 26, "Сервісний посібник (Service Guide)", size=14, color=FIELD, bold=True))

    service_items = [
        ("Цільова аудиторія:", "Сертифікований інженер / сервісний технік"),
        ("Модель пристрою:", "«Біла скринька» — повна схема, шини й вузли"),
        ("Дозволені дії:", "Розбирання, заміна модулів (FRU), перепайка"),
        ("Межа втручання:", "Прямий доступ до друкованої плати й компонентів"),
        ("Діагностика:", "Контрольні точки (TP), CLI, коди DTC, Fault Trees"),
        ("Безпека техніка:", "Розряд конденсаторів, правила LOTO, ESD-захист"),
        ("Калібрування:", "Підстроювання датчиків, прошивання OTP/EEPROM"),
    ]
    yy = y2 + 62
    for title, desc in service_items:
        p.append(circle(x2 + 18, yy + 6, 4, fill=FIELD, stroke=FIELD, sw=1))
        p.append(text(x2 + 30, yy + 10, title, size=11, color=INK, bold=True, anchor="start"))
        p.append(text(x2 + 30, yy + 26, desc, size=10, color=MUTED, anchor="start"))
        yy += 41

    p.append(line(442, 70, 442, 390, color="#94a3b8", sw=1.2, dash="4,4"))
    p.append(text(442, 230, "VS", size=13, color="#64748b", bold=True, anchor="middle"))

    render(os.path.join(OUT, "user-vs-service-doc.svg"), W, H, *p,
           title="Порівняння вимог до користувацької та сервісної документації")


# ── 2. service-teardown-and-safety: Безпека техніка та порядок демонтажу ──
def fig_teardown_and_safety():
    W, H = 920, 390
    p = []

    p.append(text(W / 2, 28, "Протокол безпеки техніка та покроковий демонтаж пристрою", size=16, color=INK, bold=True))

    steps = [
        ("1. Знеструмлення й LOTO", "Відключення 230V AC / АКБ\nЗамок блокування LOTO\nПеревірка нуля напруги", POS, "#fef2f2", "#fecaca"),
        ("2. Розряд накопичувачів", "Розряд високовольтних літів\nЧерез 1 кОм / 10 Вт (5 сек)\nКонтроль DMM: U < 12 V", "#d97706", "#fffbeb", "#fde68a"),
        ("3. ESD-підготовка", "Антистатичний килимок\nЗаземлений браслет R < 1M\nРозсіювальний інструмент", NEG, "#eff6ff", "#bfdbfe"),
        ("4. Демонтаж корпусу", "Гвинти Torx (45 cN·m)\nСпуджери для засувок\nПідйом кришки без згину", "#4b5563", "#f9fafb", "#e5e7eb"),
        ("5. Шлейфи та вузли", "Відмикання ZIF-замків\nЕкстрактор для U.FL антен\nОгляд O-ring і термопасти", FIELD, "#f0fdf4", "#bbf7d0"),
    ]

    bx, by, bw, bh = 20, 60, 164, 290
    gap = 16
    for i, (head, body_txt, col, bg_col, border_col) in enumerate(steps):
        cur_x = bx + i * (bw + gap)
        p.append(rect(cur_x, by, bw, bh, fill=bg_col, stroke=border_col, sw=1.5, rx=6))
        p.append(rect(cur_x, by, bw, 40, fill=col, stroke=col, sw=1, rx=6))
        p.append(text(cur_x + bw / 2, by + 25, head, size=11, color="#ffffff", bold=True))

        lines = body_txt.split("\n")
        ty = by + 75
        for ln in lines:
            p.append(circle(cur_x + 12, ty - 3, 3, fill=col, stroke=col, sw=1))
            p.append(text(cur_x + 20, ty, ln, size=9.5, color=INK, anchor="start"))
            ty += 42

        if i < len(steps) - 1:
            ax = cur_x + bw + 1
            ay = by + bh / 2
            p.append(arrow(ax, ay, ax + gap - 2, ay, color="#64748b", sw=1.8))

    render(os.path.join(OUT, "service-teardown-and-safety.svg"), W, H, *p,
           title="Послідовність безпечного розбирання та вимоги захисту техніка")


# ── 3. power-rail-test-points-map: Карта контрольних точок і дерево живлення ──
def fig_power_rail_test_points():
    W, H = 940, 450
    p = []

    p.append(text(W / 2, 28, "Ієрархія шин живлення та карта контрольних точок (Test Points)", size=16, color=INK, bold=True))

    px, py, pw, ph = 25, 55, 890, 375
    p.append(rect(px, py, pw, ph, fill="#fafaf9", stroke="#d6d3d1", sw=1.5, rx=8))

    nodes = [
        ("vin", 50, 185, 135, 105, "Вхід живлення\n(F1 / TVS / D1)", "TP_VIN", "24.0 V ±10%", "< 200 mV", POS),
        ("buck", 240, 185, 145, 105, "Step-Down DC-DC\n(Buck 5.0V / 2A)", "TP_5V0\nTP_SW", "5.05 V ±2%\nFsw=500kHz", "< 30 mV", "#d97706"),
        ("mcu_ldo", 445, 100, 150, 105, "LDO MCU / Логіка\n(3.3V / 800mA)", "TP_3V3\nTP_NRST", "3.30 V ±1.5%\nReset > 3.0V", "< 15 mV", FIELD),
        ("core_ldo", 445, 270, 150, 105, "DC-DC Core / SoC\n(1.8V / 1.5A)", "TP_1V8_CORE\nTP_DDR", "1.80 V ±2%\nЧас < 5 ms", "< 20 mV", NEG),
        ("vref", 655, 100, 145, 105, "ІОН АЦП / VREF\n(Precision Ref)", "TP_VREF\nTP_AGND", "2.500 V ±0.1%\nЗсув < 2 mV", "< 2 mV", "#7c3aed"),
        ("diag_mcu", 655, 270, 145, 105, "MCU / SoC Ядро\n(Діагн. порти)", "TP_SWDIO\nTP_SWCLK", "SWD 3.3V\nUART 115.2k", "Signal OK", "#0284c7"),
    ]

    # Зв'язки
    p.append(arrow(185, 237, 238, 237, color=LINE, sw=2))
    p.append(text(212, 227, "+24V", size=9.5, color=POS, bold=True))

    p.append(arrow(385, 220, 443, 160, color=LINE, sw=2))
    p.append(text(405, 178, "+5V0", size=9.5, color="#d97706", bold=True))

    p.append(arrow(385, 255, 443, 315, color=LINE, sw=2))
    p.append(text(405, 298, "+5V0", size=9.5, color="#d97706", bold=True))

    p.append(arrow(595, 152, 653, 152, color=LINE, sw=2))
    p.append(text(624, 142, "+3V3", size=9.5, color=FIELD, bold=True))

    p.append(arrow(595, 322, 653, 322, color=LINE, sw=2))
    p.append(text(624, 312, "+1V8", size=9.5, color=NEG, bold=True))

    for nid, nx, ny, nw, nh, nname, ntp, nvolt, nrip, ncol in nodes:
        p.append(rect(nx, ny, nw, nh, fill="#ffffff", stroke=ncol, sw=1.8, rx=6))
        nlines = nname.split("\n")
        p.append(text(nx + nw / 2, ny + 16, nlines[0], size=10.5, color=INK, bold=True))
        if len(nlines) > 1:
            p.append(text(nx + nw / 2, ny + 30, nlines[1], size=9, color=MUTED))

        p.append(line(nx + 6, ny + 38, nx + nw - 6, ny + 38, color="#e7e5e4", sw=1))

        tplines = ntp.split("\n")
        p.append(text(nx + 8, ny + 52, tplines[0], size=9.5, color=ncol, bold=True, anchor="start"))
        if len(tplines) > 1:
            p.append(text(nx + 8, ny + 66, tplines[1], size=9, color=ncol, anchor="start"))

        vlines = nvolt.split("\n")
        p.append(text(nx + nw - 8, ny + 52, vlines[0], size=9, color=INK, anchor="end"))
        if len(vlines) > 1:
            p.append(text(nx + nw - 8, ny + 66, vlines[1], size=9, color=MUTED, anchor="end"))

        p.append(text(nx + nw / 2, ny + nh - 10, "Пульсації: " + nrip, size=9, color="#059669", bold=True))

    # Легенда
    p.append(rect(50, 390, 840, 30, fill="#f5f5f4", stroke="#e7e5e4", sw=1, rx=4))
    p.append(text(65, 409, "Легенда перевірки:", size=10, color=INK, bold=True, anchor="start"))
    p.append(circle(205, 405, 4, fill=POS, stroke=POS, sw=1))
    p.append(text(215, 409, "Первинна напруга", size=9.5, color=MUTED, anchor="start"))
    p.append(circle(355, 405, 4, fill="#d97706", stroke="#d97706", sw=1))
    p.append(text(365, 409, "Проміжна шина", size=9.5, color=MUTED, anchor="start"))
    p.append(circle(490, 405, 4, fill=FIELD, stroke=FIELD, sw=1))
    p.append(text(500, 409, "Цифрова логіка 3.3V", size=9.5, color=MUTED, anchor="start"))
    p.append(circle(650, 405, 4, fill=NEG, stroke=NEG, sw=1))
    p.append(text(660, 409, "Ядро SoC 1.8V", size=9.5, color=MUTED, anchor="start"))
    p.append(circle(780, 405, 4, fill="#7c3aed", stroke="#7c3aed", sw=1))
    p.append(text(790, 409, "Прецизійна VREF", size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "power-rail-test-points-map.svg"), W, H, *p,
           title="Ієрархія контрольних точок шин живлення та допустимі допуски напруг")


# ── 4. diagnostic-fault-tree: Алгоритмічне дерево відмов (Fault Tree) ──
def fig_diagnostic_fault_tree():
    W, H = 940, 480
    p = []

    p.append(text(W / 2, 26, "Алгоритмічне дерево пошуку несправності (Fault Tree Analysis)", size=16, color=INK, bold=True))

    # Корінь
    rx, ry, rw, rh = 365, 45, 210, 56
    p.append(rect(rx, ry, rw, rh, fill="#fee2e2", stroke=POS, sw=1.8, rx=6))
    p.append(text(rx + rw / 2, ry + 22, "Симптом: Прилад не стартує", size=11, color=POS, bold=True))
    p.append(text(rx + rw / 2, ry + 42, "LED Status: 3 спалахи (ERR_PWR)", size=10, color=INK))

    # Рівень 1
    t1_x, t1_y, t1_w, t1_h = 355, 135, 230, 58
    p.append(arrow(rx + rw / 2, ry + rh, t1_x + t1_w / 2, t1_y, color=LINE, sw=1.8))
    p.append(rect(t1_x, t1_y, t1_w, t1_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(text(t1_x + t1_w / 2, t1_y + 20, "Крок 1: Виміряти TP_VIN", size=10.5, color=INK, bold=True))
    p.append(text(t1_x + t1_w / 2, t1_y + 40, "Очікувано: 24.0 V DC (допуск ±10%)", size=9.5, color=MUTED))

    # Гілка 1А: U_in < 21.6V (Ліворуч)
    f1_x, f1_y, f1_w, f1_h = 40, 230, 265, 90
    p.append(arrow(t1_x + 30, t1_y + t1_h, f1_x + f1_w / 2, f1_y, color=POS, sw=1.8))
    p.append(text(175, 210, "U < 21.6 V або 0 V", size=10, color=POS, bold=True))
    p.append(rect(f1_x, f1_y, f1_w, f1_h, fill="#fff1f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(f1_x + f1_w / 2, f1_y + 20, "Несправність первинного кола", size=11, color=POS, bold=True))
    p.append(text(f1_x + f1_w / 2, f1_y + 40, "1. Перевірити запобіжник F1 на обрив", size=9.5, color=INK))
    p.append(text(f1_x + f1_w / 2, f1_y + 58, "2. Перевірити пробій TVS діода D1", size=9.5, color=INK))
    p.append(text(f1_x + f1_w / 2, f1_y + 76, "3. Опір TP_VIN-GND: якщо < 5 Ом — заміна D1", size=9, color=MUTED))

    # Гілка 1B: U_in = OK -> Крок 2: Вимірювання TP_3V3 (Праворуч)
    t2_x, t2_y, t2_w, t2_h = 540, 230, 270, 65
    p.append(arrow(t1_x + t1_w - 30, t1_y + t1_h, t2_x + t2_w / 2, t2_y, color=FIELD, sw=1.8))
    p.append(text(620, 210, "U_in = 24V OK", size=10, color=FIELD, bold=True))
    p.append(rect(t2_x, t2_y, t2_w, t2_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(text(t2_x + t2_w / 2, t2_y + 20, "Крок 2: Виміряти напругу на TP_3V3", size=10.5, color=INK, bold=True))
    p.append(text(t2_x + t2_w / 2, t2_y + 38, "Очікувано: 3.30 V ± 0.05 V", size=9.5, color=MUTED))
    p.append(text(t2_x + t2_w / 2, t2_y + 54, "Опір у знеструмленому стані: R > 100 Ом", size=9, color="#0284c7"))

    # Гілка 2A: R(3V3) < 2 Ом (Коротке замикання)
    f2_x, f2_y, f2_w, f2_h = 390, 345, 255, 95
    p.append(arrow(t2_x + 50, t2_y + t2_h, f2_x + f2_w / 2, f2_y, color=POS, sw=1.8))
    p.append(text(460, 320, "R < 2 Ом (КЗ)", size=10, color=POS, bold=True))
    p.append(rect(f2_x, f2_y, f2_w, f2_h, fill="#fff1f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(f2_x + f2_w / 2, f2_y + 20, "Коротке замикання шини 3.3V", size=10.5, color=POS, bold=True))
    p.append(text(f2_x + f2_w / 2, f2_y + 40, "1. Подати 1.0V / 1A з ЛБЖ, пошук тепловізором", size=9, color=INK))
    p.append(text(f2_x + f2_w / 2, f2_y + 58, "2. Пробитий керамічний MLCC (C12, C18)", size=9, color=INK))
    p.append(text(f2_x + f2_w / 2, f2_y + 76, "3. Або пробій кристала MCU -> FRU Swap", size=9, color=MUTED))

    # Гілка 2B: 3.3V OK -> Крок 3: Перевірка SWD / UART Console
    f3_x, f3_y, f3_w, f3_h = 670, 345, 255, 95
    p.append(arrow(t2_x + t2_w - 50, t2_y + t2_h, f3_x + f3_w / 2, f3_y, color=FIELD, sw=1.8))
    p.append(text(765, 320, "3.3V в нормі", size=10, color=FIELD, bold=True))
    p.append(rect(f3_x, f3_y, f3_w, f3_h, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(f3_x + f3_w / 2, f3_y + 20, "Живлення OK -> Логічний збій", size=10.5, color=FIELD, bold=True))
    p.append(text(f3_x + f3_w / 2, f3_y + 40, "1. Підключити SWD: перевірити TP_NRST", size=9, color=INK))
    p.append(text(f3_x + f3_w / 2, f3_y + 58, "2. Зчитати регістри HardFault через CLI", size=9, color=INK))
    p.append(text(f3_x + f3_w / 2, f3_y + 76, "3. Відновити образ через DFU/ISP режим", size=9, color=MUTED))

    render(os.path.join(OUT, "diagnostic-fault-tree.svg"), W, H, *p,
           title="Алгоритмічне дерево відмов: від симптому живлення до виявлення несправного елемента")


if __name__ == "__main__":
    fig_user_vs_service()
    fig_teardown_and_safety()
    fig_power_rail_test_points()
    fig_diagnostic_fault_tree()
    print("OK: figures ->", OUT)
