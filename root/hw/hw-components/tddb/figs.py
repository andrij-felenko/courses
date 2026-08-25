# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Статистична модель перколяції: накопичення пасток у діелектрику ───────
def fig_percolation_lattice():
    """Три етапи накопичення дефектів у ґратці діелектрика:
    свіжий оксид -> накопичення пасток (SILC) -> перколяційний провідний ланцюжок (пробій)."""
    W, H = 820, 420
    frags = []

    # Заголовок зверху
    frags.append(text(W / 2, 28, "Статистична модель перколяції у підзатворному діелектрику",
                      size=16, color=INK, bold=True))

    panels = [
        (40, 60, 220, 310, "1. Свіжий діелектрик", [
            "Ідеальна атомна ґратка",
            "Дефектів немає",
            "Тільки пряме тунелювання",
            "Витік мінімальний"
        ], "#eafaf0", FIELD),
        (300, 60, 220, 310, "2. Генерація пасток (SILC)", [
            "Електрони вибивають зв'язки",
            "Накопичення пасток Nt",
            "Trap-Assisted Tunneling",
            "Струм витоку зростає"
        ], "#fef9e7", "#d4ac0d"),
        (560, 60, 220, 310, "3. Перколяційний ланцюг", [
            "Густина дефектів Nt ≥ Ncrit",
            "Неперервний ланцюг пасток",
            "Локальний пробій діелектрика",
            "Стрибок струму та нагрів"
        ], "#fdecea", POS)
    ]

    for (px, py, pw, ph, title_text, bullets, bg_col, border_col) in panels:
        # Фон панелі
        frags.append(rect(px, py, pw, ph, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        frags.append(text(px + pw / 2, py + 24, title_text, size=13.5, color=border_col, bold=True))

        # Затвор зверху
        gx, gy, gw, gh = px + 15, py + 45, pw - 30, 26
        frags.append(rect(gx, gy, gw, gh, fill="#d5dbdb", stroke=LINE, sw=1.2, rx=3))
        frags.append(text(gx + gw / 2, gy + 17, "Металевий затвор (Gate)", size=11, color=INK, bold=True))

        # Шар діелектрика
        ox, oy, ow, oh = px + 15, py + 75, pw - 30, 120
        frags.append(rect(ox, oy, ow, oh, fill="#ffffff", stroke=LINE, sw=1.2, rx=2))

        # Кремнієва підкладка (канал) знизу
        sx, sy, sw, sh = px + 15, py + 198, pw - 30, 26
        frags.append(rect(sx, sy, sw, sh, fill="#ebedef", stroke=LINE, sw=1.2, rx=3))
        frags.append(text(sx + sw / 2, sy + 17, "Кремнієвий канал (Si Substrate)", size=11, color=INK, bold=True))

        # Внутрішні елементи діелектрика залежно від панелі
        if "1. Свіжий" in title_text:
            # Рівномірні лінії поля
            for lx in range(int(ox + 20), int(ox + ow - 10), 30):
                frags.append(line(lx, oy + 8, lx, oy + oh - 28, color="#aeb6bf", sw=1.0, dash="3,3"))
            frags.append(text(ox + ow / 2, oy + oh - 12, "Чистий SiO2 / High-k", size=11, color=MUTED, bold=True))

        elif "2. Генерація" in title_text:
            # Розсіяні пастки (жовтогарячі кола)
            traps = [(ox + 35, oy + 25), (ox + 85, oy + 40), (ox + 140, oy + 30),
                     (ox + 50, oy + 80), (ox + 120, oy + 95), (ox + 160, oy + 65)]
            for tx, ty in traps:
                frags.append(circle(tx, ty, 5.5, fill="#f39c12", stroke="#9a7d0a", sw=1.5))
            frags.append(text(ox + ow / 2, oy + oh - 12, "Ізольовані пастки Nt", size=11, color="#7d6608", bold=True))

        elif "3. Перколяційний" in title_text:
            # Ланцюжок пасток від затвора до підкладки
            chain = [(ox + 95, oy + 18), (ox + 88, oy + 42), (ox + 102, oy + 66),
                     (ox + 92, oy + 90), (ox + 98, oy + 108)]
            # Інші фонові пастки
            other_traps = [(ox + 30, oy + 35), (ox + 45, oy + 85), (ox + 155, oy + 45), (ox + 145, oy + 90)]
            for tx, ty in other_traps:
                frags.append(circle(tx, ty, 5, fill="#f5b7b1", stroke=POS, sw=1.0))

            # З'єднувальний провідний шлях
            for i in range(len(chain) - 1):
                frags.append(line(chain[i][0], chain[i][1], chain[i+1][0], chain[i+1][1], color=POS, sw=2.5))
            for tx, ty in chain:
                frags.append(circle(tx, ty, 7, fill=POS, stroke="#ffffff", sw=1.5))

            # Стрілка струму крізь пробійний місток
            frags.append(arrow(ox + 95, gy + gh - 2, ox + 95, oy + 8, color=POS, sw=2.2))
            frags.append(arrow(ox + 98, oy + oh - 8, ox + 98, sy + 4, color=POS, sw=2.2))
            frags.append(text(ox + ow / 2 + 35, oy + oh / 2 + 4, "Місток!", size=12, color=POS, bold=True))

        # Текстові пояснення внизу панелі
        ty = py + 240
        for b in bullets:
            frags.append(text(px + 14, ty, "• " + b, size=11, color=INK, anchor="start"))
            ty += 16

    frags.append(text(W / 2, H - 12,
                      "Випадкове блукання й накопичення пасток утворює статистичний місток пробою при досягненні Ncrit",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "percolation-lattice.svg"), W, H, *frags,
           title="Статистична модель перколяції у діелектрику")


# ── 2. Стадії деградації діелектрика: від SILC до жорсткого пробою ───────────
def fig_breakdown_stages():
    """Графік еволюції струму витоку затвора в часі:
    Свіжий витік -> Повільне зростання SILC -> М'який пробій (SBD з RTN шумом) -> Жорсткий пробій (HBD)."""
    W, H = 800, 400
    frags = []

    frags.append(text(W / 2, 26, "Еволюція струму витоку затвора під час електричного стресу",
                      size=16, color=INK, bold=True))

    # Вісь X та Y
    ox, oy = 90, 320
    gw, gh = 660, 260
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2.0))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2.0))

    # Стрілки осей
    frags.append(arrow(ox + gw - 10, oy, ox + gw + 10, oy, color=LINE, sw=2.0))
    frags.append(arrow(ox, oy - gh + 10, ox, oy - gh - 10, color=LINE, sw=2.0))

    # Підписи осей
    frags.append(text(ox + gw, oy + 28, "Час під напругою (t)", size=13, color=INK, anchor="end", bold=True))
    frags.append(text(ox - 15, oy - gh, "Струм затвора Ig (лог. шкала)", size=13, color=INK, anchor="end", bold=True))

    # Стрілка шкали струму
    frags.append(text(ox - 10, oy - 15, "10⁻¹² A", size=11, color=MUTED, anchor="end"))
    frags.append(text(ox - 10, oy - 90, "10⁻⁹ A", size=11, color=MUTED, anchor="end"))
    frags.append(text(ox - 10, oy - 170, "10⁻⁶ A", size=11, color=MUTED, anchor="end"))
    frags.append(text(ox - 10, oy - 245, "10⁻² A", size=11, color=MUTED, anchor="end"))

    # Області графіка з фоновими прямокутниками
    frags.append(rect(ox + 5, oy - gh + 10, 175, gh - 15, fill="#f4f6f8", stroke="none"))
    frags.append(rect(ox + 180, oy - gh + 10, 160, gh - 15, fill="#fef9e7", stroke="none"))
    frags.append(rect(ox + 340, oy - gh + 10, 180, gh - 15, fill="#ebf5fb", stroke="none"))
    frags.append(rect(ox + 520, oy - gh + 10, 140, gh - 15, fill="#fdecea", stroke="none"))

    # Межові лінії фаз
    frags.append(line(ox + 180, oy, ox + 180, oy - gh + 10, color="#bdc3c7", sw=1.2, dash="4,4"))
    frags.append(line(ox + 340, oy, ox + 340, oy - gh + 10, color="#bdc3c7", sw=1.2, dash="4,4"))
    frags.append(line(ox + 520, oy, ox + 520, oy - gh + 10, color="#bdc3c7", sw=1.2, dash="4,4"))

    # Назви зон
    frags.append(text(ox + 90, oy - gh + 26, "1. Свіжий оксид", size=12, color=INK, bold=True))
    frags.append(text(ox + 260, oy - gh + 26, "2. Режим SILC", size=12, color="#7d6608", bold=True))
    frags.append(text(ox + 430, oy - gh + 26, "3. М'який пробій (SBD)", size=12, color=NEG, bold=True))
    frags.append(text(ox + 590, oy - gh + 26, "4. Жорсткий пробій (HBD)", size=12, color=POS, bold=True))

    # Малювання кривої струму
    # Фаза 1: Свіжий струм
    frags.append(line(ox + 5, oy - 20, ox + 180, oy - 25, color=FIELD, sw=2.4))
    frags.append(text(ox + 90, oy - 40, "Пряме тунелювання", size=10.5, color=FIELD, italic=True))

    # Фаза 2: SILC повільний підйом
    frags.append(line(ox + 180, oy - 25, ox + 340, oy - 55, color="#d4ac0d", sw=2.4))
    frags.append(text(ox + 260, oy - 70, "Trap-Assisted\nTunneling", size=10.5, color="#7d6608", italic=True))

    # Фаза 3: SBD - різкий стрибок і RTN флуктуації
    frags.append(line(ox + 340, oy - 55, ox + 345, oy - 145, color=NEG, sw=2.4))
    rtn_pts = [
        (ox + 345, oy - 145), (ox + 365, oy - 155), (ox + 380, oy - 140),
        (ox + 400, oy - 160), (ox + 420, oy - 145), (ox + 445, oy - 158),
        (ox + 470, oy - 148), (ox + 495, oy - 165), (ox + 520, oy - 155)
    ]
    for i in range(len(rtn_pts) - 1):
        frags.append(line(rtn_pts[i][0], rtn_pts[i][1], rtn_pts[i+1][0], rtn_pts[i+1][1], color=NEG, sw=2.2))
    frags.append(text(ox + 430, oy - 180, "RTN шум (флуктуації пасток)\nR ≈ 10⁵…10⁷ Ом", size=10.5, color=NEG, bold=True))

    # Фаза 4: HBD - незворотний тепловий пробій
    frags.append(line(ox + 520, oy - 155, ox + 530, oy - 245, color=POS, sw=3.0))
    frags.append(line(ox + 530, oy - 245, ox + 655, oy - 250, color=POS, sw=3.0))
    frags.append(text(ox + 590, oy - 215, "Термічне руйнування\nR < 100 Ом (КЗ)", size=11, color=POS, bold=True))

    frags.append(text(W / 2, H - 10,
                      "SBD створює мікропровідність і шум витоку; тепловий розгін у містку завершується катастрофічним HBD",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "breakdown-stages.svg"), W, H, *frags,
           title="Стадії деградації підзатворного діелектрика")


# ── 3. Моделі екстраполяції ресурсу діелектрика ──────────────────────────────
def fig_acceleration_models():
    """Порівняння E-моделі, 1/E-моделі та Power-Law (V^-n) моделі на графіку час-напруга."""
    W, H = 800, 420
    frags = []

    frags.append(text(W / 2, 26, "Екстраполяція терміну служби: порівняння фізичних моделей",
                      size=16, color=INK, bold=True))

    ox, oy = 90, 340
    gw, gh = 660, 275
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2.0))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2.0))
    frags.append(arrow(ox + gw - 10, oy, ox + gw + 10, oy, color=LINE, sw=2.0))
    frags.append(arrow(ox, oy - gh + 10, ox, oy - gh - 10, color=LINE, sw=2.0))

    frags.append(text(ox + gw, oy + 28, "Напруга на затворі Vg (В)", size=13, color=INK, anchor="end", bold=True))
    frags.append(text(ox - 15, oy - gh, "Час до пробою ln(tbd)", size=13, color=INK, anchor="end", bold=True))

    # Зона випробувань (прискорені тести) праворуч
    test_x, test_w = ox + 430, 210
    frags.append(rect(test_x, oy - 140, test_w, 130, fill="#fef9e7", stroke="#f1c40f", sw=1.5, rx=5))
    frags.append(text(test_x + test_w / 2, oy - 118, "Зона прискорених випробувань", size=11.5, color="#7d6608", bold=True))
    frags.append(text(test_x + test_w / 2, oy - 98, "Висока напруга (2.0…3.5 В)", size=11, color="#7d6608"))
    frags.append(text(test_x + test_w / 2, oy - 80, "Час tbd: від секунд до годин", size=11, color="#7d6608"))

    # Точки експериментальних даних у тестовій зоні
    exp_pts = [(test_x + 30, oy - 40), (test_x + 60, oy - 52), (test_x + 95, oy - 62),
               (test_x + 135, oy - 76), (test_x + 175, oy - 92)]
    for px, py in exp_pts:
        frags.append(circle(px, py, 4.5, fill=POS, stroke="#922b21", sw=1.2))

    # Зона робочої напруги ліворуч
    op_x, op_w = ox + 40, 160
    frags.append(rect(op_x, oy - gh + 35, op_w, gh - 45, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(op_x + op_w / 2, oy - gh + 55, "Робоча зона (Vop ≈ 0.8 В)", size=11.5, color=FIELD, bold=True))

    # Горизонтальна лінія критерію 10 років
    frags.append(line(ox, oy - 200, ox + gw, oy - 200, color="#7f8c8d", sw=1.5, dash="5,5"))
    frags.append(text(ox + 15, oy - 206, "Ціль: 10 років надійної роботи", size=11.5, color=INK, anchor="start", bold=True))

    # Модель 1: 1/E model (Anode Hole Injection) - синя верхня крива
    frags.append(line(test_x + 175, oy - 92, test_x + 30, oy - 40, color=NEG, sw=2.2))
    frags.append(line(test_x + 30, oy - 40, op_x + op_w / 2, oy - 265, color=NEG, sw=2.2, dash="4,3"))
    frags.append(text(op_x + op_w / 2 + 10, oy - 270, "1/E-модель (Оптимістична)", size=11, color=NEG, bold=True, anchor="start"))

    # Модель 2: Power-law V^-n model - зелена середня крива
    frags.append(line(test_x + 175, oy - 92, op_x + op_w / 2, oy - 215, color=FIELD, sw=2.6, dash="5,3"))
    frags.append(text(op_x + op_w / 2 + 10, oy - 215, "V⁻ⁿ-модель (Реалістична, надтонкі оксиди)", size=11, color=FIELD, bold=True, anchor="start"))

    # Модель 3: E-model (Thermochemical) - червона нижня пряма
    frags.append(line(test_x + 175, oy - 92, op_x + op_w / 2, oy - 150, color=POS, sw=2.2, dash="4,3"))
    frags.append(text(op_x + op_w / 2 + 10, oy - 145, "E-модель (Консервативна)", size=11, color=POS, bold=True, anchor="start"))

    frags.append(text(W / 2, H - 10,
                      "Розбіжність моделей при екстраполяції від 3 В до 0.8 В сягає кількох порядків часу",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "acceleration-models.svg"), W, H, *frags,
           title="Моделі екстраполяції прискорених випробувань TDDB")


# ── 4. Розподіл Вейбула та масштабування площі ───────────────────────────────
def fig_weibull_area_scaling():
    """Графік Вейбула ln(-ln(1-F)) vs ln(t) і зсув надійності при масштабуванні площі транзистора на чіп."""
    W, H = 800, 420
    frags = []

    frags.append(text(W / 2, 26, "Розподіл Вейбула та ефект масштабування площі діелектрика",
                      size=16, color=INK, bold=True))

    ox, oy = 110, 330
    gw, gh = 640, 260
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2.0))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2.0))
    frags.append(arrow(ox + gw - 10, oy, ox + gw + 10, oy, color=LINE, sw=2.0))
    frags.append(arrow(ox, oy - gh + 10, ox, oy - gh - 10, color=LINE, sw=2.0))

    frags.append(text(ox + gw, oy + 28, "Час до відмови ln(t)", size=13, color=INK, anchor="end", bold=True))
    frags.append(text(ox - 15, oy - gh, "W = ln(−ln(1 − F))", size=13, color=INK, anchor="end", bold=True))

    # Горизонтальні позначки кумулятивної частки відмов F
    f_marks = [
        (oy - 50, "F = 0.01% (100 ppm)", "-9.2"),
        (oy - 120, "F = 1%", "-4.6"),
        (oy - 190, "F = 63.2% (W = 0, η)", "0.0"),
        (oy - 240, "F = 90%", "+0.8")
    ]
    for ypos, flabel, wlabel in f_marks:
        frags.append(line(ox, ypos, ox + gw, ypos, color="#e5e7e9", sw=1.0, dash="3,3"))
        frags.append(text(ox - 10, ypos + 4, flabel, size=10.5, color=MUTED, anchor="end"))

    # Лінія 1: Одиночний тестовий транзистор (Area A0 = 0.01 мкм²)
    # Пряма з нахилом beta
    x1_start, y1_start = ox + 380, oy - 40
    x1_end, y1_end = ox + 580, oy - 240
    frags.append(line(x1_start, y1_start, x1_end, y1_end, color=FIELD, sw=2.6))
    frags.append(text(x1_end - 20, y1_end - 10, "Одиночний транзистор (A₀)", size=12, color=FIELD, bold=True))

    # Точки тестових транзисторів
    for px, py in [(ox + 400, oy - 60), (ox + 440, oy - 100), (ox + 480, oy - 140),
                   (ox + 520, oy - 180), (ox + 560, oy - 220)]:
        frags.append(circle(px, py, 4, fill=FIELD, stroke="#145a32", sw=1.2))

    # Лінія 2: Весь кристал (Area Achip = 10 мм² = 10⁹ · A0)
    # Зсув ліворуч на Δln(t) = (1/β) · ln(Achip / A0)
    shift = 180
    x2_start, y2_start = x1_start - shift, y1_start
    x2_end, y2_end = x1_end - shift, y1_end
    frags.append(line(x2_start, y2_start, x2_end, y2_end, color=POS, sw=2.6))
    frags.append(text(x2_end - 30, y2_end - 10, "Весь чіп (Achip = 10⁹ · A₀)", size=12, color=POS, bold=True))

    # Стрілка зсуву площі
    frags.append(arrow(ox + 480, oy - 140, ox + 300, oy - 140, color=LINE, sw=2.0))
    b_box, _, _ = textbox(ox + 390, oy - 165, "Зсув площі:\nΔln(t) = (1/β) · ln(Achip / A₀)",
                          size=11, pad=6, fill="#fdfefe", stroke=LINE, sw=1.2)
    frags.append(b_box)

    # Пояснення про нахил бета
    slope_box, _, _ = textbox(ox + 520, oy - 80, "Нахил прямої = β\n(β ≈ tox / a₀, менший для тонких оксидів)",
                              size=11, pad=8, fill="#eafaf0", stroke=FIELD, sw=1.2)
    frags.append(slope_box)

    frags.append(text(W / 2, H - 10,
                      "Правило слабкої ланки: більша сумарна площа затворів чіпа різко зменшує час до першого пробою",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "weibull-area-scaling.svg"), W, H, *frags,
           title="Розподіл Вейбула та масштабування площі")


if __name__ == "__main__":
    fig_percolation_lattice()
    fig_breakdown_stages()
    fig_acceleration_models()
    fig_weibull_area_scaling()
    print("ok: figures written to", IMG)
