# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_energy_absorption_zones():
    W, H = 840, 370
    p = []

    # Title / Header
    p.append(text(W / 2, 28, "Ієрархія зон поглинання енергії удару", size=16, bold=True))

    stages = [
        ("1. Зовнішній контакт", "Пропелер і бампер", "Зминання гнучкого PC/TPU,\nрозсіювання кінетики в тепло", "#eaf2f8", "#2980b9"),
        ("2. Жертовний контур", "Зрізні гвинти променів", "Зріз нейлону PA66 (F > 220 Н),\nвідхилення променя без згину", "#fef9e7", "#d4ac0d"),
        ("3. Силовий каркас", "Карбонові деки і стійки", "Розподіл сил стиснення,\nклітка безпеки навколо плат", "#ebf5fb", "#2e86c1"),
        ("4. Захищене ядро", "Демпфери і стек FC/ESC", "Силіконові бушинги (гасіння хвиль),\nзахист пайки BGA та сенсорів", "#eafaf1", FIELD),
    ]

    card_w = 180
    card_h = 240
    gap = 24
    start_x = (W - (4 * card_w + 3 * gap)) / 2
    y0 = 55

    for i, (num, title_txt, desc_txt, fill_col, border_col) in enumerate(stages):
        x = start_x + i * (card_w + gap)
        # Card container
        p.append(rect(x, y0, card_w, card_h, fill=fill_col, stroke=border_col, sw=1.8, rx=8))

        # Stage number badge
        p.append(rect(x + 10, y0 + 12, card_w - 20, 26, fill=border_col, stroke=border_col, rx=4))
        p.append(text(x + card_w / 2, y0 + 29, num, size=11, color="#ffffff", bold=True))

        # Component Title
        p.append(text(x + card_w / 2, y0 + 64, title_txt, size=12, color=INK, bold=True))

        # Divider line inside card
        p.append(line(x + 15, y0 + 78, x + card_w - 15, y0 + 78, color=MUTED, sw=0.8, dash="2,2"))

        # Description text
        lines = desc_txt.split("\n")
        p.append(mtext(x + card_w / 2, y0 + 105, lines, size=11, color=INK, lh=1.4))

        # Energy dissipation tag at bottom
        p.append(rect(x + 12, y0 + card_h - 44, card_w - 24, 30, fill="#ffffff", stroke=border_col, sw=1, rx=4))
        e_labels = ["~10–25% енергії", "~40–60% енергії", "~20–30% пружно", "< 5% залишку"]
        p.append(text(x + card_w / 2, y0 + card_h - 25, e_labels[i], size=10, color=border_col, bold=True))

        # Arrow to next stage
        if i < 3:
            ax1 = x + card_w + 4
            ax2 = x + card_w + gap - 4
            ay = y0 + card_h / 2
            p.append(arrow(ax1, ay, ax2, ay, color=MUTED, sw=2))

    # Bottom summary legend
    p.append(rect(start_x, y0 + card_h + 16, W - 2 * start_x, 32, fill=FILL, stroke=LINE, sw=1, rx=4))
    p.append(text(W / 2, y0 + card_h + 36, "Напрямок передачі навантаження: від дешевих змінних деталей до критичної електроніки →", size=11, color=INK, italic=True))

    render(os.path.join(OUT, "energy-absorption-zones.svg"), W, H, *p)


def fig_shear_screw_mechanism():
    W, H = 840, 370
    p = []

    p.append(text(W / 2, 26, "Механізм дії жертовного зрізного гвинта променя", size=16, bold=True))

    panel_w = 380
    panel_h = 295
    y0 = 48

    # Panel 1: Робочий стан
    x1 = 25
    p.append(rect(x1, y0, panel_w, panel_h, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(x1 + panel_w / 2, y0 + 24, "А. Робоча фіксація променя", size=13, color=INK, bold=True))

    # Plates outline
    p.append(rect(x1 + 25, y0 + 60, 150, 14, fill="#2c3e50", stroke=LINE, rx=2))
    p.append(text(x1 + 100, y0 + 52, "Верхня дека (карбон)", size=10, color=MUTED))
    p.append(rect(x1 + 25, y0 + 130, 150, 14, fill="#2c3e50", stroke=LINE, rx=2))
    p.append(text(x1 + 100, y0 + 162, "Нижня дека (карбон)", size=10, color=MUTED))

    # Carbon Arm
    p.append(rect(x1 + 35, y0 + 78, 290, 48, fill="#34495e", stroke=LINE, rx=3))
    p.append(text(x1 + 240, y0 + 107, "Промінь (карбон 5 мм)", size=11, color="#ffffff", bold=True))

    # Pivot bolt indicator lines
    p.append(line(x1 + 55, y0 + 52, x1 + 55, y0 + 152, color="#7f8c8d", sw=6))
    p.append(circle(x1 + 55, y0 + 102, 5, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(x1 + 55, y0 + 185, "Сталевий болт 12.9", size=10, color=INK, bold=True))
    p.append(text(x1 + 55, y0 + 200, "(осьовий шарнір)", size=9, color=MUTED))

    # Sacrificial bolt indicator lines
    p.append(line(x1 + 145, y0 + 52, x1 + 145, y0 + 152, color="#f39c12", sw=6))
    p.append(circle(x1 + 145, y0 + 102, 5, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(x1 + 145, y0 + 185, "Нейлоновий гвинт PA66", size=10, color=POS, bold=True))
    p.append(text(x1 + 145, y0 + 200, "(зріз при F > 220 Н)", size=9, color=MUTED))

    p.append(rect(x1 + 20, y0 + 235, panel_w - 40, 36, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    p.append(text(x1 + panel_w / 2, y0 + 257, "Обидва гвинти утримують жорстку геометрію в польоті", size=10, color=MUTED))

    # Panel 2: Стан удару та зрізу
    x2 = 435
    p.append(rect(x2, y0, panel_w, panel_h, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    p.append(text(x2 + panel_w / 2, y0 + 24, "Б. Зіткнення з перешкодою (Удар F)", size=13, color=INK, bold=True))

    # Plates outline
    p.append(rect(x2 + 25, y0 + 60, 150, 14, fill="#2c3e50", stroke=LINE, rx=2))
    p.append(rect(x2 + 25, y0 + 130, 150, 14, fill="#2c3e50", stroke=LINE, rx=2))

    # Arm rotated around pivot bolt
    p.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="#34495e" stroke="%s" stroke-width="1.5"/>' %
             (x2 + 45, y0 + 78, x2 + 305, y0 + 135, x2 + 295, y0 + 183, x2 + 35, y0 + 126, LINE))
    p.append(text(x2 + 215, y0 + 165, "Промінь провернувся", size=11, color="#ffffff", bold=True))

    # Pivot bolt intact
    p.append(line(x2 + 55, y0 + 52, x2 + 55, y0 + 152, color="#7f8c8d", sw=6))
    p.append(circle(x2 + 55, y0 + 102, 5, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(x2 + 55, y0 + 185, "Шарнір цілий", size=10, color=FIELD, bold=True))
    p.append(text(x2 + 55, y0 + 200, "(вісь обертання)", size=9, color=MUTED))

    # Sheared nylon bolt
    p.append(line(x2 + 145, y0 + 52, x2 + 145, y0 + 74, color="#f39c12", sw=6))
    p.append(line(x2 + 145, y0 + 130, x2 + 145, y0 + 152, color="#f39c12", sw=6))
    p.append(text(x2 + 145, y0 + 106, "✕ ЗРІЗ", size=11, color=POS, bold=True))
    p.append(text(x2 + 145, y0 + 185, "Гвинт зрізано", size=10, color=FIELD, bold=True))
    p.append(text(x2 + 145, y0 + 200, "деки неушкоджені", size=9, color=MUTED))

    # Impact force arrow
    p.append(arrow(x2 + 345, y0 + 85, x2 + 295, y0 + 130, color=POS, sw=3))
    p.append(text(x2 + 335, y0 + 72, "Сила удару F", size=11, color=POS, bold=True))

    p.append(rect(x2 + 20, y0 + 235, panel_w - 40, 36, fill="#eafaf1", stroke=FIELD, sw=1, rx=4))
    p.append(text(x2 + panel_w / 2, y0 + 257, "Ремонт: заміна нейлонового гвинта за 30 секунд", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "shear-screw-mechanism.svg"), W, H, *p)


def fig_stack_and_strain_relief():
    W, H = 840, 380
    p = []

    p.append(text(W / 2, 26, "Захист стека та компенсатор ривка силового кабелю", size=16, bold=True))

    w_card = 385
    h_card = 300
    y0 = 48

    # Bad variant:
    x1 = 20
    p.append(rect(x1, y0, w_card, h_card, fill="#fdf2e9", stroke=POS, sw=1.5, rx=8))
    p.append(text(x1 + w_card / 2, y0 + 24, "✕ Без розвантаження (пряма пайка)", size=13, color=POS, bold=True))

    # Carbon frame bottom plate
    p.append(rect(x1 + 20, y0 + 200, 345, 12, fill="#2c3e50", stroke=LINE, rx=2))
    p.append(text(x1 + 190, y0 + 228, "Нижня дека рами (карбон)", size=10, color=MUTED))

    # ESC PCB
    p.append(rect(x1 + 35, y0 + 135, 120, 26, fill="#1e8449", stroke=LINE, rx=2))
    p.append(text(x1 + 95, y0 + 152, "Плата 4-in-1 ESC", size=10, color="#ffffff", bold=True))

    # Standoffs for PCB
    p.append(rect(x1 + 40, y0 + 161, 8, 39, fill="#7f8c8d", stroke=LINE, rx=1))
    p.append(rect(x1 + 140, y0 + 161, 8, 39, fill="#7f8c8d", stroke=LINE, rx=1))

    # Direct cable pulled tight
    p.append(line(x1 + 155, y0 + 148, x1 + 325, y0 + 82, color=POS, sw=4))
    p.append(text(x1 + 245, y0 + 105, "Кабель 12 AWG", size=10, color=POS, bold=True))

    # Torn pad detail
    p.append(circle(x1 + 155, y0 + 148, 10, fill="#fadbdb", stroke=POS, sw=1.8))
    p.append(text(x1 + 155, y0 + 132, "Відрив пайки!", size=9, color=POS, bold=True))

    # Battery flying off
    p.append(rect(x1 + 275, y0 + 42, 85, 40, fill="#34495e", stroke=LINE, rx=4))
    p.append(text(x1 + 317, y0 + 66, "LiPo Батарея", size=10, color="#ffffff", bold=True))
    p.append(arrow(x1 + 320, y0 + 36, x1 + 355, y0 + 22, color=POS, sw=2))

    p.append(rect(x1 + 15, y0 + 242, w_card - 30, 44, fill="#ffffff", stroke=POS, sw=1, rx=4))
    p.append(text(x1 + w_card / 2, y0 + 260, "Інерція батареї вириває контактні площадки", size=10, color=POS, bold=True))
    p.append(text(x1 + w_card / 2, y0 + 276, "з текстоліту — плата ESC безповоротно знищена", size=9, color=INK))

    # Good variant:
    x2 = 435
    p.append(rect(x2, y0, w_card, h_card, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(x2 + w_card / 2, y0 + 24, "✓ З компенсатором ривка (Strain Relief)", size=13, color=FIELD, bold=True))

    # Carbon frame bottom plate
    p.append(rect(x2 + 20, y0 + 200, 345, 12, fill="#2c3e50", stroke=LINE, rx=2))
    p.append(text(x2 + 190, y0 + 228, "Нижня дека рами (карбон)", size=10, color=MUTED))

    # ESC PCB
    p.append(rect(x2 + 35, y0 + 135, 120, 26, fill="#1e8449", stroke=LINE, rx=2))
    p.append(text(x2 + 95, y0 + 152, "Плата 4-in-1 ESC", size=10, color="#ffffff", bold=True))

    # Silicone dampers
    p.append(rect(x2 + 40, y0 + 161, 8, 39, fill="#3498db", stroke=LINE, rx=2))
    p.append(rect(x2 + 140, y0 + 161, 8, 39, fill="#3498db", stroke=LINE, rx=2))
    p.append(text(x2 + 95, y0 + 185, "Силіконові демпфери", size=9, color="#2980b9"))

    # S-loop slack cable
    p.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="4"/>' %
             (x2 + 155, y0 + 148, x2 + 185, y0 + 120, x2 + 190, y0 + 155, x2 + 195, y0 + 190, x2 + 230, y0 + 185, FIELD))
    p.append(text(x2 + 190, y0 + 108, "Петля слабини", size=9, color=FIELD, bold=True))

    # TPU Frame clamp / Zip-tie
    p.append(rect(x2 + 225, y0 + 172, 22, 26, fill="#2980b9", stroke=LINE, rx=3))
    p.append(text(x2 + 236, y0 + 160, "Затискач", size=9, color=INK, bold=True))

    # XT60 Connector
    p.append(rect(x2 + 265, y0 + 175, 28, 20, fill="#f1c40f", stroke=LINE, rx=2))
    p.append(text(x2 + 279, y0 + 189, "XT60", size=9, color=INK, bold=True))

    # Battery separating cleanly at XT60
    p.append(rect(x2 + 300, y0 + 170, 28, 20, fill="#d4ac0d", stroke=LINE, rx=2))
    p.append(arrow(x2 + 332, y0 + 180, x2 + 365, y0 + 180, color=FIELD, sw=2.5))
    p.append(text(x2 + 335, y0 + 160, "Чистий розрив", size=9, color=FIELD, bold=True))

    p.append(rect(x2 + 15, y0 + 242, w_card - 30, 44, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    p.append(text(x2 + w_card / 2, y0 + 260, "Ударне натягнення гаситься на карбоні рами.", size=10, color=FIELD, bold=True))
    p.append(text(x2 + w_card / 2, y0 + 276, "Розмикається роз'єм XT60, пайка плати ціла", size=9, color=INK))

    render(os.path.join(OUT, "stack-and-strain-relief.svg"), W, H, *p)


def fig_battery_impact_protection():
    W, H = 840, 380
    p = []

    p.append(text(W / 2, 26, "Комплексний механічний захист акумуляторної батареї", size=16, bold=True))

    y0 = 50
    cx = W / 2

    # Top plate of carbon frame
    p.append(rect(cx - 300, y0 + 180, 600, 14, fill="#2c3e50", stroke=LINE, rx=2))
    p.append(text(cx - 190, y0 + 215, "Верхня дека рами (карбон 2.5–3.0 мм)", size=11, color=INK, bold=True))

    # Inverted flush countersunk screws (drawn as small caps on bottom)
    p.append(rect(cx - 170, y0 + 194, 14, 12, fill="#7f8c8d", stroke=LINE, rx=1))
    p.append(text(cx - 163, y0 + 235, "Гвинти впотай (без виступу різьби)", size=9, color=FIELD, bold=True))

    p.append(rect(cx + 170, y0 + 194, 14, 12, fill="#7f8c8d", stroke=LINE, rx=1))

    # Anti-slip silicone pad
    p.append(rect(cx - 240, y0 + 168, 480, 12, fill="#e74c3c", stroke=LINE, rx=2))
    p.append(text(cx, y0 + 177, "Силіконова протиковзка накладка (μ > 0.8)", size=10, color="#ffffff", bold=True))

    # LiPo Battery Pack
    p.append(rect(cx - 220, y0 + 58, 440, 110, fill="#34495e", stroke=LINE, sw=2, rx=6))
    p.append(text(cx, y0 + 105, "LiPo Акумуляторна збірка (Pouch Cells)", size=14, color="#ffffff", bold=True))
    p.append(text(cx, y0 + 128, "М'яка алюмінієва оболонка (вразлива до точкового пробиття)", size=10, color="#bdc3c7"))

    # Front Impact Skid Plate (Carbon / TPU)
    p.append(rect(cx + 225, y0 + 48, 16, 130, fill="#2980b9", stroke=LINE, sw=1.5, rx=4))
    p.append(text(cx + 233, y0 + 36, "Захисна лижа", size=10, color="#2980b9", bold=True))

    # Dual Kevlar Straps with metal buckle (drawn as thick outline / non-overlapping)
    p.append(rect(cx - 120, y0 + 46, 26, 134, fill="none", stroke="#f39c12", sw=4, rx=3))
    p.append(rect(cx - 122, y0 + 40, 30, 8, fill="#7f8c8d", stroke=LINE, rx=2))
    p.append(text(cx - 107, y0 + 28, "Кевларовий ремінь #1", size=9, color=INK, bold=True))

    p.append(rect(cx + 90, y0 + 46, 26, 134, fill="none", stroke="#f39c12", sw=4, rx=3))
    p.append(rect(cx + 88, y0 + 40, 30, 8, fill="#7f8c8d", stroke=LINE, rx=2))
    p.append(text(cx + 103, y0 + 28, "Кевларовий ремінь #2", size=9, color=INK, bold=True))

    # Bottom summary cards
    b_y = y0 + 265
    b_w = 230
    b_h = 44

    p.append(rect(cx - 360, b_y, b_w, b_h, fill=FILL, stroke=FIELD, sw=1.2, rx=4))
    p.append(text(cx - 245, b_y + 18, "1. Подвійний ремінь", size=10, color=FIELD, bold=True))
    p.append(text(cx - 245, b_y + 34, "Утримання перевантажень > 30g", size=9, color=INK))

    p.append(rect(cx - 115, b_y, b_w, b_h, fill=FILL, stroke=FIELD, sw=1.2, rx=4))
    p.append(text(cx, b_y + 18, "2. Силіконова основа", size=10, color=FIELD, bold=True))
    p.append(text(cx, b_y + 34, "Блокування зсуву при терті", size=9, color=INK))

    p.append(rect(cx + 130, b_y, b_w, b_h, fill=FILL, stroke=FIELD, sw=1.2, rx=4))
    p.append(text(cx + 245, b_y + 18, "3. Лобова лижа", size=10, color=FIELD, bold=True))
    p.append(text(cx + 245, b_y + 34, "Захист від пробиття гілками/камінням", size=9, color=INK))

    render(os.path.join(OUT, "battery-impact-protection.svg"), W, H, *p)


if __name__ == "__main__":
    fig_energy_absorption_zones()
    fig_shear_screw_mechanism()
    fig_stack_and_strain_relief()
    fig_battery_impact_protection()
    print("All figures generated successfully.")
