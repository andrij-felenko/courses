#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/**
 * @brief Швидке перетворення 32-бітного коду Грея у двійковий код.
 *        Використовує паралельне XOR-згортання за O(log2 N) тактів.
 */
static inline uint32_t gray_to_binary32(uint32_t gray) {
    gray ^= (gray >> 1);
    gray ^= (gray >> 2);
    gray ^= (gray >> 4);
    gray ^= (gray >> 8);
    gray ^= (gray >> 16);
    return gray;
}

/**
 * @brief Обчислення 6-бітної контрольної суми BiSS-C (CRC-6).
 *        Поліном: x^6 + x^1 + 1 (0x43), початкове значення 0x00, інвертований вихід.
 */
static uint8_t biss_crc6(uint64_t data, uint8_t bit_count) {
    uint8_t crc = 0x00;
    for (int8_t i = bit_count - 1; i >= 0; --i) {
        uint8_t bit = (uint8_t)((data >> i) & 1ULL);
        uint8_t do_invert = (uint8_t)(((crc >> 5) & 1U) ^ bit);
        crc <<= 1;
        if (do_invert) {
            crc ^= 0x03; // Поліном x^6 + x^1 + 1 (молодші біти без x^6: 0b000011 = 0x03)
        }
    }
    return (uint8_t)((~crc) & 0x3FU);
}

typedef struct {
    uint32_t single_turn_raw;
    uint32_t multi_turn_raw;
    double   angle_rad;
    double   angle_deg;
    int32_t  turns_count;
    bool     error_flag;
    bool     warning_flag;
    bool     crc_valid;
} absolute_position_t;

typedef struct {
    uint8_t  single_turn_bits;
    uint8_t  multi_turn_bits;
    bool     is_gray_coded;
} encoder_config_t;

/**
 * @brief Декодування сирого кадру абсолютного енкодера BiSS-C.
 * @param raw_frame Сире 64-бітне слово, зчитане з лінії зсуву.
 * @param config    Конфігурація розрядності енкодера.
 * @param result    Вихідна структура з розпарсеними величинами.
 * @return true, якщо кадр коректний (CRC валідний і прапорець помилки відсутній).
 */
bool encoder_decode_biss_frame(uint64_t raw_frame,
                               const encoder_config_t *config,
                               absolute_position_t *result) {
    if (!config || !result) return false;

    uint8_t total_pos_bits = config->multi_turn_bits + config->single_turn_bits;
    // Структура кадру BiSS-C: [MultiTurn][SingleTurn][Error(1b)][Warning(1b)][CRC(6b)]
    uint8_t total_payload_bits = total_pos_bits + 2; // Позиція + E + W

    uint8_t received_crc = (uint8_t)(raw_frame & 0x3FU);
    uint64_t payload = (raw_frame >> 6) & ((1ULL << total_payload_bits) - 1ULL);

    uint8_t calculated_crc = biss_crc6(payload, total_payload_bits);
    result->crc_valid = (received_crc == calculated_crc);

    result->warning_flag = ((payload >> 0) & 1ULL) == 0; // '0' означає активне попередження
    result->error_flag   = ((payload >> 1) & 1ULL) == 0; // '0' означає критичну помилку

    uint64_t raw_pos = payload >> 2;
    uint64_t st_mask = (1ULL << config->single_turn_bits) - 1ULL;
    uint64_t mt_mask = (1ULL << config->multi_turn_bits) - 1ULL;

    uint32_t raw_st = (uint32_t)(raw_pos & st_mask);
    uint32_t raw_mt = (uint32_t)((raw_pos >> config->single_turn_bits) & mt_mask);

    if (config->is_gray_coded) {
        result->single_turn_raw = gray_to_binary32(raw_st);
        result->multi_turn_raw  = gray_to_binary32(raw_mt);
    } else {
        result->single_turn_raw = raw_st;
        result->multi_turn_raw  = raw_mt;
    }

    double st_steps = (double)(1ULL << config->single_turn_bits);
    result->angle_deg = ((double)result->single_turn_raw / st_steps) * 360.0;
    result->angle_rad = ((double)result->single_turn_raw / st_steps) * (2.0 * M_PI);
    result->turns_count = (int32_t)result->multi_turn_raw;

    return result->crc_valid && !result->error_flag;
}
