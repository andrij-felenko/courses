# -*- coding: utf-8 -*-
"""Фігури теми «std-типи без купи: array, span, string_view, optional»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_heap_vs_freestanding_memory():
    """Порівняння моделі динамічної купи та детермінованої пам'яті без купи."""
    W, H = 960, 520
    f = []

    # Заголовки двох моделей
    f.append(fitbox(40, 25, 420, 36, "Динамічна купа: фрагментація та небезпека", size=13, bold=True,
                    fill="#fdecea", stroke=POS, color=POS))
    f.append(fitbox(500, 25, 420, 36, "Freestanding без купи: детермінована пам'ять", size=13, bold=True,
                    fill="#eef7ee", stroke=FIELD, color=FIELD))

    # Ліва колонка: Проблеми динамічної купи
    f.append(fitbox(40, 75, 420, 26, "ОЗП мікроконтролера з купою (malloc / new / std::vector)", size=11, bold=True,
                    fill="#f4f6f8", stroke=MUTED, color=MUTED))

    # Смуга пам'яті купи з дірками
    chunks = [
        ("Зайнято: obj1 (64 Б)", 40, 95, "#fadbd8", POS),
        ("Дірка (32 Б)", 135, 60, "#eaecee", MUTED),
        ("Зайнято: obj2 (128 Б)", 195, 120, "#fadbd8", POS),
        ("Дірка (48 Б)", 315, 70, "#eaecee", MUTED),
        ("obj3 (64 Б)", 385, 75, "#fadbd8", POS),
    ]
    for lbl, x_c, w_c, fill_c, str_c in chunks:
        f.append(rect(x_c, 110, w_c, 50, fill=fill_c, stroke=str_c, sw=1.5))
        f.append(fitbox(x_c + 2, 122, w_c - 4, 26, lbl, size=9, bold=True, fill=fill_c, stroke=fill_c, color=INK))

    f.append(fitbox(40, 175, 420, 120,
        "• Невизначений час алокації: O(N) пошук вільного блоку\n"
        "• Фрагментація RAM: пам'ять є, але неперервного шматка нема\n"
        "• Ризик вичерпання пам'яті (OOM) і раптового аварійного збою\n"
        "• Заборонено в MISRA C++, DO-178C та ISO 26262",
        size=11, pad=8, fill=BG, stroke=POS))

    f.append(fitbox(40, 310, 420, 180,
        "Ціна покажчиків і метаданих:\n"
        "Кожен блок у купі вимагає прихованого заголовка (8–16 байтів)\n"
        "із розміром та прапорцями стану. При частих дрібних виділеннях\n"
        "накладні витрати пам'яті перевищують обсяг корисних даних,\n"
        "а збій виділення в обробнику переривання веде до паніки ядра.",
        size=11, pad=10, fill="#fdf2e9", stroke="#e67e22"))

    # Права колонка: Модель Freestanding без купи
    f.append(fitbox(500, 75, 420, 26, "Статичні області пам'яті та безпечні проєкції", size=11, bold=True,
                    fill="#eef2f7", stroke=FIELD, color=FIELD))

    # Секції пам'яті праворуч
    f.append(rect(500, 110, 130, 50, fill="#d4edda", stroke=FIELD, sw=1.5))
    f.append(fitbox(502, 113, 126, 22, "Flash (.rodata)", size=9, bold=True, fill="#d4edda", stroke="#d4edda", color=FIELD))
    f.append(fitbox(502, 135, 126, 22, "constexpr таблиці", size=9, fill="#d4edda", stroke="#d4edda", color=INK))

    f.append(rect(640, 110, 135, 50, fill="#d4edda", stroke=FIELD, sw=1.5))
    f.append(fitbox(642, 113, 131, 22, "Static RAM (.bss)", size=9, bold=True, fill="#d4edda", stroke="#d4edda", color=FIELD))
    f.append(fitbox(642, 135, 131, 22, "std::array (DMA буфери)", size=9, fill="#d4edda", stroke="#d4edda", color=INK))

    f.append(rect(785, 110, 135, 50, fill="#d4edda", stroke=FIELD, sw=1.5))
    f.append(fitbox(787, 113, 131, 22, "Стек процесу", size=9, bold=True, fill="#d4edda", stroke="#d4edda", color=FIELD))
    f.append(fitbox(787, 135, 131, 22, "std::optional / variant", size=9, fill="#d4edda", stroke="#d4edda", color=INK))

    f.append(fitbox(500, 175, 420, 120,
        "• Гарантований час доступу O(1) без викликів системного алокатора\n"
        "• Нульова фрагментація: розміри визначено на етапі компіляції\n"
        "• Неволодіючі проєкції: std::span та std::string_view над буферами\n"
        "• Значеннєва семантика: збереження об'єктів безпосередньо за місцем",
        size=11, pad=8, fill=BG, stroke=FIELD))

    f.append(fitbox(500, 310, 420, 180,
        "Механізм нульових накладних витрат (Zero-overhead):\n"
        "Об'єкти std::array та std::optional розміщуються безпосередньо\n"
        "у стек-фреймі чи статичному секторі пам'яті. Проєкції std::span\n"
        "і std::string_view передаються в регістрах процесора без жодного\n"
        "копіювання байтів чи динамічного захоплення пам'яті.",
        size=11, pad=10, fill="#eef7ee", stroke=FIELD))

    render(os.path.join(IMG, 'heap-vs-freestanding-memory.svg'), W, H, *f)


def fig_span_and_string_view_layout():
    """Схематичне зображення проєкцій std::span та std::string_view над неперервним DMA-буфером."""
    W, H = 960, 500
    f = []

    # Верхній заголовок: Фізичний буфер
    f.append(fitbox(40, 20, 880, 32, "Фізичний буфер у пам'яті ОЗП: uint8_t dma_rx_buffer[64]", size=12, bold=True,
                    fill="#eef2f7", stroke=LINE, color=INK))

    # Секції фізичного буфера
    f.append(rect(40, 60, 120, 55, fill="#fadbd8", stroke=POS, sw=1.5))
    f.append(fitbox(42, 65, 116, 22, "Заголовок [0..3]", size=10, bold=True, fill="#fadbd8", stroke="#fadbd8", color=POS))
    f.append(fitbox(42, 88, 116, 22, "0xAA 0x55 0x01 0x18", size=9, fill="#fadbd8", stroke="#fadbd8", color=INK))

    f.append(rect(160, 60, 440, 55, fill="#d4edda", stroke=FIELD, sw=1.5))
    f.append(fitbox(162, 65, 436, 22, "Корисне текстове навантаження: Payload [4..27] (довжина = 24 байти)", size=10, bold=True, fill="#d4edda", stroke="#d4edda", color=FIELD))
    f.append(fitbox(162, 88, 436, 22, "ASCII рядок: \"+GPS:48.45,35.05,V=12.4,OK\"", size=9, fill="#d4edda", stroke="#d4edda", color=INK))

    f.append(rect(600, 60, 120, 55, fill="#fdebd0", stroke="#e67e22", sw=1.5))
    f.append(fitbox(602, 65, 116, 22, "CRC16 [28..29]", size=10, bold=True, fill="#fdebd0", stroke="#fdebd0", color="#e67e22"))
    f.append(fitbox(602, 88, 116, 22, "0x9F 0x4B", size=9, fill="#fdebd0", stroke="#fdebd0", color=INK))

    f.append(rect(720, 60, 200, 55, fill="#f4f6f8", stroke=MUTED, sw=1.5))
    f.append(fitbox(722, 65, 196, 22, "Вільний хвіст буфера [30..63]", size=10, bold=True, fill="#f4f6f8", stroke="#f4f6f8", color=MUTED))
    f.append(fitbox(722, 88, 196, 22, "незаповнені байти ОЗП", size=9, fill="#f4f6f8", stroke="#f4f6f8", color=MUTED))

    # Стрілки проєкцій
    f.append(arrow(100, 120, 100, 160, color=NEG, sw=2))
    f.append(arrow(380, 120, 380, 160, color=FIELD, sw=2))

    # Нижня частина: std::span та std::string_view
    # Лівий блок: std::span над усім отриманим кадром
    f.append(fitbox(40, 165, 420, 34, "std::span<const uint8_t> frame (повний кадр)", size=12, bold=True,
                    fill="#ebf5fb", stroke=NEG, color=NEG))

    f.append(rect(40, 205, 205, 45, fill="#e8f8f5", stroke=NEG, sw=1.2))
    f.append(fitbox(42, 208, 201, 20, "data_ptr = &buffer[0]", size=10, bold=True, fill="#e8f8f5", stroke="#e8f8f5", color=INK))
    f.append(fitbox(42, 228, 201, 18, "вказівник на початок кадру", size=9, fill="#e8f8f5", stroke="#e8f8f5", color=MUTED))

    f.append(rect(255, 205, 205, 45, fill="#e8f8f5", stroke=NEG, sw=1.2))
    f.append(fitbox(257, 208, 201, 20, "size = 30", size=10, bold=True, fill="#e8f8f5", stroke="#e8f8f5", color=INK))
    f.append(fitbox(257, 228, 201, 18, "кількість валідних байтів", size=9, fill="#e8f8f5", stroke="#e8f8f5", color=MUTED))

    f.append(fitbox(40, 260, 420, 215,
        "Властивості std::span:\n"
        "• Не володіє пам'яттю, розмір 2 слова (8 або 16 байтів)\n"
        "• Передається у регістри процесора без копіювання буфера\n"
        "• Безпечний поділ: frame.subspan(4, 24) формує зріз за O(1)\n"
        "• Захист від втрати довжини: завжди знає власні межі\n"
        "• Перетворюється на типізовані байти через std::as_bytes",
        size=11, pad=10, fill=BG, stroke=NEG))

    # Правий блок: std::string_view над текстовим корисним навантаженням
    f.append(fitbox(500, 165, 420, 34, "std::string_view payload (текстова проєкція)", size=12, bold=True,
                    fill="#eef7ee", stroke=FIELD, color=FIELD))

    f.append(rect(500, 205, 205, 45, fill="#eafaf1", stroke=FIELD, sw=1.2))
    f.append(fitbox(502, 208, 201, 20, "ptr = &buffer[4]", size=10, bold=True, fill="#eafaf1", stroke="#eafaf1", color=INK))
    f.append(fitbox(502, 228, 201, 18, "вказівник на символ '+GPS...'", size=9, fill="#eafaf1", stroke="#eafaf1", color=MUTED))

    f.append(rect(715, 205, 205, 45, fill="#eafaf1", stroke=FIELD, sw=1.2))
    f.append(fitbox(717, 208, 201, 20, "length = 24", size=10, bold=True, fill="#eafaf1", stroke="#eafaf1", color=INK))
    f.append(fitbox(717, 228, 201, 18, "кількість символів (без '\\0')", size=9, fill="#eafaf1", stroke="#eafaf1", color=MUTED))

    f.append(fitbox(500, 260, 420, 215,
        "Властивості std::string_view:\n"
        "• Нульовий термінатор '\\0' НЕ потрібен для роботи\n"
        "• Не модифікує вхідний буфер (на відміну від C-функції strtok)\n"
        "• Дозволяє безпечний парсинг Flash-пам'яті (ROM) та ОЗП\n"
        "• Методи remove_prefix / remove_suffix зсувають вікно за O(1)\n"
        "• Порівняння payload == \"+GPS\" виконується без алокації",
        size=11, pad=10, fill=BG, stroke=FIELD))

    render(os.path.join(IMG, 'span-and-string-view-layout.svg'), W, H, *f)


def fig_optional_variant_memory_layout():
    """Схема внутрішнього розташування в пам'яті std::optional та std::variant."""
    W, H = 960, 480
    f = []

    # Ліва колонка: std::optional<T>
    f.append(fitbox(40, 25, 420, 36, "std::optional<uint32_t>: значення або порожнеча", size=13, bold=True,
                    fill="#ebf5fb", stroke=NEG, color=NEG))

    f.append(rect(40, 75, 420, 100, fill="#f4f6f8", stroke=LINE, sw=1.5))
    f.append(fitbox(45, 80, 410, 22, "Розмір: sizeof(T) + alignof(T) = 4 + 4 = 8 байтів", size=11, bold=True,
                    fill="#eef2f7", stroke="#eef2f7", color=INK))

    # Секції пам'яті optional
    f.append(rect(55, 110, 200, 50, fill="#d4edda", stroke=FIELD, sw=1.2))
    f.append(fitbox(57, 115, 196, 20, "T value (4 байти)", size=10, bold=True, fill="#d4edda", stroke="#d4edda", color=FIELD))
    f.append(fitbox(57, 135, 196, 20, "корисні дані (uint32_t)", size=9, fill="#d4edda", stroke="#d4edda", color=INK))

    f.append(rect(260, 110, 80, 50, fill="#fadbd8", stroke=POS, sw=1.2))
    f.append(fitbox(262, 115, 76, 20, "has_val", size=10, bold=True, fill="#fadbd8", stroke="#fadbd8", color=POS))
    f.append(fitbox(262, 135, 76, 20, "bool (1 Б)", size=9, fill="#fadbd8", stroke="#fadbd8", color=INK))

    f.append(rect(345, 110, 100, 50, fill="#eaecee", stroke=MUTED, sw=1.2))
    f.append(fitbox(347, 115, 96, 20, "padding", size=10, bold=True, fill="#eaecee", stroke="#eaecee", color=MUTED))
    f.append(fitbox(347, 135, 96, 20, "вирівнювання 3 Б", size=9, fill="#eaecee", stroke="#eaecee", color=MUTED))

    f.append(fitbox(40, 190, 420, 260,
        "Семантика та життєвий цикл std::optional:\n"
        "• Пам'ять під об'єкт T зарезервована всередині структури заздалегідь\n"
        "• Конструктор T викликається через placement new ТІЛЬКИ при емпласі\n"
        "• При відсутності значення прапорець has_value = false\n"
        "• Деструктор ~T() викликається явно при reset() або знищенні\n"
        "• Повна відсутність магічних констант помилок (-1, 0xFFFFFFFF, NULL)\n"
        "• Ідеально для повернення результатів читання АЦП чи парсингу",
        size=11, pad=10, fill=BG, stroke=NEG))

    # Права колонка: std::variant<T1, T2, T3>
    f.append(fitbox(500, 25, 420, 36, "std::variant<Data, Error, Ping>: типізований союз", size=13, bold=True,
                    fill="#eef7ee", stroke=FIELD, color=FIELD))

    f.append(rect(500, 75, 420, 100, fill="#f4f6f8", stroke=LINE, sw=1.5))
    f.append(fitbox(505, 80, 410, 22, "Розмір: max(sizeof(Ti)) + sizeof(index) + padding = 20 Б", size=11, bold=True,
                    fill="#eef2f7", stroke="#eef2f7", color=INK))

    # Секції пам'яті variant
    f.append(rect(515, 110, 250, 50, fill="#d4edda", stroke=FIELD, sw=1.2))
    f.append(fitbox(517, 115, 246, 20, "Спільний буфер union (16 байтів)", size=10, bold=True, fill="#d4edda", stroke="#d4edda", color=FIELD))
    f.append(fitbox(517, 135, 246, 20, "Data (16 Б) | Error (4 Б) | Ping (1 Б)", size=9, fill="#d4edda", stroke="#d4edda", color=INK))

    f.append(rect(770, 110, 70, 50, fill="#fadbd8", stroke=POS, sw=1.2))
    f.append(fitbox(772, 115, 66, 20, "index_", size=10, bold=True, fill="#fadbd8", stroke="#fadbd8", color=POS))
    f.append(fitbox(772, 135, 66, 20, "дискримінант", size=9, fill="#fadbd8", stroke="#fadbd8", color=INK))

    f.append(rect(845, 110, 60, 50, fill="#eaecee", stroke=MUTED, sw=1.2))
    f.append(fitbox(847, 115, 56, 20, "pad", size=10, bold=True, fill="#eaecee", stroke="#eaecee", color=MUTED))
    f.append(fitbox(847, 135, 56, 20, "3 байти", size=9, fill="#eaecee", stroke="#eaecee", color=MUTED))

    f.append(fitbox(500, 190, 420, 260,
        "Семантика та життєвий цикл std::variant:\n"
        "• Об'єднує альтернативні типи без динамічного виділення пам'яті\n"
        "• Зберігає активний індекс типу (index_ = 0, 1, 2...)\n"
        "• Безпека типів: не дозволяє прочитати помилковий тип (std::holds_alternative)\n"
        "• Обробка подій через std::visit або патерн Overload без віртуальних таблиць\n"
        "• Економія пам'яті: альтернативи використовують один і той самий блок ОЗП\n"
        "• Повна сумісність із freestanding за відсутності винятків",
        size=11, pad=10, fill=BG, stroke=FIELD))

    render(os.path.join(IMG, 'optional-variant-memory-layout.svg'), W, H, *f)


def main():
    fig_heap_vs_freestanding_memory()
    fig_span_and_string_view_layout()
    fig_optional_variant_memory_layout()
    print("All figures generated successfully.")


if __name__ == '__main__':
    main()
