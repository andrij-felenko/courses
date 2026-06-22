# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_FILL = "#eafaf0"
RED_FILL   = "#fdecea"
BLUE_FILL  = "#eef4ff"
GREY_FILL  = "#eef1f5"


# ── helpers для сітки карти ───────────────────────────────────────────────────
def cell(x, y, s, w, h, fill=BG, stroke=INK, sw=1.4, size=15, color=INK, bold=True):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=0)
    out += text(x + w / 2, y + h / 2 + size * 0.35, s, size=size, color=color, bold=bold)
    return out


def col_header(x, y, s, w, size=13, color=MUTED):
    return text(x + w / 2, y, s, size=size, color=color, bold=True)


# ── table-to-map: та сама функція як таблиця і як карта ───────────────────────
# Ідея: у звичайній таблиці сусіди-за-одним-бітом (001 і 101) розкидані далеко;
# на карті з осями в коді Грея вони опиняються поряд.
def fig_table_to_map():
    W, H = 720, 380
    p = []

    # ── ліворуч: таблиця істинності F(A,B,C) ──
    tx, ty = 60, 80
    rw, rh = 56, 30
    rows = [
        ("000", "0"), ("001", "1"), ("010", "0"), ("011", "1"),
        ("100", "0"), ("101", "1"), ("110", "1"), ("111", "1"),
    ]
    p.append(text(tx + rw, ty - 34, "таблиця істинності", size=13, color=INK, bold=True))
    p.append(col_header(tx, ty - 12, "ABC", rw))
    p.append(col_header(tx + rw, ty - 12, "F", rw * 0.6))
    for i, (abc, f) in enumerate(rows):
        yy = ty + i * rh
        hot = abc in ("001", "101")
        p.append(cell(tx, yy, abc, rw, rh, fill=(RED_FILL if hot else BG), size=13))
        p.append(cell(tx + rw, yy, f, rw * 0.6, rh, fill=BG, size=13,
                      color=(POS if f == "1" else MUTED)))
    # підсвітити двох далеких сусідів
    p.append(text(tx + rw * 1.9, ty + 1 * rh + rh / 2 + 4, "← різняться", size=10, color=POS, anchor="start"))
    p.append(text(tx + rw * 1.9, ty + 5 * rh + rh / 2 + 4, "← лише бітом A", size=10, color=POS, anchor="start"))

    # ── праворуч: карта Карно 2×4 ──
    mx, my = 430, 110
    cw, ch = 56, 56
    p.append(text(mx + cw * 2, my - 58, "карта Карно", size=13, color=INK, bold=True))
    # заголовки стовпців: BC у коді Грея
    cols = ["00", "01", "11", "10"]
    p.append(text(mx + cw * 2, my - 34, "BC", size=12, color=MUTED, bold=True))
    for j, c in enumerate(cols):
        p.append(col_header(mx + cw * (j + 0), my - 14, c, cw, color=NEG))
    # заголовки рядків: A
    p.append(text(mx - 18, my + ch * 0.5 + 5, "A", size=12, color=MUTED, bold=True))
    for i, a in enumerate(["0", "1"]):
        p.append(text(mx - 18, my + ch * (i + 0.5) + 5, a, size=13, color=NEG, bold=True))
    # значення: F(A,B,C). індекс рядка таблиці = A*4 + B*2 + C
    fmap = {r[0]: r[1] for r in rows}
    for i in range(2):           # A
        for j, bc in enumerate(cols):  # BC у коді Грея
            a = str(i); b, c = bc[0], bc[1]
            f = fmap[a + b + c]
            hot = (a + b + c) in ("001", "101")
            p.append(cell(mx + cw * j, my + ch * i, f, cw, ch,
                          fill=(RED_FILL if hot else BG), size=16,
                          color=(POS if f == "1" else MUTED)))
    # обвести двох сусідів, що тепер поряд
    p.append(rect(mx + cw * 1 - 3, my - 3, cw + 6, ch * 2 + 6, fill="none", stroke=POS, sw=2.6, rx=8))
    p.append(text(mx + cw * 1.0, my + ch * 2 + 22, "001 і 101 — тепер поряд", size=11, color=POS, anchor="middle"))

    # стрілка-зв'язок між поданнями
    p.append(text((tx + rw * 2.6 + mx) / 2, my + ch + 4, "та сама\nфункція", size=11, color=MUTED))

    render(os.path.join(OUT, "table-to-map.svg"), W, H, *p,
           title="Та сама функція: у таблиці сусіди далеко, на карті — поряд")


# ── grouping-rules: розмір 2ᵏ, склейка країв (тор) ───────────────────────────
# Ідея: група 2^k викидає k змінних; ліва межа сусідня правій, верхня — нижній,
# тож і чотири кути — законна група.
def fig_grouping_rules():
    W, H = 720, 380
    p = []
    cols = ["00", "01", "11", "10"]
    rows = ["00", "01", "11", "10"]
    cw, ch = 52, 52

    def kmap(ox, oy, ones, groups, label):
        out = [text(ox + cw * 2, oy - 40, label, size=12, color=INK, bold=True)]
        out.append(text(ox + cw * 2, oy - 20, "CD", size=11, color=MUTED, bold=True))
        for j, c in enumerate(cols):
            out.append(col_header(ox + cw * j, oy - 4, c, cw, size=11, color=NEG))
        out.append(text(ox - 22, oy + cw * 0.5 + 4, "AB", size=11, color=MUTED, bold=True))
        for i, r in enumerate(rows):
            out.append(text(ox - 16, oy + ch * (i + 0.5) + 4, r, size=11, color=NEG, bold=True))
        for i in range(4):
            for j in range(4):
                v = "1" if (i, j) in ones else "0"
                out.append(cell(ox + cw * j, oy + ch * i, v, cw, ch, size=14,
                                color=(POS if v == "1" else MUTED)))
        for (gi, gj, gh, gw, col) in groups:
            out.append(rect(ox + cw * gj - 3, oy + ch * gi - 3, cw * gw + 6, ch * gh + 6,
                            fill="none", stroke=col, sw=2.6, rx=10))
        return out

    # ліва карта: група 4 (квадрат AB=00..01 × CD=00..01 → лишається Ā·B... показ через сталі)
    # беремо групу 4 у рядках AB∈{00,01}? простіше: стовпці CD∈{00,01} рядок AB=00 -> 2 кл
    # зробимо групу 4: рядки AB∈{00,01} (i=0,1) × стовпці CD∈{00,01} (j=0,1) -> сталі A=0,C=0
    ones_left = {(0, 0), (0, 1), (1, 0), (1, 1)}
    groups_left = [(0, 0, 2, 2, FIELD)]
    p += kmap(60, 90, ones_left, groups_left, "група з 4 → −2 змінні")
    p.append(text(60 + cw * 2, 90 + ch * 4 + 24, "сталі: A=0, C=0  →  Ā·C̄", size=11, color=FIELD))

    # права карта: чотири кути -> сусідні через склейку (тор)
    ones_right = {(0, 0), (0, 3), (3, 0), (3, 3)}
    p += kmap(440, 90, ones_right, [], "чотири кути — теж група")
    # підсвітити кути окремими рамками
    for (i, j) in ones_right:
        p.append(rect(440 + cw * j - 3, 90 + ch * i - 3, cw + 6, ch + 6, fill="none", stroke=POS, sw=2.4, rx=8))
    # дуги-склейки країв
    oy = 90
    p.append(line(440 - 8, oy + ch * 0.5, 440 - 8, oy + ch * 3.5, color=POS, sw=1.4, dash="4 4"))
    p.append(line(440 + cw * 4 + 8, oy + ch * 0.5, 440 + cw * 4 + 8, oy + ch * 3.5, color=POS, sw=1.4, dash="4 4"))
    p.append(text(440 + cw * 2, oy + ch * 4 + 24, "край ↔ край: карта — тор  →  B̄·D̄", size=11, color=POS))

    render(os.path.join(OUT, "grouping-rules.svg"), W, H, *p,
           title="Група 2ᵏ викидає k змінних; краї карти склеєні")


# ── worked-example: повна мінімізація F(A,B,C,D) ──────────────────────────────
# Ідея: чотиризмінна карта, дві групи (обидві по 4) накривають усі одиниці.
# Функція: мінтерми {0,2,6,8,10,14}.
#   зелена  — увесь стовпець CD=10 (j=3): сталі C=1,D=0  → C·D̄
#   червона — ЧОТИРИ кути (CD∈{00,10} × AB∈{00,10}, сусідні через склейку): B=0,D=0 → B̄·D̄
def fig_worked_example():
    W, H = 560, 500
    p = []
    cols = ["00", "01", "11", "10"]
    rows = ["00", "01", "11", "10"]
    cw, ch = 64, 64
    ox, oy = 130, 90

    ones = {(0, 3), (1, 3), (2, 3), (3, 3),         # стовпець CD=10  → C·D̄
            (0, 0), (3, 0), (0, 3), (3, 3)}          # кути → B̄·D̄ (перетин із зеленою — дозволено)
    corners = [(0, 0), (0, 3), (3, 0), (3, 3)]

    p.append(text(ox + cw * 2, oy - 38, "CD", size=12, color=MUTED, bold=True))
    for j, c in enumerate(cols):
        p.append(col_header(ox + cw * j, oy - 16, c, cw, size=12, color=NEG))
    p.append(text(ox - 26, oy + cw * 0.5 + 5, "AB", size=12, color=MUTED, bold=True))
    for i, r in enumerate(rows):
        p.append(text(ox - 20, oy + ch * (i + 0.5) + 5, r, size=12, color=NEG, bold=True))

    for i in range(4):
        for j in range(4):
            v, col = ("1", POS) if (i, j) in ones else ("0", MUTED)
            p.append(cell(ox + cw * j, oy + ch * i, v, cw, ch, size=18, color=col))

    # зелена група: увесь стовпець CD=10 (j=3)
    p.append(rect(ox + cw * 3 - 4, oy - 4, cw + 8, ch * 4 + 8, fill="none", stroke=FIELD, sw=3, rx=12))
    # червона група: чотири кути (сусідні через подвійну склейку країв) — обвести кожен
    for (i, j) in corners:
        p.append(rect(ox + cw * j - 6, oy + ch * i - 6, cw + 12, ch + 12, fill="none", stroke=POS, sw=3, rx=12))
    # пунктир-склейки: ліво↔право і верх↔низ
    p.append(line(ox - 12, oy + ch * 0.5, ox - 12, oy + ch * 3.5, color=POS, sw=1.4, dash="4 4"))
    p.append(line(ox + cw * 4 + 12, oy + ch * 0.5, ox + cw * 4 + 12, oy + ch * 3.5, color=POS, sw=1.4, dash="4 4"))

    # читання груп
    yy = oy + ch * 4 + 30
    b1, _, _ = textbox(ox + cw * 1.0, yy, "зелена (стовпець): C=1, D=0  →  C·D̄", size=12, color=FIELD,
                       fill=GREEN_FILL, stroke=FIELD, sw=1.6)
    p.append(b1)
    b2, _, _ = textbox(ox + cw * 1.0, yy + 40, "червона (4 кути): B=0, D=0  →  B̄·D̄", size=12, color=POS,
                       fill=RED_FILL, stroke=POS, sw=1.6)
    p.append(b2)
    res, _, _ = textbox(ox + cw * 1.0, yy + 86, "F = C·D̄ + B̄·D̄", size=14, color=INK, bold=True,
                        fill="#f6f4ec", stroke=INK, sw=2)
    p.append(res)

    render(os.path.join(OUT, "worked-example.svg"), W, H, *p,
           title="Дві групи по чотири накривають усі одиниці → два доданки")


if __name__ == "__main__":
    fig_table_to_map()
    fig_grouping_rules()
    fig_worked_example()
    print("OK: figures written to", OUT)
