# -*- coding: utf-8 -*-
"""Генератор діаграм для теми «Рефлексія й метапрограмування».
Використовує бібліотеку svgkit з кореневої папки scripts/.
"""

import sys
import os

# Додаємо шлях до scripts/ (чотири рівні вгору від book/programming/languages/reflection-metaprogramming/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_reflection_taxonomy():
    """1. Таксономія: інтроспекція, інтероспекція та метапрограмування (compile-time vs runtime)."""
    w, h = 920, 520
    frags = []

    frags.append(text(460, 28, "Класифікація механізмів рефлексії та метапрограмування", size=16, bold=True))

    # Вісь часу (вертикальний поділ або колонки)
    frags.append(rect(40, 55, 410, 440, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(rect(470, 55, 410, 440, fill="#f8fafc", stroke="#cbd5e1", rx=8))

    frags.append(text(245, 80, "Час компіляції (Compile-Time)", size=14, bold=True, color="#1e3a8a"))
    frags.append(text(675, 80, "Час виконання (Runtime)", size=14, bold=True, color="#14532d"))

    # Блоки для Compile-Time:
    # 1. Пасивний аналіз (Інтроспекція часу компіляції)
    frags.append(fitbox(55, 105, 380, 115,
                        "Інтроспекція часу компіляції\n\n"
                        "• C++ type traits (std::is_integral, void_t)\n"
                        "• C++20 Concepts (requires clauses)\n"
                        "• C++26 static reflection (^^, std::meta::info)\n"
                        "• Rust static type queries, TypeScript types",
                        size=11.5, fill="#eff6ff", stroke="#3b82f6", bold=False))

    # 2. Активна трансформація та генерація (Метапрограмування)
    frags.append(fitbox(55, 235, 380, 125,
                        "Синтаксичні макроси та генерація коду\n\n"
                        "• Lisp макроси (defmacro, homoiconicity)\n"
                        "• Rust macro_rules! та proc_macro_derive\n"
                        "• C++ Template Metaprogramming (SFINAE, if constexpr)\n"
                        "• Генератори збірки (Qt MOC, Protobuf, ANTLR)",
                        size=11.5, fill="#e0e7ff", stroke="#6366f1", bold=False))

    # 3. Вигода часу компіляції
    frags.append(fitbox(55, 375, 380, 105,
                        "Властивості підходу:\n"
                        "✔ 100% перевірка типів до запуску\n"
                        "✔ Повний інлайнінг та нульовий рантайм-оверхед\n"
                        "✖ Довший час збірки, роздування двійкового коду",
                        size=11, fill="#ecfdf5", stroke="#10b981", bold=False))

    # Блоки для Runtime:
    # 1. Пасивний аналіз (Динамічна інтроспекція)
    frags.append(fitbox(485, 105, 380, 115,
                        "Динамічна інтроспекція (Runtime Introspection)\n\n"
                        "• C++ RTTI (typeid, dynamic_cast, vtable)\n"
                        "• Java Reflection API (Class, Method, Field)\n"
                        "• C# System.Reflection (Type, PropertyInfo)\n"
                        "• Python hasattr(), getattr(), isinstance()",
                        size=11.5, fill="#f0fdf4", stroke="#22c55e", bold=False))

    # 2. Активна модифікація (Інтероспекція / Dynamic Dispatch)
    frags.append(fitbox(485, 235, 380, 125,
                        "Інтероспекція та динамічна поведінка\n\n"
                        "• Динамічний виклик методів (Method.invoke)\n"
                        "• Dynamic Proxy (java.lang.reflect.Proxy)\n"
                        "• Емісія байткоду (C# Reflection.Emit, Java cglib)\n"
                        "• Smalltalk Metaobject Protocol, Python Monkey Patching",
                        size=11.5, fill="#fefce8", stroke="#eab308", bold=False))

    # 3. Властивості рантайму
    frags.append(fitbox(485, 375, 380, 105,
                        "Властивості підходу:\n"
                        "✔ Динамічна конфігурація плагінів і JSON/ORM\n"
                        "✖ Накладні витрати CPU (boxing, no inlining)\n"
                        "✖ Ризик помилок у рантаймі (NoSuchMethodException)",
                        size=11, fill="#fff1f2", stroke="#f43f5e", bold=False))

    render(os.path.join(IMG_DIR, "reflection-taxonomy.svg"), w, h, *frags)


def fig_moc_pipeline():
    """2. Конвеєр генерації метаоб'єктів прекомпілятором Qt MOC."""
    w, h = 900, 460
    frags = []

    frags.append(text(450, 28, "Конвеєр створення метаоб'єктних таблиць (Qt MOC / Генератор коду)", size=16, bold=True))

    # 1. Вихідні файли розробника
    frags.append(fitbox(30, 65, 200, 90,
                        "Вихідний файл C++\n\n"
                        "class Device : public QObject {\n"
                        "    Q_OBJECT\n"
                        "    Q_PROPERTY(...)\n"
                        "signals: void ready();\n"
                        "};",
                        size=10.5, fill="#f8fafc", stroke="#475569", bold=False))

    # Стрілка від Header до MOC
    frags.append(arrow(230, 110, 280, 110, color=LINE, sw=2))

    # 2. Препроцесор MOC (Meta-Object Compiler)
    frags.append(fitbox(280, 65, 230, 90,
                        "Qt MOC (Прекомпілятор)\n\n"
                        "• Розбирає синтаксис C++\n"
                        "• Шукає макрос Q_OBJECT\n"
                        "• Витягує сигнали, слоти,\n"
                        "  властивості та типи",
                        size=11, fill="#fef3c7", stroke="#d97706", bold=True))

    # Стрілка від MOC до згенерованого файлу
    frags.append(arrow(510, 110, 560, 110, color=LINE, sw=2))

    # 3. Згенерований файл moc_*.cpp
    frags.append(fitbox(560, 65, 310, 90,
                        "Згенерований moc_device.cpp\n\n"
                        "• static const uint qt_meta_data[]\n"
                        "• static const char qt_meta_stringdata[]\n"
                        "• static void qt_static_metacall(...)\n"
                        "• Реалізація сигналів (emit ready)",
                        size=10.5, fill="#e0f2fe", stroke="#0284c7", bold=False))

    # Об'єднання в компіляторі C++
    frags.append(arrow(130, 155, 130, 230, color=LINE, sw=2))
    frags.append(arrow(130, 230, 310, 230, color=LINE, sw=2))

    frags.append(arrow(715, 155, 715, 230, color=LINE, sw=2))
    frags.append(arrow(715, 230, 590, 230, color=LINE, sw=2))

    # 4. Компілятор C++
    frags.append(fitbox(310, 195, 280, 70,
                        "Компілятор C++ (GCC / Clang / MSVC)\n\n"
                        "Компілює device.cpp + moc_device.cpp\n"
                        "у єдиний об'єктний код",
                        size=11.5, fill="#edf2f7", stroke="#334155", bold=True))

    # Стрілка вниз до лінкувальника / бінарника
    frags.append(arrow(450, 265, 450, 310, color=LINE, sw=2))

    # 5. Підсумковий виконуваний файл
    frags.append(fitbox(240, 310, 420, 120,
                        "Кінцевий бінарний образ (ELF / PE)\n\n"
                        "• Машинний код методів у секції .text\n"
                        "• Незмінні таблиці QMetaObject у секції .rodata\n"
                        "• Рефлексивний доступ: пошук методів за рядковим ім'ям,\n"
                        "  з'єднання сигналів зі слотами через числові індекси",
                        size=11.5, fill="#f0fdf4", stroke="#16a34a", bold=True))

    render(os.path.join(IMG_DIR, "moc-pipeline.svg"), w, h, *frags)


def fig_p2996_cycle():
    """3. Цикл статичної рефлексії та сплайсингу в C++26 (P2996)."""
    w, h = 920, 470
    frags = []

    frags.append(text(460, 28, "Цикл статичної рефлексії та сплайсингу (C++26 P2996)", size=16, bold=True))

    # 1. Вихідні типи
    frags.append(fitbox(30, 70, 230, 120,
                        "Вихідний тип C++\n\n"
                        "struct SensorData {\n"
                        "    int id;\n"
                        "    double value;\n"
                        "    bool valid;\n"
                        "};",
                        size=11, fill="#f1f5f9", stroke="#475569", bold=False))

    # Стрілка Рефлексії ^^
    frags.append(arrow(260, 130, 350, 130, color=LINE, sw=2))
    frags.append(text(305, 118, "Оператор ^^", size=11.5, color="#1e40af", bold=True))

    # 2. Метадані (std::meta::info)
    frags.append(fitbox(350, 70, 220, 120,
                        "Метадескриптор\nstd::meta::info\n\n"
                        "constexpr auto r =\n"
                        "    ^^SensorData;\n"
                        "(непрозоре представлення\n"
                        "вузла AST у компіляторі)",
                        size=11, fill="#eff6ff", stroke="#3b82f6", bold=False))

    # Стрілка до Constexpr алгоритму
    frags.append(arrow(460, 190, 460, 240, color=LINE, sw=2))
    frags.append(text(460, 225, "std::meta::members_of()", size=11, color="#7c3aed", bold=True))

    # 3. Constexpr / Consteval обробка
    frags.append(fitbox(280, 245, 360, 95,
                        "Обчислення в компіляторі (CTFE / constexpr)\n\n"
                        "• Фільтрація нестатичних полів\n"
                        "• Отримання імен (name_of) та типів (type_of)\n"
                        "• Формування коду серіалізації/валідації",
                        size=11, fill="#f5f3ff", stroke="#8b5cf6", bold=True))

    # Стрілка Сплайсингу [: ... :]
    frags.append(arrow(640, 295, 690, 295, color=LINE, sw=2))
    frags.append(mtext(665, 260, ["Сплайсинг", "[: ... :]"], size=11, color="#b91c1c", bold=True))

    # 4. Згенерований код у AST
    frags.append(fitbox(690, 230, 200, 125,
                        "Ін'єкція в AST\n\n"
                        "auto to_json(const auto& s) {\n"
                        "    // Цикл розгортається\n"
                        "    json_write(s.[:m:]);\n"
                        "}\n"
                        "(прямий доступ до полів)",
                        size=10.5, fill="#fef2f2", stroke="#ef4444", bold=False))

    # 5. Підсумковий машинний код
    frags.append(arrow(790, 355, 790, 395, color=LINE, sw=2))
    frags.append(arrow(790, 395, 590, 395, color=LINE, sw=2))

    frags.append(fitbox(170, 365, 420, 75,
                        "Кінцевий машинний код цільового процесора\n\n"
                        "• Повний інлайнінг звернень до пам'яті: mov, ldr, str\n"
                        "• Нуль таблиць метаданих у RAM, нуль непрямих викликів",
                        size=11.5, fill="#f0fdf4", stroke="#15803d", bold=True))

    render(os.path.join(IMG_DIR, "p2996-reflection-cycle.svg"), w, h, *frags)


def fig_reflection_overhead():
    """4. Порівняння витрат виконання: прямий виклик, віртуальний виклик та рефлексія."""
    w, h = 920, 480
    frags = []

    frags.append(text(460, 28, "Порівняння конвеєра виконання: прямий виклик, vtable та рефлексія", size=16, bold=True))

    # 3 паралельні доріжки
    # 1. Прямий інлайнований виклик
    frags.append(rect(30, 60, 260, 390, fill="#f0fdf4", stroke="#86efac", rx=8))
    frags.append(text(160, 85, "1. Прямий / Inline виклик", size=13, bold=True, color="#166534"))

    frags.append(fitbox(45, 110, 230, 70, "Код виклику:\nobj.calculate(42);", size=11, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(arrow(160, 180, 160, 220, color=LINE, sw=1.5))
    frags.append(fitbox(45, 220, 230, 90, "Машинний код CPU:\n\n• Інструкції повністю інлайняться\n• Аргументи в регістрах CPU\n• Час: ~0–0.5 нс (0 тактів затримки)", size=10.5, fill="#ffffff", stroke="#16a34a"))
    frags.append(arrow(160, 310, 160, 350, color=LINE, sw=1.5))
    frags.append(fitbox(45, 350, 230, 85, "Підсумок:\n✔ Максимальна швидкість\n✔ Оптимізація конвеєра CPU\n✔ Нуль алокацій пам'яті", size=10.5, fill="#dcfce7", stroke="#22c55e", bold=True))

    # 2. Поліморфний виклик через vtable
    frags.append(rect(320, 60, 270, 390, fill="#eff6ff", stroke="#93c5fd", rx=8))
    frags.append(text(455, 85, "2. Віртуальний виклик (vtable)", size=13, bold=True, color="#1e40af"))

    frags.append(fitbox(335, 110, 240, 70, "Код виклику:\nbase_ptr->calculate(42);", size=11, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(arrow(455, 180, 455, 220, color=LINE, sw=1.5))
    frags.append(fitbox(335, 220, 240, 90, "Машинний код CPU:\n\n1. Читання vptr з об'єкта\n2. Читання адреси методу з vtable\n3. Непрямий перехід (call [rax+24])\n• Час: ~1–3 нс", size=10.5, fill="#ffffff", stroke="#2563eb"))
    frags.append(arrow(455, 310, 455, 350, color=LINE, sw=1.5))
    frags.append(fitbox(335, 350, 240, 85, "Підсумок:\n✔ Динамічний поліморфізм\n✖ Непрямий виклик (missed inline)\n✖ +8 байт на покажчик vptr", size=10.5, fill="#dbeafe", stroke="#3b82f6", bold=True))

    # 3. Виклик через рефлексію в рантаймі
    frags.append(rect(620, 60, 270, 390, fill="#fff1f2", stroke="#fda4af", rx=8))
    frags.append(text(755, 85, "3. Динамічна рефлексія", size=13, bold=True, color="#9f1239"))

    frags.append(fitbox(635, 110, 240, 70, "Код виклику:\nmethod.invoke(obj, new Object[]{42});", size=10, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(arrow(755, 180, 755, 205, color=LINE, sw=1.5))
    frags.append(fitbox(635, 205, 240, 130, "Конвеєр JVM / CLR / Dynamic:\n\n1. Пакування аргументів (boxing: int -> Integer)\n2. Створення масиву Object[] у купі\n3. Перевірка прав доступу (security check)\n4. Валідація типів параметрів\n5. Непрямий виклик через native stub\n6. Розпакування результату (unboxing)\n• Час: ~15–60 нс (до 100x повільніше)", size=9.5, fill="#ffffff", stroke="#e11d48"))
    frags.append(arrow(755, 335, 755, 350, color=LINE, sw=1.5))
    frags.append(fitbox(635, 350, 240, 85, "Підсумок:\n✔ Максимальна гнучкість у рантаймі\n✖ Високе навантаження на GC та CPU\n✖ Повна втрата типобезпеки компілятора", size=10, fill="#ffe4e6", stroke="#f43f5e", bold=True))

    render(os.path.join(IMG_DIR, "reflection-call-overhead.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_reflection_taxonomy()
    fig_moc_pipeline()
    fig_p2996_cycle()
    fig_reflection_overhead()
    print("Всі фігури успішно згенеровано.")
