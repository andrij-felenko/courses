#include "esp_adc/adc_oneshot.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_rom_sys.h"
#include "esp_log.h"

#define A_CHAN   ADC_CHANNEL_6      // GPIO34 — аналоговий вихід 49E
#define D_GPIO   GPIO_NUM_25        // цифровий вихід компаратора (поріг гвинтика)
#define DEADBAND 16                 // мертва зона на 12-бітній шкалі
static const char *TAG = "hall";

static adc_oneshot_unit_handle_t adc;

static int read_averaged(int n) {   // трохи усереднити проти шуму
    long acc = 0;
    for (int i = 0; i < n; i++) {
        int raw;
        adc_oneshot_read(adc, A_CHAN, &raw);
        acc += raw;
        esp_rom_delay_us(200);
    }
    return (int)(acc / n);
}

void app_main(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    adc_oneshot_new_unit(&unit, &adc);
    adc_oneshot_chan_cfg_t ch = { .bitwidth = ADC_BITWIDTH_DEFAULT,
                                  .atten    = ADC_ATTEN_DB_12 };
    adc_oneshot_config_channel(adc, A_CHAN, &ch);

    gpio_config_t d = { .pin_bit_mask = 1ULL << D_GPIO, .mode = GPIO_MODE_INPUT };
    gpio_config(&d);

    vTaskDelay(pdMS_TO_TICKS(50));         // хай живлення й вихід 49E устояться
    int baseline = read_averaged(64);      // біля давача НЕ має бути магніту!
    ESP_LOGI(TAG, "baseline = %d", baseline);

    while (1) {
        int delta = read_averaged(8) - baseline;
        const char *pole = delta >  DEADBAND ? "N-бік"
                         : delta < -DEADBAND ? "S-бік" : "нема";
        // цифровий вихід D0 зазвичай активний у нулі
        ESP_LOGI(TAG, "поле: %d  (%s)%s", delta, pole,
                 gpio_get_level(D_GPIO) == 0 ? "   [поріг!]" : "");
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
