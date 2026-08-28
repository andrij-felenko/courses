#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <chrono>
#include <algorithm>

template <size_t WindowSize = 256, uint32_t ExpectedPeriodUs = 1000, uint32_t ToleranceUs = 150>
class SensorWindowCollector {
public:
    enum class Error {
        BufferIncomplete,
        TimingJitterExceeded
    };

    SensorWindowCollector() = default;

    // Додавання нової вибірки з контролем часового інтервалу
    bool push(int16_t sample, std::chrono::microseconds timestamp) noexcept {
        const uint64_t ts_us = static_cast<uint64_t>(timestamp.count());
        if (last_timestamp_ != 0) {
            const int64_t dt = static_cast<int64_t>(ts_us - last_timestamp_);
            if (dt < static_cast<int64_t>(ExpectedPeriodUs - ToleranceUs) ||
                dt > static_cast<int64_t>(ExpectedPeriodUs + ToleranceUs)) {
                timing_errors_++;
            }
        }
        last_timestamp_ = ts_us;

        raw_samples_[head_idx_] = sample;
        timestamps_[head_idx_] = ts_us;

        head_idx_ = (head_idx_ + 1) % WindowSize;
        if (count_ < WindowSize) {
            count_++;
        }

        return (count_ == WindowSize);
    }

    // Експорт нормалізованого вікна у вихідний буфер інференсу
    std::expected<void, Error> exportNormalized(
        std::span<float, WindowSize> output,
        float scale_factor) const noexcept 
    {
        if (count_ < WindowSize) {
            return std::unexpected(Error::BufferIncomplete);
        }

        const size_t start_idx = head_idx_;
        for (size_t i = 0; i < WindowSize; ++i) {
            const size_t idx = (start_idx + i) % WindowSize;
            output[i] = static_cast<float>(raw_samples_[idx]) * scale_factor;
        }

        return {};
    }

    [[nodiscard]] uint32_t timingErrors() const noexcept {
        return timing_errors_;
    }

    [[nodiscard]] bool isFull() const noexcept {
        return count_ == WindowSize;
    }

private:
    std::array<int16_t, WindowSize> raw_samples_{};
    std::array<uint64_t, WindowSize> timestamps_{};
    size_t head_idx_{0};
    size_t count_{0};
    uint64_t last_timestamp_{0};
    uint32_t timing_errors_{0};
};
