#include <cstdint>

namespace dsp {

template <uint8_t ShiftK = 3>
class LowPassIirFilter {
public:
    constexpr LowPassIirFilter() noexcept = default;

    explicit constexpr LowPassIirFilter(int16_t initial_val) noexcept 
        : state_q16_(static_cast<int32_t>(initial_val) << 16) {}

    constexpr void reset(int16_t val) noexcept {
        state_q16_ = static_cast<int32_t>(val) << 16;
    }

    [[nodiscard]] constexpr int16_t update(int16_t input) noexcept {
        const int32_t input_q16 = static_cast<int32_t>(input) << 16;
        state_q16_ += (input_q16 - state_q16_) >> ShiftK;
        return static_cast<int16_t>((state_q16_ + (1 << 15)) >> 16);
    }

    [[nodiscard]] constexpr int32_t state_q16() const noexcept {
        return state_q16_;
    }

private:
    int32_t state_q16_{0};
};

} // namespace dsp
