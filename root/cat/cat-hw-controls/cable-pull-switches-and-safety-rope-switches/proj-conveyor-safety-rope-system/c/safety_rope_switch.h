#ifndef SAFETY_ROPE_SWITCH_H
#define SAFETY_ROPE_SWITCH_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Стани скінченного автомата (FSM) контуру безпеки тросового вимикача
 */
typedef enum {
    SAFETY_STATE_NORMAL = 0,        /**< Робочий стан: обидва NC-канали замкнені, контур дозволено */
    SAFETY_STATE_TRIPPED_EMERGENCY, /**< Аварійне спрацьовування: контакти розімкнені в межах допуску */
    SAFETY_STATE_DISCREPANCY_FAULT, /**< Апаратний збій: перевищено допуск розсинхронізації каналів */
    SAFETY_STATE_WAIT_MANUAL_RESET  /**< Очікування підтвердженого ручного скидання оператором */
} safety_state_t;

/**
 * @brief Структура обробки окремого NC-каналу безпеки
 */
typedef struct {
    bool raw_state;          /**< Сирий стан GPIO-піна (true = замкнений NC, false = розімкнений) */
    bool debounced_state;    /**< Відфільтрований стан каналу після дебаунсингу */
    uint16_t debounce_timer; /**< Лічильник стабілізації сигналу в мілісекундах */
} safety_channel_t;

/**
 * @brief Головна структура стану та конфігурації двоканального тросового вимикача
 */
typedef struct {
    safety_channel_t channel1;     /**< Перший NC-канал підключення */
    safety_channel_t channel2;     /**< Другий NC-канал підключення */
    safety_state_t state;          /**< Поточний стан FSM контуру безпеки */
    uint16_t discrepancy_timer_ms; /**< Таймер відліку часового розсинхрону між каналами */
    uint16_t max_discrepancy_ms;   /**< Максимально допустимий розсинхрон каналів (напр. 40 мс) */
    uint16_t debounce_time_ms;     /**< Час фільтрації дребезгу контактів (напр. 5 мс) */
    bool safety_output;            /**< Сигнальний вихід дозволу роботи (true = ОК, false = АВАРІЯ) */
    bool fault_latched;            /**< Прапорець засува блокування помилки */
} safety_rope_switch_t;

/**
 * @brief Ініціалізація структури двоканального тросового вимикача
 * @param sw Вказівник на структуру вимикача
 * @param max_discrepancy_ms Допустимий розсинхрон каналів у мілісекундах
 * @param debounce_time_ms Час дебаунсингу у мілісекундах
 */
void safety_rope_switch_init(safety_rope_switch_t *sw, uint16_t max_discrepancy_ms, uint16_t debounce_time_ms);

/**
 * @brief Періодична обробка та оновлення стану вимикача (викликається у таймерному опитуванні)
 * @param sw Вказівник на структуру вимикача
 * @param ch1_raw Поточний зчитаний стан 1-го NC-каналу з GPIO
 * @param ch2_raw Поточний зчитаний стан 2-го NC-каналу з GPIO
 * @param dt_ms Час, що минув з попереднього виклику в мілісекундах
 */
void safety_rope_switch_update(safety_rope_switch_t *sw, bool ch1_raw, bool ch2_raw, uint16_t dt_ms);

/**
 * @brief Ручне скидання блокування після усунення аварії чи розсинхронізації
 * @param sw Вказівник на структуру вимикача
 * @return true якщо скидання успішне, false якщо контакти ще не повернулися в норму
 */
bool safety_rope_switch_reset(safety_rope_switch_t *sw);

/**
 * @brief Отримання поточного стану виходу безпеки
 * @param sw Вказівник на структуру вимикача
 * @return true якщо контур безпеки замкнено (дозвіл роботи)
 */
bool safety_rope_switch_is_safe(const safety_rope_switch_t *sw);

#ifdef __cplusplus
}
#endif

#endif /* SAFETY_ROPE_SWITCH_H */
