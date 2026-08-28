const byte LATCH = 4;   // ST_CP — «клац», виставити біти
const byte CLK   = 7;   // SH_CP — тактує зсув
const byte DATA  = 8;   // DS    — біти по одному

// байти сегментів для цифр 0..9 (спільний анод: 0 = світиться)
const byte SEG[10] = {
  0xC0, 0xF9, 0xA4, 0xB0, 0x99, 0x92, 0x82, 0xF8, 0x80, 0x90
};
// вибір розряду: перший, другий, третій, четвертий
const byte SEL[4]  = { 0xF1, 0xF2, 0xF4, 0xF8 };

void setup() {
  pinMode(LATCH, OUTPUT);
  pinMode(CLK,   OUTPUT);
  pinMode(DATA,  OUTPUT);
}

void showDigit(byte value, byte pos) {
  digitalWrite(LATCH, LOW);                       // латч униз — набираємо
  shiftOut(DATA, CLK, MSBFIRST, SEG[value]);      // спершу байт сегментів
  shiftOut(DATA, CLK, MSBFIRST, SEL[pos]);        // потім байт вибору розряду
  digitalWrite(LATCH, HIGH);                      // клац — виставити на виходи
}

void loop() {
  showDigit(5, 0);   // цифра «5» у першому (правому) розряді
}
