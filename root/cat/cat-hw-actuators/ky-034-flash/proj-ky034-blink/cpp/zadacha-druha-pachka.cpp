const uint8_t PIN_LED = 8;
const uint8_t PIN_BTN = 2;             // кнопка між піном і землею

const unsigned long FLASH_MS = 200;    // тривалість кожної півфази (горить / згас)

uint8_t       flashesLeft = 0;         // скільки перемикань стану ще лишилось
bool          ledOn       = false;
unsigned long lastChange  = 0;

void setup() {
  pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_BTN, INPUT_PULLUP);      // у спокої HIGH; натиск замикає на землю → LOW
  digitalWrite(PIN_LED, LOW);
}

// Запустити пачку з n спалахів. Один «спалах» = увімкнути + вимкнути = 2 перемикання.
void startBurst(uint8_t n) {
  flashesLeft = n * 2;                 // n спалахів = 2·n змін стану
  lastChange  = millis();
  ledOn       = true;                  // перше перемикання — одразу вмикаємо
  digitalWrite(PIN_LED, HIGH);
}

void loop() {
  unsigned long now = millis();

  // 1) подія: натиск запускає пачку, але лише коли попередня вже добігла
  static bool wasPressed = false;
  bool pressed = (digitalRead(PIN_BTN) == LOW);
  if (pressed && !wasPressed && flashesLeft == 0) {
    startBurst(3);                     // блимнути тричі
  }
  wasPressed = pressed;

  // 2) сам неблокуючий прогін пачки
  if (flashesLeft > 0 && now - lastChange >= FLASH_MS) {
    lastChange = now;
    flashesLeft--;
    if (flashesLeft == 0) {
      ledOn = false;                   // остання фаза — гарантовано гасимо
    } else {
      ledOn = !ledOn;                  // перемикаємо далі
    }
    digitalWrite(PIN_LED, ledOn ? HIGH : LOW);
  }

  // loop() лишається вільним увесь час, і під час пачки теж
}
