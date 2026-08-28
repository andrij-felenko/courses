#include <stdint.h>
#include <stdbool.h>

#define ESP32_GPIO_STRAP_REG_ADDR  0x3FF44038U

#define STRAP_MASK_BOOT_MODE       (1U << 0)
#define STRAP_MASK_UART_LOG        (1U << 1)
#define STRAP_MASK_SDIO_BOOT       (1U << 2)
#define STRAP_MASK_FLASH_1V8       (1U << 5)

typedef enum {
    STRAP_BOOT_SPI_FLASH   = 0,
    STRAP_BOOT_UART_ROM    = 1,
    STRAP_BOOT_SDIO_SLAVE  = 2,
    STRAP_BOOT_UNKNOWN     = 3
} Esp32BootMode;

typedef struct {
    uint32_t raw_register_value;
    Esp32BootMode boot_mode;
    bool is_flash_voltage_1v8;
    bool is_uart_log_active;
    bool is_hardware_safe;
} Esp32StrapReport;

Esp32StrapReport esp32_analyze_strapping_state(void) {
    volatile const uint32_t *strap_reg = (volatile const uint32_t *)ESP32_GPIO_STRAP_REG_ADDR;
    uint32_t raw = *strap_reg;
    
    Esp32StrapReport report;
    report.raw_register_value = raw;
    report.is_flash_voltage_1v8 = ((raw & STRAP_MASK_FLASH_1V8) != 0U);
    report.is_uart_log_active = ((raw & STRAP_MASK_UART_LOG) != 0U);

    bool gpio0 = ((raw & STRAP_MASK_BOOT_MODE) != 0U);
    bool gpio2 = ((raw & STRAP_MASK_SDIO_BOOT) != 0U);

    if (gpio0) {
        report.boot_mode = STRAP_BOOT_SPI_FLASH;
    } else if (!gpio2) {
        report.boot_mode = STRAP_BOOT_UART_ROM;
    } else {
        report.boot_mode = STRAP_BOOT_SDIO_SLAVE;
    }

    // Безпечним вважається лише запуск з Flash за нормальної напруги 3.3V
    report.is_hardware_safe = (report.boot_mode == STRAP_BOOT_SPI_FLASH) && (!report.is_flash_voltage_1v8);

    return report;
}
