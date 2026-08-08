# -*- coding: utf-8 -*-
"""Фігури до теми «Сокет як дескриптор»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_behind_the_number():
    """Спільний шлях до struct file і розходження з таблиці операцій."""
    W, H = 980, 440
    g = []

    g.append(fitbox(290, 18, 400, 48,
                    "таблиця дескрипторів процесу\nfd 3 → struct file", size=13))
    g.append(arrow(490, 66, 490, 88, sw=1.6))
    g.append(fitbox(270, 90, 440, 48,
                    "struct file: прапорці, лічильник посилань,\n"
                    "вказівник на таблицю операцій", size=13))

    g.append(arrow(400, 138, 240, 178, sw=1.6))
    g.append(arrow(580, 138, 740, 178, sw=1.6))

    # ── ліва гілка: звичайний файл ──────────────────────────────────────
    g.append(text(60, 172, "звичайний файл", size=14, anchor="start", bold=True))
    g.append(fitbox(60, 180, 350, 44, "операції файлової системи", size=13,
                    fill="#eef2f7"))
    g.append(fitbox(60, 236, 350, 44, "inode → кеш сторінок → диск", size=13))
    g.append(fitbox(60, 292, 350, 56,
                    "вміст лежить увесь і чекає:\nє позиція, працює lseek", size=13,
                    fill="#eaf7ee"))

    # ── права гілка: сокет ──────────────────────────────────────────────
    g.append(text(570, 172, "сокет", size=14, anchor="start", bold=True))
    g.append(fitbox(570, 180, 350, 44, "операції сокета", size=13, fill="#eef2f7"))
    g.append(fitbox(570, 236, 350, 44, "стан протоколу й мережевий стек", size=13))
    g.append(fitbox(570, 292, 350, 56,
                    "буфер прийому · буфер передачі\nпозиції немає, lseek → ESPIPE",
                    size=13, fill="#fdecea"))

    g.append(fitbox(60, 366, 860, 52,
                    "усе вище таблиці операцій спільне: dup, close, fcntl, fork, epoll\n"
                    "розходження починається рівно з неї", size=13,
                    fill="#f7f3e8", stroke=MUTED))

    render(os.path.join(IMG, 'behind-the-number.svg'), W, H, *g,
           title="Що стоїть за дескриптором файлу і за дескриптором сокета")


def fig_two_queues():
    """Дві черги сокета і те, як з них виводиться готовність."""
    W, H = 980, 400
    g = []

    g.append(text(60, 46, "програма", size=14, anchor="start", bold=True))
    g.append(text(920, 46, "мережа", size=14, anchor="end", bold=True))

    # ── сокет посередині ────────────────────────────────────────────────
    g.append(rect(360, 70, 270, 230, fill="#ffffff"))
    g.append(text(495, 96, "сокет у ядрі", size=14, bold=True))
    g.append(fitbox(380, 116, 230, 60,
                    "буфер прийому\n12 КіБ із 128 КіБ", size=13, fill="#eef2f7"))
    g.append(fitbox(380, 214, 230, 60,
                    "буфер передачі\nвільно 6 КіБ із 16 КіБ", size=13, fill="#eef2f7"))

    # ── ліворуч: програма ───────────────────────────────────────────────
    g.append(text(250, 132, "read() бере, що вже прийшло", size=12, color=MUTED))
    g.append(arrow(374, 152, 130, 152, sw=1.6))
    g.append(text(250, 230, "write() кладе й повертається", size=12, color=MUTED))
    g.append(arrow(130, 250, 374, 250, sw=1.6))

    # ── праворуч: мережа ────────────────────────────────────────────────
    g.append(text(760, 132, "пакети приходять", size=12, color=MUTED))
    g.append(arrow(880, 152, 622, 152, sw=1.6))
    g.append(text(760, 230, "ядро відправляє далі", size=12, color=MUTED))
    g.append(arrow(622, 250, 880, 250, sw=1.6))

    g.append(fitbox(60, 316, 860, 62,
                    "готовий до читання = у буфері прийому щось є · "
                    "готовий до запису = у буфері передачі є місце\n"
                    "буфер прийому переповнився → оголошене вікно нуль → відправник спиняється",
                    size=13, fill="#f7f3e8", stroke=MUTED))

    render(os.path.join(IMG, 'two-queues.svg'), W, H, *g,
           title="Дві черги сокета: прийом і передача")


def fig_descriptor_vs_connection():
    """Життя дескриптора коротше за життя з'єднання з обох кінців."""
    W, H = 980, 380
    g = []

    g.append(text(40, 88, "дескриптор", size=14, anchor="start", bold=True))
    row_a = [(170, "socket()"), (330, "connect()"), (490, "dup() → 2"),
             (650, "close() → 1"), (810, "close() → 0")]
    for x, s in row_a:
        g.append(fitbox(x, 62, 150, 50, s, size=13, fill="#eef2f7"))

    g.append(text(40, 224, "з'єднання", size=14, anchor="start", bold=True))
    row_b = [(330, "встановлено"), (490, "передає далі"), (810, "аж тепер FIN")]
    for x, s in row_b:
        g.append(fitbox(x, 198, 150, 50, s, size=13, fill="#eaf7ee"))

    # напівзакриття діє на з'єднання, не на дескриптор
    g.append(text(560, 158, "shutdown(WR)", size=12, color=MUTED, anchor="end"))
    g.append(arrow(575, 116, 575, 194, color=MUTED, sw=1.4))

    g.append(fitbox(40, 288, 460, 62,
                    "close() прибирає лише запис у таблиці;\n"
                    "розмова закінчується на останньому посиланні", size=13,
                    fill="#f7f3e8", stroke=MUTED))
    g.append(fitbox(540, 288, 400, 62,
                    "TIME_WAIT: стан живе в ядрі далі,\n"
                    "уже без жодного дескриптора", size=13,
                    fill="#f7f3e8", stroke=MUTED))
    g.append(arrow(885, 252, 885, 284, color=MUTED, sw=1.4))

    render(os.path.join(IMG, 'descriptor-vs-connection.svg'), W, H, *g,
           title="Дескриптор і з'єднання: різні терміни життя")


if __name__ == '__main__':
    fig_behind_the_number()
    fig_two_queues()
    fig_descriptor_vs_connection()
    print("ok")
