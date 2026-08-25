# -*- coding: utf-8 -*-
"""Фігури до теми «Сила».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def hatch(x0, y0, x1, y1, step=12, color=MUTED, sw=1.0, dx=9, dy=9):
    """Штрихування — коротенькі діагональні рисочки вздовж лінії (лід/стіна)."""
    out = [line(x0, y0, x1, y1, color=color, sw=1.6)]
    n = int(math.hypot(x1 - x0, y1 - y0) // step)
    if n <= 0:
        return "".join(out)
    ux, uy = (x1 - x0) / (n * step), (y1 - y0) / (n * step)
    for i in range(n + 1):
        px, py = x0 + ux * step * i, y0 + uy * step * i
        out.append(line(px, py, px - dx, py + dy, color=color, sw=sw))
    return "".join(out)


def coil_h(x0, x1, y, n, amp):
    """Горизонтальна пружина-зигзаг від x0 до x1."""
    pts = [(x0, y)]
    seg = (x1 - x0) / (2 * n)
    for i in range(1, 2 * n):
        pts.append((x0 + seg * i, y + (amp if i % 2 else -amp)))
    pts.append((x1, y))
    return polyline(pts, color=INK, sw=2.2)


def coil_v(x, y0, y1, n, amp):
    """Вертикальна пружина-зигзаг від y0 (верх) до y1 (низ)."""
    pts = [(x, y0)]
    seg = (y1 - y0) / (2 * n)
    for i in range(1, 2 * n):
        pts.append((x + (amp if i % 2 else -amp), y0 + seg * i))
    pts.append((x, y1))
    return polyline(pts, color=INK, sw=2.2)


# ── Фігура 1: будова сили як вектора + складання (3-4-5) ──────────────────────
def fig_force_vector():
    W, H = 900, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Сила задана величиною, напрямом і точкою прикладання",
                  size=17, bold=True))
    f.append(line(468, 74, 468, 430, color=MUTED, sw=1.2, dash="4 6"))

    # ── ліва панель: анатомія однієї сили ──
    f.append(text(230, 72, "Одна сила", size=14, bold=True, color=MUTED))
    # тіло-блок
    f.append(rect(120, 300, 120, 74, fill="#eef2fb", stroke=INK, sw=2, rx=8))
    f.append(text(180, 343, "тіло", size=13, color=MUTED))
    # точка прикладання + стрілка сили вгору-праворуч
    P = (180, 300)
    Tip = (345, 138)
    f.append(arrow(P[0], P[1], Tip[0], Tip[1], color=POS, sw=3.4))
    f.append(circle(P[0], P[1], 5.5, fill=POS, stroke=BG, sw=1.5))
    f.append(text(Tip[0] + 14, Tip[1] - 2, "F", size=18, bold=True, color=POS, anchor="start"))
    # підписи трьох складників (рознесені, лініями-поводирями)
    f.append(text(70, 300, "точка", size=12, color=INK, anchor="middle"))
    f.append(text(70, 316, "прикладання", size=12, color=INK, anchor="middle"))
    f.append(line(108, 305, P[0] - 8, P[1], color=MUTED, sw=1.0))
    mid = ((P[0] + Tip[0]) / 2, (P[1] + Tip[1]) / 2)
    f.append(text(mid[0] - 96, mid[1] - 6, "напрям", size=12, color=INK, anchor="start"))
    f.append(line(mid[0] - 44, mid[1] - 4, mid[0] - 8, mid[1] + 6, color=MUTED, sw=1.0))
    f.append(text(300, 250, "величина ∝", size=12, color=INK, anchor="start"))
    f.append(text(300, 266, "довжина стрілки", size=12, color=INK, anchor="start"))

    # ── права панель: складання 3-4-5 ──
    f.append(text(690, 72, "Складання сил", size=14, bold=True, color=MUTED))
    O = (560, 372)
    sc = 58.0                              # px на 1 Н
    E = (O[0] + 3 * sc, O[1])              # 3 Н на схід
    N = (O[0], O[1] - 4 * sc)              # 4 Н на північ
    Rt = (O[0] + 3 * sc, O[1] - 4 * sc)    # кут прямокутника → вістря рівнодійної
    # добудова прямокутника (пунктир)
    f.append(line(E[0], E[1], Rt[0], Rt[1], color=MUTED, sw=1.3, dash="5 5"))
    f.append(line(N[0], N[1], Rt[0], Rt[1], color=MUTED, sw=1.3, dash="5 5"))
    # дві прикладені сили
    f.append(arrow(O[0], O[1], E[0], E[1], color=POS, sw=3.2))
    f.append(text((O[0] + E[0]) / 2, O[1] + 26, "3 Н", size=14, bold=True, color=POS))
    f.append(arrow(O[0], O[1], N[0], N[1], color=NEG, sw=3.2))
    f.append(text(O[0] - 16, (O[1] + N[1]) / 2, "4 Н", size=14, bold=True, color=NEG, anchor="end"))
    # рівнодійна
    f.append(arrow(O[0], O[1], Rt[0], Rt[1], color=FIELD, sw=3.8))
    f.append(text(Rt[0] + 12, Rt[1] + 2, "5 Н", size=15, bold=True, color=FIELD, anchor="start"))
    f.append(text(Rt[0] + 12, Rt[1] + 22, "рівнодійна", size=12, color=FIELD, anchor="start"))
    f.append(circle(O[0], O[1], 4.5, fill=INK, stroke=BG, sw=1.2))
    # кут θ
    f.append(text(O[0] + 40, O[1] - 20, "θ ≈ 53°", size=12, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "force-vector.svg"), W, H, *f)


# ── Фігура 2: два прояви сили — рух або деформація ────────────────────────────
def fig_two_effects():
    W, H = 900, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Силу видно лише по тому, що вона робить",
                  size=17, bold=True))

    pw, ptop, ph = 400, 60, 330
    lx, rx = 34, 466
    f.append(rect(lx, ptop, pw, ph, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=10))
    f.append(rect(rx, ptop, pw, ph, fill="#fdf0ee", stroke=POS, sw=1.6, rx=10))
    f.append(text(lx + pw / 2, ptop + 28, "Вільне тіло → міняє РУХ", size=15, bold=True, color=FIELD))
    f.append(text(rx + pw / 2, ptop + 28, "Затиснуте тіло → ДЕФОРМАЦІЯ", size=15, bold=True, color=POS))

    # ── ліва сцена: шайба на льоду розганяється ──
    gy = 250
    f.append(hatch(lx + 34, gy, lx + pw - 34, gy, step=20, color=NEG))
    f.append(text(lx + pw - 40, gy + 30, "гладкий лід", size=11, color=NEG, anchor="end"))
    bl = (lx + 150, gy - 40, 66, 40)
    f.append(rect(bl[0], bl[1], bl[2], bl[3], fill="#ffffff", stroke=INK, sw=2, rx=5))
    f.append(arrow(lx + 66, gy - 20, bl[0] - 6, gy - 20, color=POS, sw=3.2))
    f.append(text(lx + 58, gy - 26, "F", size=15, bold=True, color=POS, anchor="end"))
    f.append(arrow(bl[0] + bl[2] + 8, gy - 20, bl[0] + bl[2] + 96, gy - 20, color=FIELD, sw=3.0))
    f.append(text(bl[0] + bl[2] + 104, gy - 15, "v", size=15, bold=True, color=FIELD, anchor="start"))
    f.append(text(lx + pw / 2, gy + 66, "розганяється — рух зростає", size=13, color=INK))

    # ── права сцена: пружина стискається біля стіни ──
    wallx = rx + pw - 40
    f.append(hatch(wallx, gy - 92, wallx, gy + 22, step=16, color=MUTED, dx=-11, dy=8))
    f.append(line(wallx, gy - 92, wallx, gy + 22, color=INK, sw=2.4))
    plate = wallx - 150
    f.append(coil_h(plate, wallx, gy - 36, 6, 15))
    f.append(rect(plate - 12, gy - 62, 12, 52, fill="#eef2fb", stroke=INK, sw=2, rx=3))  # пластина
    f.append(arrow(plate - 96, gy - 36, plate - 18, gy - 36, color=POS, sw=3.2))
    f.append(text(plate - 104, gy - 42, "F", size=15, bold=True, color=POS, anchor="end"))
    # природна довжина (пунктир) + Δx
    natx = plate - 34
    f.append(line(natx, gy - 70, natx, gy + 6, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(natx, gy + 2, plate - 12, gy + 2, color=INK, sw=1.2))
    f.append(text((natx + plate - 12) / 2 - 2, gy + 18, "Δx", size=12, italic=True, color=INK))
    f.append(text(rx + pw / 2, gy + 66, "стискається — форма зростає", size=13, color=INK))

    return render(os.path.join(IMG, "two-effects.svg"), W, H, *f)


# ── Фігура 3: побутові сили = електромагнетизм; чотири взаємодії ──────────────
def fig_fundamental_forces():
    W, H = 900, 620
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Усе розмаїття сил зводиться до чотирьох взаємодій",
                  size=17, bold=True))

    # ── верх: побутові сили → електромагнітна ──
    chips = ["тертя", "натяг", "опора", "пружність", "поштовх м'яза"]
    cy = 84
    box = (270, 168, 360, 46)            # ЕМ-бокс (центр 450)
    for i, c in enumerate(chips):
        cx = 90 + i * 180
        b, w0, h0 = textbox(cx, cy, c, size=13, pad=9, fill="#fdf0ee", stroke=POS, sw=1.3)
        f.append(b)
        f.append(line(cx, cy + 16, 450 + (cx - 450) * 0.12, box[1] - 4, color=MUTED, sw=1.0))
    f.append(arrow(450, box[1] - 30, 450, box[1] - 4, color=POS, sw=2.4))
    f.append(fitbox(box[0], box[1], box[2], box[3],
                    "усе це — Електромагнітна взаємодія (на рівні атомів)",
                    size=14, fill="#fdecea", stroke=POS, sw=2.0, bold=True, color=POS))

    f.append(text(W / 2, 258, "а в самій основі природи сил лише чотири:", size=14, color=MUTED))

    # ── низ: чотири фундаментальні взаємодії (картки) ──
    cards = [
        ("Гравітаційна", "радіус: ∞", "сила ~ 10⁻³⁸", "притягує все,\nщо має масу", MUTED),
        ("Електромагнітна", "радіус: ∞", "сила ~ 10⁻²", "заряди, струми,\nсвітло, «дотик»", POS),
        ("Сильна", "радіус ~ 10⁻¹⁵ м", "сила ~ 1", "тримає\nатомне ядро", INK),
        ("Слабка", "радіус ~ 10⁻¹⁸ м", "сила ~ 10⁻⁶", "деякі\nрадіорозпади", NEG),
    ]
    cw, gap, y0, ch = 200, 18, 290, 250
    x0 = (W - (4 * cw + 3 * gap)) / 2
    for i, (name, rng, stg, note, col) in enumerate(cards):
        cx = x0 + i * (cw + gap)
        hl = (col == POS)
        f.append(rect(cx, y0, cw, ch, fill="#fdecea" if hl else FILL,
                      stroke=col, sw=2.4 if hl else 1.6, rx=10))
        f.append(text(cx + cw / 2, y0 + 34, name, size=15, bold=True, color=col))
        f.append(line(cx + 16, y0 + 48, cx + cw - 16, y0 + 48, color=col, sw=1.0))
        f.append(text(cx + cw / 2, y0 + 78, rng, size=13, color=INK))
        f.append(text(cx + cw / 2, y0 + 108, stg, size=13, bold=True, color=col))
        f.append(mtext(cx + cw / 2, y0 + 150, note, size=12.5, color=MUTED, lh=1.25))

    b, w, h = textbox(W / 2, y0 + ch + 42,
                      "гравітація мізерно слабка — та єдина завжди тільки додається й сягає без меж, тож керує зорями",
                      size=13, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "fundamental-forces.svg"), W, H, *f)


# ── Фігура 4: закон Гука — розтяг ∝ сила ──────────────────────────────────────
def fig_spring_scale():
    W, H = 900, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Закон Гука: пружина розтягується пропорційно силі",
                  size=17, bold=True))
    f.append(line(452, 70, 452, 440, color=MUTED, sw=1.2, dash="4 6"))

    # ── ліва панель: три пружини під 0, F, 2F ──
    ceil_y = 84
    f.append(hatch(70, ceil_y, 400, ceil_y, step=18, color=MUTED, dx=-9, dy=-9))
    f.append(line(70, ceil_y, 400, ceil_y, color=INK, sw=2.4))
    nat = 96                                # природна довжина (px)
    ext = 58                                # приріст на кожен вантаж
    cols = [(130, 0, "0", nat),
            (235, 1, "F", nat + ext),
            (340, 2, "2F", nat + 2 * ext)]
    base = ceil_y + nat
    f.append(line(96, base, 374, base, color=NEG, sw=1.2, dash="5 5"))
    f.append(text(384, base + 4, "природна", size=10, color=NEG, anchor="start"))
    f.append(text(384, base + 17, "довжина", size=10, color=NEG, anchor="start"))
    for cx, k, lbl, length in cols:
        bot = ceil_y + length
        f.append(coil_v(cx, ceil_y, bot, 7, 11))
        if k > 0:
            f.append(rect(cx - 20, bot, 40, 30 + 12 * (k - 1), fill="#eef2fb", stroke=INK, sw=2, rx=4))
            f.append(text(cx, bot + 20 + 6 * (k - 1), lbl, size=14, bold=True, color=NEG))
            # приріст довжини
            f.append(line(cx + 26, base, cx + 26, bot, color=FIELD, sw=2.0))
            f.append(text(cx + 32, (base + bot) / 2 + 4, "%dx" % k if k > 1 else "x",
                          size=12, bold=True, color=FIELD, anchor="start"))
        else:
            f.append(text(cx, bot + 16, "без ваги", size=11, color=MUTED))

    # ── права панель: графік F(x) — пряма через нуль ──
    O = (540, 360)
    xr, yt = 850, 110
    f.append(arrow(O[0], O[1], xr, O[1], color=INK, sw=1.8))
    f.append(arrow(O[0], O[1], O[0], yt, color=INK, sw=1.8))
    f.append(text(xr - 2, O[1] + 26, "розтяг  x", size=13, color=MUTED, anchor="end"))
    f.append(text(O[0] - 10, yt + 2, "сила  F", size=13, color=MUTED, anchor="end"))
    # пряма
    Pend = (820, 140)
    f.append(line(O[0], O[1], Pend[0], Pend[1], color=NEG, sw=3.0))
    # дві точки з проекціями
    def pt(fr, lbl):
        px = O[0] + (Pend[0] - O[0]) * fr
        py = O[1] + (Pend[1] - O[1]) * fr
        f.append(line(px, O[1], px, py, color=MUTED, sw=1.0, dash="4 4"))
        f.append(line(O[0], py, px, py, color=MUTED, sw=1.0, dash="4 4"))
        f.append(circle(px, py, 4.5, fill=NEG, stroke=BG, sw=1.5))
        f.append(text(px, O[1] + 18, lbl, size=12, color=MUTED))
        return px, py
    pt(0.5, "x")
    pt(1.0, "2x")
    # підпис нахилу — в чистому полі над прямою (ліворуч-угорі)
    f.append(text(582, 166, "нахил = k", size=13, bold=True, color=NEG, anchor="start"))
    f.append(text(582, 185, "(жорсткість)", size=12, color=MUTED, anchor="start"))

    b, w, h = textbox(720, 118, "F = k · x", size=16, pad=11,
                      fill="#eef2fb", stroke=NEG, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "spring-scale.svg"), W, H, *f)


# ── Фігура 5 (hist): одне слово vis → три сучасні величини ────────────────────
def fig_concept_split():
    W, H = 960, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Одне слово «сила» (лат. vis) ховало три різні величини",
                  size=17, bold=True))

    # ── лівий вузол: латинське слово ──
    lx, ly = 150, 300
    f.append(rect(lx - 92, ly - 52, 184, 104, fill="#eef2fb", stroke=INK, sw=2.2, rx=12))
    f.append(text(lx, ly - 6, "vis", size=36, bold=True, color=INK))
    f.append(text(lx, ly + 24, "лат. «сила, міць»", size=12.5, color=MUTED))
    f.append(text(lx, ly + 84, "двадцять століть —", size=12.5, color=MUTED))
    f.append(text(lx, ly + 101, "одне слово на трьох", size=12.5, color=MUTED))

    # ── три цільові поняття ──
    bx, bw = 560, 356          # ліва межа й ширина карток
    rows = [
        (150, NEG,   "кількість руху", "p = m · v",
         "Декарт → Гюйгенс", "змінює  сила × ЧАС"),
        (315, POS,   "сила", "F = m · a",
         "Ньютон → Мах", "тепер: похідний запис"),
        (480, FIELD, "жива сила → енергія", "½ · m · v²",
         "Ляйбніц → Коріоліс", "змінює  сила × ШЛЯХ"),
    ]
    src = (lx + 92, ly)        # точка розгалуження — правий край лівого вузла
    for cy, col, name, formula, who, role in rows:
        # промінь від спільної точки до картки (кольором гілки)
        f.append(line(src[0], src[1], bx - 6, cy, color=col, sw=3.4))
        f.append(circle(bx - 6, cy, 4.5, fill=col, stroke=BG, sw=1.4))
        # картка
        bh = 120
        hot = {POS: "#fdecea", NEG: "#eaf0fd", FIELD: "#eaf7ee"}[col]
        f.append(rect(bx, cy - bh / 2, bw, bh, fill=hot, stroke=col, sw=2.0, rx=11))
        f.append(text(bx + 20, cy - 30, name, size=15, bold=True, color=col, anchor="start"))
        f.append(text(bx + bw - 20, cy - 28, formula, size=17, bold=True, color=INK, anchor="end"))
        f.append(line(bx + 18, cy - 12, bx + bw - 18, cy - 12, color=col, sw=1.0))
        f.append(text(bx + 20, cy + 12, who, size=13, color=INK, anchor="start"))
        f.append(text(bx + 20, cy + 36, role, size=12, italic=True, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "concept-split.svg"), W, H, *f)


# ── Фігура 6 (hist): дослід с-Ґравесанде — глибина ямки ∝ v² ───────────────────
def fig_vis_viva_depth():
    W, H = 900, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Дослід с-Ґравесанде: подвій швидкість — учетверо глибша ямка",
                  size=17, bold=True))

    y0 = 250                                  # рівень поверхні глини
    cols = [(170, 1.0, "v", "×1", 22),
            (450, 2.0, "2v", "×4", 88),
            (730, 3.0, "3v", "×9", 198)]
    bw, bbot = 176, 470                       # ширина глиняного блоку, низ
    for cx, sp, vlbl, dlbl, d in cols:
        # глиняний блок
        f.append(rect(cx - bw / 2, y0, bw, bbot - y0, fill="#e9dcc4", stroke="#a9946b", sw=1.6, rx=6))
        # поверхня глини (штрихування)
        f.append(hatch(cx - bw / 2, y0, cx + bw / 2, y0, step=16, color="#a9946b", dx=-8, dy=-8))
        # напис зсунуто ліворуч від осьової лінії ямки, щоб не лягав на пунктирний слід
        f.append(text(cx - 50, y0 + (bbot - y0) / 2 + 44, "глина", size=12, color="#8a744d"))

        # падаюча кулька + стрілка швидкості (довша = прудкіша)
        alen = 46 + sp * 26
        ax = cx
        f.append(arrow(ax, y0 - 40 - alen, ax, y0 - 46, color=POS, sw=3.2))
        f.append(text(ax + 16, y0 - 40 - alen / 2, vlbl, size=15, bold=True, color=POS, anchor="start"))
        f.append(circle(ax, y0 - 30, 15, fill="#c9a24a", stroke=INK, sw=1.8))

        # ямка: пунктирний слід від поверхні + кулька на дні
        f.append(line(cx, y0, cx, y0 + d, color=MUTED, sw=1.2, dash="4 4"))
        f.append(circle(cx, y0 + d - 2, 15, fill="#c9a24a", stroke=INK, sw=1.8))

        # брекет глибини праворуч від ямки
        gx = cx + 44
        f.append(line(gx, y0, gx, y0 + d, color=FIELD, sw=2.2))
        f.append(line(gx - 5, y0, gx + 5, y0, color=FIELD, sw=2.0))
        f.append(line(gx - 5, y0 + d, gx + 5, y0 + d, color=FIELD, sw=2.0))
        f.append(text(gx + 10, y0 + d / 2 + 5, dlbl, size=15, bold=True, color=FIELD, anchor="start"))
        f.append(text(cx, bbot + 26, "глибина " + dlbl, size=12.5, color=INK))

    b, w, h = textbox(W / 2, H - 26,
                      "глибина ∝ v²  (1 : 4 : 9) — отже m·v²;   якби m·v, глибини йшли б 1 : 2 : 3",
                      size=13, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "vis-viva-depth.svg"), W, H, *f)


def arcpoly(cx, cy, r, a0, a1, color=MUTED, sw=1.4, n=14):
    """Дужка кута — полілінія від a0 до a1 (градуси, y-угору)."""
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    return polyline(pts, color=color, sw=sw)


def polygon(pts, fill=FILL, stroke=INK, sw=2.0):
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (p, fill, stroke, sw))


# ── Фігура (вставка math): діаграма вільного тіла — вивіска на двох тросах ─────
def fig_fbd_signboard():
    W, H = 940, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Вирізати тіло — і розкласти сили на осі", size=17, bold=True))
    f.append(line(470, 58, 470, 490, color=MUTED, sw=1.2, dash="4 6"))

    # ── ліва панель: реальна сцена ──
    f.append(text(235, 64, "Сцена: вивіска на двох тросах", size=14, bold=True, color=MUTED))
    R = (250, 300)
    aL, aR, Lc = math.radians(30), math.radians(45), 150
    AL = (R[0] - Lc * math.cos(aL), R[1] - Lc * math.sin(aL))
    AR = (R[0] + Lc * math.cos(aR), R[1] - Lc * math.sin(aR))
    f.append(line(R[0] - 132, R[1], R[0] + 128, R[1], color=MUTED, sw=1.0, dash="4 5"))
    f.append(line(R[0], R[1], AL[0], AL[1], color=INK, sw=2.6))
    f.append(line(R[0], R[1], AR[0], AR[1], color=INK, sw=2.6))
    for A in (AL, AR):
        f.append(rect(A[0] - 10, A[1] - 10, 20, 10, fill=INK, stroke=INK, sw=1, rx=2))
    f.append(arcpoly(R[0], R[1], 46, 150, 180))
    f.append(arcpoly(R[0], R[1], 46, 0, 45))
    f.append(text(188, 286, "30°", size=12, color=INK))
    f.append(text(308, 280, "45°", size=12, color=INK))
    f.append(text(126, 264, "трос 1", size=11, color=NEG))
    f.append(text(340, 222, "трос 2", size=11, color=POS))
    f.append(circle(R[0], R[1], 6, fill=INK, stroke=BG, sw=1.5))
    f.append(line(R[0], R[1], R[0], R[1] + 46, color=INK, sw=2))
    f.append(rect(R[0] - 66, R[1] + 46, 132, 48, fill="#eef2fb", stroke=INK, sw=2, rx=6))
    f.append(mtext(R[0], R[1] + 66, ["ВИВІСКА", "W = 200 Н"], size=13, color=INK, lh=1.35, bold=True))

    # ── права панель: вільне тіло кільця ──
    f.append(text(700, 64, "Вільне тіло: сили та осі", size=14, bold=True, color=MUTED))
    O = (655, 305)
    f.append(arrow(548, O[1], 838, O[1], color=INK, sw=1.6))
    f.append(arrow(O[0], O[1], O[0], 168, color=INK, sw=1.6))
    f.append(text(832, O[1] + 22, "x", size=13, color=MUTED, anchor="end", italic=True))
    f.append(text(O[0] + 16, 176, "y", size=13, color=MUTED, anchor="start", italic=True))
    TL = (O[0] + Lc * math.cos(math.radians(150)), O[1] - Lc * math.sin(math.radians(150)))
    TR = (O[0] + Lc * math.cos(math.radians(45)), O[1] - Lc * math.sin(math.radians(45)))
    Wt = (O[0], O[1] + 104)
    for P in (TL, TR):
        f.append(line(P[0], P[1], P[0], O[1], color=MUTED, sw=1.0, dash="4 4"))
        f.append(line(P[0], P[1], O[0], P[1], color=MUTED, sw=1.0, dash="4 4"))
    f.append(arrow(O[0], O[1], TL[0], TL[1], color=NEG, sw=3.4))
    f.append(arrow(O[0], O[1], TR[0], TR[1], color=POS, sw=3.4))
    f.append(arrow(O[0], O[1], Wt[0], Wt[1], color=INK, sw=3.4))
    f.append(text(TL[0] - 12, TL[1] - 4, "T₁", size=16, bold=True, color=NEG, anchor="end"))
    f.append(text(TR[0] + 12, TR[1] - 2, "T₂", size=16, bold=True, color=POS, anchor="start"))
    f.append(text(Wt[0] + 14, Wt[1] - 8, "W", size=16, bold=True, color=INK, anchor="start"))
    f.append(arcpoly(O[0], O[1], 46, 150, 180))
    f.append(arcpoly(O[0], O[1], 46, 0, 45))
    f.append(text(O[0] - 66, O[1] - 14, "30°", size=12, color=INK))
    f.append(text(O[0] + 58, O[1] - 22, "45°", size=12, color=INK))
    f.append(circle(O[0], O[1], 5, fill=INK, stroke=BG, sw=1.4))
    b, w, h = textbox(700, 462,
                      ["ΣFx:  −T₁·cos30° + T₂·cos45° = 0",
                       "ΣFy:   T₁·sin30° + T₂·sin45° − W = 0"],
                      size=13, pad=11, fill="#f4f6f8", stroke=MUTED, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "fbd-signboard.svg"), W, H, *f)


# ── Фігура (вставка math): брусок на похилій площині, нахилені осі ────────────
def fig_fbd_incline():
    W, H = 940, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Нахили осі за схилом — і розкладати доводиться лише вагу", size=16, bold=True))
    B, Cc, T = (170, 380), (720, 380), (720, 150)
    beta = math.atan2(B[1] - T[1], T[0] - B[0])
    f.append(polygon([B, T, Cc], fill="#eef6ef", stroke=INK, sw=2.2))
    f.append(hatch(B[0] - 6, 382, Cc[0] + 6, 382, step=16, color=MUTED, dx=-9, dy=9))
    f.append(arcpoly(B[0], B[1], 62, 0, math.degrees(beta)))
    f.append(text(B[0] + 82, B[1] - 12, "β", size=15, italic=True, color=INK))
    s = (math.cos(beta), -math.sin(beta))     # уздовж схилу вгору
    n = (-math.sin(beta), -math.cos(beta))    # нормаль назовні
    mid = ((B[0] + T[0]) / 2, (B[1] + T[1]) / 2)
    C = (mid[0] + n[0] * 24, mid[1] + n[1] * 24)
    hw, ht = 36, 21
    corners = [(C[0] + s[0] * hw + n[0] * ht, C[1] + s[1] * hw + n[1] * ht),
               (C[0] + s[0] * hw - n[0] * ht, C[1] + s[1] * hw - n[1] * ht),
               (C[0] - s[0] * hw - n[0] * ht, C[1] - s[1] * hw - n[1] * ht),
               (C[0] - s[0] * hw + n[0] * ht, C[1] - s[1] * hw + n[1] * ht)]
    f.append(polygon(corners, fill="#eef2fb", stroke=INK, sw=2))
    # нахилені осі
    f.append(line(C[0] - s[0] * 58, C[1] - s[1] * 58, C[0] + s[0] * 150, C[1] + s[1] * 150,
                  color=MUTED, sw=1.2, dash="5 5"))
    f.append(line(C[0] - n[0] * 74, C[1] - n[1] * 74, C[0] + n[0] * 20, C[1] + n[1] * 20,
                  color=MUTED, sw=1.2, dash="5 5"))
    f.append(text(C[0] + s[0] * 162, C[1] + s[1] * 162 + 6, "x′ (схил)", size=12, color=MUTED,
                  anchor="start", italic=True))
    # розклад ваги (пунктир)
    Lw = 132
    Wt = (C[0], C[1] + Lw)
    Wpar = (C[0] - s[0] * Lw * math.sin(beta), C[1] - s[1] * Lw * math.sin(beta))
    Wperp = (C[0] - n[0] * Lw * math.cos(beta), C[1] - n[1] * Lw * math.cos(beta))
    f.append(line(Wpar[0], Wpar[1], Wt[0], Wt[1], color=MUTED, sw=1.1, dash="4 4"))
    f.append(line(Wperp[0], Wperp[1], Wt[0], Wt[1], color=MUTED, sw=1.1, dash="4 4"))
    f.append(arrow(C[0], C[1], Wpar[0], Wpar[1], color=MUTED, sw=1.9))
    f.append(arrow(C[0], C[1], Wperp[0], Wperp[1], color=MUTED, sw=1.9))
    f.append(text(Wpar[0] - 8, Wpar[1] - 4, "W·sinβ", size=12, color=MUTED, anchor="end"))
    f.append(text(Wperp[0] + 8, Wperp[1] + 6, "W·cosβ", size=12, color=MUTED, anchor="start"))
    # реальні сили
    f.append(arrow(C[0], C[1], Wt[0], Wt[1], color=INK, sw=3.4))
    f.append(text(Wt[0] + 20, Wt[1] - 44, "W", size=16, bold=True, color=INK, anchor="start"))
    Nn = (C[0] + n[0] * 120, C[1] + n[1] * 120)
    f.append(arrow(C[0], C[1], Nn[0], Nn[1], color=NEG, sw=3.4))
    f.append(text(Nn[0] - 10, Nn[1] - 6, "N", size=16, bold=True, color=NEG, anchor="end"))
    Ff = (C[0] + s[0] * 95, C[1] + s[1] * 95)
    f.append(arrow(C[0], C[1], Ff[0], Ff[1], color=FIELD, sw=3.4))
    f.append(text(Ff[0] + 10, Ff[1] - 6, "f", size=16, bold=True, italic=True, color=FIELD, anchor="start"))
    # рівняння
    b, w, h = textbox(830, 250,
                      ["уздовж схилу (x′):", "   f − W·sinβ = 0", "   → f = W·sinβ",
                       "поперек (y′):", "   N − W·cosβ = 0", "   → N = W·cosβ",
                       "стоїть, поки", "   tan β ≤ μₛ"],
                      size=13, pad=12, fill="#f4f6f8", stroke=MUTED, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "fbd-incline.svg"), W, H, *f)


# ── Фігура (вставка math): вибух натягу пологих тросів ────────────────────────
def fig_tension_blowup():
    W, H = 860, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Пологі троси — велетенський натяг", size=17, bold=True))
    O = (120, 380)
    x1, ytop, ycap = 800, 96, 4.0
    sx = (x1 - O[0]) / 90.0
    sy = (O[1] - ytop) / ycap

    def X(th):
        return O[0] + th * sx

    def Y(tw):
        return O[1] - tw * sy

    f.append(arrow(O[0], O[1], x1 + 8, O[1], color=INK, sw=1.6))
    f.append(arrow(O[0], O[1], O[0], ytop - 6, color=INK, sw=1.6))
    f.append(text(x1 - 4, O[1] + 30, "кут θ, симетричний підвіс", size=12, color=MUTED, anchor="end"))
    f.append(text(O[0] - 8, ytop + 4, "T / W", size=13, color=MUTED, anchor="end"))
    for tw in (0.5, 1, 2, 3, 4):
        yy = Y(tw)
        f.append(line(O[0] - 5, yy, O[0], yy, color=INK, sw=1.2))
        f.append(text(O[0] - 11, yy + 4, ("%g" % tw), size=11, color=MUTED, anchor="end"))
    for th in (0, 30, 45, 60, 90):
        xx = X(th)
        f.append(line(xx, O[1], xx, O[1] + 5, color=INK, sw=1.2))
        f.append(text(xx, O[1] + 20, (("%d°" % th) if th else "0"), size=11, color=MUTED))
    f.append(line(O[0], Y(1), x1, Y(1), color=MUTED, sw=1.2, dash="5 5"))
    f.append(text(x1 - 2, Y(1) - 6, "T = W", size=11, color=MUTED, anchor="end"))
    # крива 1/(2 sinθ)
    pts, t = [], math.degrees(math.asin(1 / (2 * ycap)))
    while t <= 90.0001:
        tw = 1 / (2 * math.sin(math.radians(t)))
        if tw <= ycap + 1e-9:
            pts.append((X(t), Y(tw)))
        t += 1
    f.append(polyline(pts, color=POS, sw=3.0))
    for th0 in (30, 15, 90):
        tw = 1 / (2 * math.sin(math.radians(th0)))
        f.append(circle(X(th0), Y(tw), 4.5, fill=POS, stroke=BG, sw=1.5))
    f.append(text(360, Y(1) - 14, "θ=30°: T=W", size=12, color=INK, anchor="start"))
    f.append(text(252, 246, "θ=15°: T≈1.9W", size=12, color=INK, anchor="start"))
    f.append(mtext(724, Y(0.5) - 22, ["θ=90°:", "T=W/2"], size=12, color=INK, lh=1.25))
    f.append(text(196, 128, "θ → 0:  натяг → ∞", size=14, bold=True, color=POS, anchor="start"))
    b, w, h = textbox(648, 172, ["знаменник sin(α+β) → 0", "⇒ визначник → 0  ⇒  T → ∞"],
                      size=12, pad=10, fill="#fdecea", stroke=POS, sw=1.2)
    f.append(b)
    return render(os.path.join(IMG, "tension-blowup.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_force_vector(), fig_two_effects(),
          fig_fundamental_forces(), fig_spring_scale(),
          fig_concept_split(), fig_vis_viva_depth(),
          fig_fbd_signboard(), fig_fbd_incline(), fig_tension_blowup()]
    print("written:")
    for p in ps:
        print("  ", p)
