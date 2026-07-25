# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── scheduler: розпорядник обирає з готових ──────────────────────────────────
# Ідея: серед ГОТОВИХ задач планувальник обирає одну й віддає їй процесор;
# заблоковані стоять осторонь і за час не змагаються.
def fig_scheduler():
    W, H = 700, 360
    p = []
    # готові задачі (черга ліворуч)
    ready = [("A", 70), ("B", 130), ("C", 190)]
    p.append(text(130, 60, "ГОТОВІ", size=14, bold=True, color=FIELD))
    for name, y in ready:
        b, _, _ = textbox(130, y + 30, "задача " + name, size=13, min_w=150,
                          fill="#eafaf1", stroke=FIELD)
        p.append(b)
    # планувальник у центрі
    box, bw, bh = textbox(390, 150, "ПЛАНУВАЛЬНИК\n(обирає одну)", size=14, bold=True,
                          min_w=170, fill=FILL, stroke=INK, sw=2)
    p.append(box)
    # стрілки від готових до планувальника
    for _, y in ready:
        p.append(arrow(205, y + 30, 305, 150, color=FIELD, sw=1.6))
    # процесор праворуч
    cpu, _, _ = textbox(610, 150, "ПРОЦЕСОР", size=14, bold=True, min_w=120,
                        fill="#fdecea", stroke=POS, sw=2)
    p.append(cpu)
    p.append(arrow(475, 150, 548, 150, color=INK, sw=2.2))
    p.append(text(512, 138, "біжить", size=11, color=INK))
    # заблоковані (унизу, осторонь)
    p.append(text(390, 270, "ЗАБЛОКОВАНІ — за час не змагаються", size=13, bold=True, color=MUTED))
    for i, name in enumerate(["D", "E"]):
        b, _, _ = textbox(330 + i * 120, 312, "задача " + name, size=12, min_w=100,
                          fill="#f0f1f3", stroke=MUTED)
        p.append(b)
    render(os.path.join(OUT, "scheduler.svg"), W, H, *p)


# ── triggers: три приводи перемикання ────────────────────────────────────────
# Ідея: планувальник прокидається з трьох причин — добровільне блокування,
# поява важливішої задачі, тік таймера. Перший — добровільний, два — примусові.
def fig_triggers():
    W, H = 700, 320
    p = []
    box, _, _ = textbox(350, 165, "ПЛАНУВАЛЬНИК", size=15, bold=True, min_w=190,
                        fill=FILL, stroke=INK, sw=2)
    rows = [
        (70,  FIELD, "1. задача сама блокується", "добровільний"),
        (165, POS,   "2. прокинулась важливіша",  "примусовий"),
        (260, POS,   "3. тік таймера",            "примусовий"),
    ]
    for y, col, label, kind in rows:
        b, bw, _ = textbox(150, y, label, size=12, min_w=210, fill=FILL, stroke=col)
        p.append(b)
        p.append(text(150, y + 28, kind, size=11, color=col, italic=True))
        p.append(arrow(150 + 105, y, 258, 165, color=col, sw=1.7))
    render(os.path.join(OUT, "triggers.svg"), W, H, *p)


# ── timeline-помічник: смуга задачі на осі часу ──────────────────────────────
def _band(x, y, w, label, col, fill, sw=1.5):
    return rect(x, y, w, 26, fill=fill, stroke=col, sw=sw, rx=4) + \
           text(x + w / 2, y + 17, label, size=12, color=INK)


# ── cooperative: кожен біжить, доки сам не поступиться ────────────────────────
# Ідея: вгорі — як задумано (передають чергу), внизу — біда (зажерлась і морозить).
def fig_cooperative():
    W, H = 700, 340
    p = []
    ox = 60
    # вісь часу
    p.append(arrow(ox, 300, W - 30, 300, color=INK, sw=1.6))
    p.append(text(W - 30, 320, "час", size=12, italic=True, color=INK))
    # верхній рядок — як задумано
    p.append(text(ox, 60, "Як задумано: кожна попрацювала й поступилася", size=13, bold=True, color=FIELD))
    segs = [("A", 120, FIELD), ("B", 110, NEG), ("C", 130, FIELD), ("A", 100, FIELD)]
    x = ox
    for name, w, col in segs:
        p.append(_band(x, 80, w, name, col, "#eafaf1" if col == FIELD else "#eaf0fd"))
        x += w
        if x < ox + 460:
            p.append(text(x - 4, 75, "↓", size=12, color=MUTED))
    # нижній рядок — біда
    p.append(text(ox, 175, "Біда: задача B зажерлася й не поступається — усі стоять", size=13, bold=True, color=POS))
    p.append(_band(ox, 195, 80, "A", FIELD, "#eafaf1"))
    p.append(rect(ox + 80, 195, W - 30 - (ox + 80), 26, fill="#fdecea", stroke=POS, sw=2, rx=4))
    p.append(text(ox + 80 + (W - 30 - (ox + 80)) / 2, 212, "B крутиться без кінця…", size=12, bold=True, color=POS))
    p.append(text(ox + 80, 245, "C, A, D — ніколи не дістануть процесора", size=12, color=MUTED))
    render(os.path.join(OUT, "cooperative.svg"), W, H, *p)


# ── preemptive: планувальник відбирає силою ──────────────────────────────────
# Ідея: щойно прокинулась A (висока), B негайно відсувають; A заснула — B назад.
def fig_preemptive():
    W, H = 700, 300
    p = []
    ox = 70
    p.append(arrow(ox, 250, W - 30, 250, color=INK, sw=1.6))
    p.append(text(W - 30, 270, "час", size=12, italic=True, color=INK))
    # дві доріжки пріоритетів
    p.append(text(ox - 8, 95, "A (висока)", size=12, bold=True, color=POS, anchor="end"))
    p.append(text(ox - 8, 175, "B (низька)", size=12, bold=True, color=NEG, anchor="end"))
    # B біжить, потім витіснена, потім знов
    p.append(_band(ox, 162, 120, "B біжить", NEG, "#eaf0fd"))
    # A прокидається й витісняє
    p.append(_band(ox + 120, 82, 160, "A витісняє — біжить", POS, "#fdecea", sw=2))
    p.append(arrow(ox + 120, 150, ox + 120, 100, color=POS, sw=2))
    p.append(text(ox + 122, 135, "прокинулась A → B геть", size=10, color=POS, anchor="start"))
    # A заснула, B повертається
    p.append(_band(ox + 280, 162, 160, "B знову біжить", NEG, "#eaf0fd"))
    p.append(arrow(ox + 280, 100, ox + 280, 150, color=NEG, sw=2))
    p.append(text(ox + 282, 135, "A заснула → B назад", size=10, color=NEG, anchor="start"))
    render(os.path.join(OUT, "preemptive.svg"), W, H, *p)


# ── tick: серцебиття планувальника ───────────────────────────────────────────
# Ідея: таймер рівно цокає; кожен тік через переривання будить планувальник.
def fig_tick():
    W, H = 700, 320
    p = []
    ox, oy = 60, 130
    aw = W - 90
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "час", size=12, italic=True, color=INK))
    # тіки — рівні риски
    n = 8
    dx = aw / (n + 1)
    for i in range(1, n + 1):
        x = ox + i * dx
        p.append(line(x, oy - 18, x, oy + 8, color=POS, sw=2))
        p.append(text(x, oy - 24, "тік", size=10, color=POS))
        p.append(arrow(x, oy + 8, x, oy + 50, color=POS, sw=1.4))
    # планувальник унизу
    box, _, _ = textbox(ox + aw / 2, oy + 90, "кожен тік → переривання будить ПЛАНУВАЛЬНИК\n«чи не час перемкнутися?»",
                        size=13, min_w=440, fill=FILL, stroke=INK)
    p.append(box)
    # формула періоду
    p.append(text(ox + aw / 2, oy + 150, "T_тік = 1 / 1000 Гц = 1 мс  (рівний інтервал)", size=12, color=MUTED))
    render(os.path.join(OUT, "tick.svg"), W, H, *p)


# ── freertos-rule: біжить найвищий готовий; рівні — round-robin ───────────────
# Ідея: поки давач (висока) готовий — біжить лише він; засне — лог і дисплей
# (рівні) діляться по черзі; прокинеться давач — миттю забере процесор.
def fig_freertos_rule():
    W, H = 700, 340
    p = []
    ox = 80
    p.append(arrow(ox, 290, W - 30, 290, color=INK, sw=1.6))
    p.append(text(W - 30, 310, "час", size=12, italic=True, color=INK))
    p.append(text(ox - 8, 95, "давач (висока)", size=12, bold=True, color=POS, anchor="end"))
    p.append(text(ox - 8, 200, "лог/дисплей (рівні)", size=11, bold=True, color=NEG, anchor="end"))
    # давач біжить
    p.append(_band(ox, 82, 130, "давач", POS, "#fdecea", sw=2))
    # давач заснув → round-robin рівних
    rr = [("лог", NEG), ("дисп", FIELD), ("лог", NEG), ("дисп", FIELD)]
    x = ox + 130
    for name, col in rr:
        p.append(_band(x, 187, 70, name, col, "#eaf0fd" if col == NEG else "#eafaf1"))
        x += 70
    p.append(text(ox + 130 + 140, 165, "round-robin: рівні по черзі", size=11, color=MUTED))
    # давач прокинувся → витіснив
    p.append(_band(x, 82, 110, "давач знову", POS, "#fdecea", sw=2))
    p.append(arrow(x, 150, x, 100, color=POS, sw=2))
    p.append(text(x + 4, 135, "миттю витісняє", size=10, color=POS, anchor="start"))
    render(os.path.join(OUT, "freertos-rule.svg"), W, H, *p)


# ── tick-quantize (math): чому vTaskDelay(1) ≠ рівно 1 мс ─────────────────────
# Ідея: виклик падає всередину тіку; пробудження — на НАЙБЛИЖЧІЙ межі (тік+1),
# тож пауза = недожитий залишок поточного тіку, завжди менша за повний тік.
def fig_tick_quantize():
    W, H = 700, 260
    p = []
    ox, oy = 60, 150
    aw = W - 120
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 22, "час", size=12, italic=True, color=INK))
    n = 4
    dx = aw / n
    for i in range(n + 1):
        x = ox + i * dx
        p.append(line(x, oy - 14, x, oy + 14, color=POS, sw=2))
        p.append(text(x, oy + 30, "тік %d" % i, size=10, color=POS))
    # момент виклику всередині тіку 0 (фаза 0.3)
    cx = ox + 0.3 * dx
    p.append(line(cx, oy - 66, cx, oy + 14, color=NEG, sw=2, dash="4 3"))
    p.append(text(cx, oy - 72, "виклик vTaskDelay(1)", size=11, color=NEG))
    # пауза = від виклику до НАЙБЛИЖЧОЇ межі (тік 1)
    wx = ox + dx
    p.append(arrow(cx, oy - 40, wx, oy - 40, color=FIELD, sw=2))
    p.append(text((cx + wx) / 2, oy - 46, "пауза < 1 тік", size=10, color=FIELD))
    # пробудження на межі тіку 1
    p.append(circle(wx, oy, 4, fill=FIELD, stroke=FIELD))
    p.append(text(wx + 8, oy - 22, "пробудження на найближчій межі", size=11, color=FIELD, anchor="start"))
    p.append(text(ox + aw / 2, H - 16, "реальна пауза від виклику ∈ (0, 1] мс  →  гарантовано ≥1 мс дає vTaskDelay(2)",
                  size=12, color=INK))
    render(os.path.join(OUT, "tick-quantize.svg"), W, H, *p)


# ── latency-budget (math): латентність = квантування + черга ─────────────────
def fig_latency_budget():
    W, H = 700, 280
    p = []
    ox, oy = 70, 120
    aw = W - 110
    # шкала латентності
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    # квант 0..Tтік
    qw = aw * 0.5
    p.append(rect(ox, oy - 28, qw, 28, fill="#eef4ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(ox + qw / 2, oy - 9, "квантування  0…T_тік", size=12, color=NEG))
    # черга
    p.append(rect(ox + qw, oy - 28, aw - qw, 28, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(ox + qw + (aw - qw) / 2, oy - 9, "черга готових ≥0", size=12, color=FIELD))
    # позначки середнього/найгіршого
    p.append(line(ox + qw * 0.5, oy, ox + qw * 0.5, oy + 18, color=INK, sw=1.4))
    p.append(text(ox + qw * 0.5, oy + 34, "середнє = 0.5 мс", size=11, color=INK))
    p.append(line(ox + qw, oy, ox + qw, oy + 18, color=POS, sw=1.6))
    p.append(text(ox + qw, oy + 34, "найгірше = 1 мс", size=11, color=POS))
    p.append(text(ox + aw / 2, oy - 52, "L_пробудж = L_квант + L_черга", size=14, bold=True, color=INK))
    p.append(text(ox + aw / 2, H - 22, "джитер пробудження = T_тік = 1 мс", size=12, color=MUTED))
    render(os.path.join(OUT, "latency-budget.svg"), W, H, *p)


# ── ready-bitmap (proj-clz): біт i=1 → є готова задача; CLZ ───────────────────
def fig_ready_bitmap():
    W, H = 700, 300
    p = []
    ox, oy = 50, 120
    cell = 36
    bits = [0] * 32
    bits[1] = 1
    bits[3] = 1  # приклад 0x0A
    # малюємо 12 молодших бітів (досить для ідеї), MSB ліворуч
    show = 12
    p.append(text(ox, oy - 30, "Бітова карта готовності (молодші 12 бітів, MSB ліворуч)", size=12, bold=True, color=INK))
    for i in range(show):
        idx = show - 1 - i  # позиція біта (зменшується ліворуч→праворуч)
        x = ox + i * cell
        on = bits[idx]
        p.append(rect(x, oy, cell - 4, cell, fill="#fdecea" if on else FILL,
                      stroke=POS if on else MUTED, sw=2 if on else 1.2, rx=4))
        p.append(text(x + (cell - 4) / 2, oy + 24, str(on), size=14, bold=on, color=POS if on else MUTED))
        p.append(text(x + (cell - 4) / 2, oy + cell + 16, str(idx), size=10, color=MUTED))
    p.append(text(ox + show * cell / 2, oy + cell + 34, "номер пріоритету", size=10, italic=True, color=MUTED))
    # CLZ-стрілка до найстаршої одиниці (біт 3)
    msb_i = show - 1 - 3
    mx = ox + msb_i * cell + (cell - 4) / 2
    p.append(arrow(mx, oy - 8, mx, oy - 2, color=FIELD, sw=2))
    p.append(text(mx, oy - 16, "найстарша 1", size=10, color=FIELD))
    p.append(text(ox + show * cell / 2, H - 28,
                  "clz(0x0A) = 28 старших нулів  →  найвищий = 31 − 28 = 3", size=13, bold=True, color=INK))
    render(os.path.join(OUT, "ready-bitmap.svg"), W, H, *p)


# ── scan-vs-clz (proj-clz): O(N) сканування проти O(1) CLZ ────────────────────
def fig_scan_vs_clz():
    W, H = 700, 320
    p = []
    # ліворуч — лінійне сканування
    p.append(text(175, 50, "Лінійне сканування  O(N)", size=13, bold=True, color=POS))
    for i in range(6):
        y = 80 + i * 34
        lvl = 5 - i
        b, _, _ = textbox(175, y, "рівень %d: порожній?" % lvl, size=11, min_w=220,
                          fill=FILL, stroke=MUTED)
        p.append(b)
        if i < 5:
            p.append(arrow(175, y + 13, 175, y + 21, color=MUTED, sw=1.4))
    p.append(text(175, 290, "цикл довшає з числом рівнів", size=11, italic=True, color=MUTED))
    # роздільник
    p.append(line(350, 60, 350, 290, color=MUTED, sw=1, dash="4 4"))
    # праворуч — CLZ
    p.append(text(525, 50, "Одна інструкція CLZ  O(1)", size=13, bold=True, color=FIELD))
    b, bw, bh = textbox(525, 150, "31 − __builtin_clz(bitmap)", size=14, bold=True,
                        min_w=240, fill="#eafaf1", stroke=FIELD, sw=2)
    p.append(b)
    p.append(text(525, 210, "сталий час, незалежно від", size=12, color=INK))
    p.append(text(525, 230, "кількості пріоритетів", size=12, color=INK))
    p.append(text(525, 268, "nsau (Xtensa) · clz (ARM)", size=11, italic=True, color=MUTED))
    render(os.path.join(OUT, "scan-vs-clz.svg"), W, H, *p)


# ── switch-steps (proj-context-switch): три кроки перемикання ─────────────────
def fig_switch_steps():
    W, H = 720, 300
    p = []
    steps = [
        (130, FIELD, "1. ПРИВІД", "тік або vTaskDelay\n→ керування планувальнику"),
        (360, POS,   "2. ЗБЕРЕГТИ", "регістри+PC задачі A\nна ЇЇ стек; SP → TCB"),
        (590, NEG,   "3. ВІДНОВИТИ", "SP задачі B з TCB;\nрегістри+PC зі стека B"),
    ]
    for x, col, head, body in steps:
        b, bw, bh = textbox(x, 140, body, size=12, min_w=190, fill=FILL, stroke=col, sw=2)
        p.append(b)
        p.append(text(x, 90, head, size=14, bold=True, color=col))
    p.append(arrow(225, 140, 265, 140, color=INK, sw=2))
    p.append(arrow(455, 140, 495, 140, color=INK, sw=2))
    p.append(text(W / 2, 235, "SP — єдина «ручка» до всього збереженого контексту", size=13, bold=True, color=INK))
    p.append(text(W / 2, 262, "задача B відновлюється точно туди, де її спинили", size=12, color=MUTED))
    render(os.path.join(OUT, "switch-steps.svg"), W, H, *p)


# ── stack-frame (proj-context-switch): що займає стек задачі ──────────────────
def fig_stack_frame():
    W, H = 560, 360
    p = []
    cx = 280
    w = 240
    x = cx - w / 2
    parts = [
        ("локальні змінні", FILL, MUTED, 46),
        ("ланцюг викликів", FILL, MUTED, 46),
        ("ЗБЕРЕЖЕНИЙ КАДР\nрегістрів + PC", "#fdecea", POS, 70),
        ("вільний запас", "#eafaf1", FIELD, 56),
    ]
    y = 50
    p.append(text(cx, 32, "Стек задачі", size=15, bold=True, color=INK))
    for label, fill, col, h in parts:
        p.append(rect(x, y, w, h, fill=fill, stroke=col, sw=2, rx=4))
        for j, ln in enumerate(label.split("\n")):
            p.append(text(cx, y + h / 2 + 5 + (j - (label.count("\n")) / 2) * 16, ln,
                          size=12, bold=(col == POS), color=col))
        y += h
    # межа стека
    p.append(line(x - 20, y, x + w + 20, y, color=POS, sw=2, dash="5 3"))
    p.append(text(cx, y + 18, "межа стека — нижче переповнення", size=12, color=POS))
    # водяний знак
    wm = 50 + 46 + 46 + 70 + 20
    p.append(line(x - 10, wm, x, wm, color=NEG, sw=2))
    p.append(text(x - 14, wm + 4, "водяний знак", size=10, color=NEG, anchor="end"))
    p.append(text(cx, H - 14, "більший кадр (FPU) присуває до межі швидше", size=11, italic=True, color=MUTED))
    render(os.path.join(OUT, "stack-frame.svg"), W, H, *p)


if __name__ == "__main__":
    fig_scheduler()
    fig_triggers()
    fig_cooperative()
    fig_preemptive()
    fig_tick()
    fig_freertos_rule()
    fig_tick_quantize()
    fig_latency_budget()
    fig_ready_bitmap()
    fig_scan_vs_clz()
    fig_switch_steps()
    fig_stack_frame()
    print("OK: 12 figures ->", OUT)
