# -*- coding: utf-8 -*-
"""Фігури до теми «EINTR: перервані виклики й перезапуск»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_restart_decision():
    """Розвилка: що робить ядро з викликом, обірваним сигналом."""
    W, H = 980, 530
    g = []

    g.append(fitbox(320, 20, 340, 52,
                    "задача спить усередині read()\nстан S — сон, який можна перервати",
                    size=13))
    g.append(arrow(490, 74, 490, 100))

    g.append(fitbox(320, 102, 340, 52,
                    "надходить сигнал: ядро ставить прапорець\nі будить задачу",
                    size=13))
    g.append(arrow(490, 156, 490, 182))

    g.append(fitbox(320, 184, 340, 52,
                    "цикл очікування виходить\nз кодом −ERESTARTSYS",
                    size=13, fill="#eef2f7"))
    g.append(arrow(490, 238, 490, 264))

    g.append(fitbox(50, 266, 880, 48,
                    "шлях виходу з ядра дивиться на диспозицію сигналу",
                    size=14, fill="#f7f3e8", stroke=MUTED))

    for cx in (180, 490, 800):
        g.append(arrow(cx, 316, cx, 352))

    g.append(fitbox(50, 354, 260, 62,
                    "обробника немає:\nсигнал проігноровано\nабо була зупинка й SIGCONT",
                    size=12))
    g.append(fitbox(360, 354, 260, 62,
                    "є обробник,\nвстановлений\nіз SA_RESTART", size=12))
    g.append(fitbox(670, 354, 260, 62,
                    "є обробник,\nвстановлений\nбез SA_RESTART", size=12))

    for cx in (180, 490, 800):
        g.append(arrow(cx, 418, cx, 448))

    g.append(fitbox(50, 450, 260, 56,
                    "виклик грають заново", size=13, fill="#eaf7ee"))
    g.append(fitbox(360, 450, 260, 56,
                    "обробник відпрацював —\nвиклик грають заново",
                    size=13, fill="#eaf7ee"))
    g.append(fitbox(670, 450, 260, 56,
                    "read() → −1,\nerrno = EINTR", size=13, fill="#fdecea"))

    render(os.path.join(IMG, 'restart-decision.svg'), W, H, *g,
           title="Розвилка перерваного системного виклику")


def fig_rewind_registers():
    """Механіка перезапуску: ядро відкручує лічильник команд на одну інструкцію."""
    W, H = 960, 330
    g = []

    g.append(text(240, 32, "що бачить ядро на виході з виклику", size=14, bold=True))
    g.append(text(720, 32, "правка перед поверненням", size=14, bold=True))

    left = [
        "orig_rax = 0 — номер __NR_read",
        "rax = −512 — це −ERESTARTSYS",
        "rip — адреса після syscall",
    ]
    right = [
        "rax ← orig_rax, тобто знову 0",
        "rip ← rip − 2, довжина syscall",
        "решта регістрів — незаймані",
    ]
    y = 52
    for a, b in zip(left, right):
        g.append(fitbox(40, y, 400, 48, a, size=13, fill="#eef2f7"))
        g.append(fitbox(520, y, 400, 48, b, size=13, fill="#eaf7ee"))
        y += 58

    g.append(arrow(448, 128, 512, 128))

    g.append(fitbox(40, 236, 880, 62,
                    "процесор виконує ту саму інструкцію syscall ще раз:\n"
                    "програма не бачить ні переривання, ні повторного входу в ядро",
                    size=13, fill="#f7f3e8", stroke=MUTED))

    render(os.path.join(IMG, 'rewind-registers.svg'), W, H, *g,
           title="Як ядро переграє системний виклик")


def fig_timeout_restart():
    """Чому виклик із тайм-аутом не можна просто зіграти заново."""
    W, H = 990, 370
    g = []

    g.append(text(255, 30, "якби ядро просто грало виклик заново", size=14, bold=True))
    g.append(text(735, 30, "блок перезапуску: залишок переносять", size=14, bold=True))

    left = [
        "poll(…, 1000 мс) — сигнал на 300-й мс",
        "знову poll(…, 1000 мс) — сигнал на 300-й мс",
        "знову poll(…, 1000 мс) — сигнал на 300-й мс",
    ]
    right = [
        "poll(…, 1000 мс) — сигнал на 300-й мс",
        "залишок 700 мс — сигнал на 300-й мс",
        "залишок 400 мс — сигнал на 300-й мс",
        "залишок 100 мс — більше ніхто не заважає",
    ]

    y = 48
    for s in left:
        g.append(fitbox(40, y, 430, 46, s, size=12))
        y += 54

    y = 48
    for s in right:
        g.append(fitbox(520, y, 430, 46, s, size=12))
        y += 54

    g.append(text(255, 232, "потік сигналів кожні 300 мс — відлік не рушає з місця",
                 size=12, color=MUTED))

    g.append(fitbox(40, 250, 430, 66,
                    "тайм-аут не настане ніколи:\nпрограма чекає довше, ніж просила",
                    size=13, fill="#fdecea"))
    g.append(fitbox(520, 250, 430, 66,
                    "час вичерпано рівно за обіцяну 1000 мс:\npoll() повертає 0",
                    size=13, fill="#eaf7ee"))

    render(os.path.join(IMG, 'timeout-restart.svg'), W, H, *g,
           title="Тайм-аут і перезапуск виклику")


def fig_alarm_race():
    """Перегони: SIGALRM встигає прийти до входу в блокуючий виклик."""
    W, H = 1000, 430
    g = []

    g.append(text(260, 30, "як прийом працює майже завжди", size=14, bold=True))
    g.append(text(745, 30, "а як він зривається", size=14, bold=True))

    left = [
        "alarm(1) — таймер заведено",
        "read() входить у ядро й засинає",
        "через секунду ядро доставляє SIGALRM",
        "обробник ставить прапорець,\nсплячий виклик перервано",
    ]
    right = [
        "alarm(1) — таймер заведено",
        "процес витіснено з процесора\nдовше ніж на секунду",
        "SIGALRM доставлено ЩЕ ДО входу в read()",
        "обробник ставить прапорець,\nале переривати ще нема чого",
    ]

    y = 50
    for a, b in zip(left, right):
        g.append(fitbox(40, y, 440, 54, a, size=12))
        g.append(fitbox(530, y, 440, 54, b, size=12))
        y += 62

    g.append(fitbox(40, y, 440, 56,
                    "read() → −1, errno = EINTR:\nтайм-аут спрацював вчасно",
                    size=13, fill="#eaf7ee"))
    g.append(fitbox(530, y, 440, 56,
                    "read() входить у ядро й спить\nбез жодного обмеження часу",
                    size=13, fill="#fdecea"))

    g.append(fitbox(40, y + 70, 930, 46,
                    "проміжок між обробником і входом у ядро "
                    "з простору користувача закрити нічим",
                    size=13, fill="#f7f3e8", stroke=MUTED))

    render(os.path.join(IMG, 'alarm-race.svg'), W, H, *g,
           title="Перегони тайм-ауту на SIGALRM")


if __name__ == '__main__':
    fig_restart_decision()
    fig_rewind_registers()
    fig_timeout_restart()
    fig_alarm_race()
    print("ok")
