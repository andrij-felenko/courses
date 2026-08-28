#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Апаратні адреси заводських калібрувальних значень для STM32G4
 */
#define STM32G4_VREFINT_CAL_ADDR   ((const volatile uint16_t*)0x1FFF75AAUL)
#define STM32G4_TS_CAL1_ADDR       ((const volatile uint16_t*)0x1FFF75A8UL)
#define STM32G4_TS_CAL2_ADDR       ((const volatile uint16_t*)0x1FFF75CAUL)

/**
 * @brief Структура параметрів калібрування АЦП
 */
typedef struct {
    uint16_t vrefint_cal;    /* Значення VREFINT_CAL при напрузі калібрування */
    uint16_t ts_cal1;        /* Значення TS_CAL1 при температурі T1 (30 °C) */
    uint16_t ts_cal2;        /* Значення TS_CAL2 при температурі T2 (110 або 130 °C) */
    uint16_t cal_vref_mv;    /* Еталонна напруга калібрування (типово 3000 мВ) */
    int16_t  ts_cal1_temp;   /* Температура калібрування точки 1 (°C) */
    int16_t  ts_cal2_temp;   /* Температура калібрування точки 2 (°C) */
    uint8_t  vbat_div;       /* Коефіцієнт дільника напруги батареї VBAT */
    bool     valid;          /* Прапорець достовірності даних у пам'яті */
} McuAdcCalibrationData;

static inline McuAdcCalibrationData mcu_adc_read_factory_cal(void) {
    McuAdcCalibrationData cal;
    cal.vrefint_cal  = *STM32G4_VREFINT_CAL_ADDR;
    cal.ts_cal1      = *STM32G4_TS_CAL1_ADDR;
    cal.ts_cal2      = *STM32G4_TS_CAL2_ADDR;
    cal.cal_vref_mv  = 3000U;
    cal.ts_cal1_temp = 30;
    cal.ts_cal2_temp = 130;
    cal.vbat_div     = 3U;

    // Перевірка цілісності: діапазон валідних значень для 12-бітного АЦП
    if ((cal.vrefint_cal > 1000 && cal.vrefint_cal < 2500) &&
        (cal.ts_cal1 > 500 && cal.ts_cal1 < 3000) &&
        (cal.ts_cal2 > cal.ts_cal1 && cal.ts_cal2 < 4095)) {
        cal.valid = true;
    } else {
        // Fallback константи при пошкодженій або незаписаній Flash
        cal.vrefint_cal = 1650;
        cal.ts_cal1     = 1035;
        cal.ts_cal2     = 1380;
        cal.valid       = false;
    }

    return cal;
}
