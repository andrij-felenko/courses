#include <Arduino.h>
#include <SPI.h>

const int CS_PIN = 5;

// Обчислення біта парної парності
bool getEvenParity(uint16_t val) {
  uint16_t cnt = 0;
  for (int i = 0; i < 16; i++) {
    if ((val >> i) & 1) cnt++;
  }
  return (cnt % 2) != 0;
}

// Пряме опитування AS5048A по SPI
uint16_t readAS5048A(uint16_t regAddress) {
  uint16_t command = 0x4000 | (regAddress & 0x3FFF);
  if (getEvenParity(command)) {
    command |= 0x8000;
  }

  SPI.beginTransaction(SPISettings(5000000, MSBFIRST, SPI_MODE1));
  digitalWrite(CS_PIN, LOW);
  
  // Відправка запиту N і прийом результату N-1
  uint8_t msb = SPI.transfer(highByte(command));
  uint8_t lsb = SPI.transfer(lowByte(command));
  
  digitalWrite(CS_PIN, HIGH);
  SPI.endTransaction();

  uint16_t response = (msb << 8) | lsb;

  // Перевірка прапорця помилки EF (Bit 14)
  if (response & 0x4000) {
    Serial.println("Помилка кадру AS5048A!");
    return 0xFFFF;
  }

  return response & 0x3FFF; // Повертаємо 14 бітів кута
}
