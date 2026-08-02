# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GRN = "#eafaf0"   # заливка «модуль таблиці» / виграш
RED = "#fdecea"   # заливка копії правила / плати
BLU = "#eaf0fd"   # заливка об'єктів предметної моделі


def grid(x, y, w, h, name, rows, head_h=30, size=11):
    """Сітка рядків таблиці: смуга з іменем + кілька рядків, розділених лініями."""
    f = [rect(x, y, w, h, fill=BG, stroke=MUTED, sw=1.6, rx=6)]
    f.append(rect(x, y, w, head_h, fill=FILL, stroke=MUTED, sw=1.4, rx=6))
    f.append(text(x + w / 2, y + head_h - 9, name, size=size + 1, color=INK, bold=True))
    step = (h - head_h) / float(len(rows))
    for i, r in enumerate(rows):
        ry = y + head_h + step * i
        if i:
            f.append(line(x, ry, x + w, ry, color=MUTED, sw=0.9, dash="4 4"))
        f.append(text(x + 14, ry + step / 2 + size * 0.35, r, size=size, color=MUTED, anchor="start"))
    return "".join(f)


# ── 1. Три способи нарізати ту саму логіку ──────────────────────────────────
def fig_three_cuts():
    W, H = 1320, 600
    f = [text(W / 2, 34, "Одна логіка, три одиниці нарізки", size=17, bold=True)]

    for dx in (440, 880):
        f.append(line(dx, 58, dx, 545, color=MUTED, sw=1.1, dash="5 5"))

    # ══ ЛІВОРУЧ: сценарій транзакції ══
    f.append(text(220, 78, "СЦЕНАРІЙ ТРАНЗАКЦІЇ", size=14, color=INK, bold=True))
    f.append(text(220, 100, "одиниця — ДІЯ", size=11.5, color=MUTED, italic=True))

    procs = ["ПорахуватиВизнання()", "ПоказатиЗвіт()", "ВивантажитиДані()"]
    for i, name in enumerate(procs):
        y = 126 + i * 120
        f.append(rect(70, y, 300, 100, fill=BG, stroke=LINE, sw=1.7, rx=8))
        f.append(text(220, y + 24, name, size=12.5, color=INK, bold=True))
        f.append(rect(86, y + 38, 268, 28, fill=RED, stroke=POS, sw=1.3, rx=5))
        f.append(text(220, y + 57, "правило визнання виторгу", size=11, color=POS))
        f.append(text(220, y + 85, "читання й запис рядків", size=11, color=MUTED))
    f.append(mtext(220, 500, ["спільне правило — окремою копією", "в кожній процедурі"],
                   size=11.5, color=POS, lh=1.35))

    # ══ ПОСЕРЕДИНІ: модуль таблиці ══
    f.append(text(660, 78, "МОДУЛЬ ТАБЛИЦІ", size=14, color=FIELD, bold=True))
    f.append(text(660, 100, "одиниця — ТАБЛИЦЯ", size=11.5, color=MUTED, italic=True))

    f.append(rect(510, 126, 300, 150, fill=GRN, stroke=FIELD, sw=1.9, rx=8))
    f.append(text(660, 152, "КонтрактиМодуль", size=13, color=INK, bold=True))
    for i, m in enumerate(["ПорахуватиВизнання(id)", "ВизнаноНаДату(id, дата)", "ДодатиКонтракт(…)"]):
        f.append(text(530, 182 + i * 24, m, size=11, color=INK, anchor="start"))
    f.append(text(660, 262, "усі правила таблиці — тут", size=11, color=FIELD, italic=True))

    f.append(arrow(660, 280, 660, 318, color=MUTED, sw=1.7))
    f.append(grid(510, 322, 300, 120, "contracts", ["рядок 17", "рядок 18", "рядок 19"]))
    f.append(mtext(660, 500, ["один екземпляр —", "на всі рядки таблиці"],
                   size=11.5, color=FIELD, lh=1.35))

    # ══ ПРАВОРУЧ: предметна модель ══
    f.append(text(1100, 78, "ПРЕДМЕТНА МОДЕЛЬ", size=14, color=NEG, bold=True))
    f.append(text(1100, 100, "одиниця — РЯДОК", size=11.5, color=MUTED, italic=True))

    objs = [(1035, 170, "Контракт №17"), (1180, 285, "Контракт №18"), (1035, 400, "Контракт №19")]
    for cx, cy, name in objs:
        f.append(rect(cx - 78, cy - 35, 156, 70, fill=BLU, stroke=NEG, sw=1.8, rx=9))
        f.append(text(cx, cy - 6, name, size=12, color=INK, bold=True))
        f.append(text(cx, cy + 16, "дані + правило", size=10.5, color=MUTED))
    f.append(line(1035, 205, 1180, 250, color=MUTED, sw=1.4))
    f.append(line(1180, 320, 1035, 365, color=MUTED, sw=1.4))
    f.append(mtext(1100, 500, ["свій об'єкт на кожен запис —", "і своя дорога до бази"],
                   size=11.5, color=NEG, lh=1.35))

    return render(os.path.join(OUT, "three-cuts.svg"), W, H, *f)


# ── 2. Анатомія модуля таблиці ──────────────────────────────────────────────
def fig_module_anatomy():
    W, H = 1300, 650
    f = [text(W / 2, 34, "Модуль тримає поведінку, набір рядків тримає дані", size=17, bold=True)]

    # споживач
    f.append(rect(40, 150, 250, 130, fill=BG, stroke=LINE, sw=1.7, rx=8))
    f.append(text(165, 178, "код-споживач", size=12.5, color=INK, bold=True))
    f.append(text(56, 210, "contracts.Порахувати(17)", size=11, color=INK, anchor="start"))
    f.append(text(56, 236, "contracts.Визнано(17, дата)", size=11, color=INK, anchor="start"))
    f.append(text(165, 266, "ключ рядка — аргументом", size=10.5, color=POS))
    f.append(arrow(292, 215, 358, 215, color=MUTED, sw=1.8))

    # модуль контрактів
    f.append(rect(365, 120, 390, 230, fill=GRN, stroke=FIELD, sw=2, rx=9))
    f.append(line(365, 158, 755, 158, color=FIELD, sw=1.3))
    f.append(text(560, 146, "КонтрактиМодуль", size=13.5, color=INK, bold=True))
    f.append(text(560, 182, "один екземпляр на всі рядки", size=11, color=MUTED, italic=True))
    for i, m in enumerate(["ПорахуватиВизнання(id)", "ВизнаноНаДату(id, дата)", "ДодатиВизнання(id, сума, дата)"]):
        f.append(text(388, 212 + i * 26, m, size=11.5, color=INK, anchor="start"))
    f.append(text(560, 320, "власних полів рядка немає", size=11.5, color=POS, bold=True))

    # модуль товарів
    f.append(rect(880, 150, 300, 130, fill=GRN, stroke=FIELD, sw=2, rx=9))
    f.append(line(880, 186, 1180, 186, color=FIELD, sw=1.3))
    f.append(text(1030, 174, "ТовариМодуль", size=13, color=INK, bold=True))
    f.append(text(902, 214, "ТипТовару(id)", size=11.5, color=INK, anchor="start"))
    f.append(text(902, 244, "ЦінаТовару(id)", size=11.5, color=INK, anchor="start"))

    f.append(arrow(758, 235, 876, 235, color=MUTED, sw=1.8))
    f.append(mtext(817, 186, ["розмова модулів —", "теж ключем"], size=10.5, color=MUTED, lh=1.35))

    # набір рядків
    f.append(rect(365, 420, 815, 190, fill=BG, stroke=MUTED, sw=1.6, rx=10, ))
    f.append(text(772, 448, "НАБІР РЯДКІВ", size=12.5, color=MUTED, bold=True))
    f.append(grid(395, 468, 350, 122, "contracts", ["17 · табличний · 1000.00", "18 · текстовий · 600.00", "19 · табличний · 900.00"], size=10.5))
    f.append(grid(800, 468, 350, 122, "products", ["3 · табличний процесор", "4 · текстовий редактор", "5 · база даних"], size=10.5))

    f.append(arrow(500, 352, 500, 464, color=MUTED, sw=1.7))
    f.append(text(600, 396, "пошук за ключем — індексом", size=11, color=MUTED, anchor="start"))
    f.append(arrow(1030, 282, 1030, 464, color=MUTED, sw=1.7))

    return render(os.path.join(OUT, "module-anatomy.svg"), W, H, *f)


# ── 3. Дорога даних: із перекладаннями й без ────────────────────────────────
def fig_recordset_spine():
    W, H = 1300, 600
    f = [text(W / 2, 34, "Дорога даних за одну операцію", size=17, bold=True)]

    def box(x, y, w, h, lines, fill=FILL, stroke=LINE, sw=1.7, size=11.5, bold_first=True):
        out = [rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=8)]
        cy = y + h / 2 - (len(lines) - 1) * size * 1.35 / 2 + size * 0.35
        out.append(mtext(x + w / 2, cy, lines, size=size, color=INK, lh=1.35, bold=bold_first))
        return "".join(out)

    # ══ СМУГА 1: модуль таблиці ══
    f.append(text(60, 90, "МОДУЛЬ ТАБЛИЦІ", size=14, color=FIELD, bold=True, anchor="start"))
    f.append(box(60, 112, 130, 68, ["база даних"]))
    f.append(arrow(194, 146, 226, 146, color=MUTED, sw=1.8))
    f.append(box(230, 112, 160, 68, ["набір рядків"]))
    f.append(arrow(394, 146, 436, 146, color=MUTED, sw=1.8))
    f.append(box(440, 112, 240, 68, ["правило застосовано", "ПРЯМО в наборі"], fill=GRN, stroke=FIELD, sw=2, size=11.5))
    f.append(arrow(684, 146, 726, 146, color=MUTED, sw=1.8))
    f.append(box(730, 112, 175, 68, ["той самий", "набір рядків"]))

    f.append(box(960, 96, 165, 46, ["екранна сітка"], size=11.5))
    f.append(box(960, 154, 165, 46, ["звіт"], size=11.5))
    f.append(arrow(909, 138, 956, 122, color=MUTED, sw=1.7))
    f.append(arrow(909, 156, 956, 174, color=MUTED, sw=1.7))
    f.append(mtext(1215, 132, ["перекладань", "жодного"], size=12, color=FIELD, lh=1.35, bold=True))

    # зворотний шлях у базу
    f.append(line(817, 182, 817, 244, color=MUTED, sw=1.5, dash="6 4"))
    f.append(line(817, 244, 125, 244, color=MUTED, sw=1.5, dash="6 4"))
    f.append(arrow(125, 244, 125, 186, color=MUTED, sw=1.5))
    f.append(text(480, 232, "той самий набір — назад у базу", size=11, color=MUTED))

    # ══ СМУГА 2: предметна модель ══
    f.append(text(60, 322, "ПРЕДМЕТНА МОДЕЛЬ", size=14, color=NEG, bold=True, anchor="start"))
    f.append(box(60, 344, 120, 68, ["база даних"]))
    f.append(arrow(184, 378, 216, 378, color=MUTED, sw=1.8))
    f.append(box(220, 344, 150, 68, ["набір рядків"]))
    f.append(arrow(374, 378, 406, 378, color=MUTED, sw=1.8))
    f.append(box(410, 344, 120, 68, ["мапер"], fill=RED, stroke=POS, sw=1.9))
    f.append(arrow(534, 378, 566, 378, color=MUTED, sw=1.8))
    f.append(box(570, 344, 180, 68, ["об'єкти:", "операція"], fill=BLU, stroke=NEG, sw=1.9))
    f.append(arrow(754, 378, 786, 378, color=MUTED, sw=1.8))
    f.append(box(790, 344, 120, 68, ["мапер"], fill=RED, stroke=POS, sw=1.9))
    f.append(arrow(914, 378, 946, 378, color=MUTED, sw=1.8))
    f.append(box(950, 344, 215, 68, ["таблиця для", "екрана і звіту"]))

    f.append(text(470, 432, "код перекладання", size=10.5, color=POS))
    f.append(text(850, 432, "і код назад", size=10.5, color=POS))

    f.append(line(1057, 414, 1057, 476, color=MUTED, sw=1.5, dash="6 4"))
    f.append(line(1057, 476, 120, 476, color=MUTED, sw=1.5, dash="6 4"))
    f.append(arrow(120, 476, 120, 418, color=MUTED, sw=1.5))
    f.append(text(300, 464, "зміни назад у базу", size=11, color=MUTED))

    f.append(mtext(660, 534, ["два перекладання за кожен прохід — і догляд за тотожністю об'єктів у пам'яті"],
                   size=12, color=POS, lh=1.35))

    return render(os.path.join(OUT, "recordset-spine.svg"), W, H, *f)


# ── 4. Дві смуги: як набір рядків став спільною мовою і як його змінили ─────
def fig_recordset_lineage():
    W, H = 1400, 500
    f = [text(W / 2, 34, "Спільна мова застосунку: спершу набір рядків, потім об'єкт",
              size=17, bold=True)]

    def card(cx, y, w, h, year, lines, fill, stroke):
        out = [rect(cx - w / 2, y, w, h, fill=fill, stroke=stroke, sw=1.9, rx=9)]
        out.append(text(cx, y + 26, year, size=13.5, color=INK, bold=True))
        out.append(line(cx - w / 2 + 16, y + 38, cx + w / 2 - 16, y + 38, color=stroke, sw=1.1))
        out.append(mtext(cx, y + 60, lines, size=10.5, color=INK, lh=1.4))
        return "".join(out)

    # ══ СМУГА 1: набір рядків росте ══
    f.append(text(45, 70, "НАБІР РЯДКІВ СТАЄ СПІЛЬНОЮ МОВОЮ", size=13, color=FIELD,
                  bold=True, anchor="start"))

    top = [
        (140,  "1992", ["ODBC 1.0 · DAO 1.0", "доступ є —", "спільної форми немає"]),
        (360,  "1993", ["VB 3.0: Data control", "сітка бере рядки", "просто з набору"]),
        (580,  "1995", ["RDO у VB 4.0", "курсор — на боці", "клієнта"]),
        (800,  "1996", ["ADO 1.0 · Recordset", "одна назва", "для всіх джерел"]),
        (1020, "1997", ["RDS 1.5", "набір їде далі", "без з'єднання"]),
        (1240, "2002", ["DataSet у .NET 1.0", "кілька таблиць,", "зв'язки, стан рядка"]),
    ]
    for cx, year, lines in top:
        f.append(card(cx, 86, 190, 112, year, lines, GRN, FIELD))
    for i in range(len(top) - 1):
        f.append(arrow(top[i][0] + 95, 142, top[i + 1][0] - 95, 142, color=MUTED, sw=1.7))

    # ══ поворот ══
    f.append(text(W / 2, 240, "після 2002-го спільною мовою застосунку став не набір рядків, а об'єкт",
                  size=12.5, color=POS, bold=True))
    f.append(line(45, 262, W - 45, 262, color=MUTED, sw=1.2, dash="6 5"))

    # ══ СМУГА 2: об'єкт витісняє набір ══
    f.append(text(45, 290, "СПІЛЬНОЮ МОВОЮ СТАЄ ОБ'ЄКТ", size=13, color=NEG,
                  bold=True, anchor="start"))

    bot = [
        (190,  "2001", ["Hibernate: рядок → об'єкт,", "мапінг стає буденністю"]),
        (530,  "2004", ["Rails з Active Record:", "одиниця у вебі — об'єкт-рядок"]),
        (870,  "2006", ["JSON стає RFC 4627:", "дріт більше не табличний"]),
        (1210, "2007–2008", ["LINQ to SQL, Entity Framework:", "Microsoft сама обирає об'єкти"]),
    ]
    for cx, year, lines in bot:
        f.append(card(cx, 300, 300, 100, year, lines, BLU, NEG))
    for i in range(len(bot) - 1):
        f.append(arrow(bot[i][0] + 150, 350, bot[i + 1][0] - 150, 350, color=MUTED, sw=1.7))

    f.append(text(W / 2, 448, "порядок у кожній смузі хронологічний; відстані не в масштабі часу",
                  size=11, color=MUTED, italic=True))

    return render(os.path.join(OUT, "recordset-lineage.svg"), W, H, *f)


# ── допоміжне: таблиця з колонками, типами й міткою стану ───────────────────
def coltable(x, y, name, cols, types, rows, colw,
             row_h=26, title_h=26, head_h=24, type_h=20, size=10.5):
    W = sum(colw)
    H = title_h + head_h + type_h + row_h * len(rows)
    f = [rect(x, y, W, H, fill=BG, stroke=MUTED, sw=1.6, rx=7)]
    f.append(rect(x, y, W, title_h, fill=FILL, stroke=MUTED, sw=1.4, rx=7))
    f.append(text(x + W / 2, y + title_h - 8, name, size=size + 1.5, color=INK, bold=True))

    yh = y + title_h
    f.append(line(x, yh, x + W, yh, color=MUTED, sw=1.2))
    cx = x
    for i, c in enumerate(cols):
        f.append(text(cx + colw[i] / 2, yh + head_h - 7, c, size=size, color=INK, bold=True))
        cx += colw[i]

    yt = yh + head_h
    cx = x
    for i, t in enumerate(types):
        f.append(text(cx + colw[i] / 2, yt + type_h - 6, t, size=size - 1.5, color=MUTED, italic=True))
        cx += colw[i]

    ydata = yt + type_h
    f.append(line(x, ydata, x + W, ydata, color=MUTED, sw=1.2))
    for r, row in enumerate(rows):
        ry = ydata + row_h * r
        if r:
            f.append(line(x, ry, x + W, ry, color=MUTED, sw=0.8, dash="4 4"))
        cx = x
        for i, v in enumerate(row):
            col = POS if (i == len(row) - 1 and v != "без змін") else INK
            f.append(text(cx + colw[i] / 2, ry + row_h / 2 + size * 0.35, v, size=size, color=col))
            cx += colw[i]

    cx = x
    for i in range(len(cols) - 1):
        cx += colw[i]
        f.append(line(cx, yh, cx, y + H, color=MUTED, sw=0.8, dash="3 4"))
    return "".join(f)


def dashframe(x1, y1, x2, y2, color=NEG, sw=1.5, dash="7 5"):
    return "".join([
        line(x1, y1, x2, y1, color=color, sw=sw, dash=dash),
        line(x2, y1, x2, y2, color=color, sw=sw, dash=dash),
        line(x2, y2, x1, y2, color=color, sw=sw, dash=dash),
        line(x1, y2, x1, y1, color=color, sw=sw, dash=dash),
    ])


# ── 5. Що всередині набору рядків ───────────────────────────────────────────
def fig_recordset_inside():
    W, H = 1360, 650
    f = [text(W / 2, 34, "Що всередині набору рядків", size=17, bold=True)]

    # ══ контракти ══
    f.append(text(70, 78, "ТАБЛИЦЯ КОНТРАКТІВ", size=13, color=FIELD, bold=True, anchor="start"))

    f.append(rect(70, 96, 240, 150, fill=GRN, stroke=FIELD, sw=1.8, rx=8))
    f.append(text(190, 120, "індекс за id", size=12, color=INK, bold=True))
    f.append(line(86, 130, 294, 130, color=FIELD, sw=1.1))
    f.append(mtext(190, 152, ["17 → слот 0", "18 → слот 1", "19 → слот 2"], size=11, lh=1.5))
    f.append(text(190, 218, "хеш-таблиця", size=11, color=MUTED, italic=True))
    f.append(text(190, 236, "пошук ≈ O(1)", size=11, color=FIELD, bold=True))

    f.append(arrow(316, 160, 366, 160, color=MUTED, sw=1.8))

    f.append(coltable(
        372, 96, "contracts",
        ["id", "product_id", "revenue", "signed_on", "стан"],
        ["int64", "int64", "копійки (int64)", "доба (int32)", "мітка"],
        [["17", "3", "100000", "20522", "без змін"],
         ["18", "4", "60000", "20531", "змінено"],
         ["19", "3", "90000", "20540", "додано"]],
        [70, 120, 150, 140, 120]))

    f.append(mtext(1170, 140, ["колонка стану — не дані,", "а мітка: що саме", "поїде в базу"],
                   size=11, color=MUTED, lh=1.4))

    # ══ визнання ══
    f.append(text(70, 320, "ТАБЛИЦЯ ВИЗНАНЬ", size=13, color=FIELD, bold=True, anchor="start"))

    f.append(rect(70, 338, 240, 160, fill=GRN, stroke=FIELD, sw=1.8, rx=8))
    f.append(text(190, 362, "вторинний індекс", size=12, color=INK, bold=True))
    f.append(text(190, 380, "за contract_id", size=11, color=INK))
    f.append(line(86, 390, 294, 390, color=FIELD, sw=1.1))
    f.append(mtext(190, 414, ["17 → [0, 1, 2]", "18 → [3]"], size=11, lh=1.5))
    f.append(text(190, 470, "«усі рядки контракту»", size=10.5, color=MUTED, italic=True))
    f.append(text(190, 488, "без обходу таблиці", size=10.5, color=FIELD, bold=True))

    f.append(arrow(316, 410, 366, 410, color=MUTED, sw=1.8))

    f.append(coltable(
        372, 338, "recognitions",
        ["id", "contract_id", "amount", "recognized_on", "стан"],
        ["int64", "int64", "копійки", "доба", "мітка"],
        [["101", "17", "33333", "20522", "без змін"],
         ["102", "17", "33333", "20582", "без змін"],
         ["103", "17", "33334", "20612", "без змін"],
         ["104", "18", "60000", "20531", "додано"]],
        [70, 120, 150, 140, 120]))

    f.append(mtext(1170, 400, ["без цього індексу", "«визнано на дату»", "перебирає всі визнання"],
                   size=11, color=POS, lh=1.4))

    f.append(text(W / 2, 580, "модуль не тримає ні рядка, ні покажчика на нього: між викликами живе тільки ключ",
                  size=12.5, color=INK, bold=True))
    f.append(text(W / 2, 606, "покажчик у C++ дійсний лише до наступної вставки — тому його не зберігають",
                  size=11.5, color=MUTED, italic=True))

    return render(os.path.join(OUT, "recordset-inside.svg"), W, H, *f)


# ── 6. Накопичені зміни й межа транзакції ───────────────────────────────────
def fig_change_boundary():
    W, H = 1300, 640
    f = [text(W / 2, 34, "Накопичені зміни й межа транзакції", size=17, bold=True)]

    # набір рядків
    f.append(rect(50, 120, 260, 180, fill=BG, stroke=MUTED, sw=1.7, rx=9))
    f.append(text(180, 146, "НАБІР РЯДКІВ", size=12.5, color=MUTED, bold=True))
    f.append(line(66, 156, 294, 156, color=MUTED, sw=1.1))
    f.append(mtext(180, 182, ["рядок 17 · без змін", "рядок 18 · змінено",
                              "рядок 19 · додано", "рядок 20 · вилучено"], size=11, lh=1.6))
    f.append(text(180, 274, "мітка — на кожному рядку", size=10.5, color=MUTED, italic=True))

    f.append(arrow(314, 200, 356, 200, color=MUTED, sw=1.8))

    # межа транзакції
    f.append(dashframe(360, 100, 1050, 300))
    f.append(text(370, 92, "ОДНА ТРАНЗАКЦІЯ", size=12.5, color=NEG, bold=True, anchor="start"))

    f.append(rect(390, 140, 250, 120, fill=FILL, stroke=LINE, sw=1.7, rx=8))
    f.append(text(515, 172, "changes()", size=12.5, color=INK, bold=True))
    f.append(mtext(515, 200, ["тільки помічені рядки —", "решта не турбує базу"],
                   size=11, color=MUTED, lh=1.4))

    f.append(arrow(644, 200, 686, 200, color=MUTED, sw=1.8))

    f.append(rect(690, 140, 320, 120, fill=FILL, stroke=LINE, sw=1.7, rx=8))
    f.append(text(850, 172, "ШЛЮЗ ТАБЛИЦІ", size=12.5, color=INK, bold=True))
    f.append(mtext(850, 200, ["INSERT · UPDATE · DELETE", "тут і тільки тут — SQL"],
                   size=11, color=MUTED, lh=1.4))

    # розгалуження
    f.append(line(850, 302, 850, 340, color=MUTED, sw=1.6))
    f.append(line(520, 340, 1000, 340, color=MUTED, sw=1.6))
    f.append(arrow(520, 340, 520, 380, color=MUTED, sw=1.6))
    f.append(arrow(1000, 340, 1000, 380, color=MUTED, sw=1.6))

    f.append(rect(360, 384, 320, 130, fill=GRN, stroke=FIELD, sw=1.9, rx=9))
    f.append(text(520, 412, "commit вдався", size=12.5, color=INK, bold=True))
    f.append(mtext(520, 440, ["accept(): мітки скинуто,", "вилучені рядки викинуто —",
                              "набір і база кажуть те саме"], size=11, color=INK, lh=1.45))

    f.append(rect(840, 384, 320, 130, fill=RED, stroke=POS, sw=1.9, rx=9))
    f.append(text(1000, 412, "commit упав → відкат", size=12.5, color=INK, bold=True))
    f.append(mtext(1000, 440, ["база незмінна, мітки ЛИШИЛИСЬ:", "повторити або reject()",
                               "до вихідних значень"], size=11, color=INK, lh=1.45))

    f.append(rect(170, 546, 960, 74, fill=RED, stroke=POS, sw=1.7, rx=9))
    f.append(mtext(650, 576,
                   [".NET-пастка: DataAdapter.Update сам кличе AcceptChanges на кожному вдалому рядку —",
                    "після відкату транзакції набір уже вважає себе збереженим. Лікує AcceptChangesDuringUpdate = false"],
                   size=11, color=INK, lh=1.5))

    return render(os.path.join(OUT, "change-boundary.svg"), W, H, *f)


if __name__ == "__main__":
    for fn in (fig_three_cuts, fig_module_anatomy, fig_recordset_spine, fig_recordset_lineage,
               fig_recordset_inside, fig_change_boundary):
        print(fn())
