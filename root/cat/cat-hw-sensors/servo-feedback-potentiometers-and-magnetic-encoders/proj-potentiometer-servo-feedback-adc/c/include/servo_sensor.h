#ifndef SERVO_SENSOR_H
#define SERVO_SENSOR_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "adc_hal.h"

/**
 * @brief Структура кільцевого буфера для обчислення ковзного середнього (Moving Average Filter).
 * Оптимізована для обчислення плинної суми за час O(1).
 */
typedef struct {
    float *buffer;        /**< Зовнішній або внутрішній масив пам'яті для вікна N вибірок */
    size_t capacity;      /**< Розмір вікна фільтра (кількість елементів N) */
    size_t head;          /**< Поточний індекс запису у кільцевому буфері */
    size_t count;         /**< Поточна кількість збережених вибірок у процесі накопичення */
    double running_sum;   /**< Плинна сума елементів буфера для виконання обчислень за O(1) */
} ring_buffer_t;

/**
 * @brief Структура експоненціального фільтра згладжування (EMA - Exponential Moving Average).
 * Формула: y_k = alpha * x_k + (1 - alpha) * y_{k-1}
 */
typedef struct {
    float alpha;          /**< Коефіцієнт згладжування (0.0 < alpha <= 1.0) */
    float filtered_val;   /**< Накопичене відфільтроване значення y_{k-1} */
    bool initialized;     /**< Прапорець первинного заповнення фільтра */
} ema_filter_t;

/**
 * @brief Структура калібрувальних параметрів та мертвих зон серводетчика.
 */
typedef struct {
    uint16_t adc_cal_zero;     /**< Калібрувальний код АЦП для нульового кута (Zero Calibration) */
    uint16_t adc_cal_span;     /**< Калібрувальний код АЦП для максимального кута (Span Calibration) */
    uint16_t adc_deadband_low; /**< Нижня межа програмного відсікання мертвої зони */
    uint16_t adc_deadband_high;/**< Верхня межа програмного відсікання мертвої зони */
    float angle_zero_deg;      /**< Фізичний кут повороту для adc_cal_zero (наприклад, 0.0°) */
    float angle_span_deg;      /**< Фізичний кут повороту для adc_cal_span (наприклад, 180.0°) */
    bool is_calibrated;        /**< Прапорець завершення процедури дворівневого калібрування */
} sensor_calib_t;

/**
 * @brief Головний дескриптор датчика кутового положення сервоприводу.
 */
typedef struct {
    adc_handle_t *adc_handle;  /**< Вказівник на апаратний драйвер АЦП */
    ring_buffer_t ring_buf;    /**< Екземпляр кільцевого буфера для ковзного середнього */
    ema_filter_t ema;          /**< Екземпляр експоненціального фільтра EMA */
    sensor_calib_t calib;      /**< Налаштування дворівневого калібрування та мертвих зон */
    uint16_t last_raw_adc;     /**< Останнє зчитане сире значення з АЦП */
    float last_filtered_adc;   /**< Значення АЦП після двокаскадної фільтрації */
    float current_angle_deg;   /**< Обчислений очищений фізичний кут у градусах */
} servo_sensor_t;

/**
 * @brief Ініціалізація кільцевого буфера ковзного середнього.
 * 
 * @param rb Вказівник на структуру кільцевого буфера.
 * @param storage_array Зовнішній масив пам'яті для елементів буфера.
 * @param capacity Розмір масиву (кількість вибірок у вікні).
 */
void ring_buffer_init(ring_buffer_t *rb, float *storage_array, size_t capacity);

/**
 * @brief Додавання нової вибірки у кільцевий буфер та обчислення середнього значення за O(1).
 * 
 * @param rb Вказівник на кільцевий буфер.
 * @param sample Нове цифрове значення з АЦП.
 * @return float Оновлене ковзне середнє значення.
 */
float ring_buffer_update(ring_buffer_t *rb, float sample);

/**
 * @brief Ініціалізація експоненціального фільтра (EMA).
 * 
 * @param ema Вказівник на структуру EMA фільтра.
 * @param alpha Коефіцієнт згладжування (0 < alpha <= 1.0).
 */
void ema_filter_init(ema_filter_t *ema, float alpha);

/**
 * @brief Оновлення експоненціального фільтра новою вибіркою.
 * 
 * @param ema Вказівник на структуру EMA фільтра.
 * @param input Новий вхідний сигнал.
 * @return float Згладжений вихідний сигнал y_k.
 */
float ema_filter_update(ema_filter_t *ema, float input);

/**
 * @brief Ініціалізація основного модуля датчика кута сервоприводу.
 * 
 * @param sensor Вказівник на дескриптор датчика.
 * @param adc_handle Вказівник на апаратний модуль АЦП.
 * @param rb_storage Вказівник на буфер пам'яті для ковзного середнього.
 * @param rb_capacity Кількість вибірок у кільцевому буфері.
 * @param ema_alpha Коефіцієнт фільтра EMA.
 */
void servo_sensor_init(servo_sensor_t *sensor, adc_handle_t *adc_handle, 
                      float *rb_storage, size_t rb_capacity, float ema_alpha);

/**
 * @brief Виконання дворівневого калібрування (Zero/Span Calibration) з налаштуванням мертвих зон.
 * 
 * @param sensor Вказівник на датчик сервоприводу.
 * @param raw_zero Кодування АЦП для нульового фізичного кута.
 * @param angle_zero Фізичний кут Zero у градусах (наприклад, 0.0°).
 * @param raw_span Кодування АЦП для кінцевого фізичного кута.
 * @param angle_span Фізичний кут Span у градусах (наприклад, 180.0° або 270.0°).
 * @param deadband_margin_codes Запас мертвої зони у відрахунках АЦП біля країв ходу.
 * @return true Якщо параметри калібрування коректні, false у разі помилки.
 */
bool servo_sensor_calibrate(servo_sensor_t *sensor, uint16_t raw_zero, float angle_zero,
                            uint16_t raw_span, float angle_span, uint16_t deadband_margin_codes);

/**
 * @brief Програмне відсікання нелінійних мертвих зон на крайніх межах механічного ходу.
 * 
 * @param calib Вказівник на структуру калібрувальних параметрів.
 * @param raw_adc Сирий код АЦП.
 * @return uint16_t Код АЦП з обмеженням у робочому коридорі.
 */
uint16_t servo_sensor_apply_deadband(const sensor_calib_t *calib, uint16_t raw_adc);

/**
 * @brief Лінійне мапування відфільтрованого кодування АЦП у фізичний кут повороту.
 * 
 * @param calib Вказівник на структуру калібрування.
 * @param filtered_adc Відфільтрований сигнал АЦП.
 * @return float Фізичний кут повороту в градусах.
 */
float servo_sensor_map_adc_to_angle(const sensor_calib_t *calib, float filtered_adc);

/**
 * @brief Повний цикл зчитування, двохрівневої фільтрації, відсікання мертвих зон та розрахунку кута.
 * 
 * @param sensor Вказівник на датчик сервоприводу.
 * @return float Поточний очищений фізичний кут повороту у градусах.
 */
float servo_sensor_read_angle(servo_sensor_t *sensor);

#endif /* SERVO_SENSOR_H */
