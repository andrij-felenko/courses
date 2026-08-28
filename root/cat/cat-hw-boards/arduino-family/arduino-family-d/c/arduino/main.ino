void setup() {
  // виконується один раз при старті: тут налаштовуємо піни, порти, давачі
  pinMode(13, OUTPUT);
}

void loop() {
  // крутиться нескінченно, доки плата жива: тут головна робота
  digitalWrite(13, HIGH);
  delay(500);
  digitalWrite(13, LOW);
  delay(500);
}
