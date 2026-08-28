// Найдрібніший скетч: блимаємо вбудованим синім LED на ESP-01S.
// LED сидить на GPIO2 і УВІМКНЕНО ЗА НИЗЬКИМ РІВНЕМ:
//   LOW  → світиться,   HIGH → гасне.

const int LED = 2;              // GPIO2 — до нього припаяно синій світлодіод

void setup() {
  pinMode(LED, OUTPUT);         // ніжка працює на вихід
  digitalWrite(LED, HIGH);      // старт із погашеним (HIGH = вимкнено!)
}

void loop() {
  digitalWrite(LED, LOW);       // світиться
  delay(500);                   // 0.5 с
  digitalWrite(LED, HIGH);      // гасне
  delay(500);
}
