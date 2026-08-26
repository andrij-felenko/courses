# -*- coding: utf-8 -*-
"""Фігури до теми «Часові позначки файлів: mtime, ctime і роздільність».
Запуск: python figs.py   → створює SVG у ./img/
"""
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Колірна палітра теми
AMBER  = "#b08900"   # попередження, relatime
SOFT_B = "#eef3fd"   # світло-синій (atime / читання)
SOFT_G = "#eaf7ef"   # світло-зелений (mtime / дані)
SOFT_A = "#fff6e0"   # світло-бурштиновий (ctime / метадані)
SOFT_R = "#fdecea"   # світло-червоний (btime / конфлікт)
DARK_B = "#1e40af"
DARK_G = "#166534"
DARK_A = "#92400e"
DARK_R = "#991b1b"


# ── 1. Структура часових позначок у дисковому іноді (Ext4 / XFS / Btrfs) ────────
def fig_inode_timestamps():
    W, H = 940, 480
    f = [text(W / 2, 28, "Анатомія часових позначок у дисковому іноді Linux (Ext4 / XFS)",
              size=16, bold=True)]

    # Загальний контейнер інода
    f.append(rect(40, 56, 860, 396, fill="#fcfdfe", stroke=LINE, sw=1.5, rx=8))
    f.append(text(80, 80, "Дисковий інод (struct ext4_inode, 256 байтів)", size=13, color=MUTED, anchor="start", bold=True))

    # Секція 1: Базова спадщина Unix (128 байтів, 32-бітний time_t)
    f.append(rect(60, 96, 820, 150, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(80, 118, "Базове тіло інода (перші 128 байтів) · 32-бітна епоха Unix (секундна точність)",
                  size=12, color="#475569", anchor="start", bold=True))

    # 3 поля базового тіла
    fields_base = [
        (80, 134, 240, 96, "i_atime (32 біти)", "Час останнього читання\n__le32 секунди від 1970\nДіапазон: 1901–2038 рр.", SOFT_B, DARK_B),
        (350, 134, 240, 96, "i_mtime (32 біти)", "Час зміни вмісту даних\n__le32 секунди від 1970\nОновлюється при write()", SOFT_G, DARK_G),
        (620, 134, 240, 96, "i_ctime (32 біти)", "Час зміни метаданих\n__le32 секунди від 1970\nОновлюється ядром VFS", SOFT_A, DARK_A),
    ]
    for x, y, w, h, title, desc, bg, col in fields_base:
        f.append(rect(x, y, w, h, fill=bg, stroke=col, sw=1.2, rx=5))
        f.append(text(x + w / 2, y + 22, title, size=12, color=col, bold=True))
        f.append(mtext(x + w / 2, y + 46, desc, size=10, color=INK, lh=1.3))

    # Секція 2: Розширене тіло (extra_isize, наносекунди та розширення епохи)
    f.append(rect(60, 260, 820, 174, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(80, 282, "Розширена частина (i_extra_isize) · Наносекунди + захист Y2038 + час народження",
                  size=12, color="#475569", anchor="start", bold=True))

    fields_extra = [
        (80, 298, 180, 120, "i_atime_extra", "30 бітів: наносекунди\n2 біти: епоха\n(до 2446 року)", SOFT_B, DARK_B),
        (280, 298, 180, 120, "i_mtime_extra", "30 бітів: наносекунди\n2 біти: епоха\n(до 2446 року)", SOFT_G, DARK_G),
        (480, 298, 180, 120, "i_ctime_extra", "30 бітів: наносекунди\n2 біти: епоха\n(до 2446 року)", SOFT_A, DARK_A),
        (680, 298, 180, 120, "i_crtime / btime", "Час створення файлу\n32 біти sec + nsec\n(Ext4/XFS v5/Btrfs)", SOFT_R, DARK_R),
    ]
    for x, y, w, h, title, desc, bg, col in fields_extra:
        f.append(rect(x, y, w, h, fill=bg, stroke=col, sw=1.2, rx=5))
        f.append(text(x + w / 2, y + 22, title, size=11, color=col, bold=True))
        f.append(mtext(x + w / 2, y + 52, desc, size=10, color=INK, lh=1.35))

    render(os.path.join(IMG, "timestamps-in-inode.svg"), W, H, *f)


# ── 2. Режими монтування atime та навантаження диска ───────────────────────────
def fig_atime_modes():
    W, H = 940, 420
    f = [text(W / 2, 28, "Порівняння політик оновлення atime при операціях читання файлу",
              size=16, bold=True)]

    modes = [
        (40, 64, 200, 326, "strictatime",
         "Кожне read() оновлює atime",
         "100% операцій читання",
         "Генерує запис метаданих\nна носій при кожному\nзчитуванні байтів.\n\nПодвоює I/O запитів.\nЗношує SSD і бруднить\nкеш сторінок VFS.",
         SOFT_R, POS, DARK_R),

        (260, 64, 200, 326, "relatime (типово)",
         "Оновлення лише за умови",
         "<= mtime / ctime або >24 год",
         "Оновлює atime тільки\nякщо старий atime\nменший за mtime/ctime,\nабо якщо минула 1 доба.\n\nЗнижує I/O на 95–99%,\nзберігаючи логіку утиліт.",
         SOFT_G, FIELD, DARK_G),

        (480, 64, 200, 326, "noatime",
         "Повна відмова від запису",
         "0% оновлень atime",
         "atime не оновлюється\nвзагалі під час читання.\n\nНайвища швидкодія I/O.\nМоже заважати старим\nпоштовим демонам чи\nагентам бекапів.",
         SOFT_B, NEG, DARK_B),

        (700, 64, 200, 326, "lazytime",
         "Відкладений запис на диск",
         "Тільки в пам'яті (RAM)",
         "Зміни atime/mtime/ctime\nтримаються в пам'яті\nструктури struct inode.\n\nСкидаються на диск лише\nпри оновленні тіла інода\nабо виклику sync().",
         SOFT_A, AMBER, DARK_A),
    ]

    for x, y, w, h, name, subtitle, trigger, desc, bg, border_col, title_col in modes:
        f.append(rect(x, y, w, h, fill=bg, stroke=border_col, sw=1.5, rx=8))
        f.append(text(x + w / 2, y + 26, name, size=13, color=title_col, bold=True))
        f.append(text(x + w / 2, y + 48, subtitle, size=10, color=MUTED, bold=True))
        f.append(line(x + 12, y + 60, x + w - 12, y + 60, color=border_col, sw=1.0))

        # Блок умови
        f.append(rect(x + 10, y + 72, w - 20, 48, fill="#ffffff", stroke=border_col, sw=1.0, rx=4))
        f.append(text(x + w / 2, y + 88, "Критерій скидання:", size=9, color=MUTED))
        f.append(text(x + w / 2, y + 106, trigger, size=9, color=title_col, bold=True))

        # Опис поведінки
        f.append(mtext(x + w / 2, y + 146, desc, size=10, color=INK, lh=1.35))

    render(os.path.join(IMG, "atime-mount-modes.svg"), W, H, *f)


# ── 3. Проблема роздільності часу в системах збирання ──────────────────────────
def fig_build_race():
    W, H = 940, 430
    f = [text(W / 2, 28, "Конфлікт 1-секундної дискретизації часу проти наносекундної точності",
              size=16, bold=True)]

    # Ліва колонка: 1-секундна гранулярність (Класичний Make)
    f.append(rect(40, 56, 415, 346, fill="#fdf8f6", stroke=POS, sw=1.5, rx=8))
    f.append(text(247, 84, "1-секундна епоха (time_t) · Пропуск збірки", size=13, color=DARK_R, bold=True))

    # Хронологія 1 сек
    f.append(rect(60, 106, 375, 48, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    f.append(text(247, 126, "Секунда t = 1700000042", size=11, color=DARK_B, bold=True))
    f.append(text(247, 142, "Діапазон 0.000 с ... 0.999 с", size=10, color=MUTED))

    events_1s = [
        (60, 166, "12:00:42.100 — Компілятор створює app.o", "mtime(app.o) = 1700000042 s", SOFT_B, DARK_B),
        (60, 226, "12:00:42.450 — Розробник править main.c", "mtime(main.c) = 1700000042 s", SOFT_A, DARK_A),
        (60, 286, "12:00:42.800 — Запуск Make", "mtime(src) <= mtime(obj) -> ПРОПУСК ЗБІРКИ!", SOFT_R, DARK_R),
    ]
    for x, y, title, sub, bg, col in events_1s:
        f.append(rect(x, y, 375, 48, fill=bg, stroke=col, sw=1.1, rx=5))
        f.append(text(x + 187, y + 20, title, size=10, color=INK, bold=True))
        f.append(text(x + 187, y + 38, sub, size=10, color=col, bold=True))

    f.append(text(247, 362, "Результат: дефект «невидимої зміни» вихідного коду", size=10, color=POS, bold=True))

    # Права колонка: Наносекундна точність (statx / Ninja)
    f.append(rect(485, 56, 415, 346, fill="#f6faf7", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(692, 84, "Наносекундна точність (struct timespec / statx)", size=13, color=DARK_G, bold=True))

    # Хронологія nsec
    f.append(rect(505, 106, 375, 48, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    f.append(text(692, 126, "Високоточний таймер ядра (ktime / TSC)", size=11, color=DARK_G, bold=True))
    f.append(text(692, 142, "Дискретизація до 1 наносекунди (10⁻⁹ с)", size=10, color=MUTED))

    events_ns = [
        (505, 166, "12:00:42.100000000 — Компіляція app.o", "mtime = 1700000042.100000000 s", SOFT_B, DARK_B),
        (505, 226, "12:00:42.450000000 — Збереження main.c", "mtime = 1700000042.450000000 s", SOFT_G, DARK_G),
        (505, 286, "12:00:42.800000000 — Запуск Ninja", "42.450 s > 42.100 s -> ЦІЛЬ ЗАСТАРІЛА, ЗБІРКА!", SOFT_G, DARK_G),
    ]
    for x, y, title, sub, bg, col in events_ns:
        f.append(rect(x, y, 375, 48, fill=bg, stroke=col, sw=1.1, rx=5))
        f.append(text(x + 187, y + 20, title, size=10, color=INK, bold=True))
        f.append(text(x + 187, y + 38, sub, size=10, color=col, bold=True))

    f.append(text(692, 362, "Результат: надійна детекція послідовності правок", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG, "build-granularity-race.svg"), W, H, *f)


# ── 4. Послідовність зміни позначок під час життєвого циклу файлу ─────────────
def fig_lifecycle_transitions():
    W, H = 940, 440
    f = [text(W / 2, 28, "Динаміка оновлення позначок atime, mtime і ctime при операціях VFS",
              size=16, bold=True)]

    steps = [
        (40, 60, 200, 340, "1. Створення файлу", "open(O_CREAT | ...)",
         "Встановлюються:\n• btime = T₀\n• mtime = T₀\n• ctime = T₀\n• atime = T₀\n\nУсі 4 позначки\nініціалізуються часом\nстворення інода.",
         SOFT_R, DARK_R),

        (260, 60, 200, 340, "2. Запис у файл", "write(fd, buf, len)",
         "Оновлюються:\n• mtime = T₁ (дані)\n• ctime = T₁ (розмір)\n\nБез змін:\n• atime (не читався)\n• btime (незмінний)",
         SOFT_G, DARK_G),

        (480, 60, 200, 340, "3. Зміна прав", "chmod() / rename()",
         "Оновлюється:\n• ctime = T₂ (метадані)\n\nБез змін:\n• mtime (тіло ціле)\n• atime (не читався)\n• btime (незмінний)",
         SOFT_A, DARK_A),

        (700, 60, 200, 340, "4. Читання файлу", "read(fd, buf, len)",
         "Оновлюється:\n• atime = T₃ (читання)\n\nБез змін:\n• mtime (без запису)\n• ctime (без правок)\n• btime (незмінний)",
         SOFT_B, DARK_B),
    ]

    for x, y, w, h, title, sub, desc, bg, col in steps:
        f.append(rect(x, y, w, h, fill=bg, stroke=col, sw=1.4, rx=8))
        f.append(text(x + w / 2, y + 28, title, size=13, color=col, bold=True))
        f.append(text(x + w / 2, y + 50, sub, size=10, color=MUTED, bold=True))
        f.append(line(x + 12, y + 64, x + w - 12, y + 64, color=col, sw=1.0))
        f.append(mtext(x + w / 2, y + 104, desc, size=11, color=INK, lh=1.4))

    # Стрілки переходу між кроками
    f.append(arrow(242, 230, 258, 230, color=LINE, sw=1.8))
    f.append(arrow(462, 230, 478, 230, color=LINE, sw=1.8))
    f.append(arrow(682, 230, 698, 230, color=LINE, sw=1.8))

    render(os.path.join(IMG, "timestamp-lifecycle.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inode_timestamps()
    fig_atime_modes()
    fig_build_race()
    fig_lifecycle_transitions()
    print("Усі 4 фігури згенеровано успішно в ./img/")
