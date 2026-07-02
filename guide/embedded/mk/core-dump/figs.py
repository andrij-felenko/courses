# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── timeline: дамп відв'язує мить збою від миті розслідування ──────────────────
# Ідея: збій, обробник і reboot стискаються в кілька сотень мілісекунд на місці;
# розбір може статися через тижні на іншому столі. Зонд мусить бути тут і зараз;
# дамп чекає скільки треба.

def fig_timeline():
    W, H = 760, 300
    p = []
    ax = 60
    ay = 120
    aw = 640

    # дві зони часу
    p.append(rect(ax, 60, 300, 150, fill="#fbeeee", stroke="#e7c6c6", sw=1.2, rx=8))
    p.append(rect(ax + 360, 60, 280, 150, fill="#eef4ff", stroke="#c9d6f0", sw=1.2, rx=8))
    p.append(text(ax + 150, 80, "на місці — кілька сотень мс", size=11, color=POS, bold=True))
    p.append(text(ax + 360 + 140, 80, "пізніше — хоч за тижні", size=11, color=NEG, bold=True))

    # вісь часу
    p.append(arrow(ax, ay, ax + aw, ay, color=INK, sw=1.8))
    p.append(text(ax + aw, ay + 20, "час", size=12, color=INK, italic=True, anchor="end"))

    # події на осі
    evs = [
        (ax + 70, "збій\n(panic)", POS, "#fdecea"),
        (ax + 180, "обробник пише\nдамп → Flash", "#e67e22", "#fff3e0"),
        (ax + 300, "reboot,\nпристрій працює", FIELD, "#eafaf0"),
        (ax + 500, "розбір на хості:\nдамп + .elf + GDB", NEG, "#eaf0fd"),
    ]
    for ex, lab, col, fill in evs:
        p.append(circle(ex, ay, 6, fill=col, stroke=col, sw=1.5))
        b, bw, bh = textbox(ex, ay - 48, lab, size=10, bold=True, color=col, fill=fill, stroke=col, sw=1.4)
        p.append(line(ex, ay - 6, ex, ay - 48 + bh / 2, color=col, sw=1.2, dash="3 3"))
        p.append(b)

    # підкреслення: зонд vs дамп
    p.append(line(ax + 70, 235, ax + 300, 235, color=POS, sw=2.0, dash="6 4"))
    p.append(text(ax + 185, 252, "живий зонд: мусить бути підключений саме тут", size=10, color=POS))
    p.append(line(ax + 180, 275, ax + 500, 275, color=NEG, sw=2.4))
    p.append(text(ax + 340, 292, "core dump: записаний раз — читається будь-коли", size=10, color=NEG, bold=True))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Дамп відв'язує мить збою від миті розслідування")


# ── anatomy: дамп = знімок задач + .elf-словник → офлайн-GDB ───────────────────
# Ідея: дамп компактний (TCB+стек кожної задачі, регістри, причина), уся RAM не
# влазить; сам по собі він — голі числа; разом зі своїм .elf оживає у звичайну
# GDB-сесію без живого чипа.

def fig_anatomy():
    W, H = 800, 360
    p = []

    # ліворуч — вміст дампа
    dx, dy, dw = 40, 60, 300
    p.append(rect(dx, dy, dw, 268, fill="#eef4ff", stroke=NEG, sw=2, rx=10))
    p.append(text(dx + dw / 2, dy + 22, "core dump (бінарний, у Flash)", size=12, color=NEG, bold=True))
    rows = [
        ("заголовок", "версія, чип, причина паніки", "#dbe6fb"),
        ("регістри кожної задачі", "PC, SP, EXCCAUSE, EXCVADDR…", "#fdecea"),
        ("стек + TCB: app_task", "повний зріз", "#eafaf0"),
        ("стек + TCB: wifi_task", "повний зріз", "#eafaf0"),
    ]
    ry = dy + 40
    for title, sub, fill in rows:
        p.append(rect(dx + 12, ry, dw - 24, 40, fill=fill, stroke=LINE, sw=1.0, rx=4))
        p.append(text(dx + dw / 2, ry + 17, title, size=11, color=INK, bold=True))
        p.append(text(dx + dw / 2, ry + 32, sub, size=9, color=MUTED))
        ry += 48
    p.append(text(dx + dw / 2, ry + 14, "купа й уся RAM не влазять —", size=10, color=POS))
    p.append(text(dx + dw / 2, ry + 30, "зберігають стеки задач і обране", size=10, color=POS))

    # посередині — .elf як словник
    ex, ey, ew, eh = 380, 150, 150, 90
    p.append(rect(ex, ey, ew, eh, fill="#fff3e0", stroke="#e67e22", sw=2, rx=8))
    p.append(text(ex + ew / 2, ey + 30, "app.elf", size=15, color="#e67e22", bold=True))
    p.append(text(ex + ew / 2, ey + 52, "«словник»", size=11, color="#e67e22"))
    p.append(text(ex + ew / 2, ey + 72, "адреса → ім'я, рядок", size=9, color=MUTED))
    p.append(arrow(dx + dw, ey + eh / 2, ex - 4, ey + eh / 2, color=NEG, sw=1.8))

    # праворуч — офлайн-GDB
    gx, gy, gw, gh = 590, 140, 175, 110
    p.append(rect(gx, gy, gw, gh, fill="#eafaf0", stroke=FIELD, sw=2, rx=8))
    p.append(text(gx + gw / 2, gy + 26, "GDB на хості", size=13, color=FIELD, bold=True))
    for i, ln in enumerate(["backtrace", "info threads", "print var"]):
        p.append(text(gx + gw / 2, gy + 48 + i * 18, ln, size=11, color=INK))
    p.append(text(gx + gw / 2, gy + gh - 6, "(живий чип не потрібен)", size=9, color=MUTED))
    p.append(arrow(ex + ew, ey + eh / 2, gx - 4, gy + gh / 2, color="#e67e22", sw=1.8))

    render(os.path.join(OUT, "anatomy.svg"), W, H, *p,
           title="Знімок задач + .elf-словник = жива GDB-сесія")


# ── two-questions: причина reset відповідає ЩО, дамп — ДЕ і ЧОМУ ────────────────
# Ідея: повне посмертне = два дешеві джерела, що відповідають на різні питання.
# Причина reset доступна завжди після перезавантаження; дамп — лише коли його
# встигли записати (і не у Flash-драйвері).

def fig_two_questions():
    W, H = 740, 320
    p = []
    cx = W / 2

    # верх — подія
    top, tw, th = textbox(cx, 56, "пристрій перезавантажився", size=12, bold=True,
                          fill="#2d3e50", stroke="#2d3e50", color="#ffffff", pad=12)
    p.append(top)

    # ліва колонка — причина reset (ЩО)
    lx = 170
    lb, lw, lh = textbox(lx, 150, "esp_reset_reason()\n(регістр RTC)", size=11, bold=True,
                         color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.8)
    p.append(lb)
    p.append(line(cx, 56 + th / 2, lx, 150 - lh / 2, color=NEG, sw=1.5))
    p.append(text(lx, 196, "ЩО сталося", size=12, color=NEG, bold=True))
    for i, ln in enumerate(["PANIC — впав у паніку", "BROWNOUT — просів струм",
                            "WDT — застряг, watchdog", "DEEPSLEEP — прокинувся"]):
        p.append(text(lx, 218 + i * 20, ln, size=10, color=INK))

    # права колонка — core dump (ДЕ і ЧОМУ)
    rx = W - 170
    rb, rw, rh = textbox(rx, 150, "core dump + .elf\n(GDB офлайн)", size=11, bold=True,
                         color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(rb)
    p.append(line(cx, 56 + th / 2, rx, 150 - rh / 2, color=FIELD, sw=1.5))
    p.append(text(rx, 196, "ДЕ і ЧОМУ", size=12, color=FIELD, bold=True))
    for i, ln in enumerate(["задача й рядок збою", "backtrace кожної задачі",
                            "регістри, EXCVADDR", "значення змінних"]):
        p.append(text(rx, 218 + i * 20, ln, size=10, color=INK))

    # підказка: дамп є не завжди
    p.append(text(rx, 218 + 4 * 20 + 4, "лише якщо встиг записатися", size=9, color=POS, italic=True))

    render(os.path.join(OUT, "two-questions.svg"), W, H, *p,
           title="Два дешеві джерела — на два різні питання")


# ── limits: чому обробник іноді не лишає дампа ─────────────────────────────────
# Ідея: запис дампа — не магія, а звичайний код у найгірший момент. Чотири
# чесні діри: збій у Flash-драйвері, пошкоджений стек, мала ділянка пам'яті,
# нестача місця в розділі.

def fig_limits():
    W, H = 740, 300
    p = []
    cx = W / 2

    ccy = 150
    core, cw, ch = textbox(cx, ccy, "обробник паніки\nпише дамп", size=12, bold=True,
                           fill="#fff3e0", stroke="#e67e22", color="#e67e22", pad=14)

    holes = [
        (160, 70, "збій у Flash-\nдрайвері → нікуди\nписати", POS, "#fdecea"),
        (W - 160, 70, "стек пошкоджено →\nbacktrace неповний\nабо хибний", POS, "#fdecea"),
        (160, H - 64, "купа не входить →\nстан поза стеком\nне видно", "#e67e22", "#fff3e0"),
        (W - 160, H - 64, "розділ малий →\nдамп обрізано", "#e67e22", "#fff3e0"),
    ]
    for hx, hy, lab, col, fill in holes:
        b, bw, bh = textbox(hx, hy, lab, size=10, bold=True, color=col, fill=fill, stroke=col, sw=1.6)
        above = hy < ccy
        dirx = 1 if hx < cx else -1
        ay_ = hy + (bh / 2 if above else -bh / 2)
        tx = cx - dirx * cw / 2
        ty = ccy - (ch / 2 if above else -ch / 2)
        p.append(line(hx, ay_, tx, ty, color=col, sw=1.5, dash="4 3"))
        p.append(b)

    p.append(core)

    render(os.path.join(OUT, "limits.svg"), W, H, *p,
           title="Запис дампа — звичайний код у найгірший момент")


# ── elf-anatomy: дамп = числа у двох сегментах + .elf-словник, зшиті за адресою ─
# Ідея (detailed): ELF-core має PT_LOAD (зрізи пам'яті: стеки+TCB) і PT_NOTE
# (нотатки NT_PRSTATUS/CORE: регістри на задачу). Це самі числа. .elf несе
# символи+DWARF (адреса→ім'я,рядок). GDB зшиває ВИКЛЮЧНО за адресою.

def fig_elf_anatomy():
    W, H = 820, 400
    p = []

    # ── ліворуч: дамп (ELF-core), два види сегментів ──
    dx, dy, dw = 34, 58, 322
    p.append(rect(dx, dy, dw, 312, fill="#eef4ff", stroke=NEG, sw=2, rx=10))
    p.append(text(dx + dw / 2, dy + 22, "core dump — файл ELF (у Flash)", size=12, color=NEG, bold=True))
    p.append(text(dx + dw / 2, dy + 39, "самі числа: адреси й значення", size=9, color=MUTED, italic=True))

    # PT_LOAD блок
    lx, ly, lw, lh = dx + 14, dy + 52, dw - 28, 112
    p.append(rect(lx, ly, lw, lh, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=6))
    p.append(text(lx + lw / 2, ly + 18, "сегменти PT_LOAD — зрізи пам'яті", size=10, color=FIELD, bold=True))
    for i, ln in enumerate(["стек + TCB: sensor_task", "стек + TCB: wifi_task", "стек + TCB: app_task"]):
        yy = ly + 30 + i * 24
        p.append(rect(lx + 10, yy, lw - 20, 20, fill="#ffffff", stroke=LINE, sw=0.9, rx=3))
        p.append(text(lx + lw / 2, yy + 14, ln, size=9, color=INK))

    # PT_NOTE блок
    nx, ny, nw, nh = dx + 14, ly + lh + 12, dw - 28, 96
    p.append(rect(nx, ny, nw, nh, fill="#fdecea", stroke=POS, sw=1.6, rx=6))
    p.append(text(nx + nw / 2, ny + 18, "сегмент PT_NOTE — метадані", size=10, color=POS, bold=True))
    for i, ln in enumerate(["нотатка CORE / NT_PRSTATUS", "регістри на задачу:", "PC · SP · EXCCAUSE · EXCVADDR"]):
        p.append(text(nx + nw / 2, ny + 36 + i * 17, ln, size=9, color=INK,
                      bold=(i == 0)))

    # ── праворуч-угорі: .elf-словник ──
    ex, ey, ew, eh = 470, 66, 316, 128
    p.append(rect(ex, ey, ew, eh, fill="#fff3e0", stroke="#d97706", sw=2, rx=10))
    p.append(text(ex + ew / 2, ey + 22, "app.elf — словник імен", size=12, color="#b45309", bold=True))
    p.append(text(ex + ew / 2, ey + 40, "таблиця символів + DWARF", size=9, color=MUTED, italic=True))
    p.append(line(ex + 16, ey + 50, ex + ew - 16, ey + 50, color="#e7c98a", sw=1.0))
    rows = ["0x400d1f88  →  sensor_read", "sensor.c : 88", "аргумент buf  →  зсув у кадрі"]
    for i, ln in enumerate(rows):
        p.append(text(ex + ew / 2, ey + 70 + i * 18, ln, size=10, color=INK, bold=(i == 0)))

    # ── праворуч-унизу: GDB зшиває ──
    gx, gy, gw, gh = 470, 232, 316, 96
    p.append(rect(gx, gy, gw, gh, fill="#f4f6f8", stroke=INK, sw=2, rx=10))
    p.append(text(gx + gw / 2, gy + 22, "GDB на хості: зшиває за адресою", size=12, color=INK, bold=True))
    p.append(text(gx + gw / 2, gy + 44, "PC із нотатки  →  шукає в символах .elf", size=9.5, color=INK))
    p.append(text(gx + gw / 2, gy + 62, "backtrace · info threads · print var", size=9.5, color=NEG))
    p.append(text(gx + gw / 2, gy + 80, "не той .elf → впевнено хибний результат", size=9, color=POS, italic=True))

    # стрілки: дамп → GDB (числа), .elf → GDB (імена)
    p.append(arrow(dx + dw, dy + 200, gx - 4, gy + 30, color=NEG, sw=1.8))
    p.append(text(dx + dw + 66, dy + 188, "числа", size=9, color=NEG, italic=True))
    p.append(arrow(ex + ew / 2, ey + eh, gx + gw / 2, gy - 4, color="#b45309", sw=1.8))
    p.append(text(ex + ew / 2 + 40, ey + eh + 20, "імена", size=9, color="#b45309", italic=True))

    render(os.path.join(OUT, "elf-anatomy.svg"), W, H, *p,
           title="Числа в дампі + імена в .elf, зшиті GDB за адресою")


# ── xtensa-windows: чому backtrace Xtensa крихкий ─────────────────────────────
# Ідея (detailed): виклик прокручує вікно по 64 фізичних регістрах замість
# запису в стек; адреса повернення живе в a0 кадру (2 старші біти — CALLINC,
# маскувати), стек в a1. Для розмотування GDB треба WINDOWBASE/WINDOWSTART/PS.
# Коли вікон забагато — старі виштовхуються в стек.

def fig_xtensa_windows():
    import math
    W, H = 820, 400
    p = []

    # ── ліворуч: коло з 64 фізичних регістрів + видиме вікно ──
    ccx, ccy, R = 220, 226, 128
    p.append(circle(ccx, ccy, R, fill="#f4f6f8", stroke=MUTED, sw=1.4))
    p.append(circle(ccx, ccy, R - 34, fill=BG, stroke="#d8dbe0", sw=1.0))
    p.append(text(ccx, ccy - 4, "64 фізичні", size=11, color=MUTED, bold=True))
    p.append(text(ccx, ccy + 12, "регістри", size=11, color=MUTED, bold=True))

    # три «вікна» секторами: поточне (зелене) і два старіші (сині, тьмяніші)
    wins = [(-38, 22, FIELD, "#eafaf0", "вікно кадру,\nщо впав"),
            (24, 84, NEG, "#eaf0fd", "викликач"),
            (86, 146, "#7f9fe0", "#eef3fd", "старіший")]
    for a0d, a1d, col, fill, lab in wins:
        # дуга-сектор
        r_out, r_in = R, R - 34
        a0 = math.radians(a0d); a1 = math.radians(a1d)
        x0o, y0o = ccx + r_out * math.cos(a0), ccy + r_out * math.sin(a0)
        x1o, y1o = ccx + r_out * math.cos(a1), ccy + r_out * math.sin(a1)
        x1i, y1i = ccx + r_in * math.cos(a1), ccy + r_in * math.sin(a1)
        x0i, y0i = ccx + r_in * math.cos(a0), ccy + r_in * math.sin(a0)
        d = ("M%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f L%.1f %.1f A%.1f %.1f 0 0 0 %.1f %.1f Z"
             % (x0o, y0o, r_out, r_out, x1o, y1o, x1i, y1i, r_in, r_in, x0i, y0i))
        p.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (d, fill, col))
        # мітка a0/a1 у секторі
        am = math.radians((a0d + a1d) / 2); rm = (r_out + r_in) / 2
        p.append(text(ccx + rm * math.cos(am), ccy + rm * math.sin(am) + 4,
                      "a0 a1", size=9, color=col, bold=True))

    p.append(text(ccx, ccy + R + 22, "виклик прокручує вікно —", size=10, color=INK))
    p.append(text(ccx, ccy + R + 38, "у стек НЕ пише (швидко)", size=10, color=FIELD, bold=True))

    # підпис поточного вікна
    p.append(text(ccx + R + 4, ccy - 92, "a0 = адреса повернення", size=10, color=INK, anchor="start"))
    p.append(text(ccx + R + 4, ccy - 74, "(2 старші біти = CALLINC,", size=9, color=POS, anchor="start"))
    p.append(text(ccx + R + 4, ccy - 58, " маскувати: 0x8… → 0x4…)", size=9, color=POS, anchor="start"))
    p.append(text(ccx + R + 4, ccy - 38, "a1 = покажчик стека", size=10, color=INK, anchor="start"))

    # ── праворуч: що потрібно GDB, щоб розмотати ──
    gx, gy, gw = 512, 84, 276
    b, bw, bh = textbox(gx + gw / 2, gy + 44, "щоб розмотати ланцюг,\nGDB бере з дампа:", size=11,
                        bold=True, color=INK, fill="#fff3e0", stroke="#d97706", sw=1.8, min_w=gw)
    p.append(b)
    regs = ["WINDOWBASE — де вікно", "WINDOWSTART — які зайняті", "PS — стан процесора"]
    for i, ln in enumerate(regs):
        yy = gy + 96 + i * 26
        p.append(rect(gx, yy, gw, 20, fill="#f4f6f8", stroke=LINE, sw=0.9, rx=4))
        p.append(text(gx + gw / 2, yy + 14, ln, size=10, color=INK))
    p.append(text(gx + gw / 2, gy + 190, "вікон забагато →", size=10, color=INK))
    p.append(text(gx + gw / 2, gy + 206, "старі виштовхуються в стек", size=10, color=NEG, bold=True))

    # висновок-стрічка внизу
    p.append(line(gx, gy + 226, gx + gw, gy + 226, color="#e0e0e0", sw=1.0))
    p.append(text(gx + gw / 2, gy + 244, "зіпсована адреса повернення →", size=9.5, color=POS))
    p.append(text(gx + gw / 2, gy + 260, "хибний backtrace без попередження", size=9.5, color=POS, bold=True))

    render(os.path.join(OUT, "xtensa-windows.svg"), W, H, *p,
           title="Вікна регістрів: адреса повернення живе не тільки в стеку")


# ── xtensa-vs-cortexm: та сама ідея на двох архітектурах ──────────────────────
# Ідея (detailed): Xtensa — адреса повернення у вікнах (потрібні 3 рег.),
# EXCCAUSE/EXCVADDR, готовий дамп від ESP-IDF. Cortex-M — адреса в стеку (LR),
# CFSR/BFAR (з бітом BFARVALID), дамп пишеш сам у HardFault_Handler.

def fig_xtensa_vs_cortexm():
    W, H = 820, 372
    p = []

    def column(x0, w, head, hc, hfill, rows):
        cx = x0 + w / 2
        p.append(rect(x0, 52, w, 300, fill=hfill, stroke=hc, sw=2, rx=10))
        p.append(text(cx, 76, head, size=14, color=hc, bold=True))
        yy = 100
        for label, val, vc in rows:
            p.append(text(cx, yy, label, size=10, color=MUTED, bold=True))
            b = fitbox(x0 + 16, yy + 8, w - 32, 34, val, size=10, pad=6,
                       fill="#ffffff", stroke=vc, sw=1.3, color=INK, rx=5)
            p.append(b)
            yy += 58

    column(30, 372, "Xtensa (ESP32)", NEG, "#eef4ff", [
        ("адреса повернення", "у вікнах регістрів →\nтреба WINDOWBASE/WINDOWSTART/PS", FIELD),
        ("клас і адреса помилки", "EXCCAUSE (клас)  ·  EXCVADDR (адреса)", POS),
        ("хто робить дамп", "ESP-IDF: обхід задач, запис у Flash, ELF —\nвідкриває GDB готовим", FIELD),
        ("розмотування", "крихке: вікна + маскування CALLINC", INK),
    ])

    column(418, 372, "ARM Cortex-M", "#b45309", "#fff7ed", [
        ("адреса повернення", "у стеку (LR збережено в пам'ять) →\nланцюг увесь у пам'яті", FIELD),
        ("клас і адреса помилки", "CFSR (клас)  ·  BFAR/MMFAR (адреса,\nдійсна лише за бітом BFARVALID)", POS),
        ("хто робить дамп", "готового немає: HardFault_Handler\nпишеш сам, зберігаєш у .noinit-RAM", POS),
        ("розмотування", "простіше: увесь ланцюг у стеку", INK),
    ])

    # центральна вісь: спільна ідея
    p.append(text(W / 2, 44, "та сама абстракція — заморозити стан у мить смерті", size=11,
                  color=INK, bold=True))

    render(os.path.join(OUT, "xtensa-vs-cortexm.svg"), W, H, *p,
           title="Один прийом, дві архітектури: що істотне, а що деталь ядра")


# ── sizing-anatomy: звідки береться кожен байт формули розміру ─────────────────
# Ідея (math): розмір ≈ 20 + N·(12 + TCB + макс_стек). Показати ПОФАЙЛОВО, куди
# йде кожен доданок: 20 — спільний заголовок; далі N однакових блоків, у кожному
# 12 (службовий запис) + TCB + макс_стек. Множник N перед дужкою = лінійне
# зростання: додав задачу — додав цілий блок.

def fig_sizing_anatomy():
    W, H = 800, 372
    p = []

    # спільний заголовок (20 Б) — вузька смужка зверху
    hx, hy, hw, hh = 60, 62, 680, 30
    p.append(rect(hx, hy, hw, hh, fill="#f4f6f8", stroke=INK, sw=1.6, rx=5))
    p.append(text(hx + hw / 2, hy + 20, "20 Б — спільний заголовок дампа (версія, чип, причина) — один на весь файл",
                  size=10.5, color=INK, bold=True))

    # три однакові блоки «на задачу» + «…» — показати повторюваність
    by = hy + hh + 26
    bw = 200
    bh = 176
    gap = 30
    xs = [60, 60 + bw + gap, 60 + 2 * (bw + gap)]
    labels = ["задача 1", "задача 2", "задача N"]
    for i, (bx, lab) in enumerate(zip(xs, labels)):
        p.append(rect(bx, by, bw, bh, fill="#eef4ff", stroke=NEG, sw=1.8, rx=8))
        p.append(text(bx + bw / 2, by + 20, "блок «на задачу»", size=10, color=NEG, bold=True))
        p.append(text(bx + bw / 2, by + 36, lab, size=10, color=MUTED))
        # три доданки блоку, висота ∝ типовий розмір
        parts = [
            ("12 Б", "службовий запис", "#fdf0e0", "#e67e22", 26),
            ("TCB ≈ 100 Б", "блок керування", "#eafaf0", FIELD, 40),
            ("макс_стек", "найтовщий стек", "#eaf0fd", NEG, 66),
        ]
        yy = by + 46
        for val, sub, fill, col, ph in parts:
            p.append(rect(bx + 12, yy, bw - 24, ph, fill=fill, stroke=col, sw=1.2, rx=4))
            p.append(text(bx + bw / 2, yy + ph / 2 - 2, val, size=10, color=col, bold=True))
            p.append(text(bx + bw / 2, yy + ph / 2 + 12, sub, size=8.5, color=MUTED))
            yy += ph + 4

    # «…» між 2-м і N-м блоком
    midx = (xs[1] + bw + xs[2]) / 2
    p.append(text(midx, by + bh / 2, "· · ·", size=22, color=MUTED, bold=True))

    # дужка знизу: усе це × N
    ry = by + bh + 22
    p.append(line(xs[0], ry, xs[2] + bw, ry, color=NEG, sw=1.6))
    p.append(line(xs[0], ry, xs[0], ry - 8, color=NEG, sw=1.6))
    p.append(line(xs[2] + bw, ry, xs[2] + bw, ry - 8, color=NEG, sw=1.6))
    b, bw2, bh2 = textbox((xs[0] + xs[2] + bw) / 2, ry + 22,
                          "× N задач  (N = CONFIG_ESP_COREDUMP_MAX_TASKS_NUM)",
                          size=11, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.5)
    p.append(b)

    render(os.path.join(OUT, "sizing-anatomy.svg"), W, H, *p,
           title="Куди йде кожен байт: 20 + N·(12 + TCB + макс_стек)")


# ── linear-growth: дамп росте лінійно з N, а розділ — стеля ────────────────────
# Ідея (math): розмір — пряма лінія від N (нахил = 12+TCB+макс_стек). Розділи
# 64/128/256 КБ — горизонтальні стелі; де пряма перетинає стелю, дамп починає
# тихо обрізатися. Видно, що 64 КБ вичерпується вже на ~15 задачах при товстих
# стеках.

def fig_linear_growth():
    W, H = 780, 430
    p = []
    # осі
    ox, oy = 90, 360          # початок координат
    axw, axh = 610, 300       # довжина осей
    p.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))          # X: N
    p.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))          # Y: розмір
    p.append(text(ox + axw - 4, oy + 24, "N — кількість задач (MAX_TASKS_NUM)", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 60, oy - axh + 4, "розмір дампа, КБ", size=11, color=INK, italic=True, anchor="start"))

    # масштаб: N 0..40, розмір 0..280 КБ
    Nmax = 40.0
    Kmax = 280.0
    def X(n): return ox + axw * (n / Nmax)
    def Y(k): return oy - axh * (k / Kmax)

    # сітка X
    for n in range(0, 41, 8):
        p.append(line(X(n), oy, X(n), oy + 5, color=INK, sw=1.2))
        p.append(text(X(n), oy + 20, str(n), size=10, color=MUTED))

    # стелі розділів
    ceilings = [(64, "розділ 64 КБ"), (128, "розділ 128 КБ"), (256, "розділ 256 КБ")]
    for k, lab in ceilings:
        p.append(line(ox, Y(k), ox + axw, Y(k), color="#b45309", sw=1.4, dash="7 4"))
        p.append(text(ox + axw - 6, Y(k) - 6, lab, size=9.5, color="#b45309", anchor="end", bold=True))
        p.append(text(ox - 8, Y(k) + 4, str(k), size=9.5, color="#b45309", anchor="end"))

    # пряма розміру: slope = (12+100+4096)=4208 Б/задачу ≈ 4.109 КБ; +20 Б ≈ 0
    slope = 4208.0 / 1024.0     # КБ на задачу
    def size_kb(n): return (20 + n * 4208.0) / 1024.0
    p.append(line(X(0), Y(size_kb(0)), X(Nmax), Y(size_kb(Nmax)), color=NEG, sw=2.6))
    p.append(text(X(31), Y(size_kb(31)) - 12, "стек 4 КБ:  20 + N·4208 Б", size=10.5, color=NEG, bold=True, anchor="middle"))

    # точки перетину зі стелями (де дамп починає обрізатися)
    for k, _ in ceilings:
        n_cross = (k * 1024.0 - 20) / 4208.0
        if n_cross <= Nmax:
            p.append(circle(X(n_cross), Y(k), 5, fill=POS, stroke=POS, sw=1.5))
            p.append(line(X(n_cross), Y(k), X(n_cross), oy, color=POS, sw=1.0, dash="3 3"))
            p.append(text(X(n_cross), oy - 4, "N≈%d" % round(n_cross), size=9, color=POS, bold=True))

    # зона тихого обрізання (над найнижчою стелею, під прямою) — легка штриховка словом
    p.append(text(X(30), Y(240), "вище стелі → дамп", size=10, color=POS, bold=True, anchor="middle"))
    p.append(text(X(30), Y(240) + 15, "тихо обрізається", size=10, color=POS, anchor="middle"))

    render(os.path.join(OUT, "linear-growth.svg"), W, H, *p,
           title="Дамп росте лінійно з N; розділ — стеля, за якою обрізання")


# ── worst-vs-real: найгірший випадок проти реальних стеків ─────────────────────
# Ідея (math): формула бере МАКСИМАЛЬНИЙ стек для КОЖНОЇ задачі (найгірший
# випадок) — рівні високі стовпці. Реально стеки різко нерівні: одна-дві товсті
# (мережа), решта тонкі. Дві дії, що зводять розділ до мінімуму: реальні розміри
# замість максимуму (нижчі стовпці) і менший N (менше стовпців).

def fig_worst_vs_real():
    W, H = 800, 372
    p = []

    def panel(x0, w, title, tc, heights, note):
        cx = x0 + w / 2
        base = 300
        p.append(text(cx, 54, title, size=12, color=tc, bold=True))
        # осі-підлога
        p.append(line(x0 + 20, base, x0 + w - 12, base, color=INK, sw=1.4))
        n = len(heights)
        bw = (w - 44) / n * 0.66
        step = (w - 44) / n
        for i, h in enumerate(heights):
            bx = x0 + 24 + i * step
            col = NEG if h >= 60 else FIELD
            fill = "#eaf0fd" if h >= 60 else "#eafaf0"
            p.append(rect(bx, base - h, bw, h, fill=fill, stroke=col, sw=1.3, rx=2))
        # підпис-нота
        p.append(text(cx, base + 22, note, size=9.5, color=MUTED))

    # ліворуч — найгірший випадок: усі стовпці однаково високі (макс_стек)
    hi = 150
    panel(24, 372, "формула: макс_стек × кожна задача", POS,
          [hi] * 8, "рівні високі стовпці — запас на найгірше")
    p.append(text(24 + 186, 96, "N · макс_стек", size=11, color=POS, bold=True))

    # праворуч — реальність: 1–2 товсті, решта тонкі
    panel(418, 372, "реальні розміри стеків", FIELD,
          [150, 96, 40, 34, 30, 28, 26, 24], "нерівні: мережа товста, решта тонкі")
    p.append(text(418 + 186, 96, "≪ набагато менше", size=11, color=FIELD, bold=True))

    # дві стрілки-важелі внизу
    p.append(text(W / 2, 342, "два важелі: реальні стеки (нижчі стовпці) · менший N (менше стовпців)",
                  size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "worst-vs-real.svg"), W, H, *p,
           title="Найгірший випадок (запас) проти реальних стеків")


# ── core-coincident (hist): прямокутний гістерезис + збіг струмів ──────────────
# Ідея (hist): осердя має майже прямокутну петлю гістерезису — це ПОРІГ. Пів-струм
# по одному дроту (H/2) НЕ перекидає осердя; лише там, де перетинаються дріт X і
# дріт Y, поля складаються (H/2 + H/2 = H) і осердя перекидається. Так двома
# дротами з десятків адресуємо РІВНО одне осердя в сітці. Це — винахід Форрестера.

def fig_core_coincident():
    W, H = 820, 440
    p = []

    # ── ліва панель: прямокутна петля гістерезису як поріг ──
    ax, ay = 155, 230         # центр осей петлі
    axw, axh = 95, 115        # піввісь по H та по B
    p.append(text(ax, 74, "петля осердя = поріг", size=12, color=INK, bold=True))
    # осі H (гор.) та B (верт.)
    p.append(arrow(ax - axw, ay, ax + axw, ay, color=INK, sw=1.5))
    p.append(arrow(ax, ay + axh, ax, ay - axh, color=INK, sw=1.5))
    p.append(text(ax + axw, ay + 18, "H (струм)", size=10, color=MUTED, anchor="end"))
    p.append(text(ax - axw + 4, ay - axh + 2, "B", size=10, color=MUTED, anchor="start"))
    # майже прямокутна петля: горизонтальні рівні ±Bs, вертикальні стінки при ±Hc
    hc = 60                   # коерцитивне поле (поріг) — має бути > axw*0.5, < axw
    bs = 74                   # насичення
    xl = ax - axw + 12        # ліва межа горизонтальних гілок (у полі осей)
    xr = ax + axw - 12
    loop = ("M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f "
            "M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f") % (
        xl, ay - bs, ax + hc, ay - bs, ax + hc, ay + bs, xl, ay + bs,   # верхня→права стінка вниз
        xr, ay + bs, ax - hc, ay + bs, ax - hc, ay - bs, xr, ay - bs)   # нижня→ліва стінка вгору
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (loop, NEG))
    # позначки порогу +Hc/2 і +Hc
    for sgn, lab, col in [(0.5, "H/2", MUTED), (1.0, "H", POS)]:
        xx = ax + hc * sgn
        p.append(line(xx, ay - 4, xx, ay + 4, color=col, sw=1.4))
        p.append(text(xx, ay + 20, lab, size=9.5, color=col, bold=(sgn == 1.0)))
    # ключова думка: пів-струм не доходить до стінки, повний — перекидає
    b, bw, bh = textbox(ax, ay + axh + 40, "H/2 — не перекидає\nH — перекидає осердя", size=10,
                        bold=True, color=INK, fill="#f4f6f8", stroke=MUTED, sw=1.2)
    p.append(b)

    # ── права панель: сітка X×Y, збіг лише в перетині ──
    gx, gy = 470, 118         # лівий-верхній кут сітки
    cell = 58
    n = 4
    p.append(text(gx + n * cell / 2, 74, "збіг струмів у сітці", size=12, color=INK, bold=True))
    sel_row, sel_col = 1, 2   # обраний рядок (Y) і стовпець (X)

    # осердя-кільця у вузлах
    for r in range(n):
        for c in range(n):
            cxx = gx + c * cell + cell / 2
            cyy = gy + r * cell + cell / 2
            on_x = (c == sel_col)
            on_y = (r == sel_row)
            if on_x and on_y:
                ring, col = "#c0392b", POS          # перекинулось
                p.append(circle(cxx, cyy, 15, fill="#fdecea", stroke=col, sw=3))
            elif on_x or on_y:
                ring, col = "#b45309", "#b45309"     # пів-струм — не перекинулось
                p.append(circle(cxx, cyy, 13, fill="#fff7ed", stroke=col, sw=2))
            else:
                p.append(circle(cxx, cyy, 12, fill="#eef1f4", stroke=MUTED, sw=1.4))

    # дроти X (вертикальні) і Y (горизонтальні); обрані — товсті кольорові
    for c in range(n):
        xx = gx + c * cell + cell / 2
        col = POS if c == sel_col else "#d7dbe0"
        sw = 3.2 if c == sel_col else 1.4
        p.append(line(xx, gy - 6, xx, gy + n * cell + 6, color=col, sw=sw))
    for r in range(n):
        yy = gy + r * cell + cell / 2
        col = NEG if r == sel_row else "#d7dbe0"
        sw = 3.2 if r == sel_row else 1.4
        p.append(line(gx - 6, yy, gx + n * cell + 6, yy, color=col, sw=sw))

    # підписи дротів-адрес
    p.append(text(gx + sel_col * cell + cell / 2, gy - 14, "дріт X: H/2", size=10, color=POS, bold=True))
    p.append(text(gx + n * cell + 10, gy + sel_row * cell + cell / 2 + 4, "Y: H/2", size=10, color=NEG, bold=True, anchor="start"))
    # виноска на перекинуте осердя
    tx = gx + sel_col * cell + cell / 2
    ty = gy + sel_row * cell + cell / 2
    b, bw, bh = textbox(gx + n * cell / 2, gy + n * cell + 44,
                        "лише тут H/2 + H/2 = H → єдине осердя перекинулось",
                        size=10.5, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.5)
    p.append(b)

    render(os.path.join(OUT, "core-coincident.svg"), W, H, *p,
           title="Збіг струмів: два пів-струми адресують рівно одне осердя")


if __name__ == "__main__":
    fig_core_coincident()
    fig_timeline()
    fig_anatomy()
    fig_two_questions()
    fig_limits()
    fig_elf_anatomy()
    fig_xtensa_windows()
    fig_xtensa_vs_cortexm()
    fig_sizing_anatomy()
    fig_linear_growth()
    fig_worst_vs_real()
    print("OK: figures written to", OUT)
