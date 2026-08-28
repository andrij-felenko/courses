#include <iostream>
#include <cstdint>

#define POWER_COMMANDS(X) \
    X(PWR_SLEEP, 0x10, "sleep") \
    X(PWR_WAKE,  0x11, "wake")

#define SENSOR_COMMANDS(X) \
    X(SNS_READ_TEMP, 0x20, "read_temp") \
    X(SNS_READ_HUM,  0x21, "read_hum")

#define ALL_SYSTEM_COMMANDS(X) \
    POWER_COMMANDS(X) \
    SENSOR_COMMANDS(X)

enum class SystemCmd : uint8_t {
#define X(name, code, str) name = code,
    ALL_SYSTEM_COMMANDS(X)
#undef X
};

int main() {
    std::cout << "Код PWR_SLEEP: 0x" << std::hex
              << static_cast<unsigned>(SystemCmd::PWR_SLEEP) << "\n";
    return 0;
}
