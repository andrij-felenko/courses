# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори
C_CRIT  = POS            # Критичний шлях (червоний)
C_NODE  = "#2457d6"      # Звичайні вузли (синій)
C_SPAWN = "#8e44ad"      # Spawn-ребра (фіолетовий)
C_SYNC  = "#16a085"      # Sync-ребра (бірюзовий)
C_CONT  = "#333333"      # Послідовні продовження (темно-сірий)
C_BOX   = "#f8fafc"      # Світле тло панелей


# ── Фігура 1: Обчислювальний граф (DAG) та критичний шлях ──────────────────────
def fig_work_span_dag():
    W, H = 960, 560
    p = []

    # Заголовок графіка / зони
    p.append(text(280, 32, "Обчислювальний граф задачі (DAG)", size=16, color=INK, bold=True))
    p.append(text(280, 54, "Критичний шлях (Span) виділено червоним", size=12.5, color=MUTED))

    # Координати вузлів графа (cx, cy)
    nodes = {
        "v1": (280, 95,  "v₁", "w=1", True),
        "v2": (170, 185, "v₂", "w=3", True),
        "v3": (390, 185, "v₃", "w=2", False),
        "v4": (110, 285, "v₄", "w=4", True),
        "v5": (230, 285, "v₅", "w=1", False),
        "v6": (390, 285, "v₆", "w=2", False),
        "v7": (170, 395, "v₇", "w=3", True),
        "v8": (390, 395, "v₈", "w=1", False),
        "v9": (280, 495, "v₉", "w=1", True),
    }

    # Ребра: (from, to, type, is_critical)
    edges = [
        ("v1", "v2", "spawn", True),
        ("v1", "v3", "spawn", False),
        ("v2", "v4", "spawn", True),
        ("v2", "v5", "cont",  False),
        ("v3", "v6", "cont",  False),
        ("v4", "v7", "cont",  True),
        ("v5", "v7", "sync",  False),
        ("v6", "v8", "cont",  False),
        ("v7", "v9", "sync",  True),
        ("v8", "v9", "sync",  False),
    ]

    # Малювання ребер
    for f_id, t_id, e_type, is_crit in edges:
        fx, fy, _, _, _ = nodes[f_id]
        tx, ty, _, _, _ = nodes[t_id]

        if is_crit:
            col = C_CRIT
            w_line = 2.8
            dash = None
        elif e_type == "spawn":
            col = C_SPAWN
            w_line = 1.8
            dash = "4 3"
        elif e_type == "sync":
            col = C_SYNC
            w_line = 1.8
            dash = "3 3"
        else:
            col = C_CONT
            w_line = 1.6
            dash = None

        dx = tx - fx
        dy = ty - fy
        dist = math.hypot(dx, dy)
        if dist > 0:
            ux = dx / dist
            uy = dy / dist
            x1 = fx + ux * 24
            y1 = fy + uy * 24
            x2 = tx - ux * 26
            y2 = ty - uy * 26
            d_str = ' stroke-dasharray="%s"' % dash if dash else ''
            p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" marker-end="url(#arrow)"%s/>'
                     % (x1, y1, x2, y2, col, w_line, d_str))

    # Малювання вузлів
    for n_id, (cx, cy, label, w_text, is_crit) in nodes.items():
        fill_col = "#fdecea" if is_crit else "#eaf0fd"
        stroke_col = C_CRIT if is_crit else C_NODE
        sw = 2.4 if is_crit else 1.8

        p.append(circle(cx, cy, 24, fill=fill_col, stroke=stroke_col, sw=sw))
        p.append(text(cx, cy - 3, label, size=13, color=stroke_col, bold=True))
        p.append(text(cx, cy + 12, w_text, size=10, color=MUTED))

    # Легенда ребер ліворуч унизу
    p.append(rect(20, 430, 180, 115, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=6))
    p.append(text(110, 448, "Типи зв'язків", size=12, color=INK, bold=True))

    p.append(line(35, 468, 65, 468, color=C_CRIT, sw=2.5))
    p.append(text(75, 472, "Критичний шлях", size=11, color=INK, anchor="start"))

    p.append(line(35, 490, 65, 490, color=C_SPAWN, sw=1.8, dash="4 3"))
    p.append(text(75, 494, "Spawn (розгалуження)", size=11, color=INK, anchor="start"))

    p.append(line(35, 512, 65, 512, color=C_SYNC, sw=1.8, dash="3 3"))
    p.append(text(75, 516, "Sync / Join (синхронізація)", size=11, color=INK, anchor="start"))

    p.append(line(35, 532, 65, 532, color=C_CONT, sw=1.6))
    p.append(text(75, 536, "Послідовне продовження", size=11, color=INK, anchor="start"))

    # Права інформаційна панель із розрахунками
    rx, ry, rw, rh = 540, 55, 400, 485
    p.append(rect(rx, ry, rw, rh, fill=C_BOX, stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(rx + rw / 2, ry + 28, "Метрики графа виконання", size=15, color=INK, bold=True))
    p.append(line(rx + 15, ry + 42, rx + rw - 15, ry + 42, color="#cbd5e1", sw=1.2))

    # Блок 1: Робота T1
    by1 = ry + 60
    p.append(rect(rx + 15, by1, rw - 30, 85, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=6))
    p.append(text(rx + 25, by1 + 22, "1. Загальна робота  T₁  (Work)", size=13, color=C_NODE, bold=True, anchor="start"))
    p.append(text(rx + 25, by1 + 42, "Час виконання всієї програми на 1 процесорі.", size=11.5, color=MUTED, anchor="start"))
    p.append(text(rx + 25, by1 + 60, "Сума ваг усіх 9 вузлів DAG:", size=11.5, color=INK, anchor="start"))
    p.append(text(rx + 25, by1 + 76, "T₁ = 1 + 3 + 2 + 4 + 1 + 2 + 3 + 1 + 1 = 18 тактів", size=11.5, color=C_NODE, bold=True, anchor="start"))

    # Блок 2: Глибина T_inf
    by2 = by1 + 100
    p.append(rect(rx + 15, by2, rw - 30, 95, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=6))
    p.append(text(rx + 25, by2 + 22, "2. Глибина / Критичний шлях  T_∞  (Span)", size=13, color=C_CRIT, bold=True, anchor="start"))
    p.append(text(rx + 25, by2 + 42, "Час на системі з нескінченною кількістю ядер (P → ∞).", size=11.5, color=MUTED, anchor="start"))
    p.append(text(rx + 25, by2 + 60, "Найдовший спрямований шлях: v₁ → v₂ → v₄ → v₇ → v₉", size=11.5, color=INK, anchor="start"))
    p.append(text(rx + 25, by2 + 78, "T_∞ = 1 + 3 + 4 + 3 + 1 = 12 тактів", size=11.5, color=C_CRIT, bold=True, anchor="start"))

    # Блок 3: Паралелізм
    by3 = by2 + 110
    p.append(rect(rx + 15, by3, rw - 30, 105, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
    p.append(text(rx + 25, by3 + 22, "3. Граничний паралелізм  P_max = T₁ / T_∞", size=13, color=FIELD, bold=True, anchor="start"))
    p.append(text(rx + 25, by3 + 42, "Середня кількість роботи на один крок глибини:", size=11.5, color=MUTED, anchor="start"))
    p.append(text(rx + 25, by3 + 62, "P_max = 18 / 12 = 1.5", size=13, color=FIELD, bold=True, anchor="start"))
    p.append(text(rx + 25, by3 + 82, "Висновок: додавання більше ніж 2 ядер не прискорить цей", size=11, color=INK, anchor="start"))
    p.append(text(rx + 25, by3 + 97, "граф, оскільки виконання обмежене критичним шляхом.", size=11, color=INK, anchor="start"))

    # Нижня рамка із законами
    by4 = by3 + 120
    p.append(rect(rx + 15, by4, rw - 30, 50, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(rx + rw / 2, by4 + 20, "Фундаментальна межа часу:  T_P ≥ max(T₁/P, T_∞)", size=12, color=INK, bold=True))
    p.append(text(rx + rw / 2, by4 + 38, "Неможливо виконати швидше ніж T_∞ за будь-якого P.", size=11, color=MUTED))

    render(os.path.join(OUT, "work-span-dag.svg"), W, H, *p)


# ── Фігура 2: Криві прискорення та коліно насичення ────────────────────────────
def fig_parallel_speedup_knee():
    W, H = 940, 540
    p = []
    ox, oy = 85.0, 450.0
    pw, ph = 540.0, 370.0
    P_max = 64.0
    S_max = 32.0

    def X(proc):
        return ox + pw * (proc - 1.0) / (P_max - 1.0)

    def Y(spd):
        return oy - ph * min(spd, S_max) / S_max

    # Осі
    p.append(line(ox, oy, ox + pw + 15, oy, color=INK, sw=1.5))
    p.append(line(ox, oy, ox, oy - ph - 15, color=INK, sw=1.5))
    p.append(text(ox + pw / 2, oy + 42, "кількість виділених ядер / процесорів  (P)  →", size=13, color=INK, bold=True))
    p.append('<text transform="translate(%.1f,%.1f) rotate(-90)" font-family="%s" '
             'font-size="13" font-weight="700" fill="%s" text-anchor="middle">%s</text>'
             % (ox - 55, oy - ph / 2, FONT, INK, esc("реальне прискорення  S_P = T₁ / T_P  →")))

    # Позначки осі X
    for p_val in [1, 8, 16, 24, 32, 40, 48, 56, 64]:
        x_pos = X(p_val)
        p.append(line(x_pos, oy, x_pos, oy + 5, color=INK, sw=1.2))
        p.append(text(x_pos, oy + 20, str(p_val), size=11.5, color=INK))
        if p_val > 1:
            p.append(line(x_pos, oy, x_pos, oy - ph, color="#e5e7eb", sw=1.0, dash="3 3"))

    # Позначки осі Y
    for s_val in [1, 4, 8, 12, 16, 20, 24, 28, 32]:
        y_pos = Y(s_val)
        p.append(line(ox - 5, y_pos, ox, y_pos, color=INK, sw=1.2))
        p.append(text(ox - 12, y_pos + 4, "%d×" % s_val, size=11.5, color=INK, anchor="end"))
        if s_val > 1:
            p.append(line(ox, y_pos, ox + pw, y_pos, color="#e5e7eb", sw=1.0, dash="3 3"))

    # Ідеальне лінійне прискорення S_P = P
    pts_ideal = [(X(1), Y(1)), (X(32), Y(32))]
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#94a3b8" stroke-width="1.8" stroke-dasharray="5 4"/>'
             % (pts_ideal[0][0], pts_ideal[0][1], pts_ideal[1][0], pts_ideal[1][1]))
    p.append(text(X(28) - 15, Y(29), "Ідеальне лінійне S_P = P", size=11, color="#64748b", bold=True, italic=True))

    def plot_brent(par, color):
        pts = []
        proc = 1.0
        while proc <= P_max + 1e-6:
            s_val = proc / (1.0 + (proc - 1.0) / par)
            pts.append((X(proc), Y(s_val)))
            proc += 0.5
        poly = " ".join("%.1f,%.1f" % (x_pt, y_pt) for x_pt, y_pt in pts)
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (poly, color))

    # 1. Високий паралелізм Par = 250
    C_HIGH = FIELD
    plot_brent(250.0, C_HIGH)

    # 2. Помірний паралелізм Par = 20
    C_MID = "#2457d6"
    plot_brent(20.0, C_MID)

    # 3. Низький паралелізм Par = 6
    C_LOW = POS
    plot_brent(6.0, C_LOW)

    # Асимптотичні стелі
    for par_val, col, txt in [
        (20.0, C_MID, "стеля T₁/T_∞ = 20×"),
        (6.0, C_LOW, "стеля T₁/T_∞ = 6×"),
    ]:
        y_ceil = Y(par_val)
        p.append(line(ox, y_ceil, ox + pw, y_ceil, color=col, sw=1.2, dash="4 4"))
        p.append(text(ox + pw - 8, y_ceil - 6, txt, size=11, color=col, bold=True, anchor="end"))

    # Позначка коліна (knee point) для помірного паралелізму
    knee_x = X(20)
    knee_y = Y(10.5)
    p.append(circle(knee_x, knee_y, 6, fill="#ffffff", stroke=C_MID, sw=2.5))
    p.append(line(knee_x, knee_y + 8, knee_x, oy - 28, color=C_MID, sw=1.2, dash="3 3"))
    p.append(text(knee_x, oy - 12, "P ≈ T₁/T_∞ (коліно)", size=10.5, color=C_MID, bold=True))

    # Права панель з поясненнями режимів
    rx, ry, rw, rh = 650, 50, 275, 480
    p.append(rect(rx, ry, rw, rh, fill=C_BOX, stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(rx + rw / 2, ry + 26, "Три режими паралелізму", size=14, color=INK, bold=True))
    p.append(line(rx + 12, ry + 38, rx + rw - 12, ry + 38, color="#cbd5e1", sw=1.2))

    # Режим 1: Високий запас
    by1 = ry + 50
    p.append(rect(rx + 10, by1, rw - 20, 110, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
    p.append(text(rx + 18, by1 + 18, "1. Зона лінійного росту", size=12.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(rx + 18, by1 + 36, "Умова: P ≪ T₁ / T_∞", size=11.5, color=INK, bold=True, anchor="start"))
    p.append(text(rx + 18, by1 + 54, "Паралельний запас високий.", size=11, color=MUTED, anchor="start"))
    p.append(text(rx + 18, by1 + 72, "Кожен процесор отримує", size=11, color=MUTED, anchor="start"))
    p.append(text(rx + 18, by1 + 88, "роботу. S_P ≈ P (майже 100%).", size=11, color=FIELD, bold=True, anchor="start"))

    # Режим 2: Коліно
    by2 = by1 + 122
    p.append(rect(rx + 10, by2, rw - 20, 115, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=6))
    p.append(text(rx + 18, by2 + 18, "2. Точка зламу (Коліно)", size=12.5, color="#2457d6", bold=True, anchor="start"))
    p.append(text(rx + 18, by2 + 36, "Умова: P ≈ T₁ / T_∞", size=11.5, color=INK, bold=True, anchor="start"))
    p.append(text(rx + 18, by2 + 54, "Кількість ядер зрівнюється", size=11, color=MUTED, anchor="start"))
    p.append(text(rx + 18, by2 + 72, "з середнім паралелізмом.", size=11, color=MUTED, anchor="start"))
    p.append(text(rx + 18, by2 + 90, "Ефективність падає до ≈ 50%.", size=11, color="#2457d6", bold=True, anchor="start"))

    # Режим 3: Насичення
    by3 = by2 + 127
    p.append(rect(rx + 10, by3, rw - 20, 125, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=6))
    p.append(text(rx + 18, by3 + 18, "3. Плато насичення", size=12.5, color=POS, bold=True, anchor="start"))
    p.append(text(rx + 18, by3 + 36, "Умова: P ≫ T₁ / T_∞", size=11.5, color=INK, bold=True, anchor="start"))
    p.append(text(rx + 18, by3 + 54, "Дефіцит готових задач.", size=11, color=MUTED, anchor="start"))
    p.append(text(rx + 18, by3 + 72, "Час затиснутий критичним", size=11, color=MUTED, anchor="start"))
    p.append(text(rx + 18, by3 + 90, "шляхом: T_P → T_∞.", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(rx + 18, by3 + 108, "Додавання ядер марне.", size=11, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "parallel-speedup-knee.svg"), W, H, *p)


# ── Фігура 3: Порівняння топологій DAG для Merge Sort ─────────────────────────
def fig_merge_sort_dags():
    W, H = 960, 520
    p = []

    # Заголовок
    p.append(text(W / 2, 30, "Алгоритмічна пастка: наївне злиття проти паралельного", size=16, color=INK, bold=True))

    # Ліва колонка: Наївний підхід
    lx = 30
    lw = 435
    p.append(rect(lx, 55, lw, 445, fill="#fff5f5", stroke="#fca5a5", sw=1.5, rx=8))
    p.append(text(lx + lw / 2, 80, "А. Наївний паралельний Merge Sort", size=14.5, color=POS, bold=True))
    p.append(text(lx + lw / 2, 100, "Паралельний spawn підмасивів + послідовне злиття", size=11.5, color=MUTED))

    # Схема DAG наївного сортування
    p.append(circle(lx + lw / 2, 140, 18, fill="#ffffff", stroke=POS, sw=2))
    p.append(text(lx + lw / 2, 144, "Sort(N)", size=9.5, color=POS, bold=True))

    p.append(line(lx + lw / 2 - 12, 154, lx + lw / 4 + 10, 195, color=C_SPAWN, sw=1.5, dash="3 3"))
    p.append(line(lx + lw / 2 + 12, 154, lx + 3 * lw / 4 - 10, 195, color=C_SPAWN, sw=1.5, dash="3 3"))

    # Рівень 2 (підзадачі)
    p.append(circle(lx + lw / 4, 210, 16, fill="#ffffff", stroke=C_NODE, sw=1.5))
    p.append(text(lx + lw / 4, 214, "N/2", size=10, color=C_NODE))

    p.append(circle(lx + 3 * lw / 4, 210, 16, fill="#ffffff", stroke=C_NODE, sw=1.5))
    p.append(text(lx + 3 * lw / 4, 214, "N/2", size=10, color=C_NODE))

    p.append(text(lx + lw / 2, 214, ". . .", size=14, color=MUTED))

    # Рівень 3 (листя рекурсії)
    p.append(text(lx + lw / 2, 265, "[ 2^k паралельних підмасивів розміру O(1) ]", size=11, color=MUTED))

    # Рівень 4: Блокувальне послідовне злиття нагорі
    p.append(arrow(lx + lw / 4, 280, lx + lw / 2 - 20, 315, color=POS, sw=2.2))
    p.append(arrow(lx + 3 * lw / 4, 280, lx + lw / 2 + 20, 315, color=POS, sw=2.2))

    p.append(rect(lx + 45, 315, lw - 90, 50, fill="#fee2e2", stroke=POS, sw=2, rx=6))
    p.append(text(lx + lw / 2, 335, "ПОСЛІДОВНЕ ЗЛИТТЯ: Merge(N)", size=12, color=POS, bold=True))
    p.append(text(lx + lw / 2, 352, "Вага вузла = O(N) тактів на 1 ядрі!", size=11, color=POS, bold=True))

    # Характеристики наївного підходу
    p.append(rect(lx + 20, 385, lw - 40, 100, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6))
    p.append(text(lx + 30, 405, "Робота T₁:", size=11.5, color=INK, bold=True, anchor="start"))
    p.append(text(lx + 130, 405, "O(N log N)  [оптимальна]", size=11.5, color=FIELD, bold=True, anchor="start"))

    p.append(text(lx + 30, 425, "Глибина T_∞:", size=11.5, color=INK, bold=True, anchor="start"))
    p.append(text(lx + 130, 425, "O(N)  [вузьке місце нагорі]", size=11.5, color=POS, bold=True, anchor="start"))

    p.append(text(lx + 30, 445, "Паралелізм:", size=11.5, color=INK, bold=True, anchor="start"))
    p.append(text(lx + 130, 445, "T₁ / T_∞ = O(log N)", size=11.5, color=POS, bold=True, anchor="start"))

    p.append(text(lx + 30, 468, "Для N = 1 000 000: паралелізм лише ≈ 20× на будь-яких ядрах!", size=10.5, color=POS, bold=True, anchor="start"))

    # Права колонка: Повноцінне паралельне сортування
    rx = 495
    rw = 435
    p.append(rect(rx, 55, rw, 445, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    p.append(text(rx + rw / 2, 80, "Б. Повноцінний паралельний Merge Sort", size=14.5, color=FIELD, bold=True))
    p.append(text(rx + rw / 2, 100, "Паралельний поділ + паралельне бінарне злиття", size=11.5, color=MUTED))

    # Схема DAG паралельного злиття
    p.append(circle(rx + rw / 2, 140, 18, fill="#ffffff", stroke=FIELD, sw=2))
    p.append(text(rx + rw / 2, 144, "Sort(N)", size=9.5, color=FIELD, bold=True))

    p.append(line(rx + rw / 2 - 12, 154, rx + rw / 4 + 10, 195, color=C_SPAWN, sw=1.5, dash="3 3"))
    p.append(line(rx + rw / 2 + 12, 154, rx + 3 * rw / 4 - 10, 195, color=C_SPAWN, sw=1.5, dash="3 3"))

    p.append(circle(rx + rw / 4, 210, 16, fill="#ffffff", stroke=FIELD, sw=1.5))
    p.append(text(rx + rw / 4, 214, "N/2", size=10, color=FIELD))

    p.append(circle(rx + 3 * rw / 4, 210, 16, fill="#ffffff", stroke=FIELD, sw=1.5))
    p.append(text(rx + 3 * rw / 4, 214, "N/2", size=10, color=FIELD))

    p.append(text(rx + rw / 2, 214, ". . .", size=14, color=MUTED))

    # Рівень злиття: Деревоподібне паралельне злиття
    p.append(text(rx + rw / 2, 265, "[ Паралельне злиття через бінарний поділ медіани ]", size=11, color=FIELD))

    p.append(rect(rx + 45, 295, rw - 90, 70, fill="#dcfce7", stroke=FIELD, sw=2, rx=6))
    p.append(text(rx + rw / 2, 315, "ПАРАЛЕЛЬНЕ ЗЛИТТЯ: ParallelMerge", size=12, color=FIELD, bold=True))
    p.append(text(rx + rw / 2, 332, "Деревоподібна декомпозиція глибиною O(log² N)", size=11, color=INK))
    p.append(text(rx + rw / 2, 350, "Кожен крок виконується паралельно багатьма ядрами", size=10.5, color=MUTED))

    # Характеристики паралельного підходу
    p.append(rect(rx + 20, 385, rw - 40, 100, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6))
    p.append(text(rx + 30, 405, "Робота T₁:", size=11.5, color=INK, bold=True, anchor="start"))
    p.append(text(rx + 130, 405, "O(N log N)  [робочо-ефективна]", size=11.5, color=FIELD, bold=True, anchor="start"))

    p.append(text(rx + 30, 425, "Глибина T_∞:", size=11.5, color=INK, bold=True, anchor="start"))
    p.append(text(rx + 130, 425, "O(log³ N) або O(log² N)", size=11.5, color=FIELD, bold=True, anchor="start"))

    p.append(text(rx + 30, 445, "Паралелізм:", size=11.5, color=INK, bold=True, anchor="start"))
    p.append(text(rx + 130, 445, "T₁ / T_∞ = O(N / log² N)", size=11.5, color=FIELD, bold=True, anchor="start"))

    p.append(text(rx + 30, 468, "Для N = 1 000 000: паралелізм зростає до ≈ 2500× !", size=10.5, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "merge-sort-dags.svg"), W, H, *p)


# ── Фігура 4: Кроки жадібного планувальника (Теорема Брента) ───────────────────
def fig_greedy_schedule_steps():
    W, H = 940, 490
    p = []

    # Заголовок
    p.append(text(W / 2, 28, "Анатомія кроків жадібного планувальника (Теорема Брента)", size=16, color=INK, bold=True))
    p.append(text(W / 2, 48, "Розподіл обчислювальних кроків для системи з P = 3 процесорів", size=12.5, color=MUTED))

    # Схема часової шкали
    ox, oy = 70, 95
    step_w = 95
    step_h = 240

    steps_data = [
        ("t = 1", "Повний", 3, ["A₁", "A₂", "A₃"], True),
        ("t = 2", "Неповний", 1, ["B₁", "—", "—"], False),
        ("t = 3", "Повний", 3, ["C₁", "C₂", "C₃"], True),
        ("t = 4", "Неповний", 2, ["D₁", "D₂", "—"], False),
        ("t = 5", "Повний", 3, ["E₁", "E₂", "E₃"], True),
        ("t = 6", "Повний", 3, ["F₁", "F₂", "F₃"], True),
        ("t = 7", "Неповний", 1, ["G₁", "—", "—"], False),
    ]

    for i, (t_lbl, k_type, count, cores, is_full) in enumerate(steps_data):
        x = ox + i * (step_w + 18)
        col_bg = "#f0fdf4" if is_full else "#fff7ed"
        col_border = FIELD if is_full else "#ea580c"

        p.append(rect(x, oy, step_w, step_h, fill=col_bg, stroke=col_border, sw=1.6, rx=6))
        p.append(text(x + step_w / 2, oy + 22, t_lbl, size=13, color=INK, bold=True))
        p.append(text(x + step_w / 2, oy + 38, k_type, size=11, color=col_border, bold=True))
        p.append(line(x + 8, oy + 46, x + step_w - 8, oy + 46, color="#cbd5e1", sw=1.0))

        for c_idx, task_name in enumerate(cores):
            cy = oy + 60 + c_idx * 55
            is_idle = (task_name == "—")
            t_bg = "#f1f5f9" if is_idle else ("#dcfce7" if is_full else "#ffedd5")
            t_border = "#94a3b8" if is_idle else (FIELD if is_full else "#ea580c")
            t_col = MUTED if is_idle else INK

            p.append(rect(x + 10, cy, step_w - 20, 42, fill=t_bg, stroke=t_border, sw=1.2, rx=4))
            p.append(text(x + 20, cy + 18, "Ядро %d" % (c_idx + 1), size=9.5, color=MUTED, anchor="start"))
            p.append(text(x + step_w - 20, cy + 26, task_name, size=12, color=t_col, bold=not is_idle, anchor="end"))

        if not is_full:
            p.append(rect(x + 6, oy + step_h - 26, step_w - 12, 20, fill="#ffedd5", stroke="#f97316", sw=1.0, rx=3))
            p.append(text(x + step_w / 2, oy + step_h - 13, "ΔSpan ≥ 1", size=10, color="#c2410c", bold=True))
        else:
            p.append(text(x + step_w / 2, oy + step_h - 13, "3 вузли роботи", size=10, color=FIELD))

    # Нижня підсумкова панель
    by = oy + step_h + 20
    bw = W - 140
    p.append(rect(ox, by, bw, 115, fill=C_BOX, stroke="#cbd5e1", sw=1.5, rx=8))

    p.append(text(ox + 20, by + 25, "1. Повні кроки (усі P процесорів працюють):", size=12.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(ox + 35, by + 45, "Виконують рівно P вузлів. Кількість таких кроків k_full ≤ ⌊(T₁ - T_∞) / P⌋.", size=11.5, color=INK, anchor="start"))
    p.append(text(ox + 35, by + 63, "У нашому прикладі: 4 повні кроки × 3 ядра = 12 виконаних одиниць роботи.", size=11, color=MUTED, anchor="start"))

    p.append(text(ox + 20, by + 85, "2. Неповні кроки (готових вузлів < P):", size=12.5, color="#ea580c", bold=True, anchor="start"))
    p.append(text(ox + 35, by + 103, "Оскільки жадібний шедулер бере ВСІ готові вузли, критичний шлях зменшується на ≥ 1.", size=11.5, color=INK, anchor="start"))

    p.append(rect(ox + bw - 280, by + 12, 265, 90, fill="#ffffff", stroke="#93c5fd", sw=1.5, rx=6))
    p.append(text(ox + bw - 147, by + 34, "Теорема Брента:", size=13, color="#1d4ed8", bold=True))
    p.append(text(ox + bw - 147, by + 56, "T_P ≤ ⌊(T₁ - T_∞) / P⌋ + T_∞", size=12.5, color="#1d4ed8", bold=True))
    p.append(text(ox + bw - 147, by + 76, "T_P < T₁ / P + T_∞", size=12, color=INK, bold=True))
    p.append(text(ox + bw - 147, by + 93, "Шедулер у межах 2× від оптимуму!", size=10.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "greedy-schedule-steps.svg"), W, H, *p)


if __name__ == "__main__":
    fig_work_span_dag()
    fig_parallel_speedup_knee()
    fig_merge_sort_dags()
    fig_greedy_schedule_steps()
    print("All figures generated successfully.")
