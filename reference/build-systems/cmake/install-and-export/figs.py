# -*- coding: utf-8 -*-
"""Фігури до теми «install і export: зробити проєкт придатним для find_package»."""
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


# ── 1. Дерево збірки проти дерева інсталяції ────────────────────────────────
def fig_build_vs_install_tree():
    W, H = 1040, 560
    frags = []

    frags.append(text(520, 50, "Генераторні вирази ізолюють внутрішні шляхи розробника від кінцевого префікса споживача", size=13, color=MUTED))

    # Лівий блок: Build Tree
    frags.append(fitbox(40, 75, 430, 36, "ДЕРЕВО ЗБІРКИ (Build Tree — простір розробника)", size=12.5, bold=True, fill=ACCENT_FILL, stroke=NEG))
    b_lines = (
        "project/ (Дерево джерел)\n"
        " ├── include/mylib/core.hpp   (Публічні та внутрішні заголовки)\n"
        " ├── src/core.cpp             (Вихідний код реалізації)\n"
        " └── tests/test_core.cpp      (Внутрішні модульні тести)\n\n"
        "build/ (Каталог збірки)\n"
        " ├── libmylib.so              (Скомпільований бінарний файл)\n"
        " ├── CMakeFiles/...           (Службові об'єктні файли .o)\n"
        " └── unit_tests               (Тимчасовий виконуваний файл)"
    )
    frags.append(fitbox(40, 120, 430, 210, b_lines, size=11.5, fill="#ffffff", stroke=LINE))
    
    b_gen = (
        "$<BUILD_INTERFACE:...>\n"
        "Шлях: ${CMAKE_CURRENT_SOURCE_DIR}/include\n"
        "• Діє під час компіляції бібліотеки та власних тестів\n"
        "• Повністю зникає з властивостей під час інсталяції"
    )
    frags.append(fitbox(40, 340, 430, 105, b_gen, size=11.5, fill=ACCENT_FILL, stroke=NEG))

    # Центральна стрілка та підпис
    frags.append(arrow(480, 230, 560, 230, color=LINE, sw=2.2))
    frags.append(text(520, 210, "cmake --install", size=12, bold=True, color=INK))
    frags.append(text(520, 255, "Копіювання публічних", size=11, color=MUTED))
    frags.append(text(520, 270, "артефактів", size=11, color=MUTED))

    # Правий блок: Install Tree
    frags.append(fitbox(570, 75, 430, 36, "ДЕРЕВО ІНСТАЛЯЦІЇ (Install Tree — чистий префікс)", size=12.5, bold=True, fill=OK_FILL, stroke=FIELD))
    i_lines = (
        "<prefix>/ (/usr/local, /opt/mylib або vcpkg)\n"
        " ├── include/mylib/core.hpp   (CMAKE_INSTALL_INCLUDEDIR)\n"
        " ├── lib/libmylib.so          (CMAKE_INSTALL_LIBDIR)\n"
        " └── lib/cmake/MyLib/         (Метадані пакета для споживачів)\n"
        "      ├── MyLibConfig.cmake         (Головний файл конфігурації)\n"
        "      ├── MyLibConfigVersion.cmake  (Перевірка версій)\n"
        "      └── MyLibTargets.cmake        (Імпортовані цілі MyLib::mylib)"
    )
    frags.append(fitbox(570, 120, 430, 210, i_lines, size=11.5, fill="#ffffff", stroke=LINE))

    i_gen = (
        "$<INSTALL_INTERFACE:...>\n"
        "Шлях: ${CMAKE_INSTALL_INCLUDEDIR} (include)\n"
        "• Активний для зовнішніх проєктів у find_package()\n"
        "• Прив'язується до динамічного префікса без жорстких шляхів"
    )
    frags.append(fitbox(570, 340, 430, 105, i_gen, size=11.5, fill=OK_FILL, stroke=FIELD))

    # Нижній висновок
    frags.append(fitbox(40, 465, 960, 50,
                        "Головний принцип: шляхи до коду розробника ніколи не повинні потрапляти у згенеровані конфіги інсталяції",
                        size=13, bold=True, fill=WARN_FILL, stroke=POS))

    render(os.path.join(IMG, "build-vs-install-tree.svg"), W, H, *frags,
           title="Розділення Build Tree та Install Tree у CMake")


# ── 2. Повний потік експорту та генерації пакета ────────────────────────────
def fig_export_targets_flow():
    W, H = 1040, 560
    frags = []

    frags.append(text(520, 50, "Послідовність реєстрації цілей, створення конфігураційних файлів та лінкування клієнтом", size=13, color=MUTED))

    # Рядок 1: Цілі та експортні набори
    s1 = "1. add_library(mylib ...)\nОголошення цілі в проєкті:\n• target_include_directories(...)\n• target_link_libraries(...)"
    frags.append(fitbox(40, 75, 280, 100, s1, size=12, fill=ACCENT_FILL, stroke=NEG))

    frags.append(arrow(320, 125, 370, 125))

    s2 = "2. install(TARGETS mylib EXPORT MyLibTargets ...)\n• Копіює бінарники в lib/ та bin/\n• Реєструє ціль в експортному наборі"
    frags.append(fitbox(370, 75, 310, 100, s2, size=12, fill="#ffffff", stroke=LINE))

    frags.append(arrow(680, 125, 730, 125))

    s3 = "3. install(EXPORT MyLibTargets ...)\nГенерує MyLibTargets.cmake:\n• Створює ціль MyLib::mylib\n• Записує властивості IMPORTED"
    frags.append(fitbox(730, 75, 270, 100, s3, size=12, fill=OK_FILL, stroke=FIELD))

    # Стрілка вниз до конфігурації
    frags.append(arrow(865, 175, 865, 215))

    # Рядок 2: Генерація конфігів і версій
    s4a = "4а. configure_package_config_file(...)\nГенерує MyLibConfig.cmake:\n• Макрос @PACKAGE_INIT@\n• find_dependency(...) залежностей\n• include(... MyLibTargets.cmake)"
    frags.append(fitbox(40, 215, 310, 110, s4a, size=11.5, fill=OK_FILL, stroke=FIELD))

    frags.append(arrow(350, 270, 370, 270))

    s4b = "4б. write_basic_package_version_file(...)\nГенерує MyLibConfigVersion.cmake:\n• Перевірка сумісності версій\n• SameMajorVersion / SameMinorVersion"
    frags.append(fitbox(370, 215, 310, 110, s4b, size=11.5, fill=OK_FILL, stroke=FIELD))

    frags.append(arrow(680, 270, 730, 270))

    s4c = "4в. install(FILES ...)\nКопіює Config та Version файли\nу каталог lib/cmake/MyLib\nпоруч із Targets.cmake"
    frags.append(fitbox(730, 215, 270, 110, s4c, size=11.5, fill="#ffffff", stroke=LINE))

    # Стрілка вниз до споживача
    frags.append(arrow(520, 325, 520, 365))

    # Рядок 3: Споживач
    s5 = "5. Зовнішній проєкт-споживач у власному CMakeLists.txt\nfind_package(MyLib 1.2 REQUIRED CONFIG)  →  знаходить MyLibConfig.cmake\ntarget_link_libraries(client_app PRIVATE MyLib::mylib)"
    frags.append(fitbox(40, 365, 960, 70, s5, size=13, bold=True, fill=ACCENT_FILL, stroke=NEG))

    # Підсумок
    frags.append(fitbox(40, 455, 960, 50,
                        "Результат: клієнтський проєкт отримує готову імпортовану ціль із транзитивними прапорцями та заголовками",
                        size=12.5, fill=OK_FILL, stroke=FIELD))

    render(os.path.join(IMG, "export-targets-flow.svg"), W, H, *frags,
           title="Конвеєр експорту та генерації пакета для find_package")


# ── 3. Переміщуваність пакета (Relocatable Packages) ────────────────────────
def fig_relocatable_package():
    W, H = 1040, 530
    frags = []

    frags.append(text(520, 50, "Динамічне обчислення _IMPORT_PREFIX запобігає прив'язці до абсолютних шляхів хост-машини", size=13, color=MUTED))

    # Верхній блок: Логіка коду
    code_lines = (
        "# Фрагмент згенерованого MyLibTargets.cmake:\n"
        "get_filename_component(_IMPORT_PREFIX \"${CMAKE_CURRENT_LIST_FILE}\" PATH)\n"
        "get_filename_component(_IMPORT_PREFIX \"${_IMPORT_PREFIX}\" PATH)  # вгору з MyLib/\n"
        "get_filename_component(_IMPORT_PREFIX \"${_IMPORT_PREFIX}\" PATH)  # вгору з cmake/\n"
        "get_filename_component(_IMPORT_PREFIX \"${_IMPORT_PREFIX}\" PATH)  # вгору з lib/ -> корінь префікса!\n\n"
        "set_target_properties(MyLib::mylib PROPERTIES\n"
        "  INTERFACE_INCLUDE_DIRECTORIES \"${_IMPORT_PREFIX}/include\"\n"
        "  IMPORTED_LOCATION_RELEASE     \"${_IMPORT_PREFIX}/lib/libmylib.so\"\n"
        ")"
    )
    frags.append(fitbox(40, 75, 960, 180, code_lines, size=11.5, fill="#ffffff", stroke=LINE))

    # Дві стрілки вниз
    frags.append(arrow(270, 255, 270, 290))
    frags.append(arrow(750, 255, 750, 290))

    # Сценарій А: Префікс за замовчуванням
    sc_a = (
        "Розташування А: системний каталог /usr/local\n"
        "• Файл: /usr/local/lib/cmake/MyLib/MyLibTargets.cmake\n"
        "• Обчислений _IMPORT_PREFIX = /usr/local\n"
        "• Заголовки: /usr/local/include\n"
        "• Бібліотека: /usr/local/lib/libmylib.so"
    )
    frags.append(fitbox(40, 290, 460, 120, sc_a, size=11.5, fill=OK_FILL, stroke=FIELD))

    # Сценарій Б: Переміщений префікс
    sc_b = (
        "Розташування Б: ізольований каталог /opt/custom/mylib-v1.2\n"
        "• Файл: /opt/custom/mylib-v1.2/lib/cmake/MyLib/MyLibTargets.cmake\n"
        "• Обчислений _IMPORT_PREFIX = /opt/custom/mylib-v1.2\n"
        "• Заголовки: /opt/custom/mylib-v1.2/include\n"
        "• Бібліотека: /opt/custom/mylib-v1.2/lib/libmylib.so"
    )
    frags.append(fitbox(540, 290, 460, 120, sc_b, size=11.5, fill=OK_FILL, stroke=FIELD))

    # Підсумок
    frags.append(fitbox(40, 430, 960, 55,
                        "Переміщення каталогу інсталяції не ламає бінарники та заголовки — всі шляхи рахуються відносно Targets.cmake",
                        size=12.5, bold=True, fill=ACCENT_FILL, stroke=NEG))

    render(os.path.join(IMG, "relocatable-package-prefix.svg"), W, H, *frags,
           title="Обчислення релокованого префікса у Targets.cmake")


if __name__ == "__main__":
    fig_build_vs_install_tree()
    fig_export_targets_flow()
    fig_relocatable_package()
    print("Фігури успішно згенеровано.")
