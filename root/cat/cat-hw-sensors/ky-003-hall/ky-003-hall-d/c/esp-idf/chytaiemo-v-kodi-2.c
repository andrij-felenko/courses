#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

#define A_CHAN  ADC_CHANNEL_6      // ADC1_CH6 — це GPIO34, аналоговий вихід 49E
#define D_PIN   GPIO_NUM_4         // цифровий вихід компаратора
static const char *TAG = "ky024";
static adc_oneshot_unit_handle_t adc1;

static int sample(void) {
    int v = 0;
    ESP_ERROR_CHECK(adc_oneshot_read(adc1, A_CHAN, &v));
    return v;                      // 0..4095
}

void app_main(void) {
    gpio_config_t d = { .pin_bit_mask = 1ULL << D_PIN, .mode = GPIO_MODE_INPUT,
                        .pull_up_en = GPIO_PULLUP_ENABLE };
    ESP_ERROR_CHECK(gpio_config(&d));

    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };   // ADC1 не свариться з Wi-Fi
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc1));
    adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, A_CHAN, &ch));

    long acc = 0;                  // ~0.6 с без магніту: тик FreeRTOS 10 мс, дрібнішої паузи нема
    for (int i = 0; i < 64; i++) { acc += sample(); vTaskDelay(pdMS_TO_TICKS(10)); }
    int baseline = acc / 64;       // нульова лінія ≈ половина шкали (12 біт: ≈2048)

    while (1) {
        int delta = sample() - baseline;   // >0 один полюс, <0 протилежний
        ESP_LOGI(TAG, "поле: %d %s%s", delta,
                 delta > 0 ? "(N-бік)" : (delta < 0 ? "(S-бік)" : "(нема)"),
                 gpio_get_level(D_PIN) == 0 ? " [поріг!]" : "");   // поріг гвинтика
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
