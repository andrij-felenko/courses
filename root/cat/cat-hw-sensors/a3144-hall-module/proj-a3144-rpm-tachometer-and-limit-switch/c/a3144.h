#ifndef A3144_H
#define A3144_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file a3144.h
 * @brief Заголовний файл C-драйвера цифрового давача Холла A3144.
 *
 * Призначений для використання A3144 у режимах безконтактного кінцевого
 * вимикача та вимірювання швидкості обертання (RPM).
 */

/**
 * @brief Режим підтяжки вхідної лінії GPIO.
 */
typedef enum {
    A3144_PULL_NONE = 0, /**< Без внутрішнього підтягування */
    A3144_PULL_UP   = 1, /**< Внутрішнє підтягування до VCC (рекомендовано) */
    A3144_PULL_DOWN = 2  /**< Внутрішнє підтягування до GND */
} a3144_pull_t;

/**
 * @brief Параметри спрацьовування апаратного переривання EXTI.
 */
typedef enum {
    A3144_EXTI_TRIGGER_FALLING = 0, /**< Переривання за спадним фронтом (наближення магніту, LOW) */
    A3144_EXTI_TRIGGER_RISING  = 1, /**< Переривання за зростаючим фронтом (віддалення магніту, HIGH) */
    A3144_EXTI_TRIGGER_BOTH    = 2  /**< Переривання за обома фронтами (будь-яка зміна стану) */
} a3144_exti_trigger_t;

/**
 * @brief Поточний стан кінцевого вимикача на базі давача Холла.
 */
typedef enum {
    A3144_STATE_IDLE          = 0, /**< Магніт відсутній (сигнал HIGH, вимикач розімкнений) */
    A3144_STATE_MAGNET_ACTIVE = 1  /**< Магніт виявлено (сигнал LOW, вимикач замкнений) */
} a3144_state_t;

/**
 * @brief Структура конфігурації вхідного виводу GPIO, типу підтяжки та EXTI.
 */
typedef struct {
    uint16_t gpio_pin;                  /**< Номер або маска вхідного виводу GPIO */
    a3144_pull_t pull_type;             /**< Тип підтягувального резистора */
    a3144_exti_trigger_t exti_trigger;  /**< Режим спрацьовування EXTI */
    uint32_t debounce_ms;               /**< Час придушення брязкоту у мілісекундах */
    uint32_t pulses_per_rev;            /**< Кількість магнітних полюсів/імпульсів на один оберт */
    uint32_t rpm_timeout_ms;            /**< Таймаут відсутності імпульсів для скидання RPM у 0 */
} a3144_config_t;

/**
 * @brief Структура збереження стану кінцевого вимикача та метрик RPM.
 */
typedef struct {
    a3144_config_t config;               /**< Копія конфігурації давача */
    volatile a3144_state_t state;        /**< Поточний фізичний стан вимикача */
    volatile bool approach_flag;         /**< Прапорець події наближення магніту */
    volatile bool removal_flag;          /**< Прапорець події віддалення магніту */
    volatile uint32_t trigger_count;     /**< Загальний лічильник спрацьовувань */
    volatile uint32_t last_interrupt_ms; /**< Час останнього валідного переривання (мс) */
    volatile uint32_t pulse_period_ms;   /**< Період між імпульсами для розрахунку RPM (мс) */
    volatile float current_rpm;          /**< Розрахована швидкість обертання (об/хв) */
    volatile uint32_t last_rpm_update_ms;/**< Позначка часу останнього оновлення RPM */
} a3144_handle_t;

/**
 * @brief Ініціалізація драйвера давача A3144 та конфігурація структур.
 *
 * @param handle Вказівник на структуру стану давача
 * @param config Вказівник на структуру конфігурації
 * @return true у разі успішної ініціалізації, false якщо параметри некоректні
 */
bool a3144_init(a3144_handle_t *handle, const a3144_config_t *config);

/**
 * @brief Обробник апаратного переривання EXTI (викликається у контексті ISR).
 *
 * @param handle Вказівник на структуру стану давача
 * @param current_time_ms Поточний системний час у мілісекундах
 * @param is_pin_low Логічний стан виводу (true якщо LOW - магніт поруч, false якщо HIGH)
 */
void a3144_exti_isr_handler(a3144_handle_t *handle, uint32_t current_time_ms, bool is_pin_low);

/**
 * @brief Неблокувальне оброблення станів, програмного дебаунсу та розрахунку RPM у головному циклі.
 *
 * @param handle Вказівник на структуру стану давача
 * @param current_time_ms Поточний системний час у мілісекундах
 */
void a3144_process(a3144_handle_t *handle, uint32_t current_time_ms);

/**
 * @brief Перевірка наявності магнітного поля (стан кінцевого вимикача).
 *
 * @param handle Вказівник на структуру стану давача
 * @return true якщо магніт присутній (вимикач замкнений), false якщо магніт відсутній
 */
bool a3144_is_magnet_present(const a3144_handle_t *handle);

/**
 * @brief Перевірка та автоматичне скидання події наближення магніту.
 *
 * @param handle Вказівник на структуру стану давача
 * @return true якщо зафіксовано нове наближення магніту
 */
bool a3144_get_approach_event(a3144_handle_t *handle);

/**
 * @brief Перевірка та автоматичне скидання події віддалення магніту.
 *
 * @param handle Вказівник на структуру стану давача
 * @return true якщо зафіксовано нове віддалення магніту
 */
bool a3144_get_removal_event(a3144_handle_t *handle);

/**
 * @brief Отримання загальної кількості спрацьовувань кінцевого вимикача.
 *
 * @param handle Вказівник на структуру стану давача
 * @return Кількість спрацьовувань
 */
uint32_t a3144_get_trigger_count(const a3144_handle_t *handle);

/**
 * @brief Отримання поточної розрахованої швидкості обертання (RPM).
 *
 * @param handle Вказівник на структуру стану давача
 * @return Швидкість обертання у обертах за хвилину
 */
float a3144_get_rpm(const a3144_handle_t *handle);

/**
 * @brief Скидання лічильника спрацьовувань та значень RPM.
 *
 * @param handle Вказівник на структуру стану давача
 */
void a3144_reset_counters(a3144_handle_t *handle);

#endif
