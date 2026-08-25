# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PURPLE = "#7a4fb0"
SOFT = "#fbfcff"


# ── 1. Задача → окремі структури ресурсів; спільне визначає, що ми звемо процесом ─
def fig_task_and_resources():
    W, H = 1000, 560
    p = []

    def task(x, y, w, name, accent):
        out = [rect(x, y, w, 46, fill=SOFT, stroke=accent, sw=2, rx=8)]
        out.append(text(x + w / 2, y + 20, "task_struct", size=12, color=accent, bold=True))
        out.append(text(x + w / 2, y + 37, name, size=10, color=MUTED))
        return "".join(out)

    def resbox(x, y, w, h, label, accent, fill):
        return fitbox(x, y, w, h, label, size=11, fill=fill, stroke=accent, sw=1.6, color=INK)

    # ── ЛІВА половина: два процеси ────────────────────────────────────────────
    lx = 40
    p.append(fitbox(lx, 56, 420, 30, "Два процеси: спільного немає", size=13,
                    fill="#fdecea", stroke=POS, sw=1.8, color=POS, bold=True))

    p.append(task(lx + 10, 104, 180, "задача 1", NEG))
    p.append(task(lx + 230, 104, 180, "задача 2", NEG))

    left_rows = [
        "mm_struct\nвідображення пам'яті",
        "files_struct\nтаблиця дескрипторів",
        "cred\nідентичність",
    ]
    ry = 178
    for lab in left_rows:
        p.append(resbox(lx + 10, ry, 180, 56, lab, NEG, SOFT))
        p.append(resbox(lx + 230, ry, 180, 56, lab, NEG, SOFT))
        p.append(line(lx + 100, ry - 28, lx + 100, ry, color=NEG, sw=1.4))
        p.append(line(lx + 320, ry - 28, lx + 320, ry, color=NEG, sw=1.4))
        ry += 82

    p.append(fitbox(lx + 10, ry + 6, 400, 44,
                    "у кожної задачі свій примірник кожної структури —\nчужу пам'ять неможливо навіть назвати",
                    size=11, fill="#fff", stroke=MUTED, sw=1.2, color=INK))

    # ── ПРАВА половина: два потоки одного процесу ─────────────────────────────
    rx0 = 540
    p.append(fitbox(rx0, 56, 420, 30, "Два потоки: спільне все", size=13,
                    fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    p.append(task(rx0 + 10, 104, 180, "задача 1", FIELD))
    p.append(task(rx0 + 230, 104, 180, "задача 2", FIELD))

    ry = 178
    for lab in left_rows:
        p.append(resbox(rx0 + 110, ry, 200, 56, lab, FIELD, "#eafaf0"))
        # обидві задачі вказують на ОДИН примірник
        p.append(line(rx0 + 100, ry - 28, rx0 + 160, ry, color=FIELD, sw=1.4))
        p.append(line(rx0 + 320, ry - 28, rx0 + 260, ry, color=FIELD, sw=1.4))
        ry += 82

    p.append(fitbox(rx0 + 10, ry + 6, 400, 44,
                    "один примірник на двох, лічильник посилань = 2 —\nтому запис однієї задачі миттю видно другій",
                    size=11, fill="#fff", stroke=MUTED, sw=1.2, color=INK))

    # роздільник
    p.append(line(500, 56, 500, H - 60, color="#d7dbe0", sw=1.4, dash="6 6"))

    p.append(text(W / 2, H - 18,
                  "у ядрі є лише задача та структури, на які вона вказує; «процес» і «потік» — назви для двох крайніх наборів вказівників",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "task-and-resources.svg"), W, H, *p,
           title="Задача та її ресурси: спільне чи своє")


# ── 2. Що переживає execve ─────────────────────────────────────────────────────
def fig_exec_survivors():
    W, H = 940, 470
    p = []

    col_w = 400
    lx, rx0, top = 40, 500, 96

    p.append(fitbox(lx, 56, col_w, 30, "Переживає заміну образу", size=13,
                    fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD, bold=True))
    p.append(fitbox(rx0, 56, col_w, 30, "Замінюється новим образом", size=13,
                    fill="#fdecea", stroke=POS, sw=1.8, color=POS, bold=True))

    keep = [
        "PID і TGID — номер лишається той самий",
        "батько й місце в дереві процесів",
        "поточний каталог і корінь",
        "відкриті дескриптори без позначки CLOEXEC",
        "простори імен і група обмежень (cgroup)",
        "маска сигналів і черга нерозданих сигналів",
        "пріоритет (nice) та обмеження ресурсів",
    ]
    drop = [
        "усе відображення пам'яті: код, дані, купа, стеки",
        "усі регістри — виконання починається з точки входу",
        "обробники сигналів: перехоплені стають типовими",
        "решта потоків групи — лишається тільки той, хто викликав",
        "дескриптори з позначкою CLOEXEC",
        "ідентичність — якщо у файлі стоїть біт setuid",
        "відображення файлів через mmap і замки пам'яті",
    ]

    def col(x, items, accent, fill):
        out = []
        y = top
        for it in items:
            out.append(fitbox(x, y, col_w, 42, it, size=11, fill=fill, stroke=accent, sw=1.4, color=INK))
            y += 50
        return "".join(out), y

    frag, endy = col(lx, keep, FIELD, "#f4fbf6")
    p.append(frag)
    frag, endy = col(rx0, drop, POS, "#fdf5f4")
    p.append(frag)

    p.append(text(W / 2, H - 18,
                  "execve не створює процес: ідентичність лишається на місці, міняється лише вміст під нею",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "exec-survivors.svg"), W, H, *p,
           title="Заміна образу: що лишається, а що зникає")


# ── 3. Чотири шари ізоляції над спільним ядром ─────────────────────────────────
def fig_isolation_layers():
    W, H = 960, 560
    p = []

    layers = [
        ("Пам'ять — апаратна стіна", "чужих сторінок немає в таблицях цього процесу;\nдоступ не забороняють — його просто нема куди зробити", NEG, "#eef2fd"),
        ("Права — перевірка на вході в ядро", "ядро звіряє ідентичність (uid, групи, можливості)\nз кожним проханням; поламана перевірка = поламана стіна", PURPLE, "#f5f0fb"),
        ("Простори імен — інша видимість", "ті самі об'єкти ядра, інший словник імен:\nсвої номери процесів, своє дерево монтувань, своя мережа", FIELD, "#eafaf0"),
        ("cgroups — рахунок і межа", "нічого не ховає: рахує спожите й обриває понад міру\n(пам'ять, час процесора, ввід-вивід)", POS, "#fdecea"),
    ]

    x, w = 60, 840
    y = 60
    for title_s, desc, accent, fill in layers:
        p.append(rect(x, y, w, 74, fill=fill, stroke=accent, sw=1.8, rx=10))
        p.append(text(x + 20, y + 26, title_s, size=13, color=accent, anchor="start", bold=True))
        p.append(mtext(x + 20, y + 46, desc, size=11, color=INK, anchor="start", lh=1.25))
        y += 88

    # спільне ядро знизу
    p.append(rect(x, y + 4, w, 62, fill="#eceff2", stroke=INK, sw=2, rx=10))
    p.append(text(x + w / 2, y + 30, "Спільне ядро для всіх", size=13, color=INK, bold=True))
    p.append(text(x + w / 2, y + 50,
                  "один набір системних викликів, один планувальник, одні кеші процесора, один годинник",
                  size=11, color=MUTED))

    p.append(text(W / 2, H - 16,
                  "чотири шари роблять чотири різні речі; жоден з них не прибирає спільного ядра — тут і проходить межа з віртуальною машиною",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "isolation-layers.svg"), W, H, *p,
           title="Чотири шари ізоляції процесу")


# ── 4. Драбина прапорців: від fork() до pthread_create() (вставка proj) ─────
def fig_clone_ladder():
    W, H = 1090, 606
    p = []

    cols = ["пам'ять\nmm_struct", "дескриптори\nfiles_struct", "каталог і корінь\nfs_struct",
            "диспозиції\nsighand_struct", "ідентичність\nодна група задач"]
    rows = [
        ("clone без прапорців\nце і є fork()", 0, False),
        ("+ CLONE_VM", 1, False),
        ("+ CLONE_FILES", 2, False),
        ("+ CLONE_FS", 3, False),
        ("+ CLONE_SIGHAND", 4, False),
        ("+ CLONE_THREAD\nце і є pthread_create()", 5, True),
    ]

    LX, LW = 28, 300
    CX, CW, GAP = 340, 138, 8
    RY, RH, RGAP = 124, 62, 6

    # шапка з назвами колонок
    for j, c in enumerate(cols):
        x = CX + j * (CW + GAP)
        p.append(fitbox(x, 60, CW, 52, c, size=11, fill="#fff", stroke=MUTED, sw=1.2, color=MUTED))
    p.append(fitbox(LX, 60, LW, 52, "що додаємо до виклику", size=12,
                    fill="#fff", stroke=MUTED, sw=1.2, color=MUTED))

    for i, (label, shared_n, last) in enumerate(rows):
        y = RY + i * (RH + RGAP)
        p.append(fitbox(LX, y, LW, RH, label, size=12,
                        fill="#eafaf0" if last else SOFT,
                        stroke=FIELD if last else PURPLE, sw=1.8 if last else 1.4,
                        color=INK, bold=last))
        for j in range(len(cols)):
            x = CX + j * (CW + GAP)
            if j < shared_n:
                p.append(fitbox(x, y, CW, RH, "спільне", size=12, fill="#eafaf0",
                                stroke=FIELD, sw=1.6, color=FIELD, bold=True))
            else:
                p.append(fitbox(x, y, CW, RH, "своє", size=12, fill="#f4f6f8",
                                stroke=MUTED, sw=1.1, color=MUTED))

    ny = RY + len(rows) * (RH + RGAP) + 10
    p.append(fitbox(LX, ny, W - 2 * LX, 44,
                    "жоден рядок не є окремим видом істоти: щоразу той самий виклик, лише на один біт більше",
                    size=12, fill="#fff", stroke=MUTED, sw=1.2, color=INK))
    p.append(text(W / 2, H - 14,
                  "прапорці накопичуються згори вниз; крайні точки мають імена fork і pthread_create, середина імен не має",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "clone-flag-ladder.svg"), W, H, *p,
           title="Що стає спільним, коли додати ще один прапорець")


# ── 5. Дві форми виклику й пастка стека (вставка proj) ──────────────────────
def fig_clone_stack_forms():
    W, H = 1090, 540
    p = []

    PW = 490
    left, right = 30, 570

    def panel(x, head, head_color, head_fill, steps):
        out = [fitbox(x, 58, PW, 40, head, size=13, fill=head_fill,
                      stroke=head_color, sw=1.8, color=head_color, bold=True)]
        y = 116
        for txt, accent, fill in steps:
            out.append(fitbox(x, y, PW, 74, txt, size=12, fill=fill, stroke=accent,
                              sw=1.6, color=INK))
            y += 74
            if y < 420:
                out.append(arrow(x + PW / 2, y + 2, x + PW / 2, y + 22, color=MUTED, sw=1.6))
            y += 26
        return out

    p += panel(left, "clone(fn, stack + SIZE, …) — форма з функцією",
               FIELD, "#eafaf0",
               [("дитина стартує прямо у fn(arg),\nа її %rsp — верхівка виділеної ділянки", FIELD, SOFT),
                ("кадру батька в цьому стеку немає,\nі він дитині не потрібен", FIELD, SOFT),
                ("fn повертає — обгортка glibc\nробить системний виклик exit", FIELD, "#eafaf0")])

    p += panel(right, "syscall(SYS_clone, …) — сира форма",
               POS, "#fdecea",
               [("дитина прокидається на тому самому рядку C,\nале %rsp уже вказує на порожню ділянку", POS, SOFT),
                ("локальні змінні компілятор читає зі стека —\nтам не нулі, там ніщо", POS, "#fdecea"),
                ("return з цієї функції зніме зі стека\nвипадкове число й стрибне за ним", POS, "#fdecea")])

    p.append(text(W / 2, H - 16,
                  "у сирій формі перше, що робить дитина, мусить бути виклик функції або exit — жодного повернення назад",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "clone-stack-forms.svg"), W, H, *p,
           title="Дві форми clone і чому дитині потрібен власний стек")


# ── 6. Родовід слів «процес» і «fork»: ідея → формулювання → реалізації → спадок ─
def fig_fork_lineage():
    W, H = 1080, 800
    p = []

    IDEA = MUTED
    DEFN = NEG
    IMPL = FIELD
    LEGA = POS
    TINT = {IDEA: "#f3f4f6", DEFN: "#eaf0fd", IMPL: "#eafaf0", LEGA: "#fdecea"}

    # ── легенда ──────────────────────────────────────────────────────────────
    legend = [(IDEA, "ідея"), (DEFN, "формулювання"), (IMPL, "реалізація"), (LEGA, "що дожило")]
    lx = 40
    for accent, name in legend:
        p.append(fitbox(lx, 26, 236, 34, name, size=13, fill=TINT[accent],
                        stroke=accent, sw=1.8, color=accent, bold=True))
        lx += 254

    rows = [
        ("1963", IDEA, "Мелвін Конвей · Fall Joint Computer Conference",
         "«A Multiprocessor System Design»: fork і join — розгалуження керування між процесорами"),
        ("1965", DEFN, "Multics · Висоцький, Корбато, Грем",
         "процес = виконання програми з даним дескрипторним сегментом, тобто з даною картою пам'яті"),
        ("1965–66", IMPL, "Project Genie, SDS 930 · Дойч, Лемпсон",
         "BRS 9 «open fork»: задають стартову адресу, регістри й карту пам'яті — що спільне, обирає той, хто створює"),
        ("1966", DEFN, "Денніс і Ван Горн · Communications of the ACM",
         "словник багатопрограмних обчислень: обчислення, процес, мета-інструкції fork · join · quit"),
        ("1969", IMPL, "PDP-7 Unix · Томпсон",
         "fork = записати образ батька в ділянку відкачування; 27 рядків асемблера і жодного параметра"),
        ("1971", IMPL, "Unix, перша редакція · довідник fork(II)",
         "«єдиний спосіб створити процес»; помилка, якщо бракує місця в ділянці відкачування"),
        ("нині", LEGA, "Linux · clone()",
         "прапорці повертають вибір спільного, як у Genie; fork лишається окремим випадком поверх нього"),
    ]

    RAIL = 196
    y0, step = 122, 96
    p.append(line(RAIL, y0 - 34, RAIL, y0 + step * (len(rows) - 1) + 34, color=MUTED, sw=2, dash="6,5"))

    bx, bw = 244, 796
    for i, (year, accent, head, detail) in enumerate(rows):
        cy = y0 + i * step
        p.append(fitbox(46, cy - 21, 120, 42, year, size=14, fill="#ffffff",
                        stroke=accent, sw=1.8, color=accent, bold=True))
        p.append(line(166, cy, RAIL - 11, cy, color=accent, sw=1.6))
        p.append(circle(RAIL, cy, 9, fill=TINT[accent], stroke=accent))
        p.append(line(RAIL + 11, cy, bx, cy, color=accent, sw=1.6))
        p.append(rect(bx, cy - 33, bw, 66, fill=TINT[accent], stroke=accent, sw=1.7, rx=8))
        hs = fit_font(head, bw - 32, 13, True)
        p.append(text(bx + 16 + text_width(head, hs, True) / 2, cy - 6, head,
                      size=hs, color=accent, bold=True))
        ds = fit_font(detail, bw - 32, 12)
        p.append(text(bx + 16 + text_width(detail, ds) / 2, cy + 18, detail, size=ds, color=INK))

    p.append(text(W / 2, H - 24,
                  "дві реалізації розв'язують ту саму задачу протилежно: Genie описує майбутню гілку, Unix копіює наявну",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "fork-lineage.svg"), W, H, *p,
           title="Родовід «процесу» і «fork»: від статті 1963 року до clone()")


if __name__ == "__main__":
    fig_task_and_resources()
    fig_exec_survivors()
    fig_isolation_layers()
    fig_clone_ladder()
    fig_clone_stack_forms()
    fig_fork_lineage()
    print("OK: figures written to", OUT)
