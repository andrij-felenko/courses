# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def path_copying():
    """Дерево з 7 вузлів. Оновлюємо один лист (5→5*). Нова версія копіює ЛИШЕ
    шлях корінь→лист (3 нові вузли, обведені зеленим), решта піддерев спільна.
    Старе дерево — суцільним блоком угорі; новий шлях — окремим ярусом нижче,
    жоден новий вузол не лягає на старий, підписи стоять з запасом."""
    W, H = 940, 620
    green = FIELD
    R = 24

    # ── СТАРЕ дерево (спільні вузли) — верхня половина ──
    old_y = [130, 250, 370]
    node = {
        '4': (470, old_y[0]),
        '2': (290, old_y[1]), '6': (650, old_y[1]),
        '1': (200, old_y[2]), '3': (380, old_y[2]),
        '5': (560, old_y[2]), '7': (740, old_y[2]),
    }
    edges = [('4', '2'), ('4', '6'), ('2', '1'), ('2', '3'),
             ('6', '5'), ('6', '7')]

    f = []
    # ребра старого дерева
    for a, b in edges:
        f.append(line(node[a][0], node[a][1] + R, node[b][0], node[b][1] - R,
                      color=MUTED, sw=1.8))
    for k, (x, y) in node.items():
        f.append(circle(x, y, R, fill=FILL, stroke=LINE, sw=1.8))
        f.append(text(x, y + 5, k, size=15, bold=True))

    # ── НОВИЙ шлях: 4' → 6' → 5' — окремий стовпчик ЛІВОРУЧ, добре відсунутий ──
    new = {
        "4'": (130, old_y[0]),
        "6'": (130, old_y[1]),
        "5'": (130, old_y[2]),
    }
    # ребра нового шляху (суцільні зелені)
    f.append(line(new["4'"][0], new["4'"][1] + R, new["6'"][0], new["6'"][1] - R,
                  color=green, sw=2.4))
    f.append(line(new["6'"][0], new["6'"][1] + R, new["5'"][0], new["5'"][1] - R,
                  color=green, sw=2.4))
    # ПУНКТИРНІ зелені — посилання нового шляху в СПІЛЬНІ старі піддерева:
    #   4' → старий 2 (усе ліве піддерево спільне)
    f.append(line(new["4'"][0] + R, new["4'"][1] - R * 0.2, node['2'][0] - R, node['2'][1] - R * 0.2,
                  color=green, sw=1.8, dash='6,5'))
    #   6' → старий 7 (спільний лист-брат зміненого)
    f.append(line(new["6'"][0] + R, new["6'"][1] + R * 0.2, node['7'][0] - R, node['7'][1] + R * 0.6,
                  color=green, sw=1.8, dash='6,5'))

    for k, (x, y) in new.items():
        f.append(circle(x, y, R, fill='#eafaf0', stroke=green, sw=2.6))
        f.append(text(x, y + 5, k, size=15, color=INK, bold=True))

    # легенди-заголовки — рознесені, кожна у своїй зоні
    f.append(fitbox(280, 44, 380, 40, 'старе дерево — версія 1 (сірі вузли)',
                    size=13, fill=FILL, stroke=LINE))
    f.append(fitbox(40, 44, 200, 40, 'нова версія',
                    size=13, fill='#eafaf0', stroke=green, bold=True))

    # підпис зміненого листа — праворуч від старого «5», щоб не перетнути ребра
    f.append(text(560, old_y[2] + R + 22, "старий лист «5»", size=11, color=MUTED))
    f.append(text(130, old_y[2] + R + 22, "змінений лист «5*»", size=11, color=green, bold=True))

    # висновок — двома рядками внизу, з запасом
    f.append(text(W / 2, H - 54,
                  "оновлення одного листа → 3 нові вузли вздовж шляху, решта піддерев спільна",
                  size=14, color=green, bold=True))
    f.append(text(W / 2, H - 28,
                  "суцільне зелене — нові ребра · пунктирне зелене — посилання в спільне старе піддерево",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'path-copying.svg'), W, H, *f)


def cost_table():
    """Таблиця вартості: наївна копія проти структурного поділу, за операціями."""
    W, H = 880, 430
    f = []

    f.append(text(W / 2, 34, 'Вартість «зміни» незмінної структури', size=17, bold=True))

    # колонки
    cols = ['операція', 'наївна копія', 'структурний поділ', 'нових вузлів']
    col_x = [60, 300, 520, 745]      # ліві краї (для першої — ліворуч; далі центри)
    col_w = [230, 200, 205, 120]
    x0 = 40
    header_y = 74
    row_h = 58
    rows = [
        ('список: додати в голову', 'O(n)', 'O(1)', '1'),
        ('список: змінити k-й з кінця', 'O(n)', 'O(k)', 'k'),
        ('дерево-мапа: змінити ключ', 'O(n)', 'O(log n)', '~log n'),
        ('дерево-мапа: злити дві', 'O(n)', 'O(m·log n)', '~m·log n'),
    ]

    # шапка
    f.append(rect(x0, header_y, W - 2 * x0, row_h * 0.7, fill='#eef1f4', stroke=LINE, sw=1.5))
    hx = [x0 + 16, 360, 590, 800]
    anch = ['start', 'middle', 'middle', 'middle']
    for i, c in enumerate(cols):
        f.append(text(hx[i], header_y + 27, c, size=13, bold=True, anchor=anch[i]))

    y = header_y + row_h * 0.7
    for r_i, (op, naive, share, nodes) in enumerate(rows):
        yy = y + r_i * row_h
        bg = BG if r_i % 2 == 0 else '#f7f9fb'
        f.append(rect(x0, yy, W - 2 * x0, row_h, fill=bg, stroke=MUTED, sw=1))
        f.append(text(x0 + 16, yy + row_h / 2 + 5, op, size=13, anchor='start'))
        f.append(text(360, yy + row_h / 2 + 5, naive, size=14, color=POS, bold=True, anchor='middle'))
        f.append(text(590, yy + row_h / 2 + 5, share, size=14, color=FIELD, bold=True, anchor='middle'))
        f.append(text(800, yy + row_h / 2 + 5, nodes, size=13, color=INK, anchor='middle'))

    f.append(text(W / 2, y + len(rows) * row_h + 28,
                  "n — розмір структури, m — розмір меншого операнда; поділ платить за ЗМІНЕНЕ, копія — за все",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'cost-share-vs-copy.svg'), W, H, *f)


if __name__ == '__main__':
    path_copying()
    cost_table()
    print('done')
