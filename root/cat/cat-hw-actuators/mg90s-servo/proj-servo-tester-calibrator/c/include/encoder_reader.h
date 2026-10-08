#ifndef ENCODER_READER_H
#define ENCODER_READER_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file encoder_reader.h
 * @brief Модуль зчитування квадратурного енкодера з обробкою брязкоту контактів.
 *
 * Призначений для вимірювання обертання ручки керування та перетворення
 * квадрантних сигналів A/B у цільові часові інтервали для сервоприводу.
 */

#define ENCODER_DEBOUNCE_THRESHOLD_SAMPLES 3U /**< Кількість послідовних збігів для фільтрації брязкоту */

/**
 * @brief Структурний стан квадратурного енкодера
 */
typedef struct {
    int32_t position;            /**< Поточне значення лічильника кроків */
    int32_t min_position;        /**< Мінімальна межа позиції */
    int32_t max_position;        /**< Максимальна межа позиції */
    uint16_t pulse_step_us;      /**< Крок зміни імпульсу ШІМ на 1 тік енкодера (мкс) */
    
    bool raw_pin_a;              /**< Поточне сире значення лінії A */
    bool raw_pin_b;              /**< Поточне сире значення лінії B */
    bool debounced_pin_a;        /**< Відфільтроване значення лінії A */
    bool debounced_pin_b;        /**< Відфільтроване значення лінії B */

    uint8_t count_a;             /**< Лічильник стабільності лінії A */
    uint8_t count_b;             /**< Лічильник стабільності лінії B */
    
    uint8_t prev_state;          /**< Попередній збережений код стану фаз (A, B) */
} encoder_state_t;

/* Прототипи функцій */

/**
 * @brief Ініціалізація структури енкодера
 * @param enc Вказівник на структуру стану енкодера
 * @param min_pos Мінімальна позиція (відповідає 0 градусів / 1000 мкс)
 * @param max_pos Максимальна позиція (відповідає 180 градусів / 2000 мкс)
 * @param pulse_step_us Величина зміни тривалості імпульсу в мкс на один крок енкодера
 */
void encoder_init(encoder_state_t *enc, int32_t min_pos, int32_t max_pos, uint16_t pulse_step_us);

/**
 * @brief Обробка сирих сигналів з входів A та B з пригніченням брязкоту
 * @param enc Вказівник на структуру енкодера
 * @param raw_a Поточний стан фази A (true/false)
 * @param raw_b Поточний стан фази B (true/false)
 * @return true якщо відбулася зміна позиції енкодера, false якщо позиція не змінилася
 */
bool encoder_update_pins(encoder_state_t *enc, bool raw_a, bool raw_b);

/**
 * @brief Розрахунок тривалості керуючого імпульсу ШІМ на основі поточного стану енкодера
 * @param enc Вказівник на структуру енкодера
 * @return Тривалість імпульсу в мікросекундах (1000..2000 мкс)
 */
uint16_t encoder_to_pulse_us(const encoder_state_t *enc);

/**
 * @brief Розрахунок еквівалентного кута у градусах на основі позиції енкодера
 * @param enc Вказівник на структуру енкодера
 * @return Кут у градусах (0.0 .. 180.0)
 */
float encoder_to_angle_deg(const encoder_state_t *enc);

/**
 * @brief Примусове встановлення позиції енкодера
 * @param enc Вказівник на структуру енкодера
 * @param pos Нова позиція (обмежується діапазоном min_pos..max_pos)
 */
void encoder_set_position(encoder_state_t *enc, int32_t pos);

#endif /* ENCODER_READER_H */
