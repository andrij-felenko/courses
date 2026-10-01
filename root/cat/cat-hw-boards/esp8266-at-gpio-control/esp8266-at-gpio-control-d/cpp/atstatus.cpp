#include <cstdint>
#include <string>
#include <string_view>

enum class AtStatus {
    Ok,
    Error,
    Timeout
};

class Esp8266HostController {
public:
    AtStatus sendCommand(std::string_view cmd, uint32_t timeoutMs) {
        uartSend(cmd);
        uint32_t start = getTickMs();
        std::string rxBuffer;
        rxBuffer.reserve(64);

        while ((getTickMs() - start) < timeoutMs) {
            if (uartAvailable()) {
                rxBuffer += uartReadChar();
                if (rxBuffer.find("OK\r\n") != std::string::npos) {
                    return AtStatus::Ok;
                }
                if (rxBuffer.find("ERROR\r\n") != std::string::npos) {
                    return AtStatus::Error;
                }
            }
        }
        return AtStatus::Timeout;
    }

private:
    void uartSend(std::string_view data);
    bool uartAvailable();
    char uartReadChar();
    uint32_t getTickMs();
};
