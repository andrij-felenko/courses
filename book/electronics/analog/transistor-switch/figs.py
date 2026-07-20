# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: площина ключа — холодні кути, гаряча середина ───────────────────
def fig_switch_plane():
    W, H = 820, 470
    parts = []
    parts.append(text(W / 2, 30, "Площина ключа: холодні кути, гаряча середина", size=17, bold=True))

    ox, oy = 130, 380
    ax_w, ax_h = 600, 290
    Umax, Imax = 13.6, 3.5
    E, R = 12.0, 4.0                      # джерело 12 В, навантаження 4 Ω → 3 А

    def px(u): return ox + (u / Umax) * ax_w
    def py(i): return oy - (i / Imax) * ax_h

    # осі (вісь Y трохи нижче верху, щоб лишити місце під підписи)
    parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    parts.append(line(ox, oy, ox, 118, color=INK, sw=2))
    parts.append(text(340, 424, "напруга на ключі U →", size=13, color=INK))
    parts.append(mtext(58, 232, ["струм крізь", "ключ I ↑"], size=12, color=INK))

    # гіпербола сталої потужності U·I = 9 Вт (дотична до навантажувальної прямої)
    Pmax = E * E / (4 * R)                # 9 Вт
    pts = []
    u = 3.4
    while u <= Umax + 0.01:
        pts.append("%.1f,%.1f" % (px(u), py(Pmax / u)))
        u += 0.12
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
                 'stroke-dasharray="6,4"/>' % (" ".join(pts), POS))
    parts.append(text(560, 288, "U·I = 9 Вт", size=12, color=POS))

    # навантажувальна пряма: I = (E − U)/R
    parts.append(line(px(0), py(E / R), px(E), py(0), color=INK, sw=3))

    # ── три точки на прямій ─────────────────────────────────────────────────
    # відкрито (лівий верх)
    parts.append(circle(px(0.2), py(2.95), 6, fill=FIELD, stroke=FIELD))
    b, _, _ = textbox(215, 108, "відкрито:\nU ≈ 0 → P ≈ 0", size=12, color=FIELD, stroke=FIELD)
    parts.append(b)
    # закрито (правий низ, підпис під віссю)
    parts.append(circle(px(E), py(0), 6, fill=MUTED, stroke=MUTED))
    b, _, _ = textbox(655, 420, "закрито:\nI = 0 → P ≈ 0", size=12, color=MUTED, stroke=MUTED)
    parts.append(b)
    # середина — дотик гіперболи
    parts.append(circle(px(6), py(1.5), 6, fill=POS, stroke=POS))
    b, _, _ = textbox(255, 330, "тут максимум:\nP = E²/4R = 9 Вт", size=12, color=POS, stroke=POS)
    parts.append(b)
    parts.append(arrow(322, 316, 388, 262, color=POS))

    # зона над гіперболою
    b, _, _ = textbox(592, 152, "над гіперболою —\nвелика потужність:\nключ тут горить",
                      size=12, color=POS, stroke=POS)
    parts.append(b)

    # стрілка «перехід» уздовж прямої
    parts.append(arrow(px(10.4), py(0.4), px(7.6), py(1.1), color=NEG))
    parts.append(text(px(9.6) + 30, py(0.62) + 26, "перехід — блискавично", size=12, color=NEG))

    render(os.path.join(IMG, 'switch-plane.svg'), W, H, *parts)


# ── Фігура 2: гасити зайве проти кришити й усереднювати ───────────────────────
def fig_linear_vs_switch():
    W, H = 820, 500
    parts = []
    parts.append(text(W / 2, 30, "Одна робота, два способи: спалити різницю чи накришити її",
                      size=17, bold=True))
    parts.append(line(410, 60, 410, 470, color="#dddddd", sw=1.5, dash="5,5"))

    # ── ліворуч: лінійний ──
    lx = 205
    parts.append(text(lx, 66, "гасити зайве", size=15, bold=True, color=POS))
    b, _, _ = textbox(lx, 110, "джерело 12 В", size=12)
    parts.append(b)
    parts.append(arrow(lx, 132, lx, 168, color=LINE))
    b, _, _ = textbox(lx, 200, "прохідний транзистор:\nтримає на собі 7 В\nпри 2 А",
                      size=12, color=POS, stroke=POS)
    parts.append(b)
    parts.append(arrow(lx, 233, lx, 330, color=LINE))
    parts.append(text(lx - 10, 285, "5 В · 2 А", size=12, color=MUTED, anchor="end"))
    # тепло вбік
    parts.append(arrow(lx + 88, 200, lx + 130, 200, color=POS))
    parts.append(mtext(lx + 140, 194, ["14 Вт", "у тепло"], size=13, color=POS, anchor="start", bold=True))
    b, _, _ = textbox(lx, 355, "навантаження\n10 Вт", size=12)
    parts.append(b)
    b, _, _ = textbox(lx, 435, "ККД = 10/24 ≈ 42%", size=13, color=POS, stroke=POS)
    parts.append(b)

    # ── праворуч: ключ ──
    rx = 590
    parts.append(text(rx, 66, "кришити й усереднювати", size=15, bold=True, color=FIELD))
    b, _, _ = textbox(rx, 110, "джерело 12 В", size=12)
    parts.append(b)
    parts.append(arrow(rx, 132, rx, 168, color=LINE))
    b, _, _ = textbox(rx, 200, "ключ: 12 В ↔ 0 В,\nувімкнено частку\nчасу D = 5/12",
                      size=12, color=FIELD, stroke=FIELD)
    parts.append(b)
    parts.append(arrow(rx, 233, rx, 268, color=LINE))
    parts.append(arrow(rx + 88, 200, rx + 130, 200, color=FIELD))
    parts.append(mtext(rx + 140, 194, ["≈0.5 Вт", "у тепло"], size=13, color=FIELD, anchor="start", bold=True))
    b, _, _ = textbox(rx, 300, "фільтр LC:\nусереднює в часі", size=12)
    parts.append(b)
    parts.append(arrow(rx, 333, rx, 330, color=LINE))
    b, _, _ = textbox(rx, 355, "навантаження\n10 Вт", size=12)
    parts.append(b)
    b, _, _ = textbox(rx, 435, "ККД ≈ 95%", size=13, color=FIELD, stroke=FIELD)
    parts.append(b)

    render(os.path.join(IMG, 'linear-vs-switch.svg'), W, H, *parts)


# ── Фігура 3: чотири рахунки реального ключа за один період ───────────────────
def fig_four_costs():
    W, H = 830, 450
    parts = []
    parts.append(text(W / 2, 30, "Чотири рахунки реального ключа за один період", size=17, bold=True))

    ox, oy = 120, 330
    ax_w, ax_h = 620, 230
    parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    parts.append(line(ox, oy, ox, 96, color=INK, sw=2))
    parts.append(mtext(58, 196, ["потужність", "на ключі"], size=12, color=INK))
    parts.append(text(660, 362, "час, один період T →", size=12, color=MUTED))

    def px(t): return ox + t * ax_w
    def py(p): return oy - p * ax_h

    # P(t): витік — сплеск — провідність — сплеск — витік
    pts = [(px(0.00), py(0.012)), (px(0.12), py(0.012)),
           (px(0.15), py(1.00)), (px(0.18), py(0.25)),
           (px(0.62), py(0.25)), (px(0.65), py(1.00)),
           (px(0.68), py(0.012)), (px(1.00), py(0.012))]
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' %
                 (" ".join("%.1f,%.1f" % p for p in pts), POS))

    # 1 — сплески переходу
    b, _, _ = textbox(365, 66, "перехід: U та I великі заразом →\nсплеск, енергія E за кожен фронт",
                      size=12, color=POS, stroke=POS)
    parts.append(b)
    parts.append(arrow(280, 84, 210, 100, color=POS))
    parts.append(arrow(450, 84, 508, 100, color=POS))

    # 2 — провідність
    b, _, _ = textbox(365, 200, "провідність: I²·R_ON\n(довго, зате низько)", size=12,
                      color=FIELD, stroke=FIELD)
    parts.append(b)
    parts.append(arrow(365, 228, 365, 268, color=FIELD))

    # 3 — витік
    b, _, _ = textbox(642, 250, "витік: U·I_витоку —\nмайже нуль, але не нуль", size=12,
                      color=MUTED, stroke=MUTED)
    parts.append(b)
    parts.append(arrow(642, 278, 642, 322, color=MUTED))

    # 4 — керування (поза силовим колом)
    b, _, _ = textbox(560, 400, "керування: заряд у затвор чи струм у базу —\nце теж вати, і платять їх за кожен клац",
                      size=12, color=NEG, stroke=NEG)
    parts.append(b)

    render(os.path.join(IMG, 'four-costs.svg'), W, H, *parts)


# ═══ Фігури математичної вставки (math-switch-losses) ═════════════════════════

# ── Форма фронту: звідки ½·U·I·t і чому резистивне навантаження втричі дешевше ─
def fig_transition_shapes():
    W, H = 920, 580
    parts = []
    parts.append(text(W / 2, 30, "Форма сплеску на фронті: звідки береться площа", size=17, bold=True))

    ax_w, ax_h, oy = 320, 210, 400
    panels = [
        (95, "затиснуте індуктивне навантаження",
             "спершу росте струм при повній напрузі,\nпотім падає напруга при повному струмі"),
        (545, "чисто резистивне навантаження",
             "u та i рухаються разом\nнавантажувальною прямою"),
    ]

    for ox, subtitle, expl in panels:
        parts.append(text(ox + ax_w / 2, 66, subtitle, size=14, bold=True, color=INK))
        parts.append(mtext(ox + ax_w / 2, 92, expl.split("\n"), size=11.5, color=MUTED))

        # осі
        parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
        parts.append(line(ox, oy, ox, 140, color=INK, sw=2))
        parts.append(text(ox + ax_w / 2, oy + 34, "час фронту t →", size=12, color=MUTED))
        # позначки 0 і t на осі часу
        parts.append(text(ox, oy + 18, "0", size=11, color=MUTED))
        parts.append(text(ox + ax_w, oy + 18, "t", size=11, color=MUTED))

    def px(ox, x): return ox + x * ax_w
    def py(v): return oy - v * ax_h

    # ── ліва панель: затиснуте індуктивне ──
    ox = 95
    parts.append(mtext(48, 250, ["частка", "від U·I"], size=11, color=INK))
    # i(t): 0→1 за першу половину, далі полиця
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,4"/>'
                 % ("%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (px(ox, 0), py(0), px(ox, 0.5), py(1), px(ox, 1), py(1)), NEG))
    # u(t): полиця, далі 1→0
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,4"/>'
                 % ("%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (px(ox, 0), py(1), px(ox, 0.5), py(1), px(ox, 1), py(0)), FIELD))
    # p(t) — трикутник
    parts.append('<polygon points="%s" fill="%s" fill-opacity="0.18" stroke="%s" stroke-width="2.8"/>'
                 % ("%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (px(ox, 0), py(0), px(ox, 0.5), py(1), px(ox, 1), py(0)), POS, POS))
    parts.append(text(px(ox, 0.22) - 6, py(0.86), "i", size=13, color=NEG, bold=True))
    parts.append(text(px(ox, 0.80) + 12, py(0.42), "u", size=13, color=FIELD, bold=True))
    b, _, _ = textbox(px(ox, 0.5), 168, "вершина = U·I", size=12, color=POS, stroke=POS)
    parts.append(b)
    b, _, _ = textbox(px(ox, 0.5), py(0.30), "площа = ½·U·I·t", size=13, color=POS, stroke=POS)
    parts.append(b)

    # ── права панель: резистивне ──
    ox = 545
    # u(t): 1→0
    parts.append(line(px(ox, 0), py(1), px(ox, 1), py(0), color=FIELD, sw=1.8, dash="5,4"))
    # i(t): 0→1
    parts.append(line(px(ox, 0), py(0), px(ox, 1), py(1), color=NEG, sw=1.8, dash="5,4"))
    # p(t) = x(1−x) — парабола з вершиною ¼
    pts = []
    n = 60
    for k in range(n + 1):
        x = k / n
        pts.append("%.1f,%.1f" % (px(ox, x), py(x * (1 - x))))
    parts.append('<polygon points="%s %.1f,%.1f" fill="%s" fill-opacity="0.18" stroke="%s" stroke-width="2.8"/>'
                 % (" ".join(pts), px(ox, 0), py(0), POS, POS))
    parts.append(text(px(ox, 0.18) - 6, py(0.86), "u", size=13, color=FIELD, bold=True))
    parts.append(text(px(ox, 0.84) + 12, py(0.86), "i", size=13, color=NEG, bold=True))
    parts.append(line(px(ox, 0.5), py(0.25), px(ox, 0.5), py(0.62), color=POS, sw=1.2, dash="3,3"))
    b, _, _ = textbox(px(ox, 0.5), 168, "вершина = ¼·U·I", size=12, color=POS, stroke=POS)
    parts.append(b)
    b, _, _ = textbox(px(ox, 0.5), py(0.09), "площа = ⅙·U·I·t", size=13, color=POS, stroke=POS)
    parts.append(b)

    b, _, _ = textbox(W / 2, 505, "Той самий фронт t, та сама напруга, той самий струм — "
                                  "а енергія різниться втричі.\n"
                                  "Формула ½·U·I·t описує ліву картинку; на правій вона втричі завелика.",
                      size=12.5, color=INK, stroke=MUTED)
    parts.append(b)

    render(os.path.join(IMG, 'sw-transition-shapes.svg'), W, H, *parts)


# ── P(f) — пряма: перетин, стеля, гранична частота ────────────────────────────
def fig_loss_line():
    W, H = 900, 540
    parts = []
    parts.append(text(W / 2, 30, "Увесь ключ — це пряма: P(f) = P₀ + f·E_Σ", size=17, bold=True))

    ox, oy = 130, 420
    ax_w, ax_h = 640, 320
    Fmax, Pmax_ax = 250e3, 1.15          # осі: 250 кГц, 1.15 Вт
    P0, ESUM = 0.1125, 3.8e-6            # статика й енергія за період
    Pbud = 1.0                           # тепловий бюджет
    fx = P0 / ESUM                       # перетин ≈ 29.6 кГц
    fmax = (Pbud - P0) / ESUM            # ≈ 234 кГц

    def px(f): return ox + (f / Fmax) * ax_w
    def py(p): return oy - (p / Pmax_ax) * ax_h

    parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    parts.append(line(ox, oy, ox, 90, color=INK, sw=2))
    parts.append(text(ox + ax_w / 2, oy + 52, "частота перемикання f →", size=13, color=INK))
    parts.append(mtext(56, 250, ["утрати", "на ключі", "P, Вт"], size=12, color=INK))
    for f in (0, 50e3, 100e3, 150e3, 200e3, 250e3):
        parts.append(line(px(f), oy, px(f), oy + 5, color=MUTED, sw=1.2))
        parts.append(text(px(f), oy + 22, "%d" % (f / 1e3), size=11, color=MUTED))
    parts.append(text(px(250e3) + 26, oy + 22, "кГц", size=11, color=MUTED))

    # тепловий бюджет
    parts.append(line(ox, py(Pbud), ox + ax_w, py(Pbud), color=POS, sw=2, dash="7,5"))
    b, _, _ = textbox(255, py(Pbud) - 30, "тепловий бюджет P_max = 1.0 Вт", size=12, color=POS, stroke=POS)
    parts.append(b)

    # f·E_Σ — тільки динаміка
    parts.append(line(px(0), py(0), px(Fmax), py(Fmax * ESUM), color=NEG, sw=2, dash="6,4"))
    b, _, _ = textbox(640, 280, "f·E_Σ — динаміка:\nперехід + керування", size=11.5, color=NEG, stroke=NEG)
    parts.append(b)

    # P₀ — статика
    parts.append(line(ox, py(P0), ox + ax_w, py(P0), color=FIELD, sw=2, dash="6,4"))
    b, _, _ = textbox(300, py(P0) - 34, "P₀ = 0.113 Вт — статика: провідність + витік", size=11.5,
                      color=FIELD, stroke=FIELD)
    parts.append(b)

    # сума
    parts.append(line(px(0), py(P0), px(Fmax), py(P0 + Fmax * ESUM), color=INK, sw=3))
    b, _, _ = textbox(628, py(1.10), "P(f) — разом", size=12, color=INK, stroke=INK)
    parts.append(b)

    # точка перетину f×
    parts.append(line(px(fx), oy, px(fx), py(2 * P0), color=MUTED, sw=1.2, dash="3,3"))
    parts.append(circle(px(fx), py(2 * P0), 5, fill=MUTED, stroke=MUTED))
    b, _, _ = textbox(212, 128, "f× = P₀/E_Σ ≈ 30 кГц\nтут динаміка зрівнялася зі статикою", size=11.5,
                      color=MUTED, stroke=MUTED)
    parts.append(b)
    parts.append(arrow(190, 158, px(fx) - 4, py(2 * P0) - 8, color=MUTED))

    # гранична частота
    parts.append(line(px(fmax), oy, px(fmax), py(Pbud), color=POS, sw=1.2, dash="3,3"))
    parts.append(circle(px(fmax), py(Pbud), 5, fill=POS, stroke=POS))
    b, _, _ = textbox(575, 346, "f_max ≈ 234 кГц\nвище — кристал не охолодити", size=11.5,
                      color=POS, stroke=POS)
    parts.append(b)
    parts.append(arrow(px(fmax) - 24, 346, px(fmax) - 6, py(Pbud) + 20, color=POS))

    render(os.path.join(IMG, 'loss-line.svg'), W, H, *parts)


# ── Оптимум площі кристала: ванна, дно якої задає лише FOM ────────────────────
def fig_area_optimum():
    import math
    W, H = 900, 540
    parts = []
    parts.append(text(W / 2, 30, "Оптимальний кристал: провідність падає, комутація росте", size=17, bold=True))

    ox, oy = 130, 420
    ax_w, ax_h = 630, 300
    a, b_ = 0.1125, 0.076                 # P_пров = a/s,  P_ком = b·s
    Pax = 0.62
    s_lo, s_hi = 0.2, 5.0
    lg_lo, lg_hi = math.log10(s_lo), math.log10(s_hi)

    def px(s): return ox + (math.log10(s) - lg_lo) / (lg_hi - lg_lo) * ax_w
    def py(p): return oy - (p / Pax) * ax_h

    parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    parts.append(line(ox, oy, ox, 92, color=INK, sw=2))
    parts.append(text(ox + ax_w / 2, oy + 54, "площа кристала (у частках від наявної) →", size=13, color=INK))
    parts.append(mtext(56, 250, ["утрати", "на ключі", "P, Вт"], size=12, color=INK))
    for s in (0.2, 0.5, 1, 2, 5):
        parts.append(line(px(s), oy, px(s), oy + 5, color=MUTED, sw=1.2))
        parts.append(text(px(s), oy + 22, ("%g" % s) + "×", size=11, color=MUTED))

    def curve(fn, color, sw, dash=None):
        pts = []
        k = 0
        while k <= 120:
            s = 10 ** (lg_lo + (lg_hi - lg_lo) * k / 120)
            v = fn(s)
            if v <= Pax:
                pts.append("%.1f,%.1f" % (px(s), py(v)))
            k += 1
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s"%s/>'
                % (" ".join(pts), color, sw, d))

    parts.append(curve(lambda s: a / s, FIELD, 2, "6,4"))
    parts.append(curve(lambda s: b_ * s, NEG, 2, "6,4"))
    parts.append(curve(lambda s: a / s + b_ * s, POS, 3.2))

    s_opt = math.sqrt(a / b_)
    p_opt = 2 * math.sqrt(a * b_)
    parts.append(circle(px(s_opt), py(p_opt), 6, fill=POS, stroke=POS))
    parts.append(line(px(s_opt), py(p_opt), px(s_opt), oy, color=POS, sw=1.2, dash="3,3"))

    b, _, _ = textbox(268, 126, "P_пров = I²·R_ON·D ∝ 1/площа\n(більший кристал — менший R_ON)",
                      size=11.5, color=FIELD, stroke=FIELD)
    parts.append(b)
    parts.append(arrow(268, 156, 214, 212, color=FIELD))

    b, _, _ = textbox(688, 150, "P_ком = f·E_Σ ∝ площа\n(більший кристал —\nбільший заряд затвора)",
                      size=11.5, color=NEG, stroke=NEG)
    parts.append(b)
    parts.append(arrow(688, 192, 700, 246, color=NEG))

    b, _, _ = textbox(452, 340, "дно: P_пров = P_ком\nP_min = 2·√(a·b) — задає лише FOM",
                      size=12, color=POS, stroke=POS)
    parts.append(b)
    parts.append(arrow(452, 368, px(s_opt) + 6, py(p_opt) + 12, color=POS))

    b, _, _ = textbox(W / 2, 486, "Дно пласке: помилитися з площею вдвічі коштує лише +25%. "
                                  "Помилитися вдесятеро — уже вп'ятеро.",
                      size=12.5, color=INK, stroke=MUTED)
    parts.append(b)

    render(os.path.join(IMG, 'area-optimum.svg'), W, H, *parts)


# ── Теплова петля: нерухома точка, підсилення 1/(1−G) і розгін ────────────────
def fig_thermal_cobweb():
    W, H = 940, 560
    parts = []
    parts.append(text(W / 2, 30, "Ітерації R_ON ↔ температура: чи є нерухома точка", size=17, bold=True))

    ax = 300
    oy = 430
    Pax = 8.0
    a = 1.844

    panels = [(105, 0.5, "G = 0.5 — петля сходиться", FIELD),
              (555, 1.2, "G = 1.2 — петлі нема куди зійтися", POS)]

    for ox, G, subtitle, col in panels:
        parts.append(text(ox + ax / 2, 68, subtitle, size=14, bold=True, color=col))

        def px(p): return ox + (p / Pax) * ax
        def py(p): return oy - (p / Pax) * ax

        parts.append(line(ox, oy, ox + ax, oy, color=INK, sw=2))
        parts.append(line(ox, oy, ox, oy - ax, color=INK, sw=2))
        parts.append(text(ox + ax / 2, oy + 30, "утрати на вході кроку, Вт", size=11.5, color=MUTED))
        parts.append(mtext(ox - 62, oy - ax / 2 - 10, ["утрати", "на виході", "кроку, Вт"], size=11.5, color=MUTED))

        # пряма тотожності y = x
        parts.append(line(px(0), py(0), px(Pax), py(Pax), color=MUTED, sw=1.6, dash="5,4"))
        parts.append(text(px(6.9) + 26, py(6.9) - 6, "вихід = вхід", size=11, color=MUTED))

        # відображення y = a + G·x
        p_end = min(Pax, a + G * Pax)
        x_end = (p_end - a) / G
        x0p, y0p = px(0), py(a)
        x1p, y1p = px(x_end), py(p_end)
        parts.append(line(x0p, y0p, x1p, y1p, color=col, sw=2.6))
        # напис зсунуто вздовж нормалі до прямої (вгору-вліво), щоб не лежати на самій лінії
        dxl, dyl = x1p - x0p, y1p - y0p
        Ln = (dxl ** 2 + dyl ** 2) ** 0.5
        ux, uy = dxl / Ln, dyl / Ln
        lx = x0p + dxl * 0.30 + uy * 42
        ly = y0p + dyl * 0.30 - ux * 42
        parts.append(text(lx, ly, "a + G·P", size=12, color=col, anchor="start", bold=True))

        # павутинка
        p = a
        seg = ["%.1f,%.1f" % (px(p), py(0))]
        for _ in range(7):
            nxt = a + G * p
            if nxt > Pax:
                seg.append("%.1f,%.1f" % (px(p), py(Pax)))
                break
            seg.append("%.1f,%.1f" % (px(p), py(nxt)))
            seg.append("%.1f,%.1f" % (px(nxt), py(nxt)))
            p = nxt
        parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-opacity="0.85"/>'
                     % (" ".join(seg), INK))

        if G < 1:
            pstar = a / (1 - G)
            parts.append(circle(px(pstar), py(pstar), 6, fill=col, stroke=col))

    # підписи панелей
    b, _, _ = textbox(255, 128, "перетин із тотожністю —\nчесна робоча точка\nP = a/(1−G) = 3.69 Вт",
                      size=11.5, color=FIELD, stroke=FIELD)
    parts.append(b)
    parts.append(arrow(288, 162, 340, 232, color=FIELD))

    b, _, _ = textbox(700, 130, "пряма всюди вище тотожності:\nперетину нема — сходитися нема куди",
                      size=11.5, color=POS, stroke=POS)
    parts.append(b)
    parts.append(arrow(700, 164, 690, 214, color=POS))

    b, _, _ = textbox(W / 2, 502, "Ліворуч сходинки збігаються до перетину — розв'язок є. "
                                  "Праворуч кожен крок вищий за попередній,\n"
                                  "і сходинки йдуть у стелю: це не збій розрахунку, а тепловий розгін, "
                                  "знайдений на папері.",
                      size=12.5, color=INK, stroke=MUTED)
    parts.append(b)

    render(os.path.join(IMG, 'thermal-cobweb.svg'), W, H, *parts)


# ── Наївний олівець проти чесної петлі: підсилення й вертикальна стіна ────────
def _honest_dt(dt_naive, t_amb=40.0, k=1.7):
    """Чесний підйом температури для наївного підйому dt_naive.
    None — нерухомої точки нема (петля не осідає)."""
    t, prev = t_amb, None
    for _ in range(20000):
        tn = t_amb + dt_naive * k ** ((t - 25.0) / 100.0)
        step = tn - t
        if prev is not None and prev > 1e-6 and step / prev >= 1.0:
            return None
        if step < 1e-6:
            return tn - t_amb
        prev, t = step, tn
    return None


def fig_naive_vs_honest():
    W, H = 940, 600
    parts = []
    parts.append(text(W / 2, 30, "Наївний підйом температури проти чесного", size=17, bold=True))

    ox, oy = 130, 470
    ax_w, ax_h = 620, 360
    Xmax, Ymax = 80.0, 200.0
    BUDGET = 85.0          # T_j_max 125 °C при довкіллі 40 °C
    WALL = 64.2            # тут нерухома точка зникає
    EDGE = 50.0            # тут чесний підйом дорівнює бюджетові

    def px(d): return ox + (d / Xmax) * ax_w
    def py(h): return oy - (min(h, Ymax) / Ymax) * ax_h

    # зони — світлі смуги під кривою
    parts.append(rect(px(0), oy - ax_h, px(EDGE) - px(0), ax_h,
                      fill="#eafaf0", stroke="none", sw=0, rx=0))
    parts.append(rect(px(EDGE), oy - ax_h, px(WALL) - px(EDGE), ax_h,
                      fill="#fdf6e3", stroke="none", sw=0, rx=0))
    parts.append(rect(px(WALL), oy - ax_h, px(Xmax) - px(WALL), ax_h,
                      fill="#fdecea", stroke="none", sw=0, rx=0))

    parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    parts.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    parts.append(text(ox + ax_w / 2, oy + 54, "наївний підйом ΔT (усе при 25 °C), K →",
                      size=13, color=INK))
    parts.append(mtext(56, 262, ["чесний", "підйом", "ΔT, K ↑"], size=12, color=INK))

    for d in (0, 20, 40, 60, 80):
        parts.append(line(px(d), oy, px(d), oy + 5, color=MUTED, sw=1.2))
        parts.append(text(px(d), oy + 24, "%d" % d, size=11, color=MUTED))
    for h in (0, 50, 100, 150, 200):
        parts.append(line(ox - 5, py(h), ox, py(h), color=MUTED, sw=1.2))
        parts.append(text(ox - 16, py(h) + 4, "%d" % h, size=11, color=MUTED, anchor="end"))

    # пряма «якби R_ON не залежав від тепла»
    parts.append(line(px(0), py(0), px(Xmax), py(Xmax), color=MUTED, sw=1.6, dash="6,4"))
    parts.append(text(px(25) - 8, py(25) - 12, "наївно = чесно", size=11, color=MUTED, anchor="end"))

    # чесна крива
    pts = []
    d = 0.0
    while d <= WALL:
        h = _honest_dt(d)
        if h is None:
            break
        pts.append("%.1f,%.1f" % (px(d), py(h)))
        d += 0.5
    pts.append("%.1f,%.1f" % (px(WALL), py(Ymax)))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                 % (" ".join(pts), POS))

    # стіна
    parts.append(line(px(WALL), oy, px(WALL), oy - ax_h, color=POS, sw=2, dash="7,5"))

    # бюджет
    parts.append(line(ox, py(BUDGET), ox + ax_w, py(BUDGET), color=FIELD, sw=2, dash="7,5"))
    parts.append(line(px(EDGE), oy, px(EDGE), py(BUDGET), color=FIELD, sw=1.4, dash="3,3"))
    parts.append(circle(px(EDGE), py(BUDGET), 5, fill=FIELD, stroke=FIELD))

    b, _, _ = textbox(330, 145, "бюджет ΔT = 85 K  (T_j = 125 °C):\n"
                                "чесна крива сягає його вже за наївних 50 K",
                      size=11.5, color=FIELD, stroke=FIELD)
    parts.append(b)
    parts.append(arrow(330, 168, px(EDGE) - 3, py(BUDGET) - 9, color=FIELD))

    b, _, _ = textbox(722, 128, "за цією межею нерухомої\nточки нема зовсім:\nпетля не осідає ніде",
                      size=11.5, color=POS, stroke=POS)
    parts.append(b)
    parts.append(arrow(722, 162, px(WALL) + 4, 214, color=POS))

    # три робочі точки того самого SOT-23
    marks = [(35.0, "2.0 А", -70, -18), (50.1, "2.4 А", -64, -18)]
    for dn, lab, dx, dy in marks:
        h = _honest_dt(dn)
        parts.append(circle(px(dn), py(h), 5.5, fill=INK, stroke=INK))
        parts.append(text(px(dn) + dx, py(h) + dy, lab, size=12, color=INK, bold=True))
    parts.append(circle(px(77.8), oy - 6, 5.5, fill=POS, stroke=POS))
    parts.append(arrow(px(77.8), oy - 14, px(77.8), oy - ax_h + 16, color=POS))
    parts.append(text(px(77.8) - 12, oy - 26, "3.0 А", size=12, color=POS, bold=True, anchor="end"))

    b, _, _ = textbox(W / 2, 545,
                      "Той самий ключ SOT-23 на тій самій платі. Наївний олівець рахує лінійно "
                      "(пунктир) і бачить запас навіть на трьох амперах;\nчесна петля загинається "
                      "вгору й на 64 K втрачає нерухому точку. Уся правда — у відстані між "
                      "пунктиром і кривою.",
                      size=12.5, color=INK, stroke=MUTED)
    parts.append(b)

    render(os.path.join(IMG, 'naive-vs-honest.svg'), W, H, *parts)


# ── Карта вердиктів: що калькулятор каже про кожного кандидата ────────────────
def fig_verdict_map():
    import math
    W, H = 960, 470
    parts = []
    parts.append(text(W / 2, 30, "Вердикт калькулятора: 12 В · 3 А · D = 0.5 · довкілля 40 °C",
                      size=17, bold=True))

    ox, oy = 190, 360
    ax_w = 640
    F0, F1 = 1e3, 1e7                     # 1 кГц … 10 МГц

    def px(f): return ox + (math.log10(f) - math.log10(F0)) / 4.0 * ax_w

    GREEN, AMBER, RED, GREY = "#d5f2e1", "#fbeec8", "#f7d3ce", "#e6e8ea"

    rows = [
        ("SOT-23, дрібний",   [(F0, F1, RED)]),
        ("SO-8, середній",    [(F0, 1.867e6, GREEN), (1.867e6, 5.425e6, AMBER),
                               (5.425e6, 8.336e6, RED), (8.336e6, F1, GREY)]),
        ("SO-8, міліомний",   [(F0, 631e3, GREEN), (631e3, 1.507e6, AMBER),
                               (1.507e6, 2.504e6, RED), (2.504e6, F1, GREY)]),
        ("DPAK, біполярний",  [(F0, 46.9e3, GREEN), (46.9e3, 190.2e3, AMBER),
                               (190.2e3, 250.1e3, RED), (250.1e3, F1, GREY)]),
    ]

    y = 96
    for name, zones in rows:
        parts.append(text(ox - 18, y + 21, name, size=12.5, color=INK, anchor="end", bold=True))
        for a, b_, col in zones:
            parts.append(rect(px(a), y, px(b_) - px(a), 32, fill=col, stroke=MUTED, sw=1, rx=3))
        y += 52

    # вісь частоти
    parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    for f, lab in ((1e3, "1 кГц"), (1e4, "10 кГц"), (1e5, "100 кГц"),
                   (1e6, "1 МГц"), (1e7, "10 МГц")):
        parts.append(line(px(f), oy, px(f), oy + 6, color=MUTED, sw=1.2))
        parts.append(text(px(f), oy + 24, lab, size=11.5, color=MUTED))
    parts.append(text(ox + ax_w / 2, oy + 50, "частота перемикання (логарифмічна вісь) →",
                      size=13, color=INK))

    # межі стелі — числа над зеленими краями
    for f, lab, yy in ((46.9e3, "47 кГц", 262), (631e3, "631 кГц", 210), (1.867e6, "1.87 МГц", 158)):
        parts.append(line(px(f), yy - 8, px(f), oy, color=INK, sw=1.2, dash="3,3"))
        parts.append(text(px(f) + 6, yy - 14, lab, size=11.5, color=INK, anchor="start", bold=True))

    # позначки робочої точки й перетину
    parts.append(line(px(20e3), 84, px(20e3), oy, color=NEG, sw=1.6, dash="5,4"))
    parts.append(text(px(20e3), 76, "20 кГц", size=11.5, color=NEG, bold=True))
    parts.append(line(px(67e3), 84, px(67e3), oy, color=FIELD, sw=1.6, dash="5,4"))
    parts.append(text(px(67e3) + 44, 76, "67 кГц: тут середній і міліомний рівні",
                      size=11.5, color=FIELD, bold=True))

    # легенда
    lx = 190
    for col, lab in ((GREEN, "вкладається"), (AMBER, "перегрів"),
                     (RED, "розгін"), (GREY, "вже не ключ")):
        parts.append(rect(lx, 424, 22, 16, fill=col, stroke=MUTED, sw=1, rx=3))
        parts.append(text(lx + 30, 437, lab, size=12, color=INK, anchor="start"))
        lx += 30 + text_width(lab, 12) + 34

    render(os.path.join(IMG, 'verdict-map.svg'), W, H, *parts)


if __name__ == '__main__':
    fig_switch_plane()
    fig_linear_vs_switch()
    fig_four_costs()
    fig_transition_shapes()
    fig_loss_line()
    fig_area_optimum()
    fig_thermal_cobweb()
    fig_naive_vs_honest()
    fig_verdict_map()
    print("OK figures")
