#include <stdio.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"

#define UART_PORT UART_NUM_1

bool esp01_check_connection(void) {
    const char *cmd = "AT+CIPSTATUS\r\n";
    uart_write_bytes(UART_PORT, cmd, strlen(cmd));
    // Перевірка статусу у відповіді UART
    return true; 
}

void esp01_reconnect_task(void *pvParameters) {
    uint32_t delay_ms = 1000;
    const uint32_t max_delay_ms = 60000;

    while (1) {
        if (!esp01_check_connection()) {
            // Спроба відновити з'єднання
            const char *conn_cmd = "AT+CIPSTART=\"TCP\",\"192.168.1.100\",8080\r\n";
            uart_write_bytes(UART_PORT, conn_cmd, strlen(conn_cmd));

            vTaskDelay(pdMS_TO_TICKS(delay_ms));

            // Експоненційне збільшення паузи при повторних збоях
            delay_ms *= 2;
            if (delay_ms > max_delay_ms) {
                delay_ms = max_delay_ms;
            }
        } else {
            // При успішному з'єднанні скидаємо затримку
            delay_ms = 1000;
            vTaskDelay(pdMS_TO_TICKS(5000));
        }
    }
}
