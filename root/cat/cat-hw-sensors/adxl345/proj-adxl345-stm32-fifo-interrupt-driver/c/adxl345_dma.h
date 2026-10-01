/**
 * @file adxl345_dma.h
 * @brief Заголовний файл драйвера акселерометра ADXL345 для STM32 HAL.
 * @details Підтримує SPI Mode 3, режим FIFO Stream, переривання watermark INT1
 *          та безблокуюче зчитування масиву вимірювань через SPI DMA.
 */

#ifndef ADXL345_DMA_H
#define ADXL345_DMA_H

#include "stm32f4xx_hal.h"
#include <stdint.h>
#include <stdbool.h>

/* Адреси регістрів акселерометра ADXL345 */
#define ADXL345_REG_DEVID          0x00
#define ADXL345_REG_THRESH_TAP     0x1D
#define ADXL345_REG_OFSX           0x1E
#define ADXL345_REG_OFSY           0x1F
#define ADXL345_REG_OFSZ           0x20
#define ADXL345_REG_DUR            0x21
#define ADXL345_REG_LATENT         0x22
#define ADXL345_REG_WINDOW         0x23
#define ADXL345_REG_THRESH_ACT     0x24
#define ADXL345_REG_THRESH_INACT   0x25
#define ADXL345_REG_TIME_INACT     0x26
#define ADXL345_REG_ACT_INACT_CTL  0x27
#define ADXL345_REG_THRESH_FF      0x28
#define ADXL345_REG_TIME_FF        0x29
#define ADXL345_REG_TAP_AXES       0x2A
#define ADXL345_REG_ACT_TAP_STATUS 0x2B
#define ADXL345_REG_BW_RATE        0x2C
#define ADXL345_REG_POWER_CTL      0x2D
#define ADXL345_REG_INT_ENABLE     0x2E
#define ADXL345_REG_INT_MAP        0x2F
#define ADXL345_REG_INT_SOURCE     0x30
#define ADXL345_REG_DATA_FORMAT    0x31
#define ADXL345_REG_DATAX0         0x32
#define ADXL345_REG_DATAX1         0x33
#define ADXL345_REG_DATAY0         0x34
#define ADXL345_REG_DATAY1         0x35
#define ADXL345_REG_DATAZ0         0x36
#define ADXL345_REG_DATAZ1         0x37
#define ADXL345_REG_FIFO_CTL       0x38
#define ADXL345_REG_FIFO_STATUS    0x39

/* Бітові маски та прапори SPI протоколу ADXL345 */
#define ADXL345_SPI_READ           0x80
#define ADXL345_SPI_MB             0x40
#define ADXL345_DEVID_VAL          0xE5

/* Біти регістру POWER_CTL */
#define ADXL345_POWER_CTL_MEASURE  0x08
#define ADXL345_POWER_CTL_STANDBY  0x00

/* Біти регістру INT_ENABLE / INT_SOURCE */
#define ADXL345_INT_DATA_READY     0x80
#define ADXL345_INT_WATERMARK      0x02
#define ADXL345_INT_OVERRUN        0x01

/* Біти регістру DATA_FORMAT */
#define ADXL345_DATA_FORMAT_FULL_RES 0x08
#define ADXL345_DATA_FORMAT_INT_INVERT 0x20

/* Максимальна кількість відліків у FIFO буфері */
#define ADXL345_MAX_FIFO_SAMPLES   32
#define ADXL345_BYTES_PER_SAMPLE   6
#define ADXL345_DMA_BUF_SIZE       (1 + (ADXL345_MAX_FIFO_SAMPLES * ADXL345_BYTES_PER_SAMPLE))

/**
 * @brief Перелік діапазонів вимірювання прискорення.
 */
typedef enum {
    ADXL345_RANGE_2G  = 0x00,
    ADXL345_RANGE_4G  = 0x01,
    ADXL345_RANGE_8G  = 0x02,
    ADXL345_RANGE_16G = 0x03
} adxl345_range_t;

/**
 * @brief Перелік частот вихідних даних (ODR).
 */
typedef enum {
    ADXL345_ODR_6_25HZ = 0x06,
    ADXL345_ODR_12_5HZ = 0x07,
    ADXL345_ODR_25HZ   = 0x08,
    ADXL345_ODR_50HZ   = 0x09,
    ADXL345_ODR_100HZ  = 0x0A,
    ADXL345_ODR_200HZ  = 0x0B,
    ADXL345_ODR_400HZ  = 0x0C,
    ADXL345_ODR_800HZ  = 0x0D,
    ADXL345_ODR_1600HZ = 0x0E,
    ADXL345_ODR_3200HZ = 0x0F
} adxl345_odr_t;

/**
 * @brief Режими роботи апаратного FIFO буфера.
 */
typedef enum {
    ADXL345_FIFO_BYPASS = 0x00,
    ADXL345_FIFO_FIFO   = 0x40,
    ADXL345_FIFO_STREAM = 0x80,
    ADXL345_FIFO_TRIGGER= 0xC0
} adxl345_fifo_mode_t;

/**
 * @brief Перелік станів скінченного автомата драйвера.
 */
typedef enum {
    ADXL345_STATE_UNINIT = 0,
    ADXL345_STATE_IDLE,
    ADXL345_STATE_BUSY_DMA,
    ADXL345_STATE_DATA_READY,
    ADXL345_STATE_ERROR
} adxl345_state_t;

/**
 * @brief Коди повернення функцій драйвера.
 */
typedef enum {
    ADXL345_OK = 0,
    ADXL345_ERROR,
    ADXL345_BUSY,
    ADXL345_ERR_DEVID,
    ADXL345_ERR_PARAM
} adxl345_status_t;

/**
 * @brief Структура одного вимірювання (відліку) акселерометра.
 */
typedef struct {
    int16_t x_raw;
    int16_t y_raw;
    int16_t z_raw;
    float x_g;
    float y_g;
    float z_g;
} adxl345_sample_t;

/* Випереджувальне оголошення структури хендла */
typedef struct adxl345_handle_s adxl345_handle_t;

/**
 * @brief Тип покажчика на функцію зворотного виклику готовності даних.
 */
typedef void (*adxl345_callback_t)(adxl345_handle_t *hdev, uint8_t sample_count);

/**
 * @brief Структура конфігурації драйвера ADXL345.
 */
typedef struct {
    SPI_HandleTypeDef *hspi;
    GPIO_TypeDef *cs_port;
    uint16_t cs_pin;
    GPIO_TypeDef *int1_port;
    uint16_t int1_pin;
    adxl345_odr_t odr;
    adxl345_range_t range;
    uint8_t watermark_samples;
    adxl345_callback_t data_ready_cb;
} adxl345_config_t;

/**
 * @brief Головний хендл драйвера ADXL345.
 */
struct adxl345_handle_s {
    adxl345_config_t config;
    volatile adxl345_state_t state;
    float scale_factor;
    uint8_t tx_buf[ADXL345_DMA_BUF_SIZE];
    uint8_t rx_buf[ADXL345_DMA_BUF_SIZE];
    adxl345_sample_t samples[ADXL345_MAX_FIFO_SAMPLES];
    uint8_t samples_count;
};

/* Прототипи публічних функцій драйвера */
adxl345_status_t ADXL345_Init(adxl345_handle_t *hdev, const adxl345_config_t *cfg);
adxl345_status_t ADXL345_TriggerBurstReadDMA(adxl345_handle_t *hdev);
void ADXL345_OnSpiTxRxCplt(adxl345_handle_t *hdev);
void ADXL345_OnGpioExti(adxl345_handle_t *hdev, uint16_t GPIO_Pin);
adxl345_status_t ADXL345_ReadRegister(adxl345_handle_t *hdev, uint8_t reg, uint8_t *val);
adxl345_status_t ADXL345_WriteRegister(adxl345_handle_t *hdev, uint8_t reg, uint8_t val);

#endif /* ADXL345_DMA_H */
