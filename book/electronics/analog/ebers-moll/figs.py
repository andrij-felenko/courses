# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── helpers ────────────────────────────────────────────────────────────────
def diode(x, y_from, y_to, tri_up, color=INK):
    """Вертикальний діод між y_from і y_to; tri_up — вістря (катод) угорі."""
    mid = (y_from + y_to) / 2.0
    th = 15
    p = []
    if tri_up:
        # анод унизу (mid+th), катод-планка вгорі (mid-th), вістря вгору
        p.append(line(x, y_from, x, mid - th, color, 2))
        p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="none" stroke="%s" stroke-width="2"/>'
                 % (x, mid - th, x - 12, mid + th, x + 12, mid + th, color))
        p.append(line(x - 13, mid - th, x + 13, mid - th, color, 2))
        p.append(line(x, mid + th, x, y_to, color, 2))
    else:
        # анод угорі (mid-th), катод-планка внизу (mid+th), вістря вниз
        p.append(line(x, y_from, x, mid - th, color, 2))
        p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="none" stroke="%s" stroke-width="2"/>'
                 % (x, mid + th, x - 12, mid - th, x + 12, mid - th, color))
        p.append(line(x - 13, mid + th, x + 13, mid + th, color, 2))
        p.append(line(x, mid + th, x, y_to, color, 2))
    return "".join(p)


def csource(x, y_from, y_to, arrow_up, color=INK):
    """Залежне джерело струму (коло зі стрілкою) між y_from і y_to."""
    mid = (y_from + y_to) / 2.0
    r = 20
    p = [circle(x, mid, r, fill=BG, stroke=color, sw=2)]
    p.append(line(x, y_from, x, mid - r, color, 2))
    p.append(line(x, mid + r, x, y_to, color, 2))
    if arrow_up:
        p.append(arrow(x, mid + r * 0.6, x, mid - r * 0.6, color, 2))
    else:
        p.append(arrow(x, mid - r * 0.6, x, mid + r * 0.6, color, 2))
    return "".join(p)


def dot(cx, cy, r=4, color=INK):
    return circle(cx, cy, r, fill=color, stroke=color, sw=1)


# ── figure 1: equivalent circuit ────────────────────────────────────────────
def fig_equiv():
    W, H = 660, 500
    LX, RX = 290, 470          # колонка діодів / колонка джерел
    CX = (LX + RX) / 2.0       # центр для виводів К та Е
    TY, MY, BY = 115, 258, 402  # верхня / середня / нижня шини
    p = []

    # шини
    p.append(line(LX, TY, RX, TY))          # верхня (до колектора)
    p.append(line(LX, MY, RX, MY))          # середня (до бази)
    p.append(line(LX, BY, RX, BY))          # нижня (до емітера)

    # виводи
    p.append(line(CX, TY, CX, 78))          # К
    p.append(dot(CX, 78)); p.append(text(CX, 62, "К  (колектор)", 14, INK))
    p.append(line(CX, BY, CX, 440))         # Е
    p.append(dot(CX, 440)); p.append(text(CX, 462, "Е  (емітер)", 14, INK))
    p.append(line(LX, MY, 150, MY))         # Б
    p.append(dot(150, MY)); p.append(text(138, MY + 5, "Б  (база)", 14, INK, anchor="end"))

    # діоди
    p.append(diode(LX, TY, MY, tri_up=True))    # D_C: струм I_R угору (база→колектор)
    p.append(diode(LX, MY, BY, tri_up=False))   # D_E: струм I_F униз (база→емітер)
    # джерела
    p.append(csource(RX, TY, MY, arrow_up=True))    # α_F·I_F у колектор
    p.append(csource(RX, MY, BY, arrow_up=False))   # α_R·I_R в емітер

    # підписи діодів (ліворуч)
    p.append(text(LX - 26, (TY + MY) / 2 - 6, "D_C", 12, MUTED, anchor="end"))
    p.append(text(LX - 26, (TY + MY) / 2 + 13, "I_R", 14, INK, anchor="end", italic=True))
    p.append(text(LX - 26, (MY + BY) / 2 - 6, "D_E", 12, MUTED, anchor="end"))
    p.append(text(LX - 26, (MY + BY) / 2 + 13, "I_F", 14, INK, anchor="end", italic=True))
    # підписи джерел (праворуч)
    p.append(text(RX + 28, (TY + MY) / 2 + 5, "α_F·I_F", 15, FIELD, anchor="start", bold=True))
    p.append(text(RX + 28, (MY + BY) / 2 + 5, "α_R·I_R", 15, NEG, anchor="start"))

    # напруги переходів (у проміжку між колонками)
    p.append(text(CX, (TY + MY) / 2 + 4, "V_BC", 12, MUTED, italic=True))
    p.append(text(CX, (MY + BY) / 2 + 4, "V_BE", 12, MUTED, italic=True))

    render(os.path.join(IMG, 'equivalent-circuit.svg'), W, H, "".join(p))


# ── figure 2: four regions map ──────────────────────────────────────────────
def fig_regions():
    W, H = 660, 470
    p = []
    # осі в проміжках між клітинами
    p.append(arrow(35, 250, 610, 250, INK, 2))     # горизонтальна: V_BE →
    p.append(arrow(310, 432, 310, 58, INK, 2))     # вертикальна:  V_BC ↑

    boxes = [
        # x, y, fill, title, [lines]
        (320, 78, "#fdf0e3", "Насичення",
         ["D_E: відкритий · D_C: відкритий", "V_КЕ → 0 — ключ відкритий"]),
        (55, 78, "#eaf0fd", "Обернено-активний",
         ["D_E: закритий · D_C: відкритий", "слабке підсилення (α_R малий)"]),
        (320, 275, "#e9f7ef", "Активний",
         ["D_E: відкритий · D_C: закритий", "I_К ≈ α_F·I_ES·e^(V_BE/Vₜ)"]),
        (55, 275, "#eef0f2", "Відсічка",
         ["D_E: закритий · D_C: закритий", "I ≈ 0 — ключ замкнений"]),
    ]
    bw, bh = 245, 145
    for x, y, fill, title, lines in boxes:
        cx = x + bw / 2
        p.append(rect(x, y, bw, bh, fill=fill, stroke=LINE, sw=1.5, rx=10))
        p.append(text(cx, y + 34, title, 16, INK, bold=True))
        p.append(mtext(cx, y + 66, lines, 12, "#374151"))

    # підписи осей
    p.append(text(600, 242, "V_BE", 13, INK, anchor="end", italic=True))
    p.append(text(322, 70, "V_BC", 13, INK, anchor="start", italic=True))
    p.append(text(330, 452, "→ праворуч: V_BE прямішає   ·   ↑ вгору: V_BC прямішає",
                  12, MUTED))
    render(os.path.join(IMG, 'regions-map.svg'), W, H, "".join(p))


# ── figure 3: output characteristics from the model ─────────────────────────
def fig_output():
    W, H = 760, 470
    x0, y0 = 82, 400        # початок координат
    xr, yt = 720, 60        # кінці осей
    Vce_max = 4.0
    Ic_max = 3.0            # мА
    sx = (xr - x0) / Vce_max
    sy = (y0 - yt) / Ic_max

    Vt = 0.02585
    IES = 1.0e-14
    aF, aR = 0.99, 0.5
    ICS = aF * IES / aR

    p = []
    # осі
    p.append(arrow(x0, y0, xr, y0, INK, 2))
    p.append(arrow(x0, y0, x0, yt, INK, 2))
    p.append(text(xr - 4, y0 + 30, "V_КЕ, В", 13, INK, anchor="end", italic=True))
    p.append(text(x0 - 46, yt + 6, "I_К, мА", 13, INK, anchor="start", italic=True))

    # поділки X
    for v in range(0, 5):
        px = x0 + v * sx
        p.append(line(px, y0, px, y0 + 5, INK, 1.4))
        p.append(text(px, y0 + 22, str(v), 12, MUTED))
    # поділки Y
    for i in range(0, 4):
        py = y0 - i * sy
        p.append(line(x0 - 5, py, x0, py, INK, 1.4))
        p.append(text(x0 - 14, py + 4, str(i), 12, MUTED, anchor="end"))

    curves = [(0.60, MUTED), (0.65, NEG), (0.68, POS)]
    for Vbe, col in curves:
        plateau = aF * IES * (math.exp(Vbe / Vt) - 1.0)
        pts = []
        vce = 0.0
        while vce <= Vce_max + 1e-9:
            Vbc = Vbe - vce
            Ic = aF * IES * (math.exp(Vbe / Vt) - 1.0) - ICS * (math.exp(Vbc / Vt) - 1.0)
            ic_mA = Ic * 1000.0
            if ic_mA < 0:
                ic_mA = 0.0
            if ic_mA > Ic_max:
                ic_mA = Ic_max
            px = x0 + vce * sx
            py = y0 - ic_mA * sy
            pts.append("%.1f,%.1f" % (px, py))
            vce += 0.02
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (" ".join(pts), col))
        # підпис праворуч від плато
        py_lab = y0 - min(plateau * 1000.0, Ic_max) * sy
        p.append(text(xr - 6, py_lab - 8, "V_BE = %.2f В" % Vbe, 12, col, anchor="end"))

    render(os.path.join(IMG, 'output-characteristics.svg'), W, H, "".join(p))


# ── figure 4: historical timeline (для hist-вставки) ─────────────────────────
def fig_timeline():
    W, H = 720, 630
    spine_x = 176
    top, step = 74, 62
    rows = [
        ("1947", "Точковий транзистор — Бардін і Браттейн", False),
        ("1948", "Шоклі задумує площинний транзистор", False),
        ("1949", "Шоклі публікує теорію p-n-переходів", False),
        ("1951", "Перший площинний транзистор · Еберс у Bell Labs", False),
        ("1954", "МОДЕЛЬ ЕБЕРСА — МОЛЛА · Proc. IRE, грудень", True),
        ("1959", "Еберс помирає, 37 років", False),
        ("1970", "Модель Ґуммеля — Пуна — наступний крок", False),
        ("1971", "Премія Дж. Дж. Еберса · перший лауреат — Молл", False),
        ("1972", "SPICE (Берклі): Еберс — Молл усередині", False),
    ]
    p = []
    y_first, y_last = top, top + (len(rows) - 1) * step
    p.append(line(spine_x, y_first - 26, spine_x, y_last + 26, LINE, 2))
    for i, (yr, label, hot) in enumerate(rows):
        ry = top + i * step
        if hot:
            bx, bw, bh = spine_x + 24, 486, 42
            p.append(rect(bx, ry - bh / 2, bw, bh, fill="#e9f7ef", stroke=FIELD, sw=1.6, rx=9))
            p.append(text(bx + 18, ry + 5, label, 14, "#1a1a1a", anchor="start", bold=True))
            p.append(circle(spine_x, ry, 8, fill=FIELD, stroke=FIELD, sw=1))
            p.append(text(spine_x - 38, ry + 6, yr, 16, FIELD, anchor="end", bold=True))
        else:
            p.append(circle(spine_x, ry, 5, fill=INK, stroke=INK, sw=1))
            p.append(text(spine_x - 38, ry + 6, yr, 15, INK, anchor="end", bold=True))
            p.append(text(spine_x + 42, ry + 5, label, 14, "#374151", anchor="start"))
    render(os.path.join(IMG, 'timeline.svg'), W, H, "".join(p))


# ── figure: the operating-point circuit (для proj-вставки) ──────────────────
def fig_op_circuit():
    W, H = 720, 540
    p = []
    BARx = 430
    Ccol = 478                      # колонка колектор/емітер
    p.append(line(BARx, 218, BARx, 282, INK, 3))          # база-стовпчик
    p.append(line(360, 250, BARx, 250, INK, 2))           # база-вивід
    p.append(line(BARx, 228, Ccol, 200, INK, 2))          # колектор-вивід
    p.append(line(Ccol, 200, Ccol, 144, INK, 2))
    p.append(arrow(BARx, 272, Ccol, 300, INK, 2))         # емітер (стрілка назовні = n-p-n)
    p.append(line(Ccol, 300, Ccol, 358, INK, 2))
    # R_C
    p.append(rect(Ccol - 12, 86, 24, 58, fill=BG, stroke=INK, sw=2, rx=3))
    p.append(line(Ccol, 86, Ccol, 60, INK, 2))
    p.append(dot(Ccol, 60)); p.append(text(Ccol, 46, "+5 В  (V_CC)", 13, INK))
    p.append(text(Ccol + 20, 118, "R_C = 1 кΩ", 13, INK, anchor="start"))
    p.append(dot(Ccol, 172)); p.append(text(Ccol + 16, 168, "V_C", 14, FIELD, anchor="start", bold=True))
    # R_B
    p.append(rect(250, 238, 70, 24, fill=BG, stroke=INK, sw=2, rx=3))
    p.append(line(320, 250, 360, 250, INK, 2))
    p.append(line(180, 250, 250, 250, INK, 2))
    p.append(dot(180, 250)); p.append(text(168, 254, "+5 В", 13, INK, anchor="end"))
    p.append(text(150, 238, "(V_BB)", 12, MUTED, anchor="end"))
    p.append(text(285, 230, "R_B = 220 кΩ", 13, INK))
    p.append(dot(360, 250)); p.append(text(360, 236, "V_B", 14, FIELD, anchor="middle", bold=True))
    # виводи транзистора
    p.append(text(452, 208, "К", 12, MUTED, anchor="end"))
    p.append(text(418, 244, "Б", 12, MUTED, anchor="end"))
    p.append(text(452, 300, "Е", 12, MUTED, anchor="start"))
    # земля
    p.append(line(Ccol, 358, Ccol, 372, INK, 2))
    p.append(line(Ccol - 20, 372, Ccol + 20, 372, INK, 2))
    p.append(line(Ccol - 13, 379, Ccol + 13, 379, INK, 2))
    p.append(line(Ccol - 6, 386, Ccol + 6, 386, INK, 2))
    # легенда рівнянь
    lx, ly, lw, lh = 512, 320, 190, 150
    p.append(rect(lx, ly, lw, lh, fill=FILL, stroke=LINE, sw=1.4, rx=8))
    p.append(text(lx + lw/2, ly + 26, "Рівняння вузлів (KCL)", 13, INK, bold=True))
    p.append(mtext(lx + lw/2, ly + 58,
                   ["(V_BB−V_B)/R_B = I_Б", "(V_CC−V_C)/R_C = I_К"], 13, "#374151", lh=1.5))
    p.append(mtext(lx + lw/2, ly + 118,
                   ["два рівняння,", "два невідомі: V_B, V_C"], 12, MUTED, lh=1.35))
    render(os.path.join(IMG, 'op-circuit.svg'), W, H, "".join(p))


# ── figure: one Newton step overshoots (why damping is needed) ──────────────
def fig_newton_step():
    W, H = 720, 470
    x0, y0, xr, yt = 90, 400, 660, 70
    def X(x): return x0 + x * (xr - x0)
    def Y(y): return y0 - y * (y0 - yt)
    import math as _m
    p = []
    p.append(arrow(x0, y0, xr + 8, y0, INK, 2))
    p.append(arrow(x0, y0, x0, yt - 8, INK, 2))
    p.append(text(xr + 4, y0 + 28, "напруга на переході  V", 13, INK, anchor="end", italic=True))
    p.append(text(x0 - 10, yt - 4, "струм  I", 13, INK, anchor="end", italic=True))
    pts = []
    x = 0.18
    while x <= 0.985:
        pts.append("%.1f,%.1f" % (X(x), Y(_m.exp(6*(x-1)))))
        x += 0.01
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), INK))
    p.append(text(X(0.93), Y(0.80) - 4, "I = Iₛ·e^(V/Vₜ)", 13, INK, anchor="end"))
    p.append(line(X(0.15), Y(0.40), X(1.0), Y(0.30), MUTED, 1.8, dash="6 4"))
    p.append(text(X(0.17), Y(0.40) - 8, "лінія навантаження", 12, MUTED, anchor="start"))
    xs = 0.822
    p.append(dot(X(xs), Y(_m.exp(6*(xs-1))), 5, FIELD))
    p.append(text(X(xs) + 6, Y(_m.exp(6*(xs-1))) - 10, "розв'язок V*", 12, FIELD, anchor="start", bold=True))
    x0g = 0.50
    f0 = _m.exp(6*(x0g-1)); g0 = 6*f0
    p.append(dot(X(x0g), Y(f0), 5, POS))
    p.append(text(X(x0g) - 8, Y(f0) + 16, "наближення V₀", 12, POS, anchor="end", bold=True))
    xt = 1.0
    p.append(line(X(x0g), Y(f0), X(xt), Y(f0 + g0*(xt - x0g)), POS, 2, dash="2 3"))
    p.append(arrow(X(0.93), Y(f0 + g0*(0.93 - x0g)), X(1.02), Y(f0 + g0*(1.02 - x0g)), POS, 2))
    p.append(mtext(X(0.205), Y(0.90),
                   ["дотична (лінійна модель) полога —", "перетинає навантаження далеко за краєм:",
                    "крок кида V₁ ≫ V*, де e^(V/Vₜ) вибухає"],
                   12, POS, anchor="start", lh=1.4))
    xl = 0.62
    p.append(arrow(X(x0g), Y(f0), X(xl), Y(_m.exp(6*(xl-1))), FIELD, 2.4))
    p.append(text(X(xl) + 10, Y(_m.exp(6*(xl-1))) + 26, "обмежений крок (pnjlim):", 12, FIELD, anchor="start", bold=True))
    p.append(text(X(xl) + 10, Y(_m.exp(6*(xl-1))) + 42, "не далі кількох Vₜ", 12, FIELD, anchor="start"))
    render(os.path.join(IMG, 'op-newton-step.svg'), W, H, "".join(p))


# ── figure: convergence trace, damped vs undamped ───────────────────────────
def fig_op_convergence():
    W, H = 720, 470
    x0, y0, xr, yt = 92, 400, 660, 70
    NIT = 10
    Vmax = 0.8
    sx = (xr - x0) / (NIT + 0.5)
    sy = (y0 - yt) / Vmax
    p = []
    p.append(arrow(x0, y0, xr + 8, y0, INK, 2))
    p.append(arrow(x0, y0, x0, yt - 8, INK, 2))
    p.append(text(xr + 4, y0 + 28, "номер ітерації  k", 13, INK, anchor="end", italic=True))
    p.append(text(x0 - 12, yt - 4, "V_BE, В", 13, INK, anchor="end", italic=True))
    for k in range(0, NIT + 1):
        px = x0 + k * sx
        p.append(line(px, y0, px, y0 + 5, INK, 1.3))
        p.append(text(px, y0 + 22, str(k), 12, MUTED))
    for i in range(0, 5):
        vv = i * 0.2
        py = y0 - vv * sy
        p.append(line(x0 - 5, py, x0, py, INK, 1.3))
        p.append(text(x0 - 12, py + 4, "%.1f" % vv, 12, MUTED, anchor="end"))
    Vsol = 0.672
    p.append(line(x0, y0 - Vsol*sy, xr, y0 - Vsol*sy, FIELD, 1.4, dash="6 4"))
    p.append(text(xr - 4, y0 - Vsol*sy - 8, "V_BE* = 0.672 В", 12, FIELD, anchor="end", bold=True))
    damp = [0.136, 0.272, 0.406, 0.540, 0.655, 0.679, 0.673, 0.672, 0.672, 0.672]
    pts = []
    for k, v in enumerate(damp):
        pts.append("%.1f,%.1f" % (x0 + k*sx, y0 - v*sy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), NEG))
    for k, v in enumerate(damp):
        p.append(dot(x0 + k*sx, y0 - v*sy, 3.5, NEG))
    p.append(text(x0 + 5.9*sx, y0 - 0.34*sy, "з обмеженням кроку —", 12, NEG, anchor="start", bold=True))
    p.append(text(x0 + 5.9*sx, y0 - 0.34*sy + 16, "монотонно сходиться", 12, NEG, anchor="start"))
    p.append(dot(x0, y0 - 0.0*sy, 3.5, POS))
    p.append(arrow(x0, y0 - 0.02*sy, x0 + 1.0*sx, yt - 2, POS, 2.6))
    p.append(text(x0 + 1.3*sx, yt + 24, "без обмеження:", 12, POS, anchor="start", bold=True))
    p.append(text(x0 + 1.3*sx, yt + 40, "V₁ = 5 В, далі → ∞ (переповнення)", 12, POS, anchor="start"))
    render(os.path.join(IMG, 'op-convergence.svg'), W, H, "".join(p))


# ── insert figures: math-ebers-moll-derivation ──────────────────────────────
def _xmark(cx, cy, r=9, color=POS):
    return (line(cx - r, cy - r, cx + r, cy + r, color, 2.4) +
            line(cx - r, cy + r, cx + r, cy - r, color, 2.4))


# ── figure A: minority-carrier profile in the base ──────────────────────────
def fig_base_profile():
    W, H = 760, 500
    x0, xW = 190, 560
    yT, yB = 150, 375
    EML, COR = 95, 655            # ліва межа емітера / права межа колектора
    p = []

    # шари: емітер n⁺ | база p | колектор n
    p.append(rect(EML, 130, x0 - EML, 270, fill="#eaf0fd", stroke=LINE, sw=1, rx=0))
    p.append(rect(x0, 130, xW - x0, 270, fill="#fdecea", stroke=LINE, sw=1, rx=0))
    p.append(rect(xW, 130, COR - xW, 270, fill="#eaf0fd", stroke=LINE, sw=1, rx=0))
    p.append(mtext((EML + x0) / 2, 296, ["емітер", "n⁺"], 13, INK))
    p.append(mtext((xW + COR) / 2, 296, ["колектор", "n"], 13, INK))
    p.append(text(300, 362, "база (p)", 13, INK))

    # осі
    p.append(arrow(x0, 395, x0, 138, INK, 1.8))
    p.append(text(x0 - 12, 150, "n′", 14, INK, anchor="end", italic=True))
    p.append(arrow(x0, yB, 585, yB, INK, 1.8))
    p.append(text(590, yB + 4, "x", 14, INK, anchor="start", italic=True))
    p.append(line(x0, yB, x0, yB + 5, INK, 1.4)); p.append(text(x0, yB + 22, "0", 12, MUTED))
    p.append(line(xW, yB, xW, yB + 5, INK, 1.4)); p.append(text(xW, yB + 22, "W_B", 12, MUTED))

    # точний профіль (з рекомбінацією) — трохи провисає; прогин перебільшено
    u = 1.0
    sh = math.sinh(u)
    pts = []
    k = 0
    while k <= 40:
        xx = k / 40.0                       # 0..1 уздовж бази
        val = math.sinh(u * (1 - xx)) / sh   # n′(x)/n′(0), активний режим
        px = x0 + xx * (xW - x0)
        py = yB - val * (yB - yT)
        pts.append("%.1f,%.1f" % (px, py))
        k += 1
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5 4"/>'
             % (" ".join(pts), MUTED))
    # ідеалізований (тонка база) — пряма
    p.append(line(x0, yT, xW, yB, NEG, 2.6))
    p.append(dot(x0, yT, 4, NEG)); p.append(dot(xW, yB, 4, NEG))

    # анотація дифузійного струму (у порожньому куті над лінією) — конектор веде
    # від НИЖНЬОГО краю текстового блоку (не крізь останній рядок) до діагоналі
    p.append(mtext(470, 178, ["нахил профілю =", "дифузійний струм", "I_n = q·A·D_n·dn′/dx"],
                   12, INK))
    p.append(line(470, 224, 412, 280, MUTED, 1.2))

    # значення на межах — рамки з винесенням
    p.append(fitbox(180, 52, 300, 44, "n′(0) = n_B0·(e^(V_BE/Vₜ) − 1)", 13,
                    fill="#eef7f0", stroke=FIELD))
    p.append(line(300, 96, 196, 148, MUTED, 1.2))
    p.append(fitbox(392, 434, 336, 44, "n′(W_B) = n_B0·(e^(V_BC/Vₜ) − 1) ≈ 0", 13,
                    fill="#eef2f7", stroke=NEG))
    # конектор до осі x у двох сегментах — обходить підпис «W_B» на осі (не крізь текст)
    p.append(line(560, 434, 560, 404, MUTED, 1.2))
    p.append(line(560, 388, 560, 379, MUTED, 1.2))

    render(os.path.join(IMG, 'base-profile.svg'), W, H, "".join(p))


# ── figure B: transit vs recombination race ─────────────────────────────────
def fig_transit():
    W, H = 720, 470
    EL, BL, BR, CR = 70, 160, 560, 650   # межі емітера/бази/колектора
    bt, bb = 130, 270                    # верх/низ базового шару (зсунуто вниз — місце під два підписи згори)
    p = []
    p.append(rect(EL, bt, BL - EL, bb - bt, fill="#eaf0fd", stroke=LINE, sw=1, rx=0))
    p.append(rect(BL, bt, BR - BL, bb - bt, fill="#fdecea", stroke=LINE, sw=1, rx=0))
    p.append(rect(BR, bt, CR - BR, bb - bt, fill="#eaf0fd", stroke=LINE, sw=1, rx=0))
    p.append(text((EL + BL) / 2, (bt + bb) / 2 + 5, "емітер", 12, INK))
    p.append(text((BR + CR) / 2, (bt + bb) / 2 + 5, "колектор", 12, INK))
    p.append(text((BL + BR) / 2, bt - 16, "база (тонка, W_B ≪ L_n)", 13, INK))

    # електрони, що долітають (більшість)
    for yy in (155, 188, 221):
        p.append(arrow(BL + 4, yy, BR - 4, yy, FIELD, 2.2))
    # підпис-анотація рознесений далеко вгору від заголовка боксу — без накладання
    p.append(text((BL + BR) / 2, 40, "майже всі долітають до колектора", 12, FIELD))

    # рідкісна рекомбінація → струм бази
    p.append(line(BL + 4, 251, 360, 251, POS, 2.2))
    p.append(_xmark(360, 251, 8, POS))
    p.append(text(372, 255, "рекомбінація → I_Б", 12, POS, anchor="start"))

    # два годинники: τ_B малий, τ_n великий
    p.append(text(EL, 325, "гонка двох часів:", 13, INK, anchor="start", bold=True))
    p.append(rect(EL, 340, 70, 16, fill=NEG, stroke=NEG, sw=1, rx=3))
    p.append(text(EL + 82, 353, "τ_B — проліт бази  =  W_B²/(2·D_n)", 12, INK, anchor="start"))
    p.append(rect(EL, 372, 380, 16, fill=MUTED, stroke=MUTED, sw=1, rx=3))
    p.append(text(EL + 392, 385, "τ_n — час життя", 12, INK, anchor="start"))
    p.append(text(EL, 428, "втрачена частка = τ_B/τ_n   →   α_T ≈ 1 − τ_B/τ_n",
                  14, INK, anchor="start", bold=True))

    render(os.path.join(IMG, 'transit-race.svg'), W, H, "".join(p))


# ── figure C: reciprocity — one shared transfer coefficient ─────────────────
def fig_reciprocity():
    W, H = 740, 360
    p = []
    # центральний вузол — спільний перенос
    p.append(fitbox(255, 118, 230, 100,
                    "I_S\nперенос крізь базу\nq·A·D_n·n_B0\n────────────\nL_n·sinh(W_B/L_n)",
                    14, fill="#eef7f0", stroke=FIELD))
    # прямий хід (ліворуч)
    p.append(fitbox(30, 120, 170, 84,
                    "прямий хід\nV_BE вганяє,\nколектор збирає", 13,
                    fill="#eef2f7", stroke=NEG))
    p.append(arrow(202, 158, 252, 166, NEG, 2.4))
    p.append(text(227, 148, "α_F·I_ES", 14, NEG, bold=True))
    # обернений хід (праворуч)
    p.append(fitbox(540, 120, 172, 84,
                    "обернений хід\nV_BC вганяє,\nемітер збирає", 13,
                    fill="#fdecea", stroke=POS))
    p.append(arrow(538, 158, 488, 166, POS, 2.4))
    p.append(text(513, 148, "α_R·I_CS", 14, POS, bold=True))
    # підсумкова рівність
    p.append(text(W / 2, 300, "α_F·I_ES  =  α_R·I_CS  =  I_S", 20, INK, bold=True))
    p.append(text(W / 2, 328, "один потік крізь базу — один коефіцієнт", 12, MUTED))
    render(os.path.join(IMG, 'reciprocity.svg'), W, H, "".join(p))


if __name__ == '__main__':
    fig_equiv()
    fig_regions()
    fig_output()
    fig_timeline()
    fig_op_circuit()
    fig_newton_step()
    fig_op_convergence()
    fig_base_profile()
    fig_transit()
    fig_reciprocity()
    print("figs done:", os.listdir(IMG))
