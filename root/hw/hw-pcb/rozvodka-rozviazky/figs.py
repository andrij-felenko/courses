# -*- coding: utf-8 -*-
"""Фігури до теми «Розводка розв'язки: площа петлі й де насправді стоїть конденсатор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def polygon(pts, fill=FILL, stroke=LINE, sw=1.5):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (p, fill, stroke, sw)


def head(cx, cy, ang_deg, color, size=8):
    a = math.radians(ang_deg)
    bx, by = math.cos(a), math.sin(a)
    px, py = -by, bx
    x1, y1 = cx - bx * size + px * size * 0.55, cy - by * size + py * size * 0.55
    x2, y2 = cx - bx * size - px * size * 0.55, cy - by * size - py * size * 0.55
    return ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
            % (cx, cy, x1, y1, x2, y2, color))


# ── Фігура 1: Порівняння топологій розв'язки та площ петель струму ───────────
def fig_loop_inductance():
    W, H = 940, 580
    P = []

    # Тло панелей
    P.append(rect(20, 50, 435, 505, fill="#fffaf9", stroke="#f5c6cb", sw=1.5, rx=8))
    P.append(rect(485, 50, 435, 505, fill="#f8fbf9", stroke="#c3e6cb", sw=1.5, rx=8))

    # Заголовки панелей
    P.append(text(237, 78, "Хибна топологія: довгі відводи й велика петля", size=13, color=POS, bold=True))
    P.append(text(702, 78, "Оптимальна топологія: прямий хід і замкнений потік", size=13, color=FIELD, bold=True))

    # ── Ліва панель: Помилкова розводка ──
    # Чіп
    P.append(rect(45, 115, 110, 150, fill="#e9ecef", stroke="#495057", sw=2.0, rx=4))
    P.append(text(100, 185, "ЧІП (IC)", size=13, color="#212529", bold=True))
    P.append(text(100, 205, "Кристал", size=11, color=MUTED))

    # Піни чіпа
    P.append(rect(155, 140, 25, 20, fill="#ffd8a8", stroke="#d9480f", sw=1.5, rx=2))
    P.append(text(167, 154, "VDD", size=9.5, color="#d9480f", bold=True))
    P.append(rect(155, 205, 25, 20, fill="#a5d8ff", stroke="#1864ab", sw=1.5, rx=2))
    P.append(text(167, 219, "GND", size=9.5, color="#1864ab", bold=True))

    # Доріжка VDD до вії у площину
    P.append(rect(180, 145, 45, 10, fill=POS, stroke="none"))
    P.append(circle(235, 150, 12, fill="#ffe3e3", stroke=POS, sw=2))
    P.append(circle(235, 150, 5, fill=POS, stroke="none"))
    P.append(text(235, 130, "Вія VDD", size=10.5, color=POS, bold=True))

    # Доріжка GND до вії у площину
    P.append(rect(180, 210, 45, 10, fill=NEG, stroke="none"))
    P.append(circle(235, 215, 12, fill="#d0ebff", stroke=NEG, sw=2))
    P.append(circle(235, 215, 5, fill=NEG, stroke="none"))
    P.append(text(235, 240, "Вія GND", size=10.5, color=NEG, bold=True))

    # Конденсатор, винесений далеко з окремими віями
    P.append(rect(330, 135, 80, 110, fill="#f1f3f5", stroke="#adb5bd", sw=1.2, rx=4))
    P.append(text(370, 155, "Конденсатор 0402", size=10, color=MUTED))

    # Пади конденсатора
    P.append(rect(345, 170, 20, 30, fill="#ffd8a8", stroke="#d9480f", sw=1.5, rx=2))
    P.append(rect(375, 170, 20, 30, fill="#a5d8ff", stroke="#1864ab", sw=1.5, rx=2))
    P.append(rect(365, 175, 10, 20, fill="#ced4da", stroke="#868e96", sw=1.0))

    # Вії конденсатора
    P.append(circle(355, 225, 10, fill="#ffe3e3", stroke=POS, sw=1.8))
    P.append(circle(355, 225, 4, fill=POS, stroke="none"))
    P.append(line(355, 200, 355, 215, color=POS, sw=4))

    P.append(circle(385, 225, 10, fill="#d0ebff", stroke=NEG, sw=1.8))
    P.append(circle(385, 225, 4, fill=NEG, stroke="none"))
    P.append(line(385, 200, 385, 215, color=NEG, sw=4))

    # Траєкторія петлі струму (червона/синя пунктирна лінія у внутрішніх шарах)
    loop_bad = [(235, 150), (280, 150), (355, 150), (355, 225)]
    P.append(polyline(loop_bad, color=POS, sw=2.2, dash="4,3"))
    loop_bad_ret = [(385, 225), (385, 215), (280, 215), (235, 215)]
    P.append(polyline(loop_bad_ret, color=NEG, sw=2.2, dash="4,3"))

    # Велика площа петлі S1
    P.append(polygon([(235, 150), (355, 150), (385, 225), (235, 215)], fill="#ffe3e3", stroke=POS, sw=1.2))
    P.append(text(300, 185, "Велика площа петлі S₁", size=11, color=POS, bold=True))
    P.append(text(300, 200, "L_монтажу ≈ 2.8–3.5 нГн", size=10.5, color=POS))

    # Схема заміщення та наслідок
    P.append(rect(45, 305, 385, 230, fill="#ffffff", stroke="#dee2e6", sw=1.2, rx=6))
    P.append(text(237, 328, "Фізичний наслідок помилки:", size=11.5, color=POS, bold=True))
    bad_expl = [
        "1. Струм ВЧ іде через площину в обхід конденсатора;",
        "2. Вії утворюють відкритий магнітний контур (високий ESL);",
        "3. Відстань між віями > 3 мм послаблює взаємну індуктивність M;",
        "4. Просідання напруги на кристалі: ΔV = L·(di/dt) > 250 мВ;",
        "5. Високе випромінювання EMI через паразитну рамкову антену."
    ]
    for idx, el in enumerate(bad_expl):
        P.append(text(58, 358 + idx * 24, el, size=10.5, color=INK, anchor="start"))
    P.append(text(237, 510, "Конденсатор фактично відрізаний індуктивністю", size=11, color=POS, bold=True))


    # ── Права панель: Оптимальна розводка ──
    # Чіп
    P.append(rect(510, 115, 110, 150, fill="#e9ecef", stroke="#495057", sw=2.0, rx=4))
    P.append(text(565, 185, "ЧІП (IC)", size=13, color="#212529", bold=True))
    P.append(text(565, 205, "Кристал", size=11, color=MUTED))

    # Піни чіпа
    P.append(rect(620, 140, 25, 20, fill="#ffd8a8", stroke="#d9480f", sw=1.5, rx=2))
    P.append(text(632, 154, "VDD", size=9.5, color="#d9480f", bold=True))
    P.append(rect(620, 205, 25, 20, fill="#a5d8ff", stroke="#1864ab", sw=1.5, rx=2))
    P.append(text(632, 219, "GND", size=9.5, color="#1864ab", bold=True))

    # Конденсатор впритул: шлях струму йде СПЕРШУ через пади
    # Пади C
    P.append(rect(655, 135, 30, 30, fill="#ffd8a8", stroke="#d9480f", sw=1.8, rx=2))
    P.append(text(670, 153, "C+", size=10, color="#d9480f", bold=True))
    P.append(rect(655, 195, 30, 30, fill="#a5d8ff", stroke="#1864ab", sw=1.8, rx=2))
    P.append(text(670, 213, "C−", size=10, color="#1864ab", bold=True))
    P.append(rect(660, 165, 20, 30, fill="#ced4da", stroke="#868e96", sw=1.0))

    # Доріжки від пінів чіпа до падів конденсатора (широкі й ультракороткі)
    P.append(rect(645, 142, 10, 16, fill=POS, stroke="none"))
    P.append(rect(645, 207, 10, 16, fill=NEG, stroke="none"))

    # Бічні вії впритул до падів (Side-Vias з мінімальним зазором s)
    P.append(circle(705, 150, 11, fill="#ffe3e3", stroke=POS, sw=2))
    P.append(circle(705, 150, 4.5, fill=POS, stroke="none"))
    P.append(line(685, 150, 694, 150, color=POS, sw=5))
    P.append(text(745, 154, "Вія VDD", size=10, color=POS, bold=True))

    P.append(circle(705, 210, 11, fill="#d0ebff", stroke=NEG, sw=2))
    P.append(circle(705, 210, 4.5, fill=NEG, stroke="none"))
    P.append(line(685, 210, 694, 210, color=NEG, sw=5))
    P.append(text(745, 214, "Вія GND", size=10, color=NEG, bold=True))

    # Додаткова симетрична пара вій (Double Side Vias)
    P.append(circle(670, 105, 10, fill="#ffe3e3", stroke=POS, sw=1.8))
    P.append(circle(670, 105, 4, fill=POS, stroke="none"))
    P.append(line(670, 135, 670, 115, color=POS, sw=4))

    P.append(circle(670, 255, 10, fill="#d0ebff", stroke=NEG, sw=1.8))
    P.append(circle(670, 255, 4, fill=NEG, stroke="none"))
    P.append(line(670, 225, 670, 245, color=NEG, sw=4))

    # Маленька площа петлі S2
    P.append(polygon([(632, 150), (670, 150), (670, 210), (632, 210)], fill="#d3f9d8", stroke=FIELD, sw=1.2))
    P.append(text(790, 175, "Мініатюрна петля S₂", size=11, color=FIELD, bold=True))
    P.append(text(790, 192, "L_монтажу ≈ 0.4–0.6 нГн", size=10.5, color=FIELD))

    # Стрілки взаємної компенсації потоку B
    P.append(text(790, 212, "Компенсація потоків M", size=10, color="#2b8a3e", italic=True))

    # Наслідок правильної топології
    P.append(rect(510, 305, 385, 230, fill="#ffffff", stroke="#dee2e6", sw=1.2, rx=6))
    P.append(text(702, 328, "Переваги мінімальної петлі:", size=11.5, color=FIELD, bold=True))
    good_expl = [
        "1. Пін чіпа з'єднано з конденсатором ПЕРЕД виходом у площину;",
        "2. Бічні перехідні отвори розміщені на відстані s < 0.6 мм;",
        "3. Зустрічні струми створюють взаємну індуктивність M ≈ L;",
        "4. Подвійні вії знижують індуктивність паралельно (L_via / 2);",
        "5. Просідання напруги мінімальне: ΔV < 35 мВ (у межах норми)."
    ]
    for idx, el in enumerate(good_expl):
        P.append(text(523, 358 + idx * 24, el, size=10.5, color=INK, anchor="start"))
    P.append(text(702, 510, "Струм миттєво береться з локального конденсатора", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "loop-inductance-comparison.svg"), W, H, *P,
           title="Порівняння контурів розв'язки: площа петлі струму визначає паразитну індуктивність")


# ── Фігура 2: Розв'язка під BGA через Via-in-Pad (VIPPO) на зворотній стороні ───
def fig_bga_decoupling():
    W, H = 940, 600
    P = []

    # Тло
    P.append(rect(20, 50, 900, 530, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))

    # Заголовок секції
    P.append(text(470, 78, "Розріз BGA-вузла: розв'язка на звороті (Bottom) через Via-in-Pad", size=13.5, color=INK, bold=True))

    # Корпус BGA (угорі)
    P.append(rect(140, 100, 660, 50, fill="#343a40", stroke="#212529", sw=2, rx=4))
    P.append(text(470, 122, "Корпус мікросхеми BGA (SoC / FPGA)", size=12.5, color="#ffffff", bold=True))
    P.append(text(470, 138, "Кристал кремнію, підкладка та внутрішні перерозподільні шари (RDL)", size=10.5, color="#ced4da"))

    # Кульки BGA (Solder Balls)
    balls = [
        (220, "GND", NEG, "#d0ebff"),
        (300, "VDD", POS, "#ffe3e3"),
        (380, "GND", NEG, "#d0ebff"),
        (460, "VDD", POS, "#ffe3e3"),
        (540, "GND", NEG, "#d0ebff"),
        (620, "VDD", POS, "#ffe3e3"),
        (700, "GND", NEG, "#d0ebff"),
    ]
    for bx, name, col, bgcol in balls:
        P.append(circle(bx, 172, 14, fill=bgcol, stroke=col, sw=2))
        P.append(text(bx, 176, name, size=9.5, color=col, bold=True))

    # Плата: підкладка та мідні шари
    # Субстрат плати (єдиний блок діелектрика)
    P.append(rect(100, 195, 740, 200, fill="#f8f9fa", stroke="#ced4da", sw=1.5, rx=2))
    P.append(text(60, 295, "Плата", size=11, color=MUTED, bold=True))

    # Мідні шари (провідні лінії)
    # L1 Top
    P.append(line(100, 196, 840, 196, color="#d9480f", sw=3.5))
    P.append(text(60, 200, "L1 Top", size=10, color="#d9480f", bold=True))

    # L2 GND Plane
    P.append(line(100, 252, 840, 252, color=NEG, sw=3.5))
    P.append(text(60, 256, "L2 GND", size=10, color=NEG, bold=True))

    # L3 VDD Plane
    P.append(line(100, 327, 840, 327, color=POS, sw=3.5))
    P.append(text(60, 331, "L3 VDD", size=10, color=POS, bold=True))

    # L6 Bottom
    P.append(line(100, 394, 840, 394, color="#d9480f", sw=3.5))
    P.append(text(60, 398, "L6 Bot", size=10, color="#d9480f", bold=True))

    # Перехідні отвори Via-in-Pad (VIPPO), заповнені міддю та смолою
    vias = [
        (300, POS, 327, "VDD via"),
        (380, NEG, 252, "GND via"),
        (460, POS, 327, "VDD via"),
        (540, NEG, 252, "GND via"),
    ]
    for vx, col, plane_y, lab in vias:
        # Стовбур вії через лінії
        P.append(line(vx, 195, vx, 394, color=col, sw=10))
        # З'єднання з площиною
        P.append(line(vx - 14, plane_y + 5, vx + 14, plane_y + 5, color=col, sw=8))

    # Конденсатори на Bottom layer прямо під BGA
    # Конденсатор 1 під парою (300, 380)
    P.append(rect(318, 400, 44, 22, fill="#e9ecef", stroke="#495057", sw=1.5, rx=3))
    P.append(rect(296, 398, 20, 26, fill="#ffe3e3", stroke=POS, sw=1.5, rx=2))
    P.append(rect(364, 398, 20, 26, fill="#d0ebff", stroke=NEG, sw=1.5, rx=2))
    P.append(text(340, 415, "0402", size=9.5, color=MUTED, bold=True))

    # Конденсатор 2 під парою (460, 540)
    P.append(rect(478, 400, 44, 22, fill="#e9ecef", stroke="#495057", sw=1.5, rx=3))
    P.append(rect(456, 398, 20, 26, fill="#ffe3e3", stroke=POS, sw=1.5, rx=2))
    P.append(rect(524, 398, 20, 26, fill="#d0ebff", stroke=NEG, sw=1.5, rx=2))
    P.append(text(500, 415, "0201", size=9.5, color=MUTED, bold=True))

    # Вертикальна петля струму (Стрілки)
    # Петля через пару (300, 380):
    P.append(arrow(300, 388, 300, 200, color="#ffffff", sw=2.5))
    P.append(arrow(300, 172, 380, 172, color=INK, sw=2))
    P.append(arrow(380, 200, 380, 388, color="#ffffff", sw=2.5))
    P.append(arrow(364, 411, 316, 411, color=NEG, sw=2))

    # Позначка вертикальної петлі
    P.append(rect(275, 235, 130, 55, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    P.append(text(340, 255, "Вертикальна петля", size=10.5, color=FIELD, bold=True))
    P.append(text(340, 273, "h = 1.2 мм, L < 0.4 нГн", size=9.5, color=FIELD))

    # Пояснювальний блок унизу
    P.append(rect(100, 445, 740, 120, fill="#ffffff", stroke="#dee2e6", sw=1.2, rx=6))
    P.append(text(470, 468, "Чому монтаж під BGA на Bottom шарі перемагає бічне розміщення на Top:", size=11.5, color=INK, bold=True))
    bga_notes = [
        "• Відсутність горизонтальних доріжок Top-шару: струм іде прямо вниз через короткий стовбур вії;",
        "• Кульки VDD і GND розміщені на сусідніх позиціях матриці BGA (pitch 0.8 мм або 0.5 мм);",
        "• Зустрічні струми у сусідніх віях компенсують магнітні поля, знижуючи ефективну індуктивність;",
        "• Технологія VIPPO (Via-in-Pad Plated Over) усуває 'собачі кістки' (dog-bones) та паразити розводки."
    ]
    for idx, note in enumerate(bga_notes):
        P.append(text(120, 492 + idx * 18, note, size=10.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "via-in-pad-bga-decoupling.svg"), W, H, *P,
           title="Монтаж розв'язувальних конденсаторів під BGA: мінімізація вертикальної петлі струму")


if __name__ == "__main__":
    fig_loop_inductance()
    fig_bga_decoupling()
    print("Фігури успішно згенеровано.")
