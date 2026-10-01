#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "uart.h"
#include "esp8266_reset.h"

/* Зсув та адреса зчитування структури rst_info у RTC пам'яті ESP8266 */
#define RTC_BOOT_INFO_ADDR 0x60000700

/**
 * Форматування числового значення у шістнадцятковий рядок для виводу в лог
 */
static void uart_print_hex(uint32_t val) {
    const char hex_chars[] = "0123456789ABCDEF";
    char buffer[11];
    buffer[0] = '0';
    buffer[1] = 'x';
    
    for (int i = 7; i >= 0; i--) {
        buffer[2 + (7 - i)] = hex_chars[(val >> (i * 4)) & 0xF];
    }
    buffer[10] = '\0';
    uart_send_string(buffer);
}

/**
 * Функція виведення текстового підтвердження причини скидання
 */
static void print_reset_reason(rst_reason_t reason) {
    switch (reason) {
        case REASON_DEFAULT_RST:
            uart_send_string("Power-ON Reset (Звичайне увімкнення)\n");
            break;
        case REASON_EXT_SYS_RST:
            uart_send_string("External Hardware Reset / DTR-RTS Auto-Reset (Апаратне скидання)\n");
            break;
        case REASON_WDT_RST:
            uart_send_string("Hardware Watchdog Reset (Спрацювання WDT)\n");
            break;
        case REASON_SOFT_RESTART:
            uart_send_string("Software Restart (Програмний перезапуск)\n");
            break;
        default:
            uart_send_string("Інша причина скидання (код: ");
            uart_print_hex((uint32_t)reason);
            uart_send_string(")\n");
            break;
    }
}

/**
 * Головна точка входу ініціалізації мікроконтролера (Non-OS SDK Entry point)
 */
void user_init(void) {
    /* Ініціалізація UART0 на стандартну швидкість 115200 бод */
    uart0_init(DEFAULT_BAUD_RATE);
    
    uart_send_string("\n=== ESP-01 Auto-Reset & Strapping Diagnostics ===\n");

    /* Опитування рівнів виводів GPIO0 та GPIO2 одразу при старті */
    bool gpio0_low = is_gpio0_low();
    bool gpio2_high = is_gpio2_high();

    uart_send_string("[GPIO] Стан конфігураційних виводів:\n");
    uart_send_string("  - GPIO0: ");
    uart_send_string(gpio0_low ? "LOW (0) -> Режим прошивання (UART Bootloader)\n" : "HIGH (1) -> Режим виконання (Flash Boot)\n");

    uart_send_string("  - GPIO2: ");
    uart_send_string(gpio2_high ? "HIGH (1) [OK]\n" : "LOW (0) [Помилка підтяжки!]\n");

    /* Зчитування структури rst_info з фіксованої адреси RTC-пам'яті */
    const rst_info_t *reset_info = (const rst_info_t *)RTC_BOOT_INFO_ADDR;
    
    uart_send_string("[RST] Причина перезавантаження: ");
    if (reset_info != NULL) {
        print_reset_reason(reset_info->reason);
        
        if (is_auto_reset_triggered(reset_info)) {
            uart_send_string("[DIAG] Успішно виявлено спрацьовування апаратного автомату автоскидання (DTR/RTS)!\n");
        }
    } else {
        uart_send_string("Інформація про скидання недоступна.\n");
    }

    uart_send_string("=== Діагностику завершено успішно ===\n\n");
}
