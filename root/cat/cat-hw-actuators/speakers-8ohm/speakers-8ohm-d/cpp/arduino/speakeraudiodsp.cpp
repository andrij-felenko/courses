#include <Arduino.h>
#include <math.h>

class SpeakerAudioDSP {
private:
    float b0, b1, b2, a1, a2;
    float x1, x2, y1, y2;
    float maxAmplitude;

public:
    SpeakerAudioDSP() : x1(0), x2(0), y1(0), y2(0), maxAmplitude(1.0f) {}

    // Налаштування ФВЧ з частотою зрізу fc (Гц) та частотою дискретизації fs (Гц)
    void setupHighPassFilter(float sampleRate, float cutoffFreq) {
        float w0 = 2.0f * PI * cutoffFreq / sampleRate;
        float cosW0 = cos(w0);
        float alpha = sin(w0) / (2.0f * 0.7071f);

        float a0 = 1.0f + alpha;
        b0 = ((1.0f + cosW0) / 2.0f) / a0;
        b1 = (-(1.0f + cosW0)) / a0;
        b2 = ((1.0f + cosW0) / 2.0f) / a0;
        a1 = (-2.0f * cosW0) / a0;
        a2 = (1.0f - alpha) / a0;
    }

    void setMaxPeakAmplitude(float peakLimit) {
        maxAmplitude = peakLimit;
    }

    // Обробка одного аудіовідліку з фільтрацією та обмеженням піків
    float processSample(float sample) {
        float filtered = b0 * sample + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2;
        x2 = x1;
        x1 = sample;
        y2 = y1;
        y1 = filtered;

        if (filtered > maxAmplitude) {
            return maxAmplitude;
        } else if (filtered < -maxAmplitude) {
            return -maxAmplitude;
        }
        return filtered;
    }
};
