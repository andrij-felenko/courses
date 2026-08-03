# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE  = NEG
RED   = POS
GREEN = FIELD
AMBER = "#b8860b"
GREY  = "#8a8a8a"
GRID  = "#dfe3e8"


def tb(cx, cy, s, **kw):
    """textbox, але повертає лише SVG-фрагмент (відкидає w,h)."""
    return textbox(cx, cy, s, **kw)[0]


def clk_tri(x, y, size=9, color=INK):
    """Маленький трикутник-«пелюстка» позначки тактового входу."""
    return ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" '
            'stroke="%s" stroke-width="1.4"/>' % (x, y - size, x + size, y, x, y + size, color))


# ── 1. Дві схеми тригера: куди заходить reset ────────────────────────────────
def fig_two_flops():
    W, H = 880, 360
    p = []
    p.append(text(W / 2, 28, "Куди приходить сигнал скидання", size=16, bold=True))

    def flop(x0, title, sub, mode):
        q = []
        bx, by, bw, bh = x0, 120, 150, 130
        q.append(rect(bx, by, bw, bh, fill="#f7f9fb", stroke=INK, sw=1.8))
        q.append(text(bx + bw / 2, by - 34, title, size=14, bold=True, color=BLUE))
        q.append(text(bx + bw / 2, by - 16, sub, size=10.5, color=MUTED))
        # позначки тригера
        q.append(text(bx + 14, by + 34, "D", size=13, anchor="start", bold=True))
        q.append(text(bx + bw - 14, by + 34, "Q", size=13, anchor="end", bold=True))
        q.append(clk_tri(bx + 8, by + bh - 30))
        q.append(text(bx + 22, by + bh - 26, "CLK", size=11, anchor="start", color=INK))
        # вхід D, такт, вихід Q
        q.append(arrow(bx - 60, by + 30, bx, by + 30, color=INK))
        q.append(text(bx - 62, by + 24, "D", size=12, anchor="end", color=INK, bold=True))
        q.append(line(bx - 60, by + bh - 30, bx, by + bh - 30, color=INK, sw=1.6))
        q.append(text(bx - 62, by + bh - 34, "CLK", size=11, anchor="end", color=INK))
        q.append(arrow(bx + bw, by + 30, bx + bw + 60, by + 30, color=INK))
        q.append(text(bx + bw + 62, by + 24, "Q", size=12, anchor="start", color=INK, bold=True))

        if mode == "sync":
            # reset зливається в логіку перед D, керується тактом
            gx, gy = bx - 120, by + 30
            q.append(rect(gx, gy - 18, 52, 52, fill="#eef2ff", stroke=BLUE, sw=1.6))
            q.append(text(gx + 26, gy + 4, "&", size=18, bold=True, color=BLUE))
            q.append(text(gx + 26, gy + 24, "логіка", size=9, color=MUTED))
            q.append(arrow(gx + 52, gy, bx - 60, gy, color=INK))
            q.append(arrow(gx - 44, gy - 8, gx, gy - 8, color=BLUE))
            q.append(text(gx - 46, gy - 12, "rst", size=11, anchor="end", color=BLUE, bold=True))
            q.append(arrow(gx - 44, gy + 14, gx, gy + 14, color=INK))
            q.append(text(gx - 46, gy + 18, "data", size=10, anchor="end", color=INK))
            q.append(text(bx + bw / 2, by + bh + 34,
                          "reset — у тих самих дверях, що й дані:", size=11, color=INK))
            q.append(text(bx + bw / 2, by + bh + 50,
                          "діє лише на фронті такту", size=11, color=BLUE, bold=True))
        else:
            # reset на окремий вхід CLR збоку тригера
            cx_ = bx + bw / 2
            q.append(arrow(cx_, by + bh + 56, cx_, by + bh, color=RED))
            q.append(text(cx_, by + bh + 72, "CLR", size=12, color=RED, bold=True))
            q.append(text(cx_, by + bh + 88, "(окремий вхід)", size=10, color=MUTED))
            q.append(text(bx + bw / 2, by - 52,
                          "reset — власні двері тригера:", size=11, color=INK, anchor="middle"))
            q.append(text(bx + bw / 2, by - 68,
                          "діє вмить, без такту", size=11, color=RED, bold=True, anchor="middle"))
        return q

    p += flop(190, "Синхронний reset", "усередині D-логіки", "sync")
    p += flop(560, "Асинхронний reset", "окремий вхід CLR", "async")
    # роздільна вертикаль
    p.append(line(W / 2, 70, W / 2, H - 20, color=GRID, sw=1.4, dash="4 5"))
    return render(os.path.join(OUT, "two-flops.svg"), W, H, *p)


# ── 2. Часова діаграма: хто впіймає короткий імпульс reset ───────────────────
def fig_timing():
    W, H = 880, 360
    p = []
    p.append(text(W / 2, 26, "Той самий короткий reset: хто його впіймає", size=16, bold=True))

    x0, x1 = 120, 820
    # такт: 7 періодів
    def wave(y, segs, color=INK, label=""):
        q = [text(110, y + 4, label, size=12, anchor="end", bold=True, color=color)]
        px, hi = x0, segs[0][1]
        path = ["M %.1f %.1f" % (x0, y - (16 if hi else 0))]
        for (xend, lvl) in segs:
            # горизонталь до xend на поточному рівні, тоді стрибок
            path.append("L %.1f %.1f" % (xend, y - (16 if hi else 0)))
            if lvl != hi:
                path.append("L %.1f %.1f" % (xend, y - (16 if lvl else 0)))
            hi = lvl
        q.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(path), color))
        return q

    # сітка тактових фронтів
    period = 100
    edges = [x0 + period * i for i in range(8)]
    for ex in edges:
        p.append(line(ex, 60, ex, 300, color=GRID, sw=1.2, dash="3 5"))

    # CLK — меандр
    clk = []
    lvl = False
    for i in range(7):
        clk.append((x0 + period * i + period / 2, True))
        clk.append((x0 + period * (i + 1), False))
    p += wave(110, clk, color=INK, label="CLK")
    # позначити активні фронти (наростання) стрілочками
    for i in range(7):
        ex = x0 + period * i
        p.append('<path d="M%.1f %.1f l4 6 l-8 0 z" fill="%s"/>' % (ex, 96, INK))

    # RST — короткий імпульс МІЖ фронтами (не накриває жодного наростання)
    glitch_a, glitch_b = x0 + period * 2 + 18, x0 + period * 2 + 70
    rst = [(glitch_a, False), (glitch_a, True), (glitch_b, True), (glitch_b, False), (x1, False)]
    # будуємо вручну як прямокутник
    p.append(text(110, 174, "RST", size=12, anchor="end", bold=True, color=RED))
    p.append(line(x0, 174, glitch_a, 174, color=RED, sw=2))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f" fill="none" stroke="%s" stroke-width="2"/>'
             % (glitch_a, 174, glitch_a, 158, glitch_b, 158, glitch_b, 174, RED))
    p.append(line(glitch_b, 174, x1, 174, color=RED, sw=2))
    p.append(text((glitch_a + glitch_b) / 2, 150, "вузький імпульс", size=9.5, color=RED))

    # Q_sync — не зреагував (між фронтами reset зник)
    p.append(text(110, 238, "Q синхр.", size=12, anchor="end", bold=True, color=BLUE))
    p.append(line(x0, 238, x1, 238, color=BLUE, sw=2))
    p.append(text((glitch_a + glitch_b) / 2 + 30, 230, "проспав: фронту не було", size=10, color=BLUE))

    # Q_async — миттєво в 0 і назад
    p.append(text(110, 296, "Q асинхр.", size=12, anchor="end", bold=True, color=GREEN))
    p.append(line(x0, 280, glitch_a, 280, color=GREEN, sw=2))  # був у 1
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f" fill="none" stroke="%s" stroke-width="2"/>'
             % (glitch_a, 280, glitch_a, 296, glitch_b, 296, glitch_b, 280, GREEN))
    p.append(line(glitch_b, 280, x1, 280, color=GREEN, sw=2))
    p.append(text((glitch_a + glitch_b) / 2 + 30, 314, "зреагував миттєво", size=10, color=GREEN))

    return render(os.path.join(OUT, "timing.svg"), W, H, *p)


# ── 3. Вікно recovery/removal навколо фронту ─────────────────────────────────
def fig_recovery_removal():
    W, H = 820, 340
    p = []
    p.append(text(W / 2, 26, "Небезпечне вікно навколо тактового фронту", size=16, bold=True))

    edge = 410
    y = 150
    # такт
    p.append(text(80, y + 4, "CLK", size=12, anchor="end", bold=True))
    p.append(line(150, y, edge, y, color=INK, sw=2))
    p.append(line(edge, y, edge, y - 26, color=INK, sw=2))
    p.append(line(edge, y - 26, 720, y - 26, color=INK, sw=2))
    p.append('<path d="M%.1f %.1f l5 8 l-10 0 z" fill="%s"/>' % (edge, y + 12, INK))
    p.append(text(edge, y + 30, "активний фронт", size=11, color=INK))

    # заборонена зона
    rec = edge - 90   # recovery до фронту
    rem = edge + 70   # removal після фронту
    p.append('<rect x="%.1f" y="60" width="%.1f" height="160" fill="#fdecea" '
             'stroke="%s" stroke-width="1.4" rx="6"/>' % (rec, rem - rec, RED))
    p.append(line(rec, 60, rec, 220, color=RED, sw=1.4, dash="4 4"))
    p.append(line(rem, 60, rem, 220, color=RED, sw=1.4, dash="4 4"))
    p.append(text((rec + rem) / 2, 78, "не відпускати reset тут", size=11, color=RED, bold=True))

    # стрілки-розміри recovery / removal
    p.append(arrow(rec, 250, edge, 250, color=RED))
    p.append(arrow(edge, 250, rec, 250, color=RED))
    p.append(tb((rec + edge) / 2, 250, "recovery", size=11, fill="#fff", stroke=RED, color=RED, pad=5))
    p.append(arrow(edge, 286, rem, 286, color=RED))
    p.append(arrow(rem, 286, edge, 286, color=RED))
    p.append(tb((edge + rem) / 2, 286, "removal", size=11, fill="#fff", stroke=RED, color=RED, pad=5))

    # підписи-аналогії
    p.append(text((rec + edge) / 2, 234, "як setup", size=10, color=MUTED))
    p.append(text((edge + rem) / 2, 270, "як hold", size=10, color=MUTED))

    # зняття reset усередині зони → знак біди
    p.append(arrow(edge - 10, 118, edge - 10, 150, color=AMBER))
    p.append(circle(edge - 10, 104, 11, fill="#fff8e1", stroke=AMBER, sw=2))
    p.append(text(edge - 10, 109, "!", size=15, color=AMBER, bold=True))
    p.append(text(edge - 10, 92, "відпустив тут →", size=10, color=AMBER))
    p.append(text(610, 150, "→ тригер може зависнути", size=11, color=AMBER, anchor="start", bold=True))
    p.append(text(610, 168, "у невизначеному стані", size=11, color=AMBER, anchor="start"))

    return render(os.path.join(OUT, "recovery-removal.svg"), W, H, *p)


# ── 4. Синхронізатор скидання: async assert, sync de-assert ──────────────────
def fig_reset_sync():
    W, H = 880, 330
    p = []
    p.append(text(W / 2, 26, "Синхронізатор: вмикаємо вмить, відпускаємо в такт", size=16, bold=True))

    # два тригери ланцюжка; CLR-вивід виводимо ЛІВОРУЧ від боксу (не знизу),
    # щоб червоне розведення reset не перетинало тіло тригера
    def ff(x, label):
        q = [rect(x, 120, 110, 110, fill="#f7f9fb", stroke=INK, sw=1.8)]
        q.append(text(x + 55, 110, label, size=12, color=MUTED))
        q.append(text(x + 14, 150, "D", size=12, anchor="start", bold=True))
        q.append(text(x + 96, 150, "Q", size=12, anchor="end", bold=True))
        q.append(clk_tri(x + 8, 200))
        q.append(text(x + 22, 204, "CLK", size=10, anchor="start"))
        q.append(text(x + 40, 224, "CLR", size=10, color=RED, bold=True, anchor="start"))
        return q

    p += ff(330, "FF1")
    p += ff(560, "FF2")

    # D першого тригера прив'язаний до лог.1
    p.append(line(250, 150, 330, 150, color=INK, sw=1.6))
    p.append(text(238, 154, "1", size=13, anchor="end", bold=True, color=INK))
    p.append(circle(244, 150, 3, fill=INK, stroke=INK))
    p.append(text(252, 138, "лог. «1»", size=10, color=MUTED, anchor="start"))

    # Q1 -> D2
    p.append(arrow(440, 150, 560, 150, color=INK))

    # CLK спільний — заходить у CLK-вивід кожного тригера знизу
    p.append(text(296, 304, "CLK", size=12, anchor="end", bold=True))
    p.append(line(300, 300, 338, 300, color=INK, sw=1.6))
    p.append(line(338, 300, 338, 208, color=INK, sw=1.6))
    p.append(line(300, 300, 568, 300, color=INK, sw=1.6))
    p.append(line(568, 300, 568, 208, color=INK, sw=1.6))
    p.append(circle(338, 300, 3, fill=INK, stroke=INK))

    # асинхронний rst_in -> обидва CLR (горизонтальна шина зверху, спуск ЛІВОРУЧ боксів)
    p.append(text(296, 78, "rst_in", size=12, anchor="end", bold=True, color=RED))
    p.append(line(300, 74, 600, 74, color=RED, sw=1.8))           # верхня шина
    # відвід на FF1: вниз ліворуч боксу і в CLR-вивід (x=330) на рівні y=224
    p.append(line(318, 74, 318, 224, color=RED, sw=1.8))
    p.append(arrow(318, 224, 330, 224, color=RED))
    p.append(circle(318, 74, 3, fill=RED, stroke=RED))
    # відвід на FF2
    p.append(line(548, 74, 548, 224, color=RED, sw=1.8))
    p.append(arrow(548, 224, 560, 224, color=RED))
    p.append(circle(548, 74, 3, fill=RED, stroke=RED))
    p.append(text(360, 66, "(асинхронно на обидва CLR)", size=9.5, color=RED, anchor="start"))

    # вихід rst_out
    p.append(arrow(670, 150, 770, 150, color=GREEN))
    p.append(text(772, 146, "rst_out", size=12, anchor="start", bold=True, color=GREEN))
    p.append(text(772, 164, "у решту схеми", size=10, anchor="start", color=MUTED))

    # пояснення
    p.append(text(W / 2, 318, "rst_in=1 → CLR миттєво гасить обидва (assert без такту);  "
                  "rst_in=0 → «1» доповзає за 2 такти (de-assert у фронт)",
                  size=10.5, color=INK))
    return render(os.path.join(OUT, "reset-sync.svg"), W, H, *p)


# ── 5. Автомат скидання: чотири стани контрольованого старту ──────────────────
def fig_reset_fsm():
    W, H = 880, 360
    p = []
    p.append(text(W / 2, 28, "Автомат скидання: вузол виходить у роботу поетапно", size=16, bold=True))

    y = 180
    # чотири стани в ряд
    states = [
        (130, "RESET", "усе вимкнено,\nвиходи в 0", RED),
        (350, "WAIT_PLL", "чекаємо\nстабільний такт", AMBER),
        (560, "SOFT", "виходи ще тримаємо,\nдомени будимо", BLUE),
        (770, "RUN", "вузол працює", GREEN),
    ]
    cx_list = []
    for (cx, name, sub, col) in states:
        p.append(circle(cx, y, 46, fill="#f7f9fb", stroke=col, sw=2.4))
        p.append(text(cx, y - 4, name, size=12.5, bold=True, color=col))
        for i, ln in enumerate(sub.split("\n")):
            p.append(text(cx, y + 14 + i * 13, ln, size=9, color=MUTED))
        cx_list.append(cx)

    # переходи (стрілки) + умови над ними
    conds = [
        (cx_list[0], cx_list[1], "rst знято"),
        (cx_list[1], cx_list[2], "pll_locked"),
        (cx_list[2], cx_list[3], "лічильник=0"),
    ]
    for (a, b, lab) in conds:
        p.append(arrow(a + 48, y - 8, b - 48, y - 8, color=INK))
        p.append(text((a + b) / 2, y - 22, lab, size=10, color=INK, bold=True))

    # будь-яка аварія → назад у RESET (велика дуга під станами)
    p.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="1.8" stroke-dasharray="5 4" marker-end="url(#arrow)"/>'
             % (cx_list[3], y + 46, (cx_list[0] + cx_list[3]) / 2, y + 150,
                cx_list[0], y + 46, RED))
    p.append(text((cx_list[0] + cx_list[3]) / 2, y + 132,
                  "аварія (BOR / WDT / rst) → знову в RESET, асинхронно й умить",
                  size=11, color=RED, bold=True))

    # вхідна стрілка «живлення»
    p.append(arrow(40, y, cx_list[0] - 48, y, color=INK))
    p.append(text(40, y - 10, "живлення", size=10, color=MUTED, anchor="start"))

    return render(os.path.join(OUT, "reset-fsm.svg"), W, H, *p)


# ── 6. Розведення скидання: дерево по доменах, синхронізатор на кожен ─────────
def fig_reset_tree():
    W, H = 880, 430
    p = []
    p.append(text(W / 2, 28, "Розведення скидання: окремий синхронізатор на кожен домен", size=16, bold=True))

    # спільне джерело асинхронного скидання зверху
    src_x = W / 2
    p.append(rect(src_x - 95, 52, 190, 40, fill="#fdecea", stroke=RED, sw=1.8))
    p.append(text(src_x, 70, "rst_async  (POR / BOR / кнопка)", size=11, color=RED, bold=True))
    p.append(text(src_x, 86, "асинхронна подія — спільна на весь чип", size=9, color=MUTED))

    # три домени, у кожного — свій такт, свій синхронізатор, своє дерево
    domains = [
        (170, "CLK_A  100 МГц", "ядро", BLUE),
        (440, "CLK_B  25 МГц", "Ethernet", FIELD),
        (710, "CLK_C  12 МГц", "USB", AMBER),
    ]
    for (cx, clk, who, col) in domains:
        # лінія від спільного джерела вниз до синхронізатора (assert — спільний)
        p.append(line(src_x, 92, src_x, 112, color=RED, sw=1.8))
        p.append(line(src_x, 112, cx, 112, color=RED, sw=1.8))
        p.append(line(cx, 112, cx, 140, color=RED, sw=1.8))
        p.append(circle(cx if cx != src_x else cx, 112, 0.1, fill=RED, stroke=RED))

        # бокс синхронізатора домену
        p.append(rect(cx - 70, 140, 140, 56, fill="#eef2ff", stroke=col, sw=1.8))
        p.append(text(cx, 160, "reset sync", size=11, bold=True, color=col))
        p.append(text(cx, 176, clk, size=9.5, color=INK))
        p.append(text(cx, 189, "(2 тригери на ЦЕЙ такт)", size=9, color=MUTED))

        # дерево виходу: один rst_out домену гілкується до багатьох тригерів
        ty = 210
        p.append(arrow(cx, 196, cx, ty + 6, color=col))
        p.append(line(cx - 60, ty + 6, cx + 60, ty + 6, color=col, sw=1.8))
        leaves = [cx - 60, cx - 30, cx, cx + 30, cx + 60]
        for lx in leaves:
            p.append(line(lx, ty + 6, lx, ty + 28, color=col, sw=1.4))
            p.append(rect(lx - 11, ty + 28, 22, 26, fill="#f7f9fb", stroke=col, sw=1.4, rx=3))
            p.append(text(lx, ty + 45, "FF", size=9, color=col))
        p.append(text(cx, ty + 78, "тригери домену «%s»" % who, size=10, color=col, bold=True))
        p.append(text(cx, ty + 93, "(зняття синхронне з %s)" % clk.split()[0], size=9, color=MUTED))

    # підпис-висновок унизу
    p.append(line(60, 360, W - 60, 360, color=GRID, sw=1.2))
    p.append(text(W / 2, 384, "ASSERT — спільний і асинхронний на всі домени (червоне).  "
                  "DE-ASSERT — окремий і синхронний у КОЖНОМУ домені (кольорове).",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, 404, "Один синхронізатор на весь чип не годиться: «синхронно» — це синхронно з конкретним тактом.",
                  size=10, color=MUTED))
    return render(os.path.join(OUT, "reset-tree.svg"), W, H, *p)


# ── 7. [hist] Два табори: чому ASIC і FPGA розійшлися ─────────────────────────
def fig_hist_two_camps():
    W, H = 880, 430
    p = []
    p.append(text(W / 2, 28, "Два табори, дві дефолтні відповіді — і чому", size=16, bold=True))

    # ліва колонка — ASIC, права — FPGA
    def camp(x0, title, sub, col, rows, verdict):
        q = [rect(x0, 70, 360, 250, fill="#f7f9fb", stroke=col, sw=2.0)]
        q.append(text(x0 + 180, 96, title, size=15, bold=True, color=col))
        q.append(text(x0 + 180, 114, sub, size=10.5, color=MUTED))
        q.append(line(x0 + 20, 126, x0 + 340, 126, color=GRID, sw=1.2))
        for i, (head, body) in enumerate(rows):
            yy = 150 + i * 52
            q.append(text(x0 + 24, yy, head, size=11.5, bold=True, color=INK, anchor="start"))
            q.append(text(x0 + 24, yy + 16, body, size=10, color=MUTED, anchor="start"))
        # вердикт
        q.append(rect(x0 + 20, 286, 320, 26, fill="#fff", stroke=col, sw=1.6, rx=6))
        q.append(text(x0 + 180, 303, verdict, size=11.5, bold=True, color=col))
        return q

    p += camp(40, "ASIC-табір", "власний кремній, своя бібліотека комірок", RED, [
        ("Тригер з CLR — майже безплатний",
         "у комірці й так є асинхронний вхід"),
        ("Працює без такту",
         "годиться для скидання при ввімкненні"),
        ("Скидання потрібне для тесту на фабриці",
         "scan-ланцюг треба вміти обнулити"),
    ], "ЗА замовчуванням: асинхронний")

    p += camp(480, "FPGA-табір", "чужа готова матриця тригерів", BLUE, [
        ("Асинхронний вхід — дефіцитний ресурс",
         "часто веде до зайвих LUT і гіршого розведення"),
        ("Синхронний reset зливається в логіку",
         "синтез вкладає його у наявні таблиці"),
        ("Таймінг замикається легше",
         "лишається звичайний шлях даних"),
    ], "ЗА замовчуванням: синхронний")

    # стрілка-«камінь спотикання» між таборами
    p.append(text(W / 2, 230, "?", size=40, bold=True, color=AMBER))
    p.append(text(W / 2, 360,
                  "Одне залізо штовхало в асинхронний бік, інше — у синхронний.",
                  size=12, color=INK))
    p.append(text(W / 2, 382,
                  "Сперечалися не про теорію, а про те, що дешевше на ТВОЇЙ підкладці.",
                  size=11, color=MUTED))
    p.append(text(W / 2, 410,
                  "Розв'язок (asynchronous assert, synchronous de-assert) помирив обидва аж згодом.",
                  size=11, color=FIELD, bold=True))
    return render(os.path.join(OUT, "hist-two-camps.svg"), W, H, *p)


# ── 8. [hist] Часова смуга суперечки про скидання ────────────────────────────
def fig_hist_timeline():
    W, H = 900, 320
    p = []
    p.append(text(W / 2, 28, "Дорога до спільної відповіді про скидання", size=16, bold=True))

    x0, x1 = 70, 830
    y = 150
    p.append(line(x0, y, x1, y, color=GREY, sw=2.2))
    p.append('<path d="M%.1f %.1f l-10 6 l0 -12 z" fill="%s"/>' % (x1, y, GREY))

    # віхи: (час, заголовок, підпис, колір, напрямок angle: +1 знизу / -1 зверху)
    miles = [
        (0.02, "1960–70-ті", "Епоха стандартних комірок:\nасинхронний CLR — норма ASIC", RED, -1),
        (0.30, "1980-ті", "FPGA виходять у світ:\nасинхронний вхід — дефіцит у матриці", BLUE, +1),
        (0.55, "1990-ті", "DFT/scan дозріває:\nавтомат тесту вимагає керованого reset", AMBER, -1),
        (0.78, "2002, SNUG SJ", "Каммінгс і Міллз:\n«I am so confused!» — кристалізують консенсус", FIELD, +1),
        (0.96, "2003 →", "«Part Deux» (з Ґолсоном)\nі дефолти інструментів синтезу", INK, -1),
    ]
    for (t, head, body, col, d) in miles:
        x = x0 + (x1 - x0) * t
        p.append(circle(x, y, 7, fill="#fff", stroke=col, sw=2.6))
        if d < 0:
            ty = y - 30
            p.append(line(x, y - 8, x, ty + 4, color=col, sw=1.4))
            p.append(text(x, ty - 26, head, size=12, bold=True, color=col))
            for i, ln in enumerate(body.split("\n")):
                p.append(text(x, ty - 10 + i * 13, ln, size=9.5, color=MUTED))
        else:
            ty = y + 30
            p.append(line(x, y + 8, x, ty - 4, color=col, sw=1.4))
            p.append(text(x, ty + 12, head, size=12, bold=True, color=col))
            for i, ln in enumerate(body.split("\n")):
                p.append(text(x, ty + 28 + i * 13, ln, size=9.5, color=MUTED))
    return render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_two_flops()
    fig_timing()
    fig_recovery_removal()
    fig_reset_sync()
    fig_reset_fsm()
    fig_reset_tree()
    fig_hist_two_camps()
    fig_hist_timeline()
    print("OK: figures written to", OUT)
