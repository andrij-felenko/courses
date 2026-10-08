#include <cstdint>
#include <algorithm>

class OV2640ColorMatrix {
public:
    struct YUVPixel {
        uint8_t y;
        uint8_t u;
        uint8_t v;
    };

    static YUVPixel convertRGBToYUV(uint8_t r, uint8_t g, uint8_t b) {
        int32_t y_raw = (77 * r + 150 * g + 29 * b) >> 8;
        int32_t u_raw = ((-43 * r - 85 * g + 128 * b) >> 8) + 128;
        int32_t v_raw = ((128 * r - 107 * g - 21 * b) >> 8) + 128;

        return YUVPixel{
            static_cast<uint8_t>(std::clamp(y_raw, 0, 255)),
            static_cast<uint8_t>(std::clamp(u_raw, 0, 255)),
            static_cast<uint8_t>(std::clamp(v_raw, 0, 255))
        };
    }
};
