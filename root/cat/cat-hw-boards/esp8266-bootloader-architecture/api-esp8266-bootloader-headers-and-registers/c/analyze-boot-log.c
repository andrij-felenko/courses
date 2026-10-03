#include <stdint.h>
#include <stdbool.h>

/* Структура розшифрованих параметрів старту */
typedef struct {
    uint8_t reset_reason;  /* Код rst cause (1: Power-on, 2: External, 4: WDT) */
    uint8_t gpio_boot_val; /* Перша цифра кортежу boot mode */
    bool is_flash_boot;    /* Прапор нормального запуску з SPI Flash */
} boot_diagnostic_t;

/* Декодування стартового логу UART0 */
boot_diagnostic_t analyze_boot_log(uint8_t rst_cause, uint8_t boot_mode_x) {
    boot_diagnostic_t diag;
    diag.reset_reason = rst_cause;
    diag.gpio_boot_val = boot_mode_x;
    /* Режим 3 означає нормальне зчитування з флеш-пам'яті (GPIO15=0, GPIO0=1, GPIO2=1) */
    diag.is_flash_boot = (boot_mode_x == 3);
    return diag;
}
