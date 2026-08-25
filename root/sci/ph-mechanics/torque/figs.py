# -*- coding: utf-8 -*-
"""Фігури до теми «Момент сили».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5, op=1.0):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            'fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"/>'
            % (cx, cy, rx, ry, fill, op, stroke, sw))


def arc_path(cx, cy, rx, ry, a0_deg, a1_deg, color=LINE, sw=2.2):
    """Дуга еліпса від кута a0 до a1 (градуси, 0°=праворуч, проти год.)."""
    a0 = math.radians(a0_deg); a1 = math.radians(a1_deg)
    x0 = cx + rx * math.cos(a0); y0 = cy - ry * math.sin(a0)
    x1 = cx + rx * math.cos(a1); y1 = cy - ry * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    sweep = 0 if a1_deg > a0_deg else 1
    return ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (x0, y0, rx, ry, large, sweep, x1, y1, color, sw))


def arc_arrow(cx, cy, r, a0_deg, a1_deg, color=LINE, sw=2.4, head=10):
    """Дуга-стрілка (коло) від кута a0 до a1 (градуси, 0°=праворуч, проти год.)."""
    a0 = math.radians(a0_deg); a1 = math.radians(a1_deg)
    x0 = cx + r * math.cos(a0); y0 = cy - r * math.sin(a0)
    x1 = cx + r * math.cos(a1); y1 = cy - r * math.sin(a1)
    sweep_ccw = 1 if a1_deg > a0_deg else 0
    sweep = 0 if sweep_ccw else 1
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    path = ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw))
    dir_sign = 1 if sweep_ccw else -1
    tx = -math.sin(a1) * dir_sign
    ty = -math.cos(a1) * dir_sign
    L = math.hypot(tx, ty); tx, ty = tx / L, ty / L
    back = 2.2
    px, py = x1 - tx * head, y1 - ty * head
    nx, ny = -ty, tx
    h = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
         % (x1, y1, px + nx * head / back, py + ny * head / back,
            px - nx * head / back, py - ny * head / back, color))
    return path + h


def right_angle(px, py, u, v, s=13, color=MUTED):
    """Квадратик прямого кута у точці (px,py) між напрямами u і v (одиничні)."""
    ax, ay = px + u[0] * s, py + u[1] * s
    bx, by = px + v[0] * s, py + v[1] * s
    cx, cy = ax + v[0] * s, ay + v[1] * s
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="1.2"/>' % (ax, ay, cx, cy, bx, by, color))


# ── Фігура 1: плече й розклад сили ───────────────────────────────────────────
def fig_lever():
    W, H = 780, 450
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Повертає лише поперечна до важеля частина сили",
                  size=17, bold=True))

    O = (150, 340)
    P = (560, 175)
    ux, uy = P[0] - O[0], P[1] - O[1]
    L = math.hypot(ux, uy); ub = (ux / L, uy / L)

    # важіль
    f.append(line(O[0], O[1], P[0], P[1], color=INK, sw=4))
    f.append(circle(O[0], O[1], 9, fill=FILL, stroke=INK, sw=2))
    f.append(text(O[0] - 6, O[1] + 30, "вісь", size=13, color=MUTED, anchor="middle"))
    f.append(text((O[0] + P[0]) / 2 + 6, (O[1] + P[1]) / 2 + 34,
                  "важіль  r", size=14, italic=True, anchor="middle"))
    f.append(circle(P[0], P[1], 5, fill=INK, stroke=INK, sw=1))

    # сила F та її складові
    du = (0.26, -0.966)                    # напрям сили (майже вгору)
    FL = 125
    Fv = (du[0] * FL, du[1] * FL)
    fdot = Fv[0] * ub[0] + Fv[1] * ub[1]
    Fpar = (fdot * ub[0], fdot * ub[1])
    Fper = (Fv[0] - Fpar[0], Fv[1] - Fpar[1])
    Ftip = (P[0] + Fv[0], P[1] + Fv[1])
    Ppar = (P[0] + Fpar[0], P[1] + Fpar[1])
    Pper = (P[0] + Fper[0], P[1] + Fper[1])

    # пунктирний паралелограм розкладу
    f.append(line(Pper[0], Pper[1], Ftip[0], Ftip[1], color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(Ppar[0], Ppar[1], Ftip[0], Ftip[1], color=MUTED, sw=1.2, dash="4 4"))

    # складова вздовж важеля — марна (сіра)
    f.append(arrow(P[0], P[1], Ppar[0], Ppar[1], color=MUTED, sw=2.4))
    f.append(text(Ppar[0] + 12, Ppar[1] + 6, "вздовж — марна", size=12,
                  color=MUTED, anchor="start"))
    # складова впоперек — повертає (зелена)
    f.append(arrow(P[0], P[1], Pper[0], Pper[1], color=FIELD, sw=3.0))
    f.append(text(Pper[0] - 12, Pper[1] - 8, "впоперек — повертає", size=12,
                  bold=True, color=FIELD, anchor="end"))
    # повна сила F (червона)
    f.append(arrow(P[0], P[1], Ftip[0], Ftip[1], color=POS, sw=3.2))
    f.append(text(Ftip[0] + 12, Ftip[1] - 2, "F", size=16, bold=True, color=POS,
                  anchor="start"))

    # прямий кут між складовими
    upar = (Fpar[0] / math.hypot(*Fpar), Fpar[1] / math.hypot(*Fpar))
    uper = (Fper[0] / math.hypot(*Fper), Fper[1] / math.hypot(*Fper))
    f.append(right_angle(P[0], P[1], upar, uper, s=12))

    # кут θ між важелем і силою (маленька дуга біля P)
    a_bar = math.degrees(math.atan2(-(ub[1]), ub[0]))
    a_for = math.degrees(math.atan2(-(du[1]), du[0]))
    f.append(arc_arrow(P[0], P[1], 40, a_bar, a_for, color=INK, sw=1.6, head=7))
    f.append(text(P[0] + 40, P[1] - 34, "θ", size=14, italic=True, anchor="middle"))

    # формула
    b, w, h = textbox(W / 2, H - 30,
                      "M = F · r · sin θ    (упоперек: sin θ = 1 — максимум)",
                      size=14, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "lever-arm.svg"), W, H, *f)


# ── Фігура 2: момент — вектор уздовж осі ─────────────────────────────────────
def fig_vector():
    W, H = 720, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Важіль і сила — у площині, момент — уздовж осі",
                  size=17, bold=True))

    C = (330, 300)
    rx, ry = 190, 62
    # площина обертання
    f.append(ellipse(C[0], C[1], rx, ry, fill="#f4f8fc", stroke=MUTED, sw=1.5, op=1.0))
    f.append(text(C[0] - rx + 8, C[1] + ry + 26, "площина обертання",
                  size=12, color=MUTED, anchor="start"))

    # вісь (вертикаль крізь центр) — пунктир вниз, стрілка-момент угору
    f.append(line(C[0], C[1], C[0], C[1] + 70, color=MUTED, sw=1.3, dash="5 5"))
    f.append(arrow(C[0], C[1], C[0], 96, color=NEG, sw=3.4))
    f.append(text(C[0] + 14, 104, "M = r × F", size=16, bold=True, color=NEG,
                  anchor="start"))
    f.append(text(C[0] + 14, 126, "(уздовж осі)", size=12, color=NEG, anchor="start"))

    # важіль r у площині
    Pr = (C[0] + 120, C[1] + 8)
    f.append(arrow(C[0], C[1], Pr[0], Pr[1], color=INK, sw=2.6))
    f.append(text((C[0] + Pr[0]) / 2, C[1] + 30, "r", size=15, italic=True,
                  anchor="middle"))
    f.append(circle(C[0], C[1], 7, fill=FILL, stroke=INK, sw=2))
    # сила F у площині (по дотичній до обертання)
    Ft = (Pr[0] - 30, Pr[1] - 58)
    f.append(arrow(Pr[0], Pr[1], Ft[0], Ft[1], color=POS, sw=3.0))
    f.append(text(Ft[0] + 12, Ft[1] - 4, "F", size=16, bold=True, color=POS,
                  anchor="start"))

    # напрям обертання у площині
    f.append(arc_path(C[0], C[1], rx - 18, ry - 12, 200, 20, color=FIELD, sw=2.4))
    f.append(text(C[0] - rx + 30, C[1] - ry + 6, "обертання", size=12,
                  color=FIELD, anchor="start"))

    # підказка про правило правої руки
    b, w, h = textbox(W / 2, H - 34,
                      "пальці правої руки від r до F — великий палець показує M",
                      size=13, pad=10, fill="#eef2fb", stroke=NEG, sw=1.3, bold=False)
    f.append(b)
    return render(os.path.join(IMG, "torque-vector.svg"), W, H, *f)


# ── Фігура 3: гойдалка-балансир ──────────────────────────────────────────────
def fig_seesaw():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Рівновага: важче — ближче, легше — далі",
                  size=17, bold=True))

    piv = (380, 250)          # вершина опори
    scale = 150               # px на метр
    beam_y = piv[1] - 12
    # балка
    f.append(rect(piv[0] - 250, beam_y - 7, 500, 14, fill=FILL, stroke=INK, sw=1.8, rx=4))
    # опора-трикутник
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s" stroke="%s" '
             'stroke-width="1.8"/>' % (piv[0], piv[1], piv[0] - 34, piv[1] + 78,
                                       piv[0] + 34, piv[1] + 78, FILL, INK))

    def load(dx_m, mass, label, near):
        x = piv[0] + dx_m * scale
        # блок вантажу
        bw = 58
        f.append(rect(x - bw / 2, beam_y - 46, bw, 34, fill="#eef2fb", stroke=NEG, sw=1.8, rx=6))
        f.append(text(x, beam_y - 24, "%d кг" % mass, size=14, bold=True, color=NEG))
        # стрілка ваги вниз
        f.append(arrow(x, beam_y + 12, x, beam_y + 66, color=POS, sw=2.6))
        f.append(text(x, beam_y + 84, "вага", size=11, color=POS))
        # розмірна лінія до осі
        dl_y = piv[1] + 104
        f.append(line(piv[0], dl_y, x, dl_y, color=MUTED, sw=1.2))
        f.append(line(piv[0], dl_y - 6, piv[0], dl_y + 6, color=MUTED, sw=1.2))
        f.append(line(x, dl_y - 6, x, dl_y + 6, color=MUTED, sw=1.2))
        f.append(text((piv[0] + x) / 2, dl_y - 8, "%.2f м" % abs(dx_m), size=12,
                      color=MUTED))
        return x

    load(-0.75, 60, "дорослий", True)     # важчий — ближче
    load(1.50, 30, "дитина", False)       # легший — далі
    f.append(text(piv[0], piv[1] + 96, "вісь", size=12, color=MUTED))

    b, w, h = textbox(W / 2, H - 26,
                      "60 · 0.75 = 30 · 1.50 = 45 Н·м    →    сума моментів = 0",
                      size=14, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "seesaw-balance.svg"), W, H, *f)


# ── Фігура 4: пара сил ───────────────────────────────────────────────────────
def fig_couple():
    W, H = 720, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Пара сил: сумарна сила — нуль, а момент — ні",
                  size=17, bold=True))

    C = (360, 240)
    R = 128
    # кермо: обід, маточина, спиці
    f.append(circle(C[0], C[1], R, fill="#fbfcfe", stroke=INK, sw=6))
    f.append(circle(C[0], C[1], 18, fill=FILL, stroke=INK, sw=2))
    for ang in (90, 210, 330):
        a = math.radians(ang)
        f.append(line(C[0], C[1], C[0] + (R - 8) * math.cos(a),
                      C[1] - (R - 8) * math.sin(a), color=MUTED, sw=4))

    # права точка обода — сила вгору; ліва — вниз (рівні, протилежні)
    Rp = (C[0] + R, C[1])
    Lp = (C[0] - R, C[1])
    f.append(arrow(Rp[0], Rp[1], Rp[0], Rp[1] - 96, color=POS, sw=3.2))
    f.append(text(Rp[0] + 12, Rp[1] - 96, "F", size=16, bold=True, color=POS, anchor="start"))
    f.append(arrow(Lp[0], Lp[1], Lp[0], Lp[1] + 96, color=POS, sw=3.2))
    f.append(text(Lp[0] - 12, Lp[1] + 96, "F", size=16, bold=True, color=POS, anchor="end"))

    # результівне обертання (проти годинникової: право вгору + ліво вниз)
    f.append(arc_arrow(C[0], C[1], R - 42, -40, 180, color=FIELD, sw=3.0, head=11))
    f.append(text(C[0], C[1] + 58, "обертання", size=13, bold=True, color=FIELD))

    b1, w1, h1 = textbox(240, H - 30, "↑F  +  ↓F  =  0\nсумарна сила",
                         size=13, pad=9, fill="#eef2fb", stroke=NEG, sw=1.3, bold=True)
    f.append(b1)
    b2, w2, h2 = textbox(480, H - 30, "M = F · d  ≠  0\nчистий момент",
                         size=13, pad=9, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b2)
    return render(os.path.join(IMG, "couple.svg"), W, H, *f)


# ── Фігура 5: історична вісь (для вставки hist-lever) ─────────────────────────
def fig_timeline():
    W, H = 880, 930
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Від важеля до слова «torque»: понад дві тисячі років",
                  size=18, bold=True))

    spine_x = 182
    y0, step = 128, 100
    f.append(line(spine_x, y0 - 24, spine_x, y0 + step * 7 + 26, color=MUTED, sw=2.2))

    rows = [
        ("прадавно", MUTED, "#f4f6f8",
         "Важіль, лом, шадуф, коромисло терезів — у щоденному вжитку.\n"
         "Принцип знали з практики, без жодної теорії."),
        ("≈330 до н.е.", INK, "#f4f6f8",
         "«Механіка» школи Арістотеля: перший теоретичний опис —\n"
         "важіль зводять до кола. Центра ваги ще немає."),
        ("≈250 до н.е.", FIELD, "#eef6ef",
         "Архімед, «Про рівновагу площин»: строге доведення закону\n"
         "важеля через центр ваги. Правило стає теоремою."),
        ("≈340 н.е.", MUTED, "#f4f6f8",
         "Папп записує «дайте точку опори — і зрушу Землю».\n"
         "Переказ через 500 років — легенда, не прямий доказ."),
        ("XIII ст.", INK, "#f4f6f8",
         "«Наука про ваги» (Йордан Неморарій): важіль через\n"
         "уявні переміщення. Латина вживає momentum."),
        ("≈1600", INK, "#f4f6f8",
         "Галілей робить momento терміном — статичний момент,\n"
         "добуток ваги на відстань (M = F · d)."),
        ("1811", NEG, "#eef2fb",
         "«Момент сили» усталюється в механіці\n"
         "(Пуассон, «Трактат з механіки»)."),
        ("1884", POS, "#fdecea",
         "Джеймс Томсон пропонує слово «torque»; того ж року\n"
         "його вживає Сілванус Томпсон. Друге ім'я величини."),
    ]

    box_x, box_w, box_h = 210, 640, 72
    for i, (yr, col, tint) in enumerate([(r[0], r[1], r[2]) for r in rows]):
        y = y0 + i * step
        desc = rows[i][3]
        # рік — ліворуч від осі
        f.append(text(spine_x - 26, y + 5, yr, size=14, bold=True, color=col,
                      anchor="end"))
        # конектор вісь → рамка
        f.append(line(spine_x, y, box_x, y, color=col, sw=1.6))
        # вузол на осі
        f.append(circle(spine_x, y, 9, fill=tint, stroke=col, sw=2.6))
        # опис у рамці
        f.append(fitbox(box_x, y - box_h / 2, box_w, box_h, desc, size=14, pad=10,
                        fill=tint, stroke=col, sw=1.4, color=INK))

    return render(os.path.join(IMG, "history-timeline.svg"), W, H, *f)


# ── Фігура 6: внутрішні моменти гасяться попарно (для math-вставки) ───────────
def fig_internal_cancel():
    W, H = 800, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Внутрішні моменти пари сил гасяться відносно будь-якої осі",
                  size=17, bold=True))

    O = (120, 355)
    Pi = (515, 150)     # частинка i
    Pj = (605, 300)     # частинка j

    # лінія центрів (через i та j, продовжена пунктиром)
    dx, dy = Pj[0] - Pi[0], Pj[1] - Pi[1]
    Lc = math.hypot(dx, dy); ux, uy = dx / Lc, dy / Lc
    ext = 66
    f.append(line(Pi[0] - ux * ext, Pi[1] - uy * ext,
                  Pj[0] + ux * ext, Pj[1] + uy * ext,
                  color=MUTED, sw=1.2, dash="6 5"))
    f.append(text(Pj[0] + ux * ext + 6, Pj[1] + uy * ext + 4, "лінія центрів",
                  size=12, color=MUTED, anchor="start"))

    # радіус-вектори з O
    f.append(arrow(O[0], O[1], Pi[0], Pi[1], color=MUTED, sw=1.8))
    f.append(arrow(O[0], O[1], Pj[0], Pj[1], color=MUTED, sw=1.8))
    f.append(text((O[0] + Pi[0]) / 2 - 6, (O[1] + Pi[1]) / 2 - 10, "rᵢ",
                  size=15, italic=True, color=MUTED, anchor="end"))
    f.append(text((O[0] + Pj[0]) / 2 + 4, (O[1] + Pj[1]) / 2 + 26, "rⱼ",
                  size=15, italic=True, color=MUTED, anchor="start"))
    f.append(circle(O[0], O[1], 8, fill=FILL, stroke=INK, sw=2))
    f.append(text(O[0] - 4, O[1] + 28, "O", size=13, color=MUTED))

    # сили вздовж лінії центрів — рівні й протилежні
    fl = 84
    f.append(arrow(Pi[0], Pi[1], Pi[0] - ux * fl, Pi[1] - uy * fl, color=POS, sw=3.1))
    f.append(text(Pi[0] - ux * fl - 8, Pi[1] - uy * fl - 6, "fᵢⱼ",
                  size=16, bold=True, color=POS, anchor="end"))
    f.append(arrow(Pj[0], Pj[1], Pj[0] + ux * fl, Pj[1] + uy * fl, color=NEG, sw=3.1))
    f.append(text(Pj[0] + ux * fl + 8, Pj[1] + uy * fl + 8, "fⱼᵢ = −fᵢⱼ",
                  size=16, bold=True, color=NEG, anchor="start"))

    f.append(circle(Pi[0], Pi[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(text(Pi[0] + 12, Pi[1] - 4, "i", size=15, bold=True, anchor="start"))
    f.append(circle(Pj[0], Pj[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(text(Pj[0] - 12, Pj[1] + 18, "j", size=15, bold=True, anchor="end"))

    b, w, h = textbox(W / 2, H - 34,
                      "rᵢ×fᵢⱼ + rⱼ×fⱼᵢ = (rᵢ − rⱼ)×fᵢⱼ = 0     (сила ∥ лінії центрів)",
                      size=14, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "internal-torque-cancel.svg"), W, H, *f)


# ── Фігура 7: момент інерції стрижня — сума mᵢρᵢ² → інтеграл (для math-вставки) ─
def fig_rod_inertia():
    W, H = 820, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Момент інерції: сума  mᵢ·ρᵢ²  стає інтегралом  ∫ρ²dm",
                  size=17, bold=True))

    x0, x1 = 200, 660
    yr = 165
    th = 26
    # стрижень
    f.append(rect(x0, yr - th / 2, x1 - x0, th, fill="#eef2fb", stroke=INK, sw=1.8, rx=5))
    # вісь на лівому кінці (вертикаль)
    f.append(line(x0, yr - 92, x0, yr + 78, color=NEG, sw=2.4, dash="6 5"))
    f.append(text(x0, yr - 100, "вісь (на кінці)", size=13, color=NEG))
    # представницька смужка dm
    xs = x0 + 0.74 * (x1 - x0)
    f.append(rect(xs - 7, yr - th / 2, 14, th, fill=FIELD, stroke=INK, sw=1.4, rx=2))
    f.append(text(xs, yr - th / 2 - 9, "dm", size=13, color=FIELD, bold=True))
    # розмірна лінія ρ = x від осі до смужки
    dl = yr + 58
    f.append(line(x0, dl, xs, dl, color=MUTED, sw=1.2))
    f.append(line(x0, dl - 6, x0, dl + 6, color=MUTED, sw=1.2))
    f.append(line(xs, dl - 6, xs, dl + 6, color=MUTED, sw=1.2))
    f.append(text((x0 + xs) / 2, dl - 9, "ρ", size=15, italic=True, color=MUTED))
    # позначки кінців
    f.append(text(x0 - 8, yr + 5, "0", size=13, color=MUTED, anchor="end"))
    f.append(text(x1 + 8, yr + 5, "L", size=13, color=MUTED, anchor="start"))

    # два результати
    b1, w1, h1 = textbox(280, H - 78, "вісь на кінці:\nJ = M·L² / 3",
                         size=15, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b1)
    b2, w2, h2 = textbox(560, H - 78, "вісь по центру:\nJ = M·L² / 12",
                         size=15, pad=11, fill="#eef2fb", stroke=NEG, sw=1.3, bold=True)
    f.append(b2)
    b3, w3, h3 = textbox(W / 2, H - 24,
                         "J = Σ mᵢ·ρᵢ²  →  ∫ ρ² dm     (ρ — відстань смужки до осі, у квадраті)",
                         size=13, pad=9, fill=FILL, stroke=LINE, sw=1.2, bold=False)
    f.append(b3)
    return render(os.path.join(IMG, "rod-inertia.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_lever(), fig_vector(), fig_seesaw(), fig_couple(), fig_timeline(),
          fig_internal_cancel(), fig_rod_inertia()]
    print("written:")
    for p in ps:
        print("  ", p)
