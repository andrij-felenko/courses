#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint16_t t_neutral;   // Нейтраль (мкс)
    uint16_t t_min_fwd;   // Поріг руху вперед (мкс)
    uint16_t t_max_fwd;   // Максимум вперед (мкс)
    uint16_t t_min_rev;   // Поріг руху назад (мкс)
    uint16_t t_max_rev;   // Максимум назад (мкс)
} servo_calib_t;

uint16_t servo_speed_to_pulse(float speed, const servo_calib_t *calib) {
    if (speed > 1.0f) speed = 1.0f;
    if (speed < -1.0f) speed = -1.0f;

    if (speed > 0.0f) {
        return (uint16_t)(calib->t_min_fwd + speed * (calib->t_max_fwd - calib->t_min_fwd));
    } else if (speed < 0.0f) {
        return (uint16_t)(calib->t_min_rev + speed * (calib->t_min_rev - calib->t_max_rev));
    }
    return calib->t_neutral;
}
