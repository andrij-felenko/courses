#include <stdio.h>
#include <string.h>
#include "driver/uart.h"
#include "esp_log.h"

static const char *TAG = "AT_GPIO";

void send_at_cmd(const char* cmd) {
    uart_write_bytes(UART_NUM_1, cmd, strlen(cmd));
    uart_write_bytes(UART_NUM_1, "\r\n", 2);
    ESP_LOGI(TAG, "Надіслано команду: %s", cmd);
}

void configure_and_read_gpio(void) {
    // Налаштування GPIO4 на вихід та GPIO5 на вхід
    send_at_cmd("AT+IOSETCFG=4,1,0");
    send_at_cmd("AT+GPIOWRITE=4,1");
    send_at_cmd("AT+IOSETCFG=5,0,1");
    send_at_cmd("AT+GPIOREAD=5");
}
