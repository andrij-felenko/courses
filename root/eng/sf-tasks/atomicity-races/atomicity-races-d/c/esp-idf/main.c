#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;
static volatile uint32_t pulses = 0;   // volatile — свіжість значення

static void IRAM_ATTR on_pulse(void *arg) {   // обробник лише рахує
    portENTER_CRITICAL_ISR(&mux);
    pulses++;
    portEXIT_CRITICAL_ISR(&mux);
}

void pulse_task(void *arg) {
    while (1) {
        portENTER_CRITICAL(&mux);      // ← критична секція: цілісно (й проти 2-го ядра)
        uint32_t n = pulses;           //   «знімок» спільних даних
        pulses = 0;
        portEXIT_CRITICAL(&mux);       // ← переривання знову ввімкнені
        // ... далі працюємо з локальним n, поза секцією ...
        ESP_LOGI("pulse", "%u", (unsigned) n);   // повільний лог — НЕ в секції
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
