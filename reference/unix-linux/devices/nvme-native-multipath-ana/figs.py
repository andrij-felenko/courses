# -*- coding: utf-8 -*-
"""Генератор діаграм для теми NVMe Native Multipath та станів ANA."""

import os
import sys

# 4 рівні вгору до кореня репозиторію з reference/unix-linux/devices/nvme-native-multipath-ana
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)

# Палітра теми
C_OPTIMIZED = "#27ae60"     # зелений — Optimized (AO)
C_NON_OPT   = "#e67e22"     # помаранчевий — Non-Optimized (ANO)
C_INACCESSIBLE = "#c0392b"  # червоний — Inaccessible (AI) / Persistent Loss
C_CHANGE    = "#8e44ad"     # фіолетовий — Change State
C_CTRL      = "#2980b9"     # синій — контролери та стек
C_BG_BOX    = "#f8fafc"
C_ACCENT    = "#34495e"

def fig1_nvme_multipath_head_subsystem():
    """Фігура 1: Ієрархія структур ядра Linux для нативного мультипасингу NVMe."""
    w, h = 920, 520
    frags = []

    # Загальний контейнер підсистеми NVMe Subsystem
    frags.append(rect(20, 20, 880, 480, fill="#f4f7fb", stroke="#7f8c8d", sw=1.5, rx=8))
    frags.append(text(460, 45, "Підсистема ядра Linux: struct nvme_subsystem (NQN: nqn.2014-08.org.nvmexpress:...)", size=14, color=C_ACCENT, bold=True))

    # Простори користувача та master gendisk (nvme_ns_head)
    frags.append(rect(260, 65, 400, 70, fill="#eaf2f8", stroke=C_CTRL, sw=2, rx=6))
    frags.append(text(460, 88, "Користувацький простір: /dev/nvme0n1", size=15, color=C_CTRL, bold=True))
    frags.append(text(460, 115, "struct nvme_ns_head (master gendisk, iopolicy: numa | round-robin)", size=12, color=INK))

    # Стрілки маршрутизації від nvme_ns_head до контролерів
    frags.append(arrow(380, 135, 230, 180, color=LINE, sw=2))
    frags.append(arrow(540, 135, 690, 180, color=LINE, sw=2))
    frags.append(text(280, 155, "Шлях 1 (RCU)", size=11, color=MUTED, bold=True))
    frags.append(text(640, 155, "Шлях 2 (RCU)", size=11, color=MUTED, bold=True))

    # Контролер 1
    frags.append(rect(50, 180, 360, 300, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=6))
    frags.append(rect(65, 195, 330, 45, fill="#ebf5fb", stroke=C_CTRL, sw=1.5, rx=4))
    frags.append(text(230, 215, "struct nvme_ctrl (Контролер 0: /dev/nvme0)", size=13, color=C_CTRL, bold=True))
    frags.append(text(230, 232, "Транспорт: NVMe/TCP (192.168.10.1:4420), NUMA Node 0", size=11, color=MUTED))

    # Namespace 1 на Контролері 1
    frags.append(rect(65, 255, 330, 100, fill="#eafaf1", stroke=C_OPTIMIZED, sw=1.5, rx=4))
    frags.append(text(230, 278, "struct nvme_ns (Вузол шляху: /dev/nvme0c0n1)", size=12, color=C_OPTIMIZED, bold=True))
    frags.append(text(230, 298, "NSID: 1 | ANAGRPID: 1 | Стан ANA: Optimized (AO)", size=11, color=INK))
    frags.append(text(230, 318, "blk-mq hw-queues -> direct submission (zero alloc)", size=11, color=MUTED))
    frags.append(text(230, 338, "Прямий доступ PCIe Gen4 / нульова затримка пересилання", size=10, color=C_OPTIMIZED, bold=True))

    # Черга Admin та AER на Контролері 1
    frags.append(rect(65, 370, 330, 95, fill="#fdfefe", stroke="#bdc3c7", sw=1, rx=4))
    frags.append(text(230, 392, "Черга керування (Admin Queue)", size=12, color=INK, bold=True))
    frags.append(text(230, 412, "AER (Asynchronous Event Request): тип Notice (0x02)", size=11, color=MUTED))
    frags.append(text(230, 432, "ANA Log Page (LID 0x0c) -> kworker: nvme_mpath_ana_work", size=10, color=INK))
    frags.append(text(230, 452, "Оновлює ns->ana_state та активує резервні шляхи", size=10, color=MUTED))

    # Контролер 2
    frags.append(rect(510, 180, 360, 300, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=6))
    frags.append(rect(525, 195, 330, 45, fill="#ebf5fb", stroke=C_CTRL, sw=1.5, rx=4))
    frags.append(text(690, 215, "struct nvme_ctrl (Контролер 1: /dev/nvme1)", size=13, color=C_CTRL, bold=True))
    frags.append(text(690, 232, "Транспорт: NVMe/TCP (192.168.20.1:4420), NUMA Node 1", size=11, color=MUTED))

    # Namespace 1 на Контролері 2
    frags.append(rect(525, 255, 330, 100, fill="#fef9e7", stroke=C_NON_OPT, sw=1.5, rx=4))
    frags.append(text(690, 278, "struct nvme_ns (Вузол шляху: /dev/nvme1c1n1)", size=12, color=C_NON_OPT, bold=True))
    frags.append(text(690, 298, "NSID: 1 | ANAGRPID: 1 | Стан ANA: Non-Optimized (ANO)", size=11, color=INK))
    frags.append(text(690, 318, "Резервний шлях: активний, але вища затримка", size=11, color=MUTED))
    frags.append(text(690, 338, "Проксі-доступ через міжконтролерну шину NTB/PCIe", size=10, color=C_NON_OPT, bold=True))

    # Черга Admin та AER на Контролері 2
    frags.append(rect(525, 370, 330, 95, fill="#fdfefe", stroke="#bdc3c7", sw=1, rx=4))
    frags.append(text(690, 392, "Черга керування (Admin Queue)", size=12, color=INK, bold=True))
    frags.append(text(690, 412, "AER (Asynchronous Event Request): очікує подій цілі", size=11, color=MUTED))
    frags.append(text(690, 432, "Готовий до миттєвого перемикання при падінні Контролера 0", size=10, color=INK))
    frags.append(text(690, 452, "Спільний простір NSID 1 видимий через єдиний /dev/nvme0n1", size=10, color=MUTED))

    return render(os.path.join(OUT_DIR, "nvme-multipath-head-subsystem.svg"), w, h, *frags)

def fig2_nvme_ana_dual_controller_fabric():
    """Фігура 2: Двоконтролерна мережева фабрика NVMe-oF та групи ANA."""
    w, h = 940, 520
    frags = []

    # Хост
    frags.append(rect(20, 20, 900, 90, fill="#f4f7fb", stroke=C_CTRL, sw=1.5, rx=6))
    frags.append(text(470, 45, "Клієнтський сервер (NVMe Host)", size=15, color=C_CTRL, bold=True))
    frags.append(rect(50, 55, 380, 42, fill="#ffffff", stroke="#bdc3c7", sw=1, rx=4))
    frags.append(text(240, 80, "HBA Порт 0 (192.168.10.100)", size=12, color=INK, bold=True))
    frags.append(rect(510, 55, 380, 42, fill="#ffffff", stroke="#bdc3c7", sw=1, rx=4))
    frags.append(text(700, 80, "HBA Порт 1 (192.168.20.100)", size=12, color=INK, bold=True))

    # Лінії зв'язку
    frags.append(arrow(240, 97, 240, 160, color=C_OPTIMIZED, sw=2.5))
    frags.append(arrow(700, 97, 700, 160, color=C_NON_OPT, sw=2.5))
    frags.append(text(150, 130, "Шлях 1: 100 GbE RoCEv2", size=11, color=C_OPTIMIZED, bold=True))
    frags.append(text(795, 130, "Шлях 2: 100 GbE RoCEv2", size=11, color=C_NON_OPT, bold=True))

    # Дисковий масив / NVMe Target
    frags.append(rect(20, 160, 900, 340, fill="#fdfefe", stroke="#7f8c8d", sw=1.5, rx=8))
    frags.append(text(470, 185, "Двоконтролерний масив збереження (NVMe-oF Storage Target)", size=14, color=C_ACCENT, bold=True))

    # Вузол Контролера A
    frags.append(rect(40, 205, 400, 160, fill="#ebf5fb", stroke=C_CTRL, sw=1.5, rx=6))
    frags.append(text(240, 230, "Контролер A (Цільовий вузол 1)", size=13, color=C_CTRL, bold=True))
    frags.append(rect(55, 245, 370, 45, fill="#eafaf1", stroke=C_OPTIMIZED, sw=1.5, rx=4))
    frags.append(text(240, 265, "Група ANA 1: Optimized (AO)", size=12, color=C_OPTIMIZED, bold=True))
    frags.append(text(240, 282, "Прямий PCIe доступ до томів NSID 1, 2", size=10, color=INK))
    frags.append(rect(55, 300, 370, 45, fill="#fef9e7", stroke=C_NON_OPT, sw=1.5, rx=4))
    frags.append(text(240, 320, "Група ANA 2: Non-Optimized (ANO)", size=12, color=C_NON_OPT, bold=True))
    frags.append(text(240, 337, "Проксі-доступ до томів NSID 3, 4 через шину NTB", size=10, color=INK))

    # Вузол Контролера B
    frags.append(rect(500, 205, 400, 160, fill="#ebf5fb", stroke=C_CTRL, sw=1.5, rx=6))
    frags.append(text(700, 230, "Контролер B (Цільовий вузол 2)", size=13, color=C_CTRL, bold=True))
    frags.append(rect(515, 245, 370, 45, fill="#fef9e7", stroke=C_NON_OPT, sw=1.5, rx=4))
    frags.append(text(700, 265, "Група ANA 1: Non-Optimized (ANO)", size=12, color=C_NON_OPT, bold=True))
    frags.append(text(700, 282, "Проксі-доступ до томів NSID 1, 2 через шину NTB", size=10, color=INK))
    frags.append(rect(515, 300, 370, 45, fill="#eafaf1", stroke=C_OPTIMIZED, sw=1.5, rx=4))
    frags.append(text(700, 320, "Група ANA 2: Optimized (AO)", size=12, color=C_OPTIMIZED, bold=True))
    frags.append(text(700, 337, "Прямий PCIe доступ до томів NSID 3, 4", size=10, color=INK))

    # Міжконтролерна шина NTB
    frags.append(line(440, 285, 500, 285, color=POS, sw=3))
    frags.append(text(470, 275, "PCIe NTB", size=10, color=POS, bold=True))
    frags.append(text(470, 300, "Міст шини", size=9, color=MUTED))

    # Фізичний кошик накопичувачів NVMe SSD
    frags.append(rect(40, 385, 860, 100, fill="#ffffff", stroke="#95a5a6", sw=1.5, rx=6))
    frags.append(text(470, 405, "Фізичні накопичувачі NVMe SSD (Dual-Port U.2 / E1.S)", size=12, color=INK, bold=True))

    frags.append(rect(60, 420, 380, 50, fill="#f4f6f7", stroke=C_OPTIMIZED, sw=1.2, rx=4))
    frags.append(text(250, 442, "Томи 1 та 2 (NSID 1, 2 — ANAGRPID 1)", size=11, color=C_OPTIMIZED, bold=True))
    frags.append(text(250, 460, "Основний власник: Контролер A (Local NVMe Ports)", size=10, color=MUTED))

    frags.append(rect(500, 420, 380, 50, fill="#f4f6f7", stroke=C_OPTIMIZED, sw=1.2, rx=4))
    frags.append(text(690, 442, "Томи 3 та 4 (NSID 3, 4 — ANAGRPID 2)", size=11, color=C_OPTIMIZED, bold=True))
    frags.append(text(690, 460, "Основний власник: Контролер B (Local NVMe Ports)", size=10, color=MUTED))

    return render(os.path.join(OUT_DIR, "nvme-ana-dual-controller-fabric.svg"), w, h, *frags)

def fig3_nvme_ana_state_machine_and_aer():
    """Фігура 3: Автомат станів ANA, асинхронні події AER та оновлення журналу."""
    w, h = 940, 480
    frags = []

    # Заголовок
    frags.append(text(470, 30, "Автомат станів ANA (Asymmetric Namespace Access) та події AER", size=15, color=C_ACCENT, bold=True))

    # Стан 1: Optimized (AO)
    frags.append(rect(40, 70, 250, 110, fill="#eafaf1", stroke=C_OPTIMIZED, sw=2, rx=6))
    frags.append(text(165, 95, "Optimized (AO: 0x01)", size=13, color=C_OPTIMIZED, bold=True))
    frags.append(text(165, 118, "Прямий найкоротший шлях", size=11, color=INK))
    frags.append(text(165, 138, "Мінімальна затримка I/O", size=10, color=MUTED))
    frags.append(text(165, 158, "Основний робочий стан", size=10, color=C_OPTIMIZED, bold=True))

    # Стан 2: Non-Optimized (ANO)
    frags.append(rect(650, 70, 250, 110, fill="#fef9e7", stroke=C_NON_OPT, sw=2, rx=6))
    frags.append(text(775, 95, "Non-Optimized (ANO: 0x02)", size=13, color=C_NON_OPT, bold=True))
    frags.append(text(775, 118, "Непрямий шлях (проксі)", size=11, color=INK))
    frags.append(text(775, 138, "Робочий, але вища затримка", size=10, color=MUTED))
    frags.append(text(775, 158, "Резервний / Standby канал", size=10, color=C_NON_OPT, bold=True))

    # Стан 3: Change State (0x0f)
    frags.append(rect(345, 200, 250, 100, fill="#f4ecf7", stroke=C_CHANGE, sw=2, rx=6))
    frags.append(text(470, 225, "Change State (0x0F)", size=13, color=C_CHANGE, bold=True))
    frags.append(text(470, 248, "Перехідний стан аварії/міграції", size=11, color=INK))
    frags.append(text(470, 268, "Повертає NVME_SC_ANA_TRANSITION", size=10, color=C_CHANGE, bold=True))
    frags.append(text(470, 288, "Драйвер тимчасово призупиняє I/O", size=10, color=MUTED))

    # Стан 4: Inaccessible (AI)
    frags.append(rect(40, 330, 250, 110, fill="#fdedec", stroke=C_INACCESSIBLE, sw=2, rx=6))
    frags.append(text(165, 355, "Inaccessible (AI: 0x03)", size=13, color=C_INACCESSIBLE, bold=True))
    frags.append(text(165, 378, "Шлях апаратно недоступний", size=11, color=INK))
    frags.append(text(165, 398, "Помилка NVME_SC_ANA_INACCESSIBLE", size=10, color=C_INACCESSIBLE, bold=True))
    frags.append(text(165, 418, "Запити перенаправляються в обхід", size=10, color=MUTED))

    # Стан 5: Persistent Loss (PL)
    frags.append(rect(650, 330, 250, 110, fill="#eaecee", stroke="#7f8c8d", sw=2, rx=6))
    frags.append(text(775, 355, "Persistent Loss (PL: 0x04)", size=13, color="#2c3e50", bold=True))
    frags.append(text(775, 378, "Шлях втрачено безповоротно", size=11, color=INK))
    frags.append(text(775, 398, "NVME_SC_ANA_PERSISTENT_LOSS", size=10, color="#c0392b", bold=True))
    frags.append(text(775, 418, "Драйвер видаляє вузол шляху", size=10, color=MUTED))

    # Стрілки переходів
    frags.append(arrow(290, 115, 650, 115, color=LINE, sw=1.5))
    frags.append(arrow(650, 135, 290, 135, color=LINE, sw=1.5))
    frags.append(text(470, 105, "Міграція / Зміна пріоритету", size=10, color=MUTED))

    frags.append(arrow(200, 180, 350, 220, color=C_CHANGE, sw=1.5))
    frags.append(arrow(740, 180, 590, 220, color=C_CHANGE, sw=1.5))
    frags.append(arrow(470, 300, 240, 340, color=C_INACCESSIBLE, sw=1.5))
    frags.append(arrow(470, 300, 700, 340, color="#7f8c8d", sw=1.5))

    # Блок AER Notice
    frags.append(rect(320, 370, 300, 80, fill="#fcf3cf", stroke="#f39c12", sw=1.5, rx=6))
    frags.append(text(470, 392, "Оповіщення хоста: AER Notice (0x02)", size=11, color="#b7950b", bold=True))
    frags.append(text(470, 410, "Event Info: 0x03 (ANA Change Notice)", size=10, color=INK))
    frags.append(text(470, 428, "nvme_mpath_ana_work -> Get Log Page (0x0c)", size=10, color=MUTED))

    return render(os.path.join(OUT_DIR, "nvme-ana-state-machine-and-aer.svg"), w, h, *frags)

def fig4_nvme_multipath_vs_dm_stack():
    """Фігура 4: Порівняння стеку проходження I/O: dm-multipath проти Native NVMe Multipath."""
    w, h = 940, 490
    frags = []

    frags.append(text(470, 30, "Шлях проходження запиту (I/O Path): dm-multipath проти Native NVMe Multipath", size=15, color=C_ACCENT, bold=True))

    # Ліва колонка: Традиційний dm-multipath
    frags.append(rect(30, 55, 420, 415, fill="#fdfefe", stroke="#bdc3c7", sw=1.5, rx=6))
    frags.append(text(240, 80, "Традиційний dm-multipath (SCSI / Старий NVMe)", size=13, color=C_INACCESSIBLE, bold=True))

    frags.append(rect(50, 100, 380, 45, fill="#eaeded", stroke="#95a5a6", sw=1, rx=4))
    frags.append(text(240, 127, "Користувач: /dev/dm-0 (Device Mapper)", size=12, color=INK, bold=True))

    frags.append(arrow(240, 145, 240, 170, color=LINE, sw=1.5))

    frags.append(rect(50, 170, 380, 70, fill="#fdedec", stroke=C_INACCESSIBLE, sw=1.5, rx=4))
    frags.append(text(240, 192, "dm-multipath core (Окремий шар)", size=12, color=C_INACCESSIBLE, bold=True))
    frags.append(text(240, 210, "1. Блокування dm_table spinlock (контенція CPU)", size=10, color=INK))
    frags.append(text(240, 226, "2. Клонування bio / виділення struct request clone", size=10, color=POS, bold=True))

    frags.append(arrow(240, 240, 240, 265, color=LINE, sw=1.5))

    frags.append(rect(50, 265, 380, 60, fill="#eaeded", stroke="#95a5a6", sw=1, rx=4))
    frags.append(text(240, 287, "Нижні блокові пристрої: /dev/nvme0n1, /dev/nvme1n1", size=11, color=INK, bold=True))
    frags.append(text(240, 307, "Повторне планування в черзі драйвера", size=10, color=MUTED))

    frags.append(arrow(240, 325, 240, 350, color=LINE, sw=1.5))

    frags.append(rect(50, 350, 380, 105, fill="#fbfcfc", stroke="#bdc3c7", sw=1, rx=4))
    frags.append(text(240, 372, "Опитування: multipathd (демон простору користувача)", size=11, color=MUTED, bold=True))
    frags.append(text(240, 392, "• Періодичний check_path (інтервал 1-5 секунд)", size=10, color=INK))
    frags.append(text(240, 412, "• Затримка перемикання при аварії: 1-10 с", size=10, color=POS, bold=True))
    frags.append(text(240, 432, "• Додаткова затримка I/O: +8-20 мкс (оверхед)", size=10, color=POS, bold=True))

    # Права колонка: Native NVMe Multipathing
    frags.append(rect(490, 55, 420, 415, fill="#fdfefe", stroke="#bdc3c7", sw=1.5, rx=6))
    frags.append(text(700, 80, "Native NVMe Multipath (Ядро Linux)", size=13, color=C_OPTIMIZED, bold=True))

    frags.append(rect(510, 100, 380, 45, fill="#eaf2f8", stroke=C_CTRL, sw=1, rx=4))
    frags.append(text(700, 127, "Користувач: /dev/nvme0n1 (struct nvme_ns_head)", size=12, color=C_CTRL, bold=True))

    frags.append(arrow(700, 145, 700, 170, color=LINE, sw=1.5))

    frags.append(rect(510, 170, 380, 70, fill="#eafaf1", stroke=C_OPTIMIZED, sw=1.5, rx=4))
    frags.append(text(700, 192, "nvme_ns_head_submit_bio() (Швидкий шлях)", size=12, color=C_OPTIMIZED, bold=True))
    frags.append(text(700, 210, "1. Без блокувань: lockless RCU (nvme_find_path)", size=10, color=INK))
    frags.append(text(700, 226, "2. Без клонування: пряма підміна bio->bi_bdev", size=10, color=C_OPTIMIZED, bold=True))

    frags.append(arrow(700, 240, 700, 265, color=LINE, sw=1.5))

    frags.append(rect(510, 265, 380, 60, fill="#eaf2f8", stroke=C_CTRL, sw=1, rx=4))
    frags.append(text(700, 287, "Апаратна черга blk-mq вибраного nvme_ns", size=11, color=C_CTRL, bold=True))
    frags.append(text(700, 307, "Пряма передача в PCIe/RDMA/TCP Submission Queue", size=10, color=MUTED))

    frags.append(arrow(700, 325, 700, 350, color=LINE, sw=1.5))

    frags.append(rect(510, 350, 380, 105, fill="#fbfcfc", stroke="#bdc3c7", sw=1, rx=4))
    frags.append(text(700, 372, "Подієвий механізм: асинхронні події AER", size=11, color=C_OPTIMIZED, bold=True))
    frags.append(text(700, 392, "• Миттєве апаратне переривання від цілі (Notice)", size=10, color=INK))
    frags.append(text(700, 412, "• Затримка перемикання при аварії: < 500 мкс", size=10, color=C_OPTIMIZED, bold=True))
    frags.append(text(700, 432, "• Додаткова затримка I/O: < 0.2 мкс (нуль копіювань)", size=10, color=C_OPTIMIZED, bold=True))

    return render(os.path.join(OUT_DIR, "nvme-multipath-vs-dm-stack.svg"), w, h, *frags)

if __name__ == '__main__':
    fig1_nvme_multipath_head_subsystem()
    fig2_nvme_ana_dual_controller_fabric()
    fig3_nvme_ana_state_machine_and_aer()
    fig4_nvme_multipath_vs_dm_stack()
    print("All figures generated successfully.")
