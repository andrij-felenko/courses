# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для теми "Інтерполяція Лагранжа".
Використовує бібліотеку svgkit з кореневої теки scripts.
"""

import sys
import os
import math

# Підключаємо scripts/ з кореня репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def draw_basis_polynomials():
    """Фігура 1: Базисні поліноми Лагранжа L_k(x) для вузлів x0=1, x1=2, x2=4."""
    w, h = 760, 360
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" height="100%%">' % (w, h)]
    
    # Фон
    svg.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    
    # Заголовок панелі
    tb, tw, th = textbox(w/2, 28, "Базисні поліноми Лагранжа Lₖ(x) для вузлів x₀=1, x₁=2, x₂=4", size=15, bold=True, fill="#eef2f7", stroke="#4a5568")
    svg.append(tb)
    
    # Система координат
    ox, oy = 90, 290
    scale_x, scale_y = 120, 180
    
    # Сітка та осі
    svg.append(line(ox - 30, oy, ox + 450, oy, color=MUTED, sw=1.2))
    svg.append(line(ox, oy + 40, ox, oy - scale_y - 30, color=MUTED, sw=1.2))
    
    # Лінія y = 1
    y1_px = oy - scale_y
    svg.append(line(ox - 20, y1_px, ox + 450, y1_px, color="#cbd5e1", sw=1.0, dash="4,4"))
    svg.append(text(ox - 25, y1_px + 4, "y = 1", size=12, color=MUTED, anchor="end", bold=True))
    svg.append(text(ox - 25, oy + 4, "y = 0", size=12, color=MUTED, anchor="end"))
    
    # Позначки на осі X
    nodes = [1.0, 2.0, 4.0]
    node_labels = ["x₀ = 1", "x₁ = 2", "x₂ = 4"]
    for val, lbl in zip(nodes, node_labels):
        px = ox + val * scale_x
        svg.append(line(px, oy - 6, px, oy + 6, color=INK, sw=1.5))
        svg.append(text(px, oy + 22, lbl, size=13, color=INK, anchor="middle", bold=True))
    
    # Функції L0, L1, L2
    def L0(x): return (x - 2.0) * (x - 4.0) / 3.0
    def L1(x): return (x - 1.0) * (x - 4.0) / (-2.0)
    def L2(x): return (x - 1.0) * (x - 2.0) / 6.0
    
    colors = [POS, NEG, FIELD]
    funcs = [L0, L1, L2]
    names = ["L₀(x) (1 у x₀, 0 у x₁, x₂)", "L₁(x) (1 у x₁, 0 у x₀, x₂)", "L₂(x) (1 у x₂, 0 у x₀, x₁)"]
    
    for f, c in zip(funcs, colors):
        pts = []
        x_start = 0.5
        x_end = 4.2
        steps = 200
        for i in range(steps + 1):
            x_val = x_start + (x_end - x_start) * i / steps
            y_val = f(x_val)
            px = ox + x_val * scale_x
            py = oy - y_val * scale_y
            pts.append("%.1f,%.1f" % (px, py))
        svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts), c))
    
    # Ключові точки
    for k, (x_k, c) in enumerate(zip(nodes, colors)):
        px = ox + x_k * scale_x
        py_1 = oy - scale_y
        svg.append(circle(px, py_1, 5.5, fill=c, stroke=BG, sw=1.5))
        for j, x_j in enumerate(nodes):
            if k != j:
                px_0 = ox + x_j * scale_x
                svg.append(circle(px_0, oy, 4.0, fill=BG, stroke=c, sw=1.5))
                
    # Легенда праворуч зверху в чистому місці
    lx, ly = 475, 45
    svg.append(rect(lx, ly, 270, 95, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    svg.append(text(lx + 135, ly + 20, "Легенда базисних многочленів:", size=12, bold=True, color=INK))
    for idx, (nm, c) in enumerate(zip(names, colors)):
        py_l = ly + 42 + idx * 22
        svg.append(line(lx + 15, py_l - 4, lx + 35, py_l - 4, color=c, sw=2.5))
        svg.append(text(lx + 45, py_l, nm, size=11, color=INK, anchor="start"))
        
    svg.append('</svg>')
    return "\n".join(svg)

def draw_vandermonde_vs_lagrange():
    """Фігура 2: Порівняння матричної системи Вандермонда та базисної суперпозиції Лагранжа."""
    w, h = 760, 320
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" height="100%%">' % (w, h)]
    
    svg.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    
    # Заголовок
    tb, _, _ = textbox(w/2, 25, "Два шляхи побудови полінома: Метод коефіцієнтів vs Суперпозиція Лагранжа", size=14, bold=True, fill="#eef2f7", stroke="#4a5568")
    svg.append(tb)
    
    # Ліва колонка: Матричний підхід (Вандермонд)
    lx = 190
    tb1, _, _ = textbox(lx, 65, "1. Прямий метод коефіцієнтів (О(n³))", size=13, bold=True, fill="#fee2e2", stroke=POS)
    svg.append(tb1)
    
    matrix_box = [
        "[ 1  x₀  x₀²  …  x₀ⁿ ]   [ c₀ ]   [ y₀ ]",
        "[ 1  x₁  x₁²  …  x₁ⁿ ] · [ c₁ ] = [ y₁ ]",
        "[ …  …   …    …  …   ]   [ …  ]   [ …  ]",
        "[ 1  x╙  x╙²  …  x╙ⁿ ]   [ c╙ ]   [ y╙ ]"
    ]
    svg.append(rect(25, 95, 330, 115, fill="#fff5f5", stroke="#fca5a5", sw=1.2, rx=6))
    svg.append(mtext(190, 120, matrix_box, size=12, color=POS, bold=False))
    
    desc_v = [
        "• Потребує розв'язання СЛАР (О(n³))",
        "• Число обумовленості cond(V) зростає як eⁿ",
        "• Катастрофічна чисельна нестабільність"
    ]
    svg.append(mtext(190, 230, desc_v, size=11, color=INK))
    
    # Розділювальна лінія
    svg.append(line(380, 50, 380, 300, color="#e2e8f0", sw=1.5, dash="4,4"))
    
    # Права колонка: Базис Лагранжа
    rx = 570
    tb2, _, _ = textbox(rx, 65, "2. Явна суперпозиція Лагранжа (О(n²))", size=13, bold=True, fill="#dcfce7", stroke=FIELD)
    svg.append(tb2)
    
    lagrange_box = [
        "P(x) = y₀·L₀(x) + y₁·L₁(x) + … + y╙·L╙(x)",
        "",
        "де  L╖(x) = ∏ (x - xⱼ) / (x╖ - xⱼ)  (j ≠ k)"
    ]
    svg.append(rect(405, 95, 330, 115, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    svg.append(mtext(rx, 125, lagrange_box, size=12, color="#15803d", bold=True))
    
    desc_l = [
        "• Не потребує обернення матриць",
        "• Дискретний аналог імпульсного відгуку",
        "• Легко трансформується у барицентричну форму"
    ]
    svg.append(mtext(rx, 230, desc_l, size=11, color=INK))
    
    svg.append('</svg>')
    return "\n".join(svg)

def draw_runge_vs_chebyshev():
    """Фігура 3: Феномен Рунге при рівномірній сітці проти стійкої інтерполяції на вузлах Чебишова."""
    w, h = 760, 360
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" height="100%%">' % (w, h)]
    
    svg.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    
    # Заголовок
    tb, _, _ = textbox(w/2, 28, "Феномен Рунге на рівномірній сітці проти вузлів Чебишова для f(x) = 1/(1 + 25x²)", size=14, bold=True, fill="#eef2f7", stroke="#4a5568")
    svg.append(tb)
    
    # Графік
    ox, oy = 380, 250
    scale_x, scale_y = 300, 180
    
    # Осі
    svg.append(line(ox - scale_x - 20, oy, ox + scale_x + 20, oy, color=MUTED, sw=1.2))
    svg.append(line(ox, oy + 30, ox, oy - scale_y - 20, color=MUTED, sw=1.2))
    svg.append(text(ox + scale_x + 15, oy + 18, "x", size=13, color=INK, bold=True))
    svg.append(text(ox + 15, oy - scale_y - 10, "y", size=13, color=INK, bold=True))
    
    # Межі [-1, 1]
    px_m1 = ox - scale_x
    px_p1 = ox + scale_x
    svg.append(line(px_m1, oy - 5, px_m1, oy + 5, color=INK, sw=1.5))
    svg.append(line(px_p1, oy - 5, px_p1, oy + 5, color=INK, sw=1.5))
    svg.append(text(px_m1, oy + 20, "-1.0", size=12, color=INK, anchor="middle"))
    svg.append(text(px_p1, oy + 20, "1.0", size=12, color=INK, anchor="middle"))
    
    # Точна функція f(x) = 1 / (1 + 25x^2)
    def f_runge(x): return 1.0 / (1.0 + 25.0 * x * x)
    
    pts_exact = []
    steps = 300
    for i in range(steps + 1):
        x_val = -1.0 + 2.0 * i / steps
        y_val = f_runge(x_val)
        px = ox + x_val * scale_x
        py = oy - y_val * scale_y
        pts_exact.append("%.1f,%.1f" % (px, py))
    svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="5,5"/>' % (" ".join(pts_exact), INK))
    
    # Осцилюючий поліном на рівномірній сітці
    def P_uniform(x):
        exact = f_runge(x)
        edge_osc = 0.35 * (x**10) * math.sin(12 * math.pi * x)
        return exact + edge_osc
        
    pts_unif = []
    for i in range(steps + 1):
        x_val = -1.0 + 2.0 * i / steps
        y_val = P_uniform(x_val)
        px = ox + x_val * scale_x
        py = oy - y_val * scale_y
        pts_unif.append("%.1f,%.1f" % (px, py))
    svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_unif), POS))
    
    # Поліном на вузлах Чебишова
    def P_cheb(x):
        exact = f_runge(x)
        minor_err = 0.02 * math.cos(8 * math.pi * x) * (1 - x**2)
        return exact + minor_err
        
    pts_cheb = []
    for i in range(steps + 1):
        x_val = -1.0 + 2.0 * i / steps
        y_val = P_cheb(x_val)
        px = ox + x_val * scale_x
        py = oy - y_val * scale_y
        pts_cheb.append("%.1f,%.1f" % (px, py))
    svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_cheb), FIELD))
    
    # Вказуємо на крайові сплески
    svg.append(arrow(ox - scale_x * 0.70, oy - scale_y * 0.65, ox - scale_x * 0.90, oy - scale_y * 0.30, color=POS, sw=1.8))
    svg.append(text(ox - scale_x * 0.65, oy - scale_y * 0.70, "Крайові сплески похибки!", size=11, color=POS, bold=True))
    
    # Легенда у вільному правому верхньому кутку (x ~ 0.5..1.0, y ~ 0.8..1.0, px ~ 520..740, py ~ 50..130)
    lx, ly = 465, 50
    svg.append(rect(lx, ly, 275, 85, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    svg.append(line(lx + 15, ly + 20, lx + 45, ly + 20, color=INK, sw=2.0, dash="4,4"))
    svg.append(text(lx + 55, ly + 24, "Точна функція 1/(1+25x²)", size=11, color=INK))
    
    svg.append(line(lx + 15, ly + 42, lx + 45, ly + 42, color=POS, sw=2.5))
    svg.append(text(lx + 55, ly + 46, "Рівномірна сітка (катастрофа)", size=11, color=POS, bold=True))
    
    svg.append(line(lx + 15, ly + 64, lx + 45, ly + 64, color=FIELD, sw=2.5))
    svg.append(text(lx + 55, ly + 68, "Вузли Чебишова (стійка)", size=11, color=FIELD, bold=True))
    
    svg.append('</svg>')
    return "\n".join(svg)

def draw_barycentric_update():
    """Фігура 4: Схема швидкодії барицентричної форми та додавання нового вузла за O(n)."""
    w, h = 760, 320
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" height="100%%">' % (w, h)]
    
    svg.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    
    # Заголовок
    tb, _, _ = textbox(w/2, 25, "Структура обчислень у барицентричній формі Лагранжа другої родини", size=14, bold=True, fill="#eef2f7", stroke="#4a5568")
    svg.append(tb)
    
    # Блок 1: Попереднє обчислення ваг w_k
    b1_x, b1_y = 140, 110
    svg.append(rect(b1_x - 110, b1_y - 45, 220, 90, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    svg.append(text(b1_x, b1_y - 20, "1. Попередні ваги wₖ", size=13, color=NEG, bold=True))
    svg.append(text(b1_x, b1_y + 5, "wₖ = 1 / ∏ (xₖ - xⱼ)", size=12, color=INK))
    svg.append(text(b1_x, b1_y + 25, "Складність: O(n²)", size=11, color=MUTED))
    
    # Блок 2: Оцінка в точці x
    b2_x, b2_y = 380, 110
    svg.append(rect(b2_x - 110, b2_y - 45, 220, 90, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    svg.append(text(b2_x, b2_y - 20, "2. Оцінка P(x) у точці x", size=13, color=FIELD, bold=True))
    svg.append(text(b2_x, b2_y + 5, "P(x) = ∑ [wₖyₖ/(x-xₖ)] / ∑ [wₖ/(x-xₖ)]", size=11, color=INK, bold=True))
    svg.append(text(b2_x, b2_y + 25, "Складність: O(n) на точку!", size=11, color=FIELD, bold=True))
    
    # Блок 3: Додавання нового вузла
    b3_x, b3_y = 620, 110
    svg.append(rect(b3_x - 110, b3_y - 45, 220, 90, fill="#fff7ed", stroke="#ea580c", sw=1.5, rx=6))
    svg.append(text(b3_x, b3_y - 20, "3. Додавання вузла xₙ₊₁", size=13, color="#ea580c", bold=True))
    svg.append(text(b3_x, b3_y + 5, "wₖ′ = wₖ / (xₖ - xₙ₊₁)", size=12, color=INK))
    svg.append(text(b3_x, b3_y + 25, "Складність оновлення: O(n)", size=11, color="#ea580c"))
    
    # Стрілки зв'язку
    svg.append(arrow(b1_x + 110, b1_y, b2_x - 110, b2_y, color=INK, sw=1.8))
    svg.append(arrow(b3_x - 110, b3_y + 20, b2_x + 110, b2_y + 20, color="#ea580c", sw=1.8))
    
    # Нижня пояснювальна картка
    svg.append(rect(50, 195, 660, 100, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    inf_lines = [
        "Ключова перевага другої барицентричної форми:",
        "1. Скорочення спільного множника ω(x) робить чисельну оцінку високостійкою (чисельна стабільність за Гайемом).",
        "2. Знаменник суми інваріантний до зсуву значень yₖ, що дозволяє перевикористовувати ваги wₖ для будь-яких наборів даних."
    ]
    svg.append(mtext(380, 218, inf_lines, size=11, color=INK))
    
    svg.append('</svg>')
    return "\n".join(svg)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    files = {
        'lagrange-basis-polynomials.svg': draw_basis_polynomials(),
        'vandermonde-matrix-system.svg': draw_vandermonde_vs_lagrange(),
        'runge-phenomenon-vs-chebyshev.svg': draw_runge_vs_chebyshev(),
        'barycentric-weights-update.svg': draw_barycentric_update()
    }
    
    for fname, content in files.items():
        fpath = os.path.join(img_dir, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated: {fpath}")

if __name__ == '__main__':
    main()
