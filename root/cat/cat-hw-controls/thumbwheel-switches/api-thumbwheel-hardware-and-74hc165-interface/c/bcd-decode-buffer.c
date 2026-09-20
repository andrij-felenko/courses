#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t decade_count;
    bool is_valid;
    uint32_t value;
} bcd_result_t;

// Зчитування сирого масиву байтів із каскаду 74HC165
void shift165_read_bytes(uint8_t *buffer, size_t byte_count);

// Валідація та конвертація упакованого BCD в ціле число
bcd_result_t bcd_decode_buffer(const uint8_t *raw_bytes, size_t byte_count) {
    bcd_result_t res = { .decade_count = byte_count * 2, .is_valid = true, .value = 0 };
    uint32_t multiplier = 1;

    for (size_t i = 0; i < byte_count; i++) {
        // Інверсія для схеми з pull-up до VCC
        uint8_t data = ~raw_bytes[i];
        uint8_t nibbles[2] = { data & 0x0F, (data >> 4) & 0x0F };

        for (int n = 0; n < 2; n++) {
            if (nibbles[n] > 9) {
                res.is_valid = false;
                return res;
            }
            res.value += nibbles[n] * multiplier;
            multiplier *= 10;
        }
    }
    return res;
}
