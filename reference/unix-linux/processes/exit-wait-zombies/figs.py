# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREY_S = "#c8ced6"
BLUE_F = "#eef3fb"
RED_F = "#fdeeec"
GREEN_F = "#eef7f0"


# ── Фіг. 1: смерть у два кроки ──────────────────────────────────────────────
# Ідея: завершення процесу — не одна подія, а дві. Перша звільняє все дороге,
# але лишає ідентичність і результат; друга (wait батька) прибирає й це.
def fig_death_two_stages():
    W, H = 1180, 780
    p = []

    COLS = [
        (180, "живий процес", NEG, BLUE_F,
         ["адресний простір і відображення",
          "таблиця дескрипторів",
          "таймери, замки, черга сигналів",
          "номер PID і місце в дереві",
          "право виконуватися"],
         ["нічого ще не звільнено"],
         ["ps показує R або S"]),
        (590, "зомбі", POS, RED_F,
         ["рядок у таблиці процесів",
          "номер PID — досі зайнятий",
          "код виходу або сигнал смерті",
          "лічильники витраченого часу",
          "посилання на батька"],
         ["адресний простір цілком",
          "усі дескриптори закрито",
          "таймери й замки знято",
          "стек ядра звільнено",
          "діти перечеплені до підбирача"],
         ["ps показує Z, «<defunct>»",
          "сигнали на нього не діють"]),
        (1000, "прибрано", FIELD, GREEN_F,
         ["нічого:",
          "запису про процес більше немає"],
         ["рядок таблиці звільнено",
          "номер PID знову вільний"],
         ["процесу не існує;",
          "wait на нього дасть ECHILD"]),
    ]

    CW = 300
    for cx, name, color, fill, keeps, freed, note in COLS:
        x = cx - CW / 2
        p.append(fitbox(x, 80, CW, 52, name, size=16, fill=fill, stroke=color,
                        sw=1.8, bold=True, color=color))
        p.append(text(cx, 168, "що система ще тримає", size=13, color=MUTED, bold=True))
        p.append(fitbox(x, 182, CW, 152, keeps, size=13, fill=fill, stroke=color, sw=1.5))
        p.append(text(cx, 372, "чого вже немає", size=13, color=MUTED, bold=True))
        p.append(fitbox(x, 386, CW, 156, freed, size=13, fill="#f4f6f8",
                        stroke=GREY_S, sw=1.3, color=MUTED))
        p.append(fitbox(x, 580, CW, 76, note, size=13, fill=BG, stroke=color, sw=1.4))

    # переходи між станами
    p.append(arrow(336, 106, 434, 106, color=INK))
    p.append(text(385, 84, "exit()", size=13.5, color=INK, bold=True))
    p.append(arrow(746, 106, 844, 106, color=INK))
    p.append(text(795, 84, "wait()", size=13.5, color=INK, bold=True))

    p.append(fitbox(30, 690, 1120, 66,
                    ["Перший крок робить сам процес і ядро — він звільняє все, за що платить пам'яттю.",
                     "Другий робить БАТЬКО, забираючи результат: доти запис мусить існувати, бо результат ще нікому не віддано."],
                    size=13.5, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "death-two-stages.svg"), W, H, *p,
           title="Завершення у два кроки: що звільняють одразу, а що чекає на wait")


# ── Фіг. 2: SIGCHLD не чергується ───────────────────────────────────────────
# Ідея: сигналів доставлено МЕНШЕ, ніж смертей. Тому обробник, що кличе wait
# один раз, лишає частину дітей зомбі — рятує тільки цикл із WNOHANG.
def fig_sigchld_coalescing():
    W, H = 1100, 720
    p = []

    DEATHS = [(380, "A"), (415, "B"), (740, "C"), (778, "D"), (812, "E")]
    SIGS = [415, 812]

    p.append(text(550, 62, "п'ять дітей завершуються двома тісними групами — а сигналів доставлено два",
                  size=14.5, color=INK, bold=True))
    p.append(fitbox(300, 92, 500, 82,
                    ["SIGCHLD — звичайний сигнал, він не чергується:",
                     "другий примірник, що застав перший ще не",
                     "доправленим, просто зникає"],
                    size=13, fill=GREEN_F, stroke=FIELD, sw=1.4))

    # лейбли доріжок
    p.append(text(230, 250, "процеси-діти", size=13.5, color=MUTED, anchor="end", bold=True))
    p.append(text(230, 340, "сигнал SIGCHLD", size=13.5, color=MUTED, anchor="end", bold=True))
    p.append(text(230, 430, "обробник у батька", size=13.5, color=MUTED, anchor="end", bold=True))

    # доріжка 1: смерті
    p.append(line(250, 246, 1060, 246, color=GREY_S, sw=1.4, dash="4 5"))
    for x, name in DEATHS:
        p.append(circle(x, 246, 11, fill=RED_F, stroke=POS, sw=2.0))
        p.append(text(x, 218, name, size=13.5, color=POS, bold=True))

    # доріжка 2: доставки
    p.append(line(250, 336, 1060, 336, color=GREY_S, sw=1.4, dash="4 5"))
    for x in SIGS:
        p.append(circle(x, 336, 11, fill=BLUE_F, stroke=NEG, sw=2.2))

    for x, _ in DEATHS:
        target = SIGS[0] if x < 600 else SIGS[1]
        p.append(arrow(x, 258, target - (0 if x == target else 4), 322, color=POS, sw=1.5))

    # доріжка 3: обробник
    for x in SIGS:
        p.append(arrow(x, 348, x, 402, color=NEG, sw=1.6))
        p.append(fitbox(x - 78, 406, 156, 46, "обробник", size=13.5,
                        fill=BLUE_F, stroke=NEG, sw=1.6))

    p.append(line(250, 490, 1060, 490, color=INK, sw=1.8))
    p.append(text(1064, 495, "час", size=13, color=INK, anchor="start"))

    p.append(fitbox(90, 526, 440, 150,
                    ["обробник кличе waitpid() ОДИН раз",
                     "",
                     "прибрано 2 дітей із 5",
                     "троє лишаються зомбі назавжди"],
                    size=13.5, fill=RED_F, stroke=POS, sw=1.6))
    p.append(fitbox(570, 526, 440, 150,
                    ["обробник крутить цикл",
                     "while (waitpid(-1, &st, WNOHANG) > 0)",
                     "",
                     "прибрано всіх 5"],
                    size=13.5, fill=GREEN_F, stroke=FIELD, sw=1.6))

    render(os.path.join(OUT, "sigchld-coalescing.svg"), W, H, *p,
           title="Смертей п'ять, сигналів два: чому прибирати треба циклом")


# ── Фіг. 3: одне число — три різні звістки ──────────────────────────────────
# Ідея: статус, який повертає wait, — це не «код виходу». Молодший байт каже,
# ЯК саме процес скінчився, і лише від цього залежить, що означає старший.
def fig_status_word():
    W, H = 1150, 700
    p = []

    X0, CWD = 60.0, 42.0
    ROWS = [
        (124, "процес вийшов сам:  exit(3)  →  статус 0x0300",
         0x03, 0x00, "e" * 8 + "-" * 8,
         ("код виходу = 3", NEG), ("усі нулі → процес вийшов сам", MUTED),
         ["WIFEXITED(s)    → істина", "WEXITSTATUS(s)  → 3"]),
        (294, "убито сигналом, з дампом:  SIGSEGV  →  0x008B",
         0x00, 0x8b, "-" * 8 + "c" + "s" * 7,
         ("не вживається", MUTED), ("біт дампа + номер сигналу 11", POS),
         ["WIFSIGNALED(s)  → істина", "WTERMSIG(s)     → 11 (SIGSEGV)",
          "WCOREDUMP(s)    → істина"]),
        (464, "зупинено, а не вбито:  SIGTSTP  →  0x147F",
         0x14, 0x7f, "s" * 8 + "m" * 8,
         ("номер сигналу зупинки = 20", POS), ("0x7F — позначка «зупинено»", FIELD),
         ["WIFSTOPPED(s)   → істина", "WSTOPSIG(s)     → 20 (SIGTSTP)"]),
    ]

    ROLE = {
        "e": (BLUE_F, NEG), "s": (RED_F, POS),
        "c": (GREEN_F, FIELD), "m": (GREEN_F, FIELD), "-": ("#f4f6f8", GREY_S),
    }

    p.append(text(X0 + 4 * CWD, 64, "старший байт", size=13, color=MUTED, bold=True))
    p.append(text(X0 + 12 * CWD, 64, "молодший байт", size=13, color=MUTED, bold=True))
    for i in range(16):
        p.append(text(X0 + i * CWD + CWD / 2, 90, str(15 - i), size=11, color=MUTED))

    for ytop, caption, hi, lo, roles, seg_a, seg_c, macros in ROWS:
        bits = format(hi, "08b") + format(lo, "08b")
        p.append(text(X0, ytop, caption, size=14.5, color=INK, anchor="start", bold=True))
        for i, ch in enumerate(bits):
            fill, stroke = ROLE[roles[i]]
            p.append(fitbox(X0 + i * CWD, ytop + 18, CWD, 46, ch, size=15,
                            fill=fill, stroke=stroke, sw=1.4, rx=4))
        p.append(fitbox(X0, ytop + 76, 8 * CWD, 34, seg_a[0], size=13,
                        fill=BG, stroke=seg_a[1], sw=1.3, color=seg_a[1]))
        p.append(fitbox(X0 + 8 * CWD, ytop + 76, 8 * CWD, 34, seg_c[0], size=13,
                        fill=BG, stroke=seg_c[1], sw=1.3, color=seg_c[1]))
        p.append(fitbox(780, ytop + 6, 340, 92, macros, size=13,
                        fill="#f4f6f8", stroke=GREY_S, sw=1.3))

    p.append(fitbox(60, 604, 1060, 66,
                    ["Одне ціле число несе три різні звістки, і розрізняє їх молодший байт:",
                     "нуль — процес вийшов сам, 0x7F — його зупинено, будь-що інше — номер сигналу, що його вбив."],
                    size=13.5, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "status-word.svg"), W, H, *p,
           title="Статус від wait: як 16 бітів кодують три різні долі")


# ── Фіг. 4: чотири долі мертвої дитини ──────────────────────────────────────
# Ідея: зомбі — не окремий різновид збою, а один із чотирьох варіантів, і
# єдиний, у якому результат нікому не віддано й ніхто по нього не прийде.
def fig_dead_child_fates():
    W, H = 1220, 740
    p = []

    CWD, GAP = 280, 20
    X0 = 20
    COLS = [
        (FIELD, GREEN_F, ["батько кличе wait()"],
         ["wait, waitpid або waitid", "блокує або питає з WNOHANG"],
         ["ядро віддає статус", "і звільняє запис задачі", "номер PID знову вільний"],
         ["нормальний перебіг"],
         ["код виходу: доставлено"]),
        (POS, RED_F, ["батько живий,", "але не чекає"],
         ["SIGCHLD типово ігнорується,", "тож ніщо не нагадує"],
         ["запис лишається зомбі", "стільки, скільки живе батько"],
         ["зомбі накопичуються,", "номери PID зайняті"],
         ["код виходу: чекає вічно"]),
        (NEG, BLUE_F, ["батько поставив SIGCHLD", "у SIG_IGN"],
         ["або sigaction із прапорцем", "SA_NOCLDWAIT"],
         ["ядро прибирає дитину саме,", "зомбі не виникає взагалі"],
         ["wait поверне ECHILD:", "чекати вже нема на кого"],
         ["код виходу: утрачено"]),
        (INK, "#f4f6f8", ["батько помер раніше"],
         ["дитину перечеплено", "до підбирача або до PID 1"],
         ["новий батько дістає SIGCHLD", "і забирає статус"],
         ["дерево не рветься,", "прибирання гарантоване"],
         ["код виходу: не тому,", "хто його запускав"]),
    ]

    for i, (color, fill, head, cond, out, verdict, status) in enumerate(COLS):
        x = X0 + i * (CWD + GAP)
        cx = x + CWD / 2
        p.append(fitbox(x, 66, CWD, 62, head, size=14.5, fill=fill, stroke=color,
                        sw=1.8, bold=True, color=color))
        p.append(arrow(cx, 132, cx, 158, color=color, sw=1.5))
        p.append(fitbox(x, 162, CWD, 92, cond, size=13, fill=BG, stroke=GREY_S, sw=1.3))
        p.append(arrow(cx, 258, cx, 284, color=color, sw=1.5))
        p.append(fitbox(x, 288, CWD, 100, out, size=13, fill=fill, stroke=color, sw=1.5))
        p.append(arrow(cx, 392, cx, 418, color=color, sw=1.5))
        p.append(fitbox(x, 422, CWD, 92, verdict, size=13, fill=BG, stroke=color, sw=1.4))
        p.append(fitbox(x, 548, CWD, 72, status, size=13.5, fill="#f4f6f8",
                        stroke=INK, sw=1.3, bold=True))
        p.append(arrow(cx, 518, cx, 544, color=color, sw=1.5))

    p.append(fitbox(20, 650, 1180, 66,
                    ["Зомбі — не окремий різновид збою, а єдиний із чотирьох варіантів, у якому результат нікому не віддано",
                     "й ніхто по нього не прийде. Три інші закінчуються тим, що запис про померлого зникає."],
                    size=13.5, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "dead-child-fates.svg"), W, H, *p,
           title="Чотири долі мертвої дитини — і лише одна з них лишає зомбі")


# ── Фіг. 5 (вставка api): дві маски одного аргументу options ────────────────
# Ідея: options в усіх викликів родини — те саме 32-бітне слово, але ядро
# перевіряє його ДВОМА різними масками, тож частина бітів законна лише в waitid.
def fig_options_masks():
    W, H = 1400, 440
    p = []

    LX, LW = 24, 196
    X0, CW, GAP = 234, 135, 8
    HDR_Y, HDR_H = 54, 62
    MEAN_Y, MEAN_H = 124, 82
    L1_Y, L1_H = 214, 46
    L2_Y, L2_H = 268, 46
    NOTE_Y, NOTE_H = 336, 72

    OK_F, BAD_F = GREEN_F, RED_F

    FLAGS = [
        ("WNOHANG", "0x0000 0001",
         ["не блокуватися:", "якщо готових", "немає — вийти", "негайно"],
         ("приймає", True), (["приймає"], True)),
        ("WUNTRACED", "0x0000 0002",
         ["повідомляти", "й про зупинених", "дітей, а не лише", "про мертвих"],
         ("приймає", True), (["той самий біт —", "WSTOPPED"], True)),
        ("WEXITED", "0x0000 0004",
         ["повідомляти", "про мертвих —", "waitid просить", "це явно"],
         ("EINVAL", False), (["приймає"], True)),
        ("WCONTINUED", "0x0000 0008",
         ["повідомляти", "про відновлених", "сигналом", "SIGCONT"],
         ("приймає", True), (["приймає"], True)),
        ("WNOWAIT", "0x0100 0000",
         ["прочитати статус,", "не забираючи:", "зомбі лишається", "на місці"],
         ("EINVAL", False), (["приймає"], True)),
        ("__WNOTHREAD", "0x2000 0000",
         ["лише діти цього", "потоку, а не", "всієї групи", "потоків"],
         ("приймає", True), (["приймає"], True)),
        ("__WALL", "0x4000 0000",
         ["будь-яка дитина,", "хоч би який", "сигнал шле", "при смерті"],
         ("приймає", True), (["приймає"], True)),
        ("__WCLONE", "0x8000 0000",
         ["лише діти, що", "шлють не SIGCHLD", "(створені clone)"],
         ("приймає", True), (["приймає"], True)),
    ]

    p.append(fitbox(LX, HDR_Y, LW, HDR_H, ["прапорець", "і його біт"],
                    size=14, fill=BLUE_F, stroke=NEG, sw=1.6, bold=True, color=NEG))
    p.append(fitbox(LX, MEAN_Y, LW, MEAN_H, ["що він вмикає"],
                    size=14, fill=BG, stroke=GREY_S, sw=1.3, bold=True, color=MUTED))
    p.append(fitbox(LX, L1_Y, LW, L1_H, ["wait · waitpid", "wait3 · wait4"],
                    size=14, fill="#f4f6f8", stroke=INK, sw=1.5, bold=True))
    p.append(fitbox(LX, L2_Y, LW, L2_H, ["waitid"],
                    size=14, fill="#f4f6f8", stroke=INK, sw=1.5, bold=True))

    for i, (name, bits, meaning, l1, l2) in enumerate(FLAGS):
        x = X0 + i * (CW + GAP)
        p.append(fitbox(x, HDR_Y, CW, HDR_H, [name, bits],
                        size=13, fill=BLUE_F, stroke=NEG, sw=1.6, bold=True, color=NEG))
        p.append(fitbox(x, MEAN_Y, CW, MEAN_H, meaning,
                        size=12, fill=BG, stroke=GREY_S, sw=1.3))
        for (val, ok), yy, hh in ((l1, L1_Y, L1_H), (l2, L2_Y, L2_H)):
            p.append(fitbox(x, yy, CW, hh, val, size=13,
                            fill=OK_F if ok else BAD_F,
                            stroke=FIELD if ok else POS, sw=1.5,
                            color=FIELD if ok else POS, bold=not ok))

    p.append(fitbox(LX, NOTE_Y, W - 2 * LX, NOTE_H,
                    ["waitid додатково вимагає щонайменше одного з WEXITED, WSTOPPED, WCONTINUED — без жодного з них теж EINVAL.",
                     "__WALL переважає __WCLONE: коли стоїть __WALL, ядро бере будь-яку дитину, і __WCLONE уже нічого не звужує."],
                    size=13.5, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "wait-options-masks.svg"), W, H, *p,
           title="Один аргумент options — дві різні маски перевірки в ядрі")


fig_death_two_stages()
fig_sigchld_coalescing()
fig_status_word()
fig_dead_child_fates()
fig_options_masks()
print("готово:", OUT)


# ── Фіг. 6 (вставка hist): розкол SIGCLD / SIGCHLD і його розсуд ────────────
def fig_sigcld_schism():
    W, H = 1260, 640
    p = []

    ROOT = (40, 250, 280, 140)
    p.append(fitbox(ROOT[0], ROOT[1], ROOT[2], ROOT[3],
                    ["спільний корінь",
                      "1971 · wait у першій редакції",
                      "1973—74 · стан SZOMB у ядрі",
                      "батько мусить прийти по статус"],
                    size=13.5, fill=BG, stroke=INK, sw=1.8))

    UP_H = (420, 90, 380, 46)
    p.append(fitbox(UP_H[0], UP_H[1], UP_H[2], UP_H[3],
                    "System III, 1980 — SIGCLD (18)",
                    size=15, fill=RED_F, stroke=POS, sw=1.8, bold=True, color=POS))
    p.append(fitbox(420, 144, 380, 160,
                    ["сенс: «дитина померла»",
                      "SIG_IGN — ядро прибирає зомбі саме",
                      "обробник не скидається на типову дію",
                      "сигнали не зливаються: по одному на смерть"],
                    size=13, fill=BG, stroke=GREY_S, sw=1.4))

    LO_H = (420, 396, 380, 46)
    p.append(fitbox(LO_H[0], LO_H[1], LO_H[2], LO_H[3],
                    "4.1cBSD / 4.2BSD, 1982—83 — SIGCHLD (20)",
                    size=15, fill=BLUE_F, stroke=NEG, sw=1.8, bold=True, color=NEG))
    p.append(fitbox(420, 450, 380, 160,
                    ["сенс: «стан дитини змінився»",
                      "приходить і на зупинку та відновлення",
                      "звичайний сигнал: тісні смерті зливаються",
                      "SIG_IGN нічого не міняє — зомбі лишаються"],
                    size=13, fill=BG, stroke=GREY_S, sw=1.4))

    p.append(fitbox(890, 200, 330, 46, "POSIX розсуджує",
                    size=15, fill=GREEN_F, stroke=FIELD, sw=1.8, bold=True, color=FIELD))
    p.append(fitbox(890, 254, 330, 190,
                    ["1988 · ім'я SIGCHLD, виклик waitpid",
                      "1988 · SA_NOCLDSTOP — «лише смерті»",
                      "1990 · SIG_IGN для SIGCHLD заборонено",
                      "2001 · SIG_IGN і SA_NOCLDWAIT узаконено",
                      "Linux · SIGCLD — просто інше ім'я"],
                    size=13, fill=BG, stroke=GREY_S, sw=1.4))

    p.append(arrow(324, 300, 416, 200, color=POS))
    p.append(arrow(324, 340, 416, 440, color=NEG))
    p.append(arrow(804, 224, 886, 290, color=POS))
    p.append(arrow(804, 476, 886, 410, color=NEG))

    render(os.path.join(OUT, "sigcld-schism.svg"), W, H, *p,
           title="Один слот, дві задачі: як розійшлися SIGCLD і SIGCHLD і хто їх помирив")


fig_sigcld_schism()
