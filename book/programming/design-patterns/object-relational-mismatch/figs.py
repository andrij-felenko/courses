# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_seams():
    """П'ять швів неузгодженості: об'єктний бік проти реляційного, рядок за рядком."""
    W, H = 1245, 675
    frags = []

    # заголовки колонок
    frags.append(text(150, 52, "шов", size=14, bold=True, color=MUTED))
    frags.append(text(535, 52, "Об'єкти (пам'ять)", size=15, bold=True, color=NEG))
    frags.append(text(990, 52, "Реляція (таблиці)", size=15, bold=True))

    rows = [
        ("Гранулярність",
         ["багато дрібних типів:", "Money, Address, PersonName"],
         ["колонки одного рядка,", "типу «гроші» немає"]),
        ("Підтипи",
         ["ієрархія + поліморфізм:", "Payment ← CardPayment"],
         ["таблиці не успадковуються:", "одна широка / JOIN / UNION"]),
        ("Тотожність",
         ["посилання ≠ рівність значень:", "(a===b)  vs  a.equals(b)"],
         ["лише первинний ключ:", "id = 7 — і по всьому"]),
        ("Зв'язки",
         ["посилання й колекції,", "«багато-до-багатьох» задарма"],
         ["зовнішній ключ + таблиця-місток,", "напрямок часто протилежний"]),
        ("Навігація",
         ["обхід крапкою:", "order.customer.address"],
         ["запит або JOIN на кожен крок,", "N+1, якщо буквально"]),
    ]

    y = 150
    for facet, obj, rel in rows:
        fbox, _, _ = textbox(150, y, [facet], size=13, pad=11, bold=True,
                             color=NEG, fill="#f4f7fc", stroke=NEG, sw=1.6, min_w=210)
        obox, _, _ = textbox(535, y, obj, size=13, pad=12,
                             fill="#eaf3ff", stroke=NEG, sw=1.8, min_w=430)
        rbox, _, _ = textbox(990, y, rel, size=13, pad=12, min_w=430)
        frags += [fbox, obox, rbox]
        y += 108

    frags.append(text(622, 648,
                      "той самий факт — дві форми; на кожному рядку об'єктна властивість не має прямого відповідника в таблицях",
                      size=12, color=MUTED, italic=True))
    return render(os.path.join(IMG, 'seams.svg'), W, H, *frags)


def fig_navigation():
    """Обхід графа: у пам'яті — вказівники, у базі — злива запитів (N+1)."""
    W, H = 1180, 560
    frags = []

    # ── панель 1: обхід крапкою в пам'яті ─────────────────────────────────
    frags.append(rect(30, 84, 520, 430, fill=BG, stroke=MUTED, sw=1.5, rx=10))
    frags.append(text(290, 66, "У пам'яті: обхід крапкою — дешево", size=14, bold=True))

    o1, o1w, _ = textbox(130, 220, ["Order"], size=13, pad=11,
                         fill="#eaf3ff", stroke=NEG, sw=1.8, min_w=120)
    o2, o2w, _ = textbox(290, 220, ["Customer"], size=13, pad=11,
                         fill="#eaf3ff", stroke=NEG, sw=1.8, min_w=120)
    o3, o3w, _ = textbox(450, 220, ["Address"], size=13, pad=11,
                         fill="#eaf3ff", stroke=NEG, sw=1.8, min_w=120)

    frags.append(arrow(130 + o1w / 2 + 4, 220, 290 - o2w / 2 - 4, 220))
    frags.append(arrow(290 + o2w / 2 + 4, 220, 450 - o3w / 2 - 4, 220))
    frags.append(text(210, 200, ".customer", size=12, color=MUTED))
    frags.append(text(370, 200, ".address", size=12, color=MUTED))
    frags += [o1, o2, o3]

    frags.append(mtext(290, 320,
                       ["кожен крок — розіменований вказівник",
                        "у RAM, наносекунди; сто кроків нічого не варті"],
                       size=12, color=INK, lh=1.5))

    # ── панель 2: той самий обхід у базі — N+1 ────────────────────────────
    frags.append(rect(600, 84, 550, 430, fill=BG, stroke=MUTED, sw=1.5, rx=10))
    frags.append(text(875, 66, "У базі: кожен крок — окремий запит", size=14, bold=True))

    q0, _, q0h = textbox(875, 168, ["SELECT * FROM orders",
                                    "→ 3 рядки: #7 · #8 · #9"], size=12, pad=11, min_w=310)

    qcols = [(710, "#7"), (875, "#8"), (1040, "#9")]
    qboxes = []
    for cx, tag in qcols:
        qb, _, qbh = textbox(cx, 336, ["SELECT customer", "WHERE order=%s" % tag],
                             size=12, pad=10, fill="#fdf2f0", stroke=POS, sw=1.6, min_w=150)
        qboxes.append((qb, cx, qbh))

    for _, cx, qbh in qboxes:
        frags.append(arrow(875, 168 + q0h / 2 + 4, cx, 336 - qbh / 2 - 6, color=LINE))
    frags.append(q0)
    frags += [qb for qb, _, _ in qboxes]

    note, _, _ = textbox(875, 452, ["1 запит на список + 3 на клієнтів = 4",
                                    "N+1: список плюс запит на кожен рядок"],
                         size=12, pad=11, fill="#fdecea", stroke=POS, sw=2, min_w=340)
    frags.append(note)

    return render(os.path.join(IMG, 'navigation.svg'), W, H, *frags)


def fig_impedance():
    """Позичена аналогія: у електриці опір можна зрівняти (Γ=0), на стику об'єкт↔рядок — ні."""
    W, H = 1200, 640
    frags = []

    # ── панель A: електрика ───────────────────────────────────────────────
    frags.append(rect(40, 70, 1120, 235, fill=BG, stroke=MUTED, sw=1.4, rx=10))
    frags.append(text(600, 58, "В електриці: опір — одна величина, і її можна зрівняти",
                      size=15, bold=True))

    sA, sAw, _ = textbox(150, 165, ["Джерело", "опір Z₀"], size=13, pad=12,
                         fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=150)
    lA, lAw, _ = textbox(1050, 165, ["Навантаження", "опір Zₗ"], size=13, pad=12,
                         fill="#fdecea", stroke=POS, sw=1.8, min_w=150)
    # межа (стрибок опору)
    frags.append(line(700, 110, 700, 222, color=MUTED, sw=1.6, dash="6 5"))
    # падна, передана, відбита
    frags.append(arrow(150 + sAw / 2 + 8, 148, 690, 148))
    frags.append(text(410, 138, "падна хвиля", size=12, color=MUTED))
    frags.append(arrow(710, 165, 1050 - lAw / 2 - 8, 165, color=FIELD))
    frags.append(text(870, 155, "передана", size=12, color=FIELD))
    frags.append(arrow(690, 190, 150 + sAw / 2 + 8, 190, color=POS))
    frags.append(text(410, 210, "відбита — коли Zₗ ≠ Z₀", size=12, color=POS))
    frags += [sA, lA]
    frags.append(text(600, 288,
                      "Γ = (Zₗ − Z₀) / (Zₗ + Z₀)      Zₗ = Z₀ → Γ = 0: усе проходить, нічого не вертається",
                      size=13))

    # ── панель B: об'єкт ↔ рядок ──────────────────────────────────────────
    frags.append(rect(40, 345, 1120, 235, fill=BG, stroke=MUTED, sw=1.4, rx=10))
    frags.append(text(600, 333, "На стику об'єкт ↔ таблиця: «опори» різнорідні",
                      size=15, bold=True))

    sB, sBw, _ = textbox(150, 440, ["Об'єкт", "(пам'ять)"], size=13, pad=12,
                         fill="#eaf3ff", stroke=NEG, sw=1.8, min_w=150)
    lB, lBw, _ = textbox(1050, 440, ["Рядок", "(таблиця)"], size=13, pad=12,
                         fill="#f4f6f8", stroke=INK, sw=1.6, min_w=150)
    frags.append(line(660, 388, 660, 500, color=MUTED, sw=1.6, dash="6 5"))
    frags.append(text(660, 378, "переклад", size=12, color=MUTED))
    frags.append(arrow(150 + sBw / 2 + 8, 423, 650, 423))
    frags.append(text(400, 413, "зусилля програміста", size=12, color=MUTED))
    frags.append(arrow(670, 440, 1050 - lBw / 2 - 8, 440, color=FIELD))
    frags.append(text(865, 430, "лягло в рядок", size=12, color=FIELD))
    frags.append(arrow(650, 465, 150 + sBw / 2 + 8, 465, color=POS))
    frags.append(text(400, 485, "відбите зусилля — на КОЖНОМУ переході", size=12, color=POS))
    frags += [sB, lB]

    note, _, _ = textbox(600, 552,
                         ["«Опори» тут різнорідні — не два значення однієї величини, а різні речі.",
                          "Стану, де Γ = 0, немає: повністю узгодити не можна ніколи — ось де аналогія ламається."],
                         size=12.5, pad=12, fill="#fdf2f0", stroke=POS, sw=1.6, min_w=980)
    frags.append(note)
    return render(os.path.join(IMG, 'impedance.svg'), W, H, *frags)


def fig_timeline():
    """Рух об'єктних баз: спалах об'єктного табору й тихе вбирання ідей реляційним родом."""
    W, H = 1180, 1085
    frags = []
    frags.append(text(590, 34, "Хроніка: два табори й один переможець", size=17, bold=True))

    # легенда
    def swatch(x, color, label):
        out = rect(x, 46, 20, 14, fill=color, stroke=color, sw=1.4, rx=3)
        out += text(x + 28, 58, label, size=12.5, anchor="start", color=INK)
        return out
    frags.append(swatch(210, NEG, "реляційний рід — вбирає й триває"))
    frags.append(swatch(560, POS, "об'єктні бази — спалах і згасання"))
    frags.append(swatch(910, MUTED, "про сам термін"))

    # вертикальна вісь
    LX = 305
    frags.append(line(LX, 95, LX, 1035, color=MUTED, sw=2))

    rows = [
        ("1970", NEG,   ["Едґар Кодд описує реляційну модель"]),
        ("1984", MUTED, ["Коупленд і Маєр, «Making Smalltalk a Database System»",
                         "звідси часто виводять сам термін (непевно)"]),
        ("1986", POS,   ["GemStone 1.0 — перша об'єктна база на ринку"]),
        ("1988", POS,   ["ObjectStore, Versant — об'єктні бази для C++"]),
        ("1989", POS,   ["«Маніфест об'єктних баз» (Аткінсон та ін., Кіото)"]),
        ("1990", NEG,   ["«Маніфест третього покоління» (Стоунбрейкер):",
                         "реляцію не викидати — розширити"]),
        ("1991", POS,   ["консорціум ODMG (Кеттелл) — спроба єдиного стандарту"]),
        ("1993", POS,   ["ODMG-93 + мова OQL: об'єктний табір змушений",
                         "додати декларативні запити, як у SQL"]),
        ("1996", NEG,   ["Informix купує Illustra (лінія POSTGRES):",
                         "об'єктно-реляційні рушії виходять на ринок"]),
        ("1999", NEG,   ["SQL:1999 — типи-структури входять у сам стандарт SQL"]),
        ("2001", POS,   ["ODMG розпущено; ринок об'єктних баз згортається"]),
        ("2006", MUTED, ["Невард: ORM — «В'єтнам комп'ютерних наук»"]),
    ]

    tint = {NEG: "#eaf0fd", POS: "#fdecea", MUTED: "#f2f2f4"}
    y0, step = 132, 78
    for i, (year, color, lines) in enumerate(rows):
        c = y0 + i * step
        frags.append(fitbox(345, c - 29, 775, 58, lines, size=13.5, pad=11,
                            fill=tint[color], stroke=color, sw=1.7))
        frags.append(circle(LX, c, 7.5, fill=color, stroke=color, sw=1.4))
        frags.append(text(272, c + 5, year, size=15, bold=True, color=color, anchor="end"))

    return render(os.path.join(IMG, 'timeline.svg'), W, H, *frags)


def _dbtable(cx, top, name, cols, w=None, stroke=INK, sw=1.7, tint=FILL, shade=None):
    """Схематична таблиця БД: смужка-назва + список колонок. shade — індекси колонок,
    які треба затінити (напр. дубльовані/NULL). Повертає (frag, w, h)."""
    tw = max([text_width(name, 14, True)] + [text_width(c, 12.5) for c in cols])
    if w is None:
        w = tw + 46
    title_h, row_h = 33, 24
    h = title_h + len(cols) * row_h + 12
    x = cx - w / 2
    frag = rect(x, top, w, h, fill=BG, stroke=stroke, sw=sw, rx=9)
    frag += rect(x, top, w, title_h, fill=tint, stroke=stroke, sw=sw, rx=9)
    frag += rect(x, top + title_h - 9, w, 9, fill=tint, stroke="none", sw=0, rx=0)
    frag += line(x, top + title_h, x + w, top + title_h, color=stroke, sw=sw)
    frag += text(cx, top + 22, name, size=14, bold=True)
    y = top + title_h + 18
    for i, c in enumerate(cols):
        if shade and i in shade:
            frag += rect(x + 5, y - 15, w - 10, 20, fill="#eceef2", stroke="none", sw=0, rx=4)
        frag += text(x + 15, y, c, size=12.5, anchor="start", color=INK)
        y += row_h
    return frag, w, h


def fig_shapes():
    """Три форми, у які лягає ієрархія Payment ← CardPayment, BankTransfer."""
    W, H = 1230, 1120
    frags = []
    AMBER, AMBER_F = "#b7791f", "#fbf3e0"

    # ── смуга ①: одна таблиця ────────────────────────────────────────────────
    frags.append(text(40, 46, "① Одна таблиця на всю ієрархію — колонка kind обирає різновид",
                      size=15, bold=True, anchor="start"))
    t1, w1, _ = _dbtable(255, 70, "payments",
                         ["id            PK", "kind      ◄ розрізнювач",
                          "amount_cents", "currency", "created_at",
                          "card_last4", "auth_code", "iban", "reference"],
                         shade={5, 6, 7, 8})
    frags.append(t1)
    n1, _, _ = textbox(760, 150,
                       ["у КАРТКОВОМУ рядку iban, reference — NULL;",
                        "у БАНКІВСЬКОМУ card_last4, auth_code — NULL.",
                        "NOT NULL на них поставити не можна —",
                        "лише CHECK за значенням kind."],
                       size=12.5, pad=13, fill="#fdecea", stroke=POS, sw=1.7, min_w=470)
    frags.append(n1)
    frags.append(line(40, 330, W - 40, 330, color=MUTED, sw=1, dash="4 5"))

    # ── смуга ②: таблиця на клас (JOIN) ──────────────────────────────────────
    frags.append(text(40, 372, "② Таблиця на клас — повний об'єкт збирають JOIN-ом",
                      size=15, bold=True, anchor="start"))
    base, bw, bh = _dbtable(615, 398, "payments",
                            ["id            PK", "kind", "amount_cents",
                             "currency", "created_at"], tint="#eaf0fd")
    frags.append(base)
    cardj, cjw, _ = _dbtable(330, 610, "card_payments",
                             ["id   PK → payments", "card_last4  NOT NULL",
                              "auth_code   NOT NULL"], tint="#eaf3ff")
    bankj, bjw, _ = _dbtable(900, 610, "bank_transfers",
                             ["id   PK → payments", "iban       NOT NULL",
                              "reference  NOT NULL"], tint="#eaf3ff")
    frags += [cardj, bankj]
    frags.append(arrow(330, 610, 615 - 40, 398 + bh, color=NEG))
    frags.append(arrow(900, 610, 615 + 40, 398 + bh, color=NEG))
    frags.append(text(430, 585, "id = FK → payments(id)", size=11.5, color=NEG))
    frags.append(text(800, 585, "id = FK → payments(id)", size=11.5, color=NEG))
    n2, _, _ = textbox(1035, 445,
                       ["id підтипу — це і PK,",
                        "і зовнішній ключ на базу.",
                        "NOT NULL повертається.",
                        "Запис — 2 INSERT в одній",
                        "транзакції."],
                       size=12.5, pad=12, fill="#e8f6ee", stroke=FIELD, sw=1.7, min_w=250)
    frags.append(n2)
    frags.append(line(40, 745, W - 40, 745, color=MUTED, sw=1, dash="4 5"))

    # ── смуга ③: таблиця на конкретний клас (UNION) ──────────────────────────
    frags.append(text(40, 787, "③ Таблиця на конкретний клас — «усі платежі» лише через UNION",
                      size=15, bold=True, anchor="start"))
    cardc, ccw, cch = _dbtable(300, 812, "card_payments",
                               ["id            PK", "amount_cents", "currency",
                                "created_at", "card_last4", "auth_code"],
                               tint="#eaf3ff", shade={1, 2, 3})
    bankc, bcw, _ = _dbtable(700, 812, "bank_transfers",
                             ["id            PK", "amount_cents", "currency",
                              "created_at", "iban", "reference"],
                             tint="#eaf3ff", shade={1, 2, 3})
    frags += [cardc, bankc]
    frags.append(text(500, 1000, "затінене — спільні колонки, дубльовані в кожній таблиці",
                      size=11.5, color=MUTED, italic=True))
    n3, _, _ = textbox(1005, 878,
                       ["Таблиці payments НЕМАЄ —",
                        "абстрактного Payment у схемі",
                        "не існує. Зовнішній ключ на",
                        "«будь-який платіж» поставити",
                        "нема на що. id — унікальний",
                        "МІЖ таблицями (спільна",
                        "послідовність або UUID)."],
                       size=12.5, pad=12, fill="#fdecea", stroke=POS, sw=1.9, min_w=290)
    frags.append(n3)
    return render(os.path.join(IMG, 'inherit-shapes.svg'), W, H, *frags)


def fig_tradeoffs():
    """Три стратегії проти семи вимірів: де кожна виграє, де програє."""
    W, H = 1220, 640
    GOOD, GOOD_F = FIELD, "#e8f6ee"
    WARN, WARN_F = "#b7791f", "#fbf3e0"
    BAD, BAD_F = POS, "#fdecea"
    frags = []

    cols_x = [40, 300, 610, 920]
    cols_w = [250, 300, 300, 290]
    heads = ["", "① Одна таблиця", "② Таблиця на клас", "③ Конкретна таблиця"]
    for i, htxt in enumerate(heads):
        if i == 0:
            continue
        frags.append(fitbox(cols_x[i], 40, cols_w[i], 46, [htxt], size=14.5,
                            bold=True, fill="#eef1f6", stroke=INK, sw=1.5))

    rows = [
        ("«усі платежі»",
         ("1 скан · 0 JOIN", GOOD, GOOD_F),
         ("N LEFT JOIN", WARN, WARN_F),
         ("N-way UNION ALL", WARN, WARN_F)),
        ("«один платіж»",
         ("0 JOIN", GOOD, GOOD_F),
         ("1 JOIN або 2 запити", WARN, WARN_F),
         ("1 запит · 0 JOIN", GOOD, GOOD_F)),
        ("запис",
         ("1 INSERT", GOOD, GOOD_F),
         ("2 INSERT у транзакції", WARN, WARN_F),
         ("1 INSERT", GOOD, GOOD_F)),
        ("NOT NULL на полях підтипу",
         ("ні — лише CHECK", BAD, BAD_F),
         ("так", GOOD, GOOD_F),
         ("так", GOOD, GOOD_F)),
        ("ЗК на «будь-який платіж»",
         ("так — одна таблиця", GOOD, GOOD_F),
         ("так — на базу", GOOD, GOOD_F),
         ("немає куди", BAD, BAD_F)),
        ("нова гілка / спільна колонка",
         ("+колонки, дешево", GOOD, GOOD_F),
         ("+таблиця", WARN, WARN_F),
         ("правити КОЖНУ таблицю", BAD, BAD_F)),
        ("місце на диску",
         ("широка, багато NULL", WARN, WARN_F),
         ("компактно", GOOD, GOOD_F),
         ("спільне дубльовано", WARN, WARN_F)),
    ]

    y, rh = 96, 68
    for dim, *cells in rows:
        frags.append(fitbox(cols_x[0], y, cols_w[0], rh - 8, [dim], size=13,
                            bold=True, fill="#f6f7f9", stroke=MUTED, sw=1.3))
        for j, (txt, col, fil) in enumerate(cells, start=1):
            frags.append(fitbox(cols_x[j], y, cols_w[j], rh - 8, [txt], size=13,
                                fill=fil, stroke=col, sw=1.6, color=INK))
        y += rh

    return render(os.path.join(IMG, 'inherit-tradeoffs.svg'), W, H, *frags)


if __name__ == '__main__':
    print(fig_seams())
    print(fig_navigation())
    print(fig_impedance())
    print(fig_timeline())
    print(fig_shapes())
    print(fig_tradeoffs())
