/**
 * @file enabling_switch.h
 * @brief Драйвер трипозиційного пристрою дозволу та педалей «мертвої руки».
 */

#ifndef ENABLING_SWITCH_H
#define ENABLING_SWITCH_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Стани системи функціональної безпеки перемикача.
 */
typedef enum {
    ENABLING_STATE_RELEASED = 0,  /**< Положення 1: Відпущено (Вимкнено) */
    ENABLING_STATE_ACTIVE   = 1,  /**< Положення 2: Натиснуто в центр (Дозвіл роботи) */
    ENABLING_STATE_PANIC    = 2,  /**< Положення 3: Панічний натиск (Аварійна зупинка) */
    ENABLING_STATE_FAULT    = 3   /**< Помилка: Розсинхронізація каналів або КЗ */
} EnablingState;

/**
 * @brief Конфігураційні параметри драйвера.
 */
typedef struct {
    uint32_t debounce_ms;             /**< Час фільтрації брязкіту (мс) */
    uint32_t discrepancy_timeout_ms;  /**< Таймаут розсинхронізації каналів (мс) */
    bool enable_pulse_test;           /**< Прапорець активації тестових імпульсів */
} EnablingSwitchConfig;

/**
 * @brief Структура стану пристрою дозволу.
 */
typedef struct {
    EnablingSwitchConfig config;       /**< Конфігурація драйвера */
    EnablingState current_state;       /**< Поточний стан FSM */
    
    bool ch1_debounced;                /**< Відфільтрований стан каналу 1 */
    bool ch2_debounced;                /**< Відфільтрований стан каналу 2 */
    
    bool ch1_raw_last;                 /**< Попереднє сире значення каналу 1 */
    bool ch2_raw_last;                 /**< Попереднє сире значення каналу 2 */
    
    uint32_t ch1_last_change_ms;       /**< Час останньої зміни каналу 1 */
    uint32_t ch2_last_change_ms;       /**< Час останньої зміни каналу 2 */
    
    uint32_t discrepancy_start_ms;     /**< Час початку розсинхронізації */
    bool discrepancy_active;           /**< Прапорець фіксації розсинхронізації */
    
    bool requires_reset;               /**< Блокування повторного пуску (потрібне скидання) */
    bool cross_fault_detected;         /**< Помилка короткого замикання між каналами */
} EnablingSwitch;

/**
 * @brief Ініціалізація структури драйвера пристрою дозволу.
 * @param sw Вказівник на структуру перемикача.
 * @param config Конфігураційні параметри.
 */
void enabling_switch_init(EnablingSwitch *sw, EnablingSwitchConfig config);

/**
 * @brief Неблокуюче опитування каналів та оновлення кінцевого автомата станів (FSM).
 * @param sw Вказівник на структуру перемикача.
 * @param ch1_raw Поточний сирий сигнал каналу 1.
 * @param ch2_raw Поточний сирий сигнал каналу 2.
 * @param current_time_ms Поточний системний час у мілісекундах.
 * @param test_pulse_fn Вказівник на функцію виконання тестового імпульсу (може бути NULL).
 * @return Поточний стан системи безпеки.
 */
EnablingState enabling_switch_update(EnablingSwitch *sw, bool ch1_raw, bool ch2_raw, 
                                     uint32_t current_time_ms, 
                                     bool (*test_pulse_fn)(uint8_t channel));

/**
 * @brief Скидання прапорців помилок та блокування після аварійного стану.
 * @param sw Вказівник на структуру перемикача.
 */
void enabling_switch_reset(EnablingSwitch *sw);

/**
 * @brief Перетворення стану в текстовий рядок для діагностики.
 * @param state Стан безпеки.
 * @return Текстова назва стану.
 */
const char* enabling_switch_state_to_str(EnablingState state);

#endif /* ENABLING_SWITCH_H */
