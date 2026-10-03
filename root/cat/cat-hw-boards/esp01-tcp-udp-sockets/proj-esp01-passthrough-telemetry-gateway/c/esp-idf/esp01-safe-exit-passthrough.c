// C (ESP-IDF): Алгоритм автовідновлення сесії та витримання guard time для ESP-01
#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"

#define UART_PORT_NUM      UART_NUM_1
#define GUARD_TIME_MS      1050

typedef enum {
    GATEWAY_STATE_STREAMING,
    GATEWAY_STATE_EXIT_ESCAPE,
    GATEWAY_STATE_RECONNECT_SOCKET,
    GATEWAY_STATE_HARD_RESET
} gateway_fsm_state_t;

// Виконання ескейп-послідовності +++ із дотриманням захисних інтервалів
bool esp01_safe_exit_passthrough(void) {
    // Пауза тиші перед +++ (Guard Time pre-pause)
    vTaskDelay(pdMS_TO_TICKS(GUARD_TIME_MS));
    
    // Передача трьох символів без \r\n
    uart_write_bytes(UART_PORT_NUM, "+++", 3);
    
    // Пауза тиші після +++ (Guard Time post-pause)
    vTaskDelay(pdMS_TO_TICKS(GUARD_TIME_MS));
    return true;
}

// Потоковий аналіз вхідних подій розриву з'єднання
bool esp01_detect_disconnect(const char *rx_buf, size_t buf_len) {
    if (buf_len == 0 || rx_buf == NULL) return false;
    return (strstr(rx_buf, "CLOSED") != NULL || strstr(rx_buf, "WIFI DISCONNECT") != NULL);
}
