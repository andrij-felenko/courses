const uint8_t PIN_CLK = 2;
const uint8_t PIN_DT  = 3;

long counter = 0;

void setup() {
  pinMode(PIN_CLK, INPUT);        // на платі KY-040 підтяжки на CLK і DT вже є
  pinMode(PIN_DT,  INPUT);
  Serial.begin(9600);
}

void loop() {
  uint8_t result = processEncoder(digitalRead(PIN_CLK), digitalRead(PIN_DT));
  if      (result == DIR_CW)  { counter++; Serial.println(counter); }
  else if (result == DIR_CCW) { counter--; Serial.println(counter); }

  // ... тут може бути решта роботи, АЛЕ вона не має надовго блокувати цикл ...
}
