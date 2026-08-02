# -*- coding: utf-8 -*-
"""Фігури до теми «Елементи місії й команди» (reference/qgroundcontrol/planning)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def out(name):
    return os.path.join(IMG, name)


# ────────────────────────────────────────────────────────────────────────────
# 1. Три обличчя одного елемента
# ────────────────────────────────────────────────────────────────────────────
def three_faces():
    W, H = 1240, 620
    f = []

    colw = 340
    gap = 80
    x0 = 50
    cols = [
        (x0,                     "Рядок редактора",  "#eef6ff"),
        (x0 + colw + gap,        "Об'єкт у файлі .plan", "#f2f7ee"),
        (x0 + 2 * (colw + gap),  "Запис у ефірі",    "#fff4ec"),
    ]

    top = 70
    for cx, title, tint in cols:
        f.append(text(cx + colw / 2, top - 18, title, size=17, bold=True))

    # ── колонка 1: рядок редактора
    x, y = cols[0][0], top
    f.append(rect(x, y, colw, 300, fill="#eef6ff", stroke=NEG, sw=2))
    f.append(text(x + 18, y + 34, "Waypoint", size=16, bold=True, anchor="start"))
    rows1 = [
        ("Altitude", "50 m"),
        ("Altitude mode", "над зльотом"),
        ("Hold", "0 s"),
        ("Acceptance", "0 m"),
        ("Yaw", "не змінювати"),
        ("Камера", "знімок кожні 20 м"),
    ]
    ry = y + 66
    for k, v in rows1:
        f.append(text(x + 18, ry, k, size=13, color=MUTED, anchor="start"))
        f.append(text(x + colw - 18, ry, v, size=13, anchor="end"))
        ry += 30
    f.append(text(x + colw / 2, y + 300 + 34,
                  "+ рельєф під точкою, dirty,", size=12, color=MUTED))
    f.append(text(x + colw / 2, y + 300 + 52,
                  "виділення в списку", size=12, color=MUTED))

    # ── колонка 2: файл плану
    x, y = cols[1][0], top
    f.append(rect(x, y, colw, 300, fill="#f2f7ee", stroke=FIELD, sw=2))
    json_lines = [
        '"type": "SimpleItem",',
        '"command": 16,',
        '"frame": 3,',
        '"AltitudeMode": 1,',
        '"Altitude": 50,',
        '"doJumpId": 4,',
        '"params": [0, 0, 0, null,',
        '            47.3977419,',
        '            8.5455938, 50]',
    ]
    jy = y + 36
    for ln in json_lines:
        f.append(text(x + 18, jy, ln, size=13, anchor="start"))
        jy += 29
    f.append(text(x + colw / 2, y + 300 + 34,
                  "зберігає ім'я елемента", size=12, color=MUTED))
    f.append(text(x + colw / 2, y + 300 + 52,
                  "й режим висоти", size=12, color=MUTED))

    # ── колонка 3: ефір
    x, y = cols[2][0], top
    f.append(rect(x, y, colw, 300, fill="#fff4ec", stroke=POS, sw=2))
    wire = [
        ("seq", "4"),
        ("command", "16"),
        ("frame", "3"),
        ("autocontinue", "1"),
        ("param1..4", "0 0 0 NaN"),
        ("x  (шир.·10⁷)", "473977419"),
        ("y  (довг.·10⁷)", "85455938"),
        ("z", "50.0"),
    ]
    wy = y + 36
    for k, v in wire:
        f.append(text(x + 18, wy, k, size=13, color=MUTED, anchor="start"))
        f.append(text(x + colw - 18, wy, v, size=13, anchor="end"))
        wy += 29
    f.append(text(x + colw / 2, y + 300 + 34,
                  "жодних назв полів", size=12, color=MUTED))
    f.append(text(x + colw / 2, y + 300 + 52,
                  "поза номером команди", size=12, color=MUTED))

    # ── стрілки між колонками
    ay = top + 150
    f.append(arrow(cols[0][0] + colw + 12, ay, cols[1][0] - 12, ay))
    f.append(arrow(cols[1][0] + colw + 12, ay, cols[2][0] - 12, ay))
    f.append(text(cols[0][0] + colw + gap / 2, ay - 22, "збереження", size=12, color=MUTED))
    f.append(text(cols[1][0] + colw + gap / 2, ay - 22, "вивантаження", size=12, color=MUTED))

    # ── нижній рядок: що втрачається
    ly = 520
    f.append(line(x0, ly - 26, W - x0, ly - 26, color=MUTED, sw=1, dash="4,4"))
    f.append(text(cols[0][0] + colw + gap / 2, ly + 6,
                  "втрачається обчислюване", size=13, color=MUTED))
    f.append(text(cols[1][0] + colw + gap / 2, ly + 6,
                  "втрачається структура", size=13, color=MUTED))
    f.append(text(W / 2, ly + 44,
                  "назад із ефіру відновлюється лише те, що впізнається за зразком",
                  size=13, color=POS))

    render(out('three-faces.svg'), W, H, *f)


# ────────────────────────────────────────────────────────────────────────────
# 2. Шари словника команд
# ────────────────────────────────────────────────────────────────────────────
def command_layers():
    W, H = 1180, 620
    f = []

    lw, lh = 470, 62
    lx = 60
    layers = [
        ("Спільний: будь-яка прошивка, будь-який апарат", "MavCmdInfoCommon.json", "#f4f6f8"),
        ("Тип апарата: мультиротор / літак / VTOL / ровер", "MavCmdInfoMultiRotor.json", "#eef6ff"),
        ("Прошивка: PX4 або ArduPilot", "накладка плагіна прошивки", "#f2f7ee"),
        ("Прошивка + тип апарата разом", "найконкретніша накладка", "#fff4ec"),
    ]
    ly = 80
    f.append(text(lx + lw / 2, 50, "шари опису, від загального до конкретного", size=15, bold=True))
    for i, (title, sub, tint) in enumerate(layers):
        yy = ly + i * (lh + 34)
        f.append(rect(lx, yy, lw, lh, fill=tint, stroke=LINE, sw=1.5))
        f.append(text(lx + 16, yy + 26, title, size=13, bold=True, anchor="start"))
        f.append(text(lx + 16, yy + 46, sub, size=12, color=MUTED, anchor="start"))
        if i < len(layers) - 1:
            f.append(arrow(lx + lw / 2, yy + lh + 6, lx + lw / 2, yy + lh + 28))

    # права частина: зібраний опис
    rx, ry = 690, 120
    rw, rh = 420, 300
    f.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=NEG, sw=2.5))
    f.append(text(rx + rw / 2, ry + 30, "зібраний опис однієї команди", size=14, bold=True))
    keys = [
        ("friendlyName", "спільний шар"),
        ("category", "спільний шар"),
        ("specifiesCoordinate", "спільний шар"),
        ("param1.label", "спільний шар"),
        ("param3.label", "шар типу апарата"),
        ("param3.units", "шар типу апарата"),
        ("param2.enumStrings", "шар прошивки"),
    ]
    ky = ry + 62
    for k, src in keys:
        col = INK if src == "спільний шар" else (NEG if "типу" in src else FIELD)
        f.append(text(rx + 18, ky, k, size=13, anchor="start", color=col))
        f.append(text(rx + rw - 18, ky, src, size=12, anchor="end", color=MUTED))
        ky += 32

    f.append(arrow(lx + lw + 20, 250, rx - 20, 250))
    f.append(text((lx + lw + rx) / 2, 228, "накладання", size=13, color=MUTED))

    f.append(text(W / 2, 500,
                  "перекривається лише той ключ, який названо в шарі;",
                  size=14))
    f.append(text(W / 2, 526,
                  "решта дістається від попереднього шару без змін",
                  size=14))
    f.append(text(W / 2, 566,
                  "команда, якої немає в жодному шарі, редагується голими числами",
                  size=13, color=MUTED))

    render(out('command-layers.svg'), W, H, *f)


# ────────────────────────────────────────────────────────────────────────────
# 3. Рядки редактора → номери записів
# ────────────────────────────────────────────────────────────────────────────
def sequence_expand():
    W, H = 1160, 660
    f = []

    f.append(text(280, 50, "рядки в редакторі", size=16, bold=True))
    f.append(text(860, 50, "записи в місії", size=16, bold=True))

    rows = [
        ("Mission Settings", [], "#f4f6f8"),
        ("Takeoff", ["1  NAV_TAKEOFF"], "#eef6ff"),
        ("Waypoint", ["2  NAV_WAYPOINT"], "#eef6ff"),
        ("Waypoint\n+ знімок кожні 20 м\n+ швидкість 8 м/с",
         ["3  NAV_WAYPOINT",
          "4  DO_SET_CAM_TRIGG_DIST",
          "5  DO_CHANGE_SPEED"], "#fff4ec"),
        ("Return to launch", ["6  NAV_RETURN_TO_LAUNCH"], "#eef6ff"),
    ]

    left_x, left_w = 90, 380
    right_x, right_w = 660, 400
    y = 80
    right_y = 80
    item_h = 46
    gap = 16

    for label, items, tint in rows:
        nlines = label.count("\n") + 1
        box_h = max(item_h, len(items) * (item_h + 10) - 10 if items else item_h,
                    nlines * 24 + 22)
        f.append(fitbox(left_x, y, left_w, box_h, label, size=14, fill=tint))

        if not items:
            f.append(text(right_x + right_w / 2, right_y + 26,
                          "жодного запису", size=13, color=MUTED))
            f.append(line(left_x + left_w + 8, y + box_h / 2,
                          right_x - 8, right_y + 20, color=MUTED, sw=1.2, dash="4,4"))
            right_y += item_h + gap
        else:
            first_y = right_y
            for it in items:
                f.append(fitbox(right_x, right_y, right_w, item_h, it, size=13, fill="#ffffff"))
                right_y += item_h + 10
            f.append(arrow(left_x + left_w + 8, y + box_h / 2,
                           right_x - 8, first_y + (right_y - 10 - first_y) / 2))
            right_y += gap - 10

        y += box_h + gap

    base = max(y, right_y) + 30
    f.append(line(90, base, W - 90, base, color=MUTED, sw=1, dash="5,5"))
    f.append(text(W / 2, base + 34,
                  "5 рядків у редакторі  →  6 записів у місії,  останній номер = 6",
                  size=15, bold=True))
    f.append(text(W / 2, base + 62,
                  "«прямує до елемента 4» на екрані польоту — це не четвертий рядок плану",
                  size=13, color=POS))

    render(out('sequence-expand.svg'), W, H, *f)


# ────────────────────────────────────────────────────────────────────────────
# 4. Стрибок за номером і за іменем
# ────────────────────────────────────────────────────────────────────────────
def dojump_id():
    W, H = 1180, 560
    f = []

    cell_w, cell_h = 190, 52
    gapx = 26

    def strip(x, y, cells, hi=None):
        frags = []
        for i, c in enumerate(cells):
            cx = x + i * (cell_w + gapx)
            fill = "#fff4ec" if i == hi else FILL
            stroke = POS if i == hi else LINE
            frags.append(fitbox(cx, y, cell_w, cell_h, c, size=13, fill=fill, stroke=stroke))
        return frags

    # ── верх: до вставки
    f.append(text(W / 2, 46, "план до вставки нового елемента", size=15, bold=True))
    top_y = 66
    f += strip(70, top_y, ["1  Takeoff", "2  Waypoint", "3  Waypoint", "4  DO_JUMP → 2"], hi=1)
    f.append(text(W / 2, top_y + cell_h + 30,
                  "стрибок указує на номер 2 — і там справді потрібна точка", size=13, color=MUTED))

    f.append(line(70, 190, W - 70, 190, color=MUTED, sw=1, dash="5,5"))

    # ── низ ліворуч: збережено номером
    f.append(text(W / 2, 222, "після вставки елемента на початок", size=15, bold=True))

    mid_y = 250
    f.append(text(70, mid_y - 8, "стрибок збережено як номер:", size=13, anchor="start", color=POS))
    f += strip(70, mid_y + 6, ["1  Land pattern", "2  Takeoff", "3  Waypoint", "4  DO_JUMP → 2"], hi=1)
    f.append(text(W / 2, mid_y + cell_h + 36,
                  "номер 2 тепер належить зльоту — місія стрибає не туди",
                  size=13, color=POS))

    low_y = 400
    f.append(text(70, low_y - 8, "стрибок збережено як ім'я (doJumpId):", size=13,
                  anchor="start", color=FIELD))
    f += strip(70, low_y + 6,
               ["1  Land pattern", "2  Takeoff", "3  Waypoint\nім'я = 2", "4  DO_JUMP → ім'я 2"], hi=2)
    f.append(text(W / 2, low_y + cell_h + 42,
                  "при завантаженні ім'я 2 шукають серед елементів і підставляють його теперішній номер 3",
                  size=13, color=FIELD))

    render(out('dojump-id.svg'), W, H, *f)


# ────────────────────────────────────────────────────────────────────────────
# 5. Вставка proj: п'ять проходів збірки .plan → MISSION_ITEM_INT
# ────────────────────────────────────────────────────────────────────────────
def plan_pipeline():
    W, H = 1240, 730
    f = []

    f.append(text(W / 2, 50,
                  "від файлу .plan до списку MISSION_ITEM_INT: п'ять проходів",
                  size=17, bold=True))

    stages = [
        ("Читання й перевірка",
         "JSON → сирі записи; кожен пам'ятає своє ім'я doJumpId",
         "потребує: mission.items — і нічого більше"),
        ("Дім нульовим записом",
         "тільки якщо прошивка його чекає — інакше пропускаємо",
         "потребує: plannedHomePosition і відповідь плагіна прошивки"),
        ("Наскрізна перенумерація",
         "seq = позиція в остаточному масиві, рахуючи від нуля",
         "потребує: остаточний склад масиву — після рішення про дім"),
        ("Переадресація стрибків",
         "ім'я doJumpId → теперішній seq у цьому масиві",
         "потребує: готові номери — тільки після кроку 3"),
        ("Пакування в ефір",
         "градуси · 10⁷ → int32, крім MAV_FRAME_MISSION",
         "потребує: frame запису — він вирішує, чи це координата"),
    ]

    xl, wl, h = 60, 540, 78
    xr = 660
    y0, step = 96, 110
    tints = ["#eef6ff", "#f2f7ee", "#f4f6f8", "#fff4ec", "#eef6ff"]

    for i, (title, sub, need) in enumerate(stages):
        yy = y0 + i * step
        f.append(rect(xl, yy, wl, h, fill=tints[i], stroke=LINE, sw=1.5))
        f.append(circle(xl + 38, yy + h / 2, 21, fill="#ffffff", stroke=NEG, sw=2))
        f.append(text(xl + 38, yy + h / 2 + 6, str(i + 1), size=17, bold=True, color=NEG))
        f.append(text(xl + 76, yy + 32, title, size=15, bold=True, anchor="start"))
        f.append(text(xl + 76, yy + 58, sub, size=13, color=MUTED, anchor="start"))

        f.append(line(xr, yy + 14, xr, yy + h - 14, color=MUTED, sw=2))
        f.append(text(xr + 18, yy + h / 2 + 5, need, size=13, anchor="start"))

        if i < len(stages) - 1:
            f.append(arrow(xl + wl / 2, yy + h + 5, xl + wl / 2, yy + step - 5))

    base = y0 + 4 * step + h
    f.append(line(60, base + 34, W - 60, base + 34, color=MUTED, sw=1, dash="5,5"))
    f.append(text(W / 2, base + 66,
                  "порядок не переставити: крок 4 підставляє номери, яких до кроку 3 ще немає,",
                  size=14, color=POS))
    f.append(text(W / 2, base + 92,
                  "а крок 3 не знає номерів, поки крок 2 не вирішив, чи є нульовий запис",
                  size=14, color=POS))

    render(out('plan-pipeline.svg'), W, H, *f)


# ────────────────────────────────────────────────────────────────────────────
# 6. Вставка math: сходинка float32 проти рівної сітки int32 × 10⁷
# ────────────────────────────────────────────────────────────────────────────
def grid_step_ladder():
    import math
    W, H = 1220, 620
    f = []

    x0, x1 = 165, 1030
    ytop, ybot = 96, 452
    L45 = 111131.8                      # метрів на градус широти @45°

    tmax = math.log2(180.0)

    def px(deg):
        return x0 + math.log2(deg) / tmax * (x1 - x0)

    lo_m, hi_m = 0.005, 2.6
    ll, lh = math.log10(lo_m), math.log10(hi_m)

    def py(m):
        return ybot - (math.log10(m) - ll) / (lh - ll) * (ybot - ytop)

    # ── осі: тільки риски, без ліній через поле (щоб нічого не перетинало написи)
    f.append(line(x0, ytop - 6, x0, ybot, color=INK, sw=1.6))
    for v, lab in [(0.01, "1 см"), (0.1, "10 см"), (1.0, "1 м")]:
        y = py(v)
        f.append(line(x0 - 9, y, x0, y, color=INK, sw=1.6))
        f.append(text(x0 - 16, y + 4, lab, size=12, color=MUTED, anchor="end"))

    f.append(line(x0, ybot, x1, ybot, color=INK, sw=1.6))
    for d in [1, 2, 4, 8, 16, 32, 64, 128, 180]:
        x = px(d)
        f.append(line(x, ybot, x, ybot + 6, color=INK, sw=1.4))
        f.append(text(x, ybot + 24, "%d°" % d, size=12, color=MUTED))
    f.append(text((x0 + x1) / 2, ybot + 54,
                  "|координата| в градусах — межі діапазонів стоять на степенях двійки",
                  size=13, color=MUTED))
    f.append(text(x0 - 16, ytop - 30, "крок сітки на землі, по широті",
                  size=13, color=MUTED, anchor="start"))

    # ── сходинка float32
    binades = [(1, 2), (2, 4), (4, 8), (8, 16), (16, 32), (32, 64), (64, 128), (128, 180)]
    prev_y = None
    for lo, hi in binades:
        e = int(math.log2(lo))
        step = 2.0 ** (e - 23) * L45
        y = py(step)
        xa, xb = px(lo), px(hi)
        if prev_y is not None:
            f.append(line(xa, prev_y, xa, y, color=POS, sw=1.4, dash="4,4"))
        f.append(line(xa, y, xb, y, color=POS, sw=3.4))
        cm = step * 100
        lab = "%.0f см" % cm if cm >= 100 else ("%.1f см" % cm)
        f.append(text((xa + xb) / 2, y - 11, lab, size=12, color=POS, bold=True))
        prev_y = y

    # ── рівна сітка int32
    yint = py(0.011117)
    f.append(line(x0, yint, x1, yint, color=FIELD, sw=3.4))
    f.append(mtext(x1 + 14, yint - 4, ["int32 × 10⁷", "1.11 см скрізь"],
                   size=13, color=FIELD, bold=True, anchor="start"))

    # ── позначка наскрізного прикладу
    d = 47.3977
    e = int(math.floor(math.log2(d)))
    ymk = py(2.0 ** (e - 23) * L45)
    xmk = px(d)
    f.append(circle(xmk, ymk, 5, fill=BG, stroke=POS, sw=2.2))
    f.append(text(xmk, ymk + 24, "Цюрих, 47.4°", size=12, color=INK))

    f.append(text(W / 2, H - 34,
                  "щоб float32 давав крок дрібніший за 1.11 см, координата має бути меншою за 1° — "
                  "смуга 111 км обабіч екватора й нульового меридіана",
                  size=13, color=MUTED))

    render(out('float-vs-int-step.svg'), W, H, *f,
           title="крок між сусідніми зображуваними значеннями, переведений у метри")


# ────────────────────────────────────────────────────────────────────────────
# 7. Вставка math: клітинка квантування у двох точках планети (у масштабі)
# ────────────────────────────────────────────────────────────────────────────
def quant_cells():
    W, H = 1220, 660
    f = []
    S = 660.0            # пікселів на метр

    def dim_v(x, y1, y2, lab, tx):
        return [line(x, y1, x, y2, color=NEG, sw=1.4),
                line(x - 5, y1, x + 5, y1, color=NEG, sw=1.4),
                line(x - 5, y2, x + 5, y2, color=NEG, sw=1.4),
                text(tx, (y1 + y2) / 2 + 5, lab, size=13, color=NEG, anchor="end")]

    def dim_h(y, xa, xb, lab, ty):
        return [line(xa, y, xb, y, color=NEG, sw=1.4),
                line(xa, y - 5, xa, y + 5, color=NEG, sw=1.4),
                line(xb, y - 5, xb, y + 5, color=NEG, sw=1.4),
                text((xa + xb) / 2, ty, lab, size=13, color=NEG)]

    # ── Цюрих: висока вузька клітинка
    cx, cy = 300, 330
    w, h = 0.0720 * S, 0.4241 * S
    f.append(text(cx, 96, "Цюрих   47.3977° пн. ш.,  8.5456° сх. д.", size=15, bold=True))
    f.append(rect(cx - w / 2, cy - h / 2, w, h, fill="#fdecea", stroke=POS, sw=2))
    f += dim_v(cx - w / 2 - 46, cy - h / 2, cy + h / 2, "42.4 см", cx - w / 2 - 56)
    f += dim_h(cy + h / 2 + 40, cx - w / 2, cx + w / 2, "7.2 см", cy + h / 2 + 62)
    iw, ih = 0.00755 * S, 0.011118 * S
    f.append(rect(cx - iw / 2, cy - ih / 2, iw, ih, fill=FIELD, stroke=FIELD, sw=1, rx=1))
    f.append(line(cx + iw / 2 + 2, cy - ih / 2, cx + 96, cy - 96, color=FIELD, sw=1.3))
    f.append(text(cx + 100, cy - 100, "int32 × 10⁷:  1.11 × 0.75 см",
                  size=13, color=FIELD, bold=True, anchor="start"))

    # ── Найробі: низька широка клітинка
    cx2, cy2 = 850, 330
    w2, h2 = 0.4245 * S, 0.0132 * S
    f.append(text(cx2, 96, "Найробі   1.2921° пд. ш.,  36.8219° сх. д.", size=15, bold=True))
    f.append(rect(cx2 - w2 / 2, cy2 - h2 / 2, w2, h2, fill="#fdecea", stroke=POS, sw=2))
    f += dim_h(cy2 + 52, cx2 - w2 / 2, cx2 + w2 / 2, "42.5 см", cy2 + 74)
    f.append(line(cx2 - w2 / 2 - 8, cy2, cx2 - w2 / 2 - 52, cy2 - 54, color=NEG, sw=1.3))
    f.append(text(cx2 - w2 / 2 - 56, cy2 - 58, "1.3 см", size=13, color=NEG, anchor="end"))
    iw2, ih2 = 0.011132 * S, 0.011057 * S
    f.append(rect(cx2 - iw2 / 2, cy2 - ih2 / 2, iw2, ih2, fill=FIELD, stroke=FIELD, sw=1, rx=1))
    f.append(line(cx2 + iw2 / 2 + 2, cy2 - ih2 / 2, cx2 + 90, cy2 - 96, color=FIELD, sw=1.3))
    f.append(text(cx2 + 94, cy2 - 100, "int32 × 10⁷:  1.11 × 1.11 см",
                  size=13, color=FIELD, bold=True, anchor="start"))

    # ── масштабна лінійка
    sx, sy = 120, 566
    f.append(line(sx, sy, sx + 0.1 * S, sy, color=INK, sw=2))
    f.append(line(sx, sy - 6, sx, sy + 6, color=INK, sw=2))
    f.append(line(sx + 0.1 * S, sy - 6, sx + 0.1 * S, sy + 6, color=INK, sw=2))
    f.append(text(sx + 0.05 * S, sy + 24, "10 см", size=13, color=INK))

    f.append(text(W / 2, H - 34,
                  "рожеве — клітинка float32, зелене — клітинка int32 × 10⁷; обидві в масштабі. "
                  "Форму задає лише те, у який двійковий діапазон потрапило число",
                  size=13, color=MUTED))

    render(out('quant-cell.svg'), W, H, *f,
           title="одне й те саме число бітів, різні клітинки квантування")


if __name__ == '__main__':
    three_faces()
    command_layers()
    sequence_expand()
    dojump_id()
    plan_pipeline()
    grid_step_ladder()
    quant_cells()
    print('ok')
