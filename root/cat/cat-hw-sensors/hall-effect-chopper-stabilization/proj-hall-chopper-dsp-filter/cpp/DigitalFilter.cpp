#include "DigitalFilter.h"

DigitalFilter::DigitalFilter(std::size_t windowSize)
    : windowSize(windowSize), currentIndex(0), sum(0.0f) {
    if (this->windowSize == 0) {
        this->windowSize = 1; // Запобігаємо діленню на нуль
    }
    buffer.resize(this->windowSize, 0.0f);
}

float DigitalFilter::process(float newValue) {
    // Віднімаємо старе значення з суми
    sum -= buffer[currentIndex];
    
    // Записуємо нове значення в буфер
    buffer[currentIndex] = newValue;
    
    // Додаємо нове значення до суми
    sum += newValue;
    
    // Переходимо до наступного індексу циклічного буфера
    currentIndex = (currentIndex + 1) % windowSize;
    
    // Повертаємо середнє значення
    return sum / static_cast<float>(windowSize);
}
