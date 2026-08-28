/* IncidentRecorder.hpp / IncidentRecorder.cpp */
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <optional>

namespace Diagnostic {

#pragma pack(push, 1)
struct IncidentSnapshot {
    static constexpr std::uint32_t MagicTag = 0xDEADBEEFUL;

    std::uint32_t magic{MagicTag};
    std::uint32_t timestamp_sec{0};
    std::uint32_t reset_reason{0};
    std::uint32_t fault_pc{0};
    std::uint32_t fault_lr{0};
    std::uint32_t fault_cfsr{0};
    std::uint16_t supply_mv{0};
    std::int16_t  die_temp_c{0};
    std::uint16_t i2c_nack_count{0};
    std::uint16_t spi_err_count{0};
    std::uint32_t active_task_id{0};
    std::uint32_t free_heap_bytes{0};
    std::uint32_t crc32{0};
};
#pragma pack(pop)

class IncidentRecorder {
public:
    static constexpr std::uintptr_t BackupSramBase = 0x40024000UL;

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

    static void recordFatalIncident(std::uint32_t pc, std::uint32_t lr, std::uint32_t cfsr,
                                    std::uint32_t taskId, std::uint16_t vMv, std::int16_t tempC) noexcept {
        IncidentSnapshot snap;
        snap.timestamp_sec = 10423;
        snap.reset_reason = 0x20000000UL;
        snap.fault_pc = pc;
        snap.fault_lr = lr;
        snap.fault_cfsr = cfsr;
        snap.supply_mv = vMv;
        snap.die_temp_c = tempC;
        snap.active_task_id = taskId;
        snap.i2c_nack_count = 14;
        snap.spi_err_count = 0;
        snap.free_heap_bytes = 4096;

        const auto payloadSpan = std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t*>(&snap),
            sizeof(IncidentSnapshot) - sizeof(std::uint32_t)
        );
        snap.crc32 = calculateCrc32(payloadSpan);

        auto* dest = reinterpret_cast<IncidentSnapshot*>(BackupSramBase);
        *dest = snap;
    }

    static std::optional<IncidentSnapshot> retrieveLastSnapshot() noexcept {
        auto* src = reinterpret_cast<const IncidentSnapshot*>(BackupSramBase);
        if (src->magic != IncidentSnapshot::MagicTag) {
            return std::nullopt;
        }

        const auto payloadSpan = std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t*>(src),
            sizeof(IncidentSnapshot) - sizeof(std::uint32_t)
        );

        if (calculateCrc32(payloadSpan) != src->crc32) {
            return std::nullopt;
        }

        return *src;
    }
};

} // namespace Diagnostic
