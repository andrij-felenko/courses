#include "HallSensorChopper.h"

HallSensorChopper::HallSensorChopper(std::size_t filterWindowSize)
    : filter(filterWindowSize), currentPhase(0), phase0Value(0.0f), lastCompensatedValue(0.0f) {
}

void HallSensorChopper::processAdcSample(float adcValue) {
    if (currentPhase == 0) {
        // Фаза 0: позитивний напрямок струму, сигнал = Vhall + Voffset
        phase0Value = adcValue;
        
        // Перемикаємо на фазу 1 для наступного вимірювання
        currentPhase = 1;
    } else {
        // Фаза 1: зворотній напрямок струму, сигнал = -Vhall + Voffset
        float phase1Value = adcValue;
        
        // Обчислюємо корисний сигнал (Vhall), усуваючи напругу зміщення (Voffset).
        // Vhall = (phase0Value - phase1Value) / 2
        float compensatedSignal = (phase0Value - phase1Value) / 2.0f;
        
        // Передаємо компенсований сигнал у цифровий фільтр
        lastCompensatedValue = filter.process(compensatedSignal);
        
        // Повертаємося до фази 0
        currentPhase = 0;
    }
}

float HallSensorChopper::getCompensatedValue() const {
    return lastCompensatedValue;
}

int HallSensorChopper::getPhase() const {
    return currentPhase;
}
