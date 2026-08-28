/* dcr_sense_math.h - Драйвер обробки сигналу DCR-сенсингу (C99) */
#ifndef DCR_SENSE_MATH_H
#define DCR_SENSE_MATH_H

#include <stdint.h>
#include <stdbool.h>

#define DCR_TCR_COPPER       0.00393f   /* Температурний коефіцієнт міді (+0.393 %/°C) */
#define DCR_ADC_VREF         3.300f     /* Опорна напруга АЦП (Вольти) */
#define DCR_ADC_RESOLUTION   4096.0f    /* Роздільність 12-бітного АЦП */

typedef struct {
    float dcr_25c_ohm;      /* Номінальний DCR котушки при 25 °C (Ом) */
    float amp_gain;         /* Коефіцієнт підсилення вхідного ОУ */
    int16_t adc_zero_offset;/* Калібрований зсув нуля АЦП (відліки) */
    float isat_threshold_a; /* Поріг початку насичення котушки (Ампери) */
    float sat_derate_coeff; /* Коефіцієнт корекції насичення */
} DcrCalibParams;

typedef struct {
    DcrCalibParams params;
    float current_temp_c;   /* Поточна виміряна температура дроселя (°C) */
    float effective_dcr;    /* Розрахований DCR(T) з урахуванням нагріву (Ом) */
    float last_current_a;   /* Останнє обчислене значення струму (А) */
} DcrChannel;

/* Ініціалізація структури каналу */
void Dcr_Init(DcrChannel *ch, const DcrCalibParams *params);

/* Калібрування апаратного зміщення нуля */
void Dcr_CalibrateZeroOffset(DcrChannel *ch, uint16_t raw_zero_adc);

/* Оновлення температури фази (викликається з фонового таску термоконтролю) */
void Dcr_UpdateTemperature(DcrChannel *ch, float temp_c);

/* Швидкий розрахунок миттєвого струму фази (викликається в перериванні АЦП) */
float Dcr_ProcessCurrentSample(DcrChannel *ch, uint16_t raw_adc);

#endif /* DCR_SENSE_MATH_H */
