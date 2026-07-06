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


if __name__ == "__main__":
    fig_context()
    fig_container()
    fig_levels()
    fig_timeline()
    print("OK: figs written to", OUT)
