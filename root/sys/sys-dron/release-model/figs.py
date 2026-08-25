# -*- coding: utf-8 -*-
"""Фігури до теми «Модель релізів: стабільні, денні збірки, версії»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_two_streams():
    W, H = 1060, 520
    p = []

    # ── ліва колонка: назви двох ліній ─────────────────────────────────
    b, _, _ = textbox(150, 150, ["master", "тут росте нове"],
                      size=15, fill="#eef4ff", stroke=NEG)
    p.append(b)
    p.append(mtext(150, 212, ["щоденна збірка —", "це HEAD цієї гілки"],
                   size=12, color=MUTED))

    b2, _, _ = textbox(150, 370, ["Stable_V5.0", "стабільна лінія"],
                       size=15, fill="#eafaf0", stroke=FIELD)
    p.append(b2)
    p.append(mtext(150, 432, ["патч-реліз —", "новий тег на цій гілці"],
                   size=12, color=MUTED))

    # ── лінія master ───────────────────────────────────────────────────
    p.append(arrow(300, 150, 1020, 150, color=NEG, sw=2.5))
    for x in range(340, 1000, 60):
        p.append(circle(x, 150, 5, fill=NEG, stroke=NEG, sw=1))
    p.append(line(520, 128, 520, 142, color=MUTED, sw=1.5))
    p.append(text(520, 120, "тег d5.1", size=13, color=MUTED))

    # ── відгалуження стабільної ────────────────────────────────────────
    p.append(arrow(470, 165, 500, 355, color=FIELD, sw=2))
    p.append(text(455, 275, "гілку відрізають від master", size=13,
                  color=MUTED, anchor="end"))

    # ── лінія стабільної ───────────────────────────────────────────────
    p.append(arrow(500, 370, 1020, 370, color=FIELD, sw=2.5))
    tags = [
        (600, ["v5.0.0 – v5.0.4", "кандидати"]),
        (760, ["v5.0.6", "перша стабільна"]),
        (890, ["v5.0.7"]),
        (990, ["v5.0.8"]),
    ]
    for x, lines in tags:
        p.append(circle(x, 370, 5, fill=FIELD, stroke=FIELD, sw=1))
        p.append(line(x, 378, x, 392, color=MUTED, sw=1.5))
        p.append(mtext(x, 408, lines, size=12, color=INK))

    # ── повернення виправлень у master ─────────────────────────────────
    p.append(arrow(840, 356, 840, 168, color=POS, sw=2))
    p.append(mtext(858, 240, ["кожне виправлення", "зі стабільної гілки",
                              "повертають у master"],
                   size=13, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'two-streams.svg'), W, H, *p,
           title="Дві лінії постачання: master і стабільна гілка")


def fig_version_fields():
    W, H = 1100, 470
    x1, w1 = 40, 200
    x2, w2 = 260, 400
    x3, w3 = 680, 380
    p = []

    hy, hh = 60, 46
    p.append(fitbox(x1, hy, w1, hh, "номер", size=14, bold=True, fill="#e8ecf2"))
    p.append(fitbox(x2, hy, w2, hh, "що дозволено покласти всередину",
                    size=14, bold=True, fill="#e8ecf2"))
    p.append(fitbox(x3, hy, w3, hh, "що це коштує тому, хто оновлюється",
                    size=14, bold=True, fill="#e8ecf2"))

    rows = [
        (118, "Z — патч",
         ["виправлення, важливі настільки,", "щоб вимагати оновлення,",
          "і безпечні настільки,", "щоб лінія лишалась якісною"],
         ["нічого не треба вчити наново;", "оновлюють між польотами,",
          "а не перед вильотом"]),
        (230, "Y — мінорна",
         ["нове з master: функції,", "підтримка свіжих можливостей",
          "автопілота, перероблені екрани"],
         ["зʼявляються нові екрани;", "документацію читати",
          "від сторінки своєї лінії"]),
        (342, "X — мажорна",
         ["зміни, що ламають звичне:", "інша система збірки,",
          "викинуті старі протоколи,", "вищі вимоги до ОС"],
         ["переучування оператора;", "вендорський форк переносить",
          "свої зміни на нову основу"]),
    ]
    for y, c1, c2, c3 in rows:
        p.append(fitbox(x1, y, w1, 100, c1, size=15, bold=True, fill="#f7f8fa"))
        p.append(fitbox(x2, y, w2, 100, c2, size=14))
        p.append(fitbox(x3, y, w3, 100, c3, size=14))

    render(os.path.join(IMG, 'version-fields.svg'), W, H, *p,
           title="Три числа: що дозволено змінити і чим за це платить користувач")


def fig_which_build():
    W, H = 1000, 440
    p = []
    p.append(line(500, 70, 500, 400, color=MUTED, sw=1.2, dash="6 6"))

    left = 270
    right = 730

    b, _, _ = textbox(left, 110, "прошивка з релізу автопілота",
                      size=14, fill="#eafaf0", stroke=FIELD)
    p.append(b)
    b, _, _ = textbox(right, 110, "прошивка з master автопілота",
                      size=14, fill="#eef4ff", stroke=NEG)
    p.append(b)

    p.append(arrow(left, 132, left, 202, color=MUTED, sw=1.8))
    p.append(arrow(right, 132, right, 202, color=MUTED, sw=1.8))

    b, _, _ = textbox(left, 230, ["стабільна збірка станції",
                                  "vX.Y.Z, тег на гілці Stable_VX.Y"],
                      size=13, fill="#eafaf0", stroke=FIELD)
    p.append(b)
    b, _, _ = textbox(right, 230, ["щоденна збірка",
                                   "HEAD гілки master, тега немає"],
                      size=13, fill="#eef4ff", stroke=NEG)
    p.append(b)

    p.append(arrow(left, 258, left, 322, color=MUTED, sw=1.8))
    p.append(arrow(right, 258, right, 322, color=MUTED, sw=1.8))

    b, _, _ = textbox(left, 350, ["поведінка передбачувана;",
                                  "інструменти розробника сховані"],
                      size=13, fill="#f7f8fa")
    p.append(b)
    b, _, _ = textbox(right, 350, ["Mock Link та інша оснастка ввімкнені;",
                                   "ризик збоїв — на тому, хто взяв"],
                      size=13, fill="#f7f8fa")
    p.append(b)

    render(os.path.join(IMG, 'which-build.svg'), W, H, *p,
           title="Збірку станції обирає та сторона, звідки взято прошивку")


# ─────────────────────────────────────────────────────────────────────
#  Фігури до вставки «Як мінялись лінії версій QGroundControl»
# ─────────────────────────────────────────────────────────────────────

def fig_version_lines():
    """Смуги мажорних ліній у часі + що змусило підняти номер."""
    W, H = 1240, 620
    Y0, Y1 = 2010.0, 2027.0
    X0, X1 = 430, 1195

    def X(year):
        return X0 + (year - Y0) * (X1 - X0) / (Y1 - Y0)

    p = []

    # ── вісь років ────────────────────────────────────────────────────
    axis_y = 118
    p.append(line(X0, axis_y, X1, axis_y, color=MUTED, sw=1.2))
    for yr in range(2010, 2027, 2):
        p.append(line(X(yr), axis_y - 6, X(yr), axis_y, color=MUTED, sw=1.2))
        p.append(text(X(yr), axis_y - 14, str(yr), size=13, color=MUTED))

    lanes = [
        (180, 2010.25, 2014.50, "#dbe4f5", NEG,
         "1.x", "Qt 4.8, вікна з віджетів",
         "перший коміт — квітень 2010"),
        (270, 2014.50, 2016.58, "#d7ecfa", NEG,
         "2.x", "перехід на Qt 5",
         "теги від v2.2, січень 2015"),
        (360, 2016.58, 2020.15, "#d9f2e2", FIELD,
         "3.x", "інтерфейс переписано на QML",
         "v3.0.0, липень 2016"),
        (450, 2020.15, 2025.53, "#fdeadb", POS,
         "4.x", "64 біти, Qt 5.12, скинуті налаштування",
         "v4.0.0, лютий 2020"),
        (540, 2025.53, 2027.0, "#f6dcdc", POS,
         "5.x", "Qt 6 і CMake замість qmake",
         "v5.0.6, липень 2025"),
    ]

    for y, a, b, fill, edge, name, why, when in lanes:
        # підпис лінії ліворуч, з широкою колонкою
        p.append(fitbox(40, y - 34, 360, 68, [name + " — " + why, when],
                        size=14, fill="#f7f8fa", stroke=MUTED))
        p.append(rect(X(a), y - 20, X(b) - X(a), 40, fill=fill,
                      stroke=edge, sw=1.6, rx=8))
        p.append(text((X(a) + X(b)) / 2, y + 6,
                      "%.1f роки" % (b - a) if (b - a) < 5 else
                      "%.1f роки" % (b - a),
                      size=13, color=INK))

    # ── дві позначки причин пауз ──────────────────────────────────────
    p.append(line(X(2021.0), 490, X(2021.0), 585, color=MUTED, sw=1.4,
                  dash="5 5"))
    p.append(line(X(2023.9), 490, X(2023.9), 585, color=MUTED, sw=1.4,
                  dash="5 5"))
    p.append(mtext((X(2021.0) + X(2023.9)) / 2, 604,
                   ["затишшя 2021–2023: майже нема комітів,",
                    "мажорну лінію нема кому довести"],
                   size=13, color=MUTED))

    render(os.path.join(IMG, 'version-lines.svg'), W, H, *p,
           title="Мажорні лінії QGroundControl у часі й привід кожного підняття")


def fig_commit_activity():
    """Кількість комітів у master за роками — видно затишшя 2021–2023."""
    W, H = 1140, 520
    data = [
        (2010, 918), (2011, 839), (2012, 537), (2013, 1164), (2014, 1490),
        (2015, 2417), (2016, 2212), (2017, 2288), (2018, 1926), (2019, 1944),
        (2020, 1648), (2021, 750), (2022, 277), (2023, 355), (2024, 1101),
        (2025, 1170), (2026, 671),
    ]
    p = []
    base_y = 400
    top_y = 110
    max_v = 2500
    left = 90
    step = 60
    bw = 38

    # ── горизонтальні мітки шкали ─────────────────────────────────────
    for v in (0, 500, 1000, 1500, 2000, 2500):
        y = base_y - (v / max_v) * (base_y - top_y)
        p.append(line(left - 12, y, left + step * len(data) - 12, y,
                      color="#dfe3e8", sw=1))
        p.append(text(left - 24, y + 5, str(v), size=12, color=MUTED,
                      anchor="end"))

    for i, (yr, v) in enumerate(data):
        x = left + i * step
        h = (v / max_v) * (base_y - top_y)
        quiet = yr in (2021, 2022, 2023)
        p.append(rect(x - bw / 2, base_y - h, bw, h,
                      fill=("#f6dcdc" if quiet else "#dbe4f5"),
                      stroke=(POS if quiet else NEG), sw=1.4, rx=3))
        p.append(text(x, base_y - h - 10, str(v), size=12, color=INK))
        p.append(text(x, base_y + 22, str(yr), size=12, color=MUTED))

    p.append(line(left - 12, base_y, left + step * len(data) - 12, base_y,
                  color=MUTED, sw=1.4))

    p.append(mtext(left + step * 12.6, 462,
                   ["2026 рік неповний —",
                    "лічено до серпня"],
                   size=12, color=MUTED))
    p.append(mtext(left + step * 5.5, 68,
                   ["Коміти в master за роками: після 2020 активність падає"
                    " майже вдесятеро й вертається лише у 2024"],
                   size=14, color=INK))

    render(os.path.join(IMG, 'commit-activity.svg'), W, H, *p,
           title="Коміти в master QGroundControl за роками")


def fig_describe_anatomy():
    """Розбір того, що повертає git describe, і куди йде кожна складова."""
    W, H = 1120, 460
    p = []

    cols = [
        (200, "v5.0.0",
         ["найближчий тег", "нижче за HEAD в історії"],
         ["дає числа версії:", "мажорну, мінорну, патч"]),
        (560, "124",
         ["скільки комітів лягло", "після цього тега"],
         ["лічильник розробки:", "останні три цифри коду"]),
        (920, "g8b479120f",
         ["скорочений хеш", "самого коміта"],
         ["лише для впізнання збірки:", "у число НЕ входить"]),
    ]

    for cx, token, what, where in cols:
        b, _, _ = textbox(cx, 105, token, size=19, bold=True,
                          fill="#eef4ff", stroke=NEG, pad=14)
        p.append(b)
        p.append(arrow(cx, 140, cx, 196, color=MUTED, sw=1.8))
        b, _, _ = textbox(cx, 230, what, size=13, fill="#f7f8fa")
        p.append(b)
        p.append(arrow(cx, 268, cx, 324, color=MUTED, sw=1.8))
        b, _, _ = textbox(cx, 358, where, size=13, fill="#eafaf0", stroke=FIELD)
        p.append(b)

    for x in (380, 740):
        p.append(text(x, 113, "–", size=22, color=MUTED))

    p.append(text(W / 2, 428,
                  "на самому тезі хвоста немає: git describe друкує «v5.0.0», "
                  "і лічильник дорівнює нулю",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'describe-anatomy.svg'), W, H, *p,
           title="git describe --tags: тег, відстань до нього, хеш коміта")


def fig_versioncode_ladder():
    """Де в числовій шкалі магазину сидять щоденні збірки."""
    W, H = 1120, 550
    p = []

    p.append(text(W / 2, 56,
                  "BB M I PP DDD   —   66 (64-бітне ABI) · мажорна · мінорна · "
                  "патч · коміти після тега",
                  size=13, color=MUTED))

    # ── панель А: крок стабільної лінії ─────────────────────────────────
    p.append(text(W / 2, 92,
                  "Сусідні патчі стабільної лінії відрізняються рівно на 1000",
                  size=14, color=INK))

    p.append(arrow(120, 160, 1020, 160, color=MUTED, sw=2))
    stable = [(200, "v5.1.0", "665100000"), (460, "v5.1.1", "665101000"),
              (720, "v5.1.2", "665102000"), (980, "v5.1.3", "665103000")]
    for x, tag, code in stable:
        p.append(line(x, 150, x, 170, color=INK, sw=2))
        p.append(text(x, 138, tag, size=14, color=INK, bold=True))
        p.append(text(x, 192, code, size=13, color=MUTED))

    # ── збільшення одного проміжку ─────────────────────────────────────
    p.append(line(200, 206, 140, 300, color=MUTED, sw=1.2, dash="5,4"))
    p.append(line(460, 206, 1000, 300, color=MUTED, sw=1.2, dash="5,4"))
    p.append(text(480, 256, "збільшено проміжок між двома сусідніми патчами",
                  size=13, color=MUTED))

    # ── панель Б: що лежить усередині проміжку ─────────────────────────
    p.append(line(140, 340, 1000, 340, color=INK, sw=2))
    for i in range(19):
        x = 182 + i * 43
        p.append(line(x, 332, x, 348, color=NEG, sw=1.2))
    p.append(line(140, 328, 140, 352, color=INK, sw=2.5))
    p.append(line(1000, 328, 1000, 352, color=INK, sw=2.5))

    p.append(text(140, 316, "665100000", size=14, color=INK, bold=True))
    p.append(text(570, 316, "665100001 … 665100999", size=14, color=NEG,
                  bold=True))
    p.append(text(1000, 316, "665101000", size=14, color=INK, bold=True))

    p.append(text(140, 372, "v5.1.0", size=13, color=MUTED))
    p.append(text(570, 372,
                  "щоденні збірки — по одному числу на кожен коміт після d5.1.0",
                  size=13, color=NEG))
    p.append(text(1000, 372, "v5.1.1", size=13, color=MUTED))

    b, _, _ = textbox(W / 2, 448,
                      ["У полі лічильника три цифри, тож 999 — стеля.",
                       "Тисячний коміт дав би рівно 665101000 — число, "
                       "зайняте патчем v5.1.1,",
                       "тому збірка обрізає лічильник на 999 і попереджає."],
                      size=13, fill="#f7f8fa", pad=14)
    p.append(b)

    p.append(text(W / 2, 528,
                  "уся попередня лінія лежить нижче: v5.0.Z дають "
                  "665000000 … 665099000",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'versioncode-ladder.svg'), W, H, *p,
           title="Числа щоденних збірок сидять у щілинах між патчами")


def fig_hist_clocks():
    """Три чужі годинники (Qt, інструмент збірки, версія протоколу) і моменти,
       коли мажорний номер станції мусив піднятись. Фігура до вставки hist-version-lines."""
    W, H = 1280, 560
    Y0, Y1 = 2009.0, 2027.0
    X0, X1 = 350, 1215

    def X(y):
        return X0 + (y - Y0) * (X1 - X0) / (Y1 - Y0)

    p = []

    # ── вісь років ─────────────────────────────────────────────────────
    axis_y = 92
    p.append(line(X0, axis_y, X1, axis_y, color=MUTED, sw=1.2))
    for yr in range(2010, 2027, 2):
        p.append(line(X(yr), axis_y - 6, X(yr), axis_y, color=MUTED, sw=1.2))
        p.append(text(X(yr), axis_y - 13, str(yr), size=13, color=MUTED))

    rows = [
        (150, "Qt — оснастка, на якій стоїть увесь код",
         [(2009.0, 2014.5, "#dbe4f5", NEG, ["Qt 4", "(phonon, webkit)"]),
          (2014.5, 2016.6, "#d7ecfa", NEG, ["Qt 5.2+"]),
          (2016.6, 2020.15, "#d9f2e2", FIELD, ["Qt 5.5+"]),
          (2020.15, 2025.37, "#fdeadb", POS, ["Qt 5.11+, а з кінця 2020-го —",
                                              "глухий кут: 5.15.2 і тільки вона"]),
          (2025.37, 2027.0, "#f6dcdc", POS, ["Qt 6.8", "→ 6.10"])]),
        (270, "інструмент збірки",
         [(2009.0, 2025.37, "#eef4ff", NEG, ["qmake"]),
          (2025.37, 2027.0, "#f6dcdc", POS, ["CMake"])]),
        (390, "версія протоколу, яку станція розуміє",
         [(2009.0, 2017.0, "#eef4ff", NEG, ["лише MAVLink v1"]),
          (2017.0, 2025.37, "#eafaf0", FIELD, ["v1 і v2 водночас — станція вміє",
                                               "мовчки впасти назад на v1"]),
          (2025.37, 2027.0, "#f6dcdc", POS, ["лише v2"])]),
    ]

    band = 54
    for cy, label, segs in rows:
        p.append(fitbox(24, cy - band / 2, 310, band, [label],
                        size=14, fill="#f7f8fa", stroke=MUTED))
        for a, b, fill, edge, lines in segs:
            p.append(fitbox(X(a), cy - band / 2, X(b) - X(a), band, lines,
                            size=14, pad=6, fill=fill, stroke=edge, sw=1.6))

    # ── вертикальні пунктири — ТІЛЬКИ у проміжках між смугами ───────────
    gaps = [(axis_y + 8, 150 - band / 2), (150 + band / 2, 270 - band / 2),
            (270 + band / 2, 390 - band / 2), (390 + band / 2, 448)]
    marks = [(2016.58, "v3.0.0"), (2020.15, "v4.0.0"), (2025.37, "v5.0.0")]
    for xm, _ in marks:
        for ya, yb in gaps:
            p.append(line(X(xm), ya, X(xm), yb, color=MUTED, sw=1.2, dash="5 5"))

    # ── підписи мажорних підйомів під нижньою смугою ────────────────────
    tags = [
        (2016.58, ["v3.0.0 · липень 2016", "з Qt прибрали webkit"]),
        (2020.15, ["v4.0.0 · лютий 2020", "формат налаштувань і 64 біти"]),
        (2025.37, ["v5.0.0 · травень 2025", "три борги одним махом"]),
    ]
    for xm, lines in tags:
        b, w, _ = textbox(X(xm), 480, lines, size=13, fill="#ffffff", stroke=MUTED)
        p.append(b)

    p.append(text(W / 2, 538,
                  "мажорний номер підіймався не тоді, коли назбиралось нового, "
                  "а тоді, коли зрушувався чужий годинник",
                  size=13, color=INK, italic=True))

    render(os.path.join(IMG, 'hist-clocks.svg'), W, H, *p,
           title="Три годинники, яких проєкт не заводить")


if __name__ == '__main__':
    fig_hist_clocks()
    fig_two_streams()
    fig_version_fields()
    fig_which_build()
    fig_version_lines()
    fig_commit_activity()
    fig_describe_anatomy()
    fig_versioncode_ladder()
    print("ok:", os.listdir(IMG))
