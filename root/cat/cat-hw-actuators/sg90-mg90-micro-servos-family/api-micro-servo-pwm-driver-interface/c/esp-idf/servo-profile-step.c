// C (ESP-IDF / Embedded C) - Дискретний крок профілювання руху
#include <math.h>

typedef struct {
    float current_angle;
    float target_angle;
    float current_speed;
    float max_speed;       // град/сек
    float accel;           // град/сек^2
} servo_profile_t;

// Обчислення наступного кроку позиції за інтервал dt (секунди)
float servo_profile_step(servo_profile_t *prof, float dt) {
    float error = prof->target_angle - prof->current_angle;
    if (fabsf(error) < 0.01f) {
        prof->current_speed = 0.0f;
        return prof->current_angle;
    }

    // Дистанція необхідна для повного гальмування: s = v^2 / (2*a)
    float stop_dist = (prof->current_speed * prof->current_speed) / (2.0f * prof->accel);

    if (fabsf(error) <= stop_dist) {
        // Фаза гальмування
        prof->current_speed -= prof->accel * dt;
        if (prof->current_speed < 0.1f) prof->current_speed = 0.1f;
    } else {
        // Фаза розгону або постійної швидкості
        if (prof->current_speed < prof->max_speed) {
            prof->current_speed += prof->accel * dt;
            if (prof->current_speed > prof->max_speed) {
                prof->current_speed = prof->max_speed;
            }
        }
    }

    // Оновлення поточної позиції з урахуванням напрямку
    float dir = (error > 0.0f) ? 1.0f : -1.0f;
    prof->current_angle += dir * prof->current_speed * dt;

    return prof->current_angle;
}
