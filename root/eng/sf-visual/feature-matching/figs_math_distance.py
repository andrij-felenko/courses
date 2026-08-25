# -*- coding: utf-8 -*-
# Фігури для вставки math-descriptor-distance.md.
# Окремий файл, щоб не чіпати основний figs.py теми; вивід у той самий ./img.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOOD = "#16a34a"
BAD  = "#c0392b"
NEARC = "#2457d6"   # розподіл відстані до ПРАВИЛЬНОГО сусіда
RANDC = "#c0392b"   # розподіл відстані до ВИПАДКОВОГО сусіда


# ── two-distributions: чому проба відношення працює ────────────────────────────
# Ідея: відстань дескриптора до ПРАВИЛЬНОГО сусіда розподілена низько (лівий горб),
# до найкращого ВИПАДКОВОГО сусіда — високо (правий горб). Проба відношення d1/d2
# фактично питає, з якого горба взявся найближчий кандидат.
def fig_two_distributions():
    W, H = 760, 400
    p = []
    # осі
    ox, oy = 70, 300          # початок координат (лівий-нижній кут поля графіка)
    axw, axh = 620, 232
    p.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.6))          # вісь X
    p.append(line(ox, oy, ox, oy - axh, color=INK, sw=1.6))          # вісь Y
    p.append(text(ox + axw / 2, oy + 44, "відстань між дескрипторами (менша = схожіші)",
                  size=11, color=INK))
    p.append(text(ox - 46, oy - axh / 2, "як часто", size=11, color=INK, anchor="middle"))

    # дві дзвоноподібні криві (гаусоїди), намальовані як polyline
    def gauss(mu, sig, amp):
        pts = []
        for k in range(0, axw + 1, 4):
            xx = k / axw            # 0..1 уздовж осі
            val = amp * math.exp(-((xx - mu) ** 2) / (2 * sig * sig))
            px = ox + k
            py = oy - val * axh
            pts.append((px, py))
        return pts

    def poly(pts, col, sw=2.4, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        pth = " ".join("%.1f,%.1f" % q for q in pts)
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (pth, col, sw, d))

    def fillpoly(pts, col, alpha="0.10"):
        pth = ("%.1f,%.1f " % (pts[0][0], oy)) + \
              " ".join("%.1f,%.1f" % q for q in pts) + \
              (" %.1f,%.1f" % (pts[-1][0], oy))
        return '<polygon points="%s" fill="%s" fill-opacity="%s" stroke="none"/>' % (pth, col, alpha)

    left = gauss(0.20, 0.075, 0.92)     # правильний сусід: близько, вузько
    right = gauss(0.68, 0.13, 0.72)     # найкращий випадковий: далеко, широко
    p.append(fillpoly(left, NEARC, "0.12"))
    p.append(fillpoly(right, RANDC, "0.10"))
    p.append(poly(left, NEARC))
    p.append(poly(right, RANDC, dash="6,4"))

    # підписи горбів
    p.append(text(ox + 0.20 * axw, oy - 0.92 * axh - 12, "правильний сусід",
                  size=11, color=NEARC, bold=True))
    p.append(text(ox + 0.20 * axw, oy - 0.92 * axh + 6, "(та сама точка сцени)",
                  size=9, color=NEARC))
    p.append(text(ox + 0.68 * axw, oy - 0.72 * axh - 12, "найкращий випадковий",
                  size=11, color=RANDC, bold=True))
    p.append(text(ox + 0.68 * axw, oy - 0.72 * axh + 6, "(чужа точка-двійник)",
                  size=9, color=RANDC))

    # зона перекриття — де живе хиба
    ovx = ox + 0.44 * axw
    p.append(line(ovx, oy, ovx, oy - 0.30 * axh, color=MUTED, sw=1.2, dash="3,3"))
    p.append(text(ovx, oy - 0.30 * axh - 8, "перекриття", size=9, color=MUTED))
    p.append(text(ovx, oy - 0.30 * axh + 6, "тут d₁≈d₂", size=9, color=MUTED))

    p.append(fitbox(46, 336, W - 62, 46,
                    "До ПРАВИЛЬНОГО сусіда відстань мала (лівий вузький горб); до найкращого "
                    "ВИПАДКОВОГО — велика (правий широкий).\nПроба відношення d₁/d₂ питає: "
                    "найближчий кандидат — з лівого горба (мале d₁ на тлі великого d₂) чи з правого "
                    "(обидва великі)?",
                    size=10, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "two-distributions.svg"), W, H, *p,
           title="Чому працює проба відношення: два розподіли відстаней")


if __name__ == "__main__":
    fig_two_distributions()
    print("OK:", OUT)
