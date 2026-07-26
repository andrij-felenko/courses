# -*- coding: utf-8 -*-
"""Фігури до теми «OFDM: мультиплексування з ортогональними піднесними».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Один швидкий потік → багато повільних: чому довгий символ не боїться луни ──
# Ідея, яку важко сказати словами: та сама затримка луни Δ, що накриває сусідній
# короткий символ (спотворення), для вдесятеро довшого символу — мала частка.
def fig_split():
    W, H = 900, 470
    f = []

    DELTA = 30          # ширина затримки луни (та сама з обох боків!)
    echo = "#e07a6a"    # приглушений червоний для «луни»

    # ── ліворуч: один швидкий потік, короткі символи ──
    lx, ly, sh = 66, 118, 40
    tau, nL = 26, 8
    f.append(text(lx, ly - 18, "один швидкий потік", 13, INK, "start", bold=True))
    # символи
    f.append(rect(lx, ly, tau * nL, sh, fill="#eef2f7", stroke=NEG, sw=1.6, rx=4))
    for i in range(1, nL):
        f.append(line(lx + i * tau, ly, lx + i * tau, ly + sh, color=NEG, sw=1, dash="3 3"))
    f.append(text(lx, ly + sh + 20, "короткий символ  τ", 11, NEG, "start"))
    # луна: копія, зсунута на Δ — накриває наступний символ
    ey = ly + sh + 40
    k = 3
    f.append(rect(lx + k * tau + DELTA, ey, tau, 26, fill="#fbe6e2", stroke=echo, sw=1.5, rx=4))
    f.append(text(lx + k * tau + DELTA + tau / 2, ey + 17, "луна", 9.5, echo, "middle", bold=True))
    f.append(line(lx + (k + 1) * tau, ly + sh, lx + (k + 1) * tau, ey + 26, color=echo, sw=1.4, dash="4 3"))
    # дужка Δ
    by = ey + 44
    f.append(line(lx + k * tau, by, lx + k * tau + DELTA, by, color=echo, sw=2))
    f.append(text(lx + k * tau + DELTA / 2, by + 16, "Δ", 12, echo, "middle", bold=True))
    f.append(text(lx + tau * nL / 2, by + 40, "затримка луни Δ > τ", 11, echo, "middle", bold=True))
    f.append(text(lx + tau * nL / 2, by + 58, "→ накриває сусідній символ", 10.5, echo, "middle"))

    # ── стрілка поділу ──
    ax = lx + tau * nL + 44
    f.append(arrow(ax, 186, ax + 60, 186, color=INK, sw=2.4))
    f.append(text(ax + 30, 170, "поділ на", 10.5, INK, "middle", bold=True))
    f.append(text(ax + 30, 205, "N повільних", 10.5, INK, "middle", bold=True))

    # ── праворуч: N повільних потоків, довгі символи ──
    rx0 = ax + 112
    T, nR = 78, 3
    labels = ["f₀", "f₁", "f₂", "f₃"]
    ry0, rh, gap = 92, 30, 14
    f.append(text(rx0, ry0 - 14, "N повільних потоків (піднесні)", 13, FIELD, "start", bold=True))
    for j, lab in enumerate(labels):
        ry = ry0 + j * (rh + gap)
        f.append(text(rx0 - 22, ry + rh / 2 + 4, lab, 11, FIELD, "middle", bold=True))
        f.append(rect(rx0, ry, T * nR, rh, fill="#eaf6ee", stroke=FIELD, sw=1.5, rx=4))
        for i in range(1, nR):
            f.append(line(rx0 + i * T, ry, rx0 + i * T, ry + rh, color=FIELD, sw=1, dash="3 3"))
    f.append(text(rx0 + T * nR / 2, ry0 + 4 * (rh + gap) - 2, "⋮", 16, FIELD, "middle", bold=True))
    # довгий символ + та сама луна Δ
    lry = ry0 + 4 * (rh + gap) + 14
    cxr = rx0 + T * nR / 2
    f.append(rect(rx0, lry, T, rh, fill="#eaf6ee", stroke=FIELD, sw=1.6, rx=4))
    f.append(rect(rx0 + T + 6, lry, DELTA, rh, fill="#fbe6e2", stroke=echo, sw=1.4, rx=4))
    f.append(text(rx0 + T + 6 + DELTA / 2, lry + rh / 2 + 4, "Δ", 10, echo, "middle", bold=True))
    f.append(text(cxr, lry + rh + 20, "довгий символ  T = N·τ", 11, FIELD, "middle", bold=True))
    f.append(text(cxr, lry + rh + 38, "та сама Δ — крихітна частка T", 10.5, echo, "middle"))
    f.append(text(cxr, lry + rh + 56, "→ спотворення майже нема", 10.5, FIELD, "middle"))

    render(os.path.join(IMG, "split.svg"), W, H, *f,
           title="Один швидкий потік → багато повільних: довгий символ не боїться луни")


# ── 2. Ортогональність: піки одних піднесних сидять на нулях інших ─────────────
def fig_orthogonal():
    W, H = 900, 400
    f = []
    y0 = 300               # базова лінія
    amp = 150              # висота головної пелюстки
    spacing = 120          # відстань між піднесними в пікселях = Δf
    x_c0 = 210             # центр першої показаної піднесної
    N = 5
    centers = [x_c0 + k * spacing for k in range(N)]

    # вісь частоти
    f.append(line(60, y0, 850, y0, color=MUTED, sw=1.4))
    f.append(arrow(840, y0, 862, y0, color=MUTED, sw=1.4))
    f.append(text(858, y0 + 18, "частота", 11, MUTED, "end"))

    def sinc(t):
        if abs(t) < 1e-9:
            return 1.0
        return math.sin(math.pi * t) / (math.pi * t)

    # вертикальні пунктири крізь центри — показують збіг «пік ↔ нулі сусідів»
    for cx in centers:
        f.append(line(cx, y0 + 6, cx, y0 - amp - 14, color="#dfe3e8", sw=1, dash="3 4"))

    def curve(cx, color, sw):
        pts = []
        x = 70.0
        while x <= 840.0:
            val = sinc((x - cx) / spacing)
            pts.append("%.1f,%.1f" % (x, y0 - amp * val))
            x += 2.0
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                % (" ".join(pts), color, sw))

    # сусідні — приглушені, центральна — виділена
    for k, cx in enumerate(centers):
        if k == 2:
            continue
        f.append(curve(cx, "#9aa4b0", 1.6))
    f.append(curve(centers[2], FIELD, 2.6))

    # підписи піднесних під віссю
    names = ["f₀", "f₁", "f₂", "f₃", "f₄"]
    for cx, nm in zip(centers, names):
        col = FIELD if nm == "f₂" else MUTED
        f.append(text(cx, y0 + 22, nm, 12, col, "middle", bold=(nm == "f₂")))

    # точка «максимум» на центральній + позначки «нуль» на сусідах
    f.append('<circle cx="%.1f" cy="%.1f" r="5" fill="%s"/>' % (centers[2], y0 - amp, FIELD))
    f.append(text(centers[2], y0 - amp - 16, "максимум f₂", 11, FIELD, "middle", bold=True))
    for k in (1, 3):
        f.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s"/>' % (centers[k], y0, POS))
    f.append(text(centers[3] + 8, y0 - 16, "тут f₂ = 0", 10, POS, "start", bold=True))

    # дужка Δf між двома центрами
    yb = 92
    f.append(line(centers[0], yb, centers[1], yb, color=INK, sw=1.6))
    f.append(line(centers[0], yb - 5, centers[0], yb + 5, color=INK, sw=1.6))
    f.append(line(centers[1], yb - 5, centers[1], yb + 5, color=INK, sw=1.6))
    f.append(text((centers[0] + centers[1]) / 2, yb - 10, "Δf = 1/T", 12, INK, "middle", bold=True))

    f.append(text(450, 372, "Спектри перекриваються, але пік кожної піднесної припадає на нулі всіх інших — тому не заважають.",
                  11.5, INK, "middle", bold=True))

    render(os.path.join(IMG, "orthogonal.svg"), W, H, *f,
           title="Ортогональні піднесні: пік однієї — на нулях сусідів")


# ── 3. Ланцюг OFDM: серце передавача й приймача — це IFFT і FFT ────────────────
def fig_chain():
    W, H = 900, 360
    f = []

    def box(cx, cy, w, h, label, stroke, fill, bold=True, fs=12):
        f.append(fitbox(cx - w / 2, cy - h / 2, w, h, label, size=fs,
                        fill=fill, stroke=stroke, sw=1.8, bold=bold, rx=8))

    hbox = 52
    # ── передавач (верхній рядок, зліва направо) ──
    f.append(text(52, 86, "передавач", 12, NEG, "start", bold=True))
    ty = 118
    tx = [(96, 96, "біти"), (232, 116, "QAM-\nвідображення"),
          (360, 96, "IFFT"), (500, 116, "+ цикл.\nпрефікс")]
    for cx, w, lab in tx:
        col = FIELD if lab == "IFFT" else NEG
        fill = "#eaf6ee" if lab == "IFFT" else "#eef2f7"
        box(cx, ty, w, hbox, lab, col, fill)
    f.append(text(360, ty + 44, "серце", 9.5, FIELD, "middle", bold=True))
    # канал
    box(690, ty, 150, hbox + 6, "канал:\nлуни + шум", POS, "#fbe9e6")
    # стрілки передавача
    for a, b in [(144, 174), (290, 302), (408, 442), (558, 615)]:
        f.append(arrow(a, ty, b, ty, color=INK, sw=2))

    # ── поворот вниз ──
    f.append(arrow(690, ty + 31, 690, 242, color=INK, sw=2))

    # ── приймач (нижній рядок, справа наліво) ──
    f.append(text(52, 226, "приймач", 12, FIELD, "start", bold=True))
    ry = 268
    rxb = [(690, 118, "зняти\nпрефікс"), (500, 96, "FFT"),
           (352, 150, "÷ один множник\nна піднесну"), (150, 96, "біти")]
    for cx, w, lab in rxb:
        col = FIELD if lab == "FFT" else NEG
        fill = "#eaf6ee" if lab == "FFT" else "#eef2f7"
        box(cx, ry, w, hbox, lab, col, fill)
    f.append(text(500, ry + 44, "серце", 9.5, FIELD, "middle", bold=True))
    # стрілки приймача (наліво)
    for a, b in [(631, 552), (452, 430), (277, 200)]:
        f.append(arrow(a, ry, b, ry, color=INK, sw=2))

    f.append(text(450, 340, "Уся модуляція — це зворотне перетворення Фур'є; демодуляція — пряме. Канал стає одним множником на кожну піднесну.",
                  11, INK, "middle", bold=True))

    render(os.path.join(IMG, "chain.svg"), W, H, *f,
           title="Ланцюг OFDM: IFFT на передачі, FFT на прийомі")


# ── 4. Поворот 1971: банк генераторів = одне IFFT (для hist-ofdm-birth) ────────
def fig_oscbank():
    W, H = 900, 430
    f = []

    f.append(text(200, 62, "Чанг, 1966: банк генераторів", 13, NEG, "middle", bold=True))
    f.append(text(690, 62, "Вайнстайн–Еберт, 1971: одне IFFT", 13, FIELD, "middle", bold=True))

    # ── ліва половина: дані × тони → суматор ──
    rows = [(102, "d₀", "·f₀"), (160, "d₁", "·f₁"), (218, "d₂", "·f₂")]
    sx, sy = 300, 160
    mx = 192
    for ry, dlab, flab in rows:
        f.append(fitbox(58, ry - 16, 46, 32, dlab, size=13, fill="#eef2f7",
                        stroke=NEG, sw=1.6, bold=True))
        f.append(circle(mx, ry, 14, fill="#ffffff", stroke=INK, sw=1.7))
        f.append(text(mx, ry + 5, "×", 15, INK, "middle", bold=True))
        f.append(text(mx + 22, ry - 12, flab, 9.5, MUTED, "start"))
        f.append(arrow(106, ry, mx - 15, ry, color=INK, sw=1.7))
        f.append(arrow(mx + 15, ry, sx - 17, sy, color=INK, sw=1.5))
    # ⋮ — натяк, що тонів N
    f.append(text(80, 250, "⋮", 16, MUTED, "middle", bold=True))
    f.append(text(mx, 250, "⋮", 16, MUTED, "middle", bold=True))
    f.append(text(mx, 272, "N тонів", 10, MUTED, "middle"))
    # суматор
    f.append(circle(sx, sy, 17, fill="#eef2f7", stroke=INK, sw=1.8))
    f.append(text(sx, sy + 6, "Σ", 17, INK, "middle", bold=True))
    f.append(arrow(sx + 17, sy, 352, sy, color=INK, sw=1.8))
    f.append(text(370, sy + 5, "s(t)", 13, INK, "start", bold=True))
    f.append(text(200, 320, "N генераторів і N змішувачів", 11, MUTED, "middle", bold=True))
    f.append(text(200, 338, "устаткування росте як N — не збудуєш тисячу тонів", 10, MUTED, "middle"))

    # ── місток рівності ──
    f.append(line(432, 96, 432, 300, color=MUTED, sw=1.2, dash="5 6"))
    f.append(text(478, 138, "1971", 11, INK, "middle", bold=True))
    f.append(text(478, 170, "=", 26, INK, "middle", bold=True))
    f.append(text(478, 196, "та сама сума", 10, MUTED, "middle"))

    # ── права половина: одне IFFT ──
    f.append(fitbox(556, 128, 60, 64, "d₀\n⋮\ndₙ₋₁", size=12, fill="#eef2f7",
                    stroke=NEG, sw=1.6, bold=True))
    f.append(arrow(618, 160, 640, 160, color=INK, sw=1.8))
    f.append(fitbox(642, 118, 112, 84, "IFFT", size=17, fill="#eaf6ee",
                    stroke=FIELD, sw=2.0, bold=True))
    f.append(arrow(756, 160, 792, 160, color=INK, sw=1.8))
    f.append(text(806, 165, "s(t)", 13, INK, "start", bold=True))
    f.append(text(700, 240, "один блок · N·log₂N операцій", 11, FIELD, "middle", bold=True))
    f.append(text(700, 258, "масштабується — тому й дешево", 10, MUTED, "middle"))

    render(os.path.join(IMG, "oscbank.svg"), W, H, *f,
           title="Поворот 1971: банк генераторів — це рівно одне перетворення Фур'є")


# ── 5. Хронологія: теорія дозріла до 1980, продукти — з 1990-х (hist) ──────────
def fig_timeline():
    W, H = 1060, 540
    f = []

    theory = [
        (1958, "Кайнплекс", "паралельні тони", "(Collins Radio)"),
        (1966, "Чанг", "умова", "ортогональності"),
        (1967, "Салцберг", "строгий", "аналіз"),
        (1971, "Вайнстайн–Еберт", "ДПФ замість", "генераторів"),
        (1980, "Пелед–Руїс", "циклічний", "префікс"),
        (1985, "Чіміні", "стрибок", "у радіоефір"),
    ]
    adopt = [
        (1993, "ADSL / DMT", "OFDM по", "телефонній парі"),
        (1995, "DAB", "цифрове радіо", "(COFDM)"),
        (1997, "DVB-T", "наземне", "цифрове ТБ"),
        (1999, "Wi-Fi 802.11a", "масова", "бездротова мережа"),
        (2009, "4G LTE", "низхідний", "канал"),
        (2019, "5G NR", "радіо-", "інтерфейс"),
    ]
    x0, x1 = 130, 970
    step = (x1 - x0) / (len(theory) - 1)
    xs = [x0 + i * step for i in range(len(theory))]

    def draw_row(nodes, axis_y, accent, header):
        f.append(text(x0 - 42, axis_y - 78, header, 12, accent, "start", bold=True))
        f.append(line(x0 - 6, axis_y, x1 + 6, axis_y, color=MUTED, sw=1.6))
        for x, (yr, name, c1, c2) in zip(xs, nodes):
            f.append(text(x, axis_y - 50, str(yr), 15, INK, "middle", bold=True))
            fs = fit_font(name, step - 8, 11.5, bold=True)
            f.append(text(x, axis_y - 30, name, fs, accent, "middle", bold=True))
            f.append(circle(x, axis_y, 7, fill="#ffffff", stroke=accent, sw=2.4))
            f.append(text(x, axis_y + 24, c1, 10, MUTED, "middle"))
            f.append(text(x, axis_y + 38, c2, 10, MUTED, "middle"))

    draw_row(theory, 150, NEG, "ЕПОХА ТЕОРІЇ · ідея дозріває на папері")
    draw_row(adopt, 440, FIELD, "ЕПОХА ВПРОВАДЖЕННЯ · кремній дозрів")

    # ── смуга-пауза між епохами ──
    by0, bh = 250, 92
    f.append(rect(60, by0, W - 120, bh, fill="#f4f6f8", stroke=MUTED, sw=1.3, rx=10))
    f.append(text(W / 2, by0 + 26, "⏳  ПАУЗА, ПОКИ ДОЗРІВАЄ КРЕМНІЙ", 13, INK, "middle", bold=True))
    f.append(text(W / 2, by0 + 48, "Алгоритм ШПФ є з 1965-го, та дешевий real-time ШПФ у кремнії — лише наприкінці 1980-х.",
                  11, MUTED, "middle"))
    f.append(text(W / 2, by0 + 66, "Готова з 1980-го ідея масово йде в продукти аж у 1990-х.",
                  11, MUTED, "middle"))
    # стрілки, що ведуть око через паузу
    f.append(arrow(W / 2, 202, W / 2, by0 - 4, color=MUTED, sw=1.8))
    f.append(arrow(W / 2, by0 + bh + 4, W / 2, 392, color=MUTED, sw=1.8))

    render(os.path.join(IMG, "timeline.svg"), W, H, *f,
           title="OFDM: тридцять років між ідеєю і кремнієм")


# ── 6. Дискретна ортогональність: корені з одиниці складаються в нуль ──────────
# Скалярний добуток двох базисів ДПФ = Σ rⁿ по коренях з одиниці. Збіжні (k=m)
# додаються в N; рівновіддалені (k≠m) гасяться дощенту — це видно як замкнений
# многокутник, коли скласти їх хвіст-до-голови.
def fig_roots_sum():
    W, H = 1020, 440
    f = []
    R = 82
    cy = 238
    cxs = [190, 510, 830]

    def unit_circle(cx):
        return [circle(cx, cy, R, fill="#ffffff", stroke="#dfe3e8", sw=1.4),
                line(cx - R - 14, cy, cx + R + 14, cy, color="#c7ccd3", sw=1),
                line(cx, cy - R - 14, cx, cy + R + 14, color="#c7ccd3", sw=1)]

    def vec(cx, ang, color, sw=2.0, r=R):
        a = math.radians(ang)
        return arrow(cx, cy, cx + r * math.cos(a), cy - r * math.sin(a), color=color, sw=sw)

    # ── Панель 1: k = m — усі доданки під кутом 0, сума = N ──
    cx = cxs[0]
    for frag in unit_circle(cx):
        f.append(frag)
    for dy in (-6, -2, 2, 6):
        f.append(arrow(cx, cy + dy, cx + R, cy + dy, color=NEG, sw=2))
    f.append(circle(cx + R, cy, 4, fill=NEG, stroke=NEG, sw=1))
    f.append(text(cx, cy - R - 34, "k = m", 15, INK, "middle", bold=True))
    f.append(text(cx, cy - R - 15, "кожен доданок = 1", 11.5, MUTED, "middle"))
    f.append(text(cx, cy + R + 30, "усі під кутом 0", 11.5, NEG, "middle"))
    f.append(text(cx, cy + R + 50, "Σ = N", 15, NEG, "middle", bold=True))

    # ── Панель 2: k − m ≠ 0 — N рівновіддалених коренів з одиниці, сума = 0 ──
    cx = cxs[1]
    Np = 6
    for frag in unit_circle(cx):
        f.append(frag)
    for n in range(Np):
        f.append(vec(cx, 360.0 * n / Np, FIELD, sw=2.0))
    for n in range(Np):
        a = math.radians(360.0 * n / Np)
        f.append(circle(cx + R * math.cos(a), cy - R * math.sin(a), 4.2, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(cx, cy - R - 34, "k − m ≠ 0", 15, INK, "middle", bold=True))
    f.append(text(cx, cy - R - 15, "N коренів з одиниці", 11.5, MUTED, "middle"))
    f.append(text(cx, cy + R + 30, "рознесені рівномірно", 11.5, FIELD, "middle"))
    f.append(text(cx, cy + R + 50, "Σ = 0", 15, FIELD, "middle", bold=True))

    # ── Панель 3: ті самі вектори хвіст-до-голови → замкнений многокутник ──
    cx = cxs[2]
    sc = 44
    pts = [(0.0, 0.0)]
    ax_, ay_ = 0.0, 0.0
    for n in range(Np):
        a = math.radians(360.0 * n / Np)
        ax_ += math.cos(a)
        ay_ += math.sin(a)
        pts.append((ax_, ay_))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ox = (min(xs) + max(xs)) / 2
    oy = (min(ys) + max(ys)) / 2

    def tp(p):
        return (cx + (p[0] - ox) * sc, cy - (p[1] - oy) * sc)

    for n in range(Np):
        x1, y1 = tp(pts[n])
        x2, y2 = tp(pts[n + 1])
        f.append(arrow(x1, y1, x2, y2, color=FIELD, sw=2.0))
    sx, sy = tp(pts[0])
    f.append(circle(sx, sy, 5, fill=POS, stroke=POS, sw=1))
    f.append(text(cx, cy - R - 34, "хвіст-до-голови", 15, INK, "middle", bold=True))
    f.append(text(cx, cy - R - 15, "многокутник замикається", 11.5, MUTED, "middle"))
    f.append(text(cx, cy + R + 30, "старт = кінець", 11.5, POS, "middle"))
    f.append(text(cx, cy + R + 50, "Σ = 0", 15, FIELD, "middle", bold=True))

    f.append(text(W / 2, H - 16,
                  "Скалярний добуток базисів ДПФ = сума коренів з одиниці: збіжні дають N, рівновіддалені гасяться в нуль.",
                  11.5, INK, "middle", bold=True))

    render(os.path.join(IMG, "roots-sum.svg"), W, H, *f,
           title="Дискретна ортогональність: корені з одиниці складаються в нуль")


# ── 7. Циклічний префікс: лінійна згортка каналу стає кільцевою ────────────────
# Той самий відлік y[0]: без префікса його другий доданок береться з невідомого
# хвоста попереднього символу (ISI); циклічний префікс кладе туди власний x₃ —
# і лінійна згортка збігається з кільцевою. Приклад N=4, канал h=[1, 0.5].
def fig_cyclic_prefix():
    W, H = 1000, 500
    f = []
    cw, ch = 60, 46
    bx = 250                 # ліва межа тіла символу (клітинка x₀)
    tailx = bx - cw          # «проблемний» відлік одразу зліва від x₀
    names = ["x₀", "x₁", "x₂", "x₃"]
    rxT = bx + 4 * cw + 40    # ліва межа підпису-результату праворуч

    def cell(x, y, label, fill, stroke, fs=13, tcol=INK):
        return fitbox(x, y, cw, ch, label, size=fs, fill=fill, stroke=stroke,
                      sw=1.6, bold=True, color=tcol, rx=5)

    def window(y):           # рамка вікна каналу для y[0]: (проблемний відлік, x₀)
        wx0, wx1 = tailx - 4, bx + cw + 4
        return [rect(wx0, y - 6, wx1 - wx0, ch + 12, fill="none", stroke=INK, sw=1.8, rx=8),
                text((wx0 + wx1) / 2, y + ch + 26, "вікно h=[1, 0.5] для y[0]", 11, INK, "middle", bold=True)]

    # ── верхній блок: БЕЗ префікса ──
    yA = 96
    f.append(text(70, yA - 22, "Без префікса", 14, POS, "start", bold=True))
    f.append(text(tailx - 26, yA + ch / 2 + 4, "…", 20, MUTED, "middle", bold=True))
    f.append(cell(tailx, yA, "хвіст\nпопер.", "#fbe9e6", POS, fs=10.5, tcol=POS))
    for i, nm in enumerate(names):
        f.append(cell(bx + i * cw, yA, nm, "#eef2f7", NEG))
    f.append(text(bx + 2 * cw, yA - 22, "тіло символу (N = 4)", 12, NEG, "middle", bold=True))
    for frag in window(yA):
        f.append(frag)
    f.append(text(rxT, yA + 6, "y[0] = 1·x₀ + 0.5·(хвіст попереднього)", 12, POS, "start", bold=True))
    f.append(text(rxT, yA + 27, "невідомий доданок →", 11, POS, "start"))
    f.append(text(rxT, yA + 44, "міжсимвольне спотворення (ISI)", 11, POS, "start"))

    # ── нижній блок: З циклічним префіксом ──
    yB = 300
    f.append(text(70, yB - 22, "З циклічним префіксом", 14, FIELD, "start", bold=True))
    f.append(text(tailx - 26, yB + ch / 2 + 4, "…", 20, MUTED, "middle", bold=True))
    f.append(cell(tailx, yB, "x₃\nкопія", "#eaf6ee", FIELD, fs=10.5, tcol=FIELD))
    for i, nm in enumerate(names):
        f.append(cell(bx + i * cw, yB, nm, "#eef2f7", NEG))
    f.append(text(bx + 2 * cw, yB - 22, "тіло символу (N = 4)", 12, NEG, "middle", bold=True))
    for frag in window(yB):
        f.append(frag)
    # копі-стрілка від x₃ (у тілі) до префікса
    src = bx + 3 * cw + cw / 2
    dst = tailx + cw / 2
    ctrl_y = yB - 64
    f.append('<path d="M%.1f,%.1f C %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" '
             'stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
             % (src, yB - 4, src, ctrl_y, dst, ctrl_y, dst, yB - 4, FIELD))
    f.append(text((src + dst) / 2, ctrl_y - 6, "копія хвоста → у префікс", 11, FIELD, "middle", bold=True))
    f.append(text(rxT, yB + 6, "y[0] = 1·x₀ + 0.5·x₃", 12.5, FIELD, "start", bold=True))
    f.append(text(rxT, yB + 27, "= 1·x₀ + 0.5·x[(0−1) mod 4]", 11.5, FIELD, "start"))
    f.append(text(rxT, yB + 44, "→ кільцева згортка, Yₖ = Hₖ·Xₖ", 11.5, FIELD, "start", bold=True))

    f.append(text(W / 2, H - 22,
                  "Префікс підставляє власний хвіст символу там, де згортка сягнула б у попередній символ — і лінійна згортка стає кільцевою.",
                  11.5, INK, "middle", bold=True))

    render(os.path.join(IMG, "cyclic-prefix.svg"), W, H, *f,
           title="Циклічний префікс: лінійна згортка каналу → кільцева")


# ── 8. BER: циклічний префікс проти багатопроменевості (для proj-ofdm-modem) ───
# Реальний Монте-Карло (5000 символів/точку) з модема вставки: канал 12 відліків,
# розкид затримок 11. З повним CP крива падає з SNR; без CP — застигає на підлозі.
def fig_ber_cp():
    W, H = 640, 460
    L, R, T, B = 80, 30, 54, 66
    px0, px1 = L, W - R
    py0, py1 = T, H - B
    ymin_e, ymax_e = -3, 0                 # BER 10⁻³ .. 10⁰

    SNR  = [0, 4, 8, 12, 16, 20, 24]
    CP16 = [2.03e-1, 1.17e-1, 5.54e-2, 2.36e-2, 1.02e-2, 5.19e-3, 2.43e-3]
    CP8  = [2.03e-1, 1.17e-1, 5.71e-2, 2.42e-2, 1.12e-2, 6.00e-3, 3.66e-3]
    CP0  = [2.15e-1, 1.35e-1, 7.83e-2, 4.83e-2, 3.58e-2, 3.15e-2, 2.93e-2]

    def X(s):   return px0 + (s - SNR[0]) / (SNR[-1] - SNR[0]) * (px1 - px0)
    def Y(ber): return py0 + (ymax_e - math.log10(ber)) / (ymax_e - ymin_e) * (py1 - py0)

    f = [rect(px0, py0, px1 - px0, py1 - py0, fill="#ffffff", stroke=MUTED, sw=1.2)]
    labels = {0: "10⁰", -1: "10⁻¹", -2: "10⁻²", -3: "10⁻³"}
    for e in range(ymin_e, ymax_e + 1):
        y = Y(10.0 ** e)
        f.append(line(px0, y, px1, y, color="#e6e9ed", sw=1))
        f.append(text(px0 - 12, y + 4, labels[e], size=13, color=MUTED, anchor="end"))
    for s in SNR:
        x = X(s)
        f.append(line(x, py0, x, py1, color="#f0f2f4", sw=1))
        f.append(text(x, py1 + 20, str(s), size=13, color=MUTED))

    def poly(ys, color, sw=2.6, dash=None):
        pts = " ".join("%.1f,%.1f" % (X(a), Y(b)) for a, b in zip(SNR, ys))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
                'stroke-linejoin="round"/>' % (pts, color, sw, d))

    def marks(ys, color):
        return "".join(circle(X(a), Y(b), 3.6, fill=color, stroke="#ffffff", sw=1.2)
                       for a, b in zip(SNR, ys))

    f.append(poly(CP0, POS))
    f.append(poly(CP8, MUTED, sw=2.0, dash="5 4"))
    f.append(poly(CP16, NEG))
    f.append(marks(CP0, POS))
    f.append(marks(CP16, NEG))

    f.append(text(px1 - 5, Y(2.93e-2) - 14, "без CP — підлога помилок", size=13,
                  color=POS, anchor="end", bold=True))
    f.append(text(px1 - 5, 300, "CP=8 (закороткий)", size=12, color=MUTED, anchor="end"))
    f.append(text(px1 - 5, Y(2.43e-3) + 18, "CP=16 (повний)", size=13, color=NEG,
                  anchor="end", bold=True))

    f.append(text((px0 + px1) / 2, H - 16, "SNR каналу, дБ", size=14, color=INK))
    f.append('<text x="22" y="%.1f" font-family="%s" font-size="14" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 22 %.1f)">частка помилкових бітів (BER)</text>'
             % ((py0 + py1) / 2, FONT, INK, (py0 + py1) / 2))
    render(os.path.join(IMG, "ber-cp.svg"), W, H, *f,
           title="Циклічний префікс проти багатопроменевості")


# ── 9. Сузір'я до і після вирівнювача (для proj-ofdm-modem) ────────────────────
# Один символ, SNR 12 дБ, повний CP. Ліворуч — канал повернув і розтягнув точки;
# праворуч — zero-forcing зняв викривлення, крім кількох найглибших провалів H.
def fig_constellation():
    W, H = 660, 380
    pan, T, gap = 250, 52, 66
    x0a = 40
    x0b = x0a + pan + gap
    lo, hi = -2.0, 2.0

    BEFORE = ((1.39,-0.95),(-1.42,-1.12),(-1.38,-0.19),(1.10,0.44),(0.12,-0.79),(0.46,0.49),
    (0.32,0.69),(-0.80,-0.69),(-0.80,-0.20),(-0.34,0.37),(-1.14,-0.66),(1.08,0.31),(0.92,0.08),
    (-0.43,-1.01),(0.69,-0.41),(0.36,0.26),(0.24,0.28),(0.26,-0.17),(0.15,0.32),(-0.11,-0.09),
    (-0.04,-0.16),(0.44,0.89),(0.88,0.60),(-0.28,1.25),(-0.42,-1.44),(0.64,-1.05),(-0.68,-0.52),
    (-0.30,-0.32),(-0.56,0.35),(0.16,-0.86),(-0.23,-0.39),(0.03,0.57),(-0.96,-0.09),(0.63,0.98),
    (1.34,-0.67),(-0.94,0.95),(0.71,-1.01),(1.43,0.78),(0.63,0.27),(-0.81,0.80),(-1.44,-0.50),
    (0.14,1.67),(1.65,-0.63),(0.78,-0.85),(0.26,0.07),(0.26,-0.20),(0.01,-0.37),(0.67,-0.14),
    (0.48,-0.73),(-0.51,-0.50),(0.77,0.02),(0.55,0.26),(-0.15,-0.27),(-0.04,0.04),(-0.05,0.10),
    (-0.50,0.15),(-0.38,0.72),(-0.14,0.43),(1.15,0.04),(-0.33,-0.74),(-0.09,-1.11),(-1.27,0.06),
    (0.01,1.75),(0.47,1.53))
    AFTER = ((0.68,-0.58),(-0.65,-0.79),(-0.77,-0.57),(0.58,1.00),(0.76,-0.89),(0.60,0.89),
    (0.43,0.90),(-0.89,-0.80),(-0.81,-0.27),(-0.37,0.30),(-0.80,-0.82),(0.67,0.65),(0.54,0.60),
    (0.67,-0.94),(0.92,0.75),(-0.24,0.97),(-0.19,0.95),(0.65,0.29),(-0.76,0.40),(0.37,0.01),
    (-0.08,0.29),(0.84,-0.81),(0.70,-0.63),(0.59,0.79),(-0.80,-0.86),(0.41,-1.03),(-0.79,-0.59),
    (-0.48,-0.46),(-0.74,0.80),(-0.32,-1.33),(-0.56,-0.31),(0.43,0.53),(-0.79,0.44),(0.77,0.45),
    (0.77,-0.67),(-0.62,0.66),(0.63,-0.66),(1.04,0.88),(0.48,0.32),(-0.71,0.46),(-0.74,-0.68),
    (-0.64,0.87),(0.95,0.84),(0.86,0.69),(-0.30,0.34),(-1.50,1.37),(-0.95,-0.71),(1.01,-0.73),
    (0.69,-1.18),(-0.64,-0.95),(1.28,0.51),(0.76,1.00),(0.15,-0.79),(-0.25,-0.05),(1.41,-0.99),
    (0.65,1.28),(0.97,0.82),(0.35,0.42),(0.99,-0.91),(-0.91,-0.44),(-1.04,-0.82),(-0.69,0.90),
    (0.77,0.89),(0.60,0.67))

    def panel(x0, pts, caption, ideal):
        def PX(v): return x0 + (v - lo) / (hi - lo) * pan
        def PY(v): return T + (hi - v) / (hi - lo) * pan
        g = [rect(x0, T, pan, pan, fill="#ffffff", stroke=MUTED, sw=1.2)]
        g.append(line(PX(lo), PY(0), PX(hi), PY(0), color="#cfd4da", sw=1))
        g.append(line(PX(0), PY(lo), PX(0), PY(hi), color="#cfd4da", sw=1))
        g.append(text(PX(hi) - 8, PY(0) - 6, "I", size=12, color=MUTED, anchor="end"))
        g.append(text(PX(0) + 12, PY(hi) + 13, "Q", size=12, color=MUTED, anchor="start"))
        if ideal:
            for sx in (-1, 1):
                for sy in (-1, 1):
                    g.append(plus(PX(sx * 0.7071), PY(sy * 0.7071), r=8))
        col = NEG if ideal else POS
        for (re, im) in pts:
            g.append(circle(PX(re), PY(im), 3.0, fill=col, stroke="#ffffff", sw=0.8))
        g.append(text(x0 + pan / 2, T + pan + 26, caption, size=13, color=INK, bold=True))
        return g

    f = []
    f += panel(x0a, BEFORE, "до вирівнювача: Xˆ = FFT(y)", ideal=False)
    f += panel(x0b, AFTER, "після zero-forcing: Xˆ / H", ideal=True)
    f.append(arrow(x0a + pan + 8, T + pan / 2, x0b - 8, T + pan / 2))
    f.append(text((x0a + pan + x0b) / 2, T + pan / 2 - 12, "÷ H", size=14, color=FIELD, bold=True))
    render(os.path.join(IMG, "constellation.svg"), W, H, *f,
           title="Приймач знімає викривлення каналу — крім найглибших провалів")


if __name__ == "__main__":
    fig_split()
    fig_orthogonal()
    fig_chain()
    fig_oscbank()
    fig_timeline()
    fig_roots_sum()
    fig_cyclic_prefix()
    fig_ber_cp()
    fig_constellation()
    print("OK: figures written to", IMG)
