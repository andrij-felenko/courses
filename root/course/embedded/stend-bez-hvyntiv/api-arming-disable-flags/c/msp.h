#ifndef MSP_H
#define MSP_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define MSP_STATUS      101u
#define MSP_MAX_FRAME   261u   /* 5 байтів шапки + 255 payload + контрольна сума */
#define MSP_MAX_EXTRA    15u   /* молодші 4 біти заголовка BOX-прапорців */

/* Кадр MSP v1:
 *   '$' 'M' <напрямок> <size> <code> <payload[size]> <crc>
 * напрямок: '<' запит до плати, '>' відповідь плати, '!' відмова.
 * crc — XOR по size, code й усьому payload.
 *
 * Розкладка payload MSP_STATUS у Betaflight 4.x:
 *   u16 cycleTime            довжина такту PID, мкс
 *   u16 i2cErrorCounter
 *   u16 sensors              бітова карта наявних сенсорів
 *   u32 flightModeFlags      нижні 32 біти BOX-режимів
 *   u8  pidProfileIndex
 *   u16 averageSystemLoad    відсотки; той самий лічильник, що піднімає LOAD
 *   u16 gyroCycleTime        мкс
 *   u8  header               молодші 4 біти: скільки байтів BOX-прапорців далі
 *   u8  extra[header & 0x0F]
 *   u8  armingDisableFlagCount
 *   u32 armingDisableFlags   <- те, заради чого шлють запит
 *   u8  configStateFlags     біт 0: потрібне перезавантаження
 */

typedef enum {
    MSP_OK = 0,
    MSP_ERR_TOO_SHORT,
    MSP_ERR_BAD_MAGIC,
    MSP_ERR_NOT_A_REPLY,
    MSP_ERR_LENGTH,
    MSP_ERR_CHECKSUM,
    MSP_ERR_UNEXPECTED_CODE,
    MSP_ERR_TRUNCATED
} msp_err_t;

const char *msp_strerror(msp_err_t err);

typedef struct {
    uint16_t cycle_time_us;
    uint16_t i2c_errors;
    uint16_t sensors;
    uint32_t flight_mode_flags;
    uint8_t pid_profile;
    uint16_t cpu_load_pct;
    uint16_t gyro_cycle_time_us;
    uint8_t extra_mode_flags[MSP_MAX_EXTRA];
    uint8_t extra_len;
    uint8_t arming_flag_count;
    uint32_t arming_disable_flags;
    uint8_t config_state;
} msp_status_t;

/* Запит без payload; повертає довжину кадру або 0, якщо буфер малий. */
size_t msp_build_request(uint8_t code, uint8_t *buf, size_t cap);

msp_err_t msp_parse_status(const uint8_t *frame, size_t len, msp_status_t *out);

/* Зворотний бік — потрібен, щоб на стенді мати з чого розбирати
 * без підключеної плати. Повертає довжину кадру або 0. */
size_t msp_encode_status(const msp_status_t *st, uint8_t *buf, size_t cap);

#endif /* MSP_H */
