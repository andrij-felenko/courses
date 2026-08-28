#include <cstdint>
#include <cmath>
#include <array>
#include <algorithm>
#include <optional>

namespace sensors {

enum class SensorGain : uint8_t {
    Gain1x  = 0x00,
    Gain4x  = 0x01,
    Gain16x = 0x02,
    Gain60x = 0x03
};

struct RawColorSample {
    uint16_t red{0};
    uint16_t green{0};
    uint16_t blue{0};
    uint16_t clear{0};
};

struct ColorimetricResult {
    float x{0.3127f};
    float y{0.3290f};
    float illuminance_lux{0.0f};
    float cct_kelvin{6504.0f};
    uint8_t srgb_r{0};
    uint8_t srgb_g{0};
    uint8_t srgb_b{0};
    bool is_saturated{false};
};

class ColorSensorEngine {
public:
    static constexpr float D65_WHITE_X = 0.3127f;
    static constexpr float D65_WHITE_Y = 0.3290f;

    [[nodiscard]] static constexpr float computeCctMcCamy(float x, float y) noexcept {
        const float denom = 0.1858f - y;
        if (std::abs(denom) < 1e-5f) return 0.0f;
        const float n = (x - 0.3320f) / denom;
        const float n2 = n * n;
        const float n3 = n2 * n;
        return 449.0f * n3 + 3525.0f * n2 + 6823.3f * n + 5520.33f;
    }

    [[nodiscard]] static ColorimetricResult process(const RawColorSample& raw, 
                                                    float integration_ms, 
                                                    float gain) noexcept 
    {
        ColorimetricResult result{};
        result.is_saturated = (raw.clear >= 65530 || raw.red >= 65530 || 
                               raw.green >= 65530 || raw.blue >= 65530);

        const float norm = (integration_ms * gain > 0.0f) ? (1.0f / (integration_ms * gain)) : 1.0f;
        const float rn = static_cast<float>(raw.red) * norm;
        const float gn = static_cast<float>(raw.green) * norm;
        const float bn = static_cast<float>(raw.blue) * norm;

        // Матриця калібрування CCM 3x3
        constexpr std::array<std::array<float, 3>, 3> CCM = {{
            {  0.0829f,  0.1983f, -0.0381f },
            {  0.0321f,  0.2452f, -0.0210f },
            { -0.0512f, -0.0821f,  0.3891f }
        }};

        const float X = std::max(0.0f, CCM[0][0] * rn + CCM[0][1] * gn + CCM[0][2] * bn);
        const float Y = std::max(0.0f, CCM[1][0] * rn + CCM[1][1] * gn + CCM[1][2] * bn);
        const float Z = std::max(0.0f, CCM[2][0] * rn + CCM[2][1] * gn + CCM[2][2] * bn);

        const float sum = X + Y + Z;
        if (sum > 1e-4f) {
            result.x = X / sum;
            result.y = Y / sum;
        } else {
            result.x = D65_WHITE_X;
            result.y = D65_WHITE_Y;
        }

        result.illuminance_lux = 683.0f * Y;
        result.cct_kelvin = computeCctMcCamy(result.x, result.y);

        // Трансформація у простір sRGB (D65)
        float r_lin =  3.2404542f * X - 1.5371385f * Y - 0.4985314f * Z;
        float g_lin = -0.9692660f * X + 1.8760108f * Y + 0.0415560f * Z;
        float b_lin =  0.0556434f * X - 0.2040259f * Y + 1.0572252f * Z;

        const float max_channel = std::max({r_lin, g_lin, b_lin});
        if (max_channel > 1e-4f) {
            r_lin /= max_channel;
            g_lin /= max_channel;
            b_lin /= max_channel;
        }

        result.srgb_r = encodeSrgbGamma(r_lin);
        result.srgb_g = encodeSrgbGamma(g_lin);
        result.srgb_b = encodeSrgbGamma(b_lin);

        return result;
    }

private:
    [[nodiscard]] static uint8_t encodeSrgbGamma(float linear) noexcept {
        if (linear <= 0.0f) return 0;
        if (linear >= 1.0f) return 255;
        const float encoded = (linear <= 0.0031308f)
                            ? (12.92f * linear)
                            : (1.055f * std::pow(linear, 1.0f / 2.4f) - 0.055f);
        return static_cast<uint8_t>(std::clamp(encoded * 255.0f + 0.5f, 0.0f, 255.0f));
    }
};

} // namespace sensors
