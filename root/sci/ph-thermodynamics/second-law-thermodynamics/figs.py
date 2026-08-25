# -*- coding: utf-8 -*-
"""Фігури до теми «Другий закон термодинаміки (Клаузіус, Кельвін, Планк)».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"
COLOR_PURPLE = "#8e44ad"
COLOR_DARK = "#2c3e50"
COLOR_GRAY = "#6b7280"


def polyline(pts, color=LINE, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{pts_str}" fill="none" stroke="{color}" stroke-width="{sw:.1f}"{d}/>'


def render_svg(filename, width, height, elements):
    """Компонує елементи у повноцінний SVG із макером стрілки."""
    svg_defs = f"""<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M 0 1 L 10 5 L 0 9 z" fill="{LINE}" />
  </marker>
</defs>"""
    content = '\n'.join(elements)
    full_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
{svg_defs}
{content}
</svg>"""
    filepath = os.path.join(IMG_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_svg)
    print(f"Записано {filepath}")


# ── Фігура 1: Еквівалентність формулювань Клаузіуса та Кельвіна-Планка ────────
def fig_formulations_equivalence():
    W, H = 780, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 25, "Схематичне доведення еквівалентності формулювань другого закону", size=15, bold=True, color=COLOR_DARK))

    # Ліва частина: Гіпотетичне порушення Клаузіуса
    f.append(text(200, 55, "Порушення Клаузіуса → Порушення Кельвіна", size=13, bold=True, color=COLOR_DARK))
    
    # Резервуари ліворуч
    f.append(fitbox(60, 80, 280, 45, "Гарячий резервуар T_1 (висока температура)", size=11, fill="#fee2e2", stroke=COLOR_RED, sw=1.5, bold=True))
    f.append(fitbox(60, 350, 280, 45, "Холодний резервуар T_2 (низька температура)", size=11, fill="#e0f2fe", stroke=COLOR_BLUE, sw=1.5, bold=True))

    # Холодильник (порушує Клаузіуса: передає Q2 без роботи W)
    f.append(fitbox(75, 190, 110, 95, "Гіпотетична\nмашина C\n(без W_in)\nQ_2: T_2 → T_1", size=11, fill="#fef3c7", stroke=COLOR_ORANGE, sw=2, bold=True))

    # Звичайна теплова машина E (бере Q1, віддає Q2, виконує W)
    f.append(fitbox(215, 190, 110, 95, "Теплова\nмашина E\n(звичайна)\nККД η", size=11, fill="#f0fdf4", stroke=COLOR_GREEN, sw=2, bold=True))

    # Стрілки лівої частини
    f.append(arrow(130, 350, 130, 285, color=COLOR_BLUE, sw=2))
    f.append(arrow(130, 190, 130, 125, color=COLOR_RED, sw=2))
    f.append(text(105, 315, "Q_2", size=11, color=COLOR_BLUE, bold=True))
    f.append(text(105, 155, "Q_2", size=11, color=COLOR_RED, bold=True))

    f.append(arrow(270, 125, 270, 190, color=COLOR_RED, sw=2))
    f.append(arrow(270, 285, 270, 350, color=COLOR_BLUE, sw=2))
    f.append(arrow(325, 237, 365, 237, color=COLOR_GREEN, sw=2))
    f.append(text(295, 155, "Q_1", size=11, color=COLOR_RED, bold=True))
    f.append(text(295, 315, "Q_2", size=11, color=COLOR_BLUE, bold=True))
    f.append(text(345, 222, "W", size=11, color=COLOR_GREEN, bold=True))

    # Права частина: Об'єднана машина (Вічний двигун 2-го роду)
    f.append(text(580, 55, "Результат об'єднання систем C + E", size=13, bold=True, color=COLOR_DARK))

    f.append(fitbox(440, 80, 280, 45, "Гарячий резервуар T_1", size=11, fill="#fee2e2", stroke=COLOR_RED, sw=1.5, bold=True))
    f.append(fitbox(440, 350, 280, 45, "Холодний резервуар T_2 (не бере участі!)", size=11, fill="#f3f4f6", stroke=COLOR_GRAY, sw=1.5, bold=False))

    f.append(fitbox(500, 190, 160, 95, "Об'єднаний двигун\nC + E\n(єдине джерело T_1)", size=12, fill="#fef2f2", stroke=COLOR_RED, sw=2, bold=True))

    f.append(arrow(580, 125, 580, 190, color=COLOR_RED, sw=2.5))
    f.append(arrow(660, 237, 725, 237, color=COLOR_GREEN, sw=2.5))
    f.append(text(530, 155, "Q_net = Q_1 - Q_2", size=11, color=COLOR_RED, bold=True))
    f.append(text(692, 222, "W = Q_net", size=11, color=COLOR_GREEN, bold=True))

    # Пояснення знизу
    f.append(text(W / 2, 415, "Перенесення Q_2 без роботи від T_2 до T_1 дозволяє замкнути потік і перетворити Q_1 - Q_2 на роботу W без передачі тепла T_2.", size=10, color=COLOR_DARK))

    render_svg("formulations-equivalence.svg", W, H, f)


# ── Фігура 2: Цикл Карно на P-V та T-S діаграмах ─────────────────────────────
def fig_carnot_cycle_diagram():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 22, "Цикл Карно: ізотерми та адіабати на P-V та T-S діаграмах", size=15, bold=True, color=COLOR_DARK))

    # === Ліва діаграма P-V ===
    ox1, oy1 = 60, 360
    gw1, gh1 = 280, 280

    f.append(text(ox1 + gw1 / 2, 52, "P-V діаграма (робота W = ∫ P dV)", size=12, bold=True, color=COLOR_DARK))
    f.append(line(ox1, oy1, ox1 + gw1, oy1, color=LINE, sw=1.5))
    f.append(line(ox1, oy1, ox1, oy1 - gh1, color=LINE, sw=1.5))
    f.append(arrow(ox1, oy1, ox1 + gw1 + 15, oy1, color=LINE, sw=1.5))
    f.append(arrow(ox1, oy1, ox1, oy1 - gh1 - 15, color=LINE, sw=1.5))
    f.append(text(ox1 + gw1 + 10, oy1 + 18, "V", size=12, bold=True))
    f.append(text(ox1 - 15, oy1 - gh1 - 5, "P", size=12, bold=True))

    # Точки циклу P-V
    p1 = (ox1 + 50, oy1 - 230)
    p2 = (ox1 + 140, oy1 - 180)
    p3 = (ox1 + 250, oy1 - 60)
    p4 = (ox1 + 130, oy1 - 90)

    # Заповнена площа циклу
    cycle_pts = f"{p1[0]},{p1[1]} {p2[0]},{p2[1]} {p3[0]},{p3[1]} {p4[0]},{p4[1]}"
    f.append(f'<polygon points="{cycle_pts}" fill="#f0fdf4" stroke="{COLOR_GREEN}" stroke-width="1" />')

    # Криві
    f.append(polyline([p1, (ox1 + 90, oy1 - 200), p2], color=COLOR_RED, sw=2))
    f.append(polyline([p2, (ox1 + 200, oy1 - 110), p3], color=COLOR_BLUE, sw=2))
    f.append(polyline([p3, (ox1 + 180, oy1 - 70), p4], color=COLOR_BLUE, sw=2, dash="4,4"))
    f.append(polyline([p4, (ox1 + 80, oy1 - 150), p1], color=COLOR_RED, sw=2, dash="4,4"))

    # Позначки точок
    f.append(circle(p1[0], p1[1], 4, fill=COLOR_DARK))
    f.append(circle(p2[0], p2[1], 4, fill=COLOR_DARK))
    f.append(circle(p3[0], p3[1], 4, fill=COLOR_DARK))
    f.append(circle(p4[0], p4[1], 4, fill=COLOR_DARK))

    f.append(text(p1[0] - 12, p1[1] - 8, "1", size=11, bold=True))
    f.append(text(p2[0] + 10, p2[1] - 8, "2", size=11, bold=True))
    f.append(text(p3[0] + 10, p3[1] + 10, "3", size=11, bold=True))
    f.append(text(p4[0] - 12, p4[1] + 12, "4", size=11, bold=True))

    # Написи тепла
    f.append(text(ox1 + 95, oy1 - 215, "Q_1 (T_1)", size=10, bold=True, color=COLOR_RED))
    f.append(text(ox1 + 185, oy1 - 45, "Q_2 (T_2)", size=10, bold=True, color=COLOR_BLUE))
    f.append(text(ox1 + 135, oy1 - 135, "W", size=13, bold=True, color=COLOR_GREEN))


    # === Права діаграма T-S ===
    ox2, oy2 = 450, 360
    gw2, gh2 = 280, 280

    f.append(text(ox2 + gw2 / 2, 52, "T-S діаграма (Прямокутник Карно)", size=12, bold=True, color=COLOR_DARK))
    f.append(line(ox2, oy2, ox2 + gw2, oy2, color=LINE, sw=1.5))
    f.append(line(ox2, oy2, ox2, oy2 - gh2, color=LINE, sw=1.5))
    f.append(arrow(ox2, oy2, ox2 + gw2 + 15, oy2, color=LINE, sw=1.5))
    f.append(arrow(ox2, oy2, ox2, oy2 - gh2 - 15, color=LINE, sw=1.5))
    f.append(text(ox2 + gw2 + 10, oy2 + 18, "S", size=12, bold=True))
    f.append(text(ox2 - 15, oy2 - gh2 - 5, "T", size=12, bold=True))

    # Точки T-S (Прямокутник!)
    ts1 = (ox2 + 70, oy2 - 210)
    ts2 = (ox2 + 220, oy2 - 210)
    ts3 = (ox2 + 220, oy2 - 80)
    ts4 = (ox2 + 70, oy2 - 80)

    # Площа прямокутника (Корисна робота W)
    ts_pts = f"{ts1[0]},{ts1[1]} {ts2[0]},{ts2[1]} {ts3[0]},{ts3[1]} {ts4[0]},{ts4[1]}"
    f.append(f'<polygon points="{ts_pts}" fill="#f0fdf4" stroke="{COLOR_GREEN}" stroke-width="1.5" />')

    # Площа під T2 (Втрачене тепло Q2)
    q2_pts = f"{ts4[0]},{ts4[1]} {ts3[0]},{ts3[1]} {ts3[0]},{oy2} {ts4[0]},{oy2}"
    f.append(f'<polygon points="{q2_pts}" fill="#e0f2fe" stroke="{COLOR_BLUE}" stroke-width="1" stroke-dasharray="3,3" />')

    # Сторони прямокутника зі стрілками процесу
    f.append(arrow(ts1[0], ts1[1], ts2[0], ts2[1], color=COLOR_RED, sw=2))
    f.append(arrow(ts2[0], ts2[1], ts3[0], ts3[1], color=COLOR_DARK, sw=2))
    f.append(arrow(ts3[0], ts3[1], ts4[0], ts4[1], color=COLOR_BLUE, sw=2))
    f.append(arrow(ts4[0], ts4[1], ts1[0], ts1[1], color=COLOR_DARK, sw=2))

    # Позначки точок
    f.append(circle(ts1[0], ts1[1], 4, fill=COLOR_DARK))
    f.append(circle(ts2[0], ts2[1], 4, fill=COLOR_DARK))
    f.append(circle(ts3[0], ts3[1], 4, fill=COLOR_DARK))
    f.append(circle(ts4[0], ts4[1], 4, fill=COLOR_DARK))

    f.append(text(ts1[0] - 12, ts1[1] - 8, "1", size=11, bold=True))
    f.append(text(ts2[0] + 10, ts1[1] - 8, "2", size=11, bold=True))
    f.append(text(ts3[0] + 10, ts3[1] + 12, "3", size=11, bold=True))
    f.append(text(ts4[0] - 12, ts4[1] + 12, "4", size=11, bold=True))

    # Температури й ентропії
    f.append(line(ox2 - 5, ts1[1], ts1[0], ts1[1], color=COLOR_GRAY, sw=1, dash="2,2"))
    f.append(line(ox2 - 5, ts4[1], ts4[0], ts4[1], color=COLOR_GRAY, sw=1, dash="2,2"))
    f.append(text(ox2 - 25, ts1[1] + 4, "T_1", size=11, bold=True, color=COLOR_RED))
    f.append(text(ox2 - 25, ts4[1] + 4, "T_2", size=11, bold=True, color=COLOR_BLUE))

    f.append(line(ts4[0], ts4[1], ts4[0], oy2 + 5, color=COLOR_GRAY, sw=1, dash="2,2"))
    f.append(line(ts3[0], ts3[1], ts3[0], oy2 + 5, color=COLOR_GRAY, sw=1, dash="2,2"))
    f.append(text(ts4[0] - 8, oy2 + 18, "S_1", size=11, bold=True))
    f.append(text(ts3[0] - 8, oy2 + 18, "S_2", size=11, bold=True))

    # Текст площ
    f.append(text(ts1[0] + 75, ts1[1] + 60, "W = ΔS · (T_1 - T_2)", size=11, bold=True, color=COLOR_GREEN))
    f.append(text(ts4[0] + 75, oy2 - 35, "Q_2 = T_2 · ΔS", size=10, bold=True, color=COLOR_BLUE))

    render_svg("carnot-cycle-diagram.svg", W, H, f)


# ── Фігура 3: Статистична природа ентропії (розширення та мікростани) ────────
def fig_entropy_statistical_microstates():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 22, "Мікроскопічний зміст ентропії: спонтанний перехід до максимальної ймовірності", size=15, bold=True, color=COLOR_DARK))

    # Стан 1: Впорядкований (Низька ентропія)
    f.append(text(190, 55, "Початковий стан (Низька ентропія S_1)", size=12, bold=True, color=COLOR_DARK))
    f.append(rect(40, 80, 300, 220, fill="#f8fafc", stroke=COLOR_DARK, sw=2, rx=4))
    f.append(line(190, 80, 190, 300, color=COLOR_RED, sw=2, dash="4,4"))
    f.append(text(190, 315, "Перегородка", size=10, color=COLOR_RED))

    # Молекули зліва (16 молекул)
    molecules_left = [
        (70, 110), (100, 130), (130, 100), (160, 120),
        (80, 170), (120, 160), (150, 180), (75, 220),
        (110, 210), (145, 235), (85, 270), (130, 265),
        (165, 275), (60, 150), (105, 240), (155, 140)
    ]
    for mx, my in molecules_left:
        f.append(circle(mx, my, 5, fill=COLOR_BLUE, stroke=COLOR_DARK, sw=1))

    f.append(fitbox(50, 340, 280, 60, "Молекули зосереджені в одній половині\nМала кількість мікростанів W_1\nФормула Больцмана: S_1 = k_B · ln(W_1)", size=10, fill="#eff6ff", stroke=COLOR_BLUE, sw=1))

    # Стрілка спонтанного процесу
    f.append(arrow(355, 190, 425, 190, color=COLOR_GREEN, sw=3))
    f.append(text(390, 165, "Незворотне", size=10, bold=True, color=COLOR_GREEN))
    f.append(text(390, 180, "розширення", size=10, bold=True, color=COLOR_GREEN))

    # Стан 2: Рівноважний хаотичний (Висока ентропія)
    f.append(text(590, 55, "Рівноважний стан (Максимальна ентропія S_2)", size=12, bold=True, color=COLOR_DARK))
    f.append(rect(440, 80, 300, 220, fill="#f8fafc", stroke=COLOR_DARK, sw=2, rx=4))

    # Молекули розподілені по всьому об'єму (16 молекул)
    molecules_mixed = [
        (470, 110), (520, 130), (580, 100), (630, 120), (680, 150),
        (480, 170), (540, 160), (610, 180), (670, 210), (710, 260),
        (460, 240), (510, 265), (560, 220), (620, 275), (660, 280), (700, 115)
    ]
    for mx, my in molecules_mixed:
        f.append(circle(mx, my, 5, fill=COLOR_PURPLE, stroke=COLOR_DARK, sw=1))

    f.append(fitbox(450, 340, 280, 60, "Рівномірне заповнення всього об'єму V_2\nГігантське число мікростанів W_2 >> W_1\nПриріст ентропії: ΔS = S_2 - S_1 > 0", size=10, fill="#f3e8ff", stroke=COLOR_PURPLE, sw=1))

    render_svg("entropy-statistical-microstates.svg", W, H, f)


if __name__ == '__main__':
    fig_formulations_equivalence()
    fig_carnot_cycle_diagram()
    fig_entropy_statistical_microstates()
