# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def ymerc(phi_deg):
    return math.log(math.tan(math.pi / 4 + math.radians(phi_deg) / 2))


# ───────────────────────────────────────────────────────────────────────────
def conformal_stretch():
    """Три панелі: глобус → випрямлені меридіани → Меркатор.
    Показує, ЧОМУ вертикаль мусить розтягуватися рівно так само, як горизонталь."""
    W, H = 900, 470
    frags = [text(W / 2, 28, "Чому в Меркатора вертикаль розтягнута рівно як горизонталь",
                  size=16, bold=True)]

    PW, PH = 250, 250        # розмір панелі
    TOP = 68                 # верх панелей
    XS = (30, 325, 620)      # ліві краї трьох панелей
    LATS = (0, 15, 30, 45, 60, 75)
    LAM = (-3, -2, -1, 0, 1, 2, 3)   # умовні меридіани
    HALF = PW * 0.40         # піврозмах екватора в px
    YMAX = ymerc(75)

    def panel_frame(x, title):
        out = [rect(x, TOP, PW, PH, fill="#fbfcfd", stroke=MUTED, sw=1.4)]
        out.append(text(x + PW / 2, TOP - 12, title, size=13, bold=True))
        return out

    # координати всередині панелі
    def y_lin(x0, phi):                      # рівномірна широта (глобус і «сира» карта)
        return TOP + PH - 18 - phi / 90.0 * (PH - 40)

    def y_mer(x0, phi):                      # меркаторова широта
        return TOP + PH - 18 - ymerc(phi) / (YMAX * 1.10) * (PH - 40)

    def x_glob(x0, lam, phi):                # меридіани сходяться як cos φ
        return x0 + PW / 2 + lam / 3.0 * HALF * math.cos(math.radians(phi))

    def x_str(x0, lam, phi):                 # меридіани випрямлені
        return x0 + PW / 2 + lam / 3.0 * HALF

    # ── панель A: глобус ───────────────────────────────────────────────
    x0 = XS[0]
    frags += panel_frame(x0, "на глобусі")
    for phi in LATS:
        yy = y_lin(x0, phi)
        frags.append(line(x_glob(x0, -3, phi), yy, x_glob(x0, 3, phi), yy,
                          color=MUTED, sw=1.1))
    for lam in LAM:
        pts = []
        p = 0
        while p <= 78:
            pts.append((x_glob(x0, lam, p), y_lin(x0, p)))
            p += 3
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.1"/>'
                     % (" ".join("%.1f,%.1f" % q for q in pts), MUTED))
    # кружечок на місцевості, широта 60°
    cxA, cyA = x_glob(x0, 0, 60), y_lin(x0, 60)
    frags.append(circle(cxA, cyA, 12, fill="#fdecea", stroke=POS, sw=2.2))
    frags.append(text(x0 + PW / 2, TOP + PH + 22,
                      "кругла ділянка землі на 60°", size=11, color=POS))

    # ── панель B: меридіани випрямлено, вертикаль НЕ чіпали ─────────────
    x0 = XS[1]
    frags += panel_frame(x0, "меридіани випрямлено")
    for phi in LATS:
        yy = y_lin(x0, phi)
        frags.append(line(x_str(x0, -3, phi), yy, x_str(x0, 3, phi), yy, color=MUTED, sw=1.1))
    for lam in LAM:
        frags.append(line(x_str(x0, lam, 0), y_lin(x0, 0),
                          x_str(x0, lam, 78), y_lin(x0, 78), color=MUTED, sw=1.1))
    cxB, cyB = x_str(x0, 0, 60), y_lin(x0, 60)
    frags.append('<ellipse cx="%.1f" cy="%.1f" rx="24" ry="12" fill="#fdecea" '
                 'stroke="%s" stroke-width="2.2"/>' % (cxB, cyB, POS))
    frags.append(text(x0 + PW / 2, TOP + PH + 22,
                      "коло сплющилось: кути зламані", size=11, color=POS))

    # ── панель C: Меркатор ─────────────────────────────────────────────
    x0 = XS[2]
    frags += panel_frame(x0, "Меркатор")
    for phi in LATS:
        yy = y_mer(x0, phi)
        frags.append(line(x_str(x0, -3, phi), yy, x_str(x0, 3, phi), yy, color=FIELD, sw=1.2))
    for lam in LAM:
        frags.append(line(x_str(x0, lam, 0), y_mer(x0, 0),
                          x_str(x0, lam, 78), y_mer(x0, 78), color=FIELD, sw=1.2))
    cxC, cyC = x_str(x0, 0, 60), y_mer(x0, 60)
    frags.append(circle(cxC, cyC, 24, fill="#eafaf0", stroke=FIELD, sw=2.4))
    frags.append(text(x0 + PW / 2, TOP + PH + 22,
                      "коло лишилось колом, але вдвічі більшим", size=11, color=FIELD))

    # ── підсумковий рядок під панелями, у чистому полі ──────────────────
    frags.append(fitbox(30, TOP + PH + 42, W - 60, 78,
                        "\n".join([
                            "Випрямити меридіани — значить розтягнути кожну паралель у 1/cos φ разів.",
                            "Щоб форма вціліла, стільки ж треба додати й по вертикалі: dy/dφ = 1/cos φ.",
                            "Сходинки широти на карті Меркатора ростуть до полюса саме через це.",
                        ]),
                        size=13, fill="#f7fbf8", stroke=FIELD, sw=1.6))
    render(os.path.join(IMG, "conformal-stretch.svg"), W, H, *frags)


# ───────────────────────────────────────────────────────────────────────────
def clip_square():
    """Графік y(φ) = ln tan(45°+φ/2): нескінченний до полюса, зрізаний на y=π."""
    W, H = 760, 460
    frags = [text(W / 2, 28, "Де обривається карта: y(φ) росте без межі, квадрат — ні",
                  size=16, bold=True)]

    L, R = 92, W - 210        # поле графіка по x (праворуч лишаємо місце під підпис)
    B, T = H - 92, 62         # низ і верх поля
    YTOP = 4.2                # максимум по осі y

    def px(phi):
        return L + phi / 90.0 * (R - L)

    def py(y):
        return B - y / YTOP * (B - T)

    frags.append(rect(L, T, R - L, B - T, fill="#fcfcfd", stroke=MUTED, sw=1.2))
    # осі
    frags.append(line(L, B, R, B, color=INK, sw=1.8))
    frags.append(line(L, B, L, T, color=INK, sw=1.8))
    for phi in (0, 30, 60, 90):
        frags.append(line(px(phi), B, px(phi), B + 6, color=INK, sw=1.4))
        frags.append(text(px(phi), B + 22, "%d°" % phi, size=12))
    frags.append(text((L + R) / 2, B + 46, "широта φ", size=13, bold=True))
    for yv in (1, 2, 3, 4):
        frags.append(line(L - 6, py(yv), L, py(yv), color=INK, sw=1.4))
        frags.append(text(L - 14, py(yv) + 4, "%d" % yv, size=12, anchor="end"))
    frags.append(text(L - 52, (T + B) / 2, "y", size=14, bold=True, anchor="middle"))

    # сама крива
    pts = []
    p = 0.0
    while p <= 88.6:
        yy = ymerc(p)
        if yy > YTOP:
            break
        pts.append((px(p), py(yy)))
        p += 0.4
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                 % (" ".join("%.1f,%.1f" % q for q in pts), NEG))

    # рівень y = π
    frags.append(line(L, py(math.pi), R, py(math.pi), color=POS, sw=1.8, dash="6,4"))
    frags.append(text(L + 8, py(math.pi) - 9, "y = π — край квадратної карти",
                      size=12, color=POS, anchor="start", bold=True))
    # перетин
    phic = 85.0511287798
    frags.append(line(px(phic), B, px(phic), py(math.pi), color=POS, sw=1.6, dash="4,4"))
    frags.append(circle(px(phic), py(math.pi), 5, fill=POS, stroke=POS))
    frags.append(mtext(px(phic) - 12, B - 92, ["φ = 85.0511°", "тут ріжемо"],
                       size=12, color=POS, anchor="end", bold=True))
    # асимптота
    frags.append(line(px(90), B, px(90), T, color=MUTED, sw=1.4, dash="3,4"))
    frags.append(mtext(px(90) + 10, T + 30, ["полюс:", "y → ∞"],
                       size=12, color=MUTED, anchor="start"))

    frags.append(fitbox(R + 26, T + 96, 168, 176,
                        "\n".join([
                            "Полюс на карті",
                            "Меркатора не",
                            "поміщається:",
                            "розтягнення 1/cos φ",
                            "росте без межі.",
                            "",
                            "Тайлам потрібен",
                            "квадрат — тож",
                            "карту обрізають",
                            "рівно там, де",
                            "висота зрівнялась",
                            "із шириною.",
                        ]),
                        size=12, fill="#f7fbf8", stroke=FIELD, sw=1.6))
    render(os.path.join(IMG, "clip-square.svg"), W, H, *frags)


# ───────────────────────────────────────────────────────────────────────────
def tile_grid():
    """Самоподібність: z=0 → z=1 → z=2, кожен тайл ділиться рівно на чотири."""
    W, H = 900, 430
    frags = [text(W / 2, 28, "Тайлова сітка: кожен рівень — вчетверо дрібніший поділ того самого квадрата",
                  size=16, bold=True)]

    S = 210                    # сторона квадрата
    TOP = 78
    XS = (46, 345, 644)
    LBL = ("z = 0 · один тайл", "z = 1 · 2×2 тайли", "z = 2 · 4×4 тайли")

    for k, x0 in enumerate(XS):
        n = 2 ** k
        cell = S / n
        frags.append(rect(x0, TOP, S, S, fill="#fcfcfd", stroke=INK, sw=2.0))
        for i in range(1, n):
            frags.append(line(x0 + i * cell, TOP, x0 + i * cell, TOP + S, color=MUTED, sw=1.1))
            frags.append(line(x0, TOP + i * cell, x0 + S, TOP + i * cell, color=MUTED, sw=1.1))
        frags.append(text(x0 + S / 2, TOP - 14, LBL[k], size=13, bold=True))

    # підсвітка: (z=1, x=1, y=0) і його четверо дітей на z=2
    x0 = XS[1]; cell = S / 2
    frags.append(rect(x0 + cell, TOP, cell, cell, fill="#eafaf0", stroke=FIELD, sw=2.6))
    frags.append(text(x0 + cell * 1.5, TOP + cell / 2 + 5, "1,0", size=13, bold=True, color=FIELD))
    x0 = XS[2]; cell = S / 4
    frags.append(rect(x0 + 2 * cell, TOP, 2 * cell, 2 * cell, fill="#eafaf0", stroke=FIELD, sw=2.6))
    for (ix, iy) in ((2, 0), (3, 0), (2, 1), (3, 1)):
        frags.append(text(x0 + (ix + 0.5) * cell, TOP + (iy + 0.5) * cell + 4,
                          "%d,%d" % (ix, iy), size=11, color=FIELD, bold=True))

    # напрямки нумерації — на першому квадраті, стрілки поза сіткою
    x0 = XS[0]
    frags.append(arrow(x0, TOP - 32, x0 + 72, TOP - 32, color=NEG, sw=1.8))
    frags.append(text(x0 + 84, TOP - 28, "x →", size=12, color=NEG, anchor="start", bold=True))
    frags.append(arrow(x0 - 22, TOP, x0 - 22, TOP + 72, color=NEG, sw=1.8))
    frags.append(text(x0 - 30, TOP + 88, "y ↓", size=12, color=NEG, anchor="end", bold=True))
    frags.append(mtext(x0 + S / 2, TOP + S / 2 - 8,
                       ["початок — північно-", "західний кут:", "λ = −180°, φ = +85.05°"],
                       size=11, color=MUTED))

    # зв'язок «батько → четверо дітей»
    frags.append(arrow(XS[1] + S + 10, TOP + S / 2, XS[2] - 12, TOP + S / 2, color=FIELD, sw=2.0))

    frags.append(fitbox(46, TOP + S + 46, W - 92, 62,
                        "\n".join([
                            "Тайл (z, x, y) ділиться рівно на чотирьох дітей (z+1, 2x+i, 2y+j) — це квадродерево,",
                            "а адреса тайла є шляхом по ньому. Тому кеш і предзавантаження працюють цілими гілками.",
                        ]),
                        size=13, fill="#f7fbf8", stroke=FIELD, sw=1.6))
    render(os.path.join(IMG, "tile-grid.svg"), W, H, *frags)


# ───────────────────────────────────────────────────────────────────────────
def pseudo_error():
    """Ціна «псевдо»: зсув паралелі, коли еліпсоїдальну широту кладуть у сферичну формулу."""
    W, H = 760, 440
    frags = [text(W / 2, 28, "Ціна «псевдо»: на скільки з'їжджає паралель", size=16, bold=True)]

    a = 6378137.0
    f = 1 / 298.257223563
    e2 = f * (2 - f)
    e = math.sqrt(e2)

    def shift_km(d):
        p = math.radians(d)
        if d == 0:
            return 0.0
        y = a * math.log(math.tan(math.pi / 4 + p / 2) *
                         ((1 - e * math.sin(p)) / (1 + e * math.sin(p))) ** (e / 2))
        ps = 2 * math.atan(math.exp(y / a)) - math.pi / 2
        M = a * (1 - e2) / (1 - e2 * math.sin(p) ** 2) ** 1.5
        return abs((p - ps) * M) / 1000.0

    L, R = 84, W - 226
    B, T = H - 92, 66
    YMAX = 24.0

    def px(d):
        return L + d / 85.0 * (R - L)

    def py(v):
        return B - v / YMAX * (B - T)

    frags.append(rect(L, T, R - L, B - T, fill="#fcfcfd", stroke=MUTED, sw=1.2))
    frags.append(line(L, B, R, B, color=INK, sw=1.8))
    frags.append(line(L, B, L, T, color=INK, sw=1.8))
    for d in (0, 30, 45, 60, 85):
        frags.append(line(px(d), B, px(d), B + 6, color=INK, sw=1.4))
        frags.append(text(px(d), B + 22, "%d°" % d, size=12))
    frags.append(text((L + R) / 2, B + 46, "широта φ", size=13, bold=True))
    for v in (5, 10, 15, 20):
        frags.append(line(L - 6, py(v), L, py(v), color=INK, sw=1.4))
        frags.append(text(L - 12, py(v) + 4, "%d" % v, size=12, anchor="end"))
    frags.append(mtext(L - 62, (T + B) / 2 - 14, ["зсув,", "км"], size=12, bold=True))

    pts = []
    d = 0.0
    while d <= 85.01:
        pts.append((px(d), py(shift_km(d))))
        d += 0.5
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                 % (" ".join("%.1f,%.1f" % q for q in pts), POS))

    # пік на 45°
    peak = shift_km(45)
    frags.append(circle(px(45), py(peak), 5, fill=POS, stroke=POS))
    frags.append(mtext(px(45) + 12, py(peak) - 22, ["максимум ≈ 21.4 км", "на 45°"],
                       size=12, color=POS, anchor="start", bold=True))

    frags.append(fitbox(R + 28, T + 40, 182, 190,
                        "\n".join([
                            "Web Mercator бере",
                            "геодезичну широту",
                            "WGS-84 і кладе її",
                            "у сферичну формулу.",
                            "",
                            "Прийняти таку карту",
                            "за справжній",
                            "еліпсоїдальний",
                            "Меркатор — значить",
                            "промахнутися по",
                            "землі на десятки",
                            "кілометрів.",
                        ]),
                        size=12, fill="#fdf3f2", stroke=POS, sw=1.6))
    render(os.path.join(IMG, "pseudo-error.svg"), W, H, *frags)


# ───────────────────────────────────────────────────────────────────────────
def hist_wright_vs_log():
    """Що саме побачив Генрі Бонд 1645 року: чисельна таблиця Райта
    лягає точка в точку на криву логарифма тангенса півкута."""
    W, H = 900, 500
    X0, X1 = 130, 620
    Y0, Y1 = 100, 410
    PHI_MAX, Y_MAX = 80.0, 2.6

    def sum_sec(phi_deg, step_min=1.0):
        d = math.radians(step_min / 60.0)
        n = int(round(phi_deg * 60 / step_min))
        t = 0.0
        for i in range(n):
            t += 1.0 / math.cos((i + 0.5) * d)
        return t * d

    def px(phi):
        return X0 + phi / PHI_MAX * (X1 - X0)

    def py(v):
        return Y1 - v / Y_MAX * (Y1 - Y0)

    frags = [text(W / 2, 32, "Таблиця Райта і крива Бонда — та сама лінія",
                  size=17, bold=True)]

    frags.append(line(X0, Y1, X1 + 20, Y1, color=INK, sw=1.6))
    frags.append(line(X0, Y1, X0, Y0 - 20, color=INK, sw=1.6))
    for phi in (0, 20, 40, 60, 80):
        x = px(phi)
        frags.append(line(x, Y1, x, Y1 + 6, color=MUTED, sw=1.2))
        frags.append(text(x, Y1 + 26, "%d°" % phi, size=12, color=MUTED))
    for v in (0.5, 1.0, 1.5, 2.0, 2.5):
        y = py(v)
        frags.append(line(X0 - 6, y, X0, y, color=MUTED, sw=1.2))
        frags.append(text(X0 - 16, y + 4, "%.1f" % v, size=12, color=MUTED, anchor="end"))
    frags.append(text((X0 + X1) / 2, Y1 + 56, "широта φ", size=13, color=MUTED))
    frags.append(text(X0 - 74, (Y0 + Y1) / 2, "y", size=13, color=MUTED))

    pts = []
    phi = 0.0
    while phi <= PHI_MAX + 1e-9:
        pts.append("%.2f,%.2f" % (px(phi),
                                  py(math.log(math.tan(math.pi / 4 + math.radians(phi) / 2)))))
        phi += 0.5
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                 % (" ".join(pts), NEG))

    for phi in range(0, 81, 10):
        frags.append(circle(px(phi), py(sum_sec(phi)), 5.5, fill="#ffffff", stroke=POS, sw=2.4))

    frags.append(line(X0 + 26, Y0 + 24, X0 + 64, Y0 + 24, color=NEG, sw=3))
    frags.append(text(X0 + 76, Y0 + 29, "крива ln tan(45° + φ/2) — здогад Бонда, 1645",
                      size=12, color=INK, anchor="start"))
    frags.append(circle(X0 + 45, Y0 + 56, 5.5, fill="#ffffff", stroke=POS, sw=2.4))
    frags.append(text(X0 + 76, Y0 + 61, "таблиця Райта, 1599 — сума секансів",
                      size=12, color=INK, anchor="start"))

    frags.append(fitbox(668, 120, 212, 276,
                        "\n".join([
                            "Звірка на 45°,",
                            "у мінутах екватора:",
                            "",
                            "сума секансів",
                            "з кроком 1′ — 3029.9′",
                            "3437.7 · ln tan 67.5°",
                            "— теж 3029.9′",
                            "",
                            "Збіг тримається",
                            "по всій таблиці.",
                            "Саме тому Бонд",
                            "повірив у формулу",
                            "за 23 роки до того,",
                            "як її довели.",
                        ]),
                        size=12.5, fill="#f2f7f3", stroke=FIELD, sw=1.6))
    render(os.path.join(IMG, "hist-wright-vs-log.svg"), W, H, *frags)


# ───────────────────────────────────────────────────────────────────────────
def hist_two_acts():
    """Два акти народження проєкції: XVI–XVII ст. і 2005–2014."""
    W, H = 940, 560
    frags = [text(W / 2, 30, "Двічі народжена проєкція: коли практика випереджає підставу",
                  size=17, bold=True)]

    def band(y_line, label, marks, box_y, box_h):
        out = [text(58, y_line - 62, label, size=14, bold=True, anchor="start", color=MUTED)]
        xs = [m[0] for m in marks]
        out.append(line(min(xs) - 40, y_line, max(xs) + 40, y_line, color=INK, sw=2))
        for x, year, body in marks:
            out.append(circle(x, y_line, 6, fill=POS, stroke=POS, sw=2))
            out.append(text(x, y_line - 18, year, size=14, bold=True))
            out.append(fitbox(x - 66, box_y, 132, box_h, body, size=11.5, pad=7))
        return out

    frags += band(158, "Акт перший — карта є, формули немає", [
        (98, "1569", "\n".join(["Ґерард Меркатор", "друкує карту.", "Метод не", "розкриває"])),
        (242, "≈ 1589", "\n".join(["Томас Гарріот", "виводить", "математику —", "і кладе в стіл"])),
        (386, "1599", "\n".join(["Едвард Райт:", "таблиця сум", "секансів", "із кроком 1′"])),
        (530, "1645", "\n".join(["Генрі Бонд", "звіряє з логарифмом", "тангенса —", "і вгадує"])),
        (674, "1668", "\n".join(["Джеймс Ґреґорі", "доводить —", "але майже", "нечитабельно"])),
        (818, "1670", "\n".join(["Ісаак Барроу:", "прості дроби,", "перше зрозуміле", "доведення"])),
    ], 178, 100)

    frags += band(400, "Акт другий — стандарт є, підстави немає", [
        (150, "2005", "\n".join(["8 лютого:", "Google Maps —", "квадратні тайли,", "сферична формула"])),
        (380, "2007", "\n".join(["Крістофер Шмідт:", "неофіційний код", "EPSG:900913", "(GOOGLE цифрами)"])),
        (610, "2008", "\n".join(["EPSG:3785, далі", "чинний 3857", "«WGS 84 /", "Pseudo-Mercator»"])),
        (840, "2014", "\n".join(["NGA: непридатна", "для будь-якого", "офіційного", "вжитку"])),
    ], 420, 100)

    frags.append(text(W / 2, 540, "Шкала часу не в масштабі — показано лише порядок подій.",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "hist-two-acts.svg"), W, H, *frags)


def _arc(cx, cy, r, a0, a1, color=INK, sw=1.4):
    """Дуга від кута a0 до a1 (градуси, проти годинникової від осі x; екранний y — донизу)."""
    x0 = cx + r * math.cos(math.radians(a0))
    y0 = cy - r * math.sin(math.radians(a0))
    x1 = cx + r * math.cos(math.radians(a1))
    y1 = cy - r * math.sin(math.radians(a1))
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 0 if a1 > a0 else 1
    return ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f"/>' % (x0, y0, r, r, large, sweep, x1, y1, color, sw))


def _poly(points, fill, stroke="none", sw=1.5):
    d = " ".join("%.1f,%.1f" % p for p in points)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)


def _path(points, color=LINE, sw=1.8):
    d = "M " + " L ".join("%.1f %.1f" % p for p in points)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


# ───────────────────────────────────────────────────────────────────────────
def math_half_angle():
    """Вписаний кут доводить (1 + sin φ)/cos φ = tan(45° + φ/2)."""
    W, H = 820, 470
    frags = [text(W / 2, 28, "Чому (1 + sin φ)/cos φ — це тангенс кута 45° + φ/2",
                  size=16, bold=True)]

    OX, OY, R = 280, 262, 140
    PHI = 50.0
    rad = math.radians(PHI)
    Ex, Ey = OX + R, OY                       # схід кола
    Ax, Ay = OX, OY + R                       # низ кола
    Px, Py = OX + R * math.cos(rad), OY - R * math.sin(rad)
    Fx, Fy = Px, Ay                           # основа прямокутного трикутника

    frags.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.7"/>' % (OX, OY, R, LINE))

    # катети трикутника AFP
    frags.append(line(Ax, Ay, Fx, Fy, color=MUTED, sw=1.6, dash="6 5"))
    frags.append(line(Fx, Fy, Px, Py, color=MUTED, sw=1.6, dash="6 5"))

    # радіуси й хорди
    frags.append(line(OX, OY, Ex, Ey, color=MUTED, sw=1.4))
    frags.append(line(OX, OY, Px, Py, color=MUTED, sw=1.4))
    frags.append(line(Ax, Ay, Ex, Ey, color=NEG, sw=1.9))
    frags.append(line(Ax, Ay, Px, Py, color=POS, sw=2.2))

    # кути
    frags.append(_arc(OX, OY, 52, 0, PHI, color=INK, sw=1.5))
    frags.append(text(341.6, 233.3, "φ", size=14, bold=True))
    frags.append(_arc(Ax, Ay, 62, 45, 45 + PHI / 2, color=POS, sw=1.5))
    frags.append(text(329, 324, "φ/2", size=13, color=POS, bold=True))
    frags.append(_arc(Ax, Ay, 40, 0, 45, color=NEG, sw=1.5))
    frags.append(text(334, 384, "45°", size=13, color=NEG, bold=True))

    # точки
    for cx, cy in ((OX, OY), (Ex, Ey), (Ax, Ay), (Px, Py)):
        frags.append(circle(cx, cy, 4, fill=INK, stroke=INK, sw=1))
    frags.append(text(272, 280, "O", size=13, anchor="end", color=MUTED))
    frags.append(text(432, 266, "E", size=13, anchor="start", color=MUTED))
    frags.append(text(268, 420, "A", size=13, anchor="end", color=MUTED))
    frags.append(text(382, 148, "P", size=13, anchor="start", color=MUTED))

    # підписи катетів
    frags.append(text(325, 428, "cos φ", size=13, color=MUTED))
    frags.append(line(430, 296, 376, 296, color=MUTED, sw=1.1, dash="4 4"))
    frags.append(text(434, 300, "1 + sin φ", size=13, anchor="start", color=MUTED))

    frags.append(fitbox(515, 100, 285, 280, "\n".join([
        "P на колі під кутом φ,",
        "A — нижня точка кола.",
        "",
        "∠EOP = φ — центральний,",
        "∠EAP = φ/2 — вписаний.",
        "",
        "|OA| = |OE| і OA ⊥ OE,",
        "тому AE іде під 45°,",
        "а AP — під 45° + φ/2.",
        "",
        "Катети: AF = cos φ,",
        "FP = 1 + sin φ.",
        "",
        "tan(45° + φ/2) =",
        "= (1 + sin φ)/cos φ",
    ]), size=13, fill="#f7f9fc", stroke=MUTED, sw=1.5))

    render(os.path.join(IMG, "half-angle-inscribed.svg"), W, H, *frags)


# ───────────────────────────────────────────────────────────────────────────
def math_circle_hyperbola():
    """Словник φ ↔ y: та сама пара чисел на колі й на гіперболі."""
    W, H = 900, 590
    frags = [text(W / 2, 28, "Одна тотожність, дві геометрії: sec²φ − tan²φ = 1 і cosh²y − sinh²y = 1",
                  size=16, bold=True)]

    U = 95.0
    PHI = 50.0
    ph = math.radians(PHI)
    Y0 = math.log(math.tan(math.pi / 4 + ph / 2))     # 1.00575 — той самий стан

    # ── ліва панель: коло ────────────────────────────────────────────────
    O1X, O1Y = 205, 330
    frags.append(_poly([(O1X, O1Y)] +
                       [(O1X + U * math.cos(math.radians(a)), O1Y - U * math.sin(math.radians(a)))
                        for a in [i * PHI / 24 for i in range(25)]],
                       fill="#fdecea"))
    frags.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.7"/>' % (O1X, O1Y, U, LINE))
    Tx, Ty = O1X + U, O1Y - U * math.tan(ph)          # кінець дотичного відрізка
    frags.append(line(O1X, O1Y, O1X + U, O1Y, color=MUTED, sw=1.6))          # радіус = 1
    frags.append(line(O1X + U, O1Y, Tx, Ty, color=NEG, sw=3.0))              # tan φ
    frags.append(line(O1X, O1Y, Tx, Ty, color=POS, sw=3.0))                  # sec φ
    frags.append(circle(O1X + U * math.cos(ph), O1Y - U * math.sin(ph), 4,
                        fill=INK, stroke=INK, sw=1))
    frags.append(_arc(O1X, O1Y, 28, 0, PHI, color=INK, sw=1.4))
    frags.append(text(248.5, 309.7, "φ", size=14, bold=True))
    frags.append(text(250, 222, "sec φ", size=14, color=POS, bold=True))
    frags.append(text(310, 270, "tan φ", size=14, color=NEG, anchor="start", bold=True))
    frags.append(text(252, 354, "1", size=13, color=MUTED))
    frags.append(text(192, 348, "O", size=13, anchor="end", color=MUTED))

    # ── права панель: гіпербола ──────────────────────────────────────────
    O2X, O2Y = 600, 330
    ts = [-1.05 + i * (1.15 + 1.05) / 90 for i in range(91)]
    curve = [(O2X + U * math.cosh(t), O2Y - U * math.sinh(t)) for t in ts]
    sect = [(O2X, O2Y)] + [(O2X + U * math.cosh(t), O2Y - U * math.sinh(t))
                           for t in [i * Y0 / 24 for i in range(25)]]
    frags.append(_poly(sect, fill="#fdecea"))
    frags.append(line(520, O2Y, 800, O2Y, color=MUTED, sw=1.2, dash="5 5"))
    frags.append(line(O2X, 258, O2X, 402, color=MUTED, sw=1.2, dash="5 5"))
    frags.append(_path(curve, color=LINE, sw=1.7))
    Qx, Qy = O2X + U * math.cosh(Y0), O2Y - U * math.sinh(Y0)
    frags.append(line(O2X, O2Y, Qx, O2Y, color=POS, sw=3.0))                 # cosh y
    frags.append(line(Qx, O2Y, Qx, Qy, color=NEG, sw=3.0))                   # sinh y
    frags.append(line(O2X, O2Y, Qx, Qy, color=MUTED, sw=1.3))
    frags.append(circle(Qx, Qy, 4, fill=INK, stroke=INK, sw=1))
    frags.append(text(660, 360, "cosh y", size=14, color=POS, bold=True))
    frags.append(text(758, 275, "sinh y", size=14, color=NEG, anchor="start", bold=True))
    frags.append(text(588, 352, "O", size=13, anchor="end", color=MUTED))

    frags.append(text(205, 478, "коло x² + y² = 1, площа сектора = φ/2", size=12, color=MUTED))
    frags.append(text(650, 478, "гіпербола x² − y² = 1, площа сектора = y/2", size=12, color=MUTED))

    frags.append(fitbox(100, 492, 700, 78, "\n".join([
        "sec φ = cosh y      tan φ = sinh y      sin φ = tanh y      cos φ = sech y",
        "однакові кольори — однакові довжини: пара чисел на обох панелях та сама",
        "y = ∫ sec φ dφ        φ = gd(y) = 2·arctan(eʸ) − π/2",
    ]), size=13, fill="#f7f9fc", stroke=MUTED, sw=1.5))

    render(os.path.join(IMG, "circle-hyperbola.svg"), W, H, *frags)


# ───────────────────────────────────────────────────────────────────────────
def proj_seam_wrap():
    """x циклічний (mod 2^z), y обрізаний. Наївні min/max через 180-й меридіан
    перетворюють два тайли на весь світ."""
    W, H = 950, 500
    frags = [text(W / 2, 30, "Схід і захід склеєні, північ і південь — обрізані",
                  size=16, bold=True)]

    N = 8                       # рівень z = 3
    CELL = 32
    GX, GY = 78, 168
    GW = CELL * N               # 256
    R0, R1 = 3, 4               # рядки видимої області

    # 1) наївна смуга на всю ширину
    frags.append(rect(GX, GY + R0 * CELL, GW, (R1 - R0 + 1) * CELL,
                      fill="#fdecea", stroke="none", sw=0, rx=0))
    # 2) правильні два стовпці
    for col in (N - 1, 0):
        frags.append(rect(GX + col * CELL, GY + R0 * CELL, CELL, (R1 - R0 + 1) * CELL,
                          fill="#f5b7b1", stroke=POS, sw=2, rx=0))
    # 3) сітка
    for i in range(N + 1):
        frags.append(line(GX + i * CELL, GY, GX + i * CELL, GY + GW, color="#c9ced6", sw=1))
        frags.append(line(GX, GY + i * CELL, GX + GW, GY + i * CELL, color="#c9ced6", sw=1))
    frags.append(rect(GX, GY, GW, GW, fill="none", stroke=INK, sw=1.8, rx=0))

    # 4) зріз по широті — товсті смуги на верхньому й нижньому краях
    for yy in (GY, GY + GW):
        frags.append(line(GX - 6, yy, GX + GW + 6, yy, color=NEG, sw=5))
    frags.append(text(GX + GW + 14, GY + 5, "зріз +85.05°", size=11, color=NEG, anchor="start"))
    frags.append(text(GX + GW + 14, GY + GW + 5, "зріз −85.05°", size=11, color=NEG, anchor="start"))

    # 5) номери стовпців
    for i in range(N):
        frags.append(text(GX + i * CELL + CELL / 2, GY + GW + 20, str(i), size=11, color=MUTED))
    frags.append(text(GX + GW / 2, GY + GW + 42, "номер стовпця x", size=12, color=MUTED))

    # 6) склейка країв: дуга над сіткою
    top = GY - 26
    frags.append(line(GX + GW, GY - 8, GX + GW, top, color=FIELD, sw=2))
    frags.append(line(GX + GW, top, GX + 14, top, color=FIELD, sw=2))
    frags.append(arrow(GX + 14, top, GX + 2, GY - 8, color=FIELD, sw=2))
    frags.append(text(GX + GW / 2, top - 12, "x: 7 → 0, тобто mod 8 — краї склеєні",
                      size=12, color=FIELD, bold=True))

    # 7) праворуч — три висновки
    BX, BW = 400, 500
    frags.append(fitbox(BX, 150, BW, 82, "\n".join([
        "НАЇВНО:  min(7, 0) = 0,  max(7, 0) = 7",
        "стовпці 0…7 — це 8 з 8, тобто ВЕСЬ СВІТ",
    ]), size=13, fill="#fdecea", stroke=POS, sw=1.8))

    frags.append(fitbox(BX, 250, BW, 96, "\n".join([
        "ПРАВИЛЬНО: рахуємо ширину ДО floor.",
        "0.222 < 7.778  →  додаємо n:  8.222",
        "стовпці 7…8  →  7 і 8 mod 8 = 0  →  2 тайли",
    ]), size=13, fill="#eafaf1", stroke=FIELD, sw=1.8))

    frags.append(fitbox(BX, 364, BW, 96, "\n".join([
        "x  завжди  mod 2ᶻ        (циліндр)",
        "y  завжди  clamp [0, 2ᶻ−1]   (розріз)",
        "симетрична обробка осей — помилка",
    ]), size=13, fill="#f7f9fc", stroke=MUTED, sw=1.6))

    render(os.path.join(IMG, "seam-wrap.svg"), W, H, *frags)


# ───────────────────────────────────────────────────────────────────────────
def proj_float32_floor():
    """Розмір пікселя на землі падає вдвічі щорівня, а крок float32 стоїть
    на ~2.39 м. Перетин рівно на z = 16."""
    W, H = 900, 500
    frags = [text(W / 2, 30, "float32 у світових координатах: підлога 2.39 метра",
                  size=16, bold=True)]

    EQ = 2 * math.pi * 6378137.0
    FLOOR = EQ / 2 ** 24                      # 2.3887 м — крок float32 на землі
    Z0, Z1 = 8, 24
    LO, HI = -2.4, 3.0                        # log10 меж по вертикалі

    PX, PY = 96, 78                           # лівий верхній кут поля
    PW, PH = 560, 320

    def sx(z):
        return PX + (z - Z0) / (Z1 - Z0) * PW

    def sy(v):
        return PY + (HI - math.log10(v)) / (HI - LO) * PH

    # поле й горизонтальна сітка
    frags.append(rect(PX, PY, PW, PH, fill="#ffffff", stroke=MUTED, sw=1.4, rx=0))
    for e in range(-2, 4):
        v = 10.0 ** e
        yy = sy(v)
        if not (PY <= yy <= PY + PH):
            continue
        frags.append(line(PX, yy, PX + PW, yy, color="#e5e8ec", sw=1))
        lab = "%g км" % (v / 1000) if v >= 1000 else ("%g м" % v)
        frags.append(text(PX - 10, yy + 4, lab, size=11, color=MUTED, anchor="end"))

    # вертикальна сітка й підписи зуму
    for z in range(Z0, Z1 + 1, 2):
        frags.append(line(sx(z), PY, sx(z), PY + PH, color="#e5e8ec", sw=1))
        frags.append(text(sx(z), PY + PH + 20, str(z), size=11, color=MUTED))
    frags.append(text(PX + PW / 2, PY + PH + 42, "рівень зуму z", size=12, color=MUTED))

    # область, де float32 грубіший за піксель
    frags.append(rect(sx(16), PY, PX + PW - sx(16), PH,
                      fill="#fdecea", stroke="none", sw=0, rx=0))

    # спадна пряма: розмір пікселя на землі
    pts = [(sx(z), sy(EQ / 2 ** (z + 8))) for z in range(Z0, Z1 + 1)]
    frags.append(_path(pts, color=NEG, sw=2.6))

    # горизонталь: крок float32
    frags.append(line(PX, sy(FLOOR), PX + PW, sy(FLOOR), color=POS, sw=2.6))

    # перетин на z = 16
    frags.append(circle(sx(16), sy(FLOOR), 5.5, fill="#ffffff", stroke=INK, sw=2))
    frags.append(text(sx(16), PY - 12, "z = 16: крок = рівно 1 піксель", size=12, bold=True))

    # підписи кривих
    frags.append(text(sx(9), sy(EQ / 2 ** (9 + 8)) - 14, "розмір пікселя на землі",
                      size=12, color=NEG, anchor="start", bold=True))
    frags.append(text(sx(8.4), sy(FLOOR) + 20, "крок float32 ≈ 2.39 м", size=12,
                      color=POS, anchor="start", bold=True))

    # розриви на z = 20 і z = 22
    for z, mult in ((20, "×16"), (22, "×64")):
        xx = sx(z)
        y_pix, y_flr = sy(EQ / 2 ** (z + 8)), sy(FLOOR)
        frags.append(line(xx, y_flr, xx, y_pix, color=INK, sw=1.6, dash="4,3"))
        frags.append(text(xx + 8, (y_flr + y_pix) / 2 + 4, mult, size=12, bold=True,
                          anchor="start"))

    frags.append(fitbox(PX, PY + PH + 60, PW + 150, 66, "\n".join([
        "24 значущі розряди на світ завширшки 2ᶻ⁺⁸ пікселів → крок 40 075 016.686 / 2²⁴ ≈ 2.39 м,",
        "і це число ОДНЕ Й ТЕ САМЕ на будь-якому рівні. Ліки — рахувати від тайла, а не від краю світу.",
    ]), size=12, fill="#f7f9fc", stroke=MUTED, sw=1.5))

    render(os.path.join(IMG, "float32-floor.svg"), W, H, *frags)


if __name__ == "__main__":
    conformal_stretch()
    clip_square()
    tile_grid()
    pseudo_error()
    hist_wright_vs_log()
    hist_two_acts()
    math_half_angle()
    math_circle_hyperbola()
    proj_seam_wrap()
    proj_float32_floor()
    print("ok")
