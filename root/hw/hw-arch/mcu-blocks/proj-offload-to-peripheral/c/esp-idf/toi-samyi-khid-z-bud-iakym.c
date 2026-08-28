#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static volatile bool tick = false;   // прапорець «настала мить» — ставить обробник

static void on_timer(void *arg) {    // обробник: коротко, лише підняти прапорець
  tick = true;
}

void app_main(void) {
  const esp_timer_create_args_t args = { .callback = &on_timer, .name = "tick" };
  esp_timer_handle_t t;
  esp_timer_create(&args, &t);
  esp_timer_start_periodic(t, 1000); // період у мікросекундах: 1000 мкс = 1 мс

  for (;;) {
    if (tick) {                      // ядро реагує, коли зручно, а відлік — залізний
      tick = false;
      // тут — робота строго раз на мілісекунду
    }
    vTaskDelay(1);                   // віддати процесор, поки події нема
  }
}
