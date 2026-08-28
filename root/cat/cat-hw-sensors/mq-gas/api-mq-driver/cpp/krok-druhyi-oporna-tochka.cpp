// У чистому повітрі Rₛ більше за R₀ у стільки разів (з графіка даташита MQ-2).
const float CLEAN_AIR_FACTOR = 9.83f;

// Виміряти R₀ цього екземпляра: усереднити Rₛ у чистому повітрі й поділити на множник.
float mqCalibrateR0(int analogPin) {
  const int   N = 50;        // скільки замірів усереднити
  const int   MS = 500;      // пауза між ними
  float rsSum = 0.0f;
  for (int i = 0; i < N; i++) {
    rsSum += mqReadRs(analogRead(analogPin));
    delay(MS);
  }
  float rsAir = rsSum / N;              // середній опір у чистому повітрі
  return rsAir / CLEAN_AIR_FACTOR;      // → R₀ цього давача
}
