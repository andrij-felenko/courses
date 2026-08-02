# -*- coding: utf-8 -*-
"""Фігури до теми «Модель плану: місія, геозона, точки збору»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def tb(cx, cy, s, **kw):
    return textbox(cx, cy, s, **kw)[0]


# ─────────────────────────────────────────────────────────────────────────────
# 1. Три списки: один протокол, три різні читачі
# ─────────────────────────────────────────────────────────────────────────────
def fig_three_lists():
    W, H = 1220, 680
    f = []

    f.append(tb(W / 2, 92,
                "один протокол місій, один канал:\n"
                "MISSION_COUNT · MISSION_REQUEST_INT · MISSION_ITEM_INT · MISSION_ACK",
                size=14, fill="#fffbea", stroke="#b8860b", bold=True))

    cols = [
        (50, "Маршрут", "тип місії 0", "#eef4fb", NEG, [
            "«зроби це, потім те»",
            "",
            "читає навігатор",
            "послідовно, крок за кроком",
            "порядок = сам зміст",
            "",
            "живе один політ",
        ]),
        (440, "Геозона", "тип місії 1", "#eef6ef", FIELD, [
            "«сюди ніколи не заходь»",
            "",
            "читає сторож безпеки",
            "щоцикла, десятки разів",
            "порядок нічого не значить",
            "",
            "живе тижнями",
        ]),
        (830, "Точки збору", "тип місії 2", "#fbf1ee", POS, [
            "«якщо біда — сюди»",
            "",
            "читає логіка відмови",
            "один раз, у мить рішення",
            "точки рівноправні",
            "",
            "живе місяцями",
        ]),
    ]

    pw, py, ph = 340, 210, 340
    for px, title, kind, fill, stroke, items in cols:
        cx = px + pw / 2
        f.append(arrow(cx, 132, cx, py - 8))
        f.append(rect(px, py, pw, ph, fill=fill, stroke=stroke, sw=2.0, rx=10))
        f.append(text(cx, py + 36, title, size=17, bold=True, color=stroke))
        f.append(text(cx, py + 62, kind, size=13, color=MUTED))
        y = py + 106
        for it in items:
            if it:
                fs = fit_font(it, pw - 30, 14)
                f.append(text(cx, y, it, size=fs, color=INK))
            y += 32

    f.append(tb(W / 2, 616,
                "Списки незалежні: заміна маршруту не чіпає геозони,\n"
                "а стирання геозони не чіпає точок збору",
                size=14, fill=FILL, stroke=MUTED))

    render(os.path.join(IMG, 'three-lists.svg'), W, H, *f,
           title="Три списки на борту, розрізнені одним байтом типу")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Три вертикальні дороги від редактора до борту
# ─────────────────────────────────────────────────────────────────────────────
def fig_plan_layers():
    W, H = 1220, 760
    f = []

    mx, mw = 150, 920
    f.append(rect(mx, 66, mw, 66, fill="#fffbea", stroke="#b8860b", sw=2.0, rx=10))
    f.append(text(W / 2, 100, "PlanMasterController — файл .plan · прапорці змін · порядок обміну",
                  size=15, bold=True))

    cols = [
        (50, "#eef4fb", NEG,
         "MissionController\n\nvisualItems: шапка плану,\nточки, складені елементи",
         "MissionManager\nPlanManager, тип 0",
         "список команд маршруту"),
        (440, "#eef6ef", FIELD,
         "GeoFenceController\n\nполігони · кола\nточка повернення",
         "GeoFenceManager\nPlanManager, тип 1",
         "вершини, кола, точка повернення"),
        (830, "#fbf1ee", POS,
         "RallyPointController\n\nперелік точок\nз висотами",
         "RallyPointManager\nPlanManager, тип 2",
         "точки збору"),
    ]

    pw = 340
    y1, h1 = 220, 150
    y2, h2 = 430, 90
    y3, h3 = 600, 76

    f.append(text(60, y1 - 24, "у редакторі", size=13, color=MUTED, anchor="start", bold=True))
    f.append(text(60, y2 - 18, "у Vehicle", size=13, color=MUTED, anchor="start", bold=True))
    f.append(text(60, y3 - 18, "на борту", size=13, color=MUTED, anchor="start", bold=True))

    for px, fill, stroke, top, mid, bot in cols:
        cx = px + pw / 2
        f.append(arrow(cx, 138, cx, y1 - 8))
        f.append(fitbox(px, y1, pw, h1, top, size=14, fill=fill, stroke=stroke, sw=2.0))
        f.append(fitbox(px, y2, pw, h2, mid, size=14, fill=FILL, stroke=stroke, sw=1.8))
        f.append(fitbox(px, y3, pw, h3, bot, size=14, fill="#ffffff", stroke=MUTED, sw=1.8))
        f.append(arrow(cx - 30, y1 + h1 + 6, cx - 30, y2 - 6))
        f.append(arrow(cx + 30, y2 - 6, cx + 30, y1 + h1 + 6))
        f.append(arrow(cx - 30, y2 + h2 + 6, cx - 30, y3 - 6))
        f.append(arrow(cx + 30, y3 - 6, cx + 30, y2 + h2 + 6))

    f.append(text(W / 2, 716,
                  "Три розмови не можна вести водночас: спершу маршрут, потім геозона, потім точки збору",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'plan-layers.svg'), W, H, *f,
           title="Від моделі редактора до списку на борту")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Видимі елементи проти команд на борту
# ─────────────────────────────────────────────────────────────────────────────
def fig_visual_vs_mission():
    W, H = 1180, 720
    f = []

    lx, lw = 70, 400
    rx, rw = 690, 420

    f.append(text(lx + lw / 2, 78, "модель редактора — 4 видимі елементи",
                  size=15, bold=True, color=NEG))
    f.append(text(rx + rw / 2, 78, "борт — 21 команда підряд",
                  size=15, bold=True, color=POS))

    rows = [
        (120, 70, 120, 60, "шапка плану\nMissionSettingsItem", "0 — домашня точка"),
        (214, 70, 202, 60, "зліт", "1 — зліт"),
        (308, 170, 284, 190, "зйомка полігону\nComplexMissionItem\nодна фігура на карті",
         "2 … 19\n18 команд галсів"),
        (512, 70, 498, 60, "посадка", "20 — посадка"),
    ]

    for ly, lh, ry, rh, ltext, rtext in rows:
        f.append(fitbox(lx, ly, lw, lh, ltext, size=14, fill="#eef4fb", stroke=NEG, sw=1.8))
        f.append(fitbox(rx, ry, rw, rh, rtext, size=14, fill="#fbf1ee", stroke=POS, sw=1.8))
        f.append(arrow(lx + lw + 10, ly + lh / 2, rx - 10, ry + rh / 2, color=MUTED))

    f.append(tb(W / 2, 640,
                "Вставити одну точку після зльоту — і номери 2…20 зсуваються на одиницю.\n"
                "Тому перехід DO_JUMP посилається не на номер, а на сталий doJumpId елемента.",
                size=14, fill="#fffbea", stroke="#b8860b"))

    render(os.path.join(IMG, 'visual-vs-mission.svg'), W, H, *f,
           title="Що бачить користувач і що дістає апарат")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Три копії плану й дві позначки змін
# ─────────────────────────────────────────────────────────────────────────────
def fig_plan_copies():
    W, H = 1180, 600
    f = []

    f.append(fitbox(410, 90, 360, 90, "модель редактора\nте, що зараз на екрані",
                    size=15, fill="#fffbea", stroke="#b8860b", sw=2.0))
    f.append(fitbox(70, 350, 340, 90, "файл .plan\nна диску",
                    size=15, fill="#eef4fb", stroke=NEG, sw=2.0))
    f.append(fitbox(770, 350, 340, 90, "пам'ять апарата\nтри списки",
                    size=15, fill="#fbf1ee", stroke=POS, sw=2.0))

    f.append(arrow(470, 186, 290, 344, color=NEG))
    f.append(arrow(250, 344, 430, 186, color=NEG))
    f.append(arrow(710, 186, 890, 344, color=POS))
    f.append(arrow(930, 344, 750, 186, color=POS))

    f.append(tb(148, 234, "dirtyForSave\nмодель ≠ файл", size=14,
                fill="#eef4fb", stroke=NEG, bold=True))
    f.append(tb(1032, 234, "dirtyForUpload\nмодель ≠ борт", size=14,
                fill="#fbf1ee", stroke=POS, bold=True))

    f.append(line(414, 395, 766, 395, color=MUTED, sw=2.0, dash="8,7"))
    f.append(tb(W / 2, 500,
                "Файл із бортом порівняти нема як: щоб дізнатися вміст борту,\n"
                "його треба прочитати, а читання затирає модель редактора.\n"
                "Тому обидві позначки міряють розбіжність від моделі.",
                size=14, fill=FILL, stroke=MUTED))

    render(os.path.join(IMG, 'plan-copies.svg'), W, H, *f,
           title="Три копії плану й дві позначки змін")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Карта ключів файлу .plan і чотири незалежні версії (до вставки api-plan-file)
# ─────────────────────────────────────────────────────────────────────────────
def fig_plan_file_keys():
    W, H = 1260, 900
    f = []

    # оболонка файлу
    f.append(rect(40, 58, 1180, 700, fill="#fffdf5", stroke="#b8860b", sw=2.2, rx=12))
    f.append(text(62, 86, "оболонка файлу — PlanMasterController", size=14,
                  color="#8a6d1f", anchor="start", bold=True))
    f.append(tb(630, 132,
                '"fileType": "Plan"      "version": 1      "groundStation": "QGroundControl"',
                size=15, fill="#fffbea", stroke="#b8860b", bold=True))
    f.append(text(630, 176, "версія оболонки відповідає лише за те, чи це взагалі план",
                  size=13, color=MUTED))

    cols = [
        (70, "#eef4fb", NEG, '"mission"',
         'власна версія: 2\nвласник: MissionController',
         'firmwareType · vehicleType\ncruiseSpeed · hoverSpeed\nglobalPlanAltitudeMode\nplannedHomePosition\nitems[ ]',
         'будь-яка інша версія —\nпомилка «Mission: …»,\nувесь план не читається'),
        (470, "#eef6ef", FIELD, '"geoFence"',
         'власна версія: 2\nвласник: GeoFenceController',
         'polygons[ ]\ncircles[ ]\nbreachReturn\n(лише коли її задано)',
         'версія 1 і давніші —\nтихо пропущено:\nплан без геозони'),
        (870, "#fbf1ee", POS, '"rallyPoints"',
         'власна версія: 2\nвласник: RallyPointController',
         'points[ ]\n[широта, довгота, висота]',
         'версія 1 —\nтихо пропущено:\nплан без точок збору'),
    ]

    pw = 320
    yh, hh = 212, 58
    yo, ho = 292, 62
    yk, hk = 384, 168
    yv, hv = 580, 106

    f.append(text(70, yk - 14, "ключі об'єкта", size=12, color=MUTED, anchor="start"))
    f.append(text(70, yv - 14, "коли номер версії не той, якого чекає читач",
                  size=12, color=MUTED, anchor="start"))

    for px, fill, stroke, key, owner, keys, mismatch in cols:
        cx = px + pw / 2
        f.append(arrow(cx, 192, cx, yh - 8))
        f.append(fitbox(px, yh, pw, hh, key, size=19, fill=fill, stroke=stroke, sw=2.4, bold=True))
        f.append(fitbox(px, yo, pw, ho, owner, size=13, fill="#ffffff", stroke=stroke, sw=1.6))
        f.append(fitbox(px, yk, pw, hk, keys, size=14, fill=fill, stroke=stroke, sw=1.8))
        f.append(fitbox(px, yv, pw, hv, mismatch, size=13, fill="#ffffff", stroke=MUTED, sw=1.6))

    f.append(tb(630, 820,
                "Незнайомого ключа читач просто не помічає: перевіряються наявність і тип\n"
                "лише тих ключів, які він сам шукає. Чуже поле у файлі нічого не ламає.",
                size=14, fill=FILL, stroke=MUTED))

    render(os.path.join(IMG, 'plan-file-keys.svg'), W, H, *f,
           title="Файл .plan: одна оболонка, три об'єкти, чотири незалежні версії")


# ─────────────────────────────────────────────────────────────────────────────
# 6. З файлу в плаский список (до вставки proj-plan-json-roundtrip)
# ─────────────────────────────────────────────────────────────────────────────
def fig_flatten_pipeline():
    W, H = 1300, 810
    f = []

    lx, lw = 60, 470
    rx, rw = 700, 400

    f.append(text(lx + lw / 2, 60, "що лежить у файлі .plan", size=16, bold=True, color=NEG))
    f.append(text(rx + rw / 2, 60, "що дістає борт", size=16, bold=True, color=POS))

    row_h, gap, top = 50, 8, 100

    def row_y(n):
        return top + n * (row_h + gap)

    wire = [
        "0   NAV_WAYPOINT   ← дім",
        "1   NAV_TAKEOFF",
        "2   NAV_WAYPOINT",
        "3   NAV_WAYPOINT",
        "4   DO_SET_CAM_TRIGG_DIST",
        "5   NAV_WAYPOINT",
        "6   DO_SET_CAM_TRIGG_DIST",
        "7   NAV_WAYPOINT",
        "8   DO_JUMP   param1 = 2",
        "9   NAV_RETURN_TO_LAUNCH",
    ]
    for n, label in enumerate(wire):
        y = row_y(n)
        f.append(rect(rx, y, rw, row_h, fill="#fdf0d5" if n == 0 else "#fbf1ee",
                      stroke=POS, sw=1.6, rx=6))
        f.append(text(rx + 18, y + row_h / 2 + 5, label, size=13, anchor="start"))

    left = [
        (0, 1, "plannedHomePosition\n[50.4501, 30.5234, 179]", "#fdf0d5", "#b8860b"),
        (1, 1, "SimpleItem · NAV_TAKEOFF · doJumpId 1", "#eef4fb", NEG),
        (2, 1, "SimpleItem · NAV_WAYPOINT · doJumpId 2", "#eef4fb", NEG),
        (3, 4, "ComplexItem «survey»\nTransectStyleComplexItem → Items: 4 команди",
         "#eef6ef", FIELD),
        (7, 1, "SimpleItem · NAV_WAYPOINT · doJumpId 7", "#eef4fb", NEG),
        (8, 1, "SimpleItem · DO_JUMP · param1 = 2 · doJumpId 8", "#eef4fb", NEG),
        (9, 1, "SimpleItem · RETURN_TO_LAUNCH · doJumpId 9", "#eef4fb", NEG),
    ]
    for n, span, label, fill, stroke in left:
        y = row_y(n)
        h = span * row_h + (span - 1) * gap
        f.append(fitbox(lx, y, lw, h, label, size=13, fill=fill, stroke=stroke, sw=1.6))
        f.append(arrow(lx + lw + 8, y + h / 2, rx - 10, y + h / 2, color=MUTED, sw=1.4))

    jx = rx + rw + 46
    y8 = row_y(8) + row_h / 2
    y2 = row_y(2) + row_h / 2
    f.append(line(rx + rw + 2, y8, jx, y8, color=POS, sw=2.0))
    f.append(line(jx, y8, jx, y2, color=POS, sw=2.0))
    f.append(arrow(jx, y2, rx + rw + 2, y2, color=POS, sw=2.0))
    f.append(text(jx + 18, (y8 + y2) / 2 - 10, "doJumpId 2", size=12, color=POS, anchor="start"))
    f.append(text(jx + 18, (y8 + y2) / 2 + 14, "став номером 2", size=12, color=POS, anchor="start"))

    f.append(tb(W / 2, 742,
                "Три дії поспіль: домашня точка стає нульовим елементом · складений елемент розгортається у свої команди ·\n"
                "номери роздаються з позиції — і аж тоді в переходах doJumpId міняється на справжній номер",
                size=13, fill=FILL, stroke=MUTED))

    render(os.path.join(IMG, 'proj-flatten-pipeline.svg'), W, H, *f,
           title="Від файлу плану до плаского списку елементів місії")


# ─────────────────────────────────────────────────────────────────────────────
# 7. Полігон геозони тримається на лічильнику (до вставки proj-plan-json-roundtrip)
# ─────────────────────────────────────────────────────────────────────────────
def fig_fence_regroup():
    W, H = 1240, 700
    f = []

    bw, bg, x0 = 204, 18, 60

    def stream(y, items):
        for n, (label, is_vertex) in enumerate(items):
            x = x0 + n * (bw + bg)
            f.append(fitbox(x, y, bw, 78, label, size=12,
                            fill="#eef6ef" if is_vertex else "#fbf1ee",
                            stroke=FIELD if is_vertex else POS, sw=1.6))
        return x0 + len(items) * (bw + bg) - bg

    vertex = lambda lat, lon: ("5001\nparam1 = 4\n%s   %s" % (lat, lon), True)
    circle = ("5004\nparam1 = 35\n50.4508   30.5262", False)

    f.append(text(x0, 50, "потік, який іде по радіо: слова «полігон» у ньому немає",
                  size=14, bold=True, anchor="start"))

    right = stream(74, [vertex("50.4530", "30.5220"), vertex("50.4530", "30.5310"),
                        vertex("50.4480", "30.5310"), vertex("50.4480", "30.5220"), circle])

    brace_r = x0 + 4 * bw + 3 * bg
    f.append(line(x0, 172, brace_r, 172, color=FIELD, sw=2.0))
    f.append(line(x0, 172, x0, 162, color=FIELD, sw=2.0))
    f.append(line(brace_r, 172, brace_r, 162, color=FIELD, sw=2.0))
    f.append(text((x0 + brace_r) / 2, 198,
                  "лічильник у param1 сказав «нас чотири» — набираємо рівно чотири", size=13, color=FIELD))

    f.append(fitbox(x0, 218, brace_r - x0, 58, "включний полігон, 4 вершини",
                    size=14, fill="#eef6ef", stroke=FIELD, sw=1.8))
    f.append(fitbox(brace_r + bg, 218, bw, 58, "виключне коло, радіус 35 м",
                    size=12, fill="#fbf1ee", stroke=POS, sw=1.8))

    f.append(line(x0, 320, right, 320, color=MUTED, sw=1.2, dash="7,7"))

    f.append(text(x0, 362, "той самий потік, у якому загубився один елемент",
                  size=14, bold=True, anchor="start"))
    stream(386, [vertex("50.4530", "30.5220"), vertex("50.4530", "30.5310"),
                 vertex("50.4480", "30.5310"), circle])

    f.append(fitbox(x0, 500, brace_r - x0, 66,
                    "полігона немає взагалі: набралося три вершини з чотирьох,\n"
                    "а далі пішла команда іншого ґатунку",
                    size=13, fill="#fff0f0", stroke=POS, sw=1.8))
    f.append(fitbox(brace_r + bg, 500, bw, 66, "коло вціліло\nй ляже на карту",
                    size=12, fill="#fbf1ee", stroke=POS, sw=1.8))

    f.append(text(W / 2, 622,
                  "Утрата одного елемента з п'яти нищить фігуру цілком — і мовчки, якщо список на цьому й скінчився",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'proj-fence-regroup.svg'), W, H, *f,
           title="Полігон геозони тримається лише на порядку й лічильнику вершин")


if __name__ == '__main__':
    fig_three_lists()
    fig_plan_layers()
    fig_visual_vs_mission()
    fig_plan_copies()
    fig_plan_file_keys()
    fig_flatten_pipeline()
    fig_fence_regroup()
    print("ok")
