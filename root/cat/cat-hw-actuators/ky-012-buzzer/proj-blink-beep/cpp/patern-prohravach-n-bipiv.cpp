const uint8_t BUZZER = 8;
const uint8_t PIN_BTN = 2;         // кнопка між піном і землею

const unsigned long HALF_MS = 100; // тривалість кожної півфази (біп / пауза)

uint8_t       stepsLeft = 0;       // скільки перемикань стану ще лишилось
bool          soundOn   = false;
unsigned long lastFlip  = 0;

void setup() {
  pinMode(BUZZER, OUTPUT);
  pinMode(PIN_BTN, INPUT_PULLUP);  // у спокої HIGH; натиск замикає на землю → LOW
  digitalWrite(BUZZER, LOW);
}

// Запустити серію з n біпів. Один біп = увімкнути + вимкнути = 2 перемикання.
void beepSeries(uint8_t n) {
  stepsLeft = n * 2;               // n біпів = 2·n змін стану
  lastFlip  = millis();
  soundOn   = true;                // перший крок — одразу вмикаємо звук
  digitalWrite(BUZZER, HIGH);
}

bool seriesBusy() { return stepsLeft > 0; }

void loop() {
  unsigned long now = millis();

  // 1) подія: натиск запускає серію, лише коли попередня вже добігла
  static bool wasPressed = false;
  bool pressed = (digitalRead(PIN_BTN) == LOW);
  if (pressed && !wasPressed && !seriesBusy()) {
    beepSeries(3);                 // три біпи на помилку
  }
  wasPressed = pressed;

  // 2) неблокуючий прогін серії
  if (stepsLeft > 0 && now - lastFlip >= HALF_MS) {
    lastFlip = now;
    stepsLeft--;
    if (stepsLeft == 0) {
      soundOn = false;             // остання фаза — гарантовано гасимо
    } else {
      soundOn = !soundOn;          // перемикаємо далі: біп / пауза / біп …
    }
    digitalWrite(BUZZER, soundOn ? HIGH : LOW);
  }

  // loop() лишається вільним увесь час, і під час серії теж
}
