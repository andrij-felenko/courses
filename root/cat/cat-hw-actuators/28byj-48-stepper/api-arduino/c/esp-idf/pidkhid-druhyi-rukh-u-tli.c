// 28BYJ-48 через ULN2003, напівкроковий режим із розгоном. Крок робить
// одноразовий esp_timer, який після кожного кроку заводить сам себе на нову
// паузу, — це і є місцевий відповідник run(). app_main лишається вільним.
#include "driver/gpio.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define STEPS_PER_REV  4076            // напівкрок: удвічі більше кроків на оберт

static const gpio_num_t PINS[4] = {
    GPIO_NUM_16, GPIO_NUM_17, GPIO_NUM_18, GPIO_NUM_19 };

// Напівкрокова послідовність (8 тактів) у ФІЗИЧНОМУ порядку IN1..IN4 — та сама,
// що її дає AccelStepper::HALF4WIRE з пінами 8, 10, 9, 11.
static const uint8_t HALF_STEP[8][4] = {
    {1,0,0,0}, {1,1,0,0}, {0,1,0,0}, {0,1,1,0},
    {0,0,1,0}, {0,0,1,1}, {0,0,0,1}, {1,0,0,1},
};

static const float MAX_SPEED = 600.0f; // стеля, кроків/с
static const float ACCEL     = 500.0f; // прискорення, кроків/с²
static const float MIN_SPEED =  20.0f; // з якого темпу рушаємо

static esp_timer_handle_t tick;
static volatile long position = 0, target = 0;
static float speed = MIN_SPEED;
static int phase = 0;

static void apply_phase(int p) {
  for (int i = 0; i < 4; i++) gpio_set_level(PINS[i], HALF_STEP[p][i]);
}

static void step_cb(void *arg) {
  long togo = target - position;
  if (togo == 0) { speed = MIN_SPEED; return; }   // доїхали: себе не перезаводимо
  int dir = (togo > 0) ? 1 : -1;
  phase = (phase + dir + 8) & 7;
  apply_phase(phase);
  position += dir;

  // Гальмівний шлях із поточної швидкості — v²/(2a). Поки решти більше, розганяємось.
  float left = (float)(togo * dir - 1);
  float dt = 1.0f / speed;
  if (left <= speed * speed / (2.0f * ACCEL)) speed -= ACCEL * dt;
  else if (speed < MAX_SPEED)                 speed += ACCEL * dt;
  if (speed < MIN_SPEED) speed = MIN_SPEED;
  esp_timer_start_once(tick, (uint64_t)(1000000.0f / speed));   // заводимо себе знову
}

static void move_to(long p) {                     // абсолютна ціль у кроках
  target = p;
  if (position != target) esp_timer_start_once(tick, 1000);     // штовхаємо рух
}

void app_main(void) {
  gpio_config_t cfg = {
      .pin_bit_mask = (1ULL << PINS[0]) | (1ULL << PINS[1]) |
                      (1ULL << PINS[2]) | (1ULL << PINS[3]),
      .mode = GPIO_MODE_OUTPUT,
  };
  ESP_ERROR_CHECK(gpio_config(&cfg));
  const esp_timer_create_args_t args = { .callback = step_cb, .name = "step" };
  ESP_ERROR_CHECK(esp_timer_create(&args, &tick));

  move_to(STEPS_PER_REV);                         // ціль: один оберт уперед
  while (1) {                                     // цикл вільний: тут кнопка, дисплей…
    if (position == target) move_to(-position);   // доїхали — розвертаємось
    vTaskDelay(pdMS_TO_TICKS(50));
  }
}
