#ifndef ENABLING_SWITCH_H
#define ENABLING_SWITCH_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Стани скінченного автомата (FSM) 3-позиційного пристрою дозволу.
 */
typedef enum {
    ENABLING_STATE_RELEASED = 0,  /**< Позиція 1: Важіль/педаль відпущена (БЕЗПЕКА/OFF) */
    ENABLING_STATE_ENABLED,       /**< Позиція 2: Положення дозволу в середній зоні (ON) */
    ENABLING_STATE_PANIC,         /**< Позиція 3: Важіль перетиснуто в паніці (БЕЗПЕКА/OFF) */
    ENABLING_STATE_FAULT          /**< Апаратна відмова: розсинхронізм каналів або брязкіт */
} EnablingState_t;

/**
 * @brief Логічний стан фізичного контакту одного каналу.
 */
typedef enum {
    CONTACT_OPEN = 0,
    CONTACT_CLOSED = 1
} ContactState_t;

/**
 * @brief Конфігураційні параметри для фільтрації та діагностики (ISO 13849).
 */
typedef struct {
    uint32_t debounce_time_ms;      /**< Час пригнічення брязкоту контактів (типово 10-20 мс) */
    uint32_t discrepancy_time_ms;   /**< Максимально припустимий час розсинхронізму каналів (типово 50-100 мс) */
} EnablingSwitchConfig_t;

/**
 * @brief Структура стану двоканального 3-позиційного вимикача (EnablingSwitch_t).
 */
typedef struct {
    // Фізичні стани входів GPIO
    bool raw_ch1;
    bool raw_ch2;

    // Відфільтровані стани контактів
    ContactState_t debounced_ch1;
    ContactState_t debounced_ch2;

    // Таймери фільтрації брязкоту
    uint32_t ch1_debounce_timer;
    uint32_t ch2_debounce_timer;

    // Контроль розсинхронізму каналів (Discrepancy Monitoring)
    bool discrepancy_active;
    uint32_t discrepancy_timer;

    // Поточний стан та конфігурація
    EnablingState_t current_state;
    EnablingSwitchConfig_t config;
} EnablingSwitch_t;

/**
 * @brief Ініціалізація структури вимикача дозволу.
 * @param sw Вказівник на структуру вимикача.
 * @param config Налаштування таймаутів.
 */
void EnablingSwitch_Init(EnablingSwitch_t *sw, const EnablingSwitchConfig_t *config);

/**
 * @brief Періодична обробка зчитаних сигналів GPIO та оновлення автомата FSM.
 * @param sw Вказівник на структуру вимикача.
 * @param ch1_raw Сирий стан першого каналу.
 * @param ch2_raw Сирий стан другого каналу.
 * @param delta_ms Інтервал часу з попереднього виклику в мілісекундах.
 * @return Поточний стан FSM після обробки.
 */
EnablingState_t EnablingSwitch_Update(EnablingSwitch_t *sw, bool ch1_raw, bool ch2_raw, uint32_t delta_ms);

/**
 * @brief Отримання поточного стану FSM.
 */
EnablingState_t EnablingSwitch_GetState(const EnablingSwitch_t *sw);

/**
 * @brief Скидання апаратної відмови FSM (після усунення несправності).
 */
void EnablingSwitch_ResetFault(EnablingSwitch_t *sw);

#endif // ENABLING_SWITCH_H
