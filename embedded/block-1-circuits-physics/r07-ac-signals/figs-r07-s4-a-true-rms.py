# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для ⚙️-вставки до теми 1.7.4 — «True RMS у приладі».
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами (fig-r07-4a-*).
НЕ чіпає головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Нумерація підписів у тексті — Рис. 1.7.4a.k.
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
ORANGE = "#e08030"
PURPLE = "#7a3fb0"
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
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", ORANGE: "aOrange", PURPLE: "aPurple"}


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


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def polygon(points, fill=INK, stroke="none", sw=0, opacity=1.0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" fill-opacity="{opacity}"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.7.4a.1 — конвеєр True RMS: квадрат → середнє → корінь
# ════════════════════════════════════════════════════════════════════════════
def fig_pipeline():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 30, "True RMS у приладі: квадрат  →  середнє  →  корінь",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "три кроки над миттєвими відліками сигналу — рівно за означенням RMS, без жодного припущення про форму",
              11, GREY, "middle", style="italic")

    # ── ряд 1: сирий сигнал v(t) (несиметрична хвиля з постійною складовою?) ──
    ax, aw = 70, 360
    y1 = 130
    s += line(ax, y1, ax + aw, y1, GREY, 1.3)               # вісь нуля
    s += text(ax - 8, y1 + 4, "0", 10, GREY, "end")
    # синус як приклад вхідного сигналу
    pin = []
    for i in range(121):
        t = i / 120
        v = math.sin(2 * math.pi * 2 * t)
        pin.append((ax + t * aw, y1 - 42 * v))
    s += polyline(pin, RED, 2.6)
    s += text(ax, y1 - 56, "1.  миттєвий відлік  v[n]", 12, RED, "start", "bold")
    s += text(ax + aw + 10, y1 + 4, "t", 11, GREY, "start", "bold", "italic")

    # стрілка вниз: піднести до квадрата
    s += arrow(ax + aw / 2, y1 + 50, ax + aw / 2, y1 + 86, INK, 2.4)
    s += text(ax + aw / 2 + 10, y1 + 72, "піднести до квадрата  v²", 11, INK, "start", "bold")

    # ── ряд 2: квадрат v² — завжди ≥ 0, подвоєна частота ──
    y2 = 280
    s += line(ax, y2, ax + aw, y2, GREY, 1.3)
    s += text(ax - 8, y2 + 4, "0", 10, GREY, "end")
    psq = []
    for i in range(121):
        t = i / 120
        v = math.sin(2 * math.pi * 2 * t)
        psq.append((ax + t * aw, y2 - 70 * v * v))
    # заливка під квадратом (площа = сума, яку усереднюємо)
    fillpts = [(ax, y2)] + psq + [(ax + aw, y2)]
    s += polygon(fillpts, BLUE, "none", 0, 0.14)
    s += polyline(psq, BLUE, 2.6)
    s += text(ax, y2 - 84, "2.  квадрат  v²  (завжди ≥ 0)", 12, BLUE, "start", "bold")
    # рівень середнього <v²>
    mean_lvl = y2 - 35
    s += line(ax, mean_lvl, ax + aw, mean_lvl, GREEN, 2.0, "7,4")
    s += text(ax + aw + 6, mean_lvl + 4, "⟨v²⟩", 11.5, GREEN, "start", "bold", "italic")
    s += text(ax + aw / 2, mean_lvl - 8, "середнє за вікно (ковзне)", 10, GREEN, "middle", "bold")

    # стрілка вниз: корінь
    s += arrow(ax + aw / 2, y2 + 18, ax + aw / 2, y2 + 54, INK, 2.4)
    s += text(ax + aw / 2 + 10, y2 + 40, "корінь  √⟨v²⟩", 11, INK, "start", "bold")

    # ── ряд 3 (унизу): результат RMS — стале число ──
    y3 = 372
    s += rect(ax + 40, y3, 280, 50, "#eef7f0", GREEN, 1.8, 10)
    s += text(ax + 180, y3 + 22, "RMS = √⟨v²⟩", 15, GREEN, "middle", "bold", "italic")
    s += text(ax + 180, y3 + 40, "стале «діюче» значення", 10.5, INK, "middle")

    # ── права колонка: формули неперервна vs дискретна ──
    bx = 540
    s += rect(bx, 96, 360, 150, "#fbfbff", BLUE, 1.6, 12)
    s += text(bx + 180, 122, "Те саме означення двома мовами", 12.5, BLUE, "middle", "bold")
    s += text(bx + 20, 152, "неперервно (за період T):", 11, GREY, "start", style="italic")
    s += text(bx + 28, 178, "Vrms = √( (1/T)·∫ v(t)² dt )", 13.5, INK, "start", "bold")
    s += text(bx + 20, 210, "у прошивці (N відліків):", 11, GREY, "start", style="italic")
    s += text(bx + 28, 236, "Vrms = √( (1/N)·Σ v[n]² )", 13.5, INK, "start", "bold")

    s += rect(bx, 262, 360, 170, "#fff8f0", ORANGE, 1.6, 12)
    s += text(bx + 180, 288, "Чому саме «квадрат → середнє → корінь»", 12, ORANGE, "middle", "bold")
    s += text(bx + 18, 314, "• квадрат прибирає знак: + і − гріють", 11, INK, "start")
    s += text(bx + 38, 332, "однаково, тож не скорочуються", 10, GREY, "start")
    s += text(bx + 18, 356, "• середнє — це «розсіяна потужність»", 11, INK, "start")
    s += text(bx + 38, 374, "на одиничному опорі (∝ тепло)", 10, GREY, "start")
    s += text(bx + 18, 398, "• корінь повертає у вольти, щоб", 11, INK, "start")
    s += text(bx + 38, 416, "число грілo R так само, як рівний DC", 10, GREY, "start")
    save("fig-r07-4a-1-pipeline.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.7.4a.2 — чим бреше «середньовипрямний» прилад на несинусоїді
# ════════════════════════════════════════════════════════════════════════════
def fig_form_factor():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 30, "Чому дешевий мультиметр бреше на несинусоїді",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "він міряє середньовипрямне |v| і множить на 1.11 — множник, зашитий ЛИШЕ для чистого синуса",
              11, GREY, "middle", style="italic")

    panels = [
        # (заголовок, генератор v(t), правда Vrms/Vpk, |avg|/Vpk, підпис похибки, колір)
        ("Чистий синус", "sine", 0.7071, 0.6366, "похибка ≈ 0", GREEN),
        ("Меандр (50%)", "square", 1.0, 1.0, "завищує на 11%", ORANGE),
        ("Гострі піки (фазовий зріз)", "spiky", None, None, "занижує в рази", RED),
    ]
    pw = 290
    gap = 14
    x0 = 18
    for idx, (title, kind, _t1, _t2, errnote, col) in enumerate(panels):
        px = x0 + idx * (pw + gap)
        s += rect(px, 78, pw, 372, "#ffffff", col, 1.8, 12)
        s += text(px + pw / 2, 102, title, 13.5, col, "middle", "bold")

        ax = px + 30
        aw = pw - 60
        ay = 178
        amp = 52
        s += line(ax, ay, ax + aw, ay, GREY, 1.2)
        s += text(ax - 6, ay + 4, "0", 9, GREY, "end")

        # побудова сигналу: масив (t, v) у [−1..1], 1 період
        N = 240
        vs = []
        for i in range(N + 1):
            t = i / N
            if kind == "sine":
                v = math.sin(2 * math.pi * t)
            elif kind == "square":
                v = 1.0 if t < 0.5 else -1.0
            else:  # spiky: вузький імпульс із великим піком, мала шпаруватість
                # імпульс шириною ~8% періоду, висота 1.0; решта ≈ 0
                if t < 0.08:
                    v = math.sin(math.pi * t / 0.08)
                elif 0.5 <= t < 0.58:
                    v = -math.sin(math.pi * (t - 0.5) / 0.08)
                else:
                    v = 0.0
            vs.append((t, v))

        # крива сигналу
        pts = [(ax + t * aw, ay - amp * v) for (t, v) in vs]
        s += polyline(pts, INK, 2.4)

        # обчислити справжній RMS і середньовипрямне чисельно
        sq = sum(v * v for (_, v) in vs) / len(vs)
        rms = math.sqrt(sq)
        mav = sum(abs(v) for (_, v) in vs) / len(vs)
        meter = 1.11072 * mav  # що покаже середньовипрямний прилад (×форм-фактор синуса)

        # рівні: справжній RMS (зелена пунктирна) і показ приладу (червона)
        s += line(ax, ay - amp * rms, ax + aw, ay - amp * rms, GREEN, 2.0, "6,4")
        s += text(ax + aw + 4, ay - amp * rms + 4, "RMS", 9.5, GREEN, "start", "bold")
        s += line(ax, ay - amp * meter, ax + aw, ay - amp * meter, RED, 2.0, "3,3")
        # підпис показу приладу зміщуємо, щоб не злипся з RMS
        lbl_y = ay - amp * meter + (14 if abs(rms - meter) < 0.06 else 4)
        s += text(ax + aw + 4, lbl_y, "показ", 9.5, RED, "start", "bold")

        # числовий блок під графіком
        by = 250
        s += text(px + pw / 2, by, f"справжній RMS = {rms:.3f}·Vpk", 11, GREEN, "middle", "bold")
        s += text(px + pw / 2, by + 22, f"|середнє| = {mav:.3f}·Vpk", 10.5, INK, "middle")
        s += text(px + pw / 2, by + 42, f"прилад: 1.11·|середнє| = {meter:.3f}", 10.5, RED, "middle")
        err = (meter - rms) / rms * 100.0
        s += rect(px + 26, by + 58, pw - 52, 40, "#f7f7f7", col, 1.4, 8)
        s += text(px + pw / 2, by + 76, errnote, 11, col, "middle", "bold")
        s += text(px + pw / 2, by + 92, f"(відхилення {err:+.0f}%)", 9.5, GREY, "middle")

        # форм-фактор цього сигналу
        ff = rms / mav if mav > 1e-9 else float("inf")
        ffs = f"{ff:.2f}" if ff != float("inf") else "∞"
        s += text(px + pw / 2, by + 122, f"форм-фактор RMS/|avg| = {ffs}", 10, PURPLE, "middle", "bold")
        s += text(px + pw / 2, by + 140, "(прилад припускає 1.11)", 9, GREY, "middle")

    save("fig-r07-4a-2-form-factor.svg", s)


if __name__ == "__main__":
    fig_pipeline()
    fig_form_factor()
    print("OK")
