# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"


def fig_last_translation():
    """Помилка підіймається крізь внутрішні шари (recap), тоді проходить
    останню, мережеву межу — і виходить назовні як HTTP-контракт до чужих клієнтів."""
    W, H = 1060, 440
    f = []

    # ── ліворуч: внутрішні шари (recap модуля меж), приглушено ──
    f.append(fitbox(45, 62, 235, 30, "усередині — наш код", size=13, bold=True,
                    fill=BG, stroke="#c8ced6", color=MUTED))
    f.append(fitbox(45, 100, 235, 62, "застосунок · API-хендлер", size=13, fill=NEUT))
    f.append(fitbox(45, 190, 235, 62, "політика", size=13, fill=NEUT))
    f.append(fitbox(45, 280, 235, 62, "драйвер давача · I2C", size=13, fill=NEUT))
    # збій підіймається крізь стек
    f.append(arrow(300, 320, 300, 118, color="#b8bfc8", sw=2))
    f.append(text(316, 232, "збій ↑", size=12, color=MUTED, anchor="start"))

    # ── переклад на краю ──
    f.append(fitbox(360, 168, 190, 96, "переклад на краю\n\nдоменна → HTTP", size=13,
                    bold=True, fill=BG, stroke=INK))
    f.append(arrow(280, 131, 360, 200))                       # застосунок → мапер

    # ── межа мережі (пунктир) ──
    f.append(text(590, 60, "межа мережі", size=12, color=MUTED))
    f.append(line(590, 74, 590, 392, color=MUTED, sw=1.6, dash="7 6"))

    # ── назовні: HTTP-відповідь як контракт ──
    f.append(fitbox(622, 156, 210, 120,
                    "503 device_unavailable\n\ncode · detail\nRetry-After · requestId",
                    size=13, bold=True, fill=AMBER_T, stroke=AMBER))
    f.append(arrow(550, 216, 622, 216))                       # мапер → відповідь (крізь межу)

    # ── праворуч: чужі клієнти ──
    f.append(fitbox(858, 62, 175, 30, "чужий світ — не ти", size=13, bold=True,
                    fill=BG, stroke="#c8ced6", color=MUTED))
    clients = [("панель ×50 000", 100), ("застосунок", 188), ("чужа інтеграція", 276)]
    for label, cy in clients:
        f.append(fitbox(858, cy, 175, 58, label, size=13, fill=BLUE_T, stroke=NEG))
        f.append(arrow(832, 216, 858, cy + 29, color="#9aa4b0"))

    render(os.path.join(OUT, 'last-translation.svg'), W, H, *f,
           title="Остання трансляція помилки — єдина, що виходить назовні")


def fig_two_readers():
    """Одна відповідь на збій має два канали до двох читачів:
    машинний code (стабільний контракт) і людський detail (вільно змінний)."""
    W, H = 960, 360
    f = []

    # джерело — одна помилка
    f.append(fitbox(55, 148, 235, 74, "одна відповідь\nна збій", size=15, bold=True,
                    fill=NEUT, stroke=INK))

    # верхня гілка — code → машина (зелене, стабільне)
    f.append(arrow(290, 175, 452, 118))
    f.append(fitbox(460, 74, 450, 92,
                    "code  →  КОД клієнта\nстабільний ярлик · switch(code)\nконтракт — не міняється НІКОЛИ",
                    size=14, bold=True, fill=GREEN_T, stroke=FIELD))

    # нижня гілка — detail → людина (бурштин, змінне)
    f.append(arrow(290, 195, 452, 252))
    f.append(fitbox(460, 208, 450, 92,
                    "detail  →  ОКО людини\nпереклад · переписати · лагідніше\nне контракт — вільно змінюється",
                    size=14, bold=True, fill=AMBER_T, stroke=AMBER))

    render(os.path.join(OUT, 'two-readers.svg'), W, H, *f,
           title="Дві авдиторії однієї помилки — код і повідомлення")


def fig_who_acts():
    """Клас статусу відповідає на питання «хто може діяти»:
    4xx — твій бік (не повторюй), 5xx — сервер (повтори), 429 — сповільнись."""
    W, H = 980, 392
    f = []

    f.append(fitbox(340, 56, 300, 54, "клієнт отримав «ні» — що робити?",
                    size=15, bold=True, fill=NEUT, stroke=INK))

    cols = [
        (55,  "4xx", "твій бік:\nвиправ запит,\nне повторюй той самий", POS,   RED_T),
        (380, "5xx", "сервер:\nтой самий запит\nможна повторити",       FIELD, GREEN_T),
        (705, "429", "сповільнись:\nповтори після\nRetry-After",        AMBER, AMBER_T),
    ]
    cw = 220
    for x, code, action, col, tint in cols:
        cx = x + cw / 2
        f.append(arrow(490, 110, cx, 158))
        f.append(fitbox(x, 160, cw, 56, code, size=24, bold=True, stroke=col, fill=BG))
        f.append(arrow(cx, 218, cx, 250))
        f.append(fitbox(x, 252, cw, 96, action, size=14, stroke=col, fill=tint))

    render(os.path.join(OUT, 'who-acts.svg'), W, H, *f,
           title="Клас статусу = хто може діяти")


def fig_one_table():
    """Реєстр помилок як ДАНІ — одне джерело, з якого родиться і відповідь у проді,
    і golden-знімок контрактного тесту, і публічний каталог кодів."""
    W, H = 1100, 410
    f = []

    # ── центр-ліворуч: реєстр (таблиця-дані) ──
    f.append(rect(70, 140, 444, 232, fill=NEUT, stroke=INK, sw=1.6))
    f.append(text(292, 170, "реєстр помилок — це ДАНІ (один масив рядків)",
                  size=13, bold=True))
    f.append(line(86, 182, 498, 182, color="#c8ced6", sw=1.2))
    rows = [
        "DeviceNotFound  →  404 · device_not_found",
        "DeviceUnavailable  →  503 · device_unavailable (retry)",
        "InvalidCommand  →  400 · invalid_command",
        "RateLimited  →  429 · rate_limited (retry)",
        "(усе інше)  →  500 · internal — непрозоро",
    ]
    for i, r in enumerate(rows):
        f.append(text(92, 210 + i * 28, r, size=12, anchor="start"))

    # ── праворуч: три споживачі однієї таблиці ──
    cons = [
        (150, "handler toProblem (рантайм)\n→ конверт application/problem+json"),
        (248, "контрактний тест (CI)\n→ golden-знімок; червоніє на зміну форми"),
        (346, "публічний каталог\n→ коди й type-URL у docs"),
    ]
    for cy, label in cons:
        f.append(arrow(514, 256, 628, cy))
        f.append(fitbox(628, cy - 38, 430, 76, label, size=13, fill=BLUE_T, stroke=NEG))

    render(os.path.join(OUT, 'one-table.svg'), W, H, *f,
           title="Одна таблиця — три читачі: рантайм, тест, документація")


def fig_redaction_wall():
    """Гілка «усе інше»: неочікуваний виняток лишає все нутро в журналі ВДОМА,
    а назовні крізь стіну редакції проходить лише непрозорий конверт із reqId."""
    W, H = 1100, 420
    f = []

    # сирий баг заходить у межу
    f.append(fitbox(60, 175, 250, 92, "неочікуваний виняток\n(TypeError · SQL · стек)",
                    size=14, bold=True, fill=RED_T, stroke=POS))
    f.append(arrow(310, 221, 392, 221))

    # гілка default ловить будь-що
    f.append(fitbox(398, 168, 214, 106, "гілка «усе інше»\n= default\nловить БУДЬ-ЩО",
                    size=14, bold=True, fill=BG, stroke=INK))

    # вниз — у журнал, ВДОМА
    f.append(arrow(505, 274, 505, 332))
    f.append(fitbox(355, 334, 300, 70,
                    "журнал (вдома) — лог РАЗ:\nстек · SQL · виняток · reqId",
                    size=13, fill=NEUT, stroke=INK))

    # стіна редакції
    f.append(text(656, 62, "стіна редакції", size=12, color=MUTED))
    f.append(line(656, 72, 656, 398, color=MUTED, sw=1.6, dash="7 6"))
    f.append(arrow(612, 205, 742, 205))
    f.append(text(690, 192, "редаговано", size=11, color=MUTED))

    # назовні — лише непрозорий конверт
    f.append(fitbox(748, 150, 300, 132,
                    "клієнт бачить лише:\n500 · code: internal\ndetail: загальне\n"
                    "requestId: a1b2c3\n— і НУЛЬ нутрощів",
                    size=14, bold=True, fill=AMBER_T, stroke=AMBER))

    render(os.path.join(OUT, 'redaction-wall.svg'), W, H, *f,
           title="Стіна редакції: усе нутро — вдома, назовні — непрозорий 500")


def fig_error_shape_timeline():
    """Родовід форми помилки: індустрія мала дисципліну (FTP→HTTP→SOAP),
    викинула її в добу REST/JSON, і повільно вертала стандартом (gRPC, RFC 7807/9457)."""
    W, H = 1000, 792
    f = []

    ax = 250
    f.append(line(ax, 78, ax, 712, color="#c8ced6", sw=2))

    # (cy, рік+назва, суть, заливка, обвід)
    nodes = [
        (112, "1985 · FTP", "коди відповіді: перша цифра = КЛАС", GREEN_T, FIELD),
        (202, "1996 · HTTP/1.0", "4xx — твій бік · 5xx — наш бік", GREEN_T, FIELD),
        (292, "2000 · SOAP Fault", "faultcode (машина) + faultstring (людина)", GREEN_T, FIELD),
        (402, "≈2005–2015 · REST/JSON", "кожен свій: {error} · {message} · голий рядок", RED_T, POS),
        (512, "2015 · gRPC", "17 значень (0–16) — ЗАКРИТИЙ перелік", BLUE_T, NEG),
        (602, "2016 · RFC 7807", "конверт Problem Details: type·title·status·detail", BLUE_T, NEG),
        (692, "2023 · RFC 9457", "заміняє 7807 + реєстр типів помилок", BLUE_T, NEG),
    ]
    for cy, head, essence, tint, col in nodes:
        f.append(rect(306, cy - 31, 636, 62, fill=tint, stroke=col, sw=1.5))
        f.append(text(324, cy - 6, head, size=16, bold=True, anchor="start"))
        f.append(text(324, cy + 17, essence, size=13, color=MUTED, anchor="start"))
        f.append(circle(ax, cy, 8, fill=col, stroke=BG, sw=2))
        f.append(line(ax + 8, cy, 306, cy, color="#c8ced6", sw=1.4))

    # ери ліворуч від осі: смуга + короткий підпис
    eras = [
        (97, 323, FIELD, "мали\nвідповідь"),
        (371, 433, POS, "викинули"),
        (481, 723, NEG, "вертали\nстандартом"),
    ]
    for y1, y2, col, label in eras:
        f.append(rect(212, y1, 6, y2 - y1, fill=col, stroke=col, sw=1, rx=3))
        f.append(mtext(112, (y1 + y2) / 2 - 6, label, size=14, color=col, bold=True))

    render(os.path.join(OUT, 'error-shape-timeline.svg'), W, H, *f,
           title="Родовід форми помилки — мали, викинули, вертали")


def fig_machine_key_coverage():
    """Машинний ключ помилки має відповісти на ДВА питання (хто діє / що сталося);
    жоден із трьох механізмів не покриває обидва — тому їх складають у стос."""
    W, H = 1060, 470
    f = []

    # стовпці: (x, ширина, назва)
    cols = [(250, 250, "HTTP статус-клас"),
            (510, 250, "gRPC-коди"),
            (770, 260, "Problem Details type")]
    f.append(fitbox(30, 60, 210, 44, "питання ↓  /  механізм →", size=12,
                    fill=NEUT, stroke=INK, color=MUTED))
    for x, w, name in cols:
        f.append(fitbox(x, 60, w, 44, name, size=15, bold=True, fill=NEUT, stroke=INK))

    # рядки: (y, питання, [(мітка, колір, нотатка) × 3])
    rows = [
        (116, "ХТО діє?\n(чи повторювати)", [
            ("✓", FIELD, "4xx / 5xx / 429 —\nясно й грубо"),
            ("✓", FIELD, "UNAVAILABLE,\nPERMISSION_DENIED"),
            ("~", AMBER, "несе status,\nа суть — у type"),
        ]),
        (268, "ЩО саме сталося?\n(розгалузити код)", [
            ("✗", POS, "404 = і «нема»,\nі «не твій»"),
            ("~", AMBER, "17 кошиків,\nзакрито"),
            ("✓", FIELD, "type-URI / code —\nвідкрито"),
        ]),
    ]
    for ry, qlabel, cells in rows:
        f.append(fitbox(30, ry, 210, 132, qlabel, size=14, bold=True, fill=BG, stroke=INK))
        for (x, w, _), (mark, mcol, note) in zip(cols, cells):
            f.append(rect(x, ry, w, 132, fill=BG, stroke="#c8ced6", sw=1.4))
            f.append(text(x + w / 2, ry + 54, mark, size=34, bold=True, color=mcol))
            f.append(mtext(x + w / 2, ry + 86, note, size=13, color=MUTED))

    f.append(fitbox(30, 414, 1000, 44,
                    "жоден стовпчик не «✓✓»  →  реальний контракт СКЛАДАЄ їх:  "
                    "HTTP-клас (хто діє) + машинний code/type (що сталося) + detail (людині)",
                    size=14, bold=True, fill=AMBER_T, stroke=AMBER))

    render(os.path.join(OUT, 'machine-key-coverage.svg'), W, H, *f,
           title="Машинний ключ помилки: два питання, жоден механізм не покриває обидва")


if __name__ == '__main__':
    fig_last_translation()
    fig_two_readers()
    fig_who_acts()
    fig_one_table()
    fig_redaction_wall()
    fig_error_shape_timeline()
    fig_machine_key_coverage()
    print("figures written to", OUT)
