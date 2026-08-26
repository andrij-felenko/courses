# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. actuator-taxonomy.svg: Порівняльна структура 4 типів приводів ────────
def fig_actuator_taxonomy():
    W, H = 1060, 480
    p = []

    # Заголовок зверху
    p.append(text(W / 2, 35, "Класифікація та архітектура електромеханічних приводів", size=18, bold=True))
    p.append(text(W / 2, 58, "Принцип комутації, зворотний зв'язок та керування у вбудованих системах", size=12, color=MUTED))

    cols = [
        {
            "x": 30, "w": 235, "title": "Колекторний (BDC)",
            "badge": "Механічна комутація", "badge_col": POS,
            "items": [
                ("Ротор", "Обмотки на валу"),
                ("Статор", "Постійні магніти"),
                ("Комутація", "Щітки + мідний колектор"),
                ("Керування", "ШІМ через 1 H-міст"),
                ("Зворотний зв'язок", "Немає (або зовн. енкодер)"),
                ("Головна перевага", "Гранична простота й пуск"),
                ("Слабке місце", "Знос щіток, іскріння, ЕМС")
            ]
        },
        {
            "x": 285, "w": 235, "title": "Кроковий (Stepper)",
            "badge": "Дискретні кроки", "badge_col": "#d35400",
            "items": [
                ("Ротор", "Зубчастий магніт"),
                ("Статор", "Багатополюсні обмотки"),
                ("Комутація", "Електронна фазна (чопер)"),
                ("Керування", "Імпульси STEP / DIR"),
                ("Зворотний зв'язок", "Open-loop (без давача)"),
                ("Головна перевага", "Точний кут, момент спокою"),
                ("Слабке місце", "Нагрів у спокої, зрив кроків")
            ]
        },
        {
            "x": 540, "w": 235, "title": "Безколекторний (BLDC/PMSM)",
            "badge": "Синхронна машина", "badge_col": FIELD,
            "items": [
                ("Ротор", "Потужні постійні магніти"),
                ("Статор", "3-фазна симетрична обмотка"),
                ("Комутація", "Електронна (6 ключів / FOC)"),
                ("Керування", "ESC (BEMF / Холл / FOC)"),
                ("Зворотний зв'язок", "BEMF / Холл / енкодер"),
                ("Головна перевага", "ККД 90%, оберти, ресурс"),
                ("Слабке місце", "Складний 3-фазний інвертор")
            ]
        },
        {
            "x": 795, "w": 235, "title": "Сервопривід (Servo)",
            "badge": "Інтегрований вузол", "badge_col": NEG,
            "items": [
                ("Мотор", "DC / Coreless / BLDC"),
                ("Редуктор", "Металевий / пластиковий"),
                ("Давач кута", "Потенціометр / магнітний"),
                ("Керування", "ШІМ 1-2 мс / UART шина"),
                ("Зворотний зв'язок", "Внутрішній закритий PID"),
                ("Головна перевага", "Готовий кут у зборі"),
                ("Слабке місце", "Люфт редуктора, ліміт швидкості")
            ]
        }
    ]

    for c in cols:
        bx = c["x"]
        bw = c["w"]
        p.append(rect(bx, 80, bw, 380, fill="#fdfefe", stroke=LINE, sw=1.3, rx=8))
        
        # Шапка картки
        p.append(rect(bx, 80, bw, 65, fill="#f4f6f8", stroke=LINE, sw=1.3, rx=8))
        p.append(text(bx + bw / 2, 108, c["title"], size=13, bold=True))
        p.append(text(bx + bw / 2, 130, c["badge"], size=10.5, color=c["badge_col"], bold=True))

        # Рядки
        yy = 170
        for label, val in c["items"]:
            p.append(text(bx + 12, yy, label + ":", size=10, color=MUTED, anchor="start", bold=True))
            p.append(text(bx + bw - 12, yy, val, size=10, color=INK, anchor="end"))
            yy += 31
            if yy < 380:
                p.append(line(bx + 10, yy - 12, bx + bw - 10, yy - 12, color="#e2e8f0", sw=1))

    render(os.path.join(OUT, "actuator-taxonomy.svg"), W, H, *p)


# ── 2. torque-speed-comparison.svg: Криві Момент-Швидкість ──────────────────
def fig_torque_speed():
    W, H = 960, 480
    p = []

    p.append(text(W / 2, 32, "Криві залежності моменту від кутової швидкості (T-ω)", size=17, bold=True))
    p.append(text(W / 2, 54, "Порівняння механічних характеристик під різними типами навантаження", size=12, color=MUTED))

    # Область графіка
    gx, gy, gw, gh = 110, 90, 560, 320

    p.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))

    # Сітка
    for i in range(1, 5):
        y_line = gy + i * (gh / 5)
        p.append(line(gx, y_line, gx + gw, y_line, color="#f1f5f9", sw=1))
        x_line = gx + i * (gw / 5)
        p.append(line(x_line, gy, x_line, gy + gh, color="#f1f5f9", sw=1))

    # Осі координат
    p.append(arrow(gx, gy + gh, gx + gw + 35, gy + gh, color=INK, sw=2))  # Вісь X
    p.append(arrow(gx, gy + gh, gx, gy - 25, color=INK, sw=2))           # Вісь Y

    p.append(text(gx + gw + 40, gy + gh + 5, "Швидкість ω (RPM)", size=12, anchor="start", bold=True))
    p.append(text(gx - 15, gy - 15, "Момент T (Н·м)", size=12, anchor="middle", bold=True))

    # 1. BDC: лінійна спадна пряма
    # від (gx, gy + 70) до (gx + 450, gy + gh)
    p.append(line(gx, gy + 70, gx + 450, gy + gh, color=POS, sw=3))
    p.append(text(gx + 260, gy + 175, "Колекторний DC", size=11.5, color=POS, bold=True))

    # 2. Кроковий: величезний пусковий/утримуючий момент, різкий спад через L/R та протиЕРС
    path_stepper = "M %d %d Q %d %d %d %d T %d %d" % (
        gx, gy + 25,
        gx + 90, gy + 35,
        gx + 170, gy + 130,
        gx + 290, gy + gh - 10
    )
    p.append('<path d="%s" fill="none" stroke="#d35400" stroke-width="3"/>' % path_stepper)
    p.append(text(gx + 65, gy + 45, "Кроковий (утримання)", size=11, color="#d35400", bold=True))

    # 3. BLDC: подовжена пласка характеристика, високі оберти
    path_bldc = "M %d %d L %d %d Q %d %d %d %d" % (
        gx, gy + 105,
        gx + 340, gy + 115,
        gx + 470, gy + 140,
        gx + 540, gy + gh
    )
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_bldc, FIELD))
    p.append(text(gx + 390, gy + 95, "BLDC / PMSM (FOC)", size=11.5, color=FIELD, bold=True))

    # 4. Сервопривід з редуктором (високий момент на низьких обертах)
    path_servo = "M %d %d L %d %d L %d %d" % (
        gx, gy + 40,
        gx + 110, gy + 40,
        gx + 140, gy + gh
    )
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6 4"/>' % (path_servo, NEG))
    p.append(text(gx + 145, gy + 70, "Серво з редуктором", size=10.5, color=NEG, bold=True))

    # Позначки точок stall та no-load
    p.append(circle(gx, gy + 25, 4, fill="#d35400", stroke=INK, sw=1))
    p.append(text(gx - 10, gy + 28, "T_hold", size=10, anchor="end", color="#d35400"))

    p.append(circle(gx, gy + 70, 4, fill=POS, stroke=INK, sw=1))
    p.append(text(gx - 10, gy + 73, "T_stall", size=10, anchor="end", color=POS))

    p.append(circle(gx + 450, gy + gh, 4, fill=POS, stroke=INK, sw=1))
    p.append(text(gx + 450, gy + gh + 18, "ω_0 (BDC)", size=10, anchor="middle", color=POS))

    p.append(circle(gx + 540, gy + gh, 4, fill=FIELD, stroke=INK, sw=1))
    p.append(text(gx + 540, gy + gh + 18, "ω_max (BLDC)", size=10, anchor="middle", color=FIELD))

    # Права панель: Інженерні висновки
    px = 700
    p.append(rect(px, gy, 230, gh, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(px + 115, gy + 28, "Висновки для вибору", size=13, bold=True))

    notes = [
        ("Кроковий мотор:", "#d35400", "Максимальний момент у статиці. На швидкості > 1000 RPM момент падає майже до нуля."),
        ("Колекторний DC:", POS, "Лінійне падіння моменту. Легко регулювати швидкість напругою/ШІМ."),
        ("BLDC (FOC):", FIELD, "Широка зона номінального моменту. Здатний розвивати 10 000+ RPM з ККД > 85%."),
        ("Сервопривід:", NEG, "Редуктор множить момент у десятки разів, але пропорційно обмежує швидкість.")
    ]

    ny = gy + 60
    for title, col, desc in notes:
        p.append(text(px + 12, ny, title, size=11, color=col, anchor="start", bold=True))
        # Розбивка опису на рядки
        lines = []
        words = desc.split(" ")
        cur_ln = ""
        for w in words:
            if len(cur_ln + " " + w) > 26:
                lines.append(cur_ln)
                cur_ln = w
            else:
                cur_ln = (cur_ln + " " + w).strip()
        if cur_ln:
            lines.append(cur_ln)
        
        for li, ln in enumerate(lines):
            p.append(text(px + 12, ny + 16 + li * 13, ln, size=9.5, color=INK, anchor="start"))
        ny += 64

    render(os.path.join(OUT, "torque-speed-comparison.svg"), W, H, *p)


# ── 3. control-complexity-chain.svg: Апаратний і програмний стек керування ──
def fig_control_complexity():
    W, H = 1020, 500
    p = []

    p.append(text(W / 2, 32, "Стек керування та апаратна складність приводів", size=17, bold=True))
    p.append(text(W / 2, 54, "Від коду мікроконтролера до силових ключів та обмоток", size=12, color=MUTED))

    rows = [
        {
            "name": "Колекторний DC",
            "y": 80,
            "fw": "Простий ШІМ (Timer PWM)\n1-2 канали таймера",
            "driver": "Драйвер H-моста\n(напр. L298N, DRV8871)",
            "power": "4 MOSFET ключі\n(2 напівмости)",
            "feedback": "Відкритий контур або\nзовнішній інкрементний енкодер",
            "color": POS
        },
        {
            "name": "Кроковий мотор",
            "y": 180,
            "fw": "Генератор імпульсів STEP\nПрофіль розгону (Trapezoid/S-curve)",
            "driver": "Інтелектуальний чоппер\n(A4988 / TMC2209 StealthChop)",
            "power": "8 MOSFET ключів\n(2 повних H-мости)",
            "feedback": "Open-loop за замовчуванням\nStallGuard (BEMF) або енкодер",
            "color": "#d35400"
        },
        {
            "name": "BLDC / PMSM (FOC)",
            "y": 280,
            "fw": "FOC: Clarke/Park перетворення,\nPID Id/Iq струмів, SVPWM генерація",
            "driver": "3-фазний Pre-driver + Shunt\n(DRV8301 / STSPIN32)",
            "power": "6 потужних MOSFET\n(3 напівмости)",
            "feedback": "3 давачі Холла або\nвисокошвидкісний BEMF / енкодер",
            "color": FIELD
        },
        {
            "name": "Smart Bus Servo",
            "y": 380,
            "fw": "Пакетний протокол UART / RS-485\nКоманди: кут, швидкість, момент",
            "driver": "Вбудований MCU + H-міст\n(все всередині сервокорпусу)",
            "power": "Компактний H-міст\n+ металевий редуктор",
            "feedback": "Магнітний енкодер 12-біт\n+ телеметрія струму й температури",
            "color": NEG
        }
    ]

    # Заголовки стовпців
    col_headers = [
        (120, "Тип приводу"),
        (300, "Прошивка MCU (Firmware)"),
        (510, "Драйвер / Контролер"),
        (720, "Силовий каскад"),
        (900, "Зворотний зв'язок (Feedback)")
    ]
    for ch_x, ch_t in col_headers:
        p.append(text(ch_x, 72, ch_t, size=11.5, bold=True, color=INK))

    for r in rows:
        ry = r["y"]
        p.append(rect(20, ry, 980, 85, fill="#fdfefe", stroke=LINE, sw=1.1, rx=6))

        # Назва мотора ліворуч
        p.append(rect(25, ry + 5, 180, 75, fill=FILL, stroke=r["color"], sw=1.5, rx=5))
        p.append(text(115, ry + 47, r["name"], size=12, bold=True, color=r["color"]))

        # Стрілка 1
        p.append(arrow(208, ry + 42, 222, ry + 42, color=LINE, sw=1.5))

        # Firmware box
        p.append(fitbox(225, ry + 10, 180, 65, r["fw"], size=10, pad=4, fill="#ffffff", stroke="#cbd5e1"))

        # Стрілка 2
        p.append(arrow(408, ry + 42, 422, ry + 42, color=LINE, sw=1.5))

        # Driver box
        p.append(fitbox(425, ry + 10, 185, 65, r["driver"], size=10, pad=4, fill="#ffffff", stroke="#cbd5e1"))

        # Стрілка 3
        p.append(arrow(613, ry + 42, 627, ry + 42, color=LINE, sw=1.5))

        # Power stage box
        p.append(fitbox(630, ry + 10, 165, 65, r["power"], size=10, pad=4, fill="#ffffff", stroke="#cbd5e1"))

        # Стрілка 4
        p.append(arrow(798, ry + 42, 812, ry + 42, color=LINE, sw=1.5))

        # Feedback box
        p.append(fitbox(815, ry + 10, 178, 65, r["feedback"], size=10, pad=4, fill="#ffffff", stroke="#cbd5e1"))

    render(os.path.join(OUT, "control-complexity-chain.svg"), W, H, *p)


# ── 4. selection-decision-tree.svg: Дерево рішень вибору мотора ─────────────
def fig_selection_decision_tree():
    W, H = 1040, 520
    p = []

    p.append(text(W / 2, 30, "Інженерне дерево вибору типу електроприводу", size=17, bold=True))
    p.append(text(W / 2, 52, "Покроковий алгоритм від кінематичних вимог до оптимального мотора", size=12, color=MUTED))

    # Корінь: Тип руху
    p.append(rect(30, 230, 150, 60, fill="#f1f5f9", stroke=INK, sw=1.8, rx=6))
    p.append(text(105, 255, "Який тип руху", size=12, bold=True))
    p.append(text(105, 273, "потрібен системі?", size=11, color=MUTED))

    # Гілка 1: Неперервне обертання (вгору)
    p.append(line(180, 245, 240, 140, color=INK, sw=1.5))
    p.append(text(210, 175, "Неперервне", size=10, color=MUTED, bold=True))

    # Гілка 2: Дискретне позиціонування (вниз)
    p.append(line(180, 275, 240, 380, color=INK, sw=1.5))
    p.append(text(210, 345, "Позиція / Кут", size=10, color=MUTED, bold=True))

    # Вузол 1.1: Неперервне -> Швидкість/Ресурс
    p.append(rect(240, 105, 170, 70, fill="#f8fafc", stroke=LINE, sw=1.3, rx=6))
    p.append(text(325, 132, "Ресурс, оберти та", size=11.5, bold=True))
    p.append(text(325, 152, "вимоги до ККД?", size=11.5, bold=True))

    # Вузол 1.2: Позиціонування -> Тип керування
    p.append(rect(240, 345, 170, 70, fill="#f8fafc", stroke=LINE, sw=1.3, rx=6))
    p.append(text(325, 372, "Повний оберт чи", size=11.5, bold=True))
    p.append(text(325, 392, "фіксований сектор?", size=11.5, bold=True))

    # З Вузла 1.1:
    # 1.1 -> BDC
    p.append(arrow(410, 125, 520, 95, color=POS, sw=1.5))
    p.append(text(465, 100, "Низька ціна, низькі RPM", size=9.5, color=POS))
    
    # 1.1 -> BLDC
    p.append(arrow(410, 155, 520, 185, color=FIELD, sw=1.5))
    p.append(text(465, 180, "ККД > 85%, 5k+ RPM, ресурс", size=9.5, color=FIELD))

    # З Вузла 1.2:
    # 1.2 -> Секторний поворот (Серво)
    p.append(arrow(410, 365, 520, 310, color=NEG, sw=1.5))
    p.append(text(465, 328, "Сектор < 360°, важіль", size=9.5, color=NEG))

    # 1.2 -> Багатооборотне точне (Кроковий або Серво з шиною)
    p.append(arrow(410, 395, 520, 430, color="#d35400", sw=1.5))
    p.append(text(465, 420, "Багатооборотне безлюфтове", size=9.5, color="#d35400"))

    # Результати праворуч (Листки)
    # 1. Колекторний DC
    p.append(rect(525, 65, 485, 65, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(540, 92, "Колекторний DC мотор (BDC + Редуктор)", size=12, color=POS, anchor="start", bold=True))
    p.append(text(540, 114, "Застосування: колеса бюджетних роботів, помпи, вентилятори, іграшки, електроінструмент.", size=9.5, color=INK, anchor="start"))

    # 2. BLDC / PMSM
    p.append(rect(525, 155, 485, 65, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(540, 182, "Безколекторний мотор (BLDC / PMSM + FOC)", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(540, 204, "Застосування: дрони, шпинделі, електромобільність, безперервні насоси, прецизійні шарніри.", size=9.5, color=INK, anchor="start"))

    # 3. Сервопривід
    p.append(rect(525, 275, 485, 75, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(540, 300, "Сервопривід (RC PWM або Smart Bus RS-485)", size=12, color=NEG, anchor="start", bold=True))
    p.append(text(540, 320, "RC PWM: кермові поверхні літаків, замки, проста робототехніка.", size=9.5, color=INK, anchor="start"))
    p.append(text(540, 336, "Smart Bus: багатоланкові маніпулятори (Dynamixel), людиноподібні роботи з телеметрією.", size=9.5, color=INK, anchor="start"))

    # 4. Кроковий мотор
    p.append(rect(525, 395, 485, 75, fill="#fff7ed", stroke="#d35400", sw=1.5, rx=6))
    p.append(text(540, 420, "Кроковий мотор (Bipolar Stepper + TMC silent driver)", size=12, color="#d35400", anchor="start", bold=True))
    p.append(text(540, 442, "Застосування: 3D-принтери, верстати ЧПК, сканери, дозатори, фокусери об'єктивів.", size=9.5, color=INK, anchor="start"))
    p.append(text(540, 458, "Особливість: гарантована повторюваність кута без енкодера за умови запасу по моменту.", size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "selection-decision-tree.svg"), W, H, *p)


if __name__ == "__main__":
    fig_actuator_taxonomy()
    fig_torque_speed()
    fig_control_complexity()
    fig_selection_decision_tree()
    print("All figures generated successfully.")
