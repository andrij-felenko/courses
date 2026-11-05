#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <algorithm>

namespace sf::coredump {

inline constexpr uint32_t MagicHeader       = 0x434F5245U; /* 'CORE' */
inline constexpr uint32_t FlashPageSize     = 256U;
inline constexpr uint32_t PollTimeoutCycles = 500000U;
inline constexpr size_t   MaxRegions        = 4U;

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
    std::array<MemoryRegionDesc, MaxRegions> regions;
    uint32_t header_crc;
};

struct alignas(4) CpuContext {
    uint32_t r0, r1, r2, r3, r4, r5, r6, r7;
    uint32_t r8, r9, r10, r11, r12;
    uint32_t sp, lr, pc, xpsr;
    uint32_t cfsr, hfsr, mmar, bfar;
};

class PolledFlashDriver {
    static constexpr uintptr_t FlashBase = 0x40023C00U;
    static constexpr uint32_t FlashSrBsy = 1U << 16;
    static constexpr uint32_t FlashSrErr = 0x000000F2U;
    static constexpr uint32_t FlashCrPg  = 1U << 0;
    static constexpr uintptr_t IwdgKr    = 0x40003000U;

    static volatile uint32_t& Reg(uintptr_t offset) noexcept {
        return *reinterpret_cast<volatile uint32_t*>(FlashBase + offset);
    }

public:
    static void FeedWatchdog() noexcept {
        *reinterpret_cast<volatile uint32_t*>(IwdgKr) = 0xAAAAU;
    }

    static bool WaitReady() noexcept {
        uint32_t timeout = PollTimeoutCycles;
        while ((Reg(0x0C) & FlashSrBsy) && (--timeout > 0)) {
            asm volatile("nop");
        }
        if (timeout == 0) return false;
        if (Reg(0x0C) & FlashSrErr) {
            Reg(0x0C) = FlashSrErr;
            return false;
        }
        return true;
    }

    static bool WriteWord(uint32_t address, uint32_t value) noexcept {
        if (!WaitReady()) return false;
        Reg(0x10) |= FlashCrPg;
        *reinterpret_cast<volatile uint32_t*>(address) = value;
        asm volatile("dsb 0xF" ::: "memory");
        asm volatile("isb 0xF" ::: "memory");
        bool ok = WaitReady();
        Reg(0x10) &= ~FlashCrPg;
        return ok && (*reinterpret_cast<volatile uint32_t*>(address) == value);
    }
};

class CoredumpEngine {
    static uint32_t UpdateCrc32(uint32_t crc, std::span<const uint8_t> data) noexcept {
        crc = ~crc;
        for (uint8_t byte : data) {
            crc ^= static_cast<uint32_t>(byte);
            for (uint8_t bit = 0; bit < 8; ++bit) {
                uint32_t mask = -(crc & 1U);
                crc = (crc >> 1) ^ (0xEDB88320U & mask);
            }
        }
        return ~crc;
    }

    static bool WriteStream(uint32_t dest, std::span<const uint8_t> data, uint32_t& running_crc) noexcept {
        size_t words = data.size() / 4;
        auto words_view = reinterpret_cast<const uint32_t*>(data.data());

        for (size_t i = 0; i < words; ++i) {
            if (!PolledFlashDriver::WriteWord(dest + (i * 4), words_view[i])) {
                return false;
            }
            if ((i % (FlashPageSize / 4)) == 0) {
                PolledFlashDriver::FeedWatchdog();
            }
        }

        size_t tail_bytes = data.size() % 4;
        if (tail_bytes > 0) {
            uint32_t tail_word = 0xFFFFFFFFU;
            auto* tail_buf = reinterpret_cast<uint8_t*>(&tail_word);
            for (size_t j = 0; j < tail_bytes; ++j) {
                tail_buf[j] = data[(words * 4) + j];
            }
            if (!PolledFlashDriver::WriteWord(dest + (words * 4), tail_word)) {
                return false;
            }
        }

        running_crc = UpdateCrc32(running_crc, data);
        PolledFlashDriver::FeedWatchdog();
        return true;
    }

public:
    static bool CommitPanicDump(uint32_t slot_addr,
                                const CpuContext& cpu,
                                std::span<const MemoryRegionDesc> regions,
                                uint32_t crash_code,
                                uint32_t seq_num) noexcept {
        SlotHeader header{};
        header.magic = MagicHeader;
        header.state = State::Start;
        header.seq_num = seq_num;
        header.timestamp_ticks = 0;
        header.crash_reason_code = crash_code;
        header.arch_id = 1;
        header.num_regions = static_cast<uint16_t>(std::min(regions.size(), MaxRegions));

        for (size_t i = 0; i < header.num_regions; ++i) {
            header.regions[i] = regions[i];
        }

        /* 1. Позначення слота як такого, що записується */
        auto state_offset = slot_addr + offsetof(SlotHeader, state);
        if (!PolledFlashDriver::WriteWord(state_offset, static_cast<uint32_t>(State::Start))) {
            return false;
        }

        uint32_t current_offset = sizeof(SlotHeader);
        uint32_t crc = 0;

        /* 2. Запис процесорного кадру */
        std::span<const uint8_t> cpu_span{reinterpret_cast<const uint8_t*>(&cpu), sizeof(CpuContext)};
        if (!WriteStream(slot_addr + current_offset, cpu_span, crc)) {
            return false;
        }
        current_offset += sizeof(CpuContext);

        /* 3. Запис збережених сегментів пам'яті */
        for (size_t i = 0; i < header.num_regions; ++i) {
            auto ptr = reinterpret_cast<const uint8_t*>(header.regions[i].start_address);
            std::span<const uint8_t> reg_span{ptr, header.regions[i].length_bytes};
            if (!WriteStream(slot_addr + current_offset, reg_span, crc)) {
                return false;
            }
            current_offset += header.regions[i].length_bytes;
        }

        /* 4. Запис контрольної суми CRC32 */
        if (!PolledFlashDriver::WriteWord(slot_addr + current_offset, crc)) {
            return false;
        }

        /* 5. Атомарний коміт слота */
        return PolledFlashDriver::WriteWord(state_offset, static_cast<uint32_t>(State::Valid));
    }
};

} // namespace sf::coredump
