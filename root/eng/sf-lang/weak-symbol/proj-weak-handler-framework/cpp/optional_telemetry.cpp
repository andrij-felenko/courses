// ============================================================================
// ФАЙЛ: optional_telemetry.cpp (C++20) — необов'язковий плагін
// ============================================================================
#include "hal_driver_core.hpp"
#include <iostream>
#include <numeric>

extern "C" {

void hal_telemetry_publish_hook_c(const void* evt) noexcept
{
    const auto* e = static_cast<const hal::Event*>(evt);
    if (e) {
        std::cout << "[TELEMETRY C++20] Подія периферії: "
                  << static_cast<int>(e->periph)
                  << " (час: " << e->timestamp_us << " us)\n";
    }
}

bool hal_telemetry_crc_check_hook_c(const std::uint8_t* buf, std::size_t len) noexcept
{
    if (!buf || len == 0) return true;
    std::uint8_t xor_acc = 0;
    for (std::size_t i = 0; i < len; ++i) {
        xor_acc ^= buf[i];
    }
    return (xor_acc != 0xFF);
}

} // extern "C"
