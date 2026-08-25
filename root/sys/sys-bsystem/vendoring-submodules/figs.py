# -*- coding: utf-8 -*-
"""Фігури до теми «Вендоринг і git-сабмодулі»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL = "#eaf5ec"
BLUE_FILL = "#eaf0fd"


# ── 1. Порівняння моделей підключення коду ──────────────────────────────────
def fig_vendoring_models_comparison():
    W, H = 1100, 560
    frags = []

    frags.append(text(550, 48, "Чотири архітектурні моделі отримання та зберігання залежностей", size=16, bold=True))

    models = [
        ("1. Direct Vendoring", "third_party/ або vendor/",
         "• Фізичні файли в основному репо\n• 100% герметичність збірки\n• Працює без мережі й тулзів\n• Роздуває репозиторій Git\n• Втрата історії комітів апстріму", OK_FILL, FIELD),
        ("2. Git Submodules", ".gitmodules + gitlink",
         "• Вкладені незалежні репозиторії\n• Прив'язка до конкретного SHA\n• Чиста історія головного проєкту\n• Пастки detached HEAD та розсинхрону\n• Потребує --recurse-submodules", BLUE_FILL, NEG),
        ("3. Git Subtree", "git subtree add/pull",
         "• Злиття зовнішнього дерева в папку\n• Збереження історії комітів\n• Клонування в один звичайний крок\n• Важчий журнал та граф комітів\n• Складніший зворотний експорт", FILL, LINE),
        ("4. Package Managers", "Conan / vcpkg / FetchContent",
         "• Декларативний маніфест\n• Кешування пребілд-бінарників\n• Автоматичний солвер версій\n• Залежність від зовнішніх серверів\n• Необхідність мережі або проксі", WARN_FILL, POS),
    ]

    x = 35
    for i, (m_title, m_sub, m_desc, fl, st_col) in enumerate(models):
        frags.append(fitbox(x, 80, 245, 370,
                            m_title + "\n" + m_sub + "\n\n" + m_desc,
                            size=12.5, fill=fl, stroke=st_col))
        x += 265

    frags.append(fitbox(35, 475, 1030, 60,
                        "Вендоринг та сабмодулі переносять контроль над кодом у власне сховище,\n"
                        "гарантуючи автономність і відтворюваність збірки без сторонніх менеджерів пакетів.", size=13.5))

    render(os.path.join(IMG, "vendoring-models-comparison.svg"), W, H, *frags,
           title="Порівняння моделей підключення зовнішніх залежностей")


# ── 2. Внутрішня будова Git Submodule ───────────────────────────────────────
def fig_gitlink_submodule_internals():
    W, H = 1100, 560
    frags = []

    frags.append(text(550, 45, "Внутрішня структура підмодуля: gitlink, .gitmodules та сховище .git/modules", size=16, bold=True))

    # Ліва колонка: Індекс та дерево Git
    frags.append(fitbox(50, 75, 470, 370,
                        "Головний репозиторій (Parent Repository)\n\n"
                        "1. Файл конфігурації .gitmodules:\n"
                        "   [submodule \"third_party/fmt\"]\n"
                        "       path = third_party/fmt\n"
                        "       url = https://github.com/fmtlib/fmt.git\n\n"
                        "2. Запис в об'єкті Tree / Index (git ls-tree HEAD):\n"
                        "   160000 commit e69e6047321527025816...\tthird_party/fmt\n\n"
                        "3. Робочий каталог third_party/fmt/.git:\n"
                        "   gitdir: ../../.git/modules/third_party/fmt",
                        size=12.5, fill=OK_FILL, stroke=FIELD))

    frags.append(arrow(530, 260, 580, 260))

    # Права колонка: База об'єктів
    frags.append(fitbox(590, 75, 460, 370,
                        "Сховище об'єктів підмодуля (.git/modules/)\n\n"
                        "Каталог .git/modules/third_party/fmt/:\n"
                        "• config (локальні налаштування підмодуля)\n"
                        "• HEAD (вказує на зафіксований SHA коміту)\n"
                        "• objects/ (справжня база blob, tree, commit)\n"
                        "• refs/heads/ (локальні гілки підмодуля)\n\n"
                        "⚠️ Стан detached HEAD:\n"
                        "Робочий каталог підмодуля виставлений на точний SHA,\n"
                        "а не на рухому гілку. Зміни без branch губляться!",
                        size=12.5, fill=BLUE_FILL, stroke=NEG))

    frags.append(fitbox(50, 470, 1000, 60,
                        "Підмодуль у дереві Git — це спеціальний 20-байтний покажчик (mode 160000 gitlink) на SHA коміту,\n"
                        "а його повна історія та об'єкти фізично ізольовані в каталозі .git/modules/ батьківського репо.", size=13))

    render(os.path.join(IMG, "gitlink-submodule-internals.svg"), W, H, *frags,
           title="Анатомія gitlink та механізм зв'язування Git Submodule")


# ── 3. Механіка злиття дерев у Git Subtree ──────────────────────────────────
def fig_git_subtree_merge_flow():
    W, H = 1100, 560
    frags = []

    frags.append(text(550, 45, "Механізм злиття зовнішнього дерева у підкаталог через Git Subtree", size=16, bold=True))

    # Ліва частина: Зовнішній апстрім
    frags.append(fitbox(50, 75, 440, 160,
                        "Віддалений репозиторій бібліотеки (Upstream)\n\n"
                        "Коміти в гілці main:\n"
                        "C1 -> C2 -> C3 -> C4 (реліз v2.1.0)",
                        size=13, fill=BLUE_FILL, stroke=NEG))

    frags.append(arrow(270, 245, 270, 285))
    frags.append(text(390, 265, "git subtree add --prefix=vendor/lib --squash", size=11.5, color=MUTED))

    # Головний репозиторій
    frags.append(fitbox(50, 295, 1000, 150,
                        "Головний репозиторій проєкту (Monolithic Tree)\n\n"
                        "• Синтезований Squash-коміт: містить знімок файлів C4 під префіксом vendor/lib/\n"
                        "• Merge-коміт (2 батьки): батько 1 = попередній коміт проєкту, батько 2 = squash-коміт\n"
                        "• Усі файли бібліотеки стають звичайними файлами репозиторію: будь-який git clone качає все одразу",
                        size=12.5, fill=OK_FILL, stroke=FIELD))

    frags.append(fitbox(520, 75, 530, 160,
                        "Переваги проти Submodules:\n\n"
                        "• Нуль конфігураційних файлів (.gitmodules не потрібен)\n"
                        "• Немає проблем із detached HEAD або відсутністю прав на CI\n"
                        "• Можливість редагувати й комітити прямо в каталозі проєкту",
                        size=12.5, fill=FILL, stroke=LINE))

    frags.append(fitbox(50, 470, 1000, 60,
                        "Git Subtree перетворює сторонній код на звичайні файли власного репозиторію через синтез merge-комітів,\n"
                        "усуваючи залежність від вторинних репозиторіїв та специфічних прапорців клонування.", size=13))

    render(os.path.join(IMG, "git-subtree-merge-flow.svg"), W, H, *frags,
           title="Схема імпорту та злиття дерева у Git Subtree")


# ── 4. Інтеграція вендорингу в CMake ─────────────────────────────────────────
def fig_cmake_vendoring_target_graph():
    W, H = 1100, 560
    frags = []

    frags.append(text(550, 45, "Інтеграція вендореного коду в CMake: захист глобального простору цілей", size=16, bold=True))

    # Батьківський проєкт
    frags.append(fitbox(50, 75, 420, 250,
                        "Кореневий CMakeLists.txt проєкту\n\n"
                        "# 1. Перевизначення кеш-опцій залежності\n"
                        "set(BUILD_TESTING OFF CACHE BOOL \"\" FORCE)\n"
                        "set(ZLIB_BUILD_EXAMPLES OFF CACHE BOOL \"\" FORCE)\n\n"
                        "# 2. Включення з ізоляцією\n"
                        "add_subdirectory(third_party/zlib EXCLUDE_FROM_ALL SYSTEM)\n\n"
                        "# 3. Лінкування через ALIAS\n"
                        "target_link_libraries(app PRIVATE Vendor::Zlib)",
                        size=12, fill=OK_FILL, stroke=FIELD))

    frags.append(arrow(480, 200, 550, 200))
    frags.append(text(515, 185, "ізолює", size=12, color=MUTED))

    # Вендорений код
    frags.append(fitbox(560, 75, 490, 250,
                        "Вендорений підпроєкт third_party/zlib/\n\n"
                        "• Рідна ціль: add_library(zlibstatic ...)\n"
                        "• Псевдонім простору імен: add_library(Vendor::Zlib ALIAS zlibstatic)\n"
                        "• Непотрібні цілі (тести/утиліти): відсікаються EXCLUDE_FROM_ALL\n"
                        "• Заголовки (zlib.h): позначаються як SYSTEM (-isystem)",
                        size=12, fill=FILL, stroke=LINE))

    # Три захисні шари
    guards = [
        ("EXCLUDE_FROM_ALL", "Виключає сторонні тести та утиліти\nзі стандартної збірки проєкту (target all)", 50),
        ("SYSTEM Include", "Придушує діагностичні попередження\nкомпілятора (-Wall -Werror) у чужому коді", 400),
        ("ALIAS & Namespaces", "Ізолює імена цілей (Vendor::Zlib) і\nзапобігає колізіям у глобальній моделі", 750),
    ]

    for g_title, g_desc, gx in guards:
        frags.append(fitbox(gx, 350, 300, 100, g_title + "\n\n" + g_desc, size=12, fill=BLUE_FILL, stroke=NEG))

    frags.append(fitbox(50, 475, 1000, 55,
                        "Правильна інтеграція вендорингу в CMake вимагає захисту кешу, виключення зайвих цілей через EXCLUDE_FROM_ALL,\n"
                        "придушення попереджень через SYSTEM та інкапсуляції бібліотек у псевдоніми з подвійною двокрапкою.", size=12.5))

    render(os.path.join(IMG, "cmake-vendoring-target-graph.svg"), W, H, *frags,
           title="Ізоляція та керування вендореним кодом у моделі цілей CMake")


# ── 5. Ромбоподібна залежність при вендорингу ────────────────────────────────
def fig_diamond_vendoring_collision():
    W, H = 1100, 560
    frags = []

    frags.append(text(550, 45, "Ромбоподібний конфлікт при вендорингу: порушення ODR та дублювання стану", size=16, bold=True))

    # Головний додаток
    frags.append(fitbox(380, 75, 340, 80,
                        "Головний додаток: App\n\n"
                        "target_link_libraries(App PRIVATE AudioEngine NetClient)",
                        size=12.5, fill=OK_FILL, stroke=FIELD))

    frags.append(arrow(470, 160, 320, 205))
    frags.append(arrow(630, 160, 780, 205))

    # Модуль 1
    frags.append(fitbox(80, 210, 420, 120,
                        "Модуль AudioEngine\n(Вендорить Logger v1.0 у third_party/logger/)\n\n"
                        "struct LogEntry { int id; char msg[64]; };\n"
                        "Розмір структури: 68 байтів",
                        size=12, fill=FILL, stroke=LINE))

    # Модуль 2
    frags.append(fitbox(600, 210, 420, 120,
                        "Модуль NetClient\n(Вендорить Logger v2.0 у vendor/logger/)\n\n"
                        "struct LogEntry { uint64_t ts; std::string msg; };\n"
                        "Розмір структури: 48 байтів",
                        size=12, fill=FILL, stroke=LINE))

    frags.append(arrow(290, 335, 450, 375))
    frags.append(arrow(810, 335, 650, 375))

    # Конфлікт лінкера та пам'яті
    frags.append(fitbox(80, 375, 940, 90,
                        "Катастрофа лінкування та порушення One Definition Rule (ODR):\n\n"
                        "1. CMake: аварія add_library(logger) duplicate target name (якщо не ізольовано)\n"
                        "2. Лінкер: multiple definition of 'log_message' або випадковий вибір першого символу (COMDAT folding)\n"
                        "3. Виконання: NetClient викликає log_message() і передає 48 байтів замість 68 -> пошкодження пам'яті SIGSEGV",
                        size=12, fill=WARN_FILL, stroke=POS))

    frags.append(fitbox(80, 485, 940, 50,
                        "Вендоринг без централізованого узгодження версій призводить до дублювання та смертоносних колізій ODR.",
                        size=13))

    render(os.path.join(IMG, "diamond-vendoring-collision.svg"), W, H, *frags,
           title="Ромбоподібна залежність та ODR-колапс при незалежному вендорингу")


if __name__ == "__main__":
    fig_vendoring_models_comparison()
    fig_gitlink_submodule_internals()
    fig_git_subtree_merge_flow()
    fig_cmake_vendoring_target_graph()
    fig_diamond_vendoring_collision()
    print("All figures for vendoring-submodules generated successfully.")
