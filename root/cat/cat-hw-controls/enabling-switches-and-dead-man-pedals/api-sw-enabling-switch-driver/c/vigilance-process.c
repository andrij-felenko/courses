// Типи зворотних викликів для vigilance control
typedef void (*vigilance_callback_t)(void *arg);

typedef struct {
    uint32_t t_hold_ms;       // Максимальний час безперервного утримання
    uint32_t t_warn_ms;       // Час світлового/звукового попередження
    uint32_t t_react_ms;      // Граничний час на реакцію оператора
    vigilance_callback_t on_warning; // Callback попередження
    vigilance_callback_t on_alarm;   // Callback аварійного зупинення
    void *user_data;          // Користувацькі дані для callback
} vigilance_config_t;

typedef struct {
    vigilance_config_t config;
    uint32_t hold_timer;
    bool warning_active;
    bool alarm_active;
} vigilance_controller_t;

// Оновлення таймерів пильності у циклі драйвера
void vigilance_process(vigilance_controller_t *vc, enabling_state_t state, uint16_t tick_ms) {
    if (!vc) return;

    if (state == ENABLING_STATE_ENABLED) {
        vc->hold_timer += tick_ms;
        
        // Фаза 1: Перевищення t_hold -> Попередження
        if (vc->hold_timer >= vc->config.t_hold_ms && !vc->warning_active) {
            vc->warning_active = true;
            if (vc->config.on_warning) {
                vc->config.on_warning(vc->config.user_data);
            }
        }
        
        // Фаза 2: Перевищення t_hold + t_warn + t_react -> Аварія
        uint32_t total_limit = vc->config.t_hold_ms + vc->config.t_warn_ms + vc->config.t_react_ms;
        if (vc->hold_timer >= total_limit && !vc->alarm_active) {
            vc->alarm_active = true;
            if (vc->config.on_alarm) {
                vc->config.on_alarm(vc->config.user_data);
            }
        }
    } else {
        // Скидання таймерів при зміні стану педалі
        vc->hold_timer = 0;
        vc->warning_active = false;
        vc->alarm_active = false;
    }
}
