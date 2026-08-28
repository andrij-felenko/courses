// Концептуальна модель поведінки ядра serial_core на C++
#include <cstdint>
#include <chrono>

struct UartPort {
    bool is_console{true};
    bool sysrq_enabled{true};
    std::chrono::steady_clock::time_point sysrq_timeout{};
    bool in_sysrq_mode{false};
};

class SerialCoreHandler {
public:
    static bool handle_break(UartPort& port) noexcept {
        if (port.is_console && port.sysrq_enabled) {
            // Активація 5-секундного вікна очікування клавіші SysRq
            port.in_sysrq_mode = true;
            port.sysrq_timeout = std::chrono::steady_clock::now() + std::chrono::seconds(5);
            return true; // Перехоплено підсистемою SysRq
        }
        return false; // Передати далі в термінальний буфер
    }
};
