#include <cstdint>
#include <limits>

class SS41FIntervalMeter {
public:
    static uint32_t calculateDelta(uint32_t now_us, uint32_t prev_us) {
        if (now_us >= prev_us) {
            return now_us - prev_us;
        } else {
            // Опрацювання переповнення 32-бітного таймера
            return (std::numeric_limits<uint32_t>::max() - prev_us) + now_us + 1;
        }
    }

    static float calculateRPM(uint32_t interval_us, uint8_t magnet_pairs) {
        if (interval_us == 0 || magnet_pairs == 0) return 0.0f;
        // 1 хвилина = 60 000 000 мкс
        float period_us = static_cast<float>(interval_us * 2 * magnet_pairs);
        return (60000000.0f / period_us);
    }
};
