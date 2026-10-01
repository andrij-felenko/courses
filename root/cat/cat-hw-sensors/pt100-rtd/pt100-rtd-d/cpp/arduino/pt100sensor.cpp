#include <Arduino.h>
#include <math.h>

class PT100Sensor {
public:
    enum Status {
        OK = 0,
        ERR_OPEN_CIRCUIT,
        ERR_SHORT_CIRCUIT
    };

    Status calculateTemperature(float rMeasured, float &tempOut) const {
        if (rMeasured > 400.0f) {
            return ERR_OPEN_CIRCUIT;
        }
        if (rMeasured < 18.0f) {
            return ERR_SHORT_CIRCUIT;
        }

        float polyC = 1.0f - (rMeasured / kR0);
        float discriminant = (kA * kA) - (4.0f * kB * polyC);
        if (discriminant < 0.0f) {
            return ERR_SHORT_CIRCUIT;
        }
        tempOut = (-kA + sqrtf(discriminant)) / (2.0f * kB);
        return OK;
    }

private:
    static constexpr float kR0 = 100.0f;
    static constexpr float kA = 3.9083e-3f;
    static constexpr float kB = -5.775e-7f;
};
