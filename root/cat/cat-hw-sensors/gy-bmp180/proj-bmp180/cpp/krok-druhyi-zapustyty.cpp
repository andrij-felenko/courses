// Режим передискретизації: 0..3. Більше — точніше, але повільніше.
static const uint8_t OSS = 3;   // ultra high resolution

// Тривалість паузи на вимір тиску залежно від OSS, мс (із запасом).
static const uint8_t PRESS_WAIT_MS[4] = { 5, 8, 14, 26 };

// Запустити вимір температури й повернути сире 16-бітне значення (UT).
static int32_t bmp180_read_ut() {
  Wire.beginTransmission(BMP180_ADDR);
  Wire.write(0xF4);            // керівний регістр
  Wire.write(0x2E);            // команда «зміряй температуру»
  Wire.endTransmission();
  delay(5);                    // ~4.5 мс + запас

  return (int32_t)bmp180_read_u16(0xF6);   // старший+молодший байт → UT
}

// Запустити вимір тиску (з обраним OSS) і повернути сире значення (UP).
static int32_t bmp180_read_up() {
  Wire.beginTransmission(BMP180_ADDR);
  Wire.write(0xF4);
  Wire.write(0x34 + (OSS << 6));   // команда «зміряй тиск» + режим OSS
  Wire.endTransmission();
  delay(PRESS_WAIT_MS[OSS]);       // пауза за таблицею для цього OSS

  // Тиск — це ТРИ байти: 0xF6 (старший), 0xF7, 0xF8 (найдрібніший).
  Wire.beginTransmission(BMP180_ADDR);
  Wire.write(0xF6);
  Wire.endTransmission(false);
  Wire.requestFrom((int)BMP180_ADDR, 3);
  uint8_t msb  = Wire.read();
  uint8_t lsb  = Wire.read();
  uint8_t xlsb = Wire.read();

  // Зібрати 19-бітне значення й зсунути на (8 − OSS): той самий OSS, що й у команді!
  int32_t up = (((int32_t)msb << 16) | ((int32_t)lsb << 8) | xlsb) >> (8 - OSS);
  return up;
}
