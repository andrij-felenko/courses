#include <cstdint>
#include <array>

namespace motor_control::fixed_point {

struct SvpwmQ15Input {
    int16_t q_alpha{0};       // V_alpha / V_dc в форматі Q15
    int16_t q_beta{0};        // V_beta / V_dc в форматі Q15
    uint16_t arr{2400};       // Період лічильника таймера
};

struct SvpwmQ15Output {
    uint16_t ccr_a{0};
    uint16_t ccr_b{0};
    uint16_t ccr_c{0};
    uint8_t sector{0};
};

class Q15SvpwmEngine {
public:
    static constexpr int32_t Q15_ONE          = 32768;
    static constexpr int32_t Q15_SQRT3        = 56756;
    static constexpr int32_t Q15_SQRT3_HALF   = 28378;
    static constexpr int32_t Q15_ONE_AND_HALF = 49152;

    [[nodiscard]] static constexpr SvpwmQ15Output process(const SvpwmQ15Input& in) noexcept {
        const int32_t u1 = in.q_beta;
        const int32_t u2 = (Q15_SQRT3_HALF * in.q_alpha - (Q15_ONE / 2) * in.q_beta) >> 15;
        const int32_t u3 = (-Q15_SQRT3_HALF * in.q_alpha - (Q15_ONE / 2) * in.q_beta) >> 15;

        const uint8_t code = static_cast<uint8_t>(u1 > 0) |
                            (static_cast<uint8_t>(u2 > 0) << 1) |
                            (static_cast<uint8_t>(u3 > 0) << 2);

        constexpr std::array<uint8_t, 8> map{ 0, 2, 6, 1, 4, 3, 5, 0 };
        const uint8_t sector = map[code];

        const int32_t x = (((Q15_SQRT3 * in.q_beta) >> 15) * in.arr) >> 15;
        const int32_t y = (((Q15_ONE_AND_HALF * in.q_alpha + Q15_SQRT3_HALF * in.q_beta) >> 15) * in.arr) >> 15;
        const int32_t z = (((-Q15_ONE_AND_HALF * in.q_alpha + Q15_SQRT3_HALF * in.q_beta) >> 15) * in.arr) >> 15;

        int32_t t1 = 0;
        int32_t t2 = 0;
        switch (sector) {
            case 1: t1 = -z; t2 =  x; break;
            case 2: t1 =  z; t2 =  y; break;
            case 3: t1 =  x; t2 = -y; break;
            case 4: t1 = -x; t2 =  z; break;
            case 5: t1 = -y; t2 = -z; break;
            case 6: t1 =  y; t2 = -x; break;
            default: break;
        }

        const int32_t t_sum = t1 + t2;
        if (t_sum > in.arr && t_sum > 0) {
            t1 = (t1 * in.arr) / t_sum;
            t2 = (t2 * in.arr) / t_sum;
        }

        const int32_t t0 = in.arr - t1 - t2;
        const auto ta = static_cast<uint16_t>(t0 >> 2);
        const auto tb = static_cast<uint16_t>(ta + (t1 >> 1));
        const auto tc = static_cast<uint16_t>(tb + (t2 >> 1));

        switch (sector) {
            case 1: return { ta, tb, tc, sector };
            case 2: return { tb, ta, tc, sector };
            case 3: return { tc, ta, tb, sector };
            case 4: return { tc, tb, ta, sector };
            case 5: return { tb, tc, ta, sector };
            case 6: return { ta, tc, tb, sector };
            default: {
                const uint16_t mid = in.arr >> 1;
                return { mid, mid, mid, 0 };
            }
        }
    }
};

} // namespace motor_control::fixed_point
