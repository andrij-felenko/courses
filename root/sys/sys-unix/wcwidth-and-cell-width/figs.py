# -*- coding: utf-8 -*-
"""Фігури до теми «Ширина символу в комірках: wcwidth, подвійні знаки й комбінаційні»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_cell_grid_mismatch():
    """Як різні типи символів лягають у дискретну сітку комірок термінала."""
    W, H = 1080, 560
    g = []

    g.append(text(W / 2, 38, "дискретна сітка термінала: від 1 байта до складних емодзі",
                  size=15, bold=True))

    cw, ch = 56, 44
    cols_count = 10
    grid_x = 240
    start_y = 90
    row_gap = 100

    # Шапка колонок
    for c in range(cols_count):
        x = grid_x + c * cw
        g.append(rect(x, start_y - 28, cw, 22, fill="#eef2f7", stroke=MUTED, sw=1, rx=2))
        g.append(text(x + cw / 2, start_y - 13, "[%d]" % c, size=11, color=MUTED, bold=True))

    cases = [
        ("ASCII\n1 байт = 1 комірка", [
            (0, 1, "H", "#ffffff", INK),
            (1, 1, "e", "#ffffff", INK),
            (2, 1, "l", "#ffffff", INK),
            (3, 1, "l", "#ffffff", INK),
            (4, 1, "o", "#ffffff", INK),
        ], "кожен байт ASCII просуває курсор рівно на одну колонку"),

        ("CJK ієрогліфи (Wide)\n2 комірки на знак", [
            (0, 2, "語", "#eaf7ee", FIELD),
            (2, 2, "言", "#eaf7ee", FIELD),
            (4, 1, "!", "#ffffff", INK),
        ], "ієрогліфи займають квадрат 2×1 комірки; wcwidth повертає 2"),

        ("Комбінаційний знак\nбаза + діакритика (0)", [
            (0, 1, "е", "#ffffff", INK),
            (0, 0, " ́", "#fdecea", POS),
            (1, 1, "к", "#ffffff", INK),
            (2, 1, "р", "#ffffff", INK),
            (3, 1, "а", "#ffffff", INK),
            (4, 1, "н", "#ffffff", INK),
        ], "діакритика U+0301 має ширину 0 і накладається на базову літеру 'е'"),

        ("ZWJ-послідовність емодзі\n👨 + ZWJ + 💻 = 👨‍💻", [
            (0, 2, "👨‍💻", "#eaf0fd", NEG),
            (2, 1, " ", "#ffffff", INK),
            (3, 1, "o", "#ffffff", INK),
            (4, 1, "k", "#ffffff", INK),
        ], "емулятор малює 1 гліф на 2 комірки, але наївний підрахунок дає 2+0+2 = 4"),
    ]

    for idx, (label, items, note) in enumerate(cases):
        y = start_y + idx * row_gap
        # Мітка зліва
        g.append(fitbox(30, y - 2, 190, ch + 4, label, size=12, fill="#f8fafc", stroke=MUTED, sw=1))

        # Порожні клітинки сітки
        for c in range(cols_count):
            x = grid_x + c * cw
            g.append(rect(x, y, cw, ch, fill="#ffffff", stroke="#d1d5db", sw=1, rx=2))

        # Заповнені символи
        for c, span, symb, fill, col in items:
            if span == 0:
                # Маркер нульової ширини
                x = grid_x + c * cw
                g.append(rect(x + 2, y + 2, cw - 4, ch - 4, fill="none", stroke=POS, sw=1.5, rx=2))
                g.append(text(x + cw * 0.78, y + 16, "+́", size=13, color=POS, bold=True))
            else:
                x = grid_x + c * cw
                w_span = span * cw
                g.append(rect(x, y, w_span, ch, fill=fill, stroke=col if span > 1 else LINE,
                              sw=2 if span > 1 else 1.2, rx=3))
                g.append(text(x + w_span / 2, y + ch * 0.68, symb, size=15 if span == 1 else 17,
                              color=col, bold=True))

        # Примітка праворуч або знизу
        g.append(text(grid_x + 5.5 * cw, y + ch + 18, note, size=11.5, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, 'cell-grid-mismatch.svg'), W, H, *g,
                  title="Розподіл символів у сітці комірок термінала")


def fig_desync_cursor_drift():
    """Як виникає розсинхронізація та дрейф курсора між програмою й емулятором."""
    W, H = 1080, 560
    g = []

    g.append(text(W / 2, 38, "розсинхронізація: коли програма й емулятор не згодні щодо ширини",
                  size=15, bold=True))

    cw, ch = 44, 38
    cols = 12

    # Ліва колонка: Уявлення програми (Readline / Vim)
    ax = 60
    ay = 80
    g.append(fitbox(ax, ay, 440, 52, "Уявлення програми (Readline / Bash / Vim)\nВважає, що емодзі 🚀 займає 1 комірку (старий wcwidth)",
                    size=12, bold=True, fill="#fff8e6", stroke=POS, sw=1.2))

    grid_ay = ay + 72
    row_a = ["$", " ", "g", "o", " ", "🚀", " ", "a", "p", "p", " ", " "]
    for c in range(cols):
        x = ax + c * cw
        g.append(rect(x, grid_ay, cw, ch, fill="#ffffff", stroke=MUTED, sw=1, rx=2))
        g.append(text(x + cw / 2, grid_ay + ch * 0.68, row_a[c], size=13, color=INK))

    # Позиція курсора за даними програми (col 10)
    cur_a_col = 10
    g.append(rect(ax + cur_a_col * cw, grid_ay, cw, ch, fill="none", stroke=FIELD, sw=2.5, rx=2))
    g.append(text(ax + cur_a_col * cw + cw / 2, grid_ay + ch + 20, "курсор: col 10",
                  size=11, color=FIELD, bold=True))

    # Права колонка: Реальний стан на склі термінала (VTE / Alacritty)
    bx = 580
    by = 80
    g.append(fitbox(bx, by, 440, 52, "Реальний стан на склі (Термінал)\nЕмулятор намалював 🚀 на 2 комірки згідно з Unicode 15+",
                    size=12, bold=True, fill="#eaf7ee", stroke=FIELD, sw=1.2))

    grid_by = by + 72
    row_b = ["$", " ", "g", "o", " ", "🚀", "", " ", "a", "p", "p", " "]
    for c in range(cols):
        x = bx + c * cw
        if c == 5:
            g.append(rect(x, grid_by, cw * 2, ch, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=2))
            g.append(text(x + cw, grid_by + ch * 0.68, "🚀", size=15, color=NEG, bold=True))
        elif c == 6:
            continue
        else:
            g.append(rect(x, grid_by, cw, ch, fill="#ffffff", stroke=MUTED, sw=1, rx=2))
            g.append(text(x + cw / 2, grid_by + ch * 0.68, row_b[c], size=13, color=INK))

    # Реальна позиція курсора на склі (col 11)
    cur_b_col = 11
    g.append(rect(bx + cur_b_col * cw, grid_by, cw, ch, fill="none", stroke=POS, sw=2.5, rx=2))
    g.append(text(bx + cur_b_col * cw + cw / 2, grid_by + ch + 20, "курсор: col 11",
                  size=11, color=POS, bold=True))

    # Нижня частина: Що стається при натисканні Backspace
    my = 280
    g.append(line(ax, my, ax + 960, my, color="#e5e7eb", sw=1.5, dash="4,4"))

    g.append(text(W / 2, my + 30, "Користувач натискає Backspace, щоб стерти останню літеру 'p':",
                  size=13, bold=True, color=INK))

    steps = [
        ("1. Програма надсилає '\\b \\b'",
         "Програма вважає, що курсор на col 10,\nі надсилає '\\b \\b' для затирання\nоднієї комірки в позиції 10."),
        ("2. Фізичний рух курсора",
         "На склі курсор був на col 11.\nВін відступає на 10 і затирає 'p',\nа друга літера 'p' лишається!"),
        ("3. Фантомні символи",
         "Буфер програми й екран розійшлися.\nПодальший ввід перетирає сусідній\nтекст або лишає графічне сміття."),
    ]

    sy = my + 60
    for idx, (title_s, desc_s) in enumerate(steps):
        sx = 80 + idx * 320
        g.append(fitbox(sx, sy, 300, 125, "%s\n\n%s" % (title_s, desc_s),
                        size=11.5, fill="#f8fafc", stroke=MUTED, sw=1))

    return render(os.path.join(IMG, 'desync-cursor-drift.svg'), W, H, *g,
                  title="Анатомія розсинхронізації та зсуву курсора")


def fig_uax11_categories():
    """Категорії East Asian Width (UAX #11) та їх відображення в комірки."""
    W, H = 1080, 560
    g = []

    g.append(text(W / 2, 36, "Класифікація ширини символів за стандартом Unicode UAX #11",
                  size=15, bold=True))

    cards = [
        ("Wide (W)", "2 комірки", "#eaf7ee", FIELD,
         "Ієрогліфи CJK, хірагана, катакана,\nповні розділові знаки. Завжди\nмають подвійну ширину на сітці."),
        ("Fullwidth (F)", "2 комірки", "#eaf7ee", FIELD,
         "Сумісні символи повної ширини\n(U+FF01–U+FF60): латиниця, цифри\nдля сумісності з форматом CJK."),
        ("Narrow (Na)", "1 комірка", "#ffffff", LINE,
         "Вузькі символи, що мають повні\nаналоги в CJK (напівширинна\nпунктуація). Завжди 1 колонка."),
        ("Halfwidth (H)", "1 комірка", "#ffffff", LINE,
         "Напівширинні сумісні символи\n(напівширинна катакана U+FF61,\nхангиль). Завжди 1 колонка."),
        ("Ambiguous (A)", "1 або 2 комірки", "#fff8e6", POS,
         "Грецькі, кириличні літери,\nпсевдографіка, спецсимволи.\nШирина залежить від локалі."),
        ("Neutral (N)", "1 або 0 комірок", "#ffffff", LINE,
         "Решта символів (латиниця, арабське\nписьмо тощо). Друковані — 1,\nкомбінаційні та керуючі — 0."),
    ]

    cw, ch = 310, 180
    positions = [
        (60, 75), (385, 75), (710, 75),
        (60, 285), (385, 285), (710, 285)
    ]

    for (title_s, width_s, fill_c, border_c, desc_s), (x, y) in zip(cards, positions):
        content = "%s  [%s]\n\n%s" % (title_s, width_s, desc_s)
        g.append(fitbox(x, y, cw, ch, content, size=12, fill=fill_c, stroke=border_c, sw=1.5))

    g.append(fitbox(60, 495, 960, 42,
                    "Комбінаційні діакритичні знаки (Mn, Me) та керуючі коди (Cf, Cc) завжди мають ширину 0 комірок.",
                    size=12, bold=True, fill="#f1f5f9", stroke=MUTED, sw=1))

    return render(os.path.join(IMG, 'uax11-categories.svg'), W, H, *g,
                  title="Категорії East Asian Width стандарту UAX #11")


if __name__ == '__main__':
    fig_cell_grid_mismatch()
    fig_desync_cursor_drift()
    fig_uax11_categories()
    print("All figures generated successfully.")
