#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>

namespace sf::coredump {

inline constexpr uint32_t MagicHeader       = 0x434F5245U;
inline constexpr size_t   MaxSlots          = 4U;
inline constexpr size_t   SlotSize          = 4096U;
inline constexpr uintptr_t PartitionBase    = 0x08060000U;

enum class State : uint32_t {
    Erased    = 0xFFFFFFFFU,
    Start     = 0xFFFFFFFEU,
    DataOk    = 0xFFFFFFFCU,
    Valid     = 0xFFFFFFF8U,
    Extracted = 0xFFFFFFF0U,
    Dirty     = 0x00000000U
};

struct MemoryRegionDesc {
    uint32_t start_address;
    uint32_t length_bytes;
    uint32_t memory_type;
};

struct alignas(4) SlotHeader {
    uint32_t magic;
    State    state;
    uint32_t seq_num;
    uint64_t timestamp_ticks;
    uint32_t crash_reason_code;
    uint16_t arch_id;
    uint16_t num_regions;
    MemoryRegionDesc regions[4];
    uint32_t header_crc;
};

struct alignas(4) CpuContext {
    uint32_t r0, r1, r2, r3, r4, r5, r6, r7;
    uint32_t r8, r9, r10, r11, r12;
    uint32_t sp, lr, pc, xpsr;
    uint32_t cfsr, hfsr, mmar, bfar;
};

class CoredumpTriage {
    static uint32_t CalculateCrc32(std::span<const uint8_t> data, uint32_t initial = 0xFFFFFFFFU) noexcept {
        uint32_t crc = initial;
        for (uint8_t byte : data) {
            crc ^= static_cast<uint32_t>(byte);
            for (uint8_t b = 0; b < 8; ++b) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1U)));
            }
        }
        return crc;
    }

public:
    static bool VerifySlotIntegrity(uintptr_t slot_addr) noexcept {
        const auto* hdr = reinterpret_cast<const SlotHeader*>(slot_addr);
        if (hdr->magic != MagicHeader || hdr->state != State::Valid) {
            return false;
        }

        uint32_t running_crc = 0xFFFFFFFFU;
        uint32_t offset = sizeof(SlotHeader);

        /* 1. Перевірка кадру процесора */
        std::span<const uint8_t> cpu_span{
            reinterpret_cast<const uint8_t*>(slot_addr + offset),
            sizeof(CpuContext)
        };
        running_crc = CalculateCrc32(cpu_span, running_crc);
        offset += sizeof(CpuContext);

        /* 2. Перевірка збережених сегментів */
        for (uint16_t i = 0; i < hdr->num_regions && i < 4; ++i) {
            std::span<const uint8_t> reg_span{
                reinterpret_cast<const uint8_t*>(slot_addr + offset),
                hdr->regions[i].length_bytes
            };
            running_crc = CalculateCrc32(reg_span, running_crc);
            offset += hdr->regions[i].length_bytes;
        }

        running_crc = ~running_crc;
        uint32_t saved_crc = *reinterpret_cast<const uint32_t*>(slot_addr + offset);
        return (running_crc == saved_crc);
    }

    static std::optional<uintptr_t> LocateLatestValidDump() noexcept {
        std::optional<uintptr_t> best_slot = std::nullopt;
        uint32_t max_seq = 0;

        for (size_t i = 0; i < MaxSlots; ++i) {
            uintptr_t slot_addr = PartitionBase + (i * SlotSize);
            const auto* hdr = reinterpret_cast<const SlotHeader*>(slot_addr);

            if (hdr->magic == MagicHeader && hdr->state == State::Valid) {
                if (VerifySlotIntegrity(slot_addr)) {
                    if (!best_slot.has_value() || hdr->seq_num > max_seq) {
                        max_seq = hdr->seq_num;
                        best_slot = slot_addr;
                    }
                }
            }
        }
        return best_slot;
    }

    static bool MarkAsExtracted(uintptr_t slot_addr) noexcept {
        extern bool flash_write_word_cpp(uint32_t address, uint32_t value) noexcept;
        auto state_addr = static_cast<uint32_t>(slot_addr + offsetof(SlotHeader, state));
        return flash_write_word_cpp(state_addr, static_cast<uint32_t>(State::Extracted));
    }
};

} // namespace sf::coredump
