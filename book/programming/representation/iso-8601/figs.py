# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_F = "#eef4ff"
RED_F = "#fdecea"
GREEN_F = "#eaf7ef"
GREY_F = "#f4f6f8"
YELLOW_F = "#fff9db"
PURPLE_F = "#f3e8ff"
PURPLE_LINE = "#7e22ce"


# ── 1. iso8601-anatomy: Анатомія мітки часу ─────────────────────────────────
def fig_iso8601_anatomy():
    W, H = 960, 430
    p = []

    # Загальний контейнер прикладу
    p.append(fitbox(30, 48, 900, 72, "2026-08-20 T 22:30:15.123 +03:00", size=22,
                    fill=BG, stroke=LINE, sw=2, bold=True))

    # Секції розбору під рядком
    # 1. Дата (рік, місяць, день)
    p.append(fitbox(30, 140, 270, 110,
                    "Календарна дата\n\n"
                    "2026: Рік (YYYY, 4 цифри)\n"
                    "08: Місяць (MM, 01..12)\n"
                    "20: День місяця (DD, 01..31)",
                    size=12, fill=BLUE_F, stroke=NEG, sw=1.8))

    # 2. Розділювач T
    p.append(fitbox(315, 140, 80, 110,
                    "Розділ\n\n"
                    "T\n"
                    "Time\n"
                    "Designator",
                    size=12, fill=YELLOW_F, stroke=LINE, sw=1.5, bold=True))

    # 3. Час доби
    p.append(fitbox(410, 140, 270, 110,
                    "Час доби (24-годинний)\n\n"
                    "22: Години (hh, 00..23)\n"
                    "30: Хвилини (mm, 00..59)\n"
                    "15.123: Секунди й дріб (ss.sss)",
                    size=12, fill=RED_F, stroke=POS, sw=1.8))

    # 4. Зміщення часового поясу
    p.append(fitbox(695, 140, 235, 110,
                    "Зміщення від UTC\n\n"
                    "+03:00: Зміщення (+hh:mm)\n"
                    "Z: Нульове зміщення (UTC)\n"
                    "-05:00: Західні пояси",
                    size=12, fill=GREEN_F, stroke=FIELD, sw=1.8))

    # Нижній блок: Порівняння базового та розширеного форматів
    p.append(fitbox(30, 270, 440, 126,
                    "Розширений формат (Extended Format)\n\n"
                    "2026-08-20T22:30:15.123+03:00\n"
                    "• Розділювачі «-» та «:» обов'язкові\n"
                    "• Максимальна читабельність у JSON/REST API\n"
                    "• Обов'язковий стандарт для RFC 3339",
                    size=12, fill=GREY_F, stroke=LINE, sw=1.4))

    p.append(fitbox(490, 270, 440, 126,
                    "Базовий формат (Basic Format)\n\n"
                    "20260820T223015Z\n"
                    "• Розділювачі дефіси й двокрапки пропущені\n"
                    "• Компактний для бінарних і вбудованих протоколів\n"
                    "• Безпечний для імен файлів у NTFS / FAT (без «:»)",
                    size=12, fill=GREY_F, stroke=LINE, sw=1.4))

    render(os.path.join(OUT, "iso8601-anatomy.svg"), W, H, *p,
           title="Анатомія мітки часу ISO 8601 та RFC 3339")


# ── 2. lexicographical-sorting: Лексикографічне сортування ──────────────────
def fig_lexicographical_sorting():
    W, H = 960, 460
    p = []

    # Верхній блок: Ієрархія ваги розрядів Big-Endian
    p.append(fitbox(30, 48, 900, 70,
                    "Спадання ваги розряду зліва направо (Big-Endian ієрархія):\n"
                    "Рік (YYYY)  →  Місяць (MM)  →  День (DD)  →  Година (hh)  →  Хвилина (mm)  →  Секунда (ss)",
                    size=13, fill=BLUE_F, stroke=NEG, sw=2, bold=True))

    # Ліва колонка: Хаос Little/Middle Endian
    p.append(fitbox(30, 136, 435, 170,
                    "Традиційні формати: Сортування ламається\n\n"
                    "Little-Endian (DD/MM/YYYY) — лексикографічний порядок:\n"
                    "✖ 01/12/2025  (Грудень 2025)\n"
                    "✖ 02/01/2020  (Січень 2020 — виявився пізнішим!)\n"
                    "✖ 15/05/2024  (Травень 2024)\n\n"
                    "Алфавітне сортування strcmp() не збігається з часом!",
                    size=12, fill=RED_F, stroke=POS, sw=1.8))

    # Права колонка: Big-Endian ISO 8601
    p.append(fitbox(495, 136, 435, 170,
                    "ISO 8601: Лексикографічний порядок == Часовий\n\n"
                    "Big-Endian (YYYY-MM-DD) — лексикографічний порядок:\n"
                    "✓ 2020-01-02  (Найраніша дата)\n"
                    "✓ 2024-05-15  (Проміжна дата)\n"
                    "✓ 2025-12-01  (Найпізніша дата)\n\n"
                    "Побайтове порівняння memcmp() точно впорядковує час.",
                    size=12, fill=GREEN_F, stroke=FIELD, sw=1.8))

    # Нижній блок: Пастка часових поясів
    p.append(fitbox(30, 324, 900, 108,
                    "Пастка зміщень часових поясів (Timezone Offset Pitfall)\n\n"
                    "«2026-08-20T22:00:00+03:00»  та  «2026-08-20T19:00:00Z» — це одна й та сама мить часу,\n"
                    "але лексикографічно «2026-08-20T19...» < «2026-08-20T22...» через різницю цифр годин.\n"
                    "Правило для індексації та сортування: перед збереженням нормалізувати всі мітки до UTC (Z)!",
                    size=12, fill=YELLOW_F, stroke=LINE, sw=1.6))

    render(os.path.join(OUT, "lexicographical-sorting.svg"), W, H, *p,
           title="Лексикографічне сортування: побайтовий та хронологічний порядок")


# ── 3. interval-and-duration: Інтервали та тривалості ────────────────────────
def fig_interval_and_duration():
    W, H = 960, 480
    p = []

    # 4 форми інтервалів
    forms = [
        (30, 48, 435, 96,
         "1. Початок / Кінець (Start / End)\n\n"
         "2026-08-20T09:00:00Z / 2026-08-20T18:00:00Z\n"
         "Повністю фіксований проміжок між двома митями.",
         BLUE_F, NEG),
        (495, 48, 435, 96,
         "2. Початок / Тривалість (Start / Duration)\n\n"
         "2026-08-20T09:00:00Z / PT9H\n"
         "Подія з відомим стартом і тривалістю 9 годин.",
         GREEN_F, FIELD),
        (30, 160, 435, 96,
         "3. Тривалість / Кінець (Duration / End)\n\n"
         "PT9H / 2026-08-20T18:00:00Z\n"
         "Дедлайн: 9-годинний таймер із завершенням о 18:00.",
         YELLOW_F, LINE),
        (495, 160, 435, 96,
         "4. Тільки тривалість (Duration Only)\n\n"
         "P1Y2M10DT2H30M  або  P3W (3 тижні)\n"
         "Абстрактний відрізок без прив'язки до дати.",
         PURPLE_F, PURPLE_LINE),
    ]

    for x, y, w, h, txt, fill, stroke in forms:
        p.append(fitbox(x, y, w, h, txt, size=12, fill=fill, stroke=stroke, sw=1.6))

    # Синтаксис тривалості PnYnMnDTnHnMnS
    p.append(fitbox(30, 274, 900, 84,
                    "Анатомія тривалості ISO 8601: P [n]Y [n]M [n]D T [n]H [n]M [n]S\n\n"
                    "• P (Period) — позначає початок тривалості\n"
                    "• M після P = Місяці (Months);  M після T = Хвилини (Minutes)\n"
                    "• W (Week) — окремий формат для тижнів (наприклад, P4W)",
                    size=12, fill=GREY_F, stroke=LINE, sw=1.5, bold=True))

    # Повторювані інтервали
    p.append(fitbox(30, 374, 900, 80,
                    "Повторювані інтервали (Recurring Intervals): R [n] / [інтервал]\n\n"
                    "• R5 / 2026-08-20T08:00:00Z / PT1H — 5 повторів щогодини від 08:00 UTC\n"
                    "• R / PT15M — нескінченний цикл опитування кожні 15 хвилин",
                    size=12, fill=BLUE_F, stroke=NEG, sw=1.6))

    render(os.path.join(OUT, "interval-and-duration.svg"), W, H, *p,
           title="Подання часових інтервалів та тривалостей в ISO 8601")


# ── 4. leap-second-timeline: Високосна секунда ──────────────────────────────
def fig_leap_second_timeline():
    W, H = 960, 460
    p = []

    # Верхній блок: Астрономічний час проти шкали UTC
    p.append(fitbox(30, 48, 900, 72,
                    "Шкала UTC та високосна секунда 23:59:60\n"
                    "Обертання Землі (UT1) відстає від атомних годинників (TAI) → IERS додає 61-шу секунду в добу:\n"
                    "23:59:58 UTC  →  23:59:59 UTC  →  23:59:60 UTC  →  00:00:00 UTC наступного дня",
                    size=12, fill=BLUE_F, stroke=NEG, sw=1.8, bold=True))

    # Ліва колонка: Проблема POSIX (Step-back)
    p.append(fitbox(30, 138, 435, 180,
                    "POSIX Time: Стрибок часу назад (Stepping)\n\n"
                    "POSIX рахує 86400 с/добу. Секунди 60 не існує!\n"
                    "1. 23:59:59 → timestamp = N (86399)\n"
                    "2. 23:59:60 → timestamp = N+1 (86400)\n"
                    "3. 00:00:00 → timestamp = N+1 (86400 повторно!)\n\n"
                    "✖ Час робить стрибок назад: немонотонність,\n"
                    "дублікати транзакцій, таймаути в дедлоках.",
                    size=12, fill=RED_F, stroke=POS, sw=1.8))

    # Права колонка: NTP Leap Smearing
    p.append(fitbox(495, 138, 435, 180,
                    "Leap Smearing: Плавне розмазування частоти\n\n"
                    "Google, AWS, Meta розмазують ±1 с протягом 24 годин:\n"
                    "• Частота серверного генератора змінюється на ±11.57 ppm\n"
                    "• Кожна секунда доби довша на ~11.6 мікросекунд\n"
                    "• Секунда 60 ніколи не генерується явно\n\n"
                    "✓ Час строго монотонний, системний годинник не стрибає,\n"
                    "розподілені бази даних (Raft/Spanner) стабільні.",
                    size=12, fill=GREEN_F, stroke=FIELD, sw=1.8))

    # Нижній блок: Стандарти та сумісність
    p.append(fitbox(30, 334, 900, 98,
                    "Підтримка в стандартах: ISO 8601 та RFC 3339\n\n"
                    "• ISO 8601 та RFC 3339 прямо дозволяють «23:59:60» у граматиці часу\n"
                    "• Багато стандартних парсерів (наприклад, C strptime або старі JS Date) ламаються на значенні 60\n"
                    "• Надійний парсер зобов'язаний валідувати секунду в діапазоні 0..60 замість 0..59",
                    size=12, fill=YELLOW_F, stroke=LINE, sw=1.6))

    render(os.path.join(OUT, "leap-second-timeline.svg"), W, H, *p,
           title="Обробка високосної секунди: стрибок часу проти Leap Smearing")


# ── 5. fast-parse-pipeline: Конвеєр швидкого парсингу ────────────────────────
def fig_fast_parse_pipeline():
    W, H = 960, 450
    p = []

    # Вхідний буфер
    p.append(fitbox(30, 48, 900, 52,
                    "Вхідний рядок: \"2026-08-20T22:30:15Z\" (довжина 20 байтів, нуль динамічних алокацій)",
                    size=14, fill=BLUE_F, stroke=NEG, sw=2, bold=True))

    # 4 етапи конвеєра
    stages = [
        (30, 118, 205, 175,
         "1. Перевірка міток\n\n"
         "Перевірка розділювачів\n"
         "за фіксованими індексами:\n"
         "s[4]  == '-'\n"
         "s[7]  == '-'\n"
         "s[10] == 'T' || ' '\n"
         "s[13] == ':'\n"
         "s[16] == ':'",
         GREY_F, LINE),
        (255, 118, 215, 175,
         "2. Швидке множення\n\n"
         "Дві цифри за операцію:\n"
         "val = s[0]*10 + s[1] - 528\n\n"
         "Чотири цифри року:\n"
         "Y = (s[0]*1000 + s[1]*100\n"
         "   + s[2]*10 + s[3]) - 53328\n"
         "Без виклику atoi / sscanf!",
         GREEN_F, FIELD),
        (490, 118, 215, 175,
         "3. Перевірка меж\n\n"
         "Контроль діапазонів:\n"
         "• Місяць: 1 <= M <= 12\n"
         "• День: 1 <= D <= days_in_m\n"
         "• Година: 0 <= h <= 23\n"
         "• Хвилина: 0 <= m <= 59\n"
         "• Секунда: 0 <= s <= 60",
         YELLOW_F, LINE),
        (725, 118, 205, 175,
         "4. Зміщення UTC\n\n"
         "Обробка суфікса:\n"
         "• 'Z' → offset = 0 хв\n"
         "• '+hh:mm' → + (h*60+m)\n"
         "• '-hh:mm' → - (h*60+m)\n\n"
         "Unix epoch seconds = \n"
         "days_from_civil(Y,M,D)*86400\n"
         "+ h*3600 + m*60 + s - off",
         PURPLE_F, PURPLE_LINE),
    ]

    for x, y, w, h, txt, fill, stroke in stages:
        p.append(fitbox(x, y, w, h, txt, size=12, fill=fill, stroke=stroke, sw=1.6))

    # Нижня стрілка результату
    p.append(fitbox(30, 310, 900, 110,
                    "Результат конвеєра: struct tm / unix_timestamp_ns без звернення до купи (Heap)\n\n"
                    "• Продуктивність: ~10-25 наносекунд на мітку часу на сучасному CPU\n"
                    "• Відсутність фрагментації пам'яті та тиску на GC (у Go / Java / Node.js)\n"
                    "• Прогнозований час виконання для високочастотного трейдингу, HFT та IoT",
                    size=12, fill=BG, stroke=NEG, sw=1.8, bold=True))

    render(os.path.join(OUT, "fast-parse-pipeline.svg"), W, H, *p,
           title="Конвеєр побайтового парсингу ISO 8601 без динамічних алокацій")


if __name__ == "__main__":
    fig_iso8601_anatomy()
    fig_lexicographical_sorting()
    fig_interval_and_duration()
    fig_leap_second_timeline()
    fig_fast_parse_pipeline()
    print("All 5 figures generated successfully.")
