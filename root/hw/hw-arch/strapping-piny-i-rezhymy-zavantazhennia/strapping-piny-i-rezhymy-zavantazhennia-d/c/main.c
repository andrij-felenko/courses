#include <stdint.h>
#include <stdbool.h>

#define ESP32_GPIO_STRAP_REG  (*(volatile const uint32_t *)0x3FF44038U)

#define STRAP_BIT_BOOT_MODE   (1U << 0)
#define STRAP_BIT_FLASH_1V8   (1U << 5)

typedef enum {
    BOOT_HEALTH_OK = 0,
    BOOT_ERR_DOWNLOAD_MODE_LATCHED = 1,
    BOOT_ERR_CRITICAL_FLASH_VOLTAGE = 2
} BootHealthStatus;

BootHealthStatus verify_system_strapping_health(void) {
    uint32_t strap_val = ESP32_GPIO_STRAP_REG;

    // Перевірка 1: Чи не зафіксовано небезпечну напругу Flash 1.8V на GPIO12
    if ((strap_val & STRAP_BIT_FLASH_1V8) != 0U) {
        return BOOT_ERR_CRITICAL_FLASH_VOLTAGE;
    }

    // Перевірка 2: Чи завантажилися ми у нормальному режимі SPI Flash (GPIO0 == 1)
    if ((strap_val & STRAP_BIT_BOOT_MODE) == 0U) {
        return BOOT_ERR_DOWNLOAD_MODE_LATCHED;
    }

    return BOOT_HEALTH_OK;
}
