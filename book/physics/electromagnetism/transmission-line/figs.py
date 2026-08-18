# -*- coding: utf-8 -*-
"""Фігури до теми «Лінія передачі».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=LINE, sw=2):
    pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{pts_str}" fill="none" stroke="{color}" stroke-width="{sw}"/>'


def fig_lumped_vs_distributed():
    """Фігура 1: Порівняння кола зі зосередженими та розподіленими параметрами."""
    W, H = 760, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 28, "Перехід від зосереджених кіл до розподіленої лінії передачі", size=16, bold=True))

    # Ліва панель: Зосереджене коло (L << lambda)
    f.append(rect(20, 50, 350, 265, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(195, 75, "Зосереджені параметри (L ≪ λ)", size=14, bold=True, color="#1e40af"))
    f.append(text(195, 95, "Закони Кірхгофа виконуються миттєво", size=11, color=MUTED))

    # Схема зосередженого кола
    f.append(circle(60, 150, 16, fill="#eff6ff", stroke="#2563eb", sw=1.8))
    f.append(text(60, 155, "~", size=16, bold=True, color="#2563eb"))
    f.append(text(60, 182, "U(t)", size=11, color=MUTED))

    # Дроти до навантаження
    f.append(line(76, 150, 280, 150, color=LINE, sw=2))
    f.append(line(76, 230, 280, 230, color=LINE, sw=2))
    f.append(line(60, 166, 60, 230, color=LINE, sw=2))

    # Резистор R_L
    f.append(rect(280, 135, 30, 110, fill="#ffffff", stroke=INK, sw=1.8))
    f.append(text(295, 190, "R_L", size=13, bold=True))

    # Позначення струму
    f.append(arrow(110, 138, 170, 138, color="#2563eb", sw=1.8))
    f.append(text(140, 124, "I(t) однаковій всюди", size=11, color="#2563eb", bold=True))
    f.append(text(195, 275, "Фаза напруги і струму однакова по всій довжині", size=11, color=INK))

    # Права панель: Розподілена лінія (L >= lambda)
    f.append(rect(390, 50, 350, 265, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(565, 75, "Розподілена лінія передачі (L ≳ λ)", size=14, bold=True, color="#b91c1c"))
    f.append(text(565, 95, "Хвильовий процес: напруга і струм залежать від z", size=11, color=MUTED))

    # Джерело високочастотного сигналу
    f.append(circle(430, 150, 16, fill="#fef2f2", stroke="#dc2626", sw=1.8))
    f.append(text(430, 155, "~", size=16, bold=True, color="#dc2626"))
    f.append(text(430, 182, "U(0,t)", size=11, color=MUTED))

    # Два паралельні провідники лінії передачі
    f.append(line(446, 150, 650, 150, color=LINE, sw=2.5))
    f.append(line(446, 230, 650, 230, color=LINE, sw=2.5))
    f.append(line(430, 166, 430, 230, color=LINE, sw=2))

    # Навантаження Z_L
    f.append(rect(650, 135, 30, 110, fill="#ffffff", stroke=INK, sw=1.8))
    f.append(text(665, 190, "Z_L", size=13, bold=True))

    # Синусоїдальна біжуча хвиля між провідниками
    pts = []
    for x_i in range(0, 201, 5):
        px = 446 + x_i
        py = 190 + 32 * math.sin(x_i * 0.08)
        pts.append((px, py))
    f.append(polyline(pts, color="#dc2626", sw=2))

    # Вектори поля / струму в різних точках z
    f.append(arrow(470, 138, 510, 138, color="#2563eb", sw=1.8))
    f.append(text(490, 124, "I(z₁,t)", size=10, bold=True, color="#2563eb"))

    f.append(arrow(570, 138, 610, 138, color="#dc2626", sw=1.8))
    f.append(text(590, 124, "I(z₂,t)", size=10, bold=True, color="#dc2626"))

    f.append(text(565, 275, "Напруга і струм є біжучими хвилями V(z,t), I(z,t)", size=11, color=INK))

    return render(os.path.join(IMG, "lumped-vs-distributed.svg"), W, H, *f)


def fig_telegrapher_element():
    """Фігура 2: Елементарний відрізок dz лінії передачі з погонними параметрами."""
    W, H = 760, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 26, "Еквівалентна схема нескінченно малого сегмента лінії dz", size=16, bold=True))

    # Рамка для схеми
    f.append(rect(20, 48, W - 40, H - 76, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))

    # Сигнальний провідник
    f.append(line(50, 100, 140, 100, color=LINE, sw=2))

    # R_0 dz
    f.append(rect(140, 85, 75, 30, fill="#ffffff", stroke=INK, sw=1.8))
    f.append(text(177, 105, "R₀·dz", size=12, bold=True))

    f.append(line(215, 100, 265, 100, color=LINE, sw=2))

    # L_0 dz
    f.append(rect(265, 85, 75, 30, fill="#eef4ff", stroke="#2563eb", sw=1.8, rx=4))
    f.append(text(302, 105, "L₀·dz", size=12, bold=True, color="#1e40af"))

    f.append(line(340, 100, 520, 100, color=LINE, sw=2))

    # Поперечна гілка в точці z
    f.append(circle(440, 100, 4, fill=INK, stroke='none'))

    # G_0 dz
    f.append(line(440, 100, 440, 130, color=LINE, sw=2))
    f.append(rect(405, 130, 70, 30, fill="#ffffff", stroke=INK, sw=1.8))
    f.append(text(440, 150, "G₀·dz", size=12, bold=True))
    f.append(line(440, 160, 440, 185, color=LINE, sw=2))

    # C_0 dz (обкладки конденсатора)
    f.append(line(415, 185, 465, 185, color=LINE, sw=2.5))
    f.append(line(415, 195, 465, 195, color=LINE, sw=2.5))
    f.append(text(495, 193, "C₀·dz", size=12, bold=True, color="#059669"))
    f.append(line(440, 195, 440, 235, color=LINE, sw=2))

    # Зворотний провідник (земля)
    f.append(line(50, 235, 700, 235, color=LINE, sw=2))
    f.append(circle(440, 235, 4, fill=INK, stroke='none'))

    # Вхідні V(z,t), I(z,t)
    f.append(arrow(60, 75, 110, 75, color="#2563eb", sw=2))
    f.append(text(85, 62, "I(z, t)", size=12, bold=True, color="#2563eb"))

    f.append(arrow(60, 115, 60, 220, color="#dc2626", sw=1.6))
    f.append(text(25, 168, "V(z, t)", size=12, bold=True, color="#dc2626", anchor="start"))

    # Вихідні V(z+dz,t), I(z+dz,t)
    f.append(arrow(540, 75, 600, 75, color="#2563eb", sw=2))
    f.append(text(570, 62, "I(z+dz, t)", size=12, bold=True, color="#2563eb"))

    f.append(arrow(680, 115, 680, 220, color="#dc2626", sw=1.6))
    f.append(text(685, 168, "V(z+dz, t)", size=12, bold=True, color="#dc2626", anchor="start"))

    # Позначка довжини dz
    f.append(line(140, 260, 520, 260, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(330, 275, "довжина сегмента = dz", size=12, color=MUTED))

    return render(os.path.join(IMG, "telegrapher-element.svg"), W, H, *f)


def fig_poynting_flow():
    """Фігура 3: Вектор Пойнтінга та потік енергії в коаксіальній лінії."""
    W, H = 760, 350
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Транспортування енергії: потік вектора Пойнтінга S у лінії передачі", size=16, bold=True))

    # Ліва частина: Поперечний переріз коаксіала з полями E, H та полем S
    f.append(rect(20, 50, 350, 275, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(195, 75, "Поперечний переріз коаксіала", size=13, bold=True))

    # Зовнішня жила
    f.append(circle(195, 185, 80, fill="#f1f5f9", stroke=INK, sw=2.5))
    # Внутрішня жила
    f.append(circle(195, 185, 26, fill="#cbd5e1", stroke=INK, sw=2))
    f.append(text(195, 189, "+Q", size=11, bold=True, color="#b91c1c"))

    # Радіальні силові лінії E (червоні)
    angles = [0, 45, 90, 135, 180, 225, 270, 315]
    for a in angles:
        rad = math.radians(a)
        x1 = 195 + 26 * math.cos(rad)
        y1 = 185 + 26 * math.sin(rad)
        x2 = 195 + 80 * math.cos(rad)
        y2 = 185 + 80 * math.sin(rad)
        f.append(arrow(x1, y1, x2, y2, color="#dc2626", sw=1.5))

    # Колові силові лінії H (сині)
    f.append(circle(195, 185, 52, fill="none", stroke="#2563eb", sw=1.8))
    f.append(text(255, 185, "H", size=12, bold=True, color="#2563eb"))
    f.append(text(195, 115, "E", size=12, bold=True, color="#dc2626"))

    # Позначка вектора Пойнтінга S вглиб екрана
    f.append(circle(230, 140, 10, fill="#fef08a", stroke="#d97706", sw=1.5))
    f.append(line(223, 133, 237, 147, color="#d97706", sw=1.8))
    f.append(line(223, 147, 237, 133, color="#d97706", sw=1.8))
    f.append(text(230, 120, "S = E × H (вглиб)", size=11, bold=True, color="#b91c1c"))

    # Права частина: Поздовжній розріз і потік S уздовж діелектрика
    f.append(rect(390, 50, 350, 275, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(565, 75, "Поздовжній потік електромагнітної енергії", size=13, bold=True))

    # Провідник верхній (внутрішній)
    f.append(rect(420, 105, 290, 20, fill="#cbd5e1", stroke=INK, sw=1.8))
    f.append(text(565, 119, "Внутрішній провідник (+I)", size=11, bold=True))

    # Провідник нижній (зовнішній екран)
    f.append(rect(420, 245, 290, 20, fill="#cbd5e1", stroke=INK, sw=1.8))
    f.append(text(565, 259, "Зовнішній провідник (−I)", size=11, bold=True))

    # Діелектрик між ними
    f.append(rect(420, 125, 290, 120, fill="#fffbe6", stroke="none"))
    f.append(text(460, 232, "Діелектрик (ізоляція)", size=11, color=MUTED, anchor="start"))

    # Вектори E від верхнього до нижнього провідника (з відступом від стінок)
    for x_p in [480, 560, 640]:
        f.append(arrow(x_p, 128, x_p, 242, color="#dc2626", sw=1.5))
        f.append(text(x_p - 14, 185, "E", size=11, bold=True, color="#dc2626"))

    # Стрілки вектора Пойнтінга S уздовж діелектрика на y=155
    f.append(arrow(430, 155, 500, 155, color="#d97706", sw=2.5))
    f.append(arrow(510, 155, 580, 155, color="#d97706", sw=2.5))
    f.append(arrow(590, 155, 670, 155, color="#d97706", sw=2.5))
    f.append(text(565, 143, "Вектор Пойнтінга S (потік енергії)", size=12, bold=True, color="#b91c1c"))

    f.append(text(565, 298, "Енергія тече в ДІЕЛЕКТРИКУ, а не всередині міді!", size=11, bold=True, color="#1e40af"))

    return render(os.path.join(IMG, "poynting-flow.svg"), W, H, *f)


def fig_reflections_wavefront():
    """Фігура 4: Профіль напруги при відбитті в трьох режимах навантаження."""
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Відбиття хвиль та формування стоячих хвиль у лінії передачі", size=16, bold=True))

    panels = [
        ("Узгоджене навантаження: Z_L = Z_0 (Γ = 0)", "Біжуча хвиля без відбиття. Вся енергія поглинається.", "#16a34a", 0),
        ("Холостий хід: Z_L = ∞ (Γ = +1)", "Відбиття у фазі: вузол струму, пучність напруги (V_max = 2 V₀).", "#2563eb", 1),
        ("Коротке замикання: Z_L = 0 (Γ = −1)", "Відбиття у протифазі: вузол напруги (V = 0), пучність струму.", "#dc2626", 2)
    ]

    p_w, p_h = 700, 100
    y_start = 52

    for title, desc, col, idx in panels:
        py = y_start + idx * 118
        f.append(rect(30, py, p_w, p_h, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=8))
        f.append(text(45, py + 20, title, size=13, bold=True, color=col, anchor="start"))
        f.append(text(45, py + 36, desc, size=11, color=MUTED, anchor="start"))

        # Осі координат
        ox1, ox2 = 380, 710
        oy = py + 65
        f.append(line(ox1, oy, ox2, oy, color=MUTED, sw=1, dash="2,2"))

        # Графік напруги для шкірного випадку
        pts = []
        if idx == 0:
            # Узгоджене Z_L = Z_0: постійна амплітуда біжучої хвилі
            for i in range(ox2 - ox1 + 1):
                x = ox1 + i
                y = oy - 22 * math.sin(i * 0.04)
                pts.append((x, y))
            f.append(polyline(pts, color=col, sw=2))
        elif idx == 1:
            # Холостий хід Z_L = inf: пучність на кінці (x = ox2)
            for i in range(ox2 - ox1 + 1):
                x = ox1 + i
                dist_from_end = ox2 - x
                y = oy - 35 * math.cos(dist_from_end * 0.04)
                pts.append((x, y))
            f.append(polyline(pts, color=col, sw=2))
            f.append(circle(ox2, oy - 35, 4, fill=col, stroke='none'))
            f.append(text(ox2 - 35, oy - 38, "2·V₀", size=10, bold=True, color=col))
        else:
            # Коротке замикання Z_L = 0: вузол на кінці (x = ox2)
            for i in range(ox2 - ox1 + 1):
                x = ox1 + i
                dist_from_end = ox2 - x
                y = oy - 35 * math.sin(dist_from_end * 0.04)
                pts.append((x, y))
            f.append(polyline(pts, color=col, sw=2))
            f.append(circle(ox2, oy, 4, fill=col, stroke='none'))
            f.append(text(ox2 - 35, oy + 15, "V = 0", size=10, bold=True, color=col))

    return render(os.path.join(IMG, "reflections-wavefront.svg"), W, H, *f)


def fig_line_geometries():
    """Фігура 5: Поперечні перерізи та силові лінії 4 основних геометричних типів ліній."""
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Геометричні типи ліній передачі та їх характерні імпеданси", size=16, bold=True))

    boxes = [
        ("а) Коаксіальний кабель", "Z₀ = (60 / √ε_r) · ln(D/d)", "Екранована симетрія", 30, 50),
        ("б) Двопровідна лінія (вита пара)", "Z₀ = (120 / √ε_r) · arcosh(D/d)", "Симетрична відкрита", 390, 50),
        ("в) Мікросмужкова лінія (PCB)", "Z₀ ≈ (87 / √(ε_r+1.41)) · ln(...)", "Планарна квазі-ТЕМ", 30, 200),
        ("г) Плоский хвилевід (двообкладний)", "Z₀ = (377 / √ε_r) · (h / w)", "Однорідне поле E", 390, 200)
    ]

    for title, formula, tag, bx, by in boxes:
        f.append(rect(bx, by, 340, 140, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=8))
        f.append(text(bx + 15, by + 22, title, size=13, bold=True, anchor="start", color="#1e40af"))
        f.append(text(bx + 15, by + 40, formula, size=11, bold=True, anchor="start", color="#b91c1c"))
        f.append(text(bx + 15, by + 56, tag, size=10, color=MUTED, anchor="start"))

        # Схематичний рисунок перерізу справа в боксі
        cx = bx + 260
        cy = by + 85

        if "Коаксіальний" in title:
            f.append(circle(cx, cy, 35, fill="#e2e8f0", stroke=INK, sw=1.8))
            f.append(circle(cx, cy, 12, fill="#94a3b8", stroke=INK, sw=1.5))
            f.append(line(cx - 12, cy, cx + 12, cy, color=LINE, sw=1))
            f.append(line(cx, cy - 12, cx, cy + 12, color=LINE, sw=1))
        elif "Двопровідна" in title:
            f.append(circle(cx - 25, cy, 14, fill="#94a3b8", stroke=INK, sw=1.5))
            f.append(circle(cx + 25, cy, 14, fill="#94a3b8", stroke=INK, sw=1.5))
            f.append(line(cx - 11, cy, cx + 11, cy, color=MUTED, sw=1, dash="2,2"))
            f.append(text(cx, cy - 6, "D", size=10, color=MUTED))
        elif "Мікросмужкова" in title:
            # Земляна площина
            f.append(rect(cx - 45, cy + 15, 90, 8, fill="#64748b", stroke=INK, sw=1.2))
            # Діелектрик
            f.append(rect(cx - 45, cy - 15, 90, 30, fill="#fef3c7", stroke=FIELD, sw=1))
            # Доріжка
            f.append(rect(cx - 15, cy - 20, 30, 5, fill="#b91c1c", stroke=INK, sw=1.2))
        else:
            # Двообкладний
            f.append(rect(cx - 40, cy - 25, 80, 6, fill="#64748b", stroke=INK, sw=1.2))
            f.append(rect(cx - 40, cy + 19, 80, 6, fill="#64748b", stroke=INK, sw=1.2))
            for xp in [-25, 0, 25]:
                f.append(arrow(cx + xp, cy - 18, cx + xp, cy + 18, color="#dc2626", sw=1.2))

    return render(os.path.join(IMG, "poynting-flow.svg"), W, H, *f)


if __name__ == '__main__':
    fig_lumped_vs_distributed()
    fig_telegrapher_element()
    fig_poynting_flow()
    fig_reflections_wavefront()
    fig_line_geometries()
    print("Всі 5 фігур успішно згенеровано у ./img/")
