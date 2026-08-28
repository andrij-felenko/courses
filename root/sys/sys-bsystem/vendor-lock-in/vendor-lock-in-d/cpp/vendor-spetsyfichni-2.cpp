// Діалект Keil ArmCC (Arm Compiler 5, C++)
#include <cstdint>

__attribute__((section("ram_functions"))) void Flash_EraseSector(std::uint32_t address) noexcept;

uint32_t SharedBuffer[256] __attribute__((at(0x20000000)));

__packed struct TelemetryPacket {
    std::uint8_t  id;
    std::uint32_t timestamp;
};
