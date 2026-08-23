# -*- coding: utf-8 -*-
"""Генератор схем для теми 'Коли запис справді записаний'."""

import sys, os

# 4 рівні вгору до кореня репо, де лежить scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_full_write_path():
    """Повний наскрізний шлях даних від виклику write() до енергонезалежного носія."""
    w, h = 960, 680
    frags = []

    # Фон
    frags.append(rect(10, 10, 940, 660, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))

    # Рівень 1: Простір користувача
    frags.append(rect(25, 20, 910, 70, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(480, 38, "1. ПРОСТІР КОРИСТУВАЧА: БУФЕР ПРОЦЕСУ ТА СИСТЕМНІ ВИКЛИКИ", size=12, color="#334155", bold=True))
    frags.append(textbox(170, 64, "write(fd, buf, len)", size=12, pad=5, fill="#ffffff", stroke="#0284c7", bold=True)[0])
    frags.append(textbox(480, 64, "fsync(fd) / fdatasync(fd)", size=12, pad=5, fill="#ffffff", stroke="#16a34a", bold=True)[0])
    frags.append(textbox(790, 64, "open(O_DIRECT | O_SYNC)", size=12, pad=5, fill="#ffffff", stroke="#d97706", bold=True)[0])

    # Стрілки переходу в ядро
    frags.append(arrow(170, 90, 170, 130, color="#0284c7", sw=1.8))
    frags.append(arrow(480, 90, 480, 130, color="#16a34a", sw=1.8))
    frags.append(arrow(790, 90, 790, 360, color="#d97706", sw=1.8)) # O_DIRECT оминає кеш сторінок
    frags.append(text(855, 220, "обхід кешу сторінок\n(DMA з буфера)", size=10, color="#b45309", bold=True))

    # Позначка повернення write() між 1 і 2 рівнями
    frags.append(fitbox(45, 96, 250, 24, "write() повертає успіх тут (~1 мкс)!", size=10, pad=3, fill="#dcfce7", stroke="#22c55e", color="#15803d", bold=True))

    # Рівень 2: VFS і кеш сторінок
    frags.append(rect(25, 130, 700, 85, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(375, 150, "2. СТОРІНКОВИЙ КЕШ ЯДРА (PAGE CACHE / VFS)", size=12, color="#1e40af", bold=True))
    frags.append(fitbox(45, 165, 200, 42, "struct address_space\nXArray: індекс сторінок", size=10, pad=4, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(260, 165, 210, 42, "Брудні сторінки (Dirty Folios)\nПозначка PG_dirty", size=10, pad=4, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True))
    frags.append(fitbox(485, 165, 225, 42, "Потоки витіснення (wb_workfn)\ndirty_ratio / dirty_background", size=10, pad=4, fill="#ffffff", stroke="#3b82f6"))

    # Стрілка від кешу сторінок до файлової системи
    frags.append(arrow(365, 215, 365, 245, color="#1e40af", sw=1.8))

    # Рівень 3: Файлова система й журнал транзакцій
    frags.append(rect(25, 245, 700, 85, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(375, 265, "3. ФАЙЛОВА СИСТЕМА ТА ЖУРНАЛ (EXT4 / JBD2 / XFS WAL)", size=12, color="#166534", bold=True))
    frags.append(fitbox(45, 278, 210, 42, "Журнал JBD2 (транзакція)\nRunning → Committing", size=10, pad=4, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(270, 278, 210, 42, "Порядок запису data=ordered\nДані блоків → Запис журналу", size=10, pad=4, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(495, 278, 215, 42, "Commit Record (Блок коміту)\nФіксація неподільної транзакції", size=10, pad=4, fill="#fef9c3", stroke="#eab308", color="#854d0e", bold=True))

    # Стрілки від ФС та O_DIRECT до блокового рівня
    frags.append(arrow(365, 330, 365, 360, color="#166534", sw=1.8))

    # Рівень 4: Блоковий шар
    frags.append(rect(25, 360, 910, 85, fill="#faf5ff", stroke="#d8b4fe", sw=1.5, rx=8))
    frags.append(text(480, 378, "4. БЛОКОВИЙ ШАР ЯДРА (BLOCK LAYER & BLK-MQ)", size=12, color="#6b21a8", bold=True))
    frags.append(fitbox(45, 393, 260, 42, "Опис запиту struct bio\nЗлиття векторів (bio_vec)", size=10, pad=4, fill="#ffffff", stroke="#a855f7"))
    frags.append(fitbox(320, 393, 300, 42, "Багаточерговий планувальник blk-mq\nnone / kyber / bfq (Hardware Queues)", size=10, pad=4, fill="#ffffff", stroke="#a855f7"))
    frags.append(fitbox(635, 393, 285, 42, "Прапорці бар'єрів запиту:\nREQ_OP_WRITE | REQ_PREFLUSH | REQ_FUA", size=10, pad=4, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True))

    # Стрілка до контролера диска
    frags.append(arrow(480, 445, 480, 475, color="#6b21a8", sw=1.8))

    # Рівень 5: Контролер диска й летючий кеш
    frags.append(rect(25, 475, 910, 85, fill="#fff7ed", stroke="#fdba74", sw=1.5, rx=8))
    frags.append(text(480, 493, "5. КОНТРОЛЕР НАКОПИЧУВАЧА ТА ЛЕТЮЧИЙ КЕШ ЗАПИСУ (VOLATILE CACHE)", size=12, color="#9a3412", bold=True))
    frags.append(fitbox(45, 506, 270, 46, "NVMe / SATA ASIC контролер\nЧерги Submission/Completion (SQ/CQ)", size=10, pad=4, fill="#ffffff", stroke="#f97316"))
    frags.append(fitbox(330, 506, 280, 46, "Летючий DRAM/SRAM буфер запису\nЗникає при знеструмленні без PLP!", size=10, pad=4, fill="#fef2f2", stroke="#dc2626", color="#991b1b", bold=True))
    frags.append(fitbox(625, 506, 295, 46, "Команди бар'єрів накопичувача:\nNVMe Flush / FUA | ATA FLUSH CACHE", size=10, pad=4, fill="#ffffff", stroke="#f97316"))

    # Стрілка до фізичного носія
    frags.append(arrow(480, 560, 480, 590, color="#9a3412", sw=1.8))

    # Позначка повернення fsync() між 5 і 6 рівнями
    frags.append(fitbox(580, 563, 340, 24, "fsync() / O_SYNC повертається лише тут!", size=10, pad=3, fill="#dcfce7", stroke="#16a34a", color="#166534", bold=True))

    # Рівень 6: Енергонезалежний носій
    frags.append(rect(25, 590, 910, 68, fill="#f8fafc", stroke="#475569", sw=1.5, rx=8))
    frags.append(text(480, 608, "6. ЕНЕРГОНЕЗАЛЕЖНИЙ НОСІЙ (NON-VOLATILE PERSISTENT STORAGE)", size=12, color="#0f172a", bold=True))
    frags.append(fitbox(45, 620, 410, 30, "Масиви комірок NAND Flash (SLC / TLC / QLC) або магнітні пластини HDD", size=10, pad=4, fill="#ffffff", stroke="#334155"))
    frags.append(fitbox(475, 620, 445, 30, "Захист живлення (Power Loss Protection / іоністори): злив DRAM у флеш", size=10, pad=4, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True))

    render(os.path.join(OUT_DIR, "full-write-path-layers.svg"), w, h, *frags)


def fig_wal_checkpoint():
    """Схема транзакційного журналу (WAL), групового коміту та фонового чекпоінту."""
    w, h = 960, 500
    frags = []

    frags.append(rect(10, 10, 940, 480, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(480, 36, "ТРАНЗАКЦІЙНА ДОВГОВІЧНІСТЬ: WAL, БАР'ЄР СИНХРОНІЗАЦІЇ ТА ЧЕКПОІНТ", size=13, color="#1e293b", bold=True))

    # Ліва колонка: Довговічний шлях фіксації транзакції (WAL Hot Path)
    frags.append(rect(30, 60, 425, 415, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(242, 85, "ШВИДКИЙ ТРАВНИЙ ШЛЯХ (WAL HOT PATH)", size=12, color="#166534", bold=True))

    frags.append(fitbox(50, 105, 385, 48, "1. Буфер транзакції в пам'яті процесу\nФормування запису: LSN + CRC32 + Зміни даних", size=11, pad=5, fill="#ffffff", stroke="#16a34a"))
    frags.append(arrow(242, 153, 242, 175, color="#166534", sw=1.8))

    frags.append(fitbox(50, 175, 385, 48, "2. Послідовне дописування у файл WAL\nwrite() або pwrite() у хвіст логу", size=11, pad=5, fill="#ffffff", stroke="#16a34a"))
    frags.append(arrow(242, 223, 242, 245, color="#166534", sw=1.8))

    frags.append(fitbox(50, 245, 385, 52, "3. Бар'єр довговічності: fdatasync(wal_fd)\nАбо груповий коміт (Group Commit 50 транзакцій)\nКоманда Flush / FUA до накопичувача", size=10, pad=5, fill="#fef2f2", stroke="#dc2626", color="#991b1b", bold=True))
    frags.append(arrow(242, 297, 242, 320, color="#166534", sw=1.8))

    frags.append(fitbox(50, 320, 385, 45, "4. Відповідь клієнту: Commit OK / 200 OK\nТранзакція гарантовано збережена на флеші", size=11, pad=5, fill="#dcfce7", stroke="#15803d", color="#166534", bold=True))
    frags.append(arrow(242, 365, 242, 390, color="#166534", sw=1.8))

    frags.append(fitbox(50, 390, 385, 70, "5. Стан після раптової втрати живлення:\n• Усі зафіксовані в WAL транзакції відтворюються (Replay)\n• Пошкоджений хвіст (Torn Write) відкидається за CRC32\n• Жодної втрати підтверджених даних!", size=10, pad=5, fill="#ffffff", stroke="#16a34a"))

    # Права колонка: Асинхронне винесення даних (Checkpointing)
    frags.append(rect(480, 60, 450, 415, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(705, 85, "АСИНХРОННИЙ ЧЕКПОІНТ (CHECKPOINTING)", size=12, color="#1e40af", bold=True))

    frags.append(fitbox(505, 105, 400, 52, "А. Зміна сторінок таблиць у пам'яті (Buffer Pool)\nB-Tree / LSM MemTable модифікуються в RAM\n(Сторінки стають брудними)", size=10, pad=5, fill="#ffffff", stroke="#3b82f6"))
    frags.append(arrow(705, 157, 705, 185, color="#1e40af", sw=1.8))

    frags.append(fitbox(505, 185, 400, 52, "Б. Фоновий потік витіснення (Checkpoint Thread)\nВпорядкований запис брудних сторінок\nу головні файли бази даних (.db / .sst)", size=10, pad=5, fill="#ffffff", stroke="#3b82f6"))
    frags.append(arrow(705, 237, 705, 265, color="#1e40af", sw=1.8))

    frags.append(fitbox(505, 265, 400, 48, "В. fsync(db_fd) для головного файлу\nФіксація сторінок на фізичному носії", size=10, pad=5, fill="#ffffff", stroke="#3b82f6"))
    frags.append(arrow(705, 313, 705, 340, color="#1e40af", sw=1.8))

    frags.append(fitbox(505, 340, 400, 52, "Г. Безпечне зрізання журналу (Truncate WAL)\nСтарі сегменти WAL видаляються,\nбо дані вже живуть у головному сховищі", size=10, pad=5, fill="#fef9c3", stroke="#eab308", color="#854d0e", bold=True))
    frags.append(arrow(705, 392, 705, 415, color="#1e40af", sw=1.8))

    frags.append(fitbox(505, 415, 400, 45, "Чому чекпоінт не гальмує запити:\nВиконується у фоні, оминаючи гарячий тракт коміту", size=10, pad=5, fill="#ffffff", stroke="#3b82f6"))

    render(os.path.join(OUT_DIR, "wal-checkpoint-consistency.svg"), w, h, *frags)


def fig_flush_vs_fua():
    """Порівняння поведінки та затримок команд Flush Cache та Force Unit Access (FUA)."""
    w, h = 960, 470
    frags = []

    frags.append(rect(10, 10, 940, 450, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(480, 36, "МЕХАНІКА АПАРАТНИХ БАР'ЄРІВ: FLUSH CACHE ПРОТИ FUA", size=13, color="#0f172a", bold=True))

    # Ліва половина: FLUSH CACHE
    frags.append(rect(25, 60, 440, 385, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=8))
    frags.append(text(245, 85, "КОМАНДА FLUSH CACHE (СКИДАННЯ ВСЬОГО КЕШУ)", size=11, color="#991b1b", bold=True))

    frags.append(fitbox(45, 105, 400, 50, "Черга накопичувача (DRAM Cache):\n[Запис 1] [Запис 2] [Запис 3] [Запис 4]", size=11, pad=5, fill="#ffffff", stroke="#ef4444"))
    frags.append(arrow(245, 155, 245, 180, color="#dc2626", sw=1.8))

    frags.append(fitbox(45, 180, 400, 50, "Надходить команда: SYNCHRONIZE CACHE / Flush (0x00)\nКонтролер блокує обробку нових команд!", size=10, pad=5, fill="#fee2e2", stroke="#dc2626", color="#991b1b", bold=True))
    frags.append(arrow(245, 230, 245, 255, color="#dc2626", sw=1.8))

    frags.append(fitbox(45, 255, 400, 55, "Примусовий запис УСІХ буферів у флеш:\nКонтролер записує 1, 2, 3, 4 у комірки NAND\nЗатримка сплеску: 2.0 – 15.0 мс", size=10, pad=5, fill="#ffffff", stroke="#ef4444"))
    frags.append(arrow(245, 310, 245, 335, color="#dc2626", sw=1.8))

    frags.append(fitbox(45, 335, 400, 95, "Особливості Flush:\n• Скидає весь кеш, навіть чужі сторонні записи\n• Створює високий хвіст затримок (P99/P99.9 latency spikes)\n• Повна гарантія стійкості для всього накопичувача\n• Стандартний шлях для системних викликів fsync()", size=10, pad=5, fill="#ffffff", stroke="#ef4444"))

    # Права половина: FUA (Force Unit Access)
    frags.append(rect(495, 60, 440, 385, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(715, 85, "FUA: ПРАПОРЕЦЬ FORCE UNIT ACCESS ДЛЯ БЛОКА", size=11, color="#166534", bold=True))

    frags.append(fitbox(515, 105, 400, 50, "Черга накопичувача (DRAM Cache):\n[Запис 1] [Запис 2] [Запис 3 (FUA = 1)]", size=11, pad=5, fill="#ffffff", stroke="#16a34a"))
    frags.append(arrow(715, 155, 715, 180, color="#16a34a", sw=1.8))

    frags.append(fitbox(515, 180, 400, 50, "Контролер обробляє біт FUA в дескрипторі NVMe:\nЗаписи 1 і 2 лишаються в DRAM без скидання!", size=10, pad=5, fill="#dcfce7", stroke="#16a34a", color="#166534", bold=True))
    frags.append(arrow(715, 230, 715, 255, color="#16a34a", sw=1.8))

    frags.append(fitbox(515, 255, 400, 55, "Запис на носій ЛИШЕ блока 3:\nЗапис 3 скеровується прямо у флеш (SLC/TLC)\nЗатримка операції: 0.15 – 0.40 мс", size=10, pad=5, fill="#ffffff", stroke="#16a34a"))
    frags.append(arrow(715, 310, 715, 335, color="#16a34a", sw=1.8))

    frags.append(fitbox(515, 335, 400, 95, "Особливості FUA:\n• Не скидає чужі фонові записи з DRAM-кешу\n• Не паралізує конвеєр команд контролера\n• Дає стабільні низькі затримки коміту транзакцій\n• Використовується в RWF_DSYNC та блокових чергах blk-mq", size=10, pad=5, fill="#ffffff", stroke="#16a34a"))

    render(os.path.join(OUT_DIR, "flush-vs-fua-timeline.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_full_write_path()
    fig_wal_checkpoint()
    fig_flush_vs_fua()
    print("All figures generated successfully.")
