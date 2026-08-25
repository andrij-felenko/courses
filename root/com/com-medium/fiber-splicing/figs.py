# -*- coding: utf-8 -*-
import sys
import os

# 4 levels up to courses root, then scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def make_alignment_defects():
    W, H = 840, 360
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    f.append(text(W / 2, 28, "Геометричні дефекти стикування волокон", 17, INK, "middle", bold=True))
    
    panels = [
        ("Радіальне зміщення (d)", 30, 60, 245, 260),
        ("Кутовий незбіг (θ)", 295, 60, 245, 260),
        ("Осьовий зазор (s)", 560, 60, 245, 260)
    ]
    
    for title, px, py, pw, ph in panels:
        f.append(rect(px, py, pw, ph, fill="#f8fafc", stroke="#cbd5e1", rx=8))
        f.append(text(px + pw/2, py + 24, title, 14, INK, "middle", bold=True))
    
    # Panel 1: Radial offset
    f.append(rect(50, 140, 95, 50, fill="#e2e8f0", stroke="#64748b", sw=1.5))
    f.append(rect(50, 158, 95, 14, fill="#bae6fd", stroke="#0284c7", sw=1.5))
    f.append(line(50, 165, 145, 165, color="#0369a1", sw=1, dash="4,3"))
    
    f.append(rect(145, 128, 95, 50, fill="#e2e8f0", stroke="#64748b", sw=1.5))
    f.append(rect(145, 146, 95, 14, fill="#bae6fd", stroke="#0284c7", sw=1.5))
    f.append(line(145, 153, 240, 153, color="#0369a1", sw=1, dash="4,3"))
    
    f.append(line(145, 153, 145, 165, color=POS, sw=2))
    f.append(text(158, 163, "d", 13, POS, "start", bold=True))
    f.append(mtext(152, 240, ["Витік світла в оболонку", "через неузгодження ядра"], 12, color="#475569"))

    # Panel 2: Angular tilt
    f.append(rect(315, 140, 95, 50, fill="#e2e8f0", stroke="#64748b", sw=1.5))
    f.append(rect(315, 158, 95, 14, fill="#bae6fd", stroke="#0284c7", sw=1.5))
    
    f.append('<g transform="translate(410, 165) rotate(12) translate(-410, -165)">')
    f.append(rect(410, 140, 95, 50, fill="#e2e8f0", stroke="#64748b", sw=1.5))
    f.append(rect(410, 158, 95, 14, fill="#bae6fd", stroke="#0284c7", sw=1.5))
    f.append('</g>')
    
    f.append(text(428, 158, "θ", 13, POS, "middle", bold=True))
    f.append(mtext(417, 240, ["Заломлення променя за", "критичний кут θ_c"], 12, color="#475569"))

    # Panel 3: Axial gap
    f.append(rect(580, 140, 80, 50, fill="#e2e8f0", stroke="#64748b", sw=1.5))
    f.append(rect(580, 158, 80, 14, fill="#bae6fd", stroke="#0284c7", sw=1.5))
    
    f.append(rect(685, 140, 80, 50, fill="#e2e8f0", stroke="#64748b", sw=1.5))
    f.append(rect(685, 158, 80, 14, fill="#bae6fd", stroke="#0284c7", sw=1.5))
    
    f.append(arrow(660, 165, 685, 165, color=POS, sw=1.5))
    f.append(arrow(685, 165, 660, 165, color=POS, sw=1.5))
    f.append(text(672, 153, "s", 13, POS, "middle", bold=True))
    
    f.append('<polygon points="660,158 685,150 685,178 660,172" fill="#fef08a" opacity="0.6" stroke="#eab308"/>')
    f.append(mtext(682, 240, ["Розширення пучка та", "відбиття Френеля"], 12, color="#475569"))
    
    render(os.path.join(IMG, 'alignment-defects.svg'), W, H, *f)

def make_fusion_process():
    W, H = 840, 320
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    f.append(text(W / 2, 28, "Етапи дугового зварювання оптоволокна (Fusion Splicing)", 17, INK, "middle", bold=True))
    
    stages = [
        ("1. Сколювання", "Кут торця < 0.5°", 25),
        ("2. Pre-fuse & PAS", "Очищення + V-канавки", 225),
        ("3. Дугове плавлення", "Температура 1800-2000 °C", 425),
        ("4. Монолітний шов", "Втрати < 0.02 дБ + КДЗС", 625)
    ]
    
    sw_box = 185
    sh_box = 230
    
    for i, (title, sub, px) in enumerate(stages):
        f.append(rect(px, 60, sw_box, sh_box, fill="#f8fafc", stroke="#cbd5e1", rx=8))
        f.append(text(px + sw_box/2, 85, title, 13, INK, "middle", bold=True))
        f.append(text(px + sw_box/2, 105, sub, 11, MUTED, "middle"))
        
        if i < 3:
            f.append(arrow(px + sw_box + 2, 160, px + sw_box + 13, 160, color="#94a3b8", sw=2))

    # Stage 1 Details
    f.append(rect(40, 145, 60, 30, fill="#e2e8f0", stroke="#64748b"))
    f.append(rect(40, 156, 60, 8, fill="#0284c7", stroke="none"))
    f.append(rect(115, 145, 60, 30, fill="#e2e8f0", stroke="#64748b"))
    f.append(rect(115, 156, 60, 8, fill="#0284c7", stroke="none"))
    f.append(line(103, 135, 103, 185, color=POS, sw=1.5, dash="2,2"))
    f.append(text(117, 215, "Ідеальний зріз", 11, MUTED, "middle"))

    # Stage 2 Details
    f.append(rect(240, 145, 60, 30, fill="#e2e8f0", stroke="#64748b"))
    f.append(rect(240, 156, 60, 8, fill="#0284c7", stroke="none"))
    f.append(rect(335, 145, 60, 30, fill="#e2e8f0", stroke="#64748b"))
    f.append(rect(335, 156, 60, 8, fill="#0284c7", stroke="none"))
    f.append(circle(317, 135, 6, fill="#f59e0b", stroke="#b45309"))
    f.append(circle(317, 185, 6, fill="#f59e0b", stroke="#b45309"))
    f.append(line(317, 141, 317, 179, color="#eab308", sw=1.5, dash="2,2"))
    f.append(text(317, 215, "Дуга низького струму", 11, MUTED, "middle"))

    # Stage 3 Details
    f.append(rect(440, 145, 65, 30, fill="#e2e8f0", stroke="#64748b"))
    f.append(rect(440, 156, 65, 8, fill="#0284c7", stroke="none"))
    f.append(rect(510, 145, 65, 30, fill="#e2e8f0", stroke="#64748b"))
    f.append(rect(510, 156, 65, 8, fill="#0284c7", stroke="none"))
    f.append(circle(507, 160, 14, fill="#ef4444", stroke="#dc2626"))
    f.append(circle(507, 160, 7, fill="#fef08a", stroke="none"))
    f.append(text(517, 215, "Поверхневий натяг", 11, MUTED, "middle"))

    # Stage 4 Details: Avoid nested rects by using paths/polygons for KDZS sleeve overlay
    f.append(rect(640, 145, 150, 30, fill="#e2e8f0", stroke="#64748b"))
    f.append(rect(640, 156, 150, 8, fill="#0284c7", stroke="none"))
    # KDZS Sleeve drawn as grouped lines and translucent path instead of overlapping rect
    f.append('<path d="M 670,138 L 760,138 L 760,182 L 670,182 Z" fill="#38bdf8" opacity="0.4" stroke="#0284c7" stroke-width="1.5"/>')
    f.append(line(675, 174, 755, 174, color="#475569", sw=3))
    f.append(text(717, 215, "Гільза КДЗС + пруток", 11, MUTED, "middle"))

    render(os.path.join(IMG, 'fusion-process.svg'), W, H, *f)

def make_connector_polishing():
    W, H = 840, 340
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    f.append(text(W / 2, 28, "Типи полірування торців оптичних конекторів", 17, INK, "middle", bold=True))
    
    types = [
        ("PC / Flat (Physical Contact)", 30, 60, 245, 240, "-35...-40 дБ", "#94a3b8"),
        ("UPC (Ultra Physical Contact)", 295, 60, 245, 240, "-50...-55 дБ", "#2563eb"),
        ("APC (Angled Physical Contact 8°)", 560, 60, 245, 240, "< -60 дБ", "#16a34a")
    ]
    
    for title, px, py, pw, ph, rl, color_hdr in types:
        f.append(rect(px, py, pw, ph, fill="#f8fafc", stroke="#cbd5e1", rx=8))
        f.append(text(px + pw/2, py + 22, title, 12, INK, "middle", bold=True))
        f.append(rect(px + pw/2 - 50, py + 34, 100, 20, fill=color_hdr, stroke="none", rx=4))
        f.append(text(px + pw/2, py + 48, f"RL: {rl}", 11, "#ffffff", "middle", bold=True))

    # 1. PC: Flat ferrule joint
    f.append(rect(50, 140, 95, 60, fill="#f1f5f9", stroke="#64748b"))
    f.append(rect(50, 164, 95, 12, fill="#38bdf8", stroke="#0284c7"))
    f.append(rect(145, 140, 95, 60, fill="#f1f5f9", stroke="#64748b"))
    f.append(rect(145, 164, 95, 12, fill="#38bdf8", stroke="#0284c7"))
    f.append(arrow(145, 170, 95, 170, color=POS, sw=2))
    f.append(mtext(152, 245, ["Пряме відбиття Френеля", "назад у ядро джерела"], 12, color="#475569"))

    # 2. UPC: Curved convex spherical contact
    f.append(rect(315, 140, 85, 60, fill="#f1f5f9", stroke="#64748b"))
    f.append(rect(315, 164, 85, 12, fill="#38bdf8", stroke="#0284c7"))
    f.append('<path d="M 400,140 A 40,40 0 0 1 400,200 Z" fill="#f1f5f9" stroke="#64748b"/>')
    f.append('<path d="M 415,140 A 40,40 0 0 0 415,200 Z" fill="#f1f5f9" stroke="#64748b"/>')
    f.append(rect(415, 140, 85, 60, fill="#f1f5f9", stroke="#64748b"))
    f.append(rect(415, 164, 85, 12, fill="#38bdf8", stroke="#0284c7"))
    f.append(arrow(405, 170, 365, 170, color=POS, sw=1.5))
    f.append(mtext(417, 245, ["Мікроскопічний зазор", "щез, менше відбиття"], 12, color="#475569"))

    # 3. APC: 8 degree angle cut
    f.append('<g transform="translate(680, 170) rotate(-8) translate(-680, -170)">')
    f.append(rect(580, 140, 99, 60, fill="#e2e8f0", stroke="#64748b"))
    f.append(rect(580, 164, 99, 12, fill="#38bdf8", stroke="#0284c7"))
    f.append(rect(681, 140, 99, 60, fill="#e2e8f0", stroke="#64748b"))
    f.append(rect(681, 164, 99, 12, fill="#38bdf8", stroke="#0284c7"))
    f.append('</g>')
    f.append(arrow(680, 170, 640, 148, color=POS, sw=2))
    f.append(mtext(682, 245, ["Відбитий промінь іде в", "оболонку під кутом > θ_c"], 12, color="#475569"))

    render(os.path.join(IMG, 'connector-polishing.svg'), W, H, *f)

def main():
    make_alignment_defects()
    print("Generated img/alignment-defects.svg")
    make_fusion_process()
    print("Generated img/fusion-process.svg")
    make_connector_polishing()
    print("Generated img/connector-polishing.svg")

if __name__ == '__main__':
    main()
