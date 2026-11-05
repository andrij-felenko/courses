#ifndef HALL_SENSOR_CHOPPER_H
#define HALL_SENSOR_CHOPPER_H

#include "DigitalFilter.h"
#include <cstddef>

// Клас, що інкапсулює логіку чопперної стабілізації давача Холла
class HallSensorChopper {
public:
    explicit HallSensorChopper(std::size_t filterWindowSize);

    // Викликається для передачі сирих даних з АЦП.
    // В реальній системі це може викликатись в перериванні таймера або головному циклі.
    void processAdcSample(float adcValue);

    // Отримати відфільтроване та компенсоване значення магнітного поля
    float getCompensatedValue() const;

    // Отримати поточну фазу для налаштування апаратних ключів (0 або 1)
    int getPhase() const;

private:
    DigitalFilter filter;
    int currentPhase;
    float phase0Value; // Значення АЦП для фази 0 (Vhall + Voffset)
    float lastCompensatedValue;
};

#endif // HALL_SENSOR_CHOPPER_H
