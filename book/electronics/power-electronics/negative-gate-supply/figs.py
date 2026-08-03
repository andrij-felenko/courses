# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: механізм — dv/dt на вузлі впорскує струм крізь Cgd у затвор ──────
def fig_mechanism():
    W, H = 780, 470
    f = []

    # + шина вгорі
    railtop = 66
    railL, railR = 300, 560
    f.append(line(railL, railtop, railR, railtop, color=POS, sw=2.5))
    f.append(text(railR + 8, railtop + 4, "+ шина", size=14, color=POS, anchor="start", bold=True))

    # верхній ключ
    tx, ty, tw, th = 340, 100, 150, 66
    f.append(rect(tx, ty, tw, th))
    f.append(text(tx + tw / 2, ty + 27, "верхній ключ", size=14, bold=True))
    f.append(text(tx + tw / 2, ty + 48, "щойно ввімкнули", size=12, color=POS))
    f.append(line(tx + tw / 2, railtop, tx + tw / 2, ty))

    # вузол між ключами (switch node)
    node_y = 230
    node_x = tx + tw / 2
    f.append(line(node_x, ty + th, node_x, node_y))
    f.append(line(310, node_y, 560, node_y, color=INK, sw=2.6))
    # підпис вузла — цілком ЛІВОРУЧ від вертикального дроту (x=node_x), щоб дріт його не різав
    nb_body, nb_w, nb_h = textbox(0, 0, "вузол:\nшвидкий стрибок V", size=13, bold=True, stroke=INK)
    nb_cx = node_x - nb_w / 2 - 26
    f.append(textbox(nb_cx, node_y - 34, "вузол:\nшвидкий стрибок V", size=13, bold=True, stroke=INK)[0])
    # стрілка dv/dt — праворуч від вузла, підпис ще правіше (жодна лінія його не ріже)
    dv_x = 560
    f.append(arrow(dv_x, node_y + 66, dv_x, node_y + 8, color=POS, sw=2.4))
    f.append(text(dv_x + 12, node_y + 40, "dV/dt", size=15, color=POS, bold=True, anchor="start"))

    # нижній ключ (OFF)
    bx, by, bw, bh = 340, node_y + 26, 150, 74
    f.append(rect(bx, by, bw, bh))
    f.append(text(bx + bw / 2, by + 25, "нижній ключ", size=14, bold=True))
    f.append(text(bx + bw / 2, by + 46, "має бути ВИМКНЕНИЙ", size=12, color=NEG))
    f.append(line(node_x, node_y, node_x, by))
    # на землю
    gy = by + bh
    f.append(line(bx + bw / 2, gy, bx + bw / 2, gy + 24))
    f.append(line(bx + bw / 2 - 24, gy + 24, bx + bw / 2 + 24, gy + 24, color=INK, sw=2.6))
    f.append(text(bx + bw / 2, gy + 44, "витік / земля", size=12, color=MUTED))

    # Cgd — паразитна ємність від вузла (стоку) до лінії затвора; ліворуч від блоку
    cap_x = 250
    gate_y = by + 22
    f.append(line(cap_x, node_y, cap_x, node_y + 26))                       # від вузла вниз
    f.append(line(cap_x - 22, node_y + 26, cap_x + 22, node_y + 26, color=INK, sw=3))
    f.append(line(cap_x - 22, node_y + 40, cap_x + 22, node_y + 40, color=INK, sw=3))
    f.append(line(cap_x, node_y + 40, cap_x, gate_y))                       # до лінії затвора
    f.append(line(cap_x, gate_y, bx, gate_y))                              # у затвор
    # підпис Cgd — БІЛЯ пластин, але зсунутий ліворуч так, що вертикаль x=cap_x його не ріже
    f.append(text(cap_x - 30, node_y + 37, "Cgd", size=14, color=POS, anchor="end", bold=True))

    # струм-впорскування у затвор
    f.append(arrow(cap_x + 8, gate_y, bx - 6, gate_y, color=POS, sw=2.4))
    f.append(text((cap_x + bx) / 2, gate_y - 9, "струм у затвор", size=12, color=POS))

    # драйвер тримає Voff (ліворуч, нижче лінії затвора — щоб лінія не різала напис)
    f.append(line(cap_x, gate_y, cap_x, gate_y + 40))
    f.append(line(cap_x, gate_y + 40, 150, gate_y + 40))
    drv = textbox(150, gate_y + 82, "драйвер\nтримає Voff", size=12, bold=True, stroke=NEG)
    f.append(line(150, gate_y + 40, 150, gate_y + 82 - drv[2] / 2))
    f.append(drv[0])

    # висновок — праворуч знизу
    concl = textbox(630, node_y + 168,
                    "Vgs стрибає вгору →\nможе перейти поріг →\nхибне ввімкнення",
                    size=13, bold=True, stroke=POS, fill="#fdecea")[0]
    f.append(concl)

    render(os.path.join(IMG, 'mechanism.svg'), W, H, *f)


# ── Фігура 2: gate-хвиля — нульовий Voff проти від'ємного Voff ────────────────
def fig_waveform():
    W, H = 800, 400
    f = []

    x0, x1 = 70, 720
    y_on = 88
    y_th = 246
    y_zero = 298
    y_neg = 344

    def hline(y, label, color, dash=None):
        f.append(line(x0, y, x1, y, color=color, sw=1.4, dash=dash))
        f.append(text(x1 + 8, y + 4, label, size=12, color=color, anchor="start"))

    hline(y_on, "+Von", FIELD)
    hline(y_th, "поріг Vth", MUTED, dash="6 5")
    hline(y_zero, "0 В", MUTED)
    hline(y_neg, "−Voff", NEG)

    # траса A — off у 0 В: бамп угору вище Vth
    lx = 95
    ptsA = [(lx, y_on), (lx + 55, y_on), (lx + 105, y_zero), (lx + 150, y_zero),
            (lx + 198, y_th - 30), (lx + 246, y_zero), (lx + 320, y_zero)]
    dA = "M %.0f %.0f " % ptsA[0] + " ".join("L %.0f %.0f" % p for p in ptsA[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (dA, POS))
    f.append(text(lx + 198, y_th - 42, "бамп > Vth", size=12, color=POS, bold=True))
    f.append(textbox(lx + 150, y_on + 30, "off у 0 В:\nхибне ввімкнення", size=12,
                     bold=True, stroke=POS, fill="#fdecea")[0])

    # траса B — off у −Voff: той самий бамп лишається під Vth
    rx = lx + 360
    ptsB = [(rx, y_on), (rx + 55, y_on), (rx + 105, y_neg), (rx + 150, y_neg),
            (rx + 198, y_neg - 30), (rx + 246, y_neg), (rx + 320, y_neg)]
    dB = "M %.0f %.0f " % ptsB[0] + " ".join("L %.0f %.0f" % p for p in ptsB[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (dB, NEG))
    # підпис праворуч від бампа, у проміжку між 0 В і −Voff — поза кривою і горизонталями
    f.append(text(rx + 300, y_neg - 24, "той самий бамп", size=12,
                  color=NEG, bold=True, anchor="end"))
    f.append(textbox(rx + 150, y_on + 30, "off у −Voff:\nзапас до Vth тримає", size=12,
                     bold=True, stroke=FIELD, fill="#eafaf0")[0])

    render(os.path.join(IMG, 'waveform.svg'), W, H, *f)


# ── Фігура 3: як роблять від'ємну шину — двополярне зміщення довкола витоку ────
def fig_supply():
    W, H = 760, 340
    f = []

    # опорний рівень (витік) — КОРОТКИЙ стуб між двома джерелами, не крізь них
    ref_x = 420
    top_y, mid_y, bot_y = 96, 170, 244
    f.append(line(ref_x, top_y, ref_x, bot_y, color=MUTED, sw=1.6))
    # маркер рівня (коротка риска-опора драйвера)
    f.append(line(ref_x - 14, mid_y, ref_x + 14, mid_y, color=MUTED, sw=1.6))
    # підпис — ЛІВОРУЧ від вертикалі (anchor=end), щоб вертикаль x=ref_x його не різала
    f.append(text(ref_x - 22, mid_y - 4, "рівень витоку", size=12, color=MUTED, anchor="end"))
    f.append(text(ref_x - 22, mid_y + 12, "(0 драйвера)", size=12, color=MUTED, anchor="end"))

    # верхнє джерело +Von — праворуч від опорної вертикалі
    tb = textbox(ref_x + 120, top_y, "+ джерело (+15 В)", size=13, bold=True,
                 stroke=POS, fill="#fdecea")
    f.append(tb[0])
    f.append(line(ref_x, top_y, ref_x + 120 - tb[1] / 2, top_y))

    # нижнє джерело −Voff — праворуч, унизу
    bb = textbox(ref_x + 120, bot_y, "− джерело (−4 В)", size=13, bold=True,
                 stroke=NEG, fill="#eaf0fd")
    f.append(bb[0])
    f.append(line(ref_x, bot_y, ref_x + 120 - bb[1] / 2, bot_y))

    # драйвер + вихід на затвор — праворуч
    drv = textbox(660, mid_y, "драйвер", size=13, bold=True, stroke=INK)
    f.append(line(ref_x + 120 + tb[1] / 2, top_y, 660, mid_y - drv[2] / 2))
    f.append(line(ref_x + 120 + bb[1] / 2, bot_y, 660, mid_y + drv[2] / 2))
    f.append(drv[0])
    f.append(arrow(660, mid_y + drv[2] / 2 + 4, 660, mid_y + drv[2] / 2 + 40, color=INK, sw=2.2))
    f.append(text(660, mid_y + drv[2] / 2 + 58, "→ затвор", size=13, bold=True))

    # пояснення ліворуч
    src = textbox(150, mid_y,
                  "звідки напруги:\n• обмотка з двома\n  виходами,\n• заряд-помпа,\n"
                  "• двополярний\n  DC-DC-модуль",
                  size=12, bold=False, stroke=FIELD, fill="#eafaf0")
    f.append(src[0])

    render(os.path.join(IMG, 'supply.svg'), W, H, *f)


# ── Фігура 4 (вставка math): два режими піку — RC-зріз проти ємнісної стелі ────
def fig_two_regimes():
    W, H = 863, 470
    f = []

    # осі
    ox, oy = 96, 372            # початок осей
    ax_r = 690                  # права межа осі X
    ax_t = 70                   # верх осі Y
    f.append(arrow(ox, oy, ax_r + 20, oy, color=INK, sw=2))
    f.append(arrow(ox, oy, ox, ax_t - 6, color=INK, sw=2))
    f.append(text(ax_r + 24, oy + 5, "тривалість фронту t", size=13, anchor="start", bold=True))
    f.append(text(ox - 10, ax_t - 10, "пік Vgs", size=13, anchor="middle", bold=True))

    # ємнісна стеля — горизонтальна асимптота
    ceil_y = 150
    f.append(line(ox, ceil_y, ax_r, ceil_y, color=NEG, sw=1.6, dash="7 5"))
    f.append(text(ax_r - 6, ceil_y - 10, "стеля дільника: Cgd/(Cgd+Cgs)·ΔV",
                  size=12, color=NEG, anchor="end", bold=True))

    # крива піку: лінійно росте від нуля (швидкий фронт), виходить на стелю (повільний)
    # проста насичувальна форма для ілюстрації: V(t) = ceil * (1 - exp(-t/T))
    import math
    T = 150.0
    pts = []
    for i in range(0, 561, 8):
        tt = i
        v = (oy - ceil_y) * (1 - math.exp(-tt / T))
        pts.append((ox + tt, oy - v))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d, POS))

    # дотична біля нуля — нахил = Cgd·dV/dt·(щось), тобто «швидкий» лінійний закон
    # намалюємо як пунктирну пряму з тим самим початковим нахилом
    slope = (oy - ceil_y) / T
    tx_end = 150
    f.append(line(ox, oy, ox + tx_end, oy - slope * tx_end, color=FIELD, sw=1.6, dash="4 4"))
    # підпис дотичної — у вільному полі ЛІВОРУЧ-ЗНИЗУ, нижче за саму пряму (лінія його не ріже)
    fb = textbox(248, 302, "швидкий фронт:\nпік ≈ Rg·Cgd·(dV/dt)",
                 size=12, bold=True, stroke=FIELD, fill="#eafaf0")
    f.append(fb[0])

    # зони по осі X
    f.append(text(ox + 70, oy + 24, "t ≪ τ_g", size=12, color=MUTED, anchor="middle"))
    f.append(text(ox + 480, oy + 24, "t ≫ τ_g", size=12, color=MUTED, anchor="middle"))
    f.append(line(ox + 250, ax_t + 6, ox + 250, oy, color=MUTED, sw=1.0, dash="3 5"))
    f.append(text(ox + 250, ax_t + 2, "τ_g = Rg·Ciss", size=12, color=MUTED, anchor="middle"))

    # висновок-рамка праворуч унизу, у вільному куті
    box = textbox(560, 322,
                  "менший Rg → нижчий\nнахил → нижчий пік;\nстеля лишається",
                  size=12, bold=True, stroke=POS, fill="#fdecea")[0]
    f.append(box)

    render(os.path.join(IMG, 'two-regimes.svg'), W, H, *f)


# ── Фігура 5 (вставка math): дзвін у колі затвора — овершут над гладкою оцінкою ─
def fig_ringing():
    W, H = 800, 400
    f = []

    x0, x1 = 80, 690
    y_base = 300           # рівень спокою (−Voff умовно тут)
    y_th = 150             # поріг
    f.append(line(x0, y_base, x1 + 20, y_base, color=MUTED, sw=1.4))
    f.append(text(x1 + 24, y_base + 5, "рівень спокою", size=12, color=MUTED, anchor="start"))
    f.append(line(x0, y_th, x1, y_th, color=MUTED, sw=1.4, dash="6 5"))
    f.append(text(x1 + 24, y_th + 5, "поріг Vth", size=12, color=MUTED, anchor="start", bold=True))

    import math
    # гладка оцінка (RC, без L): горб, що НЕ дотягує до порога
    amp_s = (y_base - y_th) * 0.72
    pts_s = []
    for i in range(0, 611, 6):
        tt = i / 610.0
        env = math.exp(-((tt - 0.28) ** 2) / (2 * 0.11 ** 2))   # гаусів горб
        pts_s.append((x0 + i, y_base - amp_s * env))
    d_s = "M %.1f %.1f " % pts_s[0] + " ".join("L %.1f %.1f" % p for p in pts_s[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="6 4"/>' % (d_s, NEG))

    # реальна крива з дзвоном (RLC, недодемпфований): перший пік ВИЩЕ, перестрибує поріг
    amp_r = (y_base - y_th) * 1.16
    pts_r = []
    for i in range(0, 611, 4):
        tt = i / 610.0
        env = math.exp(-(tt - 0.10) * 3.2) if tt > 0.10 else math.exp((tt - 0.10) * 9)
        osc = math.cos(2 * math.pi * (tt - 0.10) / 0.20)
        val = amp_r * env * (osc if tt > 0.10 else 1.0)
        if tt <= 0.10:
            val = amp_r * math.exp((tt - 0.10) * 9)
        pts_r.append((x0 + i, y_base - max(val, -0.28 * amp_r)))
    d_r = "M %.1f %.1f " % pts_r[0] + " ".join("L %.1f %.1f" % p for p in pts_r[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d_r, POS))

    # підписи кривих — рознесені, поза кривими
    f.append(text(x0 + 250, y_th - 22, "з дзвоном (є Lg): перший пік вищий",
                  size=12, color=POS, anchor="middle", bold=True))
    f.append(text(x0 + 470, y_base - amp_s * 0.42, "гладка оцінка (без Lg)",
                  size=12, color=NEG, anchor="middle", bold=True))

    # позначка овершуту
    f.append(text(x0 + 92, y_th - 40, "перескок порога", size=12, color=POS, anchor="middle", bold=True))
    f.append(arrow(x0 + 92, y_th - 30, x0 + 92, y_th - 6, color=POS, sw=1.8))

    render(os.path.join(IMG, 'ringing.svg'), W, H, *f)


if __name__ == '__main__':
    fig_mechanism()
    fig_waveform()
    fig_supply()
    fig_two_regimes()
    fig_ringing()
    print("ok")
