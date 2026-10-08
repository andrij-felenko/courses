#include <cstdint>
#include <cmath>
#include <array>

class OV2640GammaLUT {
public:
    static constexpr size_t kNodes = 15;

    struct LUTData {
        std::array<uint8_t, kNodes> x_nodes;
        std::array<uint8_t, kNodes> y_nodes;
        std::array<uint16_t, kNodes - 1> slopes;
    };

    static LUTData generate(float gamma) {
        LUTData lut{};
        float inv_gamma = 1.0f / gamma;
        const std::array<uint8_t, kNodes> x_defaults = {
            0, 4, 8, 16, 24, 32, 48, 64, 80, 96, 128, 160, 192, 224, 255
        };

        for (size_t i = 0; i < kNodes; ++i) {
            lut.x_nodes[i] = x_defaults[i];
            float norm_x = static_cast<float>(x_defaults[i]) / 255.0f;
            float norm_y = std::pow(norm_x, inv_gamma);
            lut.y_nodes[i] = static_cast<uint8_t>(std::round(norm_y * 255.0f));
        }

        for (size_t i = 0; i < kNodes - 1; ++i) {
            uint8_t dx = lut.x_nodes[i + 1] - lut.x_nodes[i];
            int16_t dy = static_cast<int16_t>(lut.y_nodes[i + 1]) - static_cast<int16_t>(lut.y_nodes[i]);
            lut.slopes[i] = static_cast<uint16_t>((dy * 256) / dx);
        }
        return lut;
    }

    static uint8_t interpolate(uint8_t x_in, const LUTData& lut) {
        if (x_in <= lut.x_nodes.front()) return lut.y_nodes.front();
        if (x_in >= lut.x_nodes.back()) return lut.y_nodes.back();

        size_t seg = 0;
        while (seg < kNodes - 2 && x_in >= lut.x_nodes[seg + 1]) {
            seg++;
        }

        uint8_t dx = x_in - lut.x_nodes[seg];
        uint16_t dy_scaled = (dx * lut.slopes[seg]) >> 8;
        return lut.y_nodes[seg] + static_cast<uint8_t>(dy_scaled);
    }
};
