#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define DIGIMATIC_RING_CAPACITY  32  // Обов'язково ступінь двійки
#define DIGIMATIC_RING_MASK      (DIGIMATIC_RING_CAPACITY - 1)

// Результат вимірювання у форматі фіксованої крапки (мкм)
typedef struct {
    int32_t value_um;       // Значення в мікрометрах (1 мкм = 0.001 мм)
    bool is_inch;           // Прапорець одиниці: true = дюйми, false = міліметри
    bool is_negative;       // Прапорець від'ємного значення
    bool valid;             // Ознака достовірності пакета
} digimatic_measurement_t;

// Потокобезпечний кільцевий буфер сирих 52-бітних кадрів
typedef struct {
    uint64_t frames[DIGIMATIC_RING_CAPACITY];
    volatile uint16_t head;
    volatile uint16_t tail;
} digimatic_ring_t;

static digimatic_ring_t s_rx_ring = { .head = 0, .tail = 0 };
static volatile uint64_t s_shift_accumulator = 0;
static volatile uint8_t s_bit_counter = 0;

// Апаратний обробник переривання по спаду тактової лінії CLK
void digimatic_clk_input_isr(bool data_pin_state) {
    if (s_bit_counter < 52) {
        if (data_pin_state) {
            s_shift_accumulator |= ((uint64_t)1 << s_bit_counter);
        }
        s_bit_counter++;

        // Завершення прийому 52-бітного кадру
        if (s_bit_counter == 52) {
            uint16_t next_head = (s_rx_ring.head + 1) & DIGIMATIC_RING_MASK;
            if (next_head != s_rx_ring.tail) {
                s_rx_ring.frames[s_rx_ring.head] = s_shift_accumulator;
                s_rx_ring.head = next_head;
            }
            s_bit_counter = 0;
            s_shift_accumulator = 0;
        }
    }
}

// Вилучення сирого кадру з кільцевого буфера
bool digimatic_ring_pop(uint64_t *out_frame) {
    if (s_rx_ring.head == s_rx_ring.tail) {
        return false; // Буфер порожній
    }
    *out_frame = s_rx_ring.frames[s_rx_ring.tail];
    s_rx_ring.tail = (s_rx_ring.tail + 1) & DIGIMATIC_RING_MASK;
    return true;
}

// Декодування сирого кадру в цілочисельні мікрометри (fixed-point)
bool digimatic_decode_frame(uint64_t raw_frame, digimatic_measurement_t *out_result) {
    static const int32_t s_powers_of_ten[6] = { 1, 10, 100, 1000, 10000, 100000 };
    uint8_t d[13];

    for (int i = 0; i < 13; i++) {
        d[i] = (uint8_t)((raw_frame >> (i * 4)) & 0x0F);
    }

    // Перевірка синхронізуючого заголовка 0xF 0xF 0xF 0xF
    if (d[0] != 0x0F || d[1] != 0x0F || d[2] != 0x0F || d[3] != 0x0F) {
        out_result->valid = false;
        return false;
    }

    // Перевірка діапазону BCD для розрядів d5..d10
    for (int i = 5; i <= 10; i++) {
        if (d[i] > 9) {
            out_result->valid = false;
            return false;
        }
    }

    int32_t raw_mantissa = d[5] + d[6]*10 + d[7]*100 + d[8]*1000 + d[9]*10000 + d[10]*100000;
    uint8_t exponent = d[11];
    if (exponent > 5) {
        exponent = 5;
    }

    // Масштабування до цілих мікрометрів (1 мкм = 0.001 мм)
    int32_t divisor = s_powers_of_ten[exponent];
    int32_t value_um = (raw_mantissa * 1000) / divisor;

    bool is_neg = (d[4] & 0x08) != 0;
    if (is_neg) {
        value_um = -value_um;
    }

    out_result->value_um = value_um;
    out_result->is_negative = is_neg;
    out_result->is_inch = (d[12] & 0x01) != 0;
    out_result->valid = true;
    return true;
}
