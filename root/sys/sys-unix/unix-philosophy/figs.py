# -*- coding: utf-8 -*-
"""Фігури до теми «Філософія Unix: малі програми, що складаються»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def tb(*a, **kw):
    """textbox, але повертає лише svg-фрагмент."""
    body, w, h = textbox(*a, **kw)
    return body


def box_span(cx, s, size=14, pad=10, bold=False, min_w=0):
    """Ширина рамки, яку побудує textbox — щоб рахувати краї для стрілок."""
    lines = s.split("\n") if isinstance(s, str) else list(s)
    tw = max(text_width(ln, size, bold) for ln in lines)
    w = max(min_w, tw + 2 * pad)
    return cx - w / 2, cx + w / 2


# ── 1. Чому складання дешевше за перелік ────────────────────────────────────
def fig_composition():
    W, H = 1000, 460
    f = []
    # ліва панель
    f.append(rect(30, 50, 440, 370, fill="#ffffff", stroke=MUTED, sw=1.2))
    f.append(text(250, 82, "Моноліт на кожну задачу", size=15, bold=True))
    for i, s in enumerate(["програма A → задача 1",
                           "програма B → задача 2",
                           "програма C → задача 3",
                           "програма D → задача 4"]):
        f.append(tb(250, 130 + i * 52, s, size=13))
    f.append(text(250, 370, "4 програми = 4 задачі", size=14, color=NEG, bold=True))
    f.append(text(250, 398, "нова задача → новий код", size=13, color=MUTED))

    # права панель
    f.append(rect(530, 50, 440, 370, fill="#ffffff", stroke=MUTED, sw=1.2))
    f.append(text(750, 82, "Фільтри, що складаються", size=15, bold=True))
    for i, s in enumerate("ABCD"):
        f.append(tb(600 + i * 100, 130, s, size=14, bold=True, min_w=64))
    f.append(text(750, 196, "приклади ланцюжків:", size=13, color=MUTED))
    for i, s in enumerate(["A → C → B", "C → A → D", "B → D → A"]):
        f.append(text(750, 226 + i * 28, s, size=14))
    f.append(text(750, 342, "4 фільтри, ланцюжок із 3 ланок:", size=13, color=MUTED))
    f.append(text(750, 370, "4³ = 64 різні конвеєри", size=14, color=FIELD, bold=True))
    f.append(text(750, 398, "нова задача → новий рядок", size=13, color=MUTED))

    render(os.path.join(IMG, 'composition-vs-monolith.svg'), W, H, *f,
           title="Вартість росте як кількість частин, покриття — як їх сполучення")


# ── 2. Анатомія конвеєра ────────────────────────────────────────────────────
def fig_pipeline_anatomy():
    W, H = 1000, 500
    f = []
    shell = "оболонка: pipe() + fork() + dup2() + exec()"
    sl, sr = box_span(500, shell, size=14)
    f.append(tb(500, 72, shell, size=14))

    p1 = "процес A\n(наприклад, tr)"
    p2 = "процес B\n(наприклад, sort)"
    buf = "канал у ядрі\nбуфер ≈64 КіБ"
    a_l, a_r = box_span(220, p1, size=14)
    b_l, b_r = box_span(780, p2, size=14)
    c_l, c_r = box_span(500, buf, size=14)
    f.append(tb(220, 210, p1, size=14))
    f.append(tb(780, 210, p2, size=14))
    f.append(tb(500, 210, buf, size=14, fill="#eef7f0", stroke=FIELD))

    # запуск з оболонки
    f.append(arrow(430, 98, 250, 178, color=MUTED, sw=1.4))
    f.append(arrow(570, 98, 750, 178, color=MUTED, sw=1.4))

    # потік даних
    f.append(arrow(a_r + 6, 210, c_l - 6, 210))
    f.append(arrow(c_r + 6, 210, b_l - 6, 210))
    f.append(text((a_r + c_l) / 2, 190, "fd 1 — запис", size=12, color=MUTED))
    f.append(text((c_r + b_l) / 2, 190, "fd 0 — читання", size=12, color=MUTED))

    # зворотний тиск
    f.append(arrow(c_l - 6, 262, a_r + 6, 262, color=POS, sw=1.6))
    f.append(text((a_r + c_l) / 2, 288, "буфер повний → write чекає", size=12, color=POS))

    # stderr в обхід
    f.append(line(a_l - 60, 240, a_l - 60, 400, color=MUTED, sw=1.4, dash="5,4"))
    f.append(line(b_r + 60, 240, b_r + 60, 400, color=MUTED, sw=1.4, dash="5,4"))
    f.append(line(a_l - 60, 240, a_l, 240, color=MUTED, sw=1.4, dash="5,4"))
    f.append(line(b_r + 60, 240, b_r, 240, color=MUTED, sw=1.4, dash="5,4"))
    term = "термінал"
    tl, tr = box_span(500, term, size=14)
    f.append(tb(500, 400, term, size=14))
    f.append(arrow(a_l - 60, 400, tl - 6, 400, color=MUTED, sw=1.4))
    f.append(arrow(b_r + 60, 400, tr + 6, 400, color=MUTED, sw=1.4))
    f.append(text(a_l - 72, 330, "fd 2", size=12, color=MUTED, anchor="end"))
    f.append(text(b_r + 72, 330, "fd 2", size=12, color=MUTED, anchor="start"))
    f.append(text(500, 452, "діагностика йде повз конвеєр — інакше вона стала б даними для B",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'pipeline-anatomy.svg'), W, H, *f,
           title="Що саме з'єднує конвеєр")


# ── 3. Час і пам'ять: тимчасовий файл проти конвеєра ────────────────────────
def fig_time_and_memory():
    W, H = 960, 450
    f = []
    f.append(text(40, 76, "через тимчасовий файл", size=15, bold=True, anchor="start"))
    f.append(fitbox(140, 92, 260, 36, "A пише у файл", size=13, fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(420, 92, 260, 36, "B читає файл", size=13, fill="#eaf0fd", stroke=NEG))
    f.append(text(40, 158, "B стартує лише після A; диск тримає весь проміжний обсяг",
                  size=13, color=MUTED, anchor="start"))

    f.append(text(40, 226, "конвеєр", size=15, bold=True, anchor="start"))
    f.append(fitbox(140, 242, 420, 32, "A пише в канал", size=13, fill="#eef7f0", stroke=FIELD))
    f.append(fitbox(200, 286, 420, 32, "B читає з каналу", size=13, fill="#eef7f0", stroke=FIELD))
    f.append(text(40, 348, "обидва процеси живі водночас; у пам'яті — лише буфер каналу",
                  size=13, color=MUTED, anchor="start"))

    f.append(arrow(40, 396, 900, 396, color=INK, sw=1.5))
    f.append(text(880, 422, "час", size=13, color=MUTED))

    render(os.path.join(IMG, 'pipe-time-and-memory.svg'), W, H, *f,
           title="Конвеєр не зберігає проміжний результат — він його передає")


# ── 4. Режим буферизації stdout залежить від того, куди він дивиться ────────
def fig_buffering_modes():
    W, H = 1020, 480
    f = []
    ticks = [400, 560, 720, 890]
    labels = ["1 с", "2 с", "3 с", "вихід"]

    f.append(tb(190, 118, "stdout → термінал\nрежим: порядковий",
                size=13, fill="#eef7f0", stroke=FIELD))
    for i in range(3):
        f.append(tb(ticks[i], 135, "рядок %d" % (i + 1), size=13, min_w=96))
    f.append(text(890, 140, "усе вже там", size=12, color=MUTED))

    f.append(line(30, 218, 990, 218, color=MUTED, sw=1.0, dash="4,4"))

    f.append(tb(190, 288, "stdout → канал або файл\nрежим: поблоковий, ≈4 КіБ",
                size=13, fill="#fdecea", stroke=POS))
    f.append(text(560, 300, "нічого не видно", size=13, color=POS))
    f.append(tb(890, 305, "усі рядки\nвивалюються разом", size=13, min_w=96))

    f.append(arrow(340, 400, 980, 400, color=INK, sw=1.5))
    for x, s in zip(ticks, labels):
        f.append(line(x, 393, x, 407, color=INK, sw=1.5))
        f.append(text(x, 428, s, size=12, color=MUTED))
    f.append(text(500, 462,
                  "той самий код і той самий вивід — різниця лише в тому, куди дивиться fd 1",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'filter-buffering-modes.svg'), W, H, *f,
           title="Чому вивід «зависає», щойно програму поставили в конвеєр")


# ── 5. Запис у канал без читача: дві гілки ──────────────────────────────────
def fig_sigpipe_branch():
    W, H = 1000, 450
    f = []
    f.append(tb(500, 72, "write() у канал, чий читач уже закрився", size=14))
    f.append(arrow(450, 92, 280, 146))
    f.append(arrow(550, 92, 720, 146))

    f.append(tb(250, 175, "диспозиція SIGPIPE:\nтипова дія", size=13,
                fill="#fdecea", stroke=POS))
    f.append(tb(750, 175, "SIGPIPE ігнорується\nабо має обробник", size=13,
                fill="#eaf0fd", stroke=NEG))

    f.append(arrow(250, 201, 250, 244))
    f.append(arrow(750, 201, 750, 244))

    f.append(tb(250, 272, "процес гине від сигналу 13\nwrite() не повертається", size=13))
    f.append(tb(750, 272, "write() повертає −1,\nerrno = EPIPE (32 на Linux)", size=13))

    f.append(arrow(250, 298, 250, 341))
    f.append(arrow(750, 298, 750, 341))

    f.append(tb(250, 369, "оболонка звітує 141 = 128+13,\nконвеєр згортається сам", size=13))
    f.append(tb(750, 369, "ваш код мусить помітити EPIPE\nі тихо вийти — це не ваша помилка", size=13))

    f.append(text(500, 434,
                  "саме ліва гілка робить «… | head -1» миттєвим на гігабайтному вході",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'filter-sigpipe-branch.svg'), W, H, *f,
           title="Що станеться, коли наступна ланка пішла раніше за вас")


# ── Три шари історії: ідея, реалізація, формулювання ────────────────────────
def fig_birth_timeline():
    W, H = 1240, 570
    f = []

    col_w, gut = 255, 8
    col_x = [180 + i * (col_w + gut) for i in range(4)]
    col_c = [x + col_w / 2 for x in col_x]
    for cx, s in zip(col_c, ["1964", "1969–1971", "1972–1973", "1978–1984"]):
        f.append(text(cx, 78, s, size=15, bold=True, color=MUTED))

    row_y, row_h = [104, 250, 396], 130
    for y, s in zip(row_y, ["ІДЕЯ", "РЕАЛІЗАЦІЯ", "ФОРМУЛЮВАННЯ"]):
        f.append(fitbox(20, y, 150, row_h, s, size=15, bold=True,
                        fill="#eef1f5", stroke=MUTED))

    LITE = "#fbfbfc"

    def cell(r, c, s=None, accent=False):
        x, y = col_x[c], row_y[r]
        if s is None:
            return rect(x, y, col_w, row_h, fill=LITE, stroke="#dcdfe4",
                        sw=1.0, rx=6)
        if accent:
            return fitbox(x, y, col_w, row_h, s, size=13,
                          fill="#eef7f0", stroke=FIELD)
        return fitbox(x, y, col_w, row_h, s, size=12,
                      fill=LITE, stroke="#dcdfe4", sw=1.0, color=MUTED)

    f.append(cell(0, 0, "11 жовтня 1964\nзаписка Макілроя:\nз'єднувати програми\n«як садові шланги»",
                  accent=True))
    f.append(cell(0, 1, "ідея відома,\nале нема на чому\nїї втілити"))
    f.append(cell(0, 2, "Макілрой умовляє\nТомпсона"))
    f.append(cell(0, 3))

    f.append(cell(1, 0))
    f.append(cell(1, 1, "1969 — вихід із Multics\nPDP-7: перший Unix,\nфайлова система, оболонка",
                  accent=True))
    f.append(cell(1, 2, "1972 — V2: каналів ще нема\n1973 — V3: канал є,\nсинтаксис через знак >\n1973 — V4: символ |",
                  accent=True))
    f.append(cell(1, 3))

    f.append(cell(2, 0))
    f.append(cell(2, 1))
    f.append(cell(2, 2, "практика вже склалася,\nа назви для неї ще нема"))
    f.append(cell(2, 3, "1978 — передмова в BSTJ:\nчотири настанови\n1983 — доповідь Пайка\n1984 — стаття Пайка\nй Керніґана",
                  accent=True))

    f.append(text(W / 2, 552,
                  "ідея, механізм і формулювання розділені чотирнадцятьма роками — і саме в такому порядку",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'philosophy-birth-timeline.svg'), W, H, *f,
           title="Три шари, що не збіглися в часі")


# ── Реєстр кінців каналу: коли лічильник дійде до нуля ──────────────────────
def fig_fd_ledger():
    W, H = 1060, 640
    f = []

    x_step, x_who, x_cnt = 45, 430, 960

    f.append(text(x_step, 70, "крок", size=13, color=MUTED, bold=True, anchor="start"))
    f.append(text(x_who, 70, "хто тримає кінець запису", size=13, color=MUTED,
                  bold=True, anchor="start"))
    f.append(text(x_cnt, 70, "разом", size=13, color=MUTED, bold=True))
    f.append(line(40, 86, 1020, 86, color=MUTED, sw=1.2))

    rows = [
        ("pipe(p)",             "батько",              "1", MUTED),
        ("fork() — ланка A",    "батько, A",           "2", MUTED),
        ("A: dup2(p[1], 1)",    "батько, A (як fd 1)", "2", MUTED),
        ("fork() — ланка B",    "батько, A (fd 1), B", "3", MUTED),
        ("B: close(p[1])",      "батько, A (fd 1)",    "2", MUTED),
        ("батько: close(p[1])", "A (fd 1)",            "1", INK),
        ("A завершилася",       "— нікого —",          "0", FIELD),
    ]
    for i, (a, b, c, col) in enumerate(rows):
        y = 124 + i * 52
        f.append(text(x_step, y, a, size=13, anchor="start"))
        f.append(text(x_who, y, b, size=13, anchor="start"))
        f.append(text(x_cnt, y, c, size=18, color=col, bold=True))

    f.append(text(x_who, 536, "→ read() у ланки B повертає 0: це і є EOF",
                  size=13, color=FIELD, anchor="start"))

    warn = ("пропустити крок «батько: close(p[1])» — і лічильник застрягає на 1:\n"
            "ланка B чекає на дані, яких уже ніхто не надішле")
    f.append(tb(530, 592, warn, size=13, fill="#fdecea", stroke=POS, color=POS))

    render(os.path.join(IMG, 'pipe-fd-ledger.svg'), W, H, *f,
           title="Скільки дескрипторів указують на кінець ЗАПИСУ")


# ── Інваріант циклу, що збирає ланцюжок із N ланок ──────────────────────────
def fig_loop_invariant():
    W, H = 1060, 470
    f = []

    f.append(tb(530, 78, "батько: pipe() → fork() → закрити зайве", size=14))
    f.append(arrow(430, 97, 250, 161, color=MUTED, sw=1.4))
    f.append(arrow(530, 97, 530, 161, color=MUTED, sw=1.4))
    f.append(arrow(630, 97, 810, 161, color=MUTED, sw=1.4))

    kids = [
        (220, "ланка 1\nввід — свій\nвивід → канал 1"),
        (530, "ланка 2\nввід ← канал 1\nвивід → канал 2"),
        (840, "ланка 3 (остання)\nввід ← канал 2\nвивід — свій"),
    ]
    edges = []
    for cx, s in kids:
        edges.append(box_span(cx, s, size=13))
        f.append(tb(cx, 210, s, size=13, fill="#eef7f0", stroke=FIELD))

    for i, name in enumerate(("канал 1", "канал 2")):
        x1, x2 = edges[i][1] + 10, edges[i + 1][0] - 10
        f.append(arrow(x1, 210, x2, 210))
        f.append(text((x1 + x2) / 2, 188, name, size=12, color=MUTED))
        f.append(text((x1 + x2) / 2, 240, "p[0] стає prev", size=11, color=MUTED))

    f.append(text(45, 266, "після fork() батько:", size=12, color=MUTED, anchor="start"))
    acts = [
        (220, "закрив p[1];\nprev = p[0]"),
        (530, "закрив старий prev і p[1];\nprev = p[0]"),
        (840, "закрив prev;\nканалу не створював"),
    ]
    for cx, s in acts:
        f.append(tb(cx, 312, s, size=12, color=MUTED, stroke=MUTED))

    f.append(text(530, 398,
                  "інваріант: у батька в руках рівно один цікавий дескриптор — "
                  "prev, читальний кінець останнього створеного каналу", size=13))
    f.append(text(530, 428,
                  "тому довжина ланцюжка не змінює того, скільки дескрипторів "
                  "відкрито одночасно", size=12, color=MUTED))

    render(os.path.join(IMG, 'pipeline-loop-invariant.svg'), W, H, *f,
           title="Одна ітерація циклу: канал з'являється, prev переїжджає")


if __name__ == '__main__':
    fig_composition()
    fig_pipeline_anatomy()
    fig_time_and_memory()
    fig_buffering_modes()
    fig_sigpipe_branch()
    fig_birth_timeline()
    fig_fd_ledger()
    fig_loop_invariant()
    print("ok")
