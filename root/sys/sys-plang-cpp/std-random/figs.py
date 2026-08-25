# -*- coding: utf-8 -*-
"""Фігури до теми «random: рушії, розподіли й відтворюваність» (reference/cpp-standards/library)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Двошарова архітектура <random>: Engine vs Distribution ─────────────
def fig_random_architecture():
    W, H = 920, 360
    f = []

    # Застарілий C-підхід ліворуч
    f.append(rect(30, 40, 380, 290, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    f.append(text(220, 68, "Застарілий підхід (C stdlib)", size=15, color=POS, bold=True))
    
    b1, _, _ = textbox(220, 120, ["rand() % N"], size=14, pad=10, fill="#ffe3e3", stroke=POS, bold=True)
    f.append(b1)
    
    f.append(mtext(220, 185, [
        "❌ Модульне зміщення (Modulo Bias)",
        "❌ Глобальний прихований стан (не thread-safe)",
        "❌ Лише рівномірне цілочисельне значення",
        "❌ Низька якість молодших бітів в LCG"
    ], size=13, color=INK, anchor="middle", lh=1.4))

    # Сонце/розділення C++11 праворуч
    f.append(rect(440, 40, 450, 290, fill="#f4faf5", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(665, 68, "Двошарова модель C++11 <random>", size=15, color=FIELD, bold=True))

    # Шар 1: Генератор вихідних бітів (URBG / Engine)
    eng_box, ew, eh = textbox(665, 120, [
        "1. Джерело бітів (Engine / URBG)",
        "std::mt19937 / std::random_device",
        "Генерує псевдовипадкові цілі [min, max]"
    ], size=13, pad=10, fill="#e8f8ed", stroke=FIELD, bold=False)
    f.append(eng_box)

    # Стрілка зв'язку між шарами
    f.append(arrow(665, 160, 665, 195, color=FIELD, sw=2))
    f.append(text(680, 180, "сирі біти", size=11, color=MUTED, anchor="left", italic=True))

    # Шар 2: Математичний розподіл (Distribution)
    dist_box, dw, dh = textbox(665, 245, [
        "2. Математичний розподіл (Distribution)",
        "uniform_int_distribution / normal_distribution",
        "Перетворює біти у цільовий діапазон і форму"
    ], size=13, pad=10, fill="#d2f1da", stroke=FIELD, bold=False)
    f.append(dist_box)

    f.append(text(460, 345, "Чиста сепарація відповідальностей: генератор дає ентропію, розподіл дає форму", size=12, color=MUTED))

    render(os.path.join(IMG, "random-architecture.svg"), W, H, *f,
           title="Двошарова архітектура бібліотеки std::random у C++")


# ── 2. Модульне зміщення (Modulo Bias) vs Точний розподіл ─────────────────
def fig_modulo_bias():
    W, H = 920, 380
    f = []

    f.append(text(460, 30, "Аналіз Modulo Bias при rand() % 6 для RAND_MAX = 32767", size=15, color=INK, bold=True))

    # Пояснення принципу Діріхле
    f.append(text(460, 58, "32768 можливих значень розкладаються у 6 кошиків: 32768 = 5461 × 6 + 2 остача", size=13, color=MUTED))

    # Блок з Modulo Bias (ліворуч)
    f.append(rect(40, 85, 400, 240, fill="#fff8f8", stroke=POS, sw=1.5, rx=6))
    f.append(text(240, 110, "Схема rand() % 6 (зсунута ймовірність)", size=14, color=POS, bold=True))

    buckets_bias = [
        ("0", "5462", POS, 150),
        ("1", "5462", POS, 150),
        ("2", "5461", NEG, 120),
        ("3", "5461", NEG, 120),
        ("4", "5461", NEG, 120),
        ("5", "5461", NEG, 120)
    ]
    for i, (val, cnt, col, h_bar) in enumerate(buckets_bias):
        x = 75 + i * 58
        f.append(rect(x, 260 - h_bar * 0.7, 40, h_bar * 0.7, fill=col, stroke=LINE, sw=1))
        f.append(text(x + 20, 275, val, size=13, bold=True))
        f.append(text(x + 20, 255 - h_bar * 0.7, cnt, size=11, color=col, bold=True))

    f.append(text(240, 305, "Значення 0 та 1 випадають частіше!", size=12, color=POS, bold=True))

    # Блок з Rejection Sampling у C++ (праворуч)
    f.append(rect(480, 85, 400, 240, fill="#f4faf5", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(680, 110, "std::uniform_int_distribution<int>(0, 5)", size=14, color=FIELD, bold=True))

    buckets_cpp = [
        ("0", "5461", FIELD, 125),
        ("1", "5461", FIELD, 125),
        ("2", "5461", FIELD, 125),
        ("3", "5461", FIELD, 125),
        ("4", "5461", FIELD, 125),
        ("5", "5461", FIELD, 125)
    ]
    for i, (val, cnt, col, h_bar) in enumerate(buckets_cpp):
        x = 515 + i * 58
        f.append(rect(x, 260 - h_bar * 0.7, 40, h_bar * 0.7, fill=col, stroke=LINE, sw=1))
        f.append(text(x + 20, 275, val, size=13, bold=True))
        f.append(text(x + 20, 255 - h_bar * 0.7, cnt, size=11, color=col, bold=True))

    f.append(text(680, 305, "Rejection Sampling відкидає надлишок (ідеальне рівномірне)", size=12, color=FIELD, bold=True))

    f.append(text(460, 355, "Модульне ділення спотворює статистичний розподіл, руйнуючи випадковість у симуляціях", size=12, color=MUTED))

    render(os.path.join(IMG, "modulo-bias-vs-distribution.svg"), W, H, *f,
           title="Ілюстрація Modulo Bias та його усунення у std::uniform_int_distribution")


# ── 3. Трансформація рівномірного бітового потоку у нормальний ──────────
def fig_distribution_transform():
    W, H = 920, 360
    f = []

    f.append(text(460, 30, "Математична трансформація ентропії: від бітів до Gaussian Normal", size=15, color=INK, bold=True))

    # Етап 1: Генератор бітів
    b1, _, _ = textbox(150, 110, [
        "1. URBG (Engine)",
        "32-бітний integer",
        "0x8F3A10C9..."
    ], size=13, pad=10, fill="#f4f6f8", stroke=LINE)
    f.append(b1)

    f.append(arrow(240, 110, 310, 110, color=LINE, sw=1.8))
    f.append(text(275, 95, "Нормалізація", size=11, color=MUTED))

    # Етап 2: Рівномірне [0.0, 1.0)
    b2, _, _ = textbox(400, 110, [
        "2. Uniform Real",
        "u ~ U[0, 1)",
        "0.5592810..."
    ], size=13, pad=10, fill="#eaf7ee", stroke=FIELD)
    f.append(b2)

    f.append(arrow(490, 110, 560, 110, color=FIELD, sw=1.8))
    f.append(text(525, 95, "Box-Muller / Ziggurat", size=11, color=MUTED))

    # Етап 3: Нормальний розподіл
    b3, _, _ = textbox(750, 110, [
        "3. Normal Distribution",
        "x ~ N(μ, σ²)",
        "Гаусова дзвіноподібна крива"
    ], size=13, pad=10, fill="#e8f0fe", stroke=NEG)
    f.append(b3)

    # Крива Гауса знизу
    f.append(rect(150, 180, 620, 140, fill="#fafafa", stroke=LINE, sw=1, rx=6))
    f.append(text(460, 205, "Щільність ймовірності f(x) = (1 / √(2πσ²)) exp(-(x-μ)² / 2σ²)", size=12, color=INK, bold=True))

    # Намалюємо схематичну дзвоноподібну криву
    points = [(200, 300), (280, 295), (350, 280), (410, 240), (460, 220), (510, 240), (570, 280), (640, 295), (720, 300)]
    path_d = "M " + " L ".join("%d %d" % pt for pt in points)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_d, NEG))

    # Ось та позначки
    f.append(line(200, 300, 720, 300, color=MUTED, sw=1))
    f.append(line(460, 220, 460, 300, color=MUTED, sw=1, dash="4,4"))
    f.append(text(460, 314, "μ (середнє)", size=11, color=MUTED))
    f.append(text(350, 314, "-1σ", size=11, color=MUTED))
    f.append(text(570, 314, "+1σ", size=11, color=MUTED))

    f.append(text(460, 345, "Генератор надає базові випадкові біти, а розподіл застосовує нелінійне математичне перетворення", size=12, color=MUTED))

    render(os.path.join(IMG, "distribution-transformation.svg"), W, H, *f,
           title="Схема математичної трансформації бітового потоку в Гаусів розподіл")


# ── 4. MT19937 vs PCG32: Порівняння стану та швидкодії ───────────────────
def fig_mt19937_vs_pcg():
    W, H = 920, 370
    f = []

    f.append(text(460, 30, "Порівняння архітектури стану: std::mt19937 vs PCG32", size=15, color=INK, bold=True))

    # Ліва частина: MT19937
    f.append(rect(40, 55, 410, 270, fill="#fffbf5", stroke="#e67e22", sw=1.5, rx=8))
    f.append(text(245, 80, "std::mt19937 (Mersenne Twister)", size=14, color="#d35400", bold=True))

    # Стейт масив MT19937
    f.append(rect(70, 100, 350, 75, fill="#fdf2e9", stroke="#e67e22", sw=1))
    f.append(text(245, 120, "State Array: uint32_t state[624]", size=13, bold=True))
    f.append(text(245, 140, "Розмір стану в пам'яті: 2496 байтів (2.5 КБ)", size=12, color=POS))
    f.append(text(245, 160, "Період: 2¹⁹⁹³⁷ - 1 (~4.3 × 10⁶⁰⁰¹)", size=11, color=MUTED))

    f.append(mtext(245, 195, [
        "❌ Не вміщається у CPU регістрах (Cache Eviction)",
        "❌ Великий перелік операцій Bitwise Matrix Transition",
        "❌ Може відновлювати стан після 624 виходів (Linear)",
        "✔ Величезний період для обчислювальної физики"
    ], size=12, color=INK, anchor="middle", lh=1.35))

    # Права частина: PCG32
    f.append(rect(470, 55, 410, 270, fill="#f4faf5", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(675, 80, "PCG32 (Permuted Congruential Generator)", size=14, color=FIELD, bold=True))

    # Стейт PCG32
    f.append(rect(500, 100, 350, 75, fill="#e8f8ed", stroke=FIELD, sw=1))
    f.append(text(675, 120, "State: uint64_t state + uint64_t inc", size=13, bold=True))
    f.append(text(675, 140, "Розмір стану в пам'яті: 16 байтів (вміщається у регістр)", size=12, color=FIELD, bold=True))
    f.append(text(675, 160, "Період: 2⁶⁴ (~1.8 × 10¹⁹)", size=11, color=MUTED))

    f.append(mtext(675, 195, [
        "✔ Відмінна просторова та часова локальність у кеші L1",
        "✔ Висока криптоподібна статистична якість (SmallCrush)",
        "✔ Підтримує Multiple Streams (потоки через inc)",
        "✔ Значно швидший на сучасних 64-бітних CPU"
    ], size=12, color=INK, anchor="middle", lh=1.35))

    f.append(text(460, 345, "MT19937 розроблено у 1997 році для RAM; PCG враховує архітектуру L1-кешу та CPU регістрів", size=12, color=MUTED))

    render(os.path.join(IMG, "mt19937-state-and-pcg.svg"), W, H, *f,
           title="Порівняння розміру стану та локальності кешу std::mt19937 та PCG32")


if __name__ == "__main__":
    fig_random_architecture()
    fig_modulo_bias()
    fig_distribution_transform()
    fig_mt19937_vs_pcg()
    print("Всі 4 фігури успішно згенеровано у reference/cpp-standards/library/std-random/img/")
