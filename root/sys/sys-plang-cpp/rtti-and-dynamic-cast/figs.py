# -*- coding: utf-8 -*-
"""Фігури до теми «RTTI: typeid і dynamic_cast»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def box(cx, cy, s, **kw):
    """textbox повертає (тіло, w, h) — тут потрібне лише тіло."""
    body, _w, _h = textbox(cx, cy, s, **kw)
    return body


def box_wh(cx, cy, s, **kw):
    return textbox(cx, cy, s, **kw)


def badge(cx, cy, n):
    return (circle(cx, cy, 15, fill="#fdecea", stroke=POS, sw=2) +
            text(cx, cy + 5, str(n), size=14, color=POS, bold=True))


# ── 1. Де в об'єкті лежить відповідь про його тип ───────────────────────────
def fig_where_the_answer_lives():
    W, H = 1080, 360

    obj_x, obj_w = 60, 250
    vt_x, vt_w = 430, 290
    ti_x, ti_w = 800, 240

    f = []

    # заголовки колонок
    f.append(fitbox(obj_x, 30, obj_w, 40, "об'єкт Polygon", size=15, bold=True, fill="#eef3fb"))
    f.append(fitbox(vt_x, 30, vt_w, 40, "таблиця віртуальних функцій", size=15, bold=True, fill="#eef3fb"))
    f.append(fitbox(ti_x, 30, ti_w, 40, "опис типу", size=15, bold=True, fill="#eef3fb"))

    # об'єкт
    rows_o = [("vptr", "#eaf7ef"), ("поля підоб'єкта Shape", "#f4f6f8"), ("власні поля Polygon", "#f4f6f8")]
    for i, (s, bg) in enumerate(rows_o):
        f.append(fitbox(obj_x, 96 + i * 54, obj_w, 54, s, size=13, fill=bg))

    # таблиця
    rows_v = [("−2", "offset-to-top = 0", "#f4f6f8"),
              ("−1", "вказівник на type_info", "#eaf7ef"),
              ("0", "&Polygon::draw", "#f4f6f8"),
              ("1", "&Polygon::area", "#f4f6f8")]
    for i, (idx, s, bg) in enumerate(rows_v):
        y = 96 + i * 54
        f.append(fitbox(vt_x, y, vt_w, 54, s, size=13, fill=bg))
        f.append(text(vt_x - 26, y + 33, idx, size=13, color=MUTED))

    # точка прив'язки — межа між −1 і 0
    ap_y = 96 + 2 * 54
    f.append(line(vt_x - 46, ap_y, vt_x + vt_w + 14, ap_y, color=POS, sw=2.5))
    f.append(text(vt_x + vt_w / 2.0, ap_y - 62, "точка прив'язки", size=12, color=POS))

    # стрілка vptr → точка прив'язки
    f.append(arrow(obj_x + obj_w + 6, 123, vt_x - 50, ap_y - 4, color=NEG))

    # стрілка з рядка −1 у опис типу
    f.append(arrow(vt_x + vt_w + 18, 96 + 54 + 27, ti_x - 8, 150, color=NEG))

    # опис типу
    f.append(fitbox(ti_x, 96, ti_w, 108,
                    "std::type_info\n\nname(): \"7Polygon\"", size=13, fill="#eaf0fd"))
    f.append(fitbox(ti_x, 214, ti_w, 82,
                    "перелік баз і зсувів:\nShape, зсув 0", size=13, fill="#f4f6f8"))

    f.append(text(W / 2.0, 336,
                  "Немає віртуальних функцій — немає vptr, і питати нема кого.",
                  size=14, color=MUTED))

    return render(os.path.join(IMG, 'where-answer-lives.svg'), W, H, *f,
                  title="Опис типу лежить біля таблиці віртуальних функцій")


# ── 2. Множинне спадкування: приведення править адресу ──────────────────────
def fig_pointer_adjustment():
    W, H = 1080, 470

    ox, ow = 100, 300
    f = []

    f.append(text(ox + ow / 2.0, 40, "об'єкт Sprite : Drawable, Serializable", size=15, bold=True))

    blocks = [(90, "підоб'єкт Drawable\n(vptr₁ + поля)", "#eaf7ef", "+0"),
              (200, "підоб'єкт Serializable\n(vptr₂ + поля)", "#eaf0fd", "+16"),
              (310, "власні поля Sprite", "#f4f6f8", "+32")]
    for y, s, bg, off in blocks:
        f.append(fitbox(ox, y, ow, 100, s, size=13, fill=bg))
        f.append(text(ox - 42, y + 56, off, size=13, color=MUTED))

    notes = [(90, "Drawable* d = sprite;\nадреса та сама, зсув 0"),
             (200, "Serializable* z = sprite;\nкомпілятор мовчки додав 16")]
    nx, nw = 580, 420
    for y, s in notes:
        f.append(fitbox(nx, y, nw, 100, s, size=13, fill="#ffffff"))
        f.append(arrow(nx - 12, y + 50, ox + ow + 12, y + 50, color=NEG))

    f.append(fitbox(nx, 310, nw, 100,
                    "dynamic_cast<Drawable*>(z)\nмусить відняти 16", size=13, fill="#fdecea"))

    f.append(text(W / 2.0, 448,
                  "Приведення — це не лише перевірка типу, а й правка адреси; величину правки знає тільки опис типу.",
                  size=14, color=MUTED))

    return render(os.path.join(IMG, 'pointer-adjustment.svg'), W, H, *f,
                  title="Приведення в множинному спадкуванні змінює адресу")


# ── 3. dynamic_cast — обхід графа баз, а не пошук у таблиці ─────────────────
def fig_graph_walk():
    W, H = 1080, 500

    f = []
    nodes = {
        "Sprite":       (540, 70),
        "Drawable":     (300, 190),
        "Serializable": (800, 190),
        "Node":         (300, 310),
        "Streamable":   (800, 310),
        "Shared":       (540, 430),
    }
    labels = {"Shared": "Object"}

    edges = [("Sprite", "Drawable"), ("Sprite", "Serializable"),
             ("Drawable", "Node"), ("Serializable", "Streamable"),
             ("Streamable", "Shared"), ("Node", "Shared")]

    # ребра — знизу коробки до верху наступної, з відступом
    half = {}
    for name, (cx, cy) in nodes.items():
        s = labels.get(name, name)
        w = text_width(s, 15, True) + 20
        half[name] = (w / 2.0, 21.0)

    for a, b in edges:
        ax, ay = nodes[a]
        bx, by = nodes[b]
        f.append(line(ax + (bx - ax) * 0.16, ay + half[a][1] + 4,
                      bx - (bx - ax) * 0.16, by - half[b][1] - 4,
                      color=MUTED, sw=1.6))

    order = {"Sprite": 1, "Drawable": 2, "Node": 3, "Serializable": 4, "Streamable": 5}
    for name, (cx, cy) in nodes.items():
        s = labels.get(name, name)
        hot = name == "Streamable"
        f.append(box(cx, cy, s, size=15, bold=True,
                     fill="#fdecea" if hot else "#eef3fb",
                     stroke=POS if hot else LINE))
        if name in order:
            f.append(badge(cx + half[name][0] + 26, cy, order[name]))

    f.append(fitbox(40, 372, 360, 96,
                    "Гілку Drawable → Object пройдено дарма:\nдоки не порівняно описи типів,\nневідомо, де лежить ціль.",
                    size=13, fill="#ffffff"))

    f.append(text(W / 2.0, 480,
                  "Шукаємо Streamable: порядок обходу — 1…5, кожен крок звіряє опис типу й накопичує зсув.",
                  size=14, color=MUTED))

    return render(os.path.join(IMG, 'graph-walk.svg'), W, H, *f,
                  title="dynamic_cast обходить граф баз, а не читає готову таблицю")


# ── 4. Прямий обхід дерева робить піддерева суцільними відрізками ───────────
def fig_preorder_ranges():
    W, H = 1120, 650

    f = []
    nodes = {
        "Shape":       (560, 55),
        "Polygon":     (250, 150),
        "Ellipse":     (720, 150),
        "TextLabel":   (960, 150),
        "Rect":        (150, 245),
        "Triangle":    (365, 245),
        "Circle":      (720, 245),
        "RoundedRect": (150, 340),
    }
    edges = [("Shape", "Polygon"), ("Shape", "Ellipse"), ("Shape", "TextLabel"),
             ("Polygon", "Rect"), ("Polygon", "Triangle"), ("Rect", "RoundedRect"),
             ("Ellipse", "Circle")]
    kind = {"Rect": 0, "RoundedRect": 1, "Triangle": 2,
            "Ellipse": 3, "Circle": 4, "TextLabel": 5}

    half = {}
    for name in nodes:
        half[name] = (text_width(name, 15, True) / 2.0 + 10, 21.0)

    for a, b in edges:
        ax, ay = nodes[a]
        bx, by = nodes[b]
        f.append(line(ax + (bx - ax) * 0.18, ay + half[a][1] + 4,
                      bx - (bx - ax) * 0.18, by - half[b][1] - 4,
                      color=MUTED, sw=1.6))

    for name, (cx, cy) in nodes.items():
        abstract = name in ("Shape", "Polygon")
        f.append(box(cx, cy, name, size=15, bold=True,
                     fill="#f4f6f8" if abstract else "#eef3fb",
                     stroke=MUTED if abstract else LINE))
        if name in kind:
            f.append(badge(cx + half[name][0] + 26, cy, kind[name]))

    # смуга значень тега в порядку прямого обходу
    order = ["Rect", "RoundedRect", "Triangle", "Ellipse", "Circle", "TextLabel"]
    sx, cw, sy, ch = 50, 165, 420, 58
    for i, name in enumerate(order):
        f.append(fitbox(sx + i * cw, sy, cw, ch, "%d  %s" % (i, name),
                        size=13, fill="#eaf0fd"))

    def bracket(i0, i1, y, label, color):
        x0 = sx + i0 * cw + 8
        x1 = sx + (i1 + 1) * cw - 8
        return [line(x0, y, x1, y, color=color, sw=2.2),
                line(x0, y - 9, x0, y, color=color, sw=2.2),
                line(x1, y - 9, x1, y, color=color, sw=2.2),
                text((x0 + x1) / 2.0, y + 25, label, size=13, color=color)]

    f += bracket(0, 2, 502, "Polygon: 0…2", POS)
    f += bracket(3, 4, 502, "Ellipse: 3…4", POS)
    f += bracket(0, 1, 560, "Rect: 0…1", NEG)

    f.append(text(W / 2.0, 630,
                  "Абстрактні класи власного номера не мають — у них лише межі піддерева.",
                  size=14, color=MUTED))

    return render(os.path.join(IMG, 'preorder-ranges.svg'), W, H, *f,
                  title="Прямий обхід дерева перетворює «є різновидом» на порівняння відрізка")


if __name__ == '__main__':
    for fn in (fig_where_the_answer_lives, fig_pointer_adjustment, fig_graph_walk,
               fig_preorder_ranges):
        print(fn())
