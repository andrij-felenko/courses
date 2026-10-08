#include <cmath>
#include <cstdint>

class SynchronousDemodulator {
public:
    void processSample(float adcSample, float phaseAngleRad) noexcept {
        m_inphaseAccum += adcSample * std::cos(phaseAngleRad);
        m_quadratureAccum += adcSample * std::sin(phaseAngleRad);
        ++m_sampleCount;
    }

    [[nodiscard]] float getSignedDisplacement(float scaleFactor) const noexcept {
        if (m_sampleCount == 0) return 0.0f;
        const float meanInphase = m_inphaseAccum / static_cast<float>(m_sampleCount);
        return meanInphase * scaleFactor;
    }

    void reset() noexcept {
        m_inphaseAccum = 0.0f;
        m_quadratureAccum = 0.0f;
        m_sampleCount = 0;
    }

private:
    float m_inphaseAccum{0.0f};
    float m_quadratureAccum{0.0f};
    uint32_t m_sampleCount{0};
};
