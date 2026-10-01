// Приклад класу керування GPIO ESP8266 через AT-команди на мові C++
class EspGpioDriver {
public:
    enum class Status { Ok, Error, Timeout };

    Status writePin(uint8_t pin, bool high) {
        char cmd[32];
        std::snprintf(cmd, sizeof(cmd), "AT+SYSGPIOWRITE=%u,%u\r\n", pin, high ? 1 : 0);
        _uart.write(cmd);
        return parseResponse(300);
    }

private:
    UartInterface& _uart;
    Status parseResponse(uint32_t timeout_ms);
};
