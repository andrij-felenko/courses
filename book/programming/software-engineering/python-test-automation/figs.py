# -*- coding: utf-8 -*-
"""Фігури теми «Python для автоматизації тестування». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── 1. Куди йде час одного прогону тесту ──────────────────────────────────────
# Ідея: майже весь час тест ЧЕКАЄ (скидання, завантаження, відповідь), а власні
# обчислення обв'язки — це одиниці мілісекунд. Звідси: швидкодія мови обв'язки
# не є силою, що тисне на вибір інструмента.
def fig_time_budget():
    W, H = 960, 430
    f = []

    x0, x1 = 60, 900
    total = 1700.0
    bar_y, bar_h = 170, 54
    px = (x1 - x0) / total

    segs = [
        ("скидання плати", "300 мс", 300.0, "#dfe7f5", NEG),
        ("завантаження прошивки", "1200 мс", 1200.0, "#e8eef7", NEG),
        ("очікування відповіді", "200 мс", 200.0, "#d4edda", FIELD),
    ]

    x = x0
    for name, ms, val, fill, stroke in segs:
        w = val * px
        f.append(rect(x, bar_y, w, bar_h, fill=fill, stroke=stroke, sw=1.6, rx=4))
        cx = x + w / 2
        f.append(mtext(cx, 120, [name, ms], size=13, color=INK))
        f.append(line(cx, 136, cx, bar_y - 6, color=MUTED, sw=1.0, dash="3,3"))
        x += w

    # власний код обв'язки: 2 мс з 1700 — смужку свідомо намальовано ширшою
    f.append(rect(x1 - 6, bar_y, 6, bar_h, fill="#fdecea", stroke=POS, sw=1.6, rx=1))
    f.append(line(x1 - 3, bar_y + bar_h, 700, 300, color=POS, sw=1.3))
    b, bw, bh = textbox(560, 330,
                        "власний код обв'язки:\nрозібрати рядок і порівняти — 2 мс\n"
                        "(смужку намальовано ширшою, ніж вона є)",
                        size=13, fill="#fdecea", stroke=POS, sw=1.6, pad=12)
    f.append(b)

    f.append(text(480, 400, "разом ≈ 1.7 с на один тест · процесор обв'язки — 0.1% цього часу",
                  size=14, bold=True))

    render(out("time-budget.svg"), W, H, *f,
           title="Куди йде час одного прогону тесту")


# ── 2. Чому в тесті можна писати звичайний assert ─────────────────────────────
# Ідея: різниця не в операторі, а в моменті втручання — каркас переписує вузол
# assert між читанням файлу й виконанням, тому падіння знає проміжні значення.
def fig_assert_rewrite():
    W, H = 1000, 590
    f = []

    f.append(text(250, 70, "звичайний імпорт", size=15, bold=True, color=NEG))
    f.append(text(720, 70, "імпорт під наглядом каркаса", size=15, bold=True, color=FIELD))
    f.append(line(490, 95, 490, 545, color=MUTED, sw=1.2, dash="6,5"))

    # ліва колонка
    left = [
        (130, "модуль із тестами\n(текст програми)", FILL, LINE),
        (235, "байткод як є", FILL, LINE),
    ]
    prev = None
    for cy, s, fill, stroke in left:
        b, bw, bh = textbox(250, cy, s, size=13, fill=fill, stroke=stroke, pad=12)
        f.append(b)
        if prev:
            f.append(arrow(250, prev, 250, cy - bh / 2 - 4, color=LINE))
        prev = cy + bh / 2 + 4
    b, bw, bh = textbox(250, 360, "падіння каже лише:\nAssertionError",
                        size=13, fill="#fdecea", stroke=POS, sw=2, pad=12)
    f.append(arrow(250, prev, 250, 360 - bh / 2 - 4, color=LINE))
    f.append(b)

    # права колонка
    right = [
        (130, "модуль із тестами\n(текст програми)", FILL, LINE),
        (222, "синтаксичне дерево", FILL, LINE),
        (325, "вузол assert замінено:\nобчислити в тимчасові,\nпорівняти, зібрати опис", "#e8f6ec", FIELD),
        (440, "байткод + кеш .pyc", FILL, LINE),
    ]
    prev = None
    for cy, s, fill, stroke in right:
        b, bw, bh = textbox(720, cy, s, size=13, fill=fill, stroke=stroke, pad=12)
        f.append(b)
        if prev:
            f.append(arrow(720, prev, 720, cy - bh / 2 - 4, color=LINE))
        prev = cy + bh / 2 + 4
    b, bw, bh = textbox(720, 525, "падіння каже:\nassert 'PONG\\r' == 'PONG'",
                        size=13, fill="#d4edda", stroke=FIELD, sw=2, pad=12)
    f.append(arrow(720, prev, 720, 525 - bh / 2 - 4, color=LINE))
    f.append(b)

    render(out("assert-rewrite.svg"), W, H, *f,
           title="Чому в тесті можна писати звичайний assert")


# ── 3. Область фікстури: витрати проти ізоляції ───────────────────────────────
# Ідея: одна ручка регулює і час прогону, і щільність ізоляції — ширша область
# дешевша, але відкриває канал, яким стан одного тесту тече в наступний.
def fig_fixture_scopes():
    W, H = 1000, 500
    f = []

    x0, step = 190, 126
    tests = 6

    # смуга тестів
    for i in range(tests):
        x = x0 + i * step
        f.append(fitbox(x + 4, 306, step - 8, 46, "тест %d" % (i + 1), size=14))
    f.append(text(170, 335, "прогін", size=13, color=MUTED, anchor="end"))

    # сесійна область
    f.append(rect(x0, 96, step * tests, 40, fill="#e8eef7", stroke=NEG, sw=1.8))
    f.append(text(x0 + step * tests / 2, 121,
                  "сесійна: відкрити порт, підняти базу — один раз на весь прогін", size=13))
    f.append(text(170, 121, "область: сесія", size=13, color=MUTED, anchor="end"))

    # модульна область
    for k in range(2):
        x = x0 + k * step * 3
        f.append(rect(x + 3, 166, step * 3 - 6, 40, fill="#eef2f7", stroke=LINE, sw=1.6))
        f.append(text(x + step * 1.5, 191, "модульна: схема бази", size=13))
    f.append(text(170, 191, "область: модуль", size=13, color=MUTED, anchor="end"))

    # функційна область
    for i in range(tests):
        x = x0 + i * step
        f.append(fitbox(x + 6, 236, step - 12, 40, "скидання", size=12,
                        fill="#e8f6ec", stroke=FIELD))
    f.append(text(170, 261, "область: тест", size=13, color=MUTED, anchor="end"))

    # протікання стану
    cx2 = x0 + 1.5 * step
    cx5 = x0 + 4.5 * step
    f.append(text(500, 392, "стан, змінений у тесті 2, доїжджає до тесту 5 —"
                            " якщо сесійна фікстура змінювана", size=13, color=POS))
    f.append(arrow(cx2, 412, cx5, 412, color=POS, sw=1.8))

    f.append(text(500, 462, "ширша область — менше витрат на кожен тест і більше "
                            "каналів для протікання стану", size=14, bold=True))

    render(out("fixture-scopes.svg"), W, H, *f,
           title="Область фікстури: витрати проти ізоляції")


# ── 4. Три способи дістатися до системи ───────────────────────────────────────
# Ідея: чим ближче обв'язка підходить до системи, тим дрібніше вона бачить —
# і тим менше захисту лишається від аварії самої системи.
def fig_three_doors():
    W, H = 1010, 580
    f = []

    # тіло обв'язки
    f.append(rect(40, 100, 145, 400, fill="#eef2f7", stroke=LINE, sw=1.8))
    f.append(mtext(112, 285, ["обв'язка", "на Python"], size=15, bold=True))

    rows = [
        (160, "запуск процесу", "система як\nокремий процес",
         "аварія не чіпає обв'язку;\nвидно лише вивід\nі код повернення", True),
        (300, "сокет або порт", "плата чи сервіс\nна тому кінці лінії",
         "перевіряється й сам\nпротокол; усередину\nсистеми не видно", True),
        (450, "виклик функції", "бібліотека, завантажена\nв цей самий процес",
         "видно кожну функцію;\nаварія вбиває обв'язку\nразом зі звітом", False),
    ]

    for y, doorname, mid, cons, crosses in rows:
        bm, wm, hm = textbox(470, y, mid, size=13, pad=12,
                             fill="#f4f6f8" if crosses else "#fdecea",
                             stroke=LINE if crosses else POS, sw=1.6)
        f.append(arrow(185, y, 470 - wm / 2 - 6, y, color=LINE))
        f.append(text(300, y - 14, doorname, size=12, color=MUTED))
        f.append(bm)
        bc, wc, hc = textbox(800, y, cons, size=13, pad=12, fill="#fbfbfc",
                             stroke=MUTED, sw=1.4)
        f.append(arrow(470 + wm / 2 + 6, y, 800 - wc / 2 - 6, y, color=MUTED, sw=1.5))
        f.append(bc)

    # межа процесу — лише для перших двох дверей
    f.append(line(300, 118, 300, 372, color=NEG, sw=1.6, dash="7,5"))
    f.append(text(300, 108, "межа процесу", size=12, color=NEG))
    f.append(text(300, 528, "межі немає: чужий код у пам'яті обв'язки",
                  size=12, color=POS))
    f.append(line(300, 498, 300, 514, color=POS, sw=1.6, dash="7,5"))

    render(out("three-doors.svg"), W, H, *f,
           title="Три способи дістатися до системи, що не на Python")


# ── 5. Дві лінії родоводу: методи-твердження й звичайний assert ───────────────
# Для вставки hist-plain-assert.md. Верхня доріжка — як обмеження Java доїхало
# в стандартну бібліотеку Python; нижня — як його зняли з боку PyPy/py.test.
def fig_assert_lineage():
    W, H = 1220, 620
    f = []

    def track(y, label, sub, items, accent):
        f.append(text(W / 2, y - 78, label, size=17, color=accent, bold=True))
        f.append(text(W / 2, y - 56, sub, size=13, color=MUTED, italic=True))
        boxes = []
        for cx, lines in items:
            body, w, h = textbox(cx, y, lines, size=13, pad=11,
                                 stroke=accent, sw=1.8, min_w=176)
            boxes.append((cx, w, body))
        for i in range(len(boxes) - 1):
            x_from = boxes[i][0] + boxes[i][1] / 2 + 8
            x_to = boxes[i + 1][0] - boxes[i + 1][1] / 2 - 8
            f.append(arrow(x_from, y, x_to, y, color=MUTED, sw=1.6))
        for _, _, body in boxes:
            f.append(body)

    top_y = 150
    track(top_y,
          "Лінія xUnit: перевірка — це виклик методу",
          "обмеження мови-джерела їде разом із каркасом",
          [(158, "SUnit\nSmalltalk, 1994 *"),
           (450, "JUnit\nБек і Гамма, 1997"),
           (742, "PyUnit\nСтів Перселл, 1999"),
           (1044, "unittest у stdlib\nPython 2.1, 17.04.2001")],
          NEG)

    f.append(fitbox(200, 238, 820, 46,
                    "assertEqual(a, b) — значення треба ПЕРЕДАТИ методу, бо вираз їх не доносить",
                    size=14, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.2))

    bot_y = 440
    track(bot_y,
          "Лінія py.test: перевірка — це звичайний вираз",
          "обмеження знімають, зазирнувши в код тесту до запуску",
          [(140, "тести PyPy\nГ. Крекель, 2003"),
           (410, "std / utest\nEuroPython 2004"),
           (680, "py.test\nвересень 2004"),
           (950, "pytest 2.0\nлистопад 2010")],
          POS)

    # окремо — фінальний вузол ширший, ставимо власноруч під рядком
    body, w, h = textbox(W / 2, 552, "pytest 2.1, 9 липня 2011 — справжній перепис AST "
                                     "(Б. Петерсон, за підтримки merlinux)",
                         size=13, pad=11, stroke=POS, sw=2.0, fill="#fdecea")
    f.append(arrow(W / 2, bot_y + 30, W / 2, 552 - h / 2 - 8, color=POS, sw=1.8))
    f.append(body)

    f.append(text(158, 208, "* дата спірна: 1989 або 1994", size=11,
                  color=MUTED, italic=True, anchor="start"))

    render(out("assert-lineage.svg"), W, H, *f,
           title="Два родоводи твердження в Python-тестах")


# ── 6. Порядок побудови й прибирання фікстур ─────────────────────────────────
# Для вставки api-pytest-contract.md. Довідка контракту: ширша область — раніше
# будується й пізніше прибирається; прибирання йде точно у зворотному порядку.
def fig_fixture_order():
    W, H = 1060, 630
    f = []

    f.append(text(150, 92, "побудова ↓", size=13, color=NEG, bold=True, anchor="start"))
    f.append(text(985, 92, "прибирання ↑", size=13, color=POS, bold=True, anchor="end"))

    rows = [
        ("port",     "session",            "відкрити порт, дочекатися зв'язку"),
        ("schema",   "module",             "розгорнути порожню схему бази"),
        ("seed_rng", "function · autouse", "зафіксувати насіння генератора"),
        ("device",   "function",           "скинути плату, дочекатися готовності"),
    ]

    y0, dy = 118, 68
    bw, bh = 500, 50

    for i, (name, scope, what) in enumerate(rows):
        y = y0 + i * dy
        x = 96 + i * 50
        f.append(fitbox(x, y, bw, bh, f"{name} ({scope}) — {what}",
                        size=13, fill="#eef3fb", stroke=NEG, sw=1.7))
        cy = y + bh / 2
        f.append(circle(x - 27, cy, 15, fill="#eaf0fd", stroke=NEG, sw=1.8))
        f.append(text(x - 27, cy + 5, str(i + 1), size=13, color=NEG, bold=True))
        f.append(circle(x + bw + 27, cy, 15, fill="#fdecea", stroke=POS, sw=1.8))
        f.append(text(x + bw + 27, cy + 5, str(9 - i), size=13, color=POS, bold=True))

    # тіло самого тесту — п'ятий крок, посередині «сходів»
    yt = y0 + 4 * dy
    xt = 96 + 4 * 50
    f.append(fitbox(xt, yt, bw, bh, "тіло тесту: стимул → спостереження → assert",
                    size=13, fill="#e8f6ec", stroke=FIELD, sw=1.9, bold=True))
    f.append(circle(xt - 27, yt + bh / 2, 15, fill="#e8f6ec", stroke=FIELD, sw=1.8))
    f.append(text(xt - 27, yt + bh / 2 + 5, "5", size=13, color=FIELD, bold=True))

    note = ("Прибирання прив'язане до власного yield КОЖНОЇ фікстури, а не до спільного tearDown.\n"
            "Тому якщо setup кроку 4 упаде, кроки 7 · 8 · 9 однаково виконаються — не виконається\n"
            "лише те, що стоїть після yield самої «device»: туди виконання просто не дійшло.")
    f.append(fitbox(96, 518, 868, 82, note, size=13,
                    fill="#fbfbfc", stroke=MUTED, sw=1.4))

    render(out("fixture-order.svg"), W, H, *f,
           title="Один тест: що будується, у якому порядку — і що прибирається")


# ── 7. Ланцюг conftest.py, який бачить один тестовий файл ────────────────────
# Для вставки api-pytest-contract.md. Довідка контракту: видно лише conftest
# на шляху від rootdir до власної теки; сусідня гілка невидима.
def fig_conftest_chain():
    W, H = 1080, 700
    f = []

    rows = [
        (0, "dir",  "проєкт/",      "тут лежить pytest.toml → ця тека і є rootdir"),
        (1, "conf", "conftest.py",  "pytest_addoption — можна ЛИШЕ тут (корінь набору)"),
        (1, "dir",  "tests/",       ""),
        (2, "conf", "conftest.py",  "фікстури й гачки для всього набору"),
        (2, "dir",  "hardware/",    ""),
        (3, "conf", "conftest.py",  "фікстури лише цієї гілки; ім'я перекриває верхнє"),
        (3, "test", "test_link.py", "бачить усі три — саме в порядку ① → ② → ③"),
        (2, "dir",  "unit/",        ""),
        (3, "gone", "conftest.py",  "невидимий для test_link.py: сусідня гілка"),
    ]

    y0, dy = 92, 50
    numbered = 0

    for i, (ind, kind, label, ann) in enumerate(rows):
        y = y0 + i * dy
        x = 70 + ind * 46

        if kind == "dir":
            f.append(text(x, y + 22, label, size=14, color=MUTED,
                          bold=True, anchor="start"))
        elif kind == "test":
            f.append(fitbox(x, y, 190, 34, label, size=13,
                            fill="#e8f6ec", stroke=FIELD, sw=1.9, bold=True))
        elif kind == "conf":
            numbered += 1
            f.append(fitbox(x, y, 190, 34, label, size=13,
                            fill="#eef3fb", stroke=NEG, sw=1.7))
            f.append(circle(x - 22, y + 17, 13, fill="#eaf0fd", stroke=NEG, sw=1.7))
            f.append(text(x - 22, y + 22, "①②③"[numbered - 1], size=13,
                          color=NEG, bold=True))
        else:  # gone
            f.append(fitbox(x, y, 190, 34, label, size=13,
                            fill="#fdecea", stroke=POS, sw=1.5))
            f.append(circle(x - 22, y + 17, 13, fill="#fdecea", stroke=POS, sw=1.7))
            f.append(text(x - 22, y + 22, "✗", size=13, color=POS, bold=True))

        if ann:
            f.append(text(500, y + 22, ann, size=13, color=INK, anchor="start"))

    # вертикаль, що показує шлях завантаження зверху вниз
    f.append(line(48, 118, 48, 92 + 6 * dy + 17, color=NEG, sw=1.6, dash="6,4"))
    f.append(text(48, 92 + 6 * dy + 42, "згори вниз", size=12, color=NEG))

    note = ("Ланцюг рахують від rootdir до теки самого файлу; conftest сусідньої гілки не завантажується взагалі.\n"
            "Межу пошуку вгору звужує --confcutdir. Усі conftest.py імпортуються ДО тестових модулів —\n"
            "тому pytest.register_assert_rewrite(\"helpers\") має стояти саме там, інакше assert у помічнику лишиться німим.")
    f.append(fitbox(70, 574, 940, 88, note, size=13,
                    fill="#fbfbfc", stroke=MUTED, sw=1.4))

    render(out("conftest-chain.svg"), W, H, *f,
           title="Які conftest.py бачить файл tests/hardware/test_link.py")


if __name__ == "__main__":
    fig_time_budget()
    fig_assert_rewrite()
    fig_fixture_scopes()
    fig_three_doors()
    fig_assert_lineage()
    fig_fixture_order()
    fig_conftest_chain()
    print("готово:", ", ".join(sorted(os.listdir(IMG))))


# ── 8. Розкладка struct rb: істина з C і два способи з нею розійтися ──────────
# Ідея: ctypes розкладає поля за правилами платформи, не питаючи бібліотеку.
# «_pack_ = 1» і «c_ulong замість c_size_t» дають дві різні мовчазні розбіжності;
# самоопис (rb_sizeof / rb_offset) перетворює мовчання на повідомлення.
def fig_ctypes_layout():
    W, H = 1250, 520
    f = []

    X0 = 210          # ліва межа смуг
    PX = 19.0         # пікселів на байт
    BH = 46           # висота смуги

    PAD_FILL = "#eceff3"

    def strip(y, caption, sub, fields, total, ok, ticks):
        """fields: (назва, зсув, розмір, заливка). total — sizeof."""
        # підпис ліворуч, у двох рядках, ЛІВОРУЧ від смуги з полем
        f.append(text(20, y + BH / 2 - 4, caption, size=13, bold=True, anchor="start"))
        f.append(text(20, y + BH / 2 + 14, sub, size=11, color=MUTED, anchor="start"))

        for name, off, sz, fill in fields:
            x, w = X0 + off * PX, sz * PX
            f.append(rect(x, y, w, BH, fill=fill, stroke=INK, sw=1.4, rx=3))
            if sz >= 4:
                f.append(text(x + w / 2, y + BH / 2 + 5,
                              name, size=fit_font(name, w - 8, 13), color=INK))
            else:
                f.append(text(x + w / 2, y + BH / 2 + 5, name, size=12, color=MUTED))

        # позначки зсувів під смугою
        for off in ticks:
            x = X0 + off * PX
            f.append(line(x, y + BH, x, y + BH + 7, color=MUTED, sw=1.0))
            f.append(text(x, y + BH + 21, str(off), size=11, color=MUTED))

        # sizeof — праворуч від смуги, на її рівні
        col = FIELD if ok else POS
        f.append(text(X0 + total * PX + 14, y + BH / 2 + 5,
                      "sizeof = %d" % total, size=13, bold=True,
                      color=col, anchor="start"))

    U8P, SZ, U8, PADC = "#dfe7f5", "#e8eef7", "#d4edda", PAD_FILL

    # A. Істина: те, що каже сам компілятор
    strip(78, "C, 64 біти", "як розклав компілятор",
          [("data", 0, 8, U8P), ("cap", 8, 8, SZ), ("head", 16, 8, SZ),
           ("tail", 24, 8, SZ), ("len", 32, 8, SZ),
           ("o", 40, 1, U8), ("v", 41, 1, U8), ("░░░░░░", 42, 6, PADC)],
          48, True, [0, 8, 16, 24, 32, 40])

    # B. _pack_ = 1: зсуви ті самі, розміру бракує
    strip(212, "ctypes, _pack_ = 1", "«щоб напевно»",
          [("data", 0, 8, U8P), ("cap", 8, 8, SZ), ("head", 16, 8, SZ),
           ("tail", 24, 8, SZ), ("len", 32, 8, SZ),
           ("o", 40, 1, U8), ("v", 41, 1, U8)],
          42, False, [0, 8, 16, 24, 32, 40])

    # C. c_ulong на Windows: з'їхало все, починаючи з другого поля
    strip(346, "ctypes, c_ulong", "на 64-бітних Windows",
          [("data", 0, 8, U8P), ("cap", 8, 4, SZ), ("head", 12, 4, SZ),
           ("tail", 16, 4, SZ), ("len", 20, 4, SZ),
           ("o", 24, 1, U8), ("v", 25, 1, U8), ("░░░░░░", 26, 6, PADC)],
          32, False, [0, 8, 12, 16, 20, 24])

    # легенда й висновок — окремим рядком, з полем від смуг
    f.append(text(20, 448, "o = owns_data · v = overrun · ░ = набивка",
                  size=12, color=MUTED, anchor="start"))
    body, bw, bh = textbox(W / 2, 486,
                           "check_layout() звіряє sizeof і зсув КОЖНОГО поля "
                           "з відповіддю самої бібліотеки — обидві розбіжності падають при імпорті",
                           size=13, pad=11, fill="#d4edda", stroke=FIELD, sw=1.8)
    f.append(body)

    render(out("ctypes-layout.svg"), W, H, *f,
           title="Одна структура — три уявлення про неї")


# ── 9. Що лишається від звіту, коли C падає ──────────────────────────────────
# Ідея: межа процесу не рятує бібліотеку від аварії — вона рятує звіт про неї.
# Ліворуч аварія забирає весь прогін; праворуч гине лише дитина, а батько
# перетворює її код завершення на звичайне падіння тесту з насінням.
def fig_crash_boundary():
    W, H = 1180, 600
    f = []

    def tests_row(x0, y, n, bad, w=17, gap=5):
        for i in range(n):
            x = x0 + i * (w + gap)
            if i == bad:
                f.append(rect(x, y, w, w, fill="#fdecea", stroke=POS, sw=2.0, rx=2))
                f.append(text(x + w / 2, y + w - 4, "✕", size=13, color=POS, bold=True))
            else:
                f.append(rect(x, y, w, w, fill="#d4edda", stroke=FIELD, sw=1.2, rx=2))

    # ── ЛІВОРУЧ: усе в одному процесі ────────────────────────────────────────
    f.append(text(285, 66, "усе в одному процесі", size=15, bold=True))

    f.append(rect(50, 88, 470, 116, fill="#f4f6f8", stroke=INK, sw=1.8, rx=8))
    f.append(text(285, 112, "процес pytest · обв'язка · libringbuf", size=13))
    tests_row(78, 138, 20, 9)
    f.append(text(285, 190, "аварія на 37-й перевірці", size=12, color=POS))

    f.append(arrow(285, 208, 285, 252, color=POS, sw=2.0))

    f.append(rect(120, 254, 330, 46, fill="#2b2b2b", stroke="#2b2b2b", sw=1.5, rx=5))
    f.append(text(285, 283, "Segmentation fault (core dumped)", size=14,
                  color="#ffffff", bold=True))

    body, bw, bh = textbox(285, 356,
                           "зникли разом із процесом:\n"
                           "звіт, статистика, ім'я вузла,\n"
                           "номер випадку, насіння генератора",
                           size=13, pad=12, fill="#fdecea", stroke=POS, sw=1.8)
    f.append(body)

    # ── ПРАВОРУЧ: ризикова частина в дитині ──────────────────────────────────
    f.append(text(890, 66, "ризикова частина — у дитині", size=15, bold=True))

    f.append(rect(655, 88, 470, 116, fill="#f4f6f8", stroke=INK, sw=1.8, rx=8))
    f.append(text(890, 112, "батько: процес pytest", size=13))
    tests_row(683, 138, 20, -1)
    f.append(text(890, 190, "жодна перевірка не постраждала", size=12, color=FIELD))

    # стрілка вниз: запуск дитини
    f.append(arrow(760, 208, 760, 274, color=NEG, sw=1.8))
    f.append(text(752, 244, "spawn", size=12, color=NEG, anchor="end"))

    # стрілка вгору: те, що батько дізнався
    f.append(arrow(1020, 274, 1020, 208, color=POS, sw=1.8))
    f.append(text(1028, 232, "exitcode = −11", size=12, color=POS, anchor="start"))
    f.append(text(1028, 250, "труба: seed = 20260801", size=12, color=MUTED, anchor="start"))

    f.append(rect(655, 276, 470, 84, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    f.append(text(890, 302, "дитина (spawn): кампанія випадкових операцій", size=13))
    f.append(text(890, 334, "✕ убито сигналом SIGSEGV", size=14, color=POS, bold=True))

    body, bw, bh = textbox(890, 424,
                           "батько перетворює це на звичайне падіння:\n"
                           "AssertionError з кодом завершення, останнім\n"
                           "сказаним і рядком «відтворити: seed=…»",
                           size=13, pad=12, fill="#d4edda", stroke=FIELD, sw=1.8)
    f.append(body)

    # межа між панелями
    f.append(line(587, 88, 587, 470, color=MUTED, sw=1.2, dash="6,5"))

    f.append(text(W / 2, 522, "межа процесу не рятує бібліотеку від аварії — "
                              "вона рятує все, чим аварію можна пояснити",
                  size=14, bold=True))
    f.append(text(W / 2, 552, "ціна — один запуск інтерпретатора на групу "
                              "ризикованих перевірок, а не на кожну окремо",
                  size=12, color=MUTED))

    render(out("crash-boundary.svg"), W, H, *f,
           title="Куди дівається звіт, коли падає C")


if __name__ == "__main__":
    fig_ctypes_layout()
    fig_crash_boundary()
    print("додано:", "ctypes-layout.svg, crash-boundary.svg")
