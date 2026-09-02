/*
 * Перевірка драйвера на еталонному векторі Bosch і повний цикл читання
 * через імітований датчик на шині.
 */

#include "bmp280.h"

#include <stdio.h>
#include <string.h>

/* ---- Еталонний вектор -------------------------------------------------- */

/* Ті самі коефіцієнти, спаковані little-endian, як їх віддає OTP. */
static const uint8_t kCalibBytes[BMP280_CALIB_LEN] = {
    0x70, 0x6B, /* dig_T1 = 27504  */
    0x43, 0x67, /* dig_T2 = 26435  */
    0x18, 0xFC, /* dig_T3 = -1000  */
    0x7D, 0x8E, /* dig_P1 = 36477  */
    0x43, 0xD6, /* dig_P2 = -10685 */
    0xD0, 0x0B, /* dig_P3 = 3024   */
    0x27, 0x0B, /* dig_P4 = 2855   */
    0x8C, 0x00, /* dig_P5 = 140    */
    0xF9, 0xFF, /* dig_P6 = -7     */
    0x8C, 0x3C, /* dig_P7 = 15500  */
    0xF8, 0xC6, /* dig_P8 = -14600 */
    0x70, 0x17  /* dig_P9 = 6000   */
};

/* adc_P = 0x655AC = 415148, adc_T = 0x7EE90 = 519888 */
static const uint8_t kFrameBytes[BMP280_FRAME_LEN] = {
    0x65, 0x5A, 0xC0,
    0x7E, 0xE9, 0x00
};

#define REF_T_FINE     128422L
#define REF_TEMP_C100  2508L
#define REF_PRESSURE   100653uL

/* ---- Імітований датчик на шині ----------------------------------------- */

typedef struct {
    uint8_t  regs[256];
    unsigned busy_ticks; /* скільки ще звертань триватиме перетворення */
    bool     im_update;
} fake_sensor_t;

static void fake_reset(fake_sensor_t *s)
{
    memset(s->regs, 0, sizeof(s->regs));
    s->regs[BMP280_REG_ID] = BMP280_CHIP_ID;

    memcpy(&s->regs[BMP280_REG_CALIB_START], kCalibBytes, BMP280_CALIB_LEN);

    /* Після скидання дані ще порожні: 0x80000 в обох полях. */
    s->regs[BMP280_REG_DATA_START + 0] = 0x80u;
    s->regs[BMP280_REG_DATA_START + 3] = 0x80u;

    s->busy_ticks = 0u;
    s->im_update  = true; /* перше читання застає копіювання OTP */
}

static int fake_read(void *ctx, uint8_t reg, uint8_t *dst, size_t len)
{
    fake_sensor_t *s = (fake_sensor_t *)ctx;

    if ((size_t)reg + len > sizeof(s->regs)) {
        return -1; /* вихід за карту — так само як NACK на шині */
    }

    if (reg == BMP280_REG_STATUS) {
        uint8_t st = 0u;
        if (s->busy_ticks > 0u) {
            st |= BMP280_STATUS_MEASURING;
            s->busy_ticks--;
        }
        if (s->im_update) {
            st |= BMP280_STATUS_IM_UPDATE;
            s->im_update = false;
        }
        s->regs[BMP280_REG_STATUS] = st;
    }

    memcpy(dst, &s->regs[reg], len);
    return 0;
}

static int fake_write(void *ctx, uint8_t reg, uint8_t value)
{
    fake_sensor_t *s = (fake_sensor_t *)ctx;

    if (reg == BMP280_REG_RESET) {
        if (value != BMP280_RESET_KEY) {
            return -1; /* чужий ключ датчик просто ігнорує */
        }
        fake_reset(s);
        return 0;
    }

    s->regs[reg] = value;

    if (reg == BMP280_REG_CTRL_MEAS && (value & 3u) != BMP280_MODE_SLEEP) {
        /* Запуск перетворення: за два опитування статусу з'явиться кадр. */
        s->busy_ticks = 2u;
        memcpy(&s->regs[BMP280_REG_DATA_START], kFrameBytes, BMP280_FRAME_LEN);
    }
    return 0;
}

static void fake_delay(void *ctx, uint32_t ms)
{
    fake_sensor_t *s = (fake_sensor_t *)ctx;

    /* Час на хості не йде — вважаємо, що мілісекунда з'їдає один такт АЦП. */
    if (ms >= s->busy_ticks) {
        s->busy_ticks = 0u;
    } else {
        s->busy_ticks -= ms;
    }
}

/* ---- Перевірки ---------------------------------------------------------- */

static int check_reference_vector(void)
{
    bmp280_calib_t calib;
    int32_t  adc_P = 0, adc_T = 0, t_fine = 0, temp;
    uint32_t q24 = 0u;
    int failures = 0;

    if (bmp280_parse_calibration(&calib, kCalibBytes) != BMP280_OK) {
        printf("ПОМИЛКА: калібрування не розібралося\n");
        return 1;
    }
    if (calib.dig_T1 != 27504u || calib.dig_T2 != 26435 || calib.dig_T3 != -1000 ||
        calib.dig_P1 != 36477u || calib.dig_P2 != -10685 || calib.dig_P9 != 6000) {
        printf("ПОМИЛКА: коефіцієнти розібрані невірно\n");
        failures++;
    }

    if (bmp280_unpack_frame(kFrameBytes, &adc_P, &adc_T) != BMP280_OK) {
        printf("ПОМИЛКА: кадр не розпакувався\n");
        return failures + 1;
    }
    if (adc_P != 415148L || adc_T != 519888L) {
        printf("ПОМИЛКА: сирі відліки %ld / %ld замість 415148 / 519888\n",
               (long)adc_P, (long)adc_T);
        failures++;
    }

    temp = bmp280_compensate_temperature(&calib, adc_T, &t_fine);
    if (t_fine != REF_T_FINE || temp != REF_TEMP_C100) {
        printf("ПОМИЛКА: t_fine=%ld temp=%ld замість %ld / %ld\n",
               (long)t_fine, (long)temp, (long)REF_T_FINE, (long)REF_TEMP_C100);
        failures++;
    }

    if (bmp280_compensate_pressure_q24(&calib, t_fine, adc_P, &q24) != BMP280_OK) {
        printf("ПОМИЛКА: компенсація тиску відмовила\n");
        return failures + 1;
    }
    if ((q24 >> 8) != REF_PRESSURE) {
        printf("ПОМИЛКА: тиск %lu Па замість %lu\n",
               (unsigned long)(q24 >> 8), (unsigned long)REF_PRESSURE);
        failures++;
    }

    printf("Еталон: T = %ld.%02ld °C, t_fine = %ld, p = %lu.%02lu Па\n",
           (long)temp / 100, (long)temp % 100, (long)t_fine,
           (unsigned long)(q24 >> 8), (unsigned long)((q24 & 0xFFu) * 100u / 256u));
    return failures;
}

static int check_full_cycle(void)
{
    fake_sensor_t sensor;
    bmp280_dev_t  dev;
    bmp280_meas_t meas;
    bmp280_status_t rc;

    const bmp280_config_t cfg = {
        BMP280_OS_X2,      /* температура: ×2 вистачає для t_fine */
        BMP280_OS_X16,     /* тиск: максимальне усереднення, шум 0.16 Па */
        BMP280_FILTER_X4,  /* IIR ×4 проти протягів і струменів пропелерів */
        BMP280_SB_125,
        BMP280_MODE_NORMAL
    };

    const bmp280_bus_t bus = { fake_read, fake_write, fake_delay, &sensor };

    fake_reset(&sensor);

    rc = bmp280_init(&dev, &bus, &cfg);
    if (rc != BMP280_OK) {
        printf("ПОМИЛКА: ініціалізація повернула %d\n", (int)rc);
        return 1;
    }
    printf("Час перетворення: %lu мс\n",
           (unsigned long)bmp280_measure_time_ms(cfg.os_temp, cfg.os_press));

    rc = bmp280_read(&dev, &meas);
    if (rc != BMP280_OK) {
        printf("ПОМИЛКА: читання повернуло %d\n", (int)rc);
        return 1;
    }
    if (meas.temperature_c100 != REF_TEMP_C100 ||
        (meas.pressure_q24_8 >> 8) != REF_PRESSURE) {
        printf("ПОМИЛКА: повний цикл дав %ld / %lu\n",
               (long)meas.temperature_c100,
               (unsigned long)(meas.pressure_q24_8 >> 8));
        return 1;
    }

    printf("Повний цикл: T = %ld.%02ld °C, p = %lu Па\n",
           (long)meas.temperature_c100 / 100, (long)meas.temperature_c100 % 100,
           (unsigned long)(meas.pressure_q24_8 >> 8));
    return 0;
}

static int check_broken_calibration(void)
{
    bmp280_calib_t calib;
    uint8_t empty[BMP280_CALIB_LEN];

    memset(empty, 0xFF, sizeof(empty));
    if (bmp280_parse_calibration(&calib, empty) != BMP280_ERR_CALIB) {
        printf("ПОМИЛКА: обрив шини не розпізнано\n");
        return 1;
    }

    memset(empty, 0x00, sizeof(empty));
    if (bmp280_parse_calibration(&calib, empty) != BMP280_ERR_CALIB) {
        printf("ПОМИЛКА: нульове калібрування прийнято\n");
        return 1;
    }
    return 0;
}

int main(void)
{
    int failures = 0;

    failures += check_reference_vector();
    failures += check_full_cycle();
    failures += check_broken_calibration();

    if (failures != 0) {
        printf("Провалено перевірок: %d\n", failures);
        return 1;
    }
    printf("Драйвер збігається з еталоном біт-у-біт\n");
    return 0;
}
