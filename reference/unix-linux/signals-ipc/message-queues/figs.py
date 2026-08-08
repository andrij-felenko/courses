# -*- coding: utf-8 -*-
"""Фігури до теми «Черги повідомлень»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

WHITE = "#ffffff"
RED_F = "#fdecea"
BLUE_F = "#eaf0fd"
GREEN_F = "#eaf6ec"


def fig_stream_vs_records():
    """Потік байтів без меж проти списку записів із довжиною й рангом."""
    W, H = 920, 470
    b = []

    # --- канал ---
    b.append(text(50, 44, "канал — суцільний потік байтів", size=15, anchor="start", bold=True))
    b.append(rect(50, 62, 820, 52, fill=WHITE))
    b.append(text(460, 94, "3C 11 A7 04 21 09 5E 00 7F 2A B3 44 10 08 C1 6D 92 0F",
                  size=13, color=MUTED))

    for x in (330, 610):
        b.append(line(x, 114, x, 136, color=MUTED, dash="4,4"))
    b.append(text(330, 156, "тут відправник закінчив перший запис", size=12, color=MUTED))
    b.append(text(610, 190, "а тут другий — у самих байтах цього немає", size=12, color=MUTED))

    # --- черга ---
    b.append(text(50, 258, "черга — список окремих записів", size=15, anchor="start", bold=True))
    b.append(text(50, 284, "порядок надходження →", size=12, anchor="start", color=MUTED))

    chips = [
        ("«оновити налаштування»\n41 байт · ранг 1", BLUE_F),
        ("«знімок стану»\n12 байтів · ранг 1", BLUE_F),
        ("«спинися»\n8 байтів · ранг 9", RED_F),
    ]
    x = 50
    for s_, fillc in chips:
        b.append(fitbox(x, 300, 210, 72, s_, size=12, fill=fillc))
        x += 226

    b.append(fitbox(740, 300, 130, 72, "приймач", size=13, fill=GREEN_F))
    b.append(arrow(712, 336, 736, 336))

    b.append(text(163, 400, "лежать далі — ранг нижчий", size=12, color=MUTED))
    b.append(text(615, 400, "видано першим", size=12, color=POS))
    b.append(text(460, 445, "довжину й ранг зберігає ядро, тож приймач нічого не відновлює сам",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'stream-vs-records.svg'), W, H, *b)


def fig_two_disciplines():
    """Вибірка приймача (System V) проти впорядкування ядром (POSIX)."""
    W, H = 980, 500
    b = []

    panels = [
        (40, "System V", "ранг вибирає приймач", [
            ("mtype=3 · звіт", WHITE),
            ("mtype=1 · стоп", WHITE),
            ("mtype=3 · звіт", WHITE),
            ("mtype=2 · знімок", WHITE),
        ], [
            (96, "msgrcv(msgtyp=3)", BLUE_F, 0),
            (200, "msgrcv(msgtyp=−2)", RED_F, 1),
        ], "черга однорідна; хто що забере,\nвирішує аргумент msgtyp"),
        (540, "POSIX", "ранг задає відправник", [
            ("prio=9 · стоп", RED_F),
            ("prio=5 · знімок", WHITE),
            ("prio=1 · звіт", WHITE),
            ("prio=1 · звіт", WHITE),
        ], [
            (96, "mq_receive()", GREEN_F, 0),
        ], "ядро тримає чергу впорядкованою;\nприймач бере лише верх"),
    ]

    for px, title, sub, chips, readers, note in panels:
        b.append(text(px + 200, 40, title, size=16, bold=True))
        b.append(text(px + 200, 66, sub, size=12, color=MUTED))

        y = 92
        centers = []
        for s_, fillc in chips:
            b.append(fitbox(px, y, 230, 44, s_, size=12, fill=fillc))
            centers.append(y + 22)
            y += 52

        for ry, label, fillc, target in readers:
            b.append(fitbox(px + 280, ry, 160, 44, label, size=12, fill=fillc))
            b.append(arrow(px + 276, ry + 22, px + 236, centers[target]))

        b.append(fitbox(px, 330, 440, 66, note, size=12, fill=FILL))

    b.append(text(490, 448, "надходять ті самі чотири повідомлення — різниться лише те, "
                            "хто визначає порядок видачі", size=12, color=MUTED))
    b.append(text(490, 476, "вибірка дає ще й адресацію: тип може означати не важливість, "
                            "а того, кому призначено", size=12, color=MUTED))

    render(os.path.join(OUT, 'two-disciplines.svg'), W, H, *b)


def fig_notify_order():
    """Чому реєстрація має передувати вичерпуванню."""
    W, H = 980, 450
    b = []
    XS = (170, 400, 630, 855)

    rows = [
        (40, 150, "хибний порядок", [
            ("вичерпали чергу\n(порожньо)", WHITE),
            ("надійшло\nповідомлення", RED_F),
            ("mq_notify()\n— запізно", WHITE),
            ("sigsuspend()\nсон назавжди", RED_F),
        ], (500, 196, "край «порожньо → непорожньо» пройшов, коли сторожа ще не було", POS)),
        (240, 350, "правильний порядок", [
            ("mq_notify()", BLUE_F),
            ("вичерпали\nдо EAGAIN", WHITE),
            ("надійшло\nповідомлення", WHITE),
            ("сигнал →\nпрокинулися", GREEN_F),
        ], (500, 396, "сторож стоїть від самого початку, тож край нікуди не подівся", MUTED)),
    ]

    for ytitle, yline, title, boxes, note in rows:
        b.append(text(40, ytitle, title, size=15, anchor="start", bold=True))
        b.append(line(90, yline, 940, yline, color=MUTED))
        for x, (s_, fillc) in zip(XS, boxes):
            b.append(fitbox(x - 85, yline - 78, 170, 60, s_, size=12, fill=fillc))
            b.append(line(x, yline - 16, x, yline - 4, color=MUTED))
        nx, ny, ns, nc = note
        b.append(text(nx, ny, ns, size=12, color=nc))

    b.append(text(490, 435, "час →", size=12, color=MUTED))
    render(os.path.join(OUT, 'notify-order.svg'), W, H, *b)


def fig_dispatch_stages():
    """Диспетчер: де живе протитиск, а де — справедливість."""
    W, H = 1040, 470
    b = []

    b.append(text(520, 40, "шлях розпорядження крізь службу", size=16, bold=True))

    stages = [
        (40, 170, "виробники\nmq_timedsend()", BLUE_F),
        (280, 200, "черга в ядрі\nmq_maxmsg слотів\nвидача за рангом", WHITE),
        (570, 190, "дві полиці\nпо 8 записів\nтермінові · рутинні", GREEN_F),
        (850, 150, "диспетчер\nквота 4 : 1", RED_F),
    ]
    for x, w, s_, fillc in stages:
        b.append(fitbox(x, 84, w, 116, s_, size=13, fill=fillc))

    b.append(arrow(214, 142, 274, 142))
    b.append(arrow(484, 142, 564, 142))
    b.append(arrow(764, 142, 844, 142))

    notes = [
        (280, 200, 380, "черга повна →\nвідправник дістає EAGAIN\nі гальмує сам"),
        (560, 210, 665, "полиця мала НАВМИСНО:\nбільша полиця осушує чергу\nй протитиску не лишається"),
        (825, 200, 925, "після чотирьох термінових\nодне рутинне йде поза\nчергою — і не голодує"),
    ]
    for x, w, cx, s_ in notes:
        b.append(line(cx, 202, cx, 246, color=MUTED, dash="4,4"))
        b.append(fitbox(x, 250, w, 84, s_, size=12, fill=FILL))

    b.append(text(380, 372, "протитиск", size=14, bold=True, color=POS))
    b.append(text(665, 372, "місце, де його легко втратити", size=13, color=MUTED))
    b.append(text(925, 372, "справедливість", size=14, bold=True, color=NEG))

    b.append(text(520, 428, "ядро впорядковує за рангом, але від голодування не рятує; "
                            "процес додає справедливість —", size=12, color=MUTED))
    b.append(text(520, 452, "і мусить при цьому не зруйнувати протитиск, "
                            "заради якого черга й має стелю", size=12, color=MUTED))

    render(os.path.join(OUT, 'dispatch-stages.svg'), W, H, *b)


fig_stream_vs_records()
fig_two_disciplines()
fig_notify_order()
fig_dispatch_stages()
print("ok")
