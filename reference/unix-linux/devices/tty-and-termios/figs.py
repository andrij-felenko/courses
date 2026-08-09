# -*- coding: utf-8 -*-
"""Фігури до теми «TTY і послідовний порт: модель termios»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_tty_layers():
    """Три шари між дротом і програмою й прапорці, що діють на кожному."""
    W, H = 1000, 660
    g = []

    CX, CW = 310, 380
    boxes = [
        (40,  52, "програма: read() і write()"),
        (160, 52, "ядро tty: черги, буфери, файл /dev/ttyUSB0"),
        (280, 52, "лінійна дисципліна (типово N_TTY)"),
        (400, 52, "драйвер: UART, USB-перехідник або pty"),
        (520, 44, "дріт і залізо"),
    ]

    g.append(text(440, 26, "вхід", size=13, color=NEG, bold=True))
    g.append(text(560, 26, "вихід", size=13, color=POS, bold=True))

    for y, h, s in boxes:
        fill = "#eef2f7" if "дріт" in s or "програма" in s else FILL
        g.append(fitbox(CX, y, CW, h, s, size=14, fill=fill))

    gaps = [(92, 160), (212, 280), (332, 400), (452, 520)]
    for y0, y1 in gaps:
        g.append(arrow(440, y1 - 4, 440, y0 + 4, color=NEG, sw=1.6))
        g.append(arrow(560, y0 + 4, 560, y1 - 4, color=POS, sw=1.6))

    g.append(fitbox(20, 216, 270, 60,
                    "c_lflag: ICANON, ECHO, ISIG —\nзбирати рядок, друкувати назад,\n"
                    "робити з байта сигнал",
                    size=12, fill="#eaf0fd", stroke=NEG))
    g.append(fitbox(20, 340, 270, 52,
                    "c_iflag: ICRNL, IXON, IGNBRK —\nщо зробити з прийнятим байтом",
                    size=12, fill="#eaf0fd", stroke=NEG))
    g.append(fitbox(20, 458, 270, 56,
                    "c_cflag: швидкість, 8N1, парність,\nCRTSCTS, CLOCAL — це вже сам дріт",
                    size=12, fill="#f7f3e8", stroke=MUTED))

    g.append(fitbox(710, 222, 270, 48,
                    "c_oflag: OPOST, ONLCR —\nщо дописати перед відправкою",
                    size=12, fill="#fdecea", stroke=POS))

    g.append(fitbox(30, 584, 940, 52,
                    "лінійну дисципліну міняють викликом ioctl(TIOCSETD): "
                    "N_PPP або N_SLIP роблять із того самого дроту\n"
                    "мережевий інтерфейс — дріт і файл ті самі, інша лише обробка дорогою",
                    size=13, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, 'tty-layers.svg'), W, H, *g,
           title="Шари термінальної підсистеми й прапорці termios")


def fig_canonical_vs_raw():
    """Той самий набір натиснень і два різні результати read()."""
    W, H = 1000, 410
    g = []

    g.append(text(500, 40, "людина набирає", size=13, color=MUTED))

    keys = ["h", "e", "x", "забій", "y", "⏎"]
    KW, KG = 60, 8
    total = len(keys) * KW + (len(keys) - 1) * KG
    x0 = (W - total) / 2
    for i, k in enumerate(keys):
        g.append(fitbox(x0 + i * (KW + KG), 56, KW, 44, k, size=13))

    g.append(arrow(430, 108, 255, 134, color=LINE, sw=1.4))
    g.append(arrow(570, 108, 745, 134, color=LINE, sw=1.4))

    g.append(rect(30, 140, 450, 244, fill=BG, stroke=MUTED, sw=1.2))
    g.append(rect(520, 140, 450, 244, fill=BG, stroke=MUTED, sw=1.2))

    g.append(fitbox(46, 152, 418, 36, "ICANON увімкнено: канонічний режим",
                    size=13, bold=True, fill="#eaf0fd", stroke=NEG))
    g.append(fitbox(46, 196, 418, 40,
                    "read() спить, поки з дроту не прийде переведення рядка",
                    size=12, fill=BG, stroke=MUTED))

    out1 = ["h", "e", "y", "\\n"]
    t1 = len(out1) * 56 + (len(out1) - 1) * 8
    s1 = 255 - t1 / 2
    for i, b in enumerate(out1):
        g.append(fitbox(s1 + i * 64, 246, 56, 38, b, size=13, fill="#eef2f7"))
    g.append(text(255, 302, "один read() повертає 4 байти", size=12, color=MUTED))

    g.append(fitbox(46, 314, 418, 56,
                    "ані x, ані забою серед них немає:\n"
                    "ядро прибрало їх у власному буфері рядка",
                    size=12, fill="#eaf0fd", stroke=NEG))

    g.append(fitbox(536, 152, 418, 36, "ICANON вимкнено: сирий режим",
                    size=13, bold=True, fill="#fdecea", stroke=POS))
    g.append(fitbox(536, 196, 418, 40,
                    "кожен байт будить read(), щойно прийшов з дроту",
                    size=12, fill=BG, stroke=MUTED))

    out2 = ["h", "e", "x", "0x7F", "y", "0x0D"]
    t2 = len(out2) * 62 + (len(out2) - 1) * 6
    s2 = 745 - t2 / 2
    for i, b in enumerate(out2):
        g.append(fitbox(s2 + i * 68, 246, 62, 38, b, size=12, fill="#fdf3f2"))
    g.append(text(745, 302, "шість байтів і стільки ж повернень", size=12, color=MUTED))

    g.append(fitbox(536, 314, 418, 56,
                    "забій приходить звичайним байтом 0x7F;\n"
                    "що з ним робити, вирішує вже програма",
                    size=12, fill="#fdecea", stroke=POS))

    render(os.path.join(IMG, 'canonical-vs-raw.svg'), W, H, *g,
           title="Канонічний і сирий режим на тому самому вводі")


def fig_vmin_vtime():
    """Чотири комбінації VMIN і VTIME."""
    W, H = 1000, 460
    g = []

    g.append(fitbox(190, 56, 380, 36, "VTIME = 0", size=14, bold=True,
                    fill="#eef2f7", stroke=MUTED))
    g.append(fitbox(590, 56, 380, 36, "VTIME > 0", size=14, bold=True,
                    fill="#eef2f7", stroke=MUTED))
    g.append(fitbox(30, 110, 140, 126, "VMIN > 0", size=14, bold=True,
                    fill="#eef2f7", stroke=MUTED))
    g.append(fitbox(30, 250, 140, 126, "VMIN = 0", size=14, bold=True,
                    fill="#eef2f7", stroke=MUTED))

    g.append(fitbox(190, 110, 380, 126,
                    "чекати, доки набереться VMIN байтів.\n"
                    "Таймауту немає зовсім: обірваний\n"
                    "потік вішає read() назавжди.",
                    size=13, fill="#fdecea", stroke=POS))
    g.append(fitbox(590, 110, 380, 126,
                    "VTIME відлічують МІЖ байтами.\n"
                    "Тиша, довша за нього, завершує read():\n"
                    "так ловлять кадр змінної довжини.",
                    size=13, fill="#eaf6ee", stroke=FIELD))
    g.append(fitbox(190, 250, 380, 126,
                    "віддати те, що є в буфері зараз,\n"
                    "і повернутися негайно — навіть\n"
                    "з нулем байтів. Чисте опитування.",
                    size=13, fill=FILL, stroke=MUTED))
    g.append(fitbox(590, 250, 380, 126,
                    "чекати перший байт не довше VTIME.\n"
                    "Не дочекалися — read() поверне 0,\n"
                    "дочекалися — поверне все, що є.",
                    size=13, fill=FILL, stroke=MUTED))

    g.append(fitbox(30, 392, 940, 46,
                    "VTIME міряють десятими частками секунди: найменший таймаут — 100 мс, "
                    "а на 115200 бод\nу ці 100 мс уміщається близько 1150 байтів",
                    size=13, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, 'vmin-vtime.svg'), W, H, *g,
           title="Коли read() повертається: чотири комбінації VMIN і VTIME")


def fig_termios_generations():
    """Три покоління інтерфейсу налаштування термінала: sgtty → termio → termios."""
    W, H = 1060, 440
    g = []

    XS = [140, 365, 590, 815]
    CW = 210
    CENTERS = [x + CW / 2 for x in XS]

    years = ["1975—1979", "1981", "1983", "1988"]
    titles = [
        "Sixth і Seventh\nEdition Unix: sgtty",
        "System III →\nSystem V: termio",
        "4.2BSD: новий\nдрайвер термінала",
        "POSIX.1-1988:\ntermios",
    ]
    howto = [
        "stty() і gtty() — окремі\nсистемні виклики; від V7 —\nioctl(TIOCSETP, &sgttyb)",
        "ioctl(TCSETA, &termio):\nодин виклик замість\nрозсипу окремих команд",
        "ioctl-ів більшає —\nTIOCSETC, TIOCSLTC,\nTIOCLSET, TIOCLBIS",
        "tcsetattr(fd, TCSANOW, &tio)\n— іменована функція,\nпереносні типи tcflag_t",
    ]
    gains = [
        "три режими вводу:\ncooked, cbreak, raw;\nстирання «#», кілл «@»",
        "два режими: канонічний\nі неканонічний, а замість\nмежі рядка — VMIN і VTIME",
        "керування завданнями:\nCtrl+Z, стирання слова,\nповтор набраного рядка",
        "один опис термінала\nна всі Unix; надбання BSD\nвлилися в нього пізніше",
    ]

    g.append(line(140, 48, 1030, 48, color=MUTED, sw=1.5))
    for cx, yr in zip(CENTERS, years):
        g.append(circle(cx, 48, 6, fill=BG, stroke=NEG, sw=2))
        g.append(text(cx, 30, yr, size=14, color=NEG, bold=True))

    for i, x in enumerate(XS):
        g.append(line(CENTERS[i], 54, CENTERS[i], 70, color=MUTED, sw=1.2))
        g.append(fitbox(x, 70, CW, 54, titles[i], size=13, bold=True,
                        fill="#eaf0fd", stroke=NEG))
        g.append(fitbox(x, 146, CW, 76, howto[i], size=12,
                        fill=FILL, stroke=MUTED))
        g.append(fitbox(x, 246, CW, 86, gains[i], size=12,
                        fill=BG, stroke=MUTED))

    g.append(mtext(122, 178, "чим\nналаштовували", size=12, color=MUTED,
                   anchor="end", bold=True))
    g.append(mtext(122, 282, "що покоління\nпринесло", size=12, color=MUTED,
                   anchor="end", bold=True))

    g.append(fitbox(16, 356, 1028, 54,
                    "Жоден набір вимикачів не зникав: cooked став ICANON, raw — викликом cfmakeraw(),\n"
                    "а те, що додав BSD, повернулося в termios уже після стандарту",
                    size=13, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, 'termios-generations.svg'), W, H, *g,
           title="Три покоління інтерфейсу налаштування термінала")


def fig_baud_encoding():
    """Три способи покласти швидкість у termios: поле CBAUD, BOTHER, числовий speed_t."""
    W, H = 1080, 470
    g = []

    def place(x_left, cy, s, size=13, **kw):
        _, w, _ = textbox(0, 0, s, size=size, **kw)
        body, w, h = textbox(x_left + w / 2.0, cy, s, size=size, **kw)
        return body, x_left + w

    def chain(x0, cy, items, gap=42, size=13, fills=None):
        x = x0
        for i, s in enumerate(items):
            kw = {}
            if fills and fills[i]:
                kw['fill'] = fills[i]
            body, x_end = place(x, cy, s, size=size, **kw)
            g.append(body)
            if i < len(items) - 1:
                g.append(arrow(x_end + 8, cy, x_end + gap - 8, cy))
            x = x_end + gap
        return x

    rows = [
        (96,  "POSIX,\nдо glibc 2.42",
         ["c_cflag", "поле CBAUD:\nбіти 0–3 і біт 12", "індекс 0017", "38400 бод"],
         [FILL, FILL, FILL, "#eaf0fd"],
         "Швидкість — не число, а номер рядка в таблиці: доступні лише ті 31 значення, які в ній є"),
        (238, "Linux,\nBOTHER",
         ["CBAUD = BOTHER", "c_ispeed і c_ospeed:\n32-бітні числа", "250000 бод"],
         [FILL, FILL, "#eaf0fd"],
         "Значення BOTHER у полі означає «швидкість не тут»; потрібні struct termios2 і ioctl TCSETS2"),
        (380, "glibc 2.42\nі новіші",
         ["cfsetspeed(&t, 250000)", "speed_t — саме число:\nB115200 == 115200", "250000 бод"],
         [FILL, FILL, "#eaf0fd"],
         "BOTHER і TCSETS2 бібліотека ставить сама — код лишається переносним"),
    ]

    for cy, label, items, fills, note in rows:
        g.append(fitbox(20, cy - 32, 168, 64, label, size=13, bold=True,
                        fill="#eef2f7", stroke=NEG))
        chain(224, cy, items, fills=fills)
        g.append(text(224, cy + 52, note, size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'baud-encoding.svg'), W, H, *g,
           title="Одна швидкість, три способи її записати")


def fig_frame_by_pause():
    """Складання кадру з кількох read(): коротке повернення = пауза = кінець кадру."""
    W, H = 1060, 452
    g = []

    g.append(arrow(150, 58, 1000, 58, color=MUTED, sw=1.2))
    g.append(text(1028, 62, "час", size=12, color=MUTED))

    g.append(mtext(126, 110, ["байти", "на дроті"], size=13, color=MUTED,
                   anchor="end", bold=True))
    g.append(mtext(126, 218, ["read()", "повертає"], size=13, color=MUTED,
                   anchor="end", bold=True))
    g.append(mtext(126, 322, ["висновок", "програми"], size=13, color=MUTED,
                   anchor="end", bold=True))

    g.append(fitbox(150, 92, 300, 48, "кадр A — 303 байти", size=13, fill="#eef2f7"))
    g.append(fitbox(640, 92, 300, 48, "кадр B", size=13, fill="#eef2f7"))
    g.append(text(545, 82, "пауза > VTIME", size=13, color=POS, bold=True))
    g.append(arrow(545, 116, 458, 116, color=POS, sw=1.6))
    g.append(arrow(545, 116, 632, 116, color=POS, sw=1.6))

    g.append(fitbox(150, 200, 127, 48, "128", size=13, fill=FILL))
    g.append(fitbox(277, 200, 127, 48, "128", size=13, fill=FILL))
    g.append(fitbox(404, 200, 196, 48, "47", size=13, fill="#fdecea", stroke=POS))
    g.append(fitbox(600, 200, 167, 48, "чекає, тоді 128", size=12,
                    fill=BG, stroke=MUTED))

    g.append(fitbox(150, 306, 254, 44, "рівно VMIN —\nкадр ще триває",
                    size=12, fill=BG, stroke=MUTED))
    g.append(fitbox(404, 306, 196, 44, "менше за VMIN —\nкадр цілий",
                    size=12, fill="#fdecea", stroke=POS))
    g.append(fitbox(600, 306, 167, 44, "почався\nнаступний", size=12,
                    fill=BG, stroke=MUTED))

    g.append(fitbox(150, 382, 860, 48,
                    "VMIN = 128, VTIME = 1 (100 мс). Кінець кадру видно з одного: "
                    "read() повернув МЕНШЕ\nза VMIN, тобто спрацював міжбайтовий таймер, "
                    "а не набралося замовлене число байтів",
                    size=13, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, 'frame-by-pause.svg'), W, H, *g,
           title="Кадр змінної довжини з кількох read()")


if __name__ == '__main__':
    fig_tty_layers()
    fig_canonical_vs_raw()
    fig_vmin_vtime()
    fig_termios_generations()
    fig_baud_encoding()
    fig_frame_by_pause()
    print("ok")
