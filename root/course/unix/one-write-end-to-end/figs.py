# -*- coding: utf-8 -*-
"""Генератор схем для теми 'Один запис наскрізь: від write() до сектора'."""

import sys, os

# 4 рівні вгору до кореня репо, де лежить scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_full_write_pipeline():
    """Схема наскрізного шляху запису крізь сім рівнів ОС та обладнання."""
    w, h = 1000, 720
    frags = []

    # Загальна рамка
    frags.append(rect(20, 15, 960, 690, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(500, 42, "ПОВНИЙ НАСКРІЗНИЙ ШЛЯХ ЗАПИСУ: ВІД write() ДО NAND FLASH", size=15, color="#0f172a", bold=True))

    # Рівні
    # Рівень 1: Простір користувача
    frags.append(fitbox(45, 65, 910, 65,
                        "1. ПРОСТІР КОРИСТУВАЧА (USER SPACE)\n"
                        "Застосунок C/C++ ──> stdio буфер FILE (_IO_FILE: 4/8 КіБ) ──> POSIX write(fd, buf, count)\n"
                        "Регістри x86_64: RAX=1 (SYS_write), RDI=fd, RSI=buf, RDX=count ──> Інструкція SYSCALL (перехід Ring 3 ──> Ring 0)",
                        size=11, pad=6, fill="#eff6ff", stroke="#3b82f6", bold=True))
    frags.append(arrow(500, 130, 500, 150, color="#3b82f6", sw=1.8))

    # Рівень 2: VFS
    frags.append(fitbox(45, 150, 910, 65,
                        "2. ВІРТУАЛЬНА ФАЙЛОВА СИСТЕМА (VFS)\n"
                        "do_syscall_64() ──> ksys_write() ──> vfs_write()\n"
                        "Пошук struct file у current->files->fdt[fd] ──> Перевірка FMODE_WRITE, RLIMIT_FSIZE ──> f_op->write_iter()",
                        size=11, pad=6, fill="#f5f3ff", stroke="#8b5cf6", bold=True))
    frags.append(arrow(500, 215, 500, 235, color="#8b5cf6", sw=1.8))

    # Рівень 3: Page Cache & Folios
    frags.append(fitbox(45, 235, 910, 75,
                        "3. СТОРІНКОВИЙ КЕШ (PAGE CACHE) ТА ОПЕРАТИВНА ПАМ'ЯТЬ (RAM)\n"
                        "address_space (i_mapping) ──> Пошук/виділення struct folio у XArray ──> copy_from_user() з простору користувача\n"
                        "folio_mark_dirty() (прапорець PG_dirty) ──> balance_dirty_pages_ratelimited()\n"
                        "★ СИСТЕМНИЙ ВИКЛИК ПОВЕРТАЄ КЕРУВАННЯ (затримка < 1 мкс). ДАНІ ВЖЕ В RAM, АЛЕ ЩЕ НЕ НА ДИСКУ!",
                        size=11, pad=6, fill="#ecfdf5", stroke="#10b981", bold=True))
    frags.append(arrow(500, 310, 500, 330, color="#10b981", sw=1.8))

    # Рівень 4: Журналювання та транзакції ФС
    frags.append(fitbox(45, 330, 910, 65,
                        "4. ФАЙЛОВА СИСТЕМА ТА ЖУРНАЛ (EXT4 / XFS / JBD2)\n"
                        "Відкладене виділення блоків (delalloc) ──> Виділення екстентів під час скидання ──> JBD2 журнал транзакцій\n"
                        "Режим data=ordered: дані виштовхуються ДО фіксації коміт-блоку журналу (Commit Record)",
                        size=11, pad=6, fill="#fffbeb", stroke="#f59e0b", bold=True))
    frags.append(arrow(500, 395, 500, 415, color="#f59e0b", sw=1.8))

    # Рівень 5: Блоковий рівень (Block Layer & blk-mq)
    frags.append(fitbox(45, 415, 910, 80,
                        "5. БЛОКОВИЙ РІВЕНЬ (BLOCK LAYER & BLK-MQ)\n"
                        "address_space_operations->writepages() ──> Створення struct bio (вектор bio_vec з адресами сторінок)\n"
                        "submit_bio() ──> Software Staging Queues (blk_mq_ctx) ──> Планувальник I/O (none / mq-deadline / BFQ)\n"
                        "Злиття секторів (merging) у struct request ──> Hardware Dispatch Queues (blk_mq_hw_ctx)",
                        size=11, pad=6, fill="#fdf2f8", stroke="#ec4899", bold=True))
    frags.append(arrow(500, 495, 500, 515, color="#ec4899", sw=1.8))

    # Рівень 6: Драйвер пристрою та DMA
    frags.append(fitbox(45, 515, 910, 75,
                        "6. ДРАЙВЕР ПРИСТРОЮ ТА ПЕРЕДАЧА ДАНИХ (NVME / AHCI / PCIE DMA)\n"
                        "nvme_queue_rq() ──> Формування 64-байтового SQE (Submission Queue Entry: SLBA, NLB, PRP/SGL списки DMA)\n"
                        "Запис у Doorbell-регістр контролера через MMIO ──> Контролер вичитує сторінки з RAM через Bus Master DMA\n"
                        "Завершення: Контролер пише CQE в RAM + надсилає переривання MSI-X ──> end_page_writeback()",
                        size=11, pad=6, fill="#eff6ff", stroke="#2563eb", bold=True))
    frags.append(arrow(500, 590, 500, 610, color="#2563eb", sw=1.8))

    # Рівень 7: Контролер накопичувача та фізичний носій
    frags.append(fitbox(45, 610, 910, 75,
                        "7. КОНТРОЛЕР НАКОПИЧУВАЧА, FTL ТА NAND FLASH / МАГНІТНИЙ ДИСК\n"
                        "Вхід у внутрішній DRAM/SLC кеш накопичувача (ACK хосту) ──> Flash Translation Layer (трансляція LBA ──> PBA)\n"
                        "fsync() / REQ_OP_FLUSH / REQ_FUA ──> Команда NVMe Flush (0x00) / ATA FLUSH CACHE EXT\n"
                        "Фізичний запис: програмування плаваючих затворів / зарядових пасток у кристалах TLC/QLC NAND Flash",
                        size=11, pad=6, fill="#f0fdf4", stroke="#16a34a", bold=True))

    render(os.path.join(OUT_DIR, "full-write-path-pipeline.svg"), w, h, *frags)


def fig_bio_to_request_merging():
    """Схема перетворення сторінок у bio, черги blk-mq та злиття у request."""
    w, h = 980, 520
    frags = []

    frags.append(rect(20, 15, 940, 490, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(490, 42, "БЛОКОВИЙ РІВЕНЬ: ВІД СТОРІНОК RAM ДО АПАРАТНОГО ЗАПИТУ DMA", size=14, color="#0f172a", bold=True))

    # Ліва частина: Брудні сторінки та створення bio
    frags.append(rect(40, 65, 275, 420, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(177, 90, "1. СТОРІНКИ ТА STRUCT BIO", size=12, color="#1e293b", bold=True))

    frags.append(fitbox(55, 110, 245, 75, "Брудні сторінки (Page Cache)\nFolio 0: 4 КіБ (LBA 1000..1007)\nFolio 1: 4 КіБ (LBA 1008..1015)\nFolio 2: 4 КіБ (LBA 1016..1023)", size=10.5, pad=5, fill="#ecfdf5", stroke="#10b981"))
    frags.append(arrow(177, 185, 177, 215, color="#10b981", sw=1.6))

    frags.append(fitbox(55, 215, 245, 110, "struct bio (Вектор вводу-виводу)\n• bi_bdev = /dev/nvme0n1p1\n• bi_iter.bi_sector = 1000\n• bi_vcnt = 3 (вектори)\n• bio_vec[0]: page0, 4K, off=0\n• bio_vec[1]: page1, 4K, off=0\n• bio_vec[2]: page2, 4K, off=0", size=10, pad=5, fill="#eff6ff", stroke="#3b82f6"))
    frags.append(arrow(177, 325, 177, 355, color="#3b82f6", sw=1.6))

    frags.append(fitbox(55, 355, 245, 110, "Вхід у blk-mq\nsubmit_bio(bio)\nПотоковий plug-список\n(task_struct->plug)\nАкумуляція суміжних bio", size=10.5, pad=5, fill="#f5f3ff", stroke="#8b5cf6"))

    # Центральна частина: blk-mq черги та планувальник
    frags.append(rect(345, 65, 290, 420, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(490, 90, "2. BLK-MQ ТА ПЛАНУВАЛЬНИК", size=12, color="#1e293b", bold=True))

    frags.append(fitbox(360, 110, 260, 80, "Програмні черги (Staging)\nstruct blk_mq_ctx (per-CPU)\n• CPU 0 Queue | CPU 1 Queue\n• CPU 2 Queue | CPU 3 Queue\n(Нуль блокувань між ядрами)", size=10.5, pad=5, fill="#fdf2f8", stroke="#ec4899"))
    frags.append(arrow(490, 190, 490, 220, color="#ec4899", sw=1.6))

    frags.append(fitbox(360, 220, 260, 115, "Планувальник вводу-виводу\n(I/O Scheduler / Elevator)\n• none (NVMe bypass)\n• mq-deadline (дедлайни r/w)\n• BFQ (бюджетний fair-share)\nОперація: Back / Front Merge\n(зшивання суміжних bio в один)", size=10, pad=5, fill="#fffbeb", stroke="#f59e0b"))
    frags.append(arrow(490, 335, 490, 365, color="#f59e0b", sw=1.6))

    frags.append(fitbox(360, 365, 260, 100, "Апаратні черги ядра\nstruct blk_mq_hw_ctx (hctx)\nЧерга диспетчеризації\n(Dispatch Queue)\nГотові запити struct request", size=10.5, pad=5, fill="#f8fafc", stroke="#64748b"))

    # Права частина: struct request та апаратна відправка
    frags.append(rect(665, 65, 275, 420, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(802, 90, "3. STRUCT REQUEST ТА DMA", size=12, color="#1e293b", bold=True))

    frags.append(fitbox(680, 110, 245, 110, "struct request (Агрегований)\n• __sector = 1000\n• __data_len = 128 КіБ (32 bio)\n• nr_phys_segments = 32\n• bio = head_bio ──> next_bio\nПовністю готовий для DMA", size=10.5, pad=5, fill="#f0fdf4", stroke="#22c55e", bold=True))
    frags.append(arrow(802, 220, 802, 250, color="#22c55e", sw=1.6))

    frags.append(fitbox(680, 250, 245, 100, "Драйвер NVMe / AHCI\nСтворення SQE команди:\nSLBA = 1000, Length = 128 KB\nPRP / SGL таблиця фізичних\nадрес оперативної пам'яті", size=10.5, pad=5, fill="#eff6ff", stroke="#2563eb"))
    frags.append(arrow(802, 350, 802, 380, color="#2563eb", sw=1.6))

    frags.append(fitbox(680, 380, 245, 85, "Шина PCIe / Контролер\nMMIO Doorbell Ring ──>\nPCIe Bus Master DMA ──>\nКонтролер забирає 128 КіБ", size=10.5, pad=5, fill="#f1f5f9", stroke="#0f172a", bold=True))

    # Стрілки між стовпчиками
    frags.append(arrow(315, 270, 345, 270, color="#64748b", sw=2.0))
    frags.append(arrow(635, 270, 665, 270, color="#64748b", sw=2.0))

    render(os.path.join(OUT_DIR, "block-layer-bio-to-request.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_full_write_pipeline()
    fig_bio_to_request_merging()
    print("OK: generated figures for one-write-end-to-end")
