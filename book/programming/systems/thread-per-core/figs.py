# -*- coding: utf-8 -*-
"""Фігури до теми «Архітектура Thread-per-core та Shared-Nothing».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

CORE_FILL   = "#eaf2fd"
CORE_LINE   = "#2457d6"
SHARD_FILL  = "#eafaf1"
SHARD_LINE  = "#27ae60"
LOCK_FILL   = "#fdecea"
LOCK_LINE   = "#c0392b"
WARN_FILL   = "#fff6e0"
WARN_LINE   = "#caa24a"
MEM_FILL    = "#fdf2e9"
MEM_LINE    = "#e67e22"

def boxlabel(f, x, y, w, h, s, fill=FILL, stroke=LINE, tcol=INK, size=12, sw=1.5, rx=6):
    """Прямокутник із підписом по центру; багаторядковий через список або \n."""
    if isinstance(s, str) and "\n" in s:
        s = s.split("\n")
    if isinstance(s, list):
        f.append(fitbox(x, y, w, h, s, size=size, fill=fill, stroke=stroke, sw=sw, color=tcol, rx=rx))
        return
    f.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=rx))
    fs = fit_font(s, w - 14, size, bold=True)
    f.append(text(x + w / 2, y + h / 2 + fs * 0.35, s, size=fs, color=tcol, bold=True))

def note(f, cx, y, w, lines, fill=WARN_FILL, stroke=WARN_LINE, size=11):
    """Рамка-висновок знизу фігури."""
    f.append(fitbox(cx - w / 2, y, w, 18 + size * 1.35 * len(lines), lines,
                    size=size, fill=fill, stroke=stroke))

def fig_tpc_vs_threadpool():
    W, H = 880, 430
    f = [text(W / 2, 28, "Порівняння архітектур: пул потоків зі спільною пам'яттю проти Thread-per-core", size=16, bold=True)]
    f.append(text(W / 2, 48, "Конкуренція за замки та кеш-інвалідація проти повної ізоляції ядер та шардування стану",
                  size=11, color=MUTED, italic=True))

    f.append(rect(30, 75, 395, 265, fill="#fffaf9", stroke=LOCK_LINE, sw=1.8, rx=8))
    f.append(text(227, 98, "Традиційний пул потоків (Shared Memory)", size=12.5, color=LOCK_LINE, bold=True))
    f.append(text(227, 115, "Конкуренція N потоків за спільний стан через м'ютекси", size=9.5, color=MUTED))

    boxlabel(f, 45, 135, 75, 42, ["Потік 1", "(Ядро 0)"], fill=LOCK_FILL, stroke=LOCK_LINE, size=9.5, tcol=LOCK_LINE)
    boxlabel(f, 130, 135, 75, 42, ["Потік 2", "(Ядро 1)"], fill=LOCK_FILL, stroke=LOCK_LINE, size=9.5, tcol=LOCK_LINE)
    boxlabel(f, 215, 135, 75, 42, ["Потік 3", "(Ядро 2)"], fill=LOCK_FILL, stroke=LOCK_LINE, size=9.5, tcol=LOCK_LINE)
    boxlabel(f, 300, 135, 75, 42, ["Потік N", "(Ядро K)"], fill=LOCK_FILL, stroke=LOCK_LINE, size=9.5, tcol=LOCK_LINE)

    f.append(arrow(82, 178, 160, 220, color=LOCK_LINE, sw=1.6))
    f.append(arrow(167, 178, 190, 220, color=LOCK_LINE, sw=1.6))
    f.append(arrow(252, 178, 235, 220, color=LOCK_LINE, sw=1.6))
    f.append(arrow(337, 178, 260, 220, color=LOCK_LINE, sw=1.6))

    boxlabel(f, 110, 220, 235, 40, ["Спільний замок (pthread_mutex_t)", "Вузьке місце: черги очікування"],
             fill="#ffffff", stroke=LOCK_LINE, size=10, tcol=LOCK_LINE)
    boxlabel(f, 75, 275, 305, 50, ["Спільна структура даних (Хеш-таблиця / Кеш)",
                                    "Cache line bouncing між ядрами CPU",
                                    "Втрати до 70-85% тактів на інвалідацію кешу"],
             fill=LOCK_FILL, stroke=LOCK_LINE, size=9.5, tcol=LOCK_LINE)

    f.append(rect(455, 75, 395, 265, fill="#f8fdf9", stroke=SHARD_LINE, sw=1.8, rx=8))
    f.append(text(652, 98, "Thread-per-core (Shared-Nothing)", size=12.5, color=SHARD_LINE, bold=True))
    f.append(text(652, 115, "1 закріплений потік на ядро, приватна пам'ять, нуль замків", size=9.5, color=MUTED))

    boxlabel(f, 470, 135, 115, 52, ["Ядро 0 (Потік 0)", "Event Loop", "Шард даних 0"],
             fill=SHARD_FILL, stroke=SHARD_LINE, size=9.5, tcol=SHARD_LINE)
    boxlabel(f, 595, 135, 115, 52, ["Ядро 1 (Потік 1)", "Event Loop", "Шард даних 1"],
             fill=SHARD_FILL, stroke=SHARD_LINE, size=9.5, tcol=SHARD_LINE)
    boxlabel(f, 720, 135, 115, 52, ["Ядро N (Потік N)", "Event Loop", "Шард даних N"],
             fill=SHARD_FILL, stroke=SHARD_LINE, size=9.5, tcol=SHARD_LINE)

    boxlabel(f, 470, 215, 365, 45, ["Між'ядерні SPSC кільцеві буфери (Ring Buffers)",
                                     "Асинхронний обмін повідомленнями (Message Passing)",
                                     "Кожне ядро працює виключно зі своїм L1/L2 кешем"],
             fill="#ffffff", stroke=SHARD_LINE, size=9.5, tcol=SHARD_LINE)

    f.append(arrow(527, 188, 527, 213, color=SHARD_LINE, sw=1.5))
    f.append(arrow(652, 188, 652, 213, color=SHARD_LINE, sw=1.5))
    f.append(arrow(777, 188, 777, 213, color=SHARD_LINE, sw=1.5))

    boxlabel(f, 470, 275, 365, 50, ["Локальна пам'ять NUMA для кожного ядра",
                                     "Нуль системних викликів блокування (Zero Lock Contention)",
                                     "Масштабованість, близька до строго лінійної"],
             fill=SHARD_FILL, stroke=SHARD_LINE, size=9.5, tcol=SHARD_LINE)

    note(f, W / 2, 355, 800,
         ["Пул зі спільною пам'яттю деградує на 32+ ядрах через конкуренцію за замки та інвалідацію кешу.",
          "Thread-per-core ізолює стан по ядрах: кожне ядро опрацьовує свій шард без синхронізаційних блокувань."])
    render(os.path.join(IMG, "tpc-vs-threadpool.svg"), W, H, *f)

def fig_cache_coherence_bouncing():
    W, H = 880, 420
    f = [text(W / 2, 28, "Апаратний колапс спільної пам'яті: Cache Line Bouncing у протоколі MESI", size=16, bold=True)]
    f.append(text(W / 2, 48, "Як паралельний запис в одну кеш-лінію паралізує міжпроцесорну шину (UPI / Infinity Fabric)",
                  size=11, color=MUTED, italic=True))

    f.append(rect(40, 75, 230, 255, fill=CORE_FILL, stroke=CORE_LINE, sw=1.8, rx=8))
    f.append(text(155, 100, "Ядро 0 (CPU Core 0)", size=12, color=CORE_LINE, bold=True))
    boxlabel(f, 55, 120, 200, 36, "Потік 0 виконує write(X)", fill="#ffffff", stroke=CORE_LINE, size=10)
    boxlabel(f, 55, 170, 200, 60, ["L1/L2 Кеш (64 байти)", "Рядок X: Стан MODIFIED (M)", "Ексклюзивне володіння"],
             fill="#ffffff", stroke=CORE_LINE, size=9.5)
    boxlabel(f, 55, 245, 200, 65, ["Отримано BusRdX від Ядра 32:", "1. Примусове скидання даних", "2. Перехід у стан INVALID (I)"],
             fill=LOCK_FILL, stroke=LOCK_LINE, size=9.5, tcol=LOCK_LINE)

    f.append(rect(305, 110, 270, 185, fill="#fffaf0", stroke=WARN_LINE, sw=1.8, rx=8))
    f.append(text(440, 135, "Міжпроцесорна шина (Interconnect)", size=11.5, color=WARN_LINE, bold=True))
    f.append(text(440, 153, "UPI / Infinity Fabric (Затримка: 60-120 нс)", size=9.5, color=MUTED))
    boxlabel(f, 320, 170, 240, 50, ["Транзакція BusRdX (Invalidate):", "Шина блокується для передачі", "кеш-лінії між сокетами"],
             fill="#ffffff", stroke=WARN_LINE, size=9.5)
    boxlabel(f, 320, 230, 240, 50, ["Швидкість доступу до пам'яті:", "L1 кеш: ~1 нс (4 такти)", "Cache Bounce: ~80-120 нс (300 тактів)"],
             fill=LOCK_FILL, stroke=LOCK_LINE, size=9.5, tcol=LOCK_LINE)

    f.append(arrow(257, 200, 318, 200, color=LOCK_LINE, sw=1.8))
    f.append(arrow(623, 200, 562, 200, color=LOCK_LINE, sw=1.8))

    f.append(rect(610, 75, 230, 255, fill=CORE_FILL, stroke=CORE_LINE, sw=1.8, rx=8))
    f.append(text(725, 100, "Ядро 32 (CPU Core 32)", size=12, color=CORE_LINE, bold=True))
    boxlabel(f, 625, 120, 200, 36, "Потік 32 виконує write(X)", fill="#ffffff", stroke=CORE_LINE, size=10)
    boxlabel(f, 625, 170, 200, 60, ["L1/L2 Кеш (64 байти)", "Рядок X: Стан INVALID (I)", "Кеш-промах! Запит на шину"],
             fill=LOCK_FILL, stroke=LOCK_LINE, size=9.5, tcol=LOCK_LINE)
    boxlabel(f, 625, 245, 200, 65, ["Отримано рядок X з Ядра 0:", "1. Запис нового значення", "2. Перехід у стан MODIFIED (M)"],
             fill="#ffffff", stroke=CORE_LINE, size=9.5)

    note(f, W / 2, 350, 800,
         ["Коли різні ядра пишуть у спільну змінну або лічильник, 64-байтна кеш-лінія безперервно «стрибає» між L1/L2 кешами.",
          "Цей ping-pong забирає до 300 тактів на кожну операцію, знецінюючи паралелізм багатоядерного процесора."])
    render(os.path.join(IMG, "cache-coherence-bouncing.svg"), W, H, *f)

def fig_numa_topology_sharding():
    W, H = 880, 420
    f = [text(W / 2, 28, "NUMA-топологія: локальний доступ проти віддаленого перетинання сокетів", size=16, bold=True)]
    f.append(text(W / 2, 48, "Thread-per-core прив'язує пам'ять шарду строго до локального NUMA-вузла (numa_alloc_onnode)",
                  size=11, color=MUTED, italic=True))

    f.append(rect(40, 75, 365, 255, fill=SHARD_FILL, stroke=SHARD_LINE, sw=1.8, rx=8))
    f.append(text(222, 98, "NUMA Вузол 0 (Socket 0)", size=12.5, color=SHARD_LINE, bold=True))
    boxlabel(f, 55, 115, 160, 48, ["Ядра 0..31", "Прив'язані потоки TPC"], fill=CORE_FILL, stroke=CORE_LINE, size=10, tcol=CORE_LINE)
    boxlabel(f, 230, 115, 160, 48, ["Локальна RAM Вузла 0", "DDR5 Канали 0..3"], fill=MEM_FILL, stroke=MEM_LINE, size=10, tcol=MEM_LINE)

    f.append(arrow(135, 165, 135, 205, color=SHARD_LINE, sw=1.8))
    f.append(arrow(310, 165, 310, 205, color=SHARD_LINE, sw=1.8))

    boxlabel(f, 55, 205, 335, 55, ["Шарди даних 0..31 (Shared-Nothing)",
                                    "Локальне виділення пам'яті (MPOL_BIND)",
                                    "Затримка доступу: ~45-55 нс (Local Access)"],
             fill="#ffffff", stroke=SHARD_LINE, size=9.5, tcol=SHARD_LINE)
    boxlabel(f, 55, 270, 335, 45, ["Швидкість: максимальна пропускна здатність шини пам'яті",
                                    "Нуль конфліктів із потоками іншого сокета"],
             fill=SHARD_FILL, stroke=SHARD_LINE, size=9, tcol=SHARD_LINE)

    f.append(rect(420, 130, 40, 140, fill="#fdfefe", stroke=WARN_LINE, sw=1.5, rx=4))
    f.append(text(440, 185, "UPI", size=10, color=WARN_LINE, bold=True))
    f.append(text(440, 205, "Шина", size=9, color=MUTED))

    f.append(line(390, 170, 420, 170, color=WARN_LINE, sw=1.8))
    f.append(line(460, 170, 490, 170, color=WARN_LINE, sw=1.8))
    f.append(line(390, 230, 420, 230, color=LOCK_LINE, sw=1.8, dash="4,3"))
    f.append(line(460, 230, 490, 230, color=LOCK_LINE, sw=1.8, dash="4,3"))

    f.append(rect(475, 75, 365, 255, fill=SHARD_FILL, stroke=SHARD_LINE, sw=1.8, rx=8))
    f.append(text(657, 98, "NUMA Вузол 1 (Socket 1)", size=12.5, color=SHARD_LINE, bold=True))
    boxlabel(f, 490, 115, 160, 48, ["Ядра 32..63", "Прив'язані потоки TPC"], fill=CORE_FILL, stroke=CORE_LINE, size=10, tcol=CORE_LINE)
    boxlabel(f, 665, 115, 160, 48, ["Локальна RAM Вузла 1", "DDR5 Канали 4..7"], fill=MEM_FILL, stroke=MEM_LINE, size=10, tcol=MEM_LINE)

    f.append(arrow(570, 165, 570, 205, color=SHARD_LINE, sw=1.8))
    f.append(arrow(745, 165, 745, 205, color=SHARD_LINE, sw=1.8))

    boxlabel(f, 490, 205, 335, 55, ["Шарди даних 32..63 (Shared-Nothing)",
                                    "Локальне виділення пам'яті (MPOL_BIND)",
                                    "Затримка доступу: ~45-55 нс (Local Access)"],
             fill="#ffffff", stroke=SHARD_LINE, size=9.5, tcol=SHARD_LINE)
    boxlabel(f, 490, 270, 335, 45, ["Віддалений доступ без TPC (Remote NUMA):",
                                    "Затримка: ~120-160 нс (втрата до 3x продуктивності)"],
             fill=LOCK_FILL, stroke=LOCK_LINE, size=9, tcol=LOCK_LINE)

    note(f, W / 2, 350, 800,
         ["На сучасних багатосокетних серверах читання пам'яті чужого процесора через шину UPI займає втричі більше часу.",
          "Thread-per-core локалізує структури даних на «своєму» NUMA-вузлі, усуваючи паразитний міжсокетний трафік."])
    render(os.path.join(IMG, "numa-topology-sharding.svg"), W, H, *f)

def fig_cross_core_messaging():
    W, H = 880, 430
    f = [text(W / 2, 28, "Між'ядерна комунікація: асинхронні черги SPSC та маршрутизація запитів", size=16, bold=True)]
    f.append(text(W / 2, 48, "Мережева карта розподіляє трафік через RSS; взаємодія між шардами виконується без замків",
                  size=11, color=MUTED, italic=True))

    boxlabel(f, 40, 80, 800, 48, ["Мережева карта (NIC) із підтримкою Receive Side Scaling (RSS) / Flow Director",
                                  "Апаратне хешування TCP кортежу (IP:Port) -> розкидання пакетів по апаратних чергах RX"],
             fill="#f0f4f8", stroke=LINE, size=10.5)

    f.append(arrow(220, 130, 220, 160, color=LINE, sw=1.6))
    f.append(arrow(660, 130, 660, 160, color=LINE, sw=1.6))
    f.append(text(175, 148, "RX Queue 0", size=9.5, color=MUTED, bold=True))
    f.append(text(615, 148, "RX Queue 1", size=9.5, color=MUTED, bold=True))

    f.append(rect(40, 165, 360, 165, fill=CORE_FILL, stroke=CORE_LINE, sw=1.8, rx=8))
    f.append(text(220, 185, "Ядро 0 (Потік 0 / Шард 0)", size=12, color=CORE_LINE, bold=True))
    boxlabel(f, 55, 195, 330, 36, "Event Loop (io_uring / epoll): отримано запит", fill="#ffffff", stroke=CORE_LINE, size=9.5)
    boxlabel(f, 55, 238, 330, 45, ["Ключ запиту належить Шарду 1 (hash(K) % N == 1)",
                                    "Прямий доступ до чужої пам'яті ЗАБОРОНЕНО!",
                                    "Формування асинхронного повідомлення Msg"],
             fill=WARN_FILL, stroke=WARN_LINE, size=9, tcol=WARN_LINE)
    boxlabel(f, 55, 290, 330, 30, "Швидкий запис у SPSC кільцевий буфер (Push)", fill="#ffffff", stroke=CORE_LINE, size=9.5)

    f.append(rect(415, 200, 50, 100, fill=SHARD_FILL, stroke=SHARD_LINE, sw=1.5, rx=6))
    f.append(text(440, 230, "SPSC", size=10, color=SHARD_LINE, bold=True))
    f.append(text(440, 248, "Ring", size=9.5, color=SHARD_LINE, bold=True))
    f.append(text(440, 265, "Buffer", size=9, color=MUTED))

    f.append(arrow(387, 240, 413, 240, color=SHARD_LINE, sw=1.8))
    f.append(arrow(467, 240, 493, 240, color=SHARD_LINE, sw=1.8))

    f.append(rect(480, 165, 360, 165, fill=CORE_FILL, stroke=CORE_LINE, sw=1.8, rx=8))
    f.append(text(660, 185, "Ядро 1 (Потік 1 / Шард 1)", size=12, color=CORE_LINE, bold=True))
    boxlabel(f, 495, 195, 330, 36, "Event Loop: пакетоване вилучення (Pop Batch)", fill="#ffffff", stroke=CORE_LINE, size=9.5)
    boxlabel(f, 495, 238, 330, 45, ["Виконання операції над локальним Шардом 1",
                                    "Локальний L1/L2 кеш, нуль блокувань",
                                    "Формування результату (Response)"],
             fill=SHARD_FILL, stroke=SHARD_LINE, size=9, tcol=SHARD_LINE)
    boxlabel(f, 495, 290, 330, 30, "Асинхронне повернення результату через ф'ючерс", fill="#ffffff", stroke=CORE_LINE, size=9.5)

    note(f, W / 2, 350, 800,
         ["Кожне ядро обробляє лише свої дані (no-sharing). Повідомлення передаються через SPSC кільце.",
          "Пакетування блоків та вирівнювання кеш-ліній усувають накладні витрати на бар'єри."])
    render(os.path.join(IMG, "cross-core-messaging.svg"), W, H, *f)

if __name__ == '__main__':
    fig_tpc_vs_threadpool()
    fig_cache_coherence_bouncing()
    fig_numa_topology_sharding()
    fig_cross_core_messaging()
    print('Всі фігури згенеровано успішно.')
