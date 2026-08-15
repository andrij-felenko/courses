# -*- coding: utf-8 -*-
"""Фігури до теми «Спільна пам'ять POSIX»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_two_spaces():
    """Одні й ті самі фізичні сторінки під різними віртуальними адресами."""
    W, H = 860, 430
    b = []

    # Процес A
    b.append(rect(20, 30, 280, 150, fill="#ffffff"))
    b.append(text(160, 55, "Процес A (пише)", size=14, bold=True))
    b.append(rect(45, 78, 230, 62, fill=FILL))
    b.append(text(160, 103, "відображення MAP_SHARED", size=12))
    b.append(text(160, 125, "0x7f2a1c000000", size=12, color=MUTED))

    # Процес B
    b.append(rect(560, 30, 280, 150, fill="#ffffff"))
    b.append(text(700, 55, "Процес B (читає)", size=14, bold=True))
    b.append(rect(585, 78, 230, 62, fill=FILL))
    b.append(text(700, 103, "відображення MAP_SHARED", size=12))
    b.append(text(700, 125, "0x7f9d3e800000", size=12, color=MUTED))

    # Застереження посередині
    note, _, _ = textbox(430, 105, "адреси різні:\nвказівник із A\nу B нікуди\nне веде",
                         size=12, fill="#fdecea", stroke=POS)
    b.append(note)

    # Смуга фізичних сторінок
    b.append(text(430, 281, "фізичні сторінки, спільні для обох", size=13))
    for i in range(6):
        x = 190 + i * 80
        b.append(rect(x, 300, 80, 60, fill="#eaf0fd", stroke=NEG))
        b.append(text(x + 40, 335, "4 КіБ", size=11, color=NEG))

    # Стрілки «через таблицю сторінок»
    b.append(arrow(160, 182, 230, 296))
    b.append(arrow(700, 182, 630, 296))
    b.append(text(85, 245, "таблиця сторінок A", size=12, color=MUTED))
    b.append(text(775, 245, "таблиця сторінок B", size=12, color=MUTED))

    b.append(text(430, 395, "tmpfs-об'єкт /dev/shm/telemetry — сторінки в пам'яті, диска немає",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'two-spaces.svg'), W, H, *b)


def fig_segment():
    """Розкладка сегмента: індекси в окремих кеш-лініях + тіло даних."""
    W, H = 880, 300
    b = []
    b.append(text(210, 82, "заголовок — індекси", size=13, bold=True))
    b.append(text(610, 82, "тіло — самі байти", size=13, bold=True))

    b.append(fitbox(40, 110, 170, 80, "head\n(куди пишуть)\n64 байти", size=12, fill="#fdecea", stroke=POS))
    b.append(fitbox(210, 110, 170, 80, "tail\n(звідки читають)\n64 байти", size=12, fill="#eaf0fd", stroke=NEG))
    b.append(fitbox(380, 110, 460, 80, "кільце даних (степінь двійки байтів)", size=13))

    n1, _, _ = textbox(200, 245, "кожен індекс — у власній\nкеш-лінії, інакше два ядра\nб'ються за одну лінію",
                       size=12, fill="#ffffff")
    n2, _, _ = textbox(640, 245, "усередині — лише зсуви від початку\nвідображення: чужий вказівник\nтут не означає нічого",
                       size=12, fill="#ffffff")
    b.append(n1)
    b.append(n2)
    render(os.path.join(OUT, 'segment-layout.svg'), W, H, *b)


def fig_lifetime():
    """Два різні життя: ім'я в каталозі й самі сторінки."""
    W, H = 900, 330
    b = []
    b.append(text(30, 95, "ім'я в /dev/shm", size=13, anchor="start", bold=True))
    b.append(text(30, 175, "сторінки пам'яті", size=13, anchor="start", bold=True))

    b.append(rect(200, 77, 360, 26, fill="#eaf0fd", stroke=NEG))
    b.append(rect(300, 157, 460, 26, fill="#fdecea", stroke=POS))

    b.append(text(625, 95, "ім'я зникло", size=12, color=MUTED))
    b.append(text(825, 175, "пам'ять звільнено", size=12, color=MUTED))
    b.append(text(420, 130, "сторінки живуть, поки є відображення", size=12, color=MUTED))

    for x, y0, y1 in ((200, 105, 238), (560, 105, 238), (300, 185, 278), (760, 185, 278)):
        b.append(line(x, y0, x, y1, color=MUTED, dash="4,4"))

    b.append(text(200, 250, "shm_open(O_CREAT)", size=12))
    b.append(text(560, 250, "shm_unlink", size=12))
    b.append(text(300, 290, "mmap у A і B", size=12))
    b.append(text(760, 290, "останній munmap / exit", size=12))
    render(os.path.join(OUT, 'lifetime.svg'), W, H, *b)


def fig_ring_wrap():
    """Вставка proj-shm-ring: маска замість ділення й запис «через край»."""
    W, H = 900, 420
    X0, X1 = 90, 830
    b = []

    b.append(text(90, 52, "запис лягає одним шматком", size=13, anchor="start", bold=True))
    b.append(rect(X0, 70, X1 - X0, 56, fill="#ffffff"))
    b.append(rect(300, 70, 380, 56, fill="#eaf0fd", stroke=NEG))
    b.append(text(490, 103, "зайнято читачем", size=12, color=NEG))
    b.append(text(190, 103, "вільно", size=12, color=MUTED))
    b.append(text(760, 103, "вільно", size=12, color=MUTED))
    b.append(arrow(300, 160, 300, 130))
    b.append(text(300, 180, "tail & MASK", size=12))
    b.append(arrow(680, 160, 680, 130))
    b.append(text(680, 180, "head & MASK", size=12))

    b.append(text(90, 232, "запис перетнув кінець тіла — дві копії замість однієї",
                  size=13, anchor="start", bold=True))
    b.append(rect(X0, 250, X1 - X0, 56, fill="#ffffff"))
    b.append(rect(700, 250, 130, 56, fill="#fdecea", stroke=POS))
    b.append(rect(X0, 250, 110, 56, fill="#fdecea", stroke=POS))
    b.append(text(765, 283, "хвіст тіла", size=12, color=POS))
    b.append(text(145, 283, "початок тіла", size=12, color=POS))
    b.append(text(460, 283, "цього не чіпаємо", size=12, color=MUTED))
    b.append(arrow(700, 340, 700, 312))
    b.append(text(700, 360, "head & MASK", size=12))

    b.append(text(450, 400,
                  "зайнято = head − tail (беззнакова різниця) · вільно = size − зайнято · порожньо ⇔ head == tail",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'ring-wrap.svg'), W, H, *b)


def fig_wake():
    """Вставка proj-shm-ring: прапорець наміру заснути й пробудження через eventfd."""
    W, H = 900, 470
    b = []
    b.append(text(225, 48, "виробник", size=13, bold=True))
    b.append(text(675, 48, "споживач", size=13, bold=True))

    b.append(fitbox(570, 80, 210, 44, "порожньо: pop нічого не дав", size=12))
    b.append(line(675, 126, 675, 148, color=MUTED, dash="4,4"))
    b.append(fitbox(570, 150, 210, 52, "need_wake = 1\n(seq_cst)", size=12,
                    fill="#eaf0fd", stroke=NEG))
    b.append(line(675, 204, 675, 220, color=MUTED, dash="4,4"))
    b.append(fitbox(570, 222, 210, 52, "перевірити head ще раз:\nвсе одно порожньо", size=12))
    b.append(line(675, 276, 675, 292, color=MUTED, dash="4,4"))
    b.append(fitbox(570, 294, 210, 44, "read(efd) — процес спить", size=12))
    b.append(arrow(675, 342, 675, 382))
    b.append(fitbox(570, 386, 210, 44, "прокинувся, pop дає запис", size=12))

    b.append(fitbox(120, 115, 210, 52, "дані в тіло,\nпотім release-запис head", size=12))
    b.append(line(225, 169, 225, 253, color=MUTED, dash="4,4"))
    b.append(fitbox(120, 255, 210, 52, "need_wake == 1?\nобмін на 0, write(efd, 1)", size=12,
                    fill="#fdecea", stroke=POS))
    b.append(arrow(330, 281, 566, 316))
    b.append(text(440, 272, "пробудження", size=12, color=MUTED))

    b.append(text(450, 452,
                  "запис прапорця й читання head стоять на різних боках: без seq_cst обидва побачать старе",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'wake-handshake.svg'), W, H, *b)



def fig_two_namespaces():
    """Ключ System V проти шляху в /dev/shm."""
    W, H = 900, 470
    b = []
    LX, RX, BW = 40, 490, 370

    b.append(text(LX + BW / 2, 30, "System V: ключ", size=15, bold=True))
    b.append(text(RX + BW / 2, 30, "POSIX: ім'я-шлях", size=15, bold=True))

    left = [
        ("/var/run/app.pid  +  proj 'A'", FILL),
        ("ftok()  →  key 0x41050CD3", FILL),
        ("shmget(key, ...)  →  id 32769", FILL),
        ("сегмент у таблиці IPC ядра", FILL),
    ]
    right = [
        ("/dev/shm/app", FILL),
        ("open()  →  fd 5", FILL),
        ("mmap(fd, MAP_SHARED)", FILL),
        ("звичайний файл tmpfs", FILL),
    ]

    y0, BH, GAP = 48, 48, 32
    for col_x, items in ((LX, left), (RX, right)):
        y = y0
        for i, (s_, fillc) in enumerate(items):
            b.append(fitbox(col_x, y, BW, BH, s_, size=13, fill=fillc))
            if i < len(items) - 1:
                b.append(arrow(col_x + BW / 2, y + BH, col_x + BW / 2, y + BH + GAP))
            y += BH + GAP

    ybot = y0 + 4 * (BH + GAP)
    b.append(fitbox(LX, ybot, BW, 62,
                    "у файловій системі його немає:\nвидно лише в ipcs, прибирає ipcrm",
                    size=12, fill="#fdecea", stroke=MUTED))
    b.append(fitbox(RX, ybot, BW, 62,
                    "ls, chmod, rm працюють;\nзникає з останнім посиланням",
                    size=12, fill="#eaf6ec", stroke=MUTED))
    render(os.path.join(OUT, 'two-namespaces.svg'), W, H, *b)


fig_two_spaces()
fig_segment()
fig_lifetime()
fig_ring_wrap()
fig_wake()
fig_two_namespaces()
print("ok")
