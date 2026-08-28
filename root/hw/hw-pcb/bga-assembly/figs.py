# -*- coding: utf-8 -*-
"""Фігури для теми bga-assembly (BGA: монтаж і контроль).
Генерує 2 SVG-діаграми:
1. bga-smd-vs-nsmd-geometry.svg — порівняння SMD та NSMD контактних площадок BGA.
2. head-in-pillow-defect-mechanism.svg — стадії утворення дефекту Head-in-Pillow.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER      = "#b5763a"
COPPER_FILL = "#e8c9a3"
SOLDER      = "#475569"
SOLDER_FILL = "#cbd5e1"
MASK        = "#1e7e34"
MASK_FILL   = "#c3e6cb"
DIELECTRIC  = "#e2e8f0"
DIELECTRIC_STR = "#94a3b8"
SUBSTRATE   = "#fef3c7"
SUBSTRATE_STR = "#d97706"
STRESS_COL  = "#dc2626"
PASTE_FILL  = "#94a3b8"
OXIDE_COL   = "#ea580c"


def fig_smd_vs_nsmd():
    p = os.path.join(OUT, "bga-smd-vs-nsmd-geometry.svg")
    w, h = 920, 560
    frags = []

    # Тло
    frags.append(rect(10, 10, 900, 540, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=8))

    # Заголовок
    frags.append(text(460, 36, "Геометрія контактних площадок BGA: SMD проти NSMD", size=16, color=INK, bold=True))

    # Ліва колонка: SMD
    lx, rx_col = 30, 470
    col_w = 420

    # ── Лівий блок (SMD) ──
    frags.append(rect(lx, 60, col_w, 470, fill="#f8fafc", stroke="#e2e8f0", sw=1.2, rx=6))
    frags.append(text(lx + col_w / 2, 86, "SMD (Solder Mask Defined)", size=14, color=INK, bold=True))
    frags.append(text(lx + col_w / 2, 106, "Площадка обмежена вікном паяльної маски", size=11, color=MUTED))

    # Схема SMD
    # Підкладка мікросхеми (угорі)
    bga_sub_y = 135
    frags.append(rect(lx + 50, bga_sub_y, 320, 18, fill=SUBSTRATE, stroke=SUBSTRATE_STR, sw=1.2, rx=2))
    frags.append(text(lx + 210, bga_sub_y + 13, "Підкладка BGA / Корпус", size=10, color="#92400e", bold=True))
    # Верхня площадка на чіпі
    frags.append(rect(lx + 150, bga_sub_y + 18, 120, 6, fill=COPPER_FILL, stroke=COPPER, sw=1.0, rx=1))

    # Діелектрик плати FR-4 (внизу)
    pcb_y = 330
    frags.append(rect(lx + 40, pcb_y, 340, 35, fill=DIELECTRIC, stroke=DIELECTRIC_STR, sw=1.2, rx=2))
    frags.append(text(lx + 210, pcb_y + 22, "Друкована плата (FR-4 PCB)", size=10, color=MUTED, bold=True))

    # Мідна площадка на платі (широка, бо заходить під маску)
    smd_pad_w, smd_pad_h = 190, 10
    smd_pad_x = lx + 210 - smd_pad_w / 2
    smd_pad_y = pcb_y - smd_pad_h
    frags.append(rect(smd_pad_x, smd_pad_y, smd_pad_w, smd_pad_h, fill=COPPER_FILL, stroke=COPPER, sw=1.2, rx=1))

    # Паяльна маска, що напливає на мідь
    mask_h = 16
    mask_y = pcb_y - mask_h
    # Ліва частина маски
    frags.append(rect(lx + 40, mask_y, 85, mask_h, fill=MASK_FILL, stroke=MASK, sw=1.2, rx=1))
    # Права частина маски
    frags.append(rect(lx + 295, mask_y, 85, mask_h, fill=MASK_FILL, stroke=MASK, sw=1.2, rx=1))

    # Паяльна кулька BGA (змочує лише плоску верхню поверхню міді у вікні)
    smd_ball_path = (
        f'M {lx + 150} {bga_sub_y + 24} '
        f'C {lx + 90} 180, {lx + 90} 280, {lx + 125} {mask_y + 4} '
        f'L {lx + 295} {mask_y + 4} '
        f'C {lx + 330} 280, {lx + 330} 180, {lx + 270} {bga_sub_y + 24} Z'
    )
    frags.append(f'<path d="{smd_ball_path}" fill="{SOLDER_FILL}" stroke="{SOLDER}" stroke-width="1.8"/>')
    frags.append(text(lx + 210, 230, "Припій (SAC305)", size=11, color=SOLDER, bold=True))

    # Концентратори напруження (стрілочки/мітки біля краю маски)
    frags.append(circle(lx + 125, mask_y + 4, 4, fill="#fee2e2", stroke=STRESS_COL, sw=1.5))
    frags.append(circle(lx + 295, mask_y + 4, 4, fill="#fee2e2", stroke=STRESS_COL, sw=1.5))
    frags.append(text(lx + 210, 310, "Концентрація зсувних напружень на межі маски", size=10, color=STRESS_COL, bold=True))

    # Характеристики SMD (список у рамці)
    frags.append(rect(lx + 15, 380, col_w - 30, 135, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(lx + 25, 400, "• Робочий діаметр площадки = апертура маски", size=11, color=INK, anchor="start"))
    frags.append(text(lx + 25, 422, "• Змочування: лише верхній торець міді (1D)", size=11, color=INK, anchor="start"))
    frags.append(text(lx + 25, 444, "• Висока стійкість до відриву площадки від плати", size=11, color=INK, anchor="start"))
    frags.append(text(lx + 25, 466, "• Ризик втоми припою через концентрацію напруг", size=11, color=POS, anchor="start"))
    frags.append(text(lx + 25, 488, "• Вужчий канал для трасування провідників", size=11, color=POS, anchor="start"))


    # ── Правий блок (NSMD) ──
    frags.append(rect(rx_col, 60, col_w, 470, fill="#f8fafc", stroke="#e2e8f0", sw=1.2, rx=6))
    frags.append(text(rx_col + col_w / 2, 86, "NSMD (Non-Solder Mask Defined)", size=14, color=INK, bold=True))
    frags.append(text(rx_col + col_w / 2, 106, "Площадка визначена геометрією мідного п'ятака", size=11, color=MUTED))

    # Підкладка мікросхеми (угорі)
    frags.append(rect(rx_col + 50, bga_sub_y, 320, 18, fill=SUBSTRATE, stroke=SUBSTRATE_STR, sw=1.2, rx=2))
    frags.append(text(rx_col + 210, bga_sub_y + 13, "Підкладка BGA / Корпус", size=10, color="#92400e", bold=True))
    # Верхня площадка на чіпі
    frags.append(rect(rx_col + 150, bga_sub_y + 18, 120, 6, fill=COPPER_FILL, stroke=COPPER, sw=1.0, rx=1))

    # Діелектрик плати FR-4 (внизу)
    frags.append(rect(rx_col + 40, pcb_y, 340, 35, fill=DIELECTRIC, stroke=DIELECTRIC_STR, sw=1.2, rx=2))
    frags.append(text(rx_col + 210, pcb_y + 22, "Друкована плата (FR-4 PCB)", size=10, color=MUTED, bold=True))

    # Мідна площадка на платі (автономний мідний острівець меншого розміру)
    nsmd_pad_w, nsmd_pad_h = 140, 10
    nsmd_pad_x = rx_col + 210 - nsmd_pad_w / 2
    nsmd_pad_y = pcb_y - nsmd_pad_h
    frags.append(rect(nsmd_pad_x, nsmd_pad_y, nsmd_pad_w, nsmd_pad_h, fill=COPPER_FILL, stroke=COPPER, sw=1.2, rx=1))

    # Паяльна маска з зазором (clearance) навколо міді
    # Ліва частина маски (відступає на 20px від краю міді)
    frags.append(rect(rx_col + 40, mask_y, 80, mask_h, fill=MASK_FILL, stroke=MASK, sw=1.2, rx=1))
    # Права частина маски
    frags.append(rect(rx_col + 300, mask_y, 80, mask_h, fill=MASK_FILL, stroke=MASK, sw=1.2, rx=1))

    # Зазори маски (clearance)
    frags.append(text(rx_col + 130, mask_y + 11, "Зазор", size=9, color=MUTED, italic=True))
    frags.append(text(rx_col + 290, mask_y + 11, "Зазор", size=9, color=MUTED, italic=True))

    # Паяльна кулька BGA (обтікає і верх, і бічні стінки мідного п'ятака)
    nsmd_ball_path = (
        f'M {rx_col + 150} {bga_sub_y + 24} '
        f'C {rx_col + 80} 180, {rx_col + 80} 275, {nsmd_pad_x - 3} {pcb_y - 2} '
        f'L {nsmd_pad_x + nsmd_pad_w + 3} {pcb_y - 2} '
        f'C {rx_col + 340} 275, {rx_col + 340} 180, {rx_col + 270} {bga_sub_y + 24} Z'
    )
    frags.append(f'<path d="{nsmd_ball_path}" fill="{SOLDER_FILL}" stroke="{SOLDER}" stroke-width="1.8"/>')
    frags.append(text(rx_col + 210, 230, "Припій (SAC305)", size=11, color=SOLDER, bold=True))

    # Стрілочки рівномірного розподілу напружень
    frags.append(circle(nsmd_pad_x - 3, pcb_y - 4, 3.5, fill="#dcfce7", stroke=FIELD, sw=1.5))
    frags.append(circle(nsmd_pad_x + nsmd_pad_w + 3, pcb_y - 4, 3.5, fill="#dcfce7", stroke=FIELD, sw=1.5))
    frags.append(text(rx_col + 210, 310, "Рівномірний розподіл напруг (бічне охоплення)", size=10, color=FIELD, bold=True))

    # Характеристики NSMD (список у рамці)
    frags.append(rect(rx_col + 15, 380, col_w - 30, 135, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(rx_col + 25, 400, "• Робочий діаметр площадки = діаметр міді", size=11, color=INK, anchor="start"))
    frags.append(text(rx_col + 25, 422, "• Змочування: верх і бічні стінки п'ятака (3D)", size=11, color=INK, anchor="start"))
    frags.append(text(rx_col + 25, 444, "• Висока втомна міцність при термоциклюванні", size=11, color=FIELD, anchor="start"))
    frags.append(text(rx_col + 25, 466, "• Ширший канал для виходу доріжок (Escape Routing)", size=11, color=FIELD, anchor="start"))
    frags.append(text(rx_col + 25, 488, "• Ризик викришування (Pad Cratering) при згинанні", size=11, color=POS, anchor="start"))

    render(p, w, h, *frags)
    print("Generated:", p)


def fig_head_in_pillow():
    p = os.path.join(OUT, "head-in-pillow-defect-mechanism.svg")
    w, h = 960, 480
    frags = []

    # Тло
    frags.append(rect(10, 10, 940, 460, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=8))

    # Заголовок
    frags.append(text(480, 36, "Механізм утворення дефекту Head-in-Pillow (HiP) при паянні BGA", size=16, color=INK, bold=True))

    # 4 стадії
    stage_w = 215
    stage_gap = 15
    start_x = 25
    st_y = 60
    st_h = 390

    stages_data = [
        {
            "num": "1",
            "title": "Встановлення чіпа",
            "sub": "Нанесення пасти та посадка",
            "temp": "T = 25°C (Кімнатна)",
            "desc": ["Кулька BGA занурена", "в пасту на контактній", "площадці плати.", "Флюс покриває стик."],
            "warpage": False,
            "separated": False,
            "melted": False,
            "hip": False
        },
        {
            "num": "2",
            "title": "Термічне короблення",
            "sub": "Вигин корпусу в зоні Soak",
            "temp": "T = 150–180°C (Прогрів)",
            "desc": ["Нерівномірне КЛТР вигинає", "кути BGA вгору (Warpage).", "Кулька відривається,", "флюс вичерпується."],
            "warpage": True,
            "separated": True,
            "melted": False,
            "hip": False
        },
        {
            "num": "3",
            "title": "Роздільне плавлення",
            "sub": "Окиснення в зоні Reflow",
            "temp": "T = 240°C (Пік оплавлення)",
            "desc": ["Кулька й паста плавляться", "окремо одна від одної.", "На поверхні обох утворюється", "плівка оксидів (SnO/SnO₂)."],
            "warpage": True,
            "separated": True,
            "melted": True,
            "hip": False
        },
        {
            "num": "4",
            "title": "Дефект HiP",
            "sub": "Контакт без злиття (HiP)",
            "temp": "T < 217°C (Охолодження)",
            "desc": ["Чіп випрямляється.", "Кулька тисне в пасту,", "але оксидна плівка", "блокує металургійне злиття."],
            "warpage": False,
            "separated": False,
            "melted": True,
            "hip": True
        }
    ]

    for i, st in enumerate(stages_data):
        sx = start_x + i * (stage_w + stage_gap)
        # Рамка стадії
        card_fill = "#fff1f2" if st["hip"] else "#f8fafc"
        card_str = "#f43f5e" if st["hip"] else "#e2e8f0"
        frags.append(rect(sx, st_y, stage_w, st_h, fill=card_fill, stroke=card_str, sw=1.2, rx=6))

        # Номер і назва
        badge_col = POS if st["hip"] else NEG
        frags.append(circle(sx + 24, st_y + 24, 12, fill=badge_col, stroke=badge_col))
        frags.append(text(sx + 24, st_y + 29, st["num"], size=12, color="#ffffff", bold=True))
        frags.append(text(sx + 44, st_y + 22, st["title"], size=12, color=INK, anchor="start", bold=True))
        frags.append(text(sx + 44, st_y + 36, st["sub"], size=9, color=MUTED, anchor="start"))

        # Температурний маркер
        frags.append(rect(sx + 10, st_y + 48, stage_w - 20, 20, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=3))
        frags.append(text(sx + stage_w / 2, st_y + 62, st["temp"], size=10, color=INK, bold=True))

        # ── Графічна частина стадії ──
        center_x = sx + stage_w / 2

        # Плата внизу
        board_y = st_y + 230
        frags.append(rect(sx + 15, board_y, stage_w - 30, 20, fill=DIELECTRIC, stroke=DIELECTRIC_STR, sw=1.0, rx=2))
        frags.append(text(center_x, board_y + 14, "PCB", size=9, color=MUTED, bold=True))

        # Мідний пад на платі
        pad_w, pad_h = 60, 6
        pad_x = center_x - pad_w / 2
        pad_y = board_y - pad_h
        frags.append(rect(pad_x, pad_y, pad_w, pad_h, fill=COPPER_FILL, stroke=COPPER, sw=1.0, rx=1))

        # Підкладка чіпа вгорі (вигин при warpage)
        if st["warpage"]:
            # Вигнута підкладка BGA (кут піднято)
            sub_path = f'M {sx + 15} {st_y + 98} Q {center_x} {st_y + 106} {sx + stage_w - 15} {st_y + 90} L {sx + stage_w - 15} {st_y + 104} Q {center_x} {st_y + 120} {sx + 15} {st_y + 112} Z'
            frags.append(f'<path d="{sub_path}" fill="{SUBSTRATE}" stroke="{SUBSTRATE_STR}" stroke-width="1.2"/>')
            bga_pad_y = st_y + 108
            ball_y = st_y + 140
        else:
            # Рівна підкладка
            sub_y = st_y + 110
            frags.append(rect(sx + 15, sub_y, stage_w - 30, 14, fill=SUBSTRATE, stroke=SUBSTRATE_STR, sw=1.2, rx=2))
            bga_pad_y = sub_y + 14
            ball_y = st_y + 175 if not st["hip"] else st_y + 182

        frags.append(text(center_x, st_y + 102 if st["warpage"] else st_y + 121, "BGA Підкладка", size=9, color="#92400e", bold=True))
        # Верхній мідний пад BGA
        frags.append(rect(center_x - 25, bga_pad_y, 50, 4, fill=COPPER_FILL, stroke=COPPER, sw=1.0, rx=1))

        # Кулька й паста залежно від стадії
        if i == 0:
            # Стадія 1: Кулька в пасті
            frags.append(circle(center_x, ball_y, 25, fill=SOLDER_FILL, stroke=SOLDER, sw=1.5))
            # Трафаретний відбиток пасти на платі
            frags.append(rect(pad_x + 5, pad_y - 12, 50, 12, fill=PASTE_FILL, stroke=SOLDER, sw=1.2, rx=2))
            frags.append(text(center_x, pad_y - 3, "Паста", size=9, color="#ffffff", bold=True))
        elif i == 1:
            # Стадія 2: Відрив через вигин
            frags.append(circle(center_x, ball_y, 25, fill=SOLDER_FILL, stroke=SOLDER, sw=1.5))
            # Паста висихає на платі, флюс кипить
            frags.append(rect(pad_x + 8, pad_y - 8, 44, 8, fill="#a8a29e", stroke="#78716c", sw=1.0, rx=2))
            # Окиснення / дим флюсу
            frags.append(text(center_x, 195, "↑ Зазор (відрив) ↑", size=9, color=POS, bold=True))
            frags.append(circle(center_x, ball_y + 24, 2, fill=OXIDE_COL, stroke=OXIDE_COL))
        elif i == 2:
            # Стадія 3: Обидва розплавлені, але розділені оксидною кіркою
            # Розплавлена крапля кульки
            frags.append(circle(center_x, ball_y, 24, fill="#94a3b8", stroke=OXIDE_COL, sw=2.0))
            frags.append(text(center_x, ball_y + 3, "Розплав", size=9, color=INK))
            # Розплавлений горбик пасти на платі
            frags.append(f'<path d="M {pad_x + 5} {pad_y} Q {center_x} {pad_y - 16} {pad_x + 55} {pad_y} Z" fill="#94a3b8" stroke="{OXIDE_COL}" stroke-width="2.0"/>')
            frags.append(text(center_x, 195, "Оксидні плівки (SnO)", size=9, color=OXIDE_COL, bold=True))
        elif i == 3:
            # Стадія 4: Кулька сідає у впадину пасти без змочування
            # Паста у формі «подушки» (pillow)
            pillow_path = f'M {pad_x + 2} {pad_y} C {pad_x + 5} {pad_y - 18}, {pad_x + 55} {pad_y - 18}, {pad_x + 58} {pad_y} Z'
            frags.append(f'<path d="{pillow_path}" fill="{SOLDER_FILL}" stroke="{SOLDER}" stroke-width="1.5"/>')
            # Кулька (голова), що втоплена в подушку
            frags.append(circle(center_x, pad_y - 18, 23, fill=SOLDER_FILL, stroke=SOLDER, sw=1.5))
            # Незмочена межа розділу між кулькою та пастою (червона дуга)
            interface_arc = f'M {center_x - 16} {pad_y - 6} Q {center_x} {pad_y - 2} {center_x + 16} {pad_y - 6}'
            frags.append(f'<path d="{interface_arc}" fill="none" stroke="{POS}" stroke-width="2.5" stroke-dasharray="3,2"/>')
            frags.append(text(center_x, pad_y - 8, "Дефект HiP", size=9, color=POS, bold=True))

        # Текстовий опис кроку
        desc_box_y = st_y + 265
        frags.append(rect(sx + 8, desc_box_y, stage_w - 16, 110, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
        for line_idx, line_text in enumerate(st["desc"]):
            frags.append(text(sx + 14, desc_box_y + 20 + line_idx * 20, line_text, size=10, color=INK, anchor="start"))

    render(p, w, h, *frags)
    print("Generated:", p)


if __name__ == "__main__":
    fig_smd_vs_nsmd()
    fig_head_in_pillow()
