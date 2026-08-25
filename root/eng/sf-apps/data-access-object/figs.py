# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

COOL = "#eafaf0"   # спокійна заливка (контракт)


def cylinder(cx, cy, w, h, fill=BG, stroke=LINE, sw=1.5):
    """Циліндр бази даних (svgkit не має — локальний помічник)."""
    rx = w / 2.0
    ry = max(5.0, h * 0.14)
    top, bot = cy - h / 2.0, cy + h / 2.0
    out = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="none"/>'
           % (cx - rx, top, w, h, fill)]
    out.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
               'stroke-width="%.1f"/>' % (cx, bot, rx, ry, fill, stroke, sw))
    out.append(line(cx - rx, top, cx - rx, bot, color=stroke, sw=sw))
    out.append(line(cx + rx, top, cx + rx, bot, color=stroke, sw=sw))
    out.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
               'stroke-width="%.1f"/>' % (cx, top, rx, ry, fill, stroke, sw))
    return "".join(out)


# ── 1. DAO як межа: інтерфейс угорі, різні джерела внизу ─────────────────────
def fig_structure():
    W, H = 1120, 690
    f = []

    # клієнт
    f.append(rect(360, 66, 400, 84))
    f.append(text(560, 96, "Бізнес-логіка · сервіс", 15, bold=True))
    f.append(text(560, 122, 'orderDao.findByStatus("paid")', 13, color=MUTED))

    # пунктирна залежність
    f.append(line(560, 150, 560, 184, color=LINE, sw=1.8, dash="6 4"))
    f.append(arrow(560, 180, 560, 194))
    f.append(text(575, 176, "залежить лише від інтерфейсу", 12, color=MUTED, anchor="start"))

    # інтерфейс DAO
    f.append(rect(360, 198, 400, 176, fill=COOL, stroke=FIELD, sw=2.5))
    f.append(text(560, 228, "interface OrderDao", 15, bold=True))
    f.append(mtext(560, 260, ["findById(id) → OrderRow?",
                              "findByStatus(s) → OrderRow[]",
                              "insert(row) · update(row)",
                              "delete(id)"], 13))

    # рейка вниз до реалізацій
    f.append(arrow(560, 422, 560, 378))
    f.append(line(210, 422, 910, 422))
    f.append(line(210, 422, 210, 460))
    f.append(line(560, 422, 560, 460))
    f.append(line(910, 422, 910, 460))

    # SQL
    f.append(rect(50, 460, 320, 150))
    f.append(cylinder(100, 528, 44, 62))
    f.append(text(240, 494, "SqlOrderDao", 15, bold=True))
    f.append(mtext(240, 522, ["реляційна база", "SELECT · INSERT · драйвер"], 12))
    f.append(text(240, 566, "продакшн", 12, color=MUTED, italic=True))

    # REST
    f.append(rect(400, 460, 320, 150))
    f.append(fitbox(420, 500, 60, 46, "HTTP", size=13, fill=FILL))
    f.append(text(600, 494, "RestOrderDao", 15, bold=True))
    f.append(mtext(600, 522, ["сусідня служба", "JSON за HTTP"], 12))
    f.append(text(600, 566, "інше джерело", 12, color=MUTED, italic=True))

    # InMemory
    f.append(rect(750, 460, 320, 150))
    f.append(fitbox(770, 500, 60, 46, "Map", size=13, fill=FILL))
    f.append(text(910, 494, "InMemoryOrderDao", 15, bold=True))
    f.append(mtext(910, 522, ["звичайна Map", "свіжий на кожен тест"], 12))
    f.append(text(910, 566, "тест", 12, color=MUTED, italic=True))

    b, _, _ = textbox(560, 648,
                      "Підмінити реалізацію = підмінити джерело даних. Клієнт не змінюється.",
                      size=14, fill=COOL, stroke=FIELD, sw=2.5, bold=True)
    f.append(b)
    render(os.path.join(OUT, "dao-structure.svg"), W, H, *f,
           title="Один інтерфейс DAO — різні джерела під ним")


# ── 2. Вісь відмінності: DAO — джерело даних, репозиторій — колекція ─────────
def fig_vs_repository():
    W, H = 1240, 600
    f = []

    AX, AW = 40, 200        # стовпець «вимір»
    DX, DW = 260, 460       # стовпець DAO
    RX, RW = 740, 460       # стовпець «репозиторій»

    # заголовки стовпців
    f.append(fitbox(AX, 60, AW, 60, "вимір", size=13, fill=BG, color=MUTED))
    f.append(fitbox(DX, 60, DW, 60, "DAO\nмислить джерелом даних", size=15, bold=True, fill=FILL))
    f.append(fitbox(RX, 60, RW, 60, "Репозиторій\nмислить колекцією об'єктів", size=15, bold=True, fill=FILL))

    RH = 80
    rows = [
        ("Одиниця",
         "один на таблицю чи джерело",
         "один на корінь агрегату"),
        ("Методи звучать",
         "insert · findByStatus\n— мовою сховища",
         "forCustomer · overdue\n— мовою домену"),
        ("Повертає",
         "плоскі записи\n(Transfer Object / DTO)",
         "готові доменні\nсутності"),
        ("Прикидається",
         "адаптером\nдо джерела даних",
         "колекцією\nоб'єктів у пам'яті"),
    ]
    for i, (asp, dao, repo) in enumerate(rows):
        y = 132 + i * 92
        f.append(fitbox(AX, y, AW, RH, asp, size=13, fill=BG, color=MUTED))
        f.append(fitbox(DX, y, DW, RH, dao, size=13, fill=BG))
        f.append(fitbox(RX, y, RW, RH, repo, size=13, fill=BG))

    b, _, _ = textbox(620, 540,
                      ["Форма однакова — інтерфейс, за яким сховані запити.",
                       "Різниця в тому, ЩО стоїть у центрі: джерело даних чи доменна колекція."],
                      size=13, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(OUT, "dao-vs-repository.svg"), W, H, *f,
           title="DAO проти репозиторія: та сама форма, різний іменник у центрі")


# ── 3. Лінія часу: три імені однієї ідеї за три роки ────────────────────────
def fig_three_names():
    W, H = 1240, 512
    f = []

    def card(cx, top, book, who, term, essence, note):
        w, h = 360, 214
        x = cx - w / 2
        out = rect(x, top, w, h)
        out += text(cx, top + 30, book, 14, bold=True)
        out += text(cx, top + 52, who, 12, color=MUTED)
        out += fitbox(x + 24, top + 66, w - 48, 42, term, size=17,
                      bold=True, fill=COOL, stroke=FIELD, sw=2.5)
        out += mtext(cx, top + 134, essence, 13)
        out += text(cx, top + 196, note, 12, color=MUTED, italic=True)
        return out

    NODES = (210, 620, 1030)
    TOP = 58

    f.append(card(210, TOP,
                  "2001 · Core J2EE Patterns",
                  "Sun Java Center: Алур · Крупі · Малкс",
                  "Data Access Object",
                  ["«абстрагувати й сховати", "весь доступ до джерела даних»"],
                  "+ фабрика DAO, + плоский Value Object"))
    f.append(card(620, TOP,
                  "2002 · P of EAA",
                  "Мартін Фаулер",
                  "Table Data Gateway",
                  ["один об'єкт на таблицю —", "весь її SQL в одному місці"],
                  "та сама форма, інша назва"))
    f.append(card(1030, TOP,
                  "2002 → 2003 · PoEAA → DDD",
                  "Фаулер вказав → Ерік Еванс розгорнув",
                  "Repository",
                  ["прикидається колекцією", "доменних об'єктів у пам'яті"],
                  "виріс поряд, зрісся з DAO"))

    # вісь часу
    ay = 300
    f.append(line(60, ay, 1150, ay, color=LINE, sw=1.8))
    f.append(arrow(1150, ay, 1180, ay))
    f.append(text(1170, ay - 12, "час", 12, color=MUTED, anchor="end"))
    for cx in NODES:
        f.append(line(cx, TOP + 214, cx, ay - 8, color=LINE, sw=1.4, dash="4 4"))
        f.append(circle(cx, ay, 8, fill=FIELD, stroke=FIELD))

    # три вузли сходяться в одну точку — одна ідея
    conv = (620, 372)
    for cx in NODES:
        f.append(line(cx, ay + 8, conv[0], conv[1], color=MUTED, sw=1.4))
    f.append(circle(conv[0], conv[1], 5, fill=MUTED, stroke=MUTED))

    b, _, _ = textbox(620, 424,
                      ["Три роки — три імені для майже однієї ідеї: сховати доступ до даних за інтерфейсом.",
                       "Звідси плутанина DAO / Table Data Gateway / Repository донині."],
                      size=14, fill=COOL, stroke=FIELD, sw=2.5, bold=True)
    f.append(b)
    render(os.path.join(OUT, "dao-three-names.svg"), W, H, *f,
           title="Одна ідея під трьома іменами: 2001 → 2003")


# ── 4. Прихований N+1: цикл викликів проти пакетного запиту ──────────────────
def fig_n_plus_one():
    W, H = 1180, 430
    f = []
    HOT = "#fdecea"   # гаряча заливка (по одному запиту на рядок)

    # рядок 1 — наївно: 1 + N
    f.append(fitbox(40, 92, 210, 66, "Наївно\nцикл по рядках",
                    size=14, fill=BG, color=MUTED, bold=True))
    f.append(fitbox(270, 92, 156, 66, "findByStatus\n→ N рядків", size=13, fill=FILL))
    for x in (446, 522, 598, 674, 750):
        f.append(fitbox(x, 92, 68, 66, "findById", size=12, fill=HOT, stroke=POS))
    f.append(text(840, 132, "…", size=24, color=POS, bold=True))
    b, _, _ = textbox(970, 125, "1 + N запитів",
                      size=15, fill=HOT, stroke=POS, sw=2, bold=True, color=POS)
    f.append(b)

    # рядок 2 — пакетно: 2
    f.append(fitbox(40, 236, 210, 66, "Пакетно\nодин IN-запит",
                    size=14, fill=BG, color=MUTED, bold=True))
    f.append(fitbox(270, 236, 156, 66, "findByStatus\n→ N рядків", size=13, fill=FILL))
    f.append(fitbox(446, 236, 156, 66, "findByIds(ids)\n→ усі разом",
                    size=13, fill=COOL, stroke=FIELD))
    b, _, _ = textbox(970, 269, "2 запити",
                      size=15, fill=COOL, stroke=FIELD, sw=2, bold=True, color=FIELD)
    f.append(b)

    b, _, _ = textbox(590, 382,
                      "Та сама відповідь. Ліворуч — сотня походів у базу, праворуч — два.",
                      size=14, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(OUT, "dao-n-plus-one.svg"), W, H, *f,
           title="Прихований N+1: цикл викликів проти пакетного запиту")


if __name__ == "__main__":
    fig_structure()
    fig_vs_repository()
    fig_three_names()
    fig_n_plus_one()
    print("ok:", ", ".join(sorted(os.listdir(OUT))))
