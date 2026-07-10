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


def fig_axes():
    """Задача про вираз: матриця типи×операції. Новий тип = новий РЯДОК
    (ООП тримає рядки разом → дешево); нова операція = новий СТОВПЕЦЬ
    (метод у кожен клас → правка всюди). Закрити можна лише одну вісь."""
    W, H = 1000, 610
    p = []
    p.append(text(W / 2, 30, "Дві осі зростання: типи (рядки) проти операцій (стовпці)",
                  size=16, bold=True))

    ops = ["area", "perimeter", "draw", "serialize"]     # останній — новий
    types = ["Circle", "Rect", "Triangle", "Hexagon"]    # останній — новий
    lhx, lhw = 60, 150            # ліва шапка (назви типів)
    gx0 = lhx + lhw              # ліва межа клітин = 210
    cw, rh = 175, 56
    hy0, hyh = 78, 40            # верхня шапка (назви операцій)
    gy0 = hy0 + hyh             # верх першого рядка = 118

    # клітини
    for r in range(4):
        for c in range(4):
            x, y = gx0 + c * cw, gy0 + r * rh
            new_col, new_row = (c == 3), (r == 3)
            if new_col:
                fill = "#fdecea"
            elif new_row:
                fill = "#eaf7ee"
            else:
                fill = "#ffffff"
            p.append(rect(x, y, cw, rh, fill=fill, stroke="#c9ced6", sw=1.1, rx=0))

    # кутова клітина-підпис
    p.append(rect(lhx, hy0, lhw, hyh, fill="#f4f6f8", stroke="#c9ced6", sw=1.1, rx=0))
    p.append(text(lhx + lhw / 2, hy0 + hyh / 2 + 4, "тип \\ операція", size=11, color=MUTED))
    # шапка операцій
    for c, op in enumerate(ops):
        new = (c == 3)
        p.append(rect(gx0 + c * cw, hy0, cw, hyh, fill="#f4f6f8", stroke="#c9ced6", sw=1.1, rx=0))
        p.append(text(gx0 + c * cw + cw / 2, hy0 + hyh / 2 + 5, op,
                      size=13.5, bold=True, color=POS if new else INK))
    # шапка типів
    for r, tp in enumerate(types):
        new = (r == 3)
        p.append(rect(lhx, gy0 + r * rh, lhw, rh, fill="#f4f6f8", stroke="#c9ced6", sw=1.1, rx=0))
        p.append(text(lhx + lhw / 2, gy0 + r * rh + rh / 2 + 5, tp,
                      size=13.5, bold=True, color=FIELD if new else INK))

    # позначки «нове»
    p.append(plus(gx0 + 3 * cw + cw - 10, hy0 + hyh / 2, r=10))
    p.append(plus(lhx + 10, gy0 + 3 * rh + rh / 2, r=10))

    # ── виноски під сіткою ──
    gy_bottom = gy0 + 4 * rh      # 342
    fr, fw, fh = textbox(292, 430,
                         "＋ новий ТИП = новий рядок\nООП тримає рядок укупі (клас) —\nдодаємо, старого не чіпаємо",
                         size=12, pad=11, fill="#eaf7ee", stroke=FIELD, sw=1.8)
    p.append(fr)
    fr2, fw2, fh2 = textbox(720, 430,
                            "＋ нова ОПЕРАЦІЯ = новий стовпець\nметод доводиться дописати\nу КОЖЕН наявний клас",
                            size=12, pad=11, fill="#fdecea", stroke=POS, sw=1.8)
    p.append(fr2)

    p.append(text(W / 2, 512, "Процедурний switch — дзеркало: стовпці (операції) дешеві, рядки (типи) дорогі.",
                  size=12.5, color=INK))
    p.append(text(W / 2, 534, "Базовою диспетчеризацією закрити можна ОДНУ вісь, не обидві — це задача про вираз.",
                  size=12.5, italic=True, color=MUTED))

    render(os.path.join(IMG, "axes.svg"), W, H, *p)


def fig_seam_binding():
    """Та сама завіса — на різному часі зв'язування й масштабі. Що пізніше
    зв'язується варіант, то більша відкритість, але дорожче непрямування."""
    W, H = 1060, 470
    p = []
    p.append(text(W / 2, 30, "Одна ідея, чотири завіси: час зв'язування зсуває межу назовні",
                  size=16, bold=True))

    axis_y = 344
    p.append(arrow(80, axis_y, 985, axis_y, color=INK, sw=2))
    p.append(text(80, axis_y + 46, "раніше", size=11, color=MUTED, anchor="start"))
    p.append(text(985, axis_y + 46, "пізніше", size=11, color=MUTED, anchor="end"))

    stations = [
        (200, "Віртуальний клас\nабо шаблон", "збірка (compile/link)", "клас"),
        (430, "Таблиця-реєстр\n(dispatch table)", "старт застосунку", "модуль"),
        (665, "Плагін\n(динамічне завантаж.)", "завантаження", "застосунок"),
        (895, "Події / шина\npublish · subscribe", "рантайм / мережа", "система, сервіси"),
    ]
    box_y, box_w, box_h = 168, 196, 58
    for sx, label, bind, scale in stations:
        p.append(fitbox(sx - box_w / 2, box_y, box_w, box_h, label,
                        size=12.5, fill="#eef4ff", stroke=NEG, sw=1.7, bold=True))
        # конектор від рамки до осі
        p.append(line(sx, box_y + box_h, sx, axis_y - 6, color=MUTED, sw=1.1, dash="4,3"))
        p.append(circle(sx, axis_y, 4, fill=INK, stroke=INK, sw=1))
        p.append(text(sx, axis_y + 22, bind, size=11.5, bold=True, color=INK))
        p.append(text(sx, box_y - 12, scale, size=11.5, italic=True, color=FIELD))

    p.append(text(W / 2, 92, "масштаб завіси ↑   ·   пізніше зв'язування →",
                  size=12, italic=True, color=MUTED))
    p.append(text(W / 2, 424,
                  "Пізніше зв'язування: варіант додають без перезбирання — ціна за це більше непрямування.",
                  size=12.5, color=INK))

    render(os.path.join(IMG, "seam-binding.svg"), W, H, *p)


def fig_open_closed_set():
    """Коли закриватися, а коли — навпаки. Відкрита множина типів → поліморфна
    завіса (OCP). Замкнена, скінченна → вичерпний switch: компілятор сам
    показує кожне місце для оновлення; відкритість тут лише сховала б їх."""
    W, H = 1020, 560
    p = []
    p.append(text(W / 2, 30, "Відкрита множина — завіса; замкнена — вичерпний switch",
                  size=16, bold=True))

    # верхнє питання
    p.append(fitbox(W / 2 - 200, 58, 400, 50,
                    "Множина варіантів (типів) — яка вона?",
                    size=14, bold=True, fill="#f4f6f8", stroke=INK, sw=1.8))

    lcx, rcx = 268, 752
    bw = 344

    # ── ЛІВА гілка: відкрита ──
    l1 = fitbox(lcx - bw / 2, 154, bw, 58,
                "ВІДКРИТА / росте\nнові фігури, провайдери, формати весь час",
                size=12.5, bold=True, fill="#eaf7ee", stroke=FIELD, sw=1.9)
    l2 = fitbox(lcx - bw / 2, 288, bw, 58,
                "Поліморфна завіса:\nінтерфейс + взаємозамінні реалізації",
                size=12.5, fill="#ffffff", stroke=FIELD, sw=1.6)
    l3 = fitbox(lcx - bw / 2, 418, bw, 62,
                "закрито для модифікації:\nновий варіант не чіпає старе",
                size=12.5, bold=True, fill="#eaf7ee", stroke=FIELD, sw=1.9)
    p += [l1, l2, l3]

    # ── ПРАВА гілка: замкнена ──
    r1 = fitbox(rcx - bw / 2, 154, bw, 58,
                "ЗАМКНЕНА / відома\n3 стани, 4 масті — скінченна й стабільна",
                size=12.5, bold=True, fill="#eef4ff", stroke=NEG, sw=1.9)
    r2 = fitbox(rcx - bw / 2, 288, bw, 58,
                "Вичерпний switch / sealed /\nсума типів",
                size=12.5, fill="#ffffff", stroke=NEG, sw=1.6)
    r3 = fitbox(rcx - bw / 2, 418, bw, 62,
                "компілятор флагує КОЖНЕ\nмісце, що треба оновити",
                size=12.5, bold=True, fill="#eef4ff", stroke=NEG, sw=1.9)
    p += [r1, r2, r3]

    # стрілки
    p.append(arrow(W / 2 - 90, 108, lcx + 40, 152, color=FIELD, sw=1.9))
    p.append(arrow(W / 2 + 90, 108, rcx - 40, 152, color=NEG, sw=1.9))
    p.append(arrow(lcx, 212, lcx, 286, color=FIELD, sw=1.9))
    p.append(arrow(lcx, 346, lcx, 416, color=FIELD, sw=1.9))
    p.append(arrow(rcx, 212, rcx, 286, color=NEG, sw=1.9))
    p.append(arrow(rcx, 346, rcx, 416, color=NEG, sw=1.9))

    p.append(text(W / 2, 516,
                  "Відкритість корисна там, де множина справді відкрита.",
                  size=12.5, color=INK))
    p.append(text(W / 2, 538,
                  "На замкненій множині завіса лише сховала б місця, які інакше вказав би компілятор.",
                  size=12.5, italic=True, color=MUTED))

    render(os.path.join(IMG, "open-closed-set.svg"), W, H, *p)


def fig_double_dispatch():
    """Подвійна диспетчеризація: два віртуальні виклики поспіль (спершу за типом
    елемента, потім за типом відвідувача) сходяться в одну клітину матриці
    типи×операції. Видно, ЧОМУ «подвійна» і що саме обирає кожен виклик."""
    W, H = 940, 500
    p = []
    p.append(text(W / 2, 30, "Подвійна диспетчеризація: два виклики → одна клітина",
                  size=16, bold=True))

    bx, bw = 70, 430              # рамки: ліво/ширина (спан 70..500)
    cx = bx + bw / 2              # 285 — вісь рамок і стрілок
    lx = bx + bw + 26             # 526 — підписи стрілок праворуч від рамок

    # Рамка 1 — вхідний виклик
    p.append(fitbox(bx, 66, bw, 56,
                    "add.accept(printer)\nadd : Add      ·      printer : Print",
                    size=13.5, fill=FILL, stroke=INK, sw=1.8))
    # Стрілка 1 + підпис
    p.append(arrow(cx, 124, cx, 160, color=INK, sw=1.8))
    p.append(text(lx, 137, "① за РЕАЛЬНИМ типом", size=12.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(lx, 154, "елемента  →  РЯДОК", size=12.5, color=FIELD, bold=True, anchor="start"))

    # Рамка 2 — accept у класі елемента
    p.append(fitbox(bx, 166, bw, 56,
                    "Add.accept(v)  {  return v.visitAdd(this)  }\nобрано РЯДОК матриці:  Add",
                    size=13, fill="#eaf7ee", stroke=FIELD, sw=1.8))
    # Стрілка 2 + підпис
    p.append(arrow(cx, 222, cx, 258, color=INK, sw=1.8))
    p.append(text(lx, 235, "② за РЕАЛЬНИМ типом", size=12.5, color=NEG, bold=True, anchor="start"))
    p.append(text(lx, 252, "відвідувача  →  СТОВПЕЦЬ", size=12.5, color=NEG, bold=True, anchor="start"))

    # Рамка 3 — visit у класі відвідувача
    p.append(fitbox(bx, 264, bw, 56,
                    "Print.visitAdd(a)  {  …будує рядок…  }\nобрано СТОВПЕЦЬ матриці:  Print",
                    size=13, fill="#eaf0fd", stroke=NEG, sw=1.8))
    # Стрілка 3
    p.append(arrow(cx, 320, cx, 356, color=INK, sw=1.8))

    # Рамка 4 — одна клітина
    p.append(fitbox(bx, 362, bw, 48,
                    "виконано РІВНО ОДНЕ тіло — клітина ( Add × Print )",
                    size=13.5, fill="#eafaef", stroke=FIELD, sw=2.2, bold=True))

    p.append(text(W / 2, 452, "«Подвійна» — це два звичайні віртуальні виклики поспіль;",
                  size=12.5, italic=True, color=MUTED))
    p.append(text(W / 2, 470,
                  "їх перетин (тип елемента × тип відвідувача) і є одна клітина матриці операцій.",
                  size=12.5, italic=True, color=MUTED))

    render(os.path.join(IMG, "double-dispatch.svg"), W, H, *p)


def fig_visitor_matrix():
    """Та сама матриця типи×операції, але в аранжуванні Відвідувача: СТОВПЕЦЬ —
    це клас-відвідувач. Новий відвідувач = цілий новий стовпець (елементи не
    чіпаємо); новий тип вузла = новий рядок → метод у КОЖЕН відвідувач. Дзеркало
    віртуальних методів, де клас = рядок."""
    W, H = 1000, 580
    p = []
    p.append(text(W / 2, 30, "Відвідувач групує код за СТОВПЦЕМ (стовпець = клас-відвідувач)",
                  size=16, bold=True))

    cols = ["Eval", "Print", "Depth"]                        # останній — новий відвідувач
    rows = ["visitNum", "visitAdd", "visitMul", "visitNeg"]  # назва методу за рядком
    node_labels = ["Num", "Add", "Mul", "Neg"]               # останній — новий вузол

    lhx, lhw = 70, 170            # ліва шапка (типи вузлів)
    gx0 = lhx + lhw               # 240
    cw, rh = 230, 62
    hy0, hyh = 84, 44             # верхня шапка (відвідувачі)
    gy0 = hy0 + hyh               # 128

    # клітини
    for r in range(4):
        for c in range(3):
            x, y = gx0 + c * cw, gy0 + r * rh
            new_col, new_row = (c == 2), (r == 3)
            if new_row:
                fill = "#fdecea"
            elif new_col:
                fill = "#eaf7ee"
            else:
                fill = "#ffffff"
            p.append(rect(x, y, cw, rh, fill=fill, stroke="#c9ced6", sw=1.1, rx=0))
            mcol = POS if new_row else (FIELD if new_col else MUTED)
            p.append(text(x + cw / 2, y + rh / 2 + 5, rows[r] + "()", size=12.5, color=mcol))

    # кутова клітина
    p.append(rect(lhx, hy0, lhw, hyh, fill="#f4f6f8", stroke="#c9ced6", sw=1.1, rx=0))
    p.append(text(lhx + lhw / 2, hy0 + hyh / 2 + 4, "вузол \\ відвідувач", size=11.5, color=MUTED))

    # шапка відвідувачів (стовпці)
    for c, col in enumerate(cols):
        new = (c == 2)
        p.append(rect(gx0 + c * cw, hy0, cw, hyh, fill="#f4f6f8", stroke="#c9ced6", sw=1.1, rx=0))
        p.append(text(gx0 + c * cw + cw / 2, hy0 + hyh / 2 + 5, col + " : Visitor",
                      size=13.5, bold=True, color=FIELD if new else INK))

    # шапка типів вузлів (рядки)
    for r, nl in enumerate(node_labels):
        new = (r == 3)
        p.append(rect(lhx, gy0 + r * rh, lhw, rh, fill="#f4f6f8", stroke="#c9ced6", sw=1.1, rx=0))
        p.append(text(lhx + lhw / 2, gy0 + r * rh + rh / 2 + 5, nl,
                      size=13.5, bold=True, color=POS if new else INK))

    # позначки «нове»
    p.append(plus(gx0 + 3 * cw - 12, hy0 + hyh / 2, r=10))     # новий стовпець
    p.append(plus(lhx + 12, gy0 + 3 * rh + rh / 2, r=10))       # новий рядок

    # ── легенда під сіткою ──
    fr, _, _ = textbox(300, 456,
                       "＋ новий відвідувач = новий СТОВПЕЦЬ\nодин новий клас — елементи не чіпаємо\n(закрито проти осі операцій)",
                       size=12.5, pad=12, fill="#eaf7ee", stroke=FIELD, sw=1.8)
    p.append(fr)
    fr2, _, _ = textbox(722, 456,
                        "＋ новий тип вузла = новий РЯДОК\nметод visitNeg() у КОЖЕН відвідувач\n(дзеркальна ціна)",
                        size=12.5, pad=12, fill="#fdecea", stroke=POS, sw=1.8)
    p.append(fr2)

    p.append(text(W / 2, 548,
                  "Дзеркало віртуальних методів: там клас = рядок (новий тип дешевий) — тут відвідувач = стовпець (нова операція дешева).",
                  size=11.5, italic=True, color=INK))

    render(os.path.join(IMG, "visitor-matrix.svg"), W, H, *p)


def fig_expr_dispatch():
    """Чому базова диспетчеризація закриває РІВНО одну вісь: щоб старий код не
    редагувати, спільний контракт мусить перелічити одну з двох осей — саме її
    й закриває. Об'єктний виклик перелічує операції (закрито, типи відкриті);
    процедурний — дзеркало (перелічує типи, операції відкриті)."""
    W, H = 980, 480
    p = []
    p.append(text(W / 2, 30, "Спільний контракт перелічує одну вісь — саме її й закриває",
                  size=16, bold=True))
    p.append(line(W / 2, 56, W / 2, H - 52, color=MUTED, sw=1, dash="6,6"))

    def panel(cx, header, sub, contract, clabel, members, mlab):
        pp = []
        pp.append(text(cx, 80, header, size=14, bold=True, color=INK))
        pp.append(text(cx, 99, sub, size=11, italic=True, color=MUTED))
        # контракт — перелічена вісь = закрита (POS)
        pp.append(fitbox(cx - 180, 118, 360, 46, contract, size=12.5,
                         fill="#fdecea", stroke=POS, sw=1.9))
        pp.append(text(cx, 182, clabel, size=11.5, color=POS, bold=True))
        # відкрита вісь — члени (FIELD), останній новий
        bw, gap, by, bh = 118, 16, 252, 44
        total = 3 * bw + 2 * gap
        x0 = cx - total / 2
        for i, lab in enumerate(members):
            x = x0 + i * (bw + gap)
            new = (i == 2)
            pp.append(fitbox(x, by, bw, bh, lab, size=12.5,
                             fill="#eaf7ee" if new else FILL,
                             stroke=FIELD if new else LINE,
                             sw=1.8 if new else 1.4, bold=new))
        pp.append(plus(x0 + 2 * (bw + gap) + bw - 6, by, r=10))
        pp.append(text(cx, by + bh + 24, mlab[0], size=11.5, color=FIELD, bold=True))
        pp.append(text(cx, by + bh + 42, mlab[1], size=11, color=MUTED))
        return pp

    p += panel(245, "Об'єктний стиль — x.op()", "інтерфейс фіксує операції",
               "interface Shape\n{ area(); perimeter(); }",
               "перелічує ОПЕРАЦІЇ → вісь закрита",
               ["Circle", "Rect", "+ новий тип"],
               ["новий тип = новий клас,", "контракт недоторканий → відкрито"])
    p += panel(735, "Процедурний стиль — op(x)", "сума типів фіксує випадки",
               "enum Kind\n{ Circle, Rect }",
               "перелічує ТИПИ → вісь закрита",
               ["area()", "perimeter()", "+ нова оп."],
               ["нова операція = нова функція,", "контракт недоторканий → відкрито"])

    p.append(text(W / 2, H - 30,
                  "Одна вісь мусить лягти у спільний контракт — саме вона й закрита.",
                  size=12.5, color=INK))
    p.append(text(W / 2, H - 12,
                  "Базова (одинарна) диспетчеризація тримає відкритою рівно одну вісь.",
                  size=12.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "single-dispatch-axis.svg"), W, H, *p)


def fig_four_exits():
    """Чотири виходи із задачі про вираз і ціна кожного. Жоден базовий засіб не
    закриває обидві осі; за відкриття обох платять віссю (Відвідувач), статикою
    (мультиметоди), правилами узгодженості (трейти) чи кодуванням (алгебри)."""
    W, H = 1020, 486
    p = []
    p.append(text(W / 2, 28, "Чотири виходи із задачі про вираз — і чим кожен платить",
                  size=16, bold=True))

    # колонки: (назва, x, ширина)
    cols = [("рішення", 30, 232), ("+ новий\nтип", 262, 120),
            ("+ нова\nоперація", 382, 120), ("статична\nбезпека", 502, 120),
            ("ціна", 622, 368)]
    hy, hh = 50, 50
    ry0, rh = 100, 76

    # шапка
    for name, x, w in cols:
        p.append(fitbox(x, hy, w, hh, name, size=12.5, bold=True,
                        fill="#eef1f5", stroke="#c9ced6", sw=1.2, rx=4))

    def mark(x, y, w, h, ok):
        r = rect(x, y, w, h, fill=BG, stroke="#c9ced6", sw=1.1, rx=4)
        g = text(x + w / 2, y + h / 2 + 9, "✓" if ok else "✗",
                 size=25, bold=True, color=FIELD if ok else POS)
        return r + g

    rows = [
        ("Відвідувач\n(Visitor)", False, True, True,
         "перевертає вісь: операції\nвідкриті, типи — ні;\n+ accept-код"),
        ("Множинна диспетчеризація\n(CLOS, Julia)", True, True, False,
         "пропущену пару (тип, оп)\nловить рантайм, а не\nкомпілятор"),
        ("Класи типів / трейти\n(Haskell, Rust)", True, True, True,
         "узгодженість (orphan-\nправило): інстанс лише\nдля свого типу чи класу"),
        ("Обʼєктні алгебри /\ntagless-final", True, True, True,
         "терм Church-кодований:\nвільно розбирати його\nструктуру вже не можна"),
    ]
    for i, (nm, a, b, c, price) in enumerate(rows):
        y = ry0 + i * rh
        p.append(fitbox(cols[0][1], y, cols[0][2], rh, nm, size=12,
                        fill="#eaf0fd", stroke="#c9ced6", sw=1.1, rx=4))
        p.append(mark(cols[1][1], y, cols[1][2], rh, a))
        p.append(mark(cols[2][1], y, cols[2][2], rh, b))
        p.append(mark(cols[3][1], y, cols[3][2], rh, c))
        p.append(fitbox(cols[4][1], y, cols[4][2], rh, price, size=11.5,
                        fill=BG, stroke="#c9ced6", sw=1.1, rx=4))

    p.append(text(W / 2, ry0 + 4 * rh + 26,
                  "Закрити ОБИДВІ осі базовими засобами не можна.",
                  size=12.5, bold=True, color=INK))
    p.append(text(W / 2, ry0 + 4 * rh + 46,
                  "За це платять: віссю (Відвідувач) · статикою (мультиметоди) · правилами (трейти) · кодуванням (алгебри).",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "four-exits.svg"), W, H, *p)


if __name__ == "__main__":
    fig_two_shapes()
    fig_hinge()
    fig_two_versions()
    fig_dispatch_table()
    fig_axes()
    fig_seam_binding()
    fig_open_closed_set()
    fig_double_dispatch()
    fig_visitor_matrix()
    fig_expr_dispatch()
    fig_four_exits()
    print("ok: figs generated")
