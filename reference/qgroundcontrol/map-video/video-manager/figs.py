# -*- coding: utf-8 -*-
"""Фігури до теми «Відеопідсистема: джерела, керування, запис»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def tb(cx, cy, s, **kw):
    body, w, h = textbox(cx, cy, s, **kw)
    return body


def tb_h(s, size=14, pad=10):
    lines = s.split("\n") if isinstance(s, str) else list(s)
    return len(lines) * size * 1.3 + 2 * pad - size * 0.3


# ── 1. Три походження адреси ───────────────────────────────────────────────
def fig_source_origins():
    W, H = 1240, 660
    frags = []

    LX, LW = 60, 380          # колонка джерел
    MX, MW = 540, 330         # колонка перетворення
    RX, RW = 940, 250         # колонка результату

    rows = [
        ("Налаштування користувача\nтип джерела + поле адреси",
         "схема за типом:\nudp:// udp265://\nmpegts:// tcp:// rtsp://"),
        ("VIDEO_STREAM_INFORMATION\nметадані камери з борту",
         "тип потоку → джерело,\nсам порт добудовується\nдо повної адреси"),
    ]

    ys = [120, 300]
    for (src, mid), y in zip(rows, ys):
        hs, hm = tb_h(src, 14), tb_h(mid, 14)
        frags.append(fitbox(LX, y - hs / 2, LW, hs, src, size=14))
        frags.append(fitbox(MX, y - hm / 2, MW, hm, mid, size=14))
        frags.append(arrow(LX + LW + 8, y, MX - 8, y))

    # результат — один рядок-адреса
    uri_y = 210
    uri_txt = "рядок-адреса\nу приймача"
    hu = tb_h(uri_txt, 14)
    frags.append(fitbox(RX, uri_y - hu / 2, RW, hu, uri_txt, size=14,
                        stroke=FIELD, sw=2))
    frags.append(arrow(MX + MW + 8, ys[0], RX - 8, uri_y - 24))
    frags.append(arrow(MX + MW + 8, ys[1], RX - 8, uri_y + 24))

    # третя гілка — локальний пристрій
    y3 = 480
    src3 = "Локальна USB-камера\nпристрій, який бачить система"
    mid3 = "лише ідентифікатор\nпристрою, без адреси"
    res3 = "елемент QML\nмалює камеру сам"
    h3, h3m, h3r = tb_h(src3, 14), tb_h(mid3, 14), tb_h(res3, 14)
    frags.append(fitbox(LX, y3 - h3 / 2, LW, h3, src3, size=14))
    frags.append(fitbox(MX, y3 - h3m / 2, MW, h3m, mid3, size=14))
    frags.append(fitbox(RX, y3 - h3r / 2, RW, h3r, res3, size=14,
                        stroke=NEG, sw=2))
    frags.append(arrow(LX + LW + 8, y3, MX - 8, y3))
    frags.append(arrow(MX + MW + 8, y3, RX - 8, y3))

    # роздільна лінія між двома світами
    frags.append(line(40, 390, W - 40, 390, color=MUTED, sw=1.2, dash="7,6"))
    frags.append(text(LX, 372, "мережевий потік — через приймач", size=13,
                      color=MUTED, anchor="start", italic=True))
    frags.append(text(LX, 418, "локальний пристрій — повз приймач", size=13,
                      color=MUTED, anchor="start", italic=True))

    # примітка про пріоритет
    frags.append(mtext(MX + MW / 2, 574,
                       ["доки апарат надсилає метадані потоку,",
                        "вибір джерела в налаштуваннях неактивний"],
                       size=13, color=POS, lh=1.4))

    render(os.path.join(OUT, 'source-origins.svg'), W, H, *frags,
           title="Три походження адреси відеопотоку")


# ── 2. Перерахунок і порівняння ────────────────────────────────────────────
def fig_recompute():
    W, H = 1260, 700
    frags = []

    LX, LW = 50, 400
    CX, CW = 540, 300
    RX, RW = 930, 280

    signals = [
        "змінено тип джерела",
        "змінено поле адреси",
        "інший активний апарат",
        "камера повідомила стан потоку",
        "з'явився чи зник USB-пристрій",
        "перемкнуто режим низької затримки",
    ]
    y0, step = 110, 70
    ys = [y0 + i * step for i in range(len(signals))]
    hh = tb_h(signals[0], 14)

    for s, y in zip(signals, ys):
        frags.append(fitbox(LX, y - hh / 2, LW, hh, s, size=14))

    mid_y = (ys[0] + ys[-1]) / 2
    core = "перерахунок\nбажаного стану\nприймача"
    hc = tb_h(core, 15)
    frags.append(fitbox(CX, mid_y - hc / 2, CW, hc, core, size=15, stroke=FIELD, sw=2.2))

    for y in ys:
        frags.append(arrow(LX + LW + 8, y, CX - 8, mid_y + (y - mid_y) * 0.22))

    # дві відповіді
    yes_txt = "нове значення\n≠ поточного\n→ перезапуск"
    no_txt = "нове значення\n= поточному\n→ нічого не робимо"
    hy, hn = tb_h(yes_txt, 14), tb_h(no_txt, 14)
    y_yes, y_no = mid_y - 110, mid_y + 110
    frags.append(fitbox(RX, y_yes - hy / 2, RW, hy, yes_txt, size=14, stroke=POS, sw=2))
    frags.append(fitbox(RX, y_no - hn / 2, RW, hn, no_txt, size=14, stroke=NEG, sw=2))
    frags.append(arrow(CX + CW + 8, mid_y - 20, RX - 8, y_yes + 10))
    frags.append(arrow(CX + CW + 8, mid_y + 20, RX - 8, y_no - 10))

    frags.append(text(CX + CW / 2, mid_y + hc / 2 + 40,
                      "порівняння з тим, що вже стоїть у приймача",
                      size=13, color=MUTED, italic=True))

    frags.append(mtext(W / 2, 630,
                       ["перезапуск коштує секунди чорного екрана,",
                        "тому його ціна платиться лише за справжню зміну"],
                       size=13, color=MUTED, lh=1.4))

    render(os.path.join(OUT, 'recompute.svg'), W, H, *frags,
           title="Один перерахунок замість обробника на кожен вхід")


# ── 3. Два фронти запуску ──────────────────────────────────────────────────
def fig_init_fronts():
    W, H = 1180, 620
    frags = []

    top_y, bot_y = 150, 470
    mid_y = (top_y + bot_y) / 2

    start = "NotStarted"
    hs = tb_h(start, 14)
    frags.append(fitbox(60, mid_y - hs / 2, 220, hs, start, size=14))

    pend = "Pending\nзапущено обидва фронти"
    hp = tb_h(pend, 14)
    frags.append(fitbox(330, mid_y - hp / 2, 320, hp, pend, size=14))
    frags.append(arrow(288, mid_y, 322, mid_y))

    wait_top = "BackendReady\nбібліотека готова,\nчекаємо на QML"
    wait_bot = "QmlReady\nвікно готове,\nчекаємо на бібліотеку"
    hwt, hwb = tb_h(wait_top, 14), tb_h(wait_bot, 14)
    frags.append(fitbox(720, top_y - hwt / 2, 300, hwt, wait_top, size=14))
    frags.append(fitbox(720, bot_y - hwb / 2, 300, hwb, wait_bot, size=14))

    frags.append(arrow(658, mid_y - 20, 714, top_y + hwt / 2 - 6))
    frags.append(arrow(658, mid_y + 20, 714, bot_y - hwb / 2 + 6))

    frags.append(text(870, top_y + hwt / 2 + 34, "першою прийшла бібліотека",
                      size=12, color=MUTED, anchor="middle"))
    frags.append(text(870, bot_y - hwb / 2 - 26, "першим прийшов QML",
                      size=12, color=MUTED, anchor="middle"))

    run = "Running\nприймачі створено"
    hr = tb_h(run, 14)
    frags.append(fitbox(1040, mid_y - hr / 2, 100, hr, run, size=13))
    # ширша рамка з переносом: даємо запас
    frags = frags[:-1]
    frags.append(fitbox(1030, mid_y - hr / 2, 130, hr, run, size=11))

    frags.append(arrow(1024, top_y + hwt / 2 + 4, 1060, mid_y - hr / 2 - 6))
    frags.append(arrow(1024, bot_y - hwb / 2 - 4, 1060, mid_y + hr / 2 + 6))

    frags.append(mtext(W / 2, 566,
                       ["перехід у Pending робиться порівнянням із заміною:",
                        "у цю точку заходять із різних ниток, а ініціалізувати треба один раз"],
                       size=13, color=MUTED, lh=1.4))

    render(os.path.join(OUT, 'init-fronts.svg'), W, H, *frags,
           title="Два незалежні фронти готовності сходяться в один стан")


# ── 4. Життя приймача ──────────────────────────────────────────────────────
def fig_receiver_life():
    W, H = 1200, 700
    frags = []

    CX = 380
    BOXW = 460

    stations = [
        "зупинено\nадреса є, потоку нема",
        "start(timeout)\n3 с для UDP, 8 с для RTSP",
        "onStartComplete(STATUS_OK)\nприймання пішло",
        "startDecoding(стік)\nкадри йдуть на екран",
    ]
    notes = [
        ["менеджер запускає приймач,", "щойно hasVideo() істинний"],
        ["чекання асинхронне:", "головна нитка не блокується"],
        ["приймання й показ —", "два окремі кроки"],
        ["кадри в головну нитку", "не заходять узагалі"],
    ]

    y0, step = 110, 130
    ys = [y0 + i * step for i in range(len(stations))]

    for s, y in zip(stations, ys):
        h = tb_h(s, 14)
        frags.append(fitbox(CX - BOXW / 2, y - h / 2, BOXW, h, s, size=14))

    for i in range(len(stations) - 1):
        ha, hb = tb_h(stations[i], 14), tb_h(stations[i + 1], 14)
        frags.append(arrow(CX, ys[i] + ha / 2 + 4, CX, ys[i + 1] - hb / 2 - 4))

    for n, y in zip(notes, ys):
        top = y - (len(n) - 1) * 12 * 1.4 / 2
        frags.append(mtext(CX + BOXW / 2 + 30, top, n, size=12, color=MUTED,
                           anchor="start", lh=1.4))

    # петля невдачі
    fail_txt = "будь-який інший стан\nчекання 1 с → нова спроба"
    hf = tb_h(fail_txt, 14)
    fy = 570
    frags.append(fitbox(CX - BOXW / 2, fy - hf / 2, BOXW, hf, fail_txt, size=14,
                        stroke=POS, sw=2))
    frags.append(arrow(CX - BOXW / 2 - 10, ys[2], CX - BOXW / 2 - 10, fy - hf / 2 - 6,
                       color=POS))
    frags.append(line(CX - BOXW / 2 - 10, ys[2], CX - BOXW / 2, ys[2], color=POS, sw=1.8))
    frags.append(arrow(CX + BOXW / 2 + 10, fy, CX + BOXW / 2 + 10, ys[1] + 8, color=POS))
    frags.append(line(CX + BOXW / 2, fy, CX + BOXW / 2 + 10, fy, color=POS, sw=1.8))
    frags.append(line(CX + BOXW / 2 + 10, ys[1] + 8, CX + BOXW / 2, ys[1] + 8,
                      color=POS, sw=1.8))

    # виходи з циклу
    exits = "з циклу виводять лише двоє:\nSTATUS_INVALID_URL — адреса бита\nhasVideo() хибний — потік вимкнено"
    he = tb_h(exits, 13)
    frags.append(fitbox(880, fy - he / 2, 290, he, exits, size=13, stroke=NEG, sw=2))
    frags.append(arrow(CX + BOXW / 2 + 24, fy - 20, 872, fy - 20, color=NEG))

    render(os.path.join(OUT, 'receiver-life.svg'), W, H, *frags,
           title="Життя приймача з боку менеджера")


# ── 5. Перезапуск чи на ходу (вставка proj-source-resolution) ──────────────
def fig_restart_vs_live():
    W, H = 1300, 640
    frags = []

    LX, LW = 60, 400
    MX, MW = 530, 320
    RX, RW = 940, 300

    # верхня група — величини, що йдуть у побудову конвеєра
    top_items = [
        "адреса зі схемою\nudp://  udp265://  mpegts://",
        "режим низької затримки",
        "глибина буфера вирівнювання",
    ]
    top_ys = [125, 208, 288]
    for s, y in zip(top_items, top_ys):
        h = tb_h(s, 14)
        frags.append(fitbox(LX, y - h / 2, LW, h, s, size=14))

    mid_top = "прапорець змін\nchanged |= (нове ≠ поточного)"
    hmt = tb_h(mid_top, 14)
    frags.append(fitbox(MX, 208 - hmt / 2, MW, hmt, mid_top, size=14,
                        stroke=FIELD, sw=2))

    res_top = "перезапуск конвеєра\nсекунди чорного екрана"
    hrt = tb_h(res_top, 14)
    frags.append(fitbox(RX, 208 - hrt / 2, RW, hrt, res_top, size=14,
                        stroke=NEG, sw=2))

    for y in top_ys:
        frags.append(arrow(LX + LW + 10, y, MX - 10, 208 + (y - 208) * 0.18))
    frags.append(arrow(MX + MW + 10, 208, RX - 10, 208))

    frags.append(text(LX, 88, "читають, коли конвеєр БУДУЮТЬ", size=13,
                      color=MUTED, anchor="start", italic=True))

    # роздільна лінія
    frags.append(line(40, 372, W - 40, 372, color=MUTED, sw=1.2, dash="7,6"))
    frags.append(text(LX, 414, "читають НА ХОДУ, коли сталася невдача", size=13,
                      color=MUTED, anchor="start", italic=True))

    # нижня група — жива величина
    y_low = 478
    low_src = "автоматичне перепід'єднання\nrtspAutoReconnect"
    low_mid = "значення передаємо,\nпрапорця НЕ чіпаємо"
    low_res = "конвеєр працює далі,\nкартинка не блимає"
    hls, hlm, hlr = tb_h(low_src, 14), tb_h(low_mid, 14), tb_h(low_res, 14)
    frags.append(fitbox(LX, y_low - hls / 2, LW, hls, low_src, size=14))
    frags.append(fitbox(MX, y_low - hlm / 2, MW, hlm, low_mid, size=14))
    frags.append(fitbox(RX, y_low - hlr / 2, RW, hlr, low_res, size=14,
                        stroke=POS, sw=2))
    frags.append(arrow(LX + LW + 10, y_low, MX - 10, y_low))
    frags.append(arrow(MX + MW + 10, y_low, RX - 10, y_low))

    frags.append(mtext(W / 2, 578,
                       ["критерій один: коли саме значення читають —",
                        "під час побудови ланцюга чи вже під час його роботи"],
                       size=13, color=MUTED, lh=1.4))

    render(os.path.join(OUT, 'restart-vs-live.svg'), W, H, *frags,
           title="Величини перезапуску й живі величини")


# ── 6. Зворотний запис і згасання петлі (вставка proj-source-resolution) ────
def fig_writeback_loop():
    W, H = 1220, 640
    frags = []

    BW = 430
    LX, RX = 110, 680          # ліва й права колонки
    TY, BY = 130, 330          # верхній і нижній ряди
    LCX, RCX = LX + BW / 2, RX + BW / 2

    tl = "перерахунок №1\nвхід: метадані камери\nchanged = так"
    tr = "перезапуск конвеєра\n+ вибране джерело лягає\nу налаштування"
    br = "факт джерела змінився →\nсигнал → перерахунок знову"
    bl = "перерахунок №2\nті самі входи\nchanged = ні"

    htl, htr = tb_h(tl, 14), tb_h(tr, 14)
    hbr, hbl = tb_h(br, 14), tb_h(bl, 14)

    frags.append(fitbox(LX, TY - htl / 2, BW, htl, tl, size=14, stroke=FIELD, sw=2))
    frags.append(fitbox(RX, TY - htr / 2, BW, htr, tr, size=14))
    frags.append(fitbox(RX, BY - hbr / 2, BW, hbr, br, size=14))
    frags.append(fitbox(LX, BY - hbl / 2, BW, hbl, bl, size=14, stroke=POS, sw=2))

    frags.append(arrow(LX + BW + 10, TY, RX - 10, TY))
    frags.append(arrow(RCX, TY + htr / 2 + 8, RCX, BY - hbr / 2 - 8))
    frags.append(arrow(RX - 10, BY, LX + BW + 10, BY))

    frags.append(text((LX + BW + RX) / 2, TY - 46, "перше коло", size=12,
                      color=MUTED))
    frags.append(text((LX + BW + RX) / 2, BY - 42, "друге коло", size=12,
                      color=MUTED))

    exit_txt = "конвеєр не чіпаємо —\nповторне коло згасає тут"
    hex_ = tb_h(exit_txt, 14)
    EY = 490
    frags.append(fitbox(LX, EY - hex_ / 2, BW, hex_, exit_txt, size=14,
                        stroke=POS, sw=2))
    frags.append(arrow(LCX, BY + hbl / 2 + 8, LCX, EY - hex_ / 2 - 8, color=POS))

    frags.append(mtext(W / 2, 574,
                       ["ідемпотентність тут не оздоба стилю,",
                        "а те єдине, що зупиняє рекурсію «запис → сигнал → перерахунок»"],
                       size=13, color=MUTED, lh=1.4))

    render(os.path.join(OUT, 'writeback-loop.svg'), W, H, *frags,
           title="Зворотний запис джерела згасає на другому колі")


# ── 7. Розкладка накладки в кадрі ──────────────────────────────────────────
def fig_subtitle_layout():
    W, H = 1240, 810
    frags = []

    FX, FY, FW = 110, 80, 1020          # кадр 1280×720 у масштабі
    FH = int(FW * 720 / 1280)           # 574
    k = FW / 1280.0

    def px(v):                          # координата ASS → координата фігури
        return FX + v * k

    def py(v):
        return FY + v * k

    frags.append(rect(FX, FY, FW, FH, fill="#eef1f4", stroke=LINE, sw=2, rx=4))
    frags.append(text(FX + FW - 12, FY + 22, "кадр 1280 × 720", size=13,
                      color=MUTED, anchor="end"))

    # дата в кутку — \pos(10,35)
    frags.append(text(px(10), py(35), "02.08.2026", size=15, color=INK,
                      anchor="start"))
    frags.append(text(px(10), py(35) + 22, "{\\pos(10,35)}", size=11,
                      color=MUTED, anchor="start"))

    # три пари колонок
    cols = [
        (295, ["Висота:", "Швидкість:", "Курс:"], ["8.8 м", "9.7 м/с", "27°"]),
        (640, ["Батарея:", "Політ:", "Супутники:"], ["16.79 В", "3 с", "12"]),
        (985, ["Режим:"], ["AUTO"]),
    ]
    base = py(690)                      # низ блока
    lh = 23

    for xv, names, values in cols:
        xn, xval = px(xv - 10), px(xv)
        n = len(names)
        for i in range(n):
            yb = base - (n - 1 - i) * lh
            frags.append(text(xn, yb, names[i], size=15, color=INK, anchor="end"))
            frags.append(text(xval, yb, values[i], size=15, color=INK,
                              anchor="start"))
        # пунктир, що показує лінію притискання
        frags.append(line(xval - 4, base - n * lh - 14, xval - 4, base + 10,
                          color=FIELD, sw=1.6, dash="4 4"))
        frags.append(text(xval - 4, base - n * lh - 24, "x = %d" % xv, size=12,
                          color=FIELD))

    frags.append(text(px(640), py(300),
                      "жодного пікселя картинки не змінено",
                      size=15, color=MUTED))
    frags.append(text(px(640), py(690) - 3 * lh - 62,
                      "назви \\an3 — правий край · значення \\an1 — лівий край",
                      size=13, color=MUTED))

    # три пояснювальні коробки під кадром
    BW, BY, BH = 320, 690, 96
    gap = (W - 2 * 110 - 3 * BW) / 2
    boxes = [
        "кегль від ширини\n(1280 × 12) / 640 = 24",
        "крок колонок\n(1280 + 100) / (3 + 1) = 345\nx = −50 + 345 · (i + 1)",
        "низ блока\n720 − 30 = 690\nблок росте вгору",
    ]
    for i, b in enumerate(boxes):
        bx = 110 + i * (BW + gap)
        frags.append(fitbox(bx, BY, BW, BH, b, size=14))

    render(os.path.join(OUT, 'subtitle-layout.svg'), W, H, *frags,
           title="Накладка в кадрі: дві колонки тексту на кожну колонку даних")


# ── 8. Мить знімка проти інтервалу показу ──────────────────────────────────
def fig_subtitle_timing():
    W, H = 1240, 580
    frags = []

    AX0, AX1 = 300, 1170
    N = 4
    step = (AX1 - AX0) / N
    CX = (AX0 + AX1) / 2

    def draw_row(y, title_lines, sample_at_end, note, note_color):
        col = POS if sample_at_end else FIELD
        frags.append(fitbox(60, y - 42, 210, 84, title_lines, size=13))
        for i in range(N):
            x0 = AX0 + i * step
            frags.append(rect(x0, y - 26, step, 52, fill=FILL, stroke=LINE,
                              sw=1.4, rx=4))
            frags.append(text(x0 + step / 2, y + 6, "%d–%d с" % (i, i + 1),
                              size=14))
        for i in range(N):
            sx = AX0 + (i + 1) * step if sample_at_end else AX0 + i * step
            frags.append(circle(sx, y - 26, 7, fill=col, stroke=col, sw=1.5))
            frags.append(arrow(sx, y - 48, AX0 + i * step + step / 2, y - 48,
                               color=col))
        for i in range(N + 1):
            frags.append(text(AX0 + i * step, y + 48, "%d" % i, size=12,
                              color=MUTED))
        frags.append(text(CX, y + 112, note, size=13, color=note_color))

    frags.append(text(CX, 68,
                      "інтервали змикаються: кінець одного = початок наступного, "
                      "тож накладка не блимає",
                      size=13, color=MUTED))

    draw_row(170, "у застосунку:\nзнімок наприкінці\nінтервалу", True,
             "у кадрі 0–1 с видно числа, зняті на 1-й секунді — "
             "накладка біжить на секунду попереду", POS)

    draw_row(410, "як треба:\nзнімок на початку\nінтервалу", False,
             "число, підписане під інтервалом, узяте саме тоді, "
             "коли інтервал почався", FIELD)

    render(os.path.join(OUT, 'subtitle-timing.svg'), W, H, *frags,
           title="Мить знімка проти інтервалу показу")


fig_source_origins()
fig_recompute()
fig_init_fronts()
fig_receiver_life()
fig_restart_vs_live()
fig_writeback_loop()
fig_subtitle_layout()
fig_subtitle_timing()
print("ok")
