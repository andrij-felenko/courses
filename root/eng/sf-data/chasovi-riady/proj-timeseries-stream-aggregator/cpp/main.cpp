#include <iostream>
#include <vector>
#include <chrono>
#include <optional>
#include <cmath>
#include <limits>
#include <cstdint>
#include <span>

namespace timeseries {

using Timestamp = std::chrono::nanoseconds;

struct MetricSample {
    Timestamp timestamp;
    double value;
};

/* Статистичний підсумок інтервалу */
struct BucketStats {
    uint64_t bucket_index{0};
    uint64_t count{0};
    double sum{0.0};
    double min{std::numeric_limits<double>::infinity()};
    double max{-std::numeric_limits<double>::infinity()};
    double mean{0.0};
    double m2{0.0};
    double last_value{0.0};
    bool is_valid{false};

    [[nodiscard]] double variance() const noexcept {
        return (count > 1) ? (m2 / static_cast<double>(count - 1)) : 0.0;
    }

    [[nodiscard]] double stddev() const noexcept {
        return std::sqrt(variance());
    }

    void reset(uint64_t idx) noexcept {
        bucket_index = idx;
        count = 0;
        sum = 0.0;
        min = std::numeric_limits<double>::infinity();
        max = -std::numeric_limits<double>::infinity();
        mean = 0.0;
        m2 = 0.0;
        last_value = 0.0;
        is_valid = true;
    }

    void update(double val) noexcept {
        count++;
        sum += val;
        min = std::min(min, val);
        max = std::max(max, val);
        last_value = val;

        /* Чисельно стабільний розрахунок дисперсії Велфорда */
        const double delta = val - mean;
        mean += delta / static_cast<double>(count);
        const double delta2 = val - mean;
        m2 += delta * delta2;
    }
};

/* Потоковий агрегатор на базі кільцевого буфера з RAII-гарантіями */
class RingBufferAggregator {
public:
    explicit RingBufferAggregator(uint32_t series_id,
                                  Timestamp bucket_duration = std::chrono::seconds(10),
                                  size_t capacity = 64,
                                  double ema_alpha = 0.2)
        : series_id_(series_id),
          bucket_duration_ns_(bucket_duration.count()),
          capacity_(capacity),
          ema_alpha_(ema_alpha),
          buckets_(capacity) {}

    bool ingest(MetricSample sample) noexcept {
        const auto ts_ns = static_cast<uint64_t>(sample.timestamp.count());
        const uint64_t b_idx = ts_ns / bucket_duration_ns_;
        const size_t slot = b_idx % capacity_;
        auto& target = buckets_[slot];

        if (!target.is_valid || target.bucket_index < b_idx) {
            target.reset(b_idx);
        } else if (target.bucket_index > b_idx) {
            /* Відкидаємо запізнілі точки поза межами буфера */
            return false;
        }

        target.update(sample.value);

        /* Оновлення експоненційного згладжування (EMA) */
        if (!ema_value_) {
            ema_value_ = sample.value;
        } else {
            ema_value_ = (ema_alpha_ * sample.value) + ((1.0 - ema_alpha_) * (*ema_value_));
        }

        return true;
    }

    [[nodiscard]] std::optional<double> ema() const noexcept {
        return ema_value_;
    }

    [[nodiscard]] std::span<const BucketStats> buckets() const noexcept {
        return buckets_;
    }

    [[nodiscard]] uint32_t series_id() const noexcept {
        return series_id_;
    }

private:
    uint32_t series_id_;
    uint64_t bucket_duration_ns_;
    size_t capacity_;
    double ema_alpha_;
    std::optional<double> ema_value_{std::nullopt};
    std::vector<BucketStats> buckets_;
};

} // namespace timeseries
