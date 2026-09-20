#ifndef RVDT_DRIVER_H
#define RVDT_DRIVER_H

#include <stdint.h>
#include <stdbool.h>

// Прапори статусу та діагностики помилок RVDT
typedef enum {
    RVDT_OK               = 0x00, // Помилок немає
    RVDT_ERR_OPEN_CIRCUIT = 0x01, // Обрив обмотки (сума напруг нижче порогу)
    RVDT_ERR_SHORT_CIRCUIT= 0x02, // Коротке замикання (сума напруг вище порогу)
    RVDT_ERR_OUT_OF_RANGE = 0x04  // Вихід кута за допустимий діапазон (+-45 град)
} rvdt_error_t;

// Конфігурація драйвера RVDT
typedef struct {
    float max_angle_deg;     // Максимальний робочий кут (напр. 40.0 град)
    float sensitivity_v_v_deg;// Чутливість (напр. 0.025 В/В/град)
    float zero_offset_deg;   // Програмний зсув нуля в градусах
    float min_sum_voltage_v; // Мінімальна сумарна напруга (поріг обриву, напр. 0.5 В)
    float max_sum_voltage_v; // Максимальна сумарна напруга (поріг КЗ, напр. 15.0 В)
    float alpha_filter;      // Коефіцієнт ФНЧ (0.0..1.0, напр. 0.2)
} rvdt_config_t;

// Стан драйвера RVDT
typedef struct {
    float raw_angle_deg;     // Обчислений сирий кут
    float filtered_angle_deg;// Відфільтрований кут
    float v_s1;              // Напруга вторинної обмотки 1 (В)
    float v_s2;              // Напруга вторинної обмотки 2 (В)
    float sum_voltage;       // Сумарна напруга V_S1 + V_S2 (В)
    float diff_voltage;      // Різницева напруга V_S1 - V_S2 (В)
    rvdt_error_t error;      // Прапори помилок
} rvdt_state_t;

// Конструктор/ініціалізація драйвера RVDT
void rvdt_init(rvdt_state_t *state, const rvdt_config_t *config);

// Обробка вибірки АЦП та раціометричне обчислення кута
rvdt_error_t rvdt_process_sample(rvdt_state_t *state, const rvdt_config_t *config, float v_s1, float v_s2);

// Калібрування механічного нуля в поточному положенні
void rvdt_calibrate_zero(rvdt_state_t *state, rvdt_config_t *config);

#endif // RVDT_DRIVER_H
