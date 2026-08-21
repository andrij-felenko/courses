# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
WARM = "#fff6e5"
RED = "#fdecea"
GREY = "#eceff1"


# ── 1. Архітектура опитування SMART у Linux ────────────────────────────────
def fig_smart_architecture():
    W, H = 1260, 780
    p = []

    p.append(text(630, 36, "Шлях команд опитування SMART від утиліт до накопичувачів", size=17, bold=True))

    # Верхній рівень: Простір користувача
    p.append(fitbox(80, 70, 1100, 70,
                    "Простір користувача: smartctl / smartd / Prometheus node_exporter\n(Формування запиту на діагностику або читання журналів здоров'я)",
                    size=14, bold=True, fill=BLUE))

    # Розгалуження на два інтерфейси
    p.append(arrow(340, 142, 340, 186))
    p.append(arrow(920, 142, 920, 186))

    # Ліва колонка: SATA / SAS (SCSI підсистема)
    p.append(fitbox(80, 190, 520, 76,
                    "SATA / SAS: Блоковий вузол /dev/sda або /dev/sg0\nioctl(fd, SG_IO, &sg_io_hdr)",
                    size=14, bold=True, fill=WARM))

    p.append(arrow(340, 268, 340, 312))
    p.append(fitbox(80, 314, 520, 84,
                    "Драйвер libata / SCSI: Трансляція SAT (INCITS 431)\nОбгортання ATA PASS-THROUGH (16) 0x85\nКоманда 0xB0 (SMART) + Subcommand 0xD0 (Read Data)",
                    size=13, fill=GREY))

    p.append(arrow(340, 400, 340, 444))
    p.append(fitbox(80, 446, 520, 76,
                    "Контролер SATA (AHCI / SAS HBA)\nПередача пакета FIS / Taskfile до диска",
                    size=14, fill=GREY))

    # Права колонка: NVMe (Прямий Admin Queue)
    p.append(fitbox(660, 190, 520, 76,
                    "NVMe: Символьний або блоковий вузол /dev/nvme0\nioctl(fd, NVME_IOCTL_ADMIN_CMD, &admin_cmd)",
                    size=14, bold=True, fill=GREEN))

    p.append(arrow(920, 268, 920, 312))
    p.append(fitbox(660, 314, 520, 84,
                    "Драйвер ядра nvme: Admin Submission Queue (ASQ)\nOpcode 0x02 (Get Log Page)\nLog ID 0x02 (SMART / Health Information, 512 байтів)",
                    size=13, fill=GREY))

    p.append(arrow(920, 400, 920, 444))
    p.append(fitbox(660, 446, 520, 76,
                    "Шина PCIe: Прямий DMA-запис контролером у буфер процесу\nГенерація Admin Completion Queue (ACQ)",
                    size=14, fill=GREY))

    # Спільний нижній рівень: Контролер накопичувача
    p.append(arrow(340, 524, 460, 580))
    p.append(arrow(920, 524, 800, 580))

    p.append(fitbox(80, 582, 1100, 140,
                    "Вбудована мікропрограма накопичувача (Firmware)\n"
                    "• Опитування термодавачів, лічильників циклів P/E та помилок ECC/LDPC\n"
                    "• Керування пулом резервних секторів (Reallocated Sectors) та зносом комірок (Wear Leveling)\n"
                    "• Ведення 512-байтових сторінок телеметрії (ATA Attributes Table / NVMe Health Log)\n"
                    "• Виконання фонових тестів самодіагностики (Short / Extended / Offline Data Collection)",
                    size=13, fill=WARM))

    return render(os.path.join(IMG, 'smart-architecture.svg'), W, H, *p)


# ── 2. Анатомія атрибута ATA SMART та шкали оцінки ────────────────────────
def fig_attribute_anatomy():
    W, H = 1260, 720
    p = []

    p.append(text(630, 36, "Структура 12-байтового запису атрибута SMART та шкала нормалізації", size=17, bold=True))

    # 12-байтовий блок атрибута
    p.append(fitbox(80, 70, 1100, 60,
                    "12 байтів запису атрибута в таблиці ATA: [ID: 1B] [Flags: 2B] [Value: 1B] [Worst: 1B] [RAW Value: 6B] [Reserved: 1B]",
                    size=14, bold=True, fill=BLUE))

    # Чотири ключові величини
    cols = [
        ("RAW Value (6 байтів)",
         "Фізичний лічильник мікропрограми:\nкількість перепризначених секторів,\nгодини роботи, температура або помилки.\nФормат визначає виробник.",
         GREY),
        ("Normalized Value (1 байт)",
         "Нормалізоване здоров'я (100 або 200):\nпадає від 100/200 до 0 у міру деградації.\n100 = ідеально, 1 = передсмертний стан.\nОбчислюється прошивкою.",
         GREEN),
        ("Worst Value (1 байт)",
         "Найгірше зафіксоване значення:\nнайнижчий бал Normalization за всю історію\nроботи диска. Допомагає виявити\nминулі пікові перегріви чи збої.",
         WARM),
        ("Threshold (1 байт)",
         "Критичний поріг відмови:\nзадається виробником на заводі.\nЯкщо Value <= Threshold, диск формує\nвирок «SMART Trip» (гарантійна заміна).",
         RED),
    ]

    x = 80
    for title, desc, col in cols:
        p.append(fitbox(x, 150, 260, 200, title + "\n\n" + desc, size=13, fill=col))
        x += 280

    # Візуалізація шкали порівняння
    p.append(rect(80, 390, 1100, 270, fill="#ffffff", stroke=LINE))
    p.append(text(630, 420, "Співвідношення шкали нормалізації та порогу спрацьовування", size=16, bold=True))

    # Шкала: 200/100 -> Threshold -> 0
    p.append(rect(140, 460, 980, 50, fill=GREEN, stroke=FIELD))
    p.append(rect(140, 460, 300, 50, fill=RED, stroke=POS))

    p.append(text(140, 535, "0 (Повна відмова)", size=13, anchor="start", bold=True, color=POS))
    p.append(text(440, 535, "Threshold (наприклад, 36)", size=13, anchor="middle", bold=True, color=POS))
    p.append(text(800, 535, "Normalized Value = 100 (Поточний робочий стан)", size=13, anchor="middle", bold=True, color=FIELD))
    p.append(text(1120, 535, "200/100 (Завод)", size=13, anchor="end", bold=True, color=FIELD))

    # Стрілка Threshold Trip
    p.append(line(440, 445, 440, 515, color=POS, sw=2.5, dash="4,4"))
    p.append(fitbox(140, 570, 420, 70,
                    "КРИТИЧНА ЗОНА (Pre-fail trip):\nValue <= Threshold → Відмова неминуча\nТермінова заміна накопичувача",
                    size=13, bold=True, fill=RED))

    p.append(fitbox(600, 570, 520, 70,
                    "БЕЗПЕЧНА ЗОНА:\nValue > Threshold → Накопичувач у межах допуску\n(навіть якщо RAW лічильник містить одиничні збої)",
                    size=13, bold=True, fill=GREEN))

    return render(os.path.join(IMG, 'attribute-anatomy.svg'), W, H, *p)


# ── 3. Життєвий цикл пошкодженого сектора (C5 -> 05 / C6) ─────────────────
def fig_reallocation_flow():
    W, H = 1260, 740
    p = []

    p.append(text(630, 36, "Життєвий цикл дефектного сектора: перехід між Current Pending та Reallocated", size=17, bold=True))

    # 1. Помилка читання
    p.append(fitbox(430, 70, 400, 70,
                    "1. Збій читання сектора (Read Error):\nECC / LDPC не може відновити блок даних.\nДиск повертає системі помилку I/O.",
                    size=13, bold=True, fill=RED))

    p.append(arrow(630, 142, 630, 186))

    # 2. Перехід у Pending
    p.append(fitbox(380, 190, 500, 80,
                    "2. Сектор позначається як нестабільний:\nІнкремент атрибута C5 (Current Pending Sector Count).\nСектор чекає перезапису для перевірки поверхні.",
                    size=13, bold=True, fill=WARM))

    p.append(arrow(630, 272, 630, 316))

    # 3. Спроба запису
    p.append(fitbox(380, 320, 500, 60,
                    "3. Хост або утиліта виконує запис у цей LBA:\nКонтролер перевіряє фізичну магнітну ділянку.",
                    size=13, bold=True, fill=BLUE))

    # Розгалуження: Успіх чи Фізичне пошкодження
    p.append(arrow(460, 382, 300, 436))
    p.append(arrow(800, 382, 960, 436))

    # Ліва гілка: Сектор відновлено
    p.append(fitbox(80, 440, 480, 100,
                    "Варіант А: Запис успішний (soft error / cosmic ray)\n"
                    "• Фізична поверхня виявилася неушкодженою\n"
                    "• Декремент C5 (Current Pending Sector -1)\n"
                    "• Сектор повертається до звичайного обігу",
                    size=13, fill=GREEN))

    # Права гілка: Фізичне пошкодження (Reallocation)
    p.append(fitbox(700, 440, 480, 100,
                    "Варіант Б: Фізичний дефект пластини (hard error)\n"
                    "• LBA вилучається з активної адресації\n"
                    "• Адреса відображається на резервну доріжку (Spare Sector)\n"
                    "• Декремент C5 (-1) та інкремент 05 (Reallocated Sector +1)",
                    size=13, bold=True, fill=RED))

    # Фонове сканування (C6)
    p.append(arrow(320, 542, 320, 596))
    p.append(arrow(940, 542, 940, 596))

    p.append(fitbox(80, 600, 1100, 90,
                    "Фонове сканування без участі хоста (Offline Data Collection):\n"
                    "Якщо нечитабельний сектор виявлено під час внутрішньої фонової перевірки диска,\n"
                    "він також збільшує лічильник C6 (Offline Uncorrectable Sector Count).",
                    size=13, fill=GREY))

    return render(os.path.join(IMG, 'reallocation-flow.svg'), W, H, *p)


# ── 4. Структура сторінки NVMe SMART / Health Log 0x02 ────────────────────
def fig_nvme_health_log():
    W, H = 1260, 720
    p = []

    p.append(text(630, 36, "Карта полів журналу здоров'я NVMe (Log Identifier 0x02, 512 байтів)", size=17, bold=True))

    # Байт 0: Critical Warning
    p.append(fitbox(80, 70, 1100, 150,
                    "Байт 0: Маска критичних попереджень (Critical Warning Bitmask)\n"
                    "• Біт 0: Available Spare нижче критичного порогу (Available Spare Threshold)\n"
                    "• Біт 1: Температура перевищила поріг перегріву або переохолодження\n"
                    "• Біт 2: Надійність підсистеми NVM деградувала (множинні помилки носія/пам'яті)\n"
                    "• Біт 3: Носій переведено в режим «Тільки для читання» (Read Only Mode для захисту даних)\n"
                    "• Біт 4: Збій пристрою резервного живлення енергонезалежного кешу (Volatile Memory Backup Failed)",
                    size=13, bold=True, fill=RED))

    # Основні метрики здоров'я NVMe
    metrics = [
        ("Температурні поля\n(Байти 1-2, 200-215)",
         "Composite Temperature (у Кельвінах)\n+ Давачі Sensor 1..8.\nФіксація часу роботи в зоні\nпопередження та критичного нагріву.",
         WARM),
        ("Ресурс комірок\n(Байти 3, 4, 5)",
         "Available Spare (залишок резерву %)\nAvailable Spare Threshold (поріг %)\nPercentage Used (витрата ресурсу %,\nможе перевищувати 100%).",
         GREEN),
        ("Обсяги вводу-виводу\n(Байти 32-63)",
         "Data Units Read (128-біт)\nData Units Written (128-біт)\nОдиниця = 1000 секторів по 512B\n(~500 КБ даних).",
         BLUE),
        ("Помилки та надійність\n(Байти 112-175)",
         "Media & Data Integrity Errors (128-біт)\nUnsafe Shutdowns (аварійні вимкнення)\nPower On Hours (години під живленням)\nNumber of Error Log Entries.",
         GREY),
    ]

    x = 80
    for title, desc, col in metrics:
        p.append(fitbox(x, 240, 260, 210, title + "\n\n" + desc, size=13, fill=col))
        x += 280

    # Нижня частина: Відмінність NVMe від застарілих ATA атрибутів
    p.append(fitbox(80, 470, 1100, 200,
                    "Чому протокол NVMe SMART стандартизовано жорсткіше за ATA:\n\n"
                    "1. Фіксовані зміщення: Усі байти телеметрії (температура, ресурс, лічильники запису) мають суворі позиції в специфікації NVM Express.\n"
                    "2. Відсутність «магічних чисел»: Значення передаються як прямі фізичні величини (Кельвіни, відсотки, 128-бітні числа байтів),\n"
                    "   а не пропрієтарні нормалізовані бали конкретного вендора.\n"
                    "3. Асинхронні сповіщення (AEN): Контролер сам надсилає переривання хосту в разі зміни бітів Critical Warning,\n"
                    "   усуваючи потребу в неперервному агресивному опитуванні пристрою.",
                    size=13, fill=GREEN))

    return render(os.path.join(IMG, 'nvme-health-log.svg'), W, H, *p)


if __name__ == '__main__':
    fig_smart_architecture()
    fig_attribute_anatomy()
    fig_reallocation_flow()
    fig_nvme_health_log()
    print("ok")
