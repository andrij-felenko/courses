#include <cstdint>
#include <cmath>
#include <array>
#include <optional>
#include <span>
#include <algorithm>

namespace sensors {

struct RawSpectralChannels {
    uint16_t f1_415nm{0};
    uint16_t f2_445nm{0};
    uint16_t f3_480nm{0};
    uint16_t f4_515nm{0};
    uint16_t f5_555nm{0};
    uint16_t f6_590nm{0};
    uint16_t f7_630nm{0};
    uint16_t f8_680nm{0};
    uint16_t clear{0};
    uint16_t nir{0};
    uint8_t  flicker_freq_hz{0};
};

struct SpectralAnalysisResult {
    float x{0.3127f};
    float y{0.3290f};
    float cct_kelvin{6504.0f};
    float lux{0.0f};
    float cri_ra{100.0f};
    std::array<float, 8> spd_density{};
};

class AS7341SpectralAnalyzer {
public:
    static constexpr uint8_t I2C_ADDRESS = 0x39;

    [[nodiscard]] static constexpr float calculateCctMcCamy(float x, float y) noexcept {
        if (std::abs(0.1858f - y) < 1e-5f) return 0.0f;
        const float n = (x - 0.3320f) / (0.1858f - y);
        const float n2 = n * n;
        const float n3 = n2 * n;
        return 449.0f * n3 + 3525.0f * n2 + 6823.3f * n + 5520.33f;
    }

    [[nodiscard]] static SpectralAnalysisResult process(const RawSpectralChannels& raw,
                                                         float integration_time_ms,
                                                         float analog_gain) noexcept {
        SpectralAnalysisResult result{};
        const float norm = (integration_time_ms * analog_gain > 0.0f)
                         ? (1.0f / (integration_time_ms * analog_gain))
                         : 1.0f;

        constexpr std::array<float, 8> CALIBRATION_RESPONSIVITY = {
            0.120f, 0.100f, 0.090f, 0.085f, 0.080f, 0.075f, 0.070f, 0.082f
        };

        const std::array<uint16_t, 8> raw_bands = {
            raw.f1_415nm, raw.f2_445nm, raw.f3_480nm, raw.f4_515nm,
            raw.f5_555nm, raw.f6_590nm, raw.f7_630nm, raw.f8_680nm
        };

        for (size_t i = 0; i < 8; ++i) {
            result.spd_density[i] = static_cast<float>(raw_bands[i]) * norm * CALIBRATION_RESPONSIVITY[i];
        }

        // Згортка 8 смуг у тристимулус CIE 1931 XYZ
        const float X = 0.05f * result.spd_density[0] + 0.35f * result.spd_density[1] +
                        0.15f * result.spd_density[2] + 0.02f * result.spd_density[3] +
                        0.30f * result.spd_density[4] + 0.85f * result.spd_density[5] +
                        1.05f * result.spd_density[6] + 0.35f * result.spd_density[7];

        const float Y = 0.01f * result.spd_density[0] + 0.05f * result.spd_density[1] +
                        0.14f * result.spd_density[2] + 0.55f * result.spd_density[3] +
                        0.98f * result.spd_density[4] + 0.75f * result.spd_density[5] +
                        0.25f * result.spd_density[6] + 0.02f * result.spd_density[7];

        const float Z = 0.95f * result.spd_density[0] + 1.85f * result.spd_density[1] +
                        0.85f * result.spd_density[2] + 0.05f * result.spd_density[3];

        const float sum = X + Y + Z;
        if (sum > 1e-4f) {
            result.x = X / sum;
            result.y = Y / sum;
        }

        result.lux = 683.0f * Y;
        result.cct_kelvin = calculateCctMcCamy(result.x, result.y);
        result.cri_ra = estimateCri(result.spd_density, result.cct_kelvin);

        return result;
    }

private:
    [[nodiscard]] static float estimateCri(std::span<const float, 8> spd, float cct) noexcept {
        const float blue_sum = spd[0] + spd[1] + spd[2];
        const float green_sum = spd[3] + spd[4];
        const float red_sum = spd[5] + spd[6] + spd[7];
        const float total = blue_sum + green_sum + red_sum;

        if (total < 1e-4f) return 0.0f;

        const float r_ratio = red_sum / total;
        const float g_ratio = green_sum / total;

        float penalty = 0.0f;
        if (cct < 3500.0f && r_ratio < 0.35f) {
            penalty += (0.35f - r_ratio) * 150.0f;
        }
        if (g_ratio > 0.55f) {
            penalty += (g_ratio - 0.55f) * 120.0f;
        }

        return std::clamp(100.0f - penalty, 0.0f, 100.0f);
    }
};

} // namespace sensors
