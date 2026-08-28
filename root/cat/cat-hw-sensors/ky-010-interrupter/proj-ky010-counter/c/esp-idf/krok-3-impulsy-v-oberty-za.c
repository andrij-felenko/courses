#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_S      GPIO_NUM_4
#define N_SLOTS    20
#define GUARD_US   800
#define WINDOW_MS  1000               // вікно вимірювання, мс
#define BLOCKED    1                  // з калібрування
static const char *TAG = "ky010";

static volatile uint32_t pulses   = 0;
static volatile int64_t  lastEdge = 0;

static void IRAM_ATTR on_edge(void *arg) {
  int64_t t = esp_timer_get_time();
  if (t - lastEdge >= GUARD_US) { pulses++; lastEdge = t; }
}

void app_main(void) {
  gpio_config_t cfg = {
    .pin_bit_mask = 1ULL << PIN_S,
    .mode         = GPIO_MODE_INPUT,
    .intr_type    = BLOCKED ? GPIO_INTR_POSEDGE : GPIO_INTR_NEGEDGE,
  };
  ESP_ERROR_CHECK(gpio_config(&cfg));
  ESP_ERROR_CHECK(gpio_install_isr_service(0));
  ESP_ERROR_CHECK(gpio_isr_handler_add(PIN_S, on_edge, NULL));

  uint32_t pPrev = 0;
  int64_t  tWin  = esp_timer_get_time();
  while (1) {
    vTaskDelay(pdMS_TO_TICKS(WINDOW_MS));
    int64_t now = esp_timer_get_time();
    float dt = (now - tWin) / 1e6f;    // фактичний час вікна, с
    tWin = now;

    uint32_t p  = pulses;
    uint32_t dp = p - pPrev;           // приріст імпульсів за вікно
    pPrev = p;

    // об/хв = 60 · dp / (N · dt);  dt тут у секундах
    ESP_LOGI(TAG, "швидкість: %.0f об/хв", 60.0f * dp / (N_SLOTS * dt));
  }
}
