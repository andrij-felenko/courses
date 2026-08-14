# -*- coding: utf-8 -*-
"""Фігури до теми «Двофазний пошук імен у шаблонах»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_two_phases_timeline():
    W, H = 1020, 520
    f = []

    # Заголовок
    f.append(textbox(510, 45, "Два етапи аналізу шаблону компілятором",
                     size=16, bold=True, fill="#eef3f8")[0])

    # Фаза 1: Оголошення шаблону
    f.append(rect(40, 95, 440, 310, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(260, 125, "Фаза 1: Аналіз визначення (Definition Time)", size=15, bold=True))
    f.append(mtext(260, 165, ["Компілятор бачить сирий шаблон без T;",
                              "перевіряється синтаксична коректність;"],
                   size=13, color=MUTED))

    f.append(textbox(260, 235, "Незалежні імена (Non-dependent)\nПрив'язуються негайно через звичайний пошук",
                     size=13, fill="#eaf0fd", stroke=NEG)[0])
    f.append(textbox(260, 325, "Залежні імена (Dependent)\nПеревіряється лише синтаксис, пошук ВІДКЛАДАЄТЬСЯ",
                     size=13, fill="#fff8e7", stroke=FIELD)[0])

    # Стрілка переходу
    f.append(arrow(485, 250, 535, 250))
    f.append(text(510, 235, "T = Concrete", size=12, bold=True, color=MUTED))

    # Фаза 2: Інстанціювання шаблону
    f.append(rect(540, 95, 440, 310, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(760, 125, "Фаза 2: Інстанціювання (Instantiation Time)", size=15, bold=True))
    f.append(mtext(760, 165, ["Відомий конкретний тип T (наприклад Widget);",
                              "створюється конкретний код у POI;"],
                   size=13, color=MUTED))

    f.append(textbox(760, 235, "Підстановка параметрів T → Widget\nГенерується AST конкретної функції/класу",
                     size=13, fill="#eef7ee", stroke=POS)[0])
    f.append(textbox(760, 325, "Розв'язання залежних імен\nПошук у контексті POI + ADL в асоційованих просторах",
                     size=13, fill="#fdecea", stroke=POS)[0])

    # Нижній підсумок
    f.append(arrow(260, 410, 510, 450))
    f.append(arrow(760, 410, 510, 450))
    f.append(textbox(510, 475, "Результат: Незалежні імена зафіксовані на Фазі 1, залежні — розв'язані на Фазі 2",
                     size=14, bold=True, fill="#f4f4f6", stroke=MUTED)[0])

    render(os.path.join(OUT, 'two-phases-timeline.svg'), W, H, *f)


def fig_dependent_vs_nondependent():
    W, H = 1000, 490
    f = []

    # Заголовок
    f.append(textbox(500, 45, "Класифікація імен всередині шаблону template<typename T>",
                     size=16, bold=True, fill="#eef3f8")[0])

    # Корінь
    f.append(textbox(500, 110, "Ім'я у виразі або оголошенні", size=14, bold=True)[0])
    f.append(arrow(400, 130, 270, 170))
    f.append(arrow(600, 130, 730, 170))

    # Ліва гілка: Незалежні імена
    f.append(rect(40, 175, 440, 220, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(260, 205, "Незалежне ім'я (Non-dependent)", size=15, bold=True))
    f.append(mtext(260, 250, ["Не залежить від параметрів шаблону:",
                              "• std::cout, int, std::vector<int>",
                              "• helper(42) — аргумент 42 має тип int",
                              "• Base::foo() — кваліфіковано неконкретним базовим"],
                   size=12, color=MUTED))
    f.append(textbox(260, 345, "Фаза 1: Пошук у контексті оголошення шаблону",
                     size=13, fill="#eaf0fd", stroke=NEG)[0])

    # Права гілка: Залежні імена
    f.append(rect(520, 175, 440, 220, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(740, 205, "Залежне ім'я (Dependent)", size=15, bold=True))
    f.append(mtext(740, 250, ["Тип або значення залежить від T:",
                              "• x (де x має тип T), t.field",
                              "• process(x) — тип аргументу T",
                              "• this->foo(), Base<T>::bar(), typename T::type"],
                   size=12, color=MUTED))
    f.append(textbox(740, 345, "Фаза 2: Пошук у POI + ADL типів аргументів",
                     size=13, fill="#fdecea", stroke=POS)[0])

    # Нижній висновок
    f.append(textbox(500, 445, "Помилка класифікації (наприклад, пропущений this->) переносить ім'я з Фази 2 на Фазу 1!",
                     size=14, bold=True, fill="#fff8e7", stroke=FIELD)[0])

    render(os.path.join(OUT, 'dependent-vs-nondependent.svg'), W, H, *f)


def fig_poi_and_adl():
    W, H = 1000, 500
    f = []

    # Заголовок
    f.append(textbox(500, 45, "Точка інстанціювання (POI) та джерела кандидатів для залежного виклику",
                     size=16, bold=True, fill="#eef3f8")[0])

    # Джерело виклику
    f.append(textbox(500, 110, "Залежний виклик process_item(t) всередині template<typename T>",
                     size=14, bold=True, fill="#fff8e7", stroke=FIELD)[0])
    f.append(arrow(380, 130, 260, 175))
    f.append(arrow(620, 130, 740, 175))

    # Джерело 1: Контекст оголошення
    f.append(rect(40, 180, 440, 190, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(260, 210, "1. Область оголошення шаблону", size=15, bold=True))
    f.append(mtext(260, 255, ["Видимі функції та перевантаження,",
                              "оголошені ДО шаблону на Фазі 1.",
                              "Звичайний некваліфікований пошук."],
                   size=13, color=MUTED))
    f.append(textbox(260, 335, "Звичайні перевантаження з місця визначення",
                     size=13, fill="#eaf0fd", stroke=NEG)[0])

    # Джерело 2: ADL у POI
    f.append(rect(520, 180, 440, 190, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(740, 210, "2. ADL у Точці Інстанціювання (POI)", size=15, bold=True))
    f.append(mtext(740, 255, ["Пошук у просторах типів аргументів (T = ns::Widget),",
                              "які можуть бути оголошені ПІСЛЯ шаблону,",
                              "але ДО точки використання в main/бібліотеці."],
                   size=13, color=MUTED))
    f.append(textbox(740, 335, "Перевантаження з асоційованих просторів T",
                     size=13, fill="#fdecea", stroke=POS)[0])

    # Об'єднання
    f.append(arrow(260, 375, 430, 415))
    f.append(arrow(740, 375, 570, 415))
    f.append(textbox(500, 445, "Об'єднана множина кандидатів на Фазі 2 → Обирається найкраще перевантаження",
                     size=14, bold=True, fill="#eef7ee", stroke=POS)[0])

    render(os.path.join(OUT, 'poi-and-adl.svg'), W, H, *f)


if __name__ == '__main__':
    fig_two_phases_timeline()
    fig_dependent_vs_nondependent()
    fig_poi_and_adl()
    print("Figures generated successfully!")
