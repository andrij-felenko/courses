# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COLD = "#eaf0fd"
GREENFILL = "#eafaf1"


# ── 1. Три моменти життя сигналу ────────────────────────────────────────────
def fig_three_moments():
    W, H = 1060, 620
    p = []

    # джерела породження
    srcs = [
        "інший процес:\nkill()",
        "драйвер термінала:\nCtrl-C",
        "таймер, що\nдоспів",
        "пастка процесора:\nділення на нуль",
    ]
    sx, sw, gap = 40, 220, 24
    for i, s in enumerate(srcs):
        x = sx + i * (sw + gap)
        p.append(fitbox(x, 60, sw, 60, s, size=12, fill=SOFT, stroke=MUTED, sw=1.4, color=INK))
        p.append(arrow(x + sw / 2, 122, x + sw / 2, 158, color=MUTED, sw=1.4))

    # три етапи
    stage_y, stage_h = 162, 96
    stages = [
        (40, 320, "ПОРОДЖЕННЯ", "ядро ставить один біт\nу масці очікуваних", POS, WARM),
        (392, 276, "ОЧІКУВАННЯ", "біт лежить у структурі задачі;\nпрограма про нього не знає", MUTED, FILL),
        (708, 312, "ДОПРАВЛЕННЯ", "ядро дивиться маску й діє:\nобробник або типова дія", NEG, COLD),
    ]
    for x, w, head, sub, accent, fill in stages:
        p.append(rect(x, stage_y, w, stage_h, fill=fill, stroke=accent, sw=2, rx=8))
        p.append(text(x + w / 2, stage_y + 28, head, size=14, color=accent, bold=True))
        p.append(mtext(x + w / 2, stage_y + 52, sub, size=12, color=INK))
    p.append(arrow(360, stage_y + stage_h / 2, 388, stage_y + stage_h / 2, sw=1.8))
    p.append(arrow(668, stage_y + stage_h / 2, 704, stage_y + stage_h / 2, sw=1.8))

    # межа режимів — під етапом доправлення
    p.append(line(40, 336, 1020, 336, color=MUTED, sw=1.2, dash="6 6"))
    p.append(text(530, 356, "розрив у часі: між породженням і доправленням може минути будь-скільки",
                  size=12, color=MUTED, italic=True))

    # чому саме на межі
    p.append(rect(40, 384, 620, 190, fill=GREENFILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(350, 410, "Доправляють лише на межі повернення в простір користувача",
                  size=13, color=FIELD, bold=True))
    p.append(mtext(60, 436,
                   ["Саме тут ядро вже має повний користувацький контекст у відомому",
                    "місці, не тримає жодного замка й може безпечно підмінити адресу",
                    "повернення на адресу обробника. Посеред драйвера чи під замком",
                    "запустити чужу функцію простору користувача неможливо."],
                   size=12, color=INK, anchor="start"))
    p.append(line(60, 520, 640, 520, color=FIELD, sw=1.0, dash="4 4"))
    p.append(text(60, 542, "user  ← сюди повертаємось, і саме тут ядро перевіряє маску",
                  size=12, color=FIELD, anchor="start"))
    p.append(text(60, 562, "kernel  ← тут сигнал лише породжується й лежить",
                  size=12, color=MUTED, anchor="start"))

    # наслідки
    p.append(rect(688, 384, 332, 190, fill=SOFT, stroke=POS, sw=1.8, rx=8))
    p.append(text(854, 410, "Наслідки розриву", size=13, color=POS, bold=True))
    p.append(mtext(706, 436,
                   ["• немає процесора — немає доправлення;",
                    "• сон перериваний: задачу будять,",
                    "   виклик обривається кодом EINTR;",
                    "• сон неперериваний (стан D):",
                    "   не будять узагалі — навіть SIGKILL",
                    "   просто лежить очікуваним."],
                   size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "three-moments.svg"), W, H, *p,
           title="Породження, очікування, доправлення — три різні моменти")


# ── 2. Біт проти черги ──────────────────────────────────────────────────────
def fig_bit_vs_queue():
    W, H = 1020, 560
    p = []

    def burst(y, label, accent):
        out = []
        for i in range(4):
            x = 60 + i * 84
            out.append(fitbox(x, y, 68, 34, "#%d" % (i + 1), size=12,
                              fill=SOFT, stroke=accent, sw=1.4, color=accent))
            out.append(arrow(x + 34, y + 36, x + 34, y + 62, color=accent, sw=1.4))
        out.append(text(230, y - 14, label, size=12, color=MUTED))
        return out

    # ── звичайний сигнал ──
    p.append(rect(30, 60, 960, 200, fill="#ffffff", stroke=POS, sw=2, rx=10))
    p.append(text(510, 86, "Звичайний сигнал (1…31): один біт на номер", size=14, color=POS, bold=True))
    p += burst(112, "чотири породження SIGCHLD, поки сигнал заблоковано", POS)

    p.append(fitbox(430, 168, 210, 56, "маска очікуваних:\nбіт SIGCHLD = 1", size=12,
                    fill=WARM, stroke=POS, sw=1.8, color=INK))
    p.append(arrow(400, 196, 426, 196, color=POS, sw=1.8))
    p.append(arrow(644, 196, 684, 196, color=POS, sw=1.8))
    p.append(fitbox(688, 168, 280, 56, "ОДНЕ доправлення\n(скільки їх було — невідомо)", size=12,
                    fill=SOFT, stroke=POS, sw=1.8, color=INK))

    # ── реальночасовий ──
    p.append(rect(30, 292, 960, 216, fill="#ffffff", stroke=NEG, sw=2, rx=10))
    p.append(text(510, 318, "Реальночасовий сигнал (SIGRTMIN…SIGRTMAX): черга записів",
                  size=14, color=NEG, bold=True))
    p += burst(344, "чотири породження SIGRTMIN+1 із різними значеннями", NEG)

    for i in range(4):
        p.append(fitbox(430 + i * 62, 400, 54, 44, "%d" % (i + 1), size=12,
                        fill=COLD, stroke=NEG, sw=1.6, color=INK))
    p.append(arrow(400, 422, 426, 422, color=NEG, sw=1.8))
    p.append(text(552, 466, "черга: кожне породження — окремий запис із siginfo",
                  size=12, color=MUTED))
    p.append(arrow(686, 422, 722, 422, color=NEG, sw=1.8))
    p.append(fitbox(726, 400, 244, 44, "ЧОТИРИ доправлення,\nу порядку надходження", size=12,
                    fill=SOFT, stroke=NEG, sw=1.8, color=INK))

    render(os.path.join(OUT, "bit-vs-queue.svg"), W, H, *p,
           title="Чому звичайні сигнали губляться, а реальночасові — ні")


# ── 3. Кому саме доправлять сигнал ──────────────────────────────────────────
def fig_target_choice():
    W, H = 1000, 560
    p = []

    # рамка групи потоків
    p.append(rect(300, 70, 660, 400, fill="#ffffff", stroke=MUTED, sw=1.6, rx=10))
    p.append(text(630, 96, "група потоків (один процес)", size=13, color=MUTED, bold=True))

    # спільна черга очікуваних
    p.append(fitbox(340, 116, 580, 56, "спільна маска очікуваних на всю групу  (ShdPnd)",
                    size=13, fill=GREENFILL, stroke=FIELD, sw=1.8, color=INK))

    # три потоки
    names = ["потік A\nсигнал заблоковано", "потік B\nсигнал відкрито", "потік C\nсигнал відкрито"]
    for i, n in enumerate(names):
        x = 340 + i * 196
        p.append(fitbox(x, 216, 176, 62, n, size=12, fill=SOFT, stroke=NEG, sw=1.6, color=INK))
        p.append(fitbox(x, 292, 176, 46, "власна маска\n(SigPnd)", size=11,
                        fill=FILL, stroke=MUTED, sw=1.3, color=MUTED))
        p.append(line(x + 88, 172, x + 88, 212, color=MUTED, sw=1.2, dash="4 4"))

    p.append(text(630, 372, "ядро віддає сигнал БУДЬ-ЯКОМУ потоку, що його не заблокував",
                  size=12, color=FIELD))
    p.append(text(630, 394, "передбачити, кому саме, не можна", size=12, color=POS, bold=True))
    p.append(text(630, 432, "смертельна типова дія вбиває ВСЮ групу, а не один потік",
                  size=12, color=INK))

    # входи ліворуч
    p.append(fitbox(30, 116, 236, 56, "kill(pid, sig)\nсигнал процесові", size=12,
                    fill=WARM, stroke=POS, sw=1.8, color=INK))
    p.append(arrow(270, 144, 336, 144, color=POS, sw=1.8))

    p.append(fitbox(30, 216, 236, 56, "tgkill(), pthread_kill()\nсигнал конкретному потоку", size=12,
                    fill=COLD, stroke=NEG, sw=1.8, color=INK))
    p.append(arrow(270, 244, 336, 244, color=NEG, sw=1.8))

    p.append(fitbox(30, 316, 236, 74, "пастка процесора\nв самому потоці B\n(SIGSEGV, SIGFPE)", size=12,
                    fill=SOFT, stroke=INK, sw=1.8, color=INK))
    p.append(arrow(270, 500, 620, 500, color=INK, sw=1.6))
    p.append(line(148, 392, 148, 500, color=INK, sw=1.6))
    p.append(text(660, 504, "завжди тому потокові, чия інструкція завинила",
                  size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "target-choice.svg"), W, H, *p,
           title="Сигнал процесові, сигнал потокові й сигнал від власної інструкції")


# ── 4. Гонка Version 7: вікно між скиданням і перевстановленням ─────────────
def fig_v7_race():
    W, H = 1080, 540
    p = []

    AX = 300.0                      # вісь часу
    X0, X1 = 70.0, 1010.0
    p.append(line(X0, AX, X1, AX, color=MUTED, sw=2))
    p.append(text(X1 + 24, AX + 5, "час", size=12, color=MUTED, anchor="start"))

    # смуга гонки на осі
    RX0, RX1 = 320.0, 800.0
    p.append(rect(RX0, AX - 13, RX1 - RX0, 26, fill=WARM, stroke=POS, sw=2, rx=4))
    p.append(text((RX0 + RX1) / 2, AX + 40, "вікно гонки: диспозиція вже «убити», обробник ще не воскрешено",
                  size=12, color=POS, bold=True))

    # чотири події над віссю
    evs = [
        (70, 160, "надійшов SIGINT\n(перший)", MUTED, SOFT, 150.0),
        (240, 160, "ЯДРО скидає\nдиспозицію\nна типову дію", POS, WARM, 320.0),
        (420, 160, "ЯДРО кличе\nобробник", MUTED, SOFT, 500.0),
        (720, 160, "ПРОГРАМА кличе\nsignal(SIGINT, …)\n— обробник знову є", NEG, COLD, 800.0),
    ]
    for bx, bw, s, accent, fill, mx in evs:
        p.append(fitbox(bx, 150, bw, 76, s, size=12, fill=fill, stroke=accent, sw=1.8, color=INK))
        p.append(line(mx, 226, mx, AX - 14, color=accent, sw=1.4, dash="4 4"))
        p.append(circle(mx, AX, 7, fill=fill, stroke=accent, sw=2))

    # другий сигнал падає просто у вікно
    p.append(fitbox(560, 44, 200, 54, "надходить ДРУГИЙ\nSIGINT", size=12,
                    fill=WARM, stroke=POS, sw=2, color=POS, bold=True))
    p.append(arrow(660, 100, 660, AX - 16, color=POS, sw=2.2))

    # доріжка диспозиції
    LY, LH = 384.0, 46.0
    p.append(text(X0, LY - 14, "диспозиція SIGINT у ядрі:", size=12, color=MUTED, anchor="start"))
    p.append(fitbox(X0, LY, RX0 - X0, LH, "catch_int", size=13, fill=GREENFILL, stroke=NEG, sw=1.6, color=INK))
    p.append(fitbox(RX0, LY, RX1 - RX0, LH, "SIG_DFL — убити процес", size=13,
                    fill=WARM, stroke=POS, sw=2, color=POS, bold=True))
    p.append(fitbox(RX1, LY, X1 - RX1, LH, "catch_int", size=13, fill=GREENFILL, stroke=NEG, sw=1.6, color=INK))

    # наслідок
    p.append(fitbox(280, 468, 520, 44,
                    "процес убито; обробник другого сигналу не бачив", size=13,
                    fill=WARM, stroke=POS, sw=2, color=POS, bold=True))

    render(os.path.join(OUT, "v7-race.svg"), W, H, *p,
           title="Version 7: скидає ядро, перевстановлює програма — проміжок нічий")


# ── 5. Чому лічильник в обробнику недорахує (для proj-signal-race) ──────────
def fig_handler_undercount():
    W, H = 1060, 430
    X0, X1 = 100.0, 990.0
    AX = 100.0            # вісь часу
    HI, LO = 180.0, 225.0  # рівні «біт стоїть» / «біта нема»
    p = []

    # доріжка 1: надсилання
    p.append(text(X0, 32, "надсилання (raise/kill)", size=13, color=MUTED, anchor="start"))
    p.append(line(X0, AX, X1, AX, color=MUTED, sw=1.4))
    p.append(text(985, 92, "час →", size=12, color=MUTED, anchor="end"))
    sends = [(150.0, "№1"), (330.0, "№2"), (400.0, "№3"), (470.0, "№4"), (700.0, "№5")]
    for x, lab in sends:
        p.append(text(x, 62, lab, size=12, color=POS, bold=True))
        p.append(arrow(x, 70, x, AX - 2, color=POS, sw=1.8))

    # доріжка 2: біт у масці очікуваних
    p.append(text(X0, 140, "біт SIGUSR1 у масці очікуваних", size=13, color=MUTED, anchor="start"))
    p.append(text(96, HI + 4, "1", size=12, color=MUTED, anchor="end"))
    p.append(text(96, LO + 4, "0", size=12, color=MUTED, anchor="end"))
    steps = [(X0, LO, 150, LO), (150, LO, 150, HI), (150, HI, 170, HI),
             (170, HI, 170, LO), (170, LO, 330, LO), (330, LO, 330, HI),
             (330, HI, 520, HI), (520, HI, 520, LO), (520, LO, 700, LO),
             (700, LO, 700, HI), (700, HI, 720, HI), (720, HI, 720, LO),
             (720, LO, X1, LO)]
    for a, b, c, d in steps:
        p.append(line(a, b, c, d, color=NEG, sw=2.4))
    p.append(text(425, 170, "№2, №3, №4 злиплися в один біт", size=12, color=POS, bold=True))

    # доріжка 3: запуски обробника
    p.append(text(X0, 265, "виконання обробника (свій сигнал у ньому заблоковано)",
                  size=13, color=MUTED, anchor="start"))
    for x, w, lab in [(170.0, 330.0, "запуск A"), (520.0, 140.0, "B"), (720.0, 140.0, "C")]:
        p.append(fitbox(x, 285, w, 50, lab, size=13, fill=GREENFILL, stroke=FIELD, sw=1.8, color=INK))

    box, _, _ = textbox(545, 385,
                        "5 надсилань → 3 запуски обробника:\n"
                        "лічильник в обробнику міряє доправлення, а не події",
                        size=13, fill=WARM, stroke=POS, sw=2, color=INK, bold=True)
    p.append(box)

    render(os.path.join(OUT, "handler-undercount.svg"), W, H, *p,
           title="Надіслано п'ять, обробник спрацював тричі")


# ── 6. Кого називає адреса надсилання ───────────────────────────────────────
def fig_addressing_scopes():
    W, H = 1120, 645
    p = []

    # вкладені обсяги адресації
    p.append(rect(400, 40, 690, 470, fill=SOFT, stroke=MUTED, sw=1.6, rx=12))
    p.append(text(745, 72, "СЕАНС — межа винятку для SIGCONT", size=13, color=MUTED, bold=True))

    p.append(rect(430, 100, 630, 380, fill=COLD, stroke=NEG, sw=1.8, rx=10))
    p.append(text(745, 130, "ГРУПА ПРОЦЕСІВ (PGID)", size=14, color=NEG, bold=True))

    p.append(rect(460, 175, 570, 270, fill=WARM, stroke=POS, sw=2, rx=10))
    p.append(text(745, 205, "ПРОЦЕС = ГРУПА ПОТОКІВ (PID = TGID)", size=14, color=POS, bold=True))
    p.append(text(745, 232, "спільна маска очікуваних", size=12, color=MUTED))

    for i, cx in enumerate((485, 665, 845)):
        p.append(fitbox(cx, 270, 165, 64, "потік\nTID", size=13,
                        fill=GREENFILL, stroke=FIELD, sw=1.6, color=INK))
    p.append(text(745, 370, "власна маска очікуваних у кожного потоку", size=12, color=MUTED))

    # чим цілитися в кожен обсяг
    calls = [
        (95, 76, 133, 430,
         "kill(pid < -1, sig) -> група з PGID = -pid\n"
         "killpg(pgid, sig) = kill(-pgid, sig)\n"
         "kill(0, sig) -> своя група процесів", NEG, COLD),
        (185, 76, 223, 460,
         "kill(pid > 0, sig) -> si_code = SI_USER\n"
         "sigqueue(pid, sig, val) -> SI_QUEUE + значення\n"
         "pidfd_send_signal(pidfd, sig, info, 0)", POS, WARM),
        (278, 64, 302, 485,
         "tgkill(tgid, tid, sig) -> si_code = SI_TKILL\n"
         "pthread_kill(thread, sig) — обгортка над ним", FIELD, GREENFILL),
        (360, 64, 392, 460,
         "kill(pid, 0) — сигналу немає,\n"
         "лишаються перевірки існування й прав", MUTED, FILL),
    ]
    for y, h, ay, tx, s, accent, fill in calls:
        p.append(fitbox(30, y, 345, h, s, size=13, fill=fill, stroke=accent, sw=1.8, color=INK))
        p.append(arrow(378, y + h / 2, tx - 6, ay, color=accent, sw=1.6))

    p.append(fitbox(30, 528, 1060, 44,
                    "kill(-1, sig) — усім процесам, яким дозволено надсилати, крім PID 1 (init)",
                    size=13, fill=COLD, stroke=NEG, sw=1.8, color=INK))
    p.append(fitbox(30, 584, 1060, 44,
                    "raise(sig) — собі: в однопотоковій = kill(getpid(), sig), "
                    "у багатопотоковій = pthread_kill(pthread_self(), sig)",
                    size=13, fill=FILL, stroke=MUTED, sw=1.8, color=INK))

    render(os.path.join(OUT, "addressing-scopes.svg"), W, H, *p,
           title="Чотири обсяги адресації і виклики, що в них цілять")


fig_three_moments()
fig_bit_vs_queue()
fig_target_choice()
fig_v7_race()
fig_handler_undercount()
fig_addressing_scopes()
print("ok")
