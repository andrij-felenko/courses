# -*- coding: utf-8 -*-
# Фігури вставки proj-galvanic-isolation.md (окремий модуль, бо головний figs.py
# одночасно правлять інші агенти-вставки). Вивід — у спільну теку ./img.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Петля по землі ──────────────────────────────────────────────────────────
def fig_ground_loop():
    W, H = 820, 380
    f = []
    f.append(text(W/2, 26, "Петля по землі: сигнальний контур замикається ще й через землю", size=15, bold=True))

    bx, by, bw, bh = 70, 70, 150, 60
    f.append(fitbox(bx, by, bw, bh, "Давач\n(передавач)", size=13, bold=True))
    rx, ry = 600, 70
    f.append(fitbox(rx, ry, bw, bh, "Приймач\n(АЦП, R_вим)", size=13, bold=True))

    f.append(line(bx+bw, by+18, rx, ry+18, color=INK, sw=2.2))
    f.append(line(bx+bw, by+42, rx, ry+42, color=INK, sw=2.2))
    f.append(text(W/2, by-2, "сигнальна пара 4–20 мА", size=11, color=MUTED))
    f.append(arrow(330, by+18, 410, by+18, color=POS, sw=2.0))

    gA_x, gA_y = bx+bw/2, 230
    gB_x, gB_y = rx+bw/2, 230
    f.append(line(gA_x, by+bh, gA_x, gA_y, color=MUTED, sw=1.6))
    f.append(line(gB_x, ry+bh, gB_x, gB_y, color=MUTED, sw=1.6))
    for cx, cy, lab in [(gA_x, gA_y, "земля A"), (gB_x, gB_y, "земля B")]:
        f.append(line(cx-26, cy, cx+26, cy, color=INK, sw=2.5))
        f.append(line(cx-17, cy+7, cx+17, cy+7, color=INK, sw=2.0))
        f.append(line(cx-8, cy+14, cx+8, cy+14, color=INK, sw=2.0))
        f.append(text(cx, cy+30, lab, size=11, color=MUTED))
    f.append(line(gA_x, gA_y, gB_x, gB_y, color=NEG, sw=2.2, dash="7 5"))
    f.append(textbox((gA_x+gB_x)/2, gA_y+52, "U_земель ≈ кілька В\n(приводи, зварювання)", size=11,
                     fill="#eaf0fd", stroke=NEG, color=NEG)[0])
    f.append(text(W/2, by+78, "струм землі тече по тому ж контурі й додається до 4–20 мА",
                  size=12, color=POS, bold=True))

    render(os.path.join(IMG, 'ground-loop.svg'), W, H, *f)


# ── Бар'єр у петлі ──────────────────────────────────────────────────────────
def fig_barrier():
    W, H = 820, 350
    f = []
    f.append(text(W/2, 26, "Бар'єр у петлі: сигнал крізь, постійний контур землі — стоп", size=15, bold=True))

    midx = W/2
    f.append(line(midx, 60, midx, H-36, color=POS, sw=2.5, dash="6 6"))
    f.append(textbox(midx, 52, "БАР'ЄР", size=12, fill="#fdecea", stroke=POS, color=POS, bold=True)[0])
    f.append(text(midx/2, 78, "бік давача — земля A", size=12, bold=True, color=MUTED))
    f.append(text(midx + midx/2, 78, "бік приймача — земля B", size=12, bold=True, color=MUTED))

    inx, iny, bw, bh = 110, 115, 210, 80
    f.append(fitbox(inx, iny, bw, bh, "Вхід ізолятора\nчитає струм петлі,\nкерує світлом/полем", size=12, bold=True))
    outx = midx + 80
    f.append(fitbox(outx, iny, bw, bh, "Вихід ізолятора\nвідновлює струм,\nживить нову петлю", size=12, bold=True))

    f.append(arrow(inx+bw, iny+bh/2, outx, iny+bh/2, color=FIELD, sw=2.6))
    f.append(text(midx, iny+bh/2-12, "світло / поле", size=12, color=FIELD, bold=True))
    f.append(text(midx, iny+bh/2+22, "несе СИГНАЛ", size=11, color="#1e7a46"))

    f.append(textbox(inx+bw/2, 285, "так: змінний сигнал\n(значення струму)", size=11,
                     fill="#eafaf0", stroke=FIELD, color="#1e7a46")[0])
    f.append(textbox(outx+bw/2, 285, "ні: постійний контур\nструму землі — розірвано", size=11,
                     fill="#fdecea", stroke=POS, color=POS)[0])
    f.append(text(inx+bw/2, 225, "живлення A", size=10, color=MUTED))
    f.append(text(outx+bw/2, 225, "живлення B (ізольоване DC-DC)", size=10, color=MUTED))

    render(os.path.join(IMG, 'barrier.svg'), W, H, *f)


# ── Лінійна оптопара з сервопетлею ──────────────────────────────────────────
def fig_servo():
    W, H = 840, 400
    f = []
    f.append(text(W/2, 26, "Лінійна оптопара: два фотодіоди й сервопетля прибирають дрейф LED", size=15, bold=True))

    midx = W/2
    f.append(line(midx, 60, midx, H-44, color=POS, sw=2.2, dash="6 6"))
    f.append(text(midx, 54, "бар'єр", size=11, color=POS, bold=True))

    led_x, led_y = midx-120, 150
    f.append(circle(led_x, led_y, 16, fill="#fff6da", stroke="#d39e00", sw=2))
    f.append(text(led_x, led_y+5, "LED", size=11, bold=True, color="#8a6d00"))

    pd1_x, pd1_y = midx-40, 150
    pd2_x, pd2_y = midx+40, 150
    f.append(circle(pd1_x, pd1_y, 14, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(pd1_x, pd1_y+4, "PD1", size=10, bold=True, color=NEG))
    f.append(circle(pd2_x, pd2_y, 14, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(pd2_x, pd2_y+4, "PD2", size=10, bold=True, color=NEG))
    f.append(text(pd1_x, pd1_y+32, "серво (K1)", size=9, color=MUTED))
    f.append(text(pd2_x, pd2_y+32, "вихід (K2)", size=9, color=MUTED))

    f.append(arrow(led_x+16, led_y-6, pd1_x-14, pd1_y-6, color=FIELD, sw=1.8))
    f.append(arrow(led_x+16, led_y, pd2_x-14, pd2_y, color=FIELD, sw=1.8))

    ax, ay, aw, ah = 70, 120, 110, 60
    f.append(fitbox(ax, ay, aw, ah, "вх. ОП\nкерує LED", size=11, bold=True))
    f.append(text(ax+aw/2, ay-10, "I_вх (4–20 мА)", size=10, color=MUTED))
    f.append(arrow(ax-30, ay+ah/2, ax, ay+ah/2, color=INK, sw=1.8))
    f.append(arrow(ax+aw, ay+ah/2, led_x-16, led_y, color=INK, sw=1.8))
    f.append(line(pd1_x, pd1_y+14, pd1_x, 255, color=NEG, sw=1.8))
    f.append(line(pd1_x, 255, ax+aw/2, 255, color=NEG, sw=1.8))
    f.append(arrow(ax+aw/2, 255, ax+aw/2, ay+ah, color=NEG, sw=1.8))
    f.append(text((pd1_x+ax)/2, 272, "зворотний зв'язок: струм PD1 = завдання", size=10, color=NEG))

    ox, oy, ow, oh = W-180, 120, 110, 60
    f.append(fitbox(ox, oy, ow, oh, "вих. ОП\nI_PD2 → U", size=11, bold=True))
    f.append(arrow(pd2_x+14, pd2_y, ox, oy+oh/2, color=INK, sw=1.8))
    f.append(arrow(ox+ow, oy+oh/2, ox+ow+30, oy+oh/2, color=INK, sw=1.8))
    f.append(text(ox+ow+12, oy+oh/2-10, "U_вих", size=10, color=MUTED))

    f.append(textbox(midx, H-22, "K3 = K2/K1: яскравість LED випадає — лишається стале відношення фотодіодів",
                     size=11, fill="#eafaf0", stroke=FIELD, color="#1e7a46")[0])

    render(os.path.join(IMG, 'servo-optocoupler.svg'), W, H, *f)


if __name__ == '__main__':
    fig_ground_loop()
    fig_barrier()
    fig_servo()
    print("galvanic isolation figs done")
