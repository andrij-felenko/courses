# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT   = "#f2f6fd"
GREENBG = "#eafaf0"
REDBG   = "#fdeeec"
GREYBG  = "#f1f2f4"


# ── 1. Хребет рішення: від звернення до вироку ──────────────────────────────
def fig_decision():
    W, H = 1080, 812
    p = []

    MX, MW = 110.0, 470.0          # головна колонка
    SX, SW = 650.0, 380.0          # бічні виходи
    mc = MX + MW / 2

    rows = [
        (60.0,  62.0, "програма читає або пише за адресою"),
        (170.0, 76.0, "MMU шукає трансляцію\nу таблицях сторінок"),
        (296.0, 84.0, "виняток сторінкового збою:\nадреса, код помилки, збережений IP"),
        (430.0, 80.0, "чи є область (VMA),\nяка покриває цю адресу?"),
        (560.0, 80.0, "чи дозволяє область\nсаме такий доступ?"),
        (690.0, 84.0, "збій, який можна полагодити:\nдати сторінку й повторити інструкцію"),
    ]
    fills = [GREYBG, SOFT, SOFT, SOFT, SOFT, GREENBG]
    strokes = [MUTED, NEG, POS, INK, INK, FIELD]

    for (y, h, s), f, st in zip(rows, fills, strokes):
        p.append(fitbox(MX, y, MW, h, s, size=16, fill=f, stroke=st, sw=1.8))

    # вертикальні стрілки між рядками
    for i in range(len(rows) - 1):
        y0 = rows[i][0] + rows[i][1]
        y1 = rows[i + 1][0]
        p.append(arrow(mc, y0, mc, y1, color=INK, sw=1.8))

    # підписи на вертикальних переходах (у проміжку, збоку від стрілки)
    def vlabel(i, s):
        y0 = rows[i][0] + rows[i][1]
        y1 = rows[i + 1][0]
        p.append(text(mc + 16, (y0 + y1) / 2 + 4, s, size=13, color=MUTED, anchor="start"))

    vlabel(1, "трансляції нема")
    vlabel(3, "так")
    vlabel(4, "так")

    # бічні виходи
    sides = [
        (1, 180.0, 56.0, "усе на місці:\nдоступ іде далі", "так", GREENBG, FIELD),
        (3, 442.0, 56.0, "адреса нічия — SIGSEGV\n(окремо: ріст стека вниз)", "ні", REDBG, POS),
        (4, 572.0, 56.0, "доступ заборонений — SIGSEGV", "ні", REDBG, POS),
    ]
    for i, y, h, s, lab, f, st in sides:
        p.append(fitbox(SX, y, SW, h, s, size=15, fill=f, stroke=st, sw=1.8))
        ym = rows[i][0] + rows[i][1] / 2
        p.append(arrow(MX + MW, ym, SX, ym, color=MUTED, sw=1.6))
        p.append(text((MX + MW + SX) / 2, ym - 12, lab, size=13, color=MUTED))

    return render(os.path.join(OUT, "fault-decision.svg"), W, H, *p)


# ── 2. Що саме стоїть за відсутньою сторінкою ───────────────────────────────
def fig_sources():
    W, H = 1300, 470
    p = []

    cols = [
        ("анонімна пам'ять,\nще не займана",
         "читання — спільна нульова\nсторінка на всіх;\nзапис — чиста сторінка\nз обнуленого запасу",
         "дрібний", "≈1 мкс", True),
        ("файл, сторінка вже\nв кеші сторінок",
         "дані в пам'яті є;\nлишилося вписати\nїх у таблицю сторінок",
         "дрібний", "≈1 мкс", True),
        ("сторінка є, але\nзапис заборонено",
         "спільну сторінку копіюють\nдля того, хто пише\n(копіювання при записі)",
         "дрібний", "≈1–3 мкс", True),
        ("файл, у кеші\nсторінок нема",
         "читання з носія;\nзадача спить,\nпоки дані не прийдуть",
         "великий", "десятки мкс — мс", False),
        ("сторінку витіснено\nу своп",
         "читання зі свопу;\nзадача спить,\nпоки дані не прийдуть",
         "великий", "десятки мкс — мс", False),
    ]

    x0, cw, gap = 30.0, 230.0, 22.0
    for i, (head, body, verdict, cost, minor) in enumerate(cols):
        x = x0 + i * (cw + gap)
        cx = x + cw / 2
        p.append(fitbox(x, 64, cw, 78, head, size=15, fill=SOFT, stroke=NEG, sw=1.8))
        p.append(arrow(cx, 142, cx, 172, color=MUTED, sw=1.5))
        p.append(fitbox(x, 172, cw, 118, body, size=13, fill=FILL, stroke=MUTED, sw=1.4))
        p.append(arrow(cx, 290, cx, 320, color=MUTED, sw=1.5))
        p.append(fitbox(x, 320, cw, 46, verdict + " збій", size=15, bold=True,
                        fill=GREENBG if minor else REDBG,
                        stroke=FIELD if minor else POS, sw=1.8))
        p.append(text(cx, 396, cost, size=13, color=MUTED))

    p.append(text(W / 2, 32, "звернення до сторінки, якої в таблиці нема (або нема потрібного права)",
                  size=16, bold=True))
    p.append(text(W / 2, 436, "межа проходить рівно там, де починається чекання на носій",
                  size=13, color=MUTED, italic=True))
    return render(os.path.join(OUT, "fault-sources.svg"), W, H, *p)


# ── 3. Ціна за порядками величини (логарифмічна шкала) ──────────────────────
def fig_cost():
    W, H = 1060, 420
    p = []

    X0, DEC = 380.0, 78.0          # початок смуг, пікселів на декаду
    items = [
        (["трансляція без збою", "(влучання в TLB)"], 0.0, "≈1 нс", MUTED, GREYBG),
        (["дрібний збій:", "сторінка вже в пам'яті"], 3.0, "≈1 мкс", FIELD, GREENBG),
        (["великий збій:", "читання з NVMe"], 5.0, "≈100 мкс", POS, REDBG),
        (["великий збій:", "читання з обертового диска"], 6.9, "≈8 мс", POS, REDBG),
    ]

    ys = [90.0, 152.0, 214.0, 276.0]
    BH = 36.0
    for (lab, dec, val, col, bg), y in zip(items, ys):
        p.append(mtext(360, y + 14, lab, size=13, color=INK, anchor="end", lh=1.35))
        w = max(5.0, dec * DEC)
        p.append(rect(X0, y, w, BH, fill=bg, stroke=col, sw=1.8, rx=4))
        p.append(text(1035, y + 24, val, size=14, color=col, bold=True, anchor="end"))

    # вісь декад
    AY = 348.0
    p.append(line(X0, AY, X0 + 7.2 * DEC, AY, color=MUTED, sw=1.4))
    for dec, name in [(0.0, "1 нс"), (3.0, "1 мкс"), (6.0, "1 мс")]:
        x = X0 + dec * DEC
        p.append(line(x, AY, x, AY + 8, color=MUTED, sw=1.4))
        p.append(text(x, AY + 26, name, size=13, color=MUTED))
    p.append(text(1035, AY + 52, "кожна поділка — у 10 разів", size=12,
                  color=MUTED, anchor="end"))

    p.append(text(W / 2, 40, "порядки величин: чотири розряди між дрібним і великим збоєм",
                  size=16, bold=True))
    return render(os.path.join(OUT, "fault-cost.svg"), W, H, *p)


# ── 4. Вставка proj: три способи заплатити за гігабайт ──────────────────────
def fig_lab_where():
    W, H = 1170, 410
    p = []

    LX = 276.0                       # права межа колонки підписів
    cols = [(296.0, 300.0), (616.0, 280.0), (916.0, 230.0)]
    heads = ["у момент запиту", "потім, під час роботи", "найгірший один дотик"]

    p.append(text(W / 2, 34, "Три способи заплатити за 1 ГіБ анонімної пам'яті",
                  size=17, bold=True))
    for (x, w), h in zip(cols, heads):
        p.append(text(x + w / 2, 86, h, size=14, bold=True, color=MUTED))

    rows = [
        (106.0,
         ["звичайний mmap", "(лінива обіцянка)"],
         ("0.011 мс\nнічого не зроблено", GREYBG, MUTED),
         ("196 мс, розсипані\nпо 262144 збоях", REDBG, POS),
         ("1832 мкс", REDBG, POS)),
        (186.0,
         ["mmap + MAP_POPULATE", "або MADV_POPULATE_WRITE"],
         ("191 мс одним шматком\nу самому виклику", SOFT, NEG),
         ("0 збоїв —\nаж поки не витіснить", SOFT, NEG),
         ("0.9 мкс", GREENBG, FIELD)),
        (266.0,
         ["mlockall(MCL_CURRENT|MCL_FUTURE)", "+ прохід записом на старті"],
         ("193 мс одним шматком\nна старті програми", SOFT, NEG),
         ("0 збоїв гарантовано:\nсторінки прибиті", GREENBG, FIELD),
         ("11 мкс — і це вже\nне збій, а планувальник", GREENBG, FIELD)),
    ]

    RH = 68.0
    for y, lab, c2, c3, c4 in rows:
        cy = y + RH / 2
        p.append(mtext(LX, cy - 13 * 1.3 / 2 + 13 * 0.35, lab,
                       size=13, color=INK, anchor="end", lh=1.3))
        for (x, w), (s, bg, st) in zip(cols, (c2, c3, c4)):
            p.append(fitbox(x, y, w, RH, s, size=13, fill=bg, stroke=st, sw=1.7))

    p.append(text(W / 2, 356,
                  "Сумарний час майже той самий у всіх трьох рядках — "
                  "різниться лише те, коли його платять і чи можна на це покластися.",
                  size=12, color=MUTED, italic=True))
    p.append(text(W / 2, 380,
                  "«Найгірший один дотик» — максимум із 16384 замірів по одній сторінці.",
                  size=12, color=MUTED, italic=True))
    return render(os.path.join(OUT, "fault-lab-where.svg"), W, H, *p)


# ── 5. Вставка proj: скільки збоїв дає обхід файлу ──────────────────────────
def fig_lab_counts():
    W, H = 1180, 470
    p = []

    X0, BARW, TOTAL = 350.0, 660.0, 65536.0
    px = BARW / TOTAL
    BH = 42.0

    p.append(text(W / 2, 34, "Скільки збоїв коштує обхід 65536 сторінок файлу",
                  size=17, bold=True))

    # легенда
    p.append(rect(350, 60, 16, 16, fill=GREENBG, stroke=FIELD, sw=1.6, rx=3))
    p.append(text(374, 73, "дрібні збої", size=13, color=MUTED, anchor="start"))
    p.append(rect(500, 60, 16, 16, fill=REDBG, stroke=POS, sw=1.6, rx=3))
    p.append(text(524, 73, "великі збої", size=13, color=MUTED, anchor="start"))

    rows = [
        (108.0, ["теплий кеш,", "послідовно"], 4096, 0, ["4096 дрібних"]),
        (182.0, ["холодний кеш,", "послідовно"], 2048, 2048, ["2048 + 2048"]),
        (256.0, ["холодний + MADV_WILLNEED,", "потім послідовно"], 4096, 0,
         ["4096 дрібних", "+ 218 мс прогрівання"]),
        (330.0, ["холодний + MADV_RANDOM,", "вроздріб"], 2170, 59214,
         ["2170 + 59214", "5.3 секунди чекання"]),
    ]

    for y, lab, minor, major, nums in rows:
        cy = y + BH / 2
        p.append(mtext(336, cy - 13 * 1.3 / 2 + 13 * 0.35, lab,
                       size=13, color=INK, anchor="end", lh=1.3))
        wmin = max(4.0, minor * px)
        p.append(rect(X0, y, wmin, BH, fill=GREENBG, stroke=FIELD, sw=1.6, rx=3))
        if major:
            p.append(rect(X0 + wmin, y, major * px, BH,
                          fill=REDBG, stroke=POS, sw=1.6, rx=3))
        p.append(mtext(1164, cy - (len(nums) - 1) * 13 * 1.3 / 2 + 13 * 0.35,
                       nums, size=13, color=MUTED, anchor="end", lh=1.3))

    p.append(text(W / 2, 396,
                  "4096 = 65536 ÷ 16: одним збоєм fault-around відображає "
                  "16 сусідніх сторінок (fault_around_bytes = 65536)",
                  size=12, color=MUTED, italic=True))
    p.append(text(W / 2, 420,
                  "2048 = 65536 ÷ 32: вікно випереджального читання — 128 КіБ, "
                  "тобто 32 сторінки на одне звернення до носія",
                  size=12, color=MUTED, italic=True))
    p.append(text(W / 2, 444,
                  "MADV_RANDOM вимикає випереджальне читання — і майже кожна "
                  "сторінка йде на носій окремо",
                  size=12, color=MUTED, italic=True))
    return render(os.path.join(OUT, "fault-lab-counts.svg"), W, H, *p)


# ── 6. Вставка api: карта лічильників за колом підсумовування ───────────────
def fig_counter_map():
    W, H = 1100, 604
    p = []

    LX, LW = 50.0, 250.0           # колонка «коло підсумовування»
    RX, RW = 330.0, 700.0          # колонка джерел
    BH, GAP = 100.0, 20.0

    bands = [
        ("потік\n(один task)", SOFT, NEG, [
            "task/<tid>/stat\nполя 10 і 12",
            "getrusage\n(RUSAGE_THREAD)",
            "perf stat -t <tid>",
        ]),
        ("процес\n(усі його потоки)", GREENBG, FIELD, [
            "getrusage\n(RUSAGE_SELF)",
            "/proc/<pid>/stat\nполя 10–13",
            "ps -o min_flt,maj_flt",
            "/usr/bin/time -v",
        ]),
        ("контрольна група\n(cgroup v2)", SOFT, MUTED, [
            "memory.stat:\npgfault · pgmajfault",
            "memory.pressure:\nчастка часу в чеканні",
        ]),
        ("уся машина", REDBG, POS, [
            "/proc/vmstat:\npgfault · pgmajfault",
            "sar -B:\nfault/s · majflt/s",
            "/proc/pressure/memory",
        ]),
    ]

    y = 82.0
    for lab, bg, st, cells in bands:
        p.append(fitbox(LX, y, LW, BH, lab, size=16, fill=bg, stroke=st, sw=1.8))
        n = len(cells)
        cw = (RW - (n - 1) * 14.0) / n
        for i, s in enumerate(cells):
            p.append(fitbox(RX + i * (cw + 14.0), y + 12.0, cw, BH - 24.0,
                            s, size=13, fill=FILL, stroke=MUTED, sw=1.4))
        y += BH + GAP

    p.append(text(W / 2, 42, "ті самі дві події, чотири різні кола підсумовування",
                  size=17, bold=True))
    p.append(text(W / 2, 586,
                  "Ліворуч — чиє це число; праворуч — звідки його брати. "
                  "Усі лічильники наростні від старту й ніколи не скидаються.",
                  size=12, color=MUTED, italic=True))
    return render(os.path.join(OUT, "fault-counter-map.svg"), W, H, *p)


# ── 7. Вставка api: коли діє кожен важіль ──────────────────────────────────
def fig_levers():
    W, H = 1120, 580
    p = []

    LX, LW = 44.0, 300.0
    RX, RW = 372.0, 704.0
    RH, GAP = 108.0, 18.0

    rows = [
        ("у мить створення\nвідображення — mmap(2)", GREENBG, FIELD,
         "MAP_POPULATE — заповнити таблиці одразу\n"
         "MAP_LOCKED — прибити, але без гарантії\n"
         "MAP_NORESERVE — не резервувати своп\n"
         "MAP_HUGETLB — сторінки по 2 МіБ"),
        ("будь-коли потім,\nна готовій ділянці — madvise(2)", SOFT, NEG,
         "MADV_WILLNEED — тягнути в кеш сторінок наперед\n"
         "MADV_POPULATE_READ / _WRITE — заповнити таблиці зараз\n"
         "MADV_SEQUENTIAL / _RANDOM — режим випереджання\n"
         "MADV_DONTNEED — навпаки, скинути (збої повернуться)"),
        ("назавжди, поки процес\nживий — mlock(2)", SOFT, MUTED,
         "mlock / mlock2(…, MLOCK_ONFAULT)\n"
         "mlockall(MCL_CURRENT | MCL_FUTURE | MCL_ONFAULT)\n"
         "стеля — RLIMIT_MEMLOCK, обхід — CAP_IPC_LOCK"),
        ("на всю машину,\nповз процес — sysfs і sysctl", REDBG, POS,
         "/sys/kernel/debug/fault_around_bytes — 65536\n"
         "/sys/kernel/mm/transparent_hugepage/enabled\n"
         "/sys/block/<dev>/queue/read_ahead_kb — 128\n"
         "vm.max_map_count · vm.mmap_min_addr · vm.swappiness"),
    ]

    y = 78.0
    for lab, bg, st, body in rows:
        p.append(fitbox(LX, y, LW, RH, lab, size=15, fill=bg, stroke=st, sw=1.8))
        p.append(fitbox(RX, y, RW, RH, body, size=15, fill=FILL, stroke=MUTED, sw=1.4))
        y += RH + GAP

    p.append(text(W / 2, 42, "важелі впорядковані не за викликом, а за миттю, коли вони діють",
                  size=17, bold=True))
    p.append(text(W / 2, 560,
                  "Чим нижче рядок, тим ширше коло впливу: від однієї ділянки "
                  "до всіх процесів машини.",
                  size=12, color=MUTED, italic=True))
    return render(os.path.join(OUT, "fault-levers.svg"), W, H, *p)


if __name__ == "__main__":
    print(fig_decision())
    print(fig_sources())
    print(fig_cost())
    print(fig_lab_where())
    print(fig_lab_counts())
    print(fig_counter_map())
    print(fig_levers())
