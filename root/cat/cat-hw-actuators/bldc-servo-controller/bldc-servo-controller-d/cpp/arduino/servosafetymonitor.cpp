// C++ реалізація моніторингу безпеки FOC-сервоконтролера
#include <Arduino.h>

class ServoSafetyMonitor {
public:
    struct Config {
        float maxCurrentA;
        float maxTempC;
        bool isCalibrated;
    };

    enum class Status {
        Ok,
        EncoderError,
        Overcurrent,
        Overtemperature
    };

    static Status checkStatus(float currentA, float tempC, const Config& cfg) {
        if (!cfg.isCalibrated) {
            return Status::EncoderError;
        }
        if (currentA > cfg.maxCurrentA) {
            return Status::Overcurrent;
        }
        if (tempC > cfg.maxTempC) {
            return Status::Overtemperature;
        }
        return Status::Ok;
    }
};
