# -*- coding: utf-8 -*-
"""Фігури для теми switching-psu (імпульсний блок живлення) та її вставок.
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5). Вивід у ./img/.

    python figs.py
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *  # noqa: E402,F403

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

GOLD = "#b8860b"   # осердя / магнітне / світло
HOT = "#fdecea"    # тло гарячої / первинної сторони
COLD = "#e9f7ef"   # тло холодної / вторинної сторони
BLUE = "#2457d6"   # керування / сигнали
PE_COL = "#27ae60" # захисне заземлення


def _coil(x, y_top, y_bot, n=5, r=9, left=True, color=GOLD):
    """Обмотка як ланцюжок півдуг уздовж вертикалі."""
    step = (y_bot - y_top) / n
    d = "M %.1f %.1f " % (x, y_top)
    sweep = 0 if left else 1
    yy = y_top
    for _ in range(n):
        d += "A %.1f %.1f 0 0 %d %.1f %.1f " % (r, step / 2, sweep, x, yy + step)
        yy += step
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, color)


def fig_architecture():
    """Повна архітектура мережевого ізольованого імпульсного джерела (SMPS):
    від мережі 230 В через фільтр, випрямляч, активний PFC, перетворювач,
    імпульсний трансформатор, синхронний випрямляч та зворотний зв'язок."""
    W, H = 1000, 480
    bx = 570  # лінія бар'єра ізоляції
    f = []

    # Тло двох зон: ліва (первинна) та права (вторинна) з проміжком під бар'єр
    f.append(rect(15, 60, bx - 15 - 70, 395, fill=HOT, stroke=POS, sw=1.5, rx=8))
    f.append(rect(bx + 70, 60, W - 15 - (bx + 70), 395, fill=COLD, stroke=FIELD, sw=1.5, rx=8))

    y_pwr = 160
    y_fb = 355

    # Лінія бар'єра розбита на сегменти (не перетинає компоненти й підпис)
    f.append(line(bx, 48, bx, y_pwr - 50, color=POS, sw=2.2, dash="8 6"))
    f.append(line(bx, y_pwr + 68, bx, y_fb - 42, color=POS, sw=2.2, dash="8 6"))
    f.append(line(bx, y_fb + 42, bx, 420, color=POS, sw=2.2, dash="8 6"))
    f.append(text(bx, 38, "БАР'ЄР ГАЛЬВАНІЧНОЇ ІЗОЛЯЦІЇ (3-4 кВ RMS)", size=12, color=POS, bold=True))

    # Заголовки зон
    f.append(text((15 + bx - 70) / 2, 84, "ПЕРВИННА СТОРОНА («ГАРЯЧА», 230 В / 400 В)", size=13, color=POS, bold=True))
    f.append(text((bx + 70 + W - 15) / 2, 84, "ВТОРИННА СТОРОНА («ХОЛОДНА», БЕЗПЕЧНА SELV)", size=13, color=FIELD, bold=True))

    # Блоки первинної сторони
    b1, w1, h1 = textbox(75, y_pwr, "Вхідний фільтр\nEMI + захист\n(MOV, NTC, CMC)", size=11,
                         fill="#ffffff", stroke=POS, sw=1.6)
    f.append(b1)

    b2, w2, h2 = textbox(195, y_pwr, "Діодний міст\n+ активний PFC\n(Boost 400 В)", size=11,
                         fill="#ffffff", stroke=POS, sw=1.6)
    f.append(b2)

    b3, w3, h3 = textbox(320, y_pwr, "Накопичувач\nBulk 400 В\n(енергія циклу)", size=11,
                         fill="#ffffff", stroke=POS, sw=1.6)
    f.append(b3)

    b4, w4, h4 = textbox(435, y_pwr, "Силові ключі\n(MOSFET/GaN\n50-200 кГц)", size=11,
                         fill="#ffffff", stroke=POS, sw=1.6)
    f.append(b4)

    # Трансформатор на бар'єрі
    f.append(_coil(bx - 12, y_pwr - 35, y_pwr + 35, n=4, r=8, left=True, color=GOLD))
    f.append(_coil(bx + 12, y_pwr - 35, y_pwr + 35, n=4, r=8, left=False, color=GOLD))
    f.append(line(bx - 2.5, y_pwr - 42, bx - 2.5, y_pwr + 42, color=GOLD, sw=2))
    f.append(line(bx + 2.5, y_pwr - 42, bx + 2.5, y_pwr + 42, color=GOLD, sw=2))
    f.append(text(bx, y_pwr + 56, "Трансформатор", size=10, color=GOLD, bold=True))

    # Блоки вторинної сторони
    b5, w5, h5 = textbox(715, y_pwr, "Синхронний\nвипрямляч (SR)\nабо Шотткі", size=11,
                         fill="#ffffff", stroke=FIELD, sw=1.6)
    f.append(b5)

    b6, w6, h6 = textbox(835, y_pwr, "Вихідний\nLC-фільтр\n(Low ESR)", size=11,
                         fill="#ffffff", stroke=FIELD, sw=1.6)
    f.append(b6)

    b7, w7, h7 = textbox(935, y_pwr, "Вихід DC\n(12 В / 5 В\nстабільні)", size=11,
                         fill="#ffffff", stroke=FIELD, sw=1.8, bold=True)
    f.append(b7)

    # Стрілки прямого силового потоку
    f.append(arrow(130, y_pwr, 148, y_pwr, color=POS, sw=2))
    f.append(arrow(245, y_pwr, 270, y_pwr, color=POS, sw=2))
    f.append(arrow(368, y_pwr, 390, y_pwr, color=POS, sw=2))
    f.append(arrow(480, y_pwr, bx - 25, y_pwr, color=POS, sw=2))
    f.append(arrow(bx + 25, y_pwr, 660, y_pwr, color=FIELD, sw=2))
    f.append(arrow(770, y_pwr, 788, y_pwr, color=FIELD, sw=2))
    f.append(arrow(882, y_pwr, 898, y_pwr, color=FIELD, sw=2))

    # Вхід 230 В
    f.append(text(75, 96, "Мережа 230 В~", size=11, color=POS, bold=True))
    f.append(arrow(75, 106, 75, 125, color=POS, sw=1.8))

    # Нижній ярус: Контур зворотного зв'язку
    b_ref, w_ref, h_ref = textbox(835, y_fb, "Дільник напруги\n+ опорна ІС TL431\n+ Type II/III комп.", size=11,
                                  fill="#ffffff", stroke=FIELD, sw=1.6)
    f.append(b_ref)

    b_opto, w_opto, h_opto = textbox(bx, y_fb, "Оптопара PC817\n(передача світлом\nкрізь бар'єр)", size=11,
                                     fill="#fff7e6", stroke=GOLD, sw=1.8, bold=True)
    f.append(b_opto)

    b_pwm, w_pwm, h_pwm = textbox(250, y_fb, "ШІМ-контролер\n(модуляція шпаруватості D,\nструмовий захист CS)", size=11,
                                  fill="#ffffff", stroke=BLUE, sw=1.6)
    f.append(b_pwm)

    # З'єднання зворотного зв'язку
    f.append(arrow(935, 200, 935, y_fb, color=FIELD, sw=1.8))
    f.append(arrow(935, y_fb, 905, y_fb, color=FIELD, sw=1.8))
    f.append(arrow(765, y_fb, bx + 70, y_fb, color=FIELD, sw=1.8))
    f.append(arrow(bx - 70, y_fb, 360, y_fb, color=GOLD, sw=2))
    f.append(line(250, y_fb - 30, 250, 245, color=BLUE, sw=1.8))
    f.append(arrow(250, 245, 400, 200, color=BLUE, sw=1.8))
    f.append(text(300, 235, "ШІМ Gate", size=11, color=BLUE, bold=True))

    # Додаткові пояснення внизу
    f.append(text(bx, 445, "Силовий потік (вгорі) і зворотний зв'язок (внизу) перетинають ізоляцію без електричного контакту",
                  size=11, color=MUTED))

    return render(os.path.join(IMG, "architecture.svg"), W, H, *f)


def fig_emi_filter():
    """Схема вхідного кола захисту та фільтра електромагнітних завад (EMI):
    запобіжник, варистор MOV, термістор NTC, конденсатори X та Y, синфазний дросель."""
    W, H = 880, 360
    f = []

    f.append(text(W / 2, 30, "Вхідний фільтр електромагнітних завад (EMI) та захист мережі", size=15, color=INK, bold=True))

    # Лінії L, N, PE
    y_L = 80
    y_N = 220
    y_PE = 310

    f.append(line(40, y_L, 840, y_L, color=POS, sw=2.2))
    f.append(line(40, y_N, 840, y_N, color=BLUE, sw=2.2))
    f.append(line(40, y_PE, 840, y_PE, color=PE_COL, sw=2, dash="6 4"))

    f.append(text(25, y_L + 4, "L", size=14, color=POS, bold=True))
    f.append(text(25, y_N + 4, "N", size=14, color=BLUE, bold=True))
    f.append(text(25, y_PE + 4, "PE", size=13, color=PE_COL, bold=True))

    # 1. Запобіжник Fuse на лінії L
    f.append(rect(80, y_L - 10, 45, 20, fill="#ffffff", stroke=POS, sw=1.8, rx=3))
    f.append(line(70, y_L, 80, y_L, color=POS, sw=2.2))
    f.append(line(125, y_L, 135, y_L, color=POS, sw=2.2))
    f.append(text(102, y_L - 18, "Fuse", size=11, color=POS, bold=True))
    f.append(text(102, y_L + 24, "струм КЗ", size=9, color=MUTED))

    # 2. Термістор NTC на лінії L
    f.append(rect(160, y_L - 10, 45, 20, fill="#ffffff", stroke=POS, sw=1.8, rx=3))
    f.append(line(162, y_L + 8, 203, y_L - 8, color=POS, sw=1.5))
    f.append(text(182, y_L - 18, "NTC", size=11, color=POS, bold=True))
    f.append(text(182, y_L + 24, "пуск Inrush", size=9, color=MUTED))

    # 3. Варистор MOV між L і N
    f.append(line(245, y_L, 245, y_N, color=INK, sw=1.6))
    f.append(rect(230, (y_L + y_N) / 2 - 16, 30, 32, fill="#ffffff", stroke=POS, sw=1.8, rx=3))
    f.append(line(225, (y_L + y_N) / 2 + 18, 265, (y_L + y_N) / 2 - 18, color=POS, sw=1.6))
    f.append(text(245, (y_L + y_N) / 2 - 24, "MOV (варистор)", size=11, color=POS, bold=True))
    f.append(text(245, (y_L + y_N) / 2 + 32, "імпульси Surge", size=9, color=MUTED))

    # 4. Конденсатор X1/X2 між L і N (диференційний шум)
    f.append(line(340, y_L, 340, (y_L + y_N) / 2 - 8, color=INK, sw=1.6))
    f.append(line(340, y_N, 340, (y_L + y_N) / 2 + 8, color=INK, sw=1.6))
    f.append(line(325, (y_L + y_N) / 2 - 8, 355, (y_L + y_N) / 2 - 8, color=INK, sw=2.5))
    f.append(line(325, (y_L + y_N) / 2 + 8, 355, (y_L + y_N) / 2 + 8, color=INK, sw=2.5))
    f.append(text(340, (y_L + y_N) / 2 - 20, "X-конденсатор (Cx)", size=11, color=INK, bold=True))
    f.append(text(340, (y_L + y_N) / 2 + 24, "диференційний шум L-N", size=9, color=MUTED))

    # 5. Синфазний дросель (Common-Mode Choke)
    cx_cmc = 480
    f.append(rect(cx_cmc - 40, y_L - 30, 80, 190, fill="#f4f6f8", stroke=GOLD, sw=1.6, rx=6))
    f.append(_coil(cx_cmc - 15, y_L - 18, y_L + 18, n=3, r=7, left=True, color=GOLD))
    f.append(_coil(cx_cmc + 15, y_N - 18, y_N + 18, n=3, r=7, left=False, color=GOLD))
    f.append(line(cx_cmc - 2, y_L - 22, cx_cmc - 2, y_N + 22, color=GOLD, sw=2))
    f.append(line(cx_cmc + 2, y_L - 22, cx_cmc + 2, y_N + 22, color=GOLD, sw=2))
    f.append(text(cx_cmc, (y_L + y_N) / 2, "Синфазний\nдросель (CMC)", size=11, color=GOLD, bold=True))

    # 6. Конденсатори Y1/Y2 на захисне заземлення PE
    cx_y = 660
    # Y-cap від L до PE
    f.append(line(cx_y - 25, y_L, cx_y - 25, (y_L + y_PE) / 2 - 8, color=INK, sw=1.5))
    f.append(line(cx_y - 25, y_PE, cx_y - 25, (y_L + y_PE) / 2 + 8, color=INK, sw=1.5))
    f.append(line(cx_y - 37, (y_L + y_PE) / 2 - 8, cx_y - 13, (y_L + y_PE) / 2 - 8, color=INK, sw=2.5))
    f.append(line(cx_y - 37, (y_L + y_PE) / 2 + 8, cx_y - 13, (y_L + y_PE) / 2 + 8, color=INK, sw=2.5))
    f.append(text(cx_y - 25, (y_L + y_PE) / 2 - 18, "Cy (L-PE)", size=10, color=PE_COL, bold=True))

    # Y-cap від N до PE
    f.append(line(cx_y + 25, y_N, cx_y + 25, (y_N + y_PE) / 2 - 8, color=INK, sw=1.5))
    f.append(line(cx_y + 25, y_PE, cx_y + 25, (y_N + y_PE) / 2 + 8, color=INK, sw=1.5))
    f.append(line(cx_y + 13, (y_N + y_PE) / 2 - 8, cx_y + 37, (y_N + y_PE) / 2 - 8, color=INK, sw=2.5))
    f.append(line(cx_y + 13, (y_N + y_PE) / 2 + 8, cx_y + 37, (y_N + y_PE) / 2 + 8, color=INK, sw=2.5))
    f.append(text(cx_y + 25, (y_N + y_PE) / 2 - 18, "Cy (N-PE)", size=10, color=PE_COL, bold=True))

    # Вихід на міст
    f.append(arrow(780, y_L, 840, y_L, color=POS, sw=2))
    f.append(arrow(780, y_N, 840, y_N, color=BLUE, sw=2))
    f.append(text(810, (y_L + y_N) / 2, "до діодного\nмоста", size=10, color=MUTED))

    return render(os.path.join(IMG, "emi-filter.svg"), W, H, *f)


def fig_pfc_waveform():
    """Порівняння форм вхідного струму без PFC (вузькі піки, високий THD, PF ~ 0.6)
    та з активним Boost PFC (чиста синусоїда у фазі з напругою, PF > 0.98)."""
    W, H = 880, 360
    f = []
    midx = W / 2

    # Ліва половина: БЕЗ PFC
    f.append(rect(20, 45, midx - 30, 295, fill="#fff9f8", stroke=POS, sw=1.5, rx=6))
    f.append(text((20 + midx - 10) / 2, 70, "Без PFC (міст + Bulk-конденсатор)", size=13, color=POS, bold=True))
    f.append(text((20 + midx - 10) / 2, 90, "PF ≈ 0.55–0.65 · THD > 80% · вузькі піки струму", size=10, color=MUTED))

    # Графік ліворуч
    L1, R1, T1, B1 = 50, midx - 30, 120, 280
    Y0_1 = (T1 + B1) / 2
    f.append(line(L1, Y0_1, R1, Y0_1, color=MUTED, sw=1, dash="4 4"))

    # Синусоїда напруги (сіра пунктирна)
    pts_v1 = []
    import math
    for i in range(101):
        x = L1 + (R1 - L1) * (i / 100.0)
        angle = (i / 100.0) * 2 * math.pi
        y = Y0_1 - math.sin(angle) * 55
        pts_v1.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4 3"/>' % (" ".join(pts_v1), MUTED))
    f.append(text(L1 + 30, Y0_1 - 45, "Напруга U(t)", size=10, color=MUTED))

    # Струм (імпульсні піки біля верхівок напруги)
    pts_i1 = []
    for i in range(101):
        x = L1 + (R1 - L1) * (i / 100.0)
        angle = (i / 100.0) * 2 * math.pi
        s = math.sin(angle)
        # діоди проводять лише при |s| > 0.85
        curr = 0.0
        if s > 0.80:
            curr = ((s - 0.80) / 0.20) ** 2 * 68
        elif s < -0.80:
            curr = -((abs(s) - 0.80) / 0.20) ** 2 * 68
        y = Y0_1 - curr
        pts_i1.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts_i1), POS))
    f.append(text(L1 + 100, Y0_1 - 65, "Струм I(t) — імпульси!", size=10, color=POS, bold=True))

    # Права половина: З АКТИВНИМ PFC
    f.append(rect(midx + 10, 45, midx - 30, 295, fill="#f5fbf7", stroke=FIELD, sw=1.5, rx=6))
    f.append(text((midx + 10 + W - 20) / 2, 70, "З активним Boost PFC", size=13, color=FIELD, bold=True))
    f.append(text((midx + 10 + W - 20) / 2, 90, "PF > 0.98 · THD < 5% · синусоїдальний струм у фазі", size=10, color=MUTED))

    L2, R2, T2, B2 = midx + 30, W - 40, 120, 280
    Y0_2 = (T2 + B2) / 2
    f.append(line(L2, Y0_2, R2, Y0_2, color=MUTED, sw=1, dash="4 4"))

    pts_v2 = []
    pts_i2 = []
    for i in range(101):
        x = L2 + (R2 - L2) * (i / 100.0)
        angle = (i / 100.0) * 2 * math.pi
        y_v = Y0_2 - math.sin(angle) * 55
        y_i = Y0_2 - math.sin(angle) * 48
        pts_v2.append("%.1f,%.1f" % (x, y_v))
        pts_i2.append("%.1f,%.1f" % (x, y_i))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4 3"/>' % (" ".join(pts_v2), MUTED))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts_i2), FIELD))
    f.append(text(L2 + 30, Y0_2 - 45, "Напруга U(t)", size=10, color=MUTED))
    f.append(text(L2 + 115, Y0_2 - 35, "Струм I(t) у фазі", size=10, color=FIELD, bold=True))

    f.append(text(W / 2, 320, "Активний PFC формує струм пропорційно миттєвій напрузі, усуваючи гармонійне навантаження на електромережу",
                  size=11, color=MUTED))

    return render(os.path.join(IMG, "pfc-waveform.svg"), W, H, *f)


def fig_topologies():
    """Порівняння основних перетворювальних топологій SMPS: Flyback, Forward, LLC Resonant."""
    W, H = 940, 360
    f = []

    f.append(text(W / 2, 30, "Порівняння топологій імпульсних перетворювачів", size=15, color=INK, bold=True))

    col_w = 280
    gap = 25
    x_start = 35

    topos = [
        ("Flyback (зворотноходовий)", "< 75–100 Вт", POS, [
            "• Спарена котушка з зазором",
            "• Накопичення у фазі ON,",
            "  віддача у фазі OFF",
            "• Мінімум компонентів",
            "• Великі пульсації струму",
            "• Застосування: зарядки, роутери"
        ]),
        ("Forward (прямоходовий)", "100–300 Вт", BLUE, [
            "• Справжній трансформатор",
            "• Пряма передача енергії в ON",
            "• Обов'язкова обмотка розмагнічення",
            "• Вихідний накопичувальний дросель",
            "• Менший піковий струм",
            "• Застосування: сервери, промисловість"
        ]),
        ("LLC Resonant (резонансний)", "> 200 Вт – кіловати", FIELD, [
            "• Резонансний контур Lr-Cr-Lm",
            "• М'яка комутація ZVS / ZCS",
            "• Мінімальні втрати на ключах",
            "• ККД > 94–96%",
            "• Робота на частотах 100–500 кГц",
            "• Застосування: блоки живлення ПК, EV"
        ]),
    ]

    for idx, (title, pwr, col, bullets) in enumerate(topos):
        x0 = x_start + idx * (col_w + gap)
        f.append(rect(x0, 55, col_w, 280, fill="#ffffff", stroke=col, sw=1.8, rx=6))
        f.append(rect(x0, 55, col_w, 42, fill=col, stroke=col, sw=1.8, rx=6))
        f.append(text(x0 + col_w / 2, 75, title.split(" (")[0], size=13, color="#ffffff", bold=True))
        f.append(text(x0 + col_w / 2, 90, "(" + title.split(" (")[1], size=10, color="#ffffff"))
        f.append(text(x0 + col_w / 2, 118, "Діапазон потужності: " + pwr, size=11, color=col, bold=True))
        f.append(line(x0 + 15, 130, x0 + col_w - 15, 130, color=MUTED, sw=1, dash="3 3"))

        y_b = 152
        for b in bullets:
            f.append(text(x0 + 15, y_b, b, size=11, color=INK, anchor="start"))
            y_b += 22

    return render(os.path.join(IMG, "topologies.svg"), W, H, *f)


def fig_feedback_loop():
    """Контур зворотного зв'язку крізь ізоляцію: дільник напруги, опорне джерело TL431,
    ланцюг компенсації Type II, оптопара PC817 та вхід ШІМ-контролера COMP."""
    W, H = 920, 420
    bx = W / 2
    f = []

    y_opto = 180

    # Тло первинної та вторинної сторін з проміжком під бар'єр ізоляції
    f.append(rect(25, 55, bx - 25 - 65, 340, fill=HOT, stroke=POS, sw=1.5, rx=6))
    f.append(rect(bx + 65, 55, W - 25 - (bx + 65), 340, fill=COLD, stroke=FIELD, sw=1.5, rx=6))

    # Лінія бар'єра розбита на сегменти (не проходить крізь оптопару)
    f.append(line(bx, 45, bx, y_opto - 42, color=POS, sw=2, dash="8 6"))
    f.append(line(bx, y_opto + 42, bx, 400, color=POS, sw=2, dash="8 6"))
    f.append(text(bx, 35, "БАР'ЄР ІЗОЛЯЦІЇ", size=12, color=POS, bold=True))

    f.append(text((25 + bx - 65) / 2, 78, "ПЕРВИННА (ШІМ-контролер)", size=12, color=POS, bold=True))
    f.append(text((bx + 65 + W - 25) / 2, 78, "ВТОРИННА (Вихід Vout + TL431)", size=12, color=FIELD, bold=True))

    # Вторинна сторона: Vout шина
    y_vout = 105
    f.append(line(bx + 30, y_vout, W - 40, y_vout, color=FIELD, sw=2))
    f.append(text(W - 35, y_vout + 4, "Vout", size=12, color=FIELD, bold=True))

    # Дільник R1 / R2 біля правого краю
    cx_div = W - 90
    f.append(line(cx_div, y_vout, cx_div, y_vout + 25, color=INK, sw=1.5))
    f.append(rect(cx_div - 12, y_vout + 25, 24, 28, fill="#ffffff", stroke=INK, sw=1.5))
    f.append(text(cx_div, y_vout + 43, "R1", size=11, color=INK, bold=True))
    f.append(line(cx_div, y_vout + 53, cx_div, y_vout + 75, color=INK, sw=1.5))
    f.append(rect(cx_div - 12, y_vout + 75, 24, 28, fill="#ffffff", stroke=INK, sw=1.5))
    f.append(text(cx_div, y_vout + 93, "R2", size=11, color=INK, bold=True))
    f.append(line(cx_div, y_vout + 103, cx_div, y_vout + 130, color=INK, sw=1.5))
    f.append(line(cx_div - 15, y_vout + 130, cx_div + 15, y_vout + 130, color=FIELD, sw=1.5))
    f.append(text(cx_div, y_vout + 148, "GND", size=10, color=FIELD))

    # Опорна ІС TL431
    cx_tl = bx + 220
    y_tl = 265
    f.append(rect(cx_tl - 40, y_tl - 25, 80, 50, fill="#ffffff", stroke=FIELD, sw=1.8, rx=4))
    f.append(text(cx_tl, y_tl - 6, "TL431", size=12, color=FIELD, bold=True))
    f.append(text(cx_tl, y_tl + 12, "Vref = 2.495 В", size=10, color=MUTED))

    # Підключення середньої точки дільника до входу Ref TL431
    y_ref_line = y_vout + 64
    f.append(line(cx_div - 12, y_ref_line, cx_tl + 25, y_ref_line, color=INK, sw=1.5))
    f.append(line(cx_tl + 25, y_ref_line, cx_tl + 25, y_tl - 25, color=INK, sw=1.5))
    f.append(arrow(cx_tl + 25, y_tl - 25, cx_tl + 25, y_tl - 20, color=INK, sw=1.5))
    f.append(text(cx_tl + 25, y_tl - 32, "Ref", size=10, color=INK, bold=True))

    # Анод TL431 на GND
    f.append(line(cx_tl, y_tl + 25, cx_tl, y_tl + 55, color=FIELD, sw=1.5))
    f.append(line(cx_tl - 15, y_tl + 55, cx_tl + 15, y_tl + 55, color=FIELD, sw=1.5))
    f.append(text(cx_tl, y_tl + 72, "GND_sec", size=10, color=FIELD))

    # Оптопара PC817 на бар'єрі
    f.append(rect(bx - 55, y_opto - 35, 110, 70, fill="#fff7e6", stroke=GOLD, sw=1.8, rx=6))
    f.append(text(bx, y_opto - 20, "Оптопара PC817", size=11, color=GOLD, bold=True))
    f.append(circle(bx + 26, y_opto + 10, 13, fill="#ffffff", stroke=GOLD, sw=1.5))
    f.append(text(bx + 26, y_opto + 14, "LED", size=10, color=GOLD, bold=True))
    f.append(circle(bx - 26, y_opto + 10, 13, fill="#ffffff", stroke=POS, sw=1.5))
    f.append(text(bx - 26, y_opto + 14, "NPN", size=10, color=POS, bold=True))
    f.append(arrow(bx + 11, y_opto + 10, bx - 11, y_opto + 10, color=GOLD, sw=2))

    # Струм світлодіода від Vout через R_led
    f.append(line(bx + 85, y_vout, bx + 85, y_opto - 10, color=FIELD, sw=1.5))
    f.append(rect(bx + 75, y_vout + 20, 20, 26, fill="#ffffff", stroke=FIELD, sw=1.4))
    f.append(text(bx + 85, y_vout + 36, "R_led", size=10, color=FIELD))
    f.append(line(bx + 85, y_opto - 10, bx + 26, y_opto - 3, color=FIELD, sw=1.5))

    # Катод LED оптопари до катода TL431
    f.append(line(bx + 26, y_opto + 23, bx + 26, y_tl - 25, color=FIELD, sw=1.5))
    f.append(line(bx + 26, y_tl - 25, cx_tl - 20, y_tl - 25, color=FIELD, sw=1.5))
    f.append(text(bx + 65, y_tl - 32, "Катод", size=10, color=FIELD, bold=True))

    # Компенсація Type II (Rcomp + Ccomp між катодом і Ref)
    y_comp = y_tl - 65
    f.append(line(cx_tl - 20, y_tl - 25, cx_tl - 20, y_comp, color=GOLD, sw=1.5))
    f.append(line(cx_tl - 20, y_comp, cx_tl, y_comp, color=GOLD, sw=1.5))
    f.append(rect(cx_tl, y_comp - 10, 50, 20, fill="#ffffff", stroke=GOLD, sw=1.4))
    f.append(text(cx_tl + 25, y_comp + 4, "Rc, Cc", size=10, color=GOLD, bold=True))
    f.append(line(cx_tl + 50, y_comp, cx_tl + 75, y_comp, color=GOLD, sw=1.5))
    f.append(line(cx_tl + 75, y_comp, cx_tl + 75, y_ref_line, color=GOLD, sw=1.5))

    # Первинна сторона: ШІМ-контролер COMP pin
    cx_pwm = 140
    y_pwm = 220
    f.append(rect(cx_pwm - 55, y_pwm - 45, 110, 90, fill="#ffffff", stroke=POS, sw=1.8, rx=6))
    f.append(text(cx_pwm, y_pwm - 22, "ШІМ-контролер", size=11, color=POS, bold=True))
    f.append(text(cx_pwm, y_pwm + 4, "Вхід COMP", size=11, color=BLUE, bold=True))
    f.append(text(cx_pwm, y_pwm + 26, "модуляція ШІМ D", size=10, color=MUTED))

    # З'єднання фототранзистора оптопари до COMP
    f.append(line(bx - 26, y_opto - 3, bx - 26, y_pwm, color=POS, sw=1.5))
    f.append(line(bx - 26, y_pwm, cx_pwm + 55, y_pwm, color=POS, sw=1.5))
    f.append(arrow(cx_pwm + 65, y_pwm, cx_pwm + 55, y_pwm, color=POS, sw=1.5))

    # Емітер фототранзистора на первинну GND
    f.append(line(bx - 26, y_opto + 23, bx - 26, y_opto + 60, color=POS, sw=1.5))
    f.append(line(bx - 36, y_opto + 60, bx - 16, y_opto + 60, color=POS, sw=1.5))
    f.append(text(bx - 26, y_opto + 76, "GND_pri", size=10, color=POS))

    # Підпис принципу дії
    f.append(text(W / 2, 380, "Vout зростає → TL431 відкривається дужче → світлодіод світить яскравіше → транзистор тягне COMP донизу → шпаруватість D падає",
                  size=11, color=INK))

    return render(os.path.join(IMG, "feedback-loop.svg"), W, H, *f)


def fig_safety_creepage():
    """Правила електробезпеки на друкованій платі (PCB): Creepage (шлях витоку по поверхні),
    Clearance (повітряний зазор) та фрезерований проріз (Isolation Slot)."""
    W, H = 880, 360
    f = []

    f.append(text(W / 2, 30, "Вимоги стандартів безпеки (IEC 62368-1 / IEC 60950) на друкованій платі", size=14, color=INK, bold=True))

    bx = W / 2

    # Зони друкованої плати
    f.append(rect(40, 65, bx - 40 - 20, 220, fill=HOT, stroke=POS, sw=1.8, rx=6))
    f.append(rect(bx + 20, 65, W - 40 - (bx + 20), 220, fill=COLD, stroke=FIELD, sw=1.8, rx=6))

    f.append(text((40 + bx - 20) / 2, 90, "ПЕРВИННА ЗОНА (325–400 В)", size=12, color=POS, bold=True))
    f.append(text((bx + 20 + W - 40) / 2, 90, "ВТОРИННА ЗОНА (SELV < 60 В)", size=12, color=FIELD, bold=True))

    # Мідні провідники на платі
    f.append(rect(bx - 120, 140, 70, 30, fill=POS, stroke=POS, rx=3))
    f.append(text(bx - 85, 160, "Мідь 400 В", size=11, color="#ffffff", bold=True))

    f.append(rect(bx + 50, 140, 70, 30, fill=FIELD, stroke=FIELD, rx=3))
    f.append(text(bx + 85, 160, "Мідь SELV", size=11, color="#ffffff", bold=True))

    # Фрезерований проріз у платі (Milling Slot)
    f.append(rect(bx - 10, 110, 20, 150, fill="#ffffff", stroke=MUTED, sw=1.8, rx=4))
    f.append(line(bx, 118, bx, 252, color=MUTED, sw=1.5, dash="4 4"))
    f.append(text(bx, 275, "Фрезерований проріз у платі (Slot)", size=10, color=MUTED, bold=True))

    # 1. Clearance (найкоротша пряма крізь повітря)
    y_cl = 125
    f.append(line(bx - 50, y_cl, bx + 50, y_cl, color=BLUE, sw=2))
    f.append(arrow(bx - 10, y_cl, bx - 50, y_cl, color=BLUE, sw=2))
    f.append(arrow(bx + 10, y_cl, bx + 50, y_cl, color=BLUE, sw=2))
    f.append(text(bx, y_cl - 8, "Clearance ≥ 4.0–5.0 мм (по повітрю)", size=10, color=BLUE, bold=True))

    # 2. Creepage (шлях в обхід прорізу по поверхні діелектрика)
    y_cr = 195
    # Огинаюча лінія навколо прорізу
    f.append('<path d="M %d %d L %d %d L %d %d L %d %d L %d %d" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5 3"/>' %
             (bx - 50, y_cr, bx - 10, y_cr, bx - 10, 260, bx + 10, 260, bx + 10, y_cr, POS))
    f.append(line(bx + 10, y_cr, bx + 50, y_cr, color=POS, sw=2.2, dash="5 3"))
    f.append(text(bx, y_cr + 18, "Creepage ≥ 6.4–8.0 мм (поверхня)", size=10, color=POS, bold=True))

    # Пояснювальний блок знизу
    f.append(text(W / 2, 315, "Проріз у склотекстоліті перешкоджає утворенню струмопровідних містків від пилу та вологи (CTI),",
                  size=11, color=INK))
    f.append(text(W / 2, 335, "перетворюючи шлях витоку по поверхні на високонадійний повітряний зазор.",
                  size=11, color=INK))

    return render(os.path.join(IMG, "safety-creepage.svg"), W, H, *f)


if __name__ == "__main__":
    outs = [
        fig_architecture(),
        fig_emi_filter(),
        fig_pfc_waveform(),
        fig_topologies(),
        fig_feedback_loop(),
        fig_safety_creepage(),
    ]
    for o in outs:
        print("written:", o)
