const uint8_t PIN_REED = 3;
const unsigned long DEBOUNCE_MS = 20;   // двері — не поспішають, вікно можна більше

inline bool magnetPresent(uint8_t pin) { return digitalRead(pin) == LOW; }

bool          doorClosed  = false;      // стійкий (уже підтверджений) стан
bool          reading     = false;      // останнє миттєве читання
unsigned long lastChange  = 0;

void setup() {
  pinMode(PIN_REED, INPUT);
  Serial.begin(9600);
  doorClosed = magnetPresent(PIN_REED); // початковий стан при вмиканні
}

void loop() {
  unsigned long now = millis();
  bool now_reading = magnetPresent(PIN_REED);

  // щойно миттєве читання відрізнилось від попереднього — перезапускаємо таймер
  if (now_reading != reading) {
    reading = now_reading;
    lastChange = now;
  }

  // читання протрималось незмінним довше за вікно → це справжня зміна, не брязкіт
  if ((now - lastChange) >= DEBOUNCE_MS && now_reading != doorClosed) {
    doorClosed = now_reading;             // фіксуємо новий стійкий стан
    Serial.println(doorClosed ? "зачинено" : "відчинено");
    // сюди — одноразова дія на перехід (надіслати, приспати, увімкнути…)
  }
}
