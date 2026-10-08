#include <stdbool.h>
#include <stdint.h>

typedef struct {
    uint32_t deadband_us;
    uint32_t center_us;
} deadband_config_t;

typedef enum {
    SERVO_DIR_STOP = 0,
    SERVO_DIR_CW   = 1,
    SERVO_DIR_CCW  = 2
} servo_dir_t;

servo_dir_t evaluate_deadband(uint32_t pulse_in_us, uint32_t pulse_fb_us, const deadband_config_t *cfg) {
    int32_t diff = (int32_t)pulse_in_us - (int32_t)pulse_fb_us;
    
    if (diff > (int32_t)cfg->deadband_us) {
        return SERVO_DIR_CW;
    } else if (diff < -(int32_t)cfg->deadband_us) {
        return SERVO_DIR_CCW;
    }
    return SERVO_DIR_STOP;
}
