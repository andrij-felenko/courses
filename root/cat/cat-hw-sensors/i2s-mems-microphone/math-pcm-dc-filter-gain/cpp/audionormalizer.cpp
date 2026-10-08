#include <cstdint>
#include <cstddef>
#include <algorithm>

class AudioNormalizer {
public:
    static void applyFixedGainQ15(int16_t* buffer, std::size_t count, int32_t gainQ15) {
        if (!buffer || count == 0) return;

        for (std::size_t i = 0; i < count; ++i) {
            const int32_t scaled = (static_cast<int32_t>(buffer[i]) * gainQ15) >> 15;
            buffer[i] = static_cast<int16_t>(std::clamp(scaled, -32768, 32767));
        }
    }
};
