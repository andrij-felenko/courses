#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define STEP_MS 15                        // темп: 15 мс на градус

static volatile int cur_angle = 90;       // де серво зараз (наша модель)
static volatile int tgt_angle = 90;       // куди хочемо

void servo_set_target(int deg) {          // задати нову ціль (миттєво повертається)
  if (deg < 0)   deg = 0;
  if (deg > 180) deg = 180;
  tgt_angle = deg;
}

static void servo_task(void *arg) {       // окрема задача: 1 крок за прокидання
  TickType_t last = xTaskGetTickCount();
  for (;;) {
    if (cur_angle != tgt_angle) {
      cur_angle += (tgt_angle > cur_angle) ? 1 : -1;   // один градус у бік цілі
      servo_write_us(deg_to_us(cur_angle));
    }
    vTaskDelayUntil(&last, pdMS_TO_TICKS(STEP_MS));    // рівний темп, без дрейфу
  }
}

void app_main(void) {
  servo_init();
  servo_write_us(deg_to_us(cur_angle));
  xTaskCreate(servo_task, "servo", 2048, NULL, 5, NULL);
  // ...решта задач вільно робить будь-що: кнопки, давачі, зв'язок...
  // будь-коли й звідки завгодно: servo_set_target(deg) — рух почнеться сам
}
