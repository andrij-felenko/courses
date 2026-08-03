# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: три поверхи ─────────────────────────────────────────────────────
# Ідея: дескриптор → опис → inode, і на ОБОХ переходах зв'язок «багато до
# одного». Копії дескриптора (dup, fork) ведуть в ОДИН опис зі спільною
# позицією; окремі open того самого файлу дають РІЗНІ описи на один inode.
def fig_three_levels():
    W, H = 980, 700
    p = []

    # таблиця дескрипторів процесу-батька
    p.append(rect(60, 56, 420, 104, fill="#ffffff", stroke=INK, sw=1.6, rx=10))
    p.append(text(270, 80, "процес 4021 — таблиця дескрипторів", size=13, color=INK, bold=True))
    p.append(fitbox(78, 96, 120, 48, "fd 1", size=15, fill="#eef3fb", stroke=NEG, sw=1.5))
    p.append(fitbox(210, 96, 120, 48, "fd 2", size=15, fill="#eef3fb", stroke=NEG, sw=1.5))
    p.append(fitbox(342, 96, 120, 48, "fd 3", size=15, fill="#eef3fb", stroke=NEG, sw=1.5))

    # таблиця дескрипторів дитини
    p.append(rect(560, 56, 360, 104, fill="#ffffff", stroke=INK, sw=1.6, rx=10))
    p.append(text(740, 80, "процес 4022 (дитина) — своя таблиця", size=13, color=INK, bold=True))
    p.append(fitbox(580, 96, 140, 48, "fd 1", size=15, fill="#fdeeec", stroke=POS, sw=1.5))
    p.append(fitbox(750, 96, 140, 48, "fd 3", size=15, fill="#fdeeec", stroke=POS, sw=1.5))

    # описи відкритих файлів
    p.append(fitbox(60, 250, 300, 100,
                    ["опис відкритого файлу",
                     "позиція 120 · O_WRONLY",
                     "посилань: 3"],
                    size=14, fill="#eef7f0", stroke=FIELD, sw=1.8))
    p.append(fitbox(400, 250, 260, 100,
                    ["опис відкритого файлу",
                     "позиція 0 · O_RDONLY",
                     "посилань: 1"],
                    size=14, fill="#eef7f0", stroke=FIELD, sw=1.8))
    p.append(fitbox(700, 250, 220, 100,
                    ["опис відкритого файлу",
                     "позиція 4096 · O_RDONLY",
                     "посилань: 1"],
                    size=14, fill="#eef7f0", stroke=FIELD, sw=1.8))

    # дескриптор → опис
    p.append(arrow(138, 146, 170, 246, color=NEG))
    p.append(arrow(270, 146, 232, 246, color=NEG))
    p.append(arrow(402, 146, 480, 246, color=NEG))
    p.append(arrow(650, 146, 300, 246, color=POS))
    p.append(arrow(820, 146, 806, 246, color=POS))

    # inode
    p.append(fitbox(100, 430, 280, 76, ["inode 8814", "out.txt · 12 КіБ"],
                    size=14, fill="#f4f6f8", stroke=INK, sw=1.6))
    p.append(fitbox(560, 430, 300, 76, ["inode 9002", "data.bin · 4 МіБ"],
                    size=14, fill="#f4f6f8", stroke=INK, sw=1.6))

    # опис → inode
    p.append(arrow(210, 352, 240, 426, color=FIELD))
    p.append(arrow(530, 352, 662, 426, color=FIELD))
    p.append(arrow(810, 352, 758, 426, color=FIELD))

    # пояснення внизу
    p.append(fitbox(60, 552, 860, 108,
                    ["fd 1 і fd 2 батька — це dup (перенаправлення 2>&1), fd 1 дитини — успадковано через fork:",
                     "три дескриптори, ОДИН опис, одна спільна позиція на всіх",
                     "fd 3 батька і fd 3 дитини — два окремі open того самого файлу:",
                     "два описи на один inode, позиції незалежні, записи затирають одне одного"],
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, "three-levels.svg"), W, H, *p,
           title="дескриптор → опис відкритого файлу → inode")


# ── Фіг. 2: спільна позиція проти двох позицій ──────────────────────────────
# Ідея: два писарі по 5 байтів. Спільний опис — записи лягають один за одним
# (10 байтів). Два описи — обидва пишуть з нуля, половина даних зникає.
def fig_shared_offset():
    W, H = 980, 620
    p = []

    CELL = 34

    def panel(px, title, color, a_start, b_start, result, result_len, note):
        out = [rect(px, 60, 420, 470, fill="#ffffff", stroke=color, sw=1.8, rx=12)]
        out.append(text(px + 210, 88, title, size=15, color=color, bold=True))
        x0 = px + 34

        out.append(text(x0, 128, "процес A: write(fd, \"AAAAA\", 5)", size=12.5,
                        color=MUTED, anchor="start"))
        out.append(rect(x0 + a_start * CELL, 138, 5 * CELL, 40,
                        fill="#eef3fb", stroke=NEG, sw=1.6, rx=4))
        out.append(text(x0 + (a_start + 2.5) * CELL, 164, "AAAAA", size=15, color=NEG, bold=True))

        out.append(text(x0, 216, "процес B: write(fd, \"BBBBB\", 5)", size=12.5,
                        color=MUTED, anchor="start"))
        out.append(rect(x0 + b_start * CELL, 226, 5 * CELL, 40,
                        fill="#fdeeec", stroke=POS, sw=1.6, rx=4))
        out.append(text(x0 + (b_start + 2.5) * CELL, 252, "BBBBB", size=15, color=POS, bold=True))

        out.append(text(x0, 316, "у файлі:", size=12.5, color=MUTED, anchor="start"))
        out.append(rect(x0, 326, result_len * CELL, 44, fill="#eef7f0",
                        stroke=FIELD, sw=1.8, rx=4))
        out.append(text(x0 + result_len * CELL / 2, 354, result, size=15, color=INK, bold=True))

        # лінійка байтів
        for k in (0, 5, 10):
            out.append(line(x0 + k * CELL, 372, x0 + k * CELL, 384, color=MUTED, sw=1.2))
            out.append(text(x0 + k * CELL, 400, str(k), size=12, color=MUTED))

        out.append(fitbox(px + 24, 424, 372, 82, note, size=13,
                          fill="#f4f6f8", stroke=MUTED, sw=1.4))
        return out

    p += panel(40, "один опис на двох", FIELD, 0, 5, "AAAAABBBBB", 10,
               ["позиція одна: запис B почався там,",
                "де скінчився запис A —",
                "у файлі всі 10 байтів"])
    p += panel(520, "два окремі описи", POS, 0, 0, "BBBBB", 5,
               ["позиції дві, обидві з нуля:",
                "B ліг поверх A —",
                "у файлі 5 байтів, половина зникла"])

    p.append(text(490, 570, "різниця лише в тому, скільки описів створено: dup і fork дають один, другий open — новий",
                  size=13.5, color=INK))

    render(os.path.join(OUT, "shared-offset.svg"), W, H, *p,
           title="одна позиція на двох — і дві позиції на той самий файл")


# ── Фіг. 3: час життя опису ─────────────────────────────────────────────────
# Ідея: опис не належить процесові; він живе, доки на нього хтось посилається,
# і посилання бувають не лише з таблиці дескрипторів.
def fig_refcount():
    W, H = 1000, 620
    p = []

    holders = [
        (25, ["fd 3", "у процесі 4021"]),
        (265, ["fd 5 у дитині", "успадковано через fork"]),
        (515, ["відображення mmap", "дескриптор уже закрито"]),
        (755, ["дескриптор у польоті", "SCM_RIGHTS ще не прийнято"]),
    ]
    for x, lines in holders:
        p.append(fitbox(x, 62, 220, 74, lines, size=13,
                        fill="#eef3fb", stroke=NEG, sw=1.5))

    p.append(fitbox(280, 246, 440, 110,
                    ["опис відкритого файлу",
                     "позиція · прапорці · право доступу",
                     "лічильник посилань = 4"],
                    size=15, fill="#eef7f0", stroke=FIELD, sw=2.0))

    p.append(arrow(135, 140, 372, 242, color=NEG))
    p.append(arrow(375, 140, 442, 242, color=NEG))
    p.append(arrow(625, 140, 558, 242, color=NEG))
    p.append(arrow(865, 140, 628, 242, color=NEG))

    p.append(fitbox(60, 436, 400, 116,
                    ["close() у одного власника",
                     "лічильник 4 → 3",
                     "опис живий: позиція й прапорці на місці"],
                    size=13.5, fill="#eef3fb", stroke=NEG, sw=1.6))
    p.append(fitbox(540, 436, 400, 116,
                    ["зник останній власник",
                     "лічильник 0 → опис звільнено",
                     "inode відпущено; якщо й імен немає — дані стерто"],
                    size=13.5, fill="#fdeeec", stroke=POS, sw=1.6))

    p.append(arrow(420, 360, 250, 430, color=NEG))
    p.append(arrow(580, 360, 750, 430, color=POS))

    render(os.path.join(OUT, "refcount.svg"), W, H, *p,
           title="опис живий, доки на нього хтось посилається")


# ── Фіг. 4 (вставка hist): будова таблиці fsp у першій редакції ─────────────
# Ідея: уже 1971 року процес тримав НЕ сам запис про відкриття, а лише його
# НОМЕР у спільній на всю машину таблиці fsp — тому fork і міг віддати
# дитині ті самі відкриття, просто збільшивши лічильник користувачів.
def fig_v1_fsp():
    W, H = 1000, 660
    p = []

    # процес
    p.append(rect(50, 56, 330, 190, fill="#ffffff", stroke=INK, sw=1.6, rx=10))
    p.append(text(215, 84, "u.fp процесу — 10 байтів", size=14, color=INK, bold=True))
    slots = [("0", "3"), ("1", "3"), ("2", "7"), ("3", "0")]
    for i, (idx, val) in enumerate(slots):
        y = 100 + i * 34
        p.append(text(84, y + 20, "слот " + idx, size=12.5, color=MUTED, anchor="start"))
        p.append(rect(180, y, 60, 26, fill="#eef3fb", stroke=NEG, sw=1.4, rx=4))
        p.append(text(210, y + 19, val, size=13.5, color=NEG, bold=True))
        p.append(text(268, y + 19, "номер запису" if val != "0" else "вільно",
                      size=12, color=MUTED, anchor="start"))

    # таблиця fsp
    p.append(rect(560, 56, 390, 300, fill="#ffffff", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(755, 84, "fsp — 50 записів на всю машину", size=14, color=FIELD, bold=True))
    p.append(text(755, 106, "по 8 байтів кожен", size=12.5, color=MUTED))

    p.append(fitbox(586, 124, 338, 30, "запис 1", size=13, fill="#f4f6f8", stroke=MUTED, sw=1.2))
    p.append(fitbox(586, 160, 338, 30, "запис 2", size=13, fill="#f4f6f8", stroke=MUTED, sw=1.2))
    p.append(fitbox(586, 196, 338, 118,
                    ["запис 3",
                     "i-число файлу (знак = режим доступу)",
                     "номер пристрою",
                     "покажчик читання-запису",
                     "скільки процесів користується: 2"],
                    size=12.5, fill="#eef7f0", stroke=FIELD, sw=1.8))
    p.append(fitbox(586, 320, 338, 26, "…", size=13, fill="#f4f6f8", stroke=MUTED, sw=1.2))

    p.append(arrow(246, 116, 580, 226, color=NEG))
    p.append(arrow(246, 150, 580, 244, color=NEG))

    # дитина
    p.append(rect(50, 300, 330, 122, fill="#ffffff", stroke=POS, sw=1.6, rx=10))
    p.append(text(215, 328, "дитина після fork — копія u.fp", size=14, color=POS, bold=True))
    p.append(fitbox(74, 344, 282, 62,
                    ["ті самі номери 3, 3, 7 —",
                     "ядро лише збільшує лічильник"],
                    size=12.5, fill="#fdeeec", stroke=POS, sw=1.4))
    p.append(arrow(360, 372, 580, 288, color=POS))

    p.append(fitbox(50, 470, 900, 150,
                    ["Процес не тримає ані позиції, ані режиму доступу: у нього лише номер запису.",
                     "Тому seek одного співвласника зсуває покажчик усім, хто має той самий номер,",
                     "а fork не копіює стан відкриття — він додає ще одного користувача запису.",
                     "Це будова першої редакції Unix, листопад 1971: ще без dup і без каналів."],
                    size=13.5, fill="#ffffff", stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, "v1-fsp.svg"), W, H, *p,
           title="перша редакція Unix: u.fp процесу і спільна таблиця fsp")


# ── Фіг. 5: рукостискання виміру (для досліду proj-shared-offset) ───────────
# Ідея: щоб зміряти спільність описів, дитина мусить бути ЖИВОЮ в момент
# виміру — звідси два канали-семафори навколо kcmp.
def fig_probe_handshake():
    W, H = 960, 660
    p = []

    # доріжки
    p.append(rect(50, 56, 380, 470, fill="#fbfcfd", stroke=MUTED, sw=1.3, rx=12))
    p.append(rect(530, 56, 380, 470, fill="#fbfcfd", stroke=MUTED, sw=1.3, rx=12))
    p.append(text(240, 80, "батько", size=15, color=NEG, bold=True))
    p.append(text(720, 80, "дитина", size=15, color=POS, bold=True))

    # крок 1 — батько
    p.append(fitbox(70, 96, 340, 58,
                    ["open(probe.txt) · write «AAAAA»",
                     "позиція опису: 0 → 5"],
                    size=13.5, fill="#eef3fb", stroke=NEG, sw=1.5))

    # fork
    p.append(text(240, 180, "fork()", size=13.5, color=MUTED, bold=True))
    p.append(arrow(300, 172, 700, 196, color=MUTED, sw=1.6))

    # крок 2 — дитина пише
    p.append(fitbox(550, 206, 340, 58,
                    ["write «BBBBB» тим самим fd",
                     "та сама позиція: 5 → 10"],
                    size=13.5, fill="#fdeeec", stroke=POS, sw=1.5))

    # up: «я записав»
    p.append(text(480, 292, "канал up: «я записав»", size=12.5, color=MUTED))
    p.append(arrow(548, 300, 412, 318, color=POS, sw=1.6))

    # крок 3 — вимір
    p.append(fitbox(70, 302, 340, 76,
                    ["fdinfo(батько) · fdinfo(дитина)",
                     "kcmp(KCMP_FILE)",
                     "дитина ЩЕ ЖИВА"],
                    size=13.5, fill="#eef7f0", stroke=FIELD, sw=1.7))

    # down: «можна виходити»
    p.append(text(480, 414, "канал down: «можна виходити»", size=12.5, color=MUTED))
    p.append(arrow(412, 422, 548, 440, color=NEG, sw=1.6))

    # крок 4 — вихід
    p.append(fitbox(550, 424, 340, 44, "_exit(0)",
                    size=13.5, fill="#fdeeec", stroke=POS, sw=1.5))
    p.append(fitbox(70, 462, 340, 44, "waitpid(kid)",
                    size=13.5, fill="#eef3fb", stroke=NEG, sw=1.5))

    p.append(fitbox(50, 552, 860, 82,
                    ["Без обох рукостискань дитина встигає вийти раніше за вимір:",
                     "тека /proc/<pid>/fdinfo зникає разом із процесом, а kcmp повертає ESRCH.",
                     "Зомбі теж не рятує — таблицю дескрипторів звільняють на _exit, а не на waitpid."],
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, "probe-handshake.svg"), W, H, *p,
           title="порядок виміру: дитина мусить дожити до kcmp")


# ── Фіг. 6: керувальне повідомлення SCM_RIGHTS ──────────────────────────────
# Ідея: дескриптор мандрує не як число в даних, а як керувальне повідомлення;
# один байт справжніх даних обов'язковий.
def fig_scm_message():
    W, H = 980, 560
    p = []

    # msghdr
    p.append(rect(50, 66, 340, 232, fill="#ffffff", stroke=NEG, sw=1.7, rx=10))
    p.append(text(220, 90, "struct msghdr", size=14, color=NEG, bold=True))
    p.append(fitbox(66, 104, 308, 40, "msg_iov  →", size=13, fill="#eef3fb", stroke=NEG, sw=1.3))
    p.append(fitbox(66, 150, 308, 40, "msg_iovlen = 1", size=13, fill="#f4f6f8", stroke=MUTED, sw=1.3))
    p.append(fitbox(66, 196, 308, 40, "msg_control  →", size=13, fill="#eef3fb", stroke=NEG, sw=1.3))
    p.append(fitbox(66, 242, 308, 40, "msg_controllen = CMSG_SPACE(4)",
                    size=13, fill="#f4f6f8", stroke=MUTED, sw=1.3))

    # iovec
    p.append(fitbox(470, 66, 460, 84,
                    ["iovec: один байт «x» — справжні дані",
                     "без них Linux керувального не надішле"],
                    size=13, fill="#eef7f0", stroke=FIELD, sw=1.6))
    p.append(arrow(376, 124, 464, 106, color=NEG, sw=1.6))

    # буфер керувальних даних
    p.append(rect(470, 200, 460, 180, fill="#ffffff", stroke=POS, sw=1.7, rx=10))
    p.append(text(700, 224, "буфер керувальних даних", size=13.5, color=POS, bold=True))
    p.append(fitbox(486, 238, 428, 72,
                    ["cmsg_len = CMSG_LEN(4)",
                     "cmsg_level = SOL_SOCKET",
                     "cmsg_type = SCM_RIGHTS"],
                    size=13, fill="#fdeeec", stroke=POS, sw=1.4))
    p.append(fitbox(486, 318, 296, 46, "CMSG_DATA: int fd = 3",
                    size=13, fill="#f4f6f8", stroke=INK, sw=1.4))
    p.append(fitbox(794, 318, 120, 46, "добивка", size=12.5,
                    fill="#f4f6f8", stroke=MUTED, sw=1.2))
    p.append(arrow(376, 216, 464, 254, color=NEG, sw=1.6))

    p.append(fitbox(50, 410, 880, 96,
                    ["Ядро переносить не число, а посилання: одержувач дістає інший номер",
                     "дескриптора й той самий опис відкритого файлу — з тією ж позицією.",
                     "Дескриптор «у польоті» вже тримає опис живим, навіть якщо відправник закрив свій."],
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, "scm-message.svg"), W, H, *p,
           title="як дескриптор їде сокетом: SCM_RIGHTS")


fig_three_levels()
fig_shared_offset()
fig_refcount()
fig_v1_fsp()
fig_probe_handshake()
fig_scm_message()
print("ok")
