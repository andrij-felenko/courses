#include <cstdint>
#include <optional>
#include <span>

class TrueRmsQ15Engine {
public:
    explicit constexpr TrueRmsQ15Engine(int32_t alpha_q15 = 32737, int16_t hysteresis = 8) noexcept
        : alpha_q15_{alpha_q15}, hysteresis_{hysteresis} {}

    void reset() noexcept {
        x_prev_ = 0;
        y_prev_q15_ = 0;
        sum_sq_ = 0;
        sample_count_ = 0;
        armed_ = false;
    }

    [[nodiscard]] std::optional<uint32_t> process_sample(int16_t raw_adc) noexcept {
        const auto x = static_cast<int32_t>(raw_adc);

        // IIR DC-Blocker у фіксованій комірці Q15
        const int32_t diff = (x - x_prev_) << 15;
        const auto feedback = static_cast<int32_t>((static_cast<int64_t>(alpha_q15_) * y_prev_q15_) >> 15);
        const int32_t y_q15 = diff + feedback;

        x_prev_ = x;
        y_prev_q15_ = y_q15;

        const int32_t y_signal = y_q15 >> 15;
        sum_sq_ += static_cast<uint64_t>(static_cast<int64_t>(y_signal) * y_signal);
        ++sample_count_;

        if (y_signal < -hysteresis_) {
            armed_ = true;
        } else if (armed_ && y_signal >= 0 && sample_count_ >= 100) {
            const uint64_t mean_sq = sum_sq_ / sample_count_;
            const uint32_t rms = integer_sqrt(mean_sq);

            sum_sq_ = 0;
            sample_count_ = 0;
            armed_ = false;
            return rms;
        }

        return std::nullopt;
    }

private:
    static uint32_t integer_sqrt(uint64_t val) noexcept {
        uint64_t b{}, q{};
        if (val == 0) return 0;
        for (b = uint64_t{1} << 62; b > 0; b >>= 2) {
            const uint64_t t = q + b;
            q >>= 1;
            if (val >= t) {
                val -= t;
                q += b;
            }
        }
        return static_cast<uint32_t>(q);
    }

    int32_t  x_prev_{0};
    int32_t  y_prev_q15_{0};
    uint64_t sum_sq_{0};
    uint32_t sample_count_{0};
    int32_t  alpha_q15_{32737};
    int16_t  hysteresis_{8};
    bool     armed_{false};
};
