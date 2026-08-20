# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. bitset-memory-layout: Масив машинних слів та адресація біта ────────────
def fig_bitset_memory_layout():
    W, H = 760, 390
    p = []
    
    p.append(text(W / 2, 30, "Подання множини у вигляді масиву слів uint64_t", size=15, bold=True))
    p.append(text(W / 2, 52, "Кожен біт кодує присутність числа: біт id = 1 якщо id ∈ S, інакше 0", size=11, color=MUTED))

    # Секція слів
    y_words = 74
    # Word 0
    p.append(fitbox(30, y_words, 335, 120,
                    "Слово data[0]  (біти 0 … 63)\n\n"
                    "Біт 2 = 1 (число 2 ∈ S)\n"
                    "Біт 5 = 1 (число 5 ∈ S)\n"
                    "Біт 63 = 1 (число 63 ∈ S)",
                    size=12, fill="#f0f4ff", stroke=NEG, sw=1.8, color=INK))
    
    # Word 1
    p.append(fitbox(395, y_words, 335, 120,
                    "Слово data[1]  (біти 64 … 127)\n\n"
                    "Біт 0 (id 64) = 1 (число 64 ∈ S)\n"
                    "Біт 1 (id 65) = 1 (число 65 ∈ S)\n"
                    "Біт 63 (id 127) = 1 (число 127 ∈ S)",
                    size=12, fill="#fdf2f0", stroke=POS, sw=1.8, color=INK))

    # Формули адресації
    y_math = 210
    p.append(fitbox(30, y_math, 700, 140,
                    "Формула адресації довільного елемента i:\n\n"
                    "Індекс слова у масиві:    word_idx = i >> 6        (еквівалент i / 64)\n"
                    "Зсув біта всередині слова:  bit_offset = i & 63        (еквівалент i % 64)\n"
                    "Бітова маска розряду:      mask = 1ULL << bit_offset\n"
                    "Перевірка: (data[word_idx] & mask) != 0   |   Встановлення: data[word_idx] |= mask",
                    size=12, fill=FILL, stroke=LINE, sw=1.4, color=INK))

    p.append(text(W / 2, H - 12, "Компактність: 1 біт на можливий елемент замість 8 байтів покажчика у вузлах дерев",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "bitset-memory-layout.svg"), W, H, *p)


# ── 2. set-operations-bitwise: Операції над множинами через інструкції ЦП ────
def fig_set_operations_bitwise():
    W, H = 760, 360
    p = []

    p.append(text(W / 2, 30, "Ізоморфізм операцій над множинами та побітових інструкцій ЦП", size=15, bold=True))

    headers = [
        ("Операція над множинами", 160),
        ("Побітова дія", 370),
        ("Машинна інструкція", 570),
    ]
    for title_str, x in headers:
        p.append(text(x, 62, title_str, size=13, bold=True, color=INK))
    p.append(line(30, 74, W - 30, 74, color=LINE, sw=1.5))

    rows = [
        ("A ∩ B  (Перетин)", "A & B  (Побітове І)", "AND  (x86 / ARM) / VPAND (AVX2)", "#eafaf1", FIELD),
        ("A ∪ B  (Об'єднання)", "A | B  (Побітове АБО)", "OR   (x86 / ARM) / VPOR (AVX2)", "#eef4ff", NEG),
        ("A △ B  (Сим. різниця)", "A ^ B  (Побітове XOR)", "XOR  (x86 / ARM) / VPXOR (AVX2)", "#fbf3eb", "#d35400"),
        ("A \\ B  (Різниця)", "A & ~B (Побітове AND-NOT)", "ANDN (x86 BMI1) / BIC (ARM)", "#fdecea", POS),
        ("U \\ A  (Доповнення)", "~A     (Побітове НЕ)", "NOT  (x86 / ARM)", "#f4f6f8", MUTED),
    ]

    y = 86
    for set_op, bit_op, instr, bg_col, stroke_col in rows:
        p.append(rect(30, y, W - 60, 38, fill=bg_col, stroke=stroke_col, sw=1.2, rx=4))
        p.append(text(160, y + 24, set_op, size=12, bold=True, color=INK))
        p.append(text(370, y + 24, bit_op, size=12, bold=True, color=INK))
        p.append(text(570, y + 24, instr, size=12, color=INK))
        y += 46

    p.append(text(W / 2, H - 12, "Одна 64-бітна інструкція обчислює дію для 64 елементів множини одночасно за 1 такт",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "set-operations-bitwise.svg"), W, H, *p)


# ── 3. fast-scan-ctz-popcnt: Апаратні примітиви POPCNT, CTZ та трюк Кернігана ──
def fig_fast_scan_ctz_popcnt():
    W, H = 760, 350
    p = []

    p.append(text(W / 2, 32, "Апаратне сканування бітів: POPCNT, CTZ та пропуск нулів", size=15, bold=True))

    # Ліва колонка: POPCNT
    p.append(fitbox(30, 60, 335, 125,
                    "Потужність множини  |S|\n\n"
                    "POPCNT / __builtin_popcountll\n\n"
                    "Рахує кількість піднятих бітів за 1 такт.\n"
                    "Замінює повільний цикл перевірки 64 бітів.",
                    size=12, fill="#eef4ff", stroke=NEG, sw=1.6, color=INK))

    # Права колонка: CTZ
    p.append(fitbox(395, 60, 335, 125,
                    "Пошук найменшого елемента\n\n"
                    "CTZ / TZCNT / __builtin_ctzll\n\n"
                    "Рахує нулі праворуч до першої «1».\n"
                    "Миттєво дає точний індекс молодшого біта.",
                    size=12, fill="#eafaf1", stroke=FIELD, sw=1.6, color=INK))

    # Нижня частина: Швидка ітерація через x & (x - 1)
    p.append(fitbox(30, 200, 700, 115,
                    "Швидка ітерація по встановлених бітах через скидання молодшого розряду:\n\n"
                    "while (word != 0) {\n"
                    "    int bit = __builtin_ctzll(word);   // Знаходимо найменший елемент за 1 інструкцію\n"
                    "    emit(base + bit);                  // Опрацьовуємо знайдений елемент\n"
                    "    word &= (word - 1);                // Скидаємо молодшу «1» (трюк Кернігана)\n"
                    "}",
                    size=11, fill=FILL, stroke=LINE, sw=1.4, color=INK))

    p.append(text(W / 2, H - 10, "Складність ітерації O(K), де K — кількість елементів, а не довжина всього масиву O(N)",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "fast-scan-ctz-popcnt.svg"), W, H, *p)


# ── 4. roaring-bitmap-containers: Архітектура контейнерів Roaring Bitmaps ────
def fig_roaring_bitmap_containers():
    W, H = 760, 380
    p = []

    p.append(text(W / 2, 30, "Дворівнева архітектура та типи контейнерів Roaring Bitmaps", size=15, bold=True))

    # 32-бітний ID
    p.append(rect(140, 50, 240, 36, fill="#eef4ff", stroke=NEG, sw=1.6, rx=4))
    p.append(text(260, 73, "Старші 16 бітів (Ключ чанка)", size=12, bold=True, color=NEG))
    
    p.append(rect(380, 50, 240, 36, fill="#fdecea", stroke=POS, sw=1.6, rx=4))
    p.append(text(500, 73, "Молодші 16 бітів (0 … 65535)", size=12, bold=True, color=POS))

    # Стрілка вниз до контейнерів
    p.append(arrow(W / 2, 90, W / 2, 115, color=LINE, sw=1.6))

    # Три типи контейнерів
    cw = 220
    ch = 195
    y_box = 120

    # 1. Array Container
    p.append(fitbox(30, y_box, cw, ch,
                    "Array Container\n\n"
                    "Кількість: < 4096 елементів\n\n"
                    "Формат: відсортований масив uint16_t\n\n"
                    "Пам'ять: cardinality × 2 байти\n"
                    "(від 2 байтів до 8 КБ)\n\n"
                    "Ідеально для розріджених даних",
                    size=11, fill="#f4f6f8", stroke=LINE, sw=1.4, color=INK))

    # 2. Bitmap Container
    p.append(fitbox(270, y_box, cw, ch,
                    "Bitmap Container\n\n"
                    "Кількість: 4096 … 61440\n\n"
                    "Формат: фіксований бітсет\n"
                    "1024 × uint64_t = 65536 біт\n\n"
                    "Пам'ять: рівно 8192 байти (8 КБ)\n\n"
                    "Ідеально для щільних даних",
                    size=11, fill="#eef4ff", stroke=NEG, sw=1.6, color=INK))

    # 3. Run Container
    p.append(fitbox(510, y_box, cw, ch,
                    "Run Container (RLE)\n\n"
                    "Кількість: довгі серії\n\n"
                    "Формат: масив пар\n"
                    "[start, length] (uint16_t)\n\n"
                    "Пам'ять: 4 байти на відрізок\n\n"
                    "Ідеально для неперервних діапазонів",
                    size=11, fill="#eafaf1", stroke=FIELD, sw=1.6, color=INK))

    p.append(text(W / 2, H - 12, "Порогове значення 4096: 4096 × 2 B = 8192 B — момент, коли масив стає більшим за бітсет",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "roaring-bitmap-containers.svg"), W, H, *p)


if __name__ == "__main__":
    fig_bitset_memory_layout()
    fig_set_operations_bitwise()
    fig_fast_scan_ctz_popcnt()
    fig_roaring_bitmap_containers()
    print("OK: figures generated in", OUT)
