# -*- coding: utf-8 -*-
"""Фігури до теми «REST».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"
GRAY  = "#9aa0a6"


# ── 1. Ресурс і його представлення ────────────────────────────────────────────
# Ідея: ресурс — абстрактна річ; дротом іде завжди представлення (JSON/XML/HTML).
def fig_resource_representation():
    W, H = 800, 340
    f = [text(W / 2, 28, "Ресурс і його представлення", size=15, bold=True)]

    # центр — абстрактний ресурс
    rx, ry, rw, rh = 60, 130, 210, 96
    f.append(rect(rx, ry, rw, rh, fill="#eef2fb", stroke=NEG, sw=2, rx=12))
    f.append(text(rx + rw / 2, ry + 28, "РЕСУРС", size=11, color=NEG, bold=True))
    f.append(text(rx + rw / 2, ry + 52, "задача №42", size=14, color=INK, bold=True))
    f.append(text(rx + rw / 2, ry + 74, "абстрактна річ", size=10.5, color=MUTED, italic=True))

    # три представлення праворуч
    bx, bw, bh = 500, 268, 74
    ys = [58, 148, 238]
    reps = [
        ("JSON — для програм",       '{ "id": 42, "done": false }', FIELD),
        ("XML — для старих систем",   '<task id="42">…</task>',      AMBER),
        ("HTML — для людини",         '<li>Задача №42</li>',         POS),
    ]
    for (lbl, snip, col), y in zip(reps, ys):
        f.append(rect(bx, y, bw, bh, fill="#fbfbfb", stroke=col, sw=1.8, rx=9))
        f.append(text(bx + bw / 2, y + 26, lbl, size=11, color=col, bold=True))
        f.append(text(bx + bw / 2, y + 50, snip, size=11, color=INK))
        # стрілка від ресурсу до представлення
        f.append(arrow(rx + rw + 6, ry + rh / 2, bx - 6, y + bh / 2, color=GRAY, sw=1.6))

    f.append(text((rx + rw + bx) / 2, ry + rh / 2 - 14, "віддається як", size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "resource-representation.svg"), W, H, *f)


# ── 2. Однорідний інтерфейс: матриця «дієслово × ціль» ────────────────────────
# Ідея: п'ять фіксованих дієслів по-різному діють на колекцію й на елемент.
def fig_methods_matrix():
    W, H = 820, 392
    f = [text(W / 2, 28, "Однорідний інтерфейс: одні дієслова на будь-який ресурс", size=15, bold=True)]

    x0, wname = 40, 150
    x1, wcol = 190, 300
    x2 = x1 + wcol
    top = 52
    hh = 46          # висота заголовка
    rh = 52          # висота рядка

    # заголовки колонок
    f.append(rect(x0, top, wname, hh, fill="#f0f2f5", stroke=LINE, sw=1.3, rx=6))
    f.append(text(x0 + wname / 2, top + hh / 2 + 5, "дієслово", size=11.5, color=MUTED, bold=True))
    f.append(rect(x1, top, wcol, hh, fill="#f0f2f5", stroke=LINE, sw=1.3, rx=6))
    f.append(text(x1 + wcol / 2, top + hh / 2 + 5, "/tasks  (колекція)", size=12, color=INK, bold=True))
    f.append(rect(x2, top, wcol, hh, fill="#f0f2f5", stroke=LINE, sw=1.3, rx=6))
    f.append(text(x2 + wcol / 2, top + hh / 2 + 5, "/tasks/42  (елемент)", size=12, color=INK, bold=True))

    rows = [
        ("GET",    FIELD, "список задач",       "одна задача"),
        ("POST",   INK,   "створити нову",      "—"),
        ("PUT",    AMBER, "—",                  "замінити цілком"),
        ("PATCH",  AMBER, "—",                  "змінити частину"),
        ("DELETE", POS,   "—",                  "видалити"),
    ]
    for i, (m, col, c1, c2) in enumerate(rows):
        y = top + hh + i * rh
        # клітина дієслова
        f.append(rect(x0, y, wname, rh, fill="#fbfbfb", stroke=LINE, sw=1.1, rx=6))
        f.append(text(x0 + wname / 2, y + rh / 2 + 5, m, size=13, color=col, bold=True))
        # колекція
        f.append(rect(x1, y, wcol, rh, fill=BG, stroke=LINE, sw=1.1, rx=6))
        f.append(text(x1 + wcol / 2, y + rh / 2 + 5, c1,
                      size=12, color=(MUTED if c1 == "—" else INK)))
        # елемент
        f.append(rect(x2, y, wcol, rh, fill=BG, stroke=LINE, sw=1.1, rx=6))
        f.append(text(x2 + wcol / 2, y + rh / 2 + 5, c2,
                      size=12, color=(MUTED if c2 == "—" else INK)))

    f.append(text(W / 2, top + hh + 5 * rh + 24,
                  "адреса каже ЩО, дієслово каже ЯК — «—» означає «зазвичай не вживають»",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "methods-matrix.svg"), W, H, *f)


# ── 3. Становий проти безстанового: чому масштаб ──────────────────────────────
# Ідея: становий прив'язує клієнта до машини з його сесією; безстановий несе
# контекст у кожному запиті, тож запити вільно розкидаються по однакових машинах.
def fig_stateless():
    W, H = 860, 384
    f = [text(W / 2, 28, "Становий проти безстанового", size=15, bold=True)]

    # ── лівий бік: становий ──
    lx = 24
    f.append(rect(lx, 46, 396, 312, fill="#fffdfa", stroke=POS, sw=1.6, rx=12))
    f.append(text(lx + 198, 70, "становий — сесія прив'язана до машини", size=12, color=POS, bold=True))

    # клієнт
    cx = lx + 60
    f.append(rect(cx - 40, 168, 84, 52, fill="#fbfbfb", stroke=INK, sw=1.6, rx=8))
    f.append(text(cx + 2, 198, "клієнт", size=11.5, color=INK, bold=True))

    # сервер A (пам'ятає)
    ax = lx + 210
    f.append(rect(ax, 92, 168, 74, fill="#eef2fb", stroke=NEG, sw=1.7, rx=9))
    f.append(text(ax + 84, 118, "сервер A", size=12, color=NEG, bold=True))
    f.append(text(ax + 84, 140, "сесія клієнта", size=10.5, color=MUTED, italic=True))
    # сервер B (не пам'ятає)
    f.append(rect(ax, 222, 168, 66, fill="#f4f4f4", stroke=GRAY, sw=1.7, rx=9))
    f.append(text(ax + 84, 248, "сервер B", size=12, color=GRAY, bold=True))
    f.append(text(ax + 84, 270, "тебе не пам'ятає", size=10.5, color=GRAY, italic=True))

    # запит 1 → A (успіх)
    f.append(text(cx + 96, 120, "запит 1", size=10, color=INK))
    f.append(arrow(cx + 46, 168, ax - 6, 128, color=NEG, sw=1.9))
    # запит 2 → B (провал)
    f.append(text(cx + 96, 272, "запит 2", size=10, color=POS))
    f.append(arrow(cx + 46, 214, ax - 6, 250, color=POS, sw=1.9))
    f.append(text(ax - 18, 230, "✗", size=20, color=POS, bold=True))

    # ── правий бік: безстановий ──
    rx = 452
    f.append(rect(rx, 46, 384, 312, fill="#f6fbf7", stroke=FIELD, sw=1.6, rx=12))
    f.append(text(rx + 192, 70, "безстановий — контекст у кожному запиті", size=12, color=FIELD, bold=True))

    # клієнт із токеном
    cx2 = rx + 66
    f.append(rect(cx2 - 46, 168, 96, 58, fill="#fbfbfb", stroke=INK, sw=1.6, rx=8))
    f.append(text(cx2 + 4, 192, "клієнт", size=11.5, color=INK, bold=True))
    f.append(text(cx2 + 4, 212, "+ токен", size=10.5, color=FIELD, bold=True))

    # три однакові сервери
    sx = rx + 220
    for i, y in enumerate((92, 168, 244)):
        f.append(rect(sx, y, 150, 52, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=9))
        f.append(text(sx + 75, y + 31, "сервер %d" % (i + 1), size=11.5, color=INK, bold=True))
        f.append(arrow(cx2 + 50, 197, sx - 6, y + 26, color=FIELD, sw=1.7))
        f.append(text(sx + 130, y + 20, "✓", size=15, color=FIELD, bold=True))
    f.append(text(cx2 + 96, 120, "будь-який запит", size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "stateless.svg"), W, H, *f)


# ── 4. Сходи зрілості REST (модель Річардсона) ────────────────────────────────
# Ідея: кожен щабель бере від HTTP більше; майже всі реальні API — на рівні 2.
def fig_richardson():
    W, H = 820, 396
    f = [text(W / 2, 28, "Сходи зрілості REST", size=15, bold=True)]

    steps = [
        ("Рівень 0", "одна адреса, RPC поверх HTTP", GRAY),
        ("Рівень 1", "ресурси — багато адрес",       NEG),
        ("Рівень 2", "дієслова + коди стану",         FIELD),
        ("Рівень 3", "гіпермедіа (HATEOAS)",          AMBER),
    ]
    bw, bh = 196, 66
    x0, ybot = 44, 312
    dx, dy = 190, 70
    boxes = []
    for i, (lvl, desc, col) in enumerate(steps):
        x = x0 + i * dx
        y = ybot - i * dy
        boxes.append((x, y))
        # сходинка-підмостя під боксом (натяк на схід)
        if i > 0:
            px, py = boxes[i - 1]
            f.append(line(px + bw, py + bh / 2, x, py + bh / 2, color=GRAY, sw=1.3, dash="4,4"))
            f.append(line(x, py + bh / 2, x, y + bh, color=GRAY, sw=1.3, dash="4,4"))
        f.append(rect(x, y, bw, bh, fill="#fbfbfb", stroke=col, sw=1.9, rx=10))
        f.append(text(x + bw / 2, y + 27, lvl, size=13, color=col, bold=True))
        f.append(text(x + bw / 2, y + 49, desc, size=10.5, color=INK))

    # маркер «майже всі API — тут» до рівня 2
    lx, ly = boxes[2]
    f.append(text(lx + bw / 2, ly + bh + 40, "майже всі «REST API» — тут", size=11, color=FIELD, bold=True))
    f.append(arrow(lx + bw / 2, ly + bh + 26, lx + bw / 2, ly + bh + 4, color=FIELD, sw=1.8))

    render(os.path.join(IMG, "richardson.svg"), W, H, *f)


# ── 5. Розкладання адрес на обробники (для proj-розбору дизайну) ──────────────
# Ідея: дві адреси-шаблони покривають увесь CRUD; кожне дієслово → своя функція.
def fig_routing_tree():
    W, H = 900, 460
    f = [text(W / 2, 30, "Розкладання адрес на обробники", size=15, bold=True)]

    px, pw = 44, 208          # ліва колонка — шаблони адрес
    hx, hw = 474, 384         # права колонка — функції-обробники
    g1 = [
        ("GET → listTasks()  ·  200", FIELD),
        ("POST → createTask()  ·  201 + Location", INK),
    ]
    g2 = [
        ("GET → getTask(id)  ·  200 / 404", FIELD),
        ("PUT → replaceTask(id)  ·  200 / 404", AMBER),
        ("PATCH → updateTask(id)  ·  200 / 404", AMBER),
        ("DELETE → deleteTask(id)  ·  204 / 404", POS),
    ]
    hh, gap = 46, 16
    y = 72
    centers1 = []
    for label, col in g1:
        f.append(fitbox(hx, y, hw, hh, label, size=12, color=INK, stroke=col, sw=1.7, fill="#fbfbfb"))
        centers1.append(y + hh / 2)
        y += hh + gap
    y += 30
    centers2 = []
    for label, col in g2:
        f.append(fitbox(hx, y, hw, hh, label, size=12, color=INK, stroke=col, sw=1.7, fill="#fbfbfb"))
        centers2.append(y + hh / 2)
        y += hh + gap

    c1 = sum(centers1) / len(centers1)
    f.append(fitbox(px, c1 - 30, pw, 60, "/tasks\n(колекція)", size=14, color=NEG, bold=True, stroke=NEG, sw=1.9, fill="#eef2fb"))
    for cy in centers1:
        f.append(arrow(px + pw + 6, c1, hx - 6, cy, color=GRAY, sw=1.6))

    c2 = sum(centers2) / len(centers2)
    f.append(fitbox(px, c2 - 30, pw, 60, "/tasks/:id\n(елемент)", size=14, color=NEG, bold=True, stroke=NEG, sw=1.9, fill="#eef2fb"))
    for cy in centers2:
        f.append(arrow(px + pw + 6, c2, hx - 6, cy, color=GRAY, sw=1.6))
    f.append(text(px + pw / 2, c2 + 48, "«:id» — параметр шляху,", size=10.5, color=MUTED, italic=True))
    f.append(text(px + pw / 2, c2 + 64, "виймається з адреси", size=10.5, color=MUTED, italic=True))

    f.append(text(W / 2, H - 16, "дві адреси — шість обробників; та сама адреса під різними дієсловами робить різне",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "routing-tree.svg"), W, H, *f)


# ── 6. Конвеєр обробника: де народжується код стану ───────────────────────────
# Ідея: кожна стадія обробника має свій вихід-помилку з власним кодом стану.
def fig_handler_pipeline():
    W, H = 860, 588
    f = [text(W / 2, 30, "Конвеєр обробника: де народжується код стану", size=15, bold=True)]

    cx, cw = 214, 340         # центральна колонка стадій
    sx, sw_ = 636, 196        # права колонка кодів-виходів
    stages = [
        ("Розібрати тіло й параметри", "400 — ламане тіло"),
        ("Перевірити ввід за схемою",  "400 / 422 — невалідний ввід"),
        ("Контекст із запиту (токен)", "401 — немає доступу"),
        ("Знайти ресурс за id",        "404 — немає такого"),
        ("Перевірити конфлікт / версію", "409 — конфлікт стану"),
        ("Змінити стан",                None),
        ("Віддати представлення",       None),
    ]
    f.append(text(sx + sw_ / 2, 58, "вихід із кодом-помилкою", size=10, color=MUTED, italic=True))
    hh, gap = 44, 16
    y = 74
    prev_top = None
    for name, fail in stages:
        cyc = y + hh / 2
        if prev_top is not None:
            f.append(arrow(cx + cw / 2, prev_top + hh, cx + cw / 2, y, color=INK, sw=1.8))
        f.append(fitbox(cx, y, cw, hh, name, size=12.5, color=INK, stroke=NEG, sw=1.7, fill="#eef2fb"))
        if fail is not None:
            f.append(arrow(cx + cw + 6, cyc, sx - 6, cyc, color=POS, sw=1.5))
            f.append(fitbox(sx, cyc - 18, sw_, 36, fail, size=10, color=POS, stroke=POS, sw=1.4, fill="#fdecea"))
        prev_top = y
        y += hh + gap

    f.append(arrow(cx + cw / 2, prev_top + hh, cx + cw / 2, y + 4, color=FIELD, sw=1.9))
    f.append(fitbox(cx - 44, y + 4, cw + 88, 52,
                    "200 OK · 201 Created (+Location) · 204 No Content",
                    size=12, color=FIELD, bold=True, stroke=FIELD, sw=1.9, fill="#f6fbf7"))
    render(os.path.join(IMG, "handler-pipeline.svg"), W, H, *f)


# ── 7. PUT замінює цілком проти PATCH, що зшиває частину ───────────────────────
# Ідея: PUT кладе повне представлення; PATCH зливає названі поля з наявним.
def fig_put_vs_patch():
    W, H = 900, 440
    f = [text(W / 2, 30, "PUT замінює цілком · PATCH зшиває частину", size=15, bold=True)]

    # збережений ресурс — згори по центру
    sbx, sby, sbw, sbh = 350, 50, 200, 84
    f.append(fitbox(sbx, sby, sbw, sbh,
                    "збережено:\ntitle: Молоко\ndone: false\npriority: low",
                    size=11.5, color=INK, stroke=MUTED, sw=1.6, fill="#f4f6f8"))
    f.append(arrow(sbx + 10, sby + sbh, 210, 166, color=GRAY, sw=1.4))
    f.append(arrow(sbx + sbw - 10, sby + sbh, 690, 166, color=GRAY, sw=1.4))

    # ── лівий стовпець: PUT (заголовок і тіло — один блок, щоб лінія зверху
    #    впиралась у край рамки, а не перетинала окремий підпис) ──
    lx = 60
    f.append(fitbox(lx, 166, 300, 92,
                    "PUT /tasks/42 — повне представлення\n \nтіло — усі поля:\ntitle: Молоко · done: TRUE · priority: low",
                    size=10.5, color=INK, stroke=AMBER, sw=1.6, fill="#fffdf5"))
    f.append(arrow(lx + 150, 258, lx + 150, 292, color=AMBER, sw=1.8))
    f.append(fitbox(lx, 296, 300, 60,
                    "увесь ресурс замінено:\ntitle: Молоко · done: TRUE · priority: low",
                    size=10.5, color=INK, stroke=FIELD, sw=1.6, fill="#f6fbf7"))
    f.append(text(lx + 150, 382, "пропустиш поле — воно скинеться; тому потрібні всі", size=10, color=MUTED, italic=True))
    f.append(text(lx + 150, 400, "повтори запит — той самий стан (ідемпотентно)", size=10, color=MUTED, italic=True))

    # ── правий стовпець: PATCH ──
    rx = 540
    f.append(fitbox(rx, 166, 300, 92,
                    "PATCH /tasks/42 — лише зміна\n \nтіло — одне поле:\ndone: TRUE",
                    size=10.5, color=INK, stroke=AMBER, sw=1.6, fill="#fffdf5"))
    f.append(arrow(rx + 150, 258, rx + 150, 292, color=AMBER, sw=1.8))
    f.append(fitbox(rx, 296, 300, 60,
                    "злито з наявним:\ntitle: Молоко · done: TRUE · priority: low",
                    size=10.5, color=INK, stroke=FIELD, sw=1.6, fill="#f6fbf7"))
    f.append(text(rx + 150, 382, "неназвані поля лишаються як були", size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "put-vs-patch.svg"), W, H, *f)


# ── 8. Виведення REST із порожнього стилю (для вставки hist-rest-fielding) ─────
# Ідея: Філдінг не подає REST готовим — він додає обмеження по одному до
# «порожнього стилю», і кожне заробляє місце. Останнє (код на вимогу) — опційне.
def fig_rest_derivation():
    W, H = 900, 566
    f = [text(W / 2, 30, "Виведення REST: обмеження додають по одному", size=15, bold=True)]

    rows = [
        ("Порожній стиль",          "жодних обмежень — дозволено все",              GRAY,  "#f4f4f4", False),
        ("+ Клієнт-сервер",         "розділити турботи: інтерфейс окремо від даних", NEG,  "#fbfbfb", False),
        ("+ Безстановість",         "рости, додаючи однакові машини",               NEG,   "#fbfbfb", False),
        ("+ Кеш",                   "не робити повторну роботу двічі",              FIELD, "#f6fbf7", False),
        ("+ Однорідний інтерфейс",  "загальність в обмін на ефективність",          POS,   "#fdecea", False),
        ("+ Шаруватість",           "вставні проміжні вузли непомітні",             NEG,   "#fbfbfb", False),
        ("+ Код на вимогу",         "необов'язковий — єдиний зі шести",             AMBER, "#fffdf5", True),
    ]

    bw, bh = 640, 52
    x = (W - bw) / 2
    y0 = 58
    pitch = bh + 22
    for i, (name, eff, col, fill, dashed) in enumerate(rows):
        y = y0 + i * pitch
        if dashed:                       # пунктирна рамка для опційного обмеження
            f.append(rect(x, y, bw, bh, fill=fill, stroke=BG, sw=1, rx=10))
            for (a, b, c, d) in ((x, y, x + bw, y), (x + bw, y, x + bw, y + bh),
                                  (x + bw, y + bh, x, y + bh), (x, y + bh, x, y)):
                f.append(line(a, b, c, d, color=col, sw=1.9, dash="6,4"))
        else:
            f.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.9, rx=10))
        f.append(text(W / 2, y + 21, name, size=13, color=col, bold=True))
        f.append(text(W / 2, y + 40, eff, size=11.5, color=(MUTED if i == 0 else INK)))
        if i < len(rows) - 1:            # стрілка-місток до наступного щабля
            f.append(arrow(W / 2, y + bh + 2, W / 2, y + bh + 18, color=GRAY, sw=1.7))

    render(os.path.join(IMG, "rest-derivation.svg"), W, H, *f)


# ── 9. Часова вісь: як народилося ім'я REST і як воно відклеїлося ──────────────
# Ідея: дві історії в одній — Філдінг називає форму вебу (1994–2000), а галузь
# позичає назву проти SOAP (2007–08), лишивши гіпермедіа за дверима.
def fig_rest_timeline():
    W, H = 1000, 312
    f = [text(W / 2, 30, "Ім'я REST: як народилося і як відклеїлося від суті", size=15, bold=True)]

    axis_y = 156
    f.append(line(56, axis_y, 944, axis_y, color=INK, sw=2))

    nodes = [
        (130, "1994–99", "Філдінг пише HTTP/1.1 та URI;\nREST веде їхній дизайн",    NEG,   True),
        (320, "2000",    "Дисертація — REST дістає ім'я\n(гіпермедіа обов'язкова)",  INK,   False),
        (510, "2007",    "Втома від SOAP; «RESTful Web\nServices» — назву позичено", AMBER, True),
        (700, "2008",    "Модель Річардсона:\nгалузь осіла на рівні 2",              FIELD, False),
        (890, "2008",    "Філдінг: «це не REST» —\nHATEOAS проігноровано",           POS,   True),
    ]
    boxw, boxh = 208, 54
    for cx, year, desc, col, above in nodes:
        f.append(circle(cx, axis_y, 8, fill=col, stroke=BG, sw=2))
        if above:
            by = axis_y - 26 - boxh
            f.append(line(cx, axis_y - 8, cx, by + boxh, color=col, sw=1.4))
            f.append(text(cx, axis_y + 22, year, size=12, color=col, bold=True))
        else:
            by = axis_y + 26
            f.append(line(cx, axis_y + 8, cx, by, color=col, sw=1.4))
            f.append(text(cx, axis_y - 14, year, size=12, color=col, bold=True))
        f.append(fitbox(cx - boxw / 2, by, boxw, boxh, desc,
                        size=11, fill="#fbfbfb", stroke=col, sw=1.6, rx=9, color=INK))

    render(os.path.join(IMG, "rest-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_resource_representation()
    fig_methods_matrix()
    fig_stateless()
    fig_richardson()
    fig_routing_tree()
    fig_handler_pipeline()
    fig_put_vs_patch()
    fig_rest_derivation()
    fig_rest_timeline()
    print("OK: 9 фігур у", IMG)
