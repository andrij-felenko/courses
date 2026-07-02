# -*- coding: utf-8 -*-
"""Фігури до теми «Три-фазний міст» (B6, шестипульсний випрямляч).
Чотири фігури, на які посилається стаття:
  three-sines.svg      — три фази 120° нарізно: верхня й нижня обвідні не сходяться
  b6-bridge.svg        — шість діодів: верхня група → +, нижня → −
  output-envelope.svg  — вихід їде по обвідній лінійних напруг; 6 горбів проти 1-фазного
  conduction-120.svg   — який діод проводить: кожен 120°, естафета на перетинах
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

PH = ["#c0392b", "#27ae60", "#2457d6"]     # кольори фаз L1 L2 L3
PHN = ["L1", "L2", "L3"]


def diode(cx, cy, scale=1.0, color=INK, down=True):
    """Символ діода: трикутник + планка. down=True — струм тече згори вниз
    (анод угорі, катод унизу). Повертає (svg, x_top, y_top, x_bot, y_bot)."""
    s = scale
    bw = 13 * s
    out = []
    if down:
        base_y = cy - 12 * s          # основа трикутника вгорі
        tip_y = cy + 9 * s            # вістря вниз (до катодної планки)
        bar_y = tip_y
        top_y = cy - 26 * s
        bot_y = cy + 24 * s
    else:
        base_y = cy + 12 * s
        tip_y = cy - 9 * s
        bar_y = tip_y
        top_y = cy - 24 * s
        bot_y = cy + 26 * s
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
        cx - bw, base_y, cx + bw, base_y, cx, tip_y, FILL, color))
    out.append(line(cx - bw, bar_y, cx + bw, bar_y, color=color, sw=2.4))
    out.append(line(cx, top_y, cx, base_y if down else tip_y, color=INK, sw=2))
    out.append(line(cx, tip_y if down else base_y, cx, bot_y, color=INK, sw=2))
    return "".join(out), cx, top_y, cx, bot_y


def three_phase_pts(x0, x1, oy, amp, n=360, phase_deg=0.0, cycles=1.0):
    """Три списки точок синусоїд, зсунутих на 120°."""
    series = []
    for k in range(3):
        pts = []
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            th = 2 * math.pi * cycles * i / n + math.radians(phase_deg) - k * 2 * math.pi / 3
            y = oy - amp * math.sin(th)
            pts.append((x, y, math.sin(th)))
        series.append(pts)
    return series


# ── Фігура 1: три фази 120° нарізно ─────────────────────────────────────────
def fig_three_sines():
    W, H = 860, 380
    f = [text(W / 2, 28, "Три фази зсунуті на 120°: коли одна провалюється, інша тримає",
              size=16, bold=True)]
    ox, oy = 70, 200
    x0, x1 = 90, 800
    amp = 120
    # осі
    f.append(line(ox, 60, ox, 340, color=INK, sw=1.6))
    f.append(arrow(ox, 66, ox, 56, color=INK))
    f.append(line(ox, oy, 812, oy, color=INK, sw=1.6))
    f.append(arrow(796, oy, 818, oy, color=INK))
    f.append(text(806, oy + 18, "t", size=12, bold=True, anchor="start"))
    f.append(text(ox - 6, 58, "U фази", size=11, bold=True, anchor="end"))

    series = three_phase_pts(x0, x1, oy, amp, n=360, cycles=1.0)
    # верхня й нижня обвідні (max і min із трьох) — заштрихувати «завжди відкриту» смугу
    n = len(series[0])
    top = []
    bot = []
    for i in range(n):
        ys = [series[k][i][1] for k in range(3)]
        top.append((series[0][i][0], min(ys)))   # min y = найвище на екрані
        bot.append((series[0][i][0], max(ys)))
    band = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in top)
    band += " L " + " L ".join("%.1f,%.1f" % (x, y) for x, y in reversed(bot))
    band += " Z"
    f.append('<path d="%s" fill="#eef2f7" stroke="none" opacity="0.9"/>' % band)
    # обвідні лінії
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="5,4"/>' % (
        " L ".join("%.1f,%.1f" % (x, y) for x, y in top), MUTED))
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="5,4"/>' % (
        " L ".join("%.1f,%.1f" % (x, y) for x, y in bot), MUTED))

    # самі синусоїди
    for k in range(3):
        pts = " L ".join("%.1f,%.1f" % (p[0], p[1]) for p in series[k])
        f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.4"/>' % (pts, PH[k]))
        # підпис фази біля лівого краю
        y0 = series[k][0][1]
        f.append(text(x0 - 6, y0 + 4, PHN[k], size=12, color=PH[k], bold=True, anchor="end"))

    # стрілка: висота смуги = завжди доступна напруга
    xm = x0 + (x1 - x0) * 0.5
    im = int(360 * 0.5)
    yt = min(series[k][im][1] for k in range(3))
    yb = max(series[k][im][1] for k in range(3))
    f.append(line(xm, yt, xm, yb, color=INK, sw=1.4, dash="2,3"))
    box, w, h = textbox(xm + 4, 320, "ця відстань\nніколи не нульова", size=10.5,
                        color=INK, bold=True, fill="#ffffff", stroke=INK, sw=1.4)
    f.append(box)
    f.append(line(xm, (yt + yb) / 2, xm + 4, 320 - h / 2, color=MUTED, sw=1.2, dash="3,3"))

    render(os.path.join(IMG, "three-sines.svg"), W, H, *f)


# ── Фігура 2: схема B6 (шість діодів) ───────────────────────────────────────
def fig_b6_bridge():
    W, H = 760, 420
    f = [text(W / 2, 28, "Шість діодів: верхня трійка ловить найвищу фазу, нижня — найнижчу",
              size=15, bold=True)]

    plus_y, minus_y = 70, 350
    xs = [250, 350, 450]                 # три вузли фаз (вертикальні лінії всередині)
    # горизонтальні шини + і −
    f.append(line(140, plus_y, 620, plus_y, color=POS, sw=2.6))
    f.append(line(140, minus_y, 620, minus_y, color=NEG, sw=2.6))
    f.append(text(632, plus_y + 4, "+", size=16, color=POS, bold=True, anchor="start"))
    f.append(text(632, minus_y + 4, "−", size=16, color=NEG, bold=True, anchor="start"))

    # верхня група: анод до фази, катод до +  (down=True: анод угорі... треба навпаки)
    # верхній діод проводить, коли фаза > шини +? ні: фаза висока → діод відкритий до +.
    # анод на боці ФАЗИ, катод на боці +. Фаза нижче за плюсову шину, тож анод унизу, катод угорі:
    for i, x in enumerate(xs):
        # верхній діод: катод (планка) угорі до +, анод унизу до вузла фази
        svg, xt, yt, xb, yb = diode(x, (plus_y + 170) / 2 + 20, scale=1.0, color=PH[i], down=False)
        f.append(svg)
        f.append(line(x, yt, x, plus_y, color=INK, sw=2))
        # нижній діод: анод угорі до вузла фази, катод унизу до −
        svg2, xt2, yt2, xb2, yb2 = diode(x, (minus_y + 250) / 2 - 20, scale=1.0, color=PH[i], down=True)
        f.append(svg2)
        f.append(line(x, yb2, x, minus_y, color=INK, sw=2))
        # вузол фази між двома діодами
        node_y = (yb + yt2) / 2
        f.append(line(x, yb, x, node_y, color=INK, sw=2))
        f.append(line(x, node_y, x, yt2, color=INK, sw=2))
        f.append(circle(x, node_y, 3.4, fill=INK, stroke=INK, sw=1))
        # вивід фази: короткий стуб ліворуч від СВОЄЇ колонки (входи заходять у три середні точки)
        f.append(line(x, node_y, x - 46, node_y, color=PH[i], sw=2.2))
        f.append(circle(x - 46, node_y, 4.5, fill=BG, stroke=PH[i], sw=2))
        f.append(text(x - 56, node_y + 4, PHN[i], size=12, color=PH[i], bold=True, anchor="end"))

    # підписи груп
    f.append(text(560, 150, "верхня група → +", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(560, 300, "нижня група → −", size=11, color=NEG, bold=True, anchor="start"))

    # навантаження праворуч між + і −
    lx = 600
    f.append(line(620, plus_y, lx + 60, plus_y, color=POS, sw=2.6))
    f.append(line(620, minus_y, lx + 60, minus_y, color=NEG, sw=2.6))
    f.append(line(lx + 60, plus_y, lx + 60, minus_y, color=INK, sw=2))
    f.append(rect(lx + 44, 190, 32, 40, fill="#eef6ef", stroke=INK, sw=1.6, rx=4))
    f.append(text(lx + 60, 214, "R", size=13, bold=True))
    f.append(text(lx + 60, 250, "U_dc", size=11, color=MUTED, bold=True))

    render(os.path.join(IMG, "b6-bridge.svg"), W, H, *f)


# ── Фігура 3: вихідна обвідна проти 1-фазного ───────────────────────────────
def fig_output_envelope():
    W, H = 860, 400
    f = [text(W / 2, 26, "Вихід їде по верхівках лінійних напруг: 6 горбів, майже рівно",
              size=15, bold=True)]
    ox, oy = 70, 300
    x0, x1 = 90, 800
    amp = 96
    f.append(line(ox, 60, ox, 356, color=INK, sw=1.6))
    f.append(arrow(ox, 66, ox, 56, color=INK))
    f.append(line(ox, oy, 812, oy, color=INK, sw=1.6))
    f.append(arrow(796, oy, 818, oy, color=INK))
    f.append(text(806, oy + 18, "t", size=12, bold=True, anchor="start"))

    # шість лінійних напруг = різниці фаз; але простіше показати |три фази| та їхню верхню обвідну.
    # намалюємо три фази тонко, тоді верхню обвідну модулів як вихід B6 (=обвідна ліній-ліній).
    series = three_phase_pts(x0, x1, oy, amp, n=540, cycles=1.5)
    # шість «плечей»: для кожної миті вихід = max(фаза) − min(фаза)  (лінія-лінія)
    n = len(series[0])
    outp = []
    for i in range(n):
        ys_signed = [series[k][i][2] for k in range(3)]      # sin-значення
        vout = (max(ys_signed) - min(ys_signed))             # у одиницях amp
        x = series[0][i][0]
        outp.append((x, oy - amp * vout))
    # тонкі фази для контексту (напівпрозорі)
    for k in range(3):
        pts = " L ".join("%.1f,%.1f" % (p[0], p[1]) for p in series[k])
        f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="1.2" opacity="0.35"/>' % (pts, PH[k]))
    # рівень нуля-осі та рівень Vpk_LL і Vmin
    ll_peak = oy - amp * math.sqrt(3)          # пік лінійної = sqrt3 * amp фази
    ll_min = oy - amp * math.sqrt(3) * math.cos(math.pi / 6)
    f.append(line(ox, ll_peak, 800, ll_peak, color=MUTED, sw=1, dash="4,4"))
    f.append(text(804, ll_peak + 4, "пік ≈ √2·U_лл", size=10, color=MUTED, anchor="start"))
    f.append(line(ox, ll_min, 800, ll_min, color=MUTED, sw=1, dash="4,4"))
    f.append(text(804, ll_min + 4, "низ", size=10, color=MUTED, anchor="start"))
    # вихід B6
    pts = " L ".join("%.1f,%.1f" % (x, y) for x, y in outp)
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.8"/>' % (pts, INK))
    f.append(text(150, ll_peak - 12, "вихід трифазного моста (6 горбів)", size=11, color=INK, bold=True, anchor="start"))

    # смуга пульсації
    f.append(line(660, ll_peak, 660, ll_min, color=POS, sw=1.6))
    f.append(text(668, (ll_peak + ll_min) / 2 + 4, "≈14%", size=10, color=POS, bold=True, anchor="start"))

    render(os.path.join(IMG, "output-envelope.svg"), W, H, *f)


# ── Фігура 4: провідність кожного діода по 120° ─────────────────────────────
def fig_conduction():
    W, H = 860, 340
    f = [text(W / 2, 26, "Естафета: у кожну мить відкриті два діоди, кожен веде 120°",
              size=15, bold=True)]
    ox, oy = 70, 150
    x0, x1 = 110, 790
    amp = 78
    f.append(line(ox, 50, ox, 250, color=INK, sw=1.6))
    f.append(arrow(ox, 56, ox, 46, color=INK))
    f.append(line(ox, oy, 812, oy, color=INK, sw=1.6))
    f.append(arrow(796, oy, 818, oy, color=INK))
    f.append(text(806, oy + 16, "θ", size=12, bold=True, anchor="start"))

    series = three_phase_pts(x0, x1, oy, amp, n=360, cycles=1.0)
    for k in range(3):
        pts = " L ".join("%.1f,%.1f" % (p[0], p[1]) for p in series[k])
        f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2" opacity="0.55"/>' % (pts, PH[k]))
        f.append(text(x0 - 6, series[k][0][1] + 4, PHN[k], size=11, color=PH[k], bold=True, anchor="end"))

    # смуга «хто зверху» (верхня група) — 6 секторів по 60°, кожна фаза 120°
    # верхня група: фаза з найбільшим +sin. Позначимо смужки нижче осі.
    yb1 = 250
    seg = (x1 - x0) / 6.0
    # порядок верхньої групи для sin: L1 max біля 90°, отже центри...
    # обчислимо із даних: для кожного 60°-сектора, яка фаза найвища
    labels_top = []
    for s in range(6):
        xc = x0 + seg * (s + 0.5)
        i = int(360 * (xc - x0) / (x1 - x0))
        ys = [series[k][i][2] for k in range(3)]
        kmax = ys.index(max(ys))
        kmin = ys.index(min(ys))
        labels_top.append((xc, kmax, kmin))
    for s in range(6):
        xa = x0 + seg * s
        xc, kmax, kmin = labels_top[s]
        f.append(line(xa, yb1 - 30, xa, yb1 + 34, color=MUTED, sw=1, dash="3,3"))
        # верхній діод (до +)
        f.append(rect(xa + 3, yb1 - 28, seg - 6, 22, fill="#fdecea" if kmax == 0 else ("#eafaf0" if kmax == 1 else "#eaf0fd"),
                      stroke=PH[kmax], sw=1.4, rx=4))
        f.append(text(xc, yb1 - 12, "D+%s" % PHN[kmax][1], size=10, color=PH[kmax], bold=True))
        # нижній діод (до −)
        f.append(rect(xa + 3, yb1, seg - 6, 22, fill="#fdecea" if kmin == 0 else ("#eafaf0" if kmin == 1 else "#eaf0fd"),
                      stroke=PH[kmin], sw=1.4, rx=4))
        f.append(text(xc, yb1 + 16, "D−%s" % PHN[kmin][1], size=10, color=PH[kmin], bold=True))
    f.append(line(x1, yb1 - 30, x1, yb1 + 34, color=MUTED, sw=1, dash="3,3"))
    f.append(text(ox - 6, yb1 - 12, "до +", size=9.5, color=POS, bold=True, anchor="end"))
    f.append(text(ox - 6, yb1 + 16, "до −", size=9.5, color=NEG, bold=True, anchor="end"))
    f.append(text(x0 + seg * 0.5, yb1 + 46, "60°", size=9.5, color=MUTED))

    render(os.path.join(IMG, "conduction-120.svg"), W, H, *f)


if __name__ == "__main__":
    fig_three_sines()
    fig_b6_bridge()
    fig_output_envelope()
    fig_conduction()
    print("OK: three-sines, b6-bridge, output-envelope, conduction-120 -> img/")
