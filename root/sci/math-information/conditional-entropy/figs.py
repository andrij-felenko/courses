# -*- coding: utf-8 -*-
"""Фігури до теми «Умовна ентропія» (conditional-entropy).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Умовна ентропія як зважене середнє залишку ─────────────────────────────
# Ідея: ширина стовпця — частота підказки p(y), висота — залишок H(X|Y=y);
# площа — внесок; середнє H(X|Y)=0.575 нижче за наосліп H(X)=0.680.
def fig_averaging():
    W, H = 820, 440
    base = 350                 # базова лінія (нуль бітів)
    x0 = 100                   # лівий край стовпців
    span = 360.0               # ширина під суму частот = 1.0
    scale = 232.0              # 1 біт → px
    f = []

    def bx(p):  return x0 + p * span
    def by(v):  return base - v * scale

    bars = [
        ("Y = певно",    "p = 0.8", 0.8, 0.469, "H = 0.469"),
        ("Y = сумнівно", "p = 0.2", 0.2, 1.000, "H = 1.000"),
    ]

    # осі
    f.append(line(x0, base, x0 + span + 20, base, color=INK, sw=1.5))
    f.append(line(x0, base + 4, x0, by(1.06), color=INK, sw=1.5))
    f.append(arrow(x0, by(1.02), x0, by(1.10), color=INK, sw=1.5))
    f.append(text(x0 - 10, by(1.08) + 2, "залишок", 10.5, INK, "end", bold=True))
    f.append(text(x0 - 10, by(1.08) + 16, "H(X|Y=y), біт", 10.5, INK, "end", bold=True))
    for v in [0.0, 0.5, 1.0]:
        f.append(line(x0 - 5, by(v), x0, by(v), color=INK, sw=1.2))
        f.append(text(x0 - 9, by(v) + 4, ("%.1f" % v), 10, MUTED, "end"))

    # довідкова лінія H(X) — наосліп
    f.append(line(x0, by(0.680), bx(1.0) + 12, by(0.680), color=NEG, sw=1.6, dash="6 4"))
    f.append(text(bx(1.0) + 18, by(0.680) - 5, "H(X) = 0.680", 11, NEG, "start", bold=True))
    f.append(text(bx(1.0) + 18, by(0.680) + 11, "(наосліп)", 10, NEG, "start"))

    # стовпці (ширина=частота, висота=залишок)
    px = x0
    for lab, pf, p, v, hl in bars:
        w = p * span
        f.append(rect(px, by(v), w, v * scale, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=4))
        f.append(text(px + w / 2, by(v) - 9, hl, 11, FIELD, "middle", bold=True))
        f.append(text(px + w / 2, base + 22, lab, 11, INK, "middle", bold=True))
        f.append(text(px + w / 2, base + 39, pf, 10.5, MUTED, "middle"))
        px += w

    # лінія середнього H(X|Y)
    f.append(line(x0, by(0.575), bx(1.0) + 12, by(0.575), color=POS, sw=2.0))
    f.append(text(bx(1.0) + 18, by(0.575) + 4, "H(X|Y) = 0.575", 11, POS, "start", bold=True))

    # анотація: сумнівний стовпець вищий за наосліп
    f.append(text(bx(0.9), by(1.0) - 30, "рідкісний сумнівний прапорець", 10, MUTED, "middle"))
    f.append(text(bx(0.9), by(1.0) - 17, "лишає більше, ніж наосліп", 10, MUTED, "middle"))

    # рамка-обчислення
    f.append(rect(508, 250, 300, 92, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=9))
    f.append(mtext(524, 278,
                   ["H(X|Y) = Σ p(y)·H(X|Y=y)",
                    "  = 0.8·0.469 + 0.2·1.000",
                    "  = 0.575 біта / символ"], 11.5, INK, "start"))

    # підпис під віссю про сенс площі
    f.append(text(x0 + span / 2, base + 66,
                  "ширина — частота підказки, висота — її залишок; площа — внесок у середнє",
                  10.5, MUTED, "middle"))

    render(os.path.join(IMG, "averaging.svg"), W, H, *f,
           title="Умовна ентропія — середній залишок непевності по всіх підказках")


# ── 2. Ланцюгове правило: невизначеність пари ділиться двома способами ─────────
# Ідея: та сама висота H(X,Y) = H(Y)+H(X|Y) = H(X)+H(Y|X); умовна частина — зелена.
def fig_chain_rule():
    W, H = 760, 440
    base = 360
    scale = 196.0              # 1 біт → px
    bw = 96
    f = []

    def by(v): return base - v * scale

    top = by(1.297)           # спільна вершина обох стовпців

    # базова лінія й нуль
    f.append(line(120, base, 640, base, color=INK, sw=1.4))
    f.append(text(112, base + 4, "0", 10, MUTED, "end"))

    # пунктир спільної вершини
    f.append(line(150, top, 610, top, color=MUTED, sw=1.3, dash="5 4"))
    f.append(text(380, top - 12, "H(X,Y) = 1.297 біта — невизначеність пари", 12, INK, "middle", bold=True))

    def column(cx, low_v, low_lab, hi_v, hi_lab, cap):
        x = cx - bw / 2
        parts = []
        # нижній сегмент (перший крок) — синій
        parts.append(rect(x, by(low_v), bw, low_v * scale, fill="#eaf0fd", stroke=NEG, sw=1.7, rx=3))
        parts.append(text(cx, by(low_v / 2) + 4, low_lab, 11, NEG, "middle", bold=True))
        # верхній сегмент (умовна ентропія) — зелений
        parts.append(rect(x, by(low_v + hi_v), bw, hi_v * scale, fill="#eef6ef", stroke=FIELD, sw=1.7, rx=3))
        parts.append(text(cx, by(low_v + hi_v / 2) + 4, hi_lab, 11, FIELD, "middle", bold=True))
        # підпис під стовпцем
        parts.append(text(cx, base + 24, cap, 10.5, INK, "middle"))
        return parts

    f += column(250, 0.722, "H(Y) = 0.722", 0.575, "H(X|Y) = 0.575", "спершу Y, тоді решта X")
    f += column(510, 0.680, "H(X) = 0.680", 0.617, "H(Y|X) = 0.617", "спершу X, тоді решта Y")

    # позначка «умовна ентропія — зелене»
    f.append(rect(624, top + 6, 14, 14, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=3))
    f.append(text(646, top + 17, "умовна", 10, FIELD, "start", bold=True))
    f.append(text(646, top + 30, "ентропія", 10, FIELD, "start", bold=True))

    # рамка-тотожність
    f.append(rect(150, 396, 460, 34, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=9))
    f.append(text(380, 418, "H(X,Y) = H(Y) + H(X|Y) = H(X) + H(Y|X)", 13, INK, "middle", bold=True))

    render(os.path.join(IMG, "chain-rule.svg"), W, H, *f,
           title="Ланцюгове правило: невизначеність пари ділиться двома способами")


# ── 3. Угнутість ентропії: чому нерівність тримає лише середнє ─────────────────
# Ідея: крива H(q) угнута; дві підказки A,B на ній; суміш дає H(X) на кривій,
# середнє залишків H(X|Y) — на хорді нижче; вершина B стирчить вище за H(X).
def fig_concavity():
    W, H = 880, 500
    xL, xR = 100.0, 560.0          # q = 0 .. 1
    base, sy = 410.0, 300.0        # H = 0 внизу; 1 біт → 300 px
    f = []

    def px(q): return xL + (xR - xL) * q
    def py(h): return base - h * sy

    def Hb(q):                      # двійкова ентропія
        if q <= 0 or q >= 1:
            return 0.0
        return -q * math.log2(q) - (1 - q) * math.log2(1 - q)

    # значення прикладу
    qA, qB = 0.05, 0.5
    wA = 0.9
    HA, HB = Hb(qA), Hb(qB)                 # 0.286, 1.000
    qbar = wA * qA + (1 - wA) * qB          # 0.095
    Hmix = Hb(qbar)                         # 0.453  = H(X)
    Hcond = wA * HA + (1 - wA) * HB         # 0.358  = H(X|Y)
    I = Hmix - Hcond                        # 0.095

    # осі
    f.append(line(xL, base, xR + 20, base, color=INK, sw=1.5))
    f.append(arrow(xR + 12, base, xR + 24, base, color=INK, sw=1.5))
    f.append(line(xL, base, xL, py(1.08), color=INK, sw=1.5))
    f.append(arrow(xL, py(1.04), xL, py(1.12), color=INK, sw=1.5))
    f.append(text(xL - 8, py(1.10) + 4, "H, біт", 11, INK, "end", bold=True))
    f.append(text(xR + 6, base + 22, "q = P(X=1)", 11, INK, "middle", bold=True))
    for v in [0.0, 0.5, 1.0]:
        f.append(line(xL - 5, py(v), xL, py(v), color=INK, sw=1.2))
        f.append(text(xL - 9, py(v) + 4, ("%.1f" % v), 10, MUTED, "end"))
    for q in [0.0, 0.5, 1.0]:
        f.append(line(px(q), base, px(q), base + 5, color=INK, sw=1.2))
        f.append(text(px(q), base + 18, ("%.1f" % q), 10, MUTED, "middle"))

    # крива H(q)
    pts = []
    q = 0.003
    while q < 1.0:
        pts.append("%.1f %.1f" % (px(q), py(Hb(q))))
        q += 0.004
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" L ".join(pts), INK))
    f.append(text(px(0.30) + 6, py(Hb(0.30)) - 10, "H(q)", 12, INK, "start", bold=True))

    # рівень H(X) — горизонталь, щоб показати, що B вище
    f.append(line(xL, py(Hmix), px(qB) + 40, py(Hmix), color=MUTED, sw=1.3, dash="6 4"))
    f.append(text(xL + 6, py(Hmix) - 6, "рівень H(X)", 10, MUTED, "start"))

    # хорда A—B
    f.append(line(px(qA), py(HA), px(qB), py(HB), color=NEG, sw=1.8, dash="7 4"))
    f.append(text((px(qA) + px(qB)) / 2 + 30, (py(HA) + py(HB)) / 2 - 8,
                  "хорда", 10.5, NEG, "middle", italic=True))

    # вертикальна напрямна на суміші q̄
    f.append(line(px(qbar), base, px(qbar), py(Hmix), color=MUTED, sw=1.2, dash="3 3"))
    f.append(line(px(qbar), base, px(qbar), base + 5, color=INK, sw=1.2))
    f.append(text(px(qbar), base + 30, "q̄=0.095", 10, INK, "middle", bold=True))

    # зазор I між хордою і кривою над q̄ (зелена дужка)
    gx = px(qbar) + 12
    f.append(line(gx, py(Hcond), gx, py(Hmix), color=FIELD, sw=2.2))
    f.append(line(gx - 3, py(Hcond), gx + 3, py(Hcond), color=FIELD, sw=2.2))
    f.append(line(gx - 3, py(Hmix), gx + 3, py(Hmix), color=FIELD, sw=2.2))
    f.append(text(gx + 8, (py(Hcond) + py(Hmix)) / 2 + 4, "I = 0.095", 10.5, FIELD, "start", bold=True))

    # точки
    f.append(circle(px(qA), py(HA), 5.5, fill=INK, stroke=BG, sw=1.5))
    f.append(text(px(qA) + 2, py(HA) + 22, "A", 13, INK, "middle", bold=True))
    f.append(circle(px(qB), py(HB), 5.5, fill=INK, stroke=BG, sw=1.5))
    f.append(text(px(qB), py(HB) - 12, "B", 13, INK, "middle", bold=True))
    f.append(circle(px(qbar), py(Hmix), 6.0, fill=FIELD, stroke=BG, sw=1.5))   # H(X) на кривій
    f.append(circle(px(qbar), py(Hcond), 6.0, fill=POS, stroke=BG, sw=1.5))    # H(X|Y) на хорді

    # анотація «B вище за рівень H(X)»
    f.append(text(px(qB) + 14, py(HB) + 4, "H(X|Y=B)=1.0", 11, POS, "start", bold=True))
    f.append(text(px(qB) + 14, py(HB) + 19, "вище за H(X) — шкодить", 10, POS, "start"))

    # правий підсумковий стовпчик
    bx0, by0 = 610, 150
    f.append(rect(bx0, by0, 250, 176, fill="#f7f9fb", stroke=LINE, sw=1.4, rx=10))
    f.append(text(bx0 + 125, by0 + 24, "Числа прикладу", 12.5, INK, "middle", bold=True))
    rows = [
        ("H(X|Y=A) = 0.286", "часта, p=0.9", FIELD),
        ("H(X|Y=B) = 1.000", "рідкісна, p=0.1", POS),
        ("H(X)   = 0.453", "на кривій (суміш)", INK),
        ("H(X|Y) = 0.358", "на хорді (середнє)", NEG),
    ]
    ry = by0 + 52
    for a, b, col in rows:
        f.append(text(bx0 + 18, ry, a, 12, col, "start", bold=True))
        f.append(text(bx0 + 232, ry, b, 9.5, MUTED, "end"))
        ry += 30
    f.append(line(bx0 + 16, ry - 16, bx0 + 234, ry - 16, color="#dfe4ea", sw=1.2))
    f.append(text(bx0 + 18, ry + 2, "0.358 ≤ 0.453, але 1.0 > 0.453", 10.5, INK, "start", italic=True))

    render(os.path.join(IMG, "concavity.svg"), W, H, *f,
           title="Угнутість ентропії: середнє під кривою, окрема вершина — над нею")


# ── 4. «Рівний голос»: етимологія equivocation як механізм каналу ─────────────
# Ідея: кілька входів шум зводить в один вихід y; за y приймач «чує» їх рівним
# голосом (aequus + vōx). Повна рівність голосів → H(X|Y=y)=1 біт двозначності.
def fig_equal_voice():
    W, H = 860, 440
    f = []

    def node(cx, cy, big, small, w, h, stroke, fill):
        p = [rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, sw=1.8, rx=8),
             text(cx, cy - 3, big, 15, INK, "middle", bold=True),
             text(cx, cy + 15, small, 10.5, MUTED, "middle")]
        return p

    f += node(150, 140, "a", "надіслали a", 140, 54, NEG, "#eaf0fd")
    f += node(150, 255, "b", "надіслали b", 140, 54, POS, "#fdecea")
    f += node(455, 197, "y", "бачить лише y", 170, 58, INK, "#f4f6f8")

    # шум зводить обидва входи в той самий вихід
    f.append(arrow(220, 150, 368, 180, color=NEG, sw=2.0))
    f.append(arrow(220, 245, 368, 214, color=POS, sw=2.0))
    f.append(text(292, 150, "шум", 10.5, MUTED, "middle", italic=True))
    f.append(text(292, 247, "шум", 10.5, MUTED, "middle", italic=True))

    # правий бік — «рівний голос» як рівні ймовірності
    f.append(text(690, 108, "«рівний голос»: за виходом y", 12, INK, "middle", bold=True))
    f.append(text(690, 126, "входи a і b майже рівноймовірні", 10.5, MUTED, "middle"))
    f.append(rect(648, 160, 40, 90, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    f.append(rect(700, 160, 40, 90, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    f.append(text(668, 210, "0.5", 12, NEG, "middle", bold=True))
    f.append(text(720, 210, "0.5", 12, POS, "middle", bold=True))
    f.append(line(640, 250, 748, 250, color=INK, sw=1.3))
    f.append(text(668, 266, "p(a|y)", 10, NEG, "middle"))
    f.append(text(720, 266, "p(b|y)", 10, POS, "middle"))
    f.append(text(690, 292, "H(X|Y=y) = 1 біт — повна двозначність", 11, INK, "middle", bold=True))

    # смуга етимології
    f.append(rect(70, 350, 720, 72, fill="#f4f6f8", stroke=LINE, sw=1.3, rx=10))
    f.append(text(430, 377,
                  "лат. aequus «рівний» + vōx «голос»  →  aequivocus «рівноголосий, двозначний»",
                  11.5, INK, "middle"))
    f.append(text(430, 401,
                  "→ англ. equivocation: слово логіки про двозначність, що його Шеннон переніс на канал",
                  11, MUTED, "middle"))

    render(os.path.join(IMG, "equal-voice.svg"), W, H, *f,
           title="Двозначність: один вихід — рівний голос за кілька входів")


# ── 5. Швидкість і двозначність у теоремі про кодування каналу ────────────────
# Ідея: R = H(x) − H(x|y). H ≤ C → двозначність до нуля; H > C → неусувний
# залишок H − C, який жоден код не прибере (Теорема 11 Шеннона, 1948).
def fig_rate_equivocation():
    W, H = 820, 440
    base = 350
    scale = 150.0
    bwd = 122
    f = []

    def by(v): return base - v * scale

    # формула зверху
    f.append(text(410, 58, "R = H(X) − H(X|Y)   —   справжня швидкість передачі",
                  12.5, INK, "middle", bold=True))

    # осі
    f.append(line(112, base, 700, base, color=INK, sw=1.5))
    f.append(line(112, base + 4, 112, by(1.72) - 6, color=INK, sw=1.5))
    f.append(arrow(112, by(1.66), 112, by(1.74), color=INK, sw=1.5))
    f.append(text(100, by(1.72) + 2, "біт/символ", 10.5, INK, "end", bold=True))
    for v in [0.0, 0.5, 1.0, 1.5]:
        f.append(line(107, by(v), 112, by(v), color=INK, sw=1.2))
        f.append(text(102, by(v) + 4, ("%.1f" % v), 10, MUTED, "end"))

    # лінія пропускної здатності C
    f.append(line(112, by(1.0), 668, by(1.0), color=FIELD, sw=1.8, dash="7 4"))
    f.append(text(674, by(1.0) - 4, "C — пропускна", 11, FIELD, "start", bold=True))
    f.append(text(674, by(1.0) + 11, "здатність каналу", 11, FIELD, "start", bold=True))

    # стовпець A: H ≤ C — усе доходить, двозначність → 0
    ax = 250
    HA = 0.7
    f.append(rect(ax - bwd / 2, by(HA), bwd, HA * scale, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=4))
    f.append(text(ax, by(HA / 2) - 2, "R → H", 12, FIELD, "middle", bold=True))
    f.append(text(ax, by(HA / 2) + 15, "усе доходить", 10, FIELD, "middle"))
    f.append(text(ax, base + 23, "H ≤ C", 12.5, INK, "middle", bold=True))
    f.append(text(ax, base + 41, "помилку й двозначність", 10.5, MUTED, "middle"))
    f.append(text(ax, base + 56, "можна звести до нуля", 10.5, MUTED, "middle"))

    # стовпець B: H > C — доходить лише C, згори неусувний залишок H − C
    bx = 540
    HB = 1.6
    f.append(rect(bx - bwd / 2, by(1.0), bwd, 1.0 * scale, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=4))
    f.append(text(bx, by(0.5) - 2, "R ≈ C", 12, FIELD, "middle", bold=True))
    f.append(text(bx, by(0.5) + 15, "доходить", 10, FIELD, "middle"))
    f.append(rect(bx - bwd / 2, by(HB), bwd, (HB - 1.0) * scale, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    f.append(text(bx, by(1.0 + (HB - 1.0) / 2) - 2, "H(X|Y) ≥ H − C", 11, POS, "middle", bold=True))
    f.append(text(bx, by(1.0 + (HB - 1.0) / 2) + 14, "неусувний залишок", 9.5, POS, "middle"))
    f.append(text(bx, base + 23, "H > C", 12.5, INK, "middle", bold=True))
    f.append(text(bx, base + 41, "двозначність не опустити", 10.5, MUTED, "middle"))
    f.append(text(bx, base + 56, "нижче за H − C", 10.5, MUTED, "middle"))

    render(os.path.join(IMG, "rate-equivocation.svg"), W, H, *f,
           title="Швидкість і двозначність: що канал доносить і що неусувно губить")


if __name__ == "__main__":
    fig_averaging()
    fig_chain_rule()
    fig_concavity()
    fig_equal_voice()
    fig_rate_equivocation()
    print("OK: figures written to", IMG)
