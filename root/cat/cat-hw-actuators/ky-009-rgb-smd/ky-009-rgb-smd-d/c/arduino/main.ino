// KY-009, спільний катод. R→D9, G→D10, B→D11 (кожен ЧЕРЕЗ резистор); − → GND.
const int R = 9, G = 10, B = 11;

void setup() {
  pinMode(R, OUTPUT);
  pinMode(G, OUTPUT);
  pinMode(B, OUTPUT);
}

void loop() {
  // Помаранчевий: повний червоний, півзеленого, без синього.
  // Спільний катод → більше число = яскравіше.
  analogWrite(R, 255);   // червоний на повну
  analogWrite(G, 128);   // зелений наполовину
  analogWrite(B, 0);     // синій вимкнено
}
