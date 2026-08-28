#include "driver/gpio.h"
#include "esp_timer.h"

#define SOL_PIN   GPIO_NUM_5
#define PULSE_MS  60

static bool     sol_on    = false;   // чи зараз соленоїд під струмом
static uint32_t sol_start = 0;       // мить увімкнення, мс

static uint32_t now_ms(void) { return (uint32_t)(esp_timer_get_time() / 1000); }

void solenoid_start(void) {          // почати клацання — не чекаючи його кінця
    gpio_set_level(SOL_PIN, 1);
    sol_on    = true;
    sol_start = now_ms();
}

void solenoid_update(void) {         // кликати щопрохід задачі: вимкне, коли настане час
    if (sol_on && (now_ms() - sol_start >= PULSE_MS)) {
        gpio_set_level(SOL_PIN, 0);
        sol_on = false;
    }
}

void app_main(void) {
    solenoid_init();
    while (1) {
        // ... читаємо кнопки, крутимо логіку, миготимо світлом ...
        if (button_pressed())
            solenoid_start();        // клац — і одразу далі, без застигання
        solenoid_update();           // а вимкнеться саме собою за 60 мс
        vTaskDelay(pdMS_TO_TICKS(1));  // задача не тримає ядро, соленоїд їй не заважає
    }
}
