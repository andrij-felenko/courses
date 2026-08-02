# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

HOT  = "#fdecea"   # підсвітка «підозріле»
COLD = "#eef4ff"
GRN  = "#eafaf1"


# ── Фігура 1: зона підозри після червоного світла ────────────────────────────
def fig_suspicion_scope():
    W, H = 1060, 470
    frags = []

    panels = [
        (40,  "Наскрізний тест",     "all",  ["червоне світло →", "підозра: 2000 функцій"]),
        (380, "Тест групи модулів",  "band", ["червоне світло →", "підозра: ≈120 функцій"]),
        (720, "Модульний тест",      "one",  ["червоне світло →", "підозра: 1 функція"]),
    ]

    PW, PH = 300, 210
    PY = 120
    COLS, ROWS = 10, 6
    cw = (PW - 20) / COLS
    ch = (PH - 20) / ROWS

    for px, title, mode, caption in panels:
        frags.append(text(px + PW / 2, 100, title, size=15, bold=True))
        frags.append(rect(px, PY, PW, PH, fill=BG, stroke=MUTED, sw=1.6, rx=8))
        for r in range(ROWS):
            for c in range(COLS):
                if mode == "all":
                    hot = True
                elif mode == "band":
                    hot = r in (2, 3)
                else:
                    hot = (r == 3 and c == 6)
                x = px + 10 + c * cw
                y = PY + 10 + r * ch
                frags.append(rect(x + 1.5, y + 1.5, cw - 3, ch - 3,
                                  fill=HOT if hot else "#f0f1f3",
                                  stroke=POS if hot else "#d5d8dd",
                                  sw=1.4 if hot else 0.8, rx=3))
        frags.append(mtext(px + PW / 2, 372, caption, size=13, color=INK))

    frags.append(text(W / 2, 440,
                      "Спрацювання коштує однаково — різниться те, скільки роботи лишається після нього.",
                      size=14, bold=True, color=NEG))
    render(os.path.join(IMG, 'suspicion-scope.svg'), W, H, *frags,
           title="Скільки кандидатів лишається після червоного світла")


# ── Фігура 2: межа одиниці, шов і дублери ────────────────────────────────────
def fig_unit_boundary():
    W, H = 1080, 490
    frags = []

    # пунктирна межа «зони підозри»
    frags.append('<rect x="240" y="140" width="420" height="250" rx="10" '
                 'fill="#fbfcfd" stroke="%s" stroke-width="2" stroke-dasharray="8 6"/>' % NEG)
    frags.append(text(450, 126, "зона підозри при червоному світлі", size=13, color=NEG, bold=True))

    unit, uw, uh = textbox(450, 210,
                           ["Одиниця під тестом", "обіцянка: «дає розібрану дату", "або каже, що рядок хибний»"],
                           size=13, bold=False, fill=COLD, stroke=NEG, sw=2.4, pad=14)
    helper, hw, hh = textbox(450, 330, ["чистий помічник —", "лишаємо справжнім"],
                             size=13, fill=GRN, stroke=FIELD, sw=2, pad=12)

    tst, tw, th = textbox(120, 210, "Тест", size=15, bold=True, fill="#fff8e1",
                          stroke="#b8860b", sw=2.2, pad=14, min_w=140)
    frags.append(tst)
    ax1 = 120 + tw / 2 + 8
    ax2 = 450 - uw / 2 - 8
    frags.append(arrow(ax1, 210, ax2, 210, color="#b8860b", sw=2.4))
    frags.append(text((ax1 + ax2) / 2, 192, "вхід і результат", size=12, italic=True, color=MUTED))

    frags.append(unit)
    frags.append(helper)

    # шов
    frags.append(line(740, 150, 740, 400, color=FIELD, sw=2.2, dash="7 6"))
    frags.append(text(740, 136, "шов", size=13, bold=True, color=FIELD))

    doubles = [(180, "Дублер бази"), (265, "Дублер годинника"), (350, "Дублер мережі")]
    for dy, label in doubles:
        box, dw, dh = textbox(910, dy, label, size=13, fill=GRN, stroke=FIELD, sw=2,
                              pad=12, min_w=210)
        frags.append(arrow(450 + uw / 2 + 8, 210, 910 - 210 / 2 - 8, dy, color=FIELD, sw=1.8))
        frags.append(box)

    frags.append(text(W / 2, 455,
                      "Підміняють лише те, чим не можеш керувати або що повільне; чисту логіку лишають справжньою.",
                      size=14, bold=True, color=NEG))
    render(os.path.join(IMG, 'unit-boundary.svg'), W, H, *frags,
           title="Що лишається в зоні підозри, коли модульний тест червоніє")


# ── Фігура 3: тривалість набору й накопичені зміни ───────────────────────────
def fig_feedback_loop():
    W, H = 1060, 440
    frags = []

    N = 12
    X0, STEP, SQ = 90, 62, 24
    BAD = 7

    def row(y, label, runs_each, caption, note):
        out = [text(X0, y - 44, label, size=14, bold=True, anchor="start")]
        for i in range(N):
            x = X0 + i * STEP
            bad = (i == BAD)
            out.append(rect(x, y - SQ / 2, SQ, SQ,
                            fill=HOT if (bad and runs_each) else "#f0f1f3",
                            stroke=POS if (bad and runs_each) else "#c9ccd2",
                            sw=1.6 if (bad and runs_each) else 1.0, rx=4))
        if runs_each:
            for i in range(N):
                x = X0 + i * STEP + SQ / 2
                col = POS if i >= BAD else FIELD
                out.append(circle(x, y + 34, 7, fill="#fdecea" if i >= BAD else "#eafaf1",
                                  stroke=col, sw=2))
        else:
            x = X0 + (N - 1) * STEP + SQ / 2
            out.append(circle(x, y + 34, 9, fill="#fdecea", stroke=POS, sw=2.4))
        out.append(text(X0 + 260, y + 70, note, size=12, italic=True, color=MUTED, anchor="start"))
        box, bw, bh = textbox(950, y, caption, size=13, bold=True, fill=COLD,
                              stroke=NEG, sw=2, pad=12, min_w=190)
        out.append(box)
        return out

    frags += row(160, "Набір іде 8 с — женеш після кожної зміни", True,
                 ["зона підозри:", "1 зміна"], "прогін після кожної зміни")
    frags += row(320, "Набір іде 40 хв — женеш раз на день", False,
                 ["зона підозри:", "12 змін"], "єдиний прогін — наприкінці")

    render(os.path.join(IMG, 'feedback-loop.svg'), W, H, *frags,
           title="Скільки твоїх змін накопичується між двома сигналами")


# ── Фігура 4: миготіння вбиває сигнал ────────────────────────────────────────
def fig_flaky_signal():
    W, H = 1000, 570
    X0, X1 = 150, 880          # n від 100 до 10000 (лог. шкала)
    YT, YB = 150, 470          # p від 1 до 0
    frags = []

    def px(n):
        return X0 + (math.log10(n) - 2.0) / 2.0 * (X1 - X0)

    def py(p):
        return YB - p * (YB - YT)

    # осі
    frags.append(line(X0, YT, X0, YB, color=INK, sw=1.8))
    frags.append(line(X0, YB, X1, YB, color=INK, sw=1.8))

    for n in (100, 300, 1000, 3000, 10000):
        x = px(n)
        frags.append(line(x, YB, x, YB + 7, color=INK, sw=1.4))
        frags.append(text(x, YB + 26, "{:,}".format(n).replace(",", " "), size=12, color=MUTED))
    for p in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = py(p)
        frags.append(line(X0 - 7, y, X0, y, color=INK, sw=1.4))
        frags.append(line(X0, y, X1, y, color="#e6e8ec", sw=1.0))
        frags.append(text(X0 - 16, y + 4, "%.2f" % p, size=12, color=MUTED, anchor="end"))

    curves = [(0.0001, NEG), (0.001, "#8e44ad"), (0.01, POS)]
    for f, col in curves:
        pts = []
        for k in range(0, 121):
            n = 10 ** (2.0 + 2.0 * k / 120.0)
            pts.append((px(n), py((1.0 - f) ** n)))
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            frags.append(line(x1, y1, x2, y2, color=col, sw=2.6))

    for cx, (f, col), label in zip((260, 520, 780), curves,
                                   ("миготіння 0.01 %", "миготіння 0.1 %", "миготіння 1 %")):
        box, bw, bh = textbox(cx, 105, label, size=13, bold=True, fill=BG, stroke=col, sw=2.6, pad=12)
        frags.append(box)

    frags.append(text((X0 + X1) / 2, YB + 62, "кількість тестів у наборі (логарифмічна шкала)",
                      size=13, color=INK))
    frags.append(text((X0 + X1) / 2, YB + 90,
                      "Одне миготіння на тисячу прогонів — і набір із 5000 тестів зелений менш ніж у 1 % випадків.",
                      size=13, bold=True, color=NEG))

    render(os.path.join(IMG, 'flaky-signal.svg'), W, H, *frags,
           title="Імовірність зеленого прогону цілком справного набору")


# ── Фігура 5 (вставка hist): від разового прогону до постійного артефакту ────
def fig_xunit_timeline():
    W, H = 1060, 700
    frags = []

    frags.append(text(W / 2, 46, "Від разового прогону до постійного артефакту",
                      size=17, bold=True))

    rows = [
        ("кінець 1950-х",
         "Тест — крок роботи: прогін і звірка з очікуваним\n"
         "результатом; готового діла після себе не лишає"),
        ("жовтень 1994",
         "SUnit: TestCase, TestSuite, TestResult\n"
         "стаття «Simple Smalltalk Testing», Smalltalk Report"),
        ("жовтень 1997",
         "JUnit: SUnit переписано на Java в літаку\n"
         "Цюрих → OOPSLA в Атланті (Бек і Гамма)"),
        ("липень 1998",
         "«Test Infected», Java Report: звичай пояснено\n"
         "масовій аудиторії Java"),
        ("1999",
         "«Extreme Programming Explained»: тест —\n"
         "несуча деталь процесу, а не особиста чеснота"),
        ("2000-і",
         "Родина xUnit: CppUnit, NUnit, PyUnit та інші —\n"
         "той самий кістяк у десятках мов"),
    ]

    AX = 292
    y0, step = 122, 95
    frags.append(line(AX, y0 - 32, AX, y0 + step * (len(rows) - 1) + 32,
                      color=MUTED, sw=2.2))

    for i, (when, what) in enumerate(rows):
        cy = y0 + step * i
        frags.append(text(252, cy + 5, when, size=15, bold=True, anchor="end"))
        frags.append(circle(AX, cy, 9, fill=BG, stroke=INK, sw=2.4))
        frags.append(fitbox(332, cy - 34, 686, 68, what, size=14,
                            fill=COLD if i >= 1 else FILL, stroke=MUTED, sw=1.6))

    frags.append(text(W / 2, H - 30,
                      "Ліворуч від 1994-го тест живе рівно стільки, скільки триває прогін; "
                      "праворуч — лежить у репозиторії поруч із кодом.",
                      size=13, color=INK))

    render(os.path.join(IMG, 'xunit-timeline.svg'), W, H, *frags,
           title="Хронологія: SUnit, JUnit, родина xUnit")


# ── Фігура 6 (вставка hist): кістяк SUnit — три класи ────────────────────────
def fig_sunit_parts():
    W, H = 1080, 620
    frags = []

    frags.append(text(W / 2, 44, "Кістяк SUnit: три класи, з яких виріс увесь xUnit",
                      size=17, bold=True))

    frags.append(rect(50, 78, 620, 404, fill=BG, stroke=INK, sw=2))
    frags.append(text(70, 106, "TestSuite — набір тестів як один об'єкт",
                      size=14, bold=True, anchor="start"))

    cases = [
        "TestCase: порожній рядок",
        "TestCase: правильна дата",
        "TestCase: 31 лютого",
    ]
    for i, name in enumerate(cases):
        y = 128 + i * 112
        frags.append(rect(80, y, 560, 92, fill=FILL, stroke=MUTED, sw=1.6))
        frags.append(text(100, y + 26, name, size=13, bold=True, anchor="start"))
        cy = y + 62
        for cx, label in ((170, "setUp"), (330, "перевірка"), (505, "tearDown")):
            box, bw, bh = textbox(cx, cy, label, size=12, fill=BG, stroke=INK, sw=1.6, pad=10)
            frags.append(box)
        frags.append(arrow(215, cy, 273, cy, color=MUTED, sw=1.6))
        frags.append(arrow(388, cy, 448, cy, color=MUTED, sw=1.6))

    frags.append(arrow(672, 280, 726, 280, color=INK, sw=2.2))

    frags.append(rect(732, 168, 300, 224, fill=BG, stroke=INK, sw=2))
    frags.append(text(882, 200, "TestResult", size=15, bold=True))
    frags.append(mtext(882, 240, ["прогнали: 3", "впало: 1", "зламалося: 0"],
                       size=13, lh=1.5))
    frags.append(rect(760, 312, 244, 46, fill=HOT, stroke=POS, sw=2))
    frags.append(text(882, 341, "вердикт: ЧЕРВОНО", size=14, bold=True, color=POS))

    frags.append(text(W / 2, 540,
                      "Тест — об'єкт, набір — об'єкт, вердикт — об'єкт.",
                      size=14, bold=True))
    frags.append(text(W / 2, 570,
                      "Саме тому прогін став машинним, а висновок — однією відповіддю замість читання роздруку.",
                      size=13))

    render(os.path.join(IMG, 'sunit-parts.svg'), W, H, *frags,
           title="Кістяк SUnit: TestCase, TestSuite, TestResult")


# ── Фігура (вставка proj): мить помилки «на одиницю» ─────────────────────────
def fig_off_by_one():
    W, H = 1120, 640
    frags = []

    CW, CH, GAP = 104, 62, 6
    X0 = 300

    def panel(ytop, heading, sub, cells, hot, notes, verdict, vcolor, tail_line):
        out = [text(60, ytop, heading, size=16, bold=True, anchor="start", color=vcolor)]
        out.append(text(60, ytop + 26, sub, size=13, color=MUTED, anchor="start"))
        cy = ytop + 62
        for i, val in enumerate(cells):
            x = X0 + i * (CW + GAP)
            out.append(text(x + CW / 2, cy - 8, str(i), size=11, color=MUTED))
            out.append(rect(x, cy, CW, CH,
                            fill="#fdecea" if i in hot else "#eef4ff",
                            stroke=POS if i in hot else NEG,
                            sw=2.4 if i in hot else 1.6, rx=6))
            out.append(text(x + CW / 2, cy + CH / 2 + 7, str(val), size=18, bold=True,
                            color=POS if i in hot else INK))
        for i, note in notes:
            x = X0 + i * (CW + GAP) + CW / 2
            out.append(text(x, cy + CH + 22, note, size=12, color=MUTED))
        box, bw, bh = textbox(940, cy + CH / 2, verdict, size=13, bold=True,
                              fill=BG, stroke=vcolor, sw=2.4, pad=13, color=vcolor)
        out.append(box)
        out.append(text(60, cy + CH + 62, tail_line, size=14, anchor="start", color=INK))
        return out

    frags += panel(
        100,
        "Правильно:  if (r->count >= RB_CAP) return false;",
        "у буфері лежать чотири елементи — по вінця, місткість вичерпано",
        [10, 20, 30, 40], set(),
        [(0, "head = tail = 0")],
        ["push(50) → false", "count лишився 4", "вміст не змінився"], FIELD,
        "pop × 5  →  10, 20, 30, 40, потім відмова.   Порядок надходження збережено.")

    frags += panel(
        390,
        "Помилка на одиницю:  if (r->count > RB_CAP) return false;",
        "той самий стан, той самий п'ятий push — але перевірка пропускає його всередину",
        [50, 20, 30, 40], {0},
        [(0, "tail = 0,  тут було 10"), (1, "head = 1")],
        ["push(50) → true", "count = 5 > RB_CAP", "найстаріше значення затерто"], POS,
        "pop × 5  →  50, 20, 30, 40, знову 50.   Один елемент зник, інший видано двічі.")

    frags.append(text(W / 2, 618,
                      "Один знак порівняння: ні виходу за межі масиву, ні падіння — "
                      "лише тихо зіпсована обіцянка.",
                      size=14, bold=True, color=INK))
    render(os.path.join(IMG, 'off-by-one-moment.svg'), W, H, *frags,
           title="Мить, коли «>» замість «>=» пускає в буфер зайвий елемент")


# ── Фігура (вставка proj): що робить каркас із кожним тестом ─────────────────
def fig_harness_anatomy():
    W, H = 1120, 500
    frags = []

    CHAIN_Y = 180

    tbl, tw, th = textbox(150, CHAIN_Y,
                          ["Таблиця тестів — масив",
                           "{ «новий буфер порожній», fn }",
                           "{ «push у повний відмовляє», fn }",
                           "… ще п'ять рядків …"],
                          size=13, fill=FILL, stroke=INK, sw=1.8, pad=13)
    frags.append(tbl)

    chain = [
        (440, ["свіжий rb_t", "на стеку"]),
        (610, ["t0 = монотонний", "годинник"]),
        (790, ["setjmp —", "точка повернення"]),
        (960, ["виклик", "тіла тесту"]),
    ]
    widths = {}
    for cx, lines in chain:
        box, bw, bh = textbox(cx, CHAIN_Y, lines, size=13, fill=COLD, stroke=NEG, sw=2, pad=12)
        widths[cx] = bw
        frags.append(box)

    prev_right = 150 + tw / 2
    for cx, _ in chain:
        frags.append(arrow(prev_right + 8, CHAIN_Y, cx - widths[cx] / 2 - 8, CHAIN_Y,
                           color=NEG, sw=2))
        prev_right = cx + widths[cx] / 2

    fail, fw, fh = textbox(500, 340,
                           ["CHECK хибний → longjmp",
                            "[FAIL] push у повний відмовляє",
                            "rb_test.c:74: маємо 99, чекали 10"],
                           size=13, fill="#fdecea", stroke=POS, sw=2.4, pad=13)
    ok, ow, oh = textbox(900, 340,
                         ["тіло дійшло до кінця",
                          "[ OK ] 0.6 мкс"],
                         size=13, fill=GRN, stroke=FIELD, sw=2.4, pad=13)
    frags.append(fail)
    frags.append(ok)

    frags.append(arrow(930, CHAIN_Y + 26, 600, 340 - fh / 2 - 6, color=POS, sw=2))
    frags.append(arrow(975, CHAIN_Y + 26, 905, 340 - oh / 2 - 6, color=FIELD, sw=2))

    RET = 252
    frags.append(line(500 - fw / 2, 340, 320, 340, color=POS, sw=2, dash="7 5"))
    frags.append(line(320, 340, 320, RET, color=POS, sw=2, dash="7 5"))
    frags.append(line(320, RET, 750, RET, color=POS, sw=2, dash="7 5"))
    frags.append(arrow(750, RET, 750, CHAIN_Y + 26, color=POS, sw=2))
    frags.append(text(535, RET - 11, "longjmp повертає точно сюди", size=12,
                      color=POS, bold=True))

    frags.append(text(W / 2, 430,
                      "Жодної магії: таблиця — звичайний масив, ізоляція — стек, звіт — printf.",
                      size=14, bold=True, color=INK))
    frags.append(text(W / 2, 458,
                      "Ключ --shuffle <зерно> міняє лише порядок обходу таблиці — і цим ловить "
                      "стан, що протік між тестами.",
                      size=13, color=MUTED))
    render(os.path.join(IMG, 'harness-anatomy.svg'), W, H, *frags,
           title="Що каркас робить із кожним тестом")


if __name__ == '__main__':
    fig_suspicion_scope()
    fig_unit_boundary()
    fig_feedback_loop()
    fig_flaky_signal()
    fig_xunit_timeline()
    fig_sunit_parts()
    fig_off_by_one()
    fig_harness_anatomy()
    print("ok")
