# -*- coding: utf-8 -*-
"""Фігури до теми «Що взагалі можна робити в обробнику сигналу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

RED_FILL = "#fdecea"
WARM = "#f7f3e8"


def fig_handler_deadlock():
    """Самозаклинювання: обробник чекає на замок, який тримає він же сам."""
    W, H = 1000, 560
    LX, LW = 40, 320          # ліва колонка: звичайний код
    RX, RW = 640, 320         # права колонка: обробник
    g = []

    g.append(text(LX + LW / 2, 20, "звичайний код програми", size=14, bold=True))
    g.append(text(RX + RW / 2, 20, "обробник сигналу", size=14, bold=True))

    g.append(fitbox(LX, 34, LW, 44, "код кличе malloc()", size=13))
    g.append(arrow(LX + LW / 2, 78, LX + LW / 2, 98))

    g.append(fitbox(LX, 100, LW, 58,
                    "malloc бере замок арени\nі перечіпляє список вільних блоків",
                    size=13, fill=WARM))
    g.append(arrow(LX + LW / 2, 158, LX + LW / 2, 178))

    g.append(fitbox(LX, 180, LW + 600, 44,
                    "рівно в цю мить ядро доставляє сигнал", size=14, fill="#eef2f7"))
    g.append(arrow(500, 224, RX + RW / 2, 248))

    g.append(fitbox(RX, 250, RW, 58,
                    "ядро кладе кадр обробника\nна той самий стек того ж потоку",
                    size=13))
    g.append(arrow(RX + RW / 2, 308, RX + RW / 2, 328))

    g.append(fitbox(RX, 330, RW, 58,
                    "обробник кличе printf(),\nа той усередині кличе malloc()",
                    size=13))
    g.append(arrow(RX + RW / 2, 388, RX + RW / 2, 408))

    g.append(fitbox(RX, 410, RW, 58,
                    "malloc бере ТОЙ САМИЙ замок —\nа він уже зайнятий", size=13,
                    fill=WARM))
    g.append(arrow(RX + RW / 2, 468, RX + RW / 2, 486))

    g.append(text(500, 476, "глухий кут", size=14, bold=True, color=POS))

    g.append(fitbox(RX, 488, RW, 56,
                    "обробник стоїть\nі чекає на звільнення замка",
                    size=13, fill=RED_FILL, stroke=POS))
    g.append(fitbox(LX, 488, LW, 56,
                    "код відпустить замок лише\nпісля повернення з обробника",
                    size=13, fill=RED_FILL, stroke=POS))
    g.append(line(LX + LW + 8, 516, RX - 8, 516, color=POS, sw=2, dash="6,5"))

    render(os.path.join(IMG, 'handler-deadlock.svg'), W, H, *g)


def fig_what_is_shared():
    """Що в обробника своє, а що спільне на весь процес."""
    W, H = 1020, 470
    LX, LW = 40, 420
    RX, RW = 560, 420
    g = []

    g.append(text(LX + LW / 2, 22, "своє — обробник має на це право", size=14,
                  bold=True, color=FIELD))
    g.append(text(RX + RW / 2, 22, "спільне на весь процес — чіпати не можна",
                  size=14, bold=True, color=POS))

    left = [
        "власний кадр на стеку:\nлокальні змінні обробника",
        "об'єкти volatile sig_atomic_t:\nзапис — один неподільний крок",
        "лок-фрі атоміки C11:\nбез замка всередині",
        "тонкі обгортки над системними викликами:\nwrite, read, kill, sigaction, _exit",
    ]
    right = [
        "арена аллокатора:\nзамок і списки вільних блоків",
        "буфери stdio та їхні замки:\nprintf, fputs, fflush",
        "локаль, таблиці часових поясів,\nстан розв'язувача імен",
        "таблиці динамічного завантажувача,\nвнутрішній стан бібліотек",
    ]

    y = 40
    for a, b in zip(left, right):
        g.append(fitbox(LX, y, LW, 62, a, size=13, fill="#eef7ef", stroke=FIELD))
        g.append(fitbox(RX, y, RW, 62, b, size=13, fill=RED_FILL, stroke=POS))
        y += 74

    g.append(fitbox(LX, y + 10, RX + RW - LX, 66,
                    "errno — окреме на кожен потік, але спільне з перерваним кадром:\n"
                    "обробник зобов'язаний зберегти його на вході й відновити перед виходом",
                    size=13, fill=WARM, stroke=MUTED))

    render(os.path.join(IMG, 'what-is-shared.svg'), W, H, *g)


def fig_signal_to_event():
    """Самоканал: сигнал перетворено на звичайну готовність дескриптора."""
    W, H = 1060, 430
    g = []

    g.append(fitbox(30, 60, 240, 84,
                    "ядро доставляє сигнал\nодному з потоків процесу", size=13))
    g.append(arrow(272, 102, 302, 102))

    g.append(fitbox(304, 60, 260, 84,
                    "обробник:\nзберегти errno →\nwrite(запис, 1 байт) →\nвідновити errno",
                    size=13, fill="#eef7ef", stroke=FIELD))
    g.append(arrow(566, 102, 596, 102))

    g.append(fitbox(598, 60, 190, 84,
                    "канал:\nбайт лежить\nі чекає", size=13, fill=WARM))
    g.append(arrow(790, 102, 820, 102))

    g.append(fitbox(822, 60, 210, 84,
                    "poll() бачить\nготовність\nчитального кінця", size=13))

    g.append(arrow(927, 144, 927, 196))

    g.append(fitbox(304, 198, 728, 78,
                    "головний цикл читає байт — і аж тепер робить справжню роботу:\n"
                    "закриває з'єднання, скидає буфери, звільняє пам'ять, виходить",
                    size=14, fill="#eef2f7"))

    g.append(fitbox(304, 320, 260, 82,
                    "тут виконано рівно один\nвиклик зі списку безпечних",
                    size=12, fill=BG, stroke=MUTED, color=MUTED))
    g.append(fitbox(598, 320, 434, 82,
                    "байт не зникне, навіть якщо сигнал прийшов\n"
                    "за мить до входу в poll() —\nсаме це прибирає гонку",
                    size=12, fill=BG, stroke=MUTED, color=MUTED))

    render(os.path.join(IMG, 'signal-to-event.svg'), W, H, *g)


def fig_shutdown_race():
    """Щілина між перевіркою прапорця й входом в очікування — і чому її нема з подією."""
    W, H = 1060, 414
    LX, LW = 20, 150
    XS = [190, 410, 630, 850]
    BW, BH = 190, 88
    g = []

    def row(y, label, cells, marks, note, note_fill, note_stroke):
        g.append(fitbox(LX, y, LW, BH, label, size=14, bold=True, fill=WARM))
        for x, s, hot in zip(XS, cells, marks):
            g.append(fitbox(x, y, BW, BH, s, size=13,
                            fill=RED_FILL if hot else FILL,
                            stroke=POS if hot else LINE))
        for x in XS[:-1]:
            g.append(arrow(x + BW + 4, y + BH / 2, x + BW + 26, y + BH / 2))
        g.append(fitbox(XS[0], y + BH + 14, XS[3] + BW - XS[0], 46, note,
                        size=13, fill=note_fill, stroke=note_stroke))

    row(36, "прапорець\nу пам'яті",
        ["головний цикл\nперевірив прапорець:\nще нуль",
         "сигнал: обробник\nставить одиницю\nсаме тут",
         "цикл входить у poll:\nперевіряти прапорець\nвже пізно",
         "спить, доки не прийде\nклієнт — а він\nможе не прийти"],
        [0, 1, 0, 0],
        "сигнал припав на щілину між перевіркою й очікуванням — і не розбудив нікого",
        RED_FILL, POS)

    row(232, "самоканал\nабо signalfd",
        ["сигнал у будь-яку\nмить: у канал\nлягає байт",
         "цикл входить\nу poll",
         "poll повертається\nнегайно: читальний\nкінець готовий",
         "закрити слухача,\nдописати в польоті,\nвмерти від сигналу"],
        [1, 0, 0, 0],
        "подія не має миті, яку можна проґавити: вона лежить у дескрипторі й чекає",
        "#eef7ef", FIELD)

    render(os.path.join(IMG, 'shutdown-race.svg'), W, H, *g)


if __name__ == '__main__':
    fig_handler_deadlock()
    fig_what_is_shared()
    fig_signal_to_event()
    fig_shutdown_race()
    print("ok")
