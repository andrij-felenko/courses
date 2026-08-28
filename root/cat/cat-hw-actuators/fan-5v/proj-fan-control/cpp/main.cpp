// Крива з гістерезисом: пуск на tOn, а стоп аж на tOff (нижче за tOn)
uint8_t tempToPercentHyst(float t) {
  static bool running = false;                 // пам'ять рішення між викликами
  const float tOn = 35.0f, tOff = 30.0f, tMax = 65.0f;
  if (!running && t >= tOn)  running = true;   // нагрілося до tOn — вмикаємось
  if ( running && t <  tOff) running = false;  // охололо аж до tOff — вимикаємось
  if (!running) return 0;
  if (t >= tMax) return 100;
  return (uint8_t)((t - tOff) / (tMax - tOff) * 100.0f);
}
