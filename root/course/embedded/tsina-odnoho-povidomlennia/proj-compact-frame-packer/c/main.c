#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TELEM_FRAME_MAGIC   0x50
#define TELEM_FRAME_VERSION 0x01
#define TELEM_FRAME_SIZE    13

typedef struct {
    uint32_t timestamp;
    int16_t  temp_centi_deg;  /* Температура * 100 (напр. 2345 = 23.45 °C) */
    uint16_t batt_millivolts; /* Напруга в мВ (напр. 3612 = 3.612 В) */
    uint8_t  hum_half_pct;    /* Вологість * 2 (напр. 117 = 58.5 %) */
    uint8_t  flags;           /* 8 дискретних бітів стану */
} TelemetryData;

/* Обчислення CRC16-CCITT (поліном 0x1021, init 0xFFFF) без таблиці в RAM */
static uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

/* Серіалізація структури у фіксований буфер (Big-Endian) */
bool telemetry_pack(const TelemetryData *src, uint8_t *dst_buf, size_t buf_len) {
    if (!src || !dst_buf || buf_len < TELEM_FRAME_SIZE) {
        return false;
    }

    dst_buf[0] = (TELEM_FRAME_MAGIC & 0xF0) | (TELEM_FRAME_VERSION & 0x0F);

    /* Час uint32_t у Big-Endian через побайтовий зсув */
    dst_buf[1] = (uint8_t)((src->timestamp >> 24) & 0xFF);
    dst_buf[2] = (uint8_t)((src->timestamp >> 16) & 0xFF);
    dst_buf[3] = (uint8_t)((src->timestamp >> 8) & 0xFF);
    dst_buf[4] = (uint8_t)(src->timestamp & 0xFF);

    /* Температура int16_t у Big-Endian */
    uint16_t raw_temp = (uint16_t)src->temp_centi_deg;
    dst_buf[5] = (uint8_t)((raw_temp >> 8) & 0xFF);
    dst_buf[6] = (uint8_t)(raw_temp & 0xFF);

    /* Напруга uint16_t у Big-Endian */
    dst_buf[7] = (uint8_t)((src->batt_millivolts >> 8) & 0xFF);
    dst_buf[8] = (uint8_t)(src->batt_millivolts & 0xFF);

    /* Вологість та бітові прапорці */
    dst_buf[9]  = src->hum_half_pct;
    dst_buf[10] = src->flags;

    /* Обчислення та запис CRC16 поверх перших 11 байтів */
    uint16_t crc = crc16_ccitt(dst_buf, 11);
    dst_buf[11] = (uint8_t)((crc >> 8) & 0xFF);
    dst_buf[12] = (uint8_t)(crc & 0xFF);

    return true;
}

/* Десеріалізація з перевіркою версії та контрольної суми */
bool telemetry_unpack(const uint8_t *src_buf, size_t buf_len, TelemetryData *dst) {
    if (!src_buf || !dst || buf_len < TELEM_FRAME_SIZE) {
        return false;
    }

    uint8_t magic_ver = src_buf[0];
    if ((magic_ver & 0xF0) != (TELEM_FRAME_MAGIC & 0xF0)) {
        return false;
    }
    if ((magic_ver & 0x0F) != TELEM_FRAME_VERSION) {
        return false;
    }

    /* Перевірка цілісності CRC16 */
    uint16_t expected_crc = ((uint16_t)src_buf[11] << 8) | src_buf[12];
    uint16_t actual_crc = crc16_ccitt(src_buf, 11);
    if (expected_crc != actual_crc) {
        return false;
    }

    /* Розпакування полів із мережевого порядку байтів */
    dst->timestamp = ((uint32_t)src_buf[1] << 24) |
                     ((uint32_t)src_buf[2] << 16) |
                     ((uint32_t)src_buf[3] << 8)  |
                     (uint32_t)src_buf[4];

    dst->temp_centi_deg  = (int16_t)(((uint16_t)src_buf[5] << 8) | src_buf[6]);
    dst->batt_millivolts = ((uint16_t)src_buf[7] << 8) | src_buf[8];
    dst->hum_half_pct    = src_buf[9];
    dst->flags           = src_buf[10];

    return true;
}
