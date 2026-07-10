# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ACC = "#7a4ea8"     # фіолетовий — акцент рішення
ACCBG = "#f3edfb"
HOTBG = "#fdecea"   # тло гарячого листка (В,В)
GREENBG = "#eef6ef"
BLUEBG = "#eaf0fd"
GREYBG = "#eef1f5"


def vtext(x, y, s, size=11, color=MUTED):
    """Вертикальний підпис осі (поворот -90)."""
    return ('<text x="%.1f" y="%.1f" transform="rotate(-90 %.1f %.1f)" '
            'font-family="%s" font-size="%d" fill="%s" text-anchor="middle">%s</text>'
            % (x, y, x, y, FONT, size, color, esc(s)))


# ── dh-utility-tree: дерево корисності Digital Homes ───────────────────────────
# Ідея: розмите «зробити DH добрим» розкладається згори вниз на атрибути →
# конкретні сценарії-листки, і кожен листок дістає пару (важливість, складність).
# Драйвери — не всі листки, а лише червоні (В,В): водночас важливі й важкі. Саме
# вони формуватимуть структуру. Решту помічаємо, але задля них будову не гнемо.

def fig_utility_tree():
    W, H = 940, 580
    p = []

    # корінь
    rootx, rooty = 118, 310
    root_body, rw, rh = textbox(rootx, rooty, "Корисність\nDigital Homes", size=12.5,
                                pad=12, fill=ACCBG, stroke=ACC, sw=2, color=ACC, bold=True)

    # атрибути-гілки та їхні листки: (текст, y, важливість, складність)
    branches = [
        ("Доступність", 122, [
            ("хмара офлайн добу → дім живий", 92, "В", "В"),
            ("хмара впала → апка в LAN бачить дім", 152, "В", "С"),
        ]),
        ("Надійність", 212, [
            ("«відчинити замок» — рівно раз", 212, "В", "В"),
        ]),
        ("Змінюваність", 302, [
            ("новий тип пристрою — без правки ядра", 272, "В", "В"),
            ("нове правило — самим користувачем", 332, "С", "С"),
        ]),
        ("Швидкодія", 422, [
            ("вимикач → світло ≤ 100 мс", 392, "В", "С"),
            ("флот 5 млн: телеметрія встигає", 452, "С", "В"),
        ]),
        ("Безпека", 512, [
            ("відеопотік — лише власнику", 512, "В", "В"),
        ]),
    ]

    lx = 585           # ліва межа листків
    leafw = 330
    bx = 320           # центр гілок

    # 1) спершу лінії (щоб рамки лягли поверх кінців ліній)
    branch_boxes = []
    for aname, ay, leaves in branches:
        ab, aw, ah = textbox(bx, ay, aname, size=11.5, pad=9,
                             fill=GREYBG, stroke=INK, sw=1.4, color=INK, bold=True)
        branch_boxes.append((ab, aw, ah, ay, leaves))
        # корінь → гілка (кінець біля лівої межі гілки)
        p.append(line(rootx + rw / 2, rooty, bx - aw / 2 - 4, ay, color=MUTED, sw=1.5))
        # гілка → кожен листок
        for txt, ly, imp, cmx in leaves:
            p.append(line(bx + aw / 2 + 4, ay, lx - 5, ly, color="#c8ccd2", sw=1.2))

    # 2) корінь і гілки поверх ліній
    p.append(root_body)
    for ab, aw, ah, ay, leaves in branch_boxes:
        p.append(ab)

    # 3) листки з парою (важливість, складність)
    for aname, ay, leaves in branches:
        for txt, ly, imp, cmx in leaves:
            hot = (imp == "В" and cmx == "В")
            fill = HOTBG if hot else BG
            stroke = POS if hot else "#c8ccd2"
            p.append(rect(lx, ly - 17, leafw, 34, fill=fill, stroke=stroke,
                          sw=1.6 if hot else 1.1, rx=7))
            p.append(text(lx + 12, ly + 4, txt, size=10, color=INK, anchor="start",
                          bold=hot))
            tag = "(%s, %s)" % (imp, cmx)
            p.append(text(lx + leafw - 12, ly + 4, tag, size=10,
                          color=POS if hot else MUTED, anchor="end", bold=hot))

    # легенда
    p.append(text(lx, H - 32, "(важливість, складність):  В — високо · С — середньо · Н — низько",
                  size=9.5, color=MUTED, anchor="start"))
    p.append(text(lx, H - 14, "червоні листки (В, В) — важливі І важкі: це архітектурні драйвери",
                  size=9.5, color=POS, anchor="start"))

    render(os.path.join(OUT, "dh-utility-tree.svg"), W, H, *p,
           title="Дерево корисності Digital Homes: від «зробити добре» до драйверів")


# ── priority-quadrant: чому саме (В,В) ─────────────────────────────────────────
# Ідея: важливість сама по собі не виділяє драйвера. Друга вісь — складність для
# структури — розводить важливі сценарії на «вийде й так» (ліворуч) і «доведеться
# будувати» (праворуч). Небезпека й уся увага живуть у верхньому правому куті.

def fig_priority_quadrant():
    W, H = 780, 520
    p = []

    gx, gy, cw, ch = 155, 90, 285, 170   # сітка 2×2

    cells = [
        # (col, row, tло, рамка, колір-тексту, текст)
        (0, 0, GREENBG, FIELD, INK, "Вийде саме собою.\nСтруктура дає це легко —\nне гнути будову задля цього."),
        (1, 0, HOTBG, POS, POS, "(В, В) — ДРАЙВЕРИ\nсюди йде вся увага:\nтут вирішується доля системи"),
        (0, 1, GREYBG, MUTED, MUTED, "Шум.\nНе витрачати на це\nдорогу ранню увагу."),
        (1, 1, BLUEBG, NEG, INK, "Важко, та не болить.\nМожна програти —\nпереробка дешева."),
    ]
    for col, row, bg, br, tc, txt in cells:
        x = gx + col * cw
        y = gy + row * ch
        bold = (col == 1 and row == 0)
        p.append(fitbox(x, y, cw, ch, txt, size=13, pad=16,
                        fill=bg, stroke=br, sw=2.0 if bold else 1.5, color=tc, bold=bold))

    # вісь важливості (ліворуч, вертикальна)
    p.append(arrow(138, gy + 2 * ch, 138, gy - 4, color=MUTED, sw=1.8))
    p.append(vtext(58, gy + ch, "важливість для успіху", size=11, color=MUTED))
    p.append(text(126, gy + 14, "В", size=11.5, color=INK, anchor="end", bold=True))
    p.append(text(126, gy + 2 * ch - 6, "Н", size=11.5, color=MUTED, anchor="end", bold=True))

    # вісь складності (знизу, горизонтальна)
    by = gy + 2 * ch + 22
    p.append(arrow(gx - 4, by, gx + 2 * cw, by, color=MUTED, sw=1.8))
    p.append(text(gx + cw, by + 30, "складність / ризик для структури", size=11, color=MUTED))
    p.append(text(gx + 6, by + 18, "Н", size=11.5, color=MUTED, anchor="start", bold=True))
    p.append(text(gx + 2 * cw - 6, by + 18, "В", size=11.5, color=INK, anchor="end", bold=True))

    render(os.path.join(OUT, "priority-quadrant.svg"), W, H, *p,
           title="Дві осі листка: важливість ловить мету, складність — де архітектура")


# ── tree-to-assert: дерево як живі дані (для proj-вставки) ─────────────────────
# Ідея: той самий шлях, що на плакаті робили оком, стає конвеєром даних —
# вкладене дерево → обхід → фільтр (В,В) → драйвери → міра одного драйвера,
# доведена до асерта, що падає в збірці. Останній вузол — фіолетовий (рішення).

def fig_tree_to_assert():
    W, H = 1040, 200
    p = []
    cy, bw, bh = 140, 190, 66

    # (cx, дві-рядковий текст, tло, рамка, колір, жирність)
    nodes = [
        (115, "дерево DH\nвкладені дані", GREYBG, INK, INK, False),
        (385, "усі листки\nобхід у глибину", BG, MUTED, INK, False),
        (655, "драйвери\n(В, В)", HOTBG, POS, POS, True),
        (925, "міра → асерт\nпадає в збірці", ACCBG, ACC, ACC, True),
    ]

    # 1) стрілки між вузлами (без підписів — жодного тексту на лініях)
    edges = [(210, 290), (480, 560), (750, 830)]
    for x1, x2 in edges:
        p.append(arrow(x1 + 3, cy, x2 - 3, cy, color=MUTED, sw=2.0))

    # 2) вузли поверх (рамки лягають на кінці стрілок)
    for cx, txt, bg, br, col, bold in nodes:
        p.append(fitbox(cx - bw / 2, cy - bh / 2, bw, bh, txt, size=14, pad=11,
                        fill=bg, stroke=br, sw=2.0 if bold else 1.5, color=col, bold=bold))

    render(os.path.join(OUT, "tree-to-assert.svg"), W, H, *p,
           title="Від дерева-даних до асерта, що падає в збірці")


if __name__ == "__main__":
    fig_utility_tree()
    fig_priority_quadrant()
    fig_tree_to_assert()
    print("OK: figures written to", OUT)
