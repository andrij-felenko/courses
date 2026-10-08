// Передача даних у зсувний регістр 74HC595 (C++ / Arduino)
#include <Arduino.h>
#include <SPI.h>

const uint8_t LATCH_PIN = 10;

void sendFrame74HC595(uint8_t segmentMask, uint8_t digitSelectMask) {
  digitalWrite(LATCH_PIN, LOW);
  
  // Передача через апаратний SPI
  SPI.transfer(digitSelectMask); // Другий регістр (розрядні ключі)
  SPI.transfer(segmentMask);     // Перший регістр (сегментні лінії)
  
  digitalWrite(LATCH_PIN, HIGH); // Засувка даних на виходах
}
