#include <cstdint>
#include <cstddef>
#include <span>
#include <atomic>
#include <array>
#include <algorithm>

namespace embedded::diag {

enum class EventType : uint8_t {
    SystemBoot         = 0x01,
    BrownoutDetected   = 0x02,
    BusSetupViolation  = 0x03,
    BusCrcError        = 0x04,
    FramingError       = 0x05,
    StressBurstStart   = 0x06
};

struct alignas(4) LogEntry {
    uint32_t  timestamp_us{0};
    EventType event_type{EventType::SystemBoot};
    uint8_t   bus_status{0};
    uint16_t  aux_data{0};
};

template <size_t Capacity = 64>
class FlightRecorder {
public:
    static constexpr uint32_t MagicPattern = 0xDEADBEEF;

    struct Storage {
        uint32_t magic;
        uint32_t boot_counter;
        uint32_t write_idx;
        uint32_t total_errors;
        std::array<LogEntry, Capacity> entries;
    };

    explicit FlightRecorder(Storage& memory) noexcept : storage_(memory) {}

    void init(uint32_t reset_flags) noexcept {
        if (storage_.magic != MagicPattern) {
            storage_.magic = MagicPattern;
            storage_.boot_counter = 1;
            storage_.write_idx = 0;
            storage_.total_errors = 0;
            storage_.entries.fill(LogEntry{});
        } else {
            storage_.boot_counter++;
        }
        log(EventType::SystemBoot, static_cast<uint8_t>(reset_flags), static_cast<uint16_t>(storage_.boot_counter));
    }

    void log(EventType evt, uint8_t status = 0, uint16_t aux = 0) noexcept {
        const uint32_t idx = storage_.write_idx % Capacity;
        storage_.entries[idx] = LogEntry{
            .timestamp_us = get_micros(),
            .event_type   = evt,
            .bus_status   = status,
            .aux_data     = aux
        };
        storage_.write_idx++;

        if (evt == EventType::BusCrcError || evt == EventType::FramingError || evt == EventType::BusSetupViolation) {
            storage_.total_errors++;
        }
    }

    [[nodiscard]] uint32_t boot_count() const noexcept { return storage_.boot_counter; }
    [[nodiscard]] uint32_t error_count() const noexcept { return storage_.total_errors; }

private:
    Storage& storage_;

    static uint32_t get_micros() noexcept {
        extern volatile uint32_t g_system_tick_us;
        return g_system_tick_us;
    }
};

/* Клас генератора граничних навантажень (Corner Stressor) */
class MarginalStressor {
public:
    constexpr explicit MarginalStressor(uint32_t seed = 0x12345678) noexcept : seed_(seed) {}

    void set_jitter_injection(bool enable) noexcept { inject_jitter_ = enable; }

    template <typename TransferFunc>
    bool execute_transfer(std::span<const uint8_t> tx, std::span<uint8_t> rx, 
                         FlightRecorder<64>& recorder, TransferFunc&& transfer_op) noexcept {
        if (inject_jitter_) {
            apply_micro_jitter();
        }

        auto [success, hw_status] = transfer_op(tx, rx);
        if (!success || (hw_status & 0x08)) {
            recorder.log(EventType::BusSetupViolation, hw_status, static_cast<uint16_t>(tx.size()));
            return false;
        }
        return true;
    }

private:
    uint32_t seed_;
    bool inject_jitter_{true};

    void apply_micro_jitter() noexcept {
        seed_ ^= seed_ << 13;
        seed_ ^= seed_ >> 17;
        seed_ ^= seed_ << 5;

        const uint32_t cycles = seed_ & 0x1F;
        for (volatile uint32_t i = 0; i < cycles; ++i) {
            #if defined(__GNUC__) || defined(__clang__)
            asm volatile("nop");
            #endif
        }
    }
};

} // namespace embedded::diag
