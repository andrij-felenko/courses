# -*- coding: utf-8 -*-
"""Фігури для теми rcd-snubber (RCD-снабер для flyback).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5). Вивід у ./img/.

    python figs.py
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *  # noqa: E402,F403

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

GOLD = "#b8860b"   # осердя / магнітне
CLAMP = "#1e8449"  # рівень фіксації (зелений, безпечний)


# ── Фігура 1: напруга на стоку — пік витоку проти плато V_clamp ──────────────
def fig_spike():
    """Осцилограма напруги на стоку: базовий рівень V_in+V_r, гострий пік
    витоку за BV_DSS (без снабера) і плато V_clamp під межею (зі снабером)."""
    W, H = 900, 470
    # осі
    ox, oy = 90, 400          # початок координат
    axr, axt = W - 40, 70     # праві/верхні межі
    f = []

    # рівні як "значення напруги" в px (більше = вища напруга):
    # V_in+V_r < V_clamp < BV_DSS < пік. Екранна y = oy − значення.
    y0 = oy                    # 0 В
    y_lvl = 190                # V_in+V_r (найнижчий із трьох рівнів)
    y_clamp = 250              # V_clamp — безпечно НИЖЧЕ за межу
    y_bvdss = 300              # BV_DSS
    y_peak = 330               # верхівка неприборканого піку (за BV_DSS)

    yy_lvl = oy - y_lvl
    yy_clamp = oy - y_clamp
    yy_bvdss = oy - y_bvdss
    yy_peak = oy - y_peak

    # координата вимикання ключа
    xsw = 300

    # осі
    f.append(arrow(ox, oy, ox, axt, color=INK, sw=2))          # вертикальна (U)
    f.append(arrow(ox, oy, axr, oy, color=INK, sw=2))          # горизонтальна (t)
    f.append(text(ox - 14, axt + 4, "U(стік)", size=13, color=INK, anchor="end", bold=True))
    f.append(text(axr - 4, oy + 22, "час", size=13, color=INK, anchor="end"))

    # межа BV_DSS (пунктир, червона) — напис ЛІВОРУЧ від осі, поза графіком
    f.append(line(ox, yy_bvdss, axr, yy_bvdss, color=POS, sw=1.8, dash="9 6"))
    f.append(text(axr - 6, yy_bvdss - 8, "BV_DSS — межа ключа", size=13, color=POS, anchor="end", bold=True))

    # рівень V_clamp (пунктир, зелений)
    f.append(line(xsw, yy_clamp, axr, yy_clamp, color=CLAMP, sw=1.8, dash="9 6"))
    f.append(text(axr - 6, yy_clamp - 8, "V_clamp (плато зі снабером)", size=13, color=CLAMP, anchor="end", bold=True))

    # рівень V_in+V_r (тонкий сірий пунктир)
    f.append(line(ox, yy_lvl, axr, yy_lvl, color=MUTED, sw=1.3, dash="4 5"))
    f.append(text(ox + 8, yy_lvl + 18, "V_in + V_r", size=12, color=MUTED, anchor="start"))

    # ── криві до вимикання: стік унизу (ключ відкритий) ──
    pre = "M %.1f %.1f L %.1f %.1f " % (ox + 6, y0 - 6, xsw, y0 - 6)

    # ── БЕЗ снабера (червона): різкий пік за BV_DSS, потім дзвін, осідання на рівень ──
    d_no = "M %.1f %.1f " % (xsw, y0 - 6)
    d_no += "L %.1f %.1f " % (xsw + 14, yy_peak)                 # злітає в пік
    d_no += "C %.1f %.1f %.1f %.1f %.1f %.1f " % (xsw + 40, yy_lvl - 40, xsw + 60, yy_lvl + 30, xsw + 80, yy_lvl - 10)  # дзвін
    d_no += "C %.1f %.1f %.1f %.1f %.1f %.1f " % (xsw + 100, yy_lvl - 25, xsw + 120, yy_lvl + 8, xsw + 150, yy_lvl)      # затухання
    d_no += "L %.1f %.1f " % (485, yy_lvl)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pre, INK))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d_no, POS))

    # ── ЗІ снабером (зелена): підлітає лише до V_clamp, тримає плато, спадає на рівень ──
    d_yes = "M %.1f %.1f " % (xsw, y0 - 6)
    d_yes += "L %.1f %.1f " % (xsw + 16, yy_clamp)               # підлітає до плато
    d_yes += "L %.1f %.1f " % (xsw + 150, yy_clamp)              # тримає плато
    d_yes += "L %.1f %.1f " % (xsw + 175, yy_lvl)                # спадає на рівень
    d_yes += "L %.1f %.1f " % (485, yy_lvl)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="1 0"/>' % (d_yes, CLAMP))

    # позначка миті вимикання (вертикальна тонка, лише до рівня плато) — напис ПІД віссю
    f.append(line(xsw, oy + 4, xsw, yy_lvl, color=MUTED, sw=1.1, dash="3 4"))
    f.append(text(xsw, oy + 22, "ключ вимкнувся", size=12, color=MUTED, anchor="middle"))

    # підпис піку — у відкритій зоні праворуч-нижче, поза кривими й рівневими написами
    b, w, h = textbox(645, 305, "пік витоку без снабера:\nвиліт за BV_DSS → пробій ключа",
                      size=13, fill="#fdecea", stroke=POS, sw=1.6, color=POS)
    f.append(b)
    # підпис зеленого плато — у відкритій зоні праворуч, нижче за плато
    b2, w2, h2 = textbox(645, 360, "зі снабером: стік тримається\nна V_clamp, ключ живий",
                         size=13, fill="#e9f7ef", stroke=CLAMP, sw=1.6, color=CLAMP)
    f.append(b2)

    render(os.path.join(IMG, "spike.svg"), W, H, *f)


# ── Фігура 2: схема RCD-снабера й шлях струму витоку ─────────────────────────
def _coil(x, y_top, y_bot, n=4, r=10):
    """Вертикальна обмотка як ланцюжок півдуг."""
    step = (y_bot - y_top) / n
    d = "M %.1f %.1f " % (x, y_top)
    yy = y_top
    for _ in range(n):
        d += "A %.1f %.1f 0 0 1 %.1f %.1f " % (r, step / 2, x, yy + step)
        yy += step
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, GOLD)


def fig_circuit():
    """Первинна обмотка + ключ; RCD-ланка (D-C-R) від шини V_in до стоку;
    червоний шлях струму витоку крізь діод у конденсатор при вимиканні."""
    W, H = 900, 480
    f = []

    # вузли
    x_rail = 150          # вертикаль первинної/обмотки
    y_top = 90            # верхня шина V_in
    y_drain = 300         # вузол стоку
    y_bot = 430           # нижня шина (земля первинної)
    x_snub = 470          # вертикаль RCD-ланки
    x_gnd = x_rail

    # верхня шина V_in
    f.append(line(90, y_top, x_snub, y_top, color=INK, sw=2.4))
    b, w, h = textbox(90, y_top, "V_in", size=13, fill="#ffffff", stroke=INK, sw=1.8)
    f.append(b)

    # первинна обмотка (від шини до стоку)
    f.append(line(x_rail, y_top, x_rail, 150, color=INK, sw=2))
    f.append(_coil(x_rail, 150, y_drain - 20, n=4, r=11))
    f.append(line(x_rail, y_drain - 20, x_rail, y_drain, color=INK, sw=2))
    f.append(text(x_rail - 34, 225, "первинна", size=13, color=GOLD, anchor="end", bold=True))
    f.append(text(x_rail - 34, 244, "L_lk у ній", size=12, color=POS, anchor="end"))

    # вузол стоку
    f.append(circle(x_rail, y_drain, 4, fill=INK, stroke=INK))
    f.append(text(x_rail + 14, y_drain - 8, "стік", size=13, color=INK, anchor="start", bold=True))

    # ключ MOSFET (спрощено: прямокутник) від стоку до землі
    f.append(line(x_rail, y_drain, x_rail, 360, color=INK, sw=2))
    b, w, h = textbox(x_rail, 385, "ключ", size=13, fill=FILL, stroke=INK, sw=1.8, min_w=70)
    f.append(b)
    f.append(line(x_rail, 385 + h / 2, x_rail, y_bot, color=INK, sw=2))

    # нижня шина (земля)
    f.append(line(x_rail, y_bot, x_snub, y_bot, color=INK, sw=2.4))
    # символ землі
    gy = y_bot
    f.append(line(x_gnd - 16, gy + 12, x_gnd + 16, gy + 12, color=INK, sw=2))
    f.append(line(x_gnd - 10, gy + 18, x_gnd + 10, gy + 18, color=INK, sw=2))
    f.append(line(x_gnd - 5, gy + 24, x_gnd + 5, gy + 24, color=INK, sw=2))
    f.append(line(x_rail, y_bot, x_rail, gy + 12, color=INK, sw=2))

    # ── RCD-ланка від верхньої шини (V_in) до стоку ──
    # діод: від стоку вгору до вузла C||R  (провідність від стоку в снабер)
    yd1 = y_drain           # низ (стік)
    yd2 = 235               # верх діода
    f.append(line(x_snub, y_top, x_snub, 150, color=INK, sw=2))   # від шини вниз

    # C та R паралельно між шиною(зверху, 150) і вузлом діода(yd2)
    xC = x_snub - 34
    xR = x_snub + 34
    ynode_top = 150
    ynode_bot = yd2
    f.append(line(x_snub, ynode_top, xC, ynode_top, color=INK, sw=2))
    f.append(line(x_snub, ynode_top, xR, ynode_top, color=INK, sw=2))
    f.append(line(x_snub, ynode_bot, xC, ynode_bot, color=INK, sw=2))
    f.append(line(x_snub, ynode_bot, xR, ynode_bot, color=INK, sw=2))
    f.append(circle(x_snub, ynode_top, 3.5, fill=INK, stroke=INK))
    f.append(circle(x_snub, ynode_bot, 3.5, fill=INK, stroke=INK))

    # конденсатор C (дві пластини)
    cy = (ynode_top + ynode_bot) / 2
    f.append(line(xC, ynode_top, xC, cy - 8, color=INK, sw=2))
    f.append(line(xC - 15, cy - 8, xC + 15, cy - 8, color=INK, sw=2.4))
    f.append(line(xC - 15, cy + 8, xC + 15, cy + 8, color=INK, sw=2.4))
    f.append(line(xC, cy + 8, xC, ynode_bot, color=INK, sw=2))
    f.append(text(xC - 22, cy + 4, "C", size=15, color=INK, anchor="end", bold=True))

    # резистор R (прямокутник)
    f.append(line(xR, ynode_top, xR, cy - 22, color=INK, sw=2))
    f.append(rect(xR - 11, cy - 22, 22, 44, fill="#ffffff", stroke=INK, sw=2, rx=3))
    f.append(line(xR, cy + 22, xR, ynode_bot, color=INK, sw=2))
    f.append(text(xR + 22, cy + 4, "R", size=15, color=INK, anchor="start", bold=True))

    # діод D (трикутник вниз-до-стоку: пропускає струм зі стоку вгору у вузол)
    dy_mid = (ynode_bot + yd1) / 2
    f.append(line(x_snub, ynode_bot, x_snub, dy_mid + 12, color=INK, sw=2))
    # трикутник вершиною ВГОРУ (анод унизу=стік, катод угорі): струм стік→вузол
    tri = "M %.1f %.1f L %.1f %.1f L %.1f %.1f z" % (
        x_snub - 11, dy_mid + 12, x_snub + 11, dy_mid + 12, x_snub, dy_mid - 6)
    f.append('<path d="%s" fill="#ffffff" stroke="%s" stroke-width="2"/>' % (tri, INK))
    f.append(line(x_snub - 12, dy_mid - 6, x_snub + 12, dy_mid - 6, color=INK, sw=2.4))  # катодна риска
    f.append(line(x_snub, dy_mid - 6, x_snub, yd1, color=INK, sw=2))
    f.append(line(x_snub, yd1, x_rail, yd1, color=INK, sw=2))          # від діода до стоку
    f.append(circle(x_rail, yd1, 4, fill=INK, stroke=INK))
    f.append(text(x_snub + 18, dy_mid + 4, "D", size=15, color=INK, anchor="start", bold=True))

    # заголовок ланки
    b, w, h = textbox(x_snub, 60, "RCD-снабер", size=14, fill="#e9f7ef", stroke=CLAMP, sw=1.8, color=CLAMP, bold=True)
    f.append(b)

    # ── червоний шлях струму витоку: стік → діод → у конденсатор ──
    # від вузла стоку праворуч по нижньому дроту, крізь діод угору
    f.append(arrow(x_rail + 40, yd1, x_snub - 16, yd1, color=POS, sw=2.6))
    f.append(arrow(x_snub, dy_mid + 14, x_snub, ynode_bot + 6, color=POS, sw=2.6))
    f.append(text(x_snub + 60, dy_mid + 40, "струм витоку", size=13, color=POS, anchor="start", bold=True))
    f.append(text(x_snub + 60, dy_mid + 58, "→ у конденсатор", size=12, color=POS, anchor="start"))

    render(os.path.join(IMG, "circuit.svg"), W, H, *f)


# ── Фігура 3: компроміс V_clamp — потужність резистора проти запасу ключа ────
def fig_tradeoff():
    """Робоче вікно V_clamp між V_r (знизу) і BV_DSS−запас (згори); крива
    розсіюваної потужності: низько → пече, високо → холодний, але без запасу."""
    W, H = 900, 470
    f = []
    ox, oy = 110, 390
    axr, axt = W - 60, 80

    # осі: X = V_clamp, Y = потужність резистора
    f.append(arrow(ox, oy, ox, axt, color=INK, sw=2))
    f.append(arrow(ox, oy, axr, oy, color=INK, sw=2))
    f.append(text(ox - 16, axt + 2, "P у резисторі", size=13, color=INK, anchor="end", bold=True))
    f.append(text(axr - 4, oy + 24, "V_clamp →", size=13, color=INK, anchor="end"))

    # позиції ключових вертикалей по X
    x_vr = 250            # V_r (нижня стіна)
    x_opt = 470           # ~2·V_r (розумний вибір)
    x_ceil = 720          # BV_DSS − запас (верхня стіна)

    # заборонені зони (ліворуч від V_r та праворуч від стелі) — легка заливка
    f.append(rect(ox + 2, axt, x_vr - ox - 2, oy - axt, fill="#fdecea", stroke="none"))
    f.append(rect(x_ceil, axt, axr - x_ceil - 2, oy - axt, fill="#fdecea", stroke="none"))

    # межі (пунктир) з написами ЗВЕРХУ, поза кривою
    f.append(line(x_vr, oy, x_vr, axt, color=POS, sw=1.8, dash="8 6"))
    f.append(text(x_vr, axt - 10, "V_r — нижче не можна", size=13, color=POS, anchor="middle", bold=True))
    f.append(line(x_ceil, oy, x_ceil, axt, color=POS, sw=1.8, dash="8 6"))
    f.append(text(x_ceil, axt - 10, "BV_DSS − запас", size=13, color=POS, anchor="middle", bold=True))

    # крива P(V_clamp) = V_clamp²/R, R ~ (V_clamp−V_r): P росте біля V_r, спадає далі
    # намалюємо гіперболо-подібну спадну від V_r до стелі
    import math
    pts = []
    for i in range(0, 101):
        vx = x_vr + (x_ceil - x_vr) * i / 100.0
        # модель форми: висока біля x_vr, спадна далі (для наочності)
        d = (vx - x_vr) / (x_ceil - x_vr)     # 0..1
        p = 1.0 / (0.12 + d * 1.6)            # спадна крива
        yv = oy - 40 - p * 70
        pts.append((vx, yv))
    dcurve = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % pt for pt in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (dcurve, INK))

    # точка розумного вибору
    d_opt = (x_opt - x_vr) / (x_ceil - x_vr)
    p_opt = 1.0 / (0.12 + d_opt * 1.6)
    y_opt = oy - 40 - p_opt * 70
    f.append(line(x_opt, oy, x_opt, y_opt, color=CLAMP, sw=1.6, dash="4 5"))
    f.append(circle(x_opt, y_opt, 6, fill=CLAMP, stroke=CLAMP))
    b, w, h = textbox(x_opt, axt + 40, "≈ 2·V_r\nрозумний вибір",
                      size=13, fill="#e9f7ef", stroke=CLAMP, sw=1.6, color=CLAMP, bold=True)
    f.append(b)

    # підписи країв кривої (у своїх рамках, поза лінією)
    b, w, h = textbox(x_vr + 78, oy - 150, "низько:\nпече резистор",
                      size=12, fill="#fdecea", stroke=POS, sw=1.4, color=POS)
    f.append(b)
    b, w, h = textbox(x_ceil - 92, oy - 70, "високо: холодно,\nта запас ключа зник",
                      size=12, fill="#fdecea", stroke=POS, sw=1.4, color=POS)
    f.append(b)

    render(os.path.join(IMG, "tradeoff.svg"), W, H, *f)


if __name__ == "__main__":
    fig_spike()
    fig_circuit()
    fig_tradeoff()
    print("OK: spike.svg, circuit.svg, tradeoff.svg")
