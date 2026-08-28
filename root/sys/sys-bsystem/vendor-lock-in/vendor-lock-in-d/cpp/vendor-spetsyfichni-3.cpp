// Діалект GCC / Clang (C++)
#include <cstdint>

[[gnu::section(".ramfunc"), gnu::noinline]] void Flash_EraseSector(std::uint32_t address) noexcept;

/* Розміщення за конкретною адресою робиться через секцію лінкера */
[[gnu::section(".shared_ram")]] std::uint32_t SharedBuffer[256];

struct [[gnu::packed]] TelemetryPacket {
    std::uint8_t  id;
    std::uint32_t timestamp;
};
