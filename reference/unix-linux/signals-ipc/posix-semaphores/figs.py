# -*- coding: utf-8 -*-
"""Фігури до теми «Семафори POSIX: іменовані й безіменні»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_counter_vs_flag():
    """Чому сповіщення мусить рахувати, а не просто підніматися."""
    W, H = 960, 430
    b = []

    b.append(text(240, 34, "якби об'єкт був прапорцем", size=14, bold=True))
    b.append(text(720, 34, "об'єкт рахує", size=14, bold=True))

    rows_left = [
        ("виробник поклав перший елемент", "прапорець піднято"),
        ("виробник поклав другий елемент", "прапорець уже піднято — слід стерто"),
        ("споживач прокинувся, узяв один", "прапорець опущено"),
        ("другий елемент лежить, а знака про нього нема", ""),
    ]
    rows_right = [
        ("виробник поклав перший елемент", "лічильник = 1"),
        ("виробник поклав другий елемент", "лічильник = 2"),
        ("споживач прокинувся, узяв один", "лічильник = 1"),
        ("лічильник не нуль — споживач не засинає й бере другий", ""),
    ]

    y = 58
    for i, (ev, st) in enumerate(rows_left):
        fill = "#fdecea" if i == 3 else FILL
        stroke = POS if i == 3 else LINE
        s = ev if not st else ev + "\n" + st
        b.append(fitbox(30, y, 420, 72, s, size=12, fill=fill, stroke=stroke))
        y += 88

    y = 58
    for i, (ev, st) in enumerate(rows_right):
        fill = "#eaf0fd" if i == 3 else FILL
        stroke = NEG if i == 3 else LINE
        s = ev if not st else ev + "\n" + st
        b.append(fitbox(510, y, 420, 72, s, size=12, fill=fill, stroke=stroke))
        y += 88

    render(os.path.join(OUT, 'counter-vs-flag.svg'), W, H, *b)


def fig_wait_post():
    """Дві операції над лічильником і межа, всередині якої вони неподільні."""
    W, H = 980, 470
    b = []

    b.append(fitbox(390, 26, 200, 66, "лічильник\n(значення ≥ 0)",
                    size=13, fill="#eaf0fd", stroke=NEG))

    b.append(text(190, 130, "sem_wait — «дай одиницю»", size=14, bold=True))
    b.append(fitbox(30, 152, 320, 78,
                    "значення більше нуля:\nвідняти одиницю й повернутися", size=12))
    b.append(fitbox(30, 252, 320, 78,
                    "значення нульове:\nстати в чергу й заснути", size=12,
                    fill="#fdecea", stroke=POS))

    b.append(text(790, 130, "sem_post — «ось одиниця»", size=14, bold=True))
    b.append(fitbox(630, 152, 320, 78,
                    "додати одиницю до значення", size=12))
    b.append(fitbox(630, 252, 320, 78,
                    "у черзі хтось стоїть:\nрозбудити одного з них", size=12,
                    fill="#eaf0fd", stroke=NEG))

    b.append(arrow(350, 191, 386, 92))
    b.append(arrow(630, 191, 594, 92))

    note, _, _ = textbox(490, 400,
                         "перевірка значення й засинання — одна неподільна дія:\n"
                         "якби між ними був проміжок, sem_post устиг би пройти\n"
                         "по порожній черзі, і будити не було б кого",
                         size=12, fill="#ffffff")
    b.append(note)

    render(os.path.join(OUT, 'wait-post.svg'), W, H, *b)


def fig_rendezvous():
    """Дві відповіді на питання «як двоє знаходять той самий лічильник»."""
    W, H = 1000, 500
    b = []

    b.append(text(250, 34, "безіменний: sem_init(&s, 1, 0)", size=14, bold=True))
    b.append(text(750, 34, "іменований: sem_open(\"/frames.filled\", …)", size=14, bold=True))

    # ліва половина
    b.append(fitbox(40, 58, 180, 56, "процес A", size=13))
    b.append(fitbox(280, 58, 180, 56, "процес B", size=13))
    b.append(arrow(130, 116, 150, 196))
    b.append(arrow(370, 116, 350, 196))
    b.append(rect(40, 200, 420, 110, fill="#f0f4ff", stroke=NEG))
    b.append(fitbox(60, 222, 150, 68, "sem_t", size=13, fill="#eaf0fd", stroke=NEG))
    b.append(fitbox(230, 222, 210, 68, "дані, заради яких\nусе робиться", size=12))
    b.append(text(250, 336, "спільне відображення: об'єкт shm", size=12, color=MUTED))
    b.append(text(250, 356, "або MAP_SHARED, зроблене до fork", size=12, color=MUTED))

    n1, _, _ = textbox(250, 412,
                       "семафор мусить лежати ВСЕРЕДИНІ\n"
                       "спільної пам'яті: копія структури\n"
                       "в кожного — це два різні семафори",
                       size=12, fill="#fdecea", stroke=POS)
    b.append(n1)

    # права половина
    b.append(fitbox(540, 58, 180, 56, "процес A", size=13))
    b.append(fitbox(780, 58, 180, 56, "процес B", size=13))
    b.append(arrow(630, 116, 650, 196))
    b.append(arrow(870, 116, 850, 196))
    b.append(rect(540, 200, 420, 110, fill="#f0f4ff", stroke=NEG))
    b.append(fitbox(560, 222, 380, 68,
                    "/dev/shm/sem.frames.filled — файл на tmpfs,\nякий libc відображає обом", size=12,
                    fill="#eaf0fd", stroke=NEG))
    b.append(text(750, 336, "домовляються про ім'я, а не про пам'ять:", size=12, color=MUTED))
    b.append(text(750, 356, "спорідненість процесів не потрібна", size=12, color=MUTED))

    n2, _, _ = textbox(750, 412,
                       "той самий об'єкт у крихітному\n"
                       "спільному відображенні, яке\n"
                       "бібліотека зробила за вас",
                       size=12, fill="#ffffff")
    b.append(n2)

    render(os.path.join(OUT, 'rendezvous.svg'), W, H, *b)


def fig_lock_order():
    """Порядок двох sem_wait: лічильний перед м'ютексом — і що дає зворотний."""
    W, H = 1040, 480
    b = []

    b.append(text(260, 32, "спершу лічильний, потім м'ютекс", size=14, bold=True))
    b.append(text(780, 32, "спершу м'ютекс, потім лічильний", size=14, bold=True))

    left = [
        "виробник: sem_wait(free_slots)\nбуфер повний — засинає, м'ютекс лишився вільним",
        "споживач: sem_wait(filled), потім sem_wait(mutex)\nбере елемент, віддає м'ютекс",
        "споживач: sem_post(free_slots)\nвиробника розбуджено — обмін триває",
    ]
    right = [
        "виробник: sem_wait(mutex)\nм'ютекс тепер у виробника",
        "виробник: sem_wait(free_slots)\nбуфер повний — засинає, ТРИМАЮЧИ м'ютекс",
        "споживач: sem_wait(filled), потім sem_wait(mutex)\nм'ютекс зайнято — засинає теж",
    ]

    y = 56
    for i, s in enumerate(left):
        b.append(fitbox(30, y, 460, 82, s, size=12))
        y += 96

    y = 56
    for i, s in enumerate(right):
        red = (i == 2)
        b.append(fitbox(550, y, 460, 82, s, size=12,
                        fill="#fdecea" if red else FILL,
                        stroke=POS if red else LINE))
        y += 96

    n1, _, _ = textbox(260, 396,
                       "той, хто спить, нічого не тримає —\n"
                       "тому розбудити його завжди є кому",
                       size=12, fill="#eaf0fd", stroke=NEG)
    b.append(n1)

    n2, _, _ = textbox(780, 396,
                       "вільний слот з'явиться лише після споживача,\n"
                       "а споживач чекає на м'ютекс виробника:\n"
                       "обидва сплять назавжди",
                       size=12, fill="#fdecea", stroke=POS)
    b.append(n2)

    render(os.path.join(OUT, 'lock-order.svg'), W, H, *b)


if __name__ == '__main__':
    fig_counter_vs_flag()
    fig_wait_post()
    fig_rendezvous()
    fig_lock_order()
    print("ok")
