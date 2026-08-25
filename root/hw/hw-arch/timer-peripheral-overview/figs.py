# -*- coding: utf-8 -*-
"""Фігури до статті «Таймери»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── 1. Будова таймера: ланцюг лічби і три способи під'єднати її до світу ──────
def fig_anatomy():
    W, H = 1040, 520
    f = []

    # Ланцюг: джерело такту → передільник → лічильник
    b, w1, h1 = textbox(120, 120, "Джерело такту\n80 МГц", size=14)
    f.append(b)
    b, w2, h2 = textbox(330, 120, "Передільник\n÷ 80", size=14)
    f.append(b)
    b, w3, h3 = textbox(560, 120, "Лічильник\n0 → 999", size=14, fill="#eef7f0", stroke=FIELD, sw=2)
    f.append(b)

    f.append(arrow(120 + w1 / 2 + 8, 120, 330 - w2 / 2 - 8, 120))
    f.append(arrow(330 + w2 / 2 + 8, 120, 560 - w3 / 2 - 8, 120))
    f.append(text(445, 172, "тік = 1 мкс", size=13, color=MUTED))

    # Три виходи лічби
    bx, bw = 700, 320
    rows = [
        (95, "ПЕРЕПОВНЕННЯ", "дорахував до межі →\nперериванням б'є період"),
        (235, "ПОРІВНЯННЯ", "лічильник дійшов до C →\nзалізо саме діє на ніжці"),
        (375, "ЗАХОПЛЕННЯ", "подія на ніжці →\nмиттєвий знімок лічби"),
    ]
    for i, (ty, cap, body) in enumerate(rows):
        f.append(rect(bx, ty, bw, 92, fill="#f9fafb"))
        f.append(text(bx + bw / 2, ty + 26, cap, size=13, bold=True, color=NEG))
        f.append(mtext(bx + bw / 2, ty + 50, body, size=12.5, color=INK))
        f.append(arrow(560 + w3 / 2 + 8, 120 + i * 8, bx - 10, ty + 46))

    # Процесор осторонь
    b, w4, h4 = textbox(560, 430, "Процесор\nвиконує свій код", size=14, fill="#fdf1ef", stroke=POS)
    f.append(b)
    f.append(line(560, 430 - h4 / 2 - 6, 560, 120 + h3 / 2 + 6, color=MUTED, sw=1.6, dash="6 6"))
    f.append(mtext(585, 285, "лічба йде\nсама, без\nучасті коду", size=12.5,
                   color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'timer-anatomy.svg'), W, H, *f,
           title="Таймер: одна лічба тактів — три способи зачепити її за світ")


# ── 2. Пилка лічильника: переповнення дає період, порівняння — шпаруватість ───
def fig_ramp():
    W, H = 1000, 500
    x0, x1 = 110, 800
    yb, yt = 280, 100          # низ і верх пилки
    per = (x1 - x0) / 3.0
    duty = 0.30
    ycmp = yb - duty * (yb - yt)
    f = []

    # осі
    f.append(line(x0, yb, x1 + 20, yb, sw=1.6))
    f.append(line(x0, yb + 6, x0, yt - 10, sw=1.6))
    f.append(text(105, 88, "лічильник", size=12, color=MUTED, anchor="end"))
    f.append(text(105, 116, "999", size=12, color=MUTED, anchor="end"))
    f.append(text(105, 286, "0", size=12, color=MUTED, anchor="end"))
    f.append(text(x1 + 18, 304, "час →", size=12, color=MUTED, anchor="end"))

    # пилка
    for k in range(3):
        xa = x0 + k * per
        f.append(line(xa, yb, xa + per, yt, color=NEG, sw=2.4))
        f.append(line(xa + per, yt, xa + per, yb, color=NEG, sw=2.4))

    # рівень порівняння
    f.append(line(x0, ycmp, x1, ycmp, color=POS, sw=1.8, dash="7 5"))
    f.append(mtext(x1 + 15, ycmp - 8, "поріг\nC = 300", size=12, color=POS, anchor="start"))

    # хвиля на ніжці
    yh, yl = 350, 405
    for k in range(3):
        xa = x0 + k * per
        xc = xa + duty * per
        f.append(line(xa, yh, xc, yh, color=FIELD, sw=2.4))
        f.append(line(xc, yh, xc, yl, color=FIELD, sw=2.4))
        f.append(line(xc, yl, xa + per, yl, color=FIELD, sw=2.4))
        f.append(line(xa + per, yl, xa + per, yh, color=FIELD, sw=2.4))
    f.append(mtext(x1 + 15, yh + 12, "ніжка:\nвисока\n30 % часу", size=12,
                   color=FIELD, anchor="start"))

    # тонкі провідні лінії від зламів пилки вниз до хвилі
    for k in range(1, 3):
        xa = x0 + k * per
        f.append(line(xa, yt, xa, yl + 14, color="#c9ced6", sw=1.1, dash="4 5"))

    # мірка періоду
    ym = 445
    xa, xc = x0 + per, x0 + 2 * per
    f.append(line(xa, ym - 7, xa, ym + 7, color=MUTED, sw=1.6))
    f.append(line(xc, ym - 7, xc, ym + 7, color=MUTED, sw=1.6))
    f.append(line(xa, ym, xc, ym, color=MUTED, sw=1.6))
    f.append(text((xa + xc) / 2, ym + 28, "період = 1000 тіків = 1 мс", size=12.5, color=MUTED))

    render(os.path.join(IMG, 'counter-ramp.svg'), W, H, *f,
           title="Лічильник біжить по колу: межа задає період, поріг — частку часу")


# ── 3. Вставка hist: таймер на платі проти таймера на кристалі ────────────────
def fig_onchip_move():
    W, H = 1180, 640
    f = []

    # ── Ліва панель: окремий корпус на платі ─────────────────────────────────
    f.append(rect(40, 62, 520, 520, fill="#ffffff", stroke="#d5d9df", sw=1.4, rx=10))
    f.append(text(300, 100, "Таймер — окрема мікросхема", size=15, bold=True, color=POS))

    f.append(rect(78, 126, 444, 268, fill="#f9fafb", stroke="#c9ced6", sw=1.4))
    f.append(text(300, 152, "друкована плата", size=12, color=MUTED))

    b, wc, hc = textbox(178, 208, "Процесор\n8080", size=13)
    f.append(b)
    b, wt, ht = textbox(420, 208, "8253\n3 × 16 біт", size=13,
                        fill="#fdf1ef", stroke=POS, sw=2)
    f.append(b)

    ybus = 292
    f.append(line(178, 208 + hc / 2 + 4, 178, ybus, color=LINE, sw=1.6))
    f.append(line(420, 208 + ht / 2 + 4, 420, ybus, color=LINE, sw=1.6))
    f.append(line(120, ybus, 480, ybus, color=LINE, sw=2.2))
    f.append(text(300, ybus + 22, "шина: адреси · дані · читання/запис", size=12, color=MUTED))

    b, wd, hd = textbox(300, 350, "дешифратор адрес", size=12, fill="#f4f6f8")
    f.append(b)
    f.append(line(300, ybus + 32, 300, 350 - hd / 2 - 4, color=MUTED, sw=1.4, dash="5 4"))

    f.append(mtext(78, 442, [
        "ще один таймер = ще одна мікросхема",
        "своє вікно в адресному просторі",
        "сокет, доріжки, рядок у переліку деталей",
        "вибір застиг у міді ще до першого рядка коду",
    ], size=12.5, color=INK, anchor="start", lh=1.55))

    # ── Права панель: той самий лічильник на кристалі ────────────────────────
    f.append(rect(620, 62, 520, 520, fill="#ffffff", stroke="#d5d9df", sw=1.4, rx=10))
    f.append(text(880, 100, "Таймер — вузол на кристалі", size=15, bold=True, color=FIELD))

    f.append(rect(658, 126, 444, 268, fill="#eef7f0", stroke=FIELD, sw=2))
    f.append(text(880, 152, "кристал мікроконтролера (8048)", size=12, color=MUTED))

    cells = [("ядро", False), ("ПЗП", False), ("ОЗП", False),
             ("порти", False), ("таймер", True)]
    widths = [text_width(s, 12, bold) + 18 for s, bold in cells]
    gap = (444 - 40 - sum(widths)) / (len(cells) - 1)
    cx = 658 + 20
    centers = []
    for (s, bold), wcell in zip(cells, widths):
        c = cx + wcell / 2
        centers.append(c)
        fill = "#d8efdf" if bold else "#ffffff"
        stroke = FIELD if bold else LINE
        b, _, hcell = textbox(c, 206, s, size=12, pad=9, fill=fill,
                              stroke=stroke, sw=2 if bold else 1.4, bold=bold)
        f.append(b)
        cx += wcell + gap

    yib = 288
    for c in centers:
        f.append(line(c, 206 + 17, c, yib, color=LINE, sw=1.4))
    f.append(line(centers[0] - 14, yib, centers[-1] + 14, yib, color=LINE, sw=2.2))
    f.append(text(880, yib + 22, "внутрішня шина периферії", size=12, color=MUTED))
    f.append(text(880, yib + 62, "таймер — просто ще один вузол на ній", size=12.5, color=FIELD))

    f.append(mtext(658, 442, [
        "ще один таймер = ще кут кремнію",
        "адреса вже своя, дешифрувати нічого",
        "нічого купувати й нічого паяти",
        "вибір за кодом і оборотний перезбіркою",
    ], size=12.5, color=INK, anchor="start", lh=1.55))

    render(os.path.join(IMG, 'onchip-move.svg'), W, H, *f,
           title="Той самий лічильник, дві адреси проживання")


# ── 4. Скільки незалежних таймерів дістає система, коли міняється їхня ціна ───
def fig_timer_count():
    W, H = 1020, 600
    f = []
    base, top = 452, 118
    scale = (base - top) / 17.0

    data = [
        ("Intel 8048", "1976", 1, "один 8-бітний"),
        ("Intel 8051", "1980", 2, "два 16-бітні"),
        ("ATmega328P", "2000-ні", 3, "два 8- + один 16-біт"),
        ("STM32F407", "2010-ті", 17, "до 17 разом"),
    ]
    xs = [160, 400, 640, 880]
    bw = 128

    f.append(line(80, base, 950, base, color=LINE, sw=1.8))

    for (name, year, n, note), xc in zip(data, xs):
        h = n * scale
        f.append(rect(xc - bw / 2, base - h, bw, h, fill="#eef7f0", stroke=FIELD, sw=2, rx=4))
        f.append(text(xc, base - h - 16, str(n), size=17, bold=True, color=FIELD))
        f.append(mtext(xc, base + 26, [name, year], size=13, color=INK, lh=1.4))
        f.append(text(xc, base + 78, note, size=11.5, color=MUTED))

    f.append(text(510, 546, "таймерів на одному кристалі — за роками",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'timer-count.svg'), W, H, *f,
           title="Коли таймер перестав коштувати корпус, їх стало багато")


# ── 5. IBM PC 1981: обидві відповіді в одному ящику ───────────────────────────
def fig_two_eras():
    W, H = 1060, 470
    f = []

    f.append(rect(50, 78, 520, 268, fill="#f9fafb", stroke="#c9ced6", sw=1.5, rx=8))
    f.append(text(310, 108, "системна плата", size=13, bold=True, color=MUTED))

    b, w1, h1 = textbox(180, 176, "8088\nпроцесор", size=13)
    f.append(b)
    b, w2, h2 = textbox(430, 176, "8253\nтаймер", size=13, fill="#fdf1ef", stroke=POS, sw=2)
    f.append(b)
    f.append(line(180 + w1 / 2 + 6, 176, 430 - w2 / 2 - 6, 176, color=LINE, sw=1.8))
    f.append(text(305, 158, "шина", size=11.5, color=MUTED))
    f.append(mtext(310, 254, ["окремий корпус поряд із процесором:",
                              "18.2 переривання на секунду · регенерація пам'яті · динамік"],
                   size=12, color=INK, lh=1.4))

    f.append(rect(660, 78, 350, 268, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(835, 108, "клавіатура", size=13, bold=True, color=MUTED))

    b, w3, h3 = textbox(835, 178, "8048", size=14, fill="#ffffff", stroke=LINE, sw=1.5, min_w=190)
    f.append(b)
    b, w4, h4 = textbox(835, 232, "таймер усередині", size=12,
                        fill="#d8efdf", stroke=FIELD, sw=2)
    f.append(b)
    f.append(text(835, 300, "цілий комп'ютер в одному корпусі", size=12, color=INK))

    f.append(line(570, 212, 660, 212, color=LINE, sw=2))
    f.append(text(615, 198, "кабель", size=11.5, color=MUTED))

    f.append(text(530, 400, "одна коробка 1981 року — і поруч у ній обидві відповіді на те саме питання",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'two-eras.svg'), W, H, *f,
           title="IBM PC: таймер на платі й таймер на кристалі одночасно")


# ── 6. Вставка proj: шлях налаштування від такту шини до двох споживачів ──────
def fig_setup_path():
    W, H = 1160, 600
    f = []

    # Верх: звідки береться такт таймера (пастка ×2)
    b, wa, ha = textbox(140, 70, "PCLK1 = 42 МГц", size=13)
    f.append(b)
    b, wb, hb = textbox(400, 70, "×2, бо подільник APB1 ≠ 1", size=13,
                        fill="#fdecea", stroke=POS)
    f.append(b)
    b, wc, hc = textbox(660, 70, "TIMCLK = 84 МГц", size=13,
                        fill="#eef7f0", stroke=FIELD)
    f.append(b)
    f.append(arrow(140 + wa / 2 + 8, 70, 400 - wb / 2 - 8, 70))
    f.append(arrow(400 + wb / 2 + 8, 70, 660 - wc / 2 - 8, 70))
    f.append(text(400, 122, "на шині 42 МГц, а в таймері вже 84", size=12.5, color=MUTED))

    # Спуск від TIMCLK до вентиля тактування
    f.append(line(660, 70 + hc / 2, 660, 165, color=LINE, sw=1.6))
    f.append(line(660, 165, 150, 165, color=LINE, sw=1.6))

    # Головний ланцюг лічби
    b, wg, hg = textbox(150, 230, "Вентиль такту\nAPB1ENR.TIM3EN", size=13)
    f.append(b)
    f.append(arrow(150, 165, 150, 230 - hg / 2 - 8))
    b, wp, hp = textbox(390, 230, "PSC = 83\n(÷ 84)", size=13, min_w=110)
    f.append(b)
    b, wn, hn = textbox(620, 230, "CNT\n0 … 999", size=13, min_w=115,
                        fill="#eef7f0", stroke=FIELD, sw=2)
    f.append(b)
    f.append(arrow(150 + wg / 2 + 8, 230, 390 - wp / 2 - 8, 230))
    f.append(arrow(390 + wp / 2 + 8, 230, 620 - wn / 2 - 8, 230))
    f.append(text((150 + wg / 2 + 390 - wp / 2) / 2, 214, "84 МГц", size=12.5, color=MUTED))
    f.append(text((390 + wp / 2 + 620 - wn / 2) / 2, 214, "тік = 1 мкс", size=12.5, color=MUTED))

    # Вимикач лічби
    b, wk, hk = textbox(620, 335, "CR1.CEN = 1", size=13)
    f.append(b)
    f.append(line(620, 335 - hk / 2 - 6, 620, 230 + hn / 2 + 6,
                  color=MUTED, sw=1.6, dash="6 6"))
    f.append(text(620, 382, "поки не ввімкнено — CNT стоїть", size=12.5, color=MUTED))

    # Дві гілки-споживачі
    PX, PW = 790, 330
    f.append(text(PX + PW / 2, 88, "ГІЛКА ПЕРЕПОВНЕННЯ", size=13, bold=True, color=NEG))
    f.append(fitbox(PX, 100, PW, 46, "CNT дійшов до ARR = 999", size=13))
    f.append(fitbox(PX, 166, PW, 62, "подія оновлення: CNT := 0,\nтіні перезаписано", size=13))
    f.append(fitbox(PX, 248, PW, 62, "SR.UIF := 1 → NVIC →\nTIM3_IRQHandler()", size=13))
    f.append(arrow(PX + PW / 2, 146, PX + PW / 2, 164))
    f.append(arrow(PX + PW / 2, 228, PX + PW / 2, 246))

    f.append(text(PX + PW / 2, 372, "ГІЛКА ПОРІВНЯННЯ", size=13, bold=True, color=FIELD))
    f.append(fitbox(PX, 384, PW, 46, "CNT дійшов до CCR1 = 250", size=13))
    f.append(fitbox(PX, 450, PW, 62, "канал сам змінює рівень\nна ніжці — код не потрібен", size=13))
    f.append(arrow(PX + PW / 2, 430, PX + PW / 2, 448))

    f.append(arrow(620 + wn / 2 + 8, 222, PX - 8, 130))
    f.append(arrow(620 + wn / 2 + 8, 240, PX - 8, 400))

    render(os.path.join(IMG, 'timer-setup-path.svg'), W, H, *f,
           title="Налаштування таймера: кілька записів у регістри вибудовують один ланцюг")


# ── 7. Вставка proj: тіньові регістри й мить, коли нова межа набуває чинності ─
def fig_preload():
    W, H = 1080, 660
    f = []
    x0 = 110
    per = 160.0          # ширина періоду з ARR = 999
    half = per / 2.0     # з ARR = 499 період удвічі коротший
    xw = x0 + 2 * per - 48   # мить запису нового ARR (усередині другого періоду)

    def axes(yb, yt, title, color):
        g = [text(x0 - 8, yt - 62, title, size=13.5, bold=True, color=color, anchor="start"),
             line(x0, yb, 960, yb, sw=1.6),
             line(x0, yb + 6, x0, yt - 26, sw=1.6),
             text(x0 - 12, yt + 5, "999", size=12, color=MUTED, anchor="end"),
             text(x0 - 12, yb + 4, "0", size=12, color=MUTED, anchor="end")]
        return g

    # ── Панель 1: ARPE = 1, зміна чекає межі періоду ──
    yb1, yt1 = 250, 120
    y499_1 = yb1 - 0.5 * (yb1 - yt1)
    f += axes(yb1, yt1, "ARPE = 1 — нове ARR чекає кінця періоду", FIELD)
    f.append(text(x0 - 12, y499_1 + 5, "499", size=12, color=MUTED, anchor="end"))
    f.append(line(x0, y499_1, 676, y499_1, color=FIELD, sw=1.5, dash="7 5"))

    for k in range(2):                      # два повні періоди по 999
        xa = x0 + k * per
        f.append(line(xa, yb1, xa + per, yt1, color=NEG, sw=2.4))
        f.append(line(xa + per, yt1, xa + per, yb1, color=NEG, sw=2.4))
    for k in range(3):                      # далі періоди по 499
        xa = x0 + 2 * per + k * half
        f.append(line(xa, yb1, xa + half, y499_1, color=NEG, sw=2.4))
        f.append(line(xa + half, y499_1, xa + half, yb1, color=NEG, sw=2.4))

    yhit1 = yb1 - 0.7 * (yb1 - yt1)
    f.append(line(xw, yb1 + 14, xw, yt1 - 18, color=POS, sw=1.6, dash="5 4"))
    f.append(circle(xw, yhit1, 5, fill=POS, stroke=POS))
    f.append(text(xw, yt1 - 26, "запис ARR = 499 (CNT = 700)", size=12.5, color=POS))
    f.append(mtext(x0 + 2 * per + 3 * half + 34, y499_1 - 6,
                   "нова межа діє\nз наступного\nперіоду", size=12.5,
                   color=FIELD, anchor="start"))

    # ── Панель 2: ARPE = 0, запис іде просто в активний регістр ──
    yb2, yt2 = 545, 430
    y499_2 = yb2 - 0.5 * (yb2 - yt2)
    f += axes(yb2, yt2, "ARPE = 0 — нове ARR діє негайно, а лічильник його вже проскочив", POS)
    f.append(text(x0 - 12, y499_2 + 5, "499", size=12, color=MUTED, anchor="end"))
    f.append(line(x0, y499_2, 900, y499_2, color=FIELD, sw=1.5, dash="7 5"))

    slope = (yb2 - yt2) / per
    yhit2 = yb2 - 0.7 * (yb2 - yt2)
    f.append(line(x0, yb2, x0 + per, yt2, color=NEG, sw=2.4))
    f.append(line(x0 + per, yt2, x0 + per, yb2, color=NEG, sw=2.4))
    f.append(line(x0 + per, yb2, xw, yhit2, color=NEG, sw=2.4))
    f.append(line(xw, yhit2, x0 + 2 * per, yt2, color=NEG, sw=2.4))
    f.append(arrow(x0 + 2 * per, yt2, x0 + 2 * per + 66, yt2 - 66 * slope, color=NEG, sw=2.4))
    f.append(line(xw, yb2 + 14, xw, yt2 - 18, color=POS, sw=1.6, dash="5 4"))
    f.append(circle(xw, yhit2, 5, fill=POS, stroke=POS))
    f.append(text(xw, yt2 - 26, "той самий запис ARR = 499", size=12.5, color=POS))

    f.append(fitbox(530, 356, 430, 58,
                    "CNT = 700 вже за межею 499 —\nзбігу не буде: лічба йде до 65535",
                    size=13, fill="#fdecea", stroke=POS, color=POS))
    f.append(text(535, 606, "один період розтягнувся до ≈65 мс замість 0.5 мс",
                  size=12.5, color=POS))

    render(os.path.join(IMG, 'timer-preload.svg'), W, H, *f,
           title="Тіньові регістри: чому нову межу переносять на кінець періоду")


# ── 8. Вставка proj: час, склеєний із двох чисел, і щілина між читаннями ──────
def fig_atomic_read():
    W, H = 1000, 440
    f = []
    x0, per = 110, 220.0
    yb, yt = 240, 150
    xwrap = x0 + per
    t1, t2 = xwrap - 62, xwrap + 62

    f.append(line(x0, yb, 830, yb, sw=1.6))
    f.append(text(825, yb + 24, "час →", size=12, color=MUTED, anchor="end"))
    for k in range(3):
        xa = x0 + k * per
        f.append(line(xa, yb, xa + per, yt, color=NEG, sw=2.4))
        f.append(line(xa + per, yt, xa + per, yb, color=NEG, sw=2.4))
    f.append(text(x0 - 12, yt + 5, "999", size=12, color=MUTED, anchor="end"))
    f.append(text(x0 - 12, yb + 4, "0", size=12, color=MUTED, anchor="end"))
    f.append(text(x0 - 26, 132, "CNT", size=12.5, color=MUTED, anchor="start"))

    f.append(line(xwrap, yt - 30, xwrap, yb + 12, color=POS, sw=1.8, dash="5 4"))
    f.append(text(xwrap, 82, "перескок: CNT → 0, а hi ще НЕ збільшено", size=12.5, color=POS))

    for x, cap in ((t1, "1) hi = 7"), (t2, "2) CNT = 3")):
        f.append(line(x, yt - 8, x, yb + 12, color=MUTED, sw=1.4, dash="4 4"))
        f.append(text(x, 118, cap, size=12.5, color=INK, bold=True))

    f.append(fitbox(140, 288, 330, 48, "код порахував 7 × 1000 + 3 = 7003 мкс", size=13))
    f.append(fitbox(530, 288, 330, 48, "насправді 8003 мкс: час стрибнув назад",
                    size=13, fill="#fdecea", stroke=POS, color=POS))
    f.append(fitbox(140, 358, 720, 48,
                    "лік: перечитати hi та зазирнути в UIF — прапорець зізнається, що перескок уже стався",
                    size=13, fill="#eef7f0", stroke=FIELD))

    render(os.path.join(IMG, 'timer-atomic-read.svg'), W, H, *f,
           title="Час зі старшої та молодшої половин: щілина між двома читаннями")


fig_anatomy()
fig_ramp()
fig_onchip_move()
fig_timer_count()
fig_two_eras()
fig_setup_path()
fig_preload()
fig_atomic_read()
print("ok")
