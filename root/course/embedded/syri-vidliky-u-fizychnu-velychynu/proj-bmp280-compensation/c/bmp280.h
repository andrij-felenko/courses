#ifndef BMP280_H
#define BMP280_H

/*
 * Драйвер цифрового барометра Bosch BMP280.
 * Уся арифметика компенсації — цілочисельна, як у datasheet 1.19.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* ---- Регістрова карта ------------------------------------------------ */

#define BMP280_REG_CALIB_START 0x88u /* 24 байти калібрування, 0x88..0x9F */
#define BMP280_REG_ID          0xD0u
#define BMP280_REG_RESET       0xE0u
#define BMP280_REG_STATUS      0xF3u
#define BMP280_REG_CTRL_MEAS   0xF4u
#define BMP280_REG_CONFIG      0xF5u
#define BMP280_REG_DATA_START  0xF7u /* 6 байтів кадру, 0xF7..0xFC */

#define BMP280_CALIB_LEN 24u
#define BMP280_FRAME_LEN 6u
#define BMP280_CHIP_ID   0x58u /* саме BMP280; 0x60 — це вже BME280 */
#define BMP280_RESET_KEY 0xB6u

/* Біти регістра статусу 0xF3 */
#define BMP280_STATUS_MEASURING (1u << 3)
#define BMP280_STATUS_IM_UPDATE (1u << 0)

/* Значення 20-бітного поля після скидання: вимірювань ще не було. */
#define BMP280_RAW_RESET 0x80000L

/* ---- Коди повернення -------------------------------------------------- */

typedef enum {
    BMP280_OK          =  0,
    BMP280_ERR_BUS     = -1, /* транзакція I2C/SPI не відбулася */
    BMP280_ERR_CHIP_ID = -2, /* на адресі сидить не BMP280 */
    BMP280_ERR_CALIB   = -3, /* калібрування не схоже на дані */
    BMP280_ERR_TIMEOUT = -4, /* датчик не звільнив статус */
    BMP280_ERR_NO_DATA = -5, /* у регістрах ще стоїть 0x80000 */
    BMP280_ERR_DEGEN   = -6, /* var1 == 0: ділення на нуль у поліномі */
    BMP280_ERR_ARG     = -7
} bmp280_status_t;

/* ---- Конфігурація DSP датчика ---------------------------------------- */

/* Кратність апаратного усереднення сигма-дельта АЦП. */
typedef enum {
    BMP280_OS_SKIP = 0, /* канал вимкнено */
    BMP280_OS_X1   = 1,
    BMP280_OS_X2   = 2,
    BMP280_OS_X4   = 3,
    BMP280_OS_X8   = 4,
    BMP280_OS_X16  = 5
} bmp280_os_t;

/* Коефіцієнт придушення вбудованого IIR-фільтра першого порядку. */
typedef enum {
    BMP280_FILTER_OFF = 0,
    BMP280_FILTER_X2  = 1,
    BMP280_FILTER_X4  = 2,
    BMP280_FILTER_X8  = 3,
    BMP280_FILTER_X16 = 4
} bmp280_filter_t;

typedef enum {
    BMP280_MODE_SLEEP  = 0,
    BMP280_MODE_FORCED = 1, /* одне вимірювання на запит, далі сон */
    BMP280_MODE_NORMAL = 3  /* автоцикл з паузою t_sb */
} bmp280_mode_t;

/* Пауза між автоциклами в режимі normal. */
typedef enum {
    BMP280_SB_0M5  = 0,
    BMP280_SB_62M5 = 1,
    BMP280_SB_125  = 2,
    BMP280_SB_250  = 3,
    BMP280_SB_500  = 4,
    BMP280_SB_1000 = 5,
    BMP280_SB_2000 = 6,
    BMP280_SB_4000 = 7
} bmp280_standby_t;

typedef struct {
    bmp280_os_t      os_temp;
    bmp280_os_t      os_press;
    bmp280_filter_t  filter;
    bmp280_standby_t standby;
    bmp280_mode_t    mode;
} bmp280_config_t;

/* ---- Шина ------------------------------------------------------------- */

/*
 * Драйвер не знає, I2C під ним чи SPI: платформа підставляє три
 * операції. read мусить виконати ПАКЕТНУ транзакцію — саме вона
 * гарантує, що всі len байтів походять з одного вимірювання.
 * Обидві операції повертають 0 на успіх.
 */
typedef struct {
    int (*read)(void *ctx, uint8_t reg, uint8_t *dst, size_t len);
    int (*write)(void *ctx, uint8_t reg, uint8_t value);
    void (*delay_ms)(void *ctx, uint32_t ms);
    void *ctx;
} bmp280_bus_t;

/* ---- Дані ------------------------------------------------------------- */

/* Заводські коефіцієнти з OTP-пам'яті кристала (0x88..0x9F). */
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
} bmp280_calib_t;

typedef struct {
    int32_t  temperature_c100; /* соті градуса Цельсія: 2508 = 25.08 °C */
    uint32_t pressure_q24_8;   /* Паскалі у форматі Q24.8 (1/256 Па)    */
    int32_t  t_fine;           /* тонка температура, для діагностики    */
} bmp280_meas_t;

typedef struct {
    bmp280_bus_t    bus;
    bmp280_config_t cfg;
    bmp280_calib_t  calib;
    int32_t         t_fine;
    uint8_t         ctrl_base; /* поля osrs_* без бітів режиму */
    bool            ready;
} bmp280_dev_t;

/* ---- Чиста обробка даних (шина не потрібна) --------------------------- */

bmp280_status_t bmp280_parse_calibration(bmp280_calib_t *calib,
                                         const uint8_t *buf /* 24 байти */);

bmp280_status_t bmp280_unpack_frame(const uint8_t *frame /* 6 байтів */,
                                    int32_t *adc_P, int32_t *adc_T);

/* Повертає соті градуса й одночасно кладе t_fine за вказівником. */
int32_t bmp280_compensate_temperature(const bmp280_calib_t *calib,
                                      int32_t adc_T, int32_t *t_fine);

bmp280_status_t bmp280_compensate_pressure_q24(const bmp280_calib_t *calib,
                                               int32_t t_fine, int32_t adc_P,
                                               uint32_t *out_q24_8);

/* Максимальний час одного перетворення для заданої передискретизації. */
uint32_t bmp280_measure_time_ms(bmp280_os_t os_temp, bmp280_os_t os_press);

/* ---- Робота з живим датчиком ------------------------------------------ */

bmp280_status_t bmp280_init(bmp280_dev_t *dev, const bmp280_bus_t *bus,
                            const bmp280_config_t *cfg);

bmp280_status_t bmp280_read(bmp280_dev_t *dev, bmp280_meas_t *out);

#endif /* BMP280_H */
