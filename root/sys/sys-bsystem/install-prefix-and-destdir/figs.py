# -*- coding: utf-8 -*-
"""Фігури до теми «Куди ставиться програма: prefix, DESTDIR і /usr/local»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL = "#eafaf1"
ACCENT_FILL = "#eaf0fd"
NEUTRAL_FILL = "#f8f9fa"


# ── 1. Ієрархія FHS: розмежування рівнів володіння ──────────────────────────
def fig_fhs_hierarchy():
    W, H = 1040, 560
    frags = []

    frags.append(text(520, 40, "Розподіл просторів імен у файловій системі Linux за стандартом FHS", size=13, color=MUTED))

    # Блок 1: /usr
    b1_title = "/usr (Дистрибутивні пакети)"
    b1_body = (
        "Власник: Менеджер пакетів (apt, dnf, pacman)\n"
        "• /usr/bin     — системні виконувані файли\n"
        "• /usr/lib     — динамічні бібліотеки (.so)\n"
        "• /usr/share   — архітектурно-незалежні ресурси\n"
        "• /usr/include — системні C/C++ заголовки\n\n"
        "Ручний запис у /usr суворо заборонений:\n"
        "будь-яке оновлення ОС перезапише ваші файли!"
    )
    frags.append(fitbox(40, 70, 460, 200, b1_title + "\n\n" + b1_body, size=11.5, fill=ACCENT_FILL, stroke=NEG))

    # Блок 2: /usr/local
    b2_title = "/usr/local (Локальний адміністратор)"
    b2_body = (
        "Власник: Системний адміністратор (ручна збірка)\n"
        "• /usr/local/bin     — локально зібрані утиліти\n"
        "• /usr/local/lib     — локальні спільні бібліотеки\n"
        "• /usr/local/include — додаткові заголовки C/C++\n\n"
        "Пакетний менеджер ОС ніколи не чіпає цей каталог.\n"
        "Стандартний префікс за замовчуванням у CMake та GNU."
    )
    frags.append(fitbox(540, 70, 460, 200, b2_title + "\n\n" + b2_body, size=11.5, fill=OK_FILL, stroke=FIELD))

    # Блок 3: /opt
    b3_title = "/opt (Автономні сторонні пакети)"
    b3_body = (
        "Власник: Сторонній розробник / вендор (Chrome, CLion, CUDA)\n"
        "• /opt/vendor/app/bin — ізольований виконуваний файл\n"
        "• /opt/vendor/app/lib — приватні зв'язані бібліотеки\n\n"
        "Кожен пакет живе у власній замкненій ієрархії.\n"
        "Не змішується з іншими програмами системи."
    )
    frags.append(fitbox(40, 290, 460, 160, b3_title + "\n\n" + b3_body, size=11.5, fill=NEUTRAL_FILL, stroke=LINE))

    # Блок 4: ~/.local
    b4_title = "~/.local (Користувацький простір XDG)"
    b4_body = (
        "Власник: Звичайний користувач без root-прав\n"
        "• ~/.local/bin   — особисті скрипти та утиліти\n"
        "• ~/.local/lib   — локальні бібліотеки користувача\n"
        "• ~/.local/share — дані застосунків користувача\n\n"
        "Безпечне встановлення через CMAKE_INSTALL_PREFIX=$HOME/.local"
    )
    frags.append(fitbox(540, 290, 460, 160, b4_title + "\n\n" + b4_body, size=11.5, fill=OK_FILL, stroke=FIELD))

    # Нижній висновок
    frags.append(fitbox(40, 470, 960, 50,
                        "Головне правило: /usr належить ОС; /usr/local — адміністратору хоста; /opt — вендорам; ~/.local — користувачу",
                        size=12.5, bold=True, fill=WARN_FILL, stroke=POS))

    render(os.path.join(IMG, "fig-fhs-hierarchy.svg"), W, H, *frags,
           title="Ієрархія просторів FHS у системі Linux")


# ── 2. Рівняння DESTDIR + PREFIX ────────────────────────────────────────────
def fig_destdir_equation():
    W, H = 1040, 560
    frags = []

    frags.append(text(520, 40, "Розведення шляхів копіювання та шляхів виконання під час пакування", size=13, color=MUTED))

    # Блок 1: Конфігурація часу компіляції (PREFIX)
    p_title = "1. КОМПІЛЯЦІЯ: Цільовий PREFIX (/usr)"
    p_body = (
        "cmake -B build -DCMAKE_INSTALL_PREFIX=/usr\n\n"
        "Зашивається в бінарні артефакти:\n"
        "• Шлях до ресурсів: /usr/share/myapp/data.json\n"
        "• Пошуковий RUNPATH: /usr/lib/myapp\n"
        "• Shebang скриптів: #!/usr/bin/python3\n"
        "• pkg-config (.pc): prefix=/usr"
    )
    frags.append(fitbox(40, 70, 430, 180, p_title + "\n\n" + p_body, size=11.5, fill=ACCENT_FILL, stroke=NEG))

    # Блок 2: Тимчасовий DESTDIR під час інсталяції
    d_title = "2. ПАКУВАННЯ: Тимчасовий DESTDIR (/tmp/pkg)"
    d_body = (
        "DESTDIR=/tmp/pkg cmake --install build\n\n"
        "Фізичне копіювання файлів у тимчасовий каталог:\n"
        "• DESTDIR діє ТІЛЬКИ як префікс файлової операції копіювання\n"
        "• Файл потрапляє у /tmp/pkg/usr/bin/myapp\n"
        "• Дані потрапляють у /tmp/pkg/usr/share/myapp/data.json"
    )
    frags.append(fitbox(570, 70, 430, 180, d_title + "\n\n" + d_body, size=11.5, fill=OK_FILL, stroke=FIELD))

    # Центральна формульна стрілка
    frags.append(fitbox(40, 270, 960, 60,
                        "Рівняння пакувальника: Шлях запису на диск = ${DESTDIR}${PREFIX}/${PATH_SUFFIX}\n"
                        "Приклад: /tmp/pkg + /usr + /bin/app  →  /tmp/pkg/usr/bin/app",
                        size=13, bold=True, fill=NEUTRAL_FILL, stroke=LINE))

    # Нижній лівий блок: Робота пакувальника
    b_pack = (
        "3. Складання пакета (.deb / .rpm / .apk)\n"
        "Пакувальник бере дерево з /tmp/pkg/ і пакує в архів.\n"
        "Префікс /tmp/pkg відкидається — в архіві файли мають шлях /usr/..."
    )
    frags.append(fitbox(40, 350, 430, 90, b_pack, size=11.5, fill=OK_FILL, stroke=FIELD))

    # Нижній правий блок: Робота на цільовій машині
    b_run = (
        "4. Виконання на машині клієнта (dpkg -i / rpm -i)\n"
        "Архів розпаковується в /usr/...\n"
        "Бінарник запускається і шукає дані за вшитим /usr/share/myapp — УСПІХ!"
    )
    frags.append(fitbox(570, 350, 430, 90, b_run, size=11.5, fill=ACCENT_FILL, stroke=NEG))

    # Попередження про помилку
    frags.append(fitbox(40, 460, 960, 60,
                        "Критична помилка: якщо DESTDIR випадково потрапить у бінарник (-DDATADIR=\"$DESTDIR/usr/share\"), "
                        "програма впаде на клієнтській машині, бо каталогу /tmp/pkg там не існує!",
                        size=12, bold=True, fill=WARN_FILL, stroke=POS))

    render(os.path.join(IMG, "fig-destdir-equation.svg"), W, H, *frags,
           title="Рівняння DESTDIR + PREFIX: розведення шляхів копіювання та виконання")


# ── 3. Релокабельність через $ORIGIN ────────────────────────────────────────
def fig_rpath_origin_relocation():
    W, H = 1040, 560
    frags = []

    frags.append(text(520, 40, "Динамічне обчислення шляху до спільних бібліотек через $ORIGIN у RUNPATH", size=13, color=MUTED))

    # Варіант 1: Абсолютний RPATH (жорстка прив'язка)
    v1_title = "Варіант А: Абсолютний RUNPATH (/opt/myapp/lib)"
    v1_body = (
        "Встановлений виконуваний файл: /opt/myapp/bin/app\n"
        "RUNPATH у заголовку ELF: /opt/myapp/lib\n\n"
        "• Якщо користувач перемістить пакет у /home/user/apps/myapp:\n"
        "  Бінарник шукатиме /opt/myapp/lib/libcore.so\n"
        "  ПОМИЛКА: libcore.so not found! Пакет не переміщуваний."
    )
    frags.append(fitbox(40, 70, 460, 190, v1_title + "\n\n" + v1_body, size=11.5, fill=WARN_FILL, stroke=POS))

    # Варіант 2: Відносний RPATH з $ORIGIN
    v2_title = "Варіант Б: Відносний RUNPATH ($ORIGIN/../lib)"
    v2_body = (
        "Встановлений виконуваний файл: <будь-де>/bin/app\n"
        "RUNPATH у заголовку ELF: $ORIGIN/../lib\n\n"
        "• $ORIGIN динамічно розгортається завантажувачем у шлях до bin/\n"
        "• $ORIGIN/../lib завжди точно вказує на сусідній каталог lib/\n"
        "  УСПІХ: пакет працює в /opt, /usr/local, ~/.local чи на USB-носії!"
    )
    frags.append(fitbox(540, 70, 460, 190, v2_title + "\n\n" + v2_body, size=11.5, fill=OK_FILL, stroke=FIELD))

    # Схема структури каталогу та стрілка резолвінгу
    tree_box = (
        "Структура релокабельного пакета:\n"
        "myapp-bundle/\n"
        " ├── bin/\n"
        " │    └── app        <── виконуваний файл ($ORIGIN = /шлях/до/myapp-bundle/bin)\n"
        " └── lib/\n"
        "      └── libcore.so <── знайдено через $ORIGIN/../lib/libcore.so"
    )
    frags.append(fitbox(40, 280, 960, 150, tree_box, size=12, fill="#ffffff", stroke=LINE))

    # Підсумок у CMake
    cmake_box = (
        "Конфігурація в CMake: set(CMAKE_INSTALL_RPATH \"$ORIGIN/../lib\")\n"
        "На macOS використовується аналог @executable_path/../lib або @loader_path/../lib"
    )
    frags.append(fitbox(40, 450, 960, 60, cmake_box, size=12.5, bold=True, fill=ACCENT_FILL, stroke=NEG))

    render(os.path.join(IMG, "fig-rpath-origin-relocation.svg"), W, H, *frags,
           title="Релокабельність бібліотек через відносний $ORIGIN у RPATH")


if __name__ == "__main__":
    fig_fhs_hierarchy()
    fig_destdir_equation()
    fig_rpath_origin_relocation()
    print("Фігури успішно згенеровано.")
