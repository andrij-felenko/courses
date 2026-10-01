#ifndef ADXL345_H
#define ADXL345_H

#include <stdint.h>
#include <stdbool.h>

/* ========================================================================= */
/*                          Карта регістрів ADXL345                          */
/* ========================================================================= */
#define ADXL345_REG_DEVID          0x00  /* Ідентифікатор пристрою (значення 0xE5) */
#define ADXL345_REG_THRESH_TAP     0x1D  /* Поріг виявлення дотику (Tap threshold) */
#define ADXL345_REG_OFSX           0x1E  /* Зсув осі X */
#define ADXL345_REG_OFSY           0x1F  /* Зсув осі Y */
#define ADXL345_REG_OFSZ           0x20  /* Зсув осі Z */
#define ADXL345_REG_DUR            0x21  /* Тривалість дотику */
#define ADXL345_REG_LATENT         0x22  /* Затримка подвійного дотику */
#define ADXL345_REG_WINDOW         0x23  /* Вікно подвійного дотику */
#define ADXL345_REG_THRESH_ACT     0x24  /* Поріг виявлення активності */
#define ADXL345_REG_THRESH_INACT   0x25  /* Поріг виявлення неактивності */
#define ADXL345_REG_TIME_INACT     0x26  /* Час неактивності */
#define ADXL345_REG_ACT_INACT_CTL  0x27  /* Керування вісями для акт./неакт. */
#define ADXL345_REG_THRESH_FF      0x28  /* Поріг вільного падіння */
#define ADXL345_REG_TIME_FF        0x29  /* Час вільного падіння */
#define ADXL345_REG_TAP_AXES       0x2A  /* Керування вісями дотику */
#define ADXL345_REG_ACT_TAP_STATUS 0x2B  /* Статус джерела дотику/активності */
#define ADXL345_REG_BW_RATE        0x2C  /* Частота даних (ODR) та енергоспоживання */
#define ADXL345_REG_POWER_CTL      0x2D  /* Керування режимами живлення */
#define ADXL345_REG_INT_ENABLE     0x2E  /* Дозвіл переривань */
#define ADXL345_REG_INT_MAP        0x2F  /* Маршрутизація переривань (INT1 / INT2) */
#define ADXL345_REG_INT_SOURCE     0x30  /* Джерела переривань (прапорці статусу) */
#define ADXL345_REG_DATA_FORMAT    0x31  /* Формат даних (діапазон, роздільність) */
#define ADXL345_REG_DATAX0         0x32  /* Дані осі X (молодший байт) */
#define ADXL345_REG_DATAX1         0x33  /* Дані осі X (старший байт) */
#define ADXL345_REG_DATAY0         0x34  /* Дані осі Y (молодший байт) */
#define ADXL345_REG_DATAY1         0x35  /* Дані осі Y (старший байт) */
#define ADXL345_REG_DATAZ0         0x36  /* Дані осі Z (молодший байт) */
#define ADXL345_REG_DATAZ1         0x37  /* Дані осі Z (старший байт) */
#define ADXL345_REG_FIFO_CTL       0x38  /* Керування буфером FIFO */
#define ADXL345_REG_FIFO_STATUS    0x39  /* Стан заповнення буфера FIFO */

/* ========================================================================= */
/*                          Константи та бітові маски                        */
/* ========================================================================= */
#define ADXL345_DEVICE_ID          0xE5  /* Очікуваний ідентифікатор DEVID */
#define ADXL345_SCALE_FACTOR_G     0.0039f /* Масштабний коефіцієнт (3.9 мг/МЗР) у режимі Full-Res */

/* BW_RATE (0x2C) - Частота вихідних даних (ODR) */
typedef enum {
    ADXL345_ODR_0_10_HZ = 0x00, /* 0.10 Гц */
    ADXL345_ODR_0_20_HZ = 0x01, /* 0.20 Гц */
    ADXL345_ODR_0_39_HZ = 0x02, /* 0.39 Гц */
    ADXL345_ODR_0_78_HZ = 0x03, /* 0.78 Гц */
    ADXL345_ODR_1_56_HZ = 0x04, /* 1.56 Гц */
    ADXL345_ODR_3_12_HZ = 0x05, /* 3.12 Гц */
    ADXL345_ODR_6_25_HZ = 0x06, /* 6.25 Гц */
    ADXL345_ODR_12_5_HZ = 0x07, /* 12.5 Гц */
    ADXL345_ODR_25_HZ   = 0x08, /* 25 Гц */
    ADXL345_ODR_50_HZ   = 0x09, /* 50 Гц */
    ADXL345_ODR_100_HZ  = 0x0A, /* 100 Гц (типове) */
    ADXL345_ODR_200_HZ  = 0x0B, /* 200 Гц */
    ADXL345_ODR_400_HZ  = 0x0C, /* 400 Гц */
    ADXL345_ODR_800_HZ  = 0x0D, /* 800 Гц */
    ADXL345_ODR_1600_HZ = 0x0E, /* 1600 Гц */
    ADXL345_ODR_3200_HZ = 0x0F  /* 3200 Гц */
} adxl345_odr_t;

#define ADXL345_BW_LOW_POWER       (1 << 4) /* Біт зниженого шуму/споживання */

/* POWER_CTL (0x2D) */
#define ADXL345_POWER_CTL_WAKEUP_8HZ  (0 << 0)
#define ADXL345_POWER_CTL_WAKEUP_4HZ  (1 << 0)
#define ADXL345_POWER_CTL_WAKEUP_2HZ  (2 << 0)
#define ADXL345_POWER_CTL_WAKEUP_1HZ  (3 << 0)
#define ADXL345_POWER_CTL_SLEEP       (1 << 2)
#define ADXL345_POWER_CTL_MEASURE     (1 << 3) /* Перехід з Standby у Measurement */
#define ADXL345_POWER_CTL_AUTO_SLEEP  (1 << 4)
#define ADXL345_POWER_CTL_LINK        (1 << 5)

/* DATA_FORMAT (0x31) */
typedef enum {
    ADXL345_RANGE_2G  = 0x00, /* +/-2g */
    ADXL345_RANGE_4G  = 0x01, /* +/-4g */
    ADXL345_RANGE_8G  = 0x02, /* +/-8g */
    ADXL345_RANGE_16G = 0x03  /* +/-16g */
} adxl345_range_t;

#define ADXL345_DATA_FORMAT_FULL_RES (1 << 3) /* Режим високої роздільності Full-Res */
#define ADXL345_DATA_FORMAT_JUSTIFY  (1 << 2) /* Ліве вирівнювання бітів */
#define ADXL345_DATA_FORMAT_SPI_3WIRE(1 << 6) /* 3-провідний режим SPI */
#define ADXL345_DATA_FORMAT_INT_INVERT(1 << 5) /* Інверсія полярності переривань */

/* INT_ENABLE (0x2E), INT_MAP (0x2F), INT_SOURCE (0x30) */
#define ADXL345_INT_OVERRUN        (1 << 0) /* Переповнення FIFO */
#define ADXL345_INT_WATERMARK      (1 << 1) /* Порог заповнення FIFO (Watermark) */
#define ADXL345_INT_FREE_FALL      (1 << 2) /* Вільне падіння */
#define ADXL345_INT_INACTIVITY     (1 << 3) /* Неактивність */
#define ADXL345_INT_ACTIVITY       (1 << 4) /* Активність */
#define ADXL345_INT_DOUBLE_TAP     (1 << 5) /* Подвійний дотик */
#define ADXL345_INT_SINGLE_TAP     (1 << 6) /* Одиночний дотик */
#define ADXL345_INT_DATA_READY     (1 << 7) /* Готовність нових даних */

/* FIFO_CTL (0x38) */
typedef enum {
    ADXL345_FIFO_BYPASS  = 0x00, /* Режим обходу буфера (Bypass) */
    ADXL345_FIFO_FIFO    = 0x01, /* Стандартний FIFO (зупиняється при 32 вибірках) */
    ADXL345_FIFO_STREAM  = 0x02, /* Потоковий буфер (Stream FIFO, кільцевий) */
    ADXL345_FIFO_TRIGGER = 0x03  /* Тригерний режим */
} adxl345_fifo_mode_t;

/* ========================================================================= */
/*                          Типи даних та структури                          */
/* ========================================================================= */

/* Коди помилок драйвера */
typedef enum {
    ADXL345_OK                =  0, /* Успішне виконання */
    ADXL345_ERR_INVALID_ARG   = -1, /* Некоректні аргументи */
    ADXL345_ERR_BUS           = -2, /* Помилка введення/виведення шини */
    ADXL345_ERR_DEVICE_NOT_FOUND = -3 /* Неправильний DEVID сенсора */
} adxl345_status_t;

/* Вказівники на функції шинного інтерфейсу (HAL) */
typedef int32_t (*adxl345_read_fn)(void *intf_ptr, uint8_t reg_addr, uint8_t *data, uint16_t len);
typedef int32_t (*adxl345_write_fn)(void *intf_ptr, uint8_t reg_addr, const uint8_t *data, uint16_t len);

/* Абстрактний апаратний інтерфейс (I2C/SPI HAL) */
typedef struct {
    adxl345_read_fn  read;     /* Функція зчитування блоку регістрів */
    adxl345_write_fn write;    /* Функція запису блоку регістрів */
    void            *intf_ptr; /* Контекст шини (указник на дескриптор I2C/SPI) */
} adxl345_hal_t;

/* Сирі (16-бітні у доповняльному коді) вимірювання осей */
typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} adxl345_raw_data_t;

/* Фізичні значення прискорення в одиницях g */
typedef struct {
    float x;
    float y;
    float z;
} adxl345_accel_g_t;

/* Конфігурація драйвера ADXL345 */
typedef struct {
    adxl345_odr_t       odr;               /* Частота оновлення даних (ODR) */
    adxl345_range_t     range;             /* Діапазон вимірювання (±2g, ±4g, ±8g, ±16g) */
    bool                full_resolution;   /* Режим Full Resolution (3.9 мг/МЗР) */
    adxl345_fifo_mode_t fifo_mode;         /* Режим FIFO (Stream, FIFO, Bypass) */
    uint8_t             watermark_samples; /* Поріг Watermark (1..32 вибірок) */
    uint8_t             int_enable_mask;   /* Маска дозволених переривань */
    uint8_t             int_map_mask;      /* Маршрутизація переривань (0 -> INT1, 1 -> INT2) */
} adxl345_config_t;

/* Основний дескриптор сенсора */
typedef struct {
    adxl345_hal_t    hal;    /* Шинний інтерфейс */
    adxl345_config_t config; /* Поточне налаштування */
    bool             initialized;
} adxl345_dev_t;

/* ========================================================================= */
/*                           Прототипи функцій                               */
/* ========================================================================= */

/* Ініціалізація акселерометра ADXL345 та його конфігурування */
adxl345_status_t adxl345_init(adxl345_dev_t *dev, const adxl345_hal_t *hal, const adxl345_config_t *config);

/* Переведення акселерометра в режим вимірювання (Measurement Mode) */
adxl345_status_t adxl345_set_measure_mode(adxl345_dev_t *dev, bool enable);

/* Атомарне burst-зчитування 6 регістрів сирих вихідних даних (DATAX0..DATAZ1) */
adxl345_status_t adxl345_read_raw(adxl345_dev_t *dev, adxl345_raw_data_t *raw);

/* Зчитування та автоматичний перерахунок у фізичне прискорення в одиницях g */
adxl345_status_t adxl345_read_accel(adxl345_dev_t *dev, adxl345_accel_g_t *accel);

/* Зчитування статусу джерел переривань (регістр INT_SOURCE) */
adxl345_status_t adxl345_read_int_source(adxl345_dev_t *dev, uint8_t *int_source);

/* Зчитування кількості накопичених вибірок у буфері FIFO */
adxl345_status_t adxl345_get_fifo_level(adxl345_dev_t *dev, uint8_t *fifo_entries);

/* Перетворення сирих 16-бітних значень у прискорення в одиницях g */
void adxl345_convert_raw_to_g(const adxl345_raw_data_t *raw, adxl345_accel_g_t *accel);

#endif /* ADXL345_H */
