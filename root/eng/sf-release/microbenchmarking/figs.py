# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

HOT   = "#c0392b"
COOL  = "#2457d6"
OK    = "#27ae60"
WARN  = "#d35400"
MUTED = "#6b7280"
INK   = "#1a1a1a"
LINE  = "#333333"
FILL  = "#f4f6f8"

# ── 1. compiler-optimization-trap.svg ─────────────────────────────────────────
def fig_compiler_trap():
    W, H = 860, 400
    p = []
    p.append(text(W / 2, 28, "ПАСТКА ОПТИМІЗАЦІЇ: НАЇВНИЙ ВИМІР ПРОТИ БАР'ЄРА", size=14, color=INK, bold=True))

    # Ліва колонка: Наївний код
    x1, y1, w1, h1 = 25, 52, 245, 320
    p.append(rect(x1, y1, w1, h1, fill="#fdf2f2", stroke=HOT, sw=1.8, rx=8))
    p.append(text(x1 + w1 / 2, y1 + 24, "НАЇВНИЙ КОД", size=12, color=HOT, bold=True))
    p.append(text(x1 + w1 / 2, y1 + 42, "без бар'єрів компілятора", size=10, color=MUTED, italic=True))

    code_naive = [
        "uint64_t t0 = rdtsc();",
        "for (int i = 0; i < N; ++i) {",
        "    uint64_t v = hash(i);",
        "}",
        "uint64_t dt = rdtsc() - t0;"
    ]
    cy = y1 + 68
    for line_text in code_naive:
        p.append(text(x1 + 12, cy, line_text, size=10, color=INK, anchor="start"))
        cy += 18

    p.append(line(x1 + 15, y1 + 170, x1 + w1 - 15, y1 + 170, color=HOT, sw=1, dash="4,3"))
    p.append(text(x1 + w1 / 2, y1 + 192, "ЩО РОБИТЬ КОМПІЛЯТОР:", size=10.5, color=HOT, bold=True))
    p.append(text(x1 + w1 / 2, y1 + 214, "1. Змінна v не читається", size=10, color=INK))
    p.append(text(x1 + w1 / 2, y1 + 232, "2. hash(i) немає побічних дій", size=10, color=INK))
    p.append(text(x1 + w1 / 2, y1 + 250, "3. Цикл викинуто (DCE)", size=10, color=HOT, bold=True))

    p.append(rect(x1 + 15, y1 + 270, w1 - 30, 34, fill="#fbecec", stroke=HOT, sw=1.2, rx=4))
    p.append(text(x1 + w1 / 2, y1 + 292, "Результат: 0.00 нс (ілюзія)", size=11, color=HOT, bold=True))

    # Стрілка між колонками
    p.append(arrow(x1 + w1 + 6, y1 + h1 / 2, x1 + w1 + 32, y1 + h1 / 2, color=MUTED, sw=2))

    # Центральна колонка: Що насправді згенерував асемблер
    x2, y2, w2, h2 = 306, 52, 245, 320
    p.append(rect(x2, y2, w2, h2, fill="#fef9e7", stroke=WARN, sw=1.8, rx=8))
    p.append(text(x2 + w2 / 2, y2 + 24, "АСЕМБЛЕР (O3)", size=12, color=WARN, bold=True))
    p.append(text(x2 + w2 / 2, y2 + 42, "реальні інструкції CPU", size=10, color=MUTED, italic=True))

    asm_naive = [
        "rdtsc           ; t0",
        "mov  rsi, rax",
        "rdtsc           ; t1",
        "sub  rax, rsi   ; dt",
        "; ТІЛО ЦИКЛУ ЗНИКЛО"
    ]
    cy = y2 + 68
    for line_text in asm_naive:
        col = WARN if "ЗНИКЛО" in line_text else INK
        bld = "ЗНИКЛО" in line_text
        p.append(text(x2 + 12, cy, line_text, size=10, color=col, anchor="start", bold=bld))
        cy += 18

    p.append(line(x2 + 15, y2 + 170, x2 + w2 - 15, y2 + 170, color=WARN, sw=1, dash="4,3"))
    p.append(text(x2 + w2 / 2, y2 + 192, "НАСЛІДОК:", size=10.5, color=WARN, bold=True))
    p.append(text(x2 + w2 / 2, y2 + 214, "Виміряно лише накладні", size=10, color=INK))
    p.append(text(x2 + w2 / 2, y2 + 232, "витрати читання таймера", size=10, color=INK))
    p.append(text(x2 + w2 / 2, y2 + 250, "(~15-25 тактів ядра)", size=10, color=MUTED))

    p.append(rect(x2 + 15, y2 + 270, w2 - 30, 34, fill="#fef5e7", stroke=WARN, sw=1.2, rx=4))
    p.append(text(x2 + w2 / 2, y2 + 292, "Помилка: 100% хибний вимір", size=11, color=WARN, bold=True))

    # Стрілка між колонками
    p.append(arrow(x2 + w2 + 6, y2 + h2 / 2, x2 + w2 + 32, y2 + h2 / 2, color=MUTED, sw=2))

    # Права колонка: Захищений вимір
    x3, y3, w3, h3 = 588, 52, 245, 320
    p.append(rect(x3, y3, w3, h3, fill="#eafaf1", stroke=OK, sw=1.8, rx=8))
    p.append(text(x3 + w3 / 2, y3 + 24, "ЗАХИЩЕНИЙ ВИМІР", size=12, color=OK, bold=True))
    p.append(text(x3 + w3 / 2, y3 + 42, "з оптимізаційним бар'єром", size=10, color=MUTED, italic=True))

    code_safe = [
        "uint64_t t0 = rdtsc_fence();",
        "for (int i = 0; i < N; ++i) {",
        "    uint64_t v = hash(i);",
        '    asm volatile("" :: "r,m"(v)',
        '                 : "memory");',
        "}",
        "uint64_t dt = rdtsc_fence() - t0;"
    ]
    cy = y3 + 68
    for line_text in code_safe:
        p.append(text(x3 + 10, cy, line_text, size=9.6, color=INK, anchor="start"))
        cy += 16

    p.append(line(x3 + 15, y3 + 185, x3 + w3 - 15, y3 + 185, color=OK, sw=1, dash="4,3"))
    p.append(text(x3 + w3 / 2, y3 + 204, "ПОВЕДІНКА БАР'ЄРА:", size=10.5, color=OK, bold=True))
    p.append(text(x3 + w3 / 2, y3 + 224, "1. Змушує обчислити v у регістр", size=10, color=INK))
    p.append(text(x3 + w3 / 2, y3 + 242, "2. Забороняє викидати цикл", size=10, color=INK))
    p.append(text(x3 + w3 / 2, y3 + 260, "3. Не додає зайвих інструкцій", size=10, color=OK, bold=True))

    p.append(rect(x3 + 15, y3 + 270, w3 - 30, 34, fill="#d4efdf", stroke=OK, sw=1.2, rx=4))
    p.append(text(x3 + w3 / 2, y3 + 292, "Результат: 4.82 нс (чесна затримка)", size=10.5, color=OK, bold=True))

    render(os.path.join(OUT, "compiler-optimization-trap.svg"), W, H, *p,
           title="Пастка компілятора при мікробенчмаркінгу")


# ── 2. multimodal-latency-distribution.svg ────────────────────────────────────
def fig_multimodal_distribution():
    W, H = 840, 420
    p = []
    p.append(text(W / 2, 26, "БАГАТОМОДАЛЬНИЙ РОЗПОДІЛ ЗАТРИМКИ ТА ОМАНЛИВІСТЬ СЕРЕДНЬОГО", size=14, color=INK, bold=True))

    # Вісь координат
    ox, oy = 80, 340
    gw, gh = 700, 270
    p.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5))
    p.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5))

    # Позначки осі X (Логарифмічна шкала затримки)
    p.append(text(ox + gw, oy + 22, "Затримка виконання (нс, лог-шкала)", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox - 10, oy - gh + 10, "Густина ймовірності p(t)", size=11, color=INK, anchor="end", bold=True))

    ticks = [
        (100, "1 нс\n(Регістри)"),
        (220, "4 нс\n(L1 Cache)"),
        (380, "15 нс\n(L2/L3 Cache)"),
        (540, "80 нс\n(DRAM RAM)"),
        (660, "1500+ нс\n(OS Interrupt)")
    ]
    for tx, lbl in ticks:
        p.append(line(ox + tx, oy, ox + tx, oy + 5, color=LINE, sw=1.2))
        lines = lbl.split("\n")
        p.append(text(ox + tx, oy + 18, lines[0], size=10, color=INK, bold=True))
        p.append(text(ox + tx, oy + 32, lines[1], size=9.5, color=MUTED))

    # Крива розподілу (три горби + важкий хвіст)
    curve_points = [
        (ox + 40, oy),
        (ox + 100, oy - 20),
        (ox + 160, oy - 90),
        (ox + 210, oy - 230), # Пік L1
        (ox + 230, oy - 230),
        (ox + 270, oy - 70),
        (ox + 320, oy - 40),
        (ox + 375, oy - 120), # Пік L2/L3
        (ox + 395, oy - 120),
        (ox + 450, oy - 35),
        (ox + 500, oy - 25),
        (ox + 535, oy - 65),  # Пік DRAM
        (ox + 555, oy - 65),
        (ox + 600, oy - 20),
        (ox + 650, oy - 12),  # Хвіст ОС
        (ox + 680, oy - 6),
        (ox + 700, oy)
    ]
    # Побудова path
    d_fill = f"M {curve_points[0][0]} {curve_points[0][1]} "
    for pt in curve_points[1:]:
        d_fill += f"L {pt[0]} {pt[1]} "
    d_fill += "Z"
    p.append(f'<path d="{d_fill}" fill="#eaf2f8" stroke="none"/>')

    d_stroke = f"M {curve_points[0][0]} {curve_points[0][1]} "
    for pt in curve_points[1:]:
        d_stroke += f"L {pt[0]} {pt[1]} "
    p.append(f'<path d="{d_stroke}" fill="{COOL}" stroke="{COOL}" stroke-width="2.4"/>')

    # Підписи під піками
    p.append(rect(ox + 160, oy - 262, 110, 22, fill="#e8f8f5", stroke=OK, sw=1, rx=4))
    p.append(text(ox + 215, oy - 247, "Мода 1: L1 Cache Hit", size=9.5, color=OK, bold=True))

    p.append(rect(ox + 330, oy - 152, 110, 22, fill="#ebf5fb", stroke=COOL, sw=1, rx=4))
    p.append(text(ox + 385, oy - 137, "Мода 2: L3 Cache Hit", size=9.5, color=COOL, bold=True))

    p.append(rect(ox + 490, oy - 97, 110, 22, fill="#fef9e7", stroke=WARN, sw=1, rx=4))
    p.append(text(ox + 545, oy - 82, "Мода 3: DRAM Miss", size=9.5, color=WARN, bold=True))

    p.append(text(ox + 650, oy - 30, "Хвіст переривань ОС", size=9.5, color=HOT, italic=True))

    # Статистичні маркери: Медіана p50, p95, p99 та Середнє арифметичне
    mx = ox + 225
    p.append(line(mx, oy, mx, oy - 210, color=OK, sw=1.8, dash="4,3"))
    p.append(text(mx, oy - 216, "p50 (медіана) = 4.2 нс", size=10, color=OK, bold=True))

    p95x = ox + 430
    p.append(line(p95x, oy, p95x, oy - 120, color=COOL, sw=1.6, dash="3,3"))
    p.append(text(p95x, oy - 126, "p95 = 22 нс", size=9.5, color=COOL, bold=True))

    p99x = ox + 580
    p.append(line(p99x, oy, p99x, oy - 90, color=WARN, sw=1.6, dash="3,3"))
    p.append(text(p99x, oy - 96, "p99 = 95 нс", size=9.5, color=WARN, bold=True))

    mean_x = ox + 355
    p.append(line(mean_x, oy, mean_x, oy - 190, color=HOT, sw=2.2))
    p.append(rect(mean_x - 70, oy - 215, 140, 24, fill="#fbecec", stroke=HOT, sw=1.4, rx=4))
    p.append(text(mean_x, oy - 199, "Середнє арифметичне: 18.4 нс", size=9.5, color=HOT, bold=True))
    p.append(text(mean_x, oy - 178, "потрапляє в порожню яму!", size=9.5, color=HOT, italic=True))

    render(os.path.join(OUT, "multimodal-latency-distribution.svg"), W, H, *p,
           title="Багатомодальний розподіл затримки мікробенчмарку")


# ── 3. microbenchmark-pipeline.svg ────────────────────────────────────────────
def fig_benchmark_pipeline():
    W, H = 840, 380
    p = []
    p.append(text(W / 2, 26, "АРХІТЕКТУРА НАДІЙНОГО ПРОГОНУ МІКРОБЕНЧМАРКУ", size=14, color=INK, bold=True))

    stages = [
        ("1. СТАБІЛІЗАЦІЯ", "Ізоляція оточення", [
            "Прив'язка до ядра (CPU affinity)",
            "Говернор performance",
            "Вимкнення Turbo Boost джиттеру"
        ], "#e8f8f5", OK),
        ("2. ПРОГРІВ", "Синхронізація кешу", [
            "Warmup цикл (L1/L2 кеші)",
            "Навчання передбачувача",
            "Стабілізація конвеєра CPU"
        ], "#ebf5fb", COOL),
        ("3. КАЛІБРУВАННЯ", "Пошук розміру батчу", [
            "Підбір N ітерацій у циклі",
            "Δt батчу >> роздільність таймера",
            "Мінімум 100-кратний запас"
        ], "#fef9e7", WARN),
        ("4. ЗАХИЩЕНИЙ ЗАМІР", "Вимірювальне ядро", [
            "Серіалізація lfence + rdtsc",
            "Бар'єри DoNotOptimize()",
            "Віднімання накладних t_bias"
        ], "#fbecec", HOT),
        ("5. АГРЕГАЦІЯ", "Статистичний аналіз", [
            "Розрахунок медіани та IQR",
            "Перцентилі p90, p95, p99",
            "Виявлення багатомодальності"
        ], "#f4ecf7", "#8e44ad")
    ]

    bx = 20
    bw = 150
    gap = 14
    by = 56
    bh = 270

    for i, (title_s, sub_s, bullets, bg_col, brd_col) in enumerate(stages):
        cur_x = bx + i * (bw + gap)
        p.append(rect(cur_x, by, bw, bh, fill=bg_col, stroke=brd_col, sw=1.8, rx=8))
        p.append(text(cur_x + bw / 2, by + 24, title_s, size=11, color=brd_col, bold=True))
        p.append(text(cur_x + bw / 2, by + 40, sub_s, size=9.5, color=MUTED, italic=True))
        p.append(line(cur_x + 10, by + 50, cur_x + bw - 10, by + 50, color=brd_col, sw=1, dash="2,2"))

        sy = by + 74
        for bullet in bullets:
            p.append(circle(cur_x + 12, sy - 3, 2.5, fill=brd_col, stroke="none"))
            words = bullet.split(" ")
            line1, line2 = "", ""
            if len(bullet) > 18:
                mid = len(words) // 2
                line1 = " ".join(words[:mid])
                line2 = " ".join(words[mid:])
            else:
                line1 = bullet

            p.append(text(cur_x + 20, sy, line1, size=9.5, color=INK, anchor="start"))
            if line2:
                sy += 13
                p.append(text(cur_x + 20, sy, line2, size=9.5, color=INK, anchor="start"))
            sy += 24

        if i < len(stages) - 1:
            arr_x = cur_x + bw + 2
            p.append(arrow(arr_x, by + bh / 2, arr_x + gap - 4, by + bh / 2, color=MUTED, sw=1.8))

    p.append(rect(20, 338, W - 40, 30, fill="#f8f9fa", stroke=LINE, sw=1, rx=6))
    p.append(text(W / 2, 357, "Результат: детермінований і відтворюваний вимір з точністю до десятих часток наносекунди", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "microbenchmark-pipeline.svg"), W, H, *p,
           title="Конвеєр надійного мікробенчмаркінгу")


if __name__ == "__main__":
    fig_compiler_trap()
    fig_multimodal_distribution()
    fig_benchmark_pipeline()
    print("All figures generated successfully.")
