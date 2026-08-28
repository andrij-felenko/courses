#include "driver/ledc.h"
#include "esp_rom_sys.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_SEND 18          // GPIO, на якому висить S (через резистор)

// LEDC тримає несучу 38 кГц; вмикаємо й вимикаємо її шпаруватістю
static void carrier(bool on) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, on ? 85 : 0);  // ~1/3
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}
static void mark(int us)  { carrier(true);  esp_rom_delay_us(us); }
static void space(int us) { carrier(false); esp_rom_delay_us(us); }

static void send_nec(uint32_t frame) {       // 32 біти, молодшим уперед
    mark(9000); space(4500);                 // преамбула NEC
    for (int i = 0; i < 32; i++) {
        mark(560);
        space(((frame >> i) & 1) ? 1690 : 560);  // «1» — довга пауза, «0» — коротка
    }
    mark(560); carrier(false);               // завершальна пачка
}

void app_main(void) {
    ledc_timer_config_t t = { .speed_mode = LEDC_LOW_SPEED_MODE,
        .duty_resolution = LEDC_TIMER_8_BIT, .timer_num = LEDC_TIMER_0,
        .freq_hz = 38000, .clk_cfg = LEDC_AUTO_CLK };
    ledc_timer_config(&t);
    ledc_channel_config_t c = { .gpio_num = PIN_SEND, .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel = LEDC_CHANNEL_0, .timer_sel = LEDC_TIMER_0, .duty = 0, .hpoint = 0 };
    ledc_channel_config(&c);

    while (1) {
        send_nec(0xCB34FF00);    // адреса 0x00, команда 0x34 з інверсіями
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
