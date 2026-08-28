const byte LATCH = 4, CLK = 7, DATA = 8;   // виводи двох 74HC595 шилда

// байти сегментів для цифр 0..9 (спільний анод: 0 = сегмент світиться)
const byte SEG[10] = {
  0xC0, 0xF9, 0xA4, 0xB0, 0x99, 0x92, 0x82, 0xF8, 0x80, 0x90
};
const byte SEL[4] = { 0xF1, 0xF2, 0xF4, 0xF8 };   // вибір розряду 1..4

int counter = 0;

void setup() {
  pinMode(LATCH, OUTPUT);
  pinMode(CLK,   OUTPUT);
  pinMode(DATA,  OUTPUT);
  pinMode(A1, INPUT_PULLUP);   // кнопка S1
  pinMode(A2, INPUT_PULLUP);   // кнопка S2
}

// виставити один розряд: байт сегментів + байт вибору, клац латчем
void showDigit(byte segByte, byte pos) {
  digitalWrite(LATCH, LOW);
  shiftOut(DATA, CLK, MSBFIRST, segByte);   // спершу сегменти
  shiftOut(DATA, CLK, MSBFIRST, SEL[pos]);  // потім вибір розряду
  digitalWrite(LATCH, HIGH);
}

// показати ціле 0..9999, перебравши всі чотири розряди по колу
void refresh(int value) {
  int v = value < 0 ? -value : value;       // модуль для показу
  byte d[4] = {
    (byte)(v / 1000 % 10), (byte)(v / 100 % 10),
    (byte)(v / 10 % 10),   (byte)(v % 10)
  };
  for (byte pos = 0; pos < 4; pos++) {
    showDigit(SEG[d[pos]], pos);
    delayMicroseconds(500);                 // трохи потримати розряд
    digitalWrite(LATCH, LOW);               // погасити перед наступним
    shiftOut(DATA, CLK, MSBFIRST, 0xFF);    // усі сегменти згашені
    shiftOut(DATA, CLK, MSBFIRST, 0xFF);
    digitalWrite(LATCH, HIGH);
  }
}

void loop() {
  static bool s1was = false, s2was = false;   // попередній стан для фронту

  bool s1 = (digitalRead(A1) == LOW);
  bool s2 = (digitalRead(A2) == LOW);
  if (s1 && !s1was) counter++;                // спрацювати раз на натиск
  if (s2 && !s2was) counter--;
  s1was = s1;  s2was = s2;

  refresh(counter);                           // перебрати розряди — раз за прохід
}
