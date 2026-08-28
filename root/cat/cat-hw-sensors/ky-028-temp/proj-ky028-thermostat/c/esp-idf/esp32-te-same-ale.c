// Те саме рідним ESP-IDF: DO на GPIO32 (не strapping), AO на GPIO34 (ADC1).
// Живлення KY-028 — від 3V3 ESP32! НЕ від 5V/VIN.
#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "ky028";
#define DO_PIN      GPIO_NUM_32
#define LOAD_PIN    GPIO_NUM_2               // тут вбудований LED; у бою — реле
#define AO_CHANNEL  ADC_CHANNEL_6            // GPIO34 = ADC1_CH6, безпечно з Wi-Fi

// 12-бітний АЦП (0..4095): БІЛЬШЕ (після інверсії) = тепліше.
#define WARM_ON   2560                       // підібрати під свою намистину
#define WARM_OFF  2400                       // зазор WARM_OFF..WARM_ON = гістерезис

static adc_oneshot_unit_handle_t adc1;
static int  rest_level = 1;                  // для читання DO як порогу
static bool state      = false;
static int  warmS      = 0;

static int read_warm(void) {
    int raw = 0;
    adc_oneshot_read(adc1, AO_CHANNEL, &raw);
    return 4095 - raw;                       // інверсія на 12 бітах
}

static int read_rest_level(void) {
    const int N = 15; int highs = 0;
    for (int i = 0; i < N; i++) { if (gpio_get_level(DO_PIN)) highs++;
                                  vTaskDelay(pdMS_TO_TICKS(5)); }
    return (highs > N / 2) ? 1 : 0;
}

void app_main(void) {
    gpio_config_t in = { .pin_bit_mask = 1ULL << DO_PIN, .mode = GPIO_MODE_INPUT,
                         .pull_up_en = GPIO_PULLUP_DISABLE,     // підтяжка є на модулі
                         .pull_down_en = GPIO_PULLDOWN_DISABLE,
                         .intr_type = GPIO_INTR_DISABLE };
    gpio_config(&in);
    gpio_config_t out = { .pin_bit_mask = 1ULL << LOAD_PIN, .mode = GPIO_MODE_OUTPUT };
    gpio_config(&out);

    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };   // саме ADC1
    adc_oneshot_new_unit(&unit, &adc1);
    adc_oneshot_chan_cfg_t ch = { .bitwidth = ADC_BITWIDTH_12,
                                  .atten    = ADC_ATTEN_DB_12 };    // ~0..3.1 В
    adc_oneshot_config_channel(adc1, AO_CHANNEL, &ch);

    vTaskDelay(pdMS_TO_TICKS(300));
    rest_level = read_rest_level();          // умова: на старті температура в НОРМІ
    warmS      = read_warm();
    ESP_LOGI(TAG, "Спокій DO = %s", rest_level ? "HIGH" : "LOW");

    while (1) {
        // Варіант А: рішення за рівнем AO (поріг задає код) — основний тут.
        warmS += (read_warm() - warmS) / 4;              // згладжування шуму АЦП

        if (!state && warmS >= WARM_ON) {
            state = true;  gpio_set_level(LOAD_PIN, 1);
            ESP_LOGI(TAG, ">> ГАРЯЧЕ (AO вище верхнього порогу)");
        } else if (state && warmS <= WARM_OFF) {
            state = false; gpio_set_level(LOAD_PIN, 0);
            ESP_LOGI(TAG, "<< норма (AO нижче нижнього порогу)");
        }

        // Варіант Б (за бажання): паралельно читати апаратний поріг гвинтика.
        // bool hw_hot = (gpio_get_level(DO_PIN) != rest_level);

        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
