#include <stdint.h>
#include <stdbool.h>

// Логічні стани трипозиційного давача дозволу
typedef enum {
    ENABLING_STATE_RELEASED = 0, // Відпущено (позиція 1)
    ENABLING_STATE_ENABLED  = 1, // Дозволено (позиція 2)
    ENABLING_STATE_PANIC    = 2, // Паніка (позиція 3)
    ENABLING_STATE_FAULT    = 3  // Апаратний збій / розсинхронізм
} enabling_state_t;

// Структура конфігурації драйвера давача
typedef struct {
    bool (*read_ch_a)(void);    // Вказівник на зчитування каналу A
    bool (*read_ch_b)(void);    // Вказівник на зчитування каналу B
    uint16_t debounce_ms;       // Час фільтрації брязкоту (мс)
    uint16_t discrepancy_ms;    // Максимальний розсинхронізм каналів (мс)
} enabling_config_t;

// Контекст виконання драйвера
typedef struct {
    enabling_config_t config;
    enabling_state_t current_state;
    uint32_t discrepancy_timer;
    bool prev_ch_a;
    bool prev_ch_b;
} enabling_driver_t;

// Ініціалізація модуля
bool enabling_driver_init(enabling_driver_t *driver, const enabling_config_t *config) {
    if (!driver || !config || !config->read_ch_a || !config->read_ch_b) {
        return false;
    }
    driver->config = *config;
    driver->current_state = ENABLING_STATE_RELEASED;
    driver->discrepancy_timer = 0;
    driver->prev_ch_a = config->read_ch_a();
    driver->prev_ch_b = config->read_ch_b();
    return true;
}
