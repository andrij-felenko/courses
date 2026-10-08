#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_sleep.h"

#define SOLENOID_PIN GPIO_NUM_4
#define PULSE_DURATION_MS 35

// Подача одиночного імпульсу розблокування для здійснення одного кроку ескапменту
void step_escapement_pulse(void) {
    gpio_set_direction(SOLENOID_PIN, GPIO_MODE_OUTPUT);
    
    // Вмикаємо соленоїд для звільнення собачки ротора
    gpio_set_level(SOLENOID_PIN, 1);
    vTaskDelay(pdMS_TO_TICKS(PULSE_DURATION_MS));
    
    // Вимикаємо струм: механічний стопор фіксує ротор у наступному положенні
    gpio_set_level(SOLENOID_PIN, 0);
}

void app_main(void) {
    // Здійснюємо дискретний крок приводу
    step_escapement_pulse();
    
    // Переходимо у режим глибокого сну на 1 годину для збереження енергії
    const uint64_t sleep_time_us = 3600ULL * 1000000ULL;
    esp_deep_sleep(sleep_time_us);
}
