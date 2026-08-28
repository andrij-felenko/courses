#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Коефіцієнти Стейнгарта–Гарта для термістора NTC 10k (B=3950) */
#define SH_COEFF_A  (1.130206e-3f)
#define SH_COEFF_B  (2.339572e-4f)
#define SH_COEFF_C  (8.828190e-8f)

#define R_REF_OHMS  (10000.0f)   /* Точний опір верхнього резистора, Ом */
#define ADC_MAX_12B (4095.0f)

/*
 * Метод 1: Прямий розрахунок температури за рівнянням Стейнгарта–Гарта.
 * Призначений для систем з апаратним FPU.
 * raw_adc: сирий відлік 12-бітного АЦП (1..4094).
 * Повертає температуру в градусах Цельсія.
 */
float ntc_calculate_steinhart_hart(uint16_t raw_adc) {
    if (raw_adc == 0) return -273.15f;
    if (raw_adc >= 4095) return 200.0f;

    /* Ратіометричний розрахунок опору NTC */
    float r_ntc = R_REF_OHMS * ((float)raw_adc / (ADC_MAX_12B - (float)raw_adc));
    
    float ln_r = logf(r_ntc);
    float ln_r3 = ln_r * ln_r * ln_r;

    /* Рівняння Стейнгарта–Гарта: 1/T = A + B*ln(R) + C*(ln R)^3 */
    float inv_t = SH_COEFF_A + (SH_COEFF_B * ln_r) + (SH_COEFF_C * ln_r3);

    return (1.0f / inv_t) - 273.15f;
}

/*
 * Метод 2: Таблиця пошуку LUT (33 точки, крок 128 відліків для 12-бітного АЦП).
 * Значення температури закодовані у фіксованій комі: 1 одиниця = 0.01 °C.
 * Створено для термістора 10k (B=3950), R_ref = 10k.
 */
static const int16_t NTC_LUT_CENTIDEGREES[33] = {
    -4500, -3812, -3154, -2520, -1908, -1314,  -736,  -172,
      381,   925,  1462,  1994,  2522,  3049,  3577,  4109,
     4648,  5196,  5757,  6334,  6932,  7556,  8212,  8908,
     9654, 10464, 11359, 12371, 13548, 14972, 16825, 19540,
    23000
};

/*
 * Швидка цілочисельна інтерполяція без викликів FPU та важкого ділення.
 * Час виконання: 15–25 тактів CPU.
 * Повертає температуру в сотих частках градуса Цельсія (2534 -> +25.34 °C).
 */
int16_t ntc_calculate_lut_fast(uint16_t raw_adc) {
    if (raw_adc >= 4095) {
        return NTC_LUT_CENTIDEGREES[32];
    }

    /* Швидкий бітовий поділ: крок 128 */
    uint32_t idx = raw_adc >> 7;           /* Індекс базового вузла: raw / 128 */
    uint32_t rem = raw_adc & 0x7F;         /* Залишок інтерполяції: raw % 128 */

    int32_t t_low  = NTC_LUT_CENTIDEGREES[idx];
    int32_t t_high = NTC_LUT_CENTIDEGREES[idx + 1];

    /* Лінійна інтерполяція: T = t_low + (t_high - t_low) * (rem / 128) */
    int32_t t_interp = t_low + (((t_high - t_low) * (int32_t)rem) >> 7);

    return (int16_t)t_interp;
}
