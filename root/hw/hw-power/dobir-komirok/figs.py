# -*- coding: utf-8 -*-
"""Фігури до теми «Добір комірок: партія, матчинг, вимір внутрішнього опору».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

AMBER = "#b8860b"   # попередження / проміжний стан
REDBG = "#fbeee6"   # світлий червоний фон
BLUBG = "#eef3fb"   # світлий синій фон
GRNBG = "#e9f7ef"   # світлий зелений фон
GRYBG = "#f4f6f8"   # світлий сірий фон


# ── 1. Розподіл параметрів у партії та бінінг ──────────────────────────────────
def fig_variance_distribution():
    W, H = 880, 430
    f = [text(W / 2, 28, "Виробничий розкид партії та розбиття на кошики (бінінг)",
              size=16.5, bold=True)]

    # Осі графіка
    x0, x1 = 90, 800
    yb, yt = 330, 80

    # Смуги кошиків (Bins)
    # Зона браку зліва
    f.append(rect(x0, yt, 110, yb - yt, fill=REDBG, stroke="none", sw=0))
    # Bin 1 (найвища ємність)
    f.append(rect(x0 + 110, yt, 160, yb - yt, fill=GRNBG, stroke="none", sw=0))
    # Bin 2 (номінал)
    f.append(rect(x0 + 270, yt, 170, yb - yt, fill=BLUBG, stroke="none", sw=0))
    # Bin 3 (нижній допуск)
    f.append(rect(x0 + 440, yt, 150, yb - yt, fill=GRYBG, stroke="none", sw=0))
    # Зона браку справа
    f.append(rect(x0 + 590, yt, 120, yb - yt, fill=REDBG, stroke="none", sw=0))

    # Осі
    f.append(line(x0, yb, x1, yb, color=INK, sw=1.6))
    f.append(line(x0, yb, x0, yt, color=INK, sw=1.6))
    f.append(text(x1 - 10, yb + 32, "Ємність Q (мА·год) / Опір AC IR (мОм) →", size=11, color=INK, anchor="end"))
    f.append(text(x0 - 12, yt + 15, "Кількість комірок N", size=11, color=INK, anchor="end"))

    # Гаусоїда (розподіл партії)
    pts = [
        (90, 325), (140, 318), (180, 300), (220, 260), (260, 200),
        (300, 140), (340, 100), (380, 88), (420, 100), (460, 140),
        (500, 200), (540, 260), (580, 300), (630, 318), (710, 328)
    ]
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d, INK))

    # Вертикальні межі кошиків
    for bx in [x0 + 110, x0 + 270, x0 + 440, x0 + 590]:
        f.append(line(bx, yt, bx, yb, color=MUTED, sw=1.2, dash="4,4"))

    # Підписи кошиків
    f.append(text(x0 + 55, yt + 25, "БРАК", size=11, bold=True, color=POS))
    f.append(text(x0 + 55, yt + 42, "Outliers", size=9.5, color=POS))

    f.append(text(x0 + 190, yt + 25, "Кошик 1 (Bin A)", size=11.5, bold=True, color=FIELD))
    f.append(text(x0 + 190, yt + 42, "3040–3060 мА·год", size=10, color=FIELD))
    f.append(text(x0 + 190, yt + 58, "12.0–12.5 мОм", size=9.5, color=MUTED))

    f.append(text(x0 + 355, yt + 25, "Кошик 2 (Bin B)", size=11.5, bold=True, color=NEG))
    f.append(text(x0 + 355, yt + 42, "3015–3039 мА·год", size=10, color=NEG))
    f.append(text(x0 + 355, yt + 58, "12.6–13.1 мОм", size=9.5, color=MUTED))

    f.append(text(x0 + 515, yt + 25, "Кошик 3 (Bin C)", size=11.5, bold=True, color=INK))
    f.append(text(x0 + 515, yt + 42, "2990–3014 мА·год", size=10, color=INK))
    f.append(text(x0 + 515, yt + 58, "13.2–13.8 мОм", size=9.5, color=MUTED))

    f.append(text(x0 + 650, yt + 25, "БРАК", size=11, bold=True, color=POS))
    f.append(text(x0 + 650, yt + 42, "ΔOCV / витік", size=9.5, color=POS))

    # Стрілка вимоги
    b, _, _ = textbox(W / 2, 395,
                      "В один акумуляторний пакет збирають комірки ТІЛЬКИ з одного кошика; змішування кошиків скорочує ресурс удвічі",
                      size=11, fill=GRNBG, stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "variance-distribution.svg"), W, H, *f)


# ── 2. Паралельний перекіс струмів і тепла ─────────────────────────────────────
def fig_parallel_current_split():
    W, H = 860, 450
    f = [text(W / 2, 28, "Перекіс струмів і перегрів у паралельній парі з різним ESR",
              size=16.5, bold=True)]

    # Спільні шини
    top_y = 90
    bot_y = 320
    bus_l = 150
    bus_r = 710

    f.append(line(bus_l, top_y, bus_r, top_y, color=POS, sw=4))
    f.append(text(bus_l - 20, top_y + 5, "+ Шина", size=12.5, bold=True, color=POS, anchor="end"))
    f.append(line(bus_l, bot_y, bus_r, bot_y, color=NEG, sw=4))
    f.append(text(bus_l - 20, bot_y + 5, "− Шина", size=12.5, bold=True, color=NEG, anchor="end"))

    # Загальний струм входу і виходу
    f.append(arrow(bus_l + 30, top_y - 28, bus_l + 30, top_y - 4, color=POS, sw=2.5))
    f.append(text(bus_l + 30, top_y - 34, "I_сум = 30 А", size=11.5, bold=True, color=POS))

    f.append(arrow(bus_r - 30, bot_y + 4, bus_r - 30, bot_y + 28, color=NEG, sw=2.5))
    f.append(text(bus_r - 30, bot_y + 42, "I_сум = 30 А", size=11.5, bold=True, color=NEG))

    # Комірка 1 (низький опір — бере весь удар)
    cx1 = 300
    f.append(line(cx1, top_y, cx1, top_y + 35, color=INK, sw=2))
    # Блок комірки 1
    f.append(rect(cx1 - 65, top_y + 35, 130, 130, fill=REDBG, stroke=POS, sw=2))
    f.append(text(cx1, top_y + 58, "Комірка 1", size=12, bold=True, color=POS))
    f.append(text(cx1, top_y + 80, "R_1 = 15 мОм", size=11.5, bold=True, color=POS))
    f.append(text(cx1, top_y + 104, "I_1 = 20 А  (67%)", size=11, bold=True, color=POS))
    f.append(text(cx1, top_y + 128, "P_1 = 20²·0.015", size=10.5, color=INK))
    f.append(text(cx1, top_y + 148, "= 6.0 Вт тепла!", size=11.5, bold=True, color=POS))
    f.append(line(cx1, top_y + 165, cx1, bot_y, color=INK, sw=2))
    f.append(arrow(cx1, top_y + 12, cx1, top_y + 30, color=POS, sw=2))

    # Комірка 2 (високий опір — сачкує)
    cx2 = 560
    f.append(line(cx2, top_y, cx2, top_y + 35, color=INK, sw=2))
    # Блок комірки 2
    f.append(rect(cx2 - 65, top_y + 35, 130, 130, fill=GRNBG, stroke=FIELD, sw=1.8))
    f.append(text(cx2, top_y + 58, "Комірка 2", size=12, bold=True, color=FIELD))
    f.append(text(cx2, top_y + 80, "R_2 = 30 мОм", size=11.5, bold=True, color=FIELD))
    f.append(text(cx2, top_y + 104, "I_2 = 10 А  (33%)", size=11, bold=True, color=FIELD))
    f.append(text(cx2, top_y + 128, "P_2 = 10²·0.030", size=10.5, color=INK))
    f.append(text(cx2, top_y + 148, "= 3.0 Вт тепла", size=11.5, bold=True, color=FIELD))
    f.append(line(cx2, top_y + 165, cx2, bot_y, color=INK, sw=2))
    f.append(arrow(cx2, top_y + 12, cx2, top_y + 30, color=FIELD, sw=2))

    # Підсумок
    b, _, _ = textbox(W / 2, 400,
                      "Низькоомна комірка бере 2× струму й виділяє 2× більше тепла: вона деградує першою, тягнучи всю паралель",
                      size=11, fill=REDBG, stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "parallel-current-split.svg"), W, H, *f)


# ── 3. Послідовне замикання на найслабшу комірку ───────────────────────────────
def fig_series_capacity_bottleneck():
    W, H = 880, 440
    f = [text(W / 2, 28, "Послідовний ланцюг: найслабша комірка замикає корисну ємність",
              size=16.5, bold=True)]

    # Рівні стовпчиків
    def y_soc(pct):
        return 310 - 1.8 * pct

    cx_list = [160, 330, 500, 670]
    caps = [3000, 3000, 2750, 3000] # Cell 3 is the weak cell
    cols = [FIELD, FIELD, POS, FIELD]

    # Стеля заряду і підлога розряду
    f.append(line(100, y_soc(100), 730, y_soc(100), color=POS, sw=1.5, dash="5,4"))
    f.append(text(740, y_soc(100) + 4, "Стеля 4.2 В (BMS OVLO)", size=10, bold=True, color=POS, anchor="start"))

    f.append(line(100, y_soc(0), 730, y_soc(0), color=NEG, sw=1.5, dash="5,4"))
    f.append(text(740, y_soc(0) + 4, "Підлога 2.8 В (BMS UVLO)", size=10, bold=True, color=NEG, anchor="start"))

    # Малюємо 4 комірки
    bw = 70
    for i, (cx, cap, col) in enumerate(zip(cx_list, caps, cols)):
        pct = (cap / 3000.0) * 100.0
        # Контур повної комірки
        f.append(rect(cx - bw / 2, y_soc(100), bw, y_soc(0) - y_soc(100), fill=GRYBG, stroke=MUTED, sw=1.2))
        # Заливка реальної ємності
        fill_col = REDBG if i == 2 else GRNBG
        f.append(rect(cx - bw / 2 + 2, y_soc(pct), bw - 4, y_soc(0) - y_soc(pct), fill=fill_col, stroke=col, sw=1.5))

        f.append(text(cx, y_soc(pct) - 10, "%d мА·год" % cap, size=11, bold=True, color=col))
        f.append(text(cx, y_soc(0) + 20, "S%d" % (i + 1), size=11.5, bold=True, color=INK))
        if i == 2:
            f.append(text(cx, y_soc(0) + 36, "Вузьке місце!", size=10, bold=True, color=POS))
        else:
            f.append(text(cx, y_soc(0) + 36, "Заблоковано 250", size=9.5, color=MUTED))

    # Стрілка блокування
    f.append(arrow(cx_list[2], y_soc(91.6) - 20, cx_list[2], y_soc(91.6) - 4, color=POS, sw=2))

    b, _, _ = textbox(W / 2, 400,
                      "Коли комірка S3 розряджається до 2.8 В, захист відсікає весь пакет: 250 мА·год у комірках S1, S2, S4 лишаються невикористаними",
                      size=11, fill=BLUBG, stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "series-capacity-bottleneck.svg"), W, H, *f)


# ── 4. AC IR (1 кГц) проти DC IR (імпульсний) ──────────────────────────────────
def fig_ac_vs_dc_impedance():
    W, H = 880, 440
    f = [text(W / 2, 28, "Порівняння методів вимірювання: AC IR (1 кГц) проти DC IR (імпульс)",
              size=16.5, bold=True)]

    # Панель зліва: AC IR 1 кГц
    p1_x, p1_y, p1_w, p1_h = 40, 65, 380, 290
    f.append(rect(p1_x, p1_y, p1_w, p1_h, fill=BG, stroke=MUTED, sw=1.4))
    f.append(text(p1_x + p1_w / 2, p1_y + 26, "AC IR (1 кГц, Міліомметр)", size=13, bold=True, color=NEG))

    # Синусоїда
    ax0, ax1 = p1_x + 30, p1_x + 350
    ayc = p1_y + 80
    f.append(line(ax0, ayc, ax1, ayc, color=MUTED, sw=1, dash="3,3"))
    sine_pts = []
    import math
    for step in range(60):
        t = step / 59.0
        x = ax0 + t * (ax1 - ax0)
        y = ayc - 26 * math.sin(t * 4 * math.pi)
        sine_pts.append((x, y))
    d_sine = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in sine_pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d_sine, NEG))
    f.append(text(p1_x + p1_w / 2, ayc + 40, "f = 1000 Гц (T = 1 мс), 4-точковий Кельвін", size=10, color=INK))

    # Опис AC
    f.append(text(p1_x + 20, p1_y + 150, "• Міряє суто омічний опір R_ohm", size=10.5, color=INK, anchor="start"))
    f.append(text(p1_x + 20, p1_y + 172, "• Не чіпає повільну хімічну поляризацію", size=10.5, color=INK, anchor="start"))
    f.append(text(p1_x + 20, p1_y + 194, "• Час тесту: 10–50 мс (ідеально для лінії)", size=10.5, color=INK, anchor="start"))
    f.append(text(p1_x + 20, p1_y + 216, "• Не розряджає й не гріє комірку", size=10.5, color=INK, anchor="start"))
    f.append(text(p1_x + 20, p1_y + 245, "Стандарт заводського сортування", size=11, bold=True, color=NEG, anchor="start"))

    # Панель справа: DC IR імпульсний
    p2_x = 460
    f.append(rect(p2_x, p1_y, p1_w, p1_h, fill=BG, stroke=MUTED, sw=1.4))
    f.append(text(p2_x + p1_w / 2, p1_y + 26, "DC IR (Струмовий імпульс під навантаженням)", size=13, bold=True, color=POS))

    # Крива відгуку напруги
    bx0, bx1 = p2_x + 30, p2_x + 350
    by_top = p1_y + 60
    by_bot = p1_y + 120
    # Напруга спокою -> миттєвий стрибок R_ohm -> похила поляризація -> відновлення
    f.append(line(bx0, by_top, bx0 + 50, by_top, color=POS, sw=2))
    f.append(line(bx0 + 50, by_top, bx0 + 50, by_top + 30, color=POS, sw=2)) # R_ohm step
    # Поляризація
    pts_dc = [(bx0 + 50, by_top + 30), (bx0 + 100, by_top + 45), (bx0 + 180, by_top + 55), (bx0 + 220, by_top + 58)]
    d_dc = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_dc)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d_dc, POS))
    # Відновлення
    f.append(line(bx0 + 220, by_top + 58, bx0 + 220, by_top + 28, color=POS, sw=2))
    f.append(line(bx0 + 220, by_top + 28, bx1, by_top + 2, color=POS, sw=2))

    f.append(text(bx0 + 55, by_top + 18, "ΔV_ohm", size=9.5, bold=True, color=INK, anchor="start"))
    f.append(text(bx0 + 130, by_top + 75, "ΔV_поляризації", size=9.5, bold=True, color=POS))

    # Опис DC
    f.append(text(p2_x + 20, p1_y + 150, "• R_dc = (V_1 − V_2) / (I_2 − I_1)", size=10.5, color=INK, anchor="start"))
    f.append(text(p2_x + 20, p1_y + 172, "• Включає R_ohm + R_ct (перенос) + R_sei", size=10.5, color=INK, anchor="start"))
    f.append(text(p2_x + 20, p1_y + 194, "• Показує реальну просадку під тягою", size=10.5, color=INK, anchor="start"))
    f.append(text(p2_x + 20, p1_y + 216, "• Триває від 1 до 10 секунд на комірку", size=10.5, color=INK, anchor="start"))
    f.append(text(p2_x + 20, p1_y + 245, "Критичний для дронів та електротяги", size=11, bold=True, color=POS, anchor="start"))

    b, _, _ = textbox(W / 2, 395,
                      "AC IR міряє стан контактів та електроліту без розряду; DC IR показує повний динамічний імпеданс під робочим струмом",
                      size=11, fill=GRNBG, stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "ac-vs-dc-impedance.svg"), W, H, *f)


# ── 5. Технологічний конвеєр добору та сортування ──────────────────────────────
def fig_sorting_pipeline():
    W, H = 900, 440
    f = [text(W / 2, 28, "Технологічний конвеєр вхідного контролю та добору комірок",
              size=16.5, bold=True)]

    # 5 послідовних кроків
    steps = [
        ("1. Вхідний огляд", "Штрихкод, партія,\nгеометрія, маса"),
        ("2. OCV та K-витік", "Тест 1 → Відстій 14d\n→ Тест 2: ΔV/Δt"),
        ("3. AC IR 1 кГц", "4-точковий Кельвін\n(R_ohm, мОм)"),
        ("4. Ємнісний цикл", "CC-CV заряд →\n0.5C розряд (А·год)"),
        ("5. Матчинг / Бінінг", "Розбиття на Bin-и\n+ Змійка в S/P")
    ]

    bx_w = 145
    bx_h = 95
    y_top = 80
    start_x = 40
    gap = 35

    for i, (title, desc) in enumerate(steps):
        x = start_x + i * (bx_w + gap)
        col = FIELD if i == 4 else (NEG if i == 1 or i == 2 else INK)
        bg_col = GRNBG if i == 4 else (BLUBG if i == 1 or i == 2 else GRYBG)

        f.append(rect(x, y_top, bx_w, bx_h, fill=bg_col, stroke=col, sw=1.8, rx=6))
        f.append(text(x + bx_w / 2, y_top + 24, title, size=11, bold=True, color=col))
        f.append(mtext(x + bx_w / 2, y_top + 50, desc, size=9.5, color=INK, lh=1.3))

        if i < len(steps) - 1:
            f.append(arrow(x + bx_w + 4, y_top + bx_h / 2, x + bx_w + gap - 4, y_top + bx_h / 2, color=INK, sw=2))

    # Виходи з кроку 2 (Відсів)
    f.append(arrow(start_x + 1 * (bx_w + gap) + bx_w / 2, y_top + bx_h,
                   start_x + 1 * (bx_w + gap) + bx_w / 2, y_top + bx_h + 45, color=POS, sw=1.8))
    f.append(rect(start_x + 1 * (bx_w + gap) - 10, y_top + bx_h + 45, bx_w + 20, 50, fill=REDBG, stroke=POS, sw=1.5))
    f.append(text(start_x + 1 * (bx_w + gap) + bx_w / 2, y_top + bx_h + 65, "ВІДСІВ (Scrap)", size=10.5, bold=True, color=POS))
    f.append(text(start_x + 1 * (bx_w + gap) + bx_w / 2, y_top + bx_h + 82, "K > 0.2 мВ/добу (КЗ сепаратора)", size=9, color=POS))

    # Результат кроку 5
    f.append(arrow(start_x + 4 * (bx_w + gap) + bx_w / 2, y_top + bx_h,
                   start_x + 4 * (bx_w + gap) + bx_w / 2, y_top + bx_h + 45, color=FIELD, sw=1.8))
    f.append(rect(start_x + 4 * (bx_w + gap) - 10, y_top + bx_h + 45, bx_w + 20, 50, fill=GRNBG, stroke=FIELD, sw=1.5))
    f.append(text(start_x + 4 * (bx_w + gap) + bx_w / 2, y_top + bx_h + 65, "ГОТОВИЙ ПАКЕТ", size=10.5, bold=True, color=FIELD))
    f.append(text(start_x + 4 * (bx_w + gap) + bx_w / 2, y_top + bx_h + 82, "ΔQ_групи < 0.2%, ΔR < 1%", size=9, color=FIELD))

    b, _, _ = textbox(W / 2, 400,
                      "Повний конвеєр фільтрує дефекти сепаратора на етапі OCV і вирівнює робочі параметри перед зварюванням нікелевою стрічкою",
                      size=11, fill=GRNBG, stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "sorting-pipeline.svg"), W, H, *f)


# ── 6. Алгоритм змійки (Serpentine / Snake Bin-Packing) ────────────────────────
def fig_snake_grouping():
    W, H = 880, 460
    f = [text(W / 2, 28, "Алгоритм змійки (Serpentine Binning) для збірки 4S4P",
              size=16.5, bold=True)]

    # 4 групи S1, S2, S3, S4
    groups = ["Група S1", "Група S2", "Група S3", "Група S4"]
    gx0 = 90
    gw = 160
    gap = 25
    gy = 75
    gh = 255

    for j, gname in enumerate(groups):
        x = gx0 + j * (gw + gap)
        f.append(rect(x, gy, gw, gh, fill=GRYBG, stroke=INK, sw=1.5, rx=6))
        f.append(text(x + gw / 2, gy + 24, gname, size=12, bold=True, color=INK))

    # 4 проходи по 4 комірки (ранжовані 1..16 від найбільшої до найменшої)
    cells_order = [
        (0, 0, "#1", "3080", 1), (1, 0, "#2", "3070", 1), (2, 0, "#3", "3060", 1), (3, 0, "#4", "3050", 1),
        (3, 1, "#5", "3040", 2), (2, 1, "#6", "3030", 2), (1, 1, "#7", "3020", 2), (0, 1, "#8", "3010", 2),
        (0, 2, "#9", "3000", 3), (1, 2, "#10", "2990", 3), (2, 2, "#11", "2980", 3), (3, 2, "#12", "2970", 3),
        (3, 3, "#13", "2960", 4), (2, 3, "#14", "2950", 4), (1, 3, "#15", "2940", 4), (0, 3, "#16", "2930", 4),
    ]

    row_y = [gy + 42, gy + 92, gy + 142, gy + 192]
    cw = 140
    ch = 38

    for g_idx, r_idx, rank, cap, pass_n in cells_order:
        x = gx0 + g_idx * (gw + gap) + (gw - cw) / 2
        y = row_y[r_idx]
        col = FIELD if pass_n in (1, 3) else NEG
        bg_c = GRNBG if pass_n in (1, 3) else BLUBG
        f.append(rect(x, y, cw, ch, fill=bg_c, stroke=col, sw=1.3, rx=4))
        f.append(text(x + 28, y + 24, rank, size=11, bold=True, color=col))
        f.append(text(x + cw - 38, y + 24, cap + " мАг", size=10, color=INK))

    # Стрілки змійки
    f.append(arrow(gx0 + 20, row_y[0] + ch / 2, gx0 + 4 * (gw + gap) - 15, row_y[0] + ch / 2, color=FIELD, sw=1.8))
    f.append(arrow(gx0 + 4 * (gw + gap) - 15, row_y[0] + ch / 2, gx0 + 4 * (gw + gap) - 15, row_y[1] + ch / 2, color=MUTED, sw=1.4))
    f.append(arrow(gx0 + 4 * (gw + gap) - 15, row_y[1] + ch / 2, gx0 + 20, row_y[1] + ch / 2, color=NEG, sw=1.8))
    f.append(arrow(gx0 + 20, row_y[1] + ch / 2, gx0 + 20, row_y[2] + ch / 2, color=MUTED, sw=1.4))
    f.append(arrow(gx0 + 20, row_y[2] + ch / 2, gx0 + 4 * (gw + gap) - 15, row_y[2] + ch / 2, color=FIELD, sw=1.8))
    f.append(arrow(gx0 + 4 * (gw + gap) - 15, row_y[2] + ch / 2, gx0 + 4 * (gw + gap) - 15, row_y[3] + ch / 2, color=MUTED, sw=1.4))
    f.append(arrow(gx0 + 4 * (gw + gap) - 15, row_y[3] + ch / 2, gx0 + 20, row_y[3] + ch / 2, color=NEG, sw=1.8))

    # Підсумок по кожній групі
    for j in range(4):
        x = gx0 + j * (gw + gap)
        f.append(text(x + gw / 2, gy + gh - 14, "Σ = 12 020 мА·год", size=11, bold=True, color=FIELD))

    b, _, _ = textbox(W / 2, 410,
                      "Зигзагоподібний розподіл автоматично компенсує сильні комірки слабкими: різниця між групами становить 0 мА·год (ідеальний баланс)",
                      size=11, fill=GRNBG, stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "snake-grouping.svg"), W, H, *f)


if __name__ == "__main__":
    fig_variance_distribution()
    fig_parallel_current_split()
    fig_series_capacity_bottleneck()
    fig_ac_vs_dc_impedance()
    fig_sorting_pipeline()
    fig_snake_grouping()
    print("OK: 6 figures ->", IMG)
