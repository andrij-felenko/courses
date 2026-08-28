# -*- coding: utf-8 -*-
"""Фігури для теми kriplennia-platy-stiiky-dopusky (кріплення плати, стійки, допуски).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори
BOARD_FILL   = "#e2e8f0"   # основа плати
BOARD_STROKE = "#475569"   # контур плати
COPPER_PAD   = "#f59e0b"   # мідні площадки
COPPER_FILL  = "#fef3c7"   # світла мідь
KEEPOUT_FILL = "#fee2e2"   # зона заборони (червонувата)
KEEPOUT_LINE = "#ef4444"   # контур заборони
TOOL_FILL    = "#ede9fe"   # зона доступу інструмента (фіолетова)
TOOL_LINE    = "#8b5cf6"
SCREW_FILL   = "#94a3b8"   # метал гвинта
SCREW_STROKE = "#334155"
WASHER_FILL  = "#cbd5e1"
WASHER_STROKE= "#64748b"


# ── 1. Зони відчуження кріпильного отвору під гвинт M3 ─────────────────────────
def fig_screw_keepout_zone():
    W, H = 840, 520
    frags = []

    # Фонова панель
    frags.append(rect(10, 10, 820, 500, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))

    # Заголовок зверху
    frags.append(text(420, 36, "Зони відчуження навколо кріпильного отвору M3 (Keepout Clearance Layers)", size=15, color=INK, bold=True))

    # Ліва частина: вигляд зверху (концентричні зони)
    cx, cy = 250, 260

    # Фрагмент друкованої плати (зелений/сірий текстоліт)
    frags.append(rect(40, 70, 420, 380, fill=BOARD_FILL, stroke=BOARD_STROKE, sw=1.5, rx=8))
    frags.append(text(80, 95, "Текстоліт PCB (Top Layer)", size=12, color=MUTED, bold=True))

    # Зона 4: Доступ монтажного інструмента (Tooling Keepout Ø12.0 мм, R=140px)
    r_tool = 140
    frags.append(circle(cx, cy, r_tool, fill=TOOL_FILL, stroke=TOOL_LINE, sw=1.5))

    # Зона 3: Зона заборони SMD компонентів і доріжок (Component Keepout Ø9.5 мм, R=105px)
    r_comp = 105
    frags.append(circle(cx, cy, r_comp, fill=KEEPOUT_FILL, stroke=KEEPOUT_LINE, sw=1.5))

    # Зона 2: Шайба DIN 125 / DIN 9021 (Washer Area Ø7.0 мм, R=70px)
    r_wash = 70
    frags.append(circle(cx, cy, r_wash, fill=WASHER_FILL, stroke=WASHER_STROKE, sw=1.5))

    # Зона 1: Мідний опорний майданчик (Annular Ring Pad Ø6.0 мм, R=56px)
    r_pad = 56
    frags.append(circle(cx, cy, r_pad, fill=COPPER_FILL, stroke=COPPER_PAD, sw=1.8))

    # Віаси зшивки шарів шасі (Stitching Vias навколо отвору)
    num_vias = 8
    r_via_orbit = 46
    for i in range(num_vias):
        ang = i * (2 * math.pi / num_vias)
        vx = cx + r_via_orbit * math.cos(ang)
        vy = cy + r_via_orbit * math.sin(ang)
        frags.append(circle(vx, vy, 4.5, fill="#fef3c7", stroke=COPPER_PAD, sw=1.2))
        frags.append(circle(vx, vy, 2.0, fill="#ffffff", stroke="#334155", sw=0.8))

    # Контур головки гвинта M3 (Screw Head ISO 7045 Ø5.6 мм, R=44px)
    r_screw = 44
    frags.append(circle(cx, cy, r_screw, fill="none", stroke=SCREW_STROKE, sw=1.8))

    # Отвор свердління (Drill Hole Ø3.2 мм, R=26px)
    r_hole = 26
    frags.append(circle(cx, cy, r_hole, fill="#ffffff", stroke="#0f172a", sw=2.0))

    # Хрестовина центру
    frags.append(line(cx - 32, cy, cx + 32, cy, color="#64748b", sw=1.0))
    frags.append(line(cx, cy - 32, cx, cy + 32, color="#64748b", sw=1.0))

    # SMD компоненти за межами зони заборони
    # Резистор 0805: лівий термінал, керамічне тіло, правий термінал (не перекриваються)
    frags.append(rect(370, 110, 6, 16, fill="#cbd5e1", stroke="#64748b", sw=0.8, rx=1))
    frags.append(rect(376, 110, 18, 16, fill="#334155", stroke="#0f172a", sw=1.0, rx=1))
    frags.append(rect(394, 110, 6, 16, fill="#cbd5e1", stroke="#64748b", sw=0.8, rx=1))
    frags.append(text(385, 104, "R 0805", size=9, color=MUTED, bold=True))

    # Конденсатор MLCC 1206 (не перекриваються)
    frags.append(rect(70, 395, 7, 18, fill="#cbd5e1", stroke="#64748b", sw=0.8, rx=1))
    frags.append(rect(77, 395, 22, 18, fill="#b45309", stroke="#78350f", sw=1.0, rx=1))
    frags.append(rect(99, 395, 7, 18, fill="#cbd5e1", stroke="#64748b", sw=0.8, rx=1))
    frags.append(text(88, 388, "MLCC 1206", size=9, color=MUTED, bold=True))

    # Сигнальна доріжка, що огинає зону відчуження
    trace_path = f"M 60,180 L 120,180 A {r_comp + 12} {r_comp + 12} 0 0 0 180,390 L 240,430"
    frags.append(f'<path d="{trace_path}" fill="none" stroke="{COPPER_PAD}" stroke-width="2.5"/>')
    frags.append(text(95, 172, "Сигнальна доріжка", size=10, color="#b45309", bold=True))

    # Права частина: Специфікація та легенда діаметрів
    lx = 480
    frags.append(rect(lx, 70, 330, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(lx + 165, 96, "Геометричний бюджет (M3)", size=13, color=INK, bold=True))

    # Елементи легенди (кольоровий маркер + текст)
    items = [
        (COPPER_PAD, COPPER_FILL, "1. Отвор свердління", "Ø3.2 мм (+0.1/-0.05 мм)", "Вільний прохід гвинта M3 (PTH/NPTH)"),
        (COPPER_PAD, COPPER_FILL, "2. Мідна площадка (Pad)", "Ø6.0 мм (Stitching Vias)", "Опорна площина + контакт із шасі"),
        (SCREW_STROKE, "none", "3. Головка гвинта M3", "Ø5.6 мм (ISO 7045)", "Зона безпосереднього тиску шліца"),
        (WASHER_STROKE, WASHER_FILL, "4. Плоска шайба DIN 125", "Ø7.0 мм (t = 0.5 мм)", "Розподіл осьового зусилля затяжки"),
        (KEEPOUT_LINE, KEEPOUT_FILL, "5. Зона заборони SMD (Keepout)", "Ø9.5 мм (Радіус R4.75 мм)", "Заборона MLCC, IC та переходів"),
        (TOOL_LINE, TOOL_FILL, "6. Доступ інструмента (Tooling)", "Ø12.0 мм (Висота Z > 15 мм)", "Прохід бити електровикрутки")
    ]

    item_y = 125
    for stroke_col, fill_col, title_txt, val_txt, desc_txt in items:
        # Маркер
        frags.append(rect(lx + 15, item_y - 10, 16, 16, fill=fill_col if fill_col != "none" else "#ffffff", stroke=stroke_col, sw=1.5, rx=3))
        frags.append(text(lx + 40, item_y + 2, title_txt, size=11, color=INK, anchor="left", bold=True))
        frags.append(text(lx + 230, item_y + 2, val_txt, size=10, color=NEG, anchor="left", bold=True))
        frags.append(text(lx + 40, item_y + 16, desc_txt, size=9, color=MUTED, anchor="left"))
        item_y += 42

    # Примітка знизу
    frags.append(text(lx + 165, 432, "Стандарти: IPC-2221 §9.2, IPC-7351, DIN 125A", size=10, color=MUTED, bold=True))

    # Нижній висновок
    frags.append(text(420, 485, "Порушення зони заборони SMD призводить до розтріскування кераміки та зрізу паяних з'єднань.", size=12, color=POS, bold=True))

    render(os.path.join(OUT, "screw-keepout-zone-clearance.svg"), W, H, *frags)


# ── 2. Механічний вигин плати та утворення тріщин у MLCC ──────────────────────
def fig_pcb_bending_mlcc_fracture():
    W, H = 840, 520
    frags = []

    # Фонова панель
    frags.append(rect(10, 10, 820, 500, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))

    # Заголовок зверху
    frags.append(text(420, 36, "Механічні напруження при затягуванні стійок і механізм зламу MLCC", size=15, color=INK, bold=True))

    # ── Верхня половина: Схема прогину плати між стійками ──
    # Основа корпусу
    frags.append(rect(50, 200, 740, 16, fill="#cbd5e1", stroke="#475569", sw=1.5, rx=2))
    frags.append(text(420, 212, "Металева основа корпусу (Enclosure Chassis Base)", size=11, color="#1e293b", bold=True))

    # Ліва стійка (H = 50px, Y=150..200)
    frags.append(rect(110, 150, 40, 50, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=2))
    frags.append(text(130, 178, "Стійка 1", size=10, color="#854d0e", bold=True))

    # Права стійка (H = 50px, Y=150..200)
    frags.append(rect(690, 150, 40, 50, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=2))
    frags.append(text(710, 178, "Стійка 2", size=10, color="#854d0e", bold=True))

    # Центральна стійка з дефектом висоти (-0.4 мм, нижча) -> прогин
    frags.append(rect(400, 162, 40, 38, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=2))
    frags.append(text(420, 185, "Δh = 0.4 мм", size=9, color=POS, bold=True))

    # Прогнута друкована плата (дуга Bezier від X=110 до X=730)
    # Точки кріплення: гвинти притискають плату до стійок
    frags.append('<path d="M 100,146 Q 420,166 740,146 L 740,154 Q 420,174 100,154 Z" fill="#94a3b8" stroke="#334155" stroke-width="1.8"/>')
    frags.append(text(250, 138, "Нейтральна вісь деформації PCB (Neutral Bending Axis)", size=10, color="#334155", italic=True))

    # Гвинти затяжки
    # Лівий гвинт
    frags.append(rect(122, 134, 16, 12, fill="#64748b", stroke="#1e293b", sw=1.2, rx=2))
    # Правий гвинт
    frags.append(rect(702, 134, 16, 12, fill="#64748b", stroke="#1e293b", sw=1.2, rx=2))
    # Центральний гвинт (затягується вниз, вигинаючи плату)
    frags.append(rect(412, 150, 16, 12, fill="#64748b", stroke="#1e293b", sw=1.2, rx=2))
    frags.append(arrow(420, 115, 420, 145, color=POS, sw=2.5))
    frags.append(text(420, 105, "Осьова сила F_clamp (Затяжка M3: 0.6 Н·м)", size=11, color=POS, bold=True))

    # Стрілки розтягу на верхній поверхні плати
    frags.append(arrow(340, 150, 300, 146, color=POS, sw=1.5))
    frags.append(arrow(500, 150, 540, 146, color=POS, sw=1.5))
    frags.append(text(340, 138, "Розтяг (+ε)", size=10, color=POS, bold=True))
    frags.append(text(500, 138, "Розтяг (+ε)", size=10, color=POS, bold=True))


    # ── Нижня половина: Збільшений вигляд розтріскування MLCC ──
    # Рамка мікроструктури
    frags.append(rect(50, 240, 740, 220, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(220, 262, "Фізика 45° зсувної тріщини в кераміці MLCC", size=12, color=INK, bold=True))

    # Базова лінія текстоліту під конденсатором
    bx, by = 90, 380
    frags.append(rect(bx, by, 340, 30, fill=BOARD_FILL, stroke=BOARD_STROKE, sw=1.5, rx=2))
    frags.append(text(bx + 170, by + 20, "FR-4 Ламінат (Вигин під напруженням σ > 100 МПа)", size=10, color=MUTED, bold=True))

    # Мідні контактні майданчики (Pads)
    pad_w, pad_h = 45, 8
    frags.append(rect(bx + 30, by - 8, pad_w, pad_h, fill=COPPER_FILL, stroke=COPPER_PAD, sw=1.5, rx=1))
    frags.append(rect(bx + 265, by - 8, pad_w, pad_h, fill=COPPER_FILL, stroke=COPPER_PAD, sw=1.5, rx=1))

    # Керамічне тіло MLCC (BaTiO3)
    cap_x, cap_y = bx + 55, by - 70
    cap_w, cap_h = 230, 62
    frags.append(rect(cap_x, cap_y, cap_w, cap_h, fill="#b45309", stroke="#78350f", sw=1.8, rx=4))
    frags.append(text(cap_x + 115, cap_y + 35, "Керамічний діелектрик (BaTiO3)", size=11, color="#fef3c7", bold=True))

    # Металеві термінації (Нікель/Олово)
    term_w = 40
    frags.append(rect(cap_x, cap_y, term_w, cap_h, fill="#94a3b8", stroke="#475569", sw=1.2, rx=2))
    frags.append(rect(cap_x + cap_w - term_w, cap_y, term_w, cap_h, fill="#94a3b8", stroke="#475569", sw=1.2, rx=2))

    # Паяльні меніски (Solder Fillets)
    frags.append(f'<polygon points="{bx+30},{by-8} {bx+75},{by-8} {bx+95},{cap_y+30} {bx+95},{cap_y+62} {bx+30},{cap_y+62}" fill="#cbd5e1" stroke="#64748b" stroke-width="1.2"/>')
    frags.append(f'<polygon points="{bx+310},{by-8} {bx+265},{by-8} {bx+245},{cap_y+30} {bx+245},{cap_y+62} {bx+310},{cap_y+62}" fill="#cbd5e1" stroke="#64748b" stroke-width="1.2"/>')
    frags.append(text(bx + 40, by - 20, "Припій", size=9, color="#475569", bold=True))

    # 45-градусна тріщина в кутку (Shear Flex Crack)
    crack_path = f"M {cap_x + term_w},{cap_y + cap_h} L {cap_x + term_w + 35},{cap_y + cap_h - 35} L {cap_x + term_w + 50},{cap_y + 10}"
    frags.append(f'<path d="{crack_path}" fill="none" stroke="{POS}" stroke-width="3.0"/>')
    frags.append(circle(cap_x + term_w, cap_y + cap_h, 4, fill=POS, stroke="#ffffff", sw=1.0))
    frags.append(text(cap_x + term_w + 55, cap_y + 25, "Зсувна тріщина 45°", size=10, color=POS, bold=True))

    # Внутрішні електроди MLCC
    for ely in range(cap_y + 12, cap_y + cap_h - 10, 8):
        frags.append(line(cap_x + 10, ely, cap_x + 160, ely, color="#e2e8f0", sw=1.0))
        frags.append(line(cap_x + 70, ely + 4, cap_x + cap_w - 10, ely + 4, color="#e2e8f0", sw=1.0))

    # Права панель пояснень та правил
    rx = 470
    frags.append(rect(rx, 255, 305, 190, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=6))
    frags.append(text(rx + 152, 275, "Правила захисту MLCC (IPC/JEDEC-9704)", size=11, color=INK, bold=True))

    rules = [
        ("Орієнтація:", "Розміщувати паралельно осі вигину", POS),
        ("Відстань d_min:", "≥ 3.0 мм (для 0603/0805), ≥ 5.0 мм (1206+)", NEG),
        ("Деформація ε:", "Граничний мікрострейн ε_max ≤ 500 με", POS),
        ("Термінація:", "Використовувати Soft-Termination (полімер)", FIELD),
        ("Пази (Slits):", "Фрезерувати розвантажувальні пази", INK)
    ]
    ry = 300
    for title_r, val_r, col_r in rules:
        frags.append(text(rx + 12, ry, title_r, size=10, color=col_r, anchor="left", bold=True))
        frags.append(text(rx + 105, ry, val_r, size=9.5, color=INK, anchor="left"))
        ry += 24

    # Загальний підсумок знизу
    frags.append(text(420, 488, "Навіть мікротріщина глибиною 20 мкм спричиняє внутрішній пробій шарів і коротке замикання шини живлення.", size=11, color=POS, bold=True))

    render(os.path.join(OUT, "pcb-bending-stress-mlcc-fracture.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_screw_keepout_zone()
    fig_pcb_bending_mlcc_fracture()
    print("Figures generated successfully in", OUT)
