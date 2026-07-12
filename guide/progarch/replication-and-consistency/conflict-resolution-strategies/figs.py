# -*- coding: utf-8 -*-
"""Фігури до кроку «Стратегії розв'язання конфліктів»
(guide/progarch/replication-and-consistency/conflict-resolution-strategies)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")

GREEN_F = "#eafaf1"
BLUE_F = "#eaf0fd"
RED_F = "#fdecea"
AMBER_F = "#fdf3e7"; AMBER_S = "#e08a3c"


def cbox(cx, cy, w, h, s, **kw):
    """Рамка з центром (cx,cy) — текст автоматично влазить (fitbox)."""
    return fitbox(cx - w / 2.0, cy - h / 2.0, w, h, s, **kw)


def conflict_born():
    """Два телефони офлайн перейменовують ту саму кімнату; синк зводить два значення разом."""
    W, H = 960, 380
    f = []
    # доріжки
    ay, by = 130, 275
    f.append(text(96, ay + 5, "телефон А", size=13, color=MUTED, anchor="end"))
    f.append(line(140, ay, 600, ay, color=LINE))
    f.append(text(96, by + 5, "телефон Б", size=13, color=MUTED, anchor="end"))
    f.append(line(140, by, 600, by, color=LINE))

    # офлайн-зона між подіями
    f.append(text(370, 203, "офлайн — репліки не бачать одна одну", size=12,
                  color=MUTED, italic=True))

    # запис А
    f.append(circle(330, ay, 8, fill=GREEN_F, stroke=FIELD, sw=2))
    f.append(text(330, ay - 18, "назва ← «Вітальня»", size=12, color=FIELD))
    # запис Б
    f.append(circle(370, by, 8, fill=BLUE_F, stroke=NEG, sw=2))
    f.append(text(370, by + 30, "назва ← «Зал»", size=12, color=NEG))

    # синхронізація зводить обидва до однієї репліки
    f.append(text(548, 150, "синк", size=12, color=MUTED, anchor="end"))
    f.append(arrow(338, ay, 690, 178, color=FIELD))
    f.append(arrow(378, by, 690, 214, color=NEG))
    f.append(cbox(800, 196, 244, 96,
                  "одна репліка, два значення:\n«Вітальня»  ?  «Зал»\nхто правий — факту немає",
                  size=13, fill=RED_F, stroke=POS, bold=True))

    render(os.path.join(IMG, "conflict-born.svg"), W, H, *f)


def four_strategies():
    """Один конфлікт — чотири родини стратегій розв'язання."""
    W, H = 1040, 480
    f = []
    # вхідний конфлікт
    f.append(cbox(520, 66, 440, 54, "конфлікт: назва = «Вітальня»  проти  «Зал»",
                  size=15, fill=RED_F, stroke=POS, bold=True))

    cols = [
        (152, "1 · Обрати переможця", GREEN_F, FIELD,
         "LWW: новіша мітка\nперемагає;\n«Вітальня» — втрачено",
         "ціна: губиться\nодин намір"),
        (388, "2 · Лишити обидва", GREEN_F, FIELD,
         "двійники (siblings):\n{ «Вітальня», «Зал» }\n→ вирішує застосунок",
         "ціна: складне читання,\nвоскресіння видалених"),
        (624, "3 · Тип без конфліктів", GREEN_F, FIELD,
         "CRDT: зливання\nвбудоване в тип →\nскрізь однаковий стан",
         "ціна: змоделювати\nдані під це"),
        (860, "4 · Уникнути", GREEN_F, FIELD,
         "усі записи ключа —\nодному власнику →\nконфлікту не існує",
         "ціна: менша\nдоступність ключа"),
    ]
    for cx, title, fill, stroke, body, cost in cols:
        # контейнер панелі
        f.append(rect(cx - 106, 122, 212, 214, fill=BG, stroke=MUTED, sw=1.3))
        # стрілка від входу до панелі
        f.append(arrow(520 + (cx - 520) * 0.12, 94, cx, 120, color=MUTED))
        # заголовок
        f.append(text(cx, 150, title, size=13, bold=True))
        f.append(line(cx - 92, 162, cx + 92, 162, color=MUTED, dash="3 3"))
        # тіло
        f.append(cbox(cx, 232, 190, 108, body, size=12, fill=fill, stroke=stroke))
        # ціна
        f.append(mtext(cx, 300, cost, size=11, color=POS, lh=1.25))
    render(os.path.join(IMG, "four-strategies.svg"), W, H, *f)


def convergence():
    """Три репліки дістають ті самі оновлення в різному порядку — зливаються в один стан."""
    W, H = 980, 440
    f = []
    f.append(text(60, 56, "оновлення:", size=12, color=MUTED, anchor="start"))
    f.append(cbox(210, 52, 118, 34, "+ «молоко»", size=12, fill=GREEN_F, stroke=FIELD))
    f.append(cbox(340, 52, 108, 34, "+ «хліб»", size=12, fill=BLUE_F, stroke=NEG))
    f.append(text(430, 56, "(два одночасні записи в спільний список)", size=12,
                  color=MUTED, anchor="start"))

    rows = [
        (140, "репліка 1", [("+ «молоко»", GREEN_F, FIELD), ("+ «хліб»", BLUE_F, NEG)]),
        (240, "репліка 2", [("+ «хліб»", BLUE_F, NEG), ("+ «молоко»", GREEN_F, FIELD)]),
        (340, "репліка 3", [("+ «молоко»", GREEN_F, FIELD), ("+ «хліб»", BLUE_F, NEG),
                            ("+ «молоко»", GREEN_F, FIELD)]),
    ]
    for y, label, toks in rows:
        f.append(text(70, y + 5, label, size=13, color=MUTED, anchor="start"))
        x = 190
        for i, (s, fill, stroke) in enumerate(toks):
            faded = (label == "репліка 3" and i == 2)
            f.append(cbox(x, y, 104, 32, s, size=11,
                          fill=(BG if faded else fill), stroke=(MUTED if faded else stroke)))
            if faded:
                f.append(text(x, y + 27, "(повтор)", size=9, color=MUTED))
            x += 112
        f.append(arrow(x - 44, y, x + 30, y, color=MUTED))
        f.append(cbox(x + 118, y, 168, 40, "{ молоко, хліб }", size=13,
                      fill=GREEN_F, stroke=FIELD, bold=True))

    # спільний підсумок
    f.append(line(770, 118, 770, 362, color=FIELD, sw=2))
    f.append(mtext(792, 232, "усі\nрепліки\nоднакові", size=13, color=FIELD, bold=True, anchor="start"))

    f.append(text(W / 2.0, 410,
                  "зливання комутативне, асоціативне та ідемпотентне → ні порядок, ні повтори не змінюють підсумок",
                  size=13, color=MUTED, italic=True))
    render(os.path.join(IMG, "convergence.svg"), W, H, *f)


def decision_map():
    """Вид даних → яку стратегію конфлікту брати."""
    W, H = 1000, 380
    f = []
    f.append(text(280, 44, "вид даних", size=14, bold=True))
    f.append(text(720, 44, "як розв'язувати конфлікт", size=14, bold=True))
    f.append(line(60, 58, 940, 58, color=MUTED))

    rows = [
        ("останнє показане значення давача", "LWW — новіше = правда", GREEN_F, FIELD),
        ("спільний набір / список", "CRDT — об'єднання, без втрат", GREEN_F, FIELD),
        ("перейменування (низька ціна)", "LWW + позначка або спитати", AMBER_F, AMBER_S),
        ("гроші · замки · «рівно раз»", "НЕ eventual: один власник / консенсус", RED_F, POS),
    ]
    y = 108
    for left, right, fill, stroke in rows:
        f.append(cbox(280, y, 380, 56, left, size=13, fill=FILL, stroke=LINE))
        f.append(arrow(478, y, 528, y, color=MUTED))
        f.append(cbox(722, y, 400, 56, right, size=13, fill=fill, stroke=stroke, bold=True))
        y += 76
    render(os.path.join(IMG, "decision-map.svg"), W, H, *f)


def lww_vs_orset():
    """Ті самі оновлення спільного списку → LWW губить елемент, OR-Set береже все
    (для вставки proj-merge-convergence)."""
    W, H = 1000, 470
    f = []
    # верх — спільний набір оновлень
    f.append(cbox(500, 72, 810, 96,
                  "ті самі оновлення спільної сцени «Вечір кіно»:\n"
                  "A: + торшер      B: + гірлянда   (одночасно)\n"
                  "потім: − торшер (бачив тег a1)      C: + торшер (новий тег c1)",
                  size=13, fill=BLUE_F, stroke=NEG))
    # дві гілки
    f.append(arrow(500, 120, 272, 176, color=MUTED))
    f.append(arrow(500, 120, 728, 176, color=MUTED))

    # ліва колонка — LWW
    f.append(text(272, 200, "LWW на цілому значенні списку", size=14, bold=True))
    f.append(cbox(272, 306, 320, 150,
                  "фінал:  { гірлянда }\n \n«торшер» тихо зник:\nперезапис затер додавання,\nякого його автор не бачив",
                  size=13, fill=RED_F, stroke=POS))
    f.append(text(272, 408, "один реальний намір загублено", size=12, color=POS, italic=True))

    # права колонка — OR-Set
    f.append(text(728, 200, "OR-Set — унікальні теги на елемент", size=14, bold=True))
    f.append(cbox(728, 306, 340, 150,
                  "фінал:  { гірлянда, торшер }\n \nусі додавання збережено;\nвидалення тега a1 тримається,\nа новий тег c1 живе далі",
                  size=13, fill=GREEN_F, stroke=FIELD))
    f.append(text(728, 408, "нічого не втрачено, без воскресіння", size=12, color=FIELD, italic=True))

    # низ
    f.append(text(W / 2.0, 448,
                  "обидві стратегії сходяться — але LWW сходиться до НЕПОВНОГО списку",
                  size=13, color=MUTED, italic=True))
    render(os.path.join(IMG, "lww-vs-orset.svg"), W, H, *f)


def lineage_timeline():
    """Три віхи розв'язання конфліктів і міграція відповідальності за злиття
    (для вставки hist-conflict-resolution-lineage)."""
    W, H = 1060, 470
    f = []
    f.append(text(W / 2.0, 34, "Три віхи: як мігрувала відповідальність за злиття",
                  size=16, bold=True))
    # вісь часу
    f.append(line(120, 120, 940, 120, color=LINE, sw=2))
    f.append(text(W / 2.0, 300, "— хто виконує злиття —", size=12, color=MUTED, italic=True))

    cols = [
        (200, "1995", AMBER_F, AMBER_S,
         "Bayou · Xerox PARC\nSOSP 1995\nмерж-процедури (Tcl)\n+ перевірки залежностей",
         "АВТОР ЗАПИСУ →\nмерж-скрипт при записі"),
        (530, "2007", BLUE_F, NEG,
         "Dynamo · Amazon\nSOSP 2007\nвекторні годинники\n+ двійники (siblings)",
         "ЗАСТОСУНОК →\nзводить двійники на читанні"),
        (860, "2011", GREEN_F, FIELD,
         "CRDT · INRIA й партнери\nSSS-2011 · RR-7506\nтипи, що зливаються\nсамі, без координації",
         "САМ ТИП ДАНИХ →\nвручну зводити нічого"),
    ]
    for x, year, fill, stroke, body, resp in cols:
        f.append(circle(x, 120, 9, fill=fill, stroke=stroke, sw=2.5))
        f.append(text(x, 100, year, size=16, color=stroke, bold=True))
        f.append(line(x, 131, x, 158, color=MUTED))
        f.append(cbox(x, 212, 284, 104, body, size=13, fill=fill, stroke=stroke))
        f.append(cbox(x, 360, 252, 66, resp, size=12, fill=BG, stroke=stroke))

    # стрілки міграції відповідальності зліва направо
    f.append(arrow(332, 360, 402, 360, color=MUTED))
    f.append(arrow(662, 360, 732, 360, color=MUTED))

    f.append(text(W / 2.0, 445,
                  "від ручних процедур злиття (Bayou) до типізованого сходження без координації (CRDT)",
                  size=13, color=MUTED, italic=True))
    render(os.path.join(IMG, "lineage-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    conflict_born()
    four_strategies()
    convergence()
    decision_map()
    lww_vs_orset()
    lineage_timeline()
    print("ok")
