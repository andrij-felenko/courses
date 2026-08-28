// CostasLoop.hpp - Idiomatic C++20 implementation of Costas Loop SDR Demodulator
#pragma once
#include <vector>
#include <span>
#include <cmath>
#include <numbers>
#include <algorithm>

namespace sdr {

class CostasLoop {
public:
    struct Config {
        double sampleRate{48000.0};
        double carrierFreq{10000.0};
        double lpfCutoff{3000.0};
        double damping{0.707};
        double loopBandwidth{0.05};
    };

    explicit CostasLoop(const Config& cfg)
        : m_phase(0.0)
        , m_nominalFreq(2.0 * std::numbers::pi * cfg.carrierFreq / cfg.sampleRate)
        , m_freqOffset(0.0)
        , m_lpfI(0.0)
        , m_lpfQ(0.0)
        , m_integrator(0.0)
    {
        double dt = 1.0 / cfg.sampleRate;
        double rc = 1.0 / (2.0 * std::numbers::pi * cfg.lpfCutoff);
        m_alpha = dt / (rc + dt);

        double denom = 1.0 + 2.0 * cfg.damping * cfg.loopBandwidth + cfg.loopBandwidth * cfg.loopBandwidth;
        m_kp = (4.0 * cfg.damping * cfg.loopBandwidth) / denom;
        m_ki = (4.0 * cfg.loopBandwidth * cfg.loopBandwidth) / denom;
    }

    [[nodiscard]] double processSample(double inputSample) noexcept {
        const double ncoI = std::cos(m_phase);
        const double ncoQ = -std::sin(m_phase);

        const double rawI = inputSample * ncoI * 2.0;
        const double rawQ = inputSample * ncoQ * 2.0;

        // Ітерація однополюсного IIR ФНЧ
        m_lpfI += m_alpha * (rawI - m_lpfI);
        m_lpfQ += m_alpha * (rawQ - m_lpfQ);

        // Фазовий дискримінатор петлі Костаса
        const double error = m_lpfI * m_lpfQ;

        // Пропорційно-інтегральний фільтр (PI)
        m_integrator += m_ki * error;
        const double control = m_kp * error + m_integrator;

        // Оновлення NCO
        m_phase += (m_nominalFreq + control);
        m_phase = std::fmod(m_phase, 2.0 * std::numbers::pi);
        if (m_phase < 0.0) {
            m_phase += 2.0 * std::numbers::pi;
        }

        return m_lpfI;
    }

    void processBlock(std::span<const float> input, std::span<float> output) noexcept {
        const std::size_t count = std::min(input.size(), output.size());
        for (std::size_t i = 0; i < count; ++i) {
            output[i] = static_cast<float>(processSample(input[i]));
        }
    }

    [[nodiscard]] double currentPhaseError() const noexcept { return m_lpfQ; }
    [[nodiscard]] double estimatedFrequencyOffsetHz(double sampleRate) const noexcept {
        return (m_integrator * sampleRate) / (2.0 * std::numbers::pi);
    }

private:
    double m_phase;
    double m_nominalFreq;
    double m_freqOffset;
    double m_alpha;
    double m_kp;
    double m_ki;
    double m_lpfI;
    double m_lpfQ;
    double m_integrator;
};

} // namespace sdr
