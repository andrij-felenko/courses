#include "user_interface.h"
#include "osapi.h"
#include "driver/uart.h"

// Користувацький обробник символьного виведення
static void custom_log_char(char c) {
    // Друк символу у послідовний порт UART0
    uart_tx_one_char(UART0, c);
}

void configure_system_logging(bool enable_logging) {
    if (enable_logging) {
        // Реєстрація власної функції друку та увімкнення логів SDK
        ets_install_putc1((void *)custom_log_char);
        system_set_os_print(1);
    } else {
        // Повне пригнічення системного логування SDK
        system_set_os_print(0);
    }
}
