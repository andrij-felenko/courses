# -*- coding: utf-8 -*-
"""Фігури до вставки «Розрахунок енергії заряду та безпечної області»
(math-soa-energy.md) теми «Активний обмежувач пускового струму».

Окремий генератор (не чіпає спільний figs.py теми, який паралельно ведуть
для інших вставок). Запуск:  python figs_soa_energy.py  → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

RED, GRN, BLU = POS, FIELD, NEG


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


# ── A. Незалежність ½CU² від опору ───────────────────────────────────────────
def fig_energy_invariant():
    """Тепло на резисторі ∫i²R dt = ½CU² незалежно від R. Три різні R дають три
    різні криві миттєвої потужності i²R, але площа під кожною — однакова."""
    W, H = 720, 440
    f = []
    x0, y0 = 100, 340
    xr, yt = 670, 90
    f.append(arrow(x0, y0, xr, y0, color=INK, sw=1.8))
    f.append(arrow(x0, y0, x0, yt, color=INK, sw=1.8))
    f.append(text((x0 + xr) / 2, y0 + 34, "час  →", size=12.5, color=INK))
    f.append('<text x="34" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 34 %.1f)">'
             'потужність на резисторі  i²·R  →</text>'
             % ((y0 + yt) / 2, FONT, INK, (y0 + yt) / 2))
    f.append(text(W / 2, yt - 24, "Площа під кожною кривою однакова: ½·C·U²",
                  size=14, bold=True, color=INK))

    tw = xr - x0 - 30
    Pmax = yt + 24
    # i²R = (U²/R)·e^(−2t/τ): пік ~ 1/R, стала спаду ~ R. Площа ~ (1/R)·R = const.
    # Підбираємо peak·(1/decay) однаковим → візуально рівна площа.
    base_area = 1.0
    cases = [
        (1.00, RED,        "малий R: пік високий, гасне швидко"),
        (0.50, "#d9a441",  "середній R"),
        (0.25, NEG,        "великий R: пік низький, тягнеться довго"),
    ]
    for peak_frac, col, _lab in cases:
        # щоб площа peak/sp була стала: sp = peak_frac / base_area
        sp = peak_frac / base_area * 4.0
        pts = []
        for i in range(200):
            t = i / 199.0
            y = y0 - (y0 - Pmax) * peak_frac * math.exp(-t * sp)
            pts.append((x0 + t * tw, y))
        f.append(polyline(pts, color=col, sw=2.4))

    # легенда праворуч, по кривих не б'є
    lx, ly = x0 + tw * 0.40, yt + 34
    for k, (peak_frac, col, lab) in enumerate(cases):
        yy = ly + k * 22
        f.append(line(lx, yy - 4, lx + 26, yy - 4, color=col, sw=3))
        f.append(text(lx + 32, yy, lab, size=11, color=INK, anchor="start"))

    box = fitbox(x0 + 14, y0 - 96, 190, 56,
                 "висота × ширина\nкомпенсуються:\n∫ i²R dt = ½CU²\n(опір скоротився!)",
                 size=10.5, fill="#eef6ee", stroke=FIELD, color="#1e6b3a")
    f.append(box)

    return render(os.path.join(IMG, "energy-invariant.svg"), W, H, *f,
                  title="Опір міняє форму кидка, але не енергію заряду")


# ── B. Лінійне наростання: пік потужності рівно вдвічі за середню ─────────────
def fig_peak_vs_avg():
    """На лінійному наростанні струм сталий, напруга на транзисторі спадає
    лінійно → потужність — трикутник: пік на старті, нуль у кінці; середнє = ½ піку."""
    W, H = 720, 430
    f = []
    x0, y0 = 110, 330
    xr, yt = 670, 90
    f.append(arrow(x0, y0, xr, y0, color=INK, sw=1.8))
    f.append(arrow(x0, y0, x0, yt, color=INK, sw=1.8))
    f.append(text((x0 + xr) / 2, y0 + 34, "час наростання  →", size=12.5, color=INK))
    f.append('<text x="40" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 40 %.1f)">'
             'потужність у кристалі  →</text>'
             % ((y0 + yt) / 2, FONT, INK, (y0 + yt) / 2))
    f.append(text(W / 2, yt - 24, "Лінійне наростання: горб потужності — трикутник",
                  size=14, bold=True, color=INK))

    tw = xr - x0 - 130        # місце праворуч під підписи
    Ttip = x0 + tw
    Ppk = yt + 36
    Pavg = (y0 + Ppk) / 2     # рівно півпіку

    # трикутник потужності p(t) = Ppk·(1 − t/T)
    tri = "%.2f,%.2f %.2f,%.2f %.2f,%.2f" % (x0, y0, x0, Ppk, Ttip, y0)
    f.append('<polygon points="%s" fill="#fdecea" stroke="none" opacity="0.75"/>' % tri)
    f.append(line(x0, Ppk, Ttip, y0, color=RED, sw=2.8))

    # рівень піку
    f.append(line(x0 - 6, Ppk, x0, Ppk, color=INK, sw=1.5))
    f.append(text(x0 - 10, Ppk + 4, "P_пік = C·U²/T", size=11.5, color=RED, anchor="end"))

    # середня лінія = пів-піку
    f.append(line(x0, Pavg, Ttip, Pavg, color="#8a5a00", sw=1.8, dash="6 4"))
    f.append(text(Ttip + 8, Pavg - 4, "P_сер = ½·P_пік", size=11.5, color="#8a5a00", anchor="start"))
    f.append(text(Ttip + 8, Pavg + 14, "= C·U²/(2T)", size=10.5, color=MUTED, anchor="start"))

    # вісь часу: 0 і T
    f.append(text(x0 - 4, y0 + 18, "0", size=11, color=INK, anchor="end"))
    f.append(line(Ttip, y0, Ttip, y0 + 6, color=INK, sw=1.5))
    f.append(text(Ttip, y0 + 22, "T", size=12, color=INK))

    # площа = енергія
    box = fitbox(x0 + tw * 0.26, Ppk + 20, 168, 36,
                 "площа трикутника\n= енергія ½·C·U²",
                 size=10.5, fill="#fff7e6", stroke="#d9a441", color="#8a5a00")
    f.append(box)

    f.append(text(x0 + tw * 0.52, y0 - 24,
                  "напруга на транзисторі спадає → горб гасне",
                  size=10.5, color=MUTED, anchor="middle"))

    return render(os.path.join(IMG, "peak-vs-avg.svg"), W, H, *f,
                  title="Лінійне наростання: пік рівно вдвічі за середню")


if __name__ == "__main__":
    fig_energy_invariant()
    fig_peak_vs_avg()
    print("OK: 2 figури (energy-invariant, peak-vs-avg) у", IMG)
