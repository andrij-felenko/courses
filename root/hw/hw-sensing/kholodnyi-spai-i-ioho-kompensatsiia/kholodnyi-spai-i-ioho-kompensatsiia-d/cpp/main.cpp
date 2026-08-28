/* cjc_thermocouple_k.hpp */
#include <array>
#include <cmath>
#include <expected>
#include <span>

namespace sensing {

enum class SensorError {
    ColdJunctionOutOfRange,
    VoltageOutOfRange,
    HardwareFault
};

struct Celsius {
    float value;
    constexpr explicit Celsius(float v = 0.0f) : value(v) {}
    constexpr auto operator<=>(const Celsius&) const = default;
};

struct Millivolts {
    float value;
    constexpr explicit Millivolts(float v = 0.0f) : value(v) {}
    constexpr auto operator<=>(const Millivolts&) const = default;
};

class NistTypeK {
public:
    /* Пряме перетворення: T_cjc -> V_cjc */
    [[nodiscard]] static constexpr Millivolts temp_to_mv(Celsius temp) noexcept {
        const float t = temp.value;
        if (t < 0.0f) {
            constexpr std::array<float, 10> c = {
                0.0f, 3.945013e-2f, 2.362237e-5f, -3.285891e-7f,
                -4.990483e-9f, -6.750906e-11f, -5.741032e-13f, -3.108894e-15f,
                -1.045161e-17f, -1.988927e-20f
            };
            return Millivolts(evaluate_horner(c, t));
        } else {
            constexpr std::array<float, 10> c = {
                -1.7600413686e-2f, 3.8921204975e-2f, 1.8558770032e-5f,
                -9.9457592874e-8f, 3.1840945719e-10f, -5.6072844889e-13f,
                5.6075059059e-16f, -3.2020720003e-19f, 9.7151147152e-23f,
                -1.2104721275e-26f
            };
            float mv = evaluate_horner(c, t);
            constexpr float a0 = 0.1185976f;
            constexpr float a1 = -1.183432e-4f;
            constexpr float a2 = 126.9686f;
            const float diff = t - a2;
            mv += a0 * std::exp(a1 * diff * diff);
            return Millivolts(mv);
        }
    }

    /* Зворотне перетворення: V_total -> T_hot */
    [[nodiscard]] static constexpr Celsius mv_to_temp(Millivolts mv) noexcept {
        const float v = mv.value;
        if (v < 0.0f) {
            constexpr std::array<float, 9> d = {
                0.0f, 2.5173462e1f, -1.1662878f, -1.0833638f,
                -8.9773540e-1f, -3.7342377e-1f, -8.6632643e-2f, -1.0450598e-2f,
                -5.1920577e-4f
            };
            return Celsius(evaluate_horner(d, v));
        } else if (v <= 20.644f) {
            constexpr std::array<float, 10> d = {
                0.0f, 2.508355e1f, 7.860106e-2f, -2.503131e-1f,
                8.315270e-2f, -1.228034e-2f, 9.804036e-4f, -4.413030e-5f,
                1.057734e-6f, -1.052755e-8f
            };
            return Celsius(evaluate_horner(d, v));
        } else {
            constexpr std::array<float, 7> d = {
                -1.318058e2f, 4.830222e1f, -1.646031f, 5.464731e-2f,
                -9.650715e-4f, 8.802193e-6f, -3.110810e-8f
            };
            return Celsius(evaluate_horner(d, v));
        }
    }

    /* Канонічний конвеєр CJC із контролем меж і поверненням std::expected */
    [[nodiscard]] static std::expected<Celsius, SensorError> calculate(
        Millivolts v_meas,
        Celsius t_cjc) noexcept
    {
        if (t_cjc.value < -40.0f || t_cjc.value > 125.0f) {
            return std::unexpected(SensorError::ColdJunctionOutOfRange);
        }

        const auto v_cjc = temp_to_mv(t_cjc);
        const auto v_total = Millivolts(v_meas.value + v_cjc.value);

        if (v_total.value < -5.891f || v_total.value > 54.886f) {
            return std::unexpected(SensorError::VoltageOutOfRange);
        }

        return mv_to_temp(v_total);
    }

private:
    /* Чисельно стабільна схема Горнера */
    template <std::size_t N>
    [[nodiscard]] static constexpr float evaluate_horner(
        const std::array<float, N>& coeff,
        float x) noexcept
    {
        float result = coeff[N - 1];
        for (std::size_t i = N - 1; i > 0; --i) {
            result = result * x + coeff[i - 1];
        }
        return result;
    }
};

} // namespace sensing
