// KY-009, спільний катод. ESP32, ESP-IDF. Логіка 3.3 В — резистори рахуй на 3.3!
#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_R  GPIO_NUM_25          // LEDC пускає ШІМ майже на будь-який GPIO
#define PIN_G  GPIO_NUM_26
#define PIN_B  GPIO_NUM_27

static const ledc_channel_t CH[3] = { LEDC_CHANNEL_0, LEDC_CHANNEL_1, LEDC_CHANNEL_2 };
static const int PINS[3] = { PIN_R, PIN_G, PIN_B };

static void leds_init(void) {
    ledc_timer_config_t tim = {                  // спільний таймер на всі три канали
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .timer_num       = LEDC_TIMER_0,
        .duty_resolution = LEDC_TIMER_8_BIT,     // 8 біт → 0…255, як звикли
        .freq_hz         = 5000,                 // 5 кГц — вище за поріг мерехтіння
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&tim));

    ledc_channel_config_t ch = {
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .timer_sel  = LEDC_TIMER_0,
        .intr_type  = LEDC_INTR_DISABLE,
        .duty = 0, .hpoint = 0,
    };
    for (int i = 0; i < 3; i++) {                // прив'язати кожен пін до свого каналу
        ch.channel = CH[i];
        ch.gpio_num = PINS[i];
        ESP_ERROR_CHECK(ledc_channel_config(&ch));
    }
}

// Єдиний шлюз кольору. Спільний катод: більше число → яскравіше.
static void set_color(uint8_t r, uint8_t g, uint8_t b) {
    const uint8_t v[3] = { r, g, b };
    for (int i = 0; i < 3; i++) {
        ledc_set_duty(LEDC_LOW_SPEED_MODE, CH[i], v[i]);
        ledc_update_duty(LEDC_LOW_SPEED_MODE, CH[i]);   // без цього нове значення не поїде
    }
}

void app_main(void) {
    leds_init();
    while (1) {
        set_color(255,   0,   0); vTaskDelay(pdMS_TO_TICKS(600));  // червоний
        set_color(  0, 255,   0); vTaskDelay(pdMS_TO_TICKS(600));  // зелений
        set_color(  0,   0, 255); vTaskDelay(pdMS_TO_TICKS(600));  // синій
        set_color(255, 255,   0); vTaskDelay(pdMS_TO_TICKS(600));  // жовтий
        set_color(255, 255, 255); vTaskDelay(pdMS_TO_TICKS(600));  // білий
    }
}
