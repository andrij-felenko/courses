// Обчислює B5 з сирої температури — потрібне і для °C, і для тиску.
static int32_t bmp180_compute_B5(int32_t UT) {
  int32_t X1 = ((UT - (int32_t)cal.AC6) * (int32_t)cal.AC5) >> 15;
  int32_t X2 = ((int32_t)cal.MC << 11) / (X1 + (int32_t)cal.MD);
  return X1 + X2;
}

// Справжня температура в градусах Цельсія.
float bmp180_temperature() {
  int32_t UT = bmp180_read_ut();
  int32_t B5 = bmp180_compute_B5(UT);
  int32_t T  = (B5 + 8) >> 4;       // десяті градуса
  return T / 10.0f;                 // → °C
}

// Справжній тиск у паскалях.
int32_t bmp180_pressure() {
  int32_t UT = bmp180_read_ut();
  int32_t UP = bmp180_read_up();
  int32_t B5 = bmp180_compute_B5(UT);       // температура входить у тиск

  int32_t B6 = B5 - 4000;
  int32_t X1 = ((int32_t)cal.B2 * ((B6 * B6) >> 12)) >> 11;
  int32_t X2 = ((int32_t)cal.AC2 * B6) >> 11;
  int32_t X3 = X1 + X2;
  int32_t B3 = ((((int32_t)cal.AC1 * 4 + X3) << OSS) + 2) / 4;

  X1 = ((int32_t)cal.AC3 * B6) >> 13;
  X2 = ((int32_t)cal.B1 * ((B6 * B6) >> 12)) >> 16;
  X3 = ((X1 + X2) + 2) >> 2;
  uint32_t B4 = ((uint32_t)cal.AC4 * (uint32_t)(X3 + 32768)) >> 15;
  uint32_t B7 = ((uint32_t)UP - B3) * (uint32_t)(50000UL >> OSS);

  int32_t p;
  if (B7 < 0x80000000UL) p = (B7 * 2) / B4;
  else                   p = (B7 / B4) * 2;

  X1 = (p >> 8) * (p >> 8);
  X1 = (X1 * 3038) >> 16;
  X2 = (-7357 * p) >> 16;
  p  = p + ((X1 + X2 + 3791) >> 4);
  return p;                          // паскалі
}
