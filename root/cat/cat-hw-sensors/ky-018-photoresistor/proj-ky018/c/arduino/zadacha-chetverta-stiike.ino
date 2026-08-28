const uint8_t PIN_LDR = A0;
const uint8_t PIN_LED = 13;

const int DARK_ON  = 300;   // темніше цього → УВІМКНУТИ (нижній поріг)
const int LIGHT_OFF = 400;  // світліше цього → ВИМКНУТИ (верхній поріг)

bool lampOn = false;        // поточний стан — частина рішення!

void setup() {
  pinMode(PIN_LED, OUTPUT);
}

void loop() {
  int light = analogRead(PIN_LDR);   // (краще — уже згладжений; див. збірку нижче)

  if (!lampOn && light < DARK_ON)      lampOn = true;    // було світло, стало темно
  else if (lampOn && light > LIGHT_OFF) lampOn = false;  // було темно, стало світло
  // якщо відлік між порогами — жодна умова не спрацює, стан лишається

  digitalWrite(PIN_LED, lampOn ? HIGH : LOW);
  delay(50);
}
