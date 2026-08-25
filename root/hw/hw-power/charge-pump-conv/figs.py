# -*- coding: utf-8 -*-
"""figs.py — фігури до теми «Зарядовий насос» (charge-pump-conv.md) та її вставки.
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Запуск:  python figs.py  →  пише всі SVG у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── спільний символ конденсатора на вертикальному проводі ────────────────────
def vcap(x, ytop, ybot, color=INK, sw=2.6, gap=10, half=14):
    """Конденсатор на вертикалі x між ytop..ybot. Повертає (svg, y-середина пластин)."""
    midy = (ytop + ybot) / 2
    out = [line(x, ytop, x, midy - gap / 2, color=color, sw=1.9),
           line(x - half, midy - gap / 2, x + half, midy - gap / 2, color=color, sw=sw),
           line(x - half, midy + gap / 2, x + half, midy + gap / 2, color=color, sw=sw),
           line(x, midy + gap / 2, x, ybot, color=color, sw=1.9)]
    return "".join(out), midy


def gnd(x, y, color=INK, sw=2.0):
    """Символ землі під точкою (x,y) — три рисочки, що звужуються."""
    return "".join([
        line(x, y, x, y + 12, color=color, sw=sw),
        line(x - 10, y + 12, x + 10, y + 12, color=color, sw=sw),
        line(x - 6, y + 16, x + 6, y + 16, color=color, sw=sw),
        line(x - 2.5, y + 20, x + 2.5, y + 20, color=color, sw=sw)])


def vsource(x, ytop, y, label, color=POS):
    """Маленький «+» вхід зверху проводу x на висоті y із підписом label."""
    return plus(x, y, r=8) + text(x, y - 16, label, size=12, color=color, bold=True)


# ── doubler: дві фази подвоювача (заряд → підняти низ до Vвх → 2·Vвх) ─────────
# Несе вагу: показує МЕХАНІКУ подвоєння — у фазі 2 низ Cf піднято до Vвх,
# тож верх (що тримає ще Vвх) опиняється на 2·Vвх. Це не виразити словами так наочно.
def fig_doubler():
    W, H = 900, 430
    P = []

    def phase(ox, title, sub, sub_color):
        out = [rect(ox + 20, 60, 380, 290, fill="none", stroke="#e4e4e4", sw=2, rx=10),
               text(ox + 210, 86, title, size=13, color=sub_color, bold=True)]
        # вхід Vвх (ліворуч)
        vx = ox + 56
        out.append(vsource(vx, 150, 150, "Vвх"))
        out.append(line(vx, 158, vx, 300, color=INK, sw=2))
        return out, vx

    # ── ФАЗА 1: Cf паралельно входу, заряд до Vвх
    left, vx1 = phase(0, "Фаза 1 — зарядка", "", NEG)
    P += left
    # верхній провід до Cf
    cfx = 190
    P.append(line(vx1, 150, cfx, 150, color=FIELD, sw=2.6))
    cf1, _ = vcap(cfx, 150, 300, color=FIELD)
    P.append(cf1)
    P.append(text(cfx + 24, 200, "Cf", size=13, color=FIELD, bold=True, anchor="start"))
    P.append(text(cfx + 24, 218, "= Vвх", size=11, color=MUTED, anchor="start"))
    P.append(line(cfx, 300, vx1, 300, color=FIELD, sw=2.6))
    # пластини: верх +Vвх, низ 0
    P.append(text(cfx - 22, 162, "+Vвх", size=10, color=INK, anchor="end"))
    P.append(text(cfx - 22, 298, "0", size=10, color=INK, anchor="end"))
    # вихідний конденсатор живить навантаження окремо
    P.append(text(330, 138, "Cвих живить", size=10, color=MUTED))
    P.append(text(330, 152, "навантаження", size=10, color=MUTED))
    co1, _ = vcap(330, 165, 300, color=INK)
    P.append(co1)

    # ── ФАЗА 2: низ Cf піднято до Vвх → верх на 2·Vвх
    right, vx2 = phase(450, "Фаза 2 — підкачка", "", FIELD)
    P += right
    cfx2 = 640
    # низ Cf тепер підключений до Vвх (піднятий), верх іде у вихід
    P.append(line(vx2, 150, cfx2, 250, color=FIELD, sw=2.6))   # вхід → низ Cf
    cf2, _ = vcap(cfx2, 110, 250, color=FIELD)
    P.append(cf2)
    P.append(text(cfx2 + 22, 150, "= 2·Vвх", size=11, color=POS, anchor="start", bold=True))
    P.append(text(cfx2 + 22, 168, "(Vвх+Vвх)", size=10, color=MUTED, anchor="start"))
    P.append(text(cfx2 - 22, 250, "Vвх", size=10, color=INK, anchor="end"))
    P.append(text(cfx2 - 22, 122, "2·Vвх", size=10, color=POS, anchor="end"))
    # верх Cf → вихід
    outx = 800
    P.append(line(cfx2, 110, outx, 110, color=FIELD, sw=2.6))
    P.append(line(outx, 110, outx, 165, color=INK, sw=2))
    P.append(text(outx, 100, "2·Vвх", size=12, color=POS, bold=True))
    co2, _ = vcap(outx, 165, 300, color=INK)
    P.append(co2)
    P.append(text(outx + 18, 235, "Cвих", size=11, color=MUTED, anchor="start"))
    P.append(line(vx2, 300, outx, 300, color=INK, sw=2))

    render("img/doubler.svg", W, H, *P,
           title="Подвоювач: Cf заряджають, тоді його низ піднімають до Vвх")


# ── inverter: дві фази інвертора (заряд → перевернути → −Vвх) ─────────────────
# Несе вагу: показує, що інверсія — це той самий Cf, але ПЕРЕВЕРНУТИЙ:
# верх садять на землю, тож низ провалюється на −Vвх.
def fig_inverter():
    W, H = 900, 420
    P = []

    def frame(ox, title, color):
        return [rect(ox + 20, 60, 380, 280, fill="none", stroke="#e4e4e4", sw=2, rx=10),
                text(ox + 210, 86, title, size=13, color=color, bold=True)]

    # ── ФАЗА 1: заряд до Vвх (як у подвоювача)
    P += frame(0, "Фаза 1 — зарядка", NEG)
    vx1 = 56
    P.append(vsource(vx1, 140, 140, "Vвх"))
    P.append(line(vx1, 148, vx1, 290, color=INK, sw=2))
    cfx = 180
    P.append(line(vx1, 140, cfx, 140, color=FIELD, sw=2.6))
    cf1, _ = vcap(cfx, 140, 290, color=FIELD)
    P.append(cf1)
    P.append(line(cfx, 290, vx1, 290, color=FIELD, sw=2.6))
    P.append(text(cfx + 22, 200, "Cf = Vвх", size=12, color=FIELD, bold=True, anchor="start"))
    P.append(text(cfx - 22, 152, "+Vвх", size=10, color=INK, anchor="end"))
    P.append(text(cfx - 22, 288, "0", size=10, color=INK, anchor="end"))

    # ── ФАЗА 2: переворот — верх на землю, низ → −Vвх
    P += frame(450, "Фаза 2 — переворот", FIELD)
    cfx2 = 600
    # верхню пластину садять на землю
    P.append(line(cfx2, 140, cfx2 - 70, 140, color=FIELD, sw=2.6))
    P += [gnd(cfx2 - 70, 140)]
    cf2, _ = vcap(cfx2, 140, 250, color=FIELD)
    P.append(cf2)
    P.append(text(cfx2 + 20, 132, "0 (земля)", size=10, color=INK, anchor="start"))
    P.append(text(cfx2 + 20, 258, "−Vвх", size=11, color=NEG, anchor="start", bold=True))
    P.append(text(cfx2 - 22, 200, "Cf", size=12, color=FIELD, bold=True, anchor="end"))
    # низ Cf → вихід (−Vвх)
    outx = 810
    P.append(line(cfx2, 250, outx, 250, color=NEG, sw=2.6))
    co2, ym = vcap(outx, 150, 250, color=INK)   # вихідний конденсатор «вгору» до 0-лінії
    P.append(line(outx, 150, outx, 140, color=INK, sw=2))
    P.append(text(outx, 130, "−Vвх", size=12, color=NEG, bold=True))
    P.append(co2)
    P.append(text(outx + 18, 200, "Cвих", size=11, color=MUTED, anchor="start"))

    render("img/inverter.svg", W, H, *P,
           title="Інвертор: зарядити Cf до Vвх, перевернути → −Vвх")


# ── current: струм як заряд, перенесений пакетами Q = Cf·ΔV, f разів/с ────────
# Несе вагу: показує, ЧОМУ струм помпи фундаментально малий — це Cf·ΔV·f.
def fig_current():
    W, H = 880, 400
    P = []
    P.append(line(0, 0, 0, 0, color=BG))  # no-op, тримає список непорожнім
    # формула зверху в рамці
    box = fitbox(70, 50, 740, 34, "Iвих = Q · f = Cf · ΔV · f   (заряд пакета × кількість пакетів за секунду)",
                 size=14, bold=True, fill="#f6f6f6", stroke=MUTED)
    P.append(box)
    # вхід / вихід — резервуари
    P.append(rect(100, 165, 96, 84, fill="#eef3fb", stroke=NEG, sw=2, rx=8))
    P.append(text(148, 150, "ВХІД", size=13, color=INK, bold=True))
    P.append(rect(684, 165, 96, 84, fill="#fbe9e7", stroke=POS, sw=2, rx=8))
    P.append(text(732, 150, "ВИХІД", size=13, color=INK, bold=True))
    # пакети Q, що крокують зліва направо
    qx = [232, 348, 464, 580]
    for x in qx:
        P.append(rect(x, 191, 52, 32, fill="#eef8ef", stroke=FIELD, sw=2, rx=6))
        P.append(text(x + 26, 213, "Q", size=15, color=FIELD, bold=True))
    # стрілки між пакетами і до резервуарів
    P.append(arrow(196, 207, 228, 207))
    for i in range(len(qx) - 1):
        P.append(arrow(qx[i] + 52 + 2, 207, qx[i + 1] - 2, 207))
    P.append(arrow(580 + 52 + 2, 207, 682, 207))
    P.append(text(440, 262, "кожен цикл переносить пакет Q = Cf·ΔV; за секунду таких пакетів f",
                  size=12, color=MUTED))
    # нижній висновок
    note = fitbox(70, 320, 740, 56,
                  "Більше струму → потрібен більший Cf або вища частота f, а обидва мають стелю.\n"
                  "Тому зарядний насос — для малих струмів (міліампери — сотні мА), не для потужності.",
                  size=12, fill="#fbf7ec", stroke="#caa24a")
    P.append(note)
    render("img/current.svg", W, H, *P,
           title="Струм насоса — це заряд, перенесений пакетами")


# ── droop: еквівалент n·Vвх + Rвих і просадка під навантаженням ───────────────
# Несе вагу: пояснює, ЧОМУ є вихідний опір і чому ефективність падає на проміжній напрузі.
def fig_droop():
    W, H = 900, 430
    P = []
    # ── ліворуч: еквівалентна схема
    P.append(rect(40, 60, 380, 300, fill="none", stroke="#e4e4e4", sw=2, rx=10))
    P.append(text(230, 86, "Еквівалент", size=13, color=INK, bold=True))
    # ідеальне джерело n·Vвх (коло)
    P.append(circle(110, 190, 26, fill="none", stroke=INK, sw=2.4))
    P.append(text(110, 186, "n·Vвх", size=11, color=INK, bold=True))
    P.append(text(110, 202, "ідеал", size=9, color=MUTED))
    P.append(line(110, 164, 110, 140, color=INK, sw=2))
    P.append(line(110, 140, 200, 140, color=INK, sw=2))
    # резистор Rвих
    P.append(rect(200, 126, 96, 28, fill="#fbe9e7", stroke=POS, sw=2, rx=5))
    P.append(text(248, 144, "Rвих≈1/(Cf·f)", size=10, color=POS, bold=True))
    P.append(line(296, 140, 356, 140, color=INK, sw=2))
    P.append(text(360, 132, "Vвих", size=11, color=POS, bold=True, anchor="start"))
    # вихідний конденсатор + земля
    P.append(line(356, 140, 356, 230, color=INK, sw=2))
    co, _ = vcap(356, 200, 250, color=INK)
    # власне з'єднання низу джерела й виходу через землю
    P.append(line(110, 216, 110, 320, color=INK, sw=2))
    P.append(line(110, 320, 356, 320, color=INK, sw=2))
    P.append(line(356, 250, 356, 320, color=INK, sw=2))
    P.append(co)
    P.append(text(230, 348, "Vвих = n·Vвх − Iвих·Rвих", size=12.5, color=INK, bold=True))

    # ── праворуч: лінія просадки Vвих(Iвих)
    P.append(rect(460, 60, 420, 300, fill="none", stroke="#e4e4e4", sw=2, rx=10))
    P.append(text(670, 86, "Просадка під навантаженням", size=13, color=INK, bold=True))
    ax, ay0, ay1, axr = 510, 110, 300, 850
    P.append(arrow(ax, 306, ax, 108))     # вісь Vвих
    P.append(arrow(ax, 300, axr, 300))    # вісь Iвих
    P.append(text(502, 118, "Vвих", size=11, color=INK, bold=True, anchor="end"))
    P.append(text(axr + 2, 304, "Iвих", size=11, color=INK, bold=True, anchor="start"))
    # рівень ідеалу
    P.append(line(ax, 130, axr, 130, color="#e4e4e4", sw=1.2))
    P.append(text(ax + 6, 124, "n·Vвх (без струму)", size=10, color=MUTED, anchor="start"))
    # похила лінія просадки
    P.append('<polyline points="510,130 840,250" fill="none" stroke="%s" '
             'stroke-width="3" stroke-linejoin="round"/>' % POS)
    P.append(text(700, 208, "падає з Iвих", size=11, color=POS, bold=True))
    P.append(text(670, 326, "ККД ≈ Vвих/(n·Vвх): далеко від кратного — палить, як лінійний",
                  size=10.5, color=INK))

    note = fitbox(70, 392, 760, 28,
                  "Насос ефективний, лише коли вихід близький до n·Vвх; на проміжній напрузі зайве йде в тепло, як у лінійного стабілізатора",
                  size=11, fill="#fbf7ec", stroke="#caa24a")
    P.append(note)
    render("img/droop.svg", W, H, *P,
           title="Насос = ідеальне джерело n·Vвх із вихідним опором")


# ── ratios: набір фіксованих коефіцієнтів і коли брати насос ─────────────────
# Несе вагу: зводить нішу — дискретні кратності + чітке «брати / не брати».
def fig_ratios():
    W, H = 900, 420
    P = []
    P.append(text(450, 64, "Досяжні коефіцієнти (більше конденсаторів → більше варіантів):",
                  size=12.5, color=INK, bold=True))
    chips = [("×½", NEG), ("×1", MUTED), ("×1.5", NEG), ("×2", POS), ("×3", POS), ("−1", NEG)]
    cw, gap, x0 = 96, 24, 0
    total = len(chips) * cw + (len(chips) - 1) * gap
    x = (W - total) / 2
    for label, col in chips:
        P.append(rect(x, 84, cw, 44, fill="#f6f9fc", stroke=col, sw=2, rx=10))
        P.append(text(x + cw / 2, 113, label, size=16, color=col, bold=True))
        x += cw + gap
    # ✓ брати
    P.append(rect(40, 156, 410, 180, fill="#eef8ef", stroke=FIELD, sw=1.8, rx=10))
    P.append(text(245, 182, "✓ Брати, коли:", size=13, color=FIELD, bold=True))
    for i, ln in enumerate([
            "• немає місця/бажання на котушку (мала, тиха, дешева)",
            "• струм малий: міліампери — сотні мА",
            "• зсув ЖК-дисплея, від'ємна шина для ОП,",
            "• напруга програмування flash, підкачка затвора"]):
        P.append(text(60, 210 + i * 26, ln, size=11, color=INK, anchor="start"))
    # ✗ не брати
    P.append(rect(470, 156, 410, 180, fill="#fbe9e7", stroke=POS, sw=1.8, rx=10))
    P.append(text(675, 182, "✗ Не брати, коли:", size=13, color=POS, bold=True))
    for i, ln in enumerate([
            "• потрібен помітний струм / потужність",
            "• потрібен високий ККД на проміжній напрузі",
            "• → тут виграють перетворювачі з котушкою",
            "•   (buck / boost / buck-boost)"]):
        P.append(text(490, 210 + i * 26, ln, size=11, color=INK, anchor="start"))
    note = fitbox(70, 384, 760, 26,
                  "Насос — нішевий інструмент для малих тихих допоміжних шин без котушки; силову роботу лишають котушковим топологіям",
                  size=11, fill="#eef8ef", stroke=FIELD)
    P.append(note)
    render("img/ratios.svg", W, H, *P,
           title="Що вміє насос і коли його брати")


# ── comp-hookup: пінаут 7660 + дві обв'язки (інвертор / подвоювач) ────────────
# Несе вагу: показує ОДНУ й ту саму 8-вивідну деталь у двох увімкненнях.
def fig_hookup():
    W, H = 960, 540
    parts = []

    def chip(cx, cy, title, vin_label, vout_label, vin_pin, vout_pin):
        out = []
        bw, bh = 150, 200
        x, y = cx - bw / 2, cy - bh / 2
        out.append(rect(x, y, bw, bh, fill=FILL, stroke=INK, sw=2, rx=8))
        out.append('<path d="M%.1f %.1f a 10 10 0 0 0 20 0" fill="none" '
                   'stroke="%s" stroke-width="2"/>' % (cx - 10, y, INK))
        out.append(text(cx, cy - 4, "7660", size=15, color=MUTED, bold=True))
        out.append(text(cx, cy + 14, "клас", size=11, color=MUTED))

        left_names  = ["NC/BOOST", "CAP+", "GND", "CAP−"]
        right_names = ["V+", "OSC", "LV", "VOUT"]
        left_nums   = [1, 2, 3, 4]
        right_nums  = [8, 7, 6, 5]
        ys = [y + bh * (i + 0.5) / 4 for i in range(4)]

        for i, yy in enumerate(ys):
            out.append(line(x - 16, yy, x, yy, color=INK, sw=2))
            out.append(text(x - 6, yy - 5, str(left_nums[i]), size=10,
                            color=MUTED, anchor="end"))
            out.append(text(x + 6, yy + 4, left_names[i], size=11, color=INK,
                            anchor="start"))
            out.append(line(x + bw, yy, x + bw + 16, yy, color=INK, sw=2))
            out.append(text(x + bw + 6, yy - 5, str(right_nums[i]), size=10,
                            color=MUTED, anchor="start"))
            out.append(text(x + bw - 6, yy + 4, right_names[i], size=11,
                            color=INK, anchor="end"))

        cfx = x - 52
        out.append(line(x - 16, ys[1], cfx, ys[1], color=INK, sw=2))
        out.append(line(x - 16, ys[3], cfx, ys[3], color=INK, sw=2))
        out.append(line(cfx, ys[1], cfx, ys[1] + 14, color=INK, sw=2))
        out.append(line(cfx, ys[3], cfx, ys[3] - 14, color=INK, sw=2))
        out.append(line(cfx - 13, ys[1] + 14, cfx + 13, ys[1] + 14, color=INK, sw=2.5))
        out.append(line(cfx - 13, ys[3] - 14, cfx + 13, ys[3] - 14, color=INK, sw=2.5))
        out.append(text(cfx - 20, (ys[1] + ys[3]) / 2 + 4, "Cf", size=12,
                        color=NEG, anchor="end", italic=True))

        gx = x - 40
        out.append(line(x - 16, ys[2], gx, ys[2], color=INK, sw=2))
        out.append(line(gx, ys[2], gx, ys[2] + 12, color=INK, sw=2))
        out.append(line(gx - 9, ys[2] + 12, gx + 9, ys[2] + 12, color=INK, sw=2))
        out.append(line(gx - 5, ys[2] + 16, gx + 5, ys[2] + 16, color=INK, sw=2))

        pin_y = {8: ys[0], 7: ys[1], 6: ys[2], 5: ys[3]}
        iy = pin_y[vin_pin]
        out.append(line(x + bw + 16, iy, x + bw + 60, iy, color=POS, sw=2.5))
        out.append(plus(x + bw + 70, iy, r=8))
        out.append(text(x + bw + 70, iy - 16, vin_label, size=12, color=POS,
                        anchor="middle", bold=True))
        oy = pin_y[vout_pin]
        out.append(line(x + bw + 16, oy, x + bw + 60, oy, color=INK, sw=2.5))
        coutx = x + bw + 60
        out.append(line(coutx, oy, coutx, oy + 22, color=INK, sw=2))
        out.append(line(coutx - 12, oy + 22, coutx + 12, oy + 22, color=INK, sw=2.5))
        out.append(line(coutx - 12, oy + 28, coutx + 12, oy + 28, color=INK, sw=2.5))
        out.append(line(coutx, oy + 28, coutx, oy + 38, color=INK, sw=2))
        out.append(line(coutx - 8, oy + 38, coutx + 8, oy + 38, color=INK, sw=2))
        out.append(line(coutx - 4, oy + 42, coutx + 4, oy + 42, color=INK, sw=2))
        out.append(text(coutx + 18, oy + 6, "Cout", size=11, color=MUTED,
                        anchor="start", italic=True))
        col = NEG if vout_label.startswith("−") else POS
        out.append(text(coutx, oy - 12, vout_label, size=13, color=col,
                        anchor="middle", bold=True))

        out.append(text(cx, y - 22, title, size=15, color=INK, bold=True))
        return out

    parts += chip(255, 300, "Інвертор:  −Vвх", "Vвх", "−Vвх", vin_pin=8, vout_pin=5)
    parts += chip(705, 300, "Подвоювач:  2·Vвх", "Vвх", "2·Vвх", vin_pin=5, vout_pin=8)
    parts.append(line(W / 2, 70, W / 2, H - 30, color=MUTED, sw=1.2, dash="6,6"))

    render("img/comp-hookup.svg", W, H, *parts,
           title="Насос 7660-класу: одна деталь — дві обв'язки")


if __name__ == "__main__":
    fig_doubler()
    fig_inverter()
    fig_current()
    fig_droop()
    fig_ratios()
    fig_hookup()
    print("generated: doubler, inverter, current, droop, ratios, comp-hookup")
