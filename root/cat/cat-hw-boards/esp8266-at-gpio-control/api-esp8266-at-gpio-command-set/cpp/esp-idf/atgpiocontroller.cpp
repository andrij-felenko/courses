#include <iostream>
#include <string_view>
#include "driver/uart.h"
#include "esp_log.h"

class AtGpioController {
    uart_port_t uart_num;
public:
    explicit AtGpioController(uart_port_t port) : uart_num(port) {}

    void send_command(std::string_view cmd) const {
        uart_write_bytes(uart_num, cmd.data(), cmd.size());
        uart_write_bytes(uart_num, "\r\n", 2);
        ESP_LOGI("AT_CPP", "Команда: %.*s", static_cast<int>(cmd.size()), cmd.data());
    }

    void init_io() const {
        send_command("AT+IOSETCFG=4,1,0");
        send_command("AT+GPIOWRITE=4,1");
        send_command("AT+GPIOREAD=5");
    }
};
