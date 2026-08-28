// license_viewer.hpp / license_viewer.cpp — ідіоматична C++ реалізація
#include <array>
#include <string_view>
#include <cstdio>

struct ComponentLicense {
    std::string_view module;
    std::string_view version;
    std::string_view license_type;
    std::string_view copyright;
};

// Незмінний реєстр компонентів у Flash
inline constexpr std::array<ComponentLicense, 6> kEmbeddedSbom{{
    { "FreeRTOS Kernel",   "10.5.1",  "MIT",          "Amazon.com, Inc." },
    { "lwIP TCP/IP Stack", "2.2.0",   "BSD-3-Clause", "Swedish Institute of Computer Science" },
    { "mbed TLS",          "3.4.1",   "Apache-2.0",   "TrustedFirmware.org" },
    { "ARM CMSIS Core",    "5.9.0",   "Apache-2.0",   "Arm Limited" },
    { "STM32Cube HAL",     "1.11.0",  "BSD-3-Clause", "STMicroelectronics" },
    { "Madgwick AHRS",     "1.2.0",   "MIT",          "Sebastian Madgwick" }
}};

template <typename Writer>
void print_system_licenses(Writer&& write_uart) {
    write_uart("\r\n--- ПАСПОРТ СТОРОННІХ КОМПОНЕНТІВ ПРОШИВКИ ---\r\n");
    char line[120];
    for (const auto& c : kEmbeddedSbom) {
        int len = snprintf(line, sizeof(line), "[%-16.*s v%-7.*s] %-12.*s (c) %.*s\r\n",
                           static_cast<int>(c.module.size()), c.module.data(),
                           static_cast<int>(c.version.size()), c.version.data(),
                           static_cast<int>(c.license_type.size()), c.license_type.data(),
                           static_cast<int>(c.copyright.size()), c.copyright.data());
        if (len > 0) {
            write_uart(std::string_view(line, static_cast<size_t>(len)));
        }
    }
    write_uart("Повні тексти ліцензій: https://vendor.example.com/legal/licenses\r\n\r\n");
}
