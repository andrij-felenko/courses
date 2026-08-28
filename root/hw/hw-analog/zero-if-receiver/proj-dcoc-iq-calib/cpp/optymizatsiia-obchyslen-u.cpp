#include <cstdint>
#include <span>
#include <complex>

namespace zero_if {

// Q15 фіксований фільтр DCOC для вбудованих мікроконтролерів без FPU
template <uint8_t ShiftK = 9>
class FixedDcocFilterQ15 {
public:
    constexpr FixedDcocFilterQ15() noexcept = default;

    void process(std::span<std::complex<int16_t>> samples) noexcept {
        for (auto& sample : samples) {
            acc_i_ += static_cast<int32_t>(sample.real()) - (acc_i_ >> ShiftK);
            acc_q_ += static_cast<int32_t>(sample.imag()) - (acc_q_ >> ShiftK);

            const auto mean_i = static_cast<int16_t>(acc_i_ >> ShiftK);
            const auto mean_q = static_cast<int16_t>(acc_q_ >> ShiftK);

            sample = {static_cast<int16_t>(sample.real() - mean_i),
                      static_cast<int16_t>(sample.imag() - mean_q)};
        }
    }

private:
    int32_t acc_i_{0};
    int32_t acc_q_{0};
};

} // namespace zero_if
