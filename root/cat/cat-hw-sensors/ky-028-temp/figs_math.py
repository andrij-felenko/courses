# -*- coding: utf-8 -*-
"""Фігури до math-вставки «math-thermistor-temp.md» теми KY-028.
Окремий модуль (щоб не заважати паралельним правкам figs.py), той самий вивід ./img/.
Запуск:  python figs_math.py
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Крива опір↔температура NTC (нелінійність, що вимагає формули) ───────────
def fig_ntc_curve():
    """R(T) для NTC 10 кΩ, B=3950: крута на холоді, полога на спеці."""
    W, H = 780, 500
    f = [text(W / 2, 30, "NTC 10 кΩ: опір падає з теплом — круто на холоді, полого на спеці",
              size=15, bold=True)]

    ox, oy = 118, 410          # початок осей (лівий-нижній кут)
    aw, ah = 540, 330          # довжина осей
    tmin, tmax = -10.0, 90.0   # °C
    R0, T0K, B = 10000.0, 298.15, 3950.0

    def R_of(tC):
        return R0 * math.exp(B * (1.0 / (tC + 273.15) - 1.0 / T0K))

    rmax = R_of(tmin)          # найбільший опір — на найхолоднішому кінці

    # осі
    f.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))
    f.append(text(ox + aw / 2, oy + 44, "температура, °C", size=12, bold=True))
    f.append(text(ox - 84, oy - ah / 2, "опір, кΩ", size=12, bold=True))

    def px(tC):
        return ox + (tC - tmin) / (tmax - tmin) * aw

    def py(R):
        return oy - (R / rmax) * ah

    # сітка X (кожні 20 °C)
    tC = 0
    while tC <= tmax:
        x = px(tC)
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.4))
        f.append(text(x, oy + 22, "%d" % tC, size=10.5, color=MUTED))
        tC += 20
    # сітка Y (кожні 20 кΩ)
    rk = 0
    while rk * 1000 <= rmax + 1:
        y = py(rk * 1000)
        f.append(line(ox - 5, y, ox, y, color=INK, sw=1.4))
        f.append(text(ox - 12, y + 4, "%d" % rk, size=10.5, color=MUTED, anchor="end"))
        rk += 20

    # крива
    pts = []
    t = tmin
    while t <= tmax + 0.01:
        pts.append("%.1f,%.1f" % (px(t), py(R_of(t))))
        t += 1.0
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), POS))

    # опорна точка 25 °C = 10 кΩ (T0,R0)
    x25, y25 = px(25), py(10000)
    f.append(line(x25, oy, x25, y25, color=NEG, sw=1.3, dash="4 3"))
    f.append(line(ox, y25, x25, y25, color=NEG, sw=1.3, dash="4 3"))
    f.append(circle(x25, y25, 5, fill=BG, stroke=NEG, sw=2.2))
    f.append(text(x25 + 12, y25 - 12, "25 °C → 10 кΩ", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(x25 + 12, y25 + 6, "опорна точка (R₀, T₀)", size=9.5, color=MUTED, anchor="start"))

    # підписи крутизни на хвостах
    f.append(text(px(-3), py(R_of(-3)) - 14, "круто", size=11, bold=True, color=POS, anchor="middle"))
    f.append(text(px(78), py(R_of(78)) - 20, "полого", size=11, bold=True, color=POS, anchor="middle"))

    # анотація нелінійності (у вільному правому куті над кривою)
    box = textbox(W - 208, 148,
                  ["Однакові кроки в °C дають",
                   "РІЗНІ кроки в кΩ — тому",
                   "напруга не пропорційна",
                   "градусам: потрібна крива."],
                  size=10, pad=10, fill="#f6f7f9", stroke=MUTED, color=INK)
    f.append(box[0])

    return render(os.path.join(IMG, 'ntc-curve.svg'), W, H, *f)


# ── 2. Що дільник KY-028 робить із чистою напругою термістора ─────────────────
def fig_ao_distortion():
    """Ліворуч — напруга чесного дільника (монотонна, повний розмах);
    праворуч — AO KY-028: перевернута, стиснута, зсунута тінь тієї ж кривої."""
    W, H = 860, 480
    f = [text(W / 2, 28, "Чому AO не обернути в градуси: що дільник робить із кривою",
              size=15, bold=True)]

    R0, T0K, B, Rfix, Vs = 10000.0, 298.15, 3950.0, 10000.0, 3.3

    def Rof(tC):
        return R0 * math.exp(B * (1.0 / (tC + 273.15) - 1.0 / T0K))

    def panel(x0, title, invert, compress, subtitle, col):
        boxw, boxh = 320, 320
        ox = x0 + 52
        oy = 402
        aw, ah = 236, 300
        f.append(rect(x0, 66, boxw, boxh, fill=BG, stroke=MUTED, sw=1.4, rx=10))
        f.append(text(x0 + boxw / 2, 92, title, size=12.5, bold=True, color=col))
        # осі
        f.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
        f.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.8))
        f.append(text(ox - 12, oy - ah + 4, "U", size=11, bold=True, anchor="end"))
        # напруга чесного дільника з тим самим NTC у нижньому плечі → монотонно вгору
        tmin, tmax = 0.0, 80.0
        raw = []
        t = tmin
        while t <= tmax + 0.01:
            u = Vs * Rfix / (Rof(t) + Rfix)     # росте з теплом (опір NTC падає)
            raw.append((t, u))
            t += 1.0
        umin = min(u for _, u in raw)
        umax = max(u for _, u in raw)
        pts = []
        for t, u in raw:
            frac = (u - umin) / (umax - umin)   # 0..1
            if invert:
                frac = 1.0 - frac               # перевертання підтяжкою
            if compress:
                frac = 0.30 + frac * 0.32       # стиск + зсув (вузький розмах)
            xx = ox + (t - tmin) / (tmax - tmin) * aw
            yy = oy - frac * ah
            pts.append("%.1f,%.1f" % (xx, yy))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), col))
        f.append(text(ox + aw - 4, oy + 22, "тепліше →", size=9.5, color=MUTED, anchor="end"))
        # підпис під панеллю — двома короткими рядками
        subs = subtitle.split("\n")
        for i, s in enumerate(subs):
            f.append(text(x0 + boxw / 2, oy + 26 + i * 15, s, size=9.5, color=MUTED))

    # ліва панель — чистий дільник (KY-013)
    panel(24, "Чесний дільник (як у KY-013)", False, False,
          "монотонна, повний розмах →\nкриву обертають, °C рахуються", FIELD)
    # права панель — AO KY-028
    panel(516, "AO на платі KY-028", True, True,
          "перевернута + стиснута + зсунута,\nB невідома → обернути НЕ можна", POS)

    # «машина спотворення» між панелями
    f.append(arrow(344, 250, 512, 250, color=INK))
    box = textbox(430, 208, ["навантаження", "+ підтяжка"], size=9.5, pad=7,
                  fill="#f6f7f9", stroke=MUTED, color=INK)
    f.append(box[0])

    return render(os.path.join(IMG, 'ao-distortion.svg'), W, H, *f)


if __name__ == '__main__':
    fig_ntc_curve()
    fig_ao_distortion()
    print("OK: ntc-curve.svg, ao-distortion.svg")
