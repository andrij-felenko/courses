#ifndef G3MB202P_H
#define G3MB202P_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file g3mb202p.h
 * @brief Заголовочний файл драйвера твердотільного реле (SSR) G3MB-202P.
 *
 * Реле G3MB-202P призначене для комутації навантаження змінного струму (AC 100..240 V, до 2 A)
 * із гальванічною розв'язкою через оптопару та апаратною схемою виявлення переходу через нуль (Zero-Cross).
 */

/* Максимальний час увімкнення/вимкнення симістора при перетині нуля AC (1/2 періоду 50 Гц = 10 мс) */
#define G3MB202P_ZERO_CROSS_DELAY_MS 10U

/* Рекомендований мінімальний інтервал безпеки між перемиканнями силового реле (100 мс) */
#define G3MB202P_MIN_SWITCH_INTERVAL_MS 100U

/**
 * @brief Статуси виконання операцій драйвера G3MB-202P.
 */
typedef enum {
    G3MB202P_OK = 0,               /**< Успішне виконання операції */
    G3MB202P_ERROR_INVALID_PARAM,  /**< Передано некоректний вказівник або параметр */
    G3MB202P_ERROR_NOT_INITIALIZED,/**< Драйвер не ініціалізовано */
    G3MB202P_ERROR_THROTTLED       /**< Перемикання відхилено через перевищення частоти комутації */
} g3mb202p_status_t;

/**
 * @brief Полярність керуючого сигналу GPIO для вхідного світлодіода оптопари.
 */
typedef enum {
    G3MB202P_ACTIVE_HIGH = 0, /**< Active HIGH: HIGH (1) подає струм на світлодіод SSR */
    G3MB202P_ACTIVE_LOW  = 1  /**< Active LOW: LOW (0) подає струм на світлодіод SSR */
} g3mb202p_active_level_t;

/**
 * @brief Логічний стан силового навантаження.
 */
typedef enum {
    G3MB202P_STATE_OFF = 0, /**< Силове навантаження вимкнено */
    G3MB202P_STATE_ON  = 1  /**< Силове навантаження увімкнено */
} g3mb202p_state_t;

/**
 * @brief Вказівник на функцію апаратного запису логічного рівня в GPIO.
 * @param pin Номер цифрового виводу GPIO.
 * @param level Логічний рівень (true = HIGH, false = LOW).
 */
typedef void (*g3mb202p_gpio_write_fn)(uint8_t pin, bool level);

/**
 * @brief Вказівник на функцію затримки мікроконтролера в мілісекундах.
 * @param ms Тривалість затримки у мілісекундах.
 */
typedef void (*g3mb202p_delay_ms_fn)(uint32_t ms);

/**
 * @brief Вказівник на функцію отримання системного часу в мілісекундах (millis).
 * @return Системний час у мілісекундах від запуску МК.
 */
typedef uint32_t (*g3mb202p_get_ms_fn)(void);

/**
 * @brief Структура конфігурації драйвера G3MB-202P.
 */
typedef struct {
    uint8_t gpio_pin;                    /**< Номер виводу GPIO мікроконтролера */
    g3mb202p_active_level_t active_level;/**< Полярність керуючого сигналу */
    g3mb202p_state_t initial_state;      /**< Початковий безпечний стан реле */
    uint32_t min_switch_interval_ms;     /**< Захисна затримка між перемиканнями (мс) */
    g3mb202p_gpio_write_fn gpio_write;   /**< Функція апаратного запису GPIO (обов'язкова) */
    g3mb202p_delay_ms_fn delay_ms;       /**< Функція затримки МК (опціонально) */
    g3mb202p_get_ms_fn get_ms;           /**< Функція системного таймера МК (опціонально) */
} g3mb202p_config_t;

/**
 * @brief Дескриптор стану драйвера G3MB-202P.
 */
typedef struct {
    g3mb202p_config_t config;      /**< Скопійована конфігурація */
    g3mb202p_state_t current_state;/**< Фіксований поточний стан навантаження */
    uint32_t last_switch_time_ms;  /**< Часовий штамп останнього перемикання */
    bool is_initialized;          /**< Прапорець ініціалізації драйвера */
} g3mb202p_t;

/**
 * @brief Безпечна ініціалізація драйвера G3MB-202P.
 * 
 * Налаштовує початковий рівень GPIO та фіксує безпечний початковий стан навантаження.
 * 
 * @param handle Вказівник на дескриптор драйвера.
 * @param config Вказівник на структуру конфігурації.
 * @return G3MB202P_OK у разі успішної ініціалізації або код помилки.
 */
g3mb202p_status_t g3mb202p_init(g3mb202p_t *handle, const g3mb202p_config_t *config);

/**
 * @brief Перевірка, чи минув захисний часовий інтервал для безпечного перемикання.
 * 
 * @param handle Вказівник на дескриптор драйвера.
 * @return true якщо перемикання дозволено, false у протилежному випадку.
 */
bool g3mb202p_can_switch(const g3mb202p_t *handle);

/**
 * @brief Встановлення заданого стану реле (ON або OFF) з урахуванням затримок безпеки.
 * 
 * @param handle Вказівник на дескриптор драйвера.
 * @param state Бажаний стан реле (G3MB202P_STATE_ON або G3MB202P_STATE_OFF).
 * @return G3MB202P_OK, G3MB202P_ERROR_THROTTLED або інший відповідний код статусу.
 */
g3mb202p_status_t g3mb202p_set_state(g3mb202p_t *handle, g3mb202p_state_t state);

/**
 * @brief Увімкнення навантаження 240 В змінного струму.
 * 
 * @param handle Вказівник на дескриптор драйвера.
 * @return G3MB202P_OK або код помилки.
 */
g3mb202p_status_t g3mb202p_turn_on(g3mb202p_t *handle);

/**
 * @brief Вимкнення навантаження 240 В змінного струму.
 * 
 * @param handle Вказівник на дескриптор драйвера.
 * @return G3MB202P_OK або код помилки.
 */
g3mb202p_status_t g3mb202p_turn_off(g3mb202p_t *handle);

/**
 * @brief Безпечне перемикання стану реле на протилежний (Toggle).
 * 
 * @param handle Вказівник на дескриптор драйвера.
 * @return G3MB202P_OK або код помилки.
 */
g3mb202p_status_t g3mb202p_toggle(g3mb202p_t *handle);

/**
 * @brief Отримання зафіксованого поточного стану реле.
 * 
 * @param handle Вказівник на дескриптор драйвера.
 * @param state Вказівник для збереження поточного стану.
 * @return G3MB202P_OK або код помилки.
 */
g3mb202p_status_t g3mb202p_get_state(const g3mb202p_t *handle, g3mb202p_state_t *state);

#endif /* G3MB202P_H */
