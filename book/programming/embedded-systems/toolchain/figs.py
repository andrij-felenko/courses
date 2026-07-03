# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Тулчейн як конвеєр окремих інструментів ─────────────────────────────
def fig_pipeline():
    W, H = 760, 300
    frags = []
    frags.append(text(W/2, 26, "Тулчейн: ланцюг окремих інструментів", size=17, bold=True))

    # вхідні файли (кілька .c)
    frags.append(fitbox(30, 70, 96, 46, ".c\n.c  .c", size=13, fill="#eef2ff", stroke=NEG, bold=True))
    frags.append(text(78, 132, "ваш код +\nбібліотеки", size=11, color=MUTED))

    stages = [
        (170, "компі-\nлятор", "перекладає\nC → команди"),
        (330, "асем-\nблер", "команди →\nчисла (.o)"),
        (490, "лінкер", "зшиває все,\nдає адреси"),
    ]
    for x, name, sub in stages:
        frags.append(fitbox(x-58, 78, 116, 42, name, size=14, bold=True))
        frags.append(text(x, 138, sub, size=11, color=MUTED))

    # вихід
    frags.append(fitbox(628, 78, 108, 42, ".elf →\n.bin", size=13, fill="#eafaf1", stroke=FIELD, bold=True))
    frags.append(text(682, 138, "образ\nдля Flash", size=11, color=MUTED))

    # стрілки
    xs = [126, 254, 414, 574]
    for x in xs:
        frags.append(arrow(x, 99, x+42, 99))

    # рамка «драйвер збірки» знизу
    frags.append(rect(150, 190, 456, 74, fill="#fff7ed", stroke=POS, sw=1.6, rx=8))
    frags.append(text(378, 214, "драйвер збірки (make / CMake / idf.py)", size=13, bold=True, color=POS))
    frags.append(text(378, 236, "вирішує, ЩО, В ЯКОМУ ПОРЯДКУ і з ЯКИМИ ключами запускати", size=11, color=MUTED))
    frags.append(text(378, 254, "— щоб не кликати кожен інструмент руками", size=11, color=MUTED))
    for x in (200, 330, 490):
        frags.append(line(x, 122, x, 190, color=POS, sw=1, dash="4 3"))

    render(os.path.join(OUT, 'pipeline.svg'), W, H, *frags)


# ── 2. Крос-компіляція: будуємо тут, виконуємо там ─────────────────────────
def fig_cross():
    W, H = 720, 300
    frags = []
    frags.append(text(W/2, 26, "Крос-компіляція: будуємо на ПК — для чипа", size=17, bold=True))

    # ПК
    frags.append(rect(40, 70, 300, 180, fill="#eef2ff", stroke=NEG, sw=1.8, rx=10))
    frags.append(text(190, 96, "ПК-«завод»  (ядро x86)", size=14, bold=True, color=NEG))
    frags.append(fitbox(80, 120, 220, 40, "тут ПРАЦЮЄ тулчейн", size=13, bold=True))
    frags.append(text(190, 186, "багато пам'яті й обчислень —", size=11, color=MUTED))
    frags.append(text(190, 204, "збере прошивку за секунди", size=11, color=MUTED))
    frags.append(text(190, 232, "але сам код чипа тут НЕ біжить", size=11, color=POS))

    # МК
    frags.append(rect(430, 70, 250, 180, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(555, 96, "МК  (Xtensa / RISC-V)", size=14, bold=True, color=FIELD))
    frags.append(fitbox(460, 120, 190, 40, "тут ВИКОНУЄТЬСЯ код", size=13, bold=True))
    frags.append(text(555, 186, "лічені кілобайти пам'яті —", size=11, color=MUTED))
    frags.append(text(555, 204, "сам зібрати себе не зміг би", size=11, color=MUTED))
    frags.append(text(555, 232, "біжить готовим машинним кодом", size=11, color=FIELD))

    # стрілка з підписом
    frags.append(arrow(342, 150, 428, 150))
    frags.append(text(385, 140, ".bin", size=12, bold=True))

    render(os.path.join(OUT, 'cross.svg'), W, H, *frags)


# ── 3. Три слова однієї команди: arm-none-eabi-gcc ─────────────────────────
def fig_triplet():
    W, H = 720, 250
    frags = []
    frags.append(text(W/2, 26, "Ім'я команди читається як паспорт цілі", size=17, bold=True))

    frags.append(text(W/2, 70, "arm-none-eabi-gcc", size=26, bold=True))

    parts = [
        (150, "arm", "яке ЯДРО", "архітектура\nкоманд"),
        (312, "none", "який виробник", "не важить\n(порожньо)"),
        (452, "eabi", "яка ОС / ABI", "жодної ОС —\nголе залізо"),
        (600, "gcc", "який ІНСТРУМЕНТ", "компілятор\n(gcc, ld, gdb…)"),
    ]
    for x, word, q, sub in parts:
        frags.append(line(x, 82, x, 118, color=MUTED, sw=1, dash="3 3"))
        frags.append(fitbox(x-66, 118, 132, 36, q, size=12, bold=True))
        frags.append(text(x, 178, sub, size=11, color=MUTED))

    frags.append(text(W/2, 226, "той самий gcc, лише націлений на інший чіп → інша прошивка з того самого коду",
                      size=12, color=INK))
    render(os.path.join(OUT, 'triplet.svg'), W, H, *frags)


fig_pipeline()
fig_cross()
fig_triplet()
print("ok")
