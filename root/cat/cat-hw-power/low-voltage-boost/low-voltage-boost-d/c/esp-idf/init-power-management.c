#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"

#define BOOST_EN_PIN GPIO_NUM_4
#define BATT_ADC_CHANNEL ADC_CHANNEL_0

// Пороги напруги акумулятора (у мілівольтах)
#define UVLO_SHUTDOWN_THRESHOLD_MV 2700
#define UVLO_RECOVERY_THRESHOLD_MV 3000

static adc_oneshot_unit_handle_t adc_handle;

void init_power_management(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << BOOST_EN_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
    gpio_set_level(BOOST_EN_PIN, 1); // Увімкнути підвищувач за замовчуванням
}

void check_battery_voltage_and_protect(uint32_t battery_mv) {
    static bool power_enabled = true;
    
    if (power_enabled && (battery_mv < UVLO_SHUTDOWN_THRESHOLD_MV)) {
        // Напруга впала нижче критичної — вимикаємо підвищувач для захисту акумулятора
        gpio_set_level(BOOST_EN_PIN, 0);
        power_enabled = false;
    } else if (!power_enabled && (battery_mv > UVLO_RECOVERY_THRESHOLD_MV)) {
        // Напруга відновилася з гістерезисом — умикаємо підвищувач
        gpio_set_level(BOOST_EN_PIN, 1);
        power_enabled = true;
    }
}
