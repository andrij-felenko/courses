const uint8_t PIN_LED = 13;   // вбудований світлодіод сидить на виводі 13

void setup() {
    pinMode(PIN_LED, OUTPUT);   // вивід тепер керує світом
}

void loop() {
    digitalWrite(PIN_LED, HIGH);  // 5 В на виводі → світлодіод світить
    delay(500);                   // чекаємо 500 мс
    digitalWrite(PIN_LED, LOW);   // 0 В на виводі → гасне
    delay(500);
}
