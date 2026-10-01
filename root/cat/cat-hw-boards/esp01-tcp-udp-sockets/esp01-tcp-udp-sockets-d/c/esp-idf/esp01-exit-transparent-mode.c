#include <stdio.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"

#define UART_PORT_NUM UART_NUM_1

bool esp01_exit_transparent_mode(void) {
    // 1. Пауза Guard time перед +++ (щонайменше 1000 мс)
    vTaskDelay(pdMS_TO_TICKS(1050));

    // 2. Відправка послідовності +++ без \r\n
    const char *escape_seq = "+++";
    uart_write_bytes(UART_PORT_NUM, escape_seq, 3);

    // 3. Пауза Guard time після +++ (щонайменше 1000 мс)
    vTaskDelay(pdMS_TO_TICKS(1050));

    // 4. Перевірка командного режиму відправкою AT
    const char *test_cmd = "AT\r\n";
    uart_write_bytes(UART_PORT_NUM, test_cmd, 4);

    return true;
}
