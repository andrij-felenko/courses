# -*- coding: utf-8 -*-
"""Фігури до теми «Облік процесорного часу: як ядро набирає user і sys»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

USER_FILL = "#f4f6f8"
SYS_FILL = "#b8c6dd"


# ── 1. Тикова вибірка проти справжнього чергування режимів ──────────────────
def fig_tick_sampling():
    W, H = 940, 350
    x0, x1 = 120.0, 700.0
    span = x1 - x0
    ytop, hstrip = 78.0, 34.0

    # (ширина, режим): 's' — код ядра, 'u' — власний код
    segs = [(60, 'u'), (30, 's'), (45, 'u'), (50, 's'), (80, 'u'), (25, 's'),
            (50, 'u'), (45, 's'), (70, 'u'), (35, 's'), (90, 'u')]
    total = float(sum(w for w, _ in segs))
    sys_true = sum(w for w, m in segs if m == 's') / total

    frags = []
    # смуга справжнього чергування
    cur = 0.0
    bounds = []
    for w, m in segs:
        frags.append(rect(x0 + cur, ytop, w - 1.0, hstrip,
                          fill=(SYS_FILL if m == 's' else USER_FILL), sw=1.2, rx=3))
        bounds.append((cur, cur + w, m))
        cur += w
    frags.append(text(110, ytop + hstrip / 2 + 5, "задача", size=13, anchor="end"))

    # легенда
    frags.append(rect(730, 72, 18, 14, fill=USER_FILL, sw=1.2, rx=3))
    frags.append(text(756, 84, "власний код (user)", size=12, anchor="start"))
    frags.append(rect(730, 98, 18, 14, fill=SYS_FILL, sw=1.2, rx=3))
    frags.append(text(756, 110, "код ядра (sys)", size=12, anchor="start"))

    # тики
    nticks = 8
    step = span / nticks
    hits_sys = 0
    for i in range(nticks):
        off = step * (i + 0.5)
        mode = 'u'
        for a, b, m in bounds:
            if a <= off < b:
                mode = m
                break
        if mode == 's':
            hits_sys += 1
        tx = x0 + off
        frags.append(arrow(tx, 149, tx, 115))
        body, _, _ = textbox(tx, 168, "S" if mode == 's' else "U", size=13, pad=9,
                             fill=(SYS_FILL if mode == 's' else USER_FILL))
        frags.append(body)
    frags.append(text(110, 173, "тики", size=13, anchor="end"))

    sys_tick = hits_sys / float(nticks)

    # смуги порівняння
    def bar(y, frac_sys, label):
        wu = span * (1 - frac_sys)
        frags.append(fitbox(x0, y, wu - 1.0, 28,
                            "user %d%%" % round((1 - frac_sys) * 100),
                            size=13, fill=USER_FILL))
        frags.append(fitbox(x0 + wu, y, span - wu, 28,
                            "sys %d%%" % round(frac_sys * 100),
                            size=13, fill=SYS_FILL))
        frags.append(text(110, y + 19, label, size=13, anchor="end"))

    bar(230, sys_true, "насправді")
    bar(282, sys_tick, "нарахували")

    frags.append(mtext(716, 240, ["вісім тиків", "поділили час", "інакше, ніж він",
                                  "поділився насправді"], size=12, anchor="start"))

    render(os.path.join(IMG, "tick-sampling.svg"), W, H, *frags,
           title="Тик бачить одну точку, а записує цілий проміжок")


# ── 2. Масштабування: пропорція від тиків, довжина від планувальника ────────
def fig_cputime_adjust():
    W, H = 900, 380
    frags = []

    # верх ліворуч: тикові лічильники
    lx0, lw = 60.0, 340.0
    p_sys = 1.80 / 11.00
    frags.append(text(lx0, 72, "тикові лічильники", size=13, anchor="start", bold=True))
    frags.append(fitbox(lx0, 88, lw * (1 - p_sys) - 1.0, 32, "utime 9.20 с",
                        size=13, fill=USER_FILL))
    frags.append(fitbox(lx0 + lw * (1 - p_sys), 88, lw * p_sys, 32, "1.80",
                        size=12, fill=SYS_FILL))
    frags.append(text(lx0, 142, "сума 11.00 с — стороння", size=12,
                      anchor="start", color=MUTED))

    # верх праворуч: планувальник
    rx0, rw = 500.0, 340.0
    frags.append(text(rx0, 72, "лічильник планувальника", size=13,
                      anchor="start", bold=True))
    frags.append(fitbox(rx0, 88, rw, 32, "sum_exec_runtime = 12.000 с",
                        size=13, fill="#eaf3ec"))
    frags.append(text(rx0, 142, "точно, але без поділу на режими", size=12,
                      anchor="start", color=MUTED))

    # стрілки сходяться
    frags.append(arrow(250, 158, 400, 218))
    frags.append(text(214, 196, "пропорція", size=13, anchor="end"))
    frags.append(arrow(650, 158, 500, 218))
    frags.append(text(686, 196, "довжина", size=13, anchor="start"))

    # результат
    bx0, bw = 180.0, 540.0
    q_sys = 1.9636 / 12.000
    frags.append(fitbox(bx0, 236, bw * (1 - q_sys) - 1.0, 34, "utime 10.036 с",
                        size=13, fill=USER_FILL))
    frags.append(fitbox(bx0 + bw * (1 - q_sys), 236, bw * q_sys, 34, "1.964",
                        size=12, fill=SYS_FILL))
    frags.append(text(bx0, 228, "те, що бачить програма", size=13,
                      anchor="start", bold=True))

    frags.append(mtext(450, 312, ["stime′ = rtime · stime / (stime + utime)",
                                  "utime′ = rtime − stime′"], size=13))

    render(os.path.join(IMG, "cputime-adjust.svg"), W, H, *frags,
           title="Довжину беруть у планувальника, пропорцію — у тиків")


# ── 3. Порядок, у якому тик приписують категорії ────────────────────────────
def fig_tick_demux():
    W, H = 900, 510
    frags = []

    b, w, h = textbox(450, 70, "Тик — 1/HZ секунди", size=13, bold=True)
    frags.append(b)
    frags.append(arrow(450, 70 + h / 2 + 2, 450, 135 - 17))

    b2, w2, h2 = textbox(450, 135, "відняти вже виміряне: steal, hardirq, softirq",
                         size=13)
    frags.append(b2)
    frags.append(arrow(450, 135 + h2 / 2 + 2, 280, 200 - 17))

    rows = [
        (200, "це потік ksoftirqd?", "у графу softirq"),
        (262, "перерваний код був у режимі користувача?", "utime задачі"),
        (324, "це задача-простій?", "idle або iowait"),
        (386, "задача виконує гостя?", "gtime і разом з тим utime"),
        (448, "жодна з умов не збіглася", "stime задачі"),
    ]

    prev_bottom = None
    for i, (y, cond, dest) in enumerate(rows):
        cb, cw, ch = textbox(280, y, cond, size=13)
        db, dw, dh = textbox(700, y, dest, size=13, fill="#eef2f6")
        frags.append(cb)
        frags.append(db)
        ax0 = 280 + cw / 2 + 6
        ax1 = 700 - dw / 2 - 6
        frags.append(arrow(ax0, y, ax1, y))
        if i < len(rows) - 1:
            frags.append(text((ax0 + ax1) / 2, y - 13, "так", size=11, color=MUTED))
        if prev_bottom is not None:
            frags.append(arrow(280, prev_bottom + 2, 280, y - ch / 2 - 2))
        prev_bottom = y + ch / 2

    render(os.path.join(IMG, "tick-demux.svg"), W, H, *frags,
           title="Один тик іде цілком в одну категорію")


# ── 4. Атака «cheat»: робота між тиками (вставка hist-tick-accounting) ─────
def fig_cheat_tick():
    W, H = 940, 380
    x0 = 130.0
    tick_w = 250.0        # ширина одного тику на полотні
    n = 3
    ystrip = 118.0
    hstrip = 38.0
    frac = 0.80           # частка тику, яку забирає нахаба

    CHEAT_FILL = "#b8c6dd"
    HONEST_FILL = "#f4f6f8"

    frags = []

    # межі тиків: стрілки згори
    for i in range(n + 1):
        x = x0 + i * tick_w
        frags.append(line(x, ystrip - 46, x, ystrip + hstrip + 16,
                          color=MUTED, sw=1.2, dash="4,4"))
        frags.append(arrow(x, ystrip - 46, x, ystrip - 8))
        frags.append(text(x, ystrip - 54, "тик", size=12, color=MUTED))

    # смуга «хто виконується насправді»
    for i in range(n):
        xa = x0 + i * tick_w
        wc = tick_w * frac
        frags.append(rect(xa + 1, ystrip, wc - 2, hstrip, fill=CHEAT_FILL, sw=1.2, rx=3))
        frags.append(text(xa + wc / 2, ystrip + hstrip / 2 + 5, "нахаба рахує", size=12))
        frags.append(rect(xa + wc + 1, ystrip, tick_w - wc - 2, hstrip,
                          fill=HONEST_FILL, sw=1.2, rx=3))
        # позначка сну під самим тиком
        frags.append(text(xa + wc + (tick_w - wc) / 2, ystrip + hstrip / 2 + 5,
                          "спить", size=11, color=MUTED))
    frags.append(text(x0 - 14, ystrip + hstrip / 2 + 5, "процесор", size=13, anchor="end"))

    # смуга «кому записано тик»
    ybill = ystrip + hstrip + 74
    for i in range(n):
        xa = x0 + i * tick_w
        frags.append(rect(xa + 1, ybill, tick_w - 2, hstrip, fill=HONEST_FILL, sw=1.2, rx=3))
        frags.append(text(xa + tick_w / 2, ybill + hstrip / 2 + 5,
                          "весь тик — чесному", size=12))
    frags.append(text(x0 - 14, ybill + hstrip / 2 + 5, "рахунок", size=13, anchor="end"))

    # підсумок
    ysum = ybill + hstrip + 52
    b1, w1, _ = textbox(x0 + tick_w * 0.75, ysum,
                        "спожито: 80 % процесора", size=13, fill=CHEAT_FILL)
    b2, w2, _ = textbox(x0 + tick_w * 2.25, ysum,
                        "показано в top: 0 %", size=13)
    frags.append(b1)
    frags.append(b2)
    frags.append(arrow(x0 + tick_w * 0.75 + w1 / 2 + 8, ysum,
                       x0 + tick_w * 2.25 - w2 / 2 - 8, ysum))

    render(os.path.join(IMG, "cheat-tick.svg"), W, H, *frags,
           title="Робота між тиками: спожити процесор і не потрапити в облік")


# ── 5. Розкид оцінки залежно від частки p (вставка math-sampling-error) ─────
def fig_spread_vs_p():
    import math

    W, H = 960, 452
    frags = []

    def panel(x0, x1, ybase, ytop, ymax, fn, pmark, ylabels, header, sub):
        out = []
        # рамка полотна графіка
        out.append(rect(x0, ytop, x1 - x0, ybase - ytop,
                        fill="#fbfcfd", stroke="#c9d2dd", sw=1.2, rx=4))
        # горизонтальна сітка + підписи осі y (ЗА межами полотна, ліворуч)
        for v in ylabels:
            y = ybase - (v / ymax) * (ybase - ytop)
            out.append(line(x0, y, x1, y, color="#dde3ea", sw=1.0))
            out.append(text(x0 - 10, y + 4, ("%g" % v), size=12,
                            color=MUTED, anchor="end"))
        # позначки осі x (під полотном)
        for v in (0.0, 0.25, 0.5, 0.75, 1.0):
            x = x0 + v * (x1 - x0)
            out.append(line(x, ybase, x, ybase + 5, color="#9aa5b1", sw=1.0))
            out.append(text(x, ybase + 22, ("%g" % v), size=12, color=MUTED))
        # крива
        pts = []
        p = 0.01
        while p <= 0.995:
            y = ybase - (min(fn(p), ymax) / ymax) * (ybase - ytop)
            pts.append("%.1f,%.1f" % (x0 + p * (x1 - x0), y))
            p += 0.005
        out.append('<polyline points="%s" fill="none" stroke="%s" '
                   'stroke-width="2.6" stroke-linejoin="round"/>'
                   % (" ".join(pts), NEG))
        # вертикальна позначка цікавої точки; підпис — ПІД полотном, у полі
        xm = x0 + pmark * (x1 - x0)
        ym = ybase - (min(fn(pmark), ymax) / ymax) * (ybase - ytop)
        out.append(line(xm, ym, xm, ybase, color=POS, sw=1.4, dash="4 4"))
        out.append(circle(xm, ym, 5.0, fill=POS, stroke=POS, sw=1.2))
        out.append(text(xm, ybase + 42, "p = %g → %.2f" % (pmark, fn(pmark)),
                        size=12, color=POS, bold=True))
        # заголовок панелі — НАД полотном
        out.append(text((x0 + x1) / 2, ytop - 30, header, size=14, bold=True))
        out.append(text((x0 + x1) / 2, ytop - 12, sub, size=12, color=MUTED))
        return out

    ybase, ytop = 336.0, 132.0
    frags += panel(96, 430, ybase, ytop, 0.55,
                   lambda p: math.sqrt(p * (1 - p)), 0.5,
                   (0.1, 0.2, 0.3, 0.4, 0.5),
                   "Абсолютний розкид частки",
                   "√(p·(1−p)) — найгірше посередині")
    frags += panel(576, 910, ybase, ytop, 10.0,
                   lambda p: math.sqrt((1 - p) / p), 0.1,
                   (2, 4, 6, 8, 10),
                   "Відносний розкид", "√((1−p)/p) — злітає біля нуля")

    frags.append(text(W / 2, ybase + 74, "частка часу в ядрі  p", size=13))
    frags.append(text(W / 2, ybase + 94,
                      "обидві криві — в одиницях 1/√n : поділіть на корінь із числа тиків",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "spread-vs-p.svg"), W, H, *frags,
           title="Дві різні похибки тикової оцінки")


# ── 6. Фаза задачі проти фази тику (вставка math-sampling-error) ────────────
def fig_tick_phase():
    import math

    W, H = 960, 500
    frags = []
    R = 118.0
    CY = 250.0
    KERN = 0.10          # частка циклу, яку задача проводить у ядрі

    def pt(cx, turn, r):
        a = 2 * math.pi * turn
        return cx + r * math.sin(a), CY - r * math.cos(a)

    def wheel(cx, turns, header, tail, vcolor):
        out = []
        out.append(circle(cx, CY, R, fill="#ffffff", stroke="#c9d2dd", sw=2.0))
        # дуга «в ядрі» — перші KERN циклу
        x0, y0 = pt(cx, 0.0, R)
        x1, y1 = pt(cx, KERN, R)
        out.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" '
                   'fill="none" stroke="%s" stroke-width="11"/>'
                   % (x0, y0, R, R, x1, y1, POS))
        # точки-тики
        hits = 0
        for t in turns:
            f = t % 1.0
            if f < KERN:
                hits += 1
            px, py = pt(cx, f, R)
            out.append(circle(px, py, 4.6, fill=NEG, stroke="#ffffff", sw=1.2))
        # заголовок над колом
        out.append(text(cx, CY - R - 46, header, size=14, bold=True))
        # вирок під колом
        out.append(text(cx, CY + R + 42,
                        "у ядро влучили %d тиків із %d" % (hits, len(turns)),
                        size=13))
        out.append(text(cx, CY + R + 64,
                        "оцінка %.1f %% проти справжніх %.0f %% — %s"
                        % (100.0 * hits / len(turns), 100 * KERN, tail),
                        size=13, color=vcolor, bold=True))
        return out

    N = 24
    # ліворуч: період задачі кратний періодові тику — фаза стоїть на місці
    frags += wheel(258, [0.55] * N, "Період кратний тикові", "і так завжди", POS)
    # праворуч: розстроєний період — фаза обходить цикл
    golden = (math.sqrt(5) - 1) / 2
    frags += wheel(702, [(i * golden) % 1.0 for i in range(N)],
                   "Період розстроєний", "і сходиться далі", FIELD)

    # спільна легенда — унизу, під обома колами
    frags.append(text(W / 2, CY + R + 104,
                      "коло — один цикл задачі; червона дуга — 10 % циклу, "
                      "проведені в ядрі; сині точки — де застали тики",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "tick-phase.svg"), W, H, *frags,
           title="Чому похибка іноді не спадає: фаза тику всередині циклу задачі")


# ── 7. Охоплення інтерфейсів: від потоку до машини (вставка api-…) ──────────
def fig_scope_map():
    W, H = 980, 400
    x0 = 60.0
    xtext = 568.0
    rows = [
        (150, "потік", [
            "clock_gettime(CLOCK_THREAD_CPUTIME_ID) — нс, точно",
            "getrusage(RUSAGE_THREAD) · /proc/<pid>/task/<tid>/stat"]),
        (230, "процес: усі потоки", [
            "clock_gettime(CLOCK_PROCESS_CPUTIME_ID) — нс, точно",
            "getrusage(RUSAGE_SELF) · times() · stat 14–15"]),
        (310, "процес + дочекані нащадки", [
            "getrusage(RUSAGE_CHILDREN) · tms_cutime, tms_cstime",
            "/proc/<pid>/stat 16–17"]),
        (390, "контрольна група з нащадками", [
            "cpu.stat: usage_usec · user_usec · system_usec"]),
        (470, "уся машина, усі ядра", [
            "/proc/stat: рядки cpu, cpu0, cpu1, …",
            "десять граф у USER_HZ"]),
    ]

    frags = []
    y = 74.0
    hbar, pitch = 46.0, 62.0
    for w, label, lines in rows:
        frags.append(fitbox(x0, y, w, hbar, label, size=13))
        cy = y + hbar / 2
        first = cy + 4.0 if len(lines) == 1 else cy - 15.6 / 2 + 4.0
        frags.append(mtext(xtext, first, lines, size=12, anchor="start"))
        y += pitch

    render(os.path.join(IMG, "scope-map.svg"), W, H, *frags,
           title="Що саме входить у число: охоплення кожного інтерфейсу")


# ── 8. Кодування clockid процесорного годинника (вставка api-…) ─────────────
def fig_clockid_bits():
    W, H = 900, 290
    ybar, hbar = 96.0, 54.0
    xa, xb, xc, xd = 80.0, 560.0, 640.0, 820.0

    frags = [
        fitbox(xa, ybar, xb - xa, hbar, "~pid", size=15, bold=True),
        fitbox(xb, ybar, xc - xb, hbar, "P", size=15, bold=True),
        fitbox(xc, ybar, xd - xc, hbar, "which", size=15, bold=True),
        text((xa + xb) / 2, ybar - 13, "біти 31…3", size=12, color=MUTED),
        text((xb + xc) / 2, ybar - 13, "біт 2", size=12, color=MUTED),
        text((xc + xd) / 2, ybar - 13, "біти 1…0", size=12, color=MUTED),
    ]

    rows = [
        ("~pid", "PID, інвертований побітово — тому clockid завжди від'ємний"),
        ("P", "1 — годинник потоку; 0 — годинник процесу"),
        ("which", "2 = CPUCLOCK_SCHED — точна сума планувальника (0 — PROF, 1 — VIRT)"),
    ]
    yy = 200.0
    for name, desc in rows:
        frags.append(text(80, yy, name, size=13, anchor="start", bold=True))
        frags.append(text(184, yy, desc, size=13, anchor="start"))
        yy += 30

    render(os.path.join(IMG, "clockid-bits.svg"), W, H, *frags,
           title="clockid, який повертає clock_getcpuclockid()")


if __name__ == "__main__":
    fig_tick_sampling()
    fig_cputime_adjust()
    fig_tick_demux()
    fig_cheat_tick()
    fig_spread_vs_p()
    fig_tick_phase()
    fig_scope_map()
    fig_clockid_bits()
    print("ok")
