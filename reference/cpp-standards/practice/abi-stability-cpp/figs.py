# -*- coding: utf-8 -*-
"""Генератор фігур для теми «Стабільність ABI у C++ і що її ламає»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

def save(name, content, w, h):
    path = os.path.join(OUT, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n')
        f.write(f'<rect width="{w}" height="{h}" fill="{BG}"/>\n')
        f.write('\n'.join(content))
        f.write('\n</svg>\n')
    print(f'  OK: {name}')


# ── 1. Зсув таблиці віртуальних методів (vtable layout shift) ─────────────
def fig_vtable_layout_shift():
    W, H = 960, 480
    f = []

    f.append(text(480, 28, "Руйнування виклику віртуального методу через зміну vtable між версіями", size=16, color=INK, anchor="middle", bold=True))

    # Ліва колонка: Версія 1.0 (Очікування скомпільованої програми)
    f.append(text(240, 65, "Бінарник клієнта (скомпільовано з v1.0.h)", size=13, color=FIELD, anchor="middle", bold=True))
    f.append(rect(40, 80, 400, 360, fill="#f8fafc", stroke=LINE, rx=6))

    # Об'єкт у пам'яті клієнта
    f.append(text(140, 105, "Об'єкт у пам'яті:", size=12, color=MUTED, anchor="start", bold=True))
    f.append(fitbox(55, 120, 170, 44, "vptr (вказівник на vtable)\nзміщення +0x00", size=11, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(55, 172, 170, 44, "int payload_\nзміщення +0x08", size=11, fill="#ffffff", stroke=LINE))

    # Таблиця vtable v1.0
    f.append(text(275, 105, "vtable v1.0 у shared library:", size=12, color=MUTED, anchor="start", bold=True))
    f.append(fitbox(265, 120, 160, 40, "Слот 0: &Widget::render()", size=11, fill="#ffffff", stroke=LINE))
    f.append(fitbox(265, 168, 160, 40, "Слот 1: &Widget::update()", size=11, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(265, 216, 160, 40, "Слот 2: &Widget::~Widget()", size=11, fill="#ffffff", stroke=LINE))

    # Стрілка vptr -> vtable v1.0
    f.append(arrow(225, 142, 260, 142, color=FIELD, sw=2))

    # Виклик у клієнті
    f.append(fitbox(55, 275, 370, 85,
                    "Клієнтський код: w->update();\n"
                    "Асемблер: mov rax, [rdi]        ; rax = vptr\n"
                    "          call [rax + 8]        ; виклик Слот 1 (update)\n"
                    "Результат: викликається правильний метод update()",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Права колонка: Версія 1.1 з доданим віртуальним методом угорі
    f.append(text(720, 65, "Оновлена динамічна бібліотека (v1.1.so)", size=13, color=POS, anchor="middle", bold=True))
    f.append(rect(520, 80, 400, 360, fill="#fdf8f8", stroke=POS, rx=6))

    f.append(text(620, 105, "Новий vtable v1.1 у бібліотеці:", size=12, color=MUTED, anchor="start", bold=True))
    f.append(fitbox(545, 120, 350, 38, "Слот 0: &Widget::initialize()  [НОВИЙ МЕТОД]", size=11, fill="#ffebee", stroke=POS))
    f.append(fitbox(545, 164, 350, 38, "Слот 1: &Widget::render()      [ЗСУНУВСЯ З 0]", size=11, fill="#fff3e0", stroke=POS))
    f.append(fitbox(545, 208, 350, 38, "Слот 2: &Widget::update()      [ЗСУНУВСЯ З 1]", size=11, fill="#ffffff", stroke=LINE))
    f.append(fitbox(545, 252, 350, 38, "Слот 3: &Widget::~Widget()     [ЗСУНУВСЯ З 2]", size=11, fill="#ffffff", stroke=LINE))

    # Що виконує клієнт
    f.append(fitbox(535, 305, 370, 120,
                    "Старий клієнт викликає: call [rax + 8] (Слот 1)\n"
                    "Очікування клієнта: виклик update()\n"
                    "Реальність у v1.1: виклик render() замість update()!\n"
                    "Наслідок: невідповідність параметрів, читання не тих регістрів,\n"
                    "тихе пошкодження пам'яті або Crash (SIGSEGV).",
                    size=11, fill="#ffebee", stroke=POS))

    # Розділювач
    f.append(line(480, 75, 480, 445, color=MUTED, dash="4,4"))

    save("vtable-layout-shift.svg", f, W, H)


# ── 2. Невідповідність розкладки структури (struct layout mismatch) ───────
def fig_struct_padding_mismatch():
    W, H = 960, 450
    f = []

    f.append(text(480, 28, "Невідповідність розміщення полів (Padding і Alignment) між бібліотекою та клієнтом", size=16, color=INK, anchor="middle", bold=True))

    # Блок А: Бібліотека v1.0 (оригінальна розкладка)
    f.append(text(240, 65, "Бібліотека v1.0 (sizeof = 16 байтів)", size=13, color=FIELD, anchor="middle", bold=True))
    f.append(rect(40, 80, 400, 340, fill="#f8fafc", stroke=LINE, rx=6))

    # Пам'ять v1
    f.append(fitbox(60, 100, 110, 50, "int32_t id\n[4 байти]", size=11, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(175, 100, 110, 50, "uint32_t flags\n[4 байти]", size=11, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(290, 100, 130, 50, "double score\n[8 байтів]", size=11, fill="#e8f6ee", stroke=FIELD))

    f.append(text(60, 170, "Зміщення в пам'яті (Offset):", size=12, color=MUTED, anchor="start", bold=True))
    f.append(text(60, 192, "• offsetof(id)    = 0x00", size=11, color=INK, anchor="start"))
    f.append(text(60, 212, "• offsetof(flags) = 0x04", size=11, color=INK, anchor="start"))
    f.append(text(60, 232, "• offsetof(score) = 0x08 (вирівняно за 8 байтів)", size=11, color=INK, anchor="start"))

    f.append(fitbox(60, 260, 360, 140,
                    "Клієнт зчитує score:\n"
                    "movsd xmm0, [rdi + 8]\n\n"
                    "Обидві сторони однаково розуміють адресу score.\n"
                    "Читання коректне: значення 99.5 потрапляє в xmm0.",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Блок Б: Бібліотека v1.1 з доданим полем між id та flags
    f.append(text(720, 65, "Бібліотека v1.1 з новим полем (sizeof = 24 байти)", size=13, color=POS, anchor="middle", bold=True))
    f.append(rect(520, 80, 400, 340, fill="#fdf8f8", stroke=POS, rx=6))

    # Пам'ять v2
    f.append(fitbox(535, 100, 80, 50, "int32_t id\n[4 б]", size=10, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(620, 100, 85, 50, "int16_t tag\n[2 б]", size=10, fill="#ffebee", stroke=POS))
    f.append(fitbox(710, 100, 60, 50, "pad\n[2 б]", size=10, fill="#fff3e0", stroke=MUTED))
    f.append(fitbox(775, 100, 65, 50, "flags\n[4 б]", size=10, fill="#ffffff", stroke=LINE))
    f.append(fitbox(845, 100, 65, 50, "pad\n[4 б]", size=10, fill="#fff3e0", stroke=MUTED))

    f.append(text(535, 170, "Реальні зміщення у v1.1:", size=12, color=MUTED, anchor="start", bold=True))
    f.append(text(535, 192, "• offsetof(id)    = 0x00, offsetof(tag) = 0x04", size=11, color=INK, anchor="start"))
    f.append(text(535, 212, "• offsetof(flags) = 0x08 (зсунувся з 0x04 на 0x08!)", size=11, color=POS, anchor="start", bold=True))
    f.append(text(535, 232, "• offsetof(score) = 0x10 (зсунувся з 0x08 на 0x10!)", size=11, color=POS, anchor="start", bold=True))

    f.append(fitbox(535, 260, 370, 140,
                    "Незбіжний клієнт (v1.0) зчитує score за старим зміщенням:\n"
                    "movsd xmm0, [rdi + 8]\n\n"
                    "Помилка: за адресою [rdi + 8] тепер лежать flags та padding!\n"
                    "Цілі числа інтерпретуються як double (сміття/NaN).\n"
                    "При записі клієнт перетирає чужі поля у v1.1 структурі!",
                    size=11, fill="#ffebee", stroke=POS))

    # Розділювач
    f.append(line(480, 75, 480, 425, color=MUTED, dash="4,4"))

    save("struct-padding-mismatch.svg", f, W, H)


# ── 3. Передача аргументів у регістрах проти стеку ─────────────────────────
def fig_calling_conv_registers_vs_stack():
    W, H = 960, 460
    f = []

    f.append(text(480, 28, "Вплив нетривіального деструктора на конвенцію виклику System V AMD64 ABI", size=16, color=INK, anchor="middle", bold=True))

    # Ліва частина: Сирий вказівник або тривіальний тип (Pass in Registers)
    f.append(text(240, 65, "Сирий вказівник T* або тривіальна структура", size=13, color=FIELD, anchor="middle", bold=True))
    f.append(rect(40, 80, 400, 350, fill="#f8fafc", stroke=LINE, rx=6))

    f.append(fitbox(60, 100, 360, 50, "Клас ABI: INTEGER (тривіально копійований і знищуваний)\nРозмір: 8 байтів <= 16 байтів", size=11, fill="#e8f6ee", stroke=FIELD))

    f.append(fitbox(60, 165, 360, 85,
                    "Регістр процесора %rdi:\n"
                    "┌──────────────────────────────────────────────┐\n"
                    "│               0x7fff_dead_beef               │ (пряма адреса об'єкта)\n"
                    "└──────────────────────────────────────────────┘",
                    size=11, fill="#ffffff", stroke=FIELD))

    f.append(fitbox(60, 265, 360, 145,
                    "Генерація машинного коду (0 звернень до стеку):\n"
                    "  mov rdi, rax          ; запис адреси в регістр rdi\n"
                    "  call process(T*)      ; прямий стрибок\n\n"
                    "Продуктивність:\n"
                    "• 0 інструкцій запису в оперативну пам'ять\n"
                    "• Максимальна швидкість виконання у пайплайні CPU",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Права частина: std::unique_ptr (Pass in Memory / Hidden Pointer)
    f.append(text(720, 65, "std::unique_ptr<T> (має нетривіальний деструктор)", size=13, color=POS, anchor="middle", bold=True))
    f.append(rect(520, 80, 400, 350, fill="#fdf8f8", stroke=POS, rx=6))

    f.append(fitbox(540, 100, 360, 50, "Клас ABI: MEMORY (нетривіальний деструктор у C++ ABI)\nПравило: об'єкт передається через пам'ять стеку!", size=11, fill="#ffebee", stroke=POS))

    # Пам'ять стеку
    f.append(fitbox(540, 165, 360, 85,
                    "Стек процесу (RSP) + прихований вказівник у %rdi:\n"
                    "  %rdi  ──>  [ RSP + 8 ]:  0x7fff_dead_beef (адреса T)\n"
                    "             [ RSP + 0 ]:  адреса повернення",
                    size=11, fill="#ffffff", stroke=POS))

    f.append(fitbox(540, 265, 360, 145,
                    "Генерація машинного коду (навантаження на стек):\n"
                    "  mov [rsp+8], rax      ; запис вказівника на стек\n"
                    "  lea rdi, [rsp+8]      ; передача адреси слота стеку в rdi\n"
                    "  call process(uniq_ptr); функція читає через пам'ять\n\n"
                    "Ціна збереження ABI: передача unique_ptr за значенням\n"
                    "потребує зайвих Store/Load операцій у пам'ять.",
                    size=11, fill="#ffebee", stroke=POS))

    # Розділювач
    f.append(line(480, 75, 480, 435, color=MUTED, dash="4,4"))

    save("calling-conv-registers-vs-stack.svg", f, W, H)


# ── 4. Рівні захисту ABI (ABI Protection Firewall) ─────────────────────────
def fig_abi_protection_layers():
    W, H = 960, 460
    f = []

    f.append(text(480, 28, "Багаторівнева архітектура захисту стабільності двійкового інтерфейсу (ABI Firewall)", size=16, color=INK, anchor="middle", bold=True))

    # Рівень 1: C++ Header / PImpl
    f.append(fitbox(50, 70, 260, 80,
                    "1. Ідіома PImpl (Opaque Pointer)\n"
                    "Публічний клас містить лише std::unique_ptr<Impl>.\n"
                    "Розмір і vtable клієнта фіксовані назавжди (8 байтів).",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Рівень 2: Версіоновані простори імен
    f.append(fitbox(350, 70, 260, 80,
                    "2. Inline Namespaces (ABI Versioning)\n"
                    "inline namespace v2 { class Engine; }\n"
                    "Манглене ім'я кодує версію (_ZN6engine2v2…),\n"
                    "запобігаючи тихим ODR-помилкам.",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Рівень 3: Чистий C-шлюз
    f.append(fitbox(650, 70, 260, 80,
                    "3. extern \"C\" Boundary\n"
                    "Непрозорі дескриптори (typedef struct Handle*).\n"
                    "Стабільний плоский ABI між будь-якими компіляторами.",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    # Стрілки вниз
    f.append(arrow(180, 155, 180, 195, color=LINE, sw=2))
    f.append(arrow(480, 155, 480, 195, color=LINE, sw=2))
    f.append(arrow(780, 155, 780, 195, color=LINE, sw=2))

    # Рівень 4: Контроль видимості лінкера
    f.append(fitbox(150, 200, 660, 75,
                    "4. Контроль видимості символів (Symbol Visibility Firewall)\n"
                    "Прапорець компілятора: -fvisibility=hidden -fvisibility-inlines-hidden\n"
                    "Експортуються лише явно помічені символи: __attribute__((visibility(\"default\")))\n"
                    "Приватні класи, шаблони та деталі реалізації НЕ потрапляють у таблицю .dynsym!",
                    size=11, fill="#f4f6f8", stroke=LINE))

    # Стрілка вниз
    f.append(arrow(480, 280, 480, 315, color=LINE, sw=2))

    # Рівень 5: GNU Symbol Versioning і CI аудит
    f.append(fitbox(150, 320, 660, 105,
                    "5. Символьне версіонування у лінкері та Автоматичний CI-аудит (libabigail)\n"
                    "• GNU Version Script: MYLIB_1.0 { global: mylib_*; local: *; };\n"
                    "• abidw / abidiff у конвеєрі CI: аналізує DWARF-дерева типів між комітами;\n"
                    "• Автоматичне блокування pull request при зміні зміщень полів або слотів vtable.",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    save("abi-protection-layers.svg", f, W, H)


if __name__ == '__main__':
    fig_vtable_layout_shift()
    fig_struct_padding_mismatch()
    fig_calling_conv_registers_vs-stack() if False else fig_calling_conv_registers_vs_stack()
    fig_abi_protection_layers()
