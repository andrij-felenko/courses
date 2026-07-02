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


# ── 5. Анатомія пасивного P-MOSFET-захисту (детальна) ────────────────────────
def fig_pmos_anatomy():
    W, H = 760, 400
    f = [text(W / 2, 26, "Пасивний P-MOSFET-«ідеальний діод»: як вмикається і як закривається",
              size=15.5, bold=True)]

    # шини
    xin, xld = 120, 620
    yv, yg = 110, 320            # шина живлення / земля
    f.append(plus(xin - 34, yv, 11)); f.append(minus(xin - 34, yg, 11))
    f.append(line(xin - 34, yv, xin, yv, color=LINE, sw=2))
    f.append(line(xin - 34, yg, xld, yg, color=LINE, sw=2))       # земля
    f.append(text(xin - 34, yv - 22, "вхід", size=11, color=MUTED))

    # корпус MOSFET
    mx, my = xin + 60, yv
    bw, bh = 120, 70
    f.append(rect(mx, my - bh / 2, bw, bh, fill="#eef6ef", stroke=FIELD, sw=2.2, rx=8))
    f.append(text(mx + bw / 2, my - 12, "P-MOSFET", size=13, bold=True, color=FIELD))
    # витік (S) зліва, стік (D) справа
    f.append(line(xin, yv, mx, yv, color=LINE, sw=2.2))
    f.append(text(mx - 8, yv - 8, "S", size=12, bold=True, color=INK, anchor="end"))
    f.append(line(mx + bw, yv, xld, yv, color=LINE, sw=2.2))
    f.append(text(mx + bw + 8, yv - 8, "D", size=12, bold=True, color=INK))
    # body-діод усередині корпусу: анод(D) -> катод(S) => блокує зворотний струм
    dx0 = mx + bw / 2 - 22
    f.append(text(mx + bw / 2, my + 8, "body", size=9.5, color=MUTED))
    f.append(diode_symbol(dx0, my + 22, w=44, color=NEG, sw=1.8, flip=True))
    f.append(text(mx + bw / 2, my + 44, "блокує реверс", size=9, color=NEG))

    # затвор донизу через Rg на землю + стабілітрон
    gx = mx + bw / 2
    gy = my + bh / 2
    f.append(line(gx, gy, gx, gy + 26, color=LINE, sw=2))
    f.append(text(gx + 6, gy + 14, "G", size=12, bold=True, color=INK))
    # Rg
    f.append(rect(gx - 16, gy + 26, 32, 46, fill=BG, stroke=LINE, sw=1.6, rx=3))
    f.append(text(gx, gy + 54, "Rg", size=11, color=INK))
    f.append(line(gx, gy + 72, gx, yg, color=LINE, sw=2))
    # стабілітрон затвор-витік (символ праворуч)
    zx = gx + 70
    f.append(line(gx, gy + 12, zx, gy + 12, color=LINE, sw=1.6))
    f.append(line(zx, gy + 12, zx, my - bh / 2 + 6, color=LINE, sw=1.6, dash="4 3"))
    f.append(line(zx, my - bh / 2 + 6, mx + bw, my - bh / 2 + 6, color=LINE, sw=1.6, dash="4 3"))
    f.append(line(mx + bw, my - bh / 2 + 6, mx + bw, yv, color=LINE, sw=1.6, dash="4 3"))
    f.append(mtext(zx + 6, gy + 34, "стабілітрон\nзатвор–витік", size=9, color=MUTED, anchor="start"))

    # навантаження
    f.append(rect(xld, yv - 16, 34, 32, fill=BG, stroke=LINE, sw=1.8, rx=3))
    f.append(text(xld + 17, yv + 5, "R", size=12, color=INK))
    f.append(line(xld + 34, yv, xld + 34, yg, color=LINE, sw=2))

    # рівняння-підписи (праворуч від схеми, у вільному полі)
    b1, _, _ = textbox(560, 205, "Vgs = 0 − Vin = −Vin\n→ канал відкритий,\nпадіння I·Rds(on)",
                       size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b1)
    b2, _, _ = textbox(560, 285, "закриття: τ = Rg · Ciss\n(десятки–сотні мкс)\nоксид затвора: |Vgs| ≳ 20 В",
                       size=11.5, fill=BG, stroke=LINE)
    f.append(b2)
    render(os.path.join(IMG, "pmos-anatomy.svg"), W, H, *f)


# ── 6. Crowbar у часі: струм-імпульс, I²t і затиснута напруга ─────────────────
def fig_crowbar_it():
    import math
    W, H = 720, 420
    f = [text(W / 2, 24, "Crowbar у часі: струм тече крізь діод, поки I²t не перепалить запобіжник",
              size=14.5, bold=True)]

    ox, oy = 92, 210
    ax_w, ax_h = 300, 130
    # вісь струму (верхній графік)
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.7))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.7))
    f.append(text(ox - 40, oy - ax_h + 4, "струм", size=11, color=INK, anchor="start"))
    f.append(text(ox + ax_w - 4, oy + 18, "час", size=11, color=INK, anchor="end"))
    # прямокутний імпульс струму до t_fuse, тоді нуль
    tf = ox + ax_w * 0.62
    Ilv = oy - ax_h * 0.82
    f.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
             'fill="none" stroke="%s" stroke-width="2.8"/>'
             % (ox, oy, ox + 6, Ilv, tf, Ilv, tf, oy, ox + ax_w, oy, POS))
    # заливка площі I²t
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fbddd6" opacity="0.7"/>'
             % (ox + 6, Ilv, tf, Ilv, tf, oy, ox, oy))
    f.append(text((ox + tf) / 2, (Ilv + oy) / 2 + 4, "I²t", size=15, bold=True, color=POS))
    f.append(line(tf, oy, tf, oy + 6, color=INK, sw=1.3))
    f.append(text(tf, oy + 20, "t_fuse", size=10.5, color=MUTED))
    f.append(text(ox - 8, Ilv + 4, "I_rev", size=10.5, color=POS, anchor="end"))
    b, _, _ = textbox(tf + 90, oy - ax_h + 34, "площа під i²(t)\n>  I²t запобіжника\n<  I²t діода",
                      size=10.5, fill=BG, stroke=POS)
    f.append(b)

    # нижній графік: напруга на платі, затиснута ~ -0.7 В, поріг -1.5 В
    oy2 = 380
    ax_h2 = 120
    f.append(line(ox, oy2 - ax_h2 / 2, ox + ax_w, oy2 - ax_h2 / 2, color=INK, sw=1.7))   # вісь 0 В
    f.append(line(ox, oy2 - ax_h2, ox, oy2, color=INK, sw=1.7))
    f.append(text(ox - 40, oy2 - ax_h2 + 4, "V плати", size=11, color=INK, anchor="start"))
    f.append(text(ox + ax_w - 4, oy2 - ax_h2 / 2 - 6, "0 В", size=10, color=MUTED, anchor="end"))
    zero = oy2 - ax_h2 / 2
    vclamp = zero + 26      # ~ -0.7 В
    vthr = zero + 52        # ~ -1.5 В поріг оксиду
    # затиснута напруга: падає до -0.7 на час імпульсу, тоді 0
    f.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
             'fill="none" stroke="%s" stroke-width="2.6"/>'
             % (ox, zero, ox + 6, vclamp, tf, vclamp, tf, zero, ox + ax_w, zero, NEG))
    f.append(line(ox, vthr, ox + ax_w, vthr, color=POS, sw=1.4, dash="5 4"))
    f.append(text(ox + ax_w - 4, vthr + 14, "поріг оксиду ≈ −1.5 В", size=10, color=POS, anchor="end"))
    f.append(text(tf + 8, vclamp + 4, "діод тримає ≈ −0.7 В", size=10, color=NEG, anchor="start"))
    render(os.path.join(IMG, "crowbar-it.svg"), W, H, *f)


# ── 7. Форма сплеску зворотного струму при закритті каналу (math-вставка) ─────
def fig_reverse_spike():
    import math
    W, H = 740, 380
    f = [text(W / 2, 24, "Сплеск зворотного струму: пік одразу, спад у міру закриття каналу",
              size=15, bold=True)]

    ox, oy = 96, 300
    ax_w, ax_h = 560, 232
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))          # вісь часу
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))          # вісь струму
    f.append(text(ox + ax_w - 4, oy + 22, "час (у одиницях τ = Rg·Ciss)", size=11.5,
                  color=INK, anchor="end"))
    f.append(text(ox - 66, oy - ax_h + 10, "зворотний", size=11, color=INK, anchor="start"))
    f.append(text(ox - 66, oy - ax_h + 24, "струм", size=11, color=INK, anchor="start"))

    Tmax = 5.0                # осей — до 5τ
    Ipk = ax_h * 0.80         # пік у пікселях
    # мітки осі часу в одиницях τ
    for k in range(0, 6):
        x = ox + k / Tmax * ax_w
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.2))
        f.append(text(x, oy + 18, ("0" if k == 0 else "%dτ" % k), size=10.5, color=MUTED))

    # Модель: reverse current ~ ΔV / R_ch(t), R_ch(t) ∝ 1/|Vgs(t)|, Vgs спадає як e^(−t/τ).
    # Тобто провідність каналу ~ e^(−t/τ), струм ~ I_pk·e^(−t/τ) (поки канал ще проводить).
    N = 120
    pts = []
    for i in range(N + 1):
        tt = Tmax * i / N
        g = math.exp(-tt)     # нормована провідність каналу
        pts.append((ox + tt / Tmax * ax_w, oy - Ipk * g))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts), POS))
    # заливка площі = заряд Q
    poly = "%.1f,%.1f " % (ox, oy) + " ".join("%.1f,%.1f" % p for p in pts) + " %.1f,%.1f" % (pts[-1][0], oy)
    f.append('<polygon points="%s" fill="#fbddd6" opacity="0.65"/>' % poly)
    f.append(text(ox + ax_w * 0.16, oy - Ipk * 0.30, "Q = ∫ i·dt", size=15, bold=True, color=POS))

    # пік
    f.append(line(ox, oy - Ipk, ox + 6, oy - Ipk, color=MUTED, sw=1.2, dash="4 3"))
    f.append(text(ox - 8, oy - Ipk + 4, "I_пік", size=11, color=POS, anchor="end", bold=True))
    b, _, _ = textbox(ox + ax_w * 0.60, oy - ax_h + 46,
                      "I_пік = (V_вих − V_вх) / Rds(on)\nспадає з e^(−t/τ), бо канал\nзачиняється: Rканал росте",
                      size=11, fill=BG, stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "reverse-spike.svg"), W, H, *f)


# ── 8. Компроміс Rg: пік/заряд проти струму спокою (math-вставка) ─────────────
def fig_rg_tradeoff():
    import math
    W, H = 740, 400
    f = [text(W / 2, 24, "Вибір Rg: менший Rg — менший сплеск, але більший струм спокою",
              size=15, bold=True)]

    ox, oy = 96, 310
    ax_w, ax_h = 560, 244
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 40, "Rg (логарифмічна вісь) →", size=12, color=INK))

    # логарифмічна вісь Rg від 1к до 1М; дві протилежні криві
    decades = 3.0            # 10^3 діапазон (1к..1М)
    def X(rg_k):            # rg у кОм
        return ox + (math.log10(rg_k) / decades) * ax_w
    for e in range(0, 4):
        rg_k = 10 ** e
        x = ox + e / decades * ax_w
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.2))
        lbl = ("1 кОм", "10 кОм", "100 кОм", "1 МОм")[e]
        f.append(text(x, oy + 20, lbl, size=10.5, color=MUTED))

    # Струм спокою Iq = Vin/Rg  ↓ з ростом Rg (спадна крива)
    N = 80
    q = []
    for i in range(N + 1):
        e = decades * i / N
        rg_k = 10 ** e
        iq = 1.0 / rg_k          # нормовано (Vin=1)
        y = oy - (iq / 1.0) * ax_h * 0.9     # 1к -> майже верх
        q.append((ox + e / decades * ax_w, max(oy - ax_h, y)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in q), NEG))

    # Час закриття / заряд, що встиг перетекти  ∝ τ = Rg·Ciss  ↑ з ростом Rg (зростна)
    t = []
    for i in range(N + 1):
        e = decades * i / N
        rg_k = 10 ** e
        val = rg_k / 1000.0      # нормовано до 1 на 1М
        y = oy - (val / 1.0) * ax_h * 0.9
        t.append((ox + e / decades * ax_w, max(oy - ax_h, y)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in t), POS))

    # підписи кривих
    f.append(text(X(1.7), oy - ax_h * 0.86, "струм спокою  Iq = Vin/Rg", size=12,
                  color=NEG, anchor="start", bold=True))
    f.append(text(X(120), oy - ax_h * 0.86, "заряд Q ∝ τ = Rg·Ciss", size=12,
                  color=POS, anchor="end", bold=True))

    # зона компромісу посередині
    xmid = X(30)
    f.append(line(xmid, oy, xmid, oy - ax_h, color=FIELD, sw=1.6, dash="6 4"))
    b, _, _ = textbox(xmid, oy - ax_h + 40,
                      "компроміс:\nдосить малий Q,\nще прийнятний Iq",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "rg-tradeoff.svg"), W, H, *f)


# ── 9. Класифікація аварії за виміром напруги (proj-вставка) ──────────────────
def fig_fault_classes():
    W, H = 760, 470
    f = [text(W / 2, 26, "Одне число — напруга на шині — розводить три класи аварії",
              size=15.5, bold=True)]

    # верхній вузол: вимір
    top = fitbox(W / 2 - 150, 46, 300, 46,
                 "вимір: V_шини (дільник + АЦП),\nусереднено, з гістерезисом",
                 size=12, fill="#eef3fb", stroke=NEG, bold=True)
    f.append(top)

    # три гілки-питання → три класи
    ynode = 150
    xs = [150, 380, 610]
    conds = [
        "V ≈ Vвх − 0.7 В\n(на діод-падіння нижче)",
        "V ≈ 0 В\n(шина мертва)",
        "V помітно нижча,\nале не нуль",
    ]
    classes = [
        ("НЕДОВІДКРИТТЯ FET", "струм тече крізь\nbody-діод, не канал", POS),
        ("ЗАПОБІЖНИК/ОБРИВ", "коло розірване,\nживлення знято", "#8e44ad"),
        ("ПРОСАД (sag)", "перевантаження чи\nслабке джерело", "#b8860b"),
    ]
    # лінії від вузла-виміру до кожної гілки
    for x in xs:
        f.append(line(W / 2, 92, x, ynode - 4, color=MUTED, sw=1.6))
    for x, cond, (name, why, col) in zip(xs, conds, classes):
        f.append(fitbox(x - 105, ynode, 210, 48, cond, size=11, fill=BG, stroke=MUTED))
        f.append(arrow(x, ynode + 52, x, ynode + 86, color=col, sw=2))
        f.append(fitbox(x - 105, ynode + 90, 210, 44, name, size=12.5,
                        fill=FILL, stroke=col, bold=True, color=col))
        f.append(fitbox(x - 105, ynode + 138, 210, 42, why, size=10.5,
                        fill=BG, stroke=col))
        # реакція
        f.append(arrow(x, ynode + 182, x, ynode + 210, color=INK, sw=1.8))

    react = fitbox(W / 2 - 330, ynode + 214, 660, 56,
                   "РЕАКЦІЯ (спільна для всіх класів): зберегти стан у NVM ·\n"
                   "зняти навантаження (розімкнути ключ) · підняти прапорець аварії",
                   size=12, fill="#eef6ef", stroke=FIELD, bold=True)
    f.append(react)
    render(os.path.join(IMG, "fault-classes.svg"), W, H, *f)


# ── 10. Безпечне підключення АЦП до «брудного» незахищеного входу (proj) ──────
def fig_adc_guard():
    W, H = 760, 420
    f = [text(W / 2, 26, "АЦП на брудному вході: резистор бере на себе струм крізь захисні діоди",
              size=14.5, bold=True)]

    # зовнішній «брудний» вузол ліворуч
    nx = 70
    f.append(fitbox(nx - 42, 150, 120, 60, "брудний вхід\n(може бути\n< 0 В або > Vdd)",
                    size=10.5, fill="#fbeee6", stroke=POS, bold=True))
    # послідовний резистор
    rx1 = nx + 110
    f.append(line(nx + 78, 180, rx1, 180, color=LINE, sw=2))
    f.append(rect(rx1, 168, 70, 24, fill=FILL, stroke=INK, sw=1.8, rx=4))
    f.append(text(rx1 + 35, 185, "Rпосл", size=12, bold=True))
    f.append(text(rx1 + 35, 156, "10–100 кОм", size=10.5, color=MUTED))
    node = rx1 + 70
    f.append(line(node, 180, node + 150, 180, color=LINE, sw=2))

    # межа кристала МК
    chipx = node + 150
    f.append(rect(chipx, 70, 250, 250, fill="#f2f5fa", stroke=NEG, sw=1.8, rx=10))
    f.append(text(chipx + 125, 92, "усередині МК (вивід АЦП)", size=11.5, bold=True, color=NEG))
    # шина Vdd і GND усередині
    vdd_y, gnd_y = 120, 300
    f.append(line(chipx + 30, vdd_y, chipx + 220, vdd_y, color=POS, sw=2))
    f.append(text(chipx + 235, vdd_y + 4, "Vdd", size=11, bold=True, color=POS, anchor="start"))
    f.append(line(chipx + 30, gnd_y, chipx + 220, gnd_y, color=NEG, sw=2))
    f.append(text(chipx + 232, gnd_y + 4, "GND", size=11, bold=True, color=NEG, anchor="start"))

    # вузол виводу всередині
    pin = chipx + 120
    f.append(line(chipx, 180, pin, 180, color=LINE, sw=2))
    f.append(circle(pin, 180, 4, fill=INK, stroke=INK))
    f.append(text(pin, 210, "до ядра АЦП", size=10.5, color=MUTED))

    # два захисні діоди (вгору до Vdd, вниз до GND)
    f.append(diode_symbol(pin - 22, (vdd_y + 180) / 2, w=44, color=POS, flip=True))
    f.append(line(pin, 180, pin, (vdd_y + 180) / 2 + 9, color=LINE, sw=1.8))
    f.append(line(pin, (vdd_y + 180) / 2 - 9, pin, vdd_y, color=LINE, sw=1.8))
    f.append(diode_symbol(pin - 22, (gnd_y + 180) / 2, w=44, color=NEG))
    f.append(line(pin, 180, pin, (gnd_y + 180) / 2 - 9, color=LINE, sw=1.8))
    f.append(line(pin, (gnd_y + 180) / 2 + 9, pin, gnd_y, color=LINE, sw=1.8))

    # пояснювальна рамка знизу
    f.append(fitbox(W / 2 - 300, 350, 600, 52,
                    "Від'ємна напруга відкриває нижній діод: без Rпосл крізь нього тече весь струм джерела → вивід гине.\n"
                    "Rпосл обмежує цей струм: I = (Vвх − Vфікс) / Rпосл ≤ безпечні одиниці мА.",
                    size=11, fill="#fff8e1", stroke="#b8860b"))
    render(os.path.join(IMG, "adc-guard.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_kills()
    fig_three_methods()
    fig_fuse_clamp()
    fig_drop_vs_current()
    fig_pmos_anatomy()
    fig_crowbar_it()
    fig_reverse_spike()
    fig_rg_tradeoff()
    fig_fault_classes()
    fig_adc_guard()
    print("OK: 10 figures ->", IMG)
