#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <cmath>
#include <limits>
#include <algorithm>

namespace SensorPipeline {

constexpr size_t CicOrder = 3;
constexpr size_t CicDecimationRate = 10;

/* Шаблонний каскадний дециматор CIC */
template <size_t Order = CicOrder, size_t DecimationRate = CicDecimationRate>
class CicFilter {
public:
    constexpr CicFilter() = default;

    [[nodiscard]] bool process(int16_t in_sample, int32_t &out_sample) noexcept {
        int32_t x = in_sample;

        /* Інтегратори */
        integrators_[0] += x;
        integrators_[1] += integrators_[0];
        integrators_[2] += integrators_[1];

        if (++sample_count_ < DecimationRate) {
            return false;
        }
        sample_count_ = 0;

        /* Гребінчасті фільтри */
        int32_t stage = integrators_[Order - 1];
        for (size_t i = 0; i < Order; ++i) {
            int32_t diff = stage - comb_delays_[i];
            comb_delays_[i] = stage;
            stage = diff;
        }

        constexpr int32_t gain = DecimationRate * DecimationRate * DecimationRate;
        out_sample = stage / gain;
        return true;
    }

    void reset() noexcept {
        integrators_.fill(0);
        comb_delays_.fill(0);
        sample_count_ = 0;
    }

private:
    std::array<int32_t, Order> integrators_{};
    std::array<int32_t, Order> comb_delays_{};
    size_t sample_count_{0};
};

/* Статистичний агрегатор Велфорда */
class WelfordStats {
public:
    constexpr WelfordStats() = default;

    void update(float val) noexcept {
        ++count_;
        float delta = val - mean_;
        mean_ += delta / static_cast<float>(count_);
        float delta2 = val - mean_;
        m2_ += delta * delta2;

        min_val_ = std::min(min_val_, val);
        max_val_ = std::max(max_val_, val);
    }

    [[nodiscard]] uint32_t count() const noexcept { return count_; }
    [[nodiscard]] float mean() const noexcept { return mean_; }
    [[nodiscard]] float variance() const noexcept {
        return (count_ > 1) ? (m2_ / static_cast<float>(count_ - 1)) : 0.0f;
    }
    [[nodiscard]] float rms() const noexcept {
        return std::sqrt(mean_ * mean_ + variance());
    }
    [[nodiscard]] float peak_to_peak() const noexcept {
        return (max_val_ > min_val_) ? (max_val_ - min_val_) : 0.0f;
    }
    [[nodiscard]] float crest_factor() const noexcept {
        float r = rms();
        if (r < 1e-4f) return 1.0f;
        float peak = std::max(std::abs(min_val_), std::abs(max_val_));
        return peak / r;
    }

    void reset() noexcept {
        count_ = 0;
        mean_ = 0.0f;
        m2_ = 0.0f;
        min_val_ = std::numeric_limits<float>::infinity();
        max_val_ = -std::numeric_limits<float>::infinity();
    }

private:
    uint32_t count_{0};
    float mean_{0.0f};
    float m2_{0.0f};
    float min_val_{std::numeric_limits<float>::infinity()};
    float max_val_{-std::numeric_limits<float>::infinity()};
};

/* Компресор лінійних трендів Swing Door Trending */
class SdtTrendCompressor {
public:
    struct PivotPoint {
        uint32_t timestamp;
        float value;
    };

    explicit constexpr SdtTrendCompressor(float tolerance) noexcept
        : tolerance_(tolerance) {}

    void init(uint32_t t_start, float y_start) noexcept {
        t0_ = t_start;
        y0_ = y_start;
        prev_t_ = t_start;
        prev_y_ = y_start;
        s_upper_ = std::numeric_limits<float>::infinity();
        s_lower_ = -std::numeric_limits<float>::infinity();
    }

    [[nodiscard]] std::pair<bool, PivotPoint> push(uint32_t t_now, float y_now) noexcept {
        if (t_now <= t0_) {
            prev_t_ = t_now;
            prev_y_ = y_now;
            return {false, {}};
        }

        float dt = static_cast<float>(t_now - t0_);
        float slope_up = (y_now - (y0_ + tolerance_)) / dt;
        float slope_low = (y_now - (y0_ - tolerance_)) / dt;

        s_upper_ = std::min(s_upper_, slope_up);
        s_lower_ = std::max(s_lower_, slope_low);

        if (s_lower_ > s_upper_) {
            PivotPoint pivot{prev_t_, prev_y_};

            t0_ = prev_t_;
            y0_ = prev_y_;
            dt = static_cast<float>(t_now - t0_);
            s_upper_ = (dt > 0.0f) ? ((y_now - (y0_ + tolerance_)) / dt) : std::numeric_limits<float>::infinity();
            s_lower_ = (dt > 0.0f) ? ((y_now - (y0_ - tolerance_)) / dt) : -std::numeric_limits<float>::infinity();
            prev_t_ = t_now;
            prev_y_ = y_now;
            return {true, pivot};
        }

        prev_t_ = t_now;
        prev_y_ = y_now;
        return {false, {}};
    }

    [[nodiscard]] float baseline() const noexcept { return y0_; }

private:
    float tolerance_{0.5f};
    uint32_t t0_{0};
    float y0_{0.0f};
    uint32_t prev_t_{0};
    float prev_y_{0.0f};
    float s_upper_{std::numeric_limits<float>::infinity()};
    float s_lower_{-std::numeric_limits<float>::infinity()};
};

/* Структура бінарного фрейму */
#pragma pack(push, 1)
struct TelemetryPayload {
    uint32_t timestamp;
    uint8_t  status;
    int16_t  baseline;
    int16_t  mean;
    uint16_t rms;
    uint16_t peak_to_peak;
    uint8_t  crest_factor_x10;
    uint16_t sdt_p1;
    uint16_t sdt_p2;
    uint16_t crc16;
};
#pragma pack(pop)

static_assert(sizeof(TelemetryPayload) == 20, "TelemetryPayload must be exactly 20 bytes");

[[nodiscard]] constexpr uint16_t encode_zigzag16(int16_t n) noexcept {
    return static_cast<uint16_t>((n << 1) ^ (n >> 15));
}

[[nodiscard]] uint16_t compute_crc16(std::span<const uint8_t> bytes) noexcept {
    uint16_t crc = 0xFFFF;
    for (uint8_t byte : bytes) {
        crc ^= static_cast<uint16_t>(byte) << 8;
        for (int b = 0; b < 8; ++b) {
            crc = (crc & 0x8000) ? ((crc << 1) ^ 0x1021) : (crc << 1);
        }
    }
    return crc;
}

[[nodiscard]] TelemetryPayload serialize_window(
    uint32_t timestamp, uint8_t status,
    const WelfordStats &stats, const SdtTrendCompressor &sdt,
    uint16_t p1, uint16_t p2) noexcept
{
    TelemetryPayload payload{};
    payload.timestamp = timestamp;
    payload.status = status;
    payload.baseline = static_cast<int16_t>(std::lround(sdt.baseline()));
    payload.mean = static_cast<int16_t>(std::lround(stats.mean()));
    payload.rms = static_cast<uint16_t>(std::lround(stats.rms()));
    payload.peak_to_peak = static_cast<uint16_t>(std::lround(stats.peak_to_peak()));

    float cf = std::clamp(stats.crest_factor() * 10.0f, 0.0f, 255.0f);
    payload.crest_factor_x10 = static_cast<uint8_t>(std::lround(cf));
    payload.sdt_p1 = p1;
    payload.sdt_p2 = p2;

    auto span_bytes = std::span<const uint8_t>(
        reinterpret_cast<const uint8_t *>(&payload),
        sizeof(TelemetryPayload) - sizeof(uint16_t));
    payload.crc16 = compute_crc16(span_bytes);
    return payload;
}

} // namespace SensorPipeline
