// ── Шлюз звуку для ESP32 (LEDC). Решта модуля кличе tone()/noTone() через нього. ──
const uint8_t PIN_BUZ    = 25;    // будь-який GPIO, здатний на вихід
const int     BUZ_CHAN   = 0;     // один канал LEDC під зумер
const int     BUZ_RES    = 10;    // роздільність (для tone байдужа, треба для ledcSetup)

void buzzerBegin() {
  ledcSetup(BUZ_CHAN, 2000, BUZ_RES);   // завести канал (частоту задамо тоном)
  ledcAttachPin(PIN_BUZ, BUZ_CHAN);     // прив'язати пін до каналу
}

// Наші власні tone()/noTone поверх LEDC — сигнатури як в Arduino, тіло інше.
void tone(uint8_t /*pin*/, unsigned int freq) {
  ledcWriteTone(BUZ_CHAN, freq);        // меандр 50% на freq Гц; 0 → тиша
}
void noTone(uint8_t /*pin*/) {
  ledcWriteTone(BUZ_CHAN, 0);           // 0 Гц = вимкнути (шпаруватість у нуль)
}

void setup() {
  buzzerBegin();
  playMelody(scaleUpDown, sizeof(scaleUpDown) / sizeof(scaleUpDown[0]));
}
// loop(), buzzerUpdate(), таблиця нот, сигнали — БЕЗ ЖОДНОЇ ЗМІНИ
