#ifndef HALL_GIMBAL_H
#define HALL_GIMBAL_H

#include <stdint.h>
#include <stdbool.h>

// Статуси помилок джойстика на сенсорах Холла
typedef enum {
    HALL_GIMBAL_OK = 0,
    HALL_GIMBAL_ERR_OUT_OF_RANGE = 1, // Вихід аналогового рівня за допустимі електричні межі (напр. обрив)
    HALL_GIMBAL_ERR_INVALID_CALIB = 2  // Некоректні калібрувальні дані (min >= center або center >= max)
} hall_gimbal_status_t;

// Структура калібрувальних параметрів для однієї осі
typedef struct {
    uint16_t min_raw;    // Мінімальне відлічене значення АЦП (у крайньому положенні)
    uint16_t center_raw; // Значення АЦП у нейтральному стані (спокій)
    uint16_t max_raw;    // Максимальне значення АЦП
} axis_calib_t;

// Конфігурація двоосьового джойстика
typedef struct {
    axis_calib_t axis_x;
    axis_calib_t axis_y;
    float deadzone_radial; // Відносна радіальна мертва зона (наприклад, 0.05 = 5%)
    float alpha_ema;       // Коефіцієнт згладжування EMA (0.0 < alpha <= 1.0)
} hall_gimbal_config_t;

// Результат обробки координат джойстика
typedef struct {
    float x;                 // Нормована координата X від -1.0 до +1.0
    float y;                 // Нормована координата Y від -1.0 до +1.0
    hall_gimbal_status_t status; // Статус обробки та діагностики
} hall_gimbal_output_t;

// Структура екземпляра джойстика
typedef struct {
    hall_gimbal_config_t config;
    float ema_x_raw;         // Відфільтроване значення АЦП для осі X
    float ema_y_raw;         // Відфільтроване значення АЦП для осі Y
    bool initialized;        // Прапор ініціалізації
} hall_gimbal_t;

// Ініціалізація модуля джойстика
hall_gimbal_status_t hall_gimbal_init(hall_gimbal_t *gimbal, const hall_gimbal_config_t *config);

// Обробка сирих відліків АЦП двох осей X та Y
hall_gimbal_output_t hall_gimbal_process(hall_gimbal_t *gimbal, uint16_t raw_x, uint16_t raw_y);

#endif // HALL_GIMBAL_H
