# -*- coding: utf-8 -*-
"""Фігури до теми «vcpkg: порти, тріплети, маніфестний режим»."""
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


# ── 1. Архітектурний конвеєр vcpkg ──────────────────────────────────────────
def fig_architecture_flow():
    W, H = 1040, 500
    frags = []

    frags.append(text(520, 26, "Архітектурний конвеєр vcpkg у маніфестному режимі", size=16, bold=True))
    frags.append(text(520, 46, "Від декларативного маніфесту та тріплета до готового дерева інсталяції", size=12, color=MUTED))

    # Колонка 1 (x=160) — Конфігурація проєкту (3 блоки)
    inputs = [
        ("vcpkg.json", "Маніфест: прямі залежності й features", 95, ACCENT_FILL, NEG),
        ("vcpkg-configuration.json", "Реєстри, baselines та оверлеї", 190, ACCENT_FILL, NEG),
        ("Тріплет (напр. x64-windows)", "Цільова ОС, CRT (/MD чи /MT), linkage", 285, ACCENT_FILL, NEG),
    ]

    for title_txt, desc_txt, y, fill_c, strk_c in inputs:
        body, _, _ = textbox(160, y, [title_txt, desc_txt], size=10.5, fill=fill_c, stroke=strk_c, min_w=260)
        frags.append(body)

    # Стрілки від входів до рушія розв'язання
    frags.append(arrow(290, 95, 335, 160))
    frags.append(arrow(290, 190, 335, 190))
    frags.append(arrow(290, 285, 335, 220))

    # Колонка 2 (x=430) — Обчислення та перевірка графа
    body, _, _ = textbox(430, 190, [
        "Рушій залежностей",
        "1. Граф за схемою MVS",
        "2. Розрахунок ABI Hash",
        "3. Перевірка кешу",
    ], size=11, fill=GOLD_FILL, stroke=LINE, min_w=190)
    frags.append(body)

    # Стрілки розгалуження: Hit (вгору) та Miss (вниз)
    frags.append(arrow(525, 155, 605, 105))
    frags.append(text(560, 118, "Cache Hit", size=10, color=FIELD, bold=True))

    frags.append(arrow(525, 225, 605, 275))
    frags.append(text(560, 265, "Cache Miss", size=10, color=POS, bold=True))

    # Колонка 3 (x=725) — Binary Cache або Build from source
    body, _, _ = textbox(725, 105, [
        "Бінарний кеш (Binary Cache)",
        "Вилучення готового архіву",
        "(локальний диск, HTTP, NuGet, GHA)",
    ], size=10.5, fill=OK_FILL, stroke=FIELD, min_w=240)
    frags.append(body)

    body, _, _ = textbox(725, 275, [
        "Збірка з сирців (Portfile)",
        "1. Завантаження + SHA-512",
        "2. Застосування .patch латок",
        "3. vcpkg_cmake_configure / install",
    ], size=10.5, fill=WARN_FILL, stroke=POS, min_w=240)
    frags.append(body)

    # Колонка 4 (x=940) — Уніфікація пакета
    body, _, _ = textbox(940, 190, [
        "Пакетний буфер",
        "packages/<port>/",
        "Нормалізація CMake",
        "Очищення дублікатів",
    ], size=10.5, fill=FILL, stroke=LINE, min_w=150)
    frags.append(body)

    frags.append(arrow(845, 105, 890, 160))
    frags.append(arrow(845, 275, 890, 220))

    # Стрілка від буфера вниз до фінального дерева інсталяції
    frags.append(arrow(940, 245, 940, 360))

    # Нижня частина (x=520, y=420) — Фінальне дерево інсталяції
    body, _, _ = textbox(520, 420, [
        "Дерево інсталяції: build/vcpkg_installed/<triplet>/",
        "Структура: include/  |  lib/  |  bin/  |  share/<port>/  |  debug/lib/  |  debug/bin/",
        "Інтеграція: CMAKE_TOOLCHAIN_FILE автоматично встановлює CMAKE_PREFIX_PATH",
        "Споживач у CMakeLists.txt: find_package(fmt CONFIG REQUIRED) -> target_link_libraries(app PRIVATE fmt::fmt)",
    ], size=11, fill=FILL, stroke=MUTED, min_w=980)
    frags.append(body)

    render(os.path.join(IMG, "vcpkg-architecture-flow.svg"), W, H, *frags)


# ── 2. Життєвий цикл виконання portfile.cmake ───────────────────────────────
def fig_portfile_phases():
    W, H = 1040, 540
    frags = []

    frags.append(text(520, 26, "Анатомія та послідовність фаз portfile.cmake", size=16, bold=True))
    frags.append(text(520, 46, "Покроковий конвеєр збірки порту та нормалізації структури встановлення", size=12, color=MUTED))

    # Верхній рядок: Фази 1 - 3
    top_steps = [
        ("1. Отримання коду", "vcpkg_from_github / git / url", "Перевірка SHA-512 хешу", 160, 115, ACCENT_FILL, NEG),
        ("2. Патчування", "vcpkg_apply_patches", "Виправлення CMake та крос-платформ", 520, 115, ACCENT_FILL, NEG),
        ("3. Конфігурація", "vcpkg_cmake_configure", "Генерація через Ninja / Triplet flags", 880, 115, ACCENT_FILL, NEG),
    ]

    for title_txt, fn_txt, sub_txt, cx, cy, fill_c, strk_c in top_steps:
        body, _, _ = textbox(cx, cy, [title_txt, fn_txt, sub_txt], size=11, fill=fill_c, stroke=strk_c, min_w=270)
        frags.append(body)

    frags.append(arrow(295, 115, 385, 115))
    frags.append(arrow(655, 115, 745, 115))
    frags.append(arrow(880, 155, 880, 215))

    # Нижній рядок: Фази 4 - 6 (справа наліво)
    bottom_steps = [
        ("4. Збірка й монтаж", "vcpkg_cmake_install", "Інсталяція Release + Debug у packages/", 880, 275, ACCENT_FILL, NEG),
        ("5. Нормалізація", "vcpkg_cmake_config_fixup", "Перенесення share/, очищення debug/include", 520, 275, GOLD_FILL, LINE),
        ("6. Фіналізація", "vcpkg_install_copyright", "Копіювання ліцензії, PDB та pkgconfig", 160, 275, OK_FILL, FIELD),
    ]

    for title_txt, fn_txt, sub_txt, cx, cy, fill_c, strk_c in bottom_steps:
        body, _, _ = textbox(cx, cy, [title_txt, fn_txt, sub_txt], size=11, fill=fill_c, stroke=strk_c, min_w=270)
        frags.append(body)

    frags.append(arrow(745, 275, 655, 275))
    frags.append(arrow(385, 275, 295, 275))

    # Нижній підсумковий блок — Результат у packages/<port>_<triplet>/
    body, _, _ = textbox(520, 440, [
        "Результат виконання portfile: ізольований каталог packages/<port>_<triplet>/",
        "• share/<port>/*Config.cmake  ->  гарантія роботи find_package(<port> CONFIG)",
        "• include/                    ->  заголовкові файли (однакові для Release і Debug)",
        "• lib/ та debug/lib/          ->  бібліотеки .lib / .a без змішування конфігурацій",
        "• bin/ та debug/bin/          ->  виконувані файли та DLL для Windows (з супутніми PDB)",
    ], size=11, fill=FILL, stroke=MUTED, min_w=950)
    frags.append(body)

    frags.append(arrow(160, 315, 160, 380))

    render(os.path.join(IMG, "vcpkg-portfile-phases.svg"), W, H, *frags)


# ── 3. Структура тріплетів і Target vs Host ──────────────────────────────────
def fig_triplet_matrix():
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 26, "Анатомія тріплета та поділ на Target і Host", size=16, bold=True))
    frags.append(text(500, 46, "Керування платформою, зв'язуванням CRT і генераторами коду при крос-компіляції", size=12, color=MUTED))

    # Лівий блок — Target Triplet (Цільова система)
    body, _, _ = textbox(280, 185, [
        "Target Triplet (наприклад, arm64-android)",
        "",
        "VCPKG_TARGET_ARCHITECTURE = arm64",
        "VCPKG_CMAKE_SYSTEM_NAME = Android",
        "VCPKG_CRT_LINKAGE = dynamic",
        "VCPKG_LIBRARY_LINKAGE = static",
        "VCPKG_CHAINLOAD_TOOLCHAIN_FILE = ndk.toolchain.cmake",
        "",
        "Призначення: компіляція бібліотек для запуску",
        "на цільовому пристрої (смартфон, SBC, сервер)",
    ], size=10.5, fill=ACCENT_FILL, stroke=NEG, min_w=430)
    frags.append(body)

    # Правий блок — Host Triplet (Машина збірки)
    body, _, _ = textbox(720, 185, [
        "Host Triplet (наприклад, x64-linux / x64-windows)",
        "",
        "VCPKG_TARGET_ARCHITECTURE = x64",
        "VCPKG_CMAKE_SYSTEM_NAME = Linux (нативна)",
        "VCPKG_CRT_LINKAGE = dynamic",
        "VCPKG_LIBRARY_LINKAGE = dynamic",
        "",
        "Призначення: компіляція інструментів генерації коду,",
        "які запускаються ПІД ЧАС ЗБІРКИ (protoc, flatc, flex)",
    ], size=10.5, fill=GOLD_FILL, stroke=LINE, min_w=430)
    frags.append(body)

    # Центральна зв'язка — vcpkg.json host dependency
    body, _, _ = textbox(500, 345, [
        "Оголошення залежності в маніфесті vcpkg.json:",
        '{"name": "protobuf", "host": true}  ->  збирається через Host Triplet (генератор protoc)',
        '{"name": "protobuf"}                ->  збирається через Target Triplet (бібліотека libprotobuf.a)',
    ], size=11, fill=OK_FILL, stroke=FIELD, min_w=870)
    frags.append(body)

    # Стрілки від тріплетів до декларації в vcpkg.json
    frags.append(arrow(280, 275, 380, 315))
    frags.append(arrow(720, 275, 620, 315))

    # Нижній блок — Оверлей тріплети
    body, _, _ = textbox(500, 455, [
        "Overlay Triplets (власні тріплети проєкту):",
        "Додаються прапорцем --overlay-triplets=custom-triplets/ або через vcpkg-configuration.json",
        "Дозволяють задавати специфічні прапорці компілятора (VCPKG_CXX_FLAGS) та кастомні крос-тулчейни",
    ], size=10.5, fill=FILL, stroke=MUTED, min_w=870)
    frags.append(body)

    render(os.path.join(IMG, "vcpkg-triplet-matrix.svg"), W, H, *frags)


# ── 4. Модель версіонування та MVS ──────────────────────────────────────────
def fig_version_resolution():
    W, H = 1000, 500
    frags = []

    frags.append(text(500, 26, "Модель версіонування та алгоритм Minimal Version Selection (MVS)", size=16, bold=True))
    frags.append(text(500, 46, "Як vcpkg детерміновано обирає версії за допомогою baselines, version>= та overrides", size=12, color=MUTED))

    # Блок 1 — Baseline (Базовий зріз)
    body, _, _ = textbox(200, 140, [
        "1. builtin-baseline",
        "(Git commit хеш репо vcpkg)",
        "",
        "Встановлює початковий зріз:",
        "fmt: 9.1.0",
        "openssl: 3.0.8",
        "zlib: 1.2.13",
    ], size=10.5, fill=ACCENT_FILL, stroke=NEG, min_w=270)
    frags.append(body)

    # Блок 2 — Запити версій через version>=
    body, _, _ = textbox(500, 140, [
        "2. Обмеження: version>=",
        "(запити в vcpkg.json)",
        "",
        "Пакет A просить: fmt >= 9.1.0",
        "Пакет B просить: fmt >= 10.0.0",
        "Базовий зріз дає: fmt = 9.1.0",
        "High-Water Mark обирає: 10.0.0",
    ], size=10.5, fill=GOLD_FILL, stroke=LINE, min_w=270)
    frags.append(body)

    # Блок 3 — Примусове перевизначення (Overrides)
    body, _, _ = textbox(800, 140, [
        "3. Блок overrides",
        "(найвищий пріоритет)",
        "",
        '"overrides": [',
        '  {"name": "fmt", "version": "10.1.1"}',
        "]",
        "Фіксує fmt рівно на 10.1.1",
    ], size=10.5, fill=WARN_FILL, stroke=POS, min_w=270)
    frags.append(body)

    # Стрілки між етапами
    frags.append(arrow(335, 140, 365, 140))
    frags.append(arrow(635, 140, 665, 140))

    # Стрілка вниз до фінального рішення
    frags.append(arrow(500, 210, 500, 280))

    # Фінальний блок розв'язання
    body, _, _ = textbox(500, 365, [
        "Фінальний вибір версій для побудови графа залежностей:",
        "1. Якщо пакет є в секції 'overrides' -> береться ТОЧНА версія з override (ігноруючи baseline та version>=)",
        "2. Інакше -> береться максимум із (версія в baseline, максимальна з усіх version>= транзитивних вимог)",
        "3. Відсутність спонтанних оновлень (Sat-solver не шукає останню версію в інтернеті) -> 100% повторюваність",
    ], size=11, fill=OK_FILL, stroke=FIELD, min_w=910)
    frags.append(body)

    render(os.path.join(IMG, "vcpkg-version-resolution.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_architecture_flow()
    fig_portfile_phases()
    fig_triplet_matrix()
    fig_version_resolution()
    print("Всі фігури vcpkg згенеровано успішно.")
