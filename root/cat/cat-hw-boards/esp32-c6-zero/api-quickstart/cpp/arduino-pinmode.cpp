#define LED_OUT  15
#define BTN_IN   18

void setup() {
  pinMode(LED_OUT, OUTPUT);
  pinMode(BTN_IN, INPUT_PULLUP);   // ← увага: див. нижче
}

void loop() {
  bool pressed = (digitalRead(BTN_IN) == LOW);  // LOW = натиснута
  digitalWrite(LED_OUT, pressed ? HIGH : LOW);
  delay(20);
}
