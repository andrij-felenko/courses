# -*- coding: utf-8 -*-
"""Фігури до статті «Funduino — давач дощу (+LM358)».
Три SVG: пелюстка-гребінка як змінний резистор, принципова схема (LM358 як компаратор),
підключення пін-у-пін.
Запуск: python figs.py  → пише у ./img/*.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Пластина-гребінка: краплі замикають доріжки → опір падає → напруга рухається
# ─────────────────────────────────────────────────────────────────────────────
def fig_pad():
    W, H = 820, 380
    p = []

    # ── ліворуч: сама пластина з двома гребінками ──
    px, py, pw, ph = 60, 90, 300, 220
    p.append(rect(px, py, pw, ph, fill="#f6efe6", stroke="#8a6d3b", sw=2, rx=8))
    p.append(text(px + pw / 2, py - 14, "Пластина: дві гребінки доріжок", size=14, bold=True))

    # гребінка A (зверху, «+») та B (знизу, «−»), пальці вставлені один в один
    n = 6
    gap = pw / (2 * n + 1)
    top_y, bot_y = py + 24, py + ph - 24
    busA_y, busB_y = py + 18, py + ph - 18
    # шини
    p.append(line(px + 12, busA_y, px + pw - 12, busA_y, color=POS, sw=3))
    p.append(line(px + 12, busB_y, px + pw - 12, busB_y, color=NEG, sw=3))
    for i in range(n):
        xa = px + gap * (2 * i + 1) + 10
        xb = xa + gap
        p.append(line(xa, busA_y, xa, bot_y, color=POS, sw=2.4))   # палець A вниз
        p.append(line(xb, busB_y, xb, top_y, color=NEG, sw=2.4))   # палець B вгору
    p.append(text(px + 6, busA_y - 8, "доріжка A (+)", size=11, color=POS, anchor="start"))
    p.append(text(px + 6, busB_y + 18, "доріжка B (−)", size=11, color=NEG, anchor="start"))

    # три краплі, що перекривають сусідні пальці
    for dx, dy in [(px + 90, py + 120), (px + 150, py + 90), (px + 205, py + 150)]:
        p.append('<ellipse cx="%d" cy="%d" rx="16" ry="12" fill="#acd6f5" '
                 'stroke="#2457d6" stroke-width="1.2" opacity="0.85"/>' % (dx, dy))
    p.append(text(px + pw / 2, py + ph + 26,
                  "крапля з'єднує сусідні доріжки → опір між A і B падає", size=12, color=MUTED))

    # ── праворуч: як міняється опір і напруга ──
    tx = 450
    p.append(text(tx + 150, py - 14, "Що з цього виходить", size=14, bold=True))

    box1, w1, h1 = textbox(tx + 150, py + 46,
                           "СУХО\nдоріжки роз'єднані\nR ≈ 1–20 МΩ (величезний)",
                           size=13, fill="#fdf3f3", stroke=POS, bold=False)
    p.append(box1)
    box2, w2, h2 = textbox(tx + 150, py + 150,
                           "МОКРО\nвода — слабкий провідник\nR падає до кΩ",
                           size=13, fill="#eef6ff", stroke=NEG, bold=False)
    p.append(box2)
    box3, w3, h3 = textbox(tx + 150, py + 250,
                           "R у подільнику рухає напругу →\nбільше води = нижча напруга на AO",
                           size=12, fill="#eafaf0", stroke=FIELD, bold=True)
    p.append(box3)
    p.append(arrow(tx + 150, py + 46 + h1 / 2, tx + 150, py + 150 - h2 / 2))
    p.append(arrow(tx + 150, py + 150 + h2 / 2, tx + 150, py + 250 - h3 / 2))

    return render(os.path.join(IMG, 'pad.svg'), W, H, *p,
                  title="Пластина-гребінка: краплі замикають доріжки, опір падає")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Принципова схема: подільник + LM358 як компаратор + push-pull вихід
# ─────────────────────────────────────────────────────────────────────────────
def fig_schematic():
    W, H = 900, 520
    p = []

    vcc_y, gnd_y = 66, 470
    x0, x1 = 70, 840
    p.append(line(x0, vcc_y, x1, vcc_y, color=POS, sw=2.5))
    p.append(line(x0, gnd_y, x1, gnd_y, color=NEG, sw=2.5))
    p.append(text(x0, vcc_y - 12, "+V (3.3–5 В)", size=14, color=POS, anchor="start", bold=True))
    p.append(text(x0, gnd_y + 26, "GND", size=14, color=NEG, anchor="start", bold=True))

    def res_v(x, top, h, label, sub=None, fill=FILL, stroke=LINE):
        p.append(rect(x - 16, top, 32, h, fill=fill, stroke=stroke, sw=1.6))
        p.append(text(x - 24, top + h / 2 + 4, label, size=13, anchor="end", bold=True))
        if sub:
            p.append(text(x + 24, top + h / 2 + 4, sub, size=11, color=MUTED, anchor="start"))

    # ── ліворуч: подільник «пластина + резистор» дає сирий сигнал ──
    div_x = 140
    node_sig_y = 250
    # верхнє плече — сама пластина (змінний опір)
    p.append(line(div_x, vcc_y, div_x, 118))
    p.append(rect(div_x - 20, 118, 40, 60, fill="#f6efe6", stroke="#8a6d3b", sw=1.8))
    # стрілка через резистор = змінний
    p.append(line(div_x - 24, 182, div_x + 24, 128, color="#8a6d3b", sw=1.6))
    p.append(text(div_x - 26, 148, "пластина", size=12, anchor="end", bold=True))
    p.append(text(div_x + 26, 152, "R", size=12, color=MUTED, anchor="start"))
    p.append(line(div_x, 178, div_x, node_sig_y))
    # нижнє плече — постійний резистор до землі
    res_v(div_x, node_sig_y + 30, 60, "Rд", "фікс.")
    p.append(line(div_x, node_sig_y, div_x, node_sig_y + 30))
    p.append(line(div_x, node_sig_y + 90, div_x, gnd_y))
    p.append(circle(div_x, node_sig_y, 3.5, fill=INK, stroke=INK))
    # відведення сигналу праворуч + це і є AO
    p.append(line(div_x, node_sig_y, 300, node_sig_y))
    p.append(text(div_x + 8, node_sig_y - 10, "сирий сигнал = AO", size=11, color=FIELD, anchor="start", bold=True))

    # ── тример задає поріг ──
    pot_x = 300
    thr_y = 330
    p.append(line(pot_x, vcc_y, pot_x, 150))
    p.append(rect(pot_x - 20, 150, 40, 150, fill="#fff7e6", stroke="#b8860b", sw=1.8))
    p.append(text(pot_x, 222, "тример", size=12, bold=True))
    p.append(text(pot_x, 240, "поріг", size=11, color=MUTED))
    p.append(line(pot_x, 300, pot_x, gnd_y))
    p.append(line(pot_x + 20, thr_y - 44, pot_x + 44, thr_y - 44, color="#b8860b", sw=1.8))
    p.append(line(pot_x + 44, thr_y - 44, pot_x + 44, thr_y, color="#b8860b", sw=1.8))
    p.append(line(pot_x + 44, thr_y, 500, thr_y, color="#b8860b", sw=1.8))
    p.append(text(pot_x + 92, thr_y - 8, "опорна напруга", size=11, color="#b8860b"))

    # ── LM358 як компаратор (трикутник) ──
    cx = 510
    cy = (node_sig_y + thr_y) / 2
    tri = ('<path d="M%d %d L%d %d L%d %d Z" fill="#f0ecfb" stroke="#7c4dff" stroke-width="2"/>'
           % (cx, cy - 58, cx, cy + 58, cx + 100, cy))
    p.append(tri)
    p.append(text(cx + 30, cy - 4, "LM358", size=13, bold=True))
    p.append(text(cx + 26, cy + 16, "½ (ОП)", size=10, color=MUTED))
    # входи: сигнал і поріг
    p.append(text(cx + 12, node_sig_y + 5, "−", size=17, color=NEG, bold=True))
    p.append(text(cx + 12, thr_y + 5, "+", size=17, color=POS, bold=True))
    p.append(line(300, node_sig_y, cx, node_sig_y))
    p.append(line(500, thr_y, cx, thr_y))
    # живлення ОП — короткі пунктирні стуби
    p.append(line(cx + 44, cy - 40, cx + 44, vcc_y, color=POS, sw=1, dash="4 4"))
    p.append(line(cx + 60, cy + 40, cx + 60, gnd_y, color=NEG, sw=1, dash="4 4"))

    # ── вихід push-pull: БЕЗ підтяжки, прямо на штир + LED ──
    out_x = cx + 100
    node_out_x = 690
    p.append(line(out_x, cy, node_out_x, cy))
    p.append(circle(node_out_x, cy, 3.5, fill=INK, stroke=INK))
    p.append(text(node_out_x, cy - 14, "push-pull: сам тягне ↑ і ↓", size=11, color="#7c4dff", bold=True))
    # штир DO донизу
    p.append(line(node_out_x, cy, node_out_x, cy + 96))
    p.append(circle(node_out_x, cy + 96, 5, fill=BG, stroke=INK, sw=2))
    p.append(text(node_out_x, cy + 118, "DO", size=13, bold=True))

    # LED дощу: +V → R → LED → вузол виходу (світиться, коли вихід унизу)
    led_x = 790
    p.append(line(led_x, vcc_y, led_x, 150))
    res_v(led_x, 150, 40, "R")
    p.append(line(led_x, 190, led_x, 300))
    p.append('<path d="M%d %d L%d %d L%d %d Z" fill="#fdecea" stroke="%s" stroke-width="1.6"/>'
             % (led_x - 12, 300, led_x + 12, 300, led_x, 324, POS))
    p.append(line(led_x - 14, 324, led_x + 14, 324, color=POS, sw=2))
    p.append(text(led_x + 20, 314, "LED", size=11, color=MUTED, anchor="start"))
    p.append(text(led_x + 20, 328, "дощу", size=11, color=MUTED, anchor="start"))
    p.append(line(led_x, 324, led_x, cy))
    p.append(line(led_x, cy, node_out_x, cy))
    p.append(circle(led_x, cy, 3.5, fill=INK, stroke=INK))

    return render(os.path.join(IMG, 'schematic.svg'), W, H, *p,
                  title="Принципова схема: подільник, LM358 як компаратор, push-pull вихід")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Підключення пін-у-пін
# ─────────────────────────────────────────────────────────────────────────────
def fig_wiring():
    W, H = 840, 470
    p = []

    y_ao, y_do, y_vcc, y_gnd = 140, 200, 260, 320

    # плата-давач ліворуч
    mx, my, mw, mh = 60, 90, 250, 280
    p.append(rect(mx, my, mw, mh, fill="#f6efe6", stroke="#8a6d3b", sw=2, rx=10))
    p.append(text(mx + mw / 2, my + 28, "Плата давача", size=16, bold=True, color="#8a6d3b"))
    p.append(text(mx + mw / 2, my + 48, "(з LM358, 4 штирі)", size=12, color=MUTED))
    # тример і LED — угорі, вище рівнів дротів
    p.append(rect(mx + 40, my + 66, 52, 36, fill="#fff7e6", stroke="#b8860b", sw=1.6))
    p.append(text(mx + 66, my + 88, "тример", size=10))
    p.append(circle(mx + 150, my + 84, 12, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(text(mx + 178, my + 88, "LED", size=10, anchor="start", color=MUTED))
    # роз'єм до пластини
    p.append(text(mx + mw / 2, my + 122, "↘ 2 дроти до пластини", size=11, color="#8a6d3b"))

    px = mx + mw
    mod_pins = [("AO", y_ao, FIELD), ("DO", y_do, INK), ("VCC", y_vcc, POS), ("GND", y_gnd, NEG)]
    for name, yy, col in mod_pins:
        p.append(circle(px, yy, 6, fill=BG, stroke=INK, sw=2))
        p.append(text(px - 16, yy + 5, name, size=14, anchor="end", bold=True, color=col))

    # плата МК праворуч
    bx, by, bw2, bh2 = 600, 90, 200, 280
    p.append(rect(bx, by, bw2, bh2, fill="#eafaf0", stroke=FIELD, sw=2, rx=10))
    p.append(text(bx + bw2 / 2, by + 28, "Мікроконтролер", size=15, bold=True, color=FIELD))
    p.append(text(bx + bw2 / 2, by + 48, "(Arduino / ESP32)", size=11, color=MUTED))
    mcu_pins = [("A0", y_ao), ("D2", y_do), ("3.3V / 5V", y_vcc), ("GND", y_gnd)]
    for name, yy in mcu_pins:
        p.append(circle(bx, yy, 6, fill=BG, stroke=INK, sw=2))
        p.append(text(bx + 16, yy + 5, name, size=13, anchor="start", bold=True))

    # прямі дроти
    p.append(line(px, y_ao, bx, y_ao, color=FIELD, sw=2.4))
    p.append(line(px, y_do, bx, y_do, color=INK, sw=2.4))
    p.append(line(px, y_vcc, bx, y_vcc, color=POS, sw=2.4))
    p.append(line(px, y_gnd, bx, y_gnd, color=NEG, sw=2.4))

    midx = (px + bx) / 2
    p.append(text(midx, y_ao - 12, "аналог → вхід АЦП", size=11, color=MUTED))
    p.append(text(midx, y_do - 12, "поріг → цифровий вхід", size=11, color=MUTED))
    p.append(text(midx, y_vcc - 12, "живлення під логіку плати", size=11, color=MUTED))
    p.append(text(midx, y_gnd - 12, "спільна земля", size=11, color=MUTED))

    note = ("Досить будь-якого одного виходу. DO — готовий біт «дощ/сухо» (поріг крутить тример);\n"
            "AO — сира напруга, щоб самому судити про силу дощу через АЦП. Живлення — 3.3 чи 5 В "
            "під логіку вашої плати.")
    p.append(fitbox(90, 396, 660, 56, note, size=12, fill="#fff9e6",
                    stroke="#b8860b", color=INK))

    return render(os.path.join(IMG, 'wiring.svg'), W, H, *p,
                  title="Підключення: AO → АЦП, DO → цифровий вхід, живлення й земля")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Програмний гістерезис: торохтняву DO на межі згортаємо в одну чисту подію
#    (для proj-вставки — прошивка, не залізо)
# ─────────────────────────────────────────────────────────────────────────────
def fig_hysteresis():
    W, H = 860, 430
    p = []

    x0, x1 = 90, 800
    lo_y, hi_y = 150, 90            # рівні «0» (низько) і «1» (високо) для лінії DO
    base_y = 150

    # ── верхня доріжка: сирий DO з торохтнявою на межі ──
    p.append(text(x0 - 20, hi_y - 24, "DO (сирий)", size=13, bold=True, anchor="start"))
    # сегменти рівня: [x_start, x_end, level]  (level: 'hi' або 'lo')
    segs = [
        (x0, 250, 'hi'),
        (250, 262, 'lo'), (262, 276, 'hi'), (276, 289, 'lo'),   # торохтняви — початок дощу
        (289, 300, 'hi'), (300, 470, 'lo'),                     # усталився в дощ
        (470, 482, 'hi'), (482, 495, 'lo'), (495, 640, 'hi'),   # торохтняви — кінець дощу
        (640, x1, 'hi'),
    ]
    prev_y = None
    for xs, xe, lv in segs:
        yy = hi_y if lv == 'hi' else lo_y
        p.append(line(xs, yy, xe, yy, color=INK, sw=2.4))
        if prev_y is not None and prev_y != yy:      # вертикальний фронт
            p.append(line(xs, prev_y, xs, yy, color=INK, sw=2.4))
        prev_y = yy
    p.append(text(x0 - 20, hi_y + 4, "1", size=12, color=MUTED, anchor="end"))
    p.append(text(x0 - 20, lo_y + 4, "0", size=12, color=MUTED, anchor="end"))
    # позначки «пачка переходів»
    p.append(text(275, lo_y + 30, "торохтняви", size=11, color=POS))
    p.append(text(565, lo_y + 30, "торохтняви", size=11, color=POS))

    # ── нижня доріжка: підтверджений стан після витримки SETTLE ──
    clo_y, chi_y = 330, 270
    p.append(text(x0 - 20, chi_y - 24, "підтверджено (SETTLE)", size=13, bold=True, anchor="start"))
    csegs = [(x0, 300, 'hi'), (300, 640, 'lo'), (640, x1, 'hi')]
    prev_y = None
    for xs, xe, lv in csegs:
        yy = chi_y if lv == 'hi' else clo_y
        p.append(line(xs, yy, xe, yy, color=FIELD, sw=3))
        if prev_y is not None and prev_y != yy:
            p.append(line(xs, prev_y, xs, yy, color=FIELD, sw=3))
        prev_y = yy
    p.append(text(x0 - 20, chi_y + 4, "сухо", size=11, color=MUTED, anchor="end"))
    p.append(text(x0 - 20, clo_y + 4, "дощ", size=11, color=MUTED, anchor="end"))

    # вікна SETTLE — сірі смуги від першого фронту до підтвердження
    for xa, xb, lab in [(250, 300, "SETTLE"), (470, 640, "SETTLE")]:
        p.append(rect(xa, 250, xb - xa, 90, fill="#eef1f4", stroke="#cbd2d9", sw=1, rx=4))
        p.append(text((xa + xb) / 2, 246, lab, size=10, color=MUTED))

    # дві чисті події внизу
    p.append(text(300, clo_y + 40, "↑ одна подія «дощ почався»", size=11, color=FIELD, anchor="start"))
    p.append(text(640, chi_y - 40, "↑ одна подія «дощ скінчився»", size=11, color=FIELD, anchor="start"))

    p.append(fitbox(90, 372, 710, 48,
                    "Стан вважаємо справжнім лише коли він протримався SETTLE мс — це програмний гістерезис:\n"
                    "пачку торохтняв на межі згорнуто в один чистий фронт, і БЕЗ блокувального delay.",
                    size=13, fill="#eafaf0", stroke=FIELD, color=INK))

    return render(os.path.join(IMG, 'hysteresis.svg'), W, H, *p,
                  title="Програмний гістерезис: торохтняву межі — в одну подію")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Імпульсне живлення пластини з реверсом полярності — проти електролізу
# ─────────────────────────────────────────────────────────────────────────────
def fig_pulsed():
    W, H = 860, 430
    p = []

    x0, x1 = 90, 800
    # часова вісь
    p.append(line(x0, 300, x1, 300, color=MUTED, sw=1.5))
    p.append(text(x0, 322, "час →", size=11, color=MUTED, anchor="start"))

    # ── зверху: постійне живлення (як «за замовчуванням») ──
    dc_y = 80
    p.append(text(x0 - 20, dc_y - 22, "Постійне живлення VCC (гине за місяці)", size=12, bold=True, anchor="start", color=POS))
    p.append(rect(x0, dc_y, x1 - x0, 34, fill="#fdecea", stroke=POS, sw=1.6, rx=4))
    p.append(text((x0 + x1) / 2, dc_y + 22, "струм крізь вологу тече ЦІЛОДОБОВО → електроліз роз'їдає доріжки",
                  size=12, color=POS))

    # ── знизу: імпульсне живлення з GPIO, короткі вікна виміру ──
    pu_y = 200
    p.append(text(x0 - 20, pu_y - 22, "Імпульсно з GPIO: живлення лише на мить виміру", size=12, bold=True, anchor="start", color=FIELD))
    # базова лінія «вимкнено»
    p.append(line(x0, pu_y + 40, x1, pu_y + 40, color="#cbd2d9", sw=1.5, dash="4 4"))
    p.append(text(x0 - 20, pu_y + 44, "off", size=10, color=MUTED, anchor="end"))

    # чотири короткі імпульси, полярність чергується: + (червоний) / − (синій)
    pulses = [(160, POS, "+"), (330, NEG, "−"), (500, POS, "+"), (670, NEG, "−")]
    pw = 26
    for cx, col, sign in pulses:
        p.append(rect(cx, pu_y, pw, 40, fill=BG, stroke=col, sw=2, rx=3))
        p.append(text(cx + pw / 2, pu_y + 26, sign, size=16, color=col, bold=True))
        # короткий тик під імпульсом (не тягнемо до осі, щоб не різати підпис)
        p.append(line(cx + pw / 2, pu_y + 40, cx + pw / 2, pu_y + 52, color=col, sw=1, dash="3 3"))
    # дужка «період» між двома імпульсами
    a, b = pulses[0][0] + pw / 2, pulses[1][0] + pw / 2
    p.append(line(a, pu_y - 12, b, pu_y - 12, color=MUTED, sw=1.2))
    p.append(text((a + b) / 2, pu_y - 18, "період (напр. 1/год)", size=10, color=MUTED))

    # підпис: реверс полярності — під віссю праворуч, чисто, без перетинів
    p.append(text(x1, 322, "+/− чергуються щовиміру (проти анодного роз'їдання)",
                  size=11, color=NEG, anchor="end"))

    # частка часу під струмом — крихітна
    p.append(fitbox(90, 342, 710, 66,
                    "Живимо пластину з ноги МК і вмикаємо лише на 20–50 мс виміру: струм крізь вологу тече\n"
                    "частками секунди на годину замість цілодобово — електроліз майже зупинено, заряд збережено.\n"
                    "Реверс полярності щовиміру знімає ще й анодне роз'їдання (на партіях давачів: без корозії ~півроку).",
                    size=12, fill="#eafaf0", stroke=FIELD, color=INK))

    return render(os.path.join(IMG, 'pulsed.svg'), W, H, *p,
                  title="Імпульсне живлення пластини з реверсом полярності")


if __name__ == '__main__':
    fig_pad()
    fig_schematic()
    fig_wiring()
    fig_hysteresis()
    fig_pulsed()
    print("OK: pad.svg, schematic.svg, wiring.svg, hysteresis.svg, pulsed.svg")
