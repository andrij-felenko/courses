# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PURPLE = "#7a4fb0"


def codebox(x, y, w, title, lines, accent=INK, fill="#fbfcff"):
    """Картка-«програма»: заголовок угорі, лінія-роздільник, моноширинні рядки коду."""
    h = 40 + len(lines) * 20 + 14
    out = [rect(x, y, w, h, fill=fill, stroke=accent, sw=1.8, rx=10)]
    out.append(text(x + w / 2, y + 22, title, size=12, color=accent, bold=True))
    out.append(line(x + 14, y + 32, x + w - 14, y + 32, color="#e4e4e4", sw=1.2))
    cy = y + 52
    for ln in lines:
        out.append(text(x + 16, cy, ln, size=11, color=INK, anchor="start"))
        cy += 20
    return "".join(out), h


# ── 1. task-is-program: три задачі = три прості лінійні програми ───────────────
def fig_task_is_program():
    W, H = 760, 280
    p = []
    cols = [
        (40,  "Задача: блимати", PURPLE if False else FIELD,
         ["for (;;) {", "  увімкнути LED", "  чекай 500 мс", "  вимкнути LED", "  чекай 500 мс", "}"]),
        (290, "Задача: давач", NEG,
         ["for (;;) {", "  прочитати давач", "  обробити", "  чекай 1 с", "}"]),
        (540, "Задача: зв'язок", PURPLE,
         ["for (;;) {", "  чекай запит", "  відповісти", "}"]),
    ]
    for x, title, accent, lines in cols:
        frag, h = codebox(x, 70, 200, title, lines, accent=accent)
        p.append(frag)
    p.append(fitbox(120, 232, 520, 34,
                    "три прості лінійні програми замість одного клубка станів",
                    size=11, fill="#eef6ef", stroke=FIELD, sw=1.3, color=INK, bold=True))
    render(os.path.join(OUT, "task-is-program.svg"), W, H, *p,
           title="Задача — окрема маленька програма зі своїм циклом")


# ── 2. block-no-freeze: пауза однієї задачі віддає процесор іншій ──────────────
def fig_block_no_freeze():
    W, H = 720, 260
    p = []
    ox = 90
    track_w = 560
    yA, yB = 90, 170
    p.append(text(ox - 14, yA + 5, "A", size=14, color=NEG, anchor="end", bold=True))
    p.append(text(ox - 14, yB + 5, "B", size=14, color=FIELD, anchor="end", bold=True))

    # Смуга A: працює → ЧЕКАЄ (порожньо) → працює
    segA = [("працює", 0.0, 0.22, NEG, "#eef2fd"),
            ("чекає", 0.22, 0.70, MUTED, "#f4f6f8"),
            ("працює", 0.70, 1.0, NEG, "#eef2fd")]
    # Смуга B: працює саме тоді, коли A чекає
    segB = [("чекає", 0.0, 0.22, MUTED, "#f4f6f8"),
            ("працює", 0.22, 0.70, FIELD, "#eafaf0"),
            ("чекає", 0.70, 1.0, MUTED, "#f4f6f8")]
    bh = 40
    for y, segs in ((yA, segA), (yB, segB)):
        for lab, a, b, col, fill in segs:
            x = ox + a * track_w
            w = (b - a) * track_w
            dash = "5 4" if lab == "чекає" else None
            p.append(rect(x, y, w, bh, fill=fill, stroke=col, sw=1.5, rx=5))
            if dash:
                p.append(rect(x, y, w, bh, fill="none", stroke=col, sw=1.5, rx=5))
            p.append(text(x + w / 2, y + bh / 2 + 4, lab, size=11, color=col, bold=(lab == "працює")))

    # вертикальні «передачі процесора»
    for frac, lab in ((0.22, "A → B"), (0.70, "B → A")):
        x = ox + frac * track_w
        p.append(line(x, yA, x, yB + bh, color=POS, sw=1.6, dash="3 3"))
        p.append(text(x, yB + bh + 18, lab, size=10, color=POS, bold=True))

    p.append(text(W / 2, H - 14, "поки A чекає — працює B; процесор не простоює ані такту",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "block-no-freeze.svg"), W, H, *p,
           title="«Чекати» більше не морозить інших")


# ── 3. own-stack: у кожної задачі — власний стек із її станом ──────────────────
def fig_own_stack():
    W, H = 720, 300
    p = []
    titles = [("Задача A", NEG), ("Задача B", FIELD), ("Задача C", PURPLE)]
    layers = ["локальні\nзмінні", "ланцюг\nвикликів", "збережений\nконтекст\n(регістри, PC)"]
    bx0 = 70
    bw = 180
    gap = 35
    by = 70
    bh = 180
    for i, (title, accent) in enumerate(titles):
        x = bx0 + i * (bw + gap)
        p.append(rect(x, by, bw, bh, fill="#fbfcff", stroke=accent, sw=1.8, rx=10))
        p.append(text(x + bw / 2, by - 10, title, size=12, color=accent, bold=True))
        # три шари стека
        lh = (bh - 20) / 3
        fills = ["#f4f6f8", "#eef2f7", "#e7edf3"]
        for j, lab in enumerate(layers):
            ly = by + 10 + j * lh
            p.append(rect(x + 12, ly, bw - 24, lh - 8, fill=fills[j], stroke="#cfd6dd", sw=1.0, rx=4))
            p.append(mtext(x + bw / 2, ly + lh / 2 - 6, lab, size=10, color=INK, lh=1.15))
    p.append(text(W / 2, H - 16, "окремий стек = окреме «місце» задачі у своїй програмі, незалежне від інших",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "own-stack.svg"), W, H, *p,
           title="У кожної задачі — власний стек")


# ── 4. states: біжить ⇄ готова ⇄ заблокована ──────────────────────────────────
def fig_states():
    W, H = 720, 320
    p = []
    run = (200, 110)
    ready = (520, 110)
    block = (360, 250)
    r = 56
    nodes = [(run, "БІЖИТЬ", NEG, "#eef2fd"),
             (ready, "ГОТОВА", FIELD, "#eafaf0"),
             (block, "ЗАБЛОКОВАНА", POS, "#fdecea")]
    # стрілки спершу (щоб кола перекрили хвости)
    def edge(a, b, lab, col, off=0, labside=0):
        import math
        ax, ay = a; bx, by = b
        dx, dy = bx - ax, by - ay
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        # перпендикуляр для розведення двох зустрічних стрілок
        px, py = -uy, ux
        ax2 = ax + ux * r + px * off
        ay2 = ay + uy * r + py * off
        bx2 = bx - ux * r + px * off
        by2 = by - uy * r + py * off
        p.append(arrow(ax2, ay2, bx2, by2, color=col, sw=1.8))
        mx, my = (ax2 + bx2) / 2 + px * 14 * labside, (ay2 + by2) / 2 + py * 14 * labside
        p.append(text(mx, my, lab, size=10, color=col, bold=True))

    edge(ready, run, "черга", FIELD, off=14, labside=1)
    edge(run, ready, "витіснення", NEG, off=-14, labside=1)
    edge(run, block, "чекає", POS, off=10, labside=1)
    edge(block, ready, "подія настала", FIELD, off=10, labside=-1)

    for (cx, cy), lab, col, fill in nodes:
        p.append(circle(cx, cy, r, fill=fill, stroke=col, sw=2.2))
        p.append(text(cx, cy + 4, lab, size=11, color=col, bold=True))
    p.append(text(W / 2, H - 12, "на одному ядрі біжить лише одна; решта — готові або заблоковані",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "states.svg"), W, H, *p,
           title="Стани задачі")


# ── 5. xtaskcreate: функція-задача + виклик створення ──────────────────────────
def fig_xtaskcreate():
    W, H = 760, 300
    p = []
    # ліворуч — функція-задача
    frag, h = codebox(40, 70, 320, "функція-задача",
                      ["void task(void *p) {", "  setup();          // разово",
                       "  for (;;) {         // вічно", "    робота();",
                       "    vTaskDelay(...); // поступитись", "  }", "}"],
                      accent=NEG)
    p.append(frag)
    # праворуч — виклик і його аргументи
    args = [
        "task    // яку функцію",
        '"name"  // ім\'я (діагностика)',
        "2048    // розмір стека",
        "NULL    // параметр",
        "1       // пріоритет",
        "&handle // дескриптор",
    ]
    frag2, h2 = codebox(420, 70, 300, "xTaskCreate(...)", args, accent=FIELD, fill="#fbfff9")
    p.append(frag2)
    p.append(arrow(360, 70 + h / 2, 418, 70 + h2 / 2, color=POS, sw=2.0))
    p.append(text(390, 70 + h / 2 - 8, "створити", size=10, color=POS, bold=True))
    p.append(text(W / 2, H - 14, "створив одним рядком — і задача живе сама, поряд з іншими",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "xtaskcreate.svg"), W, H, *p,
           title="Створення задачі")


# ── 6. illusion: одне ядро швидко перемикається між задачами ───────────────────
def fig_illusion():
    W, H = 720, 280
    p = []
    ox = 70
    track_w = 580
    y = 120
    bh = 56
    # послідовні скибочки часу, що чергують три задачі
    order = [0, 1, 2, 0, 1, 0, 2, 1, 0, 2]
    cols = [NEG, FIELD, PURPLE]
    fills = ["#eef2fd", "#eafaf0", "#f2ecf8"]
    names = ["A", "B", "C"]
    n = len(order)
    sw = track_w / n
    for i, k in enumerate(order):
        x = ox + i * sw
        p.append(rect(x, y, sw - 2, bh, fill=fills[k], stroke=cols[k], sw=1.3, rx=3))
        p.append(text(x + sw / 2, y + bh / 2 + 4, names[k], size=12, color=cols[k], bold=True))
    p.append(arrow(ox, y + bh + 22, ox + track_w, y + bh + 22, color=INK, sw=1.6))
    p.append(text(ox + track_w, y + bh + 42, "час", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox, y - 16, "одне ядро — одна скибочка за раз", size=11, color=INK, anchor="start", bold=True))
    p.append(text(W / 2, H - 12, "перемикань десятки-сотні за секунду — і кожна задача наче біжить весь час",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "illusion.svg"), W, H, *p,
           title="Ілюзія багатьох програм на одному ядрі")


# ══════════ фігури вставки proj-fsm-instead ══════════════════════════════════

# ── A. state-diagram: коло станів контролера послідовності ─────────────────────
def fig_state_diagram():
    import math
    W, H = 720, 360
    p = []
    cx, cy, R = W / 2, 185, 115
    states = [
        ("Idle", "чекає кнопку", INK, "#f4f6f8"),
        ("Purge", "клапан LOW", NEG, "#eef2fd"),
        ("Running", "насос HIGH", FIELD, "#eafaf0"),
        ("Cooldown", "насос LOW", POS, "#fdecea"),
    ]
    trans = ["кнопка", "2 с", "кнопка", "3 с"]
    pts = []
    for i in range(4):
        ang = -math.pi / 2 + i * math.pi / 2     # зверху, далі за годинниковою
        sx = cx + R * math.cos(ang)
        sy = cy + R * math.sin(ang)
        pts.append((sx, sy))
    rr = 52
    # стрілки по колу
    for i in range(4):
        (ax, ay) = pts[i]
        (bx, by) = pts[(i + 1) % 4]
        dx, dy = bx - ax, by - ay
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        # вигин-перпендикуляр назовні
        ax2, ay2 = ax + ux * rr, ay + uy * rr
        bx2, by2 = bx - ux * rr, by - uy * rr
        p.append(arrow(ax2, ay2, bx2, by2, color=MUTED, sw=1.8))
        mx, my = (ax2 + bx2) / 2, (ay2 + by2) / 2
        # відсунути підпис назовні від центра
        ox2, oy2 = mx - cx, my - cy
        dd = math.hypot(ox2, oy2) or 1
        p.append(text(mx + ox2 / dd * 18, my + oy2 / dd * 18 + 4, trans[i],
                      size=11, color=POS, bold=True))
    for i, (name, act, col, fill) in enumerate(states):
        sx, sy = pts[i]
        p.append(circle(sx, sy, rr, fill=fill, stroke=col, sw=2.2))
        p.append(text(sx, sy - 4, name, size=13, color=col, bold=True))
        p.append(text(sx, sy + 14, act, size=9, color=MUTED))
    p.append(text(W / 2, H - 12, "одна послідовна справа — компактне коло, без спагеті з кількох справ",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "state-diagram.svg"), W, H, *p,
           title="Контролер послідовності: чотири стани, чотири переходи")


# ── B. fsm-vs-task: чого автомат не потребує проти задачі ──────────────────────
def fig_fsm_vs_task():
    W, H = 720, 320
    p = []
    # ліворуч — автомат у loop()
    p.append(rect(50, 70, 280, 200, fill="#eafaf0", stroke=FIELD, sw=2, rx=10))
    p.append(text(190, 96, "Автомат у loop()", size=13, color=FIELD, bold=True))
    has = ["state — одна змінна", "t0 — мітка часу (millis)", "switch у loop()", "неблокувальний"]
    for i, s in enumerate(has):
        p.append(text(70, 128 + i * 30, "• " + s, size=11, color=INK, anchor="start"))
    # праворуч — задача RTOS
    p.append(rect(390, 70, 280, 200, fill="#fdecea", stroke=POS, sw=2, rx=10))
    p.append(text(530, 96, "Задача RTOS", size=13, color=POS, bold=True))
    needs = ["власний стек (RAM)", "планувальник", "перемикання контексту", "черги, м'ютекси → гонки"]
    for i, s in enumerate(needs):
        p.append(text(410, 128 + i * 30, "• " + s, size=11, color=INK, anchor="start"))
    # критерій-стрілка під рамками
    p.append(text(W / 2, 296, "одна послідовна справа → ліворуч   ·   багато справ або блокувальні виклики → праворуч",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "fsm-vs-task.svg"), W, H, *p,
           title="Чого автомат не потребує — а задача потребує")


if __name__ == "__main__":
    fig_task_is_program()
    fig_block_no_freeze()
    fig_own_stack()
    fig_states()
    fig_xtaskcreate()
    fig_illusion()
    fig_state_diagram()
    fig_fsm_vs_task()
    print("OK: figures written to", OUT)
