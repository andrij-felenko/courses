# -*- coding: utf-8 -*-
"""Фігури до теми «libc як шлюз до ядра»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Три доріжки того самого «виклику функції» ────────────────────────────
def three_lanes():
    W, H = 960, 520
    f = []
    # заголовки колонок
    f.append(text(140, 82, "виклик у програмі", size=14, bold=True, color=MUTED))
    f.append(text(480, 82, "що робить libc", size=14, bold=True, color=MUTED))
    f.append(text(820, 82, "скільки системних викликів", size=14, bold=True, color=MUTED))

    rows = [
        ("qsort()\nstrtod()\nsnprintf()",
         "рахує сама, у пам'яті\nпроцесу; ядро не потрібне",
         "жодного",
         "#eaf6ef", FIELD),
        ("getpid()\nwrite()\ndup2()",
         "кладе аргументи в інші\nрегістри й б'є пасткою",
         "рівно один",
         "#eaf0fd", NEG),
        ("printf()\nmalloc()\ngetaddrinfo()",
         "своя політика: буфер,\nрозподільник, порядок\nджерел імен",
         "нуль, один або\nбагато — і зовсім\nінших на ім'я",
         "#fdecea", POS),
    ]
    ys = [110, 240, 370]
    for (a, b, c, fill, stroke), y in zip(rows, ys):
        f.append(fitbox(40, y, 200, 110, a, size=14, fill=fill, stroke=stroke))
        f.append(fitbox(340, y, 280, 110, b, size=13))
        f.append(fitbox(720, y, 200, 110, c, size=13, fill=fill, stroke=stroke))
        f.append(arrow(248, y + 55, 332, y + 55))
        f.append(arrow(628, y + 55, 712, y + 55))
    return render(os.path.join(OUT, 'three-lanes.svg'), W, H, *f,
                  title="Одна libc — три різні доріжки за межу процесу")


# ── 2. Переклад двох угод на x86-64 ─────────────────────────────────────────
def abi_translation():
    W, H = 940, 560
    f = []
    left_x, right_x, pw = 40, 540, 360
    f.append(rect(left_x, 70, pw, 330, fill="#ffffff"))
    f.append(rect(right_x, 70, pw, 330, fill="#ffffff"))
    f.append(text(left_x + pw / 2, 98, "як кличе код мовою C", size=15, bold=True))
    f.append(text(right_x + pw / 2, 98, "як приймає ядро Linux", size=15, bold=True))

    lrows = ["1-й аргумент  →  rdi", "2-й  →  rsi", "3-й  →  rdx",
             "4-й  →  rcx", "5-й  →  r8", "6-й  →  r9", "результат  ←  rax"]
    rrows = ["номер виклику  →  rax", "1-й аргумент  →  rdi", "2-й  →  rsi",
             "3-й  →  rdx", "4-й  →  r10  (не rcx)", "5-й  →  r8", "6-й  →  r9"]
    y = 130
    for i in range(7):
        col_l = POS if lrows[i].startswith("4-й") else INK
        col_r = POS if rrows[i].startswith(("номер", "4-й")) else INK
        f.append(text(left_x + 24, y, lrows[i], size=14, anchor="start", color=col_l))
        f.append(text(right_x + 24, y, rrows[i], size=14, anchor="start", color=col_r))
        y += 34

    f.append(arrow(left_x + pw + 20, 230, right_x - 20, 230))
    f.append(text((left_x + pw + right_x) / 2, 210, "обгортка", size=13, color=MUTED))
    f.append(text((left_x + pw + right_x) / 2, 262, "перекладає", size=13, color=MUTED))

    f.append(fitbox(40, 430, 400, 96,
                    "інструкція syscall затирає rcx і r11:\nтуди процесор кладе адресу\nповернення та прапорці",
                    size=13, fill="#fdecea", stroke=POS))
    f.append(fitbox(500, 430, 400, 96,
                    "rax у межах −4095…−1 — це помилка:\nlibc пише −rax у errno\nі повертає −1",
                    size=13, fill="#eaf0fd", stroke=NEG))
    return render(os.path.join(OUT, 'abi-translation.svg'), W, H, *f,
                  title="Що саме перекладає обгортка libc (x86-64)")


# ── 3. Куди дівається текст між printf і пристроєм ──────────────────────────
def stdio_buffering():
    W, H = 900, 560
    f = []
    cols = [
        (60, "вивід у термінал", "рядковий режим",
         "буфер libc\n(у пам'яті процесу)",
         "write() — на кожному\nсимволі нового рядка",
         "термінал"),
        (500, "вивід у канал або файл", "повний режим",
         "буфер libc\n(типово 4 КіБ)",
         "write() — коли буфер повний\nабо коли викликали exit()",
         "канал / файл"),
    ]
    for x, head, mode, buf, when, dev in cols:
        f.append(text(x + 170, 78, head, size=15, bold=True))
        f.append(text(x + 170, 100, mode, size=13, color=MUTED))
        f.append(fitbox(x, 120, 340, 54, "printf(\"рядок\\n\")", size=14))
        f.append(arrow(x + 170, 176, x + 170, 202))
        f.append(fitbox(x, 206, 340, 66, buf, size=13, fill="#fdf6e3", stroke="#b8860b"))
        f.append(arrow(x + 170, 274, x + 170, 300))
        f.append(fitbox(x, 304, 340, 66, when, size=13))
        f.append(arrow(x + 170, 372, x + 170, 398))
        f.append(fitbox(x, 402, 340, 50, dev, size=14, fill="#eaf6ef", stroke=FIELD))

    f.append(fitbox(60, 478, 780, 58,
                    "Поки текст у буфері, його ще ніхто не бачив: _exit() і аварія його втрачають, "
                    "а fork() копіює разом з усією пам'яттю — і рядок виходить двічі.",
                    size=13, fill="#fdecea", stroke=POS))
    return render(os.path.join(OUT, 'stdio-buffering.svg'), W, H, *f,
                  title="Той самий printf, два різні режими буфера")


# ── 4. Від execve до main і назад ───────────────────────────────────────────
def startup_chain():
    W, H = 980, 470
    f = []
    f.append(line(30, 168, 950, 168, color=MUTED, sw=1.5, dash="7,6"))
    f.append(text(940, 162, "межа привілеїв", size=12, color=MUTED, anchor="end"))
    f.append(text(40, 162, "ядро", size=12, color=MUTED, anchor="start"))
    f.append(text(40, 188, "простір користувача", size=12, color=MUTED, anchor="start"))

    f.append(fitbox(60, 66, 300, 84,
                    "execve(): відображає сегменти ELF,\nкладе argv, envp і auxv на стек,\n"
                    "передає керування на e_entry", size=13, fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(640, 66, 280, 84,
                    "exit_group(): ядро прибирає\nресурси, процес зникає",
                    size=13, fill="#eaf0fd", stroke=NEG))

    f.append(fitbox(60, 210, 200, 76, "_start\n(код libc,\nбез стекового кадру)", size=13))
    f.append(fitbox(310, 210, 260, 76,
                    "__libc_start_main:\nTLS, потоки, stdio,\nконструктори", size=13))
    f.append(fitbox(640, 210, 280, 76,
                    "exit(): деструктори,\nскидання буферів stdio", size=13,
                    fill="#fdf6e3", stroke="#b8860b"))

    f.append(fitbox(310, 350, 260, 60, "main() — ваш код", size=14,
                    fill="#eaf6ef", stroke=FIELD))

    f.append(arrow(160, 154, 160, 204))
    f.append(arrow(268, 248, 304, 248))
    f.append(arrow(440, 292, 440, 344))
    f.append(arrow(576, 380, 780, 380))
    f.append(arrow(780, 380, 780, 292))
    f.append(arrow(780, 204, 780, 154))
    f.append(text(660, 368, "повернення з main", size=12, color=MUTED, anchor="start"))
    return render(os.path.join(OUT, 'startup-chain.svg'), W, H, *f,
                  title="Ядро заходить у програму теж через libc")


# ── 5. Родовід libc: від однієї бібліотеки до кількох реалізацій ────────────
def libc_lineage():
    W, H = 1080, 630
    f = []
    ax, bx, cx = 180, 470, 760
    aw, bw, cw = 250, 250, 280

    # підписи доріжок ліворуч
    for y, name in ((150, "Unix"), (290, "Стандарти"),
                    (430, "Реалізації"), (562, "Альтернатива")):
        f.append(text(30, y, name, size=13, bold=True, color=MUTED, anchor="start"))

    # доріжка 1 — одна бібліотека
    f.append(fitbox(ax, 90, aw + 40, 110,
                    "1979 · Сьома редакція Unix\nрозділи 2 (виклики ядра)\nі 3 (підпрограми) — "
                    "одна libc,\nяку компілятор бере сам",
                    size=13, fill="#f4f6f8", stroke=LINE))

    # доріжка 2 — стандарти
    f.append(fitbox(ax, 230, aw, 110,
                    "1983 · ANSI збирає\nкомітет X3J11", size=13,
                    fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(bx, 230, bw, 110,
                    "1988 · POSIX 1003.1\nбере непереносну\nполовину бібліотеки", size=13,
                    fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(cx, 230, cw, 110,
                    "1989 · ANSI X3.159\nпереносна половина стає\nчастиною стандарту мови", size=13,
                    fill="#eaf0fd", stroke=NEG))

    # доріжка 3 — реалізації
    f.append(fitbox(ax, 370, aw, 110,
                    "1987 · Роланд Макґрат\nпочинає GNU libc\nу ФВПЗ", size=13,
                    fill="#eaf6ef", stroke=FIELD))
    f.append(fitbox(bx, 370, bw, 110,
                    "1994 · «Linux libc» —\nвідгалуження від glibc 1.x\nlibc4 (a.out) → libc5 (ELF)", size=13,
                    fill="#fdf6e3", stroke="#b8860b"))
    f.append(fitbox(cx, 370, cw, 110,
                    "1997 · glibc 2.0 —\nгілки сходяться;\nsoname libc.so.6", size=13,
                    fill="#eaf6ef", stroke=FIELD))

    # доріжка 4 — musl
    f.append(fitbox(ax, 512, cx + cw - ax, 100,
                    "2011 · musl (Річ Фелкер) — не відгалуження, а окремий код: ті самі функції "
                    "стандарту, інші пріоритети — розмір, статичне лінкування, відсутність гонок",
                    size=13, fill="#fdecea", stroke=POS))

    # стрілки
    f.append(arrow(ax + (aw + 40) / 2, 204, ax + (aw + 40) / 2, 226))
    f.append(arrow(ax + aw + 4, 285, bx - 4, 285))
    f.append(arrow(bx + bw + 4, 285, cx - 4, 285))
    f.append(arrow(ax + aw + 4, 425, bx - 4, 425))
    f.append(arrow(bx + bw + 4, 425, cx - 4, 425))
    return render(os.path.join(OUT, 'libc-lineage.svg'), W, H, *f,
                  title="Родовід libc: одна бібліотека, два стандарти, кілька реалізацій")


# ── 6. Стек у момент входу в _start (вставка proj-syscall-without-libc) ─────
def entry_stack():
    W, H = 940, 660
    f = []

    bx, bw = 250, 250          # колонка «слотів» стека
    rh, gap = 34, 4
    y0 = 74

    rows = [
        ("argc",                     "#eaf0fd", NEG),
        ("argv[0]",                  FILL,      LINE),
        ("argv[1]  …",               FILL,      LINE),
        ("argv[argc−1]",             FILL,      LINE),
        ("NULL",                     "#f0f0f0", MUTED),
        ("envp[0]",                  "#eaf6ef", FIELD),
        ("envp[1]  …",               "#eaf6ef", FIELD),
        ("NULL",                     "#f0f0f0", MUTED),
        ("auxv: {тип, значення}",    "#fdf6e3", "#b8860b"),
        ("…",                        "#fdf6e3", "#b8860b"),
        ("{AT_NULL, 0}",             "#f0f0f0", MUTED),
    ]
    ys = []
    for i, (label, fill, stroke) in enumerate(rows):
        y = y0 + i * (rh + gap)
        ys.append(y)
        f.append(fitbox(bx, y, bw, rh, label, size=14, fill=fill, stroke=stroke))

    # покажчик стека
    f.append(text(bx - 16, ys[0] + rh / 2 + 5, "%rsp →", size=15, bold=True,
                  color=NEG, anchor="end"))
    f.append(text(bx - 16, ys[0] + rh / 2 + 26, "кожен слот — 8 байтів", size=12,
                  color=MUTED, anchor="end"))

    # напрямок зростання адрес — окремо, збоку, щоб лінія не йшла крізь написи
    ax = 118
    f.append(arrow(ax, ys[0] + 6, ax, ys[-1] + rh - 6, color=MUTED, sw=1.6))
    f.append(text(ax - 12, (ys[0] + ys[-1]) / 2, "адреси", size=12, color=MUTED, anchor="end"))
    f.append(text(ax - 12, (ys[0] + ys[-1]) / 2 + 17, "ростуть", size=12, color=MUTED, anchor="end"))

    # правий стовпчик пояснень
    rx = bx + bw + 46
    f.append(fitbox(rx, ys[0], 300, rh, "sp[0]", size=13, fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(rx, ys[1], 300, rh * 4 + gap * 3,
                    "argv = (char **)(sp + 1)\nмасив вказівників, кінець — NULL",
                    size=13))
    f.append(fitbox(rx, ys[5], 300, rh * 3 + gap * 2,
                    "envp = argv + argc + 1\nтой самий формат, одразу за NULL",
                    size=13, fill="#eaf6ef", stroke=FIELD))
    f.append(fitbox(rx, ys[8], 300, rh * 3 + gap * 2,
                    "auxv — пари від ядра:\nадреса vDSO, розмір сторінки,\nдійсні UID і GID",
                    size=13, fill="#fdf6e3", stroke="#b8860b"))

    # нижня заувага
    note_y = ys[-1] + rh + 30
    f.append(fitbox(90, note_y, W - 180, 74,
                    "Адреси повернення на стеку немає: ядро не викликало програму, а стрибнуло на точку входу.\n"
                    "Тому _start не може бути звичайною функцією C — компілятор поставив би їй пролог і ret,\n"
                    "а повертатися нікуди. Розібрати цей стек також нема кому: argv і envp тут просто числа.",
                    size=13, fill="#fdecea", stroke=POS))

    return render(os.path.join(OUT, 'entry-stack.svg'), W, H, *f,
                  title="Що ядро лишає на стеку до першої інструкції програми")


# ── 7. Скільки пасток у ядро (вставка proj-syscall-without-libc) ────────────
def syscall_counts():
    W, H = 960, 552
    f = []

    lx = 300                    # правий край підписів
    bx = 320                    # початок смуг
    full = 500                  # довжина смуги для максимуму панелі
    bh = 28

    def panel(header, header_y, items, top, maxv, note, note_y):
        f.append(text(70, header_y, header, size=14, bold=True, color=MUTED, anchor="start"))
        for i, (label, val, shown, color, fill) in enumerate(items):
            y = top + i * 44
            w = max(5.0, full * val / float(maxv))
            f.append(text(lx, y + bh / 2 + 5, label, size=14, anchor="end"))
            f.append(rect(bx, y, w, bh, fill=fill, stroke=color, sw=1.5, rx=4))
            f.append(text(bx + w + 14, y + bh / 2 + 5, shown, size=14, bold=True,
                          color=color, anchor="start"))
        f.append(fitbox(70, note_y, W - 140, 46, note, size=13, fill="#f7f7f7", stroke=MUTED))

    # ── панель А: тіло циклу
    panel("1000 рядків по 20 байтів у файл — скільки разів програма зайшла в ядро", 64,
          [("printf(\"…\\n\")",  5,    "5",    FIELD, "#eaf6ef"),
           ("write(1, …)",       1000, "1000", NEG,   "#eaf0fd"),
           ("власна пастка",     1000, "1000", POS,   "#fdecea")],
          top=86, maxv=1000,
          note="Обгортка write() не додає жодного переходу — на межі вона й сира пастка однакові.\n"
               "Різницю в двісті разів робить буфер stdio, а не шлюз у ядро.",
          note_y=218)

    f.append(line(70, 288, W - 70, 288, color=MUTED, sw=1, dash="6 5"))

    # ── панель Б: уся програма
    panel("Уся програма, що друкує один рядок — усього системних викликів", 322,
          [("glibc, динамічна", 30, "≈30", MUTED, FILL),
           ("glibc, статична",  12, "≈12", NEG,   "#eaf0fd"),
           ("−nostdlib",         3, "3",   POS,   "#fdecea")],
          top=344, maxv=30,
          note="Без libc їх рівно три: execve, write, exit_group. Решта — не робота програми, а розгортання\n"
               "середовища: динамічний компонувальник, купа, пам'ять потоку. Точні числа різняться, порядок — ні.",
          note_y=476)

    return render(os.path.join(OUT, 'syscall-counts.svg'), W, H, *f,
                  title="Ціна шлюзу і ціна середовища — це різні числа")


# ── 8. Яким інструментом на яку висоту дивитися (вставка api-libc-boundary) ─
def boundary_tools():
    W, H = 980, 560
    f = []
    cx, cw = 330, 320
    f.append(fitbox(cx, 68, cw, 60, "ваш код", size=15,
                    fill="#eaf6ef", stroke=FIELD))
    f.append(fitbox(cx, 208, cw, 80, "libc\nобгортки · буфер · розподільник",
                    size=13, fill="#fdf6e3", stroke="#b8860b"))
    f.append(fitbox(cx, 368, cw, 60, "ядро", size=15,
                    fill="#eaf0fd", stroke=NEG))
    f.append(arrow(490, 132, 490, 204))
    f.append(arrow(490, 292, 490, 364))

    for y, tool, ask, fill, stroke in (
            (168, "ltrace", "чого просить\nваш код у libc", "#eaf6ef", FIELD),
            (328, "strace", "чого просить\nlibc у ядра", "#eaf0fd", NEG)):
        f.append(line(cx - 4, y, cx + cw + 8, y, color=MUTED, sw=1.5, dash="6 5"))
        f.append(fitbox(40, y - 28, 260, 56, tool, size=15, bold=True,
                        fill=fill, stroke=stroke))
        f.append(fitbox(690, y - 28, 250, 56, ask, size=13))
        f.append(arrow(304, y, 322, y))
        f.append(arrow(662, y, 686, y))

    f.append(fitbox(40, 458, 900, 74,
                    "Ще до запуску, по самому файлу: ldd і objdump -p — які бібліотеки потрібні;\n"
                    "objdump -T і nm -D — які символи й мітки версій потрібні;\n"
                    "getconf GNU_LIBC_VERSION — яку libc має ця система.",
                    size=13, stroke=MUTED))
    return render(os.path.join(OUT, 'boundary-tools.svg'), W, H, *f,
                  title="Межу libc видно з двох боків — і кожен бік має свій інструмент")


# ── 9. Чому сумісність за мітками версій однобічна (вставка api-libc-boundary)
def version_direction():
    W, H = 960, 470
    f = []

    def panel(x0, head, need, have, ok, verdict):
        g = [rect(x0, 56, 420, 330, fill="#ffffff", stroke=MUTED)]
        g.append(text(x0 + 210, 86, head, size=13, bold=True))
        g.append(text(x0 + 112, 114, "файл вимагає", size=12, color=MUTED))
        g.append(text(x0 + 309, 114, "бібліотека дає", size=12, color=MUTED))
        g.append(fitbox(x0 + 25, 124, 175, 108, need, size=13))
        g.append(fitbox(x0 + 222, 124, 175, 108, have, size=13))
        g.append(fitbox(x0 + 25, 260, 372, 106, verdict, size=14,
                        fill="#eaf6ef" if ok else "#fdecea",
                        stroke=FIELD if ok else POS))
        return g

    f += panel(40, "зібрано на glibc 2.17 → запуск на glibc 2.39",
               "GLIBC_2.2.5\nGLIBC_2.14\nGLIBC_2.17",
               "GLIBC_2.2.5 … 2.17\n… 2.28 … 2.34\n… аж до GLIBC_2.39", True,
               "усі три мітки в бібліотеці є\n— програма стартує")
    f += panel(500, "зібрано на glibc 2.39 → запуск на glibc 2.28",
               "GLIBC_2.2.5\nGLIBC_2.17\nGLIBC_2.34",
               "GLIBC_2.2.5 … 2.17\n… аж до GLIBC_2.28\nі більше нічого", False,
               "мітки GLIBC_2.34 тут немає\nй не з'явиться — старт зривається")

    f.append(fitbox(40, 402, 880, 54,
                    "Мітки версій лише додаються й ніколи не зникають — звідси однобічність.",
                    size=13, stroke=MUTED))
    return render(os.path.join(OUT, 'version-direction.svg'), W, H, *f,
                  title="Стара збірка йде на нову систему, зворотне — ні")


three_lanes()
abi_translation()
stdio_buffering()
startup_chain()
libc_lineage()
entry_stack()
syscall_counts()
boundary_tools()
version_direction()
print("ok")
