# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій до теми «Модулі C++20: інтерфейс замість заголовка»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

DIE  = "#fdecea"   # небезпека / застарілий підхід (червонуватий)
LIVE = "#e8f6ee"   # новий модульний підхід / безпечне (зеленуватий)
COLD = "#eef2fb"   # нейтральне / структури / бінарні артефакти (блакитний)
WARN = "#fff4d6"   # проміжний стан / сканування / видимість (жовтуватий)


# ── 1. Текстова модель #include проти семантичного імпорту модулів ──────────
def fig_include_vs_import():
    W, H = 1240, 490
    f = []

    # Ліва колонка: Текстовий препроцесор (#include)
    f.append(text(300, 48, "Текстовий препроцесор (#include)", size=16, bold=True, color=POS))
    f.append(text(300, 72, "Лексична вставка тексту та витік макросів у кожну одиницю", size=12, color=MUTED))

    f.append(fitbox(60, 100, 480, 75,
                    "Заголовковий файл (header.h)\n#define BUFFER_SIZE 1024\nstruct Record { int id; };\n// 50 000+ рядків транзитивних залежностей",
                    size=12, fill=DIE, stroke=POS))

    # Стрілки вставки в різні TU
    f.append(text(300, 195, "повторний синтаксичний розбір N разів", size=11, color=POS, bold=True))
    f.append(arrow(150, 208, 130, 245, color=POS))
    f.append(arrow(300, 208, 300, 245, color=POS))
    f.append(arrow(450, 208, 470, 245, color=POS))

    f.append(fitbox(60, 250, 140, 95, "Одиниця A.cpp\n\nрозбір 50k рядків\nмакроси активні", size=11, fill=DIE, stroke=POS))
    f.append(fitbox(230, 250, 140, 95, "Одиниця B.cpp\n\nрозбір 50k рядків\nризик ODR", size=11, fill=DIE, stroke=POS))
    f.append(fitbox(400, 250, 140, 95, "Одиниця C.cpp\n\nрозбір 50k рядків\nконфлікт імен", size=11, fill=DIE, stroke=POS))

    f.append(text(300, 385, "• Повторний парсинг одного й того самого AST у сотнях файлів", size=12, color=INK, anchor="middle"))
    f.append(text(300, 412, "• Макроси забруднюють увесь наступний код у файлі", size=12, color=INK, anchor="middle"))
    f.append(text(300, 439, "• Порядок вкладення #include може зламати збірку", size=12, color=INK, anchor="middle"))

    # Розділювач
    f.append(line(600, 35, 600, 465, color=MUTED, sw=1, dash="6 5"))

    # Права колонка: Семантичний імпорт модулів (C++20)
    f.append(text(920, 48, "Семантичний імпорт модулів (import)", size=16, bold=True, color=FIELD))
    f.append(text(920, 72, "Ізольована компіляція інтерфейсу в типізоване бінарне дерево (BMI)", size=12, color=MUTED))

    f.append(fitbox(680, 100, 480, 75,
                    "Інтерфейс модуля (math.cppm)\nexport module math;\nexport struct Record { int id; };\n// Ізольована одиниця трансляції",
                    size=12, fill=LIVE, stroke=FIELD))

    # Компіляція інтерфейсу в BMI
    f.append(arrow(920, 180, 920, 230, color=FIELD))
    f.append(text(920, 205, "компілюється один раз", size=11, color=FIELD, bold=True))

    f.append(fitbox(780, 235, 280, 55, "Бінарний інтерфейс (BMI)\nmath.pcm / math.ifc (AST без макросів)", size=12, fill=COLD, stroke=NEG))

    # Стрілки завантаження BMI
    f.append(arrow(830, 295, 750, 345, color=FIELD))
    f.append(arrow(920, 295, 920, 345, color=FIELD))
    f.append(arrow(1010, 295, 1090, 345, color=FIELD))

    f.append(fitbox(680, 350, 140, 75, "Споживач A.cpp\nimport math;\nмиттєвий імпорт", size=11, fill=LIVE, stroke=FIELD))
    f.append(fitbox(850, 350, 140, 75, "Споживач B.cpp\nimport math;\nізольований стан", size=11, fill=LIVE, stroke=FIELD))
    f.append(fitbox(1020, 350, 140, 75, "Споживач C.cpp\nimport math;\nнуль витоків", size=11, fill=LIVE, stroke=FIELD))

    f.append(text(920, 448, "• Нульове дублювання синтаксичного розбору • Макроси не виходять назовні", size=12, color=FIELD, bold=True, anchor="middle"))

    render(os.path.join(OUT, 'include-vs-import.svg'), W, H, *f,
           title="Текстова модель include проти семантичного імпорту модулів")


# ── 2. Анатомія модульних одиниць і розділів ────────────────────────────────
def fig_module_units_and_partitions():
    W, H = 1240, 520
    f = []

    f.append(text(620, 42, "Архітектура модуля: одиниці трансляції, розділи та межі експорту", size=16, bold=True))
    f.append(text(620, 68, "Як логічний модуль збирається з інтерфейсних файлів, розділів і внутрішньої реалізації", size=12, color=MUTED))

    # Зовнішній споживач
    f.append(fitbox(70, 220, 180, 100, "Зовнішній клієнт\nmain.cpp\n\nimport engine;\n// Бачить лише export", size=12, fill=WARN, stroke=LINE))

    f.append(arrow(255, 270, 335, 270, color=LINE))
    f.append(text(295, 255, "import", size=12, bold=True))

    # Велика рамка модуля engine
    f.append(rect(340, 95, 840, 400, fill="#fcfdfe", stroke=FIELD, sw=2, rx=8))
    f.append(text(360, 122, "Межі модуля engine (Module Purview)", size=14, bold=True, color=FIELD, anchor="start"))

    # Головна інтерфейсна одиниця (Primary Module Interface)
    f.append(fitbox(370, 145, 360, 140,
                    "Головний інтерфейс (engine.cppm)\n\nexport module engine;\nexport import :geometry;\nimport :internals;\n\nexport void run_engine();",
                    size=12, fill=LIVE, stroke=FIELD))

    # Інтерфейсний розділ (Interface Partition)
    f.append(fitbox(780, 145, 370, 110,
                    "Інтерфейсний розділ (:geometry)\nengine-geometry.cppm\n\nexport module engine:geometry;\nexport struct Vector3 { float x, y, z; };",
                    size=12, fill=LIVE, stroke=FIELD))

    # Внутрішній розділ реалізації (Internal Partition)
    f.append(fitbox(780, 280, 370, 100,
                    "Внутрішній розділ (:internals)\nengine-internals.cppm\n\nmodule engine:internals;\nvoid allocate_pool(size_t sz);",
                    size=12, fill=COLD, stroke=NEG))

    # Одиниця реалізації модуля (Module Implementation Unit)
    f.append(fitbox(370, 320, 360, 100,
                    "Одиниця реалізації (engine.cpp)\n\nmodule engine;\n// Бачить усі оголошення engine\nvoid run_engine() { /* ... */ }",
                    size=12, fill=COLD, stroke=NEG))

    # Приватний фрагмент (Private Module Fragment)
    f.append(fitbox(370, 435, 780, 50,
                    "Приватний фрагмент (module :private;) — опціональний хвіст головного інтерфейсу без перекомпіляції BMI",
                    size=11, fill="#f5f5f5", stroke=MUTED))

    # Зв'язки між розділами
    f.append(arrow(735, 185, 775, 185, color=FIELD))
    f.append(text(755, 172, "експорт", size=10, color=FIELD))

    f.append(arrow(735, 235, 775, 320, color=NEG))
    f.append(text(755, 275, "внутрішній", size=10, color=NEG))

    render(os.path.join(OUT, 'module-units-and-partitions.svg'), W, H, *f,
           title="Анатомія модульних одиниць і розділів C++20")


# ── 3. Видимість (Visibility) проти Досяжності (Reachability) ──────────────
def fig_visibility_vs_reachability():
    W, H = 1240, 480
    f = []

    f.append(text(620, 45, "Видимість імені (Visibility) проти Досяжності типу (Reachability)", size=16, bold=True))
    f.append(text(620, 70, "Чому тип може бути повністю відомим компілятору, хоча його назву заборонено писати в коді", size=12, color=MUTED))

    # Ліворуч: Всередині модуля
    f.append(text(300, 110, "Оголошення всередині модуля network", size=14, bold=True, color=FIELD))
    f.append(fitbox(60, 130, 480, 180,
                    "export module network;\n\n// 1. Неекспортований внутрішній тип\nstruct SocketHandle {\n    int fd;\n    void send_bytes(const char* data, int len);\n};\n\n// 2. Експортована фабрична функція\nexport SocketHandle open_socket(const char* url);",
                    size=12, fill=COLD, stroke=FIELD))

    f.append(text(300, 340, "SocketHandle НЕ позначено як export", size=12, bold=True, color=POS))
    f.append(text(300, 365, "Його ім'я залишається невидимим поза модулем", size=12, color=MUTED))

    # Стрілка експорту фабрики
    f.append(arrow(545, 240, 695, 240, color=FIELD, sw=2))
    f.append(text(620, 220, "import network;", size=12, bold=True, color=FIELD))

    # Праворуч: Споживач модуля
    f.append(text(940, 110, "Поведінка в коді клієнта (main.cpp)", size=14, bold=True, color=INK))

    # Блок НЕВИДИМОСТІ імені
    f.append(fitbox(700, 130, 480, 85,
                    "// ❌ НЕВИДИМІСТЬ (Visibility: False)\nSocketHandle sock = open_socket(\"...\");\n// Помилка: ім'я 'SocketHandle' не знайдено в таблиці імен",
                    size=12, fill=DIE, stroke=POS))

    # Блок ДОСЯЖНОСТІ типу
    f.append(fitbox(700, 230, 480, 125,
                    "//  ДОСЯЖНІСТЬ (Reachability: True)\nauto sock = open_socket(\"...\"); // Тип виведено через auto\nsock.send_bytes(\"ping\", 4);     // OK! Методи й поля відомі\nsize_t sz = sizeof(sock);       // OK! Розмір структури відомий",
                    size=12, fill=LIVE, stroke=FIELD))

    f.append(text(940, 390, "Компілятор володіє повним макетом типу (розмір, вирівнювання, vtable, методи),", size=12, bold=True))
    f.append(text(940, 415, "але лексичний пошук імен (Name Lookup) блокує пряме використання неекспортованого ідентифікатора.", size=12, color=MUTED))

    render(os.path.join(OUT, 'visibility-vs-reachability.svg'), W, H, *f,
           title="Видимість імені проти досяжності типу")


# ── 4. Граф збірки та динамічне сканування залежностей (P1689R5) ───────────
def fig_bmi_build_graph():
    W, H = 1240, 490
    f = []

    f.append(text(620, 42, "Конвеєр збірки модулів: динамічне сканування (P1689R5) та топологічний порядок", size=16, bold=True))
    f.append(text(620, 68, "Чому бінарний інтерфейс (BMI) мусить бути згенерований раніше, ніж почнеться компіляція споживача", size=12, color=MUTED))

    # Фаза 1: Джерела
    f.append(fitbox(50, 110, 180, 240,
                    "1. Джерельні файли\n\nmath.cppm\n(export module math;)\n\nengine.cppm\n(import math;)\n\napp.cpp\n(import engine;)",
                    size=12, fill=FILL, stroke=LINE))

    f.append(arrow(235, 230, 295, 230, color=LINE))

    # Фаза 2: Швидке сканування залежностей
    f.append(fitbox(300, 110, 230, 240,
                    "2. Сканування (Scan)\nКомпілятор: -scan-deps\n\nШвидкий препроцесорний\nпрохід шукає 'import' та\n'export module' без повної\nгенерації коду.\n\nФормує JSON за P1689R5",
                    size=12, fill=WARN, stroke=POS))

    f.append(arrow(535, 230, 595, 230, color=LINE))

    # Фаза 3: Генератор системи збірки (CMake / Ninja dyndep)
    f.append(fitbox(600, 110, 240, 240,
                    "3. Граф робіт (Ninja)\n\nТопологічне сортування:\n\n1) Збірка math.pcm (BMI)\n2) Збірка engine.pcm\n   (вимагає math.pcm)\n3) Збірка app.o\n   (вимагає engine.pcm)",
                    size=12, fill=COLD, stroke=NEG))

    f.append(arrow(845, 230, 905, 230, color=LINE))

    # Фаза 4: Двоетапна генерація об'єктів
    f.append(fitbox(910, 110, 280, 240,
                    "4. Виконання компіляції\n\nКрок A: Генерація BMI\nmath.pcm -> engine.pcm\n\nКрок B: Компіляція коду\nmath.o, engine.o, app.o\n(може йти паралельно)\n\nКрок C: Лінкування\napp (виконуваний бінарник)",
                    size=12, fill=LIVE, stroke=FIELD))

    # Пояснювальний підсумок знизу
    f.append(rect(50, 385, 1140, 70, fill="#fafbfc", stroke=MUTED, sw=1, rx=6))
    f.append(text(620, 412, "Ключова зміна: у класичному C++ усі .cpp компілювалися повністю паралельно без взаємного очікування.", size=12, bold=True, color=INK))
    f.append(text(620, 436, "У модульному C++ поява бінарного інтерфейсу (BMI) вводить строгий порядок компіляції інтерфейсів до споживачів.", size=12, color=MUTED))

    render(os.path.join(OUT, 'bmi-build-graph.svg'), W, H, *f,
           title="Конвеєр збірки модулів C++20 та протокол P1689")


if __name__ == '__main__':
    fig_include_vs_import()
    fig_module_units_and_partitions()
    fig_visibility_vs_reachability()
    fig_bmi_build_graph()
    print("Фігури успішно згенеровано у", OUT)
