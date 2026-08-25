# -*- coding: utf-8 -*-
"""Фігури до вставки «Математика лінійності LNA» (math-lna-intercept).
Окремий файл, щоб не штовхатися з основним figs.py (його теми пише інша сесія);
пише у те саме ./img/.
  imd-spectrum.svg    — два сильні тони f1,f2; на виході 2-й порядок далеко, 3-й (2f1−f2, 2f2−f1) — у смузі.
  intercept-lines.svg — лог-лог: основний тон (нахил 1:1) і IM3 (нахил 3:1) → перетин IP3; P1dB нижче ~9.6 дБ.
Запуск:  python figs-linearity.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def imd_spectrum():
    """Два сильні тони f1,f2; вихідний спектр: 2-й порядок далеко, 3-й (2f1−f2, 2f2−f1) — впритул до смуги."""
    W, H = 760, 470
    p = []
    ox, axw = 70, 620

    def freq_axis(y, label):
        out = [line(ox, y, ox + axw, y, color=INK, sw=2)]
        out.append(text(ox + axw, y + 20, "частота", size=12, color=MUTED, anchor="end"))
        out.append(text(ox - 8, y - 96, label, size=12, color=MUTED, anchor="end"))
        out.append(line(ox, y, ox, y - 96, color=INK, sw=1.4))
        return out

    def fx(f):  # умовна частота 7..15 → піксель
        return ox + 40 + (f - 7.0) / (15.0 - 7.0) * (axw - 70)

    f1, f2 = 10.0, 11.0

    def tone(y, f, h, col, lab, dash=False):
        x = fx(f)
        out = [line(x, y, x, y - h, color=col, sw=3, dash=("4 3" if dash else None))]
        out.append(text(x, y - h - 7, lab, size=12, bold=True, color=col))
        return out, x

    yT = 150
    p += freq_axis(yT, "рівень")
    p.append(text(ox, 60, "Вхід: два сильні сусідні канали", size=14, bold=True, anchor="start"))
    fr, _ = tone(yT, f1, 86, POS, "f₁"); p += fr
    fr, _ = tone(yT, f2, 86, POS, "f₂"); p += fr

    yB = 380
    p += freq_axis(yB, "рівень")
    p.append(text(ox, 250, "Вихід нелінійного LNA: де сідають нові складові", size=14, bold=True, anchor="start"))

    band_x0, band_x1 = fx(8.6), fx(12.4)
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eafaf0" opacity="0.55"/>'
             % (band_x0, yB - 100, band_x1 - band_x0, 100))
    p.append(text((band_x0 + band_x1) / 2, yB - 104, "смуга приймача (за нею фільтр)",
                  size=10, color=FIELD, anchor="middle"))

    fr, x1 = tone(yB, f1, 86, POS, "f₁"); p += fr
    fr, x2 = tone(yB, f2, 86, POS, "f₂"); p += fr
    fr, xa = tone(yB, 2 * f1 - f2, 52, NEG, "2f₁−f₂", dash=True); p += fr
    fr, xb = tone(yB, 2 * f2 - f1, 52, NEG, "2f₂−f₁", dash=True); p += fr

    p.append(text(fx(7.45), yB - 28, "f₂−f₁ →", size=10, color=MUTED, anchor="middle"))
    p.append(text(fx(7.45), yB - 14, "(геть зліва)", size=9, color=MUTED, anchor="middle"))
    p.append(text(fx(14.3), yB - 28, "← 2f, f₁+f₂", size=10, color=MUTED, anchor="middle"))
    p.append(text(fx(14.3), yB - 14, "(геть справа)", size=9, color=MUTED, anchor="middle"))

    p.append(text((xa + xb) / 2, yB + 34, "складові 3-го порядку — у смузі, фільтр їх НЕ відсіє",
                  size=11, bold=True, color=NEG, anchor="middle"))

    b, _, _ = textbox(W / 2, 446,
                      "2-й порядок (2f, f₁±f₂) лягає вдвічі вище або в самий низ — далеко, фільтр його прибере.\n"
                      "3-й порядок 2f₁−f₂ і 2f₂−f₁ сідає впритул до f₁,f₂ — у смузі, де фільтр безсилий.",
                      size=12, fill="#eef3fb", stroke=NEG)
    p.append(b)
    render(os.path.join(OUT, 'imd-spectrum.svg'), W, H, *p,
           title="Чому небезпечний саме 3-й порядок: він сідає в корисну смугу")


def intercept_lines():
    """Лог-лог: основний тон (нахил 1:1) і IM3 (нахил 3:1) перетинаються в IP3; P1dB нижче на ~9.6 дБ."""
    W, H = 720, 540
    p = []
    ox, oy = 90, 430
    axw, axh = 540, 360
    p.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))
    p.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))
    p.append(text(ox + axw, oy + 22, "вхідна потужність Pᵢₙ (дБм)", size=12, color=MUTED, anchor="end"))
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" text-anchor="middle" '
             'transform="rotate(-90 %.1f %.1f)">вихідна потужність (дБм)</text>'
             % (ox - 56, oy - axh / 2, FONT, MUTED, ox - 56, oy - axh / 2))

    xlo, xhi = -40.0, 10.0
    ylo, yhi = -90.0, 30.0

    def X(px): return ox + (px - xlo) / (xhi - xlo) * axw
    def Y(py): return oy - (py - ylo) / (yhi - ylo) * axh

    G = 20.0
    IIP3 = 0.0
    OIP3 = IIP3 + G

    # основний тон 1:1
    p.append(line(X(xlo), Y(xlo + G), X(IIP3), Y(OIP3), color=POS, sw=2.4))
    p.append(line(X(IIP3), Y(OIP3), X(2.0), Y(2.0 + G), color=POS, sw=1.4, dash="5 4"))
    p.append(text(X(-36), Y(-36 + G) - 10, "основний тон (нахил 1:1)", size=12, bold=True, color=POS, anchor="start"))

    # реальна крива стиснення
    comp_pts = [(-40, -40 + G), (-20, -20 + G), (-8, -8 + G - 0.4),
                (-4, -4 + G - 1.0), (-1, -1 + G - 2.6), (2, 2 + G - 6.0)]
    d = "M " + " L ".join("%.1f %.1f" % (X(a), Y(b)) for a, b in comp_pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, POS))

    # IM3 3:1
    def im3_out(pin): return 3 * pin - 2 * IIP3 + G
    p.append(line(X(-28), Y(im3_out(-28)), X(IIP3), Y(OIP3), color=NEG, sw=2.4))
    p.append(line(X(IIP3), Y(OIP3), X(3.0), Y(im3_out(3.0)), color=NEG, sw=1.4, dash="5 4"))
    p.append(text(X(-13), Y(im3_out(-13)) + 17, "IM3-завада (нахил 3:1)", size=12, bold=True, color=NEG, anchor="start"))

    xi, yi = X(IIP3), Y(OIP3)
    p.append(circle(xi, yi, 7, fill="#fff", stroke=INK, sw=2.4))
    p.append(text(xi + 12, yi - 8, "точка перетину IP3", size=13, bold=True, anchor="start"))
    p.append(line(xi, yi, xi, oy, color=MUTED, sw=1.2, dash="3 3"))
    p.append(line(xi, yi, ox, yi, color=MUTED, sw=1.2, dash="3 3"))
    p.append(text(xi, oy + 16, "IIP3", size=12, bold=True, color=INK, anchor="middle"))
    p.append(text(ox - 10, yi + 4, "OIP3", size=12, bold=True, color=INK, anchor="end"))

    p1_in = IIP3 - 9.6
    p1_out = p1_in + G - 1.0
    xp, yp = X(p1_in), Y(p1_out)
    p.append(circle(xp, yp, 6, fill="#fff", stroke=POS, sw=2.2))
    p.append(text(xp - 8, yp - 10, "P1dB", size=12, bold=True, color=POS, anchor="end"))
    p.append(text(xp - 8, yp + 6, "(−1 дБ)", size=10, color=POS, anchor="end"))
    p.append(line(xp, yp, xp, oy, color=POS, sw=1.0, dash="3 3"))

    gy = oy + 38
    p.append(line(xp, gy, xi, gy, color=INK, sw=1.4))
    p.append(line(xp, gy - 5, xp, gy + 5, color=INK, sw=1.4))
    p.append(line(xi, gy - 5, xi, gy + 5, color=INK, sw=1.4))
    p.append(text((xp + xi) / 2, gy - 8, "≈ 9.6 дБ (ідеальна модель)", size=11, bold=True, anchor="middle"))

    b, _, _ = textbox(W / 2, 510,
                      "Основний тон росте 1:1, завада IM3 — 3:1. Продовжені прямі сходяться в уявній точці IP3,\n"
                      "де завада «наздогнала» сигнал. Реально каскад туди не доходить — раніше стискається (P1dB).",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'intercept-lines.svg'), W, H, *p,
           title="Точка перетину IP3 і точка стиснення P1dB")


if __name__ == '__main__':
    imd_spectrum()
    intercept_lines()
    print("OK: 2 figures ->", OUT)
