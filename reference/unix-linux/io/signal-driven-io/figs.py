# -*- coding: utf-8 -*-
"""Фігури до теми «Ввід-вивід за сигналом: F_SETOWN, F_SETSIG і SIGIO»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_three_conditions():
    """Три незалежні умови, за яких подія на дескрипторі стає сигналом."""
    W, H = 1000, 412
    g = []

    c1x, c1w = 30, 250
    c2x, c2w = 300, 320
    c3x, c3w = 640, 330

    g.append(fitbox(c1x, 26, c1w, 40, "умова", size=14, bold=True, fill="#eef2f7"))
    g.append(fitbox(c2x, 26, c2w, 40, "як вмикають", size=14, bold=True, fill="#eef2f7"))
    g.append(fitbox(c3x, 26, c3w, 40, "якщо забути", size=14, bold=True, fill="#eef2f7"))

    rows = [
        (90,  "кому слати",
              "fcntl(fd, F_SETOWN, getpid())\nзапис лягає в опис відкритого файлу",
              "власник = 0:\nсигнал народжується й зникає"),
        (170, "чи слати взагалі",
              "fcntl(fd, F_SETFL, fl | O_ASYNC)\nчерез open прапорець не ставиться",
              "сигналів немає зовсім,\nпрограма чекає марно"),
        (250, "що станеться на приході",
              "обробник або блокування сигналу —\nдо ввімкнення O_ASYNC",
              "типова дія SIGIO в Linux —\nзавершити процес"),
    ]
    for y, a, b, c in rows:
        g.append(fitbox(c1x, y, c1w, 64, a, size=13, bold=True))
        g.append(fitbox(c2x, y, c2w, 64, b, size=12, fill="#eaf7ee"))
        g.append(fitbox(c3x, y, c3w, 64, c, size=12, fill="#fdecea"))

    g.append(fitbox(c1x, 336, c3x + c3w - c1x, 56,
                    "порядок важить: спершу власник, потім O_ASYNC — інакше подія,\n"
                    "що трапиться між двома викликами fcntl, пропаде безслідно",
                    size=13, fill="#f7f3e8", stroke=MUTED))

    render(os.path.join(IMG, 'three-conditions.svg'), W, H, *g,
           title="Три умови народження сигналу про готовність")


def fig_what_arrives():
    """Звичайний SIGIO проти реальночасового сигналу після F_SETSIG."""
    W, H = 1000, 430
    g = []

    lx, lw = 34, 440
    rx, rw = 526, 440

    g.append(fitbox(lx, 26, lw, 44, "SIGIO (типово)", size=15, bold=True, fill="#eef2f7"))
    g.append(fitbox(rx, 26, rw, 44, "SIGRTMIN+n після F_SETSIG", size=15, bold=True, fill="#eef2f7"))

    g.append(fitbox(lx, 96, lw, 96,
                    "у програму приходить\nномер сигналу — і все:\n"
                    "який дескриптор, читати чи писати — невідомо",
                    size=13, fill="#fdecea"))
    g.append(fitbox(rx, 96, rw, 96,
                    "siginfo_t:\nsi_fd — дескриптор\n"
                    "si_band — те саме, що revents у poll\nsi_code — POLL_IN, POLL_OUT, POLL_ERR, POLL_HUP",
                    size=13, fill="#eaf7ee"))

    g.append(fitbox(lx, 216, lw, 92,
                    "очікування — один біт:\nдесять подій, поки сигнал заблоковано,\n"
                    "дають одну доставку",
                    size=13, fill="#fdecea"))
    g.append(fitbox(rx, 216, rw, 92,
                    "очікування — черга записів:\nкожна подія зберігається окремо,\n"
                    "межа — RLIMIT_SIGPENDING",
                    size=13, fill="#eaf7ee"))

    g.append(fitbox(lx, 332, lw, 72,
                    "робота пропорційна\nкількості дескрипторів:\nпісля сигналу — повний обхід",
                    size=13))
    g.append(fitbox(rx, 332, rw, 72,
                    "робота пропорційна кількості подій —\nдоки черга не переповниться\n"
                    "й ядро не поверне звичайний SIGIO",
                    size=13))

    render(os.path.join(IMG, 'what-arrives.svg'), W, H, *g,
           title="Що дістає програма з сигналу про готовність")


def fig_batch_vs_frame():
    """Розмір порції: пачка подій за один перехід проти кадру на кожну подію."""
    W, H = 1010, 424
    g = []

    lab_x, lab_w = 30, 200
    mid_x, mid_w = 262, 300
    end_x, end_w = 604, 376

    g.append(fitbox(lab_x, 30, lab_w, 66, "epoll_wait", size=14, bold=True, fill="#eaf7ee"))
    g.append(fitbox(mid_x, 30, mid_w, 66, "один перехід межі ядра", size=13))
    g.append(arrow(mid_x + mid_w + 8, 63, end_x - 8, 63))
    g.append(fitbox(end_x, 30, end_w, 66, "до 128 готових дескрипторів\nза цей самий перехід", size=13, fill="#eef2f7"))

    g.append(fitbox(lab_x, 122, lab_w, 66, "sigwaitinfo", size=14, bold=True, fill="#f7f3e8"))
    g.append(fitbox(mid_x, 122, mid_w, 66, "перехід на кожну подію", size=13))
    g.append(arrow(mid_x + mid_w + 8, 155, end_x - 8, 155))
    g.append(fitbox(end_x, 122, end_w, 66, "одна подія з черги", size=13, fill="#eef2f7"))

    g.append(fitbox(lab_x, 214, lab_w, 78, "обробник\nз SA_SIGINFO", size=14, bold=True, fill="#fdecea"))
    g.append(fitbox(mid_x, 214, mid_w, 78, "сигнальний кадр на стеку:\nрегістри й стан FPU", size=13))
    g.append(arrow(mid_x + mid_w + 8, 253, end_x - 8, 253))
    g.append(fitbox(end_x, 214, end_w, 78,
                    "обробник, далі системний виклик\nrt_sigreturn — і теж одна подія", size=13, fill="#eef2f7"))

    g.append(fitbox(lab_x, 318, end_x + end_w - lab_x, 74,
                    "200 000 подій за секунду: 1563 виклики epoll_wait проти 200 000 доставок сигналу —\n"
                    "асимптотика однакова, стала різниться приблизно в 128 разів",
                    size=13, fill="#f7f3e8", stroke=MUTED))

    render(os.path.join(IMG, 'batch-vs-frame.svg'), W, H, *g,
           title="Розмір порції сповіщень")


def fig_two_paths():
    """Два шляхи одного циклу: адресний сигнал і безадресний SIGIO."""
    W, H = 1030, 468
    g = []

    x0, bw, gap = 30, 216, 32
    xs = [x0 + i * (bw + gap) for i in range(4)]

    g.append(fitbox(x0, 24, 4 * bw + 3 * gap, 38,
                    "звичайний хід: подія помістилася в чергу ядра",
                    size=14, bold=True, fill="#eaf7ee"))

    row1 = [
        "sigwaitinfo() віддає\nSIGRTMIN+1",
        "si_fd — котрий дескриптор,\nsi_band — те саме кодування,\nщо revents у poll",
        "read на одному дескрипторі\nдоки не EAGAIN,\nвідповідь тим же write",
        "робота пропорційна\nкількості подій",
    ]
    for i, s in enumerate(row1):
        g.append(fitbox(xs[i], 76, bw, 96, s, size=12,
                        fill="#eef2f7" if i < 3 else "#eaf7ee"))
    for i in range(3):
        g.append(arrow(xs[i] + bw + 4, 124, xs[i + 1] - 4, 124))

    g.append(fitbox(x0, 196, 4 * bw + 3 * gap, 38,
                    "черга вперлася в RLIMIT_SIGPENDING",
                    size=14, bold=True, fill="#fdecea"))

    row2 = [
        "sigwaitinfo() віддає\nзвичайний SIGIO",
        "адреси немає:\nчастину подій утрачено,\nстан невідомий",
        "sigtimedwait з нульовим часом —\nвикинути стале з черги,\nдалі poll по всіх дескрипторах",
        "робота пропорційна\nкількості з'єднань",
    ]
    for i, s in enumerate(row2):
        g.append(fitbox(xs[i], 248, bw, 96, s, size=12,
                        fill="#eef2f7" if i < 3 else "#fdecea"))
    for i in range(3):
        g.append(arrow(xs[i] + bw + 4, 296, xs[i + 1] - 4, 296))

    g.append(fitbox(x0, 372, 4 * bw + 3 * gap, 72,
                    "обидва шляхи закінчуються тією самою функцією обробки:\n"
                    "si_band і revents кодують подію однаково, тож коду для неї один",
                    size=13, fill="#f7f3e8", stroke=MUTED))

    render(os.path.join(IMG, 'two-paths.svg'), W, H, *g,
           title="Швидкий шлях і запасний шлях одного циклу")


if __name__ == '__main__':
    fig_three_conditions()
    fig_what_arrives()
    fig_batch_vs_frame()
    fig_two_paths()
    print("ok")
