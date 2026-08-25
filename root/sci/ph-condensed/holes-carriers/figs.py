#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
figs.py — Генерація SVG-фігур для теми "Дірки як носії заряду" (holes-carriers)
"""

import os

def ensure_img_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_fig1_valence_band_hole(filepath):
    """Фігура 1: Зонна діаграма валентної зони з незаповненим станом (діркою)."""
    svg = []
    svg.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 400" width="650" height="400">')
    svg.append('  <rect width="650" height="400" fill="#ffffff" />')
    
    svg.append('  <line x1="80" y1="360" x2="570" y2="360" stroke="#333333" stroke-width="2" />')
    svg.append('  <polyline points="560,355 570,360 560,365" fill="none" stroke="#333333" stroke-width="2" />')
    svg.append('  <text x="578" y="364" font-family="sans-serif" font-size="14" fill="#333333">k</text>')
    
    svg.append('  <line x1="325" y1="380" x2="325" y2="30" stroke="#333333" stroke-width="2" />')
    svg.append('  <polyline points="320,40 325,30 330,40" fill="none" stroke="#333333" stroke-width="2" />')
    svg.append('  <text x="338" y="35" font-family="sans-serif" font-size="14" fill="#333333">E</text>')
    
    pts_cb = []
    for x in range(125, 526, 10):
        y = 110 - 0.0016 * ((x - 325) ** 2)
        pts_cb.append(f"{x},{y:.1f}")
    svg.append(f'  <path d="M ' + ' L '.join(pts_cb) + '" fill="none" stroke="#0055aa" stroke-width="3" />')
    svg.append('  <text x="435" y="65" font-family="sans-serif" font-size="14" font-weight="bold" fill="#0055aa">Зона провідності E_c(k)</text>')
    
    svg.append('  <line x1="120" y1="170" x2="530" y2="170" stroke="#888888" stroke-dasharray="4,4" stroke-width="1.5" />')
    svg.append('  <line x1="120" y1="210" x2="530" y2="210" stroke="#888888" stroke-dasharray="4,4" stroke-width="1.5" />')
    svg.append('  <text x="140" y="194" font-family="sans-serif" font-size="13" font-style="italic" fill="#666666">Заборонена зона E_g</text>')
    
    pts_vb = []
    for x in range(125, 526, 10):
        y = 210 + 0.0016 * ((x - 325) ** 2)
        pts_vb.append(f"{x},{y:.1f}")
    svg.append(f'  <path d="M ' + ' L '.join(pts_vb) + '" fill="none" stroke="#cc0000" stroke-width="3" />')
    svg.append('  <text x="435" y="325" font-family="sans-serif" font-size="14" font-weight="bold" fill="#cc0000">Валентна зона E_v(k)</text>')
    
    for x in range(155, 500, 26):
        if x == 377:
            continue
        y = 210 + 0.0016 * ((x - 325) ** 2)
        svg.append(f'  <circle cx="{x}" cy="{y:.1f}" r="7" fill="#0055aa" stroke="#002266" stroke-width="1" />')
    
    hx = 377
    hy = 210 + 0.0016 * ((hx - 325) ** 2)
    svg.append(f'  <circle cx="{hx}" cy="{hy:.1f}" r="9" fill="#ffffff" stroke="#cc0000" stroke-width="2.5" />')
    svg.append(f'  <text x="{hx-4}" y="{hy+4:.1f}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#cc0000">+</text>')
    
    svg.append(f'  <line x1="{hx+15}" y1="{hy-15}" x2="{hx+65}" y2="{hy-40}" stroke="#cc0000" stroke-width="1.5" />')
    svg.append(f'  <text x="{hx+70}" y="{hy-45}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#cc0000">Дірка (k_h = -k_e, q = +e)</text>')
    svg.append(f'  <text x="{hx+70}" y="{hy-27}" font-family="sans-serif" font-size="12" fill="#555555">Ефективна маса m_h* &gt; 0</text>')
    
    svg.append('  <circle cx="325" cy="210" r="3" fill="#333333" />')
    svg.append('  <text x="290" y="200" font-family="sans-serif" font-size="12" fill="#333333">k = 0 (точка Г)</text>')
    
    svg.append('</svg>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))

def create_fig2_hole_motion(filepath):
    """Фігура 2: Естафетний механізм руху дірки в кристалічній ґратці кремнію."""
    svg = []
    svg.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 360" width="650" height="360">')
    svg.append('  <rect width="650" height="360" fill="#ffffff" />')
    
    svg.append('  <line x1="100" y1="40" x2="550" y2="40" stroke="#008800" stroke-width="2.5" />')
    svg.append('  <polyline points="540,35 550,40 540,45" fill="none" stroke="#008800" stroke-width="2.5" />')
    svg.append('  <text x="240" y="28" font-family="sans-serif" font-size="13" font-weight="bold" fill="#008800">Зовнішнє поле E_ext &gt;&gt;</text>')
    
    steps = [
        ("Крок 1: Вакансія", 40, 110, 1),
        ("Крок 2: Перескок e-", 240, 110, 2),
        ("Крок 3: Рух дірки", 440, 110, 3)
    ]
    
    for title, start_x, start_y, step_num in steps:
        svg.append(f'  <text x="{start_x+10}" y="{start_y-22}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#333333">{title}</text>')
        svg.append(f'  <rect x="{start_x}" y="{start_y-10}" width="165" height="180" fill="#fafafa" stroke="#dddddd" stroke-width="1" rx="5" />')
        
        r = 16
        c1 = (start_x + 40, start_y + 35)
        c2 = (start_x + 125, start_y + 35)
        c3 = (start_x + 40, start_y + 120)
        c4 = (start_x + 125, start_y + 120)
        
        if step_num == 1:
            hy = start_y + 77
            svg.append(f'  <line x1="{c1[0]}" y1="{c1[1]+r}" x2="{c1[0]}" y2="{hy-10}" stroke="#bbbbbb" stroke-width="2" />')
            svg.append(f'  <line x1="{c1[0]}" y1="{hy+10}" x2="{c3[0]}" y2="{c3[1]-r}" stroke="#bbbbbb" stroke-width="2" />')
            svg.append(f'  <line x1="{c2[0]}" y1="{c2[1]+r}" x2="{c4[0]}" y2="{c4[1]-r}" stroke="#bbbbbb" stroke-width="2" />')
            svg.append(f'  <line x1="{c1[0]+r}" y1="{c1[1]}" x2="{c2[0]-r}" y2="{c2[1]}" stroke="#bbbbbb" stroke-width="2" />')
            svg.append(f'  <line x1="{c3[0]+r}" y1="{c3[1]}" x2="{c4[0]-r}" y2="{c4[1]}" stroke="#bbbbbb" stroke-width="2" />')
            hole_pos = (c1[0], hy)
        elif step_num == 2:
            hx = start_x + 82
            svg.append(f'  <line x1="{c1[0]+r}" y1="{c1[1]}" x2="{hx-10}" y2="{c1[1]}" stroke="#bbbbbb" stroke-width="2" />')
            svg.append(f'  <line x1="{hx+10}" y1="{c1[1]}" x2="{c2[0]-r}" y2="{c2[1]}" stroke="#bbbbbb" stroke-width="2" />')
            svg.append(f'  <line x1="{c3[0]+r}" y1="{c3[1]}" x2="{c4[0]-r}" y2="{c4[1]}" stroke="#bbbbbb" stroke-width="2" />')
            svg.append(f'  <line x1="{c1[0]}" y1="{c1[1]+r}" x2="{c3[0]}" y2="{c3[1]-r}" stroke="#bbbbbb" stroke-width="2" />')
            svg.append(f'  <line x1="{c2[0]}" y1="{c2[1]+r}" x2="{c4[0]}" y2="{c4[1]-r}" stroke="#bbbbbb" stroke-width="2" />')
            hole_pos = (hx, c1[1])
        else:
            hy = start_y + 77
            svg.append(f'  <line x1="{c1[0]}" y1="{c1[1]+r}" x2="{c3[0]}" y2="{c3[1]-r}" stroke="#bbbbbb" stroke-width="2" />')
            svg.append(f'  <line x1="{c2[0]}" y1="{c2[1]+r}" x2="{c2[0]}" y2="{hy-10}" stroke="#bbbbbb" stroke-width="2" />')
            svg.append(f'  <line x1="{c2[0]}" y1="{hy+10}" x2="{c4[0]}" y2="{c4[1]-r}" stroke="#bbbbbb" stroke-width="2" />')
            svg.append(f'  <line x1="{c1[0]+r}" y1="{c1[1]}" x2="{c2[0]-r}" y2="{c2[1]}" stroke="#bbbbbb" stroke-width="2" />')
            svg.append(f'  <line x1="{c3[0]+r}" y1="{c3[1]}" x2="{c4[0]-r}" y2="{c4[1]}" stroke="#bbbbbb" stroke-width="2" />')
            hole_pos = (c2[0], hy)
        
        for cx, cy in [c1, c2, c3, c4]:
            svg.append(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="#e6f2ff" stroke="#0055aa" stroke-width="1.5" />')
            svg.append(f'  <text x="{cx-7}" y="{cy+4}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#003366">Si</text>')
            
        hx, hy = hole_pos
        svg.append(f'  <circle cx="{hx}" cy="{hy}" r="8" fill="#ffffff" stroke="#cc0000" stroke-width="2" />')
        svg.append(f'  <text x="{hx-4}" y="{hy+4}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#cc0000">+</text>')
        
        if step_num == 2:
            svg.append(f'  <path d="M {c2[0]-r} {c2[1]} Q {start_x+80} {start_y+60} {hx+8} {hy}" fill="none" stroke="#0055aa" stroke-width="2" stroke-dasharray="3,3" />')
            svg.append(f'  <polygon points="{hx+12},{hy-3} {hx+5},{hy+4} {hx+13},{hy+7}" fill="#0055aa" />')

    svg.append('  <line x1="120" y1="310" x2="520" y2="310" stroke="#cc0000" stroke-width="3" />')
    svg.append('  <polyline points="510,305 520,310 510,315" fill="none" stroke="#cc0000" stroke-width="3" />')
    svg.append('  <text x="180" y="300" font-family="sans-serif" font-size="13" font-weight="bold" fill="#cc0000">Макроскопічний дрейф дірки (порожнього місця) &gt;&gt;</text>')

    svg.append('  <line x1="520" y1="342" x2="120" y2="342" stroke="#0055aa" stroke-width="2" stroke-dasharray="4,4" />')
    svg.append('  <polyline points="130,337 120,342 130,347" fill="none" stroke="#0055aa" stroke-width="2" />')
    svg.append('  <text x="210" y="335" font-family="sans-serif" font-size="12" fill="#0055aa">Мікроскопічні перескоки валентних електронів &lt;&lt;</text>')

    svg.append('</svg>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))

def create_fig3_hall_effect(filepath):
    """Фігура 3: Схема ефекту Холла в p-напівпровіднику."""
    svg = []
    svg.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 420" width="650" height="420">')
    svg.append('  <rect width="650" height="420" fill="#ffffff" />')
    
    # Задня грань
    svg.append('  <polygon points="180,120 440,120 440,240 180,240" fill="#f0f0f0" stroke="#cccccc" stroke-width="1" />')
    
    # Об'єм зразка
    svg.append('  <polygon points="140,160 400,160 440,120 180,120" fill="#e6f2ff" stroke="#0055aa" stroke-width="1.5" />')
    svg.append('  <polygon points="400,160 440,120 440,240 400,280" fill="#cce5ff" stroke="#0055aa" stroke-width="1.5" />')
    svg.append('  <polygon points="140,160 400,160 400,280 140,280" fill="#deedff" stroke="#0055aa" stroke-width="2" opacity="0.9" />')
    
    # Напис на зразку
    svg.append('  <text x="180" y="215" font-family="sans-serif" font-size="14" font-weight="bold" fill="#003366">p-напівпровідник (p &gt;&gt; n)</text>')
    
    # Струм j_x та поле E_x
    svg.append('  <line x1="50" y1="235" x2="120" y2="235" stroke="#008800" stroke-width="3" />')
    svg.append('  <polyline points="110,230 120,235 110,240" fill="none" stroke="#008800" stroke-width="3" />')
    svg.append('  <text x="50" y="198" font-family="sans-serif" font-size="13" font-weight="bold" fill="#008800">Струм j_x &gt;&gt;</text>')
    
    # Магнітне поле B_z
    svg.append('  <line x1="290" y1="370" x2="290" y2="50" stroke="#cc0000" stroke-width="2.5" stroke-dasharray="6,3" />')
    svg.append('  <polyline points="285,60 290,50 295,60" fill="none" stroke="#cc0000" stroke-width="2.5" />')
    svg.append('  <text x="305" y="65" font-family="sans-serif" font-size="14" font-weight="bold" fill="#cc0000">Поле B_z</text>')
    
    # Дірка всередині зразка
    svg.append('  <circle cx="260" cy="195" r="10" fill="#ffffff" stroke="#cc0000" stroke-width="2" />')
    svg.append('  <text x="256" y="200" font-family="sans-serif" font-size="14" font-weight="bold" fill="#cc0000">+</text>')
    svg.append('  <text x="240" y="180" font-family="sans-serif" font-size="12" fill="#cc0000">v_h (дрейф)</text>')
    
    # Сила Лоренца F_L
    svg.append('  <line x1="260" y1="205" x2="260" y2="255" stroke="#cc0000" stroke-width="2" />')
    svg.append('  <polyline points="255,245 260,255 265,245" fill="none" stroke="#cc0000" stroke-width="2" />')
    svg.append('  <text x="272" y="250" font-family="sans-serif" font-size="12" font-weight="bold" fill="#cc0000">F_L = +e(v × B)</text>')
    
    # Заряди на гранях
    # Нижня грань (+)
    for x in range(160, 390, 40):
        svg.append(f'  <text x="{x}" y="272" font-family="sans-serif" font-size="14" font-weight="bold" fill="#cc0000">+</text>')
    svg.append('  <text x="460" y="272" font-family="sans-serif" font-size="12" font-weight="bold" fill="#cc0000">Позитивний заряд</text>')
    
    # Верхня грань (-)
    for x in range(160, 390, 40):
        svg.append(f'  <text x="{x}" y="152" font-family="sans-serif" font-size="16" font-weight="bold" fill="#0055aa">-</text>')
    svg.append('  <text x="460" y="125" font-family="sans-serif" font-size="12" font-weight="bold" fill="#0055aa">Негативний заряд</text>')
    
    # Вольтметр Холла V_H (дріт зсунуто на x=30, текст V_H на x=60, y=140)
    svg.append('  <line x1="140" y1="160" x2="30" y2="160" stroke="#333333" stroke-width="1.5" />')
    svg.append('  <line x1="30" y1="160" x2="30" y2="200" stroke="#333333" stroke-width="1.5" />')
    svg.append('  <line x1="30" y1="240" x2="30" y2="280" stroke="#333333" stroke-width="1.5" />')
    svg.append('  <line x1="140" y1="280" x2="30" y2="280" stroke="#333333" stroke-width="1.5" />')
    
    svg.append('  <circle cx="30" cy="220" r="20" fill="#ffffff" stroke="#333333" stroke-width="2" />')
    svg.append('  <text x="24" y="226" font-family="sans-serif" font-size="15" font-weight="bold" fill="#333333">V</text>')
    svg.append('  <text x="65" y="145" font-family="sans-serif" font-size="12" font-weight="bold" fill="#008800">V_H &gt; 0</text>')

    svg.append('</svg>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    ensure_img_dir(img_dir)
    
    f1 = os.path.join(img_dir, 'valence-band-hole.svg')
    f2 = os.path.join(img_dir, 'hole-collective-motion.svg')
    f3 = os.path.join(img_dir, 'hall-effect-p-type.svg')
    
    create_fig1_valence_band_hole(f1)
    create_fig2_hole_motion(f2)
    create_fig3_hall_effect(f3)
    
    print(f"Фігури успішно оновлено у {img_dir}")

if __name__ == '__main__':
    main()
