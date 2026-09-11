#include <math.h>

/**
 * @brief Періодичний крок профілювання швидкості (slew-rate limiter).
 * @param servo Покажчик на дескриптор сервопривода.
 * @param dt_ms Час, що минув з попереднього виклику, у мілісекундах.
 * @return true якщо вал досяг цільової точки, false якщо рух триває.
 */
bool servo_update(servo_t *servo, uint32_t dt_ms) {
    if (servo == NULL || !servo->is_attached) {
        return true;
    }

    float error = servo->target_angle_deg - servo->current_angle_deg;
    
    // Якщо помилка знаходиться в межах мертвої зони (0.05°), рух завершено
    if (fabsf(error) < 0.05f) {
        servo->current_angle_deg = servo->target_angle_deg;
        servo_write_angle(servo, servo->current_angle_deg);
        return true;
    }

    // Максимально дозволений приріст кута за пройдений інтервал часу dt
    float max_step = (servo->speed_deg_per_s * (float)dt_ms) / 1000.0f;

    if (fabsf(error) <= max_step) {
        servo->current_angle_deg = servo->target_angle_deg;
    } else {
        // Рух у напрямку цілі з постійною лімітованою швидкістю
        if (error > 0.0f) {
            servo->current_angle_deg += max_step;
        } else {
            servo->current_angle_deg -= max_step;
        }
    }

    servo_write_angle(servo, servo->current_angle_deg);
    return false;
}
