static float p0_ref = 1013.25f;    // опорний тиск «нуля висоти»

// Викликати на землі перед злетом: зробити поточне місце нульовою висотою.
void bmp280_set_zero_here(void) {
  p0_ref = bmp280_pressure_hpa();  // «тут і зараз» = 0 метрів
}

// Висота ВІДНОСНО запам'ятованого нуля (надійна, не залежить від погоди).
float bmp280_relative_altitude(void) {
  return bmp280_altitude(bmp280_pressure_hpa(), p0_ref);
}
