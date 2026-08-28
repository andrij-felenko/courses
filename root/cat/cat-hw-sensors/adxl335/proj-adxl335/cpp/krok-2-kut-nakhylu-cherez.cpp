#include <math.h>

// Кути нахилу (градуси) з трьох прискорень у g.
void tiltAngles(float ax, float ay, float az,
                float* pitch, float* roll) {
    const float RAD2DEG = 57.29578f;             // 180 / π
    *pitch = atan2f(ax, sqrtf(ay*ay + az*az)) * RAD2DEG;
    *roll  = atan2f(ay, sqrtf(ax*ax + az*az)) * RAD2DEG;
}

void loop() {
    float ax = readG(A0, 0);
    float ay = readG(A1, 1);
    float az = readG(A2, 2);

    float pitch, roll;
    tiltAngles(ax, ay, az, &pitch, &roll);

    Serial.print("pitch="); Serial.print(pitch, 1);
    Serial.print("  roll="); Serial.println(roll, 1);
    delay(50);
}
