#include "dip_switch.h"

// Симуляція фізичного стану ліній GPIO для демонстраційного приладу
// У реальній мікроконтролерній системі замінюється на виклик драйвера GPIO (наприклад, gpio_get_level чи digitalRead)
static uint8_t simulated_gpio_pins = 0xEA;

void dip_switch_set_simulated_pins(uint8_t pins_state) {
    simulated_gpio_pins = pins_state;
}

static bool read_gpio_pin(uint8_t pin_number) {
    // Повертає 0 при замкненому важелі (GND) та 1 при розімкненому (Pull-Up)
    return (simulated_gpio_pins & (1 << (pin_number % 8))) != 0;
}

void dip_switch_init(const dip_switch_config_t *config) {
    if (!config) return;
    
    for (uint8_t i = 0; i < config->pin_count && i < DIP_SWITCH_MAX_PINS; i++) {
        // У мікроконтролері тут виконується апаратне налаштування піна:
        // gpio_set_direction(config->pin_numbers[i], GPIO_MODE_INPUT);
        // gpio_set_pull_mode(config->pin_numbers[i], GPIO_PULLUP_ONLY);
        (void)config->pin_numbers[i];
    }
}

uint8_t dip_switch_read_raw_byte(const dip_switch_config_t *config) {
    if (!config) return 0;
    
    uint8_t raw_val = 0;
    for (uint8_t i = 0; i < config->pin_count && i < DIP_SWITCH_MAX_PINS; i++) {
        if (read_gpio_pin(config->pin_numbers[i])) {
            raw_val |= (1 << i);
        }
    }
    return raw_val;
}

void dip_switch_decode(const dip_switch_config_t *config, uint8_t raw_byte, dip_switch_data_t *out_data) {
    if (!config || !out_data) return;
    
    out_data->raw_pins_state = raw_byte;
    
    // Оскільки увімкнений важіль DIP-перемикача замикає лінію на GND (Active Low),
    // застосовуємо побітову інверсію для отримання прямої логіки (1 - увімкнений важіль ON)
    uint8_t mask = (1 << config->pin_count) - 1;
    out_data->config_byte = (~raw_byte) & mask;
    
    // Виділення поля адреси: побітове маскування та зсув
    out_data->device_address = (out_data->config_byte & config->address_mask) >> config->address_shift;
    
    // Виділення полів режимів роботи: побітове маскування та зсув
    out_data->mode_flags = (out_data->config_byte & config->mode_mask) >> config->mode_shift;
    
    out_data->is_valid = true;
}

bool dip_switch_read_stable(const dip_switch_config_t *config, dip_switch_data_t *out_data) {
    if (!config || !out_data) return false;
    
    uint8_t samples = config->debounce_samples;
    if (samples == 0) samples = 1;
    
    uint8_t first_read = dip_switch_read_raw_byte(config);
    
    for (uint8_t i = 1; i < samples; i++) {
        uint8_t current_read = dip_switch_read_raw_byte(config);
        if (current_read != first_read) {
            // Зчитані значення не збігаються (перехідний стан або брязкіт контактів)
            out_data->is_valid = false;
            return false;
        }
    }
    
    dip_switch_decode(config, first_read, out_data);
    return true;
}
