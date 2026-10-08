/**
 * @file tcrt5000.h
 * @brief Драйвер масиву інфрачервоних відбивальних оптичних давачів TCRT5000.
 *
 * Описує структури конфігурації, калібрування, обробки сигналів АЦП/GPIO,
 * алгоритм розрахунку зваженої позиції лінії та обчислення моторного керування.
 */

#ifndef TCRT5000_H
#define TCRT5000_H

#include "mcu_gpio_adc.h"

#ifdef __cplusplus
extern "C" {
#endif

/** Максимальна кількість сенсорів у планарному масиві */
#define TCRT5000_MAX_SENSORS 8

/** Крок позиційної ваги між сусідніми сенсорами */
#define TCRT5000_WEIGHT_STEP 1000

/** Верхня межа нормованого значення відбиття (0 = білий фон, 1000 = чорна лінія) */
#define TCRT5000_CALIB_SCALE 1000

/** Мінімальна сума відбиття для визначення наявності лінії під масивом */
#define TCRT5000_MIN_LINE_SUM 150

/**
 * @brief Статуси виконання функцій драйвера TCRT5000
 */
typedef enum {
    TCRT5000_OK = 0,                          /**< Операція успішна */
    TCRT5000_ERROR_NULL_POINTER = -1,         /**< Передано нульовий вказівник */
    TCRT5000_ERROR_INVALID_PARAM = -2,        /**< Некоректні параметри конфігурації */
    TCRT5000_ERROR_HAL = -3,                  /**< Помилка апаратного рівня (GPIO/АЦП) */
    TCRT5000_ERROR_NOT_CALIBRATED = -4,       /**< Масив давачів не відкалібровано */
    TCRT5000_WARN_LINE_LOST = 1               /**< Лінію втрачено (сума відбиття нижча порогу) */
} tcrt5000_status_t;

/**
 * @brief Конфігурація масиву давачів TCRT5000
 */
typedef struct {
    uint8_t sensor_count;                            /**< Кількість активних давачів у лінійці (1..TCRT5000_MAX_SENSORS) */
    adc_channel_t adc_channels[TCRT5000_MAX_SENSORS];/**< Канали АЦП для аналогових виходів */
    gpio_pin_t gpio_pins[TCRT5000_MAX_SENSORS];      /**< Піни GPIO для цифрових виходів (компаратори LM393) */
    bool use_analog;                                 /**< Прапор використання аналогових каналів АЦП */
    uint8_t adc_oversample;                          /**< Кількість усреднюваних вибірок АЦП (наприклад, 4) */
} tcrt5000_config_t;

/**
 * @brief Структура калібрувальних коефіцієнтів сенсорів
 */
typedef struct {
    uint16_t min_raw[TCRT5000_MAX_SENSORS];   /**< Мінімальні сирі показання АЦП (біла поверхня) */
    uint16_t max_raw[TCRT5000_MAX_SENSORS];   /**< Максимальні сирі показання АЦП (чорна лінія) */
    bool is_calibrated;                       /**< Прапор завершеного калібрування */
} tcrt5000_calibration_t;

/**
 * @brief Результат зчитування та розрахунку позиції
 */
typedef struct {
    uint16_t raw_adc[TCRT5000_MAX_SENSORS];       /**< Сирі вибірки з АЦП */
    bool digital_bits[TCRT5000_MAX_SENSORS];     /**< Дискретні логічні рівні з GPIO */
    uint16_t normalized[TCRT5000_MAX_SENSORS];   /**< Нормовані значення (0..1000) */
    int32_t line_position;                        /**< Зважена позиція лінії в умовних одиницях */
    int32_t center_position;                      /**< Еталонний центр масиву давачів */
    int32_t position_error;                       /**< Помилка відхилення (line_position - center_position) */
    bool line_detected;                           /**< Ознака наявності лінії під масивом */
} tcrt5000_reading_t;

/**
 * @brief Параметри PD-регулятора для обчислення корекції моторів
 */
typedef struct {
    float kp;             /**< Пропорційний коефіцієнт */
    float kd;             /**< Диференціальний коефіцієнт */
    int32_t last_error;   /**< Попередня помилка для розрахунку похідної */
    int16_t base_speed;   /**< Базова швидкість руху робота (PWM/RPM) */
    int16_t max_speed;    /**< Максимальне обмеження швидкості моторів */
} tcrt5000_pd_controller_t;

/**
 * @brief Згенеровані вихідні керуючі сигнали для драйвера моторів
 */
typedef struct {
    int16_t left_motor_speed;   /**< Швидкість лівого мотора */
    int16_t right_motor_speed;  /**< Швидкість правого мотора */
} tcrt5000_motor_speed_t;

/**
 * @brief Ініціалізація периферії для масиву TCRT5000.
 * @param config Вказівник на конфігурацію.
 * @return TCRT5000_OK у разі успіху.
 */
tcrt5000_status_t tcrt5000_init(const tcrt5000_config_t *config);

/**
 * @brief Скидання калібрувальних коефіцієнтів у початковий стан.
 * @param calib Вказівник на структуру калібрування.
 * @param sensor_count Кількість давачів.
 * @return TCRT5000_OK у разі успіху.
 */
tcrt5000_status_t tcrt5000_calibration_reset(tcrt5000_calibration_t *calib, uint8_t sensor_count);

/**
 * @brief Накопичення екстремумів АЦП під час проведення давача над поверхнями.
 * @param config Вказівник на конфігурацію.
 * @param calib Вказівник на структуру калібрування.
 * @return TCRT5000_OK у разі успіху.
 */
tcrt5000_status_t tcrt5000_calibration_update(const tcrt5000_config_t *config,
                                               tcrt5000_calibration_t *calib);

/**
 * @brief Фіналізація калібрування з перевіркою коректності діапазонів.
 * @param calib Вказівник на структуру калібрування.
 * @param sensor_count Кількість давачів.
 * @return TCRT5000_OK у разі успіху.
 */
tcrt5000_status_t tcrt5000_calibration_finalize(tcrt5000_calibration_t *calib, uint8_t sensor_count);

/**
 * @brief Дискретне зчитування логічних виходів компараторів LM393.
 * @param config Вказівник на конфігурацію.
 * @param reading Вказівник на структуру результату.
 * @return TCRT5000_OK у разі успіху.
 */
tcrt5000_status_t tcrt5000_read_digital(const tcrt5000_config_t *config,
                                        tcrt5000_reading_t *reading);

/**
 * @brief Повний аналоговий цикл: вибірка АЦП, нормування, розрахунок зваженого середнього та помилки.
 * @param config Вказівник на конфігурацію.
 * @param calib Вказівник на відкалібровані межі.
 * @param reading Вказівник на структуру результату.
 * @return TCRT5000_OK або TCRT5000_WARN_LINE_LOST.
 */
tcrt5000_status_t tcrt5000_read_analog(const tcrt5000_config_t *config,
                                       const tcrt5000_calibration_t *calib,
                                       tcrt5000_reading_t *reading);

/**
 * @brief Розрахунок зваженої позиції лінії (Weighted Average) за нормованими показаннями.
 *
 * Формула: Pos = SUM(i * step * val[i]) / SUM(val[i])
 *
 * @param normalized Масив нормованих відбивань (0..1000).
 * @param count Кількість давачів.
 * @param out_line_detected Вихідна ознака наявності лінії під масивом.
 * @return Обчислена позиція лінії в діапазоні [0, (count-1)*1000].
 */
int32_t tcrt5000_calculate_weighted_position(const uint16_t *normalized,
                                             uint8_t count,
                                             bool *out_line_detected);

/**
 * @brief Обчислення скоригованих швидкостей моторів на основі помилки позиції.
 * @param pd Вказівник на стан PD-регулятора.
 * @param position_error Відхилення від центрального значення.
 * @param speeds Вказівник на результати регулювання.
 * @return TCRT5000_OK у разі успіху.
 */
tcrt5000_status_t tcrt5000_compute_motor_speeds(tcrt5000_pd_controller_t *pd,
                                                int32_t position_error,
                                                tcrt5000_motor_speed_t *speeds);

#ifdef __cplusplus
}
#endif

#endif /* TCRT5000_H */
