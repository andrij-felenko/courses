# -*- coding: utf-8 -*-
"""Фігури для теми forward-converter (Forward-перетворювач прямого ходу).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5). Вивід у ./img/.

    python figs.py
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *  # noqa: E402,F403

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

GOLD = "#b8860b"   # осердя / магнітне
HOT  = "#fdecea"   # тло первинної сторони
COLD = "#e9f7ef"   # тло вторинної сторони
BLUE = "#2457d6"   # струм / сигнали
WARN = "#d35400"   # застереження / обмеження


def _dot(cx, cy, r=4, color=INK):
    """Позначка початку обмотки (конвенція точок)."""
    return circle(cx, cy, r, fill=color, stroke=color, sw=1)


def _coil_v(x, y_top, y_bot, n=4, r=8, left=True, color=GOLD):
    """Вертикальна обмотка як ланцюжок дуг."""
    step = (y_bot - y_top) / n
    d = "M %.1f %.1f " % (x, y_top)
    sweep = 0 if left else 1
    yy = y_top
    for _ in range(n):
        d += "A %.1f %.1f 0 0 %d %.1f %.1f " % (r, step / 2, sweep, x, yy + step)
        yy += step
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, color)


def _coil_h(x_left, x_right, y, n=4, r=8, color=GOLD):
    """Горизонтальна котушка / дросель як ланцюжок дуг."""
    step = (x_right - x_left) / n
    d = "M %.1f %.1f " % (x_left, y)
    xx = x_left
    for _ in range(n):
        d += "A %.1f %.1f 0 0 1 %.1f %.1f " % (step / 2, r, xx + step, y)
        xx += step
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, color)


def _diode_h(cx, cy, pointing_right=True, color=INK):
    """Горизонтальний діод з центром у (cx, cy)."""
    dx = 12 if pointing_right else -12
    p = '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
        cx - dx, cy - 8, cx - dx, cy + 8, cx + dx, cy, FILL, color
    )
    bar = line(cx + dx, cy - 9, cx + dx, cy + 9, color=color, sw=2)
    return p + bar


def _diode_v(cx, cy, pointing_up=True, color=INK):
    """Вертикальний діод з центром у (cx, cy)."""
    dy = -12 if pointing_up else 12
    p = '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
        cx - 8, cy - dy, cx + 8, cy - dy, cx, cy + dy, FILL, color
    )
    bar = line(cx - 9, cy + dy, cx + 9, cy + dy, color=color, sw=2)
    return p + bar


def _gnd(cx, cy, color=LINE):
    """Символ землі."""
    return (line(cx, cy - 12, cx, cy, color=color, sw=1.8) +
            line(cx - 16, cy, cx + 16, cy, color=color, sw=1.8) +
            line(cx - 10, cy + 5, cx + 10, cy + 5, color=color, sw=1.8) +
            line(cx - 4, cy + 10, cx + 4, cy + 10, color=color, sw=1.8))


def fig_topology():
    """Базова топологія Forward-перетворювача з розмагнічувальною обмоткою."""
    W, H = 960, 480
    f = []
    bx = 440  # бар'єр ізоляції

    # Тло первинної та вторинної зон
    f.append(rect(15, 50, bx - 30, 400, fill=HOT, stroke=POS, sw=1.5, rx=8))
    f.append(rect(bx + 15, 50, W - bx - 30, 400, fill=COLD, stroke=FIELD, sw=1.5, rx=8))

    # Лінія бар'єра
    f.append(line(bx, 40, bx, 460, color=MUTED, sw=2, dash="6 6"))
    b, w, h = textbox(bx, 30, "Гальванічна розв'язка", size=12, pad=6, fill="#ffffff", stroke=MUTED)
    f.append(b)

    # Заголовки зон
    f.append(text(215, 75, "ПЕРВИННИЙ БІК (Висока напруга)", size=13, color=POS, bold=True))
    f.append(text(690, 75, "ВТОРИННИЙ БІК (Вихідний LC-фільтр)", size=13, color=FIELD, bold=True))

    # Джерело Vin (розміщено по центру первинної комірки)
    f.append(line(70, 130, 150, 130, color=POS, sw=2))
    f.append(line(70, 390, 270, 390, color=LINE, sw=2))
    b, w, h = textbox(70, 260, "+ Vin -\nДжерело\nживлення", size=11, pad=6, fill="#ffffff", stroke=POS)
    f.append(b)
    f.append(line(70, 130, 70, 222, color=POS, sw=2))
    f.append(line(70, 298, 70, 390, color=LINE, sw=2))

    # Трансформатор: осердя
    core_x = 405
    f.append(line(core_x - 3, 110, core_x - 3, 370, color=GOLD, sw=2.5))
    f.append(line(core_x + 3, 110, core_x + 3, 370, color=GOLD, sw=2.5))
    f.append(text(core_x, 95, "Осердя", size=11, color=GOLD, bold=True))

    # Первинна обмотка Np (верхня)
    np_x = core_x - 30
    f.append(_coil_v(np_x, 130, 230, n=4, r=9, left=True, color=POS))
    f.append(_dot(np_x - 14, 138, color=POS))
    f.append(text(np_x - 30, 180, "Np", size=13, color=POS, bold=True))

    # З'єднання Np з шиною Vin і ключем Q1
    f.append(line(150, 130, np_x, 130, color=POS, sw=2))
    f.append(line(np_x, 230, 270, 230, color=LINE, sw=2))
    f.append(line(270, 230, 270, 270, color=LINE, sw=2))

    # Ключ Q1 (MOSFET)
    b, w, h = textbox(270, 310, "Ключ Q1\n(MOSFET)", size=12, pad=8, fill="#ffffff", stroke=POS)
    f.append(b)
    f.append(line(270, 350, 270, 390, color=LINE, sw=2))
    f.append(_gnd(190, 420, color=LINE))
    f.append(line(190, 390, 190, 408, color=LINE, sw=2))

    # Третя обмотка розмагнічування Nr (нижня)
    nr_x = core_x - 30
    f.append(_coil_v(nr_x, 270, 370, n=4, r=9, left=True, color=WARN))
    f.append(_dot(nr_x - 14, 362, color=WARN))  # точка знизу!
    f.append(text(nr_x - 30, 320, "Nr", size=13, color=WARN, bold=True))

    # Діод розмагнічування Dr
    f.append(line(nr_x, 270, 150, 270, color=WARN, sw=1.8))
    f.append(line(150, 270, 150, 215, color=WARN, sw=1.8))
    f.append(_diode_v(150, 190, pointing_up=True, color=WARN))
    f.append(line(150, 165, 150, 130, color=WARN, sw=1.8))
    f.append(text(195, 190, "Діод Dr", size=11, color=WARN, bold=True))
    f.append(line(nr_x, 370, 270, 370, color=WARN, sw=1.8))
    f.append(line(270, 370, 270, 390, color=WARN, sw=1.8))

    # Вторинна обмотка Ns
    ns_x = core_x + 35
    f.append(_coil_v(ns_x, 130, 230, n=4, r=9, left=False, color=FIELD))
    f.append(_dot(ns_x + 14, 138, color=FIELD))  # точка зверху
    f.append(text(ns_x + 30, 180, "Ns", size=13, color=FIELD, bold=True))

    # Прямий діод D1
    f.append(line(ns_x, 130, 520, 130, color=FIELD, sw=2))
    f.append(_diode_h(545, 130, pointing_right=True, color=FIELD))
    f.append(text(545, 108, "D1 (прямий)", size=11, color=FIELD, bold=True))
    f.append(line(570, 130, 630, 130, color=FIELD, sw=2))

    # Замикальний діод D2 (Freewheeling)
    f.append(line(630, 130, 630, 215, color=FIELD, sw=2))
    f.append(_diode_v(630, 240, pointing_up=True, color=FIELD))
    f.append(line(630, 265, 630, 370, color=FIELD, sw=2))
    f.append(text(560, 240, "D2 (замикальний)", size=11, color=FIELD, bold=True))

    # Вихідний дросель L
    f.append(line(630, 130, 670, 130, color=FIELD, sw=2))
    f.append(_coil_h(670, 750, 130, n=4, r=8, color=GOLD))
    f.append(text(710, 108, "Дросель L", size=12, color=GOLD, bold=True))
    f.append(line(750, 130, 840, 130, color=FIELD, sw=2))

    # Вихідний конденсатор Cout
    f.append(line(800, 130, 800, 220, color=FIELD, sw=2))
    b, w, h = textbox(800, 250, "Cout\nфільтр", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    f.append(b)
    f.append(line(800, 280, 800, 370, color=FIELD, sw=2))

    # Навантаження Rload та клеми Vout
    f.append(line(840, 130, 890, 130, color=FIELD, sw=2))
    b, w, h = textbox(890, 250, "Rн\nНаванта-\nження", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    f.append(b)
    f.append(line(890, 130, 890, 205, color=FIELD, sw=2))
    f.append(line(890, 295, 890, 370, color=FIELD, sw=2))
    f.append(line(ns_x, 230, ns_x, 370, color=FIELD, sw=2))
    f.append(line(ns_x, 370, 890, 370, color=FIELD, sw=2))

    f.append(_gnd(530, 400, color=FIELD))
    f.append(line(530, 370, 530, 388, color=FIELD, sw=2))

    # Вихідна напруга стрілка
    f.append(arrow(925, 360, 925, 140, color=POS, sw=2))
    f.append(text(930, 250, "+ Vout", size=12, color=POS, bold=True, anchor="start"))

    return render(os.path.join(IMG, "topology.svg"), W, H, *f)


def fig_phases():
    """Дві фази комутації прямоходового перетворювача."""
    W, H = 940, 430
    f = []

    # Ліва панель: Фаза 1 (Q1 замкнено)
    f.append(rect(15, 20, 445, 390, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(237, 50, "ФАЗА 1: Ключ Q1 ЗАМКНЕНО (Пряма передача)", size=13, color=POS, bold=True))

    b, w, h = textbox(237, 100, "1. Енергія з Vin миттєво тече крізь Np→Ns і D1 у навантаження\n"
                                "2. Дросель L НАКОПИЧУЄ енергію (струм iL лінійно зростає)\n"
                                "3. Осердя НАМАГНІЧУЄТЬСЯ струмом Im; діод Dr закритий",
                      size=11, pad=8, fill="#ffffff", stroke=POS)
    f.append(b)

    # Спрощена схема фази 1
    f.append(line(50, 190, 160, 190, color=POS, sw=2.5))
    f.append(arrow(100, 190, 130, 190, color=POS, sw=2.5))
    f.append(text(105, 175, "струм Ip", size=11, color=POS, bold=True))
    f.append(rect(160, 170, 70, 90, fill="#ffffff", stroke=GOLD, sw=2))
    f.append(text(195, 205, "Трансф.\nNp : Ns", size=11, color=GOLD, bold=True))
    f.append(line(195, 260, 195, 310, color=POS, sw=2.5))
    b, w, h = textbox(195, 335, "Q1 ВКЛ\n(замкнено)", size=11, pad=6, fill="#eafaf1", stroke=FIELD)
    f.append(b)

    f.append(line(230, 190, 310, 190, color=FIELD, sw=2.5))
    f.append(arrow(260, 190, 285, 190, color=FIELD, sw=2.5))
    f.append(text(275, 175, "D1 ВКЛ", size=11, color=FIELD, bold=True))

    b, w, h = textbox(350, 190, "Дросель L\n(заряд)", size=11, pad=6, fill="#ffffff", stroke=GOLD)
    f.append(b)
    f.append(line(390, 190, 430, 190, color=FIELD, sw=2.5))
    f.append(arrow(400, 190, 420, 190, color=FIELD, sw=2.5))

    b, w, h = textbox(350, 300, "D2 ВИКЛ\n(закритий)", size=11, pad=6, fill="#fdecea", stroke=POS)
    f.append(b)

    # Права панель: Фаза 2 (Q1 розімкнено)
    f.append(rect(480, 20, 445, 390, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(702, 50, "ФАЗА 2: Ключ Q1 РОЗІМКНЕНО (Розмагнічування)", size=13, color=BLUE, bold=True))

    b, w, h = textbox(702, 100, "1. Первинний струм розірвано; Ns знеструмлена, D1 закритий\n"
                                "2. Дросель L РОЗРЯДЖАЄТЬСЯ в навантаження крізь діод D2\n"
                                "3. Обмотка Nr скидає струм Im крізь Dr назад у джерело Vin",
                      size=11, pad=8, fill="#ffffff", stroke=BLUE)
    f.append(b)

    # Спрощена схема фази 2
    f.append(rect(515, 170, 70, 90, fill="#ffffff", stroke=GOLD, sw=2))
    f.append(text(550, 205, "Трансф.\nNr скидання", size=11, color=GOLD, bold=True))
    f.append(line(550, 170, 550, 145, color=WARN, sw=2))
    f.append(arrow(550, 145, 500, 145, color=WARN, sw=2))
    f.append(text(525, 130, "Dr скидає в Vin", size=10, color=WARN, bold=True))

    b, w, h = textbox(550, 335, "Q1 ВИКЛ\n(розімкнено)", size=11, pad=6, fill="#fdecea", stroke=POS)
    f.append(b)

    b, w, h = textbox(660, 300, "D2 ВКЛ\n(струм самоіндукції)", size=11, pad=6, fill="#eafaf1", stroke=FIELD)
    f.append(b)

    b, w, h = textbox(760, 190, "Дросель L\n(розряд)", size=11, pad=6, fill="#ffffff", stroke=GOLD)
    f.append(b)
    f.append(line(660, 270, 660, 190, color=FIELD, sw=2.5))
    f.append(line(660, 190, 720, 190, color=FIELD, sw=2.5))
    f.append(arrow(680, 190, 710, 190, color=FIELD, sw=2.5))
    f.append(line(800, 190, 890, 190, color=FIELD, sw=2.5))
    f.append(arrow(820, 190, 860, 190, color=FIELD, sw=2.5))
    f.append(text(855, 175, "до Rн", size=11, color=FIELD, bold=True))

    return render(os.path.join(IMG, "phases.svg"), W, H, *f)


def fig_core_saturation():
    """Фізика накопичення магнітного потоку та насичення осердя при відсутності розмагнічування."""
    W, H = 900, 420
    f = []

    # Ліва частина: Петля гістерезису B-H
    f.append(rect(20, 20, 410, 380, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(225, 45, "Петля гістерезису B-H фериту", size=13, color=INK, bold=True))

    # Осі
    f.append(line(60, 220, 400, 220, color=MUTED, sw=1.5))
    f.append(arrow(400, 220, 415, 220, color=MUTED, sw=1.5))
    f.append(text(410, 205, "H (струм)", size=11, color=MUTED, bold=True))

    f.append(line(225, 360, 225, 80, color=MUTED, sw=1.5))
    f.append(arrow(225, 80, 225, 65, color=MUTED, sw=1.5))
    f.append(text(240, 75, "B (індукція / потік)", size=11, color=MUTED, bold=True))

    # Лінія насичення Bsat
    f.append(line(60, 110, 390, 110, color=POS, sw=1.5, dash="6 4"))
    f.append(text(130, 100, "+ Bsat (насичення ≈ 0.35 Тл)", size=11, color=POS, bold=True))

    # Траєкторія нормального циклу (Forward з розмагнічуванням)
    f.append('<path d="M 225 220 C 260 210, 320 180, 330 150 C 310 160, 250 200, 225 220" fill="#eafaf1" stroke="#27ae60" stroke-width="2.5"/>')
    f.append(text(285, 240, "Робочий розмах ΔB\n(з поверненням у 0)", size=11, color=FIELD, bold=True))

    # Катастрофічне звалювання без розмагнічування
    f.append('<path d="M 225 220 Q 280 180 330 150 Q 360 125 385 110 L 400 108" fill="none" stroke="#c0392b" stroke-width="2.5" stroke-dasharray="4 3"/>')
    f.append(text(330, 85, "Дисбаланс: звалювання в Bsat!", size=11, color=POS, bold=True))

    # Права частина: Наслідки насичення
    f.append(rect(450, 20, 430, 380, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(665, 45, "Ланцюгова реакція руйнування", size=13, color=POS, bold=True))

    steps = [
        ("1. Неповне розмагнічування", "Залишковий потік Φ0 зростає щоциклу (flux walking)"),
        ("2. Досягнення порогу Bsat", "Домени фериту повністю орієнтовані за полем"),
        ("3. Колапс проникності", "μr падає від 2000...3000 до 1 (повітряне осердя)"),
        ("4. Обвал індуктивності Lm", "Lm падає у тисячі разів: Lm → 0"),
        ("5. Струмовий вибух і пробій", "Струм ключа стрибає до сотень ампер → смерть MOSFET")
    ]

    y_cur = 85
    for title_s, desc_s in steps:
        b, w, h = textbox(665, y_cur, title_s + "\n" + desc_s, size=11, pad=6,
                          fill="#ffffff", stroke=POS if "вибух" in title_s else MUTED, sw=1.5)
        f.append(b)
        y_cur += 62

    return render(os.path.join(IMG, "core-saturation.svg"), W, H, *f)


def fig_reset_methods():
    """Порівняння 4 методів розмагнічування осердя прямоходового перетворювача."""
    W, H = 960, 480
    f = []

    cards = [
        ("1. Третя обмотка (Tertiary)",
         "• Обмотка Nr + діод Dr повертають енергію у Vin\n"
         "• Vds(max) = 2 · Vin (при Nr = Np)\n"
         "• Жорстке обмеження: D < 0.5\n"
         "• Класичне просте рішення без втрат тепла",
         POS, 240, 130),
        ("2. RCD-кламп розмагнічування",
         "• Енергія Lm гаситься в тепло на резисторі R\n"
         "• Vds(max) = Vin + Vclamp (може бути > 2 Vin)\n"
         "• Дозволяє D > 0.5 завдяки швидшому спаду\n"
         "• Постійні втрати потужності (низький ККД)",
         WARN, 720, 130),
        ("3. Двотранзисторний (Two-Switch)",
         "• 2 ключі (верхній і нижній) + 2 діоди скидання\n"
         "• Vds(max) = РІВНО Vin на кожному ключі!\n"
         "• Енергія витоку повертається без викидів\n"
         "• D < 0.5; потрібен плаваючий драйвер",
         FIELD, 240, 360),
        ("4. Активний кламп (Active Clamp)",
         "• Допоміжний MOSFET Qaux + конденсатор Cclamp\n"
         "• Повна рекуперація енергії намагнічування\n"
         "• М'яке перемикання (ZVS) транзисторів\n"
         "• Дозволяє D > 0.5 (до 0.7); висока складність",
         BLUE, 720, 360)
    ]

    for title_s, body_s, col, cx, cy in cards:
        b, w, h = textbox(cx, cy, title_s + "\n\n" + body_s, size=11, pad=12,
                          fill="#ffffff", stroke=col, sw=2, min_w=440)
        f.append(b)

    return render(os.path.join(IMG, "reset-methods.svg"), W, H, *f)


def fig_waveforms():
    """Часові діаграми напруг і струмів у CCM-режимі прямоходового перетворювача."""
    W, H = 920, 520
    f = []

    # Сітка часу: 2 повних періоди T
    t0, t1, t2, t3, t4 = 140, 280, 460, 600, 780
    f.append(rect(15, 15, 890, 490, fill=FILL, stroke=LINE, sw=1.5, rx=8))

    # Вертикальні лінії меж тактів
    for tx in [t0, t1, t2, t3, t4]:
        f.append(line(tx, 40, tx, 480, color="#d0d5dd", sw=1.2, dash="4 4"))

    f.append(text((t0 + t1) / 2, 35, "ton = D·T", size=11, color=POS, bold=True))
    f.append(text((t1 + t2) / 2, 35, "treset", size=11, color=WARN, bold=True))
    f.append(text((t2 + t3) / 2, 35, "ton", size=11, color=POS, bold=True))

    signals = [
        ("Vgs (Ключ Q1)", 80,
         [(t0, 100), (t0, 60), (t1, 60), (t1, 100), (t2, 100), (t2, 60), (t3, 60), (t3, 100), (t4, 100)],
         POS),
        ("Vds (Стік Q1)", 160,
         [(t0, 180), (t1, 180), (t1, 130), (t2, 130), (t2, 155), (t3, 155), (t3, 180), (t4, 180)],
         POS),
        ("Im (Струм нам.)", 245,
         [(t0, 265), (t1, 220), (t2, 265), (t3, 220), (t4, 265)],
         GOLD),
        ("Vx (Перед L)", 335,
         [(t0, 355), (t0, 310), (t1, 310), (t1, 355), (t2, 355), (t2, 310), (t3, 310), (t3, 355), (t4, 355)],
         FIELD),
        ("iL (Струм L)", 430,
         [(t0, 445), (t1, 410), (t2, 435), (t3, 410), (t4, 445)],
         BLUE)
    ]

    for name, y_base, pts, col in signals:
        f.append(line(t0 - 30, y_base + 20, t4 + 30, y_base + 20, color=MUTED, sw=1.2))
        f.append(text(75, y_base, name, size=12, color=col, bold=True))

        # Малювання сигналу
        d_str = "M %.1f %.1f " % pts[0]
        for px, py in pts[1:]:
            d_str += "L %.1f %.1f " % (px, py)
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d_str, col))

    # Додаткові позначки рівнів
    f.append(text(t4 + 40, 130, "2·Vin", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(t4 + 40, 155, "Vin", size=11, color=MUTED, bold=True, anchor="start"))
    f.append(text(t4 + 40, 310, "Vin·Ns/Np", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(t4 + 40, 425, "Iout", size=11, color=BLUE, bold=True, anchor="start"))

    return render(os.path.join(IMG, "waveforms.svg"), W, H, *f)


def fig_duty_cycle_limit():
    """Вольт-секундний баланс та обмеження коефіцієнта заповнення D."""
    W, H = 940, 420
    f = []

    # Ліва частина: Площі вольт-секунд
    f.append(rect(15, 20, 440, 380, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(235, 45, "Вольт-секундний баланс: S(вкл) = S(розмагн)", size=12, color=INK, bold=True))

    # Прямокутник заряду
    f.append(rect(55, 95, 140, 100, fill="#eafaf1", stroke=POS, sw=2))
    f.append(text(125, 145, "+ Vin · ton\n(Намагнічування)", size=11, color=POS, bold=True))

    # Прямокутник розмагнічування
    f.append(rect(215, 95, 140, 100, fill="#fdecea", stroke=WARN, sw=2))
    f.append(text(285, 145, "- Vreset · treset\n(Розмагнічування)", size=11, color=WARN, bold=True))

    b, w, h = textbox(235, 280, "Умова рівноваги осердя:\n"
                                "Vin · ton = Vreset · treset\n"
                                "Якщо Nr = Np  ⇒  Vreset = Vin  ⇒  treset = ton\n"
                                "Оскільки ton + treset ≤ T  ⇒  2 · ton ≤ T  ⇒  D ≤ 0.5",
                      size=11, pad=8, fill="#ffffff", stroke=POS, sw=1.5)
    f.append(b)

    # Права частина: Графік залежності Dmax від Vreset/Vin
    f.append(rect(475, 20, 450, 380, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(700, 45, "Компроміс: Шпаруватість vs Напруга на ключі", size=12, color=INK, bold=True))

    # Таблиця порівняння параметрів
    table_text = (
        "Співвідношення     Dmax      Vds(peak)\n"
        "Nr = 2 · Np        0.33      1.5 · Vin  (мале навантаження ключа)\n"
        "Nr = Np (базове)   0.50      2.0 · Vin  (симетричний баланс)\n"
        "Nr = 0.5 · Np      0.66      3.0 · Vin  (небезпечно високий Vds)\n"
        "Active Clamp       0.70      Vin/(1-D)  (гнучкий плаваючий кламп)"
    )
    b, w, h = textbox(700, 160, table_text, size=10, pad=8, fill="#ffffff", stroke=MUTED, sw=1.5)
    f.append(b)

    b, w, h = textbox(700, 305, "Золоте правило інженера:\n"
                                "Для надійної роботи з обмоткою Nr = Np\n"
                                "контролер обмежують апаратно: Dmax ≤ 0.45...0.47\n"
                                "(запас часу на розмагнічування при стрибках)",
                      size=11, pad=8, fill="#eaf0fd", stroke=BLUE, sw=1.5)
    f.append(b)

    return render(os.path.join(IMG, "duty-cycle-limit.svg"), W, H, *f)


if __name__ == "__main__":
    outs = [
        fig_topology(),
        fig_phases(),
        fig_core_saturation(),
        fig_reset_methods(),
        fig_waveforms(),
        fig_duty_cycle_limit(),
    ]
    for o in outs:
        print("written:", o)
