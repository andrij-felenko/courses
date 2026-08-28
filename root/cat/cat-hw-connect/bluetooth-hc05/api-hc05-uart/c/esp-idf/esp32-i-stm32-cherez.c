// Те саме на чистому ESP-IDF: драйвер UART2, ніжки задаються явно.
#include "driver/uart.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define BT_UART   UART_NUM_2
#define PIN_TXD   17          // → RXD модуля (обидва 3.3 В, дільник НЕ потрібен)
#define PIN_RXD   16          // ← TXD модуля
#define BUF_SIZE  1024

void bt_uart_init(int baud) {
    const uart_config_t cfg = {
        .baud_rate  = baud,                      // робоча швидкість модуля
        .data_bits  = UART_DATA_8_BITS,          // 8 біт даних…
        .parity     = UART_PARITY_DISABLE,       // …без парності…
        .stop_bits  = UART_STOP_BITS_1,          // …1 стоп-біт — це і є 8N1
        .flow_ctrl  = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };
    ESP_ERROR_CHECK(uart_driver_install(BT_UART, BUF_SIZE, 0, 0, NULL, 0));
    ESP_ERROR_CHECK(uart_param_config(BT_UART, &cfg));
    // порядок аргументів: (порт, TX, RX, RTS, CTS)
    ESP_ERROR_CHECK(uart_set_pin(BT_UART, PIN_TXD, PIN_RXD,
                                 UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));
}

// модуль → лог; зустрічний напрям тут дає сама консоль ESP-IDF
void bt_bridge_task(void *arg) {
    uint8_t b;
    for (;;) {
        if (uart_read_bytes(BT_UART, &b, 1, pdMS_TO_TICKS(20)) == 1) putchar(b);
    }
}
