// Той самий 74HC595, але байт жене апаратний SPI — швидко.
// DS(14)→MOSI (нога 11 на Uno), SHCP(11)→SCK (нога 13 на Uno), STCP(12)→нога 10.
#include <SPI.h>

const int LATCH = 10;   // STCP смикаємо вручну; MOSI та SCK бере на себе SPI

void writeByte(uint8_t value) {
  digitalWrite(LATCH, LOW);
  SPI.transfer(value);            // весь байт одним апаратним пострілом
  digitalWrite(LATCH, HIGH);
}

void setup() {
  pinMode(LATCH, OUTPUT);
  SPI.begin();
  SPI.beginTransaction(SPISettings(8000000, MSBFIRST, SPI_MODE0));  // 8 МГц, зі старшого біта
}

void loop() {
  writeByte(0b10101010);   // ввімкнули парні виходи
  delay(300);
  writeByte(0b01010101);   // непарні
  delay(300);
}
