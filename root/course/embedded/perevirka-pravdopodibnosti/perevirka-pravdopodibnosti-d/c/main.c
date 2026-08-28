#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// Діагностичні прапорці відмов вимірювального каналу
#define SENSOR_FAULT_NONE           0x0000U
#define SENSOR_FAULT_NAN_INF        0x0001U
#define SENSOR_FAULT_ELECTRICAL_LOW 0x0002U // Обрив лінії / КЗ на GND
#define SENSOR_FAULT_ELECTRICAL_HI  0x0004U // КЗ на шину живлення VCC
#define SENSOR_FAULT_STATIC_RANGE   0x0008U // Вихід за фізичні межі величини
#define SENSOR_FAULT_SLEW_RATE_UP   0x0010U // Перевищення темпу наростання
#define SENSOR_FAULT_SLEW_RATE_DOWN 0x0020U // Перевищення темпу спадання
#define SENSOR_FAULT_CROSS_CHECK    0x0040U // Неузгодженість фізичної моделі
#define SENSOR_FAULT_STALE_TIMEOUT  0x0080U // Зависання каналу / тайм-аут

typedef enum {
    TRUST_LEVEL_FULL = 0,
    TRUST_LEVEL_DEGRADED,
    TRUST_LEVEL_ISOLATED
} TrustLevel_t;

// Конфігураційні фізичні межі сенсорного каналу
typedef struct {
    float electrical_min_v;    // Нижня електрична межа АЦП (напр. 0.2 В)
    float electrical_max_v;    // Верхня електрична межа АЦП (напр. 3.1 В)
    float range_min;           // Фізичний мінімум величини (напр. -40.0 °C)
    float range_max;           // Фізичний максимум величини (напр. +125.0 °C)
    float max_slew_up_per_s;   // Гранична швидкість росту величини в одиницях на секунду
    float max_slew_down_per_s; // Гранична швидкість спадання величини в одиницях на секунду
    uint32_t timeout_ms;       // Максимально допустима пауза між вимірами
    uint8_t penalty_weight;    // Штрафний бал за один збій (напр. 20)
    uint8_t leak_rate;         // Бал відновлення за чистий крок (напр. 1)
    uint8_t threshold_degrade; // Поріг переходу в стан DEGRADED (напр. 25)
    uint8_t threshold_isolate; // Поріг переходу в стан ISOLATED (напр. 80)
} SensorSanitizerConfig_t;

// Контекст динамічного стану сенсорного каналу
typedef struct {
    float last_valid_value;
    uint32_t last_update_time_ms;
    uint16_t fault_flags;
    uint8_t penalty_score;
    TrustLevel_t trust_level;
    bool is_initialized;
} SensorSanitizerState_t;

// Ініціалізація стану валідатора
void sensor_sanitizer_init(SensorSanitizerState_t *state) {
    if (!state) return;
    state->last_valid_value = 0.0f;
    state->last_update_time_ms = 0U;
    state->fault_flags = SENSOR_FAULT_NONE;
    state->penalty_score = 0U;
    state->trust_level = TRUST_LEVEL_FULL;
    state->is_initialized = false;
}

/**
 * @brief Повний цикл валідації та санітизації сенсорного відліку
 * @param cfg Конфігурація фізичних меж
 * @param state Стан сенсорного каналу
 * @param raw_voltage_v Виміряна напруга на вході АЦП
 * @param physical_value Обчислене фізичне значення
 * @param cross_check_valid Результат зовнішньої перехресної перевірки
 * @param now_ms Поточний монотонний час системи у мілісекундах
 * @param[out] sanitized_out Санітизоване безпечне значення для регулятора
 * @return true якщо значення придатне для використання (TRUSTED або DEGRADED)
 */
bool sensor_sanitizer_process(const SensorSanitizerConfig_t *cfg,
                             SensorSanitizerState_t *state,
                             float raw_voltage_v,
                             float physical_value,
                             bool cross_check_valid,
                             uint32_t now_ms,
                             float *sanitized_out) {
    if (!cfg || !state || !sanitized_out) return false;

    state->fault_flags = SENSOR_FAULT_NONE;
    bool step_valid = true;

    // 1. Перевірка на нечислові аномалії математики
    if (isnan(physical_value) || isinf(physical_value) || isnan(raw_voltage_v)) {
        state->fault_flags |= SENSOR_FAULT_NAN_INF;
        step_valid = false;
    }

    // 2. Електричні межі кола (обрив / КЗ)
    if (raw_voltage_v < cfg->electrical_min_v) {
        state->fault_flags |= SENSOR_FAULT_ELECTRICAL_LOW;
        step_valid = false;
    } else if (raw_voltage_v > cfg->electrical_max_v) {
        state->fault_flags |= SENSOR_FAULT_ELECTRICAL_HI;
        step_valid = false;
    }

    // 3. Статичні межі фізичного діапазону
    if (physical_value < cfg->range_min || physical_value > cfg->range_max) {
        state->fault_flags |= SENSOR_FAULT_STATIC_RANGE;
        step_valid = false;
    }

    // 4. Перевірка свіжості та тайм-ауту
    if (state->is_initialized) {
        uint32_t dt_ms = now_ms - state->last_update_time_ms;
        if (dt_ms > cfg->timeout_ms) {
            state->fault_flags |= SENSOR_FAULT_STALE_TIMEOUT;
            step_valid = false;
        }

        // 5. Динамічний фільтр швидкості зміни (Slew Rate)
        if (step_valid && dt_ms > 0U) {
            float dt_s = (float)dt_ms * 0.001f;
            float delta = physical_value - state->last_valid_value;
            float max_allowed_up = cfg->max_slew_up_per_s * dt_s;
            float max_allowed_down = cfg->max_slew_down_per_s * dt_s;

            if (delta > max_allowed_up) {
                state->fault_flags |= SENSOR_FAULT_SLEW_RATE_UP;
                step_valid = false;
                // Затискаємо викид до фізичної верхньої межі
                physical_value = state->last_valid_value + max_allowed_up;
            } else if (delta < -max_allowed_down) {
                state->fault_flags |= SENSOR_FAULT_SLEW_RATE_DOWN;
                step_valid = false;
                // Затискаємо викид до фізичної нижньої межі
                physical_value = state->last_valid_value - max_allowed_down;
            }
        }
    }

    // 6. Перехресна кореляція з іншими сенсорами
    if (!cross_check_valid) {
        state->fault_flags |= SENSOR_FAULT_CROSS_CHECK;
        step_valid = false;
    }

    // 7. Оновлення лічильника штрафів Leaky Bucket
    if (!step_valid) {
        uint16_t new_score = (uint16_t)state->penalty_score + cfg->penalty_weight;
        state->penalty_score = (new_score > 255U) ? 255U : (uint8_t)new_score;
    } else {
        if (state->penalty_score >= cfg->leak_rate) {
            state->penalty_score -= cfg->leak_rate;
        } else {
            state->penalty_score = 0U;
        }
    }

    // 8. Визначення рівня довіри до каналу
    if (state->penalty_score >= cfg->threshold_isolate) {
        state->trust_level = TRUST_LEVEL_ISOLATED;
    } else if (state->penalty_score >= cfg->threshold_degrade) {
        state->trust_level = TRUST_LEVEL_DEGRADED;
    } else {
        state->trust_level = TRUST_LEVEL_FULL;
    }

    // 9. Формування вихідного значення
    if (state->trust_level == TRUST_LEVEL_ISOLATED) {
        *sanitized_out = state->last_valid_value;
        return false;
    }

    if (step_valid || !state->is_initialized) {
        state->last_valid_value = physical_value;
        state->last_update_time_ms = now_ms;
        state->is_initialized = true;
    }

    *sanitized_out = state->last_valid_value;
    return true;
}
