# -*- coding: utf-8 -*-
"""Фігури до статті «Давач вологості ґрунту (+LM393)».
Три SVG: чому волога → менший опір; принципова схема модуля; підключення пін-у-пін.
Запуск: python figs.py  → пише у ./img/*.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Що міряє щуп: волога → менший опір → більша напруга на AO
# ─────────────────────────────────────────────────────────────────────────────
def fig_principle():
    W, H = 820, 380
    p = []

    # дві колонки: сухий ґрунт vs вологий ґрунт
    col = [
        (210, "СУХИЙ ҐРУНТ", "великий опір\n(МОм)", "струму майже нема",
         "AO високо", MUTED, FILL),
        (610, "ВОЛОГИЙ ҐРУНТ", "малий опір\n(кОм)", "струм тече легко",
         "AO низько", FIELD, "#eafaf0"),
    ]

    top = 70
    for cx, head, rlbl, curr, ao, accent, bg in col:
        # заголовок колонки
        p.append(text(cx, top, head, size=16, bold=True, color=accent))
        # два щупи в ґрунті
        gx0, gy0, gw, gh = cx - 110, top + 24, 220, 150
        p.append(rect(gx0, gy0, gw, gh, fill=bg, stroke=accent, sw=1.8, rx=8))
        # ліва пластина
        p.append(rect(cx - 66, gy0 + 20, 14, gh - 40, fill="#d9a441", stroke=LINE, sw=1.4))
        # права пластина
        p.append(rect(cx + 52, gy0 + 20, 14, gh - 40, fill="#d9a441", stroke=LINE, sw=1.4))
        # опір ґрунту між ними — рамка з написом ПО ЦЕНТРУ (текст у своїй рамці)
        b, bw, bh = textbox(cx, gy0 + gh / 2, rlbl, size=13, bold=True,
                            fill=BG, stroke=accent)
        p.append(b)
        # струм-стрілка під ґрунтом
        p.append(text(cx, gy0 + gh + 30, curr, size=13, color=accent, bold=True))
        # результат на AO — окремим написом нижче
        p.append(text(cx, gy0 + gh + 58, "→ " + ao, size=14, color=INK, bold=True))

    # роздільна вертикаль
    p.append(line(410, top - 6, 410, top + 250, color="#dddddd", sw=1.4, dash="5 5"))

    return render(os.path.join(IMG, 'principle.svg'), W, H, *p,
                  title="Щуп міряє опір ґрунту: більше води → менший опір → нижча напруга AO")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Принципова схема модуля
# ─────────────────────────────────────────────────────────────────────────────
def fig_schematic():
    W, H = 900, 520
    p = []

    # шини живлення
    vcc_y, gnd_y = 64, 470
    x0, x1 = 70, 840
    p.append(line(x0, vcc_y, x1, vcc_y, color=POS, sw=2.5))
    p.append(line(x0, gnd_y, x1, gnd_y, color=NEG, sw=2.5))
    p.append(text(x0, vcc_y - 12, "+V (3.3–5 В)", size=14, color=POS, anchor="start", bold=True))
    p.append(text(x0, gnd_y + 26, "GND", size=14, color=NEG, anchor="start", bold=True))

    def res_v(x, top, h, label, sub=None, fill=FILL, stroke=LINE):
        """Вертикальний резистор: рамка + підпис ЗЛІВА, щоб жоден дріт її не перетнув."""
        p.append(rect(x - 16, top, 32, h, fill=fill, stroke=stroke, sw=1.6))
        p.append(text(x - 24, top + h / 2 + 4, label, size=13, anchor="end", bold=True))
        if sub:
            p.append(text(x + 24, top + h / 2 + 4, sub, size=11, color=MUTED, anchor="start"))

    # ── ліворуч: щуп + фіксований резистор (подільник) ──
    probe_x = 140
    node_sig_y = 250                       # вузол сирого сигналу з щупа
    # фіксований резистор від +V до вузла
    p.append(line(probe_x, vcc_y, probe_x, 120))
    res_v(probe_x, 120, 46, "Rф", "≈10 кΩ")
    p.append(line(probe_x, 166, probe_x, node_sig_y))
    # щуп (два електроди + ґрунт) від вузла до землі
    p.append(rect(probe_x - 34, node_sig_y + 30, 68, 60, fill="#f6ecd8", stroke="#b8860b", sw=1.8, rx=6))
    p.append(text(probe_x, node_sig_y + 56, "щуп", size=12, bold=True))
    p.append(text(probe_x, node_sig_y + 74, "Rґрунту", size=11, color=MUTED))
    p.append(line(probe_x, node_sig_y + 90, probe_x, gnd_y))
    p.append(circle(probe_x, node_sig_y, 3.5, fill=INK, stroke=INK))
    # відведення сирого сигналу праворуч (у «+» входу і на AO)
    p.append(line(probe_x, node_sig_y, 300, node_sig_y))
    # штир AO — донизу від того ж вузла
    ao_x = 210
    p.append(circle(ao_x, node_sig_y, 3.5, fill=INK, stroke=INK))
    p.append(line(ao_x, node_sig_y, ao_x, node_sig_y + 150))
    p.append(circle(ao_x, node_sig_y + 150, 5, fill=BG, stroke=INK, sw=2))
    p.append(text(ao_x, node_sig_y + 172, "AO", size=13, bold=True))

    # ── тример-подільник задає поріг ──
    pot_x = 320
    thr_y = 330
    p.append(line(pot_x, vcc_y, pot_x, 150))
    p.append(rect(pot_x - 20, 150, 40, 150, fill="#fff7e6", stroke="#b8860b", sw=1.8))
    p.append(text(pot_x, 222, "тример", size=12, bold=True))
    p.append(text(pot_x, 240, "10 кΩ", size=11, color=MUTED))
    p.append(line(pot_x, 300, pot_x, gnd_y))
    # повзунок → поріг (виходить праворуч на нижньому рівні)
    p.append(line(pot_x + 20, thr_y - 40, pot_x + 44, thr_y - 40, color="#b8860b", sw=1.8))
    p.append(line(pot_x + 44, thr_y - 40, pot_x + 44, thr_y, color="#b8860b", sw=1.8))
    p.append(line(pot_x + 44, thr_y, 500, thr_y, color="#b8860b", sw=1.8))
    p.append(text(pot_x + 96, thr_y - 8, "поріг", size=12, color="#b8860b"))

    # ── компаратор LM393 (трикутник) ──
    cx = 510
    cy = (node_sig_y + thr_y) / 2          # між двома входами
    tri = ('<path d="M%d %d L%d %d L%d %d Z" fill="#eafaf0" stroke="%s" stroke-width="2"/>'
           % (cx, cy - 55, cx, cy + 55, cx + 96, cy, FIELD))
    p.append(tri)
    p.append(text(cx + 30, cy + 5, "LM393", size=13, bold=True))
    # входи: сигнал щупа на один, поріг на другий
    p.append(text(cx + 12, node_sig_y + 5, "−", size=17, color=NEG, bold=True))
    p.append(text(cx + 12, thr_y + 5, "+", size=17, color=POS, bold=True))
    p.append(line(300, node_sig_y, cx, node_sig_y))     # сигнал → «−»
    p.append(line(500, thr_y, cx, thr_y))               # поріг → «+»
    # короткі стуби живлення компаратора
    p.append(line(cx + 40, cy - 37, cx + 40, vcc_y, color=POS, sw=1, dash="4 4"))
    p.append(line(cx + 55, cy + 37, cx + 55, gnd_y, color=NEG, sw=1, dash="4 4"))

    # ── вихід: відкритий колектор + підтяжка + LED порога ──
    out_x = cx + 96
    node_out_x = 690
    p.append(line(out_x, cy, node_out_x, cy))
    p.append(circle(node_out_x, cy, 3.5, fill=INK, stroke=INK))
    # підтяжка до +V
    p.append(line(node_out_x, cy, node_out_x, 150))
    res_v(node_out_x, 150, 44, "Rпд", "10 кΩ")
    p.append(line(node_out_x, 150, node_out_x, vcc_y))
    # штир DO донизу
    p.append(line(node_out_x, cy, node_out_x, cy + 90))
    p.append(circle(node_out_x, cy + 90, 5, fill=BG, stroke=INK, sw=2))
    p.append(text(node_out_x, cy + 112, "DO", size=13, bold=True))

    # LED порога: +V → R → LED → вузол виходу
    led_x = 790
    p.append(line(led_x, vcc_y, led_x, 150))
    res_v(led_x, 150, 40, "R")
    p.append(line(led_x, 190, led_x, 300))
    p.append('<path d="M%d %d L%d %d L%d %d Z" fill="#fdecea" stroke="%s" stroke-width="1.6"/>'
             % (led_x - 12, 300, led_x + 12, 300, led_x, 324, POS))
    p.append(line(led_x - 14, 324, led_x + 14, 324, color=POS, sw=2))
    p.append(text(led_x + 22, 316, "LED", size=11, color=MUTED, anchor="start"))
    p.append(text(led_x + 22, 330, "порога", size=11, color=MUTED, anchor="start"))
    p.append(line(led_x, 324, led_x, cy))
    p.append(line(led_x, cy, node_out_x, cy))
    p.append(circle(led_x, cy, 3.5, fill=INK, stroke=INK))

    return render(os.path.join(IMG, 'schematic.svg'), W, H, *p,
                  title="Принципова схема: щуп-подільник, тример-поріг, компаратор LM393, два виходи")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Підключення пін-у-пін
# ─────────────────────────────────────────────────────────────────────────────
def fig_wiring():
    W, H = 860, 470
    p = []

    # чотири спільні рівні дротів — далеко один від одного
    y_ao, y_do, y_vcc, y_gnd = 130, 190, 250, 310

    # плата-компаратор ліворуч
    mx, my, mw, mh = 60, 90, 250, 280
    p.append(rect(mx, my, mw, mh, fill="#eef4ff", stroke=NEG, sw=2, rx=10))
    p.append(text(mx + mw / 2, my + 28, "Плата LM393", size=16, bold=True, color=NEG))
    p.append(text(mx + mw / 2, my + 48, "(модуль-компаратор)", size=12, color=MUTED))
    # тример угорі, вище рівнів дротів
    p.append(rect(mx + 40, my + 66, 54, 36, fill="#fff7e6", stroke="#b8860b", sw=1.6))
    p.append(text(mx + 67, my + 88, "тример", size=10))
    p.append(rect(mx + 150, my + 66, 54, 36, fill="#fdecea", stroke=POS, sw=1.4))
    p.append(text(mx + 177, my + 88, "LED×2", size=10))

    # чотири штирі на правому краю плати
    px = mx + mw
    mod_pins = [("AO", y_ao, FIELD), ("DO", y_do, INK), ("VCC", y_vcc, POS), ("GND", y_gnd, NEG)]
    for name, yy, col in mod_pins:
        p.append(circle(px, yy, 6, fill=BG, stroke=INK, sw=2))
        p.append(text(px - 16, yy + 5, name, size=14, anchor="end", bold=True, color=col))

    # плата МК праворуч
    bx, by, bw2, bh2 = 600, 90, 210, 280
    p.append(rect(bx, by, bw2, bh2, fill="#eafaf0", stroke=FIELD, sw=2, rx=10))
    p.append(text(bx + bw2 / 2, by + 28, "Мікроконтролер", size=15, bold=True, color=FIELD))
    p.append(text(bx + bw2 / 2, by + 48, "(Arduino / ESP32)", size=11, color=MUTED))
    mcu_pins = [("A0 (АЦП)", y_ao), ("D2", y_do), ("5V / 3.3V", y_vcc), ("GND", y_gnd)]
    for name, yy in mcu_pins:
        p.append(circle(bx, yy, 6, fill=BG, stroke=INK, sw=2))
        p.append(text(bx + 16, yy + 5, name, size=13, anchor="start", bold=True))

    # прямі дроти (рівні збігаються — без зламів)
    p.append(line(px, y_ao, bx, y_ao, color=FIELD, sw=2.4))
    p.append(line(px, y_do, bx, y_do, color=INK, sw=2.4))
    p.append(line(px, y_vcc, bx, y_vcc, color=POS, sw=2.4))
    p.append(line(px, y_gnd, bx, y_gnd, color=NEG, sw=2.4))

    # підписи призначення — НАД відповідним дротом, по центру проміжку
    midx = (px + bx) / 2
    p.append(text(midx, y_ao - 12, "сирий сигнал → АЦП", size=12, color=MUTED))
    p.append(text(midx, y_do - 12, "поріг → цифровий вхід", size=12, color=MUTED))
    p.append(text(midx, y_vcc - 12, "живлення", size=12, color=MUTED))
    p.append(text(midx, y_gnd - 12, "спільна земля", size=12, color=MUTED))

    # примітка про щуп
    note = ("Плата-компаратор — окрема від щупа: два електроди щупа йдуть двома дротами\n"
            "на власні контакти плати. Живіть VCC лише під час заміру (див. текст) — так\n"
            "щуп менше кородує. AO дає число, DO — готове «сухо/волого» за порогом гвинтика.")
    p.append(fitbox(120, 392, 620, 62, note, size=12, fill="#fff9e6",
                    stroke="#b8860b", color=INK))

    return render(os.path.join(IMG, 'wiring.svg'), W, H, *p,
                  title="Підключення: AO → АЦП, DO → цифровий вхід, живлення й земля")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Медіана проти середнього: один сплеск-викид
#    (proj-вставка — згладжування замірів)
# ─────────────────────────────────────────────────────────────────────────────
def fig_median():
    W, H = 860, 430
    p = []

    # сім замірів: шість добрих коло 640, один дикий викид (спалахнув контакт)
    vals = [642, 636, 651, 210, 639, 648, 633]
    n = len(vals)
    # область графіка
    gx0, gy0, gw, gh = 90, 70, 680, 250
    vmin, vmax = 150, 700
    def yv(v):  # значення → y (більше значення вище)
        return gy0 + gh - (v - vmin) / (vmax - vmin) * gh
    # осі
    p.append(line(gx0, gy0, gx0, gy0 + gh, color=MUTED, sw=1.4))
    p.append(line(gx0, gy0 + gh, gx0 + gw, gy0 + gh, color=MUTED, sw=1.4))
    p.append(text(gx0 - 46, gy0 + 6, "АЦП", size=12, color=MUTED, anchor="start"))
    # горизонтальні пунктири: середнє й медіана
    mean = sum(vals) / n            # ≈ 580 — просіло через викид
    srt = sorted(vals)
    median = srt[n // 2]            # 639 — стійка
    p.append(line(gx0, yv(mean), gx0 + gw, yv(mean), color=POS, sw=2, dash="7 5"))
    p.append(line(gx0, yv(median), gx0 + gw, yv(median), color=FIELD, sw=2, dash="7 5"))
    # підписи ліній — праворуч від графіка, кожен на своєму рівні, не на лінії
    p.append(text(gx0 + gw + 12, yv(median) - 6, "медіана", size=13, color=FIELD, anchor="start", bold=True))
    p.append(text(gx0 + gw + 12, yv(median) + 12, "= 639", size=12, color=FIELD, anchor="start"))
    p.append(text(gx0 + gw + 12, yv(mean) + 4, "середнє", size=13, color=POS, anchor="start", bold=True))
    p.append(text(gx0 + gw + 12, yv(mean) + 22, "≈ 580", size=12, color=POS, anchor="start"))
    # стовпчики замірів
    step = gw / (n + 1)
    for i, v in enumerate(vals):
        cx = gx0 + step * (i + 1)
        is_spike = (v == 210)
        col = POS if is_spike else NEG
        p.append(circle(cx, yv(v), 6, fill=col, stroke=col))
        # значення над точкою (для викиду — під нею, щоб не налізти на медіану)
        if is_spike:
            p.append(text(cx, yv(v) + 24, str(v), size=12, color=POS, bold=True))
            p.append(text(cx, yv(v) + 40, "викид", size=11, color=POS))
        else:
            p.append(text(cx, yv(v) - 12, str(v), size=11, color=INK))

    return render(os.path.join(IMG, 'median-vs-mean.svg'), W, H, *p,
                  title="Один поганий відлік тягне середнє вниз, а медіану — ні")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Живлення щупа через транзистор-ключ (коли виводу бракує струму)
# ─────────────────────────────────────────────────────────────────────────────
def fig_switch():
    W, H = 860, 440
    p = []

    vcc_y, gnd_y = 70, 380
    x0, x1 = 80, 780
    p.append(line(x0, vcc_y, x1, vcc_y, color=POS, sw=2.5))
    p.append(line(x0, gnd_y, x1, gnd_y, color=NEG, sw=2.5))
    p.append(text(x0, vcc_y - 12, "+3.3 / 5 В", size=13, color=POS, anchor="start", bold=True))
    p.append(text(x0, gnd_y + 26, "GND", size=13, color=NEG, anchor="start", bold=True))

    # ── МК ліворуч: вивід керування ──
    mx, my, mw, mh = 90, 150, 150, 120
    p.append(rect(mx, my, mw, mh, fill="#eafaf0", stroke=FIELD, sw=2, rx=10))
    p.append(text(mx + mw / 2, my + 34, "МК", size=15, bold=True, color=FIELD))
    p.append(text(mx + mw / 2, my + 58, "GPIO", size=12, color=MUTED))
    p.append(text(mx + mw / 2, my + 78, "«увімкни щуп»", size=11, color=MUTED))
    gpio_x = mx + mw
    gpio_y = my + mh / 2
    p.append(circle(gpio_x, gpio_y, 5, fill=BG, stroke=INK, sw=2))

    # ── резистор бази → база транзистора ──
    rb_x0 = gpio_x + 20
    p.append(line(gpio_x, gpio_y, rb_x0, gpio_y))
    p.append(rect(rb_x0, gpio_y - 12, 60, 24, fill=FILL, stroke=LINE, sw=1.5))
    p.append(text(rb_x0 + 30, gpio_y - 20, "Rбази 1 кΩ", size=11, color=MUTED))
    base_x = rb_x0 + 60 + 40
    p.append(line(rb_x0 + 60, gpio_y, base_x, gpio_y))

    # ── транзистор-ключ (n-p-n низькочастотний ключ у нижньому плечі) ──
    # тіло: коло з вертикальною базовою пластиною + колектор угору, емітер униз
    tsym_x = base_x + 26
    p.append(circle(tsym_x, gpio_y, 30, fill=BG, stroke=INK, sw=1.8))
    bp_x = tsym_x - 12                        # базова пластина всередині кола
    p.append(line(bp_x, gpio_y - 18, bp_x, gpio_y + 18, color=INK, sw=3))
    p.append(line(base_x, gpio_y, bp_x, gpio_y, color=INK, sw=1.8))   # база-вивід у пластину
    col_x = tsym_x + 6
    tb_top, tb_bot = gpio_y - 30, gpio_y + 30
    # колектор угору до щупа; емітер униз на землю
    p.append(line(bp_x + 4, gpio_y - 12, col_x, tb_top, color=INK, sw=1.8))   # до колектора
    p.append(line(bp_x + 4, gpio_y + 12, col_x, tb_bot, color=INK, sw=1.8))   # до емітера
    # підпис транзистора — під символом, добре нижче будь-яких ліній
    p.append(text(tsym_x + 42, gpio_y + 6, "T (NPN-ключ)", size=11, color=MUTED, anchor="start"))
    # емітер → земля (стрілка емітера вниз = n-p-n)
    p.append(line(col_x, tb_bot, col_x, gnd_y, color=INK, sw=1.8))

    # ── щуп у верхньому плечі: +V → щуп → колектор ──
    probe_x = col_x
    probe_top = 130
    p.append(line(probe_x, vcc_y, probe_x, probe_top))
    p.append(rect(probe_x - 34, probe_top, 68, 60, fill="#f6ecd8", stroke="#b8860b", sw=1.8, rx=6))
    p.append(text(probe_x, probe_top + 26, "щуп", size=12, bold=True))
    p.append(text(probe_x, probe_top + 44, "Rґрунту", size=11, color=MUTED))
    p.append(line(probe_x, probe_top + 60, probe_x, tb_top))
    # вузол AO знімається з верху щупа (спрощено — з боку)
    ao_x = probe_x + 120
    node_y = probe_top + 30
    p.append(line(probe_x + 34, node_y, ao_x, node_y, color=FIELD, sw=2))
    p.append(circle(ao_x, node_y, 5, fill=BG, stroke=INK, sw=2))
    p.append(text(ao_x + 12, node_y + 5, "AO → АЦП", size=12, color=FIELD, anchor="start", bold=True))

    # пояснювальна рамка внизу — з запасом, не торкається схеми
    note = ("GPIO не живить щуп напряму, а лише ВІДЧИНЯЄ транзистор: слабкий струм бази\n"
            "(через Rбази) вмикає сильніший струм колектора крізь щуп. Так вивід не\n"
            "перевантажується, а щуп живиться повним струмом лише на мілісекунди заміру.")
    p.append(fitbox(150, 392, 560, 40, note, size=11, fill="#fff9e6",
                    stroke="#b8860b", color=INK))

    return render(os.path.join(IMG, 'transistor-power.svg'), W, H, *p,
                  title="Живлення щупа через транзистор-ключ: GPIO керує, транзистор тягне струм")


if __name__ == '__main__':
    fig_principle()
    fig_schematic()
    fig_wiring()
    fig_median()
    fig_switch()
    print("OK: principle, schematic, wiring, median-vs-mean, transistor-power")
