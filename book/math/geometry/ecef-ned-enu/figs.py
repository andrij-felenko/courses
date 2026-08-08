# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# ── Проста аксонометрія: камера з азимуту A і висоти E ─────────────────────
A_CAM = math.radians(20.0)
E_CAM = math.radians(20.0)
RIGHT = (-math.sin(A_CAM), math.cos(A_CAM), 0.0)
UPV = (-math.cos(A_CAM) * math.sin(E_CAM), -math.sin(A_CAM) * math.sin(E_CAM), math.cos(E_CAM))
VIEW = (math.cos(A_CAM) * math.cos(E_CAM), math.sin(A_CAM) * math.cos(E_CAM), math.sin(E_CAM))


def d3(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def sph(phi_deg, lam_deg, r=1.0):
    p, l = math.radians(phi_deg), math.radians(lam_deg)
    return (r * math.cos(p) * math.cos(l), r * math.cos(p) * math.sin(l), r * math.sin(p))


def pr(v, cx, cy, R):
    """3D-вектор (в одиницях земного радіуса) -> екранні координати."""
    return (cx + R * d3(v, RIGHT), cy - R * d3(v, UPV))


def polyline(pts, color=LINE, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, color, sw, d))


# ══ ФІГУРА 1: осі ECEF ═══════════════════════════════════════════════════════
def ecef_axes():
    W, H = 830, 480
    cx, cy, R = 250.0, 260.0, 148.0
    f = []
    f.append(text(W / 2, 28, "ECEF: осі, прибиті до самої планети", size=16, bold=True))

    # силует кулі
    f.append(circle(cx, cy, R, fill="#fbfcfd", stroke=MUTED, sw=1.6))

    # екватор: ближня половина суцільна, дальня — пунктиром
    near, far = [], []
    t = 0.0
    while t <= 360.001:
        v = sph(0.0, t)
        p = pr(v, cx, cy, R)
        (near if d3(v, VIEW) >= 0 else far).append((t, p))
        t += 3.0
    # розбити на суцільні шматки за неперервністю кута
    def chunks(seq):
        out, cur = [], []
        prev = None
        for tt, p in seq:
            if prev is not None and tt - prev > 4.0:
                out.append(cur); cur = []
            cur.append(p); prev = tt
        if cur:
            out.append(cur)
        return out
    for ch in chunks(far):
        if len(ch) > 1:
            f.append(polyline(ch, color=MUTED, sw=1.4, dash="5,5"))
    for ch in chunks(near):
        if len(ch) > 1:
            f.append(polyline(ch, color=INK, sw=2.0))

    # нульовий меридіан (λ = 0): дуга від полюса до полюса через вісь X
    mer = [pr(sph(u, 0.0), cx, cy, R) for u in range(-90, 91, 3)]
    f.append(polyline(mer, color=POS, sw=2.2))

    # осі
    axz = pr((0, 0, 1.30), cx, cy, R)
    axx = pr((1.42, 0, 0), cx, cy, R)
    axy = pr((0, 1.34, 0), cx, cy, R)
    f.append(arrow(cx, cy, axz[0], axz[1], color=NEG, sw=2.2))
    f.append(arrow(cx, cy, axx[0], axx[1], color=POS, sw=2.2))
    f.append(arrow(cx, cy, axy[0], axy[1], color=FIELD, sw=2.2))
    f.append(text(axz[0] + 14, axz[1] + 4, "Z", size=17, bold=True, color=NEG, anchor="start"))
    f.append(text(axx[0] - 6, axx[1] + 20, "X", size=17, bold=True, color=POS, anchor="middle"))
    f.append(text(axy[0] + 12, axy[1] + 16, "Y", size=17, bold=True, color=FIELD, anchor="start"))

    # початок
    f.append(circle(cx, cy, 5, fill=INK, stroke=INK))
    f.append(text(cx - 12, cy + 22, "O", size=15, bold=True, color=INK, anchor="end"))

    # точка P і дуга довготи в екваторіальній площині
    lam = 70.0
    Pv = sph(34.0, lam)
    Pp = pr(Pv, cx, cy, R)
    f.append(line(cx, cy, Pp[0], Pp[1], color=INK, sw=1.6, dash="4,4"))
    f.append(circle(Pp[0], Pp[1], 5, fill=INK, stroke=INK))
    f.append(text(Pp[0] + 12, Pp[1] - 10, "P", size=15, bold=True, color=INK, anchor="start"))
    arc = [pr(sph(0.0, t * 1.0, 0.52), cx, cy, R) for t in range(0, int(lam) + 1, 3)]
    f.append(polyline(arc, color=POS, sw=2.0))
    mid = pr(sph(0.0, lam * 0.5, 0.68), cx, cy, R)
    f.append(text(mid[0], mid[1] + 16, "λ", size=16, bold=True, color=POS))

    # обертання навколо Z
    rot = [pr((0.30 * math.cos(math.radians(t)), 0.30 * math.sin(math.radians(t)), 1.12),
              cx, cy, R) for t in range(-150, 121, 6)]
    f.append(polyline(rot[:-1], color=NEG, sw=1.8))
    f.append(arrow(rot[-2][0], rot[-2][1], rot[-1][0], rot[-1][1], color=NEG, sw=1.8))
    f.append(text(96, 108, "ω = 7.29·10⁻⁵ рад/с", size=12, color=NEG, anchor="start"))

    # легенда
    f.append(fitbox(500, 96, 300, 250,
                    "\n".join([
                        "O — центр мас Землі",
                        "(бо саме навколо нього",
                        "ходять супутники)",
                        "",
                        "Z — середня вісь обертання",
                        "X — екватор ∩ нульовий меридіан",
                        "Y = Z × X, права трійка",
                        "",
                        "осі крутяться разом із планетою:",
                        "у скелі X, Y, Z незмінні",
                    ]), size=13, fill="#f7f9fc", stroke=NEG, sw=1.6))
    render(os.path.join(IMG, "ecef-axes.svg"), W, H, *f)


# ══ ФІГУРА 2: меридіанний еліпс, нормаль і N ════════════════════════════════
def normal_and_n():
    W, H = 840, 520
    ox, oy = 170.0, 330.0          # центр Землі на екрані
    a, b = 320.0, 252.0            # півосі в px (сплюснутість СИЛЬНО перебільшена)
    e2 = 1.0 - (b * b) / (a * a)
    phi = math.radians(55.0)
    sp, cp = math.sin(phi), math.cos(phi)
    N = a / math.sqrt(1.0 - e2 * sp * sp)
    p = N * cp
    z = N * (1.0 - e2) * sp
    z0 = -e2 * N * sp              # де нормаль перетинає вісь обертання

    f = []
    f.append(text(W / 2, 28, "Геодезична широта — це кут нормалі, а не радіуса",
                  size=16, bold=True))

    # чверть меридіанного еліпса
    pts = []
    t = 0.0
    while t <= 90.001:
        tt = math.radians(t)
        pts.append((ox + a * math.cos(tt), oy - b * math.sin(tt)))
        t += 1.5
    f.append(polyline(pts, color=NEG, sw=2.6))

    # осі
    f.append(line(ox, oy + 150, ox, oy - b - 34, color=MUTED, sw=1.4, dash="6,5"))
    f.append(line(ox - 30, oy, ox + a + 40, oy, color=MUTED, sw=1.4, dash="6,5"))
    f.append(text(ox + a + 46, oy + 5, "екватор", size=12, color=MUTED, anchor="start"))
    f.append(text(ox + 8, oy - b - 40, "вісь обертання", size=12, color=MUTED, anchor="start"))

    # точка на поверхні
    Px, Py = ox + p, oy - z
    f.append(circle(Px, Py, 5.5, fill=FIELD, stroke=FIELD))
    f.append(text(430, 120, "точка на поверхні", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(line(Px + 4, Py - 4, 426, 122, color=FIELD, sw=1.0, dash="2,3"))

    # нормаль: від перетину з віссю обертання через точку і далі назовні
    Ix, Iy = ox, oy - z0
    Ex, Ey = Px + 58 * cp, Py - 58 * sp
    f.append(line(Ix, Iy, Px, Py, color=POS, sw=2.4))
    f.append(arrow(Px, Py, Ex, Ey, color=POS, sw=2.0))
    f.append(text(Ex + 12, Ey - 6, "нормаль", size=12, bold=True, color=POS, anchor="start"))
    # підпис N — збоку від відрізка
    mx, my = (Ix + Px) / 2.0, (Iy + Py) / 2.0
    f.append(text(mx - 0.82 * 30 - 4, my - 0.57 * 30, "N", size=17, bold=True, color=POS))

    # радіус із центра (геоцентричний кут)
    f.append(line(ox, oy, Px, Py, color=INK, sw=1.8, dash="5,4"))

    # проєкції p і z
    f.append(line(ox, Py, Px, Py, color=FIELD, sw=1.8, dash="4,4"))
    f.append(text((ox + Px) / 2.0, Py - 12, "p", size=16, bold=True, color=FIELD))
    f.append(line(Px, oy, Px, Py, color=FIELD, sw=1.8, dash="4,4"))
    f.append(text(Px + 12, oy - 60, "z", size=16, bold=True, color=FIELD, anchor="start"))

    # зсув перетину вниз від центра
    f.append(line(ox, oy, ox, Iy, color=NEG, sw=3.0))
    f.append(text(ox - 14, (oy + Iy) / 2.0 + 5, "e²·N·sin φ", size=12, bold=True,
                  color=NEG, anchor="end"))

    # кути: φ біля перетину, ψ біля центра
    ar = []
    t = 0.0
    while t <= 55.001:
        tt = math.radians(t)
        ar.append((Ix + 62 * math.cos(tt), Iy - 62 * math.sin(tt)))
        t += 2.0
    f.append(polyline(ar, color=POS, sw=1.6))
    f.append(text(Ix + 84, Iy - 30, "φ", size=17, bold=True, color=POS, anchor="start"))

    psi = math.atan2(z, p)
    ar2 = []
    t = 0.0
    while t <= math.degrees(psi) + 0.001:
        tt = math.radians(t)
        ar2.append((ox + 96 * math.cos(tt), oy - 96 * math.sin(tt)))
        t += 2.0
    f.append(polyline(ar2, color=INK, sw=1.6))
    f.append(text(ox + 120, oy - 28, "ψ", size=17, bold=True, color=INK, anchor="start"))

    # пояснення
    f.append(fitbox(560, 150, 262, 214,
                    "\n".join([
                        "N = a / √(1 − e²·sin²φ)",
                        "p = N·cos φ",
                        "z = N·(1 − e²)·sin φ",
                        "",
                        "φ — геодезична (кут нормалі)",
                        "ψ — геоцентрична (кут радіуса)",
                        "",
                        "сплюснутість тут перебільшена",
                    ]), size=13, fill="#fdf7f6", stroke=POS, sw=1.6))
    render(os.path.join(IMG, "normal-and-n.svg"), W, H, *f)


# ══ ФІГУРА 3: місцева трійка ENU / NED ══════════════════════════════════════
def local_triad():
    W, H = 840, 450
    cx, cy, R = 215.0, 240.0, 140.0
    f = []
    f.append(text(W / 2, 28, "Місцева трійка: схід, північ, вгору — в точці стояння",
                  size=16, bold=True))

    f.append(circle(cx, cy, R, fill="#fbfcfd", stroke=MUTED, sw=1.6))

    near, far = [], []
    t = 0.0
    while t <= 360.001:
        v = sph(0.0, t)
        (near if d3(v, VIEW) >= 0 else far).append((t, pr(v, cx, cy, R)))
        t += 3.0

    def chunks(seq):
        out, cur, prev = [], [], None
        for tt, pp in seq:
            if prev is not None and tt - prev > 4.0:
                out.append(cur); cur = []
            cur.append(pp); prev = tt
        if cur:
            out.append(cur)
        return out
    for ch in chunks(far):
        if len(ch) > 1:
            f.append(polyline(ch, color=MUTED, sw=1.3, dash="5,5"))
    for ch in chunks(near):
        if len(ch) > 1:
            f.append(polyline(ch, color=MUTED, sw=1.8))

    lam, phi = 45.0, 40.0
    mer = [pr(sph(u, lam), cx, cy, R) for u in range(-20, 91, 3)]
    f.append(polyline(mer, color=MUTED, sw=1.5))

    # вісь Z для контексту
    zt = pr((0, 0, 1.22), cx, cy, R)
    f.append(line(cx, cy, zt[0], zt[1], color=NEG, sw=1.4, dash="6,5"))
    f.append(text(zt[0] + 12, zt[1] + 4, "Z", size=14, bold=True, color=NEG, anchor="start"))

    P = sph(phi, lam)
    Pp = pr(P, cx, cy, R)
    pl, ph_ = math.radians(lam), math.radians(phi)
    ev = (-math.sin(pl), math.cos(pl), 0.0)
    nv = (-math.sin(ph_) * math.cos(pl), -math.sin(ph_) * math.sin(pl), math.cos(ph_))
    uv = P

    def tip(vec, k):
        return (Pp[0] + k * d3(vec, RIGHT), Pp[1] - k * d3(vec, UPV))

    te, tn, tu = tip(ev, 155.0), tip(nv, 105.0), tip(uv, 100.0)
    f.append(arrow(Pp[0], Pp[1], te[0], te[1], color=FIELD, sw=2.4))
    f.append(arrow(Pp[0], Pp[1], tn[0], tn[1], color=POS, sw=2.4))
    f.append(arrow(Pp[0], Pp[1], tu[0], tu[1], color=NEG, sw=2.4))
    f.append(circle(Pp[0], Pp[1], 5.5, fill=INK, stroke=INK))

    f.append(text(390, 150, "E", size=17, bold=True, color=FIELD))
    f.append(text(200, 93, "N", size=17, bold=True, color=POS))
    f.append(text(299, 146, "U", size=17, bold=True, color=NEG))

    f.append(fitbox(478, 66, 330, 116,
                    "\n".join([
                        "ENU — схід, північ, вгору",
                        "x = E,  y = N,  z = U",
                        "геодезія, ГІС, ROS (REP-103)",
                    ]), size=13, fill="#f4fbf7", stroke=FIELD, sw=1.7))
    f.append(fitbox(478, 200, 330, 116,
                    "\n".join([
                        "NED — північ, схід, вниз",
                        "x = N,  y = E,  z = D = −U",
                        "авіація, автопілоти, MAVLink",
                    ]), size=13, fill="#fdf7f6", stroke=POS, sw=1.7))
    f.append(fitbox(478, 334, 330, 94,
                    "\n".join([
                        "перехід: поміняти дві перші осі",
                        "й розвернути третю; визначник +1 —",
                        "це поворот, а не дзеркало",
                    ]), size=13, fill="#f7f9fc", stroke=NEG, sw=1.7))
    render(os.path.join(IMG, "local-triad.svg"), W, H, *f)


def plumb_vs_normal():
    """Відхилення прямовисної лінії в Гринвічі й 102 метри на землі."""
    W, H = 900, 480
    f = []
    f.append(line(452, 40, 452, 440, color="#c9d2dc", sw=1.4, dash="6 6"))

    # ── ліва панель: дві «вертикалі» в одній точці ─────────────────────────
    f.append(text(230, 40, "Одна точка — дві вертикалі", size=15, bold=True))

    # еліпсоїд — гладка лінія
    f.append(line(40, 344, 420, 344, color=NEG, sw=2.4))
    # геоїд — хвиляста рівнева поверхня
    pts = []
    for i in range(0, 77):
        x = 40 + i * 5.0
        y = 300 - 14.0 * math.sin((x - 40) / 380.0 * 2 * math.pi)
        pts.append((x, y))
    for a, b in zip(pts, pts[1:]):
        f.append(line(a[0], a[1], b[0], b[1], color=FIELD, sw=2.4))

    ox, oy = 230.0, 300.0
    slope = -14.0 * math.cos(math.pi) * (2 * math.pi / 380.0)   # dy/dx у точці O
    nx, ny = slope, -1.0
    ln = math.hypot(nx, ny)
    nx, ny = nx / ln, ny / ln

    f.append(line(ox, oy, ox, 128, color=NEG, sw=2.0, dash="7 5"))
    f.append(arrow(ox, oy, ox + nx * 178, oy + ny * 178, color=FIELD, sw=2.4))
    f.append(circle(ox, oy, 5.5, fill="#ffffff", stroke=INK, sw=2))

    f.append(text(206, 118, "нормаль до еліпсоїда", size=12.5, color=NEG, anchor="end"))
    f.append(text(292, 106, "прямовисна лінія", size=12.5, color=FIELD, anchor="start"))
    f.append(text(216, 186, "ξ ≈ 5.3″", size=13, bold=True, anchor="end"))
    f.append(text(216, 206, "(на рисунку перебільшено)", size=11, color="#7b8794", anchor="end"))
    f.append(text(230, 272, "Гринвіч", size=12.5, anchor="middle"))

    f.append(fitbox(34, 372, 186, 58,
                    "геоїд — рівнева поверхня\nсили тяжіння, горбкувата",
                    size=12.5, fill="#f4fbf7", stroke=FIELD, sw=1.6))
    f.append(fitbox(240, 372, 186, 58,
                    "еліпсоїд WGS 84 — гладка\nматематична форма",
                    size=12.5, fill="#f7f9fc", stroke=NEG, sw=1.6))

    # ── права панель: дві лінії на землі ──────────────────────────────────
    f.append(text(676, 40, "Дві лінії на бруківці", size=15, bold=True))
    f.append(fitbox(482, 60, 176, 52, "лінія Ейрі 1851\n(латунна смуга)",
                    size=12.5, fill="#fdf7f6", stroke=POS, sw=1.6))
    f.append(fitbox(694, 60, 176, 52, "нуль IERS\n(GPS, ITRF)",
                    size=12.5, fill="#f4fbf7", stroke=FIELD, sw=1.6))
    f.append(line(570, 118, 570, 300, color=POS, sw=2.6))
    f.append(line(782, 118, 782, 300, color=FIELD, sw=2.6))
    f.append(arrow(570, 322, 782, 322, color=INK, sw=1.8))
    f.append(arrow(782, 322, 570, 322, color=INK, sw=1.8))
    f.append(text(676, 312, "102 м на схід", size=13, bold=True))
    f.append(fitbox(482, 372, 388, 58,
                    "5.3″ = 2.57·10⁻⁵ рад × 3 970 км (радіус\nпаралелі 51.48° пн. ш.) ≈ 102 м",
                    size=12.5, fill="#fbfbfc", stroke=LINE, sw=1.6))

    render(os.path.join(IMG, "plumb-vs-normal.svg"), W, H, *f)


# ══ ВСТАВКА math-ecef-to-geodetic: геометрія тотожності Боуринга ════════════
def inverse_bowring_geometry():
    """Центр кривини на еволюті — і чому один крок Боуринга влучає."""
    W, H = 900, 545
    ox, oy = 140.0, 350.0
    a, b = 330.0, 272.0                 # сплюснутість СИЛЬНО перебільшена
    ca = (a * a - b * b) / a            # виніс каспа еволюти по p
    cb = (a * a - b * b) / b            # виніс каспа еволюти по z

    phi = math.radians(52.0)
    sp, cp = math.sin(phi), math.cos(phi)
    beta = math.atan2(b * sp, a * cp)
    sb, cb_ = math.sin(beta), math.cos(beta)
    Fx, Fy = ox + a * cb_, oy - b * sb                     # основа нормалі
    hpx = 62.0
    Px, Py = Fx + hpx * cp, Fy - hpx * sp                  # задана точка
    Cx, Cy = ox + ca * cb_ ** 3, oy + cb * sb ** 3         # центр кривини

    f = []
    f.append(text(W / 2, 26, "Чому формула Боуринга точна: центр кривини лежить на нормалі",
                  size=16, bold=True))

    # осі
    f.append(line(ox, 500, ox, 66, color=MUTED, sw=1.3, dash="6,5"))
    f.append(line(96, oy, 512, oy, color=MUTED, sw=1.3, dash="6,5"))

    # чверть меридіанного еліпса
    pts = [(ox + a * math.cos(math.radians(t)), oy - b * math.sin(math.radians(t)))
           for t in range(0, 91)]
    f.append(polyline(pts, color=NEG, sw=2.6))

    # еволюта (астроїда) — тільки та чверть, що відповідає β ∈ [0°, 90°]
    ev = [(ox + ca * math.cos(math.radians(t)) ** 3, oy + cb * math.sin(math.radians(t)) ** 3)
          for t in range(0, 91)]
    f.append(polyline(ev, color=FIELD, sw=2.4))

    # складові вектора C -> P
    f.append(line(Cx, Cy, Px, Cy, color=MUTED, sw=1.5, dash="4,4"))
    f.append(line(Px, Cy, Px, Py, color=MUTED, sw=1.5, dash="4,4"))
    f.append(text((Cx + Px) / 2.0, Cy + 22, "p − e²a·cos³β", size=13, color=MUTED))
    f.append(text(Px + 12, (Cy + Py) / 2.0, "z + e′²b·sin³β", size=13, color=MUTED,
                  anchor="start"))

    # нормаль: від C через F до P і трохи далі
    f.append(line(Cx, Cy, Fx, Fy, color=POS, sw=2.4))
    f.append(arrow(Fx, Fy, Px + 22 * cp, Py - 22 * sp, color=POS, sw=2.2))

    # кут φ біля C
    arc = [(Cx + 74 * math.cos(math.radians(t)), Cy - 74 * math.sin(math.radians(t)))
           for t in range(0, 53)]
    f.append(polyline(arc, color=POS, sw=1.5))
    f.append(text(Cx + 92, Cy - 26, "φ", size=17, bold=True, color=POS, anchor="start"))

    # точки
    f.append(circle(Cx, Cy, 5.5, fill=FIELD, stroke=FIELD))
    f.append(circle(Fx, Fy, 5.0, fill=NEG, stroke=NEG))
    f.append(circle(Px, Py, 5.5, fill=POS, stroke=POS))
    f.append(circle(ox, oy, 4.0, fill=INK, stroke=INK))
    f.append(text(ox - 12, oy + 20, "O", size=14, bold=True, anchor="end"))
    f.append(text(Cx - 12, Cy + 6, "C", size=15, bold=True, color=FIELD, anchor="end"))
    f.append(text(Fx + 13, Fy + 18, "F", size=15, bold=True, color=NEG, anchor="start"))
    f.append(text(Px + 4, Py - 12, "P", size=15, bold=True, color=POS, anchor="start"))
    f.append(text((Fx + Px) / 2.0 - 16, (Fy + Py) / 2.0 - 4, "h", size=15, bold=True,
                  color=POS, anchor="end"))

    f.append(text(300, 466, "еволюта: центри кривини меридіана", size=12.5,
                  color=FIELD, anchor="start"))
    f.append(line(292, 462, 236, 420, color=FIELD, sw=1.0, dash="2,3"))

    f.append(fitbox(556, 92, 322, 292,
                    "\n".join([
                        "F — основа нормалі на еліпсоїді",
                        "P — задана точка, h уздовж нормалі",
                        "C — центр кривини меридіана:",
                        "C = ( e²a·cos³β,  −e′²b·sin³β )",
                        "e²a = 42 698 м,  e′²b = 42 841 м",
                        "",
                        "C лежить НА нормалі, тому",
                        "tan φ = (z + e′²b·sin³β)",
                        "            ⁄ (p − e²a·cos³β)",
                        "— рівність точна, не наближена",
                        "",
                        "похибка в β совгає C уздовж тієї",
                        "самої нормалі: напрям CP не",
                        "міняється в першому порядку",
                    ]), size=13, fill="#f4fbf7", stroke=FIELD, sw=1.7))
    render(os.path.join(IMG, "inverse-bowring-geometry.svg"), W, H, *f)


# ══ ВСТАВКА math-ecef-to-geodetic: як спадає похибка ════════════════════════
def inverse_convergence():
    """Геометрична збіжність простої ітерації проти одного кроку Боуринга."""
    W, H = 880, 480
    x0, x1 = 150.0, 620.0
    ytop, dec = 74.0, 30.0              # y для 10 м; піксели на десяткову декаду
    top_log = 1.0

    def yv(err):
        lg = math.log10(err) if err > 0 else -10.0
        lg = max(lg, -10.0)
        return ytop + (top_log - lg) * dec

    f = []
    f.append(text(W / 2, 26, "Похибка широти після кожного кроку (Київ, h = 180 м)",
                  size=16, bold=True))

    # сітка й підписи осі
    for lg, lab in ((1, "10 м"), (0, "1 м"), (-3, "1 мм"), (-6, "1 мкм"), (-9, "1 нм")):
        y = ytop + (top_log - lg) * dec
        f.append(line(x0 - 8, y, x1 + 16, y, color="#dfe4ea", sw=1.2))
        f.append(text(x0 - 18, y + 5, lab, size=12.5, color=MUTED, anchor="end"))

    f.append(line(x0, ytop - 10, x0, ytop + 11 * dec + 10, color=LINE, sw=1.6))
    f.append(line(x0, ytop + 11 * dec + 10, x1 + 30, ytop + 11 * dec + 10, color=LINE, sw=1.6))

    errs = [0.5937, 1.618e-3, 4.409e-6, 1.202e-8, 0.0]
    step = (x1 - x0) / 4.0
    xs = [x0 + i * step for i in range(5)]

    # підлога подвійної точності
    yfloor = yv(9.3e-10)
    f.append(line(x0, yfloor, x1 + 16, yfloor, color=NEG, sw=1.6, dash="7,5"))
    f.append(text(x1 + 22, yfloor - 10, "підлога double", size=12, color=NEG, anchor="end"))

    prev = None
    for i, (xx, e) in enumerate(zip(xs, errs)):
        y = yv(e)
        if prev:
            f.append(line(prev[0], prev[1], xx, y, color=POS, sw=2.4))
        prev = (xx, y)
        f.append(circle(xx, y, 6.0, fill=POS, stroke=POS))
        f.append(text(xx, ytop + 11 * dec + 30, ["старт", "1", "2", "3", "4"][i],
                      size=12.5, color=MUTED))

    # Боуринг: один крок
    xb, yb = xs[1], yv(7.07e-10)
    f.append(circle(xb, yb, 7.0, fill=FIELD, stroke=FIELD))
    f.append(text(xb + 16, yb + 24, "Боуринг: один крок → 0.7 нм", size=13, bold=True,
                  color=FIELD, anchor="start"))

    f.append(text(x0 + (x1 - x0) / 2.0, ytop + 11 * dec + 52, "кроків простої ітерації",
                  size=13, color=MUTED))
    f.append(text(320, 120, "нахил прямої = ×0.0027 за крок", size=13, bold=True,
                  color=POS, anchor="start"))

    f.append(fitbox(664, 92, 200, 118,
                    "\n".join([
                        "множник стиску",
                        "e²N·cos²φ",
                        "  ⁄ ((N+h)(1−e²sin²φ))",
                        "= 0.002725",
                    ]), size=12.5, fill="#fdf7f6", stroke=POS, sw=1.6))
    f.append(fitbox(664, 236, 200, 100,
                    "\n".join([
                        "пряма в лог-масштабі",
                        "= геометрична",
                        "збіжність: 2.6 цифри",
                        "за крок",
                    ]), size=12.5, fill="#f7f9fc", stroke=NEG, sw=1.6))
    render(os.path.join(IMG, "inverse-convergence.svg"), W, H, *f)


# ══ ВСТАВКА math-ecef-to-geodetic: де розв'язок перестає бути єдиним ════════
def inverse_caustic():
    """Усередині еволюти з точки виходить чотири нормалі — широти не існує."""
    W, H = 900, 520
    ox, oy = 285.0, 262.0
    a, b = 250.0, 206.0
    ca = (a * a - b * b) / a
    cb = (a * a - b * b) / b
    Qx, Qy = 25.0, 30.0                 # точка всередині астроїди (в осях еліпса)

    def cross(t):
        cs, sn = math.cos(t), math.sin(t)
        return (Qx - a * cs) * (a * sn) - (Qy - b * sn) * (b * cs)

    roots, t = [], 0.0
    while t < 2 * math.pi:
        t2 = t + 0.002
        if cross(t) == 0.0 or cross(t) * cross(t2) < 0:
            lo, hi = t, t2
            for _ in range(60):
                mid = (lo + hi) / 2.0
                if cross(lo) * cross(mid) <= 0:
                    hi = mid
                else:
                    lo = mid
            roots.append((lo + hi) / 2.0)
        t = t2

    f = []
    f.append(text(W / 2, 26, "Область, де широти просто немає: чотири нормалі з однієї точки",
                  size=16, bold=True))

    pts = [(ox + a * math.cos(math.radians(t)), oy - b * math.sin(math.radians(t)))
           for t in range(0, 361)]
    f.append(polyline(pts, color=NEG, sw=2.4))

    # межа-еліпс, на якій ρ обертається в нуль
    gp = [(ox + ca * math.cos(math.radians(t)), oy - cb * math.sin(math.radians(t)))
          for t in range(0, 361)]
    f.append(polyline(gp, color=MUTED, sw=1.4, dash="5,4"))

    # еволюта
    evo = [(ox + ca * math.cos(math.radians(t)) ** 3, oy - cb * math.sin(math.radians(t)) ** 3)
           for t in range(0, 361)]
    f.append(polyline(evo, color=FIELD, sw=2.2))

    QX, QY = ox + Qx, oy - Qy
    for t in roots:
        fx, fy = ox + a * math.cos(t), oy - b * math.sin(t)
        f.append(line(QX, QY, fx, fy, color=POS, sw=1.7))
        f.append(circle(fx, fy, 4.5, fill=POS, stroke=POS))
    f.append(circle(QX, QY, 5.5, fill=INK, stroke=INK))
    f.append(text(QX + 12, QY - 10, "Q", size=15, bold=True, anchor="start"))

    f.append(fitbox(596, 92, 280, 306,
                    "\n".join([
                        "зелена крива — еволюта,",
                        "сірий пунктир — еліпс ρ = 0:",
                        "p² + (1−e²)z² = (e²a)²",
                        "",
                        "у справжніх числах його півосі",
                        "42 698 м і 42 841 м — тобто вся",
                        "область умістилася б у коло",
                        "радіусом 43 км навколо центра",
                        "Землі (h ≈ −6 370 км)",
                        "",
                        "усередині: чотири нормалі,",
                        "чотири «широти», жодна не",
                        "краща за інші — задача не має",
                        "єдиного розв'язку, і кожен",
                        "метод віддає свою гілку",
                    ]), size=12.5, fill="#f7f9fc", stroke=NEG, sw=1.7))
    render(os.path.join(IMG, "inverse-caustic.svg"), W, H, *f)


if __name__ == "__main__":
    ecef_axes()
    normal_and_n()
    local_triad()
    plumb_vs_normal()
    inverse_bowring_geometry()
    inverse_convergence()
    inverse_caustic()
    print("ok")
