# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Магнітна проникність» (magnetic-permeability)."""
import os
import sys

# Шлях до кореневої теки scripts/ (4 рівні вгору від root/sci/ph-electromagnetism/magnetic-permeability)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_b_h_m_vectors():
    """Фігура 1: Зв'язок векторів B, H та M у вакуумі, парамагнетику та феромагнетику."""
    w, h = 820, 300
    svg = ""

    # Заголовок / тло трьох панелей
    panels = [
        ("Вакуум: відгук відсутній", 140, 40, 240, 230),
        ("Парамагнетик: слабкий відгук", 410, 40, 240, 230),
        ("Феромагнетик: доменне підсилення", 680, 40, 240, 230),
    ]

    for title, cx, y, pw, ph in panels:
        px = cx - pw / 2
        svg += rect(px, y, pw, ph, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8)
        svg += text(cx, y + 25, title, size=13, color=INK, anchor="middle", bold=True)
        svg += line(px + 10, y + 36, px + pw - 10, y + 36, color="#cbd5e1", sw=1)

    # Панель 1: Вакуум
    # Зовнішнє поле H
    svg += arrow(60, 115, 160, 115, color=LINE, sw=2)
    svg += text(110, 105, "H (напруженість)", size=11, color=INK, anchor="middle", bold=True)
    
    svg += text(140, 155, "M = 0  (речовини нема)", size=12, color=MUTED, anchor="middle", italic=True)
    
    # Індукція B = mu0 * H
    svg += arrow(60, 210, 160, 210, color=FIELD, sw=2.5)
    svg += text(110, 200, "B = μ₀ · H", size=12, color=FIELD, anchor="middle", bold=True)
    svg += text(140, 245, "μᵣ = 1.0", size=12, color=INK, anchor="middle", bold=True)

    # Панель 2: Парамагнетик
    # Вхідне поле H
    svg += arrow(330, 105, 430, 105, color=LINE, sw=2)
    svg += text(380, 95, "H (зовнішнє)", size=11, color=INK, anchor="middle", bold=True)

    # Вектор намагніченості M (малий, співнапрямлений)
    svg += arrow(330, 145, 365, 145, color=POS, sw=2)
    svg += text(425, 149, "M (диполі за полем)", size=11, color=POS, anchor="middle", bold=True)

    # Індукція B = mu0 (H + M)
    svg += arrow(330, 210, 445, 210, color=FIELD, sw=2.5)
    svg += text(390, 200, "B = μ₀ · (H + M)", size=12, color=FIELD, anchor="middle", bold=True)
    svg += text(410, 245, "μᵣ = 1 + χ > 1  (χ ≈ 10⁻⁵)", size=12, color=INK, anchor="middle", bold=True)

    # Панель 3: Феромагнетик
    # Вхідне поле H
    svg += arrow(600, 95, 680, 95, color=LINE, sw=2)
    svg += text(640, 85, "H (навіть мале)", size=11, color=INK, anchor="middle", bold=True)

    # Величезний вектор M
    svg += arrow(600, 140, 750, 140, color=POS, sw=3)
    svg += text(680, 130, "M (спільні домени)", size=11, color=POS, anchor="middle", bold=True)

    # Індукція B >> mu0 H
    svg += arrow(600, 205, 770, 205, color=FIELD, sw=3.5)
    svg += text(685, 195, "B ≈ μ₀ · M  (у 10³–10⁵ разів)", size=12, color=FIELD, anchor="middle", bold=True)
    svg += text(680, 245, "μᵣ >> 1  (до 100 000+)", size=12, color=INK, anchor="middle", bold=True)

    render(os.path.join(IMG_DIR, "b-h-m-vectors.svg"), w, h, svg)


def fig_magnetic_classes():
    """Фігура 2: Мікроскопічні механізми діа-, пара- та феромагнетизму."""
    w, h = 860, 320
    svg = ""

    cols = [
        ("Діамагнетизм", 155, 30, 260, 270),
        ("Парамагнетизм", 430, 30, 260, 270),
        ("Феромагнетизм", 705, 30, 260, 270),
    ]

    for title, cx, y, cw, ch in cols:
        px = cx - cw / 2
        svg += rect(px, y, cw, ch, fill="#ffffff", stroke=LINE, sw=1.2, rx=8)
        svg += text(cx, y + 25, title, size=14, color=INK, anchor="middle", bold=True)
        svg += line(px + 10, y + 36, px + cw - 10, y + 36, color="#cbd5e1", sw=1)

    # Стовпчик 1: Діамагнетизм
    # Орбіта з ларморовою прецесією
    svg += circle(155, 120, 35, fill="#f4f6f8", stroke=NEG, sw=1.5)
    svg += circle(155, 120, 6, fill=POS, stroke=POS, sw=1) # ядро
    # Електрон на орбіті
    svg += circle(155, 85, 4, fill=NEG, stroke=NEG, sw=1)
    svg += text(155, 75, "e⁻", size=10, color=NEG, anchor="middle", bold=True)
    # Стрілка індукованого моменту (вниз, проти B)
    svg += arrow(155, 120, 155, 175, color=NEG, sw=2)
    svg += text(205, 155, "Δm (проти B)", size=10, color=NEG, anchor="middle", bold=True)
    # Пояснення
    svg += text(155, 215, "Ларморова прецесія орбіт", size=11, color=INK, anchor="middle", bold=True)
    svg += text(155, 235, "Індукований момент проти поля", size=10, color=MUTED, anchor="middle")
    svg += text(155, 260, "χ < 0,  μᵣ < 1  (не залежить від T)", size=11, color=INK, anchor="middle", bold=True)

    # Стовпчик 2: Парамагнетизм
    # Невпорядковані стрілочки та вирівнювання
    dipoles = [(360, 105, 385, 95), (430, 100, 455, 90), (380, 145, 410, 130), (450, 140, 480, 125)]
    for x1, y1, x2, y2 in dipoles:
        svg += arrow(x1, y1, x2, y2, color=POS, sw=2)
    svg += circle(360, 105, 3, fill=POS, stroke=POS, sw=1)
    svg += circle(430, 100, 3, fill=POS, stroke=POS, sw=1)
    svg += circle(380, 145, 3, fill=POS, stroke=POS, sw=1)
    svg += circle(450, 140, 3, fill=POS, stroke=POS, sw=1)
    
    svg += text(430, 175, "Тепловий рух проти поля H", size=10, color=MUTED, anchor="middle", italic=True)
    svg += text(430, 215, "Власні неспарені спіни", size=11, color=INK, anchor="middle", bold=True)
    svg += text(430, 235, "Орієнтація за зовнішнім полем", size=10, color=MUTED, anchor="middle")
    svg += text(430, 260, "χ > 0,  μᵣ > 1  (Закон Кюрі ~ 1/T)", size=11, color=INK, anchor="middle", bold=True)

    # Стовпчик 3: Феромагнетизм
    # Доменна структура (рамка з прозорою заливкою без другого непрозорого rect)
    svg += '<rect x="635" y="80" width="140" height="90" rx="4" fill="none" stroke="#333333" stroke-width="1.2"/>'
    # Межі доменів
    svg += line(705, 80, 705, 170, color=LINE, sw=1, dash="3,3")
    svg += line(635, 125, 705, 125, color=LINE, sw=1, dash="3,3")
    # Стрілки в доменах
    svg += arrow(650, 105, 690, 105, color=FIELD, sw=2) # домен 1
    svg += arrow(650, 150, 680, 160, color=FIELD, sw=2) # домен 2
    svg += arrow(720, 125, 765, 125, color=FIELD, sw=2.5) # великий домен 3
    
    svg += text(705, 190, "Стінки Блоха зміщуються", size=10, color=FIELD, anchor="middle", bold=True)
    svg += text(705, 215, "Обмінна квантова взаємодія", size=11, color=INK, anchor="middle", bold=True)
    svg += text(705, 235, "Спонтанна намагніченість доменів", size=10, color=MUTED, anchor="middle")
    svg += text(705, 260, "μᵣ >> 1  (гістерезис, точка Кюрі)", size=11, color=INK, anchor="middle", bold=True)

    render(os.path.join(IMG_DIR, "magnetic-classes.svg"), w, h, svg)


def fig_hysteresis_loop():
    """Фігура 3: Графік петлі магнітного гістерезису B(H) з ключовими точками."""
    w, h = 800, 440
    svg = ""

    # Координатна сітка та осі
    ox, oy = 400, 220
    
    # Тло блоку
    svg += rect(30, 20, 740, 400, fill="#ffffff", stroke=LINE, sw=1.2, rx=8)

    # Осі H та B
    svg += arrow(70, oy, 730, oy, color=LINE, sw=1.5)
    svg += text(735, oy + 4, "H", size=14, color=INK, anchor="start", bold=True)
    svg += text(710, oy + 22, "(А/м)", size=11, color=MUTED, anchor="middle")

    svg += arrow(ox, 400, ox, 40, color=LINE, sw=1.5)
    svg += text(ox - 15, 45, "B", size=14, color=INK, anchor="end", bold=True)
    svg += text(ox - 15, 62, "(Тл)", size=11, color=MUTED, anchor="end")

    # Основна крива намагнічування (із центру 0,0 до насичення)
    svg += '<path d="M 400 220 Q 460 215 520 120 T 640 85" fill="none" stroke="#2563eb" stroke-width="2" stroke-dasharray="4,4"/>'
    svg += text(490, 185, "початкова крива", size=10, color="#2563eb", anchor="middle", italic=True)

    # Петля гістерезису (замкнений контур)
    loop_path = (
        "M 640 85 "
        "C 520 88 430 100 400 120 "
        "C 360 145 325 180 310 220 "
        "C 290 280 230 350 160 355 "
        "C 280 352 370 340 400 320 "
        "C 440 295 475 260 490 220 "
        "C 510 160 570 90 640 85 Z"
    )
    # Заливка площі петлі (втрати на гістерезис)
    svg += f'<path d="{loop_path}" fill="#eff6ff" stroke="#dc2626" stroke-width="2.5"/>'

    # Стрілочки напрямку обходу петлі
    svg += arrow(360, 150, 335, 185, color="#dc2626", sw=2)
    svg += arrow(440, 290, 465, 255, color="#dc2626", sw=2)

    # Ключові точки
    # +Bs (насичення)
    svg += circle(640, 85, 4.5, fill="#dc2626", stroke=LINE, sw=1)
    svg += line(640, 85, 640, oy, color=MUTED, sw=1, dash="2,2")
    svg += text(640, oy + 16, "+H_s", size=11, color=INK, anchor="middle", bold=True)
    svg += line(ox, 85, 640, 85, color=MUTED, sw=1, dash="2,2")
    svg += text(ox - 8, 90, "+B_s (насичення)", size=11, color=INK, anchor="end", bold=True)

    # -Bs
    svg += circle(160, 355, 4.5, fill="#dc2626", stroke=LINE, sw=1)
    svg += line(160, 355, 160, oy, color=MUTED, sw=1, dash="2,2")
    svg += text(160, oy - 8, "−H_s", size=11, color=INK, anchor="middle", bold=True)
    svg += line(160, 355, ox, 355, color=MUTED, sw=1, dash="2,2")
    svg += text(ox + 8, 360, "−B_s", size=11, color=INK, anchor="start", bold=True)

    # +Br (залишкова індукція)
    svg += circle(400, 120, 5, fill="#16a34a", stroke=LINE, sw=1)
    svg += text(ox + 12, 125, "B_r (залишкова індукція)", size=12, color="#16a34a", anchor="start", bold=True)

    # -Br
    svg += circle(400, 320, 5, fill="#16a34a", stroke=LINE, sw=1)
    svg += text(ox - 12, 325, "−B_r", size=12, color="#16a34a", anchor="end", bold=True)

    # -Hc (коерцитивна сила)
    svg += circle(310, 220, 5, fill="#7c3aed", stroke=LINE, sw=1)
    svg += text(270, oy - 12, "−H_c (коерцитивна сила)", size=11, color="#7c3aed", anchor="middle", bold=True)

    # +Hc
    svg += circle(490, 220, 5, fill="#7c3aed", stroke=LINE, sw=1)
    svg += text(520, oy + 18, "+H_c", size=12, color="#7c3aed", anchor="middle", bold=True)

    # Пояснення площі
    svg += text(210, 75, "Площа петлі = ∮ H dB", size=12, color="#dc2626", anchor="middle", bold=True)
    svg += text(210, 95, "(втрати енергії на цикл)", size=11, color=MUTED, anchor="middle", italic=True)

    render(os.path.join(IMG_DIR, "hysteresis-loop.svg"), w, h, svg)


def fig_permeability_curves():
    """Фігура 4: Залежність магнітної проникності mu_r та mu_diff від напруженості поля H."""
    w, h = 800, 360
    svg = ""

    # Рамка графіка
    svg += rect(30, 20, 740, 320, fill="#ffffff", stroke=LINE, sw=1.2, rx=8)

    # Осі
    ox, oy = 80, 280
    svg += arrow(ox, oy, 720, oy, color=LINE, sw=1.5)
    svg += text(725, oy + 4, "H (А/м)", size=13, color=INK, anchor="start", bold=True)

    svg += arrow(ox, oy, ox, 40, color=LINE, sw=1.5)
    svg += text(ox - 10, 45, "μᵣ, B", size=13, color=INK, anchor="end", bold=True)

    # 1. Крива індукції B(H) (зелена)
    svg += '<path d="M 80 280 C 130 278 180 260 240 180 C 300 100 420 82 700 80" fill="none" stroke="#16a34a" stroke-width="2.5"/>'
    svg += text(650, 70, "B(H) індукція", size=12, color="#16a34a", anchor="middle", bold=True)

    # 2. Крива відносної статичної проникності mu_r(H) = B / (mu0 * H) (синя)
    svg += '<path d="M 80 230 C 140 228 190 190 230 90 C 260 40 310 130 400 210 C 500 265 600 278 700 279" fill="none" stroke="#2563eb" stroke-width="2.5"/>'
    svg += text(340, 60, "μ_max (максимальна)", size=12, color="#2563eb", anchor="middle", bold=True)

    # Точка mu_i (початкова проникність)
    svg += circle(80, 230, 4.5, fill="#2563eb", stroke=LINE, sw=1)
    svg += text(ox - 8, 234, "μ_i (початкова)", size=11, color="#2563eb", anchor="end", bold=True)

    # Точка mu_max
    svg += circle(235, 75, 5, fill="#2563eb", stroke=LINE, sw=1)
    svg += line(235, 75, 235, oy, color=MUTED, sw=1, dash="2,2")
    svg += text(235, oy + 16, "H(μ_max)", size=11, color=INK, anchor="middle")

    # Зона насичення
    svg += text(620, 260, "μ_диф → 1 при H → ∞", size=11, color=MUTED, anchor="middle", italic=True)

    # Легенда / пояснення праворуч
    svg += text(560, 145, "Три режими проникності:", size=12, color=INK, anchor="middle", bold=True)
    svg += text(560, 165, "1. Слабкі поля: μ_i (пружний рух стінок)", size=11, color=MUTED, anchor="middle")
    svg += text(560, 185, "2. Середні поля: μ_max (необоротні стрибки)", size=11, color=MUTED, anchor="middle")
    svg += text(560, 205, "3. Сильні поля: насичення (μ_диф → μ₀)", size=11, color=MUTED, anchor="middle")

    render(os.path.join(IMG_DIR, "permeability-curves.svg"), w, h, svg)


def fig_soft_hard_magnets():
    """Фігура 5: Порівняння магнітом'яких та магнітотвердих матеріалів."""
    w, h = 820, 320
    svg = ""

    # Ліва панель: Магнітом'які матеріали
    svg += rect(30, 20, 365, 280, fill="#ffffff", stroke=LINE, sw=1.2, rx=8)
    svg += text(212, 45, "Магнітом'які матеріали", size=13, color="#16a34a", anchor="middle", bold=True)
    svg += line(45, 56, 380, 56, color="#cbd5e1", sw=1)

    # Осі для м'якого матеріалу
    sox, soy = 212, 160
    svg += arrow(60, soy, 365, soy, color=MUTED, sw=1.2)
    svg += arrow(sox, 260, sox, 70, color=MUTED, sw=1.2)
    svg += text(365, soy + 12, "H", size=11, color=MUTED, anchor="end")
    svg += text(sox - 8, 75, "B", size=11, color=MUTED, anchor="end")

    # Вузька висока петля (мале Hc, велике Br, величезне mu_r)
    soft_loop = (
        "M 240 85 "
        "C 225 86 215 95 212 100 "
        "C 209 110 205 140 203 160 "
        "C 200 195 190 230 184 235 "
        "C 199 234 209 225 212 220 "
        "C 215 210 219 180 221 160 "
        "C 224 125 234 90 240 85 Z"
    )
    svg += f'<path d="{soft_loop}" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>'
    svg += text(212, 275, "Трансформаторна сталь, ферити, пермалой (H_c < 100 А/м)", size=10, color=INK, anchor="middle")

    # Права панель: Магнітотверді матеріали
    svg += rect(425, 20, 365, 280, fill="#ffffff", stroke=LINE, sw=1.2, rx=8)
    svg += text(607, 45, "Магнітотверді матеріали", size=13, color="#dc2626", anchor="middle", bold=True)
    svg += line(440, 56, 775, 56, color="#cbd5e1", sw=1)

    # Осі для твердого матеріалу
    hox, hoy = 607, 160
    svg += arrow(455, hoy, 760, hoy, color=MUTED, sw=1.2)
    svg += arrow(hox, 260, hox, 70, color=MUTED, sw=1.2)
    svg += text(760, hoy + 12, "H", size=11, color=MUTED, anchor="end")
    svg += text(hox - 8, 75, "B", size=11, color=MUTED, anchor="end")

    # Широка прямокутна петля (величезне Hc, велике Br, велике (BH)max)
    hard_loop = (
        "M 720 95 "
        "C 650 97 618 105 607 115 "
        "C 580 125 515 135 490 160 "
        "C 480 200 482 225 494 225 "
        "C 564 223 596 215 607 205 "
        "C 634 195 699 185 724 160 "
        "C 734 120 732 95 720 95 Z"
    )
    svg += f'<path d="{hard_loop}" fill="#fee2e2" stroke="#dc2626" stroke-width="2"/>'
    svg += text(607, 275, "Постійні магніти: NdFeB, SmCo, Alnico (H_c > 10⁴ А/м)", size=10, color=INK, anchor="middle")

    render(os.path.join(IMG_DIR, "soft-hard-magnets.svg"), w, h, svg)


if __name__ == "__main__":
    fig_b_h_m_vectors()
    fig_magnetic_classes()
    fig_hysteresis_loop()
    fig_permeability_curves()
    fig_soft_hard_magnets()
    print("Всі фігури для magnetic-permeability успішно згенеровано.")
