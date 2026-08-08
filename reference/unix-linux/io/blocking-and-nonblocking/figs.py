# -*- coding: utf-8 -*-
"""Фігури до теми «Блокуючий і неблокуючий режим»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_two_answers():
    """Дві відповіді на те саме очікування: де перебуває потік, поки даних немає."""
    W, H = 940, 330
    g = []

    # ── смуга «блокуючий» ──────────────────────────────────────────────
    g.append(text(24, 92, "блокуючий", size=14, anchor="start", bold=True))
    g.append(fitbox(200, 62, 120, 52, "read()", size=14))
    g.append(fitbox(324, 62, 356, 52,
                    "задача спить у черзі очікування\n0 % процесора, потік зайнятий",
                    size=13, fill="#eef2f7"))
    g.append(fitbox(684, 62, 232, 52, "повертає n байтів", size=13, fill="#eaf7ee"))

    # позначка «дані прийшли» над межею x=684
    g.append(text(684, 30, "дані прийшли — драйвер будить чергу", size=12, color=MUTED))
    g.append(arrow(684, 38, 684, 58, color=MUTED, sw=1.4))

    # ── смуга «неблокуючий» ────────────────────────────────────────────
    g.append(text(24, 182, "неблокуючий", size=14, anchor="start", bold=True))
    g.append(fitbox(200, 152, 120, 52, "read()", size=14))
    g.append(fitbox(324, 152, 128, 52, "EAGAIN", size=13, fill="#fdecea"))
    g.append(fitbox(456, 152, 224, 52,
                    "потік працює\nз іншими дескрипторами", size=12, fill="#eef2f7"))
    g.append(fitbox(684, 152, 232, 52, "read() → n байтів", size=13, fill="#eaf7ee"))

    # ── підсумкова смуга ───────────────────────────────────────────────
    g.append(fitbox(200, 236, 716, 54,
                    "у неблокуючому режимі одне засинання обслуговує сотні дескрипторів:\n"
                    "потік спить не в read(), а в очікуванні готовності",
                    size=13, fill="#f7f3e8", stroke=MUTED))

    render(os.path.join(IMG, 'two-answers.svg'), W, H, *g,
           title="Блокуючий і неблокуючий режим очікування")


def fig_where_state_lives():
    """Той самий стан розмови: у кадрах стека або у власній структурі."""
    W, H = 940, 350
    g = []

    g.append(text(230, 30, "стан у кадрах стека", size=14, bold=True))
    g.append(text(700, 30, "стан у власній структурі", size=14, bold=True))

    # ── ліва колона: стек ──────────────────────────────────────────────
    left_rows = [
        "main() → accept()",
        "handle_client(fd)",
        "read_request(fd, ...)",
        "read(fd, ...) — тут задача спить",
    ]
    y = 54
    for i, s in enumerate(left_rows):
        fill = "#fdecea" if i == len(left_rows) - 1 else FILL
        g.append(fitbox(30, y, 400, 44, s, size=13, fill=fill))
        y += 50

    g.append(fitbox(30, 262, 400, 62,
                    "де саме ми в протоколі — видно з кадрів;\n"
                    "ядро тримає їх разом із потоком задарма",
                    size=12, fill="#eef2f7", stroke=MUTED))

    # ── права колона: структури ────────────────────────────────────────
    right_rows = [
        "conn[7]:  стан = ЧЕКАЄМО ТІЛО, зсув 128",
        "conn[8]:  стан = ПИШЕМО ВІДПОВІДЬ, зсув 40",
        "conn[9]:  стан = ЧЕКАЄМО ЗАГОЛОВОК",
        "один потік, один стек на всіх",
    ]
    y = 54
    for i, s in enumerate(right_rows):
        fill = "#eaf7ee" if i == len(right_rows) - 1 else FILL
        g.append(fitbox(510, y, 400, 44, s, size=12, fill=fill))
        y += 50

    g.append(fitbox(510, 262, 400, 62,
                    "той самий стан, але виписаний руками;\n"
                    "після кожної події стек порожній",
                    size=12, fill="#eef2f7", stroke=MUTED))

    render(os.path.join(IMG, 'where-state-lives.svg'), W, H, *g,
           title="Де зберігається стан незавершеної розмови")


def fig_coverage():
    """Кого прапорець справді стосується, а де чекання лишається."""
    W, H = 960, 430
    g = []

    g.append(text(235, 30, "O_NONBLOCK діє", size=14, bold=True, color=FIELD))
    g.append(text(725, 30, "чекання лишається попри прапорець", size=14, bold=True, color=POS))

    works = [
        "сокет: read і write повертають EAGAIN",
        "канал і FIFO — так само",
        "термінал і послідовний порт",
        "eventfd, timerfd, signalfd",
    ]
    stays = [
        "звичайний файл: прапорець приймають,\nале читання все одно чекає на диск",
        "open() на FIFO, поки нема пари",
        "розв'язання імені (getaddrinfo)",
        "сторінковий збій на відображеному файлі",
        "fsync і close із SO_LINGER",
        "розбір шляху через завислий NFS",
    ]

    y = 56
    for s in works:
        g.append(fitbox(30, y, 410, 52, s, size=13, fill="#eaf7ee", stroke=FIELD))
        y += 60

    y = 56
    for s in stays:
        g.append(fitbox(520, y, 410, 52, s, size=13, fill="#fdecea", stroke=POS))
        y += 60

    render(os.path.join(IMG, 'nonblock-coverage.svg'), W, H, *g,
           title="Що прапорець неблокуючости покриває, а що ні")


def fig_phase_machine():
    """Автомат станів одного з'єднання: те, що в блокуючій версії було порядком рядків."""
    W, H = 920, 470
    g = []

    BX, BW = 100, 410          # колонка станів
    AX, AW = 550, 350          # колонка приміток
    ARR = 150                  # вісь стрілок переходу
    LBL = 340                  # центр підписів переходу

    states = [
        (44, 68, "PH_HEADER\nчитаємо в hdr[4], поки hdr_got < 4"),
        (158, 68, "PH_BODY\nчитаємо в body[], поки body_got < body_len"),
        (272, 68, "повідомлення ціле\nout_push(4 + body_len)\nout_flush()"),
        (386, 56, "phase = PH_HEADER, hdr_got = 0"),
    ]
    fills = [FILL, FILL, "#eaf7ee", "#eef2f7"]
    for (y, h, s), f in zip(states, fills):
        g.append(fitbox(BX, y, BW, h, s, size=13, fill=f))

    # переходи
    trans = [
        (112, 158, 140, "hdr_got == 4 → body_len = ntohl(hdr)"),
        (226, 272, 254, "body_got == body_len — повідомлення ціле"),
        (340, 386, 368, "з'єднання готове до наступного повідомлення"),
    ]
    for y1, y2, ly, s in trans:
        g.append(arrow(ARR, y1, ARR, y2))
        g.append(text(LBL, ly, s, size=12, color=MUTED))

    # зворотний шлях ліворуч
    g.append(line(BX, 414, 60, 414))
    g.append(line(60, 414, 60, 78))
    g.append(arrow(60, 78, BX, 78))

    notes = [
        (44, 68, "read() дав менше за 4 байти або EAGAIN:\nлічильник росте, фаза лишається"),
        (158, 68, "read() дав менше, ніж лишалося, або EAGAIN:\nросте body_got, фаза лишається"),
        (272, 68, "write узяв не все — лишився хвіст:\narm() вмикає EPOLLOUT"),
        (386, 56, "хвіст дописано — arm() вимикає EPOLLOUT"),
    ]
    for y, h, s in notes:
        cy = y + h / 2
        g.append(line(BX + BW, cy, AX, cy, color=MUTED, sw=1.2, dash="4,4"))
        g.append(fitbox(AX, y, AW, h, s, size=12, fill="#f7f3e8", stroke=MUTED))

    render(os.path.join(IMG, 'phase-machine.svg'), W, H, *g,
           title="Фази одного з'єднання в циклі подій")


def fig_epollout_ladder():
    """Як умикається й вимикається EPOLLOUT на недописаному хвості."""
    W, H = 960, 352
    g = []

    C1, W1 = 20, 190
    C2, W2 = 222, 350
    C3, W3 = 584, 150
    C4, W4 = 746, 194

    head = [(C1, W1, "подія"), (C2, W2, "що робить обробник"),
            (C3, W3, "out_off / out_len"), (C4, W4, "маска після arm()")]
    for x, w, s in head:
        g.append(fitbox(x, 26, w, 40, s, size=13, bold=True, fill="#eef2f7"))

    rows = [
        (76, "повідомлення зібране",
         "out_push(40004 Б); out_flush():\nwrite узяв 16384, далі EAGAIN",
         "16384 / 40004", "EPOLLIN | EPOLLOUT"),
        (140, "EPOLLOUT",
         "out_flush(): write узяв 16384,\nдалі знову EAGAIN",
         "32768 / 40004", "EPOLLIN | EPOLLOUT\nбез epoll_ctl"),
        (204, "EPOLLOUT",
         "out_flush(): write узяв 7236,\nчерга спорожніла",
         "0 / 0", "EPOLLIN"),
    ]
    for y, a, b, c, d in rows:
        g.append(fitbox(C1, y, W1, 52, a, size=12))
        g.append(fitbox(C2, y, W2, 52, b, size=12))
        g.append(fitbox(C3, y, W3, 52, c, size=12, fill="#eef2f7"))
        fill = "#eaf7ee" if d == "EPOLLIN" else "#f7f3e8"
        g.append(fitbox(C4, y, W4, 52, d, size=12, fill=fill))

    g.append(fitbox(C1, 272, 920, 60,
                    "якби EPOLLOUT лишався ввімкненим завжди, epoll_wait повертав би "
                    "готовність до запису негайно\nй нескінченно — цикл крутився б "
                    "на 100 % процесора, нічого не роблячи",
                    size=13, fill="#fdecea", stroke=POS))

    render(os.path.join(IMG, 'epollout-ladder.svg'), W, H, *g,
           title="Умикання й вимикання EPOLLOUT на недописаному хвості")


def fig_three_levels():
    """Три рівні вмикання неблокуючости й коло тих, кого зміна зачіпає."""
    W, H = 980, 380
    g = []

    g.append(text(160, 30, "де вмикають", size=13, bold=True))
    g.append(text(505, 30, "чим саме", size=13, bold=True))
    g.append(text(835, 30, "кого зачіпає", size=13, bold=True))

    rows = [
        ("при створенні\nдескриптора",
         "socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0)\n"
         "accept4(lfd, NULL, NULL, SOCK_NONBLOCK)\n"
         "pipe2(fd, O_NONBLOCK)\n"
         "open(path, O_RDONLY | O_NONBLOCK)",
         "опис відкритого файлу —\nвід першої миті життя",
         "#eaf7ee", FIELD),
        ("на вже відкритому\nдескрипторі",
         "f = fcntl(fd, F_GETFL, 0);\n"
         "fcntl(fd, F_SETFL, f | O_NONBLOCK);",
         "той самий опис —\nразом з усіма, хто його ділить",
         "#f7f3e8", MUTED),
        ("на один виклик",
         "recv(fd, buf, n, MSG_DONTWAIT)\n"
         "preadv2(fd, iov, 1, -1, RWF_NOWAIT)",
         "нікого: спільний опис\nлишається недоторканим",
         "#eef2f7", NEG),
    ]

    y = 52
    for title, calls, scope, fill, stroke in rows:
        g.append(fitbox(24, y, 272, 92, title, size=13, fill=fill, stroke=stroke))
        g.append(fitbox(316, y, 382, 92, calls, size=11, fill=FILL))
        g.append(fitbox(718, y, 238, 92, scope, size=12, fill=fill, stroke=stroke))
        y += 108

    render(os.path.join(IMG, 'three-levels.svg'), W, H, *g,
           title="Три рівні вмикання неблокуючого режиму")


def fig_connect_flow():
    """Перебіг неблокуючого connect і відповіді, які легко переплутати з невдачею."""
    W, H = 980, 480
    g = []

    g.append(text(200, 28, "перебіг", size=13, bold=True))
    g.append(text(690, 28, "інші відповіді того самого connect", size=13, bold=True))

    steps = [
        (48, 50, "connect(fd, addr, len)", FILL, LINE),
        (116, 50, "−1, errno = EINPROGRESS", "#fdecea", POS),
        (184, 58, "epoll_wait → EPOLLOUT\n(на невдачі ще й EPOLLERR)", FILL, LINE),
        (264, 58, "getsockopt(fd, SOL_SOCKET,\nSO_ERROR, &err, &len)", FILL, LINE),
        (344, 44, "err == 0 → з'єднано", "#eaf7ee", FIELD),
        (402, 58, "err != 0 → це і є причина;\nсокет закрити, створити новий",
         "#fdecea", POS),
    ]
    for y, h, s, fill, stroke in steps:
        g.append(fitbox(40, y, 320, h, s, size=12, fill=fill, stroke=stroke))

    for y0, y1 in ((100, 114), (168, 182), (244, 262), (324, 342), (390, 400)):
        g.append(arrow(200, y0, 200, y1, color=MUTED, sw=1.4))

    notes = [
        (48, 60, "0 — з'єднано одразу; звична відповідь\nна сокеті домену Unix і на loopback"),
        (124, 60, "EAGAIN замість EINPROGRESS — тільки на\nсокеті домену Unix: черга слухача повна"),
        (200, 60, "EALREADY — попереднє рукостискання ще триває;\nце не «спробуй ще», а «питаєш не тим викликом»"),
        (276, 60, "EISCONN — з'єднання вже встановлено; саме так\nвиглядає успіх для коду, що повторює connect"),
        (352, 60, "готовність до запису сама собою нічого не доводить:\nневдале з'єднання теж робить сокет готовим"),
    ]
    for y, h, s in notes:
        g.append(fitbox(412, y, 544, h, s, size=11, fill="#eef2f7", stroke=MUTED))

    render(os.path.join(IMG, 'connect-flow.svg'), W, H, *g,
           title="Неблокуючий connect: перебіг і сусідні відповіді")


if __name__ == '__main__':
    fig_two_answers()
    fig_where_state_lives()
    fig_coverage()
    fig_phase_machine()
    fig_epollout_ladder()
    fig_three_levels()
    fig_connect_flow()
    print("ok")
