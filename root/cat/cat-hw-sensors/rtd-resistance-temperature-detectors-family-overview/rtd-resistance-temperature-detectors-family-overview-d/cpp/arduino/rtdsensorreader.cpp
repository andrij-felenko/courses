#include <Arduino.h>

class RtdSensorReader {
private:
    const float _rRef;
    const float _r0;
    const float _alpha;

public:
    struct Measurement {
        float temperatureC;
        float resistance;
        bool isFault;
        const char* faultMessage;
    };

    RtdSensorReader(float rRef = 400.0f, float r0 = 100.0f)
        : _rRef(rRef), _r0(r0), _alpha(0.003851f) {}

    Measurement readFromAdcCode(uint16_t rawCode, uint8_t bitResolution = 15) {
        Measurement result;
        uint32_t maxCode = (1UL << bitResolution) - 1;

        if (rawCode >= maxCode) {
            result.isFault = true;
            result.faultMessage = "Обрив лінії (Open Circuit)";
            result.temperatureC = NAN;
            result.resistance = NAN;
            return result;
        }

        if (rawCode == 0) {
            result.isFault = true;
            result.faultMessage = "Коротке замикання (Short Circuit)";
            result.temperatureC = NAN;
            result.resistance = NAN;
            return result;
        }

        result.isFault = false;
        result.faultMessage = "OK";

        // Обчислення опору за раціометричною формулою
        result.resistance = ((float)rawCode / (float)(1UL << bitResolution)) * _rRef;

        // Розрахунок температури
        result.temperatureC = (result.resistance - _r0) / (_r0 * _alpha);

        return result;
    }
};
