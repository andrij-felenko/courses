# -*- coding: utf-8 -*-
"""Фігури до теми «Точки налаштування й об'єкти-CPO»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_adl_vs_cpo():
    """Порівняння шляхів виклику: класичний ADL проти CPO."""
    W, H = 1040, 420
    out = []

    # Ліва колонка — Класичний ADL
    out.append(text(260, 40, "Класичний ADL (using std::swap)", size=16, color=INK, bold=True))

    b1, w1, h1 = textbox(260, 95, "using std::swap;\nswap(a, b);", size=14, pad=12, fill="#fff3e0", stroke="#e65100")
    out.append(b1)

    b2, w2, h2 = textbox(260, 190, ["1. Пошук у поточній області дій", "2. Пошук через ADL в неймспейсі аргументів", "3. Запасний варіант std::swap"], size=13, pad=12)
    out.append(b2)
    out.append(arrow(260, 95 + h1 / 2 + 4, 260, 190 - h2 / 2 - 4))

    b3, w3, h3 = textbox(260, 310, ["Недоліки:", "• Ризик викрадення ADL (hijacking)", "• Забудькуватість: виклик std::swap(a, b)", "• Помилки компіляції всередині шаблону"], size=13, pad=12, fill="#fdecea", stroke=POS)
    out.append(b3)
    out.append(arrow(260, 190 + h2 / 2 + 4, 260, 310 - h3 / 2 - 4))

    # Розділювач
    out.append(line(520, 30, 520, 390, color=MUTED, sw=1.5, dash="4,4"))

    # Права колонка — CPO
    out.append(text(780, 40, "CPO в C++20 (std::ranges::swap)", size=16, color=INK, bold=True))

    c1, cw1, ch1 = textbox(780, 95, "std::ranges::swap(a, b);", size=14, pad=12, fill="#e8f5e9", stroke="#2e7d32")
    out.append(c1)

    c2, cw2, ch2 = textbox(780, 190, ["1. Кваліфіковане викликання operator()", "2. Автоматична диспетчеризація всередині", "3. Захищений Poisoned Context для ADL"], size=13, pad=12)
    out.append(c2)
    out.append(arrow(780, 95 + ch1 / 2 + 4, 780, 190 - ch2 / 2 - 4))

    c3, cw3, ch3 = textbox(780, 310, ["Переваги:", "• Захист від викрадення ADL", "• Прямий виклик без using", "• Точні помилки на рівні концептів"], size=13, pad=12, fill="#eaf7ee", stroke=FIELD)
    out.append(c3)
    out.append(arrow(780, 190 + ch2 / 2 + 4, 780, 310 - ch3 / 2 - 4))

    render(os.path.join(IMG, 'adl-vs-cpo-resolution.svg'), W, H, *out,
           title="Пошук імен: класичний ADL проти Customization Point Objects (CPO)")


def fig_cpo_dispatch_ladder():
    """Ієрархія вибору реалізації всередині CPO (Dispatch Ladder)."""
    W = 1040
    M = 30
    head = ["Рівень", "Механізм перевірки", "Умова активації", "Результат"]
    cols = [140, 300, 340, 200]
    rows = [
        ["Рівень 1", "Метод-член класу", "t.begin() є валідним та повертає діапазон", "Виклик t.begin()"],
        ["Рівень 2", "ADL у Poisoned Context", "begin(t) визначено в неймспейсі T", "Виклик begin(t) через ADL"],
        ["Рівень 3", "Запасна реалізація", "T є масивом або має стандартний фолбек", "Обхід елементів або std::move"],
        ["Невдача", "Перевірка концепту", "Жодна умова не справдилася", "SFINAE / Concept Error"],
    ]
    HH, RH, GAP = 58, 64, 6
    H = 50 + HH + len(rows) * RH + 30
    out = []

    x = M
    for i, c in enumerate(cols):
        out.append(fitbox(x, 50, c - GAP, HH - GAP, head[i], size=14, bold=True, fill="#e8edf3"))
        x += c

    y = 50 + HH
    for ri, r in enumerate(rows):
        is_err = (ri == 3)
        x = M
        for i, cell in enumerate(r):
            if is_err:
                fill = "#fdecea"
                col = POS
            elif ri == 0:
                fill = "#e8f5e9"
                col = INK
            elif ri == 1:
                fill = "#eef4ff"
                col = INK
            else:
                fill = "#fff8e1"
                col = INK

            out.append(fitbox(x, y, cols[i] - GAP, RH - GAP, cell, size=13,
                              bold=(i == 0), color=col, fill=fill))
            x += cols[i]
        y += RH

    render(os.path.join(IMG, 'cpo-dispatch-ladder.svg'), W, H, *out,
           title="Ієрархія вибору реалізації всередині CPO (Dispatch Ladder)")


def fig_tag_invoke_architecture():
    """Архітектура tag_invoke: єдиний вузол ADL для всіх точок налаштування."""
    W, H = 1000, 380
    out = []

    # Три CPO / теги вгорі
    t1, tw1, th1 = textbox(200, 80, "exec::connect\n(Tag Object 1)", size=13, pad=12, fill="#eef4ff", stroke=NEG)
    t2, tw2, th2 = textbox(500, 80, "exec::start\n(Tag Object 2)", size=13, pad=12, fill="#eef4ff", stroke=NEG)
    t3, tw3, th3 = textbox(800, 80, "exec::set_value\n(Tag Object 3)", size=13, pad=12, fill="#eef4ff", stroke=NEG)

    out.append(t1)
    out.append(t2)
    out.append(t3)

    # Єдиний диспетчер у центрі
    m, mw, mh = textbox(500, 210, ["Єдина функція диспетчеризації", "tag_invoke(tag, target, args...)", "(ADL пошук лише одного імені)"], size=14, pad=16, fill="#fff3e0", stroke="#e65100", bold=True)
    out.append(m)

    out.append(arrow(200, 80 + th1 / 2 + 4, 500 - mw / 4, 210 - mh / 2 - 4))
    out.append(arrow(500, 80 + th2 / 2 + 4, 500, 210 - mh / 2 - 4))
    out.append(arrow(800, 80 + th3 / 2 + 4, 500 + mw / 4, 210 - mh / 2 - 4))

    # Користувацькі перевантаження внизу
    u1, uw1, uh1 = textbox(300, 320, "friend void tag_invoke(connect_t,\n  MySender&&, MyReceiver&&)", size=12, pad=10, fill="#eaf7ee", stroke=FIELD)
    u2, uw2, uh2 = textbox(700, 320, "friend void tag_invoke(set_value_t,\n  MyReceiver&&, Values...)", size=12, pad=10, fill="#eaf7ee", stroke=FIELD)

    out.append(u1)
    out.append(u2)

    out.append(arrow(500 - mw / 4, 210 + mh / 2 + 4, 300, 320 - uh1 / 2 - 4))
    out.append(arrow(500 + mw / 4, 210 + mh / 2 + 4, 700, 320 - uh2 / 2 - 4))

    render(os.path.join(IMG, 'tag-invoke-architecture.svg'), W, H, *out,
           title="Архітектура tag_invoke: єдиний вузол ADL для всіх точок налаштування")


if __name__ == '__main__':
    fig_adl_vs_cpo()
    fig_cpo_dispatch_ladder()
    fig_tag_invoke_architecture()
    print("ok")
