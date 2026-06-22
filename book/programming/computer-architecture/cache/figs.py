# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── gap: ядро мчить, пам'ять відстає ──────────────────────────────────────────
# Ідея: дві криві зростання в часі — ядро по крутій, пам'ять по пологій;
# вертикаль між ними = розрив («стіна пам'яті»), що дедалі ширшає.

def fig_gap():
    W, H = 720, 380
    ox, oy = 90, 300          # початок осей
    aw, ah = 420, 250         # довжина осей
    p = []

    p.append(arrow(ox, oy, ox, oy - ah - 6, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    p.append(text(ox - 10, oy - ah + 2, "швидкодія", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox - 10, oy - ah + 16, "(лог.)", size=9, color=MUTED, anchor="end"))
    p.append(text(ox + aw, oy + 20, "роки →", size=11, color=INK, anchor="end", bold=True))

    # крива ядра — крута експонента
    core = []
    mem = []
    for i in range(0, 101):
        t = i / 100.0
        core.append("%.1f,%.1f" % (ox + t * aw, oy - ah * (0.06 + 0.9 * (t ** 1.7))))
        mem.append("%.1f,%.1f" % (ox + t * aw, oy - ah * (0.06 + 0.20 * t)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(core), POS))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(mem), NEG))

    p.append(text(ox + aw * 0.52, oy - ah * 0.82, "ядро", size=12, color=POS, bold=True, anchor="start"))
    p.append(text(ox + aw * 0.52, oy - ah * 0.82 + 14, "× тисячі", size=9.5, color=POS, anchor="start"))
    p.append(text(ox + aw * 0.60, oy - ah * 0.20, "пам'ять", size=12, color=NEG, bold=True, anchor="start"))
    p.append(text(ox + aw * 0.60, oy - ah * 0.20 + 14, "× лише в рази", size=9.5, color=NEG, anchor="start"))

    # розрив на правому краю
    gx = ox + aw * 0.985
    yt = oy - ah * (0.06 + 0.9)
    yb = oy - ah * (0.06 + 0.20)
    p.append(line(gx, yb, gx, yt, color=FIELD, sw=2.2, dash="5 4"))
    p.append(text(gx + 8, (yt + yb) / 2 - 6, "розрив", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(gx + 8, (yt + yb) / 2 + 8, "(дедалі", size=9, color=FIELD, anchor="start"))
    p.append(text(gx + 8, (yt + yb) / 2 + 20, "ширший)", size=9, color=FIELD, anchor="start"))

    # пояснювальна рамка
    box = fitbox(ox + 12, oy - ah + 6, 196, 84,
                 "Звернення в головну\nпам'ять = десятки–сотні\nтактів простою ядра",
                 size=11, fill="#fdecea", stroke=POS, color=INK)
    p.append(box)

    render(os.path.join(OUT, "gap.svg"), W, H, *p,
           title="Ядро прискорюється швидше за пам'ять — розрив дедалі ширшає")


# ── hierarchy: піраміда пам'яті ───────────────────────────────────────────────
# Ідея: трапеції-щаблі від вузької швидкої вершини (регістри) до широкої
# повільної основи (RAM); стрілки збоку — час доступу й обсяг ростуть униз.

def fig_hierarchy():
    W, H = 720, 420
    cx = 300
    p = []
    levels = [
        ("регістри", "миттєво · байти", 150, "#eafaf0"),
        ("кеш L1", "~3 такти · десятки КБ", 230, "#eef4ff"),
        ("кеш L2", "~12 тактів · сотні КБ", 310, "#eef4ff"),
        ("кеш L3", "~40 тактів · одиниці МБ", 390, "#eef4ff"),
        ("головна пам'ять (RAM)", "~100+ тактів · гігабайти", 480, "#fdf4f4"),
    ]
    top, rowh = 70, 64
    for i, (name, sub, w, fill) in enumerate(levels):
        y = top + i * rowh
        x = cx - w / 2
        p.append(rect(x, y, w, rowh - 12, fill=fill, stroke=LINE, sw=1.6, rx=6))
        p.append(text(cx, y + 22, name, size=12.5, color=INK, bold=True))
        p.append(text(cx, y + 39, sub, size=9.5, color=MUTED))

    # бічні осі-стрілки
    ax = cx + 290
    p.append(arrow(ax, top + 6, ax, top + len(levels) * rowh - 10, color=NEG, sw=1.8))
    p.append(text(ax + 8, top + 40, "час доступу ↑", size=10.5, color=NEG, anchor="start", bold=True))
    p.append(text(ax + 8, top + 56, "обсяг ↑", size=10.5, color=NEG, anchor="start", bold=True))
    axl = cx - 290
    p.append(arrow(axl, top + len(levels) * rowh - 10, axl, top + 6, color=POS, sw=1.8))
    p.append(text(axl - 8, top + 40, "швидкість ↑", size=10.5, color=POS, anchor="end", bold=True))
    p.append(text(axl - 8, top + 56, "ціна за біт ↑", size=10.5, color=POS, anchor="end"))

    render(os.path.join(OUT, "hierarchy.svg"), W, H, *p,
           title="Ієрархія пам'яті: ближче до ядра — швидше, дрібніше, дорожче")


# ── locality: часова й просторова локальність ─────────────────────────────────
# Ідея: ліворуч цикл повертається до тих самих комірок (часова), праворуч іде
# по сусідніх (просторова); кольором виділено, що саме «гаряче».

def fig_locality():
    W, H = 720, 360
    p = []

    # ── ліва панель: часова ──
    lx = 60
    p.append(text(lx + 130, 70, "Часова локальність", size=13, color=INK, bold=True, anchor="middle"))
    p.append(text(lx + 130, 88, "(temporal): недавнє — знову", size=10, color=MUTED, anchor="middle"))
    # стрічка комірок, одна підсвічена, дугові повтори до неї
    cellw, cy = 30, 150
    for i in range(8):
        x = lx + i * cellw
        hot = (i == 3)
        p.append(rect(x, cy, cellw - 4, 30, fill=("#fdecea" if hot else FILL),
                      stroke=(POS if hot else LINE), sw=(2 if hot else 1.2), rx=4))
    hx = lx + 3 * cellw + (cellw - 4) / 2
    for k, r in enumerate((46, 64, 82)):
        p.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>'
                 % (hx - 2, cy, r, r, hx + 2, cy, POS))
    p.append(text(lx + 130, cy + 78, "та сама комірка `i`, `sum`,", size=10.5, color=INK, anchor="middle"))
    p.append(text(lx + 130, cy + 94, "лічильник — щоітерації", size=10.5, color=INK, anchor="middle"))
    p.append(text(lx + 130, cy + 116, "→ тримай недавнє в кеші", size=10.5, color=POS, anchor="middle", bold=True))

    # роздільник
    p.append(line(W / 2, 60, W / 2, H - 30, color="#d8dde3", sw=1.2, dash="4 4"))

    # ── права панель: просторова ──
    rx = 400
    p.append(text(rx + 130, 70, "Просторова локальність", size=13, color=INK, bold=True, anchor="middle"))
    p.append(text(rx + 130, 88, "(spatial): сусід — слідом", size=10, color=MUTED, anchor="middle"))
    for i in range(8):
        x = rx + i * cellw
        seq = (i < 4)
        p.append(rect(x, cy, cellw - 4, 30, fill=("#eafaf0" if seq else FILL),
                      stroke=(FIELD if seq else LINE), sw=(2 if seq else 1.2), rx=4))
        if i < 3:
            ax0 = x + (cellw - 4) / 2
            p.append(arrow(ax0 + 4, cy - 8, ax0 + cellw - 4, cy - 8, color=FIELD, sw=1.5))
    p.append(text(rx + 130, cy + 78, "a[0], a[1], a[2]… — підряд", size=10.5, color=INK, anchor="middle"))
    p.append(text(rx + 130, cy + 94, "масив, рядок, потік", size=10.5, color=INK, anchor="middle"))
    p.append(text(rx + 130, cy + 116, "→ бери сусідів наперед, блоком", size=10.5, color=FIELD, anchor="middle", bold=True))

    render(os.path.join(OUT, "locality.svg"), W, H, *p,
           title="Дві властивості реального коду, на яких тримається кеш")


# ── line: кеш-лінія, влучання й промах ────────────────────────────────────────
# Ідея: ядро ←→ кеш (кілька ліній по N сусідів) ←→ RAM; влучання = коротка
# дешева стрілка, промах = довгий дорогий похід, що тягне ЦІЛУ лінію.

def fig_line():
    W, H = 740, 380
    p = []
    ymid = 200

    # ядро
    p.append(rect(40, ymid - 35, 90, 70, fill="#eafaf0", stroke=INK, sw=1.8))
    p.append(text(85, ymid - 4, "ядро", size=13, color=INK, bold=True))
    p.append(text(85, ymid + 14, "потрібне число", size=9, color=MUTED))

    # кеш: чотири лінії по 4 комірки
    kx, ky = 200, 120
    p.append(text(kx + 140, ky - 14, "КЕШ", size=12, color=NEG, bold=True))
    cellw = 28
    for r in range(4):
        for c in range(4):
            x = kx + c * cellw
            y = ky + r * 34
            hot = (r == 1)
            p.append(rect(x, y, cellw - 3, 26, fill=("#eef4ff" if hot else FILL),
                          stroke=(NEG if hot else LINE), sw=(1.8 if hot else 1.0), rx=3))
        p.append(text(kx + 4 * cellw + 8, ky + r * 34 + 18, "лінія", size=9, color=MUTED, anchor="start"))
    p.append(rect(kx - 8, ky - 8, 4 * cellw + 48, 4 * 34 + 8, fill="none", stroke=NEG, sw=1.4, rx=8))

    # RAM
    rx = 560
    p.append(rect(rx, ymid - 90, 140, 200, fill="#fdf4f4", stroke=INK, sw=1.6))
    p.append(text(rx + 70, ymid - 70, "головна", size=11.5, color=INK, bold=True))
    p.append(text(rx + 70, ymid - 54, "пам'ять (RAM)", size=11.5, color=INK, bold=True))
    p.append(text(rx + 70, ymid + 96, "повільна, велика", size=9, color=MUTED))
    # блок-лінія в RAM
    for c in range(4):
        p.append(rect(rx + 14 + c * 28, ymid - 24, 25, 26, fill="#fde9e7", stroke=POS, sw=1.2, rx=3))
    p.append(text(rx + 70, ymid + 22, "блок сусідів", size=9, color=POS))

    # влучання: ядро → кеш, коротко
    p.append(arrow(133, ymid - 18, kx - 12, ky + 34 + 13, color=FIELD, sw=2.2))
    p.append(text(150, ymid - 40, "влучання (hit):", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(150, ymid - 26, "дані вже в кеші — пара тактів", size=9.5, color=FIELD, anchor="start"))

    # промах: кеш → RAM і назад цілою лінією
    p.append(arrow(kx + 4 * cellw + 44, ymid + 60, rx - 6, ymid - 11, color=POS, sw=2.2))
    p.append(text(kx + 150, ymid + 120, "промах (miss): похід у RAM —", size=10.5, color=POS, anchor="middle", bold=True))
    p.append(text(kx + 150, ymid + 136, "десятки тактів, та приносять ЦІЛУ лінію сусідів", size=9.5, color=INK, anchor="middle"))

    render(os.path.join(OUT, "line.svg"), W, H, *p,
           title="Кеш-лінія: один дорогий промах тягне цілий блок сусідів")


# ── hitmiss: середній час як зважена суміш ────────────────────────────────────
# Ідея: смужка-частка влучань/промахів + підставлені числа, що дають середнє,
# близьке до швидкості кешу.

def fig_hitmiss():
    W, H = 720, 340
    p = []

    # смужка часток
    bx, by, bw, bh = 80, 90, 560, 44
    hitw = bw * 0.95
    p.append(rect(bx, by, hitw, bh, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=0))
    p.append(rect(bx + hitw, by, bw - hitw, bh, fill="#fdecea", stroke=POS, sw=1.6, rx=0))
    p.append(text(bx + hitw / 2, by + 27, "влучання 95% · 3 такти", size=11.5, color=INK, bold=True))
    p.append(text(bx + hitw + (bw - hitw) / 2, by - 8, "промах 5%", size=10, color=POS, bold=True))
    p.append(text(bx + hitw + (bw - hitw) / 2, by + 60, "· 100 тактів", size=9.5, color=POS))

    # формула-блок
    fx, fy = W / 2, 195
    p.append(text(fx, fy, "середній = 0.95·3 + 0.05·100 = 2.85 + 5.0 = 7.85 такту",
                  size=13, color=INK, bold=True))

    # порівняння стовпчиками
    g1x, g2x, gtop, gmaxh = 250, 470, 250, 70
    # без кешу = 100 → масштаб
    h_no = gmaxh
    h_yes = gmaxh * 7.85 / 100
    p.append(rect(g1x - 40, gtop - h_no, 80, h_no, fill="#fdecea", stroke=POS, sw=1.6, rx=4))
    p.append(text(g1x, gtop - h_no - 8, "100", size=12, color=POS, bold=True))
    p.append(text(g1x, gtop + 18, "без кешу", size=10, color=INK))
    p.append(rect(g2x - 40, gtop - h_yes, 80, h_yes, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=4))
    p.append(text(g2x, gtop - h_yes - 8, "≈ 8", size=12, color=FIELD, bold=True))
    p.append(text(g2x, gtop + 18, "із кешем", size=10, color=INK))
    p.append(arrow(g1x + 48, gtop - 10, g2x - 48, gtop - 10, color=MUTED, sw=1.6))
    p.append(text((g1x + g2x) / 2, gtop - 18, "≈ ×13", size=10, color=MUTED, bold=True))

    render(os.path.join(OUT, "hitmiss.svg"), W, H, *p,
           title="Висока частка влучань «розчиняє» рідкісні дорогі промахи")


# ── friendly: дружній і недружній обхід ───────────────────────────────────────
# Ідея: одна стрічка пам'яті, поділена на лінії; ліворуч послідовний доступ
# (1 промах на лінію), праворуч стрибковий (промах щоразу).

def fig_friendly():
    W, H = 740, 380
    p = []
    cellw = 26

    def strip(x0, y0, order, label, sub, good):
        out = []
        # 16 комірок = 4 лінії по 4
        for i in range(16):
            x = x0 + i * cellw
            line_idx = i // 4
            shade = "#eef4ff" if line_idx % 2 == 0 else "#e3ecfb"
            out.append(rect(x, y0, cellw - 2, 28, fill=shade, stroke=LINE, sw=0.9, rx=2))
            if i % 4 == 0:
                out.append(line(x, y0 - 5, x, y0 + 33, color=NEG, sw=1.6))
        out.append(line(x0 + 16 * cellw, y0 - 5, x0 + 16 * cellw, y0 + 33, color=NEG, sw=1.6))
        # порядок доступу + позначка промах/влучання
        col = FIELD if good else POS
        for step, idx in enumerate(order):
            x = x0 + idx * cellw + (cellw - 2) / 2
            miss = (idx % 4 == 0) if good else True
            mk = ("•" if not miss else "✗")
            mc = (FIELD if not miss else POS)
            out.append(text(x, y0 - 10, mk, size=12, color=mc, bold=True))
            out.append(text(x, y0 + 46, str(step + 1), size=9, color=MUTED))
        out.append(text(x0 + 8 * cellw, y0 - 34, label, size=12.5, color=col, bold=True, anchor="middle"))
        out.append(text(x0 + 8 * cellw, y0 + 64, sub, size=10, color=INK, anchor="middle"))
        return out

    p += strip(70, 110, list(range(8)), "Дружній: підряд (крок 1)",
               "1 промах ✗ на лінію, далі влучання • — лінія йде в діло вся", good=True)
    p += strip(70, 260, [0, 4, 8, 12], "Недружній: стрибками (крок = ширина лінії)",
               "майже кожен доступ — промах ✗, з лінії беремо одну комірку", good=False)

    # легенда
    p.append(text(W - 30, 96, "✗ промах   • влучання", size=10, color=MUTED, anchor="end"))

    render(os.path.join(OUT, "friendly.svg"), W, H, *p,
           title="Та сама робота, інший порядок — швидкодія різниться в рази")


# ════════════════ фігури вставки proj-cache-friendly-code ════════════════

# ── order: рядковий vs стовпцевий обхід матриці ───────────────────────────────
# Ідея: матриця N×N, колір клітинки = кешлінія; ліворуч обхід уздовж пам'яті,
# праворуч — впоперек, що стрибає в нову лінію щокроку.

def fig_order():
    W, H = 740, 380
    p = []
    n = 4
    cell = 46

    def matrix(x0, y0, by_row, title, sub, good):
        out = []
        out.append(text(x0 + n * cell / 2, y0 - 34, title, size=12.5,
                        color=(FIELD if good else POS), bold=True, anchor="middle"))
        # кольори ліній: кожен РЯДОК — своя лінія (row-major)
        line_fill = ["#eef4ff", "#eafaf0", "#fdf3e7", "#fdecea"]
        order = []
        for r in range(n):
            for c in range(n):
                order.append((r, c) if by_row else None)
        if not by_row:
            order = [(r, c) for c in range(n) for r in range(n)]
        # намалювати клітинки
        for r in range(n):
            for c in range(n):
                x, y = x0 + c * cell, y0 + r * cell
                out.append(rect(x, y, cell - 4, cell - 4, fill=line_fill[r], stroke=LINE, sw=1.0, rx=3))
        # стрілки порядку обходу
        pts = []
        for (r, c) in order:
            pts.append((x0 + c * cell + (cell - 4) / 2, y0 + r * cell + (cell - 4) / 2))
        for i in range(len(pts) - 1):
            (xa, ya), (xb, yb) = pts[i], pts[i + 1]
            col = FIELD if good else POS
            out.append(line(xa, ya, xb, yb, color=col, sw=1.4))
        out.append(circle(pts[0][0], pts[0][1], 4, fill=INK, stroke=INK, sw=1))
        out.append(text(x0 + n * cell / 2, y0 + n * cell + 22, sub, size=10, color=INK, anchor="middle"))
        return out

    p += matrix(80, 110, True, "Рядками (for r: for c)",
                "уздовж пам'яті: 1 промах на рядок, далі влучання", good=True)
    p += matrix(440, 110, False, "Стовпцями (for c: for r)",
                "впоперек пам'яті: щокрок — нова лінія, промах", good=False)

    # підпис про кольори
    p.append(text(W / 2, H - 18, "колір = кешлінія (рядок матриці); матриця лежить у пам'яті рядок за рядком",
                  size=10, color=MUTED, anchor="middle", italic=True))

    render(os.path.join(OUT, "order.svg"), W, H, *p,
           title="Той самий масив, той самий обсяг роботи — інший порядок обходу")


# ── stride: крок доступу й кешлінія ───────────────────────────────────────────
# Ідея: одна стрічка пам'яті; крок 1 використовує лінію повністю, великий крок
# тягне лінію заради однієї комірки.

def fig_stride():
    W, H = 740, 320
    p = []
    cellw = 30

    def row(y0, step, label, sub, good):
        out = []
        out.append(text(60, y0 - 22, label, size=12, color=(FIELD if good else POS),
                        bold=True, anchor="start"))
        for i in range(16):
            x = 60 + i * cellw
            line_idx = i // 4
            shade = "#eef4ff" if line_idx % 2 == 0 else "#e3ecfb"
            out.append(rect(x, y0, cellw - 2, 30, fill=shade, stroke=LINE, sw=0.9, rx=2))
            if i % 4 == 0:
                out.append(line(x, y0 - 4, x, y0 + 34, color=NEG, sw=1.6))
        out.append(line(60 + 16 * cellw, y0 - 4, 60 + 16 * cellw, y0 + 34, color=NEG, sw=1.6))
        touched = list(range(0, 16, step))
        for k, idx in enumerate(touched):
            x = 60 + idx * cellw + (cellw - 2) / 2
            miss = (idx % 4 == 0) if good else True
            out.append(text(x, y0 - 8, ("✗" if miss else "•"), size=12,
                            color=(POS if miss else FIELD), bold=True))
            out.append(circle(x, y0 + 15, 3, fill=INK, stroke=INK, sw=1))
        out.append(text(60 + 8 * cellw, y0 + 54, sub, size=10, color=INK, anchor="middle"))
        return out

    p += row(110, 1, "Крок 1 (сусідні комірки)",
             "перший у лінії — промах ✗, наступні три — влучання •; лінію використано повністю", good=True)
    p += row(220, 4, "Крок = ширина лінії",
             "кожне звернення — нова лінія, суцільні промахи ✗; з лінії в діло одна комірка", good=False)

    render(os.path.join(OUT, "stride.svg"), W, H, *p,
           title="Крок доступу (stride): пам'ять їздить не байтами, а кешлініями")


# ── layout: AoS проти SoA та де кеш вмикається ────────────────────────────────
# Ідея: ліворуч розкладка даних (AoS тягне зайве, SoA — ні); праворуч — чи є
# взагалі кеш (8-біт МК vs МК із кешем флешу).

def fig_layout():
    W, H = 740, 380
    p = []

    # ── ліва панель: AoS vs SoA ──
    lx = 50
    p.append(text(lx + 150, 70, "Розкладка даних", size=13, color=INK, bold=True, anchor="middle"))
    p.append(text(lx + 150, 86, "беремо лише поле x зі структур {x,y,z}", size=9.5, color=MUTED, anchor="middle"))

    # AoS: x y z x y z ...
    cellw = 26
    ay = 120
    p.append(text(lx, ay - 8, "AoS:", size=11, color=INK, bold=True, anchor="start"))
    labs = ["x", "y", "z"] * 4
    for i, lab in enumerate(labs):
        x = lx + 40 + i * cellw
        use = (lab == "x")
        p.append(rect(x, ay, cellw - 3, 26, fill=("#eafaf0" if use else "#f0f1f3"),
                      stroke=(FIELD if use else "#c7ccd2"), sw=(1.6 if use else 0.9), rx=3))
        p.append(text(x + (cellw - 3) / 2, ay + 18, lab, size=10,
                      color=(INK if use else MUTED)))
    p.append(text(lx + 40 + 6 * cellw, ay + 48, "одна лінія → корисна лише третина", size=9.5, color=POS, anchor="middle"))

    # SoA: x x x x | y y y y | z z z z
    sy = 200
    p.append(text(lx, sy - 8, "SoA:", size=11, color=INK, bold=True, anchor="start"))
    labs2 = ["x"] * 4 + ["y"] * 4 + ["z"] * 4
    for i, lab in enumerate(labs2):
        x = lx + 40 + i * cellw
        use = (lab == "x")
        p.append(rect(x, sy, cellw - 3, 26, fill=("#eafaf0" if use else "#f0f1f3"),
                      stroke=(FIELD if use else "#c7ccd2"), sw=(1.6 if use else 0.9), rx=3))
        p.append(text(x + (cellw - 3) / 2, sy + 18, lab, size=10,
                      color=(INK if use else MUTED)))
    p.append(text(lx + 40 + 2 * cellw, sy + 48, "усі x поспіль → лінія йде в діло вся", size=9.5, color=FIELD, anchor="middle"))

    # роздільник
    p.append(line(W / 2 + 30, 60, W / 2 + 30, H - 40, color="#d8dde3", sw=1.2, dash="4 4"))

    # ── права панель: чи є кеш ──
    rx = 440
    p.append(text(rx + 130, 70, "Чи є з цього зиск?", size=13, color=INK, bold=True, anchor="middle"))
    p.append(text(rx + 130, 86, "залежить від заліза", size=9.5, color=MUTED, anchor="middle"))

    b1 = fitbox(rx, 110, 260, 70,
                "8-бітний МК без кеша\n(SRAM ~1 такт): будь-яка комірка\nоднаково близька — порядок майже не важить",
                size=10, fill="#f0f1f3", stroke="#9aa0a6", color=INK)
    p.append(b1)
    b2 = fitbox(rx, 200, 260, 70,
                "МК із кешем флешу (ESP32-клас):\nпорядок важить сильно, як на ПК —\nпромах флешу дорогий",
                size=10, fill="#eef4ff", stroke=NEG, color=INK)
    p.append(b2)

    render(os.path.join(OUT, "layout.svg"), W, H, *p,
           title="Форма даних і наявність кеша вирішують, чи буде зиск")


if __name__ == "__main__":
    fig_gap()
    fig_hierarchy()
    fig_locality()
    fig_line()
    fig_hitmiss()
    fig_friendly()
    fig_order()
    fig_stride()
    fig_layout()
    print("figs: готово")
