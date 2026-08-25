# -*- coding: utf-8 -*-
"""Фігури до теми «Yield» (вихід придатних кристалів) та її 🧮-вставки.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
DEAD = "#fdecec"   # заливка враженого кристала
LIVE = "#eef6ef"   # заливка цілого кристала
GOLD = "#b9770e"   # орієнтир «одна помилка на кристал»


def _x(cx, cy, size=17, color=POS):
    """Червоний хрестик-дефект."""
    return text(cx, cy + size * 0.34, "×", size=size, color=color, bold=True)


# ── ФІГУРИ ОСНОВНОЇ СТАТТІ ───────────────────────────────────────────────────

# 1. Та сама густина дефектів по-різному вражає великі й малі кристали.
def fig_defects():
    W, H = 760, 430
    f = [text(W / 2, 28, "Та сама густина дефектів — різна доля втрат", size=15, bold=True)]

    # спільна розсипка дефектів у нормованих координатах кола (одиничний радіус)
    pts = [(-0.55, -0.50), (-0.10, -0.62), (0.40, -0.40), (-0.30, -0.05),
           (0.25, 0.10), (0.60, -0.05), (-0.55, 0.35), (0.05, 0.45),
           (0.45, 0.45), (-0.20, 0.62)]

    def wafer(cx, cy, R, n, title):
        out = [circle(cx, cy, R, fill="#f3f7fc", stroke=INK, sw=2)]
        # flat (зріз) знизу
        out.append(line(cx - R * 0.34, cy + R * 0.94, cx + R * 0.34, cy + R * 0.94,
                        color=BG, sw=6))
        step = 2.0 * R / n
        x0, y0 = cx - R, cy - R
        # які клітинки вражені: точка лежить у клітинці
        hit = set()
        for px, py in pts:
            gx = int((px + 1.0) / 2.0 * n)
            gy = int((py + 1.0) / 2.0 * n)
            gx = min(max(gx, 0), n - 1)
            gy = min(max(gy, 0), n - 1)
            hit.add((gx, gy))
        live = dead = 0
        for gy in range(n):
            for gx in range(n):
                cxx = x0 + gx * step
                cyy = y0 + gy * step
                # лишаємо тільки клітинки, чий центр у колі
                mx = cxx + step / 2 - cx
                my = cyy + step / 2 - cy
                if mx * mx + my * my > (R - step * 0.15) ** 2:
                    continue
                bad = (gx, gy) in hit
                if bad:
                    dead += 1
                else:
                    live += 1
                out.append(rect(cxx, cyy, step - 1, step - 1,
                                fill=(DEAD if bad else LIVE),
                                stroke=MUTED, sw=0.7, rx=0))
        for px, py in pts:
            out.append(_x(cx + px * R, cy + py * R, size=int(step * 0.5)))
        out.append(text(cx, cy + R + 26, title, size=12.5, bold=True))
        tot = live + dead
        y = int(round(100.0 * live / tot)) if tot else 0
        out.append(text(cx, cy + R + 44, "придатних ≈ %d%%" % y,
                        size=12, color=(FIELD if y >= 50 else POS), bold=True))
        return out

    f += wafer(195, 200, 150, 4, "великі кристали")
    f += wafer(565, 200, 150, 8, "дрібні кристали")
    # підсумковий рядок
    f.append(text(W / 2, 415,
                  "та сама розсипка дефектів (×): великий кристал майже завжди ловить дефект, "
                  "дрібний здебільшого оминає",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "defects.svg"), W, H, *f)


def _curve_axes(f, ox, oy, w, h):
    """Осі для кривої виходу 0..100% по Y, 0..A_max по X. Повертає масштабери."""
    f.append(line(ox, oy, ox, oy - h, color=INK, sw=1.6))      # Y
    f.append(line(ox, oy, ox + w, oy, color=INK, sw=1.6))      # X
    for frac, lbl in [(0, "0%"), (0.25, "25%"), (0.5, "50%"), (0.75, "75%"), (1.0, "100%")]:
        yy = oy - frac * h
        f.append(line(ox - 5, yy, ox, yy, color=INK, sw=1.2))
        f.append(text(ox - 9, yy + 4, lbl, size=11, color=MUTED, anchor="end"))


# 2. Крива виходу Y ≈ e^(−D·A): спад експоненційний.
def fig_yield_curve():
    W, H = 740, 380
    f = [text(W / 2, 28, "Вихід падає з площею кристала (модель Пуассона)", size=15, bold=True)]
    ox, oy, w, h = 92, 300, 540, 220
    Amax = 8.0
    _curve_axes(f, ox, oy, w, h)
    f.append(text(ox - 9, oy - h - 8, "вихід Y", size=12, color=MUTED, anchor="start"))
    f.append(text(ox + w, oy + 22, "площа кристала A →", size=12, color=MUTED, anchor="end"))

    def plot(D, color, label, ly):
        pts = []
        N = 120
        for i in range(N + 1):
            A = Amax * i / N
            Y = math.exp(-D * A)
            x = ox + (A / Amax) * w
            y = oy - Y * h
            pts.append("%.1f,%.1f" % (x, y))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), color))
        f.append(text(ox + w + 6, ly, label, size=11, color=color, anchor="start"))

    plot(0.2, FIELD, "мало дефектів", oy - math.exp(-0.2 * Amax) * h)
    plot(0.5, POS, "багато дефектів", oy - math.exp(-0.5 * Amax) * h)

    # точки на кривій D=0.5: малий 0.5 см² → 78%, великий 6 см² → 5%
    for A, lbl, place in [(0.5, "малий кристал", "up"), (6.0, "великий кристал", "up")]:
        Y = math.exp(-0.5 * A)
        x = ox + (A / Amax) * w
        y = oy - Y * h
        f.append(circle(x, y, 4, fill=POS, stroke="#7a1812", sw=1.2))
        f.append(line(x, y, x, oy, color=MUTED, sw=1, dash="3,3"))
        f.append(text(x, oy + 17, lbl, size=10.5, color=INK))
        f.append(text(x, y - 9, "%d%%" % round(Y * 100), size=11, color=POS, bold=True))

    f.append(text(ox + w * 0.52, oy - h + 26, "Y ≈ e^(−D · A)", size=14, bold=True))
    f.append(text(W / 2, 368,
                  "подвоїти площу — не вдвічі, а експоненційно менше придатних: "
                  "ось чому великий чіп коштує непропорційно дорого",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "yield-curve.svg"), W, H, *f)


# 3. Подвійний удар по ціні: менше кристалів + нижчий вихід.
def fig_cost():
    W, H = 720, 320
    f = [text(W / 2, 28, "Подвійний удар по ціні великого кристала", size=15, bold=True)]
    f.append(fitbox(70, 70, 580, 50,
                    "Менше кристалів на пластині\nвелика площа → їх просто менше вміщається",
                    size=13, fill=FILL, stroke=MUTED))
    f.append(fitbox(70, 132, 580, 50,
                    "Нижчий вихід (більше браку)\nвелика площа → частіше ловить дефект (Y ↓)",
                    size=13, fill="#fdf3f2", stroke=POS))
    f.append(arrow(360, 188, 360, 214, color=INK, sw=2.2))
    box, bw, bh = textbox(360, 248, "ціна за придатний кристал\nросте набагато швидше за площу",
                          size=12.5, fill="#fde0dd", stroke=POS, color=POS, bold=True, min_w=320)
    f.append(box)
    f.append(text(W / 2, 308,
                  "два множники діють в один бік — тому подвоєння площі може здорожчати "
                  "придатний кристал у кілька разів",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "cost.svg"), W, H, *f)


# ── ФІГУРИ 🧮-ВСТАВКИ (math-yield-math.md) ───────────────────────────────────

# m1. Крива виходу з орієнтиром 1/e (та сама модель, акцент на математиці).
def fig_curve_math():
    W, H = 760, 400
    f = [text(W / 2, 28, "Вихід Y = e^(−A·D): спад експоненційний", size=15, bold=True)]
    ox, oy, w, h = 96, 312, 470, 232
    Amax = 8.0
    D = 0.5
    _curve_axes(f, ox, oy, w, h)
    f.append(text(ox - 9, oy - h - 8, "вихід Y", size=12, color=MUTED, anchor="start"))
    f.append(text(ox + w, oy + 22, "площа A, см² →", size=12, color=MUTED, anchor="end"))
    # підписи поділок осі X
    for A in [2, 4, 6, 8]:
        x = ox + (A / Amax) * w
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.2))
        f.append(text(x, oy + 18, str(A), size=10.5, color=MUTED))

    pts = []
    N = 140
    for i in range(N + 1):
        A = Amax * i / N
        Y = math.exp(-D * A)
        pts.append("%.1f,%.1f" % (ox + (A / Amax) * w, oy - Y * h))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), POS))

    # орієнтир 1/e на A = 1/D = 2 см²
    Ae = 1.0 / D
    xe = ox + (Ae / Amax) * w
    ye = oy - math.exp(-1) * h
    f.append(line(ox, ye, xe, ye, color=GOLD, sw=1.4, dash="5,4"))
    f.append(line(xe, ye, xe, oy, color=GOLD, sw=1.4, dash="5,4"))
    f.append(circle(xe, ye, 4.5, fill=GOLD, stroke="#7a4f08", sw=1.2))
    f.append(text(xe + 8, ye - 6, "A = 1/D → Y = 1/e ≈ 37%", size=11, color=GOLD,
                  anchor="start", bold=True))

    # три ключові точки
    for A in [0.5, 6.0]:
        Y = math.exp(-D * A)
        x = ox + (A / Amax) * w
        y = oy - Y * h
        f.append(circle(x, y, 3.6, fill=POS, stroke="#7a1812", sw=1.0))
        f.append(text(x, y - 8, "%d%%" % round(Y * 100), size=10.5, color=POS, bold=True))

    # бічна табличка-розклад
    tx = ox + w + 30
    f.append(fitbox(tx, 70, 150, 250, "", fill="#fbfbfb", stroke="#e4e4e4"))
    rows = ["D = 0.5 деф./см²", "", "A = 0.5 → 78%", "A = 2.0 → 37%", "A = 6.0 → 5%",
            "", "×12 площі →", "÷15 придатних"]
    for i, r in enumerate(rows):
        f.append(text(tx + 12, 96 + i * 28, r, size=11.5,
                      color=(INK if "→" in r or "D =" in r else MUTED),
                      anchor="start", bold=("→" in r)))
    return render(os.path.join(IMG, "curve-math.svg"), W, H, *f)


# m2. Та сама розсипка дефектів, дві сітки кристалів (велика vs дрібна).
def fig_wafer_math():
    W, H = 760, 430
    f = [text(W / 2, 28, "Ті самі дефекти, інший розмір кристала", size=15, bold=True)]
    pts = [(-0.55, -0.50), (-0.10, -0.62), (0.40, -0.40), (-0.30, -0.05),
           (0.25, 0.10), (0.60, -0.05), (-0.55, 0.35), (0.05, 0.45),
           (0.45, 0.45), (-0.20, 0.62)]

    def wafer(cx, cy, R, n, title):
        out = [circle(cx, cy, R, fill="#fbfbfb", stroke=MUTED, sw=1.8)]
        out.append(line(cx - R * 0.34, cy + R * 0.94, cx + R * 0.34, cy + R * 0.94,
                        color="#d8d8d8", sw=4))
        step = 2.0 * R / n
        x0, y0 = cx - R, cy - R
        hit = set()
        for px, py in pts:
            gx = min(max(int((px + 1.0) / 2.0 * n), 0), n - 1)
            gy = min(max(int((py + 1.0) / 2.0 * n), 0), n - 1)
            hit.add((gx, gy))
        live = dead = 0
        for gy in range(n):
            for gx in range(n):
                cxx, cyy = x0 + gx * step, y0 + gy * step
                mx, my = cxx + step / 2 - cx, cyy + step / 2 - cy
                if mx * mx + my * my > (R - step * 0.15) ** 2:
                    continue
                bad = (gx, gy) in hit
                live, dead = (live, dead + 1) if bad else (live + 1, dead)
                out.append(rect(cxx, cyy, step - 1, step - 1,
                                fill=(DEAD if bad else LIVE), stroke=MUTED, sw=0.7, rx=0))
        for px, py in pts:
            out.append(_x(cx + px * R, cy + py * R, size=int(step * 0.5)))
        out.append(text(cx, cy + R + 26, title, size=12.5, bold=True))
        tot = live + dead
        out.append(text(cx, cy + R + 44, "придатних ≈ %d%%" % (round(100 * live / tot) if tot else 0),
                        size=12, color=FIELD, bold=True))
        return out

    f += wafer(195, 205, 150, 4, "великі кристали (4×4)")
    f += wafer(565, 205, 150, 8, "дрібні кристали (8×8)")
    f.append(text(W / 2, 418,
                  "дрібний кристал втрачає менше площі на кожен дефект — це та сама "
                  "експонента, побачена очима",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "wafer-math.svg"), W, H, *f)


# m3. Моноліт проти чиплетів: вихід кожного дрібного кристала кардинально вищий.
def fig_chiplets_math():
    W, H = 760, 430
    f = [text(W / 2, 28, "Моноліт проти чиплетів тієї ж сумарної площі", size=15, bold=True)]
    f.append(text(W / 2, 48, "та сама логіка, та сама густина D = 0.5/см² — але вихід різний",
                  size=11.5, color=MUTED, italic=True))

    # ліворуч: моноліт
    f.append(rect(50, 70, 320, 250, fill="#fdf6f5", stroke=POS, sw=1.6, rx=12))
    f.append(text(210, 96, "Моноліт: один кристал A = 4 см²", size=13, bold=True))
    f.append(rect(140, 116, 140, 140, fill=DEAD, stroke=POS, sw=2.0, rx=6))
    f.append(_x(178, 168, size=20))
    f.append(_x(240, 200, size=20))
    f.append(_x(196, 232, size=20))
    f.append(text(210, 278, "будь-який × → весь кристал у брак", size=10.5, color=POS))
    f.append('<text x="64" y="306" font-family="Consolas, monospace" font-size="12.5" '
             'fill="%s" font-weight="700">Y = e^(−4·0.5) = e^(−2) ≈ 13.5%%</text>' % INK)

    # праворуч: чиплети
    f.append(rect(390, 70, 320, 250, fill="#f1f8f3", stroke=FIELD, sw=1.6, rx=12))
    f.append(text(550, 96, "Чиплети: 4 кристали по 1 см²", size=13, bold=True))
    quad = [(470, 116, DEAD, POS, "×"), (556, 116, LIVE, FIELD, "OK"),
            (470, 202, LIVE, FIELD, "OK"), (556, 202, DEAD, POS, "×")]
    for qx, qy, fill, stroke, mark in quad:
        f.append(rect(qx, qy, 72, 72, fill=fill, stroke=stroke, sw=1.8, rx=5))
        if mark == "×":
            f.append(_x(qx + 36, qy + 36, size=18))
        else:
            f.append(text(qx + 36, qy + 42, "OK", size=12, color=FIELD, bold=True))
    f.append(text(550, 308, "брак — лише дефектний квадратик, решта годні", size=10, color=FIELD))
    f.append('<text x="404" y="306" font-family="Consolas, monospace" font-size="12" '
             'fill="%s" font-weight="700">Y₁ = e^(−0.5) ≈ 60.7%% на чиплет</text>' % INK)

    f.append(arrow(372, 195, 388, 195, color=INK, sw=2.2))

    # підсумкова смуга
    f.append(rect(50, 336, 660, 60, fill="#fbfbfb", stroke="#e4e4e4", sw=1.4, rx=10))
    f.append('<text x="66" y="360" font-family="Consolas, monospace" font-size="12" '
             'fill="%s">моноліт : зі 100 заготовок годних ≈ 14</text>' % INK)
    f.append('<text x="66" y="380" font-family="Consolas, monospace" font-size="12" '
             'fill="%s">чиплети : зі 100 годних ≈ 61 → ≈ 15 систем по 4</text>' % INK)
    f.append(text(700, 414, "ціна виграшу — щільний міжз'єднувач між кристалами",
                  size=10.5, color=MUTED, anchor="end", italic=True))
    return render(os.path.join(IMG, "chiplets-math.svg"), W, H, *f)


if __name__ == "__main__":
    fig_defects()
    fig_yield_curve()
    fig_cost()
    fig_curve_math()
    fig_wafer_math()
    fig_chiplets_math()
    print("yield figs done ->", IMG)
