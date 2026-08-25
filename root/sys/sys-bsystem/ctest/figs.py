# -*- coding: utf-8 -*-
"""Фігури до теми «CTest: реєстрація й запуск тестів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL = "#eaf5ec"
ACCENT_FILL = "#eaf0fd"


# ── 1. Життєвий цикл тестування: від CMakeLists.txt до CTest ───────────────────
def fig_ctest_architecture():
    W, H = 1060, 560
    frags = []

    frags.append(text(530, 48, "Життєвий цикл тестування в CMake та CTest", size=16, bold=True))
    frags.append(text(530, 72, "Розділення фаз конфігурації, компіляції бінарників та оркестрації процесів", size=13, color=MUTED))

    # Колонка 1: Фаза конфігурації CMake
    frags.append(rect(50, 100, 280, 360, fill=FILL, stroke=LINE))
    frags.append(text(190, 128, "1. Конфігурація (CMake)", size=14, bold=True))
    frags.append(fitbox(65, 148, 250, 64, "enable_testing()\nadd_test(NAME ... COMMAND ...)\nset_tests_properties(...)", size=12.5, fill=BG))
    frags.append(arrow(190, 222, 190, 252))
    frags.append(text(190, 240, "генерація метаданих", size=11, color=MUTED, anchor="middle"))
    frags.append(fitbox(65, 260, 250, 75, "Дерево CTestTestfile.cmake:\n• команди запуску й аргументи\n• властивості (TIMEOUT, LABELS)\n• фікстури й залежності", size=12, fill=ACCENT_FILL, stroke=NEG))

    # Колонка 2: Фаза збірки
    frags.append(rect(390, 100, 280, 360, fill=FILL, stroke=LINE))
    frags.append(text(530, 128, "2. Компіляція (Build Tool)", size=14, bold=True))
    frags.append(fitbox(405, 148, 250, 64, "cmake --build build\n(Ninja / Make / MSBuild)", size=12.5, fill=BG))
    frags.append(arrow(530, 222, 530, 252))
    frags.append(text(530, 240, "компіляція й лінкування", size=11, color=MUTED, anchor="middle"))
    frags.append(fitbox(405, 260, 250, 75, "Тестові виконувані файли:\n• unit_tests (GoogleTest)\n• integration_tests (Catch2)\n• допоміжні утиліти й скрипти", size=12, fill=OK_FILL, stroke=FIELD))

    # Стрілки з 1 і 2 до 3
    frags.append(arrow(330, 300, 385, 300))
    frags.append(arrow(670, 300, 725, 300))

    # Колонка 3: Фаза виконання CTest
    frags.append(rect(730, 100, 280, 360, fill=FILL, stroke=LINE))
    frags.append(text(870, 128, "3. Виконання (CTest)", size=14, bold=True))
    frags.append(fitbox(745, 148, 250, 74, "ctest --test-dir build -j8\n• читає CTestTestfile.cmake\n• паралельно спавнить процеси\n• стежить за кодами й таймаутом", size=12, fill=BG))
    frags.append(arrow(870, 232, 870, 262))
    frags.append(text(870, 250, "збір результатів і логів", size=11, color=MUTED, anchor="middle"))
    frags.append(fitbox(745, 270, 250, 75, "Артефакти й звіти:\n• LastTest.log (детальні логи)\n• junit-report.xml (для CI/CD)\n• MemoryCheck / Sanitize звіти", size=12, fill=ACCENT_FILL, stroke=NEG))

    frags.append(fitbox(50, 480, 960, 58,
                        "CMake описує тести й генерує CTestTestfile.cmake; білд-система компілює бінарники;\n"
                        "CTest запускає зібрані програми як окремі процеси, контролює ізоляцію, час і повернення.", size=13.5))

    render(os.path.join(IMG, "ctest-architecture.svg"), W, H, *frags,
           title="Життєвий цикл тестування: від CMakeLists.txt до звітів CTest")


# ── 2. Декларативні фікстури: SETUP, REQUIRED та CLEANUP ───────────────────────
def fig_fixtures_lifecycle():
    W, H = 1040, 520
    frags = []

    frags.append(text(520, 48, "Декларативні фікстури у CTest", size=16, bold=True))
    frags.append(text(520, 72, "Гарантоване виконання підготовки та очищення ресурсів навіть у разі аварії тестів", size=13, color=MUTED))

    # Блок 1: SETUP
    frags.append(fitbox(60, 110, 260, 130,
                        "1. FIXTURES_SETUP: db_init\n\n"
                        "• запуск тимчасової БД / мока\n"
                        "• міграція схеми даних\n"
                        "• запис порту у файл", size=12.5, fill=ACCENT_FILL, stroke=NEG))

    # Стрілка від Setup до Required
    frags.append(arrow(320, 175, 385, 175))
    frags.append(text(352, 162, "успіх", size=11, color=FIELD, anchor="middle", bold=True))

    # Блок 2: REQUIRED (паралельні тести)
    frags.append(rect(390, 100, 280, 260, fill=FILL, stroke=LINE))
    frags.append(text(530, 126, "2. FIXTURES_REQUIRED: db_init", size=13, bold=True))
    frags.append(fitbox(405, 140, 250, 50, "test_user_auth (worker 1)", size=12, fill=OK_FILL, stroke=FIELD))
    frags.append(fitbox(405, 200, 250, 50, "test_order_create (worker 2)", size=12, fill=OK_FILL, stroke=FIELD))
    frags.append(fitbox(405, 260, 250, 50, "test_payment_fail (worker 3)", size=12, fill=WARN_FILL, stroke=POS))
    frags.append(text(530, 335, "паралельне виконання (ctest -j)", size=11, color=MUTED, anchor="middle"))

    # Стрілка від Required до Cleanup
    frags.append(arrow(670, 175, 735, 175))
    frags.append(text(702, 162, "завжди", size=11, color=INK, anchor="middle", bold=True))

    # Блок 3: CLEANUP
    frags.append(fitbox(740, 110, 240, 130,
                        "3. FIXTURES_CLEANUP: db_init\n\n"
                        "• зупинка контейнера / сервера\n"
                        "• очищення тимчасових файлів\n"
                        "• звільнення портів", size=12.5, fill=ACCENT_FILL, stroke=NEG))

    # Гілка аварії SETUP
    frags.append(line(190, 240, 190, 390, color=POS, sw=1.5, dash="4,4"))
    frags.append(line(190, 390, 860, 390, color=POS, sw=1.5, dash="4,4"))
    frags.append(arrow(860, 390, 860, 240, color=POS, sw=1.5))
    frags.append(fitbox(270, 372, 400, 36, "якщо SETUP падає → тести пропускаються, але CLEANUP виконується!", size=11.5, fill=WARN_FILL, stroke=POS))

    frags.append(fitbox(60, 440, 920, 58,
                        "FIXTURES_SETUP готує середовище; FIXTURES_REQUIRED запускає набір тестів, що залежать від нього;\n"
                        "FIXTURES_CLEANUP гарантовано звільняє ресурси навіть при краху або таймауті будь-якого тесту.", size=13.5))

    render(os.path.join(IMG, "fixtures-lifecycle.svg"), W, H, *frags,
           title="Декларативні фікстури: SETUP, REQUIRED та CLEANUP")


# ── 3. Реєстрація тестів: gtest_add_tests vs gtest_discover_tests ──────────────
def fig_test_discovery_mechanism():
    W, H = 1060, 540
    frags = []

    frags.append(text(530, 48, "Реєстрація тестів GoogleTest у CMake", size=16, bold=True))
    frags.append(text(530, 72, "Статичний розбір вихідних файлів проти динамічного виявлення бінарником", size=13, color=MUTED))

    # Ліва сторона: gtest_add_tests
    frags.append(rect(50, 100, 450, 340, fill=FILL, stroke=LINE))
    frags.append(text(275, 128, "gtest_add_tests (CMake Configure Time)", size=14, bold=True, color=POS))
    frags.append(fitbox(70, 148, 410, 65, "CMake сканує .cpp вихідники регулярними виразами\nпід час виконання cmake -B build.\nШукає TEST(), TEST_F(), TYPED_TEST().", size=12.5, fill=BG))
    frags.append(arrow(275, 220, 275, 255))
    frags.append(text(275, 240, "парсинг тексту", size=11, color=MUTED, anchor="middle"))
    frags.append(fitbox(70, 260, 410, 100, "Вразливості методу:\n• Не бачить тестів, згенерованих C++ макросами/шаблонами\n• Не бачить Value-Parameterized тестів (INSTANTIATE_TEST_SUITE_P)\n• Додавання тесту в .cpp вимагає перезапуску CMake конфігурації!", size=12, fill=WARN_FILL, stroke=POS))
    frags.append(text(275, 410, "Застарілий підхід (статичний парсинг)", size=12, color=POS, bold=True))

    # Права сторона: gtest_discover_tests
    frags.append(rect(560, 100, 450, 340, fill=FILL, stroke=LINE))
    frags.append(text(785, 128, "gtest_discover_tests (Post-Build / Test Time)", size=14, bold=True, color=FIELD))
    frags.append(fitbox(580, 148, 410, 65, "CMake створює скрипт пост-збірки.\nПісля компіляції запускається бінарник:\n./test_runner --gtest_list_tests", size=12.5, fill=BG))
    frags.append(arrow(785, 220, 785, 255))
    frags.append(text(785, 240, "динамічне опитування бінарника", size=11, color=MUTED, anchor="middle"))
    frags.append(fitbox(580, 260, 410, 100, "Переваги методу:\n• 100% точний список усіх тестів (включно з параметризованими)\n• Редагування .cpp не вимагає cmake конфігурації — CTest оновить список сам\n• Кожен тест GoogleTest стає окремою одиницею CTest з власним логом", size=12, fill=OK_FILL, stroke=FIELD))
    frags.append(text(785, 410, "Сучасний стандарт (динамічний discovery)", size=12, color=FIELD, bold=True))

    frags.append(fitbox(50, 460, 960, 58,
                        "gtest_add_tests парсить текст на етапі конфігурації й пропускає динамічні тести;\n"
                        "gtest_discover_tests опитує скомпільований бінарник і реєструє точний список тестів без перезапуску CMake.", size=13.5))

    render(os.path.join(IMG, "test-discovery-mechanism.svg"), W, H, *frags,
           title="Реєстрація тестів: статичний аналіз проти динамічного опитування")


# ── 4. Паралельне планування тестів за вартістю (COST) ─────────────────────────
def fig_parallel_scheduling_cost():
    W, H = 1060, 550
    frags = []

    frags.append(text(530, 48, "Паралельне планування тестів у CTest (ctest -j2)", size=16, bold=True))
    frags.append(text(530, 72, "Вплив властивості COST та історії LastTest.log на загальний час виконання (makespan)", size=13, color=MUTED))

    # Секція 1: Без COST (FIFO)
    frags.append(rect(50, 95, 960, 180, fill=FILL, stroke=LINE))
    frags.append(text(80, 122, "1. Без оптимізації за COST (випадковий/FIFO порядок): загальний час = 28 с", size=13.5, bold=True, anchor="start", color=POS))

    # Потік 1
    frags.append(text(120, 160, "Потік 1:", size=12.5, bold=True, anchor="end"))
    frags.append(fitbox(130, 140, 140, 36, "test_a (3 с)", size=12, fill=OK_FILL, stroke=FIELD))
    frags.append(fitbox(280, 140, 140, 36, "test_b (4 с)", size=12, fill=OK_FILL, stroke=FIELD))
    frags.append(fitbox(430, 140, 140, 36, "test_c (2 с)", size=12, fill=OK_FILL, stroke=FIELD))
    frags.append(fitbox(580, 140, 400, 36, "ПРОСТІЙ ПОТОКУ (очікування завершення важкого тесту)", size=11.5, fill=WARN_FILL, stroke=POS, color=POS))

    # Потік 2
    frags.append(text(120, 220, "Потік 2:", size=12.5, bold=True, anchor="end"))
    frags.append(fitbox(130, 200, 140, 36, "test_d (4 с)", size=12, fill=OK_FILL, stroke=FIELD))
    frags.append(fitbox(280, 200, 140, 36, "test_e (4 с)", size=12, fill=OK_FILL, stroke=FIELD))
    frags.append(fitbox(430, 200, 550, 36, "test_integration_heavy (20 с) — пізній старт!", size=12, fill=WARN_FILL, stroke=POS))

    # Секція 2: З оптимізацією COST (LPT — Longest Processing Time first)
    frags.append(rect(50, 295, 960, 175, fill=FILL, stroke=LINE))
    frags.append(text(80, 322, "2. З властивістю COST або історією CTest (найдовші тести стартують першими): час = 20 с", size=13.5, bold=True, anchor="start", color=FIELD))

    # Потік 1
    frags.append(text(120, 360, "Потік 1:", size=12.5, bold=True, anchor="end"))
    frags.append(fitbox(130, 340, 550, 36, "test_integration_heavy (COST 20.0) — миттєвий старт на початку прогону", size=12, fill=ACCENT_FILL, stroke=NEG))

    # Потік 2
    frags.append(text(120, 420, "Потік 2:", size=12.5, bold=True, anchor="end"))
    frags.append(fitbox(130, 400, 130, 36, "test_b (4 с)", size=12, fill=OK_FILL, stroke=FIELD))
    frags.append(fitbox(270, 400, 130, 36, "test_d (4 с)", size=12, fill=OK_FILL, stroke=FIELD))
    frags.append(fitbox(410, 400, 130, 36, "test_e (4 с)", size=12, fill=OK_FILL, stroke=FIELD))
    frags.append(fitbox(550, 400, 130, 36, "test_a (3 с)", size=12, fill=OK_FILL, stroke=FIELD))
    frags.append(fitbox(690, 400, 130, 36, "test_c (2 с)", size=12, fill=OK_FILL, stroke=FIELD))

    frags.append(fitbox(50, 485, 960, 52,
                        "Без пріоритетів важкий тест, запущений наприкінці, змушує всі інші ядра простоювати.\n"
                        "Встановлення COST або використання даних попереднього прогону зменшує загальний час CI.", size=13.5))

    render(os.path.join(IMG, "parallel-scheduling-cost.svg"), W, H, *frags,
           title="Паралельне планування тестів за вартістю (COST)")


def main():
    fig_ctest_architecture()
    fig_fixtures_lifecycle()
    fig_test_discovery_mechanism()
    fig_parallel_scheduling_cost()
    print("Всі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
