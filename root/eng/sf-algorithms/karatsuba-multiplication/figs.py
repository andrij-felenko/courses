# -*- coding: utf-8 -*-
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Кольори теми ─────────────────────────────────────────────────────────────
C_SPLIT_H = "#e0f2fe"     # Старша половина (світло-блакитний)
C_SPLIT_L = "#fef3c7"     # Молодша половина (світло-бурштиновий)
C_STROKE_H = "#0284c7"    # Синій контур
C_STROKE_L = "#d97706"    # Бурштиновий контур
C_MID     = "#dcfce7"     # Зелений результат
C_MID_S   = "#16a34a"     # Зелений контур
C_ALERT   = "#fee2e2"     # Червоний акцент
C_ALERT_S = "#dc2626"     # Червоний контур


# ── Фігура 1: Декомпозиція та три добутки Карацуби ───────────────────────────
def fig_karatsuba_split_recursion():
    W, H = 940, 520
    p = []

    # Заголовок блоків операндів
    p.append(text(240, 60, "Вхідні операнди (розбиття навпіл по m = n/2 лімбів)", size=13, color=INK, bold=True))
    
    # Операнд X
    p.append(text(60, 105, "Число X :", size=13, color=INK, bold=True, anchor="start"))
    p.append(rect(140, 85, 150, 40, fill=C_SPLIT_H, stroke=C_STROKE_H, sw=1.8, rx=5))
    p.append(text(215, 110, "X_h  (старші n/2)", size=12, color=INK, bold=True))
    p.append(rect(290, 85, 150, 40, fill=C_SPLIT_L, stroke=C_STROKE_L, sw=1.8, rx=5))
    p.append(text(365, 110, "X_l  (молодші n/2)", size=12, color=INK, bold=True))

    # Операнд Y
    p.append(text(60, 160, "Число Y :", size=13, color=INK, bold=True, anchor="start"))
    p.append(rect(140, 140, 150, 40, fill=C_SPLIT_H, stroke=C_STROKE_H, sw=1.8, rx=5))
    p.append(text(215, 165, "Y_h  (старші n/2)", size=12, color=INK, bold=True))
    p.append(rect(290, 140, 150, 40, fill=C_SPLIT_L, stroke=C_STROKE_L, sw=1.8, rx=5))
    p.append(text(365, 165, "Y_l  (молодші n/2)", size=12, color=INK, bold=True))

    # Розділювальна лінія
    p.append(line(480, 50, 480, 490, color="#cbd5e1", sw=1.2, dash="4 4"))

    # Порівняння: Класичний підхід (4 множення)
    p.append(rect(510, 50, 395, 200, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=8))
    p.append(text(707, 76, "Шкільний підхід (4 множення)", size=13, color=POS, bold=True))
    
    rows_school = [
        ("Z2  = X_h · Y_h", "старший блок"),
        ("Z1a = X_h · Y_l", "перехресний добуток 1"),
        ("Z1b = X_l · Y_h", "перехресний добуток 2"),
        ("Z0  = X_l · Y_l", "молодший блок"),
    ]
    sy = 108
    for expr, note in rows_school:
        p.append(rect(530, sy - 14, 160, 26, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
        p.append(text(610, sy + 4, expr, size=11.5, color=POS, bold=True))
        p.append(text(705, sy + 4, "← " + note, size=11, color=MUTED, anchor="start"))
        sy += 34

    # Порівняння: Карацуба (3 множення)
    p.append(rect(510, 270, 395, 220, fill="#f0fdf4", stroke=C_MID_S, sw=1.6, rx=8))
    p.append(text(707, 296, "Трюк Карацуби (3 множення)", size=13, color=C_MID_S, bold=True))
    
    rows_kara = [
        ("Z2   = X_h · Y_h", "1-й рекурсивний добуток"),
        ("Z0   = X_l · Y_l", "2-й рекурсивний добуток"),
        ("Zmid = (X_h + X_l) · (Y_h + Y_l)", "3-й рекурсивний добуток"),
    ]
    ky = 328
    for expr, note in rows_kara:
        p.append(rect(525, ky - 14, 215, 26, fill="#dcfce7", stroke=C_MID_S, sw=1.2, rx=4))
        p.append(text(632, ky + 4, expr, size=11, color=C_MID_S, bold=True))
        p.append(text(748, ky + 4, "← " + note, size=10.5, color=MUTED, anchor="start"))
        ky += 34

    p.append(rect(525, 435, 365, 40, fill="#ffffff", stroke=C_MID_S, sw=1.3, rx=5))
    p.append(text(707, 459, "Z1 = Zmid − Z2 − Z0   (лише 2 віднімання!)", size=11.5, color=C_MID_S, bold=True))

    # Ліва нижня частина: Складання фінального результату зі зсувами
    p.append(rect(45, 240, 410, 250, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=8))
    p.append(text(250, 268, "Збирання результату зсувами (B = 2^32 або 2^64)", size=12.5, color=INK, bold=True))

    p.append(rect(65, 295, 370, 36, fill="#e0f2fe", stroke="#0284c7", sw=1.3, rx=4))
    p.append(text(250, 318, "Z2 · B^(2m)   [зсув на 2m слів вліво]", size=11.5, color="#0369a1", bold=True))

    p.append(text(250, 348, "+", size=15, color=INK, bold=True))

    p.append(rect(65, 360, 370, 36, fill="#dcfce7", stroke="#16a34a", sw=1.3, rx=4))
    p.append(text(250, 383, "Z1 · B^m      [зсув на m слів вліво]", size=11.5, color="#15803d", bold=True))

    p.append(text(250, 413, "+", size=15, color=INK, bold=True))

    p.append(rect(65, 425, 370, 36, fill="#fef3c7", stroke="#d97706", sw=1.3, rx=4))
    p.append(text(250, 448, "Z0            [без зсуву, молодша частина]", size=11.5, color="#b45309", bold=True))

    render(os.path.join(OUT, "karatsuba-split-recursion.svg"), W, H, *p,
           title="Декомпозиція множення: 3 множення Карацуби замість 4 класичних")


# ── Фігура 2: Дерево рекурсії алгоритму Карацуби ─────────────────────────────
def fig_karatsuba_recursion_tree():
    W, H = 940, 520
    p = []

    # Рівень 0 (Корінь)
    r0_x, r0_y = 440, 75
    p.append(rect(r0_x - 85, r0_y - 20, 170, 40, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(r0_x, r0_y + 5, "Розмір n (1 задача)", size=12, color=NEG, bold=True))

    # Рівень 1
    r1_y = 185
    r1_xs = [200, 440, 680]
    p.append(line(r0_x, r0_y + 20, r1_xs[0], r1_y - 20, color=LINE, sw=1.4))
    p.append(line(r0_x, r0_y + 20, r1_xs[1], r1_y - 20, color=LINE, sw=1.4))
    p.append(line(r0_x, r0_y + 20, r1_xs[2], r1_y - 20, color=LINE, sw=1.4))

    labels_r1 = [
        "Z2: n/2",
        "Z0: n/2",
        "Zmid: n/2",
    ]
    for x, lbl in zip(r1_xs, labels_r1):
        p.append(rect(x - 70, r1_y - 18, 140, 36, fill="#eff6ff", stroke=NEG, sw=1.5, rx=5))
        p.append(text(x, r1_y + 5, lbl, size=11.5, color=NEG, bold=True))

    # Рівень 2
    r2_y = 295
    r2_xs = [
        100, 190, 280,
        360, 440, 520,
        600, 690, 780
    ]
    for idx, px in enumerate(r1_xs):
        for c in range(3):
            cx = r2_xs[idx * 3 + c]
            p.append(line(px, r1_y + 18, cx, r2_y - 16, color=MUTED, sw=1.1))

    for x in r2_xs:
        p.append(rect(x - 36, r2_y - 15, 72, 30, fill="#f0fdf4", stroke=C_MID_S, sw=1.2, rx=4))
        p.append(text(x, r2_y + 5, "n/4", size=11, color=C_MID_S, bold=True))

    # Пунктир до листків
    for x in [100, 280, 440, 600, 780]:
        p.append(line(x, r2_y + 15, x, 385, color=MUTED, sw=1.0, dash="3 3"))

    # Рівень листків (базовий поріг)
    leaf_y = 415
    p.append(rect(60, leaf_y - 18, 760, 36, fill="#fef3c7", stroke="#d97706", sw=1.6, rx=6))
    p.append(text(440, leaf_y + 5, "Листки: 3^(log2 n) = n^(log2 3) ≈ n^1.585 підзадач базового розміру (шкільний стовпчик)", size=11.5, color="#92400e", bold=True))

    # Права панель: Обсяг роботи на рівнях
    rx = 860
    p.append(text(rx, 40, "Робота рівня", size=12, color=INK, bold=True))
    p.append(line(815, 52, 905, 52, color=LINE, sw=1.2))

    p.append(text(rx, r0_y + 5, "c · n", size=12, color=INK, bold=True))
    p.append(text(rx, r1_y + 5, "3 · c(n/2) = 1.5 cn", size=11.5, color=INK, bold=True))
    p.append(text(rx, r2_y + 5, "9 · c(n/4) = 2.25 cn", size=11.5, color=INK, bold=True))
    p.append(text(rx, 350, "⋮", size=16, color=MUTED, bold=True))
    p.append(text(rx, leaf_y + 5, "Θ(n^1.585)", size=12, color=POS, bold=True))

    # Ліва шкала глибини
    lx = 50
    p.append(text(lx, 40, "Глибина", size=12, color=INK, bold=True))
    p.append(line(15, 52, 85, 52, color=LINE, sw=1.2))
    p.append(text(lx, r0_y + 5, "k = 0", size=11.5, color=MUTED))
    p.append(text(lx, r1_y + 5, "k = 1", size=11.5, color=MUTED))
    p.append(text(lx, r2_y + 5, "k = 2", size=11.5, color=MUTED))
    p.append(text(lx, 350, "⋮", size=16, color=MUTED, bold=True))
    p.append(text(lx, leaf_y + 5, "log2 n", size=11.5, color=MUTED, bold=True))

    # Нижній висновок
    p.append(rect(60, 465, 820, 36, fill="#f8fafc", stroke="#cbd5e1", sw=1.3, rx=6))
    p.append(text(470, 488, "Сума геометричної прогресії зі знаменником q = 3/2 > 1 домінує в листках: T(n) = O(n^(log2 3))", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "karatsuba-recursion-tree.svg"), W, H, *p,
           title="Дерево рекурсії Карацуби: коефіцієнт розгалуження a = 3, глибина log2 n")


# ── Фігура 3: Порівняння алгоритмів множення та точки переходу (Crossover) ────
def fig_multiplication_algorithms_crossover():
    W, H = 940, 520
    p = []

    ox, oy = 90.0, 430.0
    pw, ph = 540.0, 350.0

    # Осі
    p.append(line(ox, oy, ox + pw + 25, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ox, oy - ph - 20, color=INK, sw=1.6))
    p.append(text(ox + pw / 2 + 10, oy + 42, "розмір операнда в лімбах / бітах (логарифмічна шкала)  →", size=12.5, color=INK, bold=True))
    p.append('<text transform="translate(%.1f,%.1f) rotate(-90)" font-family="%s" '
             'font-size="12.5" font-weight="700" fill="%s" text-anchor="middle">%s</text>'
             % (ox - 55, oy - ph / 2, FONT, INK, esc("час множення T(n)  →")))

    # Позначки по осі X
    ticks_x = [
        (1, "1", "64 біти"),
        (16, "16", "1 Кбіт"),
        (48, "48", "3 Кбіти"),
        (128, "128", "8 Кбіт"),
        (512, "512", "32 Кбіт"),
        (2048, "2048", "128 Кбіт"),
        (8192, "8192", "512 Кбіт"),
    ]

    def log_x(val):
        l2 = math.log2(max(val, 1))
        return ox + pw * (l2 / 13.0)

    for val, lbl, bits in ticks_x:
        xp = log_x(val)
        p.append(line(xp, oy, xp, oy + 5, color=INK, sw=1.2))
        p.append(text(xp, oy + 20, lbl, size=11, color=INK))
        p.append(text(xp, oy + 32, bits, size=9.5, color=MUTED))
        if val > 1:
            p.append(line(xp, oy, xp, oy - ph, color="#f1f5f9", sw=1.0, dash="3 3"))

    # Криві алгоритмів
    pts_school = []
    pts_kara = []
    pts_toom = []
    pts_fft = []

    for l2_idx in range(0, 131):
        l2 = l2_idx / 10.0
        n_val = 2.0 ** l2
        xp = ox + pw * (l2 / 13.0)

        t_school = 0.08 * (n_val ** 2.0)
        t_kara = 1.4 * (n_val ** 1.585)
        t_toom = 6.5 * (n_val ** 1.465)
        t_fft = 45.0 * n_val * max(math.log2(n_val + 2), 1.0)

        def log_y(t):
            lt = math.log2(max(t, 0.05))
            norm = (lt + 4.0) / 24.0
            return oy - ph * min(max(norm, 0.0), 1.0)

        pts_school.append((xp, log_y(t_school)))
        pts_kara.append((xp, log_y(t_kara)))
        pts_toom.append((xp, log_y(t_toom)))
        pts_fft.append((xp, log_y(t_fft)))

    poly_sch = " ".join("%.1f,%.1f" % pt for pt in pts_school)
    poly_kar = " ".join("%.1f,%.1f" % pt for pt in pts_kara)
    poly_too = " ".join("%.1f,%.1f" % pt for pt in pts_toom)
    poly_fft = " ".join("%.1f,%.1f" % pt for pt in pts_fft)

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly_sch, POS))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (poly_kar, C_STROKE_H))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="5 3"/>' % (poly_too, "#8e44ad"))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (poly_fft, FIELD))

    # Точки переходу (Crossover thresholds)
    # 1. School -> Karatsuba (~36 лімбів)
    x_c1 = log_x(36)
    p.append(line(x_c1, oy, x_c1, oy - ph, color=POS, sw=1.3, dash="4 4"))
    p.append(circle(x_c1, oy - ph * 0.38, 4.5, fill="#fee2e2", stroke=POS, sw=2))
    p.append(text(x_c1, oy - ph * 0.38 - 14, "Поріг Карацуби (≈ 32–48 слів)", size=11, color=POS, bold=True, anchor="middle"))

    # 2. Karatsuba -> Toom-3 (~180 лімбів)
    x_c2 = log_x(180)
    p.append(line(x_c2, oy, x_c2, oy - ph, color="#8e44ad", sw=1.3, dash="4 4"))
    p.append(circle(x_c2, oy - ph * 0.58, 4.5, fill="#f3e8ff", stroke="#8e44ad", sw=2))
    p.append(text(x_c2, oy - ph * 0.58 - 14, "Поріг Toom-3 (≈ 150–250)", size=10.5, color="#8e44ad", bold=True, anchor="middle"))

    # 3. Toom-3 -> FFT (~2500 лімбів)
    x_c3 = log_x(2500)
    p.append(line(x_c3, oy, x_c3, oy - ph, color=FIELD, sw=1.3, dash="4 4"))
    p.append(circle(x_c3, oy - ph * 0.82, 4.5, fill="#dcfce7", stroke=FIELD, sw=2))
    p.append(text(x_c3, oy - ph * 0.82 - 14, "Поріг FFT (≈ 2048–4096)", size=10.5, color=FIELD, bold=True, anchor="middle"))

    # Легенда
    lx, ly, lw, lh = 665.0, 65.0, 255.0, 395.0
    p.append(rect(lx, ly, lw, lh, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(lx + lw / 2, ly + 24, "Ієрархія алгоритмів", size=13, color=INK, bold=True))

    rows_leg = [
        (POS,       "Шкільний (Basecase)",   "O(n^2)",         "Найпростіший; малий оверхед;\nшвидкий до 32 слів (2048 біт)"),
        (C_STROKE_H, "Карацуба (Karatsuba)", "O(n^1.585)",     "Розбиття на 2 частини (3 mul);\nоптимум: 32 – 200 слів"),
        ("#8e44ad", "Тум-Кук (Toom-3)",      "O(n^1.465)",     "Розбиття на 3 частини (5 mul);\nоптимум: 200 – 2000 слів"),
        (FIELD,     "Шьонгаґе-Штрассен/FFT", "O(n log n)",     "Швидке перетворення Фур'є;\nдля велетенських чисел"),
    ]
    ry = ly + 56
    for col, name, comp, note in rows_leg:
        p.append(line(lx + 14, ry + 4, lx + 40, ry + 4, color=col, sw=3.2))
        p.append(text(lx + 48, ry - 3, name, size=11.5, color=INK, bold=True, anchor="start"))
        p.append(text(lx + lw - 14, ry - 3, comp, size=11, color=col, bold=True, anchor="end"))
        lines_note = note.split("\n")
        p.append(text(lx + 48, ry + 15, lines_note[0], size=10, color=MUTED, anchor="start"))
        p.append(text(lx + 48, ry + 29, lines_note[1], size=10, color=MUTED, anchor="start"))
        ry += 60

    box_note, _, _ = textbox(lx + lw / 2, ly + lh - 25, "На практиці (GMP): гібридний конвеєр", size=11,
                             pad=6, fill="#edf2f7", stroke="#cbd5e1", bold=True)
    p.append(box_note)

    render(os.path.join(OUT, "multiplication-algorithms-crossover.svg"), W, H, *p,
           title="Порівняння алгоритмів множення: точки переходу та діапазони ефективності")


# ── Фігура 4: Схема скретчпад-буфера під час рекурсії ─────────────────────────
def fig_scratchpad_memory_layout():
    W, H = 940, 480
    p = []

    # Верхнє порівняння
    # Варіант А: Наївне динамічне виділення
    p.append(rect(45, 55, 400, 180, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(245, 82, "Наївний підхід: виділення malloc() у кожному вузлі", size=12, color=POS, bold=True))
    
    p.append(rect(65, 105, 360, 36, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(245, 128, "Рівень 0: malloc(2n) для результатів Z2, Z0, Zmid", size=11, color=POS))

    p.append(rect(85, 148, 320, 34, fill="#ffffff", stroke=POS, sw=1.1, rx=4))
    p.append(text(245, 170, "Рівень 1: 3 × malloc(n) для підзадач...", size=10.5, color=POS))

    p.append(text(245, 215, "⚠️ O(n^1.585) викликів алокатора руйнують продуктивність!", size=11, color=POS, bold=True))

    # Варіант Б: Єдиний скретчпад
    p.append(rect(495, 55, 400, 180, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(695, 82, "Оптимальний підхід: єдиний скретчпад (Scratchpad)", size=12, color=FIELD, bold=True))

    p.append(rect(515, 105, 360, 36, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(695, 128, "Один буфер розміром ≈ 3n слів на самому початку", size=11, color=FIELD, bold=True))

    p.append(rect(515, 148, 360, 34, fill="#ffffff", stroke=FIELD, sw=1.1, rx=4))
    p.append(text(695, 170, "Вузол рекурсії лише зміщує покажчик: scratch + offset", size=10.5, color=INK))

    p.append(text(695, 215, "✓ 0 викликів malloc під час рекурсії; кеш-локальність L1/L2", size=11, color=FIELD, bold=True))

    # Нижня частина: Анатомія розподілу пам'яті в єдиному буфері
    p.append(rect(45, 260, 850, 200, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(470, 288, "Анатомія лінійного скретчпада розміром S(n) ≤ 3n слів", size=13, color=INK, bold=True))

    bx = 70.0
    by = 315.0
    total_w = 800.0

    # Сегмент 1: Zmid буфер
    w1 = total_w * 0.38
    p.append(rect(bx, by, w1, 55, fill="#e0f2fe", stroke="#0284c7", sw=1.6, rx=5))
    p.append(text(bx + w1 / 2, by + 24, "Тимчасовий добуток Zmid", size=11.5, color="#0369a1", bold=True))
    p.append(text(bx + w1 / 2, by + 42, "розмір: n слів (2 · m)", size=10.5, color=MUTED))

    # Сегмент 2: Суми (Xh + Xl) та (Yh + Yl)
    w2 = total_w * 0.22
    p.append(rect(bx + w1, by, w2, 55, fill="#fef3c7", stroke="#d97706", sw=1.6, rx=5))
    p.append(text(bx + w1 + w2 / 2, by + 24, "Суми половин", size=11.5, color="#92400e", bold=True))
    p.append(text(bx + w1 + w2 / 2, by + 42, "m + 1 слів кожна", size=10.5, color=MUTED))

    # Сегмент 3: Вкладений скретчпад для підзадач
    w3 = total_w * 0.40
    p.append(rect(bx + w1 + w2, by, w3, 55, fill="#f3e8ff", stroke="#8e44ad", sw=1.6, rx=5))
    p.append(text(bx + w1 + w2 + w3 / 2, by + 24, "Вкладений скретчпад наступного рівня", size=11.5, color="#6b21a8", bold=True))
    p.append(text(bx + w1 + w2 + w3 / 2, by + 42, "розмір: S(n/2) ≈ 1.5 n слів", size=10.5, color=MUTED))

    # Пояснення прогресії пам'яті
    p.append(rect(70, 395, 800, 48, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
    p.append(text(470, 418, "Рекурентність пам'яті: S(n) = n + (m + 1) + S(n/2) = 1.5n + S(n/2) + 1  ⇒  Сума прогресії S(n) < 3n слів", size=11.5, color=INK, bold=True))
    p.append(text(470, 434, "Пам'ять перевикористовується між послідовними рекурсивними гілками Z2, Z0 та Zmid", size=10.5, color=MUTED))

    render(os.path.join(OUT, "scratchpad-memory-layout.svg"), W, H, *p,
           title="Організація пам'яті: єдиний скретчпад лінійного розміру замість рекурсивних алокацій")


if __name__ == "__main__":
    fig_karatsuba_split_recursion()
    fig_karatsuba_recursion_tree()
    fig_multiplication_algorithms_crossover()
    fig_scratchpad_memory_layout()
    print("Всі 4 фігури успішно згенеровано у %s" % OUT)
