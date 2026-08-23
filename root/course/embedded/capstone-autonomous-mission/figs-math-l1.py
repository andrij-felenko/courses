# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Геометрія L1: відхилення + швидкість → кут η → бічне прискорення ───────
def fig_l1_geometry():
    W, H = 940, 470
    p = []
    p.append(text(W / 2, 28, "з відхилення d і швидкості V народжується кут η, а з нього — бічне прискорення",
                  size=13, color=MUTED))

    # цільова лінія маршруту (пряма A→B), горизонтальна
    path_y = 330
    ax, bx = 90, 720
    p.append(line(ax, path_y, bx, path_y, color=FIELD, sw=3))
    p.append(text(ax - 8, path_y + 5, "A", size=14, color=FIELD, anchor="end", bold=True))
    p.append(text(bx + 12, path_y + 5, "B", size=14, color=FIELD, anchor="start", bold=True))
    p.append(text(300, path_y + 26, "бажана лінія маршруту", size=12, color=FIELD))

    # апарат — над лінією (відхилення d вгору = вниз по екрану менше y)
    vx, vy = 240, 200          # позиція апарата
    p.append(circle(vx, vy, 9, fill="#eaf3ff", stroke=NEG, sw=2.4))
    p.append(text(vx, vy - 18, "апарат", size=12, color=NEG, bold=True, anchor="middle"))

    # відхилення d — перпендикуляр від апарата до лінії
    p.append(line(vx, vy, vx, path_y, color=POS, sw=1.8, dash="5,4"))
    p.append(text(vx - 12, (vy + path_y) / 2, "d", size=15, color=POS, bold=True, anchor="end"))
    p.append(text(vx - 12, (vy + path_y) / 2 + 20, "(crosstrack)", size=11, color=POS, anchor="end"))

    # вектор швидкості V — під невеликим кутом до лінії (апарат летить майже вздовж, трохи «в лінію»)
    import math as _m
    vlen = 150
    vdir = _m.radians(18)      # кут курсу відносно лінії
    vex = vx + vlen * _m.cos(vdir)
    vey = vy + vlen * _m.sin(vdir)
    p.append(arrow(vx, vy, vex, vey, color=NEG, sw=2.6))
    p.append(text(vex + 8, vey + 4, "V", size=15, color=NEG, bold=True, anchor="start"))

    # опорна точка L1_ref — на лінії, попереду на дузі радіуса L1 від апарата
    # для наочності: точка на лінії маршруту попереду
    refx = 520
    refy = path_y
    p.append(circle(refx, refy, 7, fill="#fff6e6", stroke="#d98218", sw=2.2))
    p.append(text(refx, refy - 16, "L1_ref", size=12.5, color="#b56c12", bold=True))
    p.append(text(refx + 12, refy + 20, "ціль попереду на лінії", size=11, color="#b56c12", anchor="start"))

    # відрізок L1 — від апарата до опорної точки
    p.append(line(vx, vy, refx, refy, color=INK, sw=2))
    lmx, lmy = (vx + refx) / 2, (vy + refy) / 2
    p.append(text(lmx + 6, lmy - 8, "L1", size=15, color=INK, bold=True, anchor="start"))

    # кут η — між V і відрізком L1 (біля апарата)
    # намалюємо дугу між напрямком V і напрямком на ref
    r_arc = 46
    ang_v = _m.atan2(vey - vy, vex - vx)
    ang_l = _m.atan2(refy - vy, refx - vx)
    a0, a1 = sorted([ang_v, ang_l])
    arc_pts = []
    steps = 24
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps
        arc_pts.append("%.1f,%.1f" % (vx + r_arc * _m.cos(a), vy + r_arc * _m.sin(a)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (" ".join(arc_pts), POS))
    amid = (a0 + a1) / 2
    p.append(text(vx + (r_arc + 16) * _m.cos(amid), vy + (r_arc + 16) * _m.sin(amid) + 4,
                  "η", size=17, color=POS, bold=True))

    # вектор бічного прискорення a_cmd — перпендикуляр до V, «вниз до лінії»
    # напрям: повернути V на -90° (у бік лінії)
    perp = ang_v + _m.radians(90)
    aclen = 92
    acx = vx + aclen * _m.cos(perp)
    acy = vy + aclen * _m.sin(perp)
    p.append(arrow(vx, vy, acx, acy, color="#8e44ad", sw=2.8))
    p.append(text(acx - 12, acy + 6, "a_cmd", size=14, color="#8e44ad", bold=True, anchor="end"))
    p.append(text(acx - 12, acy + 24, "тягне до лінії", size=11, color="#8e44ad", anchor="end"))

    # формула-плашка внизу
    b, bw, bh = textbox(W / 2, 430,
                        "a_cmd = 2 · V² / L1 · sin η        (Park, Deyst, How, 2004)",
                        size=15, pad=12, fill="#faf6ff", stroke="#8e44ad", color=INK, bold=True)
    p.append(b)
    return render(os.path.join(OUT, "l1-geometry.svg"), W, H, *p)


# ── 2. Кут η = геометрія + гасіння швидкості; L1 = (1/π)·ζ·T·V ───────────────
def fig_eta_decomposition():
    W, H = 940, 500
    p = []
    p.append(text(W / 2, 28, "команду формують ДВА доданки: куди летіти (η₁) і як гасити зближення (η₂)",
                  size=13, color=MUTED))

    # ліва половина: η1 — геометричний доданок (тягне до опорної точки)
    lx = 250
    # права половина: η2 — доданок гасіння (протидіє швидкості зближення)
    rx = 690

    # --- η1 ---
    p.append(rect(40, 60, 420, 250, fill="#faf6ff", stroke="#8e44ad", sw=1.6, rx=10))
    p.append(text(250, 86, "η₁ — геометрія: «де ціль»", size=14, color="#8e44ad", bold=True))
    # маленька сцена: апарат, ціль, кут
    import math as _m
    ox, oy = 150, 220
    p.append(circle(ox, oy, 8, fill="#eaf3ff", stroke=NEG, sw=2.2))
    p.append(arrow(ox, oy, ox + 130, oy - 8, color=NEG, sw=2.2))      # V
    p.append(text(ox + 134, oy - 8, "V", size=13, color=NEG, bold=True, anchor="start"))
    p.append(arrow(ox, oy, ox + 120, oy + 55, color="#8e44ad", sw=2.2))  # на ціль
    p.append(circle(ox + 120, oy + 55, 6, fill="#fff6e6", stroke="#d98218", sw=2))
    p.append(text(ox + 128, oy + 60, "L1_ref", size=11.5, color="#b56c12", anchor="start"))
    p.append(text(ox + 62, oy + 6, "η₁", size=15, color="#8e44ad", bold=True))
    p.append(fitbox(60, 262, 380, 38,
                    "η₁ = asin(відхилення / L1) — кут між швидкістю й напрямом на опорну точку",
                    size=12, pad=6, fill=BG, stroke="none", color=INK))

    # --- η2 ---
    p.append(rect(480, 60, 420, 250, fill="#eef7ee", stroke=FIELD, sw=1.6, rx=10))
    p.append(text(690, 86, "η₂ — гасіння: «як швидко зближаюсь»", size=13.5, color="#1e7d42", bold=True))
    ox2, oy2 = 590, 210
    # лінія маршруту
    p.append(line(540, 250, 850, 250, color=FIELD, sw=2.5))
    p.append(circle(ox2, oy2, 8, fill="#eaf3ff", stroke=NEG, sw=2.2))
    # складові швидкості: вздовж (ltrackVel) і впоперек (xtrackVel)
    p.append(arrow(ox2, oy2, ox2 + 110, oy2, color=MUTED, sw=2))       # вздовж
    p.append(text(ox2 + 114, oy2 - 6, "V∥", size=12, color=MUTED, anchor="start"))
    p.append(arrow(ox2, oy2, ox2, oy2 + 40, color=POS, sw=2.4))        # впоперек (до лінії)
    p.append(text(ox2 - 8, oy2 + 30, "V⊥", size=12, color=POS, anchor="end", bold=True))
    p.append(fitbox(500, 262, 380, 38,
                    "η₂ = atan2(V⊥, V∥) — реагує на ШВИДКІСТЬ зближення, а не лише на відстань",
                    size=12, pad=6, fill=BG, stroke="none", color=INK))

    # сума
    b, bw, bh = textbox(W / 2, 350, "η = η₁ + η₂        →        a_cmd = 2·V²/L1 · sin η",
                        size=15, pad=12, fill=FILL, stroke=INK, color=INK, bold=True)
    p.append(b)

    # довжина огляду L1
    p.append(text(W / 2, 400, "довжина огляду масштабується зі швидкістю — тому «період» петлі сталий:",
                  size=12.5, color=MUTED))
    b2, bw2, bh2 = textbox(W / 2, 445,
                           "L1 = (1/π) · ζ · T · V        ζ = NAVL1_DAMPING,  T = NAVL1_PERIOD",
                           size=15, pad=12, fill="#eaf3ff", stroke=NEG, color=INK, bold=True)
    p.append(b2)
    return render(os.path.join(OUT, "l1-eta-decomposition.svg"), W, H, *p)


# ── 3. Замалий період → розгойдування; віраж R = V²/(g·tan φ) ────────────────
def fig_period_and_turn():
    W, H = 940, 500
    p = []
    p.append(text(W / 2, 28, "замалий період T → коротка L1 → апарат «нишпорить»; віраж задає крен φ",
                  size=13, color=MUTED))

    import math as _m
    # ── ліворуч: дві траєкторії підходу до лінії ──
    p.append(text(250, 66, "підхід до лінії маршруту", size=13, color=INK, bold=True))
    ly = 150
    x0, x1 = 60, 470
    p.append(line(x0, ly, x1, ly, color=FIELD, sw=3))
    p.append(text(x1 + 6, ly + 5, "лінія", size=11.5, color=FIELD, anchor="start"))

    # плавна траєкторія (адекватний період) — гладко лягає на лінію
    pts_good = []
    for i in range(61):
        t = i / 60
        x = x0 + (x1 - x0) * t
        # експоненційний підхід згори
        y = ly - 70 * _m.exp(-3.2 * t)
        pts_good.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts_good), NEG))
    p.append(text(x0 + 150, ly - 66, "T достатній: гладко лягає", size=11.5, color=NEG, bold=True, anchor="start"))

    # розгойдана траєкторія (замалий період) — згасаючий синус навколо лінії
    pts_bad = []
    for i in range(81):
        t = i / 80
        x = x0 + (x1 - x0) * t
        y = ly - 62 * _m.exp(-1.1 * t) * _m.cos(9.0 * t)
        pts_bad.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="6,4"/>' % (" ".join(pts_bad), POS))
    p.append(text(x0 + 120, ly + 60, "T замалий: перелітає й нишпорить", size=11.5, color=POS, bold=True, anchor="start"))

    # ── праворуч: віраж — вид згори + переріз крена ──
    cxr = 720
    p.append(text(cxr, 66, "координований віраж", size=13, color=INK, bold=True))
    # коло радіуса R (вид згори)
    Rr = 95
    ccx, ccy = cxr, 190
    p.append(circle(ccx, ccy, Rr, fill="none", stroke=MUTED, sw=1.6))
    p.append(circle(ccx, ccy, 3, fill=INK, stroke=INK))
    p.append(line(ccx, ccy, ccx + Rr, ccy, color=INK, sw=1.6, dash="4,3"))
    p.append(text(ccx + Rr / 2, ccy - 8, "R", size=15, color=INK, bold=True))
    # апарат на колі + вектор швидкості (по дотичній) + прискорення (до центру)
    ang = _m.radians(-35)
    pxx = ccx + Rr * _m.cos(ang)
    pyy = ccy + Rr * _m.sin(ang)
    p.append(circle(pxx, pyy, 7, fill="#eaf3ff", stroke=NEG, sw=2.2))
    # дотична (V)
    tang = ang + _m.radians(90)
    p.append(arrow(pxx, pyy, pxx + 55 * _m.cos(tang), pyy + 55 * _m.sin(tang), color=NEG, sw=2.2))
    p.append(text(pxx + 58 * _m.cos(tang), pyy + 55 * _m.sin(tang), "V", size=13, color=NEG, bold=True, anchor="start"))
    # доцентрове a
    p.append(arrow(pxx, pyy, pxx + 0.55 * (ccx - pxx), pyy + 0.55 * (ccy - pyy), color="#8e44ad", sw=2.4))
    p.append(text((pxx + ccx) / 2 - 4, (pyy + ccy) / 2 - 6, "a", size=13, color="#8e44ad", bold=True, anchor="end"))

    # формули-плашки внизу праворуч
    b, bw, bh = textbox(cxr, 330, "a = V² / R = g · tan φ", size=15, pad=11,
                        fill="#faf6ff", stroke="#8e44ad", color=INK, bold=True)
    p.append(b)
    b2, bw2, bh2 = textbox(cxr, 378, "R = V² / (g · tan φ)", size=15, pad=11,
                           fill=FILL, stroke=INK, color=INK, bold=True)
    p.append(b2)

    # нижній підсумок на всю ширину
    b3, bw3, bh3 = textbox(W / 2, 455,
                           "коротша L1 → крутіший поворот на те саме відхилення → перебір і коливання;\nдовша L1 → м'якший, але млявіший підхід. Період T налаштовує саме цей компроміс.",
                           size=12.5, pad=12, fill="#f7faf7", stroke=FIELD, color=INK)
    p.append(b3)
    return render(os.path.join(OUT, "l1-period-turn.svg"), W, H, *p)


if __name__ == "__main__":
    fig_l1_geometry()
    fig_eta_decomposition()
    fig_period_and_turn()
    print("ok")
