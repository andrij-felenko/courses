#include <cstdint>
#include <cmath>
#include <array>
#include <optional>

namespace Sensors {

enum class PirState : uint8_t {
    Idle,
    PositivePeakDetected,
    NegativePeakDetected,
    MotionConfirmed
};

struct PirConfig {
    static constexpr uint16_t DefaultBaselineAdc = 2048;
    static constexpr uint16_t ThresholdOffsetAdc = 350;
    static constexpr uint32_t MinPulseWidthMs = 100;
    static constexpr uint32_t MaxPulseWidthMs = 1500;
    static constexpr uint32_t MotionWindowMs = 2500;
    static constexpr float AlphaBaseline = 0.005f;
    static constexpr float AlphaLowPass = 0.24f;
};

class MotionEvent {
public:
    uint32_t timestampMs;
    uint16_t peakAmplitudeAdc;
    uint32_t pulseDurationMs;
};

class PyroelectricProcessor {
public:
    PyroelectricProcessor() noexcept
        : m_baseline(static_cast<float>(PirConfig::DefaultBaselineAdc))
        , m_iirFiltered(static_cast<float>(PirConfig::DefaultBaselineAdc))
        , m_state(PirState::Idle)
        , m_lastPeakTimeMs(0)
        , m_peakAmplitude(0)
    {}

    [[nodiscard]] std::optional<MotionEvent> processSample(uint16_t rawAdc, uint32_t currentTimeMs) noexcept {
        // 1. ФНЧ першого порядку для видалення 50 Гц шумів
        m_iirFiltered += PirConfig::AlphaLowPass * (static_cast<float>(rawAdc) - m_iirFiltered);

        // 2. Адаптивне коригування нульової лінії за відсутності сигналу
        const float absDiff = std::abs(m_iirFiltered - m_baseline);
        if (absDiff < static_cast<float>(PirConfig::ThresholdOffsetAdc) / 2.0f) {
            m_baseline += PirConfig::AlphaBaseline * (m_iirFiltered - m_baseline);
        }

        const float posThreshold = m_baseline + static_cast<float>(PirConfig::ThresholdOffsetAdc);
        const float negThreshold = m_baseline - static_cast<float>(PirConfig::ThresholdOffsetAdc);

        std::optional<MotionEvent> event = std::nullopt;

        // 3. Автомат станів виявлення дворівневого хвильового сигналу
        switch (m_state) {
            case PirState::Idle:
                if (m_iirFiltered > posThreshold) {
                    m_state = PirState::PositivePeakDetected;
                    m_lastPeakTimeMs = currentTimeMs;
                    m_peakAmplitude = static_cast<uint16_t>(m_iirFiltered - m_baseline);
                } else if (m_iirFiltered < negThreshold) {
                    m_state = PirState::NegativePeakDetected;
                    m_lastPeakTimeMs = currentTimeMs;
                    m_peakAmplitude = static_cast<uint16_t>(m_baseline - m_iirFiltered);
                }
                break;

            case PirState::PositivePeakDetected:
                if ((currentTimeMs - m_lastPeakTimeMs) > PirConfig::MotionWindowMs) {
                    m_state = PirState::Idle;
                } else if (m_iirFiltered < negThreshold) {
                    const uint32_t delta = currentTimeMs - m_lastPeakTimeMs;
                    if (delta >= PirConfig::MinPulseWidthMs && delta <= PirConfig::MaxPulseWidthMs) {
                        m_state = PirState::MotionConfirmed;
                        event = MotionEvent{currentTimeMs, m_peakAmplitude, delta};
                    }
                }
                break;

            case PirState::NegativePeakDetected:
                if ((currentTimeMs - m_lastPeakTimeMs) > PirConfig::MotionWindowMs) {
                    m_state = PirState::Idle;
                } else if (m_iirFiltered > posThreshold) {
                    const uint32_t delta = currentTimeMs - m_lastPeakTimeMs;
                    if (delta >= PirConfig::MinPulseWidthMs && delta <= PirConfig::MaxPulseWidthMs) {
                        m_state = PirState::MotionConfirmed;
                        event = MotionEvent{currentTimeMs, m_peakAmplitude, delta};
                    }
                }
                break;

            case PirState::MotionConfirmed:
                if ((currentTimeMs - m_lastPeakTimeMs) > PirConfig::MotionWindowMs) {
                    m_state = PirState::Idle;
                }
                break;
        }

        return event;
    }

    [[nodiscard]] float getBaseline() const noexcept { return m_baseline; }
    [[nodiscard]] float getFilteredSignal() const noexcept { return m_iirFiltered; }

private:
    float m_baseline;
    float m_iirFiltered;
    PirState m_state;
    uint32_t m_lastPeakTimeMs;
    uint16_t m_peakAmplitude;
};

} // namespace Sensors
