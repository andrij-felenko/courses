#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RF_MAGIC_WORD       0x52464341  /* "RFCA" - RF Calibration Array */
#define RF_CHANNEL_COUNT    14
#define MAX_POWER_DBM       20
#define MIN_POWER_DBM       -10

typedef enum {
    RF_CALIB_OK = 0,
    RF_CALIB_ERR_MAGIC,
    RF_CALIB_ERR_CRC,
    RF_CALIB_ERR_RANGE,
    RF_CALIB_ERR_HARDWARE
} rf_calib_status_t;

typedef struct {
    uint32_t magic;
    uint8_t  xtal_cap_trim;              /* Коригування навантажувальної ємності кварца (0..63) */
    int8_t   power_offset_dbm[RF_CHANNEL_COUNT]; /* Поправка вихідної потужності для кожного каналу */
    uint16_t crc16;
} __attribute__((packed)) rf_calibration_data_t;

static uint16_t calculate_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

rf_calib_status_t rf_apply_calibration(const rf_calibration_data_t *calib) {
    if (calib == NULL) {
        return RF_CALIB_ERR_HARDWARE;
    }
    if (calib->magic != RF_MAGIC_WORD) {
        return RF_CALIB_ERR_MAGIC;
    }

    /* Перевірка контрольної суми структури без поля crc16 */
    size_t payload_len = sizeof(rf_calibration_data_t) - sizeof(uint16_t);
    uint16_t computed_crc = calculate_crc16((const uint8_t *)calib, payload_len);
    if (computed_crc != calib->crc16) {
        return RF_CALIB_ERR_CRC;
    }

    if (calib->xtal_cap_trim > 63) {
        return RF_CALIB_ERR_RANGE;
    }

    /* Запис коригування кварца у фіксований регістр апаратного PLL (імітація HW) */
    volatile uint32_t *xtal_reg = (volatile uint32_t *)0x40024040;
    *xtal_reg = (*xtal_reg & ~0x3F) | (calib->xtal_cap_trim & 0x3F);

    /* Запис поправкових коефіцієнтів у таблицю потужності трансивера */
    volatile int8_t *power_lut = (volatile int8_t *)0x40024100;
    for (uint8_t ch = 0; ch < RF_CHANNEL_COUNT; ++ch) {
        int8_t offset = calib->power_offset_dbm[ch];
        if (offset < -12 || offset > 12) {
            return RF_CALIB_ERR_RANGE;
        }
        power_lut[ch] = offset;
    }

    return RF_CALIB_OK;
}
