# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки §3.2.6m — «Карти Карно: мінімізація логіки руками».
Чистий Python, без залежностей. Вивід → ./img/ (унікальні імена fig-15-6m-*).
Стиль (AUTHORING §9): білий фон; «1»/істина червоний, «0»/хибність синій;
поле/«накриття» зелене; стрілки через marker; шрифт sans-serif.
Хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація підписів: Рис. 3.2.6m.k.
НЕ чіпає головний figs.py розділу.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"   # «1» / істина
BLUE  = "#1f47b5"   # «0» / хибність
GREEN = "#1f8a3b"   # накриття / висновок
AMBER = "#caa24a"   # «байдуже» / акцент
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", GREEN: "aGreen", GREY: "aGrey"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def roundrect(x, y, w, h, color=GREEN, sw=3, rx=14, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{color}" stroke-width="{sw}"{d}/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


def bit_cell(x, y, w, h, val, fill_bg="#ffffff"):
    """Клітинка карти зі значенням 0/1; «1» червона, «0» синя."""
    s = rect(x, y, w, h, fill_bg, GREY, 1.6)
    col = RED if val == "1" else (BLUE if val == "0" else AMBER)
    s += text(x + w / 2, y + h / 2 + 7, val, 22, col, "middle", "bold")
    return s


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.2.6m.1 — від таблиці істинності до карти: сусідні рядки розкидані,
#  сусідні клітинки — поряд (код Грея).
# ════════════════════════════════════════════════════════════════════════════
def fig_table_to_map():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 34, "Та сама функція двічі: таблиця істинності  →  карта Карно",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "У таблиці сусіди-за-одним-бітом розкидані; на карті їх ставлять ПОРЯД — у цьому вся ідея",
              12.5, GREY, "middle", style="italic")

    # --- таблиця істинності (ліворуч): F(A,B,C) ---
    rows = [
        ("0", "0", "0", "0"),
        ("0", "0", "1", "1"),
        ("0", "1", "0", "0"),
        ("0", "1", "1", "1"),
        ("1", "0", "0", "0"),
        ("1", "0", "1", "1"),
        ("1", "1", "0", "1"),
        ("1", "1", "1", "1"),
    ]
    tx, ty = 60, 110
    cw, rh = 46, 42
    heads = ["A", "B", "C", "F"]
    for j, hd in enumerate(heads):
        hx = tx + j * cw
        col = INK if j < 3 else GREEN
        s += rect(hx, ty - rh, cw, rh, "#f3f3f3", GREY, 1.6)
        s += text(hx + cw / 2, ty - rh / 2 + 6, hd, 17, col, "middle", "bold")
    for i, (a, b, c, f) in enumerate(rows):
        ry = ty + i * rh
        s += rect(tx, ry, cw, rh, "#ffffff", GREY, 1.2)
        s += rect(tx + cw, ry, cw, rh, "#ffffff", GREY, 1.2)
        s += rect(tx + 2 * cw, ry, cw, rh, "#ffffff", GREY, 1.2)
        s += text(tx + cw / 2, ry + rh / 2 + 5, a, 15, GREY, "middle")
        s += text(tx + 1.5 * cw, ry + rh / 2 + 5, b, 15, GREY, "middle")
        s += text(tx + 2.5 * cw, ry + rh / 2 + 5, c, 15, GREY, "middle")
        s += bit_cell(tx + 3 * cw, ry, cw, rh, f, "#fbfbfb")
    s += text(tx + 2 * cw, ty + 8 * rh + 26, "8 рядків = 2³ комбінацій", 12.5, GREY, "middle", style="italic")

    # позначимо два рядки, що відрізняються лише бітом A (010-рядок №3 і 110-рядок №7? )
    # Беремо рядки ABC=001 (i=1, F=1) та ABC=101 (i=5, F=1): різняться лише A.
    y1 = ty + 1 * rh + rh / 2
    y5 = ty + 5 * rh + rh / 2
    s += roundrect(tx - 5, ty + 1 * rh - 3, 4 * cw + 10, rh + 6, AMBER, 2.4, 8)
    s += roundrect(tx - 5, ty + 5 * rh - 3, 4 * cw + 10, rh + 6, AMBER, 2.4, 8)
    s += text(tx + 4 * cw + 16, y1 + 5, "001", 12, AMBER, "start", "bold")
    s += text(tx + 4 * cw + 16, y5 + 5, "101", 12, AMBER, "start", "bold")
    s += text(tx + 4 * cw + 16, (y1 + y5) / 2 + 5, "різняться лише A,", 11.5, AMBER, "start")
    s += text(tx + 4 * cw + 16, (y1 + y5) / 2 + 20, "та в таблиці — далеко", 11.5, AMBER, "start")

    # --- карта Карно (праворуч): рядки A; стовпці BC у коді Грея ---
    mx, my = 600, 150
    gw, gh = 70, 66
    s += text(mx + 2 * gw, my - 64, "Карта Карно тієї ж F(A,B,C)", 15.5, INK, "middle", "bold")
    # підпис осей
    s += text(mx - 30, my - 22, "A\\BC", 14, INK, "middle", "bold")
    col_labels = ["00", "01", "11", "10"]  # код Грея!
    for j, cl in enumerate(col_labels):
        s += text(mx + j * gw + gw / 2, my - 20, cl, 14, INK, "middle", "bold")
    row_labels = ["0", "1"]
    # значення карти: індекс мінтерму m = A*4 + B*2 + C; стовпці у Греї 00,01,11,10
    # F=1 для m: 001(1),011(3),101(5),110(6),111(7)
    F = {0: "0", 1: "1", 2: "0", 3: "1", 4: "0", 5: "1", 6: "1", 7: "1"}
    gray_c = [0, 1, 3, 2]  # BC -> код стовпця у Греї: 00->0, 01->1, 11->3, 10->2
    for ri, rl in enumerate(row_labels):
        s += text(mx - 20, my + ri * gh + gh / 2 + 6, rl, 14, INK, "middle", "bold")
        for cj, bc in enumerate(gray_c):
            m = ri * 4 + bc
            cellx = mx + cj * gw
            celly = my + ri * gh
            s += bit_cell(cellx, celly, gw, gh, F[m], "#ffffff")
            s += text(cellx + 4, celly + 14, f"m{m}", 9.5, GREY, "start")

    # підсвітимо ті ж дві клітинки 001 і 101 — тепер вони ПОРЯД (один стовпець)
    # 001: A=0,BC=01 -> row0,col1 ; 101: A=1,BC=01 -> row1,col1
    cx = mx + 1 * gw
    s += roundrect(cx - 4, my - 4, gw + 8, 2 * gh + 8, AMBER, 3, 10)
    s += text(cx + gw / 2, my + 2 * gh + 24, "001 і 101 — поряд!", 12.5, AMBER, "middle", "bold")

    # стрілка-зв'язка таблиця → карта
    s += arrow(tx + 4 * cw + 120, 320, mx - 60, 250, GREY, 2.2, "6,5")
    s += text((tx + 4 * cw + 120 + mx - 60) / 2, 270, "переставити", 12, GREY, "middle", style="italic")
    s += text((tx + 4 * cw + 120 + mx - 60) / 2, 286, "у код Грея", 12, GREY, "middle", style="italic")
    save("fig-15-6m-1-table-to-map.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.2.6m.2 — правила накриття: групи 1·2·4·8, сусідство по краях (тор),
#  і яку змінну «з'їдає» група.
# ════════════════════════════════════════════════════════════════════════════
def fig_grouping_rules():
    W, H = 960, 560
    s = header(W, H)
    s += text(W / 2, 34, "Як накривати одиниці: групи 1·2·4·8 — кожна викидає змінні",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "Що більша група, то коротший доданок; краї карти склеєні (карта — тор), тож кути сусідні",
              12.5, GREY, "middle", style="italic")

    gw, gh = 62, 58

    def draw_map(ox, oy, vals, title, sub):
        out = text(ox + 2 * gw, oy - 44, title, 15.5, INK, "middle", "bold")
        out += text(ox + 2 * gw, oy - 26, sub, 11.5, GREEN, "middle", style="italic")
        out += text(ox - 24, oy - 18, "AB\\CD", 11.5, INK, "middle", "bold")
        cl = ["00", "01", "11", "10"]
        for j, c in enumerate(cl):
            out += text(ox + j * gw + gw / 2, oy - 16, c, 12, INK, "middle", "bold")
        rl = ["00", "01", "11", "10"]
        for i, r in enumerate(rl):
            out += text(ox - 18, oy + i * gh + gh / 2 + 5, r, 12, INK, "middle", "bold")
        for i in range(4):
            for j in range(4):
                out += bit_cell(ox + j * gw, oy + i * gh, gw, gh, vals[i][j], "#ffffff")
        return out

    # карта 1: пара (2 клітинки) і четвірка (4 клітинки)
    ox1, oy1 = 70, 130
    v1 = [
        ["0", "1", "1", "0"],
        ["0", "1", "1", "0"],
        ["0", "0", "0", "0"],
        ["0", "0", "0", "0"],
    ]
    s += draw_map(ox1, oy1, v1, "Група 4 → −2 змінні", "накрили 4 → лишилось 2 літери")
    # четвірка: стовпці 01,11 (j=1,2) × рядки 00,01 (i=0,1) = центральний блок 2×2
    s += roundrect(ox1 + 1 * gw - 4, oy1 - 4, 2 * gw + 8, 2 * gh + 8, GREEN, 3.4, 12)
    s += text(ox1 + 2 * gw, oy1 + 2 * gh + 22, "B·C̄ ?  →  тут = Ā·B", 12.5, GREEN, "middle", "bold")
    s += text(ox1 + 2 * gw, oy1 + 2 * gh + 40, "(сталі: A=0, B=1; C,D — будь-які)", 11, GREY, "middle")

    # карта 2: краєве сусідство — кути склеєні (тор)
    ox2, oy2 = 560, 130
    v2 = [
        ["1", "0", "0", "1"],
        ["0", "0", "0", "0"],
        ["0", "0", "0", "0"],
        ["1", "0", "0", "1"],
    ]
    s += draw_map(ox2, oy2, v2, "Чотири КУТИ — теж група!", "карта склеєна по краях, як тор")
    # обведемо чотири кути окремими овалами + позначимо склейку
    cw_, ch_ = gw, gh
    for (i, j) in [(0, 0), (0, 3), (3, 0), (3, 3)]:
        s += roundrect(ox2 + j * gw - 3, oy2 + i * gh - 3, gw + 6, gh + 6, GREEN, 3, 10)
    # стрілки склейки лівий-правий і верх-низ
    s += arrow(ox2 - 12, oy2 + gh / 2, ox2 - 12, oy2 + 3 * gh + gh / 2, GREEN, 2, "4,4")
    s += arrow(ox2 - 12, oy2 + 3 * gh + gh / 2, ox2 - 12, oy2 + gh / 2, GREEN, 2, "4,4")
    s += text(ox2 + 2 * gw, oy2 + 4 * gh + 22, "B̄·D̄  (сталі: B=0, D=0)", 12.5, GREEN, "middle", "bold")
    s += text(ox2 + 2 * gw, oy2 + 4 * gh + 40, "ліва й права межі — сусіди; верх і низ — теж", 11, GREY, "middle")

    # нижня шкала: розмір групи ↔ скільки змінних лишилось (для 4 змінних)
    by = 470
    s += text(W / 2, by, "Правило обсягу: група з 2ᵏ клітинок викидає k змінних", 14.5, INK, "middle", "bold")
    items = [("1", "4 літери"), ("2", "3 літери"), ("4", "2 літери"), ("8", "1 літера"), ("16", "F=1 завжди")]
    bx = 150
    step = 130
    for k, (sz, lit) in enumerate(items):
        cx = bx + k * step
        s += circle(cx, by + 38, 20, "#fff", GREEN, 2.6)
        s += text(cx, by + 44, sz, 16, GREEN, "middle", "bold")
        s += text(cx, by + 78, lit, 12, INK, "middle")
        if k < len(items) - 1:
            s += arrow(cx + 24, by + 38, cx + step - 24, by + 38, GREY, 1.8)
    save("fig-15-6m-2-grouping-rules.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.2.6m.3 — повний приклад: накрити карту найбільшими групами →
#  прочитати мінімальну суму добутків; і «байдуже» (X) як вільний козир.
# ════════════════════════════════════════════════════════════════════════════
def fig_worked_example():
    W, H = 960, 540
    s = header(W, H)
    s += text(W / 2, 34, "Мінімізація руками: накрий усі 1 найбільшими групами — і прочитай відповідь",
              19, INK, "middle", "bold")
    s += text(W / 2, 56, "Кожну 1 має накрити хоч одна група; груп беруть якомога менше і якомога більших; X — «байдуже»",
              12.5, GREY, "middle", style="italic")

    gw, gh = 66, 60

    def draw_map(ox, oy, vals):
        out = text(ox - 24, oy - 18, "AB\\CD", 11.5, INK, "middle", "bold")
        cl = ["00", "01", "11", "10"]
        for j, c in enumerate(cl):
            out += text(ox + j * gw + gw / 2, oy - 16, c, 12, INK, "middle", "bold")
        rl = ["00", "01", "11", "10"]
        for i, r in enumerate(rl):
            out += text(ox - 18, oy + i * gh + gh / 2 + 5, r, 12, INK, "middle", "bold")
        for i in range(4):
            for j in range(4):
                out += bit_cell(ox + j * gw, oy + i * gh, gw, gh, vals[i][j], "#ffffff")
        return out

    ox, oy = 70, 150
    # функція: F=1 у правому стовпці пар + один X-доданок
    vals = [
        ["1", "0", "0", "1"],
        ["1", "0", "0", "1"],
        ["0", "0", "X", "1"],
        ["0", "0", "0", "1"],
    ]
    s += draw_map(ox, oy, vals)

    # Група A (зелена): увесь стовпець CD=10 (j=3) — четвірка → C·D̄
    s += roundrect(ox + 3 * gw - 4, oy - 4, gw + 8, 4 * gh + 8, GREEN, 3.4, 12)
    # Група B (червона): кути лівого стовпця CD=00 (j=0), рядки 00,01 (i=0,1) → Ā·C̄·D̄
    s += roundrect(ox + 0 * gw - 4, oy - 4, gw + 8, 2 * gh + 8, RED, 3, 12)
    # позначка X як козир
    s += text(ox + 2 * gw + gw / 2, oy + 2 * gh + gh + 4, "↑ X можна взяти за 1 (зручно) або 0",
              11, AMBER, "middle", style="italic")

    # легенда груп праворуч
    lx, ly = 560, 150
    s += text(lx, ly - 18, "Зчитуємо кожну групу → доданок:", 15, INK, "start", "bold")
    s += roundrect(lx, ly + 6, 26, 22, GREEN, 3.2, 6)
    s += text(lx + 38, ly + 23, "стовпець CD=10 (4 клітинки):", 13.5, INK, "start")
    s += text(lx + 38, ly + 45, "сталі C=1, D=0  →  C·D̄", 15, GREEN, "start", "bold")

    s += roundrect(lx, ly + 70, 26, 22, RED, 3, 6)
    s += text(lx + 38, ly + 87, "пара в кутку CD=00, A=0 (2 клітинки):", 13.5, INK, "start")
    s += text(lx + 38, ly + 109, "сталі A=0, C=0, D=0  →  Ā·C̄·D̄", 15, RED, "start", "bold")

    # підсумкова формула
    s += line(lx, ly + 135, lx + 360, ly + 135, FAINT, 1.6)
    s += text(lx, ly + 165, "F = C·D̄ + Ā·C̄·D̄", 21, INK, "start", "bold")
    s += text(lx, ly + 192, "Дві групи → два доданки, дві суми. Усе.", 12.5, GREY, "start", style="italic")

    # порівняння з «у лоб» (СДНФ)
    s += text(lx, ly + 230, "А «в лоб» з таблиці було б:", 13, GREY, "start")
    s += text(lx, ly + 252, "ĀB̄C̄D̄ + ĀBC̄D̄ + CD̄(усі 4) — довжелезно",
              12.5, GREY, "start", style="italic")
    s += roundrect(lx - 6, ly + 150, 372, 26, GREEN, 2.2, 8, dash="5,4")

    # маленька ремарка про SOP/POS
    s += text(W / 2, H - 26, "Тут накривали ОДИНИЦІ → сума добутків (SOP). Накриєш НУЛІ — дістанеш добуток сум (POS).",
              12.5, GREY, "middle", style="italic")
    save("fig-15-6m-3-worked-example.svg", s)


if __name__ == "__main__":
    fig_table_to_map()
    fig_grouping_rules()
    fig_worked_example()
    print("done.")
