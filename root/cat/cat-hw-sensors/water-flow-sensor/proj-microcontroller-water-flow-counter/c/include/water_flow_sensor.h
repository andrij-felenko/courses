#ifndef WATER_FLOW_SENSOR_H
#define WATER_FLOW_SENSOR_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "ring_buffer.h"

/**
 * @file water_flow_sensor.h
 * @brief Інтерфейс низькорівневого C-драйвера давача витрати води (турбіна G1/2" + Холл).
 */

/**
 * @brief Структура конфігурації драйвера витратоміра.
 */
typedef struct {
    float k_factor;               /**< K-фактор давача (Гц на (л/хв)), для G1/2″ зазвичай 7.5 */
    uint32_t sample_period_ms;    /**< Період обчислення метрик у мілісекундах */
    float min_flow_cutoff_lpm;   /**< Поріг відсічення шумів (мінімальна витрата, л/хв) */
    uint8_t exti_gpio_pin;        /**< Номер виводу GPIO для зовнішніх переривань EXTI */
} water_flow_config_t;

/**
 * @brief Структура поточних виміряних метрик водоспоживання.
 */
typedef struct {
    float pulse_frequency_hz;     /**< Мобільне середнє частоти імпульсів (Гц) */
    float flow_rate_lpm;          /**< Миттєва витрата води у літрах за хвилину (л/хв) */
    double total_volume_liters;   /**< Сумарний накопичений об'єм пропущеної рідини (л) */
    uint64_t total_pulse_count;   /**< Загальна кількість підрахованих імпульсів */
    uint32_t last_update_ms;      /**< Часова мітка останнього перерахунку (мс) */
} water_flow_metrics_t;

/**
 * @brief Ініціалізація низькорівневого драйвера витрати води.
 * @param config Вказівник на конфігураційну структуру.
 * @return true у разі успішної ініціалізації.
 */
bool water_flow_sensor_init(const water_flow_config_t *config);

/**
 * @brief Обробник переривання EXTI (викликається з ISR при кожному фронті імпульсу Холла).
 * @param timestamp_us Поточний системний час у мікросекундах.
 */
void water_flow_sensor_on_pulse_isr(uint32_t timestamp_us);

/**
 * @brief Періодична обробка обчислень за таймером (викликається у неблокуючому циклі/таймері).
 * @param current_timestamp_ms Поточний системний час у мілісекундах.
 */
void water_flow_sensor_process_timer_tick(uint32_t current_timestamp_ms);

/**
 * @brief Отримання копії поточної структури метрик водоспоживання.
 * @param out_metrics Вказівник на структуру для запису метрик.
 */
void water_flow_sensor_get_metrics(water_flow_metrics_t *out_metrics);

/**
 * @brief Встановлення/відновлення накопиченого об'єму води та лічильника імпульсів.
 * @param total_liters Значення відновленого об'єму у літрах.
 * @param total_pulses Значення відновленого лічильника імпульсів.
 */
void water_flow_sensor_set_total_volume(double total_liters, uint64_t total_pulses);

/**
 * @brief Отримання вказівника на внутрішній кільцевий буфер імпульсів.
 * @return Вказівник на ring_buffer_t.
 */
ring_buffer_t* water_flow_sensor_get_ring_buffer(void);

#endif /* WATER_FLOW_SENSOR_H */
