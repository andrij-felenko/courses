#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-діаграм для теми «Модель менеджера залежностей C++»."""

import sys
import os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_abi_combinatorial_explosion():
    """Діаграма 1: Багатовимірний простір параметрів збірки C++ та вибух несумісних бінарників."""
    w, h = 920, 520
    frags = []

    # Заголовок зверху
    frags.append(text(460, 28, "Багатовимірний простір бінарної сумісності (ABI) у C++", size=17, bold=True))
    frags.append(text(460, 48, "Один вихідний код C++ породжує тисячі взаємно несумісних бінарних артефактів", size=12, color=MUTED))

    # Ліва частина: Вхідний вихідний код
    src_box, _, _ = textbox(130, 270, "Вихідний код\nбібліотеки\nlibdemo.cpp\nlibdemo.h", size=13, pad=12, fill="#eef2f7", stroke="#4b5563", bold=True)
    frags.append(src_box)

    # 6 параметрів компіляції (осі вибуху)
    dims = [
        ("Компілятор та версія", "GCC 11/12/13/14, Clang 14..18, MSVC 19.x", 110),
        ("Стандарт мови C++", "-std=c++14, c++17, c++20, c++23", 175),
        ("C++ Runtime / Стандартна б-ка", "libstdc++ (old/dual ABI), libc++, MSVC CRT (/MD, /MT, /MDd)", 240),
        ("Тип компонування та PIC", "Static (.a/.lib) vs Shared (.so/.dll), -fPIC / -fPIE", 305),
        ("Конфігурація оптимізації", "Debug, Release, RelWithDebInfo, MinSizeRel, ASan/TSan", 370),
        ("Цільова архітектура й SIMD", "x86_64 (AVX2, AVX512), AArch64, ARMv7 (NEON)", 435),
    ]

    for title_dim, desc_dim, y_pos in dims:
        # Прямокутник виміру
        frags.append(rect(300, y_pos - 22, 320, 44, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=5))
        frags.append(text(312, y_pos - 4, title_dim, size=12, bold=True, color=INK, anchor="start"))
        frags.append(text(312, y_pos + 13, desc_dim, size=10.5, color=MUTED, anchor="start"))
        
        # Стрілка від вихідного коду до параметра
        frags.append(arrow(210, 270, 298, y_pos, color="#64748b", sw=1.2))
        # Стрілка від параметра до матриці бінарників
        frags.append(arrow(622, y_pos, 695, y_pos, color=POS, sw=1.2))

    # Права частина: Вибух пакетів
    frags.append(rect(700, 90, 205, 385, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(802, 118, "Матриця артефактів", size=13, bold=True, color=POS))
    frags.append(text(802, 136, "Комбінаторний вибух", size=11, color=MUTED))

    pkgs = [
        "pkg_gcc13_cxx20_libstdc++_rel",
        "pkg_gcc13_cxx17_libstdc++_dbg",
        "pkg_clang17_cxx20_libc++_rel",
        "pkg_msvc19_cxx20_MD_rel",
        "pkg_msvc19_cxx20_MDd_dbg",
        "pkg_msvc19_cxx20_MT_rel",
        "pkg_arm64_gcc12_cxx17_pic",
        "... (понад 1000 комбінацій)",
    ]

    for idx, p_name in enumerate(pkgs):
        y_pkg = 170 + idx * 36
        is_last = (idx == len(pkgs) - 1)
        fill_c = "#ffffff" if not is_last else "#fee2e2"
        stroke_c = "#cbd5e1" if not is_last else POS
        frags.append(rect(712, y_pkg - 12, 181, 26, fill=fill_c, stroke=stroke_c, sw=1, rx=4))
        frags.append(text(802, y_pkg + 5, p_name, size=9.5, bold=is_last, color=INK if not is_last else POS))

    return render(os.path.join(IMG_DIR, "abi-combinatorial-explosion.svg"), w, h, *frags)


def fig_diamond_dependency_odr():
    """Діаграма 2: Ромбоподібна залежність, порушення ODR та змішування несумісних структур у пам'яті."""
    w, h = 920, 520
    frags = []

    frags.append(text(460, 26, "Ромбоподібний конфлікт залежностей і наслідки порушення ODR", size=17, bold=True))
    frags.append(text(460, 46, "Неможливість одночасного співіснування двох версій однієї бібліотеки в єдиному адресному просторі C++", size=12, color=MUTED))

    # Кореневий застосунок
    app_box, _, _ = textbox(460, 95, "Головний застосунок\nApp (main.cpp)", size=13, pad=10, fill="#e0f2fe", stroke="#0284c7", bold=True)
    frags.append(app_box)

    # Проміжні бібліотеки B і C
    lib_b, _, _ = textbox(250, 205, "Бібліотека LibAudio\n(вимагає Logger v1.2.0)", size=12, pad=10, fill="#f8fafc", stroke="#475569", bold=True)
    lib_c, _, _ = textbox(670, 205, "Бібліотека LibRender\n(вимагає Logger v2.1.0)", size=12, pad=10, fill="#f8fafc", stroke="#475569", bold=True)
    frags.append(lib_b)
    frags.append(lib_c)

    # Стрілки від App до LibAudio та LibRender
    frags.append(arrow(415, 118, 290, 180, color="#0284c7", sw=1.5))
    frags.append(arrow(505, 118, 630, 180, color="#0284c7", sw=1.5))

    # Дві конфліктні версії внизу
    v1_box, _, _ = textbox(250, 325, "Logger v1.2.0\nstruct LogRecord {\n  int level;   // 4 B\n  char msg[64];// 64 B\n}; // Total 68 B", size=11, pad=10, fill="#fef9c3", stroke="#ca8a04")
    v2_box, _, _ = textbox(670, 325, "Logger v2.1.0\nstruct LogRecord {\n  uint64_t ts; // 8 B\n  int level;   // 4 B\n  string msg;  // 32 B\n}; // Total 48 B", size=11, pad=10, fill="#fee2e2", stroke=POS)
    frags.append(v1_box)
    frags.append(v2_box)

    frags.append(arrow(250, 238, 250, 280, color="#ca8a04", sw=1.5))
    frags.append(arrow(670, 238, 670, 280, color=POS, sw=1.5))

    # Центральна зона конфлікту ODR
    frags.append(rect(140, 400, 640, 100, fill="#fff1f2", stroke=POS, sw=1.8, rx=8))
    frags.append(text(460, 424, "КАТАСТРОФА ЛІНКУВАННЯ ТА ВИКОНАННЯ (ODR VIOLATION)", size=13, bold=True, color=POS))
    frags.append(text(460, 448, "• Статичне лінкування: помилка 'duplicate symbol Logger::format(LogRecord*)' або підміна версії", size=11, color=INK))
    frags.append(text(460, 468, "• Динамічне лінкування (ELF Interposition): застосунок виконує один екземпляр класу з хибним зміщенням полів", size=11, color=INK))
    frags.append(text(460, 488, "• Наслідок: непередбачуване пошкодження пам'яті (Memory Corruption) та збій SIGSEGV під час виконання", size=11, color=POS, bold=True))

    frags.append(arrow(250, 372, 340, 400, color=POS, sw=1.5))
    frags.append(arrow(670, 372, 580, 400, color=POS, sw=1.5))

    return render(os.path.join(IMG_DIR, "diamond-dependency-odr.svg"), w, h, *frags)


def fig_source_vs_binary_cache():
    """Діаграма 3: Порівняння Source-based моделі та моделі бінарного кешування з хешуванням Package ID."""
    w, h = 920, 490
    frags = []

    frags.append(text(460, 26, "Моделі постачання: Збірка з вихідного коду проти Бінарного кешу", size=17, bold=True))
    frags.append(text(460, 46, "Гарантія повної сумісності ціною часу збірки проти миттєвого завантаження за детермінованим хешем", size=12, color=MUTED))

    # Ліва колонка: Source-based модель
    frags.append(rect(30, 75, 415, 395, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(237, 102, "Source-Based (vcpkg / FetchContent)", size=14, bold=True, color="#0f172a"))

    src_steps = [
        ("1. Завантаження коду", "Клонування Git-репозиторію або tar.gz архіву", 145),
        ("2. Локальна конфігурація", "Запуск CMake/Autotools/Meson із локальним тулчейном", 215),
        ("3. Повна збірка з сирців", "Компіляція всіх C/C++ файлів на машині розробника", 285),
        ("4. Інсталяція в sysroot", "Копіювання згенерованих .a / .so та заголовків у префікс", 355),
    ]

    for s_title, s_desc, y_s in src_steps:
        frags.append(rect(50, y_s - 20, 375, 52, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
        frags.append(text(65, y_s - 2, s_title, size=12, bold=True, color=INK, anchor="start"))
        frags.append(text(65, y_s + 17, s_desc, size=10.5, color=MUTED, anchor="start"))
        if y_s < 355:
            frags.append(arrow(237, y_s + 32, 237, y_s + 48, color="#64748b", sw=1.2))

    frags.append(text(237, 442, "✓ 100% узгодженість прапорців  |  ✗ Тривалий час компіляції", size=11, bold=True, color=INK))

    # Права колонка: Binary Caching (Conan модель)
    frags.append(rect(475, 75, 415, 395, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(682, 102, "Binary Caching (Conan Package ID)", size=14, bold=True, color=FIELD))

    bin_steps = [
        ("1. Розрахунок Package ID", "Хеш: SHA1(OS + Arch + Compiler + Std + Options + Deps)", 145),
        ("2. Запит до бінарного сховища", "Перевірка наявності артефакту з цим Package ID на сервері", 215),
        ("3. Завантаження готового бінарника", "Миттєве отримання сумісного архіву (Cache Hit)", 285),
        ("4. Fallback: локальна збірка", "Збірка з сирців лише якщо в кеші немає точного збігу", 355),
    ]

    for b_title, b_desc, y_b in bin_steps:
        frags.append(rect(495, y_b - 20, 375, 52, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
        frags.append(text(510, y_b - 2, b_title, size=12, bold=True, color=INK, anchor="start"))
        frags.append(text(510, y_b + 17, b_desc, size=10.5, color=MUTED, anchor="start"))
        if y_b < 355:
            frags.append(arrow(682, y_b + 32, 682, y_b + 48, color=FIELD, sw=1.2))

    frags.append(text(682, 442, "✓ Миттєве завантаження (секунди)  |  ✓ Захист від несумісності", size=11, bold=True, color=FIELD))

    return render(os.path.join(IMG_DIR, "source-vs-binary-cache.svg"), w, h, *frags)


def fig_manager_build_system_bridge():
    """Діаграма 4: Архітектура інтеграції менеджера залежностей із системою збірки через генератори."""
    w, h = 920, 480
    frags = []

    frags.append(text(460, 26, "Архітектурний міст: від маніфесту залежностей до моделі цілей CMake", size=17, bold=True))
    frags.append(text(460, 46, "Як менеджер пакетів транслює розв'язаний граф у нативні структури системи збірки", size=12, color=MUTED))

    # 1. Шар оголошення
    m_box, _, _ = textbox(140, 150, "Маніфест проєкту\nconanfile.py / txt\nvcpkg.json\n[requires] fmt/10.1.1", size=12, pad=10, fill="#f8fafc", stroke="#475569", bold=True)
    frags.append(m_box)

    # 2. Шар розв'язання менеджером
    mgr_box, _, _ = textbox(140, 340, "Менеджер пакетів\n(Conan / vcpkg)\n1. Розв'язання графа\n2. Збірка / Завантаження\n3. Розгортання файлів", size=12, pad=10, fill="#e0f2fe", stroke="#0284c7", bold=True)
    frags.append(mgr_box)

    frags.append(arrow(140, 205, 140, 275, color="#0284c7", sw=1.5))

    # 3. Шар генераторів (міст)
    frags.append(rect(320, 95, 270, 335, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=8))
    frags.append(text(455, 122, "ГЕНЕРАТОРИ (GENERATORS)", size=13, bold=True, color="#854d0e"))

    gen_items = [
        ("CMakeDeps / CMakeToolchain", "Створює fmt-config.cmake,\nconan_toolchain.cmake", 180),
        ("PkgConfigDeps", "Створює fmt.pc для\nсистем без CMake", 265),
        ("CMake Imported Targets", "Експортує ціль\nfmt::fmt з властивостями", 350),
    ]

    for g_title, g_desc, y_g in gen_items:
        frags.append(rect(335, y_g - 22, 240, 60, fill="#ffffff", stroke="#fde047", sw=1.2, rx=5))
        frags.append(text(455, y_g - 4, g_title, size=11.5, bold=True, color=INK))
        frags.append(mtext(455, y_g + 14, g_desc, size=10, color=MUTED))

    frags.append(arrow(240, 340, 318, 340, color="#ca8a04", sw=1.5))

    # 4. Шар споживання у системі збірки
    frags.append(rect(640, 95, 250, 335, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(765, 122, "СИСТЕМА ЗБІРКИ (CMake)", size=13, bold=True, color=FIELD))

    cmake_code = (
        "find_package(fmt CONFIG REQUIRED)\n\n"
        "add_executable(my_app main.cpp)\n\n"
        "target_link_libraries(my_app\n"
        "  PRIVATE\n"
        "    fmt::fmt\n"
        ")"
    )
    frags.append(rect(655, 160, 220, 160, fill="#ffffff", stroke="#bbf7d0", sw=1.2, rx=5))
    frags.append(mtext(668, 185, cmake_code, size=11, color=INK, anchor="start"))

    frags.append(text(765, 355, "Автоматичне прокидання:", size=11, bold=True, color=INK))
    frags.append(text(765, 375, "• -I/path/to/fmt/include", size=10.5, color=MUTED))
    frags.append(text(765, 395, "• -L/path/to/fmt/lib -lfmt", size=10.5, color=MUTED))
    frags.append(text(765, 415, "• Потрібні прапорці компілятора", size=10.5, color=MUTED))

    frags.append(arrow(590, 240, 638, 240, color=FIELD, sw=1.5))

    return render(os.path.join(IMG_DIR, "manager-build-system-bridge.svg"), w, h, *frags)


if __name__ == "__main__":
    print("Генерація діаграм для dependency-manager-model...")
    fig_abi_combinatorial_explosion()
    fig_diamond_dependency_odr()
    fig_source_vs_binary_cache()
    fig_manager_build_system_bridge()
    print("Готово!")
