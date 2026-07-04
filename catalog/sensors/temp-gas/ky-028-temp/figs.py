# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-028 — цифровий давач температури».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def resistor(cx, cy, w=34, h=15, horiz=False):
    """Прямокутник-резистор із центром (cx,cy)."""
    if horiz:
        w, h = h * 2.2, w * 0.44
    return rect(cx - w / 2, cy - h / 2, w, h, fill=FILL, stroke=INK, sw=1.6, rx=3)


# ── 1. Принципова схема KY-028 ────────────────────────────────────────────────
def fig_schematic():
    W, H = 980, 600
    f = [text(W / 2, 30, "Схема KY-028: NTC-термістор + компаратор LM393 + гвинтик-поріг",
              size=16, bold=True)]

    # рейки живлення
    vcc_y, gnd_y = 92, 548
    left_x, right_x = 150, 900
    f.append(line(left_x, vcc_y, right_x, vcc_y, color=POS, sw=2.2))
    f.append(text(left_x - 8, vcc_y + 4, "+V", size=13, bold=True, color=POS, anchor="end"))
    f.append(line(left_x, gnd_y, right_x, gnd_y, color=INK, sw=2.2))
    f.append(text(left_x - 8, gnd_y + 4, "GND", size=13, bold=True, anchor="end"))

    # ── термісторний дільник ──
    dx = 300
    node_y = (vcc_y + gnd_y) / 2 - 6           # вузол «голос температури»
    # термістор (верхнє плече): від +V до вузла, намистина-коло з написом NTC
    f.append(line(dx, vcc_y, dx, node_y - 50, color=INK, sw=2))
    f.append(circle(dx, node_y - 72, 20, fill="#f6efe6", stroke=INK, sw=2))
    f.append(line(dx, node_y - 52, dx, node_y, color=INK, sw=2))
    # маленька діагональна стрілка «змінний з температури» — праворуч від намистини, не крізь текст
    f.append(arrow(dx + 34, node_y - 54, dx + 6, node_y - 90, color=POS))
    f.append(text(dx + 40, node_y - 96, "NTC 10 кΩ", size=10.5, bold=True, color=POS, anchor="start"))
    f.append(text(dx + 40, node_y - 80, "опір ↓ з теплом", size=9.5, color=MUTED, anchor="start"))
    # постійний резистор (нижнє плече): від вузла до GND
    f.append(line(dx, node_y, dx, node_y + 34, color=INK, sw=2))
    f.append(resistor(dx, node_y + 52))
    f.append(text(dx + 26, node_y + 56, "R", size=11, bold=True, anchor="start"))
    f.append(line(dx, node_y + 70, dx, gnd_y, color=INK, sw=2))
    # вузол
    f.append(circle(dx, node_y, 4, fill=INK, stroke=INK))

    # лінія від вузла праворуч до входу компаратора (+вхід)
    cmp_x = 560
    in_plus_y = node_y - 22
    in_minus_y = node_y + 22
    f.append(line(dx, node_y, dx + 70, node_y, color=FIELD, sw=2))
    f.append(line(dx + 70, node_y, dx + 70, in_plus_y, color=FIELD, sw=2))
    f.append(line(dx + 70, in_plus_y, cmp_x, in_plus_y, color=FIELD, sw=2))

    # відгалуження на AO (навантажений відвід) — ліворуч і ВГОРУ, у чисту зону над рейкою
    ao_x = 200
    ao_y = vcc_y - 6
    f.append(line(dx, node_y, ao_x, node_y, color=MUTED, sw=2, dash="4 3"))
    f.append(line(ao_x, node_y, ao_x, ao_y, color=MUTED, sw=2, dash="4 3"))
    f.append(circle(ao_x, ao_y, 5, fill=BG, stroke=MUTED, sw=2))
    f.append(text(ao_x - 12, ao_y + 4, "AO", size=12, bold=True, color=MUTED, anchor="end"))
    # анотація AO — окремим блоком у лівому-нижньому вільному куті
    box = textbox(230, gnd_y - 66, "AO — навантажений відвід:\nпритлумлений і перевернутий\n(відносний тренд, НЕ °C)",
                  size=10, pad=9, fill="#f6f7f9", stroke=MUTED, color=MUTED)
    f.append(box[0])

    # ── по центру: гвинтик-поріг (потенціометр) → −вхід ──
    px = 430
    f.append(line(px, vcc_y, px, node_y + 100, color=INK, sw=2))
    f.append(resistor(px, node_y + 122, w=44))
    # стрілка движка
    f.append(arrow(px + 36, node_y + 104, px + 6, node_y + 120, color=FIELD))
    f.append(text(px + 44, node_y + 100, "гвинтик", size=10.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(px + 44, node_y + 114, "3296W", size=9.5, color=MUTED, anchor="start"))
    f.append(line(px, node_y + 144, px, gnd_y, color=INK, sw=2))
    # движок → −вхід компаратора
    wiper_y = node_y + 122
    f.append(line(px, wiper_y, px + 40, wiper_y, color=NEG, sw=2))
    f.append(line(px + 40, wiper_y, px + 40, in_minus_y, color=NEG, sw=2))
    f.append(line(px + 40, in_minus_y, cmp_x, in_minus_y, color=NEG, sw=2))
    f.append(circle(px, wiper_y, 3.5, fill=NEG, stroke=NEG))
    f.append(text(px + 46, in_minus_y - 6, "поріг", size=10.5, bold=True, color=NEG, anchor="start"))

    # ── компаратор LM393 (трикутник) ──
    tri_w, tri_h = 100, 110
    tx0 = cmp_x
    ty_top = node_y - tri_h / 2
    ty_bot = node_y + tri_h / 2
    tip_x = tx0 + tri_w
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#eef2f6" stroke="%s" stroke-width="2"/>'
             % (tx0, ty_top, tx0, ty_bot, tip_x, node_y, INK))
    f.append(text(tx0 + 40, node_y - 4, "LM393", size=12, bold=True))
    f.append(text(tx0 + 40, node_y + 14, "компар.", size=10, color=MUTED))
    # символи входів — ВСЕРЕДИНІ трикутника (праворуч від лівого краю), щоб вхідні дроти їх не перетинали
    f.append(text(tx0 + 14, in_plus_y + 5, "+", size=15, bold=True, color=FIELD, anchor="start"))
    f.append(text(tx0 + 14, in_minus_y + 5, "−", size=15, bold=True, color=NEG, anchor="start"))

    # вихід компаратора → вузол DO
    out_x = tip_x
    do_node_x = 760
    f.append(line(out_x, node_y, do_node_x, node_y, color=INK, sw=2.2))
    # підтяжка виходу (відкритий колектор) до +V
    f.append(line(do_node_x, node_y, do_node_x, node_y - 64, color=INK, sw=2))
    f.append(resistor(do_node_x, node_y - 84, horiz=False))
    f.append(text(do_node_x + 26, node_y - 80, "підтяжка", size=10, color=MUTED, anchor="start"))
    f.append(line(do_node_x, node_y - 104, do_node_x, vcc_y, color=INK, sw=2))
    f.append(circle(do_node_x, node_y, 4, fill=INK, stroke=INK))
    # вивід DO назовні
    f.append(line(do_node_x, node_y, right_x - 20, node_y, color=INK, sw=2.2))
    f.append(circle(right_x - 20, node_y, 5, fill=BG, stroke=INK, sw=2))
    f.append(text(right_x - 12, node_y - 12, "DO", size=12, bold=True, anchor="start"))
    f.append(text(right_x - 12, node_y + 16, "0/1 — поріг", size=9.5, color=MUTED, anchor="start"))

    # LED2 від вузла DO вниз до GND (індикатор порогу)
    led2_x = 838
    f.append(line(do_node_x, node_y, led2_x, node_y, color=INK, sw=1.6))
    f.append(line(led2_x, node_y, led2_x, node_y + 44, color=INK, sw=1.6))
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#fdecea" stroke="%s" stroke-width="1.6"/>'
             % (led2_x - 8, node_y + 44, led2_x + 8, node_y + 44, led2_x, node_y + 60, POS))
    f.append(line(led2_x, node_y + 60, led2_x, gnd_y, color=INK, sw=1.6))
    f.append(text(led2_x + 12, node_y + 52, "LED2", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(led2_x + 12, node_y + 66, "(поріг)", size=9, color=MUTED, anchor="start"))

    # LED1 живлення (окремо ліворуч від рейки, суто індикатор)
    l1x = 660
    f.append(line(l1x, vcc_y, l1x, vcc_y + 26, color=INK, sw=1.6))
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#eafaf0" stroke="%s" stroke-width="1.6"/>'
             % (l1x - 8, vcc_y + 26, l1x + 8, vcc_y + 26, l1x, vcc_y + 42, FIELD))
    f.append(line(l1x, vcc_y + 42, l1x, gnd_y, color=INK, sw=1.2, dash="3 4"))
    f.append(text(l1x + 12, vcc_y + 24, "LED1", size=10, bold=True, color=FIELD, anchor="start"))
    f.append(text(l1x + 12, vcc_y + 38, "(живлення)", size=9, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, 'schematic.svg'), W, H, *f)


# ── 2. Підключення KY-028 до мікроконтролера ──────────────────────────────────
def fig_wiring():
    W, H = 860, 470
    f = [text(W / 2, 30, "Підключення KY-028: чотири дроти до мікроконтролера",
              size=16, bold=True)]

    # плата модуля (ліворуч)
    mx, my, mw, mh = 70, 110, 250, 250
    f.append(rect(mx, my, mw, mh, fill="#e9f0fb", stroke=NEG, sw=2, rx=14))
    f.append(text(mx + mw / 2, my + 26, "модуль KY-028", size=13, bold=True, color=NEG))
    # намистина-термістор
    f.append(circle(mx + 46, my + 78, 15, fill="#f6efe6", stroke=INK, sw=2))
    f.append(text(mx + 46, my + 82, "NTC", size=9.5, bold=True))
    f.append(text(mx + 46, my + 106, "термістор", size=9, color=MUTED))
    # мікросхема
    f.append(rect(mx + 110, my + 62, 60, 34, fill=FILL, stroke=INK, sw=1.6, rx=4))
    f.append(text(mx + 140, my + 83, "LM393", size=10, bold=True))
    # гвинтик
    f.append(circle(mx + 200, my + 78, 14, fill="#eafaf0", stroke=FIELD, sw=2))
    f.append(line(mx + 192, my + 78, mx + 208, my + 78, color=FIELD, sw=2))
    f.append(text(mx + 200, my + 106, "гвинтик", size=9, color=FIELD))

    # гребінка на 4 штирі (праворуч від модуля)
    pins = ["AO", "G", "+", "DO"]
    pcols = [MUTED, INK, POS, INK]
    py0 = my + 140
    pgap = 26
    px = mx + mw
    pin_y = {}
    for i, (nm, col) in enumerate(zip(pins, pcols)):
        yy = py0 + i * pgap
        pin_y[nm] = yy
        f.append(circle(px, yy, 6, fill=BG, stroke=col, sw=2))
        f.append(text(px - 16, yy + 4, nm, size=11, bold=True, color=col, anchor="end"))

    # плата МК (праворуч)
    bx, by, bw, bh = 560, 90, 240, 300
    f.append(rect(bx, by, bw, bh, fill="#eef7f0", stroke=FIELD, sw=2, rx=14))
    f.append(text(bx + bw / 2, by + 26, "мікроконтролер", size=13, bold=True, color=FIELD))
    # входи плати
    board_pins = [("A0", "аналоговий вхід", "#8a6d3b"),
                  ("D2", "цифровий вхід", INK),
                  ("5V / 3.3V", "живлення", POS),
                  ("GND", "земля", INK)]
    by0 = by + 70
    bgap = 60
    bpin_y = {}
    for i, (nm, desc, col) in enumerate(board_pins):
        yy = by0 + i * bgap
        bpin_y[nm] = yy
        f.append(circle(bx, yy, 6, fill=BG, stroke=col, sw=2))
        f.append(text(bx + 16, yy - 3, nm, size=11, bold=True, color=col, anchor="start"))
        f.append(text(bx + 16, yy + 13, desc, size=9.5, color=MUTED, anchor="start"))

    # дроти пін→пін (ведемо повз написи, з ламаними, кожен на своїй висоті-коридорі)
    def wire(p_from, p_to, col, corridor):
        x1, y1 = px, pin_y[p_from]
        x2, y2 = bx, bpin_y[p_to]
        f.append(line(x1, y1, corridor, y1, color=col, sw=2.4))
        f.append(line(corridor, y1, corridor, y2, color=col, sw=2.4))
        f.append(line(corridor, y2, x2, y2, color=col, sw=2.4))

    wire("+",  "5V / 3.3V", POS,   410)
    wire("G",  "GND",       INK,   470)
    wire("DO", "D2",        INK,   440)
    wire("AO", "A0",        "#8a6d3b", 380)

    # підказки внизу — короткими рядками, щоб рамка не вилазила за полотно
    b2 = textbox(W / 2, 420,
                 ["Живлення бери під логіку плати (рівень DO/AO = напрузі живлення).",
                  "Поріг виставляй гвинтиком по LED2. Треба лише «так/ні» — AO можна не чіпати."],
                 size=10.5, pad=9, fill="#fbfbfc", stroke=MUTED, color=INK)
    f.append(b2[0])

    return render(os.path.join(IMG, 'wiring.svg'), W, H, *f)


# ── 3. Гістерезис: один поріг дрижить, два — ні ───────────────────────────────
def fig_hysteresis():
    W, H = 980, 470
    f = [text(W / 2, 30, "Гістерезис: чому один поріг дрижить, а два — ні",
              size=16, bold=True)]

    import math
    x0, x1 = 90, 890
    N = 560
    # СПІЛЬНИЙ сигнал: температура повільно повзе вгору й дрібно тремтить.
    # y більше = холодніше (умовно), «гарячий» бік — угорі; тут малюємо
    # як зростання «температурної напруги» знизу вгору повз поріг.
    def sig(i, mid, span):
        # повільне зростання від -span до +span + дрібний шум
        base = -span * math.cos(math.pi * i / N)          # плавний підйом
        noise = 3.0 * math.sin(i / 3.1) + 1.6 * math.sin(i / 1.3)
        return mid - (base + noise)                        # менше y = вище

    # -- верхня панель: ОДИН поріг --
    tmid = 110
    thr = tmid
    f.append(text(x0 - 2, 62, "ОДИН поріг — біт дрижить на межі", size=12, bold=True, color=POS, anchor="start"))
    f.append(line(x0, thr, x1, thr, color=POS, sw=1.8, dash="6 4"))
    f.append(text(x1 + 6, thr + 4, "поріг", size=10.5, bold=True, color=POS, anchor="start"))
    pts, states1 = [], []
    for i in range(N + 1):
        xx = x0 + (x1 - x0) * i / N
        yy = sig(i, tmid, 30)
        pts.append("%.1f,%.1f" % (xx, yy))
        states1.append(1 if yy < thr else 0)               # вище порогу = «гаряче»
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts), INK))
    # DO як реальний ступінчастий трек цього ж сигналу — багато перемикань біля межі
    dy = 168
    f.append(text(x0 - 2, dy + 4, "DO", size=11, bold=True, anchor="start"))
    up, down = dy - 9, dy + 9
    prev = states1[0]
    trk = ["%.1f,%.1f" % (x0, down if prev == 0 else up)]
    for i in range(1, N + 1):
        xx = x0 + (x1 - x0) * i / N
        if states1[i] != prev:
            trk.append("%.1f,%.1f" % (xx, down if prev == 0 else up))
            trk.append("%.1f,%.1f" % (xx, up if states1[i] == 1 else down))
            prev = states1[i]
    trk.append("%.1f,%.1f" % (x1, up if prev == 1 else down))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(trk), NEG))
    f.append(text((x0 + x1) / 2, dy + 30, "багато перемикань — «тремтіння»", size=10.5, color=NEG))

    # -- нижня панель: ДВА пороги --
    bmid = 300
    hi = bmid - 13
    lo = bmid + 13
    f.append(text(x0 - 2, 252, "ДВА пороги (гістерезис) — один чистий перехід", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(line(x0, hi, x1, hi, color=POS, sw=1.8, dash="6 4"))
    f.append(text(x1 + 6, hi + 4, "верх ↑", size=10.5, bold=True, color=POS, anchor="start"))
    f.append(line(x0, lo, x1, lo, color=NEG, sw=1.8, dash="6 4"))
    f.append(text(x1 + 6, lo + 4, "низ ↓", size=10.5, bold=True, color=NEG, anchor="start"))
    pts2, states2 = [], []
    st = 0                                                  # стан з гістерезисом
    for i in range(N + 1):
        xx = x0 + (x1 - x0) * i / N
        yy = sig(i, bmid, 30)
        pts2.append("%.1f,%.1f" % (xx, yy))
        if st == 0 and yy < hi:                            # піднявся вище ВЕРХНЬОГО
            st = 1
        elif st == 1 and yy > lo:                          # опустився нижче НИЖНЬОГО
            st = 0
        states2.append(st)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts2), INK))
    dy2 = 360
    f.append(text(x0 - 2, dy2 + 4, "DO", size=11, bold=True, anchor="start"))
    up2, down2 = dy2 - 9, dy2 + 9
    prev = states2[0]
    trk2 = ["%.1f,%.1f" % (x0, down2 if prev == 0 else up2)]
    for i in range(1, N + 1):
        xx = x0 + (x1 - x0) * i / N
        if states2[i] != prev:
            trk2.append("%.1f,%.1f" % (xx, down2 if prev == 0 else up2))
            trk2.append("%.1f,%.1f" % (xx, up2 if states2[i] == 1 else down2))
            prev = states2[i]
    trk2.append("%.1f,%.1f" % (x1, up2 if prev == 1 else down2))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(trk2), FIELD))
    f.append(text((x0 + x1) / 2, dy2 + 30, "мертва зона між порогами гасить тремтіння", size=10.5, color=FIELD))

    return render(os.path.join(IMG, 'hysteresis.svg'), W, H, *f)


# ── 4. Автовизначення полярності DO на старті ─────────────────────────────────
def fig_polarity():
    W, H = 960, 420
    f = [text(W / 2, 30, "Автовизначення полярності DO при старті",
              size=16, bold=True)]

    # крок 1: замір спокою
    b1 = textbox(200, 110,
                 ["СТАРТ", "прочитати DO", "поки поріг ще", "не перетнуто"],
                 size=12, pad=12, bold=True, fill="#eef4ff", stroke=NEG)
    f.append(b1[0])

    # стрілка вниз до розгалуження
    f.append(arrow(200, 110 + b1[2] / 2, 200, 205, color=INK))

    # ромб-рішення
    dcx, dcy = 200, 235
    f.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (dcx, dcy - 30, dcx + 90, dcy, dcx, dcy + 30, dcx - 90, dcy, FILL, INK))
    f.append(text(dcx, dcy - 2, "спокій", size=11, bold=True))
    f.append(text(dcx, dcy + 14, "= ?", size=11, bold=True))

    # гілка «спокій = HIGH»
    f.append(line(dcx + 90, dcy, 470, dcy, color=INK, sw=1.8))
    f.append(text(360, dcy - 8, "HIGH", size=11, bold=True, color=POS))
    b2 = textbox(620, 175,
                 ["спокій = HIGH  →  НОРМА = HIGH", "перетин порогу = LOW = «гаряче»"],
                 size=11, pad=10, fill="#fdecea", stroke=POS)
    f.append(line(470, dcy, 470, 175, color=INK, sw=1.8))
    f.append(arrow(470, 175, 620 - b2[1] / 2, 175, color=INK))
    f.append(b2[0])

    # гілка «спокій = LOW»
    f.append(line(dcx, dcy + 30, dcx, 330, color=INK, sw=1.8))
    f.append(text(dcx + 12, 300, "LOW", size=11, bold=True, color=NEG, anchor="start"))
    b3 = textbox(620, 330,
                 ["спокій = LOW  →  НОРМА = LOW", "перетин порогу = HIGH = «гаряче»"],
                 size=11, pad=10, fill="#eef4ff", stroke=NEG)
    f.append(arrow(dcx, 330, 620 - b3[1] / 2, 330, color=INK))
    f.append(b3[0])

    # висновок
    b4 = textbox(W / 2, 392,
                 "Далі «гаряче» = будь-який стан, ПРОТИЛЕЖНИЙ до спокою. Код працює на обох партіях без правок.",
                 size=11, pad=9, bold=True, fill="#eafaf1", stroke=FIELD)
    f.append(b4[0])

    return render(os.path.join(IMG, 'polarity.svg'), W, H, *f)


if __name__ == '__main__':
    fig_schematic()
    fig_wiring()
    fig_hysteresis()
    fig_polarity()
    print("OK: schematic.svg, wiring.svg, hysteresis.svg, polarity.svg")
