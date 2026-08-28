#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_S    GPIO_NUM_4       // будь-який GPIO вміє переривання
#define N_SLOTS  20               // прорізів на диску
static const char *TAG = "ky010";

static volatile uint32_t pulses = 0;   // лічильник; його чіпає ISR → volatile

static void IRAM_ATTR on_edge(void *arg) {   // ISR в IRAM: коротка, без логів
  pulses++;
}

void app_main(void) {
  gpio_config_t cfg = {
    .pin_bit_mask = 1ULL << PIN_S,
    .mode         = GPIO_MODE_INPUT,
    .pull_up_en   = GPIO_PULLUP_DISABLE,
    .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type    = GPIO_INTR_POSEDGE,       // передній фронт
  };
  ESP_ERROR_CHECK(gpio_config(&cfg));
  ESP_ERROR_CHECK(gpio_install_isr_service(0));
  ESP_ERROR_CHECK(gpio_isr_handler_add(PIN_S, on_edge, NULL));

  while (1) {
    vTaskDelay(pdMS_TO_TICKS(1000));         // раз на секунду знімаємо зріз
    uint32_t p = pulses;                     // 32 біти читаються атомарно
    ESP_LOGI(TAG, "обертів усього: %u", (unsigned)(p / N_SLOTS));
  }
}
