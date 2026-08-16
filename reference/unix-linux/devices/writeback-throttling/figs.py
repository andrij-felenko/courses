# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
WARM = "#fff6e5"
RED = "#fdecea"
GREY = "#eceff1"


# ── 1. Та сама черга, різна кількість записів усередині ─────────────────────
def fig_read_behind_writeback():
    W, H = 1420, 620
    p = []

    p.append(line(W / 2, 40, W / 2, H - 30, color=MUTED, sw=1.2, dash="7 7"))

    SCALE = 22.0          # пікселів на мілісекунду очікування
    SLOT_W = 62
    N = 8

    def panel(cx, head, filled, wait_ms, wait_color, note):
        p.append(text(cx, 62, head, size=16, bold=True))

        x0 = cx - N * SLOT_W / 2.0
        for i in range(N):
            busy = i < filled
            p.append(rect(x0 + i * SLOT_W, 104, SLOT_W - 8, 50,
                          fill=(WARM if busy else GREY),
                          stroke=(POS if busy else MUTED),
                          sw=(1.8 if busy else 1.0), rx=4))
            if busy:
                p.append(text(x0 + i * SLOT_W + (SLOT_W - 8) / 2.0, 136,
                              "запис", size=12, color=POS))
        p.append(text(cx, 190, note, size=13, color=MUTED))

        p.append(text(x0, 268, "час до завершення читання", size=13,
                      color=MUTED, anchor="start"))
        bw = wait_ms * SCALE
        p.append(rect(x0, 292, bw, 40, fill=wait_color, stroke=LINE, sw=1.5, rx=5))
        p.append(text(x0 + bw + 14, 319, "%s мс" % wait_ms, size=16,
                      color=INK, bold=True, anchor="start"))

    panel(360, "Глибину зворотного запису не обмежено", 8, 19, RED,
          "таблиця команд носія зайнята повністю (у прикладі — 32 команди)")
    panel(1060, "Глибину зворотного запису обмежено", 2, 1.2, GREEN,
          "у таблиці лишається місце")

    p.append(text(W / 2, 430,
                  "Порядок подання в обох панелях однаковий.",
                  size=15, color=INK))
    p.append(text(W / 2, 462,
                  "Змінилася тільки кількість незавершених записів у носії.",
                  size=15, color=INK))

    render(os.path.join(IMG, 'read-behind-writeback.svg'), W, H, *p)


# ── 2. Чому мінімум, а не середнє ───────────────────────────────────────────
def fig_why_minimum():
    W, H = 1420, 640
    p = []

    p.append(line(W / 2, 40, W / 2, H - 30, color=MUTED, sw=1.2, dash="7 7"))

    BASE = 400.0          # лінія нуля затримки
    TARGET_H = 78.0       # висота цільової затримки
    BAR_W = 34
    GAP = 14

    def panel(cx, head, heights, verdict, hi_color):
        p.append(text(cx, 62, head, size=16, bold=True))

        n = len(heights)
        total = n * BAR_W + (n - 1) * GAP
        x0 = cx - total / 2.0

        lo = min(heights)
        for i, hgt in enumerate(heights):
            x = x0 + i * (BAR_W + GAP)
            is_min = (hgt == lo)
            p.append(rect(x, BASE - hgt, BAR_W, hgt,
                          fill=(hi_color if is_min else BLUE),
                          stroke=(POS if (is_min and hi_color is RED) else LINE),
                          sw=(2.0 if is_min else 1.2), rx=3))

        # вісь часу
        p.append(line(x0 - 20, BASE, x0 + total + 20, BASE, color=LINE, sw=1.6))
        p.append(text(cx, BASE + 30, "вікно спостереження 100 мс",
                      size=13, color=MUTED))

        # ціль
        p.append(line(x0 - 20, BASE - TARGET_H, x0 + total + 20, BASE - TARGET_H,
                      color=FIELD, sw=2.0, dash="8 6"))
        p.append(text(x0 + total + 30, BASE - TARGET_H - 12, "цільова",
                      size=12, color=FIELD, anchor="end"))

        imin = heights.index(lo)
        xmin = x0 + imin * (BAR_W + GAP) + BAR_W / 2.0
        p.append(text(xmin, BASE - lo - 16, "мінімум", size=12, color=INK))

        p.append(text(cx, BASE + 92, verdict, size=15, bold=True))

    panel(360, "Сплеск: черга наповнилась і спорожніла",
          [30, 152, 188, 22, 170, 44, 200, 60],
          "мінімум нижчий за ціль → глибину піднімають", GREEN)

    panel(1060, "Стояча черга: не спорожніла жодного разу",
          [124, 160, 142, 176, 130, 190, 148, 166],
          "мінімум вищий за ціль → глибину ділять навпіл", RED)

    render(os.path.join(IMG, 'why-minimum.svg'), W, H, *p)


# ── 3. Замкнена петля й три пороги ──────────────────────────────────────────
def fig_wbt_loop():
    W, H = 1400, 780
    p = []

    boxes = {}

    def box(key, cx, cy, lines, fill):
        f, w, h = textbox(cx, cy, lines, size=14, pad=16, fill=fill, stroke=LINE)
        p.append(f)
        boxes[key] = (cx, cy, w, h)

    box('meas', 350, 120,
        ["мінімум затримки читання", "за вікном 100 мс"], BLUE)
    box('cmp', 1030, 120,
        ["порівняння з цільовою затримкою", "2 мс без обертання · 75 мс з обертанням"], GREEN)
    box('step', 1030, 330,
        ["щабель гальмування", "перевищено → +1, глибина ÷ 2",
         "вклалися → −1, глибина вгору на крок"], WARM)
    box('depth', 350, 330,
        ["дозволена глибина", "незавершених записів"], GREY)

    def edge(a, b, dx=0.0, dy=0.0):
        ax, ay, aw, ah = boxes[a]
        bx, by, bw, bh = boxes[b]
        if abs(ay - by) < 1:                      # горизонтально
            x1 = ax + aw / 2 + 8 if bx > ax else ax - aw / 2 - 8
            x2 = bx - bw / 2 - 8 if bx > ax else bx + bw / 2 + 8
            p.append(arrow(x1, ay + dy, x2, by + dy))
        else:                                     # вертикально
            y1 = ay + ah / 2 + 8 if by > ay else ay - ah / 2 - 8
            y2 = by - bh / 2 - 8 if by > ay else by + bh / 2 + 8
            p.append(arrow(ax + dx, y1, bx + dx, y2))

    edge('meas', 'cmp')
    edge('cmp', 'step')
    edge('step', 'depth')
    edge('depth', 'meas')

    p.append(text(350, 232, "менше записів у носії — швидші читання",
                  size=13, color=MUTED, anchor="end"))

    # три пороги
    p.append(arrow(350, 330 + boxes['depth'][3] / 2 + 8, 350, 470))
    p.append(text(700, 452, "один лічильник незавершених записів, три пороги",
                  size=15, bold=True))

    tri = [("фоновий запис\nі сусіднє введення-виведення", "чверть глибини", RED),
           ("звичайний буферизований запис", "половина глибини", WARM),
           ("високий пріоритет\nі гальмування на брудних сторінках", "повна глибина", GREEN)]
    xs = [270, 700, 1130]
    for (title_, val, fill), cx in zip(tri, xs):
        f, w, h = textbox(cx, 546, title_.split("\n"), size=13, pad=14,
                          fill=fill, stroke=LINE)
        p.append(f)
        p.append(text(cx, 546 + h / 2 + 34, val, size=14, bold=True))

    p.append(line(150, 500, 1250, 500, color=MUTED, sw=1.0, dash="6 6"))

    p.append(text(700, 700,
                  "Понад свій поріг запит не отримує тега — той, хто подає, засинає",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'wbt-loop.svg'), W, H, *p)


if __name__ == '__main__':
    fig_read_behind_writeback()
    fig_why_minimum()
    fig_wbt_loop()
    print("ok")
