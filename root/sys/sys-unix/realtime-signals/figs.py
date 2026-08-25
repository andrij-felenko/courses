# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COLD = "#eaf0fd"
GREENFILL = "#eafaf1"


# ── 1. Порядок доправлення ──────────────────────────────────────────────────
def fig_delivery_order():
    W, H = 1180, 680
    p = []

    p.append(text(W / 2, 34, "Що очікує в процесі — і кого ядро віддасть наступним",
                  size=17, color=INK, bold=True))

    # ── ліва частина: що очікує
    p.append(rect(40, 66, 640, 540, fill=BG, stroke=MUTED, sw=1.4, rx=10))
    p.append(text(360, 92, "ОЧІКУЄ", size=13, color=MUTED, bold=True))

    # звичайні — бітова маска
    p.append(rect(64, 108, 592, 104, fill=WARM, stroke=POS, sw=1.8, rx=8))
    p.append(text(360, 132, "Звичайні 1…31 — бітова маска", size=13, color=POS, bold=True))
    bits = [("SIGTERM", "1"), ("SIGCHLD", "1"), ("SIGHUP", "0"), ("SIGUSR1", "0")]
    bx, bw, bgap = 92, 122, 16
    for i, (nm, v) in enumerate(bits):
        x = bx + i * (bw + bgap)
        p.append(fitbox(x, 150, bw, 44, nm + "\n" + v, size=11,
                        fill=BG, stroke=POS if v == "1" else MUTED, sw=1.4, color=INK))
    p.append(text(360, 206, "скільки разів породжено — не видно", size=11,
                  color=MUTED, italic=True))

    # реальночасові — черги
    p.append(rect(64, 234, 592, 352, fill=COLD, stroke=NEG, sw=1.8, rx=8))
    p.append(text(360, 258, "Реальночасові 32…64 — окрема черга на кожен номер",
                  size=13, color=NEG, bold=True))

    queues = [
        ("SIGRTMIN+0", ["стоп"]),
        ("SIGRTMIN+1", ["#7", "#3", "#9"]),
        ("SIGRTMIN+2", []),
        ("SIGRTMIN+5", ["лог", "лог"]),
    ]
    qy, qh, qgap = 278, 62, 12
    for i, (nm, items) in enumerate(queues):
        y = qy + i * (qh + qgap)
        p.append(fitbox(88, y, 152, qh, nm, size=12, fill=BG, stroke=NEG, sw=1.4, color=NEG))
        if not items:
            p.append(text(400, y + qh / 2 + 5, "порожня", size=11, color=MUTED, italic=True))
            continue
        cw, cgap = 92, 14
        for j, it in enumerate(items):
            x = 264 + j * (cw + cgap)
            p.append(fitbox(x, y + 10, cw, qh - 20, it, size=11,
                            fill=SOFT, stroke=NEG, sw=1.2, color=INK))
        p.append(text(264 + len(items) * (cw + cgap) + 26, y + qh / 2 + 5,
                      "← кладуть сюди", size=11, color=MUTED, anchor="start"))

    # ── права частина: порядок вибору
    p.append(rect(716, 66, 424, 540, fill=GREENFILL, stroke=FIELD, sw=1.8, rx=10))
    p.append(text(928, 92, "ЯДРО ВІДДАЄ В ТАКОМУ ПОРЯДКУ", size=13, color=FIELD, bold=True))

    steps = [
        "1.  SIGTERM  —  звичайні мають перевагу",
        "2.  SIGCHLD  —  теж звичайний",
        "3.  SIGRTMIN+0 «стоп»  —  менший номер",
        "4.  SIGRTMIN+1 «#7»  —  хто перший ліг",
        "5.  SIGRTMIN+1 «#3»",
        "6.  SIGRTMIN+1 «#9»",
        "7.  SIGRTMIN+5 «лог», далі другий «лог»",
    ]
    sy = 118
    for i, s in enumerate(steps):
        p.append(fitbox(740, sy + i * 54, 376, 42, s, size=11,
                        fill=BG, stroke=FIELD if i > 1 else POS, sw=1.3, color=INK))

    p.append(mtext(928, 512,
                   ["Номер працює як пріоритет: черга меншого",
                    "номера спорожнюється повністю раніше,",
                    "ніж почнеться черга більшого."],
                   size=12, color=INK))

    p.append(text(W / 2, 646,
                  "усередині номера — у порядку надсилання;  між номерами — менший перший;  "
                  "між родинами — звичайні перші",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "delivery-order.svg"), W, H, *p)


# ── 2. Запис черги: siginfo ─────────────────────────────────────────────────
def fig_siginfo_record():
    W, H = 1180, 640
    p = []

    p.append(text(W / 2, 34, "Один номер сигналу — різні джерела; розрізняє їх si_code",
                  size=17, color=INK, bold=True))

    sources = [
        ("kill()\nчужий процес", "SI_USER", "si_pid, si_uid", POS),
        ("sigqueue()\nчужий процес", "SI_QUEUE", "si_pid, si_uid, si_value", POS),
        ("POSIX-таймер\nдоспів", "SI_TIMER", "si_value з sigevent, si_overrun", NEG),
        ("mq_notify()\nчерга повідомлень", "SI_MESGQ", "si_value з sigevent", NEG),
        ("завершено\nасинхронний ввід", "SI_ASYNCIO", "si_value з sigevent", NEG),
    ]

    sx, sw, sgap = 40, 208, 20
    for i, (src, code, fields, accent) in enumerate(sources):
        x = sx + i * (sw + sgap)
        p.append(fitbox(x, 66, sw, 62, src, size=12, fill=SOFT, stroke=accent, sw=1.6, color=INK))
        p.append(arrow(x + sw / 2, 130, x + sw / 2, 164, color=accent, sw=1.5))
        p.append(fitbox(x, 168, sw, 40, code, size=12, fill=BG, stroke=accent, sw=1.8, color=accent))
        p.append(fitbox(x, 216, sw, 56, fields, size=10, fill=BG, stroke=MUTED, sw=1.1, color=MUTED))
        p.append(arrow(x + sw / 2, 274, x + sw / 2, 306, color=MUTED, sw=1.4))

    # сам запис
    p.append(rect(40, 312, 1100, 176, fill=COLD, stroke=NEG, sw=2, rx=10))
    p.append(text(590, 338, "ЗАПИС У ЧЕРЗІ — siginfo_t", size=14, color=NEG, bold=True))
    fields = [
        "si_signo\nномер сигналу",
        "si_code\nзвідки взявся",
        "si_pid / si_uid\nхто надіслав",
        "si_value\nчотири байти\nабо вказівник",
    ]
    fx, fw, fgap = 68, 250, 14
    for i, f in enumerate(fields):
        p.append(fitbox(fx + i * (fw + fgap), 356, fw, 108, f, size=12,
                        fill=BG, stroke=NEG, sw=1.4, color=INK))

    p.append(rect(40, 508, 540, 106, fill=GREENFILL, stroke=FIELD, sw=1.6, rx=8))
    p.append(text(310, 534, "Щоб це побачити", size=13, color=FIELD, bold=True))
    p.append(mtext(310, 558,
                   ["sigaction() з прапорцем SA_SIGINFO і обробником",
                    "на три аргументи — або sigwaitinfo()/sigtimedwait(),",
                    "або читання зі signalfd."],
                   size=11, color=INK))

    p.append(rect(600, 508, 540, 106, fill=WARM, stroke=POS, sw=1.6, rx=8))
    p.append(text(870, 534, "Межа безпеки", size=13, color=POS, bold=True))
    p.append(mtext(870, 558,
                   ["Надіслати ЧУЖОМУ процесові запис із невід'ємним",
                    "si_code ядро не дасть: невід'ємні коди належать",
                    "самому ядру (0x80) і kill() (0)."],
                   size=11, color=INK))

    render(os.path.join(OUT, "siginfo-record.svg"), W, H, *p)


# ── 3. Ціна черги ───────────────────────────────────────────────────────────
def fig_queue_budget():
    W, H = 1160, 620
    p = []

    p.append(text(W / 2, 34, "Черга коштує пам'яті, і квота — спільна на всього користувача",
                  size=17, color=INK, bold=True))

    # процеси одного користувача
    p.append(rect(40, 66, 420, 240, fill=SOFT, stroke=MUTED, sw=1.4, rx=10))
    p.append(text(250, 92, "процеси одного власника", size=12, color=MUTED, bold=True))
    procs = ["служба A", "служба B", "чужий\nскрипт того ж\nкористувача"]
    for i, s in enumerate(procs):
        p.append(fitbox(64, 110 + i * 62, 372, 50, s, size=11,
                        fill=BG, stroke=MUTED, sw=1.2, color=INK))
        p.append(arrow(444, 135 + i * 62, 520, 200, color=MUTED, sw=1.3))

    # квота
    p.append(rect(528, 108, 300, 190, fill=WARM, stroke=POS, sw=2, rx=10))
    p.append(text(678, 136, "RLIMIT_SIGPENDING", size=13, color=POS, bold=True))
    p.append(mtext(678, 160,
                   ["спільна квота записів",
                    "на РЕАЛЬНОГО власника,",
                    "по всіх його процесах",
                    "(ulimit -i)"],
                   size=11, color=INK))
    p.append(text(678, 284, "рахуються і звичайні теж", size=10, color=MUTED, italic=True))

    # два виходи
    p.append(arrow(834, 170, 900, 150, color=FIELD, sw=1.6))
    p.append(fitbox(908, 118, 216, 66, "є місце\nsigqueue() = 0", size=12,
                    fill=GREENFILL, stroke=FIELD, sw=1.6, color=INK))
    p.append(arrow(834, 240, 900, 260, color=POS, sw=1.6))
    p.append(fitbox(908, 230, 216, 66, "місця немає\nsigqueue() = EAGAIN", size=12,
                    fill=WARM, stroke=POS, sw=1.6, color=INK))

    # kill окремо
    p.append(rect(40, 336, 540, 108, fill=BG, stroke=NEG, sw=1.6, rx=8))
    p.append(text(310, 362, "kill() квоту не питає", size=13, color=NEG, bold=True))
    p.append(mtext(310, 386,
                   ["Один примірник сигналу, який ще не очікує, покласти",
                    "вдасться завжди — інакше вичерпана квота робила б",
                    "процеси невбиваними."],
                   size=11, color=INK))

    # ядро: один слот + лічильник
    p.append(rect(600, 336, 524, 108, fill=GREENFILL, stroke=FIELD, sw=1.6, rx=8))
    p.append(text(862, 362, "Таймер бере запис наперед", size=13, color=FIELD, bold=True))
    p.append(mtext(862, 386,
                   ["POSIX-таймер бере свій запис при створенні й тримає",
                    "щонайбільше ОДИН незабраний сигнал; решту спрацювань",
                    "рахує лічильник пропусків (timer_getoverrun)."],
                   size=11, color=INK))

    p.append(rect(40, 472, 1084, 110, fill=SOFT, stroke=MUTED, sw=1.4, rx=8))
    p.append(text(582, 498, "Що з цього виходить для відправника", size=13, color=INK, bold=True))
    p.append(mtext(582, 522,
                   ["EAGAIN — не аварія, а звичайний стан під сплеском. Потрібен план:",
                    "спробувати ще раз, злити кілька подій в одну й надіслати один сигнал,",
                    "або чесно повідомити про втрату. Мовчки проковтнути — повернутися до злипання."],
                   size=11, color=INK))

    render(os.path.join(OUT, "queue-budget.svg"), W, H, *p)


# ── 4. Дослід: що надіслано проти того, що забрано ──────────────────────────
def fig_dispatch_experiment():
    W, H = 1160, 590
    p = []

    p.append(text(W / 2, 34, "Дослід «порядок»: 100 записів у більший номер, один — у менший",
                  size=17, color=INK, bold=True))

    ROWS = [106, 158, 210, 262, 322]

    # ── ліворуч: надіслано
    p.append(rect(40, 62, 480, 356, fill=BG, stroke=MUTED, sw=1.4, rx=10))
    p.append(text(280, 90, "НАДІСЛАНО — у часі", size=13, color=MUTED, bold=True))

    sent = [
        ("sigqueue → SIGRTMIN+1, вантаж 0", False),
        ("sigqueue → SIGRTMIN+1, вантаж 1", False),
        ("⋮   ще 97 таких записів", False),
        ("sigqueue → SIGRTMIN+1, вантаж 99", False),
        ("sigqueue → SIGRTMIN+0, вантаж 999", True),
    ]
    for y, (s, hot) in zip(ROWS, sent):
        p.append(fitbox(96, y, 404, 40, s, size=12,
                        fill=WARM if hot else SOFT,
                        stroke=POS if hot else MUTED, sw=1.6 if hot else 1.2,
                        color=INK))
    p.append(arrow(70, 112, 70, 352, color=MUTED, sw=1.6))
    p.append(text(70, 378, "час", size=11, color=MUTED))

    # ── бар'єр
    p.append(line(578, 78, 578, 400, color=NEG, sw=1.8, dash="6 5"))
    p.append(fitbox(534, 402, 92, 44, "бар'єр\nбайт у канал", size=10,
                    fill=COLD, stroke=NEG, sw=1.4, color=NEG))

    # ── праворуч: забрано
    p.append(rect(636, 62, 484, 356, fill=BG, stroke=MUTED, sw=1.4, rx=10))
    p.append(text(878, 90, "ЗАБРАНО sigtimedwait — у порядку доправлення",
                  size=13, color=MUTED, bold=True))

    got = [
        ("SIGRTMIN+0, вантаж 999   ← надіслано ОСТАННІМ", True),
        ("SIGRTMIN+1, вантаж 0", False),
        ("SIGRTMIN+1, вантаж 1", False),
        ("⋮   вантажі 2…98, без пропусків", False),
        ("SIGRTMIN+1, вантаж 99", False),
    ]
    for y, (s, hot) in zip(ROWS, got):
        p.append(fitbox(660, y, 436, 40, s, size=12,
                        fill=WARM if hot else SOFT,
                        stroke=POS if hot else MUTED, sw=1.6 if hot else 1.2,
                        color=INK))

    # стрілка «останній став першим»
    p.append(arrow(510, 342, 652, 126, color=POS, sw=1.8))

    # ── підсумок
    p.append(rect(40, 462, 1080, 100, fill=GREENFILL, stroke=FIELD, sw=1.4, rx=8))
    p.append(mtext(580, 490,
                   ["Бар'єр тримає приймач, доки відправник не наповнить чергу: без нього записи",
                    "забиралися б по одному, і черги — а отже, і порядку — просто не існувало б.",
                    "Менший номер обганяє більший; усередині одного номера — суворо порядок надсилання."],
                   size=12, color=INK))

    render(os.path.join(OUT, "dispatch-experiment.svg"), W, H, *p)


fig_delivery_order()
fig_siginfo_record()
fig_queue_budget()
fig_dispatch_experiment()
print("ok")
