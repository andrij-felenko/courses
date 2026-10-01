#include "ACS712.h"

ACS712Sensor::ACS712Sensor(uint8_t pin, ACS712Model model, float vcc, uint16_t adcResolution)
    : _pin(pin), _vcc(vcc), _adcResolution(adcResolution), _zeroVoltage(vcc / 2.0f), _relayState(false) {
    switch (model) {
        case ACS712Model::ACS712_05B:
            _sensitivity = 0.185f;
            break;
        case ACS712Model::ACS712_20A:
            _sensitivity = 0.100f;
            break;
        case ACS712Model::ACS712_30A:
            _sensitivity = 0.066f;
            break;
    }
}

void ACS712Sensor::begin() {
    pinMode(_pin, INPUT);
}

void ACS712Sensor::calibrateZero(size_t samples) {
    uint32_t sumAdc = 0;
    for (size_t i = 0; i < samples; ++i) {
        sumAdc += analogRead(_pin);
        delay(2);
    }
    float avgAdc = static_cast<float>(sumAdc) / static_cast<float>(samples);
    _zeroVoltage = (avgAdc / static_cast<float>(_adcResolution - 1)) * _vcc;
}

float ACS712Sensor::readCurrentDC() {
    int adcVal = analogRead(_pin);
    float voltage = (static_cast<float>(adcVal) / static_cast<float>(_adcResolution - 1)) * _vcc;
    return (voltage - _zeroVoltage) / _sensitivity;
}

float ACS712Sensor::readCurrentRMS(float frequencyHz) {
    uint32_t periodUs = static_cast<uint32_t>(1000000.0f / frequencyHz);
    uint32_t startTime = micros();
    
    double sumSquares = 0.0;
    size_t sampleCount = 0;
    
    while (micros() - startTime < periodUs) {
        int adcVal = analogRead(_pin);
        float voltage = (static_cast<float>(adcVal) / static_cast<float>(_adcResolution - 1)) * _vcc;
        float current = (voltage - _zeroVoltage) / _sensitivity;
        
        sumSquares += current * current;
        sampleCount++;
        delayMicroseconds(200);
    }
    
    if (sampleCount == 0) return 0.0f;
    return sqrt(static_cast<float>(sumSquares / sampleCount));
}

bool ACS712Sensor::checkOvercurrent(float thresholdA, float hysteresisA, uint8_t relayPin) {
    float currentRMS = readCurrentRMS();
    
    if (!_relayState && currentRMS >= thresholdA) {
        _relayState = true;
        digitalWrite(relayPin, HIGH); // Відключити навантаження при струмі перевантаження
    } else if (_relayState && currentRMS < (thresholdA - hysteresisA)) {
        _relayState = false;
        digitalWrite(relayPin, LOW); // Відновити живлення при падінні нижче порогу з гістерезисом
    }
    
    return _relayState;
}
