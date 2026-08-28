#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>

namespace safety {

enum class Status : std::uint8_t {
    Ok             = 0x00,
    ErrCpuReg      = 0x01,
    ErrCpuFlags    = 0x02,
    ErrCpuPc       = 0x03,
    ErrRamMarchC   = 0x10,
    ErrFlashCrc    = 0x20,
    ErrClockDrift  = 0x30,
    ErrWdtTrigger  = 0x40,
    ErrAdcVref     = 0x50,
    ErrGpioStuck   = 0x60
};

// Контекст неруйнівного зрізу ОЗП на базі std::span
template <std::size_t SliceWords = 16>
class RamSliceScanner {
public:
    explicit RamSliceScanner(std::span<std::uint32_t> ram_region) noexcept
        : region_(ram_region), current_offset_(0) {}

    [[nodiscard]] Status scan_next_slice() noexcept;
    void reset() noexcept { current_offset_ = 0; }

private:
    std::span<std::uint32_t> region_;
    std::size_t current_offset_;
    std::array<std::uint32_t, SliceWords> backup_buffer_{};
};

// Контекст інкрементального підрахунку CRC32 Flash
class FlashCrcScanner {
public:
    FlashCrcScanner(std::span<const std::uint8_t> flash_area,
                    std::uint32_t expected_crc,
                    std::size_t bytes_per_quantum = 1024) noexcept
        : flash_(flash_area), expected_crc_(expected_crc),
          quantum_(bytes_per_quantum), processed_(0), running_crc_(0xFFFFFFFFU) {}

    struct StepResult {
        Status status;
        bool is_cycle_finished;
    };

    [[nodiscard]] StepResult scan_quantum() noexcept;
    void reset() noexcept {
        processed_ = 0;
        running_crc_ = 0xFFFFFFFFU;
    }

private:
    std::span<const std::uint8_t> flash_;
    std::uint32_t expected_crc_;
    std::size_t quantum_;
    std::size_t processed_;
    std::uint32_t running_crc_;
};

// Перевірка тактового генератора
class ClockMonitor {
public:
    constexpr ClockMonitor(std::uint32_t expected, std::uint32_t tolerance) noexcept
        : expected_(expected), tolerance_(tolerance) {}

    [[nodiscard]] Status verify_frequency(std::uint32_t measured_counts) const noexcept {
        const std::uint32_t min_allowed = expected_ - tolerance_;
        const std::uint32_t max_allowed = expected_ + tolerance_;
        if (measured_counts < min_allowed || measured_counts > max_allowed) {
            return Status::ErrClockDrift;
        }
        return Status::Ok;
    }

private:
    std::uint32_t expected_;
    std::uint32_t tolerance_;
};

// Захищений вхід у Safe State
[[noreturn]] void enter_safe_state(Status reason) noexcept;

} // namespace safety
