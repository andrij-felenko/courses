# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT   = "#fbfcff"
COLD   = "#eef3fd"
WARM   = "#fdf3e7"
GREENF = "#eaf7ef"
GREY   = "#f0f1f3"
PURPLE = "#7a4fb0"


def panel(x, y, w, h, head, accent, fill=SOFT):
    out = [rect(x, y, w, h, fill=fill, stroke=accent, sw=2, rx=10)]
    out.append(text(x + w / 2, y + 28, head, size=14, color=accent, bold=True))
    return "".join(out)


# ── 1. Анатомія черги: голова в об'єкті, записи на стеках сплячих ────────────
def fig_anatomy():
    W, H = 1080, 620
    p = []

    # об'єкт із головою черги
    p.append(panel(50, 110, 300, 200, "Об'єкт, якого чекають", NEG, COLD))
    p.append(mtext(200, 168, ["структура сокета,", "відкритого файлу драйвера,", "буфера пристрою"],
                   size=12, color=MUTED, lh=1.35))
    p.append(fitbox(76, 226, 248, 66,
                    "wait_queue_head\nспін-замок + голова списку", size=12, fill=SOFT, stroke=NEG))

    # три записи в черзі
    ex, ew, eh = 470, 300, 84
    ys = [110, 226, 342]
    labels = [
        "запис №1  ·  flags = 0\nprivate → задача A  ·  func",
        "запис №2  ·  flags = 0\nprivate → задача B  ·  func",
        "запис №3  ·  EXCLUSIVE\nprivate → задача C  ·  func",
    ]
    for y, s in zip(ys, labels):
        p.append(fitbox(ex, y, ew, eh, s, size=12, fill=WARM, stroke=POS))

    p.append(text(620, 96, "записи лежать на стеках самих задач", size=12, color=POS, bold=True))

    # зв'язки голова → записи
    for y in ys:
        p.append(arrow(350, 259, ex - 6, y + eh / 2, color=NEG))

    # задачі
    tx, tw, th = 830, 200, 84
    tasks = ["task_struct A\nстан = S, спить", "task_struct B\nстан = S, спить", "task_struct C\nстан = S, спить"]
    for y, s in zip(ys, tasks):
        p.append(fitbox(tx, y, tw, th, s, size=12, fill=GREY, stroke=MUTED))
        p.append(arrow(ex + ew + 4, y + eh / 2, tx - 6, y + th / 2, color=MUTED))

    # черга готових — порожня для цих задач
    p.append(fitbox(470, 500, 560, 62,
                    "черга готових цього процесорного ядра: жодної з цих задач тут немає",
                    size=13, fill=GREENF, stroke=FIELD))
    p.append(text(200, 400, "поки список порожній,", size=12, color=MUTED))
    p.append(text(200, 422, "черга не коштує нічого", size=12, color=MUTED))

    render(os.path.join(OUT, "waitqueue-anatomy.svg"), W, H,
           text(W / 2, 46, "Черга очікування живе в об'єкті, а її записи — у пам'яті сплячих", size=17, bold=True),
           *p)


# ── 2. Втрачена побудка: невірний і вірний порядок дій ──────────────────────
def fig_lost_wakeup():
    W, H = 1140, 620
    p = []

    def side(px, head, accent, rows, verdict, vcolor, vfill):
        out = [rect(px, 80, 500, 480, fill=BG, stroke=accent, sw=2, rx=12)]
        out.append(text(px + 250, 112, head, size=14, color=accent, bold=True))
        out.append(text(px + 130, 146, "той, хто чекає", size=12, color=INK, bold=True))
        out.append(text(px + 370, 146, "той, хто будить", size=12, color=INK, bold=True))
        y = 172
        for lane, s, color, fill in rows:
            bx = px + 20 if lane == 0 else px + 260
            out.append(fitbox(bx, y, 220, 56, s, size=11, fill=fill, stroke=color))
            y += 66
        out.append(fitbox(px + 20, y + 8, 460, 48, verdict, size=12, fill=vfill, stroke=vcolor, color=vcolor))
        return "".join(out)

    wrong = [
        (0, "перевірити умову:\nданих немає", MUTED, SOFT),
        (1, "покласти дані\nв об'єкт", MUTED, WARM),
        (1, "wake_up():\nу черзі порожньо", POS, WARM),
        (0, "стати в чергу", MUTED, SOFT),
        (0, "schedule()", POS, "#fdecea"),
    ]
    right = [
        (0, "стати в чергу,\nстан = TASK_INTERRUPTIBLE", MUTED, SOFT),
        (1, "покласти дані\nв об'єкт", MUTED, WARM),
        (1, "wake_up(): знайшов запис,\nставить стан = RUNNING", FIELD, WARM),
        (0, "перевірити умову:\nдані є", MUTED, SOFT),
        (0, "вийти з циклу", FIELD, GREENF),
    ]

    p.append(side(40, "Перевірити, потім стати в чергу", POS, wrong,
                  "дані є, а задача спить: побудку втрачено", POS, "#fdecea"))
    p.append(side(600, "Стати в чергу, потім перевірити", FIELD, right,
                  "найгірше, що сталося: умову перевірено двічі", FIELD, GREENF))

    render(os.path.join(OUT, "lost-wakeup.svg"), W, H,
           text(W / 2, 46, "Два порядки дій: у чому різниця між зависанням і зайвим обертом циклу",
                size=17, bold=True),
           *p)


# ── 3. Шлях пробудження ─────────────────────────────────────────────────────
def fig_wake_path():
    W, H = 1120, 600
    p = []

    bw, bh = 300, 118
    xs = [50, 410, 770]
    y1, y2 = 100, 320

    top = [
        ("Контекст перервання", "дані покладено в об'єкт;\nwq_has_sleeper() каже:\nохочі є", POS, WARM),
        ("wake_up(mode, key)", "спін-замок черги,\nобхід списку\nвід голови", NEG, COLD),
        ("Фільтр кожного запису", "стан у масці?\nключ збігся?\nвиключний — і досить?", PURPLE, SOFT),
    ]
    bottom = [
        ("Ядро-ціль", "прапорець «перепланувати»\nабо коротке перервання\nна сусіднє ядро", FIELD, GREENF),
        ("try_to_wake_up()", "стан = RUNNING,\nвибір ядра,\nвставити в чергу готових", FIELD, GREENF),
        ("entry->func()", "зняти запис зі списку\nабо виконати власний код\n(так працює epoll)", PURPLE, SOFT),
    ]

    for x, (head, body, accent, fill) in zip(xs, top):
        p.append(rect(x, y1, bw, bh, fill=fill, stroke=accent, sw=2, rx=10))
        p.append(text(x + bw / 2, y1 + 28, head, size=13, color=accent, bold=True))
        p.append(mtext(x + bw / 2, y1 + 54, body, size=11, color=INK, lh=1.35))

    for x, (head, body, accent, fill) in zip(xs, bottom):
        p.append(rect(x, y2, bw, bh, fill=fill, stroke=accent, sw=2, rx=10))
        p.append(text(x + bw / 2, y2 + 28, head, size=13, color=accent, bold=True))
        p.append(mtext(x + bw / 2, y2 + 54, body, size=11, color=INK, lh=1.35))

    p.append(arrow(xs[0] + bw, y1 + bh / 2, xs[1] - 6, y1 + bh / 2))
    p.append(arrow(xs[1] + bw, y1 + bh / 2, xs[2] - 6, y1 + bh / 2))
    p.append(arrow(xs[2] + bw / 2, y1 + bh, xs[2] + bw / 2, y2 - 6))
    p.append(arrow(xs[2] - 6, y2 + bh / 2, xs[1] + bw + 4, y2 + bh / 2))
    p.append(arrow(xs[1] - 6, y2 + bh / 2, xs[0] + bw + 4, y2 + bh / 2))

    p.append(fitbox(50, 490, 1020, 56,
                    "розбуджена задача ще не виконала жодної інструкції: вона лише знову стала кандидатом",
                    size=13, fill=SOFT, stroke=MUTED))

    render(os.path.join(OUT, "wake-path.svg"), W, H,
           text(W / 2, 46, "Що відбувається між «дані прийшли» і «задача знову в черзі готових»",
                size=17, bold=True),
           *p)


# ── 4. Виключні охочі в хвості списку ───────────────────────────────────────
def fig_exclusive():
    W, H = 1180, 520
    p = []

    p.append(fitbox(40, 190, 120, 90, "голова\nчерги", size=12, fill=COLD, stroke=NEG))

    bw, bh, y = 160, 90, 190
    xs = [210, 400, 590, 780, 970]
    items = [
        ("запис A\nне-виключний", FIELD, GREENF, "будиться"),
        ("запис B\nне-виключний", FIELD, GREENF, "будиться"),
        ("запис C\nВИКЛЮЧНИЙ", FIELD, GREENF, "будиться,\nлічильник вичерпано"),
        ("запис D\nВИКЛЮЧНИЙ", MUTED, GREY, "не чіпаємо"),
        ("запис E\nВИКЛЮЧНИЙ", MUTED, GREY, "не чіпаємо"),
    ]
    for x, (s, color, fill, status) in zip(xs, items):
        p.append(fitbox(x, y, bw, bh, s, size=12, fill=fill, stroke=color))
        p.append(mtext(x + bw / 2, y + bh + 30, status, size=11, color=color, lh=1.3))

    p.append(arrow(160, y + bh / 2, xs[0] - 6, y + bh / 2))
    for a, b in zip(xs, xs[1:]):
        p.append(arrow(a + bw, y + bh / 2, b - 6, y + bh / 2, color=MUTED))

    # зони
    p.append(line(210, 148, 550, 148, color=FIELD, sw=2))
    p.append(text(380, 138, "сповістити всіх", size=12, color=FIELD, bold=True))
    p.append(line(590, 148, 1130, 148, color=PURPLE, sw=2))
    p.append(text(860, 138, "конкуренти за одну здобич: досить одного", size=12, color=PURPLE, bold=True))

    # межа зупинки обходу
    p.append(line(756, 176, 756, 300, color=POS, sw=2, dash="6 5"))
    p.append(text(756, 330, "тут обхід зупиняється", size=12, color=POS, bold=True))

    p.append(fitbox(40, 400, 1100, 56,
                    "прапорець виключності ставлять записові в хвіст, тому один обхід списку виконує дві різні політики",
                    size=13, fill=SOFT, stroke=MUTED))

    render(os.path.join(OUT, "exclusive-waiters.svg"), W, H,
           text(W / 2, 46, "Гримуча отара і виключні охочі: чому порядок у списку раптом важить",
                size=17, bold=True),
           *p)


# ── 5. Хто кого будить у модулі wqdemo ──────────────────────────────────────
def fig_wqdemo_flow():
    W, H = 1180, 690
    p = []

    cols = [(40, 250), (350, 250), (660, 190), (910, 230)]
    heads = ["хто діє", "що змінює в пристрої", "яку чергу будить", "хто прокинеться"]
    for (x, w), h in zip(cols, heads):
        p.append(text(x + w / 2, 122, h, size=13, color=MUTED, bold=True))

    rows = [
        (150, POS, WARM, ["write(2)\nз простору користувача",
                          "кладе байти\nв кільце", "readq", "читачі,\nщо стоять у read()"]),
        (262, POS, WARM, ["таймер\n(м'який контекст)",
                          "кладе байти\nв кільце", "readq", "читачі,\nщо стоять у read()"]),
        (374, NEG, COLD, ["read(2)", "звільняє місце\nв кільці",
                          "writeq", "письменники,\nщо стоять у write()"]),
        (486, MUTED, GREY, ["poll(2) / epoll", "не змінює\nнічого",
                            "нікого\nне будить", "poll_wait() лише\nреєструє запис\nу двох чергах"]),
    ]

    bh = 88
    for y, accent, fill, cells in rows:
        for (x, w), s in zip(cols, cells):
            p.append(fitbox(x, y, w, bh, s, size=12, fill=fill, stroke=accent))
        cy = y + bh / 2
        for (x1, w1), (x2, _) in zip(cols, cols[1:]):
            p.append(arrow(x1 + w1, cy, x2 - 6, cy, color=accent))

    p.append(fitbox(40, 600, 1100, 58,
                    "порядок незмінний: змінити кільце під замком · відпустити замок · "
                    "wq_has_sleeper() · будити",
                    size=13, fill=GREENF, stroke=FIELD))

    render(os.path.join(OUT, "wqdemo-flow.svg"), W, H,
           text(W / 2, 52, "Модуль wqdemo: три джерела подій, дві черги, один спін-замок",
                size=17, bold=True),
           *p)


fig_anatomy()
fig_lost_wakeup()
fig_wake_path()
fig_exclusive()
fig_wqdemo_flow()
print("ok")
