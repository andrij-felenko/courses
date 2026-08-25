# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── classic: постійне з'єднання двох пристроїв ────────────────────────────────
# Ідея: Classic — це пара «точка-точка» з неперервним двостороннім потоком,
# на відміну від мережі з багатьма вузлами; «завжди увімкнене» радіо їсть енергію.

def fig_classic():
    W, H = 700, 250
    p = []
    y = 130
    lx, rx = 150, 550

    a, aw, ah = textbox(lx, y, "телефон", size=14, bold=True, fill="#eef4ff", stroke=NEG, sw=2, min_w=150)
    b, bw, bh = textbox(rx, y, "ESP32", size=14, bold=True, fill="#eafaf0", stroke=FIELD, sw=2, min_w=150)

    # неперервний двосторонній потік: дві зустрічні стрілки
    p.append(arrow(lx + aw / 2 + 4, y - 12, rx - bw / 2 - 4, y - 12, color=INK, sw=2.2))
    p.append(arrow(rx - bw / 2 - 4, y + 12, lx + aw / 2 + 4, y + 12, color=INK, sw=2.2))
    p.append(text(W / 2, y - 22, "неперервний потік в обидва боки", size=12, color=INK, bold=True))
    p.append(text(W / 2, y + 36, "з'єднання живе весь час", size=11, color=MUTED, italic=True))

    p.append(a)
    p.append(b)

    p.append(text(W / 2, H - 26, "радіо «завжди увімкнене» — стабільний потік, але відчутна витрата енергії",
                  size=11, color=POS, italic=True))

    render(os.path.join(OUT, "classic.svg"), W, H, *p,
           title="Bluetooth Classic: стала пара «точка-точка»")


# ── spp: заміна дроту UART радіоканалом ───────────────────────────────────────
# Ідея: та сама модель — послідовний потік байтів, — лише канал тепер радіо;
# тому код майже не міняється (Serial → SerialBT).

def fig_spp():
    W, H = 700, 300
    p = []

    # верх: було — дріт UART
    yt = 96
    la, aw, ah = textbox(150, yt, "пристрій A", size=13, bold=True, fill=FILL, stroke=INK, sw=1.6, min_w=150)
    lb, bw, bh = textbox(550, yt, "пристрій B", size=13, bold=True, fill=FILL, stroke=INK, sw=1.6, min_w=150)
    p.append(line(150 + aw / 2, yt, 550 - bw / 2, yt, color=INK, sw=2.4))
    p.append(text(W / 2, yt - 12, "дріт UART (TX / RX / GND)", size=11, color=INK, bold=True))
    p.append(la)
    p.append(lb)
    p.append(text(60, yt + 4, "БУЛО", size=12, color=MUTED, bold=True, anchor="start"))

    # низ: стало — той самий потік по Bluetooth SPP
    yb = 214
    ca, _, _ = textbox(150, yb, "пристрій A", size=13, bold=True, fill="#eef4ff", stroke=NEG, sw=1.8, min_w=150)
    cb, _, _ = textbox(550, yb, "пристрій B", size=13, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8, min_w=150)
    # хвиляста «радіо» лінія між ними
    pts = []
    x0, x1 = 150 + aw / 2, 550 - bw / 2
    for i in range(0, 121):
        t = i / 120.0
        x = x0 + t * (x1 - x0)
        yy = yb + 7 * math.sin(t * math.pi * 9)
        pts.append("%.1f,%.1f" % (x, yy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="round"/>' % (" ".join(pts), NEG))
    p.append(text(W / 2, yb - 12, "той самий потік байтів по Bluetooth SPP", size=11, color=NEG, bold=True))
    p.append(ca)
    p.append(cb)
    p.append(text(60, yb + 4, "СТАЛО", size=12, color=MUTED, bold=True, anchor="start"))

    p.append(text(W / 2, H - 18, "модель та сама — послідовний потік; змінився лише канал",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "spp.svg"), W, H, *p,
           title="SPP: Bluetooth прикидається UART (дріт → радіо)")


# ── pairing: спарювання як одноразова довіра ──────────────────────────────────
# Ідея: чотири кроки — виявлення, ключ, довіра (обмін ключами), пам'ять; далі
# пристрої з'єднуються самі.

def fig_pairing():
    W, H = 740, 230
    p = []
    y = 116
    bw, bh = 150, 64
    gap = 36
    total = 4 * bw + 3 * gap
    x = (W - total) / 2
    steps = [
        ("Виявлення", "знайти поруч", "#eef4ff", NEG),
        ("Ключ", "PIN / звірка", "#fdf6e3", "#b8860b"),
        ("Довіра", "обмін ключами", "#eafaf0", FIELD),
        ("Пам'ять", "далі — самі", "#f2ecf8", "#8a5fb0"),
    ]
    centers = []
    for i, (title_s, sub, fill, col) in enumerate(steps):
        bx = x + i * (bw + gap)
        p.append(rect(bx, y - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.8))
        p.append(text(bx + bw / 2, y - 6, title_s, size=13, color=col, bold=True))
        p.append(text(bx + bw / 2, y + 16, sub, size=11, color=INK))
        centers.append((bx, bx + bw))
        if i > 0:
            p.append(arrow(centers[i - 1][1] + 2, y, bx - 2, y, color=INK, sw=1.8))

    p.append(text(W / 2, H - 22, "робиться раз: спарилися — і відтепер пристрої «свої»",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "pairing.svg"), W, H, *p,
           title="Спарювання: одноразова довіра між двома")


# ── profiles: профіль = готовий сценарій під задачу ───────────────────────────
# Ідея: профіль домовляється не лише ЯК передати біти, а й ЩО саме; SPP — для
# довільних даних, решта спеціалізовані.

def fig_profiles():
    W, H = 700, 280
    p = []
    profs = [
        ("SPP", "послідовні дані\n(бездротовий UART)", FIELD, "#eafaf0"),
        ("A2DP", "стереозвук\n(навушники)", NEG, "#eef4ff"),
        ("HID", "клавіатури, миші\n(ввід)", "#8a5fb0", "#f2ecf8"),
        ("HFP", "гарнітура, дзвінки\n(голос)", POS, "#fdecea"),
    ]
    bw, bh = 150, 92
    gap = 28
    total = 4 * bw + 3 * gap
    x0 = (W - total) / 2
    y = 120
    for i, (name, sub, col, fill) in enumerate(profs):
        bx = x0 + i * (bw + gap)
        p.append(rect(bx, y, bw, bh, fill=fill, stroke=col, sw=1.8))
        p.append(text(bx + bw / 2, y + 26, name, size=16, color=col, bold=True))
        p.append(mtext(bx + bw / 2, y + 50, sub, size=11, color=INK))

    # SPP підкреслити як універсальний для довільних даних
    p.append(text(x0 + bw / 2, y + bh + 22, "↑ для довільних даних — саме SPP",
                  size=11, color=FIELD, bold=True))
    p.append(text(W / 2, H - 16, "кожен профіль домовляється не лише ЯК передати біти, а й ЩО саме й навіщо",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "profiles.svg"), W, H, *p,
           title="Профілі Bluetooth: готові сценарії під різні задачі")


# ── underhood: чистий потік нагорі, брудний ефір унизу ────────────────────────
# Ідея: застосунок бачить рівний UART-потік; стек робить пакети/CRC/ACK/ретраї;
# найнижче — спільний шумний ефір 2.4 ГГц. SPP ховає ненадійність, не скасовує.

def fig_underhood():
    W, H = 726, 300
    p = []
    bx, bw = 120, 460
    layers = [
        (70,  "застосунок: SerialBT.print / read", "#eafaf0", FIELD, "бачить рівний UART-потік"),
        (140, "стек Bluetooth: RFCOMM, пакети, CRC, ACK, ретраї, стрибки частоти", "#eef4ff", NEG, "ховає всю чорну роботу"),
        (210, "ефір 2.4 ГГц: спільний, з втратами й завадами", "#fdecea", POS, "тут реальна ненадійність"),
    ]
    for cy, lab, fill, col, note in layers:
        p.append(fitbox(bx, cy - 26, bw, 52, lab, size=12, fill=fill, stroke=col, sw=1.8, bold=True, color=INK))
        p.append(text(bx + bw + 10, cy + 4, note, size=10, color=col, anchor="start"))

    # стрілки «униз/угору» між шарами
    for y1, y2 in [(96, 114), (166, 184)]:
        p.append(arrow(W / 2 - 30, y1, W / 2 - 30, y2, color=MUTED, sw=1.5))
        p.append(arrow(W / 2 + 30, y2, W / 2 + 30, y1, color=MUTED, sw=1.5))

    p.append(text(W / 2, H - 24, "чистий потік нагорі — результат боротьби стека внизу; SPP ховає ненадійність, а не скасовує",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "underhood.svg"), W, H, *p,
           title="Під капотом SPP: чистий потік над брудним ефіром")


# ── classic-vs-ble: потік проти ощадливих сплесків ────────────────────────────
# Ідея: Classic — неперервний потік (енергія), BLE — короткі сплески й сон
# (мізерна енергія). Дві різні філософії на одній часовій осі.

def fig_classic_vs_ble():
    W, H = 700, 300
    p = []
    ox = 150
    aw = 500

    # Classic: суцільна «зайнята» смуга
    yc = 96
    p.append(text(ox - 12, yc + 4, "Classic", size=13, color=NEG, bold=True, anchor="end"))
    p.append(rect(ox, yc - 14, aw, 28, fill="#eef4ff", stroke=NEG, sw=1.6, rx=4))
    p.append(text(ox + aw / 2, yc + 5, "неперервний потік — радіо ввімкнене весь час", size=11, color=NEG))

    # BLE: рідкі вузькі сплески, між ними сон
    yb = 190
    p.append(text(ox - 12, yb + 4, "BLE", size=13, color=FIELD, bold=True, anchor="end"))
    p.append(line(ox, yb, ox + aw, yb, color=MUTED, sw=1.2, dash="4 4"))
    for i in range(5):
        sx = ox + 30 + i * (aw - 60) / 4
        p.append(rect(sx - 7, yb - 22, 14, 44, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=2))
    p.append(text(ox + aw / 2, yb + 40, "короткі сплески, між ними пристрій спить", size=11, color=FIELD))

    # підписи призначення
    p.append(text(ox + aw / 2, yc - 26, "звук, файли, серійні дані (SPP) — енергія не критична",
                  size=10, color=MUTED, italic=True))
    p.append(text(W / 2, H - 18, "BLE: давачі, маячки, носимі — роки від маленької батарейки (характеристики, GATT)",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "classic-vs-ble.svg"), W, H, *p,
           title="Classic проти BLE: потік проти ощадливих сплесків")


if __name__ == "__main__":
    fig_classic()
    fig_spp()
    fig_pairing()
    fig_profiles()
    fig_underhood()
    fig_classic_vs_ble()
    print("OK: figures written to", OUT)
