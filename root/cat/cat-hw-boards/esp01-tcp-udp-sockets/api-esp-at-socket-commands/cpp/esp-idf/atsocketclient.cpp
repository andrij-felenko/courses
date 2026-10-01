#include <iostream>
#include <string_view>
#include <cstdio>
#include "driver/uart.h"
#include "esp_log.h"

class AtSocketClient {
    uart_port_t uart_num;
public:
    explicit AtSocketClient(uart_port_t port) : uart_num(port) {}

    void send_payload(uint8_t link_id, std::string_view data) const {
        char cmd_buf[32];
        int cmd_len = std::snprintf(cmd_buf, sizeof(cmd_buf), "AT+CIPSEND=%u,%zu\r\n", 
                                    link_id, data.size());
        
        uart_write_bytes(uart_num, cmd_buf, cmd_len);
        vTaskDelay(pdMS_TO_TICKS(50));
        uart_write_bytes(uart_num, data.data(), data.size());
    }
};
