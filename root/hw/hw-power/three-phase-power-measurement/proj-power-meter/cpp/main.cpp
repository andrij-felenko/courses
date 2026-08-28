// cpp
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <span>
#include <algorithm>
#include <numeric>
#include <expected>

namespace power_meter {

constexpr size_t SamplesPerPeriod = 128;
constexpr size_t NumPhases = 3;

struct PhaseMetrics {
    float v_rms{0.0f};
    float i_rms{0.0f};
    float p_active{0.0f};
    float q_reactive{0.0f};
    float s_apparent{0.0f};
    float power_factor{1.0f};
};

struct SystemMetrics {
    std::array<PhaseMetrics, NumPhases> phases{};
    float p_total{0.0f};
    float q_total{0.0f};
    float s_total{0.0f};
    float pf_total{1.0f};
    float i_neutral_rms{0.0f};
    double energy_kwh_accumulated{0.0};
};

struct Calibration {
    float v_scale{1.0f};
    float i_scale{1.0f};
    float v_offset{0.0f};
    float i_offset{0.0f};
};

enum class MeterError {
    InvalidBufferSize,
    NullCalibration,
    ComputationOverflow
};

class ThreePhaseAnalyzer {
public:
    explicit ThreePhaseAnalyzer(Calibration cal) : cal_(cal) {}

    [[nodiscard]] std::expected<SystemMetrics, MeterError> analyze_frame(
        std::span<const float> raw_v,
        std::span<const float> raw_i,
        double current_kwh_acc = 0.0) const noexcept
    {
        if (raw_v.size() != NumPhases * SamplesPerPeriod ||
            raw_i.size() != NumPhases * SamplesPerPeriod)
        {
            return std::unexpected(MeterError::InvalidBufferSize);
        }

        SystemMetrics sys{};
        sys.energy_kwh_accumulated = current_kwh_acc;
        float sum_p_total = 0.0f;
        float sum_q_total = 0.0f;
        constexpr int q_shift = SamplesPerPeriod / 4;

        for (size_t ph = 0; ph < NumPhases; ++ph) {
            auto v_phase = raw_v.subspan(ph * SamplesPerPeriod, SamplesPerPeriod);
            auto i_phase = raw_i.subspan(ph * SamplesPerPeriod, SamplesPerPeriod);

            float sum_v2 = 0.0f;
            float sum_i2 = 0.0f;
            float sum_p  = 0.0f;
            float sum_q  = 0.0f;

            for (size_t k = 0; k < SamplesPerPeriod; ++k) {
                const float v = (v_phase[k] - cal_.v_offset) * cal_.v_scale;
                const float i = (i_phase[k] - cal_.i_offset) * cal_.i_scale;

                sum_v2 += v * v;
                sum_i2 += i * i;
                sum_p  += v * i;

                const size_t k_q = (k >= q_shift) ? (k - q_shift) : (k + SamplesPerPeriod - q_shift);
                const float v_90 = (v_phase[k_q] - cal_.v_offset) * cal_.v_scale;
                sum_q += v_90 * i;
            }

            auto& res = sys.phases[ph];
            res.v_rms = std::sqrt(sum_v2 / static_cast<float>(SamplesPerPeriod));
            res.i_rms = std::sqrt(sum_i2 / static_cast<float>(SamplesPerPeriod));
            res.p_active = sum_p / static_cast<float>(SamplesPerPeriod);
            res.q_reactive = sum_q / static_cast<float>(SamplesPerPeriod);
            res.s_apparent = res.v_rms * res.i_rms;

            if (res.s_apparent > 1e-5f) {
                res.power_factor = std::clamp(res.p_active / res.s_apparent, -1.0f, 1.0f);
            }

            sum_p_total += res.p_active;
            sum_q_total += res.q_reactive;
        }

        // Струм нейтрального провідника
        float sum_in2 = 0.0f;
        for (size_t k = 0; k < SamplesPerPeriod; ++k) {
            const float iA = (raw_i[0 * SamplesPerPeriod + k] - cal_.i_offset) * cal_.i_scale;
            const float iB = (raw_i[1 * SamplesPerPeriod + k] - cal_.i_offset) * cal_.i_scale;
            const float iC = (raw_i[2 * SamplesPerPeriod + k] - cal_.i_offset) * cal_.i_scale;
            const float iN = iA + iB + iC;
            sum_in2 += iN * iN;
        }
        sys.i_neutral_rms = std::sqrt(sum_in2 / static_cast<float>(SamplesPerPeriod));

        sys.p_total = sum_p_total;
        sys.q_total = sum_q_total;
        sys.s_total = std::hypot(sys.p_total, sys.q_total);
        sys.pf_total = (sys.s_total > 1e-5f) ? (sys.p_total / sys.s_total) : 1.0f;

        constexpr double frame_duration_sec = 0.02;
        const double energy_joules = static_cast<double>(sys.p_total) * frame_duration_sec;
        sys.energy_kwh_accumulated += energy_joules / 3600000.0;

        return sys;
    }

private:
    Calibration cal_;
};

} // namespace power_meter
