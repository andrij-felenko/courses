void setup() {
  Serial.begin(115200);
  Wire.begin();                                    // (на ESP32/Pico — зі своїми ніжками)

  uint8_t id;
  if (!bmp280_who_am_i(&id) || id != BMP280_CHIP_ID) {
    Serial.println(F("Це не BMP280 (або давач мовчить). Стоп."));
    while (true) delay(1000);
  }
  bmp280_read_calibration();                        // один раз — коефіцієнти
  bmp280_configure();                               // передискретизація, фільтр, режим
  Serial.println(F("BMP280 готовий (сирий драйвер)."));
}

void loop() {
  Serial.print(F("T = ")); Serial.print(bmp280_temperature(), 2);   Serial.print(F(" C   "));
  Serial.print(F("P = ")); Serial.print(bmp280_pressure_hpa(), 2);  Serial.println(F(" hPa"));
  delay(1000);
}
