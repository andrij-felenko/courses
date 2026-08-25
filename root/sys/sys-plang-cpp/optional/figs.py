# -*- coding: utf-8 -*-
"""Фігури до теми «std::optional»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Макет пам'яті std::optional<T> у порівнянні з іншими підходами ─────────────
def fig_optional_layout():
    W, H = 940, 450
    f = []

    f.append(text(470, 35, "Макет пам'яті std::optional<T> та альтернативних підходів", size=16, color=INK, anchor="middle", bold=True))

    # Секція 1: T* на купі (std::unique_ptr<T>)
    f.append(text(50, 75, "1. Указівник на купу (std::unique_ptr<T>): відсутнє значення = nullptr", size=13, color=NEG, anchor="start", bold=True))
    f.append(fitbox(50, 95, 260, 90, "std::unique_ptr<T>\nptr ────────────────┐\n(sizeof = 8 байтів)   │", size=12, fill="#eef2f7", stroke=LINE))
    f.append(arrow(310, 140, 420, 140, color=NEG, sw=2))
    f.append(fitbox(425, 95, 460, 90, "Динамічний буфер у купі (Heap Allocation)\nОб'єкт T [sizeof(T) байтів]\nДодатковий виклик malloc/free + pointer chasing", size=12, fill="#f4f6f8", stroke=LINE))

    # Розділювальна лінія 1
    f.append(line(40, 205, 900, 205, color=MUTED, sw=1, dash="4 4"))

    # Секція 2: std::optional<T> (Порожній і заповнений стан)
    f.append(text(50, 225, "2. std::optional<T>: суцільна пам'ять без купі (Stack-allocated continuous memory)", size=13, color=FIELD, anchor="start", bold=True))

    # Порожній optional (nullopt)
    f.append(fitbox(50, 245, 410, 110,
                    "Порожній стан (std::nullopt):\n"
                    "[ storage: Uninitialized memory (alignas T) ] [ bool has_value = false ]\n"
                    "Конструктор T НЕ викликався. Пам'ять у купі НЕ виділяється.",
                    size=12, fill="#fff7e6", stroke=POS))

    # Заповнений optional (engaged)
    f.append(fitbox(480, 245, 410, 110,
                    "Заповнений стан (Engaged optional):\n"
                    "[ storage: Constructed object T(args...) ] [ bool has_value = true  ]\n"
                    "Об'єкт T сконструйовано за допомогою placement new у буфері.",
                    size=12, fill="#e8f6ee", stroke=FIELD))

    # Примітки щодо розміру
    f.append(text(50, 385, "Обчислення розміру: sizeof(std::optional<T>) = sizeof(T) + alignof(T) (з урахуванням padding байтів)", size=11, color=MUTED, anchor="start"))
    f.append(text(50, 410, "Приклади: optional<char> = 2 байти, optional<int32_t> = 8 байтів, optional<double> = 16 байтів", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'optional-layout.svg'), W, H, *f,
           title="Макет пам'яті std::optional<T>")


# ── 2. Монадичний конвеєр обробки у C++23 ──────────────────────────────────
def fig_monadic_pipeline():
    W, H = 940, 400
    f = []

    f.append(text(470, 35, "Монадичний конвеєр обробки std::optional (C++23)", size=16, color=INK, anchor="middle", bold=True))

    # Вхідні дані
    f.append(fitbox(40, 90, 160, 90, "Вхідні дані\nstd::optional<T>", size=12, fill="#eef2f7", stroke=LINE))

    # Крок 1: and_then
    f.append(arrow(200, 135, 245, 135, color=INK, sw=2))
    f.append(fitbox(250, 90, 180, 90, ".and_then(f)\n[T -> optional<U>]\nКоротке замикання", size=12, fill="#e8f6ee", stroke=FIELD))

    # Крок 2: transform
    f.append(arrow(430, 135, 475, 135, color=INK, sw=2))
    f.append(fitbox(480, 90, 180, 90, ".transform(g)\n[U -> V]\nОбгортка у optional", size=12, fill="#e8f6ee", stroke=FIELD))

    # Крок 3: or_else
    f.append(arrow(660, 135, 705, 135, color=INK, sw=2))
    f.append(fitbox(710, 90, 180, 90, ".or_else(h)\n[ () -> optional<V> ]\nЗапасний результат", size=12, fill="#fff7e6", stroke=POS))

    # Вихідний результат
    f.append(arrow(470, 180, 470, 230, color=INK, sw=2))
    f.append(fitbox(270, 235, 400, 75, "Підсумковий результат: std::optional<V>\n(або обчислене значення, або дефолт без винятків)", size=12, fill="#e8f6ee", stroke=FIELD))

    # Пояснення розгалуження
    f.append(text(470, 345, "Якщо на будь-якому кроці повертається nullopt, and_then та transform пропускають обчислення", size=11, color=MUTED, anchor="middle"))
    f.append(text(470, 365, "or_else активується лише тоді, коли ланцюжок порожній, надаючи альтернативний відновлений результат", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, 'monadic-pipeline.svg'), W, H, *f,
           title="Монадичний конвеєр обробки std::optional")


if __name__ == '__main__':
    fig_optional_layout()
    fig_monadic_pipeline()
    print("Згенеровано фігури в img/")
