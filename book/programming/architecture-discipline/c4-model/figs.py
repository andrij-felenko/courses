# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SYS = "#eaf0fd"   # заливка нашої системи
EXT = "#f4f6f8"   # заливка зовнішніх систем
PER = "#eef7ef"   # заливка людини/актора
DB  = "#fef6e9"   # заливка сховищ


def box(cx, cy, w, h, title, sub, fill, stroke, ts=13.5, ss=10.5, rx=8):
    """Коробка з назвою й дрібним підписом-технологією під нею."""
    x, y = cx - w / 2, cy - h / 2
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.7, rx=rx)
    if sub:
        out += text(cx, cy - 3, title, size=ts, color=INK, bold=True)
        out += text(cx, cy + ss + 5, sub, size=ss, color=MUTED, italic=True)
    else:
        out += text(cx, cy + ts * 0.35, title, size=ts, color=INK, bold=True)
    return out


def person(cx, cy, label, w=118, h=64):
    """Актор: кружечок-голова над коробкою-підписом."""
    out = circle(cx, cy - h / 2 - 12, 13, fill=PER, stroke=FIELD, sw=1.7)
    out += box(cx, cy + 4, w, h, label, "", PER, FIELD, ts=12.5, rx=10)
    return out


def edge(x1, y1, x2, y2, label, lx=None, ly=None, size=10, color=MUTED):
    """Стрілка + напис поруч (координати напису задаємо явно, щоб не накладати)."""
    out = arrow(x1, y1, x2, y2, color=INK, sw=1.8)
    if label:
        out += text(lx, ly, label, size=size, color=color, italic=True)
    return out


# ── 1. Контекст: одна коробка-система, люди й чужі системи довкола ────────────
def fig_context():
    W, H = 820, 440
    p = []
    p.append(text(W / 2, 30, "Рівень 1 — Контекст: система і її світ", size=16, bold=True))
    p.append(text(W / 2, 50, "одна коробка — наша система; довкола — люди й чужі системи", size=11, color=MUTED, italic=True))

    # наша система — центр
    sx, sy = W / 2, 250
    p.append(box(sx, sy, 210, 84, "Інтернет-магазин", "наша система", SYS, NEG, ts=15, ss=11))

    # покупець — ліворуч зверху
    px, py = 150, 170
    p.append(person(px, py, "Покупець"))
    p.append(edge(px + 30, py + 20, sx - 112, sy - 18, "переглядає й купує [HTTPS]",
                  lx=300, ly=175, size=10))

    # платіжний шлюз — праворуч зверху
    p.append(box(670, 150, 200, 66, "Платіжний шлюз", "зовнішня система", EXT, MUTED, ts=13, ss=10))
    p.append(edge(sx + 112, sy - 22, 670 - 40, 150 + 40, "проводить оплату [API]",
                  lx=560, ly=205, size=10))

    # пошта — праворуч знизу
    p.append(box(670, 330, 200, 66, "Пошта (email)", "зовнішня система", EXT, MUTED, ts=13, ss=10))
    p.append(edge(sx + 112, sy + 14, 670 - 40, 330 - 26, "шле листи [SMTP]",
                  lx=568, ly=300, size=10))

    # сервіс доставки — знизу
    p.append(box(230, 360, 200, 66, "Сервіс доставки", "зовнішня система", EXT, MUTED, ts=13, ss=10))
    p.append(edge(sx - 70, sy + 42, 230 + 40, 360 - 30, "замовляє відправлення",
                  lx=250, ly=318, size=10))

    # підсумок
    p.append(text(W / 2, 425, "Нутрощів системи тут НЕ видно — діаграма окреслює межу, а не будову.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "context.svg"), W, H, *p)


# ── 2. Контейнер: усередині системи — застосунки й сховища ────────────────────
def fig_container():
    W, H = 820, 500
    p = []
    p.append(text(W / 2, 30, "Рівень 2 — Контейнер: з чого зроблено систему", size=16, bold=True))
    p.append(text(W / 2, 50, "контейнер = те, що запускають окремо (сервіс, база, черга), НЕ Docker", size=11, color=MUTED, italic=True))

    # межа системи — пунктирна рамка
    bx, by, bw, bh = 190, 96, 440, 360
    p.append(rect(bx, by, bw, bh, fill="#fbfcff", stroke=NEG, sw=1.6, rx=14))
    p.append(text(bx + 14, by + 22, "межа: Інтернет-магазин", size=11, color=NEG, bold=True, anchor="start"))

    cx = bx + bw / 2

    # веб-застосунок
    web_y = 165
    p.append(box(cx, web_y, 250, 60, "Веб-застосунок", "React, у браузері", SYS, NEG, ts=13.5, ss=10))
    # API
    api_y = 275
    p.append(box(cx, api_y, 250, 60, "API-сервіс", "Java / Spring", SYS, NEG, ts=13.5, ss=10))
    # база
    db_y = 390
    p.append(box(cx - 105, db_y, 190, 60, "База даних", "PostgreSQL", DB, "#8a6508", ts=13, ss=10))
    # черга
    p.append(box(cx + 115, db_y, 170, 60, "Черга задач", "RabbitMQ", DB, "#8a6508", ts=13, ss=10))

    # зв'язки всередині (стрілки збоку від коробок, написи ліворуч/праворуч від лінії)
    p.append(arrow(cx, web_y + 30, cx, api_y - 30, color=INK, sw=1.8))
    p.append(text(cx + 12, (web_y + api_y) / 2 + 4, "запити [HTTPS/JSON]", size=10, color=MUTED, italic=True, anchor="start"))

    p.append(arrow(cx - 70, api_y + 30, cx - 105, db_y - 30, color=INK, sw=1.8))
    p.append(text(cx - 150, (api_y + db_y) / 2 + 4, "читає/пише [SQL]", size=10, color=MUTED, italic=True, anchor="end"))

    p.append(arrow(cx + 70, api_y + 30, cx + 115, db_y - 30, color=INK, sw=1.8))
    p.append(text(cx + 205, (api_y + db_y) / 2 + 4, "кладе задачі", size=10, color=MUTED, italic=True, anchor="start"))

    # покупець ззовні ліворуч
    p.append(person(90, 165, "Покупець"))
    p.append(arrow(90 + 34, 165, bx - 2, web_y, color=INK, sw=1.8))
    p.append(text(90, 118, "відкриває", size=10, color=MUTED, italic=True))

    # платіжний шлюз ззовні праворуч
    p.append(box(730, 275, 150, 58, "Платіжний", "шлюз (external)", EXT, MUTED, ts=12.5, ss=9.5))
    p.append(arrow(cx + 125, api_y, 730 - 75, 275, color=INK, sw=1.8))
    p.append(text(700, 250, "оплата [API]", size=10, color=MUTED, italic=True))

    p.append(text(W / 2, 484, "Видно технології (в дужках) і протоколи (на стрілках) — рівно щоб зорієнтуватися.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "container.svg"), W, H, *p)


# ── 3. Чотири рівні як матрьошка + масштаб + читач ────────────────────────────
def fig_levels():
    W, H = 860, 470
    p = []
    p.append(text(W / 2, 30, "Чотири рівні C4 — зум в ОДНУ систему, не чотири системи", size=16, bold=True))

    # вкладені прямокутники
    levels = [
        ("Контекст",  "континент",       "замовник, новий у команді",  NEG,  SYS),
        ("Контейнер", "країни, траси",    "будь-який розробник",        FIELD, "#eaf6ef"),
        ("Компонент", "вулиці",           "розробник цього сервіса",    "#8a6508", DB),
        ("Код",       "окремі будинки",   "рідко; краще автогенерація", MUTED, FILL),
    ]
    # геометрія матрьошки — зліва
    ox, oy = 60, 70
    ow, oh = 360, 360
    step = 40
    for i, (name, scale, who, sc, fc) in enumerate(levels):
        x = ox + i * step
        y = oy + i * step
        w = ow - 2 * i * step
        h = oh - 2 * i * step
        p.append(rect(x, y, w, h, fill=fc, stroke=sc, sw=1.9, rx=10))
        # назва рівня — у верхній смузі кожної рамки
        p.append(text(x + w / 2, y + 22, name, size=13.5, color=sc, bold=True))

    # стрілка «зум» збоку від матрьошки
    p.append(arrow(ox + ow + 22, oy + 20, ox + ow + 22, oy + oh - 20, color=INK, sw=2))
    p.append(text(ox + ow + 34, oy + oh / 2 - 8, "зум усередину", size=10.5, color=INK, bold=True, anchor="start"))
    p.append(text(ox + ow + 34, oy + oh / 2 + 8, "ОДНІЄЇ коробки", size=10.5, color=INK, anchor="start"))
    p.append(text(ox + ow + 34, oy + oh / 2 + 24, "рівня вище", size=10.5, color=MUTED, italic=True, anchor="start"))

    # таблиця праворуч: масштаб карти + хто читає
    tx = 560
    ty = 90
    rh = 78
    cw1, cw2 = 130, 168
    # шапка
    p.append(rect(tx, ty, cw1, 34, fill="#eef1f4", stroke=MUTED, sw=1.3, rx=0))
    p.append(text(tx + cw1 / 2, ty + 22, "масштаб карти", size=11, color=INK, bold=True))
    p.append(rect(tx + cw1, ty, cw2, 34, fill="#eef1f4", stroke=MUTED, sw=1.3, rx=0))
    p.append(text(tx + cw1 + cw2 / 2, ty + 22, "хто це читає", size=11, color=INK, bold=True))
    for i, (name, scale, who, sc, fc) in enumerate(levels):
        ry = ty + 34 + i * rh
        p.append(rect(tx, ry, cw1, rh, fill=fc, stroke=sc, sw=1.4, rx=0))
        p.append(text(tx + cw1 / 2, ry + rh / 2 - 8, name, size=12, color=sc, bold=True))
        p.append(text(tx + cw1 / 2, ry + rh / 2 + 12, scale, size=10, color=MUTED, italic=True))
        p.append(rect(tx + cw1, ry, cw2, rh, fill=BG, stroke="#d7dbe0", sw=1.2, rx=0))
        p.append(text(tx + cw1 + cw2 / 2, ry + rh / 2 + 4, who, size=10.5, color=INK))

    p.append(text(W / 2, 455, "Верхні дві карти малюють майже завжди; нижні дві — вибірково.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "levels.svg"), W, H, *p)


# ── 4. Хронологія народження C4 (для вставки hist-) ───────────────────────────
def fig_timeline():
    W, H = 960, 470
    p = []
    p.append(text(W / 2, 30, "Як народилася C4 — від коренів до відкритого стандарту", size=16, bold=True))
    p.append(text(W / 2, 50, "коріння зростало роками; назви й абревіатура усталилися пізніше", size=11, color=MUTED, italic=True))

    # горизонтальна вісь часу
    ax0, ax1 = 90, W - 60
    ay = 250
    p.append(line(ax0, ay, ax1, ay, color=INK, sw=2.2))
    p.append(arrow(ax1 - 1, ay, ax1 + 1, ay, color=INK, sw=2.2))

    # віхи: (частка вздовж осі 0..1, рік, заголовок, рядки-опис, вгору?)
    marks = [
        (0.00, "2006–2009", "Коріння",       ["тренінги з архітектури,", "проектні вправи на дошці"], True),
        (0.30, "початок 2010", "Назви",       ["усталюються context,", "containers, components,", "classes"], False),
        (0.52, "початок 2011", "Абревіатура", ["уперше вжито", "слово «C4»"], True),
        (0.72, "2015–2016", "Рівень 4",       ["«classes» →", "«code»"], False),
        (0.98, "2018", "Відкрито",            ["сайт (CC-ліцензія)", "+ стаття на InfoQ"], True),
    ]
    for frac, year, head, body, up in marks:
        x = ax0 + (ax1 - ax0) * frac
        # крапка на осі
        p.append(circle(x, ay, 7, fill=SYS, stroke=NEG, sw=2.4))
        # рік — біля осі, з протилежного боку від картки
        yr_y = ay + 26 if up else ay - 16
        p.append(text(x, yr_y, year, size=11.5, color=NEG, bold=True))
        # картка з описом — угору або вниз
        lines = [head] + body
        tw = max(text_width(ln, 11.5, ln == head) for ln in lines)
        bw = tw + 22
        bh = len(lines) * 17 + 16
        if up:
            by = ay - 44 - bh
            p.append(line(x, ay - 8, x, by + bh, color=MUTED, sw=1.2, dash="3,3"))
        else:
            by = ay + 44
            p.append(line(x, ay + 8, x, by, color=MUTED, sw=1.2, dash="3,3"))
        bx = min(max(x - bw / 2, 6), W - bw - 6)
        p.append(rect(bx, by, bw, bh, fill="#fbfcff", stroke=NEG, sw=1.5, rx=8))
        p.append(text(bx + bw / 2, by + 19, head, size=12.5, color=INK, bold=True))
        for i, ln in enumerate(body):
            p.append(text(bx + bw / 2, by + 19 + (i + 1) * 17, ln, size=10.5, color=MUTED, italic=True))

    p.append(text(W / 2, H - 20, "Не одна дата винаходу, а повільне визрівання: спершу практика, потім назви, потім ім'я, потім відкритий стандарт.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "origin-timeline.svg"), W, H, *p)


# ── 5. Метамодель: п'ять абстракцій і суворе вкладення ────────────────────────
def fig_metamodel():
    W, H = 920, 600
    p = []
    p.append(text(W / 2, 30, "Метамодель C4 — п'ять абстракцій і суворе вкладення", size=16, bold=True))
    p.append(text(W / 2, 52, "діаграми — це в'ю; сама модель — оцей маленький словник понять", size=11, color=MUTED, italic=True))

    # актор ліворуч
    px, py = 120, 150
    p.append(person(px, py, "Людина"))

    # центральний стовпчик вкладення
    cx = 470
    boxes = [
        (150, "Програмна система", "наша або зовнішня", SYS, NEG),
        (268, "Контейнер",         "застосунок або сховище", SYS, NEG),
        (386, "Компонент",         "група логіки за інтерфейсом", SYS, NEG),
        (504, "Елемент коду",      "клас · функція · модуль", FILL, MUTED),
    ]
    for cy, title, sub, fc, sc in boxes:
        p.append(box(cx, cy, 300, 64, title, sub, fc, sc, ts=14, ss=10.5))

    # "містить (1..*)" між сусідніми боксами
    for cy0, cy1 in [(150, 268), (268, 386), (386, 504)]:
        my = (cy0 + cy1) / 2
        p.append(arrow(cx, cy0 + 32, cx, cy1 - 32, color=INK, sw=1.8))
        p.append(text(cx + 16, my + 4, "містить (1..*)", size=10.5, color=MUTED, italic=True, anchor="start"))

    # людина користується системою
    p.append(arrow(px + 59, py - 4, cx - 152, 140, color=INK, sw=1.8))
    p.append(text(258, 122, "користується", size=10.5, color=MUTED, italic=True))

    # права колонка — рівень і як часто малюють
    notes = [
        (150, "Рівень 1 · Контекст", "малюють завжди"),
        (268, "Рівень 2 · Контейнер", "малюють завжди"),
        (386, "Рівень 3 · Компонент", "вибірково"),
        (504, "Рівень 4 · Код", "рідко · автогенерація"),
    ]
    for cy, a, b in notes:
        p.append(text(752, cy - 5, a, size=11, color=NEG, bold=True))
        p.append(text(752, cy + 13, b, size=10, color=MUTED, italic=True))

    p.append(text(W / 2, 568, "Кожен рівень — це «зазирнути всередину» ОДНІЄЇ коробки рівня вище. Порядок вкладення незмінний; вигляд — ні.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "metamodel.svg"), W, H, *p)


# ── 6. Одна модель — багато в'ю (проекції) ────────────────────────────────────
def fig_views():
    W, H = 960, 600
    p = []
    p.append(text(W / 2, 30, "Одна модель — багато в'ю: діаграма є проекцією", size=16, bold=True))
    p.append(text(W / 2, 52, "вибираєш scope (що в центрі) і рівень — дістаєш готову діаграму", size=11, color=MUTED, italic=True))

    # центр — єдина модель
    mx, my, mw, mh = 480, 300, 300, 116
    p.append(rect(mx - mw / 2, my - mh / 2, mw, mh, fill=SYS, stroke=NEG, sw=2.2, rx=12))
    p.append(text(mx, my - 26, "ЄДИНА МОДЕЛЬ", size=15, color=INK, bold=True))
    p.append(text(mx, my - 4, "люди · системи · контейнери", size=10.5, color=MUTED, italic=True))
    p.append(text(mx, my + 14, "компоненти · зв'язки", size=10.5, color=MUTED, italic=True))
    p.append(text(mx, my + 36, "(один граф понять)", size=10, color=NEG, italic=True))

    # картки-в'ю навколо
    cards = [
        (195, 112, "Контекст", "система · рівень 1"),
        (765, 112, "Контейнер", "система · рівень 2"),
        (150, 300, "Компонент: API", "1 контейнер · рів. 3"),
        (810, 300, "Компонент: Веб", "1 контейнер · рів. 3"),
        (215, 496, "Динамічна", "сценарій у русі"),
        (745, 496, "Розгортання", "на яке залізо"),
    ]
    for cxx, cyy, t, s in cards:
        p.append(box(cxx, cyy, 214, 62, t, s, FILL, MUTED, ts=12.5, ss=10))

    # стрілки-проекції з країв моделі до карток (кінець — трохи не доходить до картки)
    edges = [
        (400, 247, 268, 138),   # top-left
        (560, 247, 692, 138),   # top-right
        (330, 292, 263, 300),   # mid-left
        (630, 292, 697, 300),   # mid-right
        (400, 355, 285, 468),   # bottom-left
        (560, 355, 672, 468),   # bottom-right
    ]
    for x1, y1, x2, y2 in edges:
        p.append(arrow(x1, y1, x2, y2, color=INK, sw=1.7))

    p.append(text(W / 2, 578, "Стрілка — проекція. Правиш модель раз — усі в'ю оновлюються разом, бо це один граф, а не сім окремих малюнків.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "views.svg"), W, H, *p)


# ── 7. Анатомія елемента й зв'язку (рекомендована нотація) ────────────────────
def fig_notation():
    W, H = 920, 560
    p = []
    p.append(text(W / 2, 30, "Анатомія коробки й стрілки — з чого читається сама діаграма", size=16, bold=True))
    p.append(text(W / 2, 52, "нотація вільна, але кожна частина підпису має свою роль", size=11, color=MUTED, italic=True))

    # великий елемент ліворуч
    ex, ey, ew, eh = 100, 165, 300, 152
    p.append(rect(ex, ey, ew, eh, fill=SYS, stroke=NEG, sw=2, rx=10))
    ecx = ex + ew / 2
    rows = [
        (205, "API-сервіс", 15, INK, True, False),
        (235, "[Контейнер]", 11, NEG, True, False),
        (262, "Java · Spring Boot", 11, MUTED, False, True),
        (292, "надає REST-API замовлень", 10.5, MUTED, False, True),
    ]
    for ry, s, sz, col, bd, it in rows:
        p.append(text(ecx, ry, s, size=sz, color=col, bold=bd, italic=it))

    # виноски праворуч
    callouts = [
        (205, "1 · назва — що це"),
        (235, "2 · тип елемента (людина / система / контейнер / компонент)"),
        (262, "3 · технологія у дужках"),
        (292, "4 · опис — одне речення"),
    ]
    for ry, s in callouts:
        p.append(line(ex + ew, ry, ex + ew + 58, ry, color=MUTED, sw=1.2))
        p.append(text(ex + ew + 64, ry + 4, s, size=10.5, color=INK, anchor="start"))

    # зв'язок унизу
    ay = 442
    p.append(box(210, ay, 180, 54, "Веб-застосунок", "", SYS, NEG, ts=12.5, rx=8))
    p.append(box(600, ay, 180, 54, "API-сервіс", "", SYS, NEG, ts=12.5, rx=8))
    p.append(arrow(302, ay, 508, ay, color=INK, sw=1.9))
    p.append(text(405, ay - 16, "надсилає запити [HTTPS/JSON]", size=10.5, color=MUTED, italic=True))
    p.append(text(405, ay + 30, "напрям стрілки = хто ініціює", size=10, color=INK))
    p.append(text(405, ay + 48, "підпис = дія + протокол", size=10, color=MUTED, italic=True))

    p.append(text(W / 2, 535, "Коробка сама каже, що вона; стрілка — що передає й куди. Легенда обов'язкова, бо кольори в різних авторів різні.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "notation.svg"), W, H, *p)


# ── 8. Розгортання: контейнер → N інстансів у вкладених вузлах ─────────────────
def fig_deployment():
    W, H = 980, 560
    p = []
    p.append(text(W / 2, 30, "Розгортання: один контейнер стає багатьма копіями на залізі", size=16, bold=True))
    p.append(text(W / 2, 52, "статична модель каже ЩО; в'ю розгортання — ДЕ і в СКІЛЬКОХ копіях", size=11, color=MUTED, italic=True))

    # контейнер зі статичної моделі — ліворуч
    p.append(box(150, 250, 190, 70, "API-сервіс", "[Контейнер]", SYS, NEG, ts=13.5, ss=10.5))
    p.append(arrow(247, 250, 374, 250, color=INK, sw=1.9))
    p.append(text(305, 234, "розгортається як", size=10.5, color=MUTED, italic=True))

    # зовнішній вузол — регіон
    p.append(rect(380, 118, 560, 324, fill="#fbfcff", stroke=NEG, sw=1.6, rx=14))
    p.append(text(396, 140, "Регіон: eu-central-1  [вузол розгортання]", size=11, color=NEG, bold=True, anchor="start"))

    # балансувальник — інфравузол
    p.append(box(660, 186, 250, 48, "Балансувальник", "інфравузол", FILL, MUTED, ts=12.5, ss=9.5))

    # два вузли (VM/pod), у кожному — інстанс
    for nx, inst in [(410, "інстанс 1"), (690, "інстанс 2")]:
        p.append(rect(nx, 250, 230, 172, fill=FILL, stroke=MUTED, sw=1.5, rx=10))
        p.append(text(nx + 14, 272, "Вузол (VM/pod)", size=10.5, color=INK, bold=True, anchor="start"))
        p.append(box(nx + 115, 344, 180, 58, "API-сервіс", inst, SYS, NEG, ts=12.5, ss=9.5))
        p.append(arrow(660, 210, nx + 115, 250, color=INK, sw=1.6))

    p.append(text(660, 462, "копій стільки, скільки треба — це й є автомасштабування", size=10.5, color=INK, bold=True))
    p.append(text(W / 2, 536, "Один контейнер моделі → N копій-інстансів у вкладених вузлах. Саме тут доречні справжні Docker і Kubernetes — не на рівні 2.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "deployment.svg"), W, H, *p)


# ── 9. C4 як код: одна модель годує і рендер, і перевірку (для вставки proj-) ──
def fig_model_pipeline():
    W, H = 1000, 545
    p = []
    p.append(text(W / 2, 30, "C4 як код: одна модель — і рендер в'ю, і перевірка коду", size=16, bold=True))
    p.append(text(W / 2, 52, "єдиний вхід — типізована модель; з неї виводяться діаграми й нею ж завалюється невірна залежність",
                  size=10.5, color=MUTED, italic=True))

    # МОДЕЛЬ — єдине джерело, ліворуч по центру
    mx, my, mw, mh = 40, 208, 200, 148
    mcx = mx + mw / 2
    p.append(rect(mx, my, mw, mh, fill=SYS, stroke=NEG, sw=2, rx=12))
    p.append(text(mcx, my + 32, "МОДЕЛЬ як дані", size=13.5, color=INK, bold=True))
    p.append(text(mcx, my + 60, "елементи + ID", size=10.5, color=MUTED, italic=True))
    p.append(text(mcx, my + 82, "оголошені зв'язки", size=10.5, color=MUTED, italic=True))
    p.append(text(mcx, my + 112, "єдине джерело", size=10.5, color=NEG, italic=True))
    p.append(text(mcx, my + 132, "правди", size=10.5, color=NEG, italic=True))

    # ── Верхня доріжка: РЕНДЕР ──
    pjx, pjy, pjw, pjh = 360, 118, 240, 64
    p.append(rect(pjx, pjy, pjw, pjh, fill=FILL, stroke=MUTED, sw=1.6, rx=8))
    p.append(text(pjx + pjw / 2, pjy + 27, "project(scope, рівень)", size=12.5, color=INK, bold=True))
    p.append(text(pjx + pjw / 2, pjy + 48, "фільтр графа → текст", size=10, color=MUTED, italic=True))
    p.append(arrow(mx + mw, my + 34, pjx - 4, pjy + pjh / 2, color=INK, sw=1.9))

    ocx, ocy, ocw, och = 720, 102, 250, 96
    p.append(rect(ocx, ocy, ocw, och, fill="#eef7ef", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(ocx + ocw / 2, ocy + 27, "Дві узгоджені діаграми", size=12.5, color=INK, bold=True))
    p.append(text(ocx + ocw / 2, ocy + 50, "контекст + контейнер", size=10.5, color=MUTED, italic=True))
    p.append(text(ocx + ocw / 2, ocy + 72, "Mermaid / PlantUML", size=10.5, color=MUTED, italic=True))
    p.append(arrow(pjx + pjw, pjy + pjh / 2, ocx - 4, ocy + och / 2, color=INK, sw=1.9))

    # ── Нижня доріжка: ПЕРЕВІРКА ──
    fx, fy, fw, fh = 360, 362, 240, 64
    p.append(rect(fx, fy, fw, fh, fill=FILL, stroke=MUTED, sw=1.6, rx=8))
    p.append(text(fx + fw / 2, fy + 27, "checkFitness(модель, код)", size=12, color=INK, bold=True))
    p.append(text(fx + fw / 2, fy + 48, "оголошене  vs  фактичне", size=10, color=MUTED, italic=True))
    # два входи fitness: оголошені зв'язки (з моделі) і фактичні (з коду)
    p.append(arrow(mx + mw, my + mh - 26, fx - 4, fy + 20, color=INK, sw=1.9))
    p.append(text(300, 300, "оголошені зв'язки", size=10, color=MUTED, italic=True))
    cbx, cby, cbw, cbh = 40, 430, 200, 66
    p.append(rect(cbx, cby, cbw, cbh, fill=DB, stroke="#8a6508", sw=1.6, rx=8))
    p.append(text(cbx + cbw / 2, cby + 28, "КОД: import-и", size=12.5, color=INK, bold=True))
    p.append(text(cbx + cbw / 2, cby + 48, "фактичні залежності", size=10, color=MUTED, italic=True))
    p.append(arrow(cbx + cbw, cby + 18, fx - 4, fy + fh - 14, color=INK, sw=1.9))
    p.append(text(300, 474, "скан коду", size=10, color=MUTED, italic=True))

    # виходи: PASS / FAIL
    p.append(rect(720, 330, 250, 44, fill="#eef7ef", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(720 + 125, 330 + 27, "PASS — код = моделі", size=11.5, color="#1e7a3d", bold=True))
    p.append(rect(720, 392, 250, 62, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    p.append(text(720 + 125, 392 + 25, "FAIL: web → db", size=12, color=POS, bold=True))
    p.append(text(720 + 125, 392 + 45, "такої стрілки нема", size=10, color=POS, italic=True))
    p.append(arrow(fx + fw, fy + 20, 716, 330 + 22, color=INK, sw=1.7))
    p.append(arrow(fx + fw, fy + fh - 16, 716, 392 + 31, color=INK, sw=1.7))

    p.append(text(W / 2, 527, "Правиш модель раз — обидві діаграми оновлюються разом; проводиш заборонену залежність — падає складання.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "pipeline.svg"), W, H, *p)


# ── 10. Ліс вкладення: єдиний батько + ациклічність → глибина = рівень ─────────
def fig_nesting_forest():
    W, H = 900, 560
    p = []
    p.append(text(W / 2, 30, "Ліс вкладення: єдиний батько й ациклічність дають дерево", size=16, bold=True))
    p.append(text(W / 2, 50, "глибина вузла в дереві — це і є рівень C4; тому рівнів рівно чотири", size=11, color=MUTED, italic=True))

    # горизонтальні смуги глибини + підпис рівня ліворуч
    depths = [
        (150, "рівень 1", "система · людина"),
        (265, "рівень 2", "контейнер"),
        (380, "рівень 3", "компонент"),
        (495, "рівень 4", "код"),
    ]
    for dy, lvl, kind in depths:
        p.append(text(24, dy - 4, lvl, size=11.5, color=NEG, bold=True, anchor="start"))
        p.append(text(24, dy + 13, kind, size=10, color=MUTED, italic=True, anchor="start"))

    # дерево «Магазин» + два тривіальні дерева (Покупець, Платіжний шлюз)
    p.append(box(310, 150, 126, 52, "Покупець", "людина", PER, FIELD, ts=12.5, ss=9.5))
    p.append(box(490, 150, 150, 52, "Магазин", "система", SYS, NEG, ts=13, ss=9.5))
    p.append(box(690, 150, 158, 52, "Платіжний шлюз", "система", EXT, MUTED, ts=11.5, ss=9))
    p.append(box(430, 265, 118, 48, "Веб", "контейнер", SYS, NEG, ts=12.5, ss=9))
    p.append(box(580, 265, 118, 48, "API", "контейнер", SYS, NEG, ts=12.5, ss=9))
    p.append(box(520, 380, 126, 48, "Замовлення", "компонент", SYS, NEG, ts=11, ss=9))
    p.append(box(680, 380, 118, 48, "Платежі", "компонент", SYS, NEG, ts=11.5, ss=9))
    p.append(box(520, 495, 150, 48, "OrderService", "клас", FILL, MUTED, ts=11.5, ss=9))

    # ребра-батьки (дитина → батько): тонкі суцільні лінії
    p.append(line(430, 241, 470, 176, color=INK, sw=1.5))   # Веб → Магазин
    p.append(line(580, 241, 510, 176, color=INK, sw=1.5))   # API → Магазин
    p.append(line(520, 356, 555, 289, color=INK, sw=1.5))   # Замовлення → API
    p.append(line(680, 356, 605, 289, color=INK, sw=1.5))   # Платежі → API
    p.append(line(520, 471, 520, 404, color=INK, sw=1.5))   # OrderService → Замовлення
    p.append(text(490, 206, "містить", size=9.5, color=MUTED, italic=True))   # у V-проміжку між ребрами до «Магазин»

    # заборонений другий батько: Платежі → Веб (був би граф, не ліс)
    p.append(line(640, 360, 486, 300, color=POS, sw=1.6, dash="5,4"))   # закінчується РІВНО на ✗ (не ріже його)
    p.append(text(486, 300, "✗", size=16, color=POS, bold=True))
    p.append(text(628, 314, "2-й батько заборонено", size=10, color=POS, anchor="start"))
    p.append(text(628, 330, "(глибина була б неоднозначна)", size=9.5, color=MUTED, italic=True, anchor="start"))

    p.append(text(W / 2, 540, "Кожен вузол має щонайбільше одного батька, і жоден не свій предок — тож структура є ліс, а глибина завжди визначена.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "nesting-forest.svg"), W, H, *p)


# ── 11. Проєкція: діаграма — індукований підграф + підняті ребра ───────────────
def fig_projection():
    W, H = 900, 470
    p = []
    p.append(text(W / 2, 30, "Проєкція: діаграма — індукований підграф і підняті ребра", size=16, bold=True))
    p.append(text(W / 2, 50, "той самий зв'язок моделі виглядає по-різному на різних рівнях", size=11, color=MUTED, italic=True))

    # верх — справжній зв'язок рівня 3
    p.append(box(230, 128, 200, 58, "Замовлення", "компонент у API", SYS, NEG, ts=13, ss=10))
    p.append(box(560, 128, 150, 58, "База даних", "контейнер", DB, "#8a6508", ts=12.5, ss=10))
    p.append(arrow(332, 128, 483, 128, color=INK, sw=1.9))
    p.append(text(407, 111, "читає [SQL]", size=10.5, color=MUTED, italic=True))
    p.append(text(230, 178, "рівень 3 — справжній зв'язок у моделі", size=10, color=NEG, italic=True))

    # стрілка вниз — проєкція з підняттям кінців
    p.append(arrow(395, 205, 395, 268, color=INK, sw=2))
    p.append(text(410, 230, "проєкція на рівень 2:", size=10.5, color=INK, bold=True, anchor="start"))
    p.append(text(410, 246, "кінець підняти до предка-контейнера", size=10, color=MUTED, italic=True, anchor="start"))
    p.append(text(410, 261, "Замовлення  ⟹  API", size=10.5, color=NEG, bold=True, anchor="start"))

    # низ — той самий зв'язок, піднятий до рівня 2
    p.append(box(230, 330, 200, 58, "API", "контейнер", SYS, NEG, ts=13, ss=10))
    p.append(box(560, 330, 150, 58, "База даних", "контейнер", DB, "#8a6508", ts=12.5, ss=10))
    p.append(arrow(332, 330, 483, 330, color=INK, sw=1.9))
    p.append(text(407, 313, "читає [SQL]", size=10.5, color=MUTED, italic=True))
    p.append(text(230, 380, "рівень 2 — той самий зв'язок, піднятий", size=10, color=NEG, italic=True))

    # права панель — правило індукції
    body, bw, bh = textbox(772, 235,
                           "правило проєкції\n\nвершини: лишаємо ті,\nщо проходять предикат\n(scope + рівень)\n\nребро u→v лишається\nтільки якщо обидва\nкінці лишились\n\nглибший a→b підіймається\nдо предок(a) → предок(b)",
                           size=10.5, pad=12, fill="#fbfcff", stroke=NEG, sw=1.5, min_w=210)
    p.append(body)

    p.append(text(W / 2, 452, "Кожна діаграма читає той самий граф; ніщо не малюється двічі — тому в'ю не можуть суперечити одна одній.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "projection.svg"), W, H, *p)


# ── 12. Бюджет читаності: елементи ростуть лінійно, зв'язки — квадратично ──────
def fig_readability_budget():
    W, H = 900, 500
    p = []
    p.append(text(W / 2, 30, "Бюджет читаності: чому межа — кільканадцять, а не з повітря", size=16, bold=True))
    p.append(text(W / 2, 50, "стежити доводиться зв'язки, а їх — до n·(n−1)/2; стеля сприйняття ріже саме їх", size=11, color=MUTED, italic=True))

    ox, oy = 120, 410          # початок координат
    ax1, ay1 = 820, 90         # край осей
    nmax = 24
    vmax = 280.0
    def X(n): return ox + (ax1 - ox) * (n / nmax)
    def Y(v): return oy - (oy - ay1) * (v / vmax)
    p.append(line(ox, oy, ax1, oy, color=INK, sw=2))          # вісь X
    p.append(line(ox, oy, ox, ay1, color=INK, sw=2))          # вісь Y
    p.append(text((ox + ax1) / 2, oy + 42, "кількість елементів на діаграмі  n", size=11, color=INK))
    p.append(text(ox - 92, (oy + ay1) / 2 - 8, "скільки", size=10.5, color=INK, anchor="start"))
    p.append(text(ox - 92, (oy + ay1) / 2 + 7, "зв'язків", size=10.5, color=INK, anchor="start"))
    p.append(text(ox - 92, (oy + ay1) / 2 + 22, "стежити", size=10.5, color=MUTED, italic=True, anchor="start"))

    for n in (0, 4, 8, 12, 16, 20, 24):
        p.append(line(X(n), oy, X(n), oy + 5, color=INK, sw=1.4))
        p.append(text(X(n), oy + 20, str(n), size=10, color=MUTED))

    # квадратична крива зв'язків n(n-1)/2
    pts = []
    for n in range(0, nmax + 1):
        pts.append("%.1f,%.1f" % (X(n), Y(n * (n - 1) / 2)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), POS))
    p.append(text(X(21) + 6, Y(21 * 20 / 2) - 6, "зв'язки ≈ n²/2", size=11, color=POS, bold=True, anchor="start"))

    # лінійна лінія елементів n
    p.append(line(X(0), Y(0), X(nmax), Y(nmax), color=NEG, sw=2))
    p.append(text(X(24) - 4, Y(24) - 12, "елементи ~ n", size=10.5, color=NEG, anchor="end"))

    # стеля сприйняття C = 66 → n* = 12
    C = 66.0
    p.append(line(ox, Y(C), ax1, Y(C), color=INK, sw=1.6, dash="6,4"))
    p.append(text(ax1 - 4, Y(C) - 8, "стеля сприйняття", size=10.5, color=INK, bold=True, anchor="end"))
    p.append(line(X(12), oy, X(12), Y(C), color=MUTED, sw=1.5, dash="4,4"))
    p.append(circle(X(12), Y(C), 4.5, fill=BG, stroke=POS, sw=2.2))
    p.append(text(X(12) + 8, 384, "n* ≈ 12", size=11.5, color=INK, bold=True, anchor="start"))   # праворуч від drop-лінії, над лінією елементів

    # підпис-висновок про √
    body, bw, bh = textbox(320, 155,
                           "стеля стоїть на зв'язках,\nа зв'язків ≈ n²/2, тому\nбюджет елементів n* ≈ √(2·стеля)\n— корінь із малого числа,\nзвідси «кільканадцять»",
                           size=10.5, pad=11, fill="#fbfcff", stroke=NEG, sw=1.4, min_w=250)
    p.append(body)

    p.append(text(W / 2, 476, "Межа не з повітря: подвоїш елементи — учетверо більше зв'язків стежити; корінь зі стелі й дає десятки, не сотні.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "readability-budget.svg"), W, H, *p)


if __name__ == "__main__":
    fig_context()
    fig_container()
    fig_levels()
    fig_timeline()
    fig_metamodel()
    fig_views()
    fig_notation()
    fig_deployment()
    fig_model_pipeline()
    fig_nesting_forest()
    fig_projection()
    fig_readability_budget()
    print("OK: figs written to", OUT)
