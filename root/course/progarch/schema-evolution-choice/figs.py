# -*- coding: utf-8 -*-
"""Фігури до кроку «Вибір стратегії еволюції даних».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#eafaf0"
REDFILL   = "#fdecea"
YELL      = "#fff8e8"
YSTROKE   = "#c9a93b"
BLUEFILL  = "#eef2f6"


# ───────── Фіг. 1: лійка рішення ─────────
def fig_decision_funnel():
    W, H = 1080, 660
    f = []

    # старт
    b, _, _ = textbox(300, 80, "Треба змінити\nформу даних",
                      size=14, bold=True, fill=FILL, stroke=INK, sw=2)
    f.append(b)
    f.append(arrow(300, 116, 300, 150, color=INK, sw=1.9))

    # ── розвилка 1: похідні дані? ──
    f.append(fitbox(196, 152, 208, 62, "Це похідні\nдані?",
                    size=15, fill=YELL, stroke=YSTROKE, bold=True, sw=2))
    # так → перебудова
    f.append(text(468, 172, "так", size=13, color=FIELD, bold=True))
    f.append(arrow(404, 183, 608, 183, color=FIELD, sw=1.9))
    f.append(fitbox(610, 150, 400, 68,
                    "Не мігруй нічого: зміни функцію →\nперебудуй із джерела\n(немає вікна — найдешевше)",
                    size=13, fill=GREENFILL, stroke=FIELD, bold=True))
    # ні ↓
    f.append(text(318, 250, "ні", size=13, color=INK, bold=True))
    f.append(arrow(300, 214, 300, 292, color=INK, sw=1.9))

    # ── розвилка 2: переписувані? ──
    f.append(fitbox(186, 294, 228, 66, "Наявні дані\nможна переписати?",
                    size=14, fill=YELL, stroke=YSTROKE, bold=True, sw=2))
    # так → міграція на місці
    f.append(mtext(474, 278, ["так —", "змінне,", "обмежене"],
                   size=11.5, color=FIELD, bold=True))
    f.append(arrow(414, 327, 608, 327, color=FIELD, sw=1.9))
    f.append(fitbox(610, 294, 400, 68,
                    "Міграція на місці:\nexpand → backfill → contract\n(вікно коротке, дані твої)",
                    size=13, fill=FILL, stroke=MUTED, bold=True))
    # ні ↓ → schema-on-read
    f.append(mtext(322, 392, ["ні —", "незмінна", "історія"],
                   size=11.5, color=INK, bold=True))
    f.append(arrow(300, 360, 300, 438, color=INK, sw=1.9))
    f.append(fitbox(100, 440, 400, 74,
                    "schema-on-read:\nверсіонуй записи, декодуй на читанні,\nісторію не переписуй",
                    size=13, fill=BLUEFILL, stroke=INK, bold=True))

    # ── наскрізний банер: неконтрольована межа ──
    f.append(fitbox(96, 556, 918, 76,
                    "Перетинає межу, яку не оновиш разом (пристрої в полі, зовнішні клієнти, незалежні сервіси)?\n"
                    "→ обидві форми мусять бути валідні одночасно; тримай сумісність — вікно може не закритися ніколи",
                    size=13, fill=YELL, stroke=YSTROKE, bold=True, sw=2))
    # пунктирні звʼязки від двох міграційних виходів донизу до банера
    f.append(line(810, 362, 810, 556, color=MUTED, sw=1.2, dash="4 6"))
    f.append(line(300, 514, 300, 556, color=MUTED, sw=1.2, dash="4 6"))

    render(os.path.join(IMG, "decision-funnel.svg"), W, H, *f,
           title="Лійка рішення: яку стратегію еволюції даних узяти")


# ───────── Фіг. 2: вікно співіснування — cutover проти expand-contract ─────────
def fig_coexistence_window():
    W, H = 1120, 500
    f = []

    def xtick(x, y):
        return line(x, y - 8, x, y + 8, color=INK, sw=1.6)

    def cross(cx, cy):
        s = circle(cx, cy, 13, fill="#ffffff", stroke=POS, sw=1.9)
        s += line(cx - 8, cy - 8, cx + 8, cy + 8, color=POS, sw=2)
        s += line(cx + 8, cy - 8, cx - 8, cy + 8, color=POS, sw=2)
        return s

    def check(cx, cy):
        s = circle(cx, cy, 13, fill=GREENFILL, stroke=FIELD, sw=1.9)
        s += text(cx, cy + 5, "✓", size=15, color=FIELD, bold=True)
        return s

    # ── ВЕРХ: cutover ──
    f.append(text(66, 96, "Cutover — жорсткий флип", size=15, color=POS,
                  bold=True, anchor="start"))
    yT = 128
    f.append(line(150, yT, 1020, yT, color=INK, sw=2))
    # мить флипу
    f.append(line(560, yT - 30, 560, yT + 30, color=POS, sw=2.6))
    f.append(text(560, yT - 40, "мить флипу — усі мусять перескочити разом",
                  size=12.5, color=POS, bold=True))
    f.append(text(350, yT + 34, "стара форма", size=13, color=MUTED, bold=True))
    f.append(text(790, yT + 34, "нова форма", size=13, color=MUTED, bold=True))
    # старий читач, що не перескочив
    f.append(cross(690, yT))
    f.append(text(690, yT + 56, "старий читач ще живий → ламається",
                  size=12.5, color=POS, bold=True))

    # ── НИЗ: expand → migrate → contract ──
    f.append(text(66, 250, "Expand → Migrate → Contract", size=15,
                  color=FIELD, bold=True, anchor="start"))
    yB = 360
    # смуга співіснування (позаду) — накриває expand+migrate
    f.append(rect(150, 300, 590, 132, fill=GREENFILL, stroke=FIELD, sw=1.3, rx=8))
    f.append(text(445, 292, "обидві форми валідні — будь-який читач, оновлений чи ні, працює",
                  size=12.5, color=FIELD, bold=True))
    # вісь
    f.append(line(150, yB, 1020, yB, color=INK, sw=2))
    for x in (150, 445, 740, 1020):
        f.append(xtick(x, yB))
    # фази — підписи під віссю
    f.append(mtext(297, yB + 28, ["EXPAND", "пиши обидві,", "читай стару"],
                   size=12.5, color=INK, bold=True))
    f.append(mtext(592, yB + 28, ["MIGRATE", "бекфіл старих рядків,", "читачі → нова"],
                   size=12.5, color=INK, bold=True))
    f.append(mtext(880, yB + 28, ["CONTRACT", "припини писати стару,", "викинь"],
                   size=12.5, color=MUTED, bold=True))
    # читачі переходять будь-де в смузі — безпечно
    f.append(check(360, yB))
    f.append(check(640, yB))
    # закриття вікна
    f.append(line(740, yB - 30, 740, yB + 8, color=MUTED, sw=1.8, dash="5 5"))
    f.append(text(830, yB - 40, "вікно закрите — лишилась одна форма",
                  size=12, color=MUTED, bold=True))

    # девіз
    f.append(text(W / 2, 476,
                  "Ніколи не флип: відкрий вікно, де обидві форми істинні, і закрий, "
                  "лише коли всі перейшли",
                  size=13, color=INK, bold=True))

    render(os.path.join(IMG, "coexistence-window.svg"), W, H, *f,
           title="Cutover ламає тих, кого не оновив; expand-contract тримає вікно")


# ───────── Фіг. 3: матриця стратегій ─────────
def fig_strategy_matrix():
    W, H = 1120, 610
    f = []

    colA, colB = 250, 668
    cw = 396
    row1y, row2y = 176, 372
    rh = 176

    # заголовки колонок
    f.append(fitbox(colA, 66, cw, 88,
                    "Контролюєш обидва боки\nТАК\n(один сервіс, спільний деплой)",
                    size=13, fill=BLUEFILL, stroke=INK, bold=True))
    f.append(fitbox(colB, 66, cw, 88,
                    "Контролюєш обидва боки\nНІ\n(пристрої в полі, зовнішні клієнти)",
                    size=13, fill=BLUEFILL, stroke=INK, bold=True))
    # заголовки рядків
    f.append(fitbox(64, row1y, 168, rh, "Пере-\nписувані\nТАК\n(змінне,\nобмежене)",
                    size=13, fill=BLUEFILL, stroke=INK, bold=True))
    f.append(fitbox(64, row2y, 168, rh, "Пере-\nписувані\nНІ\n(незмінна\nісторія)",
                    size=13, fill=BLUEFILL, stroke=INK, bold=True))

    # клітини
    f.append(fitbox(colA, row1y, cw, rh,
                    "Міграція на місці.\nBig-bang, якщо простій прийнятний;\n"
                    "інакше expand-contract.\nВікно коротке.",
                    size=13, fill=GREENFILL, stroke=FIELD, bold=True))
    f.append(fitbox(colB, row1y, cw, rh,
                    "expand → migrate → contract.\nBackward + forward сумісність.\n"
                    "Вікно довге, але закриється.",
                    size=13, fill=YELL, stroke=YSTROKE, bold=True))
    f.append(fitbox(colA, row2y, cw, rh,
                    "schema-on-read.\nВерсіонуй записи,\nдекодер росте кейсами.\n"
                    "Історію не чіпаєш.",
                    size=13, fill=YELL, stroke=YSTROKE, bold=True))
    f.append(fitbox(colB, row2y, cw, rh,
                    "schema-on-read + ПОСТІЙНА сумісність.\n"
                    "Версію ніколи не перепризначай.\nContract може не настати.",
                    size=13, fill=REDFILL, stroke=POS, bold=True))

    # банер: похідні дані обходять матрицю
    f.append(fitbox(232, 566, 656, 40,
                    "А якщо дані ПОХІДНІ — матриця не потрібна: зміни функцію й перебудуй із джерела",
                    size=13, fill=FILL, stroke=INK, bold=True, sw=2))

    render(os.path.join(IMG, "strategy-matrix.svg"), W, H, *f,
           title="Стратегія випливає з двох питань: переписувані? · контролюєш обидва боки?")


# ───────── Фіг. 4 (вставка hist): родовід сумісності + гілка доставки ─────────
def fig_compat_lineage():
    W, H = 1180, 500
    f = []

    # ── ВЕРХНЯ ГІЛКА: родовід сумісності ──
    f.append(text(W / 2, 52,
                  "Родовід сумісності схем — кожен крок штовхає форму ближче до читача",
                  size=14, color=INK, bold=True))

    lin = [
        ("1984 · ASN.1",
         "теги замість позицій;\n«зарезервуй біти на потім»,\nстарий код ігнорує незнане",
         FILL, MUTED),
        ("2007–08 · Thrift · Protobuf",
         "поле — за НОМЕРОМ,\nне за іменем;\nневідомий тег зберігають",
         FILL, MUTED),
        ("2009 · Apache Avro",
         "схема писаря їде з даними;\nчитач резолвить свою\nпроти писаревої",
         FILL, MUTED),
        ("2015 · Schema Registry",
         "центральний реєстр версій;\nгейт сумісності (backward)\nне пустить ламке в прод",
         GREENFILL, FIELD),
    ]
    lx = [10, 310, 610, 910]
    cw = 260
    for (hdr, body, bf, bs), x in zip(lin, lx):
        f.append(fitbox(x, 64, cw, 30, hdr, size=13, fill=BLUEFILL, stroke=INK, bold=True))
        f.append(fitbox(x, 94, cw, 92, body, size=13, fill=bf, stroke=bs))
    # стрілки прогресії між картками
    for x1 in (270, 570, 870):
        f.append(arrow(x1, 140, x1 + 40, 140, color=INK, sw=1.9))

    # ── стрілка від «реєстру» донизу в банер ──
    f.append(arrow(1040, 186, 1040, 210, color=FIELD, sw=2))

    # ── ЦЕНТРАЛЬНИЙ БАНЕР: висновок ──
    f.append(fitbox(40, 210, 1100, 84,
                    "Сумісність — властивість ЧИТАННЯ, а не труби.\n"
                    "Обидві гілки штовхають турботу в мить читання: "
                    "реєстр — форму, ідемпотентність — дублі.",
                    size=15, fill=YELL, stroke=YSTROKE, bold=True, sw=2))

    # ── стрілка від гілки доставки вгору в банер ──
    f.append(arrow(200, 342, 200, 296, color=POS, sw=2))

    # ── НИЖНЯ ГІЛКА: чому «рівно раз» — міф ──
    f.append(text(W / 2, 326,
                  "Паралельна гілка: чому «рівно раз» на доставці — міф",
                  size=14, color=INK, bold=True))

    dev = [
        ("1975 · Дві армії (Two Generals)",
         "Аккоюнлу, Еканадгам, Губер;\nназвав Джим Ґрей, 1978:\n«рівно раз» на доставці —\nдовести неможливо",
         REDFILL, POS),
        ("Практика замість дива",
         "at-least-once + ідемпотентність\n= «фактично раз»;\nчитач терпить дублі й повтори",
         FILL, MUTED),
        ("2017 · Kafka EOS",
         "ідемпотентний продюсер\n+ транзакції;\n«рівно раз» лише В МЕЖАХ Kafka",
         YELL, YSTROKE),
    ]
    dx = [30, 420, 810]
    dw = 340
    for (hdr, body, bf, bs), x in zip(dev, dx):
        f.append(fitbox(x, 342, dw, 30, hdr, size=13, fill=BLUEFILL, stroke=INK, bold=True))
        f.append(fitbox(x, 372, dw, 96, body, size=12.5, fill=bf, stroke=bs))
    # стрілки прогресії між картками доставки
    for x1 in (370, 760):
        f.append(arrow(x1, 420, x1 + 50, 420, color=INK, sw=1.9))

    render(os.path.join(IMG, "compat-lineage.svg"), W, H, *f,
           title="Дві лінії роду, що збіглися в одному законі: сумісність живе в читанні")


# ───────── Фіг. 5: тріаж-диспетч (вставка proj-dh-change-triage) ─────────
def fig_triage_dispatch():
    W, H = 1200, 900
    f = []
    xl, lw = 530, 440   # ліва координата й ширина листків-стратегій

    def dbox(cy, h, s):
        return fitbox(145, cy - h / 2, 210, h, s, size=13,
                      fill=YELL, stroke=YSTROKE, bold=True, sw=2)

    def leaf(cy, h, s, fill, stroke, color):
        return fitbox(xl, cy - h / 2, lw, h, s, size=13,
                      fill=fill, stroke=stroke, bold=True, color=color)

    def yes(cy):
        return text(432, cy - 11, "так", size=12, color=FIELD, bold=True)

    def no(cy):
        return text(266, cy, "ні", size=12, color=INK, bold=True)

    # старт
    b, _, _ = textbox(250, 66, "Зміна даних DH", size=14, bold=True,
                      fill=FILL, stroke=INK, sw=2)
    f.append(b)
    f.append(arrow(250, 88, 250, 116))

    # D0 — ґвардія
    cy = 151
    f.append(dbox(cy, 68, "Перепризначає\nсенс живого ключа?"))
    f.append(yes(cy)); f.append(arrow(356, cy, 528, cy))
    f.append(leaf(cy, 58, "FORBIDDEN\nзаведи нову версію — не чіпай ключ (напр. сенс wh)",
                  REDFILL, POS, POS))
    f.append(no(cy + 58)); f.append(arrow(250, cy + 34, 250, cy + 80))

    # D1 — похідні
    cy = 263
    f.append(dbox(cy, 58, "Похідні дані?"))
    f.append(yes(cy)); f.append(arrow(356, cy, 528, cy))
    f.append(leaf(cy, 56, "REBUILD\nперебудуй із джерела, без вікна (місячне число)",
                  GREENFILL, FIELD, FIELD))
    f.append(no(cy + 55)); f.append(arrow(250, cy + 29, 250, cy + 79))

    # D2 — додавання
    cy = 375
    f.append(dbox(cy, 60, "Додаєш нове\nполе / значення?"))
    f.append(yes(cy)); f.append(arrow(356, cy, 528, cy))
    f.append(leaf(cy, 56, "ADD\nдодай поруч, старе валідне (новий тип; nullable-поле)",
                  BLUEFILL, NEG, NEG))
    f.append(no(cy + 58)); f.append(arrow(250, cy + 30, 250, cy + 82))

    # D3 — прибирання
    cy = 489
    f.append(dbox(cy, 62, "Прибираєш\nстару форму?"))
    f.append(yes(cy)); f.append(arrow(356, cy, 528, cy))
    f.append(leaf(cy, 56, "RETIRE\nприбери, коли читачів нема (schema:1)",
                  FILL, MUTED, MUTED))
    f.append(no(cy + 59)); f.append(arrow(250, cy + 31, 250, cy + 84))

    # D4 — переписуваність
    cy = 607
    f.append(dbox(cy, 66, "Переписуване\n(не незмінна історія)?"))
    f.append(yes(cy)); f.append(arrow(356, cy, 528, cy))
    f.append(leaf(cy, 62, "MIGRATE IN-PLACE\nexpand → backfill → contract (zone→tariff_zone)",
                  GREENFILL, FIELD, FIELD))
    f.append(no(cy + 62)); f.append(arrow(250, cy + 33, 250, cy + 90))

    # фінал «ні» → schema-on-read
    f.append(fitbox(90, 694, 320, 66,
                    "SCHEMA-ON-READ\nверсіонуй записи, декодуй на читанні\n(незмінна історія)",
                    size=13, fill=BLUEFILL, stroke=NEG, bold=True, color=NEG))

    # банер: контроль над боками задає лише ширину вікна
    f.append(fitbox(430, 700, 690, 56,
                    "Контролюєш обидва боки? → лише ШИРИНА вікна:\nТАК коротке · НІ довге + forward-сумісність",
                    size=13, fill=YELL, stroke=YSTROKE, bold=True, sw=2))

    render(os.path.join(IMG, "triage-dispatch.svg"), W, H, *f,
           title="Класифікатор змін: перше «так» дає стратегію")


# ───────── Фіг. 6: два годинники retire (вставка proj-dh-change-triage) ─────────
def fig_retire_two_clocks():
    W, H = 1180, 620
    f = []
    BLUEROW = "#dfe7f5"
    NOWX = 890

    # лінія «зараз» через обидва годинники
    f.append(line(NOWX, 100, NOWX, 468, color=INK, sw=2))
    f.append(text(NOWX, 92, "зараз", size=12, color=INK, bold=True))

    # ── ВЕРХ: годинник живого трафіку ──
    f.append(text(90, 96, "Годинник живого трафіку schema:1",
                  size=14, color=INK, bold=True, anchor="start"))
    axisY = 210
    f.append(line(150, axisY, 905, axisY, color=INK, sw=2))
    for bx, bh in ((180, 90), (230, 72), (280, 54), (330, 38), (380, 22), (430, 10)):
        f.append(rect(bx, axisY - bh, 34, bh, fill=BLUEROW, stroke=NEG, sw=1.2, rx=2))
    f.append(line(468, 116, 468, axisY + 4, color=MUTED, sw=1.4, dash="4 4"))
    f.append(text(430, 108, "останній живий schema:1-запит",
                  size=11.5, color=MUTED, bold=True, anchor="start"))
    f.append(text(640, axisY - 8, "нуль трафіку", size=12, color=MUTED, italic=True))
    f.append(text(505, axisY + 30, "наївний гейт бачить нуль → «зелено, прибирай декодер»",
                  size=12, color=POS, bold=True, anchor="start"))

    # ── НИЗ: годинник збереження історії ──
    f.append(text(90, 300, "Годинник збереження історії (retention)",
                  size=14, color=INK, bold=True, anchor="start"))
    barY, barH = 322, 60
    f.append(rect(150, barY, 750, barH, fill=GREENFILL, stroke=FIELD, sw=1.4, rx=8))
    f.append(text(600, barY - 8, "вікно retention — усе це ще можна перечитати",
                  size=12, color=FIELD, bold=True))
    for ry in (barY + 12, barY + 24, barY + 36):
        f.append(rect(168, ry, 44, 9, fill=BLUEROW, stroke=NEG, sw=1.1, rx=2))
    f.append(text(560, barY + 40, "перерахунок / lineage читає стару історію",
                  size=11.5, color=POS, bold=True))
    f.append(arrow(872, barY + 54, 220, barY + 54, color=POS, sw=1.9))
    f.append(line(190, barY + barH, 190, barY + barH + 20, color=MUTED, sw=1.2, dash="4 4"))
    f.append(mtext(190, barY + barH + 36,
                   ["найстаріший збережений schema:1-рядок", "— ще в межах retention"],
                   size=11, color=INK, bold=True))
    f.append(text(150, 470, "правильний гейт бачить досяжний рядок → «червоно, декодер ще потрібен»",
                  size=12, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(IMG, "retire-two-clocks.svg"), W, H, *f,
           title="Два годинники: жива тиша ≠ порожня історія")


if __name__ == "__main__":
    fig_decision_funnel()
    fig_coexistence_window()
    fig_strategy_matrix()
    fig_compat_lineage()
    fig_triage_dispatch()
    fig_retire_two_clocks()
    print("OK: decision-funnel, coexistence-window, strategy-matrix, compat-lineage, "
          "triage-dispatch, retire-two-clocks")
