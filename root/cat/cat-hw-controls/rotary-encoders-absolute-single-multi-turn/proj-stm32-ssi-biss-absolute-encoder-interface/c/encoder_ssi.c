#include "encoder_ssi.h"
#include "gray_code.h"
#include "biss_crc.h"
#include <stddef.h>

void encoder_ssi_init_config(encoder_config_t *config,
                             uint8_t st_bits,
                             uint8_t mt_bits,
                             bool is_gray,
                             bool has_crc) {
    if (config == NULL) return;

    config->single_turn_bits = st_bits;
    config->multi_turn_bits = mt_bits;
    config->is_gray_code = is_gray;
    config->has_biss_crc = has_crc;
    config->active_low_status = true; /* За стандартом BiSS-C/SSI nERROR та nWARN активні у 0 */
}

bool encoder_ssi_parse_frame(const encoder_config_t *config,
                             uint64_t raw_frame,
                             encoder_frame_t *out_frame) {
    if (config == NULL || out_frame == NULL) {
        return false;
    }

    out_frame->raw_frame = raw_frame;
    out_frame->crc_valid = true;
    out_frame->error_flag = false;
    out_frame->warning_flag = false;

    uint8_t st_bits = config->single_turn_bits;
    uint8_t mt_bits = config->multi_turn_bits;

    /*
     * Структура кадру BiSS-C / SSI (від старших бітів MSB до молодших LSB):
     * [MT_Bits (опція)] [ST_Bits] [nERROR (1 біт)] [nWARN (1 біт)] [CRC-6 (6 бітів)]
     */
    uint64_t current_frame = raw_frame;

    /* 1. Виділення та верифікація CRC, якщо вона присутня в кадрі */
    if (config->has_biss_crc) {
        out_frame->crc = (uint8_t)(current_frame & BISS_CRC6_MASK);
        current_frame >>= 6; /* Відсікаємо біти CRC */

        uint8_t payload_bits = mt_bits + st_bits + 2; /* Дані + nERROR + nWARN */
        uint64_t payload_data = current_frame & ((1ULL << payload_bits) - 1ULL);

        out_frame->crc_valid = biss_crc6_verify(payload_data, payload_bits, out_frame->crc);
    } else {
        out_frame->crc = 0;
    }

    /* 2. Виділення статусних бітів (nWARN та nERROR) */
    uint8_t raw_nwarn = (uint8_t)(current_frame & 0x01);
    current_frame >>= 1;

    uint8_t raw_nerror = (uint8_t)(current_frame & 0x01);
    current_frame >>= 1;

    if (config->active_low_status) {
        out_frame->error_flag = (raw_nerror == 0);
        out_frame->warning_flag = (raw_nwarn == 0);
    } else {
        out_frame->error_flag = (raw_nerror != 0);
        out_frame->warning_flag = (raw_nwarn != 0);
    }

    /* 3. Виділення однооборотної позиції (Single-Turn) */
    uint64_t st_raw = current_frame & ((1ULL << st_bits) - 1ULL);
    current_frame >>= st_bits;

    if (config->is_gray_code) {
        out_frame->single_turn_pos = gray_to_binary32((uint32_t)st_raw);
    } else {
        out_frame->single_turn_pos = (uint32_t)st_raw;
    }

    /* 4. Виділення багатооборотного лічильника (Multi-Turn) */
    if (mt_bits > 0) {
        uint64_t mt_raw = current_frame & ((1ULL << mt_bits) - 1ULL);
        if (config->is_gray_code) {
            out_frame->multi_turn_count = gray_to_binary32((uint32_t)mt_raw);
        } else {
            out_frame->multi_turn_count = (uint32_t)mt_raw;
        }
    } else {
        out_frame->multi_turn_count = 0;
    }

    /* Кадр вважається валідним, якщо CRC співпадає та відсутня апаратна помилка nERROR */
    return out_frame->crc_valid && (!out_frame->error_flag);
}

double encoder_frame_to_angle_degrees(const encoder_config_t *config,
                                      const encoder_frame_t *frame) {
    if (config == NULL || frame == NULL || config->single_turn_bits == 0) {
        return 0.0;
    }

    uint64_t max_counts = 1ULL << config->single_turn_bits;
    double fraction = (double)frame->single_turn_pos / (double)max_counts;
    return fraction * 360.0;
}
