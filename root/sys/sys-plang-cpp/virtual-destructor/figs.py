# -*- coding: utf-8 -*-
"""Фігури теми «Віртуальний деструктор і поліморфне видалення»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_slicing_and_leak_on_delete():
    """Витік ресурсів та невідповідність розміру при видаленні через невіртуальну базу."""
    W, H = 940, 430
    f = []

    # ── Заголовки двох колонок
    f.append(fitbox(40, 30, 410, 40, "Без virtual: статичний виклик ~Base()",
                    size=13, bold=True, fill="#fdecea", stroke=POS, color=POS))
    f.append(fitbox(490, 30, 410, 40, "З virtual: динамічний виклик ~Derived()",
                    size=13, bold=True, fill="#eef7ee", stroke=FIELD, color=FIELD))

    # ── Ліва колонка: об'єкт у купі без віртуального деструктора
    f.append(rect(40, 85, 410, 230, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(245, 110, "Об'єкт Derived у динамічній пам'яті (купа)", size=12, color=MUTED, bold=True))

    # Частина Base
    f.append(rect(60, 125, 370, 50, fill="#eef2f7", stroke=MUTED, sw=1.2, rx=4))
    f.append(text(245, 145, "Частина Base (vptr або поля бази)", size=12, bold=True, color=LINE))
    f.append(text(245, 163, "Зруйновано: викликано ~Base()", size=11, color=FIELD))

    # Частина Derived
    f.append(rect(60, 185, 370, 115, fill="#fff3f2", stroke=POS, sw=1.5, rx=4))
    f.append(text(245, 208, "Частина Derived (члени похідного класу)", size=12, bold=True, color=POS))
    f.append(text(245, 232, "• GPU-дескриптори (VkDevice, OpenGL ID) → витік", size=11, color=POS))
    f.append(text(245, 252, "• Динамічні буфери (std::vector, std::string) → витік", size=11, color=POS))
    f.append(text(245, 272, "• Деструктор ~Derived() НЕ викликано взагалі!", size=11, color=POS, bold=True))

    # Пояснення внизу зліва
    f.append(fitbox(40, 328, 410, 80,
                    "Наслідки delete (Base*)p:\n"
                    "1. Витік ресурсів, захоплених похідним класом.\n"
                    "2. Sized deallocation: деалокатор дістає sizeof(Base) замість sizeof(Derived) → руйнування пулів пам'яті.\n"
                    "3. За стандартом [expr.delete] — невизначена поведінка (UB)!",
                    size=11, fill="#fdf7f7", stroke=POS, color=INK))

    # ── Права колонка: об'єкт у купі з віртуальним деструктором
    f.append(rect(490, 85, 410, 230, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(695, 110, "Об'єкт Derived у динамічній пам'яті (купа)", size=12, color=MUTED, bold=True))

    # Частина Base
    f.append(rect(510, 125, 370, 50, fill="#eef7ee", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(695, 145, "Частина Base (vptr → vtable Derived)", size=12, bold=True, color=LINE))
    f.append(text(695, 163, "Зруйновано коректно: викликано ~Base()", size=11, color=FIELD))

    # Частина Derived
    f.append(rect(510, 185, 370, 115, fill="#eef7ee", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(695, 208, "Частина Derived (члени похідного класу)", size=12, bold=True, color=FIELD))
    f.append(text(695, 232, "• GPU-дескриптори звільнено через vkDestroyDevice", size=11, color=FIELD))
    f.append(text(695, 252, "• Внутрішні буфери очищено деструкторами членів", size=11, color=FIELD))
    f.append(text(695, 272, "• Деструктор ~Derived() викликано через vtable (D0)", size=11, color=FIELD, bold=True))

    # Пояснення внизу справа
    f.append(fitbox(490, 328, 410, 80,
                    "Результат delete (Base*)p:\n"
                    "1. Повне та коректне розгортання ланцюга деструкторів.\n"
                    "2. Деалокація з точним розміром повного об'єкта sizeof(Derived).\n"
                    "3. Коректна базова адреса пам'яті навіть при множинному успадкуванні.",
                    size=11, fill="#f2f9f4", stroke=FIELD, color=INK))

    render(os.path.join(IMG, 'slicing-and-leak-on-delete.svg'), W, H, *f,
           title="Витік ресурсів та UB при невіртуальному видаленні")


def fig_vtable_dtor_dispatch():
    """Будова vtable: подвійний слот деструктора (D0 deleting та D1 complete) в ABI."""
    W, H = 940, 410
    f = []

    # ── Лівий блок: об'єкт Derived у пам'яті
    f.append(rect(40, 50, 240, 260, fill=FILL, stroke=LINE, sw=1.4, rx=6))
    f.append(text(160, 75, "Екземпляр Derived", size=13, bold=True, color=LINE))

    f.append(rect(55, 95, 210, 48, fill="#e8f0fe", stroke=NEG, sw=1.5, rx=4))
    f.append(text(160, 115, "vptr (покажчик vtable)", size=12, bold=True, color=NEG))
    f.append(text(160, 132, "вказує на vtable Derived", size=10, color=MUTED))

    f.append(rect(55, 155, 210, 50, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    f.append(text(160, 175, "Поля базового класу Base", size=11, color=LINE))
    f.append(text(160, 193, "int base_id, flags...", size=10, color=MUTED))

    f.append(rect(55, 215, 210, 75, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    f.append(text(160, 235, "Поля похідного класу", size=11, color=LINE))
    f.append(text(160, 255, "std::vector<char> buffer", size=10, color=MUTED))
    f.append(text(160, 273, "int socket_fd...", size=10, color=MUTED))

    # Стрілка від vptr до таблиці
    f.append(arrow(265, 119, 368, 119, color=NEG, sw=2))

    # ── Середній блок: Таблиця vtable (Itanium ABI)
    f.append(rect(370, 50, 270, 260, fill="#f8fafc", stroke=NEG, sw=1.4, rx=6))
    f.append(text(505, 75, "vtable для Derived (Itanium ABI)", size=13, bold=True, color=NEG))

    f.append(rect(385, 95, 240, 36, fill="#ffffff", stroke=MUTED, sw=1, rx=3))
    f.append(text(505, 117, "offset-to-top (0) / RTTI ptr", size=11, color=MUTED))

    f.append(rect(385, 138, 240, 42, fill="#eef7ee", stroke=FIELD, sw=1.5, rx=3))
    f.append(text(505, 156, "Слот D1: Complete Dtor", size=12, bold=True, color=FIELD))
    f.append(text(505, 172, "руйнує члени й бази без free()", size=10, color=MUTED))

    f.append(rect(385, 188, 240, 46, fill="#fdecea", stroke=POS, sw=1.5, rx=3))
    f.append(text(505, 206, "Слот D0: Deleting Dtor", size=12, bold=True, color=POS))
    f.append(text(505, 224, "викликає D1 + operator delete", size=10, color=MUTED))

    f.append(rect(385, 242, 240, 36, fill="#ffffff", stroke=MUTED, sw=1, rx=3))
    f.append(text(505, 264, "Інші віртуальні методи (render...)", size=11, color=LINE))

    # ── Правий блок: Що робить інструкція delete base_ptr;
    f.append(rect(680, 50, 220, 260, fill="#fdfbf7", stroke="#d97706", sw=1.4, rx=6))
    f.append(text(790, 75, "Виконання delete p;", size=13, bold=True, color="#d97706"))

    f.append(text(790, 105, "1. Отримання vptr", size=11, bold=True, color=LINE))
    f.append(text(790, 122, "p->vptr", size=10, color=MUTED))

    f.append(text(790, 148, "2. Виклик слота D0", size=11, bold=True, color=POS))
    f.append(text(790, 165, "vtable[D0_slot](p)", size=10, color=MUTED))

    f.append(text(790, 192, "3. Руйнування об'єкта", size=11, bold=True, color=FIELD))
    f.append(text(790, 209, "~Derived() → ~Base()", size=10, color=MUTED))

    f.append(text(790, 236, "4. Звільнення пам'яті", size=11, bold=True, color=NEG))
    f.append(text(790, 253, "operator delete(p, sizeof(D))", size=10, color=MUTED))

    f.append(text(790, 280, "5. Пам'ять чиста", size=11, bold=True, color=FIELD))

    # Стрілка від слота D0 до виконання
    f.append(arrow(625, 211, 678, 211, color=POS, sw=2))

    # Нижній висновок
    f.append(fitbox(40, 330, 860, 60,
                    "Компілятор розбиває віртуальний деструктор на дві сутності в ABI:\n"
                    "• D1 (Complete Object) викликається для автоматичних і статичних об'єктів (де пам'ять звільняє стек/сегмент).\n"
                    "• D0 (Deleting Destructor) викликається оператором delete для динамічних об'єктів (виконує руйнування та викликає operator delete).",
                    size=11, fill="#f4f6f8", stroke=LINE, color=INK))

    render(os.path.join(IMG, 'vtable-dtor-dispatch.svg'), W, H, *f,
           title="Диспетчеризація віртуального деструктора через vtable")


def fig_destruction_chain():
    """Ланцюг руйнування об'єкта зверху вниз та перемикання vptr."""
    W, H = 940, 380
    f = []

    steps = [
        (40, "1. Вхід у ~Derived()",
         "vptr вказує на vtable Derived.\n"
         "Виконується тіло користувацького\n"
         "деструктора Derived::~Derived().", FIELD),
        (260, "2. Члени Derived",
         "Нестатичні члени Derived\n"
         "руйнуються у зворотному порядку\n"
         "до їхнього оголошення в класі.", FIELD),
        (480, "3. Зміна vptr → Base",
         "Середовище перемикає vptr об'єкта\n"
         "на vtable класу Base!\n"
         "Частини Derived більше не існує.", NEG),
        (700, "4. Тіло й члени Base",
         "Виконується Base::~Base().\n"
         "Члени Base руйнуються у зворотному\n"
         "порядку. Об'єкт помер.", POS),
    ]

    for x, header, desc, col in steps:
        f.append(rect(x, 40, 200, 210, fill=FILL, stroke=col, sw=1.5, rx=6))
        f.append(fitbox(x + 8, 48, 184, 32, header, size=12, bold=True, fill="#ffffff", stroke=col, color=col))
        f.append(fitbox(x + 8, 88, 184, 150, desc, size=11, fill=BG, stroke=MUTED, color=INK))

    # Стрілки переходу між кроками
    for ax in [240, 460, 680]:
        f.append(arrow(ax, 145, ax + 18, 145, color=LINE, sw=2))

    # Нижній висновок
    f.append(fitbox(40, 275, 860, 80,
                    "Критичний інваріант: усередині деструктора базового класу об'єкт уже втратив свою похідну природу.\n"
                    "Перемикання vptr гарантує, що віртуальні виклики з Base::~Base() підуть у версію Base (або викличуть паніку pure virtual call),\n"
                    "а не звертатимуться до вже мертвої пам'яті й зруйнованих членів Derived.",
                    size=11, fill="#fdfbf7", stroke="#d97706", color=INK))

    render(os.path.join(IMG, 'destruction-chain.svg'), W, H, *f,
           title="Порядок розгортання ланцюга деструкторів")


def fig_protected_dtor_pattern():
    """Патерн захищеного невіртуального деструктора для mixin / CRTP / нединамічних баз."""
    W, H = 940, 360
    f = []

    # ── Ліва частина: Заборона видалення через вказівник на базу
    f.append(rect(40, 40, 410, 220, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
    f.append(text(245, 68, "Спроба видалення через Base*", size=13, bold=True, color=POS))

    f.append(fitbox(55, 85, 380, 75,
                    "Base* p = new Derived();\n"
                    "delete p;  // ❌ ПОМИЛКА КОМПІЛЯЦІЇ!\n"
                    "error: '~Base' is protected within this context",
                    size=11, fill="#ffffff", stroke=POS, color=POS))

    f.append(fitbox(55, 170, 380, 75,
                    "Компілятор фізично блокує поліморфне видалення.\n"
                    "Випадкове руйнування через невіртуальну базу стає неможливим ще на етапі збирання.",
                    size=11, fill="#ffffff", stroke=MUTED, color=INK))

    # ── Права частина: Дозволене безпечне використання
    f.append(rect(490, 40, 410, 220, fill="#eef7ee", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(695, 68, "Безпечне використання Derived", size=13, bold=True, color=FIELD))

    f.append(fitbox(505, 85, 380, 75,
                    "Derived d;         // ✔ Автоматичний стек\n"
                    "auto p = std::make_unique<Derived>(); // ✔ Купа\n"
                    "delete derived_p;  // ✔ Явне видалення Derived*",
                    size=11, fill="#ffffff", stroke=FIELD, color=FIELD))

    f.append(fitbox(505, 170, 380, 75,
                    "Деструктор Derived має доступ до protected-деструктора ~Base().\n"
                    "Об'єкт безпечно будується і руйнується з нульовими накладними витратами.",
                    size=11, fill="#ffffff", stroke=MUTED, color=INK))

    # Нижній висновок
    f.append(fitbox(40, 280, 860, 60,
                    "protected ~Base() = default — ідеальний вибір для базових класів mixin, CRTP та класів-політик:\n"
                    "100% захист від UB при нульовому розмірі (0 байтів на vptr) та повній можливості інлайнінгу деструктора.",
                    size=11, fill="#f4f6f8", stroke=LINE, color=INK))

    render(os.path.join(IMG, 'protected-dtor-pattern.svg'), W, H, *f,
           title="Патерн захищеного невіртуального деструктора")


if __name__ == '__main__':
    fig_slicing_and_leak_on_delete()
    fig_vtable_dtor_dispatch()
    fig_destruction_chain()
    fig_protected_dtor_pattern()
    print("Всі 4 фігури згенеровано успішно.")
