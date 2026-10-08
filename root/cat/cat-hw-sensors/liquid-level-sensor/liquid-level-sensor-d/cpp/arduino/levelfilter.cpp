#include <Arduino.h>
#include <algorithm>

template <size_t N>
class LevelFilter {
private:
    float samples[N];
    size_t index = 0;
    float emaValue = 0.0f;
    float alpha = 0.2f;
    bool initialized = false;

public:
    LevelFilter(float filterAlpha) : alpha(filterAlpha) {
        std::fill(samples, samples + N, 0.0f);
    }

    float update(float rawValue) {
        samples[index] = rawValue;
        index = (index + 1) % N;

        float sortedSamples[N];
        std::copy(samples, samples + N, sortedSamples);
        std::sort(sortedSamples, sortedSamples + N);

        float medianValue = sortedSamples[N / 2];

        if (!initialized) {
            emaValue = medianValue;
            initialized = true;
        } else {
            emaValue = alpha * medianValue + (1.0f - alpha) * emaValue;
        }
        return emaValue;
    }
};

// Приклад створення об'єкта фільтра з вікном на 5 елементів
LevelFilter<5> tankFilter(0.15f);
