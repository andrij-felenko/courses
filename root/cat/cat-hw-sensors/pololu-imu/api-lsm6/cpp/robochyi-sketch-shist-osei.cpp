#include <Wire.h>
#include <LSM6.h>

LSM6 imu;                       // об'єкт = мікросхема LSM6DS33

void setup() {
  Serial.begin(9600);
  Wire.begin();                 // на ESP32/STM32/Pico задай свої ніжки: Wire.begin(21, 22);

  if (!imu.init()) {            // знайти чип; false = його на шині немає
    Serial.println("LSM6DS33 не знайдено — перевір дроти, живлення, підтяжки");
    while (1);                  // далі немає сенсу — зупиняємось
  }
  imu.enableDefault();         // увімкнути акселерометр (±2 g) і гіроскоп (±245 °/с)
}

void loop() {
  imu.read();                  // оновити a.x/a.y/a.z та g.x/g.y/g.z

  char buf[64];
  // %6d — шестизнакове поле, щоб стовпчики не «стрибали»
  snprintf(buf, sizeof(buf), "A: %6d %6d %6d   G: %6d %6d %6d",
           imu.a.x, imu.a.y, imu.a.z,
           imu.g.x, imu.g.y, imu.g.z);
  Serial.println(buf);

  delay(100);                  // 10 разів на секунду — вистачить, щоб дивитись очима
}
