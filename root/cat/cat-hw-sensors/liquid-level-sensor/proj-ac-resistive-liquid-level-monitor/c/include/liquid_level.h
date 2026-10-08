#ifndef LIQUID_LEVEL_H
#define LIQUID_LEVEL_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file liquid_level.h
 * @brief Інтерфейс драйвера для опитання аналогових та тумблерних давачів рівня рідини.
 *
 * Модуль реалізує цифровізацію пікових значень для придушення сплесків та хвилювання
 * поверхні рідини, програмний гістерезис для керування помпою, а також таймери
 * захисту від сухого ходу та тривалого перекачування.
 */

#ifdef __cplusplus
extern "C" {
#endif

/** @brief Максимальна кількість відліків у ковзному вікні пікового фільтра АЦП */
#define LIQUID_LEVEL_PEAK_WINDOW_MAX 16

/**
 * @brief Режими роботи автоматики контролю рівня рідини.
 */
typedef enum {
    LIQUID_LEVEL_MODE_FILL = 0, /**< Режим наповнення: увімкнення помпи при низькому рівні, вимкнення при високому */
    LIQUID_LEVEL_MODE_DRAIN     /**< Режим відкачування: увімкнення помпи при високому рівні, вимкнення при низькому */
} liquid_level_mode_t;

/**
 * @brief Стан виконавчого обладнання (помпи) та захисних блокувань.
 */
typedef enum {
    PUMP_STATE_OFF = 0,       /**< Помпа вимкнена, нормальний режим */
    PUMP_STATE_RUNNING,       /**< Помпа активна та здійснює перекачування */
    PUMP_STATE_FAULT_DRY_RUN, /**< Аварійне вимкнення: виявлено сухий хід (відсутність динаміки рівня) */
    PUMP_STATE_FAULT_OVERRUN  /**< Аварійне вимкнення: перевищено допустимий час безперервної роботи */
} pump_state_t;

/**
 * @brief Коди повернення функцій драйвера рівня рідини.
 */
typedef enum {
    LIQUID_LEVEL_OK = 0,         /**< Операція виконана успішно */
    LIQUID_LEVEL_ERROR_NULL_PTR, /**< Передано нульовий вказівник */
    LIQUID_LEVEL_ERROR_PARAM,    /**< Некоректні параметри конфігурації */
    LIQUID_LEVEL_ERROR_HAL       /**< Помилка апаратного рівня абстракції (АЦП/GPIO) */
} liquid_level_status_t;

/**
 * @brief Структура налаштування драйвера давача рівня рідини.
 */
typedef struct {
    uint8_t  adc_channel;           /**< Номер аналогового каналу АЦП */
    uint16_t adc_min_raw;           /**< Значення АЦП при мінімальному рівні (0%) */
    uint16_t adc_max_raw;           /**< Значення АЦП при максимальному рівні (100%) */
    uint8_t  peak_window_size;      /**< Розмір вікна пікової фільтрації (1..LIQUID_LEVEL_PEAK_WINDOW_MAX) */

    uint8_t  gpio_pin_low_float;    /**< Номер GPIO аварійного нижнього поплавка (тумблера) */
    uint8_t  gpio_pin_high_float;   /**< Номер GPIO аварійного верхнього поплавка (тумблера) */
    uint8_t  gpio_pin_pump_relay;   /**< Номер GPIO керування реле помпи */

    float    threshold_turn_on_pct; /**< Поріг увімкнення помпи у відсотках (0..100%) */
    float    threshold_turn_off_pct;/**< Поріг вимкнення помпи у відсотках (0..100%) */

    uint32_t dry_run_timeout_ms;    /**< Час очікування зміни рівня до фіксації сухого ходу (мс) */
    uint32_t max_run_timeout_ms;    /**< Граничний час безперервної роботи помпи (мс) */
    uint32_t debounce_time_ms;      /**< Інтервал програмного антибрязкоту поплавкових GPIO (мс) */

    liquid_level_mode_t mode;       /**< Обраний режим автоматики (наповнення чи відкачування) */
} liquid_level_config_t;

/**
 * @brief Поточні виміряні метрики та стан автоматики.
 */
typedef struct {
    uint16_t raw_adc;               /**< Останній миттєвий відлік АЦП */
    uint16_t peak_adc;              /**< Відфільтроване пікове значення АЦП */
    float    level_pct;             /**< Обчислений рівень рідини у відсотках (0.0% .. 100.0%) */

    bool     low_float_active;      /**< Стан нижнього поплавкового тумблера з антибрязкотом */
    bool     high_float_active;     /**< Стан верхнього поплавкового тумблера з антибрязкотом */

    pump_state_t pump_state;        /**< Поточний стан помпи */
    uint32_t pump_running_time_ms;  /**< Тривалість роботи помпи у поточному циклі (мс) */
    uint32_t last_fault_time_ms;    /**< Системний час останнього спрацьовування захисту (мс) */
} liquid_level_data_t;

/**
 * @brief Контекст екземпляра драйвера давача рівня.
 */
typedef struct {
    liquid_level_config_t config;   /**< Конфігураційні параметри */

    /* Внутрішній буфер цифровізації пікового значення */
    uint16_t adc_window[LIQUID_LEVEL_PEAK_WINDOW_MAX];
    uint8_t  window_head;
    uint8_t  window_count;

    /* Антибрязкот нижнього поплавкового GPIO */
    bool     raw_low_state;
    bool     debounced_low_state;
    uint32_t low_state_change_ms;

    /* Антибрязкот верхнього поплавкового GPIO */
    bool     raw_high_state;
    bool     debounced_high_state;
    uint32_t high_state_change_ms;

    /* Стан помпи та захисні таймери */
    pump_state_t pump_state;
    uint32_t pump_start_time_ms;
    float    initial_pump_level_pct;/**< Початковий рівень при запуску помпи для перевірки сухого ходу */
    uint32_t last_process_time_ms;

    liquid_level_data_t data;       /**< Публічна структура телеметрії */
    bool initialized;               /**< Прапорець завершення ініціалізації */
} liquid_level_t;

/**
 * @brief Ініціалізація драйвера давача рівня рідини.
 *
 * @param dev Вказівник на структуру контексту драйвера.
 * @param config Вказівник на конфігураційні параметри.
 * @return liquid_level_status_t Результат ініціалізації.
 */
liquid_level_status_t liquid_level_init(liquid_level_t *dev, const liquid_level_config_t *config);

/**
 * @brief Періодичний обробник опитання сигналів, фільтрації та безпеки помпи.
 *
 * @param dev Вказівник на контекст драйвера.
 * @param current_time_ms Поточний системний час у мілісекундах.
 * @return liquid_level_status_t Результат виконання чергового циклу.
 */
liquid_level_status_t liquid_level_process(liquid_level_t *dev, uint32_t current_time_ms);

/**
 * @brief Отримання копії поточних метрик та стану автоматики.
 *
 * @param dev Вказівник на контекст драйвера.
 * @param out_data Вказівник на структуру для збереження даних.
 * @return liquid_level_status_t Результат виконання.
 */
liquid_level_status_t liquid_level_get_data(const liquid_level_t *dev, liquid_level_data_t *out_data);

/**
 * @brief Скидання аварійного блокування помпи (після усунення причин сухого ходу чи перекачування).
 *
 * @param dev Вказівник на контекст драйвера.
 * @return liquid_level_status_t Результат виконання.
 */
liquid_level_status_t liquid_level_reset_fault(liquid_level_t *dev);

/**
 * @brief Зміна режиму роботи автоматики (наповнення / відкачування).
 *
 * @param dev Вказівник на контекст драйвера.
 * @param mode Новий режим роботи.
 * @return liquid_level_status_t Результат виконання.
 */
liquid_level_status_t liquid_level_set_mode(liquid_level_t *dev, liquid_level_mode_t mode);

#ifdef __cplusplus
}
#endif

#endif /* LIQUID_LEVEL_H */
