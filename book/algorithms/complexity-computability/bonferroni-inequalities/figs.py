# -*- coding: utf-8 -*-
"""
Генерація SVG-фігур для теми "Нерівності Бонферроні".
Використовує svgkit з кореневої папки scripts.
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору від цієї теки)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def create_img_dir():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir

def fig_bounds_oscillation(out_path):
    """
    Малюнок 1: Загасання осциляцій та збіжність верхніх і нижніх меж Бонферроні
    до істинного значення ймовірності P(U A_i).
    """
    w, h = 840, 480
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        '  <defs>',
        '    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % LINE,
        '    </marker>',
        '  </defs>',
        '  <rect width="100%%" height="100%%" fill="%s"/>' % BG
    ]

    # Заголовок та сітка
    svg.append(text(w / 2, 32, "Збіжність та осциляція меж Бонферроні залежно від порядку k", size=17, bold=True))
    
    # Осі координат
    ox, oy = 90, 390
    gw, gh = 700, 300
    
    # Горизонтальні лінії сітки
    for val, label in [(0.0, "0.0"), (0.2, "0.2"), (0.4, "0.4"), (0.6, "0.6"), (0.8, "0.8"), (1.0, "1.0")]:
        y_pos = oy - val * gh
        svg.append(line(ox - 5, y_pos, ox + gw + 10, y_pos, color="#e5e7eb", sw=1.0))
        svg.append(text(ox - 15, y_pos + 4, label, size=12, color=MUTED, anchor="end"))
        
    # Вісь X (Порядок k) та вісь Y (Значення оцінки)
    svg.append(arrow(ox, oy + 10, ox, oy - gh - 30, color=INK, sw=2.0))
    svg.append(arrow(ox - 10, oy, ox + gw + 20, oy, color=INK, sw=2.0))
    
    svg.append(text(ox - 45, oy - gh - 20, "Оцінка ймовірності", size=13, bold=True, anchor="start"))
    svg.append(text(ox + gw + 15, oy + 35, "Порядок k", size=13, bold=True, anchor="end"))

    # Стовпчики / Порядки k = 1..6
    k_points = [
        (1, 0.95, "k=1 (Верхня: S₁)", POS, -24),
        (2, 0.25, "k=2 (Нижня: S₁-S₂)", NEG, 24),
        (3, 0.78, "k=3 (Верхня: S₁-S₂+S₃)", POS, -24),
        (4, 0.40, "k=4 (Нижня: S₁-S₂+S₃-S₄)", NEG, 24),
        (5, 0.65, "k=5 (Верхня)", POS, -24),
        (6, 0.55, "k=6 (Точне P(⋃Aᵢ))", FIELD, 24)
    ]
    
    x_coords = []
    y_coords = []
    
    for k_val, p_val, lbl, col, off_y in k_points:
        cx = ox + (k_val / 6.7) * gw
        cy = oy - p_val * gh
        x_coords.append(cx)
        y_coords.append(cy)
        
        # Засічка на осі X
        svg.append(line(cx, oy - 4, cx, oy + 4, color=INK, sw=1.5))
        svg.append(text(cx, oy + 20, "k = %d" % k_val, size=13, bold=True))

    # Істинна ймовірність P(∪ A_i) = 0.55
    true_p = 0.55
    true_y = oy - true_p * gh
    svg.append(line(ox, true_y, ox + gw, true_y, color=FIELD, sw=2.0, dash="6 4"))
    
    # Підпис істинної ймовірності у лівому куті над лінією
    tb, tw_box, th_box = textbox(ox + 100, true_y - 20, "Точне P(⋃ Aᵢ) = 0.55", size=12, fill="#e8f5e9", stroke=FIELD, pad=5)
    svg.append(tb)

    # Лінія осциляції меж
    poly_pts = " ".join(["%.1f,%.1f" % (x_coords[i], y_coords[i]) for i in range(len(x_coords))])
    svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="4 2"/>' % (poly_pts, MUTED))

    # Точки меж
    for i, (k_val, p_val, lbl, col, off_y) in enumerate(k_points):
        cx, cy = x_coords[i], y_coords[i]
        svg.append(circle(cx, cy, 6, fill=col, stroke="#ffffff", sw=2.0))
        
        tb, twb, thb = textbox(cx, cy + off_y, lbl, size=11, fill="#ffffff", stroke=col, pad=4)
        svg.append(tb)

    # Легенда внизу
    tb1, w1, h1 = textbox(190, 445, "Непарне k: Верхня межа (≥ P)", size=12, fill="#fbe9e7", stroke=POS, pad=6)
    tb2, w2, h2 = textbox(480, 445, "Парне k: Нижня межа (≤ P)", size=12, fill="#e8eaf6", stroke=NEG, pad=6)
    tb3, w3, h3 = textbox(730, 445, "Межа Буля (k=1)", size=12, fill="#fff3e0", stroke="#e65100", pad=6)
    svg.append(tb1)
    svg.append(tb2)
    svg.append(tb3)

    svg.append('</svg>')
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(svg))

def fig_combinatorial_identity(out_path):
    """
    Малюнок 2: Поведінка індикаторного многочлена f_k(m) для парних та непарних k
    ілюструє, чому урізані суми є строгими межами для будь-якої кількості m подій, що відбулися.
    """
    w, h = 820, 420
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        '  <defs>',
        '    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % LINE,
        '    </marker>',
        '  </defs>',
        '  <rect width="100%%" height="100%%" fill="%s"/>' % BG
    ]

    svg.append(text(w / 2, 28, "Аналіз індикаторної функції f_k(m) = ∑_{r=1}^k (-1)^{r-1} C(m, r)", size=16, bold=True))

    # Стовпчик 1: m = 0
    bx1, by1 = 150, 210
    tb1, w1, h1 = textbox(bx1, by1 - 100, "Випадок m = 0\n(жодна подія не відбулася)", size=13, fill="#f5f5f5", stroke=MUTED, pad=8, bold=True)
    svg.append(tb1)
    
    tb1_sub, _, _ = textbox(bx1, by1, "C(0, r) = 0  ∀r ≥ 1\n\n  f_k(0) = 0\n\nТочна рівність 0 = 0\n(для будь-якого k)", size=12, fill="#ffffff", stroke=LINE, pad=10)
    svg.append(tb1_sub)

    # Стовпчик 2: m >= 1, k непарне
    bx2, by2 = 450, 210
    tb2, w2, h2 = textbox(bx2, by2 - 100, "Випадок m ≥ 1\n(k = 1, 3, 5... - непарне)", size=13, fill="#fbe9e7", stroke=POS, pad=8, bold=True)
    svg.append(tb2)
    
    tb2_sub, _, _ = textbox(bx2, by2, "f_k(m) = 1 + C(m-1, k)\n\nОскільки C(m-1, k) ≥ 0:\n  f_k(m) ≥ 1\n\nВерхня оцінка для I(⋃ Aᵢ)=1", size=12, fill="#ffffff", stroke=POS, pad=10)
    svg.append(tb2_sub)

    # Стовпчик 3: m >= 1, k парне
    bx3, by3 = 710, 210
    tb3, w3, h3 = textbox(bx3, by3 - 100, "Випадок m ≥ 1\n(k = 2, 4, 6... - парне)", size=13, fill="#e8eaf6", stroke=NEG, pad=8, bold=True)
    svg.append(tb3)
    
    tb3_sub, _, _ = textbox(bx3, by3, "f_k(m) = 1 - C(m-1, k)\n\nОскільки C(m-1, k) ≥ 0:\n  f_k(m) ≤ 1\n\nНижня оцінка для I(⋃ Aᵢ)=1", size=12, fill="#ffffff", stroke=NEG, pad=10)
    svg.append(tb3_sub)

    # Нижня узагальнююча рамка
    tb_bottom, wb, hb = textbox(w / 2, 365, "Висновок: Математичне сподівання E[f_k(m)] дає P(⋃ Aᵢ) ≤ S₁ - S₂ + ... + S_k (непарні k)\nта P(⋃ Aᵢ) ≥ S₁ - S₂ + ... - S_k (парні k) для довільних залежних подій.", size=13, fill="#e8f5e9", stroke=FIELD, pad=10, bold=True)
    svg.append(tb_bottom)

    svg.append('</svg>')
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(svg))

def fig_network_reliability(out_path):
    """
    Малюнок 3: Застосування нерівностей Бонферроні до оцінки надійності мережі
    з перетинанням відмов (Cut-Sets).
    """
    w, h = 840, 450
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        '  <defs>',
        '    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % LINE,
        '    </marker>',
        '  </defs>',
        '  <rect width="100%%" height="100%%" fill="%s"/>' % BG
    ]

    svg.append(text(w / 2, 28, "Оцінка імовірності відмови системи за допомогою перерізів (Cut-Sets)", size=16, bold=True))

    # Джерело S (ліворуч)
    sx, sy = 80, 180
    svg.append(circle(sx, sy, 22, fill="#e0f2fe", stroke=NEG, sw=2.0))
    svg.append(text(sx, sy + 5, "S", size=14, bold=True, color=NEG))
    
    # Приймач T (праворуч)
    tx, ty = 340, 180
    svg.append(circle(tx, ty, 22, fill="#e0f2fe", stroke=NEG, sw=2.0))
    svg.append(text(tx, ty + 5, "T", size=14, bold=True, color=NEG))

    # Вузли між S та T
    n1x, n1y = 210, 100
    n2x, n2y = 210, 260
    
    svg.append(circle(n1x, n1y, 18, fill=FILL, stroke=LINE, sw=1.5))
    svg.append(text(n1x, n1y + 4, "V₁", size=12, bold=True))

    svg.append(circle(n2x, n2y, 18, fill=FILL, stroke=LINE, sw=1.5))
    svg.append(text(n2x, n2y + 4, "V₂", size=12, bold=True))

    # Лінії зв'язку між вузлами
    svg.append(line(sx + 20, sy - 10, n1x - 15, n1y + 10, color=LINE, sw=1.8))
    svg.append(line(n1x + 15, n1y + 10, tx - 20, ty - 10, color=LINE, sw=1.8))
    
    svg.append(line(sx + 20, sy + 10, n2x - 15, n2y - 10, color=LINE, sw=1.8))
    svg.append(line(n2x + 15, n2y - 10, tx - 20, ty + 10, color=LINE, sw=1.8))
    
    svg.append(line(n1x, n1y + 18, n2x, n2y - 18, color=LINE, sw=1.5, dash="4 2"))

    # Події відмов (A1, A2, A3 - мінімальні перерізи)
    tb_net, _, _ = textbox(210, 335, "Граф мережі та мінімальні перерізи відмови:\n A₁: {e(S,V₁), e(S,V₂)}\n A₂: {e(V₁,T), e(V₂,T)}\n A₃: {e(S,V₁), e(V₁,V₂), e(V₂,T)}", size=11, fill="#ffffff", stroke=MUTED, pad=6)
    svg.append(tb_net)

    # Права частина: Порівняння складності та точності
    px = 600
    
    # Точне обчислення (2^n)
    tb_exact, _, _ = textbox(px, 100, "Точний вираз Poincaré (2ⁿ - 1 доданків):\n P(A₁ ∪ A₂ ∪ A₃) = S₁ - S₂ + S₃\n Складність: NP-hard / #P-complete", size=12, fill="#fbe9e7", stroke=POS, pad=8, bold=True)
    svg.append(tb_exact)

    # Наближення 1-го порядку (Буль)
    tb_k1, _, _ = textbox(px, 200, "Оцінка k = 1 (Нерівність Буля):\n P(Відмови) ≤ P(A₁) + P(A₂) + P(A₃)\n Швидке верхнє обмеження risk O(n)", size=12, fill="#fff3e0", stroke="#e65100", pad=8)
    svg.append(tb_k1)

    # Наближення 2-го порядку (Бонферроні k=2)
    tb_k2, _, _ = textbox(px, 300, "Оцінка k = 2 (Бонферроні нижнє):\n P(Відмови) ≥ S₁ - [P(A₁∩A₂) + P(A₁∩A₃) + P(A₂∩A₃)]\n Враховує подвійні перетини cut-sets O(n²)", size=12, fill="#e8eaf6", stroke=NEG, pad=8)
    svg.append(tb_k2)

    # Нижня підсумкова рамка
    tb_footer, _, _ = textbox(w / 2, 405, "Перевага Бонферроні: Обчислення S₁ та S₂ вимагає O(n²), уникаючи вибуху 2ⁿ комбінацій.", size=12, fill="#e8f5e9", stroke=FIELD, pad=8, bold=True)
    svg.append(tb_footer)

    svg.append('</svg>')
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(svg))

def main():
    img_dir = create_img_dir()
    fig_bounds_oscillation(os.path.join(img_dir, "bonferroni-bounds-oscillation.svg"))
    fig_combinatorial_identity(os.path.join(img_dir, "indicator-combinatorial-function.svg"))
    fig_network_reliability(os.path.join(img_dir, "network-reliability-cutsets.svg"))
    print("Figures generated successfully in", img_dir)

if __name__ == "__main__":
    main()
