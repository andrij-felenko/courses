# -*- coding: utf-8 -*-
"""Фігури до теми «Шаблони: параметризація типом»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_template_compilation_pipeline():
    W, H = 1040, 520
    f = []

    # Заголовок
    f.append(textbox(520, 35, "Конвеєр інстанціювання шаблону: від рецепта до бінарного коду",
                     size=16, bold=True, fill="#eef3f8")[0])

    # Лівий блок: Шаблон (креслення)
    f.append(rect(40, 75, 270, 380, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(175, 105, "Шаблон (Blueprint)", size=15, bold=True))
    f.append(mtext(175, 140, ["Єдиний вихідний код", "без конкретних типів"], size=12, color=MUTED))
    f.append(textbox(175, 220, "template <typename T>\nclass Vector {\n  T* data_;\n  size_t sz_;\npublic:\n  void push(T val);\n};",
                     size=12, fill="#f8fafc", stroke=LINE)[0])
    f.append(textbox(175, 390, "Пам'ять не виділяється;\nмашинний код відсутній",
                     size=12, fill="#fff8e7", stroke=FIELD)[0])

    # Центральний блок: Аргументи та Компілятор
    f.append(arrow(310, 265, 370, 265))
    f.append(text(340, 250, "Виклик", size=11, bold=True, color=MUTED))

    f.append(rect(375, 75, 290, 380, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(520, 105, "Точка інстанціювання", size=15, bold=True))
    f.append(mtext(520, 140, ["Підстановка аргументів", "та генерація AST"], size=12, color=MUTED))

    f.append(textbox(520, 205, "Vector<int> vi;\nVector<double> vd;\nVector<Widget> vw;",
                     size=12, fill="#eaf0fd", stroke=NEG)[0])
    f.append(arrow(520, 255, 520, 295))
    f.append(textbox(520, 350, "Компілятор C++:\n1. Підстановка T -> Type\n2. Семантична перевірка\n3. Генерація окремих AST",
                     size=12, fill="#f4f6f8", stroke=LINE)[0])

    # Правий блок: Конкретні типи й машинний код
    f.append(arrow(665, 265, 725, 265))
    f.append(text(695, 250, "Кодогенерація", size=11, bold=True, color=MUTED))

    f.append(rect(730, 75, 270, 380, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(865, 105, "Згенеровані класи", size=15, bold=True))
    f.append(mtext(865, 140, ["Повна мономорфізація", "окремий код для кожного T"], size=12, color=MUTED))

    f.append(textbox(865, 200, "class Vector_int {\n  int* data_;\n  void push(int);\n};",
                     size=11, fill="#eef7ee", stroke=POS)[0])
    f.append(textbox(865, 290, "class Vector_double {\n  double* data_;\n  void push(double);\n};",
                     size=11, fill="#eef7ee", stroke=POS)[0])
    f.append(textbox(865, 380, "class Vector_Widget {\n  Widget* data_;\n  void push(Widget);\n};",
                     size=11, fill="#eef7ee", stroke=POS)[0])

    # Нижній підсумок
    f.append(textbox(520, 485, "Статичний поліморфізм: нульовий оверхед під час виконання, оптимізація та інлайнінг кожного типу",
                     size=13, bold=True, fill="#f4f4f6", stroke=MUTED)[0])

    render(os.path.join(OUT, 'template-compilation-pipeline.svg'), W, H, *f)


def fig_template_parameters_taxonomy():
    W, H = 1040, 500
    f = []

    # Заголовок
    f.append(textbox(520, 35, "Таксономія параметрів шаблонів у C++",
                     size=16, bold=True, fill="#eef3f8")[0])

    # Корінь
    f.append(textbox(520, 95, "Параметри шаблону (Template Parameters)", size=14, bold=True)[0])
    f.append(arrow(380, 115, 180, 155))
    f.append(arrow(520, 115, 520, 155))
    f.append(arrow(660, 115, 860, 155))

    # Категорія 1: Параметри-типи
    f.append(rect(30, 160, 300, 270, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(180, 190, "1. Параметри-типи", size=15, bold=True))
    f.append(mtext(180, 225, ["typename T або class T", "Приймають будь-які типи даних"], size=12, color=MUTED))
    f.append(textbox(180, 285, "template <typename T = int>\nvoid swap(T& a, T& b);",
                     size=12, fill="#eaf0fd", stroke=NEG)[0])
    f.append(textbox(180, 375, "Приклади аргументів:\nint, double, std::string,\nstd::vector<int>, void*",
                     size=12, fill="#f4f6f8", stroke=LINE)[0])

    # Категорія 2: Нетипізовані параметри (NTTP)
    f.append(rect(350, 160, 340, 270, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(520, 190, "2. Нетипізовані (NTTP)", size=15, bold=True))
    f.append(mtext(520, 225, ["Константні значення часу компіляції", "Цілі, покажчики, auto, C++20 float/str"], size=12, color=MUTED))
    f.append(textbox(520, 285, "template <typename T, size_t N>\nstruct Array { T buf[N]; };\ntemplate <auto Val> void log();",
                     size=11, fill="#fff8e7", stroke=FIELD)[0])
    f.append(textbox(520, 375, "Еволюція стандарту:\n• C++98: int, enum, вказівники\n• C++17: auto N (виведення типу)\n• C++20: float, double, Literal Class",
                     size=11, fill="#f4f6f8", stroke=LINE)[0])

    # Категорія 3: Параметри-шаблони
    f.append(rect(710, 160, 300, 270, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(860, 190, "3. Параметри-шаблони", size=15, bold=True))
    f.append(mtext(860, 225, ["Шаблони як параметри", "template <typename> class C"], size=12, color=MUTED))
    f.append(textbox(860, 285, "template <typename T,\n  template <typename> class C>\nclass Queue { C<T> data; };",
                     size=11, fill="#fdecea", stroke=POS)[0])
    f.append(textbox(860, 375, "Передається сімейство типів:\nQueue<int, std::vector>\n(без повторення <int>)",
                     size=12, fill="#f4f6f8", stroke=LINE)[0])

    # Нижній висновок
    f.append(textbox(520, 465, "Поєднання трьох категорій створює виразну й строго типізовану систему метапрограмування",
                     size=13, bold=True, fill="#f4f4f6", stroke=MUTED)[0])

    render(os.path.join(OUT, 'template-parameters-taxonomy.svg'), W, H, *f)


def fig_dependent_name_disambiguation():
    W, H = 1040, 480
    f = []

    # Заголовок
    f.append(textbox(520, 35, "Синтаксична неоднозначність залежних імен у шаблонах",
                     size=16, bold=True, fill="#eef3f8")[0])

    # Ліва половина: typename disambiguator
    f.append(rect(40, 75, 460, 335, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(270, 105, "Неоднозначність типу: ключове слово typename", size=14, bold=True))
    f.append(mtext(270, 140, ["Конфлікт: Тлумачення виразу T::name * p;", "Тип (оголошення покажчика) чи статичне поле (множення)?"],
                   size=12, color=MUTED))

    f.append(textbox(270, 205, "T::SubType * ptr;\n// Компілятор вважає: T::SubType — значення,\n// і виконує множення на ptr!",
                     size=12, fill="#fff8e7", stroke=FIELD)[0])
    f.append(arrow(270, 255, 270, 290))
    f.append(textbox(270, 335, "typename T::SubType * ptr;\n// Ключове слово typename явно вказує компілятору:\n// T::SubType є типом даних у залежній області",
                     size=12, fill="#eef7ee", stroke=POS)[0])

    # Права половина: template disambiguator
    f.append(rect(540, 75, 460, 335, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(770, 105, "Неоднозначність методу: префікс template", size=14, bold=True))
    f.append(mtext(770, 140, ["Конфлікт: Тлумачення виразу obj.func<int>(val);", "Виклик методу-шаблону чи операція менше-ніж (obj.func < int)?"],
                   size=12, color=MUTED))

    f.append(textbox(770, 205, "obj.get<int>(0);\n// Символ '<' парситься як оператор 'менше ніж',\n// спричиняючи синтаксичну помилку!",
                     size=12, fill="#fff8e7", stroke=FIELD)[0])
    f.append(arrow(770, 255, 770, 290))
    f.append(textbox(770, 335, "obj.template get<int>(0);\n// Префікс template явно вказує компілятору:\n// символ '<' відкриває список аргументів шаблону",
                     size=12, fill="#eef7ee", stroke=POS)[0])

    # Підсумок
    f.append(textbox(520, 445, "На Фазі 1 компілятор не знає структуру T, тому за замовчуванням вважає всі залежні імена значеннями",
                     size=13, bold=True, fill="#f4f4f6", stroke=MUTED)[0])

    render(os.path.join(OUT, 'dependent-name-disambiguation.svg'), W, H, *f)


if __name__ == '__main__':
    fig_template_compilation_pipeline()
    fig_template_parameters_taxonomy()
    fig_dependent_name_disambiguation()
    print("Figures generated successfully!")
