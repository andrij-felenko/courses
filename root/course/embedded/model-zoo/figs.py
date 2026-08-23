# -*- coding: utf-8 -*-
"""Фігури до теми «Зоопарк моделей детекції» (як читати назви моделей і вибирати).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Перший розріз зоопарку: яка задача? ───────────────────────────────────
def fig_tasks():
    """Чотири задачі зору від легшої до важчої: класифікація (один ярлик на
    кадр), детекція (рамки + класи), сегментація (маска пікселів), трекінг
    (та сама ціль у часі). Назва моделі насамперед каже, яку з них вона
    розв'язує — і ціна росте зліва направо."""
    W, H = 900, 320
    f = [text(W / 2, 30, "Перший розріз: яку задачу розв'язує модель", size=17, bold=True)]

    cells = [
        ("КЛАСИФІКАЦІЯ", "що в кадрі?", "один ярлик\n«людина 0.9»", FIELD),
        ("ДЕТЕКЦІЯ", "що і ДЕ?", "рамки + класи\n«людина тут»", NEG),
        ("СЕГМЕНТАЦІЯ", "які саме пікселі?", "маска по контуру\nкожен піксель", POS),
        ("ТРЕКІНГ", "та сама ціль у часі", "ID + траєкторія\nкадр за кадром", INK),
    ]
    bw, gap = 190, 24
    x0 = (W - (bw * 4 + gap * 3)) / 2
    for i, (name, q, out, col) in enumerate(cells):
        x = x0 + i * (bw + gap)
        f.append(rect(x, 80, bw, 150, fill=BG, stroke=col, sw=2))
        f.append(text(x + bw / 2, 108, name, size=13, bold=True, color=col))
        f.append(text(x + bw / 2, 132, q, size=11, color=MUTED))
        f.append(mtext(x + bw / 2, 162, out, size=12))
        if i < 3:
            f.append(arrow(x + bw + 2, 155, x + bw + gap - 2, 155))

    f.append(text(W / 2, 268, "дешевше ◄———————————————————► дорожче (більше обчислень)",
                  size=12, color=MUTED))
    f.append(text(W / 2, H - 18,
                  "для дрона, що цілиться, головна — ДЕТЕКЦІЯ: де об'єкт у кадрі",
                  size=12, color=INK))
    return render(os.path.join(IMG, "tasks.svg"), W, H, *f)


# ── 2. Анатомія назви: backbone + (neck) + head ──────────────────────────────
def fig_anatomy():
    """Чому назв так багато: детектор збирають із кубиків. Backbone (хребет)
    видобуває ознаки — його часто беруть готовий (MobileNet, ResNet). Neck
    зводить ознаки різних масштабів. Head (голова) видає рамки. «MobileNet-SSD»
    = хребет MobileNet + голова SSD. Звідси комбінаторика імен."""
    W, H = 880, 360
    f = [text(W / 2, 30, "Чому назв так багато: модель — це конструктор", size=17, bold=True)]

    # конвеєр кубиків
    blocks = [
        ("КАДР", "вхід", MUTED, 70),
        ("BACKBONE\n(хребет)", "видобуває ознаки\nMobileNet · ResNet", NEG, 150),
        ("NECK\n(шия)", "зводить масштаби\nпіраміда ознак", FIELD, 190),
        ("HEAD\n(голова)", "видає рамки\nSSD · YOLO-head", POS, 190),
        ("РАМКИ", "клас + рамка\n+ упевненість", MUTED, 70),
    ]
    x = 30
    cy = 150
    for i, (name, sub, col, bw) in enumerate(blocks):
        bh = 96
        f.append(rect(x, cy - bh / 2, bw, bh, fill=BG, stroke=col, sw=2))
        f.append(mtext(x + bw / 2, cy - 14, name, size=12, bold=True, color=col))
        f.append(mtext(x + bw / 2, cy + 18, sub, size=10, color=MUTED))
        if i < len(blocks) - 1:
            f.append(arrow(x + bw + 2, cy, x + bw + 22, cy))
        x += bw + 24

    # підпис-приклад
    f.append(fitbox(W / 2 - 290, 244, 580, 60,
                    "«MobileNet-SSD» = хребет MobileNet + голова SSD\n«YOLOv8» = свій хребет + своя голова, навчені разом",
                    size=13, bold=True, fill=FILL, stroke=LINE))
    f.append(text(W / 2, H - 16,
                  "переставляєш хребти й голови — дістаєш десятки назв; найдорожчий за обчисленнями — хребет",
                  size=12, color=INK))
    return render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 3. Центральний компроміс: швидкість ↔ точність ↔ розмір ──────────────────
def fig_tradeoff():
    """Головний закон зоопарку. Варіанти n/s/m/l/x однієї родини — це одна
    модель у різних «вагах»: більший = точніший, але повільніший і важчий.
    Виграш у точності спадає (n→s багато, l→x майже нічого), а ціна тактів
    росте лінійно. Дрон сидить ліворуч: бере найменший варіант, що ще влучає."""
    W, H = 820, 440
    f = [text(W / 2, 30, "Центральний компроміс: швидкість ↔ точність ↔ розмір", size=17, bold=True)]

    # осі
    ox, oy = 90, 360            # початок (лівий-низ)
    ax, ay = 740, 70            # межі
    f.append(line(ox, oy, ax, oy, color=LINE, sw=1.6))   # X
    f.append(line(ox, oy, ox, ay, color=LINE, sw=1.6))   # Y
    f.append(text((ox + ax) / 2, oy + 38, "обчислення / такти на кадр  (більше →)", size=12, color=INK))
    f.append(text(ox - 60, (oy + ay) / 2, "точність", size=12, color=INK, anchor="middle"))
    f.append(text(ox - 60, (oy + ay) / 2 + 16, "(вище ↑)", size=11, color=MUTED, anchor="middle"))

    # крива діминішинг-рітернс: точки n,s,m,l,x
    pts = [(0.10, 0.62, "n", "найменший\nшвидкий"),
           (0.24, 0.80, "s", ""),
           (0.46, 0.90, "m", ""),
           (0.70, 0.955, "l", ""),
           (1.00, 0.985, "x", "найбільший\nточний")]
    px = [ox + p[0] * (ax - ox) for p in pts]
    py = [oy - p[1] * (oy - ay) for p in pts]
    # лінія кривої
    for i in range(len(pts) - 1):
        f.append(line(px[i], py[i], px[i + 1], py[i + 1], color=MUTED, sw=2))
    for i, (_, _, lab, note) in enumerate(pts):
        col = FIELD if i == 0 else (POS if i == len(pts) - 1 else NEG)
        f.append(circle(px[i], py[i], 8, fill=BG, stroke=col, sw=2.4))
        f.append(text(px[i], py[i] - 16, lab, size=13, bold=True, color=col))
        if note:
            f.append(mtext(px[i] + (10 if i == 0 else -10), py[i] + 26, note,
                           size=10, color=MUTED, anchor="start" if i == 0 else "end"))

    # зона дрона — смуга малих обчислень уздовж осі X, ПІД кривою (не закриває точки)
    zx0, zx1 = ox + 2, px[2]
    f.append(rect(zx0, 298, zx1 - zx0, 46, fill="#eef6ef", stroke=FIELD, sw=1.4))
    f.append(text((zx0 + zx1) / 2, 317, "зона дрона", size=12, bold=True, color=FIELD))
    f.append(text((zx0 + zx1) / 2, 334, "найменший, що ще влучає", size=10, color=MUTED))
    # пунктир-стеля бюджету тактів
    f.append(line(px[2], oy, px[2], py[2] - 16, color=FIELD, sw=1.2, dash="5 4"))

    f.append(text(W / 2, H - 14,
                  "точність насичується (n→s багато, l→x майже нічого), а такти ростуть весь час",
                  size=12, color=INK))
    return render(os.path.join(IMG, "tradeoff.svg"), W, H, *f)


# ── 4. Родовід YOLO: одна назва, багато рук ──────────────────────────────────
def fig_yolo_lineage():
    """Часова смуга родини YOLO. До 2020-го гілку веде один автор (Редмон +
    Фархаді, Університет Вашингтона): v1→v2→v3. У лютому 2020-го Редмон
    публічно покидає зір через військові застосунки й стеження — стовбур
    обривається. Далі назву підхоплюють РІЗНІ руки: v4 (Бочковський +
    тайванські дослідники, рецензована стаття) і паралельно бренд Ultralytics
    (v5/v8/v11, без рецензованих статей, спірна нумерація). Звідси: «YOLO» —
    родина, а не модель."""
    W, H = 900, 470
    f = [text(W / 2, 30, "Родовід YOLO: одна назва, багато рук", size=17, bold=True)]

    # вісь часу
    ox, ax = 70, 830
    axis_y = 250
    f.append(line(ox, axis_y, ax, axis_y, color=LINE, sw=1.8))
    f.append(arrow(ax - 4, axis_y, ax + 8, axis_y))
    years = [(2015, "2015"), (2016, "2016"), (2018, "2018"),
             (2020, "2020"), (2023, "2023"), (2024, "2024")]
    yx = {y: ox + (y - 2014) / (2025 - 2014) * (ax - ox - 30) for y, _ in years}
    for y, lab in years:
        f.append(line(yx[y], axis_y - 5, yx[y], axis_y + 5, color=LINE, sw=1.4))
        f.append(text(yx[y], axis_y + 22, lab, size=11, color=MUTED))

    # стовбур Редмона/Фархаді (над віссю) — v1,v2,v3
    trunk = [(2015, "v1", "Редмон,\nФархаді"), (2016, "v2", ""), (2018, "v3", "")]
    for y, lab, who in trunk:
        f.append(circle(yx[y], axis_y - 70, 16, fill=BG, stroke=FIELD, sw=2.6))
        f.append(text(yx[y], axis_y - 65, lab, size=12, bold=True, color=FIELD))
        f.append(line(yx[y], axis_y - 54, yx[y], axis_y - 5, color=FIELD, sw=1.2, dash="4 3"))
        if who:
            f.append(mtext(yx[y], axis_y - 104, who, size=10, color=FIELD, bold=True))
    f.append(line(yx[2015], axis_y - 70, yx[2018], axis_y - 70, color=FIELD, sw=2))

    # точка розриву — лютий 2020
    bx = yx[2020] - 14
    f.append(line(bx, axis_y - 96, bx, axis_y + 96, color=POS, sw=2, dash="6 4"))
    bb, bw_, bh_ = textbox(bx, axis_y - 132, "лют. 2020:\nРедмон покидає зір\n(військове + стеження)",
                           size=10, bold=True, fill="#fdecea", stroke=POS, color=POS, pad=7)
    f.append(bb)

    # гілка v4 — Бочковський + Тайвань (рецензована)
    f.append(circle(yx[2020] + 14, axis_y - 70, 16, fill=BG, stroke=NEG, sw=2.6))
    f.append(text(yx[2020] + 14, axis_y - 65, "v4", size=12, bold=True, color=NEG))
    f.append(mtext(yx[2020] + 14, axis_y - 104,
                   "Бочковський +\nтайв. дослідники\n(є стаття)", size=9, color=NEG, bold=True))

    # гілка Ultralytics (під віссю) — v5,v8,v11
    ult = [(2020, "v5"), (2023, "v8"), (2024, "v11")]
    for y, lab in ult:
        xx = yx[y] + (16 if y == 2020 else 0)
        f.append(circle(xx, axis_y + 78, 16, fill=BG, stroke=POS, sw=2.6))
        f.append(text(xx, axis_y + 83, lab, size=12, bold=True, color=POS))
        f.append(line(xx, axis_y + 5, xx, axis_y + 62, color=POS, sw=1.2, dash="4 3"))
    f.append(line(yx[2020] + 16, axis_y + 78, yx[2024], axis_y + 78, color=POS, sw=2))
    f.append(mtext(yx[2023], axis_y + 120,
                   "бренд Ultralytics: без рецензованих статей,\nспірна нумерація й ліцензії",
                   size=10, color=POS, bold=True))

    f.append(text(W / 2, H - 16,
                  "до 2020-го — один стовбур; далі назву ведуть різні руки → «YOLO» це РОДИНА, а не модель",
                  size=12, color=INK))
    return render(os.path.join(IMG, "yolo-lineage.svg"), W, H, *f)


if __name__ == "__main__":
    fig_tasks()
    fig_anatomy()
    fig_tradeoff()
    fig_yolo_lineage()
    print("OK: 4 фігури у", IMG)
