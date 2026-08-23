# -*- coding: utf-8 -*-
"""Фігури до кроку «Рев'ю-воркшоп DH» (dh-review-workshop).
Дві фігури: (1) стіл рев'ю — кожен стейкхолдер бачить одну грань DH;
(2) воркшоп як перетворювач: входи → сесія → три артефакти (не вирок)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#e8f6ee"
CTR_FILL = "#eef2f7"


def seat(x, y, w, h, role, concern, accent=None):
    """Місце за столом: рамка + роль (жирна) + турбота (сіра, один рядок)."""
    col = accent or LINE
    frags = [rect(x, y, w, h, fill=FILL, stroke=col, sw=1.6)]
    frags.append(text(x + w / 2, y + 30, role, size=13, color=INK, bold=True))
    frags.append(text(x + w / 2, y + 54, concern, size=12, color=MUTED))
    return frags


# ── Фігура 1: стіл рев'ю — кожен бачить одну грань DH ────────────────────────
def fig_table():
    W, H = 960, 580
    frags = []

    # центр — DH v2 на столі
    cx0, cy0, cw, ch = 380, 250, 200, 92
    ccx, ccy = cx0 + cw / 2, cy0 + ch / 2
    # шість променів до центру (малюємо ПЕРШИМИ, щоб рамки лягли зверху)
    left_mid = [(310, 116), (310, 296), (310, 476)]
    left_to = [(cx0, cy0 + 15), (cx0, ccy), (cx0, cy0 + ch - 15)]
    right_mid = [(650, 116), (650, 296), (650, 476)]
    right_to = [(cx0 + cw, cy0 + 15), (cx0 + cw, ccy), (cx0 + cw, cy0 + ch - 15)]
    for a, b in zip(left_mid, left_to):
        frags.append(line(a[0], a[1], b[0], b[1], color=MUTED, sw=1.2))
    for a, b in zip(right_mid, right_to):
        frags.append(line(a[0], a[1], b[0], b[1], color=MUTED, sw=1.2))

    frags.append(rect(cx0, cy0, cw, ch, fill=CTR_FILL, stroke=INK, sw=2))
    frags.append(mtext(ccx, ccy - 6, ["Digital Homes v2", "усі в'ю — на столі"],
                       size=14, bold=True))

    lx, lw = 30, 280
    rx, rw = 650, 280
    h = 76
    lys = [78, 258, 438]
    left = [
        ("Безпека", "витік твіна: видно, коли нікого вдома", POS),
        ("Експлуатація", "падає о 3-й ночі — як відновити", None),
        ("Супровід", "новий тип пристрою без переписування", None),
    ]
    right = [
        ("Мобільний розробник", "шляхи апки: хмара vs прямо в хаб", None),
        ("Хмара / бекенд", "твін і MQTT: доставка, стан дому", None),
        ("Голос мешканця (продакт)", "дім живий? приватність? ціна брокера", None),
    ]
    for (role, concern, acc), y in zip(left, lys):
        frags += seat(lx, y, lw, h, role, concern, acc)
    for (role, concern, acc), y in zip(right, lys):
        frags += seat(rx, y, rw, h, role, concern, acc)

    render(os.path.join(IMG, 'review-table.svg'), W, H, *frags,
           title="Стіл рев'ю: кожен бачить одну грань DH")


# ── Фігура 2: воркшоп як перетворювач (входи → сесія → три артефакти) ─────────
def fig_transform():
    W, H = 980, 430
    frags = []

    ix, iw = 40, 250
    mx, mw = 390, 250
    ox, ow = 700, 250
    bh = 74
    iys = [70, 178, 286]
    oys = [70, 178, 286]

    inputs = ["в'ю DH v2 (C4)", "сценарії з дерева корисності", "ризик-реєстр (з модуля 2)"]
    outputs = [("ранжовані рядки ризиків", None),
               ("ADR — рішення зафіксовано", None),
               ("фітнес-функції — вартові", FIELD)]

    # стрілки входи → сесія (малюємо першими)
    my, mh = 140, 150
    m_left = [(mx, my + 30), (mx, my + mh / 2), (mx, my + mh - 30)]
    for (iy, ml) in zip(iys, m_left):
        frags.append(arrow(ix + iw, iy + bh / 2, mx - 2, ml[1], color=LINE, sw=1.7))
    # стрілки сесія → виходи
    m_right = [(mx + mw, my + 30), (mx + mw, my + mh / 2), (mx + mw, my + mh - 30)]
    for (oy, mr) in zip(oys, m_right):
        frags.append(arrow(mx + mw, mr[1], ox - 2, oy + bh / 2, color=LINE, sw=1.7))

    for cap, y in zip(inputs, iys):
        frags.append(fitbox(ix, y, iw, bh, cap, size=13))
    for (cap, acc), y in zip(outputs, oys):
        st = acc or LINE
        fl = GREEN_FILL if acc else FILL
        frags.append(fitbox(ox, y, ow, bh, cap, size=13, fill=fl, stroke=st,
                            bold=bool(acc)))

    # сесія — центр
    frags.append(rect(mx, my, mw, mh, fill=CTR_FILL, stroke=INK, sw=2))
    frags.append(text(mx + mw / 2, my + 42, "Сесія", size=15, color=INK, bold=True))
    frags.append(mtext(mx + mw / 2, my + 78,
                       ["признач сценарій власнику", "стверджуй — або познач ризик"],
                       size=12, color=MUTED))

    render(os.path.join(IMG, 'review-transform.svg'), W, H, *frags,
           title="Воркшоп — це перетворювач, не вирок")


# ── Фігура 3: «рівно один раз» — дубль команди дає одне відчинення ────────────
def fig_exactly_once():
    W, H = 920, 560
    frags = []
    APP, CLOUD, HUB, LOCK = 120, 360, 610, 780
    top, bot = 88, 452
    for x in (APP, CLOUD, HUB, LOCK):
        frags.append(line(x, top, x, bot, color=MUTED, sw=1.2))
    for name, x in (("апка", APP), ("хмара", CLOUD), ("хаб", HUB), ("замок", LOCK)):
        frags.append(fitbox(x - 65, 44, 130, 40, name, size=13, bold=True,
                            fill=CTR_FILL, stroke=INK, sw=1.6))

    # 1 апка → хмара
    frags.append(arrow(APP, 135, CLOUD, 135, sw=1.7))
    frags.append(text((APP + CLOUD) / 2, 126, "«відчинити» · id=c-42", size=12))
    # 2 хмара → хаб (MQTT)
    frags.append(arrow(CLOUD, 185, HUB, 185, sw=1.7))
    frags.append(text((CLOUD + HUB) / 2, 176, "cmd c-42 (MQTT)", size=12))
    # 3 хаб → замок: перша й ЄДИНА актуація
    frags.append(arrow(HUB, 235, LOCK, 235, sw=1.7))
    frags.append(text((HUB + LOCK) / 2, 226, "актуювати", size=12))
    frags.append(circle(LOCK, 235, 6, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(text(LOCK + 12, 239, "① відчинено", size=11, color=FIELD,
                      anchor="start", bold=True))
    # 4 ack губиться (хаб → хмара, пунктир, обривається)
    frags.append(line(HUB, 295, 470, 295, color=MUTED, sw=1.5, dash="5 4"))
    frags.append(text((HUB + 470) / 2, 286, "ack губиться", size=12, color=MUTED))
    # 5 хмара повторює по таймауту
    frags.append(arrow(CLOUD, 355, HUB, 355, sw=1.7, color=POS))
    frags.append(text((CLOUD + HUB) / 2, 346, "повтор c-42 (таймаут ack)", size=12, color=POS))
    # 6 хаб упізнає дубль — без актуації
    frags.append(text((HUB + LOCK) / 2, 392, "бачив c-42 → дубль", size=12, bold=True))
    frags.append(line(HUB, 425, 705, 425, color=MUTED, sw=1.5, dash="5 4"))
    frags.append(text(675, 444, "актуації нема ②", size=11, color=MUTED))
    # підсумок
    frags.append(fitbox(180, 462, 560, 40,
                        "Замок відчинено РІВНО РАЗ, хоч команда прийшла двічі.",
                        size=13, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.6))
    render(os.path.join(IMG, 'exactly-once.svg'), W, H, *frags,
           title="«Рівно один раз»: дубль команди — одне відчинення")


# ── Фігура 4: разовий тест vs вартовий у CI ──────────────────────────────────
def fig_sentinel_gate():
    W, H = 940, 430
    frags = []
    bw, bh = 150, 60
    xs = [110, 300, 490, 680]
    cx_title = 470

    # Рядок A — разовий аудит
    ay = 100
    frags.append(text(cx_title, 78, "Разовий аудит (v0): ловить ваду один раз",
                      size=14, bold=True))
    a_boxes = [("знахідка сесії", FILL, LINE, INK),
               ("написав асерт", FILL, LINE, INK),
               ("прогнав раз\n..FF", FILL, LINE, INK),
               ("у шухляду", "#eceff1", MUTED, MUTED)]
    for (lbl, fl, st, col), x in zip(a_boxes, xs):
        frags.append(fitbox(x, ay, bw, bh, lbl, size=13, fill=fl, stroke=st, color=col))
    for x in xs[:-1]:
        frags.append(arrow(x + bw, ay + bh / 2, x + 190 - 2, ay + bh / 2, sw=1.7))
    frags.append(text(xs[-1] + bw / 2, ay + bh + 22, "ніхто не запустить завтра",
                      size=11, color=MUTED))

    # Рядок B — вартовий у CI
    by = 268
    frags.append(text(cx_title, 246, "Вартовий у CI (v2): ловить на кожному релізі",
                      size=14, bold=True))
    b_boxes = [("знахідка сесії", FILL, LINE, INK, False),
               ("фітнес-функція", FILL, LINE, INK, False),
               ("висить у CI", GREEN_FILL, FIELD, INK, True),
               ("червоний блокує\nмердж", "#fdecea", POS, POS, True)]
    for (lbl, fl, st, col, bd), x in zip(b_boxes, xs):
        frags.append(fitbox(x, by, bw, bh, lbl, size=13, fill=fl, stroke=st, color=col, bold=bd))
    for x in xs[:-1]:
        frags.append(arrow(x + bw, by + bh / 2, x + 190 - 2, by + bh / 2, sw=1.7))
    # петля «на кожен PR»
    loop_y = by + bh + 34
    frags.append(arrow(xs[-1] + bw, loop_y, xs[0], loop_y, color=POS, sw=1.7))
    frags.append(text(cx_title, loop_y + 20, "на кожному PR — знову з нуля",
                      size=11, color=POS))
    render(os.path.join(IMG, 'sentinel-gate.svg'), W, H, *frags,
           title="Разовий тест vs вартовий у CI")


if __name__ == "__main__":
    fig_table()
    fig_transform()
    fig_exactly_once()
    fig_sentinel_gate()
    print("ok:", os.listdir(IMG))
