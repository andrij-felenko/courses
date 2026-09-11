// Структура експоненційного БІХ-фільтра струму
typedef struct {
    float alpha;         // Коефіцієнт згладжування (0.0f < alpha <= 1.0f)
    float filtered_val;  // Накопичене згладжене значення струму (мА)
    bool  initialized;   // Прапорець першого захоплення сигналу
} motor_iir_filter_t;

// Ініціалізація параметрів фільтра
static inline void motor_filter_init(motor_iir_filter_t *f, float alpha) {
    if (!f) return;
    f->alpha = (alpha > 0.0f && alpha <= 1.0f) ? alpha : 0.08f;
    f->filtered_val = 0.0f;
    f->initialized = false;
}

// Обчислення нового кроку фільтрації згладженого струму
static inline float motor_filter_step(motor_iir_filter_t *f, float raw_val) {
    if (!f) return raw_val;
    if (!f->initialized) {
        // Миттєвий старт з першого виміру для усунення початкового перехідного процесу
        f->filtered_val = raw_val;
        f->initialized = true;
    } else {
        f->filtered_val += f->alpha * (raw_val - f->filtered_val);
    }
    return f->filtered_val;
}

// Приклад інтеграції фільтра в цикл опитування АЦП перед струмовим компаратором:
// uint16_t raw_current = motor->cfg.hal.read_current_ma ? motor->cfg.hal.read_current_ma() : 0;
// uint16_t current = (uint16_t)motor_filter_step(&motor->current_filter, (float)raw_current);
// if (current >= motor->cfg.stall_current_ma) { ... }
