#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    ML_MODE_FRESH = 0,
    ML_MODE_EXTRAPOLATED,
    ML_MODE_FALLBACK_PID,
    ML_MODE_SAFE_STOP
} ml_control_mode_t;

typedef struct {
    uint64_t deadline_limit_us;
    uint64_t max_extrapolation_us;
    uint64_t fatal_timeout_us;
    float decay_lambda;
    ml_prediction_t last_valid_prediction;
    float last_derivative[ML_OUTPUT_DIM];
} deadline_watchdog_t;

void watchdog_init(deadline_watchdog_t *wd, uint64_t deadline_us, uint64_t max_extrap_us, uint64_t fatal_us, float lambda) {
    wd->deadline_limit_us = deadline_us;
    wd->max_extrapolation_us = max_extrap_us;
    wd->fatal_timeout_us = fatal_us;
    wd->decay_lambda = lambda;
    memset(&wd->last_valid_prediction, 0, sizeof(ml_prediction_t));
    memset(wd->last_derivative, 0, sizeof(wd->last_derivative));
}

ml_control_mode_t watchdog_evaluate(
    deadline_watchdog_t *wd,
    const ml_prediction_t *incoming_data,
    bool is_fresh,
    uint64_t current_time_us,
    float out_correction[ML_OUTPUT_DIM])
{
    if (is_fresh) {
        /* Оновлюємо похідну між попереднім і новим кадром для лінійної екстраполяції */
        if (wd->last_valid_prediction.timestamp_us > 0) {
            float dt_sec = (float)(incoming_data->timestamp_us - wd->last_valid_prediction.timestamp_us) * 1e-6f;
            if (dt_sec > 1e-4f) {
                for (int i = 0; i < ML_OUTPUT_DIM; ++i) {
                    wd->last_derivative[i] = (incoming_data->values[i] - wd->last_valid_prediction.values[i]) / dt_sec;
                }
            }
        }
        wd->last_valid_prediction = *incoming_data;
    }

    if (wd->last_valid_prediction.timestamp_us == 0) {
        /* Модель ще жодного разу не видала вихід: чистий Fallback */
        memset(out_correction, 0, sizeof(float) * ML_OUTPUT_DIM);
        return ML_MODE_FALLBACK_PID;
    }

    uint64_t age_us = current_time_us - wd->last_valid_prediction.timestamp_us;

    /* Режим 1: Свіжі дані в межах дедлайну */
    if (age_us <= wd->deadline_limit_us) {
        for (int i = 0; i < ML_OUTPUT_DIM; ++i) {
            out_correction[i] = wd->last_valid_prediction.values[i];
        }
        return ML_MODE_FRESH;
    }

    /* Режим 2: Пропуск дедлайну, але в межах допустимої екстраполяції */
    if (age_us <= wd->max_extrapolation_us) {
        float dt_extrap_sec = (float)(age_us - wd->deadline_limit_us) * 1e-6f;
        float decay = expf(-wd->decay_lambda * dt_extrap_sec);

        for (int i = 0; i < ML_OUTPUT_DIM; ++i) {
            /* Лінійна екстраполяція з експоненційним загасанням довіри */
            float extrapolated = wd->last_valid_prediction.values[i] + wd->last_derivative[i] * dt_extrap_sec;
            out_correction[i] = extrapolated * decay;
        }
        return ML_MODE_EXTRAPOLATED;
    }

    /* Режим 3: Глибоке запізнення, перехід на Fallback PID контролер */
    if (age_us <= wd->fatal_timeout_us) {
        memset(out_correction, 0, sizeof(float) * ML_OUTPUT_DIM);
        return ML_MODE_FALLBACK_PID;
    }

    /* Режим 4: Фатальний таймаут (зависання NPU/підсистеми): аварійна безпечна зупинка */
    memset(out_correction, 0, sizeof(float) * ML_OUTPUT_DIM);
    return ML_MODE_SAFE_STOP;
}
