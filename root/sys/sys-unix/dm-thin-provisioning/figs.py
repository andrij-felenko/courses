# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GRAY_FILL = "#eef1f4"
WARM = "#b8860b"


# ── 1. Три долі одного запису ──────────────────────────────────────────────
def fig_write_cases():
    W, H = 1360, 800
    p = []

    p.append(text(60, 52, "Пул дивиться на адресу запису й бачить один із трьох станів — "
                          "від нього залежить уся вартість операції",
                  size=16, anchor="start", bold=True))

    cols = [
        (60, "адреси немає у відображенні", NEG, BLUE_FILL,
         ["взяти вільний блок пулу",
          "занулити ту частину блока,\nяку запит не накриває",
          "покласти дані",
          "додати листок у дерево\nвідображень"],
         "дорого: виділення, занулення\nі зміна метаданих"),
        (520, "адреса відображена, блок наш", FIELD, GREEN_FILL,
         ["знайти блок у дереві",
          "покласти дані просто в нього",
          "—",
          "метадані не змінюються"],
         "дешево: звичайний запис\nплюс один пошук у дереві"),
        (980, "адреса відображена, блок спільний", POS, RED_FILL,
         ["взяти вільний блок пулу",
          "скопіювати ВЕСЬ старий блок\nу новий",
          "покласти поверх нові дані",
          "переставити листок нашого\nдерева на новий блок"],
         "найдорожче: 4 КіБ запису тягнуть\nкопіювання цілого блока пулу"),
    ]

    for x0, title, col, fil, steps, tail in cols:
        p.append(fitbox(x0, 84, 320, 58, title, size=14, bold=True,
                        fill=fil, stroke=col, sw=1.8))
        for i, s in enumerate(steps):
            p.append(fitbox(x0, 168 + i * 104, 320, 84, s, size=13,
                            fill=BG, stroke=col if s != "—" else MUTED, sw=1.4))
        p.append(fitbox(x0, 600, 320, 84, tail, size=13,
                        fill=fil, stroke=col, sw=1.6))

    p.append(fitbox(60, 716, 1240, 60,
                    "Спільний блок упізнають не за лічильником посилань, а за міткою часу в самому "
                    "відображенні: якщо його зробили пізніше за останній знімок тому — він точно нічий, крім нашого",
                    size=14, fill=GRAY_FILL, stroke=MUTED, sw=1.6))

    render(os.path.join(IMG, "write-cases.svg"), W, H, *p)


# ── 2. Анатомія пулу: два пристрої, два рівні дерева ───────────────────────
def fig_pool_anatomy():
    W, H = 1400, 880
    p = []

    p.append(text(60, 52, "Пул — це пара пристроїв: маленький із відображеннями і великий із даними",
                  size=16, anchor="start", bold=True))

    # ── ліва панель: метадані ───────────────────────────────────────────
    p.append(rect(60, 84, 700, 640, fill=BG, stroke=NEG, sw=2, rx=10))
    p.append(text(80, 118, "пристрій метаданих — типово одиниці ГіБ, стеля 16 ГіБ",
                  size=14, anchor="start", bold=True, color=NEG))

    p.append(fitbox(90, 140, 300, 52, "суперблок", size=14, bold=True,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(text(410, 172, "єдине місце, яке пишуть на місці", size=13,
                  anchor="start", color=MUTED))

    p.append(arrow(240, 192, 240, 236, color=NEG, sw=1.8))

    p.append(fitbox(90, 236, 620, 56, "верхнє дерево:  номер тому  →  корінь його дерева відображень",
                    size=14, fill=GRAY_FILL, stroke=INK, sw=1.6))

    p.append(arrow(240, 292, 200, 336, color=NEG, sw=1.6))
    p.append(arrow(560, 292, 600, 336, color=FIELD, sw=1.6))

    p.append(fitbox(90, 336, 260, 78, "дерево тому app\nлогічний блок → запис",
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.6))
    p.append(fitbox(450, 336, 260, 78, "дерево знімка app-1\nлогічний блок → запис",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.6))

    p.append(arrow(220, 414, 300, 466, color=NEG, sw=1.6))
    p.append(arrow(580, 414, 500, 466, color=FIELD, sw=1.6))

    p.append(fitbox(90, 466, 620, 90,
                    "листок — 64 біти на одне відображення\n"
                    "40 бітів: номер блока даних        24 біти: час, коли відображення зробили",
                    size=14, fill=WARM_FILL, stroke=WARM, sw=1.8))

    p.append(fitbox(90, 586, 620, 118,
                    "карта простору: скільки дерев посилається на кожен блок даних\n"
                    "0 — вільний, 1 — чийсь власний, 2 і більше — спільний зі знімками\n"
                    "лежить тут-таки й міняється в тій самій транзакції, що й дерева",
                    size=14, fill=GRAY_FILL, stroke=MUTED, sw=1.6))

    # ── права панель: дані ──────────────────────────────────────────────
    p.append(rect(800, 84, 540, 640, fill=BG, stroke=FIELD, sw=2, rx=10))
    p.append(text(820, 118, "пристрій даних — власне місце", size=14,
                  anchor="start", bold=True, color=FIELD))
    p.append(text(820, 146, "порізаний на блоки однакового розміру:", size=13,
                  anchor="start", color=MUTED))
    p.append(text(820, 170, "від 64 КіБ до 1 ГіБ, кратно 64 КіБ, назавжди", size=13,
                  anchor="start", color=MUTED))

    cells = [
        ("блок 0", "посилань 2", BLUE_FILL, NEG),
        ("блок 1", "посилань 1", GREEN_FILL, FIELD),
        ("блок 2", "вільний", BG, MUTED),
        ("блок 3", "посилань 2", BLUE_FILL, NEG),
        ("блок 4", "вільний", BG, MUTED),
        ("блок 5", "посилань 1", GREEN_FILL, FIELD),
        ("блок 6", "вільний", BG, MUTED),
        ("блок 7", "вільний", BG, MUTED),
    ]
    for i, (name, st, fil, col) in enumerate(cells):
        cx = 830 + (i % 2) * 260
        cy = 210 + (i // 2) * 118
        p.append(fitbox(cx, cy, 230, 90, name + "\n" + st, size=13,
                        fill=fil, stroke=col, sw=1.6))

    p.append(fitbox(60, 752, 1280, 100,
                    "Скільки треба метаданих: приблизно 48 байтів на кожен блок даних.\n"
                    "Пул на 4 ТіБ із блоком 64 КіБ — це 67 108 864 блоків і близько 3 ГіБ метаданих;\n"
                    "той самий пул із блоком 512 КіБ — 8 388 608 блоків і близько 384 МіБ",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, "pool-anatomy.svg"), W, H, *p)


# ── 3. Ланцюг повернення місця ─────────────────────────────────────────────
def fig_reclaim_chain():
    W, H = 1320, 940
    p = []

    p.append(text(60, 52, "Місце виділяється саме, а повертається лише ланцюгом: "
                          "розірваний на будь-якій ланці — не повертається зовсім",
                  size=16, anchor="start", bold=True))

    steps = [
        ("файл видалено", "у карті вільного місця файлової системи змінилися біти — і більше ніде нічого",
         GRAY_FILL, MUTED, None),
        ("fstrim або монтування з discard", "хтось мусить обійти карту й вимовити «ці діапазони вільні» вголос",
         BLUE_FILL, NEG, "нема ні того, ні того — пул не дізнається нічого й далі росте"),
        ("запит накриває цілий блок пулу", "звільнити півблока не можна: решта половина комусь потрібна",
         BLUE_FILL, NEG, "дрібні розкидані діри при блоці 512 КіБ не звільняють нічого"),
        ("лічильник посилань упав до нуля", "поки на блок дивиться бодай один знімок, він лишається зайнятим",
         WARM_FILL, WARM, "забутий знімок мовчки тримає все, що том колись записав"),
        ("блок повернувся у вільні пулу", "тепер його видадуть під наступний перший запис будь-якого тому",
         GREEN_FILL, FIELD, None),
        ("discard_passdown до носія", "пул переказує звільнення вниз, і аж тепер про це дізнається SSD",
         GREEN_FILL, FIELD, "вимкнено — місце вільне в пулі, але зайняте всередині носія"),
    ]

    y = 96
    for i, (name, why, fil, col, fail) in enumerate(steps):
        p.append(fitbox(60, y, 400, 74, name, size=15, bold=True,
                        fill=fil, stroke=col, sw=1.8))
        p.append(fitbox(490, y, 500, 74, why, size=13,
                        fill=BG, stroke=MUTED, sw=1.2))
        if fail:
            p.append(fitbox(1020, y, 240, 74, fail, size=12,
                            fill=RED_FILL, stroke=POS, sw=1.4))
        if i < len(steps) - 1:
            p.append(arrow(260, y + 74, 260, y + 128, color=col, sw=2))
        y += 128

    p.append(fitbox(60, 862, 1200, 60,
                    "Ті самі ланки повторюються на кожному поверсі стека: гість, образ, хазяїн, пул, носій — "
                    "і кожен поверх треба вмикати окремо",
                    size=14, fill=GRAY_FILL, stroke=MUTED, sw=1.6))

    render(os.path.join(IMG, "reclaim-chain.svg"), W, H, *p)


# ── 4. Лічильник used data вздовж досліду (вставка proj-thin-by-hand) ───────
def fig_used_staircase():
    W, H = 1520, 720
    p = []

    p.append(text(60, 46, "Лічильник «used data» на семи кроках ручного досліду — "
                          "у блоках пулу по 512 КіБ, усього їх 1024",
                  size=16, anchor="start", bold=True))

    base, top, vmax = 470, 130, 20.0
    k = (base - top) / vmax

    def py(v):
        return base - v * k

    steps = [
        (0,  "новий тонкий том:\nнічого не записано", "", MUTED, GRAY_FILL),
        (16, "dd 8 МіБ\nу сирий том", "+16", NEG, BLUE_FILL),
        (16, "create_snap:\nзнімок цього тому", "+0", FIELD, GREEN_FILL),
        (17, "4 КіБ у знімок\nповерх спільного блока", "+1", POS, RED_FILL),
        (17, "blkdiscard 64 КіБ\nусередині блока", "+0", WARM, WARM_FILL),
        (17, "blkdiscard 512 КіБ\nрівно блок, знімок живий", "+0", WARM, WARM_FILL),
        (15, "знімок видалено\nз метаданих пулу", "−2", FIELD, GREEN_FILL),
    ]

    p.append(line(112, base, 1460, base, color=INK, sw=2))
    for v in (5, 10, 15, 20):
        p.append(line(112, py(v), 1460, py(v), color="#dfe3e8", sw=1, dash="4,5"))
    for v in (0, 5, 10, 15, 20):
        p.append(text(98, py(v) + 5, str(v), size=12, color=MUTED, anchor="end"))

    bw, x0, gap = 140, 140, 50
    for i, (v, name, delta, col, fil) in enumerate(steps):
        x = x0 + i * (bw + gap)
        if v:
            p.append(rect(x, py(v), bw, base - py(v), fill=fil, stroke=col, sw=2, rx=4))
        else:
            p.append(line(x, base, x + bw, base, color=col, sw=3))
        p.append(text(x + bw / 2, py(v) - 16, str(v), size=18, color=col, bold=True))
        p.append(fitbox(x - 12, base + 26, bw + 24, 78, name, size=12,
                        fill=BG, stroke=MUTED, sw=1.2))
        if delta:
            p.append(text(x - gap / 2, base + 144, delta, size=16, color=col, bold=True))

    p.append(fitbox(60, base + 176, 1400, 62,
                    "Лічильник рухають лише дві події: перший запис у ще не відображену адресу "
                    "й розрив спільності зі знімком. Звільнення подією не є — його треба попросити вголос, "
                    "воно мусить накрити цілий блок, і спрацює лише тоді, коли на блок більше ніхто не дивиться",
                    size=14, fill=GRAY_FILL, stroke=MUTED, sw=1.6))

    render(os.path.join(IMG, "used-staircase.svg"), W, H, *p)


fig_write_cases()
fig_pool_anatomy()
fig_reclaim_chain()
fig_used_staircase()
print("ok")
