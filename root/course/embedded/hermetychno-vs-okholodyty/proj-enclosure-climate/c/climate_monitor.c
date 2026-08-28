// climate_monitor.h / climate_monitor.c
// Модуль контролю мікроклімату герметичного корпусу (Embedded C99 / C11)

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define CLIMATE_HISTORY_SIZE       8
#define DEW_MARGIN_CRITICAL_C      3.0f
#define PRESSURE_LEAK_RATE_KPA_S   0.25f
#define MEMBRANE_CLOG_DP_KPA       5.0f

typedef enum {
    CLIMATE_STATUS_OK = 0,
    CLIMATE_WARN_CONDENSATION_RISK = (1 << 0),
    CLIMATE_WARN_MEMBRANE_CLOGGED  = (1 << 1),
    CLIMATE_ALERT_SEAL_BREACH      = (1 << 2),
    CLIMATE_ALERT_OVERHEAT         = (1 << 3)
} climate_status_flags_t;

typedef enum {
    THROTTLE_LEVEL_NONE = 0,
    THROTTLE_LEVEL_LIGHT,      // -25% тактової частоти
    THROTTLE_LEVEL_HEAVY,      // -50% тактової частоти, вимкнення радіомодулів
    THROTTLE_LEVEL_CRITICAL    // Екстрений перехід у сон (Sleep mode)
} thermal_throttle_level_t;

typedef struct {
    float temp_c;              // Температура внутрішнього повітря (°C)
    float humidity_rh;         // Відносна вологість (0.0 - 100.0 %)
    float pressure_kpa;        // Внутрішній абсолютний тиск (кПа)
    float wall_temp_c;         // Температура внутрішньої стінки корпусу (°C)
    float ext_pressure_kpa;    // Зовнішній барометричний тиск (кПа)
} climate_raw_sensors_t;

typedef struct {
    float dew_point_c;
    float dew_margin_c;
    float pressure_delta_kpa;
    float dp_dt_kpa_s;
    climate_status_flags_t flags;
    thermal_throttle_level_t throttle;
} climate_processed_state_t;

typedef struct {
    float pressure_history[CLIMATE_HISTORY_SIZE];
    uint32_t timestamp_history_ms[CLIMATE_HISTORY_SIZE];
    uint8_t history_idx;
    uint8_t history_count;
    climate_processed_state_t current_state;
} climate_monitor_ctx_t;

// Ініціалізація контексту
void climate_monitor_init(climate_monitor_ctx_t *ctx) {
    if (!ctx) return;
    ctx->history_idx = 0;
    ctx->history_count = 0;
    ctx->current_state.dew_point_c = 0.0f;
    ctx->current_state.dew_margin_c = 100.0f;
    ctx->current_state.pressure_delta_kpa = 0.0f;
    ctx->current_state.dp_dt_kpa_s = 0.0f;
    ctx->current_state.flags = CLIMATE_STATUS_OK;
    ctx->current_state.throttle = THROTTLE_LEVEL_NONE;
}

// Обчислення точки роси за формулою Магнуса
static float compute_dew_point(float t_c, float rh) {
    if (rh <= 0.01f) rh = 0.01f;
    if (rh > 100.0f) rh = 100.0f;
    const float a = 17.27f;
    const float b = 237.7f;
    float gamma = (a * t_c) / (b + t_c) + logf(rh / 100.0f);
    return (b * gamma) / (a - gamma);
}

// Періодична функція аналізу мікроклімату (викликається, наприклад, щосекунди)
void climate_monitor_update(climate_monitor_ctx_t *ctx,
                            const climate_raw_sensors_t *raw,
                            uint32_t now_ms) {
    if (!ctx || !raw) return;

    // 1. Розрахунок точки роси та запасу до конденсації
    float dew_point = compute_dew_point(raw->temp_c, raw->humidity_rh);
    float dew_margin = raw->wall_temp_c - dew_point;

    // 2. Розрахунок різниці внутрішнього та зовнішнього тиску
    float delta_p = raw->pressure_kpa - raw->ext_pressure_kpa;

    // 3. Обчислення швидкості зміни внутрішнього тиску dP/dt
    float dp_dt = 0.0f;
    if (ctx->history_count > 0) {
        uint8_t oldest_idx = (ctx->history_count < CLIMATE_HISTORY_SIZE) ? 0 : ctx->history_idx;
        float dt_sec = (float)(now_ms - ctx->timestamp_history_ms[oldest_idx]) / 1000.0f;
        if (dt_sec > 0.05f) {
            float dp = raw->pressure_kpa - ctx->pressure_history[oldest_idx];
            dp_dt = dp / dt_sec;
        }
    }

    // Оновлення кільцевого буфера тиску
    ctx->pressure_history[ctx->history_idx] = raw->pressure_kpa;
    ctx->timestamp_history_ms[ctx->history_idx] = now_ms;
    ctx->history_idx = (ctx->history_idx + 1) % CLIMATE_HISTORY_SIZE;
    if (ctx->history_count < CLIMATE_HISTORY_SIZE) ctx->history_count++;

    // 4. Формування прапорців стану
    climate_status_flags_t flags = CLIMATE_STATUS_OK;

    if (dew_margin < DEW_MARGIN_CRITICAL_C) {
        flags |= CLIMATE_WARN_CONDENSATION_RISK;
    }
    if (fabsf(delta_p) > MEMBRANE_CLOG_DP_KPA) {
        flags |= CLIMATE_WARN_MEMBRANE_CLOGGED;
    }
    if (fabsf(dp_dt) > PRESSURE_LEAK_RATE_KPA_S) {
        flags |= CLIMATE_ALERT_SEAL_BREACH;
    }
    if (raw->temp_c > 85.0f || raw->wall_temp_c > 75.0f) {
        flags |= CLIMATE_ALERT_OVERHEAT;
    }

    // 5. Автомат теплового тротлінгу
    thermal_throttle_level_t throttle = THROTTLE_LEVEL_NONE;
    if (raw->temp_c > 95.0f || raw->wall_temp_c > 85.0f) {
        throttle = THROTTLE_LEVEL_CRITICAL;
    } else if (raw->temp_c > 85.0f || raw->wall_temp_c > 75.0f) {
        throttle = THROTTLE_LEVEL_HEAVY;
    } else if (raw->temp_c > 75.0f || raw->wall_temp_c > 65.0f) {
        throttle = THROTTLE_LEVEL_LIGHT;
    }

    // Запис вихідного стану
    ctx->current_state.dew_point_c = dew_point;
    ctx->current_state.dew_margin_c = dew_margin;
    ctx->current_state.pressure_delta_kpa = delta_p;
    ctx->current_state.dp_dt_kpa_s = dp_dt;
    ctx->current_state.flags = flags;
    ctx->current_state.throttle = throttle;
}
