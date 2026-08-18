# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import (
    text, mtext, rect, line, arrow, circle, fit_font, text_width,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

def path_d(d, color=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{d_attr}/>'

def polygon(pts, fill=FILL, stroke=LINE, sw=1.5):
    pts_str = " ".join([f"{x:.1f},{y:.1f}" for x, y in pts])
    return f'<polygon points="{pts_str}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def build_omr_lorentz():
    """Фігура 1: Звичайний магнітоопір — викривлення траєкторії носіїв силою Лоренца."""
    w, h = 760, 320
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    out.append(f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{LINE}"/></marker></defs>')
    out.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    # Ліва панель: B = 0
    out.append(rect(20, 20, 350, 280, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    out.append(text(195, 45, "Без магнітного поля (B = 0)", size=15, bold=True, color=INK))
    
    # Провідний канал B=0
    out.append(rect(40, 70, 310, 160, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    # Вузли ґратки
    for rx_pos in [90, 165, 240, 315]:
        for ry_pos in [110, 150, 190]:
            out.append(circle(rx_pos, ry_pos, 6, fill="#e2e8f0", stroke=MUTED, sw=1))
            out.append(text(rx_pos, ry_pos + 3.5, "+", size=10, color=MUTED, bold=True))

    # Пряма траєкторія електрона
    out.append(path_d("M 50 150 L 90 110 L 165 150 L 240 110 L 315 150 L 340 150", color=NEG, sw=2.2))
    out.append(circle(50, 150, 5, fill=NEG, stroke="none"))
    out.append(arrow(315, 150, 340, 150, color=NEG, sw=2.2))
    out.append(text(195, 250, "Траєкторія пряма між зіткненнями", size=13, color=INK))
    out.append(text(195, 275, "Середній вільний пробіг максимальний", size=12, color=MUTED, italic=True))

    # Права панель: B > 0
    out.append(rect(390, 20, 350, 280, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    out.append(text(565, 45, "У магнітному полі (B > 0)", size=15, bold=True, color=INK))
    
    # Провідний канал B>0
    out.append(rect(410, 70, 310, 160, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    # Вузли ґратки
    for rx_pos in [460, 535, 610, 685]:
        for ry_pos in [110, 150, 190]:
            out.append(circle(rx_pos, ry_pos, 6, fill="#e2e8f0", stroke=MUTED, sw=1))
            out.append(text(rx_pos, ry_pos + 3.5, "+", size=10, color=MUTED, bold=True))

    # Викривлена траєкторія електрона
    curve_d = "M 420 150 Q 440 110 460 110 Q 480 170 510 160 Q 535 120 560 150 Q 585 190 610 150 Q 640 120 670 140 L 710 140"
    out.append(path_d(curve_d, color=POS, sw=2.2))
    out.append(circle(420, 150, 5, fill=NEG, stroke="none"))
    out.append(arrow(670, 140, 710, 140, color=POS, sw=2.2))

    # Символ магнітного поля B
    out.append(circle(690, 90, 10, fill="#e8f5e9", stroke=FIELD, sw=1.5))
    out.append(text(690, 94, "⊙", size=14, color=FIELD, bold=True))
    out.append(text(665, 93, "B", size=13, color=FIELD, bold=True))

    out.append(text(565, 250, "Сила Лоренца викривляє траєкторію", size=13, color=INK))
    out.append(text(565, 275, "Більше зіткнень → вищий опір R(B)", size=12, color=POS, bold=True))

    out.append("</svg>")
    return "\n".join(out)

def build_amr_barber_pole():
    """Фігура 2: Анізотропний магнітоопір (AMR) та лінеаризаційні смуги Барбера."""
    w, h = 760, 340
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    out.append(f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{LINE}"/></marker></defs>')
    out.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    # Ліва частина: Графік залежності R від кута theta
    out.append(rect(20, 20, 350, 300, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    out.append(text(195, 45, "Залежність опору R від кута θ", size=15, bold=True, color=INK))

    # Осі графіка
    out.append(arrow(60, 250, 340, 250, color=LINE, sw=1.5))
    out.append(arrow(60, 250, 60, 70, color=LINE, sw=1.5))
    out.append(text(345, 254, "θ", size=14, bold=True, color=INK))
    out.append(text(52, 65, "R", size=14, bold=True, color=INK))

    # Пунктирні рівні R_parallel та R_perp
    out.append(line(60, 90, 320, 90, color=MUTED, sw=1, dash="4,4"))
    out.append(text(45, 94, "R ∥", size=12, color=POS, bold=True))
    out.append(line(60, 210, 320, 210, color=MUTED, sw=1, dash="4,4"))
    out.append(text(45, 214, "R ⊥", size=12, color=NEG, bold=True))

    # Косинусоїдальна крива R(θ)
    curve = "M 60 90 Q 125 90 125 150 Q 125 210 190 210 Q 255 210 255 150 Q 255 90 320 90"
    out.append(path_d(curve, color=POS, sw=2.5))

    # Позначки кутів
    out.append(text(60, 270, "0°", size=12, color=INK))
    out.append(text(125, 270, "45°", size=12, color=FIELD, bold=True))
    out.append(line(125, 245, 125, 255, color=LINE, sw=1.5))
    out.append(line(125, 90, 125, 210, color=FIELD, sw=1, dash="2,2"))
    out.append(circle(125, 150, 4, fill=FIELD, stroke="none"))
    out.append(text(190, 270, "90°", size=12, color=INK))
    out.append(text(320, 270, "180°", size=12, color=INK))

    out.append(text(195, 293, "Найвища лінійність при θ = 45°", size=12, color=FIELD, bold=True))

    # Права частина: Смуги Барбера
    out.append(rect(390, 20, 350, 300, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    out.append(text(565, 45, "Смуги Барбера (Barber Poles)", size=15, bold=True, color=INK))

    out.append(rect(420, 110, 290, 80, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    out.append(text(435, 100, "Пермалой (NiFe), M ➔", size=12, color=INK, bold=True))
    out.append(arrow(430, 150, 700, 150, color=MUTED, sw=1.5))

    for bx in [450, 510, 570, 630]:
        out.append(polygon([(bx, 190), (bx + 30, 110), (bx + 45, 110), (bx + 15, 190)], fill="#f1c40f", stroke="#b7950b", sw=1))

    out.append(arrow(440, 175, 470, 125, color=POS, sw=2))
    out.append(arrow(500, 175, 530, 125, color=POS, sw=2))
    out.append(arrow(560, 175, 590, 125, color=POS, sw=2))
    out.append(text(565, 225, "Золоті смуги повертають струм I під 45°", size=13, color=INK))
    out.append(text(565, 250, "до намагніченості M", size=13, color=INK))
    out.append(text(565, 280, "Забезпечує лінійну характеристику давача", size=12, color=FIELD, bold=True))

    out.append("</svg>")
    return "\n".join(out)

def build_gmr_spin_valve():
    """Фігура 3: Гігантський магнітоопір (GMR) — спіновий вентиль."""
    w, h = 760, 340
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    out.append(f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{LINE}"/></marker></defs>')
    out.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    # Ліва панель: Паралельний стан
    out.append(rect(20, 20, 350, 300, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    out.append(text(195, 45, "Паралельний стан (P): Низький R", size=15, bold=True, color=FIELD))

    out.append(rect(50, 70, 290, 50, fill="#bbdefb", stroke=NEG, sw=1.5, rx=4))
    out.append(arrow(80, 95, 140, 95, color=NEG, sw=3))
    out.append(text(230, 99, "Феромагнетик 1 (M ↑)", size=12, bold=True, color=INK))

    out.append(rect(50, 125, 290, 30, fill="#fff9c4", stroke="#fbc02d", sw=1.5, rx=2))
    out.append(text(195, 144, "Немагнітний прошарок (Cu, 2 нм)", size=11, color=MUTED))

    out.append(rect(50, 160, 290, 50, fill="#bbdefb", stroke=NEG, sw=1.5, rx=4))
    out.append(arrow(80, 185, 140, 185, color=NEG, sw=3))
    out.append(text(230, 189, "Феромагнетик 2 (M ↑)", size=12, bold=True, color=INK))

    out.append(line(80, 60, 80, 220, color=FIELD, sw=2.5))
    out.append(arrow(80, 210, 80, 230, color=FIELD, sw=2.5))
    out.append(text(80, 245, "e⁻ (↑) проходить вільно", size=11, color=FIELD, bold=True))

    out.append(text(195, 275, "Один спіновий канал зашунтовано", size=12, color=INK))
    out.append(text(195, 295, "Опір R_P — МІНІМАЛЬНИЙ", size=13, color=FIELD, bold=True))

    # Права панель: Антипаралельний стан
    out.append(rect(390, 20, 350, 300, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    out.append(text(565, 45, "Антипаралельний (AP): Високий R", size=15, bold=True, color=POS))

    out.append(rect(420, 70, 290, 50, fill="#bbdefb", stroke=NEG, sw=1.5, rx=4))
    out.append(arrow(450, 95, 510, 95, color=NEG, sw=3))
    out.append(text(600, 99, "Феромагнетик 1 (M ↑)", size=12, bold=True, color=INK))

    out.append(rect(420, 125, 290, 30, fill="#fff9c4", stroke="#fbc02d", sw=1.5, rx=2))
    out.append(text(565, 144, "Немагнітний прошарок (Cu, 2 нм)", size=11, color=MUTED))

    out.append(rect(420, 160, 290, 50, fill="#ffcdd2", stroke=POS, sw=1.5, rx=4))
    out.append(arrow(510, 185, 450, 185, color=POS, sw=3))
    out.append(text(600, 189, "Феромагнетик 2 (M ↓)", size=12, bold=True, color=INK))

    out.append(line(450, 60, 450, 135, color=POS, sw=2))
    out.append(path_d("M 450 135 L 460 145 L 440 155 L 455 165 L 445 175", color=POS, sw=2))
    out.append(text(450, 245, "Сильне розсіювання e⁻ на межі", size=11, color=POS, bold=True))

    out.append(text(565, 275, "Обидва спінові канали розсіюються", size=12, color=INK))
    out.append(text(565, 295, "Опір R_AP — МАКСИМАЛЬНИЙ", size=13, color=POS, bold=True))

    out.append("</svg>")
    return "\n".join(out)

def build_tmr_junction():
    """Фігура 4: Тунельний магнітоопір (TMR) — тунелювання через бар'єр."""
    w, h = 760, 320
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    out.append(f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{LINE}"/></marker></defs>')
    out.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    out.append(rect(20, 20, 720, 280, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    out.append(text(380, 45, "Магнітний тунельний перехід (MTJ): Спін-поляризоване тунелювання", size=15, bold=True, color=INK))

    out.append(rect(60, 70, 220, 170, fill="#bbdefb", stroke=NEG, sw=1.5, rx=6))
    out.append(text(170, 95, "Феромагнітний електрод 1", size=13, bold=True, color=INK))
    out.append(arrow(110, 120, 170, 120, color=NEG, sw=2.5))
    out.append(text(210, 124, "M1 (↑)", size=12, color=NEG, bold=True))
    out.append(text(170, 160, "Густина станів N(E):", size=12, color=INK))
    out.append(text(170, 185, "Спін ↑ : Багато станів (N_up)", size=11, color=FIELD, bold=True))
    out.append(text(170, 210, "Спін ↓ : Мало станів (N_dn)", size=11, color=MUTED))

    out.append(rect(300, 70, 140, 170, fill="#e8eaf6", stroke="#3f51b5", sw=2, rx=4))
    out.append(text(370, 105, "Тонкий діелектрик", size=12, bold=True, color="#1a237e"))
    out.append(text(370, 125, "(MgO ~ 1 нм)", size=12, bold=True, color="#1a237e"))

    out.append(path_d("M 270 160 Q 300 160 330 175 T 410 190 L 450 190", color=POS, sw=2.5, dash="3,2"))
    out.append(text(370, 215, "Квантове тунелювання", size=11, color=POS, bold=True))

    out.append(rect(460, 70, 220, 170, fill="#ffcdd2", stroke=POS, sw=1.5, rx=6))
    out.append(text(570, 95, "Феромагнітний електрод 2", size=13, bold=True, color=INK))
    out.append(arrow(510, 120, 570, 120, color=POS, sw=2.5))
    out.append(text(610, 124, "M2 (вільний)", size=12, color=POS, bold=True))
    out.append(text(570, 160, "Перекриття спінових станів:", size=12, color=INK))
    out.append(text(570, 185, "P-стан: Великий тунельний струм", size=11, color=FIELD, bold=True))
    out.append(text(570, 210, "AP-стан: Малий тунельний струм", size=11, color=POS, bold=True))

    out.append(text(380, 275, "TMR ratio = (R_AP - R_P) / R_P = 2·P1·P2 / (1 - P1·P2)   [Формула Жюльєра]", size=13, bold=True, color=INK))

    out.append("</svg>")
    return "\n".join(out)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    files = {
        'omr-lorentz.svg': build_omr_lorentz(),
        'amr-barber-pole.svg': build_amr_barber_pole(),
        'gmr-spin-valve.svg': build_gmr_spin_valve(),
        'tmr-junction.svg': build_tmr_junction(),
    }
    
    for filename, content in files.items():
        path = os.path.join(img_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated {filename}")

if __name__ == '__main__':
    main()
