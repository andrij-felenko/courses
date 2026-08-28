/* flight_recorder.hpp - C++20 типізована обгортка діагностичного реєстратора */
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <array>
#include <concepts>

namespace notary::diagnostics {

enum class ResetCause : uint8_t {
    Unknown   = 0x00,
    PowerOn   = 0x01,
    BrownOut  = 0x02,
    PinReset  = 0x04,
    Watchdog  = 0x08,
    Software  = 0x20
};

enum class DumpError {
    InvalidMagic,
    VersionMismatch,
    CrcMismatch,
    EmptyStorage
};

struct [[gnu::packed]] CrashDump {
    static constexpr uint32_t MagicIdentifier = 0x444E4646U; /* "NFFD" */
    static constexpr uint32_t CurrentVersion  = 1U;

    uint32_t magic{MagicIdentifier};
    uint32_t version{CurrentVersion};
    uint64_t uptime_ms{0};
    uint32_t boot_count{0};
    uint8_t  last_reset_flags{0};
    uint8_t  reserved[3]{0, 0, 0};

    uint32_t cfsr{0};
    uint32_t hfsr{0};
    uint32_t bfar{0};
    uint32_t lr{0};
    uint32_t pc{0};

    uint16_t supply_mv{0};
    int16_t  die_temp_c_x10{0};
    uint32_t brownout_count{0};
    uint32_t bus_error_count{0};

    uint32_t crc32{0};

    [[nodiscard]] constexpr bool has_brownout_flag() const noexcept {
        return (last_reset_flags & static_cast<uint8_t>(ResetCause::BrownOut)) != 0;
    }

    [[nodiscard]] constexpr bool has_bus_fault() const noexcept {
        return (cfsr & 0x0000BF00U) != 0; /* BusFault flags in CFSR */
    }
};

class FlightRecorder {
public:
    explicit FlightRecorder(std::span<uint8_t> nvm_storage) noexcept
        : storage_(nvm_storage) {}

    void initialize(uint32_t raw_reset_status, uint32_t boot_counter) noexcept;
    void log_power_drop(uint16_t vdd_mv, int16_t temp_c_x10) noexcept;
    void capture_hardfault(uint32_t cfsr, uint32_t hfsr, uint32_t bfar,
                          uint32_t lr, uint32_t pc, uint16_t vdd, int16_t temp) noexcept;

    [[nodiscard]] std::expected<CrashDump, DumpError> load_and_verify() const noexcept;
    void erase_log() noexcept;

    static uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept;

private:
    std::span<uint8_t> storage_;
    uint32_t pvd_event_counter_{0};
    uint32_t bus_error_counter_{0};
};

} // namespace notary::diagnostics
