// Клас двоточкового калібрування та EMA-фільтрації для сервоприводу на C++ (Arduino)
#include <Arduino.h>

class ServoPotentiometerFilter {
private:
    float scale;
    float offset;
    float alpha;
    float filteredAngle;
    bool initialized;

public:
    ServoPotentiometerFilter(float smoothingFactor = 0.25f)
        : scale(1.0f), offset(0.0f), alpha(smoothingFactor), filteredAngle(0.0f), initialized(false) {}

    // Налаштування двоточкового калібрування за опорними вимірюваннями
    void calibrate(float rawAdc1, float angle1, float rawAdc2, float angle2) {
        if (rawAdc2 != rawAdc1) {
            scale = (angle2 - angle1) / (rawAdc2 - rawAdc1);
            offset = angle1 - scale * rawAdc1;
        }
    }

    // Зчитування та обробка нового значення від АЦП
    float process(float rawAdc) {
        float calibratedAngle = scale * rawAdc + offset;
        if (!initialized) {
            filteredAngle = calibratedAngle;
            initialized = true;
        } else {
            filteredAngle = alpha * calibratedAngle + (1.0f - alpha) * filteredAngle;
        }
        return filteredAngle;
    }

    // Скидання стану фільтра при зміні режиму
    void reset() {
        initialized = false;
    }
};
