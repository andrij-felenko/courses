#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"

// Зміна швидкості UART хоста та ESP8266 у C
esp_err_t change_esp_baudrate(uart_port_t uart_num, uint32_t new_baud) {
    char cmd[64];
    snprintf(cmd, sizeof(cmd), "AT+UART_CUR=%" PRIu32 ",8,1,0,0\r\n", new_baud);
    
    // 1. Надсилання команди зміни швидкості
    uart_write_bytes(uart_num, cmd, strlen(cmd));
    
    // 2. Очікування виходу кадру зі старого FIFO (пауза 20 мс)
    vTaskDelay(pdMS_TO_TICKS(20));
    
    // 3. Зміна швидкості периферійного контролера UART ESP-IDF
    esp_err_t err = uart_set_baudrate(uart_num, new_baud);
    if (err != ESP_OK) {
        return err;
    }
    
    // 4. Перевірка зв'язку на новій швидкості
    const char *ping = "AT\r\n";
    uart_write_bytes(uart_num, ping, strlen(ping));
    
    return ESP_OK;
}
