# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 31 — «Спектр і перетворення Фур'є» (Модуль 5).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Поточний файл покриває історичну вставку (Рис. 31.0.k): струнні моди Бернуллі,
прямокутна хвиля із синусоїд, згасання теплових мод, явище Ґіббса, таймлайн,
спадок ідеї Фур'є. Усі криві рахуються чесно (часткові суми рядів Фур'є).
Спільні помічники — у стилі Розділів 28–30.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
GOLD  = "#caa24a"
PURP  = "#9a4ea8"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    if weight == "italic":
        weight, style = "normal", "italic"
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def dot(cx, cy, r=5, fill=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def poly(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def polygon(pts, fill=INK, stroke="none", sw=1):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("  saved", name)


def _pt(x0, y0, w, ht, xv, uv):
    return (x0 + xv * w, y0 - uv * ht)


def _plot_path(x0, y0, w, ht, pts_norm, color, sw=2.4, dash=None):
    return poly([_pt(x0, y0, w, ht, xv, uv) for (xv, uv) in pts_norm], color, sw, dash=dash)


def axes(x0, y0, w, ht, color=INK):
    return arrow(x0, y0, x0, y0 - ht, color, 1.6) + arrow(x0, y0, x0 + w, y0, color, 1.6)


# ──────────────────────────────────────────────────────────────────────────
#  Часткові суми рядів Фур'є для прямокутної хвилі (чесний розрахунок)
# ──────────────────────────────────────────────────────────────────────────

def _square(x):
    return 1.0 if (x % (2 * math.pi)) < math.pi else -1.0


def _square_partial(x, m):
    """Сума m непарних гармонік: (4/π)·Σ sin((2i+1)x)/(2i+1)."""
    v = 0.0
    for i in range(m):
        k = 2 * i + 1
        v += math.sin(k * x) / k
    return (4.0 / math.pi) * v


# ════════════════════════════════════════════════════════════════════════════
#  §31.0 Історія — Фур'є й рівняння теплоти
# ════════════════════════════════════════════════════════════════════════════

def fig_string_modes():
    w, h = 720, 430
    s = header(w, h)
    s += text(w / 2, 26, "Рух струни = сума синусоїдальних гармонік (Бернуллі, 1753)",
              13.5, INK, "middle", "bold")
    x0, xw, amp = 150, 430, 34
    rows = [
        (78,  "форма струни", INK,  None),
        (170, "основний тон", GREEN, 1),
        (260, "2-га гармоніка", BLUE, 2),
        (350, "3-тя гармоніка", PURP, 3),
    ]
    for (yb, lbl, col, n) in rows:
        s += line(x0, yb, x0 + xw, yb, FAINT, 1.2)
        s += dot(x0, yb, 3, INK)
        s += dot(x0 + xw, yb, 3, INK)
        if n is None:
            pts = []
            for k in range(101):
                xx = k / 100.0
                yy = xx / 0.35 if xx < 0.35 else (1 - xx) / 0.65
                pts.append((x0 + xx * xw, yb - yy * amp))
            s += poly(pts, col, 2.6)
        else:
            pts = [(x0 + (k / 100.0) * xw, yb - math.sin(n * math.pi * k / 100.0) * amp)
                   for k in range(101)]
            s += poly(pts, col, 2.4)
        s += text(x0 + xw + 12, yb + 4, lbl, 10.5, col, "start", "bold")
    s += text(x0 - 30, 130, "=", 22, INK, "middle", "bold")
    s += text(x0 - 30, 220, "+", 20, INK, "middle", "bold")
    s += text(x0 - 30, 310, "+", 20, INK, "middle", "bold")
    s += text(x0 - 30, 392, "+ …", 13, GREY, "middle", "bold")
    s += text(w / 2, 414, "кожна мода — окрема «нота»; разом вони складають усю форму",
              10.5, GREY, "middle", "italic")
    save("fig-31-0-1-string-modes.svg", s)


def fig_square_from_sines():
    w, h = 700, 320
    s = header(w, h)
    s += text(w / 2, 26, "Прямокутна хвиля як сума непарних гармонік", 14.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 250, 560, 180
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    N = 240
    xs = [2 * math.pi * j / N for j in range(N + 1)]
    s += _plot_path(x0, y0, pw, ph, [(j / N, 0.5 + 0.42 * _square(x)) for j, x in enumerate(xs)],
                    FAINT, 2.0)
    for (m, col, lbl) in [(1, PURP, "1 гармоніка"), (3, BLUE, "3 гармоніки"), (9, GREEN, "9 гармонік")]:
        s += _plot_path(x0, y0, pw, ph,
                        [(j / N, 0.5 + 0.42 * _square_partial(x, m)) for j, x in enumerate(xs)],
                        col, 2.0)
    s += text(x0 + pw - 120, 60, "1 гармоніка", 10.5, PURP, "start", "bold")
    s += text(x0 + pw - 120, 76, "3 гармоніки", 10.5, BLUE, "start", "bold")
    s += text(x0 + pw - 120, 92, "9 гармонік", 10.5, GREEN, "start", "bold")
    s += text(w / 2, 302, "що більше доданків (ваги 1, ⅓, ⅕, …), то ближче до прямокутника",
              10.5, GREY, "middle", "italic")
    save("fig-31-0-2-square-from-sines.svg", s)


def fig_heat_modes():
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Синусоїдальні моди тепла згасають окремо; високі — найшвидше",
              13.5, INK, "middle", "bold")
    modes = [(1, 1.0), (3, 0.45), (5, 0.30), (7, 0.22)]

    def profile(x, t):
        v = 0.0
        for (n, a) in modes:
            v += a * math.sin(n * math.pi * x) * math.exp(-0.6 * (n ** 2) * t)
        return v

    panels = [(60, 0.0, "t = 0  (нерівний профіль)", RED),
              (390, 0.25, "за мить пізніше (плавний)", GREEN)]
    pw, ph, N = 270, 170, 160
    for (x0, t, lbl, col) in panels:
        y0 = 240
        zl = y0 - ph / 2
        s += rect(x0 - 8, 70, pw + 16, ph + 6, fill="#fcfcfc", stroke=FAINT, sw=1.2, rx=8)
        s += line(x0, zl, x0 + pw, zl, FAINT, 1.2)
        s += text(x0 + pw / 2, 60, lbl, 11.5, col, "middle", "bold")
        s += _plot_path(x0, zl, pw, ph / 2,
                        [(j / N, profile(j / N, t) / 1.6) for j in range(N + 1)], col, 2.4)
    s += arrow(332, 155, 386, 155, INK, 2)
    s += text(359, 143, "час", 10, GREY, "middle", "italic")
    s += text(w / 2, 288, "розклавши профіль на моди, кожну пускаємо згасати окремо: e^(−α·n²·t)",
              10.5, GREY, "middle", "italic")
    save("fig-31-0-3-heat-modes.svg", s)


def fig_gibbs():
    w, h = 700, 320
    s = header(w, h)
    s += text(w / 2, 26, "Явище Ґіббса: на стрибку сума «перестрибує» край (~9%)",
              13.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 250, 560, 180
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    N = 480
    xs = [2 * math.pi * j / N for j in range(N + 1)]
    s += _plot_path(x0, y0, pw, ph, [(j / N, 0.5 + 0.40 * _square(x)) for j, x in enumerate(xs)],
                    FAINT, 2.0)
    s += _plot_path(x0, y0, pw, ph,
                    [(j / N, 0.5 + 0.40 * _square_partial(x, 20)) for j, x in enumerate(xs)],
                    BLUE, 1.8)
    ox = x0 + 0.5 * pw
    s += text(ox + 14, 66, "викид ≈9 %", 11, RED, "start", "bold")
    s += arrow(ox + 30, 74, ox - 4, 86, RED, 1.6)
    s += text(w / 2, 302, "хоч скільки додавай гармонік, «вушко» не зникає — лише вужчає",
              10.5, GREY, "middle", "italic")
    save("fig-31-0-4-gibbs.svg", s)


def fig_timeline():
    w, h = 800, 270
    s = header(w, h)
    s += text(w / 2, 26, "Двісті п'ятдесят років однієї думки", 15, INK, "middle", "bold")
    y = 150
    s += line(36, y, 760, y, INK, 2)
    s += arrow(744, y, 772, y, INK, 2)
    events = [("1747", "хвильове р-ня", "(д'Аламбер)", BLUE, -1),
              ("1753", "гармоніки струни", "(Бернуллі)", PURP, 1),
              ("1807", "мемуар Фур'є", "відмова Лагранжа", RED, -1),
              ("1822", "«Теорія тепла»", "книга Фур'є", GREEN, 1),
              ("1829", "строге доведення", "(Діріхле)", GOLD, -1),
              ("1965", "ШПФ / FFT", "(Кулі, Тьюкі)", BLUE, 1),
              ("нині", "DSP усюди", "МК · MP3 · МРТ", INK, -1)]
    n = len(events)
    for i, (yr, t1, t2, col, side) in enumerate(events):
        x = 70 + i * (660 / (n - 1))
        s += dot(x, y, 6, col)
        if side < 0:
            s += line(x, y - 6, x, y - 30, col, 1.4, dash="3,3")
            s += text(x, y - 58, yr, 12.5, col, "middle", "bold")
            s += text(x, y - 43, t1, 9.5, INK, "middle", "bold")
            s += text(x, y - 31, t2, 8.5, GREY, "middle", "italic")
        else:
            s += line(x, y + 6, x, y + 30, col, 1.4, dash="3,3")
            s += text(x, y + 46, yr, 12.5, col, "middle", "bold")
            s += text(x, y + 61, t1, 9.5, INK, "middle", "bold")
            s += text(x, y + 73, t2, 8.5, GREY, "middle", "italic")
    save("fig-31-0-5-timeline.svg", s)


def fig_legacy():
    w, h = 760, 300
    s = header(w, h)
    s += text(w / 2, 26, "Спадок однієї ідеї: розклад на синусоїди — всюди", 14.5, INK, "middle", "bold")
    cx, cy = 110, 162
    s += circle(cx, cy, 50, fill="#eef5ee", stroke=GREEN, w=2.4)
    s += text(cx, cy - 4, "ідея", 13, GREEN, "middle", "bold")
    s += text(cx, cy + 15, "Фур'є", 13, GREEN, "middle", "bold")
    cards = [("спектроаналізатор", BLUE), ("MP3 / AAC — звук", PURP), ("JPEG — зображення", GOLD),
             ("МРТ — томографія", RED), ("Wi-Fi / 5G (OFDM)", BLUE), ("цифрові фільтри", GREEN)]
    cols, rows, bw, bh = [300, 540], [66, 144, 222], 200, 52
    for i, (lbl, col) in enumerate(cards):
        x = cols[i % 2]
        yy = rows[i // 2]
        s += arrow(cx + 50, cy, x - 6, yy + bh / 2, col, 1.5)
        s += rect(x, yy, bw, bh, fill="#fbfbfb", stroke=col, sw=1.6, rx=8)
        s += text(x + bw / 2, yy + bh / 2 + 5, lbl, 11.5, col, "middle", "bold")
    s += text(w / 2, 292, "усе це — прямі нащадки «Аналітичної теорії тепла» (1822)",
              10.5, GREY, "middle", "italic")
    save("fig-31-0-6-legacy.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §31.1 Сигнал у часі й частоті: дві мови
# ════════════════════════════════════════════════════════════════════════════

def _spectrum(x0, ybase, pw, ph, bars, col):
    """Намалювати спектр: вертикальні стовпчики bars=[(fx∈[0,1], hh∈[0,1], підпис)]."""
    s = arrow(x0, ybase, x0, ybase - ph - 14, INK, 1.4)
    s += arrow(x0, ybase, x0 + pw + 10, ybase, INK, 1.4)
    for (fx, hh, lbl) in bars:
        x = x0 + fx * pw
        s += line(x, ybase, x, ybase - hh * ph, col, 5)
        if lbl:
            s += text(x, ybase + 14, lbl, 9.5, GREY, "middle")
    return s


def fig_two_languages():
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Один сигнал — дві мови: осцилограма й спектр", 14.5, INK, "middle", "bold")
    tx, tyc, tpw, tph = 60, 150, 275, 60
    s += line(tx, tyc, tx + tpw, tyc, FAINT, 1.2)
    s += arrow(tx, tyc, tx, tyc - tph - 18, INK, 1.4)
    pts = [(j / 200.0, (0.6 * math.sin(2 * math.pi * 2 * j / 200) +
                        0.4 * math.sin(2 * math.pi * 6 * j / 200)) / 1.1) for j in range(201)]
    s += _plot_path(tx, tyc, tpw, tph, pts, BLUE, 2.2)
    s += text(tx + tpw / 2, 252, "часова область", 12, BLUE, "middle", "bold")
    s += text(tx + tpw / 2, 270, "амплітуда від часу", 9.5, GREY, "middle", "italic")
    s += text(tx + tpw + 6, tyc + 14, "час →", 9.5, INK, "start")
    s += arrow(348, 150, 398, 150, INK, 2)
    s += text(373, 140, "Фур'є", 9.5, GREY, "middle", "italic")
    s += _spectrum(410, 205, 250, 120, [(0.25, 0.85, "2 Гц"), (0.75, 0.57, "6 Гц")], GREEN)
    s += text(535, 252, "частотна область", 12, GREEN, "middle", "bold")
    s += text(535, 270, "скільки кожної частоти", 9.5, GREY, "middle", "italic")
    save("fig-31-1-1-two-languages.svg", s)


def fig_tone_chord():
    w, h = 720, 340
    s = header(w, h)
    s += text(w / 2, 24, "Чистий тон — один пік; акорд — кілька піків", 14.5, INK, "middle", "bold")
    tx, tpw = 60, 275
    yc1 = 100
    s += text(tx, yc1 - 60, "чистий тон (1 нота)", 11, BLUE, "start", "bold")
    s += line(tx, yc1, tx + tpw, yc1, FAINT, 1.2)
    s += _plot_path(tx, yc1, tpw, 44, [(j / 200.0, math.sin(2 * math.pi * 3 * j / 200)) for j in range(201)], BLUE, 2.2)
    s += _spectrum(410, yc1 + 48, 250, 92, [(0.5, 0.85, "f₀")], GREEN)
    yc2 = 250
    s += text(tx, yc2 - 60, "акорд (3 ноти)", 11, BLUE, "start", "bold")
    s += line(tx, yc2, tx + tpw, yc2, FAINT, 1.2)
    chord = [(j / 200.0, (math.sin(2 * math.pi * 3 * j / 200) +
                          math.sin(2 * math.pi * 4 * j / 200) +
                          math.sin(2 * math.pi * 5 * j / 200)) / 3.0) for j in range(201)]
    s += _plot_path(tx, yc2, tpw, 44, chord, BLUE, 2.2)
    s += _spectrum(410, yc2 + 48, 250, 92, [(0.34, 0.85, "f₁"), (0.5, 0.85, "f₂"), (0.66, 0.85, "f₃")], GREEN)
    save("fig-31-1-2-tone-chord.svg", s)


def fig_hidden_hum():
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Прихована завада: час ховає — частота викриває", 14, INK, "middle", "bold")
    tx, tyc, tpw, tph = 55, 150, 290, 62

    def sig(x):
        return (0.45 * math.sin(2 * math.pi * 2 * x) +
                0.40 * math.sin(2 * math.pi * 50 * x) +
                0.12 * math.sin(2 * math.pi * 83 * x + 1.0))

    s += line(tx, tyc, tx + tpw, tyc, FAINT, 1.2)
    N = 500
    s += _plot_path(tx, tyc, tpw, tph, [(j / N, sig(j / N) / 1.05) for j in range(N + 1)], BLUE, 1.4)
    s += text(tx + tpw / 2, 252, "часова область — суцільна каша", 11, BLUE, "middle", "bold")
    s += arrow(358, 150, 398, 150, INK, 2)
    fx0, fyb, fpw, fph = 410, 205, 260, 120
    grass = [(0.10, 0.07, ""), (0.20, 0.05, ""), (0.40, 0.06, ""), (0.62, 0.05, ""), (0.95, 0.06, "")]
    s += _spectrum(fx0, fyb, fpw, fph, grass + [(0.03, 0.50, "2 Гц"), (0.78, 0.92, "50 Гц")], GREEN)
    s += line(fx0 + 0.78 * fpw, fyb, fx0 + 0.78 * fpw, fyb - 0.92 * fph, RED, 5)
    s += text(fx0 + 0.78 * fpw, fyb - 0.92 * fph - 6, "гул!", 9.5, RED, "middle", "bold")
    s += text(fx0 + fpw / 2, 252, "частотна область — гул як на долоні", 11, GREEN, "middle", "bold")
    save("fig-31-1-3-hidden-hum.svg", s)


def fig_transform_mirror():
    w, h = 720, 240
    s = header(w, h)
    s += text(w / 2, 26, "Оборотний місток між мовами", 15, INK, "middle", "bold")
    by, bh, bw = 80, 90, 180
    for (x, fill, col, t1, t2) in [(40, "#eef3fb", BLUE, "СИГНАЛ", "у часі"),
                                   (270, "#eef7ef", GREEN, "СПЕКТР", "у частоті"),
                                   (500, "#eef3fb", BLUE, "СИГНАЛ", "у часі")]:
        s += rect(x, by, bw, bh, fill=fill, stroke=col, sw=2, rx=10)
        s += text(x + bw / 2, by + 36, t1, 12.5, col, "middle", "bold")
        s += text(x + bw / 2, by + 58, t2, 11, col, "middle", "bold")
    s += arrow(222, by + bh / 2, 268, by + bh / 2, INK, 2)
    s += text(245, by + bh / 2 - 10, "Фур'є", 10, INK, "middle", "bold")
    s += arrow(452, by + bh / 2, 498, by + bh / 2, INK, 2)
    s += text(475, by + bh / 2 - 10, "обернене", 9, INK, "middle", "bold")
    s += text(w / 2, 212, "переклад туди й назад — точний, без утрати інформації", 10.5, GREY, "middle", "italic")
    save("fig-31-1-4-transform-mirror.svg", s)


def fig_canonical_pairs():
    w, h = 720, 430
    s = header(w, h)
    s += text(w / 2, 24, "Чотири опорні пари «час ↔ частота»", 14.5, INK, "middle", "bold")
    tx, tpw = 70, 235
    fx0, fpw = 420, 235
    labels = ["1) синусоїда → один пік", "2) стала (DC) → пік на 0 Гц",
              "3) клац (імпульс) → рівний спектр", "4) шум → широкий килим"]
    kinds = ["sine", "dc", "click", "noise"]
    for r, (lbl, kind) in enumerate(zip(labels, kinds)):
        yc = 92 + r * 86
        s += text(tx, yc - 44, lbl, 11, INK, "start", "bold")
        s += line(tx, yc, tx + tpw, yc, FAINT, 1.0)
        if kind == "sine":
            pts = [(j / 200.0, 0.8 * math.sin(2 * math.pi * 3 * j / 200)) for j in range(201)]
        elif kind == "dc":
            pts = [(j / 200.0, 0.6) for j in range(201)]
        elif kind == "click":
            pts = [(j / 200.0, 0.9 if abs(j - 100) < 2 else 0.0) for j in range(201)]
        else:
            pts = [(j / 200.0, (math.sin(11 * 6.28 * j / 200) +
                                math.sin(19 * 6.28 * j / 200 + 1) +
                                math.sin(29 * 6.28 * j / 200 + 2)) / 3.0) for j in range(201)]
        s += _plot_path(tx, yc, tpw, 32, pts, BLUE, 1.8)
        fb = yc + 34
        if kind == "sine":
            bars = [(0.5, 0.9, "")]
        elif kind == "dc":
            bars = [(0.0, 0.9, "0")]
        elif kind == "click":
            bars = [(i / 14.0, 0.5, "") for i in range(15)]
        else:
            bars = [(i / 14.0, 0.35 + 0.12 * math.sin(i * 1.7), "") for i in range(15)]
        s += _spectrum(fx0, fb, fpw, 52, bars, GREEN)
        s += arrow(tx + tpw + 18, yc, fx0 - 8, fb - 26, INK, 1.6)
    save("fig-31-1-5-canonical-pairs.svg", s)


def fig_which_domain():
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Яка мова під яке питання", 15, INK, "middle", "bold")
    s += rect(40, 52, 300, 38, fill="#eef3fb", stroke=BLUE, sw=1.8, rx=8)
    s += text(190, 76, "ЧАСОВА — питання «коли»", 12, BLUE, "middle", "bold")
    s += rect(380, 52, 300, 38, fill="#eef7ef", stroke=GREEN, sw=1.8, rx=8)
    s += text(530, 76, "ЧАСТОТНА — питання «що за тон»", 11, GREEN, "middle", "bold")
    timeq = ["коли стався удар?", "який різкий фронт?", "як швидко наростає?", "як міняється рівень?"]
    freqq = ["які тони всередині?", "чи є прихований період?", "де гул-завада?", "як стиснути сигнал?"]
    for i, (q1, q2) in enumerate(zip(timeq, freqq)):
        y = 114 + i * 42
        s += text(60, y, "• " + q1, 11.5, INK, "start")
        s += text(400, y, "• " + q2, 11.5, INK, "start")
    s += text(w / 2, 292, "постав питання спершу — воно й вибере мову", 10.5, GREY, "middle", "italic")
    save("fig-31-1-6-which-domain.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §31.2 Ідея Фур'є: будь-який сигнал = сума синусоїд
# ════════════════════════════════════════════════════════════════════════════

def fig_sinusoid_anatomy():
    w, h = 700, 300
    s = header(w, h)
    s += text(w / 2, 26, "Анатомія синусоїди: частота, амплітуда, фаза", 14.5, INK, "middle", "bold")
    x0, yc, pw, A = 70, 165, 560, 68
    f, ph = 2.0, 0.6
    s += line(x0, yc, x0 + pw, yc, FAINT, 1.4, dash="5,4")
    s += arrow(x0, yc, x0 + pw + 10, yc, INK, 1.4)
    s += text(x0 + pw + 8, yc + 16, "час", 9.5, INK, "start")
    pts = [(x0 + (k / 300.0) * pw, yc - A * math.sin(2 * math.pi * f * (k / 300.0) + ph)) for k in range(301)]
    s += poly(pts, BLUE, 2.4)
    x_p1 = (math.pi / 2 - ph) / (2 * math.pi * f)
    x_p2 = x_p1 + 1.0 / f
    px1, px2 = x0 + x_p1 * pw, x0 + x_p2 * pw
    s += arrow(px1, yc, px1, yc - A, RED, 1.8)
    s += arrow(px1, yc - A, px1, yc, RED, 1.8)
    s += text(px1 + 8, yc - A / 2, "A — амплітуда", 10.5, RED, "start", "bold")
    ytop = yc - A - 22
    s += line(px1, yc - A - 6, px1, ytop - 4, GREY, 1)
    s += line(px2, yc - A - 6, px2, ytop - 4, GREY, 1)
    s += arrow(px1, ytop, px2, ytop, GREEN, 1.8)
    s += arrow(px2, ytop, px1, ytop, GREEN, 1.8)
    s += text((px1 + px2) / 2, ytop - 8, "T — період (= 1/частота)", 10.5, GREEN, "middle", "bold")
    y_start = yc - A * math.sin(ph)
    s += dot(x0, y_start, 4, PURP)
    s += arrow(x0, yc + 42, x0, y_start + 6, PURP, 1.6)
    s += text(x0 - 2, yc + 58, "φ — фаза (зсув старту)", 10.5, PURP, "start", "bold")
    save("fig-31-2-1-sinusoid-anatomy.svg", s)


def fig_harmonics_ladder():
    w, h = 700, 400
    s = header(w, h)
    s += text(w / 2, 26, "Драбина гармонік: основна частота та її кратні", 14.5, INK, "middle", "bold")
    x0, xw, A = 210, 430, 30
    rows = [(80, "основна  f₀", GREEN, 1), (170, "2-га гармоніка  2f₀", BLUE, 2),
            (260, "3-тя гармоніка  3f₀", PURP, 3), (350, "4-та гармоніка  4f₀", "#9a7a1e", 4)]
    for (yb, lbl, col, n) in rows:
        s += line(x0, yb, x0 + xw, yb, FAINT, 1.2)
        pts = [(x0 + (k / 200.0) * xw, yb - A * math.sin(2 * math.pi * n * k / 200.0)) for k in range(201)]
        s += poly(pts, col, 2.2)
        s += text(x0 - 12, yb + 4, lbl, 10.5, col, "end", "bold")
    s += text(w / 2, 388, "лише ці частоти й беруть участь у періодичному сигналі", 10.5, GREY, "middle", "italic")
    save("fig-31-2-2-harmonics-ladder.svg", s)


def fig_synthesis_saw():
    w, h = 700, 320
    s = header(w, h)
    s += text(w / 2, 26, "Синтез: пилка зростає з кожною доданою гармонікою", 14, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 250, 560, 180
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")

    def saw(x, N):
        v = 0.0
        for k in range(1, N + 1):
            v += ((-1) ** (k + 1)) * math.sin(2 * math.pi * k * x) / k
        return (2 / math.pi) * v

    M = 300
    xs = [j / M for j in range(M + 1)]
    s += _plot_path(x0, y0, pw, ph, [(x, 0.5 + 0.42 * saw(x, 40)) for x in xs], FAINT, 2.0)
    for (N, col) in [(1, PURP), (2, BLUE), (3, "#9a7a1e"), (6, GREEN)]:
        s += _plot_path(x0, y0, pw, ph, [(x, 0.5 + 0.42 * saw(x, N)) for x in xs], col, 1.8)
    s += text(x0 + pw - 122, 56, "1 гарм.", 10, PURP, "start", "bold")
    s += text(x0 + pw - 122, 72, "2 гарм.", 10, BLUE, "start", "bold")
    s += text(x0 + pw - 122, 88, "3 гарм.", 10, "#9a7a1e", "start", "bold")
    s += text(x0 + pw - 122, 104, "6 гарм.", 10, GREEN, "start", "bold")
    s += text(w / 2, 302, "що більше гармонік, то ближче до ідеального «зуба»", 10.5, GREY, "middle", "italic")
    save("fig-31-2-3-synthesis-saw.svg", s)


def fig_recipe():
    w, h = 740, 300
    s = header(w, h)
    s += text(w / 2, 26, "Рецепт частот → зібраний сигнал", 14.5, INK, "middle", "bold")
    amps = [0.9, 0.0, 0.5, 0.0, 0.3]
    labels = ["f₀", "2f₀", "3f₀", "4f₀", "5f₀"]
    fxs = [0.12, 0.30, 0.48, 0.66, 0.84]
    s += _spectrum(60, 210, 250, 150, [(fx, a, "") for fx, a in zip(fxs, amps)], GREEN)
    for fx, lbl in zip(fxs, labels):
        s += text(60 + fx * 250, 226, lbl, 9.5, GREY, "middle")
    s += text(185, 250, "РЕЦЕПТ (спектр)", 11, GREEN, "middle", "bold")
    s += arrow(332, 138, 406, 138, INK, 2)
    s += text(369, 126, "синтез", 10, INK, "middle", "bold")
    tx, tyc, tpw, tph = 430, 138, 270, 58

    def dish(x):
        return 0.9 * math.sin(2 * math.pi * 1 * x) + 0.5 * math.sin(2 * math.pi * 3 * x) + 0.3 * math.sin(2 * math.pi * 5 * x)

    s += line(tx, tyc, tx + tpw, tyc, FAINT, 1.2)
    s += _plot_path(tx, tyc, tpw, tph, [(j / 300.0, dish(j / 300.0) / 1.7) for j in range(301)], BLUE, 2.2)
    s += text(tx + tpw / 2, 250, "СТРАВА (сигнал у часі)", 11, BLUE, "middle", "bold")
    save("fig-31-2-4-recipe.svg", s)


def fig_phase():
    w, h = 720, 320
    s = header(w, h)
    s += text(w / 2, 26, "Ті самі частоти, інша фаза — інша форма", 14.5, INK, "middle", "bold")
    x0, pw = 80, 560

    def wave(x, ph2):
        return (math.sin(2 * math.pi * 1 * x) + 0.6 * math.sin(2 * math.pi * 2 * x + ph2)) / 1.6

    yc1 = 112
    s += text(x0, yc1 - 58, "фаза 2-ї гармоніки = 0", 10.5, BLUE, "start", "bold")
    s += line(x0, yc1, x0 + pw, yc1, FAINT, 1.2)
    s += _plot_path(x0, yc1, pw, 52, [(j / 300.0, wave(j / 300.0, 0.0)) for j in range(301)], BLUE, 2.2)
    yc2 = 242
    s += text(x0, yc2 - 58, "фаза 2-ї гармоніки = 90°", 10.5, PURP, "start", "bold")
    s += line(x0, yc2, x0 + pw, yc2, FAINT, 1.2)
    s += _plot_path(x0, yc2, pw, 52, [(j / 300.0, wave(j / 300.0, math.pi / 2)) for j in range(301)], PURP, 2.2)
    s += text(w / 2, 302, "склад однаковий (f₀ + 2f₀), форми різні — це робить фаза", 10.5, GREY, "middle", "italic")
    save("fig-31-2-5-phase.svg", s)


def fig_analysis_synthesis():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Аналіз і синтез: розклав — зібрав", 15, INK, "middle", "bold")
    s += rect(50, 80, 200, 100, fill="#eef3fb", stroke=BLUE, sw=2, rx=10)
    s += text(150, 104, "сигнал у часі", 11.5, BLUE, "middle", "bold")
    s += _plot_path(70, 150, 160, 28, [(j / 100.0, math.sin(2 * math.pi * 2 * j / 100.0) * 0.8) for j in range(101)], BLUE, 1.8)
    s += rect(470, 80, 200, 100, fill="#eef7ef", stroke=GREEN, sw=2, rx=10)
    s += text(570, 104, "спектр (рецепт)", 11.5, GREEN, "middle", "bold")
    s += _spectrum(500, 168, 140, 52, [(0.25, 0.9, ""), (0.5, 0.5, ""), (0.75, 0.3, "")], GREEN)
    s += arrow(255, 110, 465, 110, INK, 2)
    s += text(360, 100, "АНАЛІЗ → перетворення Фур'є", 10.5, INK, "middle", "bold")
    s += arrow(465, 150, 255, 150, INK, 2)
    s += text(360, 168, "СИНТЕЗ ← обернене", 10.5, INK, "middle", "bold")
    s += text(w / 2, 238, "що розклали, те й зберемо назад — точно й без утрат", 10.5, GREY, "middle", "italic")
    save("fig-31-2-6-analysis-synthesis.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §31.3 Спектр: що він показує
# ════════════════════════════════════════════════════════════════════════════

def _grass(x0, y0, pw, ph, n, base, amp, seed=0):
    """Псевдовипадкова «підлога шуму»: n коротких стовпчиків (детерміновано)."""
    s = ""
    for i in range(n):
        fx = 0.04 + i * (0.92 / n)
        hh = base + amp * abs(math.sin((i + seed) * 1.7) + 0.6 * math.sin((i + seed) * 0.7))
        x = x0 + fx * pw
        s += line(x, y0, x, y0 - hh * ph, GREY, 2)
    return s


def fig_spectrum_anatomy():
    w, h = 720, 330
    s = header(w, h)
    s += text(w / 2, 26, "Як читати спектр", 15, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 250, 580, 182
    s += arrow(x0, y0, x0, y0 - ph - 16, INK, 1.6)
    s += arrow(x0, y0, x0 + pw + 12, y0, INK, 1.6)
    s += text(x0 - 10, y0 - ph - 4, "величина", 10.5, INK, "end", "bold")
    s += text(x0 + pw + 10, y0 + 18, "частота (Гц) →", 10.5, INK, "middle", "bold")
    s += _grass(x0, y0, pw, ph, 46, 0.05, 0.035)
    s += line(x0 + 0.02 * pw, y0, x0 + 0.02 * pw, y0 - 0.42 * ph, BLUE, 6)
    s += text(x0 + 0.02 * pw + 4, y0 + 16, "0 Гц (DC)", 9, BLUE, "start")
    px = x0 + 0.40 * pw
    s += line(px, y0, px, y0 - 0.85 * ph, GREEN, 6)
    s += text(px, y0 - 0.85 * ph - 8, "ПІК = тон", 11.5, GREEN, "middle", "bold")
    s += text(px, y0 + 16, "частота піка", 9, GREEN, "middle")
    s += arrow(px + 102, y0 - 0.55 * ph, px + 8, y0 - 0.55 * ph, INK, 1.3)
    s += text(px + 106, y0 - 0.55 * ph + 4, "висота = сила тону", 9.5, INK, "start")
    s += text(x0 + 0.76 * pw, y0 - 28, "підлога шуму", 10, GREY, "middle", "italic")
    s += arrow(x0 + 0.76 * pw, y0 - 26, x0 + 0.73 * pw, y0 - 7, GREY, 1.2)
    save("fig-31-3-1-spectrum-anatomy.svg", s)


def fig_peak_read():
    w, h = 740, 300
    s = header(w, h)
    s += text(w / 2, 26, "Положення = яка частота · Висота = наскільки сильна", 13.5, INK, "middle", "bold")
    s += _spectrum(60, 210, 260, 150, [(0.25, 0.8, "низький"), (0.72, 0.8, "високий")], GREEN)
    s += text(190, 250, "однакові за силою, різні частоти", 10.5, GREEN, "middle", "bold")
    s += text(190, 268, "висота та сама — положення різне", 9, GREY, "middle", "italic")
    s += _spectrum(420, 210, 260, 150, [(0.3, 0.85, "гучний"), (0.7, 0.45, "тихий")], BLUE)
    s += text(550, 250, "ті самі частоти, різна сила", 10.5, BLUE, "middle", "bold")
    s += text(550, 268, "положення те саме — висота різна", 9, GREY, "middle", "italic")
    save("fig-31-3-2-peak-read.svg", s)


def fig_noise_floor():
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Сигнал над шумом: SNR = висота піка над килимом", 13.5, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 240, 560, 180
    s += arrow(x0, y0, x0, y0 - ph - 16, INK, 1.6)
    s += arrow(x0, y0, x0 + pw + 12, y0, INK, 1.6)
    s += text(x0 + pw + 10, y0 + 18, "частота →", 10, INK, "middle", "bold")
    floor = 0.16
    for i in range(50):
        fx = 0.04 + i * (0.92 / 50)
        hh = floor * (0.6 + 0.5 * abs(math.sin(i * 1.9) + 0.5 * math.sin(i * 0.6)))
        s += line(x0 + fx * pw, y0, x0 + fx * pw, y0 - hh * ph, GREY, 2)
    s += line(x0, y0 - floor * ph, x0 + pw, y0 - floor * ph, GOLD, 1.2, dash="5,4")
    s += text(x0 + pw - 2, y0 - floor * ph - 4, "підлога шуму", 9.5, "#9a7a1e", "end", "italic")
    px = x0 + 0.45 * pw
    s += line(px, y0, px, y0 - 0.86 * ph, GREEN, 6)
    s += text(px, y0 - 0.86 * ph - 8, "сигнал", 11, GREEN, "middle", "bold")
    s += arrow(px + 24, y0 - floor * ph, px + 24, y0 - 0.86 * ph, RED, 1.6)
    s += arrow(px + 24, y0 - 0.86 * ph, px + 24, y0 - floor * ph, RED, 1.6)
    s += text(px + 30, y0 - 0.5 * ph, "SNR", 11, RED, "start", "bold")
    save("fig-31-3-3-noise-floor.svg", s)


def fig_linear_db():
    w, h = 740, 320
    s = header(w, h)
    s += text(w / 2, 26, "Лінійна шкала ховає слабке — децибели показують усе", 13.5, INK, "middle", "bold")
    fxs, amps = [0.2, 0.4, 0.6, 0.8], [1.0, 0.1, 0.03, 0.01]
    s += _spectrum(60, 250, 260, 170, [(fx, a, "") for fx, a in zip(fxs, amps)], GREEN)
    s += text(190, 278, "лінійна: видно лише головний", 10.5, GREEN, "middle", "bold")
    barsdb = []
    for fx, a in zip(fxs, amps):
        db = 20 * math.log10(a)
        barsdb.append((fx, max(0.02, (60 + db) / 60.0), ""))
    s += _spectrum(420, 250, 260, 170, barsdb, BLUE)
    s += text(550, 278, "децибели: видно і слабке", 10.5, BLUE, "middle", "bold")
    for db, lbl in [(0, "0"), (-20, "−20"), (-40, "−40")]:
        yy = 250 - ((60 + db) / 60.0) * 170
        s += line(420, yy, 680, yy, FAINT, 1, dash="4,4")
        s += text(414, yy + 3, lbl + " dB", 8.5, GREY, "end")
    save("fig-31-3-4-linear-db.svg", s)


def fig_harmonic_comb():
    w, h = 720, 320
    s = header(w, h)
    s += text(w / 2, 24, "Чистий тон — один пік; спотворений — гребінець гармонік", 13.5, INK, "middle", "bold")
    s += text(70, 58, "чистий синус → 1 пік", 11, GREEN, "start", "bold")
    s += _spectrum(70, 130, 580, 80, [(0.12, 0.9, "f₀")], GREEN)
    s += text(70, 218, "спотворений → пік + гармоніки", 11, PURP, "start", "bold")
    combs = [(0.12, 0.9, "f₀"), (0.24, 0.5, "2f₀"), (0.36, 0.62, "3f₀"), (0.48, 0.32, "4f₀"),
             (0.60, 0.4, "5f₀"), (0.72, 0.22, "6f₀"), (0.84, 0.26, "7f₀")]
    s += _spectrum(70, 290, 580, 80, combs, PURP)
    save("fig-31-3-5-harmonic-comb.svg", s)


def fig_read_real():
    w, h = 740, 330
    s = header(w, h)
    s += text(w / 2, 24, "Спектр як діагноз: читаємо особливості", 13.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 250, 600, 180
    s += arrow(x0, y0, x0, y0 - ph - 16, INK, 1.6)
    s += arrow(x0, y0, x0 + pw + 12, y0, INK, 1.6)
    s += text(x0 + pw + 10, y0 + 18, "частота →", 10, INK, "middle", "bold")
    s += _grass(x0, y0, pw, ph, 54, 0.06, 0.03)
    feats = [(0.015, 0.5, BLUE, "DC"), (0.12, 0.82, GREEN, "сигнал ~2 Гц"),
             (0.55, 0.70, RED, "50 Гц (гул)"), (0.78, 0.36, "#9a7a1e", "100 Гц (2-га)")]
    for fx, hh, col, lbl in feats:
        x = x0 + fx * pw
        s += line(x, y0, x, y0 - hh * ph, col, 6)
        s += text(x, y0 - hh * ph - 7, lbl, 9.5, col, "middle", "bold")
    s += text(x0 + 0.88 * pw, y0 - 24, "підлога шуму", 9.5, GREY, "middle", "italic")
    s += arrow(x0 + 0.88 * pw, y0 - 22, x0 + 0.85 * pw, y0 - 7, GREY, 1.2)
    save("fig-31-3-6-read-real.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §31.4 Дискретне перетворення Фур'є (ДПФ)
# ════════════════════════════════════════════════════════════════════════════

def fig_correlation():
    w, h = 720, 350
    s = header(w, h)
    s += text(w / 2, 24, "Серце ДПФ: помнож сигнал на еталон і додай усе", 14, INK, "middle", "bold")
    s += line(60, 44, 90, 44, BLUE, 2)
    s += text(94, 48, "сигнал", 9.5, BLUE, "start")
    s += line(176, 44, 206, 44, GREEN, 2, dash="4,3")
    s += text(210, 48, "еталон (частота, яку перевіряємо)", 9.5, GREEN, "start")
    s += line(478, 44, 508, 44, RED, 2.6)
    s += text(512, 48, "добуток", 9.5, RED, "start")
    x0, pw = 70, 520

    def row(yc, ftest, label, big):
        out = text(x0, yc - 52, label, 10.5, INK, "start", "bold")
        out += line(x0, yc, x0 + pw, yc, FAINT, 1.2)
        out += poly([(x0 + (k / 240.0) * pw, yc - 20 * math.sin(2 * math.pi * 3 * k / 240.0)) for k in range(241)], BLUE, 1.2)
        out += poly([(x0 + (k / 240.0) * pw, yc - 20 * math.sin(2 * math.pi * ftest * k / 240.0)) for k in range(241)], GREEN, 1.2, dash="4,3")
        out += poly([(x0 + (k / 240.0) * pw, yc - 28 * math.sin(2 * math.pi * 3 * k / 240.0) * math.sin(2 * math.pi * ftest * k / 240.0)) for k in range(241)], RED, 2.4)
        verdict = "Σ велика → частота Є" if big else "Σ ≈ 0 → частоти НЕМА"
        out += text(x0 + pw / 2, yc + 46, verdict, 11, (GREEN if big else GREY), "middle", "bold")
        return out

    s += row(150, 3, "еталон = частота сигналу (збіг):", True)
    s += row(290, 5, "еталон = інша частота (незбіг):", False)
    save("fig-31-4-1-correlation.svg", s)


def fig_bins():
    w, h = 740, 300
    s = header(w, h)
    s += text(w / 2, 26, "N відліків у часі → N/2 частотних бінів", 14.5, INK, "middle", "bold")
    x0, yc, pw = 50, 150, 300
    s += line(x0, yc, x0 + pw, yc, FAINT, 1.2)

    def sig(x):
        return 0.6 * math.sin(2 * math.pi * 2 * x) + 0.4 * math.sin(2 * math.pi * 5 * x)

    s += poly([(x0 + (k / 200.0) * pw, yc - 46 * sig(k / 200.0)) for k in range(201)], BLUE, 1.4)
    for i in range(16):
        xx = i / 15.0
        s += dot(x0 + xx * pw, yc - 46 * sig(xx), 3.2, INK)
    s += text(x0 + pw / 2, 252, "N відліків (час)", 11, BLUE, "middle", "bold")
    s += arrow(x0 + pw + 14, 150, x0 + pw + 74, 150, INK, 2)
    s += text(x0 + pw + 44, 138, "ДПФ", 10, INK, "middle", "bold")
    s += _spectrum(452, 210, 250, 150, [(0.0, 0.3, ""), (0.16, 0.85, ""), (0.4, 0.6, ""), (0.6, 0.2, ""), (0.8, 0.15, "")], GREEN)
    s += text(577, 252, "N/2+1 бінів (частота)", 11, GREEN, "middle", "bold")
    s += text(577, 270, "бін k ↔ fₖ = k·fs/N", 9.5, GREY, "middle", "italic")
    save("fig-31-4-2-bins.svg", s)


def fig_nyquist():
    w, h = 720, 330
    s = header(w, h)
    s += text(w / 2, 24, "Найквіст: треба щонайменше 2 відліки на період", 14, INK, "middle", "bold")
    x0, pw = 70, 580

    def row(yc, f, nsamp, label, col):
        out = text(x0, yc - 52, label, 10.5, col, "start", "bold")
        out += line(x0, yc, x0 + pw, yc, FAINT, 1.2)
        out += poly([(x0 + (k / 300.0) * pw, yc - 36 * math.sin(2 * math.pi * f * k / 300.0)) for k in range(301)], col, 1.8)
        for i in range(nsamp + 1):
            xx = i / float(nsamp)
            yy = yc - 36 * math.sin(2 * math.pi * f * xx)
            out += line(x0 + xx * pw, yy, x0 + xx * pw, yc, FAINT, 0.8)
            out += dot(x0 + xx * pw, yy, 3.4, INK)
        return out

    s += row(120, 2, 20, "повільне коливання: відліків удосталь → чітко", GREEN)
    s += row(272, 8, 16, "на межі: рівно 2 відліки на період (fs/2)", BLUE)
    save("fig-31-4-3-nyquist.svg", s)


def fig_resolution():
    w, h = 740, 320
    s = header(w, h)
    s += text(w / 2, 24, "Роздільність Δf = fs/N: довший запис розділяє близькі тони", 12.5, INK, "middle", "bold")
    x0, yb, pw, ph = 70, 150, 600, 86
    s += arrow(x0, yb, x0, yb - ph - 12, INK, 1.4)
    s += arrow(x0, yb, x0 + pw + 10, yb, INK, 1.4)

    def hump(fx):
        return math.exp(-((fx - 0.49) ** 2) / 0.0010) + math.exp(-((fx - 0.55) ** 2) / 0.0010)

    mx = max(hump(i / 300.0) for i in range(301))
    s += poly([(x0 + (i / 300.0) * pw, yb - (hump(i / 300.0) / mx) * ph * 0.9) for i in range(301)], "#9a7a1e", 2.4)
    s += text(x0 + pw - 6, yb - ph - 2, "короткий запис → один горб", 10, "#9a7a1e", "end", "bold")
    yb2 = 290
    s += arrow(x0, yb2, x0, yb2 - ph - 12, INK, 1.4)
    s += arrow(x0, yb2, x0 + pw + 10, yb2, INK, 1.4)
    s += line(x0 + 0.49 * pw, yb2, x0 + 0.49 * pw, yb2 - ph * 0.86, GREEN, 5)
    s += line(x0 + 0.55 * pw, yb2, x0 + 0.55 * pw, yb2 - ph * 0.86, GREEN, 5)
    s += text(x0 + pw - 6, yb2 - ph - 2, "довгий запис → два чіткі піки", 10, GREEN, "end", "bold")
    save("fig-31-4-4-resolution.svg", s)


def fig_aliasing():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Аліасинг: висока частота прикидається низькою", 14, INK, "middle", "bold")
    x0, yc, pw = 70, 150, 580
    s += line(x0, yc, x0 + pw, yc, FAINT, 1.2)
    s += poly([(x0 + (k / 300.0) * pw, yc - 46 * math.sin(2 * math.pi * 9 * k / 300.0)) for k in range(301)], GREY, 1.4)
    s += poly([(x0 + (k / 300.0) * pw, yc - 46 * math.sin(2 * math.pi * 1 * k / 300.0)) for k in range(301)], GREEN, 2.2)
    for i in range(9):
        xx = i / 8.0
        s += dot(x0 + xx * pw, yc - 46 * math.sin(2 * math.pi * 1 * xx), 4, RED)
    s += text(x0 + pw - 4, 66, "справжня (швидка)", 10, GREY, "end", "bold")
    s += text(x0 + pw - 4, 234, "уявна (повільна) — її й покаже ДПФ", 10, GREEN, "end", "bold")
    s += text(x0 + pw / 2, 264, "обидві проходять через ті самі відліки (червоні) — не розрізнити", 10, RED, "middle", "italic")
    save("fig-31-4-5-aliasing.svg", s)


def fig_cost():
    w, h = 700, 300
    s = header(w, h)
    s += text(w / 2, 26, "Ціна прямого ДПФ росте як N²", 14.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 250, 560, 190
    s += arrow(x0, y0, x0, y0 - ph - 12, INK, 1.6)
    s += arrow(x0, y0, x0 + pw + 12, y0, INK, 1.6)
    s += text(x0 + pw + 8, y0 + 18, "N (відліків) →", 10, INK, "middle", "bold")
    s += text(x0 - 8, y0 - ph - 2, "операцій", 10, INK, "end", "bold")
    Nmax = 64
    n2 = [(i / Nmax, (i ** 2) / float(Nmax ** 2)) for i in range(1, Nmax + 1)]
    s += _plot_path(x0, y0, pw, ph, n2, RED, 2.6)
    s += text(*(_pt(x0, y0, pw, ph, 0.6, 0.6)), "N² — пряме ДПФ", 11, RED, "start", "bold")
    nl = [(i / Nmax, (i * math.log2(i)) / (Nmax * math.log2(Nmax)) * 0.25) for i in range(2, Nmax + 1)]
    s += _plot_path(x0, y0, pw, ph, nl, GREEN, 2.0, dash="6,4")
    s += text(*(_pt(x0, y0, pw, ph, 0.5, 0.17)), "N·log N — розумніше (далі)", 10, GREEN, "start", "bold")
    s += text(w / 2, 288, "подвоїв N — учетверо більше роботи; для тисяч відліків це мільйони", 10, GREY, "middle", "italic")
    save("fig-31-4-6-cost.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §31.5 Швидке перетворення Фур'є (ШПФ/FFT)
# ════════════════════════════════════════════════════════════════════════════

def fig_divide():
    w, h = 720, 320
    s = header(w, h)
    s += text(w / 2, 26, "Розділяй і володарюй: парні й непарні відліки", 14.5, INK, "middle", "bold")
    x0, dx, y = 120, 60, 84
    s += text(x0 - 34, y + 4, "x[n]:", 10, INK, "end", "bold")
    for i in range(8):
        col = GREEN if i % 2 == 0 else BLUE
        s += dot(x0 + i * dx, y, 6, col)
        s += text(x0 + i * dx, y - 14, str(i), 9, col, "middle", "bold")
    s += rect(90, 184, 240, 60, fill="#eef7ef", stroke=GREEN, sw=1.8, rx=8)
    s += text(210, 209, "ДПФ парних", 11.5, GREEN, "middle", "bold")
    s += text(210, 228, "x[0],x[2],x[4],x[6]  (N/2)", 9.5, GREY, "middle")
    s += rect(390, 184, 240, 60, fill="#eef3fb", stroke=BLUE, sw=1.8, rx=8)
    s += text(510, 209, "ДПФ непарних", 11.5, BLUE, "middle", "bold")
    s += text(510, 228, "x[1],x[3],x[5],x[7]  (N/2)", 9.5, GREY, "middle")
    for i in range(0, 8, 2):
        s += arrow(x0 + i * dx, y + 8, 210, 182, GREEN, 1)
    for i in range(1, 8, 2):
        s += arrow(x0 + i * dx, y + 8, 510, 182, BLUE, 1)
    s += text(w / 2, 276, "ДПФ із N точок = дві ДПФ із N/2 + дешеве склеювання", 11, INK, "middle", "bold")
    s += text(w / 2, 297, "а кожну з них — знову навпіл… (рекурсія)", 10, GREY, "middle", "italic")
    save("fig-31-5-1-divide.svg", s)


def fig_butterfly():
    w, h = 680, 300
    s = header(w, h)
    s += text(w / 2, 26, "«Метелик»: дешеве склеювання двох половин", 14.5, INK, "middle", "bold")
    ex, oy1, oy2 = 130, 110, 210
    s += dot(ex, oy1, 5, GREEN)
    s += text(ex - 12, oy1 + 4, "E[k]", 11, GREEN, "end", "bold")
    s += dot(ex, oy2, 5, BLUE)
    s += text(ex - 12, oy2 + 4, "O[k]", 11, BLUE, "end", "bold")
    tx = 300
    s += arrow(ex + 6, oy2, tx - 18, oy2, BLUE, 1.6)
    s += circle(tx, oy2, 16, fill="#ffffff", stroke=PURP, w=1.8)
    s += text(tx, oy2 + 4, "×W", 9.5, PURP, "middle", "bold")
    oxr = 520
    s += arrow(ex + 6, oy1, oxr - 6, oy1, INK, 1.6)
    s += arrow(ex + 12, oy1 + 6, oxr - 6, oy2 - 6, INK, 1.3)
    s += arrow(tx + 16, oy2, oxr - 6, oy2, INK, 1.6)
    s += arrow(tx + 14, oy2 - 6, oxr - 6, oy1 + 6, INK, 1.3)
    s += dot(oxr, oy1, 5, INK)
    s += text(oxr + 12, oy1 + 4, "X[k] = E + W·O", 11, INK, "start", "bold")
    s += dot(oxr, oy2, 5, INK)
    s += text(oxr + 12, oy2 + 4, "X[k+N/2] = E − W·O", 11, INK, "start", "bold")
    s += text(oxr - 64, oy1 - 8, "+", 14, GREEN, "middle", "bold")
    s += text(oxr - 64, oy2 + 20, "−", 14, RED, "middle", "bold")
    s += text(w / 2, 274, "з двох входів — два виходи за одне множення   (W = e^(−j2π·k/N))", 10.5, GREY, "middle", "italic")
    save("fig-31-5-2-butterfly.svg", s)


def fig_recursion_tree():
    w, h = 720, 330
    s = header(w, h)
    s += text(w / 2, 24, "Чому N·log N: log₂N рівнів, по ~N роботи на кожному", 13, INK, "middle", "bold")
    yy = [68, 138, 208, 278]
    cols = [INK, BLUE, GREEN, PURP]
    counts = [1, 2, 4, 8]
    labels = ["N", "N/2", "N/4", "1"]
    bws = [60, 60, 46, 28]
    pos = [[70 + (j + 0.5) * (560.0 / counts[lvl]) for j in range(counts[lvl])] for lvl in range(4)]
    for lvl in range(3):
        for i, px in enumerate(pos[lvl]):
            for c in pos[lvl + 1][2 * i:2 * i + 2]:
                s += line(px, yy[lvl] + 15, c, yy[lvl + 1] - 15, FAINT, 1)
    for lvl in range(4):
        for x in pos[lvl]:
            s += rect(x - bws[lvl] / 2, yy[lvl] - 15, bws[lvl], 28, fill="#fbfbfb", stroke=cols[lvl], sw=1.4, rx=6)
            s += text(x, yy[lvl] + 5, labels[lvl], 10, cols[lvl], "middle", "bold")
        s += text(656, yy[lvl] + 5, "~N", 10, GREY, "start", "italic")
    s += text(w / 2, 314, "половинимо, поки не лишиться по 1 → рівнів log₂N, кожен коштує ~N → разом N·log₂N", 9.5, GREY, "middle", "italic")
    save("fig-31-5-3-recursion-tree.svg", s)


def fig_speedup_curve():
    w, h = 700, 300
    s = header(w, h)
    s += text(w / 2, 26, "ШПФ vs пряме ДПФ: та сама відповідь, незрівнянно швидше", 13, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 250, 560, 190
    s += arrow(x0, y0, x0, y0 - ph - 12, INK, 1.6)
    s += arrow(x0, y0, x0 + pw + 12, y0, INK, 1.6)
    s += text(x0 + pw + 8, y0 + 18, "N →", 10, INK, "middle", "bold")
    s += text(x0 - 8, y0 - ph - 2, "операцій", 10, INK, "end", "bold")
    Nmax = 64
    n2 = [(i / Nmax, (i ** 2) / float(Nmax ** 2)) for i in range(1, Nmax + 1)]
    s += _plot_path(x0, y0, pw, ph, n2, RED, 2.6)
    s += text(*(_pt(x0, y0, pw, ph, 0.5, 0.62)), "N² — пряме ДПФ", 11, RED, "start", "bold")
    nl = [(i / Nmax, (i * math.log2(i)) / float(Nmax ** 2)) for i in range(2, Nmax + 1)]
    s += _plot_path(x0, y0, pw, ph, nl, GREEN, 2.6)
    s += text(*(_pt(x0, y0, pw, ph, 0.6, 0.12)), "N·log N — ШПФ", 11, GREEN, "start", "bold")
    s += text(w / 2, 288, "що більший N, то приголомшливіший відрив на користь ШПФ", 10, GREY, "middle", "italic")
    save("fig-31-5-4-speedup-curve.svg", s)


def fig_speedup_bars():
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 26, "Виграш ШПФ росте з N", 14.5, INK, "middle", "bold")
    s += text(70, 70, "розмір", 10.5, INK, "start", "bold")
    s += text(260, 70, "пряме ДПФ (N²)", 10.5, RED, "middle", "bold")
    s += text(470, 70, "ШПФ (N·log N)", 10.5, GREEN, "middle", "bold")
    s += text(640, 70, "виграш", 10.5, INK, "middle", "bold")
    rows = [("N = 64", "4 096", "384", "~11×"),
            ("N = 1 024", "1 048 576", "10 240", "~100×"),
            ("N = 1 048 576", "~10¹²", "~2·10⁷", "~50 000×")]
    y = 110
    for (nm, dft, fft, win) in rows:
        s += text(70, y, nm, 11, INK, "start", "bold")
        s += text(260, y, dft, 11, RED, "middle")
        s += text(470, y, fft, 11, GREEN, "middle")
        s += text(640, y, win, 12, INK, "middle", "bold")
        s += line(60, y + 14, 680, y + 14, FAINT, 1)
        y += 46
    s += text(w / 2, 272, "для мільйона точок — у п'ятдесят тисяч разів менше роботи", 10.5, GREY, "middle", "italic")
    save("fig-31-5-5-speedup-bars.svg", s)


def fig_realtime():
    w, h = 740, 210
    s = header(w, h)
    s += text(w / 2, 26, "ШПФ у реальному часі на мікроконтролері", 14.5, INK, "middle", "bold")
    blocks = [("АЦП", "відліки", GREY), ("буфер N", "накопич.", BLUE),
              ("ШПФ", "спектр", GREEN), ("аналіз", "піки, гул", PURP)]
    bw, bh, by = 150, 70, 80
    xs = [30, 210, 390, 570]
    for (x, (t1, t2, col)) in zip(xs, blocks):
        s += rect(x, by, bw, bh, fill="#fbfbfb", stroke=col, sw=1.8, rx=10)
        s += text(x + bw / 2, by + 32, t1, 12.5, col, "middle", "bold")
        s += text(x + bw / 2, by + 52, t2, 10, GREY, "middle", "italic")
    for i in range(3):
        s += arrow(xs[i] + bw, by + bh / 2, xs[i + 1] - 4, by + bh / 2, INK, 2)
    s += text(w / 2, 188, "кілька рядків з бібліотеки (CMSIS-DSP, arduinoFFT) — і спектр оновлюється десятки разів на секунду", 9.5, GREY, "middle", "italic")
    save("fig-31-5-6-realtime.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §31.5 Історія — ШПФ (Кулі-Тьюкі, Ґаусс)
# ════════════════════════════════════════════════════════════════════════════

def fig_coldwar():
    w, h = 740, 280
    s = header(w, h)
    s += text(w / 2, 26, "Замовник ШПФ: виявлення підземних ядерних вибухів", 13.5, INK, "middle", "bold")
    gy = 95
    s += line(40, gy, 420, gy, INK, 2)
    s += text(44, gy - 6, "поверхня", 9, GREY, "start", "italic")
    bx, by = 150, 180
    for r in (35, 60, 85):
        s += circle(bx, by, r, fill="none", stroke=GOLD, w=1.2)
    s += dot(bx, by, 7, RED)
    s += text(bx, by + 22, "вибух", 9.5, RED, "middle", "bold")
    for sx in (90, 250, 360):
        s += polygon([(sx - 8, gy), (sx + 8, gy), (sx, gy - 16)], GREEN, INK, 1)
    s += text(250, gy - 24, "сейсмометри", 9.5, GREEN, "middle", "bold")
    s += arrow(424, gy, 470, gy, INK, 2)
    s += rect(474, 70, 110, 52, fill="#eef3fb", stroke=BLUE, sw=1.6, rx=8)
    s += text(529, 92, "ШПФ", 12, BLUE, "middle", "bold")
    s += text(529, 110, "спектр", 9, GREY, "middle", "italic")
    s += arrow(586, 96, 624, 96, INK, 2)
    s += rect(628, 66, 104, 60, fill="#ffffff", stroke=INK, sw=1.4, rx=8)
    s += text(680, 90, "вибух чи", 10, INK, "middle", "bold")
    s += text(680, 108, "землетрус?", 10, INK, "middle", "bold")
    s += text(w / 2, 256, "різні спектри вибуху й землетрусу видавали порушника — та прямий ДПФ не встигав", 9.5, GREY, "middle", "italic")
    save("fig-31-5h-1-coldwar.svg", s)


def fig_gauss_before_fourier():
    w, h = 680, 240
    s = header(w, h)
    s += text(w / 2, 28, "Парадокс: «швидке ПФ» старше за саме «ПФ»", 14, INK, "middle", "bold")
    y = 128
    s += line(80, y, 600, y, INK, 2)
    s += arrow(584, y, 612, y, INK, 2)
    s += dot(200, y, 7, GREEN)
    s += line(200, y - 6, 200, y - 46, GREEN, 1.4, dash="3,3")
    s += text(200, y - 56, "1805", 13, GREEN, "middle", "bold")
    s += text(200, y - 40, "Ґаусс: швидкий алгоритм (ШПФ)", 9.5, INK, "middle", "bold")
    s += text(200, y + 24, "орбіти астероїдів", 9, GREY, "middle", "italic")
    s += dot(420, y, 7, RED)
    s += line(420, y + 6, 420, y + 40, RED, 1.4, dash="3,3")
    s += text(420, y + 54, "1807", 13, RED, "middle", "bold")
    s += text(420, y + 70, "Фур'є оприлюднює ПФ", 9.5, INK, "middle", "bold")
    s += text(w / 2, 224, "алгоритм для прискорення ПФ з'явився за два роки до самого ПФ", 10, GREY, "middle", "italic")
    save("fig-31-5h-2-gauss-before-fourier.svg", s)


def fig_rediscoveries():
    w, h = 780, 260
    s = header(w, h)
    s += text(w / 2, 26, "Той самий алгоритм відкривали ~12 разів за 160 років", 13.5, INK, "middle", "bold")
    y = 150
    s += line(40, y, 720, y, INK, 2)
    s += arrow(704, y, 732, y, INK, 2)
    events = [(120, "1805", "Ґаусс", "астероїди", GREEN, -1),
              (320, "~1903", "Рунге", "", BLUE, 1),
              (470, "1942", "Даніельсон,", "Ланцош · кристали", PURP, -1),
              (660, "1965", "Кулі, Тьюкі", "тріумф!", RED, 1)]
    for (x, yr, n1, n2, col, side) in events:
        s += dot(x, y, 6, col)
        if side < 0:
            s += line(x, y - 6, x, y - 30, col, 1.2, dash="3,3")
            s += text(x, y - 50, yr, 12, col, "middle", "bold")
            s += text(x, y - 34, n1, 9.5, INK, "middle", "bold")
            if n2:
                s += text(x, y - 20, n2, 8.5, GREY, "middle", "italic")
        else:
            s += line(x, y + 6, x, y + 30, col, 1.2, dash="3,3")
            s += text(x, y + 46, yr, 12, col, "middle", "bold")
            s += text(x, y + 62, n1, 9.5, INK, "middle", "bold")
            if n2:
                s += text(x, y + 76, n2, 8.5, GREY, "middle", "italic")
    s += text(w / 2, 246, "щоразу знаходили — і губили, бо світ іще не мав комп'ютера", 10, GREY, "middle", "italic")
    save("fig-31-5h-3-rediscoveries.svg", s)


def fig_idea_plus_computer():
    w, h = 720, 240
    s = header(w, h)
    s += text(w / 2, 28, "Чому 1805-й мовчав, а 1965-й вибухнув", 14, INK, "middle", "bold")

    def card(x, y, label, col):
        return rect(x, y, 120, 50, fill="#fbfbfb", stroke=col, sw=1.6, rx=8) + \
            text(x + 60, y + 30, label, 11, col, "middle", "bold")

    y1 = 80
    s += card(70, y1, "ідея ШПФ", GREEN)
    s += text(210, y1 + 30, "+", 16, INK, "middle", "bold")
    s += card(230, y1, "ручка/папір", GREY)
    s += text(370, y1 + 30, "=", 16, INK, "middle", "bold")
    s += card(390, y1, "цікавинка", "#9a7a1e")
    s += text(525, y1 + 30, "(однаково не порахуєш)", 9.5, GREY, "start", "italic")
    y2 = 160
    s += card(70, y2, "ідея ШПФ", GREEN)
    s += text(210, y2 + 30, "+", 16, INK, "middle", "bold")
    s += card(230, y2, "комп'ютер", BLUE)
    s += text(370, y2 + 30, "=", 16, INK, "middle", "bold")
    s += card(390, y2, "РЕВОЛЮЦІЯ", RED)
    s += text(525, y2 + 30, "(мільйони множень за мить)", 9.5, GREY, "start", "italic")
    save("fig-31-5h-4-idea-plus-computer.svg", s)


def fig_relay():
    w, h = 760, 230
    s = header(w, h)
    s += text(w / 2, 28, "Естафета винахідників ШПФ — честь спільна", 14, INK, "middle", "bold")
    names = [("Ґаусс", "1805", GREEN), ("Рунге", "~1903", BLUE),
             ("Даніельсон|Ланцош", "1942", PURP), ("Кулі|Тьюкі", "1965", RED)]
    y, xs = 118, [110, 290, 470, 650]
    for i, ((nm, yr, col), x) in enumerate(zip(names, xs)):
        s += circle(x, y, 40, fill="#fbfbfb", stroke=col, w=2)
        parts = nm.split("|")
        if len(parts) == 1:
            s += text(x, y + 2, parts[0], 11, col, "middle", "bold")
        else:
            s += text(x, y - 6, parts[0], 10, col, "middle", "bold")
            s += text(x, y + 10, parts[1], 10, col, "middle", "bold")
        s += text(x, y + 58, yr, 10, GREY, "middle", "italic")
        if i < 3:
            s += arrow(x + 42, y, xs[i + 1] - 42, y, INK, 1.8)
    s += text(w / 2, 202, "+ Ґарвін, що штовхнув ідею у світ, — і ще з десяток забутих імен", 10, GREY, "middle", "italic")
    save("fig-31-5h-5-relay.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §31.6 Вікно й витік спектра
# ════════════════════════════════════════════════════════════════════════════

def _dftmag(x):
    """Магнітуда ДПФ дійсного сигналу x: |X[k]| для k = 0 … N/2 (чесний розрахунок)."""
    N = len(x)
    out = []
    for k in range(N // 2 + 1):
        re = sum(x[n] * math.cos(2 * math.pi * k * n / N) for n in range(N))
        im = -sum(x[n] * math.sin(2 * math.pi * k * n / N) for n in range(N))
        out.append(math.hypot(re, im))
    return out


def _hann(N):
    return [0.5 - 0.5 * math.cos(2 * math.pi * n / (N - 1)) for n in range(N)]


def fig_wraparound():
    w, h = 720, 330
    s = header(w, h)
    s += text(w / 2, 24, "Прихована умова ШПФ: запис нібито повторюється вічно", 13.5, INK, "middle", "bold")
    x0, pw = 70, 560

    def row(yc, f, label, ok):
        out = text(x0, yc - 52, label, 10.5, (GREEN if ok else RED), "start", "bold")
        out += line(x0, yc, x0 + pw, yc, FAINT, 1.0)
        out += poly([(x0 + (t / 200.0) * (pw / 2), yc - 30 * math.cos(2 * math.pi * f * t / 200.0)) for t in range(201)], BLUE, 2.2)
        out += poly([(x0 + pw / 2 + (t / 200.0) * (pw / 2), yc - 30 * math.cos(2 * math.pi * f * t / 200.0)) for t in range(201)], "#9bb0e0", 1.8, dash="5,3")
        out += line(x0 + pw / 2, yc - 44, x0 + pw / 2, yc + 30, GREY, 1.0, dash="3,3")
        out += text(x0 + pw / 2, yc + 44, "шов (повтор)", 8.5, GREY, "middle", "italic")
        if not ok:
            out += dot(x0 + pw / 2, yc - 30 * math.cos(2 * math.pi * f), 4, RED)
            out += dot(x0 + pw / 2, yc - 30 * math.cos(0.0), 4, RED)
            out += text(x0 + pw / 2 + 8, yc - 36, "стрибок!", 10, RED, "start", "bold")
        return out

    s += row(108, 4, "частота вкладається ціло → шов гладкий", True)
    s += row(250, 4.5, "не вкладається ціло → на шві стрибок", False)
    save("fig-31-6-1-wraparound.svg", s)


def fig_leakage():
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Витік: тон, що не вклався у вікно, розмазується", 13.5, INK, "middle", "bold")
    N = 64
    A = [math.cos(2 * math.pi * 8 * n / N) for n in range(N)]
    B = [math.cos(2 * math.pi * 8.5 * n / N) for n in range(N)]
    MA, MB = _dftmag(A), _dftmag(B)
    mx = max(max(MA), max(MB))
    nb = 20
    s += _spectrum(60, 210, 250, 150, [(i / nb, MA[i] / mx, "") for i in range(nb)], GREEN)
    s += text(185, 250, "8.0 періодів → чистий пік", 10.5, GREEN, "middle", "bold")
    s += _spectrum(420, 210, 250, 150, [(i / nb, MB[i] / mx, "") for i in range(nb)], RED)
    s += text(545, 250, "8.5 періоду → розмазано + спідниці", 10.5, RED, "middle", "bold")
    s += text(w / 2, 284, "половина періоду на краях не сходиться — і пік «тече» в сусідні біни", 10, GREY, "middle", "italic")
    save("fig-31-6-2-leakage.svg", s)


def fig_window_shapes():
    w, h = 700, 280
    s = header(w, h)
    s += text(w / 2, 26, "Віконні функції: рамка, що м'яко гасне до країв", 13.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 220, 560, 150
    s += axes(x0, y0, pw + 10, ph + 10)
    s += poly([(x0, y0 - ph)] + [(x0 + (n / 200.0) * pw, y0 - ph) for n in range(201)] + [(x0 + pw, y0)], GREY, 1.6, dash="5,3")
    s += text(x0 + pw - 4, y0 - ph + 12, "прямокутне (просто обрізати)", 9.5, GREY, "end", "italic")
    s += _plot_path(x0, y0, pw, ph, [(n / 200.0, 0.5 - 0.5 * math.cos(2 * math.pi * n / 200.0)) for n in range(201)], GREEN, 2.4)
    s += text(x0 + 0.5 * pw, y0 - ph - 2, "Ганна", 10, GREEN, "middle", "bold")
    s += _plot_path(x0, y0, pw, ph, [(n / 200.0, 0.42 - 0.5 * math.cos(2 * math.pi * n / 200.0) + 0.08 * math.cos(4 * math.pi * n / 200.0)) for n in range(201)], PURP, 2.0)
    s += text(x0 + 0.5 * pw, y0 - 0.34 * ph, "Блекмана", 9.5, PURP, "middle", "bold")
    s += text(w / 2, 266, "множимо відліки на таку «дзвіночку» перед ШПФ — краї плавно йдуть у нуль", 10, GREY, "middle", "italic")
    save("fig-31-6-3-window-shapes.svg", s)


def fig_apply_window():
    w, h = 740, 300
    s = header(w, h)
    s += text(w / 2, 26, "Накладання вікна: краї згасають — шов сходиться", 13.5, INK, "middle", "bold")
    N = 200
    raw = [math.cos(2 * math.pi * 4.5 * n / N) for n in range(N + 1)]
    win = [0.5 - 0.5 * math.cos(2 * math.pi * n / N) for n in range(N + 1)]
    tap = [raw[i] * win[i] for i in range(N + 1)]
    panels = [(40, raw, "сирий запис", BLUE, "краї не сходяться"),
              (280, win, "× вікно Ганна", GREEN, "дзвіночка"),
              (520, tap, "= з вікном", PURP, "краї → 0")]
    pw, ph, yc = 180, 70, 150
    for (x0, data, title, col, sub) in panels:
        s += text(x0 + pw / 2, 66, title, 11, col, "middle", "bold")
        s += line(x0, yc, x0 + pw, yc, FAINT, 1.0)
        s += _plot_path(x0, yc, pw, ph, [(i / N, data[i]) for i in range(N + 1)], col, 1.8)
        s += text(x0 + pw / 2, 250, sub, 9.5, GREY, "middle", "italic")
    s += text(250, yc, "×", 16, INK, "middle", "bold")
    s += text(490, yc, "=", 16, INK, "middle", "bold")
    save("fig-31-6-4-apply-window.svg", s)


def fig_window_tradeoff():
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Компроміс вікна: витік проти роздільності", 13.5, INK, "middle", "bold")
    N = 64
    tone = [math.cos(2 * math.pi * 8.5 * n / N) for n in range(N)]
    hn = _hann(N)
    hann = [hn[n] * tone[n] for n in range(N)]
    MR, MH = _dftmag(tone), _dftmag(hann)
    mr, mh = max(MR), max(MH)
    nb = 20
    s += _spectrum(60, 210, 250, 150, [(i / nb, MR[i] / mr, "") for i in range(nb)], RED)
    s += text(185, 250, "прямокутне: вузький пік, високі спідниці", 9.5, RED, "middle", "bold")
    s += _spectrum(420, 210, 250, 150, [(i / nb, MH[i] / mh, "") for i in range(nb)], GREEN)
    s += text(545, 250, "Ганна: ширший пік, низькі спідниці", 9.5, GREEN, "middle", "bold")
    s += text(w / 2, 284, "вікно глушить витік (нижчі спідниці) ціною ширшого піка — та сама невизначеність", 9.5, GREY, "middle", "italic")
    save("fig-31-6-5-window-tradeoff.svg", s)


def fig_window_zoo():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Який вікно коли", 14.5, INK, "middle", "bold")
    s += text(70, 68, "вікно", 10.5, INK, "start", "bold")
    s += text(300, 68, "спідниці (витік)", 10, INK, "middle", "bold")
    s += text(460, 68, "ширина піка", 10, INK, "middle", "bold")
    s += text(625, 68, "для чого", 10, INK, "middle", "bold")
    rows = [("Прямокутне", "високі", "найвужча", "роздільні тони, транзієнти", GREY),
            ("Ганна (Hann)", "низькі", "середня", "універсальне (дефолт)", GREEN),
            ("Геммінга", "низькі", "середня", "майже як Ганна", BLUE),
            ("Блекмана", "дуже низькі", "ширша", "слабкий тон біля сильного", PURP),
            ("Flat-top", "низькі", "найширша", "точна амплітуда", "#9a7a1e")]
    y = 100
    for (nm, sl, bw, use, col) in rows:
        s += text(70, y, nm, 10.5, col, "start", "bold")
        s += text(300, y, sl, 9.5, INK, "middle")
        s += text(460, y, bw, 9.5, INK, "middle")
        s += text(625, y, use, 8.5, GREY, "middle")
        s += line(60, y + 12, 690, y + 12, FAINT, 1)
        y += 34
    s += text(w / 2, 272, "не знаєш, яке брати — бери Ганна; треба точна амплітуда — Flat-top", 10, GREY, "middle", "italic")
    save("fig-31-6-6-window-zoo.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §31.7 Навіщо частотна область
# ════════════════════════════════════════════════════════════════════════════

def fig_app_map():
    w, h = 740, 330
    s = header(w, h)
    s += text(w / 2, 26, "П'ять задач для частотної області", 14.5, INK, "middle", "bold")
    cx, cy = 160, 188
    s += circle(cx, cy, 54, fill="#eef7ef", stroke=GREEN, w=2.4)
    s += text(cx, cy - 4, "частотна", 12, GREEN, "middle", "bold")
    s += text(cx, cy + 14, "область", 12, GREEN, "middle", "bold")
    apps = [("виявлення тонів", "DTMF, біп, тюнер", BLUE),
            ("вібродіагностика", "оберти, дефекти", PURP),
            ("фільтрація", "прибрати гул", RED),
            ("пошук у шумі", "слабкий тон", "#9a7a1e"),
            ("стиснення", "MP3, JPEG", INK)]
    bx, bw, bh, y0 = 360, 350, 44, 58
    for i, (t1, t2, col) in enumerate(apps):
        y = y0 + i * (bh + 10)
        s += arrow(cx + 54, cy, bx - 6, y + bh / 2, col, 1.4)
        s += rect(bx, y, bw, bh, fill="#fbfbfb", stroke=col, sw=1.6, rx=8)
        s += text(bx + 14, y + 27, t1, 12, col, "start", "bold")
        s += text(bx + bw - 14, y + 27, t2, 9.5, GREY, "end", "italic")
    save("fig-31-7-1-app-map.svg", s)


def fig_tone_detect():
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Виявлення тонів: дві частоти кнопки → два піки", 13.5, INK, "middle", "bold")
    tx, tyc, tpw, tph = 55, 150, 290, 60
    s += line(tx, tyc, tx + tpw, tyc, FAINT, 1.2)

    def sig(x):
        return 0.5 * math.sin(2 * math.pi * 7 * x) + 0.5 * math.sin(2 * math.pi * 12 * x)

    s += poly([(tx + (k / 300.0) * tpw, tyc - tph * sig(k / 300.0)) for k in range(301)], BLUE, 1.5)
    s += text(tx + tpw / 2, 250, "час: нерозбірливе гудіння", 11, BLUE, "middle", "bold")
    s += arrow(358, 150, 398, 150, INK, 2)
    s += _spectrum(410, 205, 260, 120, [(0.30, 0.85, "770 Гц"), (0.62, 0.85, "1336 Гц")], GREEN)
    s += text(540, 250, "частота: два піки → цифра «5»", 11, GREEN, "middle", "bold")
    save("fig-31-7-2-tone-detect.svg", s)


def fig_vibration():
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Вібродіагностика: новий пік = дефект", 14, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 240, 580, 180
    s += arrow(x0, y0, x0, y0 - ph - 14, INK, 1.6)
    s += arrow(x0, y0, x0 + pw + 12, y0, INK, 1.6)
    s += text(x0 + pw + 10, y0 + 18, "частота →", 10, INK, "middle", "bold")
    for i in range(40):
        gx = 0.05 + i * (0.9 / 40)
        s += line(x0 + gx * pw, y0, x0 + gx * pw, y0 - (0.04 + 0.02 * abs(math.sin(i * 1.7))) * ph, GREY, 2)
    for fx, hh, lbl in [(0.12, 0.9, "оберти"), (0.24, 0.45, "2×"), (0.36, 0.28, "3×"), (0.48, 0.18, "")]:
        s += line(x0 + fx * pw, y0, x0 + fx * pw, y0 - hh * ph, GREEN, 5)
        if lbl:
            s += text(x0 + fx * pw, y0 - hh * ph - 6, lbl, 9, GREEN, "middle", "bold")
    s += line(x0 + 0.70 * pw, y0, x0 + 0.70 * pw, y0 - 0.5 * ph, RED, 5)
    s += text(x0 + 0.70 * pw, y0 - 0.5 * ph - 6, "новий пік = дефект!", 10, RED, "middle", "bold")
    s += text(w / 2, 284, "еталон здорової машини + сторожа за новими піками = поломка наперед", 9.5, GREY, "middle", "italic")
    save("fig-31-7-3-vibration.svg", s)


def fig_freq_filter():
    w, h = 760, 270
    s = header(w, h)
    s += text(w / 2, 24, "Фільтрація в частоті: вирізати пік гулу", 13.5, INK, "middle", "bold")

    def waveA(x):
        return 0.5 * math.sin(2 * math.pi * 2 * x) + 0.4 * math.sin(2 * math.pi * 22 * x)

    def waveB(x):
        return 0.55 * math.sin(2 * math.pi * 2 * x)

    for (x0, fn, title, col) in [(40, waveA, "сигнал + гул", BLUE), (530, waveB, "чисто", GREEN)]:
        yc = 110
        s += line(x0, yc, x0 + 170, yc, FAINT, 1.0)
        s += poly([(x0 + (k / 300.0) * 170, yc - 34 * fn(k / 300.0)) for k in range(301)], col, 1.5)
        s += text(x0 + 85, yc + 54, title, 10.5, col, "middle", "bold")
    s += arrow(218, 110, 250, 110, INK, 2)
    s += _spectrum(265, 150, 180, 90, [(0.12, 0.85, ""), (0.72, 0.7, "")], GREEN)
    hx, hy = 265 + 0.72 * 180, 150 - 0.7 * 90
    s += line(hx - 10, hy - 8, hx + 10, hy + 8, RED, 2)
    s += line(hx - 10, hy + 8, hx + 10, hy - 8, RED, 2)
    s += text(hx, hy - 16, "× зануляємо", 9, RED, "middle", "bold")
    s += text(355, 250, "спектр: гул окремо", 9.5, GREEN, "middle", "italic")
    s += arrow(458, 110, 520, 110, INK, 2)
    s += text(489, 98, "обернене", 8.5, GREY, "middle", "italic")
    save("fig-31-7-4-freq-filter.svg", s)


def fig_hidden_extract():
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 26, "Витягти слабке: у часі шум, у частоті — пік", 13.5, INK, "middle", "bold")
    tx, tyc, tpw, tph = 55, 150, 290, 58
    s += line(tx, tyc, tx + tpw, tyc, FAINT, 1.2)

    def sig(x):
        return (0.25 * math.sin(2 * math.pi * 9 * x) + 0.5 * math.sin(2 * math.pi * 53 * x + 0.6)
                + 0.4 * math.sin(2 * math.pi * 83 * x + 1.7) + 0.35 * math.sin(2 * math.pi * 111 * x))

    N = 500
    s += poly([(tx + (k / N) * tpw, tyc - tph * sig(k / N) / 1.4) for k in range(N + 1)], BLUE, 1.1)
    s += text(tx + tpw / 2, 250, "час: суцільний шум, тону не видно", 10.5, BLUE, "middle", "bold")
    s += arrow(358, 150, 398, 150, INK, 2)
    fx0, fyb, fpw, fph = 410, 205, 260, 120
    grass = [(0.06 + i * 0.05, 0.05 + 0.03 * abs(math.sin(i * 1.9)), "") for i in range(18)]
    s += _spectrum(fx0, fyb, fpw, fph, grass, GREEN)
    s += line(fx0 + 0.18 * fpw, fyb, fx0 + 0.18 * fpw, fyb - 0.85 * fph, GREEN, 5)
    s += text(fx0 + 0.18 * fpw, fyb - 0.85 * fph - 6, "тон!", 9.5, GREEN, "middle", "bold")
    s += text(540, 250, "частота: пік над шумом", 10.5, GREEN, "middle", "bold")
    save("fig-31-7-5-hidden.svg", s)


def fig_when():
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Час чи частота: яка область під яке питання", 13.5, INK, "middle", "bold")
    s += rect(40, 52, 300, 40, fill="#eef3fb", stroke=BLUE, sw=1.8, rx=8)
    s += text(190, 77, "ЧАС — «коли»", 12, BLUE, "middle", "bold")
    s += rect(380, 52, 300, 40, fill="#eef7ef", stroke=GREEN, sw=1.8, rx=8)
    s += text(530, 77, "ЧАСТОТА — «що за тон»", 12, GREEN, "middle", "bold")
    timeq = ["коли сталася подія", "різкий фронт, транзієнт", "таймінг, синхронізація", "просте згладжування"]
    freqq = ["які тони всередині", "який період / оберти", "де гул-завада", "розділити перекриті"]
    for i, (q1, q2) in enumerate(zip(timeq, freqq)):
        y = 116 + i * 34
        s += text(60, y, "• " + q1, 11, INK, "start")
        s += text(400, y, "• " + q2, 11, INK, "start")
    s += rect(40, 256, 640, 34, fill="#fdf6f5", stroke=RED, sw=1.4, rx=8)
    s += text(360, 277, "засторога: ШПФ потребує буфера на N відліків → затримка + такти (дрібне згладжування дешевше часовим фільтром)", 8.5, INK, "middle", "italic")
    save("fig-31-7-6-when.svg", s)


if __name__ == "__main__":
    # §31.0 Історія — Фур'є
    fig_string_modes()
    fig_square_from_sines()
    fig_heat_modes()
    fig_gibbs()
    fig_timeline()
    fig_legacy()
    # §31.1 Сигнал у часі й частоті
    fig_two_languages()
    fig_tone_chord()
    fig_hidden_hum()
    fig_transform_mirror()
    fig_canonical_pairs()
    fig_which_domain()
    # §31.2 Ідея Фур'є
    fig_sinusoid_anatomy()
    fig_harmonics_ladder()
    fig_synthesis_saw()
    fig_recipe()
    fig_phase()
    fig_analysis_synthesis()
    # §31.3 Спектр: що він показує
    fig_spectrum_anatomy()
    fig_peak_read()
    fig_noise_floor()
    fig_linear_db()
    fig_harmonic_comb()
    fig_read_real()
    # §31.4 Дискретне перетворення Фур'є
    fig_correlation()
    fig_bins()
    fig_nyquist()
    fig_resolution()
    fig_aliasing()
    fig_cost()
    # §31.5 Швидке перетворення Фур'є
    fig_divide()
    fig_butterfly()
    fig_recursion_tree()
    fig_speedup_curve()
    fig_speedup_bars()
    fig_realtime()
    # §31.5 Історія — ШПФ (Кулі-Тьюкі, Ґаусс)
    fig_coldwar()
    fig_gauss_before_fourier()
    fig_rediscoveries()
    fig_idea_plus_computer()
    fig_relay()
    # §31.6 Вікно й витік спектра
    fig_wraparound()
    fig_leakage()
    fig_window_shapes()
    fig_apply_window()
    fig_window_tradeoff()
    fig_window_zoo()
    # §31.7 Навіщо частотна область
    fig_app_map()
    fig_tone_detect()
    fig_vibration()
    fig_freq_filter()
    fig_hidden_extract()
    fig_when()
    print("OK — фігури §31.0–§31.7 (+історія ШПФ) згенеровано в", OUT)
