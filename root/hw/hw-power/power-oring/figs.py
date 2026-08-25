# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def valve(cx, cy, color, s=14, sw=2.4):
    """Символ однобічного клапана (діод): трикутник вістрям праворуч + катодна риска.
    Струм тече зліва направо (від джерела до шини)."""
    p = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" stroke="%s" stroke-width="%.1f"/>'
         % (cx - s, cy - s, cx - s, cy + s, cx + s, cy, color, sw))
    p += line(cx + s, cy - s, cx + s, cy + s, color=color, sw=sw)
    return p


# ── 1. Просто з'єднати виходи (аварійний зворотний струм) VS через клапани (OR)
def fig_combine_vs_or():
    W, H = 920, 460
    parts = []

    # роздільник між панелями
    parts.append(line(W / 2, 52, W / 2, H - 30, color=MUTED, sw=1, dash="6 6"))

    # ── ЛІВА панель: пряме з'єднання виходів ────────────────────────────────
    parts.append(text(W * 0.25, 66, "Просто з'єднати виходи", size=16, bold=True, color=POS))
    ay, by = 150, 300
    sx = 90
    nx = 300           # спільний вузол
    lx = 380           # навантаження
    ba, wa, ha = textbox(sx, ay, "Блок A\nживий 12 В", size=13, pad=10, bold=True,
                         fill="#eafaf0", stroke=FIELD, color=FIELD)
    bb, wb, hb = textbox(sx, by, "Блок B\nмертвий ≈1 В", size=13, pad=10, bold=True,
                         fill="#fdecea", stroke=POS, color=POS)
    parts += [ba, bb]
    parts.append(line(sx + wa / 2, ay, nx, ay, color=LINE, sw=2))
    parts.append(line(sx + wb / 2, by, nx, by, color=LINE, sw=2))
    parts.append(line(nx, ay, nx, by, color=LINE, sw=2))
    parts.append(circle(nx, (ay + by) / 2, 5, fill=INK, stroke=INK))
    # навантаження
    parts.append(rect(lx, (ay + by) / 2 - 26, 46, 52, fill="#f4f6f8", stroke=LINE, sw=2))
    parts.append(text(lx + 23, (ay + by) / 2 + 4, "наван-", size=11, color=INK, bold=True))
    parts.append(line(nx, (ay + by) / 2, lx, (ay + by) / 2, color=LINE, sw=2))
    # аварійний зворотний струм: з живого A вниз у мертвий B
    parts.append(arrow(nx - 16, ay + 20, nx - 16, by - 20, color=POS, sw=3.6))
    parts.append(fitbox(sx - 6, (ay + by) / 2 - 24, 118, 48,
                        "аварійний струм\nу мертвий блок",
                        size=11, fill="#fdecea", stroke=POS, color=POS, bold=True))

    # ── ПРАВА панель: через однобічні клапани (OR) ──────────────────────────
    off = W / 2
    parts.append(text(W * 0.75, 66, "Через однобічні клапани (OR)", size=16, bold=True, color=FIELD))
    sx2 = off + 60
    vx = off + 250     # клапан
    nx2 = off + 330    # спільна шина
    lx2 = off + 400
    ba2, wa2, ha2 = textbox(sx2, ay, "Блок A\nживий 12 В", size=13, pad=10, bold=True,
                            fill="#eafaf0", stroke=FIELD, color=FIELD)
    bb2, wb2, hb2 = textbox(sx2, by, "Блок B\nмертвий ≈1 В", size=13, pad=10, bold=True,
                            fill="#fdecea", stroke=POS, color=POS)
    parts += [ba2, bb2]
    # верхня гілка (живий) — клапан відкритий, струм у шину
    parts.append(line(sx2 + wa2 / 2, ay, vx - 16, ay, color=LINE, sw=2))
    parts.append(valve(vx, ay, FIELD))
    parts.append(line(vx + 16, ay, nx2, ay, color=LINE, sw=2))
    parts.append(arrow(vx + 20, ay - 20, nx2, ay - 20, color=FIELD, sw=2.6))
    parts.append(text((vx + nx2) / 2, ay - 28, "у шину", size=11, color=FIELD, bold=True))
    # нижня гілка (мертвий) — клапан замкнений, зворотний блокований
    parts.append(line(sx2 + wb2 / 2, by, vx - 16, by, color=LINE, sw=2))
    parts.append(valve(vx, by, POS))
    parts.append(line(vx + 16, by, nx2, by, color=LINE, sw=2))
    parts.append(text(vx, by + 30, "клапан замкнений", size=11, color=POS, bold=True))
    parts.append(text(vx, by + 46, "зворотний = 0", size=11, color=POS))
    # спільна шина + навантаження
    parts.append(line(nx2, ay, nx2, by, color=INK, sw=3))
    parts.append(circle(nx2, ay, 4, fill=INK, stroke=INK))
    parts.append(rect(lx2, (ay + by) / 2 - 26, 46, 52, fill="#eafaf0", stroke=FIELD, sw=2))
    parts.append(text(lx2 + 23, (ay + by) / 2 + 4, "наван-", size=11, color=FIELD, bold=True))
    parts.append(line(nx2, (ay + by) / 2, lx2, (ay + by) / 2, color=INK, sw=3))

    # нижня плашка-висновок
    parts.append(fitbox(W * 0.5 - 340, H - 44, 680, 32,
                        "Клапан у кожній гілці пускає струм лише В шину — мертве джерело вже не сток, а живе тримає навантаження.",
                        size=12, fill="#f4f6f8", stroke=LINE, color=INK))
    return render(os.path.join(OUT, 'combine-vs-or.svg'), W, H, *parts,
                  title="Об'єднання джерел: пряме з'єднання (небезпечне) проти ORing")


# ── 2. Безшовне перемикання: шина йде за найвищим джерелом ──────────────────
def fig_failover():
    W, H = 820, 430
    parts = []
    ox, oy = 96, 350          # початок координат
    aw, ah = 660, 250
    Vmax = 13.0               # верх шкали напруги
    parts.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=2))          # X: час
    parts.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=2))          # Y: напруга
    parts.append(text(ox + aw - 4, oy + 26, "час →", size=13, color=INK, anchor="end"))
    parts.append(text(ox - 8, oy - ah + 2, "напруга", size=13, color=INK, anchor="end"))

    def yv(v):
        return oy - ah * (v / Vmax)

    def xt(f):
        return ox + aw * f

    # джерело A (вище): тримається, тоді падає (відмова) на 0.50..0.62
    def A(f):
        if f < 0.50:
            return 12.6
        if f < 0.62:
            return 12.6 * (1 - (f - 0.50) / 0.12)
        return 0.0
    # джерело B (нижче): стабільне
    def B(f):
        return 12.0
    drop = 0.10               # крихітний спад на активному клапані

    N = 160
    ptsA, ptsB, ptsBus = [], [], []
    for i in range(N + 1):
        f = i / N
        ptsA.append((xt(f), yv(A(f))))
        ptsB.append((xt(f), yv(B(f))))
        ptsBus.append((xt(f), yv(max(A(f), B(f)) - drop)))

    def poly(pts, color, sw):
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)

    # лінія критичного мінімуму навантаження
    parts.append(line(ox, yv(11.0), ox + aw, yv(11.0), color=MUTED, sw=1.4, dash="6 5"))
    parts.append(text(ox + aw, yv(11.0) - 8, "мінімум для навантаження 11 В", size=11, color=MUTED, anchor="end"))

    parts.append(poly(ptsA, POS, 2.2))
    parts.append(poly(ptsB, NEG, 2.2))
    parts.append(poly(ptsBus, FIELD, 4.0))

    # підписи трас
    parts.append(text(xt(0.06), yv(12.6) - 10, "джерело A (вище)", size=12, color=POS, anchor="start", bold=True))
    parts.append(text(xt(0.06), yv(12.0) + 18, "джерело B (нижче)", size=12, color=NEG, anchor="start", bold=True))
    parts.append(text(xt(0.70), yv(11.9) + 22, "шина = найвище − крихітний спад", size=12, color=FIELD, anchor="start", bold=True))

    # точка передачі (A впав нижче B)
    fx = 0.585
    parts.append(line(xt(fx), oy, xt(fx), yv(12.7), color=MUTED, sw=1, dash="4 4"))
    parts.append(circle(xt(fx), yv(12.0 - drop), 5, fill=FIELD, stroke=FIELD))
    parts.append(fitbox(xt(fx) - 96, oy - ah - 10, 210, 40,
                        "A впав нижче B → B підхоплює",
                        size=12, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))
    # позначка відмови A
    parts.append(text(xt(0.55), yv(6.0), "A відмовляє", size=12, color=POS, anchor="middle", bold=True))
    return render(os.path.join(OUT, 'failover.svg'), W, H, *parts,
                  title="Безшовна передача: шина йде за найвищим живим джерелом")


# ── 3. Швидкість зачинення вирішує: заряд, вирваний із шини під час аварії ───
def fault_panel(parts, y0, spike_w, title, qtext, verdict, vcolor):
    x0 = 130                  # старт траси
    xf = 320                  # мить замикання
    xend = 560
    fwd = 22                  # прямий струм (пікселів угору)
    rev = 66                  # зворотний пік (пікселів униз)
    # нульова лінія струму
    parts.append(line(x0, y0, xend, y0, color=MUTED, sw=1.2, dash="5 4"))
    parts.append(text(x0 - 8, y0 + 4, "0", size=11, color=MUTED, anchor="end"))
    parts.append(text(x0 - 26, y0 - 26, "струм", size=11, color=MUTED, anchor="start"))
    # прямий струм у шину
    parts.append(line(x0, y0 - fwd, xf, y0 - fwd, color=FIELD, sw=2.6))
    parts.append(text((x0 + xf) / 2, y0 - fwd - 8, "прямий +8 А", size=11, color=FIELD, bold=True))
    # мить замикання
    parts.append(line(xf, y0 - fwd - 6, xf, y0 + rev + 6, color=POS, sw=1, dash="4 3"))
    # зворотний кидок (заштрихована площа = заряд, вирваний із шини)
    x2 = xf + spike_w
    parts.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f z" '
                 'fill="%s" fill-opacity="0.18" stroke="%s" stroke-width="2.4"/>'
                 % (xf, y0, xf, y0 + rev, x2, y0 + rev, x2, y0, POS, POS))
    parts.append(line(x2, y0, xend, y0, color=FIELD, sw=2.2))   # після зачинення струм = 0
    # заголовок панелі
    parts.append(text(x0, y0 - 58, title, size=14, bold=True, color=vcolor))
    # мітки
    parts.append(text(xf + 6, y0 + rev + 18, "зворотний −50 А", size=11, color=POS, anchor="start", bold=True))
    parts.append(text(xf, y0 + rev + 34, "замкнуло", size=11, color=POS, anchor="middle"))
    # права колонка: заряд і провал шини
    parts.append(fitbox(600, y0 - 42, 290, 40, qtext,
                        size=12, fill="#fdecea", stroke=POS, color=POS, bold=True))
    parts.append(fitbox(600, y0 + 8, 290, 40, verdict,
                        size=12, fill="#eafaf0" if vcolor == FIELD else "#fdecea",
                        stroke=vcolor, color=vcolor, bold=True))


def fig_fault_turnoff():
    W, H = 940, 470
    parts = []
    fault_panel(parts, 150, 26,
                "Швидке зачинення (активний ORing, ~300 нс)",
                "Q ≈ 50 А · 0.3 мкс = 15 мкКл",
                "провал шини ≈ 32 мВ — шина жива", FIELD)
    fault_panel(parts, 360, 220,
                "Повільне зачинення (~20 мкс)",
                "Q ≈ 50 А · 20 мкс = 1000 мкКл",
                "провал шини ≈ 2.1 В — шина падає", POS)
    parts.append(fitbox(W * 0.5 - 330, H - 34, 660, 28,
                        "Провал шини ΔV = Q / C_шини: що швидше клапан зачиниться, то менший заряд вирветься з шини.",
                        size=12, fill="#f4f6f8", stroke=LINE, color=INK))
    return render(os.path.join(OUT, 'fault-turnoff.svg'), W, H, *parts,
                  title="Аварія-замикання: швидкість зачинення тримає спільну шину")


# ═══ Фігури вставки math-oring-fault-dynamics ═══════════════════════════════
import math

# Наскрізний вузол вставки
V0, CB, LP = 12.0, 470e-6, 100e-9
T0 = math.sqrt(LP * CB)          # 6.86 мкс
Z0 = math.sqrt(LP / CB)          # 14.6 мОм
TOFF = 206.7e-9                  # 42 + 150 + 15 нс
IPK = V0 / LP * TOFF             # 24.8 А


# ── 4. Контур аварії: що насправді обмежує зворотний кидок ──────────────────
def fig_fault_loop():
    W, H = 1000, 510
    parts = []
    parts.append(line(515, 52, 515, H - 66, color=MUTED, sw=1, dash="6 6"))

    # ── ЛІВА панель: схема контуру ──────────────────────────────────────────
    parts.append(text(280, 66, "Контур аварії", size=16, bold=True, color=INK))
    xl, xr, yt, yb = 190, 440, 180, 400          # рамка контуру

    # верхня й нижня шини, права стійка
    parts.append(line(xl, yt, xr, yt, color=INK, sw=2.6))
    parts.append(line(xl, yb, xr, yb, color=INK, sw=2.6))
    parts.append(line(xr, yt, xr, 213, color=INK, sw=2.6))
    parts.append(line(xr, 257, xr, 310, color=INK, sw=2.6))
    parts.append(line(xr, 350, xr, yb, color=INK, sw=2.6))
    # ліва стійка з конденсатором
    parts.append(line(xl, yt, xl, 280, color=INK, sw=2.6))
    parts.append(line(xl, 300, xl, yb, color=INK, sw=2.6))
    parts.append(line(165, 280, 215, 280, color=NEG, sw=3.4))
    parts.append(line(165, 300, 215, 300, color=NEG, sw=3.4))
    parts.append(text(155, 285, "C_шини", size=12, color=NEG, anchor="end", bold=True))
    parts.append(text(155, 303, "470 мкФ", size=12, color=NEG, anchor="end"))

    # клапан і котушка контуру на правій стійці
    parts.append(rect(400, 213, 80, 44, fill="#eafaf0", stroke=FIELD, sw=2.2))
    parts.append(text(440, 240, "клапан", size=12, color=FIELD, bold=True))
    parts.append(rect(400, 310, 80, 40, fill="#eaf0fd", stroke=NEG, sw=2.2))
    parts.append(text(440, 336, "L", size=15, color=NEG, bold=True))
    b1, _, _ = textbox(330, 235, "R_DS(on) = 2 мОм", size=11, pad=8,
                       fill="#f4f6f8", stroke=FIELD, color=FIELD)
    b2, _, _ = textbox(330, 330, "L = 100 нГн", size=11, pad=8,
                       fill="#f4f6f8", stroke=NEG, color=NEG)
    parts += [b1, b2]

    # місце замикання
    parts.append(circle(xr, yb, 7, fill=POS, stroke=POS))
    parts.append(line(xr - 9, yb - 9, xr + 9, yb + 9, color=POS, sw=3))
    parts.append(line(xr - 9, yb + 9, xr + 9, yb - 9, color=POS, sw=3))
    parts.append(text(428, 432, "вхід замкнуло → 0 В", size=11, color=POS, bold=True))

    # зворотний струм
    parts.append(arrow(225, 160, 425, 160, color=POS, sw=3.2))
    parts.append(text(325, 146, "зворотний струм i(t)", size=12, color=POS, bold=True))
    parts.append(text(300, 202, "шина 12 В", size=12, color=INK))
    parts.append(text(315, 386, "зворотний шлях", size=11, color=MUTED))

    # ── ПРАВА панель: хто ж обмежує ─────────────────────────────────────────
    parts.append(text(755, 66, "Що обмежує кидок", size=16, bold=True, color=INK))
    parts.append(fitbox(545, 90, 420, 84,
                        "✗  Наївно, за законом Ома:\n"
                        "I = V₀ / R_DS(on) = 12 / 0.002 = 6000 А\n"
                        "Нісенітниця: струм не виникає миттєво.",
                        size=13, fill="#fdecea", stroke=POS, color=POS, bold=True))
    parts.append(fitbox(545, 192, 420, 84,
                        "✓  Насправді тримає індуктивність контуру:\n"
                        "di/dt = V₀ / L = 12 / 100 нГн = 120 А/мкс\n"
                        "За 207 нс сліпоти струм устигає до 24.8 А.",
                        size=13, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))
    parts.append(fitbox(545, 294, 420, 104,
                        "Дві сталі цього контуру:\n"
                        "T₀ = √(L·C) = 6.9 мкс — годинник аварії\n"
                        "Z₀ = √(L/C) = 14.6 мОм — хвильовий опір\n"
                        "Якби клапан не зачинився: V₀/Z₀ = 823 А",
                        size=13, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))

    parts.append(fitbox(60, H - 56, 880, 34,
                        "R_DS(on) зворотного кидка не тримає — його тримає індуктивність контуру. "
                        "Клапану лишається встигнути зачинитися.",
                        size=12, fill="#f4f6f8", stroke=LINE, color=INK))
    return render(os.path.join(OUT, 'fault-loop.svg'), W, H, *parts,
                  title="Аварійне замикання входу: хто дає заряд і хто обмежує струм")


# ── 5. Бюджет часу сліпоти й заряд, вирваний із шини ────────────────────────
def fig_turnoff_budget():
    W, H = 1000, 570
    parts = []

    # ── ВЕРХ: стовпчик бюджету ──────────────────────────────────────────────
    parts.append(text(500, 68, "Бюджет сліпоти:  t_сліп = t_поріг + t_компаратора + t_затвора",
                      size=15, bold=True, color=INK))
    bx0, bx1, by, bh = 90, 910, 112, 40
    segs = [(41.7, NEG, "#eaf0fd", "42 нс", "поріг"),
            (150.0, POS, "#fdecea", "150 нс", "компаратор"),
            (15.0, FIELD, "#eafaf0", "15 нс", "затвор")]
    total = sum(s[0] for s in segs)
    x = bx0
    centers = []
    for dur, col, fill, inside, above in segs:
        w = (bx1 - bx0) * dur / total
        parts.append(rect(x, by, w, bh, fill=fill, stroke=col, sw=2.2, rx=4))
        parts.append(text(x + w / 2, by + 26, inside, size=12, color=col, bold=True))
        parts.append(text(x + w / 2, by - 8, above, size=12, color=col, bold=True))
        centers.append(x + w / 2)
        x += w

    # три пояснювальні картки + тонкі виноски від сегментів
    cards = [(90, "t_поріг = L · I_поріг / V₀\nI_поріг = 10 мВ / 2 мОм = 5 А\n100 нГн · 5 / 12 = 42 нс", NEG, "#eaf0fd"),
             (370, "t_компаратора\nчиста затримка мікросхеми,\nнічим не скоротити: ≈ 150 нс", POS, "#fdecea"),
             (650, "t_затвора = Q_g / I_sink\n30 нКл / 2 А\n= 15 нс", FIELD, "#eafaf0")]
    for i, (cx0, s, col, fill) in enumerate(cards):
        parts.append(line(centers[i], by + bh, cx0 + 130, 186, color=col, sw=1, dash="4 3"))
        parts.append(fitbox(cx0, 186, 260, 74, s, size=12, fill=fill, stroke=col, color=col, bold=True))

    # ── НИЗ: заряд під рампою ───────────────────────────────────────────────
    parts.append(text(420, 292, "Скільки заряду насправді йде з шини", size=15, bold=True, color=INK))
    ox, oy = 150, 470                 # початок координат
    ax, ay = 550, 170                 # довжина осей
    px_ns = 420 / 220.0               # 220 нс на 420 px
    px_a = ay / 30.0                  # 30 А на 170 px
    xoff = ox + TOFF * 1e9 * px_ns    # мить зачинення
    ypk = oy - IPK * px_a

    parts.append(arrow(ox, oy, ox + ax, oy, color=INK, sw=2))
    parts.append(arrow(ox, oy, ox, oy - ay, color=INK, sw=2))
    parts.append(text(ox + ax, oy + 24, "час →", size=12, color=INK, anchor="end"))
    parts.append(text(ox - 10, oy - ay + 4, "|i_зв|", size=12, color=INK, anchor="end"))

    # наївний прямокутник
    parts.append(rect(ox, ypk, xoff - ox, oy - ypk, fill="none", stroke=MUTED, sw=1.8, rx=0))
    parts.append(line(ox, ypk, xoff, ypk, color=MUTED, sw=1.8, dash="6 4"))
    # справжній трикутник
    parts.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" fill-opacity="0.20" '
                 'stroke="%s" stroke-width="2.6"/>' % (ox, oy, xoff, ypk, xoff, oy, POS, POS))
    parts.append(line(xoff, ypk, xoff + 32, oy, color=POS, sw=2.6))
    parts.append(line(xoff, oy, xoff, ypk - 14, color=MUTED, sw=1, dash="4 4"))
    parts.append(text(xoff, oy + 22, "t_сліп = 207 нс", size=11, color=MUTED, bold=True))
    parts.append(text(xoff + 8, ypk - 18, "24.8 А", size=11, color=POS, anchor="start", bold=True))

    parts.append(fitbox(720, 300, 260, 82,
                        "Прямокутник — оцінка «I · t»:\n"
                        "Q = 24.8 А · 207 нс = 5.1 мкКл\n"
                        "ΔV = 10.9 мВ — безпечна стеля",
                        size=12, fill="#f4f6f8", stroke=MUTED, color=MUTED, bold=True))
    parts.append(fitbox(720, 398, 260, 82,
                        "Трикутник — насправді:\n"
                        "Q = ½ · 24.8 А · 207 нс = 2.6 мкКл\n"
                        "ΔV = Q / C_шини = 5.5 мВ",
                        size=12, fill="#fdecea", stroke=POS, color=POS, bold=True))

    parts.append(fitbox(60, H - 46, 880, 34,
                        "Три чверті бюджету з'їдає затримка компаратора, а не затвор. "
                        "Струм росте від нуля — заряд під трикутником удвічі менший за оцінку «I · t».",
                        size=12, fill="#f4f6f8", stroke=LINE, color=INK))
    return render(os.path.join(OUT, 'turnoff-budget.svg'), W, H, *parts,
                  title="Час сліпоти клапана й ціна цього часу для шини")


# ── 6. Провал шини проти часу сліпоти: нахил 2 і стеля ──────────────────────
def fig_tau_curve():
    W, H = 1000, 560
    parts = []
    PX0, PX1, PY0, PY1 = 130, 790, 100, 440     # поле графіка
    LX0, LX1 = 1.0, 4.477                        # log10(t, нс): 10 нс … 30 мкс
    LY0, LY1 = -2.0, 4.3                         # log10(ΔV, мВ): 0.01 мВ … 20 В

    def X(t_ns):
        return PX0 + (math.log10(t_ns) - LX0) / (LX1 - LX0) * (PX1 - PX0)

    def Y(dv_mv):
        return PY1 - (math.log10(dv_mv) - LY0) / (LY1 - LY0) * (PY1 - PY0)

    # зона обвалу: за чверть-періодом шина вже в нулі
    tq = (math.pi / 2) * T0 * 1e9
    parts.append(rect(X(tq), PY0, PX1 - X(tq), PY1 - PY0,
                      fill="#fdecea", stroke="none", sw=0, rx=0))

    # сітка десятків
    for lx, lab in [(1, "10 нс"), (2, "100 нс"), (3, "1 мкс"), (4, "10 мкс")]:
        gx = PX0 + (lx - LX0) / (LX1 - LX0) * (PX1 - PX0)
        parts.append(line(gx, PY0, gx, PY1, color="#e3e6ea", sw=1))
        parts.append(text(gx, PY1 + 22, lab, size=12, color=MUTED))
    for ly, lab in [(-2, "0.01 мВ"), (-1, "0.1 мВ"), (0, "1 мВ"), (1, "10 мВ"),
                    (2, "100 мВ"), (3, "1 В"), (4, "10 В")]:
        gy = PY1 - (ly - LY0) / (LY1 - LY0) * (PY1 - PY0)
        parts.append(line(PX0, gy, PX1, gy, color="#e3e6ea", sw=1))
        parts.append(text(PX0 - 10, gy + 4, lab, size=11, color=MUTED, anchor="end"))
    parts.append(line(PX0, PY0, PX0, PY1, color=INK, sw=2))
    parts.append(line(PX0, PY1, PX1, PY1, color=INK, sw=2))
    parts.append(text(PX1, PY1 + 44, "час сліпоти клапана  t_сліп →", size=13, color=INK, anchor="end"))
    parts.append(text(PX0 - 10, PY0 - 16, "провал шини  ΔV", size=13, color=INK, anchor="start"))

    # крива ΔV = V₀·(1 − cos(t/T₀)) — точний розв'язок LC
    pts = []
    n = 260
    for i in range(1, n + 1):
        t = (math.pi / 2) * T0 * i / n
        dv = V0 * (1 - math.cos(t / T0)) * 1e3
        if dv < 10 ** LY0:
            continue
        pts.append((X(t * 1e9), Y(dv)))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.4"/>' % (d, NEG))

    # стеля й чверть-період
    parts.append(line(PX0, Y(V0 * 1e3), PX1, Y(V0 * 1e3), color=POS, sw=1.6, dash="7 5"))
    parts.append(text(PX0 + 8, Y(V0 * 1e3) - 10, "V₀ = 12 В — шина в нулі",
                      size=11, color=POS, anchor="start", bold=True))
    parts.append(line(X(tq), PY0, X(tq), PY1, color=POS, sw=1.6, dash="7 5"))
    parts.append(text(X(tq) + 8, PY0 + 34, "(π/2)·T₀ = 10.8 мкс", size=11, color=POS,
                      anchor="start", bold=True))
    parts.append(text(X(tq) + 8, PY0 + 50, "далі рахувати нічого", size=11, color=POS, anchor="start"))

    # робочі точки
    marks = [(10, 0.013, "0.01 мВ", NEG),
             (50, 0.32, "0.3 мВ", NEG),
             (207, 5.45, "5.5 мВ", FIELD),
             (500, 31.9, "32 мВ", FIELD),
             (1200, 184.0, "184 мВ", POS)]
    for t_ns, dv, lab, col in marks:
        parts.append(circle(X(t_ns), Y(dv), 6, fill=col, stroke="#ffffff", sw=2))
        parts.append(text(X(t_ns) + 12, Y(dv) + 20, lab, size=11, color=col,
                          anchor="start", bold=True))

    parts.append(text(392, 402, "нахил 2: удвічі швидший клапан → вчетверо менший провал",
                      size=12, color=NEG, anchor="start", bold=True))

    # легенда клапанів
    leg = [(NEG, "Шотткі  < 10 нс"),
           (NEG, "надшвидкий PN  ≈ 50 нс"),
           (FIELD, "активний ORing  207 нс"),
           (FIELD, "LTC4357, даташит  500 нс"),
           (POS, "звичайний PN  1.2 мкс")]
    parts.append(rect(812, 100, 172, 152, fill="#ffffff", stroke=LINE, sw=1.4))
    parts.append(text(898, 124, "клапан і його сліпота", size=11, color=INK, bold=True))
    for i, (col, s) in enumerate(leg):
        yy = 148 + i * 22
        parts.append(circle(828, yy - 4, 5, fill=col, stroke="#ffffff", sw=1.5))
        parts.append(text(842, yy, s, size=11, color=INK, anchor="start"))

    parts.append(fitbox(60, H - 52, 880, 36,
                        "ΔV = ½·V₀·(t_сліп/T₀)² — доки t_сліп ≪ T₀. Права червона зона — не «глибший провал», "
                        "а шина в нулі: формула там уже нічого не описує.",
                        size=12, fill="#f4f6f8", stroke=LINE, color=INK))
    return render(os.path.join(OUT, 'tau-curve.svg'), W, H, *parts,
                  title="Провал шини проти часу сліпоти клапана (V₀ = 12 В, L = 100 нГн, C = 470 мкФ)")


if __name__ == '__main__':
    fig_combine_vs_or()
    fig_failover()
    fig_fault_turnoff()
    fig_fault_loop()
    fig_turnoff_budget()
    fig_tau_curve()
    print('figs done')
