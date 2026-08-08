# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
WARM = "#b8860b"


# ── 1. Цикл розбору: точка відліку, крок, виходи ─────────────────────────────
def fig_walk_loop():
    W, H = 1120, 780
    p = []

    origins = [
        (40, "шлях починається з «/»\nвідлік — корінь процесу"),
        (395, "шлях без «/» спереду\nвідлік — поточний каталог"),
        (750, "виклик із дескриптором\nвідлік — той каталог"),
    ]
    for x, label in origins:
        p.append(fitbox(x, 60, 330, 76, label, size=14, fill=BLUE_FILL, stroke=NEG))

    steps = [
        (190, 70, "поточний каталог обходу", GREEN_FILL, FIELD, True),
        (290, 64, "відрізати складник до найближчої «/»", FILL, LINE, False),
        (384, 64, "право на пошук (x) у цьому каталозі?", FILL, LINE, False),
        (478, 64, "знайти складник у таблиці імен", FILL, LINE, False),
        (572, 76, "куди веде знайдене?", WARM_FILL, WARM, False),
    ]
    for y, h, label, fill, stroke, bold in steps:
        p.append(fitbox(330, y, 460, h, label, size=14, fill=fill, stroke=stroke, bold=bold))

    p.append(arrow(205, 140, 430, 186))
    p.append(arrow(560, 140, 560, 186))
    p.append(arrow(915, 140, 690, 186))

    for a, b in ((260, 290), (354, 384), (448, 478), (542, 572)):
        p.append(arrow(560, a, 560, b - 4))

    # петля: назад до поточного каталогу
    p.append(line(330, 610, 280, 610))
    p.append(line(280, 610, 280, 225))
    p.append(arrow(280, 225, 326, 225))
    p.append(text(160, 400, "наступний складник", size=13, color=MUTED))

    p.append(fitbox(820, 372, 270, 128,
                    "зупинка з помилкою:\n"
                    "ENOENT — імені немає\n"
                    "ENOTDIR — це не каталог\n"
                    "EACCES — немає права x\n"
                    "ELOOP — забагато переходів",
                    size=13, fill=RED_FILL, stroke=POS))
    p.append(fitbox(820, 546, 270, 104,
                    "складників більше немає:\n"
                    "знайдений об'єкт\n"
                    "віддано викликові",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(794, 416, 816, 404))
    p.append(arrow(794, 510, 816, 436))
    p.append(arrow(794, 600, 816, 468))
    p.append(arrow(794, 628, 816, 592))

    p.append(fitbox(120, 676, 880, 76,
                    "жоден крок не бачить шляху цілком: ядро щоразу питає одне —\n"
                    "«який номер відповідає цьому імені в цьому каталозі»",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    render(os.path.join(IMG, 'walk-loop.svg'), W, H, *p,
           title="Розбір шляху — цикл із одного питання")


# ── 2. Стек відкладеного залишку на символьному посиланні ────────────────────
def fig_symlink_stack():
    W, H = 1080, 600
    p = []

    panels = [
        (30, "натрапили на посилання",
         "розбираємо /var/log/app/today.log\n"
         "пройдено:  /  →  var  →  log\n"
         "складник app — посилання\n"
         "його вміст:  ../../srv/logs",
         WARM_FILL, WARM),
        (380, "залишок відкладено",
         "стек:  today.log\n"
         "новий залишок:  ../../srv/logs\n"
         "каталог обходу:  /var/log\n"
         "перехід 1 із дозволених 40",
         BLUE_FILL, NEG),
        (730, "залишок повернуто",
         "«..» двічі →  /\n"
         "далі srv, потім logs\n"
         "стек порожній → беремо today.log\n"
         "знайдено inode файлу",
         GREEN_FILL, FIELD),
    ]
    for x, head, body, fill, stroke in panels:
        p.append(fitbox(x, 90, 320, 52, head, size=14, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(x, 156, 320, 190, body, size=13))

    p.append(arrow(356, 250, 374, 250))
    p.append(arrow(706, 250, 724, 250))

    p.append(fitbox(30, 396, 1020, 76,
                    "посилання не веде до файлу — воно підмінює хвіст маршруту:\n"
                    "залишок відкладається, вміст посилання стає новим початком",
                    size=14, fill=WARM_FILL, stroke=WARM))
    p.append(fitbox(30, 496, 1020, 76,
                    "вміст, що починається з «/», скидає обхід на корінь процесу;\n"
                    "сорок підстановок на один розбір — і виклик повертає ELOOP",
                    size=14, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'symlink-stack.svg'), W, H, *p,
           title="Що робить ядро, коли складник виявився посиланням")


# ── 3. Той самий рядок, різні файли ──────────────────────────────────────────
def fig_same_string():
    W, H = 1080, 560
    p = []

    lanes = [
        (110, "процес A\nкорінь = /", "etc → inode 12", "config → inode 340", GREEN_FILL, FIELD),
        (300, "процес B\nкорінь = /srv/box", "etc → inode 77", "config → inode 902", BLUE_FILL, NEG),
    ]
    for y, who, mid, last, fill, stroke in lanes:
        p.append(fitbox(40, y, 250, 90, who, size=14, fill=fill, stroke=stroke))
        p.append(arrow(298, y + 45, 344, y + 45))
        p.append(fitbox(350, y + 12, 280, 66, mid, size=14))
        p.append(arrow(638, y + 45, 684, y + 45))
        p.append(fitbox(690, y + 12, 280, 66, last, size=14, fill=fill, stroke=stroke))

    p.append(text(W / 2, 70, "обидва відкривають рядок  /etc/config", size=15, bold=True))

    p.append(fitbox(40, 434, 930, 82,
                    "рядок однаковий, файл різний: розбір іде в контексті того, хто питає —\n"
                    "його кореня, його поточного каталогу, його дерева монтувань",
                    size=14, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'same-string.svg'), W, H, *p,
           title="Шлях не називає файл сам по собі")


# ── 4. Гонка перейменування ламає лічильник глибини (вставка proj) ───────────
def fig_escape_by_rename():
    W, H = 1140, 706
    p = []

    p.append(fitbox(60, 56, 500, 44, "наша програма: рахує глибину сама",
                    size=15, fill=GREEN_FILL, stroke=FIELD, bold=True))
    p.append(fitbox(620, 56, 460, 44, "нападник: пише у свою теку пісочниці",
                    size=15, fill=RED_FILL, stroke=POS, bold=True))

    p.append(text(30, 98, "час", size=13, color=MUTED))
    p.append(arrow(30, 116, 30, 566, color=MUTED, sw=1.5))

    p.append(fitbox(60, 116, 500, 76,
                    "openat: spool → a → b → c → d\nу руках дескриптор «d», лічильник = 5",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(310, 194, 310, 304))
    p.append(fitbox(620, 212, 460, 76,
                    "rename(«spool/a/b/c/d» → «spool/d»)\nобидві теки його — право на це є",
                    size=14, fill=RED_FILL, stroke=POS))
    p.append(arrow(614, 250, 322, 250, color=POS))
    p.append(fitbox(60, 308, 500, 76,
                    "«..» п'ять разів: 5 → 4 → 3 → 2 → 1 → 0\nжоден крок не викликав заперечень",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(60, 404, 1020, 76,
                    "а «d» лежить уже на глибині 2, тож «..» веде так:\n"
                    "/srv/box/spool → /srv/box → /srv → / → /      "
                    "(корінь пісочниці позаду вже з третього кроку)",
                    size=14, fill=RED_FILL, stroke=POS))
    p.append(fitbox(60, 500, 1020, 62,
                    "далі «etc/passwd» відкривається від справжнього кореня",
                    size=15, fill=RED_FILL, stroke=POS, bold=True))
    p.append(fitbox(60, 596, 1020, 86,
                    "дескриптор пришпилений до inode, а не до місця в дереві;\n"
                    "лічильник описує дерево, яким воно було на попередньому кроці",
                    size=14, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'escape-by-rename.svg'), W, H, *p,
           title="Перевірка меж своїми руками: де відкривається щілина")


# ── 5. RESOLVE_BENEATH проти RESOLVE_IN_ROOT на тій самій втечі (вставка api) ─
def fig_resolve_scopes():
    W, H = 1120, 592
    p = []

    p.append(text(W / 2, 44,
                  "dirfd = /srv/box        шлях = \"link/passwd\"        "
                  "/srv/box/link → /etc",
                  size=15, bold=True))

    panels = [
        (30, "resolve = 0",
         "складник link — посилання\n"
         "його вміст:  /etc\n"
         "риска спереду → корінь процесу\n"
         "обхід уже поза /srv/box",
         "відкрито /etc/passwd\n"
         "саме цієї діри й боялися",
         RED_FILL, POS),
        (400, "RESOLVE_BENEATH",
         "абсолютне посилання\n"
         "відкидається одразу:\n"
         "його ціль не є нащадком\n"
         "каталога dirfd",
         "EXDEV\n"
         "виклик не відбувся",
         WARM_FILL, WARM),
        (770, "RESOLVE_IN_ROOT",
         "риска спереду означає\n"
         "сам dirfd, а не корінь;\n"
         "обхід іде далі, але\n"
         "всередині /srv/box",
         "відкрито\n/srv/box/etc/passwd\n"
         "нема такого → ENOENT",
         GREEN_FILL, FIELD),
    ]
    for x, head, body, result, fill, stroke in panels:
        p.append(fitbox(x, 86, 320, 52, head, size=14, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(x, 152, 320, 190, body, size=13))
        p.append(arrow(x + 160, 348, x + 160, 368))
        p.append(fitbox(x, 374, 320, 84, result, size=13, fill=fill, stroke=stroke))

    p.append(fitbox(30, 486, 1060, 80,
                    "BENEATH відмовляє, IN_ROOT замикає:\n"
                    "перший — для програми, що сама будує шляхи; "
                    "другий — для тієї, що приймає чужі",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    render(os.path.join(IMG, 'resolve-scopes.svg'), W, H, *p,
           title="Дві різні відповіді openat2 на ту саму втечу")


if __name__ == '__main__':
    fig_walk_loop()
    fig_symlink_stack()
    fig_same_string()
    fig_escape_by_rename()
    fig_resolve_scopes()
    print("ok")
