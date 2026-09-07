#ifndef ADC_CALIB_H
#define ADC_CALIB_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Структура калібрувальних коефіцієнтів та стану АЦП.
 */
typedef struct {
    uint32_t nominal_max_code;   /* Номінальний максимальний код (4095 для 12-біт, 16777215 для 24-біт) */
    float nominal_vref_mv;       /* Номінальна напруга опорного джерела в мілівольтах */
    
    /* Поточні відліки фонового двохточкового калібрування */
    int32_t raw_zero_code;       /* Відлік каналу AGND (зсув нуля) */
    int32_t raw_vref_code;       /* Відлік каналу внутрішньої опорної напруги VREF */
    
    /* Температурний стан та коефіцієнти полінома 2-го порядку: V_corr = a0 + a1*(T-T0) + a2*(T-T0)^2 */
    float temp_t0;               /* Базова температура калібрування (°C), зазвичай 25.0 °C */
    float poly_a0;               /* Зсув нуля при T0 (мВ) */
    float poly_a1;               /* Лінійний температурний коефіцієнт (мВ/°C) */
    float poly_a2;               /* Квадратичний коефіцієнт кривизни (мВ/°C^2) */
    
    /* Експоненційний фільтр температури: T_filt = alpha * T_raw + (1 - alpha) * T_filt */
    float filtered_temp;         /* Поточна згладжена температура кристала (°C) */
    float temp_filter_alpha;     /* Ваговий коефіцієнт фільтра (0.01 .. 0.2) */
    bool temp_initialized;       /* Прапорець ініціалізації фільтра */
} adc_calib_t;

/**
 * Ініціалізація модуля калібрування.
 */
void adc_calib_init(adc_calib_t *calib, uint32_t max_code, float vref_mv, float t0, float a0, float a1, float a2, float alpha);

/**
 * Оновлення результатів фонового вимірювання нуля (AGND) та повної шкали (VREF).
 */
void adc_calib_update_references(adc_calib_t *calib, int32_t zero_code, int32_t vref_code);

/**
 * Оновлення поточної температури з експоненційною фільтрацією.
 */
void adc_calib_update_temperature(adc_calib_t *calib, float raw_temp_degc);

/**
 * Корекція сирого відліку АЦП: двохточкове калібрування + поліноміальна термокомпенсація.
 * Повертає скориговану напругу в мілівольтах.
 */
float adc_calib_process_sample(const adc_calib_t *calib, int32_t raw_code);

/**
 * Швидка цілочисельна корекція сирого відліку у форматі з фіксованою комою.
 * Повертає скоригований код від 0 до nominal_max_code.
 */
int32_t adc_calib_correct_code_fixed(const adc_calib_t *calib, int32_t raw_code);

#ifdef __cplusplus
}
#endif

#endif /* ADC_CALIB_H */
