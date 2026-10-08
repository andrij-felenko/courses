#include <Wire.h>
#include <VL53L0X.h>

VL53L0X sensor;

void setup() {
  Serial.begin(115200);
  Wire.begin();

  sensor.setTimeout(500);
  if (!sensor.init()) {
    Serial.println("Помилка ініціалізації VL53L0X!");
    while (1);
  }

  // Встановлення профілю High Accuracy: часовий бюджет 200 мс (200000 мкс)
  sensor.setMeasurementTimingBudget(200000);

  // Запуск безперервного циклічного вимірювання
  sensor.startContinuous();
}

void loop() {
  uint16_t distance_mm = sensor.readRangeContinuousMillimeters();
  if (sensor.timeoutOccurred()) {
    Serial.println("Помилка: таймаут зчитування даних!");
  } else {
    Serial.print("Виміряна відстань: ");
    Serial.print(distance_mm);
    Serial.println(" мм");
  }
}
