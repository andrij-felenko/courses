# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _poly(pts, fill, stroke, sw=2):
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (s, fill, stroke, sw))


def _rot(px, py, cx, cy, ang):
    """Повернути точку (px,py) навколо (cx,cy) на кут ang (рад, за годинниковою)."""
    s, c = math.sin(ang), math.cos(ang)
    dx, dy = px - cx, py - cy
    return (cx + dx * c - dy * s, cy + dx * s + dy * c)


# ── Фігура: сторож перекиду — геометрія критичного кута + крива придушення ──
def f_tipover():
    W, H = 860, 440
    frags = []

    # ── ЛІВА ПАНЕЛЬ: вид з торця на косогорі, критичний кут ──────────────
    frags.append(text(215, 30, "Геометрія перекиду (вид з торця)",
                      size=16, bold=True))

    # рівень землі (нахилений косогір) — малюємо ПОВОРОТОМ усієї сцени
    # осі коліс у «рівній» системі, тоді повертаємо на phi_crit
    phi = math.atan2(0.15, 0.12)          # ≈ 51.3° — критичний кут
    px_m = 240                            # px на метр
    b = 0.30                              # колія, м
    hc = 0.12                             # висота ЦМ, м

    # опорна точка повороту — нижнє (ліве) колесо на "землі"
    pivot_x, pivot_y = 150, 340

    # колія по горизонталі, колеса на кінцях (у рівній системі)
    wl = (pivot_x, pivot_y)               # ліве (нижнє) колесо
    wr = (pivot_x + b * px_m, pivot_y)    # праве (верхнє) колесо
    # центр мас: над серединою колії на висоті h
    cm = (pivot_x + b * px_m / 2, pivot_y - hc * px_m)

    # повертаємо всю сцену навколо pivot на phi (проти годинникової -> нижнє ліве)
    ang = -phi
    wlr = _rot(*wl, pivot_x, pivot_y, ang)
    wrr = _rot(*wr, pivot_x, pivot_y, ang)
    cmr = _rot(*cm, pivot_x, pivot_y, ang)

    # горизонт (справжня земля) — горизонтальна лінія через pivot
    frags.append(line(70, pivot_y, 400, pivot_y, color=MUTED, sw=1.4, dash="5 4"))
    frags.append(text(396, pivot_y + 17, "горизонт", size=10, color=MUTED, anchor="end"))

    # схил (нахилена поверхня) — від pivot угору-праворуч
    slope_end = _rot(pivot_x + 0.34 * px_m, pivot_y, pivot_x, pivot_y, ang)
    frags.append(line(pivot_x, pivot_y, slope_end[0], slope_end[1], color=LINE, sw=2))

    # рама (нахилений корпус) як чотирикутник над віссю коліс
    ry = hc * px_m * 0.5                  # напіввисота корпусу для малюнка
    corners = [
        (wl[0] - 8, wl[1] - 4),
        (wr[0] + 8, wr[1] - 4),
        (wr[0] + 8, wr[1] - hc * px_m - 6),
        (wl[0] - 8, wl[1] - hc * px_m - 6),
    ]
    cr = [_rot(x, y, pivot_x, pivot_y, ang) for (x, y) in corners]
    frags.append(_poly(cr, fill="#eef1f5", stroke=LINE, sw=2))

    # колеса
    for (wx, wy) in (wlr, wrr):
        frags.append(circle(wx, wy, 14, fill="#e3e7ec", stroke=INK, sw=2))
        frags.append(circle(wx, wy, 3, fill=INK, stroke=INK, sw=1))

    # центр мас — маркер, і підпис ВИНЕСЕНО праворуч у порожнечу з виноскою,
    # щоб не наповзати на нахилений корпус і лінію схилу
    frags.append(circle(cmr[0], cmr[1], 8, fill="#fff", stroke=INK, sw=2.2))
    frags.append(line(cmr[0] - 8, cmr[1], cmr[0] + 8, cmr[1], color=INK, sw=2))
    frags.append(line(cmr[0], cmr[1] - 8, cmr[0], cmr[1] + 8, color=INK, sw=2))
    frags.append(text(250, 250, "центр мас", size=11, bold=True, anchor="start"))

    # вертикаль тяжіння з ЦМ униз — на критичному куті проходить над нижнім колесом
    frags.append(line(cmr[0], cmr[1], cmr[0], pivot_y + 26, color=POS, sw=2, dash="4 3"))
    frags.append(text(cmr[0] + 6, pivot_y + 22, "вага", size=11, color=POS,
                      anchor="start", bold=True))

    # плече b/2 (горизонтальне) і h (вертикальне) у РІВНІЙ системі — довідково,
    # малюємо тонко в рівній системі осторонь, щоб показати означення
    ref_x, ref_y = 470, 300
    frags.append(line(ref_x, ref_y, ref_x + b * px_m / 2, ref_y, color=NEG, sw=1.6))
    frags.append(text(ref_x + b * px_m / 4, ref_y + 16, "b/2", size=12, color=NEG,
                      bold=True))
    frags.append(line(ref_x, ref_y, ref_x, ref_y - hc * px_m, color=FIELD, sw=1.6))
    frags.append(text(ref_x - 8, ref_y - hc * px_m / 2, "h", size=12, color=FIELD,
                      bold=True, anchor="end", italic=True))
    # гіпотенуза й позначка кута
    frags.append(line(ref_x, ref_y - hc * px_m, ref_x + b * px_m / 2, ref_y,
                      color=INK, sw=1.4, dash="3 3"))
    frags.append(circle(ref_x, ref_y, 3, fill=INK, stroke=INK, sw=1))

    # підпис критичного кута — окремим рядком, з запасом, поза лініями
    box, bw, bh = textbox(210, 405, "φ_crit = arctan( (b/2) / h ) ≈ 51°",
                          size=13, fill="#fff7ec", stroke=POS, bold=True, pad=9)
    frags.append(box)

    # ── ПРАВА ПАНЕЛЬ: множник придушення від запасу ──────────────────────
    frags.append(text(650, 30, "Придушення керування від запасу",
                      size=16, bold=True))

    # осі
    gx0, gy0 = 560, 360          # початок (нуль)
    gw, gh = 240, 250            # ширина/висота поля графіка
    gx1, gy1 = gx0 + gw, gy0 - gh

    frags.append(line(gx0, gy0, gx1, gy0, color=INK, sw=1.8))     # X
    frags.append(line(gx0, gy0, gx0, gy1, color=INK, sw=1.8))     # Y
    frags.append(text(gx0 + gw / 2, gy0 + 34, "запас margin  (0 → межа 1)",
                      size=11, color=MUTED))
    # підпис осі Y — вертикально осторонь, щоб не наповзав на криві
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" '
                 'fill="%s" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">'
                 'множник 0..1</text>' % (gx0 - 34, gy0 - gh / 2, FONT, MUTED,
                                          gx0 - 34, gy0 - gh / 2))

    # позначки 0 / DEAD / 1 по X
    def X(m): return gx0 + m * gw
    def Y(v): return gy0 - v * gh
    for m, lab in ((0.0, "0"), (0.5, "0.5"), (1.0, "1")):
        frags.append(line(X(m), gy0, X(m), gy0 + 5, color=INK, sw=1.4))
        frags.append(text(X(m), gy0 + 19, lab, size=11, color=INK))
    frags.append(text(gx0 - 12, Y(1.0) + 4, "1", size=11, color=INK,
                      anchor="end"))

    DEAD = 0.5
    # крива ГАЗУ: 1 до DEAD, далі лінійно до 0 на margin=1
    thr = []
    m = 0.0
    while m <= 1.0001:
        v = 1.0 if m <= DEAD else (1.0 - m) / (1.0 - DEAD)
        thr.append((X(m), Y(v)))
        m += 0.02
    dthr = "M " + " L ".join("%.1f %.1f" % p for p in thr)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (dthr, NEG))

    # крива ПОВОРОТУ: k² (той самий k, у квадраті) — завжди нижче газу
    trn = []
    m = 0.0
    while m <= 1.0001:
        k = 1.0 if m <= DEAD else (1.0 - m) / (1.0 - DEAD)
        trn.append((X(m), Y(k * k)))
        m += 0.02
    dtrn = "M " + " L ".join("%.1f %.1f" % p for p in trn)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6" '
                 'stroke-dasharray="6 4"/>' % (dtrn, POS))

    # вертикаль DEAD (край спокійної зони)
    frags.append(line(X(DEAD), gy0, X(DEAD), Y(1.0), color=MUTED, sw=1.2, dash="3 3"))

    # підписи кривих — у порожньому нижньому-лівому куті графіка (під кривими),
    # з кольоровим зразком лінії ліворуч; поза всіма кривими й осями
    lx = X(0.06)
    ly1, ly2 = Y(0.42), Y(0.26)
    frags.append(line(lx, ly1, lx + 26, ly1, color=NEG, sw=2.6))
    frags.append(text(lx + 33, ly1 + 4, "газ  × k  (лінійно)", size=11.5,
                      color=NEG, bold=True, anchor="start"))
    frags.append(line(lx, ly2, lx + 26, ly2, color=POS, sw=2.6, dash="6 4"))
    frags.append(text(lx + 33, ly2 + 4, "поворот  × k²", size=11.5,
                      color=POS, bold=True, anchor="start"))

    # позначка спокійної зони — підпис під віссю, у власному просторі
    box2, bw2, bh2 = textbox(X(0.25), Y(1.0) - 16,
                             "спокійна зона", size=11,
                             fill="#eafaf0", stroke=FIELD, pad=7)
    frags.append(box2)

    render(os.path.join(OUT, 'tipover.svg'), W, H, *frags)
    print("ok: tipover.svg")


if __name__ == '__main__':
    f_tipover()
