#include <stdint.h>
#include <math.h>

typedef struct {
    int16_t offset_us;
    uint16_t deadband_us;
} servo_calibration_t;

uint32_t process_servo_deadband(float speed, const servo_calibration_t* cal) {
    uint32_t neutral = 1500 + cal->offset_us;
    float abs_s = fabsf(speed);
    float db_norm = (float)cal->deadband_us / 500.0f;

    if (abs_s <= db_norm) {
        return neutral;
    }

    float scaled_s = (abs_s - db_norm) / (1.0f - db_norm);
    if (speed < 0.0f) scaled_s = -scaled_s;

    return (uint32_t)(neutral + lroundf(scaled_s * 500.0f));
}
