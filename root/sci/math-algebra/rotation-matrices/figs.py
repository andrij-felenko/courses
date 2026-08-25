# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Матриці повороту».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: образи базисних векторів ───────────────────────────────────────
# Серце виведення: куди їдуть î та ĵ при повороті на θ. Їхні нові координати —
# це СТОВПЦІ матриці повороту. Показуємо і дугу кута, і пунктирні проєкції на осі,
# щоб (cos θ, sin θ) для î та (−sin θ, cos θ) для ĵ читалися прямо з картинки.
def fig_basis_images():
    W, H = 900, 470
    ox, oy = 250, 360          # початок координат
    L = 230                    # довжина одиничного вектора у пікселях
    th = math.radians(48)      # показовий кут повороту
    parts = []

    # осі
    parts.append(arrow(ox - 30, oy, ox + 360, oy, color=INK, sw=1.8))
    parts.append(arrow(ox, oy + 30, ox, oy - 330, color=INK, sw=1.8))
    parts.append(text(ox + 372, oy + 5, "x", size=16, bold=True))
    parts.append(text(ox + 6, oy - 338, "y", size=16, bold=True))

    # одиничне коло (по ньому ковзають кінці î та ĵ при повороті)
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.2" stroke-dasharray="3,4"/>' % (ox, oy, L, MUTED))

    # вихідні базисні вектори (бліді)
    parts.append(arrow(ox, oy, ox + L, oy, color=MUTED, sw=1.6))
    parts.append(arrow(ox, oy, ox, oy - L, color=MUTED, sw=1.6))
    parts.append(text(ox + L - 14, oy + 22, "î", size=15, italic=True, color=MUTED))
    parts.append(text(ox - 20, oy - L + 16, "ĵ", size=15, italic=True, color=MUTED))

    # образ î': кут θ від осі x  → (cos θ, sin θ)
    ix, iy = ox + L * math.cos(th), oy - L * math.sin(th)
    parts.append(arrow(ox, oy, ix, iy, color=POS, sw=2.4))
    # проєкції î' на осі
    parts.append(line(ix, iy, ix, oy, color=POS, sw=1.1, dash="5,4"))
    parts.append(line(ix, iy, ox, iy, color=POS, sw=1.1, dash="5,4"))
    parts.append(text(ix + 14, iy - 6, "î′", size=16, bold=True, italic=True, color=POS))
    parts.append(text((ox + ix) / 2, oy + 20, "cos θ", size=13, color=POS))
    parts.append(text(ix + 38, (oy + iy) / 2, "sin θ", size=13, color=POS, anchor="start"))

    # образ ĵ': кут θ від осі y, тобто (θ+90°) від осі x → (−sin θ, cos θ)
    jx, jy = ox - L * math.sin(th), oy - L * math.cos(th)
    parts.append(arrow(ox, oy, jx, jy, color=NEG, sw=2.4))
    parts.append(line(jx, jy, jx, oy, color=NEG, sw=1.1, dash="5,4"))
    parts.append(line(jx, jy, ox, jy, color=NEG, sw=1.1, dash="5,4"))
    parts.append(text(jx - 18, jy - 8, "ĵ′", size=16, bold=True, italic=True, color=NEG))
    parts.append(text((ox + jx) / 2 - 6, oy + 20, "−sin θ", size=13, color=NEG))
    parts.append(text(jx - 40, (oy + jy) / 2, "cos θ", size=13, color=NEG, anchor="end"))

    # дуга кута θ для î'
    ar = 56
    parts.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="1.6"/>'
                 % (ox + ar, oy, ar, ar, ox + ar * math.cos(th), oy - ar * math.sin(th), INK))
    parts.append(text(ox + ar + 22, oy - 16, "θ", size=15, italic=True, bold=True))

    # підсумкова рамка зі стовпцями матриці
    box, bw, bh = textbox(W - 168, 96,
                          "стовпці матриці:\nî′ = (cos θ, sin θ)\nĵ′ = (−sin θ, cos θ)",
                          size=13, pad=12, fill="#f4f6f8")
    parts.append(box)

    render("img/basis-rotation.svg", W, H, *parts,
           title="Куди їдуть базисні вектори при повороті на θ")


# ── Фігура 2: поворот довільного вектора ─────────────────────────────────────
# Той самий поворот діє на будь-який вектор: довжина зберігається, кут зростає на θ.
# Показуємо v та його образ v′, дугу θ між ними і збережену довжину r.
def fig_vector_rotation():
    W, H = 880, 460
    ox, oy = 150, 360
    parts = []

    parts.append(arrow(ox - 30, oy, ox + 380, oy, color=INK, sw=1.8))
    parts.append(arrow(ox, oy + 30, ox, oy - 330, color=INK, sw=1.8))
    parts.append(text(ox + 392, oy + 5, "x", size=16, bold=True))
    parts.append(text(ox + 6, oy - 338, "y", size=16, bold=True))

    r = 270
    a0 = math.radians(22)          # початковий кут вектора v
    th = math.radians(46)          # поворот
    a1 = a0 + th

    vx, vy = ox + r * math.cos(a0), oy - r * math.sin(a0)
    wx, wy = ox + r * math.cos(a1), oy - r * math.sin(a1)

    # дуга, по якій ковзає кінець вектора (довжина незмінна)
    parts.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="1.2" stroke-dasharray="3,4"/>'
                 % (vx, vy, r, r, wx, wy, MUTED))

    parts.append(arrow(ox, oy, vx, vy, color=INK, sw=2.2))
    parts.append(arrow(ox, oy, wx, wy, color=FIELD, sw=2.6))
    parts.append(text(vx + 16, vy + 6, "v", size=16, bold=True, italic=True))
    parts.append(text(wx + 14, wy - 6, "v′", size=16, bold=True, italic=True, color=FIELD))

    # підпис незмінної довжини на обох променях
    parts.append(text(ox + r * 0.5 * math.cos(a0) - 6, oy - r * 0.5 * math.sin(a0) - 10,
                      "r", size=14, italic=True, color=MUTED))
    parts.append(text(ox + r * 0.5 * math.cos(a1) - 16, oy - r * 0.5 * math.sin(a1) - 8,
                      "r", size=14, italic=True, color=MUTED))

    # дуга кута повороту θ між v та v′
    ar = 120
    parts.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="1.8"/>'
                 % (ox + ar * math.cos(a0), oy - ar * math.sin(a0), ar, ar,
                    ox + ar * math.cos(a1), oy - ar * math.sin(a1), POS))
    mid = (a0 + a1) / 2
    parts.append(text(ox + (ar + 24) * math.cos(mid), oy - (ar + 24) * math.sin(mid),
                      "θ", size=16, italic=True, bold=True, color=POS))

    box, bw, bh = textbox(W - 196, 92,
                          "поворот зберігає довжину\nі додає θ до кута:\n|v′| = |v|,  кут → кут + θ",
                          size=13, pad=12, fill="#f4f6f8")
    parts.append(box)

    render("img/vector-rotation.svg", W, H, *parts,
           title="Той самий поворот діє на будь-який вектор")


if __name__ == "__main__":
    fig_basis_images()
    fig_vector_rotation()
    print("OK: img/basis-rotation.svg, img/vector-rotation.svg")
