#include <stdbool.h>
#include <stdint.h>
#include <math.h>

// Типи підтримуваних платинових сенсорів
typedef enum {
    RTD_TYPE_PT100  = 0,
    RTD_TYPE_PT1000 = 1
} rtd_type_t;

// Статуси результату вимірювання
typedef enum {
    RTD_OK               =  0,
    RTD_ERR_OPEN_CIRCUIT = -1,  // Обрив лінії / сенсора (R > R_max)
    RTD_ERR_SHORT_CIRCUIT= -2,  // Коротке замикання (R < R_min)
    RTD_ERR_OUT_OF_RANGE = -3,  // Вихід за діапазон IEC 60751 (-200..+850 °C)
    RTD_ERR_INVALID_ARG  = -4
} rtd_status_t;

// Конфігурація аналогового тракту RTD
typedef struct {
    rtd_type_t type;         // Pt100 або Pt1000
    float      r_ref;        // Опір опорного резистора R_REF, Ом (наприклад, 4000.0f)
    uint32_t   adc_max_code; // Максимальний код повної шкали АЦП (2^23 - 1 для 24-біт уніполярного)
    float      gain;         // Коефіцієнт підсилення PGA (зазвичай 1, 2 або 4)
    float      r0_cal;       // Індивідуальне калібрування R0 сенсора (за замовчуванням 100.0f або 1000.0f)
} rtd_config_t;

// Коефіцієнти стандарту IEC 60751 (DIN EN 60751)
#define RTD_CVD_A  (3.90830e-3f)
#define RTD_CVD_B  (-5.77500e-7f)
#define RTD_CVD_C  (-4.18300e-12f)

// Межі опору для валідації справності (Pt100: -200 °C -> 18.5 Ω, +850 °C -> 390.5 Ω)
#define PT100_MIN_RESISTANCE  (15.0f)
#define PT100_MAX_RESISTANCE  (410.0f)

/**
 * @brief Обчислення температури за методом Каллендара-Ван Дюзена
 */
rtd_status_t rtd_resistance_to_temperature(float r_rtd, float r0, float *out_temp_c) {
    if (!out_temp_c || r0 <= 0.0f) {
        return RTD_ERR_INVALID_ARG;
    }

    // Перевірка фізичних меж опору платини за IEC 60751
    float r_norm = r_rtd / r0;
    if (r_norm < 0.18f || r_norm > 4.00f) {
        return RTD_ERR_OUT_OF_RANGE;
    }

    if (r_rtd >= r0) {
        // Діапазон T >= 0 °C: точний аналітичний розв'язок квадратного рівняння
        float discriminant = (RTD_CVD_A * RTD_CVD_A) - 4.0f * RTD_CVD_B * (1.0f - r_norm);
        if (discriminant < 0.0f) {
            return RTD_ERR_OUT_OF_RANGE;
        }
        *out_temp_c = (-RTD_CVD_A + sqrtf(discriminant)) / (2.0f * RTD_CVD_B);
        return RTD_OK;
    } else {
        // Діапазон T < 0 °C: 3 ітерації методом Ньютона-Рафсона для полінома 4-го порядку
        float t = (r_norm - 1.0f) / RTD_CVD_A; // Початкове лінійне наближення
        
        for (int i = 0; i < 4; ++i) {
            float t2 = t * t;
            float t3 = t2 * t;
            float t4 = t3 * t;
            
            // f(t) = R0 * (1 + A*t + B*t^2 - 100*C*t^3 + C*t^4) - R
            float f = r0 * (1.0f + RTD_CVD_A * t + RTD_CVD_B * t2 - 100.0f * RTD_CVD_C * t3 + RTD_CVD_C * t4) - r_rtd;
            
            // f'(t) = R0 * (A + 2*B*t - 300*C*t^2 + 4*C*t^3)
            float f_prime = r0 * (RTD_CVD_A + 2.0f * RTD_CVD_B * t - 300.0f * RTD_CVD_C * t2 + 4.0f * RTD_CVD_C * t3);
            
            if (fabsf(f_prime) < 1e-7f) {
                break;
            }
            
            float delta = f / f_prime;
            t -= delta;
            
            if (fabsf(delta) < 1e-4f) { // Точність 0.0001 °C досягнута
                break;
            }
        }
        
        *out_temp_c = t;
        return RTD_OK;
    }
}

/**
 * @brief Повний конвеєр: перетворення коду АЦП в опір та температуру з перевіркою аварій
 */
rtd_status_t rtd_process_adc_reading(const rtd_config_t *cfg, int32_t raw_adc_code, 
                                     float *out_resistance, float *out_temp_c) {
    if (!cfg || !out_resistance || !out_temp_c || cfg->adc_max_code == 0 || cfg->gain <= 0.0f) {
        return RTD_ERR_INVALID_ARG;
    }

    // Розрахунок опору сенсора за раціометричною формулою
    float r_measured = ((float)raw_adc_code / (float)cfg->adc_max_code) * (cfg->r_ref / cfg->gain);
    *out_resistance = r_measured;

    // Масштабування діапазону залежно від номіналу
    float scale = (cfg->type == RTD_TYPE_PT1000) ? 10.0f : 1.0f;
    float min_r = PT100_MIN_RESISTANCE * scale;
    float max_r = PT100_MAX_RESISTANCE * scale;

    if (r_measured < min_r) {
        return RTD_ERR_SHORT_CIRCUIT;
    }
    if (r_measured > max_r) {
        return RTD_ERR_OPEN_CIRCUIT;
    }

    float r0 = (cfg->r0_cal > 0.0f) ? cfg->r0_cal : ((cfg->type == RTD_TYPE_PT1000) ? 1000.0f : 100.0f);
    return rtd_resistance_to_temperature(r_measured, r0, out_temp_c);
}
