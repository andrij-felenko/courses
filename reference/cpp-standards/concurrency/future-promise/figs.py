# -*- coding: utf-8 -*-
"""Фігури до теми «future й promise: результат з іншого потоку»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

LIVE = "#e8f6ee"
WARM = "#fdecea"
COOL = "#eef2fb"

def fig_shared_state():
    W, H = 840, 420
    f = []

    # Виробник (Promise) ліворуч
    f.append(fitbox(40, 150, 200, 100, "Потік-виробник\n(Producer Thread)\n\nstd::promise<T>", size=13, fill=COOL, stroke=NEG, bold=True))

    # Спільний стан у центрі (Shared State in Heap)
    f.append(rect(290, 60, 260, 280, fill=FILL, stroke=LINE, sw=2, rx=10))
    f.append(text(420, 90, "Shared State (у купі)", size=15, bold=True))
    f.append(line(310, 105, 530, 105, color=LINE, sw=1))

    f.append(fitbox(310, 120, 220, 45, "Значення T / exception_ptr", size=12, fill=LIVE, stroke=FIELD))
    f.append(fitbox(310, 175, 220, 45, "Прапор готовності (ready flag)", size=12, fill=BG, stroke=LINE))
    f.append(fitbox(310, 230, 220, 45, "std::mutex + std::condition_variable", size=11, fill=BG, stroke=LINE))
    f.append(fitbox(310, 285, 220, 40, "Reference Count (лічильник посилань)", size=11, fill=COOL, stroke=NEG))

    # Споживач (Future) праворуч
    f.append(fitbox(600, 150, 200, 100, "Потік-споживач\n(Consumer Thread)\n\nstd::future<T>", size=13, fill=LIVE, stroke=FIELD, bold=True))

    # Стрілки запису та зчитування
    f.append(arrow(240, 175, 290, 175, color=NEG, sw=2))
    f.append(text(265, 160, "set_value()", size=11, color=NEG, bold=True))

    f.append(arrow(550, 175, 600, 175, color=FIELD, sw=2))
    f.append(text(575, 160, "get()", size=11, color=FIELD, bold=True))

    # Пояснювальний підпис внизу
    f.append(text(420, 380, "Захищений м'ютексом одноразовий канал обміну між потоками", size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, 'future-promise-state.svg'), W, H, *f,
           title="Структура Shared State між std::promise та std::future")

def fig_lifecycle():
    W, H = 880, 460
    f = []

    # Стан 1: Початковий
    f.append(fitbox(50, 180, 180, 80, "1. Порожній стан\n(Pending / Empty)\nЧекає на запис", size=12, fill=COOL, stroke=NEG))

    # Переходи до успіху / помилки / відмови
    f.append(arrow(230, 180, 350, 90, color=FIELD, sw=2))
    f.append(text(270, 120, "set_value()", size=11, color=FIELD, bold=True))

    f.append(arrow(230, 220, 350, 220, color=POS, sw=2))
    f.append(text(290, 205, "set_exception()", size=11, color=POS, bold=True))

    f.append(arrow(230, 260, 350, 350, color=MUTED, sw=2))
    f.append(text(265, 335, "~promise() без значення", size=11, color=MUTED, bold=True))

    # Стан 2: Готовий із значенням
    f.append(fitbox(350, 50, 200, 80, "2a. Готовий: Значення\n(Ready Value)\nТ міститься в буфері", size=12, fill=LIVE, stroke=FIELD))

    # Стан 3: Готовий із винятком
    f.append(fitbox(350, 180, 200, 80, "2b. Готовий: Виняток\n(Ready Exception)\nexception_ptr збережено", size=12, fill=WARM, stroke=POS))

    # Стан 4: Зламаний обіцянкою
    f.append(fitbox(350, 310, 200, 80, "2c. Порушена обіцянка\n(Broken Promise)\nfuture_error::broken_promise", size=12, fill=BG, stroke=LINE))

    # Фінальний перехід до Споживання
    f.append(arrow(550, 90, 670, 180, color=FIELD, sw=2))
    f.append(arrow(550, 220, 670, 220, color=POS, sw=2))
    f.append(arrow(550, 350, 670, 260, color=MUTED, sw=2))
    f.append(text(605, 140, "future::get()", size=11, color=INK, bold=True))

    # Стан 5: Спожитий
    f.append(fitbox(670, 180, 180, 80, "3. Спожитий стан\n(Consumed / Invalid)\nvalid() == false", size=12, fill=FILL, stroke=LINE))

    render(os.path.join(OUT, 'shared-state-lifecycle.svg'), W, H, *f,
           title="Життєвий цикл та переходи станів Shared State")

if __name__ == '__main__':
    fig_shared_state()
    fig_lifecycle()
    print("Figures generated successfully.")
