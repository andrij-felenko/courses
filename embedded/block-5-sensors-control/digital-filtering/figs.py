# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 30 — «Цифрова фільтрація сигналів» (Модуль 5).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; сигнал/поле зелене, шум синій, викид червоний;
стрілки через marker; шрифт sans-serif. Підписи нумеруються посекційно
(Рис. C.S.N) у тексті розділу. Спільні помічники скопійовано зі стилю Розділів 28–29.
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


def noise(t, phase=0.0):
    """Детермінований шумоподібний сигнал у [-1..1] (сума несумірних синусів)."""
    return (math.sin(0.7 * t + phase) + math.sin(1.7 * t + 1.3)
            + math.sin(2.9 * t + 2.1) + math.sin(5.3 * t + 0.7)) / 4.0


# ════════════════════════════════════════════════════════════════════════════
#  §30.1 Шум у сигналі: чому давачі «брешуть»
# ════════════════════════════════════════════════════════════════════════════

def fig_noisy_stream():
    w, h = 680, 300
    s = header(w, h)
    s += text(w / 2, 26, "Що ми хочемо vs що отримуємо: істина і зашумлені відліки",
              14, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 250, 560, 190
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 - 8, y0 - ph - 4, "значення", 11, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    # істинне значення — полога крива
    true = [(j / 60, 0.5 + 0.18 * math.sin(2 * math.pi * 0.8 * j / 60)) for j in range(61)]
    s += _plot_path(x0, y0, pw, ph, true, GREEN, 2.6)
    s += text(*(_pt(x0, y0, pw, ph, 0.05, 0.78)), "істинне значення (хочемо)", 10.5, GREEN, "start", "bold")
    # зашумлені відліки — точки
    for j in range(0, 61, 2):
        xv = j / 60
        uv = 0.5 + 0.18 * math.sin(2 * math.pi * 0.8 * j / 60) + 0.13 * noise(j * 1.7)
        s += dot(*_pt(x0, y0, pw, ph, xv, uv), 3, BLUE)
    s += text(*(_pt(x0, y0, pw, ph, 0.55, 0.18)), "відліки давача (маємо)", 10.5, BLUE, "start", "bold")
    save("fig-30-1-1-noisy-stream.svg", s)


def fig_three_lies():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Три способи, якими давач «бреше» — і три різні ліки",
              14.5, INK, "middle", "bold")
    cases = [("випадкове тремтіння", BLUE, "усереднення / фільтр"),
             ("поодинокі викиди", RED, "медіана / відсів"),
             ("повільний дрейф", GOLD, "калібрування")]
    pw, py, ph = 224, 50, 192
    for i, (title, col, fix) in enumerate(cases):
        x = 16 + i * 232
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=col, sw=1.4, rx=8)
        s += text(x + pw / 2, py + 22, title, 12, col, "middle", "bold")
        gx, gy, gw, gh = x + 24, py + 130, pw - 48, 70
        s += line(gx, gy - gh / 2, gx + gw, gy - gh / 2, FAINT, 1, dash="4,3")
        if i == 0:
            pts = [(k / 24, 0.5 + 0.32 * noise(k * 1.9)) for k in range(25)]
            s += _plot_path(gx, gy, gw, gh, pts, BLUE, 1.6)
        elif i == 1:
            pts = []
            for k in range(25):
                v = 0.5 + 0.05 * noise(k)
                if k in (7, 16):
                    v = 0.95
                pts.append((k / 24, v))
            s += _plot_path(gx, gy, gw, gh, pts, RED, 1.6)
        else:
            pts = [(k / 24, 0.25 + 0.5 * (k / 24) + 0.04 * noise(k)) for k in range(25)]
            s += _plot_path(gx, gy, gw, gh, pts, GOLD, 1.8)
        s += text(x + pw / 2, py + ph - 30, "лік:", 10, GREY, "middle", "bold")
        s += text(x + pw / 2, py + ph - 14, fix, 11, col, "middle", "bold")
    save("fig-30-1-2-three-lies.svg", s)


def fig_signal_noise():
    w, h = 680, 280
    s = header(w, h)
    s += text(w / 2, 26, "Сигнал (хочемо) і шум (заважає) — розділити їх і є задача",
              14, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 240, 560, 180
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    sig = [(j / 80, 0.5 + 0.28 * math.sin(2 * math.pi * 1.2 * j / 80)) for j in range(81)]
    noisy = [(xv, uv + 0.12 * noise(j * 2.1)) for j, (xv, uv) in enumerate(sig)]
    s += _plot_path(x0, y0, pw, ph, noisy, BLUE, 1.4)
    s += _plot_path(x0, y0, pw, ph, sig, GREEN, 2.6)
    s += text(*(_pt(x0, y0, pw, ph, 0.04, 0.86)), "сигнал — справжня зміна величини", 10.5, GREEN, "start", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.5, 0.1)), "сигнал + шум — те, що зчитав давач", 10.5, BLUE, "start", "bold")
    s += text(w / 2, 270, "фільтр пропускає сигнал і гасить шум — та вони частково перекриваються",
              11, GREY, "middle", "italic")
    save("fig-30-1-3-signal-noise.svg", s)


def fig_tradeoff():
    w, h = 700, 300
    s = header(w, h)
    s += text(w / 2, 26, "Головний компроміс: згладжування ↔ затримка",
              15, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 250, 560, 190
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    # справжній стрибок
    step = [(0, 0.3)] + [(0.4, 0.3), (0.4, 0.7)] + [(1, 0.7)]
    s += _plot_path(x0, y0, pw, ph, step, GREY, 1.6, dash="5,3")
    s += text(*(_pt(x0, y0, pw, ph, 0.06, 0.36)), "справжня зміна", 10, GREY, "start", "italic")
    # легкий фільтр — швидко, але шумно
    light = []
    for j in range(81):
        xv = j / 80
        base = 0.3 if xv < 0.4 else 0.7
        light.append((xv, base + 0.06 * noise(j * 2.3)))
    s += _plot_path(x0, y0, pw, ph, light, BLUE, 1.6)
    s += text(*(_pt(x0, y0, pw, ph, 0.62, 0.86)), "легкий фільтр: швидко, та шумно", 10, BLUE, "start", "bold")
    # важкий фільтр — гладко, але із затримкою
    heavy = []
    for j in range(81):
        xv = j / 80
        if xv < 0.4:
            v = 0.3
        else:
            v = 0.7 - 0.4 * math.exp(-(xv - 0.4) / 0.18)
        heavy.append((xv, v))
    s += _plot_path(x0, y0, pw, ph, heavy, RED, 2.2)
    s += text(*(_pt(x0, y0, pw, ph, 0.5, 0.3)), "важкий фільтр: гладко, та з затримкою", 10, RED, "start", "bold")
    save("fig-30-1-4-tradeoff.svg", s)


def fig_digital_analog():
    w, h = 700, 250
    s = header(w, h)
    s += text(w / 2, 26, "Фільтрувати в залізі (RC) чи в програмі (числа)",
              14.5, INK, "middle", "bold")
    # аналоговий
    s += rect(24, 50, 320, 170, fill="#fbf6ee", stroke=GOLD, sw=1.4, rx=8)
    s += text(184, 72, "аналоговий: RC-ланка", 12, "#9a7a1e", "middle", "bold")
    s += line(60, 130, 110, 130, INK, 2)
    # резистор
    s += poly([(110, 130), (118, 122), (128, 138), (138, 122), (148, 138), (158, 122), (166, 130)], INK, 2)
    s += line(166, 130, 230, 130, INK, 2)
    s += line(230, 130, 230, 150, INK, 2)
    s += line(216, 150, 244, 150, INK, 3)
    s += line(216, 158, 244, 158, INK, 3)
    s += line(230, 158, 230, 178, INK, 2)
    s += line(60, 178, 280, 178, INK, 1.6)
    s += line(60, 130, 60, 178, INK, 1.6)
    s += text(230, 200, "фіксована, дрейфує, дешева", 10, INK, "middle", "italic")
    # цифровий
    s += rect(360, 50, 316, 170, fill="#eef4fb", stroke=BLUE, sw=1.4, rx=8)
    s += text(518, 72, "цифровий: фільтр у коді", 12, BLUE, "middle", "bold")
    for j, x in enumerate([400, 440, 480, 520]):
        s += dot(x, 120 + (10 if j % 2 else -8), 3, BLUE)
    s += arrow(548, 116, 588, 116, INK, 1.8)
    s += rect(588, 100, 60, 34, fill="#fff", stroke=GREEN, sw=1.5, rx=5)
    s += text(618, 121, "filter()", 10, GREEN, "middle", "bold")
    s += text(518, 160, "відліки АЦП → програма", 10, INK, "middle", "italic")
    s += text(518, 200, "гнучка, без дрейфу, їсть такти", 10, INK, "middle", "italic")
    save("fig-30-1-5-digital-analog.svg", s)


def fig_chapter_map():
    w, h = 700, 240
    s = header(w, h)
    s += text(w / 2, 28, "Задача розділу: зашумлений потік → чиста оцінка",
              15, INK, "middle", "bold")
    s += rect(40, 80, 150, 56, fill="#eef4fb", stroke=BLUE, sw=1.6, rx=8)
    s += text(115, 104, "зашумлений", 11.5, BLUE, "middle", "bold")
    s += text(115, 122, "потік відліків", 11.5, BLUE, "middle", "bold")
    s += rect(275, 80, 150, 56, fill="#eef6ef", stroke=GREEN, sw=1.8, rx=8)
    s += text(350, 104, "ФІЛЬТР", 13, GREEN, "middle", "bold")
    s += text(350, 122, "(дешевий, у реальному часі)", 9, INK, "middle", "italic")
    s += rect(510, 80, 150, 56, fill="#f1f7f1", stroke=GREEN, sw=1.6, rx=8)
    s += text(585, 104, "чиста", 11.5, GREEN, "middle", "bold")
    s += text(585, 122, "оцінка величини", 11.5, GREEN, "middle", "bold")
    s += arrow(192, 108, 273, 108, INK, 2)
    s += arrow(427, 108, 508, 108, INK, 2)
    s += text(w / 2, 176, "інструменти попереду: ковзне середнє (§30.2) · медіана (§30.3) · EMA (§30.4)",
              11.5, INK, "middle", "bold")
    s += text(w / 2, 200, "…і компроміс згладжування ↔ затримка (§30.5), який вирішує вибір",
              11, GREY, "middle", "italic")
    save("fig-30-1-6-chapter-map.svg", s)


def _movavg(xs, N):
    out = []
    for i in range(len(xs)):
        lo = max(0, i - N + 1)
        win = xs[lo:i + 1]
        out.append(sum(win) / len(win))
    return out


# ════════════════════════════════════════════════════════════════════════════
#  §30.2 Ковзне середнє
# ════════════════════════════════════════════════════════════════════════════

def fig_window():
    w, h = 680, 260
    s = header(w, h)
    s += text(w / 2, 26, "Ковзне середнє: вікно з N відліків ковзає потоком",
              14.5, INK, "middle", "bold")
    y = 140
    xs = [70 + i * 42 for i in range(14)]
    vals = [0.5 + 0.3 * noise(i * 1.7) for i in range(14)]
    for i, x in enumerate(xs):
        s += dot(x, y - vals[i] * 60 + 30, 4, BLUE)
    s += text(70, 220, "потік відліків x[n]", 11, BLUE, "start", "bold")
    # вікно над останніми N=5
    wx0 = xs[8] - 18
    wx1 = xs[12] + 18
    s += rect(wx0, 70, wx1 - wx0, 110, fill="none", stroke=GREEN, sw=2, rx=6)
    s += text((wx0 + wx1) / 2, 64, "вікно N", 11, GREEN, "middle", "bold")
    # середнє → вихід
    mean = sum(vals[8:13]) / 5
    oy = y - mean * 60 + 30
    s += dot((wx0 + wx1) / 2, oy, 6, GREEN)
    s += arrow((wx0 + wx1) / 2, 184, (wx0 + wx1) / 2, oy + 10, GREEN, 1.6)
    s += text((wx0 + wx1) / 2, 200, "вихід = середнє", 10, GREEN, "middle", "bold")
    s += arrow(wx1 + 6, 125, wx1 + 40, 125, INK, 1.8)
    s += text(wx1 + 24, 112, "ковзає →", 9.5, INK, "middle", "italic")
    save("fig-30-2-1-window.svg", s)


def fig_result():
    w, h = 680, 280
    s = header(w, h)
    s += text(w / 2, 26, "Зашумлений вхід → згладжений вихід ковзного середнього",
              14, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 250, 560, 190
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    base = [0.5 + 0.16 * math.sin(2 * math.pi * 0.9 * j / 70) for j in range(71)]
    noisy = [b + 0.14 * noise(j * 2.1) for j, b in enumerate(base)]
    sm = _movavg(noisy, 8)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(noisy)], BLUE, 1.4)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(sm)], GREEN, 2.6)
    s += text(*(_pt(x0, y0, pw, ph, 0.5, 0.12)), "вхід (шум)", 10.5, BLUE, "start", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.05, 0.85)), "вихід (N=8)", 10.5, GREEN, "start", "bold")
    save("fig-30-2-2-result.svg", s)


def fig_running_sum():
    w, h = 700, 240
    s = header(w, h)
    s += text(w / 2, 26, "Ковзна сума: додай новий, відніми найстаріший — O(1)",
              14, INK, "middle", "bold")
    # буфер
    bx, by = 200, 100
    vals = [12, 11, 13, 10, 15]
    for i, v in enumerate(vals):
        col = GREEN if i == 4 else (RED if i == 3 else INK)
        s += rect(bx + i * 56, by, 52, 40, fill="#fbfbfb", stroke=col, sw=1.6, rx=4)
        s += text(bx + i * 56 + 26, by + 26, str(v), 14, col, "middle", "bold")
    s += text(bx + 130, by - 12, "кільцевий буфер (N=5)", 11, GREY, "middle", "italic")
    s += arrow(bx + 4 * 56 + 26, by - 24, bx + 4 * 56 + 26, by - 4, GREEN, 1.8)
    s += text(bx + 4 * 56 + 26, by - 30, "+ новий", 9.5, GREEN, "middle", "bold")
    s += arrow(bx + 3 * 56 + 26, by + 64, bx + 3 * 56 + 26, by + 44, RED, 1.8)
    s += text(bx + 3 * 56 + 26, by + 78, "− найстаріший", 9.5, RED, "middle", "bold")
    # сума → /N → вихід
    s += arrow(bx + 5 * 56, by + 20, bx + 5 * 56 + 30, by + 20, INK, 1.8)
    s += rect(bx + 5 * 56 + 32, by, 70, 40, fill="#eef6ef", stroke=GREEN, sw=1.6, rx=5)
    s += text(bx + 5 * 56 + 67, by + 18, "сума/N", 10.5, GREEN, "middle", "bold")
    s += text(bx + 5 * 56 + 67, by + 33, "= вихід", 9.5, INK, "middle")
    s += text(w / 2, 200, "вартість кроку не залежить від N — завжди плюс новий, мінус старий",
              11, GREY, "middle", "italic")
    save("fig-30-2-3-running-sum.svg", s)


def fig_window_size():
    w, h = 700, 290
    s = header(w, h)
    s += text(w / 2, 26, "Розмір вікна: мале — спритно й шумно, велике — гладко й із затримкою",
              12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 250, 560, 190
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    base = [0.3 if j < 35 else 0.7 for j in range(71)]
    noisy = [b + 0.1 * noise(j * 2.3) for j, b in enumerate(base)]
    s4 = _movavg(noisy, 4)
    s16 = _movavg(noisy, 16)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(base)], FAINT, 1.4, dash="5,3")
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(s4)], BLUE, 1.8)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(s16)], RED, 2.2)
    s += text(*(_pt(x0, y0, pw, ph, 0.7, 0.82)), "N=4: спритно, шумно", 10, BLUE, "start", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.62, 0.4)), "N=16: гладко, із затримкою", 10, RED, "start", "bold")
    save("fig-30-2-4-window-size.svg", s)


def fig_step():
    w, h = 660, 280
    s = header(w, h)
    s += text(w / 2, 26, "Відгук на стрибок: вхід-сходинка → вихід-рампа за N кроків",
              13.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 240, 560, 180
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    base = [0.25 if j < 30 else 0.8 for j in range(71)]
    sm = _movavg(base, 14)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(base)], GREY, 1.8, dash="5,3")
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(sm)], GREEN, 2.4)
    s += text(*(_pt(x0, y0, pw, ph, 0.06, 0.34)), "вхід (стрибок)", 10, GREY, "start", "italic")
    s += text(*(_pt(x0, y0, pw, ph, 0.55, 0.55)), "вихід: рампа за N", 10.5, GREEN, "start", "bold")
    s += text(w / 2, 270, "затримка ≈ (N−1)/2 — пів-вікна", 11.5, INK, "middle", "bold")
    save("fig-30-2-5-step.svg", s)


def fig_outlier():
    w, h = 680, 280
    s = header(w, h)
    s += text(w / 2, 26, "Слабке місце: один викид розмазується на N виходів",
              14, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 240, 560, 180
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    base = [0.4 + 0.04 * noise(j) for j in range(71)]
    base[35] = 0.95  # викид
    sm = _movavg(base, 8)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(base)], RED, 1.4)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(sm)], GREEN, 2.4)
    s += text(*(_pt(x0, y0, pw, ph, 0.5, 0.92)), "викид", 10, RED, "middle", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.58, 0.6)), "горб завдовжки N (не зник!)", 10, GREEN, "start", "bold")
    s += text(w / 2, 270, "усереднення не викидає аномалію, а розбавляє — звідси потреба в медіані (§30.3)",
              10.5, GREY, "middle", "italic")
    save("fig-30-2-6-outlier.svg", s)


def _median(xs, N):
    out = []
    for i in range(len(xs)):
        lo = max(0, i - N + 1)
        win = sorted(xs[lo:i + 1])
        m = len(win)
        out.append(win[m // 2] if m % 2 else (win[m // 2 - 1] + win[m // 2]) / 2)
    return out


# ════════════════════════════════════════════════════════════════════════════
#  §30.3 Медіанний фільтр
# ════════════════════════════════════════════════════════════════════════════

def fig_median_idea():
    w, h = 680, 240
    s = header(w, h)
    s += text(w / 2, 26, "Медіана: відсортувати вікно й узяти середній за величиною",
              13.5, INK, "middle", "bold")
    unsorted = [12, 11, 500, 10, 13]
    sorted_v = sorted(unsorted)
    # невідсортований ряд
    s += text(110, 80, "вікно:", 11, INK, "end", "bold")
    for i, v in enumerate(unsorted):
        s += rect(130 + i * 56, 62, 50, 36, fill="#fbfbfb", stroke=BLUE, sw=1.4, rx=4)
        s += text(130 + i * 56 + 25, 86, str(v), 13, BLUE, "middle", "bold")
    s += arrow(220, 112, 220, 138, INK, 1.8)
    s += text(280, 128, "сортуємо за величиною", 10.5, GREY, "middle", "italic")
    # відсортований ряд
    s += text(110, 178, "ряд:", 11, INK, "end", "bold")
    for i, v in enumerate(sorted_v):
        mid = (i == 2)
        s += rect(130 + i * 56, 160, 50, 36, fill="#eef6ef" if mid else "#fbfbfb",
                  stroke=GREEN if mid else GREY, sw=2 if mid else 1.2, rx=4)
        s += text(130 + i * 56 + 25, 184, str(v), 13, GREEN if mid else INK, "middle", "bold")
    s += text(130 + 2 * 56 + 25, 222, "медіана = 12", 11, GREEN, "middle", "bold")
    s += text(130 + 4 * 56 + 25, 222, "викид скраю", 9.5, RED, "middle", "italic")
    save("fig-30-3-1-idea.svg", s)


def fig_median_reject():
    w, h = 680, 240
    s = header(w, h)
    s += text(w / 2, 26, "Викид стає скраю ряду — центр його не помічає",
              14, INK, "middle", "bold")
    vals = [10, 11, 11, 12, 500]
    for i, v in enumerate(vals):
        x = 120 + i * 90
        mid = (i == 2)
        s += rect(x, 90, 78, 44, fill="#eef6ef" if mid else "#fbfbfb",
                  stroke=GREEN if mid else (RED if i == 4 else GREY), sw=2 if mid else 1.3, rx=5)
        s += text(x + 39, 118, str(v), 14, (GREEN if mid else (RED if i == 4 else INK)), "middle", "bold")
    s += line(120, 80, 558, 80, GREY, 1)
    s += text(339, 70, "відсортовано →", 10, GREY, "middle", "italic")
    s += text(120 + 2 * 90 + 39, 158, "медіана = 11 (незрушна)", 11, GREEN, "middle", "bold")
    # середнє тягнеться до викиду
    s += arrow(120 + 2 * 90 + 39, 178, 120 + 4 * 90 + 39, 178, RED, 2)
    s += text(120 + 3 * 90 + 39, 200, "середнє = 108.8 → тягнеться до 500", 11, RED, "middle", "bold")
    save("fig-30-3-2-reject.svg", s)


def fig_mean_vs_median():
    w, h = 680, 290
    s = header(w, h)
    s += text(w / 2, 26, "На спайках: середнє розмазує, медіана відкидає",
              14, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 250, 560, 195
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    base = [0.4 + 0.04 * noise(j) for j in range(71)]
    for k in (20, 45):
        base[k] = 0.92
    me = _movavg(base, 5)
    md = _median(base, 5)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(base)], FAINT, 1.2)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(me)], RED, 2)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(md)], GREEN, 2.2)
    s += text(*(_pt(x0, y0, pw, ph, 0.42, 0.74)), "середнє: горби", 10, RED, "start", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.6, 0.3)), "медіана: рівно", 10, GREEN, "start", "bold")
    save("fig-30-3-3-mean-vs-median.svg", s)


def fig_median_edge():
    w, h = 660, 280
    s = header(w, h)
    s += text(w / 2, 26, "Справжній край: медіана лишає гострим, середнє розмазує",
              13.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 240, 560, 185
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    base = [0.25 if j < 33 else 0.8 for j in range(71)]
    me = _movavg(base, 9)
    md = _median(base, 9)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(base)], FAINT, 1.4, dash="5,3")
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(me)], RED, 2)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(md)], GREEN, 2.4)
    s += text(*(_pt(x0, y0, pw, ph, 0.55, 0.45)), "середнє: рампа", 10, RED, "start", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.55, 0.86)), "медіана: гострий стрибок", 10, GREEN, "start", "bold")
    save("fig-30-3-4-edge.svg", s)


def fig_median_window():
    w, h = 700, 250
    s = header(w, h)
    s += text(w / 2, 26, "Непарне вікно відкидає до (N−1)/2 викидів",
              14, INK, "middle", "bold")
    # N=3 — один викид
    s += text(150, 70, "N = 3: переживає 1 викид", 12, GREEN, "middle", "bold")
    vals3 = [11, 500, 12]
    for i, v in enumerate(sorted(vals3)):
        x = 70 + i * 70
        mid = (i == 1)
        s += rect(x, 88, 60, 38, fill="#eef6ef" if mid else "#fbfbfb",
                  stroke=GREEN if mid else (RED if v == 500 else GREY), sw=1.8 if mid else 1.2, rx=4)
        s += text(x + 30, 113, str(v), 12, (GREEN if mid else (RED if v == 500 else INK)), "middle", "bold")
    s += text(150, 150, "медіана = 12 ✓", 11, GREEN, "middle", "bold")
    # N=5 — два викиди
    s += text(500, 70, "N = 5: переживає 2 поспіль", 12, GREEN, "middle", "bold")
    vals5 = [10, 11, 12, 400, 500]
    for i, v in enumerate(vals5):
        x = 370 + i * 56
        mid = (i == 2)
        s += rect(x, 88, 50, 38, fill="#eef6ef" if mid else "#fbfbfb",
                  stroke=GREEN if mid else (RED if v >= 400 else GREY), sw=1.8 if mid else 1.2, rx=4)
        s += text(x + 25, 113, str(v), 11, (GREEN if mid else (RED if v >= 400 else INK)), "middle", "bold")
    s += text(500, 150, "медіана = 12 ✓ (два викиди скраю)", 11, GREEN, "middle", "bold")
    s += text(w / 2, 220, "тримається, поки зіпсованих менше за половину вікна", 11, GREY, "middle", "italic")
    save("fig-30-3-5-window.svg", s)


def fig_median_combo():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Робастна зв'язка: мала медіана → ковзне середнє",
              14, INK, "middle", "bold")
    base = [0.45 + 0.06 * noise(j) for j in range(50)]
    for k in (12, 30):
        base[k] = 0.95
    afterMed = _median(base, 3)
    afterAvg = _movavg(afterMed, 6)
    stages = [("сирий\n(спайки+шум)", base, RED), ("після медіани\n(спайки геть)", afterMed, GOLD),
              ("після середнього\n(гладко)", afterAvg, GREEN)]
    pw, py, ph = 210, 60, 110
    for i, (title, data, col) in enumerate(stages):
        x = 16 + i * 232
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=col, sw=1.4, rx=8)
        a, b = title.split("\n")
        s += text(x + pw / 2, py + 20, a, 11, col, "middle", "bold")
        s += text(x + pw / 2, py + 34, b, 9.5, INK, "middle", "italic")
        gx, gy, gw, gh = x + 16, py + ph - 12, pw - 32, 50
        s += _plot_path(gx, gy, gw, gh, [(j / 49, v) for j, v in enumerate(data)], col, 1.6)
        if i < 2:
            s += arrow(x + pw + 2, py + ph / 2, x + pw + 20, py + ph / 2, INK, 1.8)
    s += text(w / 2, 220, "кожна ланка робить своє: медіана вбиває викиди, середнє гладить решту",
              11, GREY, "middle", "italic")
    save("fig-30-3-6-combo.svg", s)


def _ema(xs, a):
    out = []
    y = xs[0]
    for x in xs:
        y += a * (x - y)
        out.append(y)
    return out


# ════════════════════════════════════════════════════════════════════════════
#  §30.4 Експоненційне згладжування (EMA)
# ════════════════════════════════════════════════════════════════════════════

def fig_ema_update():
    w, h = 660, 230
    s = header(w, h)
    s += text(w / 2, 28, "Один крок EMA: оцінку підштовхують на частку α до відліку",
              13.5, INK, "middle", "bold")
    y0 = 130
    s += line(80, y0, 600, y0, INK, 2)
    yx, xx = 180, 520
    s += dot(yx, y0, 7, GREEN)
    s += text(yx, y0 - 16, "оцінка y", 12, GREEN, "middle", "bold")
    s += dot(xx, y0, 7, BLUE)
    s += text(xx, y0 - 16, "відлік x", 12, BLUE, "middle", "bold")
    # проміжок
    s += line(yx, y0 + 18, xx, y0 + 18, GREY, 1.2)
    s += text((yx + xx) / 2, y0 + 34, "проміжок (x − y)", 10.5, GREY, "middle", "italic")
    # новий y = крок на α
    ny = yx + 0.3 * (xx - yx)
    s += arrow(yx, y0, ny, y0, RED, 3)
    s += dot(ny, y0, 6, RED)
    s += text(ny, y0 - 36, "нова y", 11, RED, "middle", "bold")
    s += text((yx + ny) / 2, y0 - 50, "крок = α·(x−y)", 10, RED, "middle", "bold")
    s += text(w / 2, 206, "y ← y + α·(x − y)     одне множення, одна змінна — без буфера",
              12, INK, "middle", "bold")
    save("fig-30-4-1-update.svg", s)


def fig_ema_weighting():
    w, h = 660, 260
    s = header(w, h)
    s += text(w / 2, 26, "Чому «експоненційне»: ваги минулого згасають",
              14.5, INK, "middle", "bold")
    x0, y0 = 90, 210
    s += axes(x0, y0, 500, 150)
    s += text(x0 + 250, y0 + 22, "вік відліку (новіший ← → давніший)", 10, INK, "middle")
    s += text(x0 - 8, y0 - 150, "вага", 11, INK, "end", "bold")
    a = 0.35
    for k in range(11):
        wgt = a * (1 - a) ** k
        bh = wgt / a * 130
        s += rect(x0 + 10 + k * 42, y0 - bh, 30, bh, fill="#dceaf5" if k else "#cfe0cf",
                  stroke=GREEN if k == 0 else BLUE, sw=1.2)
    s += text(x0 + 25, y0 - 145, "α (новий)", 9.5, GREEN, "middle", "bold")
    s += text(x0 + 250, y0 - 60, "× (1−α) щокроку — експонента", 10.5, BLUE, "middle", "italic")
    s += text(w / 2, 248, "пам'ять нескінченна, але дедалі слабша (порівняйте з рівним вікном §30.2)",
              10.5, GREY, "middle", "italic")
    save("fig-30-4-2-weighting.svg", s)


def fig_ema_alpha():
    w, h = 680, 290
    s = header(w, h)
    s += text(w / 2, 26, "Одна ручка α: мала — гладко й повільно, велика — спритно й шумно",
              12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 250, 560, 195
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    base = [(0.35 if j < 35 else 0.7) + 0.1 * noise(j * 2.2) for j in range(71)]
    lo = _ema(base, 0.08)
    hi = _ema(base, 0.4)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(base)], FAINT, 1.2)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(hi)], BLUE, 1.8)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(lo)], GREEN, 2.4)
    s += text(*(_pt(x0, y0, pw, ph, 0.6, 0.86)), "α=0.4: спритно, шумно", 10, BLUE, "start", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.58, 0.4)), "α=0.08: гладко, повільно", 10, GREEN, "start", "bold")
    save("fig-30-4-3-alpha.svg", s)


def fig_ema_step():
    w, h = 660, 280
    s = header(w, h)
    s += text(w / 2, 26, "Відгук EMA на стрибок — експонента (≈63% за сталу часу)",
              13.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 240, 560, 185
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    base = [0.2 if j < 25 else 0.85 for j in range(71)]
    em = _ema(base, 0.12)
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(base)], FAINT, 1.6, dash="5,3")
    s += _plot_path(x0, y0, pw, ph, [(j / 70, v) for j, v in enumerate(em)], GREEN, 2.4)
    s += text(*(_pt(x0, y0, pw, ph, 0.06, 0.28)), "вхід (стрибок)", 10, GREY, "start", "italic")
    # 63% мітка
    target = 0.85
    p63 = 0.2 + 0.63 * (target - 0.2)
    tau_j = 25 + int(1 / 0.12)
    pp = _pt(x0, y0, pw, ph, tau_j / 70, p63)
    s += line(_pt(x0, y0, pw, ph, 0, p63)[0], pp[1], pp[0], pp[1], BLUE, 1, dash="3,3")
    s += dot(pp[0], pp[1], 4, BLUE)
    s += text(pp[0] + 6, pp[1] - 6, "63% за 1τ", 10, BLUE, "start", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.6, 0.7)), "плавна експонента", 10, GREEN, "start", "bold")
    save("fig-30-4-4-step.svg", s)


def fig_rc_twin():
    w, h = 700, 260
    s = header(w, h)
    s += text(w / 2, 26, "EMA — це цифровий RC-фільтр: та сама експонента",
              14.5, INK, "middle", "bold")
    # ліво — RC
    s += rect(24, 50, 320, 190, fill="#fbf6ee", stroke=GOLD, sw=1.4, rx=8)
    s += text(184, 72, "аналогова RC-ланка", 12, "#9a7a1e", "middle", "bold")
    s += line(50, 110, 90, 110, INK, 2)
    s += poly([(90, 110), (98, 102), (108, 118), (118, 102), (128, 118), (138, 102), (146, 110)], INK, 2)
    s += line(146, 110, 200, 110, INK, 2)
    s += line(200, 110, 200, 130, INK, 2)
    s += line(186, 130, 214, 130, INK, 3)
    s += line(186, 138, 214, 138, INK, 3)
    s += line(200, 138, 200, 158, INK, 2)
    s += line(50, 158, 230, 158, INK, 1.6)
    s += line(50, 110, 50, 158, INK, 1.6)
    # крива заряду
    s += axes(60, 228, 250, 50, GREY)
    pts = [(j / 30, 1 - math.exp(-3 * j / 30)) for j in range(31)]
    s += _plot_path(60, 228, 250, 44, pts, "#9a7a1e", 2)
    # право — EMA
    s += rect(360, 50, 316, 190, fill="#eef6ef", stroke=GREEN, sw=1.4, rx=8)
    s += text(518, 72, "EMA в коді", 12, GREEN, "middle", "bold")
    s += rect(430, 96, 176, 34, fill="#fff", stroke=GREEN, sw=1.5, rx=5)
    s += text(518, 118, "y += α·(x − y)", 12, GREEN, "middle", "bold")
    s += axes(396, 228, 250, 50, GREY)
    s += _plot_path(396, 228, 250, 44, pts, GREEN, 2)
    s += text(w / 2, 250, "однакова експонента → один і той самий фільтр НЧ першого порядку",
              10.5, GREY, "middle", "italic")
    save("fig-30-4-5-rc-twin.svg", s)


def fig_ema_cost():
    w, h = 700, 250
    s = header(w, h)
    s += text(w / 2, 26, "Ціна на МК: EMA проти буфера середнього й сортування медіани",
              13, INK, "middle", "bold")
    items = [("ковзне середнє", BLUE, "буфер N відліків", "кілька дій"),
             ("медіана", RED, "буфер N відліків", "сортування"),
             ("EMA", GREEN, "1 змінна", "1 множення")]
    pw, py, ph = 210, 56, 150
    for i, (name, col, mem, comp) in enumerate(items):
        x = 16 + i * 232
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=col, sw=1.5, rx=8)
        s += text(x + pw / 2, py + 28, name, 13, col, "middle", "bold")
        s += text(x + pw / 2, py + 64, "пам'ять:", 10, GREY, "middle", "bold")
        s += text(x + pw / 2, py + 82, mem, 11.5, INK, "middle", "bold")
        s += text(x + pw / 2, py + 110, "обчислення:", 10, GREY, "middle", "bold")
        s += text(x + pw / 2, py + 128, comp, 11.5, INK, "middle", "bold")
    s += text(w / 2, 234, "EMA — на порядки дешевша; тому стандарт там, де ресурсів обмаль",
              11, GREY, "middle", "italic")
    save("fig-30-4-6-cost.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §30.5 Компроміс згладжування ↔ затримка
# ════════════════════════════════════════════════════════════════════════════

def fig_tradeoff_curve():
    w, h = 660, 290
    s = header(w, h)
    s += text(w / 2, 26, "Головна шкала: за гладкість платять затримкою",
              14.5, INK, "middle", "bold")
    x0, y0, pw, ph = 90, 250, 480, 195
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw / 2, y0 + 24, "згладжування (чистота) →", 11, INK, "middle", "bold")
    s += text(x0 - 8, y0 - ph - 4, "затримка", 11, INK, "end", "bold")
    pts = [(t / 30, (t / 30) ** 1.6 * 0.95) for t in range(31)]
    s += _plot_path(x0, y0, pw, ph, pts, GREEN, 2.8)
    marks = [(0.18, "легкий", BLUE), (0.5, "середній", GOLD), (0.85, "важкий", RED)]
    for (xv, lbl, col) in marks:
        p = _pt(x0, y0, pw, ph, xv, xv ** 1.6 * 0.95)
        s += dot(p[0], p[1], 5, col)
        s += text(p[0] + 6, p[1] + 4, lbl, 10, col, "start", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.7, 0.18)), "«чисто й швидко» — порожньо", 10, GREY, "start", "italic")
    save("fig-30-5-1-tradeoff-curve.svg", s)


def fig_need_time():
    w, h = 680, 270
    s = header(w, h)
    s += text(w / 2, 26, "Щоб відрізнити зміну від шуму, фільтр мусить зачекати",
              14, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 230, 560, 170
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    # справжня зміна
    base = [0.35 if j < 30 else 0.7 for j in range(61)]
    s += _plot_path(x0, y0, pw, ph, [(j / 60, v) for j, v in enumerate(base)], GREEN, 2)
    for j in range(0, 61, 2):
        s += dot(*_pt(x0, y0, pw, ph, j / 60, base[j] + 0.06 * noise(j * 2)), 2.6, BLUE)
    # після 1 відліку — знак питання
    p1 = _pt(x0, y0, pw, ph, 32 / 60, 0.7)
    s += line(p1[0], y0, p1[0], y0 - ph, GREY, 1, dash="3,3")
    s += text(p1[0], y0 - ph - 4, "+1 відлік: спайк чи зміна?", 9.5, RED, "middle", "bold")
    # після кількох — ясно
    p2 = _pt(x0, y0, pw, ph, 50 / 60, 0.7)
    s += line(p2[0], y0, p2[0], y0 - ph, GREY, 1, dash="3,3")
    s += text(p2[0], y0 - ph - 4, "+кілька: ясно, що зміна", 9.5, GREEN, "middle", "bold")
    s += text(w / 2, 262, "чекання на впевненість = затримка — звідси й закон", 11, GREY, "middle", "italic")
    save("fig-30-5-2-need-time.svg", s)


def fig_operating_window():
    w, h = 680, 250
    s = header(w, h)
    s += text(w / 2, 26, "Робоча точка — між смугою сигналу й смугою шуму",
              14, INK, "middle", "bold")
    x0, xe, y = 80, 620, 150
    s += line(x0, y, xe, y, INK, 2)
    s += arrow(xe - 30, y, xe + 4, y, INK, 2)
    s += text(xe, y + 24, "частота →", 11, INK, "middle", "bold")
    # смуга сигналу (низькі частоти)
    s += rect(x0, y - 40, 180, 40, fill="#d8efd8", stroke=GREEN, sw=1.2)
    s += text(x0 + 90, y - 48, "сигнал (повільне)", 10.5, GREEN, "middle", "bold")
    # смуга шуму (високі)
    s += rect(380, y - 40, 240, 40, fill="#cfd9f3", stroke=BLUE, sw=1.2)
    s += text(500, y - 48, "шум (швидке)", 10.5, BLUE, "middle", "bold")
    # зріз фільтра між ними
    cut = 300
    s += line(cut, y - 60, cut, y + 16, RED, 2.4, dash="5,3")
    s += text(cut, y + 40, "зріз фільтра", 11, RED, "middle", "bold")
    s += arrow(cut - 8, y + 8, x0 + 30, y + 8, GREEN, 1.6)
    s += text(190, y + 12, "пропустити", 9.5, GREEN, "middle")
    s += arrow(cut + 8, y + 8, xe - 30, y + 8, BLUE, 1.6)
    s += text(470, y + 12, "відрізати", 9.5, BLUE, "middle")
    s += text(w / 2, 226, "якщо смуги перекриваються — простий фільтр безсилий, треба хитріше",
              10.5, GREY, "middle", "italic")
    save("fig-30-5-3-operating-window.svg", s)


def fig_overfilter():
    w, h = 680, 290
    s = header(w, h)
    s += text(w / 2, 26, "Перефільтрування: велика затримка розгойдує керування",
              13.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 250, 560, 195
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    s += _plot_path(x0, y0, pw, ph, [(0, 0.5), (1, 0.5)], FAINT, 1.4, dash="6,4")
    s += text(*(_pt(x0, y0, pw, ph, 0.02, 0.54)), "ціль", 10, GREY, "start", "italic")
    # легка затримка — згасає до цілі
    light = [(j / 80, 0.5 + 0.32 * math.exp(-2.5 * j / 80) * math.cos(2 * math.pi * 1.2 * j / 80)) for j in range(81)]
    s += _plot_path(x0, y0, pw, ph, light, GREEN, 2)
    s += text(*(_pt(x0, y0, pw, ph, 0.55, 0.6)), "мала затримка → сходиться", 10, GREEN, "start", "bold")
    # велика затримка — наростає
    heavy = [(j / 80, 0.5 + 0.18 * math.exp(0.8 * j / 80) * math.cos(2 * math.pi * 1.0 * j / 80)) for j in range(81)]
    heavy = [(xv, min(0.98, max(0.02, uv))) for (xv, uv) in heavy]
    s += _plot_path(x0, y0, pw, ph, heavy, RED, 2.2)
    s += text(*(_pt(x0, y0, pw, ph, 0.5, 0.92)), "велика затримка → розгойдування", 10, RED, "start", "bold")
    save("fig-30-5-4-overfilter.svg", s)


def fig_compare_filters():
    w, h = 700, 290
    s = header(w, h)
    s += text(w / 2, 26, "Та сама зміна крізь легкий, середній, важкий фільтри",
              14, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 250, 560, 195
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    base = [(0.3 if j < 30 else 0.75) + 0.08 * noise(j * 2.1) for j in range(81)]
    s += _plot_path(x0, y0, pw, ph, [(j / 80, (0.3 if j < 30 else 0.75)) for j in range(81)], FAINT, 1.4, dash="5,3")
    for (N, col, lbl) in [(4, BLUE, "легкий N=4"), (16, GOLD, "середній N=16"), (40, RED, "важкий N=40")]:
        sm = _movavg(base, N)
        s += _plot_path(x0, y0, pw, ph, [(j / 80, v) for j, v in enumerate(sm)], col, 2)
    s += text(*(_pt(x0, y0, pw, ph, 0.55, 0.86)), "N=4", 10, BLUE, "start", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.62, 0.62)), "N=16", 10, "#9a7a1e", "start", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.72, 0.42)), "N=40", 10, RED, "start", "bold")
    s += text(w / 2, 280, "чистіше = пізніше: важкий доходить останнім", 11, GREY, "middle", "italic")
    save("fig-30-5-5-comparison.svg", s)


def fig_escape():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Як обійти компроміс: додати інформацію",
              15, INK, "middle", "bold")
    cards = [("нелінійність", GREEN, "медіана б'є викид", "без плати затримкою"),
             ("адаптивність", BLUE, "α більша на події", "рух по кривій"),
             ("передбачення", PURP, "модель руху (Калман)", "прогноз гасить лаг"),
             ("частіша вибірка", GOLD, "більше відліків/с", "та сама тиша, менше мс")]
    pw, py, ph = 166, 54, 178
    for i, (name, col, line1, line2) in enumerate(cards):
        x = 14 + i * 176
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=col, sw=1.5, rx=8)
        s += text(x + pw / 2, py + 26, name, 12, col, "middle", "bold")
        s += text(x + pw / 2, py + 96, line1, 10.5, INK, "middle", "bold")
        s += text(x + pw / 2, py + 140, line2, 9.5, GREY, "middle", "italic")
    s += text(w / 2, 250, "кожна вносить щось понад сирий потік — без нової інформації компромісу не обійти",
              10, GREY, "middle", "italic")
    save("fig-30-5-6-escape.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §30.6 Який фільтр коли
# ════════════════════════════════════════════════════════════════════════════

def fig_decision_tree():
    w, h = 760, 400
    s = header(w, h)
    s += text(w / 2, 26, "Дерево рішення: спершу діагноз, тоді фільтр", 15, INK, "middle", "bold")
    # корінь
    s += rect(24, 168, 150, 64, fill="#fbfbfb", stroke=INK, sw=2, rx=8)
    s += text(99, 195, "сирий потік:", 12, INK, "middle", "bold")
    s += text(99, 214, "який характер?", 12, INK, "middle", "bold")
    # три гілки діагнозу
    nodes = [
        (44,  "ДРЕЙФ → калібрування", "не фільтр! (§28.6)", GOLD, "повзе?"),
        (170, "ВИКИДИ → медіана",     "вибиває голки (§30.3)", PURP, "голки?"),
        (294, "ШУМ → усереднення",    "EMA / ковзне (§30.2,4)", BLUE, "тремтить?"),
    ]
    for (ny, title, sub, col, q) in nodes:
        s += arrow(174, 200, 250, ny + 24, col, 1.8)
        s += text(252, ny - 6, q, 10, GREY, "start", "italic")
        s += rect(250, ny, 220, 48, fill="#fbfbfb", stroke=col, sw=1.8, rx=8)
        s += text(360, ny + 21, title, 12, col, "middle", "bold")
        s += text(360, ny + 38, sub, 9.5, GREY, "middle", "italic")
    # «усереднення» → два листки
    leaves = [
        (262, "EMA", "ресурси тиснуть · багато каналів", BLUE),
        (330, "ковзне середнє", "лінійна фаза · нуль 50 Гц", GREEN),
    ]
    for (ly, title, sub, col) in leaves:
        s += arrow(470, 318, 540, ly + 22, col, 1.8)
        s += rect(540, ly, 210, 44, fill="#ffffff", stroke=col, sw=1.6, rx=8)
        s += text(645, ly + 20, title, 12, col, "middle", "bold")
        s += text(645, ly + 36, sub, 9, GREY, "middle", "italic")
    s += text(w / 2, 390, "діагноз економить більше часу, ніж будь-який вибір алгоритму", 10.5, GREY, "middle", "italic")
    save("fig-30-6-1-decision-tree.svg", s)


def fig_compare_table():
    w, h = 720, 430
    s = header(w, h)
    s += text(w / 2, 26, "Три фільтри за критеріями вибору", 15, INK, "middle", "bold")
    colx = [365, 495, 625]
    heads = [("Ковзне", "середнє", GREEN), ("Медіана", "", PURP), ("EMA", "", BLUE)]
    for cx, (h1, h2, col) in zip(colx, heads):
        s += rect(cx - 58, 44, 116, 38, fill="#fbfbfb", stroke=col, sw=1.6, rx=6)
        s += text(cx, 62, h1, 12, col, "middle", "bold")
        if h2:
            s += text(cx, 77, h2, 12, col, "middle", "bold")
    rows = [
        ("Гладить дрібний шум",     [("✓✓", GREEN), ("~", GOLD), ("✓✓", GREEN)]),
        ("Вбиває викиди",          [("✗", RED), ("✓✓", GREEN), ("✗", RED)]),
        ("Береже різкий край",     [("✗", RED), ("✓", GREEN), ("~", GOLD)]),
        ("Лінійна фаза",           [("✓", GREEN), ("✗", RED), ("✗", RED)]),
        ("Прицільні нулі частот",  [("✓", GREEN), ("✗", RED), ("✗", RED)]),
        ("Мала пам'ять",           [("✗ N", RED), ("✗ N", RED), ("✓✓ 1", GREEN)]),
        ("Дешеві обчислення",      [("✓", GREEN), ("✗ сорт", RED), ("✓✓", GREEN)]),
        ("Передбачувана затримка", [("✓", GREEN), ("~", GOLD), ("✓", GREEN)]),
    ]
    y = 106
    for i, (lbl, cells) in enumerate(rows):
        if i % 2 == 0:
            s += rect(16, y - 20, 688, 34, fill="#f6f6f6", stroke="none", sw=0, rx=4)
        s += text(28, y, lbl, 12, INK, "start")
        for cx, (sym, col) in zip(colx, cells):
            s += text(cx, y, sym, 14, col, "middle", "bold")
        y += 38
    s += text(w / 2, y + 8, "немає універсального переможця — кожен сильний у своєму", 10.5, GREY, "middle", "italic")
    save("fig-30-6-2-compare-table.svg", s)


def fig_recipes():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Готові рецепти під типову ситуацію", 15, INK, "middle", "bold")
    cards = [
        ("Повільне довкілля", GREEN, "EMA, мала α", "темп., вологість, світло"),
        ("Далекомір з привидами", PURP, "медіана(3) → EMA", "ультразвук, лазер"),
        ("Вхід у керування", BLUE, "легкий фільтр", "свіжість понад чистоту"),
        ("Поріг / край", GOLD, "медіана / гістерезис", "не згладжувати край!"),
    ]
    cw, gap, x0, py, ph = 168, 8, 14, 52, 170
    for i, (name, col, chain, note) in enumerate(cards):
        x = x0 + i * (cw + gap)
        s += rect(x, py, cw, ph, fill="#fbfbfb", stroke=col, sw=1.6, rx=8)
        s += text(x + cw / 2, py + 28, name, 12, col, "middle", "bold")
        s += line(x + 16, py + 44, x + cw - 16, py + 44, FAINT, 1.2)
        s += text(x + cw / 2, py + 98, chain, 12.5, INK, "middle", "bold")
        s += text(x + cw / 2, py + 142, note, 10, GREY, "middle", "italic")
    s += text(w / 2, 244, "діагноз → рецепт: більшість задач лягають у ці чотири шаблони", 10.5, GREY, "middle", "italic")
    save("fig-30-6-3-recipes.svg", s)


def fig_robust_default():
    w, h = 780, 300
    s = header(w, h)
    s += text(w / 2, 26, "Зв'язка за замовчуванням: медіана(3) → EMA", 15, INK, "middle", "bold")
    base = [(0.32 if j < 24 else 0.68) + 0.06 * noise(j * 2.3) for j in range(48)]
    base[10] = base[10] + 0.50
    base[33] = base[33] - 0.42
    med = _median(base, 3)
    out = _ema(med, 0.3)
    panels = [(40, base, "сирий потік", "+спайки +шум", RED),
              (300, med, "медіана(3)", "спайки геть", PURP),
              (560, out, "EMA", "гладко", GREEN)]
    pw, ph, y0 = 180, 140, 224
    for (x0, data, title, sub, col) in panels:
        s += rect(x0 - 12, 44, pw + 24, 204, fill="#fcfcfc", stroke=FAINT, sw=1.4, rx=8)
        s += text(x0 + pw / 2, 66, title, 12.5, col, "middle", "bold")
        s += line(x0, y0, x0 + pw, y0, FAINT, 1.4)
        s += _plot_path(x0, y0, pw, ph, [(j / 47.0, v) for j, v in enumerate(data)], col, 2)
        s += text(x0 + pw / 2, 242, sub, 10, GREY, "middle", "italic")
    s += arrow(236, 150, 286, 150, INK, 2)
    s += arrow(496, 150, 546, 150, INK, 2)
    s += text(w / 2, 288, "дешева, надійна, покриває найчастіші біди — звідси й починають", 10.5, GREY, "middle", "italic")
    save("fig-30-6-4-robust-default.svg", s)


def fig_antipatterns():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Чотири типові помилки фільтрації", 15, INK, "middle", "bold")
    cards = [
        ("Усереднити викид", "спайк розмажеться", "→ медіана"),
        ("Фільтрувати дрейф", "це не шум — систематика", "→ калібрування"),
        ("Перефільтрувати", "затримка розгойдує", "→ легший фільтр"),
        ("Вірити гладкому", "гладко ≠ правильно", "→ свіжо й правдиво"),
    ]
    cw, gap, x0, py, ph = 168, 8, 14, 52, 170
    for i, (name, why, fix) in enumerate(cards):
        x = x0 + i * (cw + gap)
        s += rect(x, py, cw, ph, fill="#fdf6f5", stroke=RED, sw=1.6, rx=8)
        s += text(x + cw / 2, py + 26, "✗", 18, RED, "middle", "bold")
        s += text(x + cw / 2, py + 52, name, 11.5, INK, "middle", "bold")
        s += text(x + cw / 2, py + 98, why, 10, GREY, "middle", "italic")
        s += line(x + 16, py + 118, x + cw - 16, py + 118, FAINT, 1.2)
        s += text(x + cw / 2, py + 146, fix, 11.5, GREEN, "middle", "bold")
    s += text(w / 2, 244, "кожна має свій почерк у виході — знаючи його, причину видно за секунди", 10.5, GREY, "middle", "italic")
    save("fig-30-6-5-antipatterns.svg", s)


def fig_pipeline():
    w, h = 780, 250
    s = header(w, h)
    s += text(w / 2, 26, "Місце фільтра в тракті: одна ланка, не кінець", 15, INK, "middle", "bold")
    by, bh, bw = 86, 76, 170
    boxes = [(30, "сирі відліки", "давач (§28.1)", GREY),
             (235, "ФІЛЬТР", "геть випадкове", BLUE),
             (440, "калібрування", "геть систематичне", GOLD)]
    for (x, t1, t2, col) in boxes:
        s += rect(x, by, bw, bh, fill="#fbfbfb", stroke=col, sw=1.8, rx=8)
        s += text(x + bw / 2, by + 34, t1, 13, col, "middle", "bold")
        s += text(x + bw / 2, by + 56, t2, 10, GREY, "middle", "italic")
    s += arrow(202, by + bh / 2, 233, by + bh / 2, INK, 2)
    s += arrow(407, by + bh / 2, 438, by + bh / 2, INK, 2)
    # віяло виходів
    cxr, cyr = 610, by + bh / 2
    outs = [("рішення", 60), ("керування", 124), ("фьюжн (§33–34)", 188)]
    for (lbl, oy) in outs:
        s += arrow(cxr, cyr, 648, oy, GREEN, 1.6)
        s += rect(650, oy - 16, 120, 32, fill="#ffffff", stroke=GREEN, sw=1.5, rx=6)
        s += text(710, oy + 5, lbl, 10.5, GREEN, "middle", "bold")
    s += text(w / 2, 234, "фільтр прибирає випадкове; систематику знімає калібрування; далі — рішення й фьюжн",
              10, GREY, "middle", "italic")
    save("fig-30-6-6-pipeline.svg", s)


if __name__ == "__main__":
    fig_noisy_stream()
    fig_three_lies()
    fig_signal_noise()
    fig_tradeoff()
    fig_digital_analog()
    fig_chapter_map()
    # §30.2 Ковзне середнє
    fig_window()
    fig_result()
    fig_running_sum()
    fig_window_size()
    fig_step()
    fig_outlier()
    # §30.3 Медіанний фільтр
    fig_median_idea()
    fig_median_reject()
    fig_mean_vs_median()
    fig_median_edge()
    fig_median_window()
    fig_median_combo()
    # §30.4 Експоненційне згладжування
    fig_ema_update()
    fig_ema_weighting()
    fig_ema_alpha()
    fig_ema_step()
    fig_rc_twin()
    fig_ema_cost()
    # §30.5 Компроміс згладжування ↔ затримка
    fig_tradeoff_curve()
    fig_need_time()
    fig_operating_window()
    fig_overfilter()
    fig_compare_filters()
    fig_escape()
    # §30.6 Який фільтр коли
    fig_decision_tree()
    fig_compare_table()
    fig_recipes()
    fig_robust_default()
    fig_antipatterns()
    fig_pipeline()
    print("OK — фігури §30.1–§30.6 згенеровано в", OUT)
