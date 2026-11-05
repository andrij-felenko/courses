#include "mq7.h"
#include <math.h>

// Параметри для перерахунку коду АЦП у PPM (залежить від схеми підключення)
#define ADC_RESOLUTION   1024.0f
#define VOLTAGE_REF      5.0f
#define RL_RESISTANCE    10.0f // Опір навантажувального резистора (кОм)
#define RO_CALIBRATED    10.0f // Опір давача в чистому повітрі (потребує калібрування)

// Емпіричні коефіцієнти для апроксимації кривої CO з даташіта MQ-7
// Формула: ppm = 10 ^ ((log10(Rs/R0) - b) / m)
#define MQ7_CURVE_M      -0.77f
#define MQ7_CURVE_B      1.38f

void mq7_init(mq7_sensor_t *sensor) {
    sensor->state = MQ7_STATE_INIT;
    sensor->timer_start = 0;
    sensor->ppm = 0.0f;
    sensor->alarm_active = false;
}

// Перетворення сирого значення АЦП у рівень концентрації газу (ppm)
static float calculate_ppm(uint16_t adc_value) {
    if (adc_value == 0 || adc_value >= ADC_RESOLUTION - 1) {
        return 0.0f; // Захист від ділення на нуль
    }
    
    // Перетворення значення АЦП у напругу (Vrl)
    float v_rl = ((float)adc_value / ADC_RESOLUTION) * VOLTAGE_REF;
    
    // Обчислення опору сенсора (Rs) за дільником напруги
    float rs = ((VOLTAGE_REF - v_rl) / v_rl) * RL_RESISTANCE;
    
    // Обчислення співвідношення Rs/R0
    float ratio = rs / RO_CALIBRATED;
    if (ratio <= 0.0f) {
        return 0.0f;
    }
    
    // Обчислення ppm на основі логарифмічного рівняння
    float ppm = powf(10.0f, (log10f(ratio) - MQ7_CURVE_B) / MQ7_CURVE_M);
    return ppm;
}

bool mq7_update(mq7_sensor_t *sensor) {
    uint32_t current_time = hal_get_time_ms();
    bool new_measurement = false;

    switch (sensor->state) {
        case MQ7_STATE_INIT:
            // Старт фази очищення: нагрів при 5В
            hal_pwm_set_duty(MQ7_PWM_HIGH);
            sensor->timer_start = current_time;
            sensor->state = MQ7_STATE_HEATING_HIGH;
            break;

        case MQ7_STATE_HEATING_HIGH:
            // Чекаємо завершення 60 секунд високої температури
            if ((current_time - sensor->timer_start) >= MQ7_TIME_HIGH_MS) {
                // Перемикаємо напругу на 1.4В для фази вимірювання
                hal_pwm_set_duty(MQ7_PWM_LOW);
                sensor->timer_start = current_time;
                sensor->state = MQ7_STATE_HEATING_LOW;
            }
            break;

        case MQ7_STATE_HEATING_LOW:
            // Чекаємо завершення 90 секунд низької температури
            if ((current_time - sensor->timer_start) >= MQ7_TIME_LOW_MS) {
                // Наприкінці низькотемпературної фази газ найкраще адсорбується, робимо замір
                uint16_t adc_val = hal_adc_read();
                sensor->ppm = calculate_ppm(adc_val);
                
                // Перевірка порогу і керування бузером
                sensor->alarm_active = (sensor->ppm >= MQ7_ALARM_THRESHOLD_PPM);
                hal_buzzer_set(sensor->alarm_active);
                
                new_measurement = true;

                // Запускаємо новий цикл очищення (5В)
                hal_pwm_set_duty(MQ7_PWM_HIGH);
                sensor->timer_start = current_time;
                sensor->state = MQ7_STATE_HEATING_HIGH;
            }
            break;
    }

    return new_measurement;
}
