#ifndef ADXL345_H
#define ADXL345_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file adxl345.h
 * @brief Оголошення драйвера 3-осьового акселерометра ADXL345 для STM32.
 */

/* =========================================================================
 * РЕГІСТРИ ADXL345
 * ========================================================================= */
#define ADXL345_REG_DEVID          0x00U /* Ідентифікатор пристрою (0xE5) */
#define ADXL345_REG_THRESH_TAP     0x1DU /* Поріг для одиночного/подвійного дотику */
#define ADXL345_REG_OFSX           0x1EU /* Калібрувальне зміщення осі X */
#define ADXL345_REG_OFSY           0x1FU /* Калібрувальне зміщення осі Y */
#define ADXL345_REG_OFSZ           0x20U /* Калібрувальне зміщення осі Z */
#define ADXL345_REG_DUR            0x21U /* Тривалість дотику */
#define ADXL345_REG_LATENT         0x22U /* Затримка перед другим дотиком */
#define ADXL345_REG_WINDOW         0x23U /* Вікно другого дотику */
#define ADXL345_REG_THRESH_ACT     0x24U /* Поріг виявлення руху */
#define ADXL345_REG_THRESH_INACT   0x25U /* Поріг виявлення спокою */
#define ADXL345_REG_TIME_INACT     0x26U /* Час відсутності руху */
#define ADXL345_REG_ACT_INACT_CTL  0x27U /* Налаштування вісей руху/спокою */
#define ADXL345_REG_THRESH_FF      0x28U /* Поріг виявлення вільного падіння */
#define ADXL345_REG_TIME_FF        0x29U /* Мінімальний час вільного падіння */
#define ADXL345_REG_TAP_AXES       0x2AU /* Вибір вісей для імпульсу дотику */
#define ADXL345_REG_ACT_TAP_STATUS 0x2BU /* Джерело виникнення дотику/руху */
#define ADXL345_REG_BW_RATE        0x2CU /* Частота вихідних даних та режим живлення */
#define ADXL345_REG_POWER_CTL      0x2DU /* Режими енергозбереження та вимірювання */
#define ADXL345_REG_INT_ENABLE     0x2EU /* Маска дозволу джерел переривань */
#define ADXL345_REG_INT_MAP        0x2FU /* Призначення переривань (0=INT1, 1=INT2) */
#define ADXL345_REG_INT_SOURCE     0x30U /* Прапори активних переривань */
#define ADXL345_REG_DATA_FORMAT    0x31U /* Формат даних, розрядність та діапазон */
#define ADXL345_REG_DATAX0         0x32U /* Молодший байт даних осі X */
#define ADXL345_REG_DATAX1         0x33U /* Старший байт даних осі X */
#define ADXL345_REG_DATAY0         0x34U /* Молодший байт даних осі Y */
#define ADXL345_REG_DATAY1         0x35U /* Старший байт даних осі Y */
#define ADXL345_REG_DATAZ0         0x36U /* Молодший байт даних осі Z */
#define ADXL345_REG_DATAZ1         0x37U /* Старший байт даних осі Z */
#define ADXL345_REG_FIFO_CTL       0x38U /* Управління режимом та порогом FIFO */
#define ADXL345_REG_FIFO_STATUS    0x39U /* Кількість елементів та статус FIFO */

/* =========================================================================
 * КОНСТАНТИ ТА БІТОВІ МАСКИ
 * ========================================================================= */
#define ADXL345_DEVICE_ID          0xE5U /* Базовий ідентифікатор ADXL345 */

/* I2C-адреси пристрою (7-бітна адреса, зсунута вліво на 1 для STM32 HAL) */
#define ADXL345_I2C_ADDR_ALT_LOW   (0x53U << 1) /* ALT ADDRESS = GND */
#define ADXL345_I2C_ADDR_ALT_HIGH  (0x1DU << 1) /* ALT ADDRESS = VDD */

/* Біти регістру POWER_CTL */
#define ADXL345_POWER_CTL_LINK     (1U << 5)
#define ADXL345_POWER_CTL_AUTO_SLP (1U << 4)
#define ADXL345_POWER_CTL_MEASURE  (1U << 3)
#define ADXL345_POWER_CTL_SLEEP    (1U << 2)

/* Біти регістру DATA_FORMAT */
#define ADXL345_DATA_FORMAT_SELF_TEST (1U << 7)
#define ADXL345_DATA_FORMAT_SPI       (1U << 6)
#define ADXL345_DATA_FORMAT_INT_INVERT(1U << 5)
#define ADXL345_DATA_FORMAT_FULL_RES  (1U << 3)
#define ADXL345_DATA_FORMAT_JUSTIFY   (1U << 2)

/* Маски переривань (INT_ENABLE, INT_MAP, INT_SOURCE) */
#define ADXL345_INT_DATA_READY     (1U << 7)
#define ADXL345_INT_SINGLE_TAP     (1U << 6)
#define ADXL345_INT_DOUBLE_TAP     (1U << 5)
#define ADXL345_INT_ACTIVITY       (1U << 4)
#define ADXL345_INT_INACTIVITY     (1U << 3)
#define ADXL345_INT_FREE_FALL      (1U << 2)
#define ADXL345_INT_WATERMARK      (1U << 1)
#define ADXL345_INT_OVERRUN        (1U << 0)

/* =========================================================================
 * ТИПИ ДАНИХ
 * ========================================================================= */

/**
 * @brief Статус виконання операцій драйвера.
 */
typedef enum {
    ADXL345_OK          =  0, /* Операція успішна */
    ADXL345_ERR_PARAM   = -1, /* Некоректний аргумент */
    ADXL345_ERR_BUS     = -2, /* Помилка обміну по шині */
    ADXL345_ERR_DEV_ID  = -3, /* Невірний ідентифікатор пристрою */
    ADXL345_ERR_TIMEOUT = -4  /* Перевищено час очікування */
} adxl345_status_t;

/**
 * @brief Діапазони вимірювання прискорення.
 */
typedef enum {
    ADXL345_RANGE_2G  = 0x00U, /* +-2 g */
    ADXL345_RANGE_4G  = 0x01U, /* +-4 g */
    ADXL345_RANGE_8G  = 0x02U, /* +-8 g */
    ADXL345_RANGE_16G = 0x03U  /* +-16 g */
} adxl345_range_t;

/**
 * @brief Частота вихідних даних (Output Data Rate, ODR).
 */
typedef enum {
    ADXL345_ODR_0_10HZ = 0x00U,
    ADXL345_ODR_0_20HZ = 0x01U,
    ADXL345_ODR_0_39HZ = 0x02U,
    ADXL345_ODR_0_78HZ = 0x03U,
    ADXL345_ODR_1_56HZ = 0x04U,
    ADXL345_ODR_3_13HZ = 0x05U,
    ADXL345_ODR_6_25HZ = 0x06U,
    ADXL345_ODR_12_5HZ = 0x07U,
    ADXL345_ODR_25HZ   = 0x08U,
    ADXL345_ODR_50HZ   = 0x09U,
    ADXL345_ODR_100HZ  = 0x0AU, /* Типова за замовчуванням */
    ADXL345_ODR_200HZ  = 0x0BU,
    ADXL345_ODR_400HZ  = 0x0CU,
    ADXL345_ODR_800HZ  = 0x0DU,
    ADXL345_ODR_1600HZ = 0x0EU,
    ADXL345_ODR_3200HZ = 0x0FU
} adxl345_odr_t;

/**
 * @brief Режими роботи апаратного FIFO-буфера.
 */
typedef enum {
    ADXL345_FIFO_BYPASS  = 0x00U, /* Буфер вимкнено */
    ADXL345_FIFO_FIFO    = 0x01U, /* Заповнення до 32 відліків з зупинкою */
    ADXL345_FIFO_STREAM  = 0x02U, /* Кільцевий буфер (перезапис старих кадрів) */
    ADXL345_FIFO_TRIGGER = 0x03U  /* Запис призупиняється за подією */
} adxl345_fifo_mode_t;

/**
 * @brief Сирі (16-бітні) значення відліків акселерометра LSB.
 */
typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} adxl345_raw_data_t;

/**
 * @brief Перераховані фізичні значення прискорення у g.
 */
typedef struct {
    float x;
    float y;
    float z;
} adxl345_accel_t;

/**
 * @brief Покажчики на функції читання/запису шини.
 */
typedef int32_t (*adxl345_read_fn)(void *handle, uint8_t reg_addr, uint8_t *data, uint16_t len);
typedef int32_t (*adxl345_write_fn)(void *handle, uint8_t reg_addr, const uint8_t *data, uint16_t len);

/**
 * @brief Структура дескриптора пристрою ADXL345.
 */
typedef struct {
    adxl345_read_fn   read;         /* Функція читання шини */
    adxl345_write_fn  write;        /* Функція запису в шину */
    void             *user_handle;  /* Контекст шини (наприклад, I2C_HandleTypeDef*) */
    uint8_t           i2c_addr;     /* I2C-адреса */
    adxl345_range_t   range;        /* Поточний діапазон вимірювання */
    bool              full_res;     /* Режим максимальної роздільності */
    float             scale_factor; /* Чутливість у g/LSB */
} adxl345_dev_t;

/* =========================================================================
 * ПУБЛІЧНЕ API
 * ========================================================================= */

/**
 * @brief Ініціалізувати датчик, перевірити DEVID та активувати вимірювання.
 */
adxl345_status_t adxl345_init(adxl345_dev_t *dev);

/**
 * @brief Налаштувати формат даних (діапазон та розрядність).
 */
adxl345_status_t adxl345_set_data_format(adxl345_dev_t *dev, adxl345_range_t range, bool full_res);

/**
 * @brief Встановити частоту вихідних даних (ODR).
 */
adxl345_status_t adxl345_set_bandwidth(adxl345_dev_t *dev, adxl345_odr_t bw_rate);

/**
 * @brief Конфігурувати режим FIFO та поріг Watermark (1..32 відліки).
 */
adxl345_status_t adxl345_set_fifo_config(adxl345_dev_t *dev, adxl345_fifo_mode_t mode, uint8_t watermark_samples);

/**
 * @brief Налаштувати маски дозволу переривань та їх маршрутизацію на INT1/INT2.
 */
adxl345_status_t adxl345_configure_interrupts(adxl345_dev_t *dev, uint8_t enable_mask, uint8_t map_mask);

/**
 * @brief Зчитати один 6-байтовий кадр (X, Y, Z) у burst-режимі.
 */
adxl345_status_t adxl345_read_raw_frame(adxl345_dev_t *dev, adxl345_raw_data_t *raw);

/**
 * @brief Прочитати поточну кількість збережених відліків у FIFO.
 */
adxl345_status_t adxl345_read_fifo_entries(adxl345_dev_t *dev, uint8_t *entries);

/**
 * @brief Прочитати регістр джерел переривань INT_SOURCE.
 */
adxl345_status_t adxl345_read_interrupt_source(adxl345_dev_t *dev, uint8_t *int_source);

/**
 * @brief Конвертувати сирі LSB значення у фізичне прискорення (g).
 */
void adxl345_convert_raw_to_g(const adxl345_dev_t *dev, const adxl345_raw_data_t *raw, adxl345_accel_t *accel);

#endif /* ADXL345_H */
