#include "../include/rotary_dip_driver.h"
#include <stddef.h>

/* Внутрішній масив симуляції GPIO регістрів (4 порти по 32 ніжки) */
static uint32_t g_gpio_sim_ports[4] = {0};

uint8_t hal_gpio_read_pin(uint8_t port_id, uint8_t pin_index) {
    if (port_id >= 4 || pin_index >= 32) {
        return 0;
    }
    return (uint8_t)((g_gpio_sim_ports[port_id] >> pin_index) & 0x01);
}

void hal_gpio_write_pin(uint8_t port_id, uint8_t pin_index, uint8_t level) {
    if (port_id >= 4 || pin_index >= 32) {
        return;
    }
    if (level) {
        g_gpio_sim_ports[port_id] |= (1UL << pin_index);
    } else {
        g_gpio_sim_ports[port_id] &= ~(1UL << pin_index);
    }
}

bool rotary_dip_init(rotary_dip_t *handle, const rotary_dip_config_t *config) {
    if (handle == NULL || config == NULL) {
        return false;
    }

    handle->config = *config;
    handle->raw_code = 0;
    handle->decoded_value = 0;
    handle->is_valid = false;
    handle->last_read_timestamp = 0;

    return true;
}

uint8_t rotary_dip_gray_to_binary(uint8_t gray_val) {
    uint8_t mask = gray_val >> 1;
    uint8_t binary = gray_val;
    while (mask != 0) {
        binary ^= mask;
        mask >>= 1;
    }
    return binary & 0x0F;
}

bool rotary_dip_read(rotary_dip_t *handle, uint32_t current_time_ms) {
    if (handle == NULL) {
        return false;
    }

    /* Зчитування стану 4 бітових ліній з ізоляцією ніжок за маскою */
    uint8_t current_raw = 0;
    for (int i = 0; i < 4; i++) {
        uint8_t pin_state = hal_gpio_read_pin(handle->config.pins[i].port_id, 
                                             handle->config.pins[i].pin_index);
        
        /* У режимі PULL_UP замкнений контакт дає LOW (0), тому інвертуємо біт */
        uint8_t bit_val = 0;
        if (handle->config.pull_mode == ROTARY_DIP_PULL_UP) {
            bit_val = (pin_state == 0) ? 1 : 0;
        } else {
            bit_val = (pin_state != 0) ? 1 : 0;
        }

        current_raw |= (bit_val << i);
    }

    /* Програмний антидребезг: перевірка наївності зміни та тайм-ауту */
    if (current_raw != handle->raw_code) {
        if ((current_time_ms - handle->last_read_timestamp) < handle->config.debounce_ms) {
            /* Період антидребезгу ще не минув — ігноруємо нестабільні перехідні завади */
            return false;
        }
        handle->raw_code = current_raw;
        handle->last_read_timestamp = current_time_ms;
    }

    /* Декодування значення залежно від формату енкодера */
    switch (handle->config.encoding) {
        case ROTARY_DIP_ENCODING_BCD:
            if (handle->raw_code <= 9) {
                handle->decoded_value = handle->raw_code;
                handle->is_valid = true;
            } else {
                /* У BCD коді значення понад 9 вважається апаратною помилкою */
                handle->decoded_value = 0;
                handle->is_valid = false;
            }
            break;

        case ROTARY_DIP_ENCODING_HEX:
            handle->decoded_value = handle->raw_code & 0x0F;
            handle->is_valid = true;
            break;

        case ROTARY_DIP_ENCODING_GRAY:
            handle->decoded_value = rotary_dip_gray_to_binary(handle->raw_code);
            handle->is_valid = true;
            break;

        default:
            handle->is_valid = false;
            break;
    }

    return handle->is_valid;
}

uint8_t rotary_dip_get_modbus_address(const rotary_dip_t *handle, uint8_t base_address) {
    if (handle == NULL || !handle->is_valid) {
        return base_address;
    }
    return base_address + handle->decoded_value;
}

uint32_t rotary_dip_get_baudrate(const rotary_dip_t *handle) {
    static const uint32_t baudrate_lut[16] = {
        9600,   19200,  38400,  57600,
        115200, 230400, 460800, 921600,
        1200,   2400,   4800,   9600,
        19200,  38400,  57600,  115200
    };

    if (handle == NULL || !handle->is_valid) {
        return 9600; /* Резервна швидкість за замовчуванням */
    }

    return baudrate_lut[handle->decoded_value & 0x0F];
}
