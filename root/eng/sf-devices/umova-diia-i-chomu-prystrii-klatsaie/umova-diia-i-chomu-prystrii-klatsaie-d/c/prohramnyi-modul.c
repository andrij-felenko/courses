#include <stdbool.h>

/* Конфігурація: незмінні параметри меж */
typedef struct {
    float low_threshold;   /* Поріг вимкнення */
    float high_threshold;  /* Поріг увімкнення */
} hysteresis_config_t;

/* Стан: мутабельна пам'ять автомата */
typedef struct {
    bool current_output;   /* Поточний логічний рівень (1 / 0) */
    bool is_initialized;   /* Прапорець першого проходу */
} hysteresis_state_t;

/**
 * @brief Обчислення нового стану за поточним вимірюванням
 */
bool hysteresis_step(const hysteresis_config_t *cfg, 
                     hysteresis_state_t *state, 
                     float input_value) {
    if (!state->is_initialized) {
        /* Холодний старт: увімкнено лише якщо строго вище верхньої межі */
        state->current_output = (input_value >= cfg->high_threshold);
        state->is_initialized = true;
        return state->current_output;
    }

    if (state->current_output) {
        /* Зараз увімкнено: вимикаємо лише при спаді нижче low_threshold */
        if (input_value <= cfg->low_threshold) {
            state->current_output = false;
        }
    } else {
        /* Зараз вимкнено: вмикаємо лише при підйомі вище high_threshold */
        if (input_value >= cfg->high_threshold) {
            state->current_output = true;
        }
    }

    return state->current_output;
}
