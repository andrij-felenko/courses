// climate_engine.h / climate_engine.c
// Вбудований модуль захисту оболонки та розрахунку точки роси (C99)

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    float internal_temp_c;      // Температура повітря всередині (°C)
    float internal_humidity_rh; // Відносна вологість (0.0 - 100.0 %)
    float internal_pressure_kpa;// Внутрішній абсолютний тиск (кПа)
    float chassis_temp_c;       // Температура металевої стінки корпусу (°C)
    float ambient_pressure_kpa; // Зовнішній барометричний тиск (кПа)
} enclosure_telemetry_t;

typedef enum {
    ENV_FLAG_NORMAL           = 0,
    ENV_FLAG_CONDENSATION_RISK= (1 << 0), // Ризик випадання конденсату на стінки
    ENV_FLAG_MEMBRANE_BLOCKED = (1 << 1), // Забиття або обмерзання ePTFE клапана
    ENV_FLAG_SEAL_FAILURE     = (1 << 2), // Різкий прорив ущільнювача
    ENV_FLAG_THERMAL_OVERHEAT = (1 << 3)  // Перегрів внутрішнього об'єму
} enclosure_status_flags_t;

typedef enum {
    POWER_LIMIT_100 = 0, // Повна продуктивність
    POWER_LIMIT_75,      // Тротлінг 75% частоти
    POWER_LIMIT_50,      // Тротлінг 50% частоти, вимкнення підсвічування
    POWER_LIMIT_SAFE     // Аварійний режим (мінімальне енергоспоживання)
} power_limit_level_t;

typedef struct {
    float dew_point_c;
    float dew_point_margin_c;
    float delta_pressure_kpa;
    enclosure_status_flags_t status_flags;
    power_limit_level_t power_level;
} enclosure_diagnosis_t;

// Обчислення точки роси за формулою Магнуса-Тетенса
static float calc_dew_point_c(float temp_c, float rh) {
    if (rh < 0.1f) rh = 0.1f;
    if (rh > 100.0f) rh = 100.0f;
    const float a = 17.27f;
    const float b = 237.7f;
    float alpha = (a * temp_c) / (b + temp_c) + logf(rh / 100.0f);
    return (b * alpha) / (a - alpha);
}

// Головний автомат оцінки стану оболонки
enclosure_diagnosis_t evaluate_enclosure_climate(const enclosure_telemetry_t *t, float prev_p_kpa, float dt_sec) {
    enclosure_diagnosis_t diag;
    diag.status_flags = ENV_FLAG_NORMAL;
    diag.power_level = POWER_LIMIT_100;

    // 1. Точка роси та запас до конденсації на холодних стінках
    diag.dew_point_c = calc_dew_point_c(t->internal_temp_c, t->internal_humidity_rh);
    diag.dew_point_margin_c = t->chassis_temp_c - diag.dew_point_c;
    if (diag.dew_point_margin_c < 3.0f) {
        diag.status_flags |= ENV_FLAG_CONDENSATION_RISK;
    }

    // 2. Перепад тиску та діагностика мембрани
    diag.delta_pressure_kpa = t->internal_pressure_kpa - t->ambient_pressure_kpa;
    if (fabsf(diag.delta_pressure_kpa) > 5.0f) {
        diag.status_flags |= ENV_FLAG_MEMBRANE_BLOCKED;
    }

    // 3. Швидкість зміни тиску під час перепаду температури
    if (dt_sec > 0.01f) {
        float dp_dt = fabsf(t->internal_pressure_kpa - prev_p_kpa) / dt_sec;
        if (dp_dt > 0.25f) {
            diag.status_flags |= ENV_FLAG_SEAL_FAILURE;
        }
    }

    // 4. Тепловий стан і вибір рівня тротлінгу
    if (t->internal_temp_c > 85.0f || t->chassis_temp_c > 75.0f) {
        diag.status_flags |= ENV_FLAG_THERMAL_OVERHEAT;
        diag.power_level = POWER_LIMIT_SAFE;
    } else if (t->internal_temp_c > 75.0f || t->chassis_temp_c > 65.0f) {
        diag.power_level = POWER_LIMIT_50;
    } else if (t->internal_temp_c > 65.0f || t->chassis_temp_c > 55.0f) {
        diag.power_level = POWER_LIMIT_75;
    }

    return diag;
}
