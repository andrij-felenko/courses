#include <Wire.h>

struct BME280_CalibData {
  uint16_t dig_T1;
  int16_t  dig_T2;
  int16_t  dig_T3;

  uint16_t dig_P1;
  int16_t  dig_P2;
  int16_t  dig_P3;
  int16_t  dig_P4;
  int16_t  dig_P5;
  int16_t  dig_P6;
  int16_t  dig_P7;
  int16_t  dig_P8;
  int16_t  dig_P9;
};

static BME280_CalibData calib;
static int32_t t_fine;

void readCalibrationData(uint8_t i2cAddr) {
  Wire.beginTransmission(i2cAddr);
  Wire.write(0x88); // Початок блоку калібрувальних коефіцієнтів T та P
  Wire.endTransmission();

  Wire.requestFrom(i2cAddr, (uint8_t)24);
  calib.dig_T1 = Wire.read() | (Wire.read() << 8);
  calib.dig_T2 = Wire.read() | (Wire.read() << 8);
  calib.dig_T3 = Wire.read() | (Wire.read() << 8);

  calib.dig_P1 = Wire.read() | (Wire.read() << 8);
  calib.dig_P2 = Wire.read() | (Wire.read() << 8);
  calib.dig_P3 = Wire.read() | (Wire.read() << 8);
  calib.dig_P4 = Wire.read() | (Wire.read() << 8);
  calib.dig_P5 = Wire.read() | (Wire.read() << 8);
  calib.dig_P6 = Wire.read() | (Wire.read() << 8);
  calib.dig_P7 = Wire.read() | (Wire.read() << 8);
  calib.dig_P8 = Wire.read() | (Wire.read() << 8);
  calib.dig_P9 = Wire.read() | (Wire.read() << 8);
}

int32_t compensateTemperature(int32_t adc_T) {
  int32_t var1 = (((adc_T >> 3) - ((int32_t)calib.dig_T1 << 1)) * (int32_t)calib.dig_T2) >> 11;
  int32_t var2 = (((((adc_T >> 4) - (int32_t)calib.dig_T1) * ((adc_T >> 4) - (int32_t)calib.dig_T1)) >> 12) * (int32_t)calib.dig_T3) >> 14;
  t_fine = var1 + var2;
  return (t_fine * 5 + 128) >> 8; // Повертає температуру в 0.01 °C
}

uint32_t compensatePressure(int32_t adc_P) {
  int64_t var1 = ((int64_t)t_fine) - 128000;
  int64_t var2 = var1 * var1 * (int64_t)calib.dig_P6;
  var2 = var2 + ((var1 * (int64_t)calib.dig_P5) << 17);
  var2 = var2 + (((int64_t)calib.dig_P4) << 35);
  var1 = ((var1 * var1 * (int64_t)calib.dig_P3) >> 8) + ((var1 * (int64_t)calib.dig_P2) << 12);
  var1 = (((((int64_t)1) << 47) + var1)) * ((int64_t)calib.dig_P1) >> 33;

  if (var1 == 0) return 0; // Уникнення ділення на 0

  int64_t p = 1048576 - adc_P;
  p = (((p << 31) - var2) * 3125) / var1;
  var1 = (((int64_t)calib.dig_P9) * (p >> 13) * (p >> 13)) >> 25;
  var2 = (((int64_t)calib.dig_P8) * p) >> 19;
  p = ((p + var1 + var2) >> 8) + (((int64_t)calib.dig_P7) << 4);
  return (uint32_t)p; // Повертає тиск у Q24.8 (Паскалі * 256)
}
