// 74HC595 → ULN2003: регістр адресує канали, масив тягне їхній струм.
// Q0..Q6 регістра → IN1..IN7 масиву. COM(9) масиву → +V навантаження.
// Кожен «1» у байті → відповідний вихід ULN2003 стягує своє навантаження в −.
const int DATA = 11, CLOCK = 12, LATCH = 8;

void setChannels(uint8_t mask) {          // біт i маски → канал (i+1) масиву
  digitalWrite(LATCH, LOW);
  shiftOut(DATA, CLOCK, MSBFIRST, mask);
  digitalWrite(LATCH, HIGH);
}

void setup() {
  pinMode(DATA, OUTPUT);  pinMode(CLOCK, OUTPUT);  pinMode(LATCH, OUTPUT);
}

void loop() {
  setChannels(0b00000011);   // ввімкнули канали 1 і 2 (напр. два реле)
  delay(1000);
  setChannels(0b01001000);   // канали 4 і 7
  delay(1000);
  setChannels(0b00000000);   // усе вимкнули
  delay(1000);
}
