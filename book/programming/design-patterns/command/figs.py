# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_flow():
    """Хто в кого стріляє: клієнт створює команду-об'єкт, викликач її зберігає
    й тисне execute(), команда всередині смикає одержувача. Викликач не знає
    ні одержувача, ні дії."""
    W, H = 860, 430
    f = []

    # чотири вертикальні "смуги" ролей — з великим запасом між ними
    lanes = [
        (110, "Клієнт", "складає команду\nй віддає викликачу"),
        (330, "Викликач", "тримає команду,\nтисне execute()"),
        (560, "Команда", "об'єкт-дія:\nexecute() / undo()"),
        (770, "Одержувач", "реальна робота:\nсвітло, файл, текст"),
    ]
    top = 70
    for cx, name, sub in lanes:
        f.append(fitbox(cx - 78, top, 156, 58, name, size=15, bold=True,
                        fill="#eef2f7"))
        f.append(mtext(cx, top + 92, sub.split("\n"), size=11.5, color=MUTED))

    # рівень стрілок нижчий за підписи-смуги, щоб не перетинати текст
    ay = top + 150

    # клієнт -> викликач: "ось команда"
    f.append(arrow(110 + 82, ay, 330 - 92, ay, color=NEG, sw=2))
    f.append(text((110 + 330) / 2, ay - 12, "new AddText(\"привіт\")", size=11.5, color=NEG))

    # викликач -> команда: execute()
    f.append(arrow(330 + 92, ay, 560 - 92, ay, color=POS, sw=2))
    f.append(text((330 + 560) / 2, ay - 12, "execute()", size=12, color=POS, bold=True))

    # команда -> одержувач: конкретний виклик
    f.append(arrow(560 + 92, ay, 770 - 82, ay, color=INK, sw=2))
    f.append(text((560 + 770) / 2, ay - 12, "doc.insert(...)", size=11.5))

    # довга дуга-«стіна незнання» від викликача до одержувача
    wall_y = ay + 92
    f.append(line(330, ay + 20, 330, wall_y + 26, color=MUTED, sw=1.2, dash="5 5"))
    f.append(line(770, ay + 20, 770, wall_y + 26, color=MUTED, sw=1.2, dash="5 5"))
    note = "Викликач НЕ знає ні одержувача, ні що саме робить команда — тільки .execute()"
    f.append(fitbox((330 + 770) / 2 - 250, wall_y + 30, 500, 40, note,
                    size=12, fill="#f6faf6", stroke=FIELD))

    render(os.path.join(IMG, 'command-flow.svg'), W, H, *f,
           title="Запит подорожує як окремий об'єкт")


def fig_undo():
    """Дві стопки: зроблене й скасоване. execute() кладе команду на «зроблене»;
    undo() знімає верхню, викликає її .undo() і перекладає на «скасоване»;
    redo() — навпаки. Нова команда після undo чистить «скасоване»."""
    W, H = 820, 470
    f = []

    colL = 210          # центр стопки "зроблене"
    colR = 610          # центр стопки "скасоване"
    bw = 240            # ширина картки
    base = 400          # низ стопок (кладемо знизу вгору)
    bh = 46
    gap = 8

    f.append(text(colL, 66, "Історія (зроблене)", size=15, bold=True))
    f.append(text(colR, 66, "Скасоване", size=15, bold=True))

    done = ["AddText(\"a\")", "AddText(\"b\")", "DeleteWord()"]
    undone = ["AddText(\"c\")"]

    def stack(cx, items, hot):
        frs = []
        for i, label in enumerate(items):
            y = base - (i + 1) * (bh + gap)
            fill = "#fff4f4" if (hot and i == len(items) - 1) else "#eef2f7"
            stroke = POS if (hot and i == len(items) - 1) else LINE
            frs.append(fitbox(cx - bw / 2, y, bw, bh, label, size=13,
                              fill=fill, stroke=stroke))
        return frs, base - len(items) * (bh + gap)

    dfr, dtop = stack(colL, done, hot=True)
    ufr, utop = stack(colR, undone, hot=True)
    f += dfr + ufr

    # верхівки підписуємо — з боку, не над карткою, щоб не накластися
    f.append(text(colL + bw / 2 + 16, dtop + bh / 2 + 4, "верх", size=11,
                  color=POS, anchor="start"))
    f.append(text(colR + bw / 2 + 16, utop + bh / 2 + 4, "верх", size=11,
                  color=POS, anchor="start"))

    # стрілка undo: верх «зроблене» -> верх «скасоване»
    uy = dtop - 22
    f.append(arrow(colL + bw / 2 + 6, uy, colR - bw / 2 - 6, uy, color=NEG, sw=2))
    f.append(text((colL + colR) / 2, uy - 10, "undo(): знімаємо верх, кличемо .undo()",
                  size=12, color=NEG, bold=True))

    # стрілка redo: назад
    ry = base + 30
    f.append(arrow(colR - bw / 2 - 6, ry, colL + bw / 2 + 6, ry, color=FIELD, sw=2))
    f.append(text((colL + colR) / 2, ry + 20, "redo(): повертаємо назад і .execute()",
                  size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, 'command-undo.svg'), W, H, *f,
           title="Undo / redo — дві стопки команд")


def fig_lineage():
    """Три віхи народження патерна до GoF: Ліберман 1985 (перша згадка
    команди-об'єкта), Меєр 1988 (перша реалізація undo/redo класами-командами),
    GoF 1994 (канонізація як поведінкового патерну). Вісь часу згори вниз."""
    W, H = 880, 560
    f = []

    # вертикальна вісь часу ліворуч
    ax = 150
    top, bot = 90, 500
    f.append(line(ax, top, ax, bot, color=INK, sw=2.2))
    f.append(arrow(ax, bot - 4, ax, bot + 20, color=INK, sw=2.2))
    f.append(text(ax, bot + 40, "час", size=12, color=MUTED))

    # три віхи: (рік, y, заголовок, рядки-опис, колір-акцент)
    marks = [
        (1985, 150, "Генрі Ліберман",
         ["стаття «There's more to menu systems",
          "than meets the screen» — перша згадка",
          "команди-об'єкта; про undo — побіжно"], NEG),
        (1988, 290, "Бертран Меєр",
         ["«Object-Oriented Software Construction»,",
          "§12.2 — перша РЕАЛІЗАЦІЯ undo/redo:",
          "класи-команди execute/undo + історія"], FIELD),
        (1994, 430, "«Банда чотирьох»",
         ["«Design Patterns» — КАНОНІЗАЦІЯ як",
          "поведінкового патерну; формулювання",
          "«загорнути запит в об'єкт»"], POS),
    ]

    boxL = ax + 70          # ліва межа картки-віхи
    boxW = 620
    boxH = 96
    for year, y, title, lines, col in marks:
        # вузол на осі
        f.append(circle(ax, y + boxH / 2, 9, fill="#ffffff", stroke=col, sw=2.6))
        # рік — ліворуч від осі
        f.append(text(ax - 24, y + boxH / 2 + 5, str(year), size=15, bold=True,
                      color=col, anchor="end"))
        # сполучна риска вузол → картка
        f.append(line(ax + 9, y + boxH / 2, boxL, y + boxH / 2, color=col, sw=1.8))
        # картка
        f.append(rect(boxL, y, boxW, boxH, fill=FILL, stroke=col, sw=1.8))
        f.append(text(boxL + 16, y + 26, title, size=15, bold=True, color=col,
                      anchor="start"))
        f.append(mtext(boxL + 16, y + 48, lines, size=11.5, color=INK,
                       anchor="start", lh=1.28))

    render(os.path.join(IMG, 'command-lineage.svg'), W, H, *f,
           title="Народження патерна Команда — три віхи до GoF")


def fig_editor_history():
    """History як маршрутизатор об'єктів між двома стопками. run(): execute +
    покласти на done + СТЕРТИ undone. undo(): зняти верх done, .undo(), на undone.
    redo(): зняти верх undone, .execute(), на done. Кожна команда — чорна скринька
    з двома ґудзиками; історія не знає, що всередині."""
    W, H = 900, 500
    f = []

    colL = 230          # центр стопки "зроблене"
    colR = 670          # центр стопки "скасоване"
    bw = 250            # ширина картки-команди
    bh = 44
    gap = 9
    base = 380          # низ стопок (кладемо знизу вгору)

    f.append(text(colL, 74, "done — зроблене", size=15, bold=True))
    f.append(text(colR, 74, "undone — скасоване", size=15, bold=True))

    done = ["AddText(0,\"привіт\")", "AddText(6,\" світе\")"]
    undone = ["DeleteLastWord()"]

    def stack(cx, items, hot):
        frs = []
        top_y = base
        for i, label in enumerate(items):
            y = base - (i + 1) * (bh + gap)
            top_y = y
            is_top = (i == len(items) - 1)
            fill = "#fff4f4" if (hot and is_top) else "#eef2f7"
            stroke = POS if (hot and is_top) else LINE
            frs.append(fitbox(cx - bw / 2, y, bw, bh, label, size=12.5,
                              fill=fill, stroke=stroke))
        return frs, top_y

    dfr, dtop = stack(colL, done, hot=True)
    ufr, utop = stack(colR, undone, hot=True)
    f += dfr + ufr

    # підпис "верх" збоку від верхніх карток (не над ними — щоб не накластися)
    f.append(text(colL + bw / 2 + 18, dtop + bh / 2 + 4, "верх", size=11,
                  color=POS, anchor="start"))
    f.append(text(colR + bw / 2 + 18, utop + bh / 2 + 4, "верх", size=11,
                  color=POS, anchor="start"))

    # стрілка undo: верх done -> верх undone (над стопками)
    uy = min(dtop, utop) - 30
    f.append(arrow(colL + bw / 2 + 8, uy, colR - bw / 2 - 8, uy, color=NEG, sw=2.2))
    f.append(text((colL + colR) / 2, uy - 12, "undo(): зняти верх, .undo(), сюди",
                  size=12, color=NEG, bold=True))

    # стрілка redo: верх undone -> верх done (нижче, зворотна)
    ry = base + 34
    f.append(arrow(colR - bw / 2 - 8, ry, colL + bw / 2 + 8, ry, color=FIELD, sw=2.2))
    f.append(text((colL + colR) / 2, ry + 20, "redo(): зняти верх, .execute(), сюди",
                  size=12, color=FIELD, bold=True))

    # інваріант: нова дія стирає undone — окрема рамка-примітка внизу
    note = "run(нова команда): execute + покласти на done + СТЕРТИ undone (redo-гілку відрізано)"
    nb = fitbox(W / 2 - 340, ry + 40, 680, 40, note, size=12,
                fill="#fdf0f0", stroke=POS, sw=1.6)
    f.append(nb)

    render(os.path.join(IMG, 'editor-history.svg'), W, H, *f,
           title="History: маршрут команд між двома стопками")


if __name__ == '__main__':
    fig_flow()
    fig_undo()
    fig_lineage()
    fig_editor_history()
    print("ok")
