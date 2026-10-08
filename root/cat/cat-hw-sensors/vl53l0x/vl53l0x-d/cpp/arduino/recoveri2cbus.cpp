#include <Wire.h>
#include <VL53L0X.h>

VL53L0X sensor;
const uint8_t XSHUT_PIN = 4;
const uint8_t SCL_PIN = 22;

void recoverI2CBus() {
  pinMode(SCL_PIN, OUTPUT);
  for (int i = 0; i < 9; i++) {
    digitalWrite(SCL_PIN, HIGH);
    delayMicroseconds(5);
    digitalWrite(SCL_PIN, LOW);
    delayMicroseconds(5);
  }
  // Перезапуск сенсора через XSHUT
  digitalWrite(XSHUT_PIN, LOW);
  delay(10);
  digitalWrite(XSHUT_PIN, HIGH);
  delay(10);
}

void checkAndReadSensor() {
  uint16_t distance = sensor.readRangeSingleMillimeters();
  
  if (sensor.timeoutOccurred()) {
    Serial.println("Помилка: Таймаут I2C! Відновлення шини...");
    recoverI2CBus();
    sensor.init();
    return;
  }

  // Отримання статусу зчитаного значення
  uint8_t status = sensor.readReg(0x14); // RESULT_RANGE_STATUS
  uint8_t rangeStatus = (status >> 3) & 0x0F;

  switch (rangeStatus) {
    case 0:
      Serial.print("Успіх: ");
      Serial.print(distance);
      Serial.println(" мм");
      break;
    case 1:
      Serial.println("Помилка (Sigma Fail): Занадто сильне фонове світло");
      break;
    case 2:
      Serial.println("Помилка (Signal Fail): Слабкий відбитий сигнал (темна поверхня)");
      break;
    case 3:
      Serial.println("Помилка (Min Range Fail): Об'єкт занадто близько (<30 мм)");
      break;
    default:
      Serial.print("Помилка статус: ");
      Serial.println(rangeStatus);
      break;
  }
}
