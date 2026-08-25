# -*- coding: utf-8 -*-
"""Фігури до теми «Здоров'я батареї (SoH)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

CHARGE = "#dbe6fb"   # заливка «заряду» в баку (світло-синя)


# ── Заряд vs здоров'я: рівень у баку і розмір бака ────────────────────────────
def fig_soc_vs_soh():
    W, H = 840, 480
    f = [text(W / 2, 30, "Заряд vs здоров'я: рівень у баку і розмір бака", size=16, bold=True)]

    bw, bh = 120, 250
    ty = 96
    by = ty + bh                      # низ баків

    # ── Новий бак (ліворуч) ──────────────────────────────────────────────────
    x1 = 150
    f.append(text(x1 + bw / 2, ty - 18, "НОВА", size=13, bold=True, color=FIELD))
    # повна заливка = SoC 100%
    f.append(rect(x1, ty, bw, bh, fill=CHARGE, stroke="none", sw=0))
    f.append(rect(x1, ty, bw, bh, fill="none", stroke=INK, sw=1.8))
    f.append(text(x1 + bw / 2, ty + bh / 2, "заряд", size=11, color=NEG, bold=True))
    f.append(text(x1 + bw / 2, ty + bh / 2 + 18, "100%", size=11, color=NEG))
    f.append(text(x1 + bw / 2, by + 22, "SoH = 100%", size=12, bold=True, color=FIELD))
    f.append(text(x1 + bw / 2, by + 40, "повна → SoC 100%", size=10.5, color=MUTED))
    # двобічна стрілка «рівень ходить» ліворуч від бака
    ax = x1 - 26
    f.append(arrow(ax, ty + 8, ax, by - 8, color=NEG, sw=1.8))
    f.append(arrow(ax, by - 8, ax, ty + 8, color=NEG, sw=1.8))
    f.append(text(ax - 8, (ty + by) / 2, "рівень (SoC)", size=10, color=NEG,
                  anchor="middle", bold=True))
    f.append('<g transform="rotate(-90 %.1f %.1f)"></g>' % (ax - 8, (ty + by) / 2))

    # ── Стара комірка (праворуч) ─────────────────────────────────────────────
    x2 = 560
    lost = bh * 0.20                  # втрачена верхівка (−20% SoH)
    line80 = ty + lost                # рівень «нова повна» = 80% тут
    f.append(text(x2 + bw / 2, ty - 18, "СТАРА (2 роки)", size=13, bold=True, color=POS))
    # оригінальний контур (пунктир) — паспортна ємність
    f.append(rect(x2, ty, bw, bh, fill="none", stroke=MUTED, sw=1.4, rx=6))
    # втрачена верхівка
    f.append(rect(x2, ty, bw, lost, fill="#efe1de", stroke="none", sw=0))
    f.append(text(x2 + bw / 2, ty + lost / 2 - 2, "втрачено", size=9.5, color=POS, bold=True))
    f.append(text(x2 + bw / 2, ty + lost / 2 + 11, "з віком −20%", size=9, color=POS))
    # поточний повний заряд (до лінії 80%)
    f.append(rect(x2, line80, bw, bh - lost, fill=CHARGE, stroke="none", sw=0))
    f.append(rect(x2, line80, bw, bh - lost, fill="none", stroke=INK, sw=1.8))
    f.append(text(x2 + bw / 2, line80 + (bh - lost) / 2, "заряд", size=11, color=NEG, bold=True))
    f.append(text(x2 + bw / 2, line80 + (bh - lost) / 2 + 18, "= 100% SoC", size=10.5, color=NEG))
    # пунктирна лінія 80% через бак
    f.append(line(x2 - 6, line80, x2 + bw + 6, line80, color=POS, sw=1.2, dash="5,4"))
    f.append(text(x2 + bw / 2, by + 22, "SoH = 80%", size=12, bold=True, color=POS))
    f.append(text(x2 + bw / 2, by + 40, "теж «повна», та це 80% колишнього", size=10.5, color=MUTED))
    # стрілка «бак меншає» — донизу праворуч від бака
    sx = x2 + bw + 30
    f.append(arrow(sx, ty + 6, sx, line80 - 6, color=POS, sw=2.0))
    f.append(text(sx + 10, (ty + line80) / 2, "SoH", size=10, color=POS, anchor="start", bold=True))
    f.append(text(sx + 10, (ty + line80) / 2 + 14, "(тане)", size=9, color=POS, anchor="start"))

    # ── знак «≠» між баками ───────────────────────────────────────────────────
    f.append(text((x1 + bw + x2) / 2, (ty + by) / 2 - 6, "≠", size=30, bold=True, color=MUTED))
    f.append(text((x1 + bw + x2) / 2, (ty + by) / 2 + 22, "різні", size=10.5, color=MUTED))
    f.append(text((x1 + bw + x2) / 2, (ty + by) / 2 + 36, "речі", size=10.5, color=MUTED))

    b, _, _ = textbox(W / 2, 452,
                      "SoC — рівень заряду в баку: ходить угору-вниз щодня.  SoH — розмір самого бака: лише тане з роками.\n«повна» стара комірка (SoC 100%) вміщає менше за нову — її 100% дорівнює 80% колишнього.",
                      size=10.5, fill="#eef3fb", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "soc-vs-soh.svg"), W, H, *f)


# ── Два обличчя SoH: енергія і потужність можуть розходитися ──────────────────
def fig_two_faces():
    W, H = 820, 450
    f = [text(W / 2, 30, "Два обличчя SoH: енергія і потужність", size=16, bold=True)]
    ox, oy = 96, 330
    span_x, top = 600, 88
    PMIN = 50.0                       # низ шкали = 50%

    def yv(p):                        # SoH% → y
        return top + (oy - top) * ((100.0 - p) / (100.0 - PMIN))

    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, top - 6, ox, oy, color=MUTED, sw=1.4))
    f.append(text(ox - 10, top + 2, "SoH", size=11, color=MUTED, anchor="end", bold=True))
    f.append(text(ox + span_x, oy + 22, "роки / цикли →", size=11, color=MUTED, anchor="end"))
    for p in (100, 80, 60):
        yy = yv(p)
        f.append(line(ox - 4, yy, ox, yy, color=MUTED, sw=1.0))
        f.append(text(ox - 9, yy + 4, "%d%%" % p, size=9.5, color=MUTED, anchor="end"))

    # поріг 80% EoL
    f.append(line(ox, yv(80), ox + span_x, yv(80), color=MUTED, sw=1.0, dash="6,4"))
    f.append(text(ox + span_x, yv(80) - 6, "кінець життя ≈ 80%", size=10, color=MUTED, anchor="end"))

    # крива за ЄМНІСТЮ (енергія) — повільна, синя
    cap = []
    for i in range(0, 201):
        t = i / 200.0
        cap.append((ox + t * span_x, yv(100.0 - 15.0 * t)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in cap), NEG))
    f.append(text(ox + span_x + 4, yv(85.0) + 4, "за ємністю", size=11, color=NEG,
                  anchor="start", bold=True))
    f.append(text(ox + span_x + 4, yv(85.0) + 19, "(енергія)", size=9.5, color=NEG, anchor="start"))

    # крива за ОПОРОМ (потужність) — швидша, червона
    pw = []
    for i in range(0, 201):
        t = i / 200.0
        pw.append((ox + t * span_x, yv(100.0 - 44.0 * t)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" stroke-dasharray="6,3"/>'
             % (" ".join("%.1f,%.1f" % p for p in pw), POS))
    f.append(text(ox + span_x + 4, yv(58.0) + 2, "за опором", size=11, color=POS,
                  anchor="start", bold=True))
    f.append(text(ox + span_x + 4, yv(58.0) + 17, "(потужність)", size=9.5, color=POS, anchor="start"))

    # точка перетину порогу опором (100−44t = 80 → t = 0.4545)
    tx = 20.0 / 44.0
    cxp, cyp = ox + tx * span_x, yv(80.0)
    f.append(circle(cxp, cyp, 5, fill=POS, stroke="#ffffff", sw=1.5))
    b2, _, _ = textbox(cxp + 4, cyp + 46,
                       "тут комірка вже «сідає» під піками,\nхоча ємності ще досить",
                       size=9.5, fill="#fbeee6", stroke=POS)
    f.append(b2)

    # вертикальний розрив між кривими при t=0.72
    tg = 0.72
    xg = ox + tg * span_x
    yA, yB = yv(100.0 - 15.0 * tg), yv(100.0 - 44.0 * tg)
    f.append(line(xg, yA, xg, yB, color=INK, sw=1.0, dash="2,3"))
    f.append(text(xg - 8, (yA + yB) / 2 + 4, "дві різні цифри", size=9.5, color=INK, anchor="end"))

    b, _, _ = textbox(W / 2, 424,
                      "здоров'я має два знаки, і вони можуть розходитися: за ємністю (енергія) комірка сповзає повільно,\nа за опором (потужність) — часом швидше, перетинаючи поріг раніше. одного відсотка ємності мало.",
                      size=10.5, fill="#eef3fb", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "two-faces.svg"), W, H, *f)


# ── Як міряють SoH: ємність (еталонний розряд) і опір (стрибок) ───────────────
def fig_measure():
    W, H = 900, 450
    f = [text(W / 2, 30, "Як міряють SoH: ємність і опір", size=16, bold=True)]

    # розділювач
    f.append(line(W / 2, 60, W / 2, 348, color="#dddddd", sw=1.2, dash="4,4"))

    # ── ЛІВА панель: еталонний розряд → ампер-години ─────────────────────────
    f.append(text(230, 66, "За ємністю: еталонний розряд", size=12.5, bold=True, color=NEG))
    ox, oy = 74, 300
    top = 108
    f.append(line(ox, oy, ox + 320, oy, color=MUTED, sw=1.3))
    f.append(line(ox, oy, ox, top - 6, color=MUTED, sw=1.3))
    f.append(text(ox - 8, top + 2, "струм I", size=10, color=MUTED, anchor="end"))
    f.append(text(ox + 320, oy + 18, "час →", size=10, color=MUTED, anchor="end"))
    Iy = top + 26
    w_new, w_now = 250, 200
    # нова ємність — пунктирний контур (ширший)
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="none" '
             'stroke="%s" stroke-width="1.4" stroke-dasharray="5,4"/>'
             % (ox, Iy, w_new, oy - Iy, MUTED))
    f.append(text(ox + w_new - 4, Iy - 8, "нова (А·год)", size=9.5, color=MUTED, anchor="end"))
    # теперішня ємність — залита площа (вужча)
    f.append(rect(ox, Iy, w_now, oy - Iy, fill=CHARGE, stroke=NEG, sw=1.8))
    f.append(text(ox + w_now / 2, (Iy + oy) / 2, "площа = ∫I·dt", size=10.5, color=NEG, bold=True))
    f.append(text(ox + w_now / 2, (Iy + oy) / 2 + 16, "= А·год тепер", size=10, color=NEG))
    f.append(text(ox + 160, oy + 40, "SoH = А·год тепер / А·год нові", size=10.5, color=NEG,
                  bold=True, anchor="middle"))

    # ── ПРАВА панель: навантажувальний стрибок → R = ΔU/ΔI ────────────────────
    f.append(text(W / 2 + 230, 66, "За опором: навантажувальний стрибок", size=12.5, bold=True, color=POS))
    ax, ay = W / 2 + 60, 300
    span = 300
    f.append(line(ax, ay, ax + span, ay, color=MUTED, sw=1.3))
    f.append(line(ax, ay, ax, top - 6, color=MUTED, sw=1.3))
    f.append(text(ax - 8, top + 2, "напруга U", size=10, color=MUTED, anchor="end"))
    f.append(text(ax + span, ay + 18, "час →", size=10, color=MUTED, anchor="end"))
    Uhi, Ulo = top + 24, top + 96
    xs = ax + span * 0.42             # момент увімкнення навантаження
    xe = ax + span * 0.82
    trace = "M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" % (
        ax + 6, Uhi, xs, Uhi, xs, Ulo, xe, Ulo, xe, Uhi)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (trace, POS))
    # позначка ΔU
    f.append(line(xs - 22, Uhi, xs - 22, Ulo, color=INK, sw=1.0))
    f.append(arrow(xs - 22, Uhi + 4, xs - 22, Ulo - 4, color=INK, sw=1.4))
    f.append(text(xs - 30, (Uhi + Ulo) / 2 + 4, "ΔU", size=11, color=INK, anchor="end", bold=True))
    # позначка ΔI (момент стрибка навантаження)
    f.append(text(xs + 6, Ulo + 22, "навантаження +ΔI", size=9.5, color=MUTED, anchor="start"))
    f.append(text(ax + span / 2, ay + 40, "R = ΔU / ΔI  →  порівняй з новим",
                  size=10.5, color=POS, bold=True, anchor="middle"))

    b, _, _ = textbox(W / 2, 418,
                      "ємнісний SoH міряють ЕТАЛОННИМ РОЗРЯДОМ (точно, але треба повний цикл від повної до порожньої);\nрезистивний — НАВАНТАЖУВАЛЬНИМ СТРИБКОМ R=ΔU/ΔI проти нового опору (швидко, за секунди, без розряджання).",
                      size=10.5, fill="#f3eef6", stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "measure.svg"), W, H, *f)


# ══ Фігури до вставки math-soh-metrics ═══════════════════════════════════════

# ── Нормування двох SoH на спільну вісь ресурсу + правило мінімуму ────────────
def fig_normalize():
    W, H = 920, 500
    f = [text(W / 2, 30, "Як звести два SoH в одне число", size=16, bold=True)]

    # ── ЛІВА панель: сирі числа на різних шкалах ─────────────────────────────
    f.append(text(240, 66, "сирі числа: різні шкали", size=12.5, bold=True, color=MUTED))

    def raw_axis(y, name, name_col, lo_lab, hi_lab, frac, mark_lab, mark_col,
                 name_y, mark_y, lab_y, mark_anchor="middle"):
        g = [text(90, name_y, name, size=11, bold=True, color=name_col, anchor="start"),
             line(90, y, 400, y, color=MUTED, sw=1.4),
             line(90, y - 5, 90, y + 5, color=MUTED, sw=1.4),
             line(400, y - 5, 400, y + 5, color=MUTED, sw=1.4),
             text(90, lab_y, lo_lab, size=10, color=MUTED, anchor="start"),
             text(400, lab_y, hi_lab, size=10, color=MUTED, anchor="end")]
        mx = 90 + frac * 310
        g.append(circle(mx, y, 5, fill=mark_col, stroke="#ffffff", sw=1.5))
        g.append(text(mx if mark_anchor == "middle" else 400, mark_y, mark_lab,
                      size=10, color=mark_col, bold=True, anchor=mark_anchor))
        return g

    f += raw_axis(140, "ємність  C/C₀", NEG, "1.00 (нова)", "0.80 = поріг",
                  0.75, "виміряно 0.85", NEG, 116, 122, 162)
    f += raw_axis(225, "опір  R/R₀", POS, "1.00 (новий)", "2.00 = поріг",
                  1.00, "виміряно 2.00", POS, 201, 207, 247, mark_anchor="end")

    b1, _, _ = textbox(245, 310,
                       "0.85 і 2.00 — числа з РІЗНИХ шкал:\n"
                       "у першої поріг на 0.80, у другої на 2.00.\n"
                       "їхнє середнє не означає нічого.",
                       size=10.5, fill="#f3eef6", stroke=MUTED)
    f.append(b1)

    # ── стрілка «нормування» ─────────────────────────────────────────────────
    f.append(text(460, 176, "нормування", size=10, color=INK, bold=True))
    f.append(arrow(428, 190, 492, 190, color=INK, sw=2.0))

    # ── ПРАВА панель: спільна вісь ресурсу ───────────────────────────────────
    f.append(text(690, 66, "спільна вісь ресурсу", size=12.5, bold=True, color=FIELD))
    yc = 180
    f.append(text(540, 156, "залишок ресурсу", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(line(540, yc, 850, yc, color=MUTED, sw=1.4))
    f.append(line(540, yc - 5, 540, yc + 5, color=MUTED, sw=1.4))
    f.append(line(850, yc - 5, 850, yc + 5, color=MUTED, sw=1.4))
    f.append(text(540, 202, "100% (нова)", size=10, color=MUTED, anchor="start"))
    f.append(text(850, 202, "0% = кінець життя", size=10, color=MUTED, anchor="end"))

    xc = 540 + 0.75 * 310                     # ємнісний SoH* = 25%
    f.append(line(xc, 156, xc, yc - 6, color=NEG, sw=1.0, dash="3,3"))
    f.append(circle(xc, yc, 5, fill=NEG, stroke="#ffffff", sw=1.5))
    f.append(text(xc, 146, "за ємністю: 25%", size=10.5, color=NEG, bold=True))

    f.append(line(850, 130, 850, yc - 6, color=POS, sw=1.0, dash="3,3"))
    f.append(circle(850, yc, 5, fill=POS, stroke="#ffffff", sw=1.5))
    f.append(text(850, 118, "за опором: 0%", size=10.5, color=POS, bold=True, anchor="end"))

    b2, _, _ = textbox(690, 300,
                       "SoH = min(25%, 0%) = 0%\nланцюг рветься там, де тонше",
                       size=11, fill="#eaf7ef", stroke=FIELD)
    f.append(b2)

    b3, _, _ = textbox(460, 452,
                       "поки числа сирі, вони на різних шкалах; афінне нормування «нова = 100%, поріг = 0%» зводить їх на одну вісь.\n"
                       "далі беруть не середнє, а МІНІМУМ: пристрій відмовляє за тією віссю, що першою впала до нуля.",
                       size=10.5, fill="#eef3fb", stroke=NEG)
    f.append(b3)
    render(os.path.join(IMG, "soh-normalize.svg"), W, H, *f)


# ── Форма кривої вирішує прогноз: √t проти прямої ─────────────────────────────
def fig_shape_bias():
    W, H = 880, 480
    f = [text(W / 2, 30, "Один рік даних — три різні прогнози", size=16, bold=True)]
    ox, oy, top, span = 90, 350, 90, 690
    PLO, PHI = 76.0, 100.0

    def xt(t):
        return ox + t / 7.0 * span

    def yv(p):
        return top + (oy - top) * (PHI - p) / (PHI - PLO)

    # вікно спостереження (перший рік)
    f.append(rect(ox, top, xt(1) - ox, oy - top, fill="#f0f2f5", stroke="none", sw=0))
    f.append(text(ox, top - 22, "SoH", size=11, color=MUTED, bold=True))
    f.append(text((ox + xt(1)) / 2, top - 8, "перший рік", size=9.5, color=MUTED))

    # осі
    f.append(line(ox, oy, ox + span + 10, oy, color=MUTED, sw=1.4))
    f.append(line(ox, top - 6, ox, oy, color=MUTED, sw=1.4))
    for p in (100, 95, 90, 85, 80):
        yy = yv(p)
        f.append(line(ox - 4, yy, ox, yy, color=MUTED, sw=1.0))
        f.append(text(ox - 9, yy + 4, "%d%%" % p, size=9.5, color=MUTED, anchor="end"))
    for t in range(0, 8):
        f.append(line(xt(t), oy, xt(t), oy + 4, color=MUTED, sw=1.0))
        f.append(text(xt(t), oy + 22, "%d" % t, size=9.5, color=MUTED))
    f.append(text((ox + xt(7)) / 2, oy + 46, "роки", size=11, color=MUTED, bold=True))

    # поріг 80%
    f.append(line(ox, yv(80), ox + span + 10, yv(80), color=MUTED, sw=1.1, dash="6,4"))

    def poly(pts, color, sw=2.6, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (" ".join("%.1f,%.1f" % q for q in pts), color, sw, d))

    # справжня крива: втрата = 8·√t
    curve = [(xt(i / 60.0 * 7.0), yv(100.0 - 8.0 * math.sqrt(i / 60.0 * 7.0)))
             for i in range(0, 61)]
    f.append(poly(curve, NEG))

    # хорда від початку: 8%/рік
    f.append(poly([(xt(0), yv(100.0)), (xt(2.55), yv(100.0 - 8.0 * 2.55))], POS, dash="7,4"))

    # дотична на першому році: 4%/рік
    f.append(poly([(xt(0.5), yv(94.0)), (xt(4.3), yv(92.0 - 4.0 * 3.3))], FIELD, dash="2,4"))

    # точки перетину порогу
    for t, lab, col in ((2.5, "2.5 р", POS), (4.0, "4 р", FIELD), (6.25, "6.25 р", NEG)):
        f.append(circle(xt(t), yv(80), 5, fill=col, stroke="#ffffff", sw=1.5))
        f.append(text(xt(t), 334, lab, size=10.5, color=col, bold=True))

    # легенда праворуч угорі
    lx, tx0 = 430, 473
    for i, (col, dash, lab) in enumerate((
            (NEG, None, "справжня крива, втрата ∝ √t   →   6.25 року"),
            (POS, "7,4", "пряма від початку, 8%/рік   →   2.5 року"),
            (FIELD, "2,4", "дотична на 1-му році, 4%/рік   →   4 роки"))):
        yy = 120 + i * 26
        f.append(line(lx, yy - 4, lx + 34, yy - 4, color=col, sw=2.6, dash=dash))
        f.append(text(tx0, yy, lab, size=10.5, color=col, anchor="start"))

    b, _, _ = textbox(440, 448,
                      "ті самі дані першого року — три різні відповіді: усе вирішує ПРИПУЩЕНА форма кривої.\n"
                      "по спадній (увігнутій) кривій пряма завжди дає кінець життя зарано — тут у 2.5 раза.",
                      size=10.5, fill="#eef3fb", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "extrapolate-shape.svg"), W, H, *f)


# ── Похибка нахилу → несиметричний інтервал залишкового ресурсу ───────────────
def fig_slope_cone():
    W, H = 880, 470
    f = [text(W / 2, 30, "Похибка нахилу задає ширину прогнозу", size=16, bold=True)]
    ox, oy, top, span = 90, 360, 90, 700
    PLO, PHI = 76.0, 100.0

    def xm(m):
        return ox + m / 48.0 * span

    def yv(p):
        return top + (oy - top) * (PHI - p) / (PHI - PLO)

    # вікно спостереження
    f.append(rect(ox, top, xm(11) - ox, oy - top, fill="#f0f2f5", stroke="none", sw=0))
    f.append(text(ox, top - 22, "SoH", size=11, color=MUTED, bold=True))
    f.append(text((ox + xm(11)) / 2 + 10, top - 8, "12 вимірів / 11 міс", size=9.5, color=MUTED))

    # конус довіри (між крайніми нахилами)
    x0, y0 = xm(11), yv(92.0)
    xa, xb = xm(11 + 12.0 / 0.625), xm(11 + 12.0 / 0.375)
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fbeee6" '
             'stroke="none"/>' % (x0, y0, xa, yv(80), xb, yv(80)))

    # осі
    f.append(line(ox, oy, ox + span + 10, oy, color=MUTED, sw=1.4))
    f.append(line(ox, top - 6, ox, oy, color=MUTED, sw=1.4))
    for p in (100, 95, 90, 85, 80):
        yy = yv(p)
        f.append(line(ox - 4, yy, ox, yy, color=MUTED, sw=1.0))
        f.append(text(ox - 9, yy + 4, "%d%%" % p, size=9.5, color=MUTED, anchor="end"))
    for m in (0, 6, 12, 18, 24, 30, 36, 42, 48):
        f.append(line(xm(m), oy, xm(m), oy + 4, color=MUTED, sw=1.0))
        f.append(text(xm(m), oy + 22, "%d" % m, size=9.5, color=MUTED))
    f.append(text((ox + xm(48)) / 2, oy + 46, "місяці", size=11, color=MUTED, bold=True))
    f.append(line(ox, yv(80), ox + span + 10, yv(80), color=MUTED, sw=1.1, dash="6,4"))

    # виміри (шумні)
    offs = [0.8, -1.4, 1.1, -0.5, 1.6, -1.2, 0.3, -1.7, 0.9, -0.6, 1.3, -0.9]
    for m, dv in enumerate(offs):
        f.append(circle(xm(m), yv(97.5 - 0.5 * m + dv), 3.5, fill=NEG, stroke="#ffffff", sw=1.2))

    # пряма МНК + її продовження
    f.append('<polyline points="%.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" '
             'stroke-width="2.6"/>' % (xm(0), yv(97.5), x0, y0, NEG))
    f.append('<polyline points="%.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" '
             'stroke-width="2.2" stroke-dasharray="7,4"/>'
             % (x0, y0, xm(35), yv(80), NEG))
    # крайні нахили
    for xe in (xa, xb):
        f.append('<polyline points="%.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.6" stroke-dasharray="3,4"/>' % (x0, y0, xe, yv(80), POS))

    for xx, lab, col in ((xa, "19", POS), (xm(35), "24 міс", NEG), (xb, "32", POS)):
        f.append(circle(xx, yv(80), 4.5, fill=col, stroke="#ffffff", sw=1.4))
        f.append(text(xx, yv(80) + 24, lab, size=10.5, color=col, bold=True))

    # легенда
    lx, tx0 = 430, 473
    for i, (col, dash, sw, lab) in enumerate((
            (NEG, None, 2.6, "нахил за МНК: −0.50 %/міс   →   RUL 24 міс"),
            (POS, "3,4", 1.6, "±1σ нахилу (±0.125)   →   RUL від 19 до 32 міс"))):
        yy = 120 + i * 26
        f.append(line(lx, yy - 4, lx + 34, yy - 4, color=col, sw=sw, dash=dash))
        f.append(text(tx0, yy, lab, size=10.5, color=col, anchor="start"))

    b, _, _ = textbox(440, 430,
                      "дванадцять шумних вимірів дають нахил −0.50 ± 0.125 %/міс — і саме похибка НАХИЛУ задає ширину прогнозу.\n"
                      "інтервал несиметричний: RUL = ΔSoH / нахил, тож менший нахил відкидає кінець життя далеко вправо.",
                      size=10.5, fill="#eef3fb", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "rul-cone.svg"), W, H, *f)


# ── Вставка proj: два якорі замість повного циклу ─────────────────────────────
def fig_anchors():
    W, H = 900, 520
    f = [text(W / 2, 30, "Два якорі замість повного циклу", size=16, bold=True)]

    ox, oy = 90, 340
    span_x, top = 620, 110
    UMIN, UMAX = 3.50, 4.10

    def yu(u):
        return top + (oy - top) * (UMAX - u) / (UMAX - UMIN)

    def xt(t):
        return ox + span_x * t

    # заборонене плато OCV — смуга під кривою
    f.append(rect(ox, yu(3.80), span_x, yu(3.737) - yu(3.80),
                  fill="#fbeee6", stroke="none", sw=0))
    f.append(text(ox + span_x + 8, yu(3.80) - 2, "плато OCV", size=9.5,
                  color=POS, anchor="start", bold=True))
    f.append(text(ox + span_x + 8, yu(3.80) + 12, "3.74–3.80 В", size=9.5,
                  color=POS, anchor="start"))

    # осі
    f.append(line(ox, oy, ox + span_x + 10, oy, color=MUTED, sw=1.3))
    f.append(line(ox, oy, ox, top - 10, color=MUTED, sw=1.3))
    f.append(text(ox - 8, top - 16, "напруга, В", size=10, color=MUTED, anchor="end"))
    for u in (4.0, 3.9, 3.8, 3.7, 3.6):
        yy = yu(u)
        f.append(line(ox - 4, yy, ox, yy, color=MUTED, sw=1.0))
        f.append(text(ox - 8, yy + 4, "%.1f" % u, size=9.5, color=MUTED, anchor="end"))
    f.append(text(ox + span_x + 10, oy + 36, "час →", size=10, color=MUTED, anchor="end"))

    # хід напруги: спокій → розряд → короткий спокій на плато → розряд → спокій
    keys = [(0.00, 4.02), (0.10, 4.02), (0.42, 3.78), (0.52, 3.77),
            (0.80, 3.62), (0.95, 3.62)]
    pts = []
    for i in range(len(keys) - 1):
        t0, u0 = keys[i]
        t1, u1 = keys[i + 1]
        for k in range(21):
            s = k / 20.0
            pts.append((xt(t0 + (t1 - t0) * s), yu(u0 + (u1 - u0) * s)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts), NEG))

    # дужка ΔQ між якорями
    xa, xb = xt(0.09), xt(0.93)
    f.append(line(xa, 80, xb, 80, color=INK, sw=1.2))
    f.append(line(xa, 80, xa, 90, color=INK, sw=1.2))
    f.append(line(xb, 80, xb, 90, color=INK, sw=1.2))
    f.append(text((xa + xb) / 2, 66, "кулонометр між якорями: ΔQ = 1730 мА·год",
                  size=11, color=INK, bold=True))

    # якір 1
    f.append(circle(xa, yu(4.02), 5.5, fill=FIELD, stroke="#ffffff", sw=1.6))
    b1, _, _ = textbox(210, 122, "якір 1: спокій\nOCV 4.02 В → SoC 92.0 %",
                       size=10, fill="#eaf6ee", stroke=FIELD)
    f.append(b1)

    # якір 2
    f.append(circle(xb, yu(3.62), 5.5, fill=FIELD, stroke="#ffffff", sw=1.6))
    b2, _, _ = textbox(596, 308, "якір 2: спокій\nOCV 3.62 В → SoC 24.0 %",
                       size=10, fill="#eaf6ee", stroke=FIELD)
    f.append(b2)

    # відхилений якір на плато
    xr, yr = xt(0.47), yu(3.77)
    f.append(circle(xr, yr, 6.0, fill="#ffffff", stroke=POS, sw=2.0))
    f.append(text(xr, yr + 3.5, "✕", size=9, color=POS, bold=True))
    b3, _, _ = textbox(388, 264, "OCV тут пласка —\nякір відхилено",
                       size=10, fill="#fbeee6", stroke=POS)
    f.append(b3)

    b, _, _ = textbox(W / 2, 452,
                      "Qповна = ΔQ / (SoC₁ − SoC₂) = 1730 мА·год / 0.680 = 2544 мА·год  →  SoH за ємністю = 2544 / 3000 = 85 %\n"
                      "повного циклу не було: між якорями минуло лише 68 % шкали — і цього досить",
                      size=10.5, fill="#eef3fb", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "anchors.svg"), W, H, *f)


# ── Вставка proj: опір залежить від того, коли міряти ─────────────────────────
def fig_r_timing():
    W, H = 880, 470
    f = [text(W / 2, 30, "Той самий стрибок — три різні опори", size=16, bold=True)]

    ox, oy = 100, 336
    span_x, top = 590, 112
    LT0, LT1 = -3.0, math.log10(30.0)          # 1 мс … 30 с, логарифмічна вісь
    DMAX = 110.0                               # шкала просідання, мВ

    def xt(t):
        return ox + span_x * (math.log10(t) - LT0) / (LT1 - LT0)

    def yd(d):
        return top + (oy - top) * d / DMAX

    def sag(t):                                # просідання, мВ, при ΔI = 1 А
        return 30.0 + 25.0 * (1 - math.exp(-t / 0.3)) + 50.0 * (1 - math.exp(-t / 8.0))

    # осі
    f.append(line(ox, oy, ox + span_x + 10, oy, color=MUTED, sw=1.3))
    f.append(line(ox, oy, ox, top - 10, color=MUTED, sw=1.3))
    f.append(text(ox - 8, top - 16, "просідання, мВ", size=10, color=MUTED, anchor="end"))
    for d in (0, 30, 60, 90):
        yy = yd(d)
        f.append(line(ox - 4, yy, ox, yy, color=MUTED, sw=1.0))
        f.append(text(ox - 8, yy + 4, "%d" % d, size=9.5, color=MUTED, anchor="end"))

    # рівень до стрибка
    f.append(line(ox, top, ox + span_x + 10, top, color=MUTED, sw=1.2, dash="5,4"))
    f.append(text(ox + span_x + 14, top + 4, "рівень до стрибка", size=9.5,
                  color=MUTED, anchor="start"))

    # крива просідання
    pts = []
    for i in range(0, 241):
        lt = LT0 + (LT1 - LT0) * i / 240.0
        pts.append((ox + span_x * i / 240.0, yd(sag(10.0 ** lt))))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts), POS))

    # мітки часу на осі
    for t, lab in ((0.001, "1 мс"), (0.01, "10 мс"), (0.1, "100 мс"),
                   (1.0, "1 с"), (10.0, "10 с")):
        xx = xt(t)
        f.append(line(xx, oy, xx, oy + 5, color=MUTED, sw=1.0))
        f.append(text(xx, oy + 20, lab, size=9.5, color=MUTED))

    # три моменти виміру: пунктир від кривої вниз + значення опору
    for t, r in ((0.01, 31), (1.0, 60), (10.0, 91)):
        xx, yy = xt(t), yd(sag(t))
        f.append(line(xx, yy, xx, oy - 26, color=INK, sw=1.0, dash="3,3"))
        f.append(circle(xx, yy, 4.5, fill=INK, stroke="#ffffff", sw=1.4))
        f.append(text(xx, oy - 12, "%d мОм" % r, size=11, color=INK, bold=True))

    # що саме встигло долучитися
    f.append(text(ox + 10, 154, "омічна частина: електроліт і контакти", size=10,
                  color=MUTED, anchor="start"))
    f.append(text(xt(0.12), 190, "+ перенос заряду на межі електрода", size=10,
                  color=MUTED, anchor="start"))
    f.append(text(xt(2.4), 248, "+ дифузія вглиб", size=10,
                  color=MUTED, anchor="start"))

    b0, _, _ = textbox(772, 62, "стрибок ΔI = 1 А\nкомірка за 25 °C",
                       size=10, fill="#f3eef6", stroke=MUTED)
    f.append(b0)

    b, _, _ = textbox(W / 2, 424,
                      "один і той самий стрибок дає 31, 60 або 91 мОм — залежно лише від того, о котрій секунді глянути.\n"
                      "тому R без домовленості про момент виміру — ще не число: звіряти можна лише з еталоном, знятим за тим самим правилом.",
                      size=10.5, fill="#fbeee6", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "r-timing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_soc_vs_soh()
    fig_two_faces()
    fig_measure()
    fig_normalize()
    fig_shape_bias()
    fig_slope_cone()
    fig_anchors()
    fig_r_timing()
    print("OK: 8 figures ->", IMG)
