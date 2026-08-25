# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_contract():
    """Без файлу обмежень аналізатор і фітер сліпі; з ним — мають контракт."""
    W, H = 720, 400
    frags = []
    frags.append(text(W / 2, 30, "Файл обмежень = контракт для інструмента", size=17, bold=True))

    # ліва колонка: без обмежень
    lx = 40
    frags.append(fitbox(lx, 60, 300, 40, "Без файлу обмежень", size=15, bold=True,
                        fill="#fdecea", stroke=POS))
    items_bad = [
        "такту НЕ визначено —",
        "аналізатор мовчить",
        "піни розкидані як завгодно",
        "плата не заведеться",
        "«таймінг зійшовся» ≠ правда",
    ]
    y = 120
    for it in items_bad:
        frags.append(text(lx, y, "✗ " + it, size=13, color=POS, anchor="start"))
        y += 32

    # права колонка: з обмеженнями
    rx = 380
    frags.append(fitbox(rx, 60, 300, 40, "З файлом обмежень (SDC/XDC)", size=15, bold=True,
                        fill="#e9f7ef", stroke=FIELD))
    items_good = [
        "create_clock — період відомий",
        "аналізатор рахує slack",
        "set_property — пін прибитий",
        "IO-стандарт заданий",
        "провал таймінгу видно ще до плати",
    ]
    y = 120
    for it in items_good:
        frags.append(text(rx, y, "✓ " + it, size=13, color=FIELD, anchor="start"))
        y += 32

    # низ: підпис-міст
    frags.append(fitbox(140, 320, 440, 52,
                        "Синтез знає ЩО робить схема, але не ЯКА мета в часі\n"
                        "й де фізично піни — це дописуєш ти окремим файлом",
                        size=13, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, 'contract.svg'), W, H, *frags)


def fig_io_delay():
    """set_input_delay / set_output_delay моделюють світ поза чипом."""
    W, H = 720, 360
    frags = []
    frags.append(text(W / 2, 30, "I/O-затримки описують те, чого чип не бачить", size=17, bold=True))

    # чип посередині
    cx0, cy0 = 300, 130
    frags.append(rect(cx0, cy0, 140, 100, fill="#eef2ff", stroke=NEG, sw=2))
    frags.append(text(cx0 + 70, cy0 + 40, "FPGA", size=16, bold=True, color=NEG))
    frags.append(text(cx0 + 70, cy0 + 66, "(тригери)", size=12, color=MUTED))

    # зовнішнє джерело зліва
    frags.append(rect(40, cy0 + 15, 130, 60, fill=FILL, stroke=LINE))
    frags.append(text(105, cy0 + 40, "давач / сусідній", size=12))
    frags.append(text(105, cy0 + 58, "чип", size=12))
    frags.append(arrow(170, cy0 + 45, cx0 - 2, cy0 + 45, color=INK, sw=2))
    frags.append(text(235, cy0 + 30, "дані", size=12, color=MUTED))

    # зовнішній приймач справа
    frags.append(rect(550, cy0 + 15, 130, 60, fill=FILL, stroke=LINE))
    frags.append(text(615, cy0 + 40, "АЦП / інший", size=12))
    frags.append(text(615, cy0 + 58, "приймач", size=12))
    frags.append(arrow(cx0 + 142, cy0 + 45, 550, cy0 + 45, color=INK, sw=2))

    # спільний такт знизу
    ty = 300
    frags.append(line(105, cy0 + 75, 105, ty, color=MUTED, dash="4 3"))
    frags.append(line(cx0 + 70, cy0 + 100, cx0 + 70, ty, color=MUTED, dash="4 3"))
    frags.append(line(615, cy0 + 75, 615, ty, color=MUTED, dash="4 3"))
    frags.append(line(90, ty, 630, ty, color=INK, sw=2))
    frags.append(text(60, ty + 4, "такт", size=12, color=INK, anchor="end"))

    # підписи затримок
    frags.append(fitbox(40, 70, 250, 44,
                        "set_input_delay — коли дані\nприходять ЗЗОВНІ до фронту",
                        size=12, fill="#e9f7ef", stroke=FIELD))
    frags.append(fitbox(430, 70, 250, 44,
                        "set_output_delay — скільки часу\nПОТРІБНО приймачеві зовні",
                        size=12, fill="#e9f7ef", stroke=FIELD))
    render(os.path.join(IMG, 'io-delay.svg'), W, H, *frags)


def fig_exceptions():
    """Винятки: false_path прибирає перевірку, multicycle — послаблює."""
    W, H = 720, 340
    frags = []
    frags.append(text(W / 2, 30, "Винятки кажуть аналізаторові, де НЕ душити", size=17, bold=True))

    def ff(x, y, label):
        frags.append(rect(x, y, 54, 54, fill="#eef2ff", stroke=NEG, sw=1.8))
        frags.append(text(x + 27, y + 32, label, size=13, bold=True, color=NEG))

    # рядок 1: звичайний шлях (перевіряється)
    ff(60, 70, "A")
    ff(360, 70, "B")
    frags.append(arrow(114, 97, 360, 97, color=INK, sw=2))
    frags.append(text(237, 84, "1 такт — перевіряється", size=12, color=INK))
    frags.append(text(500, 97, "✓ звичайно", size=13, color=FIELD, anchor="start"))

    # рядок 2: false_path
    ff(60, 160, "C")
    ff(360, 160, "D")
    frags.append(line(114, 187, 360, 187, color=MUTED, sw=2, dash="6 4"))
    frags.append(text(237, 174, "цим ніколи не біжить робоче", size=11, color=MUTED))
    frags.append(text(500, 187, "set_false_path", size=12, color=POS, anchor="start"))
    frags.append(text(500, 204, "✗ не перевіряти", size=12, color=POS, anchor="start"))

    # рядок 3: multicycle
    ff(60, 250, "E")
    ff(360, 250, "F")
    frags.append(arrow(114, 277, 360, 277, color=INK, sw=2))
    frags.append(text(237, 264, "дозволено 2 такти", size=11, color=INK))
    frags.append(text(500, 277, "set_multicycle_path", size=12, color=INK, anchor="start"))
    frags.append(text(500, 294, "✓ послаблено", size=12, color=INK, anchor="start"))
    render(os.path.join(IMG, 'exceptions.svg'), W, H, *frags)


def fig_lineage():
    """Родовід SDC: корінь у світі ASIC (Synopsys), дві гілки-діалекти для FPGA."""
    W, H = 720, 430
    frags = []
    frags.append(text(W / 2, 30, "Один корінь, два діалекти для FPGA", size=17, bold=True))

    # корінь: SDC у світі ASIC
    frags.append(fitbox(210, 60, 300, 62,
                        "SDC — Synopsys Design Constraints\n"
                        "світ ASIC · на основі Tcl · лише таймінг",
                        size=13, bold=True, fill="#eef2ff", stroke=NEG))
    # інструменти-джерело під коренем
    frags.append(text(360, 142, "Design Compiler · PrimeTime · IC Compiler", size=11, color=MUTED))
    frags.append(text(360, 160, "став фактичним галузевим стандартом →", size=11, color=MUTED))

    # розгалуження
    frags.append(line(360, 168, 360, 190, color=INK, sw=1.5))
    frags.append(line(175, 190, 545, 190, color=INK, sw=1.5))
    frags.append(arrow(175, 190, 175, 214, color=INK, sw=1.8))
    frags.append(arrow(545, 190, 545, 214, color=INK, sw=1.8))

    # ліва гілка: Xilinx / AMD → XDC
    frags.append(fitbox(35, 216, 280, 100,
                        "Xilinx (нині AMD)\n"
                        "XDC — Xilinx Design Constraints\n"
                        "= SDC (таймінг)\n"
                        "+ set_property (піни, IO-стандарт)",
                        size=12, bold=True, fill="#e9f7ef", stroke=FIELD))
    frags.append(text(175, 338, "прийшов на зміну UCF", size=11, color=POS))

    # права гілка: Intel / Altera → .sdc
    frags.append(fitbox(405, 216, 280, 100,
                        "Intel (нині Altera)\n"
                        ".sdc — той самий SDC\n"
                        "таймінг у .sdc,\n"
                        "розміщення ніг — окремо",
                        size=12, bold=True, fill="#e9f7ef", stroke=FIELD))
    frags.append(text(545, 338, "читає Timing Analyzer (TimeQuest)", size=11, color=MUTED))

    # спільний підпис-міст
    frags.append(fitbox(120, 366, 480, 46,
                        "Таймінг усюди говорять мовою SDC;\n"
                        "фізику ніг — місцевим діалектом кожного виробника",
                        size=13, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, 'lineage.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_contract()
    fig_io_delay()
    fig_exceptions()
    fig_lineage()
    print("figs written to", IMG)
