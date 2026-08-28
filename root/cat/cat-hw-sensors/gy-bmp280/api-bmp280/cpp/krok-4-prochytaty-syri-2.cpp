// Температура в °C.
float bmp280_temperature(void) {
  int32_t adc_T, adc_P;
  if (!bmp280_read_raw(&adc_T, &adc_P)) return NAN;
  return bmp280_compensate_T(adc_T) / 100.0f;      // соті градуса → °C
}

// Тиск у гПа. САМ читає й температуру (щоб оновити t_fine) перед тиском.
float bmp280_pressure_hpa(void) {
  int32_t adc_T, adc_P;
  if (!bmp280_read_raw(&adc_T, &adc_P)) return NAN;
  bmp280_compensate_T(adc_T);                       // 1) спершу T → оновлює t_fine
  uint32_t p_q248 = bmp280_compensate_P(adc_P);     // 2) потім P, з готовим t_fine
  return (p_q248 / 256.0f) / 100.0f;                // Q24.8 → Па → гПа
}
