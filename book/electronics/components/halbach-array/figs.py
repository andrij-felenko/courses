# -*- coding: utf-8 -*-
"""Фігури теми «Масив Гальбаха».
Імпортує спільний svgkit зі scripts/.
Запуск:  python figs.py  (з теки теми) -> пише у ./img/

Фігури:
  1. halbach-flux-mechanism.svg — Порівняння звичайного масиву магнітів та масиву Гальбаха (суперпозиція потоку).
  2. cylinder-halbach.svg — Циліндричні масиви Гальбаха (внутрішня концентрація диполя та мультиполя).
  3. bldc-halbach-comparison.svg — Ротор безколекторного двигуна (BLDC): звичайний ротор зі сталевим ярмом проти ротора Гальбаха.
  4. inductrack-maglev.svg — Принцип пасивної магнітної левітації Inductrack на масиві Гальбаха.
"""
import os, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
from svgkit import (text, rect, line, arrow, render, INK, MUTED, POS, NEG, FIELD, FILL, BG, LINE)  # noqa: E402

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

MAGNET_N = "#e74c3c"    # Північний полюс (червоний)
MAGNET_S = "#3498db"    # Південний полюс (синій)
MAGNET_BODY = "#f8f9fa" # Тіло магніту
YOKE_FILL = "#95a5a6"   # Сталеве магнітне ярмо
AIRGAP_COL = "#2ecc71"  # Потік у робочому зазорі
TRACK_COPPER = "#d35400"# Мідна колія Inductrack


# ── Фігура 1: Суперпозиція потоку: звичайний масив проти Гальбаха ───────────
def fig_flux_mechanism():
    W, H = 840, 500
    frags = []

    # Розділ 1: Звичайне чергування полюсів (симетричне розсіювання)
    frags.append(text(420, 48, "Звичайне чергування полюсів (N-S-N-S): симетричний потік в обидва боки", size=13, color=INK, bold=True))

    x_start = 140
    y_top_arr = 110
    bw, bh = 110, 46

    # Магніти: N (вгору), S (вниз), N (вгору), S (вниз)
    conv_dirs = [("N (↑)", POS, 0, -1), ("S (↓)", NEG, 0, 1), ("N (↑)", POS, 0, -1), ("S (↓)", NEG, 0, 1)]
    for i, (lbl, col, dx, dy) in enumerate(conv_dirs):
        bx = x_start + i * (bw + 6)
        frags.append(rect(bx, y_top_arr, bw, bh, fill="#fdfefe", stroke=col, sw=2, rx=4))
        frags.append(text(bx + bw / 2, y_top_arr + 28, lbl, size=13, color=col, bold=True))
        # стрілка намагніченості всередині
        if dy < 0:
            frags.append(arrow(bx + bw / 2, y_top_arr + 38, bx + bw / 2, y_top_arr + 10, color=col, sw=2))
        else:
            frags.append(arrow(bx + bw / 2, y_top_arr + 10, bx + bw / 2, y_top_arr + 38, color=col, sw=2))

    # Лінії поля зверху й знизу (симетричні дуги)
    for i in range(3):
        x1 = x_start + i * (bw + 6) + bw / 2
        x2 = x_start + (i + 1) * (bw + 6) + bw / 2
        xm = (x1 + x2) / 2
        # Верхня дуга
        if i % 2 == 0:
            frags.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4 3"/>' %
                         (x1, y_top_arr, xm, y_top_arr - 35, x2, y_top_arr, MUTED))
            frags.append(arrow(xm - 5, y_top_arr - 35, xm + 5, y_top_arr - 35, color=MUTED, sw=1.8))
        else:
            frags.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4 3"/>' %
                         (x2, y_top_arr, xm, y_top_arr - 35, x1, y_top_arr, MUTED))
            frags.append(arrow(xm + 5, y_top_arr - 35, xm - 5, y_top_arr - 35, color=MUTED, sw=1.8))
        # Нижня дуга
        if i % 2 == 0:
            frags.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4 3"/>' %
                         (x1, y_top_arr + bh, xm, y_top_arr + bh + 35, x2, y_top_arr + bh, MUTED))
            frags.append(arrow(xm - 5, y_top_arr + bh + 35, xm + 5, y_top_arr + bh + 35, color=MUTED, sw=1.8))
        else:
            frags.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4 3"/>' %
                         (x2, y_top_arr + bh, xm, y_top_arr + bh + 35, x1, y_top_arr + bh, MUTED))
            frags.append(arrow(xm + 5, y_top_arr + bh + 35, xm - 5, y_top_arr + bh + 35, color=MUTED, sw=1.8))

    frags.append(text(680, y_top_arr + 28, "50% потоку вгору\n50% потоку вниз", size=11, color=MUTED, anchor="start"))

    # Розділ 2: Масив Гальбаха (поворот на 90°)
    y_halbach = 300
    frags.append(line(80, 240, 760, 240, color="#d0d7de", sw=1.2, dash="5 4"))
    frags.append(text(420, 268, "Масив Гальбаха: циклічний поворот вектора намагніченості на 90°", size=13, color=INK, bold=True))

    halbach_dirs = [
        ("↑", POS, 0, -1),
        ("→", FIELD, 1, 0),
        ("↓", NEG, 0, 1),
        ("←", FIELD, -1, 0),
        ("↑", POS, 0, -1)
    ]
    bw_h = 92
    x_start_h = 100
    for i, (sym, col, dx, dy) in enumerate(halbach_dirs):
        bx = x_start_h + i * (bw_h + 4)
        frags.append(rect(bx, y_halbach, bw_h, bh, fill="#fdfefe", stroke=col, sw=2, rx=4))
        frags.append(text(bx + bw_h / 2, y_halbach + 28, sym, size=15, color=col, bold=True))
        cx, cy = bx + bw_h / 2, y_halbach + bh / 2
        if dx == 1:
            frags.append(arrow(cx - 20, cy, cx + 20, cy, color=col, sw=2.2))
        elif dx == -1:
            frags.append(arrow(cx + 20, cy, cx - 20, cy, color=col, sw=2.2))
        elif dy == -1:
            frags.append(arrow(cx, cy + 14, cx, cy - 14, color=col, sw=2.2))
        elif dy == 1:
            frags.append(arrow(cx, cy - 14, cx, cy + 14, color=col, sw=2.2))

    # Конструктивна суперпозиція зверху (щільні дуги поля)
    for i in range(4):
        x1 = x_start_h + i * (bw_h + 4) + bw_h / 2
        x2 = x_start_h + (i + 1) * (bw_h + 4) + bw_h / 2
        xm = (x1 + x2) / 2
        frags.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="2.6"/>' %
                     (x1, y_halbach, xm, y_halbach - 45, x2, y_halbach, FIELD))
        frags.append(arrow(xm - 8, y_halbach - 45, xm + 8, y_halbach - 45, color=FIELD, sw=2.4))
        # Додаткові лінії для густини
        frags.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8"/>' %
                     (x1 + 15, y_halbach, xm, y_halbach - 28, x2 - 15, y_halbach, FIELD))

    frags.append(rect(600, y_halbach - 46, 210, 36, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(705, y_halbach - 24, "СИЛЬНИЙ БІК: B ≈ 1.4 × B₀\nКонструктивне додавання", size=11, color=FIELD, bold=True))

    # Деструктивна суперпозиція знизу (поле майже нуль)
    frags.append(line(x_start_h + 10, y_halbach + bh + 20, x_start_h + 5 * (bw_h + 4) - 10, y_halbach + bh + 20, color="#bdc3c7", sw=1.5, dash="3 3"))
    frags.append(rect(600, y_halbach + bh + 10, 210, 36, fill="#fdedec", stroke=POS, sw=1.5, rx=6))
    frags.append(text(705, y_halbach + bh + 32, "СЛАБКИЙ БІК: B ≈ 0\nДеструктивне взаємогасіння", size=11, color=POS, bold=True))

    # Пояснювальний підсумок унизу
    frags.append(rect(80, 426, 680, 48, fill="#f4f6f8", stroke="#d0d7de", sw=1.4, rx=6))
    frags.append(text(420, 446, "Горизонтальні сегменти замикають потік через верхній простір без сталевого ярма.", size=12, color=INK, bold=True))
    frags.append(text(420, 464, "Знизу вектори поля спрямовані протилежно і повністю гасять один одного.", size=11, color=MUTED))

    render(os.path.join(IMG, "halbach-flux-mechanism.svg"), W, H, *frags,
           title="Фізичний механізм просторової суперпозиції в масиві Гальбаха")


# ── Фігура 2: Циліндричні конфігурації Гальбаха ──────────────────────────────
def fig_cylindrical_halbach():
    W, H = 840, 460
    frags = []

    # Лівий циліндр: Внутрішній диполь Гальбаха (поле лише всередині)
    cx1, cy1, R_out, R_in = 220, 210, 110, 65
    frags.append(text(cx1, 52, "Внутрішній циліндр (диполь)", size=14, color=INK, bold=True))
    frags.append(text(cx1, 72, "Поле сконцентроване в отворі, зовні B = 0", size=11, color=MUTED))

    # 8 сегментів кільця
    N_seg = 8
    for i in range(N_seg):
        a1 = i * 2 * math.pi / N_seg
        a2 = (i + 1) * 2 * math.pi / N_seg
        amid = (a1 + a2) / 2
        # Сектор як полігон
        p1x, p1y = cx1 + R_in * math.cos(a1), cy1 + R_in * math.sin(a1)
        p2x, p2y = cx1 + R_out * math.cos(a1), cy1 + R_out * math.sin(a1)
        p3x, p3y = cx1 + R_out * math.cos(a2), cy1 + R_out * math.sin(a2)
        p4x, p4y = cx1 + R_in * math.cos(a2), cy1 + R_in * math.sin(a2)
        pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y)
        frags.append('<polygon points="%s" fill="#ffffff" stroke="%s" stroke-width="1.6"/>' % (pts, LINE))

        # Вектор намагніченості: кут повороту M = 2 * amid (для диполя k=1)
        # у циліндрі Гальбаха M(phi) має кут gamma = 2*phi (або (p+1)*phi)
        gamma = 2 * amid
        rc = (R_in + R_out) / 2
        mcx, mcy = cx1 + rc * math.cos(amid), cy1 + rc * math.sin(amid)
        arr_len = 16
        ax2 = mcx + arr_len * math.cos(gamma)
        ay2 = mcy + arr_len * math.sin(gamma)
        ax1 = mcx - arr_len * math.cos(gamma)
        ay1 = mcy - arr_len * math.sin(gamma)
        frags.append(arrow(ax1, ay1, ax2, ay2, color=POS if math.sin(gamma) < 0 else FIELD, sw=2))

    # Силові лінії всередині отвору (однорідне вертикальне поле B)
    for ox in [-36, -18, 18, 36]:
        frags.append(arrow(cx1 + ox, cy1 + 42, cx1 + ox, cy1 - 42, color=FIELD, sw=2.2))
    frags.append(rect(cx1 - 42, cy1 - 12, 84, 24, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(cx1, cy1 + 4, "Однорідне B", size=10, color=FIELD, bold=True))

    # Зовнішній нуль
    frags.append(rect(cx1 - 65, cy1 + R_out + 18, 130, 26, fill="#fdf2e9", stroke="#e67e22", sw=1.2, rx=4))
    frags.append(text(cx1, cy1 + R_out + 35, "Зовні: B = 0", size=11, color="#e67e22", bold=True))


    # Правий циліндр: Зовнішній ротор Гальбаха (мультипольний ротор BLDC)
    cx2, cy2 = 620, 210
    frags.append(text(cx2, 52, "Мультипольний масив (BLDC ротор)", size=14, color=INK, bold=True))
    frags.append(text(cx2, 72, "Поле сконцентроване зовні (або всередині статора)", size=11, color=MUTED))

    # 12 сегментів (4-полюсний масив)
    N_seg2 = 12
    for i in range(N_seg2):
        a1 = i * 2 * math.pi / N_seg2
        a2 = (i + 1) * 2 * math.pi / N_seg2
        amid = (a1 + a2) / 2
        p1x, p1y = cx2 + R_in * math.cos(a1), cy2 + R_in * math.sin(a1)
        p2x, p2y = cx2 + R_out * math.cos(a1), cy2 + R_out * math.sin(a1)
        p3x, p3y = cx2 + R_out * math.cos(a2), cy2 + R_out * math.sin(a2)
        p4x, p4y = cx2 + R_in * math.cos(a2), cy2 + R_in * math.sin(a2)
        pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y)
        frags.append('<polygon points="%s" fill="#ffffff" stroke="%s" stroke-width="1.6"/>' % (pts, LINE))

        # Поворот для 4-полюсного (p=2): gamma = (1 + p)*amid = 3*amid
        gamma = 3 * amid
        rc = (R_in + R_out) / 2
        mcx, mcy = cx2 + rc * math.cos(amid), cy2 + rc * math.sin(amid)
        arr_len = 15
        ax2 = mcx + arr_len * math.cos(gamma)
        ay2 = mcy + arr_len * math.sin(gamma)
        ax1 = mcx - arr_len * math.cos(gamma)
        ay1 = mcy - arr_len * math.sin(gamma)
        frags.append(arrow(ax1, ay1, ax2, ay2, color=FIELD if i % 2 == 0 else POS, sw=1.8))

    # Зовнішні дуги магнітного поля
    for k in range(4):
        ang_c = k * math.pi / 2 + math.pi / 4
        x_pole = cx2 + (R_out + 8) * math.cos(ang_c)
        y_pole = cy2 + (R_out + 8) * math.sin(ang_c)
        frags.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s"/>' % (x_pole, y_pole, FIELD))

    # Нульове поле у внутрішньому отворі
    frags.append(rect(cx2 - 50, cy2 - 14, 100, 28, fill="#fdf2e9", stroke="#e67e22", sw=1.2, rx=4))
    frags.append(text(cx2, cy2 + 4, "У центрі: B = 0", size=11, color="#e67e22", bold=True))

    # Нижній висновок
    frags.append(rect(100, 396, 640, 42, fill="#f4f6f8", stroke="#d0d7de", sw=1.4, rx=6))
    frags.append(text(420, 414, "Циліндр Гальбаха формує задану конфігурацію мультиполя (диполь, квадруполь)", size=12, color=INK, bold=True))
    frags.append(text(420, 430, "повністю усуваючи паразитне розсіювання на протилежній радіальній поверхні.", size=11, color=MUTED))

    render(os.path.join(IMG, "cylinder-halbach.svg"), W, H, *frags,
           title="Циліндричні масиви Гальбаха: внутрішнє та зовнішнє фокусування")


# ── Фігура 3: Порівняння роторів BLDC двигуна ───────────────────────────────
def fig_bldc_comparison():
    W, H = 840, 470
    frags = []

    # Ліва половина: Звичайний BLDC ротор
    x_c1 = 220
    frags.append(text(x_c1, 48, "Звичайний ротор із залізним ярмом", size=13, color=INK, bold=True))

    # Сталеве ярмо (Back-iron / Back-yoke)
    frags.append(rect(60, 85, 320, 34, fill=YOKE_FILL, stroke=LINE, sw=1.5, rx=3))
    frags.append(text(220, 106, "Важке сталеве магнітне ярмо (Back-yoke)", size=11, color="#ffffff", bold=True))

    # Магніти на ярмі: N, S, N, S
    m_w = 70
    for i, (lbl, col) in enumerate([("N (↑)", POS), ("S (↓)", NEG), ("N (↑)", POS), ("S (↓)", NEG)]):
        mx = 70 + i * (m_w + 10)
        frags.append(rect(mx, 119, m_w, 42, fill="#ffffff", stroke=col, sw=2, rx=3))
        frags.append(text(mx + m_w / 2, 145, lbl, size=12, color=col, bold=True))

    # Зазор і статор
    frags.append(rect(60, 185, 320, 46, fill="#e8eaed", stroke=LINE, sw=1.5, rx=3))
    frags.append(text(220, 206, "Обмотки та зубці статора", size=11, color=INK, bold=True))
    frags.append(text(220, 222, "Присутній зубцевий момент (когінг)", size=10, color=POS))

    # Властивості лівого
    props_left = [
        "• Сталеве ярмо додає 30–50% маси ротора",
        "• Прямокутна форма поля -> когінг і гармоніки",
        "• Втрати на вихрові струми в магнітах і сталі"
    ]
    for idx, p in enumerate(props_left):
        frags.append(text(60, 260 + idx * 22, p, size=11, color=INK, anchor="start"))


    # Права половина: Ротор Гальбаха
    x_c2 = 620
    frags.append(text(x_c2, 48, "Ротор Гальбаха (без сталевого ярма)", size=13, color=FIELD, bold=True))

    # Легка немагнітна гільза (вуглеволокно / титан)
    frags.append(rect(460, 85, 320, 24, fill="#34495e", stroke=LINE, sw=1.5, rx=3))
    frags.append(text(620, 101, "Немагнітний карбоновий бандаж (надлегкий)", size=10, color="#ffffff", bold=True))

    # Масив Гальбаха: ↑ → ↓ ← ↑
    m_wh = 58
    h_dirs = [("↑", POS), ("→", FIELD), ("↓", NEG), ("←", FIELD), ("↑", POS)]
    for i, (lbl, col) in enumerate(h_dirs):
        mx = 466 + i * (m_wh + 6)
        frags.append(rect(mx, 109, m_wh, 46, fill="#ffffff", stroke=col, sw=2, rx=3))
        frags.append(text(mx + m_wh / 2, 137, lbl, size=14, color=col, bold=True))

    # Потік у зазорі: чистий синус
    frags.append(rect(460, 185, 320, 46, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(620, 206, "Безпазовий статор (Coreless / Slotless)", size=11, color=FIELD, bold=True))
    frags.append(text(620, 222, "Когінг = 0, чистий синусоїдний момент", size=10, color=FIELD))

    # Властивості правого
    props_right = [
        "• Сталеве ярмо повністю відсутнє (економія ваги)",
        "• Поле в зазорі зростає на ≈40% (B ~ 1.4 B₀)",
        "• Нульовий когінг та ідеальна плавність обертання",
        "• Рекордна питома потужність (кВт/кг)"
    ]
    for idx, p in enumerate(props_right):
        frags.append(text(460, 260 + idx * 22, p, size=11, color=FIELD, anchor="start", bold=(idx == 3)))

    # Загальний підсумок унизу
    frags.append(rect(60, 368, 720, 76, fill="#fdfefe", stroke=FIELD, sw=1.6, rx=6))
    frags.append(text(420, 390, "Масив Гальбаха усуває необхідність у важкому феромагнітному осерді ротора.", size=12, color=INK, bold=True))
    frags.append(text(420, 410, "Це кардинально знижує момент інерції ротора, дозволяє миттєве прискорення приводів", size=11, color=MUTED))
    frags.append(text(420, 428, "та забезпечує максимальний ККД у дронах, сервоприводах і безпілотній авіації.", size=11, color=MUTED))

    render(os.path.join(IMG, "bldc-halbach-comparison.svg"), W, H, *frags,
           title="Порівняння конструкції ротора BLDC: класичний магнітопровід проти масиву Гальбаха")


# ── Фігура 4: Пасивна магнітна левітація Inductrack ─────────────────────────
def fig_inductrack():
    W, H = 840, 460
    frags = []

    frags.append(text(420, 46, "Принцип пасивної магнітної левітації Inductrack на масиві Гальбаха", size=14, color=INK, bold=True))

    # Візок потяга / вагон із масивом Гальбаха (рухається зі швидкістю v)
    y_car = 90
    frags.append(rect(140, y_car, 560, 90, fill="#f8f9fa", stroke=LINE, sw=1.8, rx=6))
    frags.append(text(420, y_car + 24, "Основа рухомого екіпажу (постійна швидкість v ->)", size=12, color=INK, bold=True))
    frags.append(arrow(580, y_car + 20, 670, y_car + 20, color=POS, sw=2.5))
    frags.append(text(625, y_car + 12, "v (швидкість)", size=11, color=POS, bold=True))

    # Масив Гальбаха вбудований у дно візка
    y_h = y_car + 38
    h_blocks = [("↑", POS), ("→", FIELD), ("↓", NEG), ("←", FIELD), ("↑", POS), ("→", FIELD), ("↓", NEG)]
    bw_i = 64
    x_start_i = 170
    for i, (sym, col) in enumerate(h_blocks):
        bx = x_start_i + i * (bw_i + 6)
        frags.append(rect(bx, y_h, bw_i, 40, fill="#ffffff", stroke=col, sw=1.8, rx=3))
        frags.append(text(bx + bw_i / 2, y_h + 25, sym, size=13, color=col, bold=True))

    # Робочий зазор левітації
    frags.append(arrow(110, y_h + 45, 110, y_h + 65, color=FIELD, sw=1.8))
    frags.append(arrow(110, y_h + 65, 110, y_h + 45, color=FIELD, sw=1.8))
    frags.append(text(105, y_h + 57, "h (зазор)", size=10, color=FIELD, anchor="end", bold=True))

    # Пасивна колія: Мідні смуги / замкнені котушки (Inductrack Track)
    y_track = 200
    frags.append(rect(140, y_track, 560, 48, fill="#fbeee6", stroke=TRACK_COPPER, sw=2, rx=4))
    frags.append(text(420, y_track + 22, "Пасивна колія: замкнені індуктивні контури / мідна драбина (L, R)", size=12, color=TRACK_COPPER, bold=True))
    frags.append(text(420, y_track + 38, "Не потребує електроживлення в полотні!", size=11, color=MUTED))

    # Вихрові струми та сила левітації
    for i in range(6):
        cx_i = x_start_i + i * (bw_i + 6) + bw_i / 2
        # Стрілка індукованої підйомної сили (F_lift)
        frags.append(arrow(cx_i, y_track - 5, cx_i, y_track - 30, color=FIELD, sw=2.2))
    frags.append(text(420, y_track - 35, "Сила левітації (F_lift) — відштовхування індукованим струмом", size=11, color=FIELD, bold=True))

    # Графіки F_lift та F_drag від швидкості v
    y_box = 275
    frags.append(rect(140, y_box, 560, 150, fill="#fdfefe", stroke="#d0d7de", sw=1.5, rx=6))
    frags.append(text(420, y_box + 22, "Залежність підйомної сили та магнітного опору від швидкості v", size=12, color=INK, bold=True))

    # Міні-графік
    gx0, gy0, gw, gh = 200, y_box + 120, 220, 80
    frags.append(line(gx0, gy0, gx0 + gw, gy0, color=INK, sw=1.5))
    frags.append(line(gx0, gy0, gx0, gy0 - gh, color=INK, sw=1.5))
    frags.append(text(gx0 + gw + 10, gy0 + 4, "v", size=11, color=INK, bold=True))
    frags.append(text(gx0 - 10, gy0 - gh + 10, "F", size=11, color=INK, bold=True))

    # Крива F_lift (росте як v^2/(v^2 + v_c^2))
    pts_lift = []
    for step in range(30):
        vx = step / 29.0 * 200
        v_val = step / 5.0
        f_l = gh * 0.85 * (v_val**2 / (v_val**2 + 1.5**2))
        pts_lift.append("%.1f,%.1f" % (gx0 + vx, gy0 - f_l))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts_lift), FIELD))

    # Крива F_drag (пік на v_c, потім спадає як 1/v)
    pts_drag = []
    for step in range(30):
        vx = step / 29.0 * 200
        v_val = step / 5.0
        f_d = gh * 0.85 * (v_val / (v_val**2 + 1.5**2))
        pts_drag.append("%.1f,%.1f" % (gx0 + vx, gy0 - f_d))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4 3"/>' % (" ".join(pts_drag), POS))

    # Пояснення праворуч від графіка
    frags.append(text(460, y_box + 58, "— F_lift (підйомна сила): виходить на плато", size=11, color=FIELD, anchor="start", bold=True))
    frags.append(text(460, y_box + 80, "- - F_drag (магнітне гальмування): спадає як 1/v", size=11, color=POS, anchor="start", bold=True))
    frags.append(text(460, y_box + 104, "v_c (швидкість переходу): лише кілька км/год.", size=10, color=MUTED, anchor="start"))
    frags.append(text(460, y_box + 124, "При відмові живлення левітація зберігається до зупинки.", size=10, color=INK, anchor="start"))

    render(os.path.join(IMG, "inductrack-maglev.svg"), W, H, *frags,
           title="Магнітна левітація Inductrack на пасивній колії")


if __name__ == "__main__":
    fig_flux_mechanism()
    fig_cylindrical_halbach()
    fig_bldc_comparison()
    fig_inductrack()
    print("All figures generated successfully.")
