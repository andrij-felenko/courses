// KY-009, спільний катод, живлення 5 В (Arduino Uno/Nano).
// R, G, B — кожен ЧЕРЕЗ свій гасильний резистор до PWM-піна (~).
const uint8_t PIN_R = 9;   // ~D9
const uint8_t PIN_G = 10;  // ~D10
const uint8_t PIN_B = 11;  // ~D11

void setup() {
  pinMode(PIN_R, OUTPUT);
  pinMode(PIN_G, OUTPUT);
  pinMode(PIN_B, OUTPUT);
}

// Єдиний шлюз кольору. r, g, b — яскравості 0…255.
// Спільний катод: більше число → яскравіше.
void setColor(uint8_t r, uint8_t g, uint8_t b) {
  analogWrite(PIN_R, r);
  analogWrite(PIN_G, g);
  analogWrite(PIN_B, b);
}

void loop() {
  setColor(255,   0,   0);  // червоний
  delay(600);
  setColor(  0, 255,   0);  // зелений
  delay(600);
  setColor(  0,   0, 255);  // синій
  delay(600);
  setColor(255, 255,   0);  // жовтий = червоний + зелений
  delay(600);
  setColor(255, 255, 255);  // білий = усі три
  delay(600);
}
