# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 32 — «Цифрові фільтри в мікроконтролері» (Модуль 5).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Частотні характеристики (ковзне середнє, EMA) рахуються чесно за їхніми
формулами. Спільні помічники — у стилі Розділів 28–31.
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


def _spectrum(x0, ybase, pw, ph, bars, col):
    s = arrow(x0, ybase, x0, ybase - ph - 14, INK, 1.4)
    s += arrow(x0, ybase, x0 + pw + 10, ybase, INK, 1.4)
    for (fx, hh, lbl) in bars:
        x = x0 + fx * pw
        s += line(x, ybase, x, ybase - hh * ph, col, 5)
        if lbl:
            s += text(x, ybase + 14, lbl, 9.5, GREY, "middle")
    return s


# ──────────────────────────────────────────────────────────────────────────
#  Частотні характеристики (fn = частота / Найквіст ∈ [0..1])
# ──────────────────────────────────────────────────────────────────────────

def _ma_resp(fn, N):
    """|H| ковзного середнього довжини N."""
    w = math.pi * fn
    if abs(w) < 1e-9:
        return 1.0
    return abs(math.sin(N * w / 2.0) / (N * math.sin(w / 2.0)))


def _ema_resp(fn, a):
    """|H| експоненційного згладжування з коефіцієнтом a."""
    w = math.pi * fn
    return a / math.sqrt(1.0 - 2.0 * (1.0 - a) * math.cos(w) + (1.0 - a) ** 2)


# ════════════════════════════════════════════════════════════════════════════
#  §32.1 Фільтр як «формувач спектра»
# ════════════════════════════════════════════════════════════════════════════

def fig_shaper():
    w, h = 760, 280
    s = header(w, h)
    s += text(w / 2, 24, "Фільтр множить спектр на свою частотну характеристику", 13, INK, "middle", "bold")

    def resp(fn):
        return 1.0 / (1.0 + (fn / 0.42) ** 4)

    fxs, inh = [0.15, 0.35, 0.60, 0.85], [0.7, 0.85, 0.6, 0.5]
    s += _spectrum(30, 200, 180, 120, [(fx, hh, "") for fx, hh in zip(fxs, inh)], BLUE)
    s += text(120, 240, "вхід", 10.5, BLUE, "middle", "bold")
    s += text(232, 132, "×", 18, INK, "middle", "bold")
    rx0, ry0, rpw, rph = 260, 200, 180, 120
    s += arrow(rx0, ry0, rx0, ry0 - rph - 12, INK, 1.4)
    s += arrow(rx0, ry0, rx0 + rpw + 8, ry0, INK, 1.4)
    s += _plot_path(rx0, ry0, rpw, rph, [(i / 100.0, resp(i / 100.0)) for i in range(101)], GREEN, 2.4)
    s += text(350, 240, "характеристика", 10.5, GREEN, "middle", "bold")
    s += text(462, 132, "=", 18, INK, "middle", "bold")
    outh = [inh[i] * resp(fxs[i]) for i in range(4)]
    s += _spectrum(490, 200, 180, 120, [(fx, hh, "") for fx, hh in zip(fxs, outh)], PURP)
    s += text(580, 240, "вихід", 10.5, PURP, "middle", "bold")
    s += text(w / 2, 266, "низькі частоти пройшли, високі — приглушені", 10, GREY, "middle", "italic")
    save("fig-32-1-1-shaper.svg", s)


def fig_response_anatomy():
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 26, "Паспорт фільтра: смуги пропускання, переходу, затримання", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 240, 580, 180
    s += arrow(x0, y0, x0, y0 - ph - 14, INK, 1.6)
    s += arrow(x0, y0, x0 + pw + 12, y0, INK, 1.6)
    s += text(x0 + pw + 10, y0 + 18, "частота →", 10, INK, "middle", "bold")
    s += text(x0 - 8, y0 - ph - 2, "підсилення", 10, INK, "end", "bold")

    def resp(fn):
        return 1.0 / math.sqrt(1.0 + (fn / 0.45) ** 8)

    s += line(x0, y0 - ph, x0 + pw, y0 - ph, FAINT, 1, dash="4,3")
    s += text(x0 - 6, y0 - ph + 4, "1", 9, GREY, "end")
    s += line(x0, y0 - 0.707 * ph, x0 + pw, y0 - 0.707 * ph, GOLD, 1, dash="4,3")
    s += text(x0 - 6, y0 - 0.707 * ph + 4, "0.707", 8.5, "#9a7a1e", "end")
    s += _plot_path(x0, y0, pw, ph, [(i / 200.0, resp(i / 200.0)) for i in range(201)], GREEN, 2.6)
    fc = 0.45
    s += line(x0 + fc * pw, y0, x0 + fc * pw, y0 - 0.707 * ph, RED, 1.2, dash="3,3")
    s += text(x0 + fc * pw, y0 + 16, "fc", 10, RED, "middle", "bold")
    s += text(x0 + 0.2 * pw, y0 + 34, "пропускання", 9.5, GREEN, "middle", "bold")
    s += text(x0 + 0.55 * pw, y0 + 34, "перехід", 9.5, "#9a7a1e", "middle", "bold")
    s += text(x0 + 0.82 * pw, y0 + 34, "затримання", 9.5, RED, "middle", "bold")
    save("fig-32-1-2-response-anatomy.svg", s)


def fig_movavg_response():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Ковзне середнє — це ФНЧ із нулями", 14, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 230, 580, 170
    s += arrow(x0, y0, x0, y0 - ph - 14, INK, 1.6)
    s += arrow(x0, y0, x0 + pw + 12, y0, INK, 1.6)
    s += text(x0 + pw + 6, y0 + 18, "частота → (Найквіст)", 9, INK, "end", "bold")
    s += text(x0 - 8, y0 - ph - 2, "підсилення", 10, INK, "end", "bold")
    N = 8
    s += _plot_path(x0, y0, pw, ph, [(i / 300.0, _ma_resp(i / 300.0, N)) for i in range(301)], GREEN, 2.4)
    k = 1
    while 2 * k / N < 1.0:
        fn = 2 * k / N
        s += dot(x0 + fn * pw, y0, 4, RED)
        s += text(x0 + fn * pw, y0 + 16, "нуль", 8, RED, "middle")
        k += 1
    s += text(x0 + 0.5 * pw, y0 - 0.6 * ph, "N = 8", 11, GREEN, "middle", "bold")
    s += text(w / 2, 266, "нулі — частоти з періодом, кратним вікну (усереднюються дощенту, §30.2)", 9.5, GREY, "middle", "italic")
    save("fig-32-1-3-movavg-response.svg", s)


def fig_ema_response():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "EMA — гладкий ФНЧ, зріз керується α", 14, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 230, 580, 170
    s += arrow(x0, y0, x0, y0 - ph - 14, INK, 1.6)
    s += arrow(x0, y0, x0 + pw + 12, y0, INK, 1.6)
    s += text(x0 + pw + 10, y0 + 18, "частота →", 9.5, INK, "middle", "bold")
    s += text(x0 - 8, y0 - ph - 2, "підсилення", 10, INK, "end", "bold")
    s += line(x0, y0 - 0.707 * ph, x0 + pw, y0 - 0.707 * ph, GOLD, 1, dash="4,3")
    s += text(x0 - 6, y0 - 0.707 * ph + 4, "−3дБ", 8, "#9a7a1e", "end")
    for (a, col, lbl, ly) in [(0.5, BLUE, "α=0.5 (зріз вище)", 0.66), (0.1, GREEN, "α=0.1 (зріз нижче)", 0.30)]:
        s += _plot_path(x0, y0, pw, ph, [(i / 300.0, _ema_resp(i / 300.0, a)) for i in range(301)], col, 2.4)
        s += text(*(_pt(x0, y0, pw, ph, 0.42, ly)), lbl, 10, col, "start", "bold")
    s += text(w / 2, 266, "менша α → вужча смуга пропускання → сильніше згладжування (§30.5)", 9.5, GREY, "middle", "italic")
    save("fig-32-1-4-ema-response.svg", s)


def fig_ideal_real():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Ідеальна «цегляна стіна» проти реальної характеристики", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 230, 580, 170
    s += arrow(x0, y0, x0, y0 - ph - 14, INK, 1.6)
    s += arrow(x0, y0, x0 + pw + 12, y0, INK, 1.6)
    s += text(x0 - 8, y0 - ph - 2, "підсилення", 10, INK, "end", "bold")
    fc = 0.45
    s += poly([(x0, y0 - ph), (x0 + fc * pw, y0 - ph), (x0 + fc * pw, y0)], GREY, 1.8, dash="6,4")
    s += text(x0 + 0.2 * pw, y0 - ph - 3, "ідеал (мрія)", 9.5, GREY, "middle", "italic")

    def real(fn):
        base = 1.0 / math.sqrt(1.0 + (fn / fc) ** 12)
        ripple = (1.0 + 0.04 * math.sin(fn * 40)) if fn < fc else 1.0
        return max(0.03, base * ripple)

    s += _plot_path(x0, y0, pw, ph, [(i / 300.0, real(i / 300.0)) for i in range(301)], GREEN, 2.4)
    s += text(x0 + 0.66 * pw, y0 - 0.5 * ph, "поступовий спад", 9, GREEN, "start", "bold")
    s += text(x0 + 0.85 * pw, y0 - 0.12 * ph, "ненульове затримання", 8.5, RED, "middle", "italic")
    s += text(x0 + 0.16 * pw, y0 - 0.94 * ph, "пульсації", 8.5, "#9a7a1e", "middle", "italic")
    s += text(w / 2, 266, "різкіший обрив = довший фільтр + більша затримка (невизначеність §31.6)", 9, GREY, "middle", "italic")
    save("fig-32-1-5-ideal-real.svg", s)


def fig_design_flow():
    w, h = 740, 210
    s = header(w, h)
    s += text(w / 2, 26, "Як народжується фільтр: задум у частоті → робота в часі", 12.5, INK, "middle", "bold")
    blocks = [("бажана|характеристика", "що пропускати/гасити", GREEN),
              ("процедура|проєктування", "→ коефіцієнти", GOLD),
              ("зважена сума|в часі", "множ.+додав. на відлік", BLUE)]
    bw, bh, by = 200, 76, 80
    xs = [30, 270, 510]
    for (x, (t, sub, col)) in zip(xs, blocks):
        s += rect(x, by, bw, bh, fill="#fbfbfb", stroke=col, sw=1.8, rx=10)
        parts = t.split("|")
        s += text(x + bw / 2, by + 28, parts[0], 12, col, "middle", "bold")
        s += text(x + bw / 2, by + 46, parts[1], 12, col, "middle", "bold")
        s += text(x + bw / 2, by + 64, sub, 8.5, GREY, "middle", "italic")
    for i in range(2):
        s += arrow(xs[i] + bw, by + bh / 2, xs[i + 1] - 4, by + bh / 2, INK, 2)
    s += text(w / 2, 186, "мислимо в частоті, рахуємо в часі — кілька дій на відлік, без ШПФ", 9.5, GREY, "middle", "italic")
    save("fig-32-1-6-design-flow.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §32.2 КІХ-фільтр (FIR)
# ════════════════════════════════════════════════════════════════════════════

def _lp_taps(M, fc):
    """M+1 відводів ідеального ФНЧ (зріз fc від Найквіста), згладжених вікном Ганна."""
    taps = []
    for k in range(M + 1):
        x = k - M / 2.0
        if abs(x) < 1e-9:
            sinc = fc
        else:
            sinc = fc * math.sin(math.pi * fc * x) / (math.pi * fc * x)
        win = 0.5 - 0.5 * math.cos(2 * math.pi * k / M)
        taps.append(sinc * win)
    return taps


def _fir_resp(taps, fn):
    """|H(fn)| КІХ-фільтра; fn — частота / Найквіст ∈ [0..1]."""
    w = math.pi * fn
    re = sum(taps[k] * math.cos(w * k) for k in range(len(taps)))
    im = -sum(taps[k] * math.sin(w * k) for k in range(len(taps)))
    return math.hypot(re, im)


def fig_fir_structure():
    w, h = 740, 240
    s = header(w, h)
    s += text(w / 2, 26, "Будова КІХ: лінія затримки → відводи → суматор", 13, INK, "middle", "bold")
    xs = [60, 180, 300, 420]
    ynode = 80
    labels = ["x[n]", "x[n−1]", "x[n−2]", "x[n−3]"]
    for i, (x, lbl) in enumerate(zip(xs, labels)):
        s += rect(x, ynode - 18, 86, 36, fill="#eef3fb", stroke=BLUE, sw=1.6, rx=6)
        s += text(x + 43, ynode + 5, lbl, 11, BLUE, "middle", "bold")
        if i < 3:
            s += arrow(x + 86, ynode, xs[i + 1] - 2, ynode, INK, 1.6)
            s += text((x + 86 + xs[i + 1]) / 2, ynode - 6, "z⁻¹", 9, GREY, "middle", "italic")
    sumy = 182
    s += line(xs[0] + 43, sumy, 520, sumy, GREEN, 1.2)
    bcoef = ["b₀", "b₁", "b₂", "b₃"]
    for i, x in enumerate(xs):
        midy = (ynode + 18 + sumy) / 2
        s += arrow(x + 43, ynode + 18, x + 43, sumy - 1, GREEN, 1.4)
        s += circle(x + 43, midy, 11, fill="#ffffff", stroke=GREEN, w=1.5)
        s += text(x + 43, midy + 4, "×", 9, GREEN, "middle", "bold")
        s += text(x + 58, midy + 4, bcoef[i], 9, GREEN, "start", "bold")
    s += circle(540, sumy, 20, fill="#eef7ef", stroke=INK, w=1.8)
    s += text(540, sumy + 6, "Σ", 16, INK, "middle", "bold")
    s += arrow(560, sumy, 640, sumy, INK, 2)
    s += text(648, sumy + 5, "y[n]", 12, INK, "start", "bold")
    s += text(w / 2, 224, "y[n] = b₀·x[n] + b₁·x[n−1] + …  (зважена сума входів, без зворотного зв'язку)", 9.5, GREY, "middle", "italic")
    save("fig-32-2-1-fir-structure.svg", s)


def fig_impulse():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Імпульс на вході → коефіцієнти на виході", 14, INK, "middle", "bold")

    def stems(x0, yb, vals, col, lbl):
        out = line(x0, yb, x0 + 240, yb, FAINT, 1.2)
        out += text(x0 + 120, yb + 34, lbl, 10, col, "middle", "bold")
        for i, v in enumerate(vals):
            xx = x0 + 14 + i * 30
            out += line(xx, yb, xx, yb - v * 90, col, 3)
            if v > 0:
                out += dot(xx, yb - v * 90, 3, col)
        return out

    s += stems(50, 150, [1, 0, 0, 0, 0, 0, 0], BLUE, "вхід: імпульс (1,0,0…)")
    s += arrow(312, 140, 362, 140, INK, 2)
    s += text(337, 128, "КІХ", 9, GREY, "middle", "bold")
    s += stems(384, 150, [0.2, 0.5, 0.8, 0.5, 0.2, 0, 0], GREEN, "вихід: коефіцієнти b₀…b_M, тоді 0")
    save("fig-32-2-2-impulse.svg", s)


def fig_taps_shape():
    w, h = 720, 320
    s = header(w, h)
    s += text(w / 2, 24, "Форма відводів формує характеристику", 13.5, INK, "middle", "bold")
    N = 8
    equal = [1.0 / N] * N
    hannw = [0.5 - 0.5 * math.cos(2 * math.pi * k / (N - 1)) for k in range(N)]
    bell = [v / sum(hannw) for v in hannw]
    for (x0, taps, lbl, col) in [(60, equal, "рівні відводи (ковзне середнє)", GREEN),
                                 (400, bell, "згладжені відводи (вікно)", PURP)]:
        sy = 80
        s += text(x0 + 130, 56, lbl, 10, col, "middle", "bold")
        s += line(x0, sy, x0 + 260, sy, FAINT, 1)
        for i, v in enumerate(taps):
            xx = x0 + 18 + i * 30
            s += line(xx, sy, xx, sy - v * N * 26, col, 4)
        ry0, rph, rpw = 250, 120, 260
        s += arrow(x0, ry0, x0, ry0 - rph - 10, INK, 1.4)
        s += arrow(x0, ry0, x0 + rpw + 8, ry0, INK, 1.4)
        dc = sum(taps)
        s += _plot_path(x0, ry0, rpw, rph, [(i / 200.0, _fir_resp(taps, i / 200.0) / dc) for i in range(201)], col, 2.2)
        s += text(x0 + rpw / 2, 266, "характеристика", 9, GREY, "middle", "italic")
    save("fig-32-2-3-taps-shape.svg", s)


def fig_linear_phase():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Лінійна фаза: вихід = вхід, лише зсунутий", 13.5, INK, "middle", "bold")
    x0, yc, pw = 70, 140, 580

    def sig(x):
        return 0.5 * math.sin(2 * math.pi * 2 * x) + 0.35 * math.sin(2 * math.pi * 5 * x + 0.5)

    D = 0.08
    s += line(x0, yc, x0 + pw, yc, FAINT, 1.0)
    s += poly([(x0 + (k / 300.0) * pw, yc - 42 * sig(k / 300.0)) for k in range(301)], BLUE, 2.0)
    s += poly([(x0 + (k / 300.0) * pw, yc - 42 * sig(k / 300.0 - D)) for k in range(301)], GREEN, 2.0, dash="6,3")
    s += text(x0 + 0.16 * pw, yc - 58, "вхід", 10, BLUE, "start", "bold")
    s += text(x0 + 0.45 * pw, yc + 60, "вихід (зсув M/2, форма ціла)", 10, GREEN, "start", "bold")
    s += arrow(x0 + 0.7 * pw, yc - 48, x0 + 0.7 * pw + D * pw, yc - 48, RED, 1.4)
    s += text(x0 + 0.7 * pw + D * pw / 2, yc - 54, "M/2", 8.5, RED, "middle", "bold")
    save("fig-32-2-4-linear-phase.svg", s)


def fig_fir_impl():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Реалізація КІХ: кільцевий буфер + MAC", 13.5, INK, "middle", "bold")
    cx, cy, r = 170, 145, 68
    Ncell = 6
    for i in range(Ncell):
        ang = 2 * math.pi * i / Ncell - math.pi / 2
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang)
        col = GREEN if i == 0 else BLUE
        s += circle(x, y, 18, fill=("#eef7ef" if i == 0 else "#eef3fb"), stroke=col, w=1.6)
        s += text(x, y + 4, "x" + str(i), 9, col, "middle", "bold")
    s += text(cx, cy + 4, "буфер", 9.5, INK, "middle", "bold")
    s += arrow(cx + r + 4, cy - r + 6, cx + 14, cy - r - 8, GREEN, 1.4)
    s += text(cx + r + 8, cy - r - 8, "новий", 9, GREEN, "start", "bold")
    s += text(cx, cy + r + 30, "голова рухається по колу", 8.5, GREY, "middle", "italic")
    s += rect(380, 66, 312, 150, fill="#fbfbfb", stroke=INK, sw=1.4, rx=8)
    code = [("acc = 0", INK), ("for k in 0..M:", BLUE), ("    acc += b[k]·buf[k]", GREEN), ("y = acc", INK)]
    for i, (ln, col) in enumerate(code):
        s += text(398, 100 + i * 28, ln, 12.5, col, "start", "bold")
    s += text(536, 206, "M+1 множень-додавань на відлік", 9, GREY, "middle", "italic")
    save("fig-32-2-5-fir-impl.svg", s)


def fig_more_taps():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Більше відводів → різкіша характеристика", 14, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 230, 580, 170
    s += arrow(x0, y0, x0, y0 - ph - 14, INK, 1.6)
    s += arrow(x0, y0, x0 + pw + 12, y0, INK, 1.6)
    s += text(x0 + pw + 10, y0 + 18, "частота →", 9.5, INK, "middle", "bold")
    s += text(x0 - 8, y0 - ph - 2, "підсилення", 10, INK, "end", "bold")
    for (M, col, lbl, lx) in [(8, "#9a7a1e", "M=8", 0.56), (32, BLUE, "M=32", 0.40), (64, GREEN, "M=64", 0.27)]:
        taps = _lp_taps(M, 0.3)
        dc = sum(taps)
        s += _plot_path(x0, y0, pw, ph, [(i / 300.0, _fir_resp(taps, i / 300.0) / dc) for i in range(301)], col, 2.2)
        s += text(*(_pt(x0, y0, pw, ph, lx, 0.92)), lbl, 9.5, col, "start", "bold")
    s += text(w / 2, 266, "той самий ФНЧ: більше коефіцієнтів — гостріший зріз, але дорожче й повільніше", 9, GREY, "middle", "italic")
    save("fig-32-2-6-more-taps.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §32.3 БІХ-фільтр (IIR)
# ════════════════════════════════════════════════════════════════════════════

def _butter_resp(fn, fc, order):
    """|H| фільтра Баттерворта порядку order, зріз fc (від Найквіста)."""
    return 1.0 / math.sqrt(1.0 + (fn / fc) ** (2 * order))


def fig_iir_structure():
    w, h = 740, 270
    s = header(w, h)
    s += text(w / 2, 26, "Будова БІХ: пряма гілка входів + зворотна гілка виходів", 12.5, INK, "middle", "bold")
    s += rect(40, 70, 180, 56, fill="#eef7ef", stroke=GREEN, sw=1.8, rx=8)
    s += text(130, 94, "входи x[n], x[n−1]…", 10.5, GREEN, "middle", "bold")
    s += text(130, 112, "× b₀, b₁…  (пряма)", 9, GREY, "middle", "italic")
    s += arrow(220, 98, 304, 98, GREEN, 1.8)
    s += circle(330, 98, 22, fill="#fbfbfb", stroke=INK, w=1.8)
    s += text(330, 104, "Σ", 16, INK, "middle", "bold")
    s += arrow(352, 98, 470, 98, INK, 2)
    s += text(486, 103, "y[n]", 13, INK, "start", "bold")
    s += line(420, 98, 420, 200, GREY, 1.4)
    s += arrow(420, 200, 222, 200, RED, 1.6)
    s += rect(40, 172, 180, 56, fill="#fdf6f5", stroke=RED, sw=1.8, rx=8)
    s += text(130, 196, "виходи y[n−1], y[n−2]…", 9.5, RED, "middle", "bold")
    s += text(130, 214, "× (−a₁), (−a₂)  (зворотна)", 8.5, GREY, "middle", "italic")
    s += arrow(132, 172, 318, 118, RED, 1.6)
    s += text(w / 2, 254, "вихід частково складається з самого себе — це й дає БІХ силу та ризик", 9.5, GREY, "middle", "italic")
    save("fig-32-3-1-iir-structure.svg", s)


def fig_iir_impulse():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Імпульсна характеристика БІХ згасає нескінченно", 13.5, INK, "middle", "bold")
    x0, yb, pw = 70, 200, 580
    s += line(x0, yb, x0 + pw, yb, FAINT, 1.2)
    s += text(x0 + pw + 4, yb + 4, "n", 10, INK, "start")
    a, n = 0.3, 24
    for i in range(n + 1):
        xx = x0 + 10 + i * 23
        if i <= 6:
            s += line(xx, yb, xx, yb - (1.0 / 7) * 300, "#cfcfcf", 3)
    for i in range(n + 1):
        xx = x0 + 10 + i * 23
        v = a * (1 - a) ** i
        s += line(xx, yb, xx, yb - v * 300, GREEN, 3)
        s += dot(xx, yb - v * 300, 2.5, GREEN)
    s += text(x0 + 0.5 * pw, 92, "БІХ (EMA, α=0.3): α(1−α)ⁿ — хвіст без кінця", 10, GREEN, "middle", "bold")
    s += text(x0 + 0.12 * pw, yb - 56, "КІХ: обрив після M+1 (сіре)", 9, GREY, "start", "italic")
    save("fig-32-3-2-iir-impulse.svg", s)


def fig_efficiency():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Та сама гострота: КІХ — багато коефіцієнтів, БІХ — кілька", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 230, 580, 170
    s += arrow(x0, y0, x0, y0 - ph - 14, INK, 1.6)
    s += arrow(x0, y0, x0 + pw + 12, y0, INK, 1.6)
    s += text(x0 + pw + 10, y0 + 18, "частота →", 9.5, INK, "middle", "bold")
    s += text(x0 - 8, y0 - ph - 2, "підсилення", 10, INK, "end", "bold")
    taps = _lp_taps(64, 0.3)
    dc = sum(taps)
    s += _plot_path(x0, y0, pw, ph, [(i / 300.0, _fir_resp(taps, i / 300.0) / dc) for i in range(301)], GREEN, 2.6)
    s += text(*(_pt(x0, y0, pw, ph, 0.55, 0.72)), "КІХ: 64 відводи", 10, GREEN, "start", "bold")
    s += _plot_path(x0, y0, pw, ph, [(i / 300.0, _butter_resp(i / 300.0, 0.3, 4)) for i in range(301)], BLUE, 2.2, dash="6,3")
    s += text(*(_pt(x0, y0, pw, ph, 0.42, 0.34)), "БІХ: ~9 коеф.", 10, BLUE, "start", "bold")
    s += text(w / 2, 266, "приблизно однаковий зріз — у БІХ у рази менше коефіцієнтів і обчислень", 9, GREY, "middle", "italic")
    save("fig-32-3-3-efficiency.svg", s)


def fig_stability():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Стабільний БІХ згасає, нестабільний — вибухає", 13.5, INK, "middle", "bold")

    def panel(x0, coef, title, col):
        out = text(x0 + 130, 58, title, 10, col, "middle", "bold")
        yb = 212
        out += line(x0, yb, x0 + 260, yb, FAINT, 1.2)
        y = 0.0
        vals = []
        for i in range(14):
            xin = 1.0 if i == 0 else 0.0
            y = coef * y + xin
            vals.append(y)
        mx = max(abs(v) for v in vals)
        for i, v in enumerate(vals):
            xx = x0 + 12 + i * 18
            out += line(xx, yb, xx, yb - (v / mx) * 150, col, 3)
            out += dot(xx, yb - (v / mx) * 150, 2.5, col)
        return out

    s += panel(60, 0.7, "стабільний (петля <1): згасає", GREEN)
    s += panel(400, 1.15, "нестабільний (петля >1): наростає", RED)
    s += text(w / 2, 252, "завдання проєктувальника — щоб петля згасала, а не розганялася", 9.5, GREY, "middle", "italic")
    save("fig-32-3-4-stability.svg", s)


def fig_biquad():
    w, h = 720, 240
    s = header(w, h)
    s += text(w / 2, 26, "Біквад — ланка 2-го порядку; складне будують каскадом", 12.5, INK, "middle", "bold")
    s += rect(40, 70, 200, 92, fill="#eef3fb", stroke=BLUE, sw=1.8, rx=8)
    s += text(140, 96, "БІКВАД", 12, BLUE, "middle", "bold")
    s += text(140, 116, "2 входи + 2 виходи", 9, GREY, "middle", "italic")
    s += text(140, 134, "5 коеф., ~5 множень", 9, GREY, "middle", "italic")
    s += text(140, 153, "БІХ 2-го порядку", 9.5, INK, "middle", "bold")
    s += arrow(248, 116, 292, 116, INK, 1.6)
    xs = [300, 392, 484, 576]
    for i, x in enumerate(xs):
        s += rect(x, 93, 80, 46, fill="#fbfbfb", stroke=PURP, sw=1.6, rx=6)
        s += text(x + 40, 121, "біквад " + str(i + 1), 9.5, PURP, "middle", "bold")
        if i < 3:
            s += arrow(x + 80, 116, xs[i + 1] - 2, 116, INK, 1.6)
    s += arrow(xs[3] + 80, 116, 690, 116, INK, 1.6)
    s += text(696, 121, "y", 11, INK, "start", "bold")
    s += text(w / 2, 210, "фільтр 8-го порядку = 4 біквади поспіль (стійкіше за одну довгу формулу)", 9.5, GREY, "middle", "italic")
    save("fig-32-3-5-biquad.svg", s)


def fig_phase_distort():
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 24, "КІХ зберігає форму; БІХ її спотворює", 13.5, INK, "middle", "bold")
    x0, pw = 70, 580

    def sig(x, d1, d2):
        return 0.5 * math.sin(2 * math.pi * 2 * (x - d1)) + 0.4 * math.sin(2 * math.pi * 5 * (x - d2))

    yc1 = 112
    s += line(x0, yc1, x0 + pw, yc1, FAINT, 1.0)
    s += poly([(x0 + (k / 300.0) * pw, yc1 - 38 * sig(k / 300.0, 0, 0)) for k in range(301)], GREY, 1.5)
    s += poly([(x0 + (k / 300.0) * pw, yc1 - 38 * sig(k / 300.0, 0.05, 0.05)) for k in range(301)], GREEN, 2.0)
    s += text(x0, yc1 - 58, "крізь КІХ: форма та сама, лише зсув", 10, GREEN, "start", "bold")
    yc2 = 242
    s += line(x0, yc2, x0 + pw, yc2, FAINT, 1.0)
    s += poly([(x0 + (k / 300.0) * pw, yc2 - 38 * sig(k / 300.0, 0, 0)) for k in range(301)], GREY, 1.5)
    s += poly([(x0 + (k / 300.0) * pw, yc2 - 38 * sig(k / 300.0, 0.03, 0.11)) for k in range(301)], RED, 2.0)
    s += text(x0, yc2 - 58, "крізь БІХ: частоти зсунуті по-різному → форма змінилась", 10, RED, "start", "bold")
    s += text(x0 + 0.02 * pw, yc1 + 52, "(сіре — вхід)", 8.5, GREY, "start", "italic")
    save("fig-32-3-6-phase-distort.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §32.4 Смугові фільтри: НЧ, ВЧ, смуговий
# ════════════════════════════════════════════════════════════════════════════

def _hpf_resp(fn, fc, order):
    if fn < 1e-6:
        return 0.0
    return 1.0 / math.sqrt(1.0 + (fc / fn) ** (2 * order))


def _bpf_resp(fn, f0, Q):
    if fn < 1e-6:
        return 0.0
    x = Q * (fn / f0 - f0 / fn)
    return 1.0 / math.sqrt(1.0 + x * x)


def _notch_resp(fn, f0, Q):
    if fn < 1e-6:
        return 1.0
    x = Q * (fn / f0 - f0 / fn)
    return abs(x) / math.sqrt(1.0 + x * x)


def fig_four_shapes():
    w, h = 720, 370
    s = header(w, h)
    s += text(w / 2, 24, "Чотири форми характеристики", 14.5, INK, "middle", "bold")
    panels = [(60, 70, "НЧ (ФНЧ)", "пропустити повільне", GREEN, lambda fn: _butter_resp(fn, 0.4, 4)),
              (390, 70, "ВЧ (ФВЧ)", "прибрати повільне/DC", BLUE, lambda fn: _hpf_resp(fn, 0.4, 4)),
              (60, 210, "Смуговий", "лишити одну смугу", PURP, lambda fn: _bpf_resp(fn, 0.45, 4)),
              (390, 210, "Режекторний", "вирізати одну смугу", RED, lambda fn: _notch_resp(fn, 0.45, 8))]
    pw, ph = 270, 110
    for (x0, ytop, title, sub, col, fn) in panels:
        y0 = ytop + ph
        s += arrow(x0, y0, x0, y0 - ph - 10, INK, 1.3)
        s += arrow(x0, y0, x0 + pw + 8, y0, INK, 1.3)
        s += _plot_path(x0, y0, pw, ph, [(i / 200.0, fn(i / 200.0)) for i in range(1, 201)], col, 2.4)
        s += text(x0, ytop - 10, title, 11.5, col, "start", "bold")
        s += text(x0 + pw, ytop - 10, sub, 8.5, GREY, "end", "italic")
    save("fig-32-4-1-four-shapes.svg", s)


def fig_lpf():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "ФНЧ: пропустити повільне, прибрати швидкий шум", 13, INK, "middle", "bold")
    tx, tyc, tpw, tph = 50, 130, 400, 58

    def base(x):
        return 0.6 * math.sin(2 * math.pi * 1.5 * x)

    def noisy(x):
        return base(x) + 0.18 * (math.sin(2 * math.pi * 22 * x) + math.sin(2 * math.pi * 31 * x + 1))

    s += line(tx, tyc, tx + tpw, tyc, FAINT, 1.0)
    s += poly([(tx + (k / 300.0) * tpw, tyc - tph * noisy(k / 300.0)) for k in range(301)], "#9bb0e0", 1.2)
    s += poly([(tx + (k / 300.0) * tpw, tyc - tph * base(k / 300.0)) for k in range(301)], GREEN, 2.2)
    s += text(tx + tpw / 2, 236, "сирий (шум) → згладжений (зелений)", 10, GREEN, "middle", "bold")
    rx, ry, rpw, rph = 500, 200, 180, 110
    s += arrow(rx, ry, rx, ry - rph - 10, INK, 1.3)
    s += arrow(rx, ry, rx + rpw + 8, ry, INK, 1.3)
    s += _plot_path(rx, ry, rpw, rph, [(i / 150.0, _butter_resp(i / 150.0, 0.25, 3)) for i in range(151)], GREEN, 2.2)
    s += text(rx + rpw / 2, ry + 18, "характеристика ФНЧ", 9, GREEN, "middle", "bold")
    save("fig-32-4-2-lpf.svg", s)


def fig_hpf():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "ФВЧ: прибрати постійне зміщення й дрейф", 13, INK, "middle", "bold")
    tx, tyc, tpw, tph = 50, 128, 400, 50

    def inp(x):
        return 0.45 * x - 0.1 + 0.25 * math.sin(2 * math.pi * 6 * x)

    def out(x):
        return 0.25 * math.sin(2 * math.pi * 6 * x)

    s += line(tx, tyc, tx + tpw, tyc, FAINT, 1.0)
    s += poly([(tx + (k / 300.0) * tpw, tyc - tph * inp(k / 300.0)) for k in range(301)], "#e0b09b", 1.6)
    s += poly([(tx + (k / 300.0) * tpw, tyc - tph * out(k / 300.0)) for k in range(301)], BLUE, 2.2)
    s += text(tx + tpw / 2, 236, "з дрейфом (помаранч.) → вирівняний (синій)", 10, BLUE, "middle", "bold")
    rx, ry, rpw, rph = 500, 200, 180, 110
    s += arrow(rx, ry, rx, ry - rph - 10, INK, 1.3)
    s += arrow(rx, ry, rx + rpw + 8, ry, INK, 1.3)
    s += _plot_path(rx, ry, rpw, rph, [(i / 150.0, _hpf_resp(i / 150.0, 0.2, 3)) for i in range(1, 151)], BLUE, 2.2)
    s += text(rx + rpw / 2, ry + 18, "характеристика ФВЧ", 9, BLUE, "middle", "bold")
    save("fig-32-4-3-hpf.svg", s)


def fig_bpf():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Смуговий: лишити одну смугу (центр f₀, ширина BW)", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 210, 580, 150
    s += arrow(x0, y0, x0, y0 - ph - 12, INK, 1.6)
    s += arrow(x0, y0, x0 + pw + 10, y0, INK, 1.6)
    s += text(x0 + pw + 8, y0 + 16, "частота →", 9, INK, "middle", "bold")
    f0 = 0.45
    s += line(x0, y0 - 0.707 * ph, x0 + pw, y0 - 0.707 * ph, GOLD, 1, dash="4,3")
    s += text(x0 - 4, y0 - 0.707 * ph + 4, "−3дБ", 8, "#9a7a1e", "end")
    s += _plot_path(x0, y0, pw, ph, [(i / 300.0, _bpf_resp(i / 300.0, f0, 3)) for i in range(1, 301)], PURP, 2.4)
    s += line(x0 + f0 * pw, y0, x0 + f0 * pw, y0 - ph, FAINT, 1, dash="3,3")
    s += text(x0 + f0 * pw, y0 + 16, "f₀", 10, PURP, "middle", "bold")
    s += text(x0 + f0 * pw, y0 - ph + 2, "смуга пропускання BW", 9, PURP, "middle", "bold")
    s += text(w / 2, 256, "вузька смуга = висока добротність Q = f₀/BW (гостріше, але дзвенить)", 9.5, GREY, "middle", "italic")
    save("fig-32-4-4-bpf.svg", s)


def fig_notch():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Режекторний (notch): вирізати вузьку смугу (гул 50 Гц)", 12.5, INK, "middle", "bold")
    tx, tyc, tpw, tph = 50, 130, 360, 50

    def withh(x):
        return 0.5 * math.sin(2 * math.pi * 2 * x) + 0.4 * math.sin(2 * math.pi * 30 * x)

    def clean(x):
        return 0.5 * math.sin(2 * math.pi * 2 * x)

    s += line(tx, tyc, tx + tpw, tyc, FAINT, 1.0)
    s += poly([(tx + (k / 300.0) * tpw, tyc - tph * withh(k / 300.0)) for k in range(301)], "#e0b0b0", 1.3)
    s += poly([(tx + (k / 300.0) * tpw, tyc - tph * clean(k / 300.0)) for k in range(301)], GREEN, 2.2)
    s += text(tx + tpw / 2, 236, "з гулом → без гулу", 10, GREEN, "middle", "bold")
    rx, ry, rpw, rph = 460, 200, 210, 120
    s += arrow(rx, ry, rx, ry - rph - 10, INK, 1.3)
    s += arrow(rx, ry, rx + rpw + 8, ry, INK, 1.3)
    s += _plot_path(rx, ry, rpw, rph, [(i / 200.0, _notch_resp(i / 200.0, 0.5, 12)) for i in range(1, 201)], RED, 2.2)
    s += line(rx + 0.5 * rpw, ry, rx + 0.5 * rpw, ry - rph, FAINT, 1, dash="3,3")
    s += text(rx + 0.5 * rpw, ry + 16, "50 Гц", 9, RED, "middle", "bold")
    s += text(rx + rpw / 2, ry - rph - 2, "вузький провал, решта ціла", 8.5, RED, "middle", "italic")
    save("fig-32-4-5-notch.svg", s)


def fig_relations():
    w, h = 740, 280
    s = header(w, h)
    s += text(w / 2, 24, "Як вони пов'язані: усе виводиться з ФНЧ", 13.5, INK, "middle", "bold")
    panels = [("ФВЧ", lambda fn: _hpf_resp(fn, 0.4, 3), BLUE, "= 1 − ФНЧ"),
              ("смуговий", lambda fn: _bpf_resp(fn, 0.45, 3), PURP, "= ФВЧ ∘ ФНЧ"),
              ("режекторний", lambda fn: _notch_resp(fn, 0.45, 6), RED, "= 1 − смуговий")]
    pw, ph = 200, 110
    xs = [40, 290, 540]
    for (x0, (title, fn, col, rel)) in zip(xs, panels):
        y0 = 190
        s += arrow(x0, y0, x0, y0 - ph - 10, INK, 1.3)
        s += arrow(x0, y0, x0 + pw + 6, y0, INK, 1.3)
        s += _plot_path(x0, y0, pw, ph, [(i / 150.0, fn(i / 150.0)) for i in range(1, 151)], col, 2.2)
        s += text(x0 + pw / 2, 68, title, 11, col, "middle", "bold")
        s += text(x0 + pw / 2, 228, rel, 9.5, GREY, "middle", "italic")
    s += text(w / 2, 258, "опанувавши ФНЧ, ви маєте всі чотири типи — решта виводиться з нього", 9.5, GREY, "middle", "italic")
    save("fig-32-4-6-relations.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §32.5 Реалізація на МК: fixed-point і швидкодія
# ════════════════════════════════════════════════════════════════════════════

def fig_float_fixed():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Без FPU ціла арифметика в десятки разів швидша за float", 12.5, INK, "middle", "bold")
    x0, y0 = 150, 200
    barw = 120
    items = [("float (емуляція)", "~60 тактів", 60, RED), ("ціле (нативно)", "~2 такти", 2, GREEN)]
    for i, (lbl, val, c, col) in enumerate(items):
        x = x0 + i * 270
        bh = (c / 60.0) * 150
        s += rect(x, y0 - bh, barw, bh, fill=col, stroke=INK, sw=1.2, rx=4)
        s += text(x + barw / 2, y0 + 18, lbl, 10.5, col, "middle", "bold")
        s += text(x + barw / 2, y0 - bh - 8, val, 10, INK, "middle", "bold")
    s += text(w / 2, 236, "на чипах без апаратного float кожна операція з комою емулюється — дорого", 9.5, GREY, "middle", "italic")
    save("fig-32-5-1-float-fixed.svg", s)


def fig_qformat():
    w, h = 740, 240
    s = header(w, h)
    s += text(w / 2, 26, "Формат Q15: дроби як масштабовані цілі", 13, INK, "middle", "bold")
    s += rect(40, 70, 150, 50, fill="#eef3fb", stroke=BLUE, sw=1.6, rx=8)
    s += text(115, 100, "0.5  (дріб)", 12, BLUE, "middle", "bold")
    s += arrow(192, 95, 250, 95, INK, 1.8)
    s += text(221, 85, "×32768", 9, GREY, "middle", "italic")
    s += rect(254, 70, 170, 50, fill="#eef7ef", stroke=GREEN, sw=1.6, rx=8)
    s += text(339, 100, "16384  (Q15 ціле)", 11, GREEN, "middle", "bold")
    s += text(560, 92, "кома «зашита»", 9, GREY, "middle", "italic")
    s += text(560, 106, "в масштабі 2¹⁵", 9, GREY, "middle", "italic")
    s += text(60, 162, "множення:", 11, INK, "start", "bold")
    s += text(60, 188, "Q15 × Q15  →  Q30   (добуток у ширшому регістрі)", 11.5, INK, "start")
    s += text(60, 214, "Q30  >> 15  →  Q15   (зсув коми назад у масштаб)", 11.5, INK, "start")
    save("fig-32-5-2-qformat.svg", s)


def fig_accumulator():
    w, h = 720, 240
    s = header(w, h)
    s += text(w / 2, 26, "Акумулятор має бути ширший за відліки", 13, INK, "middle", "bold")

    def bar(x, y, bits, lbl, col):
        bw = 64 * 4
        out = rect(x, y, bw, 26, fill="#ffffff", stroke=INK, sw=1, rx=3)
        out += rect(x, y, bits * 4, 26, fill=col, stroke="none", sw=0)
        out += text(x + bw + 8, y + 18, lbl, 10, INK, "start", "bold")
        return out

    s += bar(60, 66, 16, "відлік 16 біт", BLUE)
    s += bar(60, 100, 16, "× коеф. 16 біт", GREEN)
    s += bar(60, 134, 32, "= добуток 32 біт", GOLD)
    s += bar(60, 168, 64, "Σ акумулятор 64 біт (із запасом)", PURP)
    s += text(60, 212, "вузький акумулятор переповнюється на сумі — бери 32/64-бітний", 9.5, GREY, "start", "italic")
    save("fig-32-5-3-accumulator.svg", s)


def fig_overflow_sat():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Переповнення: згубне загортання vs безпечне насичення", 12, INK, "middle", "bold")
    x0, yc, pw = 70, 140, 580
    s += line(x0, yc, x0 + pw, yc, FAINT, 1.0)
    s += line(x0, yc - 60, x0 + pw, yc - 60, FAINT, 1, dash="4,3")
    s += text(x0 - 4, yc - 60, "+макс", 8, GREY, "end")
    s += line(x0, yc + 60, x0 + pw, yc + 60, FAINT, 1, dash="4,3")
    s += text(x0 - 4, yc + 64, "−макс", 8, GREY, "end")

    def val(x):
        return (x - 0.5) * 2.4

    def wrap(v):
        return ((v + 1) % 2) - 1

    def sat(v):
        return max(-1.0, min(1.0, v))

    s += poly([(x0 + (k / 300.0) * pw, yc - 60 * wrap(val(k / 300.0))) for k in range(301)], RED, 2.0)
    s += poly([(x0 + (k / 300.0) * pw, yc - 60 * sat(val(k / 300.0))) for k in range(301)], GREEN, 2.4)
    s += text(x0 + 0.62 * pw, yc - 92, "загортання (wrap): дикий стрибок", 9.5, RED, "start", "bold")
    s += text(x0 + 0.05 * pw, yc + 95, "насичення (sat): впирається в межу", 9.5, GREEN, "start", "bold")
    s += text(w / 2, 244, "ніколи не давай сумі тихо «загорнутися» — затискай (saturate) на межі", 9.5, GREY, "middle", "italic")
    save("fig-32-5-4-overflow-sat.svg", s)


def fig_coef_quant():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Квантування коефіцієнтів трохи зсуває характеристику", 12, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 220, 580, 160
    s += arrow(x0, y0, x0, y0 - ph - 12, INK, 1.6)
    s += arrow(x0, y0, x0 + pw + 10, y0, INK, 1.6)
    s += text(x0 + pw + 8, y0 + 16, "частота →", 9, INK, "middle", "bold")
    taps = _lp_taps(16, 0.3)
    q = [round(t * 15) / 15.0 for t in taps]
    dc, dcq = sum(taps), (sum(q) if abs(sum(q)) > 1e-9 else 1.0)
    s += _plot_path(x0, y0, pw, ph, [(i / 300.0, _fir_resp(taps, i / 300.0) / dc) for i in range(301)], GREEN, 2.4)
    s += _plot_path(x0, y0, pw, ph, [(i / 300.0, _fir_resp(q, i / 300.0) / dcq) for i in range(301)], RED, 2.0, dash="5,3")
    s += text(*(_pt(x0, y0, pw, ph, 0.5, 0.7)), "ідеальні коеф.", 9.5, GREEN, "start", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.42, 0.36)), "грубо квантовані", 9.5, RED, "start", "bold")
    s += text(w / 2, 256, "округлення коеф. псує характеристику; для БІХ може й дестабілізувати (§32.3)", 9, GREY, "middle", "italic")
    save("fig-32-5-5-coef-quant.svg", s)


def fig_budget():
    w, h = 720, 220
    s = header(w, h)
    s += text(w / 2, 26, "Бюджет реального часу: фільтр має влізти в період відліку", 12, INK, "middle", "bold")
    x0, y, barw, barh = 70, 110, 560, 40
    s += rect(x0, y, barw, barh, fill="#ffffff", stroke=INK, sw=1.5, rx=4)
    s += text(x0 + barw / 2, y - 10, "період відліку  T = 1/fs", 10, INK, "middle", "bold")
    s += rect(x0, y, barw * 0.35, barh, fill="#eef7ef", stroke=GREEN, sw=1.2, rx=4)
    s += text(x0 + barw * 0.175, y + 25, "фільтр", 10, GREEN, "middle", "bold")
    s += text(x0 + barw * 0.67, y + 25, "запас на решту", 10, GREY, "middle", "italic")
    s += text(w / 2, 182, "усі MAC-и фільтра + інше мусять укластися в T; не влізли — нижчий fs або легший фільтр", 9, GREY, "middle", "italic")
    save("fig-32-5-6-budget.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §32.6 КІХ vs БІХ: коли що
# ════════════════════════════════════════════════════════════════════════════

def fig_comparison():
    w, h = 720, 340
    s = header(w, h)
    s += text(w / 2, 26, "КІХ vs БІХ за критеріями вибору", 14.5, INK, "middle", "bold")
    cxk, cxb = 445, 615
    s += rect(cxk - 55, 44, 110, 30, fill="#eef7ef", stroke=GREEN, sw=1.5, rx=6)
    s += text(cxk, 64, "КІХ", 13, GREEN, "middle", "bold")
    s += rect(cxb - 55, 44, 110, 30, fill="#eef3fb", stroke=BLUE, sw=1.5, rx=6)
    s += text(cxb, 64, "БІХ", 13, BLUE, "middle", "bold")
    rows = [("Стабільність", "завжди ✓✓", GREEN, "пильнувати ~", "#9a7a1e"),
            ("Лінійна фаза (форма)", "так ✓✓", GREEN, "ні ✗", RED),
            ("Гострість за коеф.", "дорого ✗", RED, "дешево ✓✓", GREEN),
            ("Обчислення, пам'ять", "більше", RED, "менше", GREEN),
            ("Затримка", "більша", RED, "менша", GREEN),
            ("Fixed-point", "стійкий ✓", GREEN, "чутливий ~", "#9a7a1e"),
            ("Складність", "проста ✓", GREEN, "хитріша (біквади)", "#9a7a1e")]
    y = 100
    for i, (cr, kt, kc, bt, bc) in enumerate(rows):
        if i % 2 == 0:
            s += rect(20, y - 18, 680, 30, fill="#f6f6f6", stroke="none", sw=0, rx=4)
        s += text(32, y, cr, 11.5, INK, "start", "bold")
        s += text(cxk, y, kt, 10.5, kc, "middle", "bold")
        s += text(cxb, y, bt, 10.5, bc, "middle", "bold")
        y += 32
    s += text(w / 2, y + 8, "усе, у чому сильний один, — слабке місце другого", 10, GREY, "middle", "italic")
    save("fig-32-6-1-comparison.svg", s)


def fig_decision_tree():
    w, h = 720, 330
    s = header(w, h)
    s += text(w / 2, 26, "КІХ чи БІХ: дерево рішення", 14.5, INK, "middle", "bold")
    s += rect(250, 56, 220, 48, fill="#fbfbfb", stroke=INK, sw=1.8, rx=8)
    s += text(360, 78, "Форма сигналу важлива?", 11, INK, "middle", "bold")
    s += text(360, 95, "(ЕКГ, фронти, точна хвиля)", 8.5, GREY, "middle", "italic")
    s += arrow(285, 104, 160, 150, GREEN, 1.6)
    s += text(205, 122, "так", 9, GREEN, "middle", "bold")
    s += rect(70, 150, 170, 44, fill="#eef7ef", stroke=GREEN, sw=1.8, rx=8)
    s += text(155, 170, "КІХ", 13, GREEN, "middle", "bold")
    s += text(155, 187, "(лінійна фаза)", 8.5, GREY, "middle", "italic")
    s += text(155, 214, "безпека критична → теж КІХ", 8.5, GREEN, "middle", "italic")
    s += arrow(440, 104, 510, 150, INK, 1.6)
    s += text(490, 122, "ні", 9, GREY, "middle", "bold")
    s += rect(400, 150, 250, 48, fill="#fbfbfb", stroke=INK, sw=1.8, rx=8)
    s += text(525, 172, "Гострий фільтр + тісні ресурси?", 10, INK, "middle", "bold")
    s += text(525, 189, "(крутий зріз на дешевому чипі)", 8.5, GREY, "middle", "italic")
    s += arrow(470, 198, 400, 244, BLUE, 1.6)
    s += text(418, 224, "так", 9, BLUE, "middle", "bold")
    s += rect(310, 244, 170, 44, fill="#eef3fb", stroke=BLUE, sw=1.8, rx=8)
    s += text(395, 264, "БІХ", 13, BLUE, "middle", "bold")
    s += text(395, 281, "(ефективність)", 8.5, GREY, "middle", "italic")
    s += arrow(590, 198, 640, 244, GREY, 1.6)
    s += text(628, 224, "ні", 9, GREY, "middle", "bold")
    s += rect(520, 244, 180, 44, fill="#ffffff", stroke=GREY, sw=1.5, rx=8)
    s += text(610, 264, "будь-який", 11, INK, "middle", "bold")
    s += text(610, 281, "(найдешевше: EMA)", 8.5, GREY, "middle", "italic")
    save("fig-32-6-2-decision-tree.svg", s)


def fig_recipes():
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Готові рецепти: задача → сімейство", 14, INK, "middle", "bold")
    rows = [("ЕКГ, форма хвилі, фронти", "КІХ", GREEN, "лінійна фаза"),
            ("Гострий notch 50 Гц на дешевому чипі", "БІХ-біквад", BLUE, "гостро за копійки"),
            ("Просте згладжування шуму", "EMA", PURP, "найдешевший БІХ"),
            ("Безпечний фільтр у керуванні", "КІХ", GREEN, "стабільність"),
            ("Копія аналогового фільтра", "БІХ", BLUE, "нащадок Баттерворта")]
    y = 82
    for (task, fam, col, note) in rows:
        s += text(40, y, "• " + task, 11.5, INK, "start")
        s += arrow(398, y - 4, 430, y - 4, INK, 1.4)
        s += rect(436, y - 20, 116, 26, fill="#fbfbfb", stroke=col, sw=1.5, rx=6)
        s += text(494, y - 2, fam, 11, col, "middle", "bold")
        s += text(560, y, note, 9, GREY, "start", "italic")
        y += 42
    s += text(w / 2, y + 6, "задача підказує сімейство майже сама", 10, GREY, "middle", "italic")
    save("fig-32-6-3-recipes.svg", s)


def fig_already_know():
    w, h = 720, 230
    s = header(w, h)
    s += text(w / 2, 28, "Ви вже знаєте обидва (Розділ 30)", 14, INK, "middle", "bold")
    s += rect(50, 70, 290, 110, fill="#eef7ef", stroke=GREEN, sw=2, rx=10)
    s += text(195, 98, "Ковзне середнє (§30.2)", 12, GREEN, "middle", "bold")
    s += text(195, 122, "= найпростіший КІХ", 11, INK, "middle", "bold")
    s += text(195, 146, "рівні відводи · скінченна пам'ять", 9, GREY, "middle", "italic")
    s += text(195, 164, "лінійна фаза · завжди стійкий", 9, GREY, "middle", "italic")
    s += rect(380, 70, 290, 110, fill="#eef3fb", stroke=BLUE, sw=2, rx=10)
    s += text(525, 98, "EMA (§30.4)", 12, BLUE, "middle", "bold")
    s += text(525, 122, "= найпростіший БІХ", 11, INK, "middle", "bold")
    s += text(525, 146, "зворотний зв'язок · нескінченний хвіст", 9, GREY, "middle", "italic")
    s += text(525, 164, "один коефіцієнт α · гранична ефективність", 9, GREY, "middle", "italic")
    s += text(w / 2, 210, "те, що ви робили на інтуїції, — окремі випадки двох великих сімейств", 10, GREY, "middle", "italic")
    save("fig-32-6-4-already-know.svg", s)


def fig_tradeoff():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Безплатного фільтра нема: розмін переваг", 13.5, INK, "middle", "bold")
    cx, cy = 360, 150
    s += polygon([(cx - 14, cy + 42), (cx + 14, cy + 42), (cx, cy)], GREY, INK, 1)
    s += line(cx - 200, cy - 2, cx + 200, cy - 2, INK, 3)
    s += line(cx - 180, cy - 2, cx - 180, cy + 28, INK, 1.4)
    s += rect(cx - 260, cy + 28, 160, 60, fill="#eef7ef", stroke=GREEN, sw=1.8, rx=8)
    s += text(cx - 180, cy + 50, "КІХ", 12, GREEN, "middle", "bold")
    s += text(cx - 180, cy + 70, "безпека + форма", 9, GREY, "middle", "italic")
    s += line(cx + 180, cy - 2, cx + 180, cy + 28, INK, 1.4)
    s += rect(cx + 100, cy + 28, 160, 60, fill="#eef3fb", stroke=BLUE, sw=1.8, rx=8)
    s += text(cx + 180, cy + 50, "БІХ", 12, BLUE, "middle", "bold")
    s += text(cx + 180, cy + 70, "ефективність + гострота", 9, GREY, "middle", "italic")
    s += text(w / 2, 252, "схиляєш в один бік — відмовляєшся від переваг другого", 10, GREY, "middle", "italic")
    save("fig-32-6-5-tradeoff.svg", s)


def fig_toolbox():
    w, h = 740, 300
    s = header(w, h)
    s += text(w / 2, 26, "Завершений інструментарій фільтрів (Розділи 30–32)", 13, INK, "middle", "bold")
    cols = [("Розділ 30", "часові фільтри", GREEN, ["ковзне середнє", "медіана", "EMA"]),
            ("Розділ 31", "частотний погляд", BLUE, ["спектр", "Фур'є / ШПФ", "чому фільтри діють"]),
            ("Розділ 32", "проєктування", PURP, ["КІХ і БІХ", "НЧ·ВЧ·смуг.·notch", "реалізація на МК"])]
    bw, xs = 220, [20, 260, 500]
    for k, (x, (t1, t2, col, items)) in enumerate(zip(xs, cols)):
        s += rect(x, 60, bw, 200, fill="#fbfbfb", stroke=col, sw=1.8, rx=10)
        s += text(x + bw / 2, 88, t1, 12.5, col, "middle", "bold")
        s += text(x + bw / 2, 107, t2, 10, GREY, "middle", "italic")
        s += line(x + 16, 118, x + bw - 16, 118, FAINT, 1)
        for j, it in enumerate(items):
            s += text(x + bw / 2, 150 + j * 30, "• " + it, 11, INK, "middle")
        if k < 2:
            s += arrow(x + bw + 2, 160, xs[k + 1] - 2, 160, INK, 1.8)
    s += text(w / 2, 284, "від «згладити на око» до «спроєктувати під специфікацію»", 10, GREY, "middle", "italic")
    save("fig-32-6-6-toolbox.svg", s)


if __name__ == "__main__":
    # §32.1 Фільтр як «формувач спектра»
    fig_shaper()
    fig_response_anatomy()
    fig_movavg_response()
    fig_ema_response()
    fig_ideal_real()
    fig_design_flow()
    # §32.2 КІХ-фільтр (FIR)
    fig_fir_structure()
    fig_impulse()
    fig_taps_shape()
    fig_linear_phase()
    fig_fir_impl()
    fig_more_taps()
    # §32.3 БІХ-фільтр (IIR)
    fig_iir_structure()
    fig_iir_impulse()
    fig_efficiency()
    fig_stability()
    fig_biquad()
    fig_phase_distort()
    # §32.4 Смугові фільтри
    fig_four_shapes()
    fig_lpf()
    fig_hpf()
    fig_bpf()
    fig_notch()
    fig_relations()
    # §32.5 Реалізація на МК
    fig_float_fixed()
    fig_qformat()
    fig_accumulator()
    fig_overflow_sat()
    fig_coef_quant()
    fig_budget()
    # §32.6 КІХ vs БІХ
    fig_comparison()
    fig_decision_tree()
    fig_recipes()
    fig_already_know()
    fig_tradeoff()
    fig_toolbox()
    print("OK — фігури §32.1–§32.6 згенеровано в", OUT)
