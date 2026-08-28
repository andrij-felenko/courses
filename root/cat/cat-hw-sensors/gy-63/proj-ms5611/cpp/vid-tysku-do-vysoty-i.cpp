// Продовження того самого скетча: об'єкт baro вже створено вище.
float g_p0_hPa = 1013.25;        // опорний тиск; поки не обнулили — стандартна атмосфера

// Барометрична формула висоти (те, що всередині getAltitude()).
static float altitude_m(float pressure_hPa, float seaLevel_hPa) {
  return 44330.0f * (1.0f - powf(pressure_hPa / seaLevel_hPa, 0.1903f));
}

// «Обнулити» висоту: узяти поточний тиск за нуль. Усереднюємо ~40 вимірів,
// поки прилад нерухомий (напр. на землі перед злетом), щоб «нуль» не гуляв.
void zeroAltitude() {
  double sum = 0.0;
  const int N = 40;
  for (int i = 0; i < N; i++) {
    baro.read();                 // повний вимір із компенсацією
    sum += baro.getPressure();   // мбар (гПа)
    delay(20);
  }
  g_p0_hPa = (float)(sum / N);   // тепер ця точка = 0 м
}

// Відносна висота над точкою обнулення (метри).
float relativeAltitude_m() {
  baro.read();
  return altitude_m(baro.getPressure(), g_p0_hPa);
}
