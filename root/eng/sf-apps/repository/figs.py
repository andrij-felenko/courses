# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

HOT  = "#fdecea"   # тривожна заливка (розбіжність, теча)
COOL = "#eafaf0"   # спокійна заливка (контракт, закрито)


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


# ── 1. Межа: колекція назовні, сховище всередині (стаття) ───────────────────
def fig_boundary():
    W, H = 1180, 450
    f = []

    # ЛІВОРУЧ — домен
    f.append(text(185, 66, "Домен", 14, bold=True))
    f.append(rect(30, 80, 310, 280))
    f.append(text(185, 104, "колекція доменних об'єктів", 13, color=MUTED))
    f.append(fitbox(50, 116, 270, 30, "Order #41 · c-19 · 1200 · paid", size=13, fill=BG))
    f.append(fitbox(50, 152, 270, 30, "Order #42 · c-77 · 350 · new", size=13, fill=BG))
    f.append(fitbox(50, 188, 270, 30, "Order #43 · c-19 · 90 · shipped", size=13, fill=BG))
    f.append(line(46, 232, 324, 232, color=MUTED, sw=1, dash="4 3"))
    f.append(mtext(185, 252, ["add(order)", "byId(id)", "forCustomer(id)", "findOverdue()"], 13))

    # ЦЕНТР — межа
    f.append(rect(470, 80, 200, 280, fill=COOL, stroke=FIELD, sw=2.5))
    f.append(text(570, 112, "Репозиторій", 15, bold=True))
    f.append(mtext(570, 180, ["переклад", "об'єкт ⇄ запис"], 13))
    f.append(mtext(570, 240, ["драйвер · мапер", "з'єднання, пул"], 12, color=MUTED))

    # ПРАВОРУЧ — сховище
    f.append(text(960, 66, "Сховище", 14, bold=True))
    f.append(rect(770, 80, 380, 280))
    f.append(text(960, 104, "де насправді лежать дані", 13, color=MUTED))
    f.append(fitbox(790, 116, 340, 56, "SQL: рядки таблиці orders\nтранзакції, індекси", size=13, fill=BG))
    f.append(fitbox(790, 180, 340, 56, "Документна база:\nдокументи JSON", size=13, fill=BG))
    f.append(fitbox(790, 244, 340, 56, "Сусідня служба:\nJSON за HTTP", size=13, fill=BG))

    # стрілки КРІЗЬ межу
    f.append(arrow(342, 140, 768, 140))
    f.append(arrow(768, 280, 342, 280))
    f.append(text(405, 124, "проси об'єкти", 12, color=MUTED))
    f.append(text(720, 124, "SELECT", 12, color=MUTED))
    f.append(text(405, 304, "готові Order", 12, color=MUTED))
    f.append(text(720, 304, "рядки", 12, color=MUTED))

    b, _, _ = textbox(590, 405, "Домен розмовляє з колекцією. З базою розмовляє репозиторій.",
                      size=14, fill=COOL, stroke=FIELD, sw=2.5, bold=True)
    f.append(b)
    render(os.path.join(OUT, "repository-boundary.svg"), W, H, *f,
           title="Репозиторій — межа між двома світами")


# ── 2. Кістяк: контракт у домені, реалізації внизу (стаття) ─────────────────
def fig_structure():
    W, H = 1080, 660
    f = []

    # домен
    f.append(rect(340, 74, 400, 86))
    f.append(text(540, 104, "Домен · LoyaltyService", 15, bold=True))
    f.append(text(540, 132, "orders.forCustomer(id)", 13, color=MUTED))

    # пунктирна залежність
    f.append(line(540, 162, 540, 190, color=LINE, sw=1.8, dash="6 4"))
    f.append(arrow(540, 186, 540, 197))
    f.append(text(560, 184, "залежить лише від контракту", 12, color=MUTED, anchor="start"))

    # контракт
    f.append(rect(340, 200, 400, 160, fill=COOL, stroke=FIELD, sw=2.5))
    f.append(text(540, 230, "interface OrderRepository", 15, bold=True))
    f.append(mtext(540, 262, ["byId(id) → Order?", "forCustomer(id) → Order[]",
                              "save(order)", "remove(order)"], 13))

    # рейка реалізацій
    f.append(arrow(540, 408, 540, 364))
    f.append(line(260, 410, 820, 410))
    f.append(line(260, 410, 260, 450))
    f.append(line(820, 410, 820, 450))

    # SQL
    f.append(rect(60, 450, 400, 130))
    f.append(cylinder(105, 515, 46, 64))
    f.append(text(300, 490, "SqlOrderRepository", 15, bold=True))
    f.append(mtext(300, 518, ["база · SELECT / INSERT", "рядки, драйвер, з'єднання"], 12))
    f.append(text(300, 558, "правда продакшну", 12, color=MUTED, italic=True))

    # InMemory
    f.append(rect(620, 450, 400, 130))
    f.append(fitbox(645, 492, 62, 46, "Map", size=13, fill=FILL))
    f.append(text(860, 490, "InMemoryOrderRepository", 15, bold=True))
    f.append(mtext(860, 518, ["звичайна Map / dict", "свіжий екземпляр на тест"], 12))
    f.append(text(860, 558, "правда тесту", 12, color=MUTED, italic=True))

    b, _, _ = textbox(540, 620, "Підмінити реалізацію = змінити сховище, не чіпаючи домен",
                      size=14, fill=COOL, stroke=FIELD, sw=2.5, bold=True)
    f.append(b)
    render(os.path.join(OUT, "repository-structure.svg"), W, H, *f,
           title="Домен володіє контрактом; сховища тягнуться до нього")


# ── 3. Пастка псевдоніма: підробка тримає посилання (вставка) ───────────────
def fig_aliasing():
    W, H = 1160, 545
    f = []
    f.append(text(140, 76, "Крок", 14, bold=True))
    f.append(text(485, 76, "Справжній SqlOrderRepository", 14, bold=True))
    f.append(text(925, 76, "Наївна підробка InMemory", 14, bold=True))

    steps = [
        ("1 · repo.save(order)\nстатус «new»",
         "у таблицю пішов РЯДОК\n(id=41, status='new')",
         "у Map лягло ПОСИЛАННЯ\nна той самий об'єкт", FILL, FILL, LINE, LINE),
        ("2 · order.markPaid()\nбез повторного save",
         "рядок у базі не змінився:\nstatus у рядку = 'new'",
         "об'єкт у Map — той самий:\nвін уже paid", FILL, FILL, LINE, LINE),
        ("3 · repo.byId(41)\n.isPaid() → ?",
         "byId зліпив НОВИЙ Order\nіз рядка → false",
         "byId віддав ТОЙ САМИЙ об'єкт\n→ true", HOT, COOL, POS, FIELD),
    ]
    for i, (s, a, b, fa, fb, sa, sb) in enumerate(steps):
        y = 96 + i * 100
        f.append(fitbox(30, y, 220, 80, s, size=13, fill=FILL))
        f.append(fitbox(280, y, 410, 80, a, size=13, fill=fa, stroke=sa,
                        sw=2.5 if fa != FILL else 1.5))
        f.append(fitbox(720, y, 410, 80, b, size=13, fill=fb, stroke=sb,
                        sw=2.5 if fb != FILL else 1.5))

    f.append(fitbox(280, 396, 410, 54, "false · так буде в продакшні", size=14,
                    fill=HOT, stroke=POS, sw=2.5, bold=True))
    f.append(fitbox(720, 396, 410, 54, "true · так «буде» в тесті", size=14,
                    fill=COOL, stroke=FIELD, sw=2.5, bold=True))
    f.append(text(705, 431, "≠", 22, color=POS, bold=True))

    b, _, _ = textbox(580, 500,
                      ["Тест зелений, продакшн губить зміну: підробка тримає ПОСИЛАННЯ, база — РЯДОК.",
                       "Ліки: підробка теж мусить тримати РЯДОК."],
                      size=13, fill=HOT, stroke=POS, sw=2.5)
    f.append(b)
    render(os.path.join(OUT, "proj-fake-aliasing.svg"), W, H, *f,
           title="Один і той самий крок — дві різні відповіді")


# ── 4. Чотири канали недетермінованості (вставка) ───────────────────────────
def fig_determinism():
    W, H = 1180, 545
    f = []
    f.append(fitbox(30, 64, 440, 40, "Канал недетермінованості", size=14, bold=True, fill=FILL))
    f.append(fitbox(490, 64, 330, 40, "Тест на живій базі", size=14, bold=True, fill=FILL))
    f.append(fitbox(840, 64, 330, 40, "Тест на свіжій підробці", size=14, bold=True, fill=FILL))

    rows = [
        ("Залишок від попереднього тесту\n(спільна база, порядок запуску)",
         "ТЕЧЕ · чужі рядки лишаються",
         "ЗАКРИТО · новий екземпляр\nна кожен тест", COOL, FIELD),
        ("Порядок рядків без ORDER BY",
         "ТЕЧЕ · порядок не обіцяний",
         "ОМАНЛИВО ТИХО · dict тримає\nпорядок вставляння —\nтест не побачить баг", HOT, POS),
        ("Годинник: NOW(), Date.now()",
         "ТЕЧЕ · час іде",
         "ТЕЧЕ ТЕЖ · треба вколоти\nгодинник ззовні", HOT, POS),
        ("Ключі: autoincrement, UUID",
         "ТЕЧЕ · ключ щоразу інший",
         "ТЕЧЕ ТЕЖ · треба вколоти\nгенератор ключів", HOT, POS),
    ]
    for i, (c1, c2, c3, fill3, stroke3) in enumerate(rows):
        y = 112 + i * 88
        f.append(fitbox(30, y, 440, 80, c1, size=13, fill=BG))
        f.append(fitbox(490, y, 330, 80, c2, size=13, fill=HOT, stroke=POS, sw=2))
        f.append(fitbox(840, y, 330, 80, c3, size=13, fill=fill3, stroke=stroke3, sw=2))

    b, _, _ = textbox(600, 500,
                      ["Свіжий екземпляр знімає СПІЛЬНИЙ СТАН — і тільки його.",
                       "Годинник і ключі детермінованими не стають: їх треба подати ззовні."],
                      size=13, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(OUT, "proj-determinism-channels.svg"), W, H, *f,
           title="Що підробка закриває, а що ні")


# ── 5. Контракт-набір: один набір тестів — дві реалізації (вставка) ─────────
def fig_contract():
    W, H = 1080, 540
    f = []
    f.append(rect(240, 64, 600, 140, fill=COOL, stroke=FIELD, sw=2.5))
    f.append(text(540, 92, "Контракт-набір проти OrderRepository", 15, bold=True))
    f.append(mtext(540, 122, ["save(o) → byId(o.id) дає рівний o",
                              "мутація після save НЕ видима без save",
                              "recentPaidOrders: свіжі перші, чужих нема",
                              "remove(o) → byId(o.id) дає null"], 12))

    f.append(arrow(420, 206, 280, 268))
    f.append(arrow(660, 206, 800, 268))

    f.append(rect(60, 270, 400, 120))
    f.append(text(260, 300, "InMemoryOrderRepository", 15, bold=True))
    f.append(mtext(260, 328, ["на КОЖЕН коміт · ~8 мс", "без бази, без диску"], 12))
    f.append(text(260, 372, "зелений = підробка не бреше", 12, color=MUTED, italic=True))

    f.append(rect(620, 270, 400, 120))
    f.append(text(820, 300, "SqlOrderRepository", 15, bold=True))
    f.append(mtext(820, 328, ["у CI · піднімає базу", "секунди, не мілісекунди"], 12))
    f.append(text(820, 372, "червоний = контракт змінився", 12, color=MUTED, italic=True))

    b, _, _ = textbox(540, 460,
                      ["Обидві колонки зелені — підробка й база відповідають ОДНАКОВО.",
                       "Аж тоді сотні швидких тестів над підробкою можна читати",
                       "як правду про продакшн."],
                      size=13, fill=COOL, stroke=FIELD, sw=2.5)
    f.append(b)
    render(os.path.join(OUT, "proj-contract-test.svg"), W, H, *f,
           title="Один набір тестів — дві реалізації")


# ── 6. Іменник у центрі абстракції: 1984 → 2003 (вставка hist) ──────────────
def fig_noun_shift():
    W, H = 1180, 712
    f = []

    C1X, C1W = 60, 292
    C2X, C2W = 382, 248
    C3X, C3W = 660, 440

    f.append(text(C1X + C1W / 2, 74, "Коли й хто", 14, color=MUTED, bold=True))
    f.append(text(C2X + C2W / 2, 74, "Що назвали", 14, color=MUTED, bold=True))
    f.append(text(C3X + C3W / 2, 74, "Що стоїть у центрі абстракції", 14, color=MUTED, bold=True))

    RH = 84
    rows = [
        (100, "1984 · Джордж Коупленд,\nДевід Маєр (GemStone)",
         "неузгодженість опорів\n(impedance mismatch)",
         "прірву не мостять — її скасовують:\nоб'єктна СКБД замість реляційної", FILL, LINE, 1.5),
        (200, "1995–96 · Кайл Браун,\nБрюс Вайтенек (Smalltalk)",
         "Crossing Chasms",
         "рядок і таблиця:\nяк один об'єкт лягає в базу", FILL, LINE, 1.5),
        (300, "2001 · Діпак Алур, Джон Крупі,\nДен Малкс (Sun Java Center)",
         "DAO",
         "ДЖЕРЕЛО ДАНИХ\n«абстрагувати доступ до джерела»", HOT, POS, 2.5),
        (438, "2002 · Едвард Гіатт, Роб Мі\n(гостьовий запис у PoEAA)",
         "Repository",
         "КОЛЕКЦІЯ ДОМЕННИХ ОБ'ЄКТІВ\n«інтерфейс на кшталт колекції»", COOL, FIELD, 2.5),
        (538, "2003 · Ерік Еванс\n(Domain-Driven Design)",
         "REPOSITORY",
         "КОРІНЬ АГРЕГАТУ\n«лише там, де потрібен прямий доступ»", COOL, FIELD, 2.5),
    ]
    for y, who, name, noun, fill3, stroke3, sw3 in rows:
        f.append(fitbox(C1X, y, C1W, RH, who, size=13, fill=BG))
        f.append(fitbox(C2X, y, C2W, RH, name, size=15, bold=True))
        f.append(fitbox(C3X, y, C3W, RH, noun, size=14, fill=fill3, stroke=stroke3, sw=sw3))

    # смуга-маркер точно в проміжку між рядком DAO (кінець 384) і Repository (початок 438)
    b, _, _ = textbox(590, 411,
                      "тут іменник у центрі змінився: джерело даних → колекція доменних об'єктів",
                      size=14, color=FIELD, bold=True, fill=BG, stroke=FIELD, sw=2.5, pad=11)
    f.append(b)

    f.append(text(W / 2, 668, "Форма абстракції майже не змінилася — інтерфейс, за яким сховані запити.",
                  14, color=MUTED))
    f.append(text(W / 2, 690, "Змінилося те, ЩО вона обіцяє сховати: не драйвер бази, а саму наявність бази.",
                  14, bold=True))

    render(os.path.join(OUT, "hist-noun-shift.svg"), W, H, *f,
           title="Іменник у центрі абстракції: 1984 → 2003")


if __name__ == "__main__":
    fig_boundary()
    fig_structure()
    fig_aliasing()
    fig_determinism()
    fig_contract()
    fig_noun_shift()
    print("ok:", ", ".join(sorted(os.listdir(OUT))))
