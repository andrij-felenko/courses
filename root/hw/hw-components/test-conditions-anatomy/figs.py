# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e0a32e"
AMBERBG = "#fff9e6"
REDBG   = "#fbecec"
GRNBG   = "#eef6ef"
BLUEBG  = "#e9eefb"


# ── 1. parameter-table-anatomy: Анатомія таблиці Electrical Characteristics ──
def fig_parameter_table_anatomy():
    W, H = 820, 420
    p = []
    
    # Заголовок блоку умов
    p.append(rect(30, 25, 760, 40, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(text(410, 50, "Header: V_CC = 5.0 V, T_A = 25 °C, unless otherwise noted", size=12, color=INK, bold=True))
    
    # Основна таблиця
    p.append(rect(30, 75, 760, 245, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    
    # Шапка таблиці
    p.append(rect(30, 75, 760, 36, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=0))
    p.append(text(120, 98, "PARAMETER", size=11, color=LINE, bold=True))
    p.append(text(240, 98, "CONDITIONS", size=11, color=POS, bold=True))
    p.append(text(390, 98, "MIN", size=11, color=LINE, bold=True))
    p.append(text(470, 98, "TYP", size=11, color=LINE, bold=True))
    p.append(text(550, 98, "MAX", size=11, color=LINE, bold=True))
    p.append(text(630, 98, "UNITS", size=11, color=LINE, bold=True))
    p.append(text(720, 98, "STATUS", size=11, color=LINE, bold=True))
    
    # Рядок 1: RDS(on)
    p.append(line(30, 111, 790, 111, color="#cbd5e1", sw=1))
    p.append(text(120, 138, "R_DS(on)", size=11, color=INK, bold=True))
    p.append(text(240, 138, "V_GS = 10 V, I_D = 20 A, Pulsed", size=10, color=POS, bold=True))
    p.append(text(390, 138, "—", size=11, color=MUTED))
    p.append(text(470, 138, "4.2", size=11, color=INK))
    p.append(text(550, 138, "5.5", size=11, color=POS, bold=True))
    p.append(text(630, 138, "mΩ", size=11, color=INK))
    p.append(text(720, 138, "100% Tested", size=10, color=FIELD, bold=True))
    
    # Рядок 2: RDS(on) при логічному рівні
    p.append(line(30, 163, 790, 163, color="#cbd5e1", sw=1))
    p.append(text(120, 190, "R_DS(on)", size=11, color=INK, bold=True))
    p.append(text(240, 190, "V_GS = 4.5 V, I_D = 10 A, Pulsed", size=10, color=POS, bold=True))
    p.append(text(390, 190, "—", size=11, color=MUTED))
    p.append(text(470, 190, "7.8", size=11, color=INK))
    p.append(text(550, 190, "11.0", size=11, color=POS, bold=True))
    p.append(text(630, 190, "mΩ", size=11, color=INK))
    p.append(text(720, 190, "100% Tested", size=10, color=FIELD, bold=True))
    
    # Рядок 3: Quiescent current
    p.append(line(30, 215, 790, 215, color="#cbd5e1", sw=1))
    p.append(text(120, 242, "I_Q (Supply Current)", size=10, color=INK, bold=True))
    p.append(text(240, 242, "V_IN = 12 V, I_OUT = 0 mA", size=10, color=POS, bold=True))
    p.append(text(390, 242, "—", size=11, color=MUTED))
    p.append(text(470, 242, "1.2", size=11, color=INK))
    p.append(text(550, 242, "2.0", size=11, color=POS, bold=True))
    p.append(text(630, 242, "mA", size=11, color=INK))
    p.append(text(720, 242, "Sampled / QA", size=10, color=AMBER, bold=True))
    
    # Рядок 4: Slew rate
    p.append(line(30, 267, 790, 267, color="#cbd5e1", sw=1))
    p.append(text(120, 294, "SR (Slew Rate)", size=11, color=INK, bold=True))
    p.append(text(240, 294, "A_V = 1, C_L = 15 pF, V_O = 2 V", size=10, color=POS, bold=True))
    p.append(text(390, 294, "15", size=11, color=POS, bold=True))
    p.append(text(470, 294, "25", size=11, color=INK))
    p.append(text(550, 294, "—", size=11, color=MUTED))
    p.append(text(630, 294, "V/μs", size=11, color=INK))
    p.append(text(720, 294, "By Design", size=10, color=MUTED, italic=True))
    
    # Вертикальні розділювачі колонок
    for col_x in [180, 345, 430, 510, 590, 670]:
        p.append(line(col_x, 75, col_x, 320, color="#e2e8f0", sw=1))
        
    # Рамка підсвічування CONDITIONS
    p.append(rect(182, 75, 161, 245, fill="none", stroke=POS, sw=2, rx=0))
    
    # Пояснювальні виноски знизу
    tb1, _, _ = textbox(190, 365, "CONDITIONS:\nЖорсткі межі вимірювання.\nПорушив — числа праворуч не діють.", size=10, pad=8, fill=REDBG, stroke=POS, bold=True)
    p.append(tb1)
    
    tb2, _, _ = textbox(470, 365, "MIN / MAX:\nЮридична гарантія.\nATE вибраковує все за межами.", size=10, pad=8, fill=GRNBG, stroke=FIELD, bold=True)
    p.append(tb2)
    
    tb3, _, _ = textbox(710, 365, "STATUS:\nРівень тестування.\n100% тест vs розрахунок.", size=10, pad=8, fill=BLUEBG, stroke=NEG, bold=True)
    p.append(tb3)

    render(os.path.join(OUT, "parameter-table-anatomy.svg"), W, H, *p,
           title="Анатомія таблиці електричних характеристик")


# ── 2. test-vs-reality: Стенд вимірювання проти реальної плати ────────────────
def fig_test_vs_reality():
    W, H = 820, 380
    p = []
    
    # Ліва колонка — Стенд тестування ATE
    p.append(rect(40, 30, 350, 310, fill=BLUEBG, stroke=NEG, sw=1.8, rx=8))
    p.append(text(215, 60, "ЛАБОРАТОРНИЙ ТЕСТОВИЙ СТЕНД (ATE)", size=11, color=NEG, bold=True))
    
    items_l = [
        ("Тривалість імпульсу:", "t_pulse = 300 мкс (t < τ_die)"),
        ("Шпаруватість (Duty):", "D < 2% (нульовий перегрів)"),
        ("Температура кристала:", "T_j = 25 °C (холодний масив)"),
        ("Напруга на затворі:", "V_GS = 10.0 В (глибоке насичення)"),
        ("Паразитне навантаження:", "C_L = 15 пФ, R_L = ∞ (ідеальне)"),
        ("Струм споживання:", "I_q без вихідного струму I_out"),
    ]
    y = 95
    for title, val in items_l:
        p.append(text(55, y, title, size=10, color=INK, anchor="start", bold=True))
        p.append(text(55, y + 15, val, size=9, color=NEG, anchor="start"))
        p.append(line(55, y + 23, 375, y + 23, color="#c7d7f7", sw=1))
        y += 36
    p.append(text(215, 320, "РЕЗУЛЬТАТ: Ідеальні мінімальні числа у паспорті", size=10, color=NEG, bold=True))
    
    # Права колонка — Реальна схема на друкованій платі
    p.append(rect(430, 30, 350, 310, fill=REDBG, stroke=POS, sw=1.8, rx=8))
    p.append(text(605, 60, "РЕАЛЬНА РОБОЧА ДРУКОВАНА ПЛАТА", size=11, color=POS, bold=True))
    
    items_r = [
        ("Режим живлення:", "Постійний DC або висока частота ШІМ"),
        ("Шпаруватість (Duty):", "D = 50...100% (постійні втрати)"),
        ("Температура кристала:", "T_j = 95...135 °C (нагрів корпусу)"),
        ("Напруга на затворі:", "V_GS = 3.3 В (вихід логіки MCU)"),
        ("Паразитне навантаження:", "C_L = 150 пФ (траси + кабелі)"),
        ("Струм споживання:", "I_total = I_q + I_load (навантаження)"),
    ]
    y = 95
    for title, val in items_r:
        p.append(text(445, y, title, size=10, color=INK, anchor="start", bold=True))
        p.append(text(445, y + 15, val, size=9, color=POS, anchor="start"))
        p.append(line(445, y + 23, 765, y + 23, color="#f5c6cb", sw=1))
        y += 36
    p.append(text(605, 320, "РЕЗУЛЬТАТ: Опір каналу вищий у 2–4 рази, смуга вужча", size=10, color=POS, bold=True))
    
    # Підпис внизу
    p.append(text(410, 362, "Умови тесту оптимізовані для автоматичного вимірювання, а не для повторення вашої схеми", size=9, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "test-vs-reality.svg"), W, H, *p,
           title="Умови заводського стенда проти реальної плати")


# ── 3. thermal-pulse-evolution: Еволюція температури кристала в імпульсі ───────
def fig_thermal_pulse_evolution():
    W, H = 800, 360
    p = []
    
    # Осі графіка
    ax0, ay0 = 80, 270
    ax_len, ay_len = 660, 210
    p.append(line(ax0, ay0, ax0 + ax_len, ay0, color=LINE, sw=1.8))
    p.append(arrow(ax0 + ax_len - 1, ay0, ax0 + ax_len, ay0, color=LINE, sw=1.8))
    p.append(line(ax0, ay0, ax0, ay0 - ay_len, color=LINE, sw=1.8))
    p.append(arrow(ax0, ay0 - ay_len + 1, ax0, ay0 - ay_len, color=LINE, sw=1.8))
    
    p.append(text(ax0 + ax_len - 10, ay0 + 20, "Час навантаження t (логарифмічна шкала)", size=10, color=INK, anchor="end", bold=True))
    p.append(text(ax0 - 15, ay0 - ay_len + 15, "Температура кристала T_j (°C)", size=10, color=INK, anchor="middle", bold=True))
    
    # Позначки осі часу
    times = [(120, "10 мкс"), (220, "300 мкс (Тест)"), (380, "10 мс"), (520, "1 с"), (660, "DC (Статика)")]
    for tx, tlbl in times:
        p.append(line(tx, ay0 - 4, tx, ay0 + 4, color=LINE, sw=1.2))
        p.append(text(tx, ay0 + 18, tlbl, size=9, color=INK, anchor="middle", bold=(tx == 220 or tx == 660)))
        
    # Лінія початкової температури T_j = 25°C
    p.append(line(ax0, 240, ax0 + ax_len - 30, 240, color="#94a3b8", sw=1, dash="4,4"))
    p.append(text(ax0 + 10, 232, "T_j = 25 °C (Початкова)", size=9, color="#64748b", anchor="start"))
    
    # Зона імпульсного вимірювання (зелена підсвітка)
    p.append(rect(140, 80, 160, 160, fill=GRNBG, stroke=FIELD, sw=1.2, rx=4))
    p.append(text(220, 100, "Імпульсний тест", size=10, color=FIELD, bold=True))
    p.append(text(220, 116, "Тепло в об'ємі кремнію", size=9, color=FIELD))
    p.append(text(220, 130, "ΔT_j < 1.5 °C", size=9, color=FIELD, bold=True))
    
    # Зона тривалого нагріву (червона підсвітка)
    p.append(rect(580, 80, 150, 160, fill=REDBG, stroke=POS, sw=1.2, rx=4))
    p.append(text(655, 100, "DC Стаціонарний режим", size=10, color=POS, bold=True))
    p.append(text(655, 116, "Тепло через корпус і плату", size=9, color=POS))
    p.append(text(655, 130, "T_j = 115...140 °C", size=9, color=POS, bold=True))
    
    # Крива температури Tj(t)
    curve_points = [
        (80, 240), (140, 239), (220, 237), (300, 225),
        (380, 195), (460, 150), (540, 115), (620, 102), (700, 100)
    ]
    path_d = ["M %.1f %.1f" % curve_points[0]]
    for x, y in curve_points[1:]:
        path_d.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(path_d), POS))
    
    # Точки на кривій
    p.append(circle(220, 237, 4, fill=FIELD, stroke=INK, sw=1.5))
    p.append(circle(660, 100, 4, fill=POS, stroke=INK, sw=1.5))
    
    # Стрілка різниці температур
    p.append(arrow(660, 235, 660, 108, color=POS, sw=1.8))
    p.append(text(675, 175, "ΔT = P · θ_JA\n(до +100 °C)", size=9, color=POS, anchor="start", bold=True))
    
    render(os.path.join(OUT, "thermal-pulse-evolution.svg"), W, H, *p,
           title="Динаміка температури кристала під час імпульсного тесту та в DC")


# ── 4. mosfet-rdson-vs-vgs-temp: Подвійна пастка R_DS(on) ─────────────────────
def fig_mosfet_rdson_vs_vgs_temp():
    W, H = 820, 360
    p = []
    
    # Панель А: Залежність RDS(on) від V_GS
    p.append(rect(30, 25, 365, 310, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(212, 50, "А: Опір каналу від напруги затвора", size=11, color=INK, bold=True))
    
    # Осі А
    ax0, ay0 = 70, 280
    p.append(line(ax0, ay0, ax0 + 300, ay0, color=LINE, sw=1.5))
    p.append(arrow(ax0 + 299, ay0, ax0 + 300, ay0, color=LINE, sw=1.5))
    p.append(line(ax0, ay0, ax0, ay0 - 200, color=LINE, sw=1.5))
    p.append(arrow(ax0, ay0 - 199, ax0, ay0 - 200, color=LINE, sw=1.5))
    
    p.append(text(ax0 + 290, ay0 + 18, "V_GS (В)", size=9, color=INK, anchor="end", bold=True))
    p.append(text(ax0 - 10, ay0 - 190, "R_DS(on) (мОм)", size=9, color=INK, anchor="middle", bold=True))
    
    # Розмітка осі X: 2V, 3.3V, 4.5V, 10V
    v_points = [(ax0 + 40, "2.5V"), (ax0 + 90, "3.3V"), (ax0 + 150, "4.5V"), (ax0 + 270, "10V")]
    for vx, vlbl in v_points:
        p.append(line(vx, ay0 - 3, vx, ay0 + 3, color=LINE, sw=1))
        p.append(text(vx, ay0 + 15, vlbl, size=9, color=INK, anchor="middle", bold=(vlbl == "3.3V" or vlbl == "10V")))
        
    # Крива RDS(on) vs VGS
    pts_a = [(ax0 + 35, ay0 - 180), (ax0 + 60, ay0 - 140), (ax0 + 90, ay0 - 90), (ax0 + 150, ay0 - 45), (ax0 + 210, ay0 - 30), (ax0 + 270, ay0 - 25)]
    path_a = ["M %.1f %.1f" % pts_a[0]]
    for x, y in pts_a[1:]:
        path_a.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(path_a), POS))
    
    # Виноски на панелі А
    p.append(circle(ax0 + 90, ay0 - 90, 4, fill=POS, stroke=INK, sw=1.2))
    p.append(text(ax0 + 100, ay0 - 100, "3.3V Логіка: 35 мОм", size=9, color=POS, anchor="start", bold=True))
    
    p.append(circle(ax0 + 270, ay0 - 25, 4, fill=FIELD, stroke=INK, sw=1.2))
    p.append(text(ax0 + 255, ay0 - 35, "10V Тест: 5 мОм", size=9, color=FIELD, anchor="end", bold=True))
    
    
    # Панель Б: Температурний коефіцієнт (деградація від нагріву)
    p.append(rect(425, 25, 365, 310, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(607, 50, "Б: Множник опору від температури кристала", size=11, color=INK, bold=True))
    
    # Осі Б
    bx0, by0 = 465, 280
    p.append(line(bx0, by0, bx0 + 300, by0, color=LINE, sw=1.5))
    p.append(arrow(bx0 + 299, by0, bx0 + 300, by0, color=LINE, sw=1.5))
    p.append(line(bx0, by0, bx0, by0 - 200, color=LINE, sw=1.5))
    p.append(arrow(bx0, by0 - 199, bx0, by0 - 200, color=LINE, sw=1.5))
    
    p.append(text(bx0 + 290, by0 + 18, "T_j (°C)", size=9, color=INK, anchor="end", bold=True))
    p.append(text(bx0 - 10, by0 - 190, "Множник R_DS", size=9, color=INK, anchor="middle", bold=True))
    
    # Розмітка осі X: 25°C, 75°C, 125°C, 150°C
    t_points = [(bx0 + 50, "25 °C"), (bx0 + 130, "75 °C"), (bx0 + 210, "125 °C"), (bx0 + 260, "150 °C")]
    for tx, tlbl in t_points:
        p.append(line(tx, by0 - 3, tx, by0 + 3, color=LINE, sw=1))
        p.append(text(tx, by0 + 15, tlbl, size=9, color=INK, anchor="middle", bold=(tlbl == "25 °C" or tlbl == "125 °C")))
        
    # Лінія 1.0x при 25°C
    p.append(line(bx0, by0 - 40, bx0 + 280, by0 - 40, color="#94a3b8", sw=1, dash="4,4"))
    p.append(text(bx0 + 10, by0 - 45, "1.0× (База при 25°C)", size=9, color="#64748b", anchor="start"))
    
    # Крива множника опору
    pts_b = [(bx0 + 50, by0 - 40), (bx0 + 130, by0 - 85), (bx0 + 210, by0 - 145), (bx0 + 260, by0 - 185)]
    path_b = ["M %.1f %.1f" % pts_b[0]]
    for x, y in pts_b[1:]:
        path_b.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(path_b), POS))
    
    # Виноски на панелі Б
    p.append(circle(bx0 + 50, by0 - 40, 4, fill=FIELD, stroke=INK, sw=1.2))
    p.append(circle(bx0 + 210, by0 - 145, 4, fill=POS, stroke=INK, sw=1.2))
    p.append(text(bx0 + 210, by0 - 160, "125 °C: опір зростає в 1.8...2.2 рази!", size=9, color=POS, anchor="middle", bold=True))
    
    render(os.path.join(OUT, "mosfet-rdson-vs-vgs-temp.svg"), W, H, *p,
           title="Залежність опору MOSFET від керування на затворі та температури кристала")


if __name__ == "__main__":
    fig_parameter_table_anatomy()
    fig_test_vs_reality()
    fig_thermal_pulse_evolution()
    fig_mosfet_rdson_vs_vgs_temp()
    print("Усі 4 фігури успішно згенеровано.")
