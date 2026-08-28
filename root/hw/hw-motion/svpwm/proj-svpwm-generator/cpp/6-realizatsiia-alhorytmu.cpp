#include <cstdint>
#include <array>
#include <algorithm>

namespace motor_control {

struct SvpwmInput {
    float v_alpha{0.0f};      // Напруга alpha [В]
    float v_beta{0.0f};       // Напруга beta [В]
    float v_dc{48.0f};        // Напруга шини DC [В]
    uint16_t arr{2400};       // Межа лічильника таймера
};

struct SvpwmOutput {
    uint16_t ccr_a{0};        // Фаза A
    uint16_t ccr_b{0};        // Фаза B
    uint16_t ccr_c{0};        // Фаза C
    uint8_t sector{0};        // Сектор 1..6
};

class SpaceVectorModulator {
public:
    static constexpr float SQRT3        = 1.732050807568877f;
    static constexpr float SQRT3_HALF   = 0.8660254037844386f;
    static constexpr float ONE_AND_HALF = 1.5f;

    [[nodiscard]] static constexpr SvpwmOutput calculate(const SvpwmInput& in) noexcept {
        if (in.v_dc <= 0.0f || in.arr == 0) {
            const uint16_t mid = in.arr / 2;
            return { mid, mid, mid, 0 };
        }

        // 1. Швидкий пошук сектора
        const float u1 = in.v_beta;
        const float u2 = SQRT3_HALF * in.v_alpha - 0.5f * in.v_beta;
        const float u3 = -SQRT3_HALF * in.v_alpha - 0.5f * in.v_beta;

        const uint8_t code = static_cast<uint8_t>(u1 > 0.0f) |
                            (static_cast<uint8_t>(u2 > 0.0f) << 1) |
                            (static_cast<uint8_t>(u3 > 0.0f) << 2);

        constexpr std::array<uint8_t, 8> sector_map{ 0, 2, 6, 1, 4, 3, 5, 0 };
        const uint8_t sector = sector_map[code];

        // 2. Розрахунок проекцій
        const float scale = static_cast<float>(in.arr) / in.v_dc;
        const float x = SQRT3 * scale * in.v_beta;
        const float y = scale * (ONE_AND_HALF * in.v_alpha + SQRT3_HALF * in.v_beta);
        const float z = scale * (-ONE_AND_HALF * in.v_alpha + SQRT3_HALF * in.v_beta);

        // 3. Вибір часів активних векторів
        float t1 = 0.0f;
        float t2 = 0.0f;
        switch (sector) {
            case 1: t1 = -z; t2 =  x; break;
            case 2: t1 =  z; t2 =  y; break;
            case 3: t1 =  x; t2 = -y; break;
            case 4: t1 = -x; t2 =  z; break;
            case 5: t1 = -y; t2 = -z; break;
            case 6: t1 =  y; t2 = -x; break;
            default: break;
        }

        // 4. Обмеження перемодуляції
        const float arr_f = static_cast<float>(in.arr);
        const float t_sum = t1 + t2;
        if (t_sum > arr_f) {
            const float norm = arr_f / t_sum;
            t1 *= norm;
            t2 *= norm;
        }

        // 5. Симетричні пороги комутації
        const float t0 = arr_f - t1 - t2;
        const float ta = t0 * 0.25f;
        const float tb = ta + t1 * 0.5f;
        const float tc = tb + t2 * 0.5f;

        // 6. Розподіл по каналах
        const auto u_ta = static_cast<uint16_t>(ta);
        const auto u_tb = static_cast<uint16_t>(tb);
        const auto u_tc = static_cast<uint16_t>(tc);

        switch (sector) {
            case 1: return { u_ta, u_tb, u_tc, sector };
            case 2: return { u_tb, u_ta, u_tc, sector };
            case 3: return { u_tc, u_ta, u_tb, sector };
            case 4: return { u_tc, u_tb, u_ta, sector };
            case 5: return { u_tb, u_tc, u_ta, sector };
            case 6: return { u_ta, u_tc, u_tb, sector };
            default: {
                const uint16_t mid = in.arr / 2;
                return { mid, mid, mid, 0 };
            }
        }
    }
};

} // namespace motor_control
