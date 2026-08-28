// Пін, до якого припаяно світлодіод. На UNO вбудований — 13.
const uint8_t LED = 13;

void setup() {
  pinMode(LED, OUTPUT);      // налаштувати пін на вихід
}

void loop() {
  digitalWrite(LED, HIGH);   // подати ~5 В → світлодіод горить
  delay(500);                // чекати 500 мс, нічого не роблячи
  digitalWrite(LED, LOW);    // подати 0 В → гасне
  delay(500);
}
