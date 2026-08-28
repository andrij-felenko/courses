// 74HC595: виставляємо один байт на 8 виходів функцією shiftOut().
// DS(14)→нога 11, SHCP(11)→нога 12, STCP(12)→нога 8.
// OE(13)→GND, MR(10)→+5V, Vcc(16)→+5V, GND(8)→спільна.
const int DATA  = 11;   // → DS
const int CLOCK = 12;   // → SHCP
const int LATCH = 8;    // → STCP

void writeByte(uint8_t value) {
  digitalWrite(LATCH, LOW);                        // закриваємо засувку: набираємось потай
  shiftOut(DATA, CLOCK, MSBFIRST, value);          // 8 тактів: заштовхали 8 бітів
  digitalWrite(LATCH, HIGH);                        // фронт засувки → усі 8 виходів оновились разом
}

void setup() {
  pinMode(DATA, OUTPUT);
  pinMode(CLOCK, OUTPUT);
  pinMode(LATCH, OUTPUT);
}

void loop() {
  // «біжуча одиниця»: по черзі запалюємо кожен вихід
  for (int i = 0; i < 8; i++) {
    writeByte(1 << i);      // 1<<i = одиниця в i-й позиції: 00000001, 00000010, ...
    delay(120);
  }
}
