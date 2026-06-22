# -*- coding: utf-8 -*-
"""Фігури до теми «Пріоритети переривань».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# теплий жовтий для «контекст»-плиток і нот
WARM = "#fff6e0"
WARMS = "#caa24a"


# ── 1. Навіщо пріоритети: три джерела подій сходяться в один процесор ──────────
def fig_why_priority():
    W, H = 860, 300
    f = [text(W / 2, 30, "Не всі події однаково термінові", size=15, bold=True)]

    cx_proc = 620
    # три джерела ліворуч
    srcs = [
        (90, "аварія живлення", "пріоритет: високий", POS, "#fdecea"),
        (90, "точний таймер", "пріоритет: середній", FIELD, "#eef6ef"),
        (90, "натиск кнопки", "пріоритет: низький", NEG, "#eaf0fd"),
    ]
    ys = [80, 150, 220]
    bw, bh = 250, 56
    proc_cy = 150
    proc_cx = cx_proc + 70
    for (x, name, prio, col, fillc), y in zip(srcs, ys):
        f.append(rect(x, y, bw, bh, fill=fillc, stroke=col, sw=1.8))
        f.append(text(x + 16, y + 24, name, size=12, color=INK, anchor="start", bold=True))
        f.append(text(x + 16, y + 44, prio, size=10.5, color=col, anchor="start", bold=True))
        # стрілка до процесора
        f.append(arrow(x + bw + 4, y + bh / 2, proc_cx - 86, proc_cy, color=col, sw=1.8))

    # один процесор
    pb, pw, ph = textbox(proc_cx, proc_cy, "процесор\n(один)", size=13,
                         fill=WARM, stroke=WARMS, sw=2, bold=True, min_w=150)
    f.append(pb)

    f.append(text(W / 2, 280,
                  "пріоритет — число терміновості: за ним процесор вирішує, кого пустити першим",
                  size=11, color=INK, bold=True))
    render(os.path.join(IMG, "why-priority.svg"), W, H, *f)


# ── 2. Витіснення: високе переривання перебиває низьке ────────────────────────
def fig_preemption():
    W, H = 900, 360
    f = [text(W / 2, 30, "Витіснення: важливіше переривання перебиває менш важливе",
              size=15, bold=True)]

    lab_x = 30
    lane_main = 110   # основний код (синій)
    lane_low = 190    # низький ISR (зелений)
    lane_high = 270   # високий ISR (червоний)
    bh = 34

    f.append(text(lab_x, lane_main + 6, "основний код", size=10.5, color=NEG, anchor="start", bold=True))
    f.append(text(lab_x, lane_low + 6, "низький ISR", size=10.5, color=FIELD, anchor="start", bold=True))
    f.append(text(lab_x, lane_high + 6, "високий ISR", size=10.5, color=POS, anchor="start", bold=True))

    # часова шкала
    x0 = 170
    # основний код (зліва)
    f.append(rect(x0, lane_main - bh / 2, 130, bh, fill="#eaf0fd", stroke=NEG, sw=1.8))
    # низький ISR починається
    low_a_x = x0 + 130
    low_a_w = 150
    f.append(rect(low_a_x, lane_low - bh / 2, low_a_w, bh, fill="#eef6ef", stroke=FIELD, sw=1.8))
    # точка надходження високого
    hi_x = low_a_x + 95
    f.append(line(hi_x, lane_low + bh / 2, hi_x, lane_high - bh / 2, color=POS, sw=1.4, dash="3,3"))
    f.append(text(hi_x, lane_high - bh / 2 - 8, "високе переривання надходить",
                  size=10, color=POS, bold=True))
    # високий ISR біжить
    high_x = hi_x
    high_w = 180
    f.append(rect(high_x, lane_high - bh / 2, high_w, bh, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(high_x + high_w / 2, lane_high + 5, "високий ISR", size=10, color=POS, bold=True))
    # повертаємось до низького (друга зелена)
    low_b_x = high_x + high_w
    low_b_w = 160
    f.append(line(low_b_x, lane_high - bh / 2, low_b_x, lane_low + bh / 2, color=FIELD, sw=1.4, dash="3,3"))
    f.append(rect(low_b_x, lane_low - bh / 2, low_b_w, bh, fill="#eef6ef", stroke=FIELD, sw=1.8))
    f.append(text(low_b_x + low_b_w / 2, lane_low + 5, "низький ISR — далі", size=9.5, color=FIELD, bold=True))
    # основний код (справа)
    main_b_x = low_b_x + low_b_w
    f.append(rect(main_b_x, lane_main - bh / 2, 110, bh, fill="#eaf0fd", stroke=NEG, sw=1.8))

    # стрілка часу
    f.append(arrow(x0, 318, main_b_x + 110, 318, color=MUTED, sw=1.4))
    f.append(text(main_b_x + 110, 312, "час", size=10, color=MUTED, anchor="end"))

    f.append(text(W / 2, 348,
                  "низький поступається високому; коли той завершиться — доробляє з того самого місця",
                  size=11, color=INK, bold=True))
    render(os.path.join(IMG, "preemption.svg"), W, H, *f)


# ── 3. Вкладеність: контексти складаються на стек ─────────────────────────────
def fig_nesting_stack():
    W, H = 920, 400
    f = [text(W / 2, 30, "Вкладеність: контексти складаються на стек", size=15, bold=True)]

    fx0 = 50
    fw = 180
    gap = 30
    fy = 110
    fh = 210
    tile_w = 148
    tile_h = 30

    frames = [
        ("основний код", []),
        ("+ низький ISR", ["контекст осн."]),
        ("+ високий ISR", ["контекст осн.", "контекст низ."]),
        ("повертаємось", ["контекст осн."]),
    ]
    centers = []
    for i, (lab, tiles) in enumerate(frames):
        x = fx0 + i * (fw + gap)
        cx = x + fw / 2
        centers.append((x, cx))
        f.append(text(cx, fy - 14, lab, size=11, color=INK, bold=True))
        f.append(rect(x, fy, fw, fh, fill="#fbfcff", stroke=INK, sw=1.4))
        f.append(text(cx, fy + fh - 10, "стек", size=9.5, color=MUTED))
        if not tiles:
            f.append(text(cx, fy + fh / 2, "(порожній)", size=10, color=MUTED, italic=True))
        # плитки кладемо знизу вгору
        for j, t in enumerate(tiles):
            ty = fy + fh - 24 - (j + 1) * (tile_h + 6)
            tx = cx - tile_w / 2
            f.append(rect(tx, ty, tile_w, tile_h, fill=WARM, stroke=WARMS, sw=1.4, rx=5))
            f.append(text(cx, ty + tile_h / 2 + 4, t, size=9.5, color=INK))

    # стрілки між рамками
    arr_y = fy + fh / 2
    for i in range(3):
        x_right = centers[i][0] + fw
        x_next = centers[i + 1][0]
        f.append(arrow(x_right + 4, arr_y, x_next - 4, arr_y, color=INK, sw=2))

    f.append(text(W / 2, 360,
                  "що глибша вкладеність — то більше контекстів;", size=11, color=INK, bold=True))
    f.append(text(W / 2, 380,
                  "останній покладений знімається першим (LIFO)", size=10.5, color=MUTED))
    render(os.path.join(IMG, "nesting-stack.svg"), W, H, *f)


# ── 4. Однаковий рівень не витісняє: друге переривання чекає ──────────────────
def fig_same_level():
    W, H = 860, 320
    f = [text(W / 2, 30, "Однаковий рівень не витісняє: друге переривання чекає",
              size=15, bold=True)]

    lab_x = 30
    lane_a = 120   # обробник A (рівень 1)
    lane_b = 220   # обробник B (рівень 1)
    bh = 34

    f.append(text(lab_x, lane_a + 6, "рівень 1: A", size=10.5, color=FIELD, anchor="start", bold=True))
    f.append(text(lab_x, lane_b + 6, "рівень 1: B", size=10.5, color=NEG, anchor="start", bold=True))

    x0 = 150
    a_w = 240
    f.append(rect(x0, lane_a - bh / 2, a_w, bh, fill="#eef6ef", stroke=FIELD, sw=1.8))
    f.append(text(x0 + a_w / 2, lane_a + 5, "обробник A виконується", size=10, color=FIELD, bold=True))

    # подія B приходить усередині A
    bev_x = x0 + 150
    f.append(circle(bev_x, lane_a + bh / 2 + 18, 4, fill=NEG, stroke=NEG, sw=0))
    f.append(text(bev_x, lane_a + bh / 2 + 40, "подія B (той самий рівень)",
                  size=9.5, color=NEG, bold=True))

    # B стартує тільки ПІСЛЯ кінця A
    a_end = x0 + a_w
    b_x = a_end
    b_w = 200
    f.append(rect(b_x, lane_b - bh / 2, b_w, bh, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(b_x + b_w / 2, lane_b + 5, "обробник B (чекав)", size=10, color=NEG, bold=True))
    # з'єднання кінця A → початок B
    f.append(line(a_end, lane_a + bh / 2, a_end, lane_b - bh / 2, color=INK, sw=1.4, dash="3,3"))

    # дужка «чекає» від події B до старту B
    br_y = lane_b + bh / 2 + 22
    f.append(line(bev_x, br_y, a_end, br_y, color=MUTED, sw=1.4))
    f.append(line(bev_x, br_y - 6, bev_x, br_y, color=MUTED, sw=1.4))
    f.append(line(a_end, br_y - 6, a_end, br_y, color=MUTED, sw=1.4))
    f.append(text((bev_x + a_end) / 2, br_y + 16, "B чекає", size=10, color=MUTED, bold=True))

    f.append(text(W / 2, 304,
                  "серіалізація замість вкладеності: B виконується лише після A",
                  size=11, color=INK, bold=True))
    render(os.path.join(IMG, "same-level.svg"), W, H, *f)


# ── 5. Рівні переривань ESP32: 1 (низький) … 7 (NMI) ──────────────────────────
def fig_esp32_levels():
    W, H = 820, 420
    f = [text(W / 2, 30, "Рівні переривань ESP32: від 1 (низький) до 7 (NMI)",
              size=15, bold=True)]

    # сходинка: рівень 1 внизу, 7 угорі
    steps = [
        (1, "GPIO, периферія, attachInterrupt", NEG, "#eaf0fd"),
        (2, "середні — можна на C", FIELD, "#eef6ef"),
        (3, "середні — можна на C", FIELD, "#eef6ef"),
        (4, "високі — пишуть на асемблері", POS, "#fdecea"),
        (5, "високі — пишуть на асемблері", POS, "#fdecea"),
        (6, "високі — пишуть на асемблері", POS, "#fdecea"),
        (7, "NMI — немаскований", POS, "#fdecea"),
    ]
    n = len(steps)
    base_x = 110          # лівий край найнижчої сходинки
    step_dx = 18          # зсув кожної вищої сходинки праворуч
    sw_box = 470          # ширина плашки
    bh = 40
    gap = 6
    bottom_y = 360        # верх найнижчої сходинки
    num_w = 50
    for i, (lvl, ann, col, fillc) in enumerate(steps):
        y = bottom_y - i * (bh + gap)
        x = base_x + i * step_dx
        f.append(rect(x, y, sw_box, bh, fill=fillc, stroke=col, sw=1.6))
        # номер рівня — кольоровий квадрат зліва
        f.append(rect(x, y, num_w, bh, fill=col, stroke=col, sw=0))
        f.append(text(x + num_w / 2, y + bh / 2 + 6, str(lvl), size=16, color="#ffffff", bold=True))
        # підпис у плашку (fitbox у праву частину)
        bold = (lvl == 7)
        f.append(fitbox(x + num_w + 4, y + 4, sw_box - num_w - 10, bh - 8, ann,
                        size=11, fill="none", stroke="none", color=col, bold=bold))

    # стрілка «вищий рівень витісняє нижчий» праворуч
    ax = base_x + (n - 1) * step_dx + sw_box + 30
    arr_bot = bottom_y + bh        # 400 — у межах [0..420]
    arr_top = bottom_y - (n - 1) * (bh + gap)
    f.append(arrow(ax, arr_bot, ax, arr_top, color=POS, sw=2.2))
    # підпис біля стрілки, центрований по її середині (усе в межах полотна)
    mid = (arr_top + arr_bot) / 2
    side = ["вищий", "рівень", "витісняє", "нижчий"]
    for k, ln in enumerate(side):
        f.append(text(ax + 14, mid - 24 + k * 16, ln, size=10, color=POS,
                      anchor="start", bold=(k == 0)))

    render(os.path.join(IMG, "esp32-levels.svg"), W, H, *f)


# ── 6. Глибока вкладеність може переповнити стек ──────────────────────────────
def fig_stack_danger():
    W, H = 880, 360
    f = [text(W / 2, 30, "Глибока вкладеність може переповнити стек", size=15, bold=True)]

    # стек-область
    sx, sw_box = 300, 220
    sy, sh = 70, 250
    f.append(rect(sx, sy, sw_box, sh, fill="#fbfcff", stroke=INK, sw=1.6))
    # межа пам'яті біля верху
    limit_y = sy + 28
    f.append(line(sx - 10, limit_y, sx + sw_box + 10, limit_y, color=POS, sw=2, dash="5,3"))
    f.append(text(sx + sw_box + 16, limit_y + 4, "межа пам'яті", size=10, color=POS, anchor="start", bold=True))

    # кадри знизу вгору
    frames = ["основний код", "ISR рів.1", "ISR рів.2", "ISR рів.3", "ISR рів.4 …"]
    fh = 36
    fgap = 6
    fw = sw_box - 20
    fx = sx + 10
    fills = ["#eaf0fd", "#eef6ef", WARM, "#ffe3d6", "#fbecec"]
    for j, name in enumerate(frames):
        fy = sy + sh - 12 - (j + 1) * (fh + fgap)
        col = POS if j == len(frames) - 1 else INK
        f.append(rect(fx, fy, fw, fh, fill=fills[j], stroke=col, sw=1.3, rx=4))
        txt = name + " — переповнення!" if j == len(frames) - 1 else name
        f.append(fitbox(fx + 4, fy + 4, fw - 8, fh - 8, txt, size=10,
                        fill="none", stroke="none", color=col, bold=(j == len(frames) - 1)))

    # стрілка росту стека
    f.append(arrow(sx - 24, sy + sh - 14, sx - 24, sy + 40, color=POS, sw=2))
    f.append(text(sx - 30, (sy + sh / 2), "росте", size=9.5, color=POS, anchor="middle"))

    # ноти праворуч
    nx = sx + sw_box + 40
    nb1, nbw, nbh = textbox(nx + 130, 130, "кожен вкладений ISR\nдодає кадр",
                            size=10.5, fill=FILL, stroke=LINE, min_w=240)
    f.append(nb1)
    nb2, _, _ = textbox(nx + 130, 210, "Arduino: усі ISR рівня 1\n→ вкладеності немає",
                        size=10.5, fill="#eef6ef", stroke=FIELD, min_w=240)
    f.append(nb2)

    f.append(text(W / 2, 346,
                  "захист: короткі обробники, небагато рівнів", size=11, color=INK, bold=True))
    render(os.path.join(IMG, "stack-danger.svg"), W, H, *f)


# ── 7. Перевантаження AGC: зайвий потік від радара пробиває 100% ──────────────
def fig_apollo_overload():
    W, H = 860, 360
    f = [text(W / 2, 30, "Перевантаження AGC: зайвий потік від радара пробиває 100%",
              size=15, bold=True)]

    bx = 70
    by = 120
    bh = 56
    full_w = 620          # ширина, що відповідає 100%
    # межа 100%
    limit_x = bx + full_w
    f.append(line(limit_x, by - 18, limit_x, by + bh + 18, color=POS, sw=1.8, dash="4,3"))
    f.append(text(limit_x, by - 24, "100%", size=10, color=POS, bold=True))

    # сегменти бюджету (до межі)
    segs = [
        ("наведення", 0.27, NEG, "#eaf0fd"),
        ("навігація", 0.24, NEG, "#eaf0fd"),
        ("керування", 0.24, NEG, "#eaf0fd"),
        ("дисплеї", 0.25, FIELD, "#eef6ef"),
    ]
    x = bx
    for lab, frac, col, fillc in segs:
        w = full_w * frac
        f.append(rect(x, by, w, bh, fill=fillc, stroke=col, sw=1.6, rx=0))
        f.append(fitbox(x + 2, by + 8, w - 4, bh - 16, lab, size=10,
                        fill="none", stroke="none", color=col, bold=True))
        x += w
    # зайвий червоний сегмент радара (за межу)
    radar_w = full_w * 0.13
    f.append(rect(x, by, radar_w, bh, fill="#fbecec", stroke=POS, sw=1.6, rx=0))
    f.append(text(x + radar_w / 2, by + bh + 18, "радар", size=9.5, color=POS, bold=True))
    f.append(text(x + radar_w / 2, by + bh + 32, "зустрічі ~13%", size=9, color=POS))

    # підпис переповнення
    f.append(text((limit_x + x + radar_w) / 2, by + bh / 2 + 4, "→ за межу", size=9, color=POS, bold=True))

    f.append(text(W / 2, 250,
                  "→ навантаження > 100% → аларми 1201/1202", size=13, color=POS, bold=True))
    f.append(text(W / 2, 286,
                  "виконавець не встигав розкласти всі задачі за такт", size=11, color=MUTED))
    render(os.path.join(IMG, "apollo-overload.svg"), W, H, *f)


# ── 8. Пріоритет рятує: лишити критичне, скинути другорядне ───────────────────
def fig_apollo_priority_shed():
    W, H = 860, 340
    f = [text(W / 2, 30, "Пріоритет рятує: лишити критичне, скинути другорядне",
              size=15, bold=True)]

    # ліва колонка — перевантаження
    lx, lw = 60, 280
    ly, lh = 80, 210
    f.append(rect(lx, ly, lw, lh, fill="#fbfbfb", stroke=MUTED, sw=1.6, rx=10))
    f.append(text(lx + lw / 2, ly + 24, "перевантаження", size=12, color=INK, bold=True))
    left_items = [
        ("наведення", FIELD), ("навігація", FIELD), ("керування", FIELD),
        ("дисплеї", MUTED), ("другорядне", MUTED),
    ]
    for i, (it, col) in enumerate(left_items):
        f.append(text(lx + 24, ly + 56 + i * 28, "• " + it, size=11, color=col, anchor="start",
                      bold=(col == FIELD)))

    # центральна стрілка
    f.append(arrow(lx + lw + 10, ly + lh / 2, lx + lw + 150, ly + lh / 2, color=INK, sw=2.2))
    f.append(text(lx + lw + 80, ly + lh / 2 - 12, "перезапуск", size=10, color=INK, bold=True))
    f.append(text(lx + lw + 80, ly + lh / 2 + 22, "+ пріоритет", size=10, color=INK, bold=True))

    # права колонка — після
    rx = lx + lw + 160
    rw = 280
    f.append(rect(rx, ly, rw, lh, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(rx + rw / 2, ly + 24, "після", size=12, color=FIELD, bold=True))
    right_kept = ["наведення", "навігація", "керування"]
    for i, it in enumerate(right_kept):
        f.append(text(rx + 24, ly + 56 + i * 28, "• " + it, size=11, color=FIELD, anchor="start", bold=True))
    # скинуті — сірі, перекреслені
    right_shed = ["дисплеї", "другорядне"]
    for i, it in enumerate(right_shed):
        yy = ly + 56 + (3 + i) * 28
        f.append(text(rx + 24, yy, "• " + it + " — скинуто", size=11, color=MUTED, anchor="start"))
        # лінія перекреслення
        f.append(line(rx + 24, yy - 4, rx + 24 + text_width("• " + it + " — скинуто", 11), yy - 4,
                      color=MUTED, sw=1.2))

    f.append(text(W / 2, 322,
                  "AGC не падав — робив головне, жертвуючи рештою", size=11, color=INK, bold=True))
    render(os.path.join(IMG, "apollo-priority-shed.svg"), W, H, *f)


# ── 9. Рішення за секунди: аларм → Гарман → Бейлз «GO» → екіпаж ───────────────
def fig_apollo_ground_call():
    W, H = 900, 300
    f = [text(W / 2, 30, "Рішення за секунди: аларм → Гарман → Бейлз «GO» → екіпаж",
              size=15, bold=True)]

    chain = [
        ("аларм 1202\nна дисплеї", POS, "#fdecea"),
        ("Гарман\n(список безпечних кодів)", NEG, "#eaf0fd"),
        ("Бейлз: «GO»", FIELD, "#eef6ef"),
        ("екіпаж\nпродовжує", WARMS, WARM),
    ]
    bx0 = 40
    bw = 190
    gap = 30
    by = 110
    bh = 70
    for i, (label, col, fillc) in enumerate(chain):
        x = bx0 + i * (bw + gap)
        f.append(fitbox(x, by, bw, bh, label, size=11, fill=fillc, stroke=col, color=col, bold=True))
        if i < len(chain) - 1:
            f.append(arrow(x + bw + 4, by + bh / 2, x + bw + gap - 4, by + bh / 2, color=INK, sw=2))

    f.append(text(W / 2, 230,
                  "а наперед — команда MIT (Гемілтон, Лейнінг) зробила виконавець стійким",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "apollo-ground-call.svg"), W, H, *f)


# ── 10. Латентність: дописати + вектор + контекст + блокування ────────────────
def fig_latency_timeline():
    W, H = 900, 320
    f = [text(W / 2, 30, "Латентність: дописати + вектор + контекст + блокування",
              size=15, bold=True)]

    f.append(text(60, 110, "подія (запит)", size=10.5, color=INK, anchor="start", bold=True))
    f.append(text(W - 60, 110, "1-ша інструкція ISR", size=10.5, color=NEG, anchor="end", bold=True))

    bx = 70
    by = 130
    bh = 50
    segs = [
        ("дописати\nінстр.", 110, FIELD, "#eef6ef"),
        ("вектор", 110, FIELD, "#eef6ef"),
        ("контекст", 130, FIELD, "#eef6ef"),
        ("блокування", 360, POS, "#fbecec"),
    ]
    x = bx
    fixed_x0 = x
    for i, (lab, w, col, fillc) in enumerate(segs):
        f.append(rect(x, by, w, bh, fill=fillc, stroke=col, sw=1.8, rx=5))
        f.append(fitbox(x + 2, by + 6, w - 4, bh - 12, lab, size=10,
                        fill="none", stroke="none", color=col, bold=True))
        x += w
    fixed_x1 = bx + 110 + 110 + 130   # кінець трьох фіксованих
    x_end = x

    # підпис «фіксоване» під трьома першими
    f.append(text((fixed_x0 + fixed_x1) / 2, by + bh + 22, "фіксоване", size=11, color=FIELD, bold=True))
    # підпис «змінне» під блокуванням
    f.append(text((fixed_x1 + x_end) / 2, by + bh + 22, "змінне", size=11, color=POS, bold=True))

    # дужка L над усім
    br_y = by - 14
    f.append(line(bx, br_y, x_end, br_y, color=MUTED, sw=1.4))
    f.append(line(bx, br_y, bx, br_y + 6, color=MUTED, sw=1.4))
    f.append(line(x_end, br_y, x_end, br_y + 6, color=MUTED, sw=1.4))
    f.append(text((bx + x_end) / 2, br_y - 6, "L (повна латентність)", size=10.5, color=INK, bold=True))

    f.append(text(W / 2, 290,
                  "перші три — фіксована «ціна входу»; блокування робить латентність змінною",
                  size=11, color=INK, bold=True))
    render(os.path.join(IMG, "latency-timeline.svg"), W, H, *f)


# ── 11. Джитер = найгірший − найкращий випадок ────────────────────────────────
def fig_jitter():
    W, H = 860, 320
    f = [text(W / 2, 30, "Джитер = найгірший − найкращий випадок", size=15, bold=True)]

    lab_x = 40
    bx = 200
    bh = 34
    y_best = 110
    y_worst = 180

    # найкращий — короткий зелений
    best_w = 70
    f.append(text(lab_x, y_best + 6, "найкращий", size=11, color=FIELD, anchor="start", bold=True))
    f.append(rect(bx, y_best - bh / 2, best_w, bh, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=5))
    f.append(text(bx + best_w + 12, y_best + 5,
                  "фіксоване ~35 тактів ≈ 0.15 мкс", size=10.5, color=INK, anchor="start"))

    # найгірший — фіксоване + блокування
    f.append(text(lab_x, y_worst + 6, "найгірший", size=11, color=POS, anchor="start", bold=True))
    f.append(rect(bx, y_worst - bh / 2, best_w, bh, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=5))
    block_w = 480
    f.append(rect(bx + best_w, y_worst - bh / 2, block_w, bh, fill="#fbecec", stroke=POS, sw=1.8, rx=0))
    f.append(text(bx + best_w + block_w / 2, y_worst + 5,
                  "фіксоване + блокування ≈ 3.1 мкс", size=10.5, color=POS, anchor="middle", bold=True))

    # дужка джитера між правими кінцями
    best_right = bx + best_w
    worst_right = bx + best_w + block_w
    jy = 230
    f.append(line(best_right, y_best + bh / 2, best_right, jy, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(worst_right, y_worst + bh / 2, worst_right, jy, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(best_right, jy, worst_right, jy, color=INK, sw=1.6))
    f.append(line(best_right, jy - 5, best_right, jy + 5, color=INK, sw=1.6))
    f.append(line(worst_right, jy - 5, worst_right, jy + 5, color=INK, sw=1.6))
    f.append(text((best_right + worst_right) / 2, jy - 8, "джитер ≈ 2.9 мкс", size=11, color=INK, bold=True))

    f.append(text(W / 2, 300,
                  "коротші критичні секції й ISR тиснуть джитер", size=11, color=INK, bold=True))
    render(os.path.join(IMG, "jitter.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_priority()
    fig_preemption()
    fig_nesting_stack()
    fig_same_level()
    fig_esp32_levels()
    fig_stack_danger()
    fig_apollo_overload()
    fig_apollo_priority_shed()
    fig_apollo_ground_call()
    fig_latency_timeline()
    fig_jitter()
    print("OK: 11 figures ->", IMG)
