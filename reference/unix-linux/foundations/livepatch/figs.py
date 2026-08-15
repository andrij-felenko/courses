# -*- coding: utf-8 -*-
"""Фігури до теми «Живе латання ядра: livepatch і модель узгодженості»."""
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


# ── 1. Перенаправлення виклику через гачок на вході функції ────────────────
def fig_redirect():
    W, H = 1240, 620
    f = []

    f.append(fitbox(40, 250, 250, 90,
                    "хтось викликає\nhandle_request()",
                    size=14, fill=BG, stroke=INK))

    f.append(fitbox(340, 240, 280, 110,
                    "перші байти функції:\nгачок ftrace,\nвписаний у код на ходу",
                    size=13, fill=GREY_FILL, stroke=INK))

    f.append(fitbox(680, 230, 300, 130,
                    "спільний обробник livepatch:\nбере верхню латку зі стосу\nй питає стан САМЕ ЦІЄЇ задачі",
                    size=13, fill=BLUE_FILL, stroke=NEG))

    f.append(arrow(292, 295, 336, 295))
    f.append(arrow(622, 295, 676, 295))

    f.append(fitbox(680, 60, 480, 96,
                    "задача ще не перемкнена → стара версія\n(тіло функції в самому ядрі, недоторкане)",
                    size=13, fill=RED_FILL, stroke=POS))
    f.append(fitbox(680, 460, 480, 96,
                    "задача вже перемкнена → нова версія\n(тіло функції в модулі-латці)",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    f.append(arrow(900, 226, 900, 162, color=POS))
    f.append(arrow(900, 364, 900, 456, color=FIELD))

    f.append(fitbox(40, 440, 250, 130,
                    "хто вже всередині\nстарої функції —\nдоходить до кінця:\nїї ніхто не стирає",
                    size=13, fill=GREY_FILL, stroke=MUTED))

    render(os.path.join(IMG, 'redirect.svg'), W, H, *f,
           title="Виклик проходить через гачок ftrace до обробника, який обирає версію за станом задачі")


# ── 2. Небезпечне змішування версій в одній операції ───────────────────────
def fig_mixed_window():
    W, H = 1260, 640
    f = []

    f.append(text(630, 44, "одна задача, одна операція — і мить перемикання посередині",
                  size=15, color=MUTED, bold=True))

    # вісь часу
    f.append(line(70, 300, 1190, 300, color=MUTED, sw=2))
    f.append(text(70, 336, "час →", size=13, color=MUTED, anchor="start"))

    # мить перемикання
    f.append(line(630, 120, 630, 470, color=NEG, sw=2, dash="7,6"))
    f.append(text(630, 106, "тут задачу перемкнули на нову версію", size=13, color=NEG, bold=True))

    f.append(fitbox(120, 170, 400, 96,
                    "увійшла у стару handle_request()\nстара версія наприкінці\nзвільняє об'єкт",
                    size=13, fill=RED_FILL, stroke=POS))
    f.append(arrow(320, 268, 320, 294, color=POS))

    f.append(fitbox(700, 170, 440, 96,
                    "викликала НОВУ use_thing()\nнова версія теж\nзвільняє об'єкт",
                    size=13, fill=GREEN_FILL, stroke=FIELD))
    f.append(arrow(920, 268, 920, 294, color=FIELD))

    f.append(fitbox(700, 350, 440, 110,
                    "повернення у стару handle_request(),\nяка звільняє вдруге:\nподвійне звільнення",
                    size=13, bold=True, fill=RED_FILL, stroke=POS))
    f.append(arrow(920, 322, 920, 346, color=POS))

    f.append(fitbox(90, 500, 1080, 96,
                    "причина одна: стара версія однієї з латаних функцій уже лежала на стеку задачі, "
                    "коли зайшла нова версія іншої",
                    size=14, fill=BG, stroke=INK))

    render(os.path.join(IMG, 'mixed-window.svg'), W, H, *f,
           title="Чому перемикання посеред операції небезпечне: стара версія на стеку зустрічає нову")


# ── 3. Перехід за задачами: три способи зняти прапорець ────────────────────
def fig_transition():
    W, H = 1300, 700
    f = []

    f.append(fitbox(390, 40, 520, 86,
                    "початок переходу:\nпрапорець «ще не перемкнена» — кожній задачі",
                    size=14, bold=True, fill=BLUE_FILL, stroke=NEG))

    f.append(fitbox(50, 210, 380, 140,
                    "задача спить\nнадійно розгорнути її стек;\nжодної латаної функції\nтам немає → перемкнути",
                    size=13, fill=GREEN_FILL, stroke=FIELD))
    f.append(fitbox(460, 210, 380, 140,
                    "задача повертається\nз системного виклику\nчи обробника сигналу\nстек ядра порожній → перемкнути",
                    size=13, fill=GREEN_FILL, stroke=FIELD))
    f.append(fitbox(870, 210, 380, 140,
                    "неробоча задача\nперемикається сама\nперед тим, як ядро процесора\nпіде спати",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    f.append(arrow(560, 130, 240, 204, color=NEG))
    f.append(arrow(650, 130, 650, 204, color=NEG))
    f.append(arrow(740, 130, 1060, 204, color=NEG))

    f.append(fitbox(330, 430, 640, 86,
                    "прапорців не лишилося → перехід завершено,\nвсі задачі бачать один набір версій",
                    size=14, bold=True, fill=BG, stroke=INK))
    f.append(arrow(240, 354, 480, 424, color=FIELD))
    f.append(arrow(650, 354, 650, 424, color=FIELD))
    f.append(arrow(1060, 354, 820, 424, color=FIELD))

    f.append(fitbox(120, 570, 1060, 106,
                    "потік ядра, що спить усередині латаної функції, не перемикається жодним із трьох шляхів:\n"
                    "кожні 15 секунд ядро його будить, а через 15 хвилин пише його ім'я в журнал",
                    size=13, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'transition.svg'), W, H, *f,
           title="Перехід іде задача за задачею; кожна знімає свій прапорець у безпечну для себе мить")


fig_redirect()
fig_mixed_window()
fig_transition()
print("ok")
