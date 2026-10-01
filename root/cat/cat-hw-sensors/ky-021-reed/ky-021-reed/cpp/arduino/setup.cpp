const int REED_PIN = 2;
int lastState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long DEBOUNCE_DELAY = 50;

void setup() {
  pinMode(REED_PIN, INPUT);
}

void loop() {
  int reading = digitalRead(REED_PIN);
  if (reading != lastState) {
    lastDebounceTime = millis();
  }
  if ((millis() - lastDebounceTime) > DEBOUNCE_DELAY) {
    if (reading == LOW) {
      // Магніт поруч
    }
  }
  lastState = reading;
}
