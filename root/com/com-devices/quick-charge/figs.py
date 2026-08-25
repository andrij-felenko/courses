# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

QC = "#7a4fb0"   # фіолетовий — усе «квіккарджеве»


# ── why-volts: чому підіймають вольти, а не ампери ────────────────────────────
# Ідея не в самих втратах, а в ЗАПАСІ: при 5 В на пристрій доходить менше, ніж
# треба комірці з запасом на перетворювач — глухий кут не за ККД, а за фізикою.

def fig_why_volts():
    W, H = 780, 410
    p = []
    panels = [
        (40, 205, "5 В — стеля легасі", POS, "#fdecea",
         ["18 Вт ÷ 5 В = 3.6 А",
          "втрати в шнурі: 3.6² × 0.2 = 2.6 Вт",
          "падіння: 3.6 × 0.2 = 0.72 В"],
         "доходить 4.28 В",
         ["комірці треба 4.2 В, та ще й", "запас перетворювачеві зверху", "→ запасу не лишилось узагалі"]),
        (410, 575, "9 В — Quick Charge", FIELD, "#eafaf0",
         ["18 Вт ÷ 9 В = 2.0 А",
          "втрати в шнурі: 2.0² × 0.2 = 0.8 Вт",
          "падіння: 2.0 × 0.2 = 0.40 В"],
         "доходить 8.60 В",
         ["перетворювач спокійно", "знижує 8.6 В до 4.2 В", "→ запасу вдосталь"]),
    ]
    for x0, cx, head, col, fill, rows, big, tail in panels:
        p.append(rect(x0, 62, 330, 272, fill=fill, stroke=col, sw=1.5, rx=10))
        p.append(text(cx, 90, head, size=14, color=col, bold=True))
        p.append(line(x0 + 26, 102, x0 + 304, 102, color=col, sw=1.0))
        for i, r in enumerate(rows):
            p.append(text(cx, 128 + i * 26, r, size=12, color=INK))
        p.append(text(cx, 234, big, size=18, color=col, bold=True))
        for i, t in enumerate(tail):
            p.append(text(cx, 268 + i * 21, t, size=11,
                          color=col if i == 2 else MUTED, bold=(i == 2)))

    b, bw, bh = textbox(W / 2, 376,
                        "та сама потужність, той самий шнур 0.2 Ом: утричі менші втрати — і, головне, живий запас напруги",
                        size=11, fill="#eef4ff", stroke=NEG, sw=1.3, pad=9)
    p.append(b)

    render(os.path.join(OUT, "why-volts.svg"), W, H, *p,
           title="18 ватів по одному шнуру: п'ять вольтів проти дев'яти")


# ── three-states: дві межі роблять із лінії даних канал на три стани ──────────
# Ідея: блок читає кожну лінію двома компараторами (0.325 В і 2 В), тож на ній
# розрізняються ТРИ стани, а не два. Звідси й береться простір кодів.

def fig_three_states():
    W, H = 760, 450
    p = []
    AX = 210
    Y0, Y36 = 384, 100
    k = (Y0 - Y36) / 3.6

    def y(v):
        return Y0 - v * k

    p.append(text(AX, 66, "напруга на лінії даних (D+ або D−)", size=12, color=MUTED))
    p.append(line(AX, Y36 - 8, AX, Y0 + 12, color=INK, sw=2.0))

    # межі — пунктиром управо, підписи ще правіше
    for v, lab, col in [(0.325, "0.325 В — межа «є сигнал»", "#b8901f"),
                        (2.0, "2 В — межа «низький / високий»", QC)]:
        p.append(line(AX, y(v), 452, y(v), color=col, sw=1.5, dash="6 4"))
        p.append(text(462, y(v) + 4, lab, size=11, color=col, anchor="start", bold=True))

    # стани — крапки на осі, назви ліворуч, пояснення праворуч від осі
    states = [
        (0.0, "GND", "лінія притиснута до землі", MUTED),
        (0.6, "0.6 В", "«низький» — успадковано з BC1.2", NEG),
        (3.3, "3.3 В", "«високий»", POS),
    ]
    for v, name, note, col in states:
        p.append(circle(AX, y(v), 6.5, fill=col, stroke=col, sw=1.5))
        p.append(text(AX - 18, y(v) + 5, name, size=13, color=col, anchor="end", bold=True))
        p.append(text(AX + 20, y(v) - 9, note, size=11, color=INK, anchor="start"))

    b, bw, bh = textbox(W / 2, 424,
                        "дві межі → три розрізненні стани на КОЖНІЙ лінії; двох ліній уже досить, щоб закодувати напругу",
                        size=11, fill="#eafaf0", stroke=FIELD, sw=1.3, pad=9)
    p.append(b)

    render(os.path.join(OUT, "three-states.svg"), W, H, *p,
           title="Як із двох ліній даних зробили канал")


# ── hvdcp-handshake: послідовність рукостискання ──────────────────────────────
# Ідея: 1.25 с утримання — не затримка, а запобіжник: стільки жоден випадковий
# стан ліній не протримається, а ціна помилки — 12 В у п'ятивольтовому пристрої.

def fig_hvdcp_handshake():
    W, H = 800, 520
    p = []
    MX = 250

    def step(cy, s, col, fill):
        b, bw, bh = textbox(MX, cy, s, size=11.5, bold=True, color=col,
                            fill=fill, stroke=col, sw=1.6, min_w=350, pad=11)
        p.append(b)
        return bh

    step(78, "VBUS = 5 В · за BC1.2 це DCP\n(D+ замкнено на D− усередині блока)", INK, FILL)
    p.append(arrow(MX, 116, MX, 152, color=INK, sw=1.6))
    step(178, "пристрій кладе на D+ 0.6 В\nі НЕ відпускає", NEG, "#eef4ff")
    p.append(arrow(MX, 216, MX, 252, color=INK, sw=1.6))
    step(284, "блок розмикає перемичку D+/D−\nі тягне D− донизу через ≈20 кОм", QC, "#f2ecf8")
    p.append(arrow(MX, 322, MX, 358, color=INK, sw=1.6))
    step(388, "D− упала нижче 0.325 В →\nблок уміє Quick Charge", FIELD, "#eafaf0")
    p.append(arrow(MX, 424, MX, 456, color=INK, sw=1.6))
    step(482, "пристрій виставляє код → VBUS росте", INK, FILL)

    # бічні примітки
    sb, sw_, sh = textbox(620, 178, "≥ 1.25 с утримання\n(типово 1250 мс, межі 1000–1500)\nстільки не протримається\nжоден випадковий стан ліній",
                          size=10.5, fill="#eef4ff", stroke=NEG, sw=1.2, pad=9, color=INK)
    p.append(sb)
    sb2, _, _ = textbox(620, 388, "якщо D− лишилась високою —\nце звичайний DCP:\n5 В, і по тому",
                        size=10.5, fill="#fdf6e3", stroke="#b8901f", sw=1.2, pad=9, color=INK)
    p.append(sb2)
    p.append(text(452, 486, "перемикання — через 20–60 мс", size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "hvdcp-handshake.svg"), W, H, *p,
           title="Рукостискання HVDCP")


# ── code-grid: увесь простір кодів QC2.0 на одній сітці ───────────────────────
# Ідея: два рівні D+ × три стани D− = шість клітин, п'ять із яких зайняті. Уся
# «мова» протоколу вміщається в цю табличку — і одна клітина веде в QC3.0.

def fig_code_grid():
    W, H = 760, 420
    p = []
    X0, CW, GAP = 210, 170, 8
    ROWS = [(150, "D+ = 0.6 В"), (262, "D+ = 3.3 В")]
    RH = 100
    cols = ["D− = GND", "D− = 0.6 В", "D− = 3.3 В"]

    for j, c in enumerate(cols):
        p.append(text(X0 + j * (CW + GAP) + CW / 2, 118, c, size=12, color=INK, bold=True))
    for y0, lab in ROWS:
        p.append(text(X0 - 16, y0 + RH / 2 + 5, lab, size=12, color=INK, anchor="end", bold=True))

    cells = {
        (0, 0): ("5 В", "звичайний старт", NEG, "#eef4ff"),
        (0, 1): ("12 В", "", NEG, "#eef4ff"),
        (0, 2): ("QC3.0", "безперервний режим", FIELD, "#eafaf0"),
        (1, 0): ("—", "не вживається", MUTED, "#f2f2f2"),
        (1, 1): ("9 В", "", NEG, "#eef4ff"),
        (1, 2): ("20 В", "лише Class B", QC, "#f2ecf8"),
    }
    for (i, j), (big, note, col, fill) in cells.items():
        x = X0 + j * (CW + GAP)
        y = ROWS[i][0]
        p.append(rect(x, y, CW, RH, fill=fill, stroke=col, sw=1.6, rx=8))
        p.append(text(x + CW / 2, y + (48 if note else 60), big,
                      size=24 if big != "QC3.0" else 17, color=col, bold=True))
        if note:
            p.append(text(x + CW / 2, y + 76, note, size=10.5, color=MUTED))

    p.append(text(W / 2, 84, "два рівні на D+ × три стани D− — уся мова протоколу", size=12, color=MUTED))

    b, bw, bh = textbox(W / 2, 392,
                        "Class A — 5/9/12 В; Class B додає 20 В. Клітина 0.6/3.3 не задає напругу, а відмикає крок по 200 мВ.",
                        size=11, fill=FILL, stroke=LINE, sw=1.3, pad=9)
    p.append(b)

    render(os.path.join(OUT, "code-grid.svg"), W, H, *p,
           title="Коди напруги Quick Charge 2.0")


# ── inov-efficiency: пік ККД, повз який б'є сітка 5/9/12 ──────────────────────
# Ідея (за виміром TI): ККД заряду має ПІК близько 6.4 В, а не росте з напругою.
# Груба сітка QC2.0 у пік не влучає; крок 200 мВ QC3.0 — влучає. Ось нащо INOV.

def fig_inov_efficiency():
    W, H = 800, 460
    p = []
    PX0, PX1, PY0, PY1 = 130, 710, 108, 340
    VMIN, VMAX = 4.5, 13.0
    EMIN, EMAX = 85.0, 95.0

    def x(v):
        return PX0 + (v - VMIN) * (PX1 - PX0) / (VMAX - VMIN)

    def y(e):
        return PY1 - (e - EMIN) * (PY1 - PY0) / (EMAX - EMIN)

    curve = [(4.8, 91.0), (5.0, 92.0), (5.5, 93.4), (6.0, 94.3), (6.4, 94.6),
             (7.0, 94.2), (8.0, 93.0), (9.0, 91.6), (10.0, 90.3), (11.0, 89.0),
             (12.0, 87.8), (12.8, 87.0)]

    def eff(v):
        for i in range(len(curve) - 1):
            a, b = curve[i], curve[i + 1]
            if a[0] <= v <= b[0]:
                t = (v - a[0]) / (b[0] - a[0])
                return a[1] + t * (b[1] - a[1])
        return curve[-1][1]

    # сітка + осі
    for e in (85, 90, 95):
        p.append(line(PX0, y(e), PX1, y(e), color="#dcdcdc", sw=1.0))
        p.append(text(PX0 - 12, y(e) + 4, "%d%%" % e, size=11, color=MUTED, anchor="end"))
    p.append(line(PX0, PY0 - 6, PX0, PY1, color=INK, sw=1.8))
    p.append(line(PX0, PY1, PX1 + 6, PY1, color=INK, sw=1.8))
    p.append(text(66, 224, "ККД", size=12, color=MUTED, bold=True))
    p.append(text(58, 242, "заряду", size=12, color=MUTED, bold=True))
    p.append(text((PX0 + PX1) / 2, 392, "VBUS, яку блок подає в пристрій, В", size=12, color=INK, bold=True))

    # крива
    pts = " ".join("%.1f,%.1f" % (x(v), y(e)) for v, e in curve)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, INK))

    # позначки QC2.0 — повз пік
    for v in (5, 9, 12):
        p.append(circle(x(v), y(eff(v)), 6, fill="#fdecea", stroke=POS, sw=2.2))
        p.append(text(x(v), PY1 + 22, "%d В" % v, size=11, color=POS, bold=True))
    # пік — QC3.0
    p.append(circle(x(6.4), y(94.6), 7.5, fill="#eafaf0", stroke=FIELD, sw=2.6))
    p.append(text(x(6.4), PY1 + 22, "6.4 В", size=11, color=FIELD, bold=True))
    p.append(text(x(6.4), 90, "пік ККД ≈ 6.4 В", size=12, color=FIELD, bold=True))

    p.append(text(PX1, 132, "вище — не краще:", size=11, color=MUTED, anchor="end"))
    p.append(text(PX1, 150, "перепад палить ККД", size=11, color=MUTED, anchor="end"))

    legs = [(250, "QC2.0: сітка 5 / 9 / 12 В — повз пік", POS, "#fdecea"),
            (560, "QC3.0 (INOV): крок 200 мВ — точно в пік", FIELD, "#eafaf0")]
    for cx, s, col, fill in legs:
        b, bw, bh = textbox(cx, 428, s, size=11, fill=fill, stroke=col, sw=1.3, pad=9, color=INK)
        p.append(b)

    render(os.path.join(OUT, "inov-efficiency.svg"), W, H, *p,
           title="Форма виміряної TI кривої: bq25890H + QC3.0-адаптер, VBAT = 3.8 В")


# ══ Фігури математичної вставки math-hvdcp-optimum ═══════════════════════════
# Скелет моделі: P(V) = A/V² + B·V + C, де A = (Vb·Io)²·Rs, B = ½·κ·Io.
# Числа — ті самі, що у вставці: вони відтворюють виміряний TI пік 6.4 В.

M_VB, M_IO, M_RS, M_KAPPA = 3.8, 3.0, 0.045, 0.03
M_VHEAD = 0.30
M_A = (M_VB * M_IO) ** 2 * M_RS          # 5.848 Вт·В²
M_B = 0.5 * M_KAPPA * M_IO               # 0.045 Вт/В
M_VOPT = (2 * M_A / M_B) ** (1.0 / 3.0)  # 6.38 В


def _legend(p, cy, items):
    """Рядок легенди: [(cx, підпис, колір, заливка)] — рамки самі під текст."""
    for cx, s, col, fill in items:
        b, _, _ = textbox(cx, cy, s, size=11, fill=fill, stroke=col, sw=1.4,
                          pad=9, color=INK)
        p.append(b)


# ── loss-split: звідки береться мінімум ───────────────────────────────────────
# Ідея: спадний доданок A/V² (Джоуль на всьому, що ПЕРЕД ключем) і зростальний
# B·V (переліт ключа) дають суму з мінімумом. Ключове й неочевидне: на дні
# доданки стоять не порівну, а рівно 1:2 — бо в них різні степені V.

def fig_loss_split():
    W, H = 880, 600
    p = []
    PX0, PX1, PY0, PY1 = 130, 690, 100, 420
    VMIN, VMAX = 4.0, 13.0
    PMAX = 0.65

    def x(v):
        return PX0 + (v - VMIN) * (PX1 - PX0) / (VMAX - VMIN)

    def y(w):
        return PY1 - w * (PY1 - PY0) / PMAX

    def fall(v):
        return M_A / (v * v)

    def rise(v):
        return M_B * v

    # сітка й осі
    for w in (0.0, 0.2, 0.4, 0.6):
        p.append(line(PX0, y(w), PX1, y(w), color="#dcdcdc", sw=1.0))
        p.append(text(PX0 - 14, y(w) + 4, "%.1f" % w, size=11, color=MUTED, anchor="end"))
    p.append(line(PX0, PY0 - 8, PX0, PY1, color=INK, sw=1.8))
    p.append(line(PX0, PY1, PX1 + 8, PY1, color=INK, sw=1.8))
    for v in range(4, 14):
        p.append(text(x(v), PY1 + 21, "%d" % v, size=11, color=MUTED))
    p.append(text(66, 246, "втрати,", size=12, color=MUTED, bold=True))
    p.append(text(66, 264, "Вт", size=12, color=MUTED, bold=True))
    p.append(text((PX0 + PX1) / 2, PY1 + 50, "VBUS, яку блок подає на вхід перетворювача, В",
                  size=12, color=INK, bold=True))

    # три криві
    vs = [4.0 + 0.1 * i for i in range(91)]
    for fn, col, sw_ in ((fall, NEG, 2.2), (rise, POS, 2.2),
                         (lambda v: fall(v) + rise(v), INK, 3.0)):
        pts = " ".join("%.1f,%.1f" % (x(v), y(fn(v))) for v in vs)
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                 % (pts, col, sw_))

    # вертикаль V* і три крапки на ній
    XO = x(M_VOPT)
    p.append(line(XO, y(fall(M_VOPT) + rise(M_VOPT)), XO, PY1, color=FIELD, sw=1.5, dash="5 4"))
    for val in (fall(M_VOPT), rise(M_VOPT), fall(M_VOPT) + rise(M_VOPT)):
        p.append(circle(XO, y(val), 5.5, fill="#eafaf0", stroke=FIELD, sw=2.4))
    p.append(text(XO, y(fall(M_VOPT) + rise(M_VOPT)) - 18, "V* ≈ 6.4 В",
                  size=13, color=FIELD, bold=True))

    # права колонка — числа з мінімуму
    b, _, _ = textbox(790, 322,
                      ["на дні ямки:", "", "A/V*² = 0.14 Вт", "B·V*  = 0.29 Вт", "",
                       "рівно ВДВІЧІ більше,", "а не порівну"],
                      size=11, fill="#eafaf0", stroke=FIELD, sw=1.4, pad=11, color=INK)
    p.append(b)

    _legend(p, 505, [(206, "A/V² — Джоуль на всьому, що перед ключем", NEG, "#eef4ff"),
                     (560, "B·V — переліт ключа", POS, "#fdecea"),
                     (752, "сума", INK, FILL)])
    b2, _, _ = textbox(W / 2, 558,
                       "Сталі втрати (провідність нижнього ключа, дросель, затвор) у доданки не входять: вони задають ГЛИБИНУ ямки, а не місце її дна.",
                       size=11, fill=FILL, stroke=LINE, sw=1.3, pad=9)
    p.append(b2)

    render(os.path.join(OUT, "loss-split.svg"), W, H, *p,
           title="Два доданки й мінімум суми: Vb = 3.8 В, Io = 3 А, Rs = 45 мОм, κ = 3%")


# ── cost-of-miss: універсальна ямка ───────────────────────────────────────────
# Ідея: після нормування на V* ямка та сама ЗАВЖДИ — P/P* = 1/(3u²) + 2u/3, без
# жодного параметра. Біля дна ΔP/P* = x², тож дно пласке; і ямка перекошена —
# промахнутись угору дешевше, ніж униз.

def fig_cost_of_miss():
    W, H = 880, 560
    p = []
    PX0, PX1, PY0, PY1 = 130, 700, 110, 400
    UMIN, UMAX = 0.6, 2.0
    RMIN, RMAX = 0.98, 1.50

    def x(u):
        return PX0 + (u - UMIN) * (PX1 - PX0) / (UMAX - UMIN)

    def y(r):
        return PY1 - (r - RMIN) * (PY1 - PY0) / (RMAX - RMIN)

    def rel(u):
        return 1.0 / (3 * u * u) + 2 * u / 3

    # смуга «дешево» — не більше +5% втрат
    p.append(rect(x(0.81), y(1.05), x(1.26) - x(0.81), PY1 - y(1.05),
                  fill="#eafaf0", stroke=FIELD, sw=1.3, rx=4))

    for r in (1.0, 1.1, 1.2, 1.3, 1.4, 1.5):
        p.append(line(PX0, y(r), PX1, y(r), color="#dcdcdc", sw=1.0))
        p.append(text(PX0 - 14, y(r) + 4, "%+d%%" % round((r - 1) * 100), size=11,
                      color=MUTED, anchor="end"))
    p.append(line(PX0, PY0 - 8, PX0, PY1, color=INK, sw=1.8))
    p.append(line(PX0, PY1, PX1 + 8, PY1, color=INK, sw=1.8))
    for u in (0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0):
        p.append(text(x(u), PY1 + 21, "%.1f" % u, size=11, color=MUTED))
    p.append(text(60, 240, "наскільки", size=11, color=MUTED, bold=True))
    p.append(text(60, 256, "більше", size=11, color=MUTED, bold=True))
    p.append(text(60, 272, "втрат", size=11, color=MUTED, bold=True))
    p.append(text((PX0 + PX1) / 2, PY1 + 50, "u = V / V*  —  у скільки разів напруга розминулася з оптимумом",
                  size=12, color=INK, bold=True))

    us = [UMIN + 0.01 * i for i in range(141)]
    pts = " ".join("%.1f,%.1f" % (x(u), y(rel(u))) for u in us)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (pts, INK))
    p.append(circle(x(1.0), y(1.0), 5.5, fill="#eafaf0", stroke=FIELD, sw=2.4))

    # Де на цій ямці сидить сітка QC2.0 (V* = 6.38 В). Підписи виносимо вгору, у
    # порожню смугу над кривою, а поводки обриваємо з запасом і від напису, і від
    # кружка — щоб жодна лінія не заходила в рамку тексту.
    marks = [  # V,  підпис, x напису, кінець поводка
        (5.0, "5 В", 205, (204, 344)),
        (9.0, "9 В", 460, (459, 320)),
        (12.0, "12 В", 620, (648, 186)),
    ]
    for v, lab, lx, (ex, ey) in marks:
        u = v / M_VOPT
        p.append(line(lx, 150, ex, ey, color=POS, sw=1.1, dash="3 3"))
        p.append(circle(x(u), y(rel(u)), 6, fill="#fdecea", stroke=POS, sw=2.2))
        p.append(text(lx, 140, "%s  %+.1f%%" % (lab, (rel(u) - 1) * 100),
                      size=12, color=POS, bold=True))

    _legend(p, 470, [(258, "смуга «дешево»: −19% … +26% від V* — не більше +5% втрат", FIELD, "#eafaf0"),
                     (668, "сітка QC2.0 — уся повз неї", POS, "#fdecea")])
    b, _, _ = textbox(W / 2, 526,
                      ["Крива не має ЖОДНОГО параметра: A, B, Vb, Io, Rs, κ скоротились при нормуванні.",
                       "Біля дна ΔP/P* = x² — тому дно пласке, а хиба вниз коштує дорожче за хибу вгору."],
                      size=11, fill=FILL, stroke=LINE, sw=1.3, pad=9)
    p.append(b)

    render(os.path.join(OUT, "cost-of-miss.svg"), W, H, *p,
           title="Ціна промаху: та сама ямка для будь-якого понижувача за опором")


# ── opt-tracking: як оптимум їде через увесь заряд ────────────────────────────
# Ідея: V* ∝ Vb^(2/3)·Io^(1/3), тож у фазі CC він повзе вгору за коміркою, а у
# фазі CV обвалюється за струмом і сідає на підлогу — тобто назад у 5 В.

def fig_opt_tracking():
    W, H = 880, 580
    p = []
    PX0, PX1, PY0, PY1 = 130, 700, 100, 420
    VLO, VHI = 3.0, 12.5
    TCC = 60.0

    def x(t):
        return PX0 + t * (PX1 - PX0) / 100.0

    def y(v):
        return PY1 - (v - VLO) * (PY1 - PY0) / (VHI - VLO)

    def vbat(t):
        return 3.4 + 1.0 * t / TCC if t <= TCC else 4.4

    def ichg(t):
        import math
        return 3.0 if t <= TCC else 3.0 * math.exp(-(t - TCC) / 15.0)

    def vopt(t):
        return (4.0 * vbat(t) ** 2 * ichg(t) * M_RS / M_KAPPA) ** (1.0 / 3.0)

    def vfloor(t):
        vb, io = vbat(t), ichg(t)
        iin = io * vb / max(vopt(t), vb + M_VHEAD)
        return vb + iin * M_RS + M_VHEAD

    ts = [0.5 * i for i in range(201)]

    for v in (4, 5, 6, 7, 8, 9, 10, 11, 12):
        p.append(line(PX0, y(v), PX1, y(v), color="#ebebeb", sw=1.0))
        p.append(text(PX0 - 14, y(v) + 4, "%d" % v, size=11, color=MUTED, anchor="end"))
    p.append(line(PX0, PY0 - 8, PX0, PY1, color=INK, sw=1.8))
    p.append(line(PX0, PY1, PX1 + 8, PY1, color=INK, sw=1.8))
    p.append(text(64, 244, "напруга,", size=12, color=MUTED, bold=True))
    p.append(text(64, 262, "В", size=12, color=MUTED, bold=True))
    p.append(text((PX0 + PX1) / 2, PY1 + 50, "хід заряду, % часу", size=12, color=INK, bold=True))

    # Коридор, яким їде оптимум за фазу CC — головний доказ фігури: смуга
    # заштрихована, а найближчі щаблі сітки лежать ПОЗА нею з обох боків.
    # Малюємо ПЕРЕД кривими, інакше заливка їх накриє.
    p.append(rect(x(0), y(7.04), x(TCC) - x(0), y(5.93) - y(7.04),
                  fill="#eafaf0", stroke=FIELD, sw=1.3, rx=4))

    # щаблі QC2.0 — суцільні червоні, підписані на правому полі
    for v in (5, 9, 12):
        p.append(line(PX0, y(v), PX1 + 4, y(v), color=POS, sw=1.6, dash="7 5"))
        p.append(text(PX1 + 14, y(v) + 4, "%d В" % v, size=12, color=POS,
                      anchor="start", bold=True))

    # межа фаз
    p.append(line(x(TCC), PY0 - 4, x(TCC), PY1, color=MUTED, sw=1.4, dash="4 4"))
    p.append(text(x(TCC / 2), 150, "CC — струм тримають, комірка повзе вгору",
                  size=12, color=MUTED, bold=True))
    p.append(text(x(80), 150, "CV — струм спадає", size=12, color=MUTED, bold=True))

    # чого хоче модель без обмежень (сіре пунктиром) і що беруть насправді
    raw = " ".join("%.1f,%.1f" % (x(t), y(vopt(t))) for t in ts if vopt(t) >= VLO)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" '
             'stroke-dasharray="5 4"/>' % (raw, MUTED))
    flo = " ".join("%.1f,%.1f" % (x(t), y(vfloor(t))) for t in ts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" '
             'stroke-dasharray="6 4"/>' % (flo, FIELD))
    tgt = " ".join("%.1f,%.1f" % (x(t), y(max(vopt(t), vfloor(t)))) for t in ts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (tgt, INK))
    vb_ = " ".join("%.1f,%.1f" % (x(t), y(vbat(t))) for t in ts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (vb_, NEG))

    # Підпис коридору — у вільну смугу МІЖ ним і щаблем 9 В, не на криву.
    p.append(text(x(30), 250, "коридор, яким їде оптимум за фазу CC: 5.9 → 7.0 В",
                  size=12, color=FIELD, bold=True))
    p.append(text(x(30), 268, "у сітці 5/9/12 тут нема жодного щабля",
                  size=12, color=FIELD, bold=True))

    _legend(p, 492, [(128, "V* — куди тягне модель", MUTED, "#f2f2f2"),
                     (318, "ціль: що беруть насправді", INK, FILL),
                     (537, "підлога: VBAT + падіння + запас", FIELD, "#eafaf0"),
                     (737, "VBAT — комірка", NEG, "#eef4ff")])
    b, _, _ = textbox(W / 2, 542,
                      "Наприкінці заряду струм спадає, оптимум провалюється під підлогу — і правильна відповідь знову 5 В. Той самий щабель, з якого все почалось.",
                      size=11, fill=FILL, stroke=LINE, sw=1.3, pad=9)
    p.append(b)

    render(os.path.join(OUT, "opt-tracking.svg"), W, H, *p,
           title="Оптимум не стоїть на місці: куди він їде за повний заряд")


# ── qc-fsm: автомат споживача (вставка proj-qc-sink) ──────────────────────────
# Ідея: перша половина рукостискання живе В КРЕМНІЇ (їй потрібен компаратор на
# D−, якого хост не має), хост підхоплює з вердикту VBUS_STAT. Гілка «тупий DCP»
# — не помилка, а штатний вихід.

def fig_qc_fsm():
    W, H = 980, 800
    p = []
    CX = 500
    SIL = "#f0e9f8"

    def node(cx, cy, w, h, title, body, col, fill):
        out = rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=col, sw=1.6, rx=8)
        out += text(cx, cy - h / 2 + 21, title, size=13, color=col, bold=True)
        for i, ln in enumerate(body):
            out += text(cx, cy - h / 2 + 42 + i * 17, ln, size=11, color=INK)
        return out

    p.append(node(CX, 78, 280, 58, "IDLE", ["VBUS нема, драйвери в HiZ"], MUTED, FILL))
    p.append(node(CX, 190, 360, 100, "DETECT — робить сам чип", [
        "BC1.2: то хто там узагалі",
        "D+ = 0.6 В, утримання 1.25 с",
        "D− впала? отже, блок уміє QC"], QC, SIL))
    p.append(node(CX, 305, 360, 58, "CLASSIFY — читаємо VBUS_STAT", ["вердикт кремнію, а не здогад"], QC, FILL))
    p.append(node(CX, 410, 280, 76, "CODE — просимо 9 В", [
        "D+ = 3.3 / D− = 0.6", "чекаємо 80 мс + 200 мс"], QC, FILL))
    p.append(node(CX, 510, 300, 58, "АЦП: VBUS справді ≈ 9 В?", ["єдина відповідь, яку дає світ"], NEG, "#eef4ff"))
    p.append(node(CX, 605, 300, 58, "CONT — безперервний режим", ["D+ = 0.6 / D− = 3.3, тримати 80 мс"], QC, FILL))
    p.append(node(CX, 700, 300, 76, "TUNE — крок 200 мВ", [
        "імпульс ≥ 300 мкс, лік свій", "аудит АЦП раз на секунду"], FIELD, "#eafaf0"))
    p.append(node(165, 480, 230, 90, "LEGACY_5V", [
        "звичайний DCP:", "лишаємось на 5 В —", "і це правильно"], POS, "#fdecea"))
    p.append(node(855, 700, 200, 58, "RESYNC", ["код 5 В, лік := 5000"], POS, "#fdecea"))

    p.append(arrow(CX, 107, CX, 138))
    p.append(text(CX + 10, 127, "VBUS_GD = 1", size=10, color=MUTED, anchor="start"))
    p.append(arrow(CX, 240, CX, 274))
    p.append(text(CX + 10, 261, "PG_STAT = 1 (прийшов INT)", size=10, color=MUTED, anchor="start"))
    p.append(arrow(CX, 334, CX, 370))
    p.append(text(CX + 10, 356, "VBUS_STAT = 100 (HVDCP)", size=10, color=MUTED, anchor="start"))
    p.append(line(CX - 180, 305, 165, 305, color=POS, sw=1.5))
    p.append(arrow(165, 305, 165, 433, color=POS))
    p.append(text(252, 296, "VBUS_STAT = 011 (DCP)", size=10, color=POS))
    p.append(arrow(CX, 448, CX, 479))
    p.append(arrow(CX, 539, CX, 574))
    p.append(text(CX + 10, 560, "так", size=10, color=FIELD, anchor="start"))
    p.append(arrow(CX - 150, 510, 282, 510, color=POS))
    p.append(text(330, 500, "ні", size=10, color=POS))
    p.append(arrow(CX, 634, CX, 660))
    p.append(arrow(650, 715, 753, 715, color=POS))
    p.append(text(701, 707, "лік ≠ виміру", size=10, color=POS))
    p.append(line(855, 671, 855, 605, color=POS, sw=1.5))
    p.append(arrow(855, 605, 654, 605, color=POS))
    p.append(text(754, 596, "скидаємось у 5 В і лічимо наново", size=10, color=POS))

    b, bw, bh = textbox(W / 2, 772, [
        "У КОЖНОМУ стані фоном: WD_RST раз на 20 с.",
        "Проспали сторожа 40 с — DP_DAC/DM_DAC самі стають HiZ, блок губить код і падає на 5 В."],
        size=11, fill="#fff8e6", stroke="#b8860b", sw=1.3, pad=10)
    p.append(b)

    render(os.path.join(OUT, "qc-fsm.svg"), W, H, *p,
           title="Автомат споживача: де кремній, де хост і куди веде «тупий DCP»")


# ── qc-timescales: витримки протоколу проти витримок прошивки ─────────────────
# Головна думка вставки: вікна протоколу й реальні часи I²C/АЦП/сторожа лежать
# на ОДНІЙ осі — і стикаються. Транзакція шини потрапляє просто у вікно кроку.

def fig_qc_timescales():
    import math
    W, H = 900, 450
    AX0, AX1, YA = 90, 840, 250
    p = []

    def X(t_us):
        return AX0 + (AX1 - AX0) * (math.log10(t_us) - 1.0) / 7.0

    p.append(rect(X(200), 175, X(20000) - X(200), 130, fill="#eafaf0", stroke="none", sw=0, rx=0))
    p.append(text((X(200) + X(20000)) / 2, 214, "безпечне вікно кроку", size=10, color=FIELD, bold=True))

    # шкалу підписуємо НАД віссю: увесь простір під нею лишаємо виноскам прошивки
    p.append(line(AX0, YA, AX1, YA, color=INK, sw=1.8))
    for t, lab in [(1e1, "10 мкс"), (1e2, "100 мкс"), (1e3, "1 мс"), (1e4, "10 мс"),
                   (1e5, "100 мс"), (1e6, "1 с"), (1e7, "10 с"), (1e8, "100 с")]:
        p.append(line(X(t), YA - 6, X(t), YA, color=INK, sw=1.4))
        p.append(text(X(t), YA - 11, lab, size=10, color=MUTED))

    p.append(text(AX0 - 8, 197, "протокол", size=11, color=QC, bold=True, anchor="end"))
    p.append(text(AX0 - 8, 300, "прошивка", size=11, color=NEG, bold=True, anchor="end"))

    for t0, t1 in [(100, 200), (20000, 60000), (1e6, 1.5e6)]:
        p.append(rect(X(t0), 185, max(X(t1) - X(t0), 3), 16, fill="#e6d9f5", stroke=QC, sw=1.2, rx=3))
    p.append(line(X(2e5), 185, X(2e5), 201, color=QC, sw=2.5))

    for cx, ly, lines in [(X(150), 140, ["імпульс кроку", "100–200 мкс"]),
                          (X(35000), 140, ["фільтр коду", "20–60 мс"]),
                          (X(2e5), 100, ["нова напруга", "за 200 мс"]),
                          (X(1.22e6), 140, ["утримання D+", "1–1.5 с"])]:
        p.append(line(cx, 183, cx, ly + 22, color=MUTED, sw=1.0, dash="3,3"))
        p.append(mtext(cx, ly, lines, size=11, color=QC, bold=True))

    for x, ly, col, lines in [(X(70), 330, POS, ["запис I²C", "400 кГц: ≈ 70 мкс"]),
                              (X(280), 385, FIELD, ["запис I²C", "100 кГц: ≈ 280 мкс"]),
                              (X(1e6), 330, NEG, ["АЦП, одноразове:", "результат — до 1 с"]),
                              (X(4e7), 330, NEG, ["сторож I²C:", "40 с"])]:
        p.append(circle(x, YA, 4.5, fill=col, stroke=col, sw=1))
        p.append(line(x, YA + 5, x, ly - 14, color=col, sw=1.0, dash="3,3"))
        p.append(mtext(x, ly, lines, size=11, color=col, bold=True))

    b, bw, bh = textbox(W / 2, 420, [
        "Вікно імпульсу — 0.2…20 мс, аж два порядки. Але транзакція I²C на 400 кГц у нього НЕ дотягує (70 мкс),",
        "а на 100 кГц (280 мкс) вона вже сама по собі крок. Ширину імпульсу задає таймер, а не швидкість шини."],
        size=11, fill="#eef4ff", stroke=NEG, sw=1.3, pad=10)
    p.append(b)

    render(os.path.join(OUT, "qc-timescales.svg"), W, H, *p,
           title="Одна вісь часу на двох: вікна протоколу й реальні часи прошивки")


# ── reg01-map: у регістрі рівнів живуть двоє чужих ────────────────────────────
# Пастка read-modify-write: REG01 — не «два поля по три біти», і сліпий запис
# байта тихо переставляє зсув VINDPM.

def fig_reg01_map():
    W, H = 820, 330
    p = []
    X0, CW = 120, 70
    cells = [("DP_DAC[2]", "0", QC), ("DP_DAC[1]", "0", QC), ("DP_DAC[0]", "0", QC),
             ("DM_DAC[2]", "0", QC), ("DM_DAC[1]", "0", QC), ("DM_DAC[0]", "0", QC),
             ("EN_12V", "0", POS), ("VINDPM_OS", "1", POS)]
    for i, (name, rst, col) in enumerate(cells):
        x = X0 + i * CW
        fill = "#f0e9f8" if col == QC else "#fdecea"
        p.append(text(x + CW / 2, 95, str(7 - i), size=11, color=MUTED, bold=True))
        p.append(rect(x, 105, CW, 60, fill=fill, stroke=col, sw=1.5, rx=5))
        p.append(text(x + CW / 2, 128, name, size=10, color=col, bold=True))
        p.append(text(x + CW / 2, 152, rst, size=13, color=INK, bold=True))

    for x0, x1, lab, col in [(X0, X0 + 3 * CW, "DP_DAC[7:5] — рівень на D+", QC),
                             (X0 + 3 * CW, X0 + 6 * CW, "DM_DAC[4:2] — рівень на D−", QC),
                             (X0 + 6 * CW, X0 + 8 * CW, "чужі біти — не чіпати", POS)]:
        p.append(line(x0 + 4, 178, x1 - 4, 178, color=col, sw=1.6))
        p.append(text((x0 + x1) / 2, 198, lab, size=11, color=col, bold=True))

    b, bw, bh = textbox(410, 262, [
        "Скидання REG01 = 0x01 → VINDPM_OS = 1, тобто зсув VINDPM 600 мВ.",
        "Записали байт «цілком» — і зсув тихо став 400 мВ, а дозвіл на 12 В зник.",
        "Лікування: тінь регістра. Прочитати REG01 ОДИН раз, далі міняти лише біти [7:2].",
        "Та сама тінь рятує й таймінг: крок — ОДИН запис, без читання перед ним."],
        size=11, fill="#fff8e6", stroke="#b8860b", sw=1.3, pad=10)
    p.append(b)

    render(os.path.join(OUT, "reg01-map.svg"), W, H, *p,
           title="REG01 bq25890H: рядок «нижні два біти» коштує дорого")


# ── lineage-channels: розвилка 2014-го — три команди, три РІЗНІ дроти ─────────
# Ідея (hist-qc-lineage): форму протоколу вибрав не інженер, а обмеження. Кожен
# вичавив максимум із того дроту, який йому дозволили чіпати.

def fig_lineage_channels():
    W, H = 1030, 530
    p = []
    PW = 310
    cols = [
        (25, "Qualcomm · QC 2.0", "рівні на D+/D−", QC, "#f2ecf8",
         ["у виділеного блока лінії даних",
          "усе одно замкнені перемичкою —",
          "отже, вільні. Блок читає на них",
          "0.6 і 3.3 В двома порогами"],
         "жодного нового дроту:\nбудь-який наявний шнур і блок",
         "три стани на лінію, п'ять кодів;\nбезпеку нема чим купити,\nокрім часу — витримка 1.25 с"),
        (360, "MediaTek · Pump Express+", "імпульси струму на VBUS", NEG, "#eef4ff",
         ["ліній даних не чіпають узагалі.",
          "Лінію живлення веде блок — тож",
          "телефон модулює те, чим керує:",
          "власне споживання, а блок лічить"],
         "канал там, де дроту для нього нема:\nповідомлення несе навантаження",
         "рукостискання нема взагалі;\nкрок аж 0.5 В (PE+ 2.0)"),
        (695, "OPPO · VOOC", "власні контакти в роз'ємі", POS, "#fdecea",
         ["наявним каналом не користуються:",
          "свій кабель, свої жили, свій MCU",
          "у блоці. Не треба вигадувати мову",
          "для двох дротів — додай дротів"],
         "повна свобода: 5 В × 4.5 А ≈ 20 Вт,\nа перетворювач аж у розетці",
         "власний кабель і власний блок;\nбез них — ті самі 5 В / 2 А"),
    ]
    for x0, team, chan, col, fill, desc, gain, cost in cols:
        cx = x0 + PW / 2
        p.append(rect(x0, 46, PW, 400, fill="#ffffff", stroke=col, sw=1.6, rx=10))
        p.append(text(cx, 70, team, size=14, color=col, bold=True))
        b, _, _ = textbox(cx, 104, chan, size=12.5, bold=True, color=col,
                          fill=fill, stroke=col, sw=1.4, pad=8, min_w=PW - 26)
        p.append(b)
        for i, d in enumerate(desc):
            p.append(text(cx, 148 + i * 21, d, size=11.5, color=INK))
        p.append(text(cx, 250, "ЗДОБУЛИ", size=10.5, color=FIELD, bold=True))
        b2, _, _ = textbox(cx, 290, gain, size=10.5, fill="#eafaf0", stroke=FIELD,
                           sw=1.2, pad=9, color=INK, min_w=PW - 26)
        p.append(b2)
        p.append(text(cx, 348, "ЗАПЛАТИЛИ", size=10.5, color=POS, bold=True))
        b3, _, _ = textbox(cx, 398, cost, size=10.5, fill="#fdecea", stroke=POS,
                           sw=1.2, pad=9, color=INK, min_w=PW - 26)
        p.append(b3)

    b, bw, bh = textbox(W / 2, 490,
                        "одне питання — «як безмозкий блок дізнається, чого хоче телефон?» — і три різні дроти, якими на нього відповіли",
                        size=11, fill=FILL, stroke=LINE, sw=1.3, pad=9)
    p.append(b)

    render(os.path.join(OUT, "lineage-channels.svg"), W, H, *p,
           title="Розвилка 2014-го: канал вибирає протокол")


# ── lineage-converter: де жив перетворювач — і чим скінчилась суперечка ───────
# Ідея: сперечались не про напругу, а про МІСЦЕ перетворення. Синтез — не
# компроміс, а відкриття, що два табори зменшували різні доданки однієї суми.

def fig_lineage_converter():
    W, H = 1060, 470
    p = []
    rows = [
        (140, "VOOC · 2014", POS, "#fdecea",
         "блок VOOC\nMCU + контур", "5 В · 4.5 А",
         "просто ключ\nперетворювача нема", "#eafaf0", FIELD,
         "1S\n4.2 В",
         "тепло перепаду лишається в розетці.\nЦіна: власний кабель і власний блок."),
        (270, "Quick Charge 2.0 / 3.0", QC, "#f2ecf8",
         "блок HVDCP\n5 / 9 / 12 В", "9 В · 2 А",
         "buck-перетворювач\nККД падає з перепадом", "#fdecea", POS,
         "1S\n4.2 В",
         "струм у шнурі малий — зате тепло\nв кишені, просто біля комірки."),
        (400, "Синтез · QC 5 · 2020", FIELD, "#eafaf0",
         "PPS-блок\n17.6 В на запит", "17.6 В · 5.6 А",
         "насос ÷2\nККД > 98%", "#eafaf0", FIELD,
         "2S\n8.8 В",
         "і малий струм у шнурі, І майже нема\nтепла в телефоні. Обидві правди."),
    ]
    for y, era, ecol, efill, adap, cable, phone, pfill, pcol, cell, note in rows:
        p.append(text(40, y - 52, era, size=13, color=ecol, bold=True, anchor="start"))
        b, _, _ = textbox(95, y, adap, size=11, fill=efill, stroke=ecol, sw=1.4,
                          pad=8, color=INK, min_w=130)
        p.append(b)
        p.append(arrow(165, y, 295, y, color=ecol, sw=1.8))
        p.append(text(230, y - 14, cable, size=11, color=ecol, bold=True))
        b2, _, _ = textbox(390, y, phone, size=11, fill=pfill, stroke=pcol, sw=1.8,
                           pad=8, color=INK, min_w=180)
        p.append(b2)
        p.append(arrow(485, y, 555, y, color=ecol, sw=1.8))
        b3, _, _ = textbox(615, y, cell, size=11, fill=FILL, stroke=LINE, sw=1.4,
                           pad=8, color=INK, min_w=110)
        p.append(b3)
        b4, _, _ = textbox(860, y, note, size=10.5, fill="#ffffff", stroke=MUTED,
                           sw=1.1, pad=9, color=INK, min_w=330)
        p.append(b4)

    p.append(text(230, 70, "що йде в ШНУРІ", size=11.5, color=MUTED, bold=True))
    p.append(text(390, 70, "що стоїть у ТЕЛЕФОНІ", size=11.5, color=MUTED, bold=True))

    render(os.path.join(OUT, "lineage-converter.svg"), W, H, *p,
           title="Сперечались не про напругу, а про місце перетворення")


# ── lineage-timeline: три доріжки, що сходяться в одну ────────────────────────
# Ідея: показати САМЕ збіг ліній. Дати звірені — див. прозу вставки.

def fig_lineage_timeline():
    W, H = 1160, 560
    p = []
    X0, X1 = 170.0, 1080.0
    T0, T1 = 2013.0, 2021.0

    def x(t):
        return X0 + (t - T0) * (X1 - X0) / (T1 - T0)

    def bw(lab, size=10, pad=8):
        return max(text_width(ln, size, False) for ln in lab.split("\n")) + 2 * pad

    bx = x(2017.8)
    p.append(rect(bx, 64, 1090 - bx, 440, fill="#f0fdf4",
                  stroke="#d3f0dd", sw=1.0, rx=8))
    p.append(text((bx + 1090) / 2, 54, "від 2018-го — синтез", size=11.5,
                  color=FIELD, bold=True))

    # роки — КОРОТКІ засічки під доріжками: жодна лінія не ріже напису
    for yr in range(2013, 2022):
        p.append(line(x(yr), 512, x(yr), 520, color=MUTED, sw=1.2))
        p.append(text(x(yr), 538, str(yr), size=11, color=MUTED))

    lanes = [
        (130, "Qualcomm", QC, "#f2ecf8", [
            (2013.0, "QC 1.0 · 2013\n5 В / 2 А"),
            (2014.0, "QC 2.0 · 2014\n9 / 12 В"),
            (2015.7, "QC 3.0 · 2015\nкрок 200 мВ"),
            (2016.88, "QC 4 · 2016\nUSB PD"),
            (2020.57, "QC 5 · 2020\nPD PPS + 2S"),
        ]),
        (250, "MediaTek", NEG, "#eef4ff", [
            (2014.0, "PE+ · 2014\nімпульси струму"),
            (2016.41, "PE 3.0 · 2016\nPD + direct"),
        ]),
        (350, "OPPO", POS, "#fdecea", [
            (2014.2, "VOOC · 2014\n5 В / 4.5 А"),
            (2018.5, "SuperVOOC · 2018\n10 В · 2S · насос"),
        ]),
        (470, "USB-IF", FIELD, "#eafaf0", [
            (2014.6, "Type-C · 2014\n5 В — і крапка"),
            (2017.03, "PPS · 2017\nкрок 20 мВ"),
        ]),
    ]
    for ly, name, col, fill, evs in lanes:
        # рейка — лише в проміжках між «станціями», щоб не різати їхніх написів
        cur = 110.0
        for a, b2 in sorted((x(t) - bw(lab) / 2 - 8, x(t) + bw(lab) / 2 + 8)
                            for t, lab in evs):
            if a > cur:
                p.append(line(cur, ly, a, ly, color="#dcdcdc", sw=1.5))
            cur = max(cur, b2)
        if cur < 1100:
            p.append(line(cur, ly, 1100, ly, color="#dcdcdc", sw=1.5))
        p.append(text(88, ly + 5, name, size=13, color=col, bold=True, anchor="end"))
        for t, lab in evs:
            b, _, _ = textbox(x(t), ly, lab, size=10, fill=fill, stroke=col,
                              sw=1.5, pad=8, color=INK)
            p.append(b)

    render(os.path.join(OUT, "lineage-timeline.svg"), W, H, *p,
           title="Родовід: 2013–2020")


if __name__ == "__main__":
    fig_why_volts()
    fig_three_states()
    fig_hvdcp_handshake()
    fig_code_grid()
    fig_inov_efficiency()
    fig_loss_split()
    fig_cost_of_miss()
    fig_opt_tracking()
    fig_qc_fsm()
    fig_qc_timescales()
    fig_reg01_map()
    fig_lineage_channels()
    fig_lineage_converter()
    fig_lineage_timeline()
    print("OK: figures written to", OUT)
