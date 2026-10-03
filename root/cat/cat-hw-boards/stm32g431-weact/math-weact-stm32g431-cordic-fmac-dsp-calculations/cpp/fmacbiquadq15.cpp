// C++ клас квантування та масштабування коефіцієнтів біквадратного фільтра у Q15
#include <cstdint>
#include <cmath>
#include <array>
#include <algorithm>

struct FmacBiquadQ15 {
    std::array<int16_t, 3> b_q15;
    std::array<int16_t, 2> a_q15;
    uint8_t scale_shift;
};

class FmacQuantizer {
public:
    static FmacBiquadQ15 quantize(const std::array<double, 3>& b, const std::array<double, 3>& a) {
        FmacBiquadQ15 result{};
        double max_val = std::abs(b[0]);
        for (size_t i = 0; i < 3; ++i) {
            max_val = std::max({max_val, std::abs(b[i]), std::abs(a[i])});
        }

        uint8_t shift = 0;
        if (max_val >= 1.0) {
            shift = static_cast<uint8_t>(std::ceil(std::log2(max_val)));
        }
        const double scale = static_cast<double>(1U << shift);

        for (size_t i = 0; i < 3; ++i) {
            result.b_q15[i] = static_cast<int16_t>(std::round((b[i] / scale) * 32767.0));
        }
        result.a_q15[0] = static_cast<int16_t>(std::round((a[1] / scale) * 32767.0));
        result.a_q15[1] = static_cast<int16_t>(std::round((a[2] / scale) * 32767.0));
        result.scale_shift = shift;

        return result;
    }
};
