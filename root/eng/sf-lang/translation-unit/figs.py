# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. tu-preprocessing: від .cpp + .h до єдиної TU і .o ───────────────────────
def fig_tu_preprocessing():
    W, H = 760, 360
    p = []

    # Вхідні сирцеві файли
    p.append(textbox(90, 80, "main.cpp\n(основний код)", size=11, bold=True, fill="#ffffff", stroke=INK, min_w=130)[0])
    p.append(textbox(90, 160, "config.hpp\n(#include)", size=11, bold=True, fill="#fdf6e3", stroke="#b79a5e", color="#8a6a14", min_w=130)[0])
    p.append(textbox(90, 240, "<vector>, <string>\n(#include)", size=11, bold=True, fill="#fdf6e3", stroke="#b79a5e", color="#8a6a14", min_w=130)[0])

    # Стрілки до Препроцесора
    p.append(arrow(165, 80, 220, 140, color=MUTED, sw=1.5))
    p.append(arrow(165, 160, 220, 160, color=MUTED, sw=1.5))
    p.append(arrow(165, 240, 220, 180, color=MUTED, sw=1.5))

    # Препроцесор
    prep, pw, ph = textbox(290, 160, "ПРЕПРОЦЕСОР\nрозгортання #include,\nмакросів #define,\nумов #ifdef", size=10, bold=True,
                           fill="#fff6e0", stroke="#caa24a", color="#8a6a14", min_w=130)
    p.append(prep)

    # Стрілка від препроцесора до Одиниці трансляції
    p.append(arrow(290 + pw / 2 + 4, 160, 395, 160, color=MUTED, sw=2))

    # Одиниця трансляції (Translation Unit)
    tu_box = fitbox(400, 70, 140, 180, "Translation Unit\n(TU)\n\nЄдиний плоский\nтекстовий потік\n(десятки тисяч\nрядків після\nрозкриття)",
                    size=10, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG)
    p.append(tu_box)

    # Стрілка до компілятора
    p.append(arrow(545, 160, 580, 160, color=NEG, sw=2))

    # Компілятор і вихідний об'єктний файл
    comp_box, cw, ch = textbox(655, 160, "main.o (.obj)\n\nСекції:\n.text (код)\n.data (змінні)\nСимволи\nРелокації",
                               size=10, bold=True, fill="#eafaf0", stroke=FIELD, color=FIELD, min_w=125)
    p.append(comp_box)

    p.append(text(W / 2, 325, "Компілятор обробляє кожну TU абсолютно автономно, нічого не знаючи про інші .cpp файли",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "tu-preprocessing.svg"), W, H, *p,
           title="Анатомія одиниці трансляції (Translation Unit)")


# ── 2. linkage-types: три рівні зв'язування ─────────────────────────────────────
def fig_linkage_types():
    W, H = 760, 340
    p = []

    # Три колонки для трьох рівнів
    colw = 220
    x_coords = [130, 380, 630]

    # Заголовки типів
    p.append(textbox(x_coords[0], 75, "External Linkage\n(Зовнішнє)", size=12, bold=True,
                     fill="#eafaf0", stroke=FIELD, color=FIELD, min_w=colw)[0])
    p.append(textbox(x_coords[1], 75, "Internal Linkage\n(Внутрішнє)", size=12, bold=True,
                     fill="#eaf0fd", stroke=NEG, color=NEG, min_w=colw)[0])
    p.append(textbox(x_coords[2], 75, "No Linkage\n(Без зв'язування)", size=12, bold=True,
                     fill="#fdecea", stroke=POS, color=POS, min_w=colw)[0])

    # Приклади синтаксису
    p.append(fitbox(x_coords[0] - colw/2, 115, colw, 65,
                    "int global_counter;\nextern int flag;\nvoid process_packet();",
                    size=10, bold=True, fill=FILL, stroke=LINE))

    p.append(fitbox(x_coords[1] - colw/2, 115, colw, 65,
                    "static int s_cache;\nconst int kMax = 100; // C++\nnamespace { void helper(); }",
                    size=10, bold=True, fill=FILL, stroke=LINE))

    p.append(fitbox(x_coords[2] - colw/2, 115, colw, 65,
                    "void foo() {\n  int local_x = 42;\n  static int call_cnt;\n}",
                    size=10, bold=True, fill=FILL, stroke=LINE))

    # Видимість у таблиці символів (.o)
    p.append(fitbox(x_coords[0] - colw/2, 195, colw, 80,
                    "Таблиця символів:\nSTB_GLOBAL\n\nДоступно лінкеру для\nзшивання між усіма TU",
                    size=10, bold=False, fill="#ffffff", stroke=FIELD))

    p.append(fitbox(x_coords[1] - colw/2, 195, colw, 80,
                    "Таблиця символів:\nSTB_LOCAL\n\nПриховано всередині TU.\nКолізії імен відсутні",
                    size=10, bold=False, fill="#ffffff", stroke=NEG))

    p.append(fitbox(x_coords[2] - colw/2, 195, colw, 80,
                    "Таблиця символів:\nНЕМАЄ (ім'я відсутнє)\n\nІснує лише як адреса\nв стеку чи регістрі",
                    size=10, bold=False, fill="#ffffff", stroke=POS))

    p.append(text(W / 2, 305, "Рівень зв'язування визначає, чи бачить лінкер ім'я символу за межами поточного .o файлу",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "linkage-types.svg"), W, H, *p,
           title="Модель зв'язування символів у C та C++")


# ── 3. inline-comdat: дедуплікація COMDAT лінкером ──────────────────────────────
def fig_inline_comdat():
    W, H = 760, 360
    p = []

    # Заголовочний файл ліворуч у центрі
    hdr_box, hw, hh = textbox(110, 180, "math_utils.hpp\n\ninline int square(int x) {\n  return x * x;\n}",
                              size=10, bold=True, fill="#fff6e0", stroke="#caa24a", color="#8a6a14", min_w=160)
    p.append(hdr_box)

    # Дві одиниці трансляції
    tu1_box, t1w, t1h = textbox(260, 110, "TU 1 (alpha.cpp)\n#include \"math_utils.hpp\"", size=10, bold=True, fill="#ffffff", stroke=INK, min_w=150)
    tu2_box, t2w, t2h = textbox(260, 250, "TU 2 (beta.cpp)\n#include \"math_utils.hpp\"", size=10, bold=True, fill="#ffffff", stroke=INK, min_w=150)
    p.append(tu1_box)
    p.append(tu2_box)

    # Стрілки від math_utils.hpp до TU 1 та TU 2
    p.append(arrow(110 + hw/2 + 2, 160, 260 - t1w/2 - 4, 115, color=MUTED, sw=1.5))
    p.append(arrow(110 + hw/2 + 2, 200, 260 - t2w/2 - 4, 245, color=MUTED, sw=1.5))

    # Стрілки до об'єктних файлів
    p.append(arrow(260 + t1w/2 + 2, 110, 395, 110, color=MUTED, sw=1.8))
    p.append(arrow(260 + t2w/2 + 2, 250, 395, 250, color=MUTED, sw=1.8))

    # Об'єктні файли з секціями COMDAT
    p.append(fitbox(400, 80, 150, 60, "alpha.o\n.text._Z6squarei\n(COMDAT / linkonce)",
                    size=10, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG))
    p.append(fitbox(400, 220, 150, 60, "beta.o\n.text._Z6squarei\n(COMDAT / linkonce)",
                    size=10, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG))

    # Лінкер
    p.append(arrow(555, 110, 595, 160, color=MUTED, sw=1.8))
    p.append(arrow(555, 250, 595, 200, color=MUTED, sw=1.8))

    linker_box, lw, lh = textbox(635, 180, "ЛІНКЕР\nДедуплікація\nCOMDAT", size=11, bold=True,
                                 fill="#fff6e0", stroke="#caa24a", color="#8a6a14", min_w=95)
    p.append(linker_box)

    # Фінальний бінарник праворуч
    p.append(arrow(635 + lw/2 + 2, 180, 690, 180, color=FIELD, sw=2.5))
    p.append(fitbox(695, 140, 60, 80, "Бінарник:\n\nРівно 1\nкопія\nкоду!",
                    size=9, bold=True, fill="#eafaf0", stroke=FIELD, color=FIELD))

    p.append(text(W / 2, 335, "Ключове слово inline дозволяє дублювати визначення в кількох TU, а лінкер залишає лише одну копію",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "inline-comdat.svg"), W, H, *p,
           title="Дедуплікація inline-функцій лінкером через COMDAT")


# ── 4. odr-violation: невідповідність розміток через #ifdef ────────────────────
def fig_odr_violation():
    W, H = 760, 350
    p = []

    # Заголовок з умовною компіляцією
    p.append(fitbox(190, 60, 380, 65, "struct Packet {\n  int id;\n#ifdef DEBUG\n  char tag[8];\n#endif\n  int payload;\n};",
                    size=10, bold=True, fill="#fdf6e3", stroke="#b79a5e", color="#8a6a14"))

    # Дві TU з різними прапорцями компіляції
    p.append(arrow(280, 130, 190, 160, color=POS, sw=1.8))
    p.append(arrow(480, 130, 570, 160, color=FIELD, sw=1.8))

    # TU 1: DEBUG увімкнено
    p.append(textbox(190, 180, "TU 1 (sender.cpp)\n-DDEBUG (Розмір = 16B)", size=11, bold=True,
                     fill="#fdecea", stroke=POS, color=POS, min_w=240)[0])

    p.append(fitbox(70, 215, 240, 65, "Зсуви полів у TU 1:\n[+0] id (4B)\n[+4] tag (8B) [включно з padding]\n[+12] payload (4B)",
                    size=10, bold=False, fill="#ffffff", stroke=POS))

    # TU 2: DEBUG вимкнено
    p.append(textbox(570, 180, "TU 2 (receiver.cpp)\nDEBUG вимкнено (Розмір = 8B)", size=11, bold=True,
                     fill="#eafaf0", stroke=FIELD, color=FIELD, min_w=240)[0])

    p.append(fitbox(450, 215, 240, 65, "Зсуви полів у TU 2:\n[+0] id (4B)\n[+4] payload (4B)\n(поле tag взагалі відсутнє)",
                    size=10, bold=False, fill="#ffffff", stroke=FIELD))

    # Нижня рамка з поясненням катастрофи
    p.append(fitbox(70, 290, 620, 45,
                    "Порушення ODR (Ill-Formed, No Diagnostic Required): лінкер не перевіряє сумісність внутрішнього макета структур.\n"
                    "Читання payload у receiver.cpp читає байти tag з sender.cpp — руйнування пам'яті та приховані збої!",
                    size=10, bold=True, fill="#fff3cd", stroke="#856404", color="#856404"))

    render(os.path.join(OUT, "odr-violation.svg"), W, H, *p,
           title="Порушення One Definition Rule (ODR) через невідповідність макета пам'яті")


# ── 5. static-init-order: SIOF та Construct-On-First-Use ────────────────────────
def fig_static_init_order():
    W, H = 760, 360
    p = []

    # Верхня частина: Катастрофа SIOF
    p.append(text(80, 65, "Проблема: Порядок статичної ініціалізації між TU не визначений", size=12, bold=True, color=POS, anchor="start"))

    p.append(fitbox(40, 80, 290, 70, "TU A (logger.cpp)\n\nLogger g_logger;\n// Конструктор звертається\n// до g_config.getLogLevel()",
                    size=10, bold=True, fill="#fdecea", stroke=POS, color=POS))

    p.append(fitbox(430, 80, 290, 70, "TU B (config.cpp)\n\nConfig g_config;\n// Ініціалізується даними з диска\n// під час запуску програми",
                    size=10, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG))

    p.append(arrow(335, 115, 425, 115, color=POS, sw=2))
    p.append(text(380, 105, "виклик", size=10, color=POS, bold=True))
    p.append(text(380, 135, "ДО ініціалізації!\n(Crash / UB)", size=9, color=POS))

    # Розділювач
    p.append(line(40, 165, 720, 165, color=MUTED, sw=1, dash="4 4"))

    # Нижня частина: Розв'язання через Construct-On-First-Use
    p.append(text(80, 190, "Розв'язання: Патерн «Construct-On-First-Use» (Meyers' Singleton)", size=12, bold=True, color=FIELD, anchor="start"))

    p.append(fitbox(40, 205, 420, 100, "Config& getConfig() {\n  // Ініціалізується гарантовано при першому вході\n  // у функцію (потокобезпечно в C++11)\n  static Config instance;\n  return instance;\n}",
                    size=10, bold=True, fill="#eafaf0", stroke=FIELD, color=FIELD))

    p.append(fitbox(490, 205, 230, 100, "TU A (logger.cpp)\n\nLogger::Logger() {\n  auto level = getConfig().getLevel();\n  // Завжди безпечно!\n}",
                    size=10, bold=False, fill="#ffffff", stroke=FIELD))

    p.append(arrow(465, 255, 485, 255, color=FIELD, sw=2))

    p.append(text(W / 2, 335, "Локальні статичні змінні створюються ліниво в момент першого виклику функції, що усуває хаос порядку",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "static-init-order.svg"), W, H, *p,
           title="Static Initialization Order Fiasco та його розв'язання")


# ── 6. modules-vs-includes: модулі проти текстових включень ────────────────────
def fig_modules_vs_includes():
    W, H = 760, 340
    p = []

    # Ліва половина: Класичні #include
    p.append(text(190, 65, "Класичні заголовки (#include)", size=12, bold=True, color=POS))

    p.append(fitbox(40, 85, 300, 70, "#include <vector>\n#define BUFFER_SIZE 1024\n\nТекстове копіювання в кожен TU.\nПовторний парсинг N разів!",
                    size=10, bold=False, fill="#fdecea", stroke=POS))

    p.append(fitbox(40, 170, 300, 85, "Недоліки:\n• Витік макросів у весь проєкт\n• Тривалий час компіляції\n• ODR-ризики через конфлікти порядку включення",
                    size=10, bold=False, fill="#ffffff", stroke=POS))

    # Розділювач
    p.append(line(380, 50, 380, 280, color=MUTED, sw=1.5))

    # Права половина: C++20 Modules
    p.append(text(570, 65, "C++20 Modules (import / export)", size=12, bold=True, color=FIELD))

    p.append(fitbox(420, 85, 300, 70, "export module math;\nexport int square(int x) { return x * x; }\n\nКомпілюється 1 раз у бінарний інтерфейс (BMI: .pcm / .ifc)",
                    size=10, bold=False, fill="#eafaf0", stroke=FIELD))

    p.append(fitbox(420, 170, 300, 85, "Переваги:\n• Макроси НЕ експортуються назовні\n• Миттєвий імпорт розібраного AST\n• Модульне зв'язування (module linkage)\n• Повна ізоляція від порядку імпорту",
                    size=10, bold=False, fill="#ffffff", stroke=FIELD))

    p.append(text(W / 2, 305, "C++20 модулі замінюють текстове вставляння токенів семантичним імпортом скомпільованого інтерфейсу",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "modules-vs-includes.svg"), W, H, *p,
           title="Порівняння класичних заголовків та C++20 Modules")


if __name__ == "__main__":
    fig_tu_preprocessing()
    fig_linkage_types()
    fig_inline_comdat()
    fig_odr_violation()
    fig_static_init_order()
    fig_modules_vs_includes()
    print("All figures generated successfully.")
