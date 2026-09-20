#ifndef PWM_DRIVER_H
#define PWM_DRIVER_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file pwm_driver.h
 * @brief Драйвер апаратного ШІМ-сигналу для керування низькостороннім MOSFET-ключем.
 *
 * Модуль призначений для програмування апаратного таймера мікроконтролера,
 * генерації ШІМ-сигналу потрібної частоти та динамічної зміни коефіцієнта
 * заповнення (Duty Cycle) для керування силовим DC-навантаженням (двигуном).
 */

/* Максимальне значення коефіцієнта заповнення у відсотках */
#define PWM_DUTY_MAX_PERCENT   100U
#define PWM_DUTY_MIN_PERCENT   0U

/**
 * @brief Коди повернення функцій драйвера ШІМ.
 */
typedef enum {
    PWM_STATUS_OK = 0,               /**< Операцію виконано успішно */
    PWM_STATUS_INVALID_PARAM,        /**< Некоректні вхідні параметри */
    PWM_STATUS_NOT_INITIALIZED,      /**< Драйвер не ініціалізовано */
    PWM_STATUS_HW_ERROR              /**< Помилка розрахунку периферії */
} pwm_status_t;

/**
 * @brief Структура первинної конфігурації апаратного таймера.
 */
typedef struct {
    uint32_t timer_clock_hz;   /**< Частота тактування таймера (Гц), напр. 72000000 (72 МГц) */
    uint32_t pwm_frequency_hz; /**< Бажана частота ШІМ (Гц), напр. 20000 (20 кГц) */
    uint8_t timer_channel;     /**< Номер каналу ШІМ (1..4) */
    uint8_t gpio_pin;          /**< Номер виводу GPIO для виходу ШІМ */
} pwm_config_t;

/**
 * @brief Дескриптор драйвера ШІМ.
 */
typedef struct {
    pwm_config_t config;      /**< Скопійована конфігурація */
    uint16_t prescaler;       /**< Обчислене значення преддільника (PSC) */
    uint16_t period_arr;      /**< Обчислене значення періоду / автоперезавантаження (ARR) */
    uint16_t compare_ccr;     /**< Поточне значення регістру порівняння (CCR) */
    uint8_t current_duty_pct; /**< Поточний коефіцієнт заповнення (0..100%) */
    bool is_initialized;      /**< Прапорець завершення ініціалізації */
    bool is_running;          /**< Прапорець активного стану таймера */
} pwm_driver_t;

/**
 * @brief Ініціалізує апаратний таймер мікроконтролера та обчислює значення регістрів PSC та ARR.
 * 
 * @param driver Вказівник на дескриптор драйвера.
 * @param config Вказівник на структуру конфігурації.
 * @return pwm_status_t PWM_STATUS_OK при успіху або відповідний код помилки.
 */
pwm_status_t pwm_driver_init(pwm_driver_t *driver, const pwm_config_t *config);

/**
 * @brief Запускає генерацію ШІМ-сигналу на обраному виході.
 * 
 * @param driver Вказівник на дескриптор драйвера.
 * @return pwm_status_t PWM_STATUS_OK або код помилки.
 */
pwm_status_t pwm_driver_start(pwm_driver_t *driver);

/**
 * @brief Зупиняє генерацію ШІМ-сигналу (примусово притискає вихід до 0V).
 * 
 * @param driver Вказівник на дескриптор драйвера.
 * @return pwm_status_t PWM_STATUS_OK або код помилки.
 */
pwm_status_t pwm_driver_stop(pwm_driver_t *driver);

/**
 * @brief Встановлює коефіцієнт заповнення ШІМ у відсотках (0..100%).
 * 
 * @param driver Вказівник на дескриптор драйвера.
 * @param duty_percent Зміщення коефіцієнта заповнення у відсотках.
 * @return pwm_status_t PWM_STATUS_OK або код помилки.
 */
pwm_status_t pwm_set_duty_cycle(pwm_driver_t *driver, uint8_t duty_percent);

/**
 * @brief Встановлює значення регістру порівняння (CCR) напряму у відліках таймера.
 * 
 * @param driver Вказівник на дескриптор драйвера.
 * @param compare_val Значення відліків для регістру порівняння (0..ARR).
 * @return pwm_status_t PWM_STATUS_OK або код помилки.
 */
pwm_status_t pwm_set_duty_raw(pwm_driver_t *driver, uint16_t compare_val);

/**
 * @brief Отримує поточне значення коефіцієнта заповнення (0..100%).
 * 
 * @param driver Вказівник на дескриптор драйвера.
 * @return uint8_t Коефіцієнт заповнення у відсотках.
 */
uint8_t pwm_get_current_duty(const pwm_driver_t *driver);

#endif /* PWM_DRIVER_H */
