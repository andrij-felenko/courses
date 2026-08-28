#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

while (1) {
    int v = 0;
    adc_oneshot_read(s_adc, PULSE_CH, &v);
    // ...обробка...
    vTaskDelay(pdMS_TO_TICKS(20));   // ніби 50 разів на секунду
}
