# -*- coding: utf-8 -*-
"""Фігури до теми «Інерціальна система відліку».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

FICT = "#c0392b"   # вигадана сила — гаряче (POS)
MOVE = "#2457d6"   # справжній рух / швидкість — холодне (NEG)


# ── Фігура 1: вільне тіло — пряма в кожній інерціальній системі ──────────────
def fig_galilean_frames():
    W, H = 900, 486
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30,
                  "Вільне тіло — пряма лінія в кожній інерціальній системі; змінюється лише нахил",
                  size=15.5, bold=True))
    f.append(line(452, 60, 452, 402, color="#dfe4ea", sw=1.3, dash="4,6"))

    def panel(ox, title, slope_dx, vlabel):
        oy0, oytop = 392, 128            # низ (t=0) і верх осі часу
        xmax = ox + 196
        out = text(ox + 88, 82, title, size=13.5, bold=True)
        # осі
        out += arrow(ox, oy0, ox, oytop - 8, color=INK, sw=1.8)
        out += text(ox - 12, oytop - 2, "t", size=14, bold=True, italic=True, anchor="end")
        out += arrow(ox, oy0, xmax, oy0, color=INK, sw=1.8)
        out += text(xmax + 6, oy0 + 16, "x", size=14, bold=True, italic=True, anchor="start")
        # світова лінія вільного тіла — рівні кроки часу
        x0, y0, n = ox + 24, oy0 - 12, 5
        dt = (y0 - (oytop + 20)) / n
        pts = [(x0 + i * slope_dx, y0 - i * dt) for i in range(n + 1)]
        out += line(pts[0][0], pts[0][1], pts[-1][0], pts[-1][1], color=MOVE, sw=3)
        for (px, py) in pts:
            out += circle(px, py, 3.6, fill=BG, stroke=MOVE, sw=2)
        # підпис лінії — над верхнім кінцем, ліворуч
        out += text(pts[-1][0] - 8, pts[-1][1] - 10, "вільне тіло",
                    size=12, color=MOVE, bold=True, anchor="end")
        # нахил = швидкість
        mx, my = pts[3]
        out += text(mx + 16, my + 4, vlabel, size=12.5, bold=True, color=MOVE, anchor="start")
        return out

    f.append(panel(118, "Очима системи S", 30, "нахил = v"))
    f.append(panel(556, "Очима системи S′ (їде на V)", 15, "нахил = v − V"))

    b, _, _ = textbox(
        W / 2, 448,
        "нахил (швидкість) різний у різних системах, але лінія лишається ПРЯМОЮ →\n"
        "викривлення (прискорення) нульове в обох → обидві системи інерціальні, жодна не головна",
        size=12.5, pad=12, fill="#eafaf1", stroke=FIELD, sw=1.5)
    f.append(b)
    return render(os.path.join(IMG, "galilean-frames.svg"), W, H, *f)


# ── допоміжне: вагон і склянка ──────────────────────────────────────────────
def wagon(cx, cy, w=176, h=82):
    out = rect(cx - w / 2, cy - h / 2, w, h, fill="#eef2f7", stroke=LINE, sw=1.9, rx=13)
    out += rect(cx - w / 2 + 16, cy - h / 2 + 12, 30, 26, fill="#dbe6f5", stroke=LINE, sw=1.2, rx=4)
    out += rect(cx + w / 2 - 46, cy - h / 2 + 12, 30, 26, fill="#dbe6f5", stroke=LINE, sw=1.2, rx=4)
    out += circle(cx - w / 2 + 40, cy + h / 2 + 12, 13, fill="#d8dee6", stroke=LINE, sw=1.7)
    out += circle(cx + w / 2 - 40, cy + h / 2 + 12, 13, fill="#d8dee6", stroke=LINE, sw=1.7)
    return out


def table_glass(tx, ty):
    """Столик із центром опори (tx) і поверхнею на ty; склянка стоїть зверху."""
    out = rect(tx - 34, ty, 68, 6, fill="#cbb892", stroke=LINE, sw=1.2, rx=2)
    out += line(tx - 26, ty + 6, tx - 26, ty + 20, color=LINE, sw=1.6)
    out += line(tx + 26, ty + 6, tx + 26, ty + 20, color=LINE, sw=1.6)
    # склянка на поверхні (дно на ty)
    gx, gb = tx, ty
    out += ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
            'fill="#fdf6e3" stroke="%s" stroke-width="1.9"/>'
            % (gx - 12, gb - 26, gx + 12, gb - 26, gx + 8, gb, gx - 8, gb, FICT))
    return out


# ── Фігура 2: та сама подія у двох системах — вигадана сила в прискореній ─────
def fig_inertial_vs_braking():
    W, H = 900, 476
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30,
                  "Та сама склянка, дві системи: у гальмівному вагоні з'являється сила без джерела",
                  size=15, bold=True))
    f.append(line(452, 58, 452, 392, color="#dfe4ea", sw=1.3, dash="4,6"))

    # ── ЛІВОРУЧ: перон — інерціальна система ──
    f.append(text(230, 64, "Перон — інерціальна система", size=13.5, bold=True))
    cxL, cyW = 230, 196
    f.append(wagon(cxL, cyW))
    f.append(table_glass(cxL, cyW + 14))            # склянка/стіл усередині вагона
    # склянка зберігає швидкість — пряма зі стрілкою вперед
    f.append(arrow(cxL + 20, cyW - 12, cxL + 96, cyW - 12, color=MOVE, sw=3))
    f.append(text(cxL + 58, cyW - 22, "v", size=14, bold=True, color=MOVE))
    f.append(text(cxL + 20, cyW - 40, "склянка зберігає швидкість", size=11.5, color=MOVE, anchor="start"))
    # вагон гальмує — стрілка назад
    f.append(arrow(cxL - 6, cyW + 74, cxL - 78, cyW + 74, color=FICT, sw=3))
    f.append(text(cxL + 6, cyW + 78, "A: вагон гальмує", size=12, bold=True, color=FICT, anchor="start"))
    bL, _, _ = textbox(230, 348,
                       "горизонтальних сил на склянку немає  →  a = 0\n"
                       "вона просто зберігає швидкість, а стіл тікає з-під неї",
                       size=11.5, pad=10, fill="#eafaf1", stroke=FIELD, sw=1.4)
    f.append(bL)

    # ── ПРАВОРУЧ: вагон — неінерціальна система ──
    f.append(text(668, 64, "Вагон — неінерціальна система", size=13.5, bold=True))
    cxR = 668
    f.append(wagon(cxR, cyW))
    f.append(table_glass(cxR, cyW + 14))
    # велика вигадана сила вперед
    f.append(arrow(cxR + 20, cyW - 12, cxR + 104, cyW - 12, color=FICT, sw=3.6))
    f.append(text(cxR + 24, cyW - 24, "F = m·A", size=13, bold=True, color=FICT, anchor="start"))
    f.append(text(cxR + 24, cyW - 42, "вигадана сила — джерела немає", size=11.5, color=FICT, anchor="start"))
    # склянка сама розганяється
    f.append(text(cxR - 22, cyW + 40, "склянка сама\nрозганяється (a′)", size=11, color=MUTED, anchor="end"))
    bR, _, _ = textbox(668, 348,
                       "склянка сама розганяється вперед з a′ = A\n"
                       "щоб урятувати F = m·a′, дописують силу без джерела",
                       size=11.5, pad=10, fill="#fdecea", stroke=FICT, sw=1.4)
    f.append(bR)

    b, _, _ = textbox(W / 2, 440,
                      "Наявність сил без штовхача — і є прикмета неінерціальної системи.",
                      size=12.5, pad=10, fill=FILL, stroke=LINE, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "inertial-vs-braking.svg"), W, H, *f)


# ── Фігура 3: обертова система — пряма стає кривою, вигадані сили ─────────────
def fig_rotating_frame():
    W, H = 900, 486
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30,
                  "Обертова система: пряма стає кривою, і кривину пояснюють вигаданими силами",
                  size=15, bold=True))
    f.append(line(452, 58, 452, 402, color="#dfe4ea", sw=1.3, dash="4,6"))

    def omega_arc(cx, cy, r):
        sx, sy = cx - 60, cy - (r - 4)
        ex, ey = cx + 60, cy - (r - 4)
        out = ('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
               'stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
               % (sx, sy, r + 14, r + 14, ex, ey, MUTED))
        out += text(cx + 74, cy - r + 6, "ω", size=15, bold=True, italic=True, color=MUTED, anchor="start")
        return out

    R = 104
    # ── ЛІВОРУЧ: нерухома земля — пряма ──
    f.append(text(228, 64, "З нерухомої землі (інерціальна)", size=13.5, bold=True))
    cxL, cyL = 228, 244
    f.append(circle(cxL, cyL, R, fill="#eef3fb", stroke=MOVE, sw=1.8))
    f.append(circle(cxL, cyL, 4, fill=INK, stroke=INK, sw=1))
    f.append(omega_arc(cxL, cyL, R))
    # пряма траєкторія від центра назовні + рівні позначки
    for i in range(1, 6):
        px = cxL + i * 26
        f.append(circle(px, cyL, 3.4, fill=BG, stroke=INK, sw=1.8))
    f.append(arrow(cxL, cyL, cxL + 150, cyL, color=INK, sw=2.6))
    f.append(text(cxL + 96, cyL - 12, "шайба летить прямо", size=11.5, bold=True, anchor="middle"))
    bL, _, _ = textbox(228, 402,
                       "на шайбу не діє нічого  →  чесна пряма",
                       size=12, pad=10, fill="#eafaf1", stroke=FIELD, sw=1.4)
    f.append(bL)

    # ── ПРАВОРУЧ: обертова карусель — крива + вигадані сили ──
    f.append(text(668, 64, "З самої каруселі (неінерціальна)", size=13.5, bold=True))
    cxR, cyR = 668, 244
    f.append(circle(cxR, cyR, R, fill="#fbeeee", stroke=FICT, sw=1.8))
    f.append(circle(cxR, cyR, 4, fill=INK, stroke=INK, sw=1))
    f.append(omega_arc(cxR, cyR, R))
    # де шайба летіла б (пряма, ледь помітна)
    f.append(line(cxR, cyR, cxR + 150, cyR, color=MUTED, sw=1.4, dash="4,5"))
    f.append(text(cxR + 150, cyR + 16, "куди без обертання", size=10.5, color=MUTED, anchor="end"))
    # реальна крива в обертовій системі (квадратична Безьє)
    P0 = (cxR, cyR)
    P1 = (cxR + 80, cyR + 22)
    P2 = (cxR + 92, cyR + 104)
    f.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="3"/>' % (P0[0], P0[1], P1[0], P1[1], P2[0], P2[1], INK))
    # точка-зразок на кривій (t=0.6)
    t = 0.6
    Sx = (1 - t) ** 2 * P0[0] + 2 * (1 - t) * t * P1[0] + t * t * P2[0]
    Sy = (1 - t) ** 2 * P0[1] + 2 * (1 - t) * t * P1[1] + t * t * P2[1]
    f.append(circle(Sx, Sy, 5, fill="#fef6e7", stroke=INK, sw=2))
    # відцентрова — назовні від центра
    dx, dy = Sx - cxR, Sy - cyR
    d = math.hypot(dx, dy)
    ux, uy = dx / d, dy / d
    f.append(arrow(Sx, Sy, Sx + ux * 52, Sy + uy * 52, color=FICT, sw=3))
    f.append(text(Sx + ux * 52 + 6, Sy + uy * 52 + 6, "відцентрова", size=11.5, bold=True,
                  color=FICT, anchor="start"))
    # коріолісова — перпендикулярно швидкості, до увігнутого боку
    Vx = 2 * (1 - t) * (P1[0] - P0[0]) + 2 * t * (P2[0] - P1[0])
    Vy = 2 * (1 - t) * (P1[1] - P0[1]) + 2 * t * (P2[1] - P1[1])
    vd = math.hypot(Vx, Vy)
    nx, ny = -Vy / vd, Vx / vd          # поворот на 90°
    f.append(arrow(Sx, Sy, Sx + nx * 48, Sy + ny * 48, color=MOVE, sw=3))
    f.append(text(Sx + nx * 48 - 6, Sy + ny * 48 + 4, "коріолісова", size=11.5, bold=True,
                  color=MOVE, anchor="end"))
    bR, _, _ = textbox(668, 402,
                       "та сама шайба виписує дугу  →  дописують\nвідцентрову й коріолісову — обидві без джерела",
                       size=11.5, pad=10, fill="#fdecea", stroke=FICT, sw=1.4)
    f.append(bR)
    return render(os.path.join(IMG, "rotating-frame.svg"), W, H, *f)


# ── Фігура 4 (для hist-вставки): шари ідеї за 22 століття ─────────────────────
def fig_inertia_timeline():
    W, H = 980, 616
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Хто винайшов інерціальну систему: поняття зібрано шарами",
                  size=16.5, bold=True))
    f.append(text(W / 2, 57,
                  "згори вниз — за часом (не в масштабі); праворуч — який шар думки додав кожен",
                  size=12, color=MUTED))
    ys = [100, 170, 240, 310, 380, 450, 520]
    f.append(line(72, ys[0], 72, ys[-1], color=MUTED, sw=2))
    rows = [
        ("≈350 до н.е. · Аристотель (Ἀριστοτέλης)",
         "рух треба весь час штовхати — хибний старт", "ХИБНИЙ СТАРТ", MUTED, "#eef0f2"),
        ("1632 · Ґалілео Ґалілей (Galileo Galilei)",
         "відносність руху; тіло само береже рух — та коловий", "ІДЕЯ", NEG, "#eaf0fd"),
        ("1644 · Рене Декарт (René Descartes)",
         "чиста ПРЯМОЛІНІЙНА інерція (Principia, 1644)", "ФОРМУЛЮВАННЯ", NEG, "#eaf0fd"),
        ("1687 · Ісаак Ньютон (Isaac Newton)",
         "перший закон + «абсолютний простір» (Principia)", "КОДИФІКАЦІЯ", FIELD, "#eafaf1"),
        ("1869 · Карл Нойман (Carl Neumann)",
         "«тіло Альфа» — опорне тіло замість простору", "ЗАРОДОК", MUTED, "#eef0f2"),
        ("1883 · Ернст Мах (Ernst Mach)",
         "простір незримий; опора — далекі зорі й маси", "КРИТИКА", POS, "#fdecea"),
        ("1885 · Людвіг Ланге (Ludwig Lange)",
         "термін «інерціальна система» + робочий припис", "ТЕРМІН", FIELD, "#eafaf1"),
    ]
    for y, (l1, l2, tag, col, fillc) in zip(ys, rows):
        f.append(line(79, y, 150, y, color=MUTED, sw=1.4))
        f.append(circle(72, y, 7, fill=col, stroke=col, sw=1))
        f.append(rect(150, y - 27, 560, 54, fill=BG, stroke=LINE, sw=1.3, rx=8))
        fs1 = fit_font(l1, 560 - 26, 13.5, True)
        fs2 = fit_font(l2, 560 - 26, 12.5, False)
        f.append(text(163, y - 6, l1, size=fs1, bold=True, anchor="start"))
        f.append(text(163, y + 15, l2, size=fs2, color=INK, anchor="start"))
        b, _, _ = textbox(812, y, tag, size=12, pad=9, fill=fillc, stroke=col, color=col, bold=True)
        f.append(b)
    b, _, _ = textbox(
        W / 2, 583,
        "Жоден не зробив усе сам: ІДЕЯ (Ґалілей) → ФОРМУЛЮВАННЯ (Декарт) → ЗАКОН і ПРОСТІР (Ньютон) →\n"
        "КРИТИКА (Мах) → ОПЕРАЦІЙНЕ ПОНЯТТЯ Й ТЕРМІН (Ланге, на думці Ноймана)",
        size=12, pad=11, fill="#f4f6f8", stroke=LINE, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "inertia-history-timeline.svg"), W, H, *f)


# ── Фігура 5 (math-вставка): dê/dt = ω×ê — похідна приклеєного вектора ────────
def fig_rotating_derivative():
    W, H = 820, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30,
                  "Вектор, приклеєний до обертової системи, повертається: dê/dt = ω×ê",
                  size=15, bold=True))
    cx, cy, R = 280, 288, 150
    f.append(circle(cx, cy, R, fill="#f2f6fc", stroke="#c9d6ea", sw=1.6))
    # ω із площини (⊙) у центрі
    f.append(circle(cx, cy, 13, fill=BG, stroke=MUTED, sw=2))
    f.append(circle(cx, cy, 3.2, fill=MUTED, stroke=MUTED, sw=1))
    f.append(text(cx - 24, cy + 4, "ω", size=15, bold=True, italic=True, color=MUTED, anchor="end"))
    f.append(text(cx - 24, cy + 22, "(з площини)", size=10.5, color=MUTED, anchor="end"))

    def pt(theta_deg, rr):                  # math-кут (y вгору) → екран
        th = math.radians(theta_deg)
        return cx + rr * math.cos(th), cy - rr * math.sin(th)

    th0, th1 = 30, 52                       # оберт CCW = ω на нас
    ex, ey = pt(th0, R)
    e1x, e1y = pt(th1, R)
    f.append(arrow(cx, cy, ex, ey, color=INK, sw=2.6))
    f.append(text(ex + 12, ey + 4, "ê", size=15, bold=True, italic=True, anchor="start"))
    f.append(line(cx, cy, e1x, e1y, color=MUTED, sw=1.8, dash="5,5"))
    f.append(text(e1x - 6, e1y - 12, "ê′", size=14, bold=True, italic=True, color=MUTED, anchor="end"))
    ax0, ay0 = pt(th0, 46)
    ax1, ay1 = pt(th1, 46)
    f.append('<path d="M %.1f %.1f A 46 46 0 0 0 %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (ax0, ay0, ax1, ay1, MUTED))
    dphx, dphy = pt(41, 70)
    f.append(text(dphx, dphy, "dφ = ω·dt", size=11.5, color=MUTED, bold=True))
    f.append(arrow(ex, ey, e1x, e1y, color=FICT, sw=2.6))
    mx, my = (ex + e1x) / 2, (ey + e1y) / 2
    f.append(text(mx + 20, my - 4, "dê", size=13.5, bold=True, italic=True, color=FICT, anchor="start"))
    f.append(text(mx + 20, my + 14, "⟂ ê", size=11, color=FICT, anchor="start"))

    f.append(text(636, 150, "dê/dt = ω × ê", size=19, bold=True))
    bx, _, _ = textbox(636, 268,
                       "За час dt система повертає ê на dφ = ω·dt.\n"
                       "Кінець ê заходить по колу → приріст dê\n"
                       "перпендикулярний до ê, довжиною |ê|·dφ.\n"
                       "Саме це й дає векторний добуток ω×ê.",
                       size=12.5, pad=13, fill="#eef3fb", stroke=FIELD, sw=1.5)
    f.append(bx)
    return render(os.path.join(IMG, "rotating-derivative.svg"), W, H, *f)


# ── Фігура 6 (math-вставка): напрямки вигаданих сил на обертовому диску ───────
def fig_fictitious_force_directions():
    W, H = 820, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30,
                  "Вигляд згори: відцентрова — від осі, коріолісова — впоперек швидкості",
                  size=15, bold=True))
    cx, cy, R = 300, 285, 168
    f.append(circle(cx, cy, R, fill="#f4f7fc", stroke="#c9d6ea", sw=1.6))
    f.append(circle(cx, cy, 13, fill=BG, stroke=MUTED, sw=2))
    f.append(circle(cx, cy, 3.2, fill=MUTED, stroke=MUTED, sw=1))
    f.append(text(cx - 24, cy + 4, "ω", size=15, bold=True, italic=True, color=MUTED, anchor="end"))
    f.append(text(cx - 24, cy + 22, "(з площини)", size=10.5, color=MUTED, anchor="end"))

    def scr(vx, vy):                        # math-вектор → екранний напрямок
        return vx, -vy

    th_p = math.radians(36)
    rp = 132
    Px, Py = cx + rp * math.cos(th_p), cy - rp * math.sin(th_p)
    f.append(arrow(cx, cy, Px, Py, color=INK, sw=1.7))
    rmx, rmy = (cx + Px) / 2, (cy + Py) / 2
    f.append(text(rmx - 4, rmy + 22, "r ( = r⊥ )", size=12, color=INK, anchor="middle"))
    f.append(circle(Px, Py, 5.2, fill="#fef6e7", stroke=INK, sw=2))

    vdir = scr(math.cos(math.radians(200)), math.sin(math.radians(200)))
    vtx, vty = Px + vdir[0] * 82, Py + vdir[1] * 82
    f.append(arrow(Px, Py, vtx, vty, color=MOVE, sw=3))
    f.append(text(vtx - 12, vty + 16, "v", size=14, bold=True, italic=True, color=MOVE, anchor="end"))

    ux, uy = Px - cx, Py - cy
    un = math.hypot(ux, uy)
    ux, uy = ux / un, uy / un
    ctx, cty = Px + ux * 84, Py + uy * 84
    f.append(arrow(Px, Py, ctx, cty, color=FICT, sw=3.2))
    f.append(text(ctx + 10, cty - 6, "відцентрова", size=12, bold=True, color=FICT, anchor="start"))
    f.append(text(ctx + 10, cty + 12, "+m·ω²·r", size=11.5, color=FICT, anchor="start"))

    cd = scr(math.sin(math.radians(200)), -math.cos(math.radians(200)))   # (vy,−vx)
    cn = math.hypot(cd[0], cd[1])
    cdx, cdy = cd[0] / cn, cd[1] / cn
    kx, ky = Px + cdx * 78, Py + cdy * 78
    f.append(arrow(Px, Py, kx, ky, color=FICT, sw=3.2))
    f.append(text(kx, ky - 14, "коріолісова", size=12, bold=True, color=FICT, anchor="middle"))
    f.append(text(kx, ky - 30, "−2m·ω×v", size=11.5, color=FICT, anchor="middle"))

    bx, _, _ = textbox(W / 2, 466,
                       "Відцентрова — від осі назовні, залежить лише від положення.\n"
                       "Коріолісова — перпендикулярна до швидкості, лише збиває вбік.",
                       size=12, pad=11, fill=FILL, stroke=LINE, sw=1.4)
    f.append(bx)
    return render(os.path.join(IMG, "fictitious-force-directions.svg"), W, H, *f)


# ── Фігура 7 (proj-вставка): пряма ↔ спіраль — та сама подія у двох системах ──
def fig_carousel_trajectory():
    W, H = 900, 520
    omega, v, T, scale = math.pi / 2, 1.0, 4.0, 30.0
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30,
                  "Та сама шайба у двох системах: пряма ліворуч, спіраль праворуч",
                  size=15.5, bold=True))
    f.append(line(452, 58, 452, 436, color="#dfe4ea", sw=1.3, dash="4,6"))

    def omega_arc(cx, cy, r):
        sx, sy = cx - 56, cy - (r + 10)
        ex, ey = cx + 56, cy - (r + 10)
        out = ('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
               'stroke="%s" stroke-width="2.1" marker-end="url(#arrow)"/>'
               % (sx, sy, r + 22, r + 22, ex, ey, MUTED))
        out += text(cx + 72, cy - r - 6, "ω", size=15, bold=True, italic=True, color=MUTED, anchor="start")
        return out

    def poly(mapped, color, sw, dash=None):
        d = "M %.1f %.1f " % mapped[0] + " ".join("L %.1f %.1f" % p for p in mapped[1:])
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, color, sw, da)

    checks = [1, 2, 3, 4]

    # ── ЛІВОРУЧ: інерціальна — пряма ──
    cxL, cyL = 226, 252
    f.append(text(226, 66, "З нерухомої землі (інерціальна)", size=13.5, bold=True))
    f.append(circle(cxL, cyL, 2 * scale, fill="#eef3fb", stroke=MOVE, sw=1.7))
    f.append(circle(cxL, cyL, 4, fill=INK, stroke=INK, sw=1))
    f.append(omega_arc(cxL, cyL, 2 * scale))
    f.append(arrow(cxL, cyL, cxL + 4.5 * scale, cyL, color=INK, sw=2.6))
    for t in checks:
        px = cxL + t * scale
        f.append(circle(px, cyL, 4.2, fill="#fef6e7", stroke=INK, sw=2))
        f.append(text(px, cyL - 13, "t=%d" % t, size=10.5, color=INK))
    f.append(text(cxL + 4.5 * scale + 4, cyL + 17, "пряма", size=11.5, bold=True, color=INK, anchor="start"))
    f.append(text(cxL, cyL + 2 * scale + 18, "край диска (r = 2 м)", size=10.5, color=MUTED))

    # ── ПРАВОРУЧ: обертова — спіраль ──
    cxR, cyR = 652, 252
    f.append(text(652, 66, "З самої каруселі (обертова)", size=13.5, bold=True))
    f.append(circle(cxR, cyR, 2 * scale, fill="#fbeeee", stroke=FICT, sw=1.7))
    f.append(circle(cxR, cyR, 4, fill=INK, stroke=INK, sw=1))
    f.append(omega_arc(cxR, cyR, 2 * scale))
    n = 240
    spir = []
    for i in range(n + 1):
        t = T * i / n
        xr = v * t * math.cos(omega * t)
        yr = -v * t * math.sin(omega * t)
        spir.append((cxR + xr * scale, cyR - yr * scale))
    f.append(poly(spir, INK, 3))
    lbl = {1: (12, 18, "start"), 2: (-9, -12, "end"), 3: (10, -8, "start"), 4: (7, 18, "start")}
    for t in checks:
        xr = v * t * math.cos(omega * t)
        yr = -v * t * math.sin(omega * t)
        px, py = cxR + xr * scale, cyR - yr * scale
        f.append(circle(px, py, 4.2, fill="#fef6e7", stroke=INK, sw=2))
        dx, dy, an = lbl[t]
        f.append(text(px + dx, py + dy, "t=%d" % t, size=10.5, color=INK, anchor=an))

    bL, _, _ = textbox(226, 476,
                       "X = v·t,   Y = 0\nна шайбу не діє нічого → чесна пряма",
                       size=11.5, pad=10, fill="#eafaf1", stroke=FIELD, sw=1.4)
    f.append(bL)
    bR, _, _ = textbox(652, 476,
                       "x′ = v·t·cos ωt,   y′ = −v·t·sin ωt\nта сама пряма в обертових осях → спіраль",
                       size=11.5, pad=10, fill="#fdecea", stroke=FICT, sw=1.4)
    f.append(bR)
    return render(os.path.join(IMG, "carousel-trajectory.svg"), W, H, *f)


# ── Фігура 8 (proj-вставка): пастка дискретизації — Ойлер надуває знос ────────
def fig_euler_drift():
    W, H = 820, 580
    omega, v, T = math.pi / 2, 1.0, 4.0
    cx, cy, scale = 440, 312, 22.0
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30,
                  "Пастка дискретизації: явний Ойлер надуває фальшивий «відцентровий» знос",
                  size=15, bold=True))

    def accel(x, y, vx, vy):
        return omega * omega * x + 2 * omega * vy, omega * omega * y - 2 * omega * vx

    def exact():
        pts = []
        m = 300
        for i in range(m + 1):
            t = T * i / m
            pts.append((v * t * math.cos(omega * t), -v * t * math.sin(omega * t)))
        return pts

    def euler(dt):
        x, y, vx, vy = 0.0, 0.0, v, 0.0
        pts = [(x, y)]
        for _ in range(int(round(T / dt))):
            ax, ay = accel(x, y, vx, vy)
            x += vx * dt; y += vy * dt
            vx += ax * dt; vy += ay * dt
            pts.append((x, y))
        return pts

    def rk4(dt):
        s = (0.0, 0.0, v, 0.0)
        pts = [(0.0, 0.0)]

        def d(s):
            x, y, vx, vy = s
            ax, ay = accel(x, y, vx, vy)
            return (vx, vy, ax, ay)

        for _ in range(int(round(T / dt))):
            k1 = d(s)
            k2 = d(tuple(si + 0.5 * dt * ki for si, ki in zip(s, k1)))
            k3 = d(tuple(si + 0.5 * dt * ki for si, ki in zip(s, k2)))
            k4 = d(tuple(si + dt * ki for si, ki in zip(s, k3)))
            s = tuple(si + dt / 6 * (a + 2 * b + 2 * c + e) for si, a, b, c, e in zip(s, k1, k2, k3, k4))
            pts.append((s[0], s[1]))
        return pts

    def mp(pts):
        return [(cx + x * scale, cy - y * scale) for (x, y) in pts]

    def poly(mapped, color, sw, dash=None):
        dd = "M %.1f %.1f " % mapped[0] + " ".join("L %.1f %.1f" % p for p in mapped[1:])
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (dd, color, sw, da)

    f.append(circle(cx, cy, 4 * scale, fill="none", stroke="#c9d6ea", sw=1.2))
    f.append(circle(cx, cy, 2 * scale, fill="#f6f8fb", stroke="#c9d6ea", sw=1.4))
    f.append(text(cx + 4 * scale + 6, cy - 4, "r = 4 (точна ціль)", size=10.5, color=MUTED, anchor="start"))
    f.append(circle(cx, cy, 3.5, fill=INK, stroke=INK, sw=1))

    f.append(poly(mp(exact()), INK, 3))
    f.append(poly(mp(euler(0.1)), FICT, 2.6))
    f.append(poly(mp(rk4(0.1)), FIELD, 2.4, dash="6,5"))

    ex_end = exact()[-1]
    eu_end = euler(0.1)[-1]
    pex = (cx + ex_end[0] * scale, cy - ex_end[1] * scale)
    peu = (cx + eu_end[0] * scale, cy - eu_end[1] * scale)
    f.append(circle(pex[0], pex[1], 5, fill="#fef6e7", stroke=INK, sw=2))
    f.append(circle(peu[0], peu[1], 5, fill="#fdecea", stroke=FICT, sw=2))
    f.append(text(peu[0] + 9, peu[1] + 4, "r ≈ 6.4  (замість 4)", size=11, bold=True, color=FICT, anchor="start"))

    lx, ly = 92, 96
    f.append(line(lx, ly, lx + 30, ly, color=INK, sw=3))
    f.append(text(lx + 38, ly + 4, "точна спіраль (r → 4)", size=11.5, anchor="start"))
    f.append(line(lx, ly + 23, lx + 30, ly + 23, color=FICT, sw=2.6))
    f.append(text(lx + 38, ly + 27, "явний Ойлер, dt = 0.1", size=11.5, color=FICT, anchor="start"))
    f.append(line(lx, ly + 46, lx + 30, ly + 46, color=FIELD, sw=2.4, dash="6,5"))
    f.append(text(lx + 38, ly + 50, "RK4, dt = 0.1 (лягає на точну)", size=11.5, color=FIELD, anchor="start"))

    bx, _, _ = textbox(W / 2, 544,
                       "Нестійкий член +ω²·r розганяє похибку явного Ойлера — за оберт шайбу «відносить» на 60 % далі.\n"
                       "Ліки: дрібніший крок або RK4; надійніше — рахувати в інерціальній системі (пряма!) і повернути.",
                       size=11.5, pad=11, fill=FILL, stroke=LINE, sw=1.4)
    f.append(bx)
    return render(os.path.join(IMG, "euler-drift.svg"), W, H, *f)


if __name__ == "__main__":
    p1 = fig_galilean_frames()
    p2 = fig_inertial_vs_braking()
    p3 = fig_rotating_frame()
    p4 = fig_inertia_timeline()
    p5 = fig_rotating_derivative()
    p6 = fig_fictitious_force_directions()
    p7 = fig_carousel_trajectory()
    p8 = fig_euler_drift()
    print("written:")
    for p in (p1, p2, p3, p4, p5, p6, p7, p8):
        print("  ", p)
