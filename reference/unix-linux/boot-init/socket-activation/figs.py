# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff1"


# ── 1. Хто створює сокет — той і визначає, чи буде відмова ──────────────────
def fig_ordering():
    W, H = 1460, 900
    p = []

    nx, nw = 40, 330
    tx, tw = 400, 900
    T = 6.0
    sx = tw / T
    rh, gap = 56, 20

    def axis(ay):
        p.append(line(tx, ay, tx + tw, ay, color=MUTED, sw=1.4))
        for s in range(0, 7):
            p.append(line(tx + s * sx, ay, tx + s * sx, ay + 7, color=MUTED, sw=1.2))
            p.append(text(tx + s * sx, ay + 26, "%d c" % s, size=12, color=MUTED))

    def knock(y0, y1, tmark, label, color):
        x = tx + tmark * sx
        p.append(line(x, y0, x, y1, color=color, sw=2, dash="6 5"))
        p.append(text(x, y0 - 12, label, size=13, color=color, bold=True))

    # ── панель А: сокет створює сама служба ────────────────────────────────
    p.append(text(nx, 70, "Сокет створює сама служба", size=17, bold=True, anchor="start"))

    y = 132
    p.append(fitbox(nx, y, nw, rh, "процес бази стартує", size=14, fill=GREY_FILL,
                    stroke=MUTED, sw=1.3))
    p.append(fitbox(tx + 0.3 * sx, y + 8, 2.5 * sx, rh - 16,
                    "читає налаштування, відкриває файли", size=12,
                    fill=BLUE_FILL, stroke=NEG, sw=1.4, color=MUTED))
    ya_top = y
    y += rh + gap

    p.append(fitbox(nx, y, nw, rh, "сокет :5432 слухає", size=14, fill=GREY_FILL,
                    stroke=MUTED, sw=1.3))
    p.append(fitbox(tx + 2.8 * sx, y + 8, 3.2 * sx, rh - 16,
                    "socket · bind · listen — аж тепер", size=12,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.4, color=MUTED))
    ya_bot = y + rh

    knock(ya_top - 16, ya_bot + 16, 1.0, "клієнт стукає", POS)
    axis(ya_bot + 20)

    p.append(fitbox(nx, ya_bot + 62, 1260, 58,
                    "На порту немає слухача — ядро відповідає відмовою. "
                    "Клієнт мусить або впасти, або перепитувати.",
                    size=14, fill=RED_FILL, stroke=POS, sw=1.4))

    # ── панель Б: сокет створює менеджер наперед ───────────────────────────
    p.append(text(nx, 470, "Сокет створює менеджер наперед", size=17, bold=True, anchor="start"))

    y = 532
    p.append(fitbox(nx, y, nw, rh, "сокет :5432 слухає", size=14, fill=GREY_FILL,
                    stroke=MUTED, sw=1.3))
    p.append(fitbox(tx + 0.1 * sx, y + 8, 5.9 * sx, rh - 16,
                    "менеджер створив його ще до першої служби", size=12,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.4, color=MUTED))
    yb_top = y
    y += rh + gap

    p.append(fitbox(nx, y, nw, rh, "процес бази стартує", size=14, fill=GREY_FILL,
                    stroke=MUTED, sw=1.3))
    p.append(fitbox(tx + 1.0 * sx, y + 8, 2.5 * sx, rh - 16,
                    "піднявся на першому з'єднанні", size=12,
                    fill=BLUE_FILL, stroke=NEG, sw=1.4, color=MUTED))
    yb_bot = y + rh

    knock(yb_top - 16, yb_bot + 16, 1.0, "клієнт стукає", FIELD)
    axis(yb_bot + 20)

    p.append(fitbox(nx, yb_bot + 62, 1260, 58,
                    "З'єднання стає в чергу ядра, запит лягає в буфер приймання. "
                    "Клієнт нічого не помічає — він просто чекає на відповідь.",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, 'ordering-dissolved.svg'), W, H, *p)


# ── 2. Як дескриптор доходить від менеджера до служби ───────────────────────
def fig_fd_handover():
    W, H = 1520, 700
    p = []

    cw = 430
    c1, c2, c3 = 40, 545, 1050
    sh, sgap = 74, 16

    p.append(fitbox(c1, 60, cw, 46, "менеджер, він же PID 1", size=16, bold=True,
                    fill=BLUE_FILL, stroke=NEG, sw=1.4))
    p.append(fitbox(c2, 60, cw, 46, "нащадок після fork, ще до exec", size=16, bold=True,
                    fill=WARM_FILL, stroke=MUTED, sw=1.4))
    p.append(fitbox(c3, 60, cw, 46, "служба після exec", size=16, bold=True,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.4))

    left = [
        "fd = socket(AF_INET, SOCK_STREAM)",
        "bind(fd, :80)\nпорт нижче 1024 — а менеджер працює від root",
        "listen(fd, backlog)\nз цієї миті ядро приймає з'єднання в чергу",
        "fork()\nтаблиця дескрипторів копіюється в нащадка",
    ]
    mid = [
        "dup2(fd, 3)\nсокет переставлено на місце з номером 3",
        "зняти FD_CLOEXEC\nінакше exec його закриє",
        "LISTEN_FDS=1\nLISTEN_PID=<номер цього процесу>\nLISTEN_FDNAMES=http.socket",
        "execve(\"/usr/sbin/web\", …)",
    ]

    y = 136
    for a, b in zip(left, mid):
        p.append(fitbox(c1, y, cw, sh, a, size=13, fill="#ffffff", stroke=MUTED, sw=1.2))
        p.append(fitbox(c2, y, cw, sh, b, size=13, fill="#ffffff", stroke=MUTED, sw=1.2))
        y += sh + sgap

    p.append(arrow(c1 + cw + 12, 136 + 3 * (sh + sgap) + sh / 2,
                   c2 - 12, 136 + sh / 2, color=NEG))
    p.append(arrow(c2 + cw + 12, y - sgap - sh / 2, c3 - 12, 300, color=FIELD))

    # таблиця дескрипторів служби
    rows = [
        ("0", "/dev/null або журнал", GREY_FILL),
        ("1", "журнал", GREY_FILL),
        ("2", "журнал", GREY_FILL),
        ("3", "той самий сокет: прив'язаний, слухає", GREEN_FILL),
    ]
    ty = 136
    for num, what, fill in rows:
        p.append(fitbox(c3, ty, 60, 58, num, size=16, bold=True, fill="#ffffff",
                        stroke=MUTED, sw=1.2))
        p.append(fitbox(c3 + 70, ty, cw - 70, 58, what, size=13, fill=fill,
                        stroke=MUTED, sw=1.2))
        ty += 58 + 12

    p.append(fitbox(c3, ty + 20, cw, 92,
                    "socket, bind і listen служба не викликає взагалі.\n"
                    "Її перша дія з мережею — accept(3, …).",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, 'fd-handover.svg'), W, H, *p)


# ── 3. Два способи роздати роботу: сокет чи вже прийняте з'єднання ──────────
def fig_accept_modes():
    W, H = 1500, 720
    p = []

    lx, rx, pw = 40, 780, 680

    p.append(fitbox(lx, 56, pw, 50, "Accept=no — віддають сокет, що слухає",
                    size=16, bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.4))
    p.append(fitbox(rx, 56, pw, 50, "Accept=yes — віддають уже прийняте з'єднання",
                    size=16, bold=True, fill=WARM_FILL, stroke=MUTED, sw=1.4))

    # ліва панель
    p.append(fitbox(lx + 80, 140, pw - 160, 62,
                    "сокет :80, що слухає", size=15, fill=GREEN_FILL, stroke=FIELD, sw=1.4))
    p.append(arrow(lx + pw / 2, 208, lx + pw / 2, 258, color=NEG))
    p.append(text(lx + pw / 2 + 14, 236, "переданий як fd 3", size=13,
                  color=MUTED, anchor="start"))
    p.append(fitbox(lx + 80, 264, pw - 160, 78,
                    "один процес служби\naccept(3) у циклі — усі з'єднання його",
                    size=14, fill=BLUE_FILL, stroke=NEG, sw=1.4))

    for i, cx in enumerate([lx + 150, lx + 340, lx + 530]):
        p.append(fitbox(cx - 75, 470, 150, 54, "з'єднання %d" % (i + 1), size=13,
                        fill="#ffffff", stroke=MUTED, sw=1.2))
        p.append(arrow(cx, 466, lx + pw / 2, 348, color=MUTED))

    p.append(fitbox(lx, 570, pw, 96,
                    "Процес один, з'єднань скільки завгодно.\n"
                    "Так влаштована будь-яка справжня служба: вебсервер, база, шина.",
                    size=13, fill=GREY_FILL, stroke=MUTED, sw=1.3))

    # права панель
    p.append(fitbox(rx + 80, 140, pw - 160, 62,
                    "сокет :80 лишається в менеджера", size=15,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.4))
    p.append(text(rx + pw / 2, 236, "accept() викликає менеджер", size=13, color=MUTED))

    for i, cx in enumerate([rx + 150, rx + 340, rx + 530]):
        p.append(arrow(rx + pw / 2, 258, cx, 316, color=MUTED))
        p.append(fitbox(cx - 90, 322, 180, 96,
                        "web@%d.service\nокремий процес\nfd 3 = це з'єднання" % (i + 1),
                        size=12, fill=WARM_FILL, stroke=MUTED, sw=1.3))

    p.append(fitbox(rx, 570, pw, 96,
                    "Процес на кожне з'єднання — і повний запуск програми на кожне.\n"
                    "Терпимо лише для рідких і дешевих справ.",
                    size=13, fill=RED_FILL, stroke=POS, sw=1.3))

    render(os.path.join(IMG, 'accept-modes.svg'), W, H, *p)


# ── 4. Що переходить межу: чотири менеджери за сорок років ─────────────────
def fig_handover_history():
    W, H = 1560, 860
    p = []

    lx, lw = 40, 250
    mx, mw = 320, 400
    ax0, ax1 = 745, 1030
    sx, sw_ = 1055, 465

    p.append(text(mx + mw / 2, 56, "що робить менеджер", size=15, bold=True, color=MUTED))
    p.append(text((ax0 + ax1) / 2, 56, "що переходить межу", size=15, bold=True, color=MUTED))
    p.append(text(sx + sw_ / 2, 56, "що дістає служба", size=15, bold=True, color=MUTED))

    rows = [
        ("inetd\n4.3BSD, 1986",
         "слухає всі порти одразу\nі САМ викликає accept()",
         ("прийняте з'єднання", "на місцях 0, 1, 2"),
         "фільтр, що читає вхід і пише вихід:\nпро мережу не знає нічого,\nодне з'єднання — один процес",
         WARM_FILL, RED_FILL),
        ("xinetd",
         "те саме + доступ за адресою,\nмежі, частота, журнал",
         ("прийняте з'єднання", "на місцях 0, 1, 2"),
         "без змін: процес на з'єднання,\nжодного стану між ними",
         WARM_FILL, RED_FILL),
        ("launchd\nMac OS X 10.4, 2005",
         "створює й ТРИМАЄ\nслухаючі сокети наперед",
         ("слухаючий сокет", "(accept() — у служби)"),
         "постійний демон: сам викликає accept(),\nтримає стан, засинає в простої,\nне потребує root для порту 80",
         BLUE_FILL, GREEN_FILL),
        ("systemd\n«Rethinking PID 1», 2010",
         "усі оголошені сокети однією порцією\nще до першої служби",
         ("слухаючі сокети", "з місця 3 і далі"),
         "те саме — плюс порядок старту\nперестає бути питанням:\nточка зустрічі є в усіх від початку",
         BLUE_FILL, GREEN_FILL),
    ]

    y0, rh, gap = 100, 150, 40
    y = y0
    for name, mgr, mid, svc, fill_m, fill_s in rows:
        p.append(fitbox(lx, y + 20, lw, rh - 40, name, size=15, bold=True,
                        fill=GREY_FILL, stroke=MUTED, sw=1.3))
        p.append(fitbox(mx, y, mw, rh, mgr, size=14, fill=fill_m, stroke=MUTED, sw=1.4))
        cx = (ax0 + ax1) / 2
        p.append(text(cx, y + rh / 2 - 24, mid[0], size=14, color=INK, bold=True))
        p.append(text(cx, y + rh / 2 - 4, mid[1], size=13, color=MUTED))
        p.append(arrow(ax0, y + rh / 2 + 30, ax1, y + rh / 2 + 30, color=MUTED, sw=2))
        p.append(fitbox(sx, y, sw_, rh, svc, size=14, fill=fill_s, stroke=MUTED, sw=1.4))
        y += rh + gap

    ybreak = y0 + 2 * (rh + gap) - gap / 2
    p.append(line(lx, ybreak, sx + sw_, ybreak, color=POS, sw=2, dash="8 6"))

    render(os.path.join(IMG, 'handover-history.svg'), W, H, *p)


# ── Від рядків юніта до масиву дескрипторів (для api-вставки) ───────────────
def fig_fd_array_map():
    W, H = 1540, 700
    p = []

    lx, lw = 40, 520
    nx, nw = 790, 70
    dx, dw = 878, 600

    p.append(fitbox(lx, 60, lw, 48, "web.socket — що написано в юніті",
                    size=16, bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.4))
    p.append(fitbox(nx, 60, nw + 8 + dw, 48, "що процес бачить одразу після exec",
                    size=16, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.4))

    rows = [
        ("ListenStream=80", "3", "TCP :80 — уже bind, уже listen"),
        ("ListenStream=443", "4", "TCP :443 — те саме"),
        ("ListenStream=/run/web.sock", "5", "AF_UNIX /run/web.sock"),
    ]

    y0, rh, gap = 150, 62, 18
    for i, (src, num, what) in enumerate(rows):
        y = y0 + i * (rh + gap)
        p.append(fitbox(lx, y, lw, rh, src, size=14, fill="#ffffff",
                        stroke=MUTED, sw=1.2))
        p.append(arrow(lx + lw + 16, y + rh / 2, nx - 16, y + rh / 2, color=NEG))
        p.append(fitbox(nx, y, nw, rh, num, size=17, bold=True, fill="#ffffff",
                        stroke=MUTED, sw=1.2))
        p.append(fitbox(dx, y, dw, rh, what, size=13, fill=GREEN_FILL,
                        stroke=FIELD, sw=1.3))

    yname = y0 + 3 * (rh + gap)
    p.append(fitbox(lx, yname, lw, rh, "FileDescriptorName=web", size=14,
                    fill=WARM_FILL, stroke=MUTED, sw=1.2))
    p.append(arrow(lx + lw + 16, yname + rh / 2, nx - 16, yname + rh + 40,
                   color=MUTED))
    p.append(fitbox(nx, yname + rh + 10, nw + 8 + dw, 76,
                    "Ім'я одне на весь юніт — усі три дескриптори звуться «web».\n"
                    "За іменем окремий сокет не знайти: імена не унікальні.",
                    size=13, fill=WARM_FILL, stroke=MUTED, sw=1.3))

    p.append(fitbox(lx, 540, W - 2 * lx, 120,
                    "LISTEN_FDS=3        LISTEN_PID=<номер процесу служби>\n"
                    "LISTEN_FDNAMES=web:web:web\n"
                    "Порядок чисел — це порядок рядків у юніті; "
                    "між різними юнітами сокетів порядок не визначено.",
                    size=14, fill=GREY_FILL, stroke=MUTED, sw=1.4))

    render(os.path.join(IMG, 'fd-array-map.svg'), W, H, *p)


fig_ordering()
fig_fd_handover()
fig_accept_modes()
fig_handover_history()
fig_fd_array_map()
print("ok")


# ── 6. Три режими старту однієї програми ────────────────────────────────────
def fig_startup_modes():
    W, H = 1200, 700
    p = []

    # старт
    p.append(fitbox(400, 30, 400, 60, "старт echod", size=16, bold=True,
                    fill=GREY_FILL, stroke=MUTED, sw=1.4))
    p.append(arrow(600, 90, 600, 128))

    # перша розвилка
    p.append(fitbox(400, 128, 400, 84,
                    "LISTEN_PID збігається\nз власним номером процесу?",
                    size=14, fill=WARM_FILL, stroke=MUTED, sw=1.6))

    # ліва гілка — сокет робимо самі
    p.append(text(300, 148, "ні, або змінних немає", size=12, color=MUTED))
    p.append(line(400, 170, 210, 170, color=LINE, sw=1.5))
    p.append(arrow(210, 170, 210, 288))
    p.append(fitbox(60, 288, 300, 84,
                    "socket · bind · listen\nпорт 9000 робимо самі",
                    size=14, fill=BLUE_FILL, stroke=NEG, sw=1.5))

    # права гілка — нам передали
    p.append(text(626, 240, "так", size=13, color=MUTED, anchor="start"))
    p.append(arrow(600, 212, 600, 288))
    p.append(fitbox(400, 288, 400, 84,
                    "LISTEN_FDS=1, дескриптор 3\nприв'язаний і готовий",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    # друга розвилка
    p.append(arrow(600, 372, 600, 424))
    p.append(fitbox(400, 424, 400, 84,
                    "SO_ACCEPTCONN каже,\nщо це слухач?",
                    size=14, fill=WARM_FILL, stroke=MUTED, sw=1.6))

    # Accept=yes — з'єднання
    p.append(text(852, 448, "ні: Accept=yes", size=12, color=MUTED))
    p.append(arrow(800, 466, 906, 466))
    p.append(fitbox(906, 424, 264, 84,
                    "це вже прийняте з'єднання:\nобслужити його й вийти",
                    size=13, fill=RED_FILL, stroke=POS, sw=1.5))

    # спільний хвіст
    p.append(text(626, 540, "так", size=13, color=MUTED, anchor="start"))
    p.append(arrow(600, 508, 600, 580))
    p.append(arrow(210, 372, 210, 580))
    p.append(fitbox(60, 580, 740, 76,
                    "цикл accept: приймаємо з'єднання одне за одним",
                    size=15, bold=True, fill=GREY_FILL, stroke=MUTED, sw=1.5))

    render(os.path.join(IMG, 'startup-modes.svg'), W, H, *p)


fig_startup_modes()
