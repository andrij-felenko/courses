# -*- coding: utf-8 -*-
"""Фігури до теми «База terminfo»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_tparm_stack():
    """Рядок можливості — не текст, а програмка для стекової машини."""
    W, H = 1060, 560
    g = []

    g.append(text(W / 2, 44,
                  "cup = \\E[%i%p1%d;%p2%dH    ·    параметри 9 і 2 (рядок і стовпець від нуля)",
                  size=14, color=INK, bold=True))

    cols = [(60, 130), (200, 400), (612, 130), (754, 246)]
    heads = ["крок рецепта", "що він робить", "стек", "накопичений вивід"]
    hy = 76
    for (cx, cw), htext in zip(cols, heads):
        g.append(fitbox(cx, hy, cw, 42, htext, size=13, bold=True,
                        fill="#eef2f7", stroke=MUTED))

    rows = [
        ("%i", "до перших двох параметрів додати одиницю", "—", "порожньо"),
        ("\\E [", "байти йдуть у вивід як є", "—", "ESC ["),
        ("%p1", "покласти на стек перший параметр", "10", "ESC ["),
        ("%d", "зняти зі стека й надрукувати десятково", "—", "ESC [ 10"),
        (";", "байт іде у вивід як є", "—", "ESC [ 10 ;"),
        ("%p2", "покласти на стек другий параметр", "3", "ESC [ 10 ;"),
        ("%d", "зняти зі стека й надрукувати десятково", "—", "ESC [ 10 ; 3"),
        ("H", "байт іде у вивід як є", "—", "ESC [ 10 ; 3 H"),
    ]
    ry, rh = 130, 44
    for k, row in enumerate(rows):
        y = ry + k * rh
        tint = "#ffffff" if k % 2 else FILL
        for (cx, cw), cell in zip(cols, row):
            bold = (cx == 60) or (cx == 754 and k == len(rows) - 1)
            fill = "#eaf7ee" if (cx == 754 and k == len(rows) - 1) else tint
            g.append(fitbox(cx, y, cw, rh, cell, size=12.5, fill=fill,
                            stroke=MUTED, sw=1, bold=bold))

    g.append(fitbox(60, 500, 940, 44,
                    "нумерація з нуля в базі й з одиниці в послідовності — "
                    "різниця схована в одному кроці %i, а не в кожній програмі",
                    size=13, fill="#fff8e6", stroke=MUTED))

    return render(os.path.join(IMG, 'tparm-stack.svg'), W, H, *g,
                  title="Розгортання рядка з параметрами")


def fig_compiled_layout():
    """Стандартну частину адресують номером комірки — звідси заморожений набір."""
    W, H = 1180, 520
    g = []

    g.append(text(W / 2, 44, "скомпільований запис бази: що лежить у файлі",
                  size=14, color=INK, bold=True))

    band_y, band_h = 92, 96
    parts = [
        (60, 178, "заголовок\n6 двобайтових чисел:\nмітка формату й розміри", "#eaf7ee", FIELD),
        (248, 196, "імена й псевдоніми\nодин рядок тексту", FILL, MUTED),
        (454, 168, "булеві\nпо байту\nна можливість", FILL, MUTED),
        (632, 168, "числа\nпо 2 байти\nна можливість", FILL, MUTED),
        (810, 168, "зміщення рядків\nпо 2 байти\nна можливість", FILL, MUTED),
        (988, 132, "таблиця\nрядків", FILL, MUTED),
    ]
    for x, w, label, fill, stroke in parts:
        g.append(fitbox(x, band_y, w, band_h, label, size=12.5, fill=fill, stroke=stroke))

    g.append(fitbox(454, 214, 700, 52,
                    "імен цих можливостей у файлі немає: «cup» — це просто "
                    "ділянка з наперед відомим номером у таблиці зміщень",
                    size=13, fill="#fdecea", stroke=POS))

    g.append(fitbox(60, 306, 500, 96,
                    "Номер комірки — і є ім'я можливості.\n"
                    "Додати нову в стандартний набір означає зсунути\n"
                    "всі наступні номери й зробити нечитними\n"
                    "всі вже скомпільовані файли.",
                    size=13, fill="#fff8e6", stroke=MUTED))

    g.append(fitbox(620, 306, 500, 96,
                    "Тому нове дописують окремою частиною в кінці —\n"
                    "там поруч зі значеннями лежать і самі назви.\n"
                    "Саме так у базу потрапили «RGB», «Tc», «Smulx»\n"
                    "та інші домовленості останніх років.",
                    size=13, fill="#eaf7ee", stroke=FIELD))

    g.append(arrow(560, 354, 616, 354, color=MUTED, sw=1.6))

    g.append(text(W / 2, 452,
                  "мітка формату розрізняє й самі формати: 0432 — числа по два байти, "
                  "01036 — по чотири",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, 'compiled-layout.svg'), W, H, *g,
                  title="Будова скомпільованого запису")


def fig_lookup_path():
    """Від імені в змінній середовища до байтів у дескрипторі."""
    W, H = 1180, 560
    g = []

    row1 = [
        (60, 300, "TERM=xterm-256color\n\nім'я, яке процес успадкував\nвід батька — не вимір",
         "#fff8e6", MUTED),
        (440, 300, "пошук файлу запису\n\nTERMINFO · ~/.terminfo ·\nTERMINFO_DIRS · /usr/share/terminfo",
         FILL, MUTED),
        (820, 300, "запис у пам'яті\n\nбулеві, числа й рядки\nодного термінала",
         "#eaf7ee", FIELD),
    ]
    for x, w, label, fill, stroke in row1:
        g.append(fitbox(x, 84, w, 118, label, size=12.5, fill=fill, stroke=stroke))
    g.append(arrow(364, 143, 436, 143))
    g.append(arrow(744, 143, 816, 143))

    g.append(line(970, 202, 970, 240, color=LINE, sw=1.5))
    g.append(line(970, 240, 210, 240, color=LINE, sw=1.5))
    g.append(arrow(210, 240, 210, 286, color=LINE, sw=1.5))

    row2 = [
        (60, 300, "tigetstr(\"cup\")\n\nвіддає рецепт\n\\E[%i%p1%d;%p2%dH", FILL, MUTED),
        (440, 300, "tparm(рецепт, 9, 2)\n\nрозгортає в готові байти\nESC [ 10 ; 3 H",
         FILL, MUTED),
        (820, 300, "tputs(байти, 1, putc)\n\nдодає заповнення за швидкістю\nлінії — і аж тоді write",
         "#eaf7ee", FIELD),
    ]
    for x, w, label, fill, stroke in row2:
        g.append(fitbox(x, 286, w, 118, label, size=12.5, fill=fill, stroke=stroke))
    g.append(arrow(364, 345, 436, 345))
    g.append(arrow(744, 345, 816, 345))

    g.append(fitbox(440, 434, 680, 50,
                    "швидкість лінії tputs бере з termios того самого дескриптора",
                    size=13, fill="#eef2f7", stroke=MUTED))
    g.append(arrow(970, 404, 970, 430, color=MUTED, sw=1.4))

    g.append(fitbox(60, 434, 300, 50, "жоден крок не питає сам термінал",
                    size=13, fill="#fdecea", stroke=POS))

    return render(os.path.join(IMG, 'lookup-path.svg'), W, H, *g,
                  title="Шлях від імені термінала до байтів")


def fig_tparm_branches():
    """Плаский ланцюжок «інакше-якщо» й два різні стрибки тлумача."""
    W, H = 1000, 760
    g = []

    g.append(text(W / 2, 40,
                  "setaf = \\E[%?%p1%{8}%<%t3%p1%d%e%p1%{16}%<%t9%p1%{8}%-%d"
                  "%e38;5;%p1%d%;m",
                  size=13, color=INK, bold=True))
    g.append(text(W / 2, 68,
                  "одне розгалуження на три гілки — і рівно один маркер кінця «%;»",
                  size=13, color=MUTED))

    rows = [
        ("\\E [", "два байти йдуть у вивід як є", FILL),
        ("%?", "починається розгалуження; далі — код умови", "#eef2f7"),
        ("%p1 %{8} %<", "умова: чи номер кольору менший за 8", FILL),
        ("%t", "зняти зі стека; хибно — стрибок уперед", "#fdecea"),
        ("3 %p1 %d", "гілка: байт «3» і номер  →  30…37", "#eaf7ee"),
        ("%e", "гілку виконано — стрибок у кінець", "#fff8e6"),
        ("%p1 %{16} %<", "умова: чи номер менший за 16", FILL),
        ("%t", "зняти зі стека; хибно — стрибок уперед", "#fdecea"),
        ("9 %p1 %{8} %- %d", "гілка: байт «9» і номер−8  →  90…97", "#eaf7ee"),
        ("%e", "гілку виконано — стрибок у кінець", "#fff8e6"),
        ("38;5; %p1 %d", "остання гілка: довга форма на 256 кольорів", "#eaf7ee"),
        ("%;", "кінець розгалуження", "#eef2f7"),
        ("m", "завершальний байт послідовності SGR", FILL),
    ]
    top, rh = 100, 42
    for k, (tok, why, tint) in enumerate(rows):
        y = top + k * rh
        g.append(fitbox(70, y, 260, rh, tok, size=12.5, fill=tint,
                        stroke=MUTED, sw=1, bold=True))
        g.append(fitbox(350, y, 430, rh, why, size=12.5, fill="#ffffff",
                        stroke=MUTED, sw=1))

    def c(k):
        return top + k * rh + rh / 2

    # хибна умова: шукаємо найближче «%e» свого рівня
    for src, dst in ((3, 6), (7, 10)):
        g.append(line(782, c(src), 820, c(src), color=POS, sw=1.6))
        g.append(line(820, c(src), 820, c(dst), color=POS, sw=1.6))
        g.append(arrow(820, c(dst), 786, c(dst), color=POS, sw=1.6))

    # гілку виконано: шукаємо «%;» свого рівня
    for src, lane, dy in ((5, 890, -8), (9, 950, 8)):
        g.append(line(782, c(src), lane, c(src), color=FIELD, sw=1.6))
        g.append(line(lane, c(src), lane, c(12) + dy, color=FIELD, sw=1.6))
        g.append(arrow(lane, c(12) + dy, 786, c(12) + dy, color=FIELD, sw=1.6))

    g.append(fitbox(70, 690, 340, 46, "стрибок за хибною умовою:\nдо «%e» свого рівня",
                    size=12.5, fill="#fdecea", stroke=POS, sw=1.4))
    g.append(fitbox(440, 690, 340, 46, "стрибок після виконаної гілки:\nдо «%;» свого рівня",
                    size=12.5, fill="#eaf7ee", stroke=FIELD, sw=1.4))

    return render(os.path.join(IMG, 'tparm-branches.svg'), W, H, *g,
                  title="Два стрибки тлумача розгалужень")


def fig_tparm_memory():
    """Чотири сховища машини й оператори, що їх зʼєднують."""
    W, H = 1160, 520
    g = []

    g.append(text(W / 2, 38, "памʼять тлумача: чотири різні сховища й один вивід",
                  size=14, color=INK, bold=True))

    g.append(fitbox(460, 76, 240, 96, "параметри\n%p1 … %p9\nзадає виклик",
                    size=12.5, fill="#fff8e6", stroke=MUTED))
    g.append(fitbox(60, 76, 340, 96,
                    "здебільшого числа; рядки бувають\nлише в кількох можливостях —\n"
                    "тих, що програмують клавіші",
                    size=12.5, fill=FILL, stroke=MUTED))
    g.append(arrow(404, 124, 452, 124, color=MUTED, sw=1.4))
    g.append(fitbox(760, 76, 340, 96,
                    "%i — єдиний оператор, що чіпає\nсамі параметри: додає одиницю\n"
                    "до перших двох",
                    size=12.5, fill=FILL, stroke=MUTED))
    g.append(arrow(756, 124, 708, 124, color=MUTED, sw=1.4))

    g.append(arrow(580, 176, 580, 224))
    g.append(text(598, 206, "%p1 … %p9", size=12.5, color=MUTED, anchor="start"))

    g.append(fitbox(460, 228, 240, 96, "стек\nоперанди всіх\nоператорів",
                    size=12.5, fill="#eaf7ee", stroke=FIELD))
    g.append(fitbox(60, 228, 240, 96, "динамічні змінні\n%Pa … %Pz", size=12.5,
                    fill=FILL, stroke=MUTED))
    g.append(fitbox(860, 228, 240, 96, "статичні змінні\n%PA … %PZ", size=12.5,
                    fill=FILL, stroke=MUTED))

    g.append(arrow(456, 256, 306, 256, color=MUTED, sw=1.5))
    g.append(text(381, 242, "%Pa", size=12.5, color=MUTED, bold=True))
    g.append(arrow(306, 300, 456, 300, color=MUTED, sw=1.5))
    g.append(text(381, 328, "%ga", size=12.5, color=MUTED, bold=True))

    g.append(arrow(704, 256, 854, 256, color=MUTED, sw=1.5))
    g.append(text(779, 242, "%PA", size=12.5, color=MUTED, bold=True))
    g.append(arrow(854, 300, 704, 300, color=MUTED, sw=1.5))
    g.append(text(779, 328, "%gA", size=12.5, color=MUTED, bold=True))

    g.append(arrow(580, 328, 580, 376))
    g.append(text(598, 358, "%d  %s  %c", size=12.5, color=MUTED, anchor="start"))

    g.append(fitbox(460, 380, 240, 96, "вивід\nготові байти\nдля термінала",
                    size=12.5, fill="#eaf7ee", stroke=FIELD))
    g.append(fitbox(60, 380, 240, 96, "байти рецепта\nбез «%»", size=12.5,
                    fill=FILL, stroke=MUTED))
    g.append(arrow(306, 428, 456, 428, color=MUTED, sw=1.5))
    g.append(text(381, 414, "як є", size=12.5, color=MUTED))

    g.append(fitbox(760, 380, 340, 96,
                    "ncurses не скидає жодного з двох\nнаборів змінних між викликами:\n"
                    "обидві назви оманливі",
                    size=12.5, fill="#fdecea", stroke=POS))
    g.append(arrow(980, 328, 980, 376, color=POS, sw=1.5))

    return render(os.path.join(IMG, 'tparm-memory.svg'), W, H, *g,
                  title="Памʼять тлумача рядків з параметрами")


if __name__ == '__main__':
    fig_tparm_stack()
    fig_compiled_layout()
    fig_lookup_path()
    fig_tparm_branches()
    fig_tparm_memory()
    print("готово:", os.listdir(IMG))
