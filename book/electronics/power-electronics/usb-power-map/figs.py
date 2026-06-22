# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── ladder: драбина потужності USB ────────────────────────────────────────────
# Ідея: той самий роз'єм, а потужність росте сходами; підпис кожного щабля —
# хто й коли підняв стелю. Зростає домовленість, не залізо.

def fig_ladder():
    W, H = 720, 360
    p = []
    base_x, base_y = 70, 320
    steps = [
        ("USB 2.0", "2.5 Вт", "5 В · 0.5 А"),
        ("USB 3.0", "4.5 Вт", "5 В · 0.9 А"),
        ("BC 1.2", "7.5 Вт", "5 В · 1.5 А"),
        ("USB-C", "15 Вт", "5 В · 3 А"),
        ("USB-PD", "100 Вт", "20 В · 5 А"),
        ("PD EPR", "240 Вт", "48 В · 5 А"),
    ]
    n = len(steps)
    sw_ = 100          # ширина щабля
    rise = 44          # висота одного щабля
    cols = ["#eef4ff", "#e4eeff", "#dfeede", "#d6ead6", "#fdf0d6", "#fde0da"]
    for i, (lab, watt, vi) in enumerate(steps):
        h = (i + 1) * rise
        x = base_x + i * sw_
        y = base_y - h
        p.append(rect(x, y, sw_ - 8, h, fill=cols[i], stroke=INK, sw=1.4, rx=0))
        p.append(text(x + (sw_ - 8) / 2, y + 20, watt, size=14, color=INK, bold=True))
        p.append(text(x + (sw_ - 8) / 2, y + 38, lab, size=11, color=INK))
        p.append(text(x + (sw_ - 8) / 2, base_y + 16, vi, size=9, color=MUTED))

    # стрілка зростання вздовж верхівок сходів
    p.append(arrow(base_x - 8, base_y - rise + 6, base_x + (n - 1) * sw_ + sw_ - 20,
                   base_y - n * rise + 6, color=POS, sw=1.6))
    p.append(text(base_x + 8, base_y - n * rise - 8,
                  "× 100 потужності — на тому самому роз'ємі", size=12, color=POS, anchor="start", bold=True))
    p.append(line(base_x - 8, base_y, base_x + n * sw_ - 8, base_y, color=INK, sw=1.6))

    render(os.path.join(OUT, "ladder.svg"), W, H, *p,
           title="Драбина живлення USB: зростає домовленість, не залізо")


# ── connectors: покоління роз'ємів і їхні межі ────────────────────────────────
# Ідея: чотири роз'єми в ряд із позначкою струму й «однобічний/реверсивний»;
# Type-C виділено як носія всіх нових механізмів.

def fig_connectors():
    W, H = 720, 250
    p = []
    y = 120
    items = [
        ("Type-A", "до 0.9 А", "однобічний · хост", FILL),
        ("micro-USB", "до 1.5 А", "однобічний · застарів", FILL),
        ("mini-USB", "до 1.5 А", "однобічний · застарів", FILL),
        ("Type-C", "до 5 А", "реверсивний · CC, PD", "#dff0df"),
    ]
    bw, bh, gap = 150, 64, 22
    total = len(items) * bw + (len(items) - 1) * gap
    x = (W - total) / 2
    for lab, cur, note, fill in items:
        p.append(rect(x, y - bh / 2, bw, bh, fill=fill, stroke=INK, sw=1.6, rx=8))
        p.append(text(x + bw / 2, y - 8, lab, size=15, color=INK, bold=True))
        p.append(text(x + bw / 2, y + 12, cur, size=12, color=POS, bold=True))
        p.append(text(x + bw / 2, y + bh / 2 + 18, note, size=10, color=MUTED))
        x += bw + gap

    p.append(text(W / 2, H - 18,
                  "побачив Type-C — можливі високий струм і PD; побачив A чи micro — живлення скромне",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "connectors.svg"), W, H, *p,
           title="Покоління роз'ємів одразу підказують межі живлення")


# ── usbc-base: рівні струму через резистори CC ────────────────────────────────
# Ідея: джерело з Rp, пристрій з Rd, дільник на лінії CC; напруга на CC читає
# дозволений струм. Жодного чипа — два резистори.

def fig_usbc_base():
    W, H = 700, 300
    p = []
    # дві коробки: джерело й пристрій
    sx, dx = 90, 510
    by, bw, bh = 90, 120, 120
    p.append(rect(sx, by, bw, bh, fill="#fdf0d6", stroke=INK, sw=1.6, rx=8))
    p.append(text(sx + bw / 2, by + 22, "джерело", size=13, color=INK, bold=True))
    p.append(rect(dx, by, bw, bh, fill="#dff0df", stroke=INK, sw=1.6, rx=8))
    p.append(text(dx + bw / 2, by + 22, "пристрій", size=13, color=INK, bold=True))

    # лінія CC між ними
    cc_y = by + 70
    p.append(line(sx + bw, cc_y, dx, cc_y, color=INK, sw=2.0))
    p.append(text((sx + bw + dx) / 2, cc_y - 12, "лінія CC", size=12, color=NEG, bold=True))

    # Rp у джерелі (до VBUS), Rd у пристрої (до землі)
    p.append(text(sx + bw / 2, by + 70, "Rp", size=13, color=POS, bold=True))
    p.append(text(sx + bw / 2, by + 90, "(до 5 В)", size=9, color=MUTED))
    p.append(text(dx + bw / 2, by + 70, "Rd", size=13, color=NEG, bold=True))
    p.append(text(dx + bw / 2, by + 90, "(до землі)", size=9, color=MUTED))

    # стрілка «читає напругу» від точки CC у пристрій
    p.append(text((sx + bw + dx) / 2, cc_y + 22,
                  "напруга на дільнику → дозволений струм", size=11, color=INK))

    # три рівні внизу
    lv = textbox(W / 2, 250, "стандартний (~0.9 А)   ·   1.5 А   ·   3 А (= 15 Вт при 5 В)",
                 size=12, bold=True, fill="#eef4ff", stroke=NEG, sw=1.6, pad=12)
    p.append(lv[0])
    p.append(text(W / 2, 286, "більше за 15 Вт — потрібен PD", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "usbc-base.svg"), W, H, *p,
           title="Базовий USB-C: два резистори CC задають дозволений струм")


# ── pd-ladder: профілі PD ─────────────────────────────────────────────────────
# Ідея: три родини профілів — фіксовані щаблі SPR, плавний PPS, високовольтний
# EPR; усе по тій самій CC цифровими повідомленнями.

def fig_pd_ladder():
    W, H = 720, 330
    p = []
    ox, oy = 80, 280
    aw, ah = 580, 230
    # вісь напруги
    p.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.6))
    p.append(text(ox - 12, oy - ah + 4, "В", size=12, color=INK, bold=True, anchor="end"))
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))

    vmax = 52.0

    def vy(v):
        return oy - (v / vmax) * ah

    # фіксовані щаблі SPR
    spr = [5, 9, 15, 20]
    for v in spr:
        yy = vy(v)
        p.append(line(ox, yy, ox + 150, yy, color=NEG, sw=2.2))
        p.append(text(ox + 156, yy + 4, "%d В" % v, size=11, color=NEG, anchor="start", bold=True))
    p.append(text(ox + 75, vy(20) - 14, "SPR: фіксовані", size=11, color=NEG, bold=True))
    p.append(text(ox + 75, vy(20) - 0, "до 100 Вт", size=10, color=MUTED))

    # PPS — плавна смуга 3.3..21 В
    px0 = ox + 250
    p.append(rect(px0, vy(21), 110, vy(3.3) - vy(21), fill="#eafaf0", stroke=FIELD, sw=1.6, rx=4))
    p.append(text(px0 + 55, vy(12), "PPS", size=12, color=FIELD, bold=True))
    p.append(text(px0 + 55, vy(12) + 16, "плавно", size=10, color=FIELD))
    p.append(text(px0 + 55, vy(12) + 30, "крок 20 мВ", size=9, color=MUTED))

    # EPR — високовольтні щаблі
    epr = [28, 36, 48]
    ex0 = ox + 420
    for v in epr:
        yy = vy(v)
        p.append(line(ex0, yy, ex0 + 130, yy, color=POS, sw=2.4))
        p.append(text(ex0 + 136, yy + 4, "%d В" % v, size=11, color=POS, anchor="start", bold=True))
    p.append(text(ex0 + 65, vy(48) - 14, "EPR: до 240 Вт", size=11, color=POS, bold=True))

    p.append(text(W / 2, H - 14,
                  "усе по тій самій лінії CC — цифровими повідомленнями",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "pd-ladder.svg"), W, H, *p,
           title="PD піднімає напругу на вимогу: SPR, PPS, EPR")


# ── decouple: живлення розв'язане з даними ────────────────────────────────────
# Ідея: один роз'єм, різні лінії роблять різне — переговори, потужність, дані,
# швидкі пари; ролі не плутаються, бо кожна на своїх контактах.

def fig_decouple():
    W, H = 700, 300
    p = []
    # роз'єм ліворуч
    cx, cy = 110, 150
    p.append(rect(cx - 44, cy - 70, 88, 140, fill="#eef0f3", stroke=INK, sw=1.8, rx=10))
    p.append(text(cx, cy - 80, "Type-C", size=12, color=INK, bold=True))

    rows = [
        ("CC1 / CC2", "переговори про живлення (резистори, PD)", NEG),
        ("VBUS / GND", "сама потужність — 5…48 В", POS),
        ("D+ / D−", "дані USB 2.0", INK),
        ("пари TX / RX", "швидкі дані й відео (alt-mode)", FIELD),
    ]
    ry = cy - 54
    for lab, desc, col in rows:
        p.append(line(cx + 44, ry, 300, ry, color=col, sw=2.0))
        b, bw, bh = textbox(390, ry, lab, size=11, bold=True, color=col,
                            fill=BG, stroke=col, sw=1.5, min_w=120)
        p.append(b)
        p.append(text(462, ry + 4, desc, size=10, color=MUTED, anchor="start"))
        ry += 36

    p.append(text(W / 2, H - 16,
                  "живлення домовляється окремо від даних — одна роль не заважає іншій",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "decouple.svg"), W, H, *p,
           title="Один роз'єм, різні лінії: живлення розв'язане з даними")


# ── howmuch: три способи спитати «скільки можу взяти?» ─────────────────────────
# Ідея: розгалуження за типом порту → три різні механізми визначення струму.

def fig_howmuch():
    W, H = 720, 320
    p = []
    # питання вгорі
    q, qw, qh = textbox(W / 2, 56, "Скільки струму можу безпечно взяти?",
                        size=14, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=12)
    p.append(q)

    branches = [
        (150, "Type-A / micro", "угода BC 1.2", "тип порту по D+/D−\n(до 1.5 А)", "#eef4ff", NEG),
        (W / 2, "Type-C без PD", "резистори CC", "5 В · 1.5 / 3 А", "#eafaf0", FIELD),
        (W - 150, "Type-C із PD", "переговори протоколом", "9 / 15 / 20 / 48 В\n(до 240 Вт)", "#fdecea", POS),
    ]
    top_y = 56 + qh / 2
    for bx, port, how, res, fill, col in branches:
        # лінія від питання до гілки
        p.append(line(W / 2, top_y, bx, 130, color=INK, sw=1.4))
        p.append(text(bx, 150, port, size=13, color=col, bold=True))
        b, bw, bh = textbox(bx, 200, how, size=12, bold=True, color=col, fill=fill, stroke=col, sw=1.6, min_w=150)
        p.append(b)
        p.append(mtext(bx, 250, res, size=11, color=INK))

    p.append(text(W / 2, H - 14,
                  "три порти — три способи спитати; ця тема лише показує, куди дивитись",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "howmuch.svg"), W, H, *p,
           title="«Скільки можу взяти?» — три відповіді залежно від порту")


# ══ фігури для вставки hist-one-charger ═══════════════════════════════════════

# ── timeline: п'ятнадцять років до «одного дроту» ─────────────────────────────
# Ідея: горизонтальна вісь часу з віхами; зелене — крок індустрії, червоне —
# коли довелося примусити законом.

def fig_timeline():
    W, H = 740, 300
    p = []
    ax0, ax1, ay = 60, 680, 150
    p.append(line(ax0, ay, ax1, ay, color=INK, sw=2.0))
    p.append(arrow(ax1 - 4, ay, ax1 + 6, ay, color=INK, sw=2.0))

    # (рік, підпис, зверху?, це закон?)
    marks = [
        (2007, "USB BC 1.0:\nбільший струм", True, False),
        (2009, "меморандум ЄС:\nmicroUSB", False, False),
        (2014, "USB-C\nнароджується", True, False),
        (2022, "директива ЄС\n2022/2380", False, True),
        (2023, "iPhone 15:\nостанній здався", True, True),
    ]
    span = 2023 - 2007 + 1.5
    for yr, lab, top, law in marks:
        x = ax0 + (yr - 2007 + 0.5) / span * (ax1 - ax0)
        col = POS if law else FIELD
        p.append(circle(x, ay, 6, fill=col, stroke=INK, sw=1.4))
        p.append(text(x, ay + 24 if not top else ay - 44, str(yr), size=12, color=INK, bold=True))
        ly = ay - 30 if top else ay + 40
        p.append(mtext(x, ly, lab, size=10, color=col, bold=True))

    # легенда
    p.append(circle(ax0 + 14, H - 40, 6, fill=FIELD, stroke=INK, sw=1.2))
    p.append(text(ax0 + 26, H - 36, "крок індустрії", size=11, color=FIELD, anchor="start", bold=True))
    p.append(circle(ax0 + 180, H - 40, 6, fill=POS, stroke=INK, sw=1.2))
    p.append(text(ax0 + 192, H - 36, "довелося примусити законом", size=11, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="П'ятнадцять років до «одного дроту»")


# ── zoo: зоопарк роз'ємів зводиться до одного ─────────────────────────────────
# Ідея: ліворуч купа різних штекерів, праворуч — один USB-C; стрілка «тиск
# індустрії, законів, екології» зводить багато до одного.

def fig_zoo():
    W, H = 720, 300
    p = []
    # ліворуч — зоопарк
    zoo = ["barrel\n(бочка)", "Nokia\nтонкий", "Apple\n30-pin", "mini-USB", "micro-USB", "інші…"]
    zx, zy = 70, 70
    bw, bh = 110, 46
    for i, lab in enumerate(zoo):
        col = i % 2
        row = i // 2
        x = zx + col * (bw + 14)
        y = zy + row * (bh + 14)
        p.append(fitbox(x, y, bw, bh, lab, size=10, fill="#f1eef5", stroke=MUTED, sw=1.3, color=INK))
    p.append(text(zx + bw + 7, zy - 16, "десятки несумісних", size=12, color=MUTED, bold=True))

    # стрілка зведення
    midx = 380
    p.append(arrow(midx, H / 2, midx + 110, H / 2, color=POS, sw=2.2))
    p.append(mtext(midx + 55, H / 2 - 26, "тиск індустрії,\nзаконів, екології", size=10, color=POS, bold=True))

    # праворуч — один
    ox, oy = 560, H / 2
    b, ww, hh = textbox(ox, oy, "USB-C", size=18, bold=True, fill="#dff0df", stroke=FIELD, sw=2.2, pad=22)
    p.append(b)
    p.append(text(ox, oy + 56, "один дріт на все", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, "zoo.svg"), W, H, *p,
           title="Від зоопарку штекерів до одного роз'єму")


if __name__ == "__main__":
    fig_ladder()
    fig_connectors()
    fig_usbc_base()
    fig_pd_ladder()
    fig_decouple()
    fig_howmuch()
    fig_timeline()
    fig_zoo()
    print("OK: figures written to", OUT)
