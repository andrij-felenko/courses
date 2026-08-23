# -*- coding: utf-8 -*-
"""Фігури до кроку «Компакт-вибір: де живе сесія»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER = "#e08a00"


def fig_who_holds_truth():
    """Три панелі: де лежить правда про сесію — стор / токен / гібрид."""
    W, H = 1000, 430
    frags = []

    # вертикальні розділювачі між панелями
    for sx in (333, 667):
        frags.append(line(sx, 44, sx, 400, color=MUTED, sw=1, dash="4,5"))

    # ── Панель А: server-side store (правда на сервері) ──
    cx = 167
    frags.append(text(cx, 56, "А · server-side store", size=14, bold=True))
    b, _, _ = textbox(cx, 112, "кукі: sid\n(непрозорий)", size=13)
    frags.append(b)
    frags.append(arrow(cx, 140, cx, 250, color=POS, sw=2.2))
    frags += mtext(cx + 34, 184, ["звірка на", "кожен запит"], size=11,
                   color=POS, anchor="start")
    b, _, _ = textbox(cx, 278, "спільний стор\n(Redis-клас)", size=13, fill="#eef2f6")
    frags.append(b)
    frags.append(text(cx, 348, "правда на сервері", size=12, color=MUTED))

    # ── Панель Б: stateless JWT (правда в токені) ──
    cx = 500
    frags.append(text(cx, 56, "Б · stateless JWT", size=14, bold=True))
    b, _, _ = textbox(cx, 112, "токен: дані\n+ підпис", size=13)
    frags.append(b)
    frags.append(arrow(cx, 140, cx, 250, color=FIELD, sw=2.2))
    frags += mtext(cx + 34, 184, ["перевірка", "локально"], size=11,
                   color=FIELD, anchor="start")
    b, _, _ = textbox(cx, 278, "(стору нема)", size=13, fill=BG, stroke=MUTED)
    frags.append(b)
    frags.append(text(cx, 348, "правда в токені", size=12, color=MUTED))

    # ── Панель В: гібрид (гарячий шлях локальний, відкликання на сервері) ──
    cx = 833
    frags.append(text(cx, 56, "В · гібрид access+refresh", size=13, bold=True))
    b, _, _ = textbox(cx, 104, "access · хвилини", size=12)
    frags.append(b)
    frags.append(arrow(cx, 126, cx, 170, color=FIELD, sw=2.0))
    frags.append(text(cx + 30, 152, "локально", size=10, color=FIELD, anchor="start"))
    b, _, _ = textbox(cx, 198, "refresh · під наглядом", size=12)
    frags.append(b)
    frags.append(arrow(cx, 222, cx, 268, color=POS, sw=2.0))
    frags.append(text(cx + 30, 248, "раз на хв", size=10, color=POS, anchor="start"))
    b, _, _ = textbox(cx, 296, "стор:\nвідкликання", size=12, fill="#eef2f6")
    frags.append(b)
    frags += mtext(cx, 360, ["гарячий шлях локальний,", "відкликання на сервері"],
                   size=11, color=MUTED)

    render(os.path.join(IMG, "who-holds-truth.svg"), W, H, *frags,
           title="Де лежить правда про сесію")


def fig_revocation_window():
    """Скільки сесія живе ПІСЛЯ команди відкликати — три смуги."""
    W, H = 940, 360
    t0 = 250                       # x стовпа «команда відкликати»
    frags = []

    # вертикаль t=0
    frags.append(line(t0, 84, t0, 292, color=MUTED, sw=1.5, dash="4,4"))
    frags += mtext(t0, 62, ["команда: відкликати", "(украли телефон)"], size=12,
                   color=INK)

    rows = [
        (120, "А · server-side"),
        (190, "Б · stateless JWT"),
        (260, "В · гібрид"),
    ]
    for y, label in rows:
        frags.append(text(t0 - 18, y + 5, label, size=13, anchor="end"))

    # А — мертво миттєво (крихітна зелена смуга)
    frags.append(rect(t0, 108, 9, 26, fill=FIELD, stroke=FIELD, rx=3))
    frags.append(text(t0 + 22, 125, "мертво миттєво", size=12, color=FIELD, anchor="start"))

    # Б — довга червона смуга до кінця терміну (вікно вламу)
    frags.append(rect(t0, 178, 560, 26, fill="#f7d9d5", stroke=POS, rx=3))
    frags.append(text(t0 + 280, 195, "сесія лишається живою", size=12,
                      color=POS, anchor="middle"))
    frags.append(line(t0 + 560, 172, t0 + 560, 210, color=POS, sw=1.3, dash="3,3"))
    frags.append(text(t0 + 560, 226, "токен протух (напр., 24 год)", size=11,
                      color=POS, anchor="middle"))

    # В — коротка бурштинова смуга до терміну access
    frags.append(rect(t0, 248, 96, 26, fill="#fdeccb", stroke=AMBER, rx=3))
    frags.append(text(t0 + 108, 265, "мертво за термін access (хвилини)", size=12,
                      color=AMBER, anchor="start"))

    # вісь часу
    frags.append(arrow(t0, 308, 880, 308, color=MUTED, sw=1.4))
    frags.append(text(560, 328, "час після команди відкликати  →", size=12, color=MUTED))
    frags.append(text(470, 350,
                      "Для дверей довжина смуги — це час, поки чужий іще всередині.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "revocation-window.svg"), W, H, *frags,
           title="Вікно відкликання")


def fig_one_seam():
    """Один шов authenticate() — і три взаємозамінні начинки за ним."""
    W, H = 1040, 440
    frags = []

    # ── ліворуч: викликачі (бізнес-код) ──
    frags.append(text(150, 74, "викликачі (бізнес-код)", size=13, bold=True))
    for cy, name in zip((120, 176, 232),
                        ("GET /home", "POST /device/:id/unlock", "GET /telemetry")):
        b, _, _ = textbox(150, cy, name, size=13)
        frags.append(b)
    frags.append(text(150, 285, "бачать лише req.principal", size=12, color=MUTED))
    frags.append(arrow(250, 176, 344, 176, sw=2.0))

    # ── центр: ЄДИНИЙ шов ──
    sx0, sx1 = 348, 604
    cxs = (sx0 + sx1) / 2
    frags.append(rect(sx0, 118, sx1 - sx0, 116, fill="#eafaf1", stroke=FIELD, sw=2, rx=8))
    frags.append(text(cxs, 150, "authenticate()", size=15, bold=True))
    frags.append(text(cxs, 170, "єдиний шов перевірки", size=12, color=MUTED))
    frags.append(line(sx0 + 14, 182, sx1 - 14, 182, color=MUTED, sw=1))
    frags += mtext(cxs, 202, ["validate(presented)", "→ Principal | null"], size=12)
    frags.append(arrow(604, 176, 694, 176, sw=2.0))

    # ── гніздо-рейка ──
    frags.append(line(700, 118, 700, 252, color=MUTED, sw=1.4, dash="4,4"))
    frags.append(circle(700, 176, 5, fill=INK, stroke=INK))

    # ── праворуч: три взаємозамінні начинки ──
    frags.append(text(884, 74, "три взаємозамінні начинки", size=13, bold=True))
    for cy, name, col, dash in (
        (120, "А · server-side store", FIELD, None),
        (185, "Б · stateless JWT", MUTED, "4,4"),
        (250, "В · гібрид access+refresh", MUTED, "4,4"),
    ):
        if dash:
            frags.append(line(700, cy, 780, cy, color=col, sw=1.6, dash=dash))
        else:
            frags.append(arrow(700, cy, 780, cy, color=col, sw=2.0))
        b, _, _ = textbox(884, cy, name, size=13,
                          fill=("#eafaf1" if dash is None else FILL),
                          stroke=(FIELD if dash is None else LINE))
        frags.append(b)

    # ── підпис знизу ──
    frags += mtext(520, 336, [
        "Перевірка «хто це» — за однією точкою; сховище сесії (А / Б / В) — змінна деталь за швом.",
        "Поміняв рядок new …Seam(...) при збірці — жоден викликач не змінився.",
    ], size=12, color=MUTED)

    render(os.path.join(IMG, "one-seam.svg"), W, H, *frags,
           title="Один шов — три змінні начинки")


def fig_category_error():
    """Дві ролі, що їх сплутали: заява між сторонами проти живої сесії."""
    W, H = 980, 430
    frags = [line(490, 66, 490, 384, color=MUTED, sw=1, dash="4,5")]

    # ── Ліворуч: для чого JWT зроблено — заява між сторонами ──
    frags.append(text(245, 44, "Для чого зроблено — заява між сторонами",
                      size=13, bold=True))
    a, _, _ = textbox(150, 132, "сервер\nавторизації", size=12)
    frags.append(a)
    b, _, _ = textbox(352, 132, "сервіс-\nресурс", size=12)
    frags.append(b)
    frags.append(arrow(199, 132, 319, 132, color=NEG, sw=2))
    lb, _, _ = textbox(259, 105, "JWT: заява", size=11, fill=BG, stroke=NEG)
    frags.append(lb)
    frags.append(text(245, 172, "заява про суб'єкта (користувача)", size=10,
                      color=MUTED))
    frags.append(mtext(245, 216, ["сервіс звіряє печатку і вірить,",
                                  "не дзвонячи назад видавцеві"], size=12))
    frags.append(text(245, 302, "самодостатній лист через межу довіри",
                      size=12, color=MUTED))
    frags.append(text(245, 326, "JWT пасує ✓", size=15, bold=True, color=FIELD))

    # ── Праворуч: куди притягли — жива сесія ──
    frags.append(text(735, 44, "Куди притягли — жива сесія", size=13, bold=True))
    s, _, _ = textbox(640, 132, "сервер", size=12)
    frags.append(s)
    br, _, _ = textbox(832, 132, "браузер", size=12)
    frags.append(br)
    frags.append(line(677, 132, 791, 132, color=POS, sw=2))
    lb2, _, _ = textbox(734, 105, "«це ще ти?»", size=11, fill=BG, stroke=POS)
    frags.append(lb2)
    frags.append(text(734, 172, "знову й знову, той самий клієнт", size=10,
                      color=MUTED))
    frags.append(mtext(734, 210, ["треба вміти вимкнути ЗАРАЗ",
                                  "(вихід, крадіжка, забрали право)"], size=12))
    frags.append(text(734, 262, "а підписаний лист нема де скасувати",
                      size=12, color=POS))
    frags.append(text(734, 302, "мінлива правда, та сама сторона", size=12,
                      color=MUTED))
    frags.append(text(734, 326, "JWT не пасує ✗", size=15, bold=True, color=POS))

    render(os.path.join(IMG, "category-error.svg"), W, H, *frags)


def fig_jwt_sessions_arc():
    """Вертикальна хронологія: як JWT занесло в сесії — і винесло назад."""
    W, H = 960, 720
    sx = 310
    frags = [line(sx, 82, sx, 660, color=MUTED, sw=2)]
    nodes = [
        (120, NEG, ["жовтень", "2012"],
         ["OAuth 2.0 (RFC 6749, ред. Д. Гардт):",
          "access + refresh — для делегованого",
          "доступу до ЧУЖОГО ресурсу"]),
        (248, INK, ["травень", "2015"],
         ["JWT (RFC 7519, родина JOSE):",
          "підписаний самодостатній конверт",
          "ЗАЯВ між двома сторонами"]),
        (376, AMBER, ["2015–16"],
         ["хвиля «автентифікація без стану»:",
          "SPA · мікросервіси · серверлес · вендори",
          "«без серверних сесій, масштаб задарма»"]),
        (504, POS, ["червень", "2016"],
         ["Свен Слотвег (joepie91): «Годі",
          "використовувати JWT для сесій» + ч.2 —",
          "JWT не сховище сесій, його не відкликати"]),
        (632, FIELD, ["згодом"],
         ["консенсус: серверні сесії — дефолт",
          "браузерної автентифікації; JWT /",
          "access + refresh — крос-сервіс, API, OAuth2"]),
    ]
    for y, col, dl, rl in nodes:
        frags.append(circle(sx, y, 10, fill=col, stroke=col))
        dy0 = y - (len(dl) - 1) * 14 * 0.65 + 4
        frags.append(mtext(sx - 30, dy0, dl, size=14, color=col,
                           anchor="end", bold=True))
        ry0 = y - (len(rl) - 1) * 13 * 0.65 + 4
        frags.append(mtext(sx + 32, ry0, rl, size=13, color=INK, anchor="start"))
    render(os.path.join(IMG, "jwt-sessions-arc.svg"), W, H, *frags,
           title="Як JWT занесло в сесії — і винесло назад")


if __name__ == "__main__":
    fig_who_holds_truth()
    fig_revocation_window()
    fig_one_seam()
    fig_category_error()
    fig_jwt_sessions_arc()
    print("OK: who-holds-truth.svg, revocation-window.svg, one-seam.svg, "
          "category-error.svg, jwt-sessions-arc.svg")
