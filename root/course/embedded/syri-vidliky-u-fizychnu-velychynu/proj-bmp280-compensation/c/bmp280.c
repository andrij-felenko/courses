#include "bmp280.h"

#include <string.h>

/* ---- Розпакування little-endian --------------------------------------- */

static uint16_t le_u16(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

/*
 * Знакові коефіцієнти складаємо спершу як беззнакові й аж тоді звужуємо:
 * зсув p[1] << 8 у знаковому int16_t на межі 0x8000 — це переповнення.
 */
static int16_t le_s16(const uint8_t *p)
{
    uint16_t raw = le_u16(p);
    return (raw < 0x8000u) ? (int16_t)raw : (int16_t)((int32_t)raw - 0x10000);
}

bmp280_status_t bmp280_parse_calibration(bmp280_calib_t *calib, const uint8_t *buf)
{
    uint8_t and_all = 0xFFu;
    uint8_t or_all  = 0x00u;
    size_t  i;

    if (calib == NULL || buf == NULL) {
        return BMP280_ERR_ARG;
    }

    /*
     * Мертва шина віддає суцільні 0x00 (лінія притиснута) або 0xFF
     * (лінія лише підтягнута). Обидва випадки — обрив, а не калібрування.
     */
    for (i = 0; i < BMP280_CALIB_LEN; ++i) {
        and_all &= buf[i];
        or_all  |= buf[i];
    }
    if (or_all == 0x00u || and_all == 0xFFu) {
        return BMP280_ERR_CALIB;
    }

    calib->dig_T1 = le_u16(buf +  0);
    calib->dig_T2 = le_s16(buf +  2);
    calib->dig_T3 = le_s16(buf +  4);
    calib->dig_P1 = le_u16(buf +  6);
    calib->dig_P2 = le_s16(buf +  8);
    calib->dig_P3 = le_s16(buf + 10);
    calib->dig_P4 = le_s16(buf + 12);
    calib->dig_P5 = le_s16(buf + 14);
    calib->dig_P6 = le_s16(buf + 16);
    calib->dig_P7 = le_s16(buf + 18);
    calib->dig_P8 = le_s16(buf + 20);
    calib->dig_P9 = le_s16(buf + 22);

    /* dig_T1 і dig_P1 — беззнакові масштаби, нуль там фізично неможливий. */
    if (calib->dig_T1 == 0u || calib->dig_P1 == 0u) {
        return BMP280_ERR_CALIB;
    }
    return BMP280_OK;
}

/* MSB<<12 | LSB<<4 | XLSB>>4 — молодші 4 біти XLSB відкидаємо. */
static int32_t unpack20(const uint8_t *p)
{
    uint32_t raw = ((uint32_t)p[0] << 12) |
                   ((uint32_t)p[1] <<  4) |
                   ((uint32_t)p[2] >>  4);
    return (int32_t)raw;
}

bmp280_status_t bmp280_unpack_frame(const uint8_t *frame, int32_t *adc_P, int32_t *adc_T)
{
    int32_t p, t;

    if (frame == NULL || adc_P == NULL || adc_T == NULL) {
        return BMP280_ERR_ARG;
    }

    p = unpack20(frame + 0); /* 0xF7..0xF9 — тиск */
    t = unpack20(frame + 3); /* 0xFA..0xFC — температура */

    /* Скидання лишає в обох полях 0x80000: даних ще немає. */
    if (p == BMP280_RAW_RESET || t == BMP280_RAW_RESET) {
        return BMP280_ERR_NO_DATA;
    }

    *adc_P = p;
    *adc_T = t;
    return BMP280_OK;
}

/* ---- Етап 1: термометрія ---------------------------------------------- */

int32_t bmp280_compensate_temperature(const bmp280_calib_t *calib,
                                      int32_t adc_T, int32_t *t_fine)
{
    int32_t var1, var2, diff, fine;

    /* Лінійна складова: (adc_T/8 - dig_T1*2) * dig_T2 / 2048. */
    var1 = (((adc_T >> 3) - ((int32_t)calib->dig_T1 << 1)) *
            (int32_t)calib->dig_T2) >> 11;

    /* Квадратична нелінійність кристала, зважена dig_T3. */
    diff = (adc_T >> 4) - (int32_t)calib->dig_T1;
    var2 = (((diff * diff) >> 12) * (int32_t)calib->dig_T3) >> 14;

    fine = var1 + var2;
    if (t_fine != NULL) {
        *t_fine = fine;
    }

    /* Соті градуса: t_fine * 5 / 256 з округленням до найближчого. */
    return (fine * 5 + 128) >> 8;
}

/* ---- Етап 2: барометрія в 64 бітах ------------------------------------ */

bmp280_status_t bmp280_compensate_pressure_q24(const bmp280_calib_t *calib,
                                               int32_t t_fine, int32_t adc_P,
                                               uint32_t *out_q24_8)
{
    int64_t var1, var2, p;

    if (calib == NULL || out_q24_8 == NULL) {
        return BMP280_ERR_ARG;
    }

    var1 = (int64_t)t_fine - 128000;

    /* Поліном нульового зміщення: тепловий дрейф нуля тензомоста. */
    var2 = var1 * var1 * (int64_t)calib->dig_P6;
    var2 = var2 + ((var1 * (int64_t)calib->dig_P5) << 17);
    var2 = var2 + ((int64_t)calib->dig_P4 << 35);

    /* Поліном чутливості: зміна крутизни характеристики від температури. */
    var1 = ((var1 * var1 * (int64_t)calib->dig_P3) >> 8) +
           ((var1 * (int64_t)calib->dig_P2) << 12);
    /* Зсув знакового вправо тут арифметичний — так задумано в datasheet. */
    var1 = (((int64_t)1 << 47) + var1) * (int64_t)calib->dig_P1 >> 33;

    if (var1 == 0) {
        /* Побите калібрування вироджує масштаб у нуль. */
        return BMP280_ERR_DEGEN;
    }

    /* Нормалізація відліку різницею з максимумом 20-бітної шкали. */
    p = 1048576 - (int64_t)adc_P;
    p = (((p << 31) - var2) * 3125) / var1;

    /* Корекція нелінійності третього порядку (dig_P9, dig_P8, dig_P7). */
    var1 = ((int64_t)calib->dig_P9 * (p >> 13) * (p >> 13)) >> 25;
    var2 = ((int64_t)calib->dig_P8 * p) >> 19;
    p = ((p + var1 + var2) >> 8) + ((int64_t)calib->dig_P7 << 4);

    /* Q24.8 не має знака: від'ємний тиск означає зіпсовані коефіцієнти. */
    if (p < 0) {
        return BMP280_ERR_DEGEN;
    }

    *out_q24_8 = (uint32_t)p;
    return BMP280_OK;
}

/* ---- Час перетворення -------------------------------------------------- */

uint32_t bmp280_measure_time_ms(bmp280_os_t os_temp, bmp280_os_t os_press)
{
    static const uint32_t mult[6] = { 0u, 1u, 2u, 4u, 8u, 16u };
    uint32_t tenths = 13u; /* 1.25 мс на запуск циклу, округлено вгору */

    if ((unsigned)os_temp > 5u || (unsigned)os_press > 5u) {
        return 0u;
    }

    tenths += 23u * mult[os_temp];
    if (os_press != BMP280_OS_SKIP) {
        tenths += 23u * mult[os_press] + 6u; /* +0.575 мс на запис результату */
    }
    return (tenths + 9u) / 10u; /* десяті → мілісекунди, вгору */
}

/* ---- Обгортки над шиною ------------------------------------------------ */

static bmp280_status_t bus_read(const bmp280_bus_t *bus, uint8_t reg,
                                uint8_t *dst, size_t len)
{
    if (bus->read == NULL) {
        return BMP280_ERR_ARG;
    }
    return (bus->read(bus->ctx, reg, dst, len) == 0) ? BMP280_OK : BMP280_ERR_BUS;
}

static bmp280_status_t bus_write(const bmp280_bus_t *bus, uint8_t reg, uint8_t value)
{
    if (bus->write == NULL) {
        return BMP280_ERR_ARG;
    }
    return (bus->write(bus->ctx, reg, value) == 0) ? BMP280_OK : BMP280_ERR_BUS;
}

static void bus_delay(const bmp280_bus_t *bus, uint32_t ms)
{
    if (bus->delay_ms != NULL) {
        bus->delay_ms(bus->ctx, ms);
    }
}

/* ---- Ініціалізація ----------------------------------------------------- */

bmp280_status_t bmp280_init(bmp280_dev_t *dev, const bmp280_bus_t *bus,
                            const bmp280_config_t *cfg)
{
    uint8_t calib_buf[BMP280_CALIB_LEN];
    uint8_t id = 0u, status = 0u, ctrl, conf;
    unsigned attempt;
    bmp280_status_t rc;

    if (dev == NULL || bus == NULL || cfg == NULL) {
        return BMP280_ERR_ARG;
    }
    if ((unsigned)cfg->os_temp > 5u || (unsigned)cfg->os_press > 5u ||
        (unsigned)cfg->filter > 4u || (unsigned)cfg->standby > 7u) {
        return BMP280_ERR_ARG;
    }

    memset(dev, 0, sizeof(*dev));
    dev->bus = *bus;
    dev->cfg = *cfg;

    rc = bus_read(&dev->bus, BMP280_REG_ID, &id, 1u);
    if (rc != BMP280_OK) {
        return rc;
    }
    if (id != BMP280_CHIP_ID) {
        return BMP280_ERR_CHIP_ID;
    }

    rc = bus_write(&dev->bus, BMP280_REG_RESET, BMP280_RESET_KEY);
    if (rc != BMP280_OK) {
        return rc;
    }
    bus_delay(&dev->bus, 3u); /* старт після м'якого скидання */

    /*
     * Поки im_update = 1, тіньові регістри ще заповнюються з OTP —
     * прочитане в цей момент калібрування буде наполовину старим.
     */
    for (attempt = 0u; attempt < 20u; ++attempt) {
        rc = bus_read(&dev->bus, BMP280_REG_STATUS, &status, 1u);
        if (rc != BMP280_OK) {
            return rc;
        }
        if ((status & BMP280_STATUS_IM_UPDATE) == 0u) {
            break;
        }
        bus_delay(&dev->bus, 2u);
    }
    if (attempt == 20u) {
        return BMP280_ERR_TIMEOUT;
    }

    /* Усі 24 байти — однією пакетною транзакцією. */
    rc = bus_read(&dev->bus, BMP280_REG_CALIB_START, calib_buf, BMP280_CALIB_LEN);
    if (rc != BMP280_OK) {
        return rc;
    }
    rc = bmp280_parse_calibration(&dev->calib, calib_buf);
    if (rc != BMP280_OK) {
        return rc;
    }

    /* config пишемо, поки датчик у сні: у режимі normal запис ігнорується. */
    conf = (uint8_t)(((unsigned)cfg->standby << 5) | ((unsigned)cfg->filter << 2));
    rc = bus_write(&dev->bus, BMP280_REG_CONFIG, conf);
    if (rc != BMP280_OK) {
        return rc;
    }

    ctrl = (uint8_t)(((unsigned)cfg->os_temp << 5) | ((unsigned)cfg->os_press << 2));
    dev->ctrl_base = ctrl;
    rc = bus_write(&dev->bus, BMP280_REG_CTRL_MEAS,
                   (uint8_t)(ctrl | ((unsigned)cfg->mode & 3u)));
    if (rc != BMP280_OK) {
        return rc;
    }

    dev->ready = true;
    return BMP280_OK;
}

/* ---- Одне вимірювання -------------------------------------------------- */

bmp280_status_t bmp280_read(bmp280_dev_t *dev, bmp280_meas_t *out)
{
    uint8_t frame[BMP280_FRAME_LEN];
    uint8_t status = 0u;
    int32_t adc_P = 0, adc_T = 0;
    unsigned attempt;
    bmp280_status_t rc;

    if (dev == NULL || out == NULL) {
        return BMP280_ERR_ARG;
    }
    if (!dev->ready) {
        return BMP280_ERR_CALIB;
    }

    if (dev->cfg.mode == BMP280_MODE_FORCED) {
        /* Forced: кожен цикл запускається окремо, далі чип сам засинає. */
        rc = bus_write(&dev->bus, BMP280_REG_CTRL_MEAS,
                       (uint8_t)(dev->ctrl_base | BMP280_MODE_FORCED));
        if (rc != BMP280_OK) {
            return rc;
        }
    }
    bus_delay(&dev->bus, bmp280_measure_time_ms(dev->cfg.os_temp, dev->cfg.os_press));

    /*
     * Кадр беремо лише коли АЦП стоїть і тіньові регістри не переписуються:
     * інакше в шести байтах опиниться суміш двох сусідніх вимірювань.
     */
    for (attempt = 0u; attempt < 32u; ++attempt) {
        rc = bus_read(&dev->bus, BMP280_REG_STATUS, &status, 1u);
        if (rc != BMP280_OK) {
            return rc;
        }
        if ((status & (BMP280_STATUS_MEASURING | BMP280_STATUS_IM_UPDATE)) == 0u) {
            break;
        }
        bus_delay(&dev->bus, 1u);
    }
    if (attempt == 32u) {
        return BMP280_ERR_TIMEOUT;
    }

    rc = bus_read(&dev->bus, BMP280_REG_DATA_START, frame, BMP280_FRAME_LEN);
    if (rc != BMP280_OK) {
        return rc;
    }
    rc = bmp280_unpack_frame(frame, &adc_P, &adc_T);
    if (rc != BMP280_OK) {
        return rc;
    }

    /* Порядок обов'язковий: тиск компенсується вже відомою t_fine. */
    out->temperature_c100 = bmp280_compensate_temperature(&dev->calib, adc_T, &dev->t_fine);
    rc = bmp280_compensate_pressure_q24(&dev->calib, dev->t_fine, adc_P,
                                        &out->pressure_q24_8);
    if (rc != BMP280_OK) {
        return rc;
    }

    out->t_fine = dev->t_fine;
    return BMP280_OK;
}
