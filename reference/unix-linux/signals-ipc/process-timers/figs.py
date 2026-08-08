# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COLD = "#eaf0fd"
GREENFILL = "#eafaf1"


# ── 1. Чотири шари інтерфейсів ──────────────────────────────────────────────
def fig_four_layers():
    W, H = 1330, 530
    p = []

    cols = [(40, 215), (265, 200), (475, 170), (655, 335), (1000, 290)]
    heads = ["виклик", "скільки таймерів", "крок часу",
             "як приходить новина", "fork / exec"]

    for (x, w), h in zip(cols, heads):
        p.append(rect(x, 52, w, 46, fill=COLD, stroke=NEG, sw=1.6, rx=6))
        p.append(text(x + w / 2, 81, h, size=13, color=NEG, bold=True))

    rows = [
        ("alarm()",
         "один на процес",
         "цілі секунди",
         "SIGALRM,\nбез жодних подробиць",
         "переживає exec,\nне успадковується при fork"),
        ("setitimer()",
         "три:\nREAL, VIRTUAL, PROF",
         "мікросекунди",
         "SIGALRM, SIGVTALRM,\nSIGPROF",
         "переживає exec,\nне успадковується при fork"),
        ("timer_create()",
         "скільки завгодно",
         "наносекунди",
         "будь-який сигнал\n+ ваше значення в siginfo;\nабо новий потік",
         "гине і при fork,\nі при exec"),
        ("timerfd_create()",
         "скільки завгодно",
         "наносекунди",
         "дескриптор стає готовим,\nread() віддає число спрацювань",
         "успадковується при fork,\nпереживає exec без CLOEXEC"),
    ]

    y = 108
    for i, r in enumerate(rows):
        fillc = BG if i % 2 == 0 else SOFT
        p.append(rect(cols[0][0], y, cols[0][1], 76, fill=GREENFILL if i == 3 else FILL,
                      stroke=FIELD if i == 3 else MUTED, sw=1.6, rx=6))
        p.append(text(cols[0][0] + cols[0][1] / 2, y + 44, r[0], size=15,
                      color=FIELD if i == 3 else INK, bold=True))
        for (x, w), s in zip(cols[1:], r[1:]):
            p.append(fitbox(x, y, w, 76, s, size=12, fill=fillc, stroke=MUTED, sw=1.2))
        y += 82

    p.append(rect(40, 448, 1250, 62, fill=GREENFILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(mtext(665, 472,
                   ["Три перші рядки сповіщають сигналом — з усіма його обмеженнями: одна новина без подробиць,",
                    "у довільному потоці, посеред довільної інструкції. Четвертий робить час звичайною подією дескриптора."],
                   size=12.5, color=INK))

    render(os.path.join(OUT, "four-layers.svg"), W, H, *p,
           title="Чотири способи попросити ядро нагадати про час")


# ── 2. Шлях від заліза до коду ──────────────────────────────────────────────
def fig_delivery_path():
    W, H = 1270, 740
    p = []

    chain = [
        (40, 250, "апаратний таймер\nядра процесора"),
        (330, 280, "черга hrtimer:\nдедлайни, відсортовані\nза абсолютним часом"),
        (650, 250, "переривання:\nнайближчий дедлайн настав"),
        (940, 290, "ядро знімає з черги все,\nчому час уже настав"),
    ]
    for x, w, s in chain:
        p.append(fitbox(x, 78, w, 90, s, size=12.5, fill=COLD, stroke=NEG, sw=1.8))
    p.append(arrow(290, 123, 330, 123, color=MUTED, sw=1.8))
    p.append(arrow(610, 123, 650, 123, color=MUTED, sw=1.8))
    p.append(arrow(900, 123, 940, 123, color=MUTED, sw=1.8))

    # розгалуження
    p.append(line(1085, 168, 1085, 202, color=MUTED, sw=1.8))
    p.append(line(340, 202, 1085, 202, color=MUTED, sw=1.8))
    p.append(arrow(340, 202, 340, 244, color=POS, sw=1.8))
    p.append(arrow(930, 202, 930, 244, color=FIELD, sw=1.8))

    left = [
        "ШЛЯХ СИГНАЛУ\nядро породжує сигнал для процесу",
        "біт лягає в набір очікуваних\n(другий такий самий зіллється з ним)",
        "доправлення — лише на межі\nповернення в простір користувача",
        "обробник у довільному потоці\nпосеред довільної інструкції",
    ]
    right = [
        "ШЛЯХ ДЕСКРИПТОРА\nлічильник спрацювань у timerfd += 1",
        "дескриптор стає готовим на читання",
        "epoll будить той потік,\nякий сам ліг на нього спати",
        "read() віддає число спрацювань\nу звичайному місці коду",
    ]

    y = 248
    for i in range(4):
        p.append(fitbox(115, y, 450, 78, left[i], size=12.5,
                        fill=WARM if i == 0 else FILL, stroke=POS if i == 0 else MUTED, sw=1.6))
        p.append(fitbox(705, y, 450, 78, right[i], size=12.5,
                        fill=GREENFILL if i == 0 else FILL, stroke=FIELD if i == 0 else MUTED, sw=1.6))
        if i < 3:
            p.append(arrow(340, y + 78, 340, y + 96, color=POS, sw=1.6))
            p.append(arrow(930, y + 78, 930, y + 96, color=FIELD, sw=1.6))
        y += 96

    p.append(rect(115, 632, 1040, 76, fill=SOFT, stroke=MUTED, sw=1.6, rx=8))
    p.append(mtext(635, 660,
                   ["Між дедлайном і вашим кодом стоять ще планувальник, вихід ядра процесора з глибокого сну",
                    "й навмисне склеювання близьких спрацювань (timer slack). Тому таймер обіцяє «не раніше»,",
                    "а не «точно тоді»: запізнення нормоване, випередження неможливе."],
                   size=12.5, color=INK))

    render(os.path.join(OUT, "delivery-path.svg"), W, H, *p,
           title="Одне спрацювання, два способи дізнатися про нього")


# ── 3. Дрейф: відносне переозброєння проти абсолютного дедлайну ─────────────
def fig_drift():
    W, H = 1220, 590
    p = []

    def panel(y0, title, color, offsets, marks, verdict):
        p.append(rect(40, y0, 1140, 216, fill=SOFT, stroke=MUTED, sw=1.4, rx=8))
        p.append(text(610, y0 + 30, title, size=13.5, color=color, bold=True))
        ax = y0 + 140
        p.append(line(90, ax, 1130, ax, color=INK, sw=1.6))
        for k in range(6):
            x = 90 + k * 190
            p.append(line(x, ax - 7, x, ax + 7, color=MUTED, sw=1.4))
            p.append(text(x, ax + 28, "%d" % (k * 100), size=11.5, color=MUTED))
        p.append(text(1130, ax + 28, "мс", size=11.5, color=MUTED, anchor="end"))
        for k in range(6):
            x = 90 + k * 190 + offsets[k]
            p.append(circle(x, ax - 30, 7, fill=color, stroke=color, sw=1.4))
            if marks[k]:
                p.append(text(x, ax - 50, marks[k], size=11.5, color=color, bold=True))
        p.append(text(610, y0 + 196, verdict, size=12.5, color=INK))

    panel(56,
          "переозброєння ВІДНОСНЕ: наступний строк відлічують від миті, коли вже все опрацьовано",
          POS,
          [0, 12, 24, 36, 48, 60],
          ["", "+5 мс", "+10", "+15", "+20", "+25"],
          "кожні 5 мс опрацювання лягають зверху: за годину роботи набігає три хвилини відставання")

    panel(300,
          "інтервал ЯДРА: наступний дедлайн ядро рахує від попереднього дедлайну",
          FIELD,
          [0, 3, -2, 4, -1, 2],
          ["", "", "тремтіння,\nа не відставання", "", "", ""],
          "похибка кожного разу нова й невелика; вона не додається до попередньої")

    p.append(rect(40, 526, 1140, 48, fill=GREENFILL, stroke=FIELD, sw=1.6, rx=8))
    p.append(text(610, 555,
                  "it_interval у setitimer, timer_settime і timerfd_settime рахує ядро — тому періодичний таймер не збивається.",
                  size=12.5, color=INK))

    render(os.path.join(OUT, "drift.svg"), W, H, *p,
           title="Чому «поспати ще стільки ж» і «спрацьовувати щостільки» — різні речі")


# ── 4. Що буде, коли процес не встиг ────────────────────────────────────────
def fig_overrun():
    W, H = 1200, 500
    p = []

    ax = 168
    p.append(rect(200, 108, 480, 118, fill=WARM, stroke=POS, sw=1.6, rx=8))
    p.append(text(440, 132, "процес зайнятий або сигнал заблокований", size=12.5,
                  color=POS, bold=True))

    p.append(line(60, ax, 1140, ax, color=INK, sw=1.6))
    for k in range(9):
        x = 60 + k * 120
        p.append(line(x, ax - 7, x, ax + 7, color=MUTED, sw=1.4))
        p.append(text(x, ax + 30, "%d" % (k * 100), size=11.5, color=MUTED))
    p.append(text(1140, ax + 30, "мс", size=11.5, color=MUTED, anchor="end"))

    for k in range(1, 5):
        x = 60 + k * 120
        p.append(circle(x, ax - 32, 7, fill=POS, stroke=POS, sw=1.4))
    p.append(text(440, 210, "чотири спрацювання, поки нікому їх приймати", size=12,
                  color=POS))

    p.append(fitbox(60, 268, 520, 104,
                    "ШЛЯХ СИГНАЛУ\nу черзі чекає один-єдиний сигнал;\nщо сталося ще тричі, скаже timer_getoverrun() → 3",
                    size=12.5, fill=WARM, stroke=POS, sw=1.8))
    p.append(fitbox(620, 268, 520, 104,
                    "ШЛЯХ ДЕСКРИПТОРА\nread() віддає 4 — стільки спрацювань\nнабігло від минулого читання",
                    size=12.5, fill=GREENFILL, stroke=FIELD, sw=1.8))

    p.append(rect(60, 400, 1080, 76, fill=SOFT, stroke=MUTED, sw=1.6, rx=8))
    p.append(mtext(600, 428,
                   ["Жоден зі шляхів не намагається надолужити пропущене чергою сповіщень: ви дістаєте одне",
                    "сповіщення й число. Що робити з тими трьома — надолужувати роботу чи свідомо пропустити —",
                    "вирішує програма, і ядро навмисне не вирішує це за неї."],
                   size=12.5, color=INK))

    render(os.path.join(OUT, "overrun.svg"), W, H, *p,
           title="Таймер спрацював чотири рази, а сповіщення одне")


# ── 5. Два обриси планувальника (вставка proj-timerfd-scheduler) ────────────
def fig_two_shapes():
    W, H = 1300, 700
    p = []

    for x0 in (40, 670):
        p.append(rect(x0, 36, 590, 556, fill=SOFT, stroke=MUTED, sw=1.4, rx=10))

    # ── ліва панель: окремий дескриптор на задачу ──
    p.append(fitbox(70, 56, 530, 46, "A · окремий timerfd на кожну задачу",
                    size=14, bold=True, fill=COLD, stroke=NEG, sw=1.8, color=NEG))
    p.append(fitbox(70, 122, 530, 74,
                    "ЯДРО тримає N періодичних таймерів;\nфазу веде it_interval, тобто саме ядро",
                    size=12.5, fill=BG, stroke=MUTED, sw=1.6))

    fds = ["timerfd\n20 мс", "timerfd\n200 мс", "timerfd\n5 с"]
    for k, s in enumerate(fds):
        x = 70 + k * 182
        p.append(fitbox(x, 222, 166, 62, s, size=12.5, fill=COLD, stroke=NEG, sw=1.6))
        p.append(arrow(x + 83, 286, x + 83, 312, color=MUTED, sw=1.6))

    p.append(fitbox(70, 316, 530, 62, "один epoll_wait: сокети й таймери — рівні події",
                    size=12.5, fill=GREENFILL, stroke=FIELD, sw=1.6))
    p.append(fitbox(70, 402, 530, 84,
                    "на спрацювання: один read(), жодного переозброєння —\nO(1), але N дескрипторів і N таймерів у ядрі",
                    size=12.5, fill=BG, stroke=MUTED, sw=1.6))
    p.append(fitbox(70, 506, 530, 62, "доречно, поки задач одиниці-сотні й вони сталі",
                    size=12.5, fill=FILL, stroke=MUTED, sw=1.6))

    # ── права панель: один таймер і купа строків ──
    p.append(fitbox(700, 56, 530, 46, "B · один timerfd на найближчий дедлайн",
                    size=14, bold=True, fill=COLD, stroke=NEG, sw=1.8, color=NEG))
    p.append(fitbox(700, 122, 530, 74,
                    "ЯДРО тримає ОДИН таймер —\nна найближчий абсолютний дедлайн",
                    size=12.5, fill=BG, stroke=MUTED, sw=1.6))
    p.append(fitbox(700, 222, 530, 62,
                    "купа строків У ПРОГРАМІ: у корені — найближчий",
                    size=12.5, fill=WARM, stroke=POS, sw=1.6))
    p.append(arrow(965, 286, 965, 312, color=MUTED, sw=1.6))
    p.append(fitbox(700, 316, 530, 62, "один epoll_wait: сокети й ОДИН таймер",
                    size=12.5, fill=GREENFILL, stroke=FIELD, sw=1.6))
    p.append(fitbox(700, 402, 530, 84,
                    "на спрацювання: знімаємо все, чому час настав —\nO(log N) на кожен плюс одне переозброєння кореня",
                    size=12.5, fill=BG, stroke=MUTED, sw=1.6))
    p.append(fitbox(700, 506, 530, 62, "єдиний спосіб, коли строків тисячі й вони недовговічні",
                    size=12.5, fill=FILL, stroke=MUTED, sw=1.6))

    p.append(rect(40, 612, 1220, 68, fill=GREENFILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(mtext(650, 640,
                   ["Фаза в обох обрисах тримається однаково: строк задають АБСОЛЮТНИМ моментом, а наступний рахують",
                    "від номіналу, а не від миті обробки. Різниця лише в тому, хто веде розклад — ядро чи ваша купа."],
                   size=12.5, color=INK))

    render(os.path.join(OUT, "two-shapes.svg"), W, H, *p,
           title="Два способи скласти багато періодів в один цикл подій")


if __name__ == "__main__":
    fig_four_layers()
    fig_delivery_path()
    fig_drift()
    fig_overrun()
    fig_two_shapes()
    print("ok")
