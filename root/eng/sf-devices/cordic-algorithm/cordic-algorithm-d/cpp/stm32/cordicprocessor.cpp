#include <cstdint>
#include <array>
#include <utility>

namespace embedded::math {

class CordicProcessor {
public:
    static constexpr int Iterations = 31;
    static constexpr int32_t GainInvQ30 = 652032896; /* 0.607252935 * 2^30 */

    struct TrigonometricResult {
        int32_t cos_q30;
        int32_t sin_q30;
    };

    struct PolarResult {
        int32_t magnitude_q30;
        int32_t phase_bam;
    };

    /* Таблиця кутів у форматі BAM (constexpr для розташування у Flash) */
    static constexpr std::array<int32_t, Iterations> AngleTableBAM = {
        0x20000000, 0x12E4051E, 0x09FB385B, 0x051111D4,
        0x028B0D43, 0x0145D7E1, 0x00A2F61E, 0x00517C55,
        0x0028BE53, 0x00145F2F, 0x000A2F98, 0x000517CC,
        0x00028BE6, 0x000145F3, 0x0000A2FA, 0x0000517D,
        0x000028BE, 0x0000145F, 0x00000A30, 0x00000518,
        0x0000028C, 0x00000146, 0x000000A3, 0x00000051,
        0x00000029, 0x00000014, 0x0000000A, 0x00000005,
        0x00000003, 0x00000001, 0x00000001
    };

    /* Обчислення пари sin/cos за алгоритмом CORDIC */
    [[nodiscard]] static constexpr TrigonometricResult calculateSinCos(int32_t angle_bam) noexcept {
        int32_t x = GainInvQ30;
        int32_t y = 0;
        int32_t z = angle_bam;

        /* Редукція квадранта кута */
        if (angle_bam > 0x40000000) {
            x = -GainInvQ30;
            z = static_cast<int32_t>(static_cast<uint32_t>(angle_bam) - 0x80000000U);
        } else if (angle_bam < -0x40000000) {
            x = -GainInvQ30;
            z = static_cast<int32_t>(static_cast<uint32_t>(angle_bam) + 0x80000000U);
        }

        /* Обчислювальний цикл CORDIC */
        for (int i = 0; i < Iterations; ++i) {
            const int32_t x_shift = x >> i;
            const int32_t y_shift = y >> i;

            if (z >= 0) {
                x -= y_shift;
                y += x_shift;
                z -= AngleTableBAM[i];
            } else {
                x += y_shift;
                y -= x_shift;
                z += AngleTableBAM[i];
            }
        }

        return TrigonometricResult{x, y};
    }

    /* Перетворення прямокутних координат у полярні */
    [[nodiscard]] static constexpr PolarResult calculatePolar(int32_t x_in_q30, int32_t y_in_q30) noexcept {
        int32_t x = x_in_q30;
        int32_t y = y_in_q30;
        int32_t z = 0;

        if (x_in_q30 < 0) {
            x = -x_in_q30;
            y = -y_in_q30;
            z = (y_in_q30 >= 0) ? static_cast<int32_t>(0x7FFFFFFF) : static_cast<int32_t>(0x80000000);
        }

        for (int i = 0; i < Iterations; ++i) {
            const int32_t x_shift = x >> i;
            const int32_t y_shift = y >> i;

            if (y >= 0) {
                x += y_shift;
                y -= x_shift;
                z += AngleTableBAM[i];
            } else {
                x -= y_shift;
                y += x_shift;
                z -= AngleTableBAM[i];
            }
        }

        const auto scaled_mag = static_cast<int32_t>((static_cast<int64_t>(x) * GainInvQ30) >> 30);
        return PolarResult{scaled_mag, z};
    }
};

} /* namespace embedded::math */
