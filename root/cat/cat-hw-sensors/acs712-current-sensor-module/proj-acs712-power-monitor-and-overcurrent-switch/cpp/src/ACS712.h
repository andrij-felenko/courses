#ifndef ACS712_H
#define ACS712_H

#include <Arduino.h>

enum class ACS712Model {
    ACS712_05B, // 185 mV/A
    ACS712_20A, // 100 mV/A
    ACS712_30A  // 66 mV/A
};

class ACS712Sensor {
public:
    ACS712Sensor(uint8_t pin, ACS712Model model, float vcc = 5.0f, uint16_t adcResolution = 1024);

    void begin();
    void calibrateZero(size_t samples = 100);

    float readCurrentDC();
    float readCurrentRMS(float frequencyHz = 50.0f);
    bool checkOvercurrent(float thresholdA, float hysteresisA, uint8_t relayPin);

private:
    uint8_t _pin;
    float _sensitivity; // V/A
    float _vcc;
    uint16_t _adcResolution;
    float _zeroVoltage;
    bool _relayState;
};

#endif // ACS712_H
