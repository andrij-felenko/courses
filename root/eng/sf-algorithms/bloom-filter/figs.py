# -*- coding: utf-8 -*-
"""Фігури до статті «Фільтр Блума». Запуск із теки теми: python figs.py
Виводить SVG у ./img/. Розкладка — із запасом, підписи рознесено."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CW, CH = 42, 38
FILLED = "#eaf0fd"
EMPTY  = BG
HIGHLIGHT = "#fdecea"

def cell(x, y, label, w=CW, h=CH, fill=FILL, stroke=LINE, sw=1.6, tcolor=INK, tsize=14, bold=False):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=4)
    if label != "":
        out += text(x + w / 2, y + h / 2 + tsize * 0.35, label, size=tsize, color=tcolor, bold=bold)
    return out

# ── Фігура 1: Хешування та бітовий масив у фільтрі Блума ───────────────────────
def fig_lookup():
    W, H = 880, 420
    parts = []
    
    parts.append(text(W / 2, 32, "Принцип роботи фільтра Блума: вставка та перевірка належності", size=16, bold=True))
    
    # Ключі зверху
    # Ключ X (вставити)
    parts.append(rect(100, 70, 160, 44, fill="#eaf0fd", stroke=POS, sw=1.8, rx=6))
    parts.append(text(180, 97, "Ключ X (додано)", size=14, bold=True, color=POS))
    
    # Ключ Y (вставити)
    parts.append(rect(360, 70, 160, 44, fill="#eaf0fd", stroke=POS, sw=1.8, rx=6))
    parts.append(text(440, 97, "Ключ Y (додано)", size=14, bold=True, color=POS))
    
    # Ключ Z (запит)
    parts.append(rect(620, 70, 170, 44, fill="#fdecea", stroke=NEG, sw=1.8, rx=6))
    parts.append(text(705, 97, "Ключ Z (перевірка)", size=14, bold=True, color=NEG))
    
    # Бітовий масив посередині (16 бітів, m = 16)
    ax, ay = 60, 220
    bit_values = [0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0]
    
    for i in range(16):
        x = ax + i * (CW + 8)
        val_str = str(bit_values[i])
        fill_col = FILLED if bit_values[i] == 1 else EMPTY
        txt_col = POS if bit_values[i] == 1 else MUTED
        parts.append(text(x + CW / 2, ay - 12, str(i), size=12, color=MUTED))
        parts.append(cell(x, ay, val_str, w=CW, h=CH, fill=fill_col, tcolor=txt_col, bold=(bit_values[i]==1)))
    
    parts.append(text(ax - 20, ay + CH / 2 + 4, "Біти:", size=13, color=MUTED, anchor="end"))
    
    # Стрілки від ключа X до бітів 1, 4, 9
    x_indices = [1, 4, 9]
    for idx in x_indices:
        target_x = ax + idx * (CW + 8) + CW / 2
        parts.append(arrow(180, 114, target_x, ay - 4, color=POS, sw=1.5))
    parts.append(text(130, 160, "h1, h2, h3", size=12, color=POS))
    
    # Стрілки від ключа Y до бітів 3, 7, 12
    y_indices = [3, 7, 12]
    for idx in y_indices:
        target_x = ax + idx * (CW + 8) + CW / 2
        parts.append(arrow(440, 114, target_x, ay - 4, color=POS, sw=1.5))
    parts.append(text(490, 160, "h1, h2, h3", size=12, color=POS))
    
    # Стрілки від ключа Z (запит) до бітів 1, 7, 14
    z_indices = [1, 7, 14]
    for idx in z_indices:
        target_x = ax + idx * (CW + 8) + CW / 2
        parts.append(arrow(705, 114, target_x, ay - 4, color=NEG, sw=1.5))
    parts.append(text(745, 160, "h1, h2, h3", size=12, color=NEG))
    
    # Підпис знизу
    parts.append(text(W / 2, ay + CH + 45, "Усі біти для Z виявилися рівними 1 (встановлені ключами X та Y) → ХИБНОПОЗИТИВНЕ СПРАЦЬОВУВАННЯ", size=13.5, color=NEG, bold=True))
    parts.append(text(W / 2, ay + CH + 70, "Якби хоч один біт дорівнював 0, елемента Z ТОЧНО не було б у множині", size=12.5, color=MUTED))

    render(os.path.join(IMG, "bloom-filter-lookup.svg"), W, H, *parts)


# ── Фігура 2: Залежність ймовірності хибного спрацьовування p від k ───────────
def fig_fp_curve():
    W, H = 760, 400
    parts = []
    
    parts.append(text(W / 2, 32, "Ймовірність хибного спрацьовування p(k) при m/n = 8", size=16, bold=True))
    
    # Осі координат
    ox, oy = 90, 320
    gw, gh = 580, 240
    
    # Осі
    parts.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2))
    parts.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2))
    
    # Підписи осей
    parts.append(text(ox + gw / 2, oy + 45, "Кількість хеш-функцій k", size=13, bold=True))
    parts.append(text(ox - 55, oy - gh / 2, "Ймовірність p", size=13, bold=True, anchor="middle"))
    
    # Сітка та мітки по Y (0% .. 25%)
    y_ticks = [(0.0, "0%"), (0.05, "5%"), (0.10, "10%"), (0.15, "15%"), (0.20, "20%"), (0.25, "25%")]
    for val, label in y_ticks:
        y_pos = oy - (val / 0.25) * gh
        parts.append(line(ox - 5, y_pos, ox + gw, y_pos, color="#e5e9f0", sw=1))
        parts.append(text(ox - 10, y_pos + 4, label, size=11.5, color=MUTED, anchor="end"))
        
    # Мітки по X (k = 1..12)
    for k_val in range(1, 13):
        x_pos = ox + (k_val / 12.0) * gw
        parts.append(line(x_pos, oy, x_pos, oy + 5, color=LINE, sw=1.5))
        parts.append(text(x_pos, oy + 22, str(k_val), size=12, color=INK))
        
    # Крива p(k) = (1 - e^(-k/8))^k  при m/n = 8
    import math
    points = []
    mn_ratio = 8.0
    for i in range(121):
        k_v = 0.5 + i * (11.5 / 120.0)
        p_v = (1.0 - math.exp(-k_v / mn_ratio)) ** k_v
        x_p = ox + (k_v / 12.0) * gw
        y_p = oy - (p_v / 0.25) * gh
        points.append((x_p, y_p))
        
    # Малюємо криву як сукупність відрізків
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        parts.append(line(x1, y1, x2, y2, color=POS, sw=2.5))
        
    # Мінімум при k = 8 * ln(2) ≈ 5.54 -> k = 5 або 6 (p ≈ 2.15%)
    k_opt = 8.0 * math.log(2)
    p_opt = (1.0 - math.exp(-k_opt / mn_ratio)) ** k_opt
    x_opt = ox + (k_opt / 12.0) * gw
    y_opt = oy - (p_opt / 0.25) * gh
    
    parts.append(circle(x_opt, y_opt, r=5, fill=NEG, stroke=INK, sw=1.5))
    parts.append(line(x_opt, oy, x_opt, y_opt, color=NEG, sw=1.5, dash="3,3"))
    parts.append(text(x_opt + 10, y_opt - 12, f"Мінімум k ≈ 5.54 (p ≈ {p_opt*100:.2f}%)", size=12, color=NEG, bold=True))
    
    render(os.path.join(IMG, "bloom-filter-fp-curve.svg"), W, H, *parts)

if __name__ == '__main__':
    fig_lookup()
    fig_fp_curve()
    print("Згенеровано фігури в ./img/")
