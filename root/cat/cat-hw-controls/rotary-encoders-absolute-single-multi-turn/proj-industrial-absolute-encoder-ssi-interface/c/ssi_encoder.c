#include "ssi_encoder.h"

uint32_t gray_to_binary32(uint32_t gray) {
    uint32_t mask = gray >> 1;
    while (mask != 0) {
        gray ^= mask;
        mask >>= 1;
    }
    return gray;
}

uint8_t calculate_crc8(const uint8_t *data, size_t length) {
    uint8_t crc = 0xFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x07;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

bool ssi_decode_frame(const uint8_t *raw_bytes, size_t raw_len, const ssi_config_t *cfg, ssi_decoded_data_t *out_data) {
    if (!raw_bytes || !cfg || !out_data || raw_len < 4) {
        return false;
    }

    out_data->status_flags = SSI_FLAG_NONE;

    uint8_t computed_crc = calculate_crc8(raw_bytes, raw_len - 1);
    uint8_t received_crc = raw_bytes[raw_len - 1];

    if (computed_crc != received_crc) {
        out_data->status_flags |= SSI_FLAG_CRC_MISMATCH;
    }

    uint32_t frame_word = ((uint32_t)raw_bytes[0] << 24) |
                         ((uint32_t)raw_bytes[1] << 16) |
                         ((uint32_t)raw_bytes[2] << 8)  |
                         ((uint32_t)raw_bytes[3]);

    bool error_bit = (frame_word & 0x01) == 0;
    bool warn_bit  = (frame_word & 0x02) == 0;

    if (error_bit) out_data->status_flags |= SSI_FLAG_ERROR_BIT;
    if (warn_bit)  out_data->status_flags |= SSI_FLAG_WARN_BIT;

    uint32_t st_mask = (1U << cfg->singleturn_bits) - 1;
    uint32_t mt_mask = (1U << cfg->multiturn_bits) - 1;

    uint32_t raw_st = (frame_word >> 2) & st_mask;
    uint32_t raw_mt = (frame_word >> (2 + cfg->singleturn_bits)) & mt_mask;

    out_data->singleturn_raw = cfg->use_gray_code ? gray_to_binary32(raw_st) : raw_st;
    out_data->multiturn_raw  = cfg->use_gray_code ? gray_to_binary32(raw_mt) : raw_mt;

    float max_st_count = (float)(1U << cfg->singleturn_bits);
    out_data->angle_degrees = (out_data->singleturn_raw / max_st_count) * 360.0f;
    out_data->turns_count = (int32_t)out_data->multiturn_raw;

    out_data->is_valid = (out_data->status_flags == SSI_FLAG_NONE);
    return out_data->is_valid;
}
