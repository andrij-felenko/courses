const uint8_t SW  = 2;      // вивід давача (другий — на GND)
const uint8_t LED = 13;     // вбудований світлодіод

void setup() {
  pinMode(SW, INPUT_PULLUP); // внутрішня підтяжка: спокій = HIGH
  pinMode(LED, OUTPUT);
}

void loop() {
  // активний НУЛЬ: подія = LOW (кулька замкнула на землю)
  if (digitalRead(SW) == LOW) {
    digitalWrite(LED, HIGH);
    delay(50);              // грубий дебаунс: перечекати брязкіт кульки
  } else {
    digitalWrite(LED, LOW);
  }
}
