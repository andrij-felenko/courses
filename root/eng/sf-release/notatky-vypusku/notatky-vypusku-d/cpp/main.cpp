#include <iostream>
#include <string_view>
#include <vector>
#include <span>
#include <cstdint>

class TelemetryChannel {
public:
    // Старий інтерфейс: позначено стандартним атрибутом C++14 [[deprecated]]
    [[deprecated("telemetry_send() застаріла з v3.2.0; використовуйте send_fd() з параметрами QoS")]]
    bool telemetry_send(uint32_t msg_id, std::span<const uint8_t> payload) {
        std::cerr << "[WARN-DEPRECATION] Виклик застарілого методу для ID=0x" 
                  << std::hex << msg_id << ". Дивіться інструкцію міграції v3.2.0!\n";
        return payload.size() <= 8;
    }

    // Новий ідіоматичний інтерфейс CAN-FD
    bool send_fd(uint32_t msg_id, std::span<const uint8_t> payload, uint8_t qos_flags = 0) noexcept {
        static_cast<void>(qos_flags);
        return payload.size() <= 64;
    }
};
