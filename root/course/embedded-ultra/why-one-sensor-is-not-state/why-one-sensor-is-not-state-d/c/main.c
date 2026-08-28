/* Реалізація 6-DOF орієнтаційного фільтра Махоні мовою C */
#include <math.h>
#include <stdbool.h>

typedef struct {
    float q0, q1, q2, q3; /* Одиничний кватерніон орієнтації */
    float b_x, b_y, b_z;  /* Оцінене зміщення нуля гіроскопа (bias) */
    float kp;             /* Пропорційний коефіцієнт фільтра */
    float ki;             /* Інтегральний коефіцієнт компенсації дрейфу */
} ImuAttitudeFilter_t;

void imu_filter_init(ImuAttitudeFilter_t *f, float kp_gain, float ki_gain) {
    f->q0 = 1.0f;
    f->q1 = 0.0f;
    f->q2 = 0.0f;
    f->q3 = 0.0f;
    f->b_x = 0.0f;
    f->b_y = 0.0f;
    f->b_z = 0.0f;
    f->kp = kp_gain;
    f->ki = ki_gain;
}

void imu_filter_update(ImuAttitudeFilter_t *f,
                       float gx, float gy, float gz, /* рад/с */
                       float ax, float ay, float az, /* м/с^2 або g */
                       float dt)                     /* секунди */
{
    float a_norm_sq = ax * ax + ay * ay + az * az;
    float ex = 0.0f, ey = 0.0f, ez = 0.0f;

    /* Перевірка наявності валідного сигналу акселерометра */
    if (a_norm_sq > 0.001f) {
        float inv_a_norm = 1.0f / sqrtf(a_norm_sq);
        ax *= inv_a_norm;
        ay *= inv_a_norm;
        az *= inv_a_norm;

        /* Динамічний гейтинг: враховуємо акселерометр лише при довжині ~ 1g */
        float a_mag = 1.0f / inv_a_norm;
        if (a_mag >= 0.85f && a_mag <= 1.15f) {
            /* Очікуваний вектор гравітації у зв'язаній системі координат */
            float vx = 2.0f * (f->q1 * f->q3 - f->q0 * f->q2);
            float vy = 2.0f * (f->q0 * f->q1 + f->q2 * f->q3);
            float vz = f->q0 * f->q0 - f->q1 * f->q1 - f->q2 * f->q2 + f->q3 * f->q3;

            /* Векторний добуток виміряного та очікуваного векторів */
            ex = (ay * vz - az * vy);
            ey = (az * vx - ax * vz);
            ez = (ax * vy - ay * vx);

            /* Інтегральна ланка: накопичення та компенсація дрейфу нуля */
            if (f->ki > 0.0f) {
                f->b_x -= f->ki * ex * dt;
                f->b_y -= f->ki * ey * dt;
                f->b_z -= f->ki * ez * dt;
            }
        }
    }

    /* Корекція кутової швидкості */
    gx = gx - f->b_x + f->kp * ex;
    gy = gy - f->b_y + f->kp * ey;
    gz = gz - f->b_z + f->kp * ez;

    /* Чисельне інтегрування диференціального рівняння кватерніона */
    float q0_dot = 0.5f * (-f->q1 * gx - f->q2 * gy - f->q3 * gz);
    float q1_dot = 0.5f * ( f->q0 * gx + f->q2 * gz - f->q3 * gy);
    float q2_dot = 0.5f * ( f->q0 * gy - f->q1 * gz + f->q3 * gx);
    float q3_dot = 0.5f * ( f->q0 * gz + f->q1 * gy - f->q2 * gx);

    f->q0 += q0_dot * dt;
    f->q1 += q1_dot * dt;
    f->q2 += q2_dot * dt;
    f->q3 += q3_dot * dt;

    /* Обов'язкова нормалізація кватерніона для збереження ортогональності */
    float inv_q_norm = 1.0f / sqrtf(f->q0 * f->q0 + f->q1 * f->q1 + 
                                    f->q2 * f->q2 + f->q3 * f->q3);
    f->q0 *= inv_q_norm;
    f->q1 *= inv_q_norm;
    f->q2 *= inv_q_norm;
    f->q3 *= inv_q_norm;
}
