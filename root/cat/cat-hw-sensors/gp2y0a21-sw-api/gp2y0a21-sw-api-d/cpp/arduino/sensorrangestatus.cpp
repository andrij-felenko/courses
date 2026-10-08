#include <Arduino.h>

enum class SensorRangeStatus : uint8_t {
    Ok = 0,
    BlindZone,
    TooFar,
    HardwareFault
};

class DistanceDiagnostics {
private:
    uint16_t _uHighMv;
    uint16_t _uLowMv;
    uint16_t _uMinFarMv;
    bool _inBlindZone;

public:
    DistanceDiagnostics(uint16_t uHighMv = 2850, uint16_t uLowMv = 2650, uint16_t uMinFarMv = 400)
        : _uHighMv(uHighMv), _uLowMv(uLowMv), _uMinFarMv(uMinFarMv), _inBlindZone(false) {}

    SensorRangeStatus process(uint16_t voltageMv) {
        if (voltageMv < 50 || voltageMv > 3250) {
            return SensorRangeStatus::HardwareFault;
        }

        if (!_inBlindZone) {
            if (voltageMv >= _uHighMv) {
                _inBlindZone = true;
            }
        } else {
            if (voltageMv < _uLowMv) {
                _inBlindZone = false;
            }
        }

        if (_inBlindZone) {
            return SensorRangeStatus::BlindZone;
        }

        if (voltageMv < _uMinFarMv) {
            return SensorRangeStatus::TooFar;
        }

        return SensorRangeStatus::Ok;
    }

    bool isInBlindZone() const { return _inBlindZone; }
};
