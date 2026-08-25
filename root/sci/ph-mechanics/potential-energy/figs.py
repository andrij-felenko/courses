# -*- coding: utf-8 -*-
"""Фігури до теми «Потенціальна енергія».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

PE    = "#27ae60"   # потенціальна енергія / краєвид — зелене
FORCE = "#c0392b"   # сила / рух — гаряче червоне
COL   = "#2457d6"   # допоміжне холодне (відлік, розмір)


def _ball(cx, cy, r=9, col=FORCE):
    return circle(cx, cy, r, fill="#fdecea", stroke=col, sw=2.2)


# ── Фігура 1: сила = −dU/dx; долина стійка, вершина нестійка ────────────────────
def fig_force_slope():
    W, H = 920, 566
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Сила — це схил потенціальної енергії: F = − dU/dx", size=16, bold=True))
    f.append(text(W / 2, 51, "тіло котиться туди, де U менша; крутіший схил дає більшу силу", size=12.5, color=MUTED))

    def U(xd):
        return -1.00 * math.exp(-((xd - 0.0) / 0.72) ** 2) + 1.30 * math.exp(-((xd - 1.75) / 0.62) ** 2)

    xd0, xd1 = -1.7, 3.35
    xL, xR = 108, 812
    yb, ytop = 456, 130
    Umin, Umax = -1.08, 1.40

    def sx(xd):
        return xL + (xR - xL) * (xd - xd0) / (xd1 - xd0)

    def sy(u):
        return yb - (yb - ytop) * (u - Umin) / (Umax - Umin)

    def slope(xd):
        d = 0.01
        return (U(xd + d) - U(xd - d)) / (2 * d)

    # осі
    yaxis = sy(0)  # рівень U = 0
    f.append(line(xL, yb + 22, xR + 18, yb + 22, color=LINE, sw=1.6))
    f.append(text(xR + 14, yb + 42, "положення x", size=12, color=INK, anchor="end"))
    f.append(line(xL - 18, yb + 6, xL - 18, ytop - 6, color=LINE, sw=1.6))
    f.append(text(xL - 14, ytop + 2, "U", size=13, color=INK, anchor="start", italic=True))
    f.append(text(xL - 14, ytop + 18, "потенц.", size=10.5, color=MUTED, anchor="start"))

    # крива U(x)
    pts = []
    xd = xd0
    while xd <= xd1 + 1e-9:
        pts.append("%.1f,%.1f" % (sx(xd), sy(U(xd))))
        xd += 0.02
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (" ".join(pts), PE))

    # знайти долину (мінімум) і вершину (максимум)
    gx = [xd0 + i * 0.005 for i in range(int((xd1 - xd0) / 0.005) + 1)]
    valley = min((x for x in gx if -1.0 < x < 0.9), key=U)
    hill = max((x for x in gx if 0.9 < x < 2.6), key=U)

    # м'яч у долині (стійка)
    vx, vy = sx(valley), sy(U(valley))
    f.append(_ball(vx, vy - 9, 9, PE))
    f.append(line(vx, vy + 6, vx, sy(Umin) + 20, color="#cfd6df", sw=1, dash="3,5"))
    f.append(text(vx, sy(Umin) + 40, "стійка рівновага", size=12, bold=True, color=PE))
    f.append(text(vx, sy(Umin) + 57, "(мінімум U)", size=11, color=MUTED))

    # м'яч на вершині (нестійка)
    hx, hy = sx(hill), sy(U(hill))
    f.append(_ball(hx, hy - 9, 9, FORCE))
    f.append(text(hx, hy - 26, "нестійка", size=12, bold=True, color=FORCE))
    f.append(text(hx, hy - 11, "(максимум U)", size=10.5, color=MUTED))
    # маленькі стрілки-розбіг обабіч вершини
    f.append(arrow(hx - 8, hy - 4, hx - 30, hy + 2, color=FORCE, sw=1.8))
    f.append(arrow(hx + 8, hy - 4, hx + 30, hy + 2, color=FORCE, sw=1.8))

    # горизонтальні стрілки сили в кількох точках (F = −нахил)
    for xd, lab in [(-1.15, None), (0.72, None), (2.45, None)]:
        s = slope(xd)
        if abs(s) < 0.05:
            continue
        px, py = sx(xd), sy(U(xd))
        f.append(_ball(px, py - 9, 6.5, COL))
        direction = -1 if s > 0 else 1
        L = min(60, 26 + abs(s) * 26)
        f.append(arrow(px, py - 9, px + direction * L, py - 9, color=FORCE, sw=3.0))
    f.append(text(sx(0.72) + 4, sy(U(0.72)) - 30, "F", size=14, bold=True, italic=True, color=FORCE, anchor="start"))
    f.append(text(sx(-1.15), sy(U(-1.15)) - 30, "сила → до меншого U", size=11, color=FORCE))

    # дотична-нахил у точці на правому спуску вершини
    tx = 2.15
    ty = U(tx)
    m = slope(tx)
    x1d, x2d = tx - 0.42, tx + 0.42
    f.append(line(sx(x1d), sy(ty + m * (x1d - tx)), sx(x2d), sy(ty + m * (x2d - tx)),
                  color=INK, sw=1.8, dash="6,4"))
    f.append(text(sx(tx) + 30, sy(ty) - 6, "нахил dU/dx", size=11, color=INK, anchor="start"))

    # формула-рамка (у порожньому полі над долиною, осторонь від осі)
    b, bw, bh = textbox(388, 152, ["F = − dU/dx", "сила = мінус крутість схилу"],
                        size=13, pad=11, fill="#eef7f0", stroke=PE, sw=1.5, color=INK, bold=True)
    f.append(b)

    cap, cw, ch = textbox(W / 2, 540,
                          ["Задай одну функцію — потенціальну енергію від положення — і всі сили випливуть із неї як ухил місцевості з мапи висот.",
                           "Природа зсуває тіло до нижчого U: у долині (мінімумі) воно застигає стійко, на вершині (максимумі) тікає від поштовху."],
                          size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(cap)
    return render(os.path.join(IMG, "force-slope.svg"), W, H, *f)


# ── спіральна пружина між стіною й тілом ───────────────────────────────────────
def _spring(x0, x1, y, coils=7, amp=13):
    n = coils
    seg = (x1 - x0) / (n + 1.0)
    pts = ["%.1f,%.1f" % (x0, y)]
    pts.append("%.1f,%.1f" % (x0 + seg * 0.5, y))
    for i in range(n):
        xa = x0 + seg * (i + 0.5)
        pts.append("%.1f,%.1f" % (xa + seg * 0.25, y - amp))
        pts.append("%.1f,%.1f" % (xa + seg * 0.75, y + amp))
    pts.append("%.1f,%.1f" % (x1 - seg * 0.5, y))
    pts.append("%.1f,%.1f" % (x1, y))
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), INK)


def _wall(x, y, h):
    s = [line(x, y - h, x, y + h, color=INK, sw=2.6)]
    for yy in range(int(y - h), int(y + h), 9):
        s.append(line(x, yy, x - 9, yy + 9, color=MUTED, sw=1.2))
    return "".join(s)


# ── Фігура 2: пружна енергія ½kx² — симетрична долина ──────────────────────────
def fig_spring_well():
    W, H = 900, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Пружна енергія U = ½·k·x² — симетрична параболічна долина", size=16, bold=True))
    f.append(text(W / 2, 51, "стиск і розтяг на однакове x запасають однаково; сила F = −k·x завжди тягне до дна", size=12.5, color=MUTED))

    xc = 450                 # екранний центр = x = 0 (вільна довжина)
    xspan = 150              # px на одиницю зсуву (для верхніх пружин)
    wall_x = 150
    sy_row = 118             # ряд пружин

    # три стани пружини
    states = [(-0.75, "стиск  (−x)", +1), (0.0, "вільна  (x = 0)", 0), (0.75, "розтяг  (+x)", -1)]
    block_w = 30
    for xd, lab, fdir in states:
        bx = xc + xd * 100
        f.append(_wall(wall_x, sy_row, 26))
        f.append(_spring(wall_x, bx - block_w / 2, sy_row))
        f.append(rect(bx - block_w / 2, sy_row - 18, block_w, 36, fill="#eef7f0", stroke=PE, sw=1.8, rx=3))
        if fdir != 0:
            f.append(arrow(bx, sy_row + 30, bx + fdir * 34, sy_row + 30, color=FORCE, sw=2.6))
            f.append(text(bx + fdir * 17, sy_row + 52, "F", size=12, bold=True, italic=True, color=FORCE))
        f.append(text(bx, sy_row - 28, lab, size=11.5, color=INK))

    # ── парабола U = ½kx² ──
    xL, xR = 150, 770
    yb, ytop = 448, 214
    k = 1.0
    xdmax = 1.25
    Umax = 0.5 * k * xdmax ** 2

    def px(xd):
        return xc + (xR - xL) / 2.0 * (xd / xdmax) * 0.94

    def py(u):
        return yb - (yb - ytop) * (u / Umax)

    # осі
    f.append(line(xL, yb, xR, yb, color=LINE, sw=1.6))
    f.append(text(xc, yb + 34, "зсув x  (стиск ← 0 → розтяг)", size=12, color=INK, anchor="middle"))
    f.append(line(xc, yb + 6, xc, ytop - 8, color=LINE, sw=1.4))
    f.append(text(xc + 6, ytop + 2, "U", size=13, italic=True, color=INK, anchor="start"))

    pts = []
    xd = -xdmax
    while xd <= xdmax + 1e-9:
        pts.append("%.1f,%.1f" % (px(xd), py(0.5 * k * xd ** 2)))
        xd += 0.02
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (" ".join(pts), PE))

    # симетрична пара ±a — однакова U
    a = 0.95
    ua = 0.5 * k * a ** 2
    for sign in (-1, 1):
        xx, yy = px(sign * a), py(ua)
        f.append(line(xx, yy, xx, yb, color="#cfd6df", sw=1, dash="3,5"))
        f.append(line(xc, yy, xx, yy, color="#cfd6df", sw=1, dash="3,5"))
        f.append(_ball(xx, yy, 7, PE))
        f.append(text(xx, yb + 20, ("−a" if sign < 0 else "+a"), size=12, bold=True, color=INK))
        # повертальна стрілка сили — до центру
        f.append(arrow(xx, yy - 16, xc + sign * 26, yy - 16, color=FORCE, sw=2.2))
    f.append(text(xc, py(ua) - 12, "однакова U для +a і −a", size=11.5, color=PE))
    f.append(text(px(0), yb - 6, "дно: рівновага x=0", size=11, color=MUTED))

    # рамка формул
    b, bw, bh = textbox(W / 2, 524,
                        ["Закон Гука F = −k·x росте лінійно зі зсувом → потенціальна енергія U = ½·k·x² росте квадратично.",
                         "Парабола симетрична: запас однаковий у будь-який бік, а повертальна сила = нахил, тож завжди тягне до дна."],
                        size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "spring-well.svg"), W, H, *f)


# ── Фігура 3: запас mgh лінійний + довільний нуль ──────────────────────────────
def fig_store_reference():
    W, H = 920, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Запас тяжіння U = m·g·h росте прямо з висотою, а нуль обирають довільно",
                  size=15.5, bold=True))
    f.append(line(462, 62, 462, 486, color="#dfe4ea", sw=1.2, dash="4,6"))

    # ── ЛІВОРУЧ: сходинки висоти, лінійний запас ──
    f.append(text(230, 88, "Підняти — укласти запас", size=13.5, bold=True, color=PE))
    gy = 430
    f.append(line(70, gy, 430, gy, color=INK, sw=2))
    for hx in range(84, 430, 22):
        f.append(line(hx, gy, hx - 8, gy + 9, color=MUTED, sw=1))
    step = 96
    heights = [(1, "h", "mgh"), (2, "2h", "2mgh"), (3, "3h", "3mgh")]
    colx = [120, 230, 340]
    barx = 392
    for (mult, hlab, ulab), cxp in zip(heights, colx):
        my = gy - mult * step
        # стовпчик підйому (пунктир від землі)
        f.append(line(cxp, gy, cxp, my, color="#cfd6df", sw=1.2, dash="3,5"))
        # тіло
        f.append(rect(cxp - 15, my - 14, 30, 20, fill="#eef7f0", stroke=PE, sw=1.8, rx=3))
        f.append(text(cxp, my - 20, hlab, size=11.5, bold=True, color=INK))
        # бар запасу праворуч, висота ∝ mult (лінійно)
        bh = mult * step * 0.9
        f.append(rect(barx, gy - bh, 20, bh, fill="#e7f6ee", stroke=PE, sw=1.6, rx=3))
    f.append(text(barx + 10, gy - 3 * step * 0.9 - 12, "U ∝ h", size=12, bold=True, color=PE))
    f.append(text(230, gy + 34, "удвічі вище → удвічі більший запас (лінійно, не як v²)",
                  size=11.5, color=INK))

    # ── ПРАВОРУЧ: довільний нуль, та сама ΔU ──
    f.append(text(690, 88, "Нуль висоти — довільний", size=13.5, bold=True, color=COL))
    mx = 690
    y_top = 150      # верхнє положення тіла
    y_bot = 250      # після спуску на Δh
    y_table = 300    # рівень столу (один вибір нуля)
    y_floor = 420    # рівень підлоги (інший вибір нуля)

    # два рівні відліку
    for yy, lab, off in [(y_table, "нуль: стіл", 0), (y_floor, "нуль: підлога", 0)]:
        f.append(line(560, yy, 850, yy, color=COL, sw=1.4, dash="6,4"))
        f.append(text(846, yy - 6, lab, size=11, color=COL, anchor="end"))

    # тіло вгорі та після спуску Δh
    f.append(rect(mx - 15, y_top - 14, 30, 20, fill="#fdecea", stroke=FORCE, sw=1.8, rx=3))
    f.append(rect(mx - 15, y_bot - 14, 30, 20, fill="#f7e9e7", stroke=FORCE, sw=1.4, rx=3))
    f.append(arrow(mx + 36, y_top, mx + 36, y_bot, color=FORCE, sw=2.4))
    f.append(text(mx + 52, (y_top + y_bot) / 2 + 4, "Δh", size=12.5, bold=True, color=FORCE, anchor="start"))

    # висоти до двох нулів (різні) — ліворуч від тіла
    f.append(line(600, y_bot, 600, y_table, color=COL, sw=1.2))
    f.append(line(596, y_bot, 604, y_bot, color=COL, sw=1.2))
    f.append(line(596, y_table, 604, y_table, color=COL, sw=1.2))
    f.append(text(588, (y_bot + y_table) / 2 + 4, "h₁", size=11, color=COL, anchor="end"))
    f.append(line(576, y_bot, 576, y_floor, color=COL, sw=1.2))
    f.append(line(572, y_bot, 580, y_bot, color=COL, sw=1.2))
    f.append(line(572, y_floor, 580, y_floor, color=COL, sw=1.2))
    f.append(text(566, (y_bot + y_floor) / 2 + 4, "h₂", size=11, color=COL, anchor="end"))

    f.append(text(690, 470, "U різна (h₁ ≠ h₂), але ΔU = m·g·Δh — та сама", size=11.5, bold=True, color=INK))

    cap, cw, ch = textbox(W / 2, 516,
                          ["Абсолютне значення U залежить від обраного нуля й саме собою нічого не означає — фізично проявляється лише різниця ΔU.",
                           "Для того самого спуску Δh вона однакова за будь-якого відліку, тож нуль ставлять там, де зручно рахувати."],
                          size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(cap)
    return render(os.path.join(IMG, "store-reference.svg"), W, H, *f)


# ── Фігура 4: незалежність від шляху ⟺ нульова циркуляція (консервативність) ────
def fig_path_independence():
    W, H = 900, 502
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Робота консервативної сили залежить лише від кінців — не від шляху",
                  size=15.5, bold=True))
    f.append(text(W / 2, 51, "тому по будь-якому замкненому контурі циркуляція нульова, а локально rot F = 0",
                  size=12.5, color=MUTED))

    A = (215, 205)
    B = (600, 300)
    # дві стежки A→B (квадратичні криві Безьє), що разом складають замкнений контур
    f.append('<path d="M%.0f,%.0f Q%.0f,%.0f %.0f,%.0f" fill="none" stroke="%s" stroke-width="3"/>'
             % (A[0], A[1], 430, 120, B[0], B[1], PE))
    f.append('<path d="M%.0f,%.0f Q%.0f,%.0f %.0f,%.0f" fill="none" stroke="%s" stroke-width="3"/>'
             % (A[0], A[1], 415, 378, B[0], B[1], COL))
    # напрямні стрілки посередині кожної стежки (обидві A→B)
    f.append(arrow(391.6, 179.5, 446.9, 193.0, color=PE, sw=2.4))
    f.append(arrow(384.0, 307.0, 439.4, 320.5, color=COL, sw=2.4))
    # точки A і B
    f.append(circle(A[0], A[1], 8, fill="#fdecea", stroke=INK, sw=2))
    f.append(circle(B[0], B[1], 8, fill="#eaf0fd", stroke=INK, sw=2))
    f.append(text(A[0] - 14, A[1] - 12, "A · U вище", size=12.5, bold=True, anchor="end"))
    f.append(text(B[0] + 14, B[1] + 20, "B · U нижче", size=12.5, bold=True, anchor="start"))
    f.append(text(330, 112, "шлях 1", size=12, color=PE, bold=True))
    f.append(text(322, 402, "шлях 2", size=12, color=COL, bold=True))
    f.append(text(470, 245, "W₁ = W₂ = U(A) − U(B)", size=13, bold=True, color=INK, anchor="start"))

    # значок циркуляції (замкнений контур) праворуч
    f.append(circle(742, 200, 30, fill="none", stroke=FORCE, sw=2.2))
    f.append(arrow(726, 170, 760, 170, color=FORCE, sw=2.0))
    f.append(text(742, 148, "замкнений контур", size=11, color=MUTED))
    f.append(text(742, 258, "∮ F·dr = 0", size=13, bold=True, color=FORCE))

    cap, cw, ch = textbox(W / 2, 470,
                          ["Замкни контур (туди шляхом 1, назад шляхом 2) — повна робота W₁ − W₂ = 0: саме тому кожній точці можна приписати ОДНЕ число U.",
                           "Це і є умова консервативності; у диференціальній формі — rot F = 0, тобто нульова циркуляція по нескінченно малому контурі."],
                          size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(cap)
    return render(os.path.join(IMG, "path-independence.svg"), W, H, *f)


# ── Фігура 5: F = −∇U — градієнт перпендикулярний до еквіпотенціалей ────────────
def fig_gradient_contours():
    W, H = 900, 548
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "У 3D сила — мінус градієнт: F = −∇U", size=16, bold=True))
    f.append(text(W / 2, 51, "градієнт перпендикулярний до ліній рівного U і дивиться туди, де U росте найшвидше",
                  size=12.5, color=MUTED))

    C = (340, 300)
    Rs = [55, 105, 155, 205]
    for R in Rs:
        f.append(circle(C[0], C[1], R, fill="none", stroke=PE, sw=1.8))
    # центр — мінімум
    f.append(circle(C[0], C[1], 3.5, fill=PE, stroke=PE, sw=1))
    f.append(line(C[0] - 8, C[1], C[0] - 92, C[1], color="#cfd6df", sw=1))
    f.append(text(C[0] - 96, C[1] + 4, "мінімум U", size=11.5, bold=True, color=PE, anchor="end"))
    f.append(text(150, 118, "внутрішні кільця — нижче U, зовнішні — вище", size=11.5, color=MUTED, anchor="start"))

    # інструментована точка P на кільці R=155, кут ~32° вгору-праворуч
    P = (471.4, 217.9)   # C + 155·(cos32°, −sin32°)
    # ∇U — назовні (до більшого U), зелений
    f.append(arrow(P[0], P[1], 522.3, 186.1, color=PE, sw=2.6))
    f.append(text(560, 176, "∇U", size=13.5, bold=True, italic=True, color=PE, anchor="middle"))
    f.append(text(560, 193, "до крутішого U", size=10.5, color=MUTED))
    # F = −∇U — усередину (до меншого U), червоний
    f.append(arrow(P[0], P[1], 420.5, 249.7, color=FORCE, sw=2.8))
    f.append(text(392, 268, "F = −∇U", size=13, bold=True, italic=True, color=FORCE, anchor="middle"))
    # дотична до еквіпотенціалі (перпендикулярна градієнтові)
    f.append(line(440.7, 168.7, 502.1, 267.1, color=INK, sw=1.6, dash="6,4"))
    f.append(text(516, 292, "дотична (U = const)", size=10.5, color=INK, anchor="start"))
    f.append(circle(P[0], P[1], 4.5, fill="#fdecea", stroke=INK, sw=1.8))

    # ще одна сила-стрілка (потік до мінімуму) вгорі-ліворуч
    f.append(arrow(154.3, 228.3, 192.4, 246.1, color=FORCE, sw=2.2))
    f.append(text(150, 222, "F", size=12, bold=True, italic=True, color=FORCE, anchor="end"))

    cap, cw, ch = textbox(W / 2, 500,
                          ["Уздовж лінії рівного U зміна dU = ∇U·dr = 0 → ∇U перпендикулярний до еквіпотенціалей і вказує напрям найшвидшого зростання U.",
                           "Сила F = −∇U тягне поперек цих ліній, до нижчого U; її величина дорівнює крутості найшвидшого спуску краєвиду."],
                          size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(cap)
    return render(os.path.join(IMG, "gradient-contours.svg"), W, H, *f)


# ── Фігура 6: класифікація рівноваги за U'' і параболічне наближення ────────────
def fig_curvature_test():
    W, H = 940, 572
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Форма долини задає силу: класифікація рівноваги за U''", size=16, bold=True))
    f.append(text(W / 2, 51, "біля мінімуму U ≈ ½·U''·Δx² — парабола, з якої народжуються малі коливання",
                  size=12.5, color=MUTED))

    x0, x1 = -3.4, 3.6
    N = 700
    xs = [x0 + (x1 - x0) * i / N for i in range(N + 1)]
    kk = -0.5

    def Up(x):
        return kk * (x + 2.0) * (x - 0.2) * (x - 2.5) ** 2   # U'(x)

    def Upp(x, e=1e-3):
        return (Up(x + e) - Up(x - e)) / (2 * e)             # U''(x)

    Us = [0.0]
    for i in range(1, len(xs)):
        Us.append(Us[-1] + 0.5 * (Up(xs[i]) + Up(xs[i - 1])) * (xs[i] - xs[i - 1]))
    Umn, Umx = min(Us), max(Us)

    xL, xR = 92, 690
    yb, ytop = 470, 118

    def sx(x):
        return xL + (xR - xL) * (x - x0) / (x1 - x0)

    def sy(u):
        return yb - (yb - ytop) * (u - Umn) / (Umx - Umn)

    def Uval(xq):
        if xq <= xs[0]:
            return Us[0]
        for i in range(1, len(xs)):
            if xs[i] >= xq:
                t = (xq - xs[i - 1]) / (xs[i] - xs[i - 1])
                return Us[i - 1] + t * (Us[i] - Us[i - 1])
        return Us[-1]

    # осі
    f.append(line(xL, yb + 16, xR + 16, yb + 16, color=LINE, sw=1.6))
    f.append(text(xR + 12, yb + 40, "положення x", size=12, color=INK, anchor="end"))
    f.append(line(xL - 18, yb + 2, xL - 18, ytop - 6, color=LINE, sw=1.6))
    f.append(text(xL - 22, ytop + 2, "U", size=13, italic=True, color=INK, anchor="end"))

    # крива U(x)
    pts = ["%.1f,%.1f" % (sx(x), sy(u)) for x, u in zip(xs, Us)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (" ".join(pts), PE))

    xmin, xmax, xinf = -2.0, 0.2, 2.5

    # осцилювальна парабола біля мінімуму
    kmin = Upp(xmin)
    par = []
    xp = xmin - 0.95
    while xp <= xmin + 0.95 + 1e-9:
        u = Uval(xmin) + 0.5 * kmin * (xp - xmin) ** 2
        if u <= Umx:
            par.append("%.1f,%.1f" % (sx(xp), sy(u)))
        xp += 0.03
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.9" stroke-dasharray="7,4"/>'
             % (" ".join(par), INK))

    # маркери трьох критичних точок
    mn = (sx(xmin), sy(Uval(xmin)))
    mx = (sx(xmax), sy(Uval(xmax)))
    inf = (sx(xinf), sy(Uval(xinf)))
    f.append(_ball(mn[0], mn[1], 8, PE))
    f.append(_ball(mx[0], mx[1], 8, FORCE))
    f.append(_ball(inf[0], inf[1], 8, COL))
    f.append(text(mn[0], mn[1] + 26, "мінімум · U'' > 0", size=11.5, bold=True, color=PE))
    f.append(text(mn[0], mn[1] + 48, "парабола ½·U''·Δx²", size=11, color=INK))
    f.append(text(mx[0], mx[1] - 24, "максимум · U'' < 0", size=11.5, bold=True, color=FORCE))
    f.append(text(inf[0] + 10, inf[1] - 8, "перегин · U'' = 0", size=11.5, bold=True, color=COL, anchor="start"))

    cap, cw, ch = textbox(W / 2, 546,
                          ["Розклад Тейлора біля рівноваги (U' = 0): U ≈ U₀ + ½·U''·Δx² — знак U'' вирішує форму долини.",
                           "Угнута (U''>0) тримає: F = −U''·Δx, звідси ω = √(U''/m); опукла (U''<0) відпускає; у 3D — матриця Гессе, сідло змішане."],
                          size=11.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(cap)
    return render(os.path.join(IMG, "curvature-test.svg"), W, H, *f)


# ── Фігура (історія): дві нитки назви сходяться в «потенціальній енергії» ───────
def fig_naming_threads():
    W, H = 1000, 600
    AMBER = "#b9770e"
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Дві нитки, що сходяться в назві «потенціальна енергія»", size=16.5, bold=True))
    f.append(text(W / 2, 54, "слово «потенціальна» — від математики поля; слово «енергія» — від Аристотеля через фізику руху",
                  size=12, color=MUTED))

    bw, bh = 200, 58
    col = [150, 400, 650]
    yT, yB = 128, 330
    cyT, cyB = yT + bh / 2, yB + bh / 2

    f.append(text(54, 112, "Нитка МАТЕМАТИКИ — «потенціальна функція»", size=12.5, bold=True, color=PE, anchor="start"))
    f.append(text(54, 314, "Нитка ЕНЕРГІЇ — актуальне / потенційне Аристотеля", size=12.5, bold=True, color=COL, anchor="start"))

    topnodes = ["Лаґранж · 1773\nфункція тяжіння, без імені",
                "Ґрін · 1828\n«потенціальна функція»",
                "Ґаусс 1840 · Томсон 1845\nусталення назви"]
    botnodes = ["Аристотель · ~350 до н.е.\ndynamis / energeia",
                "Ляйбніц · vis viva\n«жива сила» ~ m·v²",
                "Юнґ · 1807\nслово «energy»"]
    for s, cx in zip(topnodes, col):
        f.append(fitbox(cx - bw / 2, yT, bw, bh, s, size=12.5, pad=7, fill="#eef7f0", stroke=PE, sw=1.6, color=INK))
    for s, cx in zip(botnodes, col):
        f.append(fitbox(cx - bw / 2, yB, bw, bh, s, size=12.5, pad=7, fill="#eaf0fb", stroke=COL, sw=1.6, color=INK))

    for i in (0, 1):
        f.append(arrow(col[i] + bw / 2 + 4, cyT, col[i + 1] - bw / 2 - 4, cyT, color=PE, sw=2.0))
        f.append(arrow(col[i] + bw / 2 + 4, cyB, col[i + 1] - bw / 2 - 4, cyB, color=COL, sw=2.0))

    cvx, cvy = 880, 258
    cb, cvw, cvh = textbox(cvx, cvy, ["Ренкін · 1853", "ПОТЕНЦІАЛЬНА ЕНЕРГІЯ", "= енергія конфігурації"],
                           size=13, pad=10, fill="#fdf3e0", stroke=AMBER, sw=2.2, color=INK, bold=True)
    f.append(cb)
    f.append(arrow(col[2] + bw / 2 + 4, cyT + 6, cvx - cvw / 2 - 4, cvy - 18, color=PE, sw=2.2))
    f.append(arrow(col[2] + bw / 2 + 4, cyB - 6, cvx - cvw / 2 - 4, cvy + 18, color=COL, sw=2.2))

    ky = 462
    kb, kw2, kh2 = textbox(cvx, ky, ["Томсон і Тет · 1867", "«актуальна» → «кінетична»"],
                           size=12.5, pad=9, fill=FILL, stroke=LINE, sw=1.5, color=INK)
    f.append(kb)
    f.append(arrow(cvx, cvy + cvh / 2 + 3, cvx, ky - kh2 / 2 - 3, color=MUTED, sw=2.0))

    cap, _, _ = textbox(W / 2, 560,
                        ["Обидві нитки тяглися нарізно: математики будували безіменну функцію поля, а «енергію» вивищив Юнґ із аристотелівської пари.",
                         "1853-го Ренкін звів їх в одну назву; 1867-го Томсон і Тет замінили Ренкінову «актуальну» на «кінетичну» — так терміни й застигли."],
                        size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(cap)
    return render(os.path.join(IMG, "naming-threads.svg"), W, H, *f)


# ══════ Фігури до вставки proj «Краєвид потенціалу під мікроскопом коду» ══════
# подвійна яма U = ¼x⁴ − ½x²  (мінімуми ±1 стійкі, максимум 0 нестійкий)
def _Upl(x):  return 0.25 * x ** 4 - 0.5 * x ** 2
def _dUpl(x): return x ** 3 - x
def _Epl(x, v): return 0.5 * v * v + _Upl(x)


def _run(kind, x, v, h, steps):
    out = [(0.0, x, v, _Epl(x, v))]
    a = -_dUpl(x)
    for i in range(steps):
        if kind == "euler":
            a = -_dUpl(x); xn = x + h * v; vn = v + h * a; x, v = xn, vn
        elif kind == "symp":
            a = -_dUpl(x); v = v + h * a; x = x + h * v
        else:  # velocity Verlet
            vh = v + 0.5 * h * a; x = x + h * vh; a = -_dUpl(x); v = vh + 0.5 * h * a
        if abs(x) > 1e3 or abs(v) > 1e3:
            break
        out.append(((i + 1) * h, x, v, _Epl(x, v)))
    return out


def _poly(pts, col, sw=3.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%s"%s/>' % (
        " ".join("%.1f,%.1f" % p for p in pts), col, sw, d)


# ── proj-Фігура 1: краєвид подвійної ями з рівновагами й рівнями енергії ────────
def fig_pl_landscape():
    W, H = 940, 640
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Краєвид подвійної ями U(x) = ¼·x⁴ − ½·x² — дві долини й хребет", size=16, bold=True))
    f.append(text(W / 2, 51, "рівноваги = корені U′; стійкість = знак U″; рівень енергії каже, замкнене тіло чи перелітає",
                  size=12.5, color=MUTED))

    xd0, xd1 = -1.72, 1.72
    xL, xR = 120, 720
    yb, ytop = 470, 108
    Umin, Umax = -0.34, 0.80

    def sx(xd): return xL + (xR - xL) * (xd - xd0) / (xd1 - xd0)
    def sy(u):  return yb - (yb - ytop) * (u - Umin) / (Umax - Umin)

    # осі
    f.append(line(xL - 16, sy(0), xR + 150, sy(0), color="#c8ced6", sw=1.1, dash="4,6"))  # U = 0
    f.append(line(xL - 16, yb + 20, xR + 20, yb + 20, color=LINE, sw=1.6))
    f.append(text(xR + 16, yb + 40, "положення x", size=12, color=INK, anchor="end"))
    f.append(line(xL - 16, yb + 6, xL - 16, ytop - 6, color=LINE, sw=1.6))
    f.append(text(xL - 12, ytop + 2, "U", size=13, italic=True, color=INK, anchor="start"))
    f.append(text(xL - 12, ytop + 18, "потенц.", size=10, color=MUTED, anchor="start"))

    # крива
    pts = []
    xd = xd0
    while xd <= xd1 + 1e-9:
        pts.append((sx(xd), sy(_Upl(xd)))); xd += 0.015
    f.append(_poly(pts, PE, 3.2))

    # рівні енергії
    E1, E2 = -0.131, 0.15
    f.append(line(sx(xd0), sy(E1), sx(xd1) + 8, sy(E1), color=COL, sw=1.8, dash="7,5"))
    f.append(text(sx(xd1) + 14, sy(E1) + 4, "E = −0.13", size=12, bold=True, color=COL, anchor="start"))
    f.append(text(sx(xd1) + 14, sy(E1) + 20, "замкнено в", size=10.5, color=COL, anchor="start"))
    f.append(text(sx(xd1) + 14, sy(E1) + 34, "одній ямі", size=10.5, color=COL, anchor="start"))
    f.append(line(sx(xd0), sy(E2), sx(xd1) + 8, sy(E2), color=FORCE, sw=1.8, dash="7,5"))
    f.append(text(sx(xd1) + 14, sy(E2) + 4, "E = +0.15", size=12, bold=True, color=FORCE, anchor="start"))
    f.append(text(sx(xd1) + 14, sy(E2) + 20, "перелітає", size=10.5, color=FORCE, anchor="start"))
    f.append(text(sx(xd1) + 14, sy(E2) + 34, "бар'єр", size=10.5, color=FORCE, anchor="start"))

    # висота бар'єра ΔU між дном ями (−¼) і хребтом (0)
    xbar = -0.42
    f.append(line(sx(xbar), sy(-0.25), sx(xbar), sy(0.0), color=INK, sw=1.4))
    f.append(line(sx(xbar) - 4, sy(-0.25), sx(xbar) + 4, sy(-0.25), color=INK, sw=1.4))
    f.append(line(sx(xbar) - 4, sy(0.0), sx(xbar) + 4, sy(0.0), color=INK, sw=1.4))
    f.append(text(sx(xbar) - 8, sy(0.0) - 8, "бар'єр ΔU = ¼", size=11, color=INK, anchor="end"))

    # рівноваги
    for xe, col, lab, sub, up in [(-1.0, PE, "стійка", "(мінімум)", False),
                                  (1.0, PE, "стійка", "(мінімум)", False),
                                  (0.0, FORCE, "нестійка", "(максимум)", True)]:
        ex, ey = sx(xe), sy(_Upl(xe))
        f.append(_ball(ex, ey, 8, col))
        if up:
            f.append(text(ex, ey - 20, lab, size=12, bold=True, color=col))
            f.append(text(ex, ey - 6, sub, size=10.5, color=MUTED))
            f.append(arrow(ex - 9, ey + 6, ex - 30, ey + 14, color=FORCE, sw=1.7))
            f.append(arrow(ex + 9, ey + 6, ex + 30, ey + 14, color=FORCE, sw=1.7))
        else:
            f.append(text(ex, yb + 40, lab, size=12, bold=True, color=col))
            f.append(text(ex, yb + 56, sub, size=10.5, color=MUTED))
            f.append(line(ex, ey + 8, ex, yb + 26, color="#cfd6df", sw=1, dash="3,5"))
            f.append(text(ex + 13, ey + 22, ("x=−1" if xe < 0 else "x=+1"), size=10.5, color=INK, anchor="start"))

    cap, cw, ch = textbox(W / 2, 590,
                          ["Одна функція U(x) задає весь краєвид: корені U′ дають три рівноваги (±1 і 0),",
                           "а знак U″ їх сортує — дно долин стійке, маківка хребта хиткa.",
                           "Рівень повної енергії вирішує долю руху: нижчий за бар'єр (E=−0.13) —",
                           "тіло гойдається в одній ямі; вищий (E=+0.15) — перелітає між обома."],
                          size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(cap)
    return render(os.path.join(IMG, "pl-landscape.svg"), W, H, *f)


# ── proj-Фігура 2: дрейф енергії E(t) — Ейлер vs симплектичні ───────────────────
def fig_pl_drift():
    W, H = 940, 548
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Дрейф енергії E(t): прямий Ейлер повзе вгору, симплектичні тримаються", size=16, bold=True))
    f.append(text(W / 2, 51, "та сама задача (x₀=1.3, v₀=0, h=0.02) трьома інтеграторами", size=12.5, color=MUTED))

    t0, t1 = 0.0, 32.0
    Elo, Ehi = -0.16, 0.03
    xL, xR = 96, 720
    yb, ytop = 470, 104

    def sx(t): return xL + (xR - xL) * (t - t0) / (t1 - t0)
    def sy(e): return yb - (yb - ytop) * (e - Elo) / (Ehi - Elo)

    # осі
    f.append(line(xL - 8, yb, xR + 20, yb, color=LINE, sw=1.6))
    f.append(text(xR + 16, yb + 20, "час t", size=12, color=INK, anchor="end"))
    f.append(line(xL - 8, yb + 6, xL - 8, ytop - 6, color=LINE, sw=1.6))
    f.append(text(xL - 4, ytop - 2, "повна енергія E", size=12, italic=True, color=INK, anchor="start"))
    for tt in range(0, 31, 5):
        f.append(line(sx(tt), yb, sx(tt), yb + 5, color=LINE, sw=1.2))
        f.append(text(sx(tt), yb + 20, str(tt), size=10.5, color=MUTED))

    # бар'єр E = 0
    f.append(line(xL, sy(0), xR + 8, sy(0), color=MUTED, sw=1.4, dash="6,5"))
    f.append(text(xR + 12, sy(0) + 4, "бар'єр E = 0", size=11.5, bold=True, color=MUTED, anchor="start"))
    # старт E₀
    f.append(line(xL, sy(-0.131), xR, sy(-0.131), color="#dfe4ea", sw=1.0, dash="2,6"))
    f.append(text(xL + 6, sy(-0.131) - 6, "E₀ = −0.131", size=10.5, color=MUTED, anchor="start"))

    steps = 1600
    eu = _run("euler", 1.3, 0.0, 0.02, steps)
    ve = _run("verlet", 1.3, 0.0, 0.02, steps)
    se = _run("symp", 1.3, 0.0, 0.02, steps)

    def clip(run):
        p = []
        for t, x, v, e in run:
            if t > t1 or e > Ehi or e < Elo:
                break
            p.append((sx(t), sy(e)))
        return p

    f.append(_poly(clip(se), PE, 2.4))          # напівнеявний Ейлер (зелена)
    f.append(_poly(clip(ve), COL, 2.6))         # Верле (синя)
    f.append(_poly(clip(eu), FORCE, 3.0))       # прямий Ейлер (червона)

    # підписи кривих
    f.append(text(sx(24), sy(-0.028), "прямий Ейлер", size=12.5, bold=True, color=FORCE, anchor="end"))
    f.append(text(sx(24), sy(-0.011), "×(1+ω²h²) щокроку", size=10.5, color=FORCE, anchor="end"))
    f.append(text(sx(30) + 6, sy(-0.131) + 24, "Верле  (смуга ≈ 3·10⁻⁵)", size=11.5, bold=True, color=COL, anchor="end"))
    f.append(text(sx(30) + 6, sy(-0.131) + 40, "симпл. Ейлер (смуга ≈ 4·10⁻³)", size=11, color=PE, anchor="end"))
    # позначка перетину бар'єра
    for t, x, v, e in eu:
        if e > 0:
            f.append(_ball(sx(t), sy(0), 5.5, FORCE))
            f.append(text(sx(t) - 6, sy(0) - 10, "t≈29.5: хибна втеча", size=10.5, bold=True, color=FORCE, anchor="end"))
            break

    cap, cw, ch = textbox(W / 2, 522,
                          ["Прямий Ейлер множить енергію на (1+ω²h²)>1 щокроку — вона неухильно росте, аж поки тіло хибно не перескочить бар'єр (E>0).",
                           "Симплектичні Верле й напівнеявний Ейлер бережуть тіньовий гамільтоніан: похибка енергії лишається в тонкій обмеженій смузі без дрейфу."],
                          size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(cap)
    return render(os.path.join(IMG, "pl-drift.svg"), W, H, *f)


# ── proj-Фігура 3: фазовий портрет (x, v) — петля Верле vs спіраль Ейлера ───────
def fig_pl_phase():
    W, H = 920, 636
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Фазовий портрет (x, v): збереження енергії = замкнена орбіта", size=16, bold=True))
    f.append(text(W / 2, 51, "Верле держить петлю навколо дна ями; Ейлер розкручується назовні й тікає за бар'єр",
                  size=12.5, color=MUTED))

    xa, xb = -0.18, 1.85
    va, vb = -1.08, 1.08
    xL, xR = 110, 700
    yb, ytop = 500, 106

    def sx(x): return xL + (xR - xL) * (x - xa) / (xb - xa)
    def sy(v): return yb - (yb - ytop) * (v - va) / (vb - va)

    # осі
    f.append(line(sx(xa), sy(0), sx(xb) + 14, sy(0), color=LINE, sw=1.5))
    f.append(text(sx(xb) + 10, sy(0) + 20, "положення x", size=12, color=INK, anchor="end"))
    f.append(line(sx(0), sy(va) + 8, sx(0), sy(vb) - 4, color=LINE, sw=1.4))
    f.append(text(sx(0) - 8, ytop - 2, "швидкість v", size=12, italic=True, color=INK, anchor="end"))

    # бар'єр x = 0 (вершина)
    f.append(line(sx(0), sy(va) + 8, sx(0), sy(vb) - 4, color=FORCE, sw=1.2, dash="5,5"))
    f.append(text(sx(0) + 6, sy(vb) - 6, "бар'єр x=0 (вершина)", size=11, color=FORCE, anchor="start"))

    # спіраль Ейлера — до виходу з рамки
    eu = _run("euler", 1.3, 0.0, 0.02, 4000)
    pe = []
    for t, x, v, e in eu:
        if x < xa or x > xb or v < va or v > vb:
            break
        pe.append((sx(x), sy(v)))
    f.append(_poly(pe, FORCE, 2.0))
    if len(pe) >= 2:
        ax, ay = pe[-1]; bx, by = pe[-2]
        f.append(arrow(bx, by, ax, ay, color=FORCE, sw=2.2))

    # петля Верле — один оберт
    ve = _run("verlet", 1.3, 0.0, 0.02, 300)
    pv = [(sx(x), sy(v)) for t, x, v, e in ve]
    f.append(_poly(pv, COL, 2.8))
    # стрілка обертання на петлі
    if len(pv) > 40:
        ax, ay = pv[40]; bx, by = pv[38]
        f.append(arrow(bx, by, ax, ay, color=COL, sw=2.4))

    # дно ями (стійка рівновага) (1, 0)
    f.append(_ball(sx(1.0), sy(0.0), 6.5, PE))
    f.append(text(sx(1.0), sy(0.0) + 24, "дно ями (стійка)", size=11.5, bold=True, color=PE))

    # підписи кривих
    f.append(text(sx(1.0), sy(0.62), "Верле — замкнена орбіта", size=12, bold=True, color=COL))
    f.append(text(sx(0.62), sy(-0.86), "Ейлер — спіраль назовні (E росте)", size=12, bold=True, color=FORCE, anchor="start"))

    cap, cw, ch = textbox(W / 2, 590,
                          ["Замкнена орбіта у фазовій площині — це і є збереження енергії:",
                           "тіло вертається в ту саму точку з тією самою швидкістю щоперіоду.",
                           "Симплектичний Верле її держить. Прямий Ейлер малює спіраль, що росте,",
                           "— видимий підпис числового підкачування енергії, аж до втечі за бар'єр."],
                          size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(cap)
    return render(os.path.join(IMG, "pl-phase.svg"), W, H, *f)


if __name__ == "__main__":
    fig_force_slope()
    fig_spring_well()
    fig_store_reference()
    fig_path_independence()
    fig_gradient_contours()
    fig_curvature_test()
    fig_naming_threads()
    fig_pl_landscape()
    fig_pl_drift()
    fig_pl_phase()
    print("OK: фігури у", IMG)
