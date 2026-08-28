// decibel_dsp.hpp — Ідіоматична C++ бібліотека акустичних перетворень (C++20)
#pragma once

#include <bit>
#include <cmath>
#include <concepts>
#include <numbers>
#include <numeric>
#include <span>
#include <vector>

namespace dsp::acoustics {

// Опорні фізичні константи
inline constexpr double p0_air_pa       = 20.0e-6;      // Опорний звуковий тиск: 20 мкПа
inline constexpr double i0_air_w_m2     = 1.0e-12;      // Опорна інтенсивність: 1 пВт/м²
inline constexpr double v0_dbu          = 0.7745966692; // 0 dBu: 0.7746 В на 600 Ом
inline constexpr double v0_dbv          = 1.0;          // 0 dBV: строго 1.0 В RMS
inline constexpr double p0_dbm_watts    = 1.0e-3;       // 0 dBm: 1 мВт

// Часові константи детектора (секунди)
inline constexpr double tau_fast_sec    = 0.125;        // Fast: 125 мс
inline constexpr double tau_slow_sec    = 1.000;        // Slow: 1000 мс

// Базові логарифмічні функції
[[nodiscard]] constexpr double to_db_power(double p, double p0 = 1.0) noexcept {
    if (p <= 0.0 || p0 <= 0.0) {
        return -std::numeric_limits<double>::infinity();
    }
    return 10.0 * std::log10(p / p0);
}

[[nodiscard]] constexpr double to_db_amplitude(double v, double v0 = 1.0) noexcept {
    if (v <= 0.0 || v0 <= 0.0) {
        return -std::numeric_limits<double>::infinity();
    }
    return 20.0 * std::log10(v / v0);
}

[[nodiscard]] constexpr double from_db_power(double db) noexcept {
    return std::pow(10.0, db / 10.0);
}

[[nodiscard]] constexpr double from_db_amplitude(double db) noexcept {
    return std::pow(10.0, db / 20.0);
}

// Електричні опорні величини
[[nodiscard]] constexpr double voltage_to_dbu(double v_rms) noexcept {
    return to_db_amplitude(v_rms, v0_dbu);
}

[[nodiscard]] constexpr double dbu_to_voltage(double dbu) noexcept {
    return v0_dbu * from_db_amplitude(dbu);
}

[[nodiscard]] constexpr double voltage_to_dbv(double v_rms) noexcept {
    return to_db_amplitude(v_rms, v0_dbv);
}

[[nodiscard]] constexpr double dbv_to_voltage(double dbv) noexcept {
    return v0_dbv * from_db_amplitude(dbv);
}

[[nodiscard]] constexpr double power_to_dbm(double power_watts) noexcept {
    return to_db_power(power_watts, p0_dbm_watts);
}

[[nodiscard]] constexpr double dbm_to_power(double dbm) noexcept {
    return p0_dbm_watts * from_db_power(dbm);
}

[[nodiscard]] constexpr double voltage_to_dbm(double v_rms, double load_ohms) noexcept {
    if (load_ohms <= 0.0 || v_rms <= 0.0) {
        return -std::numeric_limits<double>::infinity();
    }
    const double p_watts = (v_rms * v_rms) / load_ohms;
    return power_to_dbm(p_watts);
}

// Акустичні розрахунки звукового тиску
[[nodiscard]] constexpr double pressure_to_spl(double p_rms_pa) noexcept {
    return to_db_amplitude(p_rms_pa, p0_air_pa);
}

[[nodiscard]] constexpr double spl_to_pressure(double spl_db) noexcept {
    return p0_air_pa * from_db_amplitude(spl_db);
}

// Швидке наближення двійкового та десяткового логарифмів (C++20 std::countl_zero)
[[nodiscard]] constexpr float fast_log2(uint32_t val) noexcept {
    if (val == 0) return -128.0f;
    const int clz = std::countl_zero(val);
    const int exp = 31 - clz;
    const float frac = static_cast<float>(val - (1u << exp)) / static_cast<float>(1u << exp);
    return static_cast<float>(exp) + (frac * (1.442695f - 0.442695f * frac));
}

[[nodiscard]] constexpr float fast_log10(uint32_t val) noexcept {
    return fast_log2(val) * 0.30102999566f;
}

// Енергетичне підсумовування некогерентних джерел звуку
[[nodiscard]] inline double sum_noncoherent_spl(std::span<const double> levels_db) noexcept {
    if (levels_db.empty()) {
        return -std::numeric_limits<double>::infinity();
    }
    const double sum_linear = std::accumulate(
        levels_db.begin(), levels_db.end(), 0.0,
        [](double acc, double db) noexcept {
            return acc + std::pow(10.0, db / 10.0);
        });
    return 10.0 * std::log10(sum_linear);
}

// Розрахунок середньоквадратичного значення (RMS)
[[nodiscard]] inline double calculate_rms(std::span<const double> samples) noexcept {
    if (samples.empty()) return 0.0;
    const double sum_sq = std::accumulate(
        samples.begin(), samples.end(), 0.0,
        [](double acc, double s) noexcept {
            return acc + s * s;
        });
    return std::sqrt(sum_sq / static_cast<double>(samples.size()));
}

// Цифровий біквадратний фільтр (Direct Form II Transposed)
class BiquadFilter {
public:
    constexpr BiquadFilter(double b0, double b1, double b2, double a1, double a2) noexcept
        : b0_{b0}, b1_{b1}, b2_{b2}, a1_{a1}, a2_{a2} {}

    constexpr void reset() noexcept {
        s1_ = 0.0;
        s2_ = 0.0;
    }

    [[nodiscard]] constexpr double process(double in) noexcept {
        const double out = b0_ * in + s1_;
        s1_ = b1_ * in - a1_ * out + s2_;
        s2_ = b2_ * in - a2_ * out;
        return out;
    }

private:
    double b0_, b1_, b2_;
    double a1_, a2_;
    double s1_{0.0};
    double s2_{0.0};
};

// Каскадний A-weighting фільтр за стандартом IEC 61672-1 (fs = 48 кГц)
class AWeightingFilter {
public:
    AWeightingFilter() noexcept {
        stages_.emplace_back(0.169994948147430, 0.339989896294859, 0.169994948147430,
                            -0.270409810398048, -0.050478631380962);
        stages_.emplace_back(1.0, -2.0, 1.0,
                            -1.990047454833980, 0.990072166948332);
        stages_.emplace_back(1.0, 2.0, 1.0,
                            -0.485685718742828, 0.0);
    }

    void reset() noexcept {
        for (auto& stage : stages_) {
            stage.reset();
        }
    }

    [[nodiscard]] double process(double sample) noexcept {
        double current = sample;
        for (auto& stage : stages_) {
            current = stage.process(current);
        }
        return current;
    }

    void process_buffer(std::span<const double> input, std::span<double> output) noexcept {
        const size_t n = std::min(input.size(), output.size());
        for (size_t i = 0; i < n; ++i) {
            output[i] = process(input[i]);
        }
    }

private:
    std::vector<BiquadFilter> stages_;
};

// Детектор експоненційного часового зважування (Fast / Slow)
class TimeWeightingDetector {
public:
    TimeWeightingDetector(double tau_sec, double fs_hz) noexcept
        : alpha_{1.0 - std::exp(-1.0 / (fs_hz * tau_sec))} {}

    void reset() noexcept {
        mean_square_ = 0.0;
    }

    [[nodiscard]] double update(double sample_pa) noexcept {
        const double x2 = sample_pa * sample_pa;
        mean_square_ = (1.0 - alpha_) * mean_square_ + alpha_ * x2;
        const double p_rms = std::sqrt(mean_square_);
        return pressure_to_spl(p_rms);
    }

private:
    double alpha_;
    double mean_square_{0.0};
};

} // namespace dsp::acoustics
