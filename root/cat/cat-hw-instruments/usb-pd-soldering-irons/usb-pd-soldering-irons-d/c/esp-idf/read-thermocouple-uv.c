// Приклад циклу ШІМ-керування та вимірювання температури у C (ESP-IDF)
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/adc.h"

#define PWM_HEATER_PIN   GPIO_NUM_18
#define THERMOCOUPLE_ADC ADC1_CHANNEL_6

// Опитування термопари під час паузи ШІМ
uint32_t read_thermocouple_uv(void) {
    // 1. Вимикаємо силовий MOSFET (пауза нагріву)
    gpio_set_level(PWM_HEATER_PIN, 0);
    
    // 2. Пауза 2 мс для спаду індуктивних завад та заспокоєння сигнальної лінії
    vTaskDelay(pdMS_TO_TICKS(2));
    
    // 3. Зчитування значення АЦП з виходу операційного підсилювача
    int raw_adc = adc1_get_raw(THERMOCOUPLE_ADC);
    
    // Перерахунок сирого значення АЦП у мікровольти (приблизний коефіцієнт)
    uint32_t voltage_uv = raw_adc * 805; // 3.3V / 4096 ≈ 805 uV на відлік
    return voltage_uv;
}

void heater_control_loop(void) {
    while (1) {
        uint32_t thermo_uv = read_thermocouple_uv();
        // Розрахунок температури: T = T_ref + (V_uv / K_thermocouple)
        float current_temp = 25.0f + (thermo_uv / 41.0f);
        
        // Вмикаємо нагрів на новий цикл ШІМ при потребі
        if (current_temp < 330.0f) {
            gpio_set_level(PWM_HEATER_PIN, 1);
        }
        vTaskDelay(pdMS_TO_TICKS(20)); // Період ШІМ 50 Гц
    }
}
