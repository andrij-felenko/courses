# -*- coding: utf-8 -*-
"""Фігури до теми «Правка коду ядра на ходу: alternatives, static keys й text_poke»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

GREEN_FILL = "#eaf7ef"
RED_FILL = "#fdecea"
BLUE_FILL = "#eaf0fd"
GREY_FILL = "#f4f6f8"


# ── 1. Заміна на старті: три частини образу і дві долі одного місця ────────
def fig_alternatives():
    W, H = 1180, 560
    f = []

    f.append(text(590, 40, "що лежить у зібраному образі", size=14, color=MUTED, bold=True))

    f.append(fitbox(50, 70, 330, 96,
                    "секція .text\nтипова інструкція + nop-набивка\nдо довжини найдовшого варіанту",
                    size=13, fill=GREY_FILL, stroke=INK))
    f.append(fitbox(430, 70, 320, 96,
                    "секція .altinstructions\nзапис: адреса місця, адреса заміни,\nбіт можливості, обидві довжини",
                    size=13, fill=BLUE_FILL, stroke=NEG))
    f.append(fitbox(800, 70, 330, 96,
                    "секція .altinstr_replacement\nбайти заміни, поза потоком\nвиконання",
                    size=13, fill=GREY_FILL, stroke=INK))

    f.append(arrow(428, 118, 386, 118, color=NEG))
    f.append(arrow(752, 118, 794, 118, color=NEG))

    f.append(fitbox(330, 230, 520, 66,
                    "старт: apply_alternatives() читає таблицю й питає про кожен біт",
                    size=14, bold=True, fill=BG, stroke=INK))
    f.append(arrow(590, 168, 590, 226))

    f.append(fitbox(80, 400, 430, 108,
                    "біта немає\nу .text усе лишається як зібрано:\nтипова інструкція, далі nop-набивка",
                    size=13, fill=RED_FILL, stroke=POS))
    f.append(fitbox(670, 400, 430, 108,
                    "біт є\nбайти заміни скопійовано поверх,\nхвіст добито найшвидшим nop цього CPU",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    f.append(arrow(450, 298, 300, 394, color=POS))
    f.append(arrow(730, 298, 880, 394, color=FIELD))

    render(os.path.join(IMG, 'alternatives.svg'), W, H, *f,
           title="Заміна інструкцій на старті: таблиця, дві секції і дві можливі долі місця")


# ── 2. Протокол int3: три записи й три синхронізації ───────────────────────
def fig_int3_protocol():
    W, H = 1240, 640
    f = []

    CX = 250          # початок ряду комірок
    CW = 78           # ширина комірки
    NX, NW = 690, 500  # права колонка приміток

    f.append(text(250 + 5 * CW / 2, 40, "п'ять байтів за адресою X", size=13, color=MUTED, bold=True))
    f.append(text(NX + NW / 2, 40, "що дістанеться ядру, яке прийшло сюди саме зараз",
                  size=13, color=MUTED, bold=True))

    rows = [
        (70, "до правки", ["0F", "1F", "44", "00", "00"], [GREY_FILL] * 5,
         "цілий п'ятибайтовий nop:\nшвидкий шлях просто проходить крізь нього"),
        (205, "запис 1 байта", ["CC", "1F", "44", "00", "00"], [RED_FILL] + [GREY_FILL] * 4,
         "int3 у першому байті: вхід перекрито,\nядро потрапляє в обробник, а не в код"),
        (340, "запис 4 байтів", ["CC", "2A", "00", "00", "00"], [RED_FILL] + [BLUE_FILL] * 4,
         "хвіст нової інструкції на місці,\nале дійти до нього ніхто не може"),
        (475, "запис 1 байта", ["E9", "2A", "00", "00", "00"], [GREEN_FILL] * 5,
         "цілий jmp: двері відчинено\nодразу на готову нову інструкцію"),
    ]

    for y, label, bytes_, fills, note in rows:
        f.append(fitbox(40, y, 190, 52, label, size=13, bold=True, fill=BG, stroke=INK))
        for i, (b, fl) in enumerate(zip(bytes_, fills)):
            f.append(fitbox(CX + i * CW, y, CW - 6, 52, b, size=15, bold=True,
                            fill=fl, stroke=INK))
        f.append(fitbox(NX, y, NW, 52, note, size=12, fill=BG, stroke=MUTED))

    for y in (140, 275, 410):
        f.append(line(250, y + 20, 250 + 5 * CW - 6, y + 20, color=NEG, sw=1.4, dash="6 4"))
        f.append(text(250 + 5 * CW / 2, y + 12, "IPI на всі ядра: скинути вже вибраний код",
                      size=12, color=NEG))

    f.append(text(620, 600, "між сусідніми станами жодне ядро не бачить напівзаписаної інструкції",
                  size=13, color=INK, italic=True))

    render(os.path.join(IMG, 'int3-protocol.svg'), W, H, *f,
           title="Три записи й три синхронізації: як п'ять байтів міняють під живим ядром")


# ── 3. Хто що переписує і коли ─────────────────────────────────────────────
def fig_consumers():
    W, H = 1260, 580
    f = []

    C1X, C1W = 40, 250
    C2X, C2W = 315, 400
    C3X, C3W = 740, 480

    f.append(text(C1X + C1W / 2, 60, "механізм", size=13, color=MUTED, bold=True))
    f.append(text(C2X + C2W / 2, 60, "що саме переписують", size=13, color=MUTED, bold=True))
    f.append(text(C3X + C3W / 2, 60, "коли це стається", size=13, color=MUTED, bold=True))

    rows = [
        ("alternatives", "байти інструкції на місці", "на старті й на завантаженні модуля", GREY_FILL),
        ("static keys", "п'ятибайтовий nop ⇄ jmp", "рідко, за перемикачем підсистеми", BLUE_FILL),
        ("ftrace", "call __fentry__ ⇄ nop", "на вмиканні трасування, десятки тисяч місць", GREEN_FILL),
        ("static calls", "зміщення в прямому call", "коли міняють ціль виклику", BLUE_FILL),
        ("kprobes", "перший байт інструкції → int3", "на встановленні зонда", RED_FILL),
    ]

    y = 85
    for name, what, when, fill in rows:
        f.append(fitbox(C1X, y, C1W, 58, name, size=14, bold=True, fill=fill, stroke=INK))
        f.append(fitbox(C2X, y, C2W, 58, what, size=13, fill=BG, stroke=MUTED))
        f.append(fitbox(C3X, y, C3W, 58, when, size=13, fill=BG, stroke=MUTED))
        y += 72

    f.append(fitbox(40, 470, 1180, 66,
                    "усе, що міняють на вже запущеному ядрі, проходить через text_poke_bp: "
                    "int3, синхронізація, хвіст, синхронізація, перший байт",
                    size=13, bold=True, fill=GREY_FILL, stroke=INK))
    f.append(arrow(630, 442, 630, 466))

    render(os.path.join(IMG, 'consumers.svg'), W, H, *f,
           title="Один спосіб запису й п'ять різних причин ним скористатися")


if __name__ == '__main__':
    fig_alternatives()
    fig_int3_protocol()
    fig_consumers()
    print("ok")
