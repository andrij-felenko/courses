#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

// Конфігураційні параметри драйвера LVDT
typedef struct {
    uint32_t carrier_freq_hz;        // Частота сигналу збудження (Гц)
    uint16_t adc_samples_per_period; // Кількість відліків АЦП на період
    float    min_sum_threshold;      // Поріг суми напруг для виявлення обриву
    float    max_ratio_limit;        // Граничне допустиме ратіометричне значення
} lvdt_config_t;

// Структура калібрувальних коефіцієнтів
typedef struct {
    float zero_offset_ratio;         // Зсув електричного нуля (V_zero)
    float scale_factor_mm;           // Масштабний коефіцієнт (K_scale, мм)
    float poly_c0;                   // Поліноміальний коефіцієнт c0
    float poly_c1;                   // Поліноміальний коефіцієнт c1
    float poly_c2;                   // Поліноміальний коефіцієнт c2
    float poly_c3;                   // Поліноміальний коефіцієнт c3
} lvdt_calibration_t;

// Статуси виконання операцій драйвера
typedef enum {
    LVDT_OK = 0,
    LVDT_ERR_INVALID_PARAM,
    LVDT_ERR_EXCITATION_LOST,
    LVDT_ERR_WINDING_FAULT,
    LVDT_ERR_OUT_OF_RANGE
} lvdt_status_t;

// Дескриптор робочого стану LVDT
typedef struct {
    lvdt_config_t      config;
    lvdt_calibration_t calibration;
    lvdt_status_t      status_flags;
    float              last_raw_ratio;
    float              last_position_mm;
} lvdt_handle_t;

// Ініціалізація драйвера LVDT та зв'язування конфігурації
lvdt_status_t lvdt_init(lvdt_handle_t *handle, const lvdt_config_t *config, const lvdt_calibration_t *calib) {
    if (handle == NULL || config == NULL || calib == NULL) {
        return LVDT_ERR_INVALID_PARAM;
    }
    handle->config = *config;
    handle->calibration = *calib;
    handle->status_flags = LVDT_OK;
    handle->last_raw_ratio = 0.0f;
    handle->last_position_mm = 0.0f;
    return LVDT_OK;
}
