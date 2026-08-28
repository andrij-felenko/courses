#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "led_strip.h"

#define WS2812_GPIO  8      // вбудований піксель ESP32-C6-Zero
#define WS2812_COUNT 1      // він один

static led_strip_handle_t strip;

static void ws2812_init(void)
{
    led_strip_config_t strip_cfg = {
        .strip_gpio_num = WS2812_GPIO,
        .max_leds = WS2812_COUNT,
        .led_model = LED_MODEL_WS2812,
        .color_component_format = LED_STRIP_COLOR_COMPONENT_FMT_GRB,
    };
    led_strip_rmt_config_t rmt_cfg = {
        .resolution_hz = 10 * 1000 * 1000,   // 10 МГц → 1 тік = 0.1 мкс
    };
    ESP_ERROR_CHECK(led_strip_new_rmt_device(&strip_cfg, &rmt_cfg, &strip));
    led_strip_clear(strip);                  // почати з погашеного
}

void app_main(void)
{
    ws2812_init();
    while (1) {
        led_strip_set_pixel(strip, 0, 0, 40, 0);  // піксель 0: R=0 G=40 B=0
        led_strip_refresh(strip);                  // тепер відправити в LED
        vTaskDelay(pdMS_TO_TICKS(400));

        led_strip_clear(strip);                    // погасити
        led_strip_refresh(strip);
        vTaskDelay(pdMS_TO_TICKS(400));
    }
}
