# -*- coding: utf-8 -*-
"""Фігури до кроку «Класи трафіку DH».
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
AMBERST = "#c9a93b"
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


# ───────── Фіг. 1: топологія — чотири течії, чотири канали ─────────
def fig_topology():
    W, H = 1120, 632
    f = []
    # заголовки колонок
    f.append(text(150, 60, "ХТО ШЛЕ", size=13, bold=True, color=MUTED))
    f.append(text(560, 60, "КАНАЛ (примітив)", size=13, bold=True, color=MUTED))
    f.append(text(930, 60, "ХТО СПОЖИВАЄ", size=13, bold=True, color=MUTED))

    bands = [
        # cy, accent, accentbg, producer, channel(2 lines), consumers(lines)
        (128, POS, REDBG, "застосунок\n+ людина",
         "точкова черга\nодин адресат · чекають · фактично раз",
         ["один пристрій — замок,", "і жоден інший"]),
        (268, NEG, BLUEBG, "давачі\n(потік вимірів)",
         "журнал подій\nбагато читачів · свій offset · переграти",
         ["жива панель · твін дому", "історія · тривоги", "(кожен незалежно, свій темп)"]),
        (408, FIELD, GREENBG, "сервіс\nдомену",
         "тема pub/sub\nфан-аут · видавець не знає, хто слухає",
         ["пуш · автоматика", "аудит · безпека", "(додати слухача — не чіпати видавця)"]),
        (548, AMBER, AMBERBG, "планувальник",
         "робоча черга\nпул воркерів · один таск — один воркер",
         ["воркер · воркер · воркер", "(взаємозамінні, масштабуй кількістю)"]),
    ]
    for cy, ac, acbg, prod, chan, cons in bands:
        # тло смуги
        f.append(rect(32, cy - 58, 1056, 116, fill="#fbfcfd", stroke="#e5e7eb", sw=1, rx=12))
        # продюсер
        f.append(fitbox(60, cy - 30, 170, 60, prod, size=12.5, bold=True,
                        fill=acbg, stroke=ac, color=INK, sw=1.6))
        f.append(arrow(232, cy, 372, cy, color=ac, sw=2.2))
        # канал
        f.append(fitbox(376, cy - 34, 320, 68, chan, size=12.5, bold=True,
                        fill=FAINT, stroke=ac, color=INK, sw=2))
        f.append(arrow(700, cy, 792, cy, color=ac, sw=2.2))
        # споживачі
        f.append(fitbox(796, cy - 38, 296, 76, cons, size=12, bold=False,
                        fill="#ffffff", stroke=ac, color=INK, sw=1.6))

    f.append(fitbox(230, 596, 660, 30,
                    "Не одна труба на все — по одній на кожну форму трафіку.",
                    size=13.5, fill=FILL, stroke=INK, color=INK, bold=True, sw=1.8))

    render(os.path.join(IMG, "dh-traffic-topology.svg"), W, H, *f,
           title="Чотири течії трафіку DH — кожна до свого каналу")


# ───────── Фіг. 2: матриця класифікації ─────────
def fig_matrix():
    W, H = 1160, 392
    f = []
    # колонки: (x, w, заголовок)
    cols = [
        (36, 168, "Клас трафіку"),
        (204, 210, "Скільки споживачів"),
        (414, 120, "Хто чекає"),
        (534, 176, "Гарантія"),
        (710, 132, "Переграти"),
        (842, 282, "Примітив"),
    ]
    # шапка
    hy = 66
    for x, w, title in cols:
        f.append(fitbox(x, hy, w, 46, title, size=13, bold=True,
                        fill="#eef1f4", stroke=LINE, color=INK, sw=1.4))

    rows = [
        (POS,   REDBG,   "Команда\nпристрою",  "один адресат",       "так", "фактично раз",   "важить",  "точкова\nчерга"),
        (NEG,   BLUEBG,  "Телеметрія",          "багато незалежних",  "ні",  "щонайменше раз", "не важить", "журнал\nподій"),
        (FIELD, GREENBG, "Подія\nдомену",       "багато, невідомих",  "ні",  "щонайменше раз", "бажаний", "тема\npub/sub"),
        (AMBER, AMBERBG, "Фонова\nзадача",      "пул воркерів",       "ні",  "щонайменше раз", "не важить", "черга +\nконкурентні\nспоживачі"),
    ]
    ry = 116
    rh = 62
    for ac, acbg, cls, cons, waits, deliv, order, prim in rows:
        vals = [cls, cons, waits, deliv, order, prim]
        for (x, w, _), v in zip(cols, vals):
            last = (x == cols[-1][0])
            f.append(fitbox(x, ry, w, rh, v, size=12.5,
                            bold=(last or x == cols[0][0]),
                            fill=(acbg if last else "#ffffff"),
                            stroke=(ac if last else "#d5dae0"),
                            color=INK, sw=(1.8 if last else 1.2)))
        ry += rh

    render(os.path.join(IMG, "traffic-matrix.svg"), W, H, *f,
           title="Форма трафіку добирає примітив — п'ять питань, один рядок")


# ───────── Фіг. 3: ціна схибленого добору ─────────
def fig_mismatch():
    W, H = 1120, 452
    f = []

    def event_box(cx, cy):
        return fitbox(cx - 95, cy - 26, 190, 52, "подія домену\n«гість відчинив»",
                      size=12.5, bold=True, fill=FAINT, stroke=INK, color=INK, sw=1.6)

    # ── ЛІВА: хибно — черга ──
    f.append(rect(32, 58, 512, 356, fill="#fdf5f4", stroke=POS, sw=1.6, rx=12))
    f.append(text(288, 84, "ХИБНО: подія — точковою чергою", size=14, bold=True, color=POS))
    f.append(event_box(288, 128))
    f.append(arrow(288, 154, 288, 190, color=POS, sw=2.2))
    f.append(fitbox(148, 190, 280, 52, "черга\nодин споживач на повідомлення",
                    size=12, bold=True, fill=REDBG, stroke=POS, color=INK, sw=1.8))
    # розгалуження до двох, що конкурують
    f.append(arrow(230, 242, 150, 300, color=POS, sw=2))
    f.append(arrow(346, 242, 426, 300, color=POS, sw=2))
    f.append(fitbox(74, 302, 150, 48, "пуш", size=13, bold=True,
                    fill="#ffffff", stroke=LINE, color=INK, sw=1.4))
    f.append(fitbox(352, 302, 150, 48, "аудит", size=13, bold=True,
                    fill="#ffffff", stroke=LINE, color=INK, sw=1.4))
    f.append(text(288, 326, "б'ються", size=12, bold=True, color=POS))
    f.append(xmark(288, 300, r=9))
    f.append(fitbox(60, 366, 456, 38,
                    "кожну подію дістає лише ОДИН — пуш губить одні, аудит інші",
                    size=12, fill="#ffffff", stroke=POS, color=INK, sw=1.4))

    # ── ПРАВА: правильно — тема ──
    f.append(rect(576, 58, 512, 356, fill="#f3fbf6", stroke=FIELD, sw=1.6, rx=12))
    f.append(text(832, 84, "ПРАВИЛЬНО: подія — темою pub/sub", size=14, bold=True, color=FIELD))
    f.append(event_box(832, 128))
    f.append(arrow(832, 154, 832, 190, color=FIELD, sw=2.2))
    f.append(fitbox(692, 190, 280, 52, "тема pub/sub\nкопія КОЖНОМУ підписнику",
                    size=12, bold=True, fill=GREENBG, stroke=FIELD, color=INK, sw=1.8))
    f.append(arrow(770, 242, 700, 300, color=FIELD, sw=2))
    f.append(arrow(894, 242, 964, 300, color=FIELD, sw=2))
    f.append(fitbox(620, 302, 150, 48, "пуш", size=13, bold=True,
                    fill="#ffffff", stroke=FIELD, color=INK, sw=1.4))
    f.append(fitbox(896, 302, 150, 48, "аудит", size=13, bold=True,
                    fill="#ffffff", stroke=FIELD, color=INK, sw=1.4))
    f.append(check(700, 280, r=8))
    f.append(check(964, 280, r=8))
    f.append(fitbox(604, 366, 456, 38,
                    "кожен підписник дістає СВОЮ копію кожної події — бачать усе",
                    size=12, fill="#ffffff", stroke=FIELD, color=INK, sw=1.4))

    render(os.path.join(IMG, "mismatch-cost.svg"), W, H, *f,
           title="Та сама подія, два канали — і різниця вилазить на другому споживачі")


# ───────── Фіг. 4 (до proj): механіка курсора — чому черга краде ─────────
def fig_cursors():
    W, H = 1120, 650
    f = []
    X0, STEP, CW = 240, 88, 76          # рядок із 6 комірок-подій
    cells_x = [X0 + i * STEP for i in range(6)]
    center = lambda i: cells_x[i] + CW / 2
    right_edge = lambda i: cells_x[i] + CW

    # ── Панель А: черга — ОДИН спільний курсор ──
    f.append(rect(40, 56, 1040, 262, fill="#fdf5f4", stroke=POS, sw=1.6, rx=12))
    f.append(text(64, 88, "ЧЕРГА (point-to-point): один спільний курсор — кожне повідомлення дістає лише ОДИН споживач",
                  size=14, bold=True, color=POS, anchor="start"))
    for i, x in enumerate(cells_x):
        push = (i % 2 == 0)             # e1,e3,e5 → пуш; e2,e4,e6 → аудит
        f.append(fitbox(x, 114, CW, 52, "e%d" % (i + 1), size=16, bold=True,
                        fill=(BLUEBG if push else AMBERBG),
                        stroke=(NEG if push else AMBER), color=INK, sw=1.8))
    f.append(text(64, 198, "курсор крокує 1→2→1→2…  (round-robin) — по черзі, кожне лише наступному",
                  size=12.5, color=INK, anchor="start"))
    f.append(fitbox(240, 228, 220, 52, "пуш  →  e1, e3, e5", size=13, bold=True,
                    fill=BLUEBG, stroke=NEG, color=INK, sw=1.8))
    f.append(fitbox(486, 228, 220, 52, "аудит  →  e2, e4, e6", size=13, bold=True,
                    fill=AMBERBG, stroke=AMBER, color=INK, sw=1.8))
    f.append(fitbox(732, 228, 320, 52, "жоден не бачить усе —\nполовина губиться в кожного",
                    size=13, bold=True, fill="#ffffff", stroke=POS, color=POS, sw=1.8))

    # ── Панель Б: журнал — у КОЖНОГО свій offset ──
    f.append(rect(40, 342, 1040, 288, fill="#f3fbf6", stroke=FIELD, sw=1.6, rx=12))
    f.append(text(64, 374, "ЖУРНАЛ (event log): у кожного читача СВІЙ offset — кожен проходить усі 6 незалежно",
                  size=14, bold=True, color=FIELD, anchor="start"))
    for i, x in enumerate(cells_x):
        f.append(fitbox(x, 400, CW, 48, "e%d" % (i + 1), size=16, bold=True,
                        fill=FAINT, stroke=LINE, color=INK, sw=1.4))
    readers = [("пуш · offset=6", 5),
               ("аудит · offset=3", 2),
               ("аналітика · offset=1", 0)]
    ty = 492
    for label, idx in readers:
        f.append(text(64, ty + 5, label, size=12.5, bold=True, color=INK, anchor="start"))
        f.append(line(X0, ty, right_edge(5), ty, color="#c9d3cf", sw=2))     # уся стрічка
        f.append(line(X0, ty, right_edge(idx), ty, color=FIELD, sw=3.2))     # пройдене цим читачем
        f.append(circle(right_edge(idx), ty, 5.5, fill=FIELD, stroke=FIELD, sw=1))
        ty += 40
    f.append(fitbox(792, 470, 268, 104,
                    "Спільний offset = знову ЧЕРГА:\nдва читачі на одному курсорі\nділять потік (та сама крадіжка).\nПриватний offset кожному —\nте саме лікування, що й тема.",
                    size=11.5, bold=False, fill="#ffffff", stroke=FIELD, color=INK, sw=1.6))

    render(os.path.join(IMG, "cursor-mechanics.svg"), W, H, *f,
           title="Один спільний курсор краде; приватний курсор кожному — ні")


# ───────── Фіг. 5 (hist): родовід трьох намірів ─────────
def fig_genealogy():
    W, H = 1180, 560
    f = []
    f.append(text(590, 42, "Родовід трьох намірів: два старі корені зійшлися 2003-го",
                  size=15, bold=True, color=INK))

    # два корені ліворуч
    f.append(fitbox(48, 128, 322, 92,
                    "CQS · Меєр · 1988\nкоманда (роби) · запит (дай дані)",
                    size=12.5, bold=True, fill=BLUEBG, stroke=NEG, color=INK, sw=1.8))
    f.append(fitbox(48, 348, 322, 92,
                    "Ідея події · Observer, GoF · 1994\nсталося → інші реагують, не знаючи кого",
                    size=12.5, bold=True, fill=GREENBG, stroke=FIELD, color=INK, sw=1.8))

    # синтез посередині
    f.append(fitbox(468, 228, 248, 112,
                    "EIP · Гопе й Вулф · 2003\nдоповідь PLoP 2002 → книжка\nнамір повідомлення",
                    size=12.5, bold=True, fill=AMBERBG, stroke=AMBER, color=INK, sw=2.2))
    f.append(arrow(370, 174, 468, 262, color=NEG, sw=2.2))
    f.append(arrow(370, 394, 468, 314, color=FIELD, sw=2.2))

    # три гілки праворуч
    branches = [
        (96,  POS,   REDBG,   "КОМАНДА\n«зроби це» — виклич процедуру деінде"),
        (238, NEG,   BLUEBG,  "ДОКУМЕНТ\n«ось дані» — передай факт, вирішує сам"),
        (380, FIELD, GREENBG, "ПОДІЯ\n«сталося» — сповісти; зміст часто порожній"),
    ]
    for y, ac, acbg, s in branches:
        f.append(arrow(716, 284, 820, y + 52, color=ac, sw=2))
        f.append(fitbox(820, y, 322, 104, s, size=12.5, bold=True,
                        fill=acbg, stroke=ac, color=INK, sw=1.8))

    render(os.path.join(IMG, "intent-genealogy.svg"), W, H, *f,
           title="Родовід трьох намірів повідомлення — CQS і подія зійшлися в EIP")


# ───────── Фіг. 6 (hist): одне слово — три очікування ─────────
def fig_three_intents():
    W, H = 1180, 500
    f = []
    f.append(text(590, 42, "Одне слово — три очікування, яких із байтів не видно",
                  size=15, bold=True, color=INK))

    # німий пакунок і три німі питання
    f.append(fitbox(56, 150, 250, 150, "«ПОВІДОМЛЕННЯ»\nбайти без наміру",
                    size=14, bold=True, fill=FAINT, stroke=MUTED, color=INK, sw=1.8))
    f.append(fitbox(340, 150, 250, 150,
                    "Отримувач не знає:\n— чекати відповідь?\n— хто споживач і скільки?\n— чи важить свіжість?",
                    size=12.5, bold=False, fill=BG, stroke=MUTED, color=INK, sw=1.4))
    f.append(text(628, 122, "назвати намір", size=12, bold=True, color=AMBER))
    f.append(arrow(590, 225, 656, 225, color=INK, sw=2.4))

    # три названі наміри, кожен відповідає на три питання
    answers = [
        (96,  POS,   REDBG,   "КОМАНДА — «роби це»\nвідповідь можлива · один адресат · час критичний"),
        (222, NEG,   BLUEBG,  "ДОКУМЕНТ — «ось дані»\nбез відповіді · вирішує сам споживач · зміст, не час"),
        (348, FIELD, GREENBG, "ПОДІЯ — «сталося»\nбез відповіді · багато невідомих · вміст часто порожній"),
    ]
    for y, ac, acbg, s in answers:
        f.append(arrow(656, 225, 668, y + 52, color=ac, sw=1.8))
        f.append(fitbox(668, y, 496, 104, s, size=12.5, bold=True,
                        fill=acbg, stroke=ac, color=INK, sw=1.8))

    render(os.path.join(IMG, "one-word-three-intents.svg"), W, H, *f,
           title="Одне слово — три очікування: команда, документ, подія")


if __name__ == "__main__":
    fig_topology()
    fig_matrix()
    fig_mismatch()
    fig_cursors()
    fig_genealogy()
    fig_three_intents()
    print("OK: dh-traffic-topology.svg, traffic-matrix.svg, mismatch-cost.svg, "
          "cursor-mechanics.svg, intent-genealogy.svg, one-word-three-intents.svg")
