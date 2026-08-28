#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "ky028";
#define LOAD_PIN    GPIO_NUM_2
#define AO_CHANNEL  ADC_CHANNEL_6            // GPIO34 — ADC1, працює й з Wi-Fi

// Пороги в одиницях (4095 - сире): БІЛЬШЕ = тепліше. Верхній > нижнього;
// зазор між ними — і є гістерезис. Підібрати під свою намистину.
#define WARM_ON     2560
#define WARM_OFF    2400

static adc_oneshot_unit_handle_t adc1;
static bool state = false;                   // true = навантаження ввімкнене
static int  warmS = 0;                       // згладжене значення (проти шуму АЦП)

static int read_warm(void) {
    int raw = 0;
    adc_oneshot_read(adc1, AO_CHANNEL, &raw);
    return 4095 - raw;                       // інвертуємо: більше = тепліше
}

void app_main(void) {
    gpio_config_t out = { .pin_bit_mask = 1ULL << LOAD_PIN, .mode = GPIO_MODE_OUTPUT };
    gpio_config(&out);

    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    adc_oneshot_new_unit(&unit, &adc1);
    adc_oneshot_chan_cfg_t ch = { .bitwidth = ADC_BITWIDTH_12,
                                  .atten    = ADC_ATTEN_DB_12 };
    adc_oneshot_config_channel(adc1, AO_CHANNEL, &ch);

    warmS = read_warm();                     // початкове наповнення фільтра

    while (1) {
        int warm = read_warm();
        warmS += (warm - warmS) / 4;         // проста згладжувальна ланка (шум АЦП)

        // Гістерезис ЗА РІВНЕМ: два різні пороги вгору й униз.
        if (!state && warmS >= WARM_ON) {            // вище верхнього → вмикаємо
            state = true;  gpio_set_level(LOAD_PIN, 1);
            ESP_LOGI(TAG, ">> ГАРЯЧЕ (warm вище верхнього порогу)");
        } else if (state && warmS <= WARM_OFF) {     // нижче нижнього → вимикаємо
            state = false; gpio_set_level(LOAD_PIN, 0);
            ESP_LOGI(TAG, "<< норма (warm нижче нижнього порогу)");
        }
        // у зоні WARM_OFF..WARM_ON стан НЕ міняється — тремтіння погашене

        ESP_LOGD(TAG, "warm = %d", warmS);           // для підбору порогів
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
