# -*- coding: utf-8 -*-
"""Фігури до теми «MOSFET: поріг відкривання» (book/electronics/microelectronics).
Запуск:  python figs.py   → пише 8 SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── Локальні відтінки напівпровідника (поверх палітри svgkit) ────────────────
P_BODY = "#eaf0e8"   # p-підкладка
P_EDGE = "#7a8a78"
NREG   = "#cfd9ea"   # n⁺-області
OXIDE  = "#fff3b0"   # оксид
OX_EDG = "#e0a32e"
GATE   = "#cfd6dd"   # метал затвора
CHAN   = "#cfe0f5"   # інверсійний n-канал
DEPL   = "#f3eef6"   # збіднена область
WATER  = "#cfe0f5"   # вода у греблі
DAMCOL = "#cdbfa8"   # тіло греблі


def arrowhead(x, y, color, d=5, dir="down"):
    """Маленький трикутник-вістря (svgkit дає лише INK-стрілку; для кольорових — свій)."""
    if dir == "down":
        pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (x - d, y - d, x + d, y - d, x, y)
    else:  # up
        pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (x - d, y + d, x + d, y + d, x, y)
    return '<polygon points="%s" fill="%s"/>' % (pts, color)


def carrier(cx, cy, kind, r=5):
    """Носій заряду: 'e' електрон (синій −), 'h' дірка (червоний +)."""
    if kind == "e":
        return (circle(cx, cy, r, fill="#dfe7f0", stroke=NEG, sw=1.3) +
                line(cx - r * 0.5, cy, cx + r * 0.5, cy, color=NEG, sw=1.3))
    return (circle(cx, cy, r, fill="#fdecea", stroke=POS, sw=1.3) +
            text(cx, cy + r * 0.55, "+", size=int(r * 1.7), color=POS, bold=True))


def mosfet_panel(x0, y0, w, gate_label, surface,
                 sub_label="p", chan_h=0.0, gate_color=INK):
    """Розріз MOSFET: p-підкладка, два n⁺-береги, оксид, затвор; поверхня
    surface ∈ {'holes','depl','chan'}. chan_h — товщина каналу (px), якщо chan.
    Повертає (svg, body_x, body_y, body_w, body_h)."""
    body_h = 78.0
    by = y0
    bx = x0
    f = []
    # тіло p-підкладки
    f.append(rect(bx, by, w, body_h, fill=P_BODY, stroke=P_EDGE, sw=1.6, rx=0))
    # n⁺ береги (витік / стік)
    nw = w * 0.24
    f.append(rect(bx + 8, by, nw, 30, fill=NREG, stroke=NEG, sw=1.3, rx=0))
    f.append(text(bx + 8 + nw / 2, by + 20, "n⁺", size=11, bold=True))
    f.append(rect(bx + w - 8 - nw, by, nw, 30, fill=NREG, stroke=NEG, sw=1.3, rx=0))
    f.append(text(bx + w - 8 - nw / 2, by + 20, "n⁺", size=11, bold=True))
    # оксид + затвор по центру
    gx = bx + w * 0.30
    gw = w * 0.40
    f.append(rect(gx, by - 12, gw, 8, fill=OXIDE, stroke=OX_EDG, sw=1.2, rx=0))
    f.append(rect(gx + 6, by - 28, gw - 12, 16, fill=GATE, stroke=INK, sw=1.3, rx=0))
    gf = fit_font(gate_label, gw - 16, 11, True)
    f.append(text(gx + gw / 2, by - 17, gate_label, size=max(9, gf), color=gate_color, bold=True))
    # поверхня під оксидом
    if surface == "holes":
        for i in range(5):
            f.append(carrier(gx + gw * (i + 0.5) / 5, by + 16, "h", r=6))
    elif surface == "depl":
        f.append(rect(gx, by, gw, 20, fill=DEPL, stroke="#b9a0c8", sw=1.1, rx=0))
        for i in range(5):
            f.append(text(gx + gw * (i + 0.5) / 5, by + 15, "−", size=11, color="#7a5b9a", bold=True))
    elif surface == "chan":
        ch = max(8.0, chan_h)
        f.append(rect(gx, by, gw, ch, fill=CHAN, stroke=NEG, sw=1.3, rx=0))
        n = 6
        for i in range(n):
            f.append(carrier(gx + gw * (i + 0.5) / n, by + ch / 2, "e", r=3.6))
    return "".join(f), bx, by, w, body_h


# ── осі графіка (svgkit не має — будуємо через line()+arrow()) ────────────────
def axes(ox, oy, top, right, xlabel, ylabel):
    f = [arrow(ox, oy, ox, top, color=INK, sw=2),
         arrow(ox, oy, right, oy, color=INK, sw=2),
         text(right + 6, oy + 4, xlabel, size=13, color=INK, anchor="start", bold=True),
         text(ox - 4, top - 8, ylabel, size=13, color=INK, anchor="middle", bold=True)]
    return "".join(f)


def polyline(pts, color, sw=2.6):
    d = "M " + " L ".join("%.1f,%.1f" % p for p in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


# ════════════════════════════════════════════════════════════════════════════
# 1. three-stages.svg — нема каналу → збіднення → інверсія
# ════════════════════════════════════════════════════════════════════════════
def fig_three_stages():
    W, H = 900, 300
    f = []
    panels = [
        (40,  "Vgs = 0",        "затвор 0В",  "holes", 0,    "повно дірок — каналу нема",  MUTED),
        (330, "мала Vgs (< Vth)", "затвор +",  "depl",  0,    "дірки пішли — збіднення",    MUTED),
        (620, "Vgs > Vth",      "затвор ++",  "chan",  12,   "електронний канал — відкрито!", FIELD),
    ]
    for x0, head, glab, surf, ch, cap, capcol in panels:
        f.append(text(x0 + 110, 58, head, size=12, bold=True))
        svg, bx, by, bw, bh = mosfet_panel(x0, 150, 220, glab, surf, chan_h=ch)
        f.append(svg)
        f.append(text(x0 + 110, by + bh + 20, cap, size=10, color=capcol,
                      bold=(surf == "chan")))
    f.append(text(W / 2, H - 12,
                  "Поле спершу розчищає поверхню від дірок (збіднення), далі стягує електрони й творить канал (інверсія).",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "three-stages.svg"), W, H, *f,
           title="Як росте напруга затвора: нема каналу → збіднення → інверсія")


# ════════════════════════════════════════════════════════════════════════════
# 2. inversion-layer.svg — інверсія зблизька
# ════════════════════════════════════════════════════════════════════════════
def fig_inversion_layer():
    W, H = 720, 320
    f = []
    # тіло p-підкладки
    bx, by, bw, bh = 120, 170, 480, 110
    f.append(rect(bx, by, bw, bh, fill=P_BODY, stroke=P_EDGE, sw=1.8, rx=0))
    f.append(text(W / 2, by + bh - 18, "p-підкладка (дірки в глибині)", size=11))
    # n⁺ береги
    f.append(rect(140, 170, 110, 40, fill=NREG, stroke=NEG, sw=1.6, rx=0))
    f.append(text(195, 194, "n⁺ витік", size=10, bold=True))
    f.append(rect(470, 170, 110, 40, fill=NREG, stroke=NEG, sw=1.6, rx=0))
    f.append(text(525, 194, "n⁺ стік", size=10, bold=True))
    # оксид + затвор
    f.append(rect(250, 150, 220, 12, fill=OXIDE, stroke=OX_EDG, sw=1.6, rx=0))
    f.append(text(360, 159, "оксид", size=9))
    f.append(rect(260, 120, 200, 24, fill=GATE, stroke=INK, sw=1.6, rx=0))
    f.append(text(360, 136, "затвор +", size=11, bold=True))
    # ряд «+» на затворі
    for i in range(7):
        f.append(text(280 + i * 28, 114, "+", size=12, color=POS, bold=True))
    # стрілки поля вниз (сині), з вістрям
    for i in range(6):
        xx = 285 + i * 32
        f.append(line(xx, 146, xx, 170, color=NEG, sw=1.6))
        f.append(arrowhead(xx, 171, NEG, d=4, dir="down"))
    # інверсійний шар (канал) — електрони
    f.append(rect(250, 170, 220, 12, fill=CHAN, stroke=NEG, sw=1.6, rx=0))
    n = 12
    for i in range(n):
        f.append(carrier(262 + i * (216.0 / (n - 1)), 176, "e", r=4.0))
    f.append(text(360, 202, "інверсійний шар = канал (місток витік→стік)",
                  size=10, color=FIELD, bold=True))
    f.append(text(W / 2, H - 10,
                  "Електрони, стягнуті полем до поверхні, утворюють тонкий n-шар, що сполучає два n⁺-береги. Це і є канал.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "inversion-layer.svg"), W, H, *f,
           title="Інверсія: поле стягує електрони, p-поверхня стає n-каналом")


# ════════════════════════════════════════════════════════════════════════════
# 3. threshold-transfer.svg — передатна крива Id(Vgs)
# ════════════════════════════════════════════════════════════════════════════
def fig_threshold_transfer():
    W, H = 680, 320
    ox, oy, top, right = 110, 250, 56, 544
    f = [axes(ox, oy, top, right, "Vgs", "Id")]
    vth_x = 260.0
    # крива: плоско до Vth, далі квадратично вгору
    pts = []
    x = ox
    while x <= 530:
        if x <= vth_x:
            y = oy - 2
        else:
            t = (x - vth_x) / 70.0
            y = (oy - 2) - 1.6 * t * t * 70.0
        pts.append((x, max(top + 6, y)))
        x += 6
    f.append(polyline(pts, POS, sw=2.6))
    # позначка Vth
    f.append(line(vth_x, oy, vth_x, 64, color=MUTED, sw=1.3, dash="4 3"))
    f.append(text(vth_x, oy + 20, "Vth", size=11, bold=True))
    f.append(text(170, oy + 20, "закрито", size=10, color=NEG, bold=True))
    f.append(text(440, oy + 20, "відкрито", size=10, color=FIELD, bold=True))
    f.append(text(452, 120, "струм швидко росте", size=10, color=POS))
    f.append(text(252, 232, "трохи нижче — підпороговий хвіст",
                  size=9, color=MUTED, anchor="end", italic=True))
    render(os.path.join(IMG, "threshold-transfer.svg"), W, H, *f,
           title="Передатна крива: струм стоку від напруги затвора")


# ════════════════════════════════════════════════════════════════════════════
# 4. overdrive.svg — перевищення керує товщиною каналу й опором
# ════════════════════════════════════════════════════════════════════════════
def fig_overdrive():
    W, H = 760, 300
    f = []
    cols = [
        (40,  "трохи > Vth",  5,   "великий опір", POS),
        (285, "помірно",      11,  "середній",     OX_EDG),
        (530, "значно > Vth", 18,  "малий опір",   FIELD),
    ]
    for x0, head, ch, rlab, rcol in cols:
        cx = x0 + 100
        f.append(text(cx, 58, head, size=11, bold=True))
        # розріз: тіло, оксид, затвор, канал змінної товщини
        f.append(rect(x0, 150, 200, 70, fill=P_BODY, stroke=P_EDGE, sw=1.5, rx=0))
        f.append(rect(x0, 132, 200, 8, fill=OXIDE, stroke=OX_EDG, sw=1.2, rx=0))
        f.append(rect(x0 + 20, 116, 160, 14, fill=GATE, stroke=INK, sw=1.3, rx=0))
        f.append(text(cx, 127, "затвор", size=9))
        f.append(rect(x0, 150, 200, ch, fill=CHAN, stroke=NEG, sw=1.3, rx=0))
        f.append(text(cx, 150 + ch + 18, "канал", size=9, color=NEG, bold=True))
        # плашка опору
        f.append(fitbox(x0 + 50, 244, 100, 28, rlab, size=10, fill=BG, stroke=rcol,
                        color=rcol, bold=True))
    f.append(text(W / 2, H - 8,
                  "Більше перевищення → густіший електронний шар → менший опір каналу.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "overdrive.svg"), W, H, *f,
           title="Перевищення порогу (Vgs − Vth) керує товщиною каналу")


# ════════════════════════════════════════════════════════════════════════════
# 5. logic-level.svg — 5В: логічного рівня vs звичайний
# ════════════════════════════════════════════════════════════════════════════
def fig_logic_level():
    W, H = 720, 320
    f = []
    cards = [
        (40,  "логічного рівня", "Vgs = 5 В,  Vth = 1.5 В", "перевищення = 3.5 В", FIELD,
         16, "канал налитий → малий R", "холодний"),
        (380, "звичайний",       "Vgs = 5 В,  Vth = 4 В",   "перевищення = 1 В",   POS,
         4,  "канал ледь живий → великий R", "гріється"),
    ]
    for x0, head, params, ov, ovcol, ch, rline, tline in cards:
        cx = x0 + 150
        f.append(rect(x0, 52, 300, 238, fill=BG, stroke="#c9d3dc", sw=1.4, rx=6))
        f.append(text(cx, 46, head, size=12, bold=True))
        f.append(text(cx, 84, params, size=11, bold=True))
        f.append(text(cx, 104, ov, size=10, color=ovcol, bold=True))
        # розріз
        f.append(rect(cx - 90, 150, 180, 60, fill=P_BODY, stroke=P_EDGE, sw=1.5, rx=0))
        f.append(rect(cx - 90, 134, 180, 8, fill=OXIDE, stroke=OX_EDG, sw=1.2, rx=0))
        f.append(rect(cx - 70, 120, 140, 12, fill=GATE, stroke=INK, sw=1.3, rx=0))
        f.append(text(cx, 130, "затвор 5В", size=9))
        f.append(rect(cx - 90, 150, 180, ch, fill=CHAN, stroke=NEG, sw=1.3, rx=0))
        f.append(text(cx, 232, rline, size=10, color=ovcol, bold=True))
        f.append(text(cx, 256, tline, size=10, color=ovcol, bold=True))
    f.append(text(W / 2, H - 8,
                  "Звіряй потрібну Vgs (і криву Rds(on)–Vgs) з тим, що дає твоє керування.",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(IMG, "logic-level.svg"), W, H, *f,
           title="Та сама напруга 5 В: логічного рівня vs звичайний")


# ════════════════════════════════════════════════════════════════════════════
# 6. square-law.svg — парабола Id = ½·k·(Vgs − Vth)²
# ════════════════════════════════════════════════════════════════════════════
def fig_square_law():
    W, H = 580, 400
    ox, oy, top, right = 90, 330, 66, 514
    f = [axes(ox, oy, top, right, "Vgs", "Id")]
    vth_x = 196.6
    k = 0.00265  # масштаб параболи (px на (px надлишку)²) — підібрано, щоб вершина не вилазила
    # поличка до Vth (синя)
    f.append(polyline([(ox, oy), (vth_x, oy)], NEG, sw=2.8))

    def yat(x):
        t = x - vth_x
        return max(top + 6, oy - k * t * t)
    # парабола
    pts = []
    x = vth_x
    while x <= 500:
        pts.append((x, max(top + 6, yat(x))))
        x += 3
    f.append(polyline(pts, POS, sw=2.8))
    # позначка Vth
    f.append(line(vth_x, oy, vth_x, oy + 8, color=INK, sw=1.6))
    f.append(text(vth_x, oy + 24, "Vth", size=12, bold=True))
    f.append(text(143, oy - 12, "канал закрито", size=9, color=NEG))
    f.append(text(143, oy - 26, "Id ≈ 0", size=9, color=NEG))
    # рівновіддалені кроки Vgs → дедалі більші кроки Id (пунктири)
    for sx in (333.1, 409.0, 484.8):
        sy = yat(sx)
        f.append(line(sx, oy, sx, sy, color=FIELD, sw=1.3, dash="4 3"))
        f.append(line(ox, sy, sx, sy, color=FIELD, sw=1.3, dash="4 3"))
        f.append(circle(sx, sy, 3.0, fill=POS, stroke=POS, sw=1))
    f.append(text(336, 200, "Id = ½·k·(Vgs − Vth)²", size=13, color=POS, bold=True))
    f.append(text(336, 222, "рівні кроки Vgs →", size=10, color=FIELD))
    f.append(text(336, 238, "дедалі більші кроки Id", size=10, color=FIELD))
    render(os.path.join(IMG, "square-law.svg"), W, H, *f,
           title="Передатна крива — це парабола (Vgs − Vth)²")


# ════════════════════════════════════════════════════════════════════════════
# 7. output-family.svg — сімейство Id(Vds) по одному на кожне Vov
# ════════════════════════════════════════════════════════════════════════════
def fig_output_family():
    W, H = 600, 400
    ox, oy, top, right = 80, 330, 64, 494
    f = [axes(ox, oy, top, right, "Vds", "Id")]
    # криві: підйом (тріод) до коліна Vds=Vov, далі поличка на ½·k·Vov²
    families = [
        (1, NEG,    160),   # (Vov, колір, x-коліна у px)
        (2, FIELD,  240),
        (3, OX_EDG, 320),
        (4, POS,    400),
    ]
    yscale = 14.5         # px висоти полички на одиницю ½·k·Vov² (Vov=1 → одиниця)
    for vov, col, knee_x in families:
        plateau = oy - yscale * (vov * vov)
        pts = []
        x = ox
        while x <= 480:
            if x <= knee_x:
                # парабола тріодної гілки, що гладко виходить на поличку в коліні
                t = (x - ox) / (knee_x - ox)         # 0..1
                y = oy - (plateau and (oy - plateau)) * (2 * t - t * t)
            else:
                y = plateau
            pts.append((x, y))
            x += 4
        f.append(polyline(pts, col, sw=2.6))
        f.append(text(486, plateau + 4, "Vov=%d" % vov, size=10, color=col, anchor="start", bold=True))
        f.append(circle(knee_x, plateau, 3.0, fill=col, stroke=BG, sw=1.6))
    f.append(text(288, 76, "висота поличок росте як квадрат → проміжки нерівні",
                  size=10, italic=True))
    f.append(text(200, 300, "коліно: Vds = Vov", size=9, color=MUTED))
    render(os.path.join(IMG, "output-family.svg"), W, H, *f,
           title="Звідки в даташиті сімейство кривих Id(Vds)")


# ════════════════════════════════════════════════════════════════════════════
# 8. dam-analogy.svg — гребля з порогом
# ════════════════════════════════════════════════════════════════════════════
def fig_dam_analogy():
    W, H = 720, 300
    f = []
    # ── ліва панель: закрито ──
    f.append(rect(40, 52, 300, 220, fill=BG, stroke="#c9d3dc", sw=1.4, rx=6))
    f.append(text(190, 46, "Vgs < Vth — закрито", size=12, bold=True))
    f.append(line(64, 150, 316, 150, color=MUTED, sw=1, dash="5 3"))
    f.append(text(316, 147, "Vth", size=9, color=MUTED, anchor="end", bold=True))
    f.append(rect(64, 178, 121, 66, fill=WATER, stroke=NEG, sw=1, rx=0))   # ставок-витік (нижче гребеня)
    f.append(rect(195, 228, 121, 16, fill=WATER, stroke=NEG, sw=1, rx=0))  # ставок-стік (порожній)
    f.append(text(124, 170, "рівень", size=9, color=NEG, bold=True))
    f.append(text(190, 98, "нижче гребеня — нема потоку", size=9, color=POS, bold=True))
    f.append(rect(185, 150, 10, 94, fill=DAMCOL, stroke=INK, sw=1.4, rx=0))
    f.append(text(190, 260, "гребля", size=9))
    # ── права панель: відкрито ──
    f.append(rect(380, 52, 300, 220, fill=BG, stroke="#c9d3dc", sw=1.4, rx=6))
    f.append(text(530, 46, "Vgs > Vth — відкрито", size=12, bold=True))
    f.append(line(404, 150, 656, 150, color=MUTED, sw=1, dash="5 3"))
    f.append(text(656, 147, "Vth", size=9, color=MUTED, anchor="end", bold=True))
    f.append(rect(404, 128, 121, 116, fill=WATER, stroke=NEG, sw=1, rx=0))  # ставок-витік (вище гребеня)
    f.append(rect(535, 196, 121, 48, fill=WATER, stroke=NEG, sw=1, rx=0))   # ставок-стік (натікає)
    f.append(line(518, 136, 545, 149, color=NEG, sw=2.4))                   # струмінь через гребінь
    f.append(arrowhead(547, 150, NEG, d=4, dir="down"))
    f.append(text(530, 98, "перелився — тече", size=9, color=FIELD, bold=True))
    f.append(rect(525, 150, 10, 94, fill=DAMCOL, stroke=INK, sw=1.4, rx=0))
    f.append(text(530, 260, "гребля", size=9))
    f.append(text(W / 2, H - 8,
                  "Нижче гребеня потоку нема; вище — потекло, і що вищий рівень, то рясніший потік (менший опір).",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(IMG, "dam-analogy.svg"), W, H, *f,
           title="Поріг як гребля: рівень води (Vgs) проти гребеня (Vth)")


if __name__ == "__main__":
    figs = [fig_three_stages, fig_inversion_layer, fig_threshold_transfer,
            fig_overdrive, fig_logic_level, fig_square_law,
            fig_output_family, fig_dam_analogy]
    for fn in figs:
        fn()
    print("OK: %d фігур у %s" % (len(figs), IMG))
