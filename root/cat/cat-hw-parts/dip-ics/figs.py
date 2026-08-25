# -*- coding: utf-8 -*-
"""Фігури для статті «DIP-мікросхеми (драйвери)».
Дві SVG: (1) анатомія й відлік виводів DIP-корпусу; (2) карта ролей трьох
ключових драйверних мікросхем набору. Чистий Python, залежність — лише svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_anatomy():
    """DIP згори: виїмка й крапка на «носі», два ряди по 7, відлік проти
    годинникової від виводу 1, крок 2.54 мм між сусідніми ніжками."""
    W, H = 760, 470
    frags = []

    # --- корпус мікросхеми (вид згори) ---
    bx, by, bw, bh = 250, 90, 260, 250
    frags.append(rect(bx, by, bw, bh, fill="#2b2b2b", stroke="#111", sw=2, rx=10))

    # виїмка (напівколо) на верхньому краю — маркер «носа»
    notch_cx = bx + bw / 2
    frags.append('<path d="M %.1f %.1f A 16 16 0 0 0 %.1f %.1f" '
                 'fill="%s" stroke="#111" stroke-width="2"/>'
                 % (notch_cx - 16, by, notch_cx + 16, by, BG))
    # крапка-заглибина біля виводу 1 (лівий верхній кут)
    frags.append(circle(bx + 24, by + 26, 7, fill="#111", stroke="#555", sw=1.5))

    # --- ніжки: 7 ліворуч (низ→верх: 1..7), 7 праворуч (верх→низ: 8..14) ---
    n = 7
    pitch = (bh - 44) / (n - 1)          # крок між центрами ніжок
    y0 = by + 22
    leg_w, leg_len = 16, 30

    # ліві ніжки — виводи 1..7 знизу вгору
    for i in range(n):
        num = i + 1
        cy = by + bh - 22 - i * pitch     # 1 унизу, 7 угорі
        frags.append(rect(bx - leg_len, cy - leg_w / 2, leg_len, leg_w,
                          fill="#c9ccd1", stroke="#7a7d82", sw=1.2, rx=2))
        frags.append(text(bx - leg_len - 16, cy + 5, str(num),
                          size=15, color=INK, bold=True))
        frags.append(text(bx + 22, cy + 5, str(num), size=13, color="#e8e8e8"))

    # праві ніжки — виводи 8..14 зверху вниз
    for i in range(n):
        num = 8 + i
        cy = by + 22 + i * pitch          # 8 угорі, 14 унизу
        frags.append(rect(bx + bw, cy - leg_w / 2, leg_len, leg_w,
                          fill="#c9ccd1", stroke="#7a7d82", sw=1.2, rx=2))
        frags.append(text(bx + bw + leg_len + 16, cy + 5, str(num),
                          size=15, color=INK, bold=True))
        frags.append(text(bx + bw - 22, cy + 5, str(num), size=13, color="#e8e8e8"))

    # напис на корпусі
    frags.append(text(notch_cx, by + bh / 2 + 6, "IC", size=34,
                      color="#8a8d92", bold=True))

    # --- стрілка відліку: проти годинникової від виводу 1 ---
    a_cx, a_cy = notch_cx, by + bh - 6
    frags.append('<path d="M %.1f %.1f q -70 46 -118 -2" fill="none" '
                 'stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
                 % (notch_cx + 40, by + bh + 34, FIELD))
    frags.append(text(notch_cx + 6, by + bh + 58,
                      "відлік проти годинникової від 1", size=13,
                      color=FIELD, bold=True))

    # підпис до виїмки
    tb, tw, th = textbox(notch_cx, 46, "виїмка + крапка = бік виводу 1",
                         size=13, bold=True, fill="#eef7f0", stroke=FIELD)
    frags.append(tb)

    # крок між ніжками
    frags.append(line(bx - leg_len - 40, by + bh - 22,
                      bx - leg_len - 40, by + bh - 22 - pitch,
                      color=MUTED, sw=1.4))
    frags.append(text(bx - leg_len - 46, by + bh - 22 - pitch / 2 + 4,
                      "2.54 мм", size=12, color=MUTED, anchor="end"))

    render(os.path.join(OUT, 'dip-anatomy.svg'), W, H, *frags)


def fig_roles():
    """Три драйверні DIP-и набору й що кожен «підсилює»: сигнал МК → навантаження."""
    W, H = 780, 430
    frags = []

    chips = [
        ("ULN2003", "16 ніг", "7 стоків до −",
         ["реле, соленоїди,", "крокові, яскраві LED"], "50 В · 0.5 А ×7"),
        ("L293D", "16 ніг", "2 H-мости",
         ["2 мотори вперед/назад,", "регуляція обертів"], "36 В · 0.6 А ×2"),
        ("74HC595", "16 ніг", "3 лінії → 8 виходів",
         ["нарощує виводи:", "жене байт послідовно"], "лог. рівень, малий струм"),
    ]

    col_w = 246
    x0 = 14
    gap = 8
    top = 70

    frags.append(text(W / 2, 34,
                      "три «драйвери» набору — кожен бере слабкий сигнал і керує сильним навантаженням",
                      size=13, color=MUTED))

    for i, (name, pins, core, load, rating) in enumerate(chips):
        cx = x0 + i * (col_w + gap) + col_w / 2

        # корпус-DIP (стилізований)
        chw, chh = 150, 96
        chx, chy = cx - chw / 2, top
        frags.append(rect(chx, chy, chw, chh, fill="#2b2b2b", stroke="#111", sw=2, rx=8))
        # виїмка
        frags.append('<path d="M %.1f %.1f A 12 12 0 0 0 %.1f %.1f" '
                     'fill="%s" stroke="#111" stroke-width="2"/>'
                     % (cx - 12, chy, cx + 12, chy, BG))
        frags.append(text(cx, chy + chh / 2 + 6, name, size=19, color="#f0f0f0", bold=True))
        # ніжки-риски по боках
        for k in range(8):
            ly = chy + 12 + k * ((chh - 24) / 7)
            frags.append(line(chx - 10, ly, chx, ly, color="#c9ccd1", sw=3))
            frags.append(line(chx + chw, ly, chx + chw + 10, ly, color="#c9ccd1", sw=3))

        # ярлик корпусу
        frags.append(text(cx, top + chh + 20, pins + " · DIP", size=12, color=MUTED))

        # серце («що робить»)
        b, bw2, bh2 = textbox(cx, top + chh + 52, core, size=14, bold=True,
                              fill="#eef2ff", stroke=NEG, min_w=col_w - 30)
        frags.append(b)

        # стрілка вниз до навантаження
        ay = top + chh + 52 + bh2 / 2
        frags.append(line(cx, ay + 6, cx, ay + 26, color=FIELD, sw=2.2))
        frags.append('<path d="M %.1f %.1f l -5 -8 l 10 0 z" fill="%s"/>'
                     % (cx, ay + 8, FIELD))

        # навантаження (дворядковий підпис фіксованим кеглем — без стискання)
        lbx, lbw, lbh = cx - (col_w - 24) / 2, col_w - 24, 52
        frags.append(rect(lbx, ay + 30, lbw, lbh, fill="#eef7f0", stroke=FIELD, sw=1.5))
        frags.append(mtext(cx, ay + 30 + 22, load, size=12, color=INK, lh=1.35))

        # характеристика виходу
        frags.append(text(cx, ay + 104, rating, size=11, color=MUTED))

    render(os.path.join(OUT, 'dip-roles.svg'), W, H, *frags)


def fig_595_uln_chain():
    """Зв'язка 74HC595 → ULN2003: три лінії МК заганяють байт у регістр,
    вісім виходів регістра йдуть на входи масиву, масив тягне струм у 8 навантажень
    зі свого плюса. Показує розподіл ролей: регістр вирішує ХТО, масив дає СКІЛЬКИ."""
    W, H = 820, 470
    frags = []

    # --- три лінії від МК ліворуч ---
    mcx, mcy, mcw, mch = 30, 150, 116, 150
    frags.append(rect(mcx, mcy, mcw, mch, fill="#eef2ff", stroke=NEG, sw=1.6))
    frags.append(text(mcx + mcw / 2, mcy + 26, "МК", size=17, color=INK, bold=True))
    sigs = [("DATA", "дані"), ("CLOCK", "такт"), ("LATCH", "засувка")]
    sig_y = []
    for i, (nm, ua) in enumerate(sigs):
        yy = mcy + 52 + i * 30
        sig_y.append(yy)
        frags.append(text(mcx + mcw / 2, yy, nm, size=12, color=NEG, bold=True))

    # --- 74HC595 ---
    rx, ry, rw, rh = 210, 96, 150, 258
    frags.append(rect(rx, ry, rw, rh, fill="#2b2b2b", stroke="#111", sw=2, rx=8))
    frags.append(text(rx + rw / 2, ry + 26, "74HC595", size=16, color="#f0f0f0", bold=True))
    frags.append(text(rx + rw / 2, ry + 46, "зсувний регістр", size=11, color="#b8bcc4"))

    # три входи регістра (зліва) — від МК
    in_labels = ["DS 14", "SHCP 11", "STCP 12"]
    for i, lab in enumerate(in_labels):
        yy = ry + 78 + i * 26
        frags.append(line(mcx + mcw, sig_y[i], rx, yy, color=NEG, sw=1.8))
        frags.append(text(rx + 6, yy + 4, lab, size=10, color="#cfd3da", anchor="start"))

    # вісім виходів регістра (справа): Q0..Q7
    q_y = []
    for i in range(8):
        yy = ry + 34 + i * ((rh - 52) / 7)
        q_y.append(yy)
        frags.append(line(rx + rw, yy, rx + rw + 12, yy, color="#c9ccd1", sw=2.4))
        frags.append(text(rx + rw - 8, yy + 4, "Q%d" % i, size=10, color="#cfd3da", anchor="end"))

    # --- ULN2003 ---
    ux, uy, uw, uh = 470, 96, 150, 258
    frags.append(rect(ux, uy, uw, uh, fill="#2b2b2b", stroke="#111", sw=2, rx=8))
    frags.append(text(ux + uw / 2, uy + 26, "ULN2003", size=16, color="#f0f0f0", bold=True))
    frags.append(text(ux + uw / 2, uy + 46, "7 стоків струму", size=11, color="#b8bcc4"))

    # входи масиву (зліва) IN1..IN7 — беруть Q0..Q6
    for i in range(7):
        yy = q_y[i]
        frags.append(line(rx + rw + 12, yy, ux, yy, color=FIELD, sw=1.8))
        frags.append(text(ux + 6, yy + 4, "IN%d" % (i + 1), size=10, color="#cfd3da", anchor="start"))
    # восьмий вихід Q7 нікуди (регістр має 8, масив — 7)
    frags.append(text(rx + rw + 74, q_y[7] + 4, "Q7 — вільний", size=10, color=MUTED, anchor="middle"))

    # виходи масиву (справа) OUT1..OUT7 → навантаження
    for i in range(7):
        yy = uy + 34 + i * ((uh - 52) / 6)
        frags.append(line(ux + uw, yy, ux + uw + 12, yy, color=POS, sw=2.4))
        # маленький кружок-навантаження
        lx = ux + uw + 40
        frags.append(circle(lx, yy, 8, fill="#fdecea", stroke=POS, sw=1.6))
        frags.append(text(lx + 22, yy + 4, "OUT%d" % (i + 1), size=10, color=MUTED, anchor="start"))

    # --- спільний плюс на COM ---
    plus_y = uy - 6
    frags.append(plus(ux + uw + 40, plus_y, r=9))
    frags.append(text(ux + uw + 62, plus_y + 4, "+V нав.", size=11, color=POS, anchor="start", bold=True))
    frags.append(line(ux + uw + 40, plus_y + 9, ux + uw + 40, uy + 34, color=POS, sw=1.4, dash="4,3"))
    # підпис COM→плюс
    frags.append(text(ux + uw / 2, uy + uh - 8, "COM 9 → +V", size=11, color=POS, bold=True))

    # --- підписи ролей унизу ---
    b1, w1, h1 = textbox(rx + rw / 2, H - 46, "вирішує ХТО ввімкнеться\n(3 ноги → 8 бітів)",
                         size=12, bold=True, fill="#eef2ff", stroke=NEG, min_w=190)
    frags.append(b1)
    b2, w2, h2 = textbox(ux + uw / 2, H - 46, "дає СКІЛЬКИ струму\n(тягне навантаження в −)",
                         size=12, bold=True, fill="#eef7f0", stroke=FIELD, min_w=190)
    frags.append(b2)

    frags.append(text(W / 2, 34,
                      "зв'язка 74HC595 → ULN2003: регістр адресує канали, масив живить їх",
                      size=13, color=MUTED))

    render(os.path.join(OUT, 'dip-595-uln-chain.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_anatomy()
    fig_roles()
    fig_595_uln_chain()
    print("figs done")
