# -*- coding: utf-8 -*-
"""Фігури для вставки comp-ideal-diode-ic.md (клас мікросхем-контролерів ідеального діода).
Окремий генератор, щоб не заважати основному figs.py теми. Вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1. Блок-схема контролера з зовнішнім N-FET у верхньому плечі ──────
def fig_block():
    W, H = 760, 430
    f = []
    # Зовнішній N-MOSFET згори: витік=ANODE (вхід), стік=CATHODE (вихід)
    fx, fy = 300, 70        # центр символу FET
    # шини входу/виходу
    f.append(plus(70, 90))
    f.append(text(70, 118, "Vin", size=13, color=POS, bold=True))
    f.append(line(80, 90, 200, 90))              # вхід до витоку/анода
    f.append(line(400, 90, 690, 90))             # вихід/катод до навантаження
    f.append(text(690, 118, "Vout", size=13, color=FIELD, bold=True))
    # символ MOSFET як прямокутник-ключ
    f.append(rect(fx - 55, fy - 26, 110, 52, fill="#eef7f0", stroke=FIELD, sw=2))
    f.append(text(fx, fy - 4, "N-FET", size=15, bold=True, color=FIELD))
    f.append(text(fx, fy + 15, "Rds(on)", size=11, color=MUTED))
    f.append(line(200, 90, fx - 55, 90))         # анод -> витік
    f.append(line(fx + 55, 90, 400, 90))         # стік -> катод
    # body-діод символ під ключем
    f.append(text(fx, fy + 40, "body-діод", size=10, color=MUTED))
    # точки sense
    f.append(circle(215, 90, 4, fill=INK, stroke=INK))
    f.append(text(215, 74, "IN (анод)", size=11, color=POS, bold=True))
    f.append(circle(388, 90, 4, fill=INK, stroke=INK))
    f.append(text(388, 74, "OUT (катод)", size=11, color=FIELD, bold=True))

    # Корпус контролера
    cx, cy, cw, ch = 210, 200, 340, 180
    f.append(rect(cx, cy, cw, ch, fill="#f7f4fb", stroke="#7c4bbf", sw=2))
    f.append(text(cx + cw / 2, cy + 22, "КОНТРОЛЕР ІДЕАЛЬНОГО ДІОДА", size=14, bold=True, color="#7c4bbf"))

    # блоки всередині
    f.append(textbox(cx + 95, cy + 70, "Компаратор\nVin − Vout (= Vds)\n(напрям струму)", size=11, fill="#fff", stroke=LINE)[0])
    f.append(textbox(cx + 250, cy + 70, "Драйвер\nзатвора\n(сильний)", size=11, fill="#fff", stroke=LINE)[0])
    f.append(textbox(cx + 95, cy + 138, "Насос заряду\nVgate > Vin", size=11, fill="#fdf6e3", stroke="#b8860b")[0])
    f.append(textbox(cx + 250, cy + 138, "Опора 20 мВ\n(ціль падіння)", size=11, fill="#fff", stroke=LINE)[0])

    # sense-лінії від точок у компаратор
    f.append(line(215, 94, 215, 150, color=POS, sw=1.4, dash="4,3"))
    f.append(line(215, 150, cx + 55, 150, color=POS, sw=1.4, dash="4,3"))
    f.append(line(388, 94, 420, 130, color=FIELD, sw=1.4, dash="4,3"))
    f.append(line(420, 130, cx + 135, cy + 55, color=FIELD, sw=1.4, dash="4,3"))
    # драйвер -> gate
    # GATE: ортогональний маршрут з драйвера вгору й ліворуч до затвора FET,
    # обходячи корпус праворуч, щоб не різати блоки й підписи
    gxr = cx + cw + 20        # 570 — вертикаль праворуч від корпусу
    f.append(line(cx + 250, cy + 45, cx + 250, cy + 20, color="#7c4bbf", sw=2))   # вгору з драйвера
    f.append(line(cx + 250, cy + 20, gxr, cy + 20, color="#7c4bbf", sw=2))        # праворуч
    f.append(line(gxr, cy + 20, gxr, fy + 26, color="#7c4bbf", sw=2))             # вгору
    f.append(arrow(gxr, fy + 26, fx, fy + 26, color="#7c4bbf", sw=2))            # ліворуч у затвор
    f.append(text(gxr + 30, (cy + 20 + fy + 26) / 2, "GATE", size=11, bold=True, color="#7c4bbf"))
    # насос -> драйвер
    f.append(arrow(cx + 95, cy + 116, cx + 95, cy + 92, color="#b8860b", sw=1.6))

    # земля
    f.append(line(cx + cw / 2, cy + ch, cx + cw / 2, cy + ch + 22))
    f.append(line(cx + cw / 2 - 16, cy + ch + 22, cx + cw / 2 + 16, cy + ch + 22, sw=2))
    f.append(line(cx + cw / 2 - 10, cy + ch + 27, cx + cw / 2 + 10, cy + ch + 27, sw=2))
    f.append(line(cx + cw / 2 - 4, cy + ch + 32, cx + cw / 2 + 4, cy + ch + 32, sw=2))
    f.append(text(cx + cw / 2 + 30, cy + ch + 26, "GND", size=11, color=MUTED))

    render(os.path.join(IMG, 'ic-block.svg'), W, H, *f)


# ── Фігура 2. Типова розпіновка + підключення (5 виводів) ───────────────────
def fig_pinout():
    W, H = 720, 400
    f = []
    # корпус мікросхеми
    px, py, pw, ph = 260, 120, 200, 170
    f.append(rect(px, py, pw, ph, fill="#f7f4fb", stroke="#7c4bbf", sw=2))
    f.append(text(px + pw / 2, py + ph / 2 - 8, "IC", size=20, bold=True, color="#7c4bbf"))
    f.append(text(px + pw / 2, py + ph / 2 + 14, "ideal-diode", size=12, color=MUTED))

    pins_l = [("IN / ANODE", "вхід = витік FET", POS),
              ("GND", "земля", MUTED),
              ("OUT / CATHODE", "вихід = стік FET", FIELD)]
    pins_r = [("GATE", "до затвора FET", "#7c4bbf"),
              ("CPO / SRC", "кондер насоса / витік", "#b8860b")]
    n = 3
    for i, (nm, desc, col) in enumerate(pins_l):
        y = py + 35 + i * (ph - 60) / (n - 1)
        f.append(line(px - 40, y, px, y, sw=2))
        f.append(circle(px - 40, y, 4, fill=col, stroke=col))
        f.append(text(px - 46, y - 6, nm, size=12, bold=True, color=col, anchor="end"))
        f.append(text(px - 46, y + 11, desc, size=10, color=MUTED, anchor="end"))
    for i, (nm, desc, col) in enumerate(pins_r):
        y = py + 50 + i * 70
        f.append(line(px + pw, y, px + pw + 40, y, sw=2))
        f.append(circle(px + pw + 40, y, 4, fill=col, stroke=col))
        f.append(text(px + pw + 46, y - 6, nm, size=12, bold=True, color=col, anchor="start"))
        f.append(text(px + pw + 46, y + 11, desc, size=10, color=MUTED, anchor="start"))

    # підпис-порада внизу
    f.append(textbox(W / 2, 350, "Вхід і вихід — це витік і стік того самого FET: мікросхема міряє\nпадіння на каналі (Vds) як напрям струму й прикидається діодом.\nРізні виробники звуть ці виводи то IN/OUT, то ANODE/CATHODE", size=11, fill="#eef7f0", stroke=FIELD)[0])

    render(os.path.join(IMG, 'ic-pinout.svg'), W, H, *f)


# ── Фігура 3. Тремтіння затвора біля порога та ліки ─────────────────────────
def fig_chatter():
    W, H = 740, 380
    f = []
    # осі струму (горизонтальна вісь часу, вертикальна — струм навколо нуля)
    ox, oy = 80, 130
    axw = 560
    f.append(line(ox, oy, ox + axw, oy, color=MUTED, sw=1.2))   # нульова лінія струму
    f.append(text(ox - 10, oy + 4, "0", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - 40, "I", size=12, color=INK, anchor="end", italic=True))
    f.append(text(ox + axw, oy + 20, "час", size=11, color=MUTED, italic=True))
    # поріг компаратора трохи вище нуля (одне значення для лінії й для стану затвора)
    THR = 6                       # малий позитивний поріг у координатах струму
    thy = oy - THR
    f.append(line(ox, thy, ox + axw, thy, color=POS, sw=1.2, dash="5,4"))
    f.append(text(ox + axw + 6, thy + 4, "поріг", size=10, color=POS, anchor="start"))

    # струм навантаження, що дрейфує коло нуля -> перетинає поріг туди-сюди
    import math
    def curr(t):
        return 14 * math.sin(t * 8) + 2   # коливається навколо нуля
    pts = []
    for i in range(0, axw + 1, 6):
        t = i / axw
        pts.append((ox + i, oy - curr(t)))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, NEG))
    f.append(text(ox + 60, oy - 44, "струм коло нуля", size=10, color=NEG, anchor="start"))

    # gate стан: квадратна хвиля, що смикається, коли струм перетинає поріг
    gy = 250
    gh = 34
    f.append(text(ox - 10, gy - gh / 2, "Vgate", size=11, color="#7c4bbf", anchor="end"))
    # прямокутники ON/OFF: коли val>поріг => ON
    prev_on = None
    seg_x = ox
    lvl_on = gy - gh
    lvl_off = gy
    path_parts = []
    for i in range(0, axw + 1, 6):
        t = i / axw
        on = curr(t) > THR   # той самий поріг, що й намальована лінія
        yv = lvl_on if on else lvl_off
        path_parts.append((ox + i, yv))
    d2 = "M %.1f %.1f " % path_parts[0]
    for k in range(1, len(path_parts)):
        x, y = path_parts[k]
        py = path_parts[k - 1][1]
        d2 += "L %.1f %.1f L %.1f %.1f " % (x, py, x, y)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d2, "#7c4bbf"))
    f.append(text(ox + axw + 6, gy - gh / 2, "смикається", size=10, color=POS, anchor="start"))

    # рамка-ліки
    f.append(textbox(W / 2, 335, "Ліки: невеликий позитивний поріг + опір затвора 5–10 Ом і кондер 10–100 пФ,\nабо струм-«баласт» (~100 мкА) на виході, щоб петля не гойдалась коло нуля", size=11, fill="#eef7f0", stroke=FIELD)[0])

    render(os.path.join(IMG, 'ic-chatter.svg'), W, H, *f)


if __name__ == '__main__':
    fig_block()
    fig_pinout()
    fig_chatter()
    print("OK: ic-block.svg, ic-pinout.svg, ic-chatter.svg")
