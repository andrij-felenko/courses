#include <Arduino.h>

class SharpTriangulationSensor {
private:
    uint8_t _adcPin;
    float _alpha;
    float _filteredVal;

    static constexpr float COEFF_KA = 16.5f;       // Градуювальна константа
    static constexpr float V_ZERO = 0.10f;         // Напруга зсуву (В)
    static constexpr float BLIND_THRESHOLD = 2.7f; // Напруга входу у сліпу зону (В)

public:
    enum class Status {
        Ok,
        BlindZoneWarning,
        OutOfRange
    };

    struct RangingResult {
        float distanceCm;
        float voltage;
        Status status;
    };

    SharpTriangulationSensor(uint8_t pin, float filterAlpha = 0.2f)
        : _adcPin(pin), _alpha(filterAlpha), _filteredVal(0.0f) {}

    void begin() {
        pinMode(_adcPin, INPUT);
        _filteredVal = analogRead(_adcPin);
    }

    RangingResult readDistance() {
        int rawAdc = analogRead(_adcPin);
        // EMA фільтрація відсміченого ADC сигналу
        _filteredVal = (_alpha * rawAdc) + ((1.0f - _alpha) * _filteredVal);
        
        float voltage = (_filteredVal / 1023.0f) * 5.0f; // Для 10-біт ADC та 5V опорної
        RangingResult res;
        res.voltage = voltage;

        if (voltage >= BLIND_THRESHOLD) {
            res.distanceCm = 10.0f;
            res.status = Status::BlindZoneWarning;
            return res;
        }

        float vDiff = voltage - V_ZERO;
        if (vDiff < 0.05f) {
            res.distanceCm = 80.0f;
            res.status = Status::OutOfRange;
            return res;
        }

        float calculatedDist = COEFF_KA / vDiff;

        if (calculatedDist < 10.0f) {
            res.distanceCm = 10.0f;
            res.status = Status::BlindZoneWarning;
        } else if (calculatedDist > 80.0f) {
            res.distanceCm = 80.0f;
            res.status = Status::OutOfRange;
        } else {
            res.distanceCm = calculatedDist;
            res.status = Status::Ok;
        }

        return res;
    }
};
