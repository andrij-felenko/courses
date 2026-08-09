# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL = "#fff6e5"
RED_FILL = "#fdecea"
GREY_FILL = "#eceff1"


# ── 1. Доки дістає кожен захист ─────────────────────────────────────────────
def fig_coverage():
    W, H = 1560, 860
    p = []

    p.append(text(70, 62, "шлях байта від застосунку до комірки — і скільки з нього накриває кожен захист",
                  size=16, bold=True, anchor="start"))

    hops = [("пам'ять\nзастосунку", GREY_FILL),
            ("кеш\nсторінок", GREY_FILL),
            ("блоковий\nшар", BLUE_FILL),
            ("драйвер\nі HBA", BLUE_FILL),
            ("шина\nдо носія", WARM_FILL),
            ("контролер\nносія", WARM_FILL),
            ("комірки\nносія", GREEN_FILL)]

    x0, bw, gap, y_hop, bh = 70, 190, 16, 110, 92
    centers, lefts, rights = [], [], []
    for i, (label, fill) in enumerate(hops):
        x = x0 + i * (bw + gap)
        p.append(fitbox(x, y_hop, bw, bh, label, size=14, pad=10, fill=fill))
        lefts.append(x)
        rights.append(x + bw)
        centers.append(x + bw / 2)
        if i:
            p.append(line(x - gap, y_hop + bh / 2, x, y_hop + bh / 2, color=MUTED, sw=1.4))

    bars = [("власний код виправлення помилок носія", 6, 6, GREEN_FILL, FIELD),
            ("T10 DIF — тег живе на шині й у форматі сектора", 3, 6, WARM_FILL, POS),
            ("DIX + DIF, теги генерує блоковий шар — типовий випадок", 2, 6, BLUE_FILL, NEG),
            ("DIX + DIF, теги приносить сам застосунок", 0, 6, BLUE_FILL, NEG)]

    y = 268
    for label, a, b, fill, stroke in bars:
        p.append(text(70, y, label, size=14, anchor="start", color=INK))
        bx, bxe = lefts[a], rights[b]
        p.append(rect(bx, y + 18, bxe - bx, 44, fill=fill, stroke=stroke, sw=2, rx=8))
        y += 116

    p.append(line(70, 700, W - 70, 700, color=MUTED, sw=1.2, dash="6 5"))

    n, _, _ = textbox(W / 2, 780,
                      ["Кожна ланка має власну перевірку свого відтинка, але вони не складаються в одну:",
                       "спотворення всередині ланки входить у наступний відтинок як законні дані",
                       "й дістає законну нову контрольну суму."],
                      size=14, pad=16, fill=GREY_FILL, stroke=MUTED, sw=1.5)
    p.append(n)

    render(os.path.join(IMG, 'coverage.svg'), W, H, *p,
           title="Доки дістає кожен рівень захисту даних на шляху до носія")


# ── 2. Вісім байтів: у пам'яті окремо, на шині впереміш ─────────────────────
def fig_tuple_and_layout():
    W, H = 1520, 980
    p = []

    p.append(text(70, 62, "вісім байтів захисної інформації на кожен інтервал даних",
                  size=16, bold=True, anchor="start"))

    cells = [("Guard — 2 Б\nCRC-16 від байтів даних", 400, WARM_FILL),
             ("Application — 2 Б\nвільні для власника вище", 400, GREY_FILL),
             ("Reference — 4 Б\nмолодші 32 біти адреси блока", 460, BLUE_FILL)]
    x = 70
    for label, cw, fill in cells:
        p.append(fitbox(x, 96, cw, 96, label, size=14, pad=12, fill=fill))
        x += cw + 14

    p.append(text(70, 268, "у пам'яті хоста (DIX): дані й теги — два окремі буфери",
                  size=15, bold=True, anchor="start"))

    dbw, dgap, dx0, y_data = 220, 20, 70, 300
    dcent = []
    for i in range(4):
        x = dx0 + i * (dbw + dgap)
        p.append(fitbox(x, y_data, dbw, 84, "дані блока %d" % (i + 1),
                        size=14, pad=10, fill=GREEN_FILL))
        dcent.append(x + dbw / 2)

    y_tag = 448
    for i, cx in enumerate(dcent):
        p.append(fitbox(cx - 40, y_tag, 80, 62, "тег %d" % (i + 1), size=13, pad=6, fill=BLUE_FILL))
        p.append(line(cx, y_data + 84, cx, y_tag, color=MUTED, sw=1.3, dash="5 5"))

    side, _, _ = textbox(1230, y_data + 110,
                         ["окремий список розсіювання;",
                          "у ядрі це bio_integrity_payload,",
                          "причеплений до bio збоку"],
                         size=13, pad=14, fill=GREY_FILL, stroke=MUTED, sw=1.4)
    p.append(side)

    p.append(text(70, 596, "на шині до носія (DIF): HBA вплітає теги між даними",
                  size=15, bold=True, anchor="start"))

    p.append(arrow(400, 620, 400, 668, color=NEG, sw=2))
    p.append(text(424, 652, "перемежування робить HBA, не ядро", size=13,
                  color=NEG, anchor="start"))

    y_wire, x = 700, 70
    for i in range(4):
        p.append(fitbox(x, y_wire, 220, 84, "512 Б даних", size=14, pad=10, fill=GREEN_FILL))
        x += 224
        p.append(fitbox(x, y_wire, 76, 84, "8 Б", size=13, pad=6, fill=BLUE_FILL))
        x += 84

    p.append(text(70, 848, "носій відформатований на 520 байтів на сектор — інакше тегам просто немає де лежати",
                  size=14, color=POS, anchor="start"))

    n, _, _ = textbox(W / 2, 918,
                      ["Тримати 520-байтові сектори просто в пам'яті не можна:",
                       "сторінка на 4096 байтів не ділиться на 520, і вся геометрія блокового шару розсипається."],
                      size=14, pad=15, fill=GREY_FILL, stroke=MUTED, sw=1.5)
    p.append(n)

    render(os.path.join(IMG, 'tuple-and-layout.svg'), W, H, *p,
           title="Склад восьми байтів і дві розкладки: окремо в пам'яті, впереміш на шині")


# ── 3. Запис не за тією адресою ─────────────────────────────────────────────
def fig_misdirected():
    W, H = 1500, 760
    p = []

    p.append(text(70, 62, "запис пішов не за тією адресою — що бачить носій",
                  size=16, bold=True, anchor="start"))

    p.append(fitbox(70, 110, 480, 88, "дані, призначені для блока 100", size=15, pad=12,
                    fill=GREEN_FILL, stroke=FIELD, sw=2))
    p.append(fitbox(70, 220, 230, 76, "guard\n= CRC(дані)", size=13, pad=10, fill=WARM_FILL))
    p.append(fitbox(320, 220, 230, 76, "reference\n= 100", size=13, pad=10, fill=BLUE_FILL))

    p.append(arrow(580, 200, 780, 200, color=POS, sw=2.2))
    p.append(text(580, 160, "прошивка помилилася в арифметиці адреси", size=14,
                  color=POS, anchor="start"))

    p.append(fitbox(820, 110, 610, 76, "сектор ліг на блок 200", size=15, pad=12,
                    fill=RED_FILL, stroke=POS, sw=2))

    p.append(fitbox(820, 220, 610, 76,
                    "CRC від даних збігається з guard — дані цілі", size=14, pad=12,
                    fill=GREEN_FILL, stroke=FIELD, sw=2))
    p.append(fitbox(820, 320, 610, 76,
                    "у тезі 100, а адреса 200 — не збігається", size=14, pad=12,
                    fill=RED_FILL, stroke=POS, sw=2))
    p.append(fitbox(820, 420, 610, 76,
                    "команду відхилено: 10h/03h", size=14, pad=12,
                    fill=WARM_FILL, stroke=POS, sw=2))

    n, _, _ = textbox(W / 2, 620,
                      ["Сама лише контрольна сума тут безсила: дані бездоганні, просто лежать не там.",
                       "Ловить адресу тільки тег, у який цю адресу вписали заздалегідь,",
                       "і звіряє його той, хто адресу приймає — контролер носія."],
                      size=14, pad=16, fill=GREY_FILL, stroke=MUTED, sw=1.5)
    p.append(n)

    render(os.path.join(IMG, 'misdirected-write.svg'), W, H, *p,
           title="Запис не за тією адресою і роль тега з адресою блока")


if __name__ == '__main__':
    fig_coverage()
    fig_tuple_and_layout()
    fig_misdirected()
    print("ok")
