# -*- coding: utf-8 -*-
"""Фігури до кроку «Вибір моделі реплікації»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#eafaf0"
BLUEFILL  = "#eef2fb"
REDFILL   = "#fdecea"


def fig_topology_anatomy():
    """Три моделі реплікації поруч: один лідер / мультилідер / безлідерна."""
    W, H = 1160, 520
    f = []

    # розділювачі панелей
    for sx in (388, 776):
        f.append(line(sx, 84, sx, 470, color=MUTED, sw=1, dash="4,5"))

    f.append(text(194, 66, "Один лідер", size=15, bold=True))
    f.append(text(582, 66, "Мультилідер", size=15, bold=True))
    f.append(text(970, 66, "Безлідерна", size=15, bold=True))

    # ── Панель 1: один лідер, три фоловери ──
    f.append(text(194, 108, "записи", size=12, color=MUTED))
    f.append(arrow(160, 118, 184, 158, color=POS, sw=1.8))
    f.append(arrow(228, 118, 204, 158, color=POS, sw=1.8))
    b, _, _ = textbox(194, 182, "лідер", size=13, fill=GREENFILL, stroke=FIELD, min_w=132, bold=True)
    f.append(b)
    for fx in (110, 194, 278):
        b, _, _ = textbox(fx, 328, "фоловер", size=11, fill=BLUEFILL, stroke=NEG, min_w=92)
        f.append(b)
        f.append(arrow(194, 206, fx, 306, color=LINE, sw=1.5))
    f.append(text(194, 410, "усі записи — в одного,", size=12, color=MUTED))
    f.append(text(194, 430, "фоловери лише читають", size=12, color=MUTED))
    f.append(text(194, 456, "0 конфліктів за побудовою", size=12.5, color=FIELD, italic=True))

    # ── Панель 2: два лідери, синхронізація, конфлікт ──
    f.append(text(520, 118, "запис", size=11, color=MUTED))
    f.append(text(644, 118, "запис", size=11, color=MUTED))
    f.append(arrow(520, 126, 520, 162, color=POS, sw=1.8))
    f.append(arrow(644, 126, 644, 162, color=POS, sw=1.8))
    b, _, _ = textbox(520, 186, "лідер", size=12, fill=BLUEFILL, stroke=NEG, min_w=96)
    f.append(b)
    b, _, _ = textbox(644, 186, "лідер", size=12, fill=BLUEFILL, stroke=NEG, min_w=96)
    f.append(b)
    # двобічна синхронізація
    f.append(arrow(556, 178, 608, 178, color=MUTED, sw=1.6))
    f.append(arrow(608, 196, 556, 196, color=MUTED, sw=1.6))
    f.append(text(582, 158, "копії в обидва боки", size=10.5, color=MUTED))
    b, _, _ = textbox(582, 268, "⚡ конфлікт", size=12, fill=REDFILL, stroke=POS, min_w=136, bold=True)
    f.append(b)
    f.append(arrow(536, 208, 566, 244, color=POS, sw=1.5))
    f.append(arrow(628, 208, 598, 244, color=POS, sw=1.5))
    f.append(text(582, 410, "кожен лідер пише локально,", size=12, color=MUTED))
    f.append(text(582, 430, "копії летять в обидва боки", size=12, color=MUTED))
    f.append(text(582, 456, "→ конфлікти", size=12.5, color=POS, italic=True))

    # ── Панель 3: безлідерна, кворум ──
    b, _, _ = textbox(970, 120, "клієнт", size=11, fill=FILL, stroke=MUTED, min_w=88)
    f.append(b)
    reps = (896, 970, 1044)
    for i, rx in enumerate(reps):
        acked = (i != 2)   # W=2 підтверджують, третій — ще ні
        col = FIELD if acked else MUTED
        fillc = GREENFILL if acked else "#eef1f4"
        b, _, _ = textbox(rx, 214, "репліка", size=11, fill=fillc, stroke=col, min_w=92)
        f.append(b)
        f.append(arrow(970, 138, rx, 190, color=(FIELD if acked else MUTED), sw=1.6))
    f.append(text(970, 268, "W = 2 підтверджують запис", size=11.5, color=FIELD)),
    f.append(text(970, 290, "читання з R реплік", size=11.5, color=MUTED))
    f.append(text(970, 410, "лідера нема; будь-який вузол", size=12, color=MUTED))
    f.append(text(970, 430, "приймає, вирішує кворум", size=12, color=MUTED))
    f.append(text(970, 456, "W + R > N", size=12.5, color=FIELD, italic=True))

    render(os.path.join(IMG, "topology-anatomy.svg"), W, H, *f,
           title="Три моделі реплікації: скільки місць приймають запис")


def fig_write_origin():
    """Один писар → одна історія; кілька писарів → дві версії стикаються."""
    W, H = 1120, 580
    f = []

    # ── Верх: один писар ──
    f.append(text(60, 74, "Один писар", size=15, bold=True, anchor="start"))
    for sy in (128, 176, 224):
        b, _, _ = textbox(140, sy, "запис", size=11, fill=FILL, stroke=MUTED, min_w=76)
        f.append(b)
    b, _, _ = textbox(316, 176, "одна\nчерга", size=12, fill=BLUEFILL, stroke=NEG, min_w=92)
    f.append(b)
    f.append(arrow(180, 128, 268, 162, color=MUTED, sw=1.5))
    f.append(arrow(180, 176, 268, 176, color=MUTED, sw=1.5))
    f.append(arrow(180, 224, 268, 190, color=MUTED, sw=1.5))
    # лінійна історія
    hist = (("v1: off", 470), ("v2: on", 610), ("v3: off", 750))
    prev = 364
    for label, hx in hist:
        b, _, _ = textbox(hx, 176, label, size=12, fill=GREENFILL, stroke=FIELD, min_w=104)
        f.append(b)
        f.append(arrow(prev, 176, hx - 54, 176, color=FIELD, sw=1.7))
        prev = hx + 54
    f.append(text(590, 256, "усі записи стають у чергу → одна історія, конфлікту нема",
                  size=12.5, color=FIELD, italic=True))

    # розділювач
    f.append(line(60, 300, W - 60, 300, color=MUTED, sw=1, dash="4,5"))

    # ── Низ: кілька писарів ──
    f.append(text(60, 344, "Кілька писарів", size=15, bold=True, anchor="start"))
    b, _, _ = textbox(150, 404, "застосунок\n→ off", size=11, fill=FILL, stroke=MUTED, min_w=118)
    f.append(b)
    b, _, _ = textbox(150, 486, "хаб\n→ on", size=11, fill=FILL, stroke=MUTED, min_w=118)
    f.append(b)
    b, _, _ = textbox(348, 404, "вузол A", size=12, fill=BLUEFILL, stroke=NEG, min_w=104)
    f.append(b)
    b, _, _ = textbox(348, 486, "вузол B", size=12, fill=BLUEFILL, stroke=NEG, min_w=104)
    f.append(b)
    f.append(arrow(210, 404, 294, 404, color=POS, sw=1.7))
    f.append(arrow(210, 486, 294, 486, color=POS, sw=1.7))
    # гілки стикаються в конфлікті
    b, _, _ = textbox(700, 445, "⚡ off ‖ on\nжодне не пізніше —\nзвести мусить хтось", size=12,
                      fill=REDFILL, stroke=POS, min_w=210, bold=True)
    f.append(b)
    f.append(arrow(402, 410, 588, 430, color=NEG, sw=1.7))
    f.append(arrow(402, 480, 588, 462, color=NEG, sw=1.7))
    f.append(text(500, 396, "гілка «off»", size=10.5, color=MUTED))
    f.append(text(500, 508, "гілка «on»", size=10.5, color=MUTED))
    f.append(text(430, 548, "два незалежні писарі → дві версії того самого ключа",
                  size=12.5, color=POS, italic=True))

    render(os.path.join(IMG, "write-origin.svg"), W, H, *f,
           title="Звідки береться конфлікт: один писар проти кількох")


def fig_decision_axis():
    """Дерево рішення: один лідер — дефолт; вихід крізь заставу конфліктів."""
    W, H = 860, 600
    f = []
    cx = 320

    # дефолт
    b, _, _ = textbox(cx, 84, "Один лідер — дефолт:\nлишайся, поки не назвався тиск",
                      size=13, fill=GREENFILL, stroke=FIELD, min_w=380, bold=True)
    f.append(b)
    f.append(arrow(cx, 114, cx, 152, color=LINE, sw=1.8))

    # питання 1
    b, _, _ = textbox(cx, 186, "чи мусять записи прийматися\nв КІЛЬКОХ місцях одразу?",
                      size=12.5, fill=FILL, stroke=MUTED, min_w=352)
    f.append(b)

    # «ні» → лишаєшся
    f.append(arrow(cx + 178, 186, cx + 258, 186, color=FIELD, sw=1.7))
    f.append(text(cx + 214, 174, "ні", size=12, color=FIELD, bold=True))
    b, _, _ = textbox(cx + 372, 186, "лишаєшся:\nодин лідер", size=12,
                      fill=GREENFILL, stroke=FIELD, min_w=150)
    f.append(b)

    # «так» вниз крізь заставу
    f.append(arrow(cx, 214, cx, 258, color=POS, sw=1.8))
    f.append(text(cx + 18, 238, "так", size=12, color=POS, bold=True))
    b, _, _ = textbox(cx, 292, "⚡ застава: успадковуєш конфлікти", size=13,
                      fill=REDFILL, stroke=POS, min_w=392, bold=True)
    f.append(b)
    f.append(arrow(cx, 320, cx, 362, color=LINE, sw=1.8))

    # питання 2
    b, _, _ = textbox(cx, 398, "є природний «дім» на запис?\n(регіон · користувач · пристрій)",
                      size=12, fill=FILL, stroke=MUTED, min_w=352)
    f.append(b)

    # дві розв'язки
    f.append(arrow(cx - 150, 428, 190, 492, color=NEG, sw=1.7))
    f.append(text(214, 470, "так", size=12, color=NEG, bold=True))
    b, _, _ = textbox(190, 526, "Мультилідер\nлідер на регіон", size=12,
                      fill=BLUEFILL, stroke=NEG, min_w=196, bold=True)
    f.append(b)

    f.append(arrow(cx + 150, 428, 520, 492, color=NEG, sw=1.7))
    f.append(text(470, 470, "ні", size=12, color=NEG, bold=True))
    b, _, _ = textbox(560, 526, "Безлідерна\nкворум W + R > N", size=12,
                      fill=BLUEFILL, stroke=NEG, min_w=196, bold=True)
    f.append(b)

    render(os.path.join(IMG, "decision-axis.svg"), W, H, *f,
           title="Вибір моделі: дефолт і застава на виході")


def fig_worksheet_grid():
    """Аркуш вибору: 4 набори даних DH × 3 ворота → модель + названа ціна."""
    # колонки: (x, w, заголовок)
    cols = [
        (20,  152, "Набір даних DH"),
        (176, 214, "G1 · де народжуються\nзаписи"),
        (394, 224, "G2 · доступність запису\nпід розривом незаперечна?"),
        (622, 150, "G3 · природний\nдім на запис?"),
        (776, 244, "Модель"),
        (1024, 200, "Названа ціна"),
    ]
    W = cols[-1][0] + cols[-1][1] + 20
    # рядки даних: список клітинок під кожну колонку
    rows = [
        ["Твін дому",
         "один хаб на дім\n→ одне місце",
         "ні — хаб буферить,\nдоллється по лінії",
         "так —\nдім / регіон",
         "один лідер +\nчитальні репліки",
         "пауза на\nfailover"],
        ["Реєстр\n(назви, тариф)",
         "одна адмін-стежка\n→ одне місце",
         "ні — правлять зрідка,\nfail-closed за сумніву",
         "так —\nакаунт / регіон",
         "один лідер +\nрепліки",
         "пауза на failover\n(пишемо рідко)"],
        ["Телеметрія\n(потік давачів)",
         "кожен давач — свій\nрядок; спільного\nключа НЕМА",
         "ні — буфер на хабі,\nдренаж по лінії",
         "н/д — нема\nза що битися",
         "один лідер +\nрепліки (append-only)",
         "пауза на failover;\nвтрат 0 (черга)"],
        ["Крос-регіон\n(гіпотеза)",
         "дім належить ОДНОМУ\nрегіону → одне\nмісце на ключ",
         "ні — той самий\nхаб-буфер + fail-closed",
         "так —\nрегіон дому",
         "один лідер НА РЕГІОН\n(гео-шард) + репліки",
         "крос-регіон-читання\nплатять RTT"],
    ]
    row_y = [110, 190, 270, 352]
    row_h = [76, 76, 76, 84]
    H = row_y[-1] + row_h[-1] + 44
    f = []
    # заголовок таблиці
    hy, hh = 46, 56
    for (cx, cw, title) in cols:
        f.append(fitbox(cx, hy, cw, hh, title, size=12, pad=6,
                        fill=BLUEFILL, stroke=NEG, bold=True, color=INK))
    # рядки
    for r, cells in enumerate(rows):
        y, h = row_y[r], row_h[r]
        for c, (cx, cw, _) in enumerate(cols):
            txt = cells[c]
            if c == 0:
                fill, stroke, bold, color = FILL, MUTED, True, INK
            elif c == 4:                       # колонка «Модель» — зелена
                fill, stroke, bold, color = GREENFILL, FIELD, True, INK
            elif c == 5:                       # колонка «Ціна»
                fill, stroke, bold, color = "#fff8ec", "#c9922e", False, INK
            else:
                fill, stroke, bold, color = FILL, MUTED, False, INK
            f.append(fitbox(cx, y, cw, h, txt, size=11.5, pad=6,
                            fill=fill, stroke=stroke, bold=bold, color=color))
    # підсумковий пасок
    fy = row_y[-1] + row_h[-1] + 10
    f.append(fitbox(20, fy, W - 40, 30,
                    "G1 і G2 порожні на КОЖНОМУ рядку → жоден тиск на мультимастер не назвався → один лідер скрізь",
                    size=13, pad=6, fill=GREENFILL, stroke=FIELD, bold=True))
    render(os.path.join(IMG, "worksheet-grid.svg"), W, H, *f,
           title="Аркуш вибору: набори даних DH крізь три ворота")


def fig_conflict_count():
    """Скільки конфліктів/год народжує другий писар на твіні — і нуль за одного лідера."""
    W, H = 940, 500
    f = []

    base_y = 410          # вісь-основа
    top_y = 92            # стеля області стовпців
    span = base_y - top_y # 318 px під максимум 150k
    vmax = 150000.0

    def bar_h(v):
        return span * (v / vmax)

    # вісь
    f.append(line(150, base_y, W - 40, base_y, color=INK, sw=1.6))
    f.append(text(150, base_y + 24, "0", size=12, color=MUTED, anchor="middle"))

    bars = [
        (230, "Один лідер", "(будь-який Δ)", 0,      FIELD,  GREENFILL),
        (405, "Наївний active-active", "Δ = 20 мс", 20000, "#e0913a", "#fff1df"),
        (580, "Наївний active-active", "Δ = 80 мс", 80000, POS,     REDFILL),
        (755, "Наївний active-active", "Δ = 150 мс", 150000, POS,    REDFILL),
    ]
    bw = 118
    for (cx, name, sub, val, col, fillc) in bars:
        h = bar_h(val)
        x = cx - bw / 2
        if val == 0:
            # нульовий стовпець — плаский маркер на осі
            f.append(line(x, base_y, x + bw, base_y, color=col, sw=4))
            f.append(text(cx, base_y - 12, "0", size=15, color=col, anchor="middle", bold=True))
        else:
            f.append(rect(x, base_y - h, bw, h, fill=fillc, stroke=col, sw=1.8, rx=4))
            lbl = ("%d тис." % (val // 1000))
            f.append(text(cx, base_y - h - 12, lbl, size=14, color=col, anchor="middle", bold=True))
        # підпис під віссю (дворядковий)
        f.append(text(cx, base_y + 24, name, size=11.5, color=INK, anchor="middle", bold=True))
        f.append(text(cx, base_y + 40, sub, size=11, color=MUTED, anchor="middle"))

    # вертикальна вісь-підпис
    f.append(text(150, top_y - 30, "конфлікти / год", size=13, color=INK, anchor="start", bold=True))
    f.append(text(150, top_y - 12,
                  "500 тис. домів · 120 записів/дім·год · p = 0.5",
                  size=11.5, color=MUTED, anchor="start"))
    # нотатка про масштабування — у вільному верхньо-лівому кутку, повз стовпці
    b, _, _ = textbox(430, 152,
                      "↑ лінійно з затримкою Δ\n↑ КВАДРАТИЧНО з частотою\nзапису W у ключ",
                      size=12, fill=FILL, stroke=MUTED, min_w=228)
    f.append(b)

    render(os.path.join(IMG, "conflict-count.svg"), W, H, *f,
           title="Ціна другого писаря на твіні: конфлікти проти нуля")


def fig_lineage_tree():
    """Родовід трьох моделей: одне питання → три гілки, у кожної свій предок."""
    W, H = 1200, 620
    f = []

    b, _, _ = textbox(600, 66, "Одне питання:\nде можна приймати запис?",
                      size=14, fill=FILL, stroke=MUTED, min_w=392, bold=True)
    f.append(b)

    heads = ((214, "Один лідер", GREENFILL, FIELD),
             (600, "Мультилідер", BLUEFILL, NEG),
             (990, "Безлідерна", BLUEFILL, NEG))
    for hx, label, fill, stroke in heads:
        f.append(arrow(600, 96, hx, 156, color=LINE, sw=1.6))
        b, _, _ = textbox(hx, 178, label, size=14, fill=fill, stroke=stroke,
                          min_w=176, bold=True)
        f.append(b)

    # ── гілка «Один лідер» ──
    left = (("первинний примірник\n(primary copy)\nЕлсберг · Дей, 1976", 300),
            ("«master/slave» →\nprimary / replica\nу ранніх СУБД", 442))
    prev_bottom = 198
    for s, cy in left:
        b, _, _ = textbox(214, cy, s, size=11.5, fill=GREENFILL, stroke=FIELD, min_w=250)
        f.append(b)
        f.append(arrow(214, prev_bottom, 214, cy - 36, color=FIELD, sw=1.4))
        prev_bottom = cy + 36

    # ── гілка «Мультилідер» ──
    mid = (("Lotus Notes, 1989\nдвобічна реплікація", 288),
           ("Bayou · Xerox PARC · 1995\nофлайн / мобільні", 388),
           ("CouchDB, 2005\nмультимастер у вебі", 488))
    prev_bottom = 198
    for s, cy in mid:
        b, _, _ = textbox(600, cy, s, size=11.5, fill=BLUEFILL, stroke=NEG, min_w=286)
        f.append(b)
        f.append(arrow(600, prev_bottom, 600, cy - 28, color=NEG, sw=1.4))
        prev_bottom = cy + 28

    # ── гілка «Безлідерна» ──
    b, _, _ = textbox(990, 288, "Amazon Dynamo\nSOSP 2007", size=12,
                      fill=BLUEFILL, stroke=NEG, min_w=210, bold=True)
    f.append(b)
    f.append(arrow(990, 198, 990, 262, color=NEG, sw=1.4))
    b, _, _ = textbox(990, 410,
                      "кворуми N·R·W · sloppy quorum\nhinted handoff · версійні вектори",
                      size=11, fill=FILL, stroke=MUTED, min_w=344)
    f.append(b)
    f.append(arrow(990, 314, 990, 384, color=NEG, sw=1.4))

    f.append(text(600, 566,
                  "Три гілки — три болі, не меню з трьох рівних; кожну викувала окрема потреба.",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, "lineage-tree.svg"), W, H, *f,
           title="Родовід трьох реплікацій: одне питання, три предки")


def fig_pendulum():
    """Маятник дефолту: суворість → доступність (2000-ті) → знову суворість + автозаміна."""
    W, H = 1200, 560
    f = []

    f.append(line(150, 150, 1120, 150, color=MUTED, sw=1, dash="3,6"))
    f.append(line(150, 410, 1120, 410, color=MUTED, sw=1, dash="3,6"))
    f.append(text(20, 44, "СУВОРІСТЬ", size=13, color=FIELD, bold=True, anchor="start"))
    f.append(text(20, 60, "один авторитетний примірник", size=11, color=MUTED, anchor="start"))
    f.append(text(150, 452, "ДОСТУПНІСТЬ ЗАПИСУ", size=13, color=POS, bold=True, anchor="start"))
    f.append(text(150, 470, "корзина, що завжди пише", size=11, color=MUTED, anchor="start"))

    pts = [(250, 168), (560, 402), (820, 214), (1060, 150)]
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        f.append(line(x1, y1, x2, y2, color=INK, sw=2.6))
    for x, y in pts:
        f.append(circle(x, y, 7, fill=BG, stroke=INK, sw=2.4))

    b, _, _ = textbox(268, 96, "1976 · первинний примірник\n(Елсберг–Дей) → один лідер\nстає тихим дефолтом",
                      size=11.5, fill=GREENFILL, stroke=FIELD, min_w=300)
    f.append(b)
    b, _, _ = textbox(556, 478, "2007 · Amazon Dynamo\nкорзина «завжди пише» →\nбезлідерна, кворуми в мейнстрим",
                      size=11.5, fill=REDFILL, stroke=POS, min_w=320, bold=True)
    f.append(b)
    b, _, _ = textbox(820, 116, "2012 · Google Spanner\nконсенсус (Paxos) на шард",
                      size=11.5, fill=BLUEFILL, stroke=NEG, min_w=272)
    f.append(b)
    b, _, _ = textbox(1048, 300, "2015 · CockroachDB\nRaft на діапазон:\nсуворість + автозаміна",
                      size=11.5, fill=BLUEFILL, stroke=NEG, min_w=252, bold=True)
    f.append(b)

    f.append(text(600, 62, "маятник індустрії: доступність — і назад до суворості",
                  size=12.5, color=INK, bold=True))
    f.append(text(600, 528,
                  "мультилідер — паралельна гілка (офлайн / гео): Notes 1989 · Bayou 1995 · CouchDB 2005",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "pendulum.svg"), W, H, *f,
           title="Маятник дефолту реплікації")


if __name__ == "__main__":
    fig_topology_anatomy()
    fig_write_origin()
    fig_decision_axis()
    fig_worksheet_grid()
    fig_conflict_count()
    fig_lineage_tree()
    fig_pendulum()
    print("OK: topology-anatomy.svg, write-origin.svg, decision-axis.svg, "
          "worksheet-grid.svg, conflict-count.svg, lineage-tree.svg, pendulum.svg")
