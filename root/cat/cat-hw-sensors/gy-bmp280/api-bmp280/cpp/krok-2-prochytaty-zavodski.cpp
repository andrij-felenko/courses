// Заводські коефіцієнти BMP280 (з даташита; типи саме такі!).
struct bmp280_calib {
  uint16_t dig_T1;   // беззнаковий
  int16_t  dig_T2, dig_T3;
  uint16_t dig_P1;   // беззнаковий
  int16_t  dig_P2, dig_P3, dig_P4, dig_P5, dig_P6, dig_P7, dig_P8, dig_P9;
};

static bmp280_calib calib;      // сюди прочитаємо один раз на старті

// Прочитати всі 24 байти калібрування від 0x88 і розкласти в структуру.
bool bmp280_read_calibration(void) {
  uint8_t b[24];
  if (!rdN(0x88, b, 24)) return false;

  // Кожні два байти: молодший перший (little-endian) → 16-бітне число.
  calib.dig_T1 = (uint16_t)(b[0]  | (b[1]  << 8));
  calib.dig_T2 = (int16_t) (b[2]  | (b[3]  << 8));
  calib.dig_T3 = (int16_t) (b[4]  | (b[5]  << 8));
  calib.dig_P1 = (uint16_t)(b[6]  | (b[7]  << 8));
  calib.dig_P2 = (int16_t) (b[8]  | (b[9]  << 8));
  calib.dig_P3 = (int16_t) (b[10] | (b[11] << 8));
  calib.dig_P4 = (int16_t) (b[12] | (b[13] << 8));
  calib.dig_P5 = (int16_t) (b[14] | (b[15] << 8));
  calib.dig_P6 = (int16_t) (b[16] | (b[17] << 8));
  calib.dig_P7 = (int16_t) (b[18] | (b[19] << 8));
  calib.dig_P8 = (int16_t) (b[20] | (b[21] << 8));
  calib.dig_P9 = (int16_t) (b[22] | (b[23] << 8));
  return true;
}
