# -*- coding: utf-8 -*-
"""Фігури до теми «Вимоги вжитку: PUBLIC, PRIVATE, INTERFACE»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL = "#eaf5ec"
INFO_FILL = "#eef4fb"


# ── 1. Три рівні вимог вжитку: PRIVATE, PUBLIC, INTERFACE ───────────────────
def fig_levels():
    W, H = 1080, 580
    frags = []

    frags.append(text(540, 42, "Розподіл властивостей цілі за ключовими словами", size=16, bold=True))
    frags.append(text(540, 68, "Куди команди target_* записують параметри збірки", size=13, color=MUTED))

    # Три чіткі вертикальні картки: PRIVATE, PUBLIC, INTERFACE
    # PRIVATE
    frags.append(fitbox(50, 95, 300, 370,
                        "PRIVATE\n\n"
                        "Запис потрапляє лише у власні властивості цілі:\n"
                        "• INCLUDE_DIRECTORIES\n"
                        "• COMPILE_DEFINITIONS\n"
                        "• COMPILE_OPTIONS\n"
                        "• LINK_LIBRARIES\n\n"
                        "Призначення:\n"
                        "Внутрішні заголовки (src/),\n"
                        "макроси реалізації,\n"
                        "прапорці компілятора,\n"
                        "закриті допоміжні бібліотеки.\n\n"
                        "Споживачам НЕ передається.", size=12.5, fill=WARN_FILL, stroke=POS))

    # PUBLIC
    frags.append(fitbox(390, 95, 300, 370,
                        "PUBLIC\n\n"
                        "Запис одночасно потрапляє в обидва списки:\n"
                        "• Власні (для своєї збірки)\n"
                        "• INTERFACE_* (для споживачів)\n\n"
                        "Призначення:\n"
                        "Публічні заголовки (include/),\n"
                        "макровизначення конфігурації API,\n"
                        "бібліотеки, чиї типи є частиною\n"
                        "відкритого інтерфейсу.\n\n"
                        "Потрібно і автору, і споживачу.", size=12.5, fill=OK_FILL, stroke=FIELD))

    # INTERFACE
    frags.append(fitbox(730, 95, 300, 370,
                        "INTERFACE\n\n"
                        "Запис потрапляє лише у властивості вжитку:\n"
                        "• INTERFACE_INCLUDE_DIRECTORIES\n"
                        "• INTERFACE_COMPILE_DEFINITIONS\n"
                        "• INTERFACE_COMPILE_FEATURES\n"
                        "• INTERFACE_LINK_LIBRARIES\n\n"
                        "Призначення:\n"
                        "Header-only бібліотеки,\n"
                        "суто інтерфейсні прапорці мови,\n"
                        "пакети налаштувань компілятора.\n\n"
                        "Сама ціль нічого не збирає.", size=12.5, fill=INFO_FILL, stroke=NEG))

    frags.append(fitbox(50, 485, 980, 65,
                        "Ключове слово обирає цільову торбу властивостей: PRIVATE будує лише саму ціль;\n"
                        "INTERFACE наповнює інтерфейс для клієнтів; PUBLIC записує властивість в обидва списки.", size=13))

    render(os.path.join(IMG, "public-private-interface.svg"), W, H, *frags,
           title="Розподіл вимог вжитку між власною збіркою та інтерфейсом споживача")


# ── 2. Транзитивне поширення вимог у DAG залежностей ────────────────────────
def fig_dag_propagation():
    W, H = 1060, 580
    frags = []

    frags.append(text(530, 42, "Транзитивність вимог вжитку в ланцюжку цілей", size=16, bold=True))
    frags.append(text(530, 68, "Поширення шляхів включення й макросів від джерела до фінальної програми", size=13, color=MUTED))

    # Math Core
    frags.append(fitbox(60, 100, 260, 130, "math_core\n(бібліотека)\nINTERFACE_INCLUDE = math/\nINTERFACE_DEFS = USE_SIMD", size=12, fill=INFO_FILL, stroke=NEG))

    # Сценарій А: engine лінкує math_core як PRIVATE
    frags.append(fitbox(400, 100, 260, 130, "engine\n(лінкує math_core PRIVATE)\nМає: math/, USE_SIMD\nЕкспортує: лише engine/", size=12, fill=WARN_FILL, stroke=POS))

    # app
    frags.append(fitbox(740, 100, 260, 130, "app\n(виконуваний файл)\nОтримує: engine/\nНЕ отримує: math/, USE_SIMD", size=12, fill=FILL, stroke=LINE))

    frags.append(arrow(320, 165, 400, 165))
    frags.append(text(360, 152, "PRIVATE", size=11, bold=True, color=POS))

    frags.append(arrow(660, 165, 740, 165))
    frags.append(text(700, 152, "лінкує", size=11, bold=True, color=LINE))

    frags.append(text(530, 255, "▼ Порівняння: що відбувається при PUBLIC-лінкуванні ▼", size=13.5, bold=True, color=FIELD))

    # Сценарій Б: engine лінкує math_core як PUBLIC
    frags.append(fitbox(60, 285, 260, 130, "math_core\n(бібліотека)\nINTERFACE_INCLUDE = math/\nINTERFACE_DEFS = USE_SIMD", size=12, fill=INFO_FILL, stroke=NEG))

    frags.append(fitbox(400, 285, 260, 130, "engine\n(лінкує math_core PUBLIC)\nМає: math/, USE_SIMD\nЕкспортує: engine/ + math/", size=12, fill=OK_FILL, stroke=FIELD))

    frags.append(fitbox(740, 285, 260, 130, "app\n(виконуваний файл)\nОтримує: engine/\n+ ТРАНЗИТИВНО math/, USE_SIMD", size=12, fill=OK_FILL, stroke=FIELD))

    frags.append(arrow(320, 350, 400, 350))
    frags.append(text(360, 337, "PUBLIC", size=11, bold=True, color=FIELD))

    frags.append(arrow(660, 350, 740, 350))
    frags.append(text(700, 337, "лінкує", size=11, bold=True, color=FIELD))

    frags.append(fitbox(60, 480, 940, 68,
                        "PRIVATE ізолює залежність: деталі реалізації math_core не протікають у споживача engine.\n"
                        "PUBLIC просуває вимоги вжитку далі по графу, роблячи типи math_core доступними в app.", size=13))

    render(os.path.join(IMG, "dag-propagation.svg"), W, H, *frags,
           title="Поширення вимог вжитку через ланцюжки залежностей у графі")


# ── 3. Інтерфейсна бібліотека (Header-Only) ─────────────────────────────────
def fig_header_only():
    W, H = 1000, 500
    frags = []

    frags.append(text(500, 42, "Інтерфейсна ціль (INTERFACE Library) у CMake", size=16, bold=True))
    frags.append(text(500, 68, "Ціль без об'єктних файлів, що існує виключно як пакет вимог вжитку", size=13, color=MUTED))

    # Інтерфейсна ціль у центрі
    frags.append(fitbox(350, 100, 300, 135, "add_library(json_parser INTERFACE)\n\nINTERFACE_INCLUDE = include/\nINTERFACE_FEATURES = cxx_std_20\n(Джерел .cpp немає, бінарник не створюється)", size=12, fill=INFO_FILL, stroke=NEG))

    # Два споживачі
    frags.append(fitbox(90, 290, 360, 120, "add_executable(web_service ...)\ntarget_link_libraries(web_service\n  PRIVATE json_parser)\n\nКомпілятор дістає: -Iinclude/ -std=c++20", size=12, fill=OK_FILL, stroke=FIELD))

    frags.append(fitbox(550, 290, 360, 120, "add_library(client_sdk SHARED ...)\ntarget_link_libraries(client_sdk\n  PUBLIC json_parser)\n\nКомпілятор дістає: -Iinclude/ -std=c++20\nЕкспортує вимоги своїм споживачам", size=12, fill=OK_FILL, stroke=FIELD))

    frags.append(arrow(420, 235, 270, 290))
    frags.append(arrow(580, 235, 730, 290))

    frags.append(fitbox(60, 435, 880, 45,
                        "Інтерфейсна ціль надає спільні заголовки та прапорці мови без зайвого кроку лінкування бінарного файлу.", size=13))

    render(os.path.join(IMG, "header-only-interface.svg"), W, H, *frags,
           title="Структура та поширення вимог інтерфейсної бібліотеки")


# ── 4. Генераторні вирази: BUILD_INTERFACE проти INSTALL_INTERFACE ─────────
def fig_build_vs_install():
    W, H = 1040, 530
    frags = []

    frags.append(text(520, 42, "Розділення шляхів: розробка в репозиторії проти встановленого пакета", size=16, bold=True))
    frags.append(text(520, 68, "Як генераторні вирази запобігають зашиванню локальних шляхів розробника в експорт", size=13, color=MUTED))

    # Визначення цілі
    frags.append(fitbox(160, 95, 720, 85,
                        "target_include_directories(mylib PUBLIC\n"
                        "  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>\n"
                        "  $<INSTALL_INTERFACE:include>\n"
                        ")", size=13, fill=FILL, stroke=LINE))

    # Дві колонки
    frags.append(fitbox(60, 215, 430, 175,
                        "Контекст 1: Збірка всередині проєкту (BUILD)\n\n"
                        "Працює вираз: $<BUILD_INTERFACE:...>\n"
                        "Шлях до заголовків:\n"
                        "/home/user/project/src/mylib/include\n\n"
                        "Тести та приклади проєкту бачать вихідний код", size=12, fill=OK_FILL, stroke=FIELD))

    frags.append(fitbox(550, 215, 430, 175,
                        "Контекст 2: Встановлений пакет (INSTALL)\n\n"
                        "Працює вираз: $<INSTALL_INTERFACE:...>\n"
                        "Шлях до заголовків:\n"
                        "<prefix>/include (наприклад /usr/local/include)\n\n"
                        "Зовнішні споживачі знаходять заголовки в системі", size=12, fill=INFO_FILL, stroke=NEG))

    frags.append(arrow(380, 180, 275, 215))
    frags.append(arrow(660, 180, 765, 215))

    frags.append(fitbox(60, 430, 920, 65,
                        "Без розділення команда install(EXPORT) видасть фатальну помилку, захищаючи від поширення\n"
                        "жорстко закодованих шляхів машини розробника в поширюваний дистрибутив.", size=13))

    render(os.path.join(IMG, "build-vs-install-interface.svg"), W, H, *frags,
           title="Розділення шляхів включення для етапів збірки та встановлення")


if __name__ == "__main__":
    fig_levels()
    fig_dag_propagation()
    fig_header_only()
    fig_build_vs_install()
    print("Всі фігури згенеровано успішно.")
