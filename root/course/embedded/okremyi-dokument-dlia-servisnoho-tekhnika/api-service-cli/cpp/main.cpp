/* Об'єктний інтерфейс безпечного сервісного керування периферією */
#include <cstdint>
#include <chrono>
#include <expected>
#include <span>

enum class ActChannel : uint8_t {
    Relay1   = 0x01,
    Relay2   = 0x02,
    ValvePwm = 0x03,
    FanOut   = 0x04
};

struct ActCommand {
    ActChannel channel;
    std::chrono::seconds duration{5}; /* Захисний тайм-аут за замовчуванням 5 с */
    uint16_t pwmPermille{1000};       /* 1000 = 100% заповнення */
    bool forceOverride{false};
};

enum class ActError : uint16_t {
    TimeoutExceeded = 0x4001,
    ThermalLockout  = 0x4002,
    InvalidChannel  = 0x4003,
    SafetyInterlock = 0x4004
};

class ServiceActuatorController {
public:
    static std::expected<void, ActError> execute(const ActCommand& cmd) noexcept;
    static void emergencyAllOff() noexcept;
};
