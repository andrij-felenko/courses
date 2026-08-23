# -*- coding: utf-8 -*-
"""Фігури до кроку «Навіщо розподіляти».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER = "#b45309"   # акцент для «географії» та «середнього» щабля
GRN_D = "#0e7d4b"   # темно-зелений акцент
RED_T, GRN_T, AMB_T, NEU_T = "#fdecea", "#eafaf0", "#fdf6e3", "#f4f6f8"


# ───────── Фіг. 1: чотири стіни однієї машини ─────────
def fig_four_walls():
    W, H = 1120, 560
    f = []

    # центральна машина
    bx, by, bw, bh = 490, 130, 140, 300
    f.append(rect(bx, by, bw, bh, fill="#eef2fb", stroke=INK, sw=2))
    f.append(mtext(bx + bw / 2, by + 44,
                   ["ОДНА", "МАШИНА"], size=16, bold=True, color=INK, lh=1.15))
    f.append(mtext(bx + bw / 2, by + 150,
                   ["усе скінченне:", "диск · RAM", "пропускна", "аптайм"],
                   size=11.5, color=MUTED, lh=1.4))

    def wall(x, y, title, accent, phys, thresh, shape, shape_tint, shape_stroke):
        w, h = 380, 180
        o = rect(x, y, w, h, fill="#ffffff", stroke=accent, sw=2)
        o += text(x + w / 2, y + 32, title, size=17, bold=True, color=accent)
        o += mtext(x + w / 2, y + 60, phys, size=12.5, color=INK, lh=1.25)
        o += text(x + w / 2, y + h - 52, thresh, size=11, italic=True, color=MUTED)
        o += fitbox(x + 24, y + h - 40, w - 48, 30, shape,
                    size=12.5, fill=shape_tint, stroke=shape_stroke, color=INK, bold=True, sw=1.7)
        return o

    # ліві стіни
    f.append(wall(60, 90, "НЕ ВЛАЗИТЬ", POS,
                  ["набір даних більший", "за диск чи RAM однієї машини"],
                  "100 ТБ у машину на 32 не влізуть",
                  "форма: РОЗБИТИ дані", RED_T, POS))
    f.append(wall(60, 300, "ВПАДЕ", NEG,
                  ["машина колись неодмінно помре —", "аптайм має жорстку стелю"],
                  "згорів диск — зникла вся правда",
                  "форма: КОПІЇ в різних доменах відмови", GRN_T, FIELD))
    # праві стіни
    f.append(wall(680, 90, "НЕ ВСТИГАЄ", GRN_D,
                  ["потік запитів більший", "за те, що бере одна машина"],
                  "десятки тис. запитів/с — стеля вузла",
                  "читання: КОПІЇ · записи: РОЗБИТИ", NEU_T, MUTED))
    f.append(wall(680, 300, "ДАЛЕКО", AMBER,
                  ["світло ~200 000 км/с у волокні —", "непорушний спід на затримку"],
                  "Нью-Йорк⇄Сідней ≈160 мс туди-й-назад",
                  "форма: КОПІЇ ближче до людей", GRN_T, FIELD))

    # стрілки від машини до кожної стіни (назовні)
    f.append(arrow(bx, 180, 445, 180, color=POS, sw=2.2))
    f.append(arrow(bx, 390, 445, 390, color=NEG, sw=2.2))
    f.append(arrow(bx + bw, 180, 675, 180, color=GRN_D, sw=2.2))
    f.append(arrow(bx + bw, 390, 675, 390, color=AMBER, sw=2.2))

    render(os.path.join(IMG, "four-walls.svg"), W, H, *f,
           title="Чотири стіни однієї машини — кожна інша фізика, кожна жене в свій бік")


# ───────── Фіг. 2: драбина розподілу — координація дорожчає зі щаблем ─────────
def fig_ladder():
    W, H = 1100, 580
    f = []

    def step(x, y, title, accent, buys, chip, chip_tint, chip_stroke):
        w, h = 300, 150
        o = rect(x, y, w, h, fill="#ffffff", stroke=accent, sw=2)
        o += text(x + w / 2, y + 32, title, size=15, bold=True, color=accent)
        o += text(x + 20, y + 62, "купує: " + buys, size=12, color=INK, anchor="start")
        o += fitbox(x + 20, y + h - 46, w - 40, 32, chip,
                    size=12, fill=chip_tint, stroke=chip_stroke, color=INK, bold=True, sw=1.6)
        return o

    # три щаблі, що піднімаються зліва направо
    f.append(step(70, 370, "1. Одна більша машина", MUTED,
                  "ємність і потік надовго",
                  "координація: НУЛЬ", GRN_T, FIELD))
    f.append(step(400, 250, "2. Репліки для читань", NEG,
                  "витривалість і читання",
                  "платить лише лагом реплік", AMB_T, AMBER))
    f.append(step(730, 130, "3. Розбити — багато писарів", POS,
                  "потік записів і ємність",
                  "консенсус · замки · 2PC · годинники", RED_T, POS))

    # far-left вертикальна стрілка «податок росте»
    f.append(arrow(45, 515, 45, 135, color=INK, sw=2))
    f.append(mtext(235, 170, ["▲ що вищий щабель —", "то дорожча координація"],
                   size=13, bold=True, color=INK, lh=1.3))

    # маленькі сходинкові стрілки між щаблями
    f.append(arrow(372, 430, 398, 360, color=MUTED, sw=1.8))
    f.append(arrow(702, 310, 728, 240, color=MUTED, sw=1.8))

    # правило внизу
    f.append(fitbox(70, 522, 960, 34,
                    "правило: копії — раніше за розбиття, розбиття — раніше за багато писарів; піднімайся лише під поміряним числом",
                    size=12.5, fill=NEU_T, stroke=INK, color=INK, bold=True, sw=1.6))

    render(os.path.join(IMG, "ladder.svg"), W, H, *f,
           title="Драбина розподілу: кожен вищий щабель дорожчий за попередній")


# ───────── Фіг. 3: DH — який набір даних об яку стіну ─────────
def fig_dh_datasets():
    W, H = 1060, 530
    f = []

    # заголовки колонок
    f.append(text(160, 74, "набір даних", size=12, color=MUTED, bold=True))
    f.append(text(400, 74, "обсяг · потік", size=12, color=MUTED, bold=True))
    f.append(text(650, 74, "стіни", size=12, color=MUTED, bold=True))
    f.append(text(880, 74, "вирок", size=12, color=MUTED, bold=True))

    def row(y, accent, name, sub, vol, flow, wall_chips, verdict, v_tint, v_stroke):
        x, w, h = 60, 940, 170
        o = rect(x, y, w, h, fill="#ffffff", stroke=accent, sw=2)
        # A: назва
        o += text(x + 20, y + 66, name, size=16, bold=True, color=accent, anchor="start")
        o += text(x + 20, y + 92, sub, size=11.5, italic=True, color=MUTED, anchor="start")
        # роздільники колонок
        for sx in (280, 540, 760):
            o += line(x + sx, y + 16, x + sx, y + h - 16, color="#e5e7eb", sw=1.2)
        # B: метрики
        o += text(x + 300, y + 70, vol, size=13, color=INK, anchor="start")
        o += text(x + 300, y + 100, flow, size=13, color=INK, anchor="start")
        # C: стіни (чипи)
        cy = y + 52
        for label, tint, stroke in wall_chips:
            o += fitbox(x + 552, cy, 190, 34, label, size=11.5,
                        fill=tint, stroke=stroke, color=INK, bold=True, sw=1.6)
            cy += 44
        # D: вирок
        o += fitbox(x + 772, y + 54, 150, 62, verdict, size=11.5,
                    fill=v_tint, stroke=v_stroke, color=INK, bold=True, sw=1.7)
        return o

    f.append(row(90, POS, "Телеметрія", "потік із пристроїв",
                 "~52 ТБ/рік", "~33 000 записів/с",
                 [("НЕ ВЛАЗИТЬ", RED_T, POS), ("НЕ ВСТИГАЄ (запис)", RED_T, POS)],
                 "→ розбити\nза home_id\n(доми незалежні\n→ дешево)", RED_T, POS))
    f.append(row(290, FIELD, "Реєстр і стан", "усе, що не телеметрія",
                 "~7 ГБ", "потік малий",
                 [("жодної стіни", GRN_T, FIELD)],
                 "→ один вузол\n+ репліки,\nще роками", GRN_T, FIELD))

    f.append(fitbox(60, 478, 940, 34,
                    "розподіляй набір даних, що вперся в стіну, — не всю систему",
                    size=13.5, fill=NEU_T, stroke=INK, color=INK, bold=True, sw=1.6))

    render(os.path.join(IMG, "dh-datasets.svg"), W, H, *f,
           title="Digital Homes: розбити те, що вперлося, — і лише те")


# ───────── Фіг. 4 (вставка hist): маятник розподілу в часі ─────────
def fig_pendulum():
    W, H = 1220, 680
    f = []

    def polyline(points, color, sw):
        pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                'stroke-linejoin="round" stroke-linecap="round"/>' % (pts, color, sw))

    # смуги-полюси
    f.append(rect(70, 55, 1080, 150, fill=RED_T, stroke="#f2c9c2", sw=1))
    f.append(rect(70, 300, 1080, 105, fill=GRN_T, stroke="#bfe6cf", sw=1))
    f.append(text(90, 92, "РОЗБИТИ ВСЕ — бейдж зрілості",
                  size=15, bold=True, color=POS, anchor="start"))
    f.append(text(610, 388, "ОДНА МАШИНА — нудно, дешево, працює",
                  size=15, bold=True, color=FIELD, anchor="middle"))

    # крива-маятник: угору до піка (2010), тоді вниз назад
    pts = [(150, 355), (310, 348), (500, 250), (620, 155),
           (720, 112), (860, 200), (1000, 300), (1110, 360)]
    years = ["1976", "1986", "2003", "2006", "2010", "2015", "2017", "2023"]
    f.append(polyline(pts[0:5], POS, 3.2))     # хитнуло до розбиття
    f.append(polyline(pts[4:8], FIELD, 3.2))   # хитнуло назад
    ycol = [POS, POS, POS, POS, POS, FIELD, FIELD, FIELD]
    ylab = [(150, 378), (310, 372), (500, 236), (620, 138),
            (720, 95), (860, 224), (1000, 324), (1110, 384)]
    for (x, y), c, yr, (lx, ly) in zip(pts, ycol, years, ylab):
        f.append(circle(x, y, 6, fill=BG, stroke=c, sw=2.5))
        f.append(text(lx, ly, yr, size=13, bold=True, color=INK))

    # роздільник і легенда подій
    f.append(line(70, 422, 1150, 422, color="#e5e7eb", sw=1.2))
    f.append(text(90, 448, "Хитнуло ДО розбиття — сила, потім мода",
                  size=14, bold=True, color=POS, anchor="start"))
    f.append(text(660, 448, "Хитнуло НАЗАД — до однієї машини",
                  size=14, bold=True, color=FIELD, anchor="start"))

    left = [
        "1976 · Tandem NonStop — shared-nothing заради відмовостійкості",
        "1983 · Teradata (DBC/1012) — перша комерційна shared-nothing БД",
        "1986 · Stonebraker: «The Case for Shared Nothing» — названо й на щит",
        "2003–06 · Google: GFS · MapReduce · Bigtable — «розподілити все» = мрія",
        "2009–10 · NoSQL-мітап · «MongoDB is web scale» — масштаб як бейдж",
    ]
    right = [
        "2015 · «Monolith First» (Fowler) · «Boring Technology» (McKinley)",
        "2017 · «You Are Not Google» (Oz Nova / Ozan Onay) — метод UNPHAT",
        "2023 · «Just Use Postgres for Everything» (Schmidt) — згорнути стек",
    ]
    for i, s in enumerate(left):
        y = 474 + i * 26
        f.append(circle(92, y - 4, 3, fill=POS, stroke=POS, sw=1))
        f.append(text(104, y, s, size=13, color=INK, anchor="start"))
    for i, s in enumerate(right):
        y = 474 + i * 26
        f.append(circle(662, y - 4, 3, fill=FIELD, stroke=FIELD, sw=1))
        f.append(text(674, y, s, size=13, color=INK, anchor="start"))

    f.append(fitbox(70, 632, 1080, 34,
                    "щоразу тяглися до розбиття як до бейджа — перш ніж сила змусила; "
                    "і щоразу верталися до правила: спершу назви силу числом",
                    size=13, fill=NEU_T, stroke=INK, color=INK, bold=True, sw=1.6))

    render(os.path.join(IMG, "pendulum.svg"), W, H, *f,
           title="Маятник розподілу: між «розбити все» і «одна машина»")


if __name__ == "__main__":
    fig_four_walls()
    fig_ladder()
    fig_dh_datasets()
    fig_pendulum()
    print("OK: four-walls.svg, ladder.svg, dh-datasets.svg, pendulum.svg")
