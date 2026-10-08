#include <Arduino.h>

class BLDCEncoderFOC {
private:
  const uint16_t cpr = 16384;
  uint8_t polePairs;
  uint16_t zeroOffset;

public:
  BLDCEncoderFOC(uint8_t pp, uint16_t offset) : polePairs(pp), zeroOffset(offset) {}

  float getElectricalAngleRad(uint16_t rawAngle) {
    int32_t corrected = (int32_t)rawAngle - (int32_t)zeroOffset;
    if (corrected < 0) {
      corrected += cpr;
    }
    float mechNorm = (float)corrected / (float)cpr;
    float elecRad = fmod(mechNorm * polePairs * 2.0f * PI, 2.0f * PI);
    if (elecRad < 0.0f) elecRad += 2.0f * PI;
    return elecRad;
  }
};
