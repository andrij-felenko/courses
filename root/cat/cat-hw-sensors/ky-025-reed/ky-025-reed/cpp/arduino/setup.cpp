const int reedPin = 2;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;
int lastState = HIGH;

void setup() {
    pinMode(reedPin, INPUT);
}

void loop() {
    int currentState = digitalRead(reedPin);
    if (currentState != lastState) {
        lastDebounceTime = millis();
        lastState = currentState;
    }
    if ((millis() - lastDebounceTime) > debounceDelay) {
        // Стан стабілізувався
    }
}
