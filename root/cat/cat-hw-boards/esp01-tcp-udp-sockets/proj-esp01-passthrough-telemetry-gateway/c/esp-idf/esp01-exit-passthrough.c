// C (ESP-IDF): Автомат станів та керування прозорим шлюзом телеметрії ESP-01
#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"

typedef enum {
    GATEWAY_STATE_INIT,
    GATEWAY_STATE_CONNECT_SOCKET,
    GATEWAY_STATE_ENTER_PASSTHROUGH,
    GATEWAY_STATE_STREAMING,
    GATEWAY_STATE_RECOVERY
} gateway_state_t;

static const uart_port_t UART_PORT = UART_NUM_1;

// Виконання ескейп-послідовності виходу з прозорого режиму з витриманням таймаутів
bool esp01_exit_passthrough(void) {
    // 1. Витримуємо захисний інтервал тиші перед надсиланням (1050 мс)
    vTaskDelay(pdMS_TO_TICKS(1050));
    
    // 2. Відправляємо рівно три символи '+' без термінуючого рядка \r\n
    const char *escape_seq = "+++";
    uart_write_bytes(UART_PORT, escape_seq, 3);
    
    // 3. Витримуємо захисний інтервал тиші після надсилання (1050 мс)
    vTaskDelay(pdMS_TO_TICKS(1050));
    return true;
}

// Перевірка наявності асинхронного маркера розриву сокета в потоці UART RX
bool check_socket_closed(const uint8_t *buffer, size_t len) {
    if (len < 6) return false;
    return (strstr((const char *)buffer, "CLOSED") != NULL || 
            strstr((const char *)buffer, "WIFI DISCONNECT") != NULL);
}
