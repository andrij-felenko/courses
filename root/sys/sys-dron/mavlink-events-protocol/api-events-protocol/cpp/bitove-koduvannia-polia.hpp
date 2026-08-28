#include <cstdint>

// Типобезпечні обгортки для роботи з log_levels (C++20)
constexpr uint8_t packLogLevels(uint8_t internalLevel, uint8_t externalSeverity) noexcept {
    return static_cast<uint8_t>(((internalLevel & 0x0F) << 4) | (externalSeverity & 0x0F));
}

constexpr uint8_t getInternalLogLevel(uint8_t logLevels) noexcept {
    return static_cast<uint8_t>((logLevels >> 4) & 0x0F);
}

constexpr uint8_t getExternalSeverity(uint8_t logLevels) noexcept {
    return static_cast<uint8_t>(logLevels & 0x0F);
}
