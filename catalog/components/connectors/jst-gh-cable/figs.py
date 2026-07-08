# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_anatomy():
    """Устрій GH-зʼєднувача: корпус-гніздо (housing) з боковою засувкою,
    крок 1.25 мм, обтискний контакт (crimp) із дротом, ключ полярності."""
    W, H = 760, 520
    f = []

    # ── Верхній блок: корпус-гніздо (housing) вид збоку, з засувкою ──────────
    f.append(text(W/2, 30, "Корпус-гніздо (housing) GHR-06V-S — вид збоку", size=15, bold=True))

    hx, hy, hw, hh = 130, 70, 380, 90          # тіло корпусу
    f.append(rect(hx, hy, hw, hh, fill="#eef2f7", stroke=LINE, sw=2, rx=8))

    # шість гнізд контактів усередині (порожнини)
    n = 6
    pitch_px = 46
    gap0 = hx + 55
    for i in range(n):
        cx = gap0 + i*pitch_px
        f.append(rect(cx-13, hy+22, 26, hh-44, fill="#ffffff", stroke=MUTED, sw=1.2, rx=3))
        f.append(text(cx, hy+hh-14, str(i+1), size=12, color=MUTED))

    # бокова засувка (side latch) — виступ-пружина збоку
    f.append('<path d="M %d %d q -26 6 -26 26 q 0 20 26 26" fill="none" stroke="%s" stroke-width="3"/>'
             % (hx+4, hy+18, POS))
    lb, _, _ = textbox(hx-62, hy+hh/2, "бокова\nзасувка", size=11, color=POS,
                       fill="#fdecea", stroke=POS, sw=1.4, pad=7)
    f.append(lb)
    f.append(line(hx-30, hy+hh/2, hx-6, hy+hh/2, color=POS, sw=1.4))

    # ключ полярності (проріз згори — заходить лише одним боком)
    f.append(rect(hx+hw-70, hy-10, 22, 12, fill=FIELD, stroke=LINE, sw=1.2, rx=2))
    kb, _, _ = textbox(hx+hw+58, hy-2, "ключ\nполярності", size=11, color=FIELD,
                       fill="#e9f8ef", stroke=FIELD, sw=1.4, pad=7)
    f.append(kb)
    f.append(line(hx+hw-48, hy-4, hx+hw+8, hy-4, color=FIELD, sw=1.4))

    # розмір кроку 1.25 мм між двома сусідніми гніздами:
    # виносні лінії короткі (закінчуються НАД стрілкою), підпис — ще нижче,
    # тож ані лінії, ані стрілка не перетинають напис
    ax = gap0
    bx = gap0 + pitch_px
    dimy = hy+hh+22          # рівень стрілки-розміру
    f.append(line(ax, hy+hh+6, ax, dimy, color=NEG, sw=1))
    f.append(line(bx, hy+hh+6, bx, dimy, color=NEG, sw=1))
    f.append(arrow(ax, dimy, bx, dimy, color=NEG, sw=1.5))
    f.append(arrow(bx, dimy, ax, dimy, color=NEG, sw=1.5))
    f.append(text((ax+bx)/2, dimy+20, "1.25 мм — крок (pitch)", size=12, color=NEG, bold=True))

    # ── Нижній блок: обтискний контакт (crimp) із дротом ─────────────────────
    f.append(text(W/2, 300, "Обтискний контакт SSHL-002T-P0.2 + дріт AWG 26–30", size=15, bold=True))

    cx0, cy0 = 90, 360
    # пружинна частина (гніздо-мама, куди входить штир плати)
    f.append(rect(cx0, cy0-18, 66, 36, fill="#eef2f7", stroke=LINE, sw=2, rx=5))
    # підпис пружинного контакту — ліворуч-знизу, з виносним штрихом
    f.append(line(cx0+33, cy0+18, cx0+33, cy0+40, color=MUTED, sw=1))
    f.append(text(cx0+33, cy0+54, "пружинний", size=11, color=INK))
    f.append(text(cx0+33, cy0+70, "контакт", size=11, color=INK))

    # обтискні «крила» під жилу (ближче) та ізоляцію (далі)
    wing1 = cx0+80
    wing2 = cx0+126
    f.append('<path d="M %d %d l 14 -16 l 14 16 M %d %d l 14 16 l 14 -16" fill="none" stroke="%s" stroke-width="2"/>'
             % (wing1, cy0-2, wing1, cy0+2, INK))
    f.append('<path d="M %d %d l 16 -18 l 16 18 M %d %d l 16 18 l 16 -18" fill="none" stroke="%s" stroke-width="2"/>'
             % (wing2, cy0-2, wing2, cy0+2, INK))
    # підписи крил — рознесені по вертикалі, кожен зі своїм штрихом (не в один рядок → без накладань)
    f.append(line(wing1+14, cy0+18, wing1+14, cy0+40, color=MUTED, sw=1))
    f.append(text(wing1+14, cy0+54, "обтиск жили", size=11, color=INK))
    f.append(line(wing2+16, cy0+22, wing2+16, cy0+72, color=MUTED, sw=1))
    f.append(text(wing2+16, cy0+86, "обтиск ізоляції", size=11, color=INK))

    # дріт: жила (мідь) + ізоляція
    wy = cy0
    f.append(line(cx0+114, wy, cx0+156, wy, color=POS, sw=3))            # оголена жила
    f.append(rect(cx0+156, wy-10, 210, 20, fill="#ffe9c7", stroke="#c98a1a", sw=1.5, rx=8))  # ізоляція
    f.append(line(cx0+171, wy, cx0+357, wy, color=POS, sw=3))
    f.append(text(cx0+261, wy-18, "ізольований провід", size=11, color="#9a6a12"))
    f.append(text(cx0+261, wy+72, "жила: мідь, ~0.05–0.13 мм²", size=11, color="#9a6a12"))

    return render(os.path.join(IMG, 'gh-anatomy.svg'), W, H, *f)


def fig_pinout():
    """Орієнтація пін-1 і типові порти Pixhawk на GH: TELEM-6, GPS-6, I2C-4, CAN-4, Power-6.
    Пін-1 завжди 5V, останній — GND; шукати пін-1 за міткою/трикутником на корпусі."""
    W, H = 820, 640
    f = []
    f.append(text(W/2, 30, "Пін-1 і стандартні порти Pixhawk (DS-009) на JST-GH", size=15, bold=True))

    # ── орієнтація пін-1 ─────────────────────────────────────────────────────
    ox, oy = 60, 60
    f.append(rect(ox, oy, 300, 84, fill="#eef2f7", stroke=LINE, sw=2, rx=8))
    for i in range(6):
        cx = ox+40 + i*44
        col = POS if i == 0 else (NEG if i == 5 else "#ffffff")
        f.append(circle(cx, oy+42, 13, fill=col, stroke=LINE, sw=1.5))
        f.append(text(cx, oy+47, str(i+1), size=12,
                      color="#ffffff" if i in (0, 5) else INK, bold=(i in (0, 5))))
    # трикутник-мітка над пін-1
    f.append('<path d="M %d %d l 8 -12 l 8 12 z" fill="%s"/>' % (ox+40-8, oy+16, POS))
    f.append(text(ox+150, oy-6, "мітка/трикутник = пін 1", size=12, color=POS, bold=True))
    lb, _, _ = textbox(ox+150, oy+112, "пін 1 = 5V (червоний)   ·   останній = GND (чорний)",
                       size=12, pad=8, fill=FILL, stroke=MUTED, sw=1.2)
    f.append(lb)

    # ── таблиці портів ───────────────────────────────────────────────────────
    def port(px, py, title, pins, title_col=INK):
        rowh = 26
        colw = 210
        f.append(fitbox(px, py, colw, 24, title, size=13, bold=True,
                        fill="#e8edf3", stroke=LINE, sw=1.4))
        for i, (name, note) in enumerate(pins):
            yy = py + 24 + i*rowh
            # номер піна
            numcol = POS if i == 0 else (NEG if i == len(pins)-1 else "#ffffff")
            f.append(rect(px, yy, 30, rowh, fill=numcol, stroke=LINE, sw=1))
            f.append(text(px+15, yy+rowh-8, str(i+1), size=12,
                          color="#ffffff" if (i == 0 or i == len(pins)-1) else INK, bold=True))
            # назва сигналу
            f.append(rect(px+30, yy, colw-30, rowh, fill="#ffffff", stroke=MUTED, sw=1))
            f.append(text(px+40, yy+rowh-8, name, size=12, anchor="start",
                          color=INK, bold=True))
            if note:
                f.append(text(px+colw-10, yy+rowh-8, note, size=10, anchor="end", color=MUTED))
        return py + 24 + len(pins)*rowh

    # ряд 1: TELEM, GPS
    y1 = 210
    port(60, y1, "TELEM (6-pin)", [
        ("5V", "жив."), ("TX", "→ радіо"), ("RX", "← радіо"),
        ("CTS", "потік"), ("RTS", "потік"), ("GND", "земля")])
    port(320, y1, "GPS (6-pin)", [
        ("5V", "жив."), ("TX", "→ GPS"), ("RX", "← GPS"),
        ("SCL", "I²C"), ("SDA", "I²C"), ("GND", "земля")])

    # ряд 1 продовження: Power праворуч
    port(580, y1, "POWER (6-pin)", [
        ("5V", "вихід"), ("5V", "вихід"), ("I_BAT", "струм"),
        ("V_BAT", "напруга"), ("GND", "земля"), ("GND", "земля")])

    # ряд 2: I2C, CAN
    y2 = y1 + 24 + 6*26 + 30
    port(60, y2, "I²C (4-pin)", [
        ("5V", "жив."), ("SCL", "такт"), ("SDA", "дані"), ("GND", "земля")])
    port(320, y2, "CAN (4-pin)", [
        ("5V", "жив."), ("CAN_H", "шина"), ("CAN_L", "шина"), ("GND", "земля")])

    # примітка про сигнальні рівні
    note, _, _ = textbox(600, y2+70,
                         "Сигнали: логіка 3.3V\n(TTL, не RS-232!)\nЖивлення пінів 5V\nструм ≤ 1 A на контакт",
                         size=12, pad=10, fill="#fdf6e3", stroke="#c98a1a", sw=1.4, color="#7a5310")
    f.append(note)

    return render(os.path.join(IMG, 'gh-pinout.svg'), W, H, *f)


def fig_timeline():
    """Історична дуга: чому Pixhawk перейшов із DF13 на JST-GH.
    Три епохи — DF13 без клямки, хаос клонів, ухвалення стандарту GH."""
    W, H = 900, 470
    f = []
    f.append(text(W / 2, 30, "Від DF13 до JST-GH: чому змінили зʼєднувач", size=16, bold=True))

    # горизонтальна вісь часу
    axy = 96
    f.append(line(50, axy, W - 50, axy, color=MUTED, sw=2))
    for xx, lbl in [(140, "2013"), (360, "2014"), (560, "2015–16"), (790, "2020")]:
        f.append(circle(xx, axy, 5, fill=INK, stroke=INK, sw=1))
        f.append(text(xx, axy - 14, lbl, size=12, color=MUTED, bold=True))

    # ── Епоха 1: DF13 (біль) ────────────────────────────────────────────────
    b1x, b1y, b1w, b1h = 60, 130, 250, 150
    f.append(rect(b1x, b1y, b1w, b1h, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    f.append(text(b1x + b1w / 2, b1y + 24, "Pixhawk 1: Hirose DF13", size=13, bold=True, color=POS))
    for i, ln in enumerate(["— тримається лише тертям,", "  без клямки → губиться в", "  вібрації",
                            "— контакти крихітні,", "  вручну не обтиснути",
                            "— знімати важко"]):
        f.append(text(b1x + 14, b1y + 48 + i * 17, ln, size=11, anchor="start", color=INK))

    # ── Епоха 2: хаос клонів ────────────────────────────────────────────────
    b2x, b2y, b2w, b2h = 335, 300, 250, 130
    f.append(rect(b2x, b2y, b2w, b2h, fill="#fff7e6", stroke="#c98a1a", sw=1.6, rx=8))
    f.append(text(b2x + b2w / 2, b2y + 24, "Хаос клонів", size=13, bold=True, color="#9a6a12"))
    for i, ln in enumerate(["десятки копій ставлять", "несумісні зʼєднувачі:", "JST SH (1.0 мм) чи",
                            "Molex PicoBlade —", "піни гнуться, не заходить"]):
        f.append(text(b2x + 14, b2y + 48 + i * 17, ln, size=11, anchor="start", color=INK))

    # ── Епоха 3: стандарт GH ────────────────────────────────────────────────
    b3x, b3y, b3w, b3h = 610, 130, 250, 165
    f.append(rect(b3x, b3y, b3w, b3h, fill="#e9f8ef", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(b3x + b3w / 2, b3y + 24, "Стандарт: JST-GH", size=13, bold=True, color="#1e7a45"))
    for i, ln in enumerate(["— бокова клямка тримає", "  під вібрацією",
                            "— ключ полярності",
                            "— однакові розкладки", "  в усіх виробників",
                            "Cube ~2015 → GH;", "Dronecode HW-WG 2016;", "документ DS-009"]):
        f.append(text(b3x + 14, b3y + 48 + i * 17, ln, size=11, anchor="start", color=INK))

    # звʼязки-стрілки між епохами (нижче написів, повз рамки)
    f.append(arrow(b1x + b1w, b1y + b1h - 30, b2x, b2y + 20, color=MUTED, sw=1.8))
    f.append(arrow(b2x + b2w, b2y + 20, b3x, b3y + b3h - 30, color=MUTED, sw=1.8))

    return render(os.path.join(IMG, 'gh-history.svg'), W, H, *f)


if __name__ == '__main__':
    print(fig_anatomy())
    print(fig_pinout())
    print(fig_timeline())
