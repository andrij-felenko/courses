/**
 * @file driver_bmp280.h
 * @brief Промисловий MISRA-сумісний драйвер цифрового датчика тиску та температури.
 * @details Реалізація асинхронного неблокуючого драйвера з підтримкою DMA,
 *          цілочисельної компенсації у Q-форматі та автоматів відновлення шини.
 */

#ifndef DRIVER_BMP280_H
#define DRIVER_BMP280_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ── Регістрова карта чипа ─────────────────────────────────────────────────── */
#define BMP280_REG_TEMP_XLSB      0xFCU
#define BMP280_REG_TEMP_LSB       0xFBU
#define BMP280_REG_TEMP_MSB       0xFAU
#define BMP280_REG_PRESS_XLSB     0xF9U
#define BMP280_REG_PRESS_LSB      0xF8U
#define BMP280_REG_PRESS_MSB      0xF7U
#define BMP280_REG_CONFIG         0xF5U
#define BMP280_REG_CTRL_MEAS      0xF4U
#define BMP280_REG_STATUS         0xF3U
#define BMP280_REG_RESET          0xE0U
#define BMP280_REG_CHIP_ID        0xD0U
#define BMP280_REG_CALIB_START    0x88U

#define BMP280_CHIP_ID_VALUE      0x58U
#define BMP280_SOFT_RESET_CMD     0xB6U
#define BMP280_CALIB_DATA_SIZE    24U
#define BMP280_BURST_DATA_SIZE    6U

/* ── Статуси та коди помилок драйвера ─────────────────────────────────────── */
typedef enum {
    BMP280_OK = 0,
    BMP280_ERR_NULL_PTR,
    BMP280_ERR_INVALID_ID,
    BMP280_ERR_BUS_TIMEOUT,
    BMP280_ERR_BUS_NACK,
    BMP280_ERR_CRC_MISMATCH,
    BMP280_ERR_BUSY,
    BMP280_ERR_RECOVERY_FAILED,
    BMP280_ERR_OVERFLOW
} bmp280_status_t;

/* ── Режими роботи та конфігурація передискретизації (OSR) ─────────────────── */
typedef enum {
    BMP280_OSR_SKIPPED = 0x00U,
    BMP280_OSR_1X      = 0x01U,
    BMP280_OSR_2X      = 0x02U,
    BMP280_OSR_4X      = 0x03U,
    BMP280_OSR_8X      = 0x04U,
    BMP280_OSR_16X     = 0x05U
} bmp280_osr_t;

typedef enum {
    BMP280_MODE_SLEEP  = 0x00U,
    BMP280_MODE_FORCED = 0x01U,
    BMP280_MODE_NORMAL = 0x03U
} bmp280_mode_t;

typedef enum {
    BMP280_FILTER_OFF = 0x00U,
    BMP280_FILTER_2   = 0x01U,
    BMP280_FILTER_4   = 0x02U,
    BMP280_FILTER_8   = 0x03U,
    BMP280_FILTER_16  = 0x04U
} bmp280_filter_t;

typedef enum {
    BMP280_STANDBY_0_5_MS  = 0x00U,
    BMP280_STANDBY_62_5_MS = 0x01U,
    BMP280_STANDBY_125_MS  = 0x02U,
    BMP280_STANDBY_250_MS  = 0x03U,
    BMP280_STANDBY_500_MS  = 0x04U,
    BMP280_STANDBY_1000_MS = 0x05U
} bmp280_standby_t;

/* ── Машина станів драйвера ───────────────────────────────────────────────── */
typedef enum {
    BMP280_STATE_UNINITIALIZED = 0,
    BMP280_STATE_RESETTING,
    BMP280_STATE_READING_NVM,
    BMP280_STATE_CONFIGURING,
    BMP280_STATE_IDLE,
    BMP280_STATE_MEASURING,
    BMP280_STATE_BURST_READ_DMA,
    BMP280_STATE_COMPENSATING,
    BMP280_STATE_RECOVERY,
    BMP280_STATE_FATAL_ERROR
} bmp280_state_t;

/* ── Фабричні коефіцієнти NVM ─────────────────────────────────────────────── */
typedef struct {
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;
    uint16_t dig_P1;
    int16_t  dig_P2;
    int16_t  dig_P3;
    int16_t  dig_P4;
    int16_t  dig_P5;
    int16_t  dig_P6;
    int16_t  dig_P7;
    int16_t  dig_P8;
    int16_t  dig_P9;
} bmp280_calib_data_t;

/* ── Фізичні інженерні значення у SI ──────────────────────────────────────── */
typedef struct {
    int32_t  temperature_centidegrees;  /**< Температура: 2465 = 24.65 °C */
    uint32_t pressure_pascals;          /**< Тиск у Паскалях: 101325 Па */
    uint32_t pressure_q24_8;            /**< Тиск у форматі Q24.8 Паскалів */
    uint32_t timestamp_us;              /**< Мітка часу захоплення вибірки */
    bool     valid;                     /**< Прапорець достовірності даних */
} bmp280_sample_t;

/* ── Абстракція шини зв'язку (Hardware Bus Interface) ─────────────────────── */
typedef struct {
    uint8_t dev_addr;
    bmp280_status_t (*read)(uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, uint16_t len);
    bmp280_status_t (*write)(uint8_t dev_addr, uint8_t reg_addr, const uint8_t *data, uint16_t len);
    bmp280_status_t (*read_dma_start)(uint8_t dev_addr, uint8_t reg_addr, uint8_t *buf, uint16_t len);
    void            (*delay_ms)(uint32_t ms);
    void            (*bus_recover)(void);
} bmp280_bus_t;

/* ── Головний контекст дескриптора драйвера ───────────────────────────────── */
typedef struct {
    bmp280_bus_t        bus;
    bmp280_calib_data_t calib;
    bmp280_state_t      state;
    int32_t             t_fine;
    uint8_t             dma_rx_buf[BMP280_BURST_DATA_SIZE];
    bmp280_sample_t     last_sample;
    uint32_t            error_count;
    uint32_t            recovery_count;
} bmp280_handle_t;

/* ── Публічний API драйвера ───────────────────────────────────────────────── */
bmp280_status_t bmp280_init(bmp280_handle_t *dev, const bmp280_bus_t *bus);
bmp280_status_t bmp280_configure(bmp280_handle_t *dev,
                                 bmp280_osr_t osr_t,
                                 bmp280_osr_t osr_p,
                                 bmp280_mode_t mode,
                                 bmp280_filter_t filter,
                                 bmp280_standby_t standby);

bmp280_status_t bmp280_read_sync(bmp280_handle_t *dev, bmp280_sample_t *sample);
bmp280_status_t bmp280_start_read_async_dma(bmp280_handle_t *dev);
void            bmp280_dma_complete_callback(bmp280_handle_t *dev);
bmp280_status_t bmp280_compensate(bmp280_handle_t *dev, const uint8_t *raw_6b, bmp280_sample_t *out_sample);

uint8_t         bmp280_calc_crc8_dallas(const uint8_t *data, size_t len);
bmp280_status_t bmp280_recover_bus(bmp280_handle_t *dev);

#ifdef __cplusplus
}
#endif

#endif /* DRIVER_BMP280_H */
