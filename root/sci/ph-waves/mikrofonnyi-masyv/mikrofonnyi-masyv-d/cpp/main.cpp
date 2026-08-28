#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <algorithm>

class DelayAndSumBeamformer {
public:
    DelayAndSumBeamformer(std::size_t numMics, float micSpacingMeters, float soundSpeed = 343.0f)
        : m_numMics(numMics), m_spacing(micSpacingMeters), m_c(soundSpeed) {}

    // Фазування променя для цільового кута в градусах
    [[nodiscard]] std::vector<float> processFrame(const std::vector<std::vector<float>>& multiChannelIn,
                                                  float samplingRate, float steerAngleDeg) const {
        const std::size_t frameLen = multiChannelIn[0].size();
        std::vector<float> output(frameLen, 0.0f);
        const float rad = steerAngleDeg * std::numbers::pi_v<float> / 180.0f;

        for (std::size_t m = 0; m < m_numMics; ++m) {
            const float delaySec = static_cast<float>(m) * m_spacing * std::sin(rad) / m_c;
            const float shiftSamples = delaySec * samplingRate;
            const int sInt = static_cast<int>(std::floor(shiftSamples));
            const float sFrac = shiftSamples - static_cast<float>(sInt);

            for (std::size_t i = 0; i < frameLen; ++i) {
                const int idx = static_cast<int>(i) + sInt;
                float sample = 0.0f;
                if (idx >= 0 && static_cast<std::size_t>(idx + 1) < frameLen) {
                    sample = (1.0f - sFrac) * multiChannelIn[m][idx] + sFrac * multiChannelIn[m][idx + 1];
                } else if (idx >= 0 && static_cast<std::size_t>(idx) < frameLen) {
                    sample = multiChannelIn[m][idx];
                }
                output[i] += sample / static_cast<float>(m_numMics);
            }
        }
        return output;
    }

private:
    std::size_t m_numMics;
    float m_spacing;
    float m_c;
};
