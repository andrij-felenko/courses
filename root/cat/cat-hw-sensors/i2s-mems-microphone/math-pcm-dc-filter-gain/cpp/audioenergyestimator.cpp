#include <cstdint>
#include <cstddef>
#include <cmath>

class AudioEnergyEstimator {
public:
    static uint16_t calculateRMS(const int16_t* buffer, std::size_t count) {
        if (!buffer || count == 0) return 0;

        uint64_t sumSquares = 0;
        for (std::size_t i = 0; i < count; ++i) {
            const int32_t sample = buffer[i];
            sumSquares += static_cast<uint64_t>(sample * sample);
        }

        const uint64_t meanSquare = sumSquares / count;
        return static_cast<uint16_t>(std::sqrt(meanSquare));
    }
};
