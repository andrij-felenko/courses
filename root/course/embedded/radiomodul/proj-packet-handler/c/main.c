#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define PREAMBLE_BYTE     0xAA
#define PREAMBLE_LEN      4
#define SYNC_WORD         0xD391
#define CRC16_POLY        0x1021
#define CRC16_INIT        0xFFFF
#define LFSR_SEED         0x7F
#define MAX_PAYLOAD_LEN   64
#define MAX_FRAME_LEN     (PREAMBLE_LEN + 2 + 1 + MAX_PAYLOAD_LEN + 2)

typedef struct {
    uint8_t payload[MAX_PAYLOAD_LEN];
    uint8_t length;
    bool    crc_ok;
} RxPacketResult;

// Ініціалізація та обчислення CRC-16 CCITT
uint16_t crc16_update(uint16_t crc, uint8_t data) {
    crc ^= ((uint16_t)data << 8);
    for (uint8_t i = 0; i < 8; i++) {
        if (crc & 0x8000) {
            crc = (crc << 1) ^ CRC16_POLY;
        } else {
            crc = (crc << 1);
        }
    }
    return crc;
}

// 7-бітний LFSR скремблер (x^7 + x^4 + 1)
void lfsr_whiten(uint8_t *data, size_t len) {
    uint8_t lfsr = LFSR_SEED;
    for (size_t i = 0; i < len; i++) {
        uint8_t out_byte = 0;
        for (int bit = 7; bit >= 0; bit--) {
            uint8_t lfsr_out = (lfsr >> 6) & 0x01;
            uint8_t feedback = ((lfsr >> 6) ^ (lfsr >> 3)) & 0x01;
            lfsr = ((lfsr << 1) | feedback) & 0x7F;

            uint8_t in_bit = (data[i] >> bit) & 0x01;
            out_byte |= ((in_bit ^ lfsr_out) << bit);
        }
        data[i] = out_byte;
    }
}

// Формування кадру для відправки в ефір
size_t packet_encode(const uint8_t *payload, uint8_t payload_len, uint8_t *frame_out) {
    if (payload_len > MAX_PAYLOAD_LEN) return 0;

    size_t idx = 0;

    // 1. Преамбула (4 байти 0xAA)
    for (size_t i = 0; i < PREAMBLE_LEN; i++) {
        frame_out[idx++] = PREAMBLE_BYTE;
    }

    // 2. Синхрослово (0xD391, MSB first)
    frame_out[idx++] = (uint8_t)(SYNC_WORD >> 8);
    frame_out[idx++] = (uint8_t)(SYNC_WORD & 0xFF);

    // 3. Байт довжини корисного навантаження
    uint8_t len_byte = payload_len;
    frame_out[idx++] = len_byte;

    // 4. Тимчасовий буфер для скремблювання корисного навантаження
    uint8_t whitened_payload[MAX_PAYLOAD_LEN];
    memcpy(whitened_payload, payload, payload_len);
    lfsr_whiten(whitened_payload, payload_len);

    memcpy(&frame_out[idx], whitened_payload, payload_len);
    idx += payload_len;

    // 5. Розрахунок CRC-16 (по довжині та скрембльованому payload)
    uint16_t crc = CRC16_INIT;
    crc = crc16_update(crc, len_byte);
    for (size_t i = 0; i < payload_len; i++) {
        crc = crc16_update(crc, whitened_payload[i]);
    }

    frame_out[idx++] = (uint8_t)(crc >> 8);
    frame_out[idx++] = (uint8_t)(crc & 0xFF);

    return idx;
}

// Декодування та верифікація прийнятого кадру
bool packet_decode(const uint8_t *frame, size_t frame_len, RxPacketResult *result) {
    if (frame_len < (PREAMBLE_LEN + 2 + 1 + 2)) return false;

    // 1. Пошук синхрослова
    size_t sync_pos = 0;
    bool sync_found = false;
    for (size_t i = 0; i <= frame_len - 2; i++) {
        uint16_t sw = ((uint16_t)frame[i] << 8) | frame[i + 1];
        if (sw == SYNC_WORD) {
            sync_pos = i + 2;
            sync_found = true;
            break;
        }
    }
    if (!sync_found) return false;

    // 2. Читання довжини
    if (sync_pos >= frame_len) return false;
    uint8_t payload_len = frame[sync_pos++];
    if (payload_len > MAX_PAYLOAD_LEN) return false;
    if (sync_pos + payload_len + 2 > frame_len) return false;

    // 3. Перевірка CRC
    uint16_t calc_crc = CRC16_INIT;
    calc_crc = crc16_update(calc_crc, payload_len);
    for (size_t i = 0; i < payload_len; i++) {
        calc_crc = crc16_update(calc_crc, frame[sync_pos + i]);
    }

    uint16_t rx_crc = ((uint16_t)frame[sync_pos + payload_len] << 8) | 
                      frame[sync_pos + payload_len + 1];

    result->length = payload_len;
    result->crc_ok = (calc_crc == rx_crc);

    if (!result->crc_ok) {
        return false;
    }

    // 4. Дескремблювання даних
    memcpy(result->payload, &frame[sync_pos], payload_len);
    lfsr_whiten(result->payload, payload_len);

    return true;
}
