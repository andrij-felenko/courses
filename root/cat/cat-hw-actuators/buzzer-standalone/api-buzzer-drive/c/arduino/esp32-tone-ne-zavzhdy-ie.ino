// ESP32, ядро 3.x: пасивний зумер через апаратний LEDC
const uint8_t BUZ = 25;          // будь-який GPIO, що вміє вихід

void setup() {
  // freq — стартова частота (переб'ється нижче), resolution — біти
  // роздільної здатності шпаруватості (для тону нам байдужа, беремо 8)
  ledcAttach(BUZ, 2000, 8);      // прив'язали LEDC до виводу
}

void playNote(uint32_t freq, uint16_t ms) {
  if (freq == 0) ledcWriteTone(BUZ, 0);   // 0 Гц → тиша
  else           ledcWriteTone(BUZ, freq); // 50%-меандр цієї частоти
  delay(ms);                                // (у бойовому коді — millis!)
  ledcWriteTone(BUZ, 0);
}

void loop() {
  playNote(523, 200);            // до
  playNote(659, 200);            // мі
  playNote(784, 400);            // соль
  delay(2000);
}
