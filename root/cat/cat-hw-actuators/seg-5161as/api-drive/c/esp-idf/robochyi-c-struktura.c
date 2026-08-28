#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Виводи в тому самому порядку a,b,c,d,e,f,g,DP — тут це номери GPIO.
static const gpio_num_t SEG_PIN[8] = {
  GPIO_NUM_4,  GPIO_NUM_5,  GPIO_NUM_6,  GPIO_NUM_7,
  GPIO_NUM_15, GPIO_NUM_16, GPIO_NUM_17, GPIO_NUM_18,
};
static const bool COMMON_ANODE = false;   // 5161AS — спільний катод

// Замість pinMode у циклі — один опис одразу на всі вісім ніг.
static void seg_begin(void) {
  uint64_t pins = 0;
  for (int i = 0; i < 8; i++) pins |= 1ULL << SEG_PIN[i];
  gpio_config_t cfg = {
    .pin_bit_mask = pins,
    .mode         = GPIO_MODE_OUTPUT,
    .pull_up_en   = GPIO_PULLUP_DISABLE,
    .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type    = GPIO_INTR_DISABLE,
  };
  ESP_ERROR_CHECK(gpio_config(&cfg));
  for (int i = 0; i < 8; i++) gpio_set_level(SEG_PIN[i], COMMON_ANODE);
}

// Той самий єдиний рядок фізики: полярність вирішує рівень.
static void seg_show_mask(uint8_t mask) {
  for (int i = 0; i < 8; i++) {
    bool on = (mask >> i) & 1;
    gpio_set_level(SEG_PIN[i], COMMON_ANODE ? !on : on);
  }
}

static void seg_show_hex(uint8_t v, bool dot) {
  uint8_t m = FONT[v & 0x0F];
  if (dot) m |= SDP;
  seg_show_mask(m);
}

void app_main(void) {
  seg_begin();
  while (true) {
    for (uint8_t v = 0; v < 16; v++) {
      seg_show_hex(v, v == 10);
      vTaskDelay(pdMS_TO_TICKS(500));
    }
  }
}
