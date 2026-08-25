# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

HL = "#eafaf0"   # заливка виділеного рядка / моделі


# ── 1. Анатомія: рядок таблиці ↔ об'єкт, що вміє діяти ──────────────────────
def fig_anatomy():
    W, H = 1000, 470
    f = []
    f.append(text(W / 2, 32, "Active Record: об'єкт — це рядок, який уміє діяти", size=17, bold=True))

    # ── ЛІВОРУЧ: таблиця orders ──
    TX, TW = 40, 390
    f.append(text(TX + TW / 2, 68, "таблиця orders у базі", size=12.5, color=MUTED))

    cols = [("id", 55), ("customer_id", 125), ("total", 90), ("status", 120)]
    rows = [
        (41, "c-77", "350", "new", False),
        (42, "c-19", "1200", "paid", True),
        (43, "c-19", "90", "shipped", False),
    ]
    HDR_Y, HDR_H, ROW_H = 84, 30, 34
    BODY_Y = HDR_Y + HDR_H

    f.append(rect(TX, HDR_Y, TW, HDR_H, fill=FILL, stroke=LINE, sw=1.5, rx=0))
    f.append(rect(TX, BODY_Y, TW, ROW_H * len(rows), fill=BG, stroke=LINE, sw=1.5, rx=0))
    # виділений рядок — під текстом
    for i, r in enumerate(rows):
        if r[4]:
            f.append(rect(TX, BODY_Y + i * ROW_H, TW, ROW_H, fill=HL, stroke=FIELD, sw=2.5, rx=0))

    # роздільники колонок
    xs = [TX]
    for _, w in cols:
        xs.append(xs[-1] + w)
    for x in xs[1:-1]:
        f.append(line(x, HDR_Y, x, BODY_Y + ROW_H * len(rows), color=MUTED, sw=1))
    # роздільники рядків
    for i in range(1, len(rows)):
        f.append(line(TX, BODY_Y + i * ROW_H, TX + TW, BODY_Y + i * ROW_H, color=MUTED, sw=1))

    centers = [(xs[i] + xs[i + 1]) / 2 for i in range(len(cols))]
    for c, (name, _) in zip(centers, cols):
        f.append(text(c, HDR_Y + 20, name, size=12, color=MUTED, bold=True))
    for i, r in enumerate(rows):
        y = BODY_Y + i * ROW_H + 22
        for c, val in zip(centers, r[:4]):
            f.append(text(c, y, str(val), size=12, color=INK))

    # двигун патерну — під таблицею
    f.append(rect(TX, 250, TW, 96, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
    f.append(text(TX + TW / 2, 276, "увесь двигун — один if у save():", size=12, color=INK, bold=True))
    f.append(text(TX + TW / 2, 302, "немає ключа → рядка ще немає → INSERT", size=11.5, color=INK))
    f.append(text(TX + TW / 2, 326, "є ключ → рядок існує → UPDATE", size=11.5, color=INK))

    # ── ПРАВОРУЧ: об'єкт ──
    CX, CW = 570, 390
    f.append(text(CX + CW / 2, 68, "об'єкт Order у пам'яті програми", size=12.5, color=MUTED))
    f.append(rect(CX, 84, CW, 352, fill=BG, stroke=FIELD, sw=2.2, rx=10))
    f.append(rect(CX, 84, CW, 34, fill=FILL, stroke=FIELD, sw=1.5, rx=10))
    f.append(text(CX + CW / 2, 106, "Order — об'єкт рядка id = 42", size=13, color=INK, bold=True))

    f.append(text(CX + 15, 140, "поля = колонки того самого рядка", size=11.5, color=MUTED, anchor="start"))
    f.append(rect(CX + 15, 150, 360, 96, fill=BG, stroke=MUTED, sw=1.2, rx=6))
    for i, s in enumerate(['id = 42', 'customerId = "c-19"', 'total = 1200', 'status = "paid"']):
        f.append(text(CX + 32, 172 + i * 22, s, size=12.5, color=INK, anchor="start"))

    f.append(text(CX + 15, 270, "доступ до бази — у самому класі", size=11.5, color=MUTED, anchor="start"))
    f.append(rect(CX + 15, 278, 360, 78, fill=BG, stroke=MUTED, sw=1.2, rx=6))
    for i, s in enumerate(['Order.find(42)', 'save() → INSERT або UPDATE', 'delete()']):
        f.append(text(CX + 32, 302 + i * 22, s, size=12.5, color=POS, anchor="start"))

    f.append(text(CX + 15, 380, "предметне правило — на тих самих даних", size=11.5, color=MUTED, anchor="start"))
    f.append(rect(CX + 15, 388, 360, 34, fill=HL, stroke=FIELD, sw=1.6, rx=6))
    f.append(text(CX + CW / 2, 410, 'canCancel() → true, бо status = "paid"', size=12, color=INK))

    # ── СТРІЛКИ між рядком і об'єктом ──
    f.append(arrow(TX + TW + 4, 157, CX - 4, 157, color=MUTED, sw=1.8))
    f.append(arrow(CX - 4, 176, TX + TW + 4, 176, color=MUTED, sw=1.8))
    f.append(text(500, 145, "find() → SELECT", size=11, color=MUTED))
    f.append(text(500, 198, "save() → UPDATE", size=11, color=MUTED))

    render(os.path.join(OUT, 'active-record-anatomy.svg'), W, H, *f)


# ── 2. Active Record ↔ Data Mapper: різниця в одній стрілці ─────────────────
def fig_vs_mapper():
    W, H = 980, 430
    f = []
    f.append(text(W / 2, 32, "Різниця — в тому, куди дивиться одна стрілка", size=17, bold=True))

    # ── ЛІВОРУЧ: Active Record ──
    L = 260
    f.append(text(L, 62, "ACTIVE RECORD", size=14, color=FIELD, bold=True))
    f.append(text(L, 84, "об'єкт ЗНАЄ про базу", size=11.5, color=MUTED, italic=True))
    f.append(rect(L - 140, 98, 280, 40, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(L, 123, "код застосунку", size=12.5, color=INK))
    f.append(arrow(L, 138, L, 168, color=MUTED, sw=1.8))
    f.append(rect(L - 170, 168, 340, 100, fill=HL, stroke=FIELD, sw=2.2, rx=10))
    f.append(text(L, 194, "Order", size=13.5, color=INK, bold=True))
    f.append(text(L, 218, "дані рядка + предметні правила", size=11.5, color=INK))
    f.append(text(L, 240, "+ find() / save() / delete()", size=11.5, color=POS))
    f.append(arrow(L, 268, L, 302, color=POS, sw=2))
    f.append(rect(L - 110, 302, 220, 40, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(L, 327, "таблиця orders", size=12.5, color=INK))
    f.append(text(L, 372, "стрілка виходить із самого об'єкта:", size=11.5, color=MUTED))
    f.append(text(L, 392, "нуль зайвих класів — і нуль межі", size=11.5, color=MUTED))

    # ── роздільна вісь ──
    f.append(line(500, 56, 500, 400, color=MUTED, sw=1.2, dash="5 5"))

    # ── ПРАВОРУЧ: Data Mapper ──
    R = 740
    f.append(text(R, 62, "DATA MAPPER", size=14, color=NEG, bold=True))
    f.append(text(R, 84, "об'єкт про базу не знає нічого", size=11.5, color=MUTED, italic=True))
    f.append(rect(R - 140, 98, 280, 40, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(R, 123, "код застосунку", size=12.5, color=INK))
    f.append(arrow(R, 138, R, 168, color=MUTED, sw=1.8))
    f.append(rect(600, 168, 200, 100, fill=FILL, stroke=NEG, sw=2.2, rx=10))
    f.append(text(700, 196, "OrderMapper", size=13, color=INK, bold=True))
    f.append(text(700, 222, "знає і про об'єкт,", size=11.5, color=INK))
    f.append(text(700, 244, "і про таблицю", size=11.5, color=INK))
    f.append(rect(828, 182, 128, 72, fill=BG, stroke=NEG, sw=1.6, rx=8))
    f.append(text(892, 208, "Order", size=13, color=INK, bold=True))
    f.append(text(892, 232, "дані + правила", size=11, color=INK))
    f.append(arrow(802, 218, 826, 218, color=NEG, sw=1.8))
    f.append(arrow(R, 268, R, 302, color=NEG, sw=2))
    f.append(rect(620, 302, 280, 40, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(760, 327, "таблиця orders", size=12.5, color=INK))
    # від об'єкта до бази стрілки НЕМАЄ
    f.append(line(892, 254, 892, 302, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(884, 270, 900, 286, color=POS, sw=2.4))
    f.append(line(900, 270, 884, 286, color=POS, sw=2.4))
    f.append(text(R, 372, "переклад винесено в окремий клас:", size=11.5, color=MUTED))
    f.append(text(R, 392, "об'єкт живе без бази — але за плату", size=11.5, color=MUTED))

    render(os.path.join(OUT, 'ar-vs-mapper.svg'), W, H, *f)


# ── 3. Дві ціни: майже нуль на старті проти плати наперед ───────────────────
def fig_cost():
    W, H = 900, 470
    X0, XW, Y0, YS = 110.0, 700.0, 380.0, 280.0
    f = []
    f.append(text(W / 2, 32, "Дві ціни, що ростуть по-різному", size=17, bold=True))

    def ar(t):
        return 0.03 + 1.6 * (t ** 2.6)

    def dm(t):
        return 0.45 + 0.25 * t

    def px(t):
        return X0 + t * XW

    def py(v):
        return Y0 - v * YS

    def curve(fn, t1, color, sw=2.4, n=64):
        out = []
        for i in range(n):
            a, b = t1 * i / n, t1 * (i + 1) / n
            out.append(line(px(a), py(fn(a)), px(b), py(fn(b)), color=color, sw=sw))
        return out

    # осі
    f.append(arrow(X0, Y0, X0 + XW + 28, Y0, color=INK, sw=1.6))
    f.append(arrow(X0, Y0, X0, 78, color=INK, sw=1.6))
    f.append(text(100, 66, "↑ сумарна ціна: код + тести + зміни", size=12, color=MUTED, anchor="start"))
    f.append(text(470, 428, "складність предметної логіки →", size=12.5, color=INK))
    f.append(text(470, 450, "наскільки форма об'єктів відходить від форми таблиць",
                  size=11.5, color=MUTED, italic=True))

    # криві (Active Record обриваємо там, де вилітає за поле)
    t_top = 0.83
    f.extend(curve(dm, 1.0, NEG))
    f.extend(curve(ar, t_top, POS))

    # точка, де ціни зрівнялися (шукаємо навпіл)
    lo, hi = 0.0, t_top
    for _ in range(60):
        mid = (lo + hi) / 2
        if ar(mid) < dm(mid):
            lo = mid
        else:
            hi = mid
    tc = (lo + hi) / 2
    f.append(line(px(tc), Y0, px(tc), py(ar(tc)) - 10, color=MUTED, sw=1.2, dash="4 4"))
    f.append(circle(px(tc), py(ar(tc)), 5, fill=BG, stroke=POS, sw=2.2))
    f.append(text(505, 178, "точка, де ціни зрівнялися", size=11.5, color=INK, anchor="end"))
    f.append(arrow(512, 182, px(tc) - 12, py(ar(tc)) - 6, color=MUTED, sw=1.4))

    # підписи кривих
    f.append(text(250, 336, "Active Record", size=12.5, color=POS, bold=True))
    f.append(text(215, 224, "Data Mapper", size=12.5, color=NEG, bold=True))

    # зони
    f.append(text(330, 286, "CRUD, форми над даними —", size=12, color=MUTED))
    f.append(text(330, 306, "Active Record дешевший", size=12, color=MUTED))
    f.append(text(766, 148, "багата модель —", size=12, color=MUTED))
    f.append(text(766, 168, "мапер дешевший", size=12, color=MUTED))

    render(os.path.join(OUT, 'ar-vs-mapper-cost.svg'), W, H, *f)


# ── 4. Історія імені: практика без назви → ім'я → розкол надвоє ─────────────
def fig_naming_timeline():
    W, H = 1180, 840
    AX = 590                      # вісь розколу
    f = []
    f.append(text(W / 2, 34, "Ім'я приходить пізно — і відразу розколює світ надвоє",
                  size=17, bold=True))

    # ── ДО ІМЕНІ: вісь ще не існує, рамки перекривають усю ширину ──
    f.append(text(100, 68, "ДО ІМЕНІ · практика є, назви немає — і сперечатися нема про що",
                  size=12, color=MUTED, anchor="start", italic=True))

    def wide(y, h, year, head, sub, size=13, fill=FILL, stroke=MUTED, sw=1.4):
        f.append(rect(100, y, 980, h, fill=fill, stroke=stroke, sw=sw, rx=8))
        f.append(text(124, y + 34, year, size=14, color=INK, anchor="start", bold=True))
        f.append(text(290, y + 22, head, size=size, color=INK, anchor="start", bold=True))
        f.append(text(290, y + 46, sub, size=11.5, color=MUTED, anchor="start"))

    wide(84, 56, "1984",
         "Коупленд і Маєр, «Making Smalltalk a Database System» (SIGMOD)",
         "розрив між об'єктами й таблицями стає предметом дослідження")
    wide(152, 56, "1995",
         "Браун і Вайтенек, «Crossing Chasms» на PLoP'95",
         "перша мова патернів про той самий розрив — територію нанесено на карту")

    # ── РОЗВИЛКА: тут народжується слово ──
    f.append(rect(100, 224, 980, 64, fill=HL, stroke=FIELD, sw=2.4, rx=8))
    f.append(text(124, 262, "5 листопада 2002", size=14, color=INK, anchor="start", bold=True))
    f.append(text(290, 248, "Мартін Фаулер, «Patterns of Enterprise Application Architecture»",
                  size=13.5, color=INK, anchor="start", bold=True))
    f.append(text(290, 274, "два імені народжуються поруч: Active Record і Data Mapper — і звичка стає вибором",
                  size=12, color=INK, anchor="start"))

    # ── вісь розколу починається ТІЛЬКИ після імені ──
    f.append(line(AX, 292, AX, 800, color=MUTED, sw=2))

    f.append(text(554, 326, "ЯК ІМ'Я СТАВАЛО ЗАМОВЧУВАННЯМ", size=13.5, color=POS,
                  anchor="end", bold=True))
    f.append(text(626, 326, "ЯК ІМ'Я СТАВАЛО МІШЕННЮ", size=13.5, color=NEG,
                  anchor="start", bold=True))

    def pill(y, s):
        f.append(rect(AX - 36, y - 14, 72, 28, fill=BG, stroke=MUTED, sw=1.5, rx=14))
        f.append(text(AX, y + 5, s, size=12.5, color=INK, bold=True))

    def box(side, y, h, lines, color):
        x = 118 if side == "L" else 632
        f.append(rect(x, y, 430, h, fill=BG, stroke=color, sw=1.8, rx=8))
        for i, (s, sz, col, bold) in enumerate(lines):
            f.append(text(x + 18, y + 24 + i * 22, s, size=sz, color=col,
                          anchor="start", bold=bold))

    # 2004 — бум і глум починаються ОДНОГО року
    pill(400, "2004")
    box("L", 356, 88, [
        ("лютий · Basecamp виходить у світ", 12, INK, False),
        ("24 липня · Rails 0.5.0: «The end of vaporware!»", 12.5, INK, True),
        ("README дослівно цитує означення Фаулера", 11.5, MUTED, False),
    ], POS)
    box("R", 356, 88, [
        ("Тед Невард на TechEd (BOF):", 12, INK, False),
        ("«ORM — це В'єтнам інформатики»", 12.5, INK, True),
        ("того самого року, що й Rails 0.5.0", 11.5, MUTED, False),
    ], NEG)

    # 2005 — рік, коли бум їде сам
    pill(493, "2005")
    box("L", 460, 66, [
        ("13 грудня · Rails 1.0", 12.5, INK, True),
        ("Jolt-нагорода · «Hacker of the Year»", 11.5, MUTED, False),
    ], POS)

    # 2006 — дві мови, той самий рік, протилежний вибір
    pill(586, "2006")
    box("L", 542, 88, [
        ("13 квітня · Doctrine для PHP", 12.5, INK, True),
        ("Rails-підхід переходить у чужу мову:", 11.5, MUTED, False),
        ("Active Record як очевидний вибір", 11.5, MUTED, False),
    ], POS)
    box("R", 542, 88, [
        ("SQLAlchemy: Баєр свідомо будує", 12, INK, False),
        ("Data Mapper для Python", 12.5, INK, True),
        ("26 червня · есе Неварда «В'єтнам»", 11.5, MUTED, False),
    ], NEG)

    # 2010 — самовирок
    pill(679, "2010")
    box("R", 646, 66, [
        ("21 грудня · Doctrine 2", 12.5, INK, True),
        ("той самий проєкт викидає свій Active Record", 11.5, MUTED, False),
    ], NEG)

    # 2011–12 — присуд фреймворкові
    pill(761, "2011–12")
    box("R", 728, 66, [
        ("Мартін · Вінн · Ґрімм", 12.5, INK, True),
        ("«фреймворк — це не архітектура»", 12, MUTED, False),
    ], NEG)

    render(os.path.join(OUT, 'active-record-naming-timeline.svg'), W, H, *f)


# ── Втрачене оновлення і лічильник версій ───────────────────────────────────
def fig_lost_update():
    W, H = 1040, 790
    AX, DX, BX = 120.0, 520.0, 920.0     # смуги: клієнт A, рядок у базі, клієнт B
    LC, RC = 320.0, 720.0                # осі підписів ліворуч і праворуч
    f = []
    f.append(text(W / 2, 32, "Втрачене оновлення — і як його ловить лічильник версій",
                  size=17, bold=True))

    def lanes(y_top, y_bot):
        return [line(AX, y_top, AX, y_bot, color=MUTED, sw=1.2, dash="4 4"),
                line(BX, y_top, BX, y_bot, color=MUTED, sw=1.2, dash="4 4"),
                line(DX, y_top, DX, y_bot, color=FIELD, sw=2)]

    def heads(y):
        return [text(AX, y, "Клієнт A", size=13, color=INK, bold=True),
                text(DX, y, "рядок orders id = 42", size=13, color=FIELD, bold=True),
                text(BX, y, "Клієнт B", size=13, color=INK, bold=True)]

    def step(y, side, label, verdict, vcolor):
        """side='A' — стрілка зліва направо; side='B' — справа наліво."""
        out = []
        rows = label if isinstance(label, list) else [label]
        cx = LC if side == "A" else RC
        out.append(mtext(cx, y - 16 if len(rows) == 1 else y - 32, rows, size=12, color=INK))
        if side == "A":
            out.append(arrow(AX + 10, y, DX - 10, y, color=MUTED, sw=1.7))
            out.append(text(DX + 16, y + 4, verdict, size=12, color=vcolor,
                            anchor="start", bold=True))
        else:
            out.append(arrow(BX - 10, y, DX + 10, y, color=MUTED, sw=1.7))
            out.append(text(DX - 16, y + 4, verdict, size=12, color=vcolor,
                            anchor="end", bold=True))
        return out

    # ══ Панель 1: без лічильника ══
    f.append(text(W / 2, 78, "БЕЗ лічильника: save() пише лише змінену колонку — і цього мало",
                  size=13.5, color=POS, bold=True))
    f.extend(lanes(124, 356))
    f.extend(heads(112))
    f.extend(step(160, "A", "SELECT → бачить total = 100", "віддав рядок", MUTED))
    f.extend(step(220, "B", "SELECT → бачить total = 100", "віддав рядок", MUTED))
    f.extend(step(280, "A", ["UPDATE orders SET total = 110", "WHERE id = 42"],
                  "1 рядок ✓", FIELD))
    f.extend(step(340, "B", ["UPDATE orders SET total = 120", "WHERE id = 42"],
                  "1 рядок ✓", POS))
    f.append(text(W / 2, 386, "у базі total = 120 — робота A зникла, і ніхто не скаржився",
                  size=13, color=POS, bold=True))

    # ══ Панель 2: з лічильником ══
    f.append(text(W / 2, 438, "З лічильником: у WHERE додано ту версію, яку читали",
                  size=13.5, color=FIELD, bold=True))
    f.extend(lanes(484, 716))
    f.extend(heads(472))
    f.extend(step(520, "A", "SELECT → total = 100, lock_version = 0", "віддав рядок", MUTED))
    f.extend(step(580, "B", "SELECT → total = 100, lock_version = 0", "віддав рядок", MUTED))
    f.extend(step(640, "A", ["UPDATE orders SET total = 110, lock_version = 1",
                             "WHERE id = 42 AND lock_version = 0"], "1 рядок ✓", FIELD))
    f.extend(step(700, "B", ["UPDATE orders SET total = 120, lock_version = 1",
                             "WHERE id = 42 AND lock_version = 0"],
                  "0 рядків → StaleObject", POS))
    f.append(text(W / 2, 748,
                  "у базі total = 110 — B спіймано на застарілому читанні й відправлено перечитати",
                  size=13, color=FIELD, bold=True))

    render(os.path.join(OUT, 'ar-lost-update.svg'), W, H, *f)


# ── Брудний набір і лічильник тягнуть у різні боки ──────────────────────────
def fig_dirty_vs_version():
    W, H = 1020, 530
    f = []
    f.append(text(W / 2, 32, "Безкоштовного обіду немає: чотири клітини однієї таблиці",
                  size=17, bold=True))
    f.append(text(W / 2, 58, "два клієнти одночасно правлять рядок id = 42",
                  size=12.5, color=MUTED, italic=True))

    C1X, C2X, CW = 300.0, 640.0, 320.0
    R1Y, R2Y, RH = 152.0, 306.0, 130.0

    f.append(mtext(C1X + CW / 2, 104, ["A міняє status, B міняє total", "(РІЗНІ колонки)"],
                   size=12.5, color=INK, bold=True))
    f.append(mtext(C2X + CW / 2, 104, ["обидва міняють total", "(ТА САМА колонка)"],
                   size=12.5, color=INK, bold=True))
    f.append(mtext(152, R1Y + RH / 2 - 8, ["save() пише лише", "змінені колонки"],
                   size=12.5, color=INK, bold=True))
    f.append(mtext(152, R2Y + RH / 2 - 8, ["+ лічильник версій", "на РЯДОК"],
                   size=12.5, color=INK, bold=True))

    def cell(x, y, mark, head, body, color, fill):
        out = [rect(x, y, CW, RH, fill=fill, stroke=color, sw=2, rx=8)]
        out.append(text(x + 26, y + 36, mark, size=19, color=color, bold=True))
        out.append(text(x + CW / 2 + 12, y + 36, head, size=13, color=color, bold=True))
        out.append(mtext(x + CW / 2, y + 66, body, size=11.5, color=INK))
        return out

    f.extend(cell(C1X, R1Y, "✓", "обидва доїхали",
                  ["різні колонки — різні UPDATE,", "вони просто не зустрілися"],
                  FIELD, "#eafaf0"))
    f.extend(cell(C2X, R1Y, "✗", "тихо втрачене оновлення",
                  ["у базі 20 — десятку A стерто,", "жодної помилки ніхто не бачив"],
                  POS, "#fdecea"))
    f.extend(cell(C1X, R2Y, "✗", "ХИБНИЙ конфлікт",
                  ["B відхилено, хоч воно й", "не торкалося status"],
                  POS, "#fdecea"))
    f.extend(cell(C2X, R2Y, "✓", "спіймано",
                  ["0 рядків → StaleObject,", "B перечитує й вирішує наново"],
                  FIELD, "#eafaf0"))

    f.append(mtext(W / 2, 474, [
        "Лічильник рахує РЯДОК, а не колонку: він купує безпеку в правій колонці",
        "ціною хибних конфліктів у лівій. Обидві клітини «✓» одночасно не вмикаються.",
    ], size=12.5, color=INK))

    render(os.path.join(OUT, 'ar-dirty-vs-version.svg'), W, H, *f)


# ── N+1: лінійне складання і розтин одного походу ────────────────────────────
def fig_n1_chain():
    W, H = 1220, 630
    f = []
    f.append(text(W / 2, 32, "N+1 — це цикл, у якому одиниця роботи — похід у базу",
                  size=17, bold=True))
    f.append(text(W / 2, 58, "N = 100 замовлень · один похід ≈ 1.3 мс · масштаб однаковий в обох смугах",
                  size=12.5, color=MUTED, italic=True))

    PX, X0 = 30.0, 60.0          # пікселів на мілісекунду
    HOP = "#eaf0fd"

    # ── смуга 1: N+1 ──
    f.append(text(X0, 92, "N+1 — сто один похід, кожен чекає, поки повернеться попередній",
                  size=12.5, color=INK, anchor="start", bold=True))
    y1, BH = 104, 44
    x = X0
    w0 = 2.0 * PX
    f.append(rect(x, y1, w0, BH, fill=FILL, stroke=INK, sw=1.5, rx=3))
    f.append(text(x + w0 / 2, y1 + 28, "1", size=13, color=INK, bold=True))
    x += w0 + 5
    for _ in range(12):
        f.append(rect(x, y1, 1.3 * PX, BH, fill=HOP, stroke=NEG, sw=1.2, rx=3))
        x += 1.3 * PX + 3
    bx, bw = x + 4, 180.0
    f.append(rect(bx, y1, bw, BH, fill=BG, stroke=MUTED, sw=1.2, rx=3))
    f.append(text(bx + bw / 2, y1 + 28, "⋯ ще 89 ⋯", size=12.5, color=MUTED))
    xe = bx + bw

    f.append(line(X0, 162, xe, 162, color=MUTED, sw=1.4))
    f.append(line(X0, 157, X0, 167, color=MUTED, sw=1.4))
    f.append(line(xe, 157, xe, 167, color=MUTED, sw=1.4))
    f.append(text((X0 + xe) / 2, 186, "101 похід · разом ≈ 131 мс", size=13.5, color=NEG, bold=True))
    f.append(text(xe + 32, 122, "101 × 1.3 мс", size=13, color=NEG, anchor="start", bold=True))
    f.append(text(xe + 32, 144, "лінійно за N", size=12, color=MUTED, anchor="start"))

    # ── смуга 2: пакет ──
    f.append(text(X0, 232, "Пакет — два походи, скільки б не було замовлень",
                  size=12.5, color=INK, anchor="start", bold=True))
    y2 = 244
    x = X0
    f.append(rect(x, y2, w0, BH, fill=FILL, stroke=INK, sw=1.5, rx=3))
    f.append(text(x + w0 / 2, y2 + 28, "1", size=13, color=INK, bold=True))
    x += w0 + 5
    w1 = 2.6 * PX
    f.append(rect(x, y2, w1, BH, fill=FILL, stroke=FIELD, sw=1.8, rx=3))
    f.append(text(x + w1 / 2, y2 + 28, "2", size=13, color=INK, bold=True))
    xe2 = x + w1

    f.append(line(X0, 302, xe2, 302, color=MUTED, sw=1.4))
    f.append(line(X0, 297, X0, 307, color=MUTED, sw=1.4))
    f.append(line(xe2, 297, xe2, 307, color=MUTED, sw=1.4))
    f.append(text((X0 + xe2) / 2, 326, "2 походи · ≈ 4.6 мс", size=13.5, color=FIELD, bold=True))
    f.append(mtext(xe2 + 40, 266, [
        "той самий набір даних опиняється в пам'яті —",
        "але дріт перетнули двічі, а не сто один раз",
    ], size=12.5, color=INK, anchor="start"))

    # тінь: докуди тягнеться смуга 1
    f.append(line(xe, y1 + BH + 26, xe, y2 + BH + 4, color=MUTED, sw=1.2, dash="5 5"))

    # ── розтин одного походу ──
    f.append(line(40, 352, W - 40, 352, color=MUTED, sw=1, dash="6 6"))
    f.append(text(W / 2, 386, "Розтин одного походу: 1.3 мс — і лише 4% з них база справді працює",
                  size=15, bold=True))

    BX, SC = 80.0, 704.0         # px на мілісекунду в розтині
    by, bh2 = 440.0, 52.0
    segs = [(0.35, "#eaf0fd", NEG), (0.80, FILL, MUTED), (0.05, "#fdecea", POS), (0.05, "#eafaf0", FIELD)]
    x = BX
    marks = []
    for ms, fill_, st in segs:
        w = ms * SC
        f.append(rect(x, by, w, bh2, fill=fill_, stroke=st, sw=1.6, rx=0))
        marks.append((x, x + w))
        x += w
    xdb0, xdb1 = marks[2][0], marks[3][1]

    f.append(text((marks[0][0] + marks[0][1]) / 2, 518,
                  "застосунок: побудова SQL, драйвер,", size=11.5, color=INK))
    f.append(text((marks[0][0] + marks[0][1]) / 2, 538,
                  "syscall, розбір відповіді — 0.35 мс", size=11.5, color=INK))
    f.append(text((marks[1][0] + marks[1][1]) / 2, 518,
                  "дріт: похід туди й назад між зонами доступності — 0.80 мс",
                  size=11.5, color=INK))
    f.append(text((marks[1][0] + marks[1][1]) / 2, 538,
                  "(вимірювання по 28 регіонах: від 0.39 до 2.42 мс)",
                  size=11.5, color=MUTED, italic=True))

    f.append(line(xdb0, 430, xdb1, 430, color=FIELD, sw=1.6))
    f.append(line(xdb0, 430, xdb0, 440, color=FIELD, sw=1.6))
    f.append(line(xdb1, 430, xdb1, 440, color=FIELD, sw=1.6))
    f.append(arrow(xdb1 + 4, 428, xdb1 + 26, 418, color=MUTED, sw=1.3))
    f.append(mtext(xdb1 + 32, 410, ["база: 0.10 мс", "план 0.05 + вибірка 0.05"],
                   size=11.5, color=INK, anchor="start"))

    f.append(text(W / 2, 578,
                  "Корисної роботи — 0.05 мс: спуск по B-дереву й читання рядка з кеша. "
                  "Решта 96% — конверт.",
                  size=13, color=INK, bold=True))
    f.append(text(W / 2, 602,
                  "Один похід коштує стільки ж, скільки ≈ 400 зайвих рядків у відповіді: "
                  "платять за конверт, а не за лист.",
                  size=12.5, color=MUTED))

    render(os.path.join(OUT, 'n1-chain.svg'), W, H, *f)


# ── N+1 і пул з'єднань: стеля, поділена на N ─────────────────────────────────
def fig_n1_pool():
    import math
    W, H = 1020, 520
    X0, XW, Y0, YT = 110.0, 800.0, 420.0, 100.0
    LO, HI, RMAX = 10.0, 2000.0, 400.0
    f = []
    f.append(text(W / 2, 32, "Пул: N+1 не сповільнює систему — він опускає її стелю",
                  size=17, bold=True))

    def px(lam):
        return X0 + XW * (math.log10(lam) - math.log10(LO)) / (math.log10(HI) - math.log10(LO))

    def py(ms):
        return Y0 - min(ms, RMAX) / RMAX * (Y0 - YT)

    # осі
    f.append(arrow(X0, Y0, X0 + XW + 26, Y0, color=INK, sw=1.6))
    f.append(arrow(X0, Y0, X0, YT - 14, color=INK, sw=1.6))
    f.append(text(105, 72, "↑ час відповіді, мс", size=12, color=MUTED, anchor="start"))
    f.append(text(510, 470, "темп запитів λ, запитів/с (логарифмічна шкала) →",
                  size=12.5, color=INK))
    for v in (0, 100, 200, 300, 400):
        f.append(line(X0 - 5, py(v), X0, py(v), color=INK, sw=1.2))
        f.append(text(X0 - 12, py(v) + 4, str(v), size=11.5, color=MUTED, anchor="end"))
    for v in (10, 30, 100, 300, 1000, 2000):
        f.append(line(px(v), Y0, px(v), Y0 + 5, color=INK, sw=1.2))
        f.append(text(px(v), Y0 + 22, str(v), size=11.5, color=MUTED))

    def curve(Whold, P, color):
        lmax = P / (Whold / 1000.0)
        out = []
        prev = None
        n = 400
        for i in range(n + 1):
            lam = LO * (HI / LO) ** (i / n)
            if lam >= lmax * 0.999:
                break
            r = Whold / (1 - lam / lmax)
            if r > RMAX:
                break
            cur = (px(lam), py(r))
            if prev:
                out.append(line(prev[0], prev[1], cur[0], cur[1], color=color, sw=2.6))
            prev = cur
        out.append(line(px(lmax), Y0, px(lmax), YT - 6, color=color, sw=1.6, dash="5 5"))
        return out, lmax

    a, lmax_a = curve(131.0, 5, NEG)
    b, lmax_b = curve(4.6, 5, FIELD)
    f.extend(b)
    f.extend(a)

    f.append(text(px(lmax_a), 88, "стеля ≈ 38 зап/с", size=12, color=NEG, bold=True))
    f.append(text(px(lmax_b), 88, "стеля ≈ 1090 зап/с", size=12, color=FIELD, bold=True))

    # легенда
    f.append(rect(392, 120, 400, 76, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    f.append(line(408, 146, 440, 146, color=NEG, sw=2.6))
    f.append(text(450, 150, "N+1: з'єднання зайняте 131 мс", size=12, color=INK, anchor="start"))
    f.append(line(408, 174, 440, 174, color=FIELD, sw=2.6))
    f.append(text(450, 178, "пакет: з'єднання зайняте 4.6 мс", size=12, color=INK, anchor="start"))

    box = textbox(560, 285, [
        "Закон Літтла: L = λ · W",
        "пул із P з'єднань вичерпано, коли L = P → λₘₐₓ = P / W",
        "N+1 множить W на (N+1) — і ділить стелю на стільки ж",
    ], size=12, pad=12, fill=BG, stroke=MUTED, sw=1.4)[0]
    f.append(box)

    render(os.path.join(OUT, 'n1-pool.svg'), W, H, *f)


# ── Хвіст: рідкісне стає звичайним ───────────────────────────────────────────
def fig_n1_tail():
    W, H = 980, 500
    X0, XW, Y0, YT = 110.0, 780.0, 400.0, 90.0
    NMAX = 300.0
    f = []
    f.append(text(W / 2, 32, "Хвіст: N+1 перетворює рідкісне на звичайне", size=17, bold=True))
    f.append(text(W / 2, 58,
                  "p — шанс, що ОДИН запит вискочить за поріг; крива — шанс, що це станеться "
                  "бодай раз за сторінку",
                  size=12.5, color=MUTED, italic=True))

    def px(n):
        return X0 + XW * n / NMAX

    def py(q):
        return Y0 - q * (Y0 - YT)

    f.append(arrow(X0, Y0, X0 + XW + 26, Y0, color=INK, sw=1.6))
    f.append(arrow(X0, Y0, X0, YT - 14, color=INK, sw=1.6))
    f.append(text(105, 70, "↑ шанс, що сторінка зачепить бодай один повільний запит",
                  size=12, color=MUTED, anchor="start"))
    f.append(text(500, 442, "N — скільки рядків повернув перший запит →", size=12.5, color=INK))
    for v in (0, 50, 100, 150, 200, 250, 300):
        f.append(line(px(v), Y0, px(v), Y0 + 5, color=INK, sw=1.2))
        f.append(text(px(v), Y0 + 22, str(v), size=11.5, color=MUTED))
    for v, s in ((0, "0"), (0.25, "25%"), (0.5, "50%"), (0.75, "75%"), (1.0, "100%")):
        f.append(line(X0 - 5, py(v), X0, py(v), color=INK, sw=1.2))
        f.append(text(X0 - 12, py(v) + 4, s, size=11.5, color=MUTED, anchor="end"))

    def curve(p, color):
        out = []
        prev = None
        for i in range(0, 301, 2):
            q = 1 - (1 - p) ** (i + 1)
            cur = (px(i), py(q))
            if prev:
                out.append(line(prev[0], prev[1], cur[0], cur[1], color=color, sw=2.6))
            prev = cur
        return out

    f.extend(curve(0.001, NEG))
    f.extend(curve(0.01, POS))

    # позначка N ≈ 69 → 50%
    f.append(line(px(68), Y0, px(68), py(0.5), color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(X0, py(0.5), px(68), py(0.5), color=MUTED, sw=1.2, dash="4 4"))
    f.append(circle(px(68), py(0.5), 5, fill=BG, stroke=POS, sw=2.4))
    f.append(mtext(215, 150, [
        "N ≈ 69 — і вже половина",
        "сторінок ловить «рідкісний»",
        "повільний запит",
    ], size=12, color=INK, bold=True))
    f.append(arrow(250, 204, px(68) - 5, py(0.5) - 8, color=MUTED, sw=1.4))

    # позначка N = 100 → 64%
    q100 = 1 - 0.99 ** 101
    f.append(circle(px(100), py(q100), 5, fill=BG, stroke=POS, sw=2.4))
    f.append(mtext(620, 250, [
        "N = 100 → 64% сторінок",
        "Дін і Барросо міряли те саме на віялі",
        "зі 100 серверів: 63%",
    ], size=12, color=INK))
    f.append(arrow(500, 245, px(100) + 8, py(q100) + 5, color=MUTED, sw=1.4))

    f.append(text(770, 175, "p = 0.01 — один запит зі ста повільний", size=12, color=POS, bold=True))
    f.append(text(650, 385, "p = 0.001 — один із тисячі", size=12, color=NEG, bold=True))

    f.append(text(W / 2, 472,
                  "Половина сторінок ловить хвіст уже за N ≈ 0.693/p — і це не про збій, "
                  "а про справну систему.",
                  size=12.5, color=INK, bold=True))

    render(os.path.join(OUT, 'n1-tail.svg'), W, H, *f)


if __name__ == '__main__':
    fig_anatomy()
    fig_vs_mapper()
    fig_cost()
    fig_naming_timeline()
    fig_lost_update()
    fig_dirty_vs_version()
    fig_n1_chain()
    fig_n1_pool()
    fig_n1_tail()
    print("figures written to", OUT)
