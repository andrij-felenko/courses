#include <Wire.h>

#define SDA_PIN 8
#define SCL_PIN 9

// Типова адреса модуля GY-BMP280: SDO притягнутий до землі → 0x76.
// Якщо SDO на живленні (або в «рідному» виконанні Bosch) → 0x77.
#define BMP_ADDR 0x76
#define REG_ID   0xD0     // регістр ідентифікатора чипа
#define BMP280_ID 0x58    // очікуване значення для BMP280

// Прочитати один байт із регістра reg пристрою addr.
bool readReg(uint8_t addr, uint8_t reg, uint8_t &out) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0)   // false: повторний старт, без стопу
    return false;                          // давач не відповів на адресу
  if (Wire.requestFrom(addr, (uint8_t)1) != 1)
    return false;                          // давач не віддав байт
  out = Wire.read();
  return true;
}

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 2000) {}
  Wire.begin(SDA_PIN, SCL_PIN, 100000);

  uint8_t id = 0;
  if (!readReg(BMP_ADDR, REG_ID, id)) {
    Serial.printf("За адресою 0x%02X ніхто не відповідає. "
                  "Спробуй 0x77 і перевір дроти.\n", BMP_ADDR);
    return;
  }
  Serial.printf("Регістр 0x%02X = 0x%02X — ", REG_ID, id);
  if (id == BMP280_ID)      Serial.println("це BMP280, як і чекали.");
  else if (id == 0x60)      Serial.println("це BME280 (з вологістю), не BMP280!");
  else                      Serial.println("невідомий чип за цією адресою.");
}

void loop() {}
