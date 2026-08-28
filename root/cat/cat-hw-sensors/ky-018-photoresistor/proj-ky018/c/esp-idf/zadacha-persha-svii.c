#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define LDR_CHAN  ADC_CHANNEL_6    // GPIO34 — канал блоку ADC1

static adc_oneshot_unit_handle_t adc1;
static int raw_min = 4095;   // «перевернуті» межі, щоб перший же відлік їх стягнув
static int raw_max = 0;

static void calibrate(uint16_t seconds) {
  TickType_t until = xTaskGetTickCount() + pdMS_TO_TICKS(seconds * 1000);
  while (xTaskGetTickCount() < until) {
    int v = 0;
    ESP_ERROR_CHECK(adc_oneshot_read(adc1, LDR_CHAN, &v));
    if (v < raw_min) raw_min = v;  // побачили темніше — опустили дно
    if (v > raw_max) raw_max = v;  // побачили світліше — підняли стелю
    vTaskDelay(pdMS_TO_TICKS(5));
  }
}
