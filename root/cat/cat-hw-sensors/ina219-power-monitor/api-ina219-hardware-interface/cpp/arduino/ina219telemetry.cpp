// Зчитування телеметрії INA219 з обробкою прапорців CNVR та OVF для Arduino C++
#include <Arduino.h>

class Ina219Telemetry {
public:
    static constexpr uint16_t CNVR_MASK = (1U << 1);
    static constexpr uint16_t OVF_MASK  = (1U << 0);

    struct MeasurementResult {
        float busVoltageV;
        float currentMa;
        float powerMw;
        bool dataReady;
        bool overflow;
    };

    static MeasurementResult parseTelemetry(uint16_t rawBusReg, int16_t rawCurrentReg, 
                                            uint16_t rawPowerReg, float currentLsbMa) 
    {
        MeasurementResult result;
        result.dataReady = (rawBusReg & CNVR_MASK) != 0;
        result.overflow  = (rawBusReg & OVF_MASK) != 0;

        if (result.overflow) {
            result.currentMa = 0.0f;
            result.powerMw   = 0.0f;
            return result;
        }

        uint16_t rawBus = rawBusReg >> 3;
        result.busVoltageV = rawBus * 0.004f;
        result.currentMa   = rawCurrentReg * currentLsbMa;
        result.powerMw     = rawPowerReg * 20.0f * currentLsbMa;

        return result;
    }
};
