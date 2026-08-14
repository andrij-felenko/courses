# -*- coding: utf-8 -*-
"""Фігури до теми «Ієрархія стандартних винятків у C++»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Ієрархічне дерево класів std::exception ────────────────────────────
def fig_std_exception_tree():
    W, H = 940, 520
    f = []

    f.append(text(470, 30, "Ієрархія стандартних класів винятків C++ (std::exception)", size=16, color=INK, anchor="middle", bold=True))

    # Базовий клас std::exception
    f.append(fitbox(370, 55, 200, 55,
                    "std::exception\n"
                    "virtual what() const noexcept\n"
                    "virtual ~exception() noexcept",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Лінії від std::exception до основних гілок
    f.append(line(470, 110, 470, 130, color=LINE, sw=2))
    f.append(line(135, 130, 805, 130, color=LINE, sw=2))

    # Вертикальні відгалуження
    f.append(arrow(135, 130, 135, 150, color=LINE, sw=2))
    f.append(arrow(345, 130, 345, 150, color=LINE, sw=2))
    f.append(arrow(580, 130, 580, 150, color=LINE, sw=2))
    f.append(arrow(805, 130, 805, 150, color=LINE, sw=2))

    # Гілка 1: std::logic_error
    f.append(fitbox(45, 155, 180, 50,
                    "std::logic_error\n"
                    "Помилки в логіці програми",
                    size=11, fill="#eef2f7", stroke=LINE))

    f.append(line(135, 205, 135, 225, color=LINE, sw=1.5))
    f.append(fitbox(20, 230, 230, 125,
                    "• std::invalid_argument\n"
                    "• std::domain_error\n"
                    "• std::length_error\n"
                    "• std::out_of_range\n"
                    "• std::future_error (C++11)",
                    size=10, fill="#f4f6f8", stroke=LINE))

    # Гілка 2: std::runtime_error
    f.append(fitbox(255, 155, 180, 50,
                    "std::runtime_error\n"
                    "Збої зовнішнього середовища",
                    size=11, fill="#fff7e6", stroke=POS))

    f.append(line(345, 205, 345, 225, color=LINE, sw=1.5))
    f.append(fitbox(235, 230, 220, 145,
                    "• std::range_error\n"
                    "• std::overflow_error\n"
                    "• std::underflow_error\n"
                    "• std::system_error (C++11)\n"
                    "  └─ std::filesystem_error (C++17)\n"
                    "• std::format_error (C++20)",
                    size=10, fill="#fffaf0", stroke=POS))

    # Гілка 3: Винятки виділення пам'яті та типів (bad_*)
    f.append(fitbox(490, 155, 180, 50,
                    "Низькорівневі bad_*\n"
                    "Пам'ять та тип-система",
                    size=11, fill="#fff0f0", stroke=NEG))

    f.append(line(580, 205, 580, 225, color=LINE, sw=1.5))
    f.append(fitbox(470, 230, 220, 135,
                    "• std::bad_alloc\n"
                    "  └─ bad_array_new_length\n"
                    "• std::bad_cast\n"
                    "• std::bad_typeid\n"
                    "• std::bad_exception",
                    size=10, fill="#fff5f5", stroke=NEG))

    # Гілка 4: Винятки обгорткових типів (bad_*_access)
    f.append(fitbox(715, 155, 180, 50,
                    "Контейнери bad_*_access\n"
                    "C++11 / C++17 / C++20",
                    size=11, fill="#f0edfe", stroke="#6b4cba"))

    f.append(line(805, 205, 805, 225, color=LINE, sw=1.5))
    f.append(fitbox(695, 230, 220, 135,
                    "• std::bad_optional_access\n"
                    "• std::bad_variant_access\n"
                    "• std::bad_any_cast\n"
                    "• std::bad_weak_ptr\n"
                    "• std::bad_function_call",
                    size=10, fill="#f8f6ff", stroke="#6b4cba"))

    # Пояснювальний підпис
    f.append(line(40, 480, 900, 480, color=MUTED, sw=1, dash="4 4"))
    f.append(text(470, 502, "logic_error передбачає можливість виправлення алгоритму; runtime_error описує події, непідконтрольні коду", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, 'std-exception-tree.svg'), W, H, *f,
           title="Ієрархія стандартних винятків C++")


# ── 2. Диспетчеризація поліморфного catch та зрізання об'єктів (slicing) ──
def fig_exception_dispatch_flow():
    W, H = 940, 440
    f = []

    f.append(text(470, 30, "Поліморфне перехоплення за посиланням проти зрізання об'єкта (Slicing)", size=16, color=INK, anchor="middle", bold=True))

    # Генерація винятку
    f.append(fitbox(330, 55, 280, 60,
                    "throw std::out_of_range(\"Index 5 out of bounds\");\n"
                    "Об'єкт створено у спеціальній зоні пам'яті EH",
                    size=11, fill="#eef2f7", stroke=LINE))

    # Розгалуження на два шляхи catch
    f.append(arrow(380, 115, 240, 160, color=FIELD, sw=2))
    f.append(arrow(580, 115, 700, 160, color=NEG, sw=2))

    f.append(text(280, 130, "Безпечний шлях (Посилання)", size=11, color=FIELD, bold=True))
    f.append(text(670, 130, "Небезпечний шлях (За значенням)", size=11, color=NEG, bold=True))

    # Шлях A: catch (const std::exception& e)
    f.append(fitbox(40, 165, 400, 120,
                    "catch (const std::exception& e)\n\n"
                    "• Зв'язується через const посилання на оригінал\n"
                    "• Таблиця vtable зберігає вихідний тип out_of_range\n"
                    "• e.what() повертає: \"Index 5 out of bounds\"\n"
                    "• Копіювання відсутнє (Нульовий оверхед)",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Шлях B: catch (std::exception e)
    f.append(fitbox(500, 165, 400, 120,
                    "catch (std::exception e)  // ⚠️ Object Slicing!\n\n"
                    "• Створюється копія лише базової частини std::exception\n"
                    "• Поле std::string із повідомленням ЗРІЗАЄТЬСЯ\n"
                    "• Таблиця vtable скидається до std::exception::vtable\n"
                    "• e.what() повертає банальне: \"std::exception\"",
                    size=11, fill="#fff0f0", stroke=NEG))

    # Висновки нижнього блоку
    f.append(fitbox(40, 310, 860, 95,
                    "ПРАВИЛО ПЕРЕХОПЛЕННЯ ВИНЯТКІВ У C++:\n"
                    "1. Завжди перехоплюйте винятки за константним посиланням: catch (const std::exception& e).\n"
                    "2. Розміщуйте блоки catch від найменш абстрактного (похідного) до найбільш абстрактного (базового).\n"
                    "3. Порушення порядку (наприклад, catch (const std::exception&) перед catch (const std::out_of_range&)) робить похідний блок недосяжним кодом.",
                    size=11, fill="#fffaf0", stroke=POS))

    render(os.path.join(OUT, 'exception-dispatch-flow.svg'), W, H, *f,
           title="Поліморфне перехоплення винятків та Slicing")


# ── 3. Макет пам'яті об'єкта винятку та std::system_error ─────────────────
def fig_exception_memory_layout():
    W, H = 940, 440
    f = []

    f.append(text(470, 30, "Макет пам'яті std::system_error та механізм зберігання what()", size=16, color=INK, anchor="middle", bold=True))

    # Схема об'єкта std::system_error
    f.append(text(50, 60, "Фізичне розміщення об'єкта std::system_error в EH-купі (Exception Heap):", size=13, color=INK, anchor="start", bold=True))

    f.append(fitbox(50, 85, 540, 200,
                    "┌─────────────────────────────────────────────────────────────┐\n"
                    "│ vptr ───► vtable (std::system_error)                       │\n"
                    "├─────────────────────────────────────────────────────────────┤\n"
                    "│ std::runtime_error payload: std::string what_buffer_        │\n"
                    "│  └─ ptr: 0x7f9a... ──► \"Network socket read failed: Connection reset\" │\n"
                    "├─────────────────────────────────────────────────────────────┤\n"
                    "│ std::error_code code_:                                      │\n"
                    "│  ├─ int val_ = 104 (ECONNRESET)                             │\n"
                    "│  └─ const std::error_category* cat_ ──► &system_category() │\n"
                    "└─────────────────────────────────────────────────────────────┘",
                    size=11, fill="#eef2f7", stroke=LINE))

    # Стрелки к дочерним структурам
    f.append(arrow(600, 180, 660, 180, color=FIELD, sw=2))

    f.append(fitbox(665, 85, 225, 200,
                    "Особливості роботи what():\n\n"
                    "• Повідомлення what() генерується\n"
                    "  ПІД ЧАС КОНСТРУЮВАННЯ.\n"
                    "• Конструктор форматує рядок:\n"
                    "  \"custom_prefix: error_message\".\n"
                    "• Метод what() повертає c_str()\n"
                    "  готового внутрішнього рядка.\n"
                    "• what() не виділяє пам'ять\n"
                    "  і має специфікатор noexcept!",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Пояснювальний блок для std::error_category
    f.append(fitbox(50, 305, 840, 100,
                    "ЧОМУ WHAT() МАЄ ГАРАНТІЮ NOEXCEPT:\n"
                    "Якщо під час обробки винятку (stack unwinding) метод what() кинув би власний виняток (наприклад, std::bad_alloc при спробі виділити пам'ять для std::string), середовище виконання C++ негайно викликає std::terminate(). Тому всі стандартні винятки зберігають буфер повідомлення заздалегідь або повертають статичні вказівники.",
                    size=11, fill="#fffaf0", stroke=POS))

    render(os.path.join(OUT, 'exception-memory-layout.svg'), W, H, *f,
           title="Макет пам'яті std::system_error")


def main():
    fig_std_exception_tree()
    fig_exception_dispatch_flow()
    fig_exception_memory_layout()
    print("Фігури успішно згенеровано.")

if __name__ == '__main__':
    main()
