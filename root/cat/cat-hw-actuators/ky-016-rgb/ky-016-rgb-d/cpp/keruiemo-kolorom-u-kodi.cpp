const uint8_t PIN_R = 9;    // усі три — PWM-піни (з «~» на Uno)
const uint8_t PIN_G = 10;
const uint8_t PIN_B = 11;

void setColor(uint8_t r, uint8_t g, uint8_t b) {
  analogWrite(PIN_R, r);    // 0 = колір вимкнено, 255 = повна яскравість
  analogWrite(PIN_G, g);
  analogWrite(PIN_B, b);
}

void setup() {
  setColor(255, 90, 0);     // багато червоного, трохи зеленого, без синього → помаранчевий
}

void loop() {}
