# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: порядок дій execve і точка неповернення ─────────────────────────
# Ідея: усе, що вміє відмовляти, ядро робить, поки старий образ ще цілий.
# Після межі відмовляти нема кому — лишається тільки вбити процес.
def fig_exec_timeline():
    W, H = 1020, 880
    p = []

    LX, LW = 50.0, 520.0          # колонка етапів
    RX, RW = 610.0, 360.0         # колонка наслідку відмови
    BH, STEP = 62.0, 78.0

    p.append(text(W / 2, 40, "execve: спершу все, що може відмовити", size=16,
                  color=INK, bold=True))

    before = [
        ("відкрити файл, перевірити право на виконання,\nnoexec і чи не пише в файл хтось інший",
         "−1:  EACCES · ENOENT · ETXTBSY"),
        ("прочитати перші байти й запропонувати їх\nобробникам форматів: ELF, «#!», інші",
         "−1:  ENOEXEC"),
        ("розібрати заголовки, знайти інтерпретатор\n(завантажувач або інтерпретатор сценарію)",
         "−1:  ENOENT · ELOOP"),
        ("скопіювати argv і envp у нове відображення:\nстарий простір зараз зникне",
         "−1:  E2BIG · ENOMEM"),
    ]
    after = [
        "поставити нове відображення пам'яті,\nвикинути старе",
        "знищити решту потоків без прибирання,\nскинути спіймані сигнали на типову дію",
        "розкласти сегменти з файлу, стек,\nдопоміжний вектор",
        "регістри на точку входу —\nвиконується вже інша програма",
    ]

    y = 76.0
    for stage, fail in before:
        p.append(fitbox(LX, y, LW, BH, stage.split("\n"), size=13.5,
                        fill="#eef3fb", stroke=NEG, sw=1.5))
        p.append(fitbox(RX, y + 10, RW, BH - 20, fail, size=13,
                        fill="#ffffff", stroke="#c8ced6", sw=1.2))
        y += STEP

    # межа
    y += 8
    p.append(line(LX, y, W - 50, y, color=POS, sw=2.6, dash="9 6"))
    p.append(text(LX + 8, y - 12, "точка неповернення", size=14.5, color=POS,
                  anchor="start", bold=True))
    y += 26

    y_first_after = y
    for stage in after:
        p.append(fitbox(LX, y, LW, BH, stage.split("\n"), size=13.5,
                        fill="#fdeeec", stroke=POS, sw=1.5))
        y += STEP

    p.append(fitbox(RX, y_first_after + 60, RW, 130,
                    ["старої програми вже немає,",
                     "нової ще немає — повертати",
                     "−1 нема кому й нікуди.",
                     "Будь-яка помилка тут:",
                     "ядро надсилає SIGSEGV",
                     "(до версії 3.17 — SIGKILL)"],
                    size=13, fill="#fdeeec", stroke=POS, sw=1.5))

    p.append(fitbox(LX, y + 12, W - 2 * LX, 56,
                    ["Ззовні виклик атомарний: процес або досі виконує стару програму й має errno,",
                     "або вже виконує нову. Проміжного стану програміст не бачить ніколи."],
                    size=13.5, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "exec-timeline.svg"), W, H, *p,
           title="Порядок дій execve і точка неповернення")


# ── Фіг. 2: що переживає заміну образу ──────────────────────────────────────
# Ідея: не перелік винятків, а одне правило. Переживає те, на що можна
# послатися числом чи іменем у ядрі; гине те, на що можна послатися лише
# адресою всередині старого образу. Диспозиція сигналу розпадається рівно так.
def fig_exec_survives():
    W, H = 1040, 700
    p = []

    CW = 450.0
    LX, RX = 50.0, 540.0

    p.append(text(W / 2, 40, "Правило: переживає запис у ядрі, гине адреса в образі",
                  size=16, color=INK, bold=True))

    p.append(text(LX + CW / 2, 78, "переживає заміну", size=15, color=NEG, bold=True))
    p.append(text(RX + CW / 2, 78, "гине разом зі старим образом", size=15, color=POS, bold=True))

    p.append(fitbox(LX, 94, CW, 300,
                    ["номер процесу, батько, група, сеанс",
                     "керівний термінал",
                     "справжні uid і gid, додаткові групи",
                     "поточний і кореневий каталоги, umask",
                     "дескриптори без позначки close-on-exec",
                     "обмеження ресурсів, nice, спожитий час",
                     "блокування записів у файлах (fcntl)",
                     "маска сигналів і черга нерозданих",
                     "alarm і три інтервальні таймери"],
                    size=13.5, fill="#eef3fb", stroke=NEG, sw=1.6))

    p.append(fitbox(RX, 94, CW, 300,
                    ["усі відображення: код, дані, купа, стеки",
                     "ділянки mmap і спільна пам'ять",
                     "значення регістрів",
                     "решта потоків — без жодного прибирання",
                     "обробники atexit, каталогові потоки",
                     "альтернативний стек сигналів, замки mlock",
                     "таймери, створені timer_create",
                     "середовище обчислень з рухомою комою",
                     "дескриптори з позначкою close-on-exec"],
                    size=13.5, fill="#fdeeec", stroke=POS, sw=1.6))

    p.append(text(W / 2, 434, "перевірка правила: диспозиція сигналу розпадається за ним надвоє",
                  size=14.5, color=INK, bold=True))

    TW, GAP = 306.0, 26.0
    X0 = (W - (3 * TW + 2 * GAP)) / 2
    cells = [
        (["спійманий сигнал", "— це АДРЕСА обробника", "у старому образі",
          "→ скинуто на типову дію"], POS, "#fdeeec"),
        (["«ігнорувати» й «типова дія»", "— це позначки, не адреси",
          "→ лишаються як були"], NEG, "#eef3fb"),
        (["маска й черга нерозданих", "живуть у структурах ядра",
          "→ переходять цілими"], NEG, "#eef3fb"),
    ]
    for i, (lines, color, fill) in enumerate(cells):
        p.append(fitbox(X0 + i * (TW + GAP), 452, TW, 110, lines, size=13,
                        fill=fill, stroke=color, sw=1.5))

    p.append(fitbox(50, 590, W - 100, 68,
                    ["Той самий поділ пояснює таймери: alarm і setitimer названі сталими, які знає будь-яка програма,",
                     "тож переходять; таймер від timer_create має ідентифікатор, виданий тій програмі, якої вже немає."],
                    size=13.5, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "exec-survives.svg"), W, H, *p,
           title="Що переживає заміну образу, а що гине")


# ── Фіг. 3: що саме побудовано на момент першої інструкції ──────────────────
# Ідея: exec не «завантажує програму». Він створює відображення з файлу й
# розкладає стек. З диска на цю мить не прочитано жодного байта коду.
def fig_new_image_layout():
    W, H = 1040, 760
    p = []

    p.append(text(W / 2, 40, "Що є в новому образі на момент першої інструкції",
                  size=16, color=INK, bold=True))

    # ── файл ──
    FX, FW = 60.0, 280.0
    p.append(rect(FX, 96, FW, 470, fill="#ffffff", stroke=INK, sw=1.6, rx=10))
    p.append(text(FX + FW / 2, 124, "виконуваний файл ELF", size=14, color=INK, bold=True))

    file_rows = [
        ("заголовки програми", 146),
        ("ім'я інтерпретатора\n(сегмент PT_INTERP)", 220),
        ("сегмент коду", 320),
        ("сегмент даних", 396),
        ("розмір неініціалізованих\nданих — самих даних немає", 462),
    ]
    for label, y in file_rows:
        p.append(fitbox(FX + 16, y, FW - 32, 62, label.split("\n"), size=12.5,
                        fill="#f4f6f8", stroke="#c8ced6", sw=1.2))

    # ── адресний простір ──
    AX, AW = 640.0, 340.0
    p.append(text(AX + AW / 2, 88, "адресний простір процесу", size=14, color=INK, bold=True))
    p.append(text(AX + AW / 2, 110, "вершина простору", size=12, color=MUTED))

    mem_rows = [
        (["стек:  рядки argv і envp,", "масиви покажчиків,", "допоміжний вектор"], 120, 84, NEG, "#eef3fb"),
        (["динамічний завантажувач —", "відображено з файлу", "інтерпретатора"], 216, 76, FIELD, "#eef7f0"),
        (["спільні бібліотеки:", "ще нічого не відображено"], 304, 58, MUTED, "#ffffff"),
        (["купа: brk на початку,", "жодної сторінки"], 374, 58, MUTED, "#ffffff"),
        (["дані — відображено з файлу,", "запис дозволено"], 444, 58, POS, "#fdeeec"),
        (["код — відображено з файлу,", "читання й виконання"], 514, 58, POS, "#fdeeec"),
    ]
    for lines, y, h, color, fill in mem_rows:
        p.append(fitbox(AX, y, AW, h, lines, size=12.5, fill=fill, stroke=color, sw=1.5))
    p.append(text(AX + AW / 2, 592, "низ простору", size=12, color=MUTED))

    # ── стрілки файл → пам'ять (у вільному коридорі між колонками) ──
    p.append(arrow(FX + FW + 10, 251, AX - 10, 254, color=FIELD, sw=1.8))
    p.append(arrow(FX + FW + 10, 351, AX - 10, 543, color=POS, sw=1.8))
    p.append(arrow(FX + FW + 10, 427, AX - 10, 473, color=POS, sw=1.8))

    p.append(fitbox(374, 108, 240, 96,
                    ["стрілка = створено запис", "«ці адреси відповідають",
                     "цьому шматкові файлу»"],
                    size=12.5, fill="#ffffff", stroke="#c8ced6", sw=1.2))

    p.append(fitbox(60, 626, W - 120, 96,
                    ["З диска на цю мить не прочитано ЖОДНОГО байта коду: створено лише відображення.",
                     "Перша інструкція нової програми викличе сторінковий збій, і аж він підніме одну сторінку.",
                     "Тому програма на сто мегабайтів стартує швидко — на старті читають одиниці сторінок."],
                    size=13.5, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "new-image-layout.svg"), W, H, *p,
           title="Новий образ: відображення з файлу й розкладений стек")


# ── Фіг. 4: як «#!» переписує argv ──────────────────────────────────────────
# Ідея: увесь механізм сценаріїв зводиться до переписування масиву аргументів,
# і все після імені інтерпретатора стає ОДНИМ рядком — звідси класична пастка.
def fig_shebang_argv():
    W, H = 1060, 720
    p = []

    p.append(text(W / 2, 40, "Файл із «#!»: ядро переписує argv", size=16,
                  color=INK, bold=True))

    p.append(fitbox(60, 66, 440, 66,
                    ["користувач набрав:", "report data.csv --dry-run"],
                    size=13.5, fill="#ffffff", stroke="#c8ced6", sw=1.3))
    p.append(fitbox(560, 66, 440, 66,
                    ["перший рядок файлу report:", "#!/usr/bin/awk -f"],
                    size=13.5, fill="#ffffff", stroke="#c8ced6", sw=1.3))

    p.append(arrow(W / 2, 138, W / 2, 168, color=INK))
    p.append(text(W / 2, 190, "ядро складає новий масив аргументів", size=14,
                  color=INK, bold=True))

    rows = [
        ("argv[0]", "/usr/bin/awk", "ім'я інтерпретатора з рядка «#!»", NEG, "#eef3fb"),
        ("argv[1]", "-f", "усе після імені — ОДНИМ рядком", NEG, "#eef3fb"),
        ("argv[2]", "/usr/local/bin/report", "шлях до самого файлу-сценарію", FIELD, "#eef7f0"),
        ("argv[3]", "data.csv", "аргументи користувача, від argv[1]", MUTED, "#ffffff"),
        ("argv[4]", "--dry-run", "аргументи користувача, від argv[1]", MUTED, "#ffffff"),
    ]
    y = 210.0
    for idx, val, origin, color, fill in rows:
        p.append(text(130, y + 30, idx, size=13, color=MUTED, anchor="end", bold=True))
        p.append(fitbox(146, y, 350, 46, val, size=13.5, fill=fill, stroke=color, sw=1.5))
        p.append(fitbox(530, y + 6, 470, 34, origin, size=12.5,
                        fill="#ffffff", stroke="#c8ced6", sw=1.1))
        y += 56

    p.append(line(60, 512, W - 60, 512, color="#c8ced6", sw=1.4))
    p.append(text(60, 542, "та сама властивість — і найпоширеніша пастка", size=14,
                  color=POS, anchor="start", bold=True))

    p.append(fitbox(60, 560, 440, 66,
                    ["#!/usr/bin/env python3 -u"],
                    size=13.5, fill="#fdeeec", stroke=POS, sw=1.5))
    p.append(arrow(510, 593, 550, 593, color=POS))
    p.append(fitbox(560, 560, 440, 66,
                    ["argv[1] = «python3 -u» — один рядок",
                     "із пробілом усередині імені програми"],
                    size=13, fill="#fdeeec", stroke=POS, sw=1.5))

    p.append(fitbox(60, 644, W - 120, 52,
                    ["env шукає програму з таким іменем і не знаходить: ключ до інтерпретатора так не передати."],
                    size=13, fill="#f4f6f8", stroke=INK, sw=1.3))

    render(os.path.join(OUT, "shebang-argv.svg"), W, H, *p,
           title="Як «#!» переписує масив аргументів")


# ── Фіг. 5 (вставка hist): як «#!» розповзався системами ────────────────────
# Ідея: механізм придумали за один вечір, а типовим він став лише через
# три з половиною роки — і то не в тій системі, де народився.
def fig_shebang_history():
    W, H = 1080, 700
    p = []

    DX, DW = 50.0, 250.0          # колонка дати
    TX, TW = 330.0, 700.0         # колонка події
    BH, STEP = 74.0, 88.0

    p.append(text(W / 2, 42, "Шлях «#!» від листа до звичаю", size=17,
                  color=INK, bold=True))

    rows = [
        ("1979 · Сьома редакція", "#eef3fb", NEG,
         ["exec розуміє лише двійковий файл; сценарій запускає оболонка,",
          "підхопивши відмову ENOEXEC, — і в списку процесів видно її, не сценарій"]),
        ("бл. 1978 · csh, Берклі", "#eef3fb", NEG,
         ["перший символ «#» означає «сценарій мій»; усе інше csh віддає",
          "стандартній оболонці — домовленість на один символ, без імені програми"]),
        ("10 січня 1980 · Bell Labs", "#eafaf1", FIELD,
         ["лист Денніса Рітчі: ядро саме читає «#!» і бере решту рядка",
          "за ім'я інтерпретатора; усередині Bell Labs — Восьма редакція"]),
        ("жовтень 1980 · 4.0BSD", "#fdf6e3", "#b8860b",
         ["код у системі є, але типово вимкнений; рядок короткий,",
          "аргумент після імені інтерпретатора ще не доходить"]),
        ("вересень 1983 · 4.2BSD", "#eafaf1", FIELD,
         ["увімкнено типово (kern_exec.c, Роберт Елз) — саме звідси звичай",
          "розходиться по всьому світу разом із берклійськими стрічками"]),
        ("1988 · SVR4", "#fdf6e3", "#b8860b",
         ["перша ПУБЛІЧНА система від AT&T із «#!»: вісім років потому,",
          "як механізм народився в тій-таки компанії"]),
        ("POSIX · донині", "#fdeeec", POS,
         ["не стандартизовано: комітет не може приписати, за яким шляхом",
          "у системі лежить інтерпретатор, — тож механізм лишився звичаєм"]),
    ]

    y = 72.0
    for date, fill, stroke, body in rows:
        p.append(fitbox(DX, y, DW, BH, date, size=13.5,
                        fill=fill, stroke=stroke, sw=1.6, bold=True))
        p.append(fitbox(TX, y, TW, BH, body, size=13,
                        fill="#ffffff", stroke="#c8ced6", sw=1.2))
        y += STEP

    render(os.path.join(OUT, "shebang-history.svg"), W, H, *p)


# ── Фіг. 6 (вставка proj): таблиця дескрипторів крізь заміну образу ─────────
# Ідея: таблиця належить процесові, а не образові; FD_CLOEXEC — єдина позначка,
# яка каже ядру закрити елемент саме в мить заміни. Опис відкритого файлу
# (а з ним і зсув) той самий по обидва боки.
def fig_fd_across():
    W, H = 1040, 580
    p = []

    LX, RX, PW = 50.0, 610.0, 380.0

    p.append(text(LX + PW / 2, 88, "перед execve — процес 4711",
                  size=15, bold=True))
    p.append(text(RX + PW / 2, 88, "після execve — той самий процес 4711",
                  size=15, bold=True))

    left = [
        (["fd 0, 1, 2 — термінал"], FILL, LINE),
        (["fd 4  →  /tmp/exec-probe.dat", "відкрито з O_CLOEXEC"], "#eef3fb", NEG),
        (["fd 3  →  /tmp/exec-probe.dat", "зсув виставлено на 10"], "#eafaf1", FIELD),
    ]
    right = [
        (["fd 0, 1, 2 — той самий термінал"], FILL, LINE),
        (["fd 4 — порожньо", "ядро закрило в мить заміни"], "#fdeeec", POS),
        (["fd 3 — те саме, що й було", "lseek(fd, 0, SEEK_CUR) → 10"], "#eafaf1", FIELD),
    ]

    ys = [104.0, 164.0, 224.0]
    for (lines, fill, stroke), y in zip(left, ys):
        p.append(fitbox(LX, y, PW, 52, lines, size=14,
                        fill=fill, stroke=stroke, sw=1.5))
    for (lines, fill, stroke), y in zip(right, ys):
        p.append(fitbox(RX, y, PW, 52, lines, size=14,
                        fill=fill, stroke=stroke, sw=1.5))

    p.append(line(520, 96, 520, 300, color=POS, sw=2.4, dash="9 6"))
    p.append(text(520, 344, "execve", size=15, color=POS, bold=True))

    p.append(arrow(LX + PW / 2, 282, 400, 392))
    p.append(arrow(RX + PW / 2, 282, 640, 392))

    p.append(fitbox(300, 396, 440, 78,
                    ["той самий опис відкритого файлу",
                     "інод файлу · режим O_RDWR · зсув 10"],
                    size=14, fill="#eafaf1", stroke=FIELD, sw=1.8))

    p.append(mtext(W / 2, 516,
                   ["Таблиця дескрипторів належить процесові, а не образові,",
                    "тому переживає заміну разом з описом відкритого файлу."],
                   size=13, color=MUTED))

    render(os.path.join(OUT, "exec-fd-across.svg"), W, H, *p)


fig_exec_timeline()
fig_exec_survives()
fig_new_image_layout()
fig_shebang_argv()
fig_shebang_history()
fig_fd_across()
print("готово:", OUT)
