#include "stm32f4xx_hal.h"

extern ADC_HandleTypeDef hadc1;              // канал під AO налаштовує CubeMX

#define WINDOW_MS  50                        // тривалість вікна вимірювання
#define ADC_MAX    4095                      // стеля 12-бітного АЦП STM32

static uint16_t center  = 2048;              // де стоїть центр сигналу (для контролю країв)
static uint8_t  clipped = 0;                 // чи вперся сигнал у край АЦП цього вікна

// Одне вимірювання: розмах за вікно + перевірка, чи сигнал не б'ється об краї.
static uint16_t measure_amplitude(void) {
    uint16_t lo = ADC_MAX, hi = 0;
    uint32_t t0 = HAL_GetTick();
    while (HAL_GetTick() - t0 < WINDOW_MS) {
        HAL_ADC_Start(&hadc1);
        if (HAL_ADC_PollForConversion(&hadc1, 2) != HAL_OK) continue;
        uint16_t v = (uint16_t)HAL_ADC_GetValue(&hadc1);
        if (v > hi) hi = v;
        if (v < lo) lo = v;
    }
    HAL_ADC_Stop(&hadc1);
    center  = (hi + lo) / 2;                     // центр вікна = де сидить зсув
    clipped = (hi >= ADC_MAX) || (lo == 0);      // уперлися в стелю чи підлогу?
    return hi - lo;                              // розмах = груба гучність
}

// Перевести розмах у грубі рівні (пороги — під свій модуль, шкала 12-бітна).
static const char *loudness_level(uint16_t amp) {
    if (amp < 32)  return "тиша";
    if (amp < 120) return "чутно";
    if (amp < 480) return "голосно";
    return "дуже голосно";
}

void ky038_ao_loop(void) {                   // кличемо з головного while (1)
    uint16_t amp = measure_amplitude();
    printf("розмах = %4u  →  %s", amp, loudness_level(amp));
    if (clipped)                             // сигнал уперся в край — розмаху не вір
        printf("  [!] обрізання: центр=%u, підправ гвинтик до середини", center);
    printf("\r\n");
}
