# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

CW  = "#c0392b"   # за годинниковою — гарячий
CCW = "#2457d6"   # проти годинникової — холодний


def rotor(cx, cy, r, spin, label=None, lc=INK):
    """Кружок-ротор зі стрілкою обертання. spin: +1 = CW, -1 = CCW."""
    col = CW if spin > 0 else CCW
    out = circle(cx, cy, r, fill="#ffffff", stroke=col, sw=2.4)
    # дуга-стрілка напряму обертання
    a0, a1 = (-70, 150) if spin > 0 else (250, 30)
    x0 = cx + r * 0.72 * math.cos(math.radians(a0))
    y0 = cy - r * 0.72 * math.sin(math.radians(a0))
    x1 = cx + r * 0.72 * math.cos(math.radians(a1))
    y1 = cy - r * 0.72 * math.sin(math.radians(a1))
    sweep = 1 if spin > 0 else 0
    out += ('<path d="M %.1f %.1f A %.1f %.1f 0 1 %d %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
            % (x0, y0, r * 0.72, r * 0.72, sweep, x1, y1, col))
    if label:
        out += text(cx, cy + 4, label, size=13, color=lc, bold=True)
    return out


# ── Фігура 1: + проти X — та сама схема обертань, різні осі керування ──────────
def fig_plus_vs_x():
    W, H = 720, 380
    parts = []
    R = 24

    def frame(cx, cy, plus, tag):
        out = []
        arm = 82
        if plus:  # рами під 0/90/180/270
            pos = [(cx, cy - arm), (cx + arm, cy), (cx, cy + arm), (cx - arm, cy)]
        else:     # рами під 45/135/225/315
            d = arm * 0.707
            pos = [(cx + d, cy - d), (cx + d, cy + d), (cx - d, cy + d), (cx - d, cy - d)]
        # промені-балки
        for (px, py) in pos:
            out.append(line(cx, cy, px, py, color=MUTED, sw=6))
        out.append(circle(cx, cy, 12, fill="#eef1f4", stroke=LINE, sw=1.5))
        # напрям «уперед» (ніс) — угору
        out.append(arrow(cx, cy, cx, cy - arm - 34, color=INK, sw=2.2))
        out.append(text(cx, cy - arm - 42, "ніс", size=12, color=INK, bold=True))
        # ротори: діагональні — один напрям (CW), сусідні — інший (CCW)
        # порядок pos: [перед/правий-перед, правий/правий-зад, зад/лівий-зад, лівий/лівий-перед]
        spins = [+1, -1, +1, -1]
        for (px, py), s in zip(pos, spins):
            out.append(rotor(px, py, R, s))
        out.append(text(cx, cy + arm + 44, tag, size=14, color=INK, bold=True))
        return "".join(out)

    parts.append(frame(185, 175, True,  "Плюс-рама (+)"))
    parts.append(frame(535, 175, False, "Ікс-рама (X)"))

    # легенда
    ly = 330
    parts.append(circle(250, ly, 9, fill="#ffffff", stroke=CW, sw=2.4))
    parts.append(text(268, ly + 4, "за годинниковою", size=12, color=CW, anchor="start"))
    parts.append(circle(430, ly, 9, fill="#ffffff", stroke=CCW, sw=2.4))
    parts.append(text(448, ly + 4, "проти годинникової", size=12, color=CCW, anchor="start"))

    render(os.path.join(IMG, 'plus-vs-x.svg'), W, H, *parts,
           title="Одна логіка обертань, дві геометрії керма")


# ── Фігура 2: внесок одного ротора у сумарний віслюк сил (force + torque) ──────
def fig_wrench():
    W, H = 700, 340
    parts = []
    cx, cy = 210, 200
    arm = 150
    # тіло й балка
    parts.append(circle(cx, cy, 14, fill="#eef1f4", stroke=LINE, sw=1.6))
    parts.append(text(cx, cy + 34, "центр мас", size=12, color=MUTED))
    parts.append(line(cx, cy, cx + arm, cy, color=MUTED, sw=6))
    # ротор на кінці балки
    rx, ry = cx + arm, cy
    parts.append(rotor(rx, ry, 26, +1))
    # тяга — з площини вгору (показуємо як стрілку «на нас/угору»)
    parts.append(arrow(rx, ry - 30, rx, ry - 105, color=FIELD, sw=2.6))
    parts.append(text(rx + 6, ry - 90, "тяга T", size=13, color=FIELD, anchor="start", bold=True))
    # плече
    parts.append(line(cx, cy + 70, rx, cy + 70, color=INK, sw=1.2, dash="4 4"))
    parts.append(line(cx, cy, cx, cy + 76, color=INK, sw=1, dash="4 4"))
    parts.append(line(rx, ry, rx, cy + 76, color=INK, sw=1, dash="4 4"))
    parts.append(text((cx + rx) / 2, cy + 88, "плече d", size=12, color=INK, bold=True))
    # реактивний момент навколо осі ротора
    parts.append(text(rx, ry + 52, "реактивний момент Q", size=11, color=CW))

    # праворуч — три наслідки
    bx = 470
    b, w1, h1 = textbox(bx, 92, "T · d  →\nнахил (крен/тангаж)", size=13,
                        fill="#eafaf1", stroke=FIELD, color=INK)
    parts.append(b)
    b, w2, h2 = textbox(bx, 175, "Q  →\nрискання (yaw)", size=13,
                        fill="#fdecea", stroke=CW, color=INK)
    parts.append(b)
    b, w3, h3 = textbox(bx, 258, "ΣT  →\nпідйом угору", size=13,
                        fill="#eef1f4", stroke=LINE, color=INK)
    parts.append(b)

    render(os.path.join(IMG, 'rotor-wrench.svg'), W, H, *parts,
           title="Один ротор дає силу, момент від плеча і реактивний момент")


# ── Фігура 3: чому фіксована вертикальна тяга = недокерованість ────────────────
def fig_underactuated():
    W, H = 700, 320
    parts = []

    def craft(cx, cy, tilt, caption, moving):
        out = []
        L = 70
        a = math.radians(tilt)
        # корпус (лінія-платформа), нахилена на tilt
        dx, dy = L * math.cos(a), -L * math.sin(a)
        out.append(line(cx - dx, cy - dy, cx + dx, cy + dy, color=MUTED, sw=7))
        out.append(circle(cx, cy, 10, fill="#eef1f4", stroke=LINE, sw=1.5))
        # тяга — завжди перпендикулярна платформі (з тіла вгору)
        nx, ny = math.sin(a), -math.cos(a)   # нормаль до платформи
        tl = 80
        out.append(arrow(cx, cy, cx + nx * tl, cy + ny * tl, color=FIELD, sw=2.6))
        out.append(text(cx + nx * tl - 4, cy + ny * tl - 8, "T", size=13, color=FIELD, bold=True))
        # горизонтальна складова руху
        if moving:
            hx = nx * tl
            out.append(arrow(cx, cy + 52, cx + hx * 0.9, cy + 52, color=INK, sw=2.2))
            out.append(text(cx + hx * 0.45, cy + 74, "рух убік", size=12, color=INK, bold=True))
        out.append(text(cx, cy + 104, caption, size=13, color=INK, bold=True))
        return "".join(out)

    parts.append(craft(180, 150, 0,  "Рівна платформа:\nтяга строго вгору, убік — нікуди", False))
    parts.append(craft(520, 150, 25, "Нахилив усю раму —\nз'явилась бічна складова", True))

    render(os.path.join(IMG, 'underactuated.svg'), W, H, *parts,
           title="Щоб полетіти вбік, звичайна рама мусить нахилитися")


# ── Фігура (math-mixer-matrix): геометрія мотора → його стовпчик у матриці ─────
def fig_motor_to_column():
    """Три числа про мотор (xᵢ уперед, yᵢ убік, σᵢ обертання) перетворюються
    на його стовпчик [1, −yᵢ, +xᵢ, σᵢ·κ] у матриці розподілу."""
    W, H = 720, 380
    parts = []
    cx, cy = 175, 195

    # тіло, осі body-frame
    parts.append(circle(cx, cy, 12, fill="#eef1f4", stroke=LINE, sw=1.6))
    parts.append(arrow(cx, cy, cx, cy - 120, color=MUTED, sw=1.8))  # +x (ніс, угору на схемі)
    parts.append(text(cx + 10, cy - 112, "x (ніс)", size=11, color=MUTED, anchor="start"))
    parts.append(arrow(cx, cy, cx + 118, cy, color=MUTED, sw=1.8))  # +y (праворуч)
    parts.append(text(cx + 90, cy - 8, "y (правий борт)", size=11, color=MUTED, anchor="start"))

    # один мотор у точці (уперед-праворуч)
    mx, my = cx + 92, cy - 68
    parts.append(line(cx, cy, mx, my, color=MUTED, sw=5))
    parts.append(rotor(mx, my, 22, +1))
    # плече-координати
    parts.append(line(cx, my, mx, my, color=INK, sw=1, dash="4 4"))
    parts.append(line(mx, cy, mx, my, color=INK, sw=1, dash="4 4"))
    parts.append(text((cx + mx) / 2, my - 7, "yᵢ", size=12, color=INK, bold=True))
    parts.append(text(mx + 8, (cy + my) / 2, "xᵢ", size=12, color=INK, anchor="start", bold=True))
    parts.append(text(mx, my - 30, "мотор i, σᵢ", size=11, color=INK, bold=True))

    # праворуч — стовпчик цього мотора
    b, w, h = textbox(545, 108, "стовпчик мотора i\nу матриці розподілу:", size=13,
                      fill="#eef1f4", stroke=LINE, color=INK)
    parts.append(b)
    rows = [
        ("1", "тяга — завжди вгору"),
        ("−yᵢ", "плече вбік → крен"),
        ("+xᵢ", "плече вперед → тангаж"),
        ("σᵢ·κ", "напрям обертання → рискання"),
    ]
    y = 162
    for lhs, rhs in rows:
        parts.append(text(430, y, lhs, size=14, color=INK, anchor="start", bold=True))
        parts.append(text(478, y, rhs, size=11, color=MUTED, anchor="start"))
        y += 44

    render(os.path.join(IMG, 'motor-to-column.svg'), W, H, *parts,
           title="Три числа про мотор → його стовпчик матриці")


# ── Вставка (hist): механічний баланс реактивних моментів у де Ботеза ──────────
def fig_hist_torque_balance():
    """Дві діагоналі гвинтів, зустрічні обертання; баланс тримає не чип,
    а важіль пілота, що змінює крок усіх чотирьох гвинтів разом."""
    W, H = 720, 400
    parts = []
    cx, cy = 230, 200
    arm = 128
    # хрест балок-ферм (bridge-like girders) — товсті, «важкі»
    pos = [(cx, cy - arm), (cx + arm, cy), (cx, cy + arm), (cx - arm, cy)]
    for (px, py) in pos:
        parts.append(line(cx, cy, px, py, color=MUTED, sw=9))
    parts.append(circle(cx, cy, 15, fill="#eef1f4", stroke=LINE, sw=1.8))
    # шестилопатеві гвинти: північ/південь — один напрям, схід/захід — інший
    spins = [+1, -1, +1, -1]
    for (px, py), s in zip(pos, spins):
        parts.append(rotor(px, py, 30, s))
        # натяк на 6 лопатей — короткі промінці всередині кола
        for k in range(6):
            a = math.radians(k * 60 + (12 if s > 0 else -12))
            parts.append(line(px, py, px + 22 * math.cos(a), py - 22 * math.sin(a),
                              color=(CW if s > 0 else CCW), sw=1.1))
    parts.append(text(cx, cy + arm + 46, "чотири шестилопатеві гвинти", size=12, color=INK, bold=True))
    parts.append(text(cx, cy - arm - 40, "діагоналі — зустрічні обертання", size=11, color=MUTED))

    # праворуч — хто ж «рахує» баланс: не чип, а пілот через тяги
    b, w, h = textbox(560, 95, "БЕЗ електроніки", size=13,
                      fill="#fdecea", stroke=CW, color=INK, bold=True)
    parts.append(b)
    rows = [
        "штурвали + важіль + педалі",
        "тяги й ексцентрики →",
        "змінюють КРОК усіх гвинтів",
        "пілот балансує сам,",
        "щомиті, усіма кінцівками",
    ]
    y = 150
    for r in rows:
        parts.append(text(430, y, r, size=12, color=INK, anchor="start"))
        y += 26
    parts.append(text(430, y + 8, "сумарний закрут = 0", size=12, color=FIELD, anchor="start", bold=True))

    render(os.path.join(IMG, 'hist-torque-balance.svg'), W, H, *parts,
           title="Баланс чотирьох гвинтів — механічно, важелем пілота")


# ── Вставка (hist): проліферація гвинтів Оемішена проти сучасного чипа ─────────
def fig_hist_oehmichen_vs_chip():
    """Ліворуч: 4 несучі + 8 допоміжних гвинтів від ОДНОГО двигуна, ролі кольором.
    Праворуч: те саме керування, згорнуте в один чип із 4 моторами."""
    W, H = 720, 430
    parts = []

    # ── Ліворуч: машина Оемішена ──
    cx, cy = 195, 205
    # хрест
    arm = 96
    lift = [(cx, cy - arm), (cx + arm, cy), (cx, cy + arm), (cx - arm, cy)]
    for (px, py) in lift:
        parts.append(line(cx, cy, px, py, color=MUTED, sw=7))
    parts.append(circle(cx, cy, 12, fill="#eef1f4", stroke=LINE, sw=1.6))
    # 4 несучі гвинти (зустрічні)
    for (px, py), s in zip(lift, [+1, -1, +1, -1]):
        parts.append(rotor(px, py, 21, s))
    # допоміжні: 5 горизонтальних (стабілізація) — маленькі зелені; 1 ніс (кермо); 2 тяга
    aux_stab = [(cx - 55, cy - 55), (cx + 55, cy - 55), (cx + 55, cy + 55),
                (cx - 55, cy + 55), (cx, cy + 40)]
    for (px, py) in aux_stab:
        parts.append(circle(px, py, 8, fill="#eafaf1", stroke=FIELD, sw=1.8))
    # ніс — кермо (один)
    parts.append(circle(cx, cy - 40, 8, fill="#fdecea", stroke=CW, sw=1.8))
    # тяга — пара
    for px in (cx - 34, cx + 34):
        parts.append(circle(px, cy, 8, fill="#eef1f4", stroke=INK, sw=1.8))
    parts.append(text(cx, cy - arm - 30, "один двигун → 12 гвинтів", size=12, color=INK, bold=True))
    parts.append(text(cx, cy + arm + 34, "Оемішен № 2 (1924)", size=12, color=MUTED, bold=True))

    # легенда ролей
    ly = 372
    parts.append(circle(60, ly, 7, fill="#ffffff", stroke=CW, sw=2))
    parts.append(text(72, ly + 4, "несуть", size=11, color=INK, anchor="start"))
    parts.append(circle(150, ly, 7, fill="#eafaf1", stroke=FIELD, sw=1.8))
    parts.append(text(162, ly + 4, "стабілізують (×5)", size=11, color=INK, anchor="start"))
    parts.append(circle(300, ly, 7, fill="#fdecea", stroke=CW, sw=1.8))
    parts.append(text(312, ly + 4, "кермо + тяга", size=11, color=INK, anchor="start"))

    # ── стрілка «сто років» ──
    parts.append(arrow(400, 200, 470, 200, color=INK, sw=2.4))
    parts.append(text(435, 186, "~100 років", size=11, color=MUTED))

    # ── Праворуч: сучасний квадрокоптер + чип ──
    dx, dy = 570, 175
    a = 88
    d = a * 0.707
    xpos = [(dx + d, dy - d), (dx + d, dy + d), (dx - d, dy + d), (dx - d, dy - d)]
    for (px, py) in xpos:
        parts.append(line(dx, dy, px, py, color=MUTED, sw=6))
    for (px, py), s in zip(xpos, [+1, -1, +1, -1]):
        parts.append(rotor(px, py, 20, s))
    parts.append(rect(dx - 16, dy - 12, 32, 24, fill="#111827", stroke=INK, sw=1.2, rx=3))
    parts.append(text(dx, dy + 4, "µC", size=11, color="#ffffff", bold=True))
    parts.append(text(dx, dy - a - 20, "4 мотори, 0 допоміжних", size=12, color=INK, bold=True))
    parts.append(text(dx, dy + a + 30, "чип рахує баланс", size=12, color=FIELD, bold=True))
    parts.append(text(dx, dy + a + 48, "тисячі разів на секунду", size=11, color=MUTED))

    render(os.path.join(IMG, 'hist-oehmichen-vs-chip.svg'), W, H, *parts,
           title="Ту саму задачу колись розв'язували залізом, тепер — чипом")


if __name__ == '__main__':
    fig_plus_vs_x()
    fig_wrench()
    fig_underactuated()
    fig_motor_to_column()
    fig_hist_torque_balance()
    fig_hist_oehmichen_vs_chip()
    print("figures written")
