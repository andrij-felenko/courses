#ifndef QUAD_ENCODER_DRIVER_H
#define QUAD_ENCODER_DRIVER_H

#include "quad_encoder_types.h"

// Часові константи для обробки кнопки (у мілісекундах)
#define ENCODER_BTN_DEBOUNCE_MS     20U
#define ENCODER_BTN_LONG_PRESS_MS 1000U

/**
 * @brief Ініціалізація структури квадратурного енкодера.
 * @param enc Вказівник на екземпляр енкодера.
 * @param initial_a Початковий стан лінії фази A (0 або 1).
 * @param initial_b Початковий стан лінії фази B (0 або 1).
 */
void quad_encoder_init(quad_encoder_t *enc, uint8_t initial_a, uint8_t initial_b);

/**
 * @brief Обробник зміни стану фазових ліній A і B (зазвичай викликається з ISR).
 * @param enc Вказівник на екземпляр енкодера.
 * @param phase_a Поточний стан фази A.
 * @param phase_b Поточний стан фази B.
 */
void quad_encoder_update_phases(quad_encoder_t *enc, uint8_t phase_a, uint8_t phase_b);

/**
 * @brief Періодичний обробник кнопки (викликається в системному таймері або суперциклі).
 * @param enc Вказівник на екземпляр енкодера.
 * @param raw_button_state Сирий стан контакту кнопки (1 - активний/натиснуто, 0 - відпущено).
 * @param current_time_ms Поточний системний час у мілісекундах.
 * @return Подія кнопки, якщо вона виникла під час цього потактового оновлення.
 */
quad_encoder_event_t quad_encoder_update_button(quad_encoder_t *enc, uint8_t raw_button_state, uint32_t current_time_ms);

/**
 * @brief Отримання поточної абсолютної позиції енкодера.
 * @param enc Вказівник на екземпляр енкодера.
 * @return Атомарно зчитане значення лічильника.
 */
int32_t quad_encoder_get_position(const quad_encoder_t *enc);

/**
 * @brief Визначення зміни позиції з моменту останньої перевірки.
 * @param enc Вказівник на екземпляр енкодера.
 * @return Дельта зміни позиції (позитивне або негативне значення).
 */
int32_t quad_encoder_get_delta(quad_encoder_t *enc);

#endif // QUAD_ENCODER_DRIVER_H
