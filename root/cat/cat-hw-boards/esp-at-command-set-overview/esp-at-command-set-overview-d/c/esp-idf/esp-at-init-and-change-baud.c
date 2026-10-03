// Ініціалізація та зміна швидкості UART для ESP-AT (C / ESP-IDF)
#include <stdio.h>
#include <string.h>
#include "driver/uart.h"

#define UART_NUM UART_NUM_1

void esp_at_init_and_change_baud(uint32_t new_baud) {
    // 1. Відключення ехо-режиму на початковій швидкості 115200
    const char *cmd_ate0 = "ATE0\r\n";
    uart_write_bytes(UART_NUM, cmd_ate0, strlen(cmd_ate0));
    
    // 2. Відправка команди тимчасової зміни швидкості (UART_CUR)
    char cmd_baud[64];
    snprintf(cmd_baud, sizeof(cmd_baud), "AT+UART_CUR=%lu,8,1,0,0\r\n", (unsigned long)new_baud);
    uart_write_bytes(UART_NUM, cmd_baud, strlen(cmd_baud));
    
    // Очікування передачі останнього байта перед переналаштуванням порту хоста
    uart_wait_tx_done(UART_NUM, pdMS_TO_TICKS(100));
    
    // 3. Переналаштування UART-периферії хост-мікроконтролера
    uart_set_baudrate(UART_NUM, new_baud);
    
    // 4. Перевірка зв'язку на новій швидкості
    const char *cmd_at = "AT\r\n";
    uart_write_bytes(UART_NUM, cmd_at, strlen(cmd_at));
}
