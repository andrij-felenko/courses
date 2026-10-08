#include <Arduino.h>

struct LUTPoint {
    float rOhm;
    float tempC;
};

class RTDLUTLinearizer {
private:
    static constexpr LUTPoint lut[] = {
        {18.520f, -200.0f},
        {38.521f, -150.0f},
        {60.256f, -100.0f},
        {80.306f,  -50.0f},
        {100.000f,   0.0f},
        {119.397f,  50.0f},
        {138.506f, 100.0f}
    };
    static constexpr uint8_t lutSize = sizeof(lut) / sizeof(lut[0]);

public:
    static float interpolate(float rMeas) {
        if (rMeas <= lut[0].rOhm) return lut[0].tempC;
        if (rMeas >= lut[lutSize - 1].rOhm) return lut[lutSize - 1].tempC;

        uint8_t low = 0;
        uint8_t high = lutSize - 1;

        while (high - low > 1) {
            uint8_t mid = (low + high) / 2;
            if (lut[mid].rOhm > rMeas) {
                high = mid;
            } else {
                low = mid;
            }
        }

        float r0 = lut[low].rOhm;
        float r1 = lut[high].rOhm;
        float t0 = lut[low].tempC;
        float t1 = lut[high].tempC;

        return t0 + (rMeas - r0) * (t1 - t0) / (r1 - r0);
    }
};
