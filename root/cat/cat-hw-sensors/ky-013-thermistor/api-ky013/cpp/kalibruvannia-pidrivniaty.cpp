float T_OFFSET = 0.0f;   // поправка з калібрування, °C (спершу 0)

float readTempCalibrated() {
  float t = resistanceToTempC(rawToResistance(readRawAveraged(16)));
  return t + T_OFFSET;
}

// РАЗОВО: поклади поряд добрий термометр, дай зрівнятися, зчитай обидва.
// Скажімо, еталон показує 23.0, а KY-013 (з T_OFFSET=0) видає 25.4.
// Тоді  T_OFFSET = 23.0 − 25.4 = −2.4;  вписуєш це число у код.
