# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff3"
WARM = "#b8860b"


# ── 1. Прапорець лежить в inode, а не на імені ──────────────────────────────
def fig_flag_in_inode():
    W, H = 1340, 700

    p = [text(W / 2, 44, "прапорець лежить в inode — тому обидва імені захищено однаково",
              size=18, bold=True, color=INK)]

    # два каталоги ліворуч
    DX, DW, DH = 60, 330, 120
    p.append(fitbox(DX, 150, DW, DH,
                    ["каталог /etc", "рядок таблиці:", "resolv.conf → inode 128"],
                    size=14, pad=12, fill=GREY_FILL, stroke=MUTED, sw=1.4))
    p.append(fitbox(DX, 400, DW, DH,
                    ["каталог /var/backups", "рядок таблиці:", "resolv.conf → inode 128"],
                    size=14, pad=12, fill=GREY_FILL, stroke=MUTED, sw=1.4))

    # inode посередині
    IX, IW = 490, 330
    p.append(rect(IX, 130, IW, 430, fill=BG, stroke=INK, sw=2))
    p.append(text(IX + IW / 2, 165, "inode 128", size=16, bold=True, color=INK))

    rows = [
        ("режим  rw-r--r--", BLUE_FILL, NEG, False),
        ("власник  root:root", FILL, MUTED, False),
        ("розмір  82 Б", FILL, MUTED, False),
        ("часи  зміни / доступу", FILL, MUTED, False),
        ("імен на цей вміст: 2", GREEN_FILL, FIELD, False),
        ("прапорці: ----i-------", RED_FILL, POS, True),
    ]
    ry = 190
    for label, fill, stroke, bold in rows:
        p.append(fitbox(IX + 18, ry, IW - 36, 50, [label], size=13.5, pad=10,
                        fill=fill, stroke=stroke, sw=2.0 if bold else 1.2, bold=bold))
        ry += 62

    # стрілки від каталогів до inode
    p.append(arrow(DX + DW + 14, 210, IX - 12, 260, color=MUTED, sw=1.8))
    p.append(arrow(DX + DW + 14, 460, IX - 12, 410, color=MUTED, sw=1.8))

    # виноски праворуч
    NX, NW = 900, 380
    p.append(fitbox(NX, 190, NW, 130,
                    ["біти режиму: «кому вільно»", "власник переписує їх сам,", "нікого не питаючи"],
                    size=14, pad=12, fill=BLUE_FILL, stroke=NEG, sw=1.6))
    p.append(fitbox(NX, 380, NW, 130,
                    ["прапорці: «чи можна взагалі»", "тримають і власника,", "і root без потрібної можливості"],
                    size=14, pad=12, fill=RED_FILL, stroke=POS, sw=1.8))
    p.append(line(IX + IW + 10, 255, NX - 10, 255, color=NEG, sw=1.4, dash="5,4"))
    p.append(line(IX + IW + 10, 445, NX - 10, 445, color=POS, sw=1.4, dash="5,4"))

    # висновок
    p.append(fitbox(60, 600, W - 120, 62,
                    ["rm через будь-яке з двох імен → EPERM: перевірка щоразу дістається того самого inode"],
                    size=15, pad=14, fill=WARM_FILL, stroke=WARM, sw=1.8, bold=True))

    return render(os.path.join(IMG, 'flag-in-inode.svg'), W, H, *p)


# ── 2. Де саме спрацьовує перевірка, а де ні ────────────────────────────────
def fig_where_check_fires():
    LEFT = [
        ("open(…, O_WRONLY) — відкрити на запис", "перевірка права писати в inode"),
        ("unlink / rename — прибрати або перейменувати", "перевірка над жертвою: ловить і «i», і «a»"),
        ("link — створити ще одне жорстке ім'я", "нове ім'я міняє лічильник в самому inode"),
        ("chmod / chown / utimes", "спільний шлях зміни атрибутів inode"),
        ("setxattr — записати розширений атрибут", "запис атрибута — теж зміна об'єкта"),
        ("write через уже відкритий дескриптор", "перевірка в шляху запису: ext4 з 2019, f2fs з 2020"),
        ("запис у відображену в пам'ять сторінку", "не код помилки, а сигнал SIGBUS"),
    ]
    RIGHT = [
        ("read — прочитати вміст", "прапорець про незмінність, не про таємність"),
        ("перейменувати батьківський каталог", "inode не чіпали — просто шлях став іншим"),
        ("змонтувати іншу систему поверх каталогу", "за тим самим шляхом читається інший вміст"),
        ("переформатувати носій", "разом із файловою системою зникає й inode"),
        ("chattr -i з можливістю CAP_LINUX_IMMUTABLE", "хто має право поставити, той має право й зняти"),
    ]

    W, H = 1420, 950
    CW, GAP = 620, 60
    LX = 60
    RX = LX + CW + GAP
    ROW_H, STEP = 76, 92
    TOP = 190

    p = [text(W / 2, 46, "незмінний файл: де операція впирається в заборону, а де проходить",
              size=18, bold=True, color=INK)]

    p.append(fitbox(LX, 110, CW, 54, ["упирається в EPERM"], size=16, pad=12,
                    fill=RED_FILL, stroke=POS, sw=2, bold=True))
    p.append(fitbox(RX, 110, CW, 54, ["проходить безперешкодно"], size=16, pad=12,
                    fill=GREEN_FILL, stroke=FIELD, sw=2, bold=True))

    for i, (op, why) in enumerate(LEFT):
        p.append(fitbox(LX, TOP + i * STEP, CW, ROW_H, [op, why],
                        size=13.5, pad=12, fill=RED_FILL, stroke=POS, sw=1.3))
    for i, (op, why) in enumerate(RIGHT):
        p.append(fitbox(RX, TOP + i * STEP, CW, ROW_H, [op, why],
                        size=13.5, pad=12, fill=GREEN_FILL, stroke=FIELD, sw=1.3))

    p.append(fitbox(LX, 850, W - 2 * LX, 62,
                    ["захищено об'єкт, а не шлях до нього: усе, що не чіпає сам inode, минає перевірку"],
                    size=15, pad=14, fill=WARM_FILL, stroke=WARM, sw=1.8, bold=True))

    return render(os.path.join(IMG, 'where-check-fires.svg'), W, H, *p)


# ── 3. Хто здатен зняти прапорець ───────────────────────────────────────────
def fig_who_can_undo():
    W, H = 1340, 700
    PW = 600
    LX, RX = 60, 60 + 600 + 60

    p = [text(W / 2, 46, "гарантія варта стільки, скільки варта перешкода на шляху до зняття",
              size=18, bold=True, color=INK)]

    p.append(rect(LX, 90, PW, 470, fill=BG, stroke=NEG, sw=2))
    p.append(text(LX + PW / 2, 126, "Linux: усе вирішує можливість", size=16, bold=True, color=NEG))
    p.append(fitbox(LX + 30, 150, PW - 60, 68,
                    ["процес root, можливість CAP_LINUX_IMMUTABLE на місці"],
                    size=13.5, pad=12, fill=FILL, stroke=MUTED, sw=1.2))
    p.append(arrow(LX + PW / 2, 222, LX + PW / 2, 252, color=POS, sw=2))
    p.append(fitbox(LX + 30, 256, PW - 60, 62,
                    ["chattr -i проходить: прапорець знято однією командою"],
                    size=13.5, pad=12, fill=RED_FILL, stroke=POS, sw=1.6))

    p.append(fitbox(LX + 30, 348, PW - 60, 68,
                    ["процес, у якого цю можливість прибрано", "з обмежувальної множини"],
                    size=13.5, pad=12, fill=FILL, stroke=MUTED, sw=1.2))
    p.append(arrow(LX + PW / 2, 420, LX + PW / 2, 450, color=FIELD, sw=2))
    p.append(fitbox(LX + 30, 454, PW - 60, 82,
                    ["chattr -i → EPERM; повернути можливість зсередини не можна —",
                     "лише запуск наново поза цим оточенням"],
                    size=13.5, pad=12, fill=GREEN_FILL, stroke=FIELD, sw=1.6))

    p.append(rect(RX, 90, PW, 470, fill=BG, stroke=WARM, sw=2))
    p.append(text(RX + PW / 2, 126, "4.4BSD: усе вирішує рівень безпеки", size=16, bold=True, color=WARM))
    p.append(fitbox(RX + 30, 150, PW - 60, 68,
                    ["системний прапорець schg, рівень безпеки 0"],
                    size=13.5, pad=12, fill=FILL, stroke=MUTED, sw=1.2))
    p.append(arrow(RX + PW / 2, 222, RX + PW / 2, 252, color=POS, sw=2))
    p.append(fitbox(RX + 30, 256, PW - 60, 62,
                    ["chflags noschg проходить: прапорець знято"],
                    size=13.5, pad=12, fill=RED_FILL, stroke=POS, sw=1.6))

    p.append(fitbox(RX + 30, 348, PW - 60, 68,
                    ["та сама система, рівень безпеки піднято до 1 або вище"],
                    size=13.5, pad=12, fill=FILL, stroke=MUTED, sw=1.2))
    p.append(arrow(RX + PW / 2, 420, RX + PW / 2, 450, color=FIELD, sw=2))
    p.append(fitbox(RX + 30, 454, PW - 60, 82,
                    ["зняти не можна нікому, і знизити рівень теж не можна —",
                     "шлях назад лише через перезавантаження"],
                    size=13.5, pad=12, fill=GREEN_FILL, stroke=FIELD, sw=1.6))

    p.append(fitbox(60, 600, W - 120, 62,
                    ["сам біт скрізь однаковий: різниця не в забороні, а в тому, наскільки важко її погасити"],
                    size=15, pad=14, fill=WARM_FILL, stroke=WARM, sw=1.8, bold=True))

    return render(os.path.join(IMG, 'who-can-undo.svg'), W, H, *p)


# ── 4. Три різні «ні» від ioctl ─────────────────────────────────────────────
def fig_three_refusals():
    W, H = 1300, 660

    p = [text(W / 2, 44, "три різні відмови на той самий ioctl — і три різні висновки",
              size=18, bold=True, color=INK)]

    C1X, C1W = 60, 210
    C2X, C2W = 300, 500
    C3X, C3W = 830, 410

    p.append(text(C1X + C1W / 2, 96, "код помилки", size=14, bold=True, color=MUTED))
    p.append(text(C2X + C2W / 2, 96, "що це насправді означає", size=14, bold=True, color=MUTED))
    p.append(text(C3X + C3W / 2, 96, "що з цим робити", size=14, bold=True, color=MUTED))

    rows = [
        (120, "ENOTTY", GREY_FILL, MUTED,
         ["у ядрі для цієї файлової системи",
          "немає обробника прапорців узагалі,",
          "і ioctl каже «недоречний виклик»"],
         ["робити нічого: тут немає чого",
          "ані прочитати, ані поставити"]),
        (280, "EOPNOTSUPP", WARM_FILL, WARM,
         ["поле є, але цього біта ФС не має —",
          "або ви просите погасити біт,",
          "який гасити не можна (ext4 і extents)"],
         ["звузити прохання: читати-міняти-писати",
          "замість запису всього поля одним числом"]),
        (440, "EPERM", RED_FILL, POS,
         ["поле є, біт є, бракує повноваження:",
          "саме i та a вимагають",
          "можливості CAP_LINUX_IMMUTABLE"],
         ["дати процесові цю можливість —",
          "і не забувати, що вона ж дозволяє зняти"]),
    ]

    for y, code, fill, stroke, mid, act in rows:
        p.append(fitbox(C1X, y, C1W, 110, [code],
                        size=17, pad=14, fill=fill, stroke=stroke, sw=2, bold=True))
        p.append(fitbox(C2X, y, C2W, 110, mid,
                        size=13.5, pad=14, fill=FILL, stroke=MUTED, sw=1.3))
        p.append(fitbox(C3X, y, C3W, 110, act,
                        size=13.5, pad=14, fill=BG, stroke=stroke, sw=1.6))

    p.append(fitbox(60, 580, W - 120, 64,
                    ["«нема де», «є, та не це» і «є, та не тобі» — програма, що друкує лише"
                     " «не вдалося», викидає весь діагноз"],
                    size=15, pad=14, fill=GREEN_FILL, stroke=FIELD, sw=1.8, bold=True))

    return render(os.path.join(IMG, 'three-refusals.svg'), W, H, *p)


if __name__ == '__main__':
    for f in (fig_flag_in_inode, fig_where_check_fires, fig_who_can_undo,
              fig_three_refusals):
        print(f())
