# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COLD = "#eaf0fd"
GREENFILL = "#eafaf1"


# ── 1. Два набори бітів і рішення на межі ───────────────────────────────────
def fig_two_sets():
    W, H = 1080, 660
    p = []

    # набір очікуваних
    p.append(rect(50, 70, 420, 150, fill=WARM, stroke=POS, sw=2, rx=8))
    p.append(text(260, 98, "НАБІР ОЧІКУВАНИХ", size=14, color=POS, bold=True))
    p.append(text(260, 120, "що вже надійшло і ще не опрацьовано", size=12, color=INK))
    cells = ["INT", "TERM", "HUP", "CHLD", "USR1"]
    bits1 = [1, 1, 0, 1, 0]
    for i, (nm, b) in enumerate(zip(cells, bits1)):
        x = 74 + i * 76
        p.append(rect(x, 142, 62, 56, fill=BG, stroke=POS if b else MUTED, sw=1.6, rx=5))
        p.append(text(x + 31, 166, nm, size=11, color=MUTED))
        p.append(text(x + 31, 188, "1" if b else "0", size=15,
                      color=POS if b else MUTED, bold=True))

    # маска заблокованих
    p.append(rect(50, 262, 420, 150, fill=COLD, stroke=NEG, sw=2, rx=8))
    p.append(text(260, 290, "МАСКА ЗАБЛОКОВАНИХ", size=14, color=NEG, bold=True))
    p.append(text(260, 312, "що програма попросила поки не доправляти", size=12, color=INK))
    bits2 = [1, 1, 0, 0, 0]
    for i, (nm, b) in enumerate(zip(cells, bits2)):
        x = 74 + i * 76
        p.append(rect(x, 334, 62, 56, fill=BG, stroke=NEG if b else MUTED, sw=1.6, rx=5))
        p.append(text(x + 31, 358, nm, size=11, color=MUTED))
        p.append(text(x + 31, 380, "1" if b else "0", size=15,
                      color=NEG if b else MUTED, bold=True))

    # обчислення на межі
    p.append(arrow(486, 148, 556, 216, color=MUTED, sw=1.6))
    p.append(arrow(486, 336, 556, 268, color=MUTED, sw=1.6))
    p.append(rect(560, 196, 470, 92, fill=GREENFILL, stroke=FIELD, sw=2, rx=8))
    p.append(text(795, 224, "на межі повернення в простір користувача", size=13,
                  color=FIELD, bold=True))
    p.append(text(795, 254, "доправити можна лише: очікувані І НЕ заблоковані", size=12.5, color=INK))
    p.append(text(795, 274, "тут це рівно один сигнал — CHLD", size=12, color=INK, bold=True))

    # три долі
    p.append(arrow(795, 292, 795, 336, color=FIELD, sw=1.8))
    p.append(fitbox(560, 340, 220, 96,
                    "CHLD — доправляють\nобробник або типова дія\n(біт очікування знімають)",
                    size=12, fill=GREENFILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(810, 340, 220, 96,
                    "INT, TERM — лежать далі\nнічого не втрачено,\nчекають на зняття маски",
                    size=12, fill=COLD, stroke=NEG, sw=1.8))

    p.append(rect(50, 470, 980, 130, fill=SOFT, stroke=MUTED, sw=1.6, rx=8))
    p.append(text(540, 500, "Блокування — це не ігнорування", size=14, color=INK, bold=True))
    p.append(mtext(78, 528,
                   ["Заблокований сигнал зберігає свій біт у наборі очікуваних: щойно маску знімуть,",
                    "його доправлять негайно. Диспозиція «ігнорувати» (SIG_IGN) робить протилежне —",
                    "сигнал доходить до доправлення й там його викидають назавжди.",
                    "Обидва набори — бітові карти однакової форми, тож звичайний сигнал, поки лежить",
                    "заблокований, повторами не накопичується: другий такий самий просто зливається з першим."],
                   size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "two-sets.svg"), W, H, *p,
           title="Що ядро вирішує щоразу, повертаючи керування програмі")


# ── 2. Вікно між перевіркою й засинанням ────────────────────────────────────
def fig_race_window():
    W, H = 1080, 620
    p = []

    # верхня доріжка — наївний код
    p.append(rect(40, 62, 1000, 210, fill=WARM, stroke=POS, sw=2, rx=8))
    p.append(text(540, 90, "Перевірити прапорець, потім заснути — між ними є щілина", size=14,
                  color=POS, bold=True))
    p.append(line(90, 176, 960, 176, color=INK, sw=1.8))
    p.append(text(1000, 180, "час", size=12, color=MUTED, anchor="start"))
    marks = [(150, "перевірка\nprapor == 0", -1), (430, "щілина", 1), (700, "pause()\nзасинає", -1)]
    for x, lbl, side in marks:
        p.append(line(x, 168, x, 184, color=INK, sw=1.6))
        if side < 0:
            p.append(mtext(x, 132, lbl, size=12, color=INK))
        else:
            p.append(mtext(x, 210, lbl, size=12, color=MUTED))
    p.append(arrow(430, 246, 430, 194, color=POS, sw=2))
    p.append(text(430, 264, "сигнал приходить саме тут: обробник ставить прапорець і виходить",
                  size=12, color=POS))
    p.append(text(830, 138, "спить, доки не прийде", size=12, color=POS, bold=True))
    p.append(text(830, 158, "НАСТУПНИЙ сигнал", size=12, color=POS, bold=True))

    # нижня доріжка — під маскою
    p.append(rect(40, 318, 1000, 240, fill=COLD, stroke=NEG, sw=2, rx=8))
    p.append(text(540, 346, "Під маскою щілини немає: засинання й зняття маски — одна дія", size=14,
                  color=NEG, bold=True))
    p.append(line(90, 432, 960, 432, color=INK, sw=1.8))
    p.append(text(1000, 436, "час", size=12, color=MUTED, anchor="start"))
    marks2 = [(150, "заблокувати\nINT"), (360, "перевірка\nprapor == 0"), (620, "sigsuspend():\nзняти маску + заснути")]
    for x, lbl in marks2:
        p.append(line(x, 424, x, 440, color=INK, sw=1.6))
        p.append(mtext(x, 392, lbl, size=12, color=INK))
    p.append(arrow(470, 502, 470, 450, color=NEG, sw=2))
    p.append(text(470, 522, "сигнал приходить тут — але заблокований, тож лише лягає в очікувані",
                  size=12, color=NEG))
    p.append(text(800, 470, "sigsuspend знімає маску вже зсередини сну:", size=12, color=NEG,
                  anchor="middle"))
    p.append(text(800, 490, "накопичене доправляють негайно, сон уривається", size=12, color=NEG))

    render(os.path.join(OUT, "race-window.svg"), W, H, *p,
           title="Гонка «перевірив — заснув» і те, чим її закривають")


# ── 3. Два шляхи одного сигналу ─────────────────────────────────────────────
def fig_two_paths():
    W, H = 1100, 700
    p = []

    p.append(fitbox(420, 58, 260, 54, "надійшов SIGTERM", size=13,
                    fill=SOFT, stroke=INK, sw=2, bold=True))
    p.append(arrow(480, 114, 300, 158, color=MUTED, sw=1.8))
    p.append(arrow(620, 114, 800, 158, color=MUTED, sw=1.8))
    p.append(text(300, 142, "не заблокований", size=12, color=POS, bold=True))
    p.append(text(800, 142, "заблокований", size=12, color=NEG, bold=True))

    # ліва колонка — класичний шлях
    p.append(rect(40, 166, 480, 380, fill=WARM, stroke=POS, sw=2, rx=8))
    p.append(text(280, 194, "ЧЕРЕЗ ОБРОБНИК", size=14, color=POS, bold=True))
    steps_l = [
        "ядро вставляє виклик функції\nміж двома машинними інструкціями",
        "обробник працює на довільному стеку,\nусередині невідомо якої роботи",
        "звідси можна кликати лише\nасинхронно-сигнально-безпечне",
        "усе, що треба зробити насправді,\nдоводиться відкладати прапорцем",
    ]
    for i, s in enumerate(steps_l):
        y = 216 + i * 82
        p.append(fitbox(66, y, 428, 62, s, size=12, fill=BG, stroke=POS, sw=1.4))
        if i < len(steps_l) - 1:
            p.append(arrow(280, y + 62, 280, y + 78, color=POS, sw=1.5))

    # права колонка — через дескриптор
    p.append(rect(580, 166, 480, 380, fill=COLD, stroke=NEG, sw=2, rx=8))
    p.append(text(820, 194, "ЧЕРЕЗ SIGNALFD", size=14, color=NEG, bold=True))
    steps_r = [
        "біт лягає в набір очікуваних\nі спокійно там чекає",
        "дескриптор стає готовим на читання —\nзвичайна подія для epoll",
        "read() віддає 128 байтів siginfo\nі знімає біт очікування",
        "код виконується в точці циклу,\nяку програма обрала сама",
    ]
    for i, s in enumerate(steps_r):
        y = 216 + i * 82
        p.append(fitbox(606, y, 428, 62, s, size=12, fill=BG, stroke=NEG, sw=1.4))
        if i < len(steps_r) - 1:
            p.append(arrow(820, y + 62, 820, y + 78, color=NEG, sw=1.5))

    p.append(rect(40, 572, 1020, 100, fill=GREENFILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(550, 600, "Перемикач між шляхами — маска, а не сам signalfd", size=13,
                  color=FIELD, bold=True))
    p.append(mtext(70, 626,
                   ["signalfd лише дає читати вже накопичене; він нічого не блокує сам.",
                    "Забули заблокувати — сигнал піде лівим шляхом і типова дія вб'є процес раніше, ніж дійде до read()."],
                   size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "two-paths.svg"), W, H, *p,
           title="Один сигнал, два шляхи: обробник або дескриптор")


# ── 4. Розкладка signalfd_siginfo по байтах ─────────────────────────────────
def fig_siginfo_layout():
    W, H = 1120, 580
    X0, BW = 100, 60          # лівий край сітки й ширина одного байта
    RY, RH, RG = 100, 40, 6   # верх першого рядка, висота рядка, проміжок
    p = []

    p.append(text(560, 44, "struct signalfd_siginfo — рівно 128 байтів", size=15,
                  color=INK, bold=True))
    p.append(text(560, 70, "кожен рядок — 16 байтів; усі поля фіксованої ширини, "
                           "тож read() не потребує шару сумісності", size=12, color=MUTED))

    rows = [
        [("ssi_signo", 0, 4, FIELD, GREENFILL), ("ssi_errno", 4, 4, MUTED, SOFT),
         ("ssi_code", 8, 4, FIELD, GREENFILL), ("ssi_pid", 12, 4, POS, WARM)],
        [("ssi_uid", 16, 4, POS, WARM), ("ssi_fd", 20, 4, NEG, COLD),
         ("ssi_tid", 24, 4, NEG, COLD), ("ssi_band", 28, 4, NEG, COLD)],
        [("ssi_overrun", 32, 4, NEG, COLD), ("ssi_trapno", 36, 4, NEG, COLD),
         ("ssi_status", 40, 4, NEG, COLD), ("ssi_int", 44, 4, NEG, COLD)],
        [("ssi_ptr", 48, 8, NEG, COLD), ("ssi_utime", 56, 8, NEG, COLD)],
        [("ssi_stime", 64, 8, NEG, COLD), ("ssi_addr", 72, 8, NEG, COLD)],
        [("ssi_addr_lsb", 80, 2, NEG, COLD), ("__pad2", 82, 2, MUTED, SOFT),
         ("ssi_syscall", 84, 4, NEG, COLD), ("ssi_call_addr", 88, 8, NEG, COLD)],
        [("ssi_arch", 96, 4, NEG, COLD),
         ("__pad[28] — резерв до рівно 128 байтів", 100, 12, MUTED, SOFT)],
        [("…той самий резерв", 112, 16, MUTED, SOFT)],
    ]

    for r, cells in enumerate(rows):
        y = RY + r * (RH + RG)
        p.append(text(X0 - 14, y + 25, str(r * 16), size=11, color=MUTED, anchor="end"))
        for nm, off, sz, col, fill in cells:
            x = X0 + (off - r * 16) * BW
            p.append(fitbox(x, y, sz * BW, RH, nm, size=12, pad=6,
                            fill=fill, stroke=col, sw=1.6))

    p.append(text(X0 - 14, RY - 12, "зсув", size=11, color=MUTED, anchor="end"))

    legend = [
        (100, 508, FIELD, GREENFILL, "завжди осмислені: ssi_signo і ssi_code"),
        (600, 508, POS, WARM, "хто надіслав: ssi_pid, ssi_uid"),
        (100, 544, NEG, COLD, "осмислені лише для певних сигналів"),
        (600, 544, MUTED, SOFT, "не вживається або резерв"),
    ]
    for x, y, col, fill, lbl in legend:
        p.append(rect(x, y - 13, 22, 22, fill=fill, stroke=col, sw=1.6, rx=4))
        p.append(text(x + 32, y + 4, lbl, size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "siginfo-layout.svg"), W, H, *p,
           title="Розкладка структури, яку віддає read() з signalfd")


# ── Стани наглядача під час згортання ───────────────────────────────────────
def fig_shutdown_states():
    W, H = 1100, 620
    p = []

    p.append(text(560, 38, "Наглядач має три стани, і всі переходи приносять дескриптори",
                  size=14, color=INK, bold=True))

    p.append(rect(340, 66, 400, 92, fill=GREENFILL, stroke=FIELD, sw=2, rx=8))
    p.append(text(540, 96, "RUNNING", size=15, color=FIELD, bold=True))
    p.append(mtext(540, 122, ["діти працюють, цикл спить в epoll_wait,",
                              "наглядач не робить нічого"], size=12, color=INK))

    p.append(arrow(540, 158, 540, 206, color=INK, sw=1.8))
    p.append(mtext(768, 176, ["SIGINT або SIGTERM,",
                              "прочитаний із signalfd"], size=12, color=NEG, anchor="start"))

    p.append(rect(340, 208, 400, 112, fill=COLD, stroke=NEG, sw=2, rx=8))
    p.append(text(540, 238, "DRAINING", size=15, color=NEG, bold=True))
    p.append(mtext(540, 264, ["SIGTERM кожній живій дитині,",
                              "timerfd заведено на пільгові 2 с,",
                              "цикл далі приймає події"], size=12, color=INK))

    p.append(arrow(540, 320, 540, 366, color=INK, sw=1.8))
    p.append(mtext(768, 338, ["timerfd став готовим:",
                              "пільговий час вичерпано"], size=12, color=POS, anchor="start"))

    p.append(rect(340, 368, 400, 92, fill=WARM, stroke=POS, sw=2, rx=8))
    p.append(text(540, 398, "KILLING", size=15, color=POS, bold=True))
    p.append(mtext(540, 424, ["SIGKILL решті — цього сигналу",
                              "не блокують і не ігнорують"], size=12, color=INK))

    p.append(arrow(540, 460, 540, 504, color=INK, sw=1.8))
    p.append(mtext(768, 478, ["останній SIGCHLD:",
                              "живих дітей не лишилось"], size=12, color=MUTED, anchor="start"))

    p.append(fitbox(390, 506, 300, 56, "вихід із циклу", size=13,
                    fill=SOFT, stroke=INK, sw=2, bold=True))

    p.append(rect(24, 208, 286, 252, fill=SOFT, stroke=MUTED, sw=1.8, rx=8))
    p.append(text(167, 238, "У БУДЬ-ЯКОМУ СТАНІ", size=13, color=MUTED, bold=True))
    p.append(mtext(167, 268, ["SIGCHLD із того самого",
                              "дескриптора каже лише",
                              "«щось змінилося».",
                              "Скільки саме дітей вийшло,",
                              "покаже waitpid(WNOHANG)",
                              "у циклі — доки не поверне",
                              "нуль або мінус одиницю."], size=12, color=INK))

    render(os.path.join(OUT, "shutdown-states.svg"), W, H, *p,
           title="Три стани наглядача й події, що їх перемикають")


fig_two_sets()
fig_race_window()
fig_two_paths()
fig_siginfo_layout()
fig_shutdown_states()
print("ok")
