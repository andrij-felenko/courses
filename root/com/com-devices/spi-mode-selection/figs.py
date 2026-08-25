# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори ролей (поверх палітри svgkit): такт — холодний, дані — нейтральні.
CLK = NEG          # такт SCK — синій
DAT = "#7a5fb0"    # лінія даних — фіолетовий, щоб не плутати з такт/вибіркою
CAP = FIELD        # фронт ВИБІРКИ (захоплення) — зелений
CHG = POS          # фронт ЗМІНИ даних — червоний


# ── Помічник: намалювати такт SCK як меандр ───────────────────────────────────
# cpol=0 → у спокої низько, перший фронт угору; cpol=1 → дзеркально.
# Повертає список фрагментів + список x-координат фронтів (по порядку в часі).
def clock(x0, ymid, amp, period, n, cpol, color=CLK, sw=2.4):
    hi, lo = ymid - amp, ymid + amp          # «високо» вище за центр (менший y)
    idle = lo if cpol == 0 else hi           # рівень спокою
    act = hi if cpol == 0 else lo            # рівень під час такту
    frags = []
    edges = []
    half = period / 2.0
    # коротка «полиця спокою» перед першим фронтом
    x = x0
    y = idle
    pts = [(x, y)]
    lead = half * 0.6
    x += lead
    pts.append((x, y))
    for i in range(n):                       # n тактів = 2n фронтів
        # фронт у активний рівень
        edges.append(x)
        y = act
        pts.append((x, y))
        x += half
        pts.append((x, y))
        # фронт назад у спокій
        edges.append(x)
        y = idle
        pts.append((x, y))
        x += half
        pts.append((x, y))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                 'stroke-linejoin="miter" stroke-linecap="round"/>' % (poly, color, sw))
    return frags, edges, x


# ── Помічник: лінія даних, що міняє рівень у заданих точках x ──────────────────
# changes — список x, де біт перемикається; level0 — стартовий рівень (0/1).
def dataline(x_start, x_end, ymid, amp, changes, level0, color=DAT, sw=2.4):
    hi, lo = ymid - amp, ymid + amp
    lvl = hi if level0 else lo
    pts = [(x_start, lvl)]
    cur = level0
    for cx in changes:
        pts.append((cx, lvl))                # доходимо до точки зміни
        cur = 1 - cur
        lvl = hi if cur else lo
        pts.append((cx, lvl))                # вертикальний перепад
    pts.append((x_end, lvl))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="miter" stroke-linecap="round"/>' % (poly, color, sw))


def tick_arrow(x, y_from, y_to, color, sw=1.6):
    return arrow(x, y_from, x, y_to, color=color, sw=sw)


# ── 1. CPOL: рівень спокою такту ──────────────────────────────────────────────
def fig_cpol():
    W, H = 700, 300
    p = []
    amp, period, n = 26, 56, 5
    x0 = 150
    # CPOL = 0
    yA = 96
    f, edges, xend = clock(x0, yA, amp, period, n, 0)
    p += f
    p.append(text(x0 - 16, yA + 4, "CPOL = 0", size=12, color=CLK, bold=True, anchor="end"))
    p.append(text(xend + 8, yA + amp + 2, "спокій низько", size=10, color=MUTED, anchor="start"))
    p.append(text(x0 + 2, yA + amp + 18, "перший фронт — наростання", size=10, color=FIELD, anchor="start"))
    # CPOL = 1
    yB = 210
    f, edges, xend = clock(x0, yB, amp, period, n, 1)
    p += f
    p.append(text(x0 - 16, yB + 4, "CPOL = 1", size=12, color=CLK, bold=True, anchor="end"))
    p.append(text(xend + 8, yB - amp - 6, "спокій високо", size=10, color=MUTED, anchor="start"))
    p.append(text(x0 + 2, yB + amp + 18, "перший фронт — спадання", size=10, color=POS, anchor="start"))

    p.append(text(W / 2, H - 14, "CPOL лише перевертає всю діаграму такту згори вниз",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "cpol.svg"), W, H, *p,
           title="CPOL — рівень такту SCK у спокої")


# ── 2. CPHA: на якому фронті вибірка ──────────────────────────────────────────
def fig_cpha():
    W, H = 700, 330
    p = []
    amp, period, n = 24, 60, 4
    x0 = 150
    # спільний CPOL=0 такт для обох; різниця лише у фронті вибірки
    # CPHA = 0 — вибірка на першому (наростання)
    yClkA = 88
    f, edgesA, xend = clock(x0, yClkA, amp, period, n, 0)
    p += f
    p.append(text(x0 - 16, yClkA + 4, "SCK", size=11, color=CLK, bold=True, anchor="end"))
    p.append(text(x0 - 16, yClkA + 20, "(CPHA=0)", size=9, color=MUTED, anchor="end"))
    # дані: міняються трохи раніше за наростання, стоять на захопленні
    yDatA = 150
    rises = edgesA[0::2]                       # наростання (для CPOL=0 — парні індекси)
    # зміни даних — перед кожним наростанням
    changes = [x0 + period * 0.3 + i * period for i in range(n)]
    p.append(dataline(x0, xend, yDatA, amp * 0.7, changes, 1, color=DAT))
    p.append(text(x0 - 16, yDatA + 4, "дані", size=11, color=DAT, bold=True, anchor="end"))
    for rx in rises:
        p.append(tick_arrow(rx, yDatA + amp * 0.7 + 18, yDatA + amp * 0.7 + 2, CAP))
    p.append(text((x0 + xend) / 2, yDatA + amp * 0.7 + 34,
                  "вибірка на ПЕРШОМУ фронті — дані вже стоять", size=10, color=CAP, bold=True))

    # CPHA = 1 — вибірка на другому
    yClkB = 232
    f, edgesB, xend = clock(x0, yClkB, amp, period, n, 0)
    p += f
    p.append(text(x0 - 16, yClkB + 4, "SCK", size=11, color=CLK, bold=True, anchor="end"))
    p.append(text(x0 - 16, yClkB + 20, "(CPHA=1)", size=9, color=MUTED, anchor="end"))
    yDatB = 294
    # зміни — на першому фронті (наростанні), вибірка — на другому (спаданні)
    falls = edgesB[1::2]
    changesB = edgesB[0::2]
    p.append(dataline(x0, xend, yDatB, amp * 0.55, changesB, 1, color=DAT))
    p.append(text(x0 - 16, yDatB + 4, "дані", size=11, color=DAT, bold=True, anchor="end"))
    for fx in falls:
        p.append(tick_arrow(fx, yDatB - amp * 0.55 - 16, yDatB - amp * 0.55 - 2, CAP))
    p.append(text((x0 + xend) / 2, yDatB - amp * 0.55 - 22,
                  "перший фронт виставляє біт, вибірка — на ДРУГОМУ", size=10, color=CAP, bold=True))

    render(os.path.join(OUT, "cpha.svg"), W, H, *p,
           title="CPHA — на якому фронті знімають біт")


# ── 3. Чотири режими = (CPOL, CPHA) ───────────────────────────────────────────
def fig_fourmodes():
    W, H = 700, 320
    p = []
    # таблиця 2×2: рядки CPHA, стовпці CPOL
    x0, y0 = 150, 80
    cw, ch = 230, 92
    gx, gy = 20, 18
    cells = [
        (0, 0, "Mode 0", "(0, 0)", "спокій низько\nвибірка по наростанню", True),
        (1, 0, "Mode 1", "(0, 1)", "спокій низько\nвибірка по спаданню", False),
        (0, 1, "Mode 2", "(1, 0)", "спокій високо\nвибірка по спаданню", False),
        (1, 1, "Mode 3", "(1, 1)", "спокій високо\nвибірка по наростанню", True),
    ]
    # підписи осей
    p.append(text(x0 + cw / 2, y0 - 16, "CPOL = 0", size=12, color=CLK, bold=True))
    p.append(text(x0 + cw + gx + cw / 2, y0 - 16, "CPOL = 1", size=12, color=CLK, bold=True))
    p.append(text(x0 - 24, y0 + ch / 2, "CPHA=0", size=11, color=MUTED, anchor="end"))
    p.append(text(x0 - 24, y0 + ch + gy + ch / 2, "CPHA=1", size=11, color=MUTED, anchor="end"))
    for col, row, name, pair, desc, common in cells:
        cx = x0 + col * (cw + gx)
        cy = y0 + row * (ch + gy)
        fill = "#eafaf0" if common else FILL
        stroke = FIELD if common else LINE
        p.append(rect(cx, cy, cw, ch, fill=fill, stroke=stroke, sw=2 if common else 1.4))
        p.append(text(cx + cw / 2, cy + 26, "%s  %s" % (name, pair), size=14, color=INK, bold=True))
        p.append(mtext(cx + cw / 2, cy + 50, desc, size=11, color=MUTED))
        if common:
            p.append(text(cx + cw / 2, cy + ch - 10, "★ найпоширеніший", size=9, color=FIELD, bold=True))
    p.append(text(W / 2, H - 14, "номер режиму — це просто пара (CPOL, CPHA); найчастіші — 0 і 3",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "fourmodes.svg"), W, H, *p,
           title="Чотири режими SPI = (CPOL, CPHA)")


# ── 4. Mode 0 докладно ────────────────────────────────────────────────────────
def fig_mode0():
    W, H = 700, 300
    p = []
    amp, period, n = 26, 70, 4
    x0 = 130
    yClk = 96
    f, edges, xend = clock(x0, yClk, amp, period, n, 0)
    p += f
    p.append(text(x0 - 14, yClk + 4, "SCK", size=11, color=CLK, bold=True, anchor="end"))
    rises = edges[0::2]
    falls = edges[1::2]
    yDat = 178
    # дані виставляють на попередньому спаді / при CS↓; біти: 1 0 1 1
    bits = [1, 0, 1, 1]
    changes = [x0 + period * 0.28]            # перший біт виставлено до першого фронту
    for i in range(1, n):
        changes.append(falls[i - 1])          # дальші — на спадах
    levels = []
    p.append(dataline(x0, xend, yDat, amp * 0.7, changes, bits[0], color=DAT))
    p.append(text(x0 - 14, yDat + 4, "MOSI", size=11, color=DAT, bold=True, anchor="end"))
    # стрілки вибірки на наростаннях
    for i, rx in enumerate(rises):
        p.append(tick_arrow(rx, yDat + amp * 0.7 + 20, yDat + amp * 0.7 + 2, CAP))
        p.append(text(rx, yDat + amp * 0.7 + 36, "біт %d" % (i + 1), size=9, color=CAP))
    # підписи механіки
    p.append(text(x0 + period * 0.5, yClk - amp - 10, "спад: ГОТУЄМО біт", size=10, color=CHG))
    p.append(text((x0 + xend) / 2, H - 40,
                  "наростання: ЗНІМАЄМО біт (фронт влучає в середину стабільного рівня)",
                  size=10, color=CAP, bold=True))
    p.append(text(W / 2, H - 14, "Mode 0: спокій низько, вибірка по наростанню — типовий за замовчуванням",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "mode0.svg"), W, H, *p,
           title="Mode 0 докладно: готуємо на спаді, знімаємо на наростанні")


# ── 5. Пастка: різні режими → сміття ──────────────────────────────────────────
def fig_mismatch():
    W, H = 700, 330
    p = []
    amp, period, n = 24, 72, 4
    x0 = 130
    yClk = 92
    f, edges, xend = clock(x0, yClk, amp, period, n, 0)
    p += f
    p.append(text(x0 - 14, yClk + 4, "SCK", size=11, color=CLK, bold=True, anchor="end"))
    rises = edges[0::2]
    falls = edges[1::2]
    # дані: ведучий виставляє для Mode 0 (на спаді), вони дійсні навколо наростання
    yDat = 174
    bits = [1, 0, 0, 1]
    changes = [x0 + period * 0.28] + [falls[i - 1] for i in range(1, n)]
    p.append(dataline(x0, xend, yDat, amp * 0.7, changes, bits[0], color=DAT))
    p.append(text(x0 - 14, yDat + 4, "MOSI", size=11, color=DAT, bold=True, anchor="end"))
    # ведучий (Mode 0): зелені стрілки на наростаннях — чіткі біти
    for rx in rises:
        p.append(tick_arrow(rx, yDat - amp * 0.7 - 16, yDat - amp * 0.7 - 2, CAP))
    p.append(text((x0 + xend) / 2, yDat - amp * 0.7 - 22,
                  "ведучий (Mode 0): знімай на наростанні — чіткі біти", size=10, color=CAP, bold=True))
    # ведений (Mode 1): червоні стрілки на спаданнях — потрапляють на перехід
    for i, fx in enumerate(falls):
        p.append(tick_arrow(fx, yDat + amp * 0.7 + 40, yDat + amp * 0.7 + 4, CHG))
    # позначимо переходи даних (вертикалі) пунктиром, щоб видно «небезпечну зону»
    for cx in changes[1:]:
        p.append(line(cx, yDat - amp * 0.7, cx, yDat + amp * 0.7 + 44, color=CHG, sw=0.8, dash="2 3"))
    p.append(text((x0 + xend) / 2, yDat + amp * 0.7 + 58,
                  "ведений (Mode 1): знімає на спаданні — якраз на ПЕРЕХОДІ даних", size=10, color=CHG, bold=True))
    p.append(text(W / 2, H - 14,
                  "дроти з'єднані бездоганно, а біти виходять зсунуті чи хибні",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "mismatch.svg"), W, H, *p,
           title="Пастка: ведучий і ведений у різних режимах → сміття")


# ── 6. Визначити режим із даташита ────────────────────────────────────────────
def fig_datasheet():
    W, H = 700, 300
    p = []
    amp, period, n = 24, 70, 4
    x0 = 130
    yClk = 110
    f, edges, xend = clock(x0, yClk, amp, period, n, 0)
    p += f
    p.append(text(x0 - 14, yClk + 4, "SCK", size=11, color=CLK, bold=True, anchor="end"))
    rises = edges[0::2]
    # погляд 1: рівень спокою
    p.append(text(x0 - 4, yClk + amp + 26, "погляд 1", size=10, color=NEG, bold=True, anchor="start"))
    p.append(line(x0, yClk + amp, x0, yClk + amp + 22, color=NEG, sw=1.2, dash="3 3"))
    p.append(text(x0 + 4, yClk + amp + 40, "рівень у спокої → CPOL", size=10, color=NEG, anchor="start"))
    p.append(text(x0 + 4, yClk + amp + 54, "тут низько → CPOL = 0", size=10, color=MUTED, anchor="start"))
    # дані + стрілки вибірки на наростаннях
    yDat = 176
    bits = [1, 0, 1, 0]
    changes = [x0 + period * 0.28] + [edges[1::2][i - 1] for i in range(1, n)]
    p.append(dataline(x0, xend, yDat, amp * 0.6, changes, bits[0], color=DAT))
    p.append(text(x0 - 14, yDat + 4, "дані", size=11, color=DAT, bold=True, anchor="end"))
    for rx in rises:
        p.append(tick_arrow(rx, yDat + amp * 0.6 + 20, yDat + amp * 0.6 + 2, CAP))
    p.append(text((x0 + xend) / 2, yDat + amp * 0.6 + 36,
                  "погляд 2: на якому фронті стрілка вибірки → CPHA", size=10, color=CAP, bold=True))
    p.append(text((x0 + xend) / 2, yDat + amp * 0.6 + 50,
                  "тут на наростанні (першому) → CPHA = 0", size=10, color=MUTED))
    p.append(text(W / 2, H - 14, "CPOL = 0 і CPHA = 0 разом = Mode 0",
                  size=11, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "datasheet.svg"), W, H, *p,
           title="Читати режим із часової діаграми даташита")


# ── 7. Усі чотири режими поряд: фронт вибірки проти фронту зміни ───────────────
# Worked-приклад у графіці: один і той самий байт, чотири режими; видно, на якому
# фронті ВИБІРКА (зелена), а на якому дані МІНЯЮТЬСЯ (червоний).
def fig_all_modes():
    W, H = 720, 560
    p = []
    amp, period, n = 18, 50, 4
    x0 = 150
    rowH = 128
    y_top = 70
    specs = [
        ("Mode 0", 0, 0),
        ("Mode 1", 0, 1),
        ("Mode 2", 1, 0),
        ("Mode 3", 1, 1),
    ]
    for idx, (name, cpol, cpha) in enumerate(specs):
        yClk = y_top + idx * rowH
        f, edges, xend = clock(x0, yClk, amp, period, n, cpol)
        p += f
        p.append(text(x0 - 16, yClk + 4, name, size=12, color=INK, bold=True, anchor="end"))
        p.append(text(x0 - 16, yClk + 20, "(%d,%d)" % (cpol, cpha), size=9, color=MUTED, anchor="end"))
        # фронти за часом: edges[0],edges[1],...; «перший фронт такту» = edges[0]
        # вибірка: CPHA=0 → перші фронти (індекси 0,2,4..); CPHA=1 → другі (1,3,5..)
        cap_edges = edges[0::2] if cpha == 0 else edges[1::2]
        chg_edges = edges[1::2] if cpha == 0 else edges[0::2]
        yDat = yClk + 54
        # дані міняються на chg-фронтах; перший біт виставлено до першого фронту
        changes = [x0 + period * 0.30] + [chg_edges[i] for i in range(len(chg_edges) - 1)]
        p.append(dataline(x0, xend, yDat, amp * 0.62, changes, 1, color=DAT))
        p.append(text(x0 - 16, yDat + 4, "дані", size=10, color=DAT, anchor="end"))
        # зелені стрілки — вибірка (знизу вгору в лінію даних)
        for cx in cap_edges:
            p.append(tick_arrow(cx, yDat + amp * 0.62 + 16, yDat + amp * 0.62 + 1, CAP))
        # короткі червоні риски на фронтах зміни
        for cx in chg_edges:
            p.append(line(cx, yClk - amp - 4, cx, yClk - amp - 14, color=CHG, sw=2.0))
    # легенда
    ly = H - 26
    p.append(line(x0, ly, x0 + 24, ly, color=CAP, sw=2.2))
    p.append(text(x0 + 30, ly + 4, "↑ фронт ВИБІРКИ (захоплення біта)", size=10, color=CAP, anchor="start", bold=True))
    p.append(line(x0 + 320, ly, x0 + 344, ly, color=CHG, sw=2.2))
    p.append(text(x0 + 350, ly + 4, "| фронт ЗМІНИ даних", size=10, color=CHG, anchor="start", bold=True))
    render(os.path.join(OUT, "all-modes.svg"), W, H, *p,
           title="Усі чотири режими: де вибірка, а де зміна даних")


if __name__ == "__main__":
    fig_cpol()
    fig_cpha()
    fig_fourmodes()
    fig_mode0()
    fig_mismatch()
    fig_datasheet()
    fig_all_modes()
    print("OK: figures written to", OUT)
