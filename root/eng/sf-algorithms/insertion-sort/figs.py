# -*- coding: utf-8 -*-
"""Фігури для статті «Сортування вставками (Insertion Sort)» та її вставок.
Генерує 4 SVG у ./img:
1. insertion-mechanism.svg — анатомія кроку сортування вставками
2. inversion-pairs.svg — інверсії та їх покрокове усунення
3. binary-vs-linear-insertion.svg — порівняння лінійних та двійкових вставок
4. hybrid-cutoff.svg — поріг ефективності гібридних сортувань (Timsort/Introsort)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

# Палітра
BG_SORTED   = "#e8f5e9"   # Відсортована частина (світло-зелене)
BORDER_SORT = "#2e7d32"   # Темно-зелений
BG_KEY      = "#fff9c4"   # Вийнятий ключ (світло-жовте)
BORDER_KEY  = "#f57f17"   # Жовто-помаранчевий
BG_UNSORTED = "#f5f5f5"   # Невідсортована частина (світло-сіре)
BORDER_UNS  = "#757575"   # Сірий
BG_SHIFT    = "#ffebee"   # Елементи, що зсуваються (світло-червоне)
BORDER_SHF  = "#c62828"   # Червоний

def cell(x, y, w, h, val, fill=FILL, stroke=LINE, sw=1.5, tc=INK, bold=True, fs=15):
    return (rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=4) +
            text(x + w / 2, y + h / 2 + 5, val, size=fs, color=tc, bold=bold))

# ── Фігура 1: Анатомія кроку сортування вставками ────────────────────────────
def fig_mechanism():
    W, H = 780, 360
    cw, ch = 56, 44
    x0, y0 = 70, 75
    f = []

    # Заголовок блоку 1: Початковий стан кроку
    f.append(text(x0, y0 - 30, "1. Стан перед вставкою елемента A[4] = 3", size=13, color=INK, anchor="start", bold=True))
    
    vals1 = [2, 5, 7, 9, 3, 8]
    # Зони
    f.append(rect(x0, y0 - 18, 4 * cw, 14, fill=BG_SORTED, stroke=BORDER_SORT, sw=1, rx=2))
    f.append(text(x0 + 2 * cw, y0 - 8, "Відсортований префікс A[0..3]", size=10, color=BORDER_SORT, bold=True))

    f.append(rect(x0 + 4 * cw, y0 - 18, cw, 14, fill=BG_KEY, stroke=BORDER_KEY, sw=1, rx=2))
    f.append(text(x0 + 4 * cw + cw / 2, y0 - 8, "Ключ", size=10, color=BORDER_KEY, bold=True))

    f.append(rect(x0 + 5 * cw, y0 - 18, cw, 14, fill=BG_UNSORTED, stroke=BORDER_UNS, sw=1, rx=2))
    f.append(text(x0 + 5 * cw + cw / 2, y0 - 8, "Суфікс", size=10, color=BORDER_UNS))

    for i, v in enumerate(vals1):
        if i < 4:
            fl, st = BG_SORTED, BORDER_SORT
        elif i == 4:
            fl, st = BG_KEY, BORDER_KEY
        else:
            fl, st = BG_UNSORTED, BORDER_UNS
        f.append(cell(x0 + i * cw, y0, cw, ch, str(v), fill=fl, stroke=st, sw=1.6))
        f.append(text(x0 + i * cw + cw / 2, y0 + ch + 15, f"[{i}]", size=11, color=MUTED))

    # Стрілка збереження ключа в регістр
    f.append(arrow(x0 + 4 * cw + cw / 2, y0 + ch + 22, x0 + 4 * cw + cw / 2, y0 + ch + 42, color=BORDER_KEY, sw=1.5))
    f.append(rect(x0 + 4 * cw - 15, y0 + ch + 44, cw + 30, 24, fill=BG_KEY, stroke=BORDER_KEY, sw=1.2, rx=3))
    f.append(text(x0 + 4 * cw + cw / 2, y0 + ch + 60, "key = 3", size=11, color=BORDER_KEY, bold=True))

    # Заголовок блоку 2: Зсув та запис
    y1 = y0 + 155
    f.append(text(x0, y1 - 30, "2. Зсув більших елементів праворуч та вставка key на позицію [1]", size=13, color=INK, anchor="start", bold=True))

    vals2 = [2, 3, 5, 7, 9, 8]
    for i, v in enumerate(vals2):
        if i == 0:
            fl, st = BG_SORTED, BORDER_SORT
        elif i == 1:
            fl, st = BG_KEY, BORDER_KEY
        elif i <= 4:
            fl, st = BG_SHIFT, BORDER_SHF
        else:
            fl, st = BG_UNSORTED, BORDER_UNS
        f.append(cell(x0 + i * cw, y1, cw, ch, str(v), fill=fl, stroke=st, sw=1.6))
        f.append(text(x0 + i * cw + cw / 2, y1 + ch + 15, f"[{i}]", size=11, color=MUTED))

    # Стрілки зсувів
    f.append(arrow(x0 + 3 * cw + cw / 2, y1 - 8, x0 + 4 * cw + cw / 2, y1 - 8, color=BORDER_SHF, sw=1.5))
    f.append(arrow(x0 + 2 * cw + cw / 2, y1 - 8, x0 + 3 * cw + cw / 2, y1 - 8, color=BORDER_SHF, sw=1.5))
    f.append(arrow(x0 + 1 * cw + cw / 2, y1 - 8, x0 + 2 * cw + cw / 2, y1 - 8, color=BORDER_SHF, sw=1.5))

    # Пояснення праворуч
    tx = x0 + 6 * cw + 25
    f.append(fitbox(tx, y0, 280, ch + 20, "1. Копіюємо A[4] у змінну key = 3\n2. Порівнюємо key з елементами зліва", size=11, fill="#fafafa", stroke="#e0e0e0"))
    f.append(fitbox(tx, y1 - 10, 280, ch + 40, "3. Оскільки 9>3, 7>3, 5>3 — зсуваємо їх праворуч\n4. Оскільки 2<=3 — зупинка, вставляємо key в A[1]", size=11, fill="#fafafa", stroke="#e0e0e0"))

    render(os.path.join(IMG, "insertion-mechanism.svg"), W, H, *f,
           title="Анатомія одного кроку сортування вставками")

# ── Фігура 2: Інверсії та їх покрокове усунення ──────────────────────────────
def fig_inversions():
    W, H = 880, 360
    f = []

    # Ліва частина: концепція інверсій
    lx = 40
    f.append(text(lx, 65, "Початковий масив: [4, 2, 1, 3]", size=14, color=INK, anchor="start", bold=True))
    f.append(text(lx, 88, "Кількість інверсій I = 4 : (4,2), (4,1), (4,3), (2,1)", size=12, color=POS, anchor="start", bold=True))

    cw, ch = 38, 34
    y_trace = 120

    steps = [
        ("Початок", [4, 2, 1, 3], "I = 4", MUTED),
        ("Вставка 2", [2, 4, 1, 3], "I = 3 (без (4,2))", FIELD),
        ("Вставка 1", [1, 2, 4, 3], "I = 1 (без (4,1),(2,1))", FIELD),
        ("Вставка 3", [1, 2, 3, 4], "I = 0 (без (4,3))", FIELD),
    ]

    for idx, (label, arr, inv_label, col) in enumerate(steps):
        yy = y_trace + idx * 52
        f.append(text(lx, yy + 22, label, size=11, color=INK, anchor="start"))
        for j, val in enumerate(arr):
            f.append(cell(lx + 100 + j * cw, yy, cw, ch, str(val), fill=BG_SORTED if idx == 3 else FILL, stroke=BORDER_SORT if idx == 3 else LINE, sw=1.2, fs=13))
        f.append(text(lx + 100 + 4 * cw + 15, yy + 22, inv_label, size=11, color=col, anchor="start", bold=True))

    # Права частина: ключова теорема
    rx = 520
    f.append(fitbox(rx, 65, 320, 240, 
        "Фундаментальна теорема про інверсії:\n\n"
        "• Інверсія — це пара (i, j), де i < j, але A[i] > A[j].\n\n"
        "• Кожен елементарний зсув суміжних елементів\n"
        "  зменшує число інверсій I рівно на 1.\n\n"
        "• Загальна кількість зсувів = точна кількість інверсій I.\n\n"
        "• Час роботи: T(N) = O(N + I).\n\n"
        "• Якщо масив k-майже відсортований (I ≤ k·N),\n"
        "  алгоритм працює за O(k·N) = O(N).",
        size=11, fill="#f8f9fa", stroke="#cfd8dc"))

    render(os.path.join(IMG, "inversion-pairs.svg"), W, H, *f,
           title="Зв'язок сортування вставками з числом інверсій у масиві")

# ── Фігура 3: Лінійні проти двійкових вставок ────────────────────────────────
def fig_binary_vs_linear():
    W, H = 840, 360
    f = []

    # Ліва колонка: Класичні лінійні вставки
    f.append(rect(50, 60, 350, 260, fill="#fcfcfc", stroke="#b0bec5", sw=1.5, rx=6))
    f.append(text(225, 88, "Лінійні вставки (Linear Insertion)", size=14, color=INK, bold=True))
    f.append(line(70, 102, 380, 102, color="#cfd8dc", sw=1))

    f.append(fitbox(65, 115, 320, 185,
        "Пошук позиції суміщений зі зсувом:\n\n"
        "• Рухаємося справа наліво: A[j] > key.\n"
        "• Кожне порівняння супроводжується зсувом.\n\n"
        "Складність:\n"
        "• Порівняння: O(N²) у середньому / найгіршому.\n"
        "• Порівняння в найкращому: O(N) (1 на крок!).\n"
        "• Зсуви пам'яті: O(N²).\n\n"
        "Ідеально: для майже впорядкованих даних.",
        size=11, fill="#ffffff", stroke="#eceff1"))

    # Права колонка: Двійкові вставки
    f.append(rect(440, 60, 350, 260, fill="#fcfcfc", stroke="#b0bec5", sw=1.5, rx=6))
    f.append(text(615, 88, "Двійкові вставки (Binary Insertion)", size=14, color=INK, bold=True))
    f.append(line(460, 102, 770, 102, color="#cfd8dc", sw=1))

    f.append(fitbox(455, 115, 320, 185,
        "Пошук позиції відокремлений від зсуву:\n\n"
        "• Позиція шукається бінарним пошуком у A[0..i-1].\n"
        "• Після знаходження — блоковий зсув (memmove).\n\n"
        "Складність:\n"
        "• Порівняння: O(N log N) завжди (навіть у найгіршому!).\n"
        "• Порівняння в найкращому: O(N log N) (не адаптивне!).\n"
        "• Зсуви пам'яті: O(N²).\n\n"
        "Ідеально: коли операція порівняння дорога (рядки, об'єкти).",
        size=11, fill="#ffffff", stroke="#eceff1"))

    render(os.path.join(IMG, "binary-vs-linear-insertion.svg"), W, H, *f,
           title="Порівняння лінійного та двійкового сортування вставками")

# ── Фігура 4: Поріг ефективності гібридних сортувань ─────────────────────────
def fig_hybrid_cutoff():
    W, H = 820, 370
    f = []

    # Координатні осі
    ox, oy = 90, 280
    gx_len, gy_len = 380, 200

    f.append(line(ox, oy, ox + gx_len, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - gy_len, color=INK, sw=1.8))

    f.append(text(ox + gx_len, oy + 25, "Розмір підмасиву N", size=12, color=INK, anchor="end", bold=True))
    f.append(text(ox - 10, oy - gy_len + 10, "Час (нс)", size=12, color=INK, anchor="end", bold=True))

    # Зона переваги Insertion Sort (N <= 24)
    cutoff_x = ox + 150
    f.append(rect(ox, oy - gy_len + 20, 150, gy_len - 20, fill="#e8f5e9", stroke="#a5d6a7", sw=1, rx=0))
    f.append(text(ox + 75, oy - gy_len + 40, "Зона переваги", size=11, color=BORDER_SORT, bold=True))
    f.append(text(ox + 75, oy - gy_len + 56, "Insertion Sort", size=11, color=BORDER_SORT, bold=True))

    # Поділки на осі X
    ticks = [(0, "0"), (75, "16"), (150, "32"), (225, "48"), (300, "64")]
    for tx, lbl in ticks:
        f.append(line(ox + tx, oy, ox + tx, oy + 5, color=INK, sw=1.2))
        f.append(text(ox + tx, oy + 18, lbl, size=11, color=MUTED))

    # Вертикальна лінія порогу (N = 32)
    f.append(line(cutoff_x, oy, cutoff_x, oy - gy_len + 20, color=POS, sw=1.5, dash="4,4"))
    f.append(text(cutoff_x, oy + 32, "Пороговий перетин N ≈ 16..32", size=10, color=POS, bold=True))

    # Крива Insertion Sort (T(N) = c1 * N^2, але мала константа)
    pts_ins = []
    for x in range(0, 320, 15):
        val = 0.0022 * (x ** 2) + 0.15 * x + 5
        pts_ins.append(f"{ox + x:.1f},{oy - min(val, gy_len - 15):.1f}")
    f.append(f'<polyline points="{" ".join(pts_ins)}" fill="none" stroke="{BORDER_SORT}" stroke-width="2.5"/>')
    f.append(text(ox + 260, oy - 165, "Insertion Sort (O(N²))", size=11, color=BORDER_SORT, bold=True))

    # Крива Quicksort / Mergesort (T(N) = c2 * N log N + C_overhead через рекурсію)
    pts_quick = []
    for x in range(0, 320, 15):
        val = 45 + 0.38 * x + 0.0004 * (x ** 2)
        pts_quick.append(f"{ox + x:.1f},{oy - min(val, gy_len - 15):.1f}")
    f.append(f'<polyline points="{" ".join(pts_quick)}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')
    f.append(text(ox + 290, oy - 120, "Quicksort (O(N log N))", size=11, color=NEG, bold=True))

    # Пояснювальний блок праворуч
    rx = 500
    f.append(fitbox(rx, 65, 290, 245,
        "Чому гібридні сортування перемикаються:\n\n"
        "1. Нульовий оверхед виклику:\n"
        "   Quicksort/Mergesort витрачають 30–50 нс\n"
        "   на створення стекового кадру рекурсії.\n\n"
        "2. Кеш-локальність L1:\n"
        "   Підмасив із 16–32 чисел (64–128 байтів)\n"
        "   повністю вміщується в 1–2 кеш-лінії CPU.\n\n"
        "3. Відсутність branch mispredictions:\n"
        "   На малих впорядкованих відрізках процесор\n"
        "   передбачає переходи з точністю >98%.\n\n"
        "Використовується в: Timsort, std::sort (Introsort).",
        size=11, fill="#f8f9fa", stroke="#cfd8dc"))

    render(os.path.join(IMG, "hybrid-cutoff.svg"), W, H, *f,
           title="Поріг перемикання алгоритмів у гібридних сортуваннях")

def main():
    fig_mechanism()
    fig_inversions()
    fig_binary_vs_linear()
    fig_hybrid_cutoff()
    print("Всі 4 фігури успішно згенеровано у ./img")

if __name__ == "__main__":
    main()
