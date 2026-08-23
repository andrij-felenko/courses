# -*- coding: utf-8 -*-
"""Фігури до кроку «Три варіанти твіна».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER   = "#b8860b"
AMBERBG = "#fff8e8"
REDBG   = "#fdecea"
BLUEBG  = "#eaf0fd"
GREENBG = "#eafaf0"
FAINT   = "#f4f6f8"


def xmark(cx, cy, r=8, color=POS, sw=2.6):
    return (line(cx - r, cy - r, cx + r, cy + r, color=color, sw=sw) +
            line(cx - r, cy + r, cx + r, cy - r, color=color, sw=sw))


def check(cx, cy, r=8, color=FIELD, sw=2.8):
    return (line(cx - r, cy, cx - r * 0.2, cy + r * 0.8, color=color, sw=sw) +
            line(cx - r * 0.2, cy + r * 0.8, cx + r, cy - r, color=color, sw=sw))


# ───────── Фіг. 1: де живе правда — три варіанти твіна ─────────
def fig_three_ways():
    W, H = 1180, 448
    f = []

    # ── Панель А: актор на дім (синій) ──
    f.append(rect(30, 56, 360, 376, fill="#fbfcfe", stroke=NEG, sw=1.6, rx=12))
    f.append(text(210, 86, "А · Актор на дім", size=14.5, bold=True, color=NEG))
    f.append(fitbox(60, 104, 138, 42, "звіт", size=12.5, bold=True,
                    fill=BG, stroke=NEG, color=INK, sw=1.4))
    f.append(fitbox(222, 104, 138, 42, "команда", size=12.5, bold=True,
                    fill=BG, stroke=NEG, color=INK, sw=1.4))
    f.append(arrow(129, 148, 195, 170, color=NEG, sw=1.8))
    f.append(arrow(291, 148, 225, 170, color=NEG, sw=1.8))
    f.append(fitbox(60, 172, 300, 40, "пошта → по одному, без гонок",
                    size=12.5, bold=True, fill=BLUEBG, stroke=NEG, color=INK, sw=1.8))
    f.append(arrow(210, 212, 210, 240, color=NEG, sw=2))
    f.append(fitbox(60, 242, 300, 92, "дім #42 (актор)\nстан — у пам'яті:\nheater=off · lock · 20°",
                    size=13, bold=True, fill=BG, stroke=NEG, color=INK, sw=2))
    f.append(fitbox(52, 384, 316, 38, "правда — у пам'яті об'єкта",
                    size=12.5, bold=True, fill=FAINT, stroke=NEG, color=INK, sw=1.6))

    # ── Панель Б: рядки в базі (бурштин) ──
    f.append(rect(410, 56, 360, 376, fill="#fffdf7", stroke=AMBER, sw=1.6, rx=12))
    f.append(text(590, 86, "Б · Рядки в базі", size=14.5, bold=True, color=AMBER))
    f.append(fitbox(470, 104, 240, 42, "звіт / команда", size=12.5, bold=True,
                    fill=BG, stroke=AMBER, color=INK, sw=1.4))
    f.append(arrow(590, 148, 590, 172, color=AMBER, sw=2))
    f.append(fitbox(470, 174, 240, 92, "шард за home_id\nhome42 → { heater:off,\nlock, 20° }",
                    size=12.5, bold=True, fill=AMBERBG, stroke=AMBER, color=INK, sw=2))
    f.append(arrow(590, 268, 590, 292, color=AMBER, sw=2))
    f.append(fitbox(452, 294, 276, 56, "кожна зміна = читати →\nміняти → писати (контеншен)",
                    size=12, bold=False, fill=BG, stroke=AMBER, color=INK, sw=1.4))
    f.append(fitbox(432, 384, 316, 38, "правда — у рядку на диску",
                    size=12.5, bold=True, fill=FAINT, stroke=AMBER, color=INK, sw=1.6))

    # ── Панель В: журнал і проєкції (зелений) ──
    f.append(rect(790, 56, 360, 376, fill="#f8fdfa", stroke=FIELD, sw=1.6, rx=12))
    f.append(text(970, 86, "В · Журнал і проєкції", size=14.5, bold=True, color=FIELD))
    f.append(text(970, 112, "журнал дому — тільки дописуємо", size=11.5, color=MUTED))
    evx = [837, 905, 973, 1041]
    for i, x in enumerate(evx):
        f.append(fitbox(x, 122, 62, 34, "e%d" % (i + 1), size=13, bold=True,
                        fill=FAINT, stroke=LINE, color=INK, sw=1.3))
    f.append(arrow(970, 158, 970, 190, color=FIELD, sw=2))
    f.append(fitbox(824, 192, 292, 62, "проєкція: поточний стан\n= згортка журналу",
                    size=12.5, bold=True, fill=GREENBG, stroke=FIELD, color=INK, sw=2))
    f.append(fitbox(824, 268, 292, 82, "інші проєкції над тим самим\nжурналом: історія, аудит,\nаналітика — кожна своя",
                    size=11.5, bold=False, fill=BG, stroke=FIELD, color=INK, sw=1.4))
    f.append(fitbox(812, 384, 316, 38, "правда — у журналі; стан рахуємо",
                    size=12.5, bold=True, fill=FAINT, stroke=FIELD, color=INK, sw=1.6))

    render(os.path.join(IMG, "twin-three-ways.svg"), W, H, *f,
           title="Три варіанти твіна — де живе правда про дім")


# ───────── Фіг. 2: спільна лінійка (матриця 3×5) ─────────
def fig_ruler():
    W, H = 1180, 400
    f = []

    # стовпці: (x, w). Перший — підписи варіантів.
    LX, LW = 30, 196
    cx0, cw, gap = 232, 182, 4
    cols = [cx0 + i * (cw + gap) for i in range(5)]
    heads = ["Команда на дім\n(серіалізація)", "Читання\n«покажи дім»",
             "Історія\nй аудит", "Відновлення\nпісля падіння", "Аналітика\nпо флоту"]

    # шапка
    hy, hh = 50, 54
    f.append(fitbox(LX, hy, LW, hh, "варіант ↓ / сценарій →", size=12, bold=True,
                    fill="#eef1f4", stroke=LINE, color=MUTED, sw=1.3))
    for x, s in zip(cols, heads):
        f.append(fitbox(x, hy, cw, hh, s, size=12.5, bold=True,
                        fill="#eef1f4", stroke=LINE, color=INK, sw=1.3))

    def cell(x, y, w, h, kind, tag):
        bg = {"y": GREENBG, "n": REDBG, "~": AMBERBG}[kind]
        st = {"y": FIELD, "n": POS, "~": AMBER}[kind]
        out = rect(x, y, w, h, fill=bg, stroke="#dfe4ea", sw=1)
        mx = x + w / 2
        if kind == "y":
            out += check(mx, y + 24, r=9)
        elif kind == "n":
            out += xmark(mx, y + 24, r=9)
        else:
            out += text(mx, y + 31, "≈", size=23, color=AMBER, bold=True)
        out += text(mx, y + 56, tag, size=11.5, color=INK)
        return out

    # рядки: (accent, bg, назва, [(kind, tag) ×5])
    rows = [
        (NEG, BLUEBG, "Актор\nна дім", [
            ("y", "пошта серіалізує"), ("y", "з пам'яті, миттєво"),
            ("n", "нема"), ("~", "зі снапшотів"), ("n", "розсипано")]),
        (AMBER, AMBERBG, "Рядки\nв базі", [
            ("~", "блокування"), ("~", "репліки, лаг"),
            ("n", "нема"), ("y", "база тривка"), ("y", "SQL по стану")]),
        (FIELD, GREENBG, "Журнал\nі проєкції", [
            ("~", "порядок у лозі"), ("~", "проєкція відстає"),
            ("y", "задарма"), ("y", "переграти"), ("y", "проєкція")]),
    ]
    ry, rh = 116, 74
    for ac, acbg, name, cells in rows:
        f.append(fitbox(LX, ry, LW, rh, name, size=13, bold=True,
                        fill=acbg, stroke=ac, color=INK, sw=1.8))
        for x, (kind, tag) in zip(cols, cells):
            f.append(cell(x, ry, cw, rh, kind, tag))
        ry += rh

    # легенда
    ly = 368
    f.append(check(250, ly - 4, r=8))
    f.append(text(268, ly, "виграє задарма", size=12, color=INK, anchor="start"))
    f.append(text(470, ly, "≈", size=20, color=AMBER, bold=True))
    f.append(text(486, ly, "тягне, але коштує", size=12, color=INK, anchor="start"))
    f.append(xmark(700, ly - 4, r=8))
    f.append(text(718, ly, "не тягне — потрібна інша система", size=12, color=INK, anchor="start"))

    render(os.path.join(IMG, "twin-ruler.svg"), W, H, *f,
           title="Спільна лінійка: жоден варіант не бере все")


# ───────── Фіг. 3: один сценарій — спільний вхід для всіх трьох ─────────
def fig_scenario():
    W, H = 960, 384
    f = []

    # твін дому #42 — ліворуч
    f.append(fitbox(40, 150, 200, 96,
                    "дім #42\nзамок «entrance»\nтвін: { bolt, version }",
                    size=13, bold=True, fill=FAINT, stroke=INK, color=INK, sw=1.8))

    # дві команди «замкни» — майже одночасно
    f.append(fitbox(300, 70, 300, 52, "сесія A:  замкни  (seq 6)",
                    size=13, bold=True, fill=BLUEBG, stroke=NEG, color=INK, sw=1.6))
    f.append(fitbox(300, 274, 300, 52, "сесія B:  замкни  (seq 7)",
                    size=13, bold=True, fill=BLUEBG, stroke=NEG, color=INK, sw=1.6))
    f.append(arrow(300, 96, 244, 176, color=NEG, sw=2))
    f.append(arrow(300, 300, 244, 220, color=NEG, sw=2))
    f.append(text(322, 205, "майже одночасно", size=12, color=MUTED, anchor="start", italic=True))

    # хвиля часу далі — і крах вузла
    f.append(arrow(240, 198, 636, 198, color=INK, sw=2))
    # символ краху — зигзаг на кінці стрічки часу
    cx, cy = 662, 196
    for dx, dy in [(-14, -18), (12, -6), (-6, 8), (16, 18)]:
        f.append(line(cx, cy, cx + dx, cy + dy, color=POS, sw=3))
    f.append(fitbox(596, 112, 152, 40, "вузол гине", size=13, bold=True,
                    fill=REDBG, stroke=POS, color=INK, sw=1.8))

    # дві питання-осі, які сценарій ставить кожному варіанту
    f.append(fitbox(720, 118, 216, 72,
                    "① гонка\nобидві команди враховано?\n(version = 7?)",
                    size=12, bold=True, fill=BG, stroke=INK, color=INK, sw=1.4))
    f.append(fitbox(720, 210, 216, 72,
                    "② крах\nправда вціліла\nпісля воскресіння?",
                    size=12, bold=True, fill=BG, stroke=INK, color=INK, sw=1.4))

    render(os.path.join(IMG, "scenario-fixture.svg"), W, H, *f,
           title="Один сценарій: дві «замкни» на дім #42, потім крах вузла")


# ───────── Фіг. 4: перша різниця — хто виграє гонку (серіалізація) ─────────
def fig_race():
    W, H = 1160, 452
    f = []
    LX, LW = 24, 138
    lanes = [
        (72,  NEG,   BLUEBG,  "А · Актор\nна дім"),
        (204, AMBER, AMBERBG, "Б · Рядок\nу базі"),
        (336, FIELD, GREENBG, "В · Журнал\nі проєкція"),
    ]
    for y, ac, acbg, name in lanes:
        f.append(fitbox(LX, y, LW, 104, name, size=13, bold=True,
                        fill=acbg, stroke=ac, color=INK, sw=1.8))

    # ── Лане А: пошта серіалізує ──
    yA = 72
    f.append(fitbox(176, yA + 8, 156, 88, "пошта (FIFO)\n[ seq6 ]\n[ seq7 ]",
                    size=12.5, bold=True, fill=BLUEBG, stroke=NEG, color=INK, sw=1.6))
    f.append(arrow(332, yA + 52, 384, yA + 52, color=NEG, sw=2))
    f.append(text(358, yA + 42, "по одному", size=10.5, color=MUTED))
    f.append(fitbox(388, yA + 20, 150, 64, "актор застосовує\nпо черзі",
                    size=12.5, bold=True, fill=BG, stroke=NEG, color=INK, sw=1.4))
    f.append(arrow(538, yA + 52, 590, yA + 52, color=NEG, sw=2))
    f.append(fitbox(594, yA + 26, 178, 52, "version 5 → 6 → 7", size=13, bold=True,
                    fill=GREENBG, stroke=FIELD, color=INK, sw=1.6))
    f.append(check(792, yA + 52, r=10))
    f.append(fitbox(820, yA + 20, 316, 64,
                    "гонки нема ЗА ПОБУДОВОЮ —\nскринька і є та черга",
                    size=12, bold=True, fill=FAINT, stroke=NEG, color=INK, sw=1.4))

    # ── Лане Б: RMW-гонка й лік ──
    yB = 204
    f.append(fitbox(176, yB + 4, 210, 42, "txn①:  read v5 → write v6",
                    size=12, bold=False, fill=BG, stroke=AMBER, color=INK, sw=1.3))
    f.append(fitbox(176, yB + 58, 210, 42, "txn②:  read v5 → write v6",
                    size=12, bold=False, fill=BG, stroke=AMBER, color=INK, sw=1.3))
    f.append(arrow(386, yB + 25, 446, yB + 44, color=AMBER, sw=1.8))
    f.append(arrow(386, yB + 79, 446, yB + 60, color=AMBER, sw=1.8))
    f.append(fitbox(450, yB + 26, 150, 52, "v6 — одна\nкоманда зникла",
                    size=12, bold=True, fill=REDBG, stroke=POS, color=INK, sw=1.6))
    f.append(xmark(524, yB + 90, r=9))
    f.append(arrow(600, yB + 52, 652, yB + 52, color=AMBER, sw=2))
    f.append(text(626, yB + 42, "лік", size=10.5, color=MUTED))
    f.append(fitbox(656, yB + 20, 300, 64,
                    "CAS: «…WHERE version = 5»\nдруга не збігається → ретрай → v7",
                    size=11.5, bold=True, fill=GREENBG, stroke=FIELD, color=INK, sw=1.4))
    f.append(check(980, yB + 52, r=10))
    f.append(fitbox(1008, yB + 26, 128, 52, "версія рядка\nабо замок",
                    size=11.5, bold=True, fill=FAINT, stroke=AMBER, color=INK, sw=1.4))

    # ── Лане В: лог дає порядок ──
    yV = 336
    f.append(text(176, yV + 8, "лог — тільки дописуємо, позиція = порядок",
                  size=11, color=MUTED, anchor="start"))
    slots = [("e5", FAINT, LINE), ("e6", GREENBG, FIELD), ("e7", GREENBG, FIELD)]
    sx = 176
    for lab, bg, st in slots:
        f.append(fitbox(sx, yV + 20, 64, 56, lab, size=13, bold=True,
                        fill=bg, stroke=st, color=INK, sw=1.5))
        sx += 72
    f.append(arrow(sx + 2, yV + 48, sx + 54, yV + 48, color=FIELD, sw=2))
    f.append(fitbox(sx + 58, yV + 22, 178, 52, "згортка apply\n→ version 7",
                    size=12.5, bold=True, fill=GREENBG, stroke=FIELD, color=INK, sw=1.6))
    f.append(check(sx + 260, yV + 48, r=10))
    f.append(fitbox(sx + 290, yV + 22, 250, 52,
                    "дописи не перетирають —\nгонки на втрату нема",
                    size=11.5, bold=True, fill=FAINT, stroke=FIELD, color=INK, sw=1.4))

    render(os.path.join(IMG, "race-serialization.svg"), W, H, *f,
           title="Перша різниця: хто не дасть двом «замкни» злитися")


# ───────── Фіг. 5: друга різниця — хто переживе крах (відновлення) ─────────
def fig_crash():
    W, H = 1160, 452
    f = []
    LX, LW = 24, 138
    lanes = [
        (72,  NEG,   BLUEBG,  "А · Актор\nзі снапшота"),
        (204, AMBER, AMBERBG, "Б · Рядок\nна диску"),
        (336, FIELD, GREENBG, "В · Журнал\nпереграти"),
    ]
    for y, ac, acbg, name in lanes:
        f.append(fitbox(LX, y, LW, 104, name, size=13, bold=True,
                        fill=acbg, stroke=ac, color=INK, sw=1.8))

    # ── Лане А: RAM стерто → снапшот → переграти хвіст ──
    yA = 72
    # RAM стерто крахом: червона рамка й приглушений напис (без перекреслення тексту)
    f.append(fitbox(176, yA + 18, 158, 66, "RAM: version 7\n(стерто крахом)",
                    size=12, bold=True, fill=REDBG, stroke=POS, color=MUTED, sw=1.6))
    f.append(arrow(334, yA + 52, 386, yA + 52, color=NEG, sw=2))
    f.append(fitbox(390, yA + 22, 168, 60, "снапшот v5\n(на диску)",
                    size=12.5, bold=True, fill=GREENBG, stroke=FIELD, color=INK, sw=1.5))
    f.append(arrow(558, yA + 52, 610, yA + 52, color=NEG, sw=2))
    f.append(fitbox(614, yA + 22, 200, 60, "+ переграти хвіст\ne6, e7 → v7",
                    size=12.5, bold=True, fill=GREENBG, stroke=FIELD, color=INK, sw=1.5))
    f.append(check(836, yA + 52, r=10))
    f.append(fitbox(864, yA + 20, 272, 64,
                    "БЕЗ журналу хвоста → лише v5:\nдві команди втрачено",
                    size=11.5, bold=True, fill=REDBG, stroke=POS, color=INK, sw=1.4))

    # ── Лане Б: рядок уже на диску ──
    yB = 204
    f.append(fitbox(176, yB + 22, 210, 60, "рядок v7 на диску\n(зафіксовано, fsync)",
                    size=12.5, bold=True, fill=AMBERBG, stroke=AMBER, color=INK, sw=1.6))
    f.append(arrow(386, yB + 52, 438, yB + 52, color=AMBER, sw=2))
    f.append(fitbox(442, yB + 26, 168, 52, "вцілів як є", size=13, bold=True,
                    fill=GREENBG, stroke=FIELD, color=INK, sw=1.5))
    f.append(check(632, yB + 52, r=10))
    f.append(fitbox(662, yB + 20, 474, 64,
                    "нема окремого воскресіння: зафіксоване = тривке;\n"
                    "незавершена txn — атомарний відкат, без пів-команди",
                    size=11.5, bold=True, fill=FAINT, stroke=AMBER, color=INK, sw=1.4))

    # ── Лане В: лог на диску → переграти ──
    yV = 336
    f.append(fitbox(176, yV + 22, 190, 60, "лог e6, e7 на диску\n(fsync до ack)",
                    size=12, bold=True, fill=GREENBG, stroke=FIELD, color=INK, sw=1.6))
    f.append(arrow(366, yV + 52, 418, yV + 52, color=FIELD, sw=2))
    f.append(fitbox(422, yV + 22, 200, 60, "переграти зі\nснапшота → v7",
                    size=12.5, bold=True, fill=GREENBG, stroke=FIELD, color=INK, sw=1.5))
    f.append(check(644, yV + 52, r=10))
    f.append(fitbox(674, yV + 20, 462, 64,
                    "порядок беруть із позицій у лозі;\n"
                    "проєкцію відбудовуємо згорткою наново",
                    size=11.5, bold=True, fill=FAINT, stroke=FIELD, color=INK, sw=1.4))

    render(os.path.join(IMG, "crash-recovery.svg"), W, H, *f,
           title="Друга різниця: хто переживе смерть вузла")


# ───────── Фіг. 6: три стіни в різних одиницях (вставка math) ─────────
def fig_three_walls():
    W, H = 1180, 500
    f = []

    panels = [
        # (x0, accent, panelbg, accentbg, title, fear, wall, unit)
        (30, NEG, "#fbfcfe", BLUEBG, "А · Актор",
         "RAM: 1.25 ГБ/вузол\n(ноутбукова дрібниця)",
         "реанімація вузла\n125 000 домів ≈ 6 с\nкожні ~9 діб",
         "секунди × частота"),
        (410, AMBER, "#fffdf7", AMBERBG, "Б · База",
         "вал читань: 30 тис/с\n(дрібний коло записів)",
         "злива 2.5 млн RMW/с\n→ ~500 вузлів\n+ стеля рядка 1000/с",
         "IOPS × вузли"),
        (790, FIELD, "#f8fdfa", GREENBG, "В · Журнал",
         "доклад у хвіст\n(дешевий, без RMW)",
         "43 ТБ/добу → ~4 ПБ/кв\nреплей ~год\nбез снапшотів",
         "байти × час"),
    ]

    for x0, ac, pbg, acbg, title, fear, wall, unit in panels:
        cx = x0 + 180
        f.append(rect(x0, 64, 360, 392, fill=pbg, stroke=ac, sw=1.6, rx=12))
        f.append(text(cx, 92, title, size=15, bold=True, color=ac))
        # чого бояться дарма — сірий блок, позначений хрестиком «не стіна»
        f.append(text(cx, 118, "чого бояться дарма", size=11, color=MUTED))
        f.append(fitbox(x0 + 34, 130, 292, 50, fear, size=12, bold=False,
                        fill=FAINT, stroke="#cfd6dd", color=MUTED, sw=1.3))
        f.append(xmark(x0 + 332, 124, r=8, color=MUTED, sw=2.4))
        f.append(arrow(cx, 188, cx, 212, color=ac, sw=2))
        # справжня стіна — кольоровий блок
        f.append(text(cx, 230, "справжня стіна", size=12, bold=True, color=ac))
        f.append(fitbox(x0 + 26, 240, 308, 98, wall, size=13.5, bold=True,
                        fill=acbg, stroke=ac, color=INK, sw=2.2))
        # одиниця
        f.append(text(cx, 372, "одиниця:", size=11, color=MUTED))
        f.append(fitbox(x0 + 56, 384, 248, 46, unit, size=14, bold=True,
                        fill=BG, stroke=ac, color=ac, sw=1.8))

    f.append(fitbox(40, 466, 1100, 30,
                    "три стіни — три різні одиниці (секунди · вузли · байти); однією «складністю» їх не порівняти",
                    size=13, bold=True, fill=FAINT, stroke=LINE, color=INK, sw=1.4))

    render(os.path.join(IMG, "twin-three-walls.svg"), W, H, *f,
           title="Три варіанти — три стіни в різних одиницях")


# ───────── Фіг. 7: снапшот як спільний важіль (вставка math) ─────────
def fig_snapshot_lever():
    import math
    W, H = 1020, 470
    f = []
    x0, x1 = 150, 900          # вісь X (інтервал снапшота, лог)
    yb, yt = 384, 84           # вісь Y (час, лог; униз — швидше)

    LXmin, LXmax = math.log10(60), math.log10(90 * 86400)   # 1 хв … 90 діб
    LYmin, LYmax = -5.0, 1.0                                  # 10 мкс … 10 с

    def X(iv):
        return x0 + (math.log10(iv) - LXmin) / (LXmax - LXmin) * (x1 - x0)

    def Y(t):
        return yb - (math.log10(t) - LYmin) / (LYmax - LYmin) * (yb - yt)

    def tail(iv):   # час згортки хвоста: 0.5 под/с · iv, згортка 10⁶/с
        return 0.5 * iv / 1e6

    # смуги тла за часом
    for lo, hi, col, lab in [
        (1e-5, 1e-2, GREENBG, "інтерактивно"),
        (1e-2, 1.0,  AMBERBG, "помітно"),
        (1.0,  10.0, REDBG,   "болісно"),
    ]:
        ytop, ybot = Y(hi), Y(lo)
        f.append(rect(x0, ytop, x1 - x0, ybot - ytop, fill=col, stroke="none", sw=0, rx=0))
        f.append(text(x1 - 12, ytop + 20, lab, size=12, color=MUTED, anchor="end"))

    # осі
    f.append(line(x0, yt, x0, yb, color=INK, sw=1.6))
    f.append(line(x0, yb, x1, yb, color=INK, sw=1.6))

    # позначки Y (час)
    for t, lab in [(1e-3, "1 мс"), (1e-2, "10 мс"), (1e-1, "100 мс"), (1.0, "1 с")]:
        y = Y(t)
        f.append(line(x0 - 6, y, x0, y, color=INK, sw=1.4))
        f.append(text(x0 - 12, y + 4, lab, size=11.5, color=INK, anchor="end"))

    # позначки X (інтервал)
    for iv, lab in [(60, "1 хв"), (3600, "1 год"), (86400, "1 доба"), (90 * 86400, "ніколи")]:
        x = X(iv)
        f.append(line(x, yb, x, yb + 6, color=INK, sw=1.4))
        f.append(text(x, yb + 24, lab, size=12, color=INK, bold=(lab in ("1 год", "ніколи"))))

    # лінія важеля (пряма в лог-лог)
    f.append(line(X(60), Y(tail(60)), X(90 * 86400), Y(tail(90 * 86400)), color=INK, sw=2.6))

    # точка: годинний снапшот → 1.8 мс
    xh, yh = X(3600), Y(tail(3600))
    f.append(circle(xh, yh, 6.5, fill=FIELD, stroke=BG, sw=2))
    f.append(fitbox(xh + 18, 300, 250, 46,
                    "годинний снапшот:\nчитання дому 1.8 мс · реанімація швидка",
                    size=11.5, bold=False, fill=BG, stroke=FIELD, color=INK, sw=1.4))

    # точка: ніколи → 3.9 с
    xn, yn = X(90 * 86400), Y(tail(90 * 86400))
    f.append(circle(xn, yn, 6.5, fill=POS, stroke=BG, sw=2))
    f.append(fitbox(xn - 252, 44, 244, 46,
                    "снапшот ніколи:\n3.9 с на дім · реанімація в хвилини",
                    size=11.5, bold=False, fill=BG, stroke=POS, color=INK, sw=1.4))

    # підписи осей
    f.append(text((x0 + x1) / 2, yb + 52, "інтервал снапшота (лог) →", size=13, bold=True))
    f.append(text(x0 - 4, yt - 16, "час відновлення (лог; униз — швидше)",
                  size=12, bold=True, color=INK, anchor="start"))

    render(os.path.join(IMG, "twin-snapshot-lever.svg"), W, H, *f,
           title="Снапшот — той самий важіль на дві стіни")


if __name__ == "__main__":
    fig_three_ways()
    fig_ruler()
    fig_scenario()
    fig_race()
    fig_crash()
    fig_three_walls()
    fig_snapshot_lever()
    print("OK: twin-three-ways.svg, twin-ruler.svg, "
          "scenario-fixture.svg, race-serialization.svg, crash-recovery.svg, "
          "twin-three-walls.svg, twin-snapshot-lever.svg")
