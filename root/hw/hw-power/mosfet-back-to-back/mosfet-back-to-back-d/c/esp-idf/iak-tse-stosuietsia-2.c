// Те саме на ESP-IDF: два звичайні виходи — два незалежні дозволи на одну лінію.
#include "driver/gpio.h"

void power_path_init(void) {
    gpio_config_t io = {
        .pin_bit_mask = (1ULL << FET_CHG_EN) | (1ULL << FET_DSG_EN),
        .mode = GPIO_MODE_OUTPUT,
    };
    ESP_ERROR_CHECK(gpio_config(&io));
}

void power_path(bool allow_charge, bool allow_discharge) {
    gpio_set_level(FET_CHG_EN, allow_charge    ? 1 : 0);    // канал напряму «заряд»
    gpio_set_level(FET_DSG_EN, allow_discharge ? 1 : 0);    // канал напряму «розряд»
    // обидва 0 → лінія розірвана в обидва боки (body-діоди назустріч)
    // обидва 1 → провід в обидва боки (2·Rds(on))
}
