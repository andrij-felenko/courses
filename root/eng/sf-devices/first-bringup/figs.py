# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_ladder():
    """Драбина запуску: 6 сходинок знизу вгору, кожна спирається на попередню."""
    W, H = 720, 470
    frags = []
    steps = [
        ("Живлення", "правильна напруга на кожному виводі чіпа"),
        ("Тактування", "тактовий сигнал іде — ядро має від чого крокувати"),
        ("Ядро й перший вивід", "блимання = доказ життя (main() виконується)"),
        ("Консоль", "текст у термінал — система дістала голос"),
        ("Перша периферія", "по одному давачу за раз; спершу сканування шини"),
        ("Повний застосунок", "усе разом — коли кожна цеглина доведена окремо"),
    ]
    n = len(steps)
    x = 70
    bw = 560
    bh = 46
    gap = 20
    y0 = 70
    # знизу вгору: перший елемент списку — найнижча сходинка
    for i, (title, sub) in enumerate(steps):
        # рядок 0 (Живлення) внизу
        y = y0 + (n - 1 - i) * (bh + gap)
        hot = (i == 2)  # "ядро й перший вивід" — акцент (блимання)
        fill = "#eafaf0" if hot else FILL
        stroke = FIELD if hot else LINE
        frags.append(rect(x, y, bw, bh, fill=fill, stroke=stroke, sw=2 if hot else 1.5))
        frags.append(text(x + 16, y + 20, title, size=15, color=INK, anchor="start", bold=True))
        frags.append(text(x + 16, y + 38, sub, size=11, color=MUTED, anchor="start"))
        # номер-кружок
        frags.append(circle(x - 22, y + bh / 2, 13, fill=BG, stroke=stroke, sw=2))
        frags.append(text(x - 22, y + bh / 2 + 5, str(i + 1), size=13, color=stroke, bold=True))
        # стрілка вгору до наступної сходинки
        if i < n - 1:
            ax = x + bw + 34
            frags.append(arrow(ax, y + 6, ax, y - gap + 4))

    # підпис осі напрямку
    frags.append(text(x + bw + 34, y0 - gap - 4, "вище", size=11, color=MUTED))
    frags.append(text(x + bw + 34, y0 + (n - 1) * (bh + gap) + bh + 16, "нижче", size=11, color=MUTED))
    render(os.path.join(IMG, 'bringup-ladder.svg'), W, H, *frags,
           title="Драбина запуску: знизу вгору, кожна сходинка спирається на доведену нижче")


def fig_bisection():
    """Бісекція: 8 змін, поділ навпіл — 3 кроки замість 8."""
    W, H = 720, 400
    frags = []
    n = 8
    x0 = 90
    cellw = 60
    top = 90
    rowh = 88
    culprit = 5  # 0-based індекс винної зміни (6-та)

    def draw_row(y, lo, hi, label, active_lo, active_hi):
        # клітинки lo..hi
        for k in range(n):
            cx = x0 + k * cellw
            inside = active_lo <= k <= active_hi
            is_c = (k == culprit)
            if is_c and inside:
                fill, stroke = "#fdecea", POS
            elif inside:
                fill, stroke = FILL, LINE
            else:
                fill, stroke = "#f0f1f3", "#c4c9d0"
            frags.append(rect(cx, y, cellw - 8, 40, fill=fill, stroke=stroke,
                              sw=2 if (is_c and inside) else 1.3))
            tc = POS if (is_c and inside) else (INK if inside else "#aab0b8")
            frags.append(text(cx + (cellw - 8) / 2, y + 25, str(k + 1), size=13,
                              color=tc, bold=is_c and inside))
        frags.append(text(x0 - 16, y + 25, label, size=12, color=MUTED, anchor="end"))

    # рядок 1: усі 8 під підозрою, ділимо навпіл (1-4 | 5-8)
    draw_row(top, 0, 7, "крок 1", 0, 7)
    midx = x0 + 4 * cellw - 4
    frags.append(line(midx, top - 8, midx, top + 48, color=NEG, sw=2, dash="4,3"))
    frags.append(text(x0 + 4 * cellw + 130, top + 62,
                      "перевіряємо ліву половину — чисто → винне у правій", size=11,
                      color=MUTED, anchor="middle"))

    # рядок 2: лишилось 5-8, ділимо (5-6 | 7-8)
    y2 = top + rowh
    draw_row(y2, 0, 7, "крок 2", 4, 7)
    midx2 = x0 + 6 * cellw - 4
    frags.append(line(midx2, y2 - 8, midx2, y2 + 48, color=NEG, sw=2, dash="4,3"))
    frags.append(text(x0 + 4 * cellw + 130, y2 + 62,
                      "5–6 чи 7–8? ліва пара винна → лишилось двоє", size=11,
                      color=MUTED, anchor="middle"))

    # рядок 3: лишилось 5-6, ділимо -> винний 6
    y3 = top + 2 * rowh
    draw_row(y3, 0, 7, "крок 3", 4, 5)
    midx3 = x0 + 5 * cellw - 4
    frags.append(line(midx3, y3 - 8, midx3, y3 + 48, color=NEG, sw=2, dash="4,3"))
    frags.append(text(x0 + 4 * cellw + 130, y3 + 62,
                      "5 чи 6? винною лишається зміна 6", size=11,
                      color=POS, anchor="middle"))

    render(os.path.join(IMG, 'bisection.svg'), W, H, *frags,
           title="Бісекція: 8 змін — 3 поділи навпіл замість 8 перевірок")


def fig_smoke_lineage():
    """Родовід терміна «димовий тест»: судна → сантехніка → електроніка → ПЗ."""
    W, H = 760, 340
    frags = []
    axis_y = 150
    x_lo, x_hi = 70, 690
    frags.append(line(x_lo, axis_y, x_hi, axis_y, color=LINE, sw=2))
    frags.append(arrow(x_hi - 2, axis_y, x_hi + 8, axis_y))

    stations = [
        (0.02, "судна", "1836", "дим у корпус —\nде виходить, там щілина", True),
        (0.30, "сантехніка", "1875", "дим у труби —\nпробоїни й витоки", True),
        (0.62, "електроніка", "усталилось\nу XX ст.", "увімкнув плату —\nпішов дим — вимкни", False),
        (0.90, "тестування ПЗ", "кінець XX ст.", "швидка перевірка:\nсистема взагалі жива?", False),
    ]
    for frac, name, when, note, documented in stations:
        cx = x_lo + frac * (x_hi - x_lo)
        col = FIELD if documented else MUTED
        # вузол
        frags.append(circle(cx, axis_y, 9, fill=BG, stroke=col, sw=2.5))
        # назва етапу над віссю
        frags.append(text(cx, axis_y - 46, name, size=15, color=INK, bold=True))
        frags.append(text(cx, axis_y - 26, when, size=11.5, color=col))
        # образ під віссю
        frags.append(mtext(cx, axis_y + 34, note, size=11, color=MUTED, lh=1.25))

    # легенда: документоване vs фольклор
    ly = H - 26
    frags.append(circle(x_lo + 6, ly, 7, fill=BG, stroke=FIELD, sw=2.5))
    frags.append(text(x_lo + 20, ly + 4, "задокументована дата (першоджерело)", size=11,
                      color=MUTED, anchor="start"))
    frags.append(circle(x_lo + 366, ly, 7, fill=BG, stroke=MUTED, sw=2.5))
    frags.append(text(x_lo + 380, ly + 4, "запозичення — образ усталений, точна дата фольклорна",
                      size=11, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'smoke-lineage.svg'), W, H, *frags,
           title="Родовід «димового тесту»: той самий фокус мандрує галузями")


if __name__ == '__main__':
    fig_ladder()
    fig_bisection()
    fig_smoke_lineage()
    print("ok")
