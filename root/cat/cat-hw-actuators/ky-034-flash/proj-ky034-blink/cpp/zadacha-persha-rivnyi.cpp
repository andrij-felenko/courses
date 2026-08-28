const uint8_t PIN_LED = 8;             // S модуля на цифровому виході

const unsigned long ON_MS  = 500;      // скільки триває «увімкнено»
const unsigned long OFF_MS = 500;      // скільки триває «згасло»

bool          ledOn      = false;      // поточний стан вогника
unsigned long lastChange = 0;          // коли востаннє перемикали (мс від старту)

void setup() {
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);          // старт зі згаслого — відомий початковий стан
}

void loop() {
  unsigned long now = millis();
  // скільки має тривати поточна фаза: якщо горить — ON_MS, якщо згас — OFF_MS
  unsigned long phase = ledOn ? ON_MS : OFF_MS;

  if (now - lastChange >= phase) {     // час перемкнути фазу?
    lastChange = now;
    ledOn = !ledOn;
    digitalWrite(PIN_LED, ledOn ? HIGH : LOW);
  }

  // тут loop() пролітає вільно — можна читати кнопки, опитувати давачі, крутити іншу логіку
}
