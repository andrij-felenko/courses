#ifndef TOGGLE_SWITCH_TYPES_H
#define TOGGLE_SWITCH_TYPES_H

#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"

// Фізичний та логічний стан 3-позиційного тумблера (ON1-OFF-ON2 / ON-OFF-ON)
typedef enum {
    TOGGLE_STATE_OFF = 0,    // Важіль у нейтральному центральному положенні (OFF)
    TOGGLE_STATE_ON1 = 1,    // Положення 1 (наприклад, верхнє)
    TOGGLE_STATE_ON2 = 2,    // Положення 2 (наприклад, нижнє)
    TOGGLE_STATE_INVALID = 3 // Невизначений або заборонений стан (напр. одночасний контакт на двох лініях)
} toggle_switch_state_t;

// Подія зміни стану тумблера
typedef struct {
    toggle_switch_state_t previous_state;
    toggle_switch_state_t current_state;
    uint32_t timestamp_ms;
} toggle_switch_event_t;

// Конфігурація підключення 3-позиційного тумблера (SPDT з центральним OFF або DPDT)
typedef struct {
    gpio_num_t pin_on1;       // Пін GPIO для положення ON1 (-1 якщо 2-позиційний ON-OFF)
    gpio_num_t pin_on2;       // Пін GPIO для положення ON2
    uint32_t debounce_ms;     // Час затримки фільтрації брязкоту контактів (мс)
    bool active_low;          // true: підтяжка до VCC, замкнено на GND (LOW)
} toggle_switch_config_t;

#endif // TOGGLE_SWITCH_TYPES_H
