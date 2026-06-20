# -*- coding: utf-8 -*-
"""Фігури до теми «Захист від переполюсування».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def diode_symbol(x, y, w=44, color=INK, sw=2.2, flip=False):
    """Символ діода (трикутник + риска) уздовж горизонталі, центр (x+w/2, y).
    Анод ліворуч, катод праворуч; flip=True дзеркалить."""
    h = 18
    if not flip:
        tri = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (x, y - h / 2, x, y + h / 2, x + w * 0.62, y)
        barx = x + w * 0.62
    else:
        tri = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (x + w, y - h / 2, x + w, y + h / 2, x + w * 0.38, y)
        barx = x + w * 0.38
    out = '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (tri, "#fdecea", color, sw)
    out += line(barx, y - h / 2 - 2, barx, y + h / 2 + 2, color=color, sw=sw + 0.6)
    return out


# ── 1. Чому зворотна полярність убиває плату ─────────────────────────────────
def fig_why_kills():
    W, H = 740, 380
    f = [text(W / 2, 26, "Зворотна полярність жене струм туди, куди він не має текти", size=16, bold=True)]

    def panel(x0, title, src_top_plus, ok):
        col = FIELD if ok else POS
        fl = "#eef6ef" if ok else "#fbeee6"
        f.append(rect(x0, 52, 320, 296, fill=BG, stroke=col, sw=2, rx=12))
        f.append(text(x0 + 160, 76, title, size=13.5, bold=True, color=INK))
        # клеми джерела
        ty, by = 110, 250
        if src_top_plus:
            f.append(plus(x0 + 40, ty, 11)); f.append(minus(x0 + 40, by, 11))
        else:
            f.append(minus(x0 + 40, ty, 11)); f.append(plus(x0 + 40, by, 11))
        # шина живлення (верх) і земля (низ)
        f.append(line(x0 + 40, ty, x0 + 90, ty, color=LINE, sw=2))
        f.append(line(x0 + 40, by, x0 + 90, by, color=LINE, sw=2))
        f.append(line(x0 + 90, ty, x0 + 280, ty, color=LINE, sw=2))   # VCC rail
        f.append(line(x0 + 90, by, x0 + 280, by, color=LINE, sw=2))   # GND rail
        # електролітичний конденсатор (полярний): + завжди вгорі
        cx = x0 + 150
        f.append(line(cx, ty, cx, ty + 36, color=LINE, sw=2))
        f.append(line(cx - 16, ty + 36, cx + 16, ty + 36, color=LINE, sw=3))     # пряма пластина (+)
        f.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="3"/>'
                 % (cx - 16, ty + 50, cx, ty + 44, cx + 16, ty + 50, LINE))      # вигнута (−)
        f.append(line(cx, ty + 50, cx, by, color=LINE, sw=2))
        f.append(text(cx + 22, ty + 34, "+", size=15, bold=True, color=POS))
        # мікросхема з захисним діодом входу живлення на землю
        ix = x0 + 245
        f.append(rect(ix - 22, 168, 44, 64, fill="#e9edf2", stroke=LINE, sw=1.6, rx=4))
        f.append(text(ix, 204, "IC", size=12, bold=True, color=INK))
        f.append(line(ix, ty, ix, 168, color=LINE, sw=1.6))
        f.append(line(ix, 232, ix, by, color=LINE, sw=1.6))
        if ok:
            f.append(text(x0 + 160, 300, "струм тече лише вперед —", size=11.5, color=INK))
            f.append(text(x0 + 160, 318, "конденсатор і діоди в нормі", size=11.5, color=INK))
        else:
            # стрілки зворотного струму крізь кондер і діод
            f.append(arrow(cx + 4, by - 10, cx + 4, ty + 56, color=POS, sw=2.4))
            f.append(arrow(ix + 4, 230, ix + 4, 172, color=POS, sw=2.4))
            f.append(text(x0 + 160, 300, "зворотна напруга рве", size=11.5, color=POS, bold=True))
            f.append(text(x0 + 160, 318, "кондер і захисні діоди IC", size=11.5, color=POS, bold=True))

    panel(20, "Правильно: + згори", True, True)
    panel(400, "Переплутано: + знизу", False, False)
    render(os.path.join(IMG, "why-kills.svg"), W, H, *f)


# ── 2. Три способи захисту поряд ─────────────────────────────────────────────
def fig_three_methods():
    W, H = 760, 360
    f = [text(W / 2, 26, "Три способи пустити струм лише в правильний бік", size=16, bold=True)]

    cards = [
        ("Послідовний діод (Si)", NEG, "#eef2f8", "series", "Vf ≈ 0.7 В",
         "найдешевше,\nале гріє і просаджує"),
        ("Діод Шотткі", "#e08a3c", "#fbeee6", "schottky", "Vf ≈ 0.4 В",
         "те саме, але вдвічі\nменше падіння"),
        ("P-MOSFET «ідеальний діод»", FIELD, "#eef6ef", "pmos", "I·Rds(on) ≈ 0.06 В",
         "майже без втрат,\nкерування складніше"),
    ]
    cw, gap = 232, 18
    x = (W - (3 * cw + 2 * gap)) / 2
    top = 50
    for title, col, fl, kind, drop, note in cards:
        f.append(rect(x, top, cw, 286, fill=fl, stroke=col, sw=2, rx=12))
        f.append(text(x + cw / 2, top + 24, title, size=12.5, bold=True, color=INK))
        f.append(line(x + 16, top + 34, x + cw - 16, top + 34, color=col, sw=1.2))
        # схемка: + -> елемент -> навантаження
        ey = top + 96
        f.append(plus(x + 30, ey, 10))
        f.append(line(x + 40, ey, x + 70, ey, color=LINE, sw=2))
        if kind in ("series", "schottky"):
            f.append(diode_symbol(x + 70, ey, w=46, color=(NEG if kind == "series" else "#e08a3c")))
            if kind == "schottky":
                # «гачки» Шотткі на рисці
                bx = x + 70 + 46 * 0.62
                f.append(line(bx, ey - 11, bx - 6, ey - 11, color="#e08a3c", sw=2))
                f.append(line(bx, ey + 11, bx + 6, ey + 11, color="#e08a3c", sw=2))
            f.append(line(x + 116, ey, x + 150, ey, color=LINE, sw=2))
            ld = x + 150
        else:
            # P-MOSFET у верхньому плечі: прямокутник з G/S/D
            mx = x + 80
            f.append(rect(mx, ey - 22, 40, 44, fill="#e9edf2", stroke=FIELD, sw=2, rx=4))
            f.append(text(mx + 20, ey + 5, "P", size=14, bold=True, color=FIELD))
            f.append(line(x + 70, ey, mx, ey, color=LINE, sw=2))           # source
            f.append(line(mx + 40, ey, mx + 70, ey, color=LINE, sw=2))     # drain
            f.append(line(mx + 20, ey + 22, mx + 20, ey + 40, color=LINE, sw=1.6))  # gate down
            f.append(text(mx + 20, ey + 54, "G→R→земля", size=9.5, color=MUTED))
            ld = mx + 70
        # навантаження
        f.append(rect(ld, ey - 14, 30, 28, fill=BG, stroke=LINE, sw=1.6, rx=3))
        f.append(text(ld + 15, ey + 5, "R", size=12, color=INK))
        f.append(line(ld + 30, ey, ld + 30, ey + 34, color=LINE, sw=2))
        f.append(line(x + 30, ey + 16, x + 30, ey + 34, color=LINE, sw=2))
        f.append(line(x + 30, ey + 34, ld + 30, ey + 34, color=LINE, sw=2))  # земля
        # падіння + примітка
        b, _, _ = textbox(x + cw / 2, top + 200, drop, size=12.5, fill=BG, stroke=col, bold=True)
        f.append(b)
        f.append(mtext(x + cw / 2, top + 240, note, size=11, color=MUTED, lh=1.25))
        x += cw + gap
    render(os.path.join(IMG, "three-methods.svg"), W, H, *f)


# ── 3. Запобіжник + діод на землю (clamp) ────────────────────────────────────
def fig_fuse_clamp():
    W, H = 740, 360
    f = [text(W / 2, 26, "Запобіжник + діод на землю: діод «коротить» зворотну напругу", size=16, bold=True)]

    def panel(x0, title, plus_top, ok):
        col = FIELD if ok else POS
        f.append(rect(x0, 52, 320, 290, fill=BG, stroke=col, sw=2, rx=12))
        f.append(text(x0 + 160, 76, title, size=13.5, bold=True, color=INK))
        ty, by = 112, 252
        if plus_top:
            f.append(plus(x0 + 36, ty, 11)); f.append(minus(x0 + 36, by, 11))
        else:
            f.append(minus(x0 + 36, ty, 11)); f.append(plus(x0 + 36, by, 11))
        f.append(line(x0 + 36, ty, x0 + 80, ty, color=LINE, sw=2))
        f.append(line(x0 + 36, by, x0 + 290, by, color=LINE, sw=2))   # земля
        # запобіжник (прямокутник «F»)
        fx = x0 + 80
        f.append(rect(fx, ty - 11, 44, 22, fill="#f6e7c8", stroke=LINE, sw=1.6, rx=4))
        f.append(text(fx + 22, ty + 5, "F", size=12, bold=True, color=INK))
        f.append(line(fx + 44, ty, x0 + 290, ty, color=LINE, sw=2))   # шина після запобіжника
        # діод-clamp: катод на шину, анод на землю (блокує в нормі, коротить у реверсі)
        dx = x0 + 210
        f.append(line(dx, ty, dx, ty + 40, color=LINE, sw=1.8))
        # вертикальний діод символ: катод угорі
        f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (dx - 11, ty + 78, dx + 11, ty + 78, dx, ty + 50, "#fdecea", LINE))
        f.append(line(dx - 12, ty + 50, dx + 12, ty + 50, color=LINE, sw=2.6))   # риска (катод)
        f.append(line(dx, ty + 78, dx, by, color=LINE, sw=1.8))
        # навантаження
        lx = x0 + 268
        f.append(rect(lx - 14, 168, 28, 40, fill="#e9edf2", stroke=LINE, sw=1.6, rx=3))
        f.append(text(lx, 192, "IC", size=11, bold=True, color=INK))
        f.append(line(lx, ty, lx, 168, color=LINE, sw=1.6))
        f.append(line(lx, 208, lx, by, color=LINE, sw=1.6))
        if ok:
            f.append(text(x0 + 160, 304, "діод зворотно зміщений →", size=11.5, color=INK))
            f.append(text(x0 + 160, 322, "мовчить, плата живиться", size=11.5, color=INK))
        else:
            f.append(arrow(dx - 14, ty + 20, dx - 14, ty + 64, color=POS, sw=2.4))
            f.append(text(x0 + 160, 304, "діод відкрився, струм великий →", size=11, color=POS, bold=True))
            f.append(text(x0 + 160, 322, "запобіжник перегорів, плата ціла", size=11, color=POS, bold=True))

    panel(20, "Норма: діод закритий", True, True)
    panel(400, "Реверс: діод коротить, F горить", False, False)
    render(os.path.join(IMG, "fuse-clamp.svg"), W, H, *f)


# ── 4. Компроміс: падіння напруги від струму ─────────────────────────────────
def fig_drop_vs_current():
    W, H = 720, 410
    f = [text(W / 2, 26, "Падіння напруги на захисті: діод майже не змінюється, MOSFET росте від нуля",
              size=15.5, bold=True)]

    ox, oy = 92, 330
    ax_w, ax_h = 540, 250
    Imax = 10.0      # А по осі X
    Vmax = 0.8       # В по осі Y
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 42, "струм навантаження, А", size=12, color=INK))
    f.append(text(ox - 64, oy - ax_h / 2, "падіння", size=12, color=INK))
    f.append(text(ox - 64, oy - ax_h / 2 + 16, "В", size=11, color=MUTED))

    for i in range(0, 11, 2):
        x = ox + i / Imax * ax_w
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.3))
        f.append(text(x, oy + 20, str(i), size=11, color=MUTED))
    for v in (0.0, 0.2, 0.4, 0.6, 0.8):
        y = oy - v / Vmax * ax_h
        f.append(line(ox - 5, y, ox, y, color=INK, sw=1.3))
        f.append(text(ox - 18, y + 4, "%.1f" % v, size=11, color=MUTED))

    def px(i, v):
        return ox + i / Imax * ax_w, oy - v / Vmax * ax_h

    def curve(points, color, sw=2.8, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        pts = " ".join("%.1f,%.1f" % px(i, v) for i, v in points)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (pts, color, sw, d))

    # Si-діод: майже плато ~0.7 В (логарифмічно повзе)
    import math
    si = [(i, 0.55 + 0.045 * math.log1p(i)) for i in [0.05, 0.2, 0.5, 1, 2, 4, 6, 8, 10]]
    curve(si, NEG)
    # Шотткі: плато ~0.4 В
    sch = [(i, 0.30 + 0.035 * math.log1p(i)) for i in [0.05, 0.2, 0.5, 1, 2, 4, 6, 8, 10]]
    curve(sch, "#e08a3c")
    # MOSFET 20 мОм: пряма I·R від нуля
    mos = [(i, i * 0.020) for i in [0, 2, 4, 6, 8, 10]]
    curve(mos, FIELD)

    # підписи кривих
    x_si, y_si = px(10, 0.55 + 0.045 * math.log1p(10))
    f.append(text(x_si - 6, y_si - 8, "Si-діод (~0.7 В)", size=12, color=NEG, anchor="end", bold=True))
    x_sc, y_sc = px(10, 0.30 + 0.035 * math.log1p(10))
    f.append(text(x_sc - 6, y_sc - 8, "Шотткі (~0.4 В)", size=12, color="#e08a3c", anchor="end", bold=True))
    x_mo, y_mo = px(10, 0.20)
    f.append(text(x_mo - 6, y_mo + 4, "MOSFET 20 мОм", size=12, color=FIELD, anchor="end", bold=True))

    # точка перетину MOSFET та Шотткі ~ 20 А поза графіком; позначимо словом
    b, _, _ = textbox(ox + 150, oy - ax_h + 26,
                      "MOSFET виграє скрізь до ~20 А\n(де I·Rds(on) дорівнює Vf Шотткі)",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "drop-vs-current.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_kills()
    fig_three_methods()
    fig_fuse_clamp()
    fig_drop_vs_current()
    print("OK: 4 figures ->", IMG)
