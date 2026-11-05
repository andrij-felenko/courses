#ifndef DIGITAL_FILTER_H
#define DIGITAL_FILTER_H

#include <vector>
#include <cstddef>

// Цифровий фільтр на основі ковзного середнього (Moving Average)
class DigitalFilter {
public:
    explicit DigitalFilter(std::size_t windowSize);
    float process(float newValue);

private:
    std::vector<float> buffer;
    std::size_t windowSize;
    std::size_t currentIndex;
    float sum;
};

#endif // DIGITAL_FILTER_H
