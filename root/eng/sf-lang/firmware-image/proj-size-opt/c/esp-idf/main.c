#include "driver/gpio.h"
#include "esp_attr.h"
#include "esp_log.h"

// Велика таблиця тонів — читає лише DMA за покажчиком,
// статичного посилання з коду нема → gc-sections може вирізати!
// Атрибут __attribute__((used)) каже лінкеру: «лишити навіть без посилань»
static const uint16_t TONE_TABLE[] __attribute__((used)) = {
    261, 294, 330, 349, 392, 440, 494, 523
};

// Цю функцію кличе app_main() — статичне посилання видно лінкеру,
// gc-sections її не чіпає
static void play_tick(uint16_t freq) {
    // ... виводить частоту на таймер ...
    (void)freq;
}

// Обробник переривання: його адресу драйвер дістає під час виконання
// (gpio_isr_handler_add), статичного виклику з C-коду немає.
// Без __attribute__((used)) gc-sections може його вирізати!
static void IRAM_ATTR timer_isr(void *arg) __attribute__((used));
static void IRAM_ATTR timer_isr(void *arg) {
    // ... обслуговує переривання таймера ...
}

void app_main(void) {
    play_tick(TONE_TABLE[0]);   // ← статичне посилання: лінкер бачить, лишає
    ESP_LOGI("size", "живий");
}
