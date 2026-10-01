const byte HALL_A_PIN = 2;
const byte HALL_B_PIN = 3;
volatile long encoderPosition = 0;

void IRAM_ATTR onHallAChange() {
  bool stateA = digitalRead(HALL_A_PIN);
  bool stateB = digitalRead(HALL_B_PIN);
  if (stateA == stateB) {
    encoderPosition++;
  } else {
    encoderPosition--;
  }
}

void setup() {
  pinMode(HALL_A_PIN, INPUT_PULLUP);
  pinMode(HALL_B_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(HALL_A_PIN), onHallAChange, CHANGE);
}
