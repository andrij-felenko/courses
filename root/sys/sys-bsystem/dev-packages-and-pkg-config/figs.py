# -*- coding: utf-8 -*-
"""Фігури до теми «Заголовки й -dev пакунки: pkg-config і де лежить чужий API»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL = "#eaf5ec"
ACCENT_FILL = "#eef4fd"


# ── 1. Розподіл пакетів: Runtime проти Development (-dev / -devel) ─────────
def fig_dev_vs_runtime_split():
    W, H = 1040, 520
    frags = []

    frags.append(text(520, 30, "Анатомія розколу пакунків: Runtime проти Development", size=16, bold=True))
    frags.append(text(520, 54, "Дистрибутиви Linux ділять один вихідний код бібліотеки на два взаємодоповнюючі пакети:", size=13, color=MUTED))

    # Ліва колонка: Runtime пакет (libfoo / libfoo1)
    frags.append(fitbox(50, 80, 440, 44, "Пакет виконання: libfoo1 (Runtime)\nЦільова авдиторія: кінцеві користувачі та сервери", size=13, stroke=NEG, fill=ACCENT_FILL, bold=True))

    runtime_items = [
        ("libfoo.so.1.2.0 (бінарний файл)", "Скомпільований спільний об'єкт (ELF shared object)"),
        ("libfoo.so.1 -> libfoo.so.1.2.0", "Симлінк SONAME: потрібен ld.so для запуску програм"),
        ("Конфігурація та ресурси", "Файли даних, локалі, системні сервіси (за потреби)"),
        ("Призначення в системі", "Мінімальний розмір, нуль зайвих файлів на сервері"),
    ]
    y = 136
    for title_txt, desc_txt in runtime_items:
        frags.append(fitbox(50, y, 440, 54, title_txt + "\n" + desc_txt, size=12.5, stroke=LINE, fill=FILL))
        y += 64

    # Права колонка: Development пакет (libfoo-dev / libfoo-devel)
    frags.append(fitbox(550, 80, 440, 44, "Пакет розробки: libfoo-dev / libfoo-devel\nЦільова авдиторія: компілятори, інженери та збірка", size=13, stroke=FIELD, fill=OK_FILL, bold=True))

    dev_items = [
        ("/usr/include/foo/*.h (заголовки)", "Декларації функцій, типів та макросів (C/C++ API)"),
        ("libfoo.so -> libfoo.so.1", "Симлінк без версії: шукається лінкером ld при -lfoo"),
        ("libfoo.a (статичний архів)", "Архів об'єктних файлів для прапорця -static"),
        ("/usr/lib/.../pkgconfig/foo.pc", "Метадані pkg-config: прапорці компіляції та лінкування"),
    ]
    y = 136
    for title_txt, desc_txt in dev_items:
        frags.append(fitbox(550, y, 440, 54, title_txt + "\n" + desc_txt, size=12.5, stroke=FIELD, fill=FILL))
        y += 64

    # Підсумковий блок унизу
    frags.append(fitbox(50, 410, 940, 80,
                         "Чому цей поділ критичний:\n"
                         "1. Заощадження пам'яті: контейнерам і серверам не потрібні гігабайти заголовків і статичних архівів.\n"
                         "2. Співіснування ABI: у системі можуть одночасно стояти libfoo1 і libfoo2, але лише один libfoo-dev.",
                         size=12.5, stroke=LINE, fill=FILL))

    render(os.path.join(IMG, "dev-vs-runtime-split.svg"), W, H, *frags)


# ── 2. Порядок пошуку шляхів та роль sysroot ──────────────────────────────
def fig_search_paths_and_sysroot():
    W, H = 1040, 560
    frags = []

    frags.append(text(520, 30, "Драбина пошуку компілятора, лінкера та pkg-config", size=16, bold=True))
    frags.append(text(520, 54, "Як інструменти знаходять метадані, заголовки та бінарні бібліотеки:", size=13, color=MUTED))

    # Три вертикальні доріжки: Компілятор (Headers), pkg-config (.pc), Лінкер (Libraries)
    frags.append(fitbox(50, 80, 290, 40, "Заголовки (Компілятор)", size=13.5, stroke=NEG, fill=ACCENT_FILL, bold=True))
    frags.append(fitbox(375, 80, 290, 40, "Метадані (pkg-config)", size=13.5, stroke=FIELD, fill=OK_FILL, bold=True))
    frags.append(fitbox(700, 80, 290, 40, "Бібліотеки (Лінкер)", size=13.5, stroke=POS, fill=WARN_FILL, bold=True))

    steps = [
        ("1. Явні прапорці виклику", "-I/path/to/include\n-isystem /custom/include",
         "1. Змінна оточення", "PKG_CONFIG_PATH\n(перевіряється першою)",
         "1. Явні прапорці виклику", "-L/path/to/lib\n-lfoo"),

        ("2. Локальні префікси", "/usr/local/include\n(ручні інсталяції)",
         "2. Системні каталоги", "/usr/lib/.../pkgconfig\n/usr/share/pkgconfig",
         "2. Локальні префікси", "/usr/local/lib\n/usr/local/lib64"),

        ("3. Системні та Multiarch", "/usr/include/<triplet>\n/usr/include",
         "3. Перевизначення sysroot", "PKG_CONFIG_LIBDIR\n(ізоляція крос-збірки)",
         "3. Системні та Multiarch", "/usr/lib/<triplet>\n/usr/lib, /usr/lib64"),

        ("4. Динамічний запуск", "—\n(тільки етап компіляції)",
         "4. Префікс шляхів", "PKG_CONFIG_SYSROOT_DIR\n(додає префікс до -I, -L)",
         "4. Динамічний запуск", "RPATH -> LD_LIBRARY_PATH\n-> /etc/ld.so.cache"),
    ]

    y = 132
    for s1_t, s1_d, s2_t, s2_d, s3_t, s3_d in steps:
        frags.append(fitbox(50, y, 290, 68, s1_t + "\n" + s1_d, size=12, stroke=LINE, fill=FILL))
        frags.append(fitbox(375, y, 290, 68, s2_t + "\n" + s2_d, size=12, stroke=LINE, fill=FILL))
        frags.append(fitbox(700, y, 290, 68, s3_t + "\n" + s3_d, size=12, stroke=LINE, fill=FILL))
        if y < 320:
            frags.append(arrow(195, y + 68, 195, y + 78))
            frags.append(arrow(520, y + 68, 520, y + 78))
            frags.append(arrow(845, y + 68, 845, y + 78))
        y += 78

    frags.append(fitbox(50, 460, 940, 70,
                         "При крос-компіляції PKG_CONFIG_LIBDIR вимикає системні шляхи хоста й спрямовує пошук виключно в sysroot,\n"
                         "а PKG_CONFIG_SYSROOT_DIR автоматично модифікує абсолютні прапорці -I/usr/include -> -I$SYSROOT/usr/include.",
                         size=12.5, stroke=LINE, fill=FILL))

    render(os.path.join(IMG, "search-paths-and-sysroot.svg"), W, H, *frags)


# ── 3. Граф залежностей: Динамічне проти Статичного лінкування ─────────────
def fig_pc_dependency_graph():
    W, H = 1040, 560
    frags = []

    frags.append(text(520, 30, "Розгортання залежностей pkg-config: Shared проти Static", size=16, bold=True))
    frags.append(text(520, 54, "Чому динамічне лінкування потребує одного прапорця, а статичне — усього транзитивного дерева:", size=13, color=MUTED))

    # Ліва частина: Динамічне лінкування (Dynamic / Shared)
    frags.append(fitbox(50, 80, 430, 40, "Динамічне лінкування: pkg-config --libs foo", size=13.5, stroke=NEG, fill=ACCENT_FILL, bold=True))

    body, _, _ = textbox(265, 170, [
        "Бібліотека: foo.pc",
        "Libs: -L${libdir} -lfoo",
        "Requires.private: libcrypto, zlib",
        "Libs.private: -lm -lpthread",
    ], size=12.5, fill=FILL, stroke=LINE)
    frags.append(body)

    frags.append(arrow(265, 220, 265, 270))
    frags.append(text(275, 248, "тільки публічні Libs", size=12, color=MUTED, anchor="start"))

    body, _, _ = textbox(265, 310, [
        "Команда лінкера при збірці програми:",
        "gcc main.o -lfoo -o app",
        "DT_NEEDED у libfoo.so сам вказує на libcrypto та zlib",
        "Динамічний завантажувач ld.so підтягне їх під час запуску",
    ], size=12.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    # Права частина: Статичне лінкування (Static)
    frags.append(fitbox(560, 80, 430, 40, "Статичне лінкування: pkg-config --static --libs foo", size=13.5, stroke=POS, fill=WARN_FILL, bold=True))

    body, _, _ = textbox(775, 170, [
        "Бібліотека: foo.pc",
        "Обхід Requires + Requires.private",
        "і збір усіх Libs + Libs.private",
    ], size=12.5, fill=FILL, stroke=LINE)
    frags.append(body)

    # Дерево залежностей статичного лінкування
    frags.append(arrow(700, 220, 640, 260))
    frags.append(arrow(850, 220, 910, 260))

    body, _, _ = textbox(630, 290, ["libcrypto.pc", "-lcrypto"], size=12, fill=FILL, stroke=LINE)
    frags.append(body)

    body, _, _ = textbox(910, 290, ["zlib.pc", "-lz"], size=12, fill=FILL, stroke=LINE)
    frags.append(body)

    frags.append(arrow(775, 320, 775, 360))

    body, _, _ = textbox(775, 410, [
        "Команда лінкера при статичній збірці:",
        "gcc -static main.o -lfoo -lcrypto -lz -lm -lpthread -o app",
        "Архів libfoo.a містить невирішені символи SHA256_* і deflate;",
        "Лінкер ld мусить отримати всі допоміжні архіви явно!",
    ], size=12.5, fill=WARN_FILL, stroke=POS)
    frags.append(body)

    frags.append(fitbox(50, 480, 940, 56,
                         "Ключ --static змушує pkg-config рекурсивно обійти поля Requires.private і додати прапорці Libs.private,\n"
                         "гарантуючи, що всі транзитивні статичні залежності потраплять у командний рядок у правильному порядку.",
                         size=12.5, stroke=LINE, fill=FILL))

    render(os.path.join(IMG, "pc-dependency-graph.svg"), W, H, *frags)


fig_dev_vs_runtime_split()
fig_search_paths_and_sysroot()
fig_pc_dependency_graph()
print("Figures generated successfully.")
