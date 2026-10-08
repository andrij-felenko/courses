#include "driver/gpio.h"
#include "driver/ledc.h"
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define HEATER_PWM_PIN GPIO_NUM_18
#define LEDC_DUTY_5V   1023  // 100% ШІМ при 5.0 В
#define LEDC_DUTY_1V4  286   // ~1.4 В від 5.0 В (286/1023)

void mq7_control_task(void *pvParameters) {
    adc_oneshot_unit_handle_t adc_handle = (adc_oneshot_unit_handle_t)pvParameters;
    int adc_raw = 0;

    while (1) {
        // Фаза 1: 5.0 В випалювання (60 с)
        ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, LEDC_DUTY_5V);
        ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
        vTaskDelay(pdMS_TO_TICKS(60000));

        // Фаза 2: 1.4 В вимірювання (90 с)
        ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, LEDC_DUTY_1V4);
        ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);

        // Пауза 85 с до термічної стабілізації
        vTaskDelay(pdMS_TO_TICKS(85000));

        // Зчитування сигналу наприкінці фази
        adc_oneshot_read(adc_handle, ADC_CHANNEL_0, &adc_raw);

        // Залишок фази (5 с)
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
