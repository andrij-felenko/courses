#include <Arduino.h>

class PDBTelemetry {
private:
    float vDividerRatio;
    float shuntResistorOhm;
    float ampGain;
    float adcVref;
    uint32_t adcResolution;
    float consumedmAh;

public:
    PDBTelemetry(float dividerRatio, float shuntOhm, float gain, float vref = 3.3f, uint32_t res = 4096)
        : vDividerRatio(dividerRatio), shuntResistorOhm(shuntOhm), 
          ampGain(gain), adcVref(vref), adcResolution(res), consumedmAh(0.0f) {}

    struct TelemetryData {
        float voltageV;
        float currentA;
        float consumedmAh;
    };

    TelemetryData update(uint16_t rawAdcVoltage, uint16_t rawAdcCurrent, float dtSeconds) {
        float vAdc = (static_cast<float>(rawAdcVoltage) / adcResolution) * adcVref;
        float iAdc = (static_cast<float>(rawAdcCurrent) / adcResolution) * adcVref;

        float voltageV = vAdc * vDividerRatio;
        float vShunt = iAdc / ampGain;
        float currentA = vShunt / shuntResistorOhm;

        consumedmAh += (currentA * 1000.0f) * (dtSeconds / 3600.0f);

        return { voltageV, currentA, consumedmAh };
    }
};
