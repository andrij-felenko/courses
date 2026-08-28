#include <stdint.h>
#include <stdbool.h>

/* Адреси системної пам'яті STM32G4 / STM32L4 */
#define ADDR_VREFINT_CAL  ((const volatile uint16_t*)0x1FFF75AAUL)
#define ADDR_TS_CAL1      ((const volatile uint16_t*)0x1FFF75A8UL)
#define ADDR_TS_CAL2      ((const volatile uint16_t*)0x1FFF75CAUL)

typedef struct {
    uint32_t vdda_mv;           /* Напруга живлення, мВ */
    int32_t  temperature_degc;  /* Температура кристала, 0.1 °C */
    uint32_t vbat_mv;           /* Напруга батареї, мВ */
} McuPowerMetrics;

/**
 * @brief Розрахунок фізичних параметрів за сирими відліками АЦП
 * @param raw_vrefint Сирий код каналу VREFINT
 * @param raw_temp    Сирий код каналу датчика температури
 * @param raw_vbat    Сирий код каналу VBAT
 */
McuPowerMetrics mcu_calculate_metrics(uint16_t raw_vrefint,
                                      uint16_t raw_temp,
                                      uint16_t raw_vbat) {
    McuPowerMetrics res;
    if (raw_vrefint == 0) {
        res.vdda_mv = 0;
        res.temperature_degc = 0;
        res.vbat_mv = 0;
        return res;
    }

    uint16_t vref_cal = *ADDR_VREFINT_CAL;
    uint16_t ts_cal1  = *ADDR_TS_CAL1;
    uint16_t ts_cal2  = *ADDR_TS_CAL2;

    /* Захист від пошкодженого або некаліброваного ROM */
    if (vref_cal < 1000 || vref_cal > 2500) vref_cal = 1650;
    if (ts_cal2 <= ts_cal1) { ts_cal1 = 1035; ts_cal2 = 1380; }

    /* 1. Розрахунок VDDA: 3000 мВ * VREFINT_CAL / Raw_VREFINT */
    uint32_t vdda = ((uint32_t)3000 * vref_cal + (raw_vrefint / 2)) / raw_vrefint;
    res.vdda_mv = vdda;

    /* 2. Нормалізація термодатчика до 3.0 В */
    uint32_t ts_norm = ((uint32_t)raw_temp * vref_cal + (raw_vrefint / 2)) / raw_vrefint;

    /* 3. Інтерполяція температури: (130°C - 30°C) * (TS_norm - CAL1) / (CAL2 - CAL1) + 30°C */
    int32_t cal_delta = (int32_t)ts_cal2 - (int32_t)ts_cal1;
    int32_t temp_01c = ((int32_t)(ts_norm - ts_cal1) * 1000) / cal_delta + 300;
    res.temperature_degc = temp_01c;

    /* 4. Напруга батареї з урахуванням дільника 1/3 */
    uint32_t vbat_channel_mv = (vdda * (uint32_t)raw_vbat + 2047) / 4095;
    res.vbat_mv = vbat_channel_mv * 3;

    return res;
}
