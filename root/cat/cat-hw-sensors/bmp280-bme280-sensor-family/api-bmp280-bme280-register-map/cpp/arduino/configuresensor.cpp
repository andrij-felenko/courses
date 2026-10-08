void configureSensor() {
  // 1. Запис config (0xF5)
  Wire.beginTransmission(BMP280_ADDR);
  Wire.write(0xF5);
  Wire.write((0x02 << 5) | (0x02 << 2)); // t_sb = 62.5ms, filter = 4
  Wire.endTransmission();

  // 2. Запис ctrl_hum (0xF2) - обов'язково перед ctrl_meas!
  Wire.beginTransmission(BMP280_ADDR);
  Wire.write(0xF2);
  Wire.write(0x01); // osrs_h = x1
  Wire.endTransmission();

  // 3. Запис ctrl_meas (0xF4) - фіксує і ctrl_hum, і ctrl_meas
  Wire.beginTransmission(BMP280_ADDR);
  Wire.write(0xF4);
  Wire.write((0x02 << 5) | (0x05 << 2) | 0x03); // osrs_t = x2, osrs_p = x16, mode = Normal
  Wire.endTransmission();
}
