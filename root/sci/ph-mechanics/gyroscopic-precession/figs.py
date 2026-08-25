# -*- coding: utf-8 -*-
"""Фігури до теми «Гіроскопічна прецесія».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

PREC = "#7d3c98"   # колір прецесії (окремий від spin/torque)


def ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5, op=1.0, dash=None, rot=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    tr = ' transform="rotate(%.2f %.1f %.1f)"' % (rot, cx, cy) if rot is not None else ''
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            'fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"%s%s/>'
            % (cx, cy, rx, ry, fill, op, stroke, sw, d, tr))


def arc_arrow(cx, cy, r, a0_deg, a1_deg, color=LINE, sw=2.4, head=10):
    """Дуга-стрілка (коло) від кута a0 до a1 (градуси, 0°=праворуч, проти год.)."""
    a0 = math.radians(a0_deg); a1 = math.radians(a1_deg)
    x0 = cx + r * math.cos(a0); y0 = cy - r * math.sin(a0)
    x1 = cx + r * math.cos(a1); y1 = cy - r * math.sin(a1)
    sweep_ccw = 1 if a1_deg > a0_deg else 0
    sweep = 0 if sweep_ccw else 1
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    path = ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw))
    dir_sign = 1 if sweep_ccw else -1
    tx = -math.sin(a1) * dir_sign
    ty = -math.cos(a1) * dir_sign
    L = math.hypot(tx, ty); tx, ty = tx / L, ty / L
    back = 2.2
    px, py = x1 - tx * head, y1 - ty * head
    nx, ny = -ty, tx
    h = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
         % (x1, y1, px + nx * head / back, py + ny * head / back,
            px - nx * head / back, py - ny * head / back, color))
    return path + h


def out_of_plane(cx, cy, r=15, color=NEG):
    """Символ ⊙ — вектор із площини (до глядача)."""
    return (circle(cx, cy, r, fill="#f2ecf7", stroke=color, sw=2.2)
            + circle(cx, cy, 2.6, fill=color, stroke=color, sw=1))


def right_angle(px, py, u, v, s=11, color=MUTED):
    ax, ay = px + u[0] * s, py + u[1] * s
    bx, by = px + v[0] * s, py + v[1] * s
    cx, cy = ax + v[0] * s, ay + v[1] * s
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="1.2"/>' % (ax, ay, cx, cy, bx, by, color))


# ── Фігура 1: не крутиться — падає; крутиться — прецесує ──────────────────────
def fig_fall_vs_precess():
    W, H = 940, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Та сама сила тяжіння — а поведінка протилежна",
                  size=17, bold=True))
    f.append(line(W / 2, 62, W / 2, H - 70, color="#e3e7ee", sw=1.4))

    # ── ліва панель: не обертається → падає ──
    Px = 240
    piv = (Px, 430)
    f.append(text(Px, 84, "НЕ обертається", size=14, bold=True, color=MUTED))
    # опора
    f.append(line(Px - 60, piv[1], Px + 60, piv[1], color=INK, sw=2.4))
    for xx in range(-48, 49, 16):
        f.append(line(Px + xx, piv[1], Px + xx - 10, piv[1] + 12, color=MUTED, sw=1.2))
    f.append(circle(piv[0], piv[1], 5, fill=INK, stroke=INK, sw=1))
    # похилена вісь (початкова) + центр мас
    th0 = math.radians(24)
    axL = 150
    up = (math.sin(th0), -math.cos(th0))
    tip = (piv[0] + axL * up[0], piv[1] + axL * up[1])
    cmL = (piv[0] + 0.62 * axL * up[0], piv[1] + 0.62 * axL * up[1])
    f.append(line(piv[0], piv[1], tip[0], tip[1], color=INK, sw=4.0))
    f.append(circle(cmL[0], cmL[1], 7, fill=FILL, stroke=INK, sw=2))
    # вага
    f.append(arrow(cmL[0], cmL[1], cmL[0], cmL[1] + 66, color=INK, sw=2.6))
    f.append(text(cmL[0] + 12, cmL[1] + 46, "m·g", size=13, bold=True,
                  anchor="start"))
    # завалена вісь (пунктир) + дуга падіння
    thf = math.radians(70)
    upf = (math.sin(thf), -math.cos(thf))
    tipf = (piv[0] + axL * upf[0], piv[1] + axL * upf[1])
    f.append(line(piv[0], piv[1], tipf[0], tipf[1], color=MUTED, sw=2.0, dash="7 5"))
    f.append(arc_arrow(piv[0], piv[1], axL + 18, 66, 20, color=POS, sw=2.6, head=11))
    f.append(text(Px + 118, 250, "падає", size=15, bold=True, color=POS,
                  anchor="middle"))

    # ── права панель: обертається → прецесує ──
    Qx = 690
    piv2 = (Qx, 430)
    f.append(text(Qx, 84, "обертається", size=14, bold=True, color=MUTED))
    f.append(line(Qx - 60, piv2[1], Qx + 60, piv2[1], color=INK, sw=2.4))
    for xx in range(-48, 49, 16):
        f.append(line(Qx + xx, piv2[1], Qx + xx - 10, piv2[1] + 12, color=MUTED, sw=1.2))
    f.append(circle(piv2[0], piv2[1], 5, fill=INK, stroke=INK, sw=1))
    tip2 = (piv2[0] + axL * up[0], piv2[1] + axL * up[1])
    cm2 = (piv2[0] + 0.62 * axL * up[0], piv2[1] + 0.62 * axL * up[1])
    f.append(line(piv2[0], piv2[1], tip2[0], tip2[1], color=INK, sw=4.0))
    # диск-ротор упоперек осі
    perp = (up[1], -up[0])
    dk = 30
    f.append(line(cm2[0] - dk * perp[0], cm2[1] - dk * perp[1],
                  cm2[0] + dk * perp[0], cm2[1] + dk * perp[1], color=INK, sw=6.5))
    # вектор L уздовж осі
    Lend = (tip2[0] + 46 * up[0], tip2[1] + 46 * up[1])
    f.append(arrow(cm2[0], cm2[1], Lend[0], Lend[1], color=NEG, sw=3.6))
    f.append(text(Lend[0] + 14, Lend[1] + 2, "L", size=19, bold=True, color=NEG,
                  anchor="start"))
    # спін ω
    f.append(text(cm2[0] - 46, cm2[1] + 4, "ω", size=15, bold=True, color=FIELD,
                  anchor="end"))
    f.append(arc_arrow(cm2[0], cm2[1], 34, 150, -20, color=FIELD, sw=2.2, head=9))
    # вага
    f.append(arrow(cm2[0], cm2[1], cm2[0], cm2[1] + 66, color=INK, sw=2.6))
    f.append(text(cm2[0] + 12, cm2[1] + 46, "m·g", size=13, bold=True, anchor="start"))
    # момент M — з площини (⊙), горизонтальний
    f.append(out_of_plane(Qx - 96, 372, r=14, color=POS))
    f.append(text(Qx - 96, 372 + 34, "M", size=14, bold=True, color=POS))
    f.append(text(Qx - 96, 372 + 51, "(⊥ до L)", size=11, color=POS))
    # прецесія — горизонтальне коло, що його виписує кінець осі
    f.append(ellipse(tip2[0] - 6, tip2[1], 92, 24, fill="none", stroke=PREC,
                     sw=1.6, dash="5 5"))
    f.append(arc_arrow(tip2[0] - 6, tip2[1], 92, 20, -150, color=PREC, sw=2.6, head=11))
    f.append(text(Qx + 40, 150, "Ω — прецесує", size=15, bold=True, color=PREC,
                  anchor="middle"))

    b, w, h = textbox(W / 2, H - 44,
                      "нема наявного L → момент нарощує його «через голову»: дзиґа падає\nє великий L → момент повертає його впоперек: дзиґа прецесує",
                      size=13.5, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "fall-vs-precess.svg"), W, H, *f)


# ── Фігура 2: серце прецесії — dL ⊥ L повертає вектор (як рух по колу) ─────────
def fig_vector_heart():
    W, H = 940, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Момент штовхає L упоперек — і той повертається, а не росте",
                  size=17, bold=True))

    # ── ліворуч: вид згори на кінець вектора L ──
    O = (270, 250)
    R = 122
    f.append(text(O[0], 70, "вид згори (уздовж вертикалі)", size=12.5, color=MUTED))
    f.append(ellipse(O[0], O[1], R, R, fill="none", stroke="#d7dbe0", sw=1.3, dash="4 5"))
    f.append(circle(O[0], O[1], 4, fill=INK, stroke=INK, sw=1))

    # L (горизонтальна складова) — праворуч
    A = (O[0] + R, O[1])
    f.append(arrow(O[0], O[1], A[0], A[1], color=NEG, sw=3.4))
    f.append(text((O[0] + A[0]) / 2, O[1] + 22, "L·sinθ", size=14, italic=True,
                  color=NEG, anchor="middle"))

    # M = dL/dt — по дотичній (вгору) у кінці A
    f.append(arrow(A[0], A[1], A[0], A[1] - 78, color=POS, sw=3.2))
    f.append(text(A[0] + 10, A[1] - 60, "M = dL/dt", size=13.5, bold=True, color=POS,
                  anchor="start"))
    f.append(right_angle(A[0], A[1], (0, -1), (-1, 0), s=12))

    # L' — повернутий на dφ
    dphi = math.radians(33)
    Ap = (O[0] + R * math.cos(dphi), O[1] - R * math.sin(dphi))
    f.append(arrow(O[0], O[1], Ap[0], Ap[1], color=NEG, sw=2.0))
    f.append('<path d="M %.1f %.1f A 30 30 0 0 0 %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="1.4"/>' % (O[0] + 30, O[1], O[0] + 30 * math.cos(dphi),
                                       O[1] - 30 * math.sin(dphi), MUTED))
    bis = math.radians(16)
    f.append(text(O[0] + 66 * math.cos(bis), O[1] - 66 * math.sin(bis) + 4, "dφ",
                  size=13, italic=True, color=MUTED))
    # напрям прецесії
    f.append(arc_arrow(O[0], O[1], R + 20, 44, 104, color=PREC, sw=2.4, head=10))
    f.append(text(O[0] - 58, O[1] - 62, "Ω", size=17, bold=True, color=PREC))

    # ── праворуч: та сама геометрія для швидкості (рух по колу) ──
    O2 = (660, 250)
    r2 = 74
    f.append(text(O2[0], 70, "той самий поворот — для швидкості", size=12.5, color=MUTED))
    f.append(ellipse(O2[0], O2[1], r2, r2, fill="none", stroke="#d7dbe0", sw=1.3, dash="4 5"))
    f.append(circle(O2[0], O2[1], 4, fill=INK, stroke=INK, sw=1))
    Q = (O2[0] + r2, O2[1])
    # v по дотичній (вгору) — синім (роль L)
    f.append(arrow(Q[0], Q[1], Q[0], Q[1] - 70, color=NEG, sw=3.2))
    f.append(text(Q[0] + 10, Q[1] - 54, "v", size=15, bold=True, color=NEG, anchor="start"))
    # F до центра — червоним (роль M)
    f.append(arrow(Q[0], Q[1], O2[0] + 16, O2[1], color=POS, sw=3.0))
    f.append(text(O2[0] + r2 * 0.5, O2[1] - 12, "F", size=15, bold=True, color=POS,
                  anchor="middle"))
    f.append(right_angle(Q[0], Q[1], (0, -1), (-1, 0), s=11))
    f.append(arc_arrow(O2[0], O2[1], r2 + 18, -6, 66, color=MUTED, sw=1.8, head=9))
    f.append(mtext(O2[0], O2[1] + r2 + 48,
                   ["сила F ⊥ v → v повертається,", "тіло біжить колом"],
                   size=12, color=MUTED))

    b, w, h = textbox(W / 2, H - 32,
                      "Ω = M / (L·sinθ) = m·g·r / (J·ω)   —   нахил θ випадає; швидший спін (більше ω) → повільніша прецесія",
                      size=14, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "vector-heart.svg"), W, H, *f)


# ── Фігура 3: Земля як велетенська дзиґа — прецесія рівнодень ─────────────────
def fig_earth():
    W, H = 900, 590
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Земля — велетенська дзиґа: вісь виписує коло за ~25 772 роки",
                  size=17, bold=True))

    C = (330, 380)
    R = 96
    a = 23.5
    ar = math.radians(a)
    u = (math.sin(ar), -math.cos(ar))     # вісь Землі (вгору-праворуч)
    p = (math.cos(ar), math.sin(ar))      # напрям екватора (перпендикуляр)

    # полюс орбіти — вертикаль
    f.append(line(C[0], C[1], C[0], 150, color=MUTED, sw=1.4, dash="6 6"))
    f.append(text(C[0] - 8, 168, "полюс орбіти", size=12, color=MUTED, anchor="end"))

    # тіло Землі
    f.append(circle(C[0], C[1], R, fill="#eef2fb", stroke=INK, sw=1.8))
    # екваторіальний виступ (еліпс, повернений під вісь)
    f.append(ellipse(C[0], C[1], R * 1.16, R * 0.30, fill="none", stroke=POS,
                     sw=2.2, rot=a))
    # лопаті виступу
    lobe_n = (C[0] + R * 1.16 * p[0], C[1] + R * 1.16 * p[1])   # ближча до Сонця (праворуч)
    lobe_f = (C[0] - R * 1.16 * p[0], C[1] - R * 1.16 * p[1])
    f.append(text(C[0], C[1] + R + 44, "екваторіальний виступ", size=12.5, bold=True,
                  color=POS))

    # вісь Землі
    tip = (C[0] + (R + 128) * u[0], C[1] + (R + 128) * u[1])
    bot = (C[0] - (R + 40) * u[0], C[1] - (R + 40) * u[1])
    f.append(line(bot[0], bot[1], tip[0], tip[1], color=INK, sw=3.2))
    f.append(text(C[0] + 118, C[1] - 6, "вісь Землі", size=13, bold=True, anchor="start"))
    f.append(text(C[0] + 118, C[1] + 12, "(нахил 23.5°)", size=11.5, color=MUTED,
                  anchor="start"))
    # спін Землі
    f.append(arc_arrow(C[0], C[1], R - 20, 200, -30, color=FIELD, sw=2.0, head=9))
    f.append(text(C[0] - 6, C[1] + 6, "ω", size=15, bold=True, color=FIELD, anchor="end"))

    # Сонце й Місяць праворуч + нерівна тяга
    f.append(circle(820, 380, 22, fill="#fdecea", stroke=POS, sw=2.2))
    for k in range(0, 360, 45):
        kr = math.radians(k)
        f.append(line(820 + 24 * math.cos(kr), 380 + 24 * math.sin(kr),
                      820 + 33 * math.cos(kr), 380 + 33 * math.sin(kr), color=POS, sw=1.8))
    f.append(text(820, 432, "Сонце,", size=12.5, bold=True, color=POS))
    f.append(text(820, 449, "Місяць", size=12.5, bold=True, color=POS))
    # тяга ближчої лопаті — довша, дальшої — коротша (обидві до Сонця)
    f.append(arrow(lobe_n[0], lobe_n[1], lobe_n[0] + 96, lobe_n[1] - 8, color=POS, sw=3.0))
    f.append(arrow(lobe_f[0], lobe_f[1], lobe_f[0] + 50, lobe_f[1] - 4, color=NEG, sw=2.2))
    f.append(text(470, 486, "нерівна тяга на виступ → момент", size=12.5, bold=True,
                  color=INK, anchor="middle"))

    # коло, що його виписує вісь у небі (конус прецесії)
    SkyC = (C[0], 150)
    srx = (R + 128) * math.sin(ar)
    f.append(ellipse(SkyC[0], SkyC[1], srx, srx * 0.26, fill="none", stroke=PREC,
                     sw=1.8, dash="6 5"))
    f.append(arc_arrow(SkyC[0], SkyC[1], srx, 30, -150, color=PREC, sw=2.4, head=10))
    # поточний напрям осі = Полярна; протилежний = Вега
    f.append(circle(tip[0], tip[1], 5, fill=PREC, stroke=PREC, sw=1))
    f.append(text(tip[0] + 12, tip[1] - 6, "Полярна (нині)", size=12, bold=True,
                  color=PREC, anchor="start"))
    vega = (SkyC[0] - srx, SkyC[1])
    f.append(circle(vega[0], vega[1], 5, fill=PREC, stroke=PREC, sw=1))
    f.append(text(vega[0] - 12, vega[1] - 8, "Вега (~12 тис. р.)", size=12, color=PREC,
                  anchor="end"))

    b, w, h = textbox(W / 2, H - 40,
                      "момент Сонця й Місяця не випрямляє вісь, а змушує її прецесувати —\nтак «мандрує» Полярна зоря й поволі сповзають рівнодення",
                      size=13.5, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "earth-precession.svg"), W, H, *f)


# ── Фігура 4 (вставка math): дві гілки прецесії з квадратного рівняння ────────
def fig_two_branches():
    W, H = 900, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Точна умова — квадрат по Ω: дві гілки прецесії",
                  size=17, bold=True))

    # параметри (безрозмірні): I⊥ = J = m·g·r = 1, cosθ = 0.8
    Iperp, J, mgr, ct = 1.0, 1.0, 1.0, 0.8
    wc = math.sqrt(4 * Iperp * mgr * ct) / J          # критичний спін ≈ 1.789
    wmax = 6.0
    Ymax = 7.6

    # система координат графіка
    ox, oy = 150, H - 96                # початок осей
    plotW, plotH = 660, 384
    sx = plotW / wmax
    sy = plotH / Ymax

    def PX(w): return ox + w * sx
    def PY(y): return oy - y * sy

    # осі
    f.append(arrow(ox, oy, ox + plotW + 20, oy, color=INK, sw=2.0))
    f.append(arrow(ox, oy, ox, oy - plotH - 16, color=INK, sw=2.0))
    f.append(text(ox + plotW + 8, oy + 26, "спін  J·ω₃", size=13, bold=True,
                  anchor="end"))
    f.append(text(ox - 12, oy - plotH - 2, "темп  Ω", size=13, bold=True, anchor="end"))

    # зона «нема стійкої прецесії» (ліворуч від порога)
    f.append(rect(ox, oy - plotH - 12, PX(wc) - ox, plotH + 12,
                  fill="#faf1f0", stroke='none', sw=0, rx=0))
    f.append(line(PX(wc), oy, PX(wc), oy - plotH - 12, color=POS, sw=1.6, dash="6 5"))
    f.append(mtext((ox + PX(wc)) / 2, oy - plotH + 40,
                   ["нижче порога —", "стійкої прецесії", "нема (дзиґа", "падає з нутацією)"],
                   size=11.5, color=POS))
    f.append(text(PX(wc), oy + 22, "поріг", size=12, bold=True, color=POS))

    # гілки Ω±(ω₃)
    N = 160
    top, bot = [], []
    for i in range(N + 1):
        w = wc + (wmax - wc) * i / N
        disc = math.sqrt(max(0.0, (J * w) ** 2 - 4 * Iperp * mgr * ct))
        Wp = (J * w + disc) / (2 * Iperp * ct)
        Wm = (J * w - disc) / (2 * Iperp * ct)
        top.append((PX(w), PY(min(Wp, Ymax))))
        bot.append((PX(w), PY(Wm)))
    dpath = "M " + " L ".join("%.1f %.1f" % p for p in top)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (dpath, PREC))
    dpath = "M " + " L ".join("%.1f %.1f" % p for p in bot)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (dpath, NEG))

    # елементарна формула Ω = m·g·r/(J·ω₃) — пунктиром, лягає на повільну гілку
    el = []
    for i in range(N + 1):
        w = 0.55 + (wmax - 0.55) * i / N
        y = mgr / (J * w)
        if y <= Ymax:
            el.append((PX(w), PY(y)))
    dpath = "M " + " L ".join("%.1f %.1f" % p for p in el)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" '
             'stroke-dasharray="6 5"/>' % (dpath, INK))

    # точка злиття гілок на порозі
    ymc = (J * wc) / (2 * Iperp * ct)
    f.append(circle(PX(wc), PY(ymc), 5, fill=POS, stroke=POS, sw=1))

    # підписи гілок
    f.append(text(PX(4.3), PY(5.6) + 4, "швидка  Ω⁺ ≈ J·ω₃ /(I⊥·cosθ)", size=13,
                  bold=True, color=PREC, anchor="middle"))
    f.append(text(PX(4.5), PY(0.55), "повільна  Ω⁻ ≈ m·g·r /(J·ω₃)", size=13,
                  bold=True, color=NEG, anchor="middle"))
    # легенда: пунктир = елементарна формула (у чистому верхньому куті)
    lx, ly = PX(2.55), PY(7.05)
    f.append(line(lx, ly, lx + 40, ly, color=INK, sw=2, dash="6 5"))
    f.append(text(lx + 48, ly + 4, "елементарна  m·g·r /(J·ω₃)  — лягає на повільну гілку",
                  size=11.5, color=INK, anchor="start", italic=True))

    b, w, h = textbox(W / 2, H - 34,
                      ["I⊥·cosθ·Ω² − J·ω₃·Ω + m·g·r = 0   →   два корені;",
                       "повільний = елементарна формула, швидкий існує й без тяжіння"],
                      size=13.5, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "math-two-branches.svg"), W, H, *f)


# ── Фігура 5 (вставка math): ефективний потенціал і нутація ───────────────────
def fig_effective_potential():
    W, H = 940, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Нутація: рух θ у ефективному потенціалі → кивання з каспами",
                  size=17, bold=True))

    # ── ліва панель: U_eff(θ) ──
    Iperp, J, mgr, w3 = 1.0, 1.0, 1.0, 3.0
    th0 = math.radians(35.0)                 # дзиґу відпустили зі спокою при θ₀
    Lz = J * w3 * math.cos(th0)              # → φ̇ = 0 при θ₀

    def Ueff(th):
        s = math.sin(th)
        return (Lz - J * w3 * math.cos(th)) ** 2 / (2 * Iperp * s * s) + mgr * math.cos(th)

    lo, hi = math.radians(20.0), math.radians(66.0)
    N = 200
    xs = [lo + (hi - lo) * i / N for i in range(N + 1)]
    us = [Ueff(t) for t in xs]
    umin, umax = min(us), max(us)
    # мінімум = стала прецесія
    imin = us.index(umin)
    th_ss = xs[imin]

    ox, oy = 90, H - 110
    plotW, plotH = 360, 330

    def PXt(th): return ox + (th - lo) / (hi - lo) * plotW
    def PYu(u): return oy - (u - umin) / (umax - umin) * plotH

    f.append(arrow(ox, oy, ox + plotW + 18, oy, color=INK, sw=2.0))
    f.append(arrow(ox, oy, ox, oy - plotH - 16, color=INK, sw=2.0))
    f.append(text(ox + plotW + 12, oy + 24, "θ →", size=13, bold=True, anchor="end"))
    f.append(text(ox - 8, oy - plotH - 2, "U_eff(θ)", size=13, bold=True, anchor="end"))

    # рівень енергії дзиґи, відпущеної зі спокою: E = U_eff(θ₀)
    E0 = Ueff(th0)
    # друга точка повороту θ₁ (де U_eff знову = E0, праворуч від мінімуму)
    th1 = None
    for i in range(imin, N + 1):
        if us[i] >= E0:
            th1 = xs[i]
            break
    if th1 is None:
        th1 = hi

    # смуга нутації
    f.append(rect(PXt(th0), oy - plotH - 12, PXt(th1) - PXt(th0), plotH + 12,
                  fill="#eef6ef", stroke='none', sw=0, rx=0))
    # лінія енергії E0
    f.append(line(PXt(th0), PYu(E0), PXt(th1), PYu(E0), color=FIELD, sw=2.0, dash="6 4"))
    f.append(text(PXt(th1) + 6, PYu(E0) + 4, "E", size=13, bold=True, color=FIELD,
                  anchor="start"))

    # крива U_eff
    pts = [(PXt(t), PYu(u)) for t, u in zip(xs, us)]
    dpath = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (dpath, NEG))

    # точки: θ₀ (відпуск/касп), θ_ss (мінімум = стала прецесія), θ₁
    f.append(circle(PXt(th0), PYu(E0), 5, fill=POS, stroke=POS, sw=1))
    f.append(text(PXt(th0), oy + 22, "θ₀", size=13, bold=True, color=POS))
    f.append(text(PXt(th0) - 4, PYu(E0) - 12, "відпустили", size=11, color=POS,
                  anchor="middle"))
    f.append(circle(PXt(th1), PYu(E0), 5, fill=POS, stroke=POS, sw=1))
    f.append(text(PXt(th1), oy + 22, "θ₁", size=13, bold=True, color=POS))
    f.append(circle(PXt(th_ss), PYu(umin), 5, fill=PREC, stroke=PREC, sw=1))
    f.append(text(PXt(th_ss), oy + 22, "θₛₛ", size=13, bold=True, color=PREC))
    f.append(text(PXt(th_ss) + 4, PYu(umin) + 48, "стала прецесія", size=11,
                  color=PREC, anchor="middle"))

    # ── права панель: слід вістря осі — каспи ──
    Cx, Cy = 640, 250
    band_r0, band_r1 = 150, 210          # θ₀ (вгорі, менший конус) і θ₁ (нижче)
    f.append(text(Cx, 96, "слід кінця осі на небесній сфері", size=12.5, color=MUTED))
    # дві паралелі — межі нутації
    f.append(ellipse(Cx, Cy, band_r0, band_r0 * 0.34, fill="none", stroke=POS,
                     sw=1.6, dash="5 5"))
    f.append(ellipse(Cx, Cy, band_r1, band_r1 * 0.34, fill="none", stroke=POS,
                     sw=1.6, dash="5 5"))
    f.append(text(Cx + band_r0 + 8, Cy - band_r0 * 0.34 - 4, "θ₀", size=12, bold=True,
                  color=POS, anchor="start"))
    f.append(text(Cx + band_r1 + 8, Cy - band_r1 * 0.34, "θ₁", size=12, bold=True,
                  color=POS, anchor="start"))

    # цикоїда з каспами: параметрично між двома паралелями, дрейф по φ
    curve = []
    M = 320
    span = math.radians(230)             # показуємо частину повного кола
    a0 = math.radians(150)
    loops = 5.0                          # скільки кивків на показаному куті
    for i in range(M + 1):
        u = i / M
        phi = a0 - span * u              # дрейф прецесії (за годинниковою на вигляд)
        s = 0.5 * (1 - math.cos(2 * math.pi * loops * u))   # 0 при каспі (θ₀), 1 внизу (θ₁)
        rr = band_r0 + (band_r1 - band_r0) * s
        x = Cx + rr * math.cos(phi)
        y = Cy - rr * 0.34 * math.sin(phi)
        curve.append((x, y))
    dpath = "M " + " L ".join("%.1f %.1f" % p for p in curve)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (dpath, PREC))
    f.append(text(Cx, Cy + band_r1 * 0.34 + 30,
                  "касп угорі (φ̇ = 0) — дзиґу відпустили зі спокою", size=11.5,
                  color=PREC))
    # напрям дрейфу — прецесія
    f.append(arc_arrow(Cx, Cy, band_r1 + 26, 8, -60, color=MUTED, sw=1.8, head=9))
    f.append(text(Cx - band_r1 - 20, Cy - 40, "Ω", size=15, bold=True, color=MUTED,
                  anchor="end"))

    b, w, h = textbox(W / 2, H - 30,
                      "мала нутація: частота ≈ J·ω₃ /I⊥,  амплітуда ∝ 1/ω₃²  —  а середній темп = m·g·r /(J·ω) (елементарна формула)",
                      size=13, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "math-effective-potential.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════
#  Фігури до вставки proj-top-simulation: числовий дослід із дзиґою
# ══════════════════════════════════════════════════════════════════════════
# Симетрична дзиґа (велосипедне колесо-гіроскоп зі статті), одиниці СІ.
TM, TR, TG = 4.0, 0.10, 9.8          # маса, плече опора→ц.мас, g
TI3 = 4.0 * 0.30 ** 2                # 0.36  — момент уздовж осі спіну (обід)
TI1 = 0.5 * 4.0 * 0.30 ** 2 + 4.0 * 0.10 ** 2   # 0.22 — поперечний, коло опори
TMGR = TM * TG * TR                  # 3.92


def top_deriv(s, cth=0.0):
    """Похідна стану [θ, φ, ψ, θ̇, p_φ, p_ψ] симетричної дзиґи.
    cth — коефіцієнт в'язкого гасіння нутації (момент −cth·θ̇)."""
    th, ph, ps, thd, pphi, ppsi = s
    sinth, costh = math.sin(th), math.cos(th)
    s2 = sinth * sinth
    if s2 < 1e-12:
        s2 = 1e-12
    phid = (pphi - ppsi * costh) / (TI1 * s2)
    psid = ppsi / TI3 - phid * costh
    thdd = sinth * (phid * phid * costh - (ppsi / TI1) * phid + TMGR / TI1) - cth * thd / TI1
    return [thd, phid, psid, thdd, 0.0, 0.0]


def top_run(th0, phid0, w3, T, dt=0.0005, cth=0.0):
    """Розкрутити дзиґу й повернути списки (t, θ, φ). Чистий RK4, без numpy."""
    ppsi = TI3 * w3
    pphi = TI1 * phid0 * math.sin(th0) ** 2 + ppsi * math.cos(th0)
    s = [th0, 0.0, 0.0, 0.0, pphi, ppsi]
    ts, ths, phs = [0.0], [th0], [0.0]
    n = int(T / dt)
    for i in range(n):
        k1 = top_deriv(s, cth)
        s2v = [a + 0.5 * dt * b for a, b in zip(s, k1)]
        k2 = top_deriv(s2v, cth)
        s3v = [a + 0.5 * dt * b for a, b in zip(s, k2)]
        k3 = top_deriv(s3v, cth)
        s4v = [a + dt * b for a, b in zip(s, k3)]
        k4 = top_deriv(s4v, cth)
        s = [a + dt / 6.0 * (b + 2 * c + 2 * d + e)
             for a, b, c, d, e in zip(s, k1, k2, k3, k4)]
        ts.append((i + 1) * dt); ths.append(s[0]); phs.append(s[1])
    return ts, ths, phs


def polyline(pts, color=LINE, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = "M " + " L ".join("%.2f %.2f" % (x, y) for x, y in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (p, color, sw, d)


def plot_box(x0, y0, w, h, xlab, ylab, title):
    """Рамка-графік; повертає список фрагментів (осі-підписи додає викликач)."""
    f = [rect(x0, y0, w, h, fill="#fcfdff", stroke="#c7ccd6", sw=1.4, rx=4)]
    f.append(text(x0 + w / 2, y0 - 12, title, size=13.5, bold=True))
    f.append(text(x0 + w / 2, y0 + h + 40, xlab, size=12.5, color=MUTED))
    return f


# ── Фігура 6: траєкторія кінця осі — три режими запуску ───────────────────────
def fig_tip_trajectory():
    W, H = 940, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Слід кінця осі: нутація, накладена на прецесію",
                  size=17, bold=True))

    x0, y0, pw, ph = 128, 92, 690, 320
    th0 = math.radians(35.0); w3 = 20.0
    c = math.cos(th0)
    om = TMGR / (TI3 * w3)
    om_steady = (TI3 * w3 - math.sqrt((TI3 * w3) ** 2 - 4 * TI1 * c * TMGR)) / (2 * TI1 * c)
    runs = [(0.0, "відпустили зі спокою (φ̇₀ = 0) → каспи-вістря", POS, "6 4"),
            (om_steady, "точно розрахунковий темп → рівне коло", FIELD, None),
            (2 * om, "запуск швидше за темп → хвиля", NEG, None)]
    curves = []
    for pd, lab, col, dash in runs:
        _, ths, phs = top_run(th0, pd, w3, 1.28)
        pts = [(math.degrees(phs[i]), math.degrees(ths[i]))
               for i in range(0, len(phs), 4)]     # проріджуємо для легкого SVG
        curves.append((pts, lab, col, dash))
    phmax = 36.0
    thlo, thhi = 33.4, 36.6
    def mx(phd): return x0 + phd / phmax * pw
    def my(thd): return y0 + (thd - thlo) / (thhi - thlo) * ph
    f += plot_box(x0, y0, pw, ph, "кут прецесії  φ  (градуси) →", "",
                  "той самий гіроскоп, три способи відпустити — інтегровано RK4")
    f.append(text(x0 - 58, y0 + ph / 2, "нахил осі θ", size=12.5, color=MUTED))
    f.append(text(x0 - 58, y0 + ph / 2 + 18, "(вище = вертикальніше)", size=10.5,
                  color=MUTED))
    for tv in (34, 35, 36):
        yy = my(tv)
        f.append(line(x0, yy, x0 + pw, yy, color="#e6e9f0", sw=1.0))
        f.append(text(x0 - 10, yy + 4, "%d°" % tv, size=11, color=MUTED, anchor="end"))
    for pts, lab, col, dash in curves:
        clip = [(mx(px), my(pt)) for px, pt in pts if px <= phmax]
        f.append(polyline(clip, color=col, sw=2.4, dash=dash))
    f.append(circle(mx(0), my(35.0), 4.5, fill=INK, stroke=INK, sw=1))
    f.append(text(mx(0) + 10, my(35.0) - 10, "старт", size=11, color=INK, anchor="start"))
    ly = y0 + ph + 62
    for i, (pts, lab, col, dash) in enumerate(curves):
        yy = ly + i * 25
        f.append(line(x0 + 6, yy, x0 + 48, yy, color=col, sw=3.0, dash=dash))
        f.append(text(x0 + 58, yy + 4, lab, size=13, color=INK, anchor="start"))
    return render(os.path.join(IMG, "tip-trajectory.svg"), W, H, *f)


# ── Фігура 7: нутація і її згасання від тертя ─────────────────────────────────
def fig_nutation_damping():
    W, H = 940, 506
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Нутація згасає від тертя — прецесія лишається",
                  size=17, bold=True))
    x0, y0, pw, ph = 100, 88, 750, 300
    T = 8.0
    tsu, thu, _ = top_run(math.radians(90.0), 0.0, 20.0, T, dt=0.001, cth=0.0)
    tsd, thd, _ = top_run(math.radians(90.0), 0.0, 20.0, T, dt=0.001, cth=0.30)
    thlo, thhi = 89.4, 92.4
    def mx(t): return x0 + t / T * pw
    def my(d): return y0 + (thhi - d) / (thhi - thlo) * ph
    f += plot_box(x0, y0, pw, ph, "час  t  (секунди) →", "",
                  "нахил θ у часі: старт горизонтально (θ = 90°), спін 20 рад/с")
    f.append(text(x0 - 56, y0 + ph / 2, "нахил θ", size=12.5, color=MUTED))
    for tv in (90, 91, 92):
        yy = my(tv)
        f.append(line(x0, yy, x0 + pw, yy, color="#e6e9f0", sw=1.0))
        f.append(text(x0 - 8, yy + 4, "%d°" % tv, size=11, color=MUTED, anchor="end"))
    for tv in range(1, 9):
        f.append(text(mx(tv), y0 + ph + 18, "%d" % tv, size=10.5, color=MUTED))
    pu = [(mx(tsu[i]), my(math.degrees(thu[i]))) for i in range(0, len(tsu), 6)]
    f.append(polyline(pu, color="#9aa4bf", sw=1.5))
    pd = [(mx(tsd[i]), my(math.degrees(thd[i]))) for i in range(0, len(tsd), 6)]
    f.append(polyline(pd, color=PREC, sw=2.0))
    f.append(text(mx(6.7), my(91.85), "без тертя: нутація вічна", size=12,
                  color="#6b76a0", anchor="middle"))
    f.append(text(mx(5.7), my(90.28), "з тертям: осідає на рівну прецесію",
                  size=12, color=PREC, bold=True, anchor="middle"))
    b, w, h = textbox(x0 + pw / 2, y0 + ph + 78,
                      "тертя гасить дрібне швидке кивання (θ̇ велике), а повільну "
                      "прецесію (θ̇ ≈ 0) майже не чіпає — вісь і далі обходить коло",
                      size=12.5, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "nutation-damping.svg"), W, H, *f)


# ── Фігура 8: спляча дзиґа — стійкість вертикалі ──────────────────────────────
def fig_sleeping_top():
    W, H = 900, 526
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Спляча дзиґа: ефективна енергія нахилу біля вертикалі",
                  size=17, bold=True))
    x0, y0, pw, ph = 118, 92, 664, 300

    def Ueff(th, w3):
        a = TI3 * w3
        s, c = math.sin(th), math.cos(th)
        return (a - a * c) ** 2 / (2 * TI1 * s * s) + TMGR * c

    thmin, thmax = math.radians(1.5), math.radians(42.0)
    fast, slow = 8.0, 3.0
    N = 240
    cf = [thmin + (thmax - thmin) * i / N for i in range(N + 1)]
    base = Ueff(thmin, fast)
    Uf = [Ueff(t, fast) - base for t in cf]
    Us = [Ueff(t, slow) - base for t in cf]
    ylo = min(min(Uf), min(Us)) - 0.15
    yhi = max(max(Uf), max(Us)) + 0.20
    def mx(th): return x0 + (th - thmin) / (thmax - thmin) * pw
    def my(u): return y0 + (yhi - u) / (yhi - ylo) * ph
    f += plot_box(x0, y0, pw, ph, "нахил осі від вертикалі  θ  (градуси) →", "",
                  "яма коло θ = 0 тримає вісь вертикально; горб — валить її")
    f.append(text(x0 - 40, y0 + ph / 2, "U(θ)", size=12.5, color=MUTED))
    for dg in (0, 10, 20, 30, 40):
        xx = mx(math.radians(dg))
        f.append(line(xx, y0, xx, y0 + ph, color="#eef0f5", sw=1.0))
        f.append(text(xx, y0 + ph + 18, "%d°" % dg, size=10.5, color=MUTED))
    f.append(line(mx(0), y0, mx(0), y0 + ph, color=MUTED, sw=1.2, dash="4 4"))
    f.append(polyline([(mx(t), my(u)) for t, u in zip(cf, Uf)], color=FIELD, sw=2.6))
    f.append(polyline([(mx(t), my(u)) for t, u in zip(cf, Us)], color=POS, sw=2.6))
    f.append(text(x0 + pw * 0.50, y0 + 46,
                  "швидкий спін → яма: вертикаль стійка (спить)",
                  size=12.5, color=FIELD, bold=True, anchor="middle"))
    f.append(text(x0 + pw * 0.46, y0 + ph - 22,
                  "повільний спін → горб: вертикаль хитка (валиться)",
                  size=12.5, color=POS, bold=True, anchor="middle"))
    b, w, h = textbox(x0 + pw / 2, y0 + ph + 80,
                      "поріг сну:  (I₃·ω)² ≥ 4·I₁·m·g·r     — вище за нього θ = 0 стійке",
                      size=13, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "sleeping-top.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════
#  Фігури до вставки hist-gyroscope: історія явища й приладу
# ══════════════════════════════════════════════════════════════════════════
def fig_two_threads():
    """Дві нитки — небесне явище й лабораторний прилад — на спільній осі часу."""
    W, H = 1040, 620
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Дві нитки, що не зустрічалися: явище «прецесія» і прилад «гіроскоп»",
                  size=17, bold=True))

    yA, yB = 205, 435
    f.append(arrow(250, yA, 992, yA, color=MUTED, sw=2.0))
    f.append(arrow(250, yB, 992, yB, color=MUTED, sw=2.0))
    f.append(mtext(148, yA - 8, ["ЯВИЩЕ", "рівнодень", "(небо)"], size=12, color=NEG, bold=True))
    f.append(mtext(148, yB - 8, ["ПРИЛАД-", "дзиґа", "(лабораторія)"], size=12, color=PREC, bold=True))

    A = [(300, "~129 до н.е.", ["Гіппарх", "побачив зсув"]),
         (470, "~150 н.е.", ["Птолемей", "1°/100 р — замало"]),
         (645, "~900", ["аль-Баттані", "54.5″/рік"]),
         (810, "1687", ["Ньютон", "момент на виступ"]),
         (952, "1749", ["д'Аламбер", "строгий вивід"])]
    for (x, date, lines) in A:
        b, w, h = textbox(x, 118, "\n".join(lines), size=12, pad=8,
                          fill="#eef2fb", stroke=NEG, sw=1.2)
        f.append(line(x, 118 + h / 2, x, yA - 8, color="#c9d2e6", sw=1.1, dash="3 4"))
        f.append(b)
        f.append(circle(x, yA, 6, fill=NEG, stroke=NEG, sw=1))
        f.append(text(x, yA + 22, date, size=12, bold=True, color=INK))

    Bn = [(360, "1817", ["Боненбергер", "куля в кардані"]),
          (610, "1832", ["Джонсон", "«ротаскоп» — диск"]),
          (852, "1852", ["Фуко", "назвав «гіроскоп»"])]
    for (x, date, lines) in Bn:
        b, w, h = textbox(x, 515, "\n".join(lines), size=12, pad=8,
                          fill="#f2ecf7", stroke=PREC, sw=1.2)
        f.append(line(x, yB + 8, x, 515 - h / 2, color="#d8cbe6", sw=1.1, dash="3 4"))
        f.append(b)
        f.append(circle(x, yB, 6, fill=PREC, stroke=PREC, sw=1))
        f.append(text(x, yB - 14, date, size=12, bold=True, color=INK))

    f.append(text(300, 262, "звідси слово «прецесія»", size=12, italic=True, color=NEG))
    f.append(text(852, 382, "звідси слово «гіроскоп»", size=12, italic=True, color=PREC))
    b, w, h = textbox(W / 2, 322, "дві історії — одна фізика: момент повертає вектор L розкрученої осі",
                      size=13.5, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "two-threads.svg"), W, H, *f)


def fig_foucault_name():
    """Чому «гіроскоп»: розкручена вісь тримає напрям на зорю, Земля йде під нею."""
    W, H = 940, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Чому «гіроскоп»: прилад, яким Фуко побачив обертання Землі",
                  size=17, bold=True))

    # Земля — поверхня як полога дуга (path, без кола поза кадром)
    f.append('<path d="M 60 472 Q 470 428 880 472 L 880 560 L 60 560 Z" '
             'fill="#eef2fb" stroke="none"/>')
    f.append('<path d="M 60 472 Q 470 428 880 472" fill="none" stroke="%s" '
             'stroke-width="1.6"/>' % INK)
    f.append(arc_arrow(470, 985, 534, 95, 85, color=FIELD, sw=2.4, head=11))
    f.append(text(470, 408, "обертання Землі →", size=12.5, bold=True, color=FIELD))
    f.append(text(800, 500, "поверхня Землі", size=12, color=MUTED))

    S = (700, 118)
    f.append(circle(S[0], S[1], 4, fill=INK, stroke=INK, sw=1))
    for k in range(0, 360, 45):
        kr = math.radians(k)
        f.append(line(S[0] + 7 * math.cos(kr), S[1] + 7 * math.sin(kr),
                      S[0] + 15 * math.cos(kr), S[1] + 15 * math.sin(kr), color=INK, sw=1.6))
    f.append(mtext(725, 112, ["далека зоря", "(стоїть на місці)"], size=12, color=INK,
                   anchor="start"))

    G = (300, 300)
    dx, dy = S[0] - G[0], S[1] - G[1]
    Ln = math.hypot(dx, dy)
    u = (dx / Ln, dy / Ln)
    pu = (-u[1], u[0])
    f.append(line(G[0], 446, G[0], 398, color=INK, sw=3.2))
    f.append(line(G[0] - 30, 446, G[0] + 30, 446, color=INK, sw=3.2))
    f.append(ellipse(G[0], G[1], 70, 96, fill="none", stroke=MUTED, sw=2.0))
    f.append(ellipse(G[0], G[1], 96, 52, fill="none", stroke=MUTED, sw=2.0))
    f.append(text(G[0] + 108, G[1] + 6, "карданів підвіс", size=11.5, color=MUTED,
                  anchor="start"))
    r0 = (G[0] - 40 * pu[0], G[1] - 40 * pu[1])
    r1 = (G[0] + 40 * pu[0], G[1] + 40 * pu[1])
    f.append(line(r0[0], r0[1], r1[0], r1[1], color=INK, sw=7.0))
    f.append(arc_arrow(G[0], G[1], 30, 150, -20, color=FIELD, sw=2.2, head=9))
    f.append(text(G[0] - 44, G[1] + 6, "ω", size=15, bold=True, color=FIELD, anchor="end"))
    Le = (G[0] + 66 * u[0], G[1] + 66 * u[1])
    f.append(arrow(G[0], G[1], Le[0], Le[1], color=NEG, sw=3.4))
    f.append(text(Le[0] + 12, Le[1] - 6, "L", size=18, bold=True, color=NEG, anchor="start"))
    f.append(line(Le[0], Le[1], S[0] - 18 * u[0], S[1] - 18 * u[1], color=NEG, sw=1.4, dash="6 5"))
    # (підпис осі прибрано — дублював рамку-фізику й перетинав пунктир)

    b, w, h = textbox(300, 150, "жодного моменту → L незрушний:\nвісь сама лишається на зорі",
                      size=12.5, pad=9, fill="#eef2fb", stroke=NEG, sw=1.2, bold=True)
    f.append(b)
    b, w, h = textbox(W / 2, 524,
                      "gyros — обертання  ·  skopein — дивитися  →  «дивитися на обертання».  Леон Фуко, 1852",
                      size=13, pad=11, fill=FILL, stroke=PREC, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "foucault-name.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_fall_vs_precess(), fig_vector_heart(), fig_earth(),
          fig_two_branches(), fig_effective_potential(),
          fig_tip_trajectory(), fig_nutation_damping(), fig_sleeping_top(),
          fig_two_threads(), fig_foucault_name()]
    print("written:")
    for p in ps:
        print("  ", p)
