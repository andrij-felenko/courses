# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
WARM = "#fff6e5"
RED = "#fdecea"
GREY = "#eceff1"


# ── 1. Два набори квитків: звідки береться полиця ───────────────────────────
def fig_two_tag_pools():
    W, H = 1460, 900
    p = []

    p.append(line(W / 2, 50, W / 2, H - 40, color=MUTED, sw=1.2, dash="7 7"))

    def submitters(cx, y):
        h = 0
        for dx in (-230, 0, 230):
            f, w, h = textbox(cx + dx, y, "процес", size=13, pad=12,
                              fill=BLUE, stroke=LINE)
            p.append(f)
        return h

    def slots(cx, y, n, w_one, label, fill):
        """Ряд однакових комірок — модель скінченної таблиці."""
        total = n * w_one
        x0 = cx - total / 2
        for i in range(n):
            p.append(rect(x0 + i * w_one, y, w_one - 6, 44, fill=fill,
                          stroke=LINE, sw=1.2, rx=4))
        p.append(text(cx, y + 76, label, size=13, color=MUTED))
        return 44

    # ══ ліворуч: none ══════════════════════════════════════════════════════
    lx = 365
    p.append(text(lx, 84, "З «none»: квиток один", size=17, bold=True))

    y_src = 160
    h_src = submitters(lx, y_src)

    y_tag = 305
    f, w_t, h_t = textbox(lx, y_tag,
                          ["квиток пристрою", "стільки, скільки слотів у носія"],
                          size=13, pad=15, fill=RED, stroke=POS, sw=2)
    p.append(f)
    for dx in (-230, 0, 230):
        p.append(arrow(lx + dx, y_src + h_src / 2 + 6,
                       lx + dx * 0.28, y_tag - h_t / 2 - 6))

    y_hw = 450
    slots(lx, y_hw, 6, 62, "апаратна черга носія", GREY)
    p.append(arrow(lx, y_tag + h_t / 2 + 6, lx, y_hw - 8))

    p.append(fitbox(lx - 290, 600, 580, 96,
                    ["запит не з'являється, поки в носія немає",
                     "вільного слота — тож ніде й нічого",
                     "накопичувати: порядок = порядок надходження"],
                    size=14, fill=BG, stroke=MUTED, sw=1.2))

    # ══ праворуч: планувальник ════════════════════════════════════════════
    rx = 1095
    p.append(text(rx, 84, "З планувальником: квитків два набори",
                  size=17, bold=True))

    h_src2 = submitters(rx, y_src)

    y_k = 290
    f, w_k, h_k = textbox(rx, y_k,
                          ["квиток ядра", "їх навмисно більше, ніж слотів"],
                          size=13, pad=15, fill=GREEN, stroke=FIELD, sw=2)
    p.append(f)
    for dx in (-230, 0, 230):
        p.append(arrow(rx + dx, y_src + h_src2 / 2 + 6,
                       rx + dx * 0.28, y_k - h_k / 2 - 6))

    y_shelf = 412
    slots(rx, y_shelf, 9, 62, "полиця: подано, але ще не відправлено", WARM)
    p.append(arrow(rx, y_k + h_k / 2 + 6, rx, y_shelf - 8))

    y_tag2 = 560
    f, w_t2, h_t2 = textbox(rx, y_tag2,
                            ["квиток пристрою: видають лише тому,",
                             "кого планувальник вибрав"],
                            size=13, pad=15, fill=RED, stroke=POS, sw=2)
    p.append(f)
    p.append(arrow(rx, y_shelf + 52, rx, y_tag2 - h_t2 / 2 - 6))

    y_hw2 = 662
    slots(rx, y_hw2, 6, 62, "апаратна черга носія", GREY)
    p.append(arrow(rx, y_tag2 + h_t2 / 2 + 6, rx, y_hw2 - 8))

    p.append(fitbox(rx - 290, 782, 580, 70,
                    ["на полиці лежить кілька сотень запитів одночасно —",
                     "тільки тому питання «чий перший» має сенс"],
                    size=14, fill=BG, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'two-tag-pools.svg'), W, H, *p,
           title="Полиця виникає з різниці між двома наборами квитків")


# ── 2. mq-deadline: ті самі запити в двох порядках ──────────────────────────
def fig_deadline_two_orders():
    W, H = 1420, 820
    p = []

    lx, rx = 360, 1035
    p.append(text(lx, 88, "Порядок за номером сектора", size=17, bold=True))
    p.append(text(rx, 88, "Порядок за строком", size=17, bold=True))

    # (сектор, тип, залишок строку в мс) — той самий набір у двох порядках
    by_sector = [
        ("сектор 1 040 · читання", "лишилось 180 мс", BLUE),
        ("сектор 1 216 · читання", "лишилось 340 мс", BLUE),
        ("сектор 1 288 · запис", "лишилось 4 700 мс", GREEN),
        ("сектор 9 502 · читання", "лишилось 60 мс", BLUE),
        ("сектор 74 810 · читання", "строк сплив", RED),
    ]
    by_deadline = [
        ("сектор 74 810 · читання", "строк сплив", RED),
        ("сектор 9 502 · читання", "лишилось 60 мс", BLUE),
        ("сектор 1 040 · читання", "лишилось 180 мс", BLUE),
        ("сектор 1 216 · читання", "лишилось 340 мс", BLUE),
        ("сектор 1 288 · запис", "лишилось 4 700 мс", GREEN),
    ]

    bw, bh, gap = 480, 78, 22
    y0 = 132

    def column(cx, rows):
        ys = []
        for i, (a, b, col) in enumerate(rows):
            y = y0 + i * (bh + gap)
            stroke = POS if col is RED else LINE
            sw = 2.4 if col is RED else 1.5
            p.append(fitbox(cx - bw / 2, y, bw, bh, [a, b],
                            size=14, fill=col, stroke=stroke, sw=sw))
            ys.append(y)
        return ys

    ys_l = column(lx, by_sector)
    ys_r = column(rx, by_deadline)

    # підпис вертикального напрямку кожного стовпця
    p.append(text(lx, y0 - 18, "звідси беруть, поки жоден строк не сплив",
                  size=13, color=MUTED))
    p.append(text(rx, y0 - 18, "сюди дивляться перед кожною пачкою",
                  size=13, color=MUTED))

    # прострочений запит вискакує з правого стовпця
    y_out = ys_r[0] + bh / 2
    p.append(arrow(rx - bw / 2 - 10, y_out, lx + bw / 2 + 14, y_out, color=POS, sw=2.4))
    p.append(text((lx + rx) / 2, y_out - 20, "прострочений іде поза чергою",
                  size=14, color=POS, bold=True))

    p.append(fitbox(W / 2 - 470, 660, 940, 108,
                    ["Кожен запит стоїть в обох списках одночасно.",
                     "Сортування дає вигоду носієві, строк дає стелю очікування,",
                     "а пачка з шістнадцяти запитів окупає перехід між далекими ділянками."],
                    size=15, fill=BG, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'deadline-two-orders.svg'), W, H, *p,
           title="Два списки, між якими планувальник перемикається")


# ── 3. Рівний час не означає рівної роботи ──────────────────────────────────
def fig_time_vs_sectors():
    W, H = 1360, 660
    p = []

    x0 = 130
    slice_w = 620          # 100 мс у масштабі
    bh = 76

    p.append(text(x0, 82, "Однакова скибка часу — 100 мс на обертовому диску",
                  size=17, anchor="start", bold=True))

    def row(y, name, work_w, work_label, note, col, stroke):
        p.append(text(x0 - 24, y + bh / 2 + 5, name, size=14,
                      anchor="end", bold=True))
        p.append(rect(x0, y, slice_w, bh, fill=GREY, stroke=MUTED, sw=1.4))
        p.append(rect(x0, y, max(work_w, 7), bh, fill=col, stroke=stroke, sw=2.2))
        if work_w > 150:
            p.append(text(x0 + work_w / 2, y + bh / 2 + 5, work_label,
                          size=15, bold=True))
        else:
            p.append(text(x0 + work_w + 18, y + bh / 2 + 5, work_label,
                          size=15, anchor="start", bold=True, color=POS))
        p.append(text(x0 + slice_w + 40, y + bh / 2 + 5, note,
                      size=14, anchor="start", color=MUTED))

    # 150 МБ/с суцільно → 15 МБ за 100 мс; 4 КіБ вроздріб при 12.2 мс на звертання
    row(150, "послідовний читач", 590, "15 МБ",
        "передавання майже без пауз", GREEN, FIELD)
    row(300, "випадковий читач", 8, "32 КіБ",
        "вісім звертань, решта — переїзди головки", RED, POS)

    p.append(text(x0, 268, "корисна робота всередині скибки", size=13,
                  anchor="start", color=MUTED))

    p.append(fitbox(x0 - 24, 440, 1150, 130,
                    ["Різниця — у чотириста з гаком разів, і вона не властивість процесу,",
                     "а властивість того, куди він звертається. Тому частку носія міряють",
                     "не мілісекундами, а секторами: бюджет у секторах обіцяє обсяг роботи,",
                     "а скибка часу обіцяє лише доступ до пристрою."],
                    size=15, fill=BG, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'time-vs-sectors.svg'), W, H, *p,
           title="Чому частку носія рахують у секторах, а не в часі")


# ── 4. Kyber: замкнена петля на власному вимірюванні ────────────────────────
def fig_kyber_loop():
    W, H = 1300, 860
    p = []

    cx = 760
    rows = [
        (120, ["запити класу: читання · синхронний запис · решта"], BLUE),
        (270, ["запас квитків класу:", "не більше N команд цього класу в польоті"], WARM),
        (420, ["пристрій виконує те, що впустили"], GREY),
        (570, ["вимір: скільки запит пролежав у ядрі",
               "й скільки його виконував сам пристрій"], GREEN),
        (720, ["порівняти з ціллю: 2 мс на читання, 10 мс на запис"], BLUE),
    ]

    hs, ws = [], []
    for y, lines, col in rows:
        f, w, h = textbox(cx, y, lines, size=14, pad=16, fill=col, stroke=LINE)
        p.append(f)
        hs.append(h)
        ws.append(w)

    for i in range(len(rows) - 1):
        y1 = rows[i][0] + hs[i] / 2 + 6
        y2 = rows[i + 1][0] - hs[i + 1] / 2 - 6
        p.append(arrow(cx, y1, cx, y2))

    # зворотний зв'язок: ліворуч угору, до запасу квитків
    back_x = 150
    y_from = rows[-1][0]
    y_to = rows[1][0]
    p.append(line(cx - ws[-1] / 2 - 10, y_from, back_x, y_from, color=POS, sw=2.2))
    p.append(line(back_x, y_from, back_x, y_to, color=POS, sw=2.2))
    p.append(arrow(back_x, y_to, cx - ws[1] / 2 - 10, y_to, color=POS, sw=2.2))

    f, w_n, h_n = textbox(295, 470,
                          ["вище цілі →", "квитків менше",
                           "нижче цілі →", "квитків більше"],
                          size=13, pad=13, fill=RED, stroke=POS, sw=1.6)
    p.append(f)

    p.append(minus(295, 470 - h_n / 2 - 20))
    p.append(plus(295, 470 + h_n / 2 + 20))

    p.append(fitbox(cx - 470, 800, 940, 46,
                    ["Керована величина — глибина черги в пристрої, а не порядок запитів."],
                    size=15, fill=BG, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'kyber-loop.svg'), W, H, *p,
           title="Kyber підбирає глибину черги за власним виміром затримки")


# ── 5. Що саме охоплює годинник у замірі (вставка proj) ─────────────────────
def fig_measure_path():
    W, H = 1500, 1020
    p = []

    RX, WX = 420, 1120          # колонки: читач ліворуч, писар праворуч

    f, w, h = textbox(RX, 95, ["читач", "pread 4 КіБ, O_DIRECT",
                               "один запит у польоті"],
                      size=13, pad=15, fill=BLUE, stroke=POS, sw=2)
    p.append(f)
    f, w, h = textbox(WX, 95, ["писар", "1 МіБ у кеш поспіль",
                               "звичайний буферизований запис"],
                      size=13, pad=15, fill=WARM, stroke=LINE)
    p.append(f)

    # шлях писаря: через кеш і крізь гальмо фонового запису
    f, w, h = textbox(WX, 255, ["сторінковий кеш", "запис підтверджено вже тут"],
                      size=13, pad=13, fill=GREY, stroke=LINE)
    p.append(f)
    p.append(arrow(WX, 145, WX, 255 - h / 2 - 6))
    y_wbt = 410
    f, w, h2 = textbox(WX, y_wbt, ["гальмо фонового запису", "wbt_lat_usec"],
                       size=13, pad=13, fill=RED, stroke=POS, sw=1.8)
    p.append(f)
    p.append(arrow(WX, 255 + h / 2 + 6, WX, y_wbt - h2 / 2 - 6))

    # шлях читача: повз кеш, прямо на блоковий рівень
    f, w, h = textbox(215, 255, ["O_DIRECT", "минає кеш"],
                      size=12, pad=11, fill=BG, stroke=MUTED, sw=1.2)
    p.append(f)

    y_shelf = 505
    p.append(fitbox(240, y_shelf, 1040, 78,
                    ["полиця блокового рівня: до nr_requests запитів чекають вибору"],
                    size=15, fill=FILL, stroke=LINE))
    p.append(arrow(RX, 145, RX, y_shelf - 6))
    p.append(arrow(WX, y_wbt + h2 / 2 + 6, WX, y_shelf - 6))

    CX = 760
    f, w, h = textbox(CX, 660, ["планувальник",
                                "none · mq-deadline · bfq · kyber"],
                      size=14, pad=15, fill=GREEN, stroke=POS, sw=2)
    p.append(f)
    p.append(arrow(CX, y_shelf + 78 + 4, CX, 660 - h / 2 - 6))
    y_sched_bot = 660 + h / 2

    f, w, h = textbox(CX, 790, "теги пристрою: скільки команд у польоті одночасно",
                      size=13, pad=13, fill=GREY, stroke=LINE)
    p.append(f)
    p.append(arrow(CX, y_sched_bot + 6, CX, 790 - h / 2 - 6))

    f, w, h3 = textbox(CX, 900, "носій: власна внутрішня черга, власний порядок",
                       size=13, pad=13, fill=BLUE, stroke=LINE)
    p.append(f)
    p.append(arrow(CX, 790 + h / 2 + 6, CX, 900 - h3 / 2 - 6))

    # дужка виміру ліворуч
    bx, y_top, y_bot = 130, 150, 900 + h3 / 2
    p.append(line(bx, y_top, bx, y_bot, color=POS, sw=2))
    p.append(line(bx - 16, y_top, bx + 16, y_top, color=POS, sw=2))
    p.append(line(bx - 16, y_bot, bx + 16, y_bot, color=POS, sw=2))
    p.append(text(bx, y_top - 16, "clock_gettime", size=11, color=MUTED))
    p.append(text(bx, y_bot + 26, "clock_gettime", size=11, color=MUTED))

    p.append(fitbox(240, 955, 1040, 50,
                    ["Годинник охоплює весь шлях: полиця, планувальник, черга носія."],
                    size=15, fill=BG, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'measure-path.svg'), W, H, *p,
           title="Що саме потрапляє в поміряний час одного читання")


# ── Карта sysfs: де лежать ручки планувальника ──────────────────────────────
def fig_knobs_map():
    """Дерево sysfs: що спільне для всіх планувальників, а що змінюється разом
    із вибором. Окремим рядком — ваги cgroup, які живуть поза /sys/block."""
    W, H = 1560, 1120
    p = []

    X_ROOT, X_L2, X_L3, X_L4 = 200, 570, 905, 1315

    def box(cx, cy, lines, **kw):
        f, w, h = textbox(cx, cy, lines, **kw)
        p.append(f)
        return w, h

    def connect(x1, y1, w1, x2, y2, w2):
        p.append(arrow(x1 + w1 / 2 + 8, y1, x2 - w2 / 2 - 8, y2))

    # ── рівень 1: сам пристрій ─────────────────────────────────────────────
    w_root, _ = box(X_ROOT, 430, "/sys/block/nvme0n1/", size=14, pad=13,
                    bold=True, fill=GREY, stroke=LINE)

    # ── рівень 2: queue/ і mq/ ─────────────────────────────────────────────
    w_q, _ = box(X_L2, 300, "queue/", size=14, pad=13, bold=True,
                 fill=BLUE, stroke=LINE)
    w_mq, _ = box(X_L2, 880, "mq/0/ … mq/N−1/", size=14, pad=13, bold=True,
                  fill=BLUE, stroke=LINE)
    connect(X_ROOT, 430, w_root, X_L2, 300, w_q)
    connect(X_ROOT, 430, w_root, X_L2, 880, w_mq)

    # ── рівень 3: вибір, сталі атрибути, змінний каталог ────────────────────
    w_sch, _ = box(X_L3, 110, "scheduler", size=14, pad=13, bold=True,
                   fill=RED, stroke=POS, sw=2)
    w_att, _ = box(X_L3, 275, ["nr_requests", "rotational",
                               "wbt_lat_usec", "read_ahead_kb"],
                   size=13, pad=12, fill=GREY, stroke=LINE)
    w_ios, _ = box(X_L3, 520, "iosched/", size=14, pad=13, bold=True,
                   fill=GREEN, stroke=POS, sw=2)
    connect(X_L2, 300, w_q, X_L3, 110, w_sch)
    connect(X_L2, 300, w_q, X_L3, 275, w_att)
    connect(X_L2, 300, w_q, X_L3, 520, w_ios)

    # ── рівень 4: що саме лежить усередині ─────────────────────────────────
    w_rd, _ = box(X_L4, 110, ["читання: none [mq-deadline] kyber bfq",
                              "запис: echo bfq > scheduler"],
                  size=13, pad=13, fill=BG, stroke=MUTED, sw=1.2)
    connect(X_L3, 110, w_sch, X_L4, 110, w_rd)

    box(X_L4, 205, "перемикання скидає nr_requests", size=13, pad=12,
        fill=RED, stroke=POS, sw=1.6)
    box(X_L4, 300, "однакові за будь-якого планувальника", size=13, pad=12,
        fill=BG, stroke=MUTED, sw=1.2)

    w_dl, _ = box(X_L4, 470, ["mq-deadline", "read_expire · write_expire",
                              "fifo_batch · writes_starved",
                              "front_merges · prio_aging_expire"],
                  size=13, pad=13, fill=WARM, stroke=LINE)
    w_bq, _ = box(X_L4, 645, ["bfq", "slice_idle · slice_idle_us",
                              "low_latency · strict_guarantees",
                              "max_budget · timeout_sync",
                              "back_seek_max · back_seek_penalty"],
                  size=13, pad=13, fill=WARM, stroke=LINE)
    w_ky, _ = box(X_L4, 785, ["kyber", "read_lat_nsec · write_lat_nsec"],
                  size=13, pad=13, fill=WARM, stroke=LINE)
    connect(X_L3, 520, w_ios, X_L4, 470, w_dl)
    connect(X_L3, 520, w_ios, X_L4, 645, w_bq)
    connect(X_L3, 520, w_ios, X_L4, 785, w_ky)

    box(X_L4, 875, "під none каталогу iosched/ немає", size=13, pad=12,
        fill=BG, stroke=MUTED, sw=1.2)

    # ── скільки апаратних черг ─────────────────────────────────────────────
    w_n, _ = box(1010, 985, ["N — кількість апаратних черг носія",
                             "окремого файлу nr_hw_queues немає",
                             "mq/<n>/nr_tags — глибина однієї черги"],
                 size=13, pad=13, fill=GREY, stroke=LINE)
    connect(X_L2, 880, w_mq, 1010, 985, w_n)

    # ── ваги cgroup: інше дерево ───────────────────────────────────────────
    w_cg, _ = box(255, 1075, "/sys/fs/cgroup/<група>/", size=14, pad=13,
                  bold=True, fill=GREY, stroke=LINE)
    w_wt, _ = box(650, 1075, "io.bfq.weight", size=13, pad=13,
                  fill=GREEN, stroke=POS, sw=1.8)
    connect(255, 1075, w_cg, 650, 1075, w_wt)
    w_nt, _ = box(1050, 1075, "лише для bfq · 1..1000 · типово 100",
                  size=13, pad=12, fill=BG, stroke=MUTED, sw=1.2)
    connect(650, 1075, w_wt, 1050, 1075, w_nt)

    render(os.path.join(IMG, 'scheduler-knobs-map.svg'), W, H, *p,
           title="Де в sysfs лежать ручки планувальника блокового вводу-виводу")


# ── Придатність: чому самого лише «найменшого строку» замало ────────────────
def fig_wf2q_eligibility():
    """Одна мить вибору в B-WF2Q+. Найменший строк — у черги C, але її
    віртуальний початок уже правіше за системний час, тож вона поза грою."""
    W, H = 1320, 640
    p = []

    X0, X1 = 300, 1200
    VMAX = 11.0
    sx = lambda v: X0 + v / VMAX * (X1 - X0)

    AY = 500
    p.append(line(X0 - 40, AY, X1 + 24, AY, color=INK, sw=1.6))
    for v in (0, 2, 4, 6, 8, 10):
        p.append(line(sx(v), AY - 6, sx(v), AY + 6, color=MUTED, sw=1.2))
        p.append(text(sx(v), AY + 30, str(v), size=13, color=MUTED))
    p.append(text((X0 + X1) / 2, AY + 66,
                  "віртуальний час: видані сектори на одиницю ваги",
                  size=14, color=MUTED))

    # курсор системного віртуального часу
    XV = sx(0.64)
    p.append(line(XV, 110, XV, AY + 10, color=POS, sw=2.2, dash="7 6"))
    p.append(text(XV, 96, "V = 0.64", size=14, bold=True, color=POS))

    rows = [
        ("C", 1.28, 2.56, "бюджет 256 · вага 200", RED),
        ("A", 0.00, 5.12, "бюджет 512 · вага 100", GREEN),
        ("B", 0.00, 5.12, "бюджет 512 · вага 100", GREEN),
    ]
    ys = (170, 290, 400)
    for (name, st, fi, sub, fill), y in zip(rows, ys):
        p.append(rect(sx(st), y - 26, sx(fi) - sx(st), 52,
                      fill=fill, stroke=LINE, sw=1.6, rx=6))
        p.append(text((sx(st) + sx(fi)) / 2, y + 6, name, size=18, bold=True))
        p.append(text(X0 - 60, y - 4, "черга " + name, size=14, bold=True,
                      anchor="end"))
        p.append(text(X0 - 60, y + 18, sub, size=12, color=MUTED, anchor="end"))
        p.append(text(sx(st), y - 40, "start %.2f" % st, size=12, color=MUTED))
        p.append(text(sx(fi), y - 40, "finish %.2f" % fi, size=12, color=MUTED))

    p.append(fitbox(760, 148, 500, 62,
                    ["start 1.28 > V — черга вже взяла наперед,",
                     "у цьому раунді її не розглядають"],
                    size=13, fill=RED, stroke=POS, sw=1.6))
    p.append(fitbox(760, 330, 500, 62,
                    ["start 0 ≤ V — обидві придатні;",
                     "серед них беруть найменший finish"],
                    size=13, fill=GREEN, stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, 'wf2q-eligibility.svg'), W, H, *p,
           title="Найменший строк — у C, але черга дістається A або B")


# ── Відхилення від ідеалу: що саме додає перевірка придатності ──────────────
def fig_wf2q_deviation():
    """Скільки секторів черга C має понад свою ідеальну частку в кожній точці.
    Ті самі ваги й бюджети; різниться лише правило вибору."""
    W, H = 1340, 700
    p = []

    X0, X1 = 190, 1200
    SMAX = 4096.0
    DTOP, DBOT = 448.0, -256.0
    YT, YB = 150, 560
    sx = lambda s: X0 + s / SMAX * (X1 - X0)
    sy = lambda d: YT + (DTOP - d) / (DTOP - DBOT) * (YB - YT)

    # осі
    p.append(line(X0, YT - 10, X0, YB + 10, color=INK, sw=1.6))
    p.append(line(X0 - 10, sy(0), X1 + 16, sy(0), color=INK, sw=1.6))
    p.append(line(X0, YB, X1, YB, color=MUTED, sw=1.2))
    for s in (1024, 2048, 3072, 4096):
        p.append(line(sx(s), YB - 5, sx(s), YB + 7, color=MUTED, sw=1.2))
    p.append(text((X0 + X1) / 2, YB + 66, "усього видано секторів",
                  size=14, color=MUTED))
    for s in (1024, 2048, 3072, 4096):
        p.append(text(sx(s), YB + 34, str(s), size=12, color=MUTED))

    for d, lab in ((384, "+384"), (128, "+128"), (0, "0"),
                   (-128, "−128"), (-256, "−256")):
        p.append(text(X0 - 22, sy(d) + 5, lab, size=12, color=MUTED,
                      anchor="end"))
    p.append(text(X0, YT - 34, "відхилення черги C від ідеалу, сектори",
                  size=13, color=MUTED, anchor="start"))

    for d in (128, -128):
        p.append(line(X0, sy(d), X1, sy(d), color=FIELD, sw=1.4, dash="6 6"))

    def curve(pts, color, sw=2.6):
        d = " ".join("%.1f,%.1f" % (sx(s), sy(v)) for s, v in pts)
        return ('<polyline points="%s" fill="none" stroke="%s" '
                'stroke-width="%.1f"/>' % (d, color, sw))

    wfq = [(0, 0), (768, 384), (1792, -128), (2816, 384), (3840, -128),
           (4096, 0)]
    wf2q = [(0, 0), (256, 128), (768, -128), (1280, 128), (1792, -128),
            (2304, 128), (2816, -128), (3328, 128), (3840, -128), (4096, 0)]
    p.append(curve(wfq, POS))
    p.append(curve(wf2q, NEG))

    p.append(fitbox(620, 84, 580, 54,
                    ["коридор ±128 = B_C·(1 − w_C/W) — стеля, яку дає придатність"],
                    size=13, fill=GREEN, stroke=FIELD, sw=1.4))

    p.append(fitbox(200, 648, 450, 52,
                    ["найменший строк без придатності (WFQ)"],
                    size=13, fill=RED, stroke=POS, sw=1.8))
    p.append(fitbox(700, 648, 450, 52,
                    ["придатність, тоді строк (B-WF2Q+)"],
                    size=13, fill=BLUE, stroke=NEG, sw=1.8))

    render(os.path.join(IMG, 'wf2q-deviation.svg'), W, H, *p,
           title="Ті самі ваги й бюджети, два правила вибору")


if __name__ == '__main__':
    fig_two_tag_pools()
    fig_deadline_two_orders()
    fig_time_vs_sectors()
    fig_kyber_loop()
    fig_measure_path()
    fig_knobs_map()
    fig_wf2q_eligibility()
    fig_wf2q_deviation()
    print("ok")
