const uint8_t BUZZER = 8;

bool          beeping   = false;   // чи зараз триває біп
unsigned long beepUntil = 0;       // момент (мс), коли біп треба вимкнути

void setup() {
  pinMode(BUZZER, OUTPUT);
  digitalWrite(BUZZER, LOW);
}

// Запустити біп на ms мілісекунд і ОДРАЗУ повернути керування.
void beepStart(unsigned int ms) {
  digitalWrite(BUZZER, HIGH);      // вмикаємо звук зараз
  beeping   = true;
  beepUntil = millis() + ms;       // запам'ятовуємо, КОЛИ вимкнути
}

// Смикати в КОЖНОМУ loop(): гасить біп, коли настав його час. Нічого не блокує.
void beepUpdate() {
  if (beeping && (long)(millis() - beepUntil) >= 0) {  // час вийшов?
    digitalWrite(BUZZER, LOW);
    beeping = false;
  }
}

void loop() {
  // приклад події: раз на 2 с пускаємо короткий біп
  static unsigned long lastEvent = 0;
  if (millis() - lastEvent >= 2000) {
    lastEvent = millis();
    beepStart(80);                 // пустили й полетіли далі — loop() не завмер
  }

  beepUpdate();                    // єдиний обов'язок біпа щоцикл

  // ...тут будь-яка інша логіка: читання кнопок, давачів — вона не блокована
}
