# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

MINE = "#eaf0fd"      # твій код — холодний
MINE_S = NEG
THEIRS = "#fdecea"    # чужий код — гарячий
THEIRS_S = POS


# ── Фігура 1: сходинка інверсії ─────────────────────────────────────────────
def fig_ladder():
    W, H = 1000, 640
    rows = [
        ("Звичайний виклик", "sort(v) — керування назад одразу", "нічого", MINE, MINE_S),
        ("Зворотний виклик", "компаратор, таймер, обробник", "мить одного виклику", MINE, MINE_S),
        ("Гніздо для плагіна", "ти даєш шматки, збирає їх чужий код", "які шматки взагалі існують", FILL, LINE),
        ("Шаблонний метод", "кроки твої, послідовність — базового класу", "порядок кроків операції", FILL, LINE),
        ("Каркас із run()", "точку входу пише він, ти — обробники", "вхід у програму й життєвий цикл", THEIRS, THEIRS_S),
        ("Платформа", "serverless, мобільна ОС, браузер", "сам процес і його розгортання", THEIRS, THEIRS_S),
    ]
    frags = [text(W / 2, 36, "Скільки саме керування віддано", size=19, bold=True)]
    frags.append(text(310, 72, "Сходинка", size=15, bold=True, color=MUTED))
    frags.append(text(760, 72, "Що вже не твоє", size=15, bold=True, color=MUTED))

    y0 = 100
    step = 86
    frags.append(text(52, 86, "глибше", size=12, color=MUTED))
    frags.append(arrow(52, 104, 52, y0 + 5 * step + 64, color=MUTED, sw=2))

    for i, (name, ex, lost, fill, stroke) in enumerate(rows):
        y = y0 + i * step
        frags.append(fitbox(100, y, 420, 64, [name, ex], size=15,
                            fill=fill, stroke=stroke, sw=2))
        frags.append(fitbox(570, y, 370, 64, lost, size=15,
                            fill="#ffffff", stroke=MUTED, sw=1.5))
    render(os.path.join(OUT, 'inversion-ladder.svg'), W, H, *frags)


# ── Фігура 2: бібліотеки складаються, каркаси — ні ───────────────────────────
def fig_two_owners():
    W, H = 1020, 560
    frags = []

    # ── ліва панель ──
    frags.append(rect(30, 56, 450, 470, fill="#ffffff", stroke=MUTED, sw=1.5))
    frags.append(text(255, 88, "Бібліотеки складаються", size=17, bold=True, color=MINE_S))

    frags.append(fitbox(60, 130, 130, 300, ["твій main", "", "цикл — твій"],
                        size=15, fill=MINE, stroke=MINE_S, sw=2))

    libs = [("бібліотека логів", 150), ("HTTP-клієнт", 250), ("розбір JSON", 350)]
    for label, y in libs:
        frags.append(fitbox(280, y, 170, 60, label, size=14, fill=FILL, stroke=LINE, sw=1.5))
        frags.append(arrow(192, y + 20, 276, y + 20, color=MINE_S))
        frags.append(arrow(276, y + 44, 192, y + 44, color=MUTED))
    frags.append(text(255, 470, "кличеш ти — керування щоразу вертається", size=13, color=MUTED))
    frags.append(text(255, 496, "скільки завгодно бібліотек в одній програмі", size=13, color=MUTED))

    # ── права панель ──
    frags.append(rect(540, 56, 450, 470, fill="#ffffff", stroke=MUTED, sw=1.5))
    frags.append(text(765, 88, "Каркаси змагаються", size=17, bold=True, color=THEIRS_S))

    frags.append(fitbox(575, 118, 170, 58, "каркас A: run()", size=14,
                        fill=THEIRS, stroke=THEIRS_S, sw=2))
    frags.append(fitbox(785, 118, 170, 58, "каркас B: run()", size=14,
                        fill=THEIRS, stroke=THEIRS_S, sw=2))

    frags.append(fitbox(600, 226, 330, 50, "головний потік процесу", size=15,
                        fill=FILL, stroke=LINE, sw=2))
    frags.append(arrow(660, 180, 700, 222, color=THEIRS_S))
    frags.append(line(872, 180, 846, 205, color=MUTED, sw=2, dash="6 5"))
    frags.append(text(900, 232, "трон уже зайнято", size=13, color=THEIRS_S))

    frags.append(text(765, 306, "господар лише один — другий стає гостем:", size=13, color=MUTED))
    shims = [("крок гостя у простої господаря", 322),
             ("свій потік + черга передач", 372),
             ("спільне очікування дескрипторів", 422)]
    for label, y in shims:
        frags.append(fitbox(600, y, 330, 42, label, size=14, fill="#ffffff", stroke=MUTED, sw=1.5))

    render(os.path.join(OUT, 'two-owners.svg'), W, H, *frags)


# ── Фігура 3: глибина проникнення й ціна виходу ─────────────────────────────
def fig_penetration():
    W, H = 1020, 600
    frags = []

    # ── ліворуч: каркас на краю ──
    frags.append(text(260, 40, "Каркас на краю", size=17, bold=True, color=MINE_S))
    frags.append(rect(50, 60, 420, 420, fill="#ffffff", stroke=THEIRS_S, sw=2))
    frags.append(text(260, 96, "каркас гукає тільки адаптери", size=14, color=THEIRS_S))

    for cx in (140, 260, 380):
        frags.append(fitbox(cx - 55, 120, 110, 48, "адаптер", size=14,
                            fill=THEIRS, stroke=THEIRS_S, sw=1.5))
        frags.append(arrow(cx, 176, cx, 234, color=THEIRS_S))

    frags.append(rect(80, 240, 360, 210, fill=MINE, stroke=MINE_S, sw=2.5))
    frags.append(mtext(260, 300, ["Домен", "звичайні функції й типи",
                                  "жодного чужого імені всередині"],
                       size=15, color=INK))
    frags.append(text(260, 400, "кличеться з тесту в п'ять рядків", size=13, color=MUTED))

    frags.append(text(260, 512, "перетинів у ядро: 3 · чужих типів у ядрі: 0", size=14, bold=True))
    frags.append(text(260, 542, "щоб піти — переписати три адаптери", size=13, color=MUTED))

    # ── праворуч: каркас усередині ──
    frags.append(text(760, 40, "Каркас усередині", size=17, bold=True, color=THEIRS_S))
    frags.append(rect(550, 60, 420, 420, fill="#ffffff", stroke=THEIRS_S, sw=2))
    frags.append(text(760, 96, "каркас гукає прямо в домен", size=14, color=THEIRS_S))

    for cx in (590, 640, 690, 740, 790, 840, 890):
        frags.append(arrow(cx, 120, cx, 174, color=THEIRS_S, sw=1.5))

    frags.append(rect(575, 180, 370, 270, fill=MINE, stroke=MINE_S, sw=2.5))
    frags.append(text(760, 212, "домен, у якому оселився каркас", size=15, color=INK))

    for label, cx in (("Request", 650), ("Session", 760), ("ORM-клас", 875)):
        b, _, _ = textbox(cx, 268, label, size=13, fill=THEIRS, stroke=THEIRS_S, sw=1.5)
        frags.append(b)

    frags.append(text(760, 336, "чужі типи в кожній сигнатурі", size=13, color=MUTED))
    frags.append(text(760, 366, "поведінка залежить від його версії", size=13, color=MUTED))
    frags.append(text(760, 410, "тест = підняти весь каркас", size=13, color=MUTED))

    frags.append(text(760, 512, "перетинів у ядро: десятки", size=14, bold=True))
    frags.append(text(760, 542, "щоб піти — правити майже кожен файл", size=13, color=MUTED))

    render(os.path.join(OUT, 'penetration.svg'), W, H, *frags)


# ── Фігура 4 (вставка proj-two-faces): одне ядро — два обличчя ───────────────
def fig_two_faces():
    W, H = 1060, 550
    frags = []

    # ── ліва колонка: бібліотечне обличчя ──
    frags.append(rect(30, 56, 330, 380, fill="#ffffff", stroke=MINE_S, sw=1.5))
    frags.append(text(195, 80, "Бібліотечне обличчя", size=15, bold=True, color=MINE_S))
    left = [
        ["1. зібрати pollfd:", "свої fd + watches() ядра"],
        ["2. timeout — ближчий із двох:", "свій дедлайн і next_deadline()"],
        ["3. poll(...) — чекаєш ТИ"],
        ["4. core.step(now, ready)"],
        ["5. take_event() → обробник"],
    ]
    for i, lines in enumerate(left):
        y = 100 + i * 66
        frags.append(fitbox(50, y, 290, 56, lines, size=13, fill=MINE, stroke=MINE_S, sw=1.5))
        if i < 4:
            frags.append(arrow(195, y + 56, 195, y + 64, color=MINE_S, sw=1.5))

    # ── права колонка: каркасне обличчя ──
    frags.append(rect(700, 56, 330, 380, fill="#ffffff", stroke=THEIRS_S, sw=1.5))
    frags.append(text(865, 80, "Каркасне обличчя: run()", size=15, bold=True, color=THEIRS_S))
    right = [
        ["1. run() збирає pollfd", "з watches() ядра"],
        ["2. timeout = next_deadline()"],
        ["3. poll(...) — чекає run()"],
        ["4. core.step(now, ready)"],
        ["5. take_event() → обробник,", "який ти передав у run()"],
    ]
    for i, lines in enumerate(right):
        y = 100 + i * 66
        frags.append(fitbox(720, y, 290, 56, lines, size=13, fill=THEIRS, stroke=THEIRS_S, sw=1.5))
        if i < 4:
            frags.append(arrow(865, y + 56, 865, y + 64, color=THEIRS_S, sw=1.5))

    # ── ядро посередині ──
    frags.append(rect(380, 56, 300, 380, fill=FILL, stroke=LINE, sw=2.5))
    frags.append(text(530, 84, "ЯДРО — бібліотека", size=15, bold=True))
    api = [
        "add(now, ціль, дані) → Id",
        "step(now, ready)",
        "next_deadline() → час?",
        "watches() / generation()",
        "take_event() → Event?",
        "cancel(id)",
    ]
    for i, m in enumerate(api):
        frags.append(fitbox(398, 104 + i * 40, 264, 34, m, size=13,
                            fill="#ffffff", stroke=MUTED, sw=1.2))
    frags.append(mtext(530, 372, ["жодного циклу й sleep;", "годинник приходить аргументом"],
                       size=12, color=MUTED))

    # ── обидві колонки кличуть ті самі методи ──
    frags.append(line(195, 440, 195, 466, color=MUTED, sw=1.5))
    frags.append(line(865, 440, 865, 466, color=MUTED, sw=1.5))
    frags.append(line(195, 466, 865, 466, color=MUTED, sw=1.5))
    frags.append(arrow(530, 466, 530, 440, color=MUTED, sw=1.8))

    frags.append(text(530, 500, "Оболонку run() можна написати ЗЗОВНІ — самим лише публічним заголовком ядра.",
                      size=14, bold=True))
    frags.append(text(530, 524, "Якщо не можна — бібліотечне обличчя неповне.",
                      size=13, color=MUTED))

    render(os.path.join(OUT, 'two-faces.svg'), W, H, *frags)


# ── Фігура 5 (вставка proj-two-faces): черга подій проти дзвінка зсередини ────
def fig_event_queue():
    W, H = 1000, 520
    frags = []

    # ── згори: обробник кличуть зсередини step() ──
    frags.append(rect(30, 56, 940, 190, fill="#ffffff", stroke=THEIRS_S, sw=1.5))
    frags.append(text(500, 84, "Обробник кличуть ЗСЕРЕДИНИ step()", size=16, bold=True, color=THEIRS_S))

    frags.append(fitbox(60, 110, 170, 60, "цикл господаря", size=14, fill=FILL, stroke=LINE))
    frags.append(arrow(234, 140, 296, 140, color=LINE))
    frags.append(fitbox(300, 110, 220, 60, ["step()", "обходить свої запити"],
                        size=14, fill=THEIRS, stroke=THEIRS_S, sw=2))
    frags.append(arrow(524, 140, 586, 140, color=THEIRS_S))
    frags.append(fitbox(590, 110, 190, 60, "твій обробник", size=14, fill=MINE, stroke=MINE_S, sw=2))

    frags.append(line(685, 170, 685, 202, color=POS, sw=2))
    frags.append(line(685, 202, 410, 202, color=POS, sw=2))
    frags.append(arrow(410, 202, 410, 172, color=POS, sw=2))
    frags.append(text(500, 228, "cancel() з обробника міняє контейнер, який step() саме обходить",
                      size=13, color=POS))

    # ── знизу: обробника кличе власник циклу, після step() ──
    frags.append(rect(30, 272, 940, 220, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(500, 300, "Обробника кличе ВЛАСНИК ЦИКЛУ — після того, як step() повернувся",
                      size=16, bold=True, color=FIELD))

    frags.append(fitbox(60, 326, 150, 60, "цикл господаря", size=13, fill=FILL, stroke=LINE))
    frags.append(arrow(214, 356, 262, 356, color=LINE))
    frags.append(fitbox(266, 326, 200, 60, ["step() — лише", "кладе події в чергу"],
                        size=13, fill=FILL, stroke=LINE))
    frags.append(arrow(470, 356, 518, 356, color=LINE))
    frags.append(fitbox(522, 326, 180, 60, ["take_event()", "— поза step()"],
                        size=13, fill=FILL, stroke=FIELD, sw=2))
    frags.append(arrow(706, 356, 754, 356, color=LINE))
    frags.append(fitbox(758, 326, 180, 60, "твій обробник", size=13, fill=MINE, stroke=MINE_S, sw=2))

    frags.append(text(500, 424, "обробник вільно кличе cancel() і add() — ядро вже не всередині свого обходу",
                      size=13, color=FIELD))
    frags.append(text(500, 452, "саме так зроблено curl_multi_info_read()", size=13, color=MUTED))

    render(os.path.join(OUT, 'event-queue.svg'), W, H, *frags)


# ── Фігура 6 (вставка proj-two-loops): хто спить — той і володіє циклом ──────
def fig_sleep_owner():
    W, H = 1100, 600
    frags = [text(W / 2, 34, "Битва двох каркасів — це битва за сон, а не за цикл",
                  size=18, bold=True)]

    ticks = [320, 420, 520, 620, 720, 820, 920, 1020]
    AX_L, AX_R = 300, 1060

    # ── ряд 1: крок гостя у простої господаря ──
    Y = 100
    frags.append(text(40, Y + 30, "1. Крок гостя у простої", size=15, bold=True, anchor="start"))
    frags.append(text(40, Y + 52, "прокидається за годинником,", size=12, color=MUTED, anchor="start"))
    frags.append(text(40, Y + 72, "період таймера T", size=12, color=MUTED, anchor="start"))
    frags.append(line(AX_L, Y + 50, AX_R, Y + 50, color=LINE, sw=2))
    for x in ticks:
        frags.append(line(x, Y + 42, x, Y + 58, color=LINE, sw=2))
    frags.append(text(320, Y + 82, "пробудження", size=11, color=MUTED))
    frags.append(arrow(545, Y + 6, 545, Y + 42, color=POS, sw=2))
    frags.append(text(545, Y - 2, "дані прийшли", size=12, color=POS))
    frags.append(circle(620, Y + 50, 6, fill=FIELD, stroke=FIELD))
    frags.append(line(545, Y + 68, 620, Y + 68, color=POS, sw=2))
    frags.append(text(700, Y + 82, "помічено аж тут", size=12, color=FIELD))
    frags.append(text(940, Y + 82, "1/T пробуджень за секунду", size=12, color=MUTED))

    # ── ряд 2: гість у власному потоці ──
    Y = 268
    frags.append(text(40, Y + 34, "2. Гість у власному потоці", size=15, bold=True, anchor="start"))
    frags.append(text(40, Y + 56, "спить своїм сном,", size=12, color=MUTED, anchor="start"))
    frags.append(text(40, Y + 76, "результат — через чергу", size=12, color=MUTED, anchor="start"))

    frags.append(text(AX_L + 8, Y + 16, "гість", size=11, color=MUTED, anchor="start"))
    frags.append(line(AX_L, Y + 28, AX_R, Y + 28, color=LINE, sw=2))
    frags.append(arrow(545, Y - 4, 545, Y + 20, color=POS, sw=2))
    frags.append(text(545, Y - 12, "дані прийшли", size=12, color=POS))
    frags.append(circle(545, Y + 28, 6, fill=FIELD, stroke=FIELD))
    frags.append(text(700, Y + 16, "гість прокинувся негайно", size=11, color=FIELD, anchor="start"))

    frags.append(text(AX_L + 8, Y + 74, "господар", size=11, color=MUTED, anchor="start"))
    frags.append(line(AX_L, Y + 88, AX_R, Y + 88, color=LINE, sw=2))
    for x in ticks:
        frags.append(line(x, Y + 82, x, Y + 94, color=LINE, sw=1.6))
    frags.append(arrow(553, Y + 36, 614, Y + 80, color=MUTED, sw=1.6))
    frags.append(circle(620, Y + 88, 6, fill=FIELD, stroke=FIELD))
    frags.append(text(700, Y + 118, "у цикл господаря — на найближчому черпанні", size=12, color=MUTED))
    frags.append(text(700, Y + 140, "є посилка в цикл (Qt, GTK, PostMessage) — негайно й без тиків",
                      size=12, color=MUTED))

    # ── ряд 3: один сон на двох ──
    Y = 452
    frags.append(text(40, Y + 30, "3. Один сон на двох", size=15, bold=True, anchor="start"))
    frags.append(text(40, Y + 52, "epoll на fd гостя", size=12, color=MUTED, anchor="start"))
    frags.append(text(40, Y + 72, "і fd господаря", size=12, color=MUTED, anchor="start"))
    frags.append(line(AX_L, Y + 50, AX_R, Y + 50, color=LINE, sw=2, dash="8 6"))
    frags.append(text(410, Y + 36, "жодного тика — сон", size=11, color=MUTED))
    frags.append(arrow(545, Y + 6, 545, Y + 42, color=POS, sw=2))
    frags.append(text(545, Y - 2, "дані прийшли", size=12, color=POS))
    frags.append(circle(545, Y + 50, 6, fill=FIELD, stroke=FIELD))
    frags.append(text(800, Y + 78, "прокинувся рівно тут: нуль зайвих пробуджень", size=12, color=FIELD))

    render(os.path.join(OUT, 'two-loops-sleep.svg'), W, H, *frags)


# ── Фігура 7 (вставка proj-two-loops): спільне очікування дескрипторів ───────
def fig_shared_wait():
    W, H = 1060, 560
    frags = [text(W / 2, 34, "Спосіб 3: один сон обслуговує обох", size=18, bold=True)]

    # ── гість віддає свої fd і свій таймер ──
    frags.append(rect(40, 70, 280, 214, fill=THEIRS, stroke=THEIRS_S, sw=2))
    frags.append(text(180, 98, "гість: libcurl multi", size=15, bold=True, color=THEIRS_S))
    frags.append(fitbox(58, 114, 244, 66, ["SOCKETFUNCTION", "«стеж за цим fd на читання»"],
                        size=12, fill="#ffffff", stroke=MUTED, sw=1.2))
    frags.append(fitbox(58, 196, 244, 66, ["TIMERFUNCTION", "«розбуди мене через 200 мс»"],
                        size=12, fill="#ffffff", stroke=MUTED, sw=1.2))
    frags.append(text(180, 306, "гість більше не спить сам", size=12, color=MUTED))

    # ── господар віддає свій дескриптор ──
    frags.append(rect(40, 330, 280, 104, fill=MINE, stroke=MINE_S, sw=2))
    frags.append(mtext(180, 366, ["господар", "ConnectionNumber(dpy)", "або власний eventfd"],
                       size=13, color=INK))

    # ── спільний набір ──
    frags.append(rect(400, 110, 240, 300, fill=FILL, stroke=LINE, sw=2.5))
    frags.append(text(520, 140, "набір epoll", size=15, bold=True))
    for label, y in (("сокети гостя", 158), ("timerfd гостя", 222), ("fd господаря", 286)):
        frags.append(fitbox(416, y, 208, 50, label, size=13, fill="#ffffff", stroke=MUTED, sw=1.2))
    frags.append(text(520, 388, "усе, чого варто чекати", size=12, color=MUTED))

    frags.append(arrow(324, 147, 394, 178, color=THEIRS_S, sw=1.8))
    frags.append(arrow(324, 229, 394, 242, color=THEIRS_S, sw=1.8))
    frags.append(arrow(324, 380, 394, 316, color=MINE_S, sw=1.8))

    # ── єдиний сон ──
    frags.append(rect(700, 148, 320, 112, fill="#ffffff", stroke=FIELD, sw=2.5))
    frags.append(mtext(860, 184, ["epoll_wait(ep, evs, n, −1)",
                                  "єдиний сон процесу",
                                  "нуль пробуджень у спокої"], size=13, color=INK))
    frags.append(arrow(644, 240, 696, 212, color=LINE, sw=1.8))

    # ── розбір ──
    frags.append(rect(700, 300, 320, 140, fill="#ffffff", stroke=MUTED, sw=1.5))
    frags.append(text(860, 328, "що прокинулось — тому й крок", size=13, color=MUTED))
    frags.append(fitbox(716, 340, 288, 44, "fd гостя → curl_multi_socket_action",
                        size=12, fill=THEIRS, stroke=THEIRS_S, sw=1.2))
    frags.append(fitbox(716, 390, 288, 44, "fd господаря → крок його циклу",
                        size=12, fill=MINE, stroke=MINE_S, sw=1.2))
    frags.append(arrow(860, 262, 860, 296, color=LINE, sw=1.8))

    frags.append(text(530, 484, "Ціна: гість мусить віддати свої fd і таймер, господар — уміти прийняти чужий fd.",
                      size=14, bold=True))
    frags.append(text(530, 512, "GLUT не вміє ні того, ні того — з ним лишаються способи 1 і 2.",
                      size=13, color=MUTED))

    render(os.path.join(OUT, 'two-loops-shared-wait.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_ladder()
    fig_two_owners()
    fig_penetration()
    fig_two_faces()
    fig_event_queue()
    fig_sleep_owner()
    fig_shared_wait()
    print("ok")
