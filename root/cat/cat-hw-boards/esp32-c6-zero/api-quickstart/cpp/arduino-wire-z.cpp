#include <Wire.h>

#define I2C_SDA   6
#define I2C_SCL   7
#define DEV_ADDR  0x68
#define REG_WHO   0x75

void setup() {
  Serial.begin(115200);
  Wire.begin(I2C_SDA, I2C_SCL);   // ← ноги шини задаються тут

  Wire.beginTransmission(DEV_ADDR);
  Wire.write(REG_WHO);            // сказати, який регістр читаємо
  Wire.endTransmission(false);    // false = не відпускати шину (repeated start)

  Wire.requestFrom(DEV_ADDR, 1);  // попросити 1 байт
  if (Wire.available()) {
    uint8_t who = Wire.read();
    Serial.printf("WHO_AM_I = 0x%02X\n", who);
  } else {
    Serial.println("Давач мовчить: перевір адресу й підтяжки");
  }
}

void loop() {}
