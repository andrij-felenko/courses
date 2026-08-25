# -*- coding: utf-8 -*-
"""Фігури до теми «Внесок в апстрим: процес, вимоги, рев'ю»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── 1. Два рахунки зміни ────────────────────────────────────────────────────
def fig_two_bills():
    W, H = 1020, 560
    f = []

    cols = [
        (50, 430, "ЦІНА ПРИЙНЯТТЯ\nувага кількох супровідників, тут і зараз", POS, [
            "лінтери й формат пройдено локально",
            "CI зелений — збірку перевіряти не треба",
            "зміна вузька й про одну тему",
            "опис: задача, як перевіряв, що ламається",
        ]),
        (540, 430, "ЦІНА ВОЛОДІННЯ\nжиття зміни в дереві всі наступні роки", NEG, [
            "інваріанти коду: Facts, плагін прошивки",
            "тести на нову підсистему",
            "рішення узагальнене, а не під один продукт",
            "коміт у форматі, який читає реліз-машина",
        ]),
    ]

    for x, w, head, color, items in cols:
        f.append(fitbox(x, 56, w, 74, head, size=16, bold=True,
                        fill="#ffffff", stroke=color, sw=2.2))
        y = 152
        for it in items:
            f.append(fitbox(x, y, w, 56, it, size=15))
            y += 66

    f.append(fitbox(50, 428, 920, 76,
                    "Обидва рахунки платить не автор зміни, а проєкт.\n"
                    "Тому процес внеску перекладає якомога більше роботи на автора: він один, "
                    "супровідників мало, а зміна лишається назавжди.",
                    size=15, fill="#ffffff", stroke=INK, sw=2))

    render(os.path.join(IMG, 'two-bills.svg'), W, H, *f,
           title="Дві ціни, які проєкт платить за прийняту зміну")


# ── 2. Три кільця перевірки ─────────────────────────────────────────────────
def fig_three_rings():
    W, H = 1080, 440
    f = []

    rings = [
        (40, 290, "ЛОКАЛЬНІ ГАЧКИ\nсекунди, ще до коміту", FIELD,
         "формат і відступи\nзаборонені виклики\nсекрети в коді\nлінт QML і Python"),
        (395, 290, "CI НА П'ЯТЬ ПЛАТФОРМ\nдесятки хвилин, у черзі", NEG,
         "збірка під кожну ОС\nпопередження = помилка\nмодульні тести\nпакування збірок"),
        (750, 290, "РЕВ'Ю ЛЮДИНОЮ\nгодини або доба", POS,
         "чи розв'язує задачу\nчи рішення узагальнене\nчи не росте борг\nчи це взагалі сюди"),
    ]

    for x, w, head, color, catches in rings:
        f.append(fitbox(x, 66, w, 84, head, size=16, bold=True,
                        fill="#ffffff", stroke=color, sw=2.2))
        f.append(fitbox(x, 178, w, 150, catches, size=15))

    f.append(arrow(340, 108, 388, 108))
    f.append(arrow(695, 108, 743, 108))

    f.append(text(540, 372, "Що далі кільце, то дорожчий цикл «помилка → виправлення»",
                  size=15, color=INK, bold=True))
    f.append(text(540, 400, "тому кожне кільце ловить лише те, чого не вміє попереднє",
                  size=14, color=MUTED, italic=True))

    render(os.path.join(IMG, 'three-rings.svg'), W, H, *f,
           title="Три кільця, крізь які проходить зміна")


# ── 3. Текст коміту як вхід машини випуску ──────────────────────────────────
def fig_release_input():
    W, H = 1010, 370
    f = []

    lanes = [
        (70, "коміти у форматі\ntype(scope): опис", "semantic-release\nчитає історію", "номер наступного\nвипуску"),
        (200, "мітки на запиті\nRN: BUGFIX і подібні", "збирач нотаток\nвипуску", "абзац у нотатках\nдля пілотів"),
    ]

    for y, src, mid, dst in lanes:
        f.append(fitbox(40, y, 270, 92, src, size=15, stroke=NEG, sw=2))
        f.append(fitbox(365, y, 270, 92, mid, size=15))
        f.append(fitbox(690, y, 270, 92, dst, size=15, stroke=FIELD, sw=2))
        f.append(arrow(314, y + 46, 361, y + 46))
        f.append(arrow(639, y + 46, 686, y + 46))

    f.append(text(505, 330,
                  "Текст коміту тут не коментар для людей, а вхідні дані машини",
                  size=15, bold=True))

    render(os.path.join(IMG, 'release-input.svg'), W, H, *f,
           title="Куди потрапляє те, що ви написали словами")


# ── 4. Один гачок, два входи (вставка proj-local-gate) ──────────────────────
def fig_hook_two_entries():
    W, H = 1000, 630
    f = []

    f.append(fitbox(50, 56, 380, 76, "git commit\nна машині автора",
                    size=16, bold=True, stroke=NEG, sw=2.2, fill="#ffffff"))
    f.append(fitbox(570, 56, 380, 76, "pull request\nзбірка на сервері",
                    size=16, bold=True, stroke=NEG, sw=2.2, fill="#ffffff"))
    f.append(arrow(240, 136, 240, 174))
    f.append(arrow(760, 136, 760, 174))

    f.append(fitbox(50, 178, 900, 84,
                    "ОДНЕ ВИЗНАЧЕННЯ ГАЧКА — .pre-commit-config.yaml\n"
                    "types: [c++]   ·   exclude: ^(build/|libs/|test/)   ·   pass_filenames: true",
                    size=16, bold=True, stroke=INK, sw=2.4, fill="#ffffff"))
    f.append(arrow(500, 266, 500, 304))

    f.append(fitbox(50, 308, 900, 84,
                    "pre-commit ховає незакомічене й передає шляхи\n"
                    "підготовлених файлів аргументами командного рядка",
                    size=16))
    f.append(arrow(500, 396, 500, 434))

    f.append(fitbox(50, 438, 900, 84,
                    "qgc_guards.py: прибрати коментарі й літерали  →\n"
                    "прогнати правила  →  надрукувати знахідки  →  код повернення",
                    size=16))

    f.append(arrow(500, 526, 260, 556))
    f.append(arrow(500, 526, 740, 556))
    f.append(fitbox(90, 552, 340, 62, "0 — коміт іде далі,\nсерверна перевірка зелена",
                    size=15, stroke=FIELD, sw=2.2, fill="#ffffff"))
    f.append(fitbox(570, 552, 340, 62, "1 — «файл:рядок: правило: що не так»\nі зупинка",
                    size=15, stroke=POS, sw=2.2, fill="#ffffff"))

    render(os.path.join(IMG, 'hook-two-entries.svg'), W, H, *f,
           title="Локальна й серверна перевірки — два входи в одне визначення")


if __name__ == '__main__':
    fig_two_bills()
    fig_three_rings()
    fig_release_input()
    fig_hook_two_entries()
    print('ok')
