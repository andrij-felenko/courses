# -*- coding: utf-8 -*-
"""Фігури до теми «Витісненість ядра: від PREEMPT_NONE до PREEMPT_RT»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREY = "#e9ecef"
GREEN_BG = "#e6f5ec"
RED_BG = "#fdecea"


# ── 1. Коли розбуджена задача справді сідає на процесор ──────────────────────
def fig_models():
    W, H = 1080, 560
    P = []

    P.append(text(115, 76, "модель", size=14, bold=True))
    P.append(text(585, 76, "коли розбуджена задача R справді сідає на процесор",
                  size=14, bold=True))
    P.append(text(970, 76, "порядок затримки", size=14, bold=True))
    P.append(line(15, 92, 1065, 92, color=MUTED, sw=1))

    rows = [
        ("PREEMPT_NONE",
         ["тільки вихід у простір користувача",
          "та явні cond_resched() у довгих циклах"],
         0.86, "десятки мілісекунд"),
        ("PREEMPT_VOLUNTARY",
         ["додатково — кожна позначка might_sleep()",
          "у коді ядра"],
         0.64, "одиниці мілісекунд"),
        ("PREEMPT (повне)",
         ["будь-де, крім ділянок під спін-замком",
          "і коду переривань"],
         0.34, "сотні мікросекунд"),
        ("PREEMPT_RT",
         ["спін-замки сплять, переривання — потоки;",
          "заборонених ділянок лишається крихта"],
         0.12, "десятки мікросекунд"),
    ]

    x0, xw = 300.0, 570.0
    for i, (name, descr, frac, lat) in enumerate(rows):
        y = 120 + i * 105
        P.append(fitbox(15, y - 6, 200, 44, name, size=13, bold=True))
        gw = xw * frac
        P.append(rect(x0, y, gw, 32, fill=GREY, stroke=MUTED, sw=1.2))
        P.append(rect(x0 + gw, y, xw - gw, 32, fill=GREEN_BG, stroke=FIELD, sw=1.5))
        P.append(text(x0 + gw + (xw - gw) / 2, y + 21, "R біжить", size=12, color=FIELD))
        P.append(mtext(x0, y + 52, descr, size=12, color=MUTED, anchor="start", lh=1.35))
        P.append(text(970, y + 21, lat, size=13))

    P.append(text(300, 540,
                  "↑ нуль часу: подія сталася, прапорець «пора перемкнутися» вже стоїть",
                  size=12, color=MUTED, anchor="start"))
    return render(os.path.join(OUT, "models-latency.svg"), W, H, *P)


# ── 2. Прапорець, лічильник і місця перевірки ────────────────────────────────
def fig_gate():
    W, H = 1000, 580
    P = []

    P.append(textbox(250, 80, "тік таймера · пробудження задачі · зміна пріоритету",
                     size=13)[0])
    P.append(arrow(250, 106, 250, 138))
    P.append(textbox(250, 168, ["ядро ставить прапорець",
                                "TIF_NEED_RESCHED = 1"], size=13)[0])
    P.append(arrow(250, 200, 250, 232))
    P.append(textbox(250, 268, ["чи можна перемикати саме тут?",
                                "preempt_count == 0 ?"], size=13, bold=True,
                     fill="#fff9e6", stroke=POS)[0])
    P.append(arrow(195, 300, 135, 344))
    P.append(arrow(305, 300, 365, 344))
    P.append(fitbox(20, 350, 210, 76,
                    ["≠ 0 — ні:", "прапорець висить далі,", "ядро працює як працювало"],
                    size=12))
    P.append(fitbox(280, 350, 220, 76,
                    ["= 0 — так:", "schedule() тут і зараз,", "задачу знімають"],
                    size=12, fill=GREEN_BG, stroke=FIELD))

    P.append(text(760, 76, "preempt_count — одне слово, кілька полів", size=13, bold=True))
    fields = ["NMI — немасковане переривання",
              "HARDIRQ — обробник переривання",
              "SOFTIRQ — local_bh_disable()",
              "PREEMPT — spin_lock(), preempt_disable()"]
    for i, f in enumerate(fields):
        P.append(fitbox(560, 95 + i * 62, 400, 50, f, size=13))
    P.append(fitbox(560, 350, 400, 76,
                    ["Будь-яке ненульове поле означає",
                     "«тут перемикати не можна».",
                     "Нуль у всіх — витіснення дозволене."],
                    size=12, fill="#f9fafb", stroke=MUTED))

    P.append(text(500, 452, "де ядро питає цей вентиль", size=13, bold=True))
    spots = [["вихід із ядра", "в простір користувача", "— у всіх моделях"],
             ["preempt_enable()", "spin_unlock()", "— PREEMPT і RT"],
             ["повернення з переривання", "в код ядра", "— PREEMPT і RT"],
             ["cond_resched()", "у довгих циклах", "— NONE і VOLUNTARY"]]
    for i, s in enumerate(spots):
        P.append(fitbox(20 + i * 246, 468, 230, 82, s, size=12))
    return render(os.path.join(OUT, "preempt-gate.svg"), W, H, *P)


# ── 3. Що саме перероблює PREEMPT_RT ─────────────────────────────────────────
def fig_rt():
    W, H = 1020, 520
    P = []

    P.append(text(280, 70, "звичайне ядро (PREEMPT)", size=14, bold=True))
    P.append(text(790, 70, "PREEMPT_RT", size=14, bold=True))

    rows = [
        (["spinlock_t: чекають, крутячись;",
          "витіснення на цьому ядрі вимкнене"],
         ["сплячий замок: чекання — це сон,",
          "з успадкуванням пріоритету"], False),
        (["обробник переривання виконується",
          "одразу, у контексті переривання"],
         ["обробник — потік ядра",
          "зі своїм пріоритетом"], False),
        (["softirq виконується на виході",
          "з переривання, витіснити не можна"],
         ["softirq — у потоці,",
          "витісняється як усе інше"], False),
        (["raw_spinlock_t — рідкісний виняток"],
         ["raw_spinlock_t — без змін:",
          "тут витіснення заборонене й далі"], True),
    ]

    for i, (left, right, hot) in enumerate(rows):
        y = 100 + i * 88
        fill = RED_BG if hot else FILL
        stroke = POS if hot else LINE
        P.append(fitbox(40, y, 480, 64, left, size=13, fill=fill, stroke=stroke))
        P.append(arrow(534, y + 32, 590, y + 32))
        P.append(fitbox(600, y, 390, 64, right, size=13, fill=fill, stroke=stroke))

    P.append(fitbox(40, 442, 950, 58,
                    ["Незмінним лишається крихітне ядро заборони: NMI, вхід у переривання, сам планувальник, raw_spinlock.",
                     "Саме ці ділянки й задають нижню межу затримки, яку не подолати вже нічим."],
                    size=12, fill="#f9fafb", stroke=MUTED))
    return render(os.path.join(OUT, "rt-transform.svg"), W, H, *P)


# ── 4. Лінивий прапорець ─────────────────────────────────────────────────────
def fig_lazy_flag():
    W, H = 1000, 400
    P = []
    x0, x1 = 280.0, 940.0

    y = 110
    P.append(fitbox(15, y - 12, 235, 56,
                    ["звичайна задача", "будить звичайну"], size=12, bold=True))
    P.append(text(280, y - 20, "подія: ставлять слабкий прапорець LAZY",
                  size=12, color=MUTED, anchor="start"))
    P.append(rect(x0, y, 480, 30, fill=GREY, stroke=MUTED, sw=1.2))
    P.append(text(x0 + 240, y + 20, "задача працює далі — до найближчого тіку", size=12))
    P.append(rect(x0 + 480, y, x1 - x0 - 480, 30, fill=GREEN_BG, stroke=FIELD))
    P.append(text(x0 + 480 + (x1 - x0 - 480) / 2, y + 20, "перемикання", size=12, color=FIELD))
    P.append(text(760, y + 52, "↑ тік таймера підвищує LAZY до справжнього NEED_RESCHED",
                  size=12, color=MUTED))

    y = 250
    P.append(fitbox(15, y - 12, 235, 56,
                    ["прокинулася", "реальночасова задача"], size=12, bold=True))
    P.append(text(280, y - 20, "подія: ставлять справжній прапорець NEED_RESCHED",
                  size=12, color=MUTED, anchor="start"))
    P.append(rect(x0, y, 30, 30, fill=GREY, stroke=MUTED, sw=1.2))
    P.append(rect(x0 + 30, y, x1 - x0 - 30, 30, fill=GREEN_BG, stroke=FIELD))
    P.append(text(x0 + 30 + (x1 - x0 - 30) / 2, y + 20,
                  "перемикання одразу — на найближчій безпечній межі", size=12, color=FIELD))

    P.append(fitbox(40, 330, 920, 52,
                    ["Лінивий прапорець дає повному витісненню пропускну здатність, близьку до PREEMPT_NONE,",
                     "не забираючи негайності там, де вона справді потрібна."],
                    size=12, fill="#f9fafb", stroke=MUTED))
    return render(os.path.join(OUT, "lazy-flag.svg"), W, H, *P)


BLUE_BG = "#eaf0fd"


# ── 5. Відносний сон проти абсолютного (вставка proj-measure-latency) ────────
def fig_drift():
    W, H = 1140, 470
    P = []

    x0, dx = 270, 190
    marks = [x0 + i * dx for i in range(5)]          # 270 460 650 840 1030
    top, bot = 112, 300

    P.append(text(650, 62, "моменти, коли потік МАЄ прокинутися: tₖ = t₀ + k·T",
                  size=15, bold=True))
    for i, x in enumerate(marks):
        P.append(line(x, top, x, bot, color=MUTED, sw=1.2, dash="5 5"))
        P.append(text(x, top - 12, ["t₀", "t₁", "t₂", "t₃", "t₄"][i],
                      size=13, color=MUTED))

    # рядок 1 — відносний сон: зсув накопичується
    yA = 170
    P.append(fitbox(25, yA - 32, 210, 64,
                    ["відносний сон", "nanosleep(T)"], size=13, fill=RED_BG, stroke=POS))
    P.append(line(255, yA, 1115, yA, color=MUTED, sw=1.2))
    for i, x in enumerate(marks):
        mx = x + 18 * i
        if i:
            P.append(line(x, yA, mx, yA, color=POS, sw=6))
        P.append(circle(mx, yA, 8, fill=RED_BG, stroke=POS, sw=2))

    # рядок 2 — абсолютний сон: лише тремтіння навколо сітки
    yB = 258
    jit = [4, 8, 3, 10, 5]
    P.append(fitbox(25, yB - 32, 210, 64,
                    ["абсолютний сон", "TIMER_ABSTIME"], size=13, fill=GREEN_BG, stroke=FIELD))
    P.append(line(255, yB, 1115, yB, color=MUTED, sw=1.2))
    for i, x in enumerate(marks):
        mx = x + jit[i]
        P.append(line(x, yB, mx, yB, color=FIELD, sw=6))
        P.append(circle(mx, yB, 8, fill=GREEN_BG, stroke=FIELD, sw=2))

    P.append(fitbox(35, 326, 1070, 56,
                    ["Відносний сон: кожен оберт додає до кроку власну роботу й затримку, тож сітка тікає —",
                     "а запізнення непомітне, бо відлік щоразу ведеться від щойно пропущеного прокидання."],
                    size=13, fill=RED_BG, stroke=POS))
    P.append(fitbox(35, 394, 1070, 56,
                    ["Абсолютний сон: наступний момент рахують від сітки, а не від «зараз» — дрейф не накопичується,",
                     "кожне запізнення лишається при своєму оберті, і різниця «мав — прокинувся» і є те, що ми міряємо."],
                    size=13, fill=GREEN_BG, stroke=FIELD))
    return render(os.path.join(OUT, "sleep-drift.svg"), W, H, *P)


# ── 6. Куди зникає час і чим це видно (вставка proj-measure-latency) ─────────
def fig_hunt():
    W, H = 1150, 490
    P = []

    c1, w1 = 25, 385
    c2, w2 = 425, 285
    c3, w3 = 730, 395

    P.append(text(c1 + w1 / 2, 64, "куди зник час", size=15, bold=True))
    P.append(text(c2 + w2 / 2, 64, "чим це видно", size=15, bold=True))
    P.append(text(c3 + w3 / 2, 64, "що з цим робити", size=15, bold=True))
    P.append(line(20, 82, 1130, 82, color=MUTED, sw=1))

    rows = [
        (["переривання вимкнені —", "ядро не дізналося про подію"],
         ["ftrace: irqsoff"],
         ["винуватця називає рядок", "«started at» у трасі"]),
        (["витіснення заборонене —", "ядро знає, але не перемикає"],
         ["ftrace: preemptoff"],
         ["довга ділянка під спін-замком", "або затяжний softirq"]),
        (["від пробудження задачі", "до її першої інструкції"],
         ["ftrace: wakeup_rt"],
         ["та сама величина, що й у нашій", "програмі, — але разом із трасою"]),
        (["процесор виконував те,", "чого ядро не бачило взагалі"],
         ["hwlatdetect"],
         ["прошивка й SMI: ядро безсиле,", "лишається BIOS або інше залізо"]),
        (["ядро прокидалося з глибокого", "сну або на низькій частоті"],
         ["cpupower idle-info,", "turbostat"],
         ["/dev/cpu_dma_latency = 0,", "governor performance"]),
    ]

    y = 96
    for a, b, c in rows:
        P.append(fitbox(c1, y, w1, 66, a, size=13, fill=RED_BG, stroke=POS))
        P.append(fitbox(c2, y, w2, 66, b, size=13, fill=BLUE_BG, stroke=NEG, bold=True))
        P.append(fitbox(c3, y, w3, 66, c, size=13, fill=GREEN_BG, stroke=FIELD))
        y += 78

    return render(os.path.join(OUT, "latency-hunt.svg"), W, H, *P)


# ── 7. Чотири шари важелів (вставка api-preempt-controls) ────────────────────
def _chip(x, y, w, h, head, sub):
    o = rect(x, y, w, h, fill=FILL, stroke=LINE, sw=1.2)
    o += text(x + w / 2, y + 21, head, size=fit_font(head, w - 20, 13, True), bold=True)
    o += text(x + w / 2, y + 39, sub, size=fit_font(sub, w - 20, 11), color=MUTED)
    return o


def fig_levers():
    W, H = 1160, 566
    P = []

    P.append(text(150, 42, "де живе важіль", size=13, bold=True))
    P.append(text(720, 42, "що саме крутять", size=13, bold=True))
    P.append(line(20, 54, 1140, 54, color=MUTED, sw=1))

    bands = [
        (["Складання ядра"], ["перескладання", "й перезавантаження"], [
            ("CONFIG_PREEMPT_LAZY · CONFIG_PREEMPT_RT", "яка машинерія взагалі вкомпільована"),
            ("CONFIG_PREEMPT_DYNAMIC", "дозволити вибір моделі при завантаженні"),
            ("CONFIG_DEBUG_ATOMIC_SLEEP", "лаятися на сон у забороненому контексті"),
            ("CONFIG_DEBUG_PREEMPT", "ловити хиби лічильника заборон"),
        ]),
        (["Командний рядок ядра"], ["перезавантаження"], [
            ("preempt=none|voluntary|full|lazy", "модель, з якою система стартує"),
            ("threadirqs", "обробники переривань — у потоки"),
            ("isolcpus= · nohz_full= · rcu_nocbs=", "прибрати з ядра процесора чужу роботу"),
            ("irqaffinity=", "куди за замовчуванням падають переривання"),
        ]),
        (["Файли на ходу"], ["діє негайно"], [
            ("/sys/kernel/debug/sched/preempt", "перемкнути модель просто зараз"),
            ("sched_rt_period_us · sched_rt_runtime_us", "стеля часу для реальночасових задач"),
            ("timer_migration", "чи тікають таймери з простійних ядер"),
            ("ftrace: preemptoff, wakeup_rt", "побачити, хто саме тримав процесор"),
        ]),
        (["Одна задача"], ["діє негайно,", "лише на неї"], [
            ("chrt -f -p 70 «pid потоку irq/N»", "пріоритет потокового обробника"),
            ("taskset · cpuset у cgroup v2", "на яких ядрах їй дозволено бігти"),
            ("sched_setscheduler() у програмі", "клас і пріоритет самої задачі"),
            ("preempt_disable() · local_lock()", "заборона витіснення у власному коді"),
        ]),
    ]

    for i, (name, cost, chips) in enumerate(bands):
        y = 70 + i * 120
        P.append(rect(20, y, 260, 108, fill="#f9fafb", stroke=MUTED, sw=1.2))
        P.append(mtext(150, y + 34, name, size=13, bold=True))
        P.append(mtext(150, y + 76, cost, size=11, color=MUTED))
        for j, (head, sub) in enumerate(chips):
            cx = 300 + (j % 2) * 430
            cy = y + 2 + (j // 2) * 56
            P.append(_chip(cx, cy, 410, 48, head, sub))

    return render(os.path.join(OUT, "preempt-levers.svg"), W, H, *P)


if __name__ == "__main__":
    fig_models()
    fig_gate()
    fig_rt()
    fig_lazy_flag()
    fig_drift()
    fig_hunt()
    fig_levers()
    print("ok")
