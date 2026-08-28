const uint8_t PIN_BUZ = 8;

unsigned long toneOffAt = 0;   // millis(), коли вимкнути тон; 0 = вже мовчимо
bool          toneOn    = false;

// Почати тон freq Гц на dur мс і одразу повернутися.
void beep(unsigned int freq, unsigned int dur) {
  tone(PIN_BUZ, freq);            // залізо саме жене меандр; ми не чекаємо
  toneOffAt = millis() + dur;     // запам'ятали ДЕДЛАЙН, а не «спимо dur мс»
  toneOn    = true;
}

// Кликати на КОЖНОМУ витку loop(): гляне на годинник і вимкне тон, коли час.
void buzzerUpdate() {
  if (toneOn && millis() >= toneOffAt) {
    noTone(PIN_BUZ);
    toneOn = false;
  }
}

void setup() {
  pinMode(PIN_BUZ, OUTPUT);
  beep(1000, 200);                // пікнули 1 кГц на 200 мс
}

void loop() {
  buzzerUpdate();                 // ← зумер обслуговується тут, фоном
  // ...будь-яка інша робота: кнопки, давачі, мотор — усе жваве...
}
