// cli_license.hpp / cli_license.cpp — ідіоматична C++ версія для вбудованої консолі
#include <array>
#include <string_view>
#include <format>
#include <span>

struct LicenseEntry {
    std::string_view name;
    std::string_view version;
    std::string_view spdx_id;
    std::string_view copyright;
};

// Незмінна таблиця у Flash пам'яті (constexpr)
inline constexpr std::array<LicenseEntry, 8> kFirmwareLicenses{{
    { "FreeRTOS Kernel",       "10.5.1",  "MIT",          "Amazon.com, Inc. or its affiliates" },
    { "lwIP TCP/IP Stack",     "2.2.0",   "BSD-3-Clause", "Swedish Institute of Computer Science" },
    { "mbed TLS",              "3.4.1",   "Apache-2.0",   "TrustedFirmware.org" },
    { "FatFS Module",          "R0.15",   "FatFS-Notice", "ChaN" },
    { "ARM CMSIS Core & DSP",  "5.9.0",   "Apache-2.0",   "Arm Limited" },
    { "STM32CubeH7 HAL",       "1.11.0",  "BSD-3-Clause", "STMicroelectronics" },
    { "Wi-Fi PHY Driver",      "2.4.18",  "Proprietary",  "Silicon Vendor Corp" },
    { "Flight Autopilot Core", "3.2.0",   "Proprietary",  "Aerospace Dynamics Inc." }
}};

template <typename OutputFunctor>
void print_firmware_licenses(OutputFunctor&& out) {
    out("\r\n=== СПИСОК КОМПОНЕНТІВ ТА ЛІЦЕНЗІЙ ПРОШИВКИ (SBOM) ===\r\n");
    out("Назва                    Версія   Ліцензія     Власник копірайту\r\n");
    out("------------------------------------------------------------------------\r\n");

    for (const auto& entry : kFirmwareLicenses) {
        // Форматування рядка фіксованої ширини
        char buffer[128];
        int written = snprintf(buffer, sizeof(buffer), "%-24.*s %-8.*s %-12.*s %.*s\r\n",
                               static_cast<int>(entry.name.size()), entry.name.data(),
                               static_cast<int>(entry.version.size()), entry.version.data(),
                               static_cast<int>(entry.spdx_id.size()), entry.spdx_id.data(),
                               static_cast<int>(entry.copyright.size()), entry.copyright.data());
        if (written > 0) {
            out(std::string_view(buffer, static_cast<size_t>(written)));
        }
    }
    out("------------------------------------------------------------------------\r\n");
    out("Повний текст ліцензій доступний за запитом або в інструкції користувача.\r\n\r\n");
}
