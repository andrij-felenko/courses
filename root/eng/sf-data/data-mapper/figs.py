# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_mismatch():
    """Один об'єкт розкладається на рядок, ще два рядки в іншій таблиці — і нічого."""
    W, H = 980, 560
    frags = []

    frags.append(text(190, 46, "Один об'єкт у пам'яті", size=15, bold=True))
    frags.append(text(700, 46, "…і те, на що він розкладається в базі", size=15, bold=True))

    # ── лівий бік: живий об'єкт ────────────────────────────────────────────
    obj, ow, oh = textbox(190, 290, [
        "Order #7",
        "placedAt: 2026-07-14",
        "total: Money(2500.00, UAH)",
        "lines: [OrderLine, OrderLine]",
        "total() · cancel() — правила",
    ], size=13, pad=12, fill="#eaf3ff", stroke=NEG, sw=2, min_w=300)

    # ── правий бік: те, у що воно перетворюється ───────────────────────────
    head, hw, hh = textbox(700, 130, [
        "orders — один рядок",
        "id=7 · placed_at='2026-07-14'",
        "total_cents=250000 · currency='UAH'",
        "Money розклався на дві колонки",
    ], size=13, pad=12, min_w=300)

    lines_box, lw, lh = textbox(700, 300, [
        "order_lines — два рядки",
        "id=11 · order_id=7 · sku='A' · qty=2",
        "id=12 · order_id=7 · sku='B' · qty=1",
        "одне поле масиву стало таблицею",
    ], size=13, pad=12, min_w=300)

    none_box, nw, nh = textbox(700, 462, [
        "total() · cancel()",
        "у базі не існує нічого",
        "поведінку не зберігають",
    ], size=13, pad=12, fill="#fafafa", stroke=MUTED, min_w=300)

    # ── стрілки: віяло від об'єкта до трьох наслідків ──────────────────────
    ox_r = 190 + ow / 2
    frags.append(arrow(ox_r + 8, 262, 700 - hw / 2 - 8, 138, color=LINE))
    frags.append(arrow(ox_r + 8, 290, 700 - lw / 2 - 8, 300, color=LINE))
    frags.append(arrow(ox_r + 8, 320, 700 - nw / 2 - 8, 452, color=MUTED))

    frags += [obj, head, lines_box, none_box]
    return render(os.path.join(IMG, 'mismatch.svg'), W, H, *frags)


def fig_ar_vs_dm():
    """Два способи розв'язати ту саму невідповідність — і хто про кого знає."""
    W, H = 1000, 560
    frags = []

    # ── панель 1: Active Record ───────────────────────────────────────────
    frags.append(rect(30, 70, 460, 460, fill=BG, stroke=MUTED, sw=1.5, rx=10))
    frags.append(text(260, 52, "Active Record", size=16, bold=True))

    ar_obj, aw, ah = textbox(260, 200, [
        "Order",
        "правила домену: total(), cancel()",
        "+ доступ до бази: save(), find()",
        "знає таблицю orders і її колонки",
    ], size=13, pad=12, fill="#fdecea", stroke=POS, sw=2)

    ar_tbl, atw, ath = textbox(260, 420, [
        "orders",
        "id · placed_at · total_cents",
    ], size=13, pad=12, min_w=240)

    frags.append(arrow(260, 200 + ah / 2 + 6, 260, 420 - ath / 2 - 6, color=POS))
    frags.append(text(280, 325, "клас знає таблицю", size=12, color=POS, anchor="start"))
    frags.append(text(260, 505, "одна річ живе одразу у двох світах", size=12, color=MUTED))
    frags += [ar_obj, ar_tbl]

    # ── панель 2: Data Mapper ─────────────────────────────────────────────
    frags.append(rect(510, 70, 460, 460, fill=BG, stroke=MUTED, sw=1.5, rx=10))
    frags.append(text(740, 52, "Data Mapper", size=16, bold=True))

    dm_obj, dw, dh = textbox(680, 150, [
        "Order",
        "лише правила домену",
        "total() · cancel()",
        "про базу не знає",
    ], size=13, pad=12, fill="#eaf3ff", stroke=NEG, sw=2)

    dm_tbl, dtw, dth = textbox(680, 450, [
        "orders",
        "id · placed_at · total_cents",
    ], size=13, pad=12, min_w=240)

    dm_map, mw, mh = textbox(870, 300, [
        "OrderMapper",
        "знає обидві форми",
        "find · insert · update",
    ], size=13, pad=12, fill="#eafaf0", stroke=FIELD, sw=2)

    # пунктир «прямого зв'язку нема» + перекреслення
    frags.append(line(680, 150 + dh / 2 + 4, 680, 450 - dth / 2 - 4, color=MUTED, sw=1.4, dash="6,6"))
    frags.append(circle(680, 300, 13, fill=BG, stroke=POS, sw=2))
    frags.append(line(674, 294, 686, 306, color=POS, sw=2.2))
    frags.append(line(686, 294, 674, 306, color=POS, sw=2.2))
    frags.append(mtext(645, 292, ["не знають", "одне про одного"], size=12, color=POS, anchor="end"))

    # мапер тягнеться в обидва боки
    frags.append(arrow(870 - mw / 2 - 4, 300 - mh / 2 + 4, 680 + dw / 2 + 6, 150 + dh / 2 - 4, color=FIELD))
    frags.append(arrow(870 - mw / 2 - 4, 300 + mh / 2 - 4, 680 + dtw / 2 + 6, 450 - dth / 2 + 4, color=FIELD))
    frags.append(text(812, 218, "будує об'єкт", size=12, color=FIELD, anchor="start"))
    frags.append(text(812, 388, "читає й пише SQL", size=12, color=FIELD, anchor="start"))
    frags.append(text(740, 505, "кожен світ міняється, не чіпаючи іншого", size=12, color=MUTED))
    frags += [dm_obj, dm_tbl, dm_map]

    return render(os.path.join(IMG, 'ar-vs-dm.svg'), W, H, *frags)


def fig_identity():
    """Два об'єкти на один рядок: другий запис тихо стирає перший."""
    W, H = 900, 610
    frags = []

    row_top, rw, rh = textbox(450, 92, [
        "рядок orders id=7",
        "status='new' · total=500",
    ], size=13, pad=12, min_w=260)

    a_obj, aw, ah = textbox(200, 245, [
        "Order #7 — копія A",
        "status='new' · total=500",
    ], size=13, pad=12, fill="#eaf3ff", stroke=NEG, min_w=250)

    b_obj, bw, bh = textbox(700, 245, [
        "Order #7 — копія B",
        "status='new' · total=500",
    ], size=13, pad=12, fill="#eaf3ff", stroke=NEG, min_w=250)

    a_chg, acw, ach = textbox(200, 375, [
        "a.applyDiscount()",
        "total: 500 → 450",
    ], size=13, pad=12, min_w=200)

    b_chg, bcw, bch = textbox(700, 375, [
        "b.cancel()",
        "status: new → cancelled",
    ], size=13, pad=12, min_w=200)

    row_bottom, fw, fh = textbox(450, 540, [
        "рядок orders id=7 після обох записів",
        "status='cancelled' · total=500",
        "знижку, яку зробила A, стерто",
    ], size=13, pad=12, fill="#fdecea", stroke=POS, sw=2, min_w=300)

    # два завантаження з одного рядка
    frags.append(arrow(420, 92 + rh / 2 + 4, 240, 245 - ah / 2 - 6))
    frags.append(arrow(480, 92 + rh / 2 + 4, 660, 245 - bh / 2 - 6))
    frags.append(text(300, 168, "find(7)", size=12, anchor="end"))
    frags.append(text(600, 168, "find(7)", size=12, anchor="start"))

    # кожна копія змінюється своїм
    frags.append(arrow(200, 245 + ah / 2 + 4, 200, 375 - ach / 2 - 6))
    frags.append(arrow(700, 245 + bh / 2 + 4, 700, 375 - bch / 2 - 6))

    # обидві пишуться назад — друга поверх першої
    frags.append(arrow(240, 375 + ach / 2 + 6, 400, 540 - fh / 2 - 8))
    frags.append(arrow(660, 375 + bch / 2 + 6, 500, 540 - fh / 2 - 8, color=POS))
    frags.append(mtext(200, 448, ["1) update(a)", "пише total=450"], size=12, anchor="end"))
    frags.append(mtext(700, 448, ["2) update(b)", "пише весь рядок"], size=12, color=POS, anchor="start"))

    frags += [row_top, a_obj, b_obj, a_chg, b_chg, row_bottom]
    return render(os.path.join(IMG, 'identity.svg'), W, H, *frags)


def fig_tx_seam():
    """Хто відкриває транзакцію: мапер сам собі — чи сценарій над ним."""
    W, H = 1040, 620
    frags = []

    # ── панель 1: кожен мапер сам собі транзакція ─────────────────────────
    frags.append(rect(30, 78, 460, 510, fill=BG, stroke=MUTED, sw=1.5, rx=10))
    frags.append(text(260, 52, "Мапер сам відкриває транзакцію", size=15, bold=True))

    s1, s1w, s1h = textbox(260, 128, [
        "сценарій: скасувати замовлення",
    ], size=12, pad=11, min_w=290)

    m1, m1w, m1h = textbox(260, 218, [
        "OrderMapper.update(order)",
        "BEGIN · UPDATE orders · COMMIT",
    ], size=12, pad=11, min_w=290)

    m2, m2w, m2h = textbox(260, 400, [
        "StockMapper.release(lines)",
        "BEGIN · DELETE reserves · COMMIT",
    ], size=12, pad=11, min_w=290)

    r1, r1w, r1h = textbox(260, 528, [
        "замовлення скасоване,",
        "товар навіки в резерві",
    ], size=12, pad=11, fill="#fdecea", stroke=POS, sw=2, min_w=290)

    frags.append(arrow(260, 128 + s1h / 2 + 5, 260, 218 - m1h / 2 - 6))
    frags.append(arrow(260, 218 + m1h / 2 + 5, 260, 296, color=MUTED))
    frags.append(circle(260, 312, 15, fill=BG, stroke=POS, sw=2.2))
    frags.append(line(253, 305, 267, 319, color=POS, sw=2.4))
    frags.append(line(267, 305, 253, 319, color=POS, sw=2.4))
    frags.append(text(288, 316, "процес упав тут", size=12, color=POS, anchor="start"))
    frags.append(arrow(260, 330, 260, 400 - m2h / 2 - 6, color=MUTED))
    frags.append(text(260, 462, "друге вже не сталося", size=11, color=MUTED))
    frags += [s1, m1, m2, r1]

    # ── панель 2: транзакцію відкриває сценарій ───────────────────────────
    frags.append(rect(550, 78, 460, 510, fill=BG, stroke=MUTED, sw=1.5, rx=10))
    frags.append(text(780, 52, "Транзакцію відкриває сценарій", size=15, bold=True))

    s2, s2w, s2h = textbox(780, 128, [
        "сценарій: скасувати замовлення",
    ], size=12, pad=11, min_w=290)

    # зелений конверт транзакції
    frags.append(rect(600, 178, 360, 296, fill="#f3fbf6", stroke=FIELD, sw=2, rx=10))
    frags.append(text(780, 206, "BEGIN", size=13, color=FIELD, bold=True))

    n1, n1w, n1h = textbox(780, 262, [
        "OrderMapper(tx).update(order)",
    ], size=12, pad=11, min_w=280)

    n2, n2w, n2h = textbox(780, 342, [
        "StockMapper(tx).release(lines)",
    ], size=12, pad=11, min_w=280)

    frags.append(text(780, 396, "обидва — на одному з'єднанні tx", size=11, color=MUTED))
    frags.append(text(780, 444, "COMMIT", size=13, color=FIELD, bold=True))

    r2, r2w, r2h = textbox(780, 528, [
        "збій будь-де — ROLLBACK:",
        "не сталося ні того, ні іншого",
    ], size=12, pad=11, fill="#eafaf0", stroke=FIELD, sw=2, min_w=290)

    frags.append(arrow(780, 128 + s2h / 2 + 5, 780, 172))
    frags += [s2, n1, n2, r2]

    return render(os.path.join(IMG, 'tx-seam.svg'), W, H, *frags)


def fig_update_strategies():
    """Три способи звести колекцію позицій — і чим кожен платить."""
    W, H = 1100, 700
    frags = []

    cur, cw, ch = textbox(260, 92, [
        "у базі зараз",
        "id=11 A×2 · id=12 B×1 · id=13 D×4",
    ], size=12, pad=11, min_w=330)

    want, ww, wh = textbox(840, 92, [
        "в об'єкті в пам'яті",
        "0: A×2 · 1: B×3 · 2: C×5",
    ], size=12, pad=11, fill="#eaf3ff", stroke=NEG, sw=2, min_w=330)

    frags.append(arrow(840 - ww / 2 - 10, 92, 260 + cw / 2 + 10, 92, color=LINE))
    frags.append(text(550, 148, "об'єкт не сказав, що саме змінилося — мапер мусить це вирішити сам",
                      size=12, color=MUTED))
    frags += [cur, want]

    cols = [
        (185, "1. Стерти й вписати наново", POS, [
            "DELETE order_lines",
            "WHERE order_id = 7",
            "INSERT ×3",
        ], [
            "у базі: id=14 A · id=15 B · id=16 C",
        ], [
            ("+", "найпростіший код із можливих"),
            ("+", "порядок = порядок у масиві"),
            ("-", "id позицій щоразу нові"),
            ("-", "4 записи там, де змінилось одне"),
            ("-", "каскад знесе все, що на них"),
            ("-", "посилалося"),
        ]),
        (550, "2. Звірити з базою (diff)", NEG, [
            "SELECT поточні рядки",
            "UPDATE id=12 · INSERT C",
            "DELETE id=13",
        ], [
            "у базі: id=11 A · id=12 B · id=17 C",
        ], [
            ("+", "мінімум записів, id живуть"),
            ("+", "аудит бачить справжню зміну"),
            ("-", "зайве читання перед кожним"),
            ("-", "записом"),
            ("-", "треба стабільний ключ позиції"),
            ("-", "переставлення ламає UNIQUE"),
        ]),
        (915, "3. Знімок при завантаженні", FIELD, [
            "find() кладе поруч копію",
            "порівняння зі знімком,",
            "а не з базою",
        ], [
            "ті самі записи, 0 зайвих читань",
        ], [
            ("+", "найдешевше з трьох"),
            ("-", "мапер тримає стан"),
            ("-", "між викликами"),
            ("-", "у нього з'явився час життя"),
            ("=", "це вже Unit of Work"),
        ]),
    ]

    for cx, title, accent, ops, after, notes in cols:
        frags.append(rect(cx - 165, 190, 330, 470, fill=BG, stroke=MUTED, sw=1.5, rx=10))
        frags.append(text(cx, 220, title, size=13, color=accent, bold=True))

        opbox, obw, obh = textbox(cx, 285, ops, size=11, pad=10, min_w=290)
        afbox, afw, afh = textbox(cx, 375, after, size=11, pad=10,
                                  fill="#fafafa", stroke=MUTED, min_w=290)
        frags += [opbox, afbox]

        y = 435
        for mark, s in notes:
            color = FIELD if mark == "+" else (POS if mark == "-" else MUTED)
            glyph = "+" if mark == "+" else ("−" if mark == "-" else "→")
            frags.append(text(cx - 143, y, glyph, size=12, color=color, anchor="start", bold=True))
            frags.append(text(cx - 128, y, s, size=11, color=INK, anchor="start"))
            y += 26

    return render(os.path.join(IMG, 'update-strategies.svg'), W, H, *frags)


def fig_round_trip():
    """Два обходи туди-й-назад: через базу закривається, через домен — ні."""
    W, H = 1140, 790
    frags = []

    # ── панель 1: D → R → D ───────────────────────────────────────────────
    frags.append(rect(30, 80, 470, 630, fill=BG, stroke=MUTED, sw=1.5, rx=10))
    frags.append(text(265, 50, "Обхід через базу: об'єкт → рядок → об'єкт", size=15, bold=True))

    a1, a1w, a1h = textbox(265, 160, [
        "o — Order #7",
        "placed_at: 2026-07-14 00:00",
        "lines: A×2 по 250.00 UAH",
        "status: new",
    ], size=13, pad=12, fill="#eaf3ff", stroke=NEG, sw=2, min_w=350)

    a2, a2w, a2h = textbox(265, 390, [
        "r = save(o) — рядок orders",
        "placed_at = '2026-07-14T00:00:00'",
        "total_cents = 50000 · currency = 'UAH'",
        "status = 'new'",
    ], size=13, pad=12, min_w=350)

    a3, a3w, a3h = textbox(265, 620, [
        "load(r) — Order #7",
        "placed_at: 2026-07-14 00:00",
        "lines: A×2 по 250.00 UAH",
        "status: new",
    ], size=13, pad=12, fill="#eaf3ff", stroke=NEG, sw=2, min_w=350)

    frags.append(arrow(265, 160 + a1h / 2 + 6, 265, 390 - a2h / 2 - 8))
    frags.append(text(278, 282, "save", size=13, anchor="start", bold=True))
    frags.append(arrow(265, 390 + a2h / 2 + 6, 265, 620 - a3h / 2 - 8))
    frags.append(text(278, 512, "load", size=13, anchor="start", bold=True))

    # зелена дуга «те саме» ліворуч
    frags.append(line(70, 160, 70, 620, color=FIELD, sw=2))
    frags.append(line(70, 160, 265 - a1w / 2 - 6, 160, color=FIELD, sw=2))
    frags.append(line(70, 620, 265 - a3w / 2 - 6, 620, color=FIELD, sw=2))
    frags.append(circle(70, 390, 15, fill=BG, stroke=FIELD, sw=2))
    frags.append(text(70, 396, "=", size=17, color=FIELD, bold=True))
    frags += [a1, a2, a3]

    # ── панель 2: R → D → R ───────────────────────────────────────────────
    frags.append(rect(530, 80, 580, 630, fill=BG, stroke=MUTED, sw=1.5, rx=10))
    frags.append(text(820, 50, "Обхід через домен: рядок → об'єкт → рядок", size=15, bold=True))

    b1, b1w, b1h = textbox(845, 152, [
        "r — рядок, який уже лежить у базі",
        "placed_at = '2026-07-14'",
        "total_cents = 999   ← брехня: позиції дають 50000",
    ], size=12, pad=11, min_w=420)

    b2, b2w, b2h = textbox(845, 320, [
        "load(r) — Order #7",
        "placed_at: 2026-07-14 00:00",
        "total() рахує з позицій → 500.00 UAH",
        "колонку total_cents ніхто навіть не читав",
    ], size=12, pad=11, fill="#eaf3ff", stroke=NEG, sw=2, min_w=420)

    b3, b3w, b3h = textbox(845, 500, [
        "save(load(r)) — рядок вийшов ІНШИЙ",
        "placed_at = '2026-07-14T00:00:00'",
        "total_cents = 50000   ← підсумок перерахований",
    ], size=12, pad=11, fill="#fdecea", stroke=POS, sw=2, min_w=420)

    b4, b4w, b4h = textbox(845, 655, [
        "ще один обхід — і нічого не змінилось",
        "e(e(r)) = e(r) — далі рядок стоїть",
    ], size=12, pad=11, fill="#eafaf0", stroke=FIELD, sw=2, min_w=420)

    frags.append(arrow(845, 152 + b1h / 2 + 5, 845, 320 - b2h / 2 - 8))
    frags.append(text(858, 240, "load", size=13, anchor="start", bold=True))
    frags.append(arrow(845, 320 + b2h / 2 + 5, 845, 500 - b3h / 2 - 8))
    frags.append(text(858, 415, "save", size=13, anchor="start", bold=True))
    frags.append(arrow(845, 500 + b3h / 2 + 5, 845, 655 - b4h / 2 - 8, color=FIELD))
    frags.append(text(858, 590, "load, потім save ще раз", size=12, color=FIELD, anchor="start"))

    # червоне «≠» ліворуч між r і save(load(r))
    frags.append(line(570, 152, 570, 500, color=POS, sw=2))
    frags.append(line(570, 152, 845 - b1w / 2 - 6, 152, color=POS, sw=2))
    frags.append(line(570, 500, 845 - b3w / 2 - 6, 500, color=POS, sw=2))
    frags.append(circle(570, 326, 15, fill=BG, stroke=POS, sw=2))
    frags.append(text(570, 332, "≠", size=17, color=POS, bold=True))
    frags += [b1, b2, b3, b4]

    frags.append(text(570, 748, "Ліворуч рівність обов'язкова. Праворуч її нема — і не мусить бути: "
                                "рядок лише став канонічним.", size=13, color=MUTED))

    return render(os.path.join(IMG, 'round-trip.svg'), W, H, *frags)


def fig_fibers():
    """Рядки розпадаються на волокна; у кожному — рівно один канонічний."""
    W, H = 1180, 700
    frags = []

    frags.append(text(330, 46, "R — усі рядки, які може містити база", size=15, bold=True))
    frags.append(text(1000, 46, "D — об'єкти домену", size=15, bold=True))
    frags.append(rect(30, 70, 600, 560, fill="#fbfcfd", stroke=MUTED, sw=1.5, rx=10))
    frags.append(rect(880, 70, 240, 560, fill="#fbfcfd", stroke=MUTED, sw=1.5, rx=10))

    fibers = [
        (165, "волокно замовлення #7", [
            "('2026-07-14', 999)",
            "('2026-07-14 00:00:00', 0)",
        ], "('2026-07-14T00:00:00', 50000)", "Order #7"),
        (350, "волокно замовлення #8", [
            "('2026-07-15', 1)",
            "('2026-07-15 00:00:00', 77)",
        ], "('2026-07-15T00:00:00', 12000)", "Order #8"),
        (535, "волокно замовлення #9", [
            "('2026-07-16', 42)",
        ], "('2026-07-16T00:00:00', 300)", "Order #9"),
    ]

    for cy, title, junk, canon, objname in fibers:
        n = len(junk)
        fh = 74 + n * 26
        frags.append(rect(60, cy - fh / 2, 540, fh, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=26))
        frags.append(text(76, cy - fh / 2 + 22, title, size=12, color=MUTED, anchor="start"))

        y = cy - fh / 2 + 46
        for s in junk:
            frags.append(text(88, y, "·", size=13, color=MUTED, anchor="start"))
            frags.append(text(102, y, s, size=12, color=INK, anchor="start"))
            y += 26

        cbox, cw, ch = textbox(430, cy + 4, [canon], size=12, pad=9,
                               fill="#eafaf0", stroke=FIELD, sw=2)
        frags.append(cbox)
        frags.append(text(430, cy + 4 - ch / 2 - 9, "канонічний", size=11, color=FIELD, bold=True))

        obox, ow, oh = textbox(1000, cy, [objname], size=13, pad=10,
                               fill="#eaf3ff", stroke=NEG, sw=2, min_w=140)
        frags.append(obox)

        # load: усе волокно → один об'єкт
        frags.append(arrow(608, cy - 22, 1000 - ow / 2 - 8, cy - 8, color=LINE))
        # save: об'єкт → канонічний рядок
        frags.append(arrow(1000 - ow / 2 - 8, cy + 12, 430 + cw / 2 + 8, cy + 22, color=FIELD))

    # підписи стрілок — у вільних коридорах МІЖ волокнами, повз усі лінії
    frags.append(text(770, 240, "load", size=13, bold=True))
    frags.append(mtext(770, 262, ["злива все волокно", "в один об'єкт"],
                       size=11, color=MUTED, lh=1.5))
    frags.append(text(770, 428, "save", size=13, color=FIELD, bold=True))
    frags.append(mtext(770, 450, ["вертає рівно одного", "представника з волокна"],
                       size=11, color=MUTED, lh=1.5))

    frags.append(mtext(330, 664, [
        "e = save∘load зносить будь-який рядок на канонічний свого волокна — і там лишає.",
        "Нерухомі точки e — це і є образ save. Волокон рівно стільки, скільки об'єктів у D.",
    ], size=13, color=INK, lh=1.45))

    return render(os.path.join(IMG, 'fibers.svg'), W, H, *frags)


def fig_two_camps():
    """Дві смуги за ознакою «чий клас» — і два переходи через межу, обидва 2010-го."""
    W, H = 1360, 760
    frags = []

    # ── момент, коли таборам роздали імена ────────────────────────────────
    frags.append(line(490, 170, 490, 570, color=MUTED, sw=1.6, dash="7,6"))
    frags.append(mtext(490, 84, [
        "листопад 2002: PoEAA дає обом",
        "підходам імена — Active Record і Data Mapper",
    ], size=12, color=MUTED))

    # ── смуга A: клас належить механізму збереження ───────────────────────
    frags.append(text(680, 150, "Табір «клас належить механізму збереження»", size=14, bold=True, color=POS))

    a_ejb, aw1, ah1 = textbox(330, 215, [
        "EJB 2.0 CMP",
        "2001 · Sun",
        "бін належить контейнеру",
    ], size=12, pad=10, fill="#fdecea", stroke=POS, sw=1.8)

    a_rails, aw2, ah2 = textbox(620, 215, [
        "Rails ActiveRecord",
        "липень 2004 · DHH",
        "клас знає таблицю",
    ], size=12, pad=10, fill="#fdecea", stroke=POS, sw=1.8, min_w=170)

    a_doc1, aw3, ah3 = textbox(830, 215, [
        "Doctrine 1",
        "2006–2008 · PHP",
        "extends Doctrine_Record",
    ], size=12, pad=10, fill="#fdecea", stroke=POS, sw=1.8)

    a_ef1, aw4, ah4 = textbox(1120, 215, [
        "Entity Framework 1",
        "2008 · Microsoft",
        "extends EntityObject",
    ], size=12, pad=10, fill="#fdecea", stroke=POS, sw=1.8, min_w=170)

    # ── смуга B: клас твій, збереження — окрема служба ────────────────────
    frags.append(text(680, 610, "Табір «клас твій, збереження — окрема служба»", size=14, bold=True, color=NEG))

    b_top, bw1, bh1 = textbox(130, 520, [
        "TopLink",
        "1994 · Smalltalk",
        "відповідність — зовні",
    ], size=12, pad=10, fill="#eaf3ff", stroke=NEG, sw=1.8)

    b_hib, bw2, bh2 = textbox(330, 520, [
        "Hibernate",
        "2001 · Гевін Кінг",
        "звичайні класи + XML",
    ], size=12, pad=10, fill="#eaf3ff", stroke=NEG, sw=1.8, min_w=170)

    b_jpa, bw3, bh3 = textbox(700, 520, [
        "JPA 1.0 · SQLAlchemy",
        "2006",
        "стандарт і Python-мапер",
    ], size=12, pad=10, fill="#eaf3ff", stroke=NEG, sw=1.8)

    b_doc2, bw4, bh4 = textbox(940, 520, [
        "Doctrine 2",
        "грудень 2010",
        "збереження — служба",
    ], size=12, pad=10, fill="#eaf3ff", stroke=NEG, sw=1.8, min_w=170)

    b_ef4, bw5, bh5 = textbox(1230, 520, [
        "Entity Framework 4",
        "2010 · POCO",
        "клас звільнено",
    ], size=12, pad=10, fill="#eaf3ff", stroke=NEG, sw=1.8, min_w=170)

    # ── бунт проти контейнера: той самий 2001-й, дві відповіді ────────────
    frags.append(arrow(330, 215 + ah1 / 2 + 6, 330, 520 - bh2 / 2 - 8, color=LINE))
    frags.append(mtext(348, 358, ["бунт проти", "контейнера"], size=12, anchor="start"))

    # ── два переходи через межу — обидва 2010-го, обидва в один бік ───────
    frags.append(arrow(830, 215 + ah3 / 2 + 6, 940, 520 - bh4 / 2 - 8, color=POS, sw=2.4))
    frags.append(mtext(810, 372, ["переписано >90% коду,", "сумісності з 1.x — нуль"],
                       size=11, color=POS, anchor="end"))

    frags.append(arrow(1120, 215 + ah4 / 2 + 6, 1230, 520 - bh5 / 2 - 8, color=POS, sw=2.4))
    frags.append(mtext(1100, 372, ["POCO: клас звільнили", "від базового класу"],
                       size=11, color=POS, anchor="end"))

    frags += [a_ejb, a_rails, a_doc1, a_ef1, b_top, b_hib, b_jpa, b_doc2, b_ef4]

    frags.append(text(680, 690, "Обидва переходи через межу сталися 2010 року — і обидва в один бік",
                      size=13, color=MUTED, italic=True))

    return render(os.path.join(IMG, 'two-camps.svg'), W, H, *frags)


if __name__ == '__main__':
    print(fig_mismatch())
    print(fig_ar_vs_dm())
    print(fig_identity())
    print(fig_tx_seam())
    print(fig_update_strategies())
    print(fig_two_camps())
    print(fig_round_trip())
    print(fig_fibers())
