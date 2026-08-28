#include <Wire.h>
#include <MPU6050.h>     // бібліотека Джеффа Роуберґа (i2cdevlib)

MPU6050 mpu;             // адреса за замовчуванням 0x68 (AD0 на землі)

int16_t ax, ay, az;      // сирі значення акселерометра
int16_t gx, gy, gz;      // сирі значення гіроскопа

void setup() {
    Serial.begin(115200);
    Wire.begin();

    mpu.initialize();    // будить чип і ставить типові діапазони (±2g, ±250°/s)

    // Перше, що робимо ЗАВЖДИ — питаємо, чи це взагалі наш чип.
    if (mpu.testConnection()) {
        Serial.println(F("MPU-6050 на місці"));
    } else {
        Serial.println(F("MPU-6050 НЕ відповідає — перевір пайку/адресу/клон"));
        while (1) { }    // далі йти немає сенсу
    }
}

void loop() {
    // Один виклик читає всі шість осей одним пакетом по I2C.
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    float accX = ax / 16384.0f;    // g   (при діапазоні ±2g)
    float gyrX = gx / 131.0f;      // °/s (при діапазоні ±250°/s)

    Serial.print(accX); Serial.print('\t');
    Serial.println(gyrX);
    delay(20);
}
