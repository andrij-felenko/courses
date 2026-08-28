// FatalHandler.hpp / FatalHandler.cpp
#include <cstdint>
#include <cstring>
#include <span>
#include <optional>

namespace Diagnostics {

inline constexpr std::uint32_t SnapshotMagic = 0xDEADBEEFUL;
inline constexpr std::uintptr_t BackupSramAddr = 0x40024000UL;

#pragma pack(push, 1)
struct CrashDump {
    std::uint32_t magic{SnapshotMagic};
    std::uint32_t reset_reason{0};
    std::uint32_t fault_pc{0};
    std::uint32_t fault_lr{0};
    std::uint32_t fault_cfsr{0};
    std::uint16_t v_bat_mv{0};
    std::int16_t  temp_c{0};
    std::uint16_t bus_i2c_nack{0};
    std::uint16_t rtos_task_id{0};
    std::uint32_t crc32{0};
};
#pragma pack(pop)

class CrashManager {
public:
    static std::uint32_t calculateCrc32(std::span<const std::uint8_t> data) noexcept {
        std::uint32_t crc = 0xFFFFFFFFUL;
        for (const auto byte : data) {
            crc ^= byte;
            for (int bit = 0; bit < 8; ++bit) {
                crc = (crc >> 1) ^ (0xEDB88320UL & -(crc & 1));
            }
        }
        return ~crc;
    }

    static void handleFatalCrash(const std::uint32_t* stackFrame) noexcept {
        __asm volatile ("cpsid i" : : : "memory");

        CrashDump dump;
        dump.reset_reason = 0x20000000UL;
        dump.fault_pc = stackFrame[6];
        dump.fault_lr = stackFrame[5];
        dump.fault_cfsr = *reinterpret_cast<const volatile std::uint32_t*>(0xE000ED28UL);
        dump.v_bat_mv = 2780;
        dump.temp_c = 64;
        dump.bus_i2c_nack = 14;
        dump.rtos_task_id = 2;

        const auto payload = std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t*>(&dump),
            sizeof(CrashDump) - sizeof(std::uint32_t)
        );
        dump.crc32 = calculateCrc32(payload);

        auto* target = reinterpret_cast<CrashDump*>(BackupSramAddr);
        *target = dump;

        __asm volatile ("dsb 0xF" : : : "memory");
        __asm volatile ("isb 0xF" : : : "memory");

        *reinterpret_cast<volatile std::uint32_t*>(0xE000ED0CUL) = 0x05FA0004UL;

        while (true) {
            __asm volatile ("nop");
        }
    }
};

} // namespace Diagnostics
