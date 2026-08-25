# -*- coding: utf-8 -*-
"""Фігури до теми «std::expected: монадичне оброблення помилок без винятків»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Макет пам'яті std::expected<T, E> ──────────────────────────────────
def fig_expected_layout():
    W, H = 940, 430
    f = []

    f.append(text(50, 40, "Макет пам'яті std::expected<T, E> (Теговане об'єднання на стеку)", size=16, color=INK, anchor="start", bold=True))

    # Стан 1: Успішне значення (has_value == true)
    f.append(text(50, 75, "Стан 1: Успішний результат (Значення T активне)", size=14, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(50, 95, 540, 110,
                    "Об'єкт std::expected<std::string, std::error_code> (на стеку):\n"
                    "┌───────────────────────────────────────────────┬──────────────┐\n"
                    "│ Буфер під корисне значення T (std::string)   │ Прапорець    │\n"
                    "│ ptr: 0x7fff... | size: 14 | capacity: 31      │ bool: true   │\n"
                    "└───────────────────────────────────────────────┴──────────────┘",
                    size=12, fill="#e8f6ee", stroke=FIELD))

    f.append(arrow(600, 150, 680, 150, color=FIELD, sw=2))

    f.append(fitbox(685, 95, 205, 110,
                    "Доступ через:\n"
                    "• *exp або exp.value()\n"
                    "• exp->length()\n"
                    "Конструктор T викликано в осередку storage_", size=11, fill="#f4f6f8", stroke=LINE))

    # Стан 2: Помилка (has_value == false)
    f.append(text(50, 235, "Стан 2: Помилка (Значення E активне через std::unexpected)", size=14, color=NEG, anchor="start", bold=True))
    f.append(fitbox(50, 255, 540, 110,
                    "Об'єкт std::expected<std::string, std::error_code> (на стеку):\n"
                    "┌───────────────────────────────────────────────┬──────────────┐\n"
                    "│ Буфер під помилку E (std::error_code)         │ Прапорець    │\n"
                    "│ val: 2 (ENOENT) | cat: &generic_category()    │ bool: false  │\n"
                    "└───────────────────────────────────────────────┴──────────────┘",
                    size=12, fill="#fff0f0", stroke=NEG))

    f.append(arrow(600, 310, 680, 310, color=NEG, sw=2))

    f.append(fitbox(685, 255, 205, 110,
                    "Доступ через:\n"
                    "• exp.error()\n"
                    "• exp.has_value() == false\n"
                    "Спроба *exp — UB!\n"
                    "value() кидає bad_expected_access", size=11, fill="#f4f6f8", stroke=LINE))

    f.append(text(470, 400, "sizeof(std::expected<T, E>) = max(sizeof(T), sizeof(E)) + align_padding + sizeof(bool)", size=11, color=MUTED))

    render(os.path.join(OUT, 'expected-layout.svg'), W, H, *f,
           title="Макет пам'яті std::expected")


# ── 2. Монадичний конвеєр оброблення помилок ─────────────────────────────
def fig_monadic_pipeline():
    W, H = 940, 440
    f = []

    f.append(text(50, 35, "Конвеєр монадичних трансформацій std::expected", size=16, color=INK, anchor="start", bold=True))

    # Початковий виклик
    f.append(fitbox(50, 65, 180, 80, "read_file(path)\n───►\nstd::expected<string, Error>", size=12, fill="#eef2f7", stroke=LINE))

    # Гілка success і error після read_file
    f.append(arrow(230, 105, 280, 75, color=FIELD, sw=2))
    f.append(arrow(230, 105, 280, 135, color=NEG, sw=2))

    f.append(text(250, 60, "Value(string)", size=10, color=FIELD, bold=True))
    f.append(text(250, 150, "Err(IoError)", size=10, color=NEG, bold=True))

    # Етап 1: and_then(parse_json)
    f.append(fitbox(285, 45, 200, 60, ".and_then(parse_json)\n(виклики лише при Value)", size=11, fill="#e8f6ee", stroke=FIELD))
    # Обхід помилки в bypass
    f.append(line(285, 135, 515, 135, color=NEG, sw=2, dash="4 4"))

    # Гілка після parse_json
    f.append(arrow(485, 75, 520, 75, color=FIELD, sw=2))

    # Етап 2: transform(extract_config)
    f.append(fitbox(525, 45, 200, 60, ".transform(extract_user)\n(чиста функція T1 -> T2)", size=11, fill="#e8f6ee", stroke=FIELD))
    f.append(line(515, 135, 755, 135, color=NEG, sw=2, dash="4 4"))

    f.append(arrow(725, 75, 760, 75, color=FIELD, sw=2))
    f.append(arrow(755, 135, 760, 135, color=NEG, sw=2))

    # Відновлення через or_else
    f.append(fitbox(765, 45, 140, 120, "Результат:\n.or_else(fallback)\n\nПомилка пролітає\nповз and_then,\nале перехоплюється\nв or_else()", size=10, fill="#fff7e6", stroke=POS))

    # Розділювач та підсумок дій
    f.append(line(40, 195, 900, 195, color=MUTED, sw=1, dash="6 5"))

    # Таблиця сигнатур
    f.append(text(50, 225, "Правила проходження сигналів у монадичних операторах:", size=13, color=INK, anchor="start", bold=True))

    f.append(fitbox(50, 245, 410, 160,
                    "and_then(f): T -> std::expected<U, E>\n"
                    "• Якщо has_value() == true  ──► викликає f(value()), повертає новий expected<U, E>\n"
                    "• Якщо has_value() == false ──► пропускає f, повертає std::unexpected(error())",
                    size=11, fill="#f4f6f8", stroke=LINE))

    f.append(fitbox(480, 245, 410, 160,
                    "transform(f): T -> U\n"
                    "• Якщо has_value() == true  ──► обгортає f(value()) у новий expected<U, E>\n"
                    "• Якщо has_value() == false ──► повертає std::unexpected(error()) без змін",
                    size=11, fill="#f4f6f8", stroke=LINE))

    render(os.path.join(OUT, 'monadic-pipeline-flow.svg'), W, H, *f,
           title="Монадичний конвеєр std::expected")


# ── 3. Порівняльний спектр стратегій оброблення помилок ──────────────────
def fig_error_handling_spectrum():
    W, H = 940, 420
    f = []

    f.append(text(50, 35, "Спектр методів оброблення помилок у C++: Детермінізм проти Зручності", size=16, color=INK, anchor="start", bold=True))

    # Колонки матриці
    col_w = 200
    gap = 15

    # 1. C-Style (errno / return code)
    f.append(fitbox(50, 65, col_w, 310,
                    "C Return Codes / errno\n\n"
                    "➕ Оверхед: 0 байтів\n"
                    "➕ Таблиці винятків: Ні\n"
                    "➕ Виклик: 100% детермінований\n\n"
                    "➖ Типобезпека: Низька (-1)\n"
                    "➖ Контроль: Легко ігнорувати\n"
                    "➖ Канал: Забруднює результат\n"
                    "➖ Читабельність: goto out / nested if",
                    size=11, fill="#f4f6f8", stroke=LINE))

    # 2. C++ Exceptions (try / catch)
    f.append(fitbox(50 + col_w + gap, 65, col_w, 310,
                    "C++ Exceptions\n\n"
                    "➕ Читабельність: Висока\n"
                    "➕ Ігнорування: Неможливо\n"
                    "➕ Контекст: Повний (call stack)\n\n"
                    "➖ Оверхед: Блоут тексту (.eh_frame)\n"
                    "➖ Надійність: Надертермінова затримка стеку\n"
                    "➖ Сфера: Заборонено в RTOS / Kernel",
                    size=11, fill="#fff0f0", stroke=NEG))

    # 3. std::optional<T>
    f.append(fitbox(50 + (col_w + gap)*2, 65, col_w, 310,
                    "std::optional<T>\n\n"
                    "➕ Оверхед: Лише sizeof(bool)\n"
                    "➕ Без винятків: Детерміновано\n"
                    "➕ Типобезпека: Висока\n\n"
                    "➖ Інформативність: Лише факт 'немає'\n"
                    "➖ Причина: Втрачено код помилки\n"
                    "➖ Композиція: Потребує C++23 monadic",
                    size=11, fill="#fff7e6", stroke=POS))

    # 4. std::expected<T, E>
    f.append(fitbox(50 + (col_w + gap)*3, 65, col_w, 310,
                    "std::expected<T, E>\n\n"
                    "💎 Оверхед: Зафіксований на стеку\n"
                    "💎 Детермінізм: 100% передбачуваний\n"
                    "💎 Причина: Повний тип помилки E\n"
                    "💎 Композиція: and_then / transform\n"
                    "💎 Прозорість: Явний тип повернення",
                    size=11, fill="#e8f6ee", stroke=FIELD))

    f.append(text(470, 395, "std::expected поєднує детермінізм C-кодів із читабельністю винятків та типобезпекою C++", size=11, color=MUTED))

    render(os.path.join(OUT, 'error-handling-tradeoffs.svg'), W, H, *f,
           title="Порівняльний спектр оброблення помилок")


def main():
    fig_expected_layout()
    fig_monadic_pipeline()
    fig_error_handling_spectrum()
    print("Фігури успішно згенеровано.")

if __name__ == '__main__':
    main()
