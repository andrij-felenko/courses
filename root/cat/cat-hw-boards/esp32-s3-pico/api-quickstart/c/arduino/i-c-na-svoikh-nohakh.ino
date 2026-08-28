#include <Wire.h>

void setup() {
  Serial.begin(115200);
  Wire.begin(8, 9);              // SDA=GPIO8, SCL=GPIO9 — свої ноги
  Wire.setClock(400000);        // 400 кГц (fast mode); за замовчуванням 100 кГц

  Wire.beginTransmission(0x76); // чи є хтось за адресою 0x76?
  if (Wire.endTransmission() == 0)
    Serial.println("BMP280 відповідає");
  else
    Serial.println("тиша на шині: перевір ноги, живлення й підтяжки");
}

void loop() {}
