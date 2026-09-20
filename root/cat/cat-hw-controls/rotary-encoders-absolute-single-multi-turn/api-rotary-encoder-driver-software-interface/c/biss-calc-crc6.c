#include <stdint.h>
#include <stdbool.h>

typedef enum {
    BISS_OK = 0,
    BISS_ERR_CRC = 1,
    BISS_ERR_WARN = 2,
    BISS_ERR_TIMEOUT = 3
} biss_status_t;

typedef struct {
    uint32_t singleturn_raw;
    uint32_t multiturn_raw;
    uint32_t position_binary;
    bool error_bit;
    bool warning_bit;
    uint8_t crc_received;
    uint8_t crc_calculated;
} biss_frame_t;

// Обчислення CRC-6 для кадру BiSS-C
uint8_t biss_calc_crc6(uint64_t data, size_t bit_len) {
    uint8_t crc = 0x00;
    for (int i = bit_len - 1; i >= 0; i--) {
        uint8_t bit = (data >> i) & 0x01;
        uint8_t crc_msb = (crc >> 5) & 0x01;
        crc <<= 1;
        if (bit ^ crc_msb) {
            crc ^= 0x03; // Поліном 0x43 (x6 + x + 1, без молодшого біта)
        }
    }
    return (crc ^ 0x3F) & 0x3F; // Інверсія результату
}

// Декодування сирого кадру
biss_status_t biss_parse_frame(uint64_t raw_bits, size_t pos_bits, biss_frame_t *frame) {
    frame->crc_received = raw_bits & 0x3F;
    uint64_t payload = raw_bits >> 6;
    
    frame->crc_calculated = biss_calc_crc6(payload, pos_bits + 2);
    if (frame->crc_received != frame->crc_calculated) {
        return BISS_ERR_CRC;
    }

    frame->warning_bit = (payload & 0x01) == 0;
    frame->error_bit = ((payload >> 1) & 0x01) == 0;
    
    uint32_t gray_pos = (payload >> 2) & ((1ULL << pos_bits) - 1);
    
    // Перетворення коду Грея у двійковий
    uint32_t bin = gray_pos;
    for (uint32_t mask = bin >> 1; mask > 0; mask >>= 1) {
        bin ^= mask;
    }
    frame->position_binary = bin;

    if (!frame->error_bit) return BISS_ERR_CRC; // Апаратна помилка енкодера
    return frame->warning_bit ? BISS_OK : BISS_ERR_WARN;
}
