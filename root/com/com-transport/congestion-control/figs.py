# -*- coding: utf-8 -*-
import sys, os
# Підключаємо svgkit із кореневої папки scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── ФІГ.1 Congestion Collapse vs Controlled Goodput ───────────────────────────
def fig_collapse():
    W, H = 760, 420
    p = []
    
    ox, oy = 90.0, 340.0
    gx_w, gy_h = 600.0, 260.0
    
    # Вісі координат
    p.append(line(ox, oy, ox + gx_w + 20, oy, color=INK, sw=2.0))
    p.append(line(ox, oy, ox, oy - gy_h - 20, color=INK, sw=2.0))
    
    p.append(text(ox + gx_w + 10, oy + 25, "Запропоноване навантаження (Offloaded Load)", size=12, color=INK, anchor="end", bold=True))
    p.append(text(ox - 15, oy - gy_h - 10, "Корисна пропускність (Goodput)", size=12, color=INK, anchor="start", bold=True))
    
    # Пропускна здатність C (пунктирна лінія)
    cap_y = oy - 200.0
    cap_x = ox + 220.0
    p.append(line(ox, cap_y, ox + gx_w, cap_y, color=MUTED, sw=1.5, dash="4 4"))
    p.append(text(ox + gx_w + 5, cap_y + 4, "Ємність C", size=11, color=MUTED, anchor="start", bold=True))
    
    # Ідеальна крива (до C, потім плато)
    p.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6 4"/>'
             % (ox, oy, cap_x, cap_y, ox + gx_w, cap_y, FIELD))
    p.append(text(ox + gx_w - 40, cap_y - 10, "Ідеал (без втрат)", size=11, color=FIELD, bold=True))
    
    # Крива з Управлінням Заторами (AIMD / BBR)
    # Плавний підйом до C і стабільність біля C
    p.append('<path d="M %.1f %.1f Q %.1f %.1f, %.1f %.1f T %.1f %.1f" fill="none" stroke="%s" stroke-width="3.0"/>'
             % (ox, oy, cap_x - 30, cap_y + 10, cap_x + 40, cap_y + 15, ox + gx_w, cap_y + 12, NEG))
    
    # Крива Колапсу заторів (Congestion Collapse - Drop Tail)
    # Росте до піку біля cap_x, далі стрімко падає до нуля
    p.append('<path d="M %.1f %.1f Q %.1f %.1f, %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="3.0"/>'
             % (ox, oy, cap_x - 40, cap_y + 30, cap_x, cap_y + 25, cap_x + 80, cap_y + 35, cap_x + 180, oy - 20, ox + gx_w, oy - 15, POS))
    
    # Мітки підписів для кривих
    b1, _, _ = textbox(ox + 360, oy - 55, "З керуванням заторами\n(AIMD / BBR — високий Goodput)", size=11, fill="#eaf0fd", stroke=NEG, pad=6)
    p.append(b1)
    
    b2, _, _ = textbox(ox + 450, oy - 165, "Катастрофічний колапс (Collapse)\n(Повторні передачі спалюють пропускність)", size=11, fill="#fdecea", stroke=POS, pad=6)
    p.append(b2)
    
    # Підсумковий пояснювальний блок
    b_note, _, _ = textbox(W / 2, 390, "При переповненні буферів невиправдані повторні передачі пакетів призводять до падіння корисного трафіку майже до нуля.", size=12, fill="#fff7ee", stroke=LINE)
    p.append(b_note)
    
    render(os.path.join(OUT, "congestion-collapse.svg"), W, H, *p,
           title="Колапс пропускної здатності мережі (Congestion Collapse)")


# ── ФІГ.2 Water-Filling (Max-Min Fairness) ───────────────────────────────────
def fig_water_filling():
    W, H = 760, 420
    p = []
    
    # Три ребра-пляшкові шийки (Bottlenecks)
    # Потік f1 іде через B1 (C1=4)
    # Потоки f2, f3 ідуть через B2 (C2=10)
    # Потоки f3, f4 ідуть через B3 (C3=8)
    
    bx = [140.0, 380.0, 620.0]
    by = 280.0
    bw = 140.0
    bh = 180.0
    
    capacities = [4, 10, 8]
    names = ["Ребро E1 (Ємність = 4)", "Ребро E2 (Ємність = 10)", "Ребро E3 (Ємність = 8)"]
    
    # Малювання судин ребер
    for x, cap, name in zip(bx, capacities, names):
        # Контур судини
        p.append(rect(x - bw/2, by - bh, bw, bh, fill="#f8fafc", stroke=MUTED, sw=2.0))
        p.append(text(x, by + 22, name, size=12, color=INK, bold=True))
    
    # Стовпчики потоків всередині судин
    # В E1: f1 (4) -> заповнено повністю
    p.append(rect(bx[0] - 45, by - 160, 90, 160, fill="#dbeafe", stroke=NEG, sw=1.5))
    p.append(text(bx[0], by - 80, "f1 = 4.0\n(Bottleneck)", size=12, color=NEG, bold=True))
    
    # В E2: f2 (6.0), f3 (4.0) -> сума 10
    p.append(rect(bx[1] - 60, by - 160, 55, 160, fill="#dcfce7", stroke=FIELD, sw=1.5))
    p.append(text(bx[1] - 32.5, by - 80, "f2 = 6.0", size=11, color=FIELD, bold=True))
    
    p.append(rect(bx[1] + 5, by - 106.6, 55, 106.6, fill="#fef3c7", stroke=POS, sw=1.5))
    p.append(text(bx[1] + 32.5, by - 53, "f3 = 4.0", size=11, color=POS, bold=True))
    
    # В E3: f3 (4.0), f4 (4.0) -> сума 8
    p.append(rect(bx[2] - 60, by - 106.6, 55, 106.6, fill="#fef3c7", stroke=POS, sw=1.5))
    p.append(text(bx[2] - 32.5, by - 53, "f3 = 4.0", size=11, color=POS, bold=True))
    
    p.append(rect(bx[2] + 5, by - 106.6, 55, 106.6, fill="#f3e8ff", stroke="#7e22ce", sw=1.5))
    p.append(text(bx[2] + 32.5, by - 53, "f4 = 4.0", size=11, color="#7e22ce", bold=True))
    
    # Рівні обмежень "Water-filling"
    p.append(line(bx[0] - bw/2 - 10, by - 160, bx[0] + bw/2 + 10, by - 160, color=POS, sw=2.0, dash="3 3"))
    p.append(text(bx[0] - bw/2 - 15, by - 160, "Межа E1", size=10, color=POS, anchor="end", bold=True))
    
    p.append(line(bx[1] - bw/2 - 10, by - 160, bx[1] + bw/2 + 10, by - 160, color=POS, sw=2.0, dash="3 3"))
    p.append(text(bx[1] - bw/2 - 15, by - 160, "Межа E2", size=10, color=POS, anchor="end", bold=True))
    
    # Пояснювальний текст знизу
    b_wf, _, _ = textbox(W / 2, 380,
                         "Алгоритм Water-Filling піднімає швидкості всіх потоків однаково, поки вузькі місця (Bottlenecks) не фіксують їх у порядку зростання.",
                         size=12, fill="#fff7ee", stroke=LINE)
    p.append(b_wf)
    
    render(os.path.join(OUT, "water-filling.svg"), W, H, *p,
           title="Максимально-мінімальна справедливість (Water-Filling Algorithm)")


# ── ФІГ.3 Network Utility Maximization (NUM / Kelly Dual) ─────────────────────
def fig_num_kelly_dual():
    W, H = 760, 400
    p = []
    
    # Лівий блок — Джерела трафіку (Sources)
    sx, sy, sw, sh = 140.0, 200.0, 200.0, 160.0
    p.append(rect(sx - sw/2, sy - sh/2, sw, sh, fill="#eff6ff", stroke=NEG, sw=2.0))
    p.append(text(sx, sy - sh/2 + 25, "ДЖЕРЕЛА (Sources)", size=14, color=NEG, bold=True))
    p.append(mtext(sx, sy, "Оптимізація корисності:\nmax U_i(x_i) - p_path * x_i\n\nАдаптація швидкостей x_i(t)", size=11, color=INK))
    
    # Правий блок — Мережеві Вузли/Ребра (Links)
    lx, ly, lw, lh = 620.0, 200.0, 200.0, 160.0
    p.append(rect(lx - lw/2, ly - lh/2, lw, lh, fill="#f0fdf4", stroke=FIELD, sw=2.0))
    p.append(text(lx, ly - lh/2 + 25, "ВУЗЛИ МЕРЕЖІ (Links)", size=14, color=FIELD, bold=True))
    p.append(mtext(lx, ly, "Вимірювання черг / надлишку:\ny_e = sum(x_i) vs C_e\n\nОновлення цін p_e(t+1)", size=11, color=INK))
    
    # Стрілка знизу: Передача Трафіку (x_i) від джерел до мережі
    p.append(arrow(sx + sw/2, sy + 30, lx - lw/2, ly + 30, color=NEG, sw=2.5))
    b_fwd, _, _ = textbox((sx + lx)/2, sy + 30, "Потік даних: швидкість x_i(t)", size=11, fill="#eaf0fd", stroke=NEG, pad=5)
    p.append(b_fwd)
    
    # Стрілка зверху: Зворотний зв'язок (ціни p_e / ECN / затримка) від мережі до джерел
    p.append(arrow(lx - lw/2, ly - 30, sx + sw/2, sy - 30, color=POS, sw=2.5))
    b_back, _, _ = textbox((sx + lx)/2, sy - 30, "Сигнал затору: ціна p_e(t) / ECN / Drop", size=11, fill="#fdecea", stroke=POS, pad=5)
    p.append(b_back)
    
    # Нижня рамка з висновком
    b_kelly, _, _ = textbox(W / 2, 355,
                            "Подвоїста декомпозиція Келлі: Мережа обчислює ціни заторів у вузлах, а джерела незалежно регулюють швидкості.",
                            size=12, fill="#fff7ee", stroke=LINE)
    p.append(b_kelly)
    
    render(os.path.join(OUT, "num-kelly-dual.svg"), W, H, *p,
           title="Подвоїста декомпозиція оптимізації мережевих utility (Kelly's NUM)")


# ── ФІГ.4 Backpressure Routing (Градієнт тиску черг) ──────────────────────────
def fig_backpressure_routing():
    W, H = 760, 420
    p = []
    
    ux, uy = 200.0, 200.0
    vx, vy = 560.0, 200.0
    
    # Ребро між u та v
    p.append(line(ux, uy, vx, vy, color=MUTED, sw=3.0, dash="6 4"))
    p.append(text((ux + vx)/2, uy - 45, "Ребро (u, v) з ємністю C = 10", size=12, color=INK, bold=True))
    
    # Вузол u з чергами
    p.append(circle(ux, uy, 65, fill="#eff6ff", stroke=NEG, sw=2.5))
    p.append(text(ux, uy - 45, "Вузол u", size=15, color=NEG, bold=True))
    
    # Черги в u
    b_u, _, _ = textbox(ux, uy + 5, "Черга A: Q_u[A] = 18\nЧерга B: Q_u[B] = 5", size=11, fill=BG, stroke=NEG, pad=6)
    p.append(b_u)
    
    # Вузол v з чергами
    p.append(circle(vx, vy, 65, fill="#f0fdf4", stroke=FIELD, sw=2.5))
    p.append(text(vx, vy - 45, "Вузол v", size=15, color=FIELD, bold=True))
    
    # Черги в v
    b_v, _, _ = textbox(vx, vy + 5, "Черга A: Q_v[A] = 6\nЧерга B: Q_v[B] = 10", size=11, fill=BG, stroke=FIELD, pad=6)
    p.append(b_v)
    
    # Перепад тиску (Backpressure calculation)
    # Delta Q_A = 18 - 6 = 12
    # Delta Q_B = 5 - 10 = -5
    # Перемагає товар A
    
    # Стрілка пересилки товару A
    p.append(arrow(ux + 70, uy - 15, vx - 70, vy - 15, color=POS, sw=3.5))
    
    b_grad, _, _ = textbox((ux + vx)/2, uy + 75,
                           "Різниця тиску черг:\nΔQ(A) = 18 - 6 = +12 (Перемагає!)\nΔQ(B) = 5 - 10 = -5\n\nПересилаємо товар A з u до v",
                           size=11, fill="#fff7ee", stroke=POS, pad=6)
    p.append(b_grad)
    
    render(os.path.join(OUT, "backpressure-routing.svg"), W, H, *p,
           title="Маршрутизація зворотного тиску (Backpressure Routing)")


# ── ФІГ.5 AIMD Phase Plane (Фазова площина двох потоків) ──────────────────────
def fig_aimd_phase_plane():
    W, H = 760, 440
    p = []
    
    ox, oy = 120.0, 360.0
    size = 280.0
    
    # Вісі координат x1 та x2
    p.append(line(ox, oy, ox + size + 30, oy, color=INK, sw=2.0))
    p.append(line(ox, oy, ox, oy - size - 30, color=INK, sw=2.0))
    
    p.append(text(ox + size + 25, oy + 20, "Швидкість потоку x1", size=12, color=INK, anchor="end", bold=True))
    p.append(text(ox - 15, oy - size - 20, "Швидкість потоку x2", size=12, color=INK, anchor="start", bold=True))
    
    # Лінія ємності x1 + x2 = C (з'єднує (0, C) та (C, 0))
    cx1, cy1 = ox, oy - size
    cx2, cy2 = ox + size, oy
    p.append(line(cx1, cy1, cx2, cy2, color=POS, sw=2.2))
    p.append(text(ox + size - 30, oy - size + 30, "Лінія ємності: x1 + x2 = C", size=11, color=POS, bold=True))
    
    # Лінія справедливості x1 = x2 (діагональ 45 градусів)
    p.append(line(ox, oy, ox + size, oy - size, color=FIELD, sw=2.0, dash="5 4"))
    p.append(text(ox + size - 80, oy - size - 10, "Лінія справедливості: x1 = x2", size=11, color=FIELD, bold=True))
    
    # Точка справедливості (C/2, C/2)
    eq_x, eq_y = ox + size/2, oy - size/2
    p.append(circle(eq_x, eq_y, 6, fill=FIELD, stroke=BG, sw=2.0))
    p.append(text(eq_x + 15, eq_y - 12, "Оптимум (C/2, C/2)", size=11, color=FIELD, bold=True))
    
    # Пилоподібна траєкторія AIMD (збіжність від точки A до оптимальної точки)
    # Точки траєкторії:
    pts = [
        (ox + 40, oy - 120),  # Початкова точка p0
        (ox + 130, oy - 210), # Адитивний ріст до переповнення (p1)
        (ox + 65, oy - 105),  # Мультиплікативне зменшення x/2 (p2)
        (ox + 145, oy - 185), # Адитивний ріст (p3)
        (ox + 72.5, oy - 92.5),# Зменшення (p4)
        (ox + 140, oy - 160)  # Близько до лінії справедливості
    ]
    
    # Малювання сегментів AIMD
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i+1]
        color = NEG if (i % 2 == 0) else POS
        sw = 2.0 if (i % 2 == 0) else 1.8
        dash = None if (i % 2 == 0) else "4 3"
        p.append(line(x1, y1, x2, y2, color=color, sw=sw, dash=dash))
    
    # Пояснювальний текстовий блок праворуч
    b_aimd, _, _ = textbox(ox + size + 160, oy - size/2 - 20,
                           "Динаміка AIMD:\n\n1. Адитивний ріст (+α):\n   Рух під кутом 45° паралельно\n   лінії справедливості.\n\n2. Мультиплікативний зріз (×β):\n   Променеве скорочення до нуля.\n\nРезультат: Збіжність до точки\nсправедливого оптимуму!",
                           size=11, fill="#fff7ee", stroke=LINE, pad=8)
    p.append(b_aimd)
    
    render(os.path.join(OUT, "aimd-phase-plane.svg"), W, H, *p,
           title="Фазова площина AIMD: збіжність до справедливості")


if __name__ == "__main__":
    fig_collapse()
    fig_water_filling()
    fig_num_kelly_dual()
    fig_backpressure_routing()
    fig_aimd_phase_plane()
    print("OK figs")
