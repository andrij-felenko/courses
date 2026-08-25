# -*- coding: utf-8 -*-
"""Фігури до теми «Взаємна інформація» (mutual-information).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def Hbin(p):
    if p <= 0 or p >= 1:
        return 0.0
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


# ── 1. Взаємна інформація = скорочення невизначеності: I = H(X) − H(X|Y) ──────
# Ідея: невизначеність про X до Y (повний стовпчик) ділиться після погляду на Y
# на збиту частину I(X;Y) та залишок H(X|Y). Приклад-числа з BSC: 0.53 і 0.47.
def fig_uncertainty_drop():
    W, H = 780, 430
    f = []
    base = 350
    scale = 232.0            # 1 біт = 232 px
    top = base - scale
    bw = 96

    # ── ліворуч: уся невизначеність до Y ──
    xL = 176
    f.append(rect(xL, top, bw, scale, fill="#dbe4fb", stroke=NEG, sw=1.9))
    f.append(text(xL + bw / 2, (top + base) / 2 + 5, "H(X)", 15, NEG, "middle", bold=True))
    f.append(text(xL + bw / 2, base + 24, "до Y", 12, INK, "middle", bold=True))
    f.append(text(xL + bw / 2, base + 42, "уся невизначеність = 1 біт", 10, MUTED, "middle"))

    # ── стрілка «показали Y» ──
    f.append(arrow(xL + bw + 16, top + 24, 452, top + 24, color=INK, sw=2.0))
    f.append(text((xL + bw + 16 + 452) / 2, top + 12, "показали Y", 11.5, INK, "middle", bold=True))

    # ── праворуч: той самий стовпчик, поділений ──
    xR = 468
    hI = 0.531 * scale       # збито
    hR = 0.469 * scale       # лишилось
    yI = top
    yR = top + hI
    f.append(rect(xR, yI, bw, hI, fill="#eef6ef", stroke=FIELD, sw=1.9))
    f.append(rect(xR, yR, bw, hR, fill="#eef0f2", stroke=MUTED, sw=1.9))
    f.append(text(xR + bw / 2, base + 24, "після Y", 12, INK, "middle", bold=True))

    # виносні підписи двох частин праворуч
    f.append(line(xR + bw, yI + hI / 2, 600, yI + hI / 2, color=FIELD, sw=1.3))
    f.append(text(608, yI + hI / 2 - 6, "I(X;Y) ≈ 0.53 біта", 12, FIELD, "start", bold=True))
    f.append(text(608, yI + hI / 2 + 12, "це Y розповів про X", 10, MUTED, "start"))

    f.append(line(xR + bw, yR + hR / 2, 600, yR + hR / 2, color=MUTED, sw=1.3))
    f.append(text(608, yR + hR / 2 - 6, "H(X|Y) ≈ 0.47 біта", 12, INK, "start", bold=True))
    f.append(text(608, yR + hR / 2 + 12, "залишок непевності", 10, MUTED, "start"))

    # підсумкова тотожність унизу
    f.append(text(W / 2, 412, "H(X)  =  I(X;Y)  +  H(X|Y)", 13.5, INK, "middle", bold=True))
    render(os.path.join(IMG, "uncertainty-drop.svg"), W, H, *f,
           title="Взаємна інформація — скільки невизначеності про X збиває погляд на Y")


# ── 2. Діаграма Венна: перекриття двох ентропій ───────────────────────────────
# Ідея: круг H(X) і круг H(Y) налягають; лінза — I(X;Y); місяці — H(X|Y), H(Y|X);
# уся площа — спільна ентропія H(X,Y).
def fig_venn():
    W, H = 780, 470
    f = []
    cyc = 250
    r = 152
    cxL, cxR = 300, 480       # центри; відстань 180 → лінза завширшки 124 px

    # круги з напівпрозорою заливкою — перекриття само проступає
    f.append('<circle cx="%d" cy="%d" r="%d" fill="#d7e2fb" fill-opacity="0.78" '
             'stroke="%s" stroke-width="2"/>' % (cxL, cyc, r, NEG))
    f.append('<circle cx="%d" cy="%d" r="%d" fill="#fbdbd6" fill-opacity="0.62" '
             'stroke="%s" stroke-width="2"/>' % (cxR, cyc, r, POS))

    # заголовки кругів — над ними, осторонь
    f.append(text(cxL - 78, cyc - r - 10, "H(X) — вхід", 13, NEG, "middle", bold=True))
    f.append(text(cxR + 78, cyc - r - 10, "H(Y) — вихід", 13, POS, "middle", bold=True))

    # підписи трьох областей (по вертикалі центрів)
    f.append(text(cxL - 74, cyc - 6, "H(X|Y)", 15, INK, "middle", bold=True))
    f.append(text(cxL - 74, cyc + 14, "лише X", 10, MUTED, "middle"))

    f.append(text((cxL + cxR) / 2, cyc - 6, "I(X;Y)", 15.5, FIELD, "middle", bold=True))
    f.append(text((cxL + cxR) / 2, cyc + 14, "спільне", 10, INK, "middle"))

    f.append(text(cxR + 74, cyc - 6, "H(Y|X)", 15, INK, "middle", bold=True))
    f.append(text(cxR + 74, cyc + 14, "шум", 10, MUTED, "middle"))

    # нижній підпис: уся площа = спільна ентропія
    f.append(line(cxL - r + 20, cyc + r + 18, cxR + r - 20, cyc + r + 18, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(W / 2, cyc + r + 40, "уся площа обох кругів = спільна ентропія H(X,Y)", 12, INK, "middle", bold=True))
    f.append(text(W / 2, cyc + r + 58, "I(X;Y) = H(X) + H(Y) − H(X,Y)", 12.5, FIELD, "middle", bold=True))
    render(os.path.join(IMG, "venn.svg"), W, H, *f,
           title="Взаємна інформація — перекриття двох невизначеностей")


# ── 3. Двійковий симетричний канал + крива I = 1 − H(p) від рівня шуму ─────────
# Ідея: канал перевертає біт із p; з 1 біта шум забирає H(p), решта проходить.
# Праворуч — як частка, що проходить, тане до нуля при p=½.
def fig_bsc_worked():
    W, H = 900, 440
    f = []

    # ── ліва панель: сам канал ──
    xin, xout = 150, 330
    y0, y1 = 172, 302
    r = 22
    f.append(text(xin, 118, "вхід X", 12.5, INK, "middle", bold=True))
    f.append(text(xout, 118, "вихід Y", 12.5, INK, "middle", bold=True))

    # прямі (біт вцілів) — зелені
    f.append(arrow(xin + r, y0, xout - r, y0, color=FIELD, sw=2.1))
    f.append(arrow(xin + r, y1, xout - r, y1, color=FIELD, sw=2.1))
    f.append(text((xin + xout) / 2, y0 - 12, "1 − p", 11.5, FIELD, "middle", bold=True))
    f.append(text((xin + xout) / 2, y1 + 22, "1 − p", 11.5, FIELD, "middle", bold=True))

    # перехресні (переворот) — червоні
    f.append(arrow(xin + r - 4, y0 + 14, xout - r + 4, y1 - 14, color=POS, sw=2.0))
    f.append(arrow(xin + r - 4, y1 - 14, xout - r + 4, y0 + 14, color=POS, sw=2.0))
    f.append(text(xin + 32, y0 + 44, "p", 12.5, POS, "middle", bold=True))
    f.append(text(xin + 32, y1 - 44, "p", 12.5, POS, "middle", bold=True))

    # вузли поверх ліній
    for (x, y, s) in [(xin, y0, "0"), (xin, y1, "1"), (xout, y0, "0"), (xout, y1, "1")]:
        f.append(circle(x, y, r, fill=BG, stroke=INK, sw=1.9))
        f.append(text(x, y + 6, s, 16, INK, "middle", bold=True))

    f.append(text((xin + xout) / 2, 360, "з 1 біта шум забирає H(p),", 11, MUTED, "middle"))
    f.append(text((xin + xout) / 2, 377, "решта 1 − H(p) проходить", 11, MUTED, "middle"))

    # ── права панель: крива I(p) = 1 − H(p) ──
    ox, oy = 540, 358
    aw, ah = 318, 252
    ymax = 1.06

    def px(p): return ox + p * aw
    def py(v): return oy - (v / ymax) * ah

    # осі
    f.append(line(ox, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    f.append(arrow(ox + aw, oy, ox + aw + 20, oy, color=INK, sw=1.6))
    f.append(line(ox, oy + 4, ox, oy - ah - 4, color=INK, sw=1.6))
    f.append(arrow(ox, oy - ah, ox, oy - ah - 20, color=INK, sw=1.6))
    f.append(text(ox + aw / 2, oy + 40, "ймовірність перевороту p", 11, INK, "middle", bold=True))

    # вертикальний підпис осі I
    f.append('<text x="%d" y="%d" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 %d %d)">%s</text>'
             % (ox - 44, oy - ah / 2, FONT, INK, ox - 44, oy - ah / 2, esc("I(X;Y), біт/символ")))

    for p, lab in [(0.0, "0"), (0.25, "0.25"), (0.5, "0.5"), (0.75, "0.75"), (1.0, "1")]:
        f.append(line(px(p), oy, px(p), oy + 5, color=INK, sw=1.2))
        f.append(text(px(p), oy + 20, lab, 10, MUTED, "middle"))
    for v in [0.0, 0.5, 1.0]:
        f.append(line(ox - 5, py(v), ox, py(v), color=INK, sw=1.2))
        f.append(text(ox - 9, py(v) + 4, ("%.1f" % v).rstrip('0').rstrip('.'), 10, MUTED, "end"))
        if v:
            f.append(line(ox, py(v), ox + aw, py(v), color="#eef0f2", sw=1))

    # крива I = 1 − H(p)
    pts = ["%.1f,%.1f" % (px(0.0), py(1.0))]
    p = 0.004
    while p <= 0.9961:
        pts.append("%.1f,%.1f" % (px(p), py(1.0 - Hbin(p))))
        p += 0.004
    pts.append("%.1f,%.1f" % (px(1.0), py(1.0)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), NEG))

    # опорна точка p=0.1 → 0.531
    f.append(circle(px(0.1), py(0.531), 4.6, fill=POS, stroke=POS, sw=0))
    f.append(text(px(0.1) + 12, py(0.531) - 8, "p=0.1 → 0.53 біта", 10.5, POS, "start", bold=True))
    # дно при p=½
    f.append(circle(px(0.5), py(0.0), 4.6, fill=MUTED, stroke=MUTED, sw=0))
    f.append(text(px(0.5), py(0.0) - 14, "p=½ → 0: канал глухне", 10.5, MUTED, "middle", bold=True))
    render(os.path.join(IMG, "bsc-worked.svg"), W, H, *f,
           title="Скільки біт проходить крізь канал, що перевертає біти")


# ── 4. Угнутість log і нерівність Єнсена — двигун невід'ємності D ≥ 0 ──────────
# Ідея: log₂ угнутий, тож хорда між двома точками лежить НИЖЧЕ кривої. Звідси
# E[log t] ≤ log E[t]; підстав t = q/p → −D ≤ log 1 = 0 → D ≥ 0.
def fig_jensen_concavity():
    W, H = 860, 512
    f = []
    ox, oy0 = 158, 236            # ox — вісь f; oy0 — піксель рівня v=0
    aw = 600
    tmin, tmax = 0.5, 5.0
    vscale = 80.0                 # px на одиницю log₂

    def px(t): return ox + (t - tmin) / (tmax - tmin) * aw

    def py(v): return oy0 - v * vscale

    ytop = py(2.32) - 12
    ybot = py(-1.15)
    # осі
    f.append(line(ox, ybot, ox, ytop + 8, color=INK, sw=1.6))
    f.append(arrow(ox, ytop + 8, ox, ytop - 12, color=INK, sw=1.6))
    f.append(line(ox - 8, oy0, ox + aw + 12, oy0, color=INK, sw=1.6))
    f.append(arrow(ox + aw, oy0, ox + aw + 20, oy0, color=INK, sw=1.6))
    f.append(text(ox + aw + 8, oy0 + 22, "t", 13, INK, "middle", bold=True))
    f.append(text(ox - 12, ytop + 2, "log₂ t", 13, INK, "end", bold=True))

    # крива log₂ t
    pts, t = [], tmin
    while t <= tmax + 1e-9:
        pts.append("%.1f,%.1f" % (px(t), py(math.log2(t))))
        t += 0.02
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), NEG))
    f.append(text(px(4.55), py(math.log2(4.55)) - 16, "log₂ — угнутий", 12.5, NEG, "middle", bold=True))

    # дві точки й хорда під кривою
    t1, t2 = 0.7, 4.4
    v1, v2 = math.log2(t1), math.log2(t2)
    xb = (t1 + t2) / 2.0          # E[t] за рівних ваг
    vcurve = math.log2(xb)        # log₂ E[t]  (на кривій, вище)
    vchord = (v1 + v2) / 2.0      # E[log₂ t]  (на хорді, нижче)

    f.append(line(px(t1), py(v1), px(t2), py(v2), color=MUTED, sw=1.9, dash="6 4"))
    for (tt, vv, lab) in [(t1, v1, "t₁"), (t2, v2, "t₂")]:
        yend = py(vv)
        f.append(line(px(tt), oy0, px(tt), yend, color="#c9d3e8", sw=1, dash="3 3"))
        f.append(circle(px(tt), yend, 4.6, fill=NEG, stroke=BG, sw=1.3))
        ylab = oy0 + 20 if vv >= 0 else yend + 18
        f.append(text(px(tt), ylab, lab, 12.5, INK, "middle", bold=True))

    # вертикаль при E[t]
    f.append(line(px(xb), oy0, px(xb), py(vcurve), color=INK, sw=1.1, dash="3 3"))
    f.append(text(px(xb), oy0 + 20, "E[t]", 12.5, INK, "middle", bold=True))

    # дві ключові точки
    f.append(circle(px(xb), py(vcurve), 5.4, fill=FIELD, stroke=BG, sw=1.6))
    f.append(circle(px(xb), py(vchord), 5.4, fill=POS, stroke=BG, sw=1.6))
    f.append(text(px(xb) + 14, py(vcurve) - 4, "log₂ E[t]", 12.5, FIELD, "start", bold=True))
    f.append(text(px(xb) + 14, py(vchord) + 16, "E[log₂ t]", 12.5, POS, "start", bold=True))

    # розрив Єнсена — двобічна стрілка ліворуч від вертикалі
    gx = px(xb) - 20
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.7" '
             'marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
             % (gx, py(vcurve), gx, py(vchord), INK))
    f.append(text(gx - 10, (py(vcurve) + py(vchord)) / 2 + 4, "розрив", 11, INK, "end", bold=True))

    # підсумок-punchline унизу
    f.append(text(W / 2, H - 52, "Нерівність Єнсена:   E[log₂ t]  ≤  log₂ E[t]     (бо log₂ угнутий)",
                  13, INK, "middle", bold=True))
    f.append(text(W / 2, H - 28,
                  "підстав t = q/p :   −D = E[log₂(q/p)] ≤ log₂ E[q/p] = log₂ 1 = 0   ⟹   D ≥ 0",
                  12.5, FIELD, "middle", bold=True))
    render(os.path.join(IMG, "jensen-concavity.svg"), W, H, *f,
           title="Чому взаємна інформація невід'ємна: угнутість логарифма")


# ── 5. Ємність як пік: I(X;Y) двійкового каналу від вхідного розподілу q ───────
# Ідея: канал (крос p) фіксований; вільний важіль — розподіл входу q=P(X=1).
# I(q)=H(r)−H(p), r=q(1−p)+(1−q)p — угнутий горб, пік при q=½ → C=1−H(p).
def fig_capacity_hump():
    W, H = 660, 470
    f = []
    p = 0.1
    Hp = Hbin(p)
    C = 1.0 - Hp
    ox, oy = 132, 372
    aw, ah = 452, 300
    imax = 0.62

    def px(q): return ox + q * aw

    def py(v): return oy - (v / imax) * ah

    # осі
    f.append(line(ox, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    f.append(arrow(ox + aw, oy, ox + aw + 20, oy, color=INK, sw=1.6))
    f.append(line(ox, oy + 4, ox, oy - ah - 6, color=INK, sw=1.6))
    f.append(arrow(ox, oy - ah, ox, oy - ah - 20, color=INK, sw=1.6))
    f.append(text(ox + aw / 2, oy + 44, "розподіл входу   q = P(X=1)", 12, INK, "middle", bold=True))
    f.append('<text x="%d" y="%d" font-family="%s" font-size="11.5" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 %d %d)">%s</text>'
             % (ox - 42, oy - ah / 2, FONT, INK, ox - 42, oy - ah / 2, esc("I(X;Y), біт/символ")))

    for q, lab in [(0.0, "0"), (0.25, "¼"), (0.5, "½"), (0.75, "¾"), (1.0, "1")]:
        f.append(line(px(q), oy, px(q), oy + 5, color=INK, sw=1.2))
        f.append(text(px(q), oy + 20, lab, 11, MUTED, "middle"))
    for v in [0.0, 0.2, 0.4, 0.6]:
        f.append(line(ox - 5, py(v), ox, py(v), color=INK, sw=1.2))
        f.append(text(ox - 9, py(v) + 4, ("%.1f" % v), 10, MUTED, "end"))
        if v:
            f.append(line(ox, py(v), ox + aw, py(v), color="#eef0f2", sw=1))

    # рівень ємності C
    f.append(line(ox, py(C), px(0.5), py(C), color=MUTED, sw=1.2, dash="5 4"))
    f.append(text(ox + 6, py(C) - 7, "C = 1 − H(p) ≈ 0.53", 11, MUTED, "start", bold=True))

    # крива I(q) = H(r) − H(p)
    pts, q = [], 0.0
    while q <= 1.0001:
        r = q * (1 - p) + (1 - q) * p
        Iq = max(0.0, Hbin(r) - Hp)
        pts.append("%.1f,%.1f" % (px(q), py(Iq)))
        q += 0.004
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), NEG))

    # пік при q=½
    f.append(line(px(0.5), oy, px(0.5), py(C), color=POS, sw=1.1, dash="3 3"))
    f.append(circle(px(0.5), py(C), 5.2, fill=POS, stroke=BG, sw=1.4))
    f.append(text(px(0.5), py(C) - 14, "q = ½   →   пік = C", 12, POS, "middle", bold=True))

    # нульові кінці
    f.append(circle(px(0.0), py(0.0), 4.4, fill=MUTED, stroke=BG, sw=1.2))
    f.append(circle(px(1.0), py(0.0), 4.4, fill=MUTED, stroke=BG, sw=1.2))
    f.append(text(px(0.30), py(0.045) - 4, "детермінований вхід → I = 0", 10.5, MUTED, "middle", bold=True))
    render(os.path.join(IMG, "capacity-hump.svg"), W, H, *f,
           title="Ємність — це пік взаємної інформації по вхідному розподілу")


# ── 6. Зсув плаг-ін оцінки: незалежні дані дають фальшиву I, ММ її гасить ──────
# Ідея: X,Y НЕЗАЛЕЖНІ (K=16 символів), істинна I = 0. Наївна плаг-ін оцінка
# з гістограми повзе за законом (K−1)²/(2N·ln2) — біти з нізвідки; поправка
# Міллера–Мадоу тримається коло нуля, щойно вибірка перестає бути надто рідкою.
def fig_proj_mi_bias():
    W, H = 880, 470
    f = []
    ox, oy = 132, 384
    aw, ah = 656, 300
    xlo, xhi = 7.3, 14.0          # вісь log₂ N
    ymax = 1.0
    # (N, plug-in, ММ) — середнє по 400 повторах, K=16, істинне I = 0
    data = [(200, 0.9097, 0.5186), (400, 0.4792, 0.1700), (800, 0.2235, 0.0306),
            (1600, 0.1047, 0.0035), (3200, 0.0516, 0.0009), (6400, 0.0255, 0.0001),
            (12800, 0.0127, 0.0001)]

    def px(N): return ox + (math.log2(N) - xlo) / (xhi - xlo) * aw

    def py(v): return oy - (v / ymax) * ah

    # осі
    f.append(line(ox, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    f.append(arrow(ox + aw, oy, ox + aw + 20, oy, color=INK, sw=1.6))
    f.append(line(ox, oy + 4, ox, oy - ah - 6, color=INK, sw=1.6))
    f.append(arrow(ox, oy - ah, ox, oy - ah - 20, color=INK, sw=1.6))
    f.append(text(ox + aw / 2, oy + 44, "розмір вибірки N   (вісь log₂)", 12, INK, "middle", bold=True))
    f.append('<text x="%d" y="%d" font-family="%s" font-size="11.5" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 %d %d)">%s</text>'
             % (ox - 46, oy - ah / 2, FONT, INK, ox - 46, oy - ah / 2, esc("оцінена I(X;Y), біт")))

    for N in [200, 800, 3200, 12800]:
        f.append(line(px(N), oy, px(N), oy + 5, color=INK, sw=1.2))
        f.append(text(px(N), oy + 20, str(N), 10.5, MUTED, "middle"))
    for v in [0.0, 0.25, 0.5, 0.75, 1.0]:
        f.append(line(ox - 5, py(v), ox, py(v), color=INK, sw=1.2))
        f.append(text(ox - 9, py(v) + 4, ("%.2f" % v), 10, MUTED, "end"))
        if v:
            f.append(line(ox, py(v), ox + aw, py(v), color="#eef0f2", sw=1))

    # істина I = 0 — жирна лінія по осі
    f.append(text(ox + aw - 4, py(0.0) - 8, "істина: I = 0", 11, FIELD, "end", bold=True))

    # теоретична крива зсуву (K−1)²/(2N·ln2)
    pts, N = [], 190.0
    while N <= 13200:
        b = (15 * 15) / (2 * N * math.log(2))
        pts.append("%.1f,%.1f" % (px(N), py(b)))
        N *= 1.03
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="6 4"/>'
             % (" ".join(pts), MUTED))

    # плаг-ін (синє) і ММ (зелене)
    pl = " ".join("%.1f,%.1f" % (px(N), py(v)) for (N, v, _) in data)
    mm = " ".join("%.1f,%.1f" % (px(N), py(m)) for (N, _, m) in data)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pl, NEG))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (mm, FIELD))
    for (N, v, m) in data:
        f.append(circle(px(N), py(v), 4.4, fill=NEG, stroke=BG, sw=1.3))
        f.append(circle(px(N), py(m), 4.4, fill=FIELD, stroke=BG, sw=1.3))

    # виноска на найгіршій точці
    f.append(text(px(200) + 10, py(0.9097) + 2, "0.91 біта з чистого шуму!", 11, NEG, "start", bold=True))

    # легенда
    lx, ly = ox + aw - 250, oy - ah + 8
    f.append(rect(lx, ly, 250, 74, fill="#ffffff", stroke=MUTED, sw=1.1))
    f.append(line(lx + 14, ly + 20, lx + 40, ly + 20, color=NEG, sw=2.6))
    f.append(circle(lx + 27, ly + 20, 4.2, fill=NEG, stroke=BG, sw=1.2))
    f.append(text(lx + 48, ly + 24, "плаг-ін (наївна)", 11, INK, "start", bold=True))
    f.append(line(lx + 14, ly + 40, lx + 40, ly + 40, color=FIELD, sw=2.6))
    f.append(circle(lx + 27, ly + 40, 4.2, fill=FIELD, stroke=BG, sw=1.2))
    f.append(text(lx + 48, ly + 44, "поправка Міллера–Мадоу", 11, INK, "start", bold=True))
    f.append(line(lx + 14, ly + 60, lx + 40, ly + 60, color=MUTED, sw=1.8, dash="6 4"))
    f.append(text(lx + 48, ly + 64, "теорія  (K−1)²/(2N·ln2)", 11, INK, "start", bold=True))
    render(os.path.join(IMG, "proj-mi-bias.svg"), W, H, *f,
           title="Зсув наївної оцінки: біти з нізвідки й поправка на них")


# ── 7. Blahut–Arimoto: дві межі стискаються на ємність C ──────────────────────
# Ідея: за ітерацій нижня межа Σ r·Dₓ (поточна I) росте, верхня maxₓ Dₓ спадає;
# їхній розрив — гарантована похибка, і обидві сходяться на C. Z-канал, p=0.3.
def fig_proj_ba_convergence():
    W, H = 820, 462
    f = []
    ox, oy = 120, 372
    aw, ah = 620, 288
    ylo, yhi = 0.48, 0.64
    C = 0.5037
    # (ітерація, нижня IL, верхня IU)
    data = [(1, 0.4934, 0.6215), (2, 0.5017, 0.5543), (3, 0.5033, 0.5253),
            (4, 0.5036, 0.5129), (5, 0.5037, 0.5076), (6, 0.5037, 0.5054),
            (7, 0.5037, 0.5044), (8, 0.5037, 0.5040), (9, 0.5037, 0.5038),
            (10, 0.5037, 0.5037)]

    def px(i): return ox + (i - 1) / 9.0 * aw

    def py(v): return oy - (v - ylo) / (yhi - ylo) * ah

    # осі
    f.append(line(ox, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    f.append(arrow(ox + aw, oy, ox + aw + 20, oy, color=INK, sw=1.6))
    f.append(line(ox, oy + 4, ox, oy - ah - 6, color=INK, sw=1.6))
    f.append(arrow(ox, oy - ah, ox, oy - ah - 20, color=INK, sw=1.6))
    f.append(text(ox + aw / 2, oy + 42, "номер ітерації", 12, INK, "middle", bold=True))
    f.append('<text x="%d" y="%d" font-family="%s" font-size="11.5" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 %d %d)">%s</text>'
             % (ox - 48, oy - ah / 2, FONT, INK, ox - 48, oy - ah / 2, esc("біт/символ")))

    for i in range(1, 11):
        f.append(line(px(i), oy, px(i), oy + 5, color=INK, sw=1.2))
        f.append(text(px(i), oy + 20, str(i), 10.5, MUTED, "middle"))
    for v in [0.48, 0.52, 0.56, 0.60, 0.64]:
        f.append(line(ox - 5, py(v), ox, py(v), color=INK, sw=1.2))
        f.append(text(ox - 9, py(v) + 4, "%.2f" % v, 10, MUTED, "end"))
        if abs(v - 0.48) > 1e-9:
            f.append(line(ox, py(v), ox + aw, py(v), color="#eef0f2", sw=1))

    # рівень ємності
    f.append(line(ox, py(C), ox + aw, py(C), color=FIELD, sw=1.6, dash="6 4"))
    f.append(text(ox + aw - 4, py(C) + 18, "ємність C = 0.5037", 11.5, FIELD, "end", bold=True))

    up = " ".join("%.1f,%.1f" % (px(i), py(u)) for (i, _, u) in data)
    lo = " ".join("%.1f,%.1f" % (px(i), py(l)) for (i, l, _) in data)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (up, POS))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (lo, NEG))
    for (i, l, u) in data:
        f.append(circle(px(i), py(u), 4.2, fill=POS, stroke=BG, sw=1.2))
        f.append(circle(px(i), py(l), 4.2, fill=NEG, stroke=BG, sw=1.2))

    # підписи двох меж
    f.append(text(px(4) + 6, py(0.5129) - 24, "верхня: maxₓ Dₓ  ≥  C", 11.5, POS, "start", bold=True))
    f.append(text(px(4) + 6, py(0.5036) + 20, "нижня: Σ r·Dₓ  ≤  C   (поточна I)", 11.5, NEG, "start", bold=True))

    # розрив = гарантована похибка (на ітерації 2)
    gi = 2
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.7" '
             'marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
             % (px(gi) - 22, py(0.5543), px(gi) - 22, py(0.5017), INK))
    f.append(text(px(gi) - 30, (py(0.5543) + py(0.5017)) / 2 + 4, "розрив =", 10.5, INK, "end", bold=True))
    f.append(text(px(gi) - 30, (py(0.5543) + py(0.5017)) / 2 + 18, "похибка", 10.5, INK, "end", bold=True))
    render(os.path.join(IMG, "proj-ba-convergence.svg"), W, H, *f,
           title="Blahut–Arimoto: верхня й нижня межі стискаються на ємність")


# ── Одна величина, дві назви: Шеннон 1948 → Фано 1961 (для hist-naming) ────────
# Ідея: та сама величина спершу звалась «швидкість передавання» R = H(x)−H_y(x)
# (погляд із боку відправника), а Фано назвав її «взаємною інформацією» I(X;Y),
# і крапка з комою показує симетрію, що вже ховалась у формулі.
def fig_two_names():
    W, H = 880, 270
    f = []

    cxL, cxR = 215, 665

    # заголовки-роки над рамками (вільний текст, не в рамці)
    f.append(text(cxL, 80, "1948 · Клод Шеннон", 14, NEG, "middle", bold=True))
    f.append(text(cxR, 80, "1961 · Роберт Фано", 14, FIELD, "middle", bold=True))

    # рамки з формулами — через fitbox (текст у рамці)
    f.append(fitbox(90, 100, 250, 54, "R = H(x) − H_y(x)",
                    size=17, bold=True, fill="#dbe4fb", stroke=NEG, color=INK))
    f.append(fitbox(540, 100, 250, 54, "I(X;Y) = I(Y;X)",
                    size=17, bold=True, fill="#e5f3ea", stroke=FIELD, color=INK))

    # стрілка переходу між рамками (у проміжку, повз написи)
    f.append(arrow(345, 127, 535, 127, color=INK, sw=2.2))
    f.append(text(440, 115, "13 років", 12, INK, "middle", bold=True))
    f.append(text(440, 143, "та сама величина", 10.5, MUTED, "middle"))

    # підписи-назви під рамками
    f.append(text(cxL, 178, "«швидкість передавання»", 12.5, MUTED, "middle"))
    f.append(text(cxL, 196, "потік крізь канал", 10.5, MUTED, "middle"))
    f.append(text(cxR, 178, "«взаємна інформація»", 12.5, MUTED, "middle"))
    f.append(text(cxR, 196, "зв'язок між двома величинами", 10.5, MUTED, "middle"))

    # підсумок унизу
    f.append(text(W / 2, 236, "Крапка з комою в I(X;Y) виставляє напоказ симетрію, "
                              "приховану у формулі Шеннона", 12, INK, "middle", bold=True))
    render(os.path.join(IMG, "two-names.svg"), W, H, *f,
           title="Одна величина, дві назви — «швидкість передавання» і «взаємна інформація»")


if __name__ == "__main__":
    fig_uncertainty_drop()
    fig_venn()
    fig_bsc_worked()
    fig_jensen_concavity()
    fig_capacity_hump()
    fig_proj_mi_bias()
    fig_proj_ba_convergence()
    fig_two_names()
    print("OK: figures written to", IMG)
