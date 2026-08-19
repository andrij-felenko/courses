# -*- coding: utf-8 -*-
"""Фігури теми «std::launder і повторне використання сховища»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_storage_reuse_invariant():
    """Повторне використання пам'яті й оптимізація Constant Propagation: зіткнення інваріантів."""
    W, H = 960, 480
    f = []

    # ── Заголовки колонок
    f.append(fitbox(40, 30, 420, 40, "Без std::launder (невизначена поведінка)",
                    size=14, bold=True, fill="#fdecea", stroke=POS, color=POS))
    f.append(fitbox(500, 30, 420, 40, "Із застосуванням std::launder (коректно)",
                    size=14, bold=True, fill="#eef7ee", stroke=FIELD, color=FIELD))

    # ── Загальна початкова точка
    f.append(fitbox(280, 85, 400, 44, "Пам'ять 0x1000: Config{ const int id = 100; }\nКомпілятор кешує id = 100 у регістрі",
                    size=12, bold=False, fill="#eef2f7", stroke=MUTED, color=INK))

    # Стрілки розгалуження
    f.append(arrow(380, 132, 250, 155, color=MUTED, sw=1.5))
    f.append(arrow(580, 132, 710, 155, color=MUTED, sw=1.5))

    # ── Ліва колонка (без launder)
    f.append(fitbox(50, 160, 400, 50, "1. p->~Config()  // знищення старого об'єкта\n2. new (p) Config{500}  // запис 500 у пам'ять 0x1000",
                    size=12, fill=FILL, stroke=LINE))
    f.append(arrow(250, 212, 250, 235, color=LINE, sw=1.5))

    f.append(fitbox(50, 240, 400, 60, "Читання через старий вказівник: int x = p->id;\nОптимізатор: «id константний, отже не змінювався».\nЗначення береться з регістра (100 замість 500)!",
                    size=12, bold=True, fill="#fdecea", stroke=POS, color=POS))
    f.append(arrow(250, 302, 250, 325, color=POS, sw=1.5))

    f.append(fitbox(50, 330, 400, 52, "Порушення інваріантів абстрактної машини:\nтихе пошкодження логіки (Silent Data Corruption)",
                    size=12, fill="#fdecea", stroke=POS, color=POS))

    # ── Права колонка (із launder)
    f.append(fitbox(510, 160, 400, 50, "1. p->~Config()  // знищення старого об'єкта\n2. new (p) Config{500}  // запис 500 у пам'ять 0x1000",
                    size=12, fill=FILL, stroke=LINE))
    f.append(arrow(710, 212, 710, 235, color=LINE, sw=1.5))

    f.append(fitbox(510, 240, 400, 60, "Бар'єр оптимізатора: auto* np = std::launder(p);\nЧитання через оновлений вказівник: int x = np->id;\nОптимізатор зобов'язаний перечитати пам'ять!",
                    size=12, bold=True, fill="#eef7ee", stroke=FIELD, color=FIELD))
    f.append(arrow(710, 302, 710, 325, color=FIELD, sw=1.5))

    f.append(fitbox(510, 330, 400, 52, "Завантаження з RAM/кешу: x отримує 500.\nІнваріанти збережено, нуль накладних витрат у рантаймі.",
                    size=12, fill="#eef7ee", stroke=FIELD, color=FIELD))

    # Підсумок унизу
    f.append(text(480, 430,
                  "std::launder розриває ланцюжок припущень оптимізатора про незмінність const-полів за фіксованою адресою.",
                  size=13, color=INK))

    render(os.path.join(IMG, 'storage-reuse-invariant.svg'), W, H, *f,
           title="Повторне використання пам'яті й оптимізація Constant Propagation")


def fig_transparent_replacement_decision():
    """Дерево рішень [basic.life]: коли старий вказівник дійсний автоматично, а коли потрібен std::launder."""
    W, H = 960, 520
    f = []

    f.append(fitbox(280, 20, 400, 42, "Створення нового об'єкта Y у сховищі X (placement new)",
                    size=13, bold=True, fill="#eef2f7", stroke=MUTED, color=INK))
    f.append(arrow(480, 64, 480, 85, color=MUTED, sw=1.5))

    # Рівень 1: той самий тип?
    f.append(fitbox(300, 90, 360, 42, "Тип Y точно збігається з типом X?",
                    size=13, bold=True, fill=FILL, stroke=LINE))
    f.append(arrow(300, 111, 190, 111, color=POS, sw=1.5))
    f.append(text(245, 103, "Ні", size=11, color=POS, bold=True))
    f.append(arrow(480, 134, 480, 160, color=FIELD, sw=1.5))
    f.append(text(495, 148, "Так", size=11, color=FIELD, bold=True))

    # Гілка "Інший тип"
    f.append(fitbox(20, 90, 160, 42, "Потрібен std::launder\n(або вказівник new)",
                    size=11, fill="#fdecea", stroke=POS, color=POS))

    # Рівень 2: чи є повним об'єктом?
    f.append(fitbox(290, 165, 380, 42, "X і Y — повні об'єкти (не підоб'єкти базових класів)?",
                    size=12, bold=True, fill=FILL, stroke=LINE))
    f.append(arrow(290, 186, 190, 186, color=POS, sw=1.5))
    f.append(text(240, 178, "Ні", size=11, color=POS, bold=True))
    f.append(arrow(480, 209, 480, 235, color=FIELD, sw=1.5))
    f.append(text(495, 223, "Так", size=11, color=FIELD, bold=True))

    # Гілка "Підоб'єкт"
    f.append(fitbox(20, 165, 160, 42, "Потрібен std::launder\n(зміна ієрархії)",
                    size=11, fill="#fdecea", stroke=POS, color=POS))

    # Рівень 3: const або посилання?
    f.append(fitbox(270, 240, 420, 46, "Чи містить тип X нестатичні const-поля\nабо поля-посилання (T&)?",
                    size=12, bold=True, fill=FILL, stroke=LINE))
    f.append(arrow(692, 263, 780, 263, color=POS, sw=1.5))
    f.append(text(735, 255, "Так", size=11, color=POS, bold=True))
    f.append(arrow(480, 288, 480, 315, color=FIELD, sw=1.5))
    f.append(text(495, 302, "Ні", size=11, color=FIELD, bold=True))

    # Гілка "Є const або &"
    f.append(fitbox(790, 240, 150, 46, "Автозаміни НЕМАЄ!\nПотрібен std::launder",
                    size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))

    # Рівень 4: віртуальні методи / девіртуалізація
    f.append(fitbox(270, 320, 420, 46, "Чи змінюється динамічний тип поліморфного\nоб'єкта або його віртуальна таблиця?",
                    size=12, bold=True, fill=FILL, stroke=LINE))
    f.append(arrow(692, 343, 780, 343, color=POS, sw=1.5))
    f.append(text(735, 335, "Так", size=11, color=POS, bold=True))
    f.append(arrow(480, 368, 480, 395, color=FIELD, sw=1.5))
    f.append(text(495, 382, "Ні", size=11, color=FIELD, bold=True))

    # Гілка "Зміна vptr"
    f.append(fitbox(790, 320, 150, 46, "Девіртуалізація!\nПотрібен std::launder",
                    size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))

    # Фінал: прозоре заміщення
    f.append(fitbox(280, 400, 400, 52, "Прозоре заміщення (Transparently Replaceable):\nстарий вказівник автоматично вказує на новий об'єкт.\nstd::launder не потрібен.",
                    size=12, bold=True, fill="#eef7ee", stroke=FIELD, color=FIELD))

    f.append(text(480, 485,
                  "Якщо хоча б одна перевірка дає збій — старий вказівник стає «висячим», а звернення через нього — UB.",
                  size=13, color=INK))

    render(os.path.join(IMG, 'transparent-replacement-decision.svg'), W, H, *f,
           title="Умови прозорого заміщення об'єктів у C++")


def fig_launder_provenance_barrier():
    """Граф походження (Provenance) і бар'єр оптимізації std::launder в SSA-поданні."""
    W, H = 940, 440
    f = []

    # Верхній блок: Адреса пам'яті
    f.append(fitbox(340, 25, 260, 36, "Фізична адреса сховища: 0x2000",
                    size=12, fill="#eef2f7", stroke=MUTED, color=INK))

    # Зліва: SSA-граф без launder
    f.append(fitbox(40, 80, 390, 34, "SSA-граф без бар'єра походження",
                    size=13, bold=True, fill="#fdecea", stroke=POS, color=POS))

    f.append(fitbox(50, 130, 370, 42, "%ptr_old = getelementptr ... (об'єкт 1)\n%val1 = load %ptr_old [!invariant.load]",
                    size=11, fill=FILL, stroke=LINE))
    f.append(arrow(235, 174, 235, 195, color=LINE, sw=1.5))

    f.append(fitbox(50, 198, 370, 42, "store 500, %ptr_old (placement new об'єкта 2)\nОптимізатор вважає store несуттєвим для %val1",
                    size=11, fill=FILL, stroke=LINE))
    f.append(arrow(235, 242, 235, 263, color=POS, sw=1.5))

    f.append(fitbox(50, 266, 370, 52, "%val2 = %val1 (оптимізація Load CSE / ConstProp)\nРезультат: використовується старе значення 100!",
                    size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))

    # Справа: SSA-граф із launder
    f.append(fitbox(510, 80, 390, 34, "SSA-граф із бар'єром std::launder",
                    size=13, bold=True, fill="#eef7ee", stroke=FIELD, color=FIELD))

    f.append(fitbox(520, 130, 370, 42, "%ptr_old = getelementptr ... (об'єкт 1)\n%val1 = load %ptr_old [!invariant.load]",
                    size=11, fill=FILL, stroke=LINE))
    f.append(arrow(705, 174, 705, 195, color=LINE, sw=1.5))

    f.append(fitbox(520, 198, 370, 42, "store 500, %ptr_old (placement new об'єкта 2)\n%ptr_new = call @llvm.launder(%ptr_old)",
                    size=11, fill="#eef7ee", stroke=FIELD, color=FIELD))
    f.append(arrow(705, 242, 705, 263, color=FIELD, sw=1.5))

    f.append(fitbox(520, 266, 370, 52, "%val2 = load %ptr_new (новий SSA-вузол)\nОптимізатор зобов'язаний виконати реальне читання 500!",
                    size=11, bold=True, fill="#eef7ee", stroke=FIELD, color=FIELD))

    # Розділювач
    f.append(line(470, 80, 470, 340, color=MUTED, sw=1, dash="4,4"))

    # Пояснення
    f.append(text(470, 380,
                  "std::launder створює новий SSA-вузол вказівника, відрізаючи спадковість попередніх invariant-метаданих.",
                  size=13, color=INK))

    render(os.path.join(IMG, 'launder-provenance-barrier.svg'), W, H, *f,
           title="Граф походження та бар'єр оптимізації std::launder")


if __name__ == '__main__':
    fig_storage_reuse_invariant()
    fig_transparent_replacement_decision()
    fig_launder_provenance_barrier()
    print("Фігури успішно згенеровано.")
