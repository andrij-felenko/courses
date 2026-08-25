# -*- coding: utf-8 -*-
"""Фігури до теми «Рельєф і режими висоти в плані»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def tb(cx, cy, s, **kw):
    return textbox(cx, cy, s, **kw)[0]


def polyline(pts, color=LINE, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


# ─────────────────────────────────────────────────────────────────────────────
# 1. Чотири режими висоти: одне число 50 — чотири різні точки
# ─────────────────────────────────────────────────────────────────────────────
def fig_altitude_modes():
    W, H = 1240, 880
    SEA = 700.0          # рівень моря на полотні
    K = 3.0              # пікселів на метр

    def yy(alt_m):
        return SEA - K * alt_m

    f = []

    # рельєф (схил, що піднімається зліва направо)
    terrain_m = [(60, 24), (260, 36), (400, 44), (500, 52), (620, 62),
                 (740, 74), (860, 88), (980, 100), (1180, 118)]
    terrain = [(x, yy(a)) for x, a in terrain_m]

    # рівень моря
    f.append(line(50, SEA, 1200, SEA, color=NEG, sw=2.0))
    f.append(text(1190, 726, "рівень моря", size=13, color=NEG, anchor="end"))

    # рельєф
    f.append(polyline(terrain, color=INK, sw=2.6))
    f.append(text(1105, 500, "рельєф", size=13, color=INK, anchor="middle"))

    # домашня точка і її рівень
    home_alt = 29.3
    f.append(line(140, yy(home_alt), 520, yy(home_alt), color=MUTED, sw=1.6, dash="7 5"))
    f.append(circle(140, yy(home_alt), 7, fill="#ffffff", stroke=FIELD, sw=2.4))
    f.append(text(140, 654, "домашня точка", size=12, color=FIELD, anchor="middle"))
    f.append(text(424, 654, "рівень домашньої точки", size=11, color=MUTED, anchor="middle"))

    # чотири випадки: (x, від якої висоти відлік, підпис режиму)
    cases = [
        (260, 0.0,      "Absolute"),
        (500, home_alt, "Relative"),
        (740, 74.0,     "CalcAboveTerrain"),
        (980, 100.0,    "Terrain"),
    ]
    for x, base_m, name in cases:
        y_base = yy(base_m)
        y_top = yy(base_m + 50.0)
        f.append(line(x, y_base, x, y_top, color=POS, sw=1.8, dash="6 4"))
        f.append(circle(x, y_top, 9, fill="#fdecea", stroke=POS, sw=2.4))
        f.append(text(x, y_top - 20, "50 м", size=13, color=POS, bold=True))
        f.append(text(x, y_top - 44, name, size=14, bold=True))

    # що йде на борт
    wire = [
        (260, ["відлік від рівня моря", "MAV_FRAME_GLOBAL", "param7 = 50"]),
        (500, ["відлік від домашньої точки", "MAV_FRAME_GLOBAL_RELATIVE_ALT", "param7 = 50"]),
        (740, ["відлік від рельєфу, рахує станція", "MAV_FRAME_GLOBAL", "param7 = 124"]),
        (980, ["відлік від рельєфу, рахує борт", "MAV_FRAME_GLOBAL_TERRAIN_ALT", "param7 = 50"]),
    ]
    for x, lines in wire:
        f.append(tb(x, 800, "\n".join(lines), size=10, pad=9))

    render(os.path.join(IMG, "altitude-modes.svg"), W, H, *f,
           title="Одне число 50 у чотирьох режимах висоти")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Шлях від координати до висоти рельєфу
# ─────────────────────────────────────────────────────────────────────────────
def fig_terrain_query():
    W, H = 1240, 790
    CX = 360
    f = []

    stages = [
        (110, "Елемент місії: координата змінилась"),
        (240, "Таймер елемента місії\nперезапускається на кожен рух"),
        (370, "Спільний накопичувач запитів\nтаймер 500 мс, не більш ніж 50 координат"),
        (500, "Менеджер плиток\nплитка 0.01° × 0.01°, крок 1″ ≈ 30 м"),
        (650, "Висота рельєфу під координатою"),
    ]
    for cy, s in stages:
        f.append(tb(CX, cy, s, size=13))

    # стрілки між ступенями
    for i in range(len(stages) - 1):
        y1 = stages[i][0] + 34
        y2 = stages[i + 1][0] - 34
        f.append(arrow(CX, y1, CX, y2))

    # сервер висот збоку
    f.append(tb(900, 500, "Сервер висот\nодне звернення на пачку", size=13))
    f.append(arrow(516, 478, 786, 478))
    f.append(arrow(786, 524, 516, 524))
    f.append(text(651, 462, "немає в кеші", size=11, color=MUTED))
    f.append(text(651, 552, "плитка з висотами", size=11, color=MUTED))

    # пояснювальні написи праворуч
    f.append(text(790, 246, "увесь потік проміжних координат зникає", size=12, color=MUTED))
    f.append(text(790, 376, "сто елементів місії → два звернення в мережу", size=12, color=MUTED))
    f.append(text(790, 656, "невдалі плитки запам'ятовуються з відміткою часу", size=12, color=MUTED))

    render(os.path.join(IMG, "terrain-query.svg"), W, H, *f,
           title="Від руху миші до висоти рельєфу: три ступені гасіння")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Хто рахує рельєф: станція один раз чи борт безперервно
# ─────────────────────────────────────────────────────────────────────────────
def fig_who_computes():
    W, H = 1280, 710
    f = []

    # ── рамки панелей
    f.append(rect(40, 56, 580, 600, fill="#ffffff", sw=2.0, rx=10))
    f.append(rect(660, 56, 580, 600, fill="#ffffff", sw=2.0, rx=10))
    f.append(text(330, 92, "CalcAboveTerrain — рахує станція", size=15, bold=True))
    f.append(text(950, 92, "Terrain — рахує борт", size=15, bold=True))

    base = [(80, 400), (150, 395), (220, 370), (290, 310), (360, 300),
            (430, 345), (500, 385), (570, 395)]

    # ── ліва панель: пряма між елементами місії ріже гребінь
    f.append(polyline(base, color=INK, sw=2.4))
    f.append(line(150, 335, 500, 325, color=POS, sw=2.4))
    f.append(circle(150, 335, 8, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(circle(500, 325, 8, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(circle(263, 332, 6, fill=POS, stroke=POS, sw=1.5))
    f.append(circle(411, 328, 6, fill=POS, stroke=POS, sw=1.5))
    f.append(text(240, 258, "шлях апарата — пряма", size=12, color=POS))
    f.append(tb(330, 500, "на дроті: MAV_FRAME_GLOBAL\nчисло — метри над рівнем моря", size=11, pad=9))
    f.append(tb(330, 590, "рельєфу на борту немає:\nгребінь між елементами не бачить ніхто", size=11, pad=9))

    # ── права панель: шлях повторює рельєф
    base_r = [(x + 620, y) for x, y in base]
    f.append(polyline(base_r, color=INK, sw=2.4))
    path_r = [(770, 335), (840, 310), (910, 250), (980, 240),
              (1050, 285), (1120, 325)]
    f.append(polyline(path_r, color=FIELD, sw=2.6))
    f.append(circle(770, 335, 8, fill="#eafaf0", stroke=FIELD, sw=2.2))
    f.append(circle(1120, 325, 8, fill="#eafaf0", stroke=FIELD, sw=2.2))
    f.append(text(900, 200, "шлях апарата — за рельєфом", size=12, color=FIELD))
    f.append(tb(950, 500, "на дроті: MAV_FRAME_GLOBAL_TERRAIN_ALT\nчисло — метри над землею", size=11, pad=9))
    f.append(tb(950, 590, "рельєф має бути на борту: картка пам'яті\nабо TERRAIN_DATA зі станції", size=11, pad=9))

    render(os.path.join(IMG, "who-computes.svg"), W, H, *f,
           title="Два режими над рельєфом різняться тим, хто відповідає за рельєф")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Профіль плану: перевірка хорди по всьому відрізку, крім зльоту й посадки
# ─────────────────────────────────────────────────────────────────────────────
def fig_segment_collision():
    W, H = 1240, 580
    f = []

    terrain = [(80, 455), (200, 450), (320, 430), (440, 400), (560, 352),
               (620, 300), (680, 288), (740, 310), (800, 370), (920, 410),
               (1040, 440), (1180, 450)]
    f.append(polyline(terrain, color=INK, sw=2.6))
    f.append(text(150, 508, "профіль рельєфу", size=12, color=INK))

    T = (140, 452)
    WP1 = (320, 330)
    WP2 = (560, 300)
    WP3 = (800, 305)
    L = (1040, 438)

    # відрізки: зліт, звичайний, зіткнення, посадка
    f.append(line(T[0], T[1], WP1[0], WP1[1], color=FIELD, sw=2.6))
    f.append(line(WP1[0], WP1[1], WP2[0], WP2[1], color=FIELD, sw=2.6))
    f.append(line(WP2[0], WP2[1], WP3[0], WP3[1], color=POS, sw=3.0))
    f.append(line(WP3[0], WP3[1], L[0], L[1], color=FIELD, sw=2.6))

    # вилучені з перевірки початок зльоту й кінець посадки
    f.append(line(T[0], T[1], 185, 422, color=MUTED, sw=5.0))
    f.append(line(995, 408, L[0], L[1], color=MUTED, sw=5.0))

    for p in (T, WP1, WP2, WP3, L):
        f.append(circle(p[0], p[1], 7, fill="#ffffff", stroke=INK, sw=2.0))

    f.append(text(680, 244, "зіткнення з рельєфом", size=13, color=POS, bold=True))
    f.append(text(126, 392, "зліт", size=12, color=MUTED, anchor="end"))
    f.append(text(1064, 392, "посадка", size=12, color=MUTED, anchor="start"))

    f.append(tb(620, 524,
                "перші 10 м зльоту й останні 10 м посадки з перевірки вилучено —\n"
                "інакше кожен план світився б двома зіткненнями",
                size=11, pad=9))

    render(os.path.join(IMG, "segment-collision.svg"), W, H, *f,
           title="Зіткнення шукають по всій хорді відрізка, а не по його кінцях")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Три проходи над обривом: насичення → швидкості → допуск
# ─────────────────────────────────────────────────────────────────────────────
def polyfill(pts, fill, opacity=1.0):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="none"/>'
            % (p, fill, opacity))


def fig_three_passes():
    W, H = 1240, 1140
    X0, XS, AS = 120.0, 2.0, 0.9

    def xx(d):
        return X0 + XS * d

    D = [30.0 * i for i in range(17)]        # 0 … 480 м уздовж галса
    TER = [0.0] * 6 + [100.0] * 11           # обрив між d = 150 і d = 180
    SURF = 40.0

    sat = [t + SURF for t in TER]
    rate = [40.0, 50.0, 68.0, 86.0, 104.0, 122.0] + [140.0] * 11
    keep = [0, 2, 3, 4, 5, 6, 16]

    panels = [
        (30, "Вихідний стан: галс — це дві точки",
             "пряма між ними йде крізь верхівку обриву: запас над землею падає з 40 м до нуля"),
        (295, "Прохід 1 — насичення: точка на кожен відлік профілю, крок 30 м",
              "17 точок; увесь ступінь у 100 м припадає на один відрізок завдовжки 30 м"),
        (560, "Прохід 2 — обмеження вертикальних швидкостей",
              "3 м/с набору при 5 м/с шляхової дають 18 м на відрізок: ступінь розтягується в похилу"),
        (825, "Прохід 3 — прорідження за допуском 10 м: із 17 точок лишається 7",
              "рівне плато згортається в кінці галса, похила лишається цілою"),
    ]

    f = []
    for panelIndex, (top, title, note) in enumerate(panels):
        base = top + 215

        def yy(alt):
            return base - AS * alt

        f.append(text(56, top + 20, title, size=14, bold=True, anchor="start"))
        f.append(text(56, top + 46, note, size=12, color=MUTED, anchor="start"))

        # рельєф
        ter_pts = [(xx(0), yy(0)), (xx(150), yy(0)),
                   (xx(180), yy(100)), (xx(480), yy(100))]
        f.append(polyfill(ter_pts + [(xx(480), base + 22), (xx(0), base + 22)],
                          "#c9ced4", 1.0))
        f.append(polyline(ter_pts, color=INK, sw=2.2))

        if panelIndex == 0:
            pts = [(xx(0), yy(40)), (xx(480), yy(140))]
            f.append(polyline(pts, color=POS, sw=2.8))
            for x, y in pts:
                f.append(circle(x, y, 8, fill="#ffffff", stroke=INK, sw=2.2))
            f.append(circle(xx(180), yy(100), 7, fill="#fdecea", stroke=POS, sw=2.4))
            f.append(text(xx(180) + 18, yy(100) - 16, "тут шлях сідає на землю",
                          size=12, color=POS, anchor="start"))
        else:
            alts = sat if panelIndex == 1 else rate
            if panelIndex < 3:
                f.append(polyline([(xx(d), yy(a)) for d, a in zip(D, alts)],
                                  color=FIELD, sw=2.6))
                for i, (d, a) in enumerate(zip(D, alts)):
                    if i in (0, 16):
                        f.append(circle(xx(d), yy(a), 8, fill="#ffffff", stroke=INK, sw=2.2))
                    else:
                        f.append(circle(xx(d), yy(a), 5, fill=FIELD, stroke=FIELD, sw=1.2))
            else:
                for i, (d, a) in enumerate(zip(D, rate)):
                    if i not in keep:
                        f.append(circle(xx(d), yy(a), 4.5, fill="#ffffff", stroke="#b6bcc4", sw=1.6))
                f.append(polyline([(xx(D[i]), yy(rate[i])) for i in keep],
                                  color=FIELD, sw=2.6))
                for i in keep:
                    if i in (0, 16):
                        f.append(circle(xx(D[i]), yy(rate[i]), 8, fill="#ffffff", stroke=INK, sw=2.2))
                    else:
                        f.append(circle(xx(D[i]), yy(rate[i]), 5, fill=FIELD, stroke=FIELD, sw=1.2))

        if panelIndex == 1:
            f.append(text(xx(190), base - 142, "ступінь у 100 м на 30 м шляху",
                          size=12, color=FIELD, anchor="start"))
        if panelIndex == 2:
            f.append(text(xx(5), base - 142, "правка повзе вліво, від обриву до початку галса",
                          size=12, color=FIELD, anchor="start"))
        if panelIndex == 3:
            f.append(text(xx(65), base - 30, "світлі кружки — викинуті точки", size=12,
                          color=MUTED, anchor="start"))

    # шкала відстані під нижньою панеллю
    yaxis = panels[3][0] + 215 + 40
    f.append(line(xx(0), yaxis, xx(480), yaxis, color=MUTED, sw=1.4))
    for d in (0, 150, 300, 480):
        f.append(line(xx(d), yaxis - 5, xx(d), yaxis + 5, color=MUTED, sw=1.4))
        f.append(text(xx(d), yaxis + 24, "%d" % d, size=12, color=MUTED))
    f.append(text(xx(480) + 30, yaxis + 24, "м уздовж галса", size=12,
                 color=MUTED, anchor="start"))

    render(os.path.join(IMG, "three-passes.svg"), W, H, *f,
           title="Той самий галс над обривом після кожного з трьох проходів")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Набір і зниження правляться в різні боки — тому й проходів різна кількість
# ─────────────────────────────────────────────────────────────────────────────
def fig_rate_propagation():
    W, H = 1240, 620
    XS = [180, 300, 420, 540, 660, 780, 900]
    f = []

    # ── верхній ряд: набір висоти
    b1 = 250
    f.append(text(56, 74, "Набір: правило піднімає ПОПЕРЕДНЮ точку пари",
                  size=15, bold=True, anchor="start"))
    alts1 = [b1, b1, b1, b1, b1, b1, b1 - 96]
    f.append(polyline(list(zip(XS, alts1)), color=FIELD, sw=2.4))
    for x, y in zip(XS, alts1):
        f.append(circle(x, y, 6, fill=FIELD, stroke=FIELD, sw=1.2))
    for k, i in enumerate((5, 4, 3)):
        f.append(arrow(XS[i], b1 - 8, XS[i], b1 - 52 + k * 10, color=POS))
        f.append(text(XS[i], b1 - 62 + k * 10, "%d-й прохід" % (k + 1),
                      size=12, color=POS))
    f.append(arrow(940, 122, 480, 122, color=MUTED))
    f.append(text(710, 110, "правка повзе назад, назустріч обходу",
                  size=12, color=MUTED))
    f.append(arrow(150, 300, 940, 300, color=MUTED))
    f.append(text(545, 324, "обхід масиву: i = 0 … n−2", size=12, color=MUTED))
    f.append(tb(1090, 216,
                "за один прохід\nвиправляється\nодна пара:\nпроходів стільки,\nскільки точок\nу похилій",
                size=12, pad=9))

    # ── нижній ряд: зниження
    b2 = 520
    f.append(text(56, 380, "Зниження: правило піднімає НАСТУПНУ точку пари",
                  size=15, bold=True, anchor="start"))
    alts2 = [b2 - 96, b2, b2, b2, b2, b2, b2]
    f.append(polyline(list(zip(XS, alts2)), color=FIELD, sw=2.4))
    for x, y in zip(XS, alts2):
        f.append(circle(x, y, 6, fill=FIELD, stroke=FIELD, sw=1.2))
    for i in (1, 2, 3):
        f.append(arrow(XS[i], b2 - 8, XS[i], b2 - 44, color=POS))
    f.append(text(420, b2 - 58, "усе за один прохід", size=12, color=POS))
    f.append(arrow(240, 428, 940, 428, color=MUTED))
    f.append(text(590, 416, "правка біжить уперед, разом з обходом",
                  size=12, color=MUTED))
    f.append(arrow(150, 570, 940, 570, color=MUTED))
    f.append(text(545, 594, "обхід масиву: i = 0 … n−2", size=12, color=MUTED))
    f.append(tb(1090, 486,
                "виправлена точка —\nта, до якої обхід\nще не дійшов:\nдругий прохід лише\nпідтверджує,\nщо правок немає",
                size=12, pad=9))

    render(os.path.join(IMG, "rate-propagation.svg"), W, H, *f,
           title="Обхід іде вперед, а правка набору — назад: звідси різна кількість проходів")


# ─────────────────────────────────────────────────────────────────────────────
# Стек класів запиту рельєфу (до вставки api-terrain-query.md)
# ─────────────────────────────────────────────────────────────────────────────
def fig_terrain_api_stack():
    W, H = 1320, 840
    f = []

    f.append(text(660, 74,
                  "ваш код створює один із цих об'єктів, підписується на terrainDataReceived і чекає",
                  size=13, color=MUTED))

    # ── ряд 1: чотири публічні класи запиту ──────────────────────────────
    row1 = [
        (190,  "TerrainAtCoordinateQuery\n→ QList<double> heights"),
        (520,  "TerrainPathQuery\n→ PathHeightInfo_t"),
        (850,  "TerrainPolyPathQuery\n→ QList<PathHeightInfo_t>"),
        (1160, "TerrainAreaQuery\n→ CarpetHeightInfo_t"),
    ]
    for cx, label in row1:
        f.append(tb(cx, 130, label, size=13, pad=10))

    # ламана віддає роботу відрізковому запитові — той самий ряд
    f.append(text(674, 122, "один відрізок за раз", size=11, color=MUTED))
    f.append(arrow(747, 142, 601, 142, color=MUTED, sw=1.6))

    # ── ряд 2: батчер під точковим запитом ───────────────────────────────
    f.append(arrow(190, 156, 190, 224))
    f.append(tb(190, 250,
                "TerrainAtCoordinateBatchManager\nтаймер 500 мс · межа 50 координат",
                size=13, pad=10))

    # ── спільна шина до шару плиток ──────────────────────────────────────
    f.append(line(190, 276, 190, 345, color=LINE, sw=1.8))
    f.append(line(520, 156, 520, 345, color=LINE, sw=1.8))
    f.append(line(1160, 156, 1160, 345, color=LINE, sw=1.8))
    f.append(line(190, 345, 1160, 345, color=LINE, sw=1.8))
    f.append(arrow(660, 345, 660, 366))

    # ── ряд 3: спільний вхід у шар плиток ────────────────────────────────
    f.append(tb(660, 392, "TerrainOfflineQuery\n(TerrainQueryInterface)",
                size=13, pad=10, min_w=430))

    # ── ряд 4: менеджер плиток ───────────────────────────────────────────
    f.append(arrow(660, 418, 660, 486))
    f.append(tb(660, 512, "TerrainTileManager\nодне звантаження за раз",
                size=13, pad=10, min_w=360))

    # ── ряд 5: кеш або мережа ────────────────────────────────────────────
    f.append(arrow(580, 540, 410, 616, color=FIELD, sw=1.8))
    f.append(arrow(740, 540, 910, 616, color=POS, sw=1.8))
    f.append(text(462, 566, "влучання", size=11, color=FIELD, anchor="end"))
    f.append(text(858, 564, "промах", size=11, color=POS, anchor="start"))

    f.append(tb(360, 642, "кеш плиток _tiles\nвідповідь без мережі",
                size=12, pad=10, stroke=FIELD))
    f.append(tb(960, 642, "GET /api/v1/carpet?points=…\nплитка 0.01° × 0.01°",
                size=12, pad=10))

    f.append(text(360, 702, "запит закривається негайно", size=11, color=MUTED))

    # ── ряд 6: невдала плитка ────────────────────────────────────────────
    f.append(arrow(960, 670, 960, 736, color=POS, sw=1.8))
    f.append(tb(960, 764, "невдала плитка → _failedTiles\nмовчання 5000 мс",
                size=12, pad=10, stroke=POS, color=POS))

    render(os.path.join(IMG, "terrain-api-stack.svg"), W, H, *f,
           title="Хто кого викликає: від об'єкта запиту до плитки на сервері")


if __name__ == "__main__":
    fig_altitude_modes()
    fig_terrain_query()
    fig_who_computes()
    fig_segment_collision()
    fig_three_passes()
    fig_rate_propagation()
    fig_terrain_api_stack()
    print("ok")
