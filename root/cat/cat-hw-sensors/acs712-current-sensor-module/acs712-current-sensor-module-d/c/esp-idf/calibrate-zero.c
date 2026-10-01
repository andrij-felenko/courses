#include <stdio.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/adc.h"

#define ADC_CHANNEL       ADC1_CHANNEL_6 // Вхід GPIO34
#define VREF              3.3f           // Опорна напруга ESP32 (В)
#define ADC_MAX           4095.0f        // 12-бітний АЦП
#define SENSITIVITY       0.185f         // Чутливість 185 мВ/А (версія 5A)
#define SAMPLES_COUNT     400            // Кількість вибірок за 20 мс (50 Гц)

static float zero_voltage = 1.65f;       // Очікуваний нуль VCC/2 для 3.3В

void calibrate_zero(void) {
    uint32_t sum = 0;
    for (int i = 0; i < 500; i++) {
        sum += adc1_get_raw(ADC_CHANNEL);
        vTaskDelay(pdMS_TO_TICKS(1));
    }
    float avg_raw = (float)sum / 500.0f;
    zero_voltage = (avg_raw * VREF) / ADC_MAX;
}

float calculate_ac_rms(void) {
    float sum_squares = 0.0f;
    for (int i = 0; i < SAMPLES_COUNT; i++) {
        int raw = adc1_get_raw(ADC_CHANNEL);
        float voltage = ((float)raw * VREF) / ADC_MAX;
        float current = (voltage - zero_voltage) / SENSITIVITY;
        sum_squares += current * current;
        esp_rom_delay_us(50); // Крок між вибірками ~50 мкс
    }
    return sqrtf(sum_squares / (float)SAMPLES_COUNT);
}
