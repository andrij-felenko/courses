# -*- coding: utf-8 -*-
"""Фігури до теми «Механічна робота».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED  = "#c0392b"    # сила / рух — гаряче
GRN  = "#1f7a3d"    # поздовжня складова, «+»
BLU  = "#2457d6"    # поперечна складова, нейтральне
REDL = "#fdecea"
GRNL = "#e7f6ee"
BLUL = "#eaf0fd"


# ── Фігура 1: W = F·d·cosθ — розклад сили на поздовжню й поперечну ─────────────
def fig_work_angle():
    W, H = 920, 486
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Роботу виконує лише складова сили вздовж руху:  W = F·d·cosθ",
                  size=16, bold=True))

    Ox, Oy = 235, 300
    ground_y = Oy
    # земля
    f.append(line(95, ground_y, 840, ground_y, color=LINE, sw=2))
    for hx in range(110, 300, 22):
        f.append(line(hx, ground_y, hx - 8, ground_y + 9, color=MUTED, sw=1))
    # ящик
    f.append(rect(150, Oy - 40, 86, 40, fill="#eef1f4", stroke=LINE, sw=1.6, rx=4))
    f.append(text(193, Oy - 16, "ящик", size=12, color=MUTED))

    # сила під кутом
    th = math.radians(32)
    FL = 250.0
    Fx = Ox + FL * math.cos(th)
    Fy = Oy - FL * math.sin(th)
    projx = Ox + FL * math.cos(th)          # кінець проєкції на землю
    # поздовжня складова (зелена, вздовж землі — трохи вище лінії)
    f.append(arrow(Ox, Oy, projx, Oy, color=GRN, sw=3.4))
    # поперечна складова (синій пунктир угору)
    f.append(line(projx, Oy, projx, Fy, color=BLU, sw=2.4, dash="6,4"))
    # сама сила (червона)
    f.append(arrow(Ox, Oy, Fx, Fy, color=RED, sw=3.4))
    f.append(text(Fx + 10, Fy - 6, "F", size=17, bold=True, italic=True, color=RED, anchor="start"))

    # прямий кут біля кінця проєкції
    f.append('<path d="M %.1f %.1f h -13 v -13" fill="none" stroke="%s" stroke-width="1.5"/>'
             % (projx, Oy, MUTED))
    # дуга кута θ
    f.append('<path d="M %.1f %.1f A 48 48 0 0 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.7"/>'
             % (Ox + 48, Oy, Ox + 48 * math.cos(th), Oy - 48 * math.sin(th), MUTED))
    f.append(text(Ox + 66, Oy - 16, "θ", size=15, italic=True, color=MUTED))

    # підписи складових
    f.append(text((Ox + projx) / 2, Oy - 12, "F∥ = F·cosθ", size=13.5, bold=True, color=GRN))
    f.append(text(projx + 12, (Oy + Fy) / 2 - 4, "F⊥ = F·sinθ", size=13, bold=True, color=BLU, anchor="start"))
    f.append(text(projx + 12, (Oy + Fy) / 2 + 15, "роботи не виконує", size=11.5, color=MUTED, anchor="start"))

    # переміщення d — під землею
    dy = Oy + 30
    f.append(arrow(Ox, dy, Ox + 330, dy, color=INK, sw=2.4))
    f.append(line(Ox, Oy + 6, Ox, dy + 8, color=MUTED, sw=1, dash="3,4"))
    f.append(line(Ox + 330, Oy + 6, Ox + 330, dy + 8, color=MUTED, sw=1, dash="3,4"))
    f.append(text(Ox + 165, dy + 22, "d — переміщення", size=13, color=INK))

    b, bw, bh = textbox(W / 2, 430,
                        ["Силу F розкладено на поздовжню F·cosθ (вздовж руху) і поперечну F·sinθ (упоперек).",
                         "Роботу творить лише поздовжня частина, тому W = F·d·cosθ = F∥·d."],
                        size=12.5, pad=12, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "work-angle.svg"), W, H, *f)


# ── Фігура 2: знак роботи — три випадки ────────────────────────────────────────
def _sign_panel(f, cx, accent, accent_l, sign, ang_txt, w_txt, effect,
                force_kind, example_lines):
    """Одна картка: тіло + рух + сила + бейдж знака + підписи."""
    top, ch = 80, 314
    f.append(rect(cx - 138, top, 276, ch, fill="#ffffff", stroke=LINE, sw=1.3, rx=8))

    gy = 240                      # рівень землі в картці
    f.append(line(cx - 96, gy, cx + 96, gy, color=LINE, sw=1.8))
    # тіло
    f.append(circle(cx - 6, gy - 15, 15, fill=accent_l, stroke=accent, sw=2.0))

    # рух v — горизонтальна стрілка вправо
    f.append(arrow(cx - 74, gy - 66, cx + 40, gy - 66, color=INK, sw=2.0))
    f.append(text(cx - 17, gy - 74, "рух  v", size=12, color=INK))

    # сила
    bx, by = cx - 6, gy - 15
    if force_kind == "fwd":          # уперед-угору (θ<90)
        tx, ty = bx + 60, by - 46
        f.append(arrow(bx, by, tx, ty, color=accent, sw=3.2))
        f.append(text(tx + 8, ty - 2, "F", size=15, bold=True, italic=True, color=accent, anchor="start"))
    elif force_kind == "perp":       # прямо вгору (θ=90)
        tx, ty = bx, by - 74
        f.append(arrow(bx, by, tx, ty, color=accent, sw=3.2))
        f.append(text(tx + 10, ty + 14, "F", size=15, bold=True, italic=True, color=accent, anchor="start"))
        f.append('<path d="M %.1f %.1f h 13 v 13" fill="none" stroke="%s" stroke-width="1.4"/>'
                 % (bx, by - 30, MUTED))
    else:                            # назад (θ>90)
        tx, ty = bx - 66, by
        f.append(arrow(bx, by, tx, ty, color=accent, sw=3.2))
        f.append(text(tx - 8, ty - 8, "F", size=15, bold=True, italic=True, color=accent, anchor="end"))

    # бейдж знака праворуч угорі картки
    bxc, byc = cx + 104, top + 34
    if sign == "+":
        f.append(plus(bxc, byc, 15))
    elif sign == "−":
        f.append(minus(bxc, byc, 15))
    else:
        f.append(circle(bxc, byc, 15, fill="#eef1f4", stroke=MUTED, sw=2))
        f.append(text(bxc, byc + 6, "0", size=17, bold=True, color=MUTED))

    # підписи під землею
    f.append(text(cx, gy + 30, ang_txt, size=13, color=INK))
    f.append(text(cx, gy + 52, w_txt, size=15, bold=True, color=accent))
    f.append(text(cx, gy + 72, effect, size=12.5, color=INK))
    f.append(mtext(cx, gy + 96, example_lines, size=11, color=MUTED, lh=1.35))


def fig_work_signs():
    W, H = 980, 492
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Знак роботи вирішує кут між силою і рухом",
                  size=16, bold=True))

    _sign_panel(f, 200, GRN, GRNL, "+", "кут < 90°", "W > 0", "розганяє тіло",
                "fwd", ["штовхаєш візок", "уперед"])
    _sign_panel(f, 490, BLU, BLUL, "0", "кут = 90°", "W = 0", "швидкість стала",
                "perp", ["натяг на мотузці,", "тяжіння на орбіті,", "нормальна реакція"])
    _sign_panel(f, 780, RED, REDL, "−", "кут > 90°", "W < 0", "гальмує тіло",
                "back", ["тертя, гальмо,", "опір повітря"])

    b, bw, bh = textbox(W / 2, 458,
                        ["Сила вперед закачує енергію в тіло (W>0), сила чисто вбік не змінює нічого (W=0),",
                         "сила назад витягує енергію (W<0). Косинус кута несе цей знак."],
                        size=12.5, pad=12, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "work-signs.svg"), W, H, *f)


# ── Фігура 3: робота як площа під графіком F(x) ────────────────────────────────
def _axes(f, ox, oy, xlen, ylen):
    f.append(arrow(ox, oy, ox + xlen, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ylen, color=LINE, sw=1.8))
    f.append(text(ox - 8, oy - ylen + 2, "сила F", size=12, color=INK, anchor="end"))
    f.append(text(ox + xlen - 4, oy + 38, "переміщення", size=12, color=INK, anchor="end"))


def fig_variable_force_area():
    W, H = 960, 476
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Робота — це площа під графіком сили F(x)",
                  size=16, bold=True))
    f.append(line(W / 2, 66, W / 2, 400, color="#dfe4ea", sw=1.2, dash="4,6"))

    # ── ЛІВОРУЧ: стала сила → прямокутник ──
    f.append(text(268, 92, "Стала сила", size=14, bold=True, color=INK))
    o1x, o1y = 120, 372
    _axes(f, o1x, o1y, 340, 262)
    Fy = o1y - 172           # рівень сталої сили
    dx = o1x + 268           # кінець шляху d
    f.append(rect(o1x, Fy, dx - o1x, o1y - Fy, fill=REDL, stroke=RED, sw=1.8, rx=0))
    f.append(line(o1x, Fy, dx, Fy, color=RED, sw=2.6))
    # позначки осей
    f.append(line(o1x - 5, Fy, o1x + 5, Fy, color=INK, sw=1.4))
    f.append(text(o1x - 12, Fy + 5, "F", size=13, italic=True, color=INK, anchor="end"))
    f.append(line(dx, o1y - 5, dx, o1y + 5, color=INK, sw=1.4))
    f.append(text(dx, o1y + 20, "d", size=13, italic=True, color=INK))
    f.append(text((o1x + dx) / 2, (Fy + o1y) / 2 + 6, "W = F·d", size=16, bold=True, color=RED))

    # ── ПРАВОРУЧ: пружина F = k·x → трикутник ──
    f.append(text(738, 92, "Пружина:  F = k·x", size=14, bold=True, color=INK))
    o2x, o2y = 560, 372
    _axes(f, o2x, o2y, 340, 262)
    xend = o2x + 300         # видовження x
    ytop = o2y - 210         # k·x на кінці
    # трикутник під прямою
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="none"/>'
             % (o2x, o2y, xend, o2y, xend, ytop, REDL))
    f.append(line(o2x, o2y, xend, ytop, color=RED, sw=2.8))          # F = k·x
    # висота k·x (пунктир)
    f.append(line(xend, o2y, xend, ytop, color=BLU, sw=1.8, dash="5,4"))
    f.append(text(xend + 10, (o2y + ytop) / 2, "k·x", size=13, bold=True, color=BLU, anchor="start"))
    # основа x
    f.append(line(xend, o2y - 5, xend, o2y + 5, color=INK, sw=1.4))
    f.append(text(xend, o2y + 20, "x", size=13, italic=True, color=INK))
    f.append(text(o2x + 165, o2y - 58, "W = ½·k·x²", size=16, bold=True, color=RED))

    b, bw, bh = textbox(W / 2, 442,
                        ["Стала сила замітає прямокутник F·d; сила пружини росте прямою F = k·x і замітає трикутник ½·k·x².",
                         "Хоч якою була б крива сили, робота — це площа під нею."],
                        size=12.5, pad=12, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "variable-force-area.svg"), W, H, *f)


# ── Фігура 4: незалежність роботи тяжіння від шляху (для вставки math) ─────────
def fig_path_independence():
    W, H = 980, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Робота тяжіння задана лише перепадом висоти Δh — не дорогою",
                  size=16, bold=True))

    # координати точок A (низько, ліворуч) і B (високо, праворуч)
    Ax, Ay = 210, 430
    Bx, By = 760, 190

    # вертикальна вісь висоти ліворуч
    axx = 108
    f.append(arrow(axx, 470, axx, 120, color=LINE, sw=1.8))
    f.append(text(axx - 8, 130, "висота", size=12.5, color=INK, anchor="end"))

    # рівнопотенціальні прямі (горизонталі U = const) крізь A і B
    for (yy, lab, who) in [(Ay, "U_A", "A"), (By, "U_B = U_A + m·g·Δh", "B")]:
        f.append(line(axx, yy, 880, yy, color="#c7ccd2", sw=1.2, dash="6,6"))
    f.append(text(884, Ay + 4, "U_A", size=12.5, color=MUTED, anchor="start"))
    f.append(text(884, By + 4, "U_B", size=12.5, color=MUTED, anchor="start"))

    # дужка Δh на осі
    f.append(line(axx, Ay, axx - 14, Ay, color=MUTED, sw=1.2))
    f.append(line(axx, By, axx - 14, By, color=MUTED, sw=1.2))
    f.append(arrow(axx - 30, Ay, axx - 30, By, color=INK, sw=1.6))
    f.append(arrow(axx - 30, By, axx - 30, Ay, color=INK, sw=1.6))
    f.append(text(axx - 40, (Ay + By) / 2 + 4, "Δh", size=14, bold=True, color=INK, anchor="end"))

    # стрілка тяжіння (у відкритій смузі вгорі)
    f.append(arrow(505, 108, 505, 166, color=MUTED, sw=2.4))
    f.append(text(518, 148, "m·g", size=13, italic=True, color=MUTED, anchor="start"))

    # ── три шляхи A → B (окремі смуги: дуга зверху, пряма посередині, сходи знизу) ──
    # 1) пряма (червоний)
    f.append(arrow(Ax, Ay, Bx, By, color=RED, sw=3.0))

    # 2) сходинками (синій) — сидять під діагоналлю
    steps = [(Ax, Ay)]
    nx = 5
    for i in range(nx):
        x0, y0 = steps[-1]
        steps.append((x0 + (Bx - Ax) / nx, y0))                  # горизонталь
        steps.append((x0 + (Bx - Ax) / nx, y0 - (Ay - By) / nx))  # вертикаль
    for i in range(len(steps) - 1):
        x1, y1 = steps[i]; x2, y2 = steps[i + 1]
        f.append(line(x1, y1, x2, y2, color=BLU, sw=2.6))

    # 3) дугою (зелений) — вигинається вгору над діагоналлю
    cx, cy = 470, 150
    f.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="3.0" marker-end="url(#arrow)"/>' % (Ax, Ay, cx, cy, Bx, By, GRN))

    # легенда у відкритій верхній лівій смузі (над усіма шляхами)
    lx, ly = 205, 132
    f.append(rect(lx, ly, 196, 96, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    for i, (col, lab) in enumerate([(RED, "пряма"), (BLU, "сходинками"), (GRN, "дугою")]):
        ry = ly + 24 + i * 26
        f.append(line(lx + 16, ry, lx + 48, ry, color=col, sw=3.2))
        f.append(text(lx + 60, ry + 5, lab, size=13, bold=True, color=col, anchor="start"))

    # точки A і B
    for (px, py, lab, dx) in [(Ax, Ay, "A", -20), (Bx, By, "B", 14)]:
        f.append(circle(px, py, 7, fill="#ffffff", stroke=INK, sw=2.2))
        f.append(text(px + dx, py + 5, lab, size=15, bold=True, color=INK))

    b, bw, bh = textbox(W / 2, 512,
                        ["Горизонтальні кроки коштують нуль (сила тяжіння ⊥ рухові), тож у роботу входить лише вертикаль.",
                         "Усі три шляхи дають те саме:  W = ∫F·dr = −m·g·Δh.  Робота залежить від кінців, не від дороги."],
                        size=12.5, pad=12, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "path-independence.svg"), W, H, *f)


# ── Фігура 5: замкнений обхід — консервативна (∮=0) проти тертя (∮<0) ───────────
def _loop_rect(f, Ax, Ay, side_h, side_w, badges, dir_note):
    """Прямокутний контур A→B→C→D→A зі стрілками обходу; badges = 4 функції-бейджі
    у порядку [ліве ребро, верх, праве ребро, низ]. Кожен badge(cx,cy)."""
    Bx, By = Ax, Ay - side_h          # верх-ліво
    Cx, Cy = Ax + side_w, Ay - side_h # верх-право
    Dx, Dy = Ax + side_w, Ay          # низ-право
    # ребра як стрілки (напрям обходу)
    f.append(arrow(Ax, Ay, Bx, By, color=INK, sw=2.2))   # ліве вгору
    f.append(arrow(Bx, By, Cx, Cy, color=INK, sw=2.2))   # верх управо
    f.append(arrow(Cx, Cy, Dx, Dy, color=INK, sw=2.2))   # праве вниз
    f.append(arrow(Dx, Dy, Ax, Ay, color=INK, sw=2.2))   # низ уліво
    # бейджі на серединах ребер (винесені назовні)
    badges[0](Ax - 34, (Ay + By) / 2)             # ліве
    badges[1]((Bx + Cx) / 2, By - 30)             # верх
    badges[2](Cx + 34, (Cy + Dy) / 2)             # праве
    badges[3]((Dx + Ax) / 2, Dy + 30)             # низ
    return (Bx, By, Cx, Cy, Dx, Dy)


def fig_conservative_vs_friction():
    W, H = 1000, 576
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Той самий замкнений обхід: консервативна сила проти тертя",
                  size=16, bold=True))

    def zero_badge(cx, cy):
        f.append(circle(cx, cy, 15, fill="#eef1f4", stroke=MUTED, sw=2))
        f.append(text(cx, cy + 6, "0", size=17, bold=True, color=MUTED))

    # ── ЛІВОРУЧ: тяжіння (консервативна) ──
    f.append(text(255, 78, "Тяжіння — консервативна", size=14.5, bold=True, color=INK))
    _loop_rect(f, 175, 400, 190, 200,
               [lambda x, y: (f.append(minus(x, y, 15)),
                              f.append(text(x - 22, y + 40, "−m·g·Δh", size=12, color=NEG, anchor="middle"))),
                lambda x, y: zero_badge(x, y),
                lambda x, y: (f.append(plus(x, y, 15)),
                              f.append(text(x + 24, y + 40, "+m·g·Δh", size=12, color=POS, anchor="middle"))),
                lambda x, y: zero_badge(x, y)],
               None)
    # стрілка тяжіння в центрі
    f.append(arrow(275, 250, 275, 300, color=MUTED, sw=2.2))
    f.append(text(288, 282, "g", size=13, italic=True, color=MUTED, anchor="start"))
    f.append(text(255, 470, "∮ F·dr = −m·g·Δh + m·g·Δh = 0",
                  size=14, bold=True, color=INK))
    f.append(text(255, 492, "підйом коштує рівно стільки, скільки віддає спуск",
                  size=11.5, color=MUTED))

    # роздільник
    f.append(line(W / 2, 66, W / 2, 456, color="#dfe4ea", sw=1.2, dash="4,6"))

    # ── ПРАВОРУЧ: тертя (дисипативна) ──
    f.append(text(745, 78, "Тертя — дисипативна", size=14.5, bold=True, color=INK))
    _loop_rect(f, 665, 400, 190, 200,
               [lambda x, y: f.append(minus(x, y, 15)),
                lambda x, y: f.append(minus(x, y, 15)),
                lambda x, y: f.append(minus(x, y, 15)),
                lambda x, y: f.append(minus(x, y, 15))],
               None)
    f.append(text(765, 305, "сила тертя", size=11.5, color=RED, anchor="middle"))
    f.append(text(765, 322, "завжди проти руху", size=11.5, color=RED, anchor="middle"))
    f.append(text(745, 470, "∮ F·dr = −μ·N·L  < 0",
                  size=14, bold=True, color=INK))
    f.append(text(745, 492, "кожне ребро відбирає, обхід не повертається в нуль",
                  size=11.5, color=MUTED))

    b, bw, bh = textbox(W / 2, 542,
                        ["Консервативна сила: замкнений обхід дає нуль — тому їй можна приписати потенціал U і роботу W = −ΔU.",
                         "Тертя: обхід дає −μ·N·L, що росте з довжиною контуру L, — потенціалу не існує."],
                        size=12.5, pad=12, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "conservative-vs-friction.svg"), W, H, *f)


# ── Фігура (вставка «історія»): дві бухгалтерії однієї сили ────────────────────
def fig_two_ledgers():
    W, H = 980, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Одна сила — два різні рахунки", size=17, bold=True))

    bh = 62
    b1x, b1w = 60, 150          # «Сила F»
    b2x, b2w = 372, 246         # середній бокс
    b3x, b3w = 762, 196         # результат

    def lane(cy, head, hcol, mid_lines, mid_fill, mid_stroke, res_lines, op1):
        p = []
        p.append(text(W / 2, cy - 52, head, size=13.5, bold=True, color=hcol))
        p.append(fitbox(b1x, cy - bh / 2, b1w, bh, "Сила F", size=15, bold=True,
                        fill=FILL, stroke=INK))
        p.append(arrow(b1x + b1w + 6, cy, b2x - 6, cy, color=hcol, sw=2))
        p.append(text((b1x + b1w + b2x) / 2, cy - 12, op1, size=12.5, bold=True, color=hcol))
        p.append(fitbox(b2x, cy - bh / 2, b2w, bh, mid_lines, size=14, bold=True,
                        fill=mid_fill, stroke=mid_stroke))
        p.append(arrow(b2x + b2w + 6, cy, b3x - 6, cy, color=hcol, sw=2))
        p.append(text((b2x + b2w + b3x) / 2, cy - 12, "змінює", size=12, color=MUTED))
        p.append(fitbox(b3x, cy - bh / 2, b3w, bh, res_lines, size=13.5, bold=True,
                        fill=FILL, stroke=hcol))
        return "".join(p)

    f.append(lane(150, "Сила діє протягом ЧАСУ  —  сторона Декарта", BLU,
                  ["Імпульс", "F · Δt"], BLUL, BLU,
                  ["кількість руху", "m · v"], "× час Δt"))
    f.append(lane(322, "Сила діє вздовж ВІДСТАНІ  —  сторона Ляйбніца", GRN,
                  ["Робота", "F · d"], REDL, RED,
                  ["кінетична енергія", "½ · m · v²"], "× відстань d"))

    b, bw, bhh = textbox(W / 2, 442,
                         ["Обидва рахунки правдиві й обидва зберігаються — вони відповідають на різні питання.",
                          "Коріоліс (1829) розвів їх, показавши, що робота дорівнює зміні ½m·v², а не m·v²."],
                         size=12.5, pad=12, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "two-ledgers.svg"), W, H, *f)


# ── Фігура (вставка «історія»): часова лінія народження поняття ────────────────
def fig_work_timeline():
    W, H = 980, 764
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 38, "Народження поняття «робота»: півтора століття", size=17, bold=True))

    axx = 250
    f.append(line(axx, 78, axx, 726, color=LINE, sw=2))

    rows = [
        ("1686",    BLU,   ["Ляйбніц: «жива сила» m·v² —", "початок суперечки з картезіанцями (m·v?)"]),
        ("1722",    BLU,   ["с-Ґравезанде: кулі в глину —", "глибина сліду росте як v²"]),
        ("1783",    MUTED, ["Лазар Карно: «момент активності»", "= сила × відстань (теорія машин)"]),
        ("1782",    MUTED, ["Ватт: кінська сила —", "33 000 фут-фунтів за хвилину"]),
        ("1829",    RED,   ["Коріоліс дає силі-на-відстані ім’я travail", "і множник ½ у величині ½m·v²"]),
        ("1826–36", RED,   ["Понселе несе «механічну роботу»", "в інженерний курс у Меці"]),
        ("~1850",   GRN,   ["Томсон і Ренкін: назва «кінетична енергія»;", "Джоуль: теплота = робота"]),
        ("1882",    GRN,   ["Сіменс: одиницю енергії названо «джоуль»", "(ухвалено 1889;  1 Дж = 1 Н·м)"]),
    ]
    y0, step = 108, 84
    for i, (year, col, lines) in enumerate(rows):
        y = y0 + i * step
        f.append(line(axx, y, axx + 28, y, color=col, sw=2))
        f.append(circle(axx, y, 7, fill=col, stroke=INK, sw=1.5))
        f.append(text(axx - 20, y + 5, year, size=14, bold=True, color=INK, anchor="end"))
        f.append(fitbox(axx + 34, y - 28, 662, 56, lines, size=13,
                        fill=FILL, stroke=col, sw=1.4))
    return render(os.path.join(IMG, "work-timeline.svg"), W, H, *f)


# ── Фігура (proj): трапеції на дискретному лозі (x,F) — оцінка й похибка ────────
def fig_trapz_log():
    W, H = 840, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Робота з логу давача: площа трапецій під виміряним F(x)",
                  size=16, bold=True))

    ox, oy = 120, 350
    xpx, ypx = 250.0, 11.6
    PX = lambda xm: ox + xm * xpx
    PY = lambda fn: oy - fn * ypx
    xs = [0.0, 0.5, 1.0, 1.5, 2.0]
    Fs = [0.0, 12.0, 20.0, 18.0, 6.0]
    pts = [(PX(x), PY(F)) for x, F in zip(xs, Fs)]

    # осі
    f.append(arrow(ox, oy, PX(2.0) + 56, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, PY(20.0) - 30, color=LINE, sw=1.8))
    f.append(text(ox + 8, PY(20.0) - 34, "сила F, Н", size=12.5, color=INK, anchor="start"))
    f.append(text(PX(2.0) + 52, oy + 22, "x, м", size=12.5, color=INK, anchor="end"))

    # заливка трапецій під хордами
    poly = ("%.1f,%.1f " % (pts[0][0], oy)
            + " ".join("%.1f,%.1f" % p for p in pts)
            + " %.1f,%.1f" % (pts[-1][0], oy))
    f.append('<polygon points="%s" fill="%s" stroke="none" opacity="0.7"/>' % (poly, REDL))

    # вертикальні сторони трапецій + позначки x
    for (px, py), xm in zip(pts, xs):
        f.append(line(px, oy, px, py, color=RED, sw=1.3, dash="4,3"))
        f.append(line(px, oy - 4, px, oy + 4, color=INK, sw=1.4))
        f.append(text(px, oy + 22, ("%g" % xm), size=12, color=INK))

    # хорди (оцінка трапеціями) + дот + значення F
    for a, b in zip(pts, pts[1:]):
        f.append(line(a[0], a[1], b[0], b[1], color=RED, sw=2.6))
    for (px, py), Fn in zip(pts, Fs):
        f.append(circle(px, py, 4.4, fill=RED, stroke="#ffffff", sw=1.5))
        f.append(text(px, py - 13, ("%g Н" % Fn), size=11.5, color=RED, bold=True))

    # справжня неперервна крива (пунктир, вища за хорди — звідси похибка)
    raises = [22, 22, 10, 22]
    path = "M %.1f %.1f" % pts[0]
    for a, b, r in zip(pts, pts[1:], raises):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - r
        path += " Q %.1f %.1f %.1f %.1f" % (mx, my, b[0], b[1])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="8,5"/>'
             % (path, BLU))

    # похибка — стрілка на прогалину між хордою і кривою (сегмент 1→2)
    tx = (pts[1][0] + pts[2][0]) / 2
    ty = (pts[1][1] + pts[2][1]) / 2 - 11
    f.append(text(232, 150, "похибка", size=12.5, color=BLU, bold=True))
    f.append(arrow(268, 154, tx - 6, ty, color=BLU, sw=1.5))

    # легенда (праворуч угорі)
    lx, ly = 610, 118
    f.append(rect(lx, ly, 212, 62, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    f.append(line(lx + 14, ly + 20, lx + 46, ly + 20, color=RED, sw=2.6))
    f.append(text(lx + 54, ly + 24, "трапеції (оцінка)", size=12, color=INK, anchor="start"))
    f.append(line(lx + 14, ly + 44, lx + 46, ly + 44, color=BLU, sw=2.2, dash="8,5"))
    f.append(text(lx + 54, ly + 48, "справжня F(x)", size=12, color=INK, anchor="start"))

    # Δx-дужка під першим сегментом
    by = oy + 40
    f.append(line(pts[0][0], by, pts[1][0], by, color=MUTED, sw=1.3))
    f.append(line(pts[0][0], by - 4, pts[0][0], by + 4, color=MUTED, sw=1.3))
    f.append(line(pts[1][0], by - 4, pts[1][0], by + 4, color=MUTED, sw=1.3))
    f.append(text((pts[0][0] + pts[1][0]) / 2, by + 14, "Δx", size=12, color=MUTED))

    b, bw, bh = textbox(W / 2, 470,
                        ["Кожна трапеція = ½(Fᵢ+Fᵢ₊₁)·Δx; сума трапецій — оцінка роботи ∫F dx.",
                         "Хорда лежить нижче опуклої кривої, тож між ними похибка; дрібніший крок Δx її зменшує."],
                        size=12.5, pad=12, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "trapz-log.svg"), W, H, *f)


# ── Фігура (proj): знак роботи вздовж шляху — F·Δr на кожному плечі ─────────────
def fig_path_sign():
    W, H = 780, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Робота вздовж шляху: добуток F·Δr сам несе знак",
                  size=16, bold=True))

    ox, oy, s = 150, 350, 82.0
    P = lambda xm, ym: (ox + xm * s, oy - ym * s)
    r0, r1, r2, r3 = P(0, 0), P(2, 0), P(2, 2), P(1, 2)
    VIO = "#7b3fbf"

    # координатну сітку прибрано — вузли з підписами (0,0)…(1,2) дають орієнтир,
    # а зайві лінії перетинали б написи

    # плечі шляху (колір = знак роботи на плечі)
    f.append(arrow(r0[0], r0[1], r1[0], r1[1], color=GRN, sw=4.4))
    f.append(arrow(r1[0], r1[1], r2[0], r2[1], color=GRN, sw=4.4))
    f.append(arrow(r2[0], r2[1], r3[0], r3[1], color=RED, sw=4.4))

    # вектори сили F (фіолетові) у вузлах
    f.append(arrow(r0[0], r0[1] - 20, r0[0] + 66, r0[1] - 20, color=VIO, sw=2.4))
    f.append(text(r0[0] + 72, r0[1] - 24, "F₀", size=13, color=VIO, bold=True, italic=True, anchor="start"))
    f.append(arrow(r1[0], r1[1], r1[0] + 42, r1[1] - 42, color=VIO, sw=2.4))
    f.append(text(r1[0] + 46, r1[1] - 46, "F₁", size=13, color=VIO, bold=True, italic=True, anchor="start"))
    f.append(arrow(r2[0], r2[1], r2[0] + 52, r2[1], color=VIO, sw=2.4))
    f.append(text(r2[0] + 58, r2[1] + 4, "F₂", size=13, color=VIO, bold=True, italic=True, anchor="start"))

    # вузли
    for pt in (r0, r1, r2, r3):
        f.append(circle(pt[0], pt[1], 4.6, fill=INK, stroke="#ffffff", sw=1.5))
    f.append(text(r0[0] - 2, r0[1] + 24, "старт (0,0)", size=11.5, color=MUTED))
    f.append(text(r3[0] - 14, r3[1] + 2, "фініш (1,2)", size=11.5, color=MUTED, anchor="end"))

    # бейджі роботи на плечах
    f.append(text((r0[0] + r1[0]) / 2, r0[1] + 26, "F·Δr = +20 Дж", size=13, color=GRN, bold=True))
    f.append(text(r1[0] + 16, (r1[1] + r2[1]) / 2, "+8 Дж", size=13, color=GRN, bold=True, anchor="start"))
    f.append(text((r2[0] + r3[0]) / 2, r2[1] - 14, "−8 Дж", size=13, color=RED, bold=True))

    # підсумок (праворуч)
    sb, sbw, sbh = textbox(600, 150,
                           ["сума плечей:",
                            "+20 + 8 − 8 = 20 Дж",
                            "",
                            "зворотне плече (−8)",
                            "ВІДНІМАЄ енергію"],
                           size=12.5, pad=12, fill="#ffffff", stroke=LINE, sw=1.3)
    f.append(sb)

    b, bw, bh = textbox(W / 2, 436,
                        ["На зворотному плечі рух іде ліворуч (Δr), а сила F₂ дивиться праворуч — добуток F·Δr від'ємний,",
                         "і 8 Дж віднімаються самі, без жодного «if». Сумувати модулі кроків — груба помилка."],
                        size=11.5, pad=12, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "path-sign.svg"), W, H, *f)


if __name__ == "__main__":
    fig_trapz_log()
    fig_path_sign()
    fig_work_angle()
    fig_work_signs()
    fig_variable_force_area()
    fig_path_independence()
    fig_conservative_vs_friction()
    fig_two_ledgers()
    fig_work_timeline()
    print("OK: фігури у", IMG)
