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
PURPLE_FILL = "#f3e8ff"


def fig_fast_slow_path():
    W, H = 1100, 560
    p = []

    # Title
    p.append(text(550, 35, "Шляхи виконання Futex: Fast Path (Userspace) vs Slow Path (Kernel)", size=17, bold=True))

    # Fast Path box (Left)
    p.append(rect(40, 60, 490, 470, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(285, 95, "Fast Path (без конкуренції)", size=16, bold=True, color=FIELD))
    p.append(text(285, 118, "Виконується 100% у просторі користувача", size=13, color=MUTED))

    p.append(fitbox(70, 145, 430, 55, "Потік А: lock()\nСпроба CAS (0 -> 1) за адресою uaddr", size=14, fill=BLUE_FILL, stroke=NEG, bold=True))
    p.append(arrow(285, 200, 285, 235, color=FIELD, sw=2))

    p.append(fitbox(70, 235, 430, 60, "Апаратна інструкція CPU\ncmpxchg / LDREX-STREX\nОновлення пам'яті в L1/L2 кеші", size=13, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(285, 295, 285, 330, color=FIELD, sw=2))

    p.append(fitbox(70, 330, 430, 65, "Результат: УСПІХ (М'ютекс захоплено)\nВиклику sys_futex() НЕМАЄ\nЗатримка: ~5-15 тактів CPU (~2-5 нс)", size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))

    p.append(text(285, 435, "Межа між простором користувача та ядром НЕ перетинається", size=12, color=FIELD, italic=True))
    p.append(text(285, 460, "Контекст не зберігається, TLB не скидається", size=12, color=MUTED))

    # Slow Path box (Right)
    p.append(rect(570, 60, 490, 470, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(815, 95, "Slow Path (наявна конкуренція)", size=16, bold=True, color=POS))
    p.append(text(815, 118, "Залучення ядра Linux для засинання", size=13, color=MUTED))

    p.append(fitbox(600, 145, 430, 55, "Потік Б: lock()\nСпроба CAS повертає 1 (Зайнято)", size=14, fill=RED_FILL, stroke=POS, bold=True))
    p.append(arrow(815, 200, 815, 235, color=POS, sw=2))

    p.append(fitbox(600, 235, 430, 60, "Системний виклик sys_futex(FUTEX_WAIT)\nПерехід у режим ядра (syscall / sysenter)\nАтомарна перевірка *uaddr == val під hb->lock", size=13, fill=WARM_FILL, stroke=POS))
    p.append(arrow(815, 295, 815, 330, color=POS, sw=2))

    p.append(fitbox(600, 330, 430, 65, "Додавання потоку в futex_hash_bucket\nПереведення потоку в стан TASK_INTERRUPTIBLE\nЗатримка: ~1000-2000 тактів CPU (~0.3-0.7 мкс)", size=13, fill=RED_FILL, stroke=POS, bold=True))

    p.append(text(815, 435, "Повне збереження контексту та виклик планувальника", size=12, color=POS, italic=True))
    p.append(text(815, 460, "Пробудження іншим потоком через FUTEX_WAKE", size=12, color=MUTED))

    render(os.path.join(IMG, 'futex-fast-slow-path.svg'), W, H, *p,
           title="Шляхи виконання Futex: Fast Path vs Slow Path")


def fig_hash_buckets():
    W, H = 1100, 580
    p = []

    # Title
    p.append(text(550, 35, "Внутрішня структура хеш-таблиці Futex у ядрі Linux", size=17, bold=True))

    # Global Hash Table container
    p.append(rect(40, 65, 1020, 480, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(550, 95, "Глобальна системна хеш-таблиця futex_queues (масив futex_hash_bucket)", size=15, bold=True))

    # Bucket 0
    p.append(rect(70, 125, 280, 390, fill=BLUE_FILL, stroke=NEG, rx=8))
    p.append(text(210, 155, "futex_hash_bucket [0]", size=14, bold=True, color=NEG))
    p.append(fitbox(90, 175, 240, 45, "Spinlock (hb->lock)", size=13, fill=WARM_FILL, stroke=POS))
    p.append(fitbox(90, 235, 240, 45, "Wait Queue (plist_head)", size=13, fill=BG, stroke=LINE))
    p.append(arrow(210, 280, 210, 310, color=NEG, sw=1.8))
    p.append(fitbox(90, 310, 240, 85, "struct futex_q\n- key: Page/MM/Offset\n- task: Thread 101\n- bitset: FUTEX_BITSET_MATCH", size=12, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(210, 395, 210, 420, color=NEG, sw=1.8))
    p.append(fitbox(90, 420, 240, 75, "struct futex_q\n- key: Page/MM/Offset\n- task: Thread 105", size=12, fill=GREEN_FILL, stroke=FIELD))

    # Bucket i (Hash lookup result)
    p.append(rect(410, 125, 280, 390, fill=PURPLE_FILL, stroke=LINE, rx=8))
    p.append(text(550, 155, "futex_hash_bucket [i]", size=14, bold=True))
    p.append(fitbox(430, 175, 240, 45, "Spinlock (hb->lock)", size=13, fill=WARM_FILL, stroke=POS))
    p.append(fitbox(430, 235, 240, 45, "Wait Queue (plist_head)", size=13, fill=BG, stroke=LINE))
    p.append(arrow(550, 280, 550, 310, color=LINE, sw=1.8))
    p.append(fitbox(430, 310, 240, 85, "struct futex_q\n- key: struct futex_key\n- task: Thread 204\n- uaddr: 0x7fff5008", size=12, fill=GREEN_FILL, stroke=FIELD))

    # Bucket N-1
    p.append(rect(750, 125, 280, 390, fill=GREY_FILL, stroke=MUTED, rx=8))
    p.append(text(890, 155, "futex_hash_bucket [N-1]", size=14, bold=True, color=MUTED))
    p.append(fitbox(770, 175, 240, 45, "Spinlock (hb->lock)", size=13, fill=WARM_FILL, stroke=POS))
    p.append(fitbox(770, 235, 240, 45, "Wait Queue (порожня)", size=13, fill=BG, stroke=MUTED))

    # Hash formula note
    p.append(text(550, 528, "Хеш-ключ hash_futex(key) обчислюється за фізичною адресою сторінки (shared) або mm_struct + uaddr (private)", size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'futex-hash-buckets.svg'), W, H, *p,
           title="Структура хеш-таблиці futex у ядрі Linux")


def fig_cmp_requeue():
    W, H = 1100, 580
    p = []

    # Title
    p.append(text(550, 35, "Оптимізація FUTEX_CMP_REQUEUE для умовних змінних (Condition Variables)", size=17, bold=True))

    # Before requeue box
    p.append(rect(40, 65, 490, 470, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(285, 95, "До виклику: 4 потоки чекають на Condvar", size=15, bold=True, color=POS))

    p.append(fitbox(70, 130, 430, 65, "Condvar Futex Bucket (uaddr_cond)\nWait Queue: Thread A, Thread B, Thread C, Thread D", size=13, fill=RED_FILL, stroke=POS, bold=True))

    p.append(text(285, 215, "Проблема без CMP_REQUEUE (Thundering Herd):", size=13, bold=True, color=POS))
    p.append(fitbox(70, 235, 430, 90, "Викликом WAKE пробуджуються всі 4 потоки.\nУсі 4 повертаються у юзерспейс і змагаються\nза м'ютекс. 1 захоплює, 3 знову йдуть у ядро!\nРезультат: 6 марних перемикань контексту.", size=12, fill=WARM_FILL, stroke=POS))

    p.append(fitbox(70, 350, 430, 60, "Mutex Futex Bucket (uaddr_mutex)\nWait Queue: (Порожня або 1 власник)", size=13, fill=BLUE_FILL, stroke=NEG))

    # After requeue box
    p.append(rect(570, 65, 490, 470, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(815, 95, "Після FUTEX_CMP_REQUEUE(wake=1, requeue=3)", size=15, bold=True, color=FIELD))

    p.append(fitbox(600, 130, 430, 65, "Condvar Futex Bucket (uaddr_cond)\nWait Queue: Порожня (усі перенесені)", size=13, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(815, 205, 815, 240, color=FIELD, sw=2))

    p.append(fitbox(600, 240, 430, 90, "Ядро атомарно:\n1. Пробуджує Thread A (wake=1) у юзерспейс.\n2. Переносить Thread B, C, D (requeue=3) з черги\n   condvar прямо в чергу mutex усередині ядра!", size=12, fill=GREEN_FILL, stroke=FIELD, bold=True))

    p.append(arrow(815, 340, 815, 375, color=FIELD, sw=2))

    p.append(fitbox(600, 375, 430, 65, "Mutex Futex Bucket (uaddr_mutex)\nWait Queue: Thread B, Thread C, Thread D", size=13, fill=PURPLE_FILL, stroke=LINE, bold=True))

    p.append(text(815, 465, "Нуль марних переходів у простір користувача для заблокованих потоків!", size=12, color=FIELD, italic=True))

    render(os.path.join(IMG, 'futex-cmp-requeue.svg'), W, H, *p,
           title="Перепідключення черги FUTEX_CMP_REQUEUE")


if __name__ == '__main__':
    fig_fast_slow_path()
    fig_hash_buckets()
    fig_cmp_requeue()
    print("SVGs successfully generated!")
