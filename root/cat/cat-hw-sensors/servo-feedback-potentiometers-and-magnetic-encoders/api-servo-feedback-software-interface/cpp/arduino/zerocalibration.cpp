#include <Arduino.h>

class ZeroCalibration {
private:
    uint16_t _zeroOffset;
    const uint16_t _maxRes;

public:
    ZeroCalibration(uint16_t maxResolution) : _zeroOffset(0), _maxRes(maxResolution) {}

    void calibrateZero(uint16_t rawAngle) {
        _zeroOffset = rawAngle % _maxRes;
    }

    uint16_t getAlignedAngle(uint16_t rawAngle) const {
        int32_t aligned = static_cast<int32_t>(rawAngle) - static_cast<int32_t>(_zeroOffset);
        if (aligned < 0) {
            aligned += _maxRes;
        }
        return static_cast<uint16_t>(aligned);
    }
};
