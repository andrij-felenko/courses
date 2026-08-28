#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

int16_t ax, ay, az, gx, gy, gz;

float roll = 0, pitch = 0;      // поточні злиті кути, °
float gyroBiasX = 0, gyroBiasY = 0;   // нуль гіроскопа (з калібрування)
uint32_t tPrev = 0;

const float ALPHA = 0.98f;      // вага гіроскопа у злитті

void setup() {
    Serial.begin(115200);
    Wire.begin();
    mpu.initialize();
    if (!mpu.testConnection()) { Serial.println(F("немає чипа")); while (1); }

    calibrateGyro();            // виміряти нуль гіроскопа (див. нижче)
    tPrev = micros();
}

void loop() {
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    // Реальний крок часу в секундах (micros() — мікросекунди).
    uint32_t now = micros();
    float dt = (now - tPrev) * 1e-6f;
    tPrev = now;

    // --- кут з акселерометра (абсолютний, шумний) ---
    float axg = ax / 16384.0f, ayg = ay / 16384.0f, azg = az / 16384.0f;
    float rollAcc  = atan2f(ayg, azg) * 180.0f / M_PI;
    float pitchAcc = atan2f(-axg, sqrtf(ayg*ayg + azg*azg)) * 180.0f / M_PI;

    // --- кутова швидкість з гіроскопа, з відрахованим нулем (°/s) ---
    float rateX = (gx - gyroBiasX) / 131.0f;
    float rateY = (gy - gyroBiasY) / 131.0f;

    // --- комплементарне злиття ---
    roll  = ALPHA * (roll  + rateX * dt) + (1.0f - ALPHA) * rollAcc;
    pitch = ALPHA * (pitch + rateY * dt) + (1.0f - ALPHA) * pitchAcc;

    Serial.print(F("roll "));  Serial.print(roll, 1);
    Serial.print(F("  pitch ")); Serial.println(pitch, 1);
    // БЕЗ delay(): точність фільтра залежить від частого, рівного циклу.
}
