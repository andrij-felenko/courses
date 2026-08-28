#include <Wire.h>
#include <LSM6.h>
#include <LIS3MDL.h>

LSM6    imu;                    // акселерометр + гіроскоп (0x6B)
LIS3MDL mag;                    // магнетометр            (0x1E)

void setup() {
  Serial.begin(9600);
  Wire.begin();                 // одна шина на обидва чипи (ESP32: Wire.begin(21, 22))

  if (!imu.init()) {
    Serial.println("LSM6DS33 не знайдено");
    while (1);
  }
  imu.enableDefault();

  if (!mag.init()) {
    Serial.println("LIS3MDL не знайдено");
    while (1);
  }
  mag.enableDefault();
}

void loop() {
  imu.read();                   // a.* та g.* — рух
  mag.read();                   // m.*        — поле

  char buf[96];
  snprintf(buf, sizeof(buf),
           "A:%6d %6d %6d  G:%6d %6d %6d  M:%6d %6d %6d",
           imu.a.x, imu.a.y, imu.a.z,
           imu.g.x, imu.g.y, imu.g.z,
           mag.m.x, mag.m.y, mag.m.z);
  Serial.println(buf);

  delay(100);
}
