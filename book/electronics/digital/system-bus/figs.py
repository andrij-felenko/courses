# -*- coding: utf-8 -*-
"""Фігури до теми «Системна шина».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Кістяк шини: процесор + три вузли на трьох групах спільних ліній ────────
# Ідея: показати одну спільну магістраль (три доріжки-групи), заведену
# паралельно до всіх. Адреса — однонапрямлена (стрілки від ядра), дані —
# двонапрямлені (стрілка в обидва боки), керування — від ядра.
def fig_bus_lines():
    W, H = 780, 430
    f = []
    f.append(text(W / 2, 30, "Одна спільна магістраль — усі вузли паралельно на ній",
                  size=17, bold=True))

    # три горизонтальні спільні лінії (групи)
    xL, xR = 60, 720
    yA, yD, yC = 300, 335, 370          # адреса / дані / керування
    f.append(line(xL, yA, xR, yA, color=NEG, sw=3))
    f.append(line(xL, yD, xR, yD, color=POS, sw=3))
    f.append(line(xL, yC, xR, yC, color=FIELD, sw=3))
    f.append(text(xR + 6, yA + 4, "адреса", size=12, anchor="start", color=NEG, bold=True))
    f.append(text(xR + 6, yD + 4, "дані", size=12, anchor="start", color=POS, bold=True))
    f.append(text(xR + 6, yC + 4, "керування", size=12, anchor="start", color=FIELD, bold=True))

    # процесор (ведучий) ліворуч угорі
    px, py, pw, ph = 70, 70, 150, 70
    f.append(fitbox(px, py, pw, ph, "процесор\n(ведучий)", size=14,
                    fill="#eef2ff", stroke=NEG, sw=2, bold=True))
    pcx = px + pw / 2
    # процесор виставляє адресу (стрілка вниз до лінії адреси) — однонапрямлено
    f.append(arrow(pcx - 30, py + ph, pcx - 30, yA - 3, color=NEG, sw=2))
    # двонапрямлені дані
    f.append(line(pcx, py + ph, pcx, yD - 3, color=POS, sw=2))
    f.append(arrow(pcx, yD - 22, pcx, yD - 3, color=POS, sw=1.8))
    f.append(arrow(pcx, yD - 3, pcx, yD - 22, color=POS, sw=1.8))
    # керування від процесора
    f.append(arrow(pcx + 30, py + ph, pcx + 30, yC - 3, color=FIELD, sw=2))

    # три ведені вузли праворуч, рівномірно
    nodes = [("ОЗП", 300), ("ПЗП", 460), ("порт /\nтаймер", 600)]
    for label, nx in nodes:
        nw, nh = 120, 62
        nxx = nx
        f.append(fitbox(nxx, 78, nw, nh, label, size=13,
                        fill="#f4f6f8", stroke=LINE, sw=1.6))
        cx = nxx + nw / 2
        # кожен вузол чіпляється до ВСІХ трьох ліній
        f.append(line(cx, 78 + nh, cx, yA - 3, color=NEG, sw=1.6))
        # дані двонапрямлені
        f.append(arrow(cx, yD - 20, cx, yD - 3, color=POS, sw=1.5))
        f.append(arrow(cx, yD - 3, cx, yD - 20, color=POS, sw=1.5))
        f.append(line(cx, yC - 3, cx, 78 + nh, color=FIELD, sw=1.6))
        # точки під'єднання до ліній
        f.append(circle(cx, yA, 3.2, fill=NEG, stroke=NEG))
        f.append(circle(cx, yD, 3.2, fill=POS, stroke=POS))
        f.append(circle(cx, yC, 3.2, fill=FIELD, stroke=FIELD))

    # точки під'єднання процесора
    f.append(circle(pcx - 30, yA, 3.2, fill=NEG, stroke=NEG))
    f.append(circle(pcx, yD, 3.2, fill=POS, stroke=POS))
    f.append(circle(pcx + 30, yC, 3.2, fill=FIELD, stroke=FIELD))

    f.append(text(W / 2, H - 14,
                  "Адресні лінії виставляє ведучий (одна стрілка); дані двонапрямлені; керування задає напрям і мить.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "bus-lines.svg"), W, H, *f)


# ── 2. Один цикл читання: адреса → вибір однієї → дані назад → защіпка ─────────
# Ідея: чотири кроки в часі зліва направо, кожен — що на якій групі ліній.
def fig_bus_cycle():
    W, H = 780, 380
    f = []
    f.append(text(W / 2, 30, "Цикл читання: адреса → вибір однієї → дані → защіпка",
                  size=17, bold=True))

    steps = [
        ("1. Ядро виставляє", ["адреса 0x2000", "керування: «читаю»"], NEG),
        ("2. Дешифратор", ["старші біти →", "«вибір» одній мікр."], FIELD),
        ("3. Мікросхема віддає", ["виходить із Hi-Z,", "дані на лінії"], POS),
        ("4. Ядро защіпує", ["пауза на устій,", "число всередину"], NEG),
    ]
    n = len(steps)
    bw, bh = 150, 96
    gap = (W - 40 - n * bw) / (n - 1)
    y = 90
    cxs = []
    for i, (title, lines, col) in enumerate(steps):
        x = 20 + i * (bw + gap)
        cxs.append(x + bw / 2)
        f.append(text(x + bw / 2, y - 8, title, size=12.5, bold=True, color=col))
        f.append(fitbox(x, y, bw, bh, "\n".join(lines), size=12,
                        fill="#f4f6f8", stroke=col, sw=1.8))
        if i < n - 1:
            ax = x + bw
            f.append(arrow(ax + 4, y + bh / 2, ax + gap - 4, y + bh / 2, color=MUTED, sw=2))

    # смуга-нагадування: старші біти на дешифратор, молодші в мікросхему
    yb = y + bh + 46
    f.append(rect(60, yb, W - 120, 66, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(W / 2, yb + 24,
                  "Старші біти адреси → дешифратор обирає мікросхему.",
                  size=12.5, color=INK))
    f.append(text(W / 2, yb + 46,
                  "Молодші біти адреси → всередину обраної мікросхеми, вибирають комірку.",
                  size=12.5, color=INK))

    f.append(text(W / 2, H - 12,
                  "У кожну мить відповідає рівно одна мікросхема; запис іде дзеркально — дані виставляє ядро.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "bus-cycle.svg"), W, H, *f)


# ── 3. Спільний дріт (один за раз) vs перемикач (кілька пар паралельно) ────────
# Ідея: зліва всі на одній лінії, підпис «веде один». Справа комутатор, дві
# пари вузлів з'єднані водночас різними шляхами.
def fig_shared_vs_switch():
    W, H = 800, 430
    f = []
    f.append(text(W / 2, 30, "Спільний дріт vs з'єднання з перемиканням", size=17, bold=True))

    # ── ЛІВО: спільна шина ──
    lx0, lx1 = 50, 350
    f.append(text((lx0 + lx1) / 2, 60, "спільний дріт: веде один за раз",
                  size=13, bold=True, color=POS))
    ybus = 250
    f.append(line(lx0, ybus, lx1, ybus, color=POS, sw=3))
    left_nodes = [("A", 80), ("B", 160), ("C", 240), ("D", 320)]
    for label, nx in left_nodes:
        f.append(circle(nx, 130, 22, fill="#fdecea", stroke=POS, sw=2))
        f.append(text(nx, 136, label, size=15, bold=True, color=POS))
        f.append(line(nx, 152, nx, ybus, color=POS, sw=1.6))
        f.append(circle(nx, ybus, 3.2, fill=POS, stroke=POS))
    # тільки одна пара реально говорить — виділимо A↔C, решта чекає
    f.append(text((lx0 + lx1) / 2, ybus + 30,
                  "лише одна пара обмінюється,", size=11, color=MUTED))
    f.append(text((lx0 + lx1) / 2, ybus + 46,
                  "решта чекає своєї черги", size=11, color=MUTED))

    # роздільник
    f.append(line(W / 2, 55, W / 2, H - 40, color="#dddddd", sw=1.5, dash="4,5"))

    # ── ПРАВО: перемикач ──
    rx0, rx1 = 450, 780
    rcx = (rx0 + rx1) / 2
    f.append(text(rcx, 60, "перемикач: кілька пар водночас",
                  size=13, bold=True, color=FIELD))
    # комутатор у центрі
    swx, swy, sww, swh = rcx - 45, 210, 90, 70
    f.append(fitbox(swx, swy, sww, swh, "кому-\nтатор", size=13,
                    fill="#e7f6ee", stroke=FIELD, sw=2, bold=True))
    scx, scy = rcx, swy + swh / 2
    right_nodes = [("A", rx0 + 20, 110), ("B", rx1 - 20, 110),
                   ("C", rx0 + 20, 360), ("D", rx1 - 20, 360)]
    pos = {}
    for label, nx, ny in right_nodes:
        f.append(circle(nx, ny, 22, fill="#e7f6ee", stroke=FIELD, sw=2))
        f.append(text(nx, ny + 6, label, size=15, bold=True, color=FIELD))
        pos[label] = (nx, ny)
        # тонка сіра лінія кожного вузла до комутатора
        f.append(line(nx, ny, scx, scy, color="#cfd6dd", sw=1.2))
    # дві активні пари: A↔D і B↔C — жирнішим зеленим крізь комутатор
    for a, b in [("A", "D"), ("B", "C")]:
        (ax, ay), (bx, by) = pos[a], pos[b]
        f.append(line(ax, ay, scx, scy, color=FIELD, sw=2.6))
        f.append(line(scx, scy, bx, by, color=FIELD, sw=2.6))
    f.append(text(rcx, H - 40,
                  "A↔D і B↔C передають одночасно, не заважаючи одне одному",
                  size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "shared-vs-switch.svg"), W, H, *f)


# ── 4. [вставка hist] Три ери з'єднання: шина → ґратка → мережа ────────────────
# Ідея: три панелі зліва направо. (1) спільна шина — вузли на одному дроті;
# (2) crossbar — матриця перехресть, кілька пар паралельно; (3) NoC —
# маршрутизатори сіткою, короткі ланки, пакет летить. Дуга подолання стелі.
def fig_hist_eras():
    W, H = 860, 400
    f = []
    f.append(text(W / 2, 28, "Три ери з'єднання в кристалі", size=17, bold=True))

    panels = [(30, 300, "Спільна шина", POS, "веде один за раз"),
              (310, 300, "Перемикач-ґратка", FIELD, "кілька пар водночас, ~N²"),
              (590, 300, "Мережа-на-кристалі", NEG, "пакети, короткі ланки")]
    for x0, w, title, col, sub in panels:
        f.append(text(x0 + w / 2, 62, title, size=14, bold=True, color=col))
        f.append(text(x0 + w / 2, 80, sub, size=11, color=MUTED))

    # роздільники між панелями
    for xd in (300, 580):
        f.append(line(xd, 52, xd, H - 30, color="#dddddd", sw=1.4, dash="4,5"))

    # ── панель 1: спільна шина ──
    ybus = 250
    f.append(line(55, ybus, 275, ybus, color=POS, sw=3))
    for i, lab in enumerate(["A", "B", "C", "D"]):
        nx = 75 + i * 62
        f.append(circle(nx, 140, 19, fill="#fdecea", stroke=POS, sw=2))
        f.append(text(nx, 146, lab, size=14, bold=True, color=POS))
        f.append(line(nx, 159, nx, ybus, color=POS, sw=1.5))
        f.append(circle(nx, ybus, 3, fill=POS, stroke=POS))
    f.append(text(165, ybus + 26, "усі на одному дроті", size=11, color=MUTED))

    # ── панель 2: crossbar (матриця перехресть) ──
    gx0, gy0, cell = 350, 120, 40
    rows, cols = 3, 3
    # горизонтальні (входи) і вертикальні (виходи) шини ґратки
    for r in range(rows):
        yy = gy0 + r * cell
        f.append(line(gx0, yy, gx0 + cols * cell, yy, color=FIELD, sw=1.8))
    for c in range(cols):
        xx = gx0 + c * cell
        f.append(line(xx, gy0, xx, gy0 + rows * cell, color=FIELD, sw=1.8))
    # замкнені перехрестя (активні пари) — жирні крапки
    for r, c in [(0, 2), (1, 0), (2, 1)]:
        f.append(circle(gx0 + c * cell, gy0 + r * cell, 5, fill=FIELD, stroke=FIELD))
    # решта перехресть — порожні кружечки
    for r in range(rows):
        for c in range(cols):
            if (r, c) not in [(0, 2), (1, 0), (2, 1)]:
                f.append(circle(gx0 + c * cell, gy0 + r * cell, 3.2,
                                fill=BG, stroke=FIELD, sw=1.3))
    f.append(text(gx0 + cols * cell / 2, gy0 + rows * cell + 26,
                  "замкнув перехрестя — пара сполучена", size=11, color=MUTED))

    # ── панель 3: NoC (маршрутизатори сіткою) ──
    nx0, ny0, ncell = 630, 120, 55
    routers = {}
    for r in range(2):
        for c in range(3):
            rx, ry = nx0 + c * ncell, ny0 + r * ncell
            routers[(r, c)] = (rx, ry)
    # ланки між сусідами
    for (r, c), (rx, ry) in routers.items():
        if (r, c + 1) in routers:
            ox, oy = routers[(r, c + 1)]
            f.append(line(rx, ry, ox, oy, color="#c9cfd6", sw=1.6))
        if (r + 1, c) in routers:
            ox, oy = routers[(r + 1, c)]
            f.append(line(rx, ry, ox, oy, color="#c9cfd6", sw=1.6))
    # маршрутизатори — маленькі квадратики
    for (r, c), (rx, ry) in routers.items():
        f.append(rect(rx - 9, ry - 9, 18, 18, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=3))
    # пакет летить маршрутом (0,0)->(0,1)->(1,1)->(1,2) — жирна дуга
    path_pts = [(0, 0), (0, 1), (1, 1), (1, 2)]
    for a, b in zip(path_pts, path_pts[1:]):
        (ax, ay), (bx, by) = routers[a], routers[b]
        f.append(line(ax, ay, bx, by, color=NEG, sw=3))
    # сам «пакет» — маленька крапка в дорозі
    px, py = routers[(1, 1)]
    f.append(circle(px, py, 4.5, fill=NEG, stroke=NEG))
    f.append(text(nx0 + ncell, ny0 + ncell + 40,
                  "пакет летить від вузла до вузла", size=11, color=MUTED))

    f.append(text(W / 2, H - 12,
                  "Кожна ера долає стелю смуги попередньої — ціною складнішого з'єднання.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "hist-eras.svg"), W, H, *f)


if __name__ == "__main__":
    fig_bus_lines()
    fig_bus_cycle()
    fig_shared_vs_switch()
    fig_hist_eras()
    print("OK: figures written to", IMG)
