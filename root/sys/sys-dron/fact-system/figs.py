# -*- coding: utf-8 -*-
"""Фігури до теми «FactSystem: факт, метадані й зв'язок зі станом»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def box(cx, cy, s, **kw):
    """textbox + межі рамки (лівий/правий край) для приєднання стрілок."""
    body, w, h = textbox(cx, cy, s, **kw)
    return body, cx - w / 2.0, cx + w / 2.0, cy - h / 2.0, cy + h / 2.0


# ── 1. Три джерела → факт → екрани ─────────────────────────────────────────
def fig_sources():
    W, H = 1060, 470
    f = []

    src = [(150, 140, "Параметри автопілота\nPARAM_VALUE"),
           (150, 250, "Телеметрія\nполя повідомлень"),
           (150, 360, "Налаштування\nсховище застосунку")]
    src_right = []
    for cx, cy, s in src:
        b, x0, x1, y0, y1 = box(cx, cy, s, size=14)
        f.append(b)
        src_right.append((x1, cy))

    # центральна панель
    px, py, pw, ph = 380, 105, 300, 290
    f.append(rect(px, py, pw, ph, fill="#ffffff", stroke=INK, sw=2))
    f.append(text(px + pw / 2.0, py + 34, "Факт", size=17, bold=True))
    f.append(fitbox(px + 22, py + 52, pw - 44, 52, "ім'я + значення", size=14))
    f.append(fitbox(px + 22, py + 114, pw - 44, 52, "тип, номер компонента", size=14))
    f.append(fitbox(px + 22, py + 176, pw - 44, 52, "сигнали про зміну", size=14))
    f.append(fitbox(px + 22, py + 238, pw - 44, 34, "метадані", size=14, fill="#eaf3ea", stroke=FIELD))

    dst = [(890, 140, "Редактор параметрів"),
           (890, 250, "Прилади польоту"),
           (890, 360, "Сторінки налаштувань")]
    dst_left = []
    for cx, cy, s in dst:
        b, x0, x1, y0, y1 = box(cx, cy, s, size=14)
        f.append(b)
        dst_left.append((x0, cy))

    for x1, cy in src_right:
        f.append(arrow(x1 + 10, cy, px - 8, cy))
    for x0, cy in dst_left:
        f.append(arrow(px + pw + 8, cy, x0 - 10, cy))

    render(os.path.join(IMG, 'sources-to-screen.svg'), W, H, *f)


# ── 2. Сире ↔ показане ─────────────────────────────────────────────────────
def fig_raw_cooked():
    W, H = 980, 660
    f = []

    f.append(text(250, 52, "показ", size=16, bold=True))
    f.append(text(700, 52, "редагування", size=16, bold=True))

    down = [(110, "сире значення\n60.0 м"),
            (230, "rawTranslator\nметри → фути"),
            (350, "показане значення\n196.850…"),
            (470, "форматування\n1 знак, одиниці"),
            (585, "«196.9 ft» на екрані")]
    prev_bottom = None
    for cy, s in down:
        b, x0, x1, y0, y1 = box(250, cy, s, size=14)
        f.append(b)
        if prev_bottom is not None:
            f.append(arrow(250, prev_bottom + 6, 250, y0 - 8))
        prev_bottom = y1

    up = [(585, "людина вводить\n250 ft"),
          (470, "cookedTranslator\nфути → метри"),
          (350, "сире значення\n76.2 м"),
          (230, "перевірка меж\nз опису величини"),
          (110, "запис і PARAM_SET")]
    prev_top = None
    for cy, s in up:
        b, x0, x1, y0, y1 = box(700, cy, s, size=14)
        f.append(b)
        if prev_top is not None:
            f.append(arrow(700, prev_top - 6, 700, y1 + 8))
        prev_top = y0

    render(os.path.join(IMG, 'raw-cooked.svg'), W, H, *f)


# ── 3. Відкладені сповіщення ───────────────────────────────────────────────
def fig_deferred():
    W, H = 1020, 400
    f = []

    msg_x = [175, 208, 252, 290, 332, 376, 418, 470, 522, 566, 612, 662, 702, 752, 802, 848]
    f.append(text(120, 95, "повідомлення з каналу: setRawValue і rawValueChanged на кожне",
                  size=14, anchor="start"))
    f.append(arrow(120, 140, 940, 140))
    for x in msg_x:
        f.append(line(x, 140, x, 120, color=NEG, sw=2))

    tick_x = [250, 420, 590, 760]
    f.append(text(120, 232, "таймер групи: одне valueChanged для екрана на такт",
                  size=14, anchor="start"))
    f.append(arrow(120, 278, 940, 278))
    for x in tick_x:
        f.append(line(x, 278, x, 252, color=POS, sw=3))

    f.append(line(250, 292, 250, 322, color=MUTED, sw=1, dash="4 4"))
    f.append(line(420, 292, 420, 322, color=MUTED, sw=1, dash="4 4"))
    f.append(line(250, 322, 420, 322, color=MUTED, sw=1.5))
    f.append(text(335, 352, "період оновлення групи (для GPS — 1000 мс)",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'deferred-signals.svg'), W, H, *f)


# ── 4. Шви власної групи: що склеєно рядками (вставка proj) ────────────────
def fig_seams():
    W, H = 1180, 500
    f = []
    f.append(text(W / 2.0, 46, "Чим склеєні артефакти власної групи фактів",
                  size=17, bold=True))

    rows = [
        (140,
         "XML дилекту\nid=42001, name=FUELCELL_STATUS",
         "обробник групи\ncase MAVLINK_MSG_ID_FUELCELL_STATUS",
         "стала, яку згенерував тулчейн",
         "перевіряє компілятор", FIELD),
        (275,
         "клас групи\nFact _pressureFact(0, \"pressure\", …)",
         "FuelCellFact.json\n\"name\": \"pressure\"",
         "рядок «pressure», написаний двічі",
         "компілятор мовчить", POS),
        (410,
         "плагін прошивки\nfactGroups(): ключ \"fuelcell\"",
         "опис екрана\ngetFact(\"fuelcell.pressure\")",
         "ключ групи + крапка + ім'я факту",
         "компілятор мовчить", POS),
    ]

    for cy, left, right, glue, verdict, color in rows:
        bl, lx0, lx1, ly0, ly1 = box(250, cy, left, size=13)
        br, rx0, rx1, ry0, ry1 = box(900, cy, right, size=13)
        f.append(bl)
        f.append(br)
        mid = (lx1 + rx0) / 2.0
        f.append(arrow(lx1 + 12, cy, rx0 - 12, cy))
        f.append(text(mid, cy - 16, glue, size=13, color=MUTED))
        f.append(text(mid, cy + 34, verdict, size=13, color=color, bold=True))

    render(os.path.join(IMG, 'custom-factgroup-seams.svg'), W, H, *f)


# ── 5. Куди веде рядок одиниць (вставка proj) ──────────────────────────────
def fig_units():
    W, H = 1180, 600
    f = []
    f.append(text(W / 2.0, 44, "Що станція робить із рядком units з опису",
                  size=17, bold=True))

    b, x0, x1, y0, y1 = box(280, 100, "рядок units з файлу опису", size=14)
    f.append(b)
    prev_bottom = y1

    steps = [
        (200,
         "є enumStrings або bitmask?",
         "перетворення НЕМАЄ\nкод лишається кодом"),
        (330,
         "рядок є серед вбудованих?\nrad · centi-degrees · centi-celsius\nnorm · gimbal-degrees",
         "вбудований перетворювач\nвибір користувача НЕ діє"),
        (470,
         "рядок є серед налаштовних?\nm · vertical m · m/s · C · m^2 · g · cm/px",
         "перетворювач за вибором\nкористувача: ft, F, kn, lbs"),
    ]

    for cy, question, answer in steps:
        qb, qx0, qx1, qy0, qy1 = box(280, cy, question, size=13,
                                     fill="#ffffff", stroke=INK, sw=2)
        f.append(qb)
        f.append(arrow(280, prev_bottom + 6, 280, qy0 - 8))
        ab, ax0, ax1, ay0, ay1 = box(880, cy, answer, size=13)
        f.append(ab)
        f.append(arrow(qx1 + 12, cy, ax0 - 12, cy))
        f.append(text((qx1 + ax0) / 2.0, cy - 14, "так", size=13, color=MUTED))
        f.append(text(296, (qy1 + 30), "ні", size=13, color=MUTED, anchor="start"))
        prev_bottom = qy1

    lb, lx0, lx1, ly0, ly1 = box(280, 555, "перетворення немає\nпідпис — той самий рядок", size=13)
    f.append(lb)
    f.append(arrow(280, prev_bottom + 6, 280, ly0 - 8))

    render(os.path.join(IMG, 'units-routing.svg'), W, H, *f)


fig_sources()
fig_raw_cooked()
fig_deferred()
fig_seams()
fig_units()
print("ok")
