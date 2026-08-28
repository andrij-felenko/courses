// --- Опитування: loop сам перевіряє ---
void loop() {
  if (digitalRead(BTN) == LOW) { /* натиснуто */ }
  // ... інша робота, що затримує перевірку
}

// --- Переривання: подія сама кличе ---
volatile bool pressed = false;          // прапорець (volatile — обовʼязково для ISR)

void IRAM_ATTR onPress() {               // обробник: КОРОТКО
  pressed = true;                        // лише підняти прапорець
}

void setup() {
  pinMode(BTN, INPUT_PULLUP);            // увімкнути підтяжку
  attachInterrupt(digitalPinToInterrupt(BTN), onPress, FALLING);
}

void loop() {
  if (pressed) {                         // loop вільний, реакція вмить
    pressed = false;
    /* обробити натиск */
  }
}
