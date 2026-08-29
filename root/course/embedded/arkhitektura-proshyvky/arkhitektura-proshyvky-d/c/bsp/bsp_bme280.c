/* bsp/bsp_bme280.c — приватна реалізація драйвера BME280.
 * Формули компенсації взято з довідника мікросхеми (Bosch BME280,
 * розділ «Compensation formulas»): вони цілочислові навмисно, бо на
 * ядрах без блока плаваючої коми числа з комою коштують сотні тактів. */
#include "bsp/bsp_bme280.h"

#include "hal/hal_time.h"

#include <string.h>

/* --- Карта регістрів --- */
#define BME280_REG_CALIB_00      0x88u  /* dig_T1..dig_P9, 26 байтів */
#define BME280_REG_ID            0xD0u
#define BME280_REG_RESET         0xE0u
#define BME280_REG_CALIB_26      0xE1u  /* dig_H2..dig_H6, 7 байтів */
#define BME280_REG_CTRL_HUM      0xF2u
#define BME280_REG_STATUS        0xF3u
#define BME280_REG_CTRL_MEAS     0xF4u
#define BME280_REG_CONFIG        0xF5u
#define BME280_REG_PRESS_MSB     0xF7u  /* 8 байтів сирих даних поспіль */

#define BME280_CHIP_ID           0x60u
#define BME280_RESET_WORD        0xB6u
#define BME280_STATUS_MEASURING  0x08u

/* Передискретизація ×1 для всіх трьох величин, режим forced. */
#define BME280_OSRS_H_X1         0x01u
#define BME280_CTRL_MEAS_FORCED  0x25u  /* osrs_t=1, osrs_p=1, mode=forced */
#define BME280_CONFIG_FILTER_OFF 0x00u

#define BME280_MEASURE_TIMEOUT_MS 20u
#define BME280_MAGIC              0x424D4532u /* "BME2" */

struct bsp_bme280 {
    uint32_t             magic;
    const hal_i2c_bus_t *bus;
    uint8_t              addr;
    hal_i2c_status_t     last_error;

    /* Калібрувальна таблиця, індивідуальна для кожного примірника
     * мікросхеми: її прошивають на заводі й читають при старті. */
    uint16_t dig_t1;
    int16_t  dig_t2, dig_t3;
    uint16_t dig_p1;
    int16_t  dig_p2, dig_p3, dig_p4, dig_p5, dig_p6, dig_p7, dig_p8, dig_p9;
    uint8_t  dig_h1, dig_h3;
    int16_t  dig_h2, dig_h4, dig_h5;
    int8_t   dig_h6;

    int32_t  t_fine; /* спільний проміжок температури для тиску й вологості */
};

_Static_assert(sizeof(struct bsp_bme280) <= sizeof(bsp_bme280_storage_t),
               "bsp_bme280_storage_t замалий: збільште bytes[] у заголовку");

static bool handle_is_live(const struct bsp_bme280 *dev)
{
    return dev != 0 && dev->magic == BME280_MAGIC;
}

static uint16_t u16_le(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static int16_t s16_le(const uint8_t *p)
{
    return (int16_t)u16_le(p);
}

static bool read_calibration(struct bsp_bme280 *dev)
{
    uint8_t buf[26] = { 0u };

    hal_i2c_status_t st =
        hal_i2c_read_regs(dev->bus, dev->addr, BME280_REG_CALIB_00, buf, sizeof buf);
    if (st != HAL_I2C_OK) {
        dev->last_error = st;
        return false;
    }

    dev->dig_t1 = u16_le(&buf[0]);
    dev->dig_t2 = s16_le(&buf[2]);
    dev->dig_t3 = s16_le(&buf[4]);
    dev->dig_p1 = u16_le(&buf[6]);
    dev->dig_p2 = s16_le(&buf[8]);
    dev->dig_p3 = s16_le(&buf[10]);
    dev->dig_p4 = s16_le(&buf[12]);
    dev->dig_p5 = s16_le(&buf[14]);
    dev->dig_p6 = s16_le(&buf[16]);
    dev->dig_p7 = s16_le(&buf[18]);
    dev->dig_p8 = s16_le(&buf[20]);
    dev->dig_p9 = s16_le(&buf[22]);
    dev->dig_h1 = buf[25];

    uint8_t hbuf[7] = { 0u };
    st = hal_i2c_read_regs(dev->bus, dev->addr, BME280_REG_CALIB_26, hbuf, sizeof hbuf);
    if (st != HAL_I2C_OK) {
        dev->last_error = st;
        return false;
    }

    dev->dig_h2 = s16_le(&hbuf[0]);
    dev->dig_h3 = hbuf[2];
    /* dig_H4 і dig_H5 — дванадцятибітні зі спільним байтом hbuf[3+1]. */
    dev->dig_h4 = (int16_t)(((int16_t)(int8_t)hbuf[3] * 16) | (int16_t)(hbuf[4] & 0x0Fu));
    dev->dig_h5 = (int16_t)(((int16_t)(int8_t)hbuf[5] * 16) | (int16_t)(hbuf[4] >> 4));
    dev->dig_h6 = (int8_t)hbuf[6];

    /* dig_P1 нульовий означає порожню калібрувальну таблицю: далі буде
     * ділення на нуль у формулі тиску, тож ловимо тут. */
    if (dev->dig_t1 == 0u || dev->dig_p1 == 0u) {
        dev->last_error = HAL_I2C_ERR_BUS;
        return false;
    }
    return true;
}

/* Температура в сотих градуса. Побічно наповнює t_fine. */
static int32_t compensate_temperature(struct bsp_bme280 *dev, int32_t adc_t)
{
    int32_t var1 = ((((adc_t >> 3) - ((int32_t)dev->dig_t1 << 1))) *
                    ((int32_t)dev->dig_t2)) >> 11;

    int32_t var2 = (((((adc_t >> 4) - ((int32_t)dev->dig_t1)) *
                      ((adc_t >> 4) - ((int32_t)dev->dig_t1))) >> 12) *
                    ((int32_t)dev->dig_t3)) >> 14;

    dev->t_fine = var1 + var2;
    return (dev->t_fine * 5 + 128) >> 8;
}

/* Тиск у форматі Q24.8 паскалів (ділити на 256). */
static uint32_t compensate_pressure(const struct bsp_bme280 *dev, int32_t adc_p)
{
    int64_t var1 = ((int64_t)dev->t_fine) - 128000;
    int64_t var2 = var1 * var1 * (int64_t)dev->dig_p6;
    var2 = var2 + ((var1 * (int64_t)dev->dig_p5) << 17);
    var2 = var2 + (((int64_t)dev->dig_p4) << 35);
    var1 = ((var1 * var1 * (int64_t)dev->dig_p3) >> 8) +
           ((var1 * (int64_t)dev->dig_p2) << 12);
    var1 = (((((int64_t)1) << 47) + var1)) * ((int64_t)dev->dig_p1) >> 33;

    if (var1 == 0) {
        return 0u; /* ділення на нуль у довіднику згадане окремо */
    }

    int64_t p = 1048576 - adc_p;
    p = (((p << 31) - var2) * 3125) / var1;
    var1 = (((int64_t)dev->dig_p9) * (p >> 13) * (p >> 13)) >> 25;
    var2 = (((int64_t)dev->dig_p8) * p) >> 19;
    p = ((p + var1 + var2) >> 8) + (((int64_t)dev->dig_p7) << 4);
    return (uint32_t)p;
}

/* Вологість у форматі Q22.10 відсотків (ділити на 1024). */
static uint32_t compensate_humidity(const struct bsp_bme280 *dev, int32_t adc_h)
{
    int32_t v = dev->t_fine - ((int32_t)76800);

    v = (((((adc_h << 14) - (((int32_t)dev->dig_h4) << 20) -
            (((int32_t)dev->dig_h5) * v)) + ((int32_t)16384)) >> 15) *
         (((((((v * ((int32_t)dev->dig_h6)) >> 10) *
              (((v * ((int32_t)dev->dig_h3)) >> 11) + ((int32_t)32768))) >> 10) +
            ((int32_t)2097152)) * ((int32_t)dev->dig_h2) + 8192) >> 14));

    v = v - (((((v >> 15) * (v >> 15)) >> 7) * ((int32_t)dev->dig_h1)) >> 4);

    if (v < 0) {
        v = 0;
    }
    if (v > 419430400) {
        v = 419430400; /* стеля 100 %RH */
    }
    return (uint32_t)(v >> 12);
}

bsp_bme280_t *bsp_bme280_init(bsp_bme280_storage_t *storage,
                              const hal_i2c_bus_t *bus,
                              uint8_t i2c_addr)
{
    if (storage == 0 || !hal_i2c_bus_is_valid(bus)) {
        return 0;
    }

    struct bsp_bme280 *dev = (struct bsp_bme280 *)storage;
    memset(dev, 0, sizeof *dev);
    dev->bus  = bus;
    dev->addr = i2c_addr;

    uint8_t chip_id = 0u;
    hal_i2c_status_t st = hal_i2c_read_reg(bus, i2c_addr, BME280_REG_ID, &chip_id);
    if (st != HAL_I2C_OK) {
        dev->last_error = st;
        return 0;
    }
    if (chip_id != BME280_CHIP_ID) {
        /* 0x58 — це BMP280 без вологості, 0x61 — BME680. Мовчки видавати
         * їхні покази за наші не можна: формули вологості інші. */
        dev->last_error = HAL_I2C_ERR_BUS;
        return 0;
    }

    st = hal_i2c_write_reg(bus, i2c_addr, BME280_REG_RESET, BME280_RESET_WORD);
    if (st != HAL_I2C_OK) {
        dev->last_error = st;
        return 0;
    }
    hal_time_delay_ms(5u); /* копіювання калібрувальної таблиці з ПЗП */

    if (!read_calibration(dev)) {
        return 0;
    }

    /* Регістр ctrl_hum набирає чинності лише після запису ctrl_meas —
     * саме тому порядок цих двох рядків не можна міняти місцями. */
    st = hal_i2c_write_reg(bus, i2c_addr, BME280_REG_CTRL_HUM, BME280_OSRS_H_X1);
    if (st == HAL_I2C_OK) {
        st = hal_i2c_write_reg(bus, i2c_addr, BME280_REG_CONFIG, BME280_CONFIG_FILTER_OFF);
    }
    if (st != HAL_I2C_OK) {
        dev->last_error = st;
        return 0;
    }

    dev->magic      = BME280_MAGIC;
    dev->last_error = HAL_I2C_OK;
    return dev;
}

bool bsp_bme280_measure(bsp_bme280_t *dev, bsp_bme280_readings_t *out_readings)
{
    if (!handle_is_live(dev) || out_readings == 0) {
        return false;
    }

    hal_i2c_status_t st = hal_i2c_write_reg(dev->bus, dev->addr,
                                            BME280_REG_CTRL_MEAS,
                                            BME280_CTRL_MEAS_FORCED);
    if (st != HAL_I2C_OK) {
        dev->last_error = st;
        return false;
    }

    /* Чекаємо на кінець перетворення за прапорцем, а не наосліп: так
     * драйвер не заклякне назавжди, коли давач відвалиться посеред виміру. */
    const uint32_t started_ms = hal_time_now_ms();
    for (;;) {
        uint8_t status = 0u;
        st = hal_i2c_read_reg(dev->bus, dev->addr, BME280_REG_STATUS, &status);
        if (st != HAL_I2C_OK) {
            dev->last_error = st;
            return false;
        }
        if ((status & BME280_STATUS_MEASURING) == 0u) {
            break;
        }
        if (hal_time_elapsed_ms(started_ms) > BME280_MEASURE_TIMEOUT_MS) {
            dev->last_error = HAL_I2C_ERR_TIMEOUT;
            return false;
        }
        hal_time_delay_ms(1u);
    }

    uint8_t raw[8] = { 0u };
    st = hal_i2c_read_regs(dev->bus, dev->addr, BME280_REG_PRESS_MSB, raw, sizeof raw);
    if (st != HAL_I2C_OK) {
        dev->last_error = st;
        return false;
    }

    /* Тиск і температура — двадцятибітні, вологість — шістнадцятибітна. */
    const int32_t adc_p = (int32_t)(((uint32_t)raw[0] << 12) |
                                    ((uint32_t)raw[1] << 4) |
                                    ((uint32_t)raw[2] >> 4));
    const int32_t adc_t = (int32_t)(((uint32_t)raw[3] << 12) |
                                    ((uint32_t)raw[4] << 4) |
                                    ((uint32_t)raw[5] >> 4));
    const int32_t adc_h = (int32_t)(((uint32_t)raw[6] << 8) | (uint32_t)raw[7]);

    /* 0x80000 у сирому полі означає «вимкнений канал»: давач такий вимір
     * не робив, і видавати його за нуль градусів було б брехнею. */
    if (adc_t == 0x80000) {
        dev->last_error = HAL_I2C_ERR_BUS;
        return false;
    }

    const int32_t  t_hundredths = compensate_temperature(dev, adc_t);
    const uint32_t p_q24_8      = compensate_pressure(dev, adc_p);
    const uint32_t h_q22_10     = compensate_humidity(dev, adc_h);

    out_readings->temperature_c = (float)t_hundredths / 100.0f;
    out_readings->pressure_hpa  = (float)p_q24_8 / 25600.0f; /* Па/256 → гПа */
    out_readings->humidity_rh   = (float)h_q22_10 / 1024.0f;

    dev->last_error = HAL_I2C_OK;
    return true;
}

hal_i2c_status_t bsp_bme280_last_error(const bsp_bme280_t *dev)
{
    return handle_is_live(dev) ? dev->last_error : HAL_I2C_ERR_ARG;
}
