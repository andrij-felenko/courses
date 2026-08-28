#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Апаратні адреси системної Flash-пам'яті для родини STM32G4 / STM32L4 */
#define MCU_VREFINT_CAL_ADDR    ((const volatile uint16_t*)0x1FFF75AAUL)
#define MCU_TS_CAL1_ADDR        ((const volatile uint16_t*)0x1FFF75A8UL)
#define MCU_TS_CAL2_ADDR        ((const volatile uint16_t*)0x1FFF75CAUL)

#define MCU_CAL_VREF_MV         (3000U)  /* Напруга заводського стенду: 3.0 В */
#define MCU_TS_CAL1_TEMP_C      (30)     /* Температура точки 1: +30 °C */
#define MCU_TS_CAL2_TEMP_C      (130)    /* Температура точки 2: +130 °C */
#define MCU_VBAT_DIV_RATIO      (3U)     /* Апаратний дільник VBAT 1/3 */

/* Результати вимірювання внутрішніх джерел */
typedef struct {
    uint32_t vdda_mv;           /* Напруга живлення в мілівольтах */
    int32_t  temperature_degc;  /* Температура кристала в десятих частках °C (0.1 °C) */
    uint32_t vbat_mv;           /* Напруга батареї в мілівольтах */
    bool     valid;             /* Ознака валідності вимірювання */
} McuInternalMetrics;

/* Структура конфігурації та кешу калібрування */
typedef struct {
    uint16_t vrefint_cal;
    uint16_t ts_cal1;
    uint16_t ts_cal2;
    bool     cal_valid;
} McuAdcDriver;

/**
 * @brief Ініціалізація та читання заводських коефіцієнтів
 */
void mcu_adc_driver_init(McuAdcDriver *driver) {
    if (!driver) return;

    driver->vrefint_cal = *MCU_VREFINT_CAL_ADDR;
    driver->ts_cal1     = *MCU_TS_CAL1_ADDR;
    driver->ts_cal2     = *MCU_TS_CAL2_ADDR;

    /* Перевірка цілісності: чи значення не є затертими (0x0000 чи 0xFFFF) */
    if ((driver->vrefint_cal > 1000 && driver->vrefint_cal < 2500) &&
        (driver->ts_cal1 > 500 && driver->ts_cal1 < 3000) &&
        (driver->ts_cal2 > driver->ts_cal1 && driver->ts_cal2 < 4095)) {
        driver->cal_valid = true;
    } else {
        /* Запасні константи за даташитом при пошкодженні пам'яті */
        driver->vrefint_cal = 1650;  /* 1.212 В при 3.0 В на 12 бітах */
        driver->ts_cal1     = 1035;  /* Орієнтовний код для +30 °C */
        driver->ts_cal2     = 1380;  /* Орієнтовний код для +130 °C */
        driver->cal_valid   = false;
    }
}

/**
 * @brief Обчислення медіани з масиву 5 відліків для придушення викидів шуму
 */
static uint16_t filter_median5(uint16_t samples[5]) {
    uint16_t s[5];
    memcpy(s, samples, sizeof(s));
    for (int i = 0; i < 4; ++i) {
        for (int j = i + 1; j < 5; ++j) {
            if (s[i] > s[j]) {
                uint16_t tmp = s[i];
                s[i] = s[j];
                s[j] = tmp;
            }
        }
    }
    return s[2]; // Центральний елемент відсортованого масиву
}

/**
 * @brief Розрахунок фізичних параметрів за сирими відліками АЦП
 */
McuInternalMetrics mcu_adc_calculate_metrics(const McuAdcDriver *driver,
                                             uint16_t raw_vrefint,
                                             uint16_t raw_temp,
                                             uint16_t raw_vbat) {
    McuInternalMetrics m;
    m.valid = false;

    if (!driver || raw_vrefint == 0) {
        m.vdda_mv = 0;
        m.temperature_degc = 0;
        m.vbat_mv = 0;
        return m;
    }

    /* 1. Точне відновлення VDDA в мілівольтах */
    uint32_t vdda_calc = ((uint32_t)MCU_CAL_VREF_MV * driver->vrefint_cal + (raw_vrefint / 2U)) / raw_vrefint;
    m.vdda_mv = vdda_calc;

    /* 2. Нормалізація коду термодатчика до напруги 3.0 В */
    uint32_t ts_norm = ((uint32_t)raw_temp * driver->vrefint_cal + (raw_vrefint / 2U)) / raw_vrefint;

    /* 3. Лінійна інтерполяція температури кристала в десятих частках °C (0.1 °C) */
    int32_t delta_t_x10 = (MCU_TS_CAL2_TEMP_C - MCU_TS_CAL1_TEMP_C) * 10;
    int32_t cal_diff = (int32_t)driver->ts_cal2 - (int32_t)driver->ts_cal1;
    if (cal_diff != 0) {
        int32_t temp_x10 = ((int32_t)(ts_norm - driver->ts_cal1) * delta_t_x10 + (cal_diff / 2)) / cal_diff + 
                           (MCU_TS_CAL1_TEMP_C * 10);
        m.temperature_degc = temp_x10;
    } else {
        m.temperature_degc = 0;
    }

    /* 4. Розрахунок напруги батареї з урахуванням дільника 1/3 */
    uint32_t vbat_raw_mv = (vdda_calc * (uint32_t)raw_vbat + 2047U) / 4095U;
    m.vbat_mv = vbat_raw_mv * MCU_VBAT_DIV_RATIO;

    m.valid = true;
    return m;
}
