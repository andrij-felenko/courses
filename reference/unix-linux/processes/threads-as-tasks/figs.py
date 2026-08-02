# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PURPLE = "#7a4fb0"
SOFT = "#fbfcff"
GREEN_T = "#eafaf0"
RED_T = "#fdecea"
BLUE_T = "#eaf0fd"


# ── 1. Спільне на групу задач ↔ своє в кожної задачі ───────────────────────────
def fig_shared_vs_own():
    W, H = 1080, 700
    p = []

    col_w = 480
    lx, rx0, top = 40, 560, 118

    p.append(fitbox(lx, 58, col_w, 44,
                    "Спільне на всю групу задач\n(структура одна, лічильник посилань = кількість потоків)",
                    size=13, fill=GREEN_T, stroke=FIELD, sw=1.8, color=FIELD, bold=True))
    p.append(fitbox(rx0, 58, col_w, 44,
                    "Своє в кожної задачі\n(лежить усередині task_struct, примірник лише власний)",
                    size=13, fill=BLUE_T, stroke=NEG, sw=1.8, color=NEG, bold=True))

    shared = [
        "mm_struct — відображення пам'яті:\nкод, купа, усі стеки, усі відображення файлів",
        "files_struct — таблиця дескрипторів:\nвідкритий тут файл миттю видно всім",
        "fs_struct — корінь, поточний каталог, umask",
        "sighand_struct — диспозиції сигналів:\nодин обробник на весь TGID",
        "signal_struct — ліміти ресурсів, таймери,\nрахунок процесорного часу, спільна черга сигналів",
        "nsproxy — набір просторів імен\n(тому потік не може піти у свій)",
        "TGID — номер програми, який повертає getpid()",
    ]
    own = [
        "TID — власний номер задачі (gettid)",
        "регістри й стек ядра (16 КіБ на x86-64)",
        "стек користувача — окрема ділянка mmap\nіз сторінкою-вартовим під нею",
        "блок локальних даних потоку (TLS):\nerrno, змінні __thread, покажчик у регістрі %fs",
        "маска сигналів, власна черга,\nальтернативний стек обробника",
        "nice, політика планування, набір дозволених ядер",
        "cred — ідентичність і можливості (!)",
    ]

    def col(x, items, accent, fill):
        out = []
        y = top
        for it in items:
            out.append(fitbox(x, y, col_w, 58, it, size=11, fill=fill, stroke=accent, sw=1.4, color=INK))
            y += 66
        return "".join(out), y

    frag, endy = col(lx, shared, FIELD, "#f4fbf6")
    p.append(frag)
    frag, endy = col(rx0, own, NEG, "#f5f8fe")
    p.append(frag)

    p.append(fitbox(lx, endy + 8, W - 2 * lx - 40, 46,
                    "cred стоїть праворуч, хоч POSIX вимагає спільних прав на всю програму: розрив закриває не ядро, "
                    "а libc — розсилкою внутрішнього сигналу всім потокам",
                    size=12, fill="#fff", stroke=PURPLE, sw=1.4, color=INK))

    p.append(text(W / 2, H - 16,
                  "питання «що станеться, якщо…» вирішує не слово «потік», а те, у якій із двох колонок лежить річ",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "shared-vs-own.svg"), W, H, *p,
           title="Група задач: що спільне, а що своє в кожного потоку")


# ── 2. Один адресний простір, кілька стеків, сторінки-вартові ─────────────────
def fig_thread_stacks():
    W, H = 1020, 720
    p = []

    MX, MW = 60, 420          # смуга адресного простору
    y = 66

    def band(y, h, label, accent, fill, size=12):
        return fitbox(MX, y, MW, h, label, size=size, fill=fill, stroke=accent, sw=1.6, color=INK)

    p.append(text(MX + MW / 2, 54, "високі адреси", size=11, color=MUTED))

    p.append(band(y, 62, "стек головної задачі\nросте вниз на вимогу", FIELD, GREEN_T))
    y += 62
    p.append(band(y, 40, "вільний проміжок до межі RLIMIT_STACK", MUTED, "#ffffff", size=11))
    y += 58

    # три стеки потоків із вартовими
    for i in (1, 2, 3):
        p.append(band(y, 52, "стек потоку %d — фіксовані 8 МіБ" % i, NEG, BLUE_T))
        y += 52
        p.append(band(y, 26, "сторінка-вартовий: жодних прав доступу", POS, RED_T, size=10))
        y += 44

    p.append(band(y, 46, "інші відображення: бібліотеки, файли, буфери", MUTED, FILL))
    y += 62
    p.append(band(y, 46, "купа — спільна на всю групу", FIELD, GREEN_T))
    y += 62
    p.append(band(y, 46, "код і статичні дані — спільні", FIELD, GREEN_T))
    p.append(text(MX + MW / 2, y + 70, "низькі адреси", size=11, color=MUTED))

    # праворуч — пояснення
    NX, NW = 545, 435
    notes = [
        ("Головний стек ростить ядро",
         "доторк нижче межі дає сторінковий збій,\nядро посуває межу — поки є запас до RLIMIT_STACK", FIELD, "#f4fbf6"),
        ("Стеки потоків ростити нікуди",
         "у спільному просторі вони росли б назустріч чужим\nділянкам, тому libc бере їх mmap-ом наперед", NEG, "#f5f8fe"),
        ("Сторінка-вартовий робить збій негайним",
         "переповнення впирається в неї й дає SIGSEGV\nзамість тихого псування сусіднього стека", POS, "#fdf5f4"),
        ("Резерв віртуальний, не фізичний",
         "1000 потоків = ~8.4 ГБ у VSZ,\nале лише ~8 МіБ реально зайнятих сторінок", PURPLE, "#f5f0fb"),
        ("Ділянку не віддають ядру",
         "після завершення потоку стек лишається\nв кеші libc — наступне створення бере готове", MUTED, "#ffffff"),
    ]
    ny = 66
    for head, body, accent, fill in notes:
        p.append(rect(NX, ny, NW, 96, fill=fill, stroke=accent, sw=1.6, rx=9))
        p.append(text(NX + 18, ny + 28, head, size=12.5, color=accent, anchor="start", bold=True))
        p.append(mtext(NX + 18, ny + 52, body, size=11, color=INK, anchor="start", lh=1.3))
        ny += 110

    p.append(text(W / 2, H - 14,
                  "усі задачі групи ділять один простір адрес; окремим у кожної лишається тільки її власний стек і блок TLS",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "thread-stacks.svg"), W, H, *p,
           title="Адресний простір багатопотокової програми")


# ── 3. Дві адреси доставки сигналу ────────────────────────────────────────────
def fig_signal_delivery():
    W, H = 1040, 620
    p = []

    # група задач
    GX, GY, GW, GH = 300, 150, 700, 300
    p.append(rect(GX, GY, GW, GH, fill="#fafbfc", stroke=INK, sw=2, rx=12))
    p.append(text(GX + 20, GY + 30, "група задач TGID 1200", size=14, color=INK, anchor="start", bold=True))

    # спільна черга
    p.append(fitbox(GX + 24, GY + 48, 300, 62,
                    "спільна черга групи\nсигнали, послані на номер 1200",
                    size=11.5, fill=GREEN_T, stroke=FIELD, sw=1.6, color=INK))

    tasks = [
        ("TID 1200", "маска: SIGTERM заблоковано", MUTED, "#f2f4f6"),
        ("TID 1203", "маска: порожня — може прийняти", FIELD, GREEN_T),
        ("TID 1204", "маска: порожня — може прийняти", FIELD, GREEN_T),
    ]
    tx = GX + 30
    for name, mask, accent, fill in tasks:
        p.append(rect(tx, GY + 136, 200, 118, fill=fill, stroke=accent, sw=1.8, rx=9))
        p.append(text(tx + 100, GY + 164, name, size=13, color=accent, bold=True))
        p.append(mtext(tx + 100, GY + 190, mask, size=10.5, color=INK, lh=1.25))
        p.append(fitbox(tx + 14, GY + 208, 172, 34, "власна черга задачі", size=10,
                        fill="#ffffff", stroke=MUTED, sw=1.1, color=MUTED))
        tx += 220

    p.append(fitbox(GX + 24, GY + 266, GW - 48, 24,
                    "таблиця диспозицій одна на групу: який би потік не отримав сигнал, виконається той самий обробник",
                    size=11, fill="#ffffff", stroke=PURPLE, sw=1.3, color=INK))

    # джерела зліва
    src = [
        ("kill 1200", "адресовано програмі: у спільну чергу,\nзвідти одній із незаблокованих задач", FIELD, GREEN_T, GY + 78),
        ("tgkill 1200, 1204", "адресовано задачі:\nу власну чергу саме цієї", NEG, BLUE_T, GY + 190),
        ("помилкова інструкція", "SIGSEGV, SIGFPE — вибору немає:\nтій задачі, що її виконала", POS, RED_T, GY + 272),
    ]
    for name, body, accent, fill, sy in src:
        p.append(rect(30, sy - 34, 236, 82, fill=fill, stroke=accent, sw=1.8, rx=9))
        p.append(text(148, sy - 10, name, size=12.5, color=accent, bold=True))
        p.append(mtext(148, sy + 10, body, size=10.5, color=INK, lh=1.25))
        p.append(arrow(270, sy + 8, GX - 8, sy + 8, color=accent, sw=1.8))

    # низ: смертельний сигнал
    p.append(fitbox(GX, GY + GH + 24, GW, 52,
                    "якщо диспозиція означає смерть — ядро завершує ВСЮ групу,\nхоч отримала сигнал лише одна задача",
                    size=13, fill=RED_T, stroke=POS, sw=1.8, color=POS, bold=True))

    p.append(text(W / 2, H - 14,
                  "надійний спосіб один: заблокувати сигнали в усіх потоках і читати їх з одного місця — sigwaitinfo або signalfd",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "signal-delivery.svg"), W, H, *p,
           title="Доставка сигналу: у групу задач і в окрему задачу")


# ── 4. Три області дії виклику ────────────────────────────────────────────────
def fig_scope_lanes():
    W, H = 1180, 940
    p = []

    CW = 340
    XS = [40, 420, 800]
    HEAD_Y, HEAD_H = 62, 74
    TOP = HEAD_Y + HEAD_H + 18
    STEP = 82
    ITEM_H = 70

    heads = [
        ("Ядро діє на всю групу",
         "поле лежить у спільній структурі\nз лічильником посилань", FIELD, GREEN_T),
        ("Ядро діє на одну задачу",
         "поле лежить усередині\nвласної task_struct", NEG, BLUE_T),
        ("Ядро діє на задачу,\nа libc вдає групу", "розсилка всім потокам\nповерх виклику, що бере одного",
         PURPLE, "#f5f0fb"),
    ]
    for x, (h1, h2, accent, fill) in zip(XS, heads):
        p.append(rect(x, HEAD_Y, CW, HEAD_H, fill=fill, stroke=accent, sw=2, rx=10))
        p.append(mtext(x + CW / 2, HEAD_Y + 24, h1, size=13.5, color=accent, bold=True, lh=1.25))
        p.append(mtext(x + CW / 2, HEAD_Y + (46 if "\n" not in h1 else 60), h2,
                       size=10.5, color=MUTED, lh=1.25))

    group_items = [
        "mm_struct\nmmap · mprotect · brk · madvise · mlockall",
        "files_struct\nopen · close · dup2 · fcntl(F_SETFD)",
        "fs_struct\nchdir · chroot · umask",
        "sighand_struct\nsigaction · signal",
        "signal_struct\nsetrlimit · alarm · setitimer · times",
        "номери групи\nsetpgid · setsid · getpgid · getppid",
        "кінець групи\nexit_group · execve · смертельний сигнал",
    ]
    task_items = [
        "планування\nnice · setpriority · sched_setscheduler",
        "розміщення на ядрах\nsched_setaffinity · getcpu",
        "черга до диска\nioprio_set",
        "сигнали, які прийме саме вона\nsigprocmask · sigaltstack · sigwaitinfo",
        "дрібні властивості\nPR_SET_NAME · PR_SET_PDEATHSIG",
        "права й можливості (сирі виклики)\nsetuid · setgid · capset",
        "фільтр викликів і простори імен\nseccomp без TSYNC · unshare · setns",
        "кінець задачі\nexit · tgkill · ptrace",
    ]
    fix_items = [
        "setuid · setgid · setresuid · setgroups\nglibc розсилає SIGSETXID усім потокам\nсвого списку й чекає підтверджень",
        "cap_set_proc\nсам по собі — лише свій потік;\n-lcap -lpsx і --wrap=pthread_create\nроблять із нього розсилку",
        "seccomp(…, SECCOMP_FILTER_FLAG_TSYNC)\nтут розсилку бере на себе саме ядро",
        "задача, народжена прямим clone()\nповз список libc — жодна розсилка\nїї не зачепить",
    ]

    def column(x, items, accent, fill, h=ITEM_H):
        out = []
        y = TOP
        for it in items:
            out.append(fitbox(x, y, CW, h, it, size=10.5, fill=fill, stroke=accent, sw=1.4, color=INK))
            y += STEP
        return "".join(out)

    p.append(column(XS[0], group_items, FIELD, "#f4fbf6"))
    p.append(column(XS[1], task_items, NEG, "#f5f8fe"))
    p.append(column(XS[2], fix_items, PURPLE, "#faf7fe", h=88))

    band_y = TOP + STEP * len(task_items) + 12
    p.append(fitbox(40, band_y, W - 80, 58,
                    "Назва нічого не обіцяє: PRIO_PROCESS, IOPRIO_WHO_PROCESS і аргумент pid у sched_setaffinity\n"
                    "усі беруть номер ЗАДАЧІ — renice й ionice по номеру програми міняють лише головний потік",
                    size=12.5, fill=RED_T, stroke=POS, sw=1.8, color=POS, bold=True))

    p.append(text(W / 2, H - 18,
                  "щоб дізнатися область дії виклику, питають не про слово «потік», а про те, у якій структурі лежить поле",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "scope-lanes.svg"), W, H, *p,
           title="Три області дії системного виклику в багатопотоковій програмі")


# ── 5. LinuxThreads ↔ NPTL (для історичної вставки) ───────────────────────────
def fig_linuxthreads_vs_nptl():
    W, H = 1180, 640
    p = []

    p.append(fitbox(30, 24, 540, 46,
                    "LinuxThreads (1996–2003)\nпотік = процес зі спільною пам'яттю",
                    size=13, fill=RED_T, stroke=POS, sw=1.8, color=POS, bold=True))
    p.append(fitbox(610, 24, 540, 46,
                    "NPTL (з 2003)\nпотік = задача в спільній групі задач",
                    size=13, fill=GREEN_T, stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    # ── ліва панель ───────────────────────────────────────────────────────────
    p.append(text(200, 108, "прохання трубою", size=10.5, color=MUTED))
    p.append(fitbox(45, 118, 190, 58, "головна задача\nPID 1200",
                    size=12, fill=SOFT, stroke=INK, sw=1.6, color=INK))
    p.append(fitbox(365, 118, 190, 58, "потік-керівник\nPID 1201",
                    size=12, fill=RED_T, stroke=POS, sw=1.8, color=POS))
    p.append(arrow(240, 147, 360, 147, color=MUTED, sw=1.6))

    p.append(line(460, 176, 460, 206, color=POS, sw=1.6))
    p.append(line(120, 206, 460, 206, color=POS, sw=1.6))
    for cx, tid in ((120, 1202), (290, 1203), (460, 1204)):
        p.append(arrow(cx, 206, cx, 232, color=POS, sw=1.6))
        p.append(fitbox(cx - 82, 234, 164, 62,
                        "потік\nPID %d" % tid,
                        size=12, fill="#fdf3f2", stroke=POS, sw=1.4, color=INK))

    p.append(fitbox(45, 312, 510, 56,
                    "усі потоки — діти керівника: він їх створює, а потім збирає через wait(),\nінакше кожен завершений лишався б зомбі",
                    size=11, fill="#ffffff", stroke=MUTED, sw=1.3, color=INK))
    p.append(fitbox(45, 382, 510, 176,
                    "що з цього виходило:\n\n"
                    "getpid() різний у кожному потоці, getppid() показує керівника\n"
                    "сигналів, адресованих програмі, не існує — тільки задачі\n"
                    "setuid() міняє права одного потоку, не всієї програми\n"
                    "SIGUSR1 і SIGUSR2 забрала бібліотека на власні потреби\n"
                    "стек у гнізді 2 МіБ за фіксованою сіткою → стеля на кількість потоків",
                    size=11, fill=RED_T, stroke=POS, sw=1.5, color=INK))

    # ── права панель ──────────────────────────────────────────────────────────
    p.append(rect(610, 96, 540, 200, fill="#f4fbf6", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(880, 122, "група задач, TGID 1200 — це й є «процес»",
                  size=12, color=FIELD, bold=True))
    for i, (tid, label) in enumerate(((1200, "лідер групи"), (1201, ""), (1202, ""), (1203, ""))):
        x = 632 + i * 130
        p.append(fitbox(x, 142, 116, 66,
                        ("TID %d\n%s" % (tid, label)) if label else "TID %d" % tid,
                        size=11.5, fill="#ffffff", stroke=FIELD, sw=1.4, color=INK))
    p.append(fitbox(632, 224, 506, 52,
                    "getpid() у кожної повертає 1200 — назовні це одна програма",
                    size=11.5, fill="#ffffff", stroke=MUTED, sw=1.3, color=INK))

    p.append(fitbox(610, 312, 540, 56,
                    "потік створює потік сам, одним clone(): посередника немає,\nтож створення різних потоків іде паралельно",
                    size=11, fill="#ffffff", stroke=MUTED, sw=1.3, color=INK))
    p.append(fitbox(610, 382, 540, 176,
                    "що для цього додали в ядро (гілка 2.5):\n\n"
                    "спільна черга сигналів групи + tgkill() у конкретну задачу\n"
                    "exit_group() — завершити всю групу одним викликом\n"
                    "CLONE_SETTLS — блок локальних даних потоку від ядра\n"
                    "CLONE_CHILD_CLEARTID — сповіщення про смерть через пам'ять,\n"
                    "тому pthread_join() чекає на слові, а не на wait()\n"
                    "futex — м'ютекс без входу в ядро, поки немає суперечки",
                    size=11, fill=GREEN_T, stroke=FIELD, sw=1.5, color=INK))

    p.append(text(W / 2, H - 16,
                  "змінилася не бібліотека, а межа між нею й ядром: керівник зник, бо ядро взяло на себе те, що він робив вручну",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "linuxthreads-vs-nptl.svg"), W, H, *p,
           title="LinuxThreads і NPTL: що змінилося")


# ── Що всередині однієї ділянки, яку libc зве стеком потоку ───────────────────
def fig_stack_block():
    W, H = 1140, 620
    p = []

    BX, BW = 60, 360
    bands = [
        (76, 56, "struct pthread — службова структура libc\nсюди вказує %fs, це саме число дає pthread_self()", PURPLE, "#f5f0fb"),
        (132, 52, "статичний блок TLS: own_counter, errno\nза від'ємними зсувами від %fs", PURPLE, "#faf7fe"),
        (184, 44, "верхівка стека, уже витрачена\n(&on_stack — точка тут)", NEG, "#e3ebfb"),
        (228, 168, "вільний стек потоку — росте вниз\n8 388 608 байтів від lo до hi", NEG, BLUE_T),
        (396, 46, "сторінка-вартовий 4 КіБ\nу maps це ---p: жодних прав", POS, RED_T),
    ]
    for y, h, s, accent, fill in bands:
        p.append(fitbox(BX, y, BW, h, s, size=11.5, fill=fill, stroke=accent, sw=1.6, color=INK))

    p.append(text(BX + BW / 2, 66, "високі адреси", size=10.5, color=MUTED))
    p.append(text(BX + BW / 2, 462, "низькі адреси", size=10.5, color=MUTED))

    marks = [(76, "hi — кінець ділянки"), (396, "lo — початок стека"), (442, "B — початок ділянки")]
    for y, s in marks:
        p.append(line(BX + BW + 6, y, 496, y, color=MUTED, sw=1.2, dash="4 3"))
        p.append(text(502, y + 4, s, size=11, color=MUTED, anchor="start"))

    WX, WW = 700, 400
    wits = [
        ("Свідок 1 — бібліотека",
         "pthread_attr_getstack → lo і size\npthread_attr_getguardsize → 4096\npthread_self() → адреса TCB",
         FIELD, "#f4fbf6", 76),
        ("Свідок 2 — ядро",
         "/proc/<pid>/maps: дві сусідні ділянки —\n---p завширшки з вартового й rw-p завширшки\nз size; /proc/<pid>/task/<tid>/ — свій каталог",
         NEG, "#f5f8fe", 208),
        ("Свідок 3 — сама програма",
         "&on_stack лежить усередині [lo, hi)\n&own_counter — трохи нижче від %fs\n&group_counter однакова в усіх задач",
         PURPLE, "#f7f3fd", 340),
    ]
    for head, body, accent, fill, y in wits:
        p.append(rect(WX, y, WW, 118, fill=fill, stroke=accent, sw=1.8, rx=9))
        p.append(text(WX + 18, y + 28, head, size=13, color=accent, anchor="start", bold=True))
        p.append(mtext(WX + 18, y + 54, body, size=11, color=INK, anchor="start", lh=1.35))

    p.append(fitbox(60, 490, W - 120, 62,
                    "lo = B + вартовий   ·   size = розмір ділянки − вартовий   ·   hi = lo + size = кінець ділянки\n"
                    "збіг усіх трьох свідків і є перевіркою: одне джерело дає твердження, три — факт",
                    size=12.5, fill="#ffffff", stroke=PURPLE, sw=1.6, color=INK))

    p.append(text(W / 2, H - 16,
                  "верхівку ділянки libc забрала собі: TCB і статичний TLS лежать усередині того, що вона зве стеком",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "stack-block.svg"), W, H, *p,
           title="Ділянка стека одного потоку зсередини")


if __name__ == "__main__":
    fig_shared_vs_own()
    fig_thread_stacks()
    fig_signal_delivery()
    fig_scope_lanes()
    fig_linuxthreads_vs_nptl()
    fig_stack_block()
    print("OK: figures written to", OUT)
