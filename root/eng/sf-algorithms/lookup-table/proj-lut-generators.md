# ⚙️ Генерація таблиць замін: від constexpr до векторних інструкцій

Таблиця замін (LUT) може генеруватися на трьох різних етапах життєвого циклу програми: під час складання коду компілятором (**compile-time**), під час запуску системи (**runtime precomputation**) або динамічно в реєстрах процесора за допомогою векторних інструкцій (**in-register SIMD**).

Нижче детально розібрано чотири практичні шаблони проектування таблиць замін, кожен із яких розв'язує свою інженерну задачу: усунення накладних витрат ініціалізації, швидку тригонометрію на мікроконтролерах без FPU, розрахунок контрольних сум без розгалужень та векторизоване перетворення байтів у регістрах процесора.

### 1. Генерація таблиці на етапі компіляції (Compile-Time LUT)

Попередній розрахунок константних таблиць позбавляє програму накладних витрат під час запуску (startup time) і розміщує дані в захищеній від запису секції пам'яті `.rodata` бінарного файлу або у Flash-пам'яті мікроконтролера. Якщо таблиця генерується динамічно під час запуску програми через цикл `init_tables()`, виникає ризик стану гонитви (race condition) у багатопотокових середовищах та витрачається оперативна пам'ять RAM замість ROM.

У мові C традиційним підходом є написання зовнішнього скрипта генерації (на Python або AWK), який формує файл заголовків `.h` із масивом констант, або використання макросів препроцесора. У сучасному C++ (стандарти C++20 та C++23) введено ключове слово `consteval`, яке зобов'язує компілятор виконати весь цикл розрахунку безпосередньо у фронтенді транслятора. Отриманий масив стає константою часу компіляції і не створює жодного коду ініціалізації у виконуваному файлі.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

/* У мові C статичну таблицю визначають як константний масив у секції .rodata.
   Таблиця містить кількість встановлених бітів (popcount) для всіх значень від 0 до 15. */
static const uint8_t NIBBLE_POPCOUNT_LUT[16] = {
    0, /* 0000 -> 0 бітів */
    1, /* 0001 -> 1 біт   */
    1, /* 0010 -> 1 біт   */
    2, /* 0011 -> 2 біти  */
    1, /* 0100 -> 1 біт   */
    2, /* 0101 -> 2 біти  */
    2, /* 0110 -> 2 біти  */
    3, /* 0111 -> 3 біти  */
    1, /* 1000 -> 1 біт   */
    2, /* 1001 -> 2 біти  */
    2, /* 1010 -> 2 біти  */
    3, /* 1011 -> 3 біти  */
    2, /* 1100 -> 2 біти  */
    3, /* 1101 -> 3 біти  */
    3, /* 1110 -> 3 біти  */
    4  /* 1111 -> 4 біти  */
};

uint32_t popcount_lut_byte(uint8_t byte) {
    /* Розбиваємо вхідний 8-бітний байт на два 4-бітних нібли (старший і молодший).
       Маска 0x0F виділяє значення 0..15, гарантуючи захист від виходу за межі масиву. */
    uint8_t low_nibble = byte & 0x0F;
    uint8_t high_nibble = (byte >> 4) & 0x0F;
    return (uint32_t)(NIBBLE_POPCOUNT_LUT[low_nibble] + NIBBLE_POPCOUNT_LUT[high_nibble]);
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>

/* У C++20 функція consteval гарантує, що вся таблиця на 256 елементів 
   буде порахована виключно компілятором під час збірки. */

consteval auto generate_byte_popcount_table() {
    std::array<uint8_t, 256> table{};
    for (size_t i = 0; i < 256; ++i) {
        uint8_t count = 0;
        /* Алгоритм Браяна Кернігана для точного підрахунку одиничних бітів */
        for (uint8_t val = static_cast<uint8_t>(i); val > 0; val &= static_cast<uint8_t>(val - 1)) {
            ++count;
        }
        table[i] = count;
    }
    return table;
}

/* Статична константна таблиця на 256 байтів, розташована у flash/rodata */
inline constexpr auto BYTE_POPCOUNT_LUT = generate_byte_popcount_table();

[[nodiscard]] constexpr uint32_t popcount_buffer(std::span<const uint8_t> data) noexcept {
    uint32_t total = 0;
    for (const uint8_t byte : data) {
        total += BYTE_POPCOUNT_LUT[byte];
    }
    return total;
}
```
:::

Зверніть увагу на машинний код: звернення `BYTE_POPCOUNT_LUT[byte]` транслюється компілятором в одну інструкцію `movzx eax, byte ptr [rip + BYTE_POPCOUNT_LUT + rdi]`. Завдяки розміру таблиці у 256 байтів вона займає всього 4 кеш-лінії по 64 байти, що дозволяє їй постійно залишатися в кеші L1 процесора.

### 2. Тригонометрична LUT з фіксованою комою та лінійною інтерполяцією

Для мікроконтролерів без апаратного блоку плаваючої коми (FPU, наприклад ARM Cortex-M0/M3) обчислення функцій через стандартну бібліотеку `math.h` викликає програмну емуляцію `sinf()`, яка займає від 120 до 450 машинних тактів на кожен виклик.

Рішенням є використання арифметики з фіксованою комою (Fixed-Point Q15). Вхідний кут нормалізують у 16-бітний діапазон `[0, 65535]`, який представляє один повний оберт кола від `0` до `2π`. Старші 8 бітів числа (зсув `>> 8`) вибирають базовий індекс вузла в таблиці з 256 елементів. Молодші 8 бітів числа (маска `& 0xFF`) є нормалізованою дробовою відстанню `frac ∈ [0, 255]` між вузлами. Лінійна інтерполяція виконується за формулою:

```
y = y0 + ((y1 - y0) * frac) >> 8
```

:::tabs
```c
#include <stdint.h>

#define SINE_LUT_BITS  8
#define SINE_LUT_SIZE  (1 << SINE_LUT_BITS)  /* 256 вузлів */
#define SINE_LUT_MASK  (SINE_LUT_SIZE - 1)

/* Опорна таблиця sin(x) на 256 вузлів для повного кола [0, 2π), масштабована в Q15 (-32768..32767).
   Значення згенеровані для sin(2π * i / 256) * 32767. */
static const int16_t SINE_Q15_LUT[256] = {
        0,   804,  1607,  2410,  3211,  4011,  4807,  5601,
     6392,  7179,  7961,  8739,  9511, 10278, 11038, 11792,
    12539, 13278, 14009, 14732, 15446, 16150, 16845, 17530,
    18204, 18867, 19519, 20159, 20787, 21402, 22004, 22594,
    23169, 23731, 24278, 24811, 25329, 25831, 26318, 26789,
    27244, 27683, 28105, 28510, 28897, 29268, 29621, 29955,
    30272, 30571, 30851, 31113, 31356, 31580, 31785, 31970,
    32137, 32284, 32412, 32520, 32609, 32678, 32727, 32757,
    32767, 32757, 32727, 32678, 32609, 32520, 32412, 32284,
    32137, 31970, 31785, 31580, 31356, 31113, 30851, 30571,
    30272, 29955, 29621, 29268, 28897, 28510, 28105, 27683,
    27244, 26789, 26318, 25831, 25329, 24811, 24278, 23731,
    23169, 22594, 22004, 21402, 20787, 20159, 19519, 18867,
    18204, 17530, 16845, 16150, 15446, 14732, 14009, 13278,
    12539, 11792, 11038, 10278,  9511,  8739,  7961,  7179,
     6392,  5601,  4807,  4011,  3211,  2410,  1607,   804,
        0,  -804, -1607, -2410, -3211, -4011, -4807, -5601,
    -6392, -7179, -7961, -8739, -9511,-10278,-11038,-11792,
   -12539,-13278,-14009,-14732,-15446,-16150,-16845,-17530,
   -18204,-18867,-19519,-20159,-20787,-21402,-22004,-22594,
   -23169,-23731,-24278,-24811,-25329,-25831,-26318,-26789,
   -27244,-27683,-28105,-28510,-28897,-29268,-29621,-29955,
   -30272,-30571,-30851,-31113,-31356,-31580,-31785,-31970,
   -32137,-32284,-32412,-32520,-32609,-32678,-32727,-32757,
   -32767,-32757,-32727,-32678,-32609,-32520,-32412,-32284,
   -32137,-31970,-31785,-31580,-31356,-31113,-30851,-30571,
   -30272,-29955,-29621,-29268,-28897,-28510,-28105,-27683,
   -27244,-26789,-26318,-25831,-25329,-24811,-24278,-23731,
   -23169,-22594,-22004,-21402,-20787,-20159,-19519,-18867,
   -18204,-17530,-16845,-16150,-15446,-14732,-14009,-13278,
   -12539,-11792,-11038,-10278, -9511, -8739, -7961, -7179,
    -6392, -5601, -4807, -4011, -3211, -2410, -1607,  -804
};

/* Обчислення sin(angle) у фіксованій комі Q15 з лінійною інтерполяцією.
   angle: 16-бітне ціле число [0..65535], що відповідає [0..2π). */
int16_t sin_fixed_q15_lerp(uint16_t angle) {
    /* Старші 8 бітів — базовий індекс у таблиці */
    uint8_t idx0 = (uint8_t)(angle >> 8);
    /* Наступний вузол замикається по колу через маскування */
    uint8_t idx1 = (uint8_t)((idx0 + 1) & SINE_LUT_MASK);

    /* Молодші 8 бітів — дробова частина t ∈ [0..255] */
    uint8_t frac = (uint8_t)(angle & 0xFF);

    int16_t y0 = SINE_Q15_LUT[idx0];
    int16_t y1 = SINE_Q15_LUT[idx1];

    /* Різниця вузлів розраховується в 32 бітах для запобігання переповненню */
    int32_t delta = (int32_t)(y1 - y0);
    int32_t interpolated = (int32_t)y0 + ((delta * (int32_t)frac) >> 8);

    return (int16_t)interpolated;
}
```
```cpp
#include <cstdint>
#include <array>
#include <numbers>
#include <cmath>

/* Універсальний C++ клас для генерації та швидкої інтерполяції 
   періодичних таблиць замін довільного розміру N */
template <size_t TableBits = 8>
class SineLookupTable {
public:
    static constexpr size_t Size = 1ULL << TableBits;
    static constexpr size_t Mask = Size - 1;

    consteval SineLookupTable() : table_{} {
        constexpr double step = 2.0 * std::numbers::pi / static_cast<double>(Size);
        for (size_t i = 0; i < Size; ++i) {
            double val = std::sin(static_cast<double>(i) * step) * 32767.0;
            table_[i] = static_cast<int16_t>(std::round(val));
        }
    }

    [[nodiscard]] constexpr int16_t operator()(uint16_t angle) const noexcept {
        constexpr uint32_t shift = 16 - TableBits;
        const size_t idx0 = (angle >> shift) & Mask;
        const size_t idx1 = (idx0 + 1) & Mask;
        const auto frac = static_cast<int32_t>(angle & ((1U << shift) - 1));

        const int32_t y0 = table_[idx0];
        const int32_t y1 = table_[idx1];
        const int32_t delta = y1 - y0;

        return static_cast<int16_t>(y0 + ((delta * frac) >> shift));
    }

private:
    std::array<int16_t, Size> table_;
};

inline constexpr SineLookupTable<8> FastSin;
```
:::

Цей алгоритм виконується всього за 6–8 машинних тактів на ядрі ARM Cortex-M4, забезпечуючи точність понад 14 бітів (похибка менша за 0.005%), що ідеально підходить для керування безколекторними двигунами (FOC, Field Oriented Control) та цифрового аудіосинтезу.

### 3. Швидке обчислення контрольної суми CRC32 через 256-елементну таблицю

Обчислення циклічного надлишкового коду CRC32 побітовим алгоритмом вимагає 8 ітерацій на кожен байт, де на кожній ітерації перевіряється молодший біт і виконується умовний XOR з поліномом `0xEDB88320`. Для передачі гігабітних потоків даних такий підхід неприпустимо повільний через залежності за даними та штрафи хибного передбачення переходів.

Табличний метод замінює обробку одного біта на обробку цілого байта (8 бітів) за один крок. Заздалегідь розрахована таблиця на 256 елементів по 4 байти (обсяг 1 КБ) містить залишок ділення на поліном для кожного можливого значення байта:

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

#define CRC32_POLYNOMIAL 0xEDB88320U

static uint32_t CRC32_TABLE[256];
static int CRC32_INITIALIZED = 0;

void crc32_init_table(void) {
    if (CRC32_INITIALIZED) return;
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t crc = i;
        for (uint32_t j = 0; j < 8; j++) {
            crc = (crc & 1) ? ((crc >> 1) ^ CRC32_POLYNOMIAL) : (crc >> 1);
        }
        CRC32_TABLE[i] = crc;
    }
    CRC32_INITIALIZED = 1;
}

uint32_t crc32_calculate(const uint8_t *data, size_t length) {
    crc32_init_table();
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; i++) {
        /* Обчислюємо індекс у таблиці як XOR поточного байта з молодшим байтом CRC */
        uint8_t table_index = (uint8_t)((crc ^ data[i]) & 0xFF);
        /* Оновлюємо акумулятор за один такт зсуву та вибірки */
        crc = CRC32_TABLE[table_index] ^ (crc >> 8);
    }
    return crc ^ 0xFFFFFFFFU;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <string_view>

/* У C++ таблиця CRC32 обчислюється на етапі компіляції 
   та не вимагає перевірок ініціалізації у runtime. */

class CRC32Calculator {
public:
    static constexpr uint32_t Polynomial = 0xEDB88320U;

    static consteval auto generate_table() {
        std::array<uint32_t, 256> table{};
        for (uint32_t i = 0; i < 256; ++i) {
            uint32_t crc = i;
            for (uint32_t j = 0; j < 8; ++j) {
                crc = (crc & 1) ? ((crc >> 1) ^ Polynomial) : (crc >> 1);
            }
            table[i] = crc;
        }
        return table;
    }

    static inline constexpr auto Table = generate_table();

    [[nodiscard]] static constexpr uint32_t compute(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (const uint8_t byte : data) {
            const auto index = static_cast<uint8_t>((crc ^ byte) & 0xFF);
            crc = Table[index] ^ (crc >> 8);
        }
        return crc ^ 0xFFFFFFFFU;
    }

    [[nodiscard]] static constexpr uint32_t compute(std::string_view str) noexcept {
        return compute(std::span{reinterpret_cast<const uint8_t*>(str.data()), str.size()});
    }
};
```
:::

Табличний розрахунок CRC32 дає прискорення у **8.5 раза** порівняно з побітовим варіантом, досягаючи пропускної здатності понад 1.2 ГБ/с на одному процесорному ядрі.

### 4. Векторна внутрішньорегістрова LUT (SIMD In-Register Lookup)

Якщо таблиця замін містить до 16 байтів, вона може повністю поміститися в один 128-бітний SIMD-регістр (`__m128i`). Спеціальна векторна інструкція перестановки байтів `pshufb` (SSSE3 на x86) або `tbl` / `vqtbl1q_u8` (ARM NEON) приймає регістр-таблицю та регістр-індекси, виконуючи 16 незалежних табличних замін одночасно за **1 такт процесора**.

Нижче наведено приклад швидкісного шістнадцяткового кодування 16 байтів у 32 символи ASCII (`0x0..0xF` → `'0'..'9', 'a'..'f'`), який працює повністю всередині регістрів і не виконує жодного звернення до оперативної пам'яті:

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <tmmintrin.h> /* SSSE3 intrinsics */

/* Векторне перетворення 16 байтів у 32 hex-символи через pshufb */
void hex_encode_16bytes_simd(const uint8_t *src, char *dst) {
    /* Завантажуємо 16 байтів у 128-бітний XMM регістр */
    __m128i input = _mm_loadu_si128((const __m128i *)src);

    /* Таблиця замін ASCII: '0'-'9', 'a'-'f' (16 байтів у регістрі XMM) */
    const __m128i hex_lut = _mm_setr_epi8(
        '0', '1', '2', '3', '4', '5', '6', '7',
        '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'
    );

    __m128i mask_low = _mm_set1_epi8(0x0F);

    /* Виділяємо молодші (low) та старші (high) 4-бітні нібли */
    __m128i low_nibbles  = _mm_and_si128(input, mask_low);
    __m128i high_nibbles = _mm_and_si128(_mm_srli_epi16(input, 4), mask_low);

    /* Паралельна таблична заміна 16 байтів за 1 такт інструкцією pshufb! */
    __m128i hex_chars_low  = _mm_shuffle_epi8(hex_lut, low_nibbles);
    __m128i hex_chars_high = _mm_shuffle_epi8(hex_lut, high_nibbles);

    /* Чергуємо старші та молодші символи для отримання правильного ASCII порядку */
    __m128i result_0_15 = _mm_unpacklo_epi8(hex_chars_high, hex_chars_low);
    __m128i result_16_31 = _mm_unpackhi_epi8(hex_chars_high, hex_chars_low);

    /* Зберігаємо 32 байти готового шістнадцяткового рядка */
    _mm_storeu_si128((__m128i *)dst, result_0_15);
    _mm_storeu_si128((__m128i *)(dst + 16), result_16_31);
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <immintrin.h>

class FastHexEncoder {
public:
    static void encode_block_16(std::span<const uint8_t, 16> src, std::span<char, 32> dst) noexcept {
        const __m128i input = _mm_loadu_si128(reinterpret_cast<const __m128i*>(src.data()));

        const __m128i hex_lut = _mm_setr_epi8(
            '0', '1', '2', '3', '4', '5', '6', '7',
            '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'
        );
        const __m128i mask_low = _mm_set1_epi8(0x0F);

        const __m128i low_nibbles  = _mm_and_si128(input, mask_low);
        const __m128i high_nibbles = _mm_and_si128(_mm_srli_epi16(input, 4), mask_low);

        const __m128i hex_low  = _mm_shuffle_epi8(hex_lut, low_nibbles);
        const __m128i hex_high = _mm_shuffle_epi8(hex_lut, high_nibbles);

        const __m128i res_part1 = _mm_unpacklo_epi8(hex_high, hex_low);
        const __m128i res_part2 = _mm_unpackhi_epi8(hex_high, hex_low);

        _mm_storeu_si128(reinterpret_cast<__m128i*>(dst.data()), res_part1);
        _mm_storeu_si128(reinterpret_cast<__m128i*>(dst.data() + 16), res_part2);
    }
};
```
:::

Векторна реалізація перетворює дані зі швидкістю понад 12 ГБ/с на сучасних x86-64 процесорах.

### Інженерні пастки реалізації

1. **Вихід за межі таблиці (Out-of-bounds):** якщо вхідний індекс не маскується, помилка призводить до читання довільної адреси процесу. Якщо розмір таблиці є степенем двійки `2^k`, завжди використовуйте швидку бітову маску `idx & (SIZE - 1)` замість повільної операції взяття за модулем `idx % SIZE`.
2. **Переповнення при множенні різниці інтерполяції:** вираз `(y1 - y0) * frac` обов'язково повинен підноситися до 32-бітного типу зі знаком (`int32_t`). Якщо різниця обчислюється у 16-бітному типі, від'ємні значення призведуть до невизначеної поведінки або спотворення знака.
3. **Хибний поділ кеш-ліній (False Sharing):** динамічні таблиці замін, які спільно використовуються декількома ядрами процесора, повинні мати вирівнювання за межею кеш-лінії (`alignas(64)` у C++ або `__attribute__((aligned(64)))` у C), щоб уникнути втрати продуктивності через когерентність кешів.
