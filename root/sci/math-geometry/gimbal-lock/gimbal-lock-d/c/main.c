#include <math.h>
#include <stdbool.h>

#define PI_2 1.57079632679489661923

typedef struct {
    double w;
    double x;
    double y;
    double z;
} Quaternion;

typedef struct {
    double roll;   /* крен φ навколо осі X, радіани */
    double pitch;  /* тангаж θ навколо осі Y, радіани */
    double yaw;    /* рискання ψ навколо осі Z, радіани */
} EulerAngles;

static inline double clamp_val(double val, double min_val, double max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

EulerAngles quaternion_to_euler_safe(Quaternion q) {
    EulerAngles angles;
    const double epsilon = 1e-6;

    /* Обчислення синуса кута тангажу */
    double sin_pitch = 2.0 * (q.w * q.y - q.x * q.z);
    sin_pitch = clamp_val(sin_pitch, -1.0, 1.0);

    /* Перевірка на складання рамок (gimbal lock) */
    if (sin_pitch >= 1.0 - epsilon) {
        /* Тангаж +90 градусів: ніс вертикально вгору */
        angles.pitch = PI_2;
        angles.roll = 0.0; /* фіксуємо вільний ступінь вільності */
        angles.yaw = -2.0 * atan2(q.x, q.w);
    } else if (sin_pitch <= -1.0 + epsilon) {
        /* Тангаж -90 градусів: ніс вертикально вниз */
        angles.pitch = -PI_2;
        angles.roll = 0.0;
        angles.yaw = 2.0 * atan2(q.x, q.w);
    } else {
        /* Регулярний стан: повноцінне обчислення */
        angles.pitch = asin(sin_pitch);

        double sin_roll_cos_pitch = 2.0 * (q.w * q.x + q.y * q.z);
        double cos_roll_cos_pitch = 1.0 - 2.0 * (q.x * q.x + q.y * q.y);
        angles.roll = atan2(sin_roll_cos_pitch, cos_roll_cos_pitch);

        double sin_yaw_cos_pitch = 2.0 * (q.w * q.z + q.x * q.y);
        double cos_yaw_cos_pitch = 1.0 - 2.0 * (q.y * q.y + q.z * q.z);
        angles.yaw = atan2(sin_yaw_cos_pitch, cos_yaw_cos_pitch);
    }

    return angles;
}
