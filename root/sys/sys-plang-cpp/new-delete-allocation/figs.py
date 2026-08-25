# -*- coding: utf-8 -*-
"""Фігури теми «new, delete й шляхи виділення пам'яті»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_new_two_phases():
    """Двофазна природа виразу new: виділення пам'яті та виклик конструктора з відкатом."""
    W, H = 940, 480
    f = []

    f.append(fitbox(40, 20, 860, 42, "Вираз new T(args...): що генерує компілятор під капотом",
                    size=16, bold=True, fill="#eef2f7", stroke=MUTED, color=MUTED))

    # Фаза 1: Виділення пам'яті
    f.append(fitbox(50, 95, 240, 52, "Фаза 1: Отримання пам'яті\nvoid* raw = operator new(sizeof(T))",
                    size=12, bold=True, fill="#e8f4fd", stroke="#1976d2", color="#0d47a1"))

    f.append(arrow(290, 121, 340, 121, color=INK, sw=1.6))

    # Перевірка на успіх
    f.append(fitbox(345, 95, 180, 52, "Пам'ять успішно\nвиділено?",
                    size=12, bold=True, fill=BG, stroke=LINE))

    # Гілка невдачі Фази 1
    f.append(arrow(435, 147, 435, 205, color=POS, sw=1.6))
    f.append(fitbox(320, 210, 230, 48, "Викид std::bad_alloc\n(або nullptr для std::nothrow)",
                    size=11, fill="#fdecea", stroke=POS, color=POS))

    # Гілка успіху Фази 1 -> Фаза 2
    f.append(arrow(525, 121, 575, 121, color=FIELD, sw=1.6))
    f.append(text(550, 110, "Так", size=12, color=FIELD, bold=True))

    # Фаза 2: Конструктор
    f.append(fitbox(580, 95, 310, 52, "Фаза 2: Ініціалізація об'єкта\nвиклик конструктора T::T(raw, args...)",
                    size=12, bold=True, fill="#eef7ee", stroke=FIELD, color=FIELD))

    # Результат Фази 2: Успіх
    f.append(arrow(735, 147, 735, 225, color=FIELD, sw=1.6))
    f.append(fitbox(610, 230, 250, 54, "Успіх: час життя об'єкта почався\nповернення T* клієнту",
                    size=12, bold=True, fill="#eef7ee", stroke=FIELD, color=FIELD))

    # Відкат при винятку в конструкторі
    f.append(line(890, 121, 915, 121, color=POS, sw=1.6))
    f.append(line(915, 121, 915, 340, color=POS, sw=1.6))
    f.append(arrow(915, 340, 785, 340, color=POS, sw=1.6))
    f.append(text(855, 328, "Виняток!", size=12, color=POS, bold=True))

    f.append(fitbox(500, 315, 275, 55, "Автоматичний відкат компілятора:\nвиклик operator delete(raw)\nта ретрансляція винятку",
                    size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))

    # Пояснювальний підсумок знизу
    f.append(fitbox(40, 395, 860, 60,
                    "Вираз new неподільний у синтаксисі, але строго двоетапний під час виконання.\n"
                    "Якщо конструктор завершується аварійно, компілятор сам звільняє сиру пам'ять, запобігаючи витоку.",
                    size=12, fill=BG, stroke=MUTED, color=INK))

    render(os.path.join(IMG, 'new-two-phases.svg'), W, H, *f,
           title="Двофазне виконання виразу new")


def fig_delete_two_phases():
    """Двофазна природа виразу delete: перевірка nullptr, деструктор і деалокація."""
    W, H = 940, 420
    f = []

    f.append(fitbox(40, 20, 860, 42, "Вираз delete ptr: послідовність руйнування та звільнення",
                    size=16, bold=True, fill="#eef2f7", stroke=MUTED, color=MUTED))

    # Перевірка на nullptr
    f.append(fitbox(50, 90, 210, 52, "Перевірка вказівника:\nptr == nullptr ?",
                    size=12, bold=True, fill=BG, stroke=LINE))

    # Гілка nullptr
    f.append(arrow(155, 142, 155, 215, color=MUTED, sw=1.6))
    f.append(text(175, 178, "Так", size=12, color=MUTED))
    f.append(fitbox(60, 220, 190, 46, "Безпечний вихід (no-op)\nжодних дій не виконується",
                    size=11, fill="#f5f5f5", stroke=MUTED, color=MUTED))

    # Гілка не nullptr -> Фаза 1
    f.append(arrow(260, 116, 315, 116, color=FIELD, sw=1.6))
    f.append(text(285, 107, "Ні", size=12, color=FIELD, bold=True))

    # Фаза 1: Деструктор
    f.append(fitbox(320, 90, 265, 52, "Фаза 1: Знищення об'єкта\nвиклик ptr->~T()\n(кінець часу життя об'єкта)",
                    size=12, bold=True, fill="#fdecea", stroke=POS, color=POS))

    f.append(arrow(585, 116, 640, 116, color=INK, sw=1.6))

    # Фаза 2: operator delete
    f.append(fitbox(645, 90, 255, 52, "Фаза 2: Повернення пам'яті\noperator delete(ptr)\nабо sized delete (C++14)",
                    size=12, bold=True, fill="#e8f4fd", stroke="#1976d2", color="#0d47a1"))

    # Стан після виконання
    f.append(arrow(772, 142, 772, 215, color=POS, sw=1.6))
    f.append(fitbox(635, 220, 275, 54, "Пам'ять повернено алокатору.\nВказівник ptr стає висячим (dangling)!",
                    size=11, bold=True, fill="#fff3e0", stroke="#f57c00", color="#e65100"))

    # Підсумок
    f.append(fitbox(40, 325, 860, 65,
                    "Деструктор завершує час життя об'єкта до того, як байти повертаються в купу.\n"
                    "Перевірка на nullptr гарантована стандартом: виклик delete nullptr є повністю безпечним.",
                    size=12, fill=BG, stroke=MUTED, color=INK))

    render(os.path.join(IMG, 'delete-two-phases.svg'), W, H, *f,
           title="Двофазне виконання виразу delete")


def fig_array_cookie_layout():
    """Розкладка масиву в пам'яті: Array Cookie та невідповідність new[] і delete."""
    W, H = 940, 480
    f = []

    f.append(fitbox(40, 20, 860, 40, "Розкладка масиву new Widget[4] у динамічній пам'яті (Itanium ABI)",
                    size=15, bold=True, fill="#eef2f7", stroke=MUTED, color=MUTED))

    # Вказівники над пам'яттю
    f.append(fitbox(30, 75, 150, 40, "p_raw (початок)\nвід operator new[]",
                    size=11, fill="#e8f4fd", stroke="#1976d2", color="#0d47a1"))

    f.append(fitbox(200, 75, 160, 40, "p_user = p_raw + 8\nповертається клієнту",
                    size=11, bold=True, fill="#eef7ee", stroke=FIELD, color=FIELD))

    f.append(arrow(105, 115, 105, 155, color="#1976d2", sw=2))
    f.append(arrow(240, 115, 240, 155, color=FIELD, sw=2))

    # Блоки пам'яті
    f.append(rect(100, 160, 740, 65, fill="#fafafa", stroke=LINE, sw=1.5))

    # Cookie
    f.append(rect(100, 160, 140, 65, fill="#fff3e0", stroke="#f57c00", sw=2))
    f.append(text(170, 185, "Cookie (8 байтів)", size=13, color="#e65100", bold=True))
    f.append(text(170, 206, "Лічильник: N = 4", size=12, color="#e65100"))

    # Елементи
    colors = ["#eef7ee", "#e8f4fd", "#eef7ee", "#e8f4fd"]
    for i in range(4):
        x = 240 + i * 150
        f.append(rect(x, 160, 150, 65, fill=colors[i], stroke=FIELD, sw=1.5))
        f.append(text(x + 75, 185, f"Widget[{i}]", size=13, color=FIELD, bold=True))
        f.append(text(x + 75, 206, "sizeof(Widget)", size=11, color=MUTED))

    # Секція небезпеки: delete vs delete[]
    f.append(fitbox(40, 245, 410, 105,
                    "Правильно: delete[] p_user\n"
                    "1. Зчитує N = 4 із позиції (p_user - 8)\n"
                    "2. Викликає Widget::~Widget() для [3], [2], [1], [0]\n"
                    "3. Передає адресу p_raw у operator delete[]",
                    size=11, fill="#eef7ee", stroke=FIELD, color=FIELD))

    f.append(fitbox(470, 245, 430, 105,
                    "Катастрофа: непарний delete p_user (UB!)\n"
                    "✖ Викликає деструктор ЛИШЕ для Widget[0]\n"
                    "✖ Деструктори Widget[1..3] НЕ викликаються (витік ресурсів!)\n"
                    "✖ Передає p_user замість p_raw у heap allocator -> крах купи!",
                    size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))

    # Підсумок знизу
    f.append(fitbox(40, 370, 860, 85,
                    "Array Cookie зберігає кількість елементів для коректного виклику всіх деструкторів.\n"
                    "Зсув покажчика робить виклики new[] і delete несумісними на рівні пам'яті:\n"
                    "алокатор отримує невірну адресу блоку, що призводить до негайного пошкодження купи.",
                    size=12, fill=BG, stroke=MUTED, color=INK))

    render(os.path.join(IMG, 'array-cookie-layout.svg'), W, H, *f,
           title="Розкладка пам'яті масиву й небезпека непарного delete")


def fig_sized_delete_lookup():
    """Порівняння звичайного delete та C++14 Sized Delete."""
    W, H = 940, 420
    f = []

    f.append(fitbox(40, 20, 860, 40, "Еволюція деалокації: класичний delete (C++98) проти Sized Delete (C++14)",
                    size=15, bold=True, fill="#eef2f7", stroke=MUTED, color=MUTED))

    # Ліва колонка: До C++14
    f.append(fitbox(60, 75, 380, 38, "До C++14: operator delete(void* ptr)",
                    size=13, bold=True, fill="#fff3e0", stroke="#f57c00", color="#e65100"))

    f.append(fitbox(60, 125, 380, 48, "1. Компілятор викликає ptr->~T()\n2. Викликає operator delete(ptr) без розміру",
                    size=12, fill=BG, stroke=LINE))

    f.append(fitbox(60, 185, 380, 95, "Алокатор пам'яті (tcmalloc / jemalloc):\n"
                                       "• Мусить читати заголовок сторінки / метадані\n"
                                       "• Визначає, до якого розмірного класу належав ptr\n"
                                       "• Зайвий промах повз кеш (cache miss) у гарячому коді",
                    size=11, fill="#fdecea", stroke=POS, color=POS))

    # Права колонка: C++14 Sized Delete
    f.append(fitbox(500, 75, 380, 38, "C++14: operator delete(void* ptr, std::size_t size)",
                    size=13, bold=True, fill="#eef7ee", stroke=FIELD, color=FIELD))

    f.append(fitbox(500, 125, 380, 48, "1. Компілятор викликає ptr->~T()\n2. Знає sizeof(T) статично -> передає розмір одразу!",
                    size=12, fill=BG, stroke=LINE))

    f.append(fitbox(500, 185, 380, 95, "Алокатор пам'яті (Slab / Size-class aware):\n"
                                       "• Миттєво знаходить потрібний bin / freelist за size\n"
                                       "• Нуль звернень до метаданих у пам'яті\n"
                                       "• Суттєве прискорення викликів deallocate у навантажених системах",
                    size=11, fill="#eef7ee", stroke=FIELD, color=FIELD))

    # Підсумок знизу
    f.append(fitbox(40, 305, 860, 85,
                    "Компілятор під час компіляції знає точний розмір повного типу sizeof(T).\n"
                    "Sized delete у C++14 передає це знання в алокатор безкоштовно,\n"
                    "усуваючи накладні витрати на пошук розміру чанка в таблицях купи.",
                    size=12, fill=BG, stroke=MUTED, color=INK))

    render(os.path.join(IMG, 'sized-delete-lookup.svg'), W, H, *f,
           title="Sized delete у C++14: оптимізація повернення пам'яті")


def fig_make_unique_exception_safety():
    """Безпека винятків: витік пам'яті при сирому new проти std::make_unique."""
    W, H = 940, 450
    f = []

    f.append(fitbox(40, 20, 860, 40, "Чому вираз new у викликах функцій небезпечний до C++17",
                    size=15, bold=True, fill="#eef2f7", stroke=MUTED, color=MUTED))

    # Приклад коду
    f.append(fitbox(60, 75, 820, 36, "process(std::unique_ptr<A>(new A()), std::unique_ptr<B>(new B()));",
                    size=13, bold=True, fill="#2b303c", stroke=LINE, color="#f8f8f2"))

    # Порядок обчислення до C++17
    f.append(fitbox(60, 125, 820, 105,
                    "Один із дозволених стандартів порядку чергування інструкцій компілятором:\n"
                    "1. operator new(sizeof(A)) -> успіх, пам'ять виділено\n"
                    "2. operator new(sizeof(B)) -> успіх, пам'ять виділено\n"
                    "3. Конструктор A::A() -> успіх\n"
                    "4. Конструктор B::B() -> ВИКИДАЄ ВИНЯТОК! 💥",
                    size=12, fill="#fff3e0", stroke="#f57c00", color="#e65100"))

    # Наслідок
    f.append(fitbox(60, 245, 395, 85,
                    "Наслідок аварії:\n"
                    "• Пам'ять під B очиститься автоматичним відкатом\n"
                    "• std::unique_ptr<A> ЩЕ НЕ СТВОРЕНО!\n"
                    "• Об'єкт A і його пам'ять втрачено назавжди (витік пам'яті!).",
                    size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))

    # Рішення make_unique
    f.append(fitbox(485, 245, 395, 85,
                    "Рішення: std::make_unique<T>()\n"
                    "process(std::make_unique<A>(), std::make_unique<B>());\n"
                    "Виділення та передача володіння в RAII-обгортку неподільні (атомарні) в межах одного виклику функції.",
                    size=11, bold=True, fill="#eef7ee", stroke=FIELD, color=FIELD))

    # Підсумок знизу
    f.append(fitbox(40, 350, 860, 75,
                    "Сирий new залишає небезпечну часову щілину між виділенням ресурсу й передачею його розумному покажчику.\n"
                    "Фабричні функції std::make_unique та std::make_shared гарантують повну виняткобезпеку за будь-яких умов.",
                    size=12, fill=BG, stroke=MUTED, color=INK))

    render(os.path.join(IMG, 'make-unique-exception-safety.svg'), W, H, *f,
           title="Виняткобезпека: пастка виклику з сирим new та захист std::make_unique")


def main():
    fig_new_two_phases()
    fig_delete_two_phases()
    fig_array_cookie_layout()
    fig_sized_delete_lookup()
    fig_make_unique_exception_safety()
    print("Всі фігури згенеровано успішно.")


if __name__ == '__main__':
    main()
