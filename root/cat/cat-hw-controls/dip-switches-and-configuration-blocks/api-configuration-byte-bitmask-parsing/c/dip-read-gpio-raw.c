#include <stdint.h>
#include <stdbool.h>

typedef struct {
    volatile uint32_t *gpio_in_reg;
    uint8_t  pin_shift;
    bool     active_low;
} dip_gpio_hw_config_t;

// Зчитування та нормалізація сирого байта з паралельних ліній GPIO
uint8_t dip_read_gpio_raw(const dip_gpio_hw_config_t *hw_cfg) {
    uint32_t port_val = *(hw_cfg->gpio_in_reg);
    uint8_t raw_byte = (uint8_t)((port_val >> hw_cfg->pin_shift) & 0xFF);
    return hw_cfg->active_low ? ((~raw_byte) & 0xFF) : raw_byte;
}
