#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define BUS_WIDTH_BITS 32
#define BYTE_WIDTH 8
#define NUM_LANES (BUS_WIDTH_BITS / BYTE_WIDTH)

typedef struct {
    uint8_t data[NUM_LANES];
    uint8_t inv_mask; // біти інверсії для кожного з 4 каналів
} EncodedBusWord;

typedef struct {
    uint8_t prev_bus[NUM_LANES];
    uint8_t prev_inv;
    uint64_t total_raw_transitions;
    uint64_t total_encoded_transitions;
} BusInvertState;

static inline uint32_t count_ones_8(uint8_t val) {
    return (uint32_t)__builtin_popcount((unsigned int)val);
}

void bus_invert_init(BusInvertState* state) {
    for (size_t i = 0; i < NUM_LANES; ++i) {
        state->prev_bus[i] = 0;
    }
    state->prev_inv = 0;
    state->total_raw_transitions = 0;
    state->total_encoded_transitions = 0;
}

EncodedBusWord bus_invert_encode_word(BusInvertState* state, uint32_t raw_data) {
    EncodedBusWord out;
    out.inv_mask = 0;

    for (size_t i = 0; i < NUM_LANES; ++i) {
        uint8_t current_byte = (uint8_t)((raw_data >> (i * 8)) & 0xFF);
        uint8_t prev_raw = state->prev_bus[i];
        if (state->prev_inv & (1 << i)) {
            prev_raw = ~prev_raw;
        }

        // Обчислюємо перемикання для сирого сигналу
        uint32_t raw_diff = count_ones_8(current_byte ^ prev_raw);
        state->total_raw_transitions += raw_diff;

        // Обчислюємо відстань Геммінга відносно фізичного стану шини
        uint32_t hamming = count_ones_8(current_byte ^ state->prev_bus[i]);

        if (hamming > (BYTE_WIDTH / 2)) {
            out.data[i] = ~current_byte;
            out.inv_mask |= (uint8_t)(1 << i);
        } else {
            out.data[i] = current_byte;
        }

        // Рахуємо реальні перемикання на закодованій шині
        uint32_t bus_diff = count_ones_8(out.data[i] ^ state->prev_bus[i]);
        state->total_encoded_transitions += bus_diff;
        state->prev_bus[i] = out.data[i];
    }

    // Додаємо перемикання ліній інверсії
    uint32_t inv_diff = count_ones_8(out.inv_mask ^ state->prev_inv);
    state->total_encoded_transitions += inv_diff;
    state->prev_inv = out.inv_mask;

    return out;
}

double bus_invert_get_savings_percent(const BusInvertState* state) {
    if (state->total_raw_transitions == 0) return 0.0;
    double raw = (double)state->total_raw_transitions;
    double enc = (double)state->total_encoded_transitions;
    return (1.0 - (enc / raw)) * 100.0;
}
