# -*- coding: utf-8 -*-
"""Фігури до теми «Формування шуму» (галузь digital, книга electronics).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GOLD = "#b8860b"


def polyline(pts, color=INK, sw=2.0, dash=None, fill="none"):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (p, fill, color, sw, d))


def filled_area(pts, baseY, fill, opacity=1.0):
    if not pts:
        return ""
    seq = list(pts) + [(pts[-1][0], baseY), (pts[0][0], baseY)]
    p = " ".join("%.2f,%.2f" % (x, y) for (x, y) in seq)
    return '<polygon points="%s" fill="%s" fill-opacity="%.2f"/>' % (p, fill, opacity)


# ── 1. Дві спектральні картини: рівний шум vs нахилений геть зі смуги ─────────
def fig_spectrum():
    W, H = 820, 380
    f = [text(W / 2, 26, "Та сама порція шуму — два способи розкласти її по частоті",
              size=16, bold=True),
         text(W / 2, 47, "ліворуч шум лежить рівно (білий); праворуч його нахилили вгору — зі смуги сигналу геть",
              size=11, color=MUTED)]

    axW, axH = 320, 210
    baseY = 300
    gap = 90
    x0L = 48
    x0R = x0L + axW + gap
    band = 0.30          # частка смуги — корисна смуга сигналу
    fs_x = lambda x0, frac: x0 + frac * axW

    def panel(x0, shaped, title):
        out = []
        # осі
        out.append(line(x0, baseY, x0 + axW, baseY, color=INK, sw=2))
        out.append(line(x0, baseY, x0, baseY - axH, color=INK, sw=2))
        out.append(arrow(x0 + axW - 2, baseY, x0 + axW + 16, baseY, color=INK, sw=2))
        out.append(text(x0 + axW / 2, baseY + 50, "частота", size=12, color=MUTED))
        out.append(text(x0 + axW + 8, baseY + 18, "fs/2", size=11, color=MUTED, anchor="end"))
        out.append(text(x0 - 6, baseY - axH + 4, "потужність шуму", size=10, color=MUTED, anchor="end"))
        # смуга сигналу (зелена) ліворуч
        bx = fs_x(x0, band)
        out.append(rect(x0, baseY - axH, bx - x0, axH, fill="#eafaf1", stroke=FIELD, sw=1.4, rx=0))
        out.append(line(bx, baseY, bx, baseY - axH, color=FIELD, sw=1.6, dash="4,4"))
        out.append(text((x0 + bx) / 2, baseY - axH + 16, "смуга", size=11, color=FIELD, bold=True))
        out.append(text((x0 + bx) / 2, baseY - axH + 30, "сигналу", size=11, color=FIELD, bold=True))
        # крива шуму
        N = 80
        pts = []
        for i in range(N + 1):
            frac = i / N
            x = x0 + frac * axW
            if shaped:
                # нахил угору: |2 sin(pi f / fs)| ~ зростає від ~0 на DC
                v = math.sin(math.pi * frac / 2.0)        # 0..1 у межах 0..fs/2
                h = (v ** 1.0) * (axH * 0.92)
            else:
                h = axH * 0.40                              # рівна пелена
            pts.append((x, baseY - h))
        # площа шуму
        out.append(filled_area(pts, baseY, "#e9edf2", 1.0))
        out.append(polyline(pts, color="#8893a3", sw=2.0))
        # площа шуму ВСЕРЕДИНІ смуги — підсвітити
        in_band = [(x, y) for (x, y) in pts if x <= bx]
        if in_band:
            out.append(filled_area(in_band, baseY, ("#f6c9c0" if not shaped else "#d8f3e2"), 1.0))
        out.append(text(x0 + axW / 2, baseY - axH - 12, title, size=13, color=INK, bold=True))
        return out, bx

    pL, bxL = panel(x0L, False, "Рівний (білий) шум")
    pR, bxR = panel(x0R, True, "Сформований (нахилений) шум")
    f += pL + pR

    # підписи-висновки під смугою
    f.append(text((x0L + bxL) / 2, H - 16, "у смузі — багато шуму", size=11, color=POS))
    f.append(text((x0R + bxR) / 2, H - 16, "у смузі — майже нема", size=11, color=FIELD))
    render(os.path.join(IMG, "spectrum.svg"), W, H, *f)


# ── 2. Петля з оберненим звʼязком: помилку квантування повертають назад ───────
def fig_loop():
    W, H = 840, 300
    f = [text(W / 2, 26, "Формувач шуму: помилку округлення міряють і повертають у вхід",
              size=16, bold=True),
         text(W / 2, 47, "квантувач відкидає молодші біти; різницю (помилку) фільтрують і додають до наступного відліку",
              size=11, color=MUTED)]

    cy = 150
    # вхід
    f.append(text(34, cy - 14, "вхід", size=11, color=MUTED, anchor="start"))
    f.append(text(34, cy + 2, "(багато біт)", size=10, color=MUTED, anchor="start"))
    f.append(arrow(40, cy, 118, cy, color=MUTED, sw=2))
    # суматор
    f.append(circle(140, cy, 22, fill="#fff7e6", stroke=GOLD, sw=2))
    f.append(text(140, cy + 6, "+", size=22, color=GOLD, bold=True))
    f.append(arrow(162, cy, 250, cy, color=INK, sw=2))
    # квантувач
    b1, w1, h1 = textbox(312, cy, "Квантувач\n(відкидає\nмолодші біти)", size=12, pad=12,
                         fill=FILL, stroke=LINE, sw=2, color=INK)
    f.append(b1)
    # вихід
    f.append(arrow(312 + w1 / 2, cy, 470, cy, color=FIELD, sw=2.2))
    f.append(text(470, cy - 12, "вихід", size=11, color=FIELD, anchor="start", bold=True))
    f.append(text(470, cy + 4, "(мало біт)", size=10, color=FIELD, anchor="start"))
    # вузол-відгалуження виходу
    nodeX = 452
    f.append(circle(nodeX, cy, 3.2, fill=INK, stroke=INK))
    # суматор-помилка: вихід − вхід квантувача = − помилка
    errSumX, errSumY = 452, cy + 90
    f.append(arrow(nodeX, cy + 4, nodeX, errSumY - 20, color=INK, sw=1.8))
    f.append(circle(errSumX, errSumY, 20, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(errSumX, errSumY + 6, "−", size=22, color=POS, bold=True))
    # вхід квантувача теж у цей суматор (щоб дістати помилку)
    preX = 250
    f.append(line(preX, cy, preX, errSumY, color=MUTED, sw=1.5, dash="3,4"))
    f.append(arrow(preX, errSumY, errSumX - 20, errSumY, color=MUTED, sw=1.6))
    f.append(text((preX + errSumX) / 2, errSumY + 22, "помилка квантування e[n]", size=10, color=POS))
    # фільтр у зворотному шляху — окремий блок ліворуч
    fbBoxX = 150
    bF, wF, hF = textbox(fbBoxX, errSumY, "Фільтр H(z)", size=12, pad=12,
                         fill="#eafaf1", stroke=FIELD, sw=2, color=INK)
    f.append(bF)
    f.append(arrow(errSumX - 20, errSumY, fbBoxX + wF / 2, errSumY, color=POS, sw=1.8))
    # від фільтра вгору назад у головний суматор
    f.append(line(fbBoxX - wF / 2, errSumY, 90, errSumY, color=FIELD, sw=1.8))
    f.append(line(90, errSumY, 90, cy + 22, color=FIELD, sw=1.8))
    f.append(arrow(90, cy + 22, 132, cy + 14, color=FIELD, sw=1.8))
    f.append(text(96, (cy + errSumY) / 2, "повертаємо", size=10, color=FIELD, anchor="start"))
    f.append(text(96, (cy + errSumY) / 2 + 14, "у вхід", size=10, color=FIELD, anchor="start"))

    b = fitbox(516, errSumY - 30, 308, 60,
               "H(z) вирішує, куди «виштовхнути» шум.\nЗатримка z⁻¹ → перший порядок, нахил 1.",
               size=12, fill="#f0fff0", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "loop.svg"), W, H, *f)


# ── 3. Часова картина: e[n] − e[n−1] хитається швидко, у середньому ≈ 0 ───────
def fig_time():
    W, H = 820, 340
    f = [text(W / 2, 26, "Перший порядок у часі: цьогоразова помилка гаситься наступного разу",
              size=16, bold=True),
         text(W / 2, 47, "формувач відсилає у вихід e[n] − e[n−1]; сусідні помилки майже однакові, тож різниця мала й швидко-змінна",
              size=11, color=MUTED)]

    x0, baseY = 70, 250
    plotW = 690
    midY = baseY - 70
    amp = 56
    N = 16
    sx = plotW / (N)
    # «справжня» дрібна помилка (повільна) — синусоїда малої амплітуди
    raw = [0.35 * math.sin(2 * math.pi * (i) / N * 1.3 + 0.6) for i in range(N + 1)]
    # сформована: різниця сусідніх → швидка пилка біля нуля
    shaped = [0.0] + [raw[i] - raw[i - 1] for i in range(1, N + 1)]

    # вісь нуля
    f.append(line(x0, midY, x0 + plotW, midY, color="#cfd6de", sw=1.2, dash="3,4"))
    f.append(text(x0 - 8, midY + 4, "0", size=11, color=MUTED, anchor="end"))
    # вісь часу
    f.append(line(x0, baseY, x0 + plotW, baseY, color=INK, sw=1.8))
    f.append(arrow(x0 + plotW, baseY, x0 + plotW + 14, baseY, color=INK, sw=1.8))
    f.append(text(x0 + plotW / 2, baseY + 28, "номер відліку n", size=12, color=MUTED))

    # криві
    rawpts = [(x0 + i * sx, midY - raw[i] / 0.4 * amp) for i in range(N + 1)]
    shppts = [(x0 + i * sx, midY - shaped[i] / 0.4 * amp) for i in range(N + 1)]
    f.append(polyline(rawpts, color=MUTED, sw=2.0, dash="5,4"))
    f.append(polyline(shppts, color=POS, sw=2.4))
    for (px, py) in shppts:
        f.append(circle(px, py, 3.6, fill=POS, stroke=POS))

    # легенда
    f.append(line(x0 + 8, baseY - 200, x0 + 40, baseY - 200, color=MUTED, sw=2.0, dash="5,4"))
    f.append(text(x0 + 46, baseY - 196, "сира помилка (повільна, мала)", size=11, color=MUTED, anchor="start"))
    f.append(line(x0 + 8, baseY - 182, x0 + 40, baseY - 182, color=POS, sw=2.4))
    f.append(text(x0 + 46, baseY - 178, "сформована: e[n] − e[n−1] (швидка, біля нуля)", size=11, color=POS, anchor="start"))

    b = fitbox(x0 + plotW - 268, baseY + 44, 268, 40,
               "Швидке хитання = висока частота: цю енергію легко зрізати фільтром поза смугою.",
               size=10, fill="#fdecea", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "time.svg"), W, H, *f)


# ── 4. Бюджет шуму: однакова повна площа, але в смузі лишилось мало ───────────
def fig_budget():
    W, H = 760, 340
    f = [text(W / 2, 26, "Повна потужність шуму та сама — змінюється лише її РОЗКЛАД",
              size=16, bold=True),
         text(W / 2, 47, "формування не прибирає шум, а пересипає його зі смуги сигналу нагору, де він нешкідливий",
              size=11, color=MUTED)]

    # дві вертикальні «склянки»: смуга сигналу vs поза смугою
    barW = 150
    baseY = 280
    maxH = 190
    xA = 150
    xB = 470
    band_frac = 0.30   # частка осі частот, що є смугою сигналу

    def stack(x, in_band_h, out_h, label):
        out = []
        # поза смугою (верх) — сірий
        out.append(rect(x, baseY - in_band_h - out_h, barW, out_h, fill="#e9edf2", stroke="#cfd6de", sw=1.2, rx=4))
        # у смузі (низ) — червоний/зелений
        col = POS if in_band_h > 40 else FIELD
        fill = "#f6c9c0" if in_band_h > 40 else "#d8f3e2"
        out.append(rect(x, baseY - in_band_h, barW, in_band_h, fill=fill, stroke=col, sw=1.4, rx=4))
        out.append(line(x - 6, baseY, x + barW + 6, baseY, color=INK, sw=1.6))
        out.append(text(x + barW / 2, baseY + 22, label, size=12, color=INK, bold=True))
        return out

    # рівний шум: площа поділена пропорційно ширині смуг → у смузі ~30%
    totalH = maxH
    f += stack(xA, int(totalH * band_frac), int(totalH * (1 - band_frac)), "Рівний шум")
    # сформований: у смузі лишилось ~6%, решта нагорі
    f += stack(xB, int(totalH * 0.06), int(totalH * 0.94), "Сформований шум")

    # підписи частин
    f.append(text(xA + barW + 14, baseY - totalH * band_frac / 2, "у смузі\n(чути)".split("\n")[0],
                  size=11, color=POS, anchor="start", bold=True))
    f.append(text(xA + barW + 14, baseY - totalH * band_frac / 2 + 14, "(шкідливо)", size=10, color=POS, anchor="start"))
    f.append(text(xB + barW + 14, baseY - totalH * 0.06 - 4, "у смузі — мало", size=11, color=FIELD, anchor="start", bold=True))
    f.append(text(xB + barW + 14, baseY - totalH * (0.06 + 0.94 / 2), "решта — нагорі\n(зріжемо)".split("\n")[0],
                  size=10, color=MUTED, anchor="start"))
    f.append(text(xB + barW + 14, baseY - totalH * (0.06 + 0.94 / 2) + 14, "(зріжемо)", size=10, color=MUTED, anchor="start"))

    # стрілка «однакова повна висота»
    f.append(line(xA - 24, baseY, xA - 24, baseY - totalH, color=MUTED, sw=1.4))
    f.append(line(xA - 30, baseY, xA - 18, baseY, color=MUTED, sw=1.4))
    f.append(line(xA - 30, baseY - totalH, xA - 18, baseY - totalH, color=MUTED, sw=1.4))
    f.append(text(xA - 70, baseY - totalH / 2, "та сама", size=10, color=MUTED))
    f.append(text(xA - 70, baseY - totalH / 2 + 13, "повна", size=10, color=MUTED))
    f.append(text(xA - 70, baseY - totalH / 2 + 26, "площа", size=10, color=MUTED))

    render(os.path.join(IMG, "budget.svg"), W, H, *f)


# ── 5. Другий порядок (error-feedback): дві комірки помилки, коефіцієнти 2 і −1 ─
def fig_feedback2():
    W, H = 860, 340
    f = [text(W / 2, 26, "Формувач другого порядку: дві комірки памʼяті помилки",
              size=16, bold=True),
         text(W / 2, 47, "у вхід повертаємо 2·e[n−1] − e[n−2] — рівно розкриті дужки (1 − z⁻¹)²; це прямо лягає на код",
              size=11, color=MUTED)]

    cy = 150
    # вхід
    f.append(text(30, cy - 12, "вхід x[n]", size=11, color=MUTED, anchor="start"))
    f.append(arrow(38, cy, 112, cy, color=MUTED, sw=2))
    # головний суматор
    f.append(circle(134, cy, 22, fill="#fff7e6", stroke=GOLD, sw=2))
    f.append(text(134, cy + 6, "+", size=22, color=GOLD, bold=True))
    f.append(arrow(156, cy, 250, cy, color=INK, sw=2))
    f.append(text(203, cy - 8, "u[n]", size=10, color=MUTED))
    # квантувач
    b1, w1, h1 = textbox(318, cy, "Квантувач\n(відкидає\nмолодші біти)", size=12, pad=12,
                         fill=FILL, stroke=LINE, sw=2, color=INK)
    f.append(b1)
    qx = 318 + w1 / 2
    f.append(arrow(qx, cy, 486, cy, color=FIELD, sw=2.2))
    f.append(text(500, cy - 12, "вихід y[n]", size=11, color=FIELD, anchor="start", bold=True))
    f.append(text(500, cy + 4, "(мало біт)", size=10, color=FIELD, anchor="start"))
    # вузол виходу
    nodeX = 486
    f.append(circle(nodeX, cy, 3.2, fill=INK, stroke=INK))
    # суматор помилки: e[n] = u[n] − y[n]
    errY = cy + 96
    f.append(arrow(nodeX, cy + 4, nodeX, errY - 20, color=INK, sw=1.6))
    f.append(circle(nodeX, errY, 18, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(nodeX, errY + 6, "−", size=20, color=POS, bold=True))
    preX = 250
    f.append(line(preX, cy, preX, errY, color=MUTED, sw=1.4, dash="3,4"))
    f.append(arrow(preX, errY, nodeX - 18, errY, color=MUTED, sw=1.5))
    f.append(text((preX + nodeX) / 2, errY + 22, "e[n] = u[n] − y[n]", size=10, color=POS))

    # дві комірки затримки e1 (z⁻¹) та e2 (z⁻²); ланцюг тягнеться праворуч→ліворуч:
    # e[n] → e1 → e2. Комірки стоять праворуч, повертають угору лівими шинами.
    z1x, z2x = 356, 236
    bz1, wz1, hz1 = textbox(z1x, errY, "z⁻¹\ne1", size=12, pad=10, fill="#eef2ff", stroke=NEG, sw=1.8, color=INK)
    bz2, wz2, hz2 = textbox(z2x, errY, "z⁻¹\ne2", size=12, pad=10, fill="#eef2ff", stroke=NEG, sw=1.8, color=INK)
    f.append(arrow(nodeX - 18, errY, z1x + wz1 / 2, errY, color=POS, sw=1.6))
    f.append(bz1)
    f.append(arrow(z1x - wz1 / 2, errY, z2x + wz2 / 2, errY, color=INK, sw=1.6))
    f.append(bz2)

    # обидва тапи вертаються у суматор ЛІВОРУЧ, повз квантувач (той праворуч):
    # униз під ряд комірок → ліворуч → угору лівою шиною → у суматор зліва.
    # Дві шини на різній висоті/відступі, тож лінії не перетинають блоків.
    bus1x, bot1Y = 92, errY + 44        # зовнішня шина для +2·e1
    bus2x, bot2Y = 116, errY + 22       # внутрішня шина для −1·e2
    # тап +2·e1
    f.append(line(z1x, errY + hz1 / 2, z1x, bot1Y, color=FIELD, sw=1.8))
    b2c = fitbox(z1x - 24, bot1Y - 11, 48, 22, "× 2", size=13, fill="#eafaf1", stroke=FIELD, bold=True)
    f.append(b2c)
    f.append(line(z1x - 24, bot1Y, bus1x, bot1Y, color=FIELD, sw=1.8))
    f.append(line(bus1x, bot1Y, bus1x, cy - 4, color=FIELD, sw=1.8))
    f.append(arrow(bus1x, cy - 4, 118, cy - 3, color=FIELD, sw=1.8))
    # тап −1·e2
    f.append(line(z2x, errY + hz2 / 2, z2x, bot2Y, color=POS, sw=1.8))
    b1c = fitbox(z2x - 30, bot2Y - 11, 60, 22, "× (−1)", size=12, fill="#fdecea", stroke=POS, bold=True)
    f.append(b1c)
    f.append(line(z2x - 30, bot2Y, bus2x, bot2Y, color=POS, sw=1.8))
    f.append(line(bus2x, bot2Y, bus2x, cy + 6, color=POS, sw=1.8))
    f.append(arrow(bus2x, cy + 6, 120, cy + 5, color=POS, sw=1.8))

    b = fitbox(560, errY - 34, 288, 68,
               "У коді: спершу e2 ← e1, тоді e1 ← e[n].\nПоправка входу = 2·e1 − e2. Два рядки стану.",
               size=12, fill="#f0fff0", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "feedback2.svg"), W, H, *f)


# ── 6. Нахили шуму: порядок 0/1/2 — 0, 6, 12 дБ на октаву (лог-лог) ────────────
def fig_slopes():
    W, H = 820, 380
    f = [text(W / 2, 26, "Що дає порядок формувача: крутіший нахил — чистіша смуга",
              size=16, bold=True),
         text(W / 2, 47, "у логарифмічних осях NTF (1 − z⁻¹)ᴸ дає пряму з нахилом L: 0, 6, 12 дБ на октаву",
              size=11, color=MUTED)]

    x0, y0 = 92, 300      # початок осей (лівий-нижній)
    axW, axH = 640, 210
    # осі
    f.append(line(x0, y0, x0 + axW, y0, color=INK, sw=2))
    f.append(line(x0, y0, x0, y0 - axH, color=INK, sw=2))
    f.append(arrow(x0 + axW, y0, x0 + axW + 14, y0, color=INK, sw=2))
    f.append(text(x0 + axW / 2, y0 + 46, "частота (лог) →", size=12, color=MUTED))
    f.append(text(x0 - 74, y0 - axH + 6, "рівень шуму", size=11, color=MUTED, anchor="start"))
    f.append(text(x0 - 74, y0 - axH + 21, "(дБ)", size=11, color=MUTED, anchor="start"))

    # смуга сигналу — вузька, ліворуч (низькі частоти)
    bandW = axW * 0.22
    f.append(rect(x0, y0 - axH, bandW, axH, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=0))
    f.append(line(x0 + bandW, y0 - axH, x0 + bandW, y0, color=FIELD, sw=1.6, dash="4,4"))
    f.append(text(x0 + bandW / 2, y0 - axH + 16, "смуга", size=11, color=FIELD, bold=True))
    f.append(text(x0 + bandW / 2, y0 - axH + 30, "сигналу", size=11, color=FIELD, bold=True))

    # три прямі, що виходять з одного «шарніру» на правому краю смуги
    # у логарифмі: нахил L означає падіння на L*6 дБ за октаву вліво
    hinge_x = x0 + bandW               # точка, де всі три ~зустрічаються
    hinge_y = y0 - axH * 0.62
    top_y = y0 - axH * 0.96
    # права межа (fs/2)
    xr = x0 + axW - 20

    def slope_line(L, color, label, dash=None):
        out = []
        # праворуч від шарніру крива йде вгору з нахилом L; ліворуч — вниз
        # праворуч: на правому краю рівень = hinge + L*(деякий крок)
        rise = L * (axH * 0.16)
        yR = max(top_y - (L - 1) * axH * 0.08, y0 - axH + 8) if L > 0 else hinge_y
        if L == 0:
            pts = [(x0 + 6, hinge_y), (xr, hinge_y)]
        else:
            # від лівого краю смуги вниз, від шарніру вгору до правого краю
            yLeft = hinge_y + L * (axH * 0.14)
            yLeft = min(yLeft, y0 - 8)
            yRight = hinge_y - L * (axH * 0.20)
            yRight = max(yRight, y0 - axH + 8)
            pts = [(x0 + 6, yLeft), (hinge_x, hinge_y), (xr, yRight)]
        out.append(polyline(pts, color=color, sw=2.6, dash=dash))
        return out, pts[-1]

    l0, _ = slope_line(0, MUTED, "порядок 0")
    l1, e1 = slope_line(1, NEG, "порядок 1")
    l2, e2 = slope_line(2, POS, "порядок 2")
    f += l0 + l1 + l2

    # підписи нахилів біля правих кінців
    f.append(text(xr + 6, hinge_y + 4, "0 (білий)", size=11, color=MUTED, anchor="start"))
    f.append(text(e1[0] + 6, e1[1] + 4, "1: 6 дБ/окт", size=11, color=NEG, anchor="start", bold=True))
    f.append(text(e2[0] + 6, e2[1] + 4, "2: 12 дБ/окт", size=11, color=POS, anchor="start", bold=True))

    # стрілки: у смузі порядок 2 нижче за порядок 1 нижче за 0
    f.append(text(x0 + bandW / 2, y0 - 14, "менше шуму", size=10, color=INK))
    f.append(text(x0 + bandW / 2, y0 - 2, "↓ вищий порядок ↓", size=10, color=INK))

    b = fitbox(x0 + bandW + 24, y0 - axH + 8, 300, 46,
               "Кожен +1 до порядку — ще ~6 дБ (≈1 біт)\nчистоти в смузі за кожне подвоєння частоти.",
               size=11, fill="#f0fff0", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "slopes.svg"), W, H, *f)


# ── 7. Фазор: |1 − e^{−jω}| = 2·sin(ω/2) — геометричний корінь усього нахилу ────
def fig_phasor():
    W, H = 760, 470
    f = [text(W / 2, 26, "Звідки береться |1 − z⁻¹| = 2·sin(ω/2): різниця двох векторів на колі",
              size=16, bold=True),
         text(W / 2, 47, "на частоті ω множник (1 − z⁻¹) — це відрізок між точками 1 та e^{−jω} одиничного кола",
              size=11, color=MUTED)]

    cx, cy, R = 250, 250, 150
    # одиничне коло
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="1.5" stroke-dasharray="4,4"/>' % (cx, cy, R, MUTED))
    # осі
    f.append(line(cx - R - 30, cy, cx + R + 34, cy, color="#cfd6de", sw=1))
    f.append(line(cx, cy - R - 30, cx, cy + R + 30, color="#cfd6de", sw=1))
    f.append(text(cx + R + 40, cy + 4, "Re", size=12, color=MUTED, anchor="start"))
    f.append(text(cx + 8, cy - R - 32, "Im", size=12, color=MUTED, anchor="start"))

    # кут ω (помірний, щоб геометрія читалась)
    w = math.radians(58)
    ax, ay = cx + R, cy                                   # точка z = 1 (нульова частота)
    bx, by = cx + R * math.cos(w), cy + R * math.sin(w)   # точка z⁻¹ = e^{−jω}, кут донизу

    # вектор до 1
    f.append(arrow(cx, cy, ax, ay, color=NEG, sw=2.4))
    f.append(text(ax + 10, ay - 8, "1", size=15, bold=True, color=NEG, anchor="start"))
    # вектор до e^{−jω}
    f.append(arrow(cx, cy, bx, by, color=GOLD, sw=2.4))
    f.append(text(bx + 12, by + 16, "z⁻¹ = e⁻ʲω", size=13, bold=True, color=GOLD, anchor="start"))

    # дуга кута ω
    arc_r = 44
    a1x, a1y = cx + arc_r * math.cos(w), cy + arc_r * math.sin(w)
    f.append('<path d="M%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.6"/>' % (cx + arc_r, cy, arc_r, arc_r, a1x, a1y, INK))
    f.append(text(cx + 60, cy + 30, "ω", size=15, bold=True, italic=True, anchor="start"))

    # ХОРДА 1 − e^{−jω} — це і є NTF першого порядку
    f.append(line(ax, ay, bx, by, color=POS, sw=3))
    mmx, mmy = (ax + bx) / 2, (ay + by) / 2
    f.append(text(mmx + 14, mmy - 2, "1 − z⁻¹", size=14, bold=True, color=POS, anchor="start"))
    f.append(text(mmx + 14, mmy + 16, "довжина = 2·sin(ω/2)", size=12, color=POS, anchor="start"))

    # права колонка-пояснення
    tx = 468
    lines = [
        ("Відрізок між двома точками", INK, False),
        ("одиничного кола, розведеними", INK, False),
        ("на кут ω, має довжину рівно", INK, False),
        ("2·sin(ω/2).", POS, True),
        ("", INK, False),
        ("ω → 0  (низька частота):", INK, False),
        ("хорда → 0, шум гаситься.", FIELD, True),
        ("", INK, False),
        ("ω → π  (fₛ/2):", INK, False),
        ("хорда → 2, шум удвічі вищий.", POS, True),
    ]
    yy = 118
    for s, col, bold in lines:
        if s:
            f.append(text(tx, yy, s, size=13, color=col, anchor="start", bold=bold))
        yy += 24

    b = fitbox(30, 402, W - 60, 52,
               "Ось геометричний корінь усього: один доданок «мінус минула помилка» перетворює пропуск шуму\n"
               "на хорду 2·sin(ω/2) — нуль коло DC, максимум коло fₛ/2. Звідси й нахил спектра шуму вгору.",
               size=12, fill="#eef7f0", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "phasor.svg"), W, H, *f)


# ── 8. Модуль NTF: крива 2·sin(πf/fₛ) від частоти, нуль на DC, підйом до fₛ/2 ───
def fig_ntf_magnitude():
    W, H = 878, 420
    f = [text(W / 2, 26, "Модуль передавальної функції шуму: |1 − z⁻¹| = 2·sin(πf/fₛ)",
              size=16, bold=True),
         text(W / 2, 47, "коефіцієнт, з яким петля пропускає шум кожної частоти: нуль коло DC, максимум 2 коло fₛ/2",
              size=11, color=MUTED)]

    ox, oy = 92, 330            # лівий-нижній кут осей
    axW, axH = 590, 250
    # осі
    f.append(line(ox, oy, ox + axW + 18, oy, color=INK, sw=2))          # частота →
    f.append(arrow(ox + axW + 4, oy, ox + axW + 20, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, oy - axH - 18, color=INK, sw=2))          # |NTF| ↑
    f.append(text(ox + axW / 2, oy + 46, "частота  →  fₛ/2", size=12, color=MUTED))
    f.append(text(ox - 8, oy - axH - 6, "|NTF|", size=12, color=MUTED, anchor="end", bold=True))

    # максимум шкали = 2 (значення на fs/2). рівень |NTF|=1 — пунктир.
    y_for = lambda val: oy - axH * (val / 2.0)
    y1 = y_for(1.0)
    f.append(line(ox, y1, ox + axW, y1, color=MUTED, sw=1, dash="5,4"))
    f.append(text(ox + axW + 4, y1 + 4, "1 — рівень рівного (білого) шуму", size=11, color=MUTED, anchor="start"))
    f.append(text(ox - 8, y_for(2.0) + 4, "2", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 8, oy + 4, "0", size=11, color=MUTED, anchor="end"))

    # крива 2·sin(πf), f: 0..0.5 (частка fs) → значення 0..2
    pts = []
    N = 120
    for k in range(N + 1):
        frac = 0.5 * k / N
        val = 2 * math.sin(math.pi * frac)
        x = ox + axW * (frac / 0.5)
        pts.append((x, y_for(val)))
    f.append(filled_area(pts, oy, "#fdecea", 1.0))
    f.append(polyline(pts, color=POS, sw=3))
    f.append(text(ox + axW * 0.60, oy - axH * 0.80, "2·sin(πf/fₛ)", size=15, bold=True, color=POS))

    # смуга сигналу — вузька коло нуля
    bw = axW * 0.13
    f.append(rect(ox, oy - axH, bw, axH, fill="#eafaf1", stroke=FIELD, sw=1.3, rx=0))
    f.append(line(ox + bw, oy - axH, ox + bw, oy, color=FIELD, sw=1.4, dash="4,4"))
    f.append(text(ox + bw / 2, oy - axH + 16, "смуга", size=11, color=FIELD, bold=True))
    f.append(text(ox + bw / 2, oy - axH + 30, "сигналу", size=11, color=FIELD, bold=True))
    f.append(text(ox + bw + 12, oy - 26, "тут |NTF| ≈ 0 → шум майже прибрано", size=12, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "ntf-magnitude.svg"), W, H, *f)


# ── 9. Порядки 0/1/2 у ЛІНІЙНИХ осях: різна форма, ПЛОЩА (повна потужність) та сама ─
def fig_order_slopes():
    W, H = 780, 440
    f = [text(W / 2, 26, "Порядок = степінь (1 − z⁻¹): глибша яма в смузі, крутіший підйом угору",
              size=16, bold=True),
         text(W / 2, 47, "щільність шуму ∝ (2·sin)²ᴸ; площа під усіма кривими однакова — формування перерозподіляє, не прибирає",
              size=11, color=MUTED)]

    ox, oy = 92, 340
    axW, axH = 590, 260
    f.append(line(ox, oy, ox + axW + 18, oy, color=INK, sw=2))
    f.append(arrow(ox + axW + 4, oy, ox + axW + 20, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, oy - axH - 18, color=INK, sw=2))
    f.append(text(ox + axW / 2, oy + 44, "частота  →  fₛ/2", size=12, color=MUTED))
    f.append(text(ox - 8, oy - axH - 6, "щільність шуму", size=12, color=MUTED, anchor="end", bold=True))

    def curve(L, color, dash=None):
        # сира форма (2 sin(pi f))^{2L}; нормуємо, щоб інтеграл був СПІЛЬНИЙ для всіх L
        N = 160
        raw = []
        for k in range(N + 1):
            frac = 0.5 * k / N
            base = 2 * math.sin(math.pi * frac)
            raw.append(base ** (2 * L) if L > 0 else 1.0)
        area = sum(raw) / len(raw)          # середнє ~ інтеграл по [0, fs/2]
        if area <= 0:
            area = 1.0
        norm = [v / area for v in raw]        # тепер у всіх однаковий інтеграл (=1)
        peak = max(max(norm), 1.0)
        top = axH * 0.92
        pts = []
        for k, v in enumerate(norm):
            frac = 0.5 * k / N
            x = ox + axW * (frac / 0.5)
            y = oy - (v / peak) * top
            pts.append((x, y))
        return pts

    # малюємо від вищого порядку до нижчого, щоб нижні лягли поверх
    p2 = curve(2, POS)
    p1 = curve(1, NEG)
    p0 = curve(0, MUTED)
    f.append(polyline(p2, color=POS, sw=2.6))
    f.append(polyline(p1, color=NEG, sw=2.6))
    f.append(polyline(p0, color=MUTED, sw=2.4, dash="6,4"))

    # підписи кривих
    f.append(text(ox + axW * 0.30, oy - axH * 0.34, "порядок 0: рівний шум", size=12, bold=True, color=MUTED, anchor="start"))
    f.append(text(ox + axW * 0.44, oy - axH * 0.60, "порядок 1: ∝ (2·sin)²", size=12, bold=True, color=NEG, anchor="start"))
    f.append(text(ox + axW * 0.55, oy - axH * 0.86, "порядок 2: ∝ (2·sin)⁴", size=12, bold=True, color=POS, anchor="start"))

    # смуга сигналу
    bw = axW * 0.13
    f.append(rect(ox, oy - axH, bw, axH, fill="#eafaf1", stroke=FIELD, sw=1.3, rx=0))
    f.append(line(ox + bw, oy - axH, ox + bw, oy, color=FIELD, sw=1.4, dash="4,4"))
    f.append(text(ox + bw / 2, oy - axH + 16, "смуга", size=11, color=FIELD, bold=True))
    f.append(text(ox + bw / 2, oy - axH + 30, "сигналу", size=11, color=FIELD, bold=True))
    f.append(text(ox + bw / 2, oy - 10, "↓ вищий", size=10, color=INK))
    f.append(text(ox + bw / 2, oy - 0, "порядок ↓", size=10, color=INK))

    b = fitbox(30, H - 44, W - 60, 34,
               "Вищий порядок вигинає криву дужче: у смузі шуму менше, зате за смугою — більше. "
               "Повна потужність (площа) незмінна.",
               size=12, fill="#eef7f0", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "order-slopes.svg"), W, H, *f)


if __name__ == "__main__":
    fig_spectrum()
    fig_loop()
    fig_time()
    fig_budget()
    fig_feedback2()
    fig_slopes()
    fig_phasor()
    fig_ntf_magnitude()
    fig_order_slopes()
    print("OK: 9 figures ->", IMG)
