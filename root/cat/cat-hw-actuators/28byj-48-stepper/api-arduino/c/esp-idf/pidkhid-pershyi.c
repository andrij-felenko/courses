// 28BYJ-48 через ULN2003. ESP32, ESP-IDF. Готової бібліотеки нема — крок робимо
// самі: таблиця тактів плюс пауза між ними. IN1..IN4 — чотири звичайні GPIO.
#include "driver/gpio.h"
#include "esp_rom_sys.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define STEPS_PER_REV  2038            // кроків на оберт ВИХІДНОГО вала (не 2048)

static const gpio_num_t PINS[4] = {    // IN1, IN2, IN3, IN4 — у ФІЗИЧНОМУ порядку
    GPIO_NUM_16, GPIO_NUM_17, GPIO_NUM_18, GPIO_NUM_19 };

// Повнокрокова послідовність: у кожному такті ввімкнено дві сусідні фази.
// Чергування обмоток заховане в самій таблиці, тому переставляти піни (як в
// аргументах Stepper) тут не треба — це та сама послідовність, що її дає
// бібліотека при порядку 8, 10, 9, 11.
static const uint8_t FULL_STEP[4][4] = {
    {1, 1, 0, 0},
    {0, 1, 1, 0},
    {0, 0, 1, 1},
    {1, 0, 0, 1},
};

static int phase = 0;                  // на якому такті ми зараз

static void stepper_init(void) {
  gpio_config_t cfg = {
      .pin_bit_mask = (1ULL << PINS[0]) | (1ULL << PINS[1]) |
                      (1ULL << PINS[2]) | (1ULL << PINS[3]),
      .mode = GPIO_MODE_OUTPUT,
  };
  ESP_ERROR_CHECK(gpio_config(&cfg));
}

static void apply_phase(int p) {
  for (int i = 0; i < 4; i++) gpio_set_level(PINS[i], FULL_STEP[p][i]);
}

// Блокуючий рух на n кроків: знак задає напрям, step_us — пауза між тактами.
// Тік FreeRTOS (типово 10 мс) для такої паузи завеликий, тому чекаємо
// мікросекундами, а щоб довгий рух не голодив планувальник — раз на 64 кроки
// віддаємо йому квант.
static void stepper_step(int n, uint32_t step_us) {
  int dir = (n >= 0) ? 1 : -1;
  int total = n * dir;
  for (int i = 0; i < total; i++) {
    phase = (phase + dir + 4) % 4;
    apply_phase(phase);
    esp_rom_delay_us(step_us);
    if ((i & 63) == 63) vTaskDelay(1);
  }
}

void app_main(void) {
  stepper_init();
  while (1) {
    stepper_step( STEPS_PER_REV, 3000);   // оберт уперед; 3 мс/крок ≈ 10 об/хв
    vTaskDelay(pdMS_TO_TICKS(1000));
    stepper_step(-STEPS_PER_REV, 3000);   // оберт назад
    vTaskDelay(pdMS_TO_TICKS(1000));
  }
}
