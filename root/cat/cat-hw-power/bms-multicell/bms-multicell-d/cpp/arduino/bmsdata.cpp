#include <Arduino.h>

struct BmsData {
  uint16_t cellVoltages[4];
  uint8_t faultFlags;
  bool isValid;
};

BmsData readBmsTelemetry() {
  BmsData data;
  data.isValid = false;
  
  if (Serial1.available() >= 13) {
    if (Serial1.read() == 0xDD && Serial1.read() == 0x03) {
      uint8_t len = Serial1.read();
      uint8_t buffer[16];
      Serial1.readBytes(buffer, len + 2);
      
      for (int i = 0; i < 4; i++) {
        data.cellVoltages[i] = (buffer[i * 2] << 8) | buffer[i * 2 + 1];
      }
      data.faultFlags = buffer[8];
      data.isValid = true;
    }
  }
  return data;
}
