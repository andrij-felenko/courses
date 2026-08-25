# -*- coding: utf-8 -*-
"""Фігури до теми «Структуровані зв'язування: auto [a, b]»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_machine():
    """Оголошення породжує ОДНУ приховану змінну; імена — псевдоніми її частин."""
    W, H = 1000, 470
    out = []

    b0, w0, h0 = textbox(W / 2, 70, "auto& [k, v] = *it;", size=19, pad=16, bold=True)
    out.append(b0)
    out.append(text(W / 2, 70 - h0 / 2 - 16, "що написано в коді", size=13, color=MUTED))

    out.append(arrow(W / 2, 70 + h0 / 2 + 6, W / 2, 155))
    out.append(text(W / 2 + 200, 122, "що з цього робить компілятор", size=13, color=MUTED))

    b1, w1, h1 = textbox(W / 2, 200,
                         ["auto& e = *it;",
                          "e — справжня змінна; імені в неї немає"],
                         size=16, pad=16, fill="#eef4ff", stroke=NEG)
    out.append(b1)

    lx, rx = 250, 750
    out.append(arrow(W / 2 - 90, 200 + h1 / 2 + 6, lx, 300 - 34))
    out.append(arrow(W / 2 + 90, 200 + h1 / 2 + 6, rx, 300 - 34))

    b2, _, h2 = textbox(lx, 300, ["k", "інше ім'я для e.first"], size=16, pad=14)
    b3, _, h3 = textbox(rx, 300, ["v", "інше ім'я для e.second"], size=16, pad=14)
    out.append(b2)
    out.append(b3)

    b4, _, _ = textbox(W / 2, 410,
                       ["жодної нової змінної, крім e:",
                        "k і v не копіюють нічого й не займають власної пам'яті"],
                       size=15, pad=14, fill="#eaf7ee", stroke=FIELD)
    out.append(b4)

    render(os.path.join(IMG, 'binding-machine.svg'), W, H, *out,
           title="Одна прихована змінна і два імені для її частин")


def fig_three_cases():
    """Три способи, якими компілятор знаходить частини об'єкта."""
    W = 1180
    M = 30
    head = ["коли застосовується", "скільки імен\nмає бути",
            "як компілятор дістає\ni-ту частину", "що дає decltype(iм'я)"]
    cols = [330, 200, 300, 290]
    rows = [
        ["E — масив T[N]", "рівно N", "e[i]", "T — тип елемента"],
        ["std::tuple_size<E>\n— повний тип",
         "стільки, скільки каже\nstd::tuple_size<E>::value",
         "e.get<i>()\nабо get<i>(e) через ADL",
         "std::tuple_element<i, E>::type\n(може бути посиланням)"],
        ["усі нестатичні поля E\nлежать в одному класі",
         "скільки полів",
         "e.поле\n(у порядку оголошення)",
         "тип поля"],
    ]
    HH, RH, GAP = 78, 88, 8
    H = 58 + HH + len(rows) * RH + 42
    out = []

    x = M
    for i, c in enumerate(cols):
        out.append(fitbox(x, 58, c - GAP, HH - GAP, head[i], size=15, bold=True,
                          fill="#e8edf3"))
        x += c

    y = 58 + HH
    for r in rows:
        x = M
        for i, cell in enumerate(r):
            fill = "#eef4ff" if i == 0 else "#f7f9fb"
            out.append(fitbox(x, y, cols[i] - GAP, RH - GAP, cell, size=15,
                              bold=(i == 0), fill=fill))
            x += cols[i]
        y += RH

    out.append(text(W / 2, H - 16,
                    "порядок перевірки саме такий: масив → tuple_size → поля; "
                    "жоден із них не «майже підходить»",
                    size=13, color=MUTED))

    render(os.path.join(IMG, 'three-cases.svg'), W, H, *out,
           title="Звідки компілятор знає, на які частини ділити")


def fig_declarator():
    """Декларатор описує приховану e, а не окремі імена."""
    W = 1160
    M = 30
    head = ["як написано", "чим стає e", "чи копіюється\nувесь об'єкт",
            "якщо праворуч тимчасовий"]
    cols = [290, 250, 250, 310]
    rows = [
        ["auto [a, b] = x;", "auto e = x;", "так, один раз", "копіюється в e"],
        ["const auto [a, b] = x;", "const auto e = x;",
         "так; a і b незмінні", "копіюється в e"],
        ["auto& [a, b] = x;", "auto& e = x;", "ні", "не компілюється"],
        ["const auto& [a, b] = x;", "const auto& e = x;", "ні",
         "життя подовжено\nдо кінця області"],
        ["auto&& [a, b] = x;", "auto&& e = x;", "ні",
         "життя подовжено\nдо кінця області"],
    ]
    HH, RH, GAP = 72, 74, 8
    H = 58 + HH + len(rows) * RH + 42
    out = []

    x = M
    for i, c in enumerate(cols):
        out.append(fitbox(x, 58, c - GAP, HH - GAP, head[i], size=15, bold=True,
                          fill="#e8edf3"))
        x += c

    y = 58 + HH
    for ri, r in enumerate(rows):
        x = M
        for i, cell in enumerate(r):
            if i == 0:
                fill = "#eef4ff"
            elif ri == 2 and i == 3:
                fill = "#fdecea"
            else:
                fill = "#f7f9fb"
            out.append(fitbox(x, y, cols[i] - GAP, RH - GAP, cell, size=15,
                              bold=(i == 0),
                              color=(POS if ri == 2 and i == 3 else INK),
                              fill=fill))
            x += cols[i]
        y += RH

    out.append(text(W / 2, H - 16,
                    "форму «одне за посиланням, друге копією» записати неможливо: "
                    "декларатор один на всіх",
                    size=13, color=MUTED))

    render(os.path.join(IMG, 'declarator-forms.svg'), W, H, *out,
           title="Що насправді описує auto, & і const перед дужками")


def fig_get_overloads():
    """Яке перевантаження get вибере компілятор для кожної форми оголошення."""
    W = 1260
    M = 30
    head = ["як написано", "тип прихованої e", "з якою категорією\ne йде у get",
            "яке перевантаження\nвибереться", "якщо його не написати"]
    cols = [300, 215, 185, 205, 295]
    rows = [
        ["auto [u, tag] = s;", "Sample", "xvalue", "get() &&",
         "візьметься const&:\nкопія замість\nпереміщення"],
        ["auto& [u, tag] = s;", "Sample&", "lvalue", "get() &",
         "помилка компіляції"],
        ["const auto& [u, tag] = s;", "const Sample&", "lvalue", "get() const&",
         "помилка компіляції"],
        ["auto&& [u, tag] = read();", "Sample&&", "xvalue", "get() &&",
         "візьметься const&:\nкопія замість\nпереміщення"],
    ]
    HH, RH, GAP = 74, 86, 8
    H = 58 + HH + len(rows) * RH + 42
    out = []

    x = M
    for i, c in enumerate(cols):
        out.append(fitbox(x, 58, c - GAP, HH - GAP, head[i], size=15, bold=True,
                          fill="#e8edf3"))
        x += c

    y = 58 + HH
    for ri, r in enumerate(rows):
        x = M
        for i, cell in enumerate(r):
            if i == 0:
                fill = "#eef4ff"
            elif i == 4:
                fill = "#fdecea"
            else:
                fill = "#f7f9fb"
            out.append(fitbox(x, y, cols[i] - GAP, RH - GAP, cell, size=15,
                              bold=(i == 0),
                              color=(POS if i == 4 else INK),
                              fill=fill))
            x += cols[i]
        y += RH

    out.append(text(W / 2, H - 16,
                    "категорію дає ТИП e, а не те, що в e є ім'я: "
                    "посилання-lvalue → lvalue, усе інше → xvalue",
                    size=13, color=MUTED))

    render(os.path.join(IMG, 'get-overloads.svg'), W, H, *out,
           title="Який із трьох get дістане частину")


fig_machine()
fig_three_cases()
fig_declarator()
fig_get_overloads()
print("ok")
