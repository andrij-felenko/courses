# -*- coding: utf-8 -*-
"""Фігури до кроку «Генератор Пірса: схема й розрахунок обв'язки кварцу».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Схема Пірса з підписаними проєктними величинами ──────────────────────
def fig_schematic():
    W, H = 720, 430
    f = []
    # інвертор-трикутник (підсилювач)
    ax, ay = 300, 150          # ліва грань
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="#eef1f5" stroke="%s" '
             'stroke-width="2"/>' % (ax, ay - 40, ax, ay + 40, ax + 80, ay, INK))
    f.append(circle(ax + 86, ay, 6, fill=BG, stroke=INK, sw=2))   # кружок інверсії
    f.append(text(ax + 40, ay + 5, "gm", size=15, bold=True))
    f.append(text(ax + 40, ay - 52, "інвертор (підсилювач)", size=12, color=MUTED))
    inL = (ax, ay)             # вхід
    inR = (ax + 92, ay)        # вихід (після кружка)

    # вузли XIN (ліворуч від входу) та XOUT (праворуч від виходу)
    xin = (170, ay)
    xout = (560, ay)
    f.append(line(inL[0], inL[1], xin[0], xin[1], color=INK, sw=2))
    f.append(line(inR[0], inR[1], xout[0], xout[1], color=INK, sw=2))
    f.append(circle(xin[0], xin[1], 4, fill=INK, stroke=INK))
    f.append(circle(xout[0], xout[1], 4, fill=INK, stroke=INK))
    f.append(text(xin[0] - 6, xin[1] - 14, "XIN", size=12, bold=True, anchor="end"))
    f.append(text(xout[0] + 6, xout[1] - 14, "XOUT", size=12, bold=True, anchor="start"))

    # кварц між XIN та XOUT (зверху)
    qy = 70
    f.append(line(xin[0], xin[1], xin[0], qy, color=INK, sw=2))
    f.append(line(xout[0], xout[1], xout[0], qy, color=INK, sw=2))
    f.append(line(xin[0], qy, 320, qy, color=INK, sw=2))
    f.append(line(410, qy, xout[0], qy, color=INK, sw=2))
    # символ кварцу: дві пластини + прямокутник
    f.append(line(320, qy - 18, 320, qy + 18, color=INK, sw=2.5))
    f.append(rect(330, qy - 14, 70, 28, fill="#fff7e6", stroke=INK, sw=2, rx=2))
    f.append(line(410, qy - 18, 410, qy + 18, color=INK, sw=2.5))
    f.append(text(365, qy - 24, "кварц (XTAL)", size=12, bold=True))
    f.append(text(365, qy + 5, "Rm Lm Cm | C0", size=10, color=MUTED))

    # Rf паралельно інвертору (знизу)
    rfy = 250
    f.append(line(xin[0], xin[1], xin[0], rfy, color=NEG, sw=1.8))
    f.append(line(inR[0], rfy, inR[0], inR[1], color=NEG, sw=1.8))
    fb = fitbox(xin[0] + 30, rfy - 16, 130, 32, "Rf  (зміщення)", size=12,
                fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    f.append(line(xin[0], rfy, xin[0] + 30, rfy, color=NEG, sw=1.8))
    f.append(line(xin[0] + 160, rfy, inR[0], rfy, color=NEG, sw=1.8))
    f.append(fb)

    # Rd послідовний у вітці XOUT
    f.append(rect(470, ay - 12, 50, 24, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    f.append(text(495, ay + 5, "Rd", size=12, bold=True, color=POS))
    f.append(text(495, ay + 34, "обмежує drive", size=10, color=MUTED))

    # C1 від XIN на землю
    def cap_to_gnd(x, top, label, sub):
        out = [line(x, top, x, top + 40, color=INK, sw=2)]
        out.append(line(x - 16, top + 40, x + 16, top + 40, color=INK, sw=2.5))
        out.append(line(x - 16, top + 50, x + 16, top + 50, color=INK, sw=2.5))
        out.append(line(x, top + 50, x, top + 66, color=INK, sw=2))
        # земля
        out.append(line(x - 16, top + 66, x + 16, top + 66, color=INK, sw=2))
        out.append(line(x - 10, top + 72, x + 10, top + 72, color=INK, sw=2))
        out.append(line(x - 4, top + 78, x + 4, top + 78, color=INK, sw=2))
        out.append(text(x + 24, top + 44, label, size=13, bold=True, anchor="start"))
        out.append(text(x + 24, top + 60, sub, size=10, color=MUTED, anchor="start"))
        return out
    f += cap_to_gnd(xin[0], ay, "C1", "на землю")
    f += cap_to_gnd(xout[0], ay, "C2", "на землю")

    # паразитна ємність (пунктир) біля XIN
    f.append(text(xin[0] - 6, ay + 60, "+ Cпар", size=11, color=MUTED, anchor="end"))

    return render(os.path.join(IMG, "pierce-design.svg"), W, H, *f,
                  title="Генератор Пірса: де живе кожне проєктне число")


# ── 2. Розрахунок навантажувальної ємності: C1=C2 під задану CL ─────────────
def fig_load_cap():
    W, H = 720, 360
    f = []
    # ліворуч: формула як «дві ємності послідовно + Cпар»
    f.append(text(180, 60, "Що кварц бачить ззовні", size=15, bold=True))
    # C1
    f.append(line(120, 110, 120, 140, color=INK, sw=2))
    f.append(line(104, 110, 136, 110, color=INK, sw=2.5)); f.append(line(104, 100, 136, 100, color=INK, sw=2.5))
    f.append(text(120, 90, "C1", size=12, bold=True))
    f.append(line(120, 140, 240, 140, color=INK, sw=2))      # вузол землі
    # C2
    f.append(line(240, 110, 240, 140, color=INK, sw=2))
    f.append(line(224, 110, 256, 110, color=INK, sw=2.5)); f.append(line(224, 100, 256, 100, color=INK, sw=2.5))
    f.append(text(240, 90, "C2", size=12, bold=True))
    f.append(text(180, 165, "через землю → послідовно", size=11, color=MUTED))
    f.append(line(120, 100, 120, 80, color=INK, sw=2)); f.append(circle(120, 80, 4, fill=INK, stroke=INK))
    f.append(line(240, 100, 240, 80, color=INK, sw=2)); f.append(circle(240, 80, 4, fill=INK, stroke=INK))
    f.append(text(120, 70, "до кварцу", size=10, color=MUTED))

    fb = fitbox(70, 210, 230, 56,
                "CL = C1·C2/(C1+C2) + Cпар", size=14, fill=FILL, bold=True)
    f.append(fb)
    f.append(text(185, 295, "Cпар = ніжки + доріжки", size=11, color=MUTED))
    f.append(text(185, 314, "(зазвичай 2…5 пФ)", size=11, color=MUTED))

    # роздільник
    f.append(line(360, 60, 360, 320, color="#dddddd", sw=1.5, dash="4 4"))

    # праворуч: симетричний випадок C1=C2=C
    f.append(text(540, 60, "Симетрично: C1 = C2 = C", size=15, bold=True))
    fb2 = fitbox(420, 95, 250, 50, "CL = C/2 + Cпар", size=15, fill="#eef9f0",
                 stroke=FIELD, bold=True)
    f.append(fb2)
    fb3 = fitbox(420, 160, 250, 50, "C = 2·(CL − Cпар)", size=15, fill="#eef9f0",
                 stroke=FIELD, bold=True)
    f.append(fb3)
    # стрілка-висновок
    f.append(text(545, 250, "↓ беремо найближчий", size=12, color=MUTED))
    f.append(text(545, 268, "стандартний номінал", size=12, color=MUTED))
    fb4 = fitbox(440, 285, 210, 40, "напр. 27 пФ на вивід", size=13, fill=FILL, bold=True)
    f.append(fb4)

    return render(os.path.join(IMG, "load-cap.svg"), W, H, *f,
                  title="Підбір C1 і C2 під навантажувальну ємність CL")


# ── 3. Погляд через від'ємний опір: −Rneg проти Rm ─────────────────────────
def fig_negative_resistance():
    W, H = 720, 340
    f = []
    # ліворуч: кварц = Rm (втрати), праворуч: схема = −Rneg (накачка)
    cx = 360
    f.append(line(cx, 70, cx, 290, color="#dddddd", sw=1.5, dash="4 4"))

    # кварц
    f.append(text(180, 60, "Кварц: втрати", size=15, bold=True))
    f.append(rect(110, 95, 140, 52, fill="#fff7e6", stroke=INK, sw=2, rx=6))
    f.append(text(180, 120, "Rm (ESR)", size=14, bold=True))
    f.append(text(180, 140, "з'їдає енергію +Ω", size=11, color=MUTED))
    f.append(text(180, 185, "тертя пластини →", size=12, color=MUTED))
    f.append(text(180, 203, "коливання гаснуть", size=12, color=MUTED))

    # схема
    f.append(text(540, 60, "Схема: накачка", size=15, bold=True))
    f.append(rect(470, 95, 160, 52, fill="#eef9f0", stroke=FIELD, sw=2, rx=6))
    f.append(text(550, 120, "−Rneg", size=14, bold=True, color=FIELD))
    f.append(text(550, 140, "вливає енергію −Ω", size=11, color=MUTED))
    f.append(text(550, 185, "gm крізь C1, C2 →", size=12, color=MUTED))
    f.append(text(550, 203, "коливання ростуть", size=12, color=MUTED))

    # умова старту знизу — на всю ширину
    fb = fitbox(150, 240, 430, 56, "старт ⟺  |Rneg|  >  Rm   (з запасом ×5)",
                size=16, fill=FILL, bold=True)
    f.append(fb)

    return render(os.path.join(IMG, "negative-resistance.svg"), W, H, *f,
                  title="Генератор як від'ємний опір, що долає втрати кварцу")


# ── 4. |Rneg| як функція gm: пік і вікно безпечного запасу ──────────────────
def fig_gm_curve():
    W, H = 720, 420
    ox, oy = 90, 340          # початок осей
    pw, ph = 560, 250         # поле графіка
    f = []
    # осі
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=2))           # X: gm
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=2))           # Y: |Rneg|
    f.append(text(ox + pw, oy + 28, "gm (крутість підсилювача) →", size=12,
                  anchor="end", color=MUTED))
    f.append(text(ox - 10, oy - ph - 8, "|Rneg|", size=12, anchor="middle", color=MUTED))

    # крива |Rneg|(gm): росте, пік, спадає (типова для Пірса)
    pts = []
    N = 120
    for i in range(N + 1):
        t = i / N
        gm = t * 1.0
        # модель: gm/(1+ k gm^2) — пік при gm=1/sqrt(k)
        k = 6.0
        r = gm / (1.0 + k * gm * gm)
        pts.append((gm, r))
    rmax = max(r for _, r in pts)
    def X(gm): return ox + gm * pw
    def Y(r):  return oy - (r / rmax) * (ph - 30)
    path = "M " + " L ".join("%.1f %.1f" % (X(gm), Y(r)) for gm, r in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path, FIELD))

    # рівень Rm (поріг) та запас ×5
    # знайдемо gm, де r = rm  (рання, висхідна гілка)
    rm = rmax * 0.30
    f.append(line(ox, Y(rm), ox + pw, Y(rm), color=POS, sw=1.8, dash="6 4"))
    f.append(text(ox + pw - 4, Y(rm) - 8, "Rm (ESR кварцу)", size=12, color=POS, anchor="end"))

    # gm_crit: перший перетин
    gm_crit = None
    for gm, r in pts:
        if r >= rm:
            gm_crit = gm; break
    f.append(line(X(gm_crit), oy, X(gm_crit), Y(rm), color=POS, sw=1.5, dash="3 3"))
    f.append(text(X(gm_crit), oy + 18, "gm_crit", size=12, color=POS, bold=True))

    # робоча точка ×5
    gm_op = min(1.0, gm_crit * 5)
    # значення кривої у робочій точці
    k = 6.0
    r_op = gm_op / (1.0 + k * gm_op * gm_op)
    f.append(circle(X(gm_op), Y(r_op), 6, fill=NEG, stroke=BG, sw=2))
    f.append(text(X(gm_op), Y(r_op) - 14, "робоча gm (×5)", size=12, color=NEG, bold=True))

    # пік
    gm_peak = 1.0 / math.sqrt(k)
    r_peak = gm_peak / (1.0 + k * gm_peak * gm_peak)
    f.append(circle(X(gm_peak), Y(r_peak), 4, fill=INK, stroke=INK))
    f.append(text(X(gm_peak), Y(r_peak) - 12, "пік |Rneg|", size=11, color=MUTED))
    f.append(text(X(gm_peak) + 4, Y(r_peak) + 18, "далі gm НЕ допомагає", size=11,
                  color=MUTED, anchor="start"))

    # зона старту (між gm_crit і спадом нижче Rm справа)
    f.append(text(ox + 8, oy - ph + 10, "вище порога — генерує", size=11, color=FIELD, anchor="start"))

    return render(os.path.join(IMG, "gm-curve.svg"), W, H, *f,
                  title="Від'ємний опір залежить від gm нелінійно: є пік")


if __name__ == "__main__":
    fig_schematic()
    fig_load_cap()
    fig_negative_resistance()
    fig_gm_curve()
    print("OK: 4 figures written to", IMG)
