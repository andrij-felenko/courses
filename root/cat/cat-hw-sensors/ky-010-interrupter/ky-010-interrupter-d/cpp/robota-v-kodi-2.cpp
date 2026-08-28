const int PIN_S      = 2;
const int BLOCKED    = HIGH;      // з калібрування вище
const unsigned long GUARD = 3;    // «мертвий час», мс — гасить дрижання на схилі

volatile unsigned long count = 0;
bool     prev = false;            // попередній стан щілини
unsigned long tEdge = 0;          // час останнього зарахованого фронту

void setup() {
  pinMode(PIN_S, INPUT);
  Serial.begin(9600);
}

void loop() {
  bool now = (digitalRead(PIN_S) == BLOCKED);
  unsigned long t = millis();

  // цікавить лише фронт «вільно → перекрито» і не частіше, ніж раз на GUARD мс
  if (now && !prev && (t - tEdge) > GUARD) {
    count++;
    tEdge = t;
    Serial.println(count);
  }
  prev = now;
}
