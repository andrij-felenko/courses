# -*- coding: utf-8 -*-
"""Фігури для статті YP-08 — модуль живлення (breadboard power supply, MB102-родина).
Дві фігури:
  1) topology.svg — внутрішня будова: вхід -> AMS1117-5.0 -> шина 5В -> AMS1117-3.3 -> шина 3.3В (каскад).
  2) mounting.svg — як модуль сідає на живильні рейки макетки, джампери 5В/OFF/3.3В, гребінки.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: внутрішня топологія (каскад двох LDO) ──────────────────────────
def fig_topology():
    W, H = 780, 400
    p = []

    # Вхід: DC-гніздо
    b, bw, bh = textbox(95, 120, "DC-гніздо\n6.5–12 В", size=13, min_w=140,
                        fill="#eef2ff", stroke=NEG)
    p.append(b)
    p.append(plus(95 - bw/2 + 16, 120 - bh/2 - 10, r=8))

    # Вхід: USB
    b2, b2w, b2h = textbox(95, 240, "USB-A\n≈5 В", size=13, min_w=140,
                          fill="#eef2ff", stroke=NEG)
    p.append(b2)

    # Вимикач між входом і першим регулятором
    p.append(textbox(255, 120, "вимикач", size=12, min_w=90, fill="#f4f6f8")[0])

    # U1: AMS1117-5.0
    u1x = 420
    b3, b3w, b3h = textbox(u1x, 120, "U1  AMS1117-5.0\nLDO", size=13, min_w=185,
                          fill="#fff6e6", stroke=POS, bold=True)
    p.append(b3)

    # Шина 5В
    r5x = 600
    b4, b4w, b4h = textbox(r5x, 120, "шина 5 В", size=14, min_w=120,
                          fill="#fdecea", stroke=POS, bold=True)
    p.append(b4)

    # U2: AMS1117-3.3 (живиться від 5В!)
    u2x = 420
    b5, b5w, b5h = textbox(u2x, 300, "U2  AMS1117-3.3\nLDO", size=13, min_w=185,
                          fill="#eaf7ef", stroke=FIELD, bold=True)
    p.append(b5)

    # Шина 3.3В
    b6, b6w, b6h = textbox(r5x, 300, "шина 3.3 В", size=14, min_w=120,
                          fill="#eaf7ef", stroke=FIELD, bold=True)
    p.append(b6)

    # З'єднання
    # DC -> вимикач
    p.append(line(95 + bw/2, 120, 255 - 45, 120, color=INK, sw=2))
    # USB -> об'єднання перед U1 (входить у ту саму точку зліва від U1)
    join_x = 255 - 45
    p.append(line(95 + b2w/2, 240, join_x, 240, color=INK, sw=2))
    p.append(line(join_x, 240, join_x, 120, color=INK, sw=2))
    p.append(circle(join_x, 120, 3.5, fill=INK, stroke=INK))
    # вимикач -> U1
    p.append(arrow(255 + 45, 120, u1x - b3w/2, 120, color=INK, sw=2))
    # U1 -> шина 5В
    p.append(arrow(u1x + b3w/2, 120, r5x - b4w/2, 120, color=POS, sw=2.4))
    # шина 5В -> вниз -> U2 (каскад)
    tap_x = r5x - b4w/2 - 30
    p.append(line(r5x - b4w/2, 120, tap_x, 120, color=POS, sw=2.2))
    p.append(circle(tap_x, 120, 3.5, fill=POS, stroke=POS))
    p.append(line(tap_x, 120, tap_x, 300, color=POS, sw=2.2))
    p.append(arrow(tap_x, 300, u2x + b5w/2, 300, color=POS, sw=2.2))
    # U2 -> шина 3.3В
    p.append(arrow(u2x - b5w/2, 300, u2x - b5w/2 - 40, 300, color=FIELD, sw=2.2))
    # маленький гачок, щоб дійти до шини 3.3В праворуч
    hook = u2x - b5w/2 - 40
    p.append(line(hook, 300, hook, 355, color=FIELD, sw=2.2))
    p.append(line(hook, 355, r5x, 355, color=FIELD, sw=2.2))
    p.append(arrow(r5x, 355, r5x, 300 + b6h/2, color=FIELD, sw=2.2))

    # Підпис-ключ: 3.3В бере СТРУМ від 5В
    note, nw, nh = textbox(r5x, 210, "3.3 В живиться\nВІД шини 5 В", size=12,
                          min_w=140, fill="#fffbe6", stroke=MUTED)
    p.append(note)

    return render(os.path.join(IMG, 'topology.svg'), W, H, *p,
                  title="YP-08: два лінійні регулятори каскадом")


# ── Фігура 2: посадка на макетку + джампери ──────────────────────────────────
def fig_mounting():
    W, H = 760, 440
    p = []

    # Плата модуля (велика рамка зверху)
    board_x, board_y, board_w, board_h = 120, 60, 520, 150
    p.append(rect(board_x, board_y, board_w, board_h, fill="#f0f4ff",
                  stroke=NEG, sw=2, rx=10))
    p.append(text(board_x + board_w/2, board_y + 24, "модуль YP-08 (вигляд згори)",
                  size=14, bold=True, color=NEG))

    # Два джампери-селектори на платі: лівий рейл і правий рейл
    def selector(cx, cy, label, pos):
        # pos: '5V' (верх), 'OFF' (центр), '3V3' (низ)
        gx = []
        colw, rowh = 74, 26
        # три позиції по вертикалі: 5В / OFF / 3.3В
        opts = [("5 В", POS), ("OFF", MUTED), ("3.3 В", FIELD)]
        for i, (t, c) in enumerate(opts):
            yy = cy - rowh + i * rowh
            active = ((pos == '5V' and i == 0) or (pos == 'OFF' and i == 1)
                      or (pos == '3V3' and i == 2))
            fill = ("#fdecea" if i == 0 else "#eee" if i == 1 else "#eaf7ef")
            gx.append(rect(cx - colw/2, yy - rowh/2, colw, rowh,
                           fill=(fill if active else "#ffffff"),
                           stroke=(c if active else "#cfcfcf"),
                           sw=(2.2 if active else 1), rx=4))
            gx.append(text(cx, yy + 5, t, size=12,
                           color=(c if active else "#9aa0a6"),
                           bold=active))
        gx.append(text(cx, cy - rowh*1.7, label, size=12, bold=True))
        # позначка перемички (колодка з 3 контактів)
        return "".join(gx)

    p.append(selector(board_x + 130, board_y + 88, "лівий рейл", '5V'))
    p.append(selector(board_x + 300, board_y + 88, "правий рейл", '3V3'))

    # Гребінка виводів (GND/3.3/5) праворуч на платі
    hdr_x = board_x + board_w - 70
    p.append(rect(hdr_x - 22, board_y + 50, 52, 74, fill="#fff", stroke=LINE, sw=1.4, rx=5))
    for i, (t, c) in enumerate([("5V", POS), ("G", INK), ("3V3", FIELD)]):
        yy = board_y + 66 + i * 22
        p.append(circle(hdr_x, yy, 5, fill="#d9b310", stroke="#8a6d00", sw=1.2))
        p.append(text(hdr_x - 30, yy + 4, t, size=11, color=c, anchor="end", bold=True))
    p.append(text(hdr_x + 4, board_y + 138, "гребінка", size=10, color=MUTED))

    # Штирі вниз (2 ряди по 0.1" — входять у дві живильні лінії макетки)
    pin_y0 = board_y + board_h
    pin_y1 = 300  # рівень рейок макетки
    left_pins_x = [board_x + 40, board_x + 40 + 20]
    right_pins_x = [board_x + board_w - 40 - 20, board_x + board_w - 40]
    for xx in left_pins_x + right_pins_x:
        p.append(line(xx, pin_y0, xx, pin_y1 - 6, color="#8a6d00", sw=2.4))

    # Макетна плата (живильні рейки)
    bb_x, bb_y, bb_w, bb_h = 80, pin_y1, 600, 110
    p.append(rect(bb_x, bb_y, bb_w, bb_h, fill="#faf7f0", stroke=MUTED, sw=1.6, rx=8))
    # Дві пари рейок: + та − зверху, + та − знизу
    def rail(y, sign, color, label):
        p.append(line(bb_x + 20, y, bb_x + bb_w - 20, y, color=color, sw=2.6))
        p.append(text(bb_x + 8, y + 4, sign, size=15, color=color, anchor="middle", bold=True))
        p.append(text(bb_x + bb_w - 8, y + 4, sign, size=15, color=color, anchor="middle", bold=True))
        p.append(text(bb_x + bb_w/2, y - 8, label, size=10, color=MUTED))
    rail(bb_y + 22, "+", POS, "лівий рейл → +")
    rail(bb_y + 40, "−", INK, "спільний GND")
    rail(bb_y + 74, "+", FIELD, "правий рейл → +")
    rail(bb_y + 92, "−", INK, "спільний GND")

    # Підпис під усім
    cap, cw, ch = textbox(W/2, H - 16, "лівий і правий рейли — незалежні: один можна дати 5 В, другий 3.3 В",
                          size=12, min_w=200, fill="#ffffff", stroke="#ffffff")
    p.append(cap)

    return render(os.path.join(IMG, 'mounting.svg'), W, H, *p,
                  title="YP-08: посадка на живильні рейки макетки")


# ── Фігура 3: дільник із рейки на АЦП + вікно вимірювання ────────────────────
def fig_divider():
    W, H = 800, 470
    p = []

    # Ліва частина — схема дільника (вертикальна колонка)
    col_x = 175
    top_y = 78          # рейка
    r1_y = 150          # R1
    node_y = 240        # вузол відводу на АЦП
    r2_y = 320          # R2
    gnd_y = 400         # земля

    # Рейка 5 В (горизонтальна риска зверху)
    p.append(line(col_x - 70, top_y, col_x + 70, top_y, color=POS, sw=3))
    p.append(plus(col_x - 60, top_y, r=9))
    p.append(text(col_x, top_y - 16, "рейка 5 В", size=13, color=POS, bold=True))
    p.append(line(col_x, top_y, col_x, r1_y - 26, color=INK, sw=2))

    # R1 (верхнє плече)
    r1, r1w, r1h = textbox(col_x, r1_y, "R1\n10 кОм", size=12, min_w=96,
                           fill="#fff6e6", stroke=POS)
    p.append(r1)
    p.append(line(col_x, r1_y + r1h/2, col_x, node_y, color=INK, sw=2))

    # Вузол відводу
    p.append(circle(col_x, node_y, 4.5, fill=INK, stroke=INK))
    # відвід праворуч на АЦП
    p.append(line(col_x, node_y, col_x + 120, node_y, color=NEG, sw=2.4))
    p.append(arrow(col_x + 120, node_y, col_x + 175, node_y, color=NEG, sw=2.4))

    # R2 (нижнє плече)
    p.append(line(col_x, node_y, col_x, r2_y - r1h/2, color=INK, sw=2))
    r2, r2w, r2h = textbox(col_x, r2_y, "R2\n15 кОм", size=12, min_w=96,
                           fill="#eef2ff", stroke=NEG)
    p.append(r2)
    p.append(line(col_x, r2_y + r2h/2, col_x, gnd_y, color=INK, sw=2))

    # Земля (спільна з модулем!)
    p.append(line(col_x - 34, gnd_y, col_x + 34, gnd_y, color=INK, sw=3))
    p.append(line(col_x - 22, gnd_y + 8, col_x + 22, gnd_y + 8, color=INK, sw=2.4))
    p.append(line(col_x - 11, gnd_y + 16, col_x + 11, gnd_y + 16, color=INK, sw=2))
    p.append(text(col_x, gnd_y + 40, "спільний GND з YP-08", size=12, color=MUTED))

    # Пін АЦП (права колонка) — рамка мікроконтролера
    mcu_x, mcu_y, mcu_w, mcu_h = col_x + 175, node_y - 46, 190, 92
    p.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#eaf7ef", stroke=FIELD, sw=2, rx=8))
    p.append(text(mcu_x + mcu_w/2, mcu_y + 26, "МК: пін АЦП", size=13, bold=True, color=FIELD))
    p.append(text(mcu_x + mcu_w/2, mcu_y + 50, "Uадц = 5·R2/(R1+R2)", size=12, color=INK))
    p.append(text(mcu_x + mcu_w/2, mcu_y + 70, "= 5·15/25 = 3.0 В", size=12, color=INK, bold=True))

    # Права нижня — «вікно» діапазону АЦП: смуга 0..Uref, куди лягає 3.0 В із запасом
    bar_x, bar_y, bar_w, bar_h = mcu_x + 12, gnd_y - 34, 166, 22
    p.append(rect(bar_x, bar_y, bar_w, bar_h, fill="#f4f6f8", stroke=LINE, sw=1.4, rx=4))
    # заливка «використаної» частини діапазону (до 3.0 з 3.3 ⇒ ~0.91)
    used = bar_w * (3.0 / 3.3)
    p.append(rect(bar_x, bar_y, used, bar_h, fill="#eaf7ef", stroke="none", sw=0, rx=4))
    xin = bar_x + used
    p.append(line(xin, bar_y - 6, xin, bar_y + bar_h + 6, color=FIELD, sw=2.4))
    p.append(text(bar_x, bar_y - 10, "0 В", size=11, color=MUTED, anchor="start"))
    p.append(text(bar_x + bar_w, bar_y - 10, "Uref = 3.3 В", size=11, color=MUTED, anchor="end"))
    p.append(text(bar_x + bar_w/2, bar_y + bar_h + 26,
                  "3.0 В — є запас до межі", size=11, color=FIELD, anchor="middle", bold=True))

    return render(os.path.join(IMG, 'divider.svg'), W, H, *p,
                  title="Дільник із рейки на АЦП: вимір напруги без перевищення діапазону")


if __name__ == '__main__':
    fig_topology()
    fig_mounting()
    fig_divider()
    print("OK: figs generated")
