#ifndef THUMBWHEEL_74HC165_H
#define THUMBWHEEL_74HC165_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Максимальна кількість розрядів (декад) у блоці
#define THUMBWHEEL_MAX_DIGITS 8

// Глибина мажоритарного буфера фільтрації брязкоту контактів
#define THUMBWHEEL_FILTER_DEPTH 5

// Визначення типів функцій-колбеків для маніпуляції GPIO-лініями
typedef void (*thumbwheel_gpio_write_fn)(bool level);
typedef bool (*thumbwheel_gpio_read_fn)(void);
typedef void (*thumbwheel_delay_us_fn)(uint32_t us);

// Конфігураційна структура C-драйвера 74HC165
typedef struct {
    thumbwheel_gpio_write_fn set_pl;   // Встановлення рівня на лінії PL (Parallel Load)
    thumbwheel_gpio_write_fn set_clk;  // Встановлення рівня на лінії CLK (Clock)
    thumbwheel_gpio_read_fn  read_q7;  // Зчитування стану лінії Q7 (Serial Data Out)
    thumbwheel_delay_us_fn   delay_us; // Функція затримки в мікросекундах

    uint8_t num_digits;                // Кількість розрядів перемикача (1..8)
    bool active_low_logic;             // true — прямий BCD (активний нуль), false — комплементарний BCD
} thumbwheel_config_t;

// Дескриптор стану драйвера та кільцевого буфера
typedef struct {
    thumbwheel_config_t config;
    uint8_t raw_history[THUMBWHEEL_MAX_DIGITS][THUMBWHEEL_FILTER_DEPTH]; // Кільцевий буфер кожної тетради
    uint8_t filter_index;                                                // Поточний індекс у буфері
    uint32_t last_valid_value;                                           // Останнє валідне підтверджене число
    bool is_initialized;
} thumbwheel_driver_t;

// Статуси повернення функцій
typedef enum {
    THUMBWHEEL_OK = 0,
    THUMBWHEEL_ERR_INVALID_PARAM,
    THUMBWHEEL_ERR_TRANSIT_CODE,  // Виявлено міжконтактний транзитний код (10..15)
    THUMBWHEEL_ERR_NOT_INIT
} thumbwheel_status_t;

/**
 * @brief Ініціалізація драйвера зчитування декадних перемикачів 74HC165
 * @param driver Вказівник на дескриптор драйвера
 * @param config Конфігураційні параметри та колбеки GPIO
 * @return THUMBWHEEL_OK у разі успішної ініціалізації
 */
thumbwheel_status_t thumbwheel_init(thumbwheel_driver_t *driver, const thumbwheel_config_t *config);

/**
 * @brief Опитування зсувного регістра, зчитування кадру, фільтрація та валідація BCD-кодів
 * @param driver Вказівник на дескриптор драйвера
 * @param out_value Змінна для запису зчитаного десяткового числа
 * @return THUMBWHEEL_OK при валідному зчитаному числі
 */
thumbwheel_status_t thumbwheel_read_value(thumbwheel_driver_t *driver, uint32_t *out_value);

#ifdef __cplusplus
}
#endif

#endif // THUMBWHEEL_74HC165_H
