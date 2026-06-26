# -*- coding: utf-8 -*-
"""Фігури до теми «Перетворювач USB↔UART».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Семантика кольорів у цій темі:
USB  = NEG      # бік USB — холодний синій (складний, хостовий)
UART = FIELD    # бік UART — зелений (простий, ніжки МК)
WARN = POS      # пастки, попередження


# ── 1. Дві мови, місток між ними ─────────────────────────────────────────────
def fig_two_worlds():
    W, H = 760, 300
    f = [text(W / 2, 26, "Дві різні мови — і місток між ними", size=16, bold=True)]

    # ПК / USB-хост зліва
    f.append(rect(28, 64, 200, 150, fill=FILL, stroke=USB, sw=1.8))
    f.append(text(128, 90, "ПК — USB-хост", size=13, color=USB, bold=True))
    f.append(line(46, 100, 210, 100, color=USB, sw=1.1))
    for i, s in enumerate(["пакети, кадри 1 мс", "хост опитує пристрій",
                           "адреси, кінцеві точки", "диференційна пара D+/D−"]):
        f.append(text(46, 124 + i * 22, "• " + s, size=10.5, anchor="start"))

    # МК / UART справа
    f.append(rect(532, 64, 200, 150, fill=FILL, stroke=UART, sw=1.8))
    f.append(text(632, 90, "МК — UART", size=13, color=UART, bold=True))
    f.append(line(550, 100, 714, 100, color=UART, sw=1.1))
    for i, s in enumerate(["потік байтів, без пакетів", "обидва шлють, коли хочуть",
                           "немає адрес — точка-точка", "дві лінії TX і RX"]):
        f.append(text(550, 124 + i * 22, "• " + s, size=10.5, anchor="start"))

    # Місток у центрі
    f.append(rect(300, 96, 160, 86, fill="#eef2fb", stroke=INK, sw=2))
    f.append(text(380, 124, "перетворювач", size=12.5, bold=True))
    f.append(text(380, 142, "USB ↔ UART", size=12.5, bold=True))
    f.append(text(380, 166, "перекладач", size=10, color=MUTED, italic=True))

    f.append(arrow(228, 139, 300, 139, color=USB, sw=2))
    f.append(arrow(460, 139, 532, 139, color=UART, sw=2))

    f.append(text(W / 2, 250,
                  "обидва боки не розуміють один одного напряму: один говорить пакетами USB,",
                  size=11))
    f.append(text(W / 2, 270,
                  "другий — рівним потоком байтів. Перетворювач перекладає в обидва боки в реальному часі.",
                  size=11))
    render(os.path.join(IMG, "two-worlds.svg"), W, H, *f)


# ── 2. Що насправді тече по дроту: байт у UART-кадрі ──────────────────────────
def fig_uart_frame():
    W, H = 760, 260
    f = [text(W / 2, 26, "Що тече по лінії UART: один байт у кадрі", size=16, bold=True)]
    f.append(text(W / 2, 46, "приклад: байт 0x53 = 'S' = 0101 0011, передається молодшим бітом уперед",
                  size=11, color=MUTED, italic=True))

    # послідовність бітів: idle, start, 8 data (LSB first), stop
    bits = [("спокій", 1, MUTED), ("старт", 0, WARN),
            ("D0", 1, INK), ("D1", 1, INK), ("D2", 0, INK), ("D3", 0, INK),
            ("D4", 1, INK), ("D5", 0, INK), ("D6", 1, INK), ("D7", 0, INK),
            ("стоп", 1, WARN)]
    x0, y_hi, y_lo = 60, 96, 150
    bw = 58
    prev = 1
    xs = x0
    for i, (lab, b, col) in enumerate(bits):
        yb = y_hi if b else y_lo
        # вертикальний перехід
        if i > 0:
            yp = y_hi if prev else y_lo
            f.append(line(xs, yp, xs, yb, color=INK, sw=2))
        f.append(line(xs, yb, xs + bw, yb, color=INK, sw=2))
        # підпис біта
        f.append(text(xs + bw / 2, y_lo + 30, lab, size=10, color=col,
                      bold=(lab in ("старт", "стоп"))))
        if lab.startswith("D"):
            f.append(text(xs + bw / 2, yb - 8, str(b), size=11, color=NEG, bold=True))
        prev = b
        xs += bw

    # рівні
    f.append(text(x0 - 8, y_hi + 4, "1", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 8, y_lo + 4, "0", size=11, color=MUTED, anchor="end"))

    # дужка тривалості біта
    f.append(line(x0 + bw, y_lo + 44, x0 + 2 * bw, y_lo + 44, color=UART, sw=1.4))
    f.append(text(x0 + 1.5 * bw, y_lo + 58, "1 біт = 1/швидкість", size=9.5,
                  color=UART, italic=True))

    f.append(text(W / 2, 244,
                  "обидва кінці мають заздалегідь знати швидкість — годинника в кадрі немає (тому «асинхронна»)",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "uart-frame.svg"), W, H, *f)


# ── 3. Три способи зробити перетворювач ───────────────────────────────────────
def fig_three_ways():
    W, H = 760, 300
    f = [text(W / 2, 26, "Три способи дати пристрою USB-порт для зв'язку", size=16, bold=True)]

    def card(x, title, col, lines, note):
        f.append(rect(x, 56, 232, 196, fill=FILL, stroke=col, sw=1.8))
        f.append(fitbox(x + 10, 66, 212, 34, title, size=12.5, color=col, bold=True,
                        fill=FILL, stroke="none", sw=0))
        f.append(line(x + 18, 104, x + 214, 104, color=col, sw=1.1))
        yy = 126
        for s in lines:
            f.append(text(x + 18, yy, "• " + s, size=10.5, anchor="start"))
            yy += 21
        f.append(line(x + 18, 214, x + 214, 214, color="#dddddd", sw=1))
        f.append(fitbox(x + 12, 222, 208, 26, note, size=10, color=MUTED, italic=True,
                        fill=FILL, stroke="none", sw=0))

    card(20, "окрема мікросхема-міст", USB,
         ["FT232, CP2102, CH340 …", "МК має лише UART", "міст робить весь USB",
          "+1 чіп на платі"],
         "класика: МК простий, USB — на мості")
    card(264, "USB прямо в мікроконтролері", UART,
         ["МК має USB-блок", "клас CDC у прошивці", "віртуальний COM-порт",
          "0 зайвих чіпів"],
         "сучасно: міст не потрібен зовсім")
    card(508, "готовий модуль / кабель", INK,
         ["USB-UART «свисток»", "плата налагодження", "для столу й макета",
          "не для серійної плати"],
         "найшвидше для проби й діагностики")

    render(os.path.join(IMG, "three-ways.svg"), W, H, *f)


# ── 4. Драйвери: CDC проти власного ──────────────────────────────────────────
def fig_drivers():
    W, H = 760, 274
    f = [text(W / 2, 26, "Драйвер на боці ПК: вбудований чи свій", size=16, bold=True)]

    # CDC ліворуч
    f.append(rect(28, 56, 330, 180, fill="#eef6ef", stroke=UART, sw=1.8))
    f.append(text(193, 82, "клас CDC-ACM (стандарт USB)", size=12.5, color="#1d7a44", bold=True))
    f.append(line(48, 94, 338, 94, color=UART, sw=1.1))
    for i, s in enumerate(["пристрій каже «я серійний порт»",
                           "драйвер уже є у Windows / macOS / Linux",
                           "вставив — і одразу новий COM-порт",
                           "нічого не встановлювати"]):
        f.append(text(48, 118 + i * 26, "• " + s, size=11, anchor="start"))
    f.append(text(193, 224, "шлях найменшого тертя", size=10, color=MUTED, italic=True))

    # власний драйвер праворуч
    f.append(rect(402, 56, 330, 180, fill="#fdeeec", stroke=WARN, sw=1.8))
    f.append(text(567, 82, "власний клас (FTDI, Prolific)", size=12.5, color=WARN, bold=True))
    f.append(line(422, 94, 712, 94, color=WARN, sw=1.1))
    for i, s in enumerate(["пристрій нестандартний для ОС",
                           "потрібен драйвер виробника",
                           "версія, підпис, сумісність ОС",
                           "є чим керувати тонко (швидкості, GPIO)"]):
        f.append(text(422, 118 + i * 26, "• " + s, size=11, anchor="start"))
    f.append(text(567, 224, "більше можливостей, але й більше клопоту", size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "drivers.svg"), W, H, *f)


# ── 5. Хто кого живить і де землю різати ──────────────────────────────────────
def fig_wiring():
    W, H = 760, 320
    f = [text(W / 2, 26, "Підключення: TX↔RX навхрест, спільна земля, обережно з 5 В", size=15, bold=True)]

    # міст / USB-бік
    f.append(rect(60, 80, 180, 150, fill=FILL, stroke=USB, sw=1.8))
    f.append(text(150, 104, "міст USB↔UART", size=12.5, color=USB, bold=True))
    f.append(text(150, 124, "(або USB-свисток)", size=9.5, color=MUTED, italic=True))
    f.append(text(80, 156, "TX", size=12, color=INK, anchor="start", bold=True))
    f.append(text(80, 186, "RX", size=12, color=INK, anchor="start", bold=True))
    f.append(text(80, 216, "GND", size=12, color=INK, anchor="start", bold=True))

    # МК-бік
    f.append(rect(520, 80, 180, 150, fill=FILL, stroke=UART, sw=1.8))
    f.append(text(610, 104, "мікроконтролер", size=12.5, color=UART, bold=True))
    f.append(text(610, 124, "(3.3 В логіка)", size=9.5, color=MUTED, italic=True))
    f.append(text(680, 156, "RX", size=12, color=INK, anchor="end", bold=True))
    f.append(text(680, 186, "TX", size=12, color=INK, anchor="end", bold=True))
    f.append(text(680, 216, "GND", size=12, color=INK, anchor="end", bold=True))

    # навхрест: TX міст -> RX МК
    f.append(line(120, 152, 300, 152, color=INK, sw=2))
    f.append(line(300, 152, 460, 182, color=INK, sw=2))
    f.append(arrow(460, 182, 638, 182, color=INK, sw=2))
    # TX МК -> RX міст
    f.append(line(638, 152, 460, 152, color=INK, sw=2))
    f.append(line(460, 152, 300, 182, color=INK, sw=2))
    f.append(arrow(300, 182, 122, 182, color=INK, sw=2))
    f.append(text(380, 144, "TX → RX", size=10, color=MUTED, italic=True))
    f.append(text(380, 200, "RX ← TX", size=10, color=MUTED, italic=True))

    # земля спільна
    f.append(line(122, 212, 678, 212, color=WARN, sw=2))
    f.append(text(380, 230, "спільна земля — обов'язково", size=10.5, color=WARN, bold=True))

    f.append(textbox(380, 276,
                     ["Дві часті помилки: з'єднати TX↔TX (тиша) і забути спільну землю.",
                      "Міст 5 В, а МК 3.3 В → на лінії RX МК потрібен перетворювач рівнів."],
                     size=10.5, color=INK, fill="#fdeeec", stroke=WARN, sw=1.3)[0])
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 6. Швидкість: дроселить не дріт, а пакування ──────────────────────────────
def fig_latency():
    W, H = 760, 280
    f = [text(W / 2, 26, "Чому «швидкий» USB не означає миттєвий байт", size=16, bold=True)]

    # шкала часу
    y = 110
    f.append(line(60, y, 700, y, color=MUTED, sw=1.2))
    # USB опитує раз на 1 мс
    for k in range(7):
        x = 90 + k * 95
        f.append(line(x, y - 8, x, y + 8, color=USB, sw=1.6))
        f.append(text(x, y + 24, "%d мс" % k, size=9.5, color=MUTED))
    f.append(text(380, y - 22, "хост опитує пристрій кадрами по 1 мс", size=11, color=USB, bold=True))

    # один байт чекає до наступного опитування
    f.append(circle(120, y, 5, fill=UART, stroke=UART, sw=1))
    f.append(text(120, y - 14, "байт готовий", size=9, color=UART))
    f.append(arrow(120, y + 38, 185, y + 38, color=WARN, sw=1.6))
    f.append(text(155, y + 54, "чекає ≤ 1 мс", size=9.5, color=WARN, italic=True))

    f.append(textbox(380, 218,
                     ["Пропускна здатність USB величезна, але байти він возить пачками раз на ~1 мс.",
                      "Одинокий байт може почекати майже мілісекунду до відправлення.",
                      "Тому в команді-відповіді важлива не «швидкість USB», а ця затримка пакування —",
                      "і вона ж робить точні паузи між байтами на боці ПК ненадійними."],
                     size=10.5, color=INK, fill=FILL, stroke=MUTED, sw=1.2)[0])
    render(os.path.join(IMG, "latency.svg"), W, H, *f)


# ── 7. Шлях прийому: ISR → кільцевий буфер → стейт-машина ────────────────────
def fig_framing_rxpath():
    W, H = 780, 300
    f = [text(W / 2, 26, "Прийом без втрат: швидкий ISR, повільний розбір — через кільцевий буфер",
              size=14.5, bold=True)]

    # лінія UART зліва
    f.append(rect(24, 96, 118, 70, fill=FILL, stroke=UART, sw=1.8))
    f.append(mtext(83, 124, ["лінія UART", "байти пачкою", "після пакування"],
                   size=10.5, color=UART))

    # ISR — короткий, у перерваннях
    f.append(rect(180, 96, 150, 70, fill="#eef2fb", stroke=USB, sw=1.8))
    f.append(text(255, 120, "ISR прийому", size=12, color=USB, bold=True))
    f.append(mtext(255, 140, ["забрав байт →", "поклав у буфер"], size=10, color=INK))

    # кільцевий буфер — серце
    f.append(circle(440, 131, 52, fill="#f0fbf3", stroke=FIELD, sw=2))
    f.append(text(440, 110, "кільцевий", size=11, color=FIELD, bold=True))
    f.append(text(440, 126, "буфер", size=11, color=FIELD, bold=True))
    f.append(text(440, 146, "head→ ←tail", size=10, color=MUTED))
    # дві стрілки по колу (запис / читання)
    f.append(arrow(440, 79, 462, 86, color=USB, sw=1.6))
    f.append(arrow(462, 176, 440, 183, color=INK, sw=1.6))

    # стейт-машина — споживач
    f.append(rect(560, 96, 196, 70, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(658, 120, "стейт-машина кадру", size=11.5, bold=True))
    f.append(mtext(658, 140, ["бере байт, коли є", "час; складає кадр"],
                   size=10, color=INK))

    # потокові стрілки
    f.append(arrow(142, 131, 178, 131, color=LINE, sw=1.8))
    f.append(arrow(332, 131, 386, 131, color=LINE, sw=1.8))
    f.append(arrow(494, 131, 558, 131, color=LINE, sw=1.8))

    f.append(textbox(W / 2, 232,
                     ["ISR мусить бути коротким: забрати байт і покласти в буфер — більше нічого.",
                      "Кільцевий буфер розв'язує швидкий прийом і повільний розбір: байти не губляться,",
                      "поки головний цикл зайнятий. Саме ця розв'язка рятує від нерівного, пачкового",
                      "припливу байтів, який лишає по собі USB-міст."],
                     size=10.5, color=INK, fill=FILL, stroke=MUTED, sw=1.2)[0])
    render(os.path.join(IMG, "rxpath.svg"), W, H, *f)


# ── 8. Стейт-машина складання кадру ──────────────────────────────────────────
def fig_framing_fsm():
    W, H = 780, 330
    f = [text(W / 2, 26, "Стейт-машина кадру [SYNC][LEN][дані…][CRC] — по одному байту",
              size=14.5, bold=True)]

    sx = [60, 240, 430, 620]
    sy = 96
    sw_ = 130
    sh = 58
    states = [("чекати SYNC", "відкидати, доки\nне 0xAA"),
              ("читати LEN", "узяти довжину,\nперевірити стелю"),
              ("збирати дані", "n байтів за\nлічильником"),
              ("читати CRC", "звірити —\nкадр готовий")]
    cols = [WARN, USB, FIELD, INK]
    for i, (title, sub) in enumerate(states):
        f.append(rect(sx[i], sy, sw_, sh, fill=FILL, stroke=cols[i], sw=1.8))
        f.append(text(sx[i] + sw_ / 2, sy + 21, title, size=11.5, color=cols[i], bold=True))
        f.append(mtext(sx[i] + sw_ / 2, sy + 37, sub, size=9, color=INK, lh=1.15))
        if i < 3:
            f.append(arrow(sx[i] + sw_, sy + sh / 2, sx[i + 1], sy + sh / 2,
                           color=LINE, sw=1.8))

    # підписи переходів
    f.append(text((sx[0] + sw_ + sx[1]) / 2, sy - 6, "0xAA", size=9.5, color=MUTED, italic=True))
    f.append(text((sx[1] + sw_ + sx[2]) / 2, sy - 6, "len ≤ MAX", size=9.5, color=MUTED, italic=True))
    f.append(text((sx[2] + sw_ + sx[3]) / 2, sy - 6, "усі дані", size=9.5, color=MUTED, italic=True))

    # повернення на старт після CRC
    f.append(line(sx[3] + sw_ / 2, sy + sh, sx[3] + sw_ / 2, sy + sh + 26, color=INK, sw=1.4))
    f.append(line(sx[3] + sw_ / 2, sy + sh + 26, sx[0] + sw_ / 2, sy + sh + 26, color=INK, sw=1.4))
    f.append(arrow(sx[0] + sw_ / 2, sy + sh + 26, sx[0] + sw_ / 2, sy + sh, color=INK, sw=1.6))
    f.append(text(W / 2, sy + sh + 44, "кадр оброблено (чи відкинуто) → знову чекати SYNC",
                  size=10, color=INK, italic=True))

    # дві аварійні гілки повернення
    f.append(line(sx[1] + sw_ / 2, sy, sx[1] + sw_ / 2, sy - 30, color=WARN, sw=1.3, dash="4,3"))
    f.append(line(sx[1] + sw_ / 2, sy - 30, sx[0] + sw_ / 2, sy - 30, color=WARN, sw=1.3, dash="4,3"))
    f.append(arrow(sx[0] + sw_ / 2, sy - 30, sx[0] + sw_ / 2, sy, color=WARN, sw=1.4))
    f.append(text((sx[0] + sx[1]) / 2 + 30, sy - 36, "LEN завелика → скид", size=9, color=WARN, italic=True))

    f.append(textbox(W / 2, sy + sh + 92,
                     ["Стан і лічильники живуть МІЖ викликами, тож кадр збирається по байту, не блокуючи МК.",
                      "Кожен прийнятий байт зсуває автомат на один крок; межі задає поле довжини, а не пауза.",
                      "Хибна довжина чи провал CRC не валять зв'язок — автомат вертається чекати наступний SYNC."],
                     size=10.5, color=INK, fill=FILL, stroke=MUTED, sw=1.2)[0])
    render(os.path.join(IMG, "frame-fsm.svg"), W, H, *f)


# ── 9. Хроніка: чіпи-мости й війна за драйвер (вставка hist) ──────────────────
def fig_bridge_timeline():
    W, H = 760, 300
    f = [text(W / 2, 26, "Чіпи-мости й війна за драйвер: коротка хроніка", size=16, bold=True)]

    y = 122
    f.append(line(56, y, 704, y, color=MUTED, sw=1.4))

    marks = [
        (1992, ["FTDI заснована", "у Глазго"], True, USB),
        (1999, ["FT8U232AM —", "перший чіп-міст"], False, UART),
        (2014, ["драйвер 2.12.0.0", "цеглить підробки"], True, WARN),
        (2016, ['"NON GENUINE', 'DEVICE FOUND!"'], False, WARN),
        (2023, ["Prolific відмовляє", "клонам у Win11"], True, USB),
    ]
    xs = [96, 248, 430, 562, 676]
    for (yr, lines, up, col), x in zip(marks, xs):
        f.append(circle(x, y, 6, fill=col, stroke=col, sw=1))
        f.append(text(x, (y - 18) if up else (y + 28), str(yr), size=12, color=col, bold=True))
        ty = y - 58 if up else y + 46
        for i, ln in enumerate(lines):
            f.append(text(x, ty + i * 15, ln, size=9.5, color=INK))

    f.append(textbox(W / 2, 252,
                     ["Мова між ПК і пристроєм — це не лише дроти, а й драйвер на боці ОС.",
                      "Хто володіє драйвером, той зрештою володіє пристроєм — головний урок історії."],
                     size=10.5, color=INK, fill=FILL, stroke=MUTED, sw=1.2)[0])
    render(os.path.join(IMG, "bridge-timeline.svg"), W, H, *f)


# ── 10. Два способи покарати клон: цегла проти відмови (вставка hist) ─────────
def fig_brick_vs_refuse():
    W, H = 760, 308
    f = [text(W / 2, 26, "Два способи покарати клон: цегла проти відмови", size=16, bold=True)]

    # FTDI — деструктивно
    f.append(rect(28, 56, 340, 196, fill="#fdeeec", stroke=WARN, sw=1.8))
    f.append(text(198, 82, "FTDI, 2014 — деструктивно", size=12.5, color=WARN, bold=True))
    f.append(line(48, 94, 348, 94, color=WARN, sw=1.1))
    for i, s in enumerate(["драйвер перезаписує PID у чіпі",
                           "0x6001 → 0x0000 у НЕЛЕТКІЙ памʼяті",
                           "слід лишається в самому пристрої",
                           "не впізнається на ЖОДНІЙ ОС потім"]):
        f.append(text(48, 120 + i * 26, "• " + s, size=10.5, anchor="start"))
    f.append(text(198, 240, "рятує лише зворотний перезапис PID", size=9.5, color=MUTED, italic=True))

    # Prolific — мʼякше
    f.append(rect(392, 56, 340, 196, fill="#eef6ef", stroke=UART, sw=1.8))
    f.append(text(562, 82, "Prolific — лише відмова", size=12.5, color="#1d7a44", bold=True))
    f.append(line(412, 94, 712, 94, color=UART, sw=1.1))
    for i, s in enumerate(["драйвер просто не запускається",
                           '«Code 10» — і все, чіп цілий',
                           "нелетку памʼять НЕ чіпає",
                           "лікується відкатом драйвера"]):
        f.append(text(412, 120 + i * 26, "• " + s, size=10.5, anchor="start"))
    f.append(text(562, 240, "та сама мета, мʼякший засіб", size=9.5, color=MUTED, italic=True))

    f.append(text(W / 2, 286,
                  "Спільний мотив — убити клон; різниця в тому, чи лишається пристрій живим після покари.",
                  size=10.5, color=INK))
    render(os.path.join(IMG, "brick-vs-refuse.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_worlds()
    fig_uart_frame()
    fig_three_ways()
    fig_drivers()
    fig_wiring()
    fig_latency()
    fig_framing_rxpath()
    fig_framing_fsm()
    fig_bridge_timeline()
    fig_brick_vs_refuse()
    print("OK: 10 figures ->", IMG)
