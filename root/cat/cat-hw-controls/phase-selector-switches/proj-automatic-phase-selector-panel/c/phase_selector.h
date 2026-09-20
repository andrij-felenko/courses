#ifndef PHASE_SELECTOR_H
#define PHASE_SELECTOR_H

#include <stdint.h>
#include <stdbool.h>

// Ідентифікатори трифазної мережі
typedef enum {
    PHASE_NONE = 0,
    PHASE_L1   = 1,
    PHASE_L2   = 2,
    PHASE_L3   = 3
} phase_id_t;

// Стани автомата FSM перемикача фаз
typedef enum {
    STATE_INIT = 0,
    STATE_MONITORING,      // Нормальна робота на вибраній фазі
    STATE_DEAD_TIME,       // Інтервал паузи (dead-time) для гасіння дуги
    STATE_RETURN_DELAY,    // Затримка повернення на пріоритетну фазу L1
    STATE_ALL_PHASES_FAULT // Аварія: усі фази вийшли за припустимі межі
} phase_selector_state_t;

// Конфігурація уставок напруги та затримок
typedef struct {
    float u_min;           // Нижній поріг напруги (V)
    float u_max;           // Верхній поріг напруги (V)
    float u_hysteresis;    // Гістерезис відновлення (V)
    uint32_t dead_time_ms; // Час паузи між відключенням та включенням (мс)
    uint32_t return_delay_ms; // Затримка повернення на L1 після стабілізації (мс)
} phase_selector_config_t;

// Структура стану контролера перемикання фаз
typedef struct {
    phase_selector_config_t config;
    phase_selector_state_t state;
    phase_id_t active_phase;      // Поточна підключена фаза
    phase_id_t target_phase;      // Цільова фаза для переключення
    uint32_t state_timer_ms;      // Лічильник часу для затримок FSM
} phase_selector_t;

// Прототипи функцій API
void phase_selector_init(phase_selector_t *ps, const phase_selector_config_t *cfg);
void phase_selector_update(phase_selector_t *ps, float u_l1, float u_l2, float u_l3, uint32_t dt_ms);
bool phase_selector_is_phase_valid(const phase_selector_t *ps, phase_id_t phase, float voltage);

#endif // PHASE_SELECTOR_H
