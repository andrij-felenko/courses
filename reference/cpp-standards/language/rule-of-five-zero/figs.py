# -*- coding: utf-8 -*-
"""Фігури теми «Правило п'яти й правило нуля»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_shallow_copy():
    """Почленне копіювання вказівника → два власники одного блоку → подвійне звільнення."""
    W, H = 800, 430
    f = []

    # ── лівий об'єкт
    f.append(fitbox(60, 62, 240, 42, "Buffer a", bold=True))
    f.append(fitbox(60, 110, 240, 38, "data = 0x1000"))
    f.append(fitbox(60, 152, 240, 38, "size = 4"))

    # ── правий об'єкт
    f.append(fitbox(500, 62, 240, 42, "Buffer b = a", bold=True))
    f.append(fitbox(500, 110, 240, 38, "data = 0x1000"))
    f.append(fitbox(500, 152, 240, 38, "size = 4"))

    # ── блок у купі
    f.append(fitbox(290, 262, 220, 62, "купа @ 0x1000\n[ 4 байти ]", fill="#eef7ee",
                    stroke=FIELD))

    # ── стрілки до одного й того самого блоку
    f.append(arrow(180, 196, 350, 258))
    f.append(arrow(620, 196, 450, 258))

    # ── наслідок
    f.append(text(400, 356, "~Buffer(b):  delete[] 0x1000   —   блок звільнено",
                  size=14, color=MUTED))
    f.append(text(400, 386, "~Buffer(a):  delete[] 0x1000   —   звільнення вже чужої пам'яті",
                  size=14, color=POS, bold=True))
    f.append(text(400, 412, "структури алокатора зруйновано", size=13, color=POS))

    render(os.path.join(IMG, 'shallow-copy.svg'), W, H, *f,
           title="Почленна копія вказівника: два об'єкти, один блок")


def fig_suppression():
    """Що глушить що — і чому втрата переміщень тиха, а втрата копій гучна."""
    W, H = 820, 400
    f = []

    y1 = 74
    f.append(fitbox(40, y1, 200, 58, "оголошено\n~Widget()"))
    f.append(arrow(248, y1 + 29, 288, y1 + 29))
    f.append(fitbox(296, y1, 210, 58, "переміщення\nне оголошується"))
    f.append(arrow(514, y1 + 29, 554, y1 + 29))
    f.append(fitbox(562, y1, 218, 58, "std::move(x)\nпотрапляє в копію"))
    f.append(fitbox(40, 156, 740, 46,
                    "ТИХО: збирається, працює правильно — просто копіює там, де мав переміщувати",
                    fill="#fdecea", stroke=POS, color=POS, bold=True))

    y2 = 244
    f.append(fitbox(40, y2, 200, 58, "оголошено\nWidget(Widget&&)"))
    f.append(arrow(248, y2 + 29, 288, y2 + 29))
    f.append(fitbox(296, y2, 210, 58, "копіювання\n= delete"))
    f.append(arrow(514, y2 + 29, 554, y2 + 29))
    f.append(fitbox(562, y2, 218, 58, "будь-яка копія —\nвідмова"))
    f.append(fitbox(40, 326, 740, 46,
                    "ГУЧНО: помилка компіляції в першому ж місці, де потрібна копія",
                    fill="#eef7ee", stroke=FIELD, color=FIELD, bold=True))

    render(os.path.join(IMG, 'suppression.svg'), W, H, *f,
           title="Одне оголошення прибирає інші — з різною ціною помилки")


def fig_rule_of_zero():
    """Ресурс у самому класі проти ресурсу в члені-власнику."""
    W, H = 860, 430
    f = []

    # ── ліва панель
    f.append(rect(40, 58, 360, 306, fill="#ffffff", stroke=POS, sw=2))
    f.append(fitbox(58, 74, 324, 40, "ресурс тримає сам клас", bold=True,
                    fill="#fdecea", stroke=POS, color=POS))
    f.append(fitbox(58, 128, 324, 38, "char* data;"))
    f.append(fitbox(58, 182, 324, 118,
                    "~Buffer()\nBuffer(const Buffer&)\noperator=(const Buffer&)\n"
                    "Buffer(Buffer&&)\noperator=(Buffer&&)"))
    f.append(text(220, 332, "п'ять функцій, узгоджених вручну", size=13, color=POS))

    # ── права панель
    f.append(rect(460, 58, 360, 306, fill="#ffffff", stroke=FIELD, sw=2))
    f.append(fitbox(478, 74, 324, 40, "ресурсом володіє член", bold=True,
                    fill="#eef7ee", stroke=FIELD, color=FIELD))
    f.append(fitbox(478, 128, 324, 38, "std::vector<char> data;"))
    f.append(fitbox(478, 182, 324, 118,
                    "— жодної з п'яти —\n\nпочленні операції вже\nправильні, бо правильний\nсам член"))
    f.append(text(640, 332, "нуль функцій", size=13, color=FIELD))

    f.append(text(430, 400,
                  "П'ятірку не скасовано — її написали один раз усередині типу-власника",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'rule-of-zero.svg'), W, H, *f,
           title="Де живе відповідальність за ресурс")


def fig_copy_and_swap_flow():
    """Три кроки присвоєння за значенням: копія → обмін → смерть параметра."""
    W, H = 920, 410
    f = []

    panels = [
        ("1 · Buffer rhs = b",
         "a:    data → блок A",
         "rhs:  data → блок B",
         "кинути може лише цей крок;\n*this ще не змінено —\nзвідси сильна гарантія",
         "#fdecea", POS),
        ("2 · swap(*this, rhs)",
         "a:    data → блок B",
         "rhs:  data → блок A",
         "обмін вказівника й числа:\nnoexcept, зірватися\nвже нічому",
         "#eef7ee", FIELD),
        ("3 · закрита дужка",
         "a:    data → блок B",
         "rhs знищено, A звільнено",
         "деструктор параметра\nвіддає старе — і про це\nв операторі жодного рядка",
         "#eef7ee", FIELD),
    ]

    for i, (title, row1, row2, note, fill, col) in enumerate(panels):
        x = 30 + i * 305
        f.append(rect(x, 48, 250, 290, fill=BG, stroke=MUTED, sw=1.2))
        f.append(fitbox(x + 14, 62, 222, 38, title, bold=True, fill=FILL))
        f.append(fitbox(x + 14, 116, 222, 36, row1, size=13))
        f.append(fitbox(x + 14, 156, 222, 36, row2, size=13))
        f.append(fitbox(x + 14, 212, 222, 110, note, size=12,
                        fill=fill, stroke=col, color=col))
        if i < 2:
            f.append(arrow(286 + i * 305, 190, 328 + i * 305, 190))

    f.append(text(460, 376,
                  "Оператор не згадує ні new, ні delete: копію робить конструктор, "
                  "звільнення — деструктор параметра.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'copy-and-swap-flow.svg'), W, H, *f,
           title="Копіюй і обмінюй: три кроки одного присвоєння")


def fig_assign_cost():
    """Чому копіюй-і-обмінюй програє переприсвоєнню в наявний буфер."""
    W, H = 880, 336
    f = []

    f.append(fitbox(30, 40, 240, 50, "копіюй і обмінюй", bold=True,
                    fill="#fdecea", stroke=POS, color=POS))
    f.append(fitbox(300, 40, 550, 50,
                    "new[n]  →  copy n  →  swap  →  delete[] старий"))
    f.append(text(575, 112,
                  "завжди одне виділення; пік пам'яті ≈ старий блок + новий",
                  size=13, color=POS))

    f.append(line(30, 136, 850, 136, color=MUTED, sw=1, dash="5,5"))

    f.append(fitbox(30, 160, 240, 50, "переприсвоєння\nна місці", bold=True,
                    fill="#eef7ee", stroke=FIELD, color=FIELD))
    f.append(fitbox(300, 160, 550, 50,
                    "capacity ≥ n ?  →  copy n у наявний блок  (інакше new[n])"))
    f.append(text(575, 232,
                  "жодного виділення, поки місткості вистачає; пік ≈ один блок",
                  size=13, color=FIELD))

    f.append(text(440, 286,
                  "У циклі присвоєнь перший варіант виділяє пам'ять щоразу, "
                  "другий — жодного разу після першої ітерації.",
                  size=13, color=INK))
    f.append(text(440, 310,
                  "Ціна економії — лише базова гарантія: перерване копіювання "
                  "лишає блок частково перезаписаним.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'assign-cost.svg'), W, H, *f,
           title="Ціна присвоєння: виділення проти переприсвоєння в місце")


def fig_hist_timeline():
    """Хроніка правил: що було фольклором, що пропозицією, а що нормою."""
    W, H = 900, 560
    f = []

    rows = [
        ("1991", "«правило трьох» — Маршалл Клайн, C++ FAQ", "порада спільноти", MUTED),
        ("2001-06-01", "Кеніг і Му уточнюють трійку (Dr. Dobb's)", "стаття", MUTED),
        ("2010-11-11", "N3203 Маурера ухвалено в Батавії", "увійшло в C++11", FIELD),
        ("C++11", "[depr.impldec]: «застаріле», але дозволене", "норма-компроміс", FIELD),
        ("2012-08-15", "«правило нуля» — Фернандеш, особистий блог", "допис", MUTED),
        ("2013-03-12", "N3578 Брауна: зробити п'ятірку нормою", "відхилено (EWG)", POS),
        ("2014-01-01", "N3839, та сама пропозиція для C++17", "не ухвалено", POS),
        ("донині", "[depr.impldec] лишається в Annex D", "чинна норма", FIELD),
    ]

    y0, dy, bh = 62, 56, 42
    for i, (date, what, badge, col) in enumerate(rows):
        y = y0 + i * dy
        f.append(fitbox(30, y, 132, bh, date, size=13, color=MUTED, fill="#ffffff",
                        stroke=FIELD if col is FIELD else LINE))
        f.append(fitbox(176, y, 452, bh, what, size=13))
        f.append(fitbox(648, y, 222, bh, badge, size=13, color=col,
                        fill="#ffffff", stroke=col))

    f.append(text(450, y0 + len(rows) * dy + 22,
                  "зелене — те, що записано в стандарті; червоне — те, що комітет не ухвалив",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'hist-timeline.svg'), W, H, *f,
           title="Хроніка трьох правил: слово спільноти й слово стандарту")


if __name__ == '__main__':
    fig_shallow_copy()
    fig_suppression()
    fig_rule_of_zero()
    fig_copy_and_swap_flow()
    fig_assign_cost()
    fig_hist_timeline()
    print('ok')
