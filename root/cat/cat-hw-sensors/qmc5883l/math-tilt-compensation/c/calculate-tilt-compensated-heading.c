#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Обчислення компенсованого дійсного азимута у градусах [0..360)
double calculate_tilt_compensated_heading(
    double bx, double by, double bz,
    double ax, double ay, double az,
    double declination_deg
) {
    // 1. Обчислення кутів крену (phi) та тангажу (theta) за акселерометром
    double roll = atan2(ay, az);
    double pitch = atan2(-ax, sqrt(ay * ay + az * az));

    // 2. Проєкція вектора магнітної індукції на горизонтальну площину
    double sin_roll = sin(roll);
    double cos_roll = cos(roll);
    double sin_pitch = sin(pitch);
    double cos_pitch = cos(pitch);

    double bx_h = bx * cos_pitch + by * sin_roll * sin_pitch + bz * cos_roll * sin_pitch;
    double by_h = by * cos_roll - bz * sin_roll;

    // 3. Обчислення магнітного азимута
    double heading_rad = atan2(by_h, bx_h);
    double heading_deg = heading_rad * (180.0 / M_PI);

    if (heading_deg < 0.0) {
        heading_deg += 360.0;
    }

    // 4. Врахування магнітного схилення та обчислення дійсного азимута
    double true_heading = heading_deg + declination_deg;

    if (true_heading >= 360.0) {
        true_heading -= 360.0;
    } else if (true_heading < 0.0) {
        true_heading += 360.0;
    }

    return true_heading;
}
