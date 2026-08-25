# ⚙️ Реалізація потокового компресора Gorilla на C та C++

Стиснення неперервного потоку вимірів телеметрії вимагає алгоритмів із мінімальними накладними витратами процесорного часу та можливістю миттєвої потокової обробки кожного вхідного кортежу `(timestamp, value)` без очікування накопичення великих пакетів даних. Алгоритм Gorilla об'єднує метод різниць другого порядку (Delta-of-Delta) для монотонно зростаючих часових міток із методом побітового виключного «АБО» (XOR) для 64-бітних дійсних чисел стандарту IEEE 754.

Головна складність практичної реалізації полягає в тому, що розмір кожного закодованого елемента варіюється від одного біта до кількох десятків бітів і не вирівнюється на межі байтів. Це вимагає створення високоефективного низькорівневого механізму побітового запису та зчитування, який мінімізує кількість звернень до оперативної пам'яті та максимально ефективно використовує регістри загального призначення сучасних процесорів.

## Архітектура компресора та робота з бітовим потоком

Компресор формує неперервний бітовий потік (англ. *bitstream*). Допоміжний клас `BitWriter` акумулює біти в буфері пам'яті. Коли в поточному байті заповнюються всі 8 бітів, вказівник переходить до наступного байта, а невикористані біти залишаються доступними для наступних записів.

Послідовність роботи компресора над серією точок часового ряду:
1. **Перша точка ряду:**
   - Часова мітка `t₀` записується повністю у вигляді 64-бітного цілого числа (8 байтів).
   - Дійсне число `v₀` записується повністю у вигляді 64-бітного двійкового представлення IEEE 754 (8 байтів).
   - Змінні стану компресора ініціалізуються цими базовими значеннями.
2. **Друга точка ряду:**
   - Обчислюється перша дельта `Δ₀ = t₁ - t₀`. Вона записується у 14 бітах (достатньо для представлення інтервалів до 16383 секунд або мілісекунд залежно від одиниць виміру часу).
   - Обчислюється `XOR = v₁ ⊕ v₀`. Якщо результат дорівнює нулю, записується один біт `'0'`. Якщо ні — записується біт `'1'`, після чого зберігаються змінні мантиси та порядку.
3. **Усі наступні точки (`i ≥ 2`):**
   - Обчислюється дельта дельт: `DOD = (tᵢ - tᵢ₋₁) - (tᵢ₋₁ - tᵢ₋₂)`. Залежно від величини `DOD` обирається один із п'яти префіксних діапазонів змінної довжини (від 1 біта для `DOD = 0` до 36 бітів для екстремальних стрибків).
   - Обчислюється `XOR = vᵢ ⊕ vᵢ₋₁`. Застосовується дворівнева схема кодування з перевіркою збереження меж провідних і кінцевих нулів попереднього кроку.

Така структура дозволяє уникнути виділення динамічної пам'яті на кожну окрему точку: компресор підтримує компактний фіксований стан у реєстрах процесора і дописує біти в попередньо виділений безперервний буфер пам'яті.

Нижче наведено повну реалізацію бітового компресора на мовах C та C++:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* Допоміжні бітові операції для підрахунку провідних і кінцевих нулів */
#if defined(__GNUC__) || defined(__clang__)
static inline int count_leading_zeros64(uint64_t x) {
    return x == 0 ? 64 : __builtin_clzll(x);
}
static inline int count_trailing_zeros64(uint64_t x) {
    return x == 0 ? 64 : __builtin_ctzll(x);
}
#else
static inline int count_leading_zeros64(uint64_t x) {
    if (x == 0) return 64;
    int n = 0;
    if ((x & 0xFFFFFFFF00000000ULL) == 0) { n += 32; x <<= 32; }
    if ((x & 0xFFFF000000000000ULL) == 0) { n += 16; x <<= 16; }
    if ((x & 0xFF00000000000000ULL) == 0) { n += 8;  x <<= 8;  }
    if ((x & 0xF000000000000000ULL) == 0) { n += 4;  x <<= 4;  }
    if ((x & 0xC000000000000000ULL) == 0) { n += 2;  x <<= 2;  }
    if ((x & 0x8000000000000000ULL) == 0) { n += 1; }
    return n;
}
static inline int count_trailing_zeros64(uint64_t x) {
    if (x == 0) return 64;
    int n = 0;
    if ((x & 0x00000000FFFFFFFFULL) == 0) { n += 32; x >>= 32; }
    if ((x & 0x000000000000FFFFULL) == 0) { n += 16; x >>= 16; }
    if ((x & 0x00000000000000FFULL) == 0) { n += 8;  x >>= 8;  }
    if ((x & 0x000000000000000FULL) == 0) { n += 4;  x >>= 4;  }
    if ((x & 0x0000000000000003ULL) == 0) { n += 2;  x >>= 2;  }
    if ((x & 0x0000000000000001ULL) == 0) { n += 1; }
    return n;
}
#endif

typedef struct {
    uint8_t *buffer;
    size_t capacity;
    size_t byte_pos;
    uint8_t bit_pos; /* 0..7: кількість вільних бітів у поточному байті */
} BitWriter;

static void bit_writer_init(BitWriter *bw, uint8_t *buf, size_t cap) {
    bw->buffer = buf;
    bw->capacity = cap;
    bw->byte_pos = 0;
    bw->bit_pos = 8;
    if (cap > 0) bw->buffer[0] = 0;
}

static void bit_writer_write_bits(BitWriter *bw, uint64_t value, int num_bits) {
    for (int i = num_bits - 1; i >= 0; --i) {
        if (bw->byte_pos >= bw->capacity) return;
        uint8_t bit = (uint8_t)((value >> i) & 1ULL);
        bw->bit_pos--;
        bw->buffer[bw->byte_pos] |= (uint8_t)(bit << bw->bit_pos);
        if (bw->bit_pos == 0) {
            bw->bit_pos = 8;
            bw->byte_pos++;
            if (bw->byte_pos < bw->capacity) {
                bw->buffer[bw->byte_pos] = 0;
            }
        }
    }
}

static size_t bit_writer_flush(BitWriter *bw) {
    if (bw->bit_pos < 8) {
        return bw->byte_pos + 1;
    }
    return bw->byte_pos;
}

typedef struct {
    BitWriter bw;
    uint64_t prev_time;
    uint64_t prev_delta;
    uint64_t prev_val_bits;
    int prev_leading;
    int prev_trailing;
    size_t count;
} GorillaEncoder;

void gorilla_encoder_init(GorillaEncoder *enc, uint8_t *buf, size_t cap) {
    bit_writer_init(&enc->bw, buf, cap);
    enc->prev_time = 0;
    enc->prev_delta = 0;
    enc->prev_val_bits = 0;
    enc->prev_leading = 64;
    enc->prev_trailing = 64;
    enc->count = 0;
}

static void encode_timestamp(GorillaEncoder *enc, uint64_t t) {
    if (enc->count == 0) {
        bit_writer_write_bits(&enc->bw, t, 64);
        enc->prev_time = t;
        return;
    }
    if (enc->count == 1) {
        uint64_t delta = t - enc->prev_time;
        bit_writer_write_bits(&enc->bw, delta, 14);
        enc->prev_delta = delta;
        enc->prev_time = t;
        return;
    }

    uint64_t delta = t - enc->prev_time;
    int64_t dod = (int64_t)delta - (int64_t)enc->prev_delta;

    if (dod == 0) {
        bit_writer_write_bits(&enc->bw, 0, 1);
    } else if (dod >= -63 && dod <= 64) {
        bit_writer_write_bits(&enc->bw, 2, 2); /* Префікс '10' */
        bit_writer_write_bits(&enc->bw, (uint64_t)(dod & 0x7F), 7);
    } else if (dod >= -255 && dod <= 256) {
        bit_writer_write_bits(&enc->bw, 6, 3); /* Префікс '110' */
        bit_writer_write_bits(&enc->bw, (uint64_t)(dod & 0x1FF), 9);
    } else if (dod >= -2047 && dod <= 2048) {
        bit_writer_write_bits(&enc->bw, 14, 4); /* Префікс '1110' */
        bit_writer_write_bits(&enc->bw, (uint64_t)(dod & 0xFFF), 12);
    } else {
        bit_writer_write_bits(&enc->bw, 15, 4); /* Префікс '1111' */
        bit_writer_write_bits(&enc->bw, (uint32_t)dod, 32);
    }

    enc->prev_delta = delta;
    enc->prev_time = t;
}

static void encode_value(GorillaEncoder *enc, double val) {
    uint64_t val_bits;
    memcpy(&val_bits, &val, sizeof(double));

    if (enc->count == 0) {
        bit_writer_write_bits(&enc->bw, val_bits, 64);
        enc->prev_val_bits = val_bits;
        return;
    }

    uint64_t xor_val = val_bits ^ enc->prev_val_bits;
    if (xor_val == 0) {
        bit_writer_write_bits(&enc->bw, 0, 1);
    } else {
        bit_writer_write_bits(&enc->bw, 1, 1);

        int leading = count_leading_zeros64(xor_val);
        int trailing = count_trailing_zeros64(xor_val);
        if (leading >= 32) leading = 31;

        if (enc->prev_leading != 64 &&
            leading >= enc->prev_leading &&
            trailing >= enc->prev_trailing) {
            bit_writer_write_bits(&enc->bw, 0, 1);
            int meaningful_len = 64 - enc->prev_leading - enc->prev_trailing;
            uint64_t meaningful_bits = (xor_val >> enc->prev_trailing);
            bit_writer_write_bits(&enc->bw, meaningful_bits, meaningful_len);
        } else {
            bit_writer_write_bits(&enc->bw, 1, 1);
            bit_writer_write_bits(&enc->bw, (uint64_t)leading, 5);
            int meaningful_len = 64 - leading - trailing;
            bit_writer_write_bits(&enc->bw, (uint64_t)meaningful_len, 6);
            uint64_t meaningful_bits = (xor_val >> trailing);
            bit_writer_write_bits(&enc->bw, meaningful_bits, meaningful_len);

            enc->prev_leading = leading;
            enc->prev_trailing = trailing;
        }
    }

    enc->prev_val_bits = val_bits;
}

void gorilla_encoder_add(GorillaEncoder *enc, uint64_t timestamp, double value) {
    encode_timestamp(enc, timestamp);
    encode_value(enc, value);
    enc->count++;
}

size_t gorilla_encoder_finish(GorillaEncoder *enc) {
    return bit_writer_flush(&enc->bw);
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <bit>
#include <bitset>
#include <cstring>
#include <optional>
#include <stdexcept>

class BitWriter {
public:
    explicit BitWriter(std::vector<uint8_t>& target)
        : out_buffer_(target), byte_pos_(0), bit_pos_(8) {
        if (out_buffer_.empty()) {
            out_buffer_.push_back(0);
        }
    }

    void write_bits(uint64_t value, int num_bits) {
        for (int i = num_bits - 1; i >= 0; --i) {
            uint8_t bit = static_cast<uint8_t>((value >> i) & 1ULL);
            bit_pos_--;
            out_buffer_[byte_pos_] |= static_cast<uint8_t>(bit << bit_pos_);
            if (bit_pos_ == 0) {
                bit_pos_ = 8;
                byte_pos_++;
                out_buffer_.push_back(0);
            }
        }
    }

    [[nodiscard]] size_t finalize() {
        if (bit_pos_ == 8 && !out_buffer_.empty() && byte_pos_ < out_buffer_.size()) {
            out_buffer_.pop_back(); // Прибираємо невикористаний нульовий байт
        }
        return out_buffer_.size();
    }

private:
    std::vector<uint8_t>& out_buffer_;
    size_t byte_pos_;
    uint8_t bit_pos_;
};

struct DataPoint {
    uint64_t timestamp;
    double value;
};

class GorillaCompressor {
public:
    explicit GorillaCompressor(std::vector<uint8_t>& output_sink)
        : writer_(output_sink) {}

    void append(const DataPoint& point) {
        encode_timestamp(point.timestamp);
        encode_value(point.value);
        count_++;
    }

    size_t close() {
        return writer_.finalize();
    }

    [[nodiscard]] size_t sample_count() const noexcept { return count_; }

private:
    BitWriter writer_;
    uint64_t prev_time_{0};
    uint64_t prev_delta_{0};
    uint64_t prev_val_bits_{0};
    int prev_leading_{64};
    int prev_trailing_{64};
    size_t count_{0};

    void encode_timestamp(uint64_t t) {
        if (count_ == 0) {
            writer_.write_bits(t, 64);
            prev_time_ = t;
            return;
        }
        if (count_ == 1) {
            uint64_t delta = t - prev_time_;
            writer_.write_bits(delta, 14);
            prev_delta_ = delta;
            prev_time_ = t;
            return;
        }

        uint64_t delta = t - prev_time_;
        int64_t dod = static_cast<int64_t>(delta) - static_cast<int64_t>(prev_delta_);

        if (dod == 0) {
            writer_.write_bits(0, 1);
        } else if (dod >= -63 && dod <= 64) {
            writer_.write_bits(2, 2); // Префікс '10'
            writer_.write_bits(static_cast<uint64_t>(dod & 0x7F), 7);
        } else if (dod >= -255 && dod <= 256) {
            writer_.write_bits(6, 3); // Префікс '110'
            writer_.write_bits(static_cast<uint64_t>(dod & 0x1FF), 9);
        } else if (dod >= -2047 && dod <= 2048) {
            writer_.write_bits(14, 4); // Префікс '1110'
            writer_.write_bits(static_cast<uint64_t>(dod & 0xFFF), 12);
        } else {
            writer_.write_bits(15, 4); // Префікс '1111'
            writer_.write_bits(static_cast<uint32_t>(dod), 32);
        }

        prev_delta_ = delta;
        prev_time_ = t;
    }

    void encode_value(double val) {
        uint64_t val_bits = std::bit_cast<uint64_t>(val);

        if (count_ == 0) {
            writer_.write_bits(val_bits, 64);
            prev_val_bits_ = val_bits;
            return;
        }

        uint64_t xor_val = val_bits ^ prev_val_bits_;
        if (xor_val == 0) {
            writer_.write_bits(0, 1);
        } else {
            writer_.write_bits(1, 1);

            int leading = std::countl_zero(xor_val);
            int trailing = std::countr_zero(xor_val);
            if (leading >= 32) leading = 31;

            if (prev_leading_ != 64 &&
                leading >= prev_leading_ &&
                trailing >= prev_trailing_) {
                writer_.write_bits(0, 1);
                int meaningful_len = 64 - prev_leading_ - prev_trailing_;
                uint64_t meaningful_bits = (xor_val >> prev_trailing_);
                writer_.write_bits(meaningful_bits, meaningful_len);
            } else {
                writer_.write_bits(1, 1);
                writer_.write_bits(static_cast<uint64_t>(leading), 5);
                int meaningful_len = 64 - leading - trailing;
                writer_.write_bits(static_cast<uint64_t>(meaningful_len), 6);
                uint64_t meaningful_bits = (xor_val >> trailing);
                writer_.write_bits(meaningful_bits, meaningful_len);

                prev_leading_ = leading;
                prev_trailing_ = trailing;
            }
        }

        prev_val_bits_ = val_bits;
    }
};
```
:::

## Аналіз продуктивності та обробка виняткових станів

Під час експлуатації потокового компресора в умовах високого навантаження слід звернути особливу увагу на оптимізацію роботи з процесорним кешем, мінімізацію промахів передбачення переходів (branch mispredictions) і коректну обробку граничних станів обчислень:

### 1. Апаратні інструкції для роботи з бітами
Для підрахунку кількості провідних і кінцевих нулів у 64-бітних регістрах сучасні процесори архітектур x86-64 та ARM64 мають спеціалізовані апаратні інструкції: `LZCNT` / `CLZ` (Count Leading Zeros) та `TZCNT` / `CTZ` (Count Trailing Zeros). Використання компіляторних вбудованих функцій `__builtin_clzll` (або `std::countl_zero` та `std::countr_zero` у стандарті C++20) транслюється в одну машинну інструкцію процесора із затримкою виконання в один такт. Це повністю усуває необхідність повільних ітеративних циклів зі зсувами бітів та перевірками умов.

### 2. Обробка спеціальних значень IEEE 754
Стандарт чисел із рухомою комою визначає спеціальні нечислові значення: нескінченність (`+Inf`, `-Inf`), невизначеність (`NaN`) та денормалізовані числа. Завдяки тому, що алгоритм Gorilla оперує безпосередньо над сирими двійковими образами (`uint64_t`), а не над значеннями через арифметичні оператори з плаваючою комою, поява `NaN` або `Inf` не викликає виняткових ситуацій FPU (Floating-Point Unit). Значення `+0.0` і `-0.0` кодуються коректно: їхній `XOR` відрізняється лише старшим знаковим бітом (`0x8000000000000000`), що викликає створення нового вікна без помилок чи викривлення даних.

### 3. Фіналізація та вирівнювання чанка
Оскільки точки записуються зі змінною бітовою довжиною, в кінці запису останній байт може містити менше 8 значущих бітів. Метод `finalize()` / `bit_writer_flush()` доповнює незавершений байт нульовими бітами і повертає точну кількість використаних байтів пам'яті. Це гарантує коректне обчислення контрольної суми CRC32-Castagnoli для всього сформованого сегмента чанка перед збереженням на дисковий накопичувач.

### 4. Робота зі зворотною сумісністю та декодуванням
Для відновлення даних декодер повинен виконувати зворотні операції в строго тій самій послідовності. При зчитуванні бітового потоку декодер спочатку зчитує 64 біти початкового часу та 64 біти першого значення. Для кожного наступного кроку декодер читає префіксні біти для визначення діапазону `DOD`, додає обчислену дельту до накопиченого часу, після чого перевіряє перший біт значення float. Якщо біт дорівнює `'0'`, попереднє значення дублюється; якщо біт дорівнює `'1'`, декодер читає прапорець вікна, видобуває значущі біти, зсуває їх на позицію `trailing` і застосовує операцію `XOR` до бітового образу попереднього значення.
