# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: пара чисел і хто як може її рухати ──────────────────────────────
# Ідея: увесь механізм тримається на тому, що чисел ДВА, і правила руху в них
# різні. М'який ходить вільно в межах жорсткого, жорсткий — лише вниз без прав.
def fig_soft_hard_pair():
    W, H = 1020, 520
    p = []

    AX_Y = 200
    p.append(line(80, AX_Y, 950, AX_Y, color=INK, sw=2.0))
    p.append(text(80, AX_Y + 30, "0", size=13.5, color=MUTED))
    p.append(text(950, AX_Y + 30, "RLIM_INFINITY", size=13.5, color=MUTED, anchor="end"))

    p.append(line(400, AX_Y - 16, 400, AX_Y + 16, color=NEG, sw=2.6))
    b, bw, bh = textbox(400, 150, "м'який · rlim_cur", size=13.5, pad=11,
                        fill="#eef3fb", stroke=NEG, sw=1.6, bold=True)
    p.append(b)

    p.append(line(780, AX_Y - 16, 780, AX_Y + 16, color=POS, sw=2.6))
    b, bw, bh = textbox(780, 150, "жорсткий · rlim_max", size=13.5, pad=11,
                        fill="#fdeeec", stroke=POS, sw=1.6, bold=True)
    p.append(b)

    p.append(fitbox(80, 258, 700, 34,
                    "тут ядро дозволяє стояти м'якому значенню",
                    size=13, fill="#eef7f0", stroke=FIELD, sw=1.4))

    BW, GAP = 290, 35
    X0 = (W - (3 * BW + 2 * GAP)) / 2
    cols = [
        (["м'який — будь-куди в [0, жорсткий]",
          "без жодних особливих прав",
          "саме це число ядро звіряє",
          "на кожному запиті ресурсу"], "#eef7f0", FIELD),
        (["жорсткий — тільки ВНИЗ",
          "теж без особливих прав,",
          "але назад підняти вже не можна:",
          "незворотне самообмеження"], "#eef3fb", NEG),
        (["жорсткий — УГОРУ",
          "лише з можливістю CAP_SYS_RESOURCE",
          "для NOFILE є ще й окрема стеля",
          "на саме значення — fs.nr_open"], "#fdeeec", POS),
    ]
    for i, (lines, fill, color) in enumerate(cols):
        p.append(fitbox(X0 + i * (BW + GAP), 340, BW, 122, lines, size=13,
                        fill=fill, stroke=color, sw=1.5))

    p.append(text(W / 2, 492,
                  "Два числа замість одного дають і делеговану стелю, і самообмеження — одним механізмом",
                  size=13.5, color=MUTED))

    render(os.path.join(OUT, "soft-hard-pair.svg"), W, H, *p,
           title="Ліміт — це пара чисел із різними правилами руху")


# ── Фіг. 2: три способи впровадження ────────────────────────────────────────
# Ідея: форма ліміту диктується не ресурсом, а тим, чи існує МОМЕНТ запиту.
# Є момент — відмовляємо; немає — б'ємо сигналом; немає навіть споживання
# як події — ліміт нема куди вставити, і його тихо вимкнули.
def fig_enforcement_styles():
    W, H = 1040, 690
    p = []

    CW, GAP = 300, 30
    X0 = (W - (3 * CW + 2 * GAP)) / 2

    cols = [
        ("Відмова у запиті", "є момент, коли процес просить",
         ["процес просить у ядра об'єкт:", "open, socket, fork, mmap, brk"],
         ["NOFILE · NPROC · SIGPENDING", "MSGQUEUE · MEMLOCK", "AS · DATA · STACK"],
         ["звичайна помилка виклику:", "EMFILE, EAGAIN, ENOMEM", "слова «ліміт» ніде немає"],
         NEG, "#eef3fb"),
        ("Сигнал під час споживання", "запиту немає — ресурс тече",
         ["ядро звіряє накопичений", "лічильник на тиках таймера"],
         ["CPU · RTTIME", "FSIZE — гібрид: і сигнал,", "і помилка write"],
         ["SIGXCPU на м'якому,", "SIGKILL на жорсткому,", "SIGXFSZ і EFBIG для файлу"],
         POS, "#fdeeec"),
        ("Перевіряти нема де", "ресурс не просять — він виникає",
         ["сторінка стає резидентною", "від дотику, а йде — від", "витіснення, не від виклику"],
         ["RSS — не діє з 2.4.30", "LOCKS — знято в 2.4.25"],
         ["жодного прояву:", "значення можна виставити,", "але його просто ігнорують"],
         MUTED, "#f4f6f8"),
    ]

    for i, (name, sub, when, which, how, color, fill) in enumerate(cols):
        x = X0 + i * (CW + GAP)
        p.append(rect(x, 62, CW, 468, fill="#ffffff", stroke=color, sw=1.8, rx=12))
        p.append(text(x + CW / 2, 94, name, size=15, color=color, bold=True))
        p.append(text(x + CW / 2, 118, sub, size=12.5, color=MUTED))
        p.append(text(x + CW / 2, 152, "коли ядро дивиться", size=12.5, color=MUTED, bold=True))
        p.append(fitbox(x + 16, 162, CW - 32, 80, when, size=13,
                        fill=fill, stroke=color, sw=1.3))
        p.append(text(x + CW / 2, 274, "які саме ліміти", size=12.5, color=MUTED, bold=True))
        p.append(fitbox(x + 16, 284, CW - 32, 80, which, size=13,
                        fill="#f4f6f8", stroke="#c8ced6", sw=1.2))
        p.append(text(x + CW / 2, 396, "як це бачить програма", size=12.5, color=MUTED, bold=True))
        p.append(fitbox(x + 16, 406, CW - 32, 88, how, size=13,
                        fill=fill, stroke=color, sw=1.3))

    p.append(fitbox(X0, 566, 3 * CW + 2 * GAP, 88,
                    ["Третій стовпець — не недогляд реалізації, а межа самої моделі:",
                     "де немає моменту запиту, туди ліміт на окремий процес нема куди вставити.",
                     "Відповіддю став інший механізм — облік і витіснення на ГРУПУ процесів (cgroups)."],
                    size=13.5, fill="#eef7f0", stroke=FIELD, sw=1.5))

    render(os.path.join(OUT, "enforcement-styles.svg"), W, H, *p,
           title="Форму ліміту диктує не ресурс, а наявність моменту запиту")


# ── Фіг. 3: звідки беруться значення в живій системі ────────────────────────
# Ідея: значення нікуди не «налаштовуються» — вони СПАДКУЮТЬСЯ по ланцюгу
# запусків. Гілок дві, і PAM є лише в одній — звідси класична пастка.
def fig_limits_provenance():
    W, H = 1060, 700
    p = []

    b, bw, bh = textbox(530, 80,
                        "ядро: значення, з якими стартує PID 1\n"
                        "NOFILE 1024 м'який · 4096 жорсткий",
                        size=13.5, pad=12, fill="#f4f6f8", stroke=INK, sw=1.6)
    p.append(b)
    p.append(arrow(530, 80 + bh / 2 + 4, 530, 156, color=INK))

    b, bw, bh = textbox(530, 178, "init — PID 1", size=14, pad=12,
                        fill="#eef7f0", stroke=FIELD, sw=1.8, bold=True)
    p.append(b)

    p.append(arrow(470, 198, 300, 250, color=NEG))
    p.append(arrow(590, 198, 760, 250, color=POS))

    left = [
        (275, "вхід у сеанс: login, sshd, дисплейний менеджер"),
        (365, "PAM, модуль pam_limits\n/etc/security/limits.conf"),
        (455, "оболонка сеансу\nulimit -n 4096 у profile або rc"),
        (545, "програма користувача"),
    ]
    for i, (y, s) in enumerate(left):
        b, bw, bh = textbox(270, y, s, size=13, pad=11, fill="#eef3fb",
                            stroke=NEG, sw=1.5, bold=(i == 3))
        p.append(b)
        if i < len(left) - 1:
            p.append(arrow(270, y + bh / 2 + 3, 270, left[i + 1][0] - 24, color=NEG))

    right = [
        (275, "systemd — менеджер служб"),
        (365, "юніт: LimitNOFILE=\nsystem.conf: DefaultLimitNOFILE="),
        (455, "служба"),
    ]
    for i, (y, s) in enumerate(right):
        b, bw, bh = textbox(790, y, s, size=13, pad=11, fill="#fdeeec",
                            stroke=POS, sw=1.5, bold=(i == 2))
        p.append(b)
        if i < len(right) - 1:
            p.append(arrow(790, y + bh / 2 + 3, 790, right[i + 1][0] - 24, color=POS))

    p.append(fitbox(60, 600, 940, 76,
                    ["У правій гілці PAM немає взагалі: служба не «входить у сеанс».",
                     "Тому правка limits.conf не діє на служби, а Limit…= в юніті не діє на вхід у термінал."],
                    size=13.5, fill="#f4f6f8", stroke=INK, sw=1.5))

    render(os.path.join(OUT, "limits-provenance.svg"), W, H, *p,
           title="Значення лімітів не налаштовують — їх успадковують")


# ── Фіг. 4: чотири стелі над дескрипторами ──────────────────────────────────
# Ідея: три з них стоять одна над одною на ОДНІЙ осі (номер дескриптора в
# процесі), а четверта міряє зовсім інше — кількість відкритих файлів у всій
# системі. Звідси різниця EMFILE і ENFILE.
def fig_nofile_ceilings():
    W, H = 980, 560
    p = []

    p.append(arrow(110, 470, 110, 186, color=MUTED, sw=2.0))
    p.append(text(110, 500, "одна вісь:", size=12.5, color=MUTED))
    p.append(text(110, 518, "скільки дескрипторів", size=12.5, color=MUTED))
    p.append(text(110, 536, "тримає ОДИН процес", size=12.5, color=MUTED))

    rungs = [
        (430, NEG, "#eef3fb",
         ["м'який RLIMIT_NOFILE — типово 1024",
          "саме його ядро звіряє в open(): вище → EMFILE"]),
        (330, POS, "#fdeeec",
         ["жорсткий RLIMIT_NOFILE — 512K у systemd від 240",
          "стеля, до якої процес сам піднімає м'який"]),
        (230, FIELD, "#eef7f0",
         ["fs.nr_open — типово 1 048 576",
          "стеля для самого ЗНАЧЕННЯ жорсткого ліміту"]),
    ]
    for y, color, fill, lines in rungs:
        p.append(line(94, y, 126, y, color=color, sw=2.6))
        p.append(fitbox(150, y - 30, 420, 60, lines, size=13,
                        fill=fill, stroke=color, sw=1.5))

    p.append(fitbox(620, 230, 320, 200,
                    ["fs.file-max",
                     "",
                     "ІНША вісь: рахує відкриті файли",
                     "в усій системі разом,",
                     "а не номер у одному процесі",
                     "",
                     "вичерпання дає ENFILE"],
                    size=13, fill="#f4f6f8", stroke=INK, sw=1.5))

    p.append(fitbox(150, 486, 790, 48,
                    "EMFILE — уперся ти; ENFILE — уперлася система",
                    size=14, fill="#ffffff", stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, "nofile-ceilings.svg"), W, H, *p,
           title="Скільки стель насправді стоїть над дескрипторами")


# ── Фіг. 5: як росла таблиця лімітів ────────────────────────────────────────
# Ідея (для вставки hist-limits-lineage): механізм не спроєктували цілим —
# він наростав шарами, і кожен шар видно в сучасній таблиці. Заразом видно
# перенумерування: 4.4BSD і Linux дали трьом однаковим лімітам різні номери.
def fig_limits_lineage():
    W, H = 1160, 830
    p = []

    ROWS = [
        "RLIMIT_CPU", "RLIMIT_FSIZE", "RLIMIT_DATA", "RLIMIT_STACK",
        "RLIMIT_CORE", "RLIMIT_RSS", "RLIMIT_NPROC", "RLIMIT_NOFILE",
        "RLIMIT_MEMLOCK", "RLIMIT_AS", "RLIMIT_LOCKS", "RLIMIT_SIGPENDING",
        "RLIMIT_MSGQUEUE", "RLIMIT_NICE", "RLIMIT_RTPRIO", "RLIMIT_RTTIME",
    ]

    # для кожного стовпця: назва, підпис, скільки всього, колір, заливка,
    # словник {ім'я ліміту: номер у ЦІЙ системі}
    bsd42 = {n: i for i, n in enumerate(ROWS[:6])}
    bsd44 = dict(bsd42)
    bsd44.update({"RLIMIT_MEMLOCK": 6, "RLIMIT_NPROC": 7, "RLIMIT_NOFILE": 8})
    linux = {n: i for i, n in enumerate(ROWS)}

    COLS = [
        ("ulimit(2)", "System III, початок 1980-х", "1 межа",
         MUTED, "#f4f6f8", {"RLIMIT_FSIZE": None}),
        ("4.2BSD · 4.3BSD", "getrlimit / setrlimit, 1983", "6 меж",
         NEG, "#eef3fb", bsd42),
        ("4.4BSD", "1993", "9 меж",
         FIELD, "#eef7f0", bsd44),
        ("Linux", "сучасне ядро", "16 меж",
         POS, "#fdeeec", linux),
    ]

    CW, GAP = 262, 20
    X0 = (W - (4 * CW + 3 * GAP)) / 2
    TOP, RH, BH = 132, 38, 30

    for c, (name, sub, cnt, color, fill, have) in enumerate(COLS):
        x = X0 + c * (CW + GAP)
        p.append(rect(x, 56, CW, TOP - 66 + len(ROWS) * RH + 12,
                      fill="#ffffff", stroke=color, sw=1.8, rx=12))
        p.append(text(x + CW / 2, 82, name, size=15, color=color, bold=True))
        p.append(text(x + CW / 2, 103, sub, size=12, color=MUTED))
        p.append(text(x + CW / 2, 123, cnt, size=12.5, color=color, bold=True))

        for r, rowname in enumerate(ROWS):
            y = TOP + r * RH
            if rowname in have:
                num = have[rowname]
                label = rowname if num is None else "%d  %s" % (num, rowname)
                p.append(fitbox(x + 14, y, CW - 28, BH, label, size=12.5,
                                fill=fill, stroke=color, sw=1.3))
            else:
                p.append(line(x + CW / 2 - 16, y + BH / 2,
                              x + CW / 2 + 16, y + BH / 2,
                              color="#d7dbe0", sw=1.6))

    p.append(fitbox(X0, TOP + len(ROWS) * RH + 26, 4 * CW + 3 * GAP, 68,
                    ["Числа перед іменами — номери констант у своїй системі.",
                     "Три однакові межі 4.4BSD і Linux пронумерували по-різному: "
                     "переносний тут ЛИШЕ текст імені, не число."],
                    size=13.5, fill="#f4f6f8", stroke=INK, sw=1.5))

    render(os.path.join(OUT, "limits-lineage.svg"), W, H, *p,
           title="Таблиця лімітів наростала шарами, і кожен шар у ній досі видно")


# ── Фіг. 6: EMFILE у циклі приймання (для вставки proj-fd-limit) ────────────
# Ідея: сама по собі відмова open() нешкідлива, але в циклі приймання вона
# зациклюється — з'єднання лишається в черзі, слухач і далі «готовий».
# Резервний дескриптор розриває цю петлю: звільнити номер, прийняти, закрити.
def fig_emfile_accept_loop():
    W, H = 1120, 740
    p = []

    LX, RX, CW = 120, 610, 400

    p.append(fitbox(LX, 44, CW, 46, "без резервного дескриптора", size=15,
                    fill="#fdeeec", stroke=POS, sw=1.8))
    p.append(fitbox(RX, 44, CW, 46, "з резервним дескриптором", size=15,
                    fill="#eef7f0", stroke=FIELD, sw=1.8))

    BH, STEP, Y0 = 56, 86, 122

    left = [
        "epoll_wait: слухач готовий",
        "accept4() → EMFILE",
        ["з'єднання лишилося в черзі —", "слухач і далі «готовий»"],
        "epoll_wait будить одразу знову",
    ]
    for i, s in enumerate(left):
        y = Y0 + i * STEP
        p.append(fitbox(LX, y, CW, BH, s, size=13.5,
                        fill="#fdeeec", stroke=POS, sw=1.5))
        if i < len(left) - 1:
            p.append(arrow(LX + CW / 2, y + BH + 4, LX + CW / 2, y + STEP - 6,
                           color=POS))

    ylast = Y0 + (len(left) - 1) * STEP
    p.append(line(LX - 6, ylast + BH / 2, LX - 46, ylast + BH / 2, color=POS, sw=1.8))
    p.append(line(LX - 46, ylast + BH / 2, LX - 46, Y0 + BH / 2, color=POS, sw=1.8))
    p.append(arrow(LX - 46, Y0 + BH / 2, LX - 8, Y0 + BH / 2, color=POS))

    right = [
        "accept4() → EMFILE",
        ["close(spare) —", "один номер під межею вільний"],
        "accept4() → з'єднання прийнято",
        ["close(client) —", "клієнт бачить розрив одразу"],
        ["spare = open(\"/dev/null\") —", "резерв на місці до наступного разу"],
    ]
    for i, s in enumerate(right):
        y = Y0 + i * STEP
        p.append(fitbox(RX, y, CW, BH, s, size=13.5,
                        fill="#eef7f0", stroke=FIELD, sw=1.5))
        if i < len(right) - 1:
            p.append(arrow(RX + CW / 2, y + BH + 4, RX + CW / 2, y + STEP - 6,
                           color=FIELD))

    p.append(fitbox(LX, 572, CW, 84,
                    ["петля без жодного поступу:", "ядро процесора зайняте вщент,",
                     "у журналі — той самий рядок без упину"],
                    size=13, fill="#ffffff", stroke=POS, sw=1.5))
    p.append(fitbox(RX, 572, CW, 84,
                    ["черга спорожніла, слухач замовк:", "перевантаження нікуди не зникло,",
                     "але стало чесною відмовою"],
                    size=13, fill="#ffffff", stroke=FIELD, sw=1.5))

    p.append(text(W / 2, 700,
                  "Різниця лише в одному наперед відкритому дескрипторі, "
                  "який тримають закритим саме на цей випадок",
                  size=13.5, color=MUTED))

    render(os.path.join(OUT, "emfile-accept-loop.svg"), W, H, *p,
           title="EMFILE у циклі приймання: петля проти чесної відмови")


fig_soft_hard_pair()
fig_enforcement_styles()
fig_limits_provenance()
fig_nofile_ceilings()
fig_limits_lineage()
fig_emfile_accept_loop()
print("готово:", OUT)
