# -*- coding: utf-8 -*-
"""Фігури до теми «Принцип еквівалентності».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

PUSH = "#c0392b"   # штовхання / прискорення — гаряче
GRAV = "#2457d6"   # тяжіння / вага — холодне


def block(cx, cy, s=52, label=None, lcolor=INK):
    """Квадратний тягарець."""
    out = rect(cx - s / 2, cy - s / 2, s, s, fill="#e8edf3", stroke=LINE, sw=1.7, rx=6)
    if label:
        out += text(cx, cy + 6, label, size=16, bold=True, color=lcolor)
    return out


def ball(cx, cy, r=12):
    return circle(cx, cy, r, fill="#fef6e7", stroke=PUSH, sw=2)


def hatched_ground(x1, x2, y, n=9):
    """Горизонтальна опора з косими рисками під нею."""
    out = line(x1, y, x2, y, color=LINE, sw=2)
    step = (x2 - x1) / n
    for i in range(n):
        gx = x1 + i * step
        out += line(gx, y, gx - 8, y + 9, color=MUTED, sw=1.2)
    return out


# ── Фігура 1: дві ролі маси — і як вони скорочуються у падінні ───────────────
def fig_two_masses():
    W, H = 820, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Дві маси, дві ролі — а у вільному падінні вони скорочуються",
                  size=16, bold=True))
    f.append(line(W / 2, 56, W / 2, 250, color="#dfe4ea", sw=1.2, dash="4,6"))

    # ── ліворуч: інертна маса — опір штовханню ──
    cxL = 205
    f.append(text(cxL, 78, "Інертна маса  mᵢ", size=15, bold=True, color=PUSH))
    f.append(hatched_ground(cxL - 95, cxL + 70, 172))
    f.append(block(cxL, 145))
    # сила штовхає зліва
    f.append(arrow(cxL - 92, 145, cxL - 30, 145, color=PUSH, sw=3.2))
    f.append(text(cxL - 75, 132, "F", size=15, bold=True, color=PUSH))
    # прискорення праворуч
    f.append(arrow(cxL + 30, 145, cxL + 78, 145, color=INK, sw=2.4))
    f.append(text(cxL + 70, 132, "a", size=14, bold=True, color=INK))
    f.append(text(cxL, 205, "штовхнув силою F  →  a = F / mᵢ", size=12.5, color=INK))
    f.append(text(cxL, 228, "mᵢ — опір зміні руху", size=12, color=MUTED))

    # ── праворуч: гравітаційна маса — «заряд» тяжіння ──
    cxR = 615
    f.append(text(cxR, 78, "Гравітаційна маса  m_g", size=15, bold=True, color=GRAV))
    f.append(block(cxR, 128))
    f.append(arrow(cxR, 156, cxR, 216, color=GRAV, sw=3.2))
    f.append(text(cxR + 46, 192, "F = m_g · g", size=13.5, bold=True, color=GRAV, anchor="start"))
    f.append(text(cxR, 240, "m_g — «заряд» тяжіння, як заряд для електрики", size=12, color=MUTED))

    # ── низ: скорочення ──
    b, bw, bh = textbox(
        W / 2, 328,
        "У вільному падінні:   mᵢ · a = m_g · g   ⟹   a = (m_g / mᵢ) · g\n"
        "Дослід: m_g = mᵢ для всіх тіл   ⟹   a = g  незалежно від маси й речовини",
        size=13, pad=11, fill="#eafaf1", stroke=FIELD, sw=1.6, bold=False)
    f.append(b)
    return render(os.path.join(IMG, "two-masses.svg"), W, H, *f)


# ── Фігура 2: скринька — тяжіння не відрізнити від прискорення ───────────────
def fig_elevator():
    W, H = 900, 450
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Зсередини скриньки тяжіння й прискорення не розрізнити",
                  size=16, bold=True))
    f.append(line(450, 56, 450, 410, color="#dfe4ea", sw=1.3, dash="4,6"))

    def room(cx, top, w=120, h=140):
        return rect(cx - w / 2, top, w, h, fill="#fbfcfe", stroke=LINE, sw=1.8, rx=8)

    rtop = 96
    rbot = rtop + 140            # 236

    # ── панель A: тяжіння = прискорення ──
    f.append(text(240, 74, "Тяжіння  =  прискорення", size=14, bold=True))
    # A1 — на планеті
    f.append(room(130, rtop))
    f.append(hatched_ground(76, 184, rbot - 12, n=6))
    f.append(ball(130, rbot - 26))
    f.append(arrow(52, rtop + 40, 52, rtop + 100, color=GRAV, sw=3))
    f.append(text(41, rtop + 74, "g", size=15, bold=True, color=GRAV, anchor="end"))
    bb, _, _ = textbox(130, 300, "на планеті\n(тяжіння g)", size=11.5, pad=7,
                       fill=FILL, stroke=LINE, sw=1.2)
    f.append(bb)
    # =
    f.append(text(250, 178, "=", size=38, bold=True))
    # A2 — ракета
    f.append(room(370, rtop))
    f.append(hatched_ground(316, 424, rbot - 12, n=6))
    f.append(ball(370, rbot - 26))
    # факел під ракетою
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s" stroke="none"/>'
             % (350, rbot, 390, rbot, 370, rbot + 34, PUSH))
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s" stroke="none"/>'
             % (360, rbot, 380, rbot, 370, rbot + 20, "#f6c445"))
    bb, _, _ = textbox(370, 300, "ракета в порожнечі\n(a = g)", size=11.5, pad=7,
                       fill=FILL, stroke=LINE, sw=1.2)
    f.append(bb)
    b, _, _ = textbox(240, 400, "кулька падає на підлогу однаково", size=12, pad=8,
                      fill="#eafaf1", stroke=FIELD, sw=1.4)
    f.append(b)

    # ── панель B: вільне падіння = спокій ──
    f.append(text(670, 74, "Вільне падіння  =  спокій", size=14, bold=True))
    # B1 — вільне падіння
    f.append(room(560, rtop))
    f.append(ball(560, rtop + 66))
    for dx in (-46, 46):
        f.append(arrow(560 + dx, rtop + 24, 560 + dx, rtop + 92, color=GRAV, sw=2))
    f.append(text(560, rbot + 6, "↓ падає у полі g", size=11.5, color=MUTED))
    bb, _, _ = textbox(560, 300, "вільне падіння\nв полі g", size=11.5, pad=7,
                       fill=FILL, stroke=LINE, sw=1.2)
    f.append(bb)
    # =
    f.append(text(670, 178, "=", size=38, bold=True))
    # B2 — далеко від мас
    f.append(room(780, rtop))
    f.append(ball(780, rtop + 66))
    for sx, sy in ((726, 118), (832, 132), (742, 200), (826, 210), (784, 116)):
        f.append(text(sx, sy, "✦", size=11, color=MUTED))
    bb, _, _ = textbox(780, 300, "спокій далеко\nвід усіх мас", size=11.5, pad=7,
                       fill=FILL, stroke=LINE, sw=1.2)
    f.append(bb)
    b, _, _ = textbox(670, 400, "кулька плаває — невагомість однакова", size=12, pad=8,
                      fill="#eafaf1", stroke=FIELD, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "elevator.svg"), W, H, *f)


# ── Фігура 3: еквівалентність лише локальна — припливні сили ─────────────────
def fig_tidal():
    W, H = 860, 450
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Еквівалентність лише локальна: припливні сили видають справжнє тяжіння",
                  size=15.5, bold=True))
    f.append(line(430, 56, 430, 386, color="#dfe4ea", sw=1.3, dash="4,6"))

    # ── ліворуч: однорідне поле (як у ракеті) ──
    f.append(text(220, 76, "Однорідне поле прискорення", size=14, bold=True, color=INK))
    for gx in (70, 140, 210, 280, 350):
        f.append(arrow(gx, 96, gx, 156, color=GRAV, sw=2.2))
    # дві кульки на одній висоті
    yB = 250
    f.append(ball(150, yB, 13))
    f.append(ball(290, yB, 13))
    f.append(line(163, yB, 277, yB, color=MUTED, sw=1.2, dash="5,5"))
    f.append(text(220, yB - 22, "стала відстань", size=12, color=MUTED))
    # однакові стрілки вниз під кульками
    f.append(arrow(150, yB + 20, 150, yB + 78, color=GRAV, sw=2.4))
    f.append(arrow(290, yB + 20, 290, yB + 78, color=GRAV, sw=2.4))
    b, _, _ = textbox(220, 410, "паралельні однакові стрілки →\nкульки не зближуються",
                      size=12, pad=8, fill="#eafaf1", stroke=FIELD, sw=1.4)
    f.append(b)

    # ── праворуч: справжнє тяжіння планети (сходиться) ──
    f.append(text(645, 76, "Тяжіння планети", size=14, bold=True, color=INK))
    center = (645, 640)             # центр планети — далеко внизу за кадром
    # поверхня планети — пологa дуга внизу
    f.append('<path d="M 470 384 Q 645 344 820 384" fill="#eaf0fb" '
             'stroke="%s" stroke-width="1.6"/>' % GRAV)
    f.append(text(645, 372, "↓ до центра планети", size=11.5, color=GRAV))
    # радіальні стрілки, що сходяться до центра

    def toward_center(px, py, ln):
        dx, dy = center[0] - px, center[1] - py
        d = math.hypot(dx, dy)
        return px + dx / d * ln, py + dy / d * ln

    for px in (500, 575, 645, 715, 790):
        ex, ey = toward_center(px, 200, 60)
        f.append(arrow(px, 200, ex, ey, color=GRAV, sw=2.2))
    # дві кульки на одній висоті — їх зводить припливна сила
    yT = 140
    f.append(ball(560, yT, 13))
    f.append(ball(730, yT, 13))
    f.append(line(573, yT, 717, yT, color=MUTED, sw=1.2, dash="5,5"))
    # короткі стрілки, спрямовані досередини (до центральної лінії)
    ex, ey = toward_center(560, yT + 18, 44)
    f.append(arrow(560, yT + 18, ex, ey, color=PUSH, sw=2.2))
    ex, ey = toward_center(730, yT + 18, 44)
    f.append(arrow(730, yT + 18, ex, ey, color=PUSH, sw=2.2))
    f.append(text(645, yT - 22, "кульки зводяться", size=12, color=PUSH))
    b, _, _ = textbox(645, 410, "стрілки сходяться до центра →\nприпливна сила: її не прибрати прискоренням",
                      size=12, pad=8, fill="#fdecea", stroke=PUSH, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "tidal-local.svg"), W, H, *f)


# ── Фігура 4: шлях точності від Ньютона до супутника (для hist-вставки) ──────
def fig_timeline():
    W, H = 980, 580
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Точність перевірки рівності мас: чотириста років — дюжина порядків",
                  size=16, bold=True))
    f.append(text(W / 2, 56, "нижче = точніше  (шкала логарифмічна: найменша помітна частка відхилення)",
                  size=12, color=MUTED))
    x0, x1 = 150, 870
    ytop, ybot = 120, 452

    def ey(e):
        return ytop + ((-3.0) - e) / 12.0 * (ybot - ytop)

    glabel = {-3: "10⁻³", -6: "10⁻⁶", -9: "10⁻⁹", -12: "10⁻¹²", -15: "10⁻¹⁵"}
    for e in (-3, -6, -9, -12, -15):
        y = ey(e)
        f.append(line(x0 - 18, y, x1 + 34, y, color="#e6e9ee", sw=1.2))
        f.append(text(x0 - 34, y + 4, glabel[e], size=12.5, color=MUTED, anchor="end"))

    pts = [
        ("Ньютон", "1687", -3.0, "10⁻³"),
        ("Бесель", "1832", -4.7, "2·10⁻⁵"),
        ("Етвеш", "1909", -8.3, "5·10⁻⁹"),
        ("Дікке", "1964", -10.5, "3·10⁻¹¹"),
        ("Брагінський", "1972", -12.0, "10⁻¹²"),
        ("Eöt-Wash", "2008", -12.7, "2·10⁻¹³"),
        ("MICROSCOPE", "2022", -15.0, "10⁻¹⁵"),
    ]
    n = len(pts)
    dx = (x1 - x0) / (n - 1)
    xs = [x0 + i * dx for i in range(n)]
    ys = [ey(p[2]) for p in pts]
    for i in range(n - 1):
        f.append(line(xs[i], ys[i], xs[i + 1], ys[i + 1], color=GRAV, sw=2.6))
    for i, (name, year, e, val) in enumerate(pts):
        x, y = xs[i], ys[i]
        f.append(line(x, y + 9, x, 466, color="#dfe4ea", sw=1.1, dash="3,5"))
        f.append(circle(x, y, 7, fill="#fef6e7", stroke=PUSH, sw=2.4))
        f.append(text(x, y - 15, val, size=12.5, bold=True, color=INK))
        f.append(text(x, 483, year, size=12.5, bold=True))
        f.append(text(x, 500, name, size=11.5, color=MUTED))
    b, _, _ = textbox(690, 150,
                      "за ~330 років — на 12 порядків точніше:\n"
                      "від 10⁻³ (тисячна) до 10⁻¹⁵",
                      size=12.5, pad=11, fill="#eafaf1", stroke=FIELD, sw=1.5)
    f.append(b)
    return render(os.path.join(IMG, "timeline.svg"), W, H, *f)


# ── Фігура 5: як улаштовані крутильні терези (для hist-вставки) ──────────────
def fig_torsion():
    W, H = 880, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Крутильні терези: рівність мас стає пошуком закруту нитки",
                  size=15.5, bold=True))
    f.append(line(430, 58, 430, 440, color="#dfe4ea", sw=1.3, dash="4,6"))

    # ── ліва панель: апарат (вид збоку) ──
    f.append(text(215, 82, "Апарат  (вид збоку)", size=13, bold=True, color=MUTED))
    f.append(hatched_ground(150, 290, 108, n=8))          # стеля-опора
    f.append(line(220, 108, 220, 158, color=LINE, sw=1.6))  # нитка
    f.append(text(236, 136, "нитка", size=11.5, color=MUTED, anchor="start"))
    f.append(line(150, 168, 290, 168, color=LINE, sw=2.4))  # коромисло
    f.append(block(150, 168, 34, "Pt", INK))
    f.append(block(290, 168, 34, "Al", INK))
    # сили: тяжіння (вниз, синє) і відцентрова (вбік, червона) на кожній масі
    f.append(arrow(150, 188, 150, 244, color=GRAV, sw=2.6))
    f.append(arrow(290, 188, 290, 244, color=GRAV, sw=2.6))
    f.append(arrow(170, 168, 214, 168, color=PUSH, sw=2.4))
    f.append(arrow(310, 168, 354, 168, color=PUSH, sw=2.4))
    f.append(text(215, 292, "↓  тяжіння  ∝ m_g", size=12.5, bold=True, color=GRAV))
    f.append(text(215, 314, "→  відцентрова (обертання Землі)  ∝ mᵢ",
                  size=12.5, bold=True, color=PUSH))
    b, _, _ = textbox(215, 372,
                      "Дві різні речовини на кінцях.\n"
                      "Тяжіння хапає m_g, відцентрова — mᵢ.",
                      size=12, pad=9, fill=FILL, stroke=LINE, sw=1.2)
    f.append(b)

    # ── права панель: логіка «різниця → закрут → поворот міняє знак» ──
    f.append(text(650, 82, "Що показала б різниця  (вид згори)", size=13, bold=True, color=MUTED))

    def topbeam(cy, left_lbl, right_lbl, cw):
        out = line(560, cy, 740, cy, color=LINE, sw=2.4)
        out += block(560, cy, 28, left_lbl, INK)
        out += block(740, cy, 28, right_lbl, INK)
        # диференційні бічні сили на кінцях — протилежні
        if cw:
            out += arrow(560, cy + 16, 560, cy + 48, color=PUSH, sw=2.2)
            out += arrow(740, cy - 16, 740, cy - 48, color=PUSH, sw=2.2)
            out += ('<path d="M 682 %d A 30 30 0 1 1 650 %d" fill="none" '
                    'stroke="%s" stroke-width="2.3" marker-end="url(#arrow)"/>'
                    % (cy, cy - 30, PUSH))
        else:
            out += arrow(560, cy - 16, 560, cy - 48, color=PUSH, sw=2.2)
            out += arrow(740, cy + 16, 740, cy + 48, color=PUSH, sw=2.2)
            out += ('<path d="M 618 %d A 30 30 0 1 1 650 %d" fill="none" '
                    'stroke="%s" stroke-width="2.3" marker-end="url(#arrow)"/>'
                    % (cy, cy + 30, PUSH))
        return out

    f.append(topbeam(150, "A", "B", True))
    f.append(text(650, 108, "τ", size=15, bold=True, color=PUSH))
    b, _, _ = textbox(650, 214, "різне  m_g/mᵢ  →  момент τ закручує нитку",
                      size=11.5, pad=8, fill="#fdecea", stroke=PUSH, sw=1.3)
    f.append(b)

    f.append(topbeam(300, "B", "A", False))
    f.append(text(650, 344, "τ", size=15, bold=True, color=PUSH))
    b, _, _ = textbox(650, 258, "поворот на 180°  →  τ міняє знак",
                      size=11.5, pad=8, fill=FILL, stroke=LINE, sw=1.2)
    f.append(b)

    b, _, _ = textbox(650, 410,
                      "Однакове відношення мас — нитка стоїть.\n"
                      "Закрут, що обертається зі зміною напрямку,\nвиказав би порушення — його не знайшли.",
                      size=11.5, pad=9, fill="#eafaf1", stroke=FIELD, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "torsion-balance.svg"), W, H, *f)


# ── Фігура 6: звідки горизонтальна «гравітація» — відцентрова на широті φ ─────
#    (для math-вставки: розклад відцентрової сили й величина g_гор)
def fig_eotvos_centrifugal():
    W, H = 780, 452
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Звідки горизонтальна «гравітація»: відцентрова на широті φ",
                  size=15, bold=True))

    C = (240, 268)
    Re = 118
    f.append(circle(C[0], C[1], Re, fill="#eef3fb", stroke=GRAV, sw=1.8))
    f.append(line(240, 150, 240, 392, color=INK, sw=1.5, dash="6,5"))
    f.append(text(240, 142, "вісь ω", size=11.5, color=MUTED))
    f.append(line(122, 268, 358, 268, color=MUTED, sw=1.1, dash="5,5"))
    f.append(text(366, 272, "екв.", size=11, color=MUTED, anchor="start"))

    P = (C[0] + Re * 0.7071, C[1] - Re * 0.7071)     # (323.4, 184.6) — широта 45°
    f.append(line(C[0], C[1], P[0], P[1], color=MUTED, sw=1.0, dash="3,4"))
    f.append(text(256, 224, "φ", size=13, italic=True))
    f.append(circle(P[0], P[1], 4.5, fill=INK, stroke=INK, sw=1))
    # виска (місцева вертикаль) — радіально назовні
    f.append(line(P[0], P[1], P[0] + 0.7071 * 30, P[1] - 0.7071 * 30, color=MUTED, sw=1.0, dash="2,3"))
    f.append(text(P[0] + 14, P[1] - 30, "виска", size=10.5, color=MUTED, anchor="end"))
    # тяжіння до центра (синє)
    f.append(arrow(P[0], P[1], P[0] - 0.7071 * 62, P[1] + 0.7071 * 62, color=GRAV, sw=3))
    # відцентрова (червона діагональ, горизонтально від осі) + розклад-паралелограм
    Q = (P[0] + 72, P[1])
    A = (P[0] + 0.7071 * 50.9, P[1] - 0.7071 * 50.9)   # радіальна складова
    B = (P[0] + 0.7071 * 50.9, P[1] + 0.7071 * 50.9)   # тангенційна (до екватора)
    f.append(line(A[0], A[1], Q[0], Q[1], color=MUTED, sw=1.0, dash="3,3"))
    f.append(line(B[0], B[1], Q[0], Q[1], color=MUTED, sw=1.0, dash="3,3"))
    f.append(arrow(P[0], P[1], Q[0], Q[1], color=PUSH, sw=3))          # повна відцентрова
    f.append(line(P[0], P[1], A[0], A[1], color=PUSH, sw=1.4, dash="4,3"))  # вертикальна складова
    f.append(text(A[0] + 4, A[1] - 4, "верт.", size=10, color=PUSH, anchor="start"))
    f.append(arrow(P[0], P[1], B[0], B[1], color=FIELD, sw=3))         # горизонтальна складова
    f.append(text(B[0] + 6, B[1] + 12, "g_гор", size=12, bold=True, color=FIELD, anchor="start"))

    # ── числа праворуч ──
    f.append(rect(440, 118, 312, 258, fill="#f7f9fb", stroke=LINE, sw=1.3, rx=8))
    tx = 458
    f.append(text(tx, 150, "відцентрова = ω²·R·cosφ", size=12, bold=True, color=PUSH, anchor="start"))
    f.append(text(tx, 178, "верт. = ω²R·cos²φ  (послаблює g)", size=11.5, color=MUTED, anchor="start"))
    f.append(text(tx, 200, "гор. = (ω²R/2)·sin2φ", size=11.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(tx, 236, "макс. на φ = 45°:", size=12, anchor="start"))
    f.append(text(tx, 258, "≈ 1.7·10⁻² м/с² ≈ 0.0017 g", size=12, bold=True, color=FIELD, anchor="start"))
    hb, _, _ = textbox(596, 328,
                       "терези читають різницю η·g_гор,\nа спільну вагу — у натяг нитки",
                       size=11, pad=9, fill="#eef7f0", stroke=FIELD, sw=1.3)
    f.append(hb)
    # легенда синьої стрілки під Землею (щоб не перетинати радіус)
    f.append(line(70, 414, 96, 414, color=GRAV, sw=3))
    f.append(text(102, 418, "тяжіння до центра (за m_g)", size=11.5, color=GRAV, anchor="start"))
    return render(os.path.join(IMG, "eotvos-centrifugal.svg"), W, H, *f)


# ── Фігура 7: припливний градієнт у числах — наскільки локальна еквівалентність ─
def fig_tidal_box():
    W, H = 900, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Наскільки локальна еквівалентність: припливний градієнт у числах",
                  size=15.5, bold=True))

    bx, by, bw, bh = 118, 116, 250, 250
    cx, cy = bx + bw / 2, by + bh / 2
    f.append('<path d="M 58 408 Q 243 370 428 408" fill="#eef3fb" stroke="%s" stroke-width="1.6"/>' % GRAV)
    f.append(text(243, 400, "↓ до центра планети", size=11, color=GRAV))
    f.append(rect(bx, by, bw, bh, fill="none", stroke=INK, sw=1.6, rx=10))
    f.append(text(bx + 2, by - 8, "вільно падна скринька", size=11, color=MUTED, anchor="start"))
    # радіальна пара (верх-низ) — розтягуються
    f.append(ball(cx, by + 34, 12))
    f.append(ball(cx, by + bh - 34, 12))
    f.append(arrow(cx, by + 28, cx, by - 4, color=PUSH, sw=2.6))
    f.append(arrow(cx, by + bh - 28, cx, by + bh + 4, color=PUSH, sw=2.6))
    f.append(text(cx + 18, by + 22, "розтяг", size=11, bold=True, color=PUSH, anchor="start"))
    # поперечна пара (ліво-право) — стискаються
    f.append(ball(bx + 34, cy, 12))
    f.append(ball(bx + bw - 34, cy, 12))
    f.append(arrow(bx + 52, cy, bx + 84, cy, color=GRAV, sw=2.4))
    f.append(arrow(bx + bw - 52, cy, bx + bw - 84, cy, color=GRAV, sw=2.4))
    f.append(text(cx, cy + 42, "стиск", size=11, bold=True, color=GRAV))
    # розмір d
    f.append(line(bx + 16, by + 34, bx + 16, by + bh - 34, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(bx + 10, cy + 4, "d", size=12, italic=True, color=MUTED, anchor="end"))

    # ── числа праворуч ──
    rx0, ry0, rw, rh = 470, 108, 400, 262
    f.append(rect(rx0, ry0, rw, rh, fill="#f7f9fb", stroke=LINE, sw=1.3, rx=8))
    tx = rx0 + 20
    y = ry0 + 34
    f.append(text(tx, y, "K∥ = 2GM/R³ = 2g/R ≈ 3.08·10⁻⁶ с⁻²  розтяг", size=12, color=PUSH, anchor="start"))
    f.append(text(tx, y + 24, "K⊥ =  GM/R³ =  g/R ≈ 1.54·10⁻⁶ с⁻²  стиск", size=12, color=GRAV, anchor="start"))
    f.append(text(tx, y + 46, "розтяг − 2·стиск = 0   (нема джерел)", size=11.5, color=MUTED, anchor="start"))
    f.append(text(tx, y + 84, "Скринька 1 м — однорідність поля:", size=12, bold=True, anchor="start"))
    f.append(text(tx + 16, y + 106, "до 10⁻⁹  →  d < 3 мм", size=12, anchor="start"))
    f.append(text(tx + 16, y + 126, "до 10⁻¹⁵ →  d < 3 нм", size=12, anchor="start"))
    f.append(text(tx, y + 164, "Дві маси 1 м нарізно розходяться:", size=12, bold=True, anchor="start"))
    f.append(text(tx + 16, y + 186, "на 1 мкм  →  за 0.80 с", size=12, anchor="start"))
    f.append(text(tx + 16, y + 206, "на 1 мм   →  за 25 с", size=12, anchor="start"))
    return render(os.path.join(IMG, "tidal-box.svg"), W, H, *f)


# ── Фігура 8: три ситуації — той самий давач, два однакові покази (для proj-вставки) ──
def fig_accel_readouts():
    W, H = 920, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Три ситуації — і той самий акселерометр: два покази однакові",
                  size=16, bold=True))

    def sensor(cx, cy, s=40):
        return (rect(cx - s / 2, cy - s / 2, s, s, fill="#e8edf3", stroke=LINE, sw=1.8, rx=7)
                + circle(cx, cy, 6, fill="#ffffff", stroke=GRAV, sw=2))

    def readout(cx, cy, valstr, color, w=156, h=60):
        return (rect(cx - w / 2, cy - h / 2, w, h, fill="#f7fafc", stroke=color, sw=2.6, rx=8)
                + text(cx, cy + 2, valstr, size=25, bold=True, color=color)
                + text(cx, cy + 21, "м/с²", size=10.5, color=MUTED))

    cols = [
        (200, "лежить на столі",    "table",  "+9.81", POS,   "f = 0 − (−9.81) = +9.81"),
        (460, "вільно падає",       "fall",   "0.00",  FIELD, "f = −9.81 − (−9.81) = 0"),
        (720, "ракета в порожнечі", "rocket", "+9.81", POS,   "f = +9.81 − 0 = +9.81"),
    ]
    cyb = 122
    for cx, label, kind, val, col, formula in cols:
        f.append(text(cx, 64, label, size=13.5, bold=True))
        f.append(sensor(cx, cyb))
        if kind == "table":
            f.append(hatched_ground(cx - 44, cx + 44, cyb + 26, n=5))
        elif kind == "fall":
            for dx in (-34, 34):
                f.append(arrow(cx + dx, cyb - 18, cx + dx, cyb + 20, color=GRAV, sw=2.2))
            f.append(text(cx, cyb + 46, "↓ падає з g", size=11, color=MUTED))
        else:  # rocket
            f.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s"/>'
                     % (cx - 18, cyb + 20, cx + 18, cyb + 20, cx, cyb + 52, PUSH))
            f.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s"/>'
                     % (cx - 9, cyb + 20, cx + 9, cyb + 20, cx, cyb + 38, "#f6c445"))
        f.append(text(cx, 192, "показ  f", size=11.5, color=MUTED))
        f.append(readout(cx, 230, val, col))
        f.append(text(cx, 288, formula, size=12, color=INK))

    # висновок + з'єднувачі до двох ОДНАКОВИХ показів (стовпці 1 і 3)
    cb, _, cbh = textbox(460, 372,
                         "показ 1  =  показ 3  =  +9.81   →   стіл і ракету не розрізнити",
                         size=12.5, pad=10, fill="#fdecea", stroke=POS, sw=1.6)
    ytop = 372 - cbh / 2 - 2
    f.append(line(200, 261, 372, ytop, color=POS, sw=1.4, dash="4,4"))
    f.append(line(720, 261, 548, ytop, color=POS, sw=1.4, dash="4,4"))
    f.append(cb)
    return render(os.path.join(IMG, "accel-readouts.svg"), W, H, *f)


# ── Фігура 9: спільна сліпа пляма — нахил і розгін дають той самий показ (для proj) ──
def fig_accel_blindspot():
    W, H = 940, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Той самий показ: нахил у тяжіння й справжній розгін — не розрізнити",
                  size=15.5, bold=True))
    f.append(line(470, 58, 470, 388, color="#dfe4ea", sw=1.3, dash="4,6"))

    def tilted_sensor(cx, cy, half, deg):
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        pts = [(cx + dx * c - dy * s, cy + dx * s + dy * c)
               for dx, dy in ((-half, -half), (half, -half), (half, half), (-half, half))]
        path = " ".join("%.1f,%.1f" % p for p in pts)
        out = ('<polygon points="%s" fill="#e8edf3" stroke="%s" stroke-width="1.8"/>'
               % (path, LINE)) + circle(cx, cy, 6, fill="#ffffff", stroke=GRAV, sw=2)
        return out, (c, s)

    # ── ЛІВОРУЧ: нерухомий, нахилений ──
    f.append(text(250, 66, "Нерухомий, але нахилений на φ", size=13.5, bold=True))
    cxL, cyL = 250, 172
    body, (fx, fy) = tilted_sensor(cxL, cyL, 34, -20)
    f.append(line(cxL - fx * 74, cyL - fy * 74, cxL + fx * 74, cyL + fy * 74,
                  color=MUTED, sw=1.3, dash="5,5"))
    f.append(body)
    f.append(arrow(cxL, cyL, cxL, cyL - 66, color=GRAV, sw=3))
    f.append(text(cxL, cyL - 76, "g (реакція)", size=12, bold=True, color=GRAV))
    f.append(arrow(cxL, cyL, cxL + fx * 50, cyL + fy * 50, color=POS, sw=3))
    f.append(text(cxL + fx * 50 + 32, cyL + fy * 50 - 6, "g·sinφ", size=12.5, bold=True,
                  color=POS, anchor="start"))
    cb, _, _ = textbox(250, 332,
                       "нерухомий:  a = 0,  нахил φ = 3°\n→ поздовжній показ  g·sin3° = 0.51 м/с²",
                       size=12, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(cb)

    # ── ПРАВОРУЧ: рівний, розганяється вперед ──
    f.append(text(690, 66, "Рівний, але розганяється вперед", size=13.5, bold=True))
    cxR, cyR = 690, 172
    body2, _ = tilted_sensor(cxR, cyR, 34, 0)
    f.append(line(cxR - 78, cyR, cxR + 78, cyR, color=MUTED, sw=1.3, dash="5,5"))
    f.append(body2)
    f.append(arrow(cxR, cyR, cxR + 66, cyR, color=POS, sw=3))
    f.append(text(cxR + 8, cyR - 12, "a = g·sin3°", size=12.5, bold=True, color=POS, anchor="start"))
    cb, _, _ = textbox(690, 332,
                       "рівний:  справжній розгін уперед\na = 0.51 м/с²  →  той самий поздовжній показ",
                       size=12, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(cb)

    # ── низ: висновок ──
    cb, _, _ = textbox(470, 436,
                       "Акселерометр видає ОДНЕ поздовжнє число — 0.51 м/с². Нахил чи розгін — не розрізнити.\n"
                       "Алгоритм читає нахил як розгін: фальшивий дрейф  ½·g·sinφ·t² ≈ 924 м за хвилину.",
                       size=12.5, pad=11, fill="#fdecea", stroke=POS, sw=1.6)
    f.append(cb)
    return render(os.path.join(IMG, "accel-blindspot.svg"), W, H, *f)


if __name__ == "__main__":
    p1 = fig_two_masses()
    p2 = fig_elevator()
    p3 = fig_tidal()
    p4 = fig_timeline()
    p5 = fig_torsion()
    p6 = fig_eotvos_centrifugal()
    p7 = fig_tidal_box()
    p8 = fig_accel_readouts()
    p9 = fig_accel_blindspot()
    print("written:")
    for p in (p1, p2, p3, p4, p5, p6, p7, p8, p9):
        print("  ", p)
