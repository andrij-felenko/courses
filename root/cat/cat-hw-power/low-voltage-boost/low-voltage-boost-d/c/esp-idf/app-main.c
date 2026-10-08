#include <stdio.h>
#include "esp_adc/adc_oneshot.h"
#include "driver/gpio.h"
#include "esp_log.h"

#define BATT_ADC_CHANNEL    ADC_CHANNEL_0
#define LOAD_ENABLE_GPIO    GPIO_NUM_18
#define MIN_BATT_VOLTAGE_MV 950  // Мінімальна допустима напруга батареї 0.95 В

static const char *TAG = "POWER_MGMT";

void app_main(void)
{
    // Налаштування GPIO для керування навантаженням
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << LOAD_ENABLE_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
    gpio_set_level(LOAD_ENABLE_GPIO, 0); // Навантаження вимкнено при старті

    // Ініціалізація АЦП для контролю батареї
    adc_oneshot_unit_handle_t adc_handle;
    adc_oneshot_unit_init_cfg_t init_config = {
        .unit_id = ADC_UNIT_1,
    };
    adc_oneshot_new_unit(&init_config, &adc_handle);

    adc_oneshot_chan_cfg_t config = {
        .bitwidth = ADC_BITWIDTH_DEFAULT,
        .atten = ADC_ATTEN_DB_12,
    };
    adc_oneshot_config_channel(adc_handle, BATT_ADC_CHANNEL, &config);

    int raw_val = 0;
    adc_oneshot_read(adc_handle, BATT_ADC_CHANNEL, &raw_val);
    
    // Перерахунок сирого значення АЦП у мілівольти
    int batt_voltage_mv = (raw_val * 3300) / 4095;
    ESP_LOGI(TAG, "Вхідна напруга батареї: %d мВ", batt_voltage_mv);

    if (batt_voltage_mv >= MIN_BATT_VOLTAGE_MV) {
        ESP_LOGI(TAG, "Напруга в нормі. Вмикаємо навантаження.");
        gpio_set_level(LOAD_ENABLE_GPIO, 1);
    } else {
        ESP_LOGW(TAG, "Напруга батареї занизька (%d мВ)! Навантаження заблоковано.", batt_voltage_mv);
    }
}
