# -*- coding: utf-8 -*-
"""Фігури для статті «OCP» (open-closed). Вивід — ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_two_shapes():
    """Дві форми додавання можливості: правка switch (шрам у робочому коді) проти
    нового класу за інтерфейсом (робочий код недоторканий)."""
    W, H = 860, 470
    p = []
    p.append(text(W / 2, 30, "Додаємо нову фігуру — два способи", size=17, bold=True))

    # роздільна лінія посередині
    p.append(line(W / 2, 56, W / 2, H - 20, color=MUTED, sw=1, dash="5,5"))

    # ── ЛІВА половина: правка switch ────────────────────────────────
    lx = 40
    p.append(text(215, 78, "Правити наявний switch", size=14, bold=True, color=POS))
    # блок коду
    p.append(rect(lx, 96, 350, 150, fill="#fdecea", stroke=POS, sw=1.5))
    code_l = [
        "double area(Shape s) {",
        "  switch (s.kind) {",
        "    case CIRCLE: ...",
        "    case RECT:   ...",
        "    case TRI:    ...   // ← дописано",
        "  }",
        "}",
    ]
    cy = 118
    for i, ln in enumerate(code_l):
        col = POS if "дописано" in ln else INK
        p.append(text(lx + 14, cy + i * 18, ln, size=12.5, color=col, anchor="start"))
    p.append(text(215, 268, "функцію перекомпільовано,", size=12, color=POS))
    p.append(text(215, 286, "перетестовано, ризик регресу", size=12, color=POS))
    # значок: тріщина в наявному
    p.append(plus(lx + 335, 96, r=11))

    # ── ПРАВА половина: новий клас за інтерфейсом ───────────────────
    rx0 = W / 2 + 40
    p.append(text(645, 78, "Додати новий клас", size=14, bold=True, color=FIELD))
    # інтерфейс (закритий, недоторканий) — по центру правої половини
    ifx, ify, ifw, ifh = rx0 + 62, 96, 200, 46
    p.append(fitbox(ifx, ify, ifw, ifh,
                    "interface Shape\n{ double area(); }",
                    size=12.5, fill="#eaf7ee", stroke=FIELD, sw=1.8))
    # реалізації: дві старі + нова
    bw, bh, by = 118, 40, 200
    xs = [rx0, rx0 + 132, rx0 + 264]
    labs = ["Circle", "Rect", "Triangle"]
    junc_x, junc_y = ifx + ifw / 2, ify + ifh + 8   # спільна точка стику під інтерфейсом
    # спершу лінії (щоб рамки лягли поверх), кінці — на нижньому краї рамок і в точці стику
    for x, lab in zip(xs, labs):
        p.append(line(x + bw / 2, by, junc_x, junc_y, color=MUTED, sw=1))
    for x, lab in zip(xs, labs):
        new = lab == "Triangle"
        p.append(fitbox(x, by, bw, bh, lab, size=12.5,
                        fill="#eaf7ee" if new else FILL,
                        stroke=FIELD if new else LINE, sw=1.8 if new else 1.5, bold=new))
    p.append(text(rx0 + 264 + bw / 2, by + bh + 18, "новий файл", size=11, color=FIELD, bold=True))
    p.append(plus(rx0 + 264 + bw - 4, by, r=11))
    p.append(text(645, 300, "старий код area() НЕ відкрито,", size=12, color=FIELD))
    p.append(text(645, 318, "не перекомпільовано, ризику нема", size=12, color=FIELD))

    # нижній підсумок
    p.append(text(215, 360, "закрито для розширення", size=12.5, italic=True, color=POS))
    p.append(text(215, 378, "(нове = правка старого)", size=11, color=MUTED))
    p.append(text(645, 360, "відкрито для розширення,", size=12.5, italic=True, color=FIELD))
    p.append(text(645, 378, "закрито для модифікації", size=11, color=MUTED))

    render(os.path.join(IMG, "two-shapes.svg"), W, H, *p)


def fig_hinge():
    """Абстракція — завіса: стабільний клієнт спирається на неї згори,
    змінні реалізації висять знизу. Видно ЩО закрито і ЩО відкрито."""
    W, H = 720, 440
    p = []
    p.append(text(W / 2, 30, "Абстракція — завіса між сталим і змінним", size=17, bold=True))

    # клієнт (стабільний, закритий)
    cx = W / 2
    p.append(fitbox(cx - 150, 60, 300, 54,
                    "Клієнт: report.render(shapes)\nне знає про конкретні фігури",
                    size=13, fill="#eaf0fd", stroke=NEG, sw=1.8))
    p.append(text(cx + 205, 87, "закрито:", size=12, color=NEG, bold=True, anchor="end"))
    p.append(text(cx + 205, 103, "не міняється", size=11, color=MUTED, anchor="end"))

    # завіса — інтерфейс
    ify, ifh = 150, 46
    p.append(line(cx, 114, cx, ify, color=INK, sw=1.5))
    p.append(fitbox(cx - 130, ify, 260, ifh,
                    "interface Shape { area(); }",
                    size=13, fill=FILL, stroke=INK, sw=2))
    p.append(text(cx + 150, ify + ifh / 2 + 4, "завіса", size=12, italic=True, color=MUTED, anchor="start"))

    # реалізації знизу (відкрито: додаємо скільки треба)
    labels = ["Circle", "Rect", "Triangle", "…новий"]
    n = len(labels)
    bw, gap = 130, 20
    total = n * bw + (n - 1) * gap
    x0 = cx - total / 2
    by = 258
    junc_y = ify + ifh          # спільна точка стику — на нижньому краї інтерфейсу
    for i, lab in enumerate(labels):
        x = x0 + i * (bw + gap)
        p.append(line(x + bw / 2, by, cx, junc_y, color=MUTED, sw=1))
    for i, lab in enumerate(labels):
        x = x0 + i * (bw + gap)
        new = (i == n - 1)
        p.append(fitbox(x, by, bw, 44, lab, size=13,
                        fill="#eaf7ee" if new else FILL,
                        stroke=FIELD if new else LINE,
                        sw=1.8 if new else 1.5, bold=new))
    p.append(text(cx, by + 80, "відкрито: нову реалізацію додаємо, нічого вгорі не чіпаючи",
                  size=12.5, color=FIELD))
    p.append(text(cx, by + 102, "( точка розширення там, де ми передбачили вісь змін )",
                  size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, "hinge.svg"), W, H, *p)


def fig_two_versions():
    """Дві прочитки одних слів OCP: ліворуч Меєр (успадкування реалізації —
    нащадок робочого класу), праворуч Мартін (поліморфна підстановка —
    взаємозамінні реалізації під абстрактним інтерфейсом)."""
    W, H = 940, 500
    p = []
    p.append(text(W / 2, 30, "«Відкрито для розширення» — двома способами", size=17, bold=True))

    # роздільна лінія посередині
    p.append(line(W / 2, 54, W / 2, H - 18, color=MUTED, sw=1, dash="6,6"))

    # ── ЛІВА половина: Меєр 1988 — успадкування реалізації ───────────
    lcx = W / 4
    p.append(text(lcx, 76, "Меєр (1988): успадкувати клас", size=14, bold=True, color=NEG))
    p.append(text(lcx, 94, "implementation inheritance", size=11, italic=True, color=MUTED))

    # клієнт лінкується до конкретного класу
    p.append(fitbox(lcx - 130, 112, 260, 40,
                    "Клієнт лінкується з класом",
                    size=12.5, fill="#eaf0fd", stroke=NEG, sw=1.6))
    # конкретний робочий батьківський клас
    py = 190
    p.append(fitbox(lcx - 130, py, 260, 52,
                    "class Report  (робочий)\nполя + код усередині",
                    size=12.5, fill=FILL, stroke=LINE, sw=2))
    # стрілка «лінкується» від клієнта донизу до класу
    p.append(arrow(lcx, 152, lcx, py - 2, color=NEG, sw=1.6))
    p.append(text(lcx + 138, 176, "лінкується", size=10.5, italic=True, color=MUTED, anchor="start"))

    # нащадок успадковує РОБОЧИЙ клас
    ny = 300
    p.append(fitbox(lcx - 96, ny, 192, 48,
                    "class PdfReport\n: Report  + нове",
                    size=12, fill="#eaf7ee", stroke=FIELD, sw=1.8, bold=True))
    p.append(arrow(lcx, ny, lcx, py + 52 + 2, color=FIELD, sw=1.6))
    p.append(text(lcx + 104, ny - 6, "успадковує", size=10.5, italic=True, color=FIELD, anchor="start"))
    p.append(text(lcx + 104, ny + 10, "реалізацію", size=10.5, italic=True, color=FIELD, anchor="start"))
    p.append(plus(lcx + 96 - 6, ny, r=10))

    p.append(text(lcx, 388, "нащадок знає НУТРО предка", size=12, color=NEG))
    p.append(text(lcx, 406, "→ зчеплення з реалізацією", size=11.5, italic=True, color=MUTED))

    # ── ПРАВА половина: Мартін 1996 — поліморфна підстановка ─────────
    rcx = 3 * W / 4
    p.append(text(rcx, 76, "Мартін (1996): абстрактний інтерфейс", size=13.5, bold=True, color=POS))
    p.append(text(rcx, 94, "polymorphic substitution", size=11, italic=True, color=MUTED))

    # клієнт
    p.append(fitbox(rcx - 130, 112, 260, 40,
                    "Клієнт викликає інтерфейс",
                    size=12.5, fill="#eaf0fd", stroke=NEG, sw=1.6))
    # абстракція (фіксована, порожня)
    ay = 190
    p.append(fitbox(rcx - 130, ay, 260, 46,
                    "abstract Report  (лише контракт)",
                    size=12, fill="#f2ecfb", stroke="#7c3aed", sw=2))
    p.append(arrow(rcx, 152, rcx, ay - 2, color=NEG, sw=1.6))
    p.append(text(rcx + 138, 176, "залежить від", size=10.5, italic=True, color=MUTED, anchor="start"))

    # три взаємозамінні реалізації під абстракцією
    labels = ["Pdf", "Html", "…нова"]
    bw, gap, bh = 120, 22, 46
    total = len(labels) * bw + (len(labels) - 1) * gap
    x0 = rcx - total / 2
    by = 300
    junc_x, junc_y = rcx, ay + 46          # точка стику під абстракцією
    for i, lab in enumerate(labels):
        x = x0 + i * (bw + gap)
        p.append(line(x + bw / 2, by, junc_x, junc_y, color=MUTED, sw=1))
    for i, lab in enumerate(labels):
        x = x0 + i * (bw + gap)
        new = (i == len(labels) - 1)
        p.append(fitbox(x, by, bw, bh,
                        lab + "Report", size=11.5,
                        fill="#eaf7ee" if new else FILL,
                        stroke=FIELD if new else LINE,
                        sw=1.8 if new else 1.5, bold=new))
    p.append(plus(x0 + (len(labels) - 1) * (bw + gap) + bw - 6, by, r=10))
    p.append(text(rcx, 388, "реалізації взаємозамінні,", size=12, color=POS))
    p.append(text(rcx, 406, "клієнт про них не знає", size=11.5, italic=True, color=MUTED))

    # нижні ярлики-висновки
    p.append(text(lcx, 448, "слова Меєра, механізм — конкретне успадкування", size=11.5, color=MUTED))
    p.append(text(rcx, 448, "ті самі слова, механізм — абстракція (ця версія в SOLID)", size=11.5, color=MUTED))

    render(os.path.join(IMG, "two-versions.svg"), W, H, *p)


def fig_dispatch_table():
    """Таблиця диспетчеризації: закритий цикл-диспетчер спирається згори на
    масив вказівників «вид знижки → функція»; кожен рядок адресує окремий
    обробник, новий вид додається дописом рядка знизу, диспетчер недоторканий."""
    W, H = 900, 470
    p = []
    p.append(text(W / 2, 30, "Завіса на таблиці: диспетчер закритий, види додаються рядком", size=15.5, bold=True))

    # ── Диспетчер (закритий клієнт) — угорі по центру ───────────────
    dx, dy, dw, dh = W / 2 - 190, 54, 380, 58
    p.append(fitbox(dx, dy, dw, dh,
                    "apply_discount(kind, total, params)\nfn = TABLE[kind];  fn(total, params);",
                    size=12.5, fill="#eaf0fd", stroke=NEG, sw=1.9))
    p.append(text(dx + dw + 10, dy + 20, "закрито:", size=11.5, color=NEG, bold=True, anchor="start"))
    p.append(text(dx + dw + 10, dy + 37, "не міняється", size=10.5, color=MUTED, anchor="start"))

    # ── Таблиця (завіса) — рядки «індекс → обробник» ────────────────
    tx = 150
    tw = 250
    ty0 = 168
    rowh = 36
    rows = ["[DISC_PERCENT]", "[DISC_FLAT]", "[DISC_LOYALTY]", "[DISC_BIRTHDAY]"]
    handlers = ["disc_percent()", "disc_flat()", "disc_loyalty()", "disc_birthday()"]
    hx = 560
    hw = 210

    # лінія-завіса від диспетчера до таблиці (елбоу збоку від заголовка)
    p.append(line(W / 2, dy + dh, hx + hw / 2 - 40, dy + dh, color=INK, sw=1.5))
    p.append(line(hx + hw / 2 - 40, dy + dh, hx + hw / 2 - 40, ty0 - 4, color=INK, sw=1.5))
    p.append(line(hx + hw / 2 - 40, ty0 - 4, hx + hw / 2, ty0 - 4, color=INK, sw=1.5))
    # заголовки колонок — над клітинами, поза лініями
    p.append(text(tx + tw / 2, ty0 - 12, "DISCOUNT_TABLE — вказівники на функції", size=12, italic=True, color=MUTED))
    p.append(text(hx + hw / 2, ty0 - 12, "обробники", size=12, italic=True, color=MUTED))
    p.append(text(tx - 16, ty0 + rowh * 1.5, "завіса", size=12, italic=True, color=MUTED, anchor="end"))

    for i, (rlab, hlab) in enumerate(zip(rows, handlers)):
        yy = ty0 + i * rowh
        new = (i == len(rows) - 1)
        cell_h = rowh - 8
        cy = yy + cell_h / 2
        # клітина-рядок таблиці
        p.append(fitbox(tx, yy, tw, cell_h, rlab, size=12,
                        fill="#eaf7ee" if new else FILL,
                        stroke=FIELD if new else LINE, sw=1.8 if new else 1.3, bold=new))
        # стрілка від рядка до обробника
        p.append(arrow(tx + tw + 6, cy, hx - 6, cy,
                       color=FIELD if new else MUTED, sw=1.6 if new else 1.2))
        # обробник
        p.append(fitbox(hx, yy, hw, cell_h, hlab, size=12,
                        fill="#eaf7ee" if new else FILL,
                        stroke=FIELD if new else LINE, sw=1.8 if new else 1.3, bold=new))

    # позначка «новий вид = один рядок»
    p.append(plus(tx - 6, ty0 + (len(rows) - 1) * rowh, r=11))
    p.append(text(W / 2, ty0 + len(rows) * rowh + 20,
                  "новий вид знижки = дописати ОДИН рядок + написати обробник",
                  size=12.5, color=FIELD, bold=True))
    p.append(text(W / 2, ty0 + len(rows) * rowh + 40,
                  "цикл-диспетчер угорі не редагується жодним символом",
                  size=11.5, italic=True, color=MUTED))

    render(os.path.join(IMG, "dispatch-table.svg"), W, H, *p)


if __name__ == "__main__":
    fig_two_shapes()
    fig_hinge()
    fig_two_versions()
    fig_dispatch_table()
    print("ok: figs generated")
