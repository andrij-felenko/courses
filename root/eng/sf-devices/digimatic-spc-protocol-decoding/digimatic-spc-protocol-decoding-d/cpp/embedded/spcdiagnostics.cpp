#include <cstdint>
#include <array>
#include <atomic>

class SpcDiagnostics {
public:
    enum class Status : uint8_t {
        Ok = 0,
        Timeout,
        PreambleError,
        BcdRangeError,
        BatteryLow,
        Overspeed
    };

    struct TelemetrySnapshot {
        uint32_t total_frames;
        uint32_t valid_frames;
        uint32_t error_count;
        uint32_t battery_warnings;
        bool link_healthy;
    };

    void recordTimeout() noexcept {
        total_frames_.fetch_add(1, std::memory_order_relaxed);
        timeout_errors_.fetch_add(1, std::memory_order_relaxed);
    }

    Status validateDigimatic(const std::array<uint8_t, 13>& d) noexcept {
        total_frames_.fetch_add(1, std::memory_order_relaxed);

        // Перевірка індикатора низького заряду батареї
        if ((d[4] & 0x04) != 0) {
            battery_warnings_.fetch_add(1, std::memory_order_relaxed);
            return Status::BatteryLow;
        }

        // Перевірка преамбули
        if (d[0] != 0x0F || d[1] != 0x0F || d[2] != 0x0F || d[3] != 0x0F) {
            preamble_errors_.fetch_add(1, std::memory_order_relaxed);
            return Status::PreambleError;
        }

        // Перевірка діапазону BCD
        for (size_t i = 5; i <= 10; ++i) {
            if (d[i] > 9) {
                bcd_errors_.fetch_add(1, std::memory_order_relaxed);
                return Status::BcdRangeError;
            }
        }

        valid_frames_.fetch_add(1, std::memory_order_relaxed);
        return Status::Ok;
    }

    TelemetrySnapshot getSnapshot() const noexcept {
        uint32_t total = total_frames_.load(std::memory_order_relaxed);
        uint32_t valid = valid_frames_.load(std::memory_order_relaxed);
        uint32_t timeouts = timeout_errors_.load(std::memory_order_relaxed);
        uint32_t preambles = preamble_errors_.load(std::memory_order_relaxed);
        uint32_t bcds = bcd_errors_.load(std::memory_order_relaxed);
        uint32_t battery = battery_warnings_.load(std::memory_order_relaxed);

        uint32_t errors = timeouts + preambles + bcds;
        bool healthy = (total < 20) || ((errors * 100 / total) < 5);

        return TelemetrySnapshot{ total, valid, errors, battery, healthy };
    }

private:
    std::atomic<uint32_t> total_frames_{0};
    std::atomic<uint32_t> valid_frames_{0};
    std::atomic<uint32_t> timeout_errors_{0};
    std::atomic<uint32_t> preamble_errors_{0};
    std::atomic<uint32_t> bcd_errors_{0};
    std::atomic<uint32_t> battery_warnings_{0};
};
