# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для математичної вставки до теми 1.9.2 —
«нВ/√Гц: спектральна густина шуму — мова даташитів» (Модуль 1, Розділ 1.9).
Чистий Python, без залежностей. Вивід → ./img/ (УНІКАЛЬНІ імена; головний figs.py розділу не чіпаємо).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація: вставка 🧮 до теми 1.9.2 → Рис. 1.9.2m.N.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
COPPER = "#cf8b5e"
ORANGE = "#e08030"
PURPLE = "#7a3fae"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", ORANGE: "aOrange", PURPLE: "aPurple"}


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
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ════════════════════════════════════════════════════════════════════════════
#  Вставка 🧮 до теми 1.9.2 — спектральна густина шуму (нВ/√Гц).  Рис. 1.9.2m.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.9.2m.1 — густина × √смуга = повний RMS-шум ─────────────────────────
def fig_density_to_rms():
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 30, "Густина — це шум «на корінь з герца». Смуга вирішує решту",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "та сама густина 10 нВ/√Гц дає різний повний шум — бо повний шум росте з коренем смуги",
              11.5, GREY, "middle", style="italic")

    # ── ліва панель: «склянки» — як накопичується потужність по смузі ──
    bx, by = 60, 95
    bw, bh = 300, 300
    s += rect(bx, by, bw, bh, "#f7f7f7", GREY, 1.5, 12)
    s += text(bx + bw / 2, by + 26, "Шум рівномірно «розлитий» по частоті",
              12.5, INK, "middle", "bold")
    s += text(bx + bw / 2, by + 44, "(білий шум: e² на кожен Гц однакова)",
              10, GREY, "middle", style="italic")

    # ряд однакових «цеглинок потужності» вздовж осі частоти
    base_y = by + bh - 60
    fx = bx + 36
    fw = bw - 70
    s += line(fx, base_y, fx + fw, base_y, INK, 2)
    s += polygon([(fx + fw, base_y), (fx + fw - 12, base_y - 5),
                  (fx + fw - 12, base_y + 5)], INK)
    s += text(fx + fw + 4, base_y + 14, "f", 12, INK, "start", "bold")
    n = 10
    cellw = fw / (n + 1.5)
    ch = 26
    for i in range(n):
        cx = fx + i * cellw + 3
        s += rect(cx, base_y - ch, cellw - 4, ch, "#d8e6ff", BLUE, 1.2, 2)
    s += text(fx, base_y - ch - 12, "кожна цеглинка = e²·Δf однакової «потужності шуму»",
              9.6, BLUE, "start")
    s += text(bx + bw / 2, base_y + 40,
              "ширша смуга = більше цеглинок = більше потужності",
              10.4, INK, "middle")
    s += text(bx + bw / 2, base_y + 56,
              "складаємо ПОТУЖНОСТІ (квадрати), не напруги",
              10.4, RED, "middle", "bold")

    # ── права панель: формула й два числові приклади ──
    px = bx + bw + 50
    pw = W - px - 50
    s += rect(px, by, pw, bh, "#ffffff", INK, 1.6, 12)
    s += text(px + pw / 2, by + 30, "Від густини до вольтів", 14, INK, "middle", "bold")

    # центральна формула
    s += rect(px + 24, by + 48, pw - 48, 52, "#eef6ee", GREEN, 1.6, 8)
    s += text(px + pw / 2, by + 72, "Vₙ(RMS) = eₙ × √BW",
              19, GREEN, "middle", "bold")
    s += text(px + pw / 2, by + 92,
              "[нВ] = [нВ/√Гц] × [√Гц]   — одиниці сходяться",
              10.4, GREY, "middle", style="italic")

    # два приклади
    ey = by + 124
    s += text(px + 24, ey, "Та сама густина eₙ = 10 нВ/√Гц:", 11.5, INK, "start", "bold")
    rows = [
        ("звукова смуга", "BW = 20 кГц", "√20000 ≈ 141", "≈ 1410 нВ = 1.41 мкВ", BLUE),
        ("вузький фільтр", "BW = 100 Гц", "√100 = 10", "≈ 100 нВ = 0.10 мкВ", GREEN),
    ]
    yy = ey + 22
    for name, bwv, root, res, col in rows:
        s += circle(px + 32, yy - 4, 4.5, col, col, 1)
        s += text(px + 44, yy, name, 11, INK, "start", "bold")
        s += text(px + 44, yy + 16, f"{bwv}:  eₙ·{root}", 10.5, GREY, "start")
        s += text(px + 44, yy + 32, res, 12, col, "start", "bold")
        yy += 56
    s += line(px + 24, yy - 6, px + pw - 24, yy - 6, FAINT, 1.4)
    s += text(px + pw / 2, yy + 14,
              "смугу звузили в 200× → шум упав лише в √200 ≈ 14×",
              10.6, RED, "middle", "bold")

    save("fig-r09-s2m-1-density-to-rms.svg", s)


# ── Рис. 1.9.2m.2 — спектр густини: поличка білого шуму й кутова частота 1/f ──
def fig_density_spectrum():
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 30, "Як густина шуму виглядає в даташиті: поличка й «хвіст» 1/f",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "графік eₙ(f) у лог-лог осях: рівне біле плато й підйом на низьких частотах",
              11.5, GREY, "middle", style="italic")

    # осі (лог-лог, схематично)
    ox, oy = 95, 380          # початок осей
    aw, ah = 770, 290
    s += line(ox, oy, ox + aw, oy, INK, 2)            # X
    s += polygon([(ox + aw, oy), (ox + aw - 12, oy - 5), (ox + aw - 12, oy + 5)], INK)
    s += line(ox, oy, ox, oy - ah, INK, 2)            # Y
    s += polygon([(ox, oy - ah), (ox - 5, oy - ah + 12), (ox + 5, oy - ah + 12)], INK)

    s += text(ox + aw / 2, oy + 44, "частота f  (лог), Гц", 12.5, INK, "middle", "bold")
    # підписи декад X
    decades = ["0.1", "1", "10", "100", "1k", "10k", "100k"]
    for i, lab in enumerate(decades):
        gx = ox + aw * (i + 0.5) / len(decades)
        s += line(gx, oy, gx, oy + 5, INK, 1.4)
        s += text(gx, oy + 20, lab, 10.5, GREY, "middle")
        s += line(gx, oy, gx, oy - ah, FAINT, 1)

    # Y підпис (вертикально)
    s += (f'<text x="26" y="{oy - ah/2:.1f}" font-family="{FONT}" font-size="12.5" '
          f'fill="{INK}" text-anchor="middle" font-weight="bold" '
          f'transform="rotate(-90 26 {oy - ah/2:.1f})">eₙ, нВ/√Гц  (лог)</text>\n')
    yvals = ["3", "10", "30", "100"]
    for i, lab in enumerate(yvals):
        gy = oy - ah * (i + 0.6) / len(yvals)
        s += line(ox - 5, gy, ox, gy, INK, 1.4)
        s += text(ox - 10, gy + 4, lab, 10.5, GREY, "end")
        s += line(ox, gy, ox + aw, gy, FAINT, 1)

    # рівень білого плато
    floor_y = oy - ah * 0.32
    # крива e_n(f): 1/f-хвіст ліворуч, плато праворуч; кутова частота fc
    fc_frac = 0.30                      # частка осі, де кутова частота
    fc_x = ox + aw * fc_frac
    pts = []
    N = 160
    for i in range(N + 1):
        frac = i / N
        gx = ox + aw * frac
        # «частота» по декадах від 0.1 до 100k -> показник
        # моделюємо e_n^2 = white^2 * (1 + fc_frac_decade/frac_decade)
        # простіше: над плато додаємо 1/f-складову, що спадає праворуч
        d = max(frac, 0.001)
        excess = (fc_frac / d) ** 1.0          # ~1/f у напрузі (1/f^2 у потужності)
        ratio = math.sqrt(1.0 + excess * excess * 0.0 + excess)  # плавно
        # обмежимо підйом, щоб не вилазив за поле
        gy = floor_y - (ah * 0.085) * math.log10(max(ratio, 1.0)) * 3.0
        gy = max(gy, oy - ah + 14)
        pts.append((gx, gy))
    s += polyline(pts, RED, 3.0)

    # плато-асимптота
    s += line(fc_x, floor_y, ox + aw - 6, floor_y, BLUE, 1.8, "7,5")
    s += text(ox + aw - 10, floor_y - 10,
              "біле плато: eₙ = const (тепловий + дробовий)", 11, BLUE, "end", "bold")
    s += text(ox + aw - 10, floor_y + 18,
              "тут шум ∝√BW", 10.4, BLUE, "end")

    # кутова частота
    s += line(fc_x, oy, fc_x, oy - ah + 10, PURPLE, 1.6, "4,4")
    s += circle(fc_x, floor_y, 5, "#ffffff", PURPLE, 2)
    s += text(fc_x + 8, oy - ah + 26, "кутова частота 1/f", 11, PURPLE, "start", "bold")
    s += text(fc_x + 8, oy - ah + 42, "(f_corner / f_c)", 9.6, PURPLE, "start", style="italic")

    # хвіст 1/f
    s += text(ox + 14, oy - ah + 60, "хвіст 1/f:", 11.5, RED, "start", "bold")
    s += text(ox + 14, oy - ah + 76, "повільні дрейфи,", 10, INK, "start")
    s += text(ox + 14, oy - ah + 90, "густина росте на НЧ", 10, INK, "start")
    s += text(ox + 14, oy - ah + 104, "(→ §1.9.3)", 9.6, GREY, "start", style="italic")

    save("fig-r09-s2m-2-density-spectrum.svg", s)


if __name__ == "__main__":
    fig_density_to_rms()
    fig_density_spectrum()
    print("OK")
