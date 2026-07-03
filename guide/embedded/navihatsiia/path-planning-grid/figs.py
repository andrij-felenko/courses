# -*- coding: utf-8 -*-
"""Фігури теми «Планування шляху: сітка і A*». Чистий Python + svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
def out(name): return os.path.join(IMG, name)

OCC = "#c9ced6"   # зайнята клітина (перешкода)
OCCED = "#8a94a6"


# ── 1) grid-world.svg — світ стає сіткою (occupancy grid) ───────────────────
def fig_grid_world():
    W, H = 780, 400
    frags = []
    frags.append(text(W / 2, 28, "Неперервний світ стає сіткою зайнятості", size=17, bold=True))

    # ── ліворуч: неперервний світ із перешкодою ──
    ox, oy = 40, 70
    side = 300
    frags.append(text(ox + side / 2, oy - 12, "світ як він є", size=13, color=MUTED, bold=True))
    frags.append(rect(ox, oy, side, side, fill="#fbfcfd", stroke=LINE, sw=1.5))
    # перешкода — многокутник (стіна-«кут»)
    poly = [(ox + 90, oy + 60), (ox + 230, oy + 60), (ox + 230, oy + 120),
            (ox + 150, oy + 120), (ox + 150, oy + 240), (ox + 90, oy + 240)]
    dd = "M %.0f %.0f " % poly[0] + " ".join("L %.0f %.0f" % p for p in poly[1:]) + " Z"
    frags.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.5"/>' % (dd, OCC, OCCED))
    # старт і ціль
    frags.append(circle(ox + 45, oy + 45, 8, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(ox + 45, oy + 45 + 4, "S", size=12, color=NEG, bold=True))
    frags.append(circle(ox + 255, oy + 255, 8, fill="#eafaf1", stroke=FIELD, sw=2))
    frags.append(text(ox + 255, oy + 255 + 4, "G", size=12, color=FIELD, bold=True))

    # стрілка «дискретизація»
    frags.append(arrow(ox + side + 18, oy + side / 2, ox + side + 78, oy + side / 2, color=INK, sw=2))
    frags.append(text(ox + side + 48, oy + side / 2 - 10, "растр", size=11.5, color=INK, anchor="middle", bold=True))

    # ── праворуч: сітка ──
    gx, gy = ox + side + 100, oy
    n = 10
    cell = side / n
    frags.append(text(gx + side / 2, oy - 12, "сітка зайнятості", size=13, color=MUTED, bold=True))
    # мапа зайнятості: 1 = стіна
    occ = [[0] * n for _ in range(n)]
    # перекладемо многокутник у клітини приблизно (кут-стіна)
    for r in range(n):
        for c in range(n):
            cxp = gx + c * cell + cell / 2
            cyp = gy + r * cell + cell / 2
            # відповідність до поля ліворуч
            lx = ox + (cxp - gx)
            ly = oy + (cyp - gy)
            # точка в многокутнику? груба перевірка за габаритами кута
            inside = ((ox + 90 <= lx <= ox + 230 and oy + 60 <= ly <= oy + 120) or
                      (ox + 90 <= lx <= ox + 150 and oy + 60 <= ly <= oy + 240))
            occ[r][c] = 1 if inside else 0
    for r in range(n):
        for c in range(n):
            x = gx + c * cell
            y = gy + r * cell
            fill = OCC if occ[r][c] else "#ffffff"
            frags.append(rect(x, y, cell, cell, fill=fill, stroke="#d0d6de", sw=0.8, rx=0))
    # старт / ціль у клітинах
    frags.append(rect(gx, gy, cell, cell, fill="#eaf0fd", stroke=NEG, sw=2, rx=0))
    frags.append(text(gx + cell / 2, gy + cell / 2 + 4, "S", size=12, color=NEG, bold=True))
    frags.append(rect(gx + 8 * cell, gy + 8 * cell, cell, cell, fill="#eafaf1", stroke=FIELD, sw=2, rx=0))
    frags.append(text(gx + 8.5 * cell, gy + 8.5 * cell + 4, "G", size=12, color=FIELD, bold=True))

    frags.append(text(W / 2, H - 12,
                      "кожна клітина — вільна (біла) або зайнята (сіра); рух дозволено лише між сусідніми вільними клітинами",
                      size=11.5, color=MUTED))
    render(out("grid-world.svg"), W, H, *frags)


# ── 2) neighbours.svg — 4- проти 8-зв'язності ───────────────────────────────
def fig_neighbours():
    W, H = 720, 320
    frags = []
    frags.append(text(W / 2, 28, "Куди можна крокувати: 4- і 8-зв'язність", size=17, bold=True))

    def grid3(ox, oy, cell, diag, title):
        f = [text(ox + 1.5 * cell, oy - 12, title, size=13, bold=True)]
        for r in range(3):
            for c in range(3):
                f.append(rect(ox + c * cell, oy + r * cell, cell, cell,
                              fill="#ffffff", stroke="#d0d6de", sw=1, rx=0))
        # центр
        ccx = ox + 1.5 * cell
        ccy = oy + 1.5 * cell
        f.append(rect(ox + cell, oy + cell, cell, cell, fill="#eaf0fd", stroke=NEG, sw=2, rx=0))
        # стрілки до сусідів
        dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dirs8 = dirs4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        dd = dirs8 if diag else dirs4
        for dc, dr in dd:
            tx = ccx + dc * cell
            ty = ccy + dr * cell
            col = FIELD if (dc == 0 or dr == 0) else POS
            f.append(arrow(ccx + dc * cell * 0.32, ccy + dr * cell * 0.32,
                           tx - dc * cell * 0.28, ty - dr * cell * 0.28, color=col, sw=1.8))
        return f

    frags += grid3(70, 70, 66, False, "4-зв'язність: ортогонально")
    frags += grid3(430, 70, 66, True, "8-зв'язність: + діагоналі")

    frags.append(text(190, 300, "4 ходи, кожен «коштує» 1", size=11.5, color=FIELD, anchor="middle"))
    frags.append(text(560, 300, "8 ходів; діагональ довша — коштує √2 ≈ 1.41",
                      size=11.5, color=POS, anchor="middle"))
    render(out("neighbours.svg"), W, H, *frags)


# ── 3) dijkstra-vs-astar.svg — сліпе коло проти скерованого еліпса ───────────
def fig_dijkstra_vs_astar():
    W, H = 780, 400
    frags = []
    frags.append(text(W / 2, 28, "Чому A* швидший: сліпа хвиля vs скерована", size=17, bold=True))

    def scene(ox, title, mode):
        f = [text(ox + 155, 60, title, size=13.5, bold=True)]
        gx, gy = ox + 30, 84
        n = 11
        cell = 26
        S = (2, 5)   # старт (col,row)
        G = (9, 5)   # ціль
        for r in range(n - 2):
            for c in range(n):
                x = gx + c * cell
                y = gy + r * cell
                # чи «оглянута» клітина?
                dS = math.hypot(c - S[0], r - S[1])
                dG = math.hypot(c - G[0], r - G[1])
                if mode == "dij":
                    seen = dS <= 4.3           # рівне коло навколо старту
                else:
                    # еліпс, витягнутий уздовж S→G: оглядаємо, де g+h мале
                    seen = (dS + dG) <= 8.4
                fill = "#fdecea" if (mode == "astar" and seen) else ("#eef3fe" if seen else "#ffffff")
                frags_fill = "#dfe7f5" if seen else "#ffffff"
                if mode == "astar" and seen:
                    frags_fill = "#fbe0dc"
                f.append(rect(x, y, cell, cell, fill=frags_fill, stroke="#d7dce4", sw=0.7, rx=0))
        # шлях S→G (пряма ланка клітин)
        for c in range(S[0], G[0] + 1):
            x = gx + c * cell
            y = gy + S[1] * cell
            f.append(rect(x, y, cell, cell, fill="none", stroke=INK, sw=1.4, rx=0))
        # S, G
        f.append(rect(gx + S[0] * cell, gy + S[1] * cell, cell, cell, fill="#eaf0fd", stroke=NEG, sw=2, rx=0))
        f.append(text(gx + (S[0] + .5) * cell, gy + (S[1] + .5) * cell + 4, "S", size=11, color=NEG, bold=True))
        f.append(rect(gx + G[0] * cell, gy + G[1] * cell, cell, cell, fill="#eafaf1", stroke=FIELD, sw=2, rx=0))
        f.append(text(gx + (G[0] + .5) * cell, gy + (G[1] + .5) * cell + 4, "G", size=11, color=FIELD, bold=True))
        return f

    frags += scene(20, "Дейкстра: росте на всі боки", "dij")
    frags += scene(410, "A*: тягнеться до цілі", "astar")

    frags.append(text(200, H - 40, "оглядає БАГАТО клітин —", size=12, color=NEG, anchor="middle"))
    frags.append(text(200, H - 22, "бо не знає, де ціль", size=12, color=NEG, anchor="middle"))
    frags.append(text(590, H - 40, "оглядає МЕНШЕ клітин —", size=12, color=POS, anchor="middle"))
    frags.append(text(590, H - 22, "евристика підказує напрям", size=12, color=POS, anchor="middle"))
    render(out("dijkstra-vs-astar.svg"), W, H, *frags)


# ── 4) heuristics.svg — Мангеттен, Чебишев, Евклід від клітини до цілі ───────
def fig_heuristics():
    W, H = 760, 400
    frags = []
    frags.append(text(W / 2, 28, "Три способи «на око» оцінити відстань до цілі", size=17, bold=True))

    gx, gy = 60, 70
    n = 8
    cell = 34
    A = (1, 6)   # клітина, з якої оцінюємо (col,row)
    G = (6, 1)   # ціль
    for r in range(n):
        for c in range(n):
            frags.append(rect(gx + c * cell, gy + r * cell, cell, cell,
                              fill="#ffffff", stroke="#d7dce4", sw=0.8, rx=0))

    def ccenter(c, r): return (gx + (c + .5) * cell, gy + (r + .5) * cell)
    ax, ay = ccenter(*A)
    ggx, ggy = ccenter(*G)

    # Мангеттен: сходинки (спершу вздовж стовпців, потім рядків)
    step_pts = [(ax, ay)]
    for c in range(A[0], G[0] + 1):
        step_pts.append(ccenter(c, A[1]))
    for r in range(A[1], G[1] - 1, -1):
        step_pts.append(ccenter(G[0], r))
    dpath = "M " + " L ".join("%.0f %.0f" % p for p in step_pts)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (dpath, NEG))

    # Чебишев: діагональ, поки можна, потім прямо (сірим, штрих)
    dc = G[0] - A[0]      # 5
    dr = A[1] - G[1]      # 5
    diag = min(dc, dr)
    cheb_pts = [(ax, ay)]
    cc, rr = A[0], A[1]
    for _ in range(diag):
        cc += 1; rr -= 1
        cheb_pts.append(ccenter(cc, rr))
    while cc < G[0]:
        cc += 1; cheb_pts.append(ccenter(cc, rr))
    while rr > G[1]:
        rr -= 1; cheb_pts.append(ccenter(cc, rr))
    cpath = "M " + " L ".join("%.0f %.0f" % p for p in cheb_pts)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6 4"/>' % (cpath, POS))

    # Евклід: пряма
    frags.append(line(ax, ay, ggx, ggy, color=FIELD, sw=2.4))

    # A, G
    frags.append(rect(gx + A[0] * cell, gy + A[1] * cell, cell, cell, fill="#eef3fe", stroke=INK, sw=2, rx=0))
    frags.append(text(ax, ay + 4, "A", size=12, color=INK, bold=True))
    frags.append(rect(gx + G[0] * cell, gy + G[1] * cell, cell, cell, fill="#eafaf1", stroke=FIELD, sw=2, rx=0))
    frags.append(text(ggx, ggy + 4, "G", size=12, color=FIELD, bold=True))

    # легенда праворуч
    lx = gx + n * cell + 30
    ly = gy + 6
    rows = [
        (NEG, "Мангеттен |Δx|+|Δy| = 10", "сітка 4-зв'язна", False),
        (POS, "Чебишев max(|Δx|,|Δy|) = 5", "8-зв'язна, діагональ=1", True),
        (FIELD, "Евклід √(Δx²+Δy²) ≈ 7.07", "пряма — фіз. відстань", False),
    ]
    for i, (col, name, note, dash) in enumerate(rows):
        y = ly + i * 60
        frags.append(line(lx, y, lx + 34, y, color=col, sw=3, dash=("6 4" if dash else None)))
        frags.append(text(lx + 44, y + 4, name, size=12.5, color=col, anchor="start", bold=True))
        frags.append(text(lx + 44, y + 22, note, size=11, color=MUTED, anchor="start"))

    frags.append(text(W / 2, H - 12,
                      "евристика має бути ДОПУСТИМА — ніколи не завищувати справжню відстань, інакше A* може проґавити найкоротший шлях",
                      size=11.5, color=MUTED))
    render(out("heuristics.svg"), W, H, *frags)


# ── 5) astar-node.svg — f = g + h на одній клітині фронту ────────────────────
def fig_astar_node():
    W, H = 740, 360
    frags = []
    frags.append(text(W / 2, 28, "Ціна клітини у A*:  f = g + h", size=17, bold=True))

    gx, gy = 60, 70
    n = 8
    cell = 34
    S = (1, 4)
    G = (6, 2)
    cur = (3, 3)   # клітина, яку оцінюємо
    for r in range(n):
        for c in range(n):
            frags.append(rect(gx + c * cell, gy + r * cell, cell, cell,
                              fill="#ffffff", stroke="#d7dce4", sw=0.8, rx=0))

    def cc(c, r): return (gx + (c + .5) * cell, gy + (r + .5) * cell)

    # g: пройдений шлях S→cur (ламана)
    gpts = [cc(S[0], S[1]), cc(2, 4), cc(2, 3), cc(cur[0], cur[1])]
    frags.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" L ".join("%.0f %.0f" % p for p in gpts), NEG))
    # h: оцінка cur→G (штрих)
    cx, cy = cc(*cur)
    ggx, ggy = cc(*G)
    frags.append(line(cx, cy, ggx, ggy, color=POS, sw=2.2, dash="6 4"))

    # позначки клітин
    frags.append(rect(gx + S[0] * cell, gy + S[1] * cell, cell, cell, fill="#eaf0fd", stroke=NEG, sw=2, rx=0))
    frags.append(text(gx + (S[0] + .5) * cell, gy + (S[1] + .5) * cell + 4, "S", size=12, color=NEG, bold=True))
    frags.append(rect(gx + G[0] * cell, gy + G[1] * cell, cell, cell, fill="#eafaf1", stroke=FIELD, sw=2, rx=0))
    frags.append(text(ggx, ggy + 4, "G", size=12, color=FIELD, bold=True))
    frags.append(rect(gx + cur[0] * cell, gy + cur[1] * cell, cell, cell, fill="#fff6e0", stroke=INK, sw=2.2, rx=0))
    frags.append(text(cx, cy + 4, "?", size=13, color=INK, bold=True))

    # підписи g та h — ВБІК від своїх ліній, щоб штрих h не різав напис
    frags.append(text((gpts[0][0] + cx) / 2 - 6, gy + 3.0 * cell + 2, "g = ціна S→сюди", size=11.5, color=NEG, anchor="middle", bold=True))
    frags.append(text((cx + ggx) / 2 + 22, (cy + ggy) / 2 + 24, "h = здогад сюди→G", size=11.5, color=POS, anchor="start", bold=True))

    # права панель — формула й правило
    lx = gx + n * cell + 28
    box = fitbox(lx, gy + 6, 240, 118,
                 "f = g + h\n\ng — точна ціна\nпройденого шляху\n\nh — евристика:\nоптимістичний здогад\nскільки лишилось",
                 size=13, pad=12, fill="#f7f9fc", stroke=LINE)
    frags.append(box)
    frags.append(text(lx + 120, gy + 150,
                      "Беремо з фронту клітину", size=11.5, color=INK, anchor="middle"))
    frags.append(text(lx + 120, gy + 168,
                      "з НАЙМЕНШИМ f", size=12.5, color=POS, anchor="middle", bold=True))
    frags.append(text(lx + 120, gy + 186,
                      "= найперспективнішу", size=11.5, color=MUTED, anchor="middle"))

    frags.append(text(W / 2, H - 12,
                      "g тягне назад до старту (обережність), h тягне вперед до цілі (жадібність); їхня сума f — розумний баланс",
                      size=11.5, color=MUTED))
    render(out("astar-node.svg"), W, H, *frags)


# ── 6) admissible-proof.svg — доказ від супротивного: дешевший шлях вийшов би раніше ──
def fig_admissible_proof():
    W, H = 760, 360
    frags = []
    frags.append(text(W / 2, 28, "Чому допустима h не проґавить найкоротший шлях", size=17, bold=True))

    # горизонтальна вісь-ідея: старт зліва, ціль справа; дві траси між ними
    S = (70, 200)
    Gc = (690, 200)
    # проміжна клітина n на дешевшій (оптимальній) трасі, ще у фронті
    N = (330, 250)

    # старт і ціль
    frags.append(circle(S[0], S[1], 15, fill="#eaf0fd", stroke=NEG, sw=2.4))
    frags.append(text(S[0], S[1] + 5, "S", size=14, color=NEG, bold=True))
    frags.append(circle(Gc[0], Gc[1], 15, fill="#eafaf1", stroke=FIELD, sw=2.4))
    frags.append(text(Gc[0], Gc[1] + 5, "G", size=14, color=FIELD, bold=True))

    # дорога 1 — «дорожча», яку A* саме збирається витягнути (верхня дуга)
    frags.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (S[0] + 14, S[1] - 6, (S[0] + Gc[0]) / 2, 90, Gc[0] - 14, Gc[1] - 6, MUTED))
    frags.append(text((S[0] + Gc[0]) / 2, 96, "шлях, який A* ось-ось оголосить: ціна f(G)", size=12, color=MUTED, bold=True))

    # дорога 2 — справді дешевша, проходить крізь ще-відкриту клітину n (нижня)
    frags.append('<path d="M %d %d L %d %d" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (S[0] + 12, S[1] + 8, N[0], N[1], NEG))
    frags.append('<path d="M %d %d L %d %d" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="7 5"/>'
                 % (N[0], N[1], Gc[0] - 12, Gc[1] + 8, POS))

    # клітина n
    frags.append(circle(N[0], N[1], 13, fill="#fff6e0", stroke=INK, sw=2.2))
    frags.append(text(N[0], N[1] + 5, "n", size=13, color=INK, bold=True, italic=True))

    # підписи g(n) і h(n)
    frags.append(text((S[0] + N[0]) / 2 - 6, (S[1] + N[1]) / 2 + 26, "g(n) — вже точно пройдено", size=11.5, color=NEG, bold=True))
    frags.append(text((N[0] + Gc[0]) / 2 + 6, (N[1] + Gc[1]) / 2 + 30, "h(n) ≤ (справжня решта)", size=11.5, color=POS, bold=True))

    # ключова нерівність — рамка (широка, щоб шрифт лишився читним)
    box = fitbox(70, 292, 620, 52,
                 "f(n) = g(n) + h(n)  ≤  (ціна дешевшого шляху)  <  f(G)",
                 size=14, pad=12, fill="#f7f9fc", stroke=INK, bold=False)
    frags.append(box)
    frags.append(text(W / 2, H - 6,
                      "отже n має МЕНШЕ f — його витягли б РАНІШЕ за G; суперечність",
                      size=12, color=POS, bold=True))
    render(out("admissible-proof.svg"), W, H, *frags)


# ── 7) consistency-triangle.svg — трикутна нерівність на евристиці ───────────
def fig_consistency_triangle():
    W, H = 720, 360
    frags = []
    frags.append(text(W / 2, 28, "Узгодженість: трикутна нерівність на h", size=17, bold=True))

    # три точки: n, сусід n', ціль G
    n = (140, 250)
    n2 = (420, 250)
    G = (560, 90)

    # ребро n→n' (реальна ціна кроку c)
    frags.append(line(n[0], n[1], n2[0], n2[1], color=INK, sw=2.6))
    frags.append(text((n[0] + n2[0]) / 2, n[1] + 26, "ціна кроку  c(n, n′)", size=12.5, color=INK, bold=True))

    # h(n) — оцінка від n до G (штрих)
    frags.append(line(n[0], n[1], G[0], G[1], color=NEG, sw=2.4, dash="7 5"))
    frags.append(text((n[0] + G[0]) / 2 - 40, (n[1] + G[1]) / 2, "h(n)", size=13, color=NEG, bold=True))

    # h(n') — оцінка від n' до G (штрих)
    frags.append(line(n2[0], n2[1], G[0], G[1], color=POS, sw=2.4, dash="7 5"))
    frags.append(text((n2[0] + G[0]) / 2 + 14, (n2[1] + G[1]) / 2, "h(n′)", size=13, color=POS, bold=True))

    # вузли
    for (px, py, lab, col, fillc) in [
        (n[0], n[1], "n", INK, "#fff6e0"),
        (n2[0], n2[1], "n′", INK, "#fff6e0"),
        (G[0], G[1], "G", FIELD, "#eafaf1")]:
        frags.append(circle(px, py, 14, fill=fillc, stroke=col, sw=2.4))
        frags.append(text(px, py + 5, lab, size=13, color=col, bold=True, italic=(lab != "G")))

    # нерівність
    box = fitbox(150, 300, 420, 46,
                 "h(n)  ≤  c(n, n′)  +  h(n′)",
                 size=15, pad=10, fill="#f7f9fc", stroke=INK, bold=True)
    frags.append(box)
    frags.append(text(W / 2, H - 4,
                      "оцінка з n не більша за «крок + оцінка з сусіда» — як сторона трикутника",
                      size=11.5, color=MUTED))
    render(out("consistency-triangle.svg"), W, H, *frags)


# ── 8) binary-heap.svg — двійкова купа: масив ⟷ дерево, sift-up ──────────────
def fig_binary_heap():
    W, H = 780, 400
    frags = []
    frags.append(text(W / 2, 28, "Двійкова купа: той самий масив, читаний як дерево", size=17, bold=True))

    vals = [3, 7, 5, 12, 9, 8, 11]   # купа: батько ≤ діти; корінь найменший
    # ── масив унизу ──
    ax, ay = 90, 330
    cw = 68
    frags.append(text(ax - 34, ay + 22, "масив:", size=12.5, color=MUTED, bold=True, anchor="middle"))
    for i, v in enumerate(vals):
        x = ax + i * cw
        fill = "#eafaf1" if i == 0 else FILL
        frags.append(rect(x, ay, cw - 6, 40, fill=fill, stroke=LINE, sw=1.4))
        frags.append(text(x + (cw - 6) / 2, ay + 26, str(v), size=15, bold=True))
        frags.append(text(x + (cw - 6) / 2, ay - 8, "[%d]" % i, size=11, color=MUTED))

    # ── дерево вгорі: позиції вузлів ──
    # рівні: 0 -> {0}; 1 -> {1,2}; 2 -> {3,4,5,6}
    node_xy = {
        0: (W / 2,        80),
        1: (W / 2 - 150, 150), 2: (W / 2 + 150, 150),
        3: (W / 2 - 220, 225), 4: (W / 2 - 80, 225),
        5: (W / 2 + 80, 225),  6: (W / 2 + 220, 225),
    }
    children = {0: (1, 2), 1: (3, 4), 2: (5, 6)}
    # ребра дерева
    for p, (l, r) in children.items():
        for c in (l, r):
            px, py = node_xy[p]; cx, cy = node_xy[c]
            frags.append(line(px, py, cx, cy, color=LINE, sw=1.3))
    # вузли
    for i, v in enumerate(vals):
        cx, cy = node_xy[i]
        fill = "#eafaf1" if i == 0 else "#fbfcfd"
        stroke = FIELD if i == 0 else LINE
        frags.append(circle(cx, cy, 20, fill=fill, stroke=stroke, sw=2))
        frags.append(text(cx, cy + 5, str(v), size=15, bold=True))
    frags.append(text(node_xy[0][0], node_xy[0][1] - 30, "мінімум — завжди тут", size=11.5, color=FIELD, bold=True))

    # формула зв'язку індексів — у вільному верхньому лівому куті
    frags.append(fitbox(120, 90, 210, 52,
                        "дитя [i] → [2i+1], [2i+2]\nбатько [i] → [(i−1)/2]",
                        size=12.5, pad=8, fill="#f7f9fc", stroke=INK))

    # sift-up ілюстрація: підпис у вільному верхньому правому куті
    frags.append(text(W - 150, 84, "sift-up: менший спливає", size=11, color=NEG, anchor="middle"))
    frags.append(text(W - 150, 99, "гілкою вгору, міняючись", size=11, color=NEG, anchor="middle"))
    frags.append(text(W - 150, 114, "із батьком", size=11, color=NEG, anchor="middle"))

    render(out("binary-heap.svg"), W, H, *frags)


# ── 9) corner-cut.svg — пастка зрізаного кута ────────────────────────────────
def fig_corner_cut():
    W, H = 760, 380
    frags = []
    frags.append(text(W / 2, 28, "Пастка зрізаного кута: діагональ крізь ріг стін", size=17, bold=True))

    n = 3
    cell = 78

    def cx_(ox, c): return ox + c * cell + cell / 2
    def cy_(oy, r): return oy + r * cell + cell / 2

    def draw_grid(ox, oy, occ, label, sub):
        frags.append(text(ox + n * cell / 2, oy - 12, label, size=13.5, color=MUTED, bold=True))
        for r in range(n):
            for c in range(n):
                x = ox + c * cell; y = oy + r * cell
                fill = OCC if occ[r][c] else "#fbfcfd"
                frags.append(rect(x, y, cell, cell, fill=fill, stroke=LINE, sw=1.3, rx=2))
        frags.append(text(ox + n * cell / 2, oy + n * cell + 22, sub, size=11.5, color=MUTED))

    # Мапа (рядок згори=0). Стіна одна: (0,1) — прямо НАД шляхом діагоналі.
    # A=(1,0) внизу-ліворуч; G=(0,1) вгорі. Діагональ A→G йшла б між (0,0) і (1,1)?
    # Простіше й чесніше: A=(2,0), G=(1,1); діагональ угору-праворуч проходить
    # між (1,0)[над A] і (2,1)[праворуч від A]. Стіна на (1,0) → діагональ заборонена,
    # а G=(1,1) досяжна обходом (2,0)->(2,1)->(1,1). Ставимо стіну і на (0,1) для «рогу».
    occ = [[0, 1, 0],
           [1, 0, 0],
           [0, 0, 0]]

    # ── ліворуч: наївний зріз ──
    ox1, oy1 = 70, 78
    draw_grid(ox1, oy1, occ, "наївно: зрізає ріг", "діагональ черкає стіну над собою")
    ax, ay = cx_(ox1, 0), cy_(oy1, 2)      # A = (row2,col0)
    gx, gy = cx_(ox1, 1), cy_(oy1, 1)      # G = (row1,col1)
    frags.append(arrow(ax, ay, gx, gy, color=POS, sw=2.8))
    frags.append(circle(ax, ay, 10, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(ax, ay + 4, "A", size=12, color=NEG, bold=True))
    frags.append(circle(gx, gy, 10, fill="#eafaf1", stroke=FIELD, sw=2))
    frags.append(text(gx, gy + 4, "G", size=12, color=FIELD, bold=True))

    # ── праворуч: правильний обхід ──
    ox2, oy2 = 430, 78
    draw_grid(ox2, oy2, occ, "правильно: обхід рогу", "два ортогональні кроки")
    a2x, a2y = cx_(ox2, 0), cy_(oy2, 2)    # (2,0)
    w2x, w2y = cx_(ox2, 1), cy_(oy2, 2)    # (2,1)
    g2x, g2y = cx_(ox2, 1), cy_(oy2, 1)    # (1,1)
    frags.append(line(a2x, a2y, w2x, w2y, color=FIELD, sw=2.8))   # право
    frags.append(arrow(w2x, w2y, g2x, g2y, color=FIELD, sw=2.8))  # вгору
    frags.append(circle(a2x, a2y, 10, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(a2x, a2y + 4, "A", size=12, color=NEG, bold=True))
    frags.append(circle(g2x, g2y, 10, fill="#eafaf1", stroke=FIELD, sw=2))
    frags.append(text(g2x, g2y + 4, "G", size=12, color=FIELD, bold=True))

    render(out("corner-cut.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_grid_world()
    fig_neighbours()
    fig_dijkstra_vs_astar()
    fig_heuristics()
    fig_astar_node()
    fig_admissible_proof()
    fig_consistency_triangle()
    fig_binary_heap()
    fig_corner_cut()
    print("OK: grid-world, neighbours, dijkstra-vs-astar, heuristics, astar-node, admissible-proof, consistency-triangle, binary-heap, corner-cut")
