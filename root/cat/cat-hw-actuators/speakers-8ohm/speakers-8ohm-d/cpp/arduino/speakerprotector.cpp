#include <Arduino.h>
#include <math.h>

class SpeakerProtector {
private:
    float b0, b1, b2, a1, a2;
    float x1 = 0.0f, x2 = 0.0f, y1 = 0.0f, y2 = 0.0f;
    int16_t maxAmplitude;

public:
    SpeakerProtector(float cutoffHz, float sampleRate, int16_t limit) {
        maxAmplitude = limit;
        float w0 = 2.0f * PI * cutoffHz / sampleRate;
        float cosW0 = cos(w0);
        float alpha = sin(w0) / (2.0f * 0.7071f);

        float a0 = 1.0f + alpha;
        b0 = ((1.0f + cosW0) / 2.0f) / a0;
        b1 = (-(1.0f + cosW0)) / a0;
        b2 = ((1.0f + cosW0) / 2.0f) / a0;
        a1 = (-2.0f * cosW0) / a0;
        a2 = (1.0f - alpha) / a0;
    }

    int16_t process(int16_t inputSample) {
        float x = static_cast<float>(inputSample);
        float y = b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2;

        x2 = x1;
        x1 = x;
        y2 = y1;
        y1 = y;

        if (y > maxAmplitude) y = static_cast<float>(maxAmplitude);
        if (y < -maxAmplitude) y = -static_cast<float>(maxAmplitude);

        return static_cast<int16_t>(y);
    }
};
