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


if __name__ == "__main__":
    fig_color_blob()
    fig_shape_contour()
    fig_hough()
    fig_template_toolbox()
    print("OK: figures written to", OUT)
