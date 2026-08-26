# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. why-validation-needed: три приховані загрози невалідованого пакета ────────
def fig_why_validation_needed():
    W, H = 960, 460
    p = []

    # Фон
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Три колонки для трьох загроз
    col_w = 280
    gap = 25
    x_start = 35
    y_top = 40
    box_h = 380

    threats = [
        ("Розбаланс напруг (ΔV)", POS, [
            "15 комірок: 3.55 В (норма)",
            "1 комірка: 3.85 В (перекос)",
            "Підсумок: 57.1 В на збірку",
            "Зарядник «бачить» недозаряд",
            "Викид на 1-й банці > 4.25 В",
            "Ризик: перенапруга і літієвий платинг"
        ]),
        ("Прихований брак зварювання", "#d35400", [
            "Холодний шов: R = 15 мОм",
            "Нормальний шов: R = 0.3 мОм",
            "Струм навантаження: I = 20 А",
            "P_loss = 20² × 0.015 = 6.0 Вт",
            "Локальний нагрів до 95°C",
            "Ризик: розплавлення сепаратора"
        ]),
        ("Похибка сенсорики BMS", NEG, [
            "Зсув АЦП або опір шлейфа",
            "AFE вимірює: 4.19 В (норма)",
            "Реальна напруга: 4.26 В",
            "Переплутані проводи балансу",
            "Зсув нуля струмового шунта",
            "Ризик: сліпота захисту OVP"
        ]),
    ]

    for i, (title, color, items) in enumerate(threats):
        cx = x_start + i * (col_w + gap) + col_w / 2
        x = x_start + i * (col_w + gap)
        y = y_top

        # Картка загрози
        p.append(rect(x, y, col_w, box_h, fill=FILL, stroke=color, sw=2, rx=8))
        
        # Шапка картки
        p.append(rect(x, y, col_w, 45, fill=color, stroke=color, sw=1, rx=8))
        p.append(rect(x, y + 35, col_w, 10, fill=color, stroke=color, sw=0, rx=0))
        p.append(text(cx, y + 28, title, size=14, color="#ffffff", bold=True))

        # Вміст списку
        item_y = y + 75
        for item in items:
            p.append(circle(x + 20, item_y - 4, 3.5, fill=color, stroke=color, sw=1))
            p.append(text(x + 32, item_y, item, size=12, color=INK, anchor="start"))
            item_y += 48

    render(os.path.join(OUT, "why-validation-needed.svg"), W, H, *p)


# ── 2. cc-cv-first-charge-profile: профіль CC/CV та робота балансира ────────────
def fig_cc_cv_charge():
    W, H = 960, 480
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    x0, y0 = 100, 400
    xw, yh = 780, 320

    # Сітка та розділова лінія CC -> CV
    x_split = x0 + 420
    p.append(rect(x0, y0 - yh, 420, yh, fill="#f8fafc", stroke="none"))
    p.append(rect(x_split, y0 - yh, xw - 420, yh, fill="#f1f5f9", stroke="none"))

    p.append(line(x_split, y0 - yh, x_split, y0, color=MUTED, sw=1.5, dash="4,4"))
    p.append(text(x0 + 210, y0 - yh + 25, "Фаза сталого струму (CC)", size=13, color=INK, bold=True))
    p.append(text(x_split + 180, y0 - yh + 25, "Фаза сталої напруги (CV) + балансування", size=13, color=INK, bold=True))

    # Горизонтальні лінії напруг
    y_ovp = y0 - yh + 60
    y_vmax = y0 - yh + 90
    y_bal = y0 - yh + 130

    p.append(line(x0, y_ovp, x0 + xw, y_ovp, color=POS, sw=1.2, dash="3,3"))
    p.append(text(x0 - 10, y_ovp + 4, "4.25 В (OVP)", size=11, color=POS, anchor="end", bold=True))

    p.append(line(x0, y_vmax, x0 + xw, y_vmax, color=FIELD, sw=1.2, dash="3,3"))
    p.append(text(x0 - 10, y_vmax + 4, "4.20 В (Стеля)", size=11, color=FIELD, anchor="end"))

    p.append(line(x0, y_bal, x0 + xw, y_bal, color="#e67e22", sw=1.2, dash="3,3"))
    p.append(text(x0 - 10, y_bal + 4, "4.15 В (Старт балансу)", size=11, color="#e67e22", anchor="end"))

    # Осі
    p.append(line(x0, y0, x0 + xw, y0, color=INK, sw=1.8))
    p.append(line(x0, y0, x0, y0 - yh, color=INK, sw=1.8))
    p.append(text(x0 + xw, y0 + 22, "Час заряду (t) →", size=12, color=MUTED, anchor="end"))
    p.append(text(x0 - 10, y0 - yh - 10, "Напруга / Струм", size=12, color=MUTED, anchor="start"))

    # Крива струму (синій): сталий до x_split, потім спадає
    pts_current = [(x0, y0 - 250), (x_split, y0 - 250), (x_split + 80, y0 - 160),
                   (x_split + 200, y0 - 70), (x0 + xw, y0 - 30)]
    pts_curr_str = " ".join("%.1f,%.1f" % pt for pt in pts_current)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts_curr_str, NEG))
    p.append(text(x0 + 120, y0 - 260, "Струм заряду I_chg (0.5C)", size=12, color=NEG, bold=True))
    p.append(text(x0 + xw - 30, y0 - 45, "I_cutoff (0.05C)", size=11, color=NEG))

    # Крива випереджаючої комірки Cell 1 (червоний)
    pts_c1 = [(x0, y0 - 60), (x0 + 180, y0 - 120), (x0 + 330, y_bal), (x_split, y_vmax),
              (x_split + 150, y_vmax), (x0 + xw, y_vmax)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts_c1), POS))
    p.append(text(x0 + 260, y_bal - 15, "Комірка 1 (випереджає)", size=11, color=POS, bold=True))

    # Крива відстаючої комірки Cell 2 (зелена)
    pts_c2 = [(x0, y0 - 40), (x0 + 200, y0 - 90), (x0 + 380, y0 - 140), (x_split, y0 - 170),
              (x_split + 180, y_bal), (x0 + xw, y_vmax)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts_c2), FIELD))
    p.append(text(x_split + 220, y_bal + 25, "Комірка 2 (відстає, підтягується)", size=11, color=FIELD, bold=True))

    # Позначення зони балансування: розміщуємо праворуч угорі над кривою
    tb_bal = textbox(x_split + 250, y0 - yh + 55, "Шунт Cell 1 УВІМКНЕНО\nI_bal = 60 мА", size=11,
                     fill="#fff3cd", stroke="#e67e22", color="#b7791f", bold=True)[0]
    p.append(tb_bal)

    render(os.path.join(OUT, "cc-cv-first-charge-profile.svg"), W, H, *p)


# ── 3. ntc-placement-thermal-map: розміщення NTC датчиків ───────────────────────
def fig_ntc_placement():
    W, H = 960, 480
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Ліва частина: схема розташування комірок та NTC
    p.append(rect(40, 40, 440, 400, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(text(260, 68, "Батарейний модуль 4S4P (вид зверху)", size=14, color=INK, bold=True))

    # Малюємо 16 циліндричних комірок 4x4
    r_cell = 24
    x_c0, y_c0 = 100, 125
    dx, dy = 75, 75

    for row in range(4):
        for col in range(4):
            cx = x_c0 + col * dx
            cy = y_c0 + row * dy
            is_core = (1 <= row <= 2) and (1 <= col <= 2)
            c_fill = "#fee2e2" if is_core else "#e2e8f0"
            p.append(circle(cx, cy, r_cell, fill=c_fill, stroke=LINE, sw=1.2))
            p.append(circle(cx, cy, 7, fill="#ffffff", stroke=LINE, sw=1))

    # NTC 1: геометричний центр (між центральними банками)
    ntc1_x, ntc1_y = x_c0 + 1.5 * dx, y_c0 + 1.5 * dy
    p.append(circle(ntc1_x, ntc1_y, 9, fill=POS, stroke="#ffffff", sw=2))
    p.append(text(ntc1_x, ntc1_y + 4, "T1", size=10, color="#ffffff", bold=True))

    # NTC 2: головна мінусова шина (куток)
    ntc2_x, ntc2_y = x_c0 - 15, y_c0 - 15
    p.append(circle(ntc2_x, ntc2_y, 9, fill=NEG, stroke="#ffffff", sw=2))
    p.append(text(ntc2_x, ntc2_y + 4, "T2", size=10, color="#ffffff", bold=True))

    # NTC 3: плата BMS (MOSFET ключі)
    ntc3_x, ntc3_y = x_c0 + 3 * dx + 20, y_c0 + 3 * dy + 20
    p.append(circle(ntc3_x, ntc3_y, 9, fill="#e67e22", stroke="#ffffff", sw=2))
    p.append(text(ntc3_x, ntc3_y + 4, "T3", size=10, color="#ffffff", bold=True))

    # Права частина: пояснення призначень і порогів
    rx, ry = 510, 40
    rw, rh = 410, 400
    p.append(rect(rx, ry, rw, rh, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    p.append(text(rx + rw / 2, ry + 30, "Карта термоточок та захисні ліміти", size=14, color=INK, bold=True))

    cards = [
        ("T1: Центр ядра збірки (Core)", POS, [
            "Найгірше відведення тепла (адіабатичне серце)",
            "Поріг заряду: COTP = 45 °C (вимкнення)",
            "Поріг розряду: DOTP = 60 °C (вимкнення)",
            "Контроль дельти: ΔT (T1 - T2) ≤ 5 °C"
        ]),
        ("T2: Силова струмознімна шина", NEG, [
            "Моніторинг опору силового з'єднувача",
            "Ловить ослаблення болтів / контактів",
            "Поріг спрацьовування: 65 °C",
            "Захист від холодного заряду: CUTP = 0 °C"
        ]),
        ("T3: Силові MOSFET та шунти BMS", "#e67e22", [
            "Нагрів ключів при тривалому розряді",
            "Тепловиділення балансувальних резисторів",
            "Поріг аварійного захисту: 85 °C",
            "Запобігає тепловому пробою кристалів"
        ]),
    ]

    card_y = ry + 55
    for title, col, lines_list in cards:
        p.append(rect(rx + 15, card_y, rw - 30, 95, fill="#ffffff", stroke=col, sw=1.5, rx=6))
        p.append(text(rx + 25, card_y + 20, title, size=12, color=col, anchor="start", bold=True))
        ly = card_y + 38
        for l in lines_list:
            p.append(text(rx + 25, ly, "• " + l, size=10, color=INK, anchor="start"))
            ly += 16
        card_y += 110

    render(os.path.join(OUT, "ntc-placement-thermal-map.svg"), W, H, *p)


# ── 4. kelvin-weld-measurement: 4-провідне вимірювання спаду на шві ─────────────
def fig_kelvin_weld():
    W, H = 960, 460
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Схема акумулятора, нікелевої стрічки та щупів
    p.append(rect(80, 180, 320, 220, fill="#f1f5f9", stroke=LINE, sw=2, rx=12))
    p.append(text(240, 300, "Корпус акумулятора (Cell)", size=16, color=MUTED, bold=True))

    # Плюсовий вивід (полюс)
    p.append(rect(180, 150, 120, 30, fill="#cbd5e1", stroke=LINE, sw=2, rx=4))
    p.append(text(240, 170, "Позитивний полюс (+)", size=11, color=INK, bold=True))

    # Нікелева стрічка зверху
    p.append(rect(120, 130, 280, 20, fill="#94a3b8", stroke=LINE, sw=1.5, rx=2))
    p.append(text(350, 122, "Нікелева стрічка", size=11, color=INK))

    # Зварні точки (spot weld nuggets)
    weld_x1, weld_x2 = 210, 140
    weld_x2 = 270
    p.append(circle(weld_x1, 140, 4, fill=POS, stroke=INK, sw=1))
    p.append(circle(weld_x2, 140, 4, fill=POS, stroke=INK, sw=1))

    # Підпис зварних точок унизу під полюсом
    p.append(text(240, 205, "Точки зварювання (Weld Nuggets)", size=11, color=POS, bold=True))

    # Силові щупи I+ та I- (Force)
    p.append(textbox(130, 35, "Force I+ (10 A)", size=11, fill="#fee2e2", stroke=POS)[0])
    p.append(line(130, 52, 130, 130, color=POS, sw=3))
    p.append(arrow(130, 52, 130, 100, color=POS, sw=3))

    p.append(textbox(380, 35, "Force I- (Return)", size=11, fill="#dbeafe", stroke=NEG)[0])
    p.append(line(380, 52, 380, 130, color=NEG, sw=3))
    p.append(arrow(380, 100, 380, 52, color=NEG, sw=3))

    # Потенційні голки V+ та V- (Sense) безпосередньо біля плями контакту
    p.append(textbox(210, 55, "Sense V+", size=10, fill="#dcfce7", stroke=FIELD)[0])
    p.append(line(210, 70, 225, 130, color=FIELD, sw=1.8, dash="3,2"))
    p.append(circle(225, 130, 3, fill=FIELD, stroke=INK, sw=1))

    p.append(textbox(280, 55, "Sense V-", size=10, fill="#dcfce7", stroke=FIELD)[0])
    p.append(line(280, 70, 265, 150, color=FIELD, sw=1.8, dash="3,2"))
    p.append(circle(265, 150, 3, fill=FIELD, stroke=INK, sw=1))

    # Права частина: Вольтметр і формули розрахунку
    rx, ry, rw, rh = 470, 50, 450, 360
    p.append(rect(rx, ry, rw, rh, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(rx + rw / 2, ry + 30, "Диференційний мікровольтметр", size=14, color=INK, bold=True))

    # Блок обчислення
    calc_lines = [
        "1. Тестовий струм:  I_test = 10.0 А",
        "2. Виміряний спад:   ΔU = 2.4 мВ = 0.0024 В",
        "3. Опір з'єднання:  R = ΔU / I = 0.24 мОм (НОРМА)",
        "",
        "Критерії бракування зварного шва:",
        "• R < 0.35 мОм  → Відмінна якість зварювання",
        "• 0.35..0.70 мОм → Задовільно (допустимий контакт)",
        "• R > 0.70 мОм  → БРАК: холодний шов / недовар",
        "",
        "Втрати при струмі 30 А (R = 1.5 мОм):",
        "P = I² · R = 30² · 0.0015 = 1.35 Вт (перегрів!)"
    ]
    cy = ry + 65
    for cl in calc_lines:
        bold = ("НОРМА" in cl) or ("БРАК" in cl) or ("1." in cl) or ("2." in cl) or ("3." in cl)
        col = POS if "БРАК" in cl else (FIELD if "НОРМА" in cl else INK)
        p.append(text(rx + 25, cy, cl, size=11, color=col, anchor="start", bold=bold))
        cy += 24

    render(os.path.join(OUT, "kelvin-weld-measurement.svg"), W, H, *p)


# ── 5. fat-state-machine-flow: автомат послідовності FAT ────────────────────────
def fig_fat_state_machine():
    W, H = 960, 480
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    p.append(text(W / 2, 35, "Автомат приймально-здавальних випробувань (FAT Pipeline)", size=16, color=INK, bold=True))

    steps = [
        ("1. Візуальний контроль", "Геометрія, полярність,\nізоляція та шлейф", 110),
        ("2. Hi-Pot & OCV", "Опір ізоляції >100 МОм,\nбазові напруги комірок", 280),
        ("3. Калібрувальний CC/CV", "Балансування комірок,\nконтроль OVP лімітів", 450),
        ("4. Тест під струмом", "Спад напруги на швах,\nтепловізійний моніторинг", 620),
        ("5. Паспорт виробу", "Фіксація параметрів,\nвидача сертифіката (Pass)", 790),
    ]

    y_mid = 160
    box_w = 145
    box_h = 80

    for i, (title, desc, cx) in enumerate(steps):
        p.append(rect(cx - box_w / 2, y_mid - box_h / 2, box_w, box_h, fill=FILL, stroke=LINE, sw=1.5, rx=6))
        p.append(text(cx, y_mid - 18, title, size=11, color=INK, bold=True))
        desc_lines = desc.split("\n")
        p.append(text(cx, y_mid + 8, desc_lines[0], size=9, color=MUTED))
        p.append(text(cx, y_mid + 24, desc_lines[1], size=9, color=MUTED))

        if i < len(steps) - 1:
            next_cx = steps[i + 1][2]
            p.append(arrow(cx + box_w / 2, y_mid, next_cx - box_w / 2, y_mid, color=FIELD, sw=2))

    fail_y = 350
    fail_w = 700
    p.append(rect(W / 2 - fail_w / 2, fail_y - 35, fail_w, 80, fill="#fee2e2", stroke=POS, sw=2, rx=8))
    p.append(text(W / 2, fail_y - 12, "СТАН АВАРІЇ / БРАКУВАННЯ (FAT REJECT / EMERGENCY SHUTDOWN)", size=13, color=POS, bold=True))
    p.append(text(W / 2, fail_y + 12, "Умови: ΔV > 30 мВ, T > 50 °C, R_weld > 0.7 мОм, похибка AFE > 5 мВ, спрацювання OVP/UVP/OCP", size=10, color=INK))
    p.append(text(W / 2, fail_y + 28, "Дія: негайне розмикання контакторів, скидання навантаження, блокування BMS у захищений режим", size=10, color=POS))

    for i, (title, desc, cx) in enumerate(steps[:4]):
        p.append(line(cx, y_mid + box_h / 2, cx, fail_y - 35, color=POS, sw=1.2, dash="3,3"))
        p.append(arrow(cx, fail_y - 45, cx, fail_y - 35, color=POS, sw=1.2))

    render(os.path.join(OUT, "fat-state-machine-flow.svg"), W, H, *p)


if __name__ == "__main__":
    fig_why_validation_needed()
    fig_cc_cv_charge()
    fig_ntc_placement()
    fig_kelvin_weld()
    fig_fat_state_machine()
    print("Всі фігури згенеровано успішно.")
