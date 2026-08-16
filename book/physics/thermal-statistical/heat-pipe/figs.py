# -*- coding: utf-8 -*-
"""Фігури до теми «Теплова трубка».
Запуск: python figs.py -> створює SVG у ./img/
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

# Палітра кольорів
HOT_COLOR  = "#c0392b"  # Гаряче / випаровувач
COLD_COLOR = "#2457d6"  # Холодне / конденсатор
VAPOR_FILL = "#fcf3cf"  # Заливка парового ядра
WICK_FILL  = "#e5c7b6"  # Заливка фітиля (мідна пудра)
METAL_FILL = "#d35400"  # Стінка мідної трубки
LINE_COLOR = "#2c3e50"


# ── 1. Схема двофазного циклу теплової трубки ─────────────────────────────────
def fig_heat_pipe_cycle():
    W, H = 840, 440
    frags = []

    # Заголовок фігури
    frags.append(text(W / 2, 28, "Замкнений двофазний цикл теплової трубки", size=16, bold=True))

    # Зони: Випаровувач (60..280), Адіабатична (280..560), Конденсатор (560..780)
    y_top = 110
    pipe_h = 220
    y_bot = y_top + pipe_h
    wick_t = 35
    wall_t = 12

    # Фон зон
    frags.append(rect(60, y_top - 40, 210, 24, fill="#fadbd8", stroke="none", rx=3))
    frags.append(text(165, y_top - 24, "Зона випаровування", size=12, color=HOT_COLOR, bold=True))

    frags.append(rect(295, y_top - 40, 250, 24, fill="#eaeded", stroke="none", rx=3))
    frags.append(text(420, y_top - 24, "Адіабатична зона", size=12, color=LINE_COLOR, bold=True))

    frags.append(rect(570, y_top - 40, 210, 24, fill="#d4e6f1", stroke="none", rx=3))
    frags.append(text(675, y_top - 24, "Зона конденсації", size=12, color=COLD_COLOR, bold=True))

    # Металева стінка (зовнішня оболонка)
    frags.append(rect(60, y_top, 720, pipe_h, fill="#fbeee6", stroke=METAL_FILL, sw=2.5, rx=8))

    # Шар фітиля (верхній та нижній)
    frags.append(rect(60, y_top + wall_t, 720, wick_t, fill=WICK_FILL, stroke="#b03a2e", sw=1.0))
    frags.append(rect(60, y_bot - wall_t - wick_t, 720, wick_t, fill=WICK_FILL, stroke="#b03a2e", sw=1.0))

    # Парове ядро (центр)
    v_y1 = y_top + wall_t + wick_t
    v_h = pipe_h - 2 * (wall_t + wick_t)
    frags.append(rect(60, v_y1, 720, v_h, fill=VAPOR_FILL, stroke="#f39c12", sw=1.2, rx=4))

    # Потік пари (велика стрілка вправо)
    frags.append(arrow(140, v_y1 + v_h / 2, 700, v_y1 + v_h / 2, color="#e67e22", sw=3.5))
    frags.append(text(420, v_y1 + v_h / 2 - 12, "Потік пари (ΔP_v)", size=13, color="#d35400", bold=True))

    # Повернення рідини у фітилі (стрілки вліво)
    frags.append(arrow(700, y_top + wall_t + wick_t / 2, 140, y_top + wall_t + wick_t / 2, color=COLD_COLOR, sw=2.5))
    frags.append(text(420, y_top + wall_t + wick_t / 2 + 4, "Капілярне повернення рідини у фітилі", size=11, color=COLD_COLOR, bold=True))

    frags.append(arrow(700, y_bot - wall_t - wick_t / 2, 140, y_bot - wall_t - wick_t / 2, color=COLD_COLOR, sw=2.5))
    frags.append(text(420, y_bot - wall_t - wick_t / 2 + 4, "Капілярне повернення рідини у фітилі", size=11, color=COLD_COLOR, bold=True))

    # Підведення тепла (Q_in) знизу ліворуч (y_bot + 65 до y_bot + 5)
    frags.append(arrow(165, y_bot + 65, 165, y_bot + 5, color=HOT_COLOR, sw=3.5))
    frags.append(text(165, y_bot + 82, "Тепловий вхід Q_in", size=13, color=HOT_COLOR, bold=True))

    # Відведення тепла (Q_out) знизу праворуч (y_bot + 5 до y_bot + 65)
    frags.append(arrow(675, y_bot + 5, 675, y_bot + 65, color=COLD_COLOR, sw=3.5))
    frags.append(text(675, y_bot + 82, "Тепловий вихід Q_out", size=13, color=COLD_COLOR, bold=True))

    # Пунктирні розділювачі зон
    frags.append(line(285, y_top - 40, 285, y_bot + 20, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(555, y_top - 40, 555, y_bot + 20, color=MUTED, sw=1.5, dash="4,4"))

    render(os.path.join(IMG_DIR, "heat-pipe-cycle.svg"), W, H, *frags)


# ── 2. Профіль тиску пари та рідини ───────────────────────────────────────────
def fig_pressure_profile():
    W, H = 800, 460
    frags = []

    frags.append(text(W / 2, 28, "Розподіл тиску у паровій та рідкій фазах вздовж трубки", size=16, bold=True))

    # Осі координат
    x0, y0 = 90, 380
    x_len = 660
    y_len = 310

    frags.append(arrow(x0, y0, x0 + x_len + 20, y0, color=LINE_COLOR, sw=2))
    frags.append(text(x0 + x_len + 10, y0 + 25, "Координата вздовж трубки (x)", size=12, bold=True))

    frags.append(arrow(x0, y0, x0, y0 - y_len - 10, color=LINE_COLOR, sw=2))
    frags.append(text(x0 - 25, y0 - y_len - 5, "Тиск (P)", size=12, bold=True))

    # Межі зон (x_evap=280, x_adiab=520, x_cond=720)
    x_e = x0 + 190
    x_a = x0 + 430
    x_c = x0 + 630

    frags.append(line(x_e, y0, x_e, y0 - y_len, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(line(x_a, y0, x_a, y0 - y_len, color=MUTED, sw=1.2, dash="3,3"))

    frags.append(text((x0 + x_e) / 2, y0 + 20, "Випаровувач", size=12, color=HOT_COLOR, bold=True))
    frags.append(text((x_e + x_a) / 2, y0 + 20, "Адіабатична", size=12, color=LINE_COLOR, bold=True))
    frags.append(text((x_a + x_c) / 2, y0 + 20, "Конденсатор", size=12, color=COLD_COLOR, bold=True))

    # Крива тиску пари P_v(x) (зверху, опускається від випаровувача до конденсатора)
    pv_points = f"M {x0},{y0-240} Q {x_e},{y0-230} {x_a},{y0-210} T {x_c},{y0-190}"
    frags.append(f'<path d="{pv_points}" fill="none" stroke="#e67e22" stroke-width="3"/>')
    frags.append(text(x0 + 80, y0 - 255, "Тиск пари P_v(x)", size=13, color="#d35400", bold=True))

    # Крива тиску рідини P_l(x) (знизу, спадає у напрямку випаровувача)
    pl_points = f"M {x0},{y0-70} Q {x_e},{y0-100} {x_a},{y0-140} T {x_c},{y0-185}"
    frags.append(f'<path d="{pl_points}" fill="none" stroke="{COLD_COLOR}" stroke-width="3"/>')
    frags.append(text(x0 + 80, y0 - 45, "Тиск рідини P_l(x)", size=13, color=COLD_COLOR, bold=True))

    # Капілярний стрибок тиску ΔP_cap у випаровувачі
    frags.append(arrow(x0 + 20, y0 - 75, x0 + 20, y0 - 235, color=POS, sw=2.5))
    frags.append(text(x0 + 45, y0 - 150, "ΔP_cap,max", size=13, color=POS, bold=True))
    frags.append(text(x0 + 45, y0 - 132, "(Лапласів помп)", size=11, color=POS))

    # Малий перепад у конденсатора
    frags.append(line(x_c, y0 - 190, x_c, y0 - 185, color=MUTED, sw=1.5))

    render(os.path.join(IMG_DIR, "pressure-profile.svg"), W, H, *frags)


# ── 3. Порівняння мікроструктур фітилів ───────────────────────────────────────
def fig_wick_types():
    W, H = 840, 360
    frags = []

    frags.append(text(W / 2, 26, "Основні типи конструкції фітилів (Wick Structures)", size=16, bold=True))

    box_w = 240
    box_h = 260
    y_b = 65

    # Панель 1: Канавки
    x1 = 30
    frags.append(rect(x1, y_b, box_w, box_h, fill="#fafafa", stroke=LINE_COLOR, sw=1.5, rx=6))
    frags.append(text(x1 + box_w/2, y_b + 25, "а) Поздовжні канавки", size=14, bold=True, color=LINE_COLOR))
    # Малюємо канавки
    for i in range(5):
        gx = x1 + 30 + i * 40
        frags.append(rect(gx, y_b + 60, 22, 100, fill="#e8f8f5", stroke="#16a085", sw=1.5))
    frags.append(text(x1 + box_w/2, y_b + 185, "Проникність K: ВЕЛИКА", size=11, color=FIELD, bold=True))
    frags.append(text(x1 + box_w/2, y_b + 205, "Радіус por r_eff: ВЕЛИКИЙ", size=11, color=POS, bold=True))
    frags.append(text(x1 + box_w/2, y_b + 230, "Чудово для гравітації", size=11, color=MUTED))

    # Панель 2: Сітка
    x2 = 300
    frags.append(rect(x2, y_b, box_w, box_h, fill="#fafafa", stroke=LINE_COLOR, sw=1.5, rx=6))
    frags.append(text(x2 + box_w/2, y_b + 25, "б) Дротяна сітка (Mesh)", size=14, bold=True, color=LINE_COLOR))
    # Малюємо сітку
    for row in range(4):
        for col in range(5):
            cx = x2 + 35 + col * 40
            cy = y_b + 70 + row * 25
            frags.append(circle(cx, cy, 8, fill="#ebf5fb", stroke=COLD_COLOR, sw=1.2))
    frags.append(text(x2 + box_w/2, y_b + 185, "Проникність K: СЕРЕДНЯ", size=11, color=LINE_COLOR, bold=True))
    frags.append(text(x2 + box_w/2, y_b + 205, "Радіус por r_eff: СЕРЕДНІЙ", size=11, color=LINE_COLOR, bold=True))
    frags.append(text(x2 + box_w/2, y_b + 230, "Гнучка, універсальна", size=11, color=MUTED))

    # Панель 3: Спечена пудра
    x3 = 570
    frags.append(rect(x3, y_b, box_w, box_h, fill="#fafafa", stroke=LINE_COLOR, sw=1.5, rx=6))
    frags.append(text(x3 + box_w/2, y_b + 25, "в) Спечена мідна пудра", size=14, bold=True, color=LINE_COLOR))
    # Малюємо гранули
    dots = [
        (40,65), (70,75), (100,65), (130,80), (160,70), (190,85),
        (50,100), (85,105), (120,98), (155,110), (180,100),
        (40,135), (75,130), (110,140), (145,132), (185,138)
    ]
    for dx, dy in dots:
        frags.append(circle(x3 + dx, y_b + dy, 12, fill=WICK_FILL, stroke=METAL_FILL, sw=1.2))
    frags.append(text(x3 + box_w/2, y_b + 185, "Проникність K: НИЗЬКА", size=11, color=POS, bold=True))
    frags.append(text(x3 + box_w/2, y_b + 205, "Радіус por r_eff: ДРІБНИЙ", size=11, color=FIELD, bold=True))
    frags.append(text(x3 + box_w/2, y_b + 230, "Максимальний тиск помпа", size=11, color=HOT_COLOR, bold=True))

    render(os.path.join(IMG_DIR, "wick-types.svg"), W, H, *frags)


# ── 4. Фізичні обмеження теплопереносу ────────────────────────────────────────
def fig_operating_limits():
    W, H = 800, 480
    frags = []

    frags.append(text(W / 2, 28, "П'ять фізичних обмежень теплопереносу Q_max(T)", size=16, bold=True))

    x0, y0 = 90, 400
    x_len = 660
    y_len = 330

    frags.append(arrow(x0, y0, x0 + x_len + 20, y0, color=LINE_COLOR, sw=2))
    frags.append(text(x0 + x_len + 10, y0 + 25, "Робоча температура (T)", size=12, bold=True))

    frags.append(arrow(x0, y0, x0, y0 - y_len - 10, color=LINE_COLOR, sw=2))
    frags.append(text(x0 - 25, y0 - y_len - 5, "Теплова потужність (Q_max)", size=12, bold=True))

    # Огинаюча крива обмежень Q_max(T)
    # Зони: В'язкісний (1), Звуковий (2), Капілярний (3), Винесення (4), Кипійний (5)
    path_d = (f"M {x0+20},{y0-30} "
              f"C {x0+60},{y0-120} {x0+90},{y0-220} {x0+150},{y0-250} "  # Звуковий/В'язкісний
              f"C {x0+250},{y0-290} {x0+400},{y0-300} {x0+500},{y0-260} " # Капілярний
              f"C {x0+560},{y0-220} {x0+600},{y0-130} {x0+630},{y0-40}")   # Кипійний

    frags.append(f'<path d="{path_d}" fill="#f4f6f8" stroke="{LINE_COLOR}" stroke-width="3.5"/>')

    # Підписи зон на кривій
    frags.append(text(x0 + 40, y0 - 80, "1. В'язкісний", size=11, color="#8e44ad", bold=True))
    frags.append(text(x0 + 110, y0 - 180, "2. Звуковий", size=11, color="#2980b9", bold=True))
    frags.append(text(x0 + 320, y0 - 315, "3. Капілярний ліміт (робоче плато)", size=13, color=FIELD, bold=True))
    frags.append(text(x0 + 520, y0 - 230, "4. Винесення", size=11, color="#e67e22", bold=True))
    frags.append(text(x0 + 600, y0 - 100, "5. Кипійний", size=11, color=HOT_COLOR, bold=True))

    # Робочий діапазон (затенення)
    frags.append(rect(x0 + 160, y0 - 280, 360, 275, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(x0 + 340, y0 - 150, "ОПТИМАЛЬНИЙ РОБОЧИЙ ДІАПАЗОН", size=14, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "operating-limits.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_heat_pipe_cycle()
    fig_pressure_profile()
    fig_wick_types()
    fig_operating_limits()
    print("Усі фігури успішно згенеровано у ./img/")
