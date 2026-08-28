#include <Wire.h>
#define DS3231_ADDR 0x68

// звичайне число → BCD (десяткові цифри по півбайтах)
uint8_t decToBcd(uint8_t v) { return (v / 10) << 4 | (v % 10); }
// BCD → звичайне число
uint8_t bcdToDec(uint8_t b) { return (b >> 4) * 10 + (b & 0x0F); }

// виставити час один раз: 2026-06-11, 14:30:00, середа (день тижня 1..7)
void setTime() {
  Wire.beginTransmission(DS3231_ADDR);
  Wire.write(0x00);             // почати з регістра секунд
  Wire.write(decToBcd(0));      // 0x00 секунди
  Wire.write(decToBcd(30));     // 0x01 хвилини
  Wire.write(decToBcd(14));     // 0x02 години (24-годинний режим)
  Wire.write(decToBcd(4));      // 0x03 день тижня (1..7)
  Wire.write(decToBcd(11));     // 0x04 число
  Wire.write(decToBcd(6));      // 0x05 місяць
  Wire.write(decToBcd(26));     // 0x06 рік (від 2000)
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  // setTime();   // розкоментувати ОДИН раз, щоб завести годинник
}

void loop() {
  // 1) сказати, з якого регістра читати
  Wire.beginTransmission(DS3231_ADDR);
  Wire.write(0x00);                       // покажчик на секунди
  Wire.endTransmission(false);            // false = повторний старт, шину не відпускаємо
  // 2) прочитати 7 байтів підряд (авто-інкремент регістра)
  Wire.requestFrom(DS3231_ADDR, 7);
  uint8_t ss  = bcdToDec(Wire.read() & 0x7F);  // лишаємо 7 бітів цифр секунд
  uint8_t mm  = bcdToDec(Wire.read());
  uint8_t hh  = bcdToDec(Wire.read() & 0x3F);  // 24-год. режим: біти 6..0
  Wire.read();                                  // день тижня — пропускаємо
  uint8_t day = bcdToDec(Wire.read());
  uint8_t mon = bcdToDec(Wire.read());
  uint8_t yr  = bcdToDec(Wire.read());

  Serial.printf("20%02u-%02u-%02u %02u:%02u:%02u\n", yr, mon, day, hh, mm, ss);
  delay(1000);
}
