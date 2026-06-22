# -*- coding: utf-8 -*-
"""Фігури до статті «Джерела опорної напруги: стабілітрон і bandgap».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Дві фігури, що несуть фізику джерела (а не метрологію):
  1) zener-drift.svg — температурний дрейф трьох еталонів (стабілітрон ~3.3 В
     із від'ємним нахилом, опорний ~6.2 В і плоский bandgap);
  2) bandgap-idea.svg — складання двох протилежних нахилів (Vbe спадає,
     K·ΔVbe росте) у майже плоску суму ≈ 1.25 В.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Температурний дрейф: стабілітрон «пливе», bandgap — ні ─────────────────
# Ідея: на одних осях (T, %відхилення) три криві. Низьковольтний стабілітрон
# ~3.3 В має помітний від'ємний нахил; опорний ~6.2 В — слабкий вигин біля нуля;
# bandgap тримає майже горизонталь. Видно, що цінна саме плоскість.

def fig_zener_drift():
    W, H = 700, 360
    ox, oy = 95, 215            # початок осей; oy — рівень 0 %
    aw = 470                    # довжина осі T
    top, bot = 80, 345          # верх/низ поля графіка
    p = []

    # підзаголовок під титулом
    p.append(text(W / 2, 46, "відхилення опорної напруги від номіналу, %",
                  size=12, color=MUTED))

    # вісь T (горизонталь на рівні 0 %) і вісь %
    p.append(arrow(ox, bot, ox, top - 6, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox + aw + 8, oy, color=INK, sw=1.8))
    p.append(text(ox + 4, top - 10, "ΔV, %", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(ox + aw + 12, oy + 4, "T, °C", size=12, color=INK, bold=True, anchor="start"))

    # сітка по % (+4..−4) і нульова лінія
    perc_px = 33.0             # px на 1 % (щоб ±4 % вкладалося в поле)
    for pc in (4, 2, -2, -4):
        gy = oy - pc * perc_px
        p.append(line(ox, gy, ox + aw - 4, gy, color="#e4e4e4", sw=1.1, dash="4 4"))
        p.append(text(ox - 8, gy + 4, "%+d%%" % pc, size=10, color=MUTED, anchor="end"))
    p.append(line(ox, oy, ox + aw - 4, oy, color=MUTED, sw=1.3))
    p.append(text(ox - 8, oy + 4, "0", size=10, color=MUTED, anchor="end"))

    # шкала T: −40..+85 °C, відлік 25 °C збігається з 0 % (кімнатна)
    tmin, tmax, tref = -40.0, 85.0, 25.0
    def tx(t):
        return ox + (t - tmin) / (tmax - tmin) * aw
    for t in (-40, 0, 25, 50, 85):
        x = tx(t)
        p.append(line(x, oy - 4, x, oy + 4, color=INK, sw=1.5))
        p.append(text(x, oy + 20, "%d" % t, size=10, color=INK))

    def curve(fn, color, sw, dash=None):
        pts = []
        for i in range(0, 201):
            t = tmin + (tmax - tmin) * i / 200.0
            pts.append("%.1f,%.1f" % (tx(t), oy - fn(t) * perc_px))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
                'stroke-linejoin="round"/>' % (" ".join(pts), color, sw, d))

    # стабілітрон ~3.3 В: −2 мВ/°C на 3300 мВ → ≈ −0.0606 %/°C, лінійно від кімнатної
    def zener_lv(t):
        return -2.0 * (t - tref) / 3300.0 * 100.0
    # опорний ~6.2 В: майже скомпенсований, лишковий слабкий параболічний вигин
    def zener_62(t):
        return -8e-5 * (t - tref) ** 2 * 100.0 / 6.2 * 0.6 + 0.0
    # bandgap: ~50 ppm/°C з легким вигином — майже плоско
    def bandgap(t):
        return (50e-6 * abs(t - tref) + 6e-7 * (t - tref) ** 2) * 100.0 * 0.0 + \
               50e-6 * (t - tref) * 100.0

    p.append(curve(zener_62, MUTED, 2.0, dash="5 4"))
    p.append(curve(zener_lv, NEG, 2.6))
    p.append(curve(bandgap, POS, 3.0))

    # підписи кривих біля них (зсунуто від осьового напису ΔV)
    p.append(text(tx(-28), oy - zener_lv(-28) * perc_px - 10,
                  "стабілітрон ~3.3 В (−2 мВ/°C)", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(tx(85) - 4, oy - zener_62(85) * perc_px - 8,
                  "опорний ~6.2 В", size=10.5, color=MUTED, anchor="end"))
    p.append(text(tx(-40) + 8, oy - bandgap(-40) * perc_px + 18,
                  "bandgap (плоска)", size=11.5, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "zener-drift.svg"), W, H, *p,
           title="Чому стабілітрон «пливе», а bandgap — ні")


# ── 2. Принцип bandgap: дві протилежні залежності складаються в нуль ──────────
# Ідея: на осях (T, V) синя лінія Vbe спадає (−2 мВ/°C), червона K·ΔVbe росте
# (PTAT), зелена сума виходить майже горизонтальною ≈ 1.25 В.

def fig_bandgap_idea():
    W, H = 680, 320
    ox, oy = 80, 250
    aw, ah = 470, 196
    p = []

    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 6, color=INK, sw=2))
    p.append(arrow(ox, oy, ox + aw + 8, oy, color=INK, sw=2))
    p.append(text(ox - 4, oy - ah - 2, "V", size=13, color=INK, bold=True, italic=True, anchor="end"))
    p.append(text(ox + aw + 12, oy + 4, "T", size=13, color=INK, bold=True, italic=True, anchor="start"))

    # дві прямі складаємо так, щоб сума лягла горизонталлю посередині поля
    x0, x1 = ox, ox + aw
    sum_y = oy - ah * 0.62            # рівень сталої суми ≈ 1.25 В
    spread = ah * 0.40               # розхил ліній на кінцях

    # Vbe (синя): спадає з T → зліва вище, справа нижче
    vbe_l, vbe_r = sum_y - spread, sum_y + spread
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (x0, vbe_l, x1, vbe_r, NEG))
    p.append(text(x1 + 4, vbe_r, "Vbe (−2 мВ/°C)", size=12, color=NEG, bold=True, anchor="start"))

    # K·ΔVbe (червона, PTAT): росте з T → дзеркально
    pt_l, pt_r = sum_y + spread, sum_y - spread
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (x0, pt_l, x1, pt_r, POS))
    p.append(text(x1 + 4, pt_r, "K·ΔVbe (PTAT, +)", size=12, color=POS, bold=True, anchor="start"))

    # сума (зелена горизонталь)
    p.append(line(x0, sum_y, x1, sum_y, color=FIELD, sw=3))
    p.append(text(x1 + 4, sum_y, "сума ≈ 1.25 В", size=12.5, color=FIELD, bold=True, anchor="start"))

    # підпис-висновок двома рядками внизу
    p.append(text(ox + aw / 2, oy + 24,
                  "Падіння переходу + помножена різниця двох переходів = майже константа.",
                  size=11.5, color=MUTED))
    p.append(text(ox + aw / 2, oy + 42,
                  "1.25 В — це і є ширина забороненої зони кремнію у вольтах.",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "bandgap-idea.svg"), W, H, *p,
           title="Складаємо дві протилежні залежності в нуль")


if __name__ == "__main__":
    fig_zener_drift()
    fig_bandgap_idea()
    print("OK: figures written to", OUT)
