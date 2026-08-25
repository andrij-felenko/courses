# -*- coding: utf-8 -*-
"""Фігури до теми «PID і дерево процесів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_ring():
    W, H = 980, 350
    f = []
    # вісь номерів
    f.append(line(100, 170, 820, 170, sw=2))
    f.append(line(100, 160, 100, 180, sw=2))
    f.append(line(820, 160, 820, 180, sw=2))
    # вже роздана ділянка
    f.append(rect(100, 162, 460, 16, fill="#e6edf7", stroke=MUTED, sw=1, rx=3))
    # підписи меж
    f.append(text(88, 202, "300", size=13, bold=True, anchor="end"))
    f.append(text(88, 222, "RESERVED_PIDS", size=11, color=MUTED, anchor="end"))
    f.append(text(832, 202, "pid_max", size=13, bold=True, anchor="start"))
    f.append(text(832, 222, "32768 … 4194304", size=11, color=MUTED, anchor="start"))
    f.append(text(330, 248, "числа тут уже роздавали", size=12, color=MUTED))
    # покажчик на останній виданий
    b, _, _ = textbox(600, 96, "останній виданий номер", size=13)
    f.append(b)
    f.append(arrow(600, 118, 600, 158))
    # обертання
    f.append(line(820, 180, 820, 265, color=NEG, sw=1.6, dash="7 5"))
    f.append(line(820, 265, 100, 265, color=NEG, sw=1.6, dash="7 5"))
    f.append(arrow(100, 265, 100, 184, color=NEG))
    b, _, _ = textbox(460, 306, "дійшовши до pid_max, пошук починається знову від 300",
                      size=13, fill="#eef3fd", stroke=NEG)
    f.append(b)
    render(os.path.join(OUT, 'pid-ring.svg'), W, H, *f,
           title="Роздача номерів по колу")


def fig_tree():
    W, H = 1000, 520
    f = []
    nodes = [
        (480, 80, "PID 1\ninit", LINE),
        (220, 200, "PID 812\nsshd", LINE),
        (740, 200, "PID 1204\nсервіс", POS),
        (220, 320, "PID 1533\nbash", LINE),
        (740, 320, "PID 1290\nробітник", LINE),
        (120, 440, "PID 1720\nmake", LINE),
        (330, 440, "PID 1721\ncc", LINE),
    ]
    for cx, cy, s, st in nodes:
        b, _, _ = textbox(cx, cy, s, size=13, stroke=st)
        f.append(b)
    # ребра «створив»
    f.append(arrow(440, 108, 252, 172))
    f.append(arrow(520, 108, 708, 172))
    f.append(arrow(220, 228, 220, 292))
    f.append(arrow(196, 348, 142, 412))
    f.append(arrow(248, 348, 312, 412))
    f.append(arrow(740, 228, 740, 292, color=MUTED))
    f.append(text(660, 252, "завершився", size=12, color=POS, anchor="end"))
    # перепідпорядкування
    f.append(line(788, 320, 900, 320, color=NEG, sw=1.6, dash="7 5"))
    f.append(line(900, 320, 900, 80, color=NEG, sw=1.6, dash="7 5"))
    f.append(arrow(900, 80, 518, 80, color=NEG))
    f.append(text(500, 496, "суцільна стрілка — «створив»;   пунктир — сироту перепідпорядковано до PID 1",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'process-tree.svg'), W, H, *f,
           title="Дерево процесів і перепідпорядкування сироти")


def fig_race():
    W, H = 980, 430
    f = []
    # смуги життя
    f.append(rect(235, 120, 665, 26, fill="#eef3fd", stroke=NEG, sw=1.4, rx=4))
    f.append(rect(235, 220, 325, 26, fill="#f1f3f5", stroke=LINE, sw=1.4, rx=4))
    f.append(rect(660, 320, 240, 26, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    # підписи смуг
    f.append(text(210, 138, "наглядач", size=13, anchor="end"))
    f.append(text(210, 238, "дитина, PID 4242", size=13, anchor="end"))
    f.append(text(210, 338, "чужий процес", size=13, anchor="end"))
    # події
    f.append(text(330, 106, "прочитав pid = 4242", size=12, color=NEG))
    f.append(text(560, 206, "завершився → номер вільний", size=12, color=MUTED, anchor="end"))
    f.append(text(580, 243, "✕", size=19, color=POS, anchor="middle"))
    f.append(text(780, 306, "новий процес отримав 4242", size=12, color=POS, anchor="end"))
    f.append(text(858, 192, "kill(4242, SIGTERM)", size=12, color=POS, anchor="end"))
    f.append(line(880, 148, 880, 300, color=POS, sw=1.6, dash="6 4"))
    f.append(arrow(880, 300, 880, 316, color=POS))
    # час
    f.append(arrow(235, 390, 900, 390, color=MUTED))
    f.append(text(914, 395, "час", size=12, color=MUTED, anchor="start"))
    render(os.path.join(OUT, 'pid-reuse-race.svg'), W, H, *f,
           title="Гонка перевикористання номера")


def fig_names():
    W, H = 980, 500
    f = []
    f.append(fitbox(70, 190, 230, 120,
                    "задача в ядрі\n(одна структура,\nті самі байти)", size=14, bold=True))
    rows = [
        (70, "TID 5307", "номер самої задачі — gettid()"),
        (160, "TGID 5301", "уся група потоків — getpid()"),
        (250, "PGID 5301", "група процесів — kill(-5301)"),
        (340, "SID 5290", "сеанс термінала"),
    ]
    for y, head, sub in rows:
        f.append(fitbox(520, y, 380, 64, head + "\n" + sub, size=14))
        f.append(arrow(305, 250, 512, y + 32))
    f.append(fitbox(70, 410, 380, 64, "з боку хоста\nPID 51234", size=14, fill="#eef3fd", stroke=NEG))
    f.append(fitbox(520, 410, 380, 64, "усередині контейнера\nPID 1", size=14, fill="#eef3fd", stroke=NEG))
    f.append(line(455, 442, 512, 442, color=NEG, sw=1.6, dash="6 4"))
    render(os.path.join(OUT, 'one-task-many-names.svg'), W, H, *f,
           title="Одна задача — кілька чисел")


def fig_sign():
    """Знак одного числового аргументу вибирає адресата (для api-довідки)."""
    W, H = 1060, 416
    cols = [(40, 190), (246, 400), (662, 360)]
    f = []
    heads = ["значення pid", "kill(pid, sig)", "waitpid(pid, …)"]
    for (x, w), s in zip(cols, heads):
        f.append(fitbox(x, 46, w, 44, s, size=14, bold=True, fill="#e6edf7"))
    rows = [
        ("pid > 0", "процес із таким PID",
         "чекати саме на цю дитину"),
        ("pid == 0", "уся група процесів відправника",
         "будь-яка дитина з групи відправника"),
        ("pid == −1", "усі, кому дозволено; крім PID 1 і себе",
         "будь-яка дитина"),
        ("pid < −1", "уся група процесів із номером −pid",
         "будь-яка дитина з групи −pid"),
    ]
    ys = [104, 176, 248, 320]
    for y, (a, b, c) in zip(ys, rows):
        f.append(fitbox(cols[0][0], y, cols[0][1], 62, a, size=14, bold=True,
                        fill="#eef3fd", stroke=NEG))
        f.append(fitbox(cols[1][0], y, cols[1][1], 62, b, size=13))
        f.append(fitbox(cols[2][0], y, cols[2][1], 62, c, size=13))
    render(os.path.join(OUT, 'pid-argument-sign.svg'), W, H, *f,
           title="Одне поле pid_t, чотири різні адресати")


def fig_pidfd_versions():
    """Коли який шматок pidfd-інтерфейсу зʼявився в ядрі."""
    W, H = 1080, 360
    f = []
    f.append(arrow(60, 200, 1040, 200, color=MUTED, sw=2))
    items = [
        (130, "Linux 5.1\npidfd_send_signal()", 150),
        (265, "Linux 5.2\nCLONE_PIDFD", 252),
        (400, "Linux 5.3\npidfd_open(), clone3()", 95),
        (535, "Linux 5.4\nwaitid(P_PIDFD)", 310),
        (680, "Linux 5.6\npidfd_getfd()", 150),
        (830, "Linux 5.10\nPIDFD_NONBLOCK", 252),
        (975, "Linux 6.9\nPIDFD_THREAD\nPIDFD_SIGNAL_*", 95),
    ]
    for x, s, y in items:
        b, w, h = textbox(x, y, s, size=12, fill="#eef3fd", stroke=NEG)
        f.append(b)
        if y < 200:
            f.append(line(x, y + h / 2, x, 194, color=MUTED, sw=1.2))
        else:
            f.append(line(x, 206, x, y - h / 2, color=MUTED, sw=1.2))
        f.append(circle(x, 200, 5, fill=BG, stroke=NEG, sw=2))
    render(os.path.join(OUT, 'pidfd-versions.svg'), W, H, *f,
           title="pidfd за версіями ядра")


def fig_ceiling_history():
    """Стеля номера процесу від 1971-го: чим її задавали і яке число виходило."""
    import math
    W = 1150
    x0, colw = 40, 430          # епоха + механізм
    xn, numw = 486, 160         # число
    xb, barw = 668, 442         # смуга
    rows = [
        ("Unix V1, 1971", "inc mpid — жодної перевірки", "стелі нема", None),
        ("Unix V6, 1975", "if (mpid < 0) — знакове слово", "32767", 32767),
        ("Unix V7, 1979", "if (mpid >= 30000)", "30000", 30000),
        ("Linux 2.4, 2001", "маска 0xffff8000, низ 300", "32768", 32768),
        ("Linux 2.6+, 2003", "sysctl pid_max, стеля PID_MAX_LIMIT", "4194304", 4194304),
        ("абсолютна межа", "FUTEX_TID_MASK — 30 біт на номер", "1073741824", 1073741824),
    ]
    top, rh, gap = 96, 66, 14
    H = top + len(rows) * (rh + gap) + 66
    f = []
    heads = [(x0, colw, "епоха й спосіб задати стелю"),
             (xn, numw, "верхня межа"),
             (xb, barw, "розмір простору номерів (шкала логарифмічна)")]
    for x, w, s in heads:
        f.append(fitbox(x, 40, w, 40, s, size=13, bold=True, fill="#e6edf7"))
    kpx = 300.0 / (math.log10(1073741824) - 4.0)
    for i, (era, how, num, val) in enumerate(rows):
        y = top + i * (rh + gap)
        last = (i == len(rows) - 1)
        col = POS if last else NEG
        f.append(fitbox(x0, y, colw, rh, era + "\n" + how, size=13,
                        fill="#eef3fd" if not last else "#fdecea", stroke=col))
        f.append(fitbox(xn, y, numw, rh, num, size=14, bold=True))
        if val is None:
            f.append(line(xb, y + rh / 2, xb + 130, y + rh / 2,
                          color=MUTED, sw=1.6, dash="7 5"))
            f.append(text(xb + 142, y + rh / 2 + 5, "лічильник мовчки переповнювався",
                          size=12, color=MUTED, anchor="start"))
        else:
            w = max(8, (math.log10(val) - 4.0) * kpx)
            f.append(rect(xb, y + rh / 2 - 11, w, 22,
                          fill="#eef3fd" if not last else "#fdecea", stroke=col, sw=1.4, rx=3))
    f.append(text(W / 2, H - 26,
                  "Стеля жодного разу не була обрана «з голови»: спершу її задавало"
                  " переповнення слова, потім — сумісність зі старим числом.",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'pid-ceiling-history.svg'), W, H, *f,
           title="Як росла стеля номера процесу")


def fig_supervisor_loop():
    """Один цикл подій: команди й смерть дитини приходять однаково (для proj-розбору)."""
    W, H = 1080, 470
    f = []
    left = [
        (90, "керівний сокет\nAF_UNIX SOCK_DGRAM"),
        (210, "pidfd дитини\nCLONE_PIDFD"),
        (330, "дедлайн зупинки\n(timeout epoll_wait)"),
    ]
    for y, s in left:
        f.append(fitbox(30, y, 250, 72, s, size=14))
    f.append(fitbox(380, 185, 270, 110, "epoll_wait()\nодна черга на все",
                    size=15, bold=True, fill="#e6edf7"))
    right = [
        (90, "команда «stop»\npidfd_send_signal(SIGTERM)", NEG),
        (210, "EPOLLIN: дитина — зомбі\nwaitid(P_PIDFD) → код виходу", FIELD),
        (330, "час вийшов\npidfd_send_signal(SIGKILL)", POS),
    ]
    for y, s, st in right:
        f.append(fitbox(730, y, 320, 72, s, size=14, stroke=st))
    f.append(arrow(285, 126, 375, 215))
    f.append(arrow(285, 246, 375, 240))
    f.append(arrow(285, 366, 375, 265))
    f.append(arrow(655, 215, 725, 126))
    f.append(arrow(655, 240, 725, 246))
    f.append(arrow(655, 265, 725, 366))
    f.append(text(540, 445, "обробника сигналу немає взагалі: смерть дитини — "
                            "така сама подія, як байти з сокета",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'pidfd-supervisor-loop.svg'), W, H, *f,
           title="Наглядач на pidfd: усе в одному циклі подій")


def fig_stop_escalation():
    """Стани зупинки й два дедлайни (для proj-розбору)."""
    W, H = 1120, 390
    f = []
    states = [
        (110, "ЖИВЕ", True, LINE),
        (400, "ЗУПИНЯЄМО\nдедлайн +5 с", False, NEG),
        (720, "ДОБИВАЄМО\nдедлайн +2 с", False, POS),
        (1000, "ПРИБРАНО", True, FIELD),
    ]
    for cx, s, bold, st in states:
        b, _, _ = textbox(cx, 180, s, size=14, bold=bold, stroke=st)
        f.append(b)
    f.append(arrow(143, 180, 338, 180))
    f.append(arrow(462, 180, 658, 180))
    f.append(arrow(782, 180, 951, 180))
    f.append(mtext(240, 118, "команда «stop»\npidfd_send_signal(SIGTERM)", size=12))
    f.append(mtext(560, 118, "дедлайн вичерпано\npidfd_send_signal(SIGKILL)", size=12))
    f.append(mtext(866, 118, "EPOLLIN\nwaitid(P_PIDFD)", size=12))
    # обхід: дитина вийшла сама під час пільги
    f.append(line(400, 205, 400, 290, color=FIELD, sw=1.6, dash="7 5"))
    f.append(line(400, 290, 1000, 290, color=FIELD, sw=1.6, dash="7 5"))
    f.append(arrow(1000, 290, 1000, 208, color=FIELD))
    f.append(text(700, 276, "вийшла сама під час пільги: EPOLLIN → waitid(P_PIDFD)",
                  size=12, color=FIELD))
    f.append(text(560, 350, "SIGKILL не можна проігнорувати — але дитина в стані D "
                            "піде лише тоді, коли ядро її відпустить",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'pidfd-stop-escalation.svg'), W, H, *f,
           title="Зупинка щаблями: два дедлайни й одна подія на вихід")


fig_ring()
fig_tree()
fig_race()
fig_names()
fig_sign()
fig_pidfd_versions()
fig_ceiling_history()
fig_supervisor_loop()
fig_stop_escalation()
print("ok")
