# -*- coding: utf-8 -*-
"""Фігури до теми «Розв'язання перевантажень: як обирається функція»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_stages():
    """Чотири стадії добору й те, що відсіює кожна."""
    W, H = 1020, 620
    f = []
    bx, bw, bh = 40, 470, 86
    step = 132
    y0 = 66

    stages = [
        ("1 · Пошук імені",
         "збираємо все, що оголошено\nпід цим іменем",
         "аргументи ще не дивимось;\nпошук зупиняється на першій\nобласті, де ім'я знайшлося"),
        ("2 · Придатність",
         "чи можна цього кандидата\nвикликати з такими аргументами",
         "вибуває той, у кого не сходиться\nкількість аргументів або немає\nперетворення хоч для одного"),
        ("3 · Порівняння",
         "для кожного аргументу — розряд\nперетворення; вектори зіставляють",
         "єдиного найкращого немає →\nнеоднозначність, а не жереб"),
        ("4 · Перевірки після вибору",
         "доступ, = delete, explicit",
         "переможець не поступається\nмісцем наступному: програма\nпросто стає неправильною"),
    ]
    for i, (head, body, note) in enumerate(stages):
        y = y0 + i * step
        f.append(rect(bx, y, bw, bh, fill="#eef3f8", stroke=LINE, sw=1.4))
        f.append(text(bx + 20, y + 28, head, size=16, bold=True, anchor="start"))
        f.append(mtext(bx + 20, y + 52, body.split("\n"), size=13,
                       color=INK, anchor="start", lh=1.35))
        f.append(mtext(bx + bw + 46, y + 30, note.split("\n"), size=13,
                       color=MUTED, anchor="start", lh=1.4))
        if i < len(stages) - 1:
            f.append(arrow(bx + bw / 2, y + bh + 6, bx + bw / 2, y + step - 6))

    f.append(text(W / 2, H - 22,
                  "одна функція на виході — або чесна помилка компіляції",
                  size=14, color=MUTED))
    render(os.path.join(OUT, 'stages.svg'), W, H, *f,
           title="Чотири стадії добору перевантаження")


def fig_conversion_ladder():
    """Драбина розрядів послідовностей неявних перетворень."""
    W, H = 1000, 560
    f = []
    x0, w = 60, 560
    h = 74
    gap = 16
    y0 = 70

    rungs = [
        ("точний збіг", "int → int · масив → покажчик · T& ← T", "#dff0e3"),
        ("підвищення", "short → int · bool → int · float → double", "#e8f1dc"),
        ("перетворення", "int → double · double → int · Похідний* → Базовий*", "#fdf3e0"),
        ("перетворення користувача", "const char* → std::string (конструктор)", "#fbe6e6"),
        ("багатокрапка", "будь-що → ...", "#f0eef4"),
    ]
    for i, (name, sample, col) in enumerate(rungs):
        y = y0 + i * (h + gap)
        f.append(rect(x0, y, w, h, fill=col, stroke=LINE, sw=1.3))
        f.append(text(x0 + 22, y + 30, name, size=16, bold=True, anchor="start"))
        f.append(text(x0 + 22, y + 55, sample, size=13, color=MUTED, anchor="start"))

    gy0 = y0
    gy1 = y0 + 3 * (h + gap) - gap
    gy2 = y0 + 5 * (h + gap) - gap
    gx = x0 + w + 44
    f.append(line(gx, gy0, gx, gy1, color=NEG, sw=2.4))
    f.append(mtext(gx + 18, gy0 + 46,
                   ["стандартна", "послідовність:", "три розряди"],
                   size=14, color=NEG, anchor="start", lh=1.35))
    f.append(line(gx, gy1 + 16, gx, gy2, color=POS, sw=2.4))
    f.append(mtext(gx + 18, gy1 + 62,
                   ["нижче за будь-яку", "стандартну — хоч би", "яка вона була"],
                   size=14, color=POS, anchor="start", lh=1.35))

    f.append(text(W / 2, H - 20,
                  "розряд усієї послідовності визначає її найгірший крок",
                  size=14, color=MUTED))
    render(os.path.join(OUT, 'conversion-ladder.svg'), W, H, *f,
           title="Чим краща послідовність перетворень — тим вище щабель")


def fig_pairwise():
    """Порівняння векторів розрядів: є переможець і немає переможця."""
    W, H = 1040, 480
    f = []

    def panel(x0, y0, title_lines, call, rows, verdict, vcolor):
        g = []
        pw = 440
        g.append(rect(x0, y0, pw, 320, fill="#ffffff", stroke=MUTED, sw=1.2))
        g.append(mtext(x0 + pw / 2, y0 + 30, title_lines, size=14,
                       color=MUTED, lh=1.35))
        g.append(text(x0 + pw / 2, y0 + 78, call, size=16, bold=True))
        # шапка таблиці
        cw = 150
        lx = x0 + 20
        cx1 = lx + 130
        cx2 = cx1 + cw
        g.append(text(cx1 + cw / 2, y0 + 118, "аргумент 1", size=13, color=MUTED))
        g.append(text(cx2 + cw / 2, y0 + 118, "аргумент 2", size=13, color=MUTED))
        for i, (name, a, b, best) in enumerate(rows):
            y = y0 + 138 + i * 62
            g.append(fitbox(lx, y, 130, 50, name, size=13, fill="#eef3f8"))
            g.append(fitbox(cx1, y, cw - 10, 50, a, size=13,
                            fill="#dff0e3" if best[0] else "#f6f6f6"))
            g.append(fitbox(cx2, y, cw - 10, 50, b, size=13,
                            fill="#dff0e3" if best[1] else "#f6f6f6"))
        g.append(text(x0 + pw / 2, y0 + 296, verdict, size=15,
                      bold=True, color=vcolor))
        return g

    f += panel(30, 60,
               ["точний збіг на першому місці,", "решта не гірша"],
               "g(1, 2.0)",
               [("g(int, double)", "точний збіг", "точний збіг", (True, True)),
                ("g(double, int)", "перетворення", "перетворення", (False, False))],
               "переможець є", FIELD)

    f += panel(560, 60,
               ["кожен виграє свою позицію", "й програє чужу"],
               "g(1, 2)",
               [("g(int, double)", "точний збіг", "перетворення", (True, False)),
                ("g(double, int)", "перетворення", "точний збіг", (False, True))],
               "неоднозначність", POS)

    f.append(text(W / 2, H - 32,
                  "кращий той, хто не гірший за ВСІМА позиціями і строго кращий хоч за однією",
                  size=14, color=MUTED))
    render(os.path.join(OUT, 'pairwise.svg'), W, H, *f,
           title="Порівнюють вектор розрядів, а не суму балів")


def fig_overload_timeline():
    """Як правила добору ставали порядконезалежними: віхи й конструкторські рішення."""
    W, H = 1120, 800
    f = []
    bx, bw, bh = 40, 400, 96
    step = 140
    y0 = 62

    events = [
        ("1980—1983 · «C with Classes»",
         "перевантаження немає зовсім",
         "чотири побоювання: розпухлий компілятор,\nрозпухла настанова, повільний код,\nнечитний код"),
        ("1984 · дошка й перший дослід",
         "механіку розписано з Фелдманом,\nМакілроєм і Шопіро",
         "перша реалізація — 18 рядків у cfront,\nопис у настанові виріс на півтори сторінки\nз сорока двох"),
        ("жовтень 1985 · випуск 1.0",
         "перевантаження є, але його треба\nоголосити словом overload",
         "розсуд у два етапи: вбудовані перетворення\nперемагають користувацькі; результат\nзалежить від порядку оголошень"),
        ("червень 1989 · cfront 2.0",
         "слово overload стає зайвим,\nдобір — порядконезалежним",
         "більше викликів визнано неоднозначними:\nчесна помилка замість тихого\nвипадкового вибору"),
        ("1990 · ARM, далі комітет ISO",
         "overload — у розділі анахронізмів",
         "ранжування послідовностей перетворень\nвигранено до вигляду, який стандарт\nносить дотепер"),
    ]
    for i, (head, body, note) in enumerate(events):
        y = y0 + i * step
        f.append(rect(bx, y, bw, bh, fill="#eef3f8", stroke=LINE, sw=1.4))
        f.append(text(bx + 20, y + 28, head, size=15, bold=True, anchor="start"))
        f.append(mtext(bx + 20, y + 52, body.split("\n"), size=13,
                       color=INK, anchor="start", lh=1.35))
        f.append(mtext(bx + bw + 60, y + 30, note.split("\n"), size=13,
                       color=MUTED, anchor="start", lh=1.4))
        if i < len(events) - 1:
            f.append(arrow(bx + bw / 2, y + bh + 8, bx + bw / 2, y + step - 8))

    f.append(text(W / 2, H - 26,
                  "рух один: від позначки, яку ставить автор, до правила, тотожного для всіх викликів",
                  size=14, color=MUTED))
    render(os.path.join(OUT, 'overload-timeline.svg'), W, H, *f,
           title="Віхи перевантаження: від слова overload до порядконезалежних правил")


if __name__ == '__main__':
    fig_stages()
    fig_conversion_ladder()
    fig_pairwise()
    fig_overload_timeline()
    print("ok")
