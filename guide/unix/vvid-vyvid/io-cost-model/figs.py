# -*- coding: utf-8 -*-
"""Генератор схем для теми 'Скільки коштує ввід-вивід'."""

import sys, os

# 4 рівні вгору до кореня, де лежить scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_copy_chains():
    """Схема шляхів копіювання даних та перемикання контексту: read/write vs sendfile vs splice vs io_uring."""
    w, h = 980, 620
    frags = []

    # Рівень 1: Простір користувача (Ring 3)
    frags.append(rect(20, 20, 940, 120, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(490, 40, "ПРОСТІР КОРИСТУВАЧА (USER SPACE, RING 3)", size=13, color="#475569", bold=True))

    # Розділювальна смуга межі ядра
    frags.append(rect(20, 150, 940, 40, fill="#e0f2fe", stroke="#38bdf8", sw=1.5, rx=6))
    frags.append(text(490, 175, "МЕЖА СИСТЕМНОГО ВИКЛИКУ (SYSCALL BOUNDARY: RING 3 ↔ RING 0)", size=12, color="#0369a1", bold=True))

    # Рівень 2: Простір ядра та апаратний рівень (Ring 0 & Hardware)
    frags.append(rect(20, 200, 940, 340, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(490, 222, "ПРОСТІР ЯДРА ТА АПАРАТНИЙ ДРАЙВЕР (PAGE CACHE, SOCK BUF, DMA)", size=13, color="#334155", bold=True))

    # Стовпець 1: Традиційний read() + write() (4 копії: 2 вхідні зліва, 2 вихідні справа)
    col1_x = 35
    frags.append(rect(col1_x, 55, 215, 75, fill="#ffffff", stroke="#ef4444", sw=1.2, rx=6))
    frags.append(text(col1_x + 107, 72, "1. Класичний read/write", size=11, color="#b91c1c", bold=True))
    frags.append(fitbox(col1_x + 10, 80, 195, 42, "Буфер користувача (RAM)\nchar buf[64KB]", size=10, pad=3, fill="#fef2f2", stroke="#f87171"))

    # Ядро стовпець 1: зліва Page cache та Диск, справа Socket buffer та NIC
    frags.append(fitbox(col1_x + 10, 235, 92, 45, "Page Cache\n(DMA з диска)", size=9, pad=2, fill="#ffffff", stroke="#ef4444"))
    frags.append(arrow(col1_x + 56, 235, col1_x + 56, 122, color="#dc2626", sw=1.5))
    frags.append(fitbox(col1_x + 10, 310, 92, 45, "Диск SSD\n(Джерело)", size=9, pad=2, fill="#ffffff", stroke="#64748b"))
    frags.append(arrow(col1_x + 56, 310, col1_x + 56, 280, color="#dc2626", sw=1.5))

    frags.append(fitbox(col1_x + 112, 235, 92, 45, "Socket Buf\n(sk_buff)", size=9, pad=2, fill="#ffffff", stroke="#ef4444"))
    frags.append(arrow(col1_x + 158, 122, col1_x + 158, 235, color="#dc2626", sw=1.5))
    frags.append(fitbox(col1_x + 112, 310, 92, 45, "Мережева NIC\n(TX ring)", size=9, pad=2, fill="#ffffff", stroke="#64748b"))
    frags.append(arrow(col1_x + 158, 280, col1_x + 158, 310, color="#dc2626", sw=1.5))

    # Стовпець 2: sendfile() (2 копії)
    col2_x = 275
    frags.append(rect(col2_x, 55, 215, 75, fill="#ffffff", stroke="#f59e0b", sw=1.2, rx=6))
    frags.append(text(col2_x + 107, 72, "2. sendfile() (Zero-Copy)", size=11, color="#b45309", bold=True))
    frags.append(fitbox(col2_x + 10, 80, 195, 42, "Лише дескриптори fd_in, fd_out\n(Без копії в user space)", size=10, pad=3, fill="#fefce8", stroke="#fbbf24"))

    # Ядро стовпець 2
    frags.append(fitbox(col2_x + 10, 235, 195, 45, "1. Page Cache (RAM)\nDMA читання з SSD", size=10, pad=3, fill="#ffffff", stroke="#f59e0b"))
    frags.append(arrow(col2_x + 107, 280, col2_x + 107, 310, color="#f59e0b", sw=1.5))
    frags.append(fitbox(col2_x + 10, 310, 195, 45, "2. Socket Buffer (sk_buff)\nТільки покажчики (SG-DMA)", size=10, pad=3, fill="#ffffff", stroke="#f59e0b"))
    frags.append(arrow(col2_x + 107, 355, col2_x + 107, 385, color="#f59e0b", sw=1.5))
    frags.append(fitbox(col2_x + 10, 385, 195, 45, "3. TX Ring Мережевої карти\nScatter-Gather DMA з RAM", size=10, pad=3, fill="#ffffff", stroke="#64748b"))

    # Стовпець 3: splice() (0 CPU копій)
    col3_x = 515
    frags.append(rect(col3_x, 55, 215, 75, fill="#ffffff", stroke="#06b6d4", sw=1.2, rx=6))
    frags.append(text(col3_x + 107, 72, "3. splice() через Pipe", size=11, color="#0e7490", bold=True))
    frags.append(fitbox(col3_x + 10, 80, 195, 42, "splice(fd_in, pipe, pipe, fd_out)\nКерування потоком у Ring 3", size=10, pad=3, fill="#ecfeff", stroke="#22d3ee"))

    # Ядро стовпець 3
    frags.append(fitbox(col3_x + 10, 235, 195, 45, "1. Вхідний дескриптор\nДжерело даних (Socket/File)", size=10, pad=3, fill="#ffffff", stroke="#06b6d4"))
    frags.append(arrow(col3_x + 107, 280, col3_x + 107, 310, color="#06b6d4", sw=1.5))
    frags.append(fitbox(col3_x + 10, 310, 195, 45, "2. pipe_buffer (кільце)\nПередача struct page*", size=10, pad=3, fill="#ffffff", stroke="#06b6d4"))
    frags.append(arrow(col3_x + 107, 355, col3_x + 107, 385, color="#06b6d4", sw=1.5))
    frags.append(fitbox(col3_x + 10, 385, 195, 45, "3. Вихідний дескриптор\nПриймач даних (Socket/File)", size=10, pad=3, fill="#ffffff", stroke="#64748b"))

    # Стовпець 4: io_uring (0 syscalls в гарячому циклі)
    col4_x = 745
    frags.append(rect(col4_x, 55, 205, 75, fill="#ffffff", stroke="#10b981", sw=1.2, rx=6))
    frags.append(text(col4_x + 102, 72, "4. io_uring (SQ/CQ)", size=11, color="#047857", bold=True))
    frags.append(fitbox(col4_x + 10, 80, 185, 42, "Спільні кільця SQ/CQ (mmap)\nSubmission Queue в Ring 3", size=10, pad=3, fill="#ecfdf5", stroke="#34d399"))

    # Ядро стовпець 4
    frags.append(fitbox(col4_x + 10, 235, 185, 45, "1. Submission Queue (SQ)\nВибірка SQE ядром", size=10, pad=3, fill="#ffffff", stroke="#10b981"))
    frags.append(arrow(col4_x + 102, 280, col4_x + 102, 310, color="#10b981", sw=1.5))
    frags.append(fitbox(col4_x + 10, 310, 185, 45, "2. Асинхронний воркер / SQPOLL\nФіксовані буфери (Registered)", size=10, pad=3, fill="#ffffff", stroke="#10b981"))
    frags.append(arrow(col4_x + 102, 355, col4_x + 102, 385, color="#10b981", sw=1.5))
    frags.append(fitbox(col4_x + 10, 385, 185, 45, "3. Completion Queue (CQ)\nЗапис CQE без перемикання", size=10, pad=3, fill="#ffffff", stroke="#059669"))

    # Нижній підсумковий рядок порівняння
    frags.append(fitbox(35, 450, 215, 75, "4 копії (2 CPU + 2 DMA)\n4 перемикання контексту\nЗабруднення кешів L1/L3", size=10, pad=4, fill="#fee2e2", stroke="#ef4444", bold=True))
    frags.append(fitbox(275, 450, 215, 75, "2 копії (0 CPU + 2 DMA)\n2 перемикання контексту\nCPU не чіпає байти в RAM", size=10, pad=4, fill="#fef3c7", stroke="#f59e0b", bold=True))
    frags.append(fitbox(515, 450, 215, 75, "0 копій CPU між fd\nПереприв'язка struct page*\nПовна гнучкість каналів", size=10, pad=4, fill="#cffafe", stroke="#0891b2", bold=True))
    frags.append(fitbox(745, 450, 205, 75, "0 копій + 0 syscalls (SQPOLL)\nАмортизація затримки\nМаксимальна пропускність", size=10, pad=4, fill="#d1fae5", stroke="#059669", bold=True))

    render(os.path.join(OUT_DIR, "io-copy-chains.svg"), w, h, *frags)


def fig_timeline():
    """Схема часової шкали та накладних витрат: синхронні системні виклики проти пакетування в io_uring."""
    w, h = 960, 460
    frags = []

    # Верхній заголовок блоку A: Синхронні виклики
    frags.append(rect(30, 20, 900, 190, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=8))
    frags.append(text(480, 42, "СИНХРОННИЙ ПІДХІД: 1 СИСТЕМНИЙ ВИКЛИК НА КОЖНУ ПОРЦІЮ (READ/WRITE)", size=13, color="#991b1b", bold=True))

    # Схема послідовності A
    xs = [50, 200, 350, 500, 650, 800]
    labels_a = [
        ("Виклик read()", "Ring 3 → Ring 0", "#ef4444"),
        ("Перехід у ядро", "Збереження reg/CR3", "#dc2626"),
        ("Копія даних", "copy_to_user()", "#b91c1c"),
        ("Вихід у Ring 3", "Відновлення reg", "#dc2626"),
        ("Виклик write()", "Ring 3 → Ring 0", "#ef4444"),
        ("Копія в sk_buff", "copy_from_user()", "#b91c1c"),
    ]
    for i, (x, (t1, t2, col)) in enumerate(zip(xs, labels_a)):
        frags.append(fitbox(x, 65, 125, 60, "%s\n%s" % (t1, t2), size=10, pad=4, fill="#ffffff", stroke=col))
        if i < len(xs) - 1:
            frags.append(arrow(x + 125, 95, xs[i+1], 95, color="#b91c1c", sw=1.5))
    frags.append(fitbox(50, 140, 860, 55, "Ціна: N системних викликів + 2·N перемикань контексту + промахи кешу процесора при копіюванні.\nПроцесор витрачає до 60% тактів на службові переходи між кільцями захисту (Ring 3 ↔ Ring 0).", size=11, pad=5, fill="#fee2e2", stroke="#dc2626"))

    # Нижній заголовок блоку B: Асинхронний io_uring
    frags.append(rect(30, 230, 900, 210, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(480, 252, "АСИНХРОННИЙ IO_URING: СПІЛЬНІ КІЛЬЦЯ ТА ПАКЕТУВАННЯ (ZERO-OVERHEAD)", size=13, color="#166534", bold=True))

    # Схема послідовності B
    frags.append(fitbox(50, 275, 230, 65, "1. Запис у чергу SQ (Ring 3)\nПрограма формує 64 SQE\nв спільній пам'яті (RAM)", size=10, pad=5, fill="#ffffff", stroke="#16a34a"))
    frags.append(arrow(280, 307, 340, 307, color="#16a34a", sw=1.8))
    frags.append(fitbox(340, 275, 260, 65, "2. Одноразовий io_uring_enter\n(Або 0 викликів у режимі SQPOLL)\nЯдро бере всю пачку SQE одразу", size=10, pad=5, fill="#ffffff", stroke="#16a34a"))
    frags.append(arrow(600, 307, 660, 307, color="#16a34a", sw=1.8))
    frags.append(fitbox(660, 275, 250, 65, "3. Збір подій з кільця CQ\nПрограма читає готові CQE\nбез жодного системного виклику", size=10, pad=5, fill="#ffffff", stroke="#16a34a"))

    frags.append(fitbox(50, 360, 860, 65, "Виграш: Амортизація накладних витрат. 1 системний виклик на сотні операцій (або нуль при SQPOLL).\nВідсутність копіювання буферів при IORING_REGISTER_BUFFERS. Процесор повністю зайнятий корисною роботою.", size=11, pad=5, fill="#dcfce7", stroke="#15803d", bold=True))

    render(os.path.join(OUT_DIR, "io-syscall-vs-uring-timeline.svg"), w, h, *frags)


def fig_memory_saturation():
    """Схема насичення шини пам'яті (Memory Bus Saturation) залежно від моделі копіювання."""
    w, h = 960, 440
    frags = []

    # Загальний контейнер
    frags.append(rect(30, 20, 900, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(480, 45, "НАСИЧЕННЯ ПРОПУСКНОЇ ЗДАТНОСТІ ШИНИ ПАМ'ЯТІ (DRAM BUS BANDWIDTH)", size=14, color="#1e293b", bold=True))

    bars = [
        ("Класичний read/write (4 проходи по RAM)", 12.5, 50, "#ef4444", "12.5 ГБ/с корисного I/O (75% смуги згорає на копіювання CPU ↔ RAM)"),
        ("sendfile / splice (2 проходи DMA)", 25.0, 50, "#f59e0b", "25.0 ГБ/с корисного I/O (50% смуги шини пам'яті звільнено)"),
        ("io_uring з Registered Buffers (0 копій)", 47.5, 50, "#10b981", "47.5 ГБ/с корисного I/O (95% теоретичної межі контролера пам'яті)"),
    ]

    base_y = 80
    for i, (title, eff, total, color, note) in enumerate(bars):
        y = base_y + i * 105
        frags.append(text(50, y + 15, title, size=12, color="#0f172a", anchor="start", bold=True))
        
        # Задня шкала 100%
        frags.append(rect(50, y + 25, 840, 32, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=4))
        
        # Заповнена шкала
        fill_w = int(840 * (eff / total))
        frags.append(rect(50, y + 25, fill_w, 32, fill=color, stroke=color, sw=1, rx=4))
        
        frags.append(text(60 + fill_w / 2, y + 45, "%.1f ГБ/с" % eff, size=11, color="#ffffff", bold=True))
        frags.append(text(50, y + 72, note, size=10, color="#475569", anchor="start", italic=True))

    render(os.path.join(OUT_DIR, "io-memory-bus-saturation.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_copy_chains()
    fig_timeline()
    fig_memory_saturation()
    print("OK: generated figures for io-cost-model")
