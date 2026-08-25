# -*- coding: utf-8 -*-
"""Фігури теми «Власні алокатори й пам'ять під контролем»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_allocator_layers():
    """Розділення виділення пам'яті й конструювання об'єктів у моделі C++."""
    W, H = 940, 480
    f = []

    # Верхній рівень: Контейнер
    f.append(fitbox(60, 50, 820, 52,
                    "Контейнер (наприклад std::vector<Widget, Alloc>)\n"
                    "Керує логікою: ємність, розмір, індексація, збереження інваріантів",
                    size=13, bold=True, fill="#eef2f7", stroke=MUTED, color=MUTED))

    # Стрілки від контейнера до traits
    f.append(arrow(260, 106, 260, 146, color=MUTED, sw=1.8))
    f.append(arrow(680, 106, 680, 146, color=MUTED, sw=1.8))
    f.append(text(260, 128, "1 · виділення сирих байтів", size=11, color=MUTED))
    f.append(text(680, 128, "2 · створення й руйнування", size=11, color=MUTED))

    # Середній рівень: traits розділяє операції
    # Лівий блок: нетипізована пам'ять
    f.append(fitbox(60, 150, 400, 180,
                    "std::allocator_traits<Alloc>::allocate(a, n)\n"
                    "Повертає сирий покажчик на неініціалізовану пам'ять T*\n\n"
                    "std::allocator_traits<Alloc>::deallocate(a, p, n)\n"
                    "Повертає байти до джерела без виклику деструкторів",
                    size=12, fill="#fdecea", stroke=POS, color=INK))

    # Правий блок: час життя об'єктів
    f.append(fitbox(480, 150, 400, 180,
                    "std::allocator_traits<Alloc>::construct(a, p, args...)\n"
                    "::new (static_cast<void*>(p)) T(args...)\n"
                    "Початок часу життя: виклик конструктора на готових байтах\n\n"
                    "std::allocator_traits<Alloc>::destroy(a, p)\n"
                    "p->~T()\n"
                    "Кінець часу життя: явний виклик деструктора",
                    size=12, fill="#eef7ee", stroke=FIELD, color=INK))

    # Стрілки до низу
    f.append(arrow(260, 334, 260, 376, color=POS, sw=1.8))
    f.append(text(260, 356, "сирі байти", size=11, color=POS))

    # Нижній рівень: Джерело сирої пам'яті
    f.append(fitbox(60, 380, 820, 56,
                    "Джерело байтів (OS / malloc / Арена / Пул / Стек-буфер)\n"
                    "Знає лише про кількість байтів і вирівнювання (alignof); нічого не знає про типи",
                    size=13, bold=True, fill=FILL, stroke=LINE, color=INK))

    render(os.path.join(IMG, 'allocator-layers.svg'), W, H, *f,
           title="Розділення виділення байтів і часу життя об'єкта")


def fig_allocator_types_contrast():
    """Порівняння трьох стратегій виділення: купа, лінійна арена, пул блоків."""
    W, H = 940, 520
    f = []

    # 1. Загальна купа (Heap)
    f.append(fitbox(40, 50, 260, 42, "Загальна купа (malloc / heap)", size=13, bold=True,
                    fill="#eef2f7", stroke=MUTED, color=MUTED))
    f.append(rect(40, 100, 260, 170, fill=BG, stroke=MUTED, sw=1.2))
    # Блоки з заголовками й фрагментацією
    f.append(fitbox(50, 110, 70, 40, "мета", size=10, fill="#fdecea", stroke=POS, color=POS))
    f.append(fitbox(122, 110, 80, 40, "блок A", size=11, fill="#eef7ee", stroke=FIELD, color=FIELD))
    f.append(fitbox(204, 110, 86, 40, "діра", size=11, fill="#f4f6f8", stroke=MUTED, color=MUTED))
    f.append(fitbox(50, 160, 90, 40, "блок B", size=11, fill="#eef7ee", stroke=FIELD, color=FIELD))
    f.append(fitbox(142, 160, 148, 40, "вільно", size=11, fill="#f4f6f8", stroke=MUTED, color=MUTED))
    f.append(fitbox(50, 210, 240, 48,
                    "• Оверхед на заголовок кожного блоку\n"
                    "• Фрагментація пам'яті\n"
                    "• Мютекси між потоками",
                    size=10, fill=FILL, stroke=LINE))

    # 2. Арена / Bump Allocator
    f.append(fitbox(340, 50, 260, 42, "Лінійна арена (Bump Pointer)", size=13, bold=True,
                    fill="#eef7ee", stroke=FIELD, color=FIELD))
    f.append(rect(340, 100, 260, 170, fill=BG, stroke=FIELD, sw=1.5))
    f.append(fitbox(350, 110, 50, 40, "об'єкт 1", size=10, fill="#eef7ee", stroke=FIELD, color=FIELD))
    f.append(fitbox(402, 110, 70, 40, "об'єкт 2", size=10, fill="#eef7ee", stroke=FIELD, color=FIELD))
    f.append(fitbox(474, 110, 45, 40, "об'єкт 3", size=10, fill="#eef7ee", stroke=FIELD, color=FIELD))
    # Вказівник cursor
    f.append(arrow(525, 185, 525, 155, color=POS, sw=2))
    f.append(text(525, 200, "cursor →", size=11, color=POS, bold=True))
    f.append(fitbox(350, 215, 240, 48,
                    "• Виділення: O(1) зсув вказівника\n"
                    "• Нульова внутрішня фрагментація\n"
                    "• Звільнення: тільки всієї арени разом",
                    size=10, fill=FILL, stroke=LINE))

    # 3. Пул фіксованих блоків (Pool / Free-list)
    f.append(fitbox(640, 50, 260, 42, "Пул слотів (Free-list Pool)", size=13, bold=True,
                    fill="#fdecea", stroke=POS, color=POS))
    f.append(rect(640, 100, 260, 170, fill=BG, stroke=POS, sw=1.5))
    f.append(fitbox(650, 110, 72, 40, "T живий", size=10, fill="#eef7ee", stroke=FIELD, color=FIELD))
    f.append(fitbox(726, 110, 80, 40, "Next* →", size=10, fill="#fdecea", stroke=POS, color=POS))
    f.append(fitbox(810, 110, 80, 40, "T живий", size=10, fill="#eef7ee", stroke=FIELD, color=FIELD))
    f.append(fitbox(650, 160, 80, 40, "Next* → ∅", size=10, fill="#fdecea", stroke=POS, color=POS))
    f.append(fitbox(734, 160, 156, 40, "T живий", size=10, fill="#eef7ee", stroke=FIELD, color=FIELD))
    f.append(fitbox(650, 215, 240, 48,
                    "• Всі блоки однакового розміру\n"
                    "• Вільні слоти зв'язані у список (free-list)\n"
                    "• O(1) поштучне виділення й звільнення",
                    size=10, fill=FILL, stroke=LINE))

    # Підсумкова порівняльна панель унизу
    f.append(fitbox(40, 300, 860, 180,
                    "Висновки для архітектури:\n"
                    "• Арена ідеальна для короткоживучих задач кадру або HTTP-запиту: тисячі дрібних об'єктів без оверхеду на free().\n"
                    "• Пул фіксованих блоків ідеальний для вузлів std::list, std::map та графів: усуває фрагментацію й прискорює кеш.\n"
                    "• Загальна купа лишається для довгоживучих об'єктів довільного непередбачуваного розміру.",
                    size=12, fill=FILL, stroke=LINE, color=INK))

    render(os.path.join(IMG, 'allocator-types-contrast.svg'), W, H, *f,
           title="Структурне порівняння стратегій розподілу пам'яті")


def fig_pmr_erasure_hierarchy():
    """Поліморфні ресурси пам'яті: стирання типу алокатора у std::pmr."""
    W, H = 940, 480
    f = []

    # Контейнери зі спільним типом
    f.append(fitbox(50, 50, 390, 60,
                    "std::pmr::vector<int> a;\n"
                    "(використовує стек-буфер)",
                    size=12, fill="#eef7ee", stroke=FIELD, color=INK))

    f.append(fitbox(500, 50, 390, 60,
                    "std::pmr::vector<int> b;\n"
                    "(використовує системну купу)",
                    size=12, fill="#eef2f7", stroke=MUTED, color=INK))

    # Спільна функція
    f.append(fitbox(270, 140, 400, 46,
                    "void process(std::pmr::vector<int>& v);\n"
                    "Один спільний тип: немає шаблонізації за алокатором!",
                    size=12, bold=True, fill=FILL, stroke=LINE, color=INK))

    f.append(arrow(245, 112, 360, 138, color=FIELD, sw=1.8))
    f.append(arrow(695, 112, 580, 138, color=MUTED, sw=1.8))

    # Проміжний рівень: polymorphic_allocator
    f.append(fitbox(200, 215, 540, 44,
                    "std::pmr::polymorphic_allocator<T> містить вказівник: memory_resource*",
                    size=12, bold=True, fill="#fdecea", stroke=POS, color=POS))
    f.append(arrow(470, 188, 470, 212, color=LINE, sw=1.8))

    # Рівень ресурсів пам'яті (memory_resource)
    f.append(fitbox(60, 290, 250, 70,
                    "monotonic_buffer_resource\n"
                    "Швидка арена на локальному масиві std::byte buffer[1024]",
                    size=11, fill="#eef7ee", stroke=FIELD, color=INK))

    f.append(fitbox(345, 290, 250, 70,
                    "unsynchronized_pool_resource\n"
                    "Пул фіксованих блоків для вузлових контейнерів",
                    size=11, fill="#fdecea", stroke=POS, color=INK))

    f.append(fitbox(630, 290, 250, 70,
                    "new_delete_resource()\n"
                    "Глобальна системна купа operator new / delete",
                    size=11, fill="#eef2f7", stroke=MUTED, color=INK))

    f.append(arrow(340, 260, 200, 288, color=POS, sw=1.6))
    f.append(arrow(470, 260, 470, 288, color=POS, sw=1.6))
    f.append(arrow(600, 260, 740, 288, color=POS, sw=1.6))

    # Ланцюжок upstream fallback
    f.append(arrow(312, 325, 342, 325, color=MUTED, sw=1.5))
    f.append(text(327, 315, "upstream", size=10, color=MUTED))
    f.append(arrow(597, 325, 627, 325, color=MUTED, sw=1.5))
    f.append(text(612, 315, "upstream", size=10, color=MUTED))

    # Нижній висновок
    f.append(fitbox(60, 390, 820, 56,
                    "Перевага PMR: поліморфізм винесено у віртуальну таблицю memory_resource,\n"
                    "тому тип контейнера залишається незмінним незалежно від стратегії розміщення пам'яті.",
                    size=12, bold=True, fill=FILL, stroke=LINE, color=INK))

    render(os.path.join(IMG, 'pmr-erasure-hierarchy.svg'), W, H, *f,
           title="Ієрархія PMR і стирання типу алокатора")


def fig_allocator_propagation_matrix():
    """Матриця поширення алокатора при копіюванні, переміщенні та обміні."""
    W, H = 940, 480
    f = []

    cols = [(40, 180), (230, 330), (570, 330)]
    heads = ["Операція контейнера", "Якщо ознака (trait) = true", "Якщо ознака (trait) = false"]
    for (x, w), s in zip(cols, heads):
        f.append(fitbox(x, 48, w, 40, s, size=12, bold=True, fill="#eef2f7", stroke=MUTED, color=MUTED))

    rows = [
        ("Копіювальне присвоєння\n(propagate_on_container_copy_assignment)",
         "Старий буфер звільняється старим алокатором;\nалокатор копіюється з джерела;\nновий буфер виділяється новим алокатором",
         "Алокатор залишається незмінним;\nновий буфер виділяється власним алокатором;\nелементи копіюються",
         FIELD),
        ("Переміщувальне присвоєння\n(propagate_on_container_move_assignment)",
         "Алокатор переміщується;\nбуфер миттєво крадеться за O(1)\n(просте копіювання вказівника на пам'ять)",
         "Якщо alloc == other.alloc → крадіжка буфера O(1).\nЯкщо alloc != other.alloc → виділення свого буфера,\nпоелементний move і O(N) час!",
         POS),
        ("Обмін (swap)\n(propagate_on_container_swap)",
         "Алокатори міняються місцями;\nбуфери міняються вказівниками за O(1)",
         "Якщо alloc == other.alloc → swap вказівників O(1).\nЯкщо alloc != other.alloc → Невизначена поведінка (UB)!",
         POS),
    ]

    y0, dy, bh = 98, 100, 88
    for i, (name, if_true, if_false, col) in enumerate(rows):
        y = y0 + i * dy
        f.append(fitbox(cols[0][0], y, cols[0][1], bh, name, size=11, bold=True, fill=FILL, stroke=LINE, color=INK))
        f.append(fitbox(cols[1][0], y, cols[1][1], bh, if_true, size=11, fill="#eef7ee", stroke=FIELD, color=FIELD))
        f.append(fitbox(cols[2][0], y, cols[2][1], bh, if_false, size=11,
                        fill="#fdecea" if col == POS else FILL, stroke=col, color=col))

    f.append(fitbox(40, 408, 860, 46,
                    "Критичний нюанс: нерівні алокатори ламають гарантію O(1) для move-операцій "
                    "і призводять до UB у swap, якщо поширення вимкнено.",
                    size=12, bold=True, fill=FILL, stroke=LINE, color=INK))

    render(os.path.join(IMG, 'allocator-propagation-matrix.svg'), W, H, *f,
           title="Поведінка алокаторів при копіюванні, переміщенні та обміні")


if __name__ == '__main__':
    fig_allocator_layers()
    fig_allocator_types_contrast()
    fig_pmr_erasure_hierarchy()
    fig_allocator_propagation_matrix()
    print('ok')
