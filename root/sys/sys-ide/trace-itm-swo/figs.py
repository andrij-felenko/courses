# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── halt-vs-trace: брейкпойнт спиняє час, траса спостерігає на ходу ─────────────
# Ідея: на лівій доріжці час РВЕТЬСЯ (ядро стало на halt — реальний час іде далі,
# програма ні); на правій ядро біжить безперервно, а спостереження тече збоку.
# Це головна теза статті: для real-time потрібне спостереження БЕЗ зупину.

def fig_halt_vs_trace():
    W, H = 720, 320
    p = []
    # ліва доріжка — halt
    lx = 60
    p.append(text(lx, 56, "Брейкпойнт: ядро стоїть", size=13, color=POS, anchor="start", bold=True))
    ly = 96
    # смуга виконання з розривом
    p.append(rect(lx, ly, 110, 26, fill="#eef4ff", stroke=INK, sw=1.4))
    p.append(text(lx + 55, ly + 17, "біжить", size=10, color=INK))
    p.append(rect(lx + 130, ly, 80, 26, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(lx + 170, ly + 17, "СТОП", size=10, color=POS, bold=True))
    p.append(rect(lx + 220, ly, 60, 26, fill="#eef4ff", stroke=INK, sw=1.4))
    p.append(text(lx + 250, ly + 17, "далі", size=10, color=INK))
    # реальний світ не чекає
    p.append(text(lx, ly + 64, "реальний час тим часом:", size=11, color=MUTED, anchor="start"))
    p.append(arrow(lx, ly + 86, lx + 280, ly + 86, color=POS, sw=2.0))
    p.append(text(lx + 140, ly + 104, "мотор крутиться, пакет летить, дедлайн збито",
                  size=9.5, color=POS))

    # роздільник
    p.append(line(W / 2 + 6, 70, W / 2 + 6, H - 40, color="#dddddd", sw=1.2, dash="5 5"))

    # права доріжка — trace
    rx = W / 2 + 40
    p.append(text(rx, 56, "Траса: ядро не спиняється", size=13, color=FIELD, anchor="start", bold=True))
    ry = 96
    p.append(rect(rx, ry, 270, 26, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(text(rx + 135, ry + 17, "ядро біжить безперервно", size=10, color=FIELD, bold=True))
    # відгалуження спостереження вниз, ядро не чіпаємо
    for i in range(5):
        xx = rx + 30 + i * 56
        p.append(arrow(xx, ry + 26, xx, ry + 60, color=NEG, sw=1.4))
    p.append(rect(rx, ry + 62, 270, 26, fill="#eef4ff", stroke=NEG, sw=1.5))
    p.append(text(rx + 135, ry + 79, "потік подій тече на хост", size=10, color=NEG))
    p.append(text(rx, ry + 116, "час видно, а виконання не рвемо", size=11, color=MUTED, anchor="start", italic=True))

    p.append(text(W / 2, H - 16,
                  "halt зупиняє і ловить миттєвий зріз; траса не спиняє і бачить поведінку в часі",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "halt-vs-trace.svg"), W, H, *p,
           title="Зупинити час чи спостерігати за ним на ходу")


# ── itm-ports: 32 стимул-порти ITM зливаються в один потік ─────────────────────
# Ідея: програма пише у будь-який із 32 портів простим записом у регістр; апаратний
# блок ITM збирає це в єдиний потік пакетів — без форматування на ядрі, дешево.

def fig_itm_ports():
    W, H = 720, 330
    p = []
    p.append(text(W / 2, 54, "Прошивка пише — ITM пакує — потік виходить",
                  size=12, color=MUTED, italic=True))
    # стовпчик портів зліва
    px = 60
    ports = [("порт 0", "printf-вивід"), ("порт 1", "мітки подій"),
             ("порт 2", "лічильник черги"), ("…", ""), ("порт 31", "будь-що своє")]
    py = 80
    cy = []
    for name, sub in ports:
        h = 34
        p.append(rect(px, py, 150, h, fill="#eef4ff", stroke=NEG, sw=1.4))
        p.append(text(px + 10, py + 22, name, size=11, color=NEG, anchor="start", bold=True))
        if sub:
            p.append(text(px + 144, py + 22, sub, size=9.5, color=MUTED, anchor="end"))
        cy.append(py + h / 2)
        py += h + 8

    # блок ITM посередині
    bx, by, bw, bh = 330, 130, 110, 90
    p.append(fitbox(bx, by, bw, bh, "ITM\n(апаратний\nблок)", size=12, bold=True,
                    fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD))
    for c in cy:
        p.append(arrow(px + 150, c, bx - 2, by + bh / 2 + (c - 175) * 0.18, color=NEG, sw=1.3))

    # єдиний потік пакетів праворуч
    p.append(arrow(bx + bw, by + bh / 2, bx + bw + 70, by + bh / 2, color=INK, sw=2.2))
    sx = bx + bw + 72
    for i, lab in enumerate(["п0", "п2", "п0", "п1"]):
        p.append(rect(sx + i * 40, by + bh / 2 - 14, 34, 28, fill="#fdf6e3", stroke="#9a7d1a", sw=1.4))
        p.append(text(sx + i * 40 + 17, by + bh / 2 + 4, lab, size=10, color="#9a7d1a"))
    p.append(text(sx + 80, by + bh / 2 + 38, "потік пакетів\n(номер порту + дані)", size=10, color=MUTED))

    p.append(text(W / 2, H - 16,
                  "запис у порт = одна команда STR; форматування й буферизації на ядрі немає",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "itm-ports.svg"), W, H, *p,
           title="ITM: 32 програмні порти в один потік пакетів")


# ── trace-pipeline: конвеєр trace → TPIU → SWO → зонд → хост ───────────────────
# Ідея: показати весь шлях траси від джерел (ITM/DWT/ETM) через злиття у TPIU
# до фізичного виносу: SWO (1 пін, вузько) АБО паралельний trace-порт (широко).

def fig_trace_pipeline():
    W, H = 740, 340
    p = []
    # джерела зліва
    src = [("ITM", "програмні\nповідомлення", "#eef4ff", NEG),
           ("DWT", "цикли, події,\nсемпли PC", "#eafaf0", FIELD),
           ("ETM", "повна траса\nінструкцій", "#fdecea", POS)]
    sx = 40
    sy0 = 80
    cyy = []
    for name, sub, fill, col in src:
        h = 56
        yy = sy0 + len(cyy) * (h + 18)
        p.append(fitbox(sx, yy, 120, h, name + "\n" + sub, size=11, bold=True,
                        fill=fill, stroke=col, sw=1.6, color=col))
        cyy.append(yy + h / 2)

    # TPIU посередині
    tx, ty, tw, th = 250, 120, 120, 96
    p.append(fitbox(tx, ty, tw, th, "TPIU\nзлиття у\nспільний потік", size=11, bold=True,
                    fill="#f6f4ec", stroke=INK, sw=1.8))
    for c in cyy:
        p.append(arrow(sx + 120, c, tx - 2, ty + th / 2 + (c - 168) * 0.25, color=INK, sw=1.5))

    # дві фізичні дороги виносу
    # SWO — 1 пін, вузько
    p.append(fitbox(460, 90, 150, 48, "SWO — 1 пін", size=12, bold=True,
                    fill="#eef4ff", stroke=NEG, sw=1.6, color=NEG))
    p.append(arrow(tx + tw, ty + 24, 458, 114, color=NEG, sw=1.8))
    p.append(text(460, 154, "вузько: ITM + DWT;", size=10, color=MUTED, anchor="start"))
    p.append(text(460, 170, "повна ETM не влізе", size=10, color=MUTED, anchor="start"))

    # паралельний trace-порт — широко
    p.append(fitbox(460, 210, 150, 48, "trace-порт\n4–32 піни", size=12, bold=True,
                    fill="#fdecea", stroke=POS, sw=1.6, color=POS))
    p.append(arrow(tx + tw, ty + th - 24, 458, 234, color=POS, sw=1.8))
    p.append(text(460, 274, "широко: тягне ETM,", size=10, color=MUTED, anchor="start"))
    p.append(text(460, 290, "але багато ніжок", size=10, color=MUTED, anchor="start"))

    # зонд → хост
    p.append(arrow(612, 114, 660, 114, color=INK, sw=2.0))
    p.append(arrow(612, 234, 660, 234, color=INK, sw=2.0))
    p.append(fitbox(662, 150, 60, 48, "зонд →\nхост", size=10, bold=True,
                    fill=FILL, stroke=INK, sw=1.4))

    render(os.path.join(OUT, "trace-pipeline.svg"), W, H, *p,
           title="Конвеєр траси: джерела → TPIU → винос на хост")


# ── dwt-cyccnt: вимір тривалості ISR лічильником циклів ────────────────────────
# Ідея: CYCCNT тикає КОЖЕН такт ядра незалежно від коду; різниця двох знімків —
# точна тривалість ділянки в циклах, без жодного зупину.

def fig_dwt_cyccnt():
    W, H = 720, 290
    p = []
    # лінія часу-тактів
    ax = 70
    ay = 150
    p.append(arrow(ax - 10, ay, W - 40, ay, color=INK, sw=1.8))
    p.append(text(W - 40, ay - 12, "такти ядра", size=10, color=MUTED, anchor="end"))
    # тики
    for i in range(13):
        xx = ax + i * 44
        p.append(line(xx, ay - 5, xx, ay + 5, color=MUTED, sw=1.0))

    # вхід/вихід ISR
    x_in = ax + 2 * 44
    x_out = ax + 9 * 44
    p.append(rect(x_in, ay - 40, x_out - x_in, 30, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(text((x_in + x_out) / 2, ay - 20, "тіло ISR виконується", size=11, color=POS, bold=True))

    p.append(arrow(x_in, ay - 58, x_in, ay - 42, color=NEG, sw=1.6))
    p.append(text(x_in, ay - 64, "знімок t0 = CYCCNT", size=10, color=NEG))
    p.append(arrow(x_out, ay - 58, x_out, ay - 42, color=FIELD, sw=1.6))
    p.append(text(x_out, ay - 64, "знімок t1 = CYCCNT", size=10, color=FIELD))

    # результат
    p.append(text(W / 2, ay + 50, "t1 − t0 = рівно стільки тактів тривав ISR", size=12, color=INK, bold=True))
    p.append(text(W / 2, ay + 74, "÷ частоту ядра → час у мікросекундах", size=11, color=MUTED))
    p.append(text(W / 2, ay + 98, "CYCCNT тикає сам, кожен такт — вимір не спиняє ядро й не спотворює час",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "dwt-cyccnt.svg"), W, H, *p,
           title="DWT-лічильник циклів: точний вимір без зупину")


# ── swo-bandwidth: SWO як вузьке горло ─────────────────────────────────────────
# Ідея: один пін має скінченну смугу; як тільки джерела генерують більше, ніж
# пін виносить, апаратний FIFO переповнюється і пакети ПАДАЮТЬ (overflow).

def fig_swo_bandwidth():
    W, H = 720, 300
    p = []
    # широкий вхід зліва (багато подій)
    p.append(text(70, 70, "Джерела генерують багато", size=12, color=POS, anchor="start", bold=True))
    p.append('<path d="M70 100 L280 130 L280 190 L70 220 Z" fill="#fdecea" stroke="%s" stroke-width="1.6"/>' % POS)
    p.append(text(150, 165, "ITM+DWT", size=12, color=POS, bold=True))

    # вузьке горло — FIFO + пін
    fx = 300
    p.append(rect(fx, 140, 70, 40, fill="#fdf6e3", stroke="#9a7d1a", sw=1.6))
    p.append(text(fx + 35, 164, "FIFO", size=11, color="#9a7d1a", bold=True))
    p.append(arrow(280, 160, fx - 2, 160, color=INK, sw=2.0))
    # тонкий пін
    p.append(rect(fx + 90, 152, 150, 16, fill="#eef4ff", stroke=NEG, sw=1.6))
    p.append(text(fx + 165, 164, "SWO — 1 пін", size=10, color=NEG, bold=True))
    p.append(arrow(fx + 70, 160, fx + 88, 160, color=INK, sw=2.0))
    p.append(arrow(fx + 240, 160, fx + 280, 160, color=NEG, sw=2.0))
    p.append(text(fx + 300, 164, "хост", size=10, color=INK, anchor="start"))

    # переповнення
    p.append(text(fx + 35, 122, "переповнення →", size=10, color=POS, anchor="middle", bold=True))
    p.append(arrow(fx + 35, 126, fx + 35, 138, color=POS, sw=1.6))
    p.append('<path d="M%d 196 l 8 14 l -16 0 z" fill="#fdecea" stroke="%s" stroke-width="1.4"/>' % (fx + 35, POS))
    p.append(text(fx + 35, 226, "зайві пакети\nпадають", size=10, color=POS))

    p.append(text(W / 2, H - 22,
                  "смуга SWO скінченна: щойно потік перевищує пропускну, частина траси втрачається мовчки",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "swo-bandwidth.svg"), W, H, *p,
           title="SWO — вузьке горло: один пін має межу пропускної")


# ════════════════ Фігури ДЕТАЛЬНОЇ версії (trace-itm-swo-d.md) ═════════════════
# Імена з префіксом «d-», щоб не плутати з фігурами базової у тій самій ./img/.


# ── d-itm-packet: формат пакета ITM на дроті ───────────────────────────────────
# Ідея: пакет ITM — це заголовок (номер порту + розмір корисних даних) і самі
# дані 1/2/4 байти; показати бітову розкладку заголовка стимул-порту.

def fig_d_itm_packet():
    W, H = 740, 330
    p = []
    # смуга пакета
    y = 90
    bh = 46

    def seg(x, w, lab, sub, fill, col):
        p.append(rect(x, y, w, bh, fill=fill, stroke=col, sw=1.6))
        p.append(text(x + w / 2, y + 20, lab, size=11, color=col, bold=True))
        if sub:
            p.append(text(x + w / 2, y + 37, sub, size=9, color=MUTED))
        return x + w

    x = 60
    x = seg(x, 200, "Заголовок", "1 байт", "#eef4ff", NEG)
    x = seg(x, 360, "Корисні дані", "1, 2 або 4 байти", "#fdf6e3", "#9a7d1a")

    # розкладка заголовка
    p.append(text(60, y + bh + 38, "Заголовок стимул-порту, біт за бітом:", size=12, color=INK, anchor="start", bold=True))
    fields = [("A[4:3]\nномер порту", "#dcecff"), ("0", "#f6f4ec"),
              ("SS\nрозмір", "#fdf6e3")]
    widths = [360, 90, 150]
    labels_bits = ["біти 7..3", "біт 2", "біти 1..0"]
    fx = 60
    yy = y + bh + 54
    for (lab, fill), w, bb in zip(fields, widths, labels_bits):
        p.append(rect(fx, yy, w, 50, fill=fill, stroke=INK, sw=1.3, rx=4))
        p.append(mtext(fx + w / 2, yy + 22, lab, size=10, color=INK))
        p.append(text(fx + w / 2, yy + 64, bb, size=9, color=MUTED))
        fx += w + 6

    p.append(text(60, yy + 92, "SS: 01 → 1 байт даних · 10 → 2 байти · 11 → 4 байти (біт 2 = 0 ⇒ це стимул-пакет)",
                  size=10, color=MUTED, anchor="start", italic=True))
    render(os.path.join(OUT, "d-itm-packet.svg"), W, H, *p,
           title="Пакет ITM: заголовок із номером порту й розміром + дані")


# ── d-swo-encoding: два кодування SWO — NRZ і Manchester ───────────────────────
# Ідея: показати ту саму послідовність бітів двома способами; NRZ потребує
# узгодженої швидкості (як UART), Manchester несе такт у собі, але вдвічі ширший.

def fig_d_swo_encoding():
    W, H = 740, 360
    p = []
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    x0 = 90
    unit = 64
    hi, lo = 0, 34

    def draw_nrz(yb, label):
        p.append(text(60, yb - 40, label, size=12, color=INK, anchor="start", bold=True))
        path = "M%d %d" % (x0, yb - (hi if bits[0] else lo))
        x = x0
        prev = bits[0]
        for b in bits:
            lvl = hi if b else lo
            if b != prev:
                path += " V%d" % (yb - lvl)
            path += " H%d" % (x + unit)
            prev = b
            x += unit
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path, NEG))
        for i, b in enumerate(bits):
            p.append(text(x0 + i * unit + unit / 2, yb + 20, str(b), size=11, color=MUTED))

    def draw_manchester(yb, label):
        p.append(text(60, yb - 40, label, size=12, color=INK, anchor="start", bold=True))
        x = x0
        path = "M%d %d" % (x, yb)
        for b in bits:
            # 1 = перехід вгору в середині, 0 = вниз; малюємо half-half
            if b == 1:
                path += " H%d V%d H%d" % (x + unit / 2, yb - hi, x + unit)
                # повернути рівень для наступного старту через вертикаль на межі
                path += " V%d" % (yb - lo) if True else ""
            else:
                path += " V%d H%d V%d H%d" % (yb - hi, x + unit / 2, yb - lo, x + unit)
            x += unit
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path, FIELD))
        for i in range(len(bits) + 1):
            xx = x0 + i * unit
            p.append(line(xx, yb - hi - 4, xx, yb + 6, color="#dddddd", sw=0.8))
        for i, b in enumerate(bits):
            p.append(text(x0 + i * unit + unit / 2, yb + 20, str(b), size=11, color=MUTED))

    draw_nrz(120, "NRZ (UART-подібне): рівень = біт; потрібна узгоджена швидкість, як в UART")
    draw_manchester(250, "Manchester: біт = напрям переходу в середині; такт несеться в сигналі, та вдвічі ширше")

    p.append(text(W / 2, H - 18,
                  "NRZ ефективніший за смугою; Manchester самосинхронний — хост ловить швидкість без точної згоди",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "d-swo-encoding.svg"), W, H, *p,
           title="Кодування SWO: NRZ проти Manchester")


# ── d-dwt-registers: ключові регістри DWT і що кожен дає ────────────────────────
# Ідея: таблиця-карта DWT — CYCCNT (час), лічильники подій (CPI/EXC/SLEEP/LSU/FOLD),
# семплер PC, компаратори; показати, що один блок дає і вимір, і профіль, і події.

def fig_d_dwt_registers():
    W, H = 740, 410
    p = []
    rows = [
        ("CYCCNT", "лічильник тактів ядра", "точний вимір тривалості", NEG),
        ("CPICNT / EXCCNT", "такти на інструкцію, вхід у винятки", "де ядро марнує цикли", FIELD),
        ("SLEEPCNT / LSUCNT", "сон, доступи до пам'яті", "профіль простою й шини", FIELD),
        ("PC sampler", "періодичний знімок PC", "статистичний профіль «де час»", "#9a7d1a"),
        ("COMP0..3 + MASK", "компаратори адрес даних", "вотчпойнти й трасування доступу", POS),
    ]
    x = 60
    y = 70
    rw = W - 120
    rh = 52
    p.append(rect(x, y, rw, 34, fill=INK, stroke=INK, sw=1.0, rx=6))
    p.append(text(x + 16, y + 22, "регістр / вузол DWT", size=11, color=BG, anchor="start", bold=True))
    p.append(text(x + 300, y + 22, "що містить", size=11, color=BG, anchor="start", bold=True))
    p.append(text(x + 540, y + 22, "навіщо", size=11, color=BG, anchor="start", bold=True))
    yy = y + 34
    for name, has, why, col in rows:
        p.append(rect(x, yy, rw, rh, fill=FILL, stroke="#d7dde6", sw=1.0))
        p.append(text(x + 16, yy + 31, name, size=11, color=col, anchor="start", bold=True))
        p.append(text(x + 300, yy + 31, has, size=10.5, color=INK, anchor="start"))
        p.append(text(x + 540, yy + 31, why, size=10.5, color=MUTED, anchor="start"))
        yy += rh

    p.append(text(W / 2, yy + 28,
                  "один блок DWT дає три речі одразу: точний вимір (CYCCNT), профіль (лічильники + семплер PC), події (компаратори)",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "d-dwt-registers.svg"), W, H, *p,
           title="DWT зсередини: вимір, профіль і події в одному блоці")


# ── d-host-tools: ланцюг декодування траси на хості ────────────────────────────
# Ідея: сирий потік SWO/trace-порту нічого не значить без .elf; хост-інструмент
# (orbuculum / OpenOCD itm / SEGGER) розбирає пакети й мапить адреси на символи.

def fig_d_host_tools():
    W, H = 740, 300
    p = []
    # сирий потік
    p.append(fitbox(40, 110, 130, 60, "сирий потік\nпакетів", size=12, bold=True,
                    fill="#fdf6e3", stroke="#9a7d1a", sw=1.6, color="#9a7d1a"))
    # декодер
    p.append(arrow(170, 140, 220, 140, color=INK, sw=2.0))
    p.append(fitbox(222, 100, 160, 80, "декодер на хості\norbuculum /\nOpenOCD itm /\nSEGGER", size=10.5, bold=True,
                    fill="#eafaf0", stroke=FIELD, sw=1.6, color=FIELD))
    # .elf збоку
    p.append(fitbox(232, 210, 140, 44, ".elf — символи", size=11, bold=True,
                    fill="#eef4ff", stroke=NEG, sw=1.5, color=NEG))
    p.append(arrow(302, 208, 302, 182, color=NEG, sw=1.6))
    # людський вихід
    p.append(arrow(382, 140, 432, 140, color=INK, sw=2.0))
    p.append(fitbox(434, 90, 270, 100,
                    "осмислений вигляд:\n«ISR_dma тривав 1240 циклів»\n«73% часу у spi_write»\n«запис у g_state з task_a»",
                    size=10.5, bold=False, fill=FILL, stroke=INK, sw=1.5))

    p.append(text(W / 2, H - 16,
                  "без рідного .elf траса лишається купою чисел; символи перетворюють адреси на імена функцій і рядки",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "d-host-tools.svg"), W, H, *p,
           title="Декодування траси на хості: пакети + .elf → сенс")


if __name__ == "__main__":
    # базова стаття
    fig_halt_vs_trace()
    fig_itm_ports()
    fig_trace_pipeline()
    fig_dwt_cyccnt()
    fig_swo_bandwidth()
    # детальна версія
    fig_d_itm_packet()
    fig_d_swo_encoding()
    fig_d_dwt_registers()
    fig_d_host_tools()
    print("OK: figures written to", OUT)
