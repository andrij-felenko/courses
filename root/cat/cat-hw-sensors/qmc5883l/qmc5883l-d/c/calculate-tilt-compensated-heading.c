#include <math.h>
#include <stdint.h>

#define M_PI_F 3.14159265358979323846f

typedef struct {
    float x;
    float y;
    float z;
} vector3f_t;

// Обчислення компенсованого азимута (в градусах)
float calculate_tilt_compensated_heading(vector3f_t mag, vector3f_t accel, vector3f_t hard_iron_offset) {
    // 1. Компенсація Hard Iron зсуву
    float mx = mag.x - hard_iron_offset.x;
    float my = mag.y - hard_iron_offset.y;
    float mz = mag.z - hard_iron_offset.z;

    // 2. Обчислення кутів крену (roll) та тангажу (pitch) з акселерометра
    float roll = atan2f(accel.y, accel.z);
    float pitch = atan2f(-accel.x, sqrtf(accel.y * accel.y + accel.z * accel.z));

    // 3. Проекція вектора на горизонтальну площину
    float cos_roll = cosf(roll);
    float sin_roll = sinf(roll);
    float cos_pitch = cosf(pitch);
    float sin_pitch = sinf(pitch);

    float X_h = mx * cos_pitch + mz * sin_pitch;
    float Y_h = mx * sin_roll * sin_pitch + my * cos_roll - mz * sin_roll * cos_pitch;

    // 4. Обчислення азимута
    float heading_rad = atan2f(Y_h, X_h);
    float heading_deg = heading_rad * (180.0f / M_PI_F);

    if (heading_deg < 0.0f) {
        heading_deg += 360.0f;
    }

    return heading_deg;
}
