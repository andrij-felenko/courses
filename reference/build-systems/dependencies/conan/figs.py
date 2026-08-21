# -*- coding: utf-8 -*-
"""Фігури до теми «Conan: рецепти, профілі, бінарні пакети»."""
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
GOLD_FILL = "#fef9e7"


# ── 1. Обчислення package_id ────────────────────────────────────────────────
def fig_package_id_hash():
    W, H = 1000, 500
    frags = []

    frags.append(text(500, 28, "Обчислення package_id у Conan 2.x", size=16, bold=True))
    frags.append(text(500, 48, "Детермінований відбиток бінарної сумісності артефакту", size=12, color=MUTED))

    # Ліва колонка — 4 складові входу
    inputs = [
        ("1. Налаштування (settings)", "os, arch, compiler, compiler.version, build_type", 95),
        ("2. Опції рецепта (options)", "shared=False, fPIC=True, with_ssl=True", 175),
        ("3. Хеші залежностей (requires)", "package_id(zlib), package_id(openssl) [minor_mode]", 255),
        ("4. Ревізія рецепта (RREV)", "хеш файлів рецепта та джерел (якщо recipe_revision_mode)", 335),
    ]

    for title_txt, desc_txt, y in inputs:
        body, _, _ = textbox(240, y, [title_txt, desc_txt], size=11.5, fill=ACCENT_FILL, stroke=NEG, min_w=380)
        frags.append(body)

    # Прямі стрілки від кожної плашки входу до центрального блоку хешування
    frags.append(arrow(435, 95, 485, 185))
    frags.append(arrow(435, 175, 485, 205))
    frags.append(arrow(435, 255, 485, 225))
    frags.append(arrow(435, 335, 485, 245))

    # Центральний блок — Хешування
    body, _, _ = textbox(595, 215, [
        "Хешування (SHA-1)",
        "Нормалізація ключів та значень",
        "Фільтрація за package_id_mode",
        "Обчислення 40-символьного хешу",
    ], size=11.5, fill=GOLD_FILL, stroke=LINE, min_w=210)
    frags.append(body)

    # Стрілка праворуч до результату
    frags.append(arrow(705, 215, 755, 215))

    # Правий блок — package_id та кеш
    body, _, _ = textbox(865, 215, [
        "package_id (Хеш)",
        "da39a3ee5e6b4b0d3255...",
        "",
        "Шлях у кеші пакета:",
        "~/.conan2/p/pkg123/p/",
    ], size=11.5, fill=OK_FILL, stroke=FIELD, min_w=190)
    frags.append(body)

    # Нижня плашка — виняток header-only
    body, _, _ = textbox(500, 440, [
        "Особливий випадок (header-only бібліотеки):",
        "У методі package_id() викликається self.info.clear() — хеш стає однаковим для всіх платформ та компіляторів",
    ], size=11, fill=FILL, stroke=MUTED, min_w=910)
    frags.append(body)

    render(os.path.join(IMG, "package-id-hash.svg"), W, H, *frags)


# ── 2. Життєвий цикл conanfile.py ───────────────────────────────────────────
def fig_recipe_lifecycle():
    W, H = 1040, 550
    frags = []

    frags.append(text(520, 26, "Життєвий цикл методів conanfile.py", size=16, bold=True))
    frags.append(text(520, 46, "Послідовність виконання методів рецепта під час збірки пакета", size=12, color=MUTED))

    # Перший ряд (кроки 1-4)
    top_steps = [
        ("1. config_options() / configure()", "Зміна або валідація налаштувань та опцій", 140, 105, ACCENT_FILL, NEG),
        ("2. layout()", "Оголошення шляхів source/build/package folder", 390, 105, ACCENT_FILL, NEG),
        ("3. requirements()", "Оголошення графа залежностей (host та build)", 640, 105, ACCENT_FILL, NEG),
        ("4. source()", "Завантаження вихідного коду (git, tar.gz)", 890, 105, GOLD_FILL, LINE),
    ]

    for title_txt, desc_txt, cx, cy, fill_c, strk_c in top_steps:
        body, _, _ = textbox(cx, cy, [title_txt, desc_txt], size=10.5, fill=fill_c, stroke=strk_c, min_w=225)
        frags.append(body)

    frags.append(arrow(255, 105, 275, 105))
    frags.append(arrow(505, 105, 525, 105))
    frags.append(arrow(755, 105, 775, 105))
    frags.append(arrow(890, 140, 890, 185))

    # Другий ряд (кроки 5-8 у зворотному напрямку праворуч наліво)
    bot_steps = [
        ("8. package_info()", "Опис контракту (cpp_info.libs, defines)", 140, 220, OK_FILL, FIELD),
        ("7. package()", "Копіювання артефактів у package_folder", 390, 220, OK_FILL, FIELD),
        ("6. build()", "Виклик системи збірки (cmake.configure/build)", 640, 220, GOLD_FILL, LINE),
        ("5. generate()", "Генерація CMakeToolchain, CMakeDeps", 890, 220, GOLD_FILL, LINE),
    ]

    for title_txt, desc_txt, cx, cy, fill_c, strk_c in bot_steps:
        body, _, _ = textbox(cx, cy, [title_txt, desc_txt], size=10.5, fill=fill_c, stroke=strk_c, min_w=225)
        frags.append(body)

    frags.append(arrow(775, 220, 755, 220))
    frags.append(arrow(525, 220, 505, 220))
    frags.append(arrow(275, 220, 255, 220))

    # Нижня частина: простори та каталоги
    frags.append(rect(25, 300, 990, 225, fill=FILL, stroke=LINE, sw=1))
    frags.append(text(520, 325, "Фізичний поділ папок у локальному кеші Conan (~/.conan2/p/)", size=13, bold=True))

    folders = [
        ("source_folder (s)", "Незмінний вихідний код", 145, 395, GOLD_FILL),
        ("build_folder (b)", "Тимчасові об'єктні файли", 395, 395, ACCENT_FILL),
        ("package_folder (p)", "Зібраний пакет (include, lib, bin)", 645, 395, OK_FILL),
        ("generators_folder", "Файли *Config.cmake, toolchain", 895, 395, ACCENT_FILL),
    ]

    for f_title, f_desc, cx, cy, fill_c in folders:
        body, _, _ = textbox(cx, cy, [f_title, f_desc], size=10.5, fill=fill_c, stroke=LINE, min_w=220)
        frags.append(body)

    frags.append(text(520, 490, "Завдяки layout() розробник може працювати як у локальній папці (editable mode), так і в кеші Conan", size=11, color=MUTED))

    render(os.path.join(IMG, "recipe-lifecycle.svg"), W, H, *frags)


# ── 3. Двопрофільна модель крос-компіляції ──────────────────────────────────
def fig_cross_compilation_profiles():
    W, H = 1040, 530
    frags = []

    frags.append(text(520, 28, "Двопрофільна модель Conan 2.x (--profile:build та --profile:host)", size=16, bold=True))
    frags.append(text(520, 48, "Розділення інструментів збірки та цільових бібліотек під час крос-компіляції", size=12, color=MUTED))

    # Ліва колонка — Контекст збірки (Build Context)
    frags.append(rect(30, 75, 450, 350, fill=ACCENT_FILL, stroke=NEG, sw=1.5))
    frags.append(text(255, 102, "Контекст збірки (Build Context)", size=13.5, bold=True, color=NEG))
    frags.append(text(255, 122, "Параметр: --profile:build (Машина розробника / CI)", size=11, color=MUTED))

    b_items = [
        ("Налаштування:", "os=Linux, arch=x86_64, compiler=gcc-13", 160),
        ("Призначення:", "Виконується прямо зараз на машині збірки", 215),
        ("Пакетні сутності:", "tool_requires (інструменти кодогенерації)", 270),
        ("Приклади пакетів:", "protobuf/protoc, cmake, ninja, nasm, gtest runner", 325),
    ]
    for k, v, cy in b_items:
        body, _, _ = textbox(255, cy, [k, v], size=10.5, fill=BG, stroke=LINE, min_w=410)
        frags.append(body)

    # Права колонка — Цільовий контекст (Host Context)
    frags.append(rect(560, 75, 450, 350, fill=OK_FILL, stroke=FIELD, sw=1.5))
    frags.append(text(785, 102, "Цільовий контекст (Host Context)", size=13.5, bold=True, color=FIELD))
    frags.append(text(785, 122, "Параметр: --profile:host (Цільова плата / Архітектура)", size=11, color=MUTED))

    h_items = [
        ("Налаштування:", "os=Linux, arch=armv8, compiler=aarch64-linux-gnu-gcc", 160),
        ("Призначення:", "Виконуватиметься на кінцевому цільовому пристрої", 215),
        ("Пакетні сутності:", "requires (бібліотеки, що лінкуються в бінарник)", 270),
        ("Приклади пакетів:", "zlib, openssl, protobuf runtime, fmt, boost", 325),
    ]
    for k, v, cy in h_items:
        body, _, _ = textbox(785, cy, [k, v], size=10.5, fill=BG, stroke=LINE, min_w=410)
        frags.append(body)

    # Центральний місток
    frags.append(arrow(485, 245, 555, 245))
    frags.append(text(520, 235, "protoc", size=11, bold=True, color=NEG))
    frags.append(text(520, 260, "код .pb.cc", size=10, color=MUTED))

    # Нижній висновок
    body, _, _ = textbox(520, 475, [
        "Команда збірки: conan install . --profile:build=default --profile:host=armv8_linux --build=missing",
        "Conan 2.x автоматично запускає x86_64 інструменти для генерації коду, а бібліотеки лінкує під ARMv8",
    ], size=11.5, fill=GOLD_FILL, stroke=LINE, min_w=980)
    frags.append(body)

    render(os.path.join(IMG, "cross-compilation-profiles.svg"), W, H, *frags)


# ── 4. Інтеграція з CMake через генератори ──────────────────────────────────
def fig_cmake_deps_toolchain():
    W, H = 1040, 530
    frags = []

    frags.append(text(520, 28, "Інтеграція Conan 2.x з CMake через CMakeToolchain та CMakeDeps", size=16, bold=True))
    frags.append(text(520, 48, "Розділення обов'язків: Conan готує оточення, CMake виконує збірку", size=12, color=MUTED))

    # Ліва колонка — Conan
    body, _, _ = textbox(200, 135, [
        "conanfile.py / conanfile.txt",
        "[requires] fmt/10.2.1, zlib/1.3.1",
        "[generators] CMakeToolchain, CMakeDeps",
    ], size=11, fill=ACCENT_FILL, stroke=NEG, min_w=330)
    frags.append(body)

    frags.append(arrow(200, 185, 200, 235))
    frags.append(text(215, 210, "conan install", size=10.5, bold=True))

    body, _, _ = textbox(200, 330, [
        "Згенеровані файли (build/generators/):",
        "1. conan_toolchain.cmake (налаштування CXX)",
        "2. fmt-config.cmake, fmtTargets.cmake",
        "3. ZLIBConfig.cmake, ZLIBTargets.cmake",
        "4. CMakePresets.json / CMakeUserPresets.json",
    ], size=10.5, fill=GOLD_FILL, stroke=LINE, min_w=330)
    frags.append(body)

    # Центральні стрілки передачі
    frags.append(arrow(370, 295, 485, 185))
    frags.append(arrow(370, 345, 485, 345))

    # Права колонка — CMakeLists.txt та збірка
    body, _, _ = textbox(740, 185, [
        "Чистий CMakeLists.txt (без прив'язки до Conan):",
        "find_package(fmt CONFIG REQUIRED)",
        "find_package(ZLIB REQUIRED)",
        "add_executable(my_app main.cpp)",
        "target_link_libraries(my_app PRIVATE fmt::fmt ZLIB::ZLIB)",
    ], size=11, fill=OK_FILL, stroke=FIELD, min_w=470)
    frags.append(body)

    body, _, _ = textbox(740, 345, [
        "Команда збірки проекту:",
        "cmake --preset conan-release",
        "cmake --build --preset conan-release",
    ], size=11.5, fill=ACCENT_FILL, stroke=NEG, min_w=470)
    frags.append(body)

    # Нижня інформаційна плашка
    body, _, _ = textbox(520, 475, [
        "Головний принцип Conan 2.x: Ніякого макрокоду Conan всередині CMakeLists.txt.",
        "Бібліотеки підключаються стандартними імпортованими цілями CMake (Target-based Modern CMake).",
    ], size=11.5, fill=FILL, stroke=MUTED, min_w=980)
    frags.append(body)

    render(os.path.join(IMG, "cmake-deps-toolchain.svg"), W, H, *frags)


# ── 5. Lock-файли та детермінізм графа ───────────────────────────────────────
def fig_lockfile_reproducibility():
    W, H = 1020, 520
    frags = []

    frags.append(text(510, 28, "Фіксація графа залежностей через conan.lock", size=16, bold=True))
    frags.append(text(510, 48, "Захист від неконтрольованого дрейфу версій у розподілених командах та CI/CD", size=12, color=MUTED))

    # Лівий блок — Декларація з діапазонами
    body, _, _ = textbox(200, 145, [
        "Декларативні залежності:",
        "zlib/[>=1.2.11 <2.0]",
        "openssl/[>=3.0 <4.0]",
        "fmt/[~10.2]",
    ], size=11.5, fill=WARN_FILL, stroke=POS, min_w=280)
    frags.append(body)

    frags.append(arrow(345, 145, 415, 145))
    frags.append(text(380, 130, "conan lock create", size=10, bold=True))

    # Центральний блок — conan.lock
    body, _, _ = textbox(620, 145, [
        "Файл замка (conan.lock):",
        "• zlib/1.3.1#rrev_a1b2 -> pkg_id_634#prev_1",
        "• openssl/3.2.0#rrev_c3d4 -> pkg_id_89f#prev_2",
        "• fmt/10.2.1#rrev_e5f6 -> pkg_id_12a#prev_1",
        "• Зафіксовані профілі (settings, options)",
    ], size=10.5, fill=GOLD_FILL, stroke=LINE, min_w=370)
    frags.append(body)

    # Стрілки до двох споживачів
    frags.append(arrow(520, 215, 310, 295))
    frags.append(arrow(720, 215, 760, 295))

    # Розробник
    body, _, _ = textbox(280, 365, [
        "Робоча станція розробника:",
        "conan install . --lockfile=conan.lock",
        "Гарантовано отримує ті самі",
        "ревізії та хеші пакетів",
    ], size=11, fill=OK_FILL, stroke=FIELD, min_w=360)
    frags.append(body)

    # CI/CD сервер
    body, _, _ = textbox(760, 365, [
        "Сервер збірки (CI/CD Pipeline):",
        "conan install . --lockfile=conan.lock",
        "Збірка на 100% повторювана,",
        "не залежить від нових релізів у ConanCenter",
    ], size=11, fill=OK_FILL, stroke=FIELD, min_w=360)
    frags.append(body)

    # Нижній висновок
    body, _, _ = textbox(510, 470, [
        "conan.lock зберігається в системі контролю версій (git) разом із вихідним кодом проєкту",
    ], size=11.5, fill=FILL, stroke=MUTED, min_w=960)
    frags.append(body)

    render(os.path.join(IMG, "lockfile-reproducibility.svg"), W, H, *frags)


def main():
    fig_package_id_hash()
    fig_recipe_lifecycle()
    fig_cross_compilation_profiles()
    fig_cmake_deps_toolchain()
    fig_lockfile_reproducibility()
    print("Всі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
