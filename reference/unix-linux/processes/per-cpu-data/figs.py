# -*- coding: utf-8 -*-
"""Фігури до теми «Дані свого ядра процесора: змінні per-CPU і local_lock»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_BG = "#e6f5ec"
RED_BG = "#fdecea"
BLUE_BG = "#eaf0fd"
GREY_BG = "#eef0f3"
WARM_BG = "#fff4e0"


# ── 1. Креслення й копії ────────────────────────────────────────────────────
def fig_layout():
    W, H = 1300, 700
    P = []

    P.append(text(W / 2, 34, "Секція .data..percpu — це план, а не дані", size=17, bold=True))

    # креслення
    tx, ty, tw = 60, 96, 250
    P.append(text(tx + tw / 2, ty - 16, "креслення блоку", size=14, bold=True, color=MUTED))
    slots = [
        ("rx_packets", "зсув 0x40"),
        ("depot", "зсув 0x80"),
        ("softnet_data", "зсув 0xc0"),
    ]
    P.append(rect(tx, ty, tw, 300, fill=GREY_BG, stroke=MUTED, sw=1.5))
    sy = ty + 30
    for name, off in slots:
        P.append(fitbox(tx + 16, sy, tw - 32, 62, name + "\n" + off, size=13, fill=BG, stroke=MUTED))
        sy += 82
    P.append(mtext(tx + tw / 2, ty + 330,
                   ["у пам'ять як дані", "не потрапляє ніколи"],
                   size=12.5, color=MUTED, lh=1.4))

    # копії
    cx0, cw, gap = 420, 260, 40
    labels = [
        ("копія ядра 0", "вузол NUMA 0", GREEN_BG, FIELD),
        ("копія ядра 1", "вузол NUMA 0", GREEN_BG, FIELD),
        ("копія ядра 2", "вузол NUMA 1", BLUE_BG, NEG),
    ]
    for i, (title_, node, bg, stroke) in enumerate(labels):
        x = cx0 + i * (cw + gap)
        P.append(text(x + cw / 2, ty - 16, title_, size=14, bold=True, color=stroke))
        P.append(rect(x, ty, cw, 300, fill=bg, stroke=stroke, sw=2))
        yy = ty + 30
        for name, _off in slots:
            P.append(fitbox(x + 16, yy, cw - 32, 62, name, size=13, fill=BG, stroke=stroke))
            yy += 82
        P.append(text(x + cw / 2, ty + 330, node, size=12.5, color=MUTED))
        P.append(text(x + cw / 2, ty + 356, "__per_cpu_offset[%d]" % i, size=12.5, color=MUTED))
        # стрілка від креслення до копії — вище рамок, щоб не різати написи
        P.append(arrow(tx + tw + 12, ty + 12, x + cw / 2 - 4, ty - 34, color=MUTED, sw=1.2))

    P.append(text(W / 2, 600,
                  "адреса = зсув у кресленні  +  __per_cpu_offset[номер ядра процесора]",
                  size=15, bold=True))
    P.append(text(W / 2, 640,
                  "на x86-64 доданок для свого ядра лежить у базі сегмента %gs — його додає сама інструкція",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "percpu-layout.svg"), W, H, *P)


# ── 2. Два супротивники ─────────────────────────────────────────────────────
def fig_enemies():
    W, H = 1340, 700
    P = []

    P.append(text(W / 2, 34, "Кого лишилося боятися у власній копії", size=17, bold=True))

    # ── ліва панель: міграція ──
    lx, lw = 50, 600
    P.append(rect(lx, 66, lw, 470, fill=BG, stroke=MUTED, sw=1.5))
    P.append(text(lx + lw / 2, 96, "Ворог перший: міграція", size=15, bold=True, color=NEG))

    P.append(fitbox(lx + 30, 120, 250, 54, "ядро процесора 3", size=13,
                    fill=BLUE_BG, stroke=NEG, bold=True))
    P.append(fitbox(lx + 320, 120, 250, 54, "ядро процесора 7", size=13,
                    fill=BLUE_BG, stroke=NEG, bold=True))

    steps_l = [
        (lx + 30, 200, "p = this_cpu_ptr(&depot)\nвказівник веде в копію 3"),
        (lx + 320, 292, "задачу перенесено сюди\nпланувальником"),
        (lx + 320, 384, "p->count++\nзапис іде в копію 3"),
    ]
    for x, y, s in steps_l:
        P.append(fitbox(x, y, 250, 66, s, size=12.5, fill=GREY_BG, stroke=MUTED))
    P.append(arrow(lx + 155, 270, lx + 430, 286, color=MUTED, sw=1.4))
    P.append(arrow(lx + 445, 360, lx + 445, 378, color=MUTED, sw=1.4))

    P.append(fitbox(lx + 30, 470, 540, 48,
                    "запис коректний — копія чужа: одне ядро недорахує, друге перерахує",
                    size=13, fill=RED_BG, stroke=POS, sw=2))

    # ── права панель: переривання ──
    rx_, rw = 690, 600
    P.append(rect(rx_, 66, rw, 470, fill=BG, stroke=MUTED, sw=1.5))
    P.append(text(rx_ + rw / 2, 96, "Ворог другий: переривання", size=15, bold=True, color=POS))

    P.append(fitbox(rx_ + 30, 120, 540, 54, "одне ядро процесора, дві течії коду", size=13,
                    fill=WARM_BG, stroke="#b8860b", bold=True))

    steps_r = [
        (rx_ + 30, 200, "код задачі читає\ncounter = 41"),
        (rx_ + 320, 292, "обробник переривання:\ncounter = 42"),
        (rx_ + 30, 384, "код задачі записує 42,\nобчислене з 41"),
    ]
    for x, y, s in steps_r:
        P.append(fitbox(x, y, 250, 66, s, size=12.5, fill=GREY_BG, stroke=MUTED))
    P.append(arrow(rx_ + 155, 270, rx_ + 430, 286, color=MUTED, sw=1.4))
    P.append(arrow(rx_ + 430, 360, rx_ + 160, 378, color=MUTED, sw=1.4))

    P.append(fitbox(rx_ + 30, 470, 540, 48,
                    "приріст обробника зник — жодного іншого процесора тут немає",
                    size=13, fill=RED_BG, stroke=POS, sw=2))

    # ── чим закривають ──
    P.append(fitbox(50, 578, 600, 82,
                    "закриває заборона витіснення:\npreempt_disable(), get_cpu_ptr(), local_lock()",
                    size=13, fill=GREEN_BG, stroke=FIELD, sw=2))
    P.append(fitbox(690, 578, 600, 82,
                    "закриває заборона переривань або неподільність:\nlocal_irq_save(), this_cpu_inc() однією інструкцією",
                    size=13, fill=GREEN_BG, stroke=FIELD, sw=2))

    render(os.path.join(OUT, "two-enemies.svg"), W, H, *P)


# ── 3. Два обличчя local_lock ───────────────────────────────────────────────
def fig_two_faces():
    W, H = 1260, 720
    P = []

    P.append(text(W / 2, 34, "Один вихідний текст — дві реалізації", size=17, bold=True))

    P.append(fitbox(400, 62, 460, 58, "local_lock(&depot.lock);", size=15,
                    fill=GREY_BG, stroke=INK, sw=2, bold=True))

    P.append(arrow(560, 126, 320, 176, color=MUTED, sw=1.6))
    P.append(arrow(700, 126, 940, 176, color=MUTED, sw=1.6))

    # ліва панель
    lx, lw = 60, 520
    P.append(rect(lx, 186, lw, 300, fill=GREEN_BG, stroke=FIELD, sw=2))
    P.append(text(lx + lw / 2, 218, "звичайне ядро", size=15, bold=True, color=FIELD))
    left_lines = [
        "розгортається в preempt_disable()",
        "витіснення заборонене",
        "переривання дозволені",
        "ділянка неперервна на цьому ядрі",
        "коштує нуль додаткових інструкцій",
    ]
    yy = 258
    for s in left_lines:
        P.append(fitbox(lx + 24, yy, lw - 48, 38, s, size=12.5, fill=BG, stroke=MUTED))
        yy += 46

    # права панель
    rx_, rw = 680, 520
    P.append(rect(rx_, 186, rw, 300, fill=BLUE_BG, stroke=NEG, sw=2))
    P.append(text(rx_ + rw / 2, 218, "ядро з PREEMPT_RT", size=15, bold=True, color=NEG))
    right_lines = [
        "розгортається в спін-замок per-CPU",
        "витіснення дозволене",
        "переривання не вимикаються",
        "задачу прибито до свого ядра",
        "виключення дає сам замок",
    ]
    yy = 258
    for s in right_lines:
        P.append(fitbox(rx_ + 24, yy, rw - 48, 38, s, size=12.5, fill=BG, stroke=MUTED))
        yy += 46

    # розділення двох сенсів
    P.append(text(W / 2, 546, "два сенси, склеєні в local_irq_save, розходяться",
                  size=14, bold=True, color=MUTED))

    P.append(fitbox(120, 574, 460, 56, "«лишити мене на цьому ядрі»\n→ прибиття задачі",
                    size=13, fill=WARM_BG, stroke="#b8860b", sw=2))
    P.append(fitbox(680, 574, 460, 56, "«не пускати сюди інших»\n→ власне замок",
                    size=13, fill=WARM_BG, stroke="#b8860b", sw=2))

    P.append(text(W / 2, 672,
                  "розділити їх стало можливо лише тому, що код тепер називає свій захист",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "local-lock-two-faces.svg"), W, H, *P)


# ── 4. Хронологія механізму (вставка hist) ─────────────────────────────────
def fig_timeline():
    W, H = 1180, 760
    P = []

    P.append(text(W / 2, 38, "Двадцять років: як per-CPU ставав першокласним", size=17, bold=True))

    ax = 250                      # вісь
    y0, pitch = 96, 82
    rows = [
        ("2002", "ядро 2.5", GREEN_BG, FIELD,
         "Расті Расселл: DEFINE_PER_CPU — статичні змінні у власній секції"),
        ("2002", "ядро 2.5", GREY_BG, MUTED,
         "kmalloc_percpu: динаміка окремим механізмом, масив вказівників"),
        ("2009", "ядро 2.6.30", BLUE_BG, NEG,
         "Теджун Хео: спільний динамічний розподілювач для статики й динаміки"),
        ("2009", "ядро 2.6.33", BLUE_BG, NEG,
         "Крістоф Ламетер: this_cpu_* — на x86 одна інструкція з префіксом %gs"),
        ("2010", "ядро 2.6.38", BLUE_BG, NEG,
         "масове переведення лічильників: vmstat, розподілювач сторінок"),
        ("2014", "ядро 3.19", RED_BG, POS,
         "__get_cpu_var зникає з дерева — лишається тільки this_cpu_ptr"),
        ("2020", "ядро 5.8", WARM_BG, "#b8860b",
         "local_lock приходить з дерева PREEMPT_RT: у захисту з'являється ім'я"),
        ("2021", "ядро 5.15", WARM_BG, "#b8860b",
         "на PREEMPT_RT той самий local_lock стає спін-замком per-CPU"),
    ]

    P.append(line(ax, y0 - 30, ax, y0 + (len(rows) - 1) * pitch + 40, color=MUTED, sw=2))

    for i, (year, ver, bg, stroke, txt) in enumerate(rows):
        cy = y0 + i * pitch
        P.append(text(ax - 130, cy - 4, year, size=15, bold=True, color=stroke))
        P.append(text(ax - 130, cy + 18, ver, size=13, color=MUTED))
        P.append(circle(ax, cy + 4, 9, fill=bg, stroke=stroke, sw=2.5))
        P.append(fitbox(ax + 34, cy - 24, 830, 56, txt, size=13.5, fill=bg, stroke=stroke, sw=1.8))

    P.append(text(W / 2, H - 44,
                  "спершу дані стали дешевими, потім дешевими стали дії над ними, "
                  "і аж наприкінці — захист дістав ім'я",
                  size=13.5, color=MUTED))

    render(os.path.join(OUT, "percpu-timeline.svg"), W, H, *P)


# ── 5. Чотири входи в ту саму копію (вставка proj) ─────────────────────────
def fig_four_doors():
    W, H = 1360, 800
    P = []

    P.append(text(W / 2, 34, "Одна копія — чотири входи, чотири різні правила", size=17, bold=True))

    cx, cw = 480, 400
    P.append(rect(cx, 150, cw, 430, fill=GREY_BG, stroke=INK, sw=2))
    P.append(text(cx + cw / 2, 184, "копія ядра процесора N", size=15, bold=True))

    P.append(fitbox(cx + 30, 210, cw - 60, 130,
                    "лічильники\nevents · bytes · misses · refills",
                    size=13, fill=GREEN_BG, stroke=FIELD, sw=2))
    P.append(fitbox(cx + 30, 370, cw - 60, 170,
                    "запас об'єктів\nlocal_lock_t + список + count",
                    size=13, fill=WARM_BG, stroke="#b8860b", sw=2))

    lx, lw = 40, 380
    left = [
        (170, 130, "таймер, контекст softirq\n\nthis_cpu_inc(events)\nзамка немає — одна інструкція"),
        (390, 150, "поповнення запасу, контекст задачі\n\nlocal_lock_irqsave(&depot.lock)\nсуперник — softirq на цьому ж ядрі"),
    ]
    for y, h, s in left:
        P.append(fitbox(lx, y, lw, h, s, size=12.5, fill=BG, stroke=MUTED, sw=1.5))
        P.append(arrow(lx + lw + 10, y + h / 2, cx - 10, y + h / 2, color=MUTED, sw=1.6))

    rx_, rw = 940, 380
    right = [
        (170, 130, "читання з будь-якого ядра\n\nper_cpu_ptr(&cnt, cpu)\nзамка немає — сума приблизна"),
        (390, 150, "гак cpuhp на ядрі, що гасне\n\nlocal_lock_irqsave + злив у спільне\nінакше пам'ять лишиться замкненою"),
    ]
    for y, h, s in right:
        P.append(fitbox(rx_, y, rw, h, s, size=12.5, fill=BG, stroke=MUTED, sw=1.5))
        P.append(arrow(cx + cw + 10, y + h / 2, rx_ - 10, y + h / 2, color=MUTED, sw=1.6))

    P.append(fitbox(200, 630, 960, 62,
                    "правило вибирає не тип даних, а контекст того, хто заходить:\nхто мій суперник на ЦЬОМУ ядрі й чи маю я право заснути",
                    size=13.5, fill=BLUE_BG, stroke=NEG, sw=2))

    P.append(text(W / 2, 740,
                  "жоден із чотирьох входів не боронить від інших ядер процесора — і не мусить",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "four-doors.svg"), W, H, *P)


# ── 6. Замір: як росте пропускна здатність (вставка proj) ──────────────────
def fig_scaling():
    import math

    W, H = 1270, 700
    P = []

    xs = [150, 320, 490, 660, 830, 1000]
    cpus = ["1", "2", "4", "8", "16", "32"]
    atomic = [170, 48, 30, 22, 16, 12]
    percpu = [1800, 3600, 7200, 14400, 28800, 57000]

    Y0, Y1 = 580.0, 110.0          # 10 млн/с … 100 000 млн/с
    span = (Y0 - Y1) / 4.0

    def ypos(v):
        return Y0 - (math.log10(v) - 1.0) * span

    P.append(text(W / 2, 34, "Той самий підрахунок тих самих подій", size=17, bold=True))
    P.append(text(126, 74, "сукупно, млн приростів за секунду — шкала логарифмічна",
                  size=12.5, color=MUTED, anchor="start"))

    for v, lbl in ((10, "10"), (100, "100"), (1000, "1 000"),
                   (10000, "10 000"), (100000, "100 000")):
        y = ypos(v)
        P.append(line(140, y, 1010, y, color="#dcdfe4", sw=1))
        P.append(text(128, y + 4, lbl, size=12, color=MUTED, anchor="end"))

    P.append(line(140, Y0, 1010, Y0, color=MUTED, sw=1.5))
    for x, lbl in zip(xs, cpus):
        P.append(text(x, Y0 + 28, lbl, size=13, color=INK))
    P.append(text(575, Y0 + 60, "скільки ядер процесора рахує водночас",
                  size=13, color=MUTED))

    for vals, color in ((atomic, POS), (percpu, FIELD)):
        pts = [(x, ypos(v)) for x, v in zip(xs, vals)]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            P.append(line(x1, y1, x2, y2, color=color, sw=2.6))
        for x, y in pts:
            P.append(circle(x, y, 5, fill=color, stroke=color, sw=1))

    P.append(text(1020, ypos(57000) + 4, "57 000", size=12.5,
                  color=FIELD, anchor="start", bold=True))
    P.append(text(1020, ypos(12) + 4, "12", size=12.5,
                  color=POS, anchor="start", bold=True))

    P.append(rect(152, 112, 410, 88, fill=BG, stroke=MUTED, sw=1.2))
    P.append(line(172, 140, 202, 140, color=FIELD, sw=3))
    P.append(text(214, 144, "this_cpu_inc — рядок у кожного свій", size=12.5,
                  color=INK, anchor="start"))
    P.append(line(172, 174, 202, 174, color=POS, sw=3))
    P.append(text(214, 178, "atomic64_inc — рядок один на всіх", size=12.5,
                  color=INK, anchor="start"))

    P.append(fitbox(380, 336, 520, 74,
                    "одна крива — пряма через початок координат,\nдруга падає тим швидше, чим більше охочих",
                    size=13, fill=BG, stroke=MUTED, sw=1.5))

    P.append(text(W / 2, 674,
                  "цифри з однієї машини; сталі залежать від заліза, форма кривих — ні",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "percpu-scaling.svg"), W, H, *P)


# ── 7. Вікна вразливості чотирьох форм доступу (вставка api) ───────────────
def fig_access_windows():
    W, H = 1340, 690
    P = []

    P.append(text(W / 2, 34, "Вікна, у які встигає влізти суперник", size=17, bold=True))
    P.append(text(W / 2, 60, "чотири форми доступу до тієї самої змінної per-CPU",
                  size=13, color=MUTED))

    S1 = (350, 210)   # обчислити адресу
    WA = (560, 130)   # вікно міграції
    S2 = (690, 170)   # прочитати
    WB = (860, 130)   # вікно переривання
    S3 = (990, 300)   # змінити й записати

    P.append(text(WA[0] + WA[1] / 2, 90, "вікно міграції", size=12.5, bold=True, color=MUTED))
    P.append(text(WB[0] + WB[1] / 2, 90, "вікно переривання", size=12.5, bold=True, color=MUTED))

    BH = 74
    rows = [
        ("this_cpu_inc(c);", "single", None, None),
        ("p = raw_cpu_ptr(&c);\np->x++;", "split", "open", "open"),
        ("p = get_cpu_ptr(&c);\np->x++;\nput_cpu_ptr(&c);", "split", "shut", "open"),
        ("local_lock_irqsave(&s.l, f);\ns.x++;\nlocal_unlock_irqrestore(&s.l, f);",
         "split", "shut", "shut"),
    ]

    y = 108
    for label, kind, wa, wb in rows:
        P.append(fitbox(40, y, 296, BH, label, size=12, fill=BG, stroke=INK, sw=1.5))

        if kind == "single":
            P.append(fitbox(S1[0], y, S3[0] + S3[1] - S1[0], BH,
                            "одна інструкція: база %gs і приріст разом — розірвати нема де",
                            size=13, fill=GREEN_BG, stroke=FIELD, sw=2))
        else:
            P.append(fitbox(S1[0], y, S1[1], BH, "обчислити\nадресу",
                            size=12.5, fill=GREY_BG, stroke=MUTED))
            P.append(fitbox(S2[0], y, S2[1], BH, "прочитати",
                            size=12.5, fill=GREY_BG, stroke=MUTED))
            P.append(fitbox(S3[0], y, S3[1], BH, "змінити й записати",
                            size=12.5, fill=GREY_BG, stroke=MUTED))
            for (wx, ww), state in ((WA, wa), (WB, wb)):
                if state == "open":
                    P.append(fitbox(wx, y, ww, BH, "відкрите",
                                    size=12.5, fill=RED_BG, stroke=POS, sw=2))
                else:
                    P.append(fitbox(wx, y, ww, BH, "закрито",
                                    size=12.5, fill=GREEN_BG, stroke=FIELD, sw=2))
        y += 130

    ly = 596
    P.append(rect(350, ly, 26, 26, fill=RED_BG, stroke=POS, sw=2))
    P.append(text(392, ly + 18, "суперник встигає влізти", size=13,
                  color=MUTED, anchor="start"))
    P.append(rect(760, ly, 26, 26, fill=GREEN_BG, stroke=FIELD, sw=2))
    P.append(text(802, ly + 18, "проміжок заклеєно", size=13,
                  color=MUTED, anchor="start"))

    P.append(text(W / 2, 668,
                  "чужого процесора не закриває жодна з чотирьох форм — для нього потрібен звичайний спін-замок",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "access-windows.svg"), W, H, *P)


if __name__ == "__main__":
    fig_layout()
    fig_enemies()
    fig_two_faces()
    fig_timeline()
    fig_four_doors()
    fig_scaling()
    fig_access_windows()
    print("ok")
