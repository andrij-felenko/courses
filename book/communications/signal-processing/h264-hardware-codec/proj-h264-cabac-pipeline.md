# ⚙️ Реалізація двійкового арифметичного кодера CABAC

Алгоритмічна реалізація показує роботу конвеєра двійкового арифметичного кодування CABAC (Context-Adaptive Binary Arithmetic Coding) стандарту H.264, що використовується в апаратних та програмних кодеках для максимального стиснення синтаксичних елементів.

## Теоретичне підґрунтя та етапи кодування CABAC

Арифметичне кодування дозволяє долати фундаментальне обмеження префіксного кодування Хаффмана, яке вимагає виділяти на кожен символ ціле число бітів (щонайменше 1 біт на символ). Якщо ймовірність появи якогось символу сягає 90%, кодування Хаффмана витрачає марний надлишок 0.9 біта на кожен символ. Арифметичне кодування ділить інтервал ймовірностей на дробові частки, дозволяючи витрачати менше ніж 1 біт на символ (наприклад, 0.15 біта на бінарний символ).

У стандарті H.264 алгоритм CABAC розбитий на чотири послідовні алгоритмічні кроки:

1. **Бінаризація (Binarization):** будь-який недвійковий синтаксичний елемент (наприклад, абсолютне значення коефіцієнта `coeff_abs_level_minus1` або вектор руху `mvd`) перетворюється у двійкову послідовність бінів (Bins). Застосовуються чотири основні схеми бінаризації:
   - *Унарне кодування (Unary — U):* число N кодується як N одиниць і закінчується нулем (наприклад, 3 перетворюється у 1110).
   - *Усічене унарне кодування (Truncated Unary — TU):* застосовується при обмеженому діапазоні значень.
   - *Кодування зафіксованої довжини (Fixed Length — FL):* стандартний звичайний двійковий код.
   - *Експоненціальний код Голомба (Exp-Golomb — EGk):* використовується для великих незв'язаних значень векторів руху.

2. **Моделювання контексту (Context Modeling):** кожен бін двійкової послідовності прив'язується до конкретної моделі контексту з індексом `ctxIdx`. Індекс обчислюється як сума базового зсуву та приросту:
   ```
   ctxIdx = ctxIdxOffset + ctxInc
   ```
   Приріст `ctxInc` обчислюється на основі синтаксичних елементів сусідніх лівого та верхнього макроблоків. Контекст зберігає стан ймовірності `pStateIdx` (від 0 до 63) та найімовірніший символ `valMPS` (0 або 1).

3. **Двійкове арифметичне кодування (Binary Arithmetic Encoding — BAC):** підтримується 9-бітний регістр діапазону `m_range` (значення у межах 256..510) та 10-бітний регістр нижньої межі `m_low`. Діапазон розділяється на піддіапазони MPS та LPS:
   ```
   rLPS = rangeTabLPS[pStateIdx][(m_range >> 6) & 3]
   rMPS = m_range - rLPS
   ```
   Якщо вхідний бін збігається з `valMPS`, розширюється діапазон MPS (`m_range = rMPS`). Якщо бін дорівнює LPS, діапазон звужується (`m_range = rLPS`), а `m_low` зміщується на величину `rMPS`.

4. **Оновлення контексту та ренормалізація (State Update & Renormalization):**
   - Після кодування кожного біна стан ймовірності оновлюється через таблиці переходів: `transIdxMPS` при появі MPS або `transIdxLPS` при появі LPS. При відносно частому виникненні LPS у певному контексті індекс `pStateIdx` зменшується, і при досягненні нуля відбувається інверсія символу `valMPS = 1 - valMPS`.
   - Якщо в результаті звуження `m_range` стає меншим за 256 (`0x100`), активується цикл ренормалізації: `m_range` та `m_low` подвоюються бітовим зсувом вліво, а найстарші біти `m_low` виводяться у вихідний потік байтів.

## Обробка переносу бітів (Carry Bit Propagation)

При додаванні значення `rMPS` до регістра `m_low` може виникнути арифметичний перенос у старші біти. Оскільки вихідний бітстрім виводиться побайтово, кодер повинен обробляти ситуацію, коли значення переносу впливає на вже згенеровані, але ще не виведені біти.

Для цього використовується лічильник підвішених бітів `m_bitsOutstanding`:
- Якщо новий біт дорівнює 0, усі попередні підвішені біти виводяться як 1.
- Якщо новий біт дорівнює 1, виводиться 1, а усі підвішені біти виводяться як 0.
- Якщо `m_low` перебуває у невизначеній зоні переносу (`256 <= m_low < 512`), вивід затримується, а лічильник `m_bitsOutstanding` збільшується на 1.

Це гарантує точність формування двійкового потоку байтів без ризику втрати біта переносу.

## Ініціалізація контекстних таблиць на початку зрізу (Slice Initialization)

На початку кожного Slice заголовка NAL кодер ініціалізує 460 контекстних моделей залежно від параметра квантування зрізу `SliceQPy` та стандартизованих коефіцієнтів `m` і `n`:

```
preCtxState = clip3(1, 126, ((m * SliceQPy) >> 4) + n)
if (preCtxState <= 62) {
    valMPS = 0;
    pStateIdx = 62 - preCtxState;
} else {
    valMPS = 1;
    pStateIdx = preCtxState - 63;
}
```

Цей крок адаптує початкові ймовірності моделі під обраний ступінь стиснення кадру, завдяки чому арифметичний кодер починає стиснення з оптимізованими станами без тривалого розгону.

## Особливості апаратної реалізації CABAC у кремнії

На відміну від програмного коду, де інструкції виконуються послідовно у циклі `while`, апаратний IP-ядро кодека змушене виконувати ренормалізацію за один такт системної частоти. Для цього у кремнії застосовуються спеціальні логічні блоки:

- **Визначник першої одиниці (Leading Zero Count — LZC):** обчислює кількість бітових зсувів за один такт без використання циклів.
- **Спекулятивні регістри маскування:** апаратна логіка обчислює значення `range` та `low` одночасно для обох гілок (як якщо б прийшов бін 0 і як якщо б прийшов бін 1), після чого мультіплексор вибирає правильну гілку на основі реального значення біна.

Це дозволяє апаратним прискорювачам CABAC досягати швидкості кодування понад 300 мільйонів бінів на секунду у сучасних системах на кристалі (SoC).

## Реалізація конвеєра кодування CABAC

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// Спрощені таблиці переходу станів CABAC H.264 (64 стани)
static const uint8_t rangeTabLPS[64][4] = {
    { 128, 176, 208, 240 }, { 128, 167, 197, 227 }, { 128, 158, 187, 216 }, { 123, 150, 178, 205 },
    { 116, 142, 169, 195 }, { 111, 135, 160, 185 }, { 105, 128, 152, 175 }, { 100, 122, 144, 166 },
    {  95, 116, 137, 158 }, {  90, 110, 130, 150 }, {  85, 104, 123, 142 }, {  81,  99, 117, 135 }
    // Повна таблиця H.264 містить 64 рядки
};

static const uint8_t transIdxMPS[64] = {
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
    17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
    33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
    49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 62, 63
};

static const uint8_t transIdxLPS[64] = {
    0, 0, 1, 2, 2, 4, 4, 5, 6, 7, 8, 9, 9, 11, 11, 12,
    13, 13, 15, 15, 16, 16, 18, 18, 19, 19, 21, 21, 22, 22, 24, 24,
    25, 25, 27, 27, 28, 28, 30, 30, 31, 31, 33, 33, 34, 34, 36, 36,
    37, 37, 39, 39, 40, 40, 42, 42, 43, 43, 45, 45, 46, 46, 48, 48
};

// Контекстне середовище кодера
typedef struct {
    uint8_t pStateIdx; // Індекс стану ймовірності (0..63)
    uint8_t valMPS;    // Найімовірніший символ (0 або 1)
} CabacContext;

typedef struct {
    uint32_t low;       // Регістр нижньої межі (10+ бітів)
    uint32_t range;     // Регістр діапазону (9 бітів, 256..510)
    uint32_t bitsOutstanding; // Кількість підвішених бітів переносу
    uint8_t* buffer;    // Вихідний буфер бітстріму
    size_t   bytePos;   // Поточна позиція в байтовому буфері
    uint8_t  bitBuf;    // Поточний накопичувач бітів (8 біт)
    int      bitLeft;   // Кількість вільних біт у накопичувачі
} CabacEncoder;

void cabac_init(CabacEncoder* enc, uint8_t* out_buf) {
    enc->low = 0;
    enc->range = 510; // Початковий діапазон H.264
    enc->bitsOutstanding = 0;
    enc->buffer = out_buf;
    enc->bytePos = 0;
    enc->bitBuf = 0;
    enc->bitLeft = 8;
}

// Запис одного біта у вихідний байтовий потік
static void put_bit(CabacEncoder* enc, int bit) {
    enc->bitBuf = (enc->bitBuf << 1) | (bit & 1);
    enc->bitLeft--;
    if (enc->bitLeft == 0) {
        enc->buffer[enc->bytePos++] = enc->bitBuf;
        enc->bitBuf = 0;
        enc->bitLeft = 8;
    }
}

// Вивід біта з урахуванням переносу (Carry bit propagation)
static void put_bit_with_outstanding(CabacEncoder* enc, int bit) {
    put_bit(enc, bit);
    while (enc->bitsOutstanding > 0) {
        put_bit(enc, !bit);
        enc->bitsOutstanding--;
    }
}

// Кодування одного двійкового символу (binVal) з оновленням контексту
void cabac_encode_bin(CabacEncoder* enc, CabacContext* ctx, int binVal) {
    // 1. Обчислення діапазону для LPS
    uint32_t rLPS = rangeTabLPS[ctx->pStateIdx][(enc->range >> 6) & 3];
    enc->range -= rLPS;

    if (binVal == ctx->valMPS) {
        // Кодування MPS (найімовірніший символ)
        ctx->pStateIdx = transIdxMPS[ctx->pStateIdx];
    } else {
        // Кодування LPS (малоймовірний символ)
        enc->low += enc->range;
        enc->range = rLPS;
        if (ctx->pStateIdx == 0) {
            ctx->valMPS = 1 - ctx->valMPS; // Інверсія MPS
        }
        ctx->pStateIdx = transIdxLPS[ctx->pStateIdx];
    }

    // 2. Ренормалізація та вивід бітів
    while (enc->range < 256) {
        if (enc->low < 256) {
            put_bit_with_outstanding(enc, 0);
        } else if (enc->low >= 512) {
            put_bit_with_outstanding(enc, 1);
            enc->low -= 512;
        } else {
            enc->bitsOutstanding++;
            enc->low -= 256;
        }
        enc->range <<= 1;
        enc->low <<= 1;
    }
}

int main(void) {
    uint8_t stream[64] = {0};
    CabacEncoder enc;
    CabacContext ctx = { .pStateIdx = 10, .valMPS = 0 }; // Початковий контекст

    cabac_init(&enc, stream);

    // Кодуємо тестову послідовність бінів: 0, 0, 1, 0, 1
    int test_bins[5] = {0, 0, 1, 0, 1};
    for (int i = 0; i < 5; i++) {
        cabac_encode_bin(&enc, &ctx, test_bins[i]);
    }

    printf("Сформовано байтів CABAC: %zu\n", enc.bytePos);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <cstdint>
#include <span>

class CabacEncoder {
public:
    struct Context {
        std::uint8_t pStateIdx{0}; // Стан ймовірності (0..63)
        std::uint8_t valMPS{0};    // Найімовірніший символ
    };

    explicit CabacEncoder(std::vector<std::uint8_t>& outputBuffer)
        : m_buffer(outputBuffer) {}

    void encodeBin(Context& ctx, bool binVal) {
        // 1. Пошук розщеплення діапазону за таблицею LPS
        std::uint32_t rLPS = s_rangeTabLPS[ctx.pStateIdx][(m_range >> 6) & 3];
        m_range -= rLPS;

        if (binVal == static_cast<bool>(ctx.valMPS)) {
            ctx.pStateIdx = s_transIdxMPS[ctx.pStateIdx];
        } else {
            m_low += m_range;
            m_range = rLPS;
            if (ctx.pStateIdx == 0) {
                ctx.valMPS = 1 - ctx.valMPS;
            }
            ctx.pStateIdx = s_transIdxLPS[ctx.pStateIdx];
        }

        // 2. Ренормалізація та вибірка старших бітів
        while (m_range < 256) {
            if (m_low < 256) {
                putBitWithOutstanding(0);
            } else if (m_low >= 512) {
                putBitWithOutstanding(1);
                m_low -= 512;
            } else {
                ++m_bitsOutstanding;
                m_low -= 256;
            }
            m_range <<= 1;
            m_low <<= 1;
        }
    }

    void flush() {
        // Завершення кодування та очищення залишків бітів
        putBitWithOutstanding((m_low >> 9) & 1);
        m_low <<= 1;
        putBitWithOutstanding((m_low >> 9) & 1);
        if (m_bitLeft < 8) {
            m_buffer.push_back(m_bitBuf << m_bitLeft);
        }
    }

private:
    void putBit(int bit) {
        m_bitBuf = static_cast<std::uint8_t>((m_bitBuf << 1) | (bit & 1));
        --m_bitLeft;
        if (m_bitLeft == 0) {
            m_buffer.push_back(m_bitBuf);
            m_bitBuf = 0;
            m_bitLeft = 8;
        }
    }

    void putBitWithOutstanding(int bit) {
        putBit(bit);
        while (m_bitsOutstanding > 0) {
            putBit(!bit);
            --m_bitsOutstanding;
        }
    }

    std::uint32_t m_low{0};
    std::uint32_t m_range{510};
    std::uint32_t m_bitsOutstanding{0};
    std::vector<std::uint8_t>& m_buffer;
    std::uint8_t m_bitBuf{0};
    int m_bitLeft{8};

    static constexpr std::array<std::array<std::uint8_t, 4>, 12> s_rangeTabLPS = {{
        { 128, 176, 208, 240 }, { 128, 167, 197, 227 }, { 128, 158, 187, 216 }, { 123, 150, 178, 205 },
        { 116, 142, 169, 195 }, { 111, 135, 160, 185 }, { 105, 128, 152, 175 }, { 100, 122, 144, 166 },
        {  95, 116, 137, 158 }, {  90, 110, 130, 150 }, {  85, 104, 123, 142 }, {  81,  99, 117, 135 }
    }};

    static constexpr std::array<std::uint8_t, 64> s_transIdxMPS = {
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
        17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
        33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
        49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 62, 63
    };

    static constexpr std::array<std::uint8_t, 64> s_transIdxLPS = {
        0, 0, 1, 2, 2, 4, 4, 5, 6, 7, 8, 9, 9, 11, 11, 12,
        13, 13, 15, 15, 16, 16, 18, 18, 19, 19, 21, 21, 22, 22, 24, 24,
        25, 25, 27, 27, 28, 28, 30, 30, 31, 31, 33, 33, 34, 34, 36, 36,
        37, 37, 39, 39, 40, 40, 42, 42, 43, 43, 45, 45, 46, 46, 48, 48
    };
};

int main() {
    std::vector<std::uint8_t> outputStream;
    CabacEncoder encoder(outputStream);

    CabacEncoder::Context syntaxContext{.pStateIdx = 10, .valMPS = 0};

    // Вхідна послідовність бінів
    const std::array<bool, 5> testSequence = {false, false, true, false, true};
    for (bool bin : testSequence) {
        encoder.encodeBin(syntaxContext, bin);
    }
    encoder.flush();

    std::cout << "Сформовано байтів CABAC (C++): " << outputStream.size() << '\n';
    return 0;
}
```
:::
