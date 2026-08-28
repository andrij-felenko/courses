#include <Wire.h>
#include <LSM6.h>
#include <LIS3MDL.h>

LSM6    imu;
LIS3MDL mag;

// Чутливості для налаштувань за замовчуванням enableDefault():
const float ACC_G     = 0.000061f;   // g на відлік        (±2 g)
const float GYRO_DPS  = 0.00875f;    // °/с на відлік      (±245 °/с)
const float MAG_GAUSS = 1.0f / 6842; // гаус на відлік     (±4 гауси)

void setup() {
  Serial.begin(9600);
  Wire.begin();

  if (!imu.init() || !mag.init()) {
    Serial.println("давач не знайдено — перевір I2C");
    while (1);
  }
  imu.enableDefault();
  mag.enableDefault();
}

void loop() {
  imu.read();
  mag.read();

  // сире (int16_t) → фізичне (float), кожну вісь на свою чутливість:
  float ax = imu.a.x * ACC_G,    ay = imu.a.y * ACC_G,    az = imu.a.z * ACC_G;
  float gx = imu.g.x * GYRO_DPS, gy = imu.g.y * GYRO_DPS, gz = imu.g.z * GYRO_DPS;
  float mx = mag.m.x * MAG_GAUSS, my = mag.m.y * MAG_GAUSS, mz = mag.m.z * MAG_GAUSS;

  Serial.print("a[g]: ");
  Serial.print(ax, 2); Serial.print(' ');
  Serial.print(ay, 2); Serial.print(' ');
  Serial.print(az, 2);

  Serial.print("   g[dps]: ");
  Serial.print(gx, 1); Serial.print(' ');
  Serial.print(gy, 1); Serial.print(' ');
  Serial.print(gz, 1);

  Serial.print("   m[Gs]: ");
  Serial.print(mx, 3); Serial.print(' ');
  Serial.print(my, 3); Serial.print(' ');
  Serial.println(mz, 3);

  delay(100);
}
