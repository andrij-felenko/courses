#ifndef BUS_DIAGNOSTICS_HPP
#define BUS_DIAGNOSTICS_HPP

#include <cstdint>
#include <array>
#include <span>
#include "stm32f4xx.h"

enum class DiagnosticEventType : uint8_t {
    None,
    TimeoutTxe,
    TimeoutRxne,
    BusLockup9Pulses,
    Tier1SoftReset,
    Tier2PinReset,
    Tier3PowerCycle,
    CalibrationCrcError,
    RecoverySuccess
};

struct DiagnosticEntry {
    uint32_t timestamp_cycles{0};
    DiagnosticEventType event{DiagnosticEventType::None};
    uint8_t peripheral_id{0};
    int8_t status_code{0};
    uint8_t aux_data{0};
};

template <size_t Capacity = 32>
class DiagnosticLog {
public:
    constexpr DiagnosticLog() noexcept = default;

    void record(DiagnosticEventType event, uint8_t periph_id, int8_t status = 0, uint8_t aux = 0) noexcept {
        entries_[head_] = DiagnosticEntry{
            .timestamp_cycles = DWT->CYCCNT,
            .event = event,
            .peripheral_id = periph_id,
            .status_code = status,
            .aux_data = aux
        };
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) ++count_;
        ++total_recorded_;
    }

    [[nodiscard]] size_t count() const noexcept { return count_; }
    [[nodiscard]] uint32_t total_recorded() const noexcept { return total_recorded_; }

private:
    std::array<DiagnosticEntry, Capacity> entries_{};
    size_t head_{0};
    size_t count_{0};
    uint32_t total_recorded_{0};
};

#endif // BUS_DIAGNOSTICS_HPP
