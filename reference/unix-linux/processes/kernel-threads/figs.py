# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COOL = "#eaf0fd"
GREENISH = "#eafaf0"


# ── 1. Порівняння: звичайна задача і задача ядра ───────────────────────────────
def fig_anatomy():
    W, H = 1060, 600
    p = []

    col_l = 40          # колонка ознаки
    col_a = 380         # звичайна задача
    col_b = 720         # задача ядра
    cw_l, cw = 320, 320
    hy = 44
    hh = 52

    p.append(fitbox(col_l, hy, cw_l, hh, "Що складає задачу", size=14,
                    fill="#ffffff", stroke=MUTED, sw=1.4, color=MUTED, bold=True))
    p.append(fitbox(col_a, hy, cw, hh, "Звичайна задача\n(потік програми)", size=13,
                    fill=COOL, stroke=NEG, sw=1.8, color=NEG, bold=True))
    p.append(fitbox(col_b, hy, cw, hh, "Задача ядра\n(PF_KTHREAD)", size=13,
                    fill=GREENISH, stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    rows = [
        ("Відображення пам'яті",
         "mm_struct — власне",
         "mm = NULL,\nactive_mm позичений"),
        ("Стек користувача",
         "є, росте від вершини\nадресного простору",
         "немає взагалі"),
        ("Стек ядра",
         "є, 16 КіБ на x86-64",
         "є, той самий —\nі він єдиний"),
        ("Образ ELF, argv, оточення",
         "є, лишилися від execve",
         "немає: нічого\nне завантажували"),
        ("/proc/N/cmdline",
         "рядок запуску",
         "порожній → ps друкує\nім'я у [дужках]"),
        ("Час у /proc/N/stat",
         "utime + stime",
         "лише stime:\nutime завжди 0"),
        ("Для планувальника",
         "рядок у черзі",
         "такий самий рядок\nу тій самій черзі"),
    ]

    y = hy + hh + 14
    rh = 58
    for name, a, b in rows:
        p.append(fitbox(col_l, y, cw_l, rh, name, size=12,
                        fill="#ffffff", stroke="#d7dbe0", sw=1.2, color=INK))
        p.append(fitbox(col_a, y, cw, rh, a, size=11,
                        fill=SOFT, stroke=NEG, sw=1.3, color=INK))
        p.append(fitbox(col_b, y, cw, rh, b, size=11,
                        fill=SOFT, stroke=FIELD, sw=1.3, color=INK))
        y += rh + 8

    p.append(text(W / 2, y + 22,
                  "різниця не в природі задачі, а в тому, чого в неї немає: половини з боку користувача",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "kernel-task-anatomy.svg"), W, H, *p,
           title="Звичайна задача і задача ядра: що є, а чого немає")


# ── 2. Народження потоку ядра і два корені дерева ─────────────────────────────
def fig_birth():
    W, H = 1060, 620
    p = []

    p.append(fitbox(40, 34, 980, 34, "Шлях створення: замовник лише лишає заявку", size=13,
                    fill="#ffffff", stroke=MUTED, sw=1.4, color=MUTED, bold=True))

    steps = [
        ("драйвер чи підсистема\nkthread_run(fn, ...)", COOL, NEG),
        ("заявку в чергу\nkthread_create_list", SOFT, MUTED),
        ("прокидається kthreadd\nPID 2", GREENISH, FIELD),
        ("клон від init_task:\nчисте оточення", SOFT, MUTED),
        ("нова задача\nвиконує fn()", GREENISH, FIELD),
    ]
    bx, by, bw, bh, gap = 40, 84, 172, 66, 30
    for i, (label, fill, stroke) in enumerate(steps):
        x = bx + i * (bw + gap)
        p.append(fitbox(x, by, bw, bh, label, size=11, fill=fill, stroke=stroke, sw=1.6, color=INK))
        if i:
            p.append(arrow(x - gap + 4, by + bh / 2, x - 5, by + bh / 2, color=MUTED, sw=1.6))

    p.append(text(W / 2, by + bh + 32,
                  "посередник потрібен, бо нова задача успадковує оточення батька — "
                  "а батьком має бути завідомо чистий предок, а не випадковий процес",
                  size=11, color=MUTED, italic=True))

    # ── дерево з двома коренями ──
    ty = 250
    p.append(fitbox(40, ty, 980, 32, "Дерево задач: два корені під спільним нулем", size=13,
                    fill="#ffffff", stroke=MUTED, sw=1.4, color=MUTED, bold=True))

    root_y = ty + 54
    p.append(fitbox(410, root_y, 240, 52, "0 — задача простою\n(swapper, у ps не видно)", size=11,
                    fill="#ffffff", stroke=MUTED, sw=1.6, color=MUTED))

    mid_y = root_y + 96
    p.append(fitbox(150, mid_y, 250, 52, "1 — init / systemd", size=12,
                    fill=COOL, stroke=NEG, sw=1.8, color=NEG, bold=True))
    p.append(fitbox(660, mid_y, 250, 52, "2 — kthreadd", size=12,
                    fill=GREENISH, stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    p.append(arrow(490, root_y + 52, 275, mid_y - 4, color=MUTED, sw=1.5))
    p.append(arrow(570, root_y + 52, 785, mid_y - 4, color=MUTED, sw=1.5))

    leaf_y = mid_y + 96
    left_leaves = ["sshd", "bash", "ваша\nпрограма"]
    right_leaves = ["[kswapd0]", "[kworker/1:2]", "[ksoftirqd/0]"]
    lw = 130
    for i, s in enumerate(left_leaves):
        x = 40 + i * (lw + 20)
        p.append(fitbox(x, leaf_y, lw, 50, s, size=11, fill=SOFT, stroke=NEG, sw=1.3, color=INK))
        p.append(line(275, mid_y + 52, x + lw / 2, leaf_y - 4, color=NEG, sw=1.2))
    for i, s in enumerate(right_leaves):
        x = 550 + i * (lw + 20)
        p.append(fitbox(x, leaf_y, lw, 50, s, size=11, fill=SOFT, stroke=FIELD, sw=1.3, color=INK))
        p.append(line(785, mid_y + 52, x + lw / 2, leaf_y - 4, color=FIELD, sw=1.2))

    p.append(text(W / 2, leaf_y + 84,
                  "потоки ядра не висять під init — тому вони не сироти, їх ніхто не перепідпорядковує "
                  "й вони не турбують wait() у першого процесу",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "kthread-birth.svg"), W, H, *p,
           title="Народження потоку ядра і два корені дерева задач")


# ── 3. Позичений адресний простір: скільки перемикань таблиць ─────────────────
def fig_lazy_tlb():
    W, H = 1040, 480
    p = []

    segs = [("A\nкористувач", COOL, NEG),
            ("K\nпотік ядра", GREENISH, FIELD),
            ("A\nкористувач", COOL, NEG),
            ("K\nпотік ядра", GREENISH, FIELD),
            ("B\nкористувач", WARM, POS)]
    x0, sw_, sh = 40, 190, 62
    bounds = [x0 + (i + 1) * sw_ for i in range(len(segs) - 1)]

    def timeline(y, title, marks, note, color):
        out = [fitbox(x0, y - 46, 960, 32, title, size=12,
                      fill="#ffffff", stroke=color, sw=1.5, color=color, bold=True)]
        for i, (label, fill, stroke) in enumerate(segs):
            out.append(fitbox(x0 + i * sw_, y, sw_ - 6, sh, label, size=11,
                              fill=fill, stroke=stroke, sw=1.5, color=INK))
        for bx, mark in zip(bounds, marks):
            if mark:
                out.append(line(bx - 3, y - 8, bx - 3, y + sh + 10, color=POS, sw=1.8, dash="4 4"))
                out.append(text(bx - 3, y + sh + 30, mark, size=10, color=POS, bold=True))
            else:
                out.append(text(bx - 3, y + sh + 30, "—", size=12, color=MUTED))
        out.append(text(x0 + 480, y + sh + 56, note, size=11, color=MUTED, italic=True))
        return out

    p += timeline(96, "Якби задача ядра мала власні таблиці сторінок",
                  ["запис CR3", "запис CR3", "запис CR3", "запис CR3"],
                  "чотири перемикання адресного простору на два виходи ядрової задачі на процесор",
                  POS)

    p += timeline(300, "Як є насправді: active_mm позичено в попередника",
                  [None, None, None, "запис CR3"],
                  "таблиці лишаються ті самі, поки не прийде задача з ВЛАСНИМ простором — тут це B",
                  FIELD)

    p.append(text(W / 2, 458,
                  "верхня половина ядрового простору однакова в усіх таблицях, тож задачі ядра байдуже, "
                  "чиї саме таблиці зараз стоять",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "lazy-tlb.svg"), W, H, *p,
           title="Позичений адресний простір: чому перемикати таблиці не треба")


# ── 4. Чотири епохи народження потоку ядра (вставка hist) ─────────────────────
def fig_eras():
    W, H = 1120, 350
    p = []

    p.append(fitbox(40, 30, 1040, 34, "Чим ядро народжувало власні потоки", size=13,
                    fill="#ffffff", stroke=MUTED, sw=1.4, color=MUTED, bold=True))

    cards = [
        ("2.4 — рання 2.6\n\nkernel_thread() з контексту\nвипадкового процесу,\nпотік чистить себе сам:\ndaemonize()", WARM, POS),
        ("2004 — kthread API\n\nkthread_create() лишає\nзаявку, а потік народжує\nчерга подій keventd", SOFT, MUTED),
        ("травень 2007 → 2.6.22\n\nпатч Еріка Бідермана:\nвиділений предок kthreadd,\nPID 2, батько PID 0", COOL, NEG),
        ("2010 → 2.6.36\n\nперебудова CMWQ\nТеджуна Хео: спільний пул\nkworker замість потоків\nна кожну чергу", GREENISH, FIELD),
    ]

    cw, gap, cy, ch = 250, 20, 88, 156
    for i, (txt, fill, stroke) in enumerate(cards):
        x = 40 + i * (cw + gap)
        p.append(fitbox(x, cy, cw, ch, txt, size=12, fill=fill, stroke=stroke, sw=1.7, color=INK))

    ly = cy + ch + 38
    p.append(line(40, ly, 1050, ly, color=MUTED, sw=1.6))
    p.append(arrow(1050, ly, 1080, ly, color=MUTED, sw=1.6))
    for i in range(4):
        p.append(circle(40 + i * (cw + gap) + cw / 2, ly, 6, fill="#ffffff", stroke=MUTED, sw=1.8))

    p.append(text(W / 2, ly + 44,
                  "щоразу та сама поправка: прибрати з народження потоку випадковість чужого оточення",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "kthread-eras.svg"), W, H, *p,
           title="Чотири епохи народження потоків ядра")


# ── 5. Робочі черги до і після CMWQ (вставка hist) ────────────────────────────
def fig_wq_pools():
    W, H = 1120, 440
    p = []

    p.append(fitbox(40, 30, 500, 40, "До 2.6.36: свій набір потоків\nна кожну чергу", size=12,
                    fill=WARM, stroke=POS, sw=1.7, color=POS, bold=True))
    p.append(fitbox(580, 30, 500, 40, "З 2.6.36: спільний пул\nна кожен процесор", size=12,
                    fill=GREENISH, stroke=FIELD, sw=1.7, color=FIELD, bold=True))

    queues = ["events", "kblockd", "xfslogd"]
    for i, q in enumerate(queues):
        ry = 100 + i * 60
        p.append(fitbox(40, ry, 116, 46, q, size=12, fill="#ffffff", stroke=MUTED, sw=1.4, color=INK))
        for j in range(4):
            p.append(fitbox(168 + j * 94, ry, 86, 46, "%s/%d" % (q[:3], j), size=11,
                            fill=WARM, stroke=POS, sw=1.3, color=INK))
    p.append(text(290, 300, "три черги × чотири процесори = дванадцять потоків,", size=12, color=MUTED, italic=True))
    p.append(text(290, 322, "і майже всі вони не роблять нічого", size=12, color=MUTED, italic=True))

    for i, q in enumerate(queues):
        x = 580 + i * 168
        p.append(fitbox(x, 100, 156, 46, q, size=12, fill="#ffffff", stroke=MUTED, sw=1.4, color=INK))
        p.append(arrow(x + 78, 148, x + 78, 176, color=MUTED, sw=1.5))
    p.append(fitbox(580, 180, 496, 46, "спільний список робіт цього процесора", size=12,
                    fill=SOFT, stroke=MUTED, sw=1.5, color=INK))
    p.append(arrow(828, 228, 828, 256, color=MUTED, sw=1.5))
    p.append(fitbox(580, 260, 496, 46, "kworker/0:0   kworker/0:1   kworker/0:2", size=12,
                    fill=GREENISH, stroke=FIELD, sw=1.7, color=INK))
    p.append(text(828, 330, "стільки виконавців, скільки треба просто зараз:", size=12, color=MUTED, italic=True))
    p.append(text(828, 352, "заснув один — прокидається наступний", size=12, color=MUTED, italic=True))

    p.append(text(W / 2, 400,
                  "черга лишилася назвою для набору правил, а виконує роботу спільний пул",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "wq-pools.svg"), W, H, *p,
           title="Робочі черги до і після перебудови CMWQ")


# ── 6. Рукостискання зупинки (вставка proj) ──────────────────────────────────
def fig_stop_handshake():
    W, H = 1080, 700
    p = []

    LX, LW = 40, 360
    RX, RW = 680, 360
    lcx, rcx = LX + LW / 2.0, RX + RW / 2.0
    midx = (LX + LW + RX) / 2.0

    p.append(fitbox(LX, 52, LW, 40, "rmmod → kdemo_exit()", size=13,
                    fill=COOL, stroke=NEG, sw=1.8, color=NEG, bold=True))
    p.append(fitbox(RX, 52, RW, 40, "потік kdemo/0", size=13,
                    fill=GREENISH, stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    def box(x, w, y, h, s, stroke):
        return fitbox(x, y, w, h, s, size=11, fill=SOFT, stroke=stroke, sw=1.5, color=INK)

    y1 = 108
    p.append(box(LX, LW, y1, 50, "kthread_stop(demo->task)", NEG))
    p.append(box(RX, RW, y1, 50, "спить у wait_event_interruptible()", FIELD))

    ay = y1 + 96
    p.append(text(midx, ay - 32, "виставляє KTHREAD_SHOULD_STOP", size=10, color=MUTED))
    p.append(text(midx, ay - 19, "і TIF_NOTIFY_SIGNAL, будить", size=10, color=MUTED))
    p.append(arrow(LX + LW + 6, ay, RX - 6, ay, color=MUTED, sw=1.7))

    y2 = ay + 24
    p.append(box(LX, LW, y2, 52, "wait_for_completion(&exited)\n— засинає сам", NEG))
    p.append(box(RX, RW, y2, 52, "прокидається; умову перевірено:\nkthread_should_stop() → true", FIELD))

    y3 = y2 + 52 + 34
    p.append(line(rcx, y2 + 52, rcx, y3 - 4, color=FIELD, sw=1.3, dash="3 4"))
    p.append(box(RX, RW, y3, 52, "break з циклу; kfree(scratch);\nпотік прибирає за собою", FIELD))

    y4 = y3 + 52 + 34
    p.append(line(rcx, y3 + 52, rcx, y4 - 4, color=FIELD, sw=1.3, dash="3 4"))
    p.append(box(RX, RW, y4, 52, "return 0 → kthread_exit(0)\ncomplete(&exited)", FIELD))

    by = y4 + 88
    p.append(text(midx, by - 26, "потік уже мертвий", size=10, color=MUTED))
    p.append(line(lcx, y2 + 52, lcx, by - 34, color=NEG, sw=1.3, dash="3 4"))
    p.append(arrow(RX - 6, by, LX + LW + 6, by, color=MUTED, sw=1.7))

    y5 = by + 22
    p.append(box(LX, LW, y5, 52, "kthread_stop() повертає 0", NEG))

    y6 = y5 + 52 + 30
    p.append(line(lcx, y5 + 52, lcx, y6 - 4, color=NEG, sw=1.3, dash="3 4"))
    p.append(box(LX, LW, y6, 52, "kfree(demo); далі ядро звільняє\nпам'ять модуля", NEG))

    p.append(text(W / 2.0, y6 + 78,
                  "поки kthread_stop() не повернувся, код потоку ще виконується — "
                  "а лежить він у пам'яті модуля",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "kthread-stop-handshake.svg"), W, H, *p,
           title="Зупинка потоку — рукостискання, а не наказ")


# ── 7. Умова засинання й чотири різні кінці (вставка proj) ───────────────────
def fig_sleep_condition():
    W, H = 540, 540
    p = []
    c1x, c1w = 40, 330
    c2x, c2w = 380, 250
    c3x, c3w = 640, 400
    W = 1080

    hy, hh = 50, 42
    p.append(fitbox(c1x, hy, c1w, hh, "Як написано засинання", size=12,
                    fill="#ffffff", stroke=MUTED, sw=1.4, color=MUTED, bold=True))
    p.append(fitbox(c2x, hy, c2w, hh, "Що бачить потік", size=12,
                    fill="#ffffff", stroke=MUTED, sw=1.4, color=MUTED, bold=True))
    p.append(fitbox(c3x, hy, c3w, hh, "Що з цього виходить", size=12,
                    fill="#ffffff", stroke=MUTED, sw=1.4, color=MUTED, bold=True))

    rows = [
        ("wait_event(wq, has_work)\nнепереривний сон",
         "розбудили, умова та сама",
         "заснув назад; і потік, і rmmod\nназавжди в стані D",
         POS, WARM),
        ("wait_event_interruptible(wq, has_work)\nядра до 6.0 включно",
         "розбудили, сигналу немає",
         "заснув назад; rmmod висить,\nчерез 120 с — «blocked for more than»",
         POS, WARM),
        ("wait_event_interruptible(wq, has_work)\nядра 6.1 і новіші",
         "kthread_stop() ставить\nTIF_NOTIFY_SIGNAL",
         "вихід із -ERESTARTSYS; якщо код\nповернення ігнорують — 100 % CPU",
         MUTED, SOFT),
        ("wait_event_interruptible(wq,\n    has_work || kthread_should_stop())",
         "прапорець перевіряє\nсама умова",
         "вийшов із циклу й повернувся —\nrmmod звільнився за мілісекунди",
         FIELD, GREENISH),
    ]

    y = hy + hh + 12
    rh = 72
    for c1, c2, c3, stroke, fill in rows:
        p.append(fitbox(c1x, y, c1w, rh, c1, size=11, fill=fill, stroke=stroke, sw=1.5, color=INK))
        p.append(fitbox(c2x, y, c2w, rh, c2, size=11, fill=SOFT, stroke=stroke, sw=1.3, color=INK))
        p.append(fitbox(c3x, y, c3w, rh, c3, size=11, fill=fill, stroke=stroke, sw=1.5, color=INK))
        y += rh + 10

    p.append(text(W / 2.0, y + 26,
                  "різниця в одному доданку умови — і в тому, чи вдасться колись вивантажити модуль",
                  size=12, color=MUTED, italic=True))

    H = y + 60
    render(os.path.join(OUT, "kthread-sleep-condition.svg"), W, H, *p,
           title="Що станеться з kthread_stop() залежно від умови засинання")


# ── 8. Анатомія назви потоку ядра (вставка api) ───────────────────────────────
def fig_name_anatomy():
    rows = [
        [("ksoftirqd", ["родина: доробляє", "відкладені softirq"]),
         ("/0", ["процесор № 0"])],
        [("kswapd", ["родина: витіснення", "сторінок"]),
         ("0", ["вузол NUMA № 0", "— риски немає"])],
        [("kworker", ["спільний", "робітник"]),
         ("/u16", ["набір без прив'язки", "до процесорів, № 16"]),
         (":3", ["робітник № 3", "у наборі"]),
         ("-writeback", ["остання робота —", "з черги writeback"])],
        [("jbd2", ["підсистема журналу"]),
         ("/sda2", ["пристрій із журналом"]),
         ("-8", ["inode журналу"])],
        [("irq", ["обробник, винесений", "у потік"]),
         ("/136", ["номер переривання"]),
         ("-iwlwifi", ["ім'я запиту: драйвер"])],
    ]

    NS, CS, PAD, GAP, BH, ROW = 17, 11, 14, 16, 42, 120

    widths = []
    for row in rows:
        ws = []
        for name, caps in row:
            tw = max(text_width(name, NS, True),
                     max(text_width(c, CS) for c in caps))
            ws.append(tw + 2 * PAD)
        widths.append(ws)

    maxrow = max(sum(ws) + GAP * (len(ws) - 1) for ws in widths)
    W = int(max(960, maxrow + 120))
    H = int(76 + len(rows) * ROW + 54)

    p = []
    for i, row in enumerate(rows):
        ws = widths[i]
        x = (W - (sum(ws) + GAP * (len(ws) - 1))) / 2.0
        y = 76 + i * ROW
        for j, (name, caps) in enumerate(row):
            if j == 0:
                fill, stroke, color = COOL, NEG, NEG
            elif name.startswith("-"):
                fill, stroke, color = GREENISH, FIELD, FIELD
            else:
                fill, stroke, color = SOFT, MUTED, INK
            p.append(fitbox(x, y, ws[j], BH, name, size=NS, pad=PAD,
                            fill=fill, stroke=stroke, sw=1.6, color=color, bold=True))
            p.append(mtext(x + ws[j] / 2.0, y + BH + 22, caps, size=CS, color=MUTED))
            x += ws[j] + GAP

    p.append(text(W / 2.0, H - 24,
                  "число після риски — процесор, набір або пристрій; "
                  "число впритул до назви — вузол пам'яті",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "kthread-name-anatomy.svg"), W, H, *p,
           title="Назва потоку ядра по частинах")


# ── 9. Дві назви однієї задачі (вставка api) ─────────────────────────────────
def fig_name_sources():
    W, H = 1040, 500
    p = []

    p.append(fitbox(340, 52, 360, 46, "задача ядра, народжена як\n\"kworker/u16:3\"", size=12,
                    fill="#ffffff", stroke=MUTED, sw=1.5, color=INK, bold=True))

    LX, RX, CW = 50, 550, 440
    p.append(arrow(430, 100, 300, 156, color=MUTED, sw=1.6))
    p.append(arrow(610, 100, 740, 156, color=MUTED, sw=1.6))

    p.append(fitbox(LX, 158, CW, 82,
                    "task_struct.comm[16]\n15 символів плюс нуль — усе,\nщо не влізло, відрізано",
                    size=12, fill=WARM, stroke=POS, sw=1.7, color=INK))
    p.append(fitbox(RX, 158, CW, 82,
                    "kthread->full_name, а для робітника —\nще й опис поточної роботи:\nдовжина не обмежена п'ятнадцятьма",
                    size=12, fill=GREENISH, stroke=FIELD, sw=1.7, color=INK))

    p.append(arrow(LX + CW / 2, 244, LX + CW / 2, 292, color=MUTED, sw=1.6))
    p.append(arrow(RX + CW / 2, 244, RX + CW / 2, 292, color=MUTED, sw=1.6))

    p.append(fitbox(LX, 294, CW, 108,
                    "події ftrace й perf (поле comm)\nдампи ядра: oops, sysrq-w\n\n"
                    "видно: kworker/u16:3",
                    size=12, fill=SOFT, stroke=POS, sw=1.4, color=INK))
    p.append(fitbox(RX, 294, CW, 108,
                    "/proc/PID/comm, /proc/PID/stat,\n/proc/PID/status → ps, top, htop\n\n"
                    "видно: kworker/u16:3-writeback",
                    size=12, fill=SOFT, stroke=FIELD, sw=1.4, color=INK))

    p.append(text(W / 2.0, 448,
                  "одна задача — дві назви: довшу /proc складає на льоту, тому в ps вона є, "
                  "а в трасуванні немає",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "kthread-name-sources.svg"), W, H, *p,
           title="Звідки інструменти беруть назву потоку ядра")


fig_anatomy()
fig_birth()
fig_lazy_tlb()
fig_eras()
fig_wq_pools()
fig_stop_handshake()
fig_sleep_condition()
fig_name_anatomy()
fig_name_sources()
print("ok")
