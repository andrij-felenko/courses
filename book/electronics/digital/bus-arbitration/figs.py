# -*- coding: utf-8 -*-
"""Фігури до теми «Арбітраж шини».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

WIN = "#27ae60"   # переможець
LOSE = "#c0392b"  # той, хто відступив
GRANT = "#2457d6"  # сигнал дозволу


# ── 1. Проблема: двоє захотіли шину водночас ────────────────────────────────
def fig_problem():
    W, H = 700, 300
    f = [text(W/2, 26, "Спільна шина: двоє хочуть говорити водночас", size=17, bold=True)]
    busy = 150
    # спільна лінія-шина
    f.append(line(60, busy, 640, busy, color=INK, sw=4))
    f.append(text(350, busy-14, "спільна шина (одна на всіх)", size=12, color=MUTED))
    # три майстри зверху
    xs = [150, 350, 550]
    labs = ["Майстер A", "Майстер B", "Майстер C"]
    want = [True, True, False]
    for x, lb, w in zip(xs, labs, want):
        col = LOSE if w else MUTED
        b, bw, bh = textbox(x, 90, lb, size=13, fill="#fdecea" if w else FILL,
                            stroke=col, bold=w)
        f.append(b)
        f.append(line(x, 90+bh/2, x, busy, color=col, sw=2.5,
                      dash="5,4" if not w else None))
        if w:
            f.append(text(x, 128, "хочу писати!", size=11.5, color=LOSE, italic=True))
    # знак зіткнення в центрі
    f.append(circle(350, busy, 15, fill="#fdecea", stroke=LOSE, sw=3))
    f.append(text(350, busy+5, "!", size=20, color=LOSE, bold=True))
    # висновок унизу
    f.append(fitbox(120, 210, 460, 62,
                    "A жене «1», B жене «0» на ту саму лінію —\n"
                    "рівень невизначений, дані зіпсовані, виходи в конфлікті.\n"
                    "Треба правило: хто говорить зараз?",
                    size=12.5, fill="#fff7ec", stroke="#b08900"))
    render(os.path.join(IMG, "problem.svg"), W, H, *f)


# ── 2. Три родини арбітражу поруч ────────────────────────────────────────────
def fig_families():
    W, H = 720, 360
    f = [text(W/2, 26, "Три способи вирішити, хто веде шину", size=17, bold=True)]
    cols = [70, 320, 500]  # ліві краї трьох панелей (розширимо)
    # рівномірні панелі
    pw = 210
    xs = [20, 255, 490]
    titles = ["Централізований\n(один суддя)", "Ланцюжок\n(дозвіл біжить рядком)",
              "Розподілений\n(змагання на лінії)"]
    for x, ttl in zip(xs, titles):
        f.append(rect(x, 44, pw, 296, fill=BG, stroke=LINE, sw=1.5))
        f.append(mtext(x+pw/2, 66, ttl.split("\n"), size=13, bold=True))

    # панель 1: арбітр у центрі, три пристрої тягнуть REQ, він шле GRANT одному
    ax = xs[0]
    arbx, arby = ax+pw/2, 150
    b, bw, bh = textbox(arbx, arby, "АРБІТР", size=12, fill="#eaf0fd", stroke=GRANT, bold=True)
    f.append(b)
    devy = 250
    dxs = [ax+45, ax+105, ax+165]
    for i, dx in enumerate(dxs):
        won = (i == 0)
        f.append(circle(dx, devy, 16, fill="#eafaf0" if won else FILL,
                        stroke=WIN if won else MUTED, sw=2))
        f.append(text(dx, devy+4, "%d" % (i+1), size=12, bold=won))
        # REQ угору (сірий), GRANT вниз тільки переможцю (синій)
        f.append(line(dx, devy-16, arbx if i==0 else dx, arby+bh/2 if i==0 else devy-40,
                      color=MUTED, sw=1.3, dash="4,3"))
    f.append(arrow(arbx, arby+bh/2, dxs[0], devy-16, color=GRANT, sw=2.2))
    f.append(text(ax+pw/2, 300, "дозвіл — пристрою 1", size=10.5, color=GRANT))
    f.append(text(ax+pw/2, 316, "решта чекає", size=10.5, color=MUTED))

    # панель 2: ланцюжок — GRANT входить зліва, зупиняється на першому охочому
    bx = xs[1]
    chy = 150
    cxs = [bx+40, bx+105, bx+170]
    stop = 1  # другий у ланцюжку — перший охочий → бере й блокує далі
    for i, cx in enumerate(cxs):
        active = (i == stop)
        f.append(circle(cx, chy, 17, fill="#eafaf0" if active else FILL,
                        stroke=WIN if active else MUTED, sw=2.2 if active else 1.5))
        f.append(text(cx, chy+4, "%d" % (i+1), size=12, bold=active))
        f.append(text(cx, chy+34, "охочий" if active else "-",
                      size=10, color=WIN if active else MUTED))
    # вхід GRANT зліва
    f.append(arrow(bx+8, chy, cxs[0]-17, chy, color=GRANT, sw=2.2))
    f.append(text(bx+20, chy-12, "GRANT", size=10, color=GRANT))
    # проходить крізь 1 (не охочий) до 2
    f.append(arrow(cxs[0]+17, chy, cxs[1]-17, chy, color=GRANT, sw=2.2))
    # від 2 далі — перекреслено (заблоковано)
    f.append(line(cxs[1]+17, chy, cxs[2]-17, chy, color=LOSE, sw=2, dash="4,3"))
    f.append(text((cxs[1]+cxs[2])/2, chy-10, "стоп", size=10, color=LOSE))
    f.append(text(bx+pw/2, 250, "Ближчий до входу", size=11, color=INK))
    f.append(text(bx+pw/2, 268, "завжди старший", size=11, color=INK))
    f.append(text(bx+pw/2, 292, "просто, але фіксований", size=10, color=MUTED))
    f.append(text(bx+pw/2, 308, "пріоритет", size=10, color=MUTED))

    # панель 3: розподілений — усі женуть ID на wired-AND, менший ID виграє
    dx0 = xs[2]
    liney = 160
    f.append(line(dx0+20, liney, dx0+pw-20, liney, color=INK, sw=3.5))
    f.append(text(dx0+pw/2, liney-10, "спільна лінія (0 б'є 1)", size=10, color=MUTED))
    ddxs = [dx0+50, dx0+105, dx0+160]
    ids = ["ID 3", "ID 5", "ID 9"]
    for i, (cx, idv) in enumerate(zip(ddxs, ids)):
        won = (i == 0)
        f.append(circle(cx, liney+55, 17, fill="#eafaf0" if won else FILL,
                        stroke=WIN if won else MUTED, sw=2.2 if won else 1.5))
        f.append(text(cx, liney+59, idv, size=10.5, bold=won))
        f.append(line(cx, liney+38, cx, liney, color=WIN if won else MUTED,
                      sw=2 if won else 1.3, dash=None if won else "4,3"))
    f.append(text(dx0+pw/2, 250, "Усі кидають номер", size=11, color=INK))
    f.append(text(dx0+pw/2, 268, "на лінію водночас;", size=11, color=INK))
    f.append(text(dx0+pw/2, 292, "менший номер виграє,", size=10, color=WIN))
    f.append(text(dx0+pw/2, 308, "решта відступає сама", size=10, color=MUTED))
    render(os.path.join(IMG, "families.svg"), W, H, *f)


# ── 3. Недеструктивне змагання біт-за-бітом (часова діаграма) ────────────────
def fig_bitwise():
    W, H = 720, 360
    f = [text(W/2, 26, "Змагання біт-за-бітом: «0» перемагає «1»", size=17, bold=True)]
    x0, dx = 150, 78
    bits_a = [0, 1, 0, 1, 1, 0]   # майстер A (менший номер)
    bits_b = [0, 1, 1, 0, 0, 1]   # майстер B — розійшлися на 3-му біті
    hi, lo = 0, 34
    rowY = {"A": 90, "B": 175, "BUS": 285}
    hA = rowY["A"]; hB = rowY["B"]; hBus = rowY["BUS"]

    def draw_wave(y, bits, color, label, gone_after=None):
        f.append(text(x0-24, y+lo+2, label, size=13, color=color, bold=True, anchor="end"))
        px, py = x0, y + (hi if bits[0] == 1 else lo)
        for i, b in enumerate(bits):
            if gone_after is not None and i > gone_after:
                # після поразки B «відпускає» — лінію показуємо блідо-пунктиром на «1»
                nx = x0 + (i+1)*dx
                yy = y + hi
                f.append(line(x0 + gone_after*dx + dx, y+hi, W-40, y+hi,
                              color=MUTED, sw=1.4, dash="3,4"))
                break
            yy = y + (hi if b == 1 else lo)
            if yy != py:
                f.append(line(px, py, px, yy, color=color, sw=2.4))
            nx = x0 + (i+1)*dx
            f.append(line(px, yy, nx, yy, color=color, sw=2.4))
            f.append(text((px+nx)/2, yy-8 if b == 1 else yy+18, str(b),
                          size=13, color=color, bold=True))
            px, py = nx, yy

    # вертикальні напрямні бітів
    for i in range(len(bits_a)+1):
        xx = x0 + i*dx
        f.append(line(xx, 78, xx, 320, color="#e5e7eb", sw=1))
    # позначки рівнів
    for y in (hA, hB, hBus):
        f.append(text(x0-24, y+hi-4, "1", size=10, color=MUTED, anchor="end"))
    draw_wave(hA, bits_a, WIN, "A")
    draw_wave(hB, bits_b, LOSE, "B", gone_after=2)
    # шина = wired-AND: 0, якщо хоч один 0
    bus = [a & b for a, b in zip(bits_a, bits_b)]
    # після 3-го біта шина = чисто A
    bus_eff = bus[:3] + bits_a[3:]
    draw_wave(hBus, bus_eff, INK, "ШИНА")

    # маркер точки розбіжності
    dxpos = x0 + 2*dx + dx/2
    f.append(line(dxpos, 70, dxpos, 330, color=LOSE, sw=1.6, dash="5,4"))
    f.append(text(dxpos, 64, "тут розійшлися", size=11, color=LOSE))
    f.append(text(dxpos+2, 200, "B жене 1, читає 0 →", size=10.5, color=LOSE, anchor="start"))
    f.append(text(dxpos+2, 216, "«я програв», мовчить", size=10.5, color=LOSE, anchor="start"))
    # підсумок
    f.append(text(x0+3*dx, hBus+52, "далі шина = повідомлення A, ціле й неушкоджене",
                  size=11, color=WIN, anchor="start"))
    render(os.path.join(IMG, "bitwise.svg"), W, H, *f)


# ── 4. Пріоритет, справедливість, голодування ───────────────────────────────
def fig_fairness():
    W, H = 700, 300
    f = [text(W/2, 26, "Ціна пріоритету: жорсткий проти по-колу", size=17, bold=True)]
    # ліва панель — фіксований пріоритет
    f.append(rect(30, 46, 300, 236, fill=BG, stroke=LINE))
    f.append(text(180, 68, "Жорсткий пріоритет", size=13, bold=True))
    laby = [95, 130, 165, 200]
    who = ["1 (найстарший)", "2", "3", "4 (наймолодший)"]
    served = [True, True, False, False]
    for y, w, s in zip(laby, who, served):
        col = WIN if s else LOSE
        f.append(circle(70, y, 12, fill="#eafaf0" if s else "#fdecea", stroke=col, sw=2))
        f.append(text(70, y+4, "•", size=14, color=col))
        f.append(text(92, y+4, w, size=11.5, anchor="start"))
        f.append(text(250, y+4, "веде" if s else "чекає...", size=11,
                      color=col, anchor="start"))
    f.append(fitbox(48, 218, 264, 50,
                    "Хто зайнятий — той і тримає шину.\n"
                    "Молодші можуть чекати вічно = голодування.",
                    size=10.8, fill="#fdecea", stroke=LOSE))
    # права панель — round-robin
    f.append(rect(370, 46, 300, 236, fill=BG, stroke=LINE))
    f.append(text(520, 68, "По колу (round-robin)", size=13, bold=True))
    cx, cy, r = 520, 150, 58
    import math
    for i in range(4):
        a = -math.pi/2 + i*math.pi/2
        px, py = cx + r*math.cos(a), cy + r*math.sin(a)
        nxt = (-math.pi/2 + (i+1)*math.pi/2)
        qx, qy = cx + r*math.cos(nxt), cy + r*math.sin(nxt)
        f.append(circle(px, py, 15, fill="#eafaf0", stroke=WIN, sw=2))
        f.append(text(px, py+4, "%d" % (i+1), size=12, bold=True))
        # стрілка по колу
        f.append(arrow(px + 12*math.cos(a+0.5), py + 12*math.sin(a+0.5),
                       qx - 12*math.cos(nxt-0.5), qy - 12*math.sin(nxt-0.5),
                       color=GRANT, sw=1.8))
    f.append(fitbox(388, 218, 264, 50,
                    "Черга йде по колу: кожен рано\n"
                    "чи пізно дістає шину. Голодування немає.",
                    size=10.8, fill="#eafaf0", stroke=WIN))
    render(os.path.join(IMG, "fairness.svg"), W, H, *f)


if __name__ == "__main__":
    fig_problem()
    fig_families()
    fig_bitwise()
    fig_fairness()
    print("OK: figures written to", IMG)
