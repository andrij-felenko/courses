// Діалект IAR C++: ключові слова та прагми
#include <cstdint>

__ramfunc void Flash_EraseSector(std::uint32_t address) noexcept;

#pragma location = 0x20000000
std::uint32_t SharedBuffer[256];

__packed struct TelemetryPacket {
    std::uint8_t  id;
    std::uint32_t timestamp;
};
