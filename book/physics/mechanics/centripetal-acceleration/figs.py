# -*- coding: utf-8 -*-
"""Фігури до теми «Центрострімке прискорення».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def vec(x1, y1, x2, y2, color=INK, sw=2.6, head=12):
    """Кольорова стрілка-вектор із власним наконечником у кольорі лінії."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x2 - ux * head, y2 - uy * head
    nx, ny = -uy, ux
    hw = head * 0.5
    ln = line(x1, y1, bx, by, color=color, sw=sw)
    h = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
         % (x2, y2, bx + nx * hw, by + ny * hw, bx - nx * hw, by - ny * hw, color))
    return ln + h


def arc_between(cx, cy, r, a0_deg, a1_deg, color=INK, sw=1.8):
    """Проста дуга від кута a0 до a1 (градуси, 0°=праворуч, проти год.), без наконечника."""
    a0 = math.radians(a0_deg); a1 = math.radians(a1_deg)
    x0 = cx + r * math.cos(a0); y0 = cy - r * math.sin(a0)
    x1 = cx + r * math.cos(a1); y1 = cy - r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    sweep = 0 if a1_deg > a0_deg else 1
    return ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw))


# ── Фігура 1: рівномірний рух по колу — v дотична, a до центра ────────────────
def fig_uniform():
    W, H = 800, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Рівномірний рух по колу: напрям крутиться — значить, є прискорення",
                  size=16.5, bold=True))

    cx, cy = 330, 262
    R = 150
    f.append(circle(cx, cy, R, fill="#fbfcfe", stroke=MUTED, sw=1.8))
    f.append(circle(cx, cy, 7, fill=INK, stroke=INK, sw=1))
    f.append(text(cx, cy + 24, "центр", size=12, color=MUTED))

    # слабкі стрілки швидкості по колу (той самий модуль, різний напрям)
    for ad in (150, 205, 270, 325):
        a = math.radians(ad)
        Px, Py = cx + R * math.cos(a), cy - R * math.sin(a)
        tx, ty = -math.sin(a), -math.cos(a)          # дотична CCW
        f.append(vec(Px, Py, Px + tx * 40, Py + ty * 40, color="#c3cbd6", sw=2.2, head=9))

    # головна точка P (угорі-праворуч)
    a = math.radians(52)
    P = (cx + R * math.cos(a), cy - R * math.sin(a))
    f.append(circle(P[0], P[1], 7, fill=INK, stroke=INK, sw=1))

    tx, ty = -math.sin(a), -math.cos(a)              # напрям руху (дотична CCW)
    nx, ny = ty, -tx                                  # нормаль назовні (угору-праворуч)
    # v — дотична, уперед
    vtip = (P[0] + tx * 80, P[1] + ty * 80)
    f.append(vec(P[0], P[1], vtip[0], vtip[1], color=INK, sw=3.0, head=13))
    vmid = (P[0] + tx * 42, P[1] + ty * 42)
    f.append(text(vmid[0] + nx * 20, vmid[1] + ny * 20 + 5, "v", size=18, bold=True,
                  italic=True, color=INK))

    # a — до центра
    ux, uy = (cx - P[0]), (cy - P[1])
    Lc = math.hypot(ux, uy); ux, uy = ux / Lc, uy / Lc
    f.append(vec(P[0], P[1], P[0] + ux * 86, P[1] + uy * 86, color=NEG, sw=3.2, head=14))
    ma = (P[0] + ux * 90, P[1] + uy * 90)
    f.append(text(ma[0] - 6, ma[1] + 18, "a = v²/r", size=15, bold=True, color=NEG, anchor="end"))
    f.append(text(ma[0] - 6, ma[1] + 36, "(до центра)", size=11.5, color=NEG, anchor="end"))

    # пунктир-дотична — ПРОДОВЖЕННЯ за кінцем v (куди полетить, якщо прибрати силу)
    fend = (vtip[0] + tx * 120, vtip[1] + ty * 120)
    f.append(line(vtip[0], vtip[1], fend[0], fend[1], color=POS, sw=2.0, dash="7,6"))
    fmid = ((vtip[0] + fend[0]) / 2, (vtip[1] + fend[1]) / 2)
    lab = (fmid[0] + nx * 40, fmid[1] + ny * 40)
    f.append(text(lab[0], lab[1], "полетить по дотичній", size=11.5, color=POS, anchor="middle"))
    f.append(text(lab[0], lab[1] + 17, "(а не «назовні»)", size=11.5, color=POS, anchor="middle"))

    b, w, h = textbox(W / 2, H - 34,
                      "|v| сталий  ·  напрям щомиті інший  →  вектор швидкості змінюється  →  є прискорення до центра",
                      size=13, pad=10, fill="#eef3fb", stroke=NEG, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "uniform-circular.svg"), W, H, *f)


# ── Фігура 2: виведення a = v²/r через подібні трикутники ─────────────────────
def fig_derivation():
    W, H = 880, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Звідки v²/r: два подібні трикутники", size=17, bold=True))

    # ── ЛІВОРУЧ: положення на колі, кут Δθ між радіусами ──
    O = (215, 268)
    R = 140
    f.append(text(O[0], 78, "положення (радіуси)", size=12.5, color=MUTED, bold=True))
    f.append(circle(O[0], O[1], R, fill="#fbfcfe", stroke="#dfe4ea", sw=1.6))
    f.append(circle(O[0], O[1], 6, fill=INK, stroke=INK, sw=1))

    a1d, a2d = 58, 104
    a1, a2 = math.radians(a1d), math.radians(a2d)
    P1 = (O[0] + R * math.cos(a1), O[1] - R * math.sin(a1))
    P2 = (O[0] + R * math.cos(a2), O[1] - R * math.sin(a2))
    f.append(vec(O[0], O[1], P1[0], P1[1], color=INK, sw=2.4, head=11))
    f.append(vec(O[0], O[1], P2[0], P2[1], color=INK, sw=2.4, head=11))
    f.append(text((O[0] + P1[0]) / 2 + 12, (O[1] + P1[1]) / 2 + 8, "r", size=15, bold=True,
                  italic=True, color=INK))
    f.append(text((O[0] + P2[0]) / 2 - 14, (O[1] + P2[1]) / 2 + 2, "r", size=15, bold=True,
                  italic=True, color=INK, anchor="end"))
    # хорда між положеннями
    f.append(line(P1[0], P1[1], P2[0], P2[1], color=POS, sw=2.4, dash="5,4"))
    f.append(text((P1[0] + P2[0]) / 2 - 4, (P1[1] + P2[1]) / 2 - 10, "хорда ≈ v·Δt",
                  size=12, bold=True, color=POS, anchor="middle"))
    # кут Δθ при центрі
    f.append(arc_between(O[0], O[1], 42, a1d, a2d, color=FIELD, sw=2.2))
    f.append(text(O[0] + 20, O[1] - 40, "Δθ", size=14, bold=True, italic=True, color=FIELD))

    # ── ПРАВОРУЧ: трикутник швидкостей ──
    T = (600, 322)
    f.append(text(650, 78, "швидкості (той самий кут Δθ)", size=12.5, color=MUTED, bold=True))
    Lv = 150
    b1 = math.radians(20)                            # v1 вправо-вниз
    b2 = math.radians(-22)                           # v2 вправо-вгору (провернута на Δθ)
    A = (T[0] + Lv * math.cos(b1), T[1] + Lv * math.sin(b1))
    Bb = (T[0] + Lv * math.cos(b2), T[1] + Lv * math.sin(b2))
    f.append(vec(T[0], T[1], A[0], A[1], color=INK, sw=2.8, head=13))
    f.append(vec(T[0], T[1], Bb[0], Bb[1], color=INK, sw=2.8, head=13))
    f.append(text((T[0] + A[0]) / 2 - 2, (T[1] + A[1]) / 2 + 20, "v", size=15, bold=True,
                  italic=True, color=INK))
    f.append(text((T[0] + Bb[0]) / 2 - 2, (T[1] + Bb[1]) / 2 - 12, "v", size=15, bold=True,
                  italic=True, color=INK))
    # Δv — між кінцями стрілок
    f.append(vec(A[0], A[1], Bb[0], Bb[1], color=NEG, sw=2.8, head=13))
    f.append(text(A[0] + 20, (A[1] + Bb[1]) / 2 + 4, "Δv", size=15, bold=True, italic=True,
                  color=NEG, anchor="start"))
    # кут Δθ при вершині T
    f.append(arc_between(T[0], T[1], 40, -22, 20, color=FIELD, sw=2.2))
    f.append(text(T[0] + 52, T[1] + 4, "Δθ", size=14, bold=True, italic=True, color=FIELD,
                  anchor="start"))

    # ── ланцюг виведення внизу ──
    b, w, h = textbox(W / 2, H - 40,
                      "рівнобедрені, спільний кут Δθ  →  подібні  →  Δv / v = хорда / r = v·Δt / r"
                      "     ⟹     a = Δv/Δt = v² / r",
                      size=13, pad=11, fill="#f0f6f1", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "derivation-triangles.svg"), W, H, *f)


# ── Фігура 3: одна роль — різні виконавці (натяг / тяжіння / тертя) ───────────
def fig_roles():
    W, H = 940, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Доцентрова сила — це роль: різні сили, усі до центра",
                  size=17, bold=True))

    cols = [(168, "Камінець на нитці", "натяг", "рука"),
            (470, "Супутник на орбіті", "тяжіння", "Земля"),
            (772, "Машина в повороті", "тертя", "центр дуги")]
    cy = 212
    R = 66

    for (cx, title, force, hub) in cols:
        f.append(text(cx, 78, title, size=13.5, bold=True, color=INK))
        # коло-траєкторія
        f.append(circle(cx, cy, R, fill="#fbfcfe", stroke="#dfe4ea", sw=1.6))
        # центр-«виконавець»
        if hub == "Земля":
            f.append(circle(cx, cy, 13, fill="#dfeaf7", stroke=NEG, sw=1.8))
        else:
            f.append(circle(cx, cy, 5, fill=INK, stroke=INK, sw=1))
        f.append(text(cx, cy + 30, hub, size=11, color=MUTED))

        # тіло на колі (угорі)
        ang = math.radians(90)
        Bx, By = cx + R * math.cos(ang), cy - R * math.sin(ang)
        f.append(circle(Bx, By, 8, fill=POS if hub != "Земля" else FIELD, stroke=INK, sw=1.3))
        # ниточка/радіус для наочності (тонка)
        f.append(line(cx, cy, Bx, By, color="#cbd2dc", sw=1.4, dash="4,4"))

        # доцентрова стрілка (тіло → центр)
        f.append(vec(Bx, By, Bx, By + 46, color=NEG, sw=3.0, head=13))
        f.append(text(cx + 12, By + 30, force, size=13, bold=True, color=NEG, anchor="start"))

        # пунктир-дотична (полетить прямо)
        f.append(line(Bx, By, Bx - 78, By, color=POS, sw=1.8, dash="6,5"))
        f.append(text(Bx - 40, By - 8, "дотична", size=10.5, color=POS, anchor="middle"))

        # підпис-величина
        f.append(text(cx, cy + R + 44, "= m·v²/r", size=13, bold=True, color=INK))

    b, w, h = textbox(W / 2, H - 36,
                      "Різні сили — одна роль: усі показують до центра й дорівнюють m·v²/r.\n"
                      "Зникне сила — тіло піде по дотичній, а не «назовні».",
                      size=12.5, pad=10, fill="#fdecea", stroke=POS, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "centripetal-roles.svg"), W, H, *f)


# ── Фігура 4 (вставка): хорда проти дуги — чесний перехід у границі ───────────
def fig_chord_arc():
    W, H = 840, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Хорда ≠ дуга: різниця другого порядку зникає в границі",
                  size=16.5, bold=True))

    O = (420, 500)
    R = 320
    a1d, a2d = 66, 114                      # відкритий кут ~48°, щоб хорда й дуга помітно різнились
    a1, a2 = math.radians(a1d), math.radians(a2d)
    P1 = (O[0] + R * math.cos(a1), O[1] - R * math.sin(a1))
    P2 = (O[0] + R * math.cos(a2), O[1] - R * math.sin(a2))

    f.append(circle(O[0], O[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(text(O[0], O[1] + 22, "центр", size=12, color=MUTED))
    # два радіуси
    f.append(line(O[0], O[1], P1[0], P1[1], color=INK, sw=2.2))
    f.append(line(O[0], O[1], P2[0], P2[1], color=INK, sw=2.2))
    f.append(text((O[0] + P1[0]) / 2 + 16, (O[1] + P1[1]) / 2 + 6, "r", size=15, bold=True,
                  italic=True, color=INK))
    f.append(text((O[0] + P2[0]) / 2 - 16, (O[1] + P2[1]) / 2 + 6, "r", size=15, bold=True,
                  italic=True, color=INK, anchor="end"))
    # точки P1, P2
    f.append(circle(P1[0], P1[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(circle(P2[0], P2[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(text(P1[0] + 16, P1[1] + 4, "P₁", size=13, bold=True, color=INK, anchor="start"))
    f.append(text(P2[0] - 16, P2[1] - 4, "P₂", size=13, bold=True, color=INK, anchor="end"))
    # дуга (пройдений шлях) — виділена зеленим, товща
    f.append(arc_between(O[0], O[1], R, a1d, a2d, color=FIELD, sw=4.2))
    amid = math.radians((a1d + a2d) / 2)
    aL = (O[0] + (R + 30) * math.cos(amid), O[1] - (R + 30) * math.sin(amid))
    f.append(text(aL[0], aL[1] - 4, "дуга = r·Δθ = v·Δt", size=13.5, bold=True, color=FIELD))
    # хорда — червона пунктирна
    f.append(line(P1[0], P1[1], P2[0], P2[1], color=POS, sw=2.6, dash="6,5"))
    cmid = ((P1[0] + P2[0]) / 2, (P1[1] + P2[1]) / 2)
    f.append(text(cmid[0], cmid[1] + 26, "хорда = 2r·sin(Δθ/2)", size=13.5, bold=True,
                  color=POS))
    # кут Δθ при центрі
    f.append(arc_between(O[0], O[1], 54, a1d, a2d, color=NEG, sw=2.4))
    f.append(text(O[0], O[1] - 66, "Δθ", size=15, bold=True, italic=True, color=NEG))

    b, w, h = textbox(W / 2, H - 30,
                      "хорда / дуга = sin(Δθ/2)/(Δθ/2) = 1 − (Δθ)²/24 + …   →   1   при  Δθ → 0",
                      size=13.5, pad=11, fill="#eef3fb", stroke=NEG, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "chord-arc-limit.svg"), W, H, *f)


# ── Фігура 5 (вставка): r, v, a — кожне диференціювання повертає на +90° ───────
def fig_rotating_vectors():
    W, H = 800, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Диференціюємо r(t) двічі: a = −ω²·r дивиться строго до центра",
                  size=16, bold=True))

    # ── ЛІВОРУЧ: коло з реальними r, v, a у точці P ──
    O = (295, 300)
    R = 150
    f.append(circle(O[0], O[1], R, fill="#fbfcfe", stroke="#dfe4ea", sw=1.6))
    f.append(circle(O[0], O[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(text(O[0], O[1] + 22, "центр", size=11.5, color=MUTED))

    ad = 57
    a = math.radians(ad)
    P = (O[0] + R * math.cos(a), O[1] - R * math.sin(a))
    # r: центр → P
    f.append(vec(O[0], O[1], P[0], P[1], color=INK, sw=2.8, head=13))
    rm = (O[0] + 0.52 * R * math.cos(a), O[1] - 0.52 * R * math.sin(a))
    f.append(text(rm[0] - 16, rm[1], "r", size=17, bold=True, italic=True, color=INK,
                  anchor="end"))
    f.append(circle(P[0], P[1], 6, fill=INK, stroke=INK, sw=1))
    # v: дотична (CCW), +90° від r
    tx, ty = -math.sin(a), -math.cos(a)
    vt = (P[0] + tx * 92, P[1] + ty * 92)
    f.append(vec(P[0], P[1], vt[0], vt[1], color=NEG, sw=2.8, head=13))
    f.append(text(vt[0] - 6, vt[1] - 10, "v = ω·r", size=14, bold=True, italic=True,
                  color=NEG, anchor="end"))
    # a: до центра, = −ω²r
    ux, uy = (O[0] - P[0]), (O[1] - P[1])
    Lc = math.hypot(ux, uy); ux, uy = ux / Lc, uy / Lc
    at = (P[0] + ux * 92, P[1] + uy * 92)
    f.append(vec(P[0], P[1], at[0], at[1], color=POS, sw=3.0, head=14))
    f.append(text(at[0] + 12, at[1] + 6, "a = −ω²·r", size=14, bold=True, italic=True,
                  color=POS, anchor="start"))

    # ── ПРАВОРУЧ: фазовий годинник — три стрілки з одного початку, +90° крок ──
    Q = (612, 292)
    f.append(text(Q[0], 112, "кожне d/dt: поворот на +90°", size=12.5, color=MUTED, bold=True))
    L = 78
    f.append(circle(Q[0], Q[1], 4, fill=INK, stroke=INK, sw=1))
    # r → праворуч
    f.append(vec(Q[0], Q[1], Q[0] + L, Q[1], color=INK, sw=2.6, head=12))
    f.append(text(Q[0] + L + 14, Q[1] + 5, "r", size=15, bold=True, italic=True, color=INK))
    # v → угору (+90°)
    f.append(vec(Q[0], Q[1], Q[0], Q[1] - L, color=NEG, sw=2.6, head=12))
    f.append(text(Q[0] + 6, Q[1] - L - 8, "v", size=15, bold=True, italic=True, color=NEG,
                  anchor="start"))
    # a → ліворуч (+180° від r = −r)
    f.append(vec(Q[0], Q[1], Q[0] - L, Q[1], color=POS, sw=2.8, head=13))
    f.append(text(Q[0] - L - 14, Q[1] + 5, "a", size=15, bold=True, italic=True, color=POS,
                  anchor="end"))
    f.append(text(Q[0], Q[1] + 44, "a протилежне r", size=12.5, bold=True, color=POS))

    b, w, h = textbox(W / 2, H - 30,
                      "r(t) = R·(cos ωt, sin ωt)   →   v = dr/dt ⊥ r   →   a = d²r/dt² = −ω²·r   "
                      "(|a| = ω²r = v²/r)",
                      size=13, pad=11, fill="#fdecea", stroke=POS, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "rotating-vectors.svg"), W, H, *f)


# ── Фігура 6 (вставка): оскулярне коло — v²/r для будь-якої кривої ────────────
def fig_osculating():
    W, H = 860, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Кривина: v²/r працює для будь-якої кривої, r — місцевий радіус",
                  size=16, bold=True))

    # хвиляста крива y = cy0 - A*sin(k*(x-x0))
    cy0, A = 250, 58
    x0 = 150
    k = 2 * math.pi / 360.0
    def yc(x):
        return cy0 - A * math.sin(k * (x - x0))
    xs = [x for x in range(120, 740, 4)]
    pts = " ".join("%.1f,%.1f" % (x, yc(x)) for x in xs)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.0"/>'
             % (pts, INK))
    f.append(text(715, yc(715) - 14, "траєкторія", size=12.5, color=MUTED, anchor="middle"))

    # точка P на висхідному схилі (не на вершині — щоб коло стояло під кутом)
    xP = 255
    yP = yc(xP)
    # нахил чисельно
    dydx = (yc(xP + 1) - yc(xP - 1)) / 2.0
    # одиничний дотичний та нормаль (нормаль у бік угнутості = вниз, +y)
    tl = math.hypot(1.0, dydx)
    tux, tuy = 1.0 / tl, dydx / tl
    nux, nuy = tuy, -tux
    if nuy < 0:                                  # нормаль має дивитися до центра (вниз)
        nux, nuy = -nux, -nuy
    # радіус кривини (для наочності беремо фіксований показовий)
    rc = 150
    C = (xP + nux * rc, yP + nuy * rc)
    # оскулярне коло (світле)
    f.append(circle(C[0], C[1], rc, fill="none", stroke="#b9c6f0", sw=2.0))
    f.append(circle(C[0], C[1], 5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(C[0] + 10, C[1] + 18, "центр кривини", size=11.5, color=NEG, anchor="start"))
    f.append(circle(xP, yP, 6, fill=INK, stroke=INK, sw=1))
    f.append(text(xP - 12, yP - 12, "P", size=14, bold=True, color=INK, anchor="end"))

    # радіус r від центра до P (пунктир) з підписом
    f.append(line(C[0], C[1], xP, yP, color=NEG, sw=1.8, dash="6,5"))
    rmx, rmy = (C[0] + xP) / 2, (C[1] + yP) / 2
    f.append(text(rmx + 14, rmy, "r", size=15, bold=True, italic=True, color=NEG,
                  anchor="start"))

    # a_n: P → центр (червона), уздовж нормалі
    f.append(vec(xP, yP, xP + nux * 84, yP + nuy * 84, color=POS, sw=3.0, head=13))
    f.append(text(xP + nux * 84 - 10, yP + nuy * 84 + 6, "a_n = v²/r", size=13.5, bold=True,
                  italic=True, color=POS, anchor="end"))
    # v: дотична (зелена)
    f.append(vec(xP, yP, xP + tux * 96, yP + tuy * 96, color=FIELD, sw=2.6, head=12))
    f.append(text(xP + tux * 96 + 8, yP + tuy * 96 - 6, "v", size=14, bold=True, italic=True,
                  color=FIELD, anchor="start"))
    # напис «оскулярне коло»
    f.append(text(C[0] + rc * 0.62, C[1] - rc * 0.80, "оскулярне коло", size=12,
                  color="#7a8bc4", anchor="middle"))

    b, w, h = textbox(W / 2, H - 28,
                      "κ = dθ/ds = 1/r   ·   a_n = κ·v² = v²/r   ·   пряма: κ = 0, r → ∞, a_n = 0",
                      size=13, pad=11, fill="#f0f6f1", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "osculating-circle.svg"), W, H, *f)


# ── Фігура 7 (вставка hist): часова стрічка двох слів ─────────────────────────
def fig_history():
    W, H = 1000, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Дві назви — у зворотному до логіки порядку", size=17, bold=True))

    # легенда напрямів + етимологія (справа вгорі)
    f.append(text(700, 74, "vis centrifuga → назовні (fugere — тікати)",
                  size=12, color=POS, anchor="start", bold=True))
    f.append(text(700, 96, "vis centripeta → до центра (petere — прагнути)",
                  size=12, color=NEG, anchor="start", bold=True))

    # вісь часу
    axy = 250
    f.append(line(105, axy, 905, axy, color=INK, sw=2.6))
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
             % (915, axy, 905, axy - 6, 905, axy + 6, INK))
    f.append(text(902, 240, "час", size=11.5, color=MUTED, anchor="end", italic=True))

    def X(year):
        return 90 + (year - 1650) * (820.0 / 45.0)

    # ── Гюйгенс (назовні, червоне) — угорі ──
    x59 = X(1659)
    f.append(circle(x59, axy, 6.5, fill=POS, stroke=POS, sw=1))
    f.append(text(x59, axy + 22, "1659", size=12.5, color=INK, bold=True))
    f.append(line(x59, axy - 6, x59, 148, color=POS, sw=1.5))
    b, w, h = textbox(x59, 110,
                      "1659 · Гюйгенс, «De vi centrifuga»\nгеометрично виводить v²/r\n"
                      "і називає силу vis centrifuga\n(рукопис; надрук. посмертно 1703)",
                      size=11, pad=8, fill="#fdecea", stroke=POS, sw=1.4, color=INK)
    f.append(b)

    x73 = X(1673)
    f.append(circle(x73, axy, 6.5, fill=POS, stroke=POS, sw=1))
    f.append(text(x73, axy + 22, "1673", size=12.5, color=INK, bold=True))
    f.append(line(x73, axy - 6, x73, 213, color=POS, sw=1.5))
    b, w, h = textbox(x73, 190,
                      "1673 · «Horologium Oscillatorium»\n13 теорем — без доведень",
                      size=11, pad=8, fill="#fdecea", stroke=POS, sw=1.4, color=INK)
    f.append(b)

    # ── Ньютон (до центра, синє) — унизу ──
    x84 = X(1684)
    f.append(circle(x84, axy, 6.5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(x84, axy - 12, "1684", size=12.5, color=INK, bold=True))
    f.append(line(x84, axy + 6, x84, 305, color=NEG, sw=1.5))
    b, w, h = textbox(x84, 340,
                      "1684 · Ньютон, «De motu corporum»\nназиває vis centripeta — до центра\n"
                      "(канонізовано в «Principia», 1687)",
                      size=11, pad=8, fill="#eaf0fd", stroke=NEG, sw=1.4, color=INK)
    f.append(b)

    # ── підсумок (унизу ліворуч, зелена рамка) ──
    b, w, h = textbox(300, 375,
                      "Логіка й історія розходяться:\nвідцентрову назвали ПЕРШОЮ (1659),\n"
                      "а доцентрову — аж через 25 років (1684).",
                      size=12, pad=10, fill="#eefaf1", stroke=FIELD, sw=1.5, color=INK, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "two-words-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_uniform(), fig_derivation(), fig_roles(),
          fig_chord_arc(), fig_rotating_vectors(), fig_osculating(),
          fig_history()]
    print("written:")
    for p in ps:
        print("  ", p)
