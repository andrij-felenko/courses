#include "esp8266_boot_pins.h"
#include <stdio.h>

// Симуляція регістрів GPIO для сумісності з автономним середовищем виконання
static uint32_t simulated_gpio_in_reg = GPIO_PIN_0_BIT | GPIO_PIN_2_BIT; // За замовчуванням SPI Flash boot (GPIO0=1, GPIO2=1, GPIO15=0)
static uint32_t simulated_gpio_enable_reg = 0;
static uint32_t simulated_gpio_out_reg = 0;

// Отримання актуального значення з вхідного регістра GPIO_IN
static uint32_t get_hardware_gpio_in(void) {
#if defined(ESP8266) || defined(ARDUINO_ARCH_ESP8266)
    return REG_READ(ESP8266_GPIO_IN_REG);
#else
    return simulated_gpio_in_reg;
#endif
}

void esp8266_boot_pins_default_config(boot_pins_config_t *config) {
    if (config == NULL) {
        return;
    }
    config->enable_internal_pullups = true;
    config->strict_flash_check = true;
    config->sample_count = 5;
}

boot_mode_t esp8266_decode_boot_mode(bool gpio15, bool gpio0, bool gpio2) {
    // Якщо GPIO15 на рівні HIGH (1), мікроконтролер переходить у режим SDIO boot
    if (gpio15) {
        return BOOT_MODE_SDIO;
    }

    // Якщо GPIO15 = 0, але GPIO2 на рівні LOW (0), це недопустимий режим (bootloop)
    if (!gpio2) {
        return BOOT_MODE_INVALID;
    }

    // При GPIO15 = 0 та GPIO2 = 1 стан GPIO0 визначає Flash boot або UART mode
    if (gpio0) {
        return BOOT_MODE_FLASH;
    } else {
        return BOOT_MODE_UART;
    }
}

boot_pins_status_t esp8266_read_boot_pins(const boot_pins_config_t *config) {
    boot_pins_config_t local_cfg;
    if (config == NULL) {
        esp8266_boot_pins_default_config(&local_cfg);
    } else {
        local_cfg = *config;
    }

    if (local_cfg.sample_count == 0) {
        local_cfg.sample_count = 1;
    }

    uint32_t raw_val = 0;

    // Опитування регістра з фіксацією останнього стабільного значення
    for (uint32_t i = 0; i < local_cfg.sample_count; ++i) {
        raw_val = get_hardware_gpio_in();
    }

    boot_pins_status_t status;
    status.raw_gpio_in = raw_val;
    status.gpio0_level = (raw_val & GPIO_PIN_0_BIT) != 0;
    status.gpio2_level = (raw_val & GPIO_PIN_2_BIT) != 0;
    status.gpio15_level = (raw_val & GPIO_PIN_15_BIT) != 0;

    status.mode = esp8266_decode_boot_mode(status.gpio15_level, status.gpio0_level, status.gpio2_level);

    return status;
}

const char* esp8266_boot_mode_to_str(boot_mode_t mode) {
    switch (mode) {
        case BOOT_MODE_FLASH:
            return "SPI Flash Boot (Нормальний запуск із флеш-пам'яті)";
        case BOOT_MODE_UART:
            return "UART Download Mode (Режим програмування через послідовний порт)";
        case BOOT_MODE_SDIO:
            return "SDIO Boot Mode (Завантаження з SD-карти)";
        case BOOT_MODE_INVALID:
        default:
            return "INVALID / Boot Error (Некоректна підтяжка виводів, ризик циклічних перезавантажень)";
    }
}

bool esp8266_reconfigure_pin_safe(uint8_t pin, bool is_output, bool initial_level) {
    uint32_t pin_bit = 0;

    switch (pin) {
        case 0:
            pin_bit = GPIO_PIN_0_BIT;
            break;
        case 2:
            pin_bit = GPIO_PIN_2_BIT;
            break;
        case 15:
            pin_bit = GPIO_PIN_15_BIT;
            break;
        default:
            return false;
    }

#if defined(ESP8266) || defined(ARDUINO_ARCH_ESP8266)
    uint32_t enable_reg = REG_READ(ESP8266_GPIO_ENABLE_REG);
    uint32_t out_reg = REG_READ(ESP8266_GPIO_OUT_REG);

    if (is_output) {
        if (initial_level) {
            out_reg |= pin_bit;
        } else {
            out_reg &= ~pin_bit;
        }
        enable_reg |= pin_bit;
    } else {
        enable_reg &= ~pin_bit;
    }

    REG_WRITE(ESP8266_GPIO_OUT_REG, out_reg);
    REG_WRITE(ESP8266_GPIO_ENABLE_REG, enable_reg);
#else
    if (is_output) {
        if (initial_level) {
            simulated_gpio_out_reg |= pin_bit;
        } else {
            simulated_gpio_out_reg &= ~pin_bit;
        }
        simulated_gpio_enable_reg |= pin_bit;
    } else {
        simulated_gpio_enable_reg &= ~pin_bit;
    }
#endif

    return true;
}
