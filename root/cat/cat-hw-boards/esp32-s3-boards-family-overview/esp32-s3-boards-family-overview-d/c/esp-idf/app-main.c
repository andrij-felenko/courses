#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_log.h"

static const char *TAG = "PERIPH_ROUTING";

void app_main(void) {
    // 1. Динамічна маршрутизація виводу UART1 TX на GPIO4 через GPIO Matrix
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_NUM_4),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
    esp_rom_gpio_connect_out_signal(GPIO_NUM_4, UART_PERIPH_SIGNAL(1, SOC_UART_TX_PIN_IDX), false, false);

    // 2. Ініціалізація ADC1 (GPIO1) - безпечний канал при активному Wi-Fi
    adc_oneshot_unit_handle_t adc1_handle;
    adc_oneshot_unit_init_cfg_t init_config1 = {
        .unit_id = ADC_UNIT_1,
        .clk_src = ADC_RTC_CLK_SRC_DEFAULT,
    };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_config1, &adc1_handle));

    adc_oneshot_chan_cfg_t config = {
        .bitwidth = ADC_BITWIDTH_DEFAULT,
        .atten = ADC_ATTEN_DB_12,
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_handle, ADC_CHANNEL_0, &config));

    int raw_adc_value = 0;
    ESP_ERROR_CHECK(adc_oneshot_read(adc1_handle, ADC_CHANNEL_0, &raw_adc_value));
    ESP_LOGI(TAG, "Прочитане значення ADC1 (GPIO1): %d", raw_adc_value);
}
