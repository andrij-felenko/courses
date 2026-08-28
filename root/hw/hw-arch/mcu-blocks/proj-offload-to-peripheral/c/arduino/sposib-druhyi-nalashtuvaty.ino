const int PIN = 18;
const int CH  = 0;       // канал LEDC
const int FREQ = 1000;   // Гц
const int RES  = 10;     // розрядність лічильника: 10 біт → діапазон 0..1023

void setup() {
  ledcSetup(CH, FREQ, RES);    // налаштувати канал: частота і роздільність
  ledcAttachPin(PIN, CH);      // прив'язати ніжку до каналу
  ledcWrite(CH, 512);          // шпаруватість 512/1023 ≈ 50 % — і все
}

void loop() {
  // порожньо: сигнал іде сам; ядро вільне для будь-чого
}
