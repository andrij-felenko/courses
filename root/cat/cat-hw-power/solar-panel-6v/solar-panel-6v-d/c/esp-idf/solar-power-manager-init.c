#include "driver/adc.h"
#include "driver/gpio.h"
#include "esp_adc_cal.h"

#define SOLAR_ADC_CHANNEL  ADC1_CHANNEL_6 // GPIO34
#define POWER_GATE_GPIO    GPIO_NUM_25
#define SOLAR_V_MIN_MV     4600  // Поріг вимкнення навантаження (4.6 В)
#define SOLAR_V_HYST_MV    4900  // Поріг увімкнення навантаження (4.9 В)

static esp_adc_cal_characteristics_t adc_chars;

void solar_power_manager_init(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << POWER_GATE_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
    gpio_set_level(POWER_GATE_GPIO, 0);

    adc1_config_width(ADC_WIDTH_BIT_12);
    adc1_config_channel_atten(SOLAR_ADC_CHANNEL, ADC_ATTEN_DB_11);
    esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_11, ADC_WIDTH_BIT_12, 1100, &adc_chars);
}

void solar_power_manager_loop(void) {
    uint32_t adc_reading = adc1_get_raw(SOLAR_ADC_CHANNEL);
    uint32_t voltage_mv = esp_adc_cal_raw_to_voltage(adc_reading, &adc_chars) * 2; // Дільник 1:1

    static bool load_enabled = false;
    if (load_enabled && (voltage_mv < SOLAR_V_MIN_MV)) {
        load_enabled = false;
        gpio_set_level(POWER_GATE_GPIO, 0); // Вимикаємо навантаження для захисту панелі від завалу
    } else if (!load_enabled && (voltage_mv > SOLAR_V_HYST_MV)) {
        load_enabled = true;
        gpio_set_level(POWER_GATE_GPIO, 1);  // Дозволяємо роботу навантаження
    }
}
