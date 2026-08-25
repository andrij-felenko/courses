# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── color-blob: кадр → HSV-поріг → морфологія → пляма (центр, площа, рамка) ────
# Ідея: найдешевший детектор. Кольоровий тон вирізаємо порогом у HSV, чистимо
# маску морфологією, а зв'язна біла пляма одразу віддає центр, площу й рамку.

def fig_color_blob():
    W, H = 760, 340
    p = []
    bw, bh = 150, 116
    ys = 120
    xs = [30, 230, 430, 630 - (630 - 430 - bw)]  # рівні проміжки
    xs = [30, 224, 418, 612]

    # 1) кадр: три кольорові об'єкти на темному тлі
    x = xs[0]
    p.append(rect(x, ys, bw, bh, fill="#1e293b", stroke=INK, sw=1.2, rx=8))
    p.append(rect(x + 16, ys + 14, 30, 26, fill=NEG, stroke="none", sw=0, rx=5))
    p.append(circle(x + bw - 28, ys + bh - 30, 16, fill=FIELD, stroke="none", sw=0))
    p.append(circle(x + bw / 2, ys + bh / 2, 26, fill="#e08a1e", stroke="none", sw=0))
    p.append(text(x + bw / 2, ys + bh + 16, "кадр", size=11, color=INK, bold=True))

    # 2) HSV-поріг → маска (лишився тільки помаранчевий тон, як біла пляма)
    x = xs[1]
    p.append(rect(x, ys, bw, bh, fill="#0a0d12", stroke=INK, sw=1.2, rx=8))
    p.append(circle(x + bw / 2, ys + bh / 2, 26, fill="#f4f6f8", stroke="none", sw=0))
    p.append(rect(x + 24, ys + 16, 5, 5, fill="#f4f6f8", stroke="none", sw=0, rx=1))
    p.append(rect(x + bw - 30, ys + bh - 24, 4, 4, fill="#f4f6f8", stroke="none", sw=0, rx=1))
    p.append(text(x + bw / 2, ys + bh + 16, "HSV-поріг → маска", size=11, color=INK, bold=True))

    # 3) морфологія: цятки прибрано, лишилась чиста пляма
    x = xs[2]
    p.append(rect(x, ys, bw, bh, fill="#0a0d12", stroke=INK, sw=1.2, rx=8))
    p.append(circle(x + bw / 2, ys + bh / 2, 26, fill="#f4f6f8", stroke="none", sw=0))
    p.append(text(x + bw / 2, ys + bh + 16, "морфологія", size=11, color=INK, bold=True))

    # 4) пляма: центр (хрест) + габаритна рамка
    x = xs[3]
    cx, cy = x + bw / 2, ys + bh / 2
    p.append(rect(x, ys, bw, bh, fill="#0a0d12", stroke=INK, sw=1.2, rx=8))
    p.append(circle(cx, cy, 26, fill="#f4f6f8", stroke="none", sw=0))
    p.append(rect(cx - 28, cy - 28, 56, 56, fill="none", stroke=FIELD, sw=2.2, rx=2))
    p.append(line(cx - 7, cy, cx + 7, cy, color=POS, sw=2.2))
    p.append(line(cx, cy - 7, cx, cy + 7, color=POS, sw=2.2))
    p.append(text(x + bw / 2, ys + bh + 16, "пляма: центр + рамка", size=11, color=INK, bold=True))

    # стрілки між кроками
    for i in range(3):
        x1 = xs[i] + bw
        x2 = xs[i + 1]
        p.append(arrow(x1 + 4, ys + bh / 2, x2 - 4, ys + bh / 2, color=INK, sw=1.7))

    # коробка «що дістаємо»
    box = fitbox(xs[3] - bw - 24, ys + bh + 36, bw + 88, 72,
                 "що дістаємо:\n• центр (cx, cy)\n• площа (пікселі)\n• габаритна рамка",
                 size=10, fill="#eafaf0", stroke=FIELD, sw=1.4, color=INK)
    # ліворуч — короткий підсумок
    p.append(text(40, ys + bh + 58,
                  "Колір — найдешевший сигнал: поріг у HSV, чистка маски —",
                  size=10.5, color=MUTED, anchor="start", italic=True))
    p.append(text(40, ys + bh + 74,
                  "і пляма сама віддає центр, площу й рамку цілі. Тягне навіть МК.",
                  size=10.5, color=MUTED, anchor="start", italic=True))
    p.append(box)

    render(os.path.join(OUT, "color-blob.svg"), W, H, *p,
           title="За кольором: маска → пляма → центр і рамка")


# ── shape-contour: контур → кути / круглість → що це ──────────────────────────
# Ідея: коли колір не виручає, форму впізнають за контуром — рахують кути
# (3 → трикутник, 4 → квадрат) або круглість (0 кутів → коло).

def fig_shape_contour():
    W, H = 760, 372
    p = []
    bw, bh = 200, 156
    ys = 110
    xs = [40, 280, 520]

    # трикутник
    x = xs[0]
    p.append(rect(x, ys, bw, bh, fill="#0f172a", stroke=INK, sw=1.2, rx=8))
    tcx = x + bw / 2
    pts = [(tcx, ys + 28), (x + 34, ys + bh - 28), (x + bw - 34, ys + bh - 28)]
    p.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="3" '
             'stroke-linejoin="round"/>' % (" ".join("%.0f,%.0f" % q for q in pts), NEG))
    for qx, qy in pts:
        p.append(circle(qx, qy, 4.5, fill=POS, stroke=BG, sw=1))
    p.append(text(tcx, ys + bh + 18, "трикутник", size=11, color=NEG, bold=True))
    p.append(text(tcx, ys + bh + 33, "контур → 3 кути", size=9, color=MUTED))

    # квадрат
    x = xs[1]
    p.append(rect(x, ys, bw, bh, fill="#0f172a", stroke=INK, sw=1.2, rx=8))
    scx = x + bw / 2
    sq = [(x + 52, ys + 36), (x + bw - 52, ys + 36),
          (x + bw - 52, ys + bh - 36), (x + 52, ys + bh - 36)]
    p.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="3" '
             'stroke-linejoin="round"/>' % (" ".join("%.0f,%.0f" % q for q in sq), FIELD))
    for qx, qy in sq:
        p.append(circle(qx, qy, 4.5, fill=POS, stroke=BG, sw=1))
    p.append(text(scx, ys + bh + 18, "квадрат", size=11, color=FIELD, bold=True))
    p.append(text(scx, ys + bh + 33, "4 кути, ≈рівні сторони", size=9, color=MUTED))

    # коло
    x = xs[2]
    p.append(rect(x, ys, bw, bh, fill="#0f172a", stroke=INK, sw=1.2, rx=8))
    ccx = x + bw / 2
    p.append(circle(ccx, ys + bh / 2, 50, fill="none", stroke="#d98a00", sw=3))
    p.append(text(ccx, ys + bh + 18, "коло", size=11, color="#d98a00", bold=True))
    p.append(text(ccx, ys + bh + 33, "0 кутів, висока круглість", size=9, color=MUTED))

    # смуга про фільтри плям
    p.append(fitbox(40, ys + bh + 50, W - 80, 56,
                    "Плями ще й фільтрують: за площею (відсіяти дрібне й завелике),\n"
                    "за видовженням і за круглістю — так із купи кандидатів лишаються самі цілі.",
                    size=10, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "shape-contour.svg"), W, H, *p,
           title="За формою: контур → кути → що це")


# ── hough: точки межі → синусоїди в (ρ,θ) → пік голосів → лінія ───────────────
# Ідея: кожна точка межі голосує за всі лінії крізь неї (синусоїда в просторі
# параметрів); справжні точки дають спільний пік — він і є шукана лінія.

def fig_hough():
    W, H = 820, 360
    p = []
    bw, bh = 240, 168
    ys = 96
    x1, x2 = 30, 300

    # ── ліва панель: точки на лінії (з розривами й шумом) ──
    p.append(text(x1 + bw / 2, ys - 10, "точки межі (розриви, шум)",
                  size=10, color=INK, bold=True))
    p.append(rect(x1, ys, bw, bh, fill="#0f172a", stroke=INK, sw=1.2, rx=8))
    # точки на прямій
    line_pts = []
    for i, t in enumerate([0.04, 0.18, 0.30, 0.55, 0.70, 0.82]):
        px = x1 + 24 + t * (bw - 48)
        py = ys + 26 + t * (bh - 52)
        line_pts.append((px, py))
        p.append(circle(px, py, 4, fill="#f8fafc", stroke="none", sw=0))
    # шумові точки
    for nx, nt in [(0.30, 0.78), (0.80, 0.20), (0.12, 0.62)]:
        p.append(circle(x1 + 24 + nx * (bw - 48), ys + 26 + nt * (bh - 52),
                        3, fill=MUTED, stroke="none", sw=0))

    # ── середня панель: синусоїди в (ρ, θ), що сходяться в пік ──
    mx = 320
    p.append(text(mx + 300 / 2, ys - 10, "простір (ρ, θ): точка → синусоїда",
                  size=10, color=INK, bold=True))
    p.append(rect(mx, ys, 300, bh, fill="#0f172a", stroke=INK, sw=1.2, rx=8))
    # синусоїди, що перетинаються в (peak_t≈0.32, середина)
    peak_x = mx + 0.34 * 300
    peak_y = ys + bh * 0.46
    for k, ph in enumerate([-0.9, -0.55, -0.2, 0.15, 0.5, 0.85]):
        pts = []
        for j in range(0, 61):
            th = j / 60.0
            xx = mx + 8 + th * (300 - 16)
            # синусоїда, що проходить через (peak), фаза зсунута для кожної точки
            yy = peak_y + 46 * math.sin(2 * math.pi * (th - 0.34) + ph) - 46 * math.sin(ph)
            yy = max(ys + 8, min(ys + bh - 8, yy))
            pts.append("%.1f,%.1f" % (xx, yy))
        p.append('<polyline points="%s" fill="none" stroke="#60a5fa" '
                 'stroke-width="1.3" stroke-linejoin="round"/>' % " ".join(pts))
    p.append(circle(peak_x, peak_y, 8, fill="none", stroke=POS, sw=2.6))
    p.append(text(peak_x, peak_y - 14, "пік = лінія", size=10, color=POS, bold=True))

    # ── права панель: відновлена лінія ──
    rx = 640
    rbw = 150
    p.append(text(rx + rbw / 2, ys - 10, "пік → лінія", size=10, color=INK, bold=True))
    p.append(rect(rx, ys, rbw, bh, fill="#0f172a", stroke=INK, sw=1.2, rx=8))
    for i, t in enumerate([0.04, 0.18, 0.30, 0.55, 0.70, 0.82]):
        p.append(circle(rx + 16 + t * (rbw - 32), ys + 22 + t * (bh - 44),
                        3.5, fill="#f8fafc", stroke="none", sw=0))
    p.append(line(rx + 12, ys + 18, rx + rbw - 12, ys + bh - 14, color=FIELD, sw=2.4))

    # стрілки між панелями
    p.append(arrow(x1 + bw + 2, ys + bh / 2, mx - 4, ys + bh / 2, color=INK, sw=1.7))
    p.append(arrow(mx + 300 + 2, ys + bh / 2, rx - 4, ys + bh / 2, color=INK, sw=1.7))

    # нижня смуга «чому це сильно»
    p.append(fitbox(30, ys + bh + 28, W - 60, 72,
                    "Сила методу — стійкість до розривів: навіть якщо лінію видно шматками,\n"
                    "голоси справжніх точок усе одно збираються в один пік.\n"
                    "Так само ловлять кола — голосуючи в просторі «центр + радіус».",
                    size=10, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "hough.svg"), W, H, *p,
           title="Перетворення Хафа: голосуванням знайти лінії й кола")


# ── template-toolbox: шаблон, мітка та правило вибору методу ──────────────────
# Ідея: для відомого взірця — або ковзний шаблон (чутливий до масштабу/повороту),
# або надійна мітка (ID + поза); праворуч — карта «який сигнал → який метод».

def fig_template_toolbox():
    W, H = 820, 360
    p = []
    ys = 92
    ph_ = 196

    # ── панель 1: шаблон ковзає → збіг ──
    x = 24
    pw = 232
    p.append(rect(x, ys, pw, ph_, fill="#fbfbfd", stroke=NEG, sw=1.7, rx=12))
    p.append(text(x + pw / 2, ys + 22, "ШАБЛОН ковзає → збіг", size=10.5, color=NEG, bold=True))
    inx, iny, inw, inh = x + 22, ys + 38, pw - 44, 118
    p.append(rect(inx, iny, inw, inh, fill="#10131a", stroke=INK, sw=1.1, rx=8))
    # розсип дрібних об'єктів
    import random
    random.seed(7)
    for _ in range(9):
        rxp = inx + 12 + random.random() * (inw - 36)
        ryp = iny + 12 + random.random() * (inh - 36)
        p.append(rect(rxp, ryp, 11, 11, fill="#334155", stroke="none", sw=0, rx=2))
    # «знайдений» зразок у рамці
    fx, fy = inx + inw / 2 - 20, iny + inh / 2 - 20
    p.append(rect(fx, fy, 40, 40, fill="#e08a1e", stroke="none", sw=0, rx=2))
    p.append('<rect x="%.0f" y="%.0f" width="40" height="40" rx="2" fill="none" '
             'stroke="%s" stroke-width="2"/>' % (fx, fy, FIELD))
    p.append(text(x + pw / 2, ys + ph_ - 14, "найбільша схожість = тут",
                  size=9, color=MUTED))

    # ── панель 2: мітка ArUco/AprilTag ──
    x = 280
    p.append(rect(x, ys, pw, ph_, fill="#fbfbfd", stroke="#d98a00", sw=1.7, rx=12))
    p.append(text(x + pw / 2, ys + 22, "МІТКА (ArUco / AprilTag)", size=10.5, color="#b06b00", bold=True))
    # 5×5 кодова матриця
    cell = 19
    grid = [
        "11111", "10011", "10101", "10001", "11111",
    ]
    g0x = x + pw / 2 - 5 * cell / 2
    g0y = ys + 44
    for r in range(5):
        for c in range(5):
            col = "#000000" if grid[r][c] == "1" else "#ffffff"
            p.append(rect(g0x + c * cell, g0y + r * cell, cell, cell,
                          fill=col, stroke="none", sw=0, rx=0))
    p.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" fill="none" '
             'stroke="%s" stroke-width="1"/>' % (g0x, g0y, 5 * cell, 5 * cell, INK))
    p.append(text(x + pw / 2, ys + ph_ - 14, "дає ID + позу → точна посадка",
                  size=9, color=MUTED))

    # ── панель 3: правило вибору ──
    x = 536
    pw3 = 260
    p.append(rect(x, ys, pw3, ph_, fill=FILL, stroke=INK, sw=1.7, rx=12))
    p.append(text(x + pw3 / 2, ys + 22, "який сигнал — такий метод", size=10.5, color=INK, bold=True))
    rules = [
        "• колір помітний → HSV-пляма",
        "• геометрія → кути / круглість",
        "• лінії, кола → Хаф (стійко)",
        "• відомий взірець → шаблон",
        "• надійна мітка → ArUco / AprilTag",
    ]
    for i, r in enumerate(rules):
        p.append(text(x + 16, ys + 50 + i * 22, r, size=9.4, color=INK, anchor="start"))
    p.append(rect(x + 14, ys + ph_ - 38, pw3 - 28, 24, fill="#eafaf0", stroke=FIELD, sw=1, rx=5))
    p.append(text(x + pw3 / 2, ys + ph_ - 22, "надто різні об'єкти → нейромережі",
                  size=9, color="#15803d", bold=True))

    # підпис унизу
    p.append(text(W / 2, ys + ph_ + 34,
                  "Класичні детектори дешеві, прозорі й без навчання — перший вибір, коли ціль "
                  "чітко задана кольором, формою чи взірцем.",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "template-toolbox.svg"), W, H, *p,
           title="Шаблон, мітка — і коли що брати")


# ── hough-accumulator: реальна теплова карта голосів (ρ, θ) із синусоїдами ─────
# Ідея (для -d.md): кілька колінеарних точок дають синусоїди, що перетинаються
# в одній комірці; саме там акумулятор накопичує найбільше голосів — це пік.

def fig_hough_accumulator():
    W, H = 720, 448
    p = []
    # межі акумулятора на полотні
    ax, ay = 90, 70
    aw, ah = 540, 280
    p.append(text(ax + aw / 2, ay - 26, "акумулятор (θ, ρ): кожна точка межі → синусоїда",
                  size=12, color=INK, bold=True))

    # дискретна сітка комірок
    ncols, nrows = 36, 20            # Δθ = 5°, рядки по ρ
    cw, ch = aw / ncols, ah / nrows

    # справжня пряма має параметри (θ0, ρ0) — на ній лежать колінеарні точки
    th0 = math.radians(55.0)
    # точки на прямій ρ0 = x cosθ0 + y sinθ0 — амплітуда/фаза синусоїди кожної
    pts = []
    for R, ph in [(0.46, 1.15), (0.60, 1.55), (0.74, 1.92), (0.86, 2.28), (0.55, 1.36)]:
        pts.append((R, ph))         # (нормована амплітуда, фаза точки)

    # теплова карта голосів: для кожної комірки рахуємо, скільки синусоїд її «зачепили»
    # будуємо голоси дискретно, як справжній акумулятор
    votes = [[0] * ncols for _ in range(nrows)]
    for R, ph in pts:
        for c in range(ncols):
            th = math.pi * (c + 0.5) / ncols          # θ ∈ [0, π)
            rho = R * math.cos(th - ph)                # ρ(θ) синусоїда, ρ ∈ [-1, 1]
            r = int((rho + 1.0) / 2.0 * nrows)         # у рядок
            if 0 <= r < nrows:
                votes[r][c] += 1

    vmax = max(max(row) for row in votes) or 1
    for r in range(nrows):
        for c in range(ncols):
            v = votes[r][c]
            if v == 0:
                continue
            t = v / vmax
            # від світло-блакитного до гарячого піка
            if v >= vmax:
                col = POS
            else:
                g = int(220 - 120 * t)
                col = "#%02x%02x%02x" % (200 - int(140 * t), g, 250 - int(60 * t))
            p.append(rect(ax + c * cw, ay + r * ch, cw + 0.6, ch + 0.6,
                          fill=col, stroke="none", sw=0, rx=0))

    # тонкі синусоїди поверх (показати, звідки голоси)
    for R, ph in pts:
        seg = []
        for c in range(0, ncols * 3 + 1):
            th = math.pi * c / (ncols * 3)
            rho = R * math.cos(th - ph)
            xx = ax + th / math.pi * aw
            yy = ay + (rho + 1.0) / 2.0 * ah
            yy = max(ay, min(ay + ah, yy))
            seg.append("%.1f,%.1f" % (xx, yy))
        p.append('<polyline points="%s" fill="none" stroke="#1f3a93" '
                 'stroke-width="1.1" stroke-opacity="0.55" stroke-linejoin="round"/>'
                 % " ".join(seg))

    # рамка акумулятора + осі
    p.append(rect(ax, ay, aw, ah, fill="none", stroke=INK, sw=1.4, rx=4))
    p.append(text(ax + aw / 2, ay + ah + 22, "θ  (кут нормалі, 0 → 180°)", size=11, color=MUTED))
    p.append(text(ax - 16, ay + ah / 2, "ρ", size=12, color=MUTED, anchor="middle"))

    # відмітка піка
    pr, pc = None, None
    for r in range(nrows):
        for c in range(ncols):
            if votes[r][c] >= vmax:
                pr, pc = r, c
    if pr is not None:
        px = ax + (pc + 0.5) * cw
        py = ay + (pr + 0.5) * ch
        p.append(circle(px, py, 13, fill="none", stroke=POS, sw=2.4))
        p.append(arrow(px + 70, py - 36, px + 14, py - 8, color=POS, sw=1.8))
        p.append(text(px + 74, py - 42, "пік = (θ*, ρ*) прямої", size=11, color=POS,
                      bold=True, anchor="start"))

    p.append(fitbox(ax, ay + ah + 36, aw, 56,
                    "Синусоїди колінеарних точок перетинаються в одній комірці —\n"
                    "там голосів найбільше (гаряча клітина): це й є шукана пряма.\n"
                    "Розриви й шум окремих точок піка не гасять.",
                    size=10, fill=FILL, stroke=INK, sw=1.2, color=INK))

    render(os.path.join(OUT, "hough-accumulator.svg"), W, H, *p,
           title="Хаф-акумулятор: теплова карта голосів")


# ── circle-hough-slice: зріз 3D-простору (cx, cy) при фіксованому радіусі r ────
# Ідея (для -d.md): для кола кожна точка краю голосує за кільце можливих центрів;
# при фіксованому r кільця перетинаються в істинному центрі — пік у площині cx-cy.

def fig_circle_hough_slice():
    W, H = 720, 430
    p = []

    # ── ліва панель: точки на колі + кільця-голоси можливих центрів ──
    lx, ly, lw, lh = 40, 70, 300, 256
    p.append(text(lx + lw / 2, ly - 24, "точки краю кола → кільця центрів", size=11.5,
                  color=INK, bold=True))
    p.append(rect(lx, ly, lw, lh, fill="#0f172a", stroke=INK, sw=1.2, rx=8))
    ccx, ccy, rr = lx + lw / 2, ly + lh / 2, 78
    # реальні точки краю
    edge = []
    for k in range(8):
        a = 2 * math.pi * k / 8 + 0.2
        ex, ey = ccx + rr * math.cos(a), ccy + rr * math.sin(a)
        edge.append((ex, ey))
    # кожна точка голосує за кільце радіуса rr можливих центрів
    for ex, ey in edge:
        p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#60a5fa" '
                 'stroke-width="1" stroke-opacity="0.5"/>' % (ex, ey, rr))
    for ex, ey in edge:
        p.append(circle(ex, ey, 3.2, fill="#f8fafc", stroke="none", sw=0))
    # справжній центр, де кільця сходяться
    p.append(circle(ccx, ccy, 4.5, fill=POS, stroke=BG, sw=1.2))
    p.append(text(ccx, ccy - 12, "центр", size=9.5, color=POS, bold=True))
    p.append(text(lx + lw / 2, ly + lh + 18, "кожне кільце — радіуса r навколо точки",
                  size=9, color=MUTED))

    # ── права панель: акумулятор-зріз (cx, cy) при r = const, пік у центрі ──
    rx, ry, rw, rh = 392, 70, 290, 256
    p.append(text(rx + rw / 2, ry - 24, "зріз акумулятора (cx, cy) при r = const",
                  size=11.5, color=INK, bold=True))
    nx, ny = 24, 22
    gw, gh = rw / nx, rh / ny
    pcx, pcy = nx // 2, ny // 2
    for r in range(ny):
        for c in range(nx):
            d = math.hypot(c - pcx, r - pcy)
            if d > 7.5:
                continue
            t = max(0.0, 1.0 - d / 7.5)
            if d < 1.2:
                col = POS
            else:
                col = "#%02x%02x%02x" % (210 - int(150 * t), 225 - int(110 * t), 250 - int(40 * t))
            p.append(rect(rx + c * gw, ry + r * gh, gw + 0.6, gh + 0.6,
                          fill=col, stroke="none", sw=0, rx=0))
    p.append(rect(rx, ry, rw, rh, fill="none", stroke=INK, sw=1.4, rx=4))
    ppx, ppy = rx + (pcx + 0.5) * gw, ry + (pcy + 0.5) * gh
    p.append(circle(ppx, ppy, 12, fill="none", stroke=POS, sw=2.4))
    p.append(text(rx + rw / 2, ry + rh + 18, "пік = центр кола (cx*, cy*)",
                  size=9.5, color=POS, bold=True))

    p.append(arrow(lx + lw + 4, ly + lh / 2, rx - 4, ly + lh / 2, color=INK, sw=1.7))

    p.append(fitbox(40, ly + lh + 34, W - 80, 56,
                    "Повний простір кола тривимірний (cx, cy, r); тут — один зріз при сталому r.\n"
                    "Кільця голосів сходяться в істинному центрі — там пік.\n"
                    "Якщо радіус невідомий, додається третя вісь — і простір росте.",
                    size=10, fill=FILL, stroke=INK, sw=1.2, color=INK))

    render(os.path.join(OUT, "circle-hough-slice.svg"), W, H, *p,
           title="Круговий Хаф: зріз простору (cx, cy) при сталому r")


# ── moment-centroid: як моменти дають центр і кут орієнтації плями ─────────────
# Ідея (для -d.md): M10/M00, M01/M00 = центроїд; центральні моменти μ задають
# головну вісь (кут орієнтації) — те, чого габаритна рамка не дає.

def fig_moment_centroid():
    W, H = 700, 410
    p = []
    bx, by, bw, bh = 60, 64, 330, 268
    p.append(text(bx + bw / 2, by - 22, "пляма → центроїд і головна вісь", size=12,
                  color=INK, bold=True))
    p.append(rect(bx, by, bw, bh, fill="#0f172a", stroke=INK, sw=1.2, rx=8))

    # видовжена пляма — повернений еліпс під кутом ang
    cx0, cy0 = bx + bw * 0.45, by + bh * 0.5
    ang = math.radians(28)
    a, b = 86, 40
    pts = []
    for k in range(49):
        t = 2 * math.pi * k / 48
        ex = a * math.cos(t)
        ey = b * math.sin(t)
        xx = cx0 + ex * math.cos(ang) - ey * math.sin(ang)
        yy = cy0 + ex * math.sin(ang) + ey * math.cos(ang)
        pts.append("%.1f,%.1f" % (xx, yy))
    p.append('<polygon points="%s" fill="#f4f6f8" fill-opacity="0.92" stroke="none"/>'
             % " ".join(pts))

    # центроїд (хрест)
    p.append(line(cx0 - 9, cy0, cx0 + 9, cy0, color=POS, sw=2.4))
    p.append(line(cx0, cy0 - 9, cx0, cy0 + 9, color=POS, sw=2.4))
    p.append(circle(cx0, cy0, 3, fill=POS, stroke="none", sw=0))
    p.append(text(cx0 + 12, cy0 - 10, "(cx, cy)", size=10, color=POS, bold=True, anchor="start"))

    # головна вісь орієнтації (уздовж великої півосі)
    hx = a * math.cos(ang)
    hy = a * math.sin(ang)
    p.append(line(cx0 - hx, cy0 - hy, cx0 + hx, cy0 + hy, color=FIELD, sw=2.6, dash="6 4"))
    p.append(text(cx0 - hx - 4, cy0 - hy - 6, "вісь, кут θ", size=10, color=FIELD,
                  bold=True, anchor="end"))

    # формули збоку
    p.append(fitbox(bx + bw + 18, by + 18, W - (bx + bw) - 36, 150,
                    "M00 = Σ 1  (площа)\n"
                    "cx = M10 / M00\n"
                    "cy = M01 / M00\n"
                    "— центральні μ —\n"
                    "θ = ½·atan2(2μ11,\n"
                    "        μ20 − μ02)",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.3, color=INK))

    p.append(fitbox(60, by + bh + 24, W - 120, 56,
                    "Нульовий і перші моменти дають площу й центр.\n"
                    "Центральні моменти другого порядку дають кут орієнтації —\n"
                    "те, чого габаритна рамка не бачить (видовжена ціль має напрям).",
                    size=10, fill=FILL, stroke=INK, sw=1.2, color=INK))

    render(os.path.join(OUT, "moment-centroid.svg"), W, H, *p,
           title="Моменти: центр і кут орієнтації плями")


# ── aruco-pose: осі XYZ, накладені на мітку у кадрі (поза з PnP) ───────────────
# Ідея (для -d.md): знайшовши 4 кути мітки відомого розміру, solvePnP дає позу;
# її показують, проєктуючи 3D-осі (X-червона, Y-зелена, Z-синя) на кадр.

def fig_aruco_pose():
    W, H = 700, 432
    p = []
    fx, fy, fw, fh = 60, 64, 580, 280
    p.append(text(fx + fw / 2, fy - 22, "кадр: мітка знайдена → поза (осі XYZ накладено)",
                  size=12, color=INK, bold=True))
    p.append(rect(fx, fy, fw, fh, fill="#10131a", stroke=INK, sw=1.2, rx=8))

    # мітка у перспективі (трапеція — нахилена площина)
    O = (fx + 215, fy + 175)              # початок осей (кут мітки), origin
    ax_x = (135, -22)                     # вектор уздовж X у кадрі (перспектива)
    ax_y = (44, 92)                       # уздовж Y
    def add(o, v, s=1.0): return (o[0] + v[0] * s, o[1] + v[1] * s)

    c0 = O
    c1 = add(O, ax_x)
    c2 = add(add(O, ax_x), ax_y)
    c3 = add(O, ax_y)
    quad = [c0, c1, c2, c3]
    p.append('<polygon points="%s" fill="#f4f6f8" stroke="%s" stroke-width="2"/>'
             % (" ".join("%.1f,%.1f" % q for q in quad), MUTED))
    # внутрішній 4×4 код мітки
    nx = 4
    for r in range(nx):
        for c in range(nx):
            # білборд-патерн (детермінований)
            on = ((r * 7 + c * 3 + (r % 2)) % 3 == 0)
            if not on:
                continue
            u0, v0 = (c + 0.18) / nx, (r + 0.18) / nx
            u1, v1 = (c + 0.82) / nx, (r + 0.82) / nx
            # білінійна інтерполяція в трапеції
            def bil(u, v):
                top = (c0[0] + (c1[0] - c0[0]) * u, c0[1] + (c1[1] - c0[1]) * u)
                bot = (c3[0] + (c2[0] - c3[0]) * u, c3[1] + (c2[1] - c3[1]) * u)
                return (top[0] + (bot[0] - top[0]) * v, top[1] + (bot[1] - top[1]) * v)
            q = [bil(u0, v0), bil(u1, v0), bil(u1, v1), bil(u0, v1)]
            p.append('<polygon points="%s" fill="#11151c" stroke="none"/>'
                     % " ".join("%.1f,%.1f" % t for t in q))
    # кути мітки — те, що знаходить детектор
    for q in quad:
        p.append(circle(q[0], q[1], 4, fill=POS, stroke=BG, sw=1))

    # 3D-осі з початку: X (червона), Y (зелена), Z (синя, «з площини»)
    axis_len = 1.05
    Xe = add(O, ax_x, axis_len)
    Ye = add(O, ax_y, axis_len)
    # Z виходить із площини мітки — вектор «угору від поверхні» (перспективно)
    Ze = (O[0] - 34, O[1] - 120)
    p.append(arrow(O[0], O[1], Xe[0], Xe[1], color=POS, sw=3))
    p.append(arrow(O[0], O[1], Ye[0], Ye[1], color=FIELD, sw=3))
    p.append(arrow(O[0], O[1], Ze[0], Ze[1], color=NEG, sw=3))
    p.append(text(Xe[0] + 8, Xe[1], "X", size=13, color=POS, bold=True, anchor="start"))
    p.append(text(Ye[0] + 6, Ye[1] + 12, "Y", size=13, color=FIELD, bold=True, anchor="start"))
    p.append(text(Ze[0] - 4, Ze[1] - 6, "Z", size=13, color=NEG, bold=True))

    # права частина кадру — пояснення конвеєра пози
    p.append(fitbox(fx + fw - 196, fy + 16, 178, 120,
                    "4 кути мітки\n+ відомий розмір\n+ калібрування камери\n"
                    "↓ solvePnP\nrvec + tvec\n= поза мітки",
                    size=10.5, fill="#fbfbfd", stroke=INK, sw=1.2, color=INK))

    p.append(fitbox(60, fy + fh + 24, W - 120, 56,
                    "Знайшовши чотири кути мітки відомого розміру, solvePnP відновлює\n"
                    "позу: поворот rvec + зсув tvec.\n"
                    "Її показують, проєктуючи осі XYZ мітки назад у кадр.",
                    size=10, fill=FILL, stroke=INK, sw=1.2, color=INK))

    render(os.path.join(OUT, "aruco-pose.svg"), W, H, *p,
           title="ArUco-поза: осі XYZ, накладені на мітку")


# ── nms-threshold: вплив порога IoU — злиття сусідів на щільній сцені ──────────
# Ідея (для -d.md): низький поріг чистить дублікати на розрідженій сцені, але на
# щільній зливає двох сусідів у одного; високий (або Soft/DIoU) зберігає обидва.

def fig_nms_threshold():
    W, H = 760, 408
    p = []

    def panel(x, title, col_title):
        pw, ph_ = 220, 250
        p.append(rect(x, 64, pw, ph_, fill="#0f172a", stroke=INK, sw=1.2, rx=8))
        p.append(text(x + pw / 2, 56, title, size=11, color=col_title, bold=True))
        return x, 64, pw, ph_

    def obj_boxes(x0, y0, pw, ph_, centers, kept, dim):
        # centers — список (cx, cy) у частках панелі; kept — чи лишилась рамка
        bw, bh = 56, 70
        for i, (fx, fy) in enumerate(centers):
            cx = x0 + fx * pw
            cy = y0 + fy * ph_
            on = kept[i]
            col = FIELD if on else MUTED
            dash = None if on else "4 3"
            sw = 2.6 if on else 1.4
            p.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="3" fill="none" '
                     'stroke="%s" stroke-width="%.1f"%s/>'
                     % (cx - bw/2, cy - bh/2, bw, bh, col, sw,
                        ' stroke-dasharray="%s"' % dash if dash else ''))
            # «голова» об'єкта — кружок усередині (показати, що це справжня ціль)
            p.append(circle(cx, cy - 14, 11, fill="#1e293b", stroke=col, sw=1.6))

    # ── панель 1: розріджена сцена, низький поріг — дублікати прибрано, OK ──
    x0, y0, pw, ph_ = panel(40, "розріджена + низький поріг", FIELD)
    # дві справжні цілі далеко; біля кожної був дубль (прибраний)
    obj_boxes(x0, y0, pw, ph_, [(0.32, 0.40), (0.34, 0.42), (0.70, 0.66), (0.72, 0.68)],
              [True, False, True, False], False)
    p.append(text(x0 + pw / 2, y0 + ph_ + 18, "дублікати прибрано ✓", size=9.5,
                  color="#15803d", bold=True))

    # ── панель 2: щільна сцена, низький поріг — сусіди ЗЛИЛИСЯ, погано ──
    x0, y0, pw, ph_ = panel(280, "щільна + низький поріг", POS)
    obj_boxes(x0, y0, pw, ph_, [(0.40, 0.52), (0.60, 0.52)], [True, False], False)
    p.append(text(x0 + pw / 2, y0 + ph_ + 18, "сусід помилково викинутий ✗", size=9.5,
                  color="#b91c1c", bold=True))

    # ── панель 3: щільна сцена, високий поріг / Soft-NMS — обидва збережено ──
    x0, y0, pw, ph_ = panel(520, "щільна + високий поріг", NEG)
    obj_boxes(x0, y0, pw, ph_, [(0.40, 0.52), (0.60, 0.52)], [True, True], False)
    p.append(text(x0 + pw / 2, y0 + ph_ + 18, "обидва збережено ✓", size=9.5,
                  color="#1d4ed8", bold=True))

    p.append(fitbox(40, 64 + 250 + 30, W - 80, 52,
                    "Зелена суцільна рамка — лишена, сіра пунктирна — викинута NMS.\n"
                    "На щільній сцені низький поріг зливає сусідів (середня);\n"
                    "високий поріг або Soft-/DIoU-NMS їх рятує.",
                    size=10, fill=FILL, stroke=INK, sw=1.2, color=INK))

    render(os.path.join(OUT, "nms-threshold.svg"), W, H, *p,
           title="Вплив порога IoU на результат NMS")


if __name__ == "__main__":
    fig_color_blob()
    fig_shape_contour()
    fig_hough()
    fig_template_toolbox()
    fig_hough_accumulator()
    fig_circle_hough_slice()
    fig_moment_centroid()
    fig_aruco_pose()
    fig_nms_threshold()
    print("OK: figures written to", OUT)
