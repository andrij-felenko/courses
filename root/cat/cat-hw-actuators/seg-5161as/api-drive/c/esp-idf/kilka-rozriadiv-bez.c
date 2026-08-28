#include "esp_timer.h"

// 4 розряди: спільні сегменти вже налаштовані в seg_begin(), тут — вибір розряду.
static const gpio_num_t DIGIT[4] = { GPIO_NUM_1, GPIO_NUM_2, GPIO_NUM_3, GPIO_NUM_8 };
static uint8_t frame[4] = { 0, 0, 0, 0 };

// Один розряд за виклик; таймер кличе кожні 2 мс → ~125 Гц на всі 4.
static void multiplex_step(void *arg) {
  static int d = 0;
  for (int i = 0; i < 4; i++) gpio_set_level(DIGIT[i], 1);   // згасити все
  seg_show_mask(frame[d]);                                   // маска розряду
  gpio_set_level(DIGIT[d], 0);                               // катод на землю
  d = (d + 1) & 3;
}

static void multiplex_begin(void) {
  gpio_config_t cfg = {
    .pin_bit_mask = (1ULL << DIGIT[0]) | (1ULL << DIGIT[1])
                  | (1ULL << DIGIT[2]) | (1ULL << DIGIT[3]),
    .mode = GPIO_MODE_OUTPUT, .pull_up_en = GPIO_PULLUP_DISABLE,
    .pull_down_en = GPIO_PULLDOWN_DISABLE, .intr_type = GPIO_INTR_DISABLE,
  };
  ESP_ERROR_CHECK(gpio_config(&cfg));
  for (int i = 0; i < 4; i++) gpio_set_level(DIGIT[i], 1);   // усі згашені

  const esp_timer_create_args_t a = { .callback = multiplex_step, .name = "mux" };
  esp_timer_handle_t h;
  ESP_ERROR_CHECK(esp_timer_create(&a, &h));
  ESP_ERROR_CHECK(esp_timer_start_periodic(h, 2000));        // період у мкс
}

static void set_number(int n) {
  for (int d = 3; d >= 0; d--) { frame[d] = FONT[n % 10]; n /= 10; }
}

void app_main(void) {
  seg_begin();
  multiplex_begin();
  set_number(1234);                   // далі перемальовує таймер
}
