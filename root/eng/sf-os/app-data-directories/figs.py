# -*- coding: utf-8 -*-
"""Фігури до теми «Теки застосунку: конфіг, дані, кеш» (eng/sf-os/app-data-directories)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Таксономія каталогів застосунку XDG та відповідність FHS ──────────────
def fig_app_directory_taxonomy():
    W, H = 1000, 460
    frags = []

    # Заголовки колонок
    cx1, w1 = 30, 210   # Категорія та змінна
    cx2, w2 = 250, 200  # Шлях у home та FHS
    cx3, w3 = 460, 150  # Носій та режим
    cx4, w4 = 620, 170  # Резервне копіювання
    cx5, w5 = 800, 170  # Безпека видалення

    hy, hh = 45, 36
    frags.append(fitbox(cx1, hy, w1, hh, "Категорія та змінна XDG", size=13, bold=True, fill="#eef2f7"))
    frags.append(fitbox(cx2, hy, w2, hh, "Шлях XDG та FHS", size=13, bold=True, fill="#eef2f7"))
    frags.append(fitbox(cx3, hy, w3, hh, "Носій і права", size=13, bold=True, fill="#eef2f7"))
    frags.append(fitbox(cx4, hy, w4, hh, "Резервування (backup)", size=13, bold=True, fill="#eef2f7"))
    frags.append(fitbox(cx5, hy, w5, hh, "Наслідок видалення", size=13, bold=True, fill="#eef2f7"))

    rows = [
        ("Конфігурація (Config)\n$XDG_CONFIG_HOME",
         "~/.config\n(FHS: /etc)",
         "Диск (Disk)\n0700 / 0755",
         "Критичне (в git/dotfiles)\nМалий обсяг",
         "Втрата налаштувань\nкористувача",
         "#ffffff", LINE),
        ("Робочі дані (Data)\n$XDG_DATA_HOME",
         "~/.local/share\n(FHS: /var/lib, /usr/share)",
         "Диск (Disk)\n0700 / 0755",
         "Обов'язкове (бази, сейви)\nВеликий обсяг",
         "Втрата важливих даних\nі стану роботи",
         "#ffffff", LINE),
        ("Стан сесії (State)\n$XDG_STATE_HOME",
         "~/.local/state\n(FHS: /var/log)",
         "Диск (Disk)\n0700",
         "Не резервується\n(виключити з dotfiles)",
         "Скидання історії, логів\nта геометрії вікон",
         "#ffffff", LINE),
        ("Кеш (Cache)\n$XDG_CACHE_HOME",
         "~/.cache\n(FHS: /var/cache)",
         "Диск (Disk)\n0700 / 0755",
         "Суворо виключити\n(сміття для бекапу)",
         "Безпечно видаляти;\nпрограма перегенерує",
         "#eaf0fd", NEG),
        ("Рантайм-сокети (Runtime)\n$XDG_RUNTIME_DIR",
         "/run/user/$UID\n(FHS: /run)",
         "RAM (tmpfs)\nСтрого 0700",
         "Неможливо й не треба\n(живе лише в сесії)",
         "Знищується ядром\nпри виході з системи",
         "#fdecea", POS),
    ]

    y = 90
    rh, gap = 64, 10
    for col1, col2, col3, col4, col5, fill, stroke in rows:
        frags.append(fitbox(cx1, y, w1, rh, col1, size=12, fill=fill, stroke=stroke))
        frags.append(fitbox(cx2, y, w2, rh, col2, size=12, fill=fill, stroke=stroke))
        frags.append(fitbox(cx3, y, w3, rh, col3, size=12, fill=fill, stroke=stroke))
        frags.append(fitbox(cx4, y, w4, rh, col4, size=12, fill=fill, stroke=stroke))
        frags.append(fitbox(cx5, y, w5, rh, col5, size=12, fill=fill, stroke=stroke))
        y += rh + gap

    render(os.path.join(OUT, 'app-directory-taxonomy.svg'), W, H, *frags,
           title="Таксономія каталогів застосунку: XDG Base Directory та відповідність FHS")


# ── 2. Атомарний запис конфігурації проти прямого перезапису ──────────────────
def fig_atomic_write_vs_direct():
    W, H = 1000, 440
    frags = []

    # Ліва колонка: Небезпечний прямий запис
    frags.append(fitbox(30, 45, 440, 36, "Прямий небезпечний запис (O_TRUNC)", size=14, bold=True, fill="#fdecea", stroke=POS))
    
    frags.append(fitbox(50, 95, 400, 50, "1. open(\"app.conf\", O_WRONLY|O_CREAT|O_TRUNC)\nФайл миттєво обнуляється на диску (розмір = 0)", size=12, fill="#ffffff", stroke=POS))
    frags.append(arrow(250, 145, 250, 175, color=POS))
    
    frags.append(fitbox(50, 175, 400, 50, "2. write(fd, buf, len)\nПобайтовий запис у файл частинами", size=12, fill="#ffffff", stroke=POS))
    frags.append(arrow(250, 225, 250, 255, color=POS))

    frags.append(fitbox(50, 255, 400, 60, "АВАРІЯ (SIGKILL, падіння або збій живлення)\nпід час кроку 1 або 2", size=12, bold=True, fill="#fdecea", stroke=POS))
    frags.append(arrow(250, 315, 250, 345, color=POS))

    frags.append(fitbox(50, 345, 400, 65, "НАСЛІДОК: Порожній або пошкоджений файл (0 байт).\nКонфігурацію втрачено, застосунок падає при старті!", size=12, fill="#fdecea", stroke=POS))

    # Права колонка: Надійний атомарний запис
    frags.append(fitbox(530, 45, 440, 36, "Надійний атомарний запис (tempfile + rename)", size=14, bold=True, fill="#e8f8f5", stroke=FIELD))

    frags.append(fitbox(550, 95, 400, 45, "1. mkstemp(\"app.conf.tmpXXXXXX\") або O_TMPFILE\nСтворення тимчасового файлу в тому ж каталозі", size=11, fill="#ffffff", stroke=FIELD))
    frags.append(arrow(750, 140, 750, 160, color=FIELD))

    frags.append(fitbox(550, 160, 400, 45, "2. write() повного вмісту та fsync(fd)\nГарантоване скидання даних ядра на фізичний диск", size=11, fill="#ffffff", stroke=FIELD))
    frags.append(arrow(750, 205, 750, 225, color=FIELD))

    frags.append(fitbox(550, 225, 400, 45, "3. rename(\"app.conf.tmp\", \"app.conf\")\nАтомарна зміна покажчика в каталозі (VFS rename)", size=11, fill="#ffffff", stroke=FIELD))
    frags.append(arrow(750, 270, 750, 290, color=FIELD))

    frags.append(fitbox(550, 290, 400, 45, "4. fsync(dir_fd)\nСинхронізація запису каталогу в журналі ФС", size=11, fill="#ffffff", stroke=FIELD))
    frags.append(arrow(750, 335, 750, 355, color=FIELD))

    frags.append(fitbox(550, 355, 400, 55, "РЕЗУЛЬТАТ: У будь-який момент аварії існує або\nповністю стара валідна версія, або повністю нова!", size=12, bold=True, fill="#e8f8f5", stroke=FIELD))

    render(os.path.join(OUT, 'atomic-write-vs-direct.svg'), W, H, *frags,
           title="Порівняння: прямий запис з обнуленням проти атомарної заміни через rename")


# ── 3. Автомат резолюції шляхів XDG ──────────────────────────────────────────
def fig_xdg_resolution_pipeline():
    W, H = 1000, 420
    frags = []

    # Крок 1
    frags.append(fitbox(30, 60, 220, 70, "1. Запит типу каталогу\n(наприклад, CONFIG)\nдля програми \"myapp\"", size=12, fill="#ffffff", stroke=LINE))
    frags.append(arrow(250, 95, 290, 95))

    # Крок 2: Перевірка змінної
    frags.append(fitbox(290, 60, 240, 70, "2. Перевірка getenv()\n$XDG_CONFIG_HOME\nчи задано і чи шлях абсолютний?", size=12, fill="#eef2f7", stroke=LINE))

    # Гілка ТАК
    frags.append(arrow(530, 95, 620, 95))
    frags.append(text(575, 85, "ТАК", size=11, bold=True, color=FIELD))
    frags.append(fitbox(620, 65, 340, 60, "Шлях = $XDG_CONFIG_HOME / \"myapp\"\nВикористання вказаного каталогу", size=12, fill="#e8f8f5", stroke=FIELD))

    # Гілка НІ
    frags.append(arrow(410, 130, 410, 190))
    frags.append(text(435, 160, "НІ", size=11, bold=True, color=POS))

    # Крок 3: Fallback до $HOME
    frags.append(fitbox(290, 190, 240, 80, "3. Fallback до HOME\nПеревірка getenv(\"HOME\")\nякщо пусто -> getpwuid(getuid())", size=12, fill="#ffffff", stroke=LINE))
    frags.append(arrow(530, 230, 620, 230))

    # Крок 4: Склеювання дефолтного шляху
    frags.append(fitbox(620, 200, 340, 60, "Шлях = $HOME / \".config\" / \"myapp\"\nСтандартний шлях за специфікацією", size=12, fill="#ffffff", stroke=LINE))

    # Зведення до створення каталогу
    frags.append(arrow(790, 125, 790, 160))
    frags.append(arrow(790, 260, 790, 300))

    frags.append(fitbox(620, 300, 340, 75, "4. Рекурсивне створення mkdir_p()\nз правами 0700 (приватні налаштування)\nабо 0755 за системною umask", size=12, bold=True, fill="#eef2f7", stroke=LINE))

    # Блок системних каталогів зліва
    frags.append(fitbox(30, 290, 220, 90, "Каскадний пошук конфігів:\n1. Користувацький каталог\n2. $XDG_CONFIG_DIRS\n(типово: /etc/xdg)", size=11, fill="#f4f6f8", stroke=LINE))

    render(os.path.join(OUT, 'xdg-resolution-pipeline.svg'), W, H, *frags,
           title="Конвеєр резолюції каталогів: перевірка змінних оточення, fallback та права")


if __name__ == '__main__':
    fig_app_directory_taxonomy()
    fig_atomic_write_vs_direct()
    fig_xdg_resolution_pipeline()
    print("All figures generated successfully.")
