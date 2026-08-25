# -*- coding: utf-8 -*-
"""Фігури до теми «Конфігурація, генерація і збірка поза деревом джерел»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

DIRTY = "#fdecea"
CLEAN = "#eaf7ef"
PANEL = "#f8fafc"
ACCENT = "#eef2ff"


# ── 1. Три фази життєвого циклу збірки ──────────────────────────────────────
def fig_phases():
    W, H = 1040, 520
    p = []

    # Три колонки для трьох фаз
    cols = [
        (40, 40, 290, 440, "Фаза 1 · Конфігурація", "(Configure Time)", NEG),
        (375, 40, 290, 440, "Фаза 2 · Генерація", "(Generate Time)", FIELD),
        (710, 40, 290, 440, "Фаза 3 · Виконання", "(Build Execution)", POS),
    ]

    for x, y, w, h, title_text, sub_text, color in cols:
        p.append(rect(x, y, w, h, fill=PANEL, stroke=color, sw=2, rx=8))
        p.append(text(x + w / 2, y + 28, title_text, size=15, bold=True, color=INK))
        p.append(text(x + w / 2, y + 48, sub_text, size=12.5, italic=True, color=MUTED))

    # Стрілки переходу між фазами
    p.append(arrow(332, 260, 372, 260, color=LINE, sw=2))
    p.append(arrow(667, 260, 707, 260, color=LINE, sw=2))

    # Фаза 1: Конфігурація
    p.append(fitbox(55, 90, 260, 60, "ВХОДИ\nCMakeLists.txt · Опції (-D)\nКомпілятор і тулчейн", size=13, fill=BG))
    p.append(fitbox(55, 168, 260, 140, "ДІЇ МЕТА-СИСТЕМИ\n• Зондування компілятора\n• Перевірка заголовків і функцій\n• Пошук бібліотек (pkg-config)\n• Побудова моделі цілей у пам'яті", size=12.5, fill=ACCENT))
    p.append(fitbox(55, 326, 260, 70, "ВИХОДИ\nCMakeCache.txt (кеш опцій)\nГраф цілей і залежностей у RAM", size=12.5, fill=BG, stroke=NEG))
    p.append(fitbox(55, 412, 260, 52, "Рушій: CMake / Meson / GN", size=12, fill=BG, stroke=MUTED, bold=True))

    # Фаза 2: Генерація
    p.append(fitbox(390, 90, 260, 60, "ВХОДИ\nМодель цілей у пам'яті\nШаблони (*.in) · Generator Exprs", size=13, fill=BG))
    p.append(fitbox(390, 168, 260, 140, "ДІЇ ГЕНЕРАТОРА\n• Розгортання виразів $<...>\n• Підстановка в config.h\n• Розрахунок прапорців і шляхів\n• Експорт у плоский низькорівневий граф", size=12.5, fill=ACCENT))
    p.append(fitbox(390, 326, 260, 70, "ВИХОДИ\nbuild.ninja / Makefile\nЗгенеровані файли (config.h)", size=12.5, fill=BG, stroke=FIELD))
    p.append(fitbox(390, 412, 260, 52, "Рушій: Генератор мета-системи", size=12, fill=BG, stroke=MUTED, bold=True))

    # Фаза 3: Виконання збірки
    p.append(fitbox(725, 90, 260, 60, "ВХОДИ\nbuild.ninja / Makefile\nВихідний код (.cpp, .c, .h)", size=13, fill=BG))
    p.append(fitbox(725, 168, 260, 140, "ДІЇ ВИКОНАВЦЯ\n• Топологічний обхід графа\n• Перевірка mtime / гешів\n• Паралельний запуск комманд\n• Компіляція та лінкування", size=12.5, fill=ACCENT))
    p.append(fitbox(725, 326, 260, 70, "ВИХОДИ\nОб'єктні файли (.o)\nБібліотеки та виконувані файли", size=12.5, fill=BG, stroke=POS))
    p.append(fitbox(725, 412, 260, 52, "Рушій: Ninja / Make / MSBuild", size=12, fill=BG, stroke=MUTED, bold=True))

    render(os.path.join(IMG, "fig-phases.svg"), W, H, *p,
           title="Три фази життєвого циклу: конфігурація, генерація і виконання")


# ── 2. In-source проти Out-of-source ────────────────────────────────────────
def fig_in_vs_out():
    W, H = 1040, 540
    p = []

    # Ліва панель: In-Source (катастрофа)
    p.append(rect(40, 40, 450, 460, fill=PANEL, stroke=POS, sw=2, rx=8))
    p.append(text(265, 72, "In-Source збірка (антипатерн)", size=15.5, bold=True, color=POS))
    p.append(text(265, 94, "Джерела змішані з артефактами в одному каталозі", size=12.5, italic=True, color=MUTED))

    p.append(fitbox(60, 115, 410, 180,
                    "Каталог проєкту:  my_project/\n"
                    "├── src/ (main.cpp, util.cpp, util.h)\n"
                    "├── CMakeLists.txt\n"
                    "├── main.o, util.o        ← тимчасові об'єктні файли\n"
                    "├── CMakeCache.txt        ← кеш конфігурації\n"
                    "├── CMakeFiles/           ← проміжне сміття тестів\n"
                    "├── config.h              ← згенерований заголовок\n"
                    "└── app                   ← скомпільований бінарник",
                    size=12.5, fill=DIRTY, stroke=POS))

    p.append(fitbox(60, 310, 410, 170,
                    "НАСЛІДКИ ТА ВАДИ:\n"
                    "✖ git status показує сотні сміттєвих файлів\n"
                    "✖ Неможливо зібрати Debug і Release одночасно\n"
                    "✖ Дерево джерел не можна змонтувати як Read-Only\n"
                    "✖ Очищення небезпечне: make clean може потерти джерела\n"
                    "✖ Перемикання гілок Git призводить до колізій артефактів",
                    size=12.5, fill=BG, stroke=POS))

    # Права панель: Out-of-Source (чистота та ізоляція)
    p.append(rect(550, 40, 450, 460, fill=PANEL, stroke=FIELD, sw=2, rx=8))
    p.append(text(775, 72, "Out-of-Source збірка (канон)", size=15.5, bold=True, color=FIELD))
    p.append(text(775, 94, "Джерела Read-Only, збірки повністю ізольовані", size=12.5, italic=True, color=MUTED))

    p.append(fitbox(570, 115, 410, 110,
                    "ДЕРЕВО ДЖЕРЕЛ (Тільки для читання / Git):\n"
                    "my_project/  (чисте, без жодного артефакту)\n"
                    "├── src/ (main.cpp, util.cpp, util.h)\n"
                    "└── CMakeLists.txt",
                    size=12.5, fill=CLEAN, stroke=FIELD))

    # Три незалежні build директорії
    p.append(fitbox(570, 240, 410, 65,
                    "build-debug/  (Debug + ASan, -O0 -g)\n"
                    "└── CMakeCache.txt, build.ninja, main.o, app",
                    size=12, fill=BG, stroke=MUTED))

    p.append(fitbox(570, 315, 410, 65,
                    "build-release/  (Release + LTO, -O3)\n"
                    "└── CMakeCache.txt, build.ninja, main.o, app",
                    size=12, fill=BG, stroke=MUTED))

    p.append(fitbox(570, 390, 410, 65,
                    "build-arm/  (Крос-збірка під Cortex-M4)\n"
                    "└── CMakeCache.txt, build.ninja, firmware.elf",
                    size=12, fill=BG, stroke=MUTED))

    p.append(fitbox(570, 465, 410, 26, "Очищення: rm -rf build-debug/ — 100% повернення до чистого стану", size=11.5, fill=CLEAN, stroke=FIELD, bold=True))

    render(os.path.join(IMG, "fig-in-vs-out.svg"), W, H, *p,
           title="Порівняння in-source та out-of-source підходів до збірки")


# ── 3. Анатомія Build-директорії ─────────────────────────────────────────────
def fig_build_anatomy():
    W, H = 1040, 560
    p = []

    p.append(rect(40, 30, 960, 500, fill=PANEL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(520, 62, "Анатомія каталогу збірки (Build Directory)", size=16, bold=True))
    p.append(text(520, 84, "Структура файлів і зон відповідальності всередині out-of-tree оточення", size=13, italic=True, color=MUTED))

    # Секція 1: Кеш і параметри
    p.append(fitbox(65, 110, 275, 185,
                    "КЕШ КОНФІГУРАЦІЇ\n\n"
                    "CMakeCache.txt\n"
                    "• Збережені опції користувача\n"
                    "• Виявлені шляхи до компіляторів\n"
                    "• Прапорці трансляції\n"
                    "• Запобігає повторним тестам",
                    size=12.5, fill=BG, stroke=NEG))

    # Секція 2: Логи зондування
    p.append(fitbox(382, 110, 275, 185,
                    "ПРОСТІР ЗОНДУВАННЯ\n\n"
                    "CMakeFiles/\n"
                    "• CMakeConfigureLog.yaml\n"
                    "• CMakeScratch/ (тривалі проби)\n"
                    "• Логи викликів try_compile()\n"
                    "• Виявлені ABI та розміри типів",
                    size=12.5, fill=BG, stroke=MUTED))

    # Секція 3: Згенерований код
    p.append(fitbox(700, 110, 275, 185,
                    "ЗГЕНЕРОВАНІ ДЖЕРЕЛА\n\n"
                    "generated/\n"
                    "• config.h (з config.h.in)\n"
                    "• version.cpp (номер релізу/комміт)\n"
                    "• Protobuf / Flex / Bison генерати\n"
                    "• Підключаються через -I build/gen",
                    size=12.5, fill=BG, stroke=FIELD))

    # Секція 4: Низькорівневий граф
    p.append(fitbox(65, 320, 275, 185,
                    "НИЗЬКОРІВНЕВИЙ ГРАФ\n\n"
                    "build.ninja / Makefile\n"
                    "• Детерміновані правила запуску\n"
                    "• Повні шляхи до файлів та утиліт\n"
                    "• Жодної логіки чи розгалужень\n"
                    "• Вхід для Ninja / Make",
                    size=12.5, fill=BG, stroke=FIELD))

    # Секція 5: База залежностей
    p.append(fitbox(382, 320, 275, 185,
                    "ЖУРНАЛИ АКТУАЛЬНОСТІ\n\n"
                    ".ninja_deps · .ninja_log\n"
                    "• База включень заголовків (depfiles)\n"
                    "• Історія часу виконання команд\n"
                    "• Обчислення застарілих вершин\n"
                    "• Швидкий інкрементальний старт",
                    size=12.5, fill=BG, stroke=MUTED))

    # Секція 6: Об'єктні файли й артефакти
    p.append(fitbox(700, 320, 275, 185,
                    "ОБ'ЄКТНИКИ ТА АРТЕФАКТИ\n\n"
                    "CMakeFiles/app.dir/ & bin/\n"
                    "• main.cpp.o, util.cpp.o\n"
                    "• libcore.a / libcore.so\n"
                    "• Фінальний бінарник bin/app\n"
                    "• Ізоляція між різними цілями",
                    size=12.5, fill=BG, stroke=POS))

    render(os.path.join(IMG, "fig-build-anatomy.svg"), W, H, *p,
           title="Анатомія каталогу збірки: кеш, зондування, граф та артефакти")


# ── 4. Дворівнева трансляція мета-системи ────────────────────────────────────
def fig_meta_translation():
    W, H = 1040, 520
    p = []

    # Верхній блок: Високорівневий граф цілей
    p.append(rect(40, 40, 960, 160, fill=PANEL, stroke=NEG, sw=2, rx=8))
    p.append(text(520, 68, "РІВЕНЬ 1 · Абстрактний граф цілей у мета-системі (CMake / Meson)", size=15, bold=True, color=NEG))

    p.append(fitbox(60, 88, 260, 95, "Ціль: libnet (STATIC)\nВходи: net.cpp, net.h\nВимоги: PUBLIC inc/net\nPRIVATE libssl", size=12.5, fill=BG, stroke=MUTED))
    p.append(fitbox(390, 88, 260, 95, "Ціль: app (EXECUTABLE)\nВходи: main.cpp\nЗалежність: PRIVATE libnet\nПрапорець: $<CONFIG:Debug:-g3>", size=12.5, fill=BG, stroke=MUTED))
    p.append(fitbox(720, 88, 260, 95, "Ціль: OpenSSL (IMPORTED)\nВимоги: INTERFACE /usr/include\nБібліотека: /usr/lib/libssl.so", size=12.5, fill=BG, stroke=MUTED))

    p.append(arrow(322, 135, 388, 135, color=LINE, sw=1.8))
    p.append(arrow(652, 135, 718, 135, color=LINE, sw=1.8))

    # Центральний перехід: Процес генерації
    p.append(rect(340, 220, 360, 50, fill=ACCENT, stroke=FIELD, sw=2, rx=6))
    p.append(text(520, 250, "ФАЗА ГЕНЕРАЦІЇ (розгортання транзитивності й $<...>)", size=13.5, bold=True, color=FIELD))
    p.append(arrow(520, 202, 520, 218, color=FIELD, sw=2))
    p.append(arrow(520, 272, 520, 288, color=FIELD, sw=2))

    # Нижній блок: Плоский DAG у Ninja
    p.append(rect(40, 290, 960, 190, fill=PANEL, stroke=POS, sw=2, rx=8))
    p.append(text(520, 318, "РІВЕНЬ 2 · Плоский низькорівневий граф виконання (build.ninja)", size=15, bold=True, color=POS))

    p.append(fitbox(60, 338, 425, 125,
                    "Команда компіляції:\n"
                    "build CMakeFiles/net.dir/net.cpp.o: CXX_COMPILER ../src/net.cpp\n"
                    "  INCLUDES = -I../src/inc/net -I/usr/include\n"
                    "  FLAGS = -O0 -g3 -fPIC -std=c++20",
                    size=12, fill=BG, stroke=MUTED))

    p.append(fitbox(555, 338, 425, 125,
                    "Команда лінкування:\n"
                    "build bin/app: CXX_EXECUTABLE CMakeFiles/app.dir/main.cpp.o libnet.a\n"
                    "  LINK_FLAGS = -Wl,-rpath,/usr/lib\n"
                    "  LINK_LIBRARIES = libnet.a /usr/lib/libssl.so",
                    size=12, fill=BG, stroke=MUTED))

    p.append(arrow(487, 400, 553, 400, color=LINE, sw=1.8))

    render(os.path.join(IMG, "fig-meta-translation.svg"), W, H, *p,
           title="Трансляція абстрактного графа цілей у плоский низькорівневий граф Ninja")


if __name__ == "__main__":
    fig_phases()
    fig_in_vs_out()
    fig_build_anatomy()
    fig_meta_translation()
    print("All figures generated successfully.")
