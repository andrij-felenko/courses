# -*- coding: utf-8 -*-
"""Фігури до теми «Черги в мережах: затримка і втрати».
Запуск:  python figs.py   → створює SVG у ./img/
Стиль і примітиви — зі спільного scripts/svgkit.py.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

ORANGE = "#e67e22"
PURPLE = "#8e44ad"
CYAN = "#16a085"

# ── 1. Базова модель M/M/1: вузол обслуговування з буфером ─────────────────
def fig_queue_model_mm1():
    W, H = 760, 360
    f = [text(W / 2, 26, "Вузол комутації як система масового обслуговування", size=15, bold=True)]

    # Вхідний потік
    f.append(arrow(40, 150, 160, 150, color=INK, sw=2.0))
    f.append(text(100, 125, "Вхідний потік λ", size=13, bold=True, color=NEG))
    f.append(text(100, 175, "пакетів / с", size=11, color=MUTED))
    f.append(text(100, 195, "(випадковий інтервал)", size=10, color=MUTED, italic=True))

    # Буфер (черга)
    f.append(line(170, 110, 370, 110, color=INK, sw=2.0))
    f.append(line(170, 190, 370, 190, color=INK, sw=2.0))
    f.append(line(170, 110, 170, 190, color=INK, sw=2.0, dash="3,3"))
    f.append(text(270, 92, "Буфер інтерфейсу (черга)", size=13, bold=True, color=INK))

    # Пакети в черзі
    pkts = [(190, "P₄"), (235, "P₃"), (280, "P₂"), (325, "P₁")]
    for px, plabel in pkts:
        f.append(rect(px, 120, 36, 60, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
        f.append(text(px + 18, 155, plabel, size=12, bold=True, color=NEG))

    # Довжина черги L_q
    f.append(line(180, 215, 360, 215, color=MUTED, sw=1.2))
    f.append(line(180, 210, 180, 220, color=MUTED, sw=1.2))
    f.append(line(360, 210, 360, 220, color=MUTED, sw=1.2))
    f.append(text(270, 235, "Середня черга L_q (пакетів)", size=11, color=MUTED))
    f.append(text(270, 252, "Час очікування W_q", size=11, bold=True, color=NEG))

    # Сервер (передавач каналу зв'язку)
    f.append(circle(440, 150, 42, fill="#fef9e7", stroke=ORANGE, sw=2.0))
    f.append(text(440, 142, "Передавач", size=12, bold=True, color=INK))
    f.append(text(440, 160, "μ = C / L_p", size=12, bold=True, color=ORANGE))

    # Пакет на передачі
    f.append(arrow(370, 150, 398, 150, color=INK, sw=1.8))

    # Вихідний потік
    f.append(arrow(482, 150, 620, 150, color=FIELD, sw=2.0))
    f.append(text(550, 125, "Вихідний канал C", size=13, bold=True, color=FIELD))
    f.append(text(550, 175, "біт / с", size=11, color=MUTED))
    f.append(text(550, 195, "Час передачі 1/μ", size=11, color=FIELD))

    # Загальний контур системи W, L
    f.append(rect(160, 65, 330, 235, fill="none", stroke=LINE, sw=1.2, rx=8))
    f.append(text(325, 290, "Вся система: середня кількість L = λ · W, час W = W_q + 1/μ", size=12, bold=True, color=INK))
    f.append(text(W / 2, 335, "Завантаження ρ = λ / μ. Стійкий стан можливий лише при ρ < 1.", size=12, color=POS, bold=True))

    render(os.path.join(IMG, "queue-model-mm1.svg"), W, H, *f)


# ── 2. Затримка проти завантаження: асимптотична стіна ───────────────────────
def fig_delay_vs_utilization():
    W, H = 760, 420
    f = [text(W / 2, 26, "Гіперболічне зростання затримки при наближенні завантаження до 1", size=15, bold=True)]

    # Вісь координат
    ox, oy = 100, 340
    gw, gh = 580, 270

    # Сітка та осі
    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))

    # Стрілки осей
    f.append(arrow(ox + gw, oy, ox + gw + 20, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy - gh, ox, oy - gh - 20, color=LINE, sw=1.8))

    f.append(text(ox + gw + 25, oy + 5, "ρ", size=14, bold=True, color=INK))
    f.append(text(ox - 10, oy - gh - 25, "Затримка W / (1/μ)", size=13, bold=True, color=INK, anchor="end"))

    # Позначки по осі X (0.0 to 1.0)
    x_ticks = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0]
    for xt in x_ticks:
        px = ox + xt * (gw - 40)
        f.append(line(px, oy, px, oy + 6, color=LINE, sw=1.2))
        f.append(text(px, oy + 22, "%.1f" % xt if xt != 1.0 else "1.0", size=11, color=MUTED))
        if xt > 0 and xt < 1.0:
            f.append(line(px, oy, px, oy - gh, color="#e5e7eb", sw=1.0, dash="3,3"))

    # Позначки по осі Y (коефіцієнт множення затримки 1x, 2x, 5x, 10x, 20x)
    y_ticks = [(1, "1×"), (2, "2×"), (5, "5×"), (10, "10×"), (20, "20×")]
    for val, lab in y_ticks:
        py = oy - (val / 20.0) * (gh - 30)
        f.append(line(ox - 6, py, ox, py, color=LINE, sw=1.2))
        f.append(text(ox - 12, py + 4, lab, size=11, color=MUTED, anchor="end"))
        f.append(line(ox, py, ox + gw - 40, py, color="#e5e7eb", sw=1.0, dash="3,3"))

    # Асимптота rho = 1
    asymp_x = ox + 1.0 * (gw - 40)
    f.append(line(asymp_x, oy, asymp_x, oy - gh, color=POS, sw=1.5, dash="4,4"))
    f.append(text(asymp_x, oy - gh - 8, "Асимптота (черга → ∞)", size=10, bold=True, color=POS))

    # Побудова графіка W(rho) = 1 / (1 - rho)
    pts = []
    for i in range(0, 96):
        r = i / 100.0
        w_val = 1.0 / (1.0 - r)
        if w_val > 20.0:
            break
        px = ox + r * (gw - 40)
        py = oy - (w_val / 20.0) * (gh - 30)
        pts.append((px, py))

    # Лінія кривої
    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=NEG, sw=2.5))

    # Ключові точки на кривій
    key_points = [
        (0.5, 2.0, "ρ=0.5 → W = 2 · (1/μ)"),
        (0.8, 5.0, "ρ=0.8 → W = 5 · (1/μ)"),
        (0.9, 10.0, "ρ=0.9 → W = 10 · (1/μ)"),
        (0.95, 20.0, "ρ=0.95 → W = 20 · (1/μ)")
    ]

    for kr, kw, klabel in key_points:
        kpx = ox + kr * (gw - 40)
        kpy = oy - (kw / 20.0) * (gh - 30)
        f.append(circle(kpx, kpy, 4, fill=POS, stroke="#ffffff", sw=1.5))
        f.append(text(kpx - 10, kpy - 10, klabel, size=10, bold=True, color=INK, anchor="end"))

    # Пояснювальний блок зон
    f.append(rect(ox + 40, oy - gh + 15, 250, 75, fill="#f9fafb", stroke="#d1d5db", sw=1.0, rx=4))
    f.append(text(ox + 50, oy - gh + 35, "Зона стабільності (ρ < 0.7):", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(ox + 50, oy - gh + 52, "Затримка передбачувана, черга мала", size=10.5, color=INK, anchor="start"))
    f.append(text(ox + 50, oy - gh + 75, "Критична зона (ρ > 0.85): вибух затримки", size=10.5, bold=True, color=POS, anchor="start"))

    render(os.path.join(IMG, "delay-vs-utilization.svg"), W, H, *f)


# ── 3. Порівняння розподілів (M/M/1, M/D/1, M/G/1) ──────────────────────────
def fig_mm1_vs_mg1_variance():
    W, H = 760, 380
    f = [text(W / 2, 26, "Вплив дисперсії розміру пакетів на затримку (Поллачек–Хінчин)", size=15, bold=True)]

    ox, oy = 100, 310
    gw, gh = 580, 230

    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    f.append(arrow(ox + gw, oy, ox + gw + 20, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy - gh, ox, oy - gh - 20, color=LINE, sw=1.8))

    f.append(text(ox + gw + 25, oy + 5, "ρ", size=14, bold=True, color=INK))
    f.append(text(ox - 10, oy - gh - 20, "Середня черга L_q", size=13, bold=True, color=INK, anchor="end"))

    # Осі
    for xt in [0.2, 0.4, 0.6, 0.8, 0.9]:
        px = ox + xt * (gw - 40)
        f.append(line(px, oy, px, oy + 5, color=LINE, sw=1.2))
        f.append(text(px, oy + 20, "%.1f" % xt, size=11, color=MUTED))
        f.append(line(px, oy, px, oy - gh, color="#f3f4f6", sw=1.0, dash="2,2"))

    max_l = 15.0
    for yv in [2, 5, 10, 15]:
        py = oy - (yv / max_l) * (gh - 20)
        f.append(line(ox - 5, py, ox, py, color=LINE, sw=1.2))
        f.append(text(ox - 10, py + 4, str(yv), size=11, color=MUTED, anchor="end"))
        f.append(line(ox, py, ox + gw - 40, py, color="#f3f4f6", sw=1.0, dash="2,2"))

    curves = [
        ("M/D/1 (фіксований розмір, Cv=0)", 0.0, FIELD, "1,0"),
        ("M/M/1 (експоненційний розмір, Cv=1)", 1.0, NEG, "1,0"),
        ("M/G/1 (пачковий трафік, Cv=2.0)", 4.0, POS, "1,0")
    ]

    for label, cv_sq, col, dsh in curves:
        pts = []
        for i in range(1, 95):
            r = i / 100.0
            lq = (r * r * (1.0 + cv_sq)) / (2.0 * (1.0 - r))
            if lq > max_l:
                break
            px = ox + r * (gw - 40)
            py = oy - (lq / max_l) * (gh - 20)
            pts.append((px, py))
        for j in range(len(pts) - 1):
            f.append(line(pts[j][0], pts[j][1], pts[j+1][0], pts[j+1][1], color=col, sw=2.4))

    # Легенда
    lx, ly = ox + 30, oy - gh + 20
    f.append(rect(lx, ly, 380, 95, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=6))
    f.append(line(lx + 15, ly + 25, lx + 45, ly + 25, color=POS, sw=2.5))
    f.append(text(lx + 55, ly + 29, "M/G/1 (Cv=2.0, змішаний/пачковий): черга в 2.5× більша", size=11, bold=True, color=POS, anchor="start"))

    f.append(line(lx + 15, ly + 52, lx + 45, ly + 52, color=NEG, sw=2.5))
    f.append(text(lx + 55, ly + 56, "M/M/1 (Cv=1.0, експоненційний): класична модель", size=11, bold=True, color=NEG, anchor="start"))

    f.append(line(lx + 15, ly + 78, lx + 45, ly + 78, color=FIELD, sw=2.5))
    f.append(text(lx + 55, ly + 82, "M/D/1 (Cv=0.0, фіксовані пакети): черга рівно в 2× менша", size=11, bold=True, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "mm1-vs-mg1-variance.svg"), W, H, *f)


# ── 4. Глобальна синхронізація TCP при Tail Drop ───────────────────────────
def fig_tail_drop_sync():
    W, H = 760, 420
    f = [text(W / 2, 26, "Глобальна синхронізація TCP при переповненні буфера (Tail Drop)", size=15, bold=True)]

    ox, oy = 80, 340
    gw, gh = 620, 240

    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    f.append(arrow(ox + gw, oy, ox + gw + 20, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy - gh, ox, oy - gh - 20, color=LINE, sw=1.8))

    f.append(text(ox + gw + 25, oy + 5, "Час t", size=13, bold=True, color=INK))
    f.append(text(ox - 10, oy - gh - 20, "Сумарне вікно / Заповнення буфера", size=12, bold=True, color=INK, anchor="end"))

    # Пояснення праворуч зверху (поза лініями)
    f.append(rect(ox + 260, oy - gh - 15, 340, 55, fill="#f9fafb", stroke="#d1d5db", sw=1.2, rx=6))
    f.append(text(ox + 270, oy - gh + 5, "1. Потоки одночасно роздувають буфер", size=10.5, color=INK, anchor="start"))
    f.append(text(ox + 270, oy - gh + 20, "2. Хвіст буфера скидає пакети ВСІХ з'єднань", size=10.5, bold=True, color=POS, anchor="start"))
    f.append(text(ox + 270, oy - gh + 35, "3. Усі TCP вдвічі ріжуть швидкість одночасно", size=10.5, color=NEG, anchor="start"))

    # Лінія ємності буфера
    cap_y = oy - gh * 0.65
    f.append(line(ox, cap_y, ox + gw, cap_y, color=POS, sw=2.0, dash="5,4"))
    f.append(text(ox + 10, cap_y - 8, "Стеля буфера (Tail Drop поріг)", size=11, bold=True, color=POS, anchor="start"))

    # Хвилі синхронного колапсу (3 цикли пилки)
    cycles = [(ox + 20, ox + 180), (ox + 180, ox + 360), (ox + 360, ox + 540)]

    for start_x, end_x in cycles:
        mid_drop_x = end_x - 15
        # Потік 1 (синій)
        f.append(line(start_x, oy - 40, mid_drop_x, cap_y + 10, color=NEG, sw=2.0))
        f.append(line(mid_drop_x, cap_y + 10, end_x, oy - 45, color=NEG, sw=2.0))

        # Потік 2 (зелений)
        f.append(line(start_x, oy - 60, mid_drop_x, cap_y + 25, color=FIELD, sw=2.0))
        f.append(line(mid_drop_x, cap_y + 25, end_x, oy - 65, color=FIELD, sw=2.0))

        # Потік 3 (помаранчевий)
        f.append(line(start_x, oy - 25, mid_drop_x, cap_y + 3, color=ORANGE, sw=2.0))
        f.append(line(mid_drop_x, cap_y + 3, end_x, oy - 30, color=ORANGE, sw=2.0))

        # Момент скидання
        f.append(circle(mid_drop_x, cap_y + 10, 5, fill=POS, stroke="#ffffff", sw=1.5))
        f.append(line(mid_drop_x, cap_y, mid_drop_x, oy, color=POS, sw=1.0, dash="2,2"))

    # Позначки під пилкою
    f.append(text(ox + 165, oy + 20, "Скидання у всіх!", size=10.5, bold=True, color=POS))
    f.append(text(ox + 345, oy + 20, "Скидання у всіх!", size=10.5, bold=True, color=POS))
    f.append(text(ox + 525, oy + 20, "Скидання у всіх!", size=10.5, bold=True, color=POS))

    # Провал утилізації каналу
    f.append(rect(ox + 200, oy - 35, 120, 30, fill="#fdecea", stroke=POS, sw=1.0, rx=4))
    f.append(text(ox + 260, oy - 16, "Канал простоює", size=11, bold=True, color=POS))

    render(os.path.join(IMG, "tail-drop-sync.svg"), W, H, *f)


# ── 5. Принцип CoDel: розрізнення доброї та поганої черги ───────────────────
def fig_codel_sojourn_time():
    W, H = 760, 420
    f = [text(W / 2, 26, "Алгоритм CoDel: розрізнення короткочасного сплеску та стоячої черги", size=15, bold=True)]

    ox, oy = 80, 340
    gw, gh = 620, 250

    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    f.append(arrow(ox + gw, oy, ox + gw + 20, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy - gh, ox, oy - gh - 20, color=LINE, sw=1.8))

    f.append(text(ox + gw + 25, oy + 5, "Час t", size=13, bold=True, color=INK))
    f.append(text(ox - 10, oy - gh - 20, "Час у черзі (sojourn time)", size=12, bold=True, color=INK, anchor="end"))

    # Поріг TARGET = 5 ms
    target_y = oy - 45
    f.append(line(ox, target_y, ox + gw, target_y, color=FIELD, sw=2.0, dash="5,4"))
    f.append(text(ox + gw - 10, target_y - 8, "TARGET = 5 мс (допустима затримка)", size=11, bold=True, color=FIELD, anchor="end"))

    # Ліва частина: "Добра черга" (тимчасовий сплеск)
    split_x = ox + 260
    f.append(line(split_x, oy, split_x, oy - gh, color="#d1d5db", sw=1.5, dash="3,3"))

    # Сплеск затримки
    f.append(line(ox + 20, oy - 15, ox + 60, oy - 120, color=NEG, sw=2.2))
    f.append(line(ox + 60, oy - 120, ox + 110, oy - 90, color=NEG, sw=2.2))
    f.append(line(ox + 110, oy - 90, ox + 170, oy - 20, color=NEG, sw=2.2))
    f.append(line(ox + 170, oy - 20, split_x - 20, oy - 10, color=NEG, sw=2.2))

    f.append(text(ox + 130, oy - gh + 20, "«Добра черга» (good queue)", size=12, bold=True, color=FIELD))
    f.append(text(ox + 130, oy - gh + 38, "Сплеск розсмоктується сам,", size=10.5, color=MUTED))
    f.append(text(ox + 130, oy - gh + 54, "пакети НЕ скидаються", size=10.5, color=FIELD, bold=True))

    # Права частина: "Погана черга" (standing queue)
    f.append(text(ox + 440, oy - gh + 20, "«Погана / стояча черга» (bad queue)", size=12, bold=True, color=POS))
    f.append(text(ox + 440, oy - gh + 38, "Мінімум за INTERVAL (100 мс) > TARGET", size=10.5, color=MUTED))
    f.append(text(ox + 440, oy - gh + 54, "CoDel вмикає скидання пакетів!", size=10.5, color=POS, bold=True))

    # Стояча черга, що не опускається нижче target
    base_sq = target_y - 60
    f.append(line(split_x + 20, oy - 20, split_x + 50, base_sq - 30, color=POS, sw=2.2))
    f.append(line(split_x + 50, base_sq - 30, split_x + 110, base_sq - 10, color=POS, sw=2.2))
    f.append(line(split_x + 110, base_sq - 10, split_x + 170, base_sq - 40, color=POS, sw=2.2))
    f.append(line(split_x + 170, base_sq - 40, split_x + 240, base_sq - 15, color=POS, sw=2.2))
    f.append(line(split_x + 240, base_sq - 15, split_x + 320, base_sq - 50, color=POS, sw=2.2))

    # Інтервал спостереження INTERVAL
    int_start = split_x + 50
    int_end = split_x + 190
    f.append(line(int_start, oy - 5, int_end, oy - 5, color=INK, sw=1.8))
    f.append(line(int_start, oy - 12, int_start, oy + 2, color=INK, sw=1.8))
    f.append(line(int_end, oy - 12, int_end, oy + 2, color=INK, sw=1.8))
    f.append(text((int_start + int_end) / 2, oy + 18, "INTERVAL = 100 мс", size=11, bold=True, color=INK))

    # Точки скидання
    drop_x1 = split_x + 190
    drop_x2 = split_x + 260
    f.append(circle(drop_x1, base_sq - 25, 5, fill=POS, stroke="#ffffff", sw=1.5))
    f.append(text(drop_x1, base_sq - 38, "Скидання 1", size=10, bold=True, color=POS))

    f.append(circle(drop_x2, base_sq - 20, 5, fill=POS, stroke="#ffffff", sw=1.5))
    f.append(text(drop_x2, base_sq - 33, "Скидання 2 (через T/√2)", size=10, bold=True, color=POS))

    render(os.path.join(IMG, "codel-sojourn-time.svg"), W, H, *f)


# ── 6. Архітектура FQ-CoDel ────────────────────────────────────────────────
def fig_fq_codel_architecture():
    W, H = 760, 420
    f = [text(W / 2, 26, "Архітектура FQ-CoDel: хешування потоків + незалежні CoDel черги", size=15, bold=True)]

    # Вхідний потік з різними типами пакетів
    f.append(text(75, 75, "Вхідний змішаний трафік", size=12, bold=True, color=INK))
    pkts_in = [
        (40, 95, "DNS", FIELD),
        (85, 95, "SSH", FIELD),
        (130, 95, "TCP 1", NEG),
        (175, 95, "TCP 2", ORANGE),
        (220, 95, "TCP 1", NEG)
    ]
    for px, py, plab, pcol in pkts_in:
        f.append(rect(px, py, 38, 30, fill="#ffffff", stroke=pcol, sw=1.8, rx=3))
        f.append(text(px + 19, py + 19, plab, size=9.5, bold=True, color=pcol))

    # Хеш-функція (5-tuple)
    f.append(arrow(150, 135, 150, 165, color=INK, sw=1.8))
    f.append(rect(60, 165, 180, 55, fill="#fef9e7", stroke=ORANGE, sw=1.5, rx=6))
    f.append(text(150, 188, "Хешування (5-tuple)", size=12, bold=True, color=INK))
    f.append(text(150, 206, "IP src/dst + Port src/dst + Proto", size=9.5, color=MUTED))

    # Стрілки розкидання у черги
    f.append(arrow(240, 180, 310, 100, color=FIELD, sw=1.5))
    f.append(arrow(240, 192, 310, 192, color=NEG, sw=1.5))
    f.append(arrow(240, 205, 310, 285, color=ORANGE, sw=1.5))

    # Набір черг (1024 Flow Queues)
    # Черга 1 (тонкий потік: DNS / SSH / VoIP)
    f.append(rect(310, 75, 170, 50, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(395, 95, "Черга 1: Інтерактивна", size=11, bold=True, color=FIELD))
    f.append(text(395, 112, "0-1 пакет, затримка < 1 мс", size=9.5, color=MUTED))

    # Черга 2 (товстий потік: TCP Download 1)
    f.append(rect(310, 165, 170, 55, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    f.append(text(395, 185, "Черга 2: Завантаження 1", size=11, bold=True, color=NEG))
    f.append(text(395, 202, "CoDel стежить за sojourn", size=9.5, color=NEG))

    # Черга N (товстий потік: TCP Download 2)
    f.append(rect(310, 260, 170, 55, fill="#fef5e7", stroke=ORANGE, sw=1.5, rx=4))
    f.append(text(395, 280, "Черга N: Завантаження 2", size=11, bold=True, color=ORANGE))
    f.append(text(395, 297, "CoDel скидає надлишок", size=9.5, color=ORANGE))

    # DRR Scheduler (Deficit Round Robin)
    f.append(arrow(480, 100, 540, 175, color=FIELD, sw=1.8))
    f.append(arrow(480, 192, 540, 192, color=NEG, sw=1.8))
    f.append(arrow(480, 285, 540, 210, color=ORANGE, sw=1.8))

    f.append(rect(540, 155, 160, 75, fill="#f4f6f8", stroke=LINE, sw=1.8, rx=6))
    f.append(text(620, 180, "DRR Планувальник", size=12, bold=True, color=INK))
    f.append(text(620, 198, "Справедлива черга", size=10.5, color=MUTED))
    f.append(text(620, 215, "Квант ~1514 байтів", size=9.5, color=MUTED))

    # Вихідний інтерфейс
    f.append(arrow(700, 192, 745, 192, color=FIELD, sw=2.2))

    # Підсумок знизу
    f.append(rect(50, 340, 660, 60, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=6))
    f.append(text(380, 362, "Результат: тонкі інтерактивні потоки передаються МИТТЄВО без черги,", size=11, bold=True, color=FIELD))
    f.append(text(380, 382, "а масивні завантаження повністю утилізують канал під контролем CoDel.", size=11, color=INK))

    render(os.path.join(IMG, "fq-codel-architecture.svg"), W, H, *f)


def main():
    fig_queue_model_mm1()
    fig_delay_vs_utilization()
    fig_mm1_vs_mg1_variance()
    fig_tail_drop_sync()
    fig_codel_sojourn_time()
    fig_fq_codel_architecture()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
