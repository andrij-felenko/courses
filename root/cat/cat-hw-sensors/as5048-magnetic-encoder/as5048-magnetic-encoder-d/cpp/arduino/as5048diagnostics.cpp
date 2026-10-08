#include <Arduino.h>

struct AS5048Diagnostics {
  uint8_t agcValue;
  bool offsetCompOk;
  bool cordicOverflow;
  bool fieldTooLow;
  bool fieldTooHigh;
  bool isValid;
};

AS5048Diagnostics parseAS5048Diagnostics(uint16_t rawFrame) {
  AS5048Diagnostics diag;
  diag.agcValue       = rawFrame & 0xFF;
  diag.offsetCompOk  = (rawFrame & (1 << 8)) != 0;
  diag.cordicOverflow = (rawFrame & (1 << 9)) != 0;
  diag.fieldTooLow   = (rawFrame & (1 << 10)) != 0;
  diag.fieldTooHigh  = (rawFrame & (1 << 11)) != 0;
  
  diag.isValid = diag.offsetCompOk && !diag.cordicOverflow && 
                 !diag.fieldTooLow && !diag.fieldTooHigh;
  return diag;
}
