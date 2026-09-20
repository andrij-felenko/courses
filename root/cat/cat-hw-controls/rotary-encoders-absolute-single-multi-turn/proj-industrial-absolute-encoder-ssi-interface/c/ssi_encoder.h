#ifndef SSI_ENCODER_H
#define SSI_ENCODER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Прапори діагностики кадру SSI
#define SSI_FLAG_NONE          0x00
#define SSI_FLAG_ERROR_BIT     0x01
#define SSI_FLAG_WARN_BIT      0x02
#define SSI_FLAG_CRC_MISMATCH  0x04

// Конфігурація бітових полів енкодера
typedef struct {
    uint8_t singleturn_bits; // Кількість бітів кута (напр. 13)
    uint8_t multiturn_bits;  // Кількість бітів обертів (напр. 12)
    bool use_gray_code;      // true - код Грея, false - двійковий код
} ssi_config_t;

// Декодовані дані з кадру енкодера
typedef struct {
    uint32_t singleturn_raw;
    uint32_t multiturn_raw;
    float angle_degrees;
    int32_t turns_count;
    uint8_t status_flags;
    bool is_valid;
} ssi_decoded_data_t;

// Прототипи функцій
uint32_t gray_to_binary32(uint32_t gray);
uint8_t calculate_crc8(const uint8_t *data, size_t length);
bool ssi_decode_frame(const uint8_t *raw_bytes, size_t raw_len, const ssi_config_t *cfg, ssi_decoded_data_t *out_data);

#endif // SSI_ENCODER_H
