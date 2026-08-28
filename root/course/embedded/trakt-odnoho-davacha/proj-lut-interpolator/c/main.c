#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define NTC_LUT_SIZE       33
#define NTC_ADC_STEP_SHIFT 7    /* 1 << 7 = 128 відліків */
#define NTC_ADC_STEP_MASK  0x7F /* 127 */
#define NTC_Q16_SHIFT      16
#define NTC_Q16_HALF       (1 << 15)

/* Статуси діагностики апаратного каналу */
typedef enum {
    NTC_STATUS_OK = 0,
    NTC_STATUS_OPEN_CIRCUIT,  /* Обрив лінії давача (код біля 0) */
    NTC_STATUS_SHORT_CIRCUIT  /* Замикання на живлення (код 4095) */
} NtcSensorStatus;

/* Таблиця попередньо обчислених температур у форматі Q16.16
   для 10k NTC (B=3950K) з підтяжкою 10k до VDDA, 12-бітний АЦП. */
static const int32_t ntc_lut_q16[NTC_LUT_SIZE] = {
    -2621440, /* Код    0: -40.00 °C (обрив / нижній упор) */
    -2097152, /* Код  128: -32.00 °C */
    -1638400, /* Код  256: -25.00 °C */
    -1245184, /* Код  384: -19.00 °C */
     -917504, /* Код  512: -14.00 °C */
     -629145, /* Код  640:  -9.60 °C */
     -367001, /* Код  768:  -5.60 °C */
     -131072, /* Код  896:  -2.00 °C */
       85196, /* Код 1024:  +1.30 °C */
      288358, /* Код 1152:  +4.40 °C */
      484966, /* Код 1280:  +7.40 °C */
      675020, /* Код 1408: +10.30 °C */
      865075, /* Код 1536: +13.20 °C */
     1055129, /* Код 1664: +16.10 °C */
     1245184, /* Код 1792: +19.00 °C */
     1441792, /* Код 1920: +22.00 °C */
     1638400, /* Код 2048: +25.00 °C (номінальна точка) */
     1841561, /* Код 2176: +28.10 °C */
     2051276, /* Код 2304: +31.30 °C */
     2274099, /* Код 2432: +34.70 °C */
     2510028, /* Код 2560: +38.30 °C */
     2765619, /* Код 2688: +42.20 °C */
     3047424, /* Код 2816: +46.50 °C */
     3361996, /* Код 2944: +51.30 °C */
     3722444, /* Код 3072: +56.80 °C */
     4141875, /* Код 3200: +63.20 °C */
     4646502, /* Код 3328: +70.90 °C */
     5269094, /* Код 3456: +80.40 °C */
     6068633, /* Код 3584: +92.60 °C */
     7143424, /* Код 3712: +109.00 °C */
     8650752, /* Код 3840: +132.00 °C */
    10813440, /* Код 3968: +165.00 °C */
    13107200  /* Код 4095: +200.00 °C (замикання / верхній упор) */
};

/**
 * @brief Кусково-лінійна інтерполяція температури за кодом АЦП.
 * @param adc_raw Сирий відлік 12-бітного АЦП [0..4095].
 * @param out_temp_c_x100 Вказівник для запису результату в сотих частках °C (наприклад 2534 = 25.34 °C).
 * @return Статус перетворення NtcSensorStatus.
 */
NtcSensorStatus ntc_interpolate_celsius(uint16_t adc_raw, int32_t *out_temp_c_x100)
{
    if (out_temp_c_x100 == NULL) {
        return NTC_STATUS_OPEN_CIRCUIT;
    }

    /* Діагностика крайніх аварійних станів шлейфу давача */
    if (adc_raw < 30) {
        *out_temp_c_x100 = -4000;
        return NTC_STATUS_OPEN_CIRCUIT;
    }
    if (adc_raw >= 4080) {
        *out_temp_c_x100 = 15000;
        return NTC_STATUS_SHORT_CIRCUIT;
    }

    /* Затискання в межі розрядності */
    if (adc_raw > 4095) {
        adc_raw = 4095;
    }

    /* Обчислення базового індексу та залишку без ділення */
    uint32_t idx = adc_raw >> NTC_ADC_STEP_SHIFT;
    uint32_t rem = adc_raw & NTC_ADC_STEP_MASK;

    if (idx >= (NTC_LUT_SIZE - 1)) {
        int32_t temp_q16 = ntc_lut_q16[NTC_LUT_SIZE - 1];
        *out_temp_c_x100 = (temp_q16 * 100 + NTC_Q16_HALF) >> NTC_Q16_SHIFT;
        return NTC_STATUS_OK;
    }

    int32_t t0 = ntc_lut_q16[idx];
    int32_t t1 = ntc_lut_q16[idx + 1];

    /* Лінійна інтерполяція у форматі Q16.16 */
    int32_t delta_t = t1 - t0;
    int32_t interpolated_q16 = t0 + ((delta_t * (int32_t)rem) >> NTC_ADC_STEP_SHIFT);

    /* Переведення в соті частки градуса з коректним симетричним округленням */
    *out_temp_c_x100 = (interpolated_q16 * 100 + NTC_Q16_HALF) >> NTC_Q16_SHIFT;
    return NTC_STATUS_OK;
}
