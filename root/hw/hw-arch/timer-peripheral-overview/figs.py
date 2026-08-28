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


# ── 9. Поглиблена функціональна структура апаратного таймера ─────────────────
def fig_core_block():
    W, H = 1180, 680
    f = []

    # Рамка ядра таймера
    f.append(rect(40, 50, 1100, 600, fill="#ffffff", stroke="#c9ced6", sw=1.5, rx=10))

    # Секція 1: Селектор такту
    f.append(rect(60, 80, 240, 220, fill="#f8fafc", stroke=MUTED, sw=1.4))
    f.append(text(180, 108, "Тактовий блок", size=13, bold=True, color=INK))
    f.append(fitbox(75, 126, 210, 36, "Внутрішній такт (CK_INT)", size=11.5))
    f.append(fitbox(75, 168, 210, 36, "Зовнішній ETR / TI1, TI2", size=11.5))
    f.append(fitbox(75, 210, 210, 36, "Тригери ITR0..ITR3 (Майстер)", size=11.5))
    f.append(fitbox(75, 252, 210, 36, "Селектор (SMCR / CKD)", size=11.5, fill="#eef7f0", stroke=FIELD))

    # Стрілка від такту до передподільника
    f.append(arrow(300, 270, 350, 270))
    f.append(text(325, 258, "CK_PSC", size=11, color=MUTED))

    # Секція 2: База часу (Time Base Unit)
    f.append(rect(350, 80, 420, 340, fill="#f9fafb", stroke=FIELD, sw=2))
    f.append(text(560, 108, "База часу (Time-Base Unit)", size=14, bold=True, color=FIELD))

    # PSC та його тінь
    f.append(rect(370, 130, 380, 72, fill="#ffffff", stroke=MUTED, sw=1.2))
    f.append(text(560, 150, "Регістр передподільника (PSC)", size=12.5, bold=True))
    f.append(fitbox(385, 162, 350, 30, "Тіньовий дільник PSC (÷ 1..65536)", size=11.5, fill="#d8efdf", stroke=FIELD))

    # CNT
    f.append(rect(370, 218, 380, 68, fill="#eef7f0", stroke=FIELD, sw=1.8))
    f.append(text(560, 240, "Головний лічильник (CNT 16 / 32-біт)", size=13, bold=True, color=FIELD))
    f.append(text(560, 268, "Режими: Прямий (Up) · Зворотний (Down) · Центрований", size=11, color=MUTED))

    # ARR та його тінь
    f.append(rect(370, 300, 380, 104, fill="#ffffff", stroke=MUTED, sw=1.2))
    f.append(text(560, 320, "Регістр автоперезавантаження (ARR)", size=12.5, bold=True))
    f.append(fitbox(385, 332, 350, 30, "Тіньовий регістр ARR (Auto-reload shadow)", size=11.5, fill="#d8efdf", stroke=FIELD))
    f.append(text(560, 386, "Буферизація: біт ARPE (Auto-reload preload enable)", size=11, color=MUTED))

    # Зв'язки всередині Time Base Unit
    f.append(arrow(560, 202, 560, 218))
    f.append(text(595, 210, "CK_CNT", size=11, color=MUTED))
    f.append(arrow(560, 286, 560, 300))

    # Секція 3: Генерація подій оновлення (Update Event - UEV)
    f.append(rect(810, 80, 310, 180, fill="#fdf1ef", stroke=POS, sw=1.5))
    f.append(text(965, 108, "Генератор подій оновлення (UEV)", size=13, bold=True, color=POS))
    f.append(fitbox(825, 126, 280, 38, "Переповнення / Спустошення CNT", size=11.5))
    f.append(fitbox(825, 170, 280, 38, "Програмна подія (EGR.UG)", size=11.5))
    f.append(fitbox(825, 214, 280, 36, "Оновлення тіньових PSC/ARR/CCR", size=11, fill="#ffffff", stroke=POS))

    # Стрілка від CNT/ARR до UEV
    f.append(arrow(750, 252, 810, 170))
    f.append(text(780, 200, "CNT == ARR", size=11, color=POS))

    # Секція 4: Канали захоплення/порівняння (Capture / Compare Channels)
    f.append(rect(60, 445, 1060, 185, fill="#f8fafc", stroke=NEG, sw=1.5))
    f.append(text(590, 470, "Канали захоплення / порівняння (Канали CH1 .. CH4)", size=13.5, bold=True, color=NEG))

    # Вхідний тракт (Input Capture)
    f.append(rect(80, 492, 450, 120, fill="#ffffff", stroke=MUTED, sw=1.2))
    f.append(text(305, 514, "Input Capture: вимірювання сигналів", size=12, bold=True, color=INK))
    f.append(fitbox(95, 530, 420, 32, "Пін TIx → Цифровий фільтр → Детектор фронтів", size=11))
    f.append(fitbox(95, 568, 420, 34, "Подія фронту копіює CNT → CCRx (мітка часу без латентності ядра)", size=11, fill="#eef7f0", stroke=FIELD))

    # Вихідний тракт (Output Compare & PWM)
    f.append(rect(580, 492, 520, 120, fill="#ffffff", stroke=MUTED, sw=1.2))
    f.append(text(840, 514, "Output Compare & PWM: генерація імпульсів", size=12, bold=True, color=INK))
    f.append(fitbox(595, 530, 490, 32, "Компаратор (CNT == CCRx) → Логіка комутації виходу", size=11))
    f.append(fitbox(595, 568, 490, 34, "ШІМ: PWM Mode 1/2 · Комплементарні виходи · Вставка Dead-Time", size=11, fill="#fdecea", stroke=POS))

    # Зв'язок CNT до каналів
    f.append(arrow(560, 420, 560, 445))
    f.append(text(510, 435, "шина лічильника CNT", size=11, color=MUTED))

    render(os.path.join(IMG, 'timer-core-block.svg'), W, H, *f,
           title="Архітектура апаратного таймера: ядро лічби, генерація подій і канали")


# ── 10. Режими рахунку та генерація ШІМ ───────────────────────────────────────
def fig_counting_modes_pwm():
    W, H = 1160, 680
    f = []

    # 3 панелі: Up-counting, Down-counting, Center-aligned
    # Панель 1: Up-counting (Edge-aligned)
    f.append(rect(40, 60, 345, 590, fill="#ffffff", stroke="#d5d9df", sw=1.4, rx=8))
    f.append(text(212, 90, "Прямий рахунок (Up-counting)", size=13, bold=True, color=NEG))
    f.append(text(212, 112, "Edge-aligned PWM (Mode 1)", size=11.5, color=MUTED))

    # Графік пилки Up
    x0_1, per_1 = 65, 85.0
    yb_1, yt_1 = 260, 150
    f.append(line(x0_1, yb_1, x0_1 + 3 * per_1 + 10, yb_1, sw=1.4))
    f.append(line(x0_1, yb_1 + 5, x0_1, yt_1 - 10, sw=1.4))
    f.append(text(x0_1 - 6, yt_1 + 4, "ARR", size=10.5, color=MUTED, anchor="end"))
    f.append(text(x0_1 - 6, yb_1 + 4, "0", size=10.5, color=MUTED, anchor="end"))

    y_ccr_1 = yb_1 - 0.6 * (yb_1 - yt_1)
    f.append(line(x0_1, y_ccr_1, x0_1 + 3 * per_1, y_ccr_1, color=POS, sw=1.2, dash="5 4"))
    f.append(text(x0_1 + 3 * per_1 + 5, y_ccr_1 + 4, "CCR", size=10.5, color=POS, anchor="start"))

    for k in range(3):
        xa = x0_1 + k * per_1
        f.append(line(xa, yb_1, xa + per_1, yt_1, color=NEG, sw=2.2))
        f.append(line(xa + per_1, yt_1, xa + per_1, yb_1, color=NEG, sw=2.2))
        # Подія UEV
        f.append(circle(xa + per_1, yt_1, 4, fill=POS, stroke=POS))

    # Вихідний сигнал ШІМ (PWM Mode 1: CNT < CCR -> High)
    yh_1, yl_1 = 320, 365
    f.append(text(55, yh_1 + 16, "OCx", size=11, bold=True, color=FIELD, anchor="end"))
    for k in range(3):
        xa = x0_1 + k * per_1
        xc = xa + 0.6 * per_1
        f.append(line(xa, yh_1, xc, yh_1, color=FIELD, sw=2.2))
        f.append(line(xc, yh_1, xc, yl_1, color=FIELD, sw=2.2))
        f.append(line(xc, yl_1, xa + per_1, yl_1, color=FIELD, sw=2.2))
        f.append(line(xa + per_1, yl_1, xa + per_1, yh_1, color=FIELD, sw=2.2))

    f.append(fitbox(55, 410, 315, 220, [
        "Особливості прямого рахунку:",
        "• Фронти вирівняні за початком періоду",
        "• UEV генерується при CNT == ARR",
        "• Спектр комутації: гармоніки на f_pwm",
        "• Односхила модуляція (крайовий ШІМ)",
        "• Застосування: світлодіоди, нагрівачі,",
        "  DC-двигуни, ЦАП через RC-фільтр"
    ], size=11.5, lh=1.45))

    # Панель 2: Down-counting
    f.append(rect(405, 60, 345, 590, fill="#ffffff", stroke="#d5d9df", sw=1.4, rx=8))
    f.append(text(577, 90, "Зворотний рахунок (Down-counting)", size=13, bold=True, color=NEG))
    f.append(text(577, 112, "Лічба ARR → 0", size=11.5, color=MUTED))

    # Графік пилки Down
    x0_2, per_2 = 430, 85.0
    yb_2, yt_2 = 260, 150
    f.append(line(x0_2, yb_2, x0_2 + 3 * per_2 + 10, yb_2, sw=1.4))
    f.append(line(x0_2, yb_2 + 5, x0_2, yt_2 - 10, sw=1.4))
    f.append(text(x0_2 - 6, yt_2 + 4, "ARR", size=10.5, color=MUTED, anchor="end"))
    f.append(text(x0_2 - 6, yb_2 + 4, "0", size=10.5, color=MUTED, anchor="end"))

    y_ccr_2 = yb_2 - 0.6 * (yb_2 - yt_2)
    f.append(line(x0_2, y_ccr_2, x0_2 + 3 * per_2, y_ccr_2, color=POS, sw=1.2, dash="5 4"))
    f.append(text(x0_2 + 3 * per_2 + 5, y_ccr_2 + 4, "CCR", size=10.5, color=POS, anchor="start"))

    for k in range(3):
        xa = x0_2 + k * per_2
        f.append(line(xa, yt_2, xa + per_2, yb_2, color=NEG, sw=2.2))
        f.append(line(xa + per_2, yb_2, xa + per_2, yt_2, color=NEG, sw=2.2))
        # Подія UEV при CNT == 0
        f.append(circle(xa + per_2, yb_2, 4, fill=POS, stroke=POS))

    # Вихідний сигнал ШІМ
    yh_2, yl_2 = 320, 365
    f.append(text(420, yh_2 + 16, "OCx", size=11, bold=True, color=FIELD, anchor="end"))
    for k in range(3):
        xa = x0_2 + k * per_2
        xc = xa + 0.4 * per_2
        f.append(line(xa, yl_2, xc, yl_2, color=FIELD, sw=2.2))
        f.append(line(xc, yl_2, xc, yh_2, color=FIELD, sw=2.2))
        f.append(line(xc, yh_2, xa + per_2, yh_2, color=FIELD, sw=2.2))
        f.append(line(xa + per_2, yh_2, xa + per_2, yl_2, color=FIELD, sw=2.2))

    f.append(fitbox(420, 410, 315, 220, [
        "Особливості зворотного рахунку:",
        "• Зворотна фаза заповнення сигналу",
        "• UEV генерується при спустошенні (0)",
        "• Завантаження CNT значенням ARR",
        "• Симетричний двійник прямого рахунку",
        "• Використовується в специфічних",
        "  протоколах генерації фазових затримок"
    ], size=11.5, lh=1.45))

    # Панель 3: Center-aligned (Up-Down)
    f.append(rect(770, 60, 350, 590, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(945, 90, "Центрований рахунок (Up-Down)", size=13, bold=True, color=FIELD))
    f.append(text(945, 112, "Center-aligned PWM (FOC / Інвертори)", size=11.5, color=MUTED))

    # Графік трикутника
    x0_3, per_3 = 795, 140.0
    yb_3, yt_3 = 260, 150
    f.append(line(x0_3, yb_3, x0_3 + 2 * per_3 + 10, yb_3, sw=1.4))
    f.append(line(x0_3, yb_3 + 5, x0_3, yt_3 - 10, sw=1.4))
    f.append(text(x0_3 - 6, yt_3 + 4, "ARR", size=10.5, color=MUTED, anchor="end"))
    f.append(text(x0_3 - 6, yb_3 + 4, "0", size=10.5, color=MUTED, anchor="end"))

    y_ccr_3 = yb_3 - 0.6 * (yb_3 - yt_3)
    f.append(line(x0_3, y_ccr_3, x0_3 + 2 * per_3, y_ccr_3, color=POS, sw=1.2, dash="5 4"))
    f.append(text(x0_3 + 2 * per_3 + 5, y_ccr_3 + 4, "CCR", size=10.5, color=POS, anchor="start"))

    for k in range(2):
        xa = x0_3 + k * per_3
        x_top = xa + per_3 / 2.0
        x_end = xa + per_3
        f.append(line(xa, yb_3, x_top, yt_3, color=FIELD, sw=2.2))
        f.append(line(x_top, yt_3, x_end, yb_3, color=FIELD, sw=2.2))
        # Точки переривань/оновлень на вершині та внизу
        f.append(circle(x_top, yt_3, 4, fill=POS, stroke=POS))
        f.append(circle(x_end, yb_3, 4, fill=POS, stroke=POS))

    # Вихідний сигнал ШІМ (симетричний відносно центру)
    yh_3, yl_3 = 320, 365
    f.append(text(785, yh_3 + 16, "OCx", size=11, bold=True, color=FIELD, anchor="end"))
    for k in range(2):
        xa = x0_3 + k * per_3
        x_rise = xa + 0.2 * per_3
        x_fall = xa + 0.8 * per_3
        f.append(line(xa, yl_3, x_rise, yl_3, color=FIELD, sw=2.2))
        f.append(line(x_rise, yl_3, x_rise, yh_3, color=FIELD, sw=2.2))
        f.append(line(x_rise, yh_3, x_fall, yh_3, color=FIELD, sw=2.2))
        f.append(line(x_fall, yh_3, x_fall, yl_3, color=FIELD, sw=2.2))
        f.append(line(x_fall, yl_3, xa + per_3, yl_3, color=FIELD, sw=2.2))
        # Осі симетрії
        f.append(line(xa + per_3 / 2.0, yt_3 - 6, xa + per_3 / 2.0, yl_3 + 12, color=MUTED, sw=1.1, dash="4 4"))

    f.append(fitbox(785, 410, 320, 220, [
        "Переваги центрованого ШІМ:",
        "• Імпульси ідеально симетричні щодо центру",
        "• Частота гармонік комутації в струмі = 2×f_pwm",
        "• Значно менші акустичний шум та пульсації",
        "• Безпечна вибірка струму АЦП (TRGO на вершині)",
        "  подалі від шумів перемикання транзисторів",
        "• Стандарт для FOC/BLDC моторних приводів"
    ], size=11.5, lh=1.45))

    render(os.path.join(IMG, 'counting-modes-pwm.svg'), W, H, *f,
           title="Режими лічби: прямий, зворотний та симетричний центрований ШІМ")


# ── 11. Комплементарні виходи та формування мертвого часу (Dead-Time) ─────────
def fig_dead_time():
    W, H = 1100, 560
    f = []

    # Часова вісь
    x0, x1 = 120, 960
    f.append(line(x0, 480, x1 + 40, 480, sw=1.5))
    f.append(text(x1 + 40, 502, "час →", size=12, color=MUTED, anchor="end"))

    # Сигнал 1: OCxREF (базовий внутрішній сигнал порівняння)
    y1_h, y1_l = 100, 150
    f.append(text(x0 - 15, y1_h + 26, "OCxREF\n(внутрішній)", size=12, bold=True, color=INK, anchor="end"))
    f.append(line(x0, y1_l, 280, y1_l, color=LINE, sw=2))
    f.append(line(280, y1_l, 280, y1_h, color=LINE, sw=2))
    f.append(line(280, y1_h, 620, y1_h, color=LINE, sw=2))
    f.append(line(620, y1_h, 620, y1_l, color=LINE, sw=2))
    f.append(line(620, y1_l, x1, y1_l, color=LINE, sw=2))

    # Сигнал 2: CHx (Верхній ключ, High-Side MOSFET)
    y2_h, y2_l = 210, 260
    f.append(text(x0 - 15, y2_h + 26, "CHx\n(High-Side)", size=12, bold=True, color=FIELD, anchor="end"))
    f.append(line(x0, y2_l, 350, y2_l, color=FIELD, sw=2.4))
    f.append(line(350, y2_l, 350, y2_h, color=FIELD, sw=2.4))
    f.append(line(350, y2_h, 620, y2_h, color=FIELD, sw=2.4))
    f.append(line(620, y2_h, 620, y2_l, color=FIELD, sw=2.4))
    f.append(line(620, y2_l, x1, y2_l, color=FIELD, sw=2.4))

    # Сигнал 3: CHxN (Нижній ключ, Low-Side MOSFET)
    y3_h, y3_l = 320, 370
    f.append(text(x0 - 15, y3_h + 26, "CHxN\n(Low-Side)", size=12, bold=True, color=POS, anchor="end"))
    f.append(line(x0, y3_h, 280, y3_h, color=POS, sw=2.4))
    f.append(line(280, y3_h, 280, y3_l, color=POS, sw=2.4))
    f.append(line(280, y3_l, 690, y3_l, color=POS, sw=2.4))
    f.append(line(690, y3_l, 690, y3_h, color=POS, sw=2.4))
    f.append(line(690, y3_h, x1, y3_h, color=POS, sw=2.4))

    # Зони мертвого часу (Dead-Time)
    # Зона 1: від спаду CHxN (280) до фронту CHx (350)
    f.append(rect(280, 80, 70, 320, fill="#fdecea", stroke=POS, sw=1.2))
    f.append(text(315, 68, "t_dead", size=12, bold=True, color=POS))
    f.append(line(280, 410, 350, 410, color=POS, sw=1.6))
    f.append(text(315, 430, "Мертвий час 1", size=11, color=POS))

    # Зона 2: від спаду CHx (620) до фронту CHxN (690)
    f.append(rect(620, 80, 70, 320, fill="#fdecea", stroke=POS, sw=1.2))
    f.append(text(655, 68, "t_dead", size=12, bold=True, color=POS))
    f.append(line(620, 410, 690, 410, color=POS, sw=1.6))
    f.append(text(655, 430, "Мертвий час 2", size=11, color=POS))

    # Пояснювальний блок знизу
    f.append(fitbox(120, 490, 840, 52,
                    "Захист від наскрізного струму (Shoot-Through): обидва транзистори гарантовано закриті під час перемикання стійки",
                    size=12.5, fill="#eef7f0", stroke=FIELD, bold=True, color=FIELD))

    render(os.path.join(IMG, 'dead-time-generation.svg'), W, H, *f,
           title="Формування мертвого часу (Dead-Time Insertion) між комплементарними виходами")


# ── 12. Ланцюг обробки вхідного сигналу Input Capture ─────────────────────────
def fig_input_capture_chain():
    W, H = 1140, 540
    f = []

    # Фізичний пін
    b1, w1, h1 = textbox(110, 180, "Зовнішній пін\n(TIMx_CH1)", size=13, fill="#f4f6f8", stroke=MUTED)
    f.append(b1)

    # 1. Цифровий фільтр
    b2, w2, h2 = textbox(320, 180, "Цифровий фільтр\n(IC1F[3:0] / f_DTS)\nN послідовних вибірок",
                         size=12.5, min_w=180, fill="#ffffff", stroke=LINE)
    f.append(b2)
    f.append(arrow(110 + w1 / 2 + 6, 180, 320 - w2 / 2 - 6, 180))
    f.append(text(210, 166, "сирий TI1", size=11, color=MUTED))

    # 2. Селектор та інвертор полярності
    b3, w3, h3 = textbox(570, 180, "Детектор фронту\n(CC1P / CC1NP)\n↑ наростаючий / ↓ спадний",
                         size=12.5, min_w=190, fill="#ffffff", stroke=LINE)
    f.append(b3)
    f.append(arrow(320 + w2 / 2 + 6, 180, 570 - w3 / 2 - 6, 180))
    f.append(text(440, 166, "фільтрований TI1F", size=11, color=MUTED))

    # 3. Передподільник захоплення
    b4, w4, h4 = textbox(810, 180, "Вхідний дільник\n(IC1PSC[1:0])\n÷1, ÷2, ÷4, ÷8 подій",
                         size=12.5, min_w=170, fill="#ffffff", stroke=LINE)
    f.append(b4)
    f.append(arrow(570 + w3 / 2 + 6, 180, 810 - w4 / 2 - 6, 180))
    f.append(text(685, 166, "TI1FP1", size=11, color=MUTED))

    # 4. Засувка і регістр CCR1
    b5, w5, h5 = textbox(1020, 180, "Регістр\nзахоплення\n(CCR1)",
                         size=13, min_w=130, fill="#eef7f0", stroke=FIELD, sw=2)
    f.append(b5)
    f.append(arrow(810 + w4 / 2 + 6, 180, 1020 - w5 / 2 - 6, 180))
    f.append(text(910, 166, "тригер IC1", size=11, color=FIELD))

    # Лічильник CNT під'єднаний до CCR1
    b_cnt, w_cnt, h_cnt = textbox(1020, 360, "Лічильник CNT\n(поточний час)", size=13, fill="#ffffff", stroke=FIELD)
    f.append(b_cnt)
    f.append(arrow(1020, 360 - h_cnt / 2 - 6, 1020, 180 + h5 / 2 + 6, color=FIELD, sw=2.2))
    f.append(text(1020 - 15, 270, "копіювання CNT → CCR1\nв апаратурі за 1 такт", size=11.5, color=FIELD, anchor="end"))

    # Події прапорців
    f.append(rect(110, 340, 750, 140, fill="#fdf1ef", stroke=POS, sw=1.4))
    f.append(text(485, 365, "Фіксація результату захоплення та статусів", size=13, bold=True, color=POS))
    f.append(fitbox(130, 385, 710, 38,
                    "Прапорець CC1IF := 1 → запит переривання NVIC / DMA для зчитування мітки часу CCR1", size=12))
    f.append(fitbox(130, 428, 710, 40,
                    "Прапорець CC1OF (Capture Overrun) := 1, якщо новий фронт надійшов до вичитування попереднього CCR1",
                    size=12, fill="#fdecea", stroke=POS, color=POS))

    render(os.path.join(IMG, 'input-capture-chain.svg'), W, H, *f,
           title="Тракт вхідного захоплення: фільтрація, детекція фронту, поділ та апаратна засувка")


fig_anatomy()
fig_ramp()
fig_onchip_move()
fig_timer_count()
fig_two_eras()
fig_setup_path()
fig_preload()
fig_atomic_read()
fig_core_block()
fig_counting_modes_pwm()
fig_dead_time()
fig_input_capture_chain()
print("ok")

