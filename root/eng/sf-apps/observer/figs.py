# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_one_to_many():
    """Один суб'єкт — багато спостерігачів; він знає лише інтерфейс, не типи."""
    W, H = 760, 430
    frags = []

    # Суб'єкт зліва
    sub, sw_, sh_ = textbox(150, 150, ["Суб'єкт", "(джерело подій)"], size=15,
                            bold=True, fill="#fdecea", stroke=POS, pad=14, min_w=190)
    frags.append(sub)
    # список підписників усередині суб'єкта — підпис нижче рамки
    frags.append(text(150, 205, "тримає список: observers[]", size=12, color=MUTED))
    frags.append(text(150, 224, "не знає їхніх класів", size=12, color=MUTED))

    # три спостерігачі справа, з великим вертикальним запасом
    obs_data = [
        (560, 90,  ["Спостерігач A", "графік цін"]),
        (560, 215, ["Спостерігач B", "журнал у файл"]),
        (560, 340, ["Спостерігач C", "сигнал тривоги"]),
    ]
    for (ox, oy, lbl) in obs_data:
        b, _, _ = textbox(ox, oy, lbl, size=14, fill="#eafaf1", stroke=FIELD,
                          pad=12, min_w=200)
        frags.append(b)
        # стрілка сповіщення від суб'єкта до кожного (notify → update)
        frags.append(arrow(250, 150, ox - 105, oy, color=INK, sw=1.8))

    # підпис на пучку стрілок
    frags.append(text(400, 130, "notify(): для кожного observer.update()",
                     size=12, color=INK, italic=True))

    # знизу — напрям знання (стрілка залежності інша, ніж стрілка виклику)
    frags.append(text(380, 400, "суб'єкт викликає всіх через спільний інтерфейс Observer",
                     size=13, color=MUTED))

    render(os.path.join(IMG, 'one-to-many.svg'), W, H, *frags,
           title="Одна зміна стану — усі залежні оновлюються самі")


def fig_push_pull():
    """Дві моделі доставки: штовхати готові дані vs штовхати лише сигнал."""
    W, H = 780, 400
    frags = []

    # ── Ліва половина: PUSH ──
    frags.append(text(200, 60, "Проштовхування (push)", size=15, bold=True, color=POS))
    sp, _, _ = textbox(90, 150, "Суб'єкт", size=14, bold=True, fill="#fdecea",
                       stroke=POS, pad=12, min_w=120)
    frags.append(sp)
    op, _, _ = textbox(320, 150, "Спостерігач", size=14, fill="#eafaf1",
                       stroke=FIELD, pad=12, min_w=140)
    frags.append(op)
    frags.append(arrow(152, 150, 248, 150, color=INK, sw=2))
    frags.append(text(200, 138, "update(дані)", size=12, color=INK, italic=True))
    frags.append(text(200, 250, "усі дані летять одразу", size=12, color=MUTED))
    frags.append(text(200, 270, "спостерігач бере, що дали", size=12, color=MUTED))

    # роздільник
    frags.append(line(390, 40, 390, 360, color="#d0d0d0", sw=1.5, dash="4,4"))

    # ── Права половина: PULL ──
    frags.append(text(585, 60, "Витягування (pull)", size=15, bold=True, color=NEG))
    sp2, _, _ = textbox(690, 150, "Суб'єкт", size=14, bold=True, fill="#fdecea",
                        stroke=POS, pad=12, min_w=120)
    frags.append(sp2)
    op2, _, _ = textbox(470, 150, "Спостерігач", size=14, fill="#eafaf1",
                        stroke=FIELD, pad=12, min_w=140)
    frags.append(op2)
    # сигнал touch туди
    frags.append(arrow(628, 128, 542, 128, color=INK, sw=2))
    frags.append(text(585, 116, "update() — лише сигнал", size=12, color=INK, italic=True))
    # запит getState назад
    frags.append(arrow(542, 172, 628, 172, color=NEG, sw=2))
    frags.append(text(585, 195, "getState() — бере потрібне", size=12, color=NEG, italic=True))
    frags.append(text(585, 270, "спостерігач сам вирішує,", size=12, color=MUTED))
    frags.append(text(585, 288, "що саме прочитати", size=12, color=MUTED))

    render(os.path.join(IMG, 'push-pull.svg'), W, H, *frags,
           title="Дві моделі доставки: штовхати дані чи лише сигнал")


def fig_notify_guards():
    """Надійний notify(): знімок списку → прапорець reentrancy → ізоляція кожного update."""
    W, H = 860, 470
    frags = []

    # Вхід
    entry, _, _ = textbox(140, 70, "setTemp(23)", size=14, bold=True,
                          fill="#eaf0fd", stroke=NEG, pad=12, min_w=170)
    frags.append(entry)
    frags.append(arrow(140, 96, 140, 148, color=INK, sw=2))

    # Крок 1: прапорець reentrancy
    g1, gw1, gh1 = textbox(140, 185, ["вже сповіщаю?", "(прапорець)"], size=13,
                           fill="#fdf6e3", stroke=POS, pad=12, min_w=190)
    frags.append(g1)
    # гілка «так» — вихід одразу
    frags.append(arrow(140 + gw1 / 2, 185, 340, 185, color=POS, sw=2))
    frags.append(text(250, 172, "так →", size=12, color=POS, italic=True))
    ret, _, _ = textbox(430, 185, ["позначити", "«є нові дані»", "і вийти"], size=12,
                        fill="#fdecea", stroke=POS, pad=10, min_w=150)
    frags.append(ret)
    # гілка «ні» — вниз
    frags.append(arrow(140, 185 + gh1 / 2, 140, 250, color=FIELD, sw=2))
    frags.append(text(175, 225, "ні ↓", size=12, color=FIELD, italic=True))

    # Крок 2: знімок списку
    g2, _, gh2 = textbox(140, 285, ["зняти КОПІЮ", "списку підписників"], size=13,
                         fill="#eafaf1", stroke=FIELD, pad=12, min_w=210)
    frags.append(g2)
    frags.append(text(140, 322, "щоб відписка під час обходу не рвала цикл",
                     size=11, color=MUTED))
    frags.append(arrow(140, 285 + gh2 / 2 + 14, 140, 370, color=INK, sw=2))

    # Крок 3: цикл із ізоляцією
    loop_box = rect(30, 375, 480, 75, fill="#f7f7f7", stroke="#c8c8c8", sw=1.5, rx=8)
    frags.append(loop_box)
    frags.append(text(270, 396, "для кожного observer у копії:", size=13, bold=True))
    frags.append(text(270, 420, "try { o.update(this) }  catch { лог, ідемо далі }",
                     size=12, color=INK, italic=True))
    frags.append(text(270, 438, "чужа помилка НЕ зриває розсилку іншим",
                     size=11, color=POS))

    # Права колонка — пояснення трьох запобіжників
    frags.append(line(560, 55, 560, 450, color="#d0d0d0", sw=1.5, dash="4,4"))
    frags.append(text(710, 78, "Три запобіжники", size=15, bold=True))
    notes = [
        (120, "1. прапорець", "проти лавини й циклу A→B→A"),
        (200, "2. копія списку", "проти краху при відписці в ході"),
        (280, "3. try навколо update", "проти зриву чужим винятком"),
    ]
    for (ny, head, body) in notes:
        frags.append(text(710, ny, head, size=13, bold=True, color=NEG))
        frags.append(text(710, ny + 20, body, size=12, color=MUTED))

    render(os.path.join(IMG, 'notify-guards.svg'), W, H, *frags,
           title="Надійний notify(): копія списку, прапорець, ізоляція кожного update")


def fig_lineage():
    """Родовід ідеї: від MVC 1979 через патерн GoF до реактивних сигналів."""
    W, H = 980, 470
    frags = []

    axis_y = 250
    x0, x1 = 60, 920
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.5))
    frags.append(arrow(x1 - 2, axis_y, x1 + 2, axis_y, color=INK, sw=2.5))

    # (x, "up"/"down", рік, рядки-опис). Крайні вузли з відступом від країв,
    # щоб рамки (min_w≈174 → пів-ширина ~87) не вилазили за viewBox.
    nodes = [
        (110, "up",   "1979", ["MVC у Xerox PARC:", "вид підписується", "на модель"]),
        (290, "down", "1994", ["патерн Observer", "у книзі GoF", "(банда чотирьох)"]),
        (475, "up",   "1999", ["названо ваду —", "«застряглий", "слухач»"]),
        (655, "down", "2009", ["Rx у Microsoft:", "IObservable —", "потік подій"]),
        (835, "up",   "2010+", ["сигнали у", "фреймворках:", "тонка реактивність"]),
    ]

    for (nx, side, year, lines) in nodes:
        frags.append(circle(nx, axis_y, 8, fill="#fdecea", stroke=POS, sw=2.5))
        if side == "up":
            # рік — збоку від вузла, щоб вертикаль-виноска його не перетинала
            frags.append(text(nx + 30, axis_y - 8, year, size=15, bold=True, color=MUTED))
            b, _, _ = textbox(nx, axis_y - 96, lines, size=12.5, fill="#eafaf1",
                              stroke=FIELD, pad=11, min_w=174)
            frags.append(b)
            frags.append(line(nx, axis_y - 10, nx, axis_y - 46, color=MUTED, sw=1.4))
        else:
            frags.append(text(nx + 30, axis_y + 16, year, size=15, bold=True, color=MUTED))
            b, _, _ = textbox(nx, axis_y + 104, lines, size=12.5, fill="#eaf0fd",
                              stroke=NEG, pad=11, min_w=174)
            frags.append(b)
            frags.append(line(nx, axis_y + 10, nx, axis_y + 54, color=MUTED, sw=1.4))

    frags.append(text(W / 2, 452,
                     "одна ідея — «залежний оновлюється сам» — під різними іменами через десятиліття",
                     size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'lineage.svg'), W, H, *frags,
           title="Родовід спостерігача: від вікна на екрані до сигналів")


if __name__ == '__main__':
    fig_one_to_many()
    fig_push_pull()
    fig_notify_guards()
    fig_lineage()
    print("figures written")
