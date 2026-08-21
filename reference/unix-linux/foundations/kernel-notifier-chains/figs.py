# -*- coding: utf-8 -*-
"""Фігури до теми «Ланцюжки сповіщень ядра (notifier chains)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

GREEN_FILL = "#eaf7ef"
RED_FILL   = "#fdecea"
BLUE_FILL  = "#eaf0fd"
GREY_FILL  = "#f4f6f8"
YELLOW_FILL = "#fef9e7"


# ── 1. Топологія ланцюжка: вказівник head, пріоритетне впорядкування та вставка ──
def fig_chain_topology():
    W, H = 1200, 560
    f = []

    f.append(text(600, 32, "СТРУКТУРА І ВПОРЯДКУВАННЯ NOTIFIER CHAIN У ПАМ'ЯТІ ЯДРА", size=14, color=MUTED, bold=True))

    # Голова ланцюжка
    f.append(fitbox(40, 70, 220, 110,
                    "ГОЛОВА ЛАНЦЮЖКА\n(atomic / blocking / srcu)\n───────────────\nзамок синхронізації\nhead → struct notifier_block*",
                    size=12, bold=True, fill=BLUE_FILL, stroke=NEG))

    # Вузол 1: priority 100
    f.append(fitbox(320, 70, 240, 110,
                    "struct notifier_block #1\npriority = 100\n───────────────\nnotifier_call = audit_cb\nnext ───────────►",
                    size=12, fill=GREY_FILL, stroke=INK))

    # Вузол 2: priority 0
    f.append(fitbox(620, 70, 240, 110,
                    "struct notifier_block #2\npriority = 0\n───────────────\nnotifier_call = fib_event\nnext ───────────►",
                    size=12, fill=GREY_FILL, stroke=INK))

    # Вузол 3: priority -50
    f.append(fitbox(920, 70, 240, 110,
                    "struct notifier_block #3\npriority = -50\n───────────────\nnotifier_call = stats_log\nnext = NULL",
                    size=12, fill=GREY_FILL, stroke=INK))

    # Стрілки між головою та вузлами
    f.append(arrow(262, 125, 318, 125, color=NEG, sw=2))
    f.append(arrow(562, 125, 618, 125, color=INK, sw=1.8))
    f.append(arrow(862, 125, 918, 125, color=INK, sw=1.8))

    # Новий вузол, який реєструється з priority = 50
    f.append(fitbox(420, 270, 290, 105,
                    "НОВИЙ ПЕРЕДПЛАТНИК\nstruct notifier_block (priority = 50)\n───────────────\nвставляється між 100 і 0\nза спаданням priority",
                    size=12, bold=True, fill=YELLOW_FILL, stroke=FIELD))

    # Пунктирні стрілки вставки
    f.append(arrow(430, 268, 410, 182, color=FIELD, sw=1.6))
    f.append(arrow(680, 268, 710, 182, color=FIELD, sw=1.6))

    # Нижня плашка: протокол обходу події
    f.append(fitbox(40, 420, 1120, 95,
                    "ПОТІК ВИКЛИКУ: notifier_call_chain(head, action, data)\n"
                    "1. Читач захоплює блокування (spin_lock / down_read / srcu_read_lock) і йде за вказівниками next.\n"
                    "2. Кожен обробник отримує: (struct notifier_block *nb, unsigned long action, void *data).\n"
                    "3. Код повернення: NOTIFY_OK (продовжити), NOTIFY_STOP (зупинити), NOTIFY_BAD (помилка, перервати ланцюг).",
                    size=12, bold=False, fill=BG, stroke=INK))

    render(os.path.join(IMG, 'notifier-chain-topology.svg'), W, H, *f,
           title="Топологія ланцюжка сповіщень: впорядкування за пріоритетом і протокол виклику")


# ── 2. Чотири типи ланцюжків у ядрі Linux ──────────────────────────────────
def fig_four_types():
    W, H = 1240, 620
    f = []

    f.append(text(620, 32, "ЧОТИРИ ТИПИ NOTIFIER CHAINS: МЕХАНІЗМИ СИНХРОНІЗАЦІЇ ТА ОБМЕЖЕННЯ", size=14, color=MUTED, bold=True))

    cols = [
        ("ATOMIC",
         "atomic_notifier_head",
         "Замок: spinlock_t\n"
         "Контекст: Атомарний (IRQ, softirq, переривання)\n"
         "Сон / I/O: СУВОРО ЗАБОРОНЕНО\n"
         "Алокація: Тільки GFP_ATOMIC\n"
         "Ціна читача: Захоплення spinlock\n"
         "Типові ланцюжки: panic_notifier_list, die_chain",
         RED_FILL, POS),
        ("BLOCKING",
         "blocking_notifier_head",
         "Замок: struct rw_semaphore\n"
         "Контекст: Процес (syscall, kthread, workqueue)\n"
         "Сон / I/O: ДОЗВОЛЕНО (сон, м'ютекси, дисковий I/O)\n"
         "Алокація: GFP_KERNEL\n"
         "Ціна читача: down_read(rwsem)\n"
         "Типові ланцюжки: reboot_notifier_list, pm_chain",
         BLUE_FILL, NEG),
        ("RAW",
         "raw_notifier_head",
         "Замок: ВІДСУТНІЙ (зовнішній замок)\n"
         "Контекст: Визначається підсистемою-власником\n"
         "Сон / I/O: Залежить від зовнішнього блокування\n"
         "Алокація: Відповідно до контексту\n"
         "Ціна читача: Нульова у ланцюжку\n"
         "Типові ланцюжки: Рання ініціалізація CPU, пастки",
         GREY_FILL, INK),
        ("SRCU",
         "srcu_notifier_head",
         "Замок: Sleepable RCU + mutex\n"
         "Контекст: Процес із паралельним читанням\n"
         "Сон / I/O: ДОЗВОЛЕНО всередині обробника\n"
         "Алокація: GFP_KERNEL\n"
         "Ціна читача: srcu_read_lock (без замків!)\n"
         "Типові ланцюжки: netdev_chain, cpu_chain",
         GREEN_FILL, FIELD),
    ]

    col_w = 270
    gap = 20
    start_x = 40

    for i, (name, struct_name, desc, fill_col, border_col) in enumerate(cols):
        cx = start_x + i * (col_w + gap)
        f.append(fitbox(cx, 60, col_w, 48, name, size=14, bold=True, fill=fill_col, stroke=border_col))
        f.append(fitbox(cx, 114, col_w, 36, struct_name, size=11, bold=True, fill=BG, stroke=MUTED))
        f.append(fitbox(cx, 156, col_w, 350, desc, size=12, fill=fill_col, stroke=border_col))

    f.append(fitbox(40, 526, 1160, 64,
                    "ЗОЛОТЕ ПРАВИЛО ВИБОРУ: якщо викликач перебуває в перериванні — Atomic; "
                    "якщо обробники мають спати й читаються рідко — Blocking; "
                    "якщо читання надчасте й допускає сон — SRCU; "
                    "якщо блокування повністю зовнішнє — Raw.",
                    size=12, bold=True, fill=BG, stroke=INK))

    render(os.path.join(IMG, 'four-chain-types.svg'), W, H, *f,
           title="Порівняння чотирьох типів ланцюжків сповіщень ядра Linux")


# ── 3. Потік сповіщень мережевого стека: netdev_chain ──────────────────────
def fig_netdev_flow():
    W, H = 1200, 580
    f = []

    f.append(text(600, 32, "ЖИТТЄВИЙ ЦИКЛ ПОДІЇ МЕРЕЖЕВОГО ПРИСТРОЮ (netdev_chain)", size=14, color=MUTED, bold=True))

    # Джерело події
    f.append(fitbox(40, 70, 300, 110,
                    "ДЖЕРЕЛО ПОДІЇ\nip link set eth0 down\n───────────────\ndev_close() / dev_change_flags()\nгенерує подію NETDEV_DOWN",
                    size=12, bold=True, fill=YELLOW_FILL, stroke=INK))

    # Виклик розсилки
    f.append(fitbox(400, 70, 380, 110,
                    "ДИСПЕТЧЕР СПОВІЩЕНЬ\ncall_netdevice_notifiers(NETDEV_DOWN, dev)\n───────────────\nвхід: srcu_read_lock(&netdev_chain.srcu)\nобхід черги struct notifier_block*",
                    size=12, bold=True, fill=BLUE_FILL, stroke=NEG))

    f.append(arrow(342, 125, 398, 125, color=INK, sw=2))

    # Передплатники
    f.append(fitbox(840, 60, 320, 80,
                    "FIB / IP ROUTING (fib_netdev_event)\nскидає маршрути через eth0\nповертає NOTIFY_OK",
                    size=11, fill=GREEN_FILL, stroke=FIELD))

    f.append(fitbox(840, 150, 320, 80,
                    "ARP / NEIGHBOUR (arp_netdev_event)\nочищає кеш сусідів для eth0\nповертає NOTIFY_OK",
                    size=11, fill=GREEN_FILL, stroke=FIELD))

    f.append(fitbox(840, 240, 320, 80,
                    "AF_PACKET / SNIFFER (packet_notifier)\nповідомляє сокети про зміну стану\nповертає NOTIFY_OK",
                    size=11, fill=GREEN_FILL, stroke=FIELD))

    f.append(fitbox(840, 330, 320, 80,
                    "BONDING / TEAM (bond_netdev_event)\nперемикає трафік на резервний порт\nповертає NOTIFY_OK",
                    size=11, fill=GREEN_FILL, stroke=FIELD))

    # Стрілки від диспетчера до передплатників
    f.append(arrow(782, 100, 838, 100, color=NEG, sw=1.5))
    f.append(arrow(782, 115, 838, 190, color=NEG, sw=1.5))
    f.append(arrow(782, 130, 838, 280, color=NEG, sw=1.5))
    f.append(arrow(782, 145, 838, 370, color=NEG, sw=1.5))

    # Вихід та завершення
    f.append(fitbox(400, 260, 380, 120,
                    "РЕЗУЛЬТАТ ОБХОДУ\n───────────────\n1. Усі обробники повернули NOTIFY_OK\n2. srcu_read_unlock(&netdev_chain.srcu)\n3. Зміна стану eth0 успішно зафіксована",
                    size=12, bold=True, fill=GREEN_FILL, stroke=FIELD))

    f.append(arrow(590, 182, 590, 258, color=FIELD, sw=2))

    # Нижня панель: вето та відкат
    f.append(fitbox(40, 440, 1120, 100,
                    "ВЕТО ТА ДВОФАЗНИЙ ПРОТОКОЛ (NETDEV_PRECHANGEMTU, CPU_UP_PREPARE):\n"
                    "Якщо будь-який обробник повертає NOTIFY_BAD, обхід негайно припиняється.\n"
                    "Ядро ініціює компенсуюче повідомлення (наприклад, NETDEV_CHANGEMTU_CANCEL або CPU_UP_CANCELED),\n"
                    "дозволяючи попереднім підсистемам відкотити тимчасово змінений стан.",
                    size=12, bold=False, fill=BG, stroke=POS))

    render(os.path.join(IMG, 'netdev-event-flow.svg'), W, H, *f,
           title="Потік сповіщень мережевого стека: реакція підсистем на подію NETDEV_DOWN")


if __name__ == '__main__':
    fig_chain_topology()
    fig_four_types()
    fig_netdev_flow()
    print("ok")
